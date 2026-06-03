import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------
# Page Config
# -------------------
st.set_page_config(page_title="Attrition Dashboard", layout="wide")

# -------------------
# Load Data
# -------------------
df = pd.read_csv("data.csv")
df.columns = df.columns.str.strip()

# -------------------
# Title
# -------------------
st.title("Employee Attrition Analytics Dashboard")
st.markdown("Analyze factors affecting employee turnover in an interactive way.")

# -------------------
# Sidebar Filters
# -------------------
st.sidebar.header("Filters")

# categorical filters
remote_filter = st.sidebar.multiselect(
    "Remote Work",
    df["remote_work"].dropna().unique(),
    default=df["remote_work"].dropna().unique()
)

job_filter = st.sidebar.multiselect(
    "Job Role",
    df["job_role"].dropna().unique(),
    default=df["job_role"].dropna().unique()
)

# numeric sliders
age_range = st.sidebar.slider(
    "Age Range",
    int(df["age"].min()),
    int(df["age"].max()),
    (25, 40)
)

income_range = st.sidebar.slider(
    "Monthly Income Range",
    int(df["monthly_income"].min()),
    int(df["monthly_income"].max()),
    (int(df["monthly_income"].min()), int(df["monthly_income"].max()))
)

distance_range = st.sidebar.slider(
    "Distance from Home",
    int(df["distance_from_home"].min()),
    int(df["distance_from_home"].max()),
    (0, int(df["distance_from_home"].max()))
)

# -------------------
# Filter Data
# -------------------
df_filtered = df[
    (df["remote_work"].isin(remote_filter)) &
    (df["job_role"].isin(job_filter)) &
    (df["age"].between(age_range[0], age_range[1])) &
    (df["monthly_income"].between(income_range[0], income_range[1])) &
    (df["distance_from_home"].between(distance_range[0], distance_range[1]))
]

# stop if empty
if df_filtered.empty:
    st.warning("No data available for selected filters")
    st.stop()

# -------------------
# KPI Section
# -------------------
st.subheader("Key Metrics")

attrition_rate = df_filtered["attrition"].mean()

col1, col2, col3 = st.columns(3)

col1.metric("Total Employees", len(df_filtered))
col2.metric("Attrition Rate", f"{attrition_rate:.2%}")
col3.metric("Avg Income", f"{df_filtered['monthly_income'].mean():.0f}")

# -------------------
# Attrition Distribution
# -------------------
st.subheader("Attrition Distribution")

attrition_counts = df_filtered["attrition"].value_counts().reset_index()
attrition_counts.columns = ["attrition", "count"]

fig1 = px.pie(
    attrition_counts,
    names="attrition",
    values="count"
)

st.plotly_chart(fig1, use_container_width=True)

# -------------------
# Work-Life Balance
# -------------------
st.subheader("Work-Life Balance vs Attrition")

wlb = df_filtered.groupby("work-life_balance")["attrition"] \
    .value_counts(normalize=True) \
    .reset_index(name="ratio")

fig2 = px.bar(
    wlb,
    x="work-life_balance",
    y="ratio",
    color="attrition",
    barmode="group"
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------
# Distance Effect
# -------------------
st.subheader("Distance from Home vs Attrition")

fig3 = px.box(
    df_filtered,
    x="attrition",
    y="distance_from_home",
    color="attrition"
)

st.plotly_chart(fig3, use_container_width=True)

# -------------------
# Promotions Effect
# -------------------
st.subheader("Promotions vs Attrition")

prom = df_filtered.groupby("number_of_promotions")["attrition"] \
    .value_counts(normalize=True) \
    .reset_index(name="ratio")

left_only = prom[prom["attrition"] == 1]

if not left_only.empty:
    fig4 = px.line(
        left_only,
        x="number_of_promotions",
        y="ratio",
        markers=True
    )
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("No attrition data for promotions filter")

# -------------------
# High Risk Group
# -------------------
st.subheader("High Risk Employees")

high_risk = df_filtered[
    (df_filtered["remote_work"] == "No") &
    (df_filtered["distance_from_home"] > df_filtered["distance_from_home"].median()) &
    (df_filtered["work-life_balance"].isin(["Poor", "Fair"])) &
    (df_filtered["number_of_promotions"] == 0)
]

st.write("High Risk Employees Count:", len(high_risk))
st.dataframe(high_risk.head())