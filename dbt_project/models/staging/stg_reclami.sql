{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'reclami') }}
),

cleaned as (
    select
        codice_cliente,
        prodotto,
        "Area di Bisogno" as area_bisogno,
        reclami_e_info
    from source
    where reclami_e_info is not null  -- Filter out null complaints
)

select * from cleaned
