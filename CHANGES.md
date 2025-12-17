# Streamlit App Enhancement - Data Exploration Tab

## Summary of Changes

### 1. Data Loader Updates (`streamlit_app/data_loader.py`)

Added 7 new data loader functions that load raw tables directly from the database using `SELECT *`:

- `load_raw_clienti()` - Loads all columns from `main.clienti`
- `load_raw_polizze()` - Loads all columns from `main.polizze`
- `load_raw_sinistri()` - Loads all columns from `main.sinistri`
- `load_raw_reclami()` - Loads all columns from `main.reclami`
- `load_raw_abitazioni()` - Loads all columns from `main.abitazioni`
- `load_raw_interazioni_clienti()` - Loads all columns from `main.interazioni_clienti`
- `load_raw_competitor_prodotti()` - Loads all columns from `main.competitor_prodotti`

All functions use `SELECT *` to import all columns without renaming, and are cached for performance.

### 2. Main App Updates (`streamlit_app/app.py`)

#### Added imports:
- `numpy` for numerical operations
- All 7 new raw data loader functions

#### New Tab Structure:
- Added "🔍 Data Exploration" as the first tab (tab0)
- Renamed all existing tabs to tab1-tab8

#### New Tab Features:

The Data Exploration tab includes:

**Sub-tabs for each table:**
1. Clienti (Customers)
2. Polizze (Policies)
3. Sinistri (Claims)
4. Reclami (Complaints)
5. Abitazioni (Housing)
6. Interazioni (Interactions)
7. Competitor (Competitor Products)

**For each table, the following analyses are provided:**

1. **Overview Metrics:**
   - Total rows
   - Total columns
   - Memory usage
   - Duplicate rows count

2. **Column Data Types Table:**
   - Column name
   - Data type
   - Non-null count
   - Null count
   - Null percentage

3. **Null Values Visualization:**
   - Horizontal bar chart showing columns with missing values
   - Color-coded by severity (red scale)
   - Success message if no nulls found

4. **Sample Data:**
   - First 100 rows displayed in interactive table

5. **Numeric Columns Analysis:**
   - Descriptive statistics (mean, std, min, max, quartiles)
   - Interactive distribution histograms
   - Multi-select to choose which columns to visualize
   - Side-by-side comparison (2 columns per row)

6. **Categorical Columns Analysis:**
   - Dropdown to select a categorical column
   - Top 20 value counts visualization
   - Key metrics: unique values, most common value, frequency, percentage

7. **Date Columns Analysis:**
   - Min date, max date, and date range in days
   - Displayed for each date column found

## Key Design Decisions

1. **SELECT * Approach:** Used `SELECT *` for simplicity and maintainability, keeping original column names
2. **Caching:** All data loaders use `@st.cache_data(ttl=3600)` for performance
3. **Helper Function:** Created `explore_dataframe()` helper to avoid code duplication across sub-tabs
4. **Interactive Elements:** Multi-select for numeric columns, dropdown for categorical columns
5. **Responsive Layout:** Dynamic column layouts and chart sizing

## Usage

Users can now:
1. Navigate to the "🔍 Data Exploration" tab (first tab)
2. Select any of the 7 sub-tabs to explore a specific table
3. View comprehensive data quality and distribution information
4. Interactively select columns to visualize
5. Understand the raw data before DBT transformations

This provides a complete view of the staging layer (raw tables) before any transformations are applied.
