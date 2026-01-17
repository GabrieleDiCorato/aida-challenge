"""
Cluster-aware NBA enhancement pipeline.

This script enhances NBA recommendations by incorporating cluster insights
and interaction preferences. It performs:

1. Cluster assignment for single-product Upper-Retail clients
2. Cluster-aware NBA recommendations
3. Urgency tier adjustment based on customer responsiveness
4. Best contact channel determination

Reads from dbt models and analytics schema, writes enhanced NBA data
back to analytics schema for consumption by dbt marts.
"""

import datetime
from pathlib import Path
from typing import Dict
import pandas as pd
import duckdb

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "aida_challenge.duckdb"
MODEL_VERSION = datetime.datetime.now().strftime("v%Y%m")

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------


def validate_dataframe(df: pd.DataFrame, name: str, min_rows: int = 1) -> None:
    """Validate DataFrame meets basic requirements."""
    if df is None or df.empty:
        raise ValueError(f"{name} is empty")

    if len(df) < min_rows:
        raise ValueError(f"{name} has only {len(df)} rows, expected at least {min_rows}")


def load_inputs(con: duckdb.DuckDBPyConnection) -> Dict[str, pd.DataFrame]:
    """Load all required data from database."""
    data = {}

    # Customer strategic segmentation
    data["customers"] = con.execute(
        """
        SELECT
            codice_cliente,
            segmento_valore,
            fase_vita,
            num_prodotti_posseduti,
            possiede_casa,
            possiede_salute,
            possiede_investimento,
            possiede_pip,
            patrimonio_totale,
            raccomandazione_nba,
            livello_urgenza
        FROM main_intermediate.int_customer_strategic_segment
    """
    ).df()
    validate_dataframe(data["customers"], "Customer data")

    # Cluster assignments
    data["clusters"] = con.execute(
        """
        SELECT
            codice_cliente,
            cluster as cluster_id,
            versione_modello
        FROM analytics.customer_clusters
        WHERE versione_modello = ?
    """,
        [MODEL_VERSION],
    ).df()

    # If no clusters for this version, try latest
    if data["clusters"].empty:
        latest_version_result = con.execute(
            """
            SELECT versione_modello
            FROM analytics.customer_clusters
            ORDER BY versione_modello DESC
            LIMIT 1
        """
        ).fetchone()

        if latest_version_result:
            data["clusters"] = con.execute(
                """
                SELECT
                    codice_cliente,
                    cluster as cluster_id,
                    versione_modello
                FROM analytics.customer_clusters
                WHERE versione_modello = ?
            """,
                [latest_version_result[0]],
            ).df()

    # Cluster summary
    if not data["clusters"].empty:
        version = data["clusters"]["versione_modello"].iloc[0]
        data["cluster_summary"] = con.execute(
            """
            SELECT
                cluster,
                possiede_casa,
                possiede_salute,
                possiede_investimento,
                possiede_pip,
                patrimonio_totale
            FROM analytics.cluster_summary
            WHERE versione_modello = ?
        """,
            [version],
        ).df()
    else:
        data["cluster_summary"] = pd.DataFrame()

    # Customer responder classification
    data["responder"] = con.execute(
        """
        SELECT
            codice_cliente,
            cluster_risposta
        FROM clienti
    """
    ).df()
    validate_dataframe(data["responder"], "Responder data")

    # Interactions for channel analysis
    data["interactions"] = con.execute(
        """
        SELECT
            codice_cliente,
            tipo_interazione,
            conversione
        FROM interazioni_clienti
    """
    ).df()
    validate_dataframe(data["interactions"], "Interactions data")

    return data


def compute_cluster_product_mix(cluster_summary: pd.DataFrame) -> pd.DataFrame:
    """
    Compute product ownership proportions by cluster.

    Returns DataFrame with cluster and mean ownership for each product.
    """
    if cluster_summary.empty:
        return pd.DataFrame(
            columns=[
                "cluster",
                "possiede_casa",
                "possiede_salute",
                "possiede_investimento",
                "possiede_pip",
            ]
        )

    product_cols = ["possiede_casa", "possiede_salute", "possiede_investimento", "possiede_pip"]

    cluster_mix = cluster_summary[["cluster"] + product_cols].copy()
    return cluster_mix


