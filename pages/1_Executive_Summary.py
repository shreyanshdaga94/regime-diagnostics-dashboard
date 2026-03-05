"""Page 1: Executive Summary — Stat cards, donut chart, regime legend."""

import sys
from pathlib import Path

# Ensure components are importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_all_data, compute_stints, compute_regime_stats
from components.charts import build_donut_chart
from components.constants import REGIME_COLORS, REGIME_ORDER

st.header("Executive Summary")

# Load data
with st.spinner("Loading data..."):
    data = load_all_data()

prices = data["prices"]
regimes = data["regimes"]
labels = data["labels"]

stints = compute_stints(regimes)
regime_stats = compute_regime_stats(prices, regimes, stints)

# ── Stat Cards ──
transitions = int((regimes != regimes.shift()).sum() - 1)
canonical_rate = labels["is_canonical"].mean() * 100 if "is_canonical" in labels.columns else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Trading Days", f"{len(regimes):,}")
col2.metric("Regimes", "8")
col3.metric("Transitions", str(transitions))
col4.metric("Canonical Match Rate", f"{canonical_rate:.1f}%")

# ── Regime Legend ──
legend_html = '<div class="regime-legend">'
for regime in REGIME_ORDER:
    color = REGIME_COLORS[regime]
    legend_html += (
        f'<span class="regime-legend-item">'
        f'<span class="regime-dot" style="background:{color}"></span>'
        f'{regime}</span>'
    )
legend_html += '</div>'
st.markdown(legend_html, unsafe_allow_html=True)

# ── Layout: Donut + Table ──
col_chart, col_table = st.columns([1, 1])

with col_chart:
    st.subheader("Regime Distribution")
    fig = build_donut_chart(regime_stats)
    st.plotly_chart(fig, use_container_width=True)

with col_table:
    st.subheader("Regime Statistics")
    display_df = regime_stats[["Regime", "Days", "% Time", "Ann. Return", "Sharpe", "Stints"]].copy()
    display_df["Ann. Return"] = display_df["Ann. Return"].apply(lambda x: f"{x:+.1f}%")
    display_df["% Time"] = display_df["% Time"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── Date range info ──
st.caption(
    f"Period: {regimes.index.min().strftime('%d %b %Y')} — "
    f"{regimes.index.max().strftime('%d %b %Y')}"
)
