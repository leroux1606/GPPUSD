"""Moving Average Crossover Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_sma, calculate_ema


class MACrossoverStrategy(BaseStrategy):
    """
    Moving Average Crossover Strategy.
    
    Buy when fast MA crosses above slow MA (golden cross).
    Sell when fast MA crosses below slow MA (death cross).
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "fast_period": 10,
            "slow_period": 30,
            "ma_type": "sma"  # 'sma' or 'ema'
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        fast_period = self.params["fast_period"]
        slow_period = self.params["slow_period"]
        ma_type = self.params["ma_type"]
        
        if ma_type == "ema":
            fast_ma = calculate_ema(df, fast_period)
            slow_ma = calculate_ema(df, slow_period)
        else:
            fast_ma = calculate_sma(df, fast_period)
            slow_ma = calculate_sma(df, slow_period)
        
        signals = pd.Series(0, index=df.index)
        
        # Golden cross: buy signal
        signals[(fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))] = 1
        
        # Death cross: sell signal
        signals[(fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))] = -1
        
        return signals

