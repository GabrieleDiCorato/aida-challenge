{{
    config(
        materialized='view',
        schema='intermediate'
    )
}}

with clienti as (
    select * from {{ ref('stg_clienti') }}
),

interactions as (
    select * from {{ ref('int_customer_interactions') }}
),

claims as (
    select * from {{ ref('int_customer_claims') }}
),

reclami as (
    select
        codice_cliente,
        count(*) as num_reclami
    from {{ source('raw', 'reclami') }}
    group by codice_cliente
),

engagement_quantiles as (
    -- Calculate quantiles for engagement classification
    select
        percentile_cont(0.33) within group (
            order by engagement_score
        ) as engagement_q33,
        percentile_cont(0.67) within group (
            order by engagement_score
        ) as engagement_q67
    from clienti
),

final as (
    select
        c.codice_cliente,
        c.engagement_score,
        c.churn_probability,
        c.clv_stimato,
        c.satisfaction_score,
        c.data_ultima_visita,

        -- Days since last visit
        case
            when c.data_ultima_visita is not null
                then date_diff('day', c.data_ultima_visita, current_date)
            else 9999
        end as giorni_ultima_visita,

        -- Urgency tier based on recency
        case
            when c.data_ultima_visita is null then 'LOW'
            when date_diff('day', c.data_ultima_visita, current_date) <= 90 then 'CRITICAL'
            when date_diff('day', c.data_ultima_visita, current_date) <= 180 then 'HIGH'
            when date_diff('day', c.data_ultima_visita, current_date) <= 365 then 'MEDIUM'
            else 'LOW'
        end as livello_urgenza,

        -- Engagement level classification
        case
            when c.engagement_score >= eq.engagement_q67 and c.churn_probability < 0.33 then 'Champion'
            when c.engagement_score <= eq.engagement_q33 or c.churn_probability >= 0.67 then 'At-Risk'
            else 'Neutral'
        end as livello_engagement,

        -- Interaction metrics
        coalesce(i.num_interazioni_totali, 0) as num_interazioni,
        coalesce(i.num_conversioni, 0) as num_conversioni,
        coalesce(i.tasso_conversione, 0) as tasso_conversione,
        coalesce(i.durata_media_minuti, 0) as durata_media_interazioni,

        -- Claims and complaints
        coalesce(cl.num_sinistri_totali, 0) as num_sinistri,
        coalesce(cl.importo_totale_liquidato, 0) as importo_sinistri_totale,
        coalesce(r.num_reclami, 0) as num_reclami,

        current_timestamp as _dbt_loaded_at

    from clienti as c
    cross join engagement_quantiles as eq
    left join interactions as i on c.codice_cliente = i.codice_cliente
    left join claims as cl on c.codice_cliente = cl.codice_cliente
    left join reclami as r on c.codice_cliente = r.codice_cliente
)

select * from final
