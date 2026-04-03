"""Tokyo Range Breakout Strategy — optimised for USD/JPY."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_atr


class TokyoRangeBreakoutStrategy(BaseStrategy):
    """
    Tokyo Session Range Breakout.

    Optimised for USD/JPY which is the most active pair during the Tokyo session.

    Logic:
    - Build the Tokyo session range (00:00–06:00 GMT)
    - Trade the breakout at London open (07:00–09:00 GMT) OR NY open (13:00–14:00 GMT)
    - Tokyo range on USD/JPY is typically 40–60 pips — well-defined and tradeable

    Edge rationale:
    USD/JPY accumulates institutional positioning during Tokyo hours.
    At London open the Western banks enter, often breaking the Tokyo range with conviction.
    The NY open is a second opportunity if London failed to break.

    Note on USD/JPY pip size: 1 pip = 0.01 (not 0.0001 like most pairs).
    The buffer param uses price units (0.15 = 15 pips for USD/JPY).
    """

    def get_default_params(self) -> Dict[str, Any]:
        return {
            "tokyo_start_hour": 0,      # GMT
            "tokyo_end_hour": 6,        # GMT
            "london_open_hour": 7,      # GMT — first breakout window
            "london_end_hour": 9,       # GMT
            "ny_open_hour": 13,         # GMT — second breakout window
            "ny_end_hour": 14,          # GMT
            "buffer": 0.15,             # 15 pips for USD/JPY (0.01 per pip × 15)
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
        tok_start = self.params["tokyo_start_hour"]
        tok_end = self.params["tokyo_end_hour"]
        lon_open = self.params["london_open_hour"]
        lon_end = self.params["london_end_hour"]
        ny_open = self.params["ny_open_hour"]
        ny_end = self.params["ny_end_hour"]
        buffer = self.params["buffer"]
        max_mult = self.params["max_range_atr_mult"]

        df["in_tokyo"] = (df["hour"] >= tok_start) & (df["hour"] < tok_end)
        df["in_london_break"] = (df["hour"] >= lon_open) & (df["hour"] < lon_end)
        df["in_ny_break"] = (df["hour"] >= ny_open) & (df["hour"] < ny_end)

        # Tokyo range maps to the same calendar date
        df["session_date"] = df["date"]

        tokyo_ranges = (
            df[df["in_tokyo"]]
            .groupby("session_date")
            .agg(tok_high=("high", "max"), tok_low=("low", "min"))
        )

        traded_london = set()
        traded_ny = set()

        for i in range(self.params["atr_period"], len(df)):
            row = df.iloc[i]
            in_break = (row["in_london_break"] and row["date"] not in traded_london) or \
                       (row["in_ny_break"] and row["date"] not in traded_ny)
            if not in_break:
                continue

            date = row["date"]
            if date not in tokyo_ranges.index:
                continue

            tok_high = tokyo_ranges.loc[date, "tok_high"]
            tok_low = tokyo_ranges.loc[date, "tok_low"]
            tok_range = tok_high - tok_low

            cur_atr = float(atr.iloc[i]) if not pd.isna(atr.iloc[i]) else 0.5
            # Minimum range: 20 pips (0.20 for USD/JPY), maximum: 2x ATR
            if tok_range < 0.20 or tok_range > cur_atr * max_mult:
                continue

            close = row["close"]
            is_london = row["in_london_break"]

            if close > tok_high + buffer:
                signals.iloc[i] = 1
                if is_london:
                    traded_london.add(date)
                else:
                    traded_ny.add(date)
            elif close < tok_low - buffer:
                signals.iloc[i] = -1
                if is_london:
                    traded_london.add(date)
                else:
                    traded_ny.add(date)

        return signals
