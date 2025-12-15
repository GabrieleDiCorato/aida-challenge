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
        nome,
        cognome,
        "Età" as eta,
        "Luogo di Nascita" as luogo_nascita,
        "Luogo di Residenza" as luogo_residenza,
        professione,
        "Stato Civile" as stato_civile,

        -- Financial
        reddito,
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
        agenzia,
        num_polizze,

        -- Scores & metrics
        engagement_score,
        churn_probability,
        clv_stimato,
        potenziale_crescita,
        reclami_totali,
        satisfaction_score,

        -- Propensity scores
        "Propensione Acquisto Prodotti Vita" as propensione_vita,
        "Propensione Acquisto Prodotti Danni" as propensione_danni,

        -- Geographic
        latitudine,
        longitudine,
        "Zona di Residenza" as zona_residenza,
        "Valore Immobiliare Medio" as valore_immobiliare_medio,
        "Probabilità Furti Stimata" as probabilita_furti,
        "Probabilità Rapine Stimata" as probabilita_rapine,

        -- Activity
        data_ultima_visita,
        visite_ultimo_anno,
        cluster_risposta

    from source
)

select * from cleaned
