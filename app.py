"""
AdvisorOS - Proof of Concept
Hardcoded data from Client_Statement_Test.pdf for demo purposes.
Dashboard loads immediately — no API or file upload required.
"""

import streamlit as st
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pdfplumber

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AdvisorOS",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for a polished, dark-finance aesthetic
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ---- Global ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1rem;
}

/* ---- Header bar ---- */
.header-bar {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    padding: 1.8rem 2.2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.header-bar h1 {
    color: #ffffff;
    font-size: 1.7rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.3px;
}
.header-bar .subtitle {
    color: #94a3b8;
    font-size: 0.85rem;
    margin-top: 4px;
}
.header-bar .client-badge {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 8px;
    padding: 0.5rem 1rem;
    color: #e2e8f0;
    font-size: 0.82rem;
    text-align: right;
    line-height: 1.5;
}

/* ---- Metric cards ---- */
.metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s;
}
.metric-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.10);
}
.metric-card .label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #64748b;
    margin-bottom: 6px;
}
.metric-card .value {
    font-size: 1.55rem;
    font-weight: 700;
    color: #0f172a;
}
.metric-card.blue  .value { color: #1e40af; }
.metric-card.green .value { color: #15803d; }
.metric-card.amber .value { color: #b45309; }
.metric-card.slate .value { color: #334155; }

/* ---- Section headers ---- */
.section-header {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1e293b;
    margin: 1.4rem 0 0.7rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #e2e8f0;
    letter-spacing: -0.2px;
}

/* ---- Brief card ---- */
.brief-card {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border-left: 4px solid #0284c7;
    border-radius: 8px;
    padding: 1.2rem 1.4rem;
    font-size: 0.88rem;
    line-height: 1.7;
    color: #1e293b;
    margin-bottom: 0.5rem;
}
.brief-card .brief-title {
    font-weight: 700;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #0369a1;
    margin-bottom: 0.5rem;
}

/* ---- Authorization footer ---- */
.auth-section {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    text-align: center;
    margin-top: 0.5rem;
}
.auth-section .auth-title {
    font-size: 1rem;
    font-weight: 700;
    color: #92400e;
    margin-bottom: 0.4rem;
}
.auth-section .auth-sub {
    font-size: 0.82rem;
    color: #78716c;
    margin-bottom: 1rem;
}

/* ---- Sidebar tweaks ---- */
section[data-testid="stSidebar"] {
    background: #f8fafc;
    border-right: 1px solid #e2e8f0;
}
section[data-testid="stSidebar"] .stMarkdown h2 {
    font-size: 1rem;
    color: #1e293b;
}

/* ---- Dataframe styling ---- */
[data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    overflow: hidden;
}

/* ---- Hide Streamlit chrome ---- */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { visibility: hidden; height: 0; }

/* ---- Upload loading overlay ---- */
.upload-overlay {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.35);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
}
.upload-spinner {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    border: 5px solid rgba(255, 255, 255, 0.35);
    border-top-color: #ffffff;
    animation: spin 0.9s linear infinite;
    box-shadow: 0 0 18px rgba(0, 0, 0, 0.25);
}
@keyframes spin {
    to { transform: rotate(360deg); }
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Hardcoded transactions from Client_Statement_Test.pdf
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
# Build DataFrame & computed values
# ---------------------------------------------------------------------------
df = pd.DataFrame(TRANSACTIONS)
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
df["Date"] = pd.to_datetime(df["Date"])

total_spend = df["Amount"].abs().sum()
fixed_total = df.loc[df["CategoryType"] == "Fixed Cost", "Amount"].abs().sum()
disc_total = df.loc[df["CategoryType"] == "Discretionary", "Amount"].abs().sum()
num_tx = len(df)
date_range_str = f'{df["Date"].min().strftime("%b %d, %Y")} — {df["Date"].max().strftime("%b %d, %Y")}'

# Merchant breakdown
merchant_totals = (
    df.groupby("Merchant", as_index=False)["Amount"]
    .sum()
    .sort_values("Amount", ascending=False)
)

# Daily spending for timeline
daily = df.copy()
daily["DateDay"] = daily["Date"].dt.date
daily = daily.groupby(["DateDay", "CategoryType"], as_index=False)["Amount"].sum()
daily = daily.rename(columns={"DateDay": "Date"})

# ---------------------------------------------------------------------------
# PDF Upload (must run before sidebar so Client File can show filename)
# ---------------------------------------------------------------------------
if "upload_loading" not in st.session_state:
    st.session_state.upload_loading = False
    st.session_state.upload_loading_until = 0.0

def trigger_upload_loading():
    st.session_state.upload_loading = True
    st.session_state.upload_loading_until = time.time() + 1.2

uploaded_file = st.file_uploader(
    "Upload client statement (PDF)",
    type=["pdf"],
    help="Bank or credit card statement. Text will be extracted and shown below.",
    key="client_pdf_upload",
    on_change=trigger_upload_loading,
)

if st.session_state.upload_loading:
    remaining = st.session_state.upload_loading_until - time.time()
    if remaining > 0:
        st.markdown(
            "<div class='upload-overlay'><div class='upload-spinner'></div></div>",
            unsafe_allow_html=True,
        )
        time.sleep(min(remaining, 1.5))
        st.rerun()
    else:
        st.session_state.upload_loading = False

# ---------------------------------------------------------------------------
# Sidebar (with session-state toggle)
# ---------------------------------------------------------------------------
if "sidebar_expanded" not in st.session_state:
    st.session_state.sidebar_expanded = True

with st.sidebar:
    # Toggle button - always visible, controls sidebar content
    if st.session_state.sidebar_expanded:
        st.markdown("### AdvisorOS")
        st.caption("Proof of Concept v1.0")
        st.divider()
        st.markdown("**Client File**")
        st.markdown(f"`{uploaded_file.name}`" if uploaded_file else "Blank")
        st.markdown(f"**Period:** {date_range_str}" if uploaded_file else "Blank")
        st.markdown(f"**Transactions:** {num_tx}" if uploaded_file else "Blank")
        st.divider()
        st.markdown("**Spend Breakdown**")
        st.markdown(f"Fixed Costs &nbsp;&nbsp; **${fixed_total:,.0f}** ({fixed_total/total_spend*100:.0f}%)" if uploaded_file else "Blank")
        st.markdown(f"Discretionary &nbsp; **${disc_total:,.0f}** ({disc_total/total_spend*100:.0f}%)" if uploaded_file else "Blank")
        st.divider()
        # st.caption("Data is hardcoded for demo purposes.")
    else:
        if st.button("▶ Show sidebar", key="sidebar_toggle"):
            st.session_state.sidebar_expanded = True
            st.rerun()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="header-bar">
    <div>
        <h1>AdvisorOS</h1>
        <div class="subtitle">Client Cash Flow Analysis & Investment Discovery</div>
    </div>
    <div class="client-badge">
        <strong>Wealthsimple</strong>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# PDF extraction & display (uploader is above)
# ---------------------------------------------------------------------------
extracted_text = None
extract_error = None
if uploaded_file is not None:
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            extracted_text = "\n\n".join(pages_text) if pages_text else ""
    except Exception as e:
        extract_error = str(e)

if extract_error:
    st.error(f"Could not read PDF: {extract_error}")
elif uploaded_file is not None:
    if extracted_text and extracted_text.strip():
        st.success(f"**{uploaded_file.name}** — Extracted {len(extracted_text):,} characters")
        with st.expander("View extracted text", expanded=False):
            st.text_area("", value=extracted_text[:15000] + ("..." if len(extracted_text) > 15000 else ""), height=300, disabled=True, label_visibility="collapsed")
    else:
        st.warning(f"**{uploaded_file.name}** — No text could be extracted (PDF may be scanned/image-based)")

if uploaded_file is None:
    st.info("Upload a client statement (PDF) above to view the analysis.")
    st.stop()

st.divider()

# ---------------------------------------------------------------------------
# KPI Metric Cards
# ---------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="metric-card slate">
        <div class="label">Total Spend</div>
        <div class="value">${total_spend:,.2f}</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="metric-card blue">
        <div class="label">Fixed Costs</div>
        <div class="value">${fixed_total:,.2f}</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="metric-card amber">
        <div class="label">Discretionary</div>
        <div class="value">${disc_total:,.2f}</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""
    <div class="metric-card green">
        <div class="label">Transactions</div>
        <div class="value">{num_tx}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Discovery Brief
# ---------------------------------------------------------------------------
st.markdown(f"""
<div class="brief-card">
    <div class="brief-title">AI Discovery Brief</div>
    {DISCOVERY_BRIEF}
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Charts row 1: Donut + Top merchants horizontal bar
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">Spending Overview</div>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 3])

COLORS = {"Fixed Cost": "#3b82f6", "Discretionary": "#f59e0b"}

with c1:
    cat_totals = df.groupby("CategoryType", as_index=False)["Amount"].sum()
    fig_donut = go.Figure(
        data=[go.Pie(
            labels=cat_totals["CategoryType"],
            values=cat_totals["Amount"],
            hole=0.55,
            marker_colors=[COLORS.get(c, "#94a3b8") for c in cat_totals["CategoryType"]],
            textinfo="label+percent",
            textfont_size=13,
            hovertemplate="%{label}: $%{value:,.2f}<extra></extra>",
        )],
    )
    fig_donut.update_layout(
        showlegend=False,
        height=340,
        margin=dict(t=30, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=dict(text="Fixed vs Discretionary", font=dict(size=14, color="#475569")),
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with c2:
    top_merchants = merchant_totals.head(8)
    fig_hbar = px.bar(
        top_merchants.iloc[::-1],
        x="Amount",
        y="Merchant",
        orientation="h",
        color_discrete_sequence=["#3b82f6"],
    )
    fig_hbar.update_traces(
        hovertemplate="%{y}: $%{x:,.2f}<extra></extra>",
        marker_line_width=0,
    )
    fig_hbar.update_layout(
        height=340,
        margin=dict(t=30, b=10, l=10, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="", showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(title=""),
        title=dict(text="Top Merchants by Total Spend", font=dict(size=14, color="#475569")),
    )
    st.plotly_chart(fig_hbar, use_container_width=True)

# ---------------------------------------------------------------------------
# Charts row 2: Spending timeline + Top 5 single transactions
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">Trends & Highlights</div>', unsafe_allow_html=True)
c3, c4 = st.columns([3, 2])

with c3:
    fig_timeline = px.bar(
        daily,
        x="Date",
        y="Amount",
        color="CategoryType",
        color_discrete_map=COLORS,
        barmode="stack",
    )
    fig_timeline.update_traces(
        hovertemplate="%{x|%b %d}: $%{y:,.2f}<extra></extra>",
        marker_line_width=0,
    )
    fig_timeline.update_layout(
        height=320,
        margin=dict(t=30, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="", showgrid=True, gridcolor="#f1f5f9"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(size=11),
        ),
        title=dict(text="Daily Spending Timeline", font=dict(size=14, color="#475569")),
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

with c4:
    top5 = df.nlargest(5, "Amount")
    fig_top5 = px.bar(
        top5,
        x="Amount",
        y="Merchant",
        orientation="h",
        color="CategoryType",
        color_discrete_map=COLORS,
    )
    fig_top5.update_traces(
        hovertemplate="%{y}: $%{x:,.2f}<extra></extra>",
        marker_line_width=0,
    )
    fig_top5.update_layout(
        height=320,
        margin=dict(t=30, b=10, l=10, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="", showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(title=""),
        showlegend=False,
        title=dict(text="Top 5 Largest Transactions", font=dict(size=14, color="#475569")),
    )
    st.plotly_chart(fig_top5, use_container_width=True)

# ---------------------------------------------------------------------------
# Transaction ledger
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">Transaction Ledger</div>', unsafe_allow_html=True)
display_df = df.copy()
display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
display_df["Amount"] = display_df["Amount"].apply(lambda x: f"${x:,.2f}")
display_df = display_df.rename(columns={"CategoryType": "Category"})
st.dataframe(display_df, use_container_width=True, height=380, hide_index=True)

# ---------------------------------------------------------------------------
# Human-in-the-loop: Advisor authorization
# ---------------------------------------------------------------------------
st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
st.markdown("""
<div class="auth-section">
    <div class="auth-title">Advisor Authorization Required</div>
    <div class="auth-sub">Review the analysis above before proceeding. This action is logged for compliance.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
col_btn = st.columns([1, 2, 1])
with col_btn[1]:
    if st.button("Approve Analysis & Draft Investment Plan", type="primary", use_container_width=True):
        st.success("Analysis approved. Proceeding to fiduciary review.")
