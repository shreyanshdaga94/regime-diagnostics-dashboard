"""Table formatters — Pandas Styler + raw HTML builders for exact HTML report replica."""

from __future__ import annotations

import numpy as np
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


# ── Raw HTML Table Builders (for exact HTML report replica) ──

def _return_bg_style(val: float) -> str:
    """Return inline CSS background for a return cell value."""
    if val >= 30:
        return "background:rgba(56,161,105,0.35); font-weight:600;"
    elif val >= 15:
        return "background:rgba(56,161,105,0.22); font-weight:600;"
    elif val >= 0:
        return "background:rgba(56,161,105,0.10); font-weight:600;"
    elif val >= -10:
        return "background:rgba(229,62,62,0.10); font-weight:600;"
    elif val >= -20:
        return "background:rgba(229,62,62,0.22); font-weight:600;"
    else:
        return "background:rgba(229,62,62,0.35); font-weight:600;"


def build_performance_html_table(regime_stats: pd.DataFrame) -> str:
    """Build raw HTML table matching the HTML report's Section 3 layout."""
    header = """<table>
    <thead><tr>
        <th>Regime</th><th>Days</th><th>% Time</th>
        <th>Ann. Return</th><th>Ann. Vol</th><th>Sharpe</th>
        <th>Max DD</th><th>Win Rate</th><th>Avg Stint</th><th>Stints</th>
    </tr></thead>
    <tbody>"""

    rows = []
    for _, row in regime_stats.iterrows():
        regime = row["Regime"]
        color = REGIME_COLORS.get(regime, "#999")
        ret = row["Ann. Return"]
        dd = row["Max DD"]

        ret_class = "positive" if ret >= 0 else "negative"
        ret_str = f"{ret:+.1f}%"

        rows.append(f"""<tr>
            <td><span class="regime-dot" style="background:{color}"></span>{regime}</td>
            <td>{int(row['Days']):,}</td>
            <td>{row['% Time']:.1f}%</td>
            <td class="{ret_class}">{ret_str}</td>
            <td>{row['Ann. Vol']:.1f}%</td>
            <td>{row['Sharpe']:.2f}</td>
            <td class="negative">{dd:.1f}%</td>
            <td>{row['Win Rate']:.1f}%</td>
            <td>{int(row['Avg Stint'])}</td>
            <td>{int(row['Stints'])}</td>
        </tr>""")

    return header + "\n".join(rows) + "</tbody></table>"


def build_heatmap_html_table(
    stats_a: pd.DataFrame,
    stats_b: pd.DataFrame,
    name_a: str,
    name_b: str,
    color_a: str,
    color_b: str,
) -> str:
    """Build raw HTML heatmap table matching HTML report Sections 4A/4B."""
    header = f"""<table>
    <thead><tr>
        <th>Regime</th>
        <th style="text-align:center;"><span style="color:{color_a};">&#9679;</span> {name_a}</th>
        <th style="text-align:center;"><span style="color:{color_b};">&#9679;</span> {name_b}</th>
        <th style="text-align:center;">Spread (pp)</th>
    </tr></thead>
    <tbody>"""

    rows = []
    for regime in REGIME_ORDER:
        match_a = stats_a[stats_a["Regime"] == regime]
        match_b = stats_b[stats_b["Regime"] == regime]
        rc = REGIME_COLORS.get(regime, "#999")

        cells = f'<td><span class="regime-dot" style="background:{rc}"></span>{regime}</td>'

        ret_a = match_a.iloc[0]["Ann. Return"] if len(match_a) > 0 else float("nan")
        ret_b = match_b.iloc[0]["Ann. Return"] if len(match_b) > 0 else float("nan")

        for ret in [ret_a, ret_b]:
            if np.isnan(ret):
                cells += '<td style="text-align:center;">&mdash;</td>'
            else:
                bg = _return_bg_style(ret)
                cells += (
                    f'<td style="text-align:center; {bg}">'
                    f'{ret:+.1f}%</td>'
                )

        if np.isnan(ret_a) or np.isnan(ret_b):
            cells += '<td style="text-align:center;">&mdash;</td>'
        else:
            spread = ret_a - ret_b
            spread_color = color_a if spread >= 0 else color_b
            cells += (
                f'<td style="text-align:center; color:{spread_color}; font-weight:700;">'
                f'{spread:+.1f}</td>'
            )

        rows.append(f"<tr>{cells}</tr>")

    return header + "\n".join(rows) + "</tbody></table>"
