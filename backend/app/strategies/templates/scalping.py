"""Price Action Scalping Strategy."""

import pandas as pd
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_ema, calculate_atr


class ScalpingStrategy(BaseStrategy):
    """
    Price Action Scalping Strategy.
    
    Quick entries based on price action and short-term momentum.
    Uses fast EMA and ATR for entries/exits.
    """
    
    def get_default_params(self) -> Dict[str, Any]:
        return {
            "ema_period": 9,
            "atr_period": 14,
            "atr_multiplier": 1.5,
            "min_candle_size": 0.0001
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        ema_period = self.params["ema_period"]
        atr_period = self.params["atr_period"]
        atr_mult = self.params["atr_multiplier"]
        min_size = self.params["min_candle_size"]
        
        ema = calculate_ema(df, ema_period)
        atr = calculate_atr(df, atr_period)

        close = df['close']
        high = df['high']
        low = df['low']
        candle_size = high - low

        signals = pd.Series(0, index=df.index)

        # Candle must have some body — filter noise but avoid spike entries
        # At least 30% of ATR (real move) and no more than 1.5x ATR (avoid news spikes)
        valid_candle = (candle_size >= atr * 0.3) & (candle_size <= atr * atr_mult)

        # Buy: price above EMA, bullish candle with valid size
        bullish_candle = close > df['open']
        above_ema = close > ema

        signals[above_ema & bullish_candle & valid_candle] = 1

        # Sell: price below EMA, bearish candle with valid size
        bearish_candle = close < df['open']
        below_ema = close < ema

        signals[below_ema & bearish_candle & valid_candle] = -1
        
        return signals

