{{
    config(
        materialized='view',
        schema='staging'
    )
}}

with nba_data as (
    select * from {{ source('analytics', 'nba_enhanced') }}
),

-- Get latest version for each customer
latest_version as (
    select
        codice_cliente,
        max(versione_modello) as versione_modello
    from nba_data
    group by codice_cliente
),

final as (
    select
        nba.codice_cliente,
        nba.cluster_id,
        nba.raccomandazione_nba_cluster as raccomandazione_nba,
        nba.livello_urgenza_adjusted as livello_urgenza,
        nba.canale_migliore as canale_contatto_preferito,
        nba.versione_modello,
        current_timestamp as _dbt_loaded_at
    from nba_data as nba
    inner join latest_version as lv
        on
            nba.codice_cliente = lv.codice_cliente
            and nba.versione_modello = lv.versione_modello
)

select * from final
