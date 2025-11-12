"""Pivot Point Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_pivot_points


class PivotPointStrategy(BaseStrategy):
    """
    Pivot Point Strategy.
    
    Buy at pivot support levels.
    Sell at pivot resistance levels.
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "method": "standard",  # 'standard', 'fibonacci', 'camarilla'
            "tolerance": 0.0005
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        method = self.params["method"]
        tolerance = self.params["tolerance"]
        
        signals = pd.Series(0, index=df.index)
        
        for i in range(1, len(df)):
            # Calculate pivot points for previous day
            prev_day = df.iloc[max(0, i-1):i]
            if len(prev_day) > 0:
                pivots = calculate_pivot_points(prev_day, method)
                
                if len(pivots) > 0:
                    current_price = df.iloc[i]['close']
                    pivot = pivots['pivot'].iloc[0]
                    
                    # Get support and resistance levels
                    support_levels = [pivots['s1'].iloc[0], pivots['s2'].iloc[0], pivots['s3'].iloc[0]]
                    resistance_levels = [pivots['r1'].iloc[0], pivots['r2'].iloc[0], pivots['r3'].iloc[0]]
                    
                    # Buy at support levels
                    for support in support_levels:
                        if abs(current_price - support) / support <= tolerance:
                            signals.iloc[i] = 1
                            break
                    
                    # Sell at resistance levels
                    for resistance in resistance_levels:
                        if abs(current_price - resistance) / resistance <= tolerance:
                            signals.iloc[i] = -1
                            break
        
        return signals

