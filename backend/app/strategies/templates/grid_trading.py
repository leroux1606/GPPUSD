"""Grid Trading Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_atr


class GridTradingStrategy(BaseStrategy):
    """
    Grid Trading Strategy.
    
    Places buy orders at regular intervals below current price.
    Places sell orders at regular intervals above current price.
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "grid_spacing": 0.001,  # 10 pips spacing
            "num_levels": 5,
            "atr_period": 14,
            "use_atr": True
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        grid_spacing = self.params["grid_spacing"]
        num_levels = self.params["num_levels"]
        use_atr = self.params["use_atr"]
        atr_period = self.params["atr_period"]
        
        signals = pd.Series(0, index=df.index)
        
        if use_atr:
            atr = calculate_atr(df, atr_period)
            spacing = atr * 1.5
        else:
            spacing = grid_spacing
        
        close = df['close']
        
        for i in range(num_levels, len(df)):
            current_price = close.iloc[i]
            
            # Check if price hit buy grid level
            for level in range(1, num_levels + 1):
                buy_level = current_price - (spacing.iloc[i] * level)
                if abs(current_price - buy_level) / current_price < 0.0001:
                    signals.iloc[i] = 1
                    break
            
            # Check if price hit sell grid level
            for level in range(1, num_levels + 1):
                sell_level = current_price + (spacing.iloc[i] * level)
                if abs(current_price - sell_level) / current_price < 0.0001:
                    signals.iloc[i] = -1
                    break
        
        return signals

