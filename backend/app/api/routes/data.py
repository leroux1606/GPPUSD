"""Data API routes."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import pandas as pd
from app.data.data_manager import data_manager
from app.data.live_feed import stream_gbpusd_live
from app.utils.logger import logger

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("/live")
async def get_live_price():
    """Get current GBP/USD price via Yahoo Finance (no broker required)."""
    import requests as _requests
    from datetime import timezone

    cached = data_manager.get_latest_price()
    if cached:
        return cached

    try:
        resp = _requests.get(
            "https://query1.finance.yahoo.com/v8/finance/chart/GBPUSD=X"
            "?interval=1m&range=1d",
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        result = resp.json().get("chart", {}).get("result", [{}])[0]
        meta   = result.get("meta", {})
        mid    = float(meta.get("regularMarketPrice") or meta.get("previousClose", 0))
        bid    = round(mid - 0.0001, 5)
        ask    = round(mid + 0.0001, 5)
        price_data = {
            "symbol": "GBP_USD",
            "bid":    bid,
            "ask":    ask,
            "mid":    mid,
            "spread": round(ask - bid, 5),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        data_manager.cache_latest_price("GBP_USD", price_data)
        return price_data
    except Exception as e:
        logger.error(f"Error getting live price: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical")
async def get_historical_data(
    symbol: str = Query(default="GBP_USD"),
    timeframe: str = Query(default="1h"),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None)
):
    """Get historical OHLCV data."""
    # Map frontend timeframe strings to OANDA format used by get_historical_async
    _TF_MAP = {
        "1m": "M1", "5m": "M5", "15m": "M15", "30m": "M30",
        "1h": "H1", "4h": "H4", "1d": "D", "1w": "W",
        # pass-through if already in OANDA format
        "M1": "M1", "M5": "M5", "M15": "M15", "M30": "M30",
        "H1": "H1", "H4": "H4", "D": "D",
    }
    oanda_tf = _TF_MAP.get(timeframe, "H1")

    # Determine count from date range or default to 300 bars
    count = 300
    if start_date and end_date:
        try:
            start = datetime.fromisoformat(start_date)
            end   = datetime.fromisoformat(end_date)
            tf_minutes = {"M1":1,"M5":5,"M15":15,"M30":30,"H1":60,"H4":240,"D":1440}.get(oanda_tf, 60)
            count = max(100, int((end - start).total_seconds() / 60 / tf_minutes) + 10)
        except Exception:
            pass

    try:
        df = await data_manager.get_historical_async(
            symbol=symbol,
            timeframe=oanda_tf,
            count=count,
        )

        if df is None or df.empty:
            raise HTTPException(status_code=503, detail="No data available from data provider")

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": df.to_dict('records'),
            "count": len(df)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download")
async def download_historical_data(
    symbol: str = Query(default="GBP_USD"),
    timeframe: str = Query(default="1h"),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    provider: str = Query(default="oanda")
):
    """Download and cache historical data."""
    try:
        from app.data.historical import download_historical, save_historical_data
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        df = await download_historical(symbol, timeframe, start, end, provider)
        filepath = save_historical_data(df, symbol, timeframe)
        
        return {
            "status": "success",
            "filepath": filepath,
            "records": len(df),
            "start_date": df['timestamp'].min().isoformat() if len(df) > 0 else None,
            "end_date": df['timestamp'].max().isoformat() if len(df) > 0 else None
        }
    except Exception as e:
        logger.error(f"Error downloading historical data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeframes")
async def get_timeframes():
    """Get available timeframes."""
    return {
        "timeframes": ["1m", "5m", "15m", "1h", "4h", "1d"],
        "default": "1h"
    }

