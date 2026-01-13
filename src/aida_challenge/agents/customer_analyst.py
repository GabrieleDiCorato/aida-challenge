"""
Customer Analyst Agent.

This agent analyzes customer profiles to identify needs, gaps, and opportunities.
"""

import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm

load_dotenv()

# Customer Analyst Agent
customer_analyst_agent = LlmAgent(
    name="customer_analyst",
    model=LiteLlm(
        model="openrouter/deepseek/deepseek-r1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        api_base="https://openrouter.ai/api/v1",
    ),
    description="Analyzes customer profiles to identify needs, gaps in coverage, and sales opportunities.",
    instruction="""You are an expert insurance customer analyst for Vita Sicura S.p.A.

Your role is to analyze the customer profile provided and identify:
1. Key customer characteristics (demographics, financial situation, risk profile)
2. Current product portfolio analysis (what they have, what's missing)
3. Potential needs based on their life stage and circumstances
4. Cross-sell and upsell opportunities
5. Risk factors and concerns to address

When analyzing, consider:
- Age and life stage (young professional, family with children, pre-retirement, etc.)
- Income level and financial capacity
- Current coverage gaps
- Claims history and risk classification
- Engagement and satisfaction levels
- Churn probability (if high, focus on retention value)

Provide your analysis in a structured format that will help the sales pitch generation.
Output your analysis in Italian since the sales team operates in Italy.
""",
    output_key="customer_analysis",
)


def get_customer_analyst_agent() -> LlmAgent:
    """Factory function to get the customer analyst agent."""
    return customer_analyst_agent
