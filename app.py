"""Regime Diagnostics Dashboard — Single-page replica of the HTML report."""

import sys
from datetime import datetime
from pathlib import Path

# Ensure components are importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from components.data_loader import load_all_data, compute_stints, compute_regime_stats
from components.charts import (
    build_donut_chart,
    build_equity_curve,
    build_performance_bars,
    build_pair_bar_chart,
    build_spread_bar_chart,
)
from components.tables import build_performance_html_table, build_heatmap_html_table
from components.constants import REGIME_COLORS, REGIME_ORDER, STRATEGY_COLORS

# ── Page Config ──
st.set_page_config(
    page_title="Layer 1 Implementation Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Password Protection ──
def _check_password() -> bool:
    """Gate the app behind a simple password prompt."""
    if st.session_state.get("authenticated"):
        return True

    try:
        correct_pw = st.secrets["password"]
    except (FileNotFoundError, KeyError):
        st.error("Dashboard password not configured. Set 'password' in Streamlit secrets.")
        st.stop()
        return False

    st.markdown(
        """<div style="display:flex;align-items:center;justify-content:center;
        min-height:60vh;"><div style="text-align:center;max-width:400px;width:100%;">
        <h2 style="color:#1a365d;margin-bottom:8px;">Regime Diagnostics Dashboard</h2>
        <p style="color:#4a5568;margin-bottom:24px;">Enter password to continue</p>
        </div></div>""",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        pwd = st.text_input("Password", type="password", key="pwd_input")
        if st.button("Login", use_container_width=True, type="primary"):
            if pwd == correct_pw:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    return False


if not _check_password():
    st.stop()

# ── Custom CSS ──
st.markdown("""
<style>
:root {
    --navy: #1a365d;
    --navy-light: #2a4a7f;
    --text: #1a202c;
    --text-secondary: #4a5568;
    --border: #e2e8f0;
    --bg: #f7fafc;
    --white: #ffffff;
}

/* Hide Streamlit chrome */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }

/* Container width */
[data-testid="stAppViewBlockContainer"] {
    max-width: 1200px;
    padding: 0 24px;
}

/* Navy header */
.dashboard-header {
    background: var(--navy);
    color: white;
    padding: 28px 40px;
    text-align: center;
    margin: -1rem -1rem 0 -1rem;
}
.dashboard-header h1 {
    font-size: 26px; font-weight: 700; margin: 0 0 4px 0; color: white;
}
.dashboard-header .subtitle {
    font-size: 13px; opacity: 0.7; margin: 0;
}

/* Section headers */
.section-header {
    font-size: 20px;
    font-weight: 700;
    color: var(--navy);
    border-bottom: 2px solid var(--navy);
    padding-bottom: 8px;
    margin: 36px 0 24px 0;
}

/* Stat cards */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 28px;
}
.stat-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.stat-value { font-size: 28px; font-weight: 700; color: var(--navy); }
.stat-label { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }

/* Regime legend */
.legend {
    display: flex; flex-wrap: wrap; gap: 14px;
    justify-content: center; margin: 16px 0;
}
.legend-item {
    display: flex; align-items: center; gap: 5px;
    font-size: 12px; font-weight: 600; color: var(--text);
}
.legend-swatch {
    width: 14px; height: 14px; border-radius: 3px; flex-shrink: 0;
}

/* Chart box */
.chart-box {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.chart-box .chart-title {
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 600;
    color: var(--navy);
    border-bottom: 1px solid var(--border);
}

/* Tables */
.chart-box table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.chart-box th {
    background: var(--navy) !important;
    color: var(--white) !important;
    padding: 8px 12px;
    text-align: left;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.chart-box td {
    padding: 7px 12px;
    border-bottom: 1px solid var(--border);
    color: var(--text);
}
.chart-box tr:nth-child(even) td { background: var(--bg); }
.chart-box tr:hover td { background: #edf2f7; }

.positive { color: #38a169 !important; font-weight: 600; }
.negative { color: #e53e3e !important; font-weight: 600; }

.regime-dot {
    display: inline-block;
    width: 10px; height: 10px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
}

/* Footer */
.dashboard-footer {
    text-align: center;
    padding: 24px;
    font-size: 11px;
    color: var(--text-secondary);
    border-top: 1px solid var(--border);
    margin-top: 20px;
}

/* Override st.pills to look more chip-like */
[data-testid="stPills"] button {
    border-radius: 20px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}

/* Responsive */
@media (max-width: 768px) {
    .stat-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
""", unsafe_allow_html=True)

# ── Load All Data ──
with st.spinner("Loading data..."):
    data = load_all_data()

prices = data["prices"]
regimes = data["regimes"]
labels = data["labels"]
strategy_prices = data["strategy_prices"]
stints = compute_stints(regimes)

# Pre-compute all strategy stats
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

date_start = regimes.index.min().strftime("%d %b %Y")
date_end = regimes.index.max().strftime("%d %b %Y")
n_days = len(regimes)
transitions = int((regimes != regimes.shift()).sum() - 1)
canonical_rate = labels["is_canonical"].mean() * 100 if "is_canonical" in labels.columns else 0
nifty_stats = all_stats.get("Nifty 50", compute_regime_stats(prices, regimes, stints))
all_strategy_names = list(strategy_prices.keys())

# ═══════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════
st.markdown(f"""
<div class="dashboard-header">
    <h1>Layer 1 Implementation Dashboard</h1>
    <p class="subtitle">Layer 1 Classification &mdash; {date_start} to {date_end} &mdash; {n_days:,} Trading Days</p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# SECTION 1: EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-header">1. Executive Summary</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="stat-grid">
    <div class="stat-card"><div class="stat-value">{n_days:,}</div><div class="stat-label">Trading Days</div></div>
    <div class="stat-card"><div class="stat-value">{regimes.nunique()}</div><div class="stat-label">Regimes Identified</div></div>
    <div class="stat-card"><div class="stat-value">{transitions}</div><div class="stat-label">Regime Transitions</div></div>
    <div class="stat-card"><div class="stat-value">{canonical_rate:.1f}%</div><div class="stat-label">Canonical Match Rate</div></div>
</div>
""", unsafe_allow_html=True)

# Regime legend
legend_items = "".join(
    f'<span class="legend-item">'
    f'<span class="legend-swatch" style="background:{REGIME_COLORS[r]}"></span>{r}</span>'
    for r in REGIME_ORDER
)
st.markdown(f'<div class="legend">{legend_items}</div>', unsafe_allow_html=True)

# Donut chart — full width
st.markdown(
    '<div class="chart-box"><div class="chart-title">Regime Distribution (% of Time)</div></div>',
    unsafe_allow_html=True,
)
fig = build_donut_chart(nifty_stats)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════
# SECTION 2: EQUITY CURVE
# ═══════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">2. Equity Curve with Regime Overlay</div>',
    unsafe_allow_html=True,
)

# Regime filter chips
selected_regimes = st.pills(
    "Highlight Regimes",
    options=list(REGIME_ORDER),
    default=list(REGIME_ORDER),
    selection_mode="multi",
    key="regime_filter_pills",
    label_visibility="collapsed",
)
visible_regimes = list(selected_regimes) if selected_regimes else list(REGIME_ORDER)

# Strategy toggle chips
st.markdown(
    '<div style="text-align:center; font-size:12px; color:#4a5568; margin:4px 0 8px 0;">'
    "Click to show/hide strategies</div>",
    unsafe_allow_html=True,
)
selected_strategies = st.pills(
    "Show Strategies",
    options=all_strategy_names,
    default=["Nifty 50"],
    selection_mode="multi",
    key="strategy_toggle_pills",
    label_visibility="collapsed",
)
if not selected_strategies:
    selected_strategies = ["Nifty 50"]

# Equity curve chart
other_strats = {k: v for k, v in strategy_prices.items() if k != "Nifty 50"}
fig = build_equity_curve(prices, stints, other_strats, visible_regimes, selected_strategies)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════
# SECTION 3: PERFORMANCE BY REGIME
# ═══════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">3. Performance by Regime</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div style="text-align:center; font-size:14px; font-weight:600; color:#1a365d; margin-bottom:8px;">'
    "Which strategy do you want the dashboard to reflect?</div>",
    unsafe_allow_html=True,
)

