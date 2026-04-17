"""Grid Trading Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_atr


class GridTradingStrategy(BaseStrategy):
    """
    Grid Trading Strategy.

    Defines a grid of price levels around a rolling anchor (EMA).
    Emits a BUY when price crosses DOWN through a grid level below the anchor
    (accumulation on dips). Emits a SELL when price crosses UP through a grid
    level above the anchor (distribution on rallies).

    Works best in range-bound / mean-reverting regimes.
    WARNING: In strong trends this strategy accumulates against the trend —
    combine with an external trend filter in production.
    """

    def get_default_params(self) -> Dict[str, Any]:
        return {
            "atr_period": 14,
            "atr_multiplier": 1.0,   # spacing between grid levels
            "num_levels": 3,          # number of levels each side of anchor
            "anchor_period": 50,      # EMA period used as grid anchor
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        atr_period = self.params["atr_period"]
        atr_mult = self.params["atr_multiplier"]
        num_levels = self.params["num_levels"]
        anchor_period = self.params["anchor_period"]

        signals = pd.Series(0, index=df.index)
        if len(df) < max(atr_period, anchor_period) + 2:
            return signals

        atr = calculate_atr(df, atr_period)
        anchor = df["close"].ewm(span=anchor_period, adjust=False).mean()

        close = df["close"].values
        anchor_v = anchor.values
        atr_v = atr.values

        for i in range(1, len(df)):
            a = anchor_v[i]
            a_prev = anchor_v[i - 1]
            spacing = atr_v[i] * atr_mult
            if pd.isna(a) or pd.isna(spacing) or spacing <= 0:
                continue

            c = close[i]
            c_prev = close[i - 1]

            for lvl in range(1, num_levels + 1):
                buy_level = a - spacing * lvl
                buy_level_prev = a_prev - spacing * lvl
                if c_prev > buy_level_prev and c <= buy_level:
                    signals.iloc[i] = 1
                    break

                sell_level = a + spacing * lvl
                sell_level_prev = a_prev + spacing * lvl
                if c_prev < sell_level_prev and c >= sell_level:
                    signals.iloc[i] = -1
                    break

        return signals
