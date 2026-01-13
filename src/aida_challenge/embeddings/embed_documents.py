"""
Embedding pipeline for insurance product documents.

This module chunks the product documents from data/documents/,
generates embeddings using OpenRouter's embedding models,
and stores them in DuckDB using the VSS extension for vector similarity search.
"""

import os
import re
from pathlib import Path
from typing import Optional

import duckdb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Configure OpenRouter API (OpenAI-compatible)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Embedding model - using a free embedding model from OpenRouter
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
DB_PATH = DATA_DIR / "aida_challenge.duckdb"

# Product name mapping from filenames
PRODUCT_MAPPING = {
    "Assicurazione_Casa_Serena.md": "Casa Serena",
    "PIP_Pensione_Serenita.md": "PIP Pensione Serenità",
    "Polizza_Salute_Protetta.md": "Salute Protetta",
    "Polizza_Vita_Futuro_Sicuro.md": "Vita Futuro Sicuro",
    "Polizza_Vita_Risparmio_Costante.md": "Vita Risparmio Costante",
}


def chunk_document_by_sections(content: str, filename: str) -> list[dict]:
    """
    Chunk a markdown document by sections (## headers).

    Returns a list of dictionaries with:
    - chunk_text: the text content of the section
    - section_header: the header title
    - product_name: mapped product name
    """
    product_name = PRODUCT_MAPPING.get(filename, filename.replace(".md", "").replace("_", " "))

    # Split by markdown headers (## or ###)
    # Keep the header with its content
    sections = re.split(r"(?=^#{2,3}\s)", content, flags=re.MULTILINE)

    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract header if present
        header_match = re.match(r"^(#{2,3})\s+(.+?)(?:\n|$)", section)
        if header_match:
            section_header = header_match.group(2).strip()
            # Remove the header line from content for cleaner text
            chunk_text = section
        else:
            # For content before first header (intro/metadata)
            section_header = "Introduzione"
            chunk_text = section

        # Skip very short chunks (less than 100 chars)
        if len(chunk_text) < 100:
            continue

        chunks.append(
            {
                "chunk_text": chunk_text,
                "section_header": section_header,
                "product_name": product_name,
            }
        )

    return chunks


def generate_embedding(text: str) -> list[float]:
    """Generate embedding for a text using OpenRouter's embedding model."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple texts in a single batch request.

    Args:
        texts: List of text strings to embed

    Returns:
        List of embeddings in the same order as input texts
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")

    if not texts:
        return []

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )

    # Sort by index to ensure order matches input
    sorted_data = sorted(response.data, key=lambda x: x.index)
    return [item.embedding for item in sorted_data]


def generate_query_embedding(text: str) -> list[float]:
    """Generate embedding for a query using OpenRouter's embedding model."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def setup_vss_extension(con: duckdb.DuckDBPyConnection) -> None:
    """Install and load the VSS extension for vector similarity search."""
    con.execute("INSTALL vss")
    con.execute("LOAD vss")


def create_embeddings_table(con: duckdb.DuckDBPyConnection) -> None:
    """Create the document_embeddings table if it doesn't exist."""
    con.execute(
        f"""
        CREATE TABLE IF NOT EXISTS document_embeddings (
            doc_id INTEGER PRIMARY KEY,
            product_name VARCHAR NOT NULL,
            section_header VARCHAR NOT NULL,
            chunk_text VARCHAR NOT NULL,
            embedding FLOAT[{EMBEDDING_DIM}] NOT NULL
        )
    """
    )


def create_hnsw_index(con: duckdb.DuckDBPyConnection) -> None:
    """Create HNSW index for fast similarity search."""
    # Enable experimental persistence for HNSW indexes
    con.execute("SET hnsw_enable_experimental_persistence = true")

    # Check if index exists
    existing_indexes = con.execute(
        """
        SELECT * FROM duckdb_indexes()
        WHERE index_name = 'embedding_hnsw_idx'
    """
    ).fetchall()

    if not existing_indexes:
        con.execute(
            """
            CREATE INDEX embedding_hnsw_idx
            ON document_embeddings
            USING HNSW (embedding)
            WITH (metric = 'cosine')
        """
        )


