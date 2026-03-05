"""Page 2: Equity Curve — Interactive chart with regime bands and strategy overlay."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_all_data, compute_stints
from components.charts import build_equity_curve
from components.constants import REGIME_ORDER, STRATEGY_COLORS

st.header("Equity Curve with Regime Overlay")

# Load data
with st.spinner("Loading data..."):
    data = load_all_data()

prices = data["prices"]
regimes = data["regimes"]
strategy_prices = data["strategy_prices"]

stints = compute_stints(regimes)

# ── Sidebar Controls ──
st.sidebar.subheader("Filters")

visible_regimes = st.sidebar.multiselect(
    "Highlight Regimes",
    options=REGIME_ORDER,
    default=REGIME_ORDER,
    key="equity_regime_filter",
)

available_strategies = list(strategy_prices.keys())
visible_strategies = st.sidebar.multiselect(
    "Show Strategies",
    options=available_strategies,
    default=["Nifty 50"],
    key="equity_strategy_filter",
)

# ── Chart ──
if not visible_strategies:
    st.warning("Select at least one strategy to display.")
else:
    # Remove Nifty 50 from strategy_prices dict since it's passed as `prices`
    other_strategies = {k: v for k, v in strategy_prices.items() if k != "Nifty 50"}

    fig = build_equity_curve(
        prices=prices,
        stints=stints,
        strategy_prices=other_strategies,
        visible_regimes=visible_regimes,
        visible_strategies=visible_strategies,
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Info ──
st.caption(
    f"All curves rebased to 100 at {prices.index[0].strftime('%d %b %Y')}. "
    f"Log y-axis. Regime bands colored by classification. "
    f"Use the multiselect to highlight specific regimes or strategies."
)
