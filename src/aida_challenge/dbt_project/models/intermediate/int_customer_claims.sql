{{
    config(
        materialized='view'
    )
}}

with sinistri as (
    select * from {{ ref('stg_sinistri') }}
),

aggregated as (
    select
        codice_cliente,

        -- Claim counts
        count(*) as num_sinistri_totali,
        count(distinct prodotto) as num_prodotti_con_sinistri,

        -- By status
        count(case when stato_liquidazione = 'Liquidato' then 1 end) as num_sinistri_liquidati,
        count(case when stato_liquidazione = 'In Lavorazione' then 1 end) as num_sinistri_in_lavorazione,
        count(case when stato_liquidazione = 'Respinto' then 1 end) as num_sinistri_respinti,

        -- Financial metrics
        sum(importo_liquidato) as importo_totale_liquidato,
        avg(importo_liquidato) as importo_medio_liquidato,
        max(importo_liquidato) as importo_max_liquidato,

        -- Dates
        min(data_sinistro) as data_primo_sinistro,
        max(data_sinistro) as data_ultimo_sinistro,

        -- Claim frequency
        count(*)::float
        / nullif(datediff('year', min(data_sinistro), current_date), 0)::float as frequenza_sinistri_annua

    from sinistri
    group by codice_cliente
)

select * from aggregated
