"""
Data loading utilities for the AIDA Challenge Dashboard.
The data is loaded from a DuckDB database and cached for performance.
This is absolutely fine in this context, as the data is static, read-only, and easily fits in memory.
"""

import duckdb
from pathlib import Path
import streamlit as st


@st.cache_resource
def get_db_connection():
    """Create and cache database connection."""
    db_path = Path("data/aida_challenge.duckdb").absolute()
    return duckdb.connect(str(db_path), read_only=True)


@st.cache_data(ttl=3600)
def load_customer_demographics():
    """Load customer demographic data."""
    con = get_db_connection()
    return con.execute(
        """
        SELECT
            codice_cliente as customer_id,
            eta as age,
            reddito as income,
            professione as profession,
            luogo_residenza as city,
            cluster_risposta as cluster,
            engagement_score,
            churn_probability,
            clv_stimato as clv,
            satisfaction_score,
            num_polizze as policy_count,
            anzianita_compagnia as tenure_years,
            visite_ultimo_anno as annual_visits
        FROM aida_challenge.main_staging.stg_clienti
    """
    ).df()


@st.cache_data(ttl=3600)
def load_policy_data():
    """Load policy and portfolio data."""
    con = get_db_connection()
    return con.execute(
        """
        SELECT
            codice_cliente as customer_id,
            prodotto as product,
            area_bisogno as need_area,
            premio_totale_annuo as annual_premium,
            stato_polizza as policy_status,
            canale_acquisizione as acquisition_channel,
            loss_ratio,
            margine_lordo as gross_margin,
            data_emissione,
            data_scadenza
        FROM aida_challenge.main_staging.stg_polizze
    """
    ).df()


@st.cache_data(ttl=3600)
def load_interaction_data():
    """Load customer interaction data."""
    con = get_db_connection()
    return con.execute(
        """
        SELECT
            codice_cliente as customer_id,
            tipo_interazione as interaction_type,
            durata_minuti as duration_minutes,
            conversione as conversion,
            data_interazione as interaction_date
        FROM aida_challenge.main_staging.stg_interazioni_clienti
    """
    ).df()


@st.cache_data(ttl=3600)
def load_geographic_data():
    """Load customer geographic data."""
    con = get_db_connection()
    return con.execute(
        """
        SELECT
            codice_cliente as customer_id,
            latitudine as lat,
            longitudine as lon,
            luogo_residenza as city,
            clv_stimato as clv
        FROM aida_challenge.main_staging.stg_clienti
        WHERE latitudine IS NOT NULL
            AND longitudine IS NOT NULL
    """
    ).df()


@st.cache_data(ttl=3600)
def load_cluster_summary():
    """Load cluster characteristics summary."""
    con = get_db_connection()
    return con.execute(
        """
        SELECT
            cluster_risposta as cluster,
            COUNT(*) as customer_count,
            AVG(eta) as avg_age,
            AVG(reddito) as avg_income,
            AVG(num_polizze) as avg_policies,
            AVG(clv_stimato) as avg_clv,
            AVG(engagement_score) as avg_engagement,
            AVG(churn_probability) as avg_churn_risk,
            AVG(satisfaction_score) as avg_satisfaction
        FROM aida_challenge.main_staging.stg_clienti
        WHERE cluster_risposta IS NOT NULL
        GROUP BY cluster_risposta
        ORDER BY cluster_risposta
    """
    ).df()


@st.cache_data(ttl=3600)
def load_channel_performance():
    """Load channel acquisition and performance data."""
    con = get_db_connection()
    return con.execute(
        """
        SELECT
            p.canale_acquisizione as channel,
            COUNT(DISTINCT p.codice_cliente) as customer_count,
            AVG(c.clv_stimato) as avg_clv,
            AVG(c.engagement_score) as avg_engagement,
            AVG(p.premio_totale_annuo) as avg_premium,
            SUM(p.premio_totale_annuo) as total_revenue,
            SUM(p.margine_lordo) as total_margin
        FROM aida_challenge.main_staging.stg_polizze p
        JOIN aida_challenge.main_staging.stg_clienti c
            ON p.codice_cliente = c.codice_cliente
        WHERE p.stato_polizza = 'Attiva'
        GROUP BY p.canale_acquisizione
        ORDER BY total_revenue DESC
    """
    ).df()


@st.cache_data(ttl=3600)
def load_product_performance():
    """Load product performance metrics."""
    con = get_db_connection()
    return con.execute(
        """
        SELECT
            prodotto as product,
            area_bisogno as need_area,
            AVG(loss_ratio) as avg_loss_ratio,
            SUM(premio_totale_annuo) as total_premium,
            SUM(margine_lordo) as total_margin,
            COUNT(*) as policy_count,
            AVG(premio_totale_annuo) as avg_premium
        FROM aida_challenge.main_staging.stg_polizze
        WHERE stato_polizza = 'Attiva'
        GROUP BY prodotto, area_bisogno
        ORDER BY total_premium DESC
    """
    ).df()


@st.cache_data(ttl=3600)
def load_interaction_summary():
    """Load interaction type summary."""
    con = get_db_connection()
    return con.execute(
        """
        SELECT
            tipo_interazione as interaction_type,
            COUNT(*) as interaction_count,
            AVG(durata_minuti) as avg_duration,
            SUM(CASE WHEN conversione THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as conversion_rate
        FROM aida_challenge.main_staging.stg_interazioni_clienti
        GROUP BY tipo_interazione
        ORDER BY interaction_count DESC
    """
    ).df()


# Raw staging table loaders - 1:1 with source tables
@st.cache_data(ttl=3600)
def load_raw_clienti():
    """Load raw clienti table."""
    con = get_db_connection()
    return con.execute("SELECT * FROM main.clienti").df()


@st.cache_data(ttl=3600)
def load_raw_polizze():
    """Load raw polizze table."""
    con = get_db_connection()
    return con.execute("SELECT * FROM main.polizze").df()


@st.cache_data(ttl=3600)
def load_raw_sinistri():
    """Load raw sinistri table."""
    con = get_db_connection()
    return con.execute("SELECT * FROM main.sinistri").df()


@st.cache_data(ttl=3600)
def load_raw_reclami():
    """Load raw reclami table."""
    con = get_db_connection()
    return con.execute("SELECT * FROM main.reclami").df()


@st.cache_data(ttl=3600)
def load_raw_abitazioni():
    """Load raw abitazioni table."""
    con = get_db_connection()
    return con.execute("SELECT * FROM main.abitazioni").df()


@st.cache_data(ttl=3600)
def load_raw_interazioni_clienti():
    """Load raw interazioni_clienti table."""
    con = get_db_connection()
    return con.execute("SELECT * FROM main.interazioni_clienti").df()


@st.cache_data(ttl=3600)
def load_raw_competitor_prodotti():
    """Load raw competitor_prodotti table."""
    con = get_db_connection()
    return con.execute("SELECT * FROM main.competitor_prodotti").df()
