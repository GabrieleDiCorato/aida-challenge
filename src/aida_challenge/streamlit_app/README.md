# AIDA Challenge - Interactive Dashboard

## Overview

This Streamlit dashboard provides interactive data visualizations and analytics for the AIDA Challenge insurance dataset, plus an AI-powered Sales Assistant with Next Best Action recommendations.

## Features

### Main Dashboard - 8 Interactive Tabs:

1. **Demographics** - Customer age, income, and profession distributions
2. **Portfolio** - Policy analysis and premium distributions by product/need area
3. **Customer Value** - CLV, engagement scores, and churn probability analysis
4. **Geography** - Interactive map showing customer locations and regional CLV
5. **Products** - Product performance, profitability, and loss ratios
6. **Lifecycle** - Customer retention, tenure, and lifecycle stage analysis
7. **Channels** - Acquisition channel performance and conversion rates
8. **Segmentation** - Deep dive into customer clusters and characteristics

### Sales Assistant (Separate Page)

- **Next Best Action Engine**: Priority-ordered customer list with product recommendations
- **AI Pitch Generation**: Personalized sales pitches using multi-agent AI system
- **Customer 360°**: Complete customer profiles with history, interactions, and claims
- **Smart Filtering**: Filter by urgency level and pitch strategy
- **RAG-Powered**: Contract information retrieval using vector similarity search

### Interactive Features:

- **Sidebar Filters**: Filter by customer cluster, age range, and income range
- **Real-time Metrics**: Key performance indicators update based on filters
- **Hover Details**: Interactive charts with detailed information on hover
- **Drill-down Analysis**: Explore data at multiple levels of granularity

## Installation

### 1. Install Dependencies

```bash
# Install dashboard dependencies
uv sync --extra dashboard

# Or install all optional dependencies
uv sync --all-groups
```

### 2. Ensure Data is Available

Make sure the DuckDB database exists at:
```
data/aida_challenge.duckdb
```

If not, run the data loading scripts first:
```bash
uv run load-raw-data
```

## Running the Dashboard

### Recommended: Using UV Script

```bash
# Launch the complete dashboard (easiest method)
uv run streamlit-app
```

### Alternative Options:

#### Option 1: Direct Streamlit Command

```bash
uv run --extra dashboard streamlit run src/aida_challenge/streamlit_app/app.py
```

#### Option 2: From streamlit_app Directory

```bash
cd src/aida_challenge/streamlit_app
uv run streamlit run app.py
```

#### Option 3: Using Activated Virtual Environment

```bash
# First activate the environment
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Then run streamlit
streamlit run src/aida_challenge/streamlit_app/app.py
```

**Note:** Make sure to run from the project root directory (`aida-challenge`) to ensure the database path is resolved correctly.

The dashboard will automatically open in your default browser at `http://localhost:8501`

## Using the Dashboard

### Main Dashboard

#### Filters (Sidebar)

- **Customer Cluster**: Filter by specific customer segments
- **Age Range**: Select age range using the slider
- **Income Range**: Select income range using the slider

All visualizations and metrics update automatically based on your filter selections.

#### Navigation

Use the tabs at the top to switch between different analysis views:
- Click on any tab to view specific insights
- All tabs respect the filters set in the sidebar
- Charts are interactive - hover for details, zoom, pan, etc.

### Sales Assistant

Access the **Sales Chatbot** page from the sidebar navigation:

1. **Priority List (Sidebar)**:
   - View customers ordered by urgency and CLV
   - Apply filters for urgency level and pitch strategy
   - Select a customer to view details

2. **Customer Details (Left Panel)**:
   - NBA context: urgency, strategy, conversion rate
   - Product portfolio and gaps
   - Complete customer profile

3. **Pitch Generation (Right Panel)**:
   - Click "Generate Pitch" to create a personalized sales pitch
   - View structured pitch with selling points, objection handling, and next steps
   - Pitches are generated using AI with customer-specific context

#### Prerequisites for Sales Assistant

Before using the Sales Assistant:
1. Set up OpenRouter API key in `.env` file
2. Run `uv run embed-documents` to generate document embeddings
3. Ensure dbt models have been built (`uv run dbt-build`)

## Technologies Used

- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **DuckDB**: High-performance analytics database
- **Pandas**: Data manipulation and analysis
- **Seaborn/Matplotlib**: Additional visualization support

## Data Source

All data is sourced directly from the DuckDB database using optimized SQL queries. The data is cached for performance, with a 1-hour TTL (time-to-live).

## Customization

### Modifying Queries

Edit `data_loader.py` to customize the data queries and add new data sources.

### Adding New Visualizations

Edit `app.py` to add new charts or modify existing ones. The code is organized by tabs for easy navigation.

### Styling

Custom CSS is included in `app.py` for additional styling. Modify the `st.markdown()` section to change colors, fonts, etc.

## Troubleshooting

### Database Connection Error

If you see a database connection error:
1. Verify the database exists at `data/aida_challenge.duckdb`
2. Check file permissions
3. Ensure the path is correct (relative to project root)

### Module Import Error

If you see import errors:
1. Make sure you installed dependencies: `uv sync --extra dashboard`
2. Run from the project root directory
3. Activate the virtual environment if using one manually

### Performance Issues

If the dashboard is slow:
1. The geographic map samples data for performance - adjust sample size in the code
2. Clear Streamlit cache: `streamlit cache clear`
3. Check filter selections - large datasets may take time to process

## License

Part of the AIDA Challenge project.
