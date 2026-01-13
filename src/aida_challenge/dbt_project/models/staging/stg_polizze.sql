{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'polizze') }}
),

cleaned as (
    select
        -- Foreign key
        codice_cliente,

        -- Product info
        "Prodotto" as prodotto,
        "Area di Bisogno" as area_bisogno,
        "Stato_Polizza" as stato_polizza,
        "Canale_Acquisizione" as canale_acquisizione,

        -- Dates
        "Data di Emissione" as data_emissione,
        "Data_Scadenza" as data_scadenza,

        -- Financial
        "Premio_Ricorrente" as premio_ricorrente,
        "Premio_Unico" as premio_unico,
        "Premio_Totale_Annuo" as premio_totale_annuo,
        "Capitale_Rivalutato" as capitale_rivalutato,
        "Massimale" as massimale,

        -- Costs & margins
        "Commissione_Perc" as commissione_perc,
        "Commissione_Euro" as commissione_euro,
        "Costi_Operativi" as costi_operativi,
        "Margine_Lordo" as margine_lordo,

        -- Claims
        "Importo_Liquidato" as importo_liquidato,
        "Sinistri_Totali" as sinistri_totali,
        "Loss_Ratio" as loss_ratio

    from source
)

select * from cleaned
