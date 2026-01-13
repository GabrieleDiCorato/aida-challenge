"""
Google ADK Multi-Agent System for Sales Pitch Generation.

This module contains agents for:
- Customer analysis
- RAG-based contract retrieval
- Sales pitch orchestration and generation
"""

from .pitch_orchestrator import generate_sales_pitch, SalesPitch
from .schemas import SalesPitchOutput

__all__ = ["generate_sales_pitch", "SalesPitch", "SalesPitchOutput"]
