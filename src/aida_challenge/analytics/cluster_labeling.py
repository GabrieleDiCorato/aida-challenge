"""
Cluster semantic labeling utilities.

This module provides functionality to automatically generate meaningful semantic
labels for customer clusters based on their characteristics (centroids), and
supports manual override of labels by data scientists.

The semantic labels make cluster assignments more interpretable and stable across
model versions, compared to arbitrary numeric IDs.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd


class ClusterLabeler:
    """
    Generates and manages semantic labels for customer clusters.

    Labels are derived from cluster centroids by identifying dominant
    characteristics. Supports manual overrides which are persisted to disk.
    """

    def __init__(self, label_storage_path: Optional[Path] = None):
        """
        Initialize the cluster labeler.

        Args:
            label_storage_path: Path to JSON file for storing manual label overrides.
                               If None, uses default location in data/analytics/
        """
        if label_storage_path is None:
            root = Path(__file__).parent.parent.parent.parent
            label_storage_path = root / "data" / "analytics" / "cluster_labels.json"

        self.label_storage_path = label_storage_path
        self.manual_labels = self._load_manual_labels()

    def _load_manual_labels(self) -> Dict[str, Dict[int, str]]:
        """
        Load manual label overrides from JSON file.

        Returns:
            Dictionary mapping model version to cluster ID to label
            Format: {"v202601": {0: "High-Value Multi-Product", ...}}
        """
        if not self.label_storage_path.exists():
            return {}

        try:
            with open(self.label_storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load manual labels from {self.label_storage_path}: {e}")
            return {}

    def save_manual_label(self, version: str, cluster_id: int, label: str) -> None:
        """
        Save a manual label override for a specific cluster.

        Args:
            version: Model version (e.g., "v202601")
            cluster_id: Cluster numeric ID
            label: Semantic label to assign
        """
        if version not in self.manual_labels:
            self.manual_labels[version] = {}

        self.manual_labels[version][cluster_id] = label

        # Persist to disk
        self.label_storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.label_storage_path, "w", encoding="utf-8") as f:
            json.dump(self.manual_labels, f, indent=2, ensure_ascii=False)

    def generate_semantic_label(
        self, cluster_id: int, centroid: pd.Series, feature_names: List[str]
    ) -> str:
        """
        Generate a semantic label for a cluster based on its centroid.

        The label describes the cluster's dominant characteristics in order:
        1. Value level (based on Total_Wealth or CLV)
        2. Product profile (which products are most common)
        3. Engagement/risk (based on churn probability or engagement score)

        Args:
            cluster_id: Numeric cluster ID
            centroid: Pandas Series with feature values for the cluster center
            feature_names: List of feature names corresponding to centroid values

        Returns:
            Semantic label string (e.g., "High-Value Multi-Product Champions")
        """
        label_parts = []

        # 1. Value level based on wealth/CLV
        if "Total_Wealth" in centroid:
            wealth = centroid["Total_Wealth"]
            if wealth >= 200000:
                label_parts.append("High-Value")
            elif wealth >= 100000:
                label_parts.append("Mid-Value")
            else:
                label_parts.append("Entry-Value")
        elif "CLV_Stimato" in centroid:
            clv = centroid["CLV_Stimato"]
            if clv >= 50000:
                label_parts.append("High-CLV")
            elif clv >= 25000:
                label_parts.append("Mid-CLV")
            else:
                label_parts.append("Growing")

        # 2. Product profile
        product_flags = [col for col in centroid.index if col.endswith("_owned")]
        if product_flags:
            num_products = sum(centroid[flag] for flag in product_flags if flag in centroid)

            if num_products >= 0.75:  # Most customers have 3+ products
                # Identify dominant product mix
                # product_scores = {
                #    flag.replace("_owned", "").capitalize(): centroid[flag]
                #    for flag in product_flags
                # }
                # dominant = max(product_scores.items(), key=lambda x: x[1])[0]

                if centroid.get("investimento_owned", 0) >= 0.8:
                    label_parts.append("Investment-Focused")
                elif (
                    centroid.get("casa_owned", 0) >= 0.8 and centroid.get("salute_owned", 0) >= 0.8
                ):
                    label_parts.append("Protection-Complete")
                else:
                    label_parts.append("Multi-Product")
            elif num_products >= 0.5:
                # Moderate product ownership - identify primary product
                product_scores = {
                    flag.replace("_owned", ""): centroid[flag] for flag in product_flags
                }
                primary = max(product_scores.items(), key=lambda x: x[1])[0]
                label_parts.append(f"{primary.capitalize()}-Core")
            else:
                # Single product customers
                product_scores = {
                    flag.replace("_owned", ""): centroid[flag] for flag in product_flags
                }
                primary = max(product_scores.items(), key=lambda x: x[1])[0]
                label_parts.append(f"{primary.capitalize()}-Only")

        # 3. Engagement/Risk profile
        if "Churn_Probability" in centroid and "Engagement_Score" in centroid:
            churn = centroid["Churn_Probability"]
            engagement = centroid["Engagement_Score"]

            if engagement >= 70 and churn < 0.3:
                label_parts.append("Champions")
            elif churn >= 0.6:
                label_parts.append("At-Risk")
            elif engagement < 50:
                label_parts.append("Low-Engagement")
        elif "Engagement_Score" in centroid:
            engagement = centroid["Engagement_Score"]
            if engagement >= 70:
                label_parts.append("Engaged")
            elif engagement < 50:
                label_parts.append("Passive")

        # Combine parts into label
        if not label_parts:
            return f"Cluster {cluster_id}"

        return " ".join(label_parts)

    def label_clusters(
        self, cluster_summary: pd.DataFrame, version: str, cluster_id_col: str = "cluster"
    ) -> pd.DataFrame:
        """
        Generate semantic labels for all clusters in a summary DataFrame.

        Checks for manual overrides first, then generates automatic labels
        based on cluster characteristics.

        Args:
            cluster_summary: DataFrame with cluster centroids (one row per cluster)
            version: Model version identifier (e.g., "v202601")
            cluster_id_col: Name of column containing cluster IDs

        Returns:
            DataFrame with added 'etichetta_cluster' column containing semantic labels
        """
        labeled = cluster_summary.copy()
        labels = []

        # Get feature columns (exclude metadata and ID columns)
        metadata_cols = {cluster_id_col, "num_customers", "etichetta_cluster", "_dbt_loaded_at"}
        feature_cols = [col for col in labeled.columns if col not in metadata_cols]

        for _, row in labeled.iterrows():
            cluster_id = int(row[cluster_id_col])

            # Check for manual override
            if version in self.manual_labels and cluster_id in self.manual_labels[version]:
                label = self.manual_labels[version][cluster_id]
            else:
                # Generate automatic label
                centroid = row[feature_cols]
                label = self.generate_semantic_label(cluster_id, centroid, feature_cols)

            labels.append(label)

        labeled["etichetta_cluster"] = labels
        return labeled

    def get_label(self, version: str, cluster_id: int) -> Optional[str]:
        """
        Get the semantic label for a specific cluster.

        Args:
            version: Model version
            cluster_id: Cluster numeric ID

        Returns:
            Semantic label if available, None otherwise
        """
        if version in self.manual_labels and cluster_id in self.manual_labels[version]:
            return self.manual_labels[version][cluster_id]
        return None

    def list_manual_labels(self, version: Optional[str] = None) -> Dict:
        """
        List all manual label overrides.

        Args:
            version: If provided, only return labels for this version

        Returns:
            Dictionary of manual labels
        """
        if version is not None:
            return {version: self.manual_labels.get(version, {})}
        return self.manual_labels.copy()


def create_cluster_metadata(
    cluster_summary: pd.DataFrame, labeler: ClusterLabeler, version: str, silhouette_score: float
) -> pd.DataFrame:
    """
    Create metadata table for clusters with semantic labels and characteristics.

    Args:
        cluster_summary: DataFrame with cluster centroids
        labeler: ClusterLabeler instance
        version: Model version
        silhouette_score: Overall clustering silhouette score

    Returns:
        DataFrame with cluster metadata including labels and key characteristics
    """
    # Add semantic labels
    labeled_summary = labeler.label_clusters(cluster_summary, version)

    # Extract key characteristics as JSON
    metadata_rows = []
    for _, row in labeled_summary.iterrows():
        # Identify top 3 distinguishing features
        feature_cols = [
            col
            for col in labeled_summary.columns
            if col not in ["cluster", "etichetta_cluster", "num_customers", "_dbt_loaded_at"]
        ]

        # Build characteristics summary
        characteristics = {}
        for col in feature_cols:
            val = row[col]
            if not pd.isna(val):
                characteristics[col] = float(val)

        metadata_rows.append(
            {
                "cluster_id": int(row["cluster"]),
                "versione_modello": version,
                "etichetta_cluster": row["etichetta_cluster"],
                "num_clienti": int(row.get("num_customers", 0)),
                "silhouette_score": silhouette_score,
                "caratteristiche_json": json.dumps(characteristics, ensure_ascii=False),
            }
        )

    return pd.DataFrame(metadata_rows)
