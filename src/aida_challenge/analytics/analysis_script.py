"""
This script performs unsupervised clustering on high-value customer segments
using K-means algorithm. It reads pre-processed customer data from dbt
intermediate models, applies clustering, generates semantic labels,
and writes results to the analytics schema in DuckDB for downstream
consumption by dbt marts.
"""

import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import duckdb
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from .cluster_labeling import ClusterLabeler, create_cluster_metadata

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

# Database path
DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "aida_challenge.duckdb"
# Random seed for reproducibility
np.random.seed(42)
# Model version - format YYYYMM
MODEL_VERSION = datetime.datetime.now().strftime("v%Y%m")

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------


def validate_dataframe(df: pd.DataFrame, name: str, min_rows: int = 1) -> None:
    """
    Validate DataFrame meets basic requirements.

    Args:
        df: DataFrame to validate
        name: Name for error messages
        min_rows: Minimum required rows

    Raises:
        ValueError: If validation fails
    """
    if df is None or df.empty:
        raise ValueError(f"{name} is empty")

    if len(df) < min_rows:
        raise ValueError(f"{name} has only {len(df)} rows, expected at least {min_rows}")

    if df.isnull().all().any():
        null_cols = df.columns[df.isnull().all()].tolist()
        raise ValueError(f"{name} has columns with all NULL values: {null_cols}")


