"""Pandas Styler formatters for gradient-colored tables."""

from __future__ import annotations

import pandas as pd

from .constants import REGIME_COLORS, REGIME_ORDER


def _return_cell_color(val: float) -> str:
    """Map ann. return value to background color CSS."""
    try:
        val = float(val)
    except (ValueError, TypeError):
        return ""
    if val >= 30:
        return "background-color: rgba(56,161,105,0.35); font-weight: 600"
    elif val >= 15:
        return "background-color: rgba(56,161,105,0.22); font-weight: 600"
    elif val >= 0:
        return "background-color: rgba(56,161,105,0.10); font-weight: 600"
    elif val >= -10:
        return "background-color: rgba(229,62,62,0.10); font-weight: 600"
    elif val >= -20:
        return "background-color: rgba(229,62,62,0.22); font-weight: 600"
    else:
        return "background-color: rgba(229,62,62,0.35); font-weight: 600"


def _dd_color(val: float) -> str:
    """Color max drawdown cells (always negative)."""
    try:
        val = float(val)
    except (ValueError, TypeError):
        return ""
    if val <= -20:
        return "color: #e53e3e; font-weight: 600"
    elif val <= -10:
        return "color: #dd6b20; font-weight: 600"
    return ""


def style_regime_stats(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    """Apply conditional formatting to regime stats DataFrame."""
    return (
        df.style
        .map(_return_cell_color, subset=["Ann. Return"])
        .map(_dd_color, subset=["Max DD"])
        .format({
            "Ann. Return": "{:+.1f}%",
            "Ann. Vol": "{:.1f}%",
            "Sharpe": "{:.2f}",
            "Max DD": "{:.1f}%",
            "Win Rate": "{:.1f}%",
            "% Time": "{:.1f}%",
            "Avg Stint": "{:.0f}",
        })
        .set_properties(**{"text-align": "center"})
        .set_properties(subset=["Regime"], **{"text-align": "left", "font-weight": "600"})
        .hide(axis="index")
    )


def build_heatmap_df(
    stats_a: pd.DataFrame, stats_b: pd.DataFrame,
    name_a: str, name_b: str,
) -> pd.DataFrame:
    """Build a comparison DataFrame with spread column for heatmap display."""
    rows = []
    for regime in REGIME_ORDER:
        match_a = stats_a[stats_a["Regime"] == regime]
        match_b = stats_b[stats_b["Regime"] == regime]
        ret_a = match_a.iloc[0]["Ann. Return"] if len(match_a) > 0 else None
        ret_b = match_b.iloc[0]["Ann. Return"] if len(match_b) > 0 else None
        spread = (ret_a - ret_b) if ret_a is not None and ret_b is not None else None
        rows.append({
            "Regime": regime,
            name_a: ret_a,
            name_b: ret_b,
            "Spread (pp)": spread,
        })
    return pd.DataFrame(rows)


def style_heatmap(df: pd.DataFrame, col_a: str, col_b: str) -> pd.io.formats.style.Styler:
    """Apply gradient coloring to the heatmap comparison table."""
    return (
        df.style
        .map(_return_cell_color, subset=[col_a, col_b])
        .format({
            col_a: "{:+.1f}%",
            col_b: "{:+.1f}%",
            "Spread (pp)": "{:+.1f}",
        }, na_rep="--")
        .set_properties(**{"text-align": "center"})
        .set_properties(subset=["Regime"], **{"text-align": "left", "font-weight": "600"})
        .hide(axis="index")
    )
