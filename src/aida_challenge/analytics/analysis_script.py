"""
This script reproduces the entire data‑preparation and modelling pipeline
used to generate the client segmentation, clustering and Next Best Action
(NBA) outputs for the insurance dataset provided in this project.  It
cleans the raw CSV inputs, engineers domain‑specific features,
performs rule‑based segmentation, applies k‑means clustering to high‑value
customers, and computes simple dynamic NBA recommendations based on
temporal triggers.  It also synthesises a small artificial dataset to
demonstrate the Dynamic NBA concept for testing.
"""

import os
import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "analytics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
# Random seed for reproducibility
np.random.seed(42)

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------


def load_data(data_dir: str) -> dict:
    """Load all required CSVs into a dictionary of DataFrames."""
    files = {
        "clienti": "clienti.csv",
        "polizze": "polizze.csv",
        "sinistri": "sinistri.csv",
        "reclami": "reclami.csv",
        "abitazioni": "abitazioni.csv",
        "interazioni": "interazioni_clienti.csv",
    }
    data = {}
    for key, fname in files.items():
        path = os.path.join(data_dir, fname)
        data[key] = pd.read_csv(path)
    return data


def clean_and_engineer(data: dict) -> pd.DataFrame:
    """Perform cleaning and feature engineering on the raw data.

    Returns a single DataFrame with one row per client and engineered
    columns:
      - Total_Wealth, value_segment, life_stage
      - num_products, owned flags for Casa/Salute/Investimento/PIP
      - Aggregated metrics: num_claims, total_claim_amount, num_complaints,
        num_interactions, conversion_rate
      - Engagement and churn derived level
      - Recency (days_since_last_visit) and urgency tier
      - Strategic segment and NBA recommendation
    """
    clienti = data["clienti"].drop_duplicates(subset=["codice_cliente"]).copy()
    polizze = data["polizze"].loc[:, ~data["polizze"].columns.str.contains("Unnamed")].copy()
    sinistri = data["sinistri"].copy()
    reclami = data["reclami"].copy()
    interazioni = data["interazioni"].copy()

    # Ensure date columns are parsed
    polizze["Data di Emissione"] = pd.to_datetime(polizze["Data di Emissione"], errors="coerce")
    polizze["Data_Scadenza"] = pd.to_datetime(polizze["Data_Scadenza"], errors="coerce")
    sinistri["Data_Sinistro"] = pd.to_datetime(sinistri["Data_Sinistro"], errors="coerce")
    interazioni["Data_Interazione"] = pd.to_datetime(
        interazioni["Data_Interazione"], errors="coerce"
    )

    # Fill missing numeric columns
    for col in ["Reddito Familiare", "Patrimonio Finanziario Stimato", "Patrimonio Reale Stimato"]:
        clienti[col] = clienti[col].fillna(0)

    # Compute total wealth and value segment
    clienti["Total_Wealth"] = (
        clienti["Reddito Familiare"]
        + clienti["Patrimonio Finanziario Stimato"]
        + clienti["Patrimonio Reale Stimato"]
    )
    q25, q75 = clienti["Total_Wealth"].quantile([0.25, 0.75])

    def classify_value(val: float) -> str:
        if val >= q75:
            return "Upper-Retail"
        elif val >= q25:
            return "Mid-Retail"
        return "Entry-Retail"

    clienti["value_segment"] = clienti["Total_Wealth"].apply(classify_value)

    # Derive life stage based on age and number of children
    def life_stage(row) -> str:
        age = row["Età"]
        kids = row["Numero Figli"]
        if age < 30:
            return "Young Single" if kids == 0 else "Young Family"
        elif age < 40:
            return "Young Family" if kids > 0 else "Young Professional"
        elif age < 55:
            return "Established Family" if kids > 0 else "Established Professional"
        elif age < 65:
            return "Pre-Retirement"
        return "Retired"

    clienti["life_stage"] = clienti.apply(life_stage, axis=1)

    # Map policy categories and compute counts
    polizze["category"] = (
        polizze["Area di Bisogno"].astype(str).str.strip().str.lower().str.replace(" ", "_")
    )
    product_counts = polizze.groupby("codice_cliente")["category"].nunique().rename("num_products")
    major_categories = ["casa", "salute", "investimento", "pip"]
    category_presence = pd.DataFrame({"codice_cliente": clienti["codice_cliente"]})
    for cat in major_categories:
        cat_clients = polizze[polizze["category"].str.contains(cat, na=False)][
            "codice_cliente"
        ].unique()
        category_presence[f"{cat}_owned"] = (
            category_presence["codice_cliente"].isin(cat_clients).astype(int)
        )

    clienti = clienti.merge(product_counts, on="codice_cliente", how="left")
    clienti["num_products"] = clienti["num_products"].fillna(0).astype(int)
    clienti = clienti.merge(category_presence, on="codice_cliente", how="left")
    clienti[[f"{cat}_owned" for cat in major_categories]] = (
        clienti[[f"{cat}_owned" for cat in major_categories]].fillna(0).astype(int)
    )

    # Aggregate claims (sinistri)
    claims_agg = (
        sinistri.groupby("codice_cliente")
        .agg(
            num_claims=("Importo_Liquidato", "count"),
            total_claim_amount=("Importo_Liquidato", "sum"),
        )
        .reset_index()
    )

    # Aggregate complaints (reclami)
    reclami_agg = reclami.groupby("codice_cliente").size().rename("num_complaints").reset_index()

    # Aggregate interactions for the last year
    current_date = pd.Timestamp(datetime.date.today())
    one_year_ago = current_date - pd.Timedelta(days=365)
    interazioni_recent = interazioni[interazioni["Data_Interazione"] >= one_year_ago]
    inter_agg = (
        interazioni_recent.groupby("codice_cliente")
        .agg(
            num_interactions=("Conversione", "count"),
            conversion_rate=("Conversione", "mean"),
            avg_duration=("Durata_Minuti", "mean"),
        )
        .reset_index()
    )

    # Merge aggregates
    clienti = clienti.merge(claims_agg, on="codice_cliente", how="left")
    clienti = clienti.merge(reclami_agg, on="codice_cliente", how="left")
    clienti = clienti.merge(inter_agg, on="codice_cliente", how="left")
    for col in [
        "num_claims",
        "total_claim_amount",
        "num_complaints",
        "num_interactions",
        "conversion_rate",
        "avg_duration",
    ]:
        clienti[col] = clienti[col].fillna(0)

    # Derive engagement level from engagement score and churn probability
    q33 = clienti["Engagement_Score"].quantile(0.33)
    q67 = clienti["Engagement_Score"].quantile(0.67)

    def engagement_level(row) -> str:
        score = row["Engagement_Score"]
        churn = row["Churn_Probability"]
        if score >= q67 and churn < 0.33:
            return "Champion"
        elif score <= q33 or churn >= 0.67:
            return "At-Risk"
        return "Neutral"

    clienti["engagement_level"] = clienti.apply(engagement_level, axis=1)

    # Compute recency and urgency tier based on last visit
    clienti["Data_Ultima_Visita"] = pd.to_datetime(clienti["Data_Ultima_Visita"], errors="coerce")
    clienti["days_since_last_visit"] = (current_date - clienti["Data_Ultima_Visita"]).dt.days
    clienti["days_since_last_visit"] = clienti["days_since_last_visit"].fillna(9999)

    def urgency_tier(days: float) -> str:
        if days <= 90:
            return "CRITICAL"
        if days <= 180:
            return "HIGH"
        if days <= 365:
            return "MEDIUM"
        return "LOW"

    clienti["urgency_tier"] = clienti["days_since_last_visit"].apply(urgency_tier)

    # Strategic segment assignment
    def strategic_segment(row) -> str:
        val = row["value_segment"]
        life = row["life_stage"]
        prods = row["num_products"]
        eng = row["engagement_level"]
        investment_only = (
            row["investimento_owned"] == 1 and row["casa_owned"] == 0 and row["salute_owned"] == 0
        )
        if val == "Upper-Retail" and life == "Young Family" and prods <= 2:
            return "Affluent Young Families"
        if val == "Upper-Retail" and investment_only:
            return "Investment-Only Affluent"
        if val == "Upper-Retail" and eng == "At-Risk":
            return "At-Risk High Value"
        if val == "Upper-Retail" and prods >= 3:
            return "Premium Multi-Holders"
        return f"{val} {life}"

    clienti["strategic_segment"] = clienti.apply(strategic_segment, axis=1)

    # NBA recommendation based on product gaps and strategic segment
    def recommend_nba(row) -> str:
        seg = row["strategic_segment"]
        owned = {cat: row[f"{cat}_owned"] for cat in major_categories}
        missing = [cat for cat, owned_flag in owned.items() if owned_flag == 0]
        # Specific segment rules
        if seg == "Affluent Young Families":
            rec = []
            if "casa" in missing:
                rec.append("Casa")
            if "salute" in missing:
                rec.append("Salute")
            if not rec:
                for p in ["investimento", "pip"]:
                    if p in missing:
                        rec.append(p.capitalize())
            return "+".join(rec) if rec else "Retention"
        if seg == "Investment-Only Affluent":
            rec = []
            for p in ["casa", "salute", "pip"]:
                if p in missing:
                    rec.append(p.capitalize())
            return "+".join(rec) if rec else "Retention"
        if seg in ("At-Risk High Value", "Premium Multi-Holders"):
            return "Retention"
        return missing[0].capitalize() if missing else "Retention"

    clienti["nba_recommendation"] = clienti.apply(recommend_nba, axis=1)

    return clienti


