export function calculatePips(price1: number, price2: number): number {
  return Math.abs(price1 - price2) * 10000;
}

export function calculatePnL(
  entryPrice: number,
  exitPrice: number,
  size: number,
  side: 'buy' | 'sell'
): number {
  const pipValue = 10; // $10 per pip for 1 lot GBP/USD
  const pips = calculatePips(entryPrice, exitPrice);
  const multiplier = side === 'buy' ? 1 : -1;
  return pips * pipValue * size * multiplier;
}

export function calculateRiskReward(
  entryPrice: number,
  stopLoss: number,
  takeProfit: number,
  side: 'buy' | 'sell'
): number {
  const risk = Math.abs(entryPrice - stopLoss);
  const reward = Math.abs(takeProfit - entryPrice);
  return reward / risk;
}

