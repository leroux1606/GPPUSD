# GBP/USD Day Trading Application

Professional day trading system for GBP/USD with live data, backtesting, technical analysis, and automated strategy creation.

## Features

### Core Capabilities
- ✅ Real-time GBP/USD price streaming
- ✅ 40+ technical indicators
- ✅ 20+ pre-built trading strategies
- ✅ Visual + code-based strategy builder
- ✅ High-accuracy backtesting engine
- ✅ Multiple stop-loss types
- ✅ Advanced position sizing
- ✅ Risk management system
- ✅ 30+ performance metrics
- ✅ TradingView-style charts
- ✅ Multi-timeframe analysis
- ✅ Walk-forward optimization
- ✅ Monte Carlo simulation

### Technical Indicators

**Trend:** SMA, EMA, WMA, VWMA, MACD, ADX, Ichimoku, Parabolic SAR, Supertrend

**Momentum:** RSI, Stochastic, CCI, Williams %R, ROC, Momentum

**Volatility:** Bollinger Bands, ATR, Keltner, Donchian

**Volume:** OBV, VWAP, MFI, A/D

**S/R:** Pivot Points, Fibonacci

### Pre-Built Strategies

1. Moving Average Crossover
2. RSI Divergence
3. Bollinger Band Breakout
4. MACD Signal
5. Stochastic Oscillator
6. Ichimoku Cloud
7. Price Action Scalping
8. Support/Resistance Bounce
9. Fibonacci Retracement
10. Range Trading
11. Breakout Strategy
12. Mean Reversion
13. Momentum Strategy
14. Grid Trading
15. Martingale
16. Pivot Point Strategy
17. Triple Screen
18. Turtle Trading
19. Session Breakout
20. Custom Strategies

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for local development)
- OANDA API account (for live data)

### Installation

1. Clone repository:
```bash
git clone <repo-url>
cd gbpusd-trading-app
```

2. Set up environment variables:
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

3. Start with Docker:
```bash
docker-compose up -d
```

4. Access application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup (Without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Usage Guide

### 1. Download Historical Data
Navigate to Dashboard → Data → Download Historical Data
- Select timeframe (1m, 5m, 15m, 1h, 4h, 1D)
- Choose date range (last 5-10 years recommended)
- Click "Download"

### 2. Create a Strategy

**Option A: Use Pre-Built Strategy**
- Go to Strategies → Templates
- Select a strategy (e.g., "Moving Average Crossover")
- Customize parameters
- Save strategy

**Option B: Visual Builder**
- Go to Strategies → Builder
- Drag indicators from left panel
- Connect nodes to create logic
- Configure entry/exit conditions
- Save strategy

**Option C: Code Editor**
- Go to Strategies → Custom
- Write Python strategy code
- Use BaseStrategy template
- Test and save

### 3. Backtest Strategy
- Go to Backtesting
- Select strategy
- Choose timeframe and date range
- Set initial capital and commission
- Configure risk management (stop loss, take profit, position sizing)
- Click "Run Backtest"
- View results (metrics, equity curve, trades)

### 4. Optimize Strategy
- Go to Backtesting → Optimize
- Select strategy and parameters to optimize
- Choose optimization method (Grid Search, Genetic Algorithm)
- Set parameter ranges
- Click "Optimize"
- View best parameter combinations

### 5. Live Trading (Paper Trading)
- Go to Trading
- Select strategy
- Enable "Paper Trading" mode
- Start automated execution
- Monitor positions and P&L

## API Documentation

### Data Endpoints
```
GET  /api/data/live             - Get current price
GET  /api/data/historical       - Get historical OHLCV
POST /api/data/download         - Download historical data
```

### Strategy Endpoints
```
GET    /api/strategies          - List strategies
POST   /api/strategies          - Create strategy
GET    /api/strategies/{id}     - Get strategy details
POST   /api/strategies/{id}/signals - Generate signals
```

### Backtesting Endpoints
```
POST /api/backtest/run          - Run backtest
POST /api/backtest/optimize     - Optimize parameters
POST /api/backtest/walk-forward - Walk-forward analysis
POST /api/backtest/monte-carlo  - Monte Carlo simulation
```

### Analytics Endpoints
```
GET /api/analytics/performance     - Performance metrics
GET /api/analytics/equity-curve    - Equity curve data
GET /api/analytics/drawdown        - Drawdown data
GET /api/analytics/monthly-returns - Monthly returns
```

### WebSocket
```
WS /ws - Real-time price updates
```

## Architecture

```
┌─────────────────┐
│   Frontend      │
│  (React + TS)   │
└────────┬────────┘
         │ HTTP/WebSocket
         │
┌────────▼────────┐
│   Backend       │
│  (FastAPI)      │
└────────┬────────┘
         │
    ┌────┼────┐
    │    │    │
┌───▼──┐ │ ┌──▼─────┐
│ DB   │ │ │ Redis  │
│(PG)  │ │ │(Cache) │
└──────┘ │ └────────┘
         │
    ┌────▼────┐
    │ OANDA   │
    │  API    │
    └─────────┘
```

## Performance Metrics

### Profitability
- Total Return (%)
- Annual Return (%)
- Monthly Returns
- Profit Factor
- Expectancy

### Risk
- Maximum Drawdown (%)
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio
- Recovery Factor

### Trade Statistics
- Total Trades
- Win Rate (%)
- Avg Win / Avg Loss
- Longest Win/Loss Streak
- Average Trade Duration

## Configuration

### Timeframes
- 1m (1 minute) - Scalping
- 5m (5 minutes) - Short-term
- 15m (15 minutes) - Intraday
- 1h (1 hour) - Swing
- 4h (4 hours) - Position
- 1D (Daily) - Long-term

### Position Sizing Methods
- Fixed Lot Size
- Percentage of Equity
- Kelly Criterion
- Optimal F
- Volatility-Based (ATR)
- Risk Per Trade

### Stop Loss Types
- Fixed Pips
- Percentage
- ATR-Based
- Trailing Stop
- Time-Based Exit
- Break-Even Stop
- Chandelier Exit

## Testing

Run backend tests:
```bash
cd backend
pytest tests/
```

Run frontend tests:
```bash
cd frontend
npm test
```

## Troubleshooting

### Issue: WebSocket not connecting
- Check backend is running on port 8000
- Verify WebSocket URL in frontend/.env
- Check browser console for errors

### Issue: Historical data download fails
- Verify API keys in backend/.env
- Check internet connection
- Try alternative data provider

### Issue: Backtest takes too long
- Reduce date range
- Use higher timeframe (e.g., 1h instead of 1m)
- Optimize strategy complexity

### Issue: Indicators not displaying
- Ensure historical data is loaded
- Check indicator parameters
- Verify chart component mounted

## License

MIT

## Support

For issues and questions, please open a GitHub issue.

