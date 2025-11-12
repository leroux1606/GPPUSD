import React from 'react';
import { useTradingStore } from '../../store';
import { tradingApi } from '../../services/api';
import { formatCurrency } from '../../utils/formatters';

export function PositionManager() {
  const { positions, updatePosition, closePosition } = useTradingStore();

  const handleClosePosition = async (positionId: string) => {
    try {
      await tradingApi.closePosition(positionId);
      closePosition(positionId);
    } catch (error) {
      console.error('Error closing position:', error);
    }
  };

  const handleModifyStopLoss = async (positionId: string, newStopLoss: number) => {
    try {
      updatePosition(positionId, { stop_loss: newStopLoss });
    } catch (error) {
      console.error('Error modifying stop loss:', error);
    }
  };

  const handleModifyTakeProfit = async (positionId: string, newTakeProfit: number) => {
    try {
      updatePosition(positionId, { take_profit: newTakeProfit });
    } catch (error) {
      console.error('Error modifying take profit:', error);
    }
  };

  return (
    <div className="position-manager">
      <h3>Manage Positions</h3>
      {positions.length === 0 ? (
        <p>No open positions</p>
      ) : (
        <div className="positions-list">
          {positions.map((position) => (
            <div key={position.id} className="position-card">
              <div className="position-info">
                <div>
                  <strong>{position.symbol}</strong> - {position.side.toUpperCase()}
                </div>
                <div>Size: {position.size} lots</div>
                <div>Entry: {position.entry_price.toFixed(5)}</div>
                {position.pnl !== undefined && (
                  <div className={position.pnl >= 0 ? 'positive' : 'negative'}>
                    P&L: {formatCurrency(position.pnl)}
                  </div>
                )}
              </div>
              <div className="position-actions">
                <div>
                  <label>Stop Loss:</label>
                  <input
                    type="number"
                    value={position.stop_loss || ''}
                    onChange={(e) =>
                      handleModifyStopLoss(position.id, parseFloat(e.target.value))
                    }
                  />
                </div>
                <div>
                  <label>Take Profit:</label>
                  <input
                    type="number"
                    value={position.take_profit || ''}
                    onChange={(e) =>
                      handleModifyTakeProfit(position.id, parseFloat(e.target.value))
                    }
                  />
                </div>
                <button onClick={() => handleClosePosition(position.id)}>Close</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

