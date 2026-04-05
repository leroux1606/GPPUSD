# Status — All Issues Resolved (2026-04-05)

## What's Working
- **Chart**: Loads candlestick data from Yahoo Finance, renders correctly
- **Indicators**: SMA, EMA, RSI, MACD etc. calculate and display on chart
- **AI Advisor**: OpenRouter connected with `liquid/lfm-2.5-1.2b-instruct:free`
- **Signal Engine**: Scans every 30 seconds across 6 pairs
- **Telegram**: Connected — test message confirmed received, live signals send automatically when engine fires
- **WebSocket**: Live connection working (green "Live" badge bottom-right)

## Fixes Applied This Session
| Issue | Fix |
|-------|-----|
| Chart not rendering | `TradingChart` returned `<LoadingSpinner>` during fetch, unmounting the chart container. Moved loading overlay inside container so chart DOM persists. |
| React StrictMode double-invoke | Removed `<React.StrictMode>` from `main.tsx` — lightweight-charts can't survive effect cleanup+recreate on same container |
| WebSocket 403 | `main.py` registered `/ws` with `add_api_route` (HTTP only). Changed to `add_api_websocket_route`. |
| WebSocket wrong port | `useWebSocket.ts` hardcoded `ws://localhost:8000`. Changed to `8002`. |
| Indicators returning 500 | `indicators.py` returned NaN floats which FastAPI can't serialize to JSON. Added `clean()` helper to replace NaN/Inf with `None`. |

## Quick Start
```bash
# Backend
cd backend
uvicorn app.main:app --reload --port 8002

# Frontend (separate terminal)
cd frontend
npm run dev
```
Open http://localhost:3000
