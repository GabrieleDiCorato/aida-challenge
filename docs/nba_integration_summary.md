# NBA Recommendations Integration - Summary

## Overview
Successfully integrated the `client_nba_enhanced.csv` file into the dbt project to enable pitch next best action recommendations.

## What Was Done

### 1. Data Source Configuration
- **Added new source**: Created `analytics` source in `_sources.yml` pointing to `client_nba_enhanced.csv`
- **Updated data loader**: Modified `data_loader.py` to include the analytics CSV file
- **Loaded data**: Successfully loaded 11,200 customer NBA records into DuckDB

### 2. Staging Model Created
**File**: `models/staging/stg_client_nba_enhanced.sql`
- **Purpose**: Clean and transform NBA data, excluding duplicated columns
- **Columns Retained** (non-duplicated, translated to Italian):
  - `codice_cliente` - Customer identifier (primary key)
  - `segmento_strategico` - Strategic customer segment (was: strategic_segment)
  - `raccomandazione_nba` - Next Best Action recommendation (was: nba_recommendation)
  - `livello_urgenza` - Urgency level: LOW, MEDIUM, HIGH, CRITICAL (was: urgency_tier)
  - `cluster` - Customer cluster assignment
  - `tasso_conversione_nba` - Historical conversion rate (was: conversion_rate)
  - `possiede_casa`, `possiede_salute`, `possiede_investimento`, `possiede_pip` - Product ownership flags (were: casa_owned, salute_owned, investimento_owned, pip_owned)

- **Columns Excluded** (duplicated from other sources):
  - `value_segment`, `life_stage`, `num_products`, `engagement_level` - Available in `dim_customers`
  - `num_claims`, `total_claim_amount` - Available in `int_customer_claims`
  - `num_complaints`, `num_interactions` - Available in `int_customer_interactions`

**Note**: All column names follow the Italian naming convention used consistently throughout the project.

### 3. Mart Model Created
**File**: `models/marts/mart_nba_recommendations.sql`
- **Purpose**: Final table for pitch next best actions combining customer data with NBA analysis
- **Features**:punteggio_urgenza` (1-4 based on urgency tier) - was: urgency_score
  - Derives `strategia_pitch` based on urgency, churn risk, and engagement - was: pitch_strategy
  - Computes `gap_prodotti` (number of key products not owned) - was: product_gap_count
  - Ordered by urgency and customer lifetime value
  - **All column names use Italian naming convention** for consistency with other martsrn risk, and engagement
  - Computes `product_gap_count` (number of key products not owned)
  - Ordered by urgency and customer lifetime value

### 4. Data Quality Tests
- **Staging model**: 17 tests passed ✓
  - Not null validations on all key fields
  - Accepted values for binary flags (0, 1)
  - Accepted values for urgency tier
  - Range validation for conversion_rate (0-1)
  - Referential integrity with customers table

- **Mart model**: 17 tests passed ✓
  - Uniqueness on codice_cliente
  - All staging tests plus mart-specific validations
  - Product gap count range (0-4)
  - Pitch strategy accepted values

### 5. Documentation
- Updated `_staging.yml` with full column documentation and tests
- Updated `_marts.yml` with comprehensive mart documentation
- Generated dbt documentation catalog

## Results Summary

### Total Records: 11,200 customers

### Urgency Distribution:
- CRITICAL: 2,363 (21.1%)
- HIGH: 1,910 (17.0%)
- MEDIUM: 1,795 (16.0%)
- LOW: 5,132 (45.8%)

### Pitch Strategy Distribution:
- Monitor: 5,821 (52.0%)
- Ready to Pitch: 3,985 (35.6%)
- Nurture & Pitch: 1,371 (12.2%)
- Retention First: 23 (0.2%)

### Top NBA Recommendations:
- Casa: 8,986 (80.2%)
- Casa+Salute+Pip: 1,669 (14.9%)
- Retention: 358 (3.2%)
- Casa+Salute: 187 (1.7%)

## Usage

### Query the NBA Recommendations
```sql
SELECT *
FROM mlivello_urgenza IN ('CRITICAL', 'HIGH')
  AND strategia_pitch = 'Ready to Pitch'
ORDER BY punteggio_urgenza DESC, clv_stimato DESC;
```

### High-Priority Customers for Immediate Action
```sql
SELECT
    codice_cliente,
    nome,
    cognome,
    raccomandazione_nba,
    livello_urgenza,
    clv_stimato,
    gap_prodotti
FROM main_marts.mart_nba_recommendations
WHERE strategia_pitch = 'Ready to Pitch'
  AND livello_urgenza = 'CRITICAL'
ORDER BY clv_stimato DESC
LIMIT 100;
```

### Column Name Translation Reference
For reference, here's the mapping from the original English CSV columns to the Italian column names used in the mart:

| Original CSV Column | Italian Column Name | Description |
|---------------------|---------------------|-------------|
| strategic_segment | segmento_strategico | Strategic customer segment |
| nba_recommendation | raccomandazione_nba | Next Best Action recommendation |
| urgency_tier | livello_urgenza | Urgency level (LOW/MEDIUM/HIGH/CRITICAL) |
| conversion_rate | tasso_conversione_nba | Historical conversion rate |
| casa_owned | possiede_casa | Home insurance ownership flag |
| salute_owned | possiede_salute | Health insurance ownership flag |
| investimento_owned | possiede_investimento | Investment product ownership flag |
| pip_owned | possiede_pip | Pension product ownership flag |
| N/A (calculated) | punteggio_urgenza | Urgency score (1-4) |
| N/A (calculated) | strategia_pitch | Pitch strategy |
| N/A (calculated) | gap_prodotti | Product gap count |IT 100;
```

## Files Modified/Created

### Created:
- `dbt_project/models/staging/stg_client_nba_enhanced.sql`
- `dbt_project/models/marts/mart_nba_recommendations.sql`

### Modified:
- `dbt_project/models/staging/_sources.yml` - Added analytics source
- `dbt_project/models/staging/_staging.yml` - Added staging documentation
- `dbt_project/models/marts/_marts.yml` - Added mart documentation
- `src/aida_challenge/data_loader.py` - Added client_nba_enhanced to data loading

## Next Steps

1. **Build downstream reports**: Create visualizations and dashboards using the mart
2. **Integrate with CRM**: Export high-priority recommendations for sales teams
3. **Monitor conversion**: Track actual vs predicted conversion rates
4. **Refresh schedule**: Set up regular NBA data updates from external analysis
