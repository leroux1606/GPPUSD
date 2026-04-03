# GBP/USD Trading App — Changes & Setup

## Bug Fixes

| # | File | Bug | Fix |
|---|------|-----|-----|
| 1 | `indicators.py` | All TA-Lib functions returned numpy arrays — `.shift()` calls in every strategy crashed | Wrapped all returns in `pd.Series(..., index=df.index)` |
| 2 | `indicators.py` | `calculate_ichimoku()` — `ta.ichimoku()` returns a tuple, not a DataFrame | Extract `result[0]` |
| 3 | `engine.py` | `result.strategies[0]` — in Backtrader, `results[0]` IS the strategy. AttributeError broke every backtest | Changed to `strategy_wrapper = result` |
| 4 | `engine.py` | `_get_equity_curve()` returned `[]` — equity curves always blank | Added `self.equity_curve` tracking in `StrategyWrapper.next()` |
| 5 | `templates/__init__.py` | Was **empty** — all strategy imports failed at startup | Added all 22 strategy exports |
| 6 | `rsi_divergence.py` | `min_divergence_strength: 0.5` = 50 RSI points needed — strategy never triggered | Changed to `0.05` |
| 7 | `session_breakout.py` | Mutated input DataFrame + fired on every bar of the open hour | Added `df.copy()` + date-based deduplication |
| 8 | `momentum.py` | Sell used `OR` — any RSI > 80 sold even in strong uptrends | Changed to `AND` (momentum down AND trend fading) |
| 9 | `scalping.py` | `candle >= 1.5x ATR` selected massive spike candles, not scalp entries | Changed to `0.3–1.5x ATR` band |

---

## New Strategies

### 1. Asian Range Breakout (`asian_range_breakout.py`)

The highest-probability GBP/USD intraday setup.

**Logic:**
- Builds the Asian session range (22:00–07:00 GMT) for each day
- Trades the breakout of that range at London open (07:00–10:00 GMT)
- 3-pip buffer filters false breakouts
- ATR filter skips erratic/news days
- One trade per day maximum

**Why it works:** GBP/USD is range-bound during the thin Asian session. At London open, large institutional flows either respect or decisively break that range. Breakouts carry strong follow-through.

**Default params:**
```
asian_start_hour:   22   (GMT)
asian_end_hour:      7   (GMT)
london_end_hour:    10   (GMT — stop taking setups after this)
buffer:         0.0003   (~3 pips above/below range)
max_range_atr_mult:  2.0 (skip if Asian range > 2x ATR)
```

---

### 2. Fair Value Gap (`fair_value_gap.py`)

ICT / Smart Money Concept imbalance strategy.

**Logic:**
- Detects 3-candle "gap" patterns where price moved so fast it left an imbalance
- Bullish FVG: `candle[i-2].high < candle[i].low` (gap upward)
- Bearish FVG: `candle[i-2].low > candle[i].high` (gap downward)
- Enters when price retraces 50% back into the gap
- Trend filter (EMA 50) ensures only trading in the right direction
- Session filter: London/NY only (07:00–20:00 GMT)

**Why it works:** Institutions leave these imbalances as unfilled orders. Price commonly returns to "fill" them before continuing in the original direction, giving high R:R entries.

**Default params:**
```
min_gap_pips:        0.0003  (~3 pips minimum gap)
fvg_fill_pct:          0.5   (enter at 50% fill)
trend_ema_period:       50
session_start_hour:      7   (GMT)
session_end_hour:       20   (GMT)
```

---

### 3. VWAP Bounce (`vwap_bounce.py`)

Institutional intraday mean-reversion.

**Logic:**
- Calculates daily VWAP (resets at midnight each day)
- Buys when price crosses back above VWAP from below, RSI confirms oversold
- Sells when price crosses back below VWAP from above, RSI confirms overbought
- Only trades during the London/NY overlap (13:00–17:00 GMT) — highest volume, cleanest reactions

**Why it works:** VWAP is the most-watched intraday benchmark for institutional algos. It acts as a self-fulfilling support/resistance. The London/NY overlap has the highest GBP/USD volume and produces the most reliable VWAP reactions.

