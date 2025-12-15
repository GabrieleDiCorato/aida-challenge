# AIDA Challenge - Quick Start Guide

## Prerequisites

- Python 3.12+
- UV package manager installed

## Installation

### Option 1: Quick Setup (Recommended)
```bash
make init
```
This will:
- Install all dependencies
- Setup dbt
- Load data into DuckDB
- Run the complete dbt pipeline

### Option 2: Step-by-Step
```bash
# Install dependencies
make install-all

# Setup dbt
make dbt-setup

# Load data
make load-data

# Run dbt pipeline
make dbt-pipeline
```

## Common Commands

### UV Scripts
```bash
# dbt commands via UV
uv run dbt-debug          # Test dbt connection
uv run dbt-run            # Run all models
uv run dbt-test           # Test all models
uv run dbt-build          # Build and test
uv run dbt-docs-generate  # Generate docs

# Model-specific
uv run dbt-run-staging       # Run staging only
uv run dbt-run-intermediate  # Run intermediate only
uv run dbt-run-marts         # Run marts only
uv run dbt-test-sources      # Test sources

# Workflows
uv run dbt-setup         # Debug + install deps
uv run dbt-full-refresh  # Full refresh + test
```

### Makefile Commands
```bash
# View all available commands
make help

# Environment setup
make install             # Install base dependencies
make install-all         # Install all including optional
make install-analysis    # Install Jupyter, matplotlib, etc.

# dbt operations
make dbt-run             # Run all models
make dbt-test            # Test all models
make dbt-build           # Build and test
make dbt-staging         # Run staging models
make dbt-marts           # Run marts models
make dbt-pipeline        # Run complete pipeline
make dbt-docs            # Generate and serve docs

# Jupyter
make notebook            # Start Jupyter notebook
make lab                 # Start Jupyter Lab

# Code quality
make format              # Format with black
make lint                # Lint with ruff
make check               # Run all checks

# Testing
make test                # Run Python tests
make test-coverage       # Run with coverage

# Cleaning
make clean               # Clean generated files
make clean-data          # Delete DuckDB database
make rebuild             # Clean and rebuild everything
```

## Project Workflow

### 1. Data Loading
```bash
# Option A: Via Jupyter notebook
make notebook
# Then run: notebooks/exploratory/00_data_loading.ipynb

# Option B: Automated
make load-data
```

### 2. Run dbt Pipeline
```bash
# Complete pipeline
make dbt-pipeline

# Or step by step
make dbt-staging
make dbt-intermediate
make dbt-marts
make dbt-test
```

### 3. View Documentation
```bash
make dbt-docs
```

### 4. Explore Data
```bash
make notebook
# Or
make lab
```

## dbt Models

### Staging Layer
- `stg_clienti` - Customer data
- `stg_polizze` - Policies
- `stg_sinistri` - Claims
- `stg_reclami` - Complaints
- `stg_abitazioni` - Housing
- `stg_interazioni_clienti` - Interactions
- `stg_competitor_prodotti` - Competitors

### Intermediate Layer
- `int_customer_policies` - Policy aggregations
- `int_customer_interactions` - Interaction metrics
- `int_customer_claims` - Claims analysis

### Marts Layer
- `dim_customers` - Customer dimension with segmentation
- `fact_policies` - Policy fact table
- `mart_competitor_analysis` - Competitive analysis

## Tips

### Quick Development Cycle
```bash
# Edit a model
vim dbt_project/models/marts/dim_customers.sql

# Run just that model
uv run dbt run --select dim_customers --project-dir dbt_project --profiles-dir dbt_project

# Or use make
cd dbt_project && dbt run --select dim_customers
```

### Debug Issues
```bash
# Check dbt connection
make dbt-debug

# View logs
cat dbt_project/logs/dbt.log

# Run with verbose output
cd dbt_project && dbt run --select dim_customers --debug
```

### Fresh Start
```bash
# Clean and rebuild everything
make rebuild

# Or completely from scratch
make clean-data
make init
```

## Environment Variables

You can customize the dbt profile by setting:
```bash
export DBT_PROFILES_DIR=./dbt_project
export DBT_PROJECT_DIR=./dbt_project
```

## Troubleshooting

### dbt can't find database
```bash
# Ensure data is loaded
make load-data

# Check database exists
ls -lh data/aida_challenge.duckdb
```

### UV command not found
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Import errors
```bash
# Sync dependencies
uv sync --all-extras
```

## Next Steps

1. Explore notebooks in `notebooks/exploratory/`
2. Review dbt models in `dbt_project/models/`
3. Check data documentation: `make dbt-docs`
4. Start analysis in Jupyter: `make notebook`
