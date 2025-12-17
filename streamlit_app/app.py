"""
AIDA Challenge - Interactive Data Visualization Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from data_loader import (
    load_customer_demographics,
    load_policy_data,
    load_geographic_data,
    load_cluster_summary,
    load_channel_performance,
    load_product_performance,
    load_interaction_summary,
    load_raw_clienti,
    load_raw_polizze,
    load_raw_sinistri,
    load_raw_reclami,
    load_raw_abitazioni,
    load_raw_interazioni_clienti,
    load_raw_competitor_prodotti,
)

# Page configuration
st.set_page_config(
    page_title="AIDA Challenge Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0173B2;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Logo and Title
logo_path = Path(__file__).parent / "images" / "vita_sicura_geometric4.png"
if logo_path.exists():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(str(logo_path), width=150)
    with col2:
        st.markdown(
            '<p class="main-header">AIDA Challenge - Insurance Analytics Dashboard</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            "**Interactive dashboard for exploring customer data, policy performance, and business insights**"
        )
else:
    st.markdown(
        '<p class="main-header">📊 AIDA Challenge - Insurance Analytics Dashboard</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "**Interactive dashboard for exploring customer data, policy performance, and business insights**"
    )

# Sidebar logo
st.sidebar.image(str(logo_path), use_container_width=True)
st.sidebar.title("🎛️ Filters")

# Load data
df_customers = load_customer_demographics()
df_policies = load_policy_data()

# Sidebar filters
clusters = ["All"] + sorted(df_customers["cluster"].dropna().unique().tolist())
selected_cluster = st.sidebar.selectbox("Customer Cluster", clusters)

age_range = st.sidebar.slider(
    "Age Range",
    int(df_customers["age"].min()),
    int(df_customers["age"].max()),
    (int(df_customers["age"].min()), int(df_customers["age"].max())),
)

income_range = st.sidebar.slider(
    "Income Range (€)",
    int(df_customers["income"].min()),
    int(df_customers["income"].max()),
    (int(df_customers["income"].min()), int(df_customers["income"].max())),
)

# Apply filters
filtered_customers = df_customers[
    (df_customers["age"] >= age_range[0])
    & (df_customers["age"] <= age_range[1])
    & (df_customers["income"] >= income_range[0])
    & (df_customers["income"] <= income_range[1])
]

if selected_cluster != "All":
    filtered_customers = filtered_customers[filtered_customers["cluster"] == selected_cluster]

# Key metrics
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Key Metrics")
st.sidebar.metric("Total Customers", f"{len(filtered_customers):,}")
st.sidebar.metric("Avg CLV", f"€{filtered_customers['clv'].mean():,.0f}")
st.sidebar.metric("Avg Engagement", f"{filtered_customers['engagement_score'].mean():.2f}")
st.sidebar.metric("Avg Churn Risk", f"{filtered_customers['churn_probability'].mean():.1%}")

# Main content tabs
tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
    [
        "🔍 Data Exploration",
        "👥 Demographics",
        "💼 Portfolio",
        "💰 Customer Value",
        "🗺️ Geography",
        "📦 Products",
        "⏳ Lifecycle",
        "📣 Channels",
        "🎯 Segmentation",
    ]
)

# Tab 0: Data Exploration (Staging Layer)
with tab0:
    st.header("🔍 Raw Data Exploration - Staging Layer")
    st.markdown(
        """
        This tab provides a detailed exploration of the raw source tables before transformation.
        Select a table below to explore its structure, data types, null values, and distributions.
        """
    )

    # Create sub-tabs for each raw table
    subtab1, subtab2, subtab3, subtab4, subtab5, subtab6, subtab7 = st.tabs(
        [
            "Clienti",
            "Polizze",
            "Sinistri",
            "Reclami",
            "Abitazioni",
            "Interazioni",
            "Competitor",
        ]
    )

    def explore_dataframe(df, table_name):
        """Helper function to explore a dataframe."""
        st.subheader(f"📊 {table_name} Overview")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        with col2:
            st.metric("Total Columns", f"{len(df.columns):,}")
        with col3:
            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        with col4:
            duplicate_rows = df.duplicated().sum()
            st.metric("Duplicate Rows", f"{duplicate_rows:,}")

        # Data Types
        st.subheader("📋 Column Data Types")
        dtype_df = pd.DataFrame(
            {
                "Column": df.dtypes.index,
                "Data Type": df.dtypes.values.astype(str),
                "Non-Null Count": [df[col].count() for col in df.columns],
                "Null Count": [df[col].isna().sum() for col in df.columns],
                "Null %": [f"{df[col].isna().sum() / len(df) * 100:.1f}%" for col in df.columns],
            }
        )
        st.dataframe(dtype_df, use_container_width=True, height=400)

        # Null Value Heatmap
        st.subheader("🔥 Null Values Heatmap")
        null_data = df.isnull().sum()
        null_data = null_data[null_data > 0].sort_values(ascending=False)

        if len(null_data) > 0:
            fig_null = px.bar(
                x=null_data.values,
                y=null_data.index,
                orientation="h",
                title="Columns with Missing Values",
                labels={"x": "Number of Null Values", "y": "Column"},
                color=null_data.values,
                color_continuous_scale="Reds",
            )
            fig_null.update_layout(showlegend=False, height=max(400, len(null_data) * 25))
            st.plotly_chart(fig_null, use_container_width=True, key=f"null_chart_{table_name}")
        else:
            st.success("✅ No missing values found in this table!")

        # Sample Data
        st.subheader("📄 Sample Data (First 100 rows)")
        st.dataframe(df.head(100), use_container_width=True, height=400)

        # Numeric Columns Distribution
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if numeric_cols:
            st.subheader("📊 Numeric Columns - Descriptive Statistics")
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)

            st.subheader("📈 Numeric Columns - Distributions")
            selected_numeric = st.multiselect(
                "Select numeric columns to visualize",
                numeric_cols,
                default=numeric_cols[:3] if len(numeric_cols) >= 3 else numeric_cols,
                key=f"numeric_{table_name}",
            )

            if selected_numeric:
                cols_per_row = 2
                for i in range(0, len(selected_numeric), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, col_name in enumerate(selected_numeric[i : i + cols_per_row]):
                        with cols[j]:
                            fig = px.histogram(
                                df,
                                x=col_name,
                                title=f"{col_name} Distribution",
                                labels={col_name: col_name},
                                color_discrete_sequence=["#0173B2"],
                            )
                            fig.update_layout(showlegend=False, height=300)
                            st.plotly_chart(
                                fig, use_container_width=True, key=f"hist_{table_name}_{col_name}"
                            )

        # Categorical Columns
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        if categorical_cols:
            st.subheader("🏷️ Categorical Columns - Value Counts")
            selected_categorical = st.selectbox(
                "Select a categorical column to explore",
                categorical_cols,
                key=f"cat_{table_name}",
            )

            if selected_categorical:
                value_counts = df[selected_categorical].value_counts().head(20)

                col1, col2 = st.columns([2, 1])
                with col1:
                    fig_cat = px.bar(
                        x=value_counts.values,
                        y=value_counts.index,
                        orientation="h",
                        title=f"Top 20 Values - {selected_categorical}",
                        labels={"x": "Count", "y": selected_categorical},
                        color=value_counts.values,
                        color_continuous_scale="Viridis",
                    )
                    fig_cat.update_layout(showlegend=False, height=500)
                    st.plotly_chart(
                        fig_cat,
                        use_container_width=True,
                        key=f"cat_chart_{table_name}_{selected_categorical}",
                    )

                with col2:
                    st.metric("Unique Values", f"{df[selected_categorical].nunique():,}")
                    st.metric("Most Common", value_counts.index[0])
                    st.metric("Most Common Count", f"{value_counts.values[0]:,}")
                    st.metric("Most Common %", f"{value_counts.values[0] / len(df) * 100:.1f}%")

        # Date Columns
        date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
        if date_cols:
            st.subheader("📅 Date Columns - Time Range")
            for date_col in date_cols:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(f"{date_col} - Min", str(df[date_col].min())[:10])
                with col2:
                    st.metric(f"{date_col} - Max", str(df[date_col].max())[:10])
                with col3:
                    date_range = (df[date_col].max() - df[date_col].min()).days
                    st.metric(f"{date_col} - Range", f"{date_range:,} days")

    # Clienti table
    with subtab1:
        df_raw_clienti = load_raw_clienti()
        explore_dataframe(df_raw_clienti, "Clienti")

    # Polizze table
    with subtab2:
        df_raw_polizze = load_raw_polizze()
        explore_dataframe(df_raw_polizze, "Polizze")

    # Sinistri table
    with subtab3:
        df_raw_sinistri = load_raw_sinistri()
        explore_dataframe(df_raw_sinistri, "Sinistri")

    # Reclami table
    with subtab4:
        df_raw_reclami = load_raw_reclami()
        explore_dataframe(df_raw_reclami, "Reclami")

    # Abitazioni table
    with subtab5:
        df_raw_abitazioni = load_raw_abitazioni()
        explore_dataframe(df_raw_abitazioni, "Abitazioni")

    # Interazioni Clienti table
    with subtab6:
        df_raw_interazioni = load_raw_interazioni_clienti()
        explore_dataframe(df_raw_interazioni, "Interazioni Clienti")

    # Competitor Prodotti table
    with subtab7:
        df_raw_competitor = load_raw_competitor_prodotti()
        explore_dataframe(df_raw_competitor, "Competitor Prodotti")

# Tab 1: Customer Demographics
with tab1:
    st.header("Customer Demographics")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Customers", f"{len(filtered_customers):,}")
    with col2:
        st.metric("Avg Age", f"{filtered_customers['age'].mean():.1f} years")
    with col3:
        st.metric("Avg Income", f"€{filtered_customers['income'].mean():,.0f}")
    with col4:
        st.metric("Avg Policies", f"{filtered_customers['policy_count'].mean():.1f}")

    col1, col2 = st.columns(2)

    with col1:
        # Age distribution
        fig_age = px.histogram(
            filtered_customers,
            x="age",
            nbins=30,
            title="Age Distribution",
            labels={"age": "Age", "count": "Number of Customers"},
            color_discrete_sequence=["#0173B2"],
        )
        fig_age.update_layout(showlegend=False)
        st.plotly_chart(fig_age, use_container_width=True)

    with col2:
        # Income distribution
        fig_income = px.histogram(
            filtered_customers,
            x="income",
            nbins=30,
            title="Income Distribution",
            labels={"income": "Income (€)", "count": "Number of Customers"},
            color_discrete_sequence=["#756bb1"],
        )
        fig_income.update_layout(showlegend=False)
        st.plotly_chart(fig_income, use_container_width=True)

    # Top professions
    st.subheader("Top 10 Professions")
    profession_counts = filtered_customers["profession"].value_counts().head(10)
    fig_prof = px.bar(
        x=profession_counts.values,
        y=profession_counts.index,
        orientation="h",
        title="Most Common Professions",
        labels={"x": "Count", "y": "Profession"},
        color=profession_counts.values,
        color_continuous_scale="Viridis",
    )
    fig_prof.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_prof, use_container_width=True)

# Tab 2: Portfolio Analysis
with tab2:
    st.header("Portfolio & Premium Analysis")

    # Merge customer data with policies for filtered view
    filtered_customer_ids = filtered_customers["customer_id"].tolist()
    filtered_policies = df_policies[df_policies["customer_id"].isin(filtered_customer_ids)]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Policies", f"{len(filtered_policies):,}")
    with col2:
        st.metric(
            "Active Policies",
            f"{len(filtered_policies[filtered_policies['policy_status']=='Attiva']):,}",
        )
    with col3:
        st.metric("Total Premium", f"€{filtered_policies['annual_premium'].sum():,.0f}")
    with col4:
        st.metric("Avg Premium", f"€{filtered_policies['annual_premium'].mean():,.0f}")

    col1, col2 = st.columns(2)

    with col1:
        # Premium by Need Area
        need_area_premium = (
            filtered_policies.groupby("need_area")["annual_premium"]
            .sum()
            .sort_values(ascending=True)
        )
        fig_need = px.bar(
            x=need_area_premium.values,
            y=need_area_premium.index,
            orientation="h",
            title="Total Premium by Need Area",
            labels={"x": "Total Premium (€)", "y": "Need Area"},
            color=need_area_premium.values,
            color_continuous_scale="Cividis",
        )
        fig_need.update_layout(showlegend=False)
        st.plotly_chart(fig_need, use_container_width=True)

    with col2:
        # Top products by premium
        product_premium = (
            filtered_policies.groupby("product")["annual_premium"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        fig_product = px.bar(
            x=product_premium.values,
            y=product_premium.index,
            orientation="h",
            title="Top 10 Products by Premium",
            labels={"x": "Total Premium (€)", "y": "Product"},
            color=product_premium.values,
            color_continuous_scale="Plasma",
        )
        fig_product.update_layout(showlegend=False)
        st.plotly_chart(fig_product, use_container_width=True)

    # Premium distribution boxplot
    st.subheader("Premium Distribution by Need Area")
    fig_box = px.box(
        filtered_policies,
        x="need_area",
        y="annual_premium",
        title="Annual Premium Distribution",
        labels={"need_area": "Need Area", "annual_premium": "Annual Premium (€)"},
        color="need_area",
    )
    fig_box.update_layout(showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

# Tab 3: Customer Value & Risk
with tab3:
    st.header("Customer Value & Risk Analysis")

    value_data = filtered_customers.dropna(subset=["engagement_score", "churn_probability", "clv"])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg CLV", f"€{value_data['clv'].mean():,.0f}")
    with col2:
        st.metric("Avg Engagement Score", f"{value_data['engagement_score'].mean():.2f}")
    with col3:
        st.metric("Avg Churn Probability", f"{value_data['churn_probability'].mean():.1%}")

    col1, col2 = st.columns(2)

    with col1:
        # Engagement vs Churn scatter
        fig_scatter = px.scatter(
            value_data,
            x="engagement_score",
            y="churn_probability",
            color="cluster",
            size="clv",
            hover_data=["customer_id", "clv"],
            title="Engagement Score vs Churn Probability",
            labels={
                "engagement_score": "Engagement Score",
                "churn_probability": "Churn Probability",
                "cluster": "Cluster",
            },
            color_discrete_sequence=["#0173B2", "#F0E442", "#56B4E9", "#D55E00", "#CC79A7"],
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        # CLV by Cluster
        fig_clv = px.box(
            value_data,
            x="cluster",
            y="clv",
            title="Customer Lifetime Value by Cluster",
            labels={"cluster": "Cluster", "clv": "CLV (€)"},
            color="cluster",
        )
        fig_clv.update_layout(showlegend=False)
        st.plotly_chart(fig_clv, use_container_width=True)

    # CLV Distribution
    st.subheader("CLV Distribution")
    fig_clv_dist = px.histogram(
        value_data,
        x="clv",
        nbins=50,
        title="Customer Lifetime Value Distribution",
        labels={"clv": "CLV (€)", "count": "Number of Customers"},
        color_discrete_sequence=["#009E73"],
    )
    st.plotly_chart(fig_clv_dist, use_container_width=True)

# Tab 4: Geographic Distribution
with tab4:
    st.header("Geographic Distribution")

    df_geo = load_geographic_data()

    # Filter geographic data based on selected customers
    filtered_geo = df_geo[df_geo["customer_id"].isin(filtered_customers["customer_id"])]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cities Covered", f"{filtered_geo['city'].nunique():,}")
    with col2:
        st.metric("Total CLV", f"€{filtered_geo['clv'].sum():,.0f}")
    with col3:
        st.metric("Avg CLV per Location", f"€{filtered_geo['clv'].mean():,.0f}")

    # Interactive map
    sample_size = min(5000, len(filtered_geo))
    geo_sample = (
        filtered_geo.sample(sample_size) if len(filtered_geo) > sample_size else filtered_geo
    )

    fig_map = px.scatter_map(
        geo_sample,
        lat="lat",
        lon="lon",
        color="clv",
        size="clv",
        hover_data=["city", "clv"],
        title=f"Customer Locations (showing {len(geo_sample):,} of {len(filtered_geo):,} customers)",
        color_continuous_scale="Plasma",
        size_max=15,
        zoom=5,
        height=600,
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)

    # Top cities by CLV
    st.subheader("Top 15 Cities by Total CLV")
    city_clv = (
        filtered_geo.groupby("city")["clv"]
        .agg(["sum", "count", "mean"])
        .sort_values("sum", ascending=False)
        .head(15)
    )
    city_clv.columns = ["Total CLV", "Customer Count", "Avg CLV"]

    fig_cities = px.bar(
        city_clv,
        y=city_clv.index,
        x="Total CLV",
        orientation="h",
        title="Cities by Total CLV",
        labels={"Total CLV": "Total CLV (€)", "city": "City"},
        color="Total CLV",
        color_continuous_scale="Viridis",
    )
    st.plotly_chart(fig_cities, use_container_width=True)

    # Display table
    st.dataframe(
        city_clv.style.format(
            {"Total CLV": "€{:,.0f}", "Customer Count": "{:,.0f}", "Avg CLV": "€{:,.0f}"}
        )
    )

# Tab 5: Product Performance
with tab5:
    st.header("Product Performance & Profitability")

    df_products = load_product_performance()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Products", f"{df_products['product'].nunique():,}")
    with col2:
        st.metric("Total Revenue", f"€{df_products['total_premium'].sum():,.0f}")
    with col3:
        st.metric("Total Margin", f"€{df_products['total_margin'].sum():,.0f}")

    col1, col2 = st.columns(2)

    with col1:
        # Loss Ratio by Top Products
        top_products = df_products.nlargest(10, "total_premium")
        fig_loss = px.bar(
            top_products,
            y="product",
            x="avg_loss_ratio",
            orientation="h",
            title="Loss Ratio - Top 10 Products by Premium",
            labels={"avg_loss_ratio": "Average Loss Ratio", "product": "Product"},
            # color="avg_loss_ratio",
            # color_continuous_scale="RdYlGn_r",
        )
        st.plotly_chart(fig_loss, use_container_width=True)

    with col2:
        # Total Margin
        fig_margin = px.bar(
            top_products,
            y="product",
            x="total_margin",
            orientation="h",
            title="Total Margin - Top 10 Products",
            labels={"total_margin": "Total Margin (€)", "product": "Product"},
            # color="total_margin",
            # color_continuous_scale="Plasma",
        )
        st.plotly_chart(fig_margin, use_container_width=True)

    # Product performance table
    st.subheader("Product Performance Details")
    product_display = df_products.copy()
    product_display = product_display.sort_values("total_premium", ascending=False).head(20)
    st.dataframe(
        product_display.style.format(
            {
                "avg_loss_ratio": "{:.2%}",
                "total_premium": "€{:,.0f}",
                "total_margin": "€{:,.0f}",
                "policy_count": "{:,.0f}",
                "avg_premium": "€{:,.0f}",
            }
        ),
        use_container_width=True,
    )

# Tab 6: Customer Lifecycle
with tab6:
    st.header("Customer Lifecycle & Retention")

    # Create lifecycle stages
    lifecycle_data = filtered_customers.copy()
    lifecycle_data["lifecycle_stage"] = pd.cut(
        lifecycle_data["tenure_years"],
        bins=[0, 2, 5, 10, float("inf")],
        labels=["New (0-2y)", "Growing (2-5y)", "Mature (5-10y)", "Loyal (10y+)"],
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Tenure", f"{lifecycle_data['tenure_years'].mean():.1f} years")
    with col2:
        new_customers = len(lifecycle_data[lifecycle_data["tenure_years"] < 2])
        st.metric("New Customers (<2y)", f"{new_customers:,}")
    with col3:
        loyal_customers = len(lifecycle_data[lifecycle_data["tenure_years"] >= 10])
        st.metric("Loyal Customers (10y+)", f"{loyal_customers:,}")
    with col4:
        st.metric("Avg Annual Visits", f"{lifecycle_data['annual_visits'].mean():.1f}")

    col1, col2 = st.columns(2)

    with col1:
        # Tenure distribution
        fig_tenure = px.histogram(
            lifecycle_data,
            x="tenure_years",
            nbins=20,
            title="Customer Tenure Distribution",
            labels={"tenure_years": "Years with Company", "count": "Number of Customers"},
            color_discrete_sequence=["#0173B2"],
        )
        st.plotly_chart(fig_tenure, use_container_width=True)

    with col2:
        # Churn by Lifecycle Stage
        fig_churn = px.box(
            lifecycle_data.dropna(subset=["churn_probability"]),
            x="lifecycle_stage",
            y="churn_probability",
            title="Churn Probability by Lifecycle Stage",
            labels={"lifecycle_stage": "Lifecycle Stage", "churn_probability": "Churn Probability"},
            color="lifecycle_stage",
        )
        fig_churn.update_layout(showlegend=False)
        st.plotly_chart(fig_churn, use_container_width=True)

    # Engagement vs Tenure
    st.subheader("Engagement Over Customer Lifetime")
    fig_eng_tenure = px.scatter(
        lifecycle_data.dropna(subset=["engagement_score"]),
        x="tenure_years",
        y="engagement_score",
        color="lifecycle_stage",
        size="policy_count",
        title="Engagement Score vs Tenure",
        labels={
            "tenure_years": "Years with Company",
            "engagement_score": "Engagement Score",
            "lifecycle_stage": "Stage",
        },
    )
    st.plotly_chart(fig_eng_tenure, use_container_width=True)

# Tab 7: Channel Performance
with tab7:
    st.header("Channel Performance & Acquisition")

    df_channels = load_channel_performance()
    df_interactions = load_interaction_summary()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Channels", f"{len(df_channels):,}")
    with col2:
        st.metric("Total Revenue", f"€{df_channels['total_revenue'].sum():,.0f}")
    with col3:
        st.metric("Avg Conversion Rate", f"{df_interactions['conversion_rate'].mean():.1f}%")

    col1, col2 = st.columns(2)

    with col1:
        # Channel Revenue
        fig_channel_rev = px.bar(
            df_channels,
            y="channel",
            x="total_revenue",
            orientation="h",
            title="Total Revenue by Acquisition Channel",
            labels={"total_revenue": "Total Revenue (€)", "channel": "Channel"},
            color="total_revenue",
            color_continuous_scale="Viridis",
        )
        st.plotly_chart(fig_channel_rev, use_container_width=True)

    with col2:
        # CLV by Channel
        fig_channel_clv = px.bar(
            df_channels,
            y="channel",
            x="avg_clv",
            orientation="h",
            title="Average CLV by Channel",
            labels={"avg_clv": "Average CLV (€)", "channel": "Channel"},
            color="avg_clv",
            color_continuous_scale="Cividis",
        )
        st.plotly_chart(fig_channel_clv, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Interaction Volume
        fig_interactions = px.bar(
            df_interactions,
            x="interaction_count",
            y="interaction_type",
            orientation="h",
            title="Interaction Volume by Type",
            labels={"interaction_count": "Number of Interactions", "interaction_type": "Type"},
            color="interaction_count",
            color_continuous_scale="Plasma",
        )
        st.plotly_chart(fig_interactions, use_container_width=True)

    with col2:
        # Conversion Rate
        fig_conversion = px.bar(
            df_interactions,
            x="conversion_rate",
            y="interaction_type",
            orientation="h",
            title="Conversion Rate by Interaction Type",
            labels={"conversion_rate": "Conversion Rate (%)", "interaction_type": "Type"},
            color="conversion_rate",
            color_continuous_scale="Viridis",
        )
        st.plotly_chart(fig_conversion, use_container_width=True)

# Tab 8: Customer Segmentation
with tab8:
    st.header("Customer Segmentation Deep Dive")

    df_clusters = load_cluster_summary()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Clusters", f"{len(df_clusters):,}")
    with col2:
        st.metric(
            "Largest Cluster", df_clusters.loc[df_clusters["customer_count"].idxmax(), "cluster"]
        )
    with col3:
        highest_clv_cluster = df_clusters.loc[df_clusters["avg_clv"].idxmax(), "cluster"]
        st.metric("Highest CLV Cluster", highest_clv_cluster)

    # Cluster sizes
    st.subheader("Cluster Distribution")
    fig_cluster_pie = px.pie(
        df_clusters,
        values="customer_count",
        names="cluster",
        title="Customer Distribution by Cluster",
        color_discrete_sequence=["#0173B2", "#F0E442", "#56B4E9", "#D55E00", "#CC79A7"],
    )
    st.plotly_chart(fig_cluster_pie, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # CLV by Cluster
        fig_cluster_clv = px.bar(
            df_clusters,
            x="cluster",
            y="avg_clv",
            title="Average CLV by Cluster",
            labels={"avg_clv": "Average CLV (€)", "cluster": "Cluster"},
            color="avg_clv",
            color_continuous_scale="Plasma",
        )
        st.plotly_chart(fig_cluster_clv, use_container_width=True)

    with col2:
        # Churn Risk by Cluster
        fig_cluster_churn = px.bar(
            df_clusters,
            x="cluster",
            y="avg_churn_risk",
            title="Churn Risk by Cluster",
            labels={"avg_churn_risk": "Average Churn Probability", "cluster": "Cluster"},
            color="avg_churn_risk",
            color_continuous_scale="RdYlGn_r",
        )
        fig_cluster_churn.add_hline(
            y=0.5, line_dash="dash", line_color="red", annotation_text="High Risk (50%)"
        )
        st.plotly_chart(fig_cluster_churn, use_container_width=True)

    # Engagement vs Satisfaction
    st.subheader("Cluster Characteristics: Engagement vs Satisfaction")
    fig_cluster_scatter = px.scatter(
        df_clusters,
        x="avg_engagement",
        y="avg_satisfaction",
        size="customer_count",
        color="cluster",
        text="cluster",
        title="Engagement vs Satisfaction by Cluster",
        labels={
            "avg_engagement": "Average Engagement Score",
            "avg_satisfaction": "Average Satisfaction Score",
            "customer_count": "Customer Count",
        },
        color_discrete_sequence=["#0173B2", "#F0E442", "#56B4E9", "#D55E00", "#CC79A7"],
    )
    fig_cluster_scatter.update_traces(textposition="top center")
    st.plotly_chart(fig_cluster_scatter, use_container_width=True)

    # Cluster details table
    st.subheader("Cluster Details")
    cluster_display = df_clusters.copy()
    st.dataframe(
        cluster_display.style.format(
            {
                "customer_count": "{:,.0f}",
                "avg_age": "{:.1f}",
                "avg_income": "€{:,.0f}",
                "avg_policies": "{:.1f}",
                "avg_clv": "€{:,.0f}",
                "avg_engagement": "{:.2f}",
                "avg_churn_risk": "{:.1%}",
                "avg_satisfaction": "{:.2f}",
            }
        ),
        use_container_width=True,
    )

# Footer
st.markdown("---")
st.markdown("**AIDA Challenge Dashboard** | Data sourced from DuckDB | Built with Streamlit")
