"""Squeeze Momentum Strategy — John Carter's TTM Squeeze."""

import pandas as pd
import numpy as np
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import (
    calculate_bollinger_bands, calculate_keltner_channels, calculate_ema
)


class SqueezeMomentumStrategy(BaseStrategy):
    """
    TTM Squeeze Momentum (John Carter).

    Trades explosive moves out of low-volatility consolidation.

    Detection:
      - 'Squeeze' = Bollinger Bands are INSIDE the Keltner Channels
        (volatility compression). In this state no position is opened.
      - When the Bollinger Bands expand back outside the Keltner Channels,
        the squeeze 'fires' — trade the direction of momentum.

    Momentum:
      - Linear regression of (close − midline) over the period, where
        midline is the average of the highest-high/lowest-low and the SMA.

    Entry:
      - On the first bar after the squeeze releases, go LONG if momentum > 0
        and rising; SHORT if momentum < 0 and falling.
      - Trend-alignment filter: price above/below EMA200 to avoid
        counter-trend whipsaws.

    Edge rationale:
      - Volatility mean-reverts; long compressions are usually followed by
        strong directional expansions.
      - High win-rate setup across all FX pairs, especially on M15/H1.
    """

    def get_default_params(self) -> Dict[str, Any]:
        return {
            "bb_period": 20,
            "bb_std": 2.0,
            "kc_period": 20,
            "kc_mult": 1.5,
            "momentum_period": 12,
            "ema_trend_period": 200,
            "use_trend_filter": True,
        }

    @staticmethod
    def _linreg_last(series: np.ndarray, period: int) -> np.ndarray:
        """Rolling linear-regression value at the end of each window."""
        n = len(series)
        out = np.full(n, np.nan)
        if n < period:
            return out
        x = np.arange(period, dtype=float)
        x_mean = x.mean()
        x_var = ((x - x_mean) ** 2).sum()
        for i in range(period - 1, n):
            y = series[i - period + 1 : i + 1]
            if np.isnan(y).any():
                continue
            y_mean = y.mean()
            slope = ((x - x_mean) * (y - y_mean)).sum() / x_var
            intercept = y_mean - slope * x_mean
            # value at the latest x (= period-1)
            out[i] = intercept + slope * (period - 1)
        return out

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        n = len(df)
        mom_p = self.params["momentum_period"]
        if n < max(self.params["bb_period"], self.params["kc_period"]) + mom_p + 5:
            return signals

        bb = calculate_bollinger_bands(df, self.params["bb_period"], self.params["bb_std"])
        kc_cols = calculate_keltner_channels(df, self.params["kc_period"], self.params["kc_mult"])
        bb_upper = bb["upper"].values
        bb_lower = bb["lower"].values
        kc_upper = kc_cols.iloc[:, 0].values  # KCUe
        kc_lower = kc_cols.iloc[:, 2].values  # KCLe

        # Squeeze state: True when BB inside KC
        in_squeeze = (bb_upper < kc_upper) & (bb_lower > kc_lower)

        # Momentum: close − midline, then linear regression smoothing
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        hh = pd.Series(high).rolling(mom_p).max().values
        ll = pd.Series(low).rolling(mom_p).min().values
        sma = pd.Series(close).rolling(mom_p).mean().values
        midline = (hh + ll) / 2
        basis = (midline + sma) / 2
        mom_raw = close - basis
        mom = self._linreg_last(mom_raw, mom_p)

        use_trend = self.params["use_trend_filter"]
        ema = calculate_ema(df, self.params["ema_trend_period"]).values

        prev_squeeze = False
        for i in range(1, n):
            cur_sq = bool(in_squeeze[i]) if not np.isnan(bb_upper[i]) else False
            # Squeeze just fired (transition True → False)
            fired = prev_squeeze and not cur_sq
            prev_squeeze = cur_sq

            if not fired or np.isnan(mom[i]):
                continue

            rising = mom[i] > mom[i - 1]
            falling = mom[i] < mom[i - 1]

            if use_trend and not np.isnan(ema[i]):
                trend_up = close[i] > ema[i]
                trend_dn = close[i] < ema[i]
            else:
                trend_up = trend_dn = True

            if mom[i] > 0 and rising and trend_up:
                signals.iloc[i] = 1
            elif mom[i] < 0 and falling and trend_dn:
                signals.iloc[i] = -1

        return signals