def embed_documents(force_rebuild: bool = False) -> None:
    """
    Main function to embed all product documents.

    Args:
        force_rebuild: If True, drop existing table and rebuild from scratch
    """
    print(f"Connecting to database: {DB_PATH}")
    con = duckdb.connect(str(DB_PATH))

    # Setup VSS extension
    print("Setting up VSS extension...")
    setup_vss_extension(con)

    # Check if we need to rebuild
    if force_rebuild:
        print("Force rebuild requested, dropping existing table...")
        con.execute("DROP TABLE IF EXISTS document_embeddings")

    # Create table
    create_embeddings_table(con)

    # Check if already populated
    count = con.execute("SELECT COUNT(*) FROM document_embeddings").fetchone()[0]
    if count > 0 and not force_rebuild:
        print(f"Table already has {count} embeddings. Use --force to rebuild.")
        con.close()
        return

    # Process each document
    doc_id = 0
    all_chunks = []

    print(f"\nProcessing documents from: {DOCUMENTS_DIR}")
    for doc_file in DOCUMENTS_DIR.glob("*.md"):
        print(f"\n  Processing: {doc_file.name}")
        content = doc_file.read_text(encoding="utf-8")
        chunks = chunk_document_by_sections(content, doc_file.name)
        print(f"    Found {len(chunks)} sections")

        for chunk in chunks:
            chunk["doc_id"] = doc_id
            all_chunks.append(chunk)
            doc_id += 1

    print(f"\nTotal chunks to embed: {len(all_chunks)}")

    # Generate embeddings in batches for efficiency
    print("\nGenerating embeddings in batch (this may take a minute)...")
    BATCH_SIZE = 100  # OpenAI/OpenRouter supports up to 2048 inputs per request

    all_embeddings = []
    for batch_start in range(0, len(all_chunks), BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, len(all_chunks))
        batch_texts = [chunk["chunk_text"] for chunk in all_chunks[batch_start:batch_end]]

        print(
            f"  Processing batch {batch_start // BATCH_SIZE + 1}: chunks {batch_start + 1}-{batch_end}/{len(all_chunks)}"
        )
        batch_embeddings = generate_embeddings_batch(batch_texts)
        all_embeddings.extend(batch_embeddings)

    # Insert all chunks with their embeddings
    print("\nInserting embeddings into database...")
    for i, (chunk, embedding) in enumerate(zip(all_chunks, all_embeddings)):
        if (i + 1) % 50 == 0:
            print(f"  Inserted: {i + 1}/{len(all_chunks)}")

        con.execute(
            """
            INSERT INTO document_embeddings (doc_id, product_name, section_header, chunk_text, embedding)
            VALUES (?, ?, ?, ?, ?)
        """,
            [
                chunk["doc_id"],
                chunk["product_name"],
                chunk["section_header"],
                chunk["chunk_text"],
                embedding,
            ],
        )

    # Create HNSW index for fast similarity search
    print("\nCreating HNSW index...")
    create_hnsw_index(con)

    final_count = con.execute("SELECT COUNT(*) FROM document_embeddings").fetchone()[0]
    print(f"\n✓ Successfully embedded {final_count} document chunks")

    # Show summary by product
    print("\nEmbeddings by product:")
    summary = con.execute(
        """
        SELECT product_name, COUNT(*) as chunk_count
        FROM document_embeddings
        GROUP BY product_name
        ORDER BY product_name
    """
    ).fetchall()
    for product, count in summary:
        print(f"  - {product}: {count} chunks")

    con.close()


def search_similar_chunks(
    query: str, product_name: Optional[str] = None, top_k: int = 5, db_path: Optional[Path] = None
) -> list[dict]:
    """
    Search for similar document chunks using cosine similarity.

    Args:
        query: The search query
        product_name: Optional filter by product name
        top_k: Number of results to return
        db_path: Optional custom database path

    Returns:
        List of dictionaries with matching chunks and scores
    """
    db = db_path or DB_PATH
    con = duckdb.connect(str(db), read_only=True)

    # Load VSS extension and enable experimental persistence
    con.execute("LOAD vss")
    con.execute("SET hnsw_enable_experimental_persistence = true")

    # Generate query embedding
    query_embedding = generate_query_embedding(query)

    # Build query with optional product filter
    if product_name:
        results = con.execute(
            f"""
            SELECT
                doc_id,
                product_name,
                section_header,
                chunk_text,
                array_cosine_similarity(embedding, ?::FLOAT[{EMBEDDING_DIM}]) as similarity
            FROM document_embeddings
            WHERE product_name = ?
            ORDER BY similarity DESC
            LIMIT ?
        """,
            [query_embedding, product_name, top_k],
        ).fetchall()
    else:
        results = con.execute(
            f"""
            SELECT
                doc_id,
                product_name,
                section_header,
                chunk_text,
                array_cosine_similarity(embedding, ?::FLOAT[{EMBEDDING_DIM}]) as similarity
            FROM document_embeddings
            ORDER BY similarity DESC
            LIMIT ?
        """,
            [query_embedding, top_k],
        ).fetchall()

    con.close()

    return [
        {
            "doc_id": r[0],
            "product_name": r[1],
            "section_header": r[2],
            "chunk_text": r[3],
            "similarity": r[4],
        }
        for r in results
    ]


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Embed product documents for RAG")
    parser.add_argument("--force", action="store_true", help="Force rebuild of embeddings")
    args = parser.parse_args()

    embed_documents(force_rebuild=args.force)


if __name__ == "__main__":
    main()
