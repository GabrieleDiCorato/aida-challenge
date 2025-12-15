{{
    config(
        materialized='table'
    )
}}

with polizze as (
    select * from {{ ref('stg_polizze') }}
),

clienti as (
    select * from {{ ref('stg_clienti') }}
),

final as (
    select
        -- Policy identifiers
        p.codice_cliente,
        p.prodotto,
        p.area_bisogno,
        p.stato_polizza,
        
        -- Customer info
        c.nome,
        c.cognome,
        c.eta,
        c.professione,
        c.agenzia,
        c.zona_residenza,
        
        -- Dates
        p.data_emissione,
        p.data_scadenza,
        datediff('day', p.data_emissione, current_date) as giorni_dalla_emissione,
        datediff('day', current_date, p.data_scadenza) as giorni_alla_scadenza,
        
        -- Financial
        p.premio_ricorrente,
        p.premio_unico,
        p.premio_totale_annuo,
        p.massimale,
        p.capitale_rivalutato,
        
        -- Costs and margins
        p.commissione_perc,
        p.commissione_euro,
        p.costi_operativi,
        p.margine_lordo,
        
        -- Performance
        p.loss_ratio,
        p.sinistri_totali,
        p.importo_liquidato,
        
        -- Channel
        p.canale_acquisizione,
        
        -- Policy status flags
        case when p.stato_polizza = 'Attiva' then 1 else 0 end as is_active,
        case when p.data_scadenza < current_date then 1 else 0 end as is_expired,
        case when p.data_scadenza between current_date and current_date + interval '90 days' then 1 else 0 end as is_expiring_soon,
        
        -- Profitability classification
        case
            when p.margine_lordo > 1000 then 'High Margin'
            when p.margine_lordo > 500 then 'Medium Margin'
            when p.margine_lordo > 0 then 'Low Margin'
            else 'Negative Margin'
        end as profitability_tier,
        
        -- Metadata
        current_timestamp as _dbt_loaded_at
        
    from polizze p
    left join clienti c on p.codice_cliente = c.codice_cliente
)

select * from final
