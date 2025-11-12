"""Data manager for storing and retrieving price data."""

import os
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from pathlib import Path
import redis
from app.config import settings
from app.utils.logger import logger
from app.data.historical import (
    download_historical,
    save_historical_data,
    load_historical_data,
    find_historical_data_files
)


class DataManager:
    """Manages historical and live data storage/retrieval."""
    
    def __init__(self):
        """Initialize data manager with Redis cache."""
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis not available: {e}. Using in-memory cache only.")
            self.redis_client = None
        
        self.data_dir = Path("data/historical")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_historical_data(
        self,
        symbol: str = "GBP_USD",
        timeframe: str = "1h",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Get historical data, using cache if available.
        
        Args:
            symbol: Trading pair symbol
            timeframe: Timeframe
            start_date: Start date
            end_date: End date
            use_cache: Whether to use cached data
        
        Returns:
            DataFrame with OHLCV data
        """
        cache_key = f"historical:{symbol}:{timeframe}:{start_date}:{end_date}"
        
        # Try Redis cache first
        if use_cache and self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    import json
                    data = json.loads(cached)
                    df = pd.DataFrame(data)
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    logger.info(f"Loaded {len(df)} candles from Redis cache")
                    return df
            except Exception as e:
                logger.warning(f"Redis cache read failed: {e}")
        
        # Try local file cache
        if use_cache:
            files = find_historical_data_files(symbol, timeframe)
            if files:
                # Find file covering the date range
                for filepath in reversed(files):  # Start with most recent
                    try:
                        df = load_historical_data(filepath)
                        if start_date and end_date:
                            mask = (df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)
                            df = df[mask]
                        if len(df) > 0:
                            logger.info(f"Loaded {len(df)} candles from file cache")
                            return df
                    except Exception:
                        continue
        
        # Download if not cached
        logger.info("Downloading historical data...")
        df = await download_historical(symbol, timeframe, start_date, end_date)
        
        # Cache the data
        if self.redis_client:
            try:
                import json
                data = df.to_dict('records')
                self.redis_client.setex(cache_key, 3600, json.dumps(data, default=str))  # 1 hour cache
            except Exception as e:
                logger.warning(f"Redis cache write failed: {e}")
        
        # Save to file
        try:
            save_historical_data(df, symbol, timeframe)
        except Exception as e:
            logger.warning(f"Failed to save historical data: {e}")
        
        return df
    
    def get_latest_price(self, symbol: str = "GBP_USD") -> Optional[Dict]:
        """
        Get latest price from cache.
        
        Args:
            symbol: Trading pair symbol
        
        Returns:
            Latest price data or None
        """
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"latest_price:{symbol}"
            cached = self.redis_client.get(cache_key)
            if cached:
                import json
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Error getting latest price from cache: {e}")
        
        return None
    
    def cache_latest_price(self, symbol: str, price_data: Dict) -> None:
        """
        Cache latest price data.
        
        Args:
            symbol: Trading pair symbol
            price_data: Price data dictionary
        """
        if not self.redis_client:
            return
        
        try:
            cache_key = f"latest_price:{symbol}"
            import json
            self.redis_client.setex(cache_key, 60, json.dumps(price_data, default=str))  # 1 minute cache
        except Exception as e:
            logger.warning(f"Error caching latest price: {e}")
    
    def clear_cache(self, symbol: Optional[str] = None, timeframe: Optional[str] = None) -> None:
        """
        Clear cached data.
        
        Args:
            symbol: Optional symbol to clear
            timeframe: Optional timeframe to clear
        """
        if not self.redis_client:
            return
        
        try:
            if symbol and timeframe:
                pattern = f"historical:{symbol}:{timeframe}:*"
            elif symbol:
                pattern = f"historical:{symbol}:*"
            else:
                pattern = "historical:*"
            
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cache keys")
        except Exception as e:
            logger.warning(f"Error clearing cache: {e}")


# Global instance
data_manager = DataManager()

