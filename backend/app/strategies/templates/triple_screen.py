"""Triple Screen Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_ema, calculate_macd, calculate_rsi


class TripleScreenStrategy(BaseStrategy):
    """
    Triple Screen Strategy.
    
    Screen 1: Trend (longer timeframe)
    Screen 2: Momentum (MACD)
    Screen 3: Entry timing (RSI)
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "trend_period": 50,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9,
            "rsi_period": 14,
            "rsi_oversold": 30,
            "rsi_overbought": 70
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        trend_period = self.params["trend_period"]
        macd_fast = self.params["macd_fast"]
        macd_slow = self.params["macd_slow"]
        macd_signal = self.params["macd_signal"]
        rsi_period = self.params["rsi_period"]
        rsi_oversold = self.params["rsi_oversold"]
        rsi_overbought = self.params["rsi_overbought"]
        
        # Screen 1: Trend
        trend_ema = calculate_ema(df, trend_period)
        uptrend = df['close'] > trend_ema
        downtrend = df['close'] < trend_ema
        
        # Screen 2: Momentum
        macd_data = calculate_macd(df, macd_fast, macd_slow, macd_signal)
        bullish_momentum = macd_data['macd'] > macd_data['signal']
        bearish_momentum = macd_data['macd'] < macd_data['signal']
        
        # Screen 3: Entry timing
        rsi = calculate_rsi(df, rsi_period)
        rsi_oversold_condition = rsi < rsi_oversold
        rsi_overbought_condition = rsi > rsi_overbought
        
        signals = pd.Series(0, index=df.index)
        
        # Buy: Uptrend + Bullish momentum + RSI oversold (pullback entry)
        signals[uptrend & bullish_momentum & rsi_oversold_condition] = 1
        
        # Sell: Downtrend + Bearish momentum + RSI overbought (bounce exit)
        signals[downtrend & bearish_momentum & rsi_overbought_condition] = -1
        
        return signals

