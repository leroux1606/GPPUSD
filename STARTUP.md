# Starting the App

## 1. Start the backend
```bash
cd C:\Private\AI\GPPUSD\backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## 2. Start the frontend (separate terminal)
```bash
cd C:\Private\AI\GPPUSD\frontend
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## First things to check

1. **Settings tab** → enter your Telegram Chat ID → click **Send Test Message** → your phone should buzz
2. **Settings tab** → click **Test AI Connection** → confirms your AI provider is working
3. **Terminal tab** → signals appear here in real-time as the engine scans (every 30 seconds)

---

## Switching AI provider

Edit `backend/.env` and change one line:
```env
AI_PROVIDER=openrouter    # or: anthropic / openai
```
Or change it live in the **Settings tab** without restarting.

---

## Useful reminders

| Thing | Where |
|-------|-------|
| Telegram token + chat ID | `backend/.env` |
| AI provider + model | Settings tab or `backend/.env` |
| Scan interval, risk % | Settings tab |
| All 26 strategies | Strategies tab |
| Backtest a strategy | Backtest tab |