def assign_single_product_clusters(
    customers: pd.DataFrame,
    clusters: pd.DataFrame,
    cluster_mix: pd.DataFrame,
    cluster_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Assign clusters to Upper-Retail clients with exactly one product.

    Uses product affinity - assigns to cluster where that product is most common.
    Ties broken by highest average wealth.
    """
    # Merge existing clusters
    customers_with_clusters = customers.merge(
        clusters[["codice_cliente", "cluster_id"]], on="codice_cliente", how="left"
    )

    if cluster_mix.empty:
        customers_with_clusters["cluster_id"] = customers_with_clusters["cluster_id"].fillna(-1)
        return customers_with_clusters

    # Identify clients needing cluster assignment
    needs_assignment = (
        (customers_with_clusters["segmento_valore"] == "Upper-Retail")
        & (customers_with_clusters["num_prodotti_posseduti"] == 1)
        & (customers_with_clusters["cluster_id"].isna())
    )

    if not needs_assignment.any():
        customers_with_clusters["cluster_id"] = customers_with_clusters["cluster_id"].fillna(-1)
        return customers_with_clusters

    # For each single-product client, find best matching cluster
    product_cols = ["possiede_casa", "possiede_salute", "possiede_investimento", "possiede_pip"]

    # Wealth ordering for tie-breaking
    if "patrimonio_totale" in cluster_summary.columns:
        wealth_order = cluster_summary.sort_values("patrimonio_totale", ascending=False)[
            "cluster"
        ].tolist()
    else:
        wealth_order = cluster_summary["cluster"].tolist()

    assigned_clusters = []
    for idx, row in customers_with_clusters[needs_assignment].iterrows():
        # Find which product is owned
        owned_product = None
        for col in product_cols:
            if row[col] == 1:
                owned_product = col
                break

        if owned_product is None:
            # Shouldn't happen for single-product clients
            assigned_clusters.append(wealth_order[0] if wealth_order else -1)
            continue

        # Find cluster with highest ownership of this product
        cluster_scores = cluster_mix.set_index("cluster")[owned_product].to_dict()

        if not cluster_scores:
            assigned_clusters.append(wealth_order[0] if wealth_order else -1)
            continue

        max_score = max(cluster_scores.values())
        candidates = [c for c, s in cluster_scores.items() if s == max_score]

        # Tie-break by wealth
        best_cluster = None
        for c in wealth_order:
            if c in candidates:
                best_cluster = c
                break

        assigned_clusters.append(best_cluster if best_cluster is not None else candidates[0])

    # Assign clusters
    customers_with_clusters.loc[needs_assignment, "cluster_id"] = assigned_clusters
    customers_with_clusters["cluster_id"] = (
        customers_with_clusters["cluster_id"].fillna(-1).astype(int)
    )

    return customers_with_clusters


def compute_cluster_product_ranking(cluster_mix: pd.DataFrame) -> Dict[int, list]:
    """
    For each cluster, rank products by ownership proportion.

    Returns dict mapping cluster_id to list of products in descending order.
    """
    if cluster_mix.empty:
        return {}

    product_cols = ["possiede_casa", "possiede_salute", "possiede_investimento", "possiede_pip"]
    product_names = ["Casa", "Salute", "Investimento", "PIP"]

    ranking = {}
    for _, row in cluster_mix.iterrows():
        cluster_id = int(row["cluster"])
        # Sort products by ownership proportion
        products_with_scores = [(name, row[col]) for name, col in zip(product_names, product_cols)]
        products_with_scores.sort(key=lambda x: x[1], reverse=True)
        ranking[cluster_id] = [p[0] for p in products_with_scores]

    return ranking


def enhance_nba_with_clusters(
    customers: pd.DataFrame, product_ranking: Dict[int, list]
) -> pd.DataFrame:
    """
    Enhance NBA recommendations using cluster product preferences.

    For Upper-Retail clients in a cluster, recommend first missing product
    in cluster's ranked list.
    """
    enhanced = customers.copy()

    def cluster_nba(row):
        # Only enhance Upper-Retail clients
        if row["segmento_valore"] != "Upper-Retail":
            return row["raccomandazione_nba"]

        cluster_id = int(row["cluster_id"])
        if cluster_id < 0:
            return row["raccomandazione_nba"]

        # Get cluster's product ranking
        ranked_products = product_ranking.get(cluster_id, ["Casa", "Salute", "Investimento", "PIP"])

        # Find missing products
        owned = {
            "Casa": row["possiede_casa"],
            "Salute": row["possiede_salute"],
            "Investimento": row["possiede_investimento"],
            "PIP": row["possiede_pip"],
        }
        missing = [p for p in ranked_products if owned.get(p, 0) == 0]

        if not missing:
            return "Retention"

        # Recommend first missing product in cluster's preference order
        return missing[0]

    enhanced["raccomandazione_nba_cluster"] = enhanced.apply(cluster_nba, axis=1)
    return enhanced


def adjust_urgency_by_responsiveness(
    customers: pd.DataFrame, responder: pd.DataFrame
) -> pd.DataFrame:
    """
    Adjust urgency tier based on customer responsiveness.

    High responders get bumped up one urgency level for non-retention NBA.
    """
    enhanced = customers.merge(
        responder[["codice_cliente", "cluster_risposta"]], on="codice_cliente", how="left"
    )

    urgency_levels = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
    inv_urgency = {v: k for k, v in urgency_levels.items()}

    def adjust_urgency(row):
        level = urgency_levels.get(row["livello_urgenza"], 0)

        # Bump up high responders with non-retention NBA
        if (
            row["cluster_risposta"] == "High_Responder"
            and row["raccomandazione_nba_cluster"] != "Retention"
        ):
            level = min(level + 1, 3)

        return inv_urgency.get(level, row["livello_urgenza"])

    enhanced["livello_urgenza_adjusted"] = enhanced.apply(adjust_urgency, axis=1)
    return enhanced


def determine_best_channel(interactions: pd.DataFrame) -> pd.DataFrame:
    """
    Determine best contact channel for each customer.

    Chooses channel with highest conversion rate, or most frequent if no conversions.
    """
    # Convert boolean to int
    interactions_clean = interactions.copy()
    interactions_clean["conversione"] = interactions_clean["conversione"].map({True: 1, False: 0})

    # Compute conversion rate per customer per channel
    channel_stats = (
        interactions_clean.groupby(["codice_cliente", "tipo_interazione"])
        .agg(conversion_rate=("conversione", "mean"), interaction_count=("conversione", "count"))
        .reset_index()
    )

    # Find best channel for each customer
    def pick_best_channel(group):
        # Highest conversion rate
        max_conv = group["conversion_rate"].max()
        candidates = group[group["conversion_rate"] == max_conv]

        if len(candidates) == 1:
            return candidates.iloc[0]["tipo_interazione"]

        # Tie-break with interaction count
        max_count = candidates["interaction_count"].max()
        top = candidates[candidates["interaction_count"] == max_count]

        # Final tie-break: alphabetical
        return sorted(top["tipo_interazione"].tolist())[0]

    best_channels = (
        channel_stats.groupby("codice_cliente")
        .apply(pick_best_channel)
        .reset_index(name="canale_migliore")
    )

    return best_channels


def write_to_database(
    con: duckdb.DuckDBPyConnection, table_name: str, df: pd.DataFrame, schema: str = "analytics"
) -> None:
    """Write DataFrame to DuckDB with validation."""
    validate_dataframe(df, f"Table {table_name}")

    con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    full_table_name = f"{schema}.{table_name}"
    con.execute(f"DROP TABLE IF EXISTS {full_table_name}")

    con.register("temp_df", df)
    con.execute(f"CREATE TABLE {full_table_name} AS SELECT * FROM temp_df")
    con.unregister("temp_df")

    row_count = con.execute(f"SELECT COUNT(*) FROM {full_table_name}").fetchone()[0]
    if row_count != len(df):
        raise ValueError(
            f"Row count mismatch for {full_table_name}: expected {len(df)}, got {row_count}"
        )


def main() -> int:
    """Execute cluster-aware NBA enhancement pipeline."""
    try:
        print("=" * 70)
        print("CLUSTER-AWARE NBA ENHANCEMENT PIPELINE")
        print("=" * 70)
        print(f"Model version: {MODEL_VERSION}")
        print(f"Database: {DB_PATH}")
        print()

        if not DB_PATH.exists():
            raise ValueError(f"Database not found: {DB_PATH}")

        con = duckdb.connect(str(DB_PATH))

        # Load data
        print("[1/6] Loading data from database...")
        data = load_inputs(con)
        print(f"      Loaded {len(data['customers']):,} customers")
        print(f"      Loaded {len(data['clusters']):,} cluster assignments")

        # Compute cluster product mix
        print("[2/6] Computing cluster product preferences...")
        cluster_mix = compute_cluster_product_mix(data["cluster_summary"])
        product_ranking = compute_cluster_product_ranking(cluster_mix)

        if cluster_mix.empty:
            print("      ⚠ No cluster data available, skipping cluster-aware enhancements")
            # Write basic NBA data
            output = data["customers"].copy()
            output["raccomandazione_nba_cluster"] = output["raccomandazione_nba"]
            output["livello_urgenza_adjusted"] = output["livello_urgenza"]
            output["cluster_id"] = -1
        else:
            print(f"      Computed preferences for {len(cluster_mix)} clusters")

            # Assign single-product clusters
            print("[3/6] Assigning clusters to single-product clients...")
            customers_with_clusters = assign_single_product_clusters(
                data["customers"], data["clusters"], cluster_mix, data["cluster_summary"]
            )
            assigned = (customers_with_clusters["cluster_id"] >= 0).sum()
            print(f"      {assigned:,} customers have cluster assignments")

            # Enhance NBA
            print("[4/6] Enhancing NBA recommendations with cluster insights...")
            customers_enhanced = enhance_nba_with_clusters(customers_with_clusters, product_ranking)

            # Adjust urgency
            print("[5/6] Adjusting urgency tiers by responsiveness...")
            output = adjust_urgency_by_responsiveness(customers_enhanced, data["responder"])

        # Determine best channels
        print("[6/6] Determining best contact channels...")
        best_channels = determine_best_channel(data["interactions"])
        output = output.merge(best_channels, on="codice_cliente", how="left")
        output["canale_migliore"] = output["canale_migliore"].fillna("N/A")
        print(
            f"      Determined channels for {(output['canale_migliore'] != 'N/A').sum():,} customers"
        )

        # Write output
        print("\n[7/7] Writing enhanced NBA data to database...")
        output_table = output[
            [
                "codice_cliente",
                "cluster_id",
                "raccomandazione_nba_cluster",
                "livello_urgenza_adjusted",
                "canale_migliore",
            ]
        ].copy()
        output_table["versione_modello"] = MODEL_VERSION

        write_to_database(con, "nba_enhanced", output_table)
        print(f"      ✓ analytics.nba_enhanced ({len(output_table):,} rows)")

        # Write cluster product mix
        if not cluster_mix.empty:
            cluster_mix_output = cluster_mix.copy()
            cluster_mix_output["versione_modello"] = MODEL_VERSION
            write_to_database(con, "cluster_product_mix", cluster_mix_output)
            print(f"      ✓ analytics.cluster_product_mix ({len(cluster_mix_output)} rows)")

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
