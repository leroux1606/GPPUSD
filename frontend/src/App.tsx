import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ErrorBoundary } from './components/Common/ErrorBoundary';
import { Navbar } from './components/Common/Navbar';
import { Sidebar } from './components/Common/Sidebar';
import { PriceTicker } from './components/Dashboard/PriceTicker';
import { AccountSummary } from './components/Dashboard/AccountSummary';
import { OpenPositions } from './components/Dashboard/OpenPositions';
import { MultiChart } from './components/Charts/MultiChart';
import { IndicatorPanel } from './components/Charts/IndicatorPanel';
import { BacktestPanel } from './components/Backtesting/BacktestPanel';
import { PerformanceMetricsDisplay } from './components/Backtesting/PerformanceMetrics';
import { EquityCurve } from './components/Backtesting/EquityCurve';
import { TradeList } from './components/Backtesting/TradeList';
import { OrderEntry } from './components/Trading/OrderEntry';
import { PositionManager } from './components/Trading/PositionManager';
import { TradeHistory } from './components/Trading/TradeHistory';
import { QuickTrade } from './components/Trading/QuickTrade';
import { RiskCalculator } from './components/Trading/RiskCalculator';
import { StrategyList } from './components/Strategy/StrategyList';
import { StrategyEditor } from './components/Strategy/StrategyEditor';
import { StrategyBuilder } from './components/Strategy/StrategyBuilder';
import { StrategyComparison } from './components/Strategy/StrategyComparison';
import { StrategyExplanation } from './components/Strategy/StrategyExplanation';
import { ParameterOptimizer } from './components/Strategy/ParameterOptimizer';
import { AnalyticsDashboard } from './components/Analytics/AnalyticsDashboard';
import { MonthlyReturns } from './components/Analytics/MonthlyReturns';
import { TradeDistribution } from './components/Analytics/TradeDistribution';
import { DrawdownChart } from './components/Backtesting/DrawdownChart';
import { IndicatorHelp } from './components/Charts/IndicatorHelp';
import { EconomicCalendar } from './components/Dashboard/EconomicCalendar';
import { useStrategyStore } from './store';
import './App.css';

function Dashboard() {
  return (
    <div className="dashboard">
      <header>
        <h1>GBP/USD Trading Dashboard</h1>
        <PriceTicker />
      </header>
      <main>
        <div className="dashboard-grid">
          <div className="dashboard-left">
            <AccountSummary />
            <OpenPositions />
          </div>
          <div className="dashboard-right">
            <EconomicCalendar />
          </div>
        </div>
      </main>
    </div>
  );
}

function Charts() {
  return (
    <div className="charts-page">
      <h2>Price Charts & Indicators</h2>
      <div className="charts-layout">
        <div className="main-chart">
          <MultiChart />
        </div>
        <div className="indicator-sidebar">
          <IndicatorPanel />
          <IndicatorHelp />
        </div>
      </div>
    </div>
  );
}

function Backtesting() {
  const [backtestResults, setBacktestResults] = React.useState<any>(null);

  return (
    <div className="backtesting-page">
      <h2>Backtesting</h2>
      <BacktestPanel onResultsChange={setBacktestResults} />
      {backtestResults && (
        <>
          <PerformanceMetricsDisplay metrics={backtestResults} />
          <div className="backtest-charts">
            <EquityCurve equityCurve={backtestResults.equity_curve || []} />
            <DrawdownChart equityCurve={backtestResults.equity_curve || []} />
          </div>
          <TradeList trades={backtestResults.trades || []} />
        </>
      )}
    </div>
  );
}

function Trading() {
  return (
    <div className="trading-page">
      <h2>Trading</h2>
      <div className="trading-layout">
        <div className="trading-left">
          <QuickTrade />
          <OrderEntry />
          <RiskCalculator />
        </div>
        <div className="trading-right">
          <OpenPositions />
          <PositionManager />
          <TradeHistory />
        </div>
      </div>
    </div>
  );
}

function Strategies() {
  const { selectedStrategy, strategies } = useStrategyStore();
  const [view, setView] = useState<'list' | 'builder' | 'comparison' | 'optimizer'>('list');

  return (
    <div className="strategies-page">
      <h2>Strategies</h2>
      <div className="strategy-tabs">
        <button className={view === 'list' ? 'active' : ''} onClick={() => setView('list')}>
          Strategy List
        </button>
        <button className={view === 'builder' ? 'active' : ''} onClick={() => setView('builder')}>
          Visual Builder
        </button>
        <button className={view === 'comparison' ? 'active' : ''} onClick={() => setView('comparison')}>
          Compare Strategies
        </button>
        <button className={view === 'optimizer' ? 'active' : ''} onClick={() => setView('optimizer')}>
          Optimize Parameters
        </button>
      </div>
      
      {view === 'list' && (
        <div className="strategies-layout">
          <div className="strategies-left">
            <StrategyList />
          </div>
          <div className="strategies-right">
            {selectedStrategy ? (
              <>
                <StrategyEditor />
                <StrategyExplanation strategyType={selectedStrategy.type} />
              </>
            ) : (
              <div>Select a strategy to view details</div>
            )}
          </div>
        </div>
      )}
      
      {view === 'builder' && <StrategyBuilder />}
      {view === 'comparison' && <StrategyComparison strategies={strategies} />}
      {view === 'optimizer' && <ParameterOptimizer strategy={selectedStrategy} />}
    </div>
  );
}

function Analytics() {
  return (
    <div className="analytics-page">
      <AnalyticsDashboard />
      <div className="analytics-charts">
        <MonthlyReturns trades={[]} />
        <TradeDistribution trades={[]} />
      </div>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <div className="app-container">
          <Navbar />
          <div className="main-layout">
            <Sidebar />
            <main className="content">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/charts" element={<Charts />} />
                <Route path="/backtesting" element={<Backtesting />} />
                <Route path="/trading" element={<Trading />} />
                <Route path="/strategies" element={<Strategies />} />
                <Route path="/analytics" element={<Analytics />} />
              </Routes>
            </main>
          </div>
        </div>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
