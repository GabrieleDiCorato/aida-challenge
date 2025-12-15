{{
    config(
        materialized='table'
    )
}}

with customer_base as (
    select * from {{ ref('int_customer_policies') }}
),

interactions as (
    select * from {{ ref('int_customer_interactions') }}
),

claims as (
    select * from {{ ref('int_customer_claims') }}
),

final as (
    select
        -- Customer identifiers
        cb.codice_cliente,
        cb.nome,
        cb.cognome,
        cb.eta,
        cb.professione,
        cb.reddito,
        cb.stato_civile,
        cb.agenzia,
        cb.zona_residenza,

        -- Policy metrics
        cb.num_prodotti_distinti,
        cb.num_polizze_totali,
        cb.num_polizze_attive,
        cb.premio_annuo_totale,
        cb.premio_annuo_medio,
        cb.massimale_totale,
        cb.margine_lordo_totale,

        -- Product mix
        cb.num_prodotti_protezione,
        cb.num_prodotti_investimento,

        -- Interaction metrics
        cb.engagement_score,
        cb.churn_probability,
        cb.clv_stimato,
        cb.satisfaction_score,
        cb.potenziale_crescita,

        -- Claims metrics
        coalesce(i.num_interazioni_totali, 0) as num_interazioni_totali,
        coalesce(i.num_conversioni, 0) as num_conversioni,
        coalesce(i.tasso_conversione, 0) as tasso_conversione,

        -- Customer scores
        coalesce(i.num_esiti_positivi, 0) as num_esiti_positivi,
        coalesce(i.durata_media_minuti, 0) as durata_media_interazioni,
        coalesce(cl.num_sinistri_totali, 0) as num_sinistri_totali,
        coalesce(cl.importo_totale_liquidato, 0) as importo_totale_liquidato,
        coalesce(cl.frequenza_sinistri_annua, 0) as frequenza_sinistri_annua,

        -- Customer segmentation
        case
            when cb.clv_stimato > 50000 and cb.churn_probability < 0.3 then 'Premium Loyal'
            when cb.clv_stimato > 50000 and cb.churn_probability >= 0.3 then 'Premium At Risk'
            when cb.churn_probability > 0.7 then 'High Churn Risk'
            when cb.potenziale_crescita > 0.5 then 'Growth Opportunity'
            when cb.num_polizze_attive = 0 then 'Inactive'
            else 'Standard'
        end as segmento_cliente,

        -- Risk classification
        case
            when coalesce(cl.num_sinistri_totali, 0) = 0 then 'No Claims'
            when coalesce(cl.frequenza_sinistri_annua, 0) < 0.5 then 'Low Risk'
            when coalesce(cl.frequenza_sinistri_annua, 0) < 1.5 then 'Medium Risk'
            else 'High Risk'
        end as classificazione_rischio,

        -- Value classification
        case
            when cb.premio_annuo_totale > 5000 then 'High Value'
            when cb.premio_annuo_totale > 2000 then 'Medium Value'
            when cb.premio_annuo_totale > 0 then 'Low Value'
            else 'No Active Policies'
        end as classificazione_valore,

        -- Metadata
        current_timestamp as _dbt_loaded_at

    from customer_base as cb
    left join interactions as i on cb.codice_cliente = i.codice_cliente
    left join claims as cl on cb.codice_cliente = cl.codice_cliente
)

select * from final
