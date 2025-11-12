"""Signal generation from indicators."""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from app.technical_analysis.indicators import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_stochastic, calculate_cci, calculate_adx
)


def generate_rsi_signals(df: pd.DataFrame, period: int = 14, oversold: float = 30, overbought: float = 70) -> pd.Series:
    """
    Generate buy/sell signals from RSI.
    
    Returns:
        Series with 1 (buy), -1 (sell), 0 (hold)
    """
    rsi = calculate_rsi(df, period)
    signals = pd.Series(0, index=df.index)
    
    signals[rsi < oversold] = 1  # Buy when oversold
    signals[rsi > overbought] = -1  # Sell when overbought
    
    return signals


def generate_macd_signals(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
    """Generate signals from MACD crossover."""
    macd_data = calculate_macd(df, fast, slow, signal)
    signals = pd.Series(0, index=df.index)
    
    macd_line = macd_data['macd']
    signal_line = macd_data['signal']
    
    # Bullish crossover
    signals[(macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))] = 1
    
    # Bearish crossover
    signals[(macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))] = -1
    
    return signals


def generate_bollinger_signals(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.Series:
    """Generate signals from Bollinger Bands."""
    bb = calculate_bollinger_bands(df, period, std_dev)
    signals = pd.Series(0, index=df.index)
    
    close = df['close']
    
    # Buy when price touches lower band
    signals[close <= bb['lower']] = 1
    
    # Sell when price touches upper band
    signals[close >= bb['upper']] = -1
    
    return signals


def generate_stochastic_signals(
    df: pd.DataFrame,
    k_period: int = 14,
    d_period: int = 3,
    oversold: float = 20,
    overbought: float = 80
) -> pd.Series:
    """Generate signals from Stochastic Oscillator."""
    stoch = calculate_stochastic(df, k_period, d_period)
    signals = pd.Series(0, index=df.index)
    
    k = stoch['k']
    d = stoch['d']
    
    # Buy when K crosses above D from oversold
    signals[(k > d) & (k.shift(1) <= d.shift(1)) & (k < oversold)] = 1
    
    # Sell when K crosses below D from overbought
    signals[(k < d) & (k.shift(1) >= d.shift(1)) & (k > overbought)] = -1
    
    return signals


def generate_cci_signals(df: pd.DataFrame, period: int = 20, oversold: float = -100, overbought: float = 100) -> pd.Series:
    """Generate signals from CCI."""
    cci = calculate_cci(df, period)
    signals = pd.Series(0, index=df.index)
    
    signals[cci < oversold] = 1  # Buy when oversold
    signals[cci > overbought] = -1  # Sell when overbought
    
    return signals


def generate_adx_trend_signals(df: pd.DataFrame, period: int = 14, threshold: float = 25) -> pd.Series:
    """Generate signals based on ADX trend strength."""
    adx = calculate_adx(df, period)
    signals = pd.Series(0, index=df.index)
    
    # Strong trend when ADX > threshold
    close = df['close']
    ema = close.ewm(span=period).mean()
    
    # Buy in uptrend
    signals[(adx > threshold) & (close > ema)] = 1
    
    # Sell in downtrend
    signals[(adx > threshold) & (close < ema)] = -1
    
    return signals


def generate_ma_crossover_signals(
    df: pd.DataFrame,
    fast_period: int = 10,
    slow_period: int = 30,
    ma_type: str = 'sma'
) -> pd.Series:
    """Generate signals from moving average crossover."""
    from app.technical_analysis.indicators import calculate_sma, calculate_ema
    
    if ma_type == 'ema':
        fast_ma = calculate_ema(df, fast_period)
        slow_ma = calculate_ema(df, slow_period)
    else:
        fast_ma = calculate_sma(df, fast_period)
        slow_ma = calculate_sma(df, slow_period)
    
    signals = pd.Series(0, index=df.index)
    
    # Golden cross: fast MA crosses above slow MA
    signals[(fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))] = 1
    
    # Death cross: fast MA crosses below slow MA
    signals[(fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))] = -1
    
    return signals


def combine_signals(signals_list: list, method: str = 'majority') -> pd.Series:
    """
    Combine multiple signal series.
    
    Args:
        signals_list: List of signal Series
        method: 'majority', 'all', 'any', or 'weighted'
    
    Returns:
        Combined signal series
    """
    if not signals_list:
        return pd.Series(0)
    
    df_signals = pd.DataFrame(signals_list).T
    
    if method == 'majority':
        # Majority vote
        combined = df_signals.sum(axis=1)
        result = pd.Series(0, index=combined.index)
        result[combined > 0] = 1
        result[combined < 0] = -1
        return result
    
    elif method == 'all':
        # All must agree
        result = pd.Series(0, index=df_signals.index)
        result[(df_signals == 1).all(axis=1)] = 1
        result[(df_signals == -1).all(axis=1)] = -1
        return result
    
    elif method == 'any':
        # Any signal triggers
        result = pd.Series(0, index=df_signals.index)
        result[(df_signals == 1).any(axis=1)] = 1
        result[(df_signals == -1).any(axis=1)] = -1
        return result
    
    else:
        # Weighted average
        weights = np.ones(len(signals_list)) / len(signals_list)
        combined = (df_signals * weights).sum(axis=1)
        result = pd.Series(0, index=combined.index)
        result[combined > 0.5] = 1
        result[combined < -0.5] = -1
        return result


def filter_signals(signals: pd.Series, min_hold_period: int = 1) -> pd.Series:
    """
    Filter signals to avoid excessive trading.
    
    Args:
        signals: Signal series
        min_hold_period: Minimum periods to hold position
    
    Returns:
        Filtered signal series
    """
    filtered = signals.copy()
    last_signal = 0
    hold_count = 0
    
    for i in range(len(filtered)):
        if filtered.iloc[i] != 0 and filtered.iloc[i] != last_signal:
            if hold_count < min_hold_period:
                filtered.iloc[i] = 0
            else:
                last_signal = filtered.iloc[i]
                hold_count = 0
        elif filtered.iloc[i] == last_signal:
            hold_count += 1
        else:
            hold_count += 1
    
    return filtered

