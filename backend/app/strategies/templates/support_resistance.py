"""Support/Resistance Bounce Strategy."""

import pandas as pd
import numpy as np
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.patterns import detect_support_resistance


class SupportResistanceStrategy(BaseStrategy):
    """
    Support/Resistance Bounce Strategy.
    
    Buy when price bounces off support level.
    Sell when price bounces off resistance level.
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "lookback": 50,
            "tolerance": 0.002,  # 0.2% tolerance for level matching
            "bounce_threshold": 0.0005  # Minimum bounce distance
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        lookback = self.params["lookback"]
        tolerance = self.params["tolerance"]
        bounce_threshold = self.params["bounce_threshold"]
        
        signals = pd.Series(0, index=df.index)
        
        for i in range(lookback, len(df)):
            window = df.iloc[i - lookback:i]
            sr_levels = detect_support_resistance(window, window=20, tolerance=tolerance)
            
            current_price = df.iloc[i]['close']
            prev_price = df.iloc[i - 1]['close']
            
            # Check support bounce
            for support in sr_levels['support']:
                if abs(current_price - support) / support <= tolerance:
                    # Price bounced up from support
                    if current_price > prev_price and (current_price - support) >= bounce_threshold:
                        signals.iloc[i] = 1
                        break
            
            # Check resistance bounce
            for resistance in sr_levels['resistance']:
                if abs(current_price - resistance) / resistance <= tolerance:
                    # Price bounced down from resistance
                    if current_price < prev_price and (resistance - current_price) >= bounce_threshold:
                        signals.iloc[i] = -1
                        break
        
        return signals

