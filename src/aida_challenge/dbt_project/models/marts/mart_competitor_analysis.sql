{{
    config(
        materialized='table'
    )
}}

with our_products as (
    select
        'AIDA Insurance' as compagnia,
        area_bisogno as tipo_prodotto,
        avg(premio_totale_annuo) as premio_medio,
        avg(massimale) as massimale_medio,
        count(*) as num_polizze
    from {{ ref('stg_polizze') }}
    where stato_polizza = 'Attiva'
    group by area_bisogno
),

competitors as (
    select
        competitor as compagnia,
        tipo_prodotto,
        premio_medio,
        massimale_medio,
        rating_clienti,
        quota_mercato_perc
    from {{ ref('stg_competitor_prodotti') }}
),

our_enriched as (
    select
        compagnia,
        tipo_prodotto,
        premio_medio,
        massimale_medio,
        null as rating_clienti,
        null as quota_mercato_perc,
        num_polizze,
        'Internal' as fonte
    from our_products
),

competitors_enriched as (
    select
        compagnia,
        tipo_prodotto,
        premio_medio,
        massimale_medio,
        rating_clienti,
        quota_mercato_perc,
        null as num_polizze,
        'Competitor' as fonte
    from competitors
),

combined as (
    select * from our_enriched
    union all
    select * from competitors_enriched
),

with_rankings as (
    select
        *,
        rank() over (
            partition by tipo_prodotto
            order by premio_medio
        ) as rank_premio,
        rank() over (
            partition by tipo_prodotto
            order by massimale_medio desc
        ) as rank_copertura,
        rank() over (
            partition by tipo_prodotto
            order by rating_clienti desc nulls last
        ) as rank_rating
    from combined
)

select * from with_rankings
