"""Fibonacci Retracement Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_fibonacci_retracement


class FibonacciStrategy(BaseStrategy):
    """
    Fibonacci Retracement Strategy.
    
    Buy at Fibonacci support levels (38.2%, 50%, 61.8%).
    Sell at Fibonacci resistance levels.
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "lookback": 50,
            "tolerance": 0.002,
            "retracement_levels": [0.382, 0.5, 0.618]
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        lookback = self.params["lookback"]
        tolerance = self.params["tolerance"]
        levels = self.params["retracement_levels"]
        
        signals = pd.Series(0, index=df.index)
        
        for i in range(lookback, len(df)):
            window = df.iloc[i - lookback:i]
            high = window['high'].max()
            low = window['low'].min()
            
            # Determine trend
            trend = 'up' if df.iloc[i]['close'] > window['close'].iloc[-lookback // 2] else 'down'
            
            fib_levels = calculate_fibonacci_retracement(high, low, trend)
            current_price = df.iloc[i]['close']
            
            # Check if price is near Fibonacci level
            for level_name, level_price in fib_levels.items():
                if abs(current_price - level_price) / level_price <= tolerance:
                    if trend == 'up':
                        # Buy at retracement levels in uptrend
                        signals.iloc[i] = 1
                    else:
                        # Sell at retracement levels in downtrend
                        signals.iloc[i] = -1
                    break
        
        return signals

