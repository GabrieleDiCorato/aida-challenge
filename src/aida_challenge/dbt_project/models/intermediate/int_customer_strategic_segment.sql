{{
    config(
        materialized='view',
        schema='intermediate'
    )
}}

with wealth_segments as (
    select * from {{ ref('int_customer_wealth_segments') }}
),

product_ownership as (
    select * from {{ ref('int_customer_product_ownership') }}
),

engagement_metrics as (
    select * from {{ ref('int_customer_engagement_metrics') }}
),

combined as (
    select
        ws.codice_cliente,
        ws.nome,
        ws.cognome,
        ws.eta,
        ws.numero_figli,
        ws.stato_civile,
        ws.professione,
        ws.patrimonio_totale,
        ws.segmento_valore,
        ws.fase_vita,

        po.possiede_casa,
        po.possiede_salute,
        po.possiede_investimento,
        po.possiede_pip,
        po.num_prodotti_posseduti,

        em.engagement_score,
        em.churn_probability,
        em.clv_stimato,
        em.livello_engagement,
        em.livello_urgenza,
        em.giorni_ultima_visita,
        em.num_interazioni,
        em.tasso_conversione,
        em.num_sinistri,
        em.num_reclami

    from wealth_segments as ws
    left join product_ownership as po on ws.codice_cliente = po.codice_cliente
    left join engagement_metrics as em on ws.codice_cliente = em.codice_cliente
),

final as (
    select
        *,

        -- Strategic segment assignment based on value, life stage, products, and engagement
        case
            -- Affluent Young Families: Upper-Retail, Young Family, <= 2 products
            when
                segmento_valore = 'Upper-Retail'
                and fase_vita = 'Young Family'
                and num_prodotti_posseduti <= 2
                then 'Affluent Young Families'

            -- Investment-Only Affluent: Upper-Retail with only investment products
            when
                segmento_valore = 'Upper-Retail'
                and possiede_investimento = 1
                and possiede_casa = 0
                and possiede_salute = 0
                then 'Investment-Only Affluent'

            -- At-Risk High Value: Upper-Retail with at-risk engagement
            when
                segmento_valore = 'Upper-Retail'
                and livello_engagement = 'At-Risk'
                then 'At-Risk High Value'

            -- Premium Multi-Holders: Upper-Retail with 3+ products
            when
                segmento_valore = 'Upper-Retail'
                and num_prodotti_posseduti >= 3
                then 'Premium Multi-Holders'

            -- Default: Combination of value segment and life stage
            else segmento_valore || ' ' || fase_vita
        end as segmento_strategico,

        -- NBA recommendation based on strategic segment and product gaps
        case
            -- Affluent Young Families: prioritize Casa and Salute
            when
                segmento_valore = 'Upper-Retail'
                and fase_vita = 'Young Family'
                and num_prodotti_posseduti <= 2
                then
                    case
                        when possiede_casa = 0 and possiede_salute = 0 then 'Casa+Salute'
                        when possiede_casa = 0 then 'Casa'
                        when possiede_salute = 0 then 'Salute'
                        when possiede_investimento = 0 then 'Investimento'
                        when possiede_pip = 0 then 'PIP'
                        else 'Retention'
                    end

            -- Investment-Only Affluent: recommend protection products
            when
                segmento_valore = 'Upper-Retail'
                and possiede_investimento = 1
                and possiede_casa = 0
                and possiede_salute = 0
                then
                    case
                        when possiede_casa = 0 and possiede_salute = 0 and possiede_pip = 0 then 'Casa+Salute+PIP'
                        when possiede_casa = 0 and possiede_salute = 0 then 'Casa+Salute'
                        when possiede_casa = 0 then 'Casa'
                        when possiede_salute = 0 then 'Salute'
                        when possiede_pip = 0 then 'PIP'
                        else 'Retention'
                    end

            -- At-Risk High Value and Premium Multi-Holders: focus on retention
            when
                (segmento_valore = 'Upper-Retail' and livello_engagement = 'At-Risk')
                or (segmento_valore = 'Upper-Retail' and num_prodotti_posseduti >= 3)
                then 'Retention'

            -- Default: recommend first missing product in priority order
            when possiede_casa = 0 then 'Casa'
            when possiede_salute = 0 then 'Salute'
            when possiede_investimento = 0 then 'Investimento'
            when possiede_pip = 0 then 'PIP'
            else 'Retention'
        end as raccomandazione_nba,

        current_timestamp as _dbt_loaded_at

    from combined
)

select * from final
