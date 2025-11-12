"""Alpha Vantage API integration (backup data provider)."""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
import httpx
from alpha_vantage.forex import Forex
from app.config import settings
from app.utils.logger import logger


class AlphaVantageProvider:
    """Alpha Vantage API data provider (backup)."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Alpha Vantage provider.
        
        Args:
            api_key: Alpha Vantage API key (defaults to settings)
        """
        self.api_key = api_key or settings.ALPHA_VANTAGE_API_KEY
        self.forex = Forex(key=self.api_key, output_format='pandas')
        self.symbol = "GBPUSD"
    
    def get_current_price(self) -> Dict[str, float]:
        """
        Get current GBP/USD price.
        
        Returns:
            Dictionary with bid, ask, and mid prices
        """
        try:
            data, meta = self.forex.get_currency_exchange_rate(
                from_currency='GBP',
                to_currency='USD'
            )
            
            rate = float(data['5. Exchange Rate'].iloc[0])
            
            # Estimate bid/ask from mid (Alpha Vantage doesn't provide spread)
            spread = 0.0002  # Typical GBP/USD spread
            bid = rate - spread / 2
            ask = rate + spread / 2
            
            return {
                "bid": bid,
                "ask": ask,
                "mid": rate,
                "spread": spread,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Alpha Vantage API error: {e}")
            raise
    
    def get_historical_data(
        self,
        timeframe: str = "1min",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get historical OHLCV data from Alpha Vantage.
        
        Args:
            timeframe: Timeframe (1min, 5min, 15min, 30min, 60min, daily)
            start_date: Start date
            end_date: End date
        
        Returns:
            List of OHLCV dictionaries
        """
        try:
            # Alpha Vantage uses different function for intraday
            if timeframe in ["1min", "5min", "15min", "30min", "60min"]:
                data, meta = self.forex.get_currency_exchange_intraday(
                    from_symbol='GBP',
                    to_symbol='USD',
                    interval=timeframe
                )
            else:
                data, meta = self.forex.get_currency_exchange_daily(
                    from_symbol='GBP',
                    to_symbol='USD'
                )
            
            candles = []
            for idx, row in data.iterrows():
                candle_time = datetime.fromisoformat(str(idx))
                
                # Filter by date range if provided
                if start_date and candle_time < start_date:
                    continue
                if end_date and candle_time > end_date:
                    continue
                
                candles.append({
                    "timestamp": candle_time.isoformat(),
                    "open": float(row['1. open']),
                    "high": float(row['2. high']),
                    "low": float(row['3. low']),
                    "close": float(row['4. close']),
                    "volume": 0  # Alpha Vantage doesn't provide volume for forex
                })
            
            return sorted(candles, key=lambda x: x["timestamp"])
        except Exception as e:
            logger.error(f"Alpha Vantage API error fetching historical data: {e}")
            raise


# Global instance
alpha_vantage_provider = AlphaVantageProvider() if settings.ALPHA_VANTAGE_API_KEY else None

