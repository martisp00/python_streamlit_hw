"""
Streamlit Homework: Sales Dashboard
Run with: streamlit run dashboard.py

Build a complete sales dashboard with:
- Sidebar filters (date range, category, region, status)
- KPI metrics row
- Multiple chart tabs (Overview, By Category, By Region, Data)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- Page Config ---
st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")

# --- Load Data ---
DATA_PATH = Path(__file__).parent / "data" / "sales_dashboard.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["revenue"] = df["quantity"] * df["unit_price"]
    return df


df = load_data()

st.title("📊 Sales Dashboard")

# =====================================================================
# TODO 1: Sidebar Filters
# =====================================================================
# Create a sidebar with the following filters:
#
# 1. Date range:
#    - Use st.sidebar.date_input for a start date and an end date
#    - Default to the min and max dates in the dataset
#
# 2. Categories:
#    - Use st.sidebar.multiselect
#    - Options: all unique categories from the dataset
#    - Default: all selected
#
# 3. Regions:
#    - Use st.sidebar.multiselect
#    - Options: all unique regions from the dataset
#    - Default: all selected
#
# 4. Status:
#    - Use st.sidebar.multiselect
#    - Options: all unique statuses from the dataset
#    - Default: all selected

st.sidebar.header("Filters")

# Your filter code here...

min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

all_categories = sorted(df["category"].dropna().unique())
all_regions = sorted(df["region"].dropna().unique())
all_statuses = sorted(df["status"].dropna().unique())

selected_categories = st.sidebar.multiselect(
    "Category", options=all_categories, default=all_categories
)
selected_regions = st.sidebar.multiselect(
    "Region", options=all_regions, default=all_regions
)
selected_statuses = st.sidebar.multiselect(
    "Status", options=all_statuses, default=all_statuses
)

# =====================================================================
# TODO 2: Apply Filters
# =====================================================================
# Filter the DataFrame using all the sidebar values from TODO 1.
# Combine conditions with & (and).
# Store the result in a variable called `filtered`.
#
# Hint: df["order_date"].dt.date converts datetime to date for comparison

filtered = df  # Replace this with the filtered version

mask = (
    (df["order_date"].dt.date >= start_date)
    & (df["order_date"].dt.date <= end_date)
    & (df["category"].isin(selected_categories))
    & (df["region"].isin(selected_regions))
    & (df["status"].isin(selected_statuses))
)

filtered = df.loc[mask].copy()

# =====================================================================
# TODO 3: KPI Metrics Row
# =====================================================================
# Create 4 columns using st.columns(4) and display these metrics:
#
# Column 1: Total Revenue — sum of filtered["revenue"], formatted as $X,XXX.XX
# Column 2: Total Orders — number of rows in filtered
# Column 3: Average Order Value — mean of filtered["revenue"], formatted as $X,XXX.XX
# Column 4: Top Category — category with the highest total revenue
#
# Hint: Use col.metric("Label", "Value")
# Hint: Handle the case where filtered is empty (total_orders == 0)

col1, col2, col3, col4 = st.columns(4)

total_orders = len(filtered)

if total_orders == 0:
    col1.metric("Total Revenue", "$0.00")
    col2.metric("Total Orders", "0")
    col3.metric("Average Order Value", "$0.00")
    col4.metric("Top Category", "—")
else:
    total_revenue = float(filtered["revenue"].sum())
    avg_order_value = float(filtered["revenue"].mean())

    top_category = (
        filtered.groupby("category")["revenue"].sum().sort_values(ascending=False).index[0]
    )

    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Total Orders", f"{total_orders:,}")
    col3.metric("Average Order Value", f"${avg_order_value:,.2f}")
    col4.metric("Top Category", str(top_category))

# =====================================================================
# TODO 4: Visualization Tabs
# =====================================================================
# Create 4 tabs: "Overview", "By Category", "By Region", "Data"
#
# Overview tab:
#   - Monthly revenue line chart
#   - Group by month: filtered.groupby(filtered["order_date"].dt.to_period("M"))
#   - Use px.line with markers=True
#
# By Category tab:
#   - Horizontal bar chart of revenue by category
#   - Use px.bar with orientation="h"
#   - Sort by revenue ascending (so highest is at top)
#
# By Region tab:
#   - Pie chart of revenue by region
#   - Use px.pie
#
# Data tab:
#   - Display the filtered DataFrame with st.dataframe
#   - Add a download button using st.download_button to export as CSV
#
# For all charts, use st.plotly_chart(fig, use_container_width=True)
# Add st.info("No data to display.") when filtered is empty

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "By Category", "By Region", "Data"])

with tab1:
    st.subheader("Monthly Revenue")
    if filtered.empty:
        st.info("No data to display.")
    else:
        monthly = (
            filtered.groupby(filtered["order_date"].dt.to_period("M"))["revenue"]
            .sum()
            .reset_index()
        )
        monthly["order_date"] = monthly["order_date"].astype(str)  # period -> string for plotly
        fig = px.line(monthly, x="order_date", y="revenue", markers=True)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Revenue by Category")
    if filtered.empty:
        st.info("No data to display.")
    else:
        by_cat = (
            filtered.groupby("category")["revenue"].sum().sort_values(ascending=True).reset_index()
        )
        fig = px.bar(by_cat, x="revenue", y="category", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Revenue by Region")
    if filtered.empty:
        st.info("No data to display.")
    else:
        by_region = filtered.groupby("region")["revenue"].sum().reset_index()
        fig = px.pie(by_region, names="region", values="revenue")
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Filtered Data")
    st.dataframe(filtered, use_container_width=True)

    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered CSV",
        data=csv_bytes,
        file_name="sales_dashboard_filtered.csv",
        mime="text/csv",
    )