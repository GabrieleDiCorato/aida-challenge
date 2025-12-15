{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'abitazioni') }}
),

cleaned as (
    select
        codice_cliente,
        "Luogo di Residenza" as luogo_residenza,
        indirizzo,
        metratura,
        sistema_allarme
    from source
)

select * from cleaned
