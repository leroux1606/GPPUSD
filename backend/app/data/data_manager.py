"""Data manager for storing and retrieving price data."""

import asyncio
import os
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from pathlib import Path
import redis
import yfinance as yf
from app.config import settings
from app.utils.logger import logger

# OANDA timeframe → yfinance interval
_OANDA_TO_YF = {
    "M1": "1m", "M5": "5m", "M15": "15m", "M30": "30m",
    "H1": "1h", "H4": "1h",  # H4 fetched as 1h then resampled
    "D": "1d", "W": "1wk",
}
# Minutes per bar (used to calculate how many calendar days to request)
_TF_MINUTES = {
    "M1": 1, "M5": 5, "M15": 15, "M30": 30,
    "H1": 60, "H4": 240, "D": 1440, "W": 10080,
}
# OANDA pair format → Yahoo Finance ticker
_PAIR_TO_YF = {
    "GBP_USD": "GBPUSD=X", "EUR_USD": "EURUSD=X", "USD_JPY": "USDJPY=X",
    "USD_CHF": "USDCHF=X", "AUD_USD": "AUDUSD=X", "USD_CAD": "USDCAD=X",
    "NZD_USD": "NZDUSD=X", "EUR_GBP": "EURGBP=X", "EUR_JPY": "EURJPY=X",
    "GBP_JPY": "GBPJPY=X",
}

# Module-level cache: key → (fetched_at, DataFrame)
# Shared across all DataManager instances so even the per-scan-cycle
# `dm = DataManager()` pattern doesn't cause redundant downloads.
_DF_CACHE: Dict[str, tuple] = {}
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
    
    async def get_historical_async(
        self,
        symbol: str = "GBP_USD",
        timeframe: str = "M15",
        count: int = 300,
    ) -> Optional[pd.DataFrame]:
        """
        Fetch recent OHLCV bars via Yahoo Finance (no broker account required).

        Results are cached at module level for (tf_minutes - 1) minutes so that
        multiple DataManager instances created within the same scan cycle share
        one download instead of hammering the API.

        Args:
            symbol:    OANDA-format pair, e.g. "GBP_USD"
            timeframe: OANDA-format timeframe, e.g. "M15"
            count:     Number of bars to return

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        yf_interval = _OANDA_TO_YF.get(timeframe, "15m")
        tf_minutes  = _TF_MINUTES.get(timeframe, 15)
        yf_symbol   = _PAIR_TO_YF.get(symbol, symbol.replace("_", "") + "=X")
        cache_key   = f"{symbol}:{timeframe}"

        # Return cached copy if it's younger than tf_minutes - 1 minutes
        if cache_key in _DF_CACHE:
            fetched_at, cached_df = _DF_CACHE[cache_key]
            age_seconds = (datetime.utcnow() - fetched_at).total_seconds()
            if age_seconds < (tf_minutes - 1) * 60:
                logger.debug(f"Cache hit {cache_key} ({age_seconds:.0f}s old)")
                return cached_df.tail(count).reset_index(drop=True)

        # Forex trades ~24 h/day, 5 days/week.  Request enough calendar days.
        bars_per_day  = (24 * 60) / tf_minutes
        calendar_days = max(14, int(count / bars_per_day * 1.6) + 7)
        start         = datetime.utcnow() - timedelta(days=calendar_days)

        loop = asyncio.get_event_loop()
        df   = await loop.run_in_executor(
            None, self._fetch_yf, yf_symbol, yf_interval, start
        )

        if df is None or df.empty:
            logger.warning(f"No data returned from Yahoo Finance for {symbol} {timeframe}")
            # Return stale cache if available rather than nothing
            if cache_key in _DF_CACHE:
                _, cached_df = _DF_CACHE[cache_key]
                logger.info(f"Using stale cache for {cache_key}")
                return cached_df.tail(count).reset_index(drop=True)
            return None

        # Resample H4 from 1h bars
        if timeframe == "H4":
            df = (
                df.set_index("timestamp")
                .resample("4h")
                .agg({"open": "first", "high": "max", "low": "min",
                      "close": "last", "volume": "sum"})
                .dropna()
                .reset_index()
            )

        _DF_CACHE[cache_key] = (datetime.utcnow(), df)
        return df.tail(count).reset_index(drop=True)

    def _fetch_yf(self, symbol: str, interval: str, start: datetime) -> Optional[pd.DataFrame]:
        """
        Blocking Yahoo Finance download via direct HTTP (v8 chart API).
        Uses requests with a browser User-Agent to avoid the empty-response
        issue that affects older yfinance builds.
        """
        import requests

        # Map interval to a range that covers the start date
        days_back = max(1, (datetime.utcnow() - start).days)
        if   days_back <= 1:  yf_range = "1d"
        elif days_back <= 5:  yf_range = "5d"
        elif days_back <= 30: yf_range = "1mo"
        elif days_back <= 90: yf_range = "3mo"
        else:                 yf_range = "6mo"

        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            f"?interval={interval}&range={yf_range}"
        )
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
        }

        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            result = data.get("chart", {}).get("result")
            if not result:
                logger.warning(f"Yahoo Finance: no result for {symbol}")
                return None

            timestamps = result[0].get("timestamp", [])
            quote      = result[0].get("indicators", {}).get("quote", [{}])[0]
            if not timestamps or not quote:
                return None

            rows = []
            for i, ts in enumerate(timestamps):
                o = quote.get("open",  [None])[i]
                h = quote.get("high",  [None])[i]
                l = quote.get("low",   [None])[i]
                c = quote.get("close", [None])[i]
                v = quote.get("volume",[0])[i]
                if None in (o, h, l, c):
                    continue
                rows.append({
                    "timestamp": pd.Timestamp(ts, unit="s", tz="UTC").tz_localize(None),
                    "open":  float(o),
                    "high":  float(h),
                    "low":   float(l),
                    "close": float(c),
                    "volume": int(v) if v else 0,
                })

            if not rows:
                return None

            df = pd.DataFrame(rows)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            return df.sort_values("timestamp").reset_index(drop=True)

        except Exception as e:
            logger.error(f"Yahoo Finance fetch error ({symbol} {interval}): {e}")
            return None

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

