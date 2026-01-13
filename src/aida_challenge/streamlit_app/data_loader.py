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
    # Database is at project root/data, streamlit_app is 3 levels deep
    db_path = Path(__file__).parent.parent.parent.parent / "data" / "aida_challenge.duckdb"
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


@st.cache_data(ttl=3600)
def get_customer_list():
    """Get list of all customers for dropdown selection."""
    con = get_db_connection()
    return con.execute(
        """
        SELECT
            codice_cliente,
            Nome || ' ' || Cognome as full_name,
            Professione as profession,
            "Luogo di Residenza" as city
        FROM main.clienti
        ORDER BY Cognome, Nome
    """
    ).df()


def get_customer_full_profile(codice_cliente: int) -> dict:
    """
    Get complete 360° customer profile for sales pitch generation.

    Returns a dictionary with:
    - demographics: Customer personal info and scores
    - policies: List of active and expired policies
    - interactions: Recent interaction history
    - claims: Claims history
    - complaints: Complaints history
    - housing: Housing information (if available)
    """
    con = get_db_connection()

    # Convert to native Python int to avoid numpy type issues
    codice_cliente = int(codice_cliente)

    # Customer demographics from dim_customers (mart)
    demographics = con.execute(
        """
        SELECT
            codice_cliente,
            nome,
            cognome,
            eta,
            professione,
            reddito,
            stato_civile,
            agenzia,
            zona_residenza,
            num_prodotti_distinti,
            num_polizze_totali,
            num_polizze_attive,
            premio_annuo_totale,
            premio_annuo_medio,
            margine_lordo_totale,
            num_prodotti_protezione,
            num_prodotti_investimento,
            engagement_score,
            churn_probability,
            clv_stimato,
            satisfaction_score,
            potenziale_crescita,
            num_interazioni_totali,
            num_conversioni,
            tasso_conversione,
            num_sinistri_totali,
            importo_totale_liquidato,
            frequenza_sinistri_annua,
            segmento_cliente,
            classificazione_rischio,
            classificazione_valore
        FROM aida_challenge.main_marts.dim_customers
        WHERE codice_cliente = ?
    """,
        [codice_cliente],
    ).df()

    # Active policies
    policies = con.execute(
        """
        SELECT
            prodotto,
            area_bisogno,
            stato_polizza,
            premio_totale_annuo,
            massimale,
            canale_acquisizione,
            data_emissione,
            data_scadenza,
            loss_ratio,
            margine_lordo
        FROM aida_challenge.main_staging.stg_polizze
        WHERE codice_cliente = ?
        ORDER BY stato_polizza DESC, data_emissione DESC
    """,
        [codice_cliente],
    ).df()

    # Interaction history (last 20)
    interactions = con.execute(
        """
        SELECT
            tipo_interazione,
            motivo,
            esito,
            conversione,
            durata_minuti,
            data_interazione
        FROM aida_challenge.main_staging.stg_interazioni_clienti
        WHERE codice_cliente = ?
        ORDER BY data_interazione DESC
        LIMIT 20
    """,
        [codice_cliente],
    ).df()

    # Claims history
    claims = con.execute(
        """
        SELECT
            prodotto,
            sinistro,
            importo_liquidato,
            stato_liquidazione,
            data_sinistro
        FROM aida_challenge.main_staging.stg_sinistri
        WHERE codice_cliente = ?
        ORDER BY data_sinistro DESC
    """,
        [codice_cliente],
    ).df()

    # Complaints
    complaints = con.execute(
        """
        SELECT
            reclami_e_info as reclami_info,
            prodotto,
            area_bisogno
        FROM aida_challenge.main_staging.stg_reclami
        WHERE codice_cliente = ?
    """,
        [codice_cliente],
    ).df()

    # Housing info
    housing = con.execute(
        """
        SELECT
            indirizzo,
            metratura,
            sistema_allarme
        FROM aida_challenge.main_staging.stg_abitazioni
        WHERE codice_cliente = ?
    """,
        [codice_cliente],
    ).df()

    return {
        "demographics": demographics.to_dict(orient="records")[0] if len(demographics) > 0 else {},
        "policies": policies.to_dict(orient="records"),
        "interactions": interactions.to_dict(orient="records"),
        "claims": claims.to_dict(orient="records"),
        "complaints": complaints.to_dict(orient="records"),
        "housing": housing.to_dict(orient="records"),
    }
