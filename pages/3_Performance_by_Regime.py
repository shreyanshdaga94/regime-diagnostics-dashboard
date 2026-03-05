"""Page 3: Performance by Regime — Tables and bar charts per strategy."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import streamlit as st

from components.data_loader import load_all_data, compute_stints, compute_regime_stats
from components.charts import build_performance_bars
from components.tables import style_regime_stats
from components.constants import REGIME_ORDER

st.header("Performance by Regime")

# Load data
with st.spinner("Loading data..."):
    data = load_all_data()

prices = data["prices"]
regimes = data["regimes"]
strategy_prices = data["strategy_prices"]
stints = compute_stints(regimes)

# ── Strategy Selector ──
strategy_name = st.selectbox(
    "Select Strategy",
    options=list(strategy_prices.keys()),
    index=0,
    key="perf_strategy_select",
)

# Compute stats for selected strategy
if strategy_name == "Nifty 50":
    strat_prices = prices
else:
    strat_prices = strategy_prices[strategy_name].dropna()
    # Re-align regimes to this strategy's available dates
    common = strat_prices.index.intersection(regimes.index)
    strat_prices = strat_prices.loc[common]

# Use the same regimes aligned to the strategy's dates
strat_regimes = regimes.reindex(strat_prices.index).dropna()
strat_prices = strat_prices.loc[strat_regimes.index]
strat_stints = compute_stints(strat_regimes)

regime_stats = compute_regime_stats(strat_prices, strat_regimes, strat_stints)

if len(regime_stats) == 0:
    st.warning("No regime data available for this strategy.")
else:
    # ── Styled Table ──
    st.subheader(f"{strategy_name} — Per-Regime Statistics")
    styled = style_regime_stats(regime_stats)
    st.dataframe(styled, use_container_width=True)

    # ── Bar Charts ──
    st.subheader(f"{strategy_name} — Return, Volatility & Sharpe by Regime")
    fig = build_performance_bars(regime_stats)
    st.plotly_chart(fig, use_container_width=True)
