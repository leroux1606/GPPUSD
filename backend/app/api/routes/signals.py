"""Live signals and settings API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.config import settings
from app.services.ai_advisor import get_market_commentary
from app.services.notifications import send_telegram
from app.utils.logger import logger

router = APIRouter(prefix="/api/signals", tags=["signals"])


# ── Settings models ────────────────────────────────────────────────────────────

class NotificationSettings(BaseModel):
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    telegram_min_priority: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = None
    active_strategies: Optional[str] = None
    signal_scan_interval: Optional[int] = None
    risk_per_trade_pct: Optional[float] = None


class AICommentaryRequest(BaseModel):
    context: dict


class TelegramTestRequest(BaseModel):
    message: str = "Test notification from GBP/USD Trader ✅"


# ── Settings endpoints ─────────────────────────────────────────────────────────

@router.get("/settings")
async def get_settings():
    """Get current notification and signal settings (tokens masked)."""
    def mask(val: str) -> str:
        if not val:
            return ""
        return val[:6] + "..." if len(val) > 6 else "***"

    return {
        "telegram_bot_token": mask(settings.TELEGRAM_BOT_TOKEN),
        "telegram_chat_id": settings.TELEGRAM_CHAT_ID,
        "telegram_min_priority": settings.TELEGRAM_MIN_PRIORITY,
        "openrouter_api_key": mask(settings.OPENROUTER_API_KEY),
        "openrouter_model": settings.OPENROUTER_MODEL,
        "active_strategies": settings.ACTIVE_STRATEGIES,
        "signal_scan_interval": settings.SIGNAL_SCAN_INTERVAL,
        "risk_per_trade_pct": settings.DEFAULT_RISK_PER_TRADE_PCT,
        "telegram_configured": bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID),
        "ai_configured": bool(settings.OPENROUTER_API_KEY),
    }


@router.post("/settings")
async def update_settings(body: NotificationSettings):
    """
    Update runtime settings.
    Note: These are runtime-only; persist them to .env for permanence.
    """
    if body.telegram_bot_token is not None:
        settings.TELEGRAM_BOT_TOKEN = body.telegram_bot_token
    if body.telegram_chat_id is not None:
        settings.TELEGRAM_CHAT_ID = body.telegram_chat_id
    if body.telegram_min_priority is not None:
        settings.TELEGRAM_MIN_PRIORITY = body.telegram_min_priority
    if body.openrouter_api_key is not None:
        settings.OPENROUTER_API_KEY = body.openrouter_api_key
    if body.openrouter_model is not None:
        settings.OPENROUTER_MODEL = body.openrouter_model
    if body.active_strategies is not None:
        settings.ACTIVE_STRATEGIES = body.active_strategies
    if body.signal_scan_interval is not None:
        settings.SIGNAL_SCAN_INTERVAL = body.signal_scan_interval
    if body.risk_per_trade_pct is not None:
        settings.DEFAULT_RISK_PER_TRADE_PCT = body.risk_per_trade_pct

    return {"success": True, "message": "Settings updated for this session"}


# ── AI Advisor ─────────────────────────────────────────────────────────────────

@router.post("/ai-commentary")
async def get_ai_commentary(body: AICommentaryRequest):
    """Get AI market commentary based on provided context."""
    if not settings.OPENROUTER_API_KEY:
        raise HTTPException(status_code=400, detail="OpenRouter API key not configured")

    commentary = await get_market_commentary(body.context)
    if commentary is None:
        raise HTTPException(status_code=502, detail="AI service unavailable")

    return {"commentary": commentary}


# ── Telegram ───────────────────────────────────────────────────────────────────

@router.post("/telegram/test")
async def test_telegram(body: TelegramTestRequest):
    """Send a test Telegram message to verify the bot is working."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        raise HTTPException(status_code=400, detail="Telegram not configured")

    success = await send_telegram(body.message, priority="info")
    if not success:
        raise HTTPException(status_code=502, detail="Failed to send Telegram message — check token and chat ID")

    return {"success": True, "message": "Test message sent to Telegram"}
