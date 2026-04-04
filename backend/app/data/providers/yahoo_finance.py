"""Yahoo Finance API integration (backup data provider)."""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
import requests
import pandas as pd
from app.utils.logger import logger

_YF_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

# Map common timeframe strings to Yahoo Finance intervals
_TF_MAP = {
    "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
    "1h": "1h", "4h": "1h", "1d": "1d",
    "M1": "1m", "M5": "5m", "M15": "15m", "M30": "30m",
    "H1": "1h", "H4": "1h", "D": "1d",
}


class YahooFinanceProvider:
    """Yahoo Finance API data provider — uses direct HTTP, no API key required."""

    def __init__(self, symbol: str = "GBPUSD=X"):
        self.symbol = symbol

    def _chart(self, interval: str, range_: str) -> dict:
        """Call the Yahoo Finance v8 chart endpoint."""
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/{self.symbol}"
            f"?interval={interval}&range={range_}"
        )
        resp = requests.get(url, headers=_YF_HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_current_price(self) -> Dict[str, float]:
        try:
            data   = self._chart("1m", "1d")
            result = data.get("chart", {}).get("result", [{}])[0]
            meta   = result.get("meta", {})
            mid    = float(meta.get("regularMarketPrice") or meta.get("previousClose", 0))
            bid    = round(mid - 0.0001, 5)
            ask    = round(mid + 0.0001, 5)
            return {
                "bid": bid, "ask": ask, "mid": mid,
                "spread": round(ask - bid, 5),
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Yahoo Finance price error: {e}")
            raise

    def get_historical_data(
        self,
        timeframe: str = "1h",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: Optional[str] = None,
    ) -> List[Dict]:
        try:
            interval = _TF_MAP.get(timeframe, "1h")

            if period:
                range_ = period
            elif start_date:
                days = max(1, (datetime.utcnow() - start_date).days)
                if   days <= 1:  range_ = "1d"
                elif days <= 5:  range_ = "5d"
                elif days <= 30: range_ = "1mo"
                elif days <= 90: range_ = "3mo"
                else:            range_ = "6mo"
            else:
                range_ = "6mo"

            data   = self._chart(interval, range_)
            result = data.get("chart", {}).get("result", [{}])[0]
            timestamps = result.get("timestamp", [])
            quote      = result.get("indicators", {}).get("quote", [{}])[0]

            candles = []
            for i, ts in enumerate(timestamps):
                o = quote.get("open",  [None])[i]
                h = quote.get("high",  [None])[i]
                l = quote.get("low",   [None])[i]
                c = quote.get("close", [None])[i]
                v = quote.get("volume",[0])[i]
                if None in (o, h, l, c):
                    continue
                dt = datetime.utcfromtimestamp(ts)
                if start_date and dt < start_date:
                    continue
                if end_date and dt > end_date:
                    continue
                candles.append({
                    "timestamp": dt.isoformat(),
                    "open": float(o), "high": float(h),
                    "low":  float(l), "close": float(c),
                    "volume": int(v) if v else 0,
                })
            return candles
        except Exception as e:
            logger.error(f"Yahoo Finance historical error: {e}")
            raise


# Global instance
yahoo_finance_provider = YahooFinanceProvider()

