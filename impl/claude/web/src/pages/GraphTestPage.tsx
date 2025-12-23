/**
 * GraphTestPage — Quick test page for SpecGraph Visualizer
 */

import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { SpecGraphViewer } from '../membrane/graph';

import '../membrane/Membrane.css';

export function GraphTestPage() {
  const navigate = useNavigate();

  const handleNodeClick = useCallback((path: string) => {
    console.log('Clicked node:', path);
    // Could navigate to /ledger with the spec selected
    // navigate(`/ledger?spec=${encodeURIComponent(path)}`);
  }, []);

  return (
    <div className="membrane" style={{ background: 'var(--surface-0)' }}>
      {/* Header */}
      <header
        style={{
          padding: '12px 16px',
          background: 'var(--surface-1)',
          borderBottom: '1px solid var(--surface-3)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <h1 style={{ margin: 0, fontSize: '16px', color: 'var(--text-primary)' }}>
          SpecGraph Visualizer
        </h1>
        <button
          onClick={() => navigate('/')}
          style={{
            padding: '6px 12px',
            background: 'var(--surface-2)',
            border: '1px solid var(--surface-3)',
            borderRadius: '4px',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
          }}
        >
          ← Back
        </button>
      </header>

      {/* Graph */}
      <div style={{ flex: 1, minHeight: 0 }}>
        <SpecGraphViewer onNodeClick={handleNodeClick} limit={50} showMinimap showControls />
      </div>
    </div>
  );
}

export default GraphTestPage;
