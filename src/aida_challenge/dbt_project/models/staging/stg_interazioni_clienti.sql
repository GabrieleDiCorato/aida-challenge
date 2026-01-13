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
        "Data_Interazione" as data_interazione,
        "Tipo_Interazione" as tipo_interazione,
        "Motivo" as motivo,
        "Durata_Minuti" as durata_minuti,
        "Esito" as esito,
        "Note" as note,
        "Conversione" as conversione
    from source
)

select * from cleaned
