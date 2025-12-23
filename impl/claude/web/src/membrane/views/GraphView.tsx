/**
 * GraphView — SpecGraph visualization view
 *
 * Displays the spec graph using Reactflow.
 * Integrates with Membrane focus system.
 */

import { useCallback, useState } from 'react';
import { SpecGraphViewer } from '../graph';

import './GraphView.css';

// =============================================================================
// Types
// =============================================================================

interface GraphViewProps {
  /** Optional filter by status */
  statusFilter?: string;
  /** Callback when a spec is clicked */
  onSpecClick?: (path: string) => void;
}

// =============================================================================
// Component
// =============================================================================

export function GraphView({ statusFilter: initialFilter, onSpecClick }: GraphViewProps) {
  const [statusFilter, setStatusFilter] = useState(initialFilter || '');
  const [limit, setLimit] = useState(50);

  // Handle node click
  const handleNodeClick = useCallback(
    (path: string) => {
      onSpecClick?.(path);
    },
    [onSpecClick]
  );

  return (
    <div className="graph-view">
      {/* Toolbar */}
      <div className="graph-view__toolbar">
        <h3 className="graph-view__title">Spec Graph</h3>
        <div className="graph-view__controls">
          <select
            className="graph-view__select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All Specs</option>
            <option value="ACTIVE">Active</option>
            <option value="ORPHAN">Orphans</option>
            <option value="DEPRECATED">Deprecated</option>
          </select>
          <select
            className="graph-view__select"
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
          >
            <option value={25}>25 specs</option>
            <option value={50}>50 specs</option>
            <option value={100}>100 specs</option>
            <option value={200}>200 specs</option>
          </select>
        </div>
      </div>

      {/* Graph */}
      <div className="graph-view__content">
        <SpecGraphViewer
          statusFilter={statusFilter || undefined}
          limit={limit}
          onNodeClick={handleNodeClick}
          showMinimap
          showControls
        />
      </div>
    </div>
  );
}

export default GraphView;
