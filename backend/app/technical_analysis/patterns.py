"""Chart pattern recognition."""

import pandas as pd
import numpy as np
import talib
from typing import List, Dict, Tuple


def detect_head_and_shoulders(df: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """
    Detect Head and Shoulders pattern.
    
    Returns:
        Series with 1 for head and shoulders, -1 for inverse, 0 otherwise
    """
    signals = pd.Series(0, index=df.index)
    
    for i in range(lookback * 2, len(df)):
        window = df.iloc[i - lookback * 2:i]
        
        # Find peaks
        peaks = []
        for j in range(1, len(window) - 1):
            if (window.iloc[j]['high'] > window.iloc[j-1]['high'] and 
                window.iloc[j]['high'] > window.iloc[j+1]['high']):
                peaks.append((j, window.iloc[j]['high']))
        
        if len(peaks) >= 3:
            # Sort by price
            peaks_sorted = sorted(peaks, key=lambda x: x[1])
            
            # Check for H&S: middle peak highest, outer peaks similar
            if len(peaks_sorted) >= 3:
                left_shoulder = peaks_sorted[-2]
                head = peaks_sorted[-1]
                right_shoulder = peaks_sorted[-3]
                
                # Head should be highest
                if head[1] > left_shoulder[1] and head[1] > right_shoulder[1]:
                    # Shoulders should be similar height
                    shoulder_diff = abs(left_shoulder[1] - right_shoulder[1]) / head[1]
                    if shoulder_diff < 0.05:  # Within 5%
                        signals.iloc[i] = -1  # Bearish H&S
    
    return signals


def detect_double_top(df: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """Detect Double Top pattern."""
    signals = pd.Series(0, index=df.index)
    
    for i in range(lookback * 2, len(df)):
        window = df.iloc[i - lookback * 2:i]
        
        # Find two similar peaks
        peaks = []
        for j in range(1, len(window) - 1):
            if (window.iloc[j]['high'] > window.iloc[j-1]['high'] and 
                window.iloc[j]['high'] > window.iloc[j+1]['high']):
                peaks.append((j, window.iloc[j]['high']))
        
        if len(peaks) >= 2:
            peaks_sorted = sorted(peaks, key=lambda x: x[1], reverse=True)
            top1 = peaks_sorted[0]
            top2 = peaks_sorted[1]
            
            # Check if peaks are similar (within 2%)
            if abs(top1[1] - top2[1]) / top1[1] < 0.02:
                signals.iloc[i] = -1  # Bearish double top
    
    return signals


def detect_double_bottom(df: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """Detect Double Bottom pattern."""
    signals = pd.Series(0, index=df.index)
    
    for i in range(lookback * 2, len(df)):
        window = df.iloc[i - lookback * 2:i]
        
        # Find two similar troughs
        troughs = []
        for j in range(1, len(window) - 1):
            if (window.iloc[j]['low'] < window.iloc[j-1]['low'] and 
                window.iloc[j]['low'] < window.iloc[j+1]['low']):
                troughs.append((j, window.iloc[j]['low']))
        
        if len(troughs) >= 2:
            troughs_sorted = sorted(troughs, key=lambda x: x[1])
            bottom1 = troughs_sorted[0]
            bottom2 = troughs_sorted[1]
            
            # Check if bottoms are similar (within 2%)
            if abs(bottom1[1] - bottom2[1]) / bottom1[1] < 0.02:
                signals.iloc[i] = 1  # Bullish double bottom
    
    return signals


def detect_triangles(df: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """Detect Triangle patterns (ascending, descending, symmetrical)."""
    signals = pd.Series(0, index=df.index)
    
    for i in range(lookback * 2, len(df)):
        window = df.iloc[i - lookback * 2:i]
        
        # Get highs and lows
        highs = window['high'].values
        lows = window['low'].values
        
        # Fit trendlines
        x = np.arange(len(highs))
        high_slope = np.polyfit(x, highs, 1)[0]
        low_slope = np.polyfit(x, lows, 1)[0]
        
        # Ascending triangle: rising lows, flat highs
        if low_slope > 0 and abs(high_slope) < 0.0001:
            signals.iloc[i] = 1
        
        # Descending triangle: falling highs, flat lows
        elif high_slope < 0 and abs(low_slope) < 0.0001:
            signals.iloc[i] = -1
        
        # Symmetrical triangle: converging trendlines
        elif (high_slope < 0 and low_slope > 0) or (abs(high_slope - low_slope) < 0.0001):
            signals.iloc[i] = 0  # Neutral
    
    return signals


def detect_wedges(df: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """Detect Wedge patterns."""
    signals = pd.Series(0, index=df.index)
    
    for i in range(lookback * 2, len(df)):
        window = df.iloc[i - lookback * 2:i]
        
        highs = window['high'].values
        lows = window['low'].values
        x = np.arange(len(highs))
        
        high_slope = np.polyfit(x, highs, 1)[0]
        low_slope = np.polyfit(x, lows, 1)[0]
        
        # Rising wedge: both trendlines rising, converging
        if high_slope > 0 and low_slope > 0 and high_slope < low_slope:
            signals.iloc[i] = -1  # Bearish
        
        # Falling wedge: both trendlines falling, converging
        elif high_slope < 0 and low_slope < 0 and abs(high_slope) < abs(low_slope):
            signals.iloc[i] = 1  # Bullish
    
    return signals


def detect_flags_pennants(df: pd.DataFrame, lookback: int = 10) -> pd.Series:
    """Detect Flag and Pennant patterns."""
    signals = pd.Series(0, index=df.index)
    
    for i in range(lookback * 3, len(df)):
        # Check for strong move before consolidation
        prev_window = df.iloc[i - lookback * 2:i - lookback]
        current_window = df.iloc[i - lookback:i]
        
        prev_range = prev_window['high'].max() - prev_window['low'].min()
        current_range = current_window['high'].max() - current_window['low'].min()
        
        # Strong move followed by tight consolidation
        if prev_range > current_range * 2:
            # Determine direction
            prev_trend = prev_window['close'].iloc[-1] - prev_window['close'].iloc[0]
            if prev_trend > 0:
                signals.iloc[i] = 1  # Bullish flag
            else:
                signals.iloc[i] = -1  # Bearish flag
    
    return signals


def detect_candlestick_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect common candlestick patterns using TA-Lib.
    
    Returns:
        DataFrame with pattern detection results
    """
    patterns = {}
    
    # Bullish patterns
    patterns['doji'] = talib.CDLDOJI(df['open'].values, df['high'].values, df['low'].values, df['close'].values)
    patterns['hammer'] = talib.CDLHAMMER(df['open'].values, df['high'].values, df['low'].values, df['close'].values)
    patterns['engulfing_bullish'] = talib.CDLENGULFING(df['open'].values, df['high'].values, df['low'].values, df['close'].values)
    patterns['morning_star'] = talib.CDLMORNINGSTAR(df['open'].values, df['high'].values, df['low'].values, df['close'].values)
    patterns['three_white_soldiers'] = talib.CDL3WHITESOLDIERS(df['open'].values, df['high'].values, df['low'].values, df['close'].values)
    
    # Bearish patterns
    patterns['shooting_star'] = talib.CDLSHOOTINGSTAR(df['open'].values, df['high'].values, df['low'].values, df['close'].values)
    patterns['hanging_man'] = talib.CDLHANGINGMAN(df['open'].values, df['high'].values, df['low'].values, df['close'].values)
    patterns['engulfing_bearish'] = talib.CDLENGULFING(df['open'].values, df['high'].values, df['low'].values, df['close'].values)
    patterns['evening_star'] = talib.CDLEVENINGSTAR(df['open'].values, df['high'].values, df['low'].values, df['close'].values)
    patterns['three_black_crows'] = talib.CDL3BLACKCROWS(df['open'].values, df['high'].values, df['low'].values, df['close'].values)
    
    return pd.DataFrame(patterns, index=df.index)


def detect_support_resistance(df: pd.DataFrame, window: int = 20, tolerance: float = 0.002) -> Dict[str, List[float]]:
    """
    Detect support and resistance levels.
    
    Args:
        df: Price DataFrame
        window: Window size for local extrema
        tolerance: Price tolerance for level matching
    
    Returns:
        Dictionary with 'support' and 'resistance' levels
    """
    highs = []
    lows = []
    
    for i in range(window, len(df) - window):
        local_high = df.iloc[i - window:i + window]['high'].max()
        local_low = df.iloc[i - window:i + window]['low'].min()
        
        if df.iloc[i]['high'] == local_high:
            highs.append(df.iloc[i]['high'])
        if df.iloc[i]['low'] == local_low:
            lows.append(df.iloc[i]['low'])
    
    # Cluster similar levels
    def cluster_levels(levels: List[float], tolerance: float) -> List[float]:
        if not levels:
            return []
        
        levels_sorted = sorted(levels)
        clusters = []
        current_cluster = [levels_sorted[0]]
        
        for level in levels_sorted[1:]:
            if abs(level - current_cluster[-1]) / current_cluster[-1] <= tolerance:
                current_cluster.append(level)
            else:
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]
        
        clusters.append(np.mean(current_cluster))
        return clusters
    
    resistance = cluster_levels(highs, tolerance)
    support = cluster_levels(lows, tolerance)
    
    return {
        'support': sorted(support),
        'resistance': sorted(resistance, reverse=True)
    }

