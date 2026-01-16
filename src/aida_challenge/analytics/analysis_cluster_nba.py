"""
analysis_cluster_nba.py
-----------------------

This script enhances the existing client‑level NBA outputs by
incorporating unsupervised cluster insights and interaction preferences.
Starting from the previously generated ``client_nba_enhanced.csv`` and
``hv_cluster_summary.csv``, it performs the following steps:

1. **Cluster assignment for one‑product Upper‑Retail clients**
   Clients in the ``Upper‑Retail`` value segment who own exactly one
   product are not present in the original K‑Means clustering (which
   only covers high‑value multi‑product customers).  To bring them
   into the same segmentation framework, we assign them to the cluster
   whose members most frequently own the same product.  If multiple
   clusters share the same ownership level, the script picks the
   cluster with the highest average ``Total_Wealth`` (proxy for
   similarity).  The cluster summaries used to compute these
   statistics are derived from the high‑value clusters.

2. **Cluster‑aware NBA recommendations**
   Once a one‑product client has been assigned to a cluster, the script
   determines the cluster’s most common product mix (a ranked list of
   product categories).  The new next‑best action (NBA) recommends the
   first missing product in that cluster’s ranked list.  For clients
   already clustered (multi‑product high‑value clients) the same logic
   applies.  Non Upper‑Retail clients retain their original
   rule‑based NBA recommendation.

3. **Urgency tier adjusted by responsiveness**
   The script merges the ``Cluster_Risposta`` (high/moderate/low
   responder classification) from ``clienti.csv``.  If a client is
   labelled ``High_Responder`` and has a non‑retention NBA, the
   urgency tier is bumped up one level (e.g. ``MEDIUM`` → ``HIGH``).
   This reflects the intuition that high responders should be
   prioritised even if their last visit was not recent.

4. **Best contact channel**
   Using ``interazioni_clienti.csv``, the script computes the
   conversion rate for each client/channel pair.  The best channel is
   chosen as the one with the highest conversion rate; if no channel
   shows any conversions, the most frequently used channel is picked.
   A default of ``N/A`` is assigned when a client has no recorded
   interactions.

The final enriched dataset is written to ``client_enhanced_nba.csv``
in the ``output`` folder.  A small CSV summarising the product
ownership distribution by cluster (used to drive the cluster‑aware
recommendations) is also saved as ``cluster_product_mix.csv``.
"""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_inputs() -> dict:
    """Load the prerequisite CSV files into DataFrames."""
    paths = {
        "client_enhanced": os.path.join(DATA_DIR, "client_nba_enhanced.csv"),
        "hv_summary": os.path.join(DATA_DIR, "hv_cluster_summary.csv"),
        "clienti": os.path.join(DATA_DIR, "clienti.csv"),
        "interazioni": os.path.join(DATA_DIR, "interazioni_clienti.csv"),
    }
    data = {}
    for key, path in paths.items():
        data[key] = pd.read_csv(path)
    return data


