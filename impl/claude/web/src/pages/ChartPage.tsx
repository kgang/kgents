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

  const handleNodeClick = useCallback(
    (path: string) => {
      // Navigate to Editor with this spec path
      navigate(`/editor?path=${encodeURIComponent(path)}`);
    },
    [navigate]
  );

  return (
    <div className="membrane" style={{ background: 'var(--surface-0)', height: '100%' }}>
      {/* Chart fills the space — navigation is in AppShell */}
      <div style={{ height: '100%', minHeight: 0 }}>
        <AstronomicalChart onNodeClick={handleNodeClick} limit={100} showControls showLegend />
      </div>
    </div>
  );
}

export default ChartPage;
