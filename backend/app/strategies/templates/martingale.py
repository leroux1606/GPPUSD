"""Martingale Strategy (RISKY - Use with caution)."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy


class MartingaleStrategy(BaseStrategy):
    """
    Martingale Strategy (RISKY).
    
    Doubles position size after each loss.
    Resets after win.
    WARNING: Can lead to significant losses. Use with extreme caution.
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "base_size": 0.01,  # Base lot size
            "max_multiplier": 8,  # Maximum position size multiplier
            "trend_period": 20
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        trend_period = self.params["trend_period"]
        
        signals = pd.Series(0, index=df.index)
        ema = df['close'].ewm(span=trend_period).mean()
        
        # Simple trend following
        signals[df['close'] > ema] = 1
        signals[df['close'] < ema] = -1
        
        return signals
    
    def get_position_size_multiplier(self, consecutive_losses: int) -> float:
        """
        Calculate position size multiplier based on consecutive losses.
        
        Args:
            consecutive_losses: Number of consecutive losses
        
        Returns:
            Position size multiplier
        """
        max_mult = self.params["max_multiplier"]
        multiplier = min(2 ** consecutive_losses, max_mult)
        return multiplier

