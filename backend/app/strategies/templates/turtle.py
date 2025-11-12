"""Turtle Trading Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_atr


class TurtleStrategy(BaseStrategy):
    """
    Turtle Trading Strategy.
    
    Buy when price breaks 20-day high.
    Sell when price breaks 20-day low.
    Uses ATR for position sizing and stops.
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "entry_period": 20,
            "exit_period": 10,
            "atr_period": 14,
            "atr_multiplier": 2.0
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        entry_period = self.params["entry_period"]
        exit_period = self.params["exit_period"]
        atr_period = self.params["atr_period"]
        atr_mult = self.params["atr_multiplier"]
        
        atr = calculate_atr(df, atr_period)
        entry_high = df['high'].rolling(window=entry_period).max()
        exit_low = df['low'].rolling(window=exit_period).min()
        
        close = df['close']
        signals = pd.Series(0, index=df.index)
        
        # Buy: break above entry high
        signals[close > entry_high.shift(1)] = 1
        
        # Sell: break below exit low
        signals[close < exit_low.shift(1)] = -1
        
        return signals
    
    def get_stop_loss(self, df: pd.DataFrame, entry_price: float, entry_index: int, direction: int) -> float:
        """
        Calculate stop loss using ATR.
        
        Args:
            df: Price DataFrame
            entry_price: Entry price
            entry_index: Entry bar index
            direction: 1 for long, -1 for short
        
        Returns:
            Stop loss price
        """
        atr_period = self.params["atr_period"]
        atr_mult = self.params["atr_multiplier"]
        
        atr = calculate_atr(df, atr_period)
        current_atr = atr.iloc[entry_index] if entry_index < len(atr) else atr.iloc[-1]
        
        if direction == 1:  # Long
            return entry_price - (current_atr * atr_mult)
        else:  # Short
            return entry_price + (current_atr * atr_mult)

