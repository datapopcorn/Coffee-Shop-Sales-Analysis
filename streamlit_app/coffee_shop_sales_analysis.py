# streamlit app for coffee shop sales analysis

import streamlit as st
import pandas as pd
import plotly.express as px
from google.cloud import bigquery
from google.oauth2 import service_account
import json
from pygwalker.api.streamlit import StreamlitRenderer

# Set page config
st.set_page_config(
    page_title="Coffee Shop Sales Analysis",
    page_icon="☕",
    layout="wide"
)

# upload credentials file
uploaded_file = st.file_uploader("Upload credentials file", type=["json"])
if uploaded_file is not None:
    credentials_json = json.loads(uploaded_file.read())
    credentials = service_account.Credentials.from_service_account_info(credentials_json)
    client = bigquery.Client(credentials=credentials)
    st.success("Credentials file uploaded successfully")
else:
    st.warning("Please upload a credentials file")
    st.stop()

# Function to run BigQuery query
def run_query(query):
    query_job = client.query(query)
    return query_job.to_dataframe()

# Title
st.title("☕ Coffee Shop Sales Analysis")

# Query item count pie chart    
item_count_query = """
SELECT 
    i.name as item_name,
    SUM(tx_i.quantity) as total_quantity
FROM `cloud-385312.coffee_shop_analysis_dbt.dim_transaction_items` tx_i
LEFT JOIN `cloud-385312.coffee_shop_analysis_dbt.dim_items` i ON tx_i.item_id = i.item_id
GROUP BY item_name
"""

# Query for monthly sales
monthly_sales_query = """
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC(transaction_date, month) AS month,
        COUNT(DISTINCT transaction_id) as order_count,
        SUM(CAST(total_spent AS NUMERIC)) as total_sales,
    FROM `cloud-385312.coffee_shop_analysis_dbt.fct_transactions`
    GROUP BY DATE_TRUNC(transaction_date, month)
)
SELECT
    month,
    order_count,
    total_sales
FROM monthly_sales
ORDER BY month ASC;
"""

# pygwalker query
pygwalker_query = """
SELECT * FROM `cloud-385312.coffee_shop_analysis_dbt.fct_transactions`
"""

# Run queries and cache results
@st.cache_data(ttl=3600)
def run_queries():
    item_count_df = run_query(item_count_query)
    monthly_sales_df = run_query(monthly_sales_query)
    pygwalker_df = run_query(pygwalker_query)
    return item_count_df, monthly_sales_df, pygwalker_df

item_count_df, monthly_sales_df, pygwalker_df = run_queries()

# Create three columns for the charts
col1, = st.columns(1)

# First chart: Item Quantity Pie Chart
with col1:
    st.subheader("Item Quantity Pie Chart")
    fig1 = px.pie(
        item_count_df,
        values='total_quantity',
        names='item_name',
        title='Item Quantity'
    )
    st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

col2, = st.columns(1)
# Third chart: Daily Sales by Location
with col2:
    st.subheader("Monthly Sales")
    fig3 = px.line(
        monthly_sales_df,
        x='month',
        y='total_sales',
        title='Monthly Sales',
        labels={'month': 'Month', 'total_sales': 'Total Sales'}
    )
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

col3, = st.columns(1)
with col3:
    st.subheader("PygWalker")
    # change date column to pandas datetime
    pygwalker_df['transaction_date'] = pd.to_datetime(pygwalker_df['transaction_date'])
    pyg_app = StreamlitRenderer(pygwalker_df)
    pyg_app.explorer()
