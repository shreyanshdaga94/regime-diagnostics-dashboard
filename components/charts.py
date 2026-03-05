"""Plotly chart builders — return go.Figure objects for st.plotly_chart()."""

from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

from .constants import REGIME_COLORS, REGIME_ORDER, STRATEGY_COLORS


def build_donut_chart(regime_stats: pd.DataFrame) -> go.Figure:
    """Regime distribution donut chart."""
    fig = go.Figure(data=[go.Pie(
        labels=regime_stats["Regime"].tolist(),
        values=regime_stats["Days"].tolist(),
        hole=0.5,
        marker=dict(colors=[REGIME_COLORS.get(r, "#999") for r in regime_stats["Regime"]]),
        textinfo="label+percent",
        textfont=dict(size=12),
        hovertemplate="%{label}: %{value} days (%{percent})<extra></extra>",
    )])
    fig.update_layout(
        margin=dict(t=30, b=30, l=30, r=30),
        height=400,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def build_equity_curve(
    prices: pd.Series,
    stints: pd.DataFrame,
    strategy_prices: Dict[str, pd.Series],
    visible_regimes: List[str] = None,
    visible_strategies: List[str] = None,
) -> go.Figure:
    """Equity curve with regime-colored background bands and multiple strategies."""
    if visible_regimes is None:
        visible_regimes = REGIME_ORDER
    if visible_strategies is None:
        visible_strategies = ["Nifty 50"]

    fig = go.Figure()

    # Add strategy traces
    all_strategies = {"Nifty 50": prices}
    all_strategies.update(strategy_prices)

    for name in visible_strategies:
        if name not in all_strategies:
            continue
        series = all_strategies[name].dropna()
        if len(series) == 0:
            continue
        rebased = (series / series.iloc[0]) * 100
        fig.add_trace(go.Scatter(
            x=rebased.index.tolist(),
            y=rebased.values.tolist(),
            mode="lines",
            name=name,
            line=dict(
                color=STRATEGY_COLORS.get(name, "#999"),
                width=2 if name == "Nifty 50" else 1.5,
            ),
            hovertemplate="%{x|%d %b %Y}: %{y:.1f}<extra>" + name + "</extra>",
        ))

    # Add regime background bands
    for _, stint in stints.iterrows():
        regime = stint["regime"]
        color = REGIME_COLORS.get(regime, "#999")
        opacity = 0.25 if regime in visible_regimes else 0.03
        fig.add_vrect(
            x0=stint["start"], x1=stint["end"],
            fillcolor=color, opacity=opacity,
            line_width=0, layer="below",
        )

    fig.update_layout(
        yaxis_type="log",
        yaxis_title="Rebased Value (100 = Start)",
        xaxis_title="",
        height=550,
        margin=dict(t=20, b=60, l=60, r=20),
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#e2e8f0", rangeslider=dict(visible=True, thickness=0.05)),
        yaxis=dict(gridcolor="#e2e8f0"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
            font=dict(size=12),
        ),
    )
    return fig


def build_performance_bars(regime_stats: pd.DataFrame) -> go.Figure:
    """3-panel bar charts: Return, Volatility, Sharpe."""
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=["Annualized Return (%)", "Annualized Volatility (%)", "Sharpe Ratio"],
        horizontal_spacing=0.08,
    )

    colors = [REGIME_COLORS.get(r, "#999") for r in regime_stats["Regime"]]
    regimes = regime_stats["Regime"].tolist()

    fig.add_trace(go.Bar(
        x=regimes, y=regime_stats["Ann. Return"].tolist(),
        marker_color=colors, showlegend=False,
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=regimes, y=regime_stats["Ann. Vol"].tolist(),
        marker_color=colors, showlegend=False,
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
    ), row=1, col=2)

    fig.add_trace(go.Bar(
        x=regimes, y=regime_stats["Sharpe"].tolist(),
        marker_color=colors, showlegend=False,
        hovertemplate="%{x}: %{y:.2f}<extra></extra>",
    ), row=1, col=3)

    fig.update_layout(
        height=380,
        margin=dict(t=40, b=80, l=50, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(tickangle=45, tickfont=dict(size=10))
    fig.update_yaxes(gridcolor="#e2e8f0")
    return fig


def build_pair_bar_chart(
    stats_a: pd.DataFrame, stats_b: pd.DataFrame,
    name_a: str, name_b: str,
    color_a: str, color_b: str,
) -> go.Figure:
    """Grouped bar chart comparing two strategies across regimes."""
    fig = go.Figure()
    for sdf, sname, color in [(stats_a, name_a, color_a), (stats_b, name_b, color_b)]:
        fig.add_trace(go.Bar(
            x=sdf["Regime"].tolist(),
            y=sdf["Ann. Return"].tolist(),
            name=sname,
            marker_color=color,
            hovertemplate="%{x}: %{y:+.1f}%<extra>" + sname + "</extra>",
        ))

    fig.update_layout(
        barmode="group",
        yaxis_title="Annualized Return (%)",
        height=400,
        margin=dict(t=30, b=80, l=60, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickangle=45, tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#e2e8f0", zeroline=True, zerolinecolor="#718096"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
            font=dict(size=12),
        ),
    )
    return fig


def build_spread_bar_chart(
    stats_a: pd.DataFrame, stats_b: pd.DataFrame,
    name_a: str, name_b: str,
    color_a: str, color_b: str,
) -> go.Figure:
    """Spread bar chart (A minus B) per regime, colored by winner."""
    regimes, spreads, colors = [], [], []
    for regime in REGIME_ORDER:
        match_a = stats_a[stats_a["Regime"] == regime]
        match_b = stats_b[stats_b["Regime"] == regime]
        if len(match_a) == 0 or len(match_b) == 0:
            continue
        ret_a = match_a.iloc[0]["Ann. Return"]
        ret_b = match_b.iloc[0]["Ann. Return"]
        spread = ret_a - ret_b
        regimes.append(regime)
        spreads.append(round(spread, 1))
        colors.append(color_a if spread >= 0 else color_b)

    fig = go.Figure(data=[go.Bar(
        x=regimes, y=spreads,
        marker_color=colors,
        text=[f"{s:+.1f}" for s in spreads],
        textposition="outside",
        textfont=dict(size=11),
        hovertemplate="%{x}: %{y:+.1f} pp<extra></extra>",
        showlegend=False,
    )])

    fig.update_layout(
        yaxis_title="Spread (pp)",
        height=380,
        margin=dict(t=30, b=80, l=60, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickangle=45, tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#e2e8f0", zeroline=True, zerolinecolor="#718096", zerolinewidth=2),
        annotations=[dict(
            text=f"<span style='color:{color_a}'>&#9632;</span> {name_a} wins &nbsp;&nbsp; "
                 f"<span style='color:{color_b}'>&#9632;</span> {name_b} wins",
            xref="paper", yref="paper", x=0.5, y=-0.22,
            showarrow=False, font=dict(size=11),
        )],
    )
    return fig


def build_decile_chart(ds: pd.DataFrame, metric_info: dict, color: str) -> go.Figure:
    """Dual-axis bar + line chart for decile analysis."""
    bar_colors = ["#dc2626" if r < 0 else "#16a34a" for r in ds["avg_return"]]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=ds["Decile"], y=ds["avg_return"],
        marker_color=bar_colors,
        text=[f"{r:.3%}" for r in ds["avg_return"]],
        textposition="outside",
        name="Avg Next-Day Return",
        yaxis="y",
    ))

    fig.add_trace(go.Scatter(
        x=ds["Decile"], y=ds["hit_rate"],
        mode="lines+markers",
        line=dict(color=color, width=2, dash="dot"),
        marker=dict(size=7, color=color),
        name="Hit Rate (% positive)",
        yaxis="y2",
    ))

    fig.add_hline(y=0, line_dash="dash", line_color="#d1d5db")

    fig.update_layout(
        title=dict(
            text=f"{metric_info['short_name']} — Avg Next-Day Return by Decile",
            font=dict(size=14),
        ),
        xaxis_title=f"{metric_info['short_name']} Decile (D1 = Lowest, D10 = Highest)",
        yaxis=dict(title=dict(text="Avg Next-Day Return"), tickformat=".2%", side="left"),
        yaxis2=dict(
            title=dict(text="Hit Rate"), tickformat=".0%",
            overlaying="y", side="right", range=[0.3, 0.7],
        ),
        legend=dict(x=0, y=1.12, orientation="h"),
        height=400,
        margin=dict(l=60, r=60, t=60, b=50),
        font=dict(family="Inter, system-ui, sans-serif", size=12),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig
