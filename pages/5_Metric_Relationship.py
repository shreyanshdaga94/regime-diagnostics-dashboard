"""Page 5: Metric Relationship Analysis — Decile analysis of 3 sub-metrics."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st
from scipy import stats

from components.data_loader import load_dashboard_csv, load_nifty_from_duckdb, decile_analysis
from components.charts import build_decile_chart
from components.constants import METRICS_CONFIG, METRIC_COLORS

st.header("Metric Relationship Analysis")
st.caption("How well do individual sub-metrics predict next-day Nifty 50 returns?")

# Load data
with st.spinner("Loading data..."):
    dashboard = load_dashboard_csv()
    nifty_db = load_nifty_from_duckdb()

# Prepare forward returns
df = dashboard.copy()
df["nifty_close"] = nifty_db
df["fwd_1d"] = df["nifty_close"].pct_change(fill_method=None).shift(-1)
n_valid = df["fwd_1d"].notna().sum()

st.markdown(
    f"**Period:** {df.index.min().strftime('%d %b %Y')} — {df.index.max().strftime('%d %b %Y')} "
    f"&nbsp;|&nbsp; **Forward horizon:** 1 trading day &nbsp;|&nbsp; "
    f"**Observations:** {n_valid:,}"
)

st.divider()

# ── Per-Metric Sections ──
for i, m in enumerate(METRICS_CONFIG):
    col = m["raw_col"]
    if col not in df.columns:
        st.warning(f"Column '{col}' not found in dashboard CSV.")
        continue

    st.subheader(f"{i + 1}. {m['name']}")
    st.caption(m["description"])

    # Decile analysis
    ds = decile_analysis(df, col)

    # Correlation stats
    v = df[[col, "fwd_1d"]].dropna()
    sp_r, sp_p = stats.spearmanr(v[col], v["fwd_1d"])
    spread = ds["avg_return"].values[-1] - ds["avg_return"].values[0]

    # Summary stats row
    scol1, scol2, scol3 = st.columns(3)
    scol1.metric("Spearman rho", f"{sp_r:.4f}")
    scol2.metric("p-value", f"{sp_p:.4f}")
    scol3.metric("D10-D1 Spread", f"{spread * 10000:+.1f} bps")

    # Chart
    fig = build_decile_chart(ds, m, METRIC_COLORS[i])
    st.plotly_chart(fig, use_container_width=True)

    # Table
    display_ds = ds[["Decile", "N", "avg_return", "median_return", "hit_rate"]].copy()
    display_ds.columns = ["Decile", "N", "Avg Return", "Median Return", "Hit Rate"]
    display_ds["Avg Return"] = display_ds["Avg Return"].apply(lambda x: f"{x * 10000:+.1f} bps")
    display_ds["Median Return"] = display_ds["Median Return"].apply(lambda x: f"{x * 10000:+.1f} bps")
    display_ds["Hit Rate"] = display_ds["Hit Rate"].apply(lambda x: f"{x:.1%}")

    st.dataframe(display_ds, use_container_width=True, hide_index=True)

    if i < len(METRICS_CONFIG) - 1:
        st.divider()
