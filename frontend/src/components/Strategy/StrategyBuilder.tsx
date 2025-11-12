import React, { useState, useCallback } from 'react';
import ReactFlow, { Node, Edge, Background, Controls, MiniMap, addEdge, Connection, applyNodeChanges, applyEdgeChanges, NodeChange, EdgeChange } from 'reactflow';
import 'reactflow/dist/style.css';

interface StrategyBuilderProps {
  onSave?: (strategy: any) => void;
}

export function StrategyBuilder({ onSave }: StrategyBuilderProps) {
  const [nodes, setNodes] = useState<Node[]>([
    { id: '1', type: 'input', data: { label: 'Entry Condition' }, position: { x: 250, y: 0 } },
    { id: '2', data: { label: 'RSI < 30' }, position: { x: 100, y: 100 } },
    { id: '3', data: { label: 'Price > EMA' }, position: { x: 400, y: 100 } },
    { id: '4', type: 'output', data: { label: 'Buy Signal' }, position: { x: 250, y: 200 } },
  ]);

  const [edges, setEdges] = useState<Edge[]>([
    { id: 'e1-2', source: '1', target: '2' },
    { id: 'e1-3', source: '1', target: '3' },
    { id: 'e2-4', source: '2', target: '4' },
    { id: 'e3-4', source: '3', target: '4' },
  ]);

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    []
  );

  return (
    <div className="strategy-builder">
      <h3>Visual Strategy Builder</h3>
      <p className="description">
        Drag and drop nodes to build your trading strategy. Connect conditions with logic gates (AND/OR).
      </p>
      <div className="builder-toolbar">
        <div className="node-palette">
          <h4>Available Nodes</h4>
          <div className="palette-items">
            <div className="palette-item" draggable>
              <span>📊 Indicator</span>
            </div>
            <div className="palette-item" draggable>
              <span>🔀 Logic Gate</span>
            </div>
            <div className="palette-item" draggable>
              <span>📈 Entry Condition</span>
            </div>
            <div className="palette-item" draggable>
              <span>📉 Exit Condition</span>
            </div>
          </div>
        </div>
        <div className="flow-canvas" style={{ width: '100%', height: '600px' }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>
      </div>
      <div className="builder-actions">
        <button onClick={() => onSave?.({ nodes, edges })}>Save Strategy</button>
        <button>Export as Code</button>
        <button>Clear Canvas</button>
      </div>
    </div>
  );
}

