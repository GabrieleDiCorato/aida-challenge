{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('analytics', 'client_nba_enhanced') }}
),

cleaned as (
    select
        -- Primary key
        codice_cliente,

        -- Strategic segmentation (new analysis)
        strategic_segment as segmento_strategico,
        nba_recommendation as raccomandazione_nba,
        urgency_tier as livello_urgenza,
        cluster,

        -- Performance metrics (new calculations)
        conversion_rate as tasso_conversione_nba,

        -- Product ownership flags (derived from policies)
        casa_owned as possiede_casa,
        salute_owned as possiede_salute,
        investimento_owned as possiede_investimento,
        pip_owned as possiede_pip

        -- Excluded columns (duplicated from other sources):
        -- value_segment, life_stage, num_products, engagement_level (from dim_customers)
        -- num_claims, total_claim_amount (from int_customer_claims)
        -- num_complaints, num_interactions (from int_customer_interactions)

    from source
)

select * from cleaned
