# AIDA Challenge

A data analytics project for exploring and extracting insights from insurance company data using modern data engineering tools.

## Project Overview

This repository contains exploratory data analysis and analytics pipelines for an insurance company dataset. The project leverages:

- **DuckDB** for efficient analytical queries on CSV data
- **dbt** for data transformation and modeling
- **UV** for fast Python dependency management
- **Jupyter** for exploratory data analysis

The goal is to explore the data, identify valuable insights, and build reproducible analytics pipelines as a proof of concept.

## Quick Start

### Prerequisites

- **Python 3.12+**
- **UV package manager** ([installation guide](https://docs.astral.sh/uv/))

### Installation

#### Option 1: One-Command Setup (Recommended)
```bash
make init
```
This will install dependencies, setup dbt, load data, and run the complete dbt pipeline.

#### Option 2: Step-by-Step Setup
```bash
# 1. Install dependencies
make install-all

# 2. Setup dbt
make dbt-setup

# 3. Load data into DuckDB
make load-data

# 4. Run dbt transformations
make dbt-pipeline
```

### Verify Installation
```bash
# Check dbt connection
make dbt-debug

# View all available commands
make help
```

## Usage

### Running dbt Transformations

```bash
# Run all models
make dbt-run

# Run specific layers
make dbt-staging        # Staging models only
make dbt-intermediate   # Intermediate models only
make dbt-marts          # Marts models only

# Test data quality
make dbt-test

# Complete pipeline (staging → intermediate → marts → test)
make dbt-pipeline

# Generate and view documentation
make dbt-docs
```

### Using UV Scripts

```bash
# dbt commands via UV
uv run dbt-run
uv run dbt-test
uv run dbt-build

# Model-specific runs
uv run dbt-run-staging
uv run dbt-run-marts
```

### Exploratory Analysis

```bash
# Start Jupyter Notebook
make notebook

# Or Jupyter Lab
make lab
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Run all checks
make check
```

## Development Workflow - data extraction

1. **Explore data** in Jupyter notebooks (`notebooks/exploratory/`)
2. **Transform data** with dbt models (`dbt_project/models/`)
3. **Test transformations** (`make dbt-test`)
4. **Document insights** and iterate

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Detailed setup and usage guide
- **[dbt_project/README.md](dbt_project/README.md)** - dbt models documentation
- **[docs/data_schema.md](docs/data_schema.md)** - Raw data schema reference

Generate and browse interactive dbt documentation:
```bash
make dbt-docs
```

## Testing

```bash
# Run Python tests
make test

# Run with coverage report
make test-coverage

# Run dbt tests
make dbt-test
```

## Maintenance

```bash
# Clean generated files
make clean

# Clean and rebuild everything
make rebuild

# Clean database (WARNING: deletes data!)
make clean-data
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

This is a group challenge project, and it's not open to exernal contributions. Suggestions and feedback are welcome! Feel free to:
- Open issues for bugs or questions
- Share ideas for data analysis approaches

## Contact

For questions or feedback about this project, please open an issue in this repository.

---