def load_customer_data(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Load customer segmentation data from dbt intermediate model.

    Args:
        con: DuckDB connection

    Returns:
        DataFrame with customer strategic segments and features

    Raises:
        ValueError: If data validation fails
    """
    query = """
    SELECT
        codice_cliente,
        segmento_valore,
        fase_vita,
        num_prodotti_posseduti,
        livello_engagement,
        segmento_strategico,
        raccomandazione_nba,
        livello_urgenza,
        possiede_casa,
        possiede_salute,
        possiede_investimento,
        possiede_pip,
        patrimonio_totale,
        clv_stimato,
        engagement_score,
        churn_probability,
        num_interazioni,
        tasso_conversione,
        num_sinistri,
        num_reclami
    FROM main_intermediate.int_customer_strategic_segment
    """

    df = con.execute(query).df()
    validate_dataframe(df, "Customer segmentation data", min_rows=100)

    return df


def cluster_high_value_clients(
    clienti: pd.DataFrame, con: duckdb.DuckDBPyConnection, labeler: ClusterLabeler
) -> tuple[pd.DataFrame, pd.DataFrame, float]:
    """
    Cluster high-value clients (Upper-Retail, >1 product) using K-means.

    Automatically selects optimal number of clusters using silhouette score.
    Generates semantic labels for clusters and writes results to database.

    Args:
        clienti: Customer DataFrame with segmentation data
        con: DuckDB connection for writing results
        labeler: ClusterLabeler instance for semantic labels

    Returns:
        Tuple of (labeled_df, cluster_summary, silhouette_score)

    Raises:
        ValueError: If clustering validation fails
    """
    high_val = clienti[
        (clienti["segmento_valore"] == "Upper-Retail") & (clienti["num_prodotti_posseduti"] > 1)
    ].copy()

    if high_val.empty:
        raise ValueError("No high-value multi-product customers found for clustering")

    if len(high_val) < 10:
        raise ValueError(f"Insufficient high-value customers for clustering: {len(high_val)}")

    features = [
        "possiede_casa",
        "possiede_salute",
        "possiede_investimento",
        "possiede_pip",
        "engagement_score",
        "churn_probability",
        "patrimonio_totale",
        "clv_stimato",
        "num_sinistri",
        "num_reclami",
        "num_interazioni",
        "tasso_conversione",
    ]

    X = high_val[features].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Determine best k using silhouette score
    best_k = 2
    best_score = -1
    max_k = min(6, len(high_val) // 3)  # At least 3 customers per cluster

    if max_k < 2:
        raise ValueError(f"Not enough customers for clustering: {len(high_val)}")

    for k in range(2, max_k + 1):
        km = KMeans(n_clusters=k, random_state=0, n_init=10)
        labels = km.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        if score > best_score:
            best_score, best_k = score, k

    # Validate silhouette score
    if best_score < 0.2:
        raise ValueError(
            f"Clustering quality too low (silhouette={best_score:.3f}). "
            "Data may not have clear cluster structure."
        )

    # Final clustering with best k
    km_final = KMeans(n_clusters=best_k, random_state=0, n_init=10)
    high_val["cluster"] = km_final.fit_predict(X_scaled)

    # Add cluster back to main dataset
    clienti_with_clusters = clienti.copy()
    clienti_with_clusters["cluster"] = -1  # Default for non-clustered
    clienti_with_clusters.loc[high_val.index, "cluster"] = high_val["cluster"]

    # Compute summary statistics per cluster
    cluster_summary = high_val.groupby("cluster")[features].mean().reset_index()
    cluster_summary["num_customers"] = high_val.groupby("cluster").size().values

    # Generate semantic labels
    labeled_summary = labeler.label_clusters(cluster_summary, MODEL_VERSION)

    # Validate cluster sizes
    min_cluster_size = labeled_summary["num_customers"].min()
    if min_cluster_size < 3:
        raise ValueError(
            f"Cluster too small (min size={min_cluster_size}). "
            "Consider reducing number of clusters."
        )

    return clienti_with_clusters, labeled_summary, best_score


def write_to_database(
    con: duckdb.DuckDBPyConnection, table_name: str, df: pd.DataFrame, schema: str = "analytics"
) -> None:
    """
    Write DataFrame to DuckDB table with validation.

    Args:
        con: DuckDB connection
        table_name: Name of target table
        df: DataFrame to write
        schema: Schema name (default: 'analytics')

    Raises:
        ValueError: If DataFrame validation fails
    """
    validate_dataframe(df, f"Table {table_name}")

    # Create schema if not exists
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    # Drop and recreate table (full refresh)
    full_table_name = f"{schema}.{table_name}"
    con.execute(f"DROP TABLE IF EXISTS {full_table_name}")

    # Register DataFrame and create table
    con.register("temp_df", df)
    con.execute(f"CREATE TABLE {full_table_name} AS SELECT * FROM temp_df")
    con.unregister("temp_df")

    # Validate write
    row_count = con.execute(f"SELECT COUNT(*) FROM {full_table_name}").fetchone()[0]
    if row_count != len(df):
        raise ValueError(
            f"Row count mismatch for {full_table_name}: " f"expected {len(df)}, got {row_count}"
        )


def main() -> int:
    """
    Execute clustering pipeline.

    Returns:
        0 on success, non-zero on failure
    """
    try:
        print("=" * 70)
        print("CUSTOMER CLUSTERING PIPELINE")
        print("=" * 70)
        print(f"Model version: {MODEL_VERSION}")
        print(f"Database: {DB_PATH}")
        print()

        # Connect to database
        if not DB_PATH.exists():
            raise ValueError(f"Database not found: {DB_PATH}. Run data_loader.py first.")

        con = duckdb.connect(str(DB_PATH))

        # Load data from dbt models
        print("[1/5] Loading customer data from dbt models...")
        clienti = load_customer_data(con)
        print(f"      Loaded {len(clienti):,} customers")

        # Initialize labeler
        print("[2/5] Initializing cluster labeler...")
        labeler = ClusterLabeler()

        # Perform clustering
        print("[3/5] Clustering high-value customers...")
        clienti_clustered, cluster_summary, silhouette = cluster_high_value_clients(
            clienti, con, labeler
        )
        num_clusters = cluster_summary["cluster"].nunique()
        num_clustered = (clienti_clustered["cluster"] >= 0).sum()
        print(f"      Created {num_clusters} clusters")
        print(f"      Clustered {num_clustered:,} customers")
        print(f"      Silhouette score: {silhouette:.3f}")

        # Create metadata
        print("[4/5] Generating cluster metadata...")
        cluster_metadata = create_cluster_metadata(
            cluster_summary, labeler, MODEL_VERSION, silhouette
        )

        # Print cluster labels
        print("\n      Cluster Labels:")
        for _, row in cluster_metadata.iterrows():
            print(
                f"        Cluster {row['cluster_id']}: {row['etichetta_cluster']} "
                f"({row['num_clienti']:,} customers)"
            )

        # Write to database
        print("\n[5/5] Writing results to database...")

        # Customer clusters
        cluster_output = clienti_clustered[
            ["codice_cliente", "cluster", "segmento_valore", "fase_vita", "num_prodotti_posseduti"]
        ].copy()
        cluster_output["versione_modello"] = MODEL_VERSION
        write_to_database(con, "customer_clusters", cluster_output)
        print(f"      ✓ analytics.customer_clusters ({len(cluster_output):,} rows)")

        # Cluster metadata
        write_to_database(con, "cluster_metadata", cluster_metadata)
        print(f"      ✓ analytics.cluster_metadata ({len(cluster_metadata)} rows)")

        # Cluster summary
        cluster_summary_output = cluster_summary.copy()
        cluster_summary_output["versione_modello"] = MODEL_VERSION
        write_to_database(con, "cluster_summary", cluster_summary_output)
        print(f"      ✓ analytics.cluster_summary ({len(cluster_summary_output)} rows)")

        con.close()

        print("\n" + "=" * 70)
        print("✓ PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70)
        return 0

    except Exception as e:
        print(f"\n✗ PIPELINE FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
