import streamlit as st

dashboard_page = st.Page("pages/data_visualization.py", title="Home Dashboard", icon="🏠")
sales_page = st.Page("pages/sales_assistant.py", title="Sales Assistant", icon="💰")

# Setup navigation
# st.title("S.T.R.A.T.E.G.Y. Dashboard")
pg = st.navigation([dashboard_page, sales_page])

# Run the navigation
pg.run()
