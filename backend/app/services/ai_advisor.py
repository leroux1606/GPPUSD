"""
AI trading advisor — supports Anthropic, OpenAI, and OpenRouter.

Provider is selected via settings.AI_PROVIDER:
  'anthropic'  → Anthropic Messages API (claude-*)
  'openai'     → OpenAI Chat Completions API (gpt-*)
  'openrouter' → OpenRouter (any model, including free ones)
"""

import httpx
from typing import Optional
from app.config import settings
from app.utils.logger import logger


SYSTEM_PROMPT = """You are an expert FX day trader with 20 years of experience.
Your job is to give concise, practical trading advice based on current market conditions.
Be direct and actionable. Focus on:
- What the market is doing RIGHT NOW
- Key levels to watch (support/resistance)
- Whether conditions favour a specific bias (bullish/bearish/neutral)
- Any warnings or notable risks
Keep responses under 120 words. Use plain English, no jargon overload."""


# ── Provider / model resolution ───────────────────────────────────────────────

def _resolve_provider_and_model() -> tuple[str, str, str]:
    """
    Return (provider, model, api_key).
    Falls back gracefully if the preferred provider has no key configured.
    """
    provider = settings.AI_PROVIDER.lower().strip()

    # Explicit model override wins; otherwise use provider-specific defaults
    if provider == "anthropic":
        key   = settings.ANTHROPIC_API_KEY
        model = settings.AI_MODEL or "claude-sonnet-4-6"
    elif provider == "openai":
        key   = settings.OPENAI_API_KEY
        model = settings.AI_MODEL or "gpt-4o-mini"
    else:  # openrouter (default)
        key   = settings.OPENROUTER_API_KEY
        model = settings.AI_MODEL or settings.OPENROUTER_MODEL or "meta-llama/llama-3.1-8b-instruct:free"
        provider = "openrouter"

    return provider, model, key


def _is_configured() -> bool:
    provider, _, key = _resolve_provider_and_model()
    return bool(key)


# ── Anthropic Messages API ────────────────────────────────────────────────────

async def _call_anthropic(model: str, api_key: str, prompt: str, max_tokens: int) -> Optional[str]:
    headers = {
        "x-api-key":         api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type":      "application/json",
    }
    payload = {
        "model":      model,
        "max_tokens": max_tokens,
        "system":     SYSTEM_PROMPT,
        "messages":   [{"role": "user", "content": prompt}],
    }
    async with httpx.AsyncClient(timeout=25.0) as client:
        resp = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["content"][0]["text"].strip()
    logger.warning(f"Anthropic {resp.status_code}: {resp.text[:200]}")
    return None


# ── OpenAI-compatible API (OpenAI and OpenRouter share the same format) ────────

async def _call_openai_compat(
    model: str, api_key: str, prompt: str, max_tokens: int,
    base_url: str = "https://api.openai.com/v1/chat/completions",
    extra_headers: Optional[dict] = None,
) -> Optional[str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json",
        **(extra_headers or {}),
    }
    payload = {
        "model":      model,
        "max_tokens": max_tokens,
        "temperature": 0.4,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
    }
    async with httpx.AsyncClient(timeout=25.0) as client:
        resp = await client.post(base_url, headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"].strip()
    logger.warning(f"OpenAI-compat {resp.status_code}: {resp.text[:200]}")
    return None


# ── Dispatcher ────────────────────────────────────────────────────────────────

async def _call_ai(prompt: str, max_tokens: int = 180) -> Optional[str]:
    provider, model, key = _resolve_provider_and_model()

    if not key:
        logger.warning(f"AI provider '{provider}' has no API key configured")
        return None

    try:
        if provider == "anthropic":
            return await _call_anthropic(model, key, prompt, max_tokens)
        elif provider == "openai":
            return await _call_openai_compat(model, key, prompt, max_tokens)
        else:  # openrouter
            return await _call_openai_compat(
                model, key, prompt, max_tokens,
                base_url="https://openrouter.ai/api/v1/chat/completions",
                extra_headers={
                    "HTTP-Referer": "https://fx-trader.local",
                    "X-Title": "FX Trader",
                },
            )
    except Exception as e:
        logger.error(f"AI advisor error ({provider}/{model}): {e}")
        return None


# ── Public API ────────────────────────────────────────────────────────────────

async def get_market_commentary(context: dict) -> Optional[str]:
    """AI market commentary based on current context."""
    if not _is_configured():
        return None

    pair    = context.get("display", context.get("pair", "GBP/USD"))
    price   = context.get("price", "N/A")
    session = context.get("session", "Unknown")
    signals = context.get("signals", [])
    signal_text = ", ".join(
        f"{s['direction'].upper()} ({s['strategy']})" for s in signals
    ) or "None"

    prompt = f"""Current {pair} market state:
- Price: {price}  |  Session: {session}
- Daily range: {context.get('daily_low','N/A')} – {context.get('daily_high','N/A')}
- ATR (14): {context.get('atr_pips','N/A')} pips  |  RSI (14): {context.get('rsi','N/A')}
- Trend: {context.get('trend','N/A')}
- Active signals: {signal_text}

Provide a brief market assessment and actionable advice."""

    return await _call_ai(prompt, max_tokens=180)


async def analyze_trade_setup(signal: dict, context: dict) -> Optional[str]:
    """AI assessment of a specific trade setup."""
    if not _is_configured():
        return None

    direction = signal.get("direction", "buy").upper()
    strategy  = signal.get("strategy", "unknown")
    entry     = signal.get("entry", 0)
    sl        = signal.get("stop_loss", 0)
    tp        = signal.get("take_profit", 0)
    rr        = signal.get("rr_ratio", 0)
    pair      = signal.get("pair_display", "GBP/USD")

    prompt = f"""{pair} {direction} signal from {strategy}.
Entry {entry} | SL {sl} | TP {tp} | R/R 1:{rr:.2f}
RSI={context.get('rsi','N/A')}, Session={context.get('session','N/A')}, \
Position={context.get('range_position','N/A')}

In 2-3 sentences: is this setup worth taking? Any caveats?"""

    return await _call_ai(prompt, max_tokens=100)


async def test_connection() -> dict:
    """Quick ping to verify AI connectivity. Returns {ok, provider, model, message}."""
    provider, model, key = _resolve_provider_and_model()
    if not key:
        return {"ok": False, "provider": provider, "model": model,
                "message": f"No API key for provider '{provider}'"}
    result = await _call_ai("Reply with exactly: OK", max_tokens=10)
    if result:
        return {"ok": True, "provider": provider, "model": model,
                "message": f"Connected — {provider}/{model}"}
    return {"ok": False, "provider": provider, "model": model,
            "message": "Request failed — check API key and model name"}
