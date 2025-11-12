import React, { useState } from 'react';
import { useStrategyStore } from '../../store';
import { Strategy } from '../../types';

export function StrategyEditor() {
  const { selectedStrategy, updateStrategy } = useStrategyStore();
  const [params, setParams] = useState<Record<string, any>>({});

  React.useEffect(() => {
    if (selectedStrategy) {
      setParams(selectedStrategy.params);
    }
  }, [selectedStrategy]);

  const handleSave = () => {
    if (selectedStrategy) {
      updateStrategy(selectedStrategy.id!, {
        ...selectedStrategy,
        params,
      });
    }
  };

  if (!selectedStrategy) {
    return <div>No strategy selected</div>;
  }

  return (
    <div className="strategy-editor">
      <h2>Edit Strategy: {selectedStrategy.name}</h2>
      <div className="editor-form">
        {Object.entries(params).map(([key, value]) => (
          <div key={key} className="param-field">
            <label>{key}</label>
            <input
              type={typeof value === 'number' ? 'number' : 'text'}
              value={value}
              onChange={(e) =>
                setParams({
                  ...params,
                  [key]: typeof value === 'number' ? parseFloat(e.target.value) : e.target.value,
                })
              }
            />
          </div>
        ))}
        <button onClick={handleSave}>Save Changes</button>
      </div>
    </div>
  );
}

