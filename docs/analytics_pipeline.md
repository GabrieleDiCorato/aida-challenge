# Analytics Pipeline Architecture

## Overview

The analytics pipeline integrates Python-based machine learning (customer clustering, NBA recommendations) with dbt data transformations to create a unified, reproducible workflow. The pipeline follows a **full-refresh** pattern and uses **validation checkpoints** that block downstream processing on failures.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          RAW DATA (CSV)                             │
│  clienti, polizze, sinistri, reclami, abitazioni, interazioni      │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     DuckDB (data_loader.py)                         │
│          Loads CSVs into `main` schema tables                       │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    dbt STAGING MODELS                               │
│  • stg_clienti.sql - Customer master data                          │
│  • stg_polizze.sql - Insurance policies                            │
│  • stg_sinistri.sql - Claims                                       │
│  • ... (other raw data staging)                                    │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 dbt INTERMEDIATE MODELS                             │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  int_customer_wealth_segments.sql                             │ │
│  │    - Calculates total wealth (income + assets)                │ │
│  │    - Assigns value segments (Upper/Mid/Entry-Retail)          │ │
│  │    - Derives life stage (age + family composition)            │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  int_customer_product_ownership.sql                           │ │
│  │    - Creates binary flags for Casa/Salute/Investimento/PIP    │ │
│  │    - Counts product categories owned                          │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  int_customer_engagement_metrics.sql                          │ │
│  │    - Calculates days since last visit                         │ │
│  │    - Assigns urgency tiers (CRITICAL/HIGH/MEDIUM/LOW)         │ │
│  │    - Classifies engagement level (Champion/Neutral/At-Risk)   │ │
│  │    - Aggregates interactions, claims, complaints              │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  int_customer_strategic_segment.sql                           │ │
│  │    - Assigns strategic segments (Affluent Young Families, etc)│ │
│  │    - Generates base NBA recommendations                       │ │
│  │    - Combines all customer features for analytics            │ │
│  └───────────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PYTHON CLUSTERING (analysis_script.py)                 │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  1. Query int_customer_strategic_segment                      │ │
│  │  2. Filter: Upper-Retail customers with >1 product            │ │
│  │  3. K-means clustering (auto-select k via silhouette score)   │ │
│  │  4. Generate semantic labels (cluster_labeling.py)            │ │
│  │  5. Validate: silhouette > 0.2, cluster size >= 3             │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  Outputs to analytics schema:                                      │
│    • customer_clusters (codice_cliente, cluster, versione)         │
│    • cluster_metadata (cluster_id, etichetta, characteristics)     │
│    • cluster_summary (centroids for each cluster)                  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│          PYTHON NBA ENHANCEMENT (analysis_cluster_nba.py)           │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  1. Query int_customer_strategic_segment                      │ │
│  │  2. Merge cluster assignments                                 │ │
│  │  3. Assign single-product clients to clusters (affinity)      │ │
│  │  4. Generate cluster-aware NBA (ranked product list)          │ │
│  │  5. Adjust urgency by responsiveness (High_Responder +1)      │ │
│  │  6. Determine best contact channel (conversion rate)          │ │
│  │  7. Validate: no empty results, channel coverage              │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  Outputs to analytics schema:                                      │
│    • nba_enhanced (NBA + cluster + urgency + channel)              │
│    • cluster_product_mix (product preferences by cluster)          │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│              dbt STAGING (Analytics Outputs)                        │
│  • stg_customer_clusters.sql - Latest cluster assignments         │
│  • stg_cluster_metadata.sql - Semantic labels & characteristics   │
│  • stg_nba_enhanced.sql - Enhanced NBA recommendations            │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     dbt MARTS (Final Tables)                        │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  mart_nba_recommendations.sql                                 │ │
│  │    - Joins customer data + strategic segment + clusters       │ │
│  │    - Includes NBA recommendations, urgency, channel           │ │
│  │    - Adds cluster labels and descriptions                     │ │
│  │    - Computes pitch strategy and readiness scores             │ │
│  │    - Cached pitch texts from LLM                              │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  • dim_customers.sql - Customer dimension with all metrics         │
│  • fact_policies.sql - Policy transactions                         │
│  • dim_competitive_intelligence.sql - Competitor analysis          │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  STREAMLIT APPLICATION                              │
│  • Sales Assistant - NBA pitch generation interface                │
│  • Data Visualization - Interactive dashboards                     │
│  • Uses utils/data_loader.py to query marts                        │
└─────────────────────────────────────────────────────────────────────┘
```

## Pipeline Execution

### Manual Execution

```bash
# Option 1: Full pipeline orchestration
uv run python -m aida_challenge.analytics.run_analytics_pipeline

