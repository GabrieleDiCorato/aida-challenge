{{
    config(
        materialized='view',
        schema='staging'
    )
}}

with cluster_data as (
    select * from {{ source('analytics', 'customer_clusters') }}
),

-- Get latest version for each customer (in case multiple versions exist)
latest_version as (
    select
        codice_cliente,
        max(versione_modello) as versione_modello
    from cluster_data
    group by codice_cliente
),

final as (
    select
        cd.codice_cliente,
        cd.cluster as cluster_id,
        cd.segmento_valore,
        cd.fase_vita,
        cd.num_prodotti_posseduti,
        cd.versione_modello,
        current_timestamp as _dbt_loaded_at
    from cluster_data as cd
    inner join latest_version as lv
        on
            cd.codice_cliente = lv.codice_cliente
            and cd.versione_modello = lv.versione_modello
)

select * from final
