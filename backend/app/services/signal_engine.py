"""
Real-time multi-pair signal engine — with session scoring, confluence detection,
and rolling win-rate tracking.

Logic per scan cycle:
  1. For each active pair, run its recommended strategies.
  2. Assign each signal a base confidence from recent win-rate (tracked live).
  3. Detect confluence: 2+ strategies agree on direction → single merged signal.
  4. Apply session-alignment bonus: +15 pts when current session is a prime
     session for that pair.
  5. Emit signals only when the merged confidence > MIN_CONFIDENCE (default 30%).
  6. Suppress re-emitting the same direction on the same strategy until it flips.
"""

import asyncio
from collections import deque
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import pandas as pd

from app.config import settings
from app.strategies.strategy_builder import StrategyBuilder, STRATEGY_REGISTRY
from app.strategies.pair_config import PAIR_CONFIG, get_pair
from app.technical_analysis.indicators import calculate_atr, calculate_rsi, calculate_ema
from app.services.regime_detector import detect_regime, strategy_allowed
from app.services.news_calendar import is_in_blackout
from app.utils.logger import logger

# Minimum confidence to emit a signal (0-100)
MIN_CONFIDENCE = 30
# Win-rate history window per strategy/pair key
WIN_RATE_WINDOW = 20


# ── Session helpers ───────────────────────────────────────────────────────────

def _get_session(hour_utc: int) -> str:
    if 22 <= hour_utc or hour_utc < 7:
        return "Asian"
    elif 7 <= hour_utc < 13:
        return "London"
    elif 13 <= hour_utc < 17:
        return "London/NY Overlap"
    elif 17 <= hour_utc < 22:
        return "NY"
    return "Unknown"


def _session_bonus(session: str, pair_config: dict) -> int:
    """Return +14 if current session is a prime session for this pair, else 0."""
    prime = pair_config.get("prime_sessions", [])
    return 14 if session in prime else 0


# ── Trade-level computation ───────────────────────────────────────────────────

def compute_trade_levels(
    df: pd.DataFrame,
    signal: int,
    pair_symbol: str = "GBP_USD",
    balance: float = 10000,
) -> Dict[str, Any]:
    """
    Compute entry, SL, TP and risk for a signal.
    - SL = 1.5× ATR, TP = 2.2× ATR (R/R ≈ 1:1.47)
    - Lot size = risk_pct of balance / (risk_pips × pip_value_usd)
    """
    if signal == 0 or len(df) < 15:
        return {}

    pair      = get_pair(pair_symbol)
    pip_mult  = pair["pip_multiplier"]
    pip_val   = pair["pip_value_usd"]
    decimals  = 3 if pair_symbol == "USD_JPY" else 5

    close = float(df["close"].iloc[-1])
    atr_s = calculate_atr(df, 14)
    atr   = float(atr_s.dropna().iloc[-1]) if not atr_s.dropna().empty else (
        0.01 if pair_symbol == "USD_JPY" else 0.001
    )

    sl_dist = atr * 1.5
    tp_dist = atr * 2.2

    if signal == 1:
        entry       = close
        stop_loss   = round(entry - sl_dist, decimals)
        take_profit = round(entry + tp_dist, decimals)
    else:
        entry       = close
        stop_loss   = round(entry + sl_dist, decimals)
        take_profit = round(entry - tp_dist, decimals)

    risk_pips   = sl_dist * pip_mult
    reward_pips = tp_dist * pip_mult
    rr_ratio    = round(tp_dist / sl_dist, 2)

    risk_amount   = balance * (settings.DEFAULT_RISK_PER_TRADE_PCT / 100)
    suggested_lot = round(risk_amount / (risk_pips * pip_val), 2)
    suggested_lot = max(0.01, min(suggested_lot, 2.0))

    return {
        "entry":         round(entry, decimals),
        "stop_loss":     stop_loss,
        "take_profit":   take_profit,
        "risk_pips":     round(risk_pips, 1),
        "reward_pips":   round(reward_pips, 1),
        "rr_ratio":      rr_ratio,
        "suggested_lot": suggested_lot,
        "atr_pips":      round(atr * pip_mult, 1),
    }


