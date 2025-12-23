/**
 * ChartPage — Astronomical Chart visualization page
 *
 * "The file is a lie. There is only the graph."
 */

import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { AstronomicalChart } from '../membrane/chart';

import '../membrane/Membrane.css';

export function ChartPage() {
  const navigate = useNavigate();

  const handleNodeClick = useCallback((path: string) => {
    console.log('Clicked star:', path);
    // Could navigate to spec detail
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
          Astronomical Chart
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
          &larr; Back
        </button>
      </header>

      {/* Chart */}
      <div style={{ flex: 1, minHeight: 0 }}>
        <AstronomicalChart onNodeClick={handleNodeClick} limit={100} showControls showLegend />
      </div>
    </div>
  );
}

export default ChartPage;