# Option 2: Step-by-step execution
uv run python -m aida_challenge.data_loader  # Load raw CSVs
uv run dbt-run --select intermediate         # Feature engineering
uv run python -m aida_challenge.analytics.analysis_script  # Clustering
uv run python -m aida_challenge.analytics.analysis_cluster_nba  # NBA
uv run dbt-run --select marts                # Final tables
```

### Automatic Execution

The pipeline is triggered automatically when:
- Running `data_loader.py --run-analytics` flag (if implemented)
- Scheduled via cron/task scheduler for regular refreshes

## Data Flow Details

### 1. Feature Engineering (dbt Intermediate)

All feature engineering previously done in Python has been moved to SQL:

- **Wealth calculation**: `reddito + patrimonio_finanziario + patrimonio_reale`
- **Value segmentation**: Quartile-based (Q25/Q75) classification
- **Life stage derivation**: Age + children logic (7 categories)
- **Product ownership**: Binary flags from `polizze.area_di_bisogno` parsing
- **Engagement classification**: Quantile-based (Q33/Q67) + churn threshold
- **Urgency tiers**: Days since last visit thresholds (90/180/365)

**Benefits**:
- Testable with dbt tests (range checks, accepted values)
- Version controlled in Git
- Reusable across multiple downstream models
- No data movement to Python (query in-place)

### 2. Clustering Logic (Python)

**Input**: `int_customer_strategic_segment` (all customers with features)

**Filter**: `segmento_valore = 'Upper-Retail' AND num_prodotti_posseduti > 1`

**Algorithm**: K-means with automatic k selection:
- Tests k=2 to k=min(6, customers/3)
- Selects k with highest silhouette score
- Requires silhouette > 0.2 (validation checkpoint)

**Features used** (12):
- `possiede_casa`, `possiede_salute`, `possiede_investimento`, `possiede_pip`
- `engagement_score`, `churn_probability`
- `patrimonio_totale`, `clv_stimato`
- `num_sinistri`, `num_reclami`, `num_interazioni`, `tasso_conversione`

**Semantic labeling** (automatic):
1. Value level: Based on `patrimonio_totale` thresholds (High/Mid/Entry)
2. Product profile: Based on ownership proportions (Multi-Product, Investment-Focused, etc.)
3. Engagement: Based on `churn_probability` and `engagement_score`

Example labels:
- "High-Value Multi-Product Champions"
- "Mid-Value Investment-Focused At-Risk"
- "High-Value Casa-Core Low-Engagement"

**Manual overrides**: Stored in `data/analytics/cluster_labels.json` by version

### 3. NBA Enhancement (Python)

**Cluster assignment for single-product clients**:
- Identify Upper-Retail with exactly 1 product
- Find cluster with highest ownership of that product
- Tie-break by cluster's average wealth

**Cluster-aware NBA**:
- Each cluster has ranked product list (by ownership proportion)
- NBA = first missing product in cluster's ranked list
- Non-Upper-Retail keep base NBA from dbt model

**Urgency adjustment**:
- If `cluster_risposta = 'High_Responder'` AND NBA != 'Retention'
- Bump urgency one level: LOW→MEDIUM, MEDIUM→HIGH, HIGH→CRITICAL

**Best channel**:
- Group interactions by customer + channel type
- Calculate conversion rate per channel
- Choose channel with max conversion rate
- Tie-break: most frequent channel
- Default: 'N/A' if no interactions

## Validation & Error Handling

### Validation Checkpoints

All validations **block downstream processing** on failure:

1. **dbt intermediate models** (Step 2/7)
   - Tests: `accepted_values`, `accepted_range`, `expression_is_true`
   - Example: `segmento_valore IN ('Upper-Retail', 'Mid-Retail', 'Entry-Retail')`
   - Failures: Raise error, log to `pipeline_errors.log`, exit code 1

2. **Clustering validation** (Step 4/7)
   - Silhouette score >= 0.2
   - Minimum cluster size >= 3 customers
   - At least 10 customers in filtered set
   - Failures: Raise `ValueError`, log traceback, exit code 1

3. **NBA enhancement validation** (Step 5/7)
   - No empty DataFrames
   - All customers have cluster assignment or -1
   - Channel determination completed
   - Failures: Raise `ValueError`, log traceback, exit code 1

4. **dbt marts** (Step 7/7)
   - All data quality tests must pass
   - Referential integrity checks
   - Range validations
   - Failures: Raise `RuntimeError`, exit code 1

### Error Logging

All errors logged to: `data/analytics/pipeline_errors.log`

Format:
```
======================================================================
[2026-01-16 14:23:45] PIPELINE ERROR
======================================================================
dbt intermediate tests failed with code 1
Traceback (most recent call last):
  ...
