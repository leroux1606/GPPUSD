"""Stochastic Oscillator Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_stochastic


class StochasticStrategy(BaseStrategy):
    """
    Stochastic Oscillator Strategy.
    
    Buy when %K crosses above %D from oversold region.
    Sell when %K crosses below %D from overbought region.
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "k_period": 14,
            "d_period": 3,
            "slow_k_period": 3,
            "oversold": 20,
            "overbought": 80
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        k_period = self.params["k_period"]
        d_period = self.params["d_period"]
        slow_k = self.params["slow_k_period"]
        oversold = self.params["oversold"]
        overbought = self.params["overbought"]
        
        stoch = calculate_stochastic(df, k_period, d_period, slow_k)
        k = stoch['k']
        d = stoch['d']
        
        signals = pd.Series(0, index=df.index)
        
        # Buy: K crosses above D from oversold
        signals[(k > d) & (k.shift(1) <= d.shift(1)) & (k < oversold)] = 1
        
        # Sell: K crosses below D from overbought
        signals[(k < d) & (k.shift(1) >= d.shift(1)) & (k > overbought)] = -1
        
        return signals

