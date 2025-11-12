"""Live data feed streaming."""

import asyncio
from typing import AsyncGenerator, Dict, Optional
from datetime import datetime
from app.data.providers.oanda import oanda_provider
from app.data.providers.alpha_vantage import alpha_vantage_provider
from app.data.providers.yahoo_finance import yahoo_finance_provider
from app.utils.logger import logger


async def stream_gbpusd_live(
    provider: str = "oanda",
    update_interval: float = 1.0
) -> AsyncGenerator[Dict, None]:
    """
    Stream live GBP/USD prices.
    
    Args:
        provider: Data provider (oanda, alpha_vantage, yahoo)
        update_interval: Update interval in seconds (default: 1.0)
    
    Yields:
        Dictionary with price data: {symbol, timestamp, bid, ask, mid, spread}
    """
    providers = []
    
    # Setup provider
    if provider == "oanda" and oanda_provider:
        providers.append(("oanda", oanda_provider))
    if provider == "alpha_vantage" and alpha_vantage_provider:
        providers.append(("alpha_vantage", alpha_vantage_provider))
    if not providers:
        providers.append(("yahoo", yahoo_finance_provider))
    
    current_provider = None
    provider_name = None
    
    for name, prov in providers:
        try:
            # Test connection
            if name == "oanda":
                prov.get_current_price()
            elif name == "alpha_vantage":
                prov.get_current_price()
            else:
                prov.get_current_price()
            
            current_provider = prov
            provider_name = name
            logger.info(f"Using {provider_name} for live data streaming")
            break
        except Exception as e:
            logger.warning(f"Provider {name} failed: {e}")
            continue
    
    if not current_provider:
        raise Exception("No available data provider for live streaming")
    
    # Stream prices
    consecutive_errors = 0
    max_errors = 5
    
    while True:
        try:
            if provider_name == "oanda" and hasattr(current_provider, 'stream_live_prices'):
                async for price_data in current_provider.stream_live_prices():
                    yield {
                        "symbol": "GBP_USD",
                        "timestamp": price_data.get("timestamp", datetime.utcnow().isoformat()),
                        "bid": price_data["bid"],
                        "ask": price_data["ask"],
                        "mid": price_data["mid"],
                        "spread": price_data["spread"]
                    }
            else:
                # Poll-based streaming for other providers
                price_data = current_provider.get_current_price()
                yield {
                    "symbol": "GBP_USD",
                    "timestamp": price_data.get("timestamp", datetime.utcnow().isoformat()),
                    "bid": price_data["bid"],
                    "ask": price_data["ask"],
                    "mid": price_data["mid"],
                    "spread": price_data["spread"]
                }
                await asyncio.sleep(update_interval)
            
            consecutive_errors = 0  # Reset error counter on success
        
        except Exception as e:
            consecutive_errors += 1
            logger.error(f"Error in live stream (attempt {consecutive_errors}/{max_errors}): {e}")
            
            if consecutive_errors >= max_errors:
                logger.error("Max consecutive errors reached. Attempting provider fallback...")
                # Try next provider
                found_next = False
                for name, prov in providers:
                    if name != provider_name:
                        try:
                            prov.get_current_price()
                            current_provider = prov
                            provider_name = name
                            consecutive_errors = 0
                            found_next = True
                            logger.info(f"Switched to {provider_name} provider")
                            break
                        except Exception:
                            continue
                
                if not found_next:
                    logger.error("All providers failed. Waiting before retry...")
                    await asyncio.sleep(10)
                    consecutive_errors = 0
            else:
                await asyncio.sleep(update_interval)

