"""Breakout Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_atr


class BreakoutStrategy(BaseStrategy):
    """
    Breakout Strategy.
    
    Buy when price breaks above recent high.
    Sell when price breaks below recent low.
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "lookback": 20,
            "atr_period": 14,
            "atr_multiplier": 1.5,
            "require_volume": True,
            "volume_threshold": 1.2
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        lookback = self.params["lookback"]
        atr_period = self.params["atr_period"]
        atr_mult = self.params["atr_multiplier"]
        require_volume = self.params["require_volume"]
        volume_threshold = self.params["volume_threshold"]
        
        atr = calculate_atr(df, atr_period)
        signals = pd.Series(0, index=df.index)
        
        # Calculate volume condition
        volume_condition = pd.Series(True, index=df.index)
        if require_volume and 'volume' in df.columns:
            avg_volume = df['volume'].rolling(window=lookback).mean()
            volume_condition = df['volume'] >= (avg_volume * volume_threshold)
        
        # Rolling high/low
        rolling_high = df['high'].rolling(window=lookback).max()
        rolling_low = df['low'].rolling(window=lookback).min()
        
        close = df['close']
        
        # Buy: break above recent high with sufficient momentum
        breakout_high = close > rolling_high.shift(1)
        sufficient_move = (close - rolling_high.shift(1)) >= (atr * atr_mult)
        signals[breakout_high & sufficient_move & volume_condition] = 1
        
        # Sell: break below recent low with sufficient momentum
        breakdown_low = close < rolling_low.shift(1)
        sufficient_move_down = (rolling_low.shift(1) - close) >= (atr * atr_mult)
        signals[breakdown_low & sufficient_move_down & volume_condition] = -1
        
        return signals

