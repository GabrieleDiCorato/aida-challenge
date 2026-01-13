"""
Sales Chatbot - AI-Powered Sales Pitch Generator

This Streamlit page provides an interface for salespeople to:
1. Select a customer from the database
2. Choose a product to pitch
3. Generate a personalized sales pitch using AI agents
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from aida_challenge.streamlit_app.data_loader import (
    get_customer_list,
    get_customer_full_profile,
)
from aida_challenge.agents import generate_sales_pitch, SalesPitch

# Page configuration
st.set_page_config(
    page_title="Sales Assistant - Vita Sicura",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .pitch-section {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .pitch-header {
        color: #1f77b4;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .customer-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-highlight {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2ecc71;
    }
    .metric-warning {
        font-size: 1.2rem;
        font-weight: bold;
        color: #e74c3c;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Available products
PRODUCTS = [
    "Casa Serena",
    "PIP Pensione Serenità",
    "Salute Protetta",
    "Vita Futuro Sicuro",
    "Vita Risparmio Costante",
]

# Product descriptions
PRODUCT_INFO = {
    "Casa Serena": {
        "type": "Assicurazione Casa",
        "area": "Protezione",
        "description": "Polizza multirischio per la casa e la famiglia con copertura danni e RC.",
    },
    "PIP Pensione Serenità": {
        "type": "Piano Pensionistico",
        "area": "Risparmio e Investimento",
        "description": "Piano individuale pensionistico con vantaggi fiscali e rendita garantita.",
    },
    "Salute Protetta": {
        "type": "Assicurazione Salute",
        "area": "Protezione",
        "description": "Copertura sanitaria completa con rimborso spese mediche e ricovero.",
    },
    "Vita Futuro Sicuro": {
        "type": "Assicurazione Vita",
        "area": "Risparmio e Investimento",
        "description": "Polizza vita a premio unico con capitale garantito e partecipazione utili.",
    },
    "Vita Risparmio Costante": {
        "type": "Assicurazione Vita",
        "area": "Risparmio e Investimento",
        "description": "Piano di accumulo con versamenti programmati e protezione caso morte.",
    },
}


def render_customer_card(profile: dict) -> None:
    """Render the customer profile card."""
    demo = profile.get("demographics", {})

    st.markdown("### 👤 Profilo Cliente")

    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Segmento",
            demo.get("segmento_cliente", "N/A"),
        )

    with col2:
        churn = demo.get("churn_probability", 0)
        st.metric(
            "Probabilità Churn",
            f"{churn:.1%}",
            delta=None,
            delta_color="inverse" if churn > 0.5 else "normal",
        )

    with col3:
        st.metric(
            "CLV Stimato",
            f"€{demo.get('clv_stimato', 0):,.0f}",
        )

    with col4:
        st.metric(
            "Satisfaction",
            f"{demo.get('satisfaction_score', 0):.1f}/100",
        )

    # Customer details expanders
    with st.expander("📋 Dati Anagrafici", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Nome:** {demo.get('nome', '')} {demo.get('cognome', '')}")
            st.write(f"**Età:** {demo.get('eta', 'N/A')} anni")
            st.write(f"**Professione:** {demo.get('professione', 'N/A')}")
        with col2:
            st.write(f"**Reddito:** €{demo.get('reddito', 0):,.0f}")
            st.write(f"**Stato Civile:** {demo.get('stato_civile', 'N/A')}")
            st.write(f"**Zona:** {demo.get('zona_residenza', 'N/A')}")

    with st.expander("📊 Portfolio Attuale"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Polizze Attive", demo.get("num_polizze_attive", 0))
        with col2:
            st.metric("Premio Totale", f"€{demo.get('premio_annuo_totale', 0):,.0f}")
        with col3:
            st.metric("Margine", f"€{demo.get('margine_lordo_totale', 0):,.0f}")

        # Show policies table
        policies = profile.get("policies", [])
        if policies:
            policies_df = pd.DataFrame(policies)
            if len(policies_df) > 0:
                display_cols = [
                    "prodotto",
                    "area_bisogno",
                    "stato_polizza",
                    "premio_totale_annuo",
                ]
                available_cols = [c for c in display_cols if c in policies_df.columns]
                st.dataframe(
                    policies_df[available_cols],
                    use_container_width=True,
                    hide_index=True,
                )

    with st.expander("📞 Storico Interazioni"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Interazioni Totali", demo.get("num_interazioni_totali", 0))
        with col2:
            st.metric("Conversioni", demo.get("num_conversioni", 0))
        with col3:
            st.metric("Tasso Conv.", f"{demo.get('tasso_conversione', 0):.1%}")

        interactions = profile.get("interactions", [])
        if interactions:
            interactions_df = pd.DataFrame(interactions[:10])
            if len(interactions_df) > 0:
                st.dataframe(interactions_df, use_container_width=True, hide_index=True)

    with st.expander("⚠️ Sinistri e Reclami"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sinistri Totali", demo.get("num_sinistri_totali", 0))
            st.write(f"**Importo Liquidato:** €{demo.get('importo_totale_liquidato', 0):,.0f}")

        claims = profile.get("claims", [])
        if claims:
            claims_df = pd.DataFrame(claims[:5])
            if len(claims_df) > 0:
                st.dataframe(claims_df, use_container_width=True, hide_index=True)

        complaints = profile.get("complaints", [])
        if complaints:
            st.write("**Reclami:**")
            for c in complaints[:3]:
                st.warning(c.get("reclami_info", "N/A"))


def render_pitch(pitch: SalesPitch) -> None:
    """Render the generated sales pitch."""
    st.markdown("### 🎯 Pitch Personalizzato")

    # Customer Summary
    st.markdown(
        f"""
    <div class="pitch-section">
        <div class="pitch-header">📌 Riepilogo Cliente</div>
        {pitch.customer_summary}
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Recommendation Rationale
    st.markdown(
        f"""
    <div class="pitch-section">
        <div class="pitch-header">💡 Motivazione Raccomandazione</div>
        {pitch.recommendation_rationale}
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Key Selling Points
    points_html = "<ul>" + "".join(f"<li>{p}</li>" for p in pitch.key_selling_points) + "</ul>"
    st.markdown(
        f"""
    <div class="pitch-section">
        <div class="pitch-header">⭐ Punti di Forza Chiave</div>
        {points_html}
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Value Proposition
    st.markdown(
        f"""
    <div class="pitch-section">
        <div class="pitch-header">💎 Proposta di Valore</div>
        {pitch.personalized_value_proposition}
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Objection Handling
    with st.expander("🛡️ Gestione Obiezioni", expanded=True):
        for i, objection in enumerate(pitch.objection_handling, 1):
            st.info(f"**{i}.** {objection}")

    # Next Steps
    with st.expander("📋 Prossimi Passi", expanded=True):
        for i, step in enumerate(pitch.suggested_next_steps, 1):
            st.success(f"**{i}.** {step}")

    # Product Highlights
    with st.expander("📄 Highlights Prodotto"):
        st.markdown(pitch.product_highlights)

    # Raw response for debugging
    with st.expander("🔧 Risposta Completa (Debug)"):
        st.text(pitch.raw_response)


def main():
    """Main application."""
    st.title("🤖 Sales Assistant")
    st.markdown("*Assistente AI per la generazione di pitch di vendita personalizzati*")

    # Sidebar for selection
    with st.sidebar:
        st.header("📋 Selezione")

        # Load customer list
        try:
            customers_df = get_customer_list()

            # Create searchable customer selector
            st.subheader("👤 Cliente")
            customer_options = customers_df.apply(
                lambda x: f"{x['full_name']} ({x['profession']}, {x['city']})",
                axis=1,
            ).tolist()

            selected_customer_idx = st.selectbox(
                "Seleziona cliente",
                options=range(len(customer_options)),
                format_func=lambda x: customer_options[x],
                key="customer_selector",
            )

            selected_customer_id = customers_df.iloc[selected_customer_idx]["codice_cliente"]

        except Exception as e:
            st.error(f"Errore caricamento clienti: {str(e)}")
            selected_customer_id = None

        st.divider()

        # Product selector
        st.subheader("📦 Prodotto")
        selected_product = st.selectbox(
            "Seleziona prodotto da proporre",
            options=PRODUCTS,
            key="product_selector",
        )

        # Show product info
        if selected_product:
            info = PRODUCT_INFO.get(selected_product, {})
            st.caption(f"**Tipo:** {info.get('type', 'N/A')}")
            st.caption(f"**Area:** {info.get('area', 'N/A')}")
            st.caption(info.get("description", ""))

        st.divider()

        # Generate button
        generate_clicked = st.button(
            "🚀 Genera Pitch",
            type="primary",
            use_container_width=True,
            disabled=selected_customer_id is None,
        )

    # Main content area
    if selected_customer_id:
        # Load customer profile
        try:
            with st.spinner("Caricamento profilo cliente..."):
                customer_profile = get_customer_full_profile(selected_customer_id)
        except Exception as e:
            st.error(f"Errore caricamento profilo: {str(e)}")
            customer_profile = None

        if customer_profile:
            # Two-column layout
            col_left, col_right = st.columns([1, 1])

            with col_left:
                render_customer_card(customer_profile)

            with col_right:
                if generate_clicked:
                    with st.spinner(
                        "🤖 Generazione pitch in corso... (può richiedere fino a 30 secondi)"
                    ):
                        try:
                            pitch = generate_sales_pitch(customer_profile, selected_product)
                            st.session_state["last_pitch"] = pitch
                            st.session_state["last_pitch_product"] = selected_product
                            st.session_state["last_pitch_customer"] = selected_customer_id
                        except Exception as e:
                            st.error(f"Errore generazione pitch: {str(e)}")
                            st.exception(e)

                # Show last generated pitch if available
                if "last_pitch" in st.session_state:
                    if (
                        st.session_state.get("last_pitch_customer") == selected_customer_id
                        and st.session_state.get("last_pitch_product") == selected_product
                    ):
                        render_pitch(st.session_state["last_pitch"])
                    else:
                        st.info(
                            "👆 Clicca 'Genera Pitch' per creare un nuovo pitch per questo cliente e prodotto."
                        )
                else:
                    st.info(
                        "👆 Seleziona un cliente e un prodotto, poi clicca 'Genera Pitch' per iniziare."
                    )
    else:
        st.info("👈 Seleziona un cliente dalla barra laterale per iniziare.")


if __name__ == "__main__":
    main()
