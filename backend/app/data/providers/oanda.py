"""OANDA API integration for live and historical data."""

import asyncio
from typing import Optional, Dict, List, AsyncGenerator
from datetime import datetime, timedelta
import httpx
from oandapyV20 import API
from oandapyV20.endpoints import instruments, accounts, pricing
from oandapyV20.exceptions import V20Error
from app.config import settings
from app.utils.logger import logger


class OANDAProvider:
    """OANDA API data provider."""
    
    def __init__(self, api_key: Optional[str] = None, account_id: Optional[str] = None):
        """
        Initialize OANDA provider.
        
        Args:
            api_key: OANDA API key (defaults to settings)
            account_id: OANDA account ID (defaults to settings)
        """
        self.api_key = api_key or settings.OANDA_API_KEY
        self.account_id = account_id or settings.OANDA_ACCOUNT_ID
        self.client = API(access_token=self.api_key, environment="practice")
        self.symbol = "GBP_USD"
    
    def get_current_price(self) -> Dict[str, float]:
        """
        Get current GBP/USD price.
        
        Returns:
            Dictionary with bid, ask, and mid prices
        """
        try:
            request = pricing.PricingInfo(accountID=self.account_id, params={"instruments": self.symbol})
            response = self.client.request(request)
            
            if response.get("prices"):
                price_data = response["prices"][0]
                bid = float(price_data["bids"][0]["price"])
                ask = float(price_data["asks"][0]["price"])
                
                return {
                    "bid": bid,
                    "ask": ask,
                    "mid": (bid + ask) / 2,
                    "spread": ask - bid,
                    "timestamp": datetime.utcnow().isoformat()
                }
            raise ValueError("No price data received from OANDA")
        except V20Error as e:
            logger.error(f"OANDA API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            raise
    
    def get_historical_data(
        self,
        timeframe: str = "M1",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        count: Optional[int] = None
    ) -> List[Dict]:
        """
        Get historical OHLCV data from OANDA.
        
        Args:
            timeframe: Timeframe (M1, M5, M15, H1, H4, D)
            start_date: Start date (required if count not provided)
            end_date: End date (defaults to now)
            count: Number of candles to retrieve (alternative to date range)
        
        Returns:
            List of OHLCV dictionaries
        """
        try:
            params = {"granularity": timeframe, "price": "M"}
            
            if count:
                params["count"] = count
            elif start_date:
                params["from"] = start_date.isoformat() + "Z"
                if end_date:
                    params["to"] = end_date.isoformat() + "Z"
            else:
                params["count"] = 500  # Default to 500 candles
            
            request = instruments.InstrumentsCandles(instrument=self.symbol, params=params)
            response = self.client.request(request)
            
            candles = []
            for candle in response.get("candles", []):
                if candle.get("complete"):
                    mid = candle["mid"]
                    candles.append({
                        "timestamp": candle["time"],
                        "open": float(mid["o"]),
                        "high": float(mid["h"]),
                        "low": float(mid["l"]),
                        "close": float(mid["c"]),
                        "volume": int(candle.get("volume", 0))
                    })
            
            return candles
        except V20Error as e:
            logger.error(f"OANDA API error fetching historical data: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            raise
    
    async def stream_live_prices(self) -> AsyncGenerator[Dict[str, float], None]:
        """
        Stream live GBP/USD prices.
        
        Yields:
            Dictionary with bid, ask, mid prices and timestamp
        """
        try:
            while True:
                try:
                    price_data = self.get_current_price()
                    yield price_data
                    await asyncio.sleep(1)  # 1 second updates
                except Exception as e:
                    logger.error(f"Error in price stream: {e}")
                    await asyncio.sleep(5)  # Wait before retry
        except Exception as e:
            logger.error(f"Stream error: {e}")
            raise
    
    def get_account_info(self) -> Dict:
        """
        Get account information.
        
        Returns:
            Account details dictionary
        """
        try:
            request = accounts.AccountDetails(accountID=self.account_id)
            response = self.client.request(request)
            return response.get("account", {})
        except V20Error as e:
            logger.error(f"OANDA API error getting account info: {e}")
            raise


# Global instance
oanda_provider = OANDAProvider() if settings.OANDA_API_KEY else None

