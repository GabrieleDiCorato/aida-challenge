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
        prodotto,
        "Area di Bisogno" as area_bisogno,
        stato_polizza,
        canale_acquisizione,
        
        -- Dates
        "Data di Emissione" as data_emissione,
        data_scadenza,
        
        -- Financial
        premio_ricorrente,
        premio_unico,
        premio_totale_annuo,
        capitale_rivalutato,
        massimale,
        
        -- Costs & margins
        commissione_perc,
        commissione_euro,
        costi_operativi,
        margine_lordo,
        
        -- Claims
        importo_liquidato,
        sinistri_totali,
        loss_ratio
        
    from source
)

select * from cleaned
