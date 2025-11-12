"""Mean Reversion Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_bollinger_bands, calculate_rsi


class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy.
    
    Buy when price deviates significantly below mean (oversold).
    Sell when price deviates significantly above mean (overbought).
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "bb_period": 20,
            "bb_std": 2.0,
            "rsi_period": 14,
            "rsi_oversold": 30,
            "rsi_overbought": 70
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        bb_period = self.params["bb_period"]
        bb_std = self.params["bb_std"]
        rsi_period = self.params["rsi_period"]
        rsi_oversold = self.params["rsi_oversold"]
        rsi_overbought = self.params["rsi_overbought"]
        
        bb = calculate_bollinger_bands(df, bb_period, bb_std)
        rsi = calculate_rsi(df, rsi_period)
        
        close = df['close']
        signals = pd.Series(0, index=df.index)
        
        # Buy: price touches lower band and RSI oversold
        signals[(close <= bb['lower']) & (rsi < rsi_oversold)] = 1
        
        # Sell: price touches upper band and RSI overbought
        signals[(close >= bb['upper']) & (rsi > rsi_overbought)] = -1
        
        return signals

