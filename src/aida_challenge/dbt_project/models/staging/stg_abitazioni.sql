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
        "Indirizzo" as indirizzo,
        "Metratura" as metratura,
        "Sistema_Allarme" as sistema_allarme
    from source
)

select * from cleaned
