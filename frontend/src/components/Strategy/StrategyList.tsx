import React, { useState, useEffect } from 'react';
import { strategyApi } from '../../services/api';
import { useStrategyStore } from '../../store';
import { Strategy } from '../../types';

export function StrategyList() {
  const { strategies, setStrategies, selectStrategy } = useStrategyStore();
  const [availableStrategies, setAvailableStrategies] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    try {
      const response = await strategyApi.list();
      setAvailableStrategies(response.data.strategies || []);
    } catch (error) {
      console.error('Error loading strategies:', error);
    }
  };

  const handleCreateStrategy = async (strategyType: string) => {
    setLoading(true);
    try {
      const config = {
        type: strategyType,
        params: {},
      };
      const response = await strategyApi.create(config);
      const newStrategy: Strategy = {
        id: Date.now().toString(),
        name: response.data.strategy.name,
        type: strategyType,
        params: response.data.strategy.params,
      };
      useStrategyStore.getState().addStrategy(newStrategy);
    } catch (error) {
      console.error('Error creating strategy:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="strategy-list">
      <h2>Strategies</h2>
      <div className="strategy-grid">
        {availableStrategies.map((strategy) => (
          <div key={strategy.name} className="strategy-card">
            <h3>{strategy.class_name}</h3>
            <p>{strategy.description}</p>
            <div className="strategy-actions">
              <button onClick={() => handleCreateStrategy(strategy.name)} disabled={loading}>
                Use Strategy
              </button>
            </div>
          </div>
        ))}
      </div>

      <h3>My Strategies</h3>
      {strategies.length === 0 ? (
        <p>No strategies created yet</p>
      ) : (
        <div className="my-strategies">
          {strategies.map((strategy) => (
            <div key={strategy.id} className="strategy-item">
              <div>
                <h4>{strategy.name}</h4>
                <p>Type: {strategy.type}</p>
              </div>
              <div className="actions">
                <button onClick={() => selectStrategy(strategy)}>Edit</button>
                <button onClick={() => useStrategyStore.getState().deleteStrategy(strategy.id!)}>
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

