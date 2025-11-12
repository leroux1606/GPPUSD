"""Oscillator indicators module (additional oscillators)."""

import pandas as pd
import numpy as np
from app.technical_analysis.indicators import calculate_rsi, calculate_stochastic, calculate_cci


def calculate_williams_r(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Williams %R Oscillator."""
    from app.technical_analysis.indicators import calculate_williams_r as calc_wr
    return calc_wr(df, period)


def calculate_momentum_oscillator(df: pd.DataFrame, period: int = 10) -> pd.Series:
    """Momentum Oscillator."""
    from app.technical_analysis.indicators import calculate_momentum
    return calculate_momentum(df, period)


def calculate_price_oscillator(df: pd.DataFrame, fast: int = 12, slow: int = 26) -> pd.Series:
    """Price Oscillator (percentage difference between MAs)."""
    from app.technical_analysis.indicators import calculate_sma
    fast_ma = calculate_sma(df, fast)
    slow_ma = calculate_sma(df, slow)
    return ((fast_ma - slow_ma) / slow_ma) * 100


def calculate_detrended_price_oscillator(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Detrended Price Oscillator."""
    from app.technical_analysis.indicators import calculate_sma
    sma = calculate_sma(df, period)
    return df['close'] - sma.shift(period // 2 + 1)


def calculate_commodity_channel_index(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Commodity Channel Index (alias)."""
    return calculate_cci(df, period)


def calculate_relative_vigor_index(df: pd.DataFrame, period: int = 10) -> pd.Series:
    """Relative Vigor Index."""
    close_open = df['close'] - df['open']
    high_low = df['high'] - df['low']
    
    numerator = close_open.rolling(window=period).mean()
    denominator = high_low.rolling(window=period).mean()
    
    rvi = numerator / denominator
    signal = rvi.rolling(window=4).mean()
    
    return pd.Series(rvi, name='rvi')


def calculate_awesome_oscillator(df: pd.DataFrame, fast: int = 5, slow: int = 34) -> pd.Series:
    """Awesome Oscillator."""
    from app.technical_analysis.indicators import calculate_sma
    fast_ma = calculate_sma(df, fast)
    slow_ma = calculate_sma(df, slow)
    return fast_ma - slow_ma


def calculate_kaufman_efficiency_ratio(df: pd.DataFrame, period: int = 10) -> pd.Series:
    """Kaufman Efficiency Ratio."""
    change = abs(df['close'] - df['close'].shift(period))
    volatility = df['close'].diff().abs().rolling(window=period).sum()
    return change / volatility


def calculate_chaikin_money_flow(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Chaikin Money Flow."""
    mf_multiplier = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
    mf_volume = mf_multiplier * df['volume']
    cmf = mf_volume.rolling(window=period).sum() / df['volume'].rolling(window=period).sum()
    return cmf


def calculate_ease_of_movement(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Ease of Movement."""
    distance = (df['high'] + df['low']) / 2 - (df['high'].shift(1) + df['low'].shift(1)) / 2
    box_ratio = df['volume'] / (df['high'] - df['low'])
    emv = distance / box_ratio
    return emv.rolling(window=period).mean()

