import React, { useState, useEffect } from 'react';
import { ErrorBoundary } from './components/Common/ErrorBoundary';
import { TradingChart } from './components/Charts/TradingChart';
import { IndicatorPanel } from './components/Charts/IndicatorPanel';
import { MultiChart } from './components/Charts/MultiChart';
import { SignalPanel } from './components/LiveSignals/SignalPanel';
import { AIAdvisor } from './components/AIAdvisor/AIAdvisor';
import { NotificationOverlay, NotificationBell } from './components/Notifications/NotificationOverlay';
import { NotificationSettings } from './components/Settings/NotificationSettings';
import { BacktestPanel } from './components/Backtesting/BacktestPanel';
import { PerformanceMetricsDisplay } from './components/Backtesting/PerformanceMetrics';
import { EquityCurve } from './components/Backtesting/EquityCurve';
import { DrawdownChart } from './components/Backtesting/DrawdownChart';
import { TradeList } from './components/Backtesting/TradeList';
import { OrderEntry } from './components/Trading/OrderEntry';
import { OpenPositions } from './components/Dashboard/OpenPositions';
import { QuickTrade } from './components/Trading/QuickTrade';
import { RiskCalculator } from './components/Trading/RiskCalculator';
import { PositionManager } from './components/Trading/PositionManager';
import { TradeHistory } from './components/Trading/TradeHistory';
import { StrategyList } from './components/Strategy/StrategyList';
import { StrategyEditor } from './components/Strategy/StrategyEditor';
import { AnalyticsDashboard } from './components/Analytics/AnalyticsDashboard';
import { MonthlyReturns } from './components/Analytics/MonthlyReturns';
import { TradeDistribution } from './components/Analytics/TradeDistribution';
import { EconomicCalendar } from './components/Dashboard/EconomicCalendar';
import { useDataStore } from './store/dataStore';
import { useTradingStore } from './store/tradingStore';
import { useNotificationStore } from './store/notificationStore';
import { useWebSocket } from './hooks/useWebSocket';
import { useUIStore, ALL_PAIRS } from './store/uiStore';
import { BacktestResult } from './types';
import './App.css';

type Tab = 'terminal' | 'trade' | 'backtest' | 'strategies' | 'analytics' | 'settings';

// ── Pair selector ─────────────────────────────────────────────────────────────
function PairSelector() {
  const { selectedPair, setPair } = useUIStore();
  return (
    <div className="pair-selector">
      {ALL_PAIRS.map((p) => (
        <button
          key={p.symbol}
          className={`pair-btn ${selectedPair === p.symbol ? 'active' : ''}`}
          onClick={() => setPair(p.symbol)}
        >
          {p.display}
        </button>
      ))}
    </div>
  );
}

// ── Live price bar ─────────────────────────────────────────────────────────────
function PriceBar() {
  const { livePrice } = useDataStore();
  const { marketContext } = useNotificationStore();
  const { selectedPair } = useUIStore();
  const pairDisplay = ALL_PAIRS.find((p) => p.symbol === selectedPair)?.display ?? selectedPair;

  return (
    <div className="price-bar">
      <div className="price-symbol">{pairDisplay}</div>
      {livePrice ? (
        <>
          <div className="price-bid">
            <span className="price-label">Bid</span>
            <span className="price-value">{livePrice.bid?.toFixed(5)}</span>
          </div>
          <div className="price-ask">
            <span className="price-label">Ask</span>
            <span className="price-value">{livePrice.ask?.toFixed(5)}</span>
          </div>
          <div className="price-spread">
            <span className="price-label">Spread</span>
            <span className="price-value">{((livePrice.spread || 0) * 10000).toFixed(1)}p</span>
          </div>
        </>
      ) : (
        <span className="price-connecting">Connecting...</span>
      )}
      {marketContext && (
        <div className="session-badge">{marketContext.session}</div>
      )}
    </div>
  );
}

// ── Status bar ─────────────────────────────────────────────────────────────────
function StatusBar() {
  const { balance, equity, getTotalPnL } = useTradingStore();
  const pnl = getTotalPnL();
  const { connected } = useWebSocket();

  return (
    <div className="status-bar">
      <div className="status-item">
        <span className="status-label">Balance</span>
        <span className="status-value">${balance.toLocaleString('en', { minimumFractionDigits: 2 })}</span>
      </div>
      <div className="status-item">
        <span className="status-label">Equity</span>
        <span className="status-value">${equity.toLocaleString('en', { minimumFractionDigits: 2 })}</span>
      </div>
      <div className="status-item">
        <span className="status-label">P&L Today</span>
        <span className={`status-value ${pnl >= 0 ? 'text-green' : 'text-red'}`}>
          {pnl >= 0 ? '+' : ''}{pnl.toFixed(2)}
        </span>
      </div>
      <div className="status-ws">
        <span className={`ws-dot ${connected ? 'ws-connected' : 'ws-disconnected'}`} />
        {connected ? 'Live' : 'Offline'}
      </div>
    </div>
  );
}

