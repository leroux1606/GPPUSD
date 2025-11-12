"""RSI Divergence Strategy."""

import pandas as pd
import numpy as np
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_rsi


class RSIDivergenceStrategy(BaseStrategy):
    """
    RSI Divergence Strategy.
    
    Detects bullish divergence (price makes lower low, RSI makes higher low).
    Detects bearish divergence (price makes higher high, RSI makes lower high).
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "rsi_period": 14,
            "lookback": 20,
            "min_divergence_strength": 0.5
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        rsi_period = self.params["rsi_period"]
        lookback = self.params["lookback"]
        min_strength = self.params["min_divergence_strength"]
        
        rsi = calculate_rsi(df, rsi_period)
        close = df['close']
        
        signals = pd.Series(0, index=df.index)
        
        for i in range(lookback * 2, len(df)):
            # Find recent peaks and troughs
            window_price = close.iloc[i - lookback:i]
            window_rsi = rsi.iloc[i - lookback:i]
            
            # Find lowest low in window
            low_idx = window_price.idxmin()
            low_price = window_price.min()
            low_rsi = rsi.loc[low_idx]
            
            # Find previous low
            prev_window_price = close.iloc[i - lookback * 2:i - lookback]
            if len(prev_window_price) > 0:
                prev_low_idx = prev_window_price.idxmin()
                prev_low_price = prev_window_price.min()
                prev_low_rsi = rsi.loc[prev_low_idx]
                
                # Bullish divergence: lower price, higher RSI
                if low_price < prev_low_price and low_rsi > prev_low_rsi:
                    divergence_strength = (low_rsi - prev_low_rsi) / 100
                    if divergence_strength >= min_strength:
                        signals.iloc[i] = 1
            
            # Find highest high in window
            high_idx = window_price.idxmax()
            high_price = window_price.max()
            high_rsi = rsi.loc[high_idx]
            
            # Find previous high
            if len(prev_window_price) > 0:
                prev_high_idx = prev_window_price.idxmax()
                prev_high_price = prev_window_price.max()
                prev_high_rsi = rsi.loc[prev_high_idx]
                
                # Bearish divergence: higher price, lower RSI
                if high_price > prev_high_price and high_rsi < prev_high_rsi:
                    divergence_strength = (prev_high_rsi - high_rsi) / 100
                    if divergence_strength >= min_strength:
                        signals.iloc[i] = -1
        
        return signals

