"""
Sales Chatbot - AI-Powered Sales Pitch Generator

This Streamlit page provides an interface for salespeople to:
1. Select a customer from the database
2. Choose a product to pitch
3. Generate a personalized sales pitch using AI agents
"""

import streamlit as st
import pandas as pd
import random
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from aida_challenge.streamlit_app.utils import (
    get_customer_full_profile,
    get_nba_recommendations,
    load_cached_pitches,
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
        background-color: ##1f77b4;
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
    .nba-item {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #2ecc71;
        cursor: pointer;
        transition: all 0.2s;
    }
    .nba-item:hover {
        background-color: #f0f8ff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .nba-item.selected {
        background-color: #e3f2fd;
        border-left-color: #1f77b4;
    }
    .urgency-critical { border-left-color: #dc3545 !important; }
    .urgency-high { border-left-color: #fd7e14 !important; }
    .urgency-medium { border-left-color: #ffc107 !important; }
    .urgency-low { border-left-color: #28a745 !important; }
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


def render_cached_pitch(pitch_text: str) -> None:
    """Render a cached pitch from the proposal CSV."""
    st.markdown("### 🎯 Pitch Personalizzato (Cached)")

    st.info("✨ Questo pitch è stato pre-generato e ottimizzato per questo cliente.")

    st.markdown(
        f"""
    <div class="pitch-section">
        <div class="pitch-header">💬 Proposta di Contatto</div>
        {pitch_text}
    </div>
    """,
        unsafe_allow_html=True,
    )


def generate_fake_email(full_name: str, customer_id: int) -> str:
    """Generate a fake email address based on customer name."""
    # Clean and format name
    parts = full_name.lower().split()
    if len(parts) >= 2:
        email_name = f"{parts[0]}.{parts[1]}"
    else:
        email_name = parts[0] if parts else "cliente"

    # Use customer ID for domain variety
    random.seed(int(customer_id))
    domains = ["email.com", "mail.it", "posta.it", "example.com", "contact.it"]
    domain = random.choice(domains)

    return f"📧 {email_name}@{domain}"


def generate_fake_phone(customer_id: int) -> str:
    """Generate a fake Italian phone number."""
    random.seed(int(customer_id))

    # Generate Italian mobile number (333-339, 340-349, 360-369, 380-389, 390-399)
    prefix = random.choice(
        [
            333,
            334,
            335,
            336,
            337,
            338,
            339,
            340,
            341,
            342,
            343,
            344,
            345,
            346,
            347,
            348,
            349,
            360,
            361,
            362,
            363,
            366,
            368,
            369,
            380,
            383,
            388,
            389,
            390,
            391,
            392,
            393,
            397,
            398,
            399,
        ]
    )

    # Generate 7 remaining digits
    number = random.randint(1000000, 9999999)

    return f"📞 +39 {prefix} {number}"


def main():
    """Main application."""
    # Initialize session state
    if "selected_nba_index" not in st.session_state:
        st.session_state["selected_nba_index"] = None
    if "show_pitch_panel" not in st.session_state:
        st.session_state["show_pitch_panel"] = False

    # Load cached pitches
    try:
        cached_pitches_df = load_cached_pitches()
        # Convert to dict for easy lookup: {customer_id: pitch_text}
        cached_pitches = dict(
            zip(cached_pitches_df["codice_cliente"], cached_pitches_df["testo_pitch"])
        )
    except Exception as e:
        st.warning(f"⚠️ Impossibile caricare pitch cached: {str(e)}")
        cached_pitches = {}

    # Logo and Title
    logo_path = Path(__file__).parent.parent / "images" / "vita_sicura_small_transparent.png"
    if not logo_path.exists():
        st.warning("Logo image not found. Please ensure the image exists at the specified path.")

    # Header with title and toggle button
    col_title, col_button = st.columns([3, 1])
    with col_title:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(str(logo_path), width=150)
        with col2:
            st.title("Sales Assistant")
            st.markdown("*Clienti prioritari con raccomandazioni Next Best Action*")

    with col_button:
        st.write("")  # Spacer
        if st.button(
            "📝 Pitch" if not st.session_state["show_pitch_panel"] else "❌ Chiudi",
            type="secondary" if not st.session_state["show_pitch_panel"] else "primary",
            use_container_width=True,
        ):
            st.session_state["show_pitch_panel"] = not st.session_state["show_pitch_panel"]

    # Sidebar for NBA priority list
    with st.sidebar:
        st.header("🎯 Lista Priorità NBA")

        # Load NBA recommendations
        try:
            nba_df = get_nba_recommendations()

            if len(nba_df) == 0:
                st.warning("Nessuna raccomandazione NBA disponibile.")
                return

            # Filter controls
            st.subheader("🔍 Filtri")

            # Urgency filter
            urgency_levels = ["Tutti"] + sorted(
                nba_df["livello_urgenza"].unique().tolist(), reverse=True
            )
            selected_urgency = st.selectbox(
                "Livello Urgenza",
                options=urgency_levels,
                key="urgency_filter",
            )

            # Strategy filter
            strategies = ["Tutte"] + nba_df["strategia_pitch"].unique().tolist()
            selected_strategy = st.selectbox(
                "Strategia Pitch",
                options=strategies,
                key="strategy_filter",
            )

            # Apply filters
            filtered_df = nba_df.copy()
            if selected_urgency != "Tutti":
                filtered_df = filtered_df[filtered_df["livello_urgenza"] == selected_urgency]
            if selected_strategy != "Tutte":
                filtered_df = filtered_df[filtered_df["strategia_pitch"] == selected_strategy]

            st.divider()

            # Display filtered count
            st.caption(f"📊 {len(filtered_df)} clienti trovati")

            # Create clickable customer list
            st.subheader("👥 Clienti Prioritari")

            # Use radio buttons for selection
            if len(filtered_df) > 0:
                # Prepare data for display table
                display_data = []
                for idx, row in filtered_df.iterrows():
                    urgency_emoji = {
                        "CRITICAL": "🔴",
                        "HIGH": "🟠",
                        "MEDIUM": "🟡",
                        "LOW": "🟢",
                    }.get(row["livello_urgenza"], "⚪")

                    # Generate random contact channel using customer ID as seed for consistency
                    # Convert to native Python int to avoid numpy type issues
                    customer_id = int(row["codice_cliente"])
                    random.seed(customer_id)
                    is_email = random.choice([True, False])

                    if is_email:
                        contatto = generate_fake_email(row["full_name"], customer_id)
                    else:
                        contatto = generate_fake_phone(customer_id)

                    display_data.append(
                        {
                            "Cliente": row["full_name"],
                            "Priorità": f"{urgency_emoji} {row['livello_urgenza']}",
                            "Contatto": contatto,
                            "Prodotto": (
                                row["raccomandazione_nba"][:20] + "..."
                                if len(row["raccomandazione_nba"]) > 20
                                else row["raccomandazione_nba"]
                            ),
                        }
                    )

                # Create DataFrame for display
                display_df = pd.DataFrame(display_data)

                # Show table with selection using on_select event
                event = st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=min(400, (len(display_df) + 1) * 35 + 3),
                    on_select="rerun",
                    selection_mode="single-row",
                    key="customer_table",
                )

                # Get selected index from event
                if event.selection and len(event.selection.rows) > 0:
                    selected_idx = event.selection.rows[0]

                    # Get selected customer data
                    selected_row = filtered_df.iloc[selected_idx]
                    customer_id = int(selected_row["codice_cliente"])

                    # Only update if different customer selected
                    if st.session_state.get("selected_customer_id") != customer_id:
                        st.session_state["selected_nba_index"] = selected_idx
                        st.session_state["selected_nba_data"] = selected_row.to_dict()
                        st.session_state["selected_customer_id"] = customer_id

                        # Generate and store contact info
                        random.seed(customer_id)
                        is_email = random.choice([True, False])

                        if is_email:
                            st.session_state["contact_info"] = generate_fake_email(
                                selected_row["full_name"], customer_id
                            )
                            st.session_state["contact_channel"] = "Email"
                        else:
                            st.session_state["contact_info"] = generate_fake_phone(customer_id)
                            st.session_state["contact_channel"] = "Telefono"
                else:
                    # Clear selection if nothing is selected
                    if "selected_nba_data" in st.session_state:
                        del st.session_state["selected_nba_data"]
                    if "selected_nba_index" in st.session_state:
                        del st.session_state["selected_nba_index"]
                    if "selected_customer_id" in st.session_state:
                        del st.session_state["selected_customer_id"]

        except Exception as e:
            st.error(f"Errore caricamento raccomandazioni NBA: {str(e)}")
            st.exception(e)
            return

        except Exception as e:
            st.error(f"Errore caricamento raccomandazioni NBA: {str(e)}")
            st.exception(e)
            return

    # Main content area
    if "selected_nba_data" in st.session_state:
        nba_data = st.session_state["selected_nba_data"]
        selected_customer_id = nba_data["codice_cliente"]
        selected_product = nba_data["raccomandazione_nba"]

        # Load customer full profile
        try:
            with st.spinner("Caricamento profilo cliente..."):
                customer_profile = get_customer_full_profile(selected_customer_id)
        except Exception as e:
            st.error(f"Errore caricamento profilo: {str(e)}")
            customer_profile = None

        if customer_profile:
            # Dynamic column layout based on pitch panel visibility
            if st.session_state["show_pitch_panel"]:
                col_left, col_right = st.columns([3, 2])
            else:
                # Single column when pitch is hidden
                col_left = st.container()
                col_right = None

            with col_left:
                # NBA Context card
                st.markdown("### 🎯 Contesto NBA")

                # Create structured NBA info table
                urgency_emoji = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠",
                    "MEDIUM": "🟡",
                    "LOW": "🟢",
                }.get(nba_data["livello_urgenza"], "⚪")

                # Build portfolio display
                portfolio_items = []
                if nba_data["possiede_casa"]:
                    portfolio_items.append("🏠 Casa")
                if nba_data["possiede_salute"]:
                    portfolio_items.append("🏥 Salute")
                if nba_data["possiede_investimento"]:
                    portfolio_items.append("💰 Investimento")
                if nba_data["possiede_pip"]:
                    portfolio_items.append("🎯 PIP")
                portfolio_str = ", ".join(portfolio_items) if portfolio_items else "Nessuno"

                # Contact channel info from session state
                contact_info = st.session_state.get("contact_info", "N/A")

                nba_info = pd.DataFrame(
                    [
                        {
                            "Campo": "Prodotto Raccomandato",
                            "Valore": f"🎯 {nba_data['raccomandazione_nba']}",
                        },
                        {
                            "Campo": "Livello Urgenza",
                            "Valore": f"{urgency_emoji} {nba_data['livello_urgenza']}",
                        },
                        {"Campo": "Canale Contatto", "Valore": contact_info},
                        {"Campo": "Strategia Pitch", "Valore": nba_data["strategia_pitch"]},
                        {"Campo": "Segmento Strategico", "Valore": nba_data["segmento_strategico"]},
                        {
                            "Campo": "Conv. Rate Previsto",
                            "Valore": f"{nba_data['tasso_conversione_nba']:.1%}",
                        },
                        {"Campo": "CLV Stimato", "Valore": f"€{nba_data['clv_stimato']:,.0f}"},
                        {"Campo": "Gap Prodotti", "Valore": f"{nba_data['gap_prodotti']} / 4"},
                        {"Campo": "Portfolio Attuale", "Valore": portfolio_str},
                    ]
                )

                st.dataframe(
                    nba_info,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Campo": st.column_config.TextColumn("Informazione", width="medium"),
                        "Valore": st.column_config.TextColumn("Dettaglio", width="large"),
                    },
                )

                st.divider()

                # Customer profile card
                render_customer_card(customer_profile)

            # Show pitch panel only if toggled on
            if col_right is not None:
                with col_right:
                    # Check if we have a cached pitch for this customer
                    cached_pitch = cached_pitches.get(selected_customer_id)

                    if cached_pitch:
                        # Display cached pitch
                        st.success("✅ Pitch pre-generato disponibile!")
                        render_cached_pitch(cached_pitch)

                        # Optional: Allow generating a new AI pitch
                        st.divider()
                        if st.button(
                            "🤖 Genera Nuovo Pitch AI",
                            type="secondary",
                            use_container_width=True,
                            help="Genera un pitch dettagliato usando l'AI agent",
                        ):
                            with st.spinner(
                                "🤖 Generazione pitch in corso... (può richiedere fino a 30 secondi)"
                            ):
                                try:
                                    pitch = generate_sales_pitch(customer_profile, selected_product)
                                    st.session_state["last_pitch"] = pitch
                                    st.session_state["last_pitch_product"] = selected_product
                                    st.session_state["last_pitch_customer"] = selected_customer_id
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Errore generazione pitch: {str(e)}")
                                    st.exception(e)

                        # Show AI-generated pitch if available
                        if "last_pitch" in st.session_state:
                            if (
                                st.session_state.get("last_pitch_customer") == selected_customer_id
                                and st.session_state.get("last_pitch_product") == selected_product
                            ):
                                st.divider()
                                st.markdown("### 🤖 Pitch AI Dettagliato")
                                render_pitch(st.session_state["last_pitch"])
                    else:
                        # No cached pitch - show generate button
                        generate_clicked = st.button(
                            f"🚀 Genera Pitch per '{selected_product}'",
                            type="primary",
                            use_container_width=True,
                        )

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
                                    "👆 Clicca 'Genera Pitch' per creare un pitch personalizzato per questo cliente."
                                )
                        else:
                            st.info(
                                "👆 Clicca 'Genera Pitch' per iniziare la generazione del pitch."
                            )
    else:
        st.info("👈 Seleziona un cliente dalla lista NBA nella barra laterale per iniziare.")

    # Footer
    st.markdown("---")
    st.markdown("**AIDA Challenge Dashboard** | Data sourced from DuckDB | Built with Streamlit")


if __name__ == "__main__":
    main()
