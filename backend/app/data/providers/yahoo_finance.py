"""Yahoo Finance API integration (backup data provider)."""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from app.utils.logger import logger


class YahooFinanceProvider:
    """Yahoo Finance API data provider (backup)."""
    
    def __init__(self):
        """Initialize Yahoo Finance provider."""
        self.symbol = "GBPUSD=X"
    
    def get_current_price(self) -> Dict[str, float]:
        """
        Get current GBP/USD price.
        
        Returns:
            Dictionary with bid, ask, and mid prices
        """
        try:
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            # Yahoo Finance provides bid/ask
            bid = float(info.get('bid', 0))
            ask = float(info.get('ask', 0))
            mid = float(info.get('regularMarketPrice', (bid + ask) / 2))
            
            return {
                "bid": bid,
                "ask": ask,
                "mid": mid,
                "spread": ask - bid if ask > 0 and bid > 0 else 0.0002,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Yahoo Finance API error: {e}")
            raise
    
    def get_historical_data(
        self,
        timeframe: str = "1m",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: Optional[str] = None
    ) -> List[Dict]:
        """
        Get historical OHLCV data from Yahoo Finance.
        
        Args:
            timeframe: Timeframe (1m, 5m, 15m, 1h, 1d)
            start_date: Start date
            end_date: End date
            period: Period string (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Returns:
            List of OHLCV dictionaries
        """
        try:
            ticker = yf.Ticker(self.symbol)
            
            if period:
                data = ticker.history(period=period, interval=timeframe)
            elif start_date and end_date:
                data = ticker.history(start=start_date, end=end_date, interval=timeframe)
            else:
                # Default to 1 year
                data = ticker.history(period="1y", interval=timeframe)
            
            candles = []
            for idx, row in data.iterrows():
                candles.append({
                    "timestamp": idx.isoformat(),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume']) if 'Volume' in row else 0
                })
            
            return candles
        except Exception as e:
            logger.error(f"Yahoo Finance API error fetching historical data: {e}")
            raise


# Global instance
yahoo_finance_provider = YahooFinanceProvider()

