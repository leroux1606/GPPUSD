"""Telegram notification service."""

import httpx
from app.config import settings
from app.utils.logger import logger


PRIORITY_EMOJI = {
    "info": "ℹ️",
    "opportunity": "🎯",
    "warning": "⚠️",
    "danger": "🚨",
}

PRIORITY_ORDER = ["info", "opportunity", "warning", "danger"]


async def send_telegram(message: str, priority: str = "info") -> bool:
    """
    Send a notification to Telegram.

    Returns True if sent, False if skipped or failed.
    """
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return False

    # Check minimum priority threshold
    min_idx = PRIORITY_ORDER.index(settings.TELEGRAM_MIN_PRIORITY) if settings.TELEGRAM_MIN_PRIORITY in PRIORITY_ORDER else 1
    cur_idx = PRIORITY_ORDER.index(priority) if priority in PRIORITY_ORDER else 0
    if cur_idx < min_idx:
        return False

    emoji = PRIORITY_EMOJI.get(priority, "📊")
    text = f"{emoji} *GBP/USD Trader*\n\n{message}"

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                logger.info(f"Telegram sent: [{priority}] {message[:60]}")
                return True
            else:
                logger.warning(f"Telegram failed {resp.status_code}: {resp.text[:200]}")
                return False
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return False


async def send_signal_notification(signal: dict) -> bool:
    """Format and send a trading signal to Telegram."""
    direction = "BUY 📈" if signal["direction"] == "buy" else "SELL 📉"
    lines = [
        f"*{direction} Signal — {signal['strategy']}*",
        f"Entry:  `{signal['entry']:.5f}`",
        f"SL:     `{signal['stop_loss']:.5f}` ({signal['risk_pips']:.1f} pips)",
        f"TP:     `{signal['take_profit']:.5f}` ({signal['reward_pips']:.1f} pips)",
        f"R/R:    `1:{signal['rr_ratio']:.2f}`",
        f"Lot:    `{signal['suggested_lot']:.2f}`",
    ]
    if signal.get("comment"):
        lines.append(f"\n_{signal['comment']}_")

    return await send_telegram("\n".join(lines), priority="opportunity")


async def send_warning_notification(message: str) -> bool:
    """Send a risk warning to Telegram."""
    return await send_telegram(message, priority="warning")
