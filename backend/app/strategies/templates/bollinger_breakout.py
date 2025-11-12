"""Bollinger Band Breakout Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_bollinger_bands


class BollingerBreakoutStrategy(BaseStrategy):
    """
    Bollinger Band Breakout Strategy.
    
    Buy when price breaks above upper band with volume confirmation.
    Sell when price breaks below lower band with volume confirmation.
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "period": 20,
            "std_dev": 2.0,
            "require_volume": True,
            "volume_threshold": 1.2  # 20% above average volume
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        period = self.params["period"]
        std_dev = self.params["std_dev"]
        require_volume = self.params["require_volume"]
        volume_threshold = self.params["volume_threshold"]
        
        bb = calculate_bollinger_bands(df, period, std_dev)
        close = df['close']
        
        signals = pd.Series(0, index=df.index)
        
        # Calculate volume condition if required
        volume_condition = pd.Series(True, index=df.index)
        if require_volume and 'volume' in df.columns:
            avg_volume = df['volume'].rolling(window=period).mean()
            volume_condition = df['volume'] >= (avg_volume * volume_threshold)
        
        # Buy signal: price breaks above upper band
        signals[(close > bb['upper']) & (close.shift(1) <= bb['upper'].shift(1)) & volume_condition] = 1
        
        # Sell signal: price breaks below lower band
        signals[(close < bb['lower']) & (close.shift(1) >= bb['lower'].shift(1)) & volume_condition] = -1
        
        return signals

