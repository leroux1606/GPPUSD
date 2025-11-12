"""MACD Signal Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_macd


class MACDSignalStrategy(BaseStrategy):
    """
    MACD Signal Strategy.
    
    Buy when MACD line crosses above signal line.
    Sell when MACD line crosses below signal line.
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "fast_period": 12,
            "slow_period": 26,
            "signal_period": 9
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        fast = self.params["fast_period"]
        slow = self.params["slow_period"]
        signal_period = self.params["signal_period"]
        
        macd_data = calculate_macd(df, fast, slow, signal_period)
        macd_line = macd_data['macd']
        signal_line = macd_data['signal']
        
        signals = pd.Series(0, index=df.index)
        
        # Bullish crossover
        signals[(macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))] = 1
        
        # Bearish crossover
        signals[(macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))] = -1
        
        return signals

