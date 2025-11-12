import React, { useState } from 'react';
import { indicatorsApi } from '../../services/api';
import { useDataStore } from '../../store/dataStore';
import { INDICATOR_NAMES } from '../../utils/constants';

export function IndicatorPanel() {
  const { indicators, addIndicator, removeIndicator } = useDataStore();
  const [selectedIndicator, setSelectedIndicator] = useState<string>('');
  const [params, setParams] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);

  const handleAddIndicator = async () => {
    if (!selectedIndicator) return;

    setLoading(true);
    try {
      const { historicalData } = useDataStore.getState();
      const timeframe = useDataStore.getState().historicalData ? Object.keys(historicalData)[0] : '1h';
      const data = historicalData[timeframe] || [];

      if (data.length === 0) {
        alert('Please load historical data first');
        return;
      }

      const response = await indicatorsApi.calculate({
        indicator: selectedIndicator,
        price_data: data,
        params,
      });

      if (response.data.type === 'series') {
        addIndicator(selectedIndicator, response.data.values);
      }
    } catch (error) {
      console.error('Error calculating indicator:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="indicator-panel">
      <h3>Indicators</h3>
      <div className="indicator-selector">
        <select
          value={selectedIndicator}
          onChange={(e) => setSelectedIndicator(e.target.value)}
        >
          <option value="">Select Indicator</option>
          {INDICATOR_NAMES.map((name) => (
            <option key={name} value={name}>
              {name.toUpperCase()}
            </option>
          ))}
        </select>
        <button onClick={handleAddIndicator} disabled={loading || !selectedIndicator}>
          {loading ? 'Adding...' : 'Add Indicator'}
        </button>
      </div>
      <div className="active-indicators">
        <h4>Active Indicators</h4>
        {Object.keys(indicators).length === 0 ? (
          <p>No indicators added</p>
        ) : (
          <ul>
            {Object.keys(indicators).map((name) => (
              <li key={name}>
                {name}
                <button onClick={() => removeIndicator(name)}>Remove</button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

