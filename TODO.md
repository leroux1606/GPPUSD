# Remaining Issues — Pick Up Here

## What's Working
- **Chart**: Loads candlestick data from Yahoo Finance (replaced OANDA, unavailable in SA)
- **AI Advisor**: OpenRouter connected with `liquid/lfm-2.5-1.2b-instruct:free` — confirmed via `POST /api/signals/test-ai` returning 200 OK
- **Signal Engine**: Scans every 30 seconds across 6 pairs
- **Telegram direct API**: Confirmed working — test message received via `curl` to `api.telegram.org`

## What's NOT Working

### 1. Telegram "Send Test Message" button returns error
- **Symptom**: UI shows "Failed — check token and chat ID" (HTTP 502)
- **Root cause**: The test endpoint in `backend/app/api/routes/signals.py:117` calls `send_telegram()` with a priority that may still be filtered by `TELEGRAM_MIN_PRIORITY`. We changed `priority="info"` to `priority="warning"` but the server may not have reloaded, or there's a caching/ghost-process issue.
- **Steps to debug**:
  1. Kill ALL Python/uvicorn processes: `taskkill /F /IM python.exe`
  2. Delete `__pycache__`: `python -c "import shutil,pathlib; [shutil.rmtree(p) for p in pathlib.Path('backend').rglob('__pycache__')]"`
  3. Restart: `cd backend && uvicorn app.main:app --reload --port 8002`
  4. Test from UI Settings tab
  5. If still failing, try changing `TELEGRAM_MIN_PRIORITY=info` in `.env` to bypass filtering entirely

### 2. AI "Test Connection" button may fail from UI
- **Symptom**: "Request failed — check API key and model name"
- **Note**: The API itself works (confirmed via curl). The issue may be that the running server still has the old (delisted) model cached in memory.
- **Steps to debug**:
  1. After full restart (step above), push the model via API:
     ```bash
     curl -X POST http://localhost:8002/api/signals/settings \
       -H "Content-Type: application/json" \
       -d '{"ai_model": "liquid/lfm-2.5-1.2b-instruct:free"}'
     ```
  2. Then test: `curl http://localhost:8002/api/signals/test-ai`

### 3. WebSocket "Offline" indicator (bottom-right)
- **Symptom**: Frontend shows "offline" badge
- **Root cause**: Frontend uses Socket.IO client but backend uses raw WebSocket — protocol mismatch
- **Priority**: Low — doesn't block functionality, chart loads via REST polling

## Key Changes Made This Session
| File | Change |
|------|--------|
| `backend/app/data/data_manager.py` | Added `get_historical_async()` with Yahoo Finance direct HTTP + caching |
| `backend/app/data/providers/yahoo_finance.py` | Rewrote from yfinance lib to direct HTTP (bypasses blocked headers) |
| `backend/app/api/routes/data.py` | Updated `/live` and `/historical` endpoints for Yahoo Finance |
| `backend/app/api/routes/signals.py` | Changed test telegram priority from "info" to "warning" |
| `backend/app/config.py` | Added `localhost:3001` to CORS origins |
| `backend/requirements.txt` | Removed pandas-ta, relaxed TA-Lib, fixed vectorbt/yfinance versions |
| `frontend/src/services/api.ts` | Backend URL → port 8002 |
| `frontend/src/services/websocket.ts` | WebSocket URL → port 8002 |
| `frontend/src/components/Charts/TradingChart.tsx` | Added 50ms delay to fix chart race condition |

## Quick Start
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002

# Frontend (separate terminal)
cd frontend
npm run dev
```
Open http://localhost:3001 — chart should load within a few seconds.
