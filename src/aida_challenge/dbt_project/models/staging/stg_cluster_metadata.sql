{{
    config(
        materialized='view',
        schema='staging'
    )
}}

with metadata as (
    select * from {{ source('analytics', 'cluster_metadata') }}
),

-- Get latest version
latest_version as (
    select max(versione_modello) as versione_modello
    from metadata
),

final as (
    select
        m.cluster_id,
        m.etichetta_cluster,
        m.num_clienti,
        m.silhouette_score as punteggio_silhouette,
        m.caratteristiche_json,
        m.versione_modello,
        current_timestamp as _dbt_loaded_at
    from metadata as m
    inner join latest_version as lv
        on m.versione_modello = lv.versione_modello
)

select * from final
