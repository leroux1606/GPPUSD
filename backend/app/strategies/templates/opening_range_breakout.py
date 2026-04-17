"""Opening Range Breakout (ORB) Strategy — London or NY open."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_atr


class OpeningRangeBreakoutStrategy(BaseStrategy):
    """
    Opening Range Breakout (ORB).

    One of the most robust intraday setups documented in both equities
    (Toby Crabel) and FX. Uses the first N minutes of the trading session
    as a reference range and trades a break of that range for the rest of
    the session.

    Logic:
      - On each trading day, measure the opening range over the first
        `range_minutes` minutes of the chosen session (London 07:00 GMT
        or NY 13:00 GMT by default).
      - After the range closes, go LONG on a break above with buffer,
        SHORT on a break below. One trade per day.
      - ATR filter skips days where the opening range is either too tiny
        (no liquidity) or too wide (news chaos).

    Edge rationale:
      - Professional market makers discover fair value in the first
        15-30 minutes, then participants position around that range.
      - A clean break often carries 1.5-2× the range in the same direction.
      - Works on all timeframes M5/M15 but best on M15 for GBP/USD.
    """

    def get_default_params(self) -> Dict[str, Any]:
        return {
            "session": "london",           # 'london' | 'ny'
            "range_minutes": 30,            # opening-range window
            "entry_cutoff_hour": 16,        # stop taking entries after this hour (GMT)
            "buffer_pips": 2,               # pips beyond range for confirmation
            "atr_period": 14,
            "min_range_atr_mult": 0.2,      # range must be ≥ 0.2 × ATR
            "max_range_atr_mult": 1.5,      # range must be ≤ 1.5 × ATR
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "timestamp" not in df.columns or len(df) < 50:
            return signals

        session = self.params["session"].lower()
        rng_min = self.params["range_minutes"]
        cutoff = self.params["entry_cutoff_hour"]
        buffer = self.params["buffer_pips"] * self.pip_size(df)
        min_mult = self.params["min_range_atr_mult"]
        max_mult = self.params["max_range_atr_mult"]

        # Session start in GMT minutes-of-day
        start_hour = 7 if session == "london" else 13
        start_mod = start_hour * 60
        end_mod = start_mod + rng_min

        df = df.copy()
        ts = pd.to_datetime(df["timestamp"])
        df["date"] = ts.dt.date
        df["min_of_day"] = ts.dt.hour * 60 + ts.dt.minute
        atr = calculate_atr(df, self.params["atr_period"])

        # Compute opening range per date
        in_range = (df["min_of_day"] >= start_mod) & (df["min_of_day"] < end_mod)
        or_levels = (
            df[in_range]
            .groupby("date")
            .agg(or_high=("high", "max"), or_low=("low", "min"))
        )

        traded_dates: set = set()
        hi = df["high"].values
        lo = df["low"].values
        cl = df["close"].values
        mod = df["min_of_day"].values
        dates = df["date"].values
        atr_v = atr.values

        for i in range(len(df)):
            d = dates[i]
            if d in traded_dates or d not in or_levels.index:
                continue

            # must be after range completion and before cutoff
            if mod[i] < end_mod or mod[i] >= cutoff * 60:
                continue

            or_high = or_levels.loc[d, "or_high"]
            or_low = or_levels.loc[d, "or_low"]
            rng = or_high - or_low
            a = atr_v[i]
            if pd.isna(a) or a <= 0:
                continue
            if rng < min_mult * a or rng > max_mult * a:
                continue

            if hi[i] > or_high + buffer and cl[i] > or_high:
                signals.iloc[i] = 1
                traded_dates.add(d)
            elif lo[i] < or_low - buffer and cl[i] < or_low:
                signals.iloc[i] = -1
                traded_dates.add(d)

        return signals
