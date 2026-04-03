"""NY Session Open Breakout — optimised for USD/CAD."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_atr


class NYBreakoutStrategy(BaseStrategy):
    """
    NY Session Open Breakout.

    Optimised for USD/CAD, which is the most active pair during North
    American trading hours and closely tracks the NY session.

    Logic:
    - Build the pre-NY range during the London morning (07:00–13:00 GMT)
    - At NY open (13:00), trade the breakout of that range
    - Only active in the first 2 hours of the NY session (13:00–15:00 GMT)

    Edge rationale:
    - USD/CAD volume spikes sharply at 13:30 GMT (US economic data releases)
    - The London-morning range often gets decisively broken at the NY open
    - Oil price moves (which open on NYMEX at 14:00 GMT) frequently drive CAD
    - One trade per day maximum prevents overtrading

    Works for EUR/USD and GBP/USD too but is most consistent on USD/CAD.
    """

    def get_default_params(self) -> Dict[str, Any]:
        return {
            "range_start_hour": 7,      # GMT — start of London session range
            "range_end_hour": 13,       # GMT — range complete at NY open
            "ny_open_hour": 13,         # GMT — start trading
            "ny_end_hour": 15,          # GMT — stop taking entries
            "buffer": 0.0003,           # ~3 pips
            "max_range_atr_mult": 2.0,
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
        ny_open = self.params["ny_open_hour"]
        ny_end = self.params["ny_end_hour"]
        buffer = self.params["buffer"]
        max_mult = self.params["max_range_atr_mult"]

        df["in_pre_range"] = (df["hour"] >= range_start) & (df["hour"] < range_end)
        df["in_ny_window"] = (df["hour"] >= ny_open) & (df["hour"] < ny_end)

        pre_ranges = (
            df[df["in_pre_range"]]
            .groupby("date")
            .agg(rng_high=("high", "max"), rng_low=("low", "min"))
        )

        traded_dates = set()

        for i in range(self.params["atr_period"], len(df)):
            row = df.iloc[i]
            if not row["in_ny_window"]:
                continue
            date = row["date"]
            if date in traded_dates or date not in pre_ranges.index:
                continue

            rng_high = pre_ranges.loc[date, "rng_high"]
            rng_low = pre_ranges.loc[date, "rng_low"]
            rng_size = rng_high - rng_low

            cur_atr = float(atr.iloc[i]) if not pd.isna(atr.iloc[i]) else 0.001
            if cur_atr == 0 or rng_size > cur_atr * max_mult or rng_size < 0.0005:
                continue

            close = row["close"]
            if close > rng_high + buffer:
                signals.iloc[i] = 1
                traded_dates.add(date)
            elif close < rng_low - buffer:
                signals.iloc[i] = -1
                traded_dates.add(date)

        return signals
