"""EUR/USD Frankfurt-London Open Breakout Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_atr


class EURUSDBreakoutStrategy(BaseStrategy):
    """
    EUR/USD Frankfurt-London Open Breakout.

    EUR/USD has a distinct two-phase London open:
    - Frankfurt opens at 07:00 GMT — European price discovery begins
    - London opens at 08:00 GMT — major institutional flow arrives

    Logic:
    - Build the overnight/Frankfurt pre-range (01:00–07:00 GMT)
    - At the London open (07:00–09:00 GMT), trade a clean break of that range
    - A buffer filters noise; ATR filter skips unusually volatile days

    Edge over generic session breakout:
    EUR/USD's pre-London range (built during low-liquidity hours) is tighter
    and more reliable than the full Asian range used for GBP/USD.
    The Frankfurt-to-London transition produces strong directional follow-through.
    """

    def get_default_params(self) -> Dict[str, Any]:
        return {
            "range_start_hour": 1,      # GMT — start building range
            "range_end_hour": 7,        # GMT — range complete at Frankfurt open
            "london_open_hour": 7,      # GMT — start trading
            "london_end_hour": 10,      # GMT — stop taking new entries
            "buffer": 0.0002,           # ~2 pips (EUR/USD is tighter than GBP/USD)
            "max_range_atr_mult": 1.8,
            "atr_period": 14,
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "timestamp" not in df.columns or len(df) < 20:
            return signals

        df = df.copy()
        ts = pd.to_datetime(df["timestamp"])
        df["hour"] = ts.dt.hour
        df["date"] = ts.dt.date

        atr = calculate_atr(df, self.params["atr_period"])
        range_start = self.params["range_start_hour"]
        range_end = self.params["range_end_hour"]
        london_open = self.params["london_open_hour"]
        london_end = self.params["london_end_hour"]
        buffer = self.params["buffer"]
        max_mult = self.params["max_range_atr_mult"]

        def in_range_hours(h):
            return range_start <= h < range_end

        df["in_pre_range"] = df["hour"].apply(in_range_hours)
        df["in_london_morning"] = (df["hour"] >= london_open) & (df["hour"] < london_end)

        # Pre-range belongs to the trading day it leads into
        df["session_date"] = df["date"]

        pre_ranges = (
            df[df["in_pre_range"]]
            .groupby("session_date")
            .agg(range_high=("high", "max"), range_low=("low", "min"))
        )

        traded_dates = set()

        for i in range(self.params["atr_period"], len(df)):
            row = df.iloc[i]
            if not row["in_london_morning"]:
                continue
            date = row["session_date"]
            if date in traded_dates or date not in pre_ranges.index:
                continue

            rng_high = pre_ranges.loc[date, "range_high"]
            rng_low = pre_ranges.loc[date, "range_low"]
            rng_size = rng_high - rng_low

            cur_atr = float(atr.iloc[i]) if not pd.isna(atr.iloc[i]) else 0.001
            if cur_atr == 0 or rng_size > cur_atr * max_mult or rng_size < 0.0003:
                continue

            close = row["close"]
            if close > rng_high + buffer:
                signals.iloc[i] = 1
                traded_dates.add(date)
            elif close < rng_low - buffer:
                signals.iloc[i] = -1
                traded_dates.add(date)

        return signals