def compute_cluster_product_mix(client_enhanced: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the proportion of clients in each cluster who own each
    product.  Returns a DataFrame indexed by cluster with columns
    'casa_owned', 'salute_owned', 'investimento_owned', 'pip_owned'.
    """
    hv = client_enhanced[client_enhanced["cluster"] >= 0]
    if hv.empty:
        # If no high-value clients are present, return an empty frame
        return pd.DataFrame(
            columns=["cluster", "casa_owned", "salute_owned", "investimento_owned", "pip_owned"]
        )
    # Group by cluster and compute mean of ownership flags
    product_cols = ["casa_owned", "salute_owned", "investimento_owned", "pip_owned"]
    cluster_mix = hv.groupby("cluster")[product_cols].mean()
    cluster_mix = cluster_mix.reset_index()
    return cluster_mix


def assign_one_product_cluster(
    client_enhanced: pd.DataFrame, cluster_mix: pd.DataFrame, summary: pd.DataFrame
) -> pd.Series:
    """
    Assign clusters to Upper-Retail clients with exactly one product.

    Args:
        client_enhanced: full client DataFrame
        cluster_mix: DataFrame with cluster product proportions
        summary: hv_cluster_summary DataFrame containing average
            Total_Wealth per cluster (fallback for ties)

    Returns:
        Series of assigned cluster IDs for clients with 1 product;
        index aligned with client_enhanced.
    """
    # Determine cluster prevalence for each product
    product_cols = ["casa_owned", "salute_owned", "investimento_owned", "pip_owned"]
    # Convert cluster mix to dictionary keyed by product
    mix_dict = {}
    for col in product_cols:
        mix_dict[col] = cluster_mix.set_index("cluster")[col].to_dict()

    # Fallback ordering by Total_Wealth: choose cluster with highest wealth
    if "Total_Wealth" in summary.columns:
        wealth_order = summary.sort_values("Total_Wealth", ascending=False)["cluster"].tolist()
    else:
        wealth_order = summary["cluster"].tolist()

    assigned = []
    for idx, row in client_enhanced.iterrows():
        # Only assign if exactly one product and Upper-Retail
        if row["value_segment"] != "Upper-Retail" or row["num_products"] != 1:
            assigned.append(np.nan)
            continue
        # Identify which product is owned
        owned_product = None
        for col in product_cols:
            if row[col] == 1:
                owned_product = col
                break
        # Determine the cluster with the highest ownership for that product
        if owned_product is None:
            # No product found (should not happen for num_products == 1)
            assigned.append(wealth_order[0] if wealth_order else -1)
            continue
        # Get ownership proportion per cluster for this product
        proportions = mix_dict.get(owned_product, {})
        if len(proportions) == 0:
            assigned.append(wealth_order[0] if wealth_order else -1)
            continue
        # Find cluster(s) with max proportion
        max_prop = max(proportions.values())
        candidates = [c for c, p in proportions.items() if p == max_prop]
        # Tie-break using wealth order
        chosen_cluster = None
        for c in wealth_order:
            if c in candidates:
                chosen_cluster = c
                break
        assigned.append(chosen_cluster if chosen_cluster is not None else candidates[0])
    return pd.Series(assigned, index=client_enhanced.index)


def determine_cluster_ranked_products(cluster_mix: pd.DataFrame) -> dict:
    """
    For each cluster, produce a ranked list of product categories
    (strings: 'casa', 'salute', 'investimento', 'pip') ordered by
    decreasing ownership proportion.  Returns a dict mapping cluster
    id to list of products.
    """
    product_cols = ["casa_owned", "salute_owned", "investimento_owned", "pip_owned"]
    ranking = {}
    for _, row in cluster_mix.iterrows():
        cluster_id = row["cluster"]
        # Sort product columns by decreasing mean proportion
        sorted_products = sorted(product_cols, key=lambda col: row[col], reverse=True)
        # Convert from flag column names to base product names
        sorted_names = [col.replace("_owned", "") for col in sorted_products]
        ranking[cluster_id] = sorted_names
    return ranking


def enhance_nba(data: dict) -> pd.DataFrame:
    """
    Generate an enhanced client DataFrame with cluster-aware NBA,
    updated urgency tiers and contact channel suggestions.

    Args:
        data: dictionary of DataFrames loaded by load_inputs()

    Returns:
        DataFrame with new columns: cluster_assigned (for one-product clients),
        nba_clustered (cluster-aware NBA), adjusted_urgency, best_contact_channel
    """
    clients = data["client_enhanced"].copy()
    summary = data["hv_summary"].copy()
    # Compute cluster product proportions and ranking
    cluster_mix = compute_cluster_product_mix(clients)
    ranking = determine_cluster_ranked_products(cluster_mix) if not cluster_mix.empty else {}

    # Assign clusters to one-product Upper-Retail clients
    assigned_clusters = assign_one_product_cluster(clients, cluster_mix, summary)
    clients["cluster_assigned"] = assigned_clusters

    # Fill missing cluster assignments with existing cluster values
    # For multi-product or non-Upper-Retail clients, cluster_assigned remains NaN
    clients.loc[clients["cluster"] >= 0, "cluster_assigned"] = clients.loc[
        clients["cluster"] >= 0, "cluster"
    ]
    # Convert to int where possible
    clients["cluster_assigned"] = clients["cluster_assigned"].fillna(-1).astype(int)

    # Determine NBA per cluster for all clients
    def cluster_based_nba(row):
        # Only override for Upper-Retail clients
        if row["value_segment"] != "Upper-Retail":
            return row["nba_recommendation"]
        cluster_id = row["cluster_assigned"]
        if cluster_id < 0:
            return row["nba_recommendation"]
        # Determine missing products
        owned_flags = {
            "casa": row["casa_owned"],
            "salute": row["salute_owned"],
            "investimento": row["investimento_owned"],
            "pip": row["pip_owned"],
        }
        missing = [p for p, flag in owned_flags.items() if flag == 0]
        # Get ranked products for cluster
        ranked = ranking.get(cluster_id, ["casa", "salute", "investimento", "pip"])
        # Propose first missing product in ranked order
        for p in ranked:
            if p in missing:
                return p.capitalize() if p != "pip" else "PIP"
        # If none missing in ranked order, default to original NBA
        return row["nba_recommendation"]

    clients["nba_clustered"] = clients.apply(cluster_based_nba, axis=1)

    # Merge Cluster_Risposta to compute high responder adjustments
    clienti = data["clienti"][["codice_cliente", "Cluster_Risposta"]].copy()
    clienti.rename(columns={"Cluster_Risposta": "responder_class"}, inplace=True)
    clients = clients.merge(clienti, on="codice_cliente", how="left")

    # Map urgency tiers to numeric levels for adjustment
    urgency_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
    inv_urgency_map = {v: k for k, v in urgency_map.items()}
    clients["urgency_level"] = clients["urgency_tier"].map(urgency_map)

    # Adjust urgency: bump up one level for high responders with non-retention NBA
    def adjust_urgency(row):
        level = row["urgency_level"]
        if row["responder_class"] == "High_Responder" and row["nba_clustered"] != "Retention":
            level = min(level + 1, 3)
        return inv_urgency_map.get(level, row["urgency_tier"])

    clients["adjusted_urgency"] = clients.apply(adjust_urgency, axis=1)

    # Determine best contact channel using interactions
    interazioni = data["interazioni"][["codice_cliente", "Tipo_Interazione", "Conversione"]].copy()
    # Convert Conversione to numeric 1/0 for mean
    interazioni["Conversione"] = interazioni["Conversione"].map({True: 1, False: 0})
    # Compute conversion rate per client per channel
    conv_rate = (
        interazioni.groupby(["codice_cliente", "Tipo_Interazione"])["Conversione"]
        .mean()
        .reset_index(name="conversion_rate")
    )
    # Compute interaction count per client per channel
    count_inter = (
        interazioni.groupby(["codice_cliente", "Tipo_Interazione"])
        .size()
        .reset_index(name="inter_count")
    )
    # Merge to compute best channel
    channel_stats = conv_rate.merge(count_inter, on=["codice_cliente", "Tipo_Interazione"])

    # Determine best channel for each client
    def pick_channel(group):
        # group: rows for one client with channels and conversion rates
        # Choose channel with highest conversion_rate; if tie (or all zero), choose highest inter_count
        max_conv = group["conversion_rate"].max()
        candidates = group[group["conversion_rate"] == max_conv]
        if len(candidates) == 1:
            return candidates.iloc[0]["Tipo_Interazione"]
        # tie: choose channel with largest inter_count
        max_count = candidates["inter_count"].max()
        top = candidates[candidates["inter_count"] == max_count]
        # if still tie, pick first in alphabetical order
        return sorted(top["Tipo_Interazione"].tolist())[0]

    best_channel = (
        channel_stats.groupby("codice_cliente")
        .apply(pick_channel)
        .reset_index(name="best_contact_channel")
    )
    # Merge best channel back
    clients = clients.merge(best_channel, on="codice_cliente", how="left")
    # Fill missing with 'N/A' for clients with no interactions
    clients["best_contact_channel"] = clients["best_contact_channel"].fillna("N/A")

    # Select final columns and write out
    out_cols = list(clients.columns)
    # Write final file
    final_path = os.path.join(OUTPUT_DIR, "client_enhanced_nba.csv")
    clients[out_cols].to_csv(final_path, index=False)

    # Write cluster mix summary for transparency
    mix_path = os.path.join(OUTPUT_DIR, "cluster_product_mix.csv")
    cluster_mix.to_csv(mix_path, index=False)

    return clients


def main():
    data = load_inputs()
    _ = enhance_nba(data)
    # Return path to the final file for sync
    return os.path.join(OUTPUT_DIR, "client_enhanced_nba.csv"), os.path.join(
        OUTPUT_DIR, "cluster_product_mix.csv"
    )


if __name__ == "__main__":
    final_file, mix_file = main()
    print("Generated:", final_file)
    print("Cluster mix:", mix_file)
