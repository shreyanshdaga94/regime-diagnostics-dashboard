"""Shared constants for the Regime Diagnostics Dashboard."""

# ── Regime Colors & Order ──
REGIME_COLORS = {
    "Goldilocks": "#38a169",
    "Melt-Up": "#d69e2e",
    "Quiet Rotation": "#4299e1",
    "Compression": "#718096",
    "Slow Bleed": "#dd6b20",
    "Crisis": "#e53e3e",
    "Volatile Chop": "#805ad5",
    "Recovery": "#38b2ac",
}

REGIME_ORDER = [
    "Goldilocks", "Melt-Up", "Quiet Rotation", "Compression",
    "Slow Bleed", "Crisis", "Volatile Chop", "Recovery",
]

STRATEGY_COLORS = {
    "Nifty 50": "#1a365d",
    "Momentum 30": "#2563eb",
    "Value 20": "#dc2626",
    "GoldBees": "#d4a017",
}

# ── Metric Relationship Config ──
METRICS_CONFIG = [
    dict(
        key="rv60",
        raw_col="volatility_volatility_level_raw",
        name="RV_60 (Realized Volatility, 60d)",
        short_name="RV_60",
        description="std(daily log returns, 60d) x sqrt(252), percentile-ranked vs 252d",
    ),
    dict(
        key="breadth",
        raw_col="participation_market_breadth_raw_level",
        name="Stock Breadth (% Above 100d MA)",
        short_name="Stock Breadth",
        description="% of Nifty 50 constituents above own 100-day MA, pct-ranked vs 252d",
    ),
    dict(
        key="return_composite",
        raw_col="trend_return_composite_raw",
        name="Return Composite (Multi-Horizon)",
        short_name="Return Composite",
        description="0.2 x scored(R3M) + 0.3 x scored(R6M) + 0.5 x scored(R12M)",
    ),
]

METRIC_COLORS = ["#2563eb", "#16a34a", "#ea580c"]
