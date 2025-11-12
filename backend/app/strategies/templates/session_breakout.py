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
        
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        
        for i in range(lookback, len(df)):
            current_hour = df.iloc[i]['hour']
            
            # London session breakout
            if current_hour == london_hour:
                window = df.iloc[i - lookback:i]
                high = window['high'].max()
                low = window['low'].min()
                current_price = df.iloc[i]['close']
                
                # Buy breakout above range
                if current_price > high + threshold:
                    signals.iloc[i] = 1
                # Sell breakdown below range
                elif current_price < low - threshold:
                    signals.iloc[i] = -1
            
            # NY session breakout
            elif current_hour == ny_hour:
                window = df.iloc[i - lookback:i]
                high = window['high'].max()
                low = window['low'].min()
                current_price = df.iloc[i]['close']
                
                if current_price > high + threshold:
                    signals.iloc[i] = 1
                elif current_price < low - threshold:
                    signals.iloc[i] = -1
        
        return signals

