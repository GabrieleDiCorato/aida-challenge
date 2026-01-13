"""
RAG Agent for contract document retrieval.

This agent searches the embedded product documents to find relevant
contract sections for the sales pitch.
"""

import os
from pathlib import Path
import sys

# Import the search function from embeddings module
from embeddings.embed_documents import search_similar_chunks

from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.function_tool import FunctionTool

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))


def search_product_documents(query: str, product_name: str, top_k: int = 5) -> str:
    """
    Search for relevant sections in product documents.

    Args:
        query: The search query describing what information is needed
        product_name: The product to search documents for
        top_k: Number of results to return

    Returns:
        Formatted string with relevant document sections
    """
    try:
        results = search_similar_chunks(query=query, product_name=product_name, top_k=top_k)

        if not results:
            return f"No relevant sections found for product: {product_name}"

        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(
                f"""
--- Sezione {i}: {result['section_header']} ---
Prodotto: {result['product_name']}
Rilevanza: {result['similarity']:.2%}

{result['chunk_text'][:1500]}...
"""
            )

        return "\n".join(formatted_results)

    except Exception as e:
        return f"Error searching documents: {str(e)}"


# Create the function tool
search_documents_tool = FunctionTool(func=search_product_documents)

# RAG Agent
rag_agent = LlmAgent(
    name="rag_agent",
    model=LiteLlm(
        model="openrouter/deepseek/deepseek-r1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        api_base="https://openrouter.ai/api/v1",
    ),
    description="Retrieves relevant contract and product information from embedded documents.",
    instruction="""You are a document retrieval specialist for Vita Sicura S.p.A. insurance products.

Your role is to:
1. Search the product documentation for relevant information
2. Extract key contract details, coverage terms, benefits, and conditions
3. Identify selling points from the contract language
4. Find relevant exclusions and limitations that should be disclosed

When searching, focus on:
- Coverage details and benefits
- Premium structures and payment options
- Key exclusions the customer should know
- Unique features that differentiate the product
- Terms that match the customer's specific situation

Use the search_product_documents tool to find relevant sections.
Always search for multiple relevant topics to get comprehensive coverage information.

Output your findings in Italian, organized by topic.
""",
    tools=[search_documents_tool],
    output_key="product_information",
)


def get_rag_agent() -> LlmAgent:
    """Factory function to get the RAG agent."""
    return rag_agent
