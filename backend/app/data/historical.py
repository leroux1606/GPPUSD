"""Historical data download and management."""

import os
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from pathlib import Path
from app.data.providers.oanda import oanda_provider
from app.data.providers.alpha_vantage import alpha_vantage_provider
from app.data.providers.yahoo_finance import yahoo_finance_provider
from app.utils.logger import logger


# Timeframe mapping
TIMEFRAME_MAP = {
    "1m": "M1",
    "5m": "M5",
    "15m": "M15",
    "1h": "H1",
    "4h": "H4",
    "1d": "D"
}


async def download_historical(
    symbol: str = "GBP_USD",
    timeframe: str = "1h",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    provider: str = "oanda"
) -> pd.DataFrame:
    """
    Download historical OHLCV data from specified provider.
    
    Args:
        symbol: Trading pair symbol
        timeframe: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
        start_date: Start date (defaults to 1 year ago)
        end_date: End date (defaults to now)
        provider: Data provider (oanda, alpha_vantage, yahoo)
    
    Returns:
        DataFrame with columns: timestamp, open, high, low, close, volume
    """
    try:
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=365)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Try providers in order of preference
        providers = []
        if provider == "oanda" and oanda_provider:
            providers.append(("oanda", oanda_provider))
        if provider == "alpha_vantage" and alpha_vantage_provider:
            providers.append(("alpha_vantage", alpha_vantage_provider))
        if provider == "yahoo" or not providers:
            providers.append(("yahoo", yahoo_finance_provider))
        
        candles = []
        last_error = None
        
        for prov_name, prov in providers:
            try:
                if prov_name == "oanda":
                    oanda_timeframe = TIMEFRAME_MAP.get(timeframe, "H1")
                    candles = prov.get_historical_data(
                        timeframe=oanda_timeframe,
                        start_date=start_date,
                        end_date=end_date
                    )
                elif prov_name == "alpha_vantage":
                    av_timeframe = timeframe.replace("m", "min").replace("h", "min")
                    candles = prov.get_historical_data(
                        timeframe=av_timeframe,
                        start_date=start_date,
                        end_date=end_date
                    )
                else:  # yahoo
                    candles = prov.get_historical_data(
                        timeframe=timeframe,
                        start_date=start_date,
                        end_date=end_date
                    )
                
                if candles:
                    logger.info(f"Downloaded {len(candles)} candles from {prov_name}")
                    break
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {prov_name} failed: {e}")
                continue
        
        if not candles:
            raise Exception(f"All providers failed. Last error: {last_error}")
        
        # Convert to DataFrame
        df = pd.DataFrame(candles)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Validate data
        df = validate_ohlcv_data(df)
        
        return df
    
    except Exception as e:
        logger.error(f"Error downloading historical data: {e}")
        raise


def validate_ohlcv_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and clean OHLCV data.
    
    Args:
        df: DataFrame with OHLCV data
    
    Returns:
        Cleaned DataFrame
    """
    # Remove duplicates
    df = df.drop_duplicates(subset=['timestamp']).reset_index(drop=True)
    
    # Validate OHLC relationships
    invalid_mask = (
        (df['high'] < df['low']) |
        (df['open'] > df['high']) |
        (df['open'] < df['low']) |
        (df['close'] > df['high']) |
        (df['close'] < df['low'])
    )
    
    if invalid_mask.any():
        logger.warning(f"Removing {invalid_mask.sum()} invalid candles")
        df = df[~invalid_mask].reset_index(drop=True)
    
    # Remove outliers (price changes > 10%)
    if len(df) > 1:
        price_change = df['close'].pct_change().abs()
        outliers = price_change > 0.1
        if outliers.any():
            logger.warning(f"Removing {outliers.sum()} outlier candles")
            df = df[~outliers].reset_index(drop=True)
    
    # Forward fill missing values
    df = df.fillna(method='ffill').fillna(method='bfill')
    
    return df


def save_historical_data(df: pd.DataFrame, symbol: str, timeframe: str, data_dir: str = "data/historical") -> str:
    """
    Save historical data to Parquet file.
    
    Args:
        df: DataFrame with OHLCV data
        symbol: Trading pair symbol
        timeframe: Timeframe
        data_dir: Data directory path
    
    Returns:
        Path to saved file
    """
    try:
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        filename = f"{symbol}_{timeframe}_{df['timestamp'].min().strftime('%Y%m%d')}_{df['timestamp'].max().strftime('%Y%m%d')}.parquet"
        filepath = os.path.join(data_dir, filename)
        df.to_parquet(filepath, index=False)
        logger.info(f"Saved historical data to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error saving historical data: {e}")
        raise


def load_historical_data(filepath: str) -> pd.DataFrame:
    """
    Load historical data from Parquet file.
    
    Args:
        filepath: Path to Parquet file
    
    Returns:
        DataFrame with OHLCV data
    """
    try:
        df = pd.read_parquet(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        logger.error(f"Error loading historical data: {e}")
        raise


def find_historical_data_files(symbol: str, timeframe: str, data_dir: str = "data/historical") -> List[str]:
    """
    Find historical data files matching symbol and timeframe.
    
    Args:
        symbol: Trading pair symbol
        timeframe: Timeframe
        data_dir: Data directory path
    
    Returns:
        List of file paths
    """
    try:
        data_path = Path(data_dir)
        if not data_path.exists():
            return []
        
        pattern = f"{symbol}_{timeframe}_*.parquet"
        files = list(data_path.glob(pattern))
        return [str(f) for f in sorted(files)]
    except Exception as e:
        logger.error(f"Error finding historical data files: {e}")
        return []

