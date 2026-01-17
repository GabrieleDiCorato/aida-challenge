# AIDA Challenge

A data analytics project for exploring and extracting insights from insurance company data using modern data engineering tools.

## Project Overview

This project contains analytics pipelines for an insurance dataset, leveraging:

- **DuckDB** for efficient analytical queries
- **dbt** for data transformation and modeling
- **Streamlit** to create a P.o.C. interactive dashboard
- **Google Agent Development Kit** to orchestrate Ai agents
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
cp src/aida_challenge/dbt_project/profiles.yml.example src/aida_challenge/dbt_project/profiles.yml

# 2. Install dependencies
uv sync --all-extras

# 3. Load data into DuckDB
uv run load-raw-data

# 4. Run dbt transformations
uv run dbt-build

# 5. Run analytics pipeline (clustering + NBA enhancement)
uv run python -m aida_challenge.analytics.run_analytics_pipeline
```

> **📋 For complete analytics pipeline documentation**, see [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

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

The dashboard includes:
- **Data Exploration**: Interactive visualizations of customer demographics, policies, and geographic distribution
- **Sales Assistant**: AI-powered pitch generation with Next Best Action recommendations (see below)

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

### Sales Assistant with Next Best Action (NBA) Recommendations

The Sales Assistant uses AI to generate personalized sales pitches, integrated with a data-driven Next Best Action recommendation engine.

#### Setup

1. **Get an OpenRouter API Key** (free) from [OpenRouter](https://openrouter.ai/keys)

2. **Configure environment**:
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenRouter API key
OPENROUTER_API_KEY=your_key_here
```

3. **Generate document embeddings** (required once):
```bash
uv run embed-documents
```

4. **Run the complete dashboard** (recommended):
```bash
uv run streamlit-app
```

Then navigate to the **Sales Chatbot** page from the sidebar.

# Features

## Next Best Action Engine
- **Priority-Ordered Customer List**: Customers ranked by urgency (CRITICAL, HIGH, MEDIUM, LOW) and CLV
- **Smart Recommendations**: Product recommendations based on customer segmentation, gaps in portfolio, and conversion probability
- **Strategic Insights**: Shows pitch strategy (Ready to Pitch, Retention First, Nurture & Pitch, Monitor)
- **Portfolio Analysis**: Visual display of current product ownership and gap analysis
- **Conversion Rate Forecasts**: NBA-specific conversion rates for recommended products

## AI-Powered Pitch Generation
- **Customer 360° View**: Complete customer profile with demographics, policies, interactions, claims
- **Multi-Agent System**: Uses Google ADK with OpenRouter's **DeepSeek R1** (free) for intelligent pitch generation
- **RAG-Powered**: Retrieves relevant contract sections using vector similarity search (DuckDB VSS)
- **Structured Output**: Generates pitches with customer summary, selling points, objection handling, and next steps
- **Personalized Context**: Incorporates NBA insights and customer history into pitch generation

## How It Works

### NBA Recommendation Flow
1. The system loads pre-computed recommendations from `mart_nba_recommendations`
2. Customers are displayed in priority order based on:
   - **Urgency Level**: CRITICAL > HIGH > MEDIUM > LOW
   - **Customer Lifetime Value (CLV)**: Higher CLV customers prioritized within each urgency tier
3. Each recommendation includes:
   - Suggested product to pitch
   - Strategic pitch approach
   - Expected conversion rate
   - Current product portfolio gaps

### AI Pitch Generation
The system uses a sequential multi-agent workflow:
1. **Customer Analyst Agent** - Analyzes the customer profile to identify needs and opportunities
2. **RAG Agent** - Retrieves relevant product contract sections from embedded documents
3. **Pitch Generator Agent** - Creates a personalized sales pitch in Italian, incorporating NBA context

### Filters and Controls

The Sales Assistant provides:
- **Urgency Filter**: Focus on specific urgency levels
- **Strategy Filter**: Filter by pitch strategy type
- **Real-time Stats**: Customer count, conversion rates, and portfolio information
- **One-Click Generation**: Generate personalized pitches with a single button

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