perf_strategy = st.pills(
    "Select Strategy",
    options=all_strategy_names,
    default="Nifty 50",
    selection_mode="single",
    key="perf_strategy_pills",
    label_visibility="collapsed",
)
if perf_strategy is None:
    perf_strategy = "Nifty 50"

regime_stats = all_stats.get(perf_strategy)
if regime_stats is not None and len(regime_stats) > 0:
    # HTML performance table
    table_html = build_performance_html_table(regime_stats)
    st.markdown(
        f'<div class="chart-box" style="overflow-x:auto;">{table_html}</div>',
        unsafe_allow_html=True,
    )

    # Bar chart with title
    st.markdown(
        f'<div class="chart-box"><div class="chart-title">'
        f"Return, Volatility &amp; Sharpe by Regime &mdash; {perf_strategy}"
        f"</div></div>",
        unsafe_allow_html=True,
    )
    fig = build_performance_bars(regime_stats)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════
# SECTION 4A: EQUITY VS GOLD
# ═══════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">4A. Equity vs Gold</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-size:13px; color:#4a5568; margin:-12px 0 20px 0;">'
    "Nifty 50 vs GoldBees annualized returns by regime. "
    "Spread = Nifty 50 minus GoldBees (negative &rarr; gold outperforms).</p>",
    unsafe_allow_html=True,
)

