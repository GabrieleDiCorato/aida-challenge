{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('analytics', 'client_nba_pitch') }}
),

cleaned as (
    select
        -- Primary key
        codice_cliente,

        raccomandazione_nba,
        pitch_suggestion as testo_pitch

    from source
)

select * from cleaned