# ── Market context ────────────────────────────────────────────────────────────

def build_market_context(
    df: pd.DataFrame,
    pair_symbol: str,
    signals: List[dict],
) -> Dict[str, Any]:
    if len(df) < 20:
        return {}

    pair     = get_pair(pair_symbol)
    pip_mult = pair["pip_multiplier"]

    close      = float(df["close"].iloc[-1])
    high_today = float(df["high"].tail(96).max())
    low_today  = float(df["low"].tail(96).min())
    daily_range = high_today - low_today

    rsi_s = calculate_rsi(df, 14)
    rsi   = round(float(rsi_s.dropna().iloc[-1]), 1) if not rsi_s.dropna().empty else None

    ema50 = calculate_ema(df, 50)
    trend = "above EMA50" if close > float(ema50.dropna().iloc[-1]) else "below EMA50"

    atr_s    = calculate_atr(df, 14)
    atr_pips = round(float(atr_s.dropna().iloc[-1]) * pip_mult, 1) if not atr_s.dropna().empty else None

    hour_utc = datetime.now(timezone.utc).hour
    session  = _get_session(hour_utc)

    range_pct = (close - low_today) / daily_range * 100 if daily_range > 0 else 50
    if range_pct > 80:
        range_position = "near daily HIGH"
    elif range_pct < 20:
        range_position = "near daily LOW"
    else:
        range_position = f"{range_pct:.0f}% of daily range"

    decimals = 3 if pair_symbol == "USD_JPY" else 5

    return {
        "pair":           pair_symbol,
        "display":        pair["display"],
        "price":          round(close, decimals),
        "session":        session,
        "daily_high":     round(high_today, decimals),
        "daily_low":      round(low_today, decimals),
        "atr_pips":       atr_pips,
        "rsi":            rsi,
        "trend":          trend,
        "range_position": range_position,
        "signals":        signals,
    }


# ── Risk warnings ─────────────────────────────────────────────────────────────

def check_risk_warnings(
    df: pd.DataFrame,
    pair_symbol: str,
    balance: float,
    equity: float,
) -> List[dict]:
    warnings = []
    if len(df) < 20:
        return warnings

    pair_display = get_pair(pair_symbol)["display"]
    hour_utc = datetime.now(timezone.utc).hour

    rsi_s = calculate_rsi(df, 14)
    if not rsi_s.dropna().empty:
        rsi = float(rsi_s.dropna().iloc[-1])
        if rsi > 78:
            warnings.append({"type": "warning", "message": f"{pair_display} RSI overbought ({rsi:.0f}) — avoid new longs"})
        elif rsi < 22:
            warnings.append({"type": "warning", "message": f"{pair_display} RSI oversold ({rsi:.0f}) — avoid new shorts"})

    if equity < balance * 0.98:
        loss_pct = (balance - equity) / balance * 100
        warnings.append({"type": "warning", "message": f"Down {loss_pct:.1f}% today — consider reducing size"})
    if equity < balance * 0.95:
        warnings.append({"type": "danger", "message": f"STOP — equity down {((balance - equity) / balance * 100):.1f}%"})

    if hour_utc in [7, 9, 13, 14, 15]:
        warnings.append({"type": "info", "message": f"⏰ {hour_utc:02d}:00 GMT — possible news. Watch spreads."})

    if pair_symbol in ("USD_CAD",) and not (13 <= hour_utc < 21):
        warnings.append({"type": "info", "message": f"{pair_display} — low activity outside NY session"})

    return warnings


# ── Rolling win-rate tracker ──────────────────────────────────────────────────

