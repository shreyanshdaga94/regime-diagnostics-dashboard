"""Page 4: Strategy Comparisons — Equity vs Gold, Momentum vs Value."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_all_data, compute_stints, compute_regime_stats
from components.charts import build_pair_bar_chart, build_spread_bar_chart
from components.tables import build_heatmap_df, style_heatmap
from components.constants import STRATEGY_COLORS

st.header("Strategy Comparisons")

# Load data
with st.spinner("Loading data..."):
    data = load_all_data()

prices = data["prices"]
regimes = data["regimes"]
strategy_prices = data["strategy_prices"]
stints = compute_stints(regimes)

# Compute stats for all strategies
all_stats = {}
for name, series in strategy_prices.items():
    s = series.dropna()
    if len(s) == 0:
        continue
    common = s.index.intersection(regimes.index)
    s_aligned = s.loc[common]
    r_aligned = regimes.reindex(common).dropna()
    s_aligned = s_aligned.loc[r_aligned.index]
    s_stints = compute_stints(r_aligned)
    all_stats[name] = compute_regime_stats(s_aligned, r_aligned, s_stints)


# ── Tabs ──
tab1, tab2 = st.tabs(["Equity vs Gold", "Momentum vs Value"])

# ── Tab 1: Equity vs Gold ──
with tab1:
    st.subheader("Nifty 50 vs GoldBees — Annualized Returns by Regime")

    if "Nifty 50" in all_stats and "GoldBees" in all_stats:
        stats_nifty = all_stats["Nifty 50"]
        stats_gold = all_stats["GoldBees"]

        # Heatmap table
        heatmap_df = build_heatmap_df(stats_nifty, stats_gold, "Nifty 50", "GoldBees")
        styled = style_heatmap(heatmap_df, "Nifty 50", "GoldBees")
        st.dataframe(styled, use_container_width=True)

        # Charts side by side
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Grouped Comparison**")
            fig = build_pair_bar_chart(
                stats_nifty, stats_gold,
                "Nifty 50", "GoldBees",
                STRATEGY_COLORS["Nifty 50"], STRATEGY_COLORS["GoldBees"],
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Return Spread (Nifty minus Gold)**")
            fig = build_spread_bar_chart(
                stats_nifty, stats_gold,
                "Nifty 50", "GoldBees",
                STRATEGY_COLORS["Nifty 50"], STRATEGY_COLORS["GoldBees"],
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Missing data for Nifty 50 or GoldBees comparison.")

# ── Tab 2: Momentum vs Value ──
with tab2:
    st.subheader("Momentum 30 vs Value 20 — Annualized Returns by Regime")

    if "Momentum 30" in all_stats and "Value 20" in all_stats:
        stats_mom = all_stats["Momentum 30"]
        stats_val = all_stats["Value 20"]

        # Heatmap table
        heatmap_df = build_heatmap_df(stats_mom, stats_val, "Momentum 30", "Value 20")
        styled = style_heatmap(heatmap_df, "Momentum 30", "Value 20")
        st.dataframe(styled, use_container_width=True)

        # Charts side by side
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Grouped Comparison**")
            fig = build_pair_bar_chart(
                stats_mom, stats_val,
                "Momentum 30", "Value 20",
                STRATEGY_COLORS["Momentum 30"], STRATEGY_COLORS["Value 20"],
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Return Spread (Momentum minus Value)**")
            fig = build_spread_bar_chart(
                stats_mom, stats_val,
                "Momentum 30", "Value 20",
                STRATEGY_COLORS["Momentum 30"], STRATEGY_COLORS["Value 20"],
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Missing data for Momentum 30 or Value 20 comparison.")
