"""Data loading functions with Streamlit caching — CSV-only for cloud deployment."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
import streamlit as st

from .constants import REGIME_ORDER

# All data lives in dashboard/data/ (bundled CSVs, no external dependencies)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@st.cache_data(ttl=3600)
def load_regime_labels() -> pd.DataFrame:
    """Load regime labels from bundled CSV."""
    return pd.read_csv(DATA_DIR / "regime_labels.csv", parse_dates=["date"], index_col="date")


@st.cache_data(ttl=3600)
def load_nifty_prices() -> pd.Series:
    """Load Nifty 50 close prices from bundled CSV."""
    df = pd.read_csv(DATA_DIR / "nifty50_close.csv", parse_dates=["date"], index_col="date")
    return df["close"] if "close" in df.columns else df.iloc[:, 0]


@st.cache_data(ttl=3600)
def load_factor_prices() -> Dict[str, pd.Series]:
    """Load Momentum 30 and Value 20 portfolio values from bundled CSVs."""
    result = {}
    for name, filename in [("Momentum 30", "momentum_30.csv"), ("Value 20", "value_20.csv")]:
        df = pd.read_csv(DATA_DIR / filename, parse_dates=["date"], index_col="date")
        result[name] = df["portfolio_value"]
    return result


@st.cache_data(ttl=3600)
def load_goldbees_prices() -> pd.Series:
    """Load GoldBees close prices from bundled CSV."""
    df = pd.read_csv(DATA_DIR / "goldbees_close.csv", parse_dates=["date"], index_col="date")
    return df["close"].astype("float64")


@st.cache_data(ttl=3600)
def load_all_data() -> Dict[str, Any]:
    """Load and align all data sources. Returns a dict with all needed data."""
    prices = load_nifty_prices()
    labels = load_regime_labels()
    factor_prices = load_factor_prices()
    gold_prices = load_goldbees_prices()

    # Align on common dates
    common = prices.index.intersection(labels.index)
    prices = prices.loc[common].sort_index()
    regimes = labels.loc[common, "confirmed_regime"].sort_index()
    labels_df = labels.loc[common].sort_index()

    # Strategy prices aligned to common dates
    strategy_prices = {}
    strategy_prices["Nifty 50"] = prices
    for name, series in factor_prices.items():
        strategy_prices[name] = series.reindex(common).sort_index()
    strategy_prices["GoldBees"] = gold_prices.reindex(common).sort_index()

    return {
        "prices": prices,
        "regimes": regimes,
        "labels": labels_df,
        "strategy_prices": strategy_prices,
    }


# ── Computation Functions ──

def compute_stints(regimes: pd.Series) -> pd.DataFrame:
    """Identify contiguous regime stints."""
    changes = (regimes != regimes.shift()).cumsum()
    stints = []
    for _, group in regimes.groupby(changes):
        stints.append({
            "start": group.index[0],
            "end": group.index[-1],
            "regime": group.iloc[0],
            "duration": len(group),
        })
    return pd.DataFrame(stints)


def compute_regime_stats(
    prices: pd.Series,
    regimes: pd.Series,
    stints: pd.DataFrame,
) -> pd.DataFrame:
    """Compute per-regime performance metrics."""
    log_ret = np.log(prices / prices.shift(1)).dropna()
    total_days = len(regimes)

    rows = []
    for regime in REGIME_ORDER:
        if regime not in regimes.values:
            continue

        mask = regimes.reindex(log_ret.index) == regime
        regime_rets = log_ret[mask]
        n_days = int(mask.sum())
        if n_days == 0:
            continue

        ann_ret = regime_rets.mean() * 252
        ann_vol = regime_rets.std(ddof=1) * np.sqrt(252) if n_days > 1 else 0.0
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0.0
        win_rate = (regime_rets > 0).sum() / n_days * 100

        regime_stints = stints[stints["regime"] == regime]
        worst_dd = 0.0
        for _, stint in regime_stints.iterrows():
            stint_prices = prices.loc[stint["start"]:stint["end"]]
            if len(stint_prices) > 1:
                hwm = stint_prices.cummax()
                dd = ((stint_prices - hwm) / hwm).min()
                worst_dd = min(worst_dd, dd)

        rows.append({
            "Regime": regime,
            "Days": n_days,
            "% Time": round(n_days / total_days * 100, 1),
            "Ann. Return": round(ann_ret * 100, 1),
            "Ann. Vol": round(ann_vol * 100, 1),
            "Sharpe": round(sharpe, 2),
            "Max DD": round(worst_dd * 100, 1),
            "Win Rate": round(win_rate, 1),
            "Avg Stint": round(regime_stints["duration"].mean(), 0),
            "Stints": len(regime_stints),
        })

    return pd.DataFrame(rows)
