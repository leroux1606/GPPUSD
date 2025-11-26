/**
 * Calculate pip value for GBP/USD
 * Standard pip = 0.0001
 */
export const PIP_VALUE = 0.0001;

/**
 * Calculate pips between two prices
 */
export function calculatePips(price1: number, price2: number): number {
  return Math.abs(price1 - price2) / PIP_VALUE;
}

/**
 * Calculate P&L for a trade
 */
export function calculatePnL(
  entryPrice: number,
  exitPrice: number,
  size: number,
  side: 'buy' | 'sell'
): number {
  const pipValue = 10; // $10 per pip for 1 standard lot GBP/USD
  const priceDiff = exitPrice - entryPrice;
  const multiplier = side === 'buy' ? 1 : -1;
  const pips = (priceDiff / PIP_VALUE) * multiplier;
  return pips * pipValue * size;
}

/**
 * Calculate Risk/Reward ratio
 */
export function calculateRiskReward(
  entryPrice: number,
  stopLoss: number,
  takeProfit: number,
  side: 'buy' | 'sell'
): number {
  let risk: number;
  let reward: number;

  if (side === 'buy') {
    risk = entryPrice - stopLoss;
    reward = takeProfit - entryPrice;
  } else {
    risk = stopLoss - entryPrice;
    reward = entryPrice - takeProfit;
  }

  if (risk <= 0) return 0;
  return reward / risk;
}

/**
 * Calculate position size based on risk percentage
 */
export function calculatePositionSize(
  accountBalance: number,
  riskPercent: number,
  stopLossPips: number,
  pipValuePerLot: number = 10
): number {
  if (stopLossPips <= 0) return 0;
  const riskAmount = accountBalance * (riskPercent / 100);
  return riskAmount / (stopLossPips * pipValuePerLot);
}

/**
 * Calculate dollar risk for a trade
 */
export function calculateRisk(
  entryPrice: number,
  stopLoss: number,
  lotSize: number,
  pipValuePerLot: number = 10
): number {
  const pips = calculatePips(entryPrice, stopLoss);
  return pips * pipValuePerLot * lotSize;
}

/**
 * Calculate win rate from trades
 */
export function calculateWinRate(wins: number, total: number): number {
  if (total === 0) return 0;
  return (wins / total) * 100;
}

/**
 * Calculate profit factor
 */
export function calculateProfitFactor(grossProfit: number, grossLoss: number): number {
  if (grossLoss === 0) return grossProfit > 0 ? Infinity : 0;
  return grossProfit / Math.abs(grossLoss);
}

/**
 * Calculate expectancy (average expected profit per trade)
 */
export function calculateExpectancy(
  winRate: number,
  avgWin: number,
  avgLoss: number
): number {
  const winProbability = winRate / 100;
  const loseProbability = 1 - winProbability;
  return winProbability * avgWin - loseProbability * Math.abs(avgLoss);
}

/**
 * Calculate Sharpe Ratio
 */
export function calculateSharpeRatio(
  returns: number[],
  riskFreeRate: number = 0
): number {
  if (returns.length === 0) return 0;

  const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
  const excessReturn = avgReturn - riskFreeRate;

  const variance =
    returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
  const stdDev = Math.sqrt(variance);

  if (stdDev === 0) return 0;
  return excessReturn / stdDev;
}

/**
 * Calculate maximum drawdown from equity curve
 */
export function calculateMaxDrawdown(equityCurve: number[]): number {
  if (equityCurve.length === 0) return 0;

  let peak = equityCurve[0];
  let maxDrawdown = 0;

  for (const equity of equityCurve) {
    if (equity > peak) {
      peak = equity;
    }
    const drawdown = ((equity - peak) / peak) * 100;
    if (drawdown < maxDrawdown) {
      maxDrawdown = drawdown;
    }
  }

  return maxDrawdown;
}

/**
 * Calculate Sortino Ratio (only considers downside volatility)
 */
export function calculateSortinoRatio(
  returns: number[],
  riskFreeRate: number = 0
): number {
  if (returns.length === 0) return 0;

  const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
  const excessReturn = avgReturn - riskFreeRate;

  const negativeReturns = returns.filter((r) => r < 0);
  if (negativeReturns.length === 0) return excessReturn > 0 ? Infinity : 0;

  const downsideVariance =
    negativeReturns.reduce((sum, r) => sum + Math.pow(r, 2), 0) / negativeReturns.length;
  const downsideDeviation = Math.sqrt(downsideVariance);

  if (downsideDeviation === 0) return 0;
  return excessReturn / downsideDeviation;
}

/**
 * Calculate Calmar Ratio (return / max drawdown)
 */
export function calculateCalmarRatio(
  annualReturn: number,
  maxDrawdown: number
): number {
  if (maxDrawdown === 0) return 0;
  return annualReturn / Math.abs(maxDrawdown);
}

/**
 * Calculate margin required for a position
 * Assuming 1:100 leverage for forex
 */
export function calculateMargin(
  price: number,
  lotSize: number,
  leverage: number = 100
): number {
  const contractSize = 100000; // Standard lot
  return (price * lotSize * contractSize) / leverage;
}

/**
 * Convert price to pips
 */
export function priceToPips(price: number): number {
  return price / PIP_VALUE;
}

/**
 * Convert pips to price
 */
export function pipsToPrice(pips: number): number {
  return pips * PIP_VALUE;
}
