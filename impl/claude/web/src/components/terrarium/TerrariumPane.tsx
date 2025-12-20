/**
 * TerrariumPane - Lens-based view pane for trace visualization.
 *
 * WARP Phase 2: React Projection Layer.
 *
 * Provides:
 * - LensSelector for mode switching
 * - SelectionChips for filter display
 * - SceneRenderer for projected content
 *
 * @example
 * <TerrariumPane
 *   defaultLens="timeline"
 *   onNodeSelect={(id) => console.log('Selected:', id)}
 * />
 */

import React, { useEffect } from 'react';
import type { LensMode } from '../../api/types/_generated/world-scenery';
import { useTerrariumView } from '../../hooks/useTerrariumView';
import { SceneRenderer } from '../scene/SceneRenderer';
import { LensSelector } from './LensSelector';
import { SelectionChips } from './SelectionChips';

// =============================================================================
// Types
// =============================================================================

export interface TerrariumPaneProps {
  /** Initial view ID to load */
  viewId?: string;
  /** Default lens mode */
  defaultLens?: LensMode;
  /** Callback when a node is selected */
  onNodeSelect?: (nodeId: string) => void;
  /** Additional CSS classes */
  className?: string;
  /** Auto-project on mount */
  autoProject?: boolean;
}

// =============================================================================
// Component
// =============================================================================

export function TerrariumPane({
  viewId,
  defaultLens = 'TIMELINE',
  onNodeSelect,
  className = '',
  autoProject = true,
}: TerrariumPaneProps): React.ReactElement {
  const {
    scene,
    lens,
    setLensMode,
    predicates,
    removePredicate,
    clearPredicates,
    project,
    isProjecting,
    error,
  } = useTerrariumView({
    viewId,
    defaultLens,
    autoProject: false, // We'll handle it manually
  });

  // Auto-project on mount if enabled
  useEffect(() => {
    if (autoProject) {
      project();
    }
  }, [autoProject, project]);

  // Re-project when lens changes
  useEffect(() => {
    if (scene) {
      project();
    }
  }, [lens]);

  return (
    <div className={`terrarium-pane flex flex-col gap-4 ${className}`}>
      {/* Controls bar */}
      <div className="terrarium-controls flex items-center gap-4 flex-wrap">
        <LensSelector current={lens} onChange={setLensMode} />

        {predicates.length > 0 && (
          <SelectionChips
            predicates={predicates}
            onRemove={removePredicate}
            onClear={clearPredicates}
          />
        )}

        {isProjecting && <span className="text-xs text-gray-500 animate-pulse">Projecting...</span>}
      </div>

      {/* Error display */}
      {error && (
        <div className="terrarium-error bg-red-900/20 border border-red-700/50 rounded p-3">
          <span className="text-sm text-red-400">{error}</span>
        </div>
      )}

      {/* Scene render */}
      <div className="terrarium-content flex-1 min-h-0">
        {scene ? (
          <SceneRenderer
            graph={scene}
            onNodeClick={onNodeSelect}
            className="h-full overflow-auto"
          />
        ) : (
          <div className="flex items-center justify-center h-32 text-gray-500">
            {isProjecting ? 'Loading...' : 'No scene to display'}
          </div>
        )}
      </div>
    </div>
  );
}

export default TerrariumPane;
