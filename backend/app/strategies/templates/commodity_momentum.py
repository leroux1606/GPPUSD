"""Commodity-Pair Momentum Strategy — AUD/USD and USD/CAD."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import (
    calculate_roc, calculate_adx, calculate_ema, calculate_atr, calculate_rsi
)


class CommodityMomentumStrategy(BaseStrategy):
    """
    Commodity-Pair Momentum Strategy.

    Designed for AUD/USD and USD/CAD — both are strongly correlated
    with commodity prices (gold/iron ore for AUD, crude oil for CAD).

    These pairs trend more cleanly than EUR/USD or GBP/USD because
    commodity cycles are slower, providing longer momentum windows.

    Logic:
    - Strong ROC (rate of change) in the direction of the trend
    - ADX confirms a real trending market (not range-bound)
    - EMA alignment: price above/below EMA50 for bias
    - RSI in healthy range (not exhausted)
    - Session filter: active session for the specific pair

    For AUD/USD: prime window is Sydney/Asian session (22:00–12:00 GMT)
    For USD/CAD: prime window is NY session (13:00–20:00 GMT)

    Configure 'prime_session' param to match the pair you're trading:
    - 'asian' for AUD/USD
    - 'ny' for USD/CAD
    - 'any' to trade all sessions
    """

    def get_default_params(self) -> Dict[str, Any]:
        return {
            "roc_period": 12,
            "roc_threshold": 0.15,    # % move required — higher = stronger signal
            "adx_period": 14,
            "adx_threshold": 22,
            "ema_period": 50,
            "rsi_period": 14,
            "rsi_min": 40,            # avoid entering into already overbought/oversold
            "rsi_max": 65,
            "prime_session": "any",   # 'asian', 'ny', 'london', 'any'
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if len(df) < 60:
            return signals

        roc = calculate_roc(df, self.params["roc_period"])
        adx = calculate_adx(df, self.params["adx_period"])
        ema = calculate_ema(df, self.params["ema_period"])
        rsi = calculate_rsi(df, self.params["rsi_period"])

        roc_thresh = self.params["roc_threshold"]
        adx_thresh = self.params["adx_threshold"]
        rsi_min = self.params["rsi_min"]
        rsi_max = self.params["rsi_max"]
        prime_session = self.params["prime_session"]

        close = df["close"]
        trending = adx > adx_thresh

        # Session filter
        session_ok = pd.Series(True, index=df.index)
        if prime_session != "any" and "timestamp" in df.columns:
            hours = pd.to_datetime(df["timestamp"]).dt.hour
            if prime_session == "asian":
                session_ok = (hours >= 22) | (hours < 12)
            elif prime_session == "ny":
                session_ok = (hours >= 13) & (hours < 21)
            elif prime_session == "london":
                session_ok = (hours >= 7) & (hours < 17)

        rsi_ok = (rsi >= rsi_min) & (rsi <= rsi_max)
        above_ema = close > ema
        below_ema = close < ema

        # Buy: positive momentum + trend + price above EMA + RSI healthy
        signals[
            (roc > roc_thresh) & trending & above_ema & rsi_ok & session_ok
        ] = 1

        # Sell: negative momentum + trend + price below EMA + RSI healthy
        signals[
            (roc < -roc_thresh) & trending & below_ema & rsi_ok & session_ok
        ] = -1

        return signals
