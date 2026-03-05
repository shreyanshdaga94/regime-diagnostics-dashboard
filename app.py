"""Regime Diagnostics Dashboard — Entry Point."""

import streamlit as st

st.set_page_config(
    page_title="Regime Diagnostics Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    [data-testid="stMetric"] {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        background: white;
    }
    [data-testid="stMetricValue"] { color: #1a365d; }
    .regime-legend { display: flex; flex-wrap: wrap; gap: 12px; margin: 8px 0; }
    .regime-legend-item {
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 0.85rem; font-weight: 500;
    }
    .regime-dot {
        width: 12px; height: 12px; border-radius: 50%; display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

st.title("Regime Diagnostics Dashboard")
st.caption("Layer 1 Classification — Nifty 50")

st.markdown("""
Navigate using the sidebar pages:
- **Executive Summary** — Overview stats & regime distribution
- **Equity Curve** — Interactive price chart with regime bands
- **Performance by Regime** — Detailed stats per regime per strategy
- **Strategy Comparisons** — Equity vs Gold, Momentum vs Value
- **Metric Relationship** — Decile analysis of sub-metrics vs next-day returns
""")
