{{
    config(
        materialized='view'
    )
}}

with clienti as (
    select * from {{ ref('stg_clienti') }}
),

polizze as (
    select * from {{ ref('stg_polizze') }}
),

aggregated as (
    select
        c.codice_cliente,
        c.nome,
        c.cognome,
        c.eta,
        c.professione,
        c.reddito,
        c.stato_civile,
        c.agenzia,
        c.zona_residenza,
        
        -- Policy aggregations
        count(distinct p.prodotto) as num_prodotti_distinti,
        count(*) as num_polizze_totali,
        count(case when p.stato_polizza = 'Attiva' then 1 end) as num_polizze_attive,
        count(case when p.stato_polizza = 'Scaduta' then 1 end) as num_polizze_scadute,
        
        -- Financial aggregations
        sum(p.premio_totale_annuo) as premio_annuo_totale,
        avg(p.premio_totale_annuo) as premio_annuo_medio,
        sum(p.massimale) as massimale_totale,
        sum(p.margine_lordo) as margine_lordo_totale,
        avg(p.loss_ratio) as loss_ratio_medio,
        
        -- Product mix
        count(case when p.area_bisogno = 'Protezione' then 1 end) as num_prodotti_protezione,
        count(case when p.area_bisogno = 'Risparmio e Investimento' then 1 end) as num_prodotti_investimento,
        
        -- Channel distribution
        count(case when p.canale_acquisizione = 'Rete Diretta Agenziale' then 1 end) as num_canale_agenziale,
        count(case when p.canale_acquisizione = 'Online' then 1 end) as num_canale_online,
        
        -- Customer metrics from clienti
        c.engagement_score,
        c.churn_probability,
        c.clv_stimato,
        c.satisfaction_score,
        c.potenziale_crescita
        
    from clienti c
    left join polizze p on c.codice_cliente = p.codice_cliente
    group by 
        c.codice_cliente, c.nome, c.cognome, c.eta, c.professione, 
        c.reddito, c.stato_civile, c.agenzia, c.zona_residenza,
        c.engagement_score, c.churn_probability, c.clv_stimato, 
        c.satisfaction_score, c.potenziale_crescita
)

select * from aggregated
