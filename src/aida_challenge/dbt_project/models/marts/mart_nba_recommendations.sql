{{
    config(
        materialized='table'
    )
}}

with nba_data as (
    select * from {{ ref('stg_client_nba_enhanced') }}
),

customers as (
    select * from {{ ref('dim_customers') }}
),

final as (
    select
        -- Customer identifiers
        c.codice_cliente,
        c.nome,
        c.cognome,
        c.eta,
        c.professione,
        c.stato_civile,
        c.agenzia,
        c.zona_residenza,

        -- Customer value & engagement
        c.clv_stimato,
        c.engagement_score,
        c.churn_probability,
        c.satisfaction_score,
        c.segmento_cliente,
        c.classificazione_valore,

        -- Product portfolio
        c.num_prodotti_distinti,
        c.num_polizze_attive,
        c.premio_annuo_totale,
        c.num_prodotti_protezione,
        c.num_prodotti_investimento,

        -- Customer behavior
        c.num_interazioni_totali,
        c.tasso_conversione as tasso_conversione_storico,
        c.num_sinistri_totali,
        c.classificazione_rischio,

        -- NBA recommendations (from external analysis)
        nba.segmento_strategico,
        nba.raccomandazione_nba,
        nba.livello_urgenza,
        nba.cluster,
        nba.tasso_conversione_nba,

        -- Product ownership flags
        nba.possiede_casa,
        nba.possiede_salute,
        nba.possiede_investimento,
        nba.possiede_pip,

        -- Pitch priority score (calculated)
        case
            when nba.livello_urgenza = 'CRITICAL' then 4
            when nba.livello_urgenza = 'HIGH' then 3
            when nba.livello_urgenza = 'MEDIUM' then 2
            when nba.livello_urgenza = 'LOW' then 1
            else 0
        end as punteggio_urgenza,

        -- Recommendation readiness
        case
            when
                nba.livello_urgenza in ('CRITICAL', 'HIGH')
                and c.churn_probability < 0.5
                and c.engagement_score > 50
                then 'Ready to Pitch'
            when
                nba.livello_urgenza in ('CRITICAL', 'HIGH')
                and c.churn_probability >= 0.5
                then 'Retention First'
            when
                nba.livello_urgenza in ('MEDIUM', 'LOW')
                and c.engagement_score > 60
                then 'Nurture & Pitch'
            else 'Monitor'
        end as strategia_pitch,

        -- Gap analysis
        (4 - (nba.possiede_casa + nba.possiede_salute + nba.possiede_investimento + nba.possiede_pip)) as gap_prodotti,

        -- Metadata
        current_timestamp as _dbt_loaded_at

    from customers as c
    inner join nba_data as nba on c.codice_cliente = nba.codice_cliente
)

select * from final
order by punteggio_urgenza desc, clv_estimato desc
