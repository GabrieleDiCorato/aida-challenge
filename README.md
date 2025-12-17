# AIDA Challenge

A data analytics project for exploring and extracting insights from insurance company data using modern data engineering tools.

## Project Overview

This project contains analytics pipelines for an insurance dataset, leveraging:

- **DuckDB** for efficient analytical queries
- **dbt** for data transformation and modeling
- **UV** for fast Python dependency management
- **Jupyter** for exploratory data analysis

The goal is to explore data, identify insights, and build reproducible pipelines.

## Quick Start

### Prerequisites

- **Python 3.12+**
- **UV package manager** ([installation guide](https://docs.astral.sh/uv/))

### Installation

```bash
# 1. Copy and configure dbt profiles
cp dbt_project/profiles.yml.example dbt_project/profiles.yml

# 2. Install dependencies
uv sync --all-extras

# 3. Load data into DuckDB
uv run load-raw-data

# 4. Run dbt transformations
uv run dbt-build
```

#### Alternative: Standard dbt Profiles Location
For a more production-ready setup, you can use the standard dbt profiles location:
```bash
# Copy profiles to ~/.dbt/ directory
mkdir -p ~/.dbt
cp dbt_project/profiles.yml.example ~/.dbt/profiles.yml
# Edit ~/.dbt/profiles.yml and adjust paths as needed

# The dbt commands will automatically use ~/.dbt/profiles.yml
```

### Verify Installation
```bash
# Check dbt connection
uv run dbt-debug
```

### Dependency Management

Choose the installation profile that matches your needs:

```bash
# Install everything (Recommended)
uv sync --all-extras

# Install specific components
uv sync --extra analysis    # For Jupyter notebooks & analysis
uv sync --extra dashboard   # For Streamlit dashboard
uv sync --extra dev         # For development (linting, testing)
```

## Usage

### Running dbt Transformations

```bash
# Run all models
uv run dbt-run

# Run specific layers
uv run dbt-run --select staging        # Staging models only
uv run dbt-run --select intermediate   # Intermediate models only
uv run dbt-run --select marts          # Marts models only

# Test data quality
uv run dbt-test

# Complete pipeline (build and test all models)
uv run dbt-build

# Generate and view documentation
uv run dbt-docs-generate
uv run dbt-docs-serve
```

### Exploratory Analysis

Launch Jupyter for interactive analysis:
```bash
# Start Jupyter Notebook
uv run --extra analysis jupyter notebook

# Or Jupyter Lab
uv run --extra analysis jupyter lab
```

Explore the database directly using DuckDB UI:
```bash
uv run explore-db
```

### Code Quality

```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Type check
uv run mypy src

# Run tests
uv run pytest
```

## Development Workflow

1. **Explore data** in Jupyter notebooks (`notebooks/exploratory/`) or DuckDB UI (`uv run explore-db`)
2. **Transform data** with dbt models (`dbt_project/models/`)
3. **Test transformations** (`uv run dbt-test`)
4. **Document insights** and iterate

## Documentation

- **[dbt_project/README.md](dbt_project/README.md)** - dbt models documentation
- **[docs/data_schema.md](docs/data_schema.md)** - Raw data schema reference

Generate and browse interactive dbt documentation:
```bash
uv run dbt-docs-generate
uv run dbt-docs-serve
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

**This is a learning and proof-of-concept project.**

This repository contains exploratory code developed for educational purposes and as a proof of concept for data analytics workflows. It is **not production-ready** and should not be used in production environments without significant review, testing, and hardening.

Key limitations:
- Code may not follow all production best practices
- Limited error handling and edge case coverage
- Data quality checks are illustrative, not comprehensive
- Performance optimization has not been a primary focus
- Security considerations are minimal

Use this code as a reference or starting point for learning, but conduct thorough review and testing before adapting it for production use cases.

## Contributing

This is a group challenge project, and it's not open to external contributions. Suggestions and feedback are welcome! Feel free to:
- Open issues for bugs or questions
- Share ideas for data analysis approaches

## Contact

For questions or feedback about this project, please open an issue in this repository.

---
