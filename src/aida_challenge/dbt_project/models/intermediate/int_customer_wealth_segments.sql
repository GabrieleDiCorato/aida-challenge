{{
    config(
        materialized='view',
        schema='intermediate'
    )
}}

with clienti_base as (
    select * from {{ ref('stg_clienti') }}
),

wealth_calculation as (
    select
        codice_cliente,
        nome,
        cognome,
        eta,
        numero_figli,
        stato_civile,
        professione,
        reddito,
        patrimonio_finanziario,
        patrimonio_reale,

        -- Calculate total wealth
        coalesce(reddito, 0)
        + coalesce(patrimonio_finanziario, 0)
        + coalesce(patrimonio_reale, 0) as patrimonio_totale

    from clienti_base
),

wealth_quantiles as (
    -- Calculate quartiles for value segmentation
    select
        percentile_cont(0.25) within group (
            order by patrimonio_totale
        ) as q25,
        percentile_cont(0.75) within group (
            order by patrimonio_totale
        ) as q75
    from wealth_calculation
),

final as (
    select
        wc.codice_cliente,
        wc.nome,
        wc.cognome,
        wc.eta,
        wc.numero_figli,
        wc.stato_civile,
        wc.professione,
        wc.reddito,
        wc.patrimonio_finanziario,
        wc.patrimonio_reale,
        wc.patrimonio_totale,

        -- Value segment based on wealth quartiles
        case
            when wc.patrimonio_totale >= wq.q75 then 'Upper-Retail'
            when wc.patrimonio_totale >= wq.q25 then 'Mid-Retail'
            else 'Entry-Retail'
        end as segmento_valore,

        -- Life stage based on age and number of children
        case
            when wc.eta < 30 and wc.numero_figli = 0 then 'Young Single'
            when wc.eta < 30 and wc.numero_figli > 0 then 'Young Family'
            when wc.eta < 40 and wc.numero_figli > 0 then 'Young Family'
            when wc.eta < 40 and wc.numero_figli = 0 then 'Young Professional'
            when wc.eta < 55 and wc.numero_figli > 0 then 'Established Family'
            when wc.eta < 55 and wc.numero_figli = 0 then 'Established Professional'
            when wc.eta < 65 then 'Pre-Retirement'
            else 'Retired'
        end as fase_vita,

        current_timestamp as _dbt_loaded_at

    from wealth_calculation as wc
    cross join wealth_quantiles as wq
)

select * from final