// ── Terminal tab (main trading view) ──────────────────────────────────────────
function TerminalTab() {
  const { selectedTimeframe, setTimeframe } = useUIStore();
  const TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1'];

  return (
    <div className="terminal-layout">
      <div className="terminal-chart-area">
        <div className="chart-toolbar">
          <div className="tf-buttons">
            {TIMEFRAMES.map((tf) => (
              <button
                key={tf}
                className={`tf-btn ${selectedTimeframe === tf ? 'active' : ''}`}
                onClick={() => setTimeframe(tf)}
              >
                {tf}
              </button>
            ))}
          </div>
          <IndicatorPanel compact />
        </div>
        <TradingChart height={480} />
      </div>
      <div className="terminal-right-panel">
        <SignalPanel />
        <AIAdvisor />
        <div className="panel eco-mini">
          <div className="panel-header"><span className="panel-title">Economic Calendar</span></div>
          <EconomicCalendar compact />
        </div>
      </div>
    </div>
  );
}

// ── Trade tab ──────────────────────────────────────────────────────────────────
function TradeTab() {
  return (
    <div className="trade-layout">
      <div className="trade-chart">
        <TradingChart height={400} />
      </div>
      <div className="trade-panel">
        <QuickTrade />
        <OrderEntry />
        <RiskCalculator />
      </div>
      <div className="trade-positions">
        <OpenPositions />
        <PositionManager />
        <TradeHistory />
      </div>
    </div>
  );
}

// ── Backtest tab ───────────────────────────────────────────────────────────────
function BacktestTab() {
  const [results, setResults] = useState<BacktestResult | null>(null);
  return (
    <div className="backtest-layout">
      <BacktestPanel onResultsChange={setResults} />
      {results && (
        <div className="backtest-results">
          <PerformanceMetricsDisplay metrics={results} />
          <div className="backtest-charts-row">
            <EquityCurve equityCurve={results.equity_curve || []} timestamps={results.timestamps} />
            <DrawdownChart equityCurve={results.equity_curve || []} timestamps={results.timestamps} />
          </div>
          <TradeList trades={results.trades || []} />
        </div>
      )}
    </div>
  );
}

// ── Strategies tab ─────────────────────────────────────────────────────────────
function StrategiesTab() {
  return (
    <div className="strategies-layout">
      <div className="strategies-left">
        <StrategyList />
      </div>
      <div className="strategies-right">
        <StrategyEditor />
      </div>
    </div>
  );
}

// ── Analytics tab ──────────────────────────────────────────────────────────────
function AnalyticsTab() {
  const { closedTrades, positions } = useTradingStore();
  const allTrades = [...closedTrades, ...positions.filter((p) => p.status === 'closed')];
  return (
    <div className="analytics-layout">
      <AnalyticsDashboard trades={allTrades} />
      <div className="analytics-row">
        <MonthlyReturns trades={allTrades} />
        <TradeDistribution trades={allTrades} />
      </div>
    </div>
  );
}

// ── Root App ───────────────────────────────────────────────────────────────────
function App() {
  const [tab, setTab] = useState<Tab>('terminal');
  useWebSocket(); // Init WebSocket at root level

  const TABS: { id: Tab; label: string }[] = [
    { id: 'terminal', label: 'Terminal' },
    { id: 'trade', label: 'Trade' },
    { id: 'backtest', label: 'Backtest' },
    { id: 'strategies', label: 'Strategies' },
    { id: 'analytics', label: 'Analytics' },
    { id: 'settings', label: 'Settings' },
  ];

  return (
    <ErrorBoundary>
      <div className="app-root">
        {/* Top navigation bar */}
        <header className="topbar">
          <div className="topbar-left">
            <span className="app-logo">FX</span>
            <PairSelector />
            <nav className="tab-nav">
              {TABS.map((t) => (
                <button
                  key={t.id}
                  className={`tab-btn ${tab === t.id ? 'active' : ''}`}
                  onClick={() => setTab(t.id)}
                >
                  {t.label}
                </button>
              ))}
            </nav>
          </div>
          <div className="topbar-right">
            <PriceBar />
            <NotificationBell />
          </div>
        </header>

        {/* Main content */}
        <main className="app-main">
          {tab === 'terminal' && <TerminalTab />}
          {tab === 'trade' && <TradeTab />}
          {tab === 'backtest' && <BacktestTab />}
          {tab === 'strategies' && <StrategiesTab />}
          {tab === 'analytics' && <AnalyticsTab />}
          {tab === 'settings' && <NotificationSettings />}
        </main>

        {/* Status bar */}
        <StatusBar />

        {/* Floating notifications */}
        <NotificationOverlay />
      </div>
    </ErrorBoundary>
  );
}

export default App;
