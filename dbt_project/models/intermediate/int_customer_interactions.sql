{{
    config(
        materialized='view'
    )
}}

with interazioni as (
    select * from {{ ref('stg_interazioni_clienti') }}
),

aggregated as (
    select
        codice_cliente,
        
        -- Interaction counts
        count(*) as num_interazioni_totali,
        count(distinct tipo_interazione) as num_tipi_interazione,
        
        -- By type
        count(case when tipo_interazione = 'Visita Agente' then 1 end) as num_visite_agente,
        count(case when tipo_interazione = 'Chat Online' then 1 end) as num_chat_online,
        count(case when tipo_interazione = 'Telefono' then 1 end) as num_telefonate,
        count(case when tipo_interazione = 'App Mobile' then 1 end) as num_app_mobile,
        count(case when tipo_interazione = 'Email' then 1 end) as num_email,
        
        -- By outcome
        count(case when esito = 'Positivo' then 1 end) as num_esiti_positivi,
        count(case when esito = 'Negativo' then 1 end) as num_esiti_negativi,
        count(case when esito = 'Neutrale' then 1 end) as num_esiti_neutrali,
        
        -- Conversion metrics
        count(case when conversione = true then 1 end) as num_conversioni,
        count(case when conversione = true then 1 end)::float / count(*)::float as tasso_conversione,
        
        -- By reason
        count(case when motivo = 'Consulenza' then 1 end) as num_consulenza,
        count(case when motivo = 'Reclamo' then 1 end) as num_reclami_interazioni,
        count(case when motivo = 'Pagamento Premio' then 1 end) as num_pagamenti,
        count(case when motivo = 'Informazioni Prodotto' then 1 end) as num_info_prodotto,
        
        -- Duration metrics
        avg(durata_minuti) as durata_media_minuti,
        sum(durata_minuti) as durata_totale_minuti,
        max(durata_minuti) as durata_max_minuti,
        
        -- Dates
        min(data_interazione) as prima_interazione,
        max(data_interazione) as ultima_interazione,
        datediff('day', min(data_interazione), max(data_interazione)) as giorni_tra_prima_ultima
        
    from interazioni
    group by codice_cliente
)

select * from aggregated
