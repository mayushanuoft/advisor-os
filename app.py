"""
AdvisorOS - Proof of Concept
Hardcoded data from Client_Statement_Test.pdf for demo purposes.
Dashboard loads immediately — no API or file upload required.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Page config & layout
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AdvisorOS",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 AdvisorOS — Client Cash Flow Analysis")

# ---------------------------------------------------------------------------
# Hardcoded transactions from Client_Statement_Test.pdf
# Categories assigned based on merchant type:
#   Fixed Cost: auto finance, property tax, gas/utilities, telecom, insurance, savings transfers
#   Discretionary: travel, dining, retail/luxury, golf, fitness, alcohol, contractor
# ---------------------------------------------------------------------------
TRANSACTIONS = [
    {"Date": "2026-03-01", "Merchant": "Equinox Fitness",                "Amount": 246.88,  "CategoryType": "Discretionary"},
    {"Date": "2026-03-01", "Merchant": "TD Auto Finance",                "Amount": 1009.59, "CategoryType": "Fixed Cost"},
    {"Date": "2026-02-24", "Merchant": "Transfer to Acct 8842",          "Amount": 3418.51, "CategoryType": "Fixed Cost"},
    {"Date": "2026-02-23", "Merchant": "LCBO Vintages",                  "Amount": 583.78,  "CategoryType": "Discretionary"},
    {"Date": "2026-02-22", "Merchant": "Toronto Golf Club",              "Amount": 1126.86, "CategoryType": "Discretionary"},
    {"Date": "2026-02-21", "Merchant": "Holt Renfrew",                   "Amount": 887.86,  "CategoryType": "Discretionary"},
    {"Date": "2026-02-20", "Merchant": "Transfer to Acct 8842",          "Amount": 3320.18, "CategoryType": "Fixed Cost"},
    {"Date": "2026-02-17", "Merchant": "Enbridge Gas",                   "Amount": 240.06,  "CategoryType": "Fixed Cost"},
    {"Date": "2026-02-15", "Merchant": "Manulife Insurance",             "Amount": 557.30,  "CategoryType": "Fixed Cost"},
    {"Date": "2026-02-14", "Merchant": "Transfer to Acct 8842",          "Amount": 3878.33, "CategoryType": "Fixed Cost"},
    {"Date": "2026-02-13", "Merchant": "Holt Renfrew",                   "Amount": 2619.24, "CategoryType": "Discretionary"},
    {"Date": "2026-02-11", "Merchant": "Manulife Insurance",             "Amount": 484.92,  "CategoryType": "Fixed Cost"},
    {"Date": "2026-02-10", "Merchant": "Holt Renfrew",                   "Amount": 2568.84, "CategoryType": "Discretionary"},
    {"Date": "2026-02-10", "Merchant": "Holt Renfrew",                   "Amount": 1331.23, "CategoryType": "Discretionary"},
    {"Date": "2026-02-10", "Merchant": "Equinox Fitness",                "Amount": 219.10,  "CategoryType": "Discretionary"},
    {"Date": "2026-02-09", "Merchant": "TD Auto Finance",                "Amount": 839.48,  "CategoryType": "Fixed Cost"},
    {"Date": "2026-02-08", "Merchant": "Alo Restaurant",                 "Amount": 732.14,  "CategoryType": "Discretionary"},
    {"Date": "2026-02-07", "Merchant": "Manulife Insurance",             "Amount": 364.79,  "CategoryType": "Fixed Cost"},
    {"Date": "2026-02-05", "Merchant": "City of Toronto Property Tax",   "Amount": 1637.01, "CategoryType": "Fixed Cost"},
    {"Date": "2026-02-05", "Merchant": "Air Canada - Signature Class",   "Amount": 4352.11, "CategoryType": "Discretionary"},
    {"Date": "2026-02-04", "Merchant": "Manulife Insurance",             "Amount": 599.59,  "CategoryType": "Fixed Cost"},
    {"Date": "2026-02-03", "Merchant": "Rogers Communications",          "Amount": 150.66,  "CategoryType": "Fixed Cost"},
    {"Date": "2026-02-02", "Merchant": "LCBO Vintages",                  "Amount": 229.63,  "CategoryType": "Discretionary"},
    {"Date": "2026-02-01", "Merchant": "LCBO Vintages",                  "Amount": 196.81,  "CategoryType": "Discretionary"},
    {"Date": "2026-01-31", "Merchant": "Equinox Fitness",                "Amount": 237.37,  "CategoryType": "Discretionary"},
    {"Date": "2026-01-31", "Merchant": "Alo Restaurant",                 "Amount": 764.27,  "CategoryType": "Discretionary"},
    {"Date": "2026-01-29", "Merchant": "Manulife Insurance",             "Amount": 517.97,  "CategoryType": "Fixed Cost"},
    {"Date": "2026-01-28", "Merchant": "Toronto Golf Club",              "Amount": 1066.84, "CategoryType": "Discretionary"},
    {"Date": "2026-01-27", "Merchant": "Rogers Communications",          "Amount": 143.74,  "CategoryType": "Fixed Cost"},
    {"Date": "2026-01-26", "Merchant": "Holt Renfrew",                   "Amount": 2468.92, "CategoryType": "Discretionary"},
    {"Date": "2026-01-25", "Merchant": "Enbridge Gas",                   "Amount": 224.85,  "CategoryType": "Fixed Cost"},
    {"Date": "2026-01-25", "Merchant": "Enbridge Gas",                   "Amount": 117.76,  "CategoryType": "Fixed Cost"},
    {"Date": "2026-01-25", "Merchant": "City of Toronto Property Tax",   "Amount": 1836.30, "CategoryType": "Fixed Cost"},
    {"Date": "2026-01-24", "Merchant": "Toronto Golf Club",              "Amount": 1168.70, "CategoryType": "Discretionary"},
    {"Date": "2026-01-23", "Merchant": "TD Auto Finance",                "Amount": 814.50,  "CategoryType": "Fixed Cost"},
    {"Date": "2026-01-22", "Merchant": "Manulife Insurance",             "Amount": 536.15,  "CategoryType": "Fixed Cost"},
    {"Date": "2026-01-19", "Merchant": "Air Canada - Signature Class",   "Amount": 5048.39, "CategoryType": "Discretionary"},
    {"Date": "2026-01-16", "Merchant": "Equinox Fitness",                "Amount": 216.46,  "CategoryType": "Discretionary"},
    {"Date": "2026-01-15", "Merchant": "Equinox Fitness",                "Amount": 203.21,  "CategoryType": "Discretionary"},
    {"Date": "2026-01-14", "Merchant": "Transfer to Acct 8842",          "Amount": 2261.67, "CategoryType": "Fixed Cost"},
    {"Date": "2026-01-14", "Merchant": "Smith & Sons LLC (Contractor)",  "Amount": 10748.48,"CategoryType": "Discretionary"},
    {"Date": "2026-01-13", "Merchant": "City of Toronto Property Tax",   "Amount": 1721.68, "CategoryType": "Fixed Cost"},
    {"Date": "2026-01-12", "Merchant": "Toronto Golf Club",              "Amount": 1196.52, "CategoryType": "Discretionary"},
    {"Date": "2026-01-11", "Merchant": "Manulife Insurance",             "Amount": 419.38,  "CategoryType": "Fixed Cost"},
    {"Date": "2026-01-09", "Merchant": "Equinox Fitness",                "Amount": 236.80,  "CategoryType": "Discretionary"},
    {"Date": "2026-01-06", "Merchant": "TD Auto Finance",                "Amount": 889.89,  "CategoryType": "Fixed Cost"},
    {"Date": "2026-01-06", "Merchant": "Toronto Golf Club",              "Amount": 1278.60, "CategoryType": "Discretionary"},
    {"Date": "2026-01-05", "Merchant": "Equinox Fitness",                "Amount": 214.36,  "CategoryType": "Discretionary"},
    {"Date": "2026-01-05", "Merchant": "Air Canada - Signature Class",   "Amount": 3979.22, "CategoryType": "Discretionary"},
    {"Date": "2026-01-03", "Merchant": "Holt Renfrew",                   "Amount": 3214.10, "CategoryType": "Discretionary"},
]

DISCOVERY_BRIEF = (
    "The client's total spending over this period is approximately $73,170, "
    "split roughly 38% fixed costs ($27,700 across auto finance, property tax, insurance, utilities, "
    "telecom, and savings transfers) and 62% discretionary ($45,470 on luxury retail, travel, dining, "
    "golf, and fitness). "
    "Notable patterns include heavy recurring spend at Holt Renfrew (~$13,090 total) and frequent "
    "premium Air Canada bookings (~$13,380), suggesting a high-lifestyle profile with significant "
    "redirect potential. "
    "An advisor could propose channeling even 20% of the discretionary outflow (~$9,000/period) into "
    "a diversified growth portfolio or tax-advantaged registered account to accelerate long-term "
    "wealth accumulation."
)

# ---------------------------------------------------------------------------
# Build DataFrame
# ---------------------------------------------------------------------------
transactions_df = pd.DataFrame(TRANSACTIONS)

# ---------------------------------------------------------------------------
# Sidebar info
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Configuration")
    st.caption("Demo mode — data hardcoded from Client_Statement_Test.pdf")
    st.divider()
    st.metric("Transactions loaded", len(transactions_df))

# ---------------------------------------------------------------------------
# Advisor Dashboard: two columns
# ---------------------------------------------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Data & Insights")
    st.info(DISCOVERY_BRIEF)

    amounts = pd.to_numeric(transactions_df["Amount"], errors="coerce").fillna(0)
    total_spend = amounts.abs().sum()

    fixed = transactions_df[transactions_df["CategoryType"] == "Fixed Cost"]
    disc = transactions_df[transactions_df["CategoryType"] == "Discretionary"]
    fixed_total = pd.to_numeric(fixed["Amount"], errors="coerce").fillna(0).abs().sum()
    disc_total = pd.to_numeric(disc["Amount"], errors="coerce").fillna(0).abs().sum()

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Spend", f"${total_spend:,.2f}")
    with m2:
        st.metric("Fixed Costs", f"${fixed_total:,.2f}")
    with m3:
        st.metric("Discretionary", f"${disc_total:,.2f}")

    st.dataframe(transactions_df, use_container_width=True, height=400)

with col_right:
    st.subheader("Visualizations")

    by_cat = transactions_df.copy()
    by_cat["_abs"] = amounts.abs()
    cat_totals = by_cat.groupby("CategoryType", as_index=False)["_abs"].sum()

    fig_donut = go.Figure(
        data=[
            go.Pie(
                labels=cat_totals["CategoryType"].tolist(),
                values=cat_totals["_abs"].tolist(),
                hole=0.5,
                marker_colors=["#1f77b4", "#ff7f0e"],
            )
        ],
        layout=go.Layout(
            title="Fixed Costs vs Discretionary",
            showlegend=True,
            height=350,
            margin=dict(t=40, b=20, l=20, r=20),
        ),
    )
    st.plotly_chart(fig_donut, use_container_width=True)

    top5 = transactions_df.nlargest(5, "Amount")
    fig_bar = px.bar(
        top5,
        x="Merchant",
        y="Amount",
        title="Top 5 Largest Transactions",
        labels={"Amount": "Amount ($)", "Merchant": "Merchant"},
    )
    fig_bar.update_layout(height=350, margin=dict(t=40, b=80, l=20, r=20), xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------------------------------------------------------------
# Human-in-the-loop: Advisor authorization
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Advisor Authorization Required")
approve_clicked = st.button("Approve Analysis & Draft Investment Plan", type="primary", use_container_width=True)
if approve_clicked:
    st.success("Analysis approved. Proceeding to fiduciary review.")
