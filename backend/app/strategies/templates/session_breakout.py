"""Session Breakout Strategy."""

import pandas as pd
from datetime import datetime, time
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy


class SessionBreakoutStrategy(BaseStrategy):
    """
    Session Breakout Strategy.
    
    Trades breakouts at London/NY session opens.
    Buy breakouts at session start, exit at session end.
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "london_open_hour": 8,  # GMT
            "ny_open_hour": 13,  # GMT
            "lookback": 30,  # Minutes
            "breakout_threshold": 0.0005
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        london_hour = self.params["london_open_hour"]
        ny_hour = self.params["ny_open_hour"]
        lookback = self.params["lookback"]
        threshold = self.params["breakout_threshold"]

        signals = pd.Series(0, index=df.index)

        if 'timestamp' not in df.columns:
            return signals

        df = df.copy()
        timestamps = pd.to_datetime(df['timestamp'])
        df['hour'] = timestamps.dt.hour
        df['date'] = timestamps.dt.date

        last_london_date = None
        last_ny_date = None

        for i in range(lookback, len(df)):
            current_hour = df.iloc[i]['hour']
            current_date = df.iloc[i]['date']

            # London session — fire only on the first bar at the open hour each day
            if current_hour == london_hour and current_date != last_london_date:
                window = df.iloc[i - lookback:i]
                high = window['high'].max()
                low = window['low'].min()
                current_price = df.iloc[i]['close']

                if current_price > high + threshold:
                    signals.iloc[i] = 1
                    last_london_date = current_date
                elif current_price < low - threshold:
                    signals.iloc[i] = -1
                    last_london_date = current_date

            # NY session — fire only on the first bar at the open hour each day
            elif current_hour == ny_hour and current_date != last_ny_date:
                window = df.iloc[i - lookback:i]
                high = window['high'].max()
                low = window['low'].min()
                current_price = df.iloc[i]['close']

                if current_price > high + threshold:
                    signals.iloc[i] = 1
                    last_ny_date = current_date
                elif current_price < low - threshold:
                    signals.iloc[i] = -1
                    last_ny_date = current_date

        return signals

