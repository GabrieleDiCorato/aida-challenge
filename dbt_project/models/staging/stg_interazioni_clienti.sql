{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'interazioni_clienti') }}
),

cleaned as (
    select
        codice_cliente,
        data_interazione,
        tipo_interazione,
        motivo,
        durata_minuti,
        esito,
        note,
        conversione
    from source
)

select * from cleaned
