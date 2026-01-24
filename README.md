# AIDA Challenge

**⚠️ NOTE: This project was developed as part of a quick Hackathon/Challenge in a university setting. It is currently archived and no longer maintained.**

A data analytics project for exploring and extracting insights from insurance company data using modern data engineering tools.

## Project Overview

The goal of this project is to build a solution to a concrete business problem: assisting an insurance company's sales network in implementing data-driven business strategies.

We deliver this through:
- **Sales Assistant Dashboard**: A Streamlit-based tool for agents to manage customer relationships and generate AI-powered personalized pitches.
- **Next Best Action Engine**: A logic-driven recommendation system to prioritize customer outreach.
- **Executive Insights**: Strategical insights for monitoring network performance (provided via separate PowerBI).

## Business Features

### Next Best Action (NBA) Engine
- **Priority-Ordered Customer List**: Customers ranked by urgency (CRITICAL, HIGH, MEDIUM, LOW) and CLV.
- **Smart Recommendations**: Product suggestions based on customer segmentation, gaps in portfolio, and conversion probability.
- **Strategic Insights**: Shows pitch strategy (Ready to Pitch, Retention First, Nurture & Pitch, Monitor).
- **Portfolio Analysis**: Visual display of current product ownership and gap analysis.
- **Conversion Rate Forecasts**: NBA-specific conversion rates for recommended products.

### AI-Powered Pitch Generation (Sales Assistant)
- **Customer 360° View**: Complete customer profile with demographics, policies, interactions, and claims.
- **Multi-Agent System**: Sequential workflow using a Customer Analyst, RAG Agent, and Pitch Generator.
- **RAG-Powered**: Retrieves relevant contract sections from document embeddings for precise product information.
- **Structured Output**: Generates personalized pitches in Italian with selling points, objection handling, and next steps.

### Interactive Dashboard
- **Data Exploration**: Visualizations of customer demographics, policy distributions, and geographic trends.
- **Filters and Controls**: Focus on specific urgency levels, strategy types, and real-time portfolio stats.

## Technical Stack

This project leverages a modern data engineering and AI stack:

- **DuckDB**: Efficient analytical queries and Vector Similarity Search (VSS).
- **dbt**: Data transformation, modeling, and quality testing.
- **Streamlit**: Interactive user interface and dashboarding.
- **Google Agent Development Kit**: Orchestration of multi-agent AI workflows.
- **UV**: Fast Python dependency and environment management.
- **Jupyter**: Exploratory data analysis and prototyping.

## Quick Start

### Prerequisites

- **Python 3.12+**
- **UV package manager** ([installation guide](https://docs.astral.sh/uv/))

### Installation

```bash
# 1. Copy and configure dbt profiles
cp src/aida_challenge/dbt_project/profiles.yml.example src/aida_challenge/dbt_project/profiles.yml

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
cp src/aida_challenge/dbt_project/profiles.yml.example ~/.dbt/profiles.yml
# Edit ~/.dbt/profiles.yml and adjust paths as needed

# The dbt commands will automatically use ~/.dbt/profiles.yml
```

### Verify Installation
```bash
# Check dbt connection
uv run dbt-debug
```

### AI Features Setup
To use the AI-powered Sales Assistant:
1. **API Key**: Obtain an OpenRouter API key from [OpenRouter](https://openrouter.ai/keys).
2. **Environment**: Copy `.env.example` to `.env` and add your key: `OPENROUTER_API_KEY=your_key_here`.
3. **Embeddings**: Generate document embeddings (required once):
   ```bash
   uv run embed-documents
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

# Invoke the DuckDB UI to explore data in your browser
uv run explore-db
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

### Interactive Dashboard

Launch the Streamlit dashboard to explore data visualizations and use the AI-powered Sales Assistant:

```bash
# Launch the complete dashboard
uv run streamlit-app

# Or manually specify the app
uv run --extra dashboard streamlit run src/aida_challenge/streamlit_app/app.py
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
2. **Transform data** with dbt models (`src/aida_challenge/dbt_project/models/`)
3. **Test transformations** (`uv run dbt-test`)
4. **Document insights** and iterate

## Documentation

- **[src/aida_challenge/dbt_project/README.md](src/aida_challenge/dbt_project/README.md)** - dbt models documentation
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
- Static dataset: we were provided a static, synthetic dataset. No effort was made to prepare for ingesting new data or handling real-time updates.
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