class WinRateTracker:
    """
    Tracks the outcome of each signal (SL hit = loss, TP hit = win).
    Evaluates pending signals on every scan using the latest price.
    Win rate per key drives the base confidence score.
    """

    def __init__(self, window: int = WIN_RATE_WINDOW):
        self._window  = window
        self._history: Dict[str, deque] = {}   # key → deque[0|1]
        self._pending: List[dict] = []         # signals waiting for resolution

    def record_signal(self, key: str, direction: str, entry: float,
                      stop_loss: float, take_profit: float,
                      max_bars: int = 16) -> None:
        """Register a new signal for outcome tracking (max_bars ≈ 4 h on M15)."""
        self._pending.append({
            "key":          key,
            "direction":    direction,
            "entry":        entry,
            "stop_loss":    stop_loss,
            "take_profit":  take_profit,
            "bars_left":    max_bars,
        })

    def update(self, current_price: float) -> None:
        """Called each scan cycle; resolves signals whose SL/TP has been hit."""
        remaining = []
        for p in self._pending:
            if p["direction"] == "buy":
                if current_price <= p["stop_loss"]:
                    self._record(p["key"], 0)        # loss
                    continue
                if current_price >= p["take_profit"]:
                    self._record(p["key"], 1)        # win
                    continue
            else:  # sell
                if current_price >= p["stop_loss"]:
                    self._record(p["key"], 0)
                    continue
                if current_price <= p["take_profit"]:
                    self._record(p["key"], 1)
                    continue

            p["bars_left"] -= 1
            if p["bars_left"] > 0:
                remaining.append(p)
            # expired without resolution → not recorded (neutral)
        self._pending = remaining

    def win_rate(self, key: str) -> Optional[float]:
        """Return win rate 0.0–1.0, or None if no history yet."""
        h = self._history.get(key)
        if not h:
            return None
        return sum(h) / len(h)

    def _record(self, key: str, outcome: int) -> None:
        if key not in self._history:
            self._history[key] = deque(maxlen=self._window)
        self._history[key].append(outcome)
        logger.debug(f"Win-rate update {key}: outcome={'WIN' if outcome else 'LOSS'}, "
                     f"rate={self.win_rate(key):.0%}")


# ── Confidence calculator ─────────────────────────────────────────────────────

def _compute_confidence(
    win_rate: Optional[float],
    confluence_count: int,
    session_bonus: int,
) -> int:
    """
    Combine three signals into a 0-99 confidence score.
    - Base: win_rate × 55  (0–55 pts; default 27 when no history)
    - Confluence: +15 per extra agreeing strategy (beyond the first), capped at +30
    - Session alignment: +14 when in a prime session for the pair
    Max achievable: 55 + 30 + 14 = 99.
    """
    base = round((win_rate if win_rate is not None else 0.5) * 55)
    conf_bonus = min(30, max(0, confluence_count - 1) * 15)
    sess = min(14, max(0, session_bonus))
    total = max(0, min(99, base + conf_bonus + sess))
    return total


# ── Signal Engine ─────────────────────────────────────────────────────────────

