"""Keltner Pullback Trend-Continuation Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import (
    calculate_ema, calculate_keltner_channels, calculate_adx, calculate_rsi
)


class KeltnerPullbackStrategy(BaseStrategy):
    """
    Keltner Pullback Trend-Continuation.

    A high-quality trend-following entry: in a strong, established trend
    you don't chase — you wait for a shallow pullback to the mean.

    Logic:
      - Trend: ADX > threshold AND price persistently above/below EMA50.
      - Pullback: price retraces to the Keltner Channel MIDLINE (EMA20)
        or between midline and lower/upper channel.
      - Trigger: a bullish (or bearish) bar closes back in the trend
        direction — a 'hammer' off the mean in an uptrend.
      - RSI filter to avoid entering when momentum has flipped.

    Entry:
      - BUY  pullback to Keltner mid during an uptrend (ADX high, close >
        EMA50, last bar bullish, RSI > 45)
      - SELL pullback to Keltner mid during a downtrend (symmetric)

    Edge rationale:
      - Trends persist longer than most retail traders believe; pullback
        entries produce excellent R:R — stop beyond the Keltner lower band,
        target the previous swing high.
      - Avoids the late-entry problem of pure breakout systems.
    """

    def get_default_params(self) -> Dict[str, Any]:
        return {
            "ema_trend": 50,
            "keltner_period": 20,
            "keltner_mult": 2.0,
            "adx_period": 14,
            "adx_min": 22,
            "rsi_period": 14,
            "rsi_long_min": 45,
            "rsi_short_max": 55,
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        n = len(df)
        if n < 60:
            return signals

        ema_trend = calculate_ema(df, self.params["ema_trend"]).values
        kc = calculate_keltner_channels(df, self.params["keltner_period"], self.params["keltner_mult"])
        kc_mid = kc.iloc[:, 1].values   # KCBe (middle = EMA)
        kc_up = kc.iloc[:, 0].values
        kc_lo = kc.iloc[:, 2].values
        adx = calculate_adx(df, self.params["adx_period"]).values
        rsi = calculate_rsi(df, self.params["rsi_period"]).values

        op = df["open"].values
        hi = df["high"].values
        lo = df["low"].values
        cl = df["close"].values

        adx_min = self.params["adx_min"]
        r_long = self.params["rsi_long_min"]
        r_short = self.params["rsi_short_max"]

        for i in range(1, n):
            if pd.isna(adx[i]) or pd.isna(kc_mid[i]) or pd.isna(ema_trend[i]):
                continue
            if adx[i] < adx_min:
                continue

            trend_up = cl[i] > ema_trend[i] and cl[i - 1] > ema_trend[i - 1]
            trend_dn = cl[i] < ema_trend[i] and cl[i - 1] < ema_trend[i - 1]

            # BUY: touched mid (or below mid) and closed back above it
            if trend_up and lo[i] <= kc_mid[i] and cl[i] > kc_mid[i] and cl[i] > op[i]:
                # Not already extended to upper band
                if cl[i] < kc_up[i] and (pd.isna(rsi[i]) or rsi[i] >= r_long):
                    signals.iloc[i] = 1
                    continue

            # SELL: touched mid (or above mid) and closed back below it
            if trend_dn and hi[i] >= kc_mid[i] and cl[i] < kc_mid[i] and cl[i] < op[i]:
                if cl[i] > kc_lo[i] and (pd.isna(rsi[i]) or rsi[i] <= r_short):
                    signals.iloc[i] = -1

        return signals
