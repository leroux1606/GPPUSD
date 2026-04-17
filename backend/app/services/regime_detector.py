"""
Market regime detection.

Classifies the current state of a pair into one of four regimes using two
well-understood, orthogonal signals:

  - ADX (14) — measures trend strength (direction-agnostic)
  - Bollinger Band width percentile — measures volatility relative to
    recent history

Regimes:
  - "trend"    → ADX high, BB width high   → favour momentum / breakout strategies
  - "range"    → ADX low,  BB width low    → favour mean-reversion strategies
  - "squeeze"  → ADX low,  BB width ultra-low → favour breakout-anticipation
                                               (squeeze momentum, ORB)
  - "volatile" → ADX low,  BB width high   → chop / news-driven — suppress signals

Each strategy declares which regimes it prefers; the signal engine uses the
detector to filter out strategies that don't fit the current state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Dict, Set
import pandas as pd
import numpy as np

from app.technical_analysis.indicators import calculate_adx, calculate_bollinger_bands


Regime = Literal["trend", "range", "squeeze", "volatile", "unknown"]


# ── Strategy → preferred regimes ──────────────────────────────────────────────
# Strategies not listed default to all regimes (backward-compat).
STRATEGY_REGIMES: Dict[str, Set[Regime]] = {
    # Momentum / trend-following
    "ma_crossover":          {"trend"},
    "macd_signal":           {"trend"},
    "ichimoku":              {"trend"},
    "momentum":              {"trend"},
    "commodity_momentum":    {"trend"},
    "triple_screen":         {"trend"},
    "turtle":                {"trend", "volatile"},
    "keltner_pullback":      {"trend"},

    # Breakout
    "breakout":              {"trend", "squeeze", "volatile"},
    "bollinger_breakout":    {"trend", "squeeze"},
    "session_breakout":      {"trend", "squeeze", "volatile"},
    "asian_range_breakout":  {"trend", "squeeze", "volatile"},
    "eur_usd_breakout":      {"trend", "squeeze", "volatile"},
    "tokyo_range_breakout":  {"trend", "squeeze", "volatile"},
    "ny_breakout":           {"trend", "squeeze", "volatile"},
    "opening_range_breakout":{"trend", "squeeze", "volatile"},
    "squeeze_momentum":      {"squeeze", "trend"},

    # Mean-reversion / range
    "rsi_divergence":        {"range", "trend"},  # div works in both
    "stochastic":            {"range"},
    "mean_reversion":        {"range", "squeeze"},
    "range_trading":         {"range", "squeeze"},
    "vwap_bounce":           {"range", "trend"},
    "fibonacci":             {"range", "trend"},
    "support_resistance":    {"range", "trend"},
    "pivot_points":          {"range", "trend"},

    # ICT / smart-money — regime-agnostic, use session filters internally
    "fair_value_gap":        {"trend", "range", "squeeze", "volatile"},
    "order_block":           {"trend", "range"},
    "liquidity_sweep":       {"range", "volatile"},

    # Scalping / grid / martingale — always allowed (user's call)
    "scalping":              {"trend", "range", "squeeze", "volatile"},
    "grid_trading":          {"range", "squeeze"},
    "martingale":            {"trend", "range", "squeeze", "volatile"},
}


@dataclass(frozen=True)
class RegimeReading:
    regime: Regime
    adx: float
    bb_width: float
    bb_width_pct: float      # 0-1 percentile of recent BB widths
    description: str


def detect_regime(
    df: pd.DataFrame,
    *,
    adx_trend_threshold: float = 22.0,
    bb_percentile_window: int = 100,
    squeeze_percentile: float = 0.15,
    volatile_percentile: float = 0.75,
) -> RegimeReading:
    """
    Classify the current regime from the tail of an OHLC DataFrame.

    Args:
        df: OHLC DataFrame (needs at least ~60 bars)
        adx_trend_threshold: ADX above this ⇒ considered trending
        bb_percentile_window: lookback for BB-width percentile ranking
        squeeze_percentile: BB width at-or-below this percentile ⇒ squeeze
        volatile_percentile: BB width at-or-above this percentile ⇒ volatile
    """
    if len(df) < 50:
        return RegimeReading("unknown", float("nan"), float("nan"), float("nan"),
                             "insufficient data (<50 bars)")

    adx_series = calculate_adx(df, 14)
    bb = calculate_bollinger_bands(df, 20, 2.0)
    width = ((bb["upper"] - bb["lower"]) / bb["middle"].replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)

    adx_val = float(adx_series.dropna().iloc[-1]) if not adx_series.dropna().empty else float("nan")
    width_val = float(width.dropna().iloc[-1]) if not width.dropna().empty else float("nan")

    recent = width.dropna().tail(bb_percentile_window)
    if len(recent) < 20 or np.isnan(width_val):
        pct = 0.5
    else:
        pct = float((recent <= width_val).sum()) / float(len(recent))

    trending = (not np.isnan(adx_val)) and adx_val >= adx_trend_threshold

    if pct <= squeeze_percentile and not trending:
        regime: Regime = "squeeze"
        desc = f"squeeze (ADX {adx_val:.0f}, BB width {pct:.0%} pct)"
    elif trending:
        regime = "trend"
        desc = f"trending (ADX {adx_val:.0f}, BB width {pct:.0%} pct)"
    elif pct >= volatile_percentile:
        regime = "volatile"
        desc = f"volatile chop (ADX {adx_val:.0f}, BB width {pct:.0%} pct)"
    else:
        regime = "range"
        desc = f"range-bound (ADX {adx_val:.0f}, BB width {pct:.0%} pct)"

    return RegimeReading(regime, adx_val, width_val, pct, desc)


def strategy_allowed(strategy_name: str, regime: Regime) -> bool:
    """Return True if the strategy is appropriate for the current regime.
    Unknown strategies / unknown regimes default to True (don't block)."""
    if regime == "unknown":
        return True
    allowed = STRATEGY_REGIMES.get(strategy_name)
    if allowed is None:
        return True
    return regime in allowed