def cluster_high_value_clients(clienti: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    """Cluster high-value clients (Upper-Retail, >1 product) and
    return the cluster-labelled DataFrame and a summary of cluster means.

    The function automatically selects the number of clusters using the
    silhouette score from k=2 to k=6.
    """
    high_val = clienti[
        (clienti["value_segment"] == "Upper-Retail") & (clienti["num_products"] > 1)
    ].copy()
    if high_val.empty:
        clienti["cluster"] = -1
        return clienti, pd.DataFrame()

    features = [
        "casa_owned",
        "salute_owned",
        "investimento_owned",
        "pip_owned",
        "Engagement_Score",
        "Churn_Probability",
        "Total_Wealth",
        "CLV_Stimato",
        "num_claims",
        "total_claim_amount",
        "num_complaints",
        "num_interactions",
        "conversion_rate",
        "avg_duration",
    ]
    X = high_val[features].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # determine best k
    best_k = 2
    best_score = -1
    max_k = min(6, len(high_val))
    for k in range(2, max_k + 1):
        km = KMeans(n_clusters=k, random_state=0, n_init=10)
        labels = km.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        if score > best_score:
            best_score, best_k = score, k
    km_final = KMeans(n_clusters=best_k, random_state=0, n_init=10)
    high_val["cluster"] = km_final.fit_predict(X_scaled)

    # Add cluster back to main dataset
    clienti = clienti.merge(
        high_val[["codice_cliente", "cluster"]], on="codice_cliente", how="left"
    )
    clienti["cluster"] = clienti["cluster"].fillna(-1).astype(int)

    # Compute summary statistics per cluster
    cluster_summary = high_val.groupby("cluster")[features].mean()
    return clienti, cluster_summary


def save_cluster_plot(high_val: pd.DataFrame, output_path: str) -> None:
    """Generate a PCA plot of clusters for high-value clients."""
    if high_val.empty or "cluster" not in high_val.columns:
        return
    features = [
        "casa_owned",
        "salute_owned",
        "investimento_owned",
        "pip_owned",
        "Engagement_Score",
        "Churn_Probability",
        "Total_Wealth",
        "CLV_Stimato",
        "num_claims",
        "total_claim_amount",
        "num_complaints",
        "num_interactions",
        "conversion_rate",
        "avg_duration",
    ]
    X = high_val[features].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    pca = PCA(n_components=2)
    comps = pca.fit_transform(X_scaled)
    plt.figure(figsize=(8, 6))
    for i in sorted(high_val["cluster"].unique()):
        idx = high_val["cluster"] == i
        plt.scatter(comps[idx, 0], comps[idx, 1], label=f"Cluster {i}", alpha=0.6)
    plt.title("Clusters of High-Value Clients (extended features)")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)


