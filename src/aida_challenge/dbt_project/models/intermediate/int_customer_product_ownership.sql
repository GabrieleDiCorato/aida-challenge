{{
    config(
        materialized='view',
        schema='intermediate'
    )
}}

with polizze as (
    select * from {{ ref('stg_polizze') }}
),

product_classification as (
    select
        codice_cliente,
        lower(replace(area_di_bisogno, ' ', '_')) as categoria_prodotto
    from polizze
    where stato_polizza = 'Attiva'
),

product_flags as (
    select
        codice_cliente,

        -- Create binary ownership flags for each major product category
        max(case when categoria_prodotto like '%casa%' or categoria_prodotto like '%abitazione%' then 1 else 0 end)
            as possiede_casa,
        max(case when categoria_prodotto like '%salute%' or categoria_prodotto like '%malattia%' then 1 else 0 end)
            as possiede_salute,
        max(
            case
                when categoria_prodotto like '%investimento%' or categoria_prodotto like '%risparmio%' then 1 else 0
            end
        ) as possiede_investimento,
        max(
            case
                when
                    categoria_prodotto like '%pip%'
                    or categoria_prodotto like '%pensione%'
                    or categoria_prodotto like '%previdenza%'
                    then 1
                else 0
            end
        ) as possiede_pip,

        -- Count distinct product categories
        count(distinct categoria_prodotto) as num_categorie_prodotto

    from product_classification
    group by codice_cliente
),

all_customers as (
    -- Ensure all customers are included, even those without active policies
    select distinct codice_cliente
    from {{ ref('stg_clienti') }}
),

final as (
    select
        ac.codice_cliente,
        coalesce(pf.possiede_casa, 0) as possiede_casa,
        coalesce(pf.possiede_salute, 0) as possiede_salute,
        coalesce(pf.possiede_investimento, 0) as possiede_investimento,
        coalesce(pf.possiede_pip, 0) as possiede_pip,
        coalesce(pf.num_categorie_prodotto, 0) as num_categorie_prodotto,

        -- Total products owned
        coalesce(pf.possiede_casa, 0)
        + coalesce(pf.possiede_salute, 0)
        + coalesce(pf.possiede_investimento, 0)
        + coalesce(pf.possiede_pip, 0) as num_prodotti_posseduti,

        current_timestamp as _dbt_loaded_at

    from all_customers as ac
    left join product_flags as pf on ac.codice_cliente = pf.codice_cliente
)

select * from final