class SignalEngine:
    """Scans multiple pairs and their recommended strategies every scan interval."""

    def __init__(self, broadcast_fn):
        self.broadcast   = broadcast_fn
        self._task: Optional[asyncio.Task] = None
        self._last: Dict[str, int] = {}    # f"{pair}:{strategy}" → last signal value
        self._balance    = 10000.0
        self._equity     = 10000.0
        self._positions: list = []
        self._tracker    = WinRateTracker()

    # ── lifecycle ────────────────────────────────────────────────────────────

    def start(self):
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(self._run())
        logger.info("Multi-pair signal engine started (session scoring + confluence + win-rate)")

    def stop(self):
        if self._task:
            self._task.cancel()
            logger.info("Signal engine stopped")

    def update_account(self, balance: float, equity: float, positions: list):
        self._balance   = balance
        self._equity    = equity
        self._positions = positions

    # ── main loop ────────────────────────────────────────────────────────────

    async def _run(self):
        while True:
            try:
                await self._scan_all()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Signal scan error: {e}")
            await asyncio.sleep(settings.SIGNAL_SCAN_INTERVAL)

    # ── scan ─────────────────────────────────────────────────────────────────

    async def _scan_all(self):
        from app.data.data_manager import DataManager
        dm = DataManager()

        hour_utc    = datetime.now(timezone.utc).hour
        session_now = _get_session(hour_utc)
        active_pairs = [p.strip() for p in settings.ACTIVE_PAIRS.split(",") if p.strip()]
        all_signals: List[dict] = []

        for pair_symbol in active_pairs:
            if pair_symbol not in PAIR_CONFIG:
                continue

            try:
                df = await dm.get_historical_async(symbol=pair_symbol, timeframe="M15", count=300)
            except Exception as e:
                logger.warning(f"Data fetch failed for {pair_symbol}: {e}")
                continue

            if df is None or len(df) < 50:
                continue

            current_price = float(df["close"].iloc[-1])
            self._tracker.update(current_price)   # resolve pending signals

            pair_cfg    = PAIR_CONFIG[pair_symbol]
            sess_bonus  = _session_bonus(session_now, pair_cfg)

            # ── detect market regime ──────────────────────────────────────
            regime = detect_regime(df)

            # ── news blackout: if a high-impact event is imminent, skip ──
            in_blackout, news_label = is_in_blackout(pair_symbol)
            if in_blackout:
                logger.info(f"{pair_symbol} — news blackout ({news_label}); skipping entries")
                await self.broadcast({
                    "type": "warning",
                    "data": {"type": "info",
                             "message": f"{pair_cfg['display']} — news blackout: {news_label}"},
                })
                # Still broadcast market context so the UI updates
                context = build_market_context(df, pair_symbol, [])
                context["regime"] = regime.regime
                context["regime_desc"] = regime.description
                context["news_blackout"] = news_label
                await self.broadcast({"type": "market_context", "data": context})
                continue

            # ── collect raw signals from each recommended strategy ────────
            raw_buy:  List[dict] = []   # strategies firing BUY this bar
            raw_sell: List[dict] = []   # strategies firing SELL this bar

            for name in pair_cfg["recommended_strategies"]:
                if name not in STRATEGY_REGISTRY:
                    continue

                # Regime filter — skip strategies whose playbook doesn't fit
                if not strategy_allowed(name, regime.regime):
                    logger.debug(f"{pair_symbol} {name}: filtered by regime={regime.regime}")
                    continue

                key = f"{pair_symbol}:{name}"
                try:
                    strategy = StrategyBuilder.create_strategy(name)
                    sigs     = strategy.generate_signals(df)
                    current  = int(sigs.iloc[-1]) if len(sigs) > 0 else 0
                    prev     = self._last.get(key, 0)
                    self._last[key] = current

                    if current != 0 and current != prev:
                        levels = compute_trade_levels(df, current, pair_symbol, self._balance)
                        if not levels:
                            continue
                        entry = {
                            "name":   name,
                            "key":    key,
                            "signal": current,
                            **levels,
                        }
                        if current == 1:
                            raw_buy.append(entry)
                        else:
                            raw_sell.append(entry)

                except Exception as e:
                    logger.error(f"{pair_symbol} {name} error: {e}")

            # ── merge into emittable signals ──────────────────────────────
            pair_signals: List[dict] = []

            for direction, raw_list in [("buy", raw_buy), ("sell", raw_sell)]:
                if not raw_list:
                    continue

                confluence_count = len(raw_list)

                if confluence_count >= 2:
                    # Use the signal with the best R/R as the anchor
                    anchor    = max(raw_list, key=lambda s: s["rr_ratio"])
                    strat_label = " + ".join(s["name"].replace("_", " ").title() for s in raw_list)
                    # Individual keys for win-rate lookup — use the best one's key
                    win_rate_val = self._tracker.win_rate(anchor["key"])
                    confidence   = _compute_confidence(win_rate_val, confluence_count, sess_bonus)

                    if confidence < MIN_CONFIDENCE:
                        continue

                    sig = self._build_signal(
                        pair_symbol=pair_symbol,
                        pair_cfg=pair_cfg,
                        direction=direction,
                        anchor=anchor,
                        strategy_label=strat_label,
                        strategies=[s["name"] for s in raw_list],
                        confluence=True,
                        confidence=confidence,
                    )
                    # track win rate for the lead strategy
                    self._tracker.record_signal(
                        anchor["key"], direction,
                        anchor["entry"], anchor["stop_loss"], anchor["take_profit"]
                    )
                    pair_signals.append(sig)
                    all_signals.append(sig)
                    await self.broadcast({"type": "signal", "data": sig})
                    logger.info(
                        f"CONFLUENCE {direction.upper()} {pair_cfg['display']} "
                        f"({confluence_count} strategies, conf={confidence}%)"
                    )

                else:
                    # Single strategy signal
                    anchor   = raw_list[0]
                    win_rate_val = self._tracker.win_rate(anchor["key"])
                    confidence   = _compute_confidence(win_rate_val, 1, sess_bonus)

                    if confidence < MIN_CONFIDENCE:
                        logger.debug(
                            f"Filtered {anchor['name']} {pair_symbol}: "
                            f"conf={confidence}% < {MIN_CONFIDENCE}%"
                        )
                        continue

                    sig = self._build_signal(
                        pair_symbol=pair_symbol,
                        pair_cfg=pair_cfg,
                        direction=direction,
                        anchor=anchor,
                        strategy_label=anchor["name"].replace("_", " ").title(),
                        strategies=[anchor["name"]],
                        confluence=False,
                        confidence=confidence,
                    )
                    self._tracker.record_signal(
                        anchor["key"], direction,
                        anchor["entry"], anchor["stop_loss"], anchor["take_profit"]
                    )
                    pair_signals.append(sig)
                    all_signals.append(sig)
                    await self.broadcast({"type": "signal", "data": sig})
                    logger.info(
                        f"Signal {direction.upper()} {pair_cfg['display']} "
                        f"via {anchor['name']} (conf={confidence}%)"
                    )

            # ── per-pair warnings ─────────────────────────────────────────
            warnings = check_risk_warnings(df, pair_symbol, self._balance, self._equity)
            for w in warnings:
                await self.broadcast({"type": "warning", "data": w})

            # ── market context ────────────────────────────────────────────
            context = build_market_context(df, pair_symbol, pair_signals)
            context["regime"] = regime.regime
            context["regime_desc"] = regime.description
            context["news_blackout"] = None
            await self.broadcast({"type": "market_context", "data": context})

    # ── helper ───────────────────────────────────────────────────────────────

    @staticmethod
    def _build_signal(
        pair_symbol: str,
        pair_cfg: dict,
        direction: str,
        anchor: dict,
        strategy_label: str,
        strategies: List[str],
        confluence: bool,
        confidence: int,
    ) -> dict:
        return {
            "id":           f"{pair_symbol}_{strategy_label}_{datetime.now(timezone.utc).isoformat()}",
            "pair":         pair_symbol,
            "pair_display": pair_cfg["display"],
            "strategy":     strategy_label,
            "strategies":   strategies,
            "direction":    direction,
            "timestamp":    datetime.now(timezone.utc).isoformat(),
            "confluence":   confluence,
            "confidence":   confidence,
            "entry":        anchor["entry"],
            "stop_loss":    anchor["stop_loss"],
            "take_profit":  anchor["take_profit"],
            "risk_pips":    anchor["risk_pips"],
            "reward_pips":  anchor["reward_pips"],
            "rr_ratio":     anchor["rr_ratio"],
            "suggested_lot": anchor["suggested_lot"],
            "atr_pips":     anchor.get("atr_pips"),
        }


# ── singleton ─────────────────────────────────────────────────────────────────
signal_engine: Optional[SignalEngine] = None
