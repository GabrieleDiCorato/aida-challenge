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
        "Prodotto" as prodotto,
        "Area di Bisogno" as area_bisogno,
        "Sinistro" as sinistro,
        "Data_Sinistro" as data_sinistro,
        "Importo_Liquidato" as importo_liquidato,
        "Stato_Liquidazione" as stato_liquidazione
    from source
    where sinistro is not null  -- Filter out null claims
)

select * from cleaned
