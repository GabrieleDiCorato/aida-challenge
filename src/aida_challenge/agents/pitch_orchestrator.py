"""
Sales Pitch Orchestrator.

This module orchestrates the multi-agent workflow:
1. Customer Analyst Agent - analyzes the customer profile
2. RAG Agent - retrieves relevant contract information
3. Pitch Generator - creates the final personalized pitch

Uses Google ADK's SequentialAgent for orchestration.
"""

import asyncio
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from google.genai import types

from .customer_analyst import customer_analyst_agent
from .rag_agent import rag_agent

load_dotenv()


@dataclass
class SalesPitch:
    """Container for the generated sales pitch."""

    customer_summary: str
    recommendation_rationale: str
    key_selling_points: list[str]
    personalized_value_proposition: str
    objection_handling: list[str]
    suggested_next_steps: list[str]
    product_highlights: str
    raw_response: str = ""


# Pitch Generator Agent - the final agent that creates the pitch
pitch_generator_agent = LlmAgent(
    name="pitch_generator",
    model=LiteLlm(
        model="openrouter/deepseek/deepseek-r1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        api_base="https://openrouter.ai/api/v1",
    ),
    description="Generates personalized sales pitches based on customer analysis and product information.",
    instruction="""You are an expert sales pitch writer for Vita Sicura S.p.A.

Based on the customer analysis and product information provided in the conversation,
generate a comprehensive and personalized sales pitch.

Your pitch MUST be in Italian and include these sections:

1. **RIEPILOGO CLIENTE**: Brief summary of the customer (2-3 sentences)

2. **MOTIVAZIONE RACCOMANDAZIONE**: Why this product is right for this customer (2-3 sentences)

3. **PUNTI DI FORZA CHIAVE**: 3-5 bullet points of key selling points tailored to this customer

4. **PROPOSTA DI VALORE PERSONALIZZATA**: A compelling value proposition that speaks directly to the customer's needs (1 paragraph)

5. **GESTIONE OBIEZIONI**: 3-4 potential objections and how to handle them

6. **PROSSIMI PASSI**: 3-4 concrete next steps for the salesperson

7. **HIGHLIGHTS PRODOTTO**: Key contract highlights relevant to this customer

Be specific, use the customer's actual data, and make the pitch feel personal.
Focus on the customer's specific situation, not generic selling points.
""",
    output_key="sales_pitch",
)


def create_pitch_pipeline() -> SequentialAgent:
    """Create the sequential agent pipeline for pitch generation."""
    return SequentialAgent(
        name="sales_pitch_pipeline",
        description="Orchestrates customer analysis, document retrieval, and pitch generation.",
        sub_agents=[
            customer_analyst_agent,
            rag_agent,
            pitch_generator_agent,
        ],
    )


