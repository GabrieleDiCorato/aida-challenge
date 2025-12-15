{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'sinistri') }}
),

cleaned as (
    select
        codice_cliente,
        prodotto,
        "Area di Bisogno" as area_bisogno,
        sinistro,
        data_sinistro,
        importo_liquidato,
        stato_liquidazione
    from source
    where sinistro is not null  -- Filter out null claims
)

select * from cleaned