if "Nifty 50" not in all_stats or "GoldBees" not in all_stats:
    st.info("GoldBees data unavailable — Section 4A skipped.")

if "Nifty 50" in all_stats and "GoldBees" in all_stats:
    stats_nifty = all_stats["Nifty 50"]
    stats_gold = all_stats["GoldBees"]

    heatmap_html = build_heatmap_html_table(
        stats_nifty, stats_gold, "Nifty 50", "GoldBees",
        STRATEGY_COLORS["Nifty 50"], STRATEGY_COLORS["GoldBees"],
    )
    st.markdown(
        f'<div class="chart-box" style="overflow-x:auto;">'
        f'<div class="chart-title">Annualized Return by Regime</div>'
        f"{heatmap_html}</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            '<div class="chart-box"><div class="chart-title">Side-by-Side Returns</div></div>',
            unsafe_allow_html=True,
        )
        fig = build_pair_bar_chart(
            stats_nifty, stats_gold, "Nifty 50", "GoldBees",
            STRATEGY_COLORS["Nifty 50"], STRATEGY_COLORS["GoldBees"],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with col2:
        st.markdown(
            '<div class="chart-box"><div class="chart-title">'
            "Return Spread (Nifty 50 minus GoldBees)</div></div>",
            unsafe_allow_html=True,
        )
        fig = build_spread_bar_chart(
            stats_nifty, stats_gold, "Nifty 50", "GoldBees",
            STRATEGY_COLORS["Nifty 50"], STRATEGY_COLORS["GoldBees"],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════
# SECTION 4B: MOMENTUM VS VALUE
# ═══════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">4B. Factor Comparison: Momentum vs Value</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-size:13px; color:#4a5568; margin:-12px 0 20px 0;">'
    "Momentum 30 vs Value 20 annualized returns by regime. "
    "Spread = Momentum minus Value (positive &rarr; momentum outperforms).</p>",
    unsafe_allow_html=True,
)

if "Momentum 30" not in all_stats or "Value 20" not in all_stats:
    st.info("Factor data unavailable — Section 4B skipped.")

if "Momentum 30" in all_stats and "Value 20" in all_stats:
    stats_mom = all_stats["Momentum 30"]
    stats_val = all_stats["Value 20"]

    heatmap_html = build_heatmap_html_table(
        stats_mom, stats_val, "Momentum 30", "Value 20",
        STRATEGY_COLORS["Momentum 30"], STRATEGY_COLORS["Value 20"],
    )
    st.markdown(
        f'<div class="chart-box" style="overflow-x:auto;">'
        f'<div class="chart-title">Annualized Return by Regime</div>'
        f"{heatmap_html}</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            '<div class="chart-box"><div class="chart-title">Side-by-Side Returns</div></div>',
            unsafe_allow_html=True,
        )
        fig = build_pair_bar_chart(
            stats_mom, stats_val, "Momentum 30", "Value 20",
            STRATEGY_COLORS["Momentum 30"], STRATEGY_COLORS["Value 20"],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with col2:
        st.markdown(
            '<div class="chart-box"><div class="chart-title">'
            "Return Spread (Momentum minus Value)</div></div>",
            unsafe_allow_html=True,
        )
        fig = build_spread_bar_chart(
            stats_mom, stats_val, "Momentum 30", "Value 20",
            STRATEGY_COLORS["Momentum 30"], STRATEGY_COLORS["Value 20"],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════
now = datetime.now().strftime("%d %b %Y, %H:%M")
st.markdown(
    f'<div class="dashboard-footer">'
    f"Generated on {now} &mdash; Regime Diagnostics Framework, Layer 1"
    f"</div>",
    unsafe_allow_html=True,
)
