"""VWAP Bounce Strategy — institutional intraday levels for GBP/USD."""

import pandas as pd
import numpy as np
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_rsi, calculate_atr


class VWAPBounceStrategy(BaseStrategy):
    """
    VWAP Bounce / Reversion Strategy.

    VWAP (Volume Weighted Average Price) is the single most-watched intraday
    level by institutional traders. Price frequently respects it as dynamic
    support/resistance throughout the trading day.

    Logic:
    - Calculate a rolling intraday VWAP (resets each calendar day).
    - Buy when price dips below VWAP and then closes back above it, confirmed
      by RSI coming up from oversold territory.
    - Sell when price rallies above VWAP and then closes back below it, confirmed
      by RSI coming down from overbought territory.
    - Only trade during the London/NY overlap (13:00–17:00 GMT) — highest volume.

    Edge rationale:
    - VWAP is a self-fulfilling institutional benchmark; algorithms use it for
      execution, creating reliable bounce/rejection points.
    - The London/NY overlap has the highest volume and cleanest VWAP reactions.
    - RSI confirmation filters whipsaws in strongly trending conditions.
    """

    def get_default_params(self) -> Dict[str, Any]:
        return {
            "rsi_period": 14,
            "rsi_oversold": 40,        # Slightly less strict than 30 for intraday
            "rsi_overbought": 60,      # Slightly less strict than 70 for intraday
            "session_start_hour": 13,  # London/NY overlap (GMT)
            "session_end_hour": 17,
            "atr_period": 14,
            "min_deviation_pips": 3,   # minimum distance from VWAP in pips (auto-scaled per pair)
        }

    def _calculate_daily_vwap(self, df: pd.DataFrame) -> pd.Series:
        """Calculate intraday VWAP that resets at the start of each calendar day."""
        if 'timestamp' not in df.columns:
            # Fallback: rolling VWAP over 50 bars
            typical = (df['high'] + df['low'] + df['close']) / 3
            cum_tp_vol = (typical * df['volume']).rolling(50).sum()
            cum_vol = df['volume'].rolling(50).sum()
            return cum_tp_vol / cum_vol.replace(0, np.nan)

        df = df.copy()
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        df['typical'] = (df['high'] + df['low'] + df['close']) / 3
        df['tp_vol'] = df['typical'] * df['volume']

        vwap = pd.Series(index=df.index, dtype=float)

        for date, group in df.groupby('date'):
            cum_tp_vol = group['tp_vol'].cumsum()
            cum_vol = group['volume'].cumsum()
            vwap.loc[group.index] = cum_tp_vol / cum_vol.replace(0, np.nan)

        return vwap

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)

        if len(df) < self.params["rsi_period"] + 2:
            return signals

        # Need volume for proper VWAP; skip if not available
        if 'volume' not in df.columns or df['volume'].sum() == 0:
            return signals

        vwap = self._calculate_daily_vwap(df)
        rsi = calculate_rsi(df, self.params["rsi_period"])

        rsi_oversold = self.params["rsi_oversold"]
        rsi_overbought = self.params["rsi_overbought"]
        min_dev = self.params["min_deviation_pips"] * self.pip_size(df)
        session_start = self.params["session_start_hour"]
        session_end = self.params["session_end_hour"]

        df = df.copy()
        if 'timestamp' in df.columns:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour

        close = df['close']

        for i in range(1, len(df)):
            if 'hour' in df.columns:
                h = df.iloc[i]['hour']
                if not (session_start <= h < session_end):
                    continue

            v = vwap.iloc[i]
            v_prev = vwap.iloc[i - 1]
            if pd.isna(v) or pd.isna(v_prev):
                continue

            r = rsi.iloc[i]
            if pd.isna(r):
                continue

            c = close.iloc[i]
            c_prev = close.iloc[i - 1]

            # Buy: price was below VWAP, crosses back above it, RSI was oversold
            below_then_above = c_prev < v_prev and c > v
            sufficient_deviation = abs(c_prev - v_prev) >= min_dev
            rsi_confirm_buy = r < rsi_oversold or (r < 50 and c_prev < v_prev)

            if below_then_above and sufficient_deviation and rsi_confirm_buy:
                signals.iloc[i] = 1

            # Sell: price was above VWAP, crosses back below it, RSI was overbought
            above_then_below = c_prev > v_prev and c < v
            rsi_confirm_sell = r > rsi_overbought or (r > 50 and c_prev > v_prev)

            if above_then_below and sufficient_deviation and rsi_confirm_sell:
                signals.iloc[i] = -1

        return signals
