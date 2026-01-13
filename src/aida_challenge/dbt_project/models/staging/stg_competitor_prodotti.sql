{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'competitor_prodotti') }}
),

cleaned as (
    select
        competitor,
        tipo_prodotto,
        premio_medio,
        massimale_medio,
        rating_clienti,
        quota_mercato_perc,
        coperture_extra
    from source
)

select * from cleaned