======================================================================
```

### Recovery from Failures

1. **Review error log**: Check `pipeline_errors.log` for details
2. **Fix root cause**: Update SQL/Python code or fix data issues
3. **Partial re-run**: Use dbt select to rebuild specific models
4. **Full re-run**: Execute `run_analytics_pipeline.py` again

## Output Tables

### Analytics Schema (`analytics.*`)

Written by Python scripts:

| Table | Description | Rows | Refresh |
|-------|-------------|------|---------|
| `customer_clusters` | Cluster assignments | ~11,200 | Full |
| `cluster_metadata` | Semantic labels + characteristics | ~3-6 | Full |
| `cluster_summary` | Cluster centroids | ~3-6 | Full |
| `nba_enhanced` | Enhanced NBA with clusters | ~11,200 | Full |
| `cluster_product_mix` | Product ownership by cluster | ~3-6 | Full |

### Marts Schema (`main_marts.*`)

Built by dbt:

| Table | Description | Rows | Refresh |
|-------|-------------|------|---------|
| `mart_nba_recommendations` | Final NBA table with all enrichments | ~11,200 | Full |
| `dim_customers` | Customer dimension | ~11,200 | Full |
| `fact_policies` | Policy fact table | ~18,000 | Full |

## Model Versioning

**Version format**: `vYYYYMM` (e.g., `v202601` for January 2026)

**Version tracking**:
- All analytics outputs include `versione_modello` column
- Staging models select latest version automatically
- Historical versions retained in database for audit
- Manual cluster labels versioned in `cluster_labels.json`

**Cluster stability**:
- Semantic labels make clusters interpretable across versions
- Cluster IDs may change between runs (K-means is not deterministic)
- Use `etichetta_cluster` for business interpretation
- Future enhancement: Store cluster centroid mappings for version comparison

## Performance Considerations

- **Current dataset**: ~11,200 customers, sub-minute execution
- **Clustering**: O(n*k*i) where n=customers, k=clusters, i=iterations
  - Current: ~500 customers × 4 clusters × 10 iterations = fast
  - Scales to 100K customers with no code changes
- **dbt models**: Materialized as views (fast) or tables (marts only)
- **Full refresh**: Acceptable for static dataset, no incremental logic needed

## Future Enhancements

### Cluster Management Dashboard

Allow data scientists to:
- View cluster characteristics and centroids
- Manually rename clusters (save to `cluster_labels.json`)
- Compare cluster stability across versions
- Export cluster assignments for further analysis

### Event-Driven NBA

Extension beyond current implementation:
- Detect life events (baby, home purchase, marriage)
- Trigger time-sensitive NBA recommendations
- Adjust urgency based on event proximity
- (Synthetic data generator removed, see `analysis_script.py.old`)

### Incremental Processing

If dataset becomes dynamic:
- Track new customers since last run
- Assign to existing clusters (nearest centroid)
- Periodic full retraining (monthly)
- Update only changed customers in marts

## Troubleshooting

### "Database not found" error
```bash
uv run python -m aida_challenge.data_loader
```

### "dbt models don't exist" error
```bash
uv run dbt-build
```

### "Silhouette score too low" error
- Clustering quality poor (data doesn't have clear structure)
- Review cluster features, may need different segmentation approach
- Check if enough high-value multi-product customers exist

### "Test failures" in dbt
- Review `dbt_project/logs/` for specific test failures
- Common issues: data quality problems, referential integrity breaks
- Fix upstream data or adjust test thresholds

### "Empty DataFrame" errors
- Usually indicates missing upstream data
- Check analytics schema tables exist
- Verify dbt intermediate models built successfully

## Running the Pipeline

**Recommended workflow**:

```bash
# 1. Ensure database is loaded
uv run python -m aida_challenge.data_loader

# 2. Build dbt models (first time or after schema changes)
uv run dbt-build

# 3. Run analytics pipeline
uv run python -m aida_challenge.analytics.run_analytics_pipeline

# 4. Verify results in Streamlit
uv run streamlit run src/aida_challenge/streamlit_app/app.py
```

**Development workflow**:

```bash
# Test single script
uv run python -m aida_challenge.analytics.analysis_script

# Test specific dbt model
uv run dbt-run --select int_customer_strategic_segment

# Run only marts
uv run dbt-run --select marts
```