async def generate_sales_pitch_async(
    customer_profile: dict,
    product_name: str,
) -> SalesPitch:
    """
    Generate a personalized sales pitch using the multi-agent system.

    Args:
        customer_profile: Complete customer profile from get_customer_full_profile()
        product_name: The product to pitch

    Returns:
        SalesPitch object with structured pitch content
    """
    # Format the customer profile for the agents
    customer_context = f"""
# Profilo Cliente

## Dati Anagrafici
- Nome: {customer_profile['demographics'].get('nome', 'N/A')} {customer_profile['demographics'].get('cognome', 'N/A')}
- Età: {customer_profile['demographics'].get('eta', 'N/A')} anni
- Professione: {customer_profile['demographics'].get('professione', 'N/A')}
- Reddito: €{customer_profile['demographics'].get('reddito', 0):,.0f}
- Stato Civile: {customer_profile['demographics'].get('stato_civile', 'N/A')}
- Zona Residenza: {customer_profile['demographics'].get('zona_residenza', 'N/A')}

## Metriche Cliente
- Segmento: {customer_profile['demographics'].get('segmento_cliente', 'N/A')}
- Classificazione Valore: {customer_profile['demographics'].get('classificazione_valore', 'N/A')}
- Classificazione Rischio: {customer_profile['demographics'].get('classificazione_rischio', 'N/A')}
- Engagement Score: {customer_profile['demographics'].get('engagement_score', 0):.1f}/100
- Satisfaction Score: {customer_profile['demographics'].get('satisfaction_score', 0):.1f}/100
- Probabilità Churn: {customer_profile['demographics'].get('churn_probability', 0):.1%}
- Potenziale Crescita: {customer_profile['demographics'].get('potenziale_crescita', 0):.1%}
- CLV Stimato: €{customer_profile['demographics'].get('clv_stimato', 0):,.0f}

## Portfolio Attuale
- Polizze Totali: {customer_profile['demographics'].get('num_polizze_totali', 0)}
- Polizze Attive: {customer_profile['demographics'].get('num_polizze_attive', 0)}
- Premio Annuo Totale: €{customer_profile['demographics'].get('premio_annuo_totale', 0):,.0f}
- Prodotti Protezione: {customer_profile['demographics'].get('num_prodotti_protezione', 0)}
- Prodotti Investimento: {customer_profile['demographics'].get('num_prodotti_investimento', 0)}

## Polizze Attive
"""
    # Add policies
    for policy in customer_profile.get("policies", []):
        if policy.get("stato_polizza") == "Attiva":
            customer_context += f"""
- {policy.get('prodotto', 'N/A')} ({policy.get('area_bisogno', 'N/A')})
  - Premio: €{policy.get('premio_totale_annuo', 0):,.0f}/anno
  - Massimale: €{policy.get('massimale', 0):,.0f}
  - Scadenza: {policy.get('data_scadenza', 'N/A')}
"""

    # Add interaction summary
    customer_context += f"""
## Storico Interazioni
- Interazioni Totali: {customer_profile['demographics'].get('num_interazioni_totali', 0)}
- Conversioni: {customer_profile['demographics'].get('num_conversioni', 0)}
- Tasso Conversione: {customer_profile['demographics'].get('tasso_conversione', 0):.1%}

## Sinistri
- Sinistri Totali: {customer_profile['demographics'].get('num_sinistri_totali', 0)}
- Importo Liquidato: €{customer_profile['demographics'].get('importo_totale_liquidato', 0):,.0f}
- Frequenza Annua: {customer_profile['demographics'].get('frequenza_sinistri_annua', 0):.2f}
"""

    # Add recent interactions
    if customer_profile.get("interactions"):
        customer_context += "\n## Ultime Interazioni\n"
        for interaction in customer_profile["interactions"][:5]:
            customer_context += f"- {interaction.get('tipo_interazione', 'N/A')}: {interaction.get('motivo', 'N/A')} - Esito: {interaction.get('esito', 'N/A')}\n"

    # Add housing info if available
    if customer_profile.get("housing"):
        customer_context += "\n## Informazioni Abitazione\n"
        for housing in customer_profile["housing"]:
            customer_context += f"- Metratura: {housing.get('metratura', 'N/A')} mq\n"
            customer_context += (
                f"- Sistema Allarme: {'Sì' if housing.get('sistema_allarme') else 'No'}\n"
            )

    # Add complaints if any
    if customer_profile.get("complaints"):
        customer_context += "\n## Reclami\n"
        for complaint in customer_profile["complaints"][:3]:
            customer_context += f"- {complaint.get('reclami_info', 'N/A')}\n"

    # Create the initial prompt
    initial_prompt = f"""
{customer_context}

---

# Prodotto da Proporre: {product_name}

Per favore:
1. Analizza il profilo del cliente e identifica le opportunità
2. Cerca le informazioni rilevanti del prodotto {product_name} nei documenti
3. Genera un pitch di vendita personalizzato per questo cliente
"""

    # Create runner and execute
    pipeline = create_pitch_pipeline()
    runner = InMemoryRunner(
        app_name="sales_pitch_generator",
        agent=pipeline,
    )

    session = await runner.session_service.create_session(
        app_name="sales_pitch_generator",
        user_id="salesperson",
    )

    # Run the pipeline
    final_response = ""
    async for event in runner.run_async(
        user_id="salesperson",
        session_id=session.id,
        new_message=types.Content(
            role="user",
            parts=[types.Part.from_text(text=initial_prompt)],
        ),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response = part.text

    # Parse the response into structured format
    return parse_pitch_response(final_response)


def parse_pitch_response(response: str) -> SalesPitch:
    """Parse the agent response into a structured SalesPitch object."""
    # Default values
    pitch = SalesPitch(
        customer_summary="",
        recommendation_rationale="",
        key_selling_points=[],
        personalized_value_proposition="",
        objection_handling=[],
        suggested_next_steps=[],
        product_highlights="",
        raw_response=response,
    )

    # Try to extract sections from the response
    sections = {
        "RIEPILOGO CLIENTE": "customer_summary",
        "MOTIVAZIONE RACCOMANDAZIONE": "recommendation_rationale",
        "PUNTI DI FORZA CHIAVE": "key_selling_points",
        "PROPOSTA DI VALORE PERSONALIZZATA": "personalized_value_proposition",
        "GESTIONE OBIEZIONI": "objection_handling",
        "PROSSIMI PASSI": "suggested_next_steps",
        "HIGHLIGHTS PRODOTTO": "product_highlights",
    }

    current_section = None
    current_content = []

    for line in response.split("\n"):
        # Check if this is a section header
        found_section = False
        for header, field in sections.items():
            if header in line.upper():
                # Save previous section
                if current_section:
                    content = "\n".join(current_content).strip()
                    if current_section in [
                        "key_selling_points",
                        "objection_handling",
                        "suggested_next_steps",
                    ]:
                        # Parse as list
                        items = [
                            item.strip().lstrip("-•*").strip()
                            for item in content.split("\n")
                            if item.strip() and not item.strip().startswith("#")
                        ]
                        setattr(pitch, current_section, items)
                    else:
                        setattr(pitch, current_section, content)

                current_section = field
                current_content = []
                found_section = True
                break

        if not found_section and current_section:
            current_content.append(line)

    # Save last section
    if current_section:
        content = "\n".join(current_content).strip()
        if current_section in ["key_selling_points", "objection_handling", "suggested_next_steps"]:
            items = [
                item.strip().lstrip("-•*").strip()
                for item in content.split("\n")
                if item.strip() and not item.strip().startswith("#")
            ]
            setattr(pitch, current_section, items)
        else:
            setattr(pitch, current_section, content)

    return pitch


def generate_sales_pitch(customer_profile: dict, product_name: str) -> SalesPitch:
    """
    Synchronous wrapper for generate_sales_pitch_async.

    Args:
        customer_profile: Complete customer profile from get_customer_full_profile()
        product_name: The product to pitch

    Returns:
        SalesPitch object with structured pitch content
    """
    return asyncio.run(generate_sales_pitch_async(customer_profile, product_name))
