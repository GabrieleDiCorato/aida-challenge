{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'clienti') }}
),

cleaned as (
    select
        -- Primary key
        codice_cliente,

        -- Demographics
        "Nome" as nome,
        "Cognome" as cognome,
        "Età" as eta,
        "Luogo di Nascita" as luogo_nascita,
        "Luogo di Residenza" as luogo_residenza,
        "Professione" as professione,
        "Stato Civile" as stato_civile,

        -- Financial
        "Reddito" as reddito,
        "Reddito Familiare" as reddito_familiare,
        "Reddito Stimato" as reddito_stimato,
        "Patrimonio Finanziario Stimato" as patrimonio_finanziario,
        "Patrimonio Reale Stimato" as patrimonio_reale,
        "Consumi Stimati" as consumi_stimati,

        -- Family
        "Numero Figli" as numero_figli,
        "Numero Familiari a Carico" as numero_familiari_carico,

        -- Company relationship
        "Anzianità con la Compagnia" as anzianita_compagnia,
        "Agenzia" as agenzia,
        "Num_Polizze" as num_polizze,

        -- Scores & metrics
        "Engagement_Score" as engagement_score,
        "Churn_Probability" as churn_probability,
        "CLV_Stimato" as clv_stimato,
        "Potenziale_Crescita" as potenziale_crescita,
        "Reclami_Totali" as reclami_totali,
        "Satisfaction_Score" as satisfaction_score,

        -- Propensity scores
        "Propensione Acquisto Prodotti Vita" as propensione_vita,
        "Propensione Acquisto Prodotti Danni" as propensione_danni,

        -- Geographic
        "Latitudine" as latitudine,
        "Longitudine" as longitudine,
        "Zona di Residenza" as zona_residenza,
        "Valore Immobiliare Medio" as valore_immobiliare_medio,
        "Probabilità Furti Stimata" as probabilita_furti,
        "Probabilità Rapine Stimata" as probabilita_rapine,

        -- Activity
        "Data_Ultima_Visita" as data_ultima_visita,
        "Visite_Ultimo_Anno" as visite_ultimo_anno,
        "Cluster_Risposta" as cluster_risposta

    from source
)

select * from cleaned
