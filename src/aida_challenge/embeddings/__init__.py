"""Embeddings module for RAG support."""

from .embed_documents import embed_documents, search_similar_chunks

__all__ = ["embed_documents", "search_similar_chunks"]
