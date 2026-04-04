"""Live signals, settings, and AI routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.config import settings
from app.services.ai_advisor import get_market_commentary, test_connection
from app.services.notifications import send_telegram
from app.utils.logger import logger

router = APIRouter(prefix="/api/signals", tags=["signals"])


# ── Models ─────────────────────────────────────────────────────────────────────

class NotificationSettings(BaseModel):
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    telegram_min_priority: Optional[str] = None
    # AI provider selection
    ai_provider: Optional[str] = None          # 'openrouter' | 'anthropic' | 'openai'
    ai_model: Optional[str] = None             # model string for the selected provider
    openrouter_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    # legacy
    openrouter_model: Optional[str] = None
    # signal engine
    active_strategies: Optional[str] = None
    signal_scan_interval: Optional[int] = None
    risk_per_trade_pct: Optional[float] = None


class AICommentaryRequest(BaseModel):
    context: dict


class TelegramTestRequest(BaseModel):
    message: str = "Test notification from FX Trader ✅"


# ── Settings ───────────────────────────────────────────────────────────────────

@router.get("/settings")
async def get_settings():
    def mask(val: str) -> str:
        return (val[:6] + "...") if len(val) > 6 else ("***" if val else "")

    provider = settings.AI_PROVIDER
    has_key = bool(
        (provider == "anthropic" and settings.ANTHROPIC_API_KEY) or
        (provider == "openai"    and settings.OPENAI_API_KEY) or
        (provider == "openrouter" and settings.OPENROUTER_API_KEY)
    )

    return {
        # Telegram
        "telegram_configured":  bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID),
        "telegram_chat_id":     settings.TELEGRAM_CHAT_ID,
        "telegram_min_priority": settings.TELEGRAM_MIN_PRIORITY,
        # AI
        "ai_configured":        has_key,
        "ai_provider":          settings.AI_PROVIDER,
        "ai_model":             settings.AI_MODEL or settings.OPENROUTER_MODEL,
        "openrouter_api_key":   mask(settings.OPENROUTER_API_KEY),
        "anthropic_api_key":    mask(settings.ANTHROPIC_API_KEY),
        "openai_api_key":       mask(settings.OPENAI_API_KEY),
        # Signal engine
        "active_strategies":    settings.ACTIVE_STRATEGIES,
        "signal_scan_interval": settings.SIGNAL_SCAN_INTERVAL,
        "risk_per_trade_pct":   settings.DEFAULT_RISK_PER_TRADE_PCT,
    }


@router.post("/settings")
async def update_settings(body: NotificationSettings):
    if body.telegram_bot_token   is not None: settings.TELEGRAM_BOT_TOKEN      = body.telegram_bot_token
    if body.telegram_chat_id     is not None: settings.TELEGRAM_CHAT_ID        = body.telegram_chat_id
    if body.telegram_min_priority is not None: settings.TELEGRAM_MIN_PRIORITY  = body.telegram_min_priority
    if body.ai_provider          is not None: settings.AI_PROVIDER             = body.ai_provider
    if body.ai_model             is not None: settings.AI_MODEL                = body.ai_model
    if body.openrouter_api_key   is not None: settings.OPENROUTER_API_KEY      = body.openrouter_api_key
    if body.anthropic_api_key    is not None: settings.ANTHROPIC_API_KEY       = body.anthropic_api_key
    if body.openai_api_key       is not None: settings.OPENAI_API_KEY          = body.openai_api_key
    if body.openrouter_model     is not None: settings.OPENROUTER_MODEL        = body.openrouter_model
    if body.active_strategies    is not None: settings.ACTIVE_STRATEGIES       = body.active_strategies
    if body.signal_scan_interval is not None: settings.SIGNAL_SCAN_INTERVAL    = body.signal_scan_interval
    if body.risk_per_trade_pct   is not None: settings.DEFAULT_RISK_PER_TRADE_PCT = body.risk_per_trade_pct
    return {"success": True}


# ── AI ─────────────────────────────────────────────────────────────────────────

@router.post("/ai-commentary")
async def get_ai_commentary(body: AICommentaryRequest):
    commentary = await get_market_commentary(body.context)
    if commentary is None:
        raise HTTPException(status_code=502, detail="AI service unavailable — check provider and API key")
    return {"commentary": commentary}


@router.post("/ai-test")
async def test_ai():
    """Test the current AI provider/model configuration."""
    result = await test_connection()
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# ── Telegram ───────────────────────────────────────────────────────────────────

@router.post("/telegram/test")
async def test_telegram(body: TelegramTestRequest):
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        raise HTTPException(status_code=400, detail="Telegram not configured")
    success = await send_telegram(body.message, priority="warning")
    if not success:
        raise HTTPException(status_code=502, detail="Failed — check token and chat ID")
    return {"success": True, "message": "Test message sent"}