def synthetic_dynamic_nba(n: int = 200) -> pd.DataFrame:
    """Generate a synthetic dataset to demonstrate Dynamic NBA logic.

    The returned DataFrame has columns for value segment, age, life stage,
    products owned, event type, days since event, predicted transition,
    transition probability, urgency tier, NBA recommendation and an expected
    conversion estimate.  This function is purely illustrative.
    """
    # Basic assignments
    ids = np.arange(20000, 20000 + n)
    value_segments = np.random.choice(
        ["Upper-Retail", "Mid-Retail", "Entry-Retail"], size=n, p=[0.3, 0.5, 0.2]
    )
    ages = []
    for seg in value_segments:
        if seg == "Upper-Retail":
            ages.append(np.random.randint(30, 65))
        elif seg == "Mid-Retail":
            ages.append(np.random.randint(25, 60))
        else:
            ages.append(np.random.randint(20, 50))
    ages = np.array(ages)
    kids = np.random.poisson(1, size=n)
    # Life stage
    life_stage = []
    for age, k in zip(ages, kids):
        if age < 30:
            life_stage.append("Young Single" if k == 0 else "Young Family")
        elif age < 40:
            life_stage.append("Young Family" if k > 0 else "Young Professional")
        elif age < 55:
            life_stage.append("Established Family" if k > 0 else "Established Professional")
        elif age < 65:
            life_stage.append("Pre-Retirement")
        else:
            life_stage.append("Retired")
    life_stage = np.array(life_stage)
    # Product ownership
    categories = ["casa", "salute", "investimento", "pip"]
    num_prods = np.random.choice([1, 2, 3, 4], size=n, p=[0.3, 0.3, 0.25, 0.15])
    owned = {f"{cat}_owned": [] for cat in categories}
    for pcount in num_prods:
        selected = np.random.choice(categories, size=pcount, replace=False)
        for cat in categories:
            owned[f"{cat}_owned"].append(1 if cat in selected else 0)
    # Events
    events = np.random.choice(
        ["baby", "home_purchase", "marriage", "approaching_55", "none"],
        size=n,
        p=[0.15, 0.15, 0.15, 0.15, 0.4],
    )
    days_since = np.where(events == "none", np.nan, np.random.randint(0, 400, size=n))
    transitions = np.random.choice(
        [
            "Young Professional → Young Family",
            "Mid-Retail → Upper-Retail",
            "Young Family → Established Family",
            "None",
        ],
        size=n,
        p=[0.2, 0.15, 0.15, 0.5],
    )
    transition_prob = np.round(np.random.uniform(0.3, 0.9, size=n), 2)
    # Base conversion approximations and event uplift
    base_conv = []
    for seg, event, d in zip(value_segments, events, days_since):
        base = 0.25 if seg == "Upper-Retail" else 0.18 if seg == "Mid-Retail" else 0.10
        factor = 1.0
        if event == "baby":
            if not np.isnan(d) and d <= 90:
                factor = 2.0
            elif d <= 180:
                factor = 1.4
        elif event == "home_purchase":
            if not np.isnan(d) and d <= 180:
                factor = 1.8
            else:
                factor = 1.2
        elif event == "marriage":
            if not np.isnan(d) and d <= 180:
                factor = 1.5
        elif event == "approaching_55":
            if not np.isnan(d) and d <= 180:
                factor = 1.6
        base_conv.append(np.round(min(base * factor, 0.95), 2))
    # Compile DataFrame
    df = pd.DataFrame(
        {
            "codice_cliente": ids,
            "value_segment": value_segments,
            "age": ages,
            "kids": kids,
            "life_stage": life_stage,
            "event_type": events,
            "days_since_event": days_since,
            "predicted_transition": transitions,
            "transition_probability": transition_prob,
            "base_conversion": base_conv,
        }
    )
    for cat in categories:
        df[f"{cat}_owned"] = owned[f"{cat}_owned"]
    # Urgency tier and NBA
    urgency = []
    nba = []
    for _, row in df.iterrows():
        ev = row["event_type"]
        d = row["days_since_event"]
        # Determine urgency by event window
        if pd.isna(d):
            urgency.append("LOW")
        else:
            if ev == "baby":
                window = 90
            elif ev == "home_purchase":
                window = 180
            elif ev == "marriage":
                window = 180
            elif ev == "approaching_55":
                window = 180
            else:
                window = 180
            if d <= window / 2:
                urgency.append("CRITICAL")
            elif d <= window:
                urgency.append("HIGH")
            elif d <= 2 * window:
                urgency.append("MEDIUM")
            else:
                urgency.append("LOW")
        # Determine NBA recommendation
        missing = [cat for cat in categories if row[f"{cat}_owned"] == 0]
        if ev == "baby":
            recs = []
            if "casa" in missing:
                recs.append("Casa")
            if "salute" in missing:
                recs.append("Salute")
            nba.append("+".join(recs) if recs else "Retention")
        elif ev == "home_purchase":
            nba.append("Casa" if "casa" in missing else "Retention")
        elif ev == "marriage":
            recs = []
            if "casa" in missing:
                recs.append("Casa")
            if "salute" in missing:
                recs.append("Salute")
            if not recs and "pip" in missing:
                recs.append("PIP")
            nba.append("+".join(recs) if recs else "Retention")
        elif ev == "approaching_55":
            nba.append("PIP" if "pip" in missing else "Retention")
        else:
            nba.append(
                next(
                    (cat.capitalize() for cat in categories if row[f"{cat}_owned"] == 0),
                    "Retention",
                )
            )
    df["urgency_tier"] = urgency
    df["nba_recommendation"] = nba
    df["expected_conversion_rate"] = df["base_conversion"]
    return df


