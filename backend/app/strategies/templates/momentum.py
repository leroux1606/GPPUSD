"""Momentum Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_roc, calculate_rsi, calculate_adx


class MomentumStrategy(BaseStrategy):
    """
    Momentum Strategy.
    
    Buy when momentum is strong and increasing.
    Sell when momentum weakens or reverses.
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "roc_period": 10,
            "rsi_period": 14,
            "adx_period": 14,
            "adx_threshold": 25,
            "momentum_threshold": 0.5
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        roc_period = self.params["roc_period"]
        rsi_period = self.params["rsi_period"]
        adx_period = self.params["adx_period"]
        adx_threshold = self.params["adx_threshold"]
        momentum_threshold = self.params["momentum_threshold"]
        
        roc = calculate_roc(df, roc_period)
        rsi = calculate_rsi(df, rsi_period)
        adx = calculate_adx(df, adx_period)
        
        signals = pd.Series(0, index=df.index)
        
        # Buy: strong positive momentum, RSI not overbought, strong trend
        strong_momentum = roc > momentum_threshold
        rsi_ok = (rsi > 50) & (rsi < 80)
        strong_trend = adx > adx_threshold
        
        signals[strong_momentum & rsi_ok & strong_trend] = 1
        
        # Sell: negative momentum, RSI overbought
        negative_momentum = roc < -momentum_threshold
        rsi_overbought = rsi > 80
        
        signals[negative_momentum | rsi_overbought] = -1
        
        return signals

