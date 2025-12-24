/**
 * ChartPage — Token Registry visualization page
 *
 * Utilitarian flat grid for navigating:
 * - 100s of specs
 * - Dozens of principles
 * - 1000s of implementations
 *
 * "The frame is humble. The content glows."
 */

import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { TokenRegistry } from '../components/registry';

export function ChartPage() {
  const navigate = useNavigate();

  const handleOpenEditor = useCallback(
    (path: string) => {
      // Navigate to Editor with this spec path
      navigate(`/editor/${encodeURIComponent(path)}`);
    },
    [navigate]
  );

  return (
    <div style={{ height: '100%', background: 'var(--color-steel-950)' }}>
      <TokenRegistry onOpenEditor={handleOpenEditor} />
    </div>
  );
}

export default ChartPage;
