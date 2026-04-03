"""Asian Range Breakout Strategy — optimised for GBP/USD."""

import pandas as pd
import numpy as np
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_atr


class AsianRangeBreakoutStrategy(BaseStrategy):
    """
    Asian Range Breakout Strategy.

    One of the highest-probability setups for GBP/USD intraday.

    Logic:
    - Build the Asian session range (22:00–07:00 GMT).
    - At London open (07:00–10:00 GMT), trade a clean breakout of that range.
    - A 'buffer' above/below the range filters false breakouts.
    - ATR confirms that the range was not unusually wide (avoids low-probability days).

    Edge rationale:
    - During the Asian session GBP/USD is range-bound with thin liquidity.
    - At London open large institutional flows either respect or break that range.
    - Breakouts of well-defined Asian ranges have historically high follow-through.
    """

    def get_default_params(self) -> Dict[str, Any]:
        return {
            "asian_start_hour": 22,    # GMT — Asia/Sydney open
            "asian_end_hour": 7,       # GMT — London open
            "london_end_hour": 10,     # GMT — stop trading after London morning
            "buffer": 0.0003,          # ~3 pips above/below range for confirmed break
            "max_range_atr_mult": 2.0, # Skip day if Asian range > 2x ATR (avoid chaotic days)
            "atr_period": 14,
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)

        if 'timestamp' not in df.columns:
            return signals

        df = df.copy()
        timestamps = pd.to_datetime(df['timestamp'])
        df['hour'] = timestamps.dt.hour
        df['date'] = timestamps.dt.date

        atr = calculate_atr(df, self.params["atr_period"])
        asian_start = self.params["asian_start_hour"]
        asian_end = self.params["asian_end_hour"]
        london_end = self.params["london_end_hour"]
        buffer = self.params["buffer"]
        max_range_mult = self.params["max_range_atr_mult"]

        # Build Asian range per calendar date
        # Asian session spans midnight: rows where hour >= 22 OR hour < 7
        def is_asian(h):
            return h >= asian_start or h < asian_end

        df['is_asian'] = df['hour'].apply(is_asian)
        df['is_london_morning'] = (df['hour'] >= asian_end) & (df['hour'] < london_end)

        # Group Asian sessions: use the *next* trading date as the key
        # (bars at 22:00 on Mon belong to the Tue London session)
        df['session_date'] = df.apply(
            lambda r: (r['date'] + pd.Timedelta(days=1)) if r['hour'] >= asian_start else r['date'],
            axis=1
        )

        asian_ranges = (
            df[df['is_asian']]
            .groupby('session_date')
            .agg(asian_high=('high', 'max'), asian_low=('low', 'min'))
        )

        traded_dates = set()

        for i in range(self.params["atr_period"], len(df)):
            row = df.iloc[i]
            if not row['is_london_morning']:
                continue

            session_date = row['session_date']
            if session_date in traded_dates:
                continue
            if session_date not in asian_ranges.index:
                continue

            asian_high = asian_ranges.loc[session_date, 'asian_high']
            asian_low = asian_ranges.loc[session_date, 'asian_low']
            asian_range = asian_high - asian_low

            # Skip if range is too wide relative to ATR (erratic day)
            current_atr = atr.iloc[i]
            if pd.isna(current_atr) or current_atr == 0:
                continue
            if asian_range > current_atr * max_range_mult:
                continue
            # Also skip if range is tiny (< 5 pips) — likely weekend/holiday gap
            if asian_range < 0.0005:
                continue

            close = row['close']

            if close > asian_high + buffer:
                signals.iloc[i] = 1
                traded_dates.add(session_date)
            elif close < asian_low - buffer:
                signals.iloc[i] = -1
                traded_dates.add(session_date)

        return signals
