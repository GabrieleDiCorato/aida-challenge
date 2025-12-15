# AIDA Insurance dbt Project

This dbt project transforms raw insurance data into analytics-ready models for customer segmentation, policy analysis, and competitive benchmarking.

## Project Structure

```
dbt_project/
├── models/
│   ├── staging/           # Clean & standardize raw data
│   │   ├── _sources.yml   # Source definitions
│   │   ├── stg_clienti.sql
│   │   ├── stg_polizze.sql
│   │   ├── stg_sinistri.sql
│   │   ├── stg_reclami.sql
│   │   ├── stg_abitazioni.sql
│   │   ├── stg_interazioni_clienti.sql
│   │   └── stg_competitor_prodotti.sql
│   ├── intermediate/      # Business logic transformations
│   │   ├── int_customer_policies.sql
│   │   ├── int_customer_interactions.sql
│   │   └── int_customer_claims.sql
│   └── marts/            # Final analytics tables
│       ├── dim_customers.sql
│       ├── fact_policies.sql
│       └── mart_competitor_analysis.sql
└── schema.yml           # Tests and documentation
```

## Models

### Staging Layer (`staging/`)
Cleans and standardizes raw data with consistent naming conventions:
- Removes Italian special characters from column names
- Filters null values where appropriate
- Maintains 1:1 relationship with source data

### Intermediate Layer (`intermediate/`)
Aggregates and joins data for specific business contexts:
- **int_customer_policies**: Customer policy portfolio aggregations
- **int_customer_interactions**: Customer interaction patterns and metrics
- **int_customer_claims**: Claims history and frequency analysis

### Marts Layer (`marts/`)
Final analytics-ready tables:
- **dim_customers**: Complete customer profiles with segmentation
- **fact_policies**: Policy-level details with customer context
- **mart_competitor_analysis**: Competitive benchmarking analysis

## Setup & Run

### Configure Connection
The `profiles.yaml` is already configured to use:
- Database: `../data/aida_challenge.duckdb`
- Schema: `main`

### Run Commands

```bash
# Navigate to dbt project
cd dbt_project

# Test source data
dbt test --select source:*

# Build staging models
dbt run --select staging

# Build all models
dbt run

# Run all tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

### Incremental Workflow
```bash
# Build specific model and downstream dependencies
dbt run --select stg_clienti+

# Build specific model only
dbt run --select stg_clienti

# Test specific model
dbt test --select stg_clienti

# Build marts only
dbt run --select marts
```

## Key Features

### Customer Segmentation
The `dim_customers` model includes automatic segmentation:
- **Premium Loyal**: High CLV, low churn risk
- **Premium At Risk**: High CLV, high churn risk
- **High Churn Risk**: Any customer with >70% churn probability
- **Growth Opportunity**: High growth potential
- **Inactive**: No active policies
- **Standard**: All others

### Risk Classification
Claims-based risk classification:
- **No Claims**: Zero claims history
- **Low Risk**: < 0.5 claims per year
- **Medium Risk**: 0.5-1.5 claims per year
- **High Risk**: > 1.5 claims per year

### Value Classification
Based on annual premium:
- **High Value**: > €5,000/year
- **Medium Value**: €2,000-€5,000/year
- **Low Value**: < €2,000/year

## Data Quality Tests

Tests are defined in `models/schema.yml` and `models/staging/_sources.yml`:

- **Uniqueness**: Primary keys (codice_cliente)
- **Not Null**: Critical fields
- **Referential Integrity**: Foreign keys to parent tables
- **Value Ranges**: Scores, probabilities, ages
- **Accepted Values**: Categorical fields

## Next Steps

1. **Add more tests**: Enhance data quality checks
2. **Create incremental models**: For large fact tables
3. **Add macros**: Reusable transformations
4. **Snapshots**: Track slowly changing dimensions
5. **Custom analyses**: Business-specific queries in `analyses/`
