"""Ichimoku Cloud Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_ichimoku


class IchimokuStrategy(BaseStrategy):
    """
    Ichimoku Cloud Strategy.
    
    Buy when price is above cloud and Tenkan crosses above Kijun.
    Sell when price is below cloud and Tenkan crosses below Kijun.
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "tenkan_period": 9,
            "kijun_period": 26,
            "senkou_b_period": 52
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        ichimoku = calculate_ichimoku(df)
        
        if ichimoku is None or len(ichimoku) == 0:
            return pd.Series(0, index=df.index)
        
        close = df['close']
        tenkan = ichimoku['ITS_9'] if 'ITS_9' in ichimoku.columns else ichimoku.iloc[:, 0]
        kijun = ichimoku['IKS_26'] if 'IKS_26' in ichimoku.columns else ichimoku.iloc[:, 1]
        senkou_a = ichimoku['ISA_9'] if 'ISA_9' in ichimoku.columns else ichimoku.iloc[:, 2]
        senkou_b = ichimoku['ISB_26'] if 'ISB_26' in ichimoku.columns else ichimoku.iloc[:, 3]
        
        signals = pd.Series(0, index=df.index)
        
        # Cloud top and bottom
        cloud_top = pd.concat([senkou_a, senkou_b], axis=1).max(axis=1)
        cloud_bottom = pd.concat([senkou_a, senkou_b], axis=1).min(axis=1)
        
        # Buy: price above cloud, Tenkan crosses above Kijun
        above_cloud = close > cloud_top
        bullish_cross = (tenkan > kijun) & (tenkan.shift(1) <= kijun.shift(1))
        signals[above_cloud & bullish_cross] = 1
        
        # Sell: price below cloud, Tenkan crosses below Kijun
        below_cloud = close < cloud_bottom
        bearish_cross = (tenkan < kijun) & (tenkan.shift(1) >= kijun.shift(1))
        signals[below_cloud & bearish_cross] = -1
        
        return signals