**Default params:**
```
rsi_period:          14
rsi_oversold:        40   (slightly less strict than 30 for intraday)
rsi_overbought:      60
session_start_hour:  13   (GMT — London/NY overlap)
session_end_hour:    17   (GMT)
min_deviation_pips:  0.0003
```

---

## Real-time System

### Signal Engine

Runs in the background and scans active strategies every 30 seconds (configurable). When a new signal is detected:

1. Computes **entry, stop loss, and take profit** prices using ATR-based levels:
   - SL = 1.5× ATR from entry
   - TP = 2.2× ATR from entry (R/R ≥ 1:1.47)
2. Calculates **suggested lot size** based on 1% account risk (configurable)
3. Broadcasts the signal via WebSocket to the UI
4. Sends a **Telegram notification** to your phone

**Risk warnings** are also auto-generated for:
- RSI extremes (> 78 or < 22)
- Equity drawdown > 2% on the day (stop prompt at 5%)
- News-window times (07:00, 09:00, 13:00, 14:00, 15:00 GMT)
- Low-liquidity Asian session (21:00–06:00 GMT)

---

## UI Overview

Single-page trading terminal with tabs:

| Tab | Contents |
|-----|----------|
| **Terminal** | Chart + Live Signals panel + AI Advisor + Economic Calendar |
| **Trade** | Chart + Order entry + Positions + History |
| **Backtest** | Strategy backtest, equity curve, drawdown, trade list |
| **Strategies** | Strategy list + editor + parameters |
| **Analytics** | Performance dashboard, monthly returns, trade distribution |
| **Settings** | Telegram, OpenRouter, active strategies, risk settings |

**Live signal cards show:**
- Direction (BUY / SELL) + strategy name
- Entry price
- Stop loss price + pips at risk
- Take profit price + pips reward
- R/R ratio
- Suggested lot size
- AI analysis note (if OpenRouter configured)

**Notification bell** in the top bar shows unread count. Toast notifications appear top-right for:
- `info` (blue) — low-priority info
- `opportunity` (green) — new trade signal
- `warning` (amber) — risk alert
- `danger` (red) — urgent, never auto-dismissed

---

## Setup

### 1. Create `.env` file in the backend folder

```env
# Data providers
OANDA_API_KEY=your_oanda_key
OANDA_ACCOUNT_ID=your_account_id
ALPHA_VANTAGE_API_KEY=your_av_key

# AI Advisor (OpenRouter — free at openrouter.ai)
OPENROUTER_API_KEY=sk-or-your_key_here
OPENROUTER_MODEL=anthropic/claude-3-haiku

# Telegram notifications
TELEGRAM_BOT_TOKEN=1234567890:ABCdef...
TELEGRAM_CHAT_ID=123456789

# Signal engine
SIGNAL_SCAN_INTERVAL=30
ACTIVE_STRATEGIES=asian_range_breakout,session_breakout,triple_screen
DEFAULT_RISK_PER_TRADE_PCT=1.0
```

### 2. Set up Telegram bot

1. Open Telegram → search `@BotFather` → send `/newbot`
2. Follow the prompts, copy the **bot token**
3. Start a conversation with your new bot (send it any message)
4. To get your **Chat ID**: open Telegram → search `@userinfobot` → it replies with your ID
5. Add both to `.env` as shown above
6. In the app go to **Settings → Send Test Message** to verify

### 3. Get OpenRouter API key

