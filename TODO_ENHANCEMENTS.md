# Enhancement Backlog

## High Priority

- **Multi-pair live prices** — price bar currently only fetches GBP/USD regardless of selected pair; hook up Yahoo Finance ticker per pair
- **Indicator persistence** — active indicators reset on page refresh; save to localStorage so they survive a reload
- **Signal notifications to Telegram** — real signals are generated but only test messages reach Telegram; wire up the signal engine to send actual trade signals
- **AI Advisor auto-mode** — the Auto toggle exists but does nothing; trigger analysis automatically on new signals or every N minutes

## Medium Priority

- **Backtesting pair support** — backtest panel is hardcoded to GBP/USD; should respect selected pair
- **Chart date range picker** — let user pick custom start/end date instead of always loading last 300 bars
- **Strategy parameter validation** — no feedback when invalid params are entered in StrategyEditor; add inline validation
- **Mobile/responsive layout** — terminal layout breaks below ~1024px wide; add a responsive fallback

## Lower Priority

- **Dark/light theme toggle** — currently dark-only
- **Export signals to CSV** — let user download signal history
- **Indicator presets** — save/load named sets of indicators (e.g. "Trend Setup", "Scalp Setup")
- **Performance** — historical data is re-fetched on every pair/timeframe switch even when already cached; fix cache keying

## Known Bugs to Revisit

- H4 timeframe maps to same Yahoo Finance interval as H1 (no native 4h support in YF); consider aggregating H1 candles into H4 on the backend
- Volume data is always 0 for forex pairs from Yahoo Finance (forex has no real volume); consider replacing with tick volume estimate or hiding volume bar for FX pairs
