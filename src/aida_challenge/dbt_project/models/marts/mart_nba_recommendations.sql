{{
    config(
        materialized='table'
    )
}}

with strategic_segment as (
    -- Use new intermediate model for base segmentation
    select * from {{ ref('int_customer_strategic_segment') }}
),

customers as (
    select * from {{ ref('dim_customers') }}
),

nba_enhanced as (
    -- Use new cluster-aware NBA recommendations if available
    select * from {{ ref('stg_nba_enhanced') }}
),

cluster_metadata as (
    -- Get cluster labels and characteristics
    select * from {{ ref('stg_cluster_metadata') }}
),

nba_pitch as (
    select * from {{ ref('stg_client_nba_pitch') }}
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

        -- Strategic segmentation (from dbt models)
        seg.segmento_strategico,
        seg.segmento_valore,
        seg.fase_vita,
        seg.livello_engagement,
        seg.patrimonio_totale,

        -- Product ownership flags
        seg.possiede_casa,
        seg.possiede_salute,
        seg.possiede_investimento,
        seg.possiede_pip,
        seg.num_prodotti_posseduti,

        -- NBA recommendations (cluster-aware if available, fallback to base)
        nba_enh.cluster_id,
        cm.etichetta_cluster as descrizione_cluster,

        -- Cluster information
        cm.num_clienti as num_clienti_cluster,
        cm.punteggio_silhouette as qualita_cluster,
        nba_enh.canale_contatto_preferito,
        pitch.testo_pitch,

        -- Best contact channel
        nba_enh.versione_modello as versione_nba,

        -- Pitch text (cached)
        coalesce(nba_enh.raccomandazione_nba, seg.raccomandazione_nba) as raccomandazione_nba,

        -- Recommendation readiness score
        coalesce(nba_enh.livello_urgenza, seg.livello_urgenza) as livello_urgenza,

        -- Pitch strategy
        case
            when coalesce(nba_enh.livello_urgenza, seg.livello_urgenza) = 'CRITICAL' then 4
            when coalesce(nba_enh.livello_urgenza, seg.livello_urgenza) = 'HIGH' then 3
            when coalesce(nba_enh.livello_urgenza, seg.livello_urgenza) = 'MEDIUM' then 2
            when coalesce(nba_enh.livello_urgenza, seg.livello_urgenza) = 'LOW' then 1
            else 0
        end as punteggio_urgenza,

        -- Product gap count
        case
            when
                coalesce(nba_enh.livello_urgenza, seg.livello_urgenza) in ('CRITICAL', 'HIGH')
                and c.churn_probability < 0.5
                and c.engagement_score > 50
                then 'Ready to Pitch'
            when
                coalesce(nba_enh.livello_urgenza, seg.livello_urgenza) in ('CRITICAL', 'HIGH')
                and c.churn_probability >= 0.5
                then 'Retention First'
            when
                coalesce(nba_enh.livello_urgenza, seg.livello_urgenza) in ('MEDIUM', 'LOW')
                and c.engagement_score > 60
                then 'Nurture & Pitch'
            else 'Monitor'
        end as strategia_pitch,

        -- Model version tracking
        (4 - seg.num_prodotti_posseduti) as gap_prodotti,

        -- Metadata
        current_timestamp as _dbt_loaded_at

    from customers as c
    inner join strategic_segment as seg
        on c.codice_cliente = seg.codice_cliente
    left join nba_enhanced as nba_enh
        on c.codice_cliente = nba_enh.codice_cliente
    left join cluster_metadata as cm
        on nba_enh.cluster_id = cm.cluster_id
    left join nba_pitch as pitch
        on c.codice_cliente = pitch.codice_cliente
)

select * from final
order by punteggio_urgenza desc, clv_stimato desc
