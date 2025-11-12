"""Utility functions."""

from typing import Any, Optional
import pandas as pd


def validate_ohlcv(df: pd.DataFrame) -> bool:
    """
    Validate OHLCV DataFrame.
    
    Args:
        df: DataFrame to validate
    
    Returns:
        True if valid
    """
    required_columns = ['open', 'high', 'low', 'close']
    
    for col in required_columns:
        if col not in df.columns:
            return False
    
    # Check OHLC relationships
    invalid = (
        (df['high'] < df['low']) |
        (df['open'] > df['high']) |
        (df['open'] < df['low']) |
        (df['close'] > df['high']) |
        (df['close'] < df['low'])
    )
    
    return not invalid.any()

