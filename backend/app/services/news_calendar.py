"""
High-impact news blackout calendar.

Reads a lightweight JSON calendar of scheduled macro events (NFP, CPI,
FOMC, BoE, ECB, etc.) and lets the signal engine skip entries inside
a configurable blackout window (default ±15 minutes).

Event schema (one entry per event):
    {
      "time": "2026-05-02T12:30:00Z",      # ISO-8601 UTC
      "currency": "USD",                    # affected currency
      "impact": "high",                     # low | medium | high
      "title": "Nonfarm Payrolls"
    }

Only events with impact == "high" trigger a blackout.

Both recurring events (e.g. "every first Friday at 12:30Z", "every Wed
14:30Z FOMC") and one-off events can be encoded directly — the file is
easy to update weekly from ForexFactory / Investing.com.

A small in-process cache reloads the file at most once per minute so
operators can edit the calendar live.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

from app.config import settings
from app.utils.logger import logger


_CACHE: List[dict] = []
_CACHE_MTIME: float = 0.0
_CACHE_LAST_CHECK: float = 0.0
_CACHE_TTL_SEC: float = 60.0


def _calendar_path() -> Path:
    """Resolve news calendar path (absolute or relative to repo root)."""
    p = Path(settings.NEWS_CALENDAR_PATH)
    if p.is_absolute():
        return p
    # backend/app/services/news_calendar.py → project root is 4 levels up
    return Path(__file__).resolve().parents[3] / p


def _load_calendar(force: bool = False) -> List[dict]:
    """Load and cache events from disk, reloading if mtime changes."""
    global _CACHE, _CACHE_MTIME, _CACHE_LAST_CHECK

    now = time.time()
    if not force and (now - _CACHE_LAST_CHECK) < _CACHE_TTL_SEC and _CACHE:
        return _CACHE

    _CACHE_LAST_CHECK = now
    path = _calendar_path()
    if not path.exists():
        return _CACHE  # silently keep previous cache; a missing file = no blackouts

    try:
        mtime = path.stat().st_mtime
        if mtime == _CACHE_MTIME and _CACHE:
            return _CACHE
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        events: List[dict] = []
        for ev in raw if isinstance(raw, list) else raw.get("events", []):
            try:
                ts = datetime.fromisoformat(ev["time"].replace("Z", "+00:00"))
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                events.append({
                    "time": ts,
                    "currency": str(ev.get("currency", "")).upper(),
                    "impact": str(ev.get("impact", "low")).lower(),
                    "title": ev.get("title", "Unknown event"),
                })
            except Exception as e:
                logger.warning(f"news_calendar: skipped malformed event {ev}: {e}")
        _CACHE = events
        _CACHE_MTIME = mtime
        logger.info(f"news_calendar: loaded {len(events)} events from {path}")
    except Exception as e:
        logger.error(f"news_calendar: failed to load {path}: {e}")
    return _CACHE


def _pair_currencies(pair: str) -> Tuple[str, str]:
    """'GBP_USD' → ('GBP', 'USD'). Accepts '_' or '/' separators."""
    s = pair.replace("/", "_").upper()
    if "_" in s and len(s) >= 7:
        a, b = s.split("_", 1)
        return a[:3], b[:3]
    return s[:3], s[3:6] if len(s) >= 6 else ""


def is_in_blackout(pair: str, now: Optional[datetime] = None) -> Tuple[bool, Optional[str]]:
    """
    Check whether *now* falls inside a ±window around a high-impact event
    affecting either leg of the pair.

    Returns:
        (in_blackout, event_label)  — label is human-readable (e.g. "USD CPI")
    """
    if not settings.NEWS_BLACKOUT_ENABLED:
        return (False, None)

    events = _load_calendar()
    if not events:
        return (False, None)

    now = now or datetime.now(timezone.utc)
    before = timedelta(minutes=settings.NEWS_BLACKOUT_MINUTES_BEFORE)
    after = timedelta(minutes=settings.NEWS_BLACKOUT_MINUTES_AFTER)

    base, quote = _pair_currencies(pair)
    affected = {base, quote}

    for ev in events:
        if ev["impact"] != "high":
            continue
        if ev["currency"] and ev["currency"] not in affected:
            continue
        if (ev["time"] - before) <= now <= (ev["time"] + after):
            return (True, f"{ev['currency']} {ev['title']}")

    return (False, None)


def upcoming_events(pair: str, hours_ahead: int = 24) -> List[dict]:
    """Return high-impact events affecting this pair in the next N hours (for UI)."""
    events = _load_calendar()
    if not events:
        return []
    now = datetime.now(timezone.utc)
    horizon = now + timedelta(hours=hours_ahead)
    base, quote = _pair_currencies(pair)
    affected = {base, quote}
    out = []
    for ev in events:
        if ev["impact"] != "high":
            continue
        if ev["currency"] and ev["currency"] not in affected:
            continue
        if now <= ev["time"] <= horizon:
            out.append({
                "time": ev["time"].isoformat(),
                "currency": ev["currency"],
                "title": ev["title"],
                "impact": ev["impact"],
            })
    return sorted(out, key=lambda e: e["time"])
