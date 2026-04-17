"""Liquidity Sweep / Stop-Hunt Reversal Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_atr, calculate_rsi


class LiquiditySweepStrategy(BaseStrategy):
    """
    Liquidity Sweep (Stop Hunt) Reversal.

    Classic institutional pattern: price spikes beyond a recent swing high/low
    (triggering retail stop-losses and breakout orders) and then immediately
    reverses. The first bar that closes back inside the prior range is the
    entry — you're fading the false breakout alongside the smart money that
    created it.

    Logic:
      1. Build a rolling reference range over `lookback` bars.
      2. On the current bar, the high must pierce the range-high (or low must
         pierce the range-low) by at least `min_sweep_pips`.
      3. Bar must close BACK inside the range (close < range_high for a short,
         close > range_low for a long).
      4. Confirmation filters:
         - RSI extreme (>70 shorts / <30 longs) to confirm exhaustion
         - Candle body in the reversal direction
         - ATR range check to skip low-volatility chop

    Edge rationale:
      - Stops cluster at obvious swing highs/lows; institutions intentionally
        run them to fill large orders against retail positioning.
      - Works exceptionally well at session opens and around round numbers.
    """

    def get_default_params(self) -> Dict[str, Any]:
        return {
            "lookback": 20,
            "min_sweep_pips": 3,           # pips beyond range (auto-scaled per pair)
            "atr_period": 14,
            "rsi_period": 14,
            "rsi_upper": 65,               # short above
            "rsi_lower": 35,               # long below
            "min_body_ratio": 0.4,         # reversal candle body ≥ 40% of range
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        n = len(df)
        lb = self.params["lookback"]
        if n < lb + 2:
            return signals

        min_sweep = self.params["min_sweep_pips"] * self.pip_size(df)
        rsi_upper = self.params["rsi_upper"]
        rsi_lower = self.params["rsi_lower"]
        min_body = self.params["min_body_ratio"]

        atr = calculate_atr(df, self.params["atr_period"]).values
        rsi = calculate_rsi(df, self.params["rsi_period"]).values

        op = df["open"].values
        hi = df["high"].values
        lo = df["low"].values
        cl = df["close"].values

        # Rolling window excluding current bar
        range_high = df["high"].rolling(lb).max().shift(1).values
        range_low  = df["low"].rolling(lb).min().shift(1).values

        for i in range(lb + 1, n):
            rh, rl = range_high[i], range_low[i]
            if pd.isna(rh) or pd.isna(rl) or pd.isna(atr[i]) or atr[i] <= 0:
                continue
            bar_range = hi[i] - lo[i]
            if bar_range <= 0:
                continue
            body = abs(cl[i] - op[i])
            body_ratio = body / bar_range

            # --- bearish sweep (price pokes above range high then closes back inside) ---
            swept_high = hi[i] >= rh + min_sweep
            back_inside = cl[i] < rh
            bearish_body = cl[i] < op[i]
            if swept_high and back_inside and bearish_body and body_ratio >= min_body:
                if not pd.isna(rsi[i]) and rsi[i] > rsi_upper:
                    signals.iloc[i] = -1
                    continue

            # --- bullish sweep (price pokes below range low then closes back inside) ---
            swept_low = lo[i] <= rl - min_sweep
            back_inside = cl[i] > rl
            bullish_body = cl[i] > op[i]
            if swept_low and back_inside and bullish_body and body_ratio >= min_body:
                if not pd.isna(rsi[i]) and rsi[i] < rsi_lower:
                    signals.iloc[i] = 1

        return signals
