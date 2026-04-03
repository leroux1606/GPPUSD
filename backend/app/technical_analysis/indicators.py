"""40+ Technical Indicators Implementation using TA-Lib and native pandas/numpy."""

import pandas as pd
import numpy as np
import talib
from typing import Union, Optional, Dict, Tuple


# ==================== TREND INDICATORS ====================

def calculate_sma(df: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.Series:
    """Simple Moving Average."""
    return pd.Series(talib.SMA(df[column].values, timeperiod=period), index=df.index)


def calculate_ema(df: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.Series:
    """Exponential Moving Average."""
    return pd.Series(talib.EMA(df[column].values, timeperiod=period), index=df.index)


def calculate_wma(df: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.Series:
    """Weighted Moving Average."""
    return pd.Series(talib.WMA(df[column].values, timeperiod=period), index=df.index)


def calculate_vwma(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Volume Weighted Moving Average."""
    pv = df['close'] * df['volume']
    result = pv.rolling(period).sum() / df['volume'].rolling(period).sum()
    return pd.Series(result.values, index=df.index)


def calculate_macd(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    column: str = 'close'
) -> pd.DataFrame:
    """MACD (Moving Average Convergence Divergence)."""
    macd, signal, hist = talib.MACD(
        df[column].values,
        fastperiod=fast_period,
        slowperiod=slow_period,
        signalperiod=signal_period
    )
    return pd.DataFrame({
        'macd': macd,
        'signal': signal,
        'histogram': hist
    }, index=df.index)


def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average Directional Index."""
    return pd.Series(talib.ADX(df['high'].values, df['low'].values, df['close'].values, timeperiod=period), index=df.index)


def calculate_ichimoku(df: pd.DataFrame) -> pd.DataFrame:
    """Ichimoku Cloud — native implementation."""
    high, low = df['high'], df['low']
    tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
    kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
    span_a = ((tenkan + kijun) / 2).shift(26)
    span_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
    chikou = df['close'].shift(-26)
    return pd.DataFrame({
        'ITS_9': tenkan,
        'IKS_26': kijun,
        'ISA_9': span_a,
        'ISB_26': span_b,
        'ICS_26': chikou,
    }, index=df.index)


def calculate_parabolic_sar(df: pd.DataFrame, acceleration: float = 0.02, maximum: float = 0.2) -> pd.Series:
    """Parabolic SAR."""
    return pd.Series(talib.SAR(df['high'].values, df['low'].values, acceleration=acceleration, maximum=maximum), index=df.index)


def calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
    """Supertrend Indicator — native implementation."""
    atr = pd.Series(talib.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=period), index=df.index)
    hl2 = (df['high'] + df['low']) / 2
    upper_basic = hl2 + multiplier * atr
    lower_basic = hl2 - multiplier * atr

    upper = upper_basic.copy()
    lower = lower_basic.copy()
    direction = pd.Series(np.ones(len(df)), index=df.index)  # 1=up, -1=down

    for i in range(1, len(df)):
        upper.iloc[i] = upper_basic.iloc[i] if upper_basic.iloc[i] < upper.iloc[i - 1] or df['close'].iloc[i - 1] > upper.iloc[i - 1] else upper.iloc[i - 1]
        lower.iloc[i] = lower_basic.iloc[i] if lower_basic.iloc[i] > lower.iloc[i - 1] or df['close'].iloc[i - 1] < lower.iloc[i - 1] else lower.iloc[i - 1]
        if df['close'].iloc[i] > upper.iloc[i - 1]:
            direction.iloc[i] = 1
        elif df['close'].iloc[i] < lower.iloc[i - 1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i - 1]

    supertrend = pd.Series(np.where(direction == 1, lower, upper), index=df.index)
    col = f'SUPERT_{period}_{multiplier}'
    return pd.DataFrame({col: supertrend, f'SUPERTd_{period}_{multiplier}': direction}, index=df.index)


# ==================== MOMENTUM INDICATORS ====================

def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = 'close') -> pd.Series:
    """Relative Strength Index."""
    return pd.Series(talib.RSI(df[column].values, timeperiod=period), index=df.index)


def calculate_stochastic(
    df: pd.DataFrame,
    k_period: int = 14,
    d_period: int = 3,
    slow_k_period: int = 3
) -> pd.DataFrame:
    """Stochastic Oscillator."""
    slowk, slowd = talib.STOCH(
        df['high'].values,
        df['low'].values,
        df['close'].values,
        fastk_period=k_period,
        slowk_period=slow_k_period,
        slowd_period=d_period
    )
    return pd.DataFrame({
        'k': slowk,
        'd': slowd
    }, index=df.index)


def calculate_cci(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Commodity Channel Index."""
    return pd.Series(talib.CCI(df['high'].values, df['low'].values, df['close'].values, timeperiod=period), index=df.index)


def calculate_williams_r(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Williams %R."""
    return pd.Series(talib.WILLR(df['high'].values, df['low'].values, df['close'].values, timeperiod=period), index=df.index)


def calculate_roc(df: pd.DataFrame, period: int = 10, column: str = 'close') -> pd.Series:
    """Rate of Change."""
    return pd.Series(talib.ROC(df[column].values, timeperiod=period), index=df.index)


def calculate_momentum(df: pd.DataFrame, period: int = 10, column: str = 'close') -> pd.Series:
    """Momentum."""
    return pd.Series(talib.MOM(df[column].values, timeperiod=period), index=df.index)


# ==================== VOLATILITY INDICATORS ====================

def calculate_bollinger_bands(
    df: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2.0,
    column: str = 'close'
) -> pd.DataFrame:
    """Bollinger Bands."""
    upper, middle, lower = talib.BBANDS(
        df[column].values,
        timeperiod=period,
        nbdevup=std_dev,
        nbdevdn=std_dev
    )
    return pd.DataFrame({
        'upper': upper,
        'middle': middle,
        'lower': lower
    }, index=df.index)


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range."""
    return pd.Series(talib.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=period), index=df.index)


def calculate_keltner_channels(
    df: pd.DataFrame,
    period: int = 20,
    multiplier: float = 2.0
) -> pd.DataFrame:
    """Keltner Channels — native implementation."""
    middle = pd.Series(talib.EMA(df['close'].values, timeperiod=period), index=df.index)
    atr = pd.Series(talib.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=period), index=df.index)
    upper = middle + multiplier * atr
    lower = middle - multiplier * atr
    return pd.DataFrame({
        f'KCUe_{period}_{multiplier}': upper,
        f'KCBe_{period}_{multiplier}': middle,
        f'KCLe_{period}_{multiplier}': lower,
    }, index=df.index)


def calculate_donchian_channels(
    df: pd.DataFrame,
    period: int = 20
) -> pd.DataFrame:
    """Donchian Channels — native implementation."""
    upper = df['high'].rolling(period).max()
    lower = df['low'].rolling(period).min()
    mid = (upper + lower) / 2
    return pd.DataFrame({
        f'DCU_{period}_{period}': upper,
        f'DCM_{period}_{period}': mid,
        f'DCL_{period}_{period}': lower,
    }, index=df.index)


# ==================== VOLUME INDICATORS ====================

def calculate_obv(df: pd.DataFrame) -> pd.Series:
    """On-Balance Volume."""
    return pd.Series(talib.OBV(df['close'].values, df['volume'].values), index=df.index)


def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """Volume Weighted Average Price — resets each calendar day."""
    tp = (df['high'] + df['low'] + df['close']) / 3
    if 'timestamp' in df.columns:
        dates = pd.to_datetime(df['timestamp']).dt.date
    else:
        dates = pd.Series(df.index).dt.date.values if hasattr(df.index, 'date') else pd.Series([0] * len(df)).values
    result = pd.Series(np.nan, index=df.index)
    df2 = df.copy()
    df2['_tp'] = tp.values
    df2['_vol'] = df['volume'].values
    df2['_date'] = dates
    for date, grp in df2.groupby('_date'):
        idx = grp.index
        cum_tpv = (grp['_tp'] * grp['_vol']).cumsum()
        cum_vol = grp['_vol'].cumsum()
        result.loc[idx] = (cum_tpv / cum_vol).values
    return result


def calculate_mfi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Money Flow Index."""
    return pd.Series(talib.MFI(df['high'].values, df['low'].values, df['close'].values, df['volume'].values, timeperiod=period), index=df.index)


def calculate_ad_line(df: pd.DataFrame) -> pd.Series:
    """Accumulation/Distribution Line."""
    return pd.Series(talib.AD(df['high'].values, df['low'].values, df['close'].values, df['volume'].values), index=df.index)


def calculate_volume_profile(df: pd.DataFrame, bins: int = 20) -> pd.DataFrame:
    """Volume Profile — native histogram implementation."""
    price_min, price_max = df['close'].min(), df['close'].max()
    bin_edges = np.linspace(price_min, price_max, bins + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    vol_by_bin = np.zeros(bins)
    for i in range(bins):
        mask = (df['close'] >= bin_edges[i]) & (df['close'] < bin_edges[i + 1])
        vol_by_bin[i] = df.loc[mask, 'volume'].sum()
    return pd.DataFrame({'price_level': bin_centers, 'volume': vol_by_bin})


# ==================== SUPPORT/RESISTANCE INDICATORS ====================

def calculate_pivot_points(df: pd.DataFrame, method: str = 'standard') -> pd.DataFrame:
    """
    Calculate Pivot Points.
    
    Args:
        df: DataFrame with OHLC data
        method: 'standard', 'fibonacci', or 'camarilla'
    
    Returns:
        DataFrame with pivot point levels
    """
    high = df['high'].iloc[-1]
    low = df['low'].iloc[-1]
    close = df['close'].iloc[-1]
    
    if method == 'standard':
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        r2 = pivot + (high - low)
        r3 = high + 2 * (pivot - low)
        s1 = 2 * pivot - high
        s2 = pivot - (high - low)
        s3 = low - 2 * (high - pivot)
        
        return pd.DataFrame({
            'pivot': [pivot],
            'r1': [r1], 'r2': [r2], 'r3': [r3],
            's1': [s1], 's2': [s2], 's3': [s3]
        })
    
    elif method == 'fibonacci':
        pivot = (high + low + close) / 3
        diff = high - low
        r1 = pivot + 0.382 * diff
        r2 = pivot + 0.618 * diff
        r3 = pivot + 1.0 * diff
        s1 = pivot - 0.382 * diff
        s2 = pivot - 0.618 * diff
        s3 = pivot - 1.0 * diff
        
        return pd.DataFrame({
            'pivot': [pivot],
            'r1': [r1], 'r2': [r2], 'r3': [r3],
            's1': [s1], 's2': [s2], 's3': [s3]
        })
    
    elif method == 'camarilla':
        pivot = (high + low + close) / 3
        diff = high - low
        r1 = close + diff * 1.1 / 12
        r2 = close + diff * 1.1 / 6
        r3 = close + diff * 1.1 / 4
        r4 = close + diff * 1.1 / 2
        s1 = close - diff * 1.1 / 12
        s2 = close - diff * 1.1 / 6
        s3 = close - diff * 1.1 / 4
        s4 = close - diff * 1.1 / 2
        
        return pd.DataFrame({
            'pivot': [pivot],
            'r1': [r1], 'r2': [r2], 'r3': [r3], 'r4': [r4],
            's1': [s1], 's2': [s2], 's3': [s3], 's4': [s4]
        })
    
    else:
        raise ValueError(f"Unknown pivot point method: {method}")


def calculate_fibonacci_retracement(
    high: float,
    low: float,
    trend: str = 'up'
) -> Dict[str, float]:
    """
    Calculate Fibonacci Retracement levels.
    
    Args:
        high: High price
        low: Low price
        trend: 'up' or 'down'
    
    Returns:
        Dictionary with Fibonacci levels
    """
    diff = high - low
    levels = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
    
    if trend == 'up':
        return {f"fib_{int(l*1000)}": high - diff * l for l in levels}
    else:
        return {f"fib_{int(l*1000)}": low + diff * l for l in levels}


# ==================== ADDITIONAL INDICATORS ====================

def calculate_aroon(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Aroon Indicator."""
    aroon_down, aroon_up = talib.AROON(df['high'].values, df['low'].values, timeperiod=period)
    return pd.DataFrame({
        'aroon_up': aroon_up,
        'aroon_down': aroon_down
    }, index=df.index)


def calculate_apo(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26) -> pd.Series:
    """Absolute Price Oscillator."""
    return pd.Series(talib.APO(df['close'].values, fastperiod=fast_period, slowperiod=slow_period), index=df.index)


def calculate_ppo(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26) -> pd.Series:
    """Percentage Price Oscillator."""
    return pd.Series(talib.PPO(df['close'].values, fastperiod=fast_period, slowperiod=slow_period), index=df.index)


def calculate_trix(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """TRIX Indicator."""
    return pd.Series(talib.TRIX(df['close'].values, timeperiod=period), index=df.index)


def calculate_ultosc(df: pd.DataFrame, period1: int = 7, period2: int = 14, period3: int = 28) -> pd.Series:
    """Ultimate Oscillator."""
    return pd.Series(talib.ULTOSC(df['high'].values, df['low'].values, df['close'].values, timeperiod1=period1, timeperiod2=period2, timeperiod3=period3), index=df.index)


def calculate_dmi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Directional Movement Index."""
    plus_di = talib.PLUS_DI(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
    minus_di = talib.MINUS_DI(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
    return pd.DataFrame({
        'plus_di': plus_di,
        'minus_di': minus_di
    }, index=df.index)


def calculate_aroon_oscillator(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Aroon Oscillator."""
    aroon = calculate_aroon(df, period)
    return aroon['aroon_up'] - aroon['aroon_down']


def calculate_tsi(df: pd.DataFrame, fast_period: int = 25, slow_period: int = 13) -> pd.Series:
    """True Strength Index — native implementation."""
    momentum = df['close'].diff(1)
    abs_momentum = momentum.abs()
    ds_pc = momentum.ewm(span=fast_period, adjust=False).mean().ewm(span=slow_period, adjust=False).mean()
    ds_abs = abs_momentum.ewm(span=fast_period, adjust=False).mean().ewm(span=slow_period, adjust=False).mean()
    tsi = 100 * ds_pc / ds_abs.replace(0, np.nan)
    return pd.Series(tsi.values, index=df.index)


def calculate_ao(df: pd.DataFrame, fast_period: int = 5, slow_period: int = 34) -> pd.Series:
    """Awesome Oscillator — native implementation."""
    midpoint = (df['high'] + df['low']) / 2
    ao = midpoint.rolling(fast_period).mean() - midpoint.rolling(slow_period).mean()
    return pd.Series(ao.values, index=df.index)


def calculate_psar(df: pd.DataFrame, af: float = 0.02, max_af: float = 0.2) -> pd.Series:
    """Parabolic SAR (alternative implementation)."""
    return calculate_parabolic_sar(df, acceleration=af, maximum=max_af)


# Indicator registry for easy access
INDICATORS = {
    # Trend
    'sma': calculate_sma,
    'ema': calculate_ema,
    'wma': calculate_wma,
    'vwma': calculate_vwma,
    'macd': calculate_macd,
    'adx': calculate_adx,
    'ichimoku': calculate_ichimoku,
    'parabolic_sar': calculate_parabolic_sar,
    'supertrend': calculate_supertrend,
    # Momentum
    'rsi': calculate_rsi,
    'stochastic': calculate_stochastic,
    'cci': calculate_cci,
    'williams_r': calculate_williams_r,
    'roc': calculate_roc,
    'momentum': calculate_momentum,
    # Volatility
    'bollinger_bands': calculate_bollinger_bands,
    'atr': calculate_atr,
    'keltner_channels': calculate_keltner_channels,
    'donchian_channels': calculate_donchian_channels,
    # Volume
    'obv': calculate_obv,
    'vwap': calculate_vwap,
    'mfi': calculate_mfi,
    'ad_line': calculate_ad_line,
    'volume_profile': calculate_volume_profile,
    # Support/Resistance
    'pivot_points': calculate_pivot_points,
    # Additional
    'aroon': calculate_aroon,
    'apo': calculate_apo,
    'ppo': calculate_ppo,
    'trix': calculate_trix,
    'ultosc': calculate_ultosc,
    'dmi': calculate_dmi,
    'aroon_oscillator': calculate_aroon_oscillator,
    'tsi': calculate_tsi,
    'ao': calculate_ao,
}

