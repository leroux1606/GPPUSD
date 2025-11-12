"""Range Trading Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_bollinger_bands, calculate_rsi


class RangeTradingStrategy(BaseStrategy):
    """
    Range Trading Strategy.
    
    Buy at lower range boundary, sell at upper range boundary.
    Works best in sideways markets.
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "lookback": 20,
            "rsi_period": 14,
            "oversold": 30,
            "overbought": 70,
            "range_threshold": 0.01  # 1% range minimum
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        lookback = self.params["lookback"]
        rsi_period = self.params["rsi_period"]
        oversold = self.params["oversold"]
        overbought = self.params["overbought"]
        range_threshold = self.params["range_threshold"]
        
        rsi = calculate_rsi(df, rsi_period)
        signals = pd.Series(0, index=df.index)
        
        for i in range(lookback, len(df)):
            window = df.iloc[i - lookback:i]
            high = window['high'].max()
            low = window['low'].min()
            range_size = (high - low) / low
            
            # Only trade if market is ranging (not trending)
            if range_size >= range_threshold:
                current_price = df.iloc[i]['close']
                current_rsi = rsi.iloc[i]
                
                # Buy at lower range with RSI oversold
                lower_range = low + (high - low) * 0.2
                if current_price <= lower_range and current_rsi < oversold:
                    signals.iloc[i] = 1
                
                # Sell at upper range with RSI overbought
                upper_range = high - (high - low) * 0.2
                if current_price >= upper_range and current_rsi > overbought:
                    signals.iloc[i] = -1
        
        return signals

