/**
 * Witness Page - TerrariumView for Walk Dashboard
 *
 * WARP Phase 3 Foundation: Session 7.
 *
 * "Trust is the currency of agency. The Witness watches, learns, and earns."
 *
 * This page displays:
 * - Active and recent Walks as SceneGraph
 * - Click to view Walk details (trace timeline)
 * - Living Earth theme with breathing surfaces
 *
 * @see protocols/agentese/contexts/time_trace_warp.py - time.walk.list
 * @see protocols/agentese/projection/warp_converters.py - walk_dashboard_to_scene
 * @see docs/skills/metaphysical-fullstack.md - Fullstack pattern
 */

import { useState, useCallback } from 'react';
import { RefreshCw, Activity, Eye } from 'lucide-react';
import { ServoSceneRenderer } from '../components/servo';
import { useWalkDashboard } from '../hooks/useWalkDashboard';
import { ShellErrorBoundary } from '../shell/ShellErrorBoundary';
import type { SceneNode } from '../components/servo/ServoNodeRenderer';

// =============================================================================
// Component
// =============================================================================

function WitnessDashboard() {
  const { scene, isLoading, error, refetch, walkCount } = useWalkDashboard({
    limit: 20,
    refreshInterval: 30000, // Refresh every 30s
  });

  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  // Handle node selection
  const handleNodeSelect = useCallback((node: SceneNode) => {
    setSelectedNodeId(node.id);

    // If it's a WALK node, we could fetch its trace timeline
    if (node.kind === 'WALK') {
      const walkId = (node.metadata as { walk_id?: string })?.walk_id;
      if (walkId) {
        console.log('[Witness] Selected walk:', walkId);
        // TODO: Phase 3 enhancement - fetch trace timeline
      }
    }
  }, []);

  // Loading state
  if (isLoading && !scene) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-400">
        <Activity className="w-12 h-12 animate-pulse mb-4" />
        <p>Loading Walk dashboard...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-400">
        <div className="text-red-400 mb-4">
          <Eye className="w-12 h-12" />
        </div>
        <p className="text-red-400 mb-2">Failed to load dashboard</p>
        <p className="text-gray-500 text-sm mb-4">{error.message}</p>
        <button
          onClick={refetch}
          className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-800/50">
        <div className="flex items-center gap-3">
          <Eye className="w-6 h-6 text-emerald-400" />
          <h1 className="text-xl font-semibold text-white">Witness</h1>
          <span className="text-sm text-gray-500">
            {walkCount} walk{walkCount !== 1 ? 's' : ''}
          </span>
        </div>

        <div className="flex items-center gap-4">
          {/* Refresh button */}
          <button
            onClick={refetch}
            disabled={isLoading}
            className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-400 hover:text-white bg-gray-800/50 hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50"
            title="Refresh dashboard"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 overflow-auto p-6 bg-gradient-to-b from-gray-900 to-gray-950">
        {scene ? (
          <ServoSceneRenderer
            scene={scene}
            selectedNodeId={selectedNodeId}
            onNodeSelect={handleNodeSelect}
            showEdges={true}
            className="min-h-full"
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <div className="text-4xl mb-4">🌿</div>
            <p className="text-lg mb-2">No walks yet</p>
            <p className="text-sm text-gray-600">
              Start a Walk to see it appear here
            </p>
          </div>
        )}
      </main>

      {/* Selected node detail panel (Phase 3 enhancement) */}
      {selectedNodeId && (
        <footer className="px-6 py-3 border-t border-gray-800/50 bg-gray-900/50">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">
              Selected: <code className="text-emerald-400">{selectedNodeId.slice(0, 16)}...</code>
            </span>
            <button
              onClick={() => setSelectedNodeId(null)}
              className="text-gray-500 hover:text-white transition-colors"
            >
              Clear selection
            </button>
          </div>
        </footer>
      )}
    </div>
  );
}

// =============================================================================
// Page Export with Error Boundary
// =============================================================================

export default function WitnessPage() {
  return (
    <ShellErrorBoundary layer="projection">
      <WitnessDashboard />
    </ShellErrorBoundary>
  );
}