1. Go to [openrouter.ai](https://openrouter.ai) and create a free account
2. Generate an API key
3. Add it to `.env` as `OPENROUTER_API_KEY=sk-or-...`
4. Recommended model: `anthropic/claude-3-haiku` (fast and cheap)

### 4. Run the app

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` (or 3000).

---

---

## Multi-Pair Support

Six pairs are now supported. Each has its own configuration, session focus, and recommended strategies.

| Pair | Best Sessions | Characteristics | Recommended Strategies |
|------|--------------|-----------------|----------------------|
| **GBP/USD** | London, Overlap | High volatility, UK data sensitive | Asian Range Breakout, Session Breakout, Triple Screen, FVG, VWAP Bounce |
| **EUR/USD** | London, Overlap | Most liquid, smooth trends | EUR/USD Breakout, MACD Signal, Bollinger Breakout, VWAP Bounce |
| **USD/JPY** | Asian, NY | Risk-on/risk-off, BoJ sensitive | Tokyo Range Breakout, Session Breakout, MACD Signal, Momentum |
| **USD/CHF** | London, Overlap | Safe-haven, inverse EUR/USD | Mean Reversion, Bollinger Breakout, Support/Resistance |
| **AUD/USD** | Asian, Sydney | Gold/iron ore correlated | Commodity Momentum, Asian Range Breakout, Breakout |
| **USD/CAD** | NY | Oil correlated, North American hours | NY Breakout, Commodity Momentum, Breakout |

### Pip Handling
- **Standard pairs** (EUR/USD, GBP/USD, USD/CHF, AUD/USD, USD/CAD): 1 pip = 0.0001
- **JPY pairs** (USD/JPY): 1 pip = 0.01 — all SL/TP/ATR calculations adjusted automatically

### Pair Selector
The topbar now has a compact pair selector. Clicking a pair:
- Changes the chart data
- Filters the AI Advisor context to that pair
- The Signal Panel has its own "All / per-pair" filter tabs

---

## New Pair-Specific Strategies (4 added)

### EUR/USD Frankfurt-London Breakout (`eur_usd_breakout.py`)
Builds the overnight pre-Frankfurt range (01:00–07:00 GMT). Trades the breakout at the London open (07:00–10:00 GMT). EUR/USD has a tighter pre-London range than GBP/USD, making it cleaner to trade.

### Tokyo Range Breakout (`tokyo_range_breakout.py`)
For USD/JPY. Builds the Tokyo session range (00:00–06:00 GMT). Trades the breakout at London open AND/OR NY open. USD/JPY accumulates institutional positioning in Tokyo; Western banks often break the range with conviction at London open.

### Commodity Momentum (`commodity_momentum.py`)
For AUD/USD and USD/CAD. Uses ROC + ADX + EMA alignment to detect clean commodity-driven trends. AUD/USD uses Asian session filter; USD/CAD uses NY session filter. Configure `prime_session` param to match the pair.

### NY Open Breakout (`ny_breakout.py`)
For USD/CAD primarily. Builds the London-morning range (07:00–13:00 GMT) and trades the breakout at NY open (13:00–15:00 GMT). USD/CAD volume spikes sharply at 13:30 GMT with US data releases.

---

## Available Strategies (26 total)

| Strategy | Type | Best For |
|----------|------|----------|
| `asian_range_breakout` | Breakout | GBP/USD London open |
| `fair_value_gap` | ICT/SMC | All sessions |
| `vwap_bounce` | Mean reversion | London/NY overlap |
| `session_breakout` | Breakout | London/NY opens |
| `triple_screen` | Multi-filter | Trend trading |
| `mean_reversion` | Mean reversion | Ranging markets |
| `bollinger_breakout` | Breakout | Volatility expansion |
| `macd_signal` | Momentum | Trend following |
| `rsi_divergence` | Reversal | Swing entries |
| `ichimoku` | Trend | Multi-confirmation |
| `ma_crossover` | Trend | Simple trend filter |
| `breakout` | Breakout | Range breakouts |
| `support_resistance` | Reversal | Key levels |
| `scalping` | Momentum | Short-term |
| `momentum` | Momentum | Strong trends |
| `stochastic` | Oscillator | Ranging markets |
| `turtle` | Trend | Long-term breakout |
| `fibonacci` | Retracement | Pullback entries |
| `range_trading` | Range | Sideways markets |
| `pivot_points` | Support/Resistance | Daily levels |
| `grid_trading` | Grid | Range-bound |
| `martingale` | ⚠️ HIGH RISK | Avoid |
