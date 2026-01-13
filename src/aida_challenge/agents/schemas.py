"""
Pydantic schemas for structured agent outputs.
"""

from pydantic import BaseModel, Field


class SalesPitchOutput(BaseModel):
    """Structured output for a personalized sales pitch."""

    customer_summary: str = Field(
        description="Brief summary of the customer profile, key characteristics, and current relationship status"
    )

    recommendation_rationale: str = Field(
        description="Why this specific product is recommended for this customer based on their profile and needs"
    )

    key_selling_points: list[str] = Field(
        description="List of 3-5 key selling points tailored to this customer's situation"
    )

    personalized_value_proposition: str = Field(
        description="A personalized value proposition that speaks directly to the customer's needs and circumstances"
    )

    objection_handling: list[str] = Field(
        description="List of potential objections the customer might have and suggested responses"
    )

    suggested_next_steps: list[str] = Field(
        description="Concrete next steps for the salesperson to take with this customer"
    )

    product_highlights: str = Field(
        description="Key highlights from the product contract relevant to this customer"
    )