def generate_dynamic_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarise the synthetic dynamic NBA data by event type and urgency."""
    summary = (
        df.groupby(["event_type", "urgency_tier"])
        .agg(
            clients=("codice_cliente", "count"), avg_conversion=("expected_conversion_rate", "mean")
        )
        .reset_index()
    )
    return summary


def main() -> None:
    # 1. Load data
    data = load_data(DATA_DIR)

    # 2. Clean and engineer features
    clienti_enhanced = clean_and_engineer(data)

    # 3. Cluster high-value clients
    clienti_clustered, cluster_summary = cluster_high_value_clients(clienti_enhanced)

    # 4. Save outputs
    final_cols = [
        "codice_cliente",
        "value_segment",
        "life_stage",
        "num_products",
        "engagement_level",
        "strategic_segment",
        "nba_recommendation",
        "urgency_tier",
        "cluster",
        "num_claims",
        "total_claim_amount",
        "num_complaints",
        "num_interactions",
        "conversion_rate",
        "casa_owned",
        "salute_owned",
        "investimento_owned",
        "pip_owned",
    ]
    clienti_clustered[final_cols].to_csv(
        os.path.join(OUTPUT_DIR, "client_nba_enhanced.csv"), index=False
    )
    cluster_summary.to_csv(os.path.join(OUTPUT_DIR, "hv_cluster_summary.csv"))
    # Plot clusters for high value
    high_val = clienti_clustered[
        (clienti_clustered["value_segment"] == "Upper-Retail")
        & (clienti_clustered["num_products"] > 1)
    ]
    save_cluster_plot(high_val, os.path.join(OUTPUT_DIR, "hv_clusters_extended.png"))

    # 5. Generate synthetic dynamic NBA dataset
    synthetic_df = synthetic_dynamic_nba(n=200)
    synthetic_df.to_csv(os.path.join(OUTPUT_DIR, "dynamic_nba_artificial.csv"), index=False)
    summary = generate_dynamic_summary(synthetic_df)
    summary.to_csv(os.path.join(OUTPUT_DIR, "dynamic_nba_summary.csv"), index=False)
    # Plot summary
    pivot = summary.pivot(index="event_type", columns="urgency_tier", values="avg_conversion")
    pivot.plot(kind="bar", figsize=(10, 6))
    plt.title("Average expected conversion by event and urgency")
    plt.ylabel("Expected conversion rate")
    plt.xlabel("Event type")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "dynamic_nba_plot.png"))

    print("Processing complete. Files saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
