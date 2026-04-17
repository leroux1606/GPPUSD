"""Pivot Point Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy


class PivotPointStrategy(BaseStrategy):
    """
    Pivot Point Strategy.

    Computes daily (or weekly) pivot levels from the previous full session's
    high/low/close and fires:
      - BUY when price touches a support level (S1/S2/S3) and rejects (bullish bar)
      - SELL when price touches a resistance level (R1/R2/R3) and rejects (bearish bar)

    Method can be 'standard', 'fibonacci', or 'camarilla'.
    """

    def get_default_params(self) -> Dict[str, Any]:
        return {
            "method": "standard",       # 'standard' | 'fibonacci' | 'camarilla'
            "tolerance_pips": 5,         # proximity-to-level in pips (auto-scaled per pair)
            "require_rejection": True,   # require bar close in the bounce direction
        }

    @staticmethod
    def _standard(high: float, low: float, close: float) -> Dict[str, float]:
        p = (high + low + close) / 3
        return {
            "pivot": p,
            "r1": 2 * p - low,
            "r2": p + (high - low),
            "r3": high + 2 * (p - low),
            "s1": 2 * p - high,
            "s2": p - (high - low),
            "s3": low - 2 * (high - p),
        }

    @staticmethod
    def _fibonacci(high: float, low: float, close: float) -> Dict[str, float]:
        p = (high + low + close) / 3
        d = high - low
        return {
            "pivot": p,
            "r1": p + 0.382 * d,
            "r2": p + 0.618 * d,
            "r3": p + 1.000 * d,
            "s1": p - 0.382 * d,
            "s2": p - 0.618 * d,
            "s3": p - 1.000 * d,
        }

    @staticmethod
    def _camarilla(high: float, low: float, close: float) -> Dict[str, float]:
        d = high - low
        return {
            "pivot": (high + low + close) / 3,
            "r1": close + d * 1.1 / 12,
            "r2": close + d * 1.1 / 6,
            "r3": close + d * 1.1 / 4,
            "s1": close - d * 1.1 / 12,
            "s2": close - d * 1.1 / 6,
            "s3": close - d * 1.1 / 4,
        }

    def _pivots(self, h: float, l: float, c: float) -> Dict[str, float]:
        m = self.params["method"]
        if m == "fibonacci":
            return self._fibonacci(h, l, c)
        if m == "camarilla":
            return self._camarilla(h, l, c)
        return self._standard(h, l, c)

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "timestamp" not in df.columns or len(df) < 30:
            return signals

        tol = self.params["tolerance_pips"] * self.pip_size(df)
        require_rejection = self.params["require_rejection"]

        df = df.copy()
        df["date"] = pd.to_datetime(df["timestamp"]).dt.date

        # Aggregate prior-day OHLC — today's pivots are derived from yesterday's data
        daily = df.groupby("date").agg(
            high=("high", "max"),
            low=("low", "min"),
            close=("close", "last"),
        ).shift(1)

        # Build fast lookup: date -> pivots dict
        pivot_cache: Dict[pd.Timestamp, Dict[str, float]] = {}
        for dt, row in daily.iterrows():
            if pd.isna(row["high"]):
                continue
            pivot_cache[dt] = self._pivots(row["high"], row["low"], row["close"])

        opens = df["open"].values
        highs = df["high"].values
        lows = df["low"].values
        closes = df["close"].values
        dates = df["date"].values

        for i in range(len(df)):
            pivots = pivot_cache.get(dates[i])
            if not pivots:
                continue

            o, h, l, c = opens[i], highs[i], lows[i], closes[i]

            # Support touches — look for bullish rejection
            for key in ("s1", "s2", "s3"):
                level = pivots[key]
                if l <= level + tol and h >= level - tol:
                    if not require_rejection or c > o:
                        signals.iloc[i] = 1
                        break

            if signals.iloc[i] != 0:
                continue

            # Resistance touches — look for bearish rejection
            for key in ("r1", "r2", "r3"):
                level = pivots[key]
                if h >= level - tol and l <= level + tol:
                    if not require_rejection or c < o:
                        signals.iloc[i] = -1
                        break

        return signals
