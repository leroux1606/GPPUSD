import React, { useState } from 'react';
import { indicatorsApi } from '../../services/api';
import { useDataStore } from '../../store/dataStore';
import { useUIStore } from '../../store/uiStore';
import { INDICATOR_NAMES } from '../../utils/constants';
import { InlineSpinner } from '../Common/LoadingSpinner';

interface IndicatorParams {
  [key: string]: number | string;
}

const DEFAULT_PARAMS: { [key: string]: IndicatorParams } = {
  sma: { period: 20 },
  ema: { period: 20 },
  macd: { fast_period: 12, slow_period: 26, signal_period: 9 },
  rsi: { period: 14 },
  bollinger_bands: { period: 20, std_dev: 2 },
  atr: { period: 14 },
  stochastic: { k_period: 14, d_period: 3 },
  cci: { period: 20 },
  adx: { period: 14 },
};

export function IndicatorPanel() {
  const { indicators, addIndicator, removeIndicator, historicalData } = useDataStore();
  const { selectedTimeframe } = useUIStore();
  const [selectedIndicator, setSelectedIndicator] = useState<string>('');
  const [params, setParams] = useState<IndicatorParams>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleIndicatorSelect = (indicator: string) => {
    setSelectedIndicator(indicator);
    setParams(DEFAULT_PARAMS[indicator] || {});
    setError(null);
  };

  const handleAddIndicator = async () => {
    if (!selectedIndicator) {
      setError('Please select an indicator');
      return;
    }

    const data = historicalData[selectedTimeframe];
    if (!data || data.length === 0) {
      setError('Please load historical data first (go to Charts page)');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await indicatorsApi.calculate({
        indicator: selectedIndicator,
        price_data: data,
        params,
      });

      if (response.data) {
        const indicatorData = {
          name: selectedIndicator,
          values: response.data.values || [],
          color: getIndicatorColor(selectedIndicator),
          type: getIndicatorType(selectedIndicator),
        };
        addIndicator(selectedIndicator, indicatorData);
        setSelectedIndicator('');
        setParams({});
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to calculate indicator';
      setError(errorMessage);
      console.error('Error calculating indicator:', err);
    } finally {
      setLoading(false);
    }
  };

  const getIndicatorColor = (indicator: string): string => {
    const colors: { [key: string]: string } = {
      sma: '#2196f3',
      ema: '#ff9800',
      macd: '#9c27b0',
      rsi: '#4caf50',
      bollinger_bands: '#e91e63',
      atr: '#00bcd4',
      stochastic: '#ff5722',
      cci: '#673ab7',
      adx: '#795548',
    };
    return colors[indicator] || '#9ca3af';
  };

  const getIndicatorType = (indicator: string): 'overlay' | 'separate' => {
    const overlayIndicators = ['sma', 'ema', 'bollinger_bands'];
    return overlayIndicators.includes(indicator) ? 'overlay' : 'separate';
  };

  return (
    <div className="indicator-panel">
      <h3>Technical Indicators</h3>
      
      {/* Indicator Selection */}
      <div className="indicator-selector">
        <select
          value={selectedIndicator}
          onChange={(e) => handleIndicatorSelect(e.target.value)}
          disabled={loading}
        >
          <option value="">Select Indicator</option>
          {INDICATOR_NAMES.map((name) => (
            <option 
              key={name} 
              value={name}
              disabled={Object.keys(indicators).includes(name)}
            >
              {name.toUpperCase()}
              {Object.keys(indicators).includes(name) ? ' (added)' : ''}
            </option>
          ))}
        </select>
      </div>

      {/* Parameter Inputs */}
      {selectedIndicator && Object.keys(params).length > 0 && (
        <div className="indicator-params">
          <h4>Parameters</h4>
          {Object.entries(params).map(([key, value]) => (
            <div key={key} className="param-input">
              <label>{key.replace(/_/g, ' ')}</label>
              <input
                type="number"
                value={value}
                onChange={(e) =>
                  setParams({
                    ...params,
                    [key]: parseFloat(e.target.value) || 0,
                  })
                }
                disabled={loading}
              />
            </div>
          ))}
        </div>
      )}

      {/* Error Message */}
      {error && <div className="indicator-error">{error}</div>}

      {/* Add Button */}
      <button
        onClick={handleAddIndicator}
        disabled={loading || !selectedIndicator}
        className="add-indicator-btn"
      >
        {loading ? (
          <>
            <InlineSpinner size={14} /> Calculating...
          </>
        ) : (
          'Add Indicator'
        )}
      </button>

      {/* Active Indicators */}
      <div className="active-indicators">
        <h4>Active Indicators ({Object.keys(indicators).length})</h4>
        {Object.keys(indicators).length === 0 ? (
          <p className="no-indicators">No indicators added yet</p>
        ) : (
          <ul>
            {Object.entries(indicators).map(([name, data]) => (
              <li key={name}>
                <span
                  className="indicator-color"
                  style={{ backgroundColor: data.color || '#9ca3af' }}
                />
                <span className="indicator-name">{name.toUpperCase()}</span>
                <span className="indicator-type">{data.type}</span>
                <button
                  onClick={() => removeIndicator(name)}
                  className="remove-btn"
                  title="Remove indicator"
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Info */}
      <div className="indicator-info">
        <p>
          Indicators are calculated using historical data. Make sure data is loaded before adding
          indicators.
        </p>
      </div>
    </div>
  );
}
