/**
 * Trail Page - Visual Trail Graph feature.
 *
 * "Bush's Memex realized: Force-directed graph showing exploration trails."
 *
 * Route: /_/trail/:id?
 *
 * Features:
 * - Force-directed graph visualization (react-flow)
 * - Step-by-step reasoning traces
 * - Explorer presence indicators
 * - Budget ring indicator
 * - Trail list sidebar
 *
 * @see spec/protocols/trail-protocol.md Section 8
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

import { useTrail, useTrailList, useTrailMetrics } from '../hooks/useTrail';
import {
  TrailGraph,
  ReasoningPanel,
  ExplorerPresence,
  BudgetRing,
  TrailBuilderPanel,
} from '../components/trail';
import { getEvidenceColor, type TrailSummary } from '../api/trail';

// =============================================================================
// Component
// =============================================================================

export default function TrailPage() {
  const { id: urlTrailId } = useParams<{ id?: string }>();
  const navigate = useNavigate();

  // Trail state
  const {
    trail,
    nodes,
    edges,
    evidence,
    loading,
    error,
    selectedStep,
    loadTrail,
    selectStep,
    forkCurrentTrail,
  } = useTrail(urlTrailId);

  // Trail list for sidebar
  const { trails, loading: listLoading, refresh: refreshList } = useTrailList(20);

  // Trail metrics
  const metrics = useTrailMetrics(trail);

  // Track active trail ID
  const [activeTrailId, setActiveTrailId] = useState<string | null>(
    urlTrailId || null
  );

  // Sync URL with active trail
  useEffect(() => {
    if (urlTrailId && urlTrailId !== activeTrailId) {
      setActiveTrailId(urlTrailId);
      loadTrail(urlTrailId);
    }
  }, [urlTrailId, activeTrailId, loadTrail]);

  // Handle trail selection from sidebar
  const handleSelectTrail = (trailId: string) => {
    setActiveTrailId(trailId);
    navigate(`/_/trail/${trailId}`);
  };

  // Handle trail creation from builder
  const handleTrailCreated = (trailId: string) => {
    refreshList();
    setActiveTrailId(trailId);
    navigate(`/_/trail/${trailId}`);
  };

  // State for fork dialog
  const [showForkDialog, setShowForkDialog] = useState(false);
  const [forkName, setForkName] = useState('');

  // Handle fork
  const handleFork = async () => {
    if (!trail) return;
    setForkName(`${trail.name} (fork)`);
    setShowForkDialog(true);
  };

  const confirmFork = async () => {
    if (!forkName) return;
    const newId = await forkCurrentTrail(forkName);
    if (newId) {
      refreshList();
      navigate(`/_/trail/${newId}`);
    }
    setShowForkDialog(false);
    setForkName('');
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur">
        <div className="max-w-[1800px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-xl font-semibold">Trail Graph</h1>
              {trail && (
                <span className="text-gray-400">
                  {trail.name || 'Untitled Trail'}
                </span>
              )}
            </div>

            {/* Actions */}
            {trail && (
              <div className="flex items-center gap-2">
                <button
                  onClick={handleFork}
                  className="px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded transition-colors"
                >
                  Fork
                </button>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(window.location.href);
                    // Show temporary copied state
                    const btn = document.activeElement as HTMLButtonElement;
                    if (btn) {
                      const original = btn.innerText;
                      btn.innerText = 'Copied!';
                      setTimeout(() => { btn.innerText = original; }, 1500);
                    }
                  }}
                  className="px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded transition-colors"
                >
                  Share
                </button>
              </div>
            )}
          </div>

          {/* Evidence badge */}
          {evidence && (
            <div className="mt-2 flex items-center gap-4 text-sm">
              <span
                className="px-2 py-0.5 rounded font-medium"
                style={{
                  backgroundColor: `${getEvidenceColor(evidence.evidence_strength)}20`,
                  color: getEvidenceColor(evidence.evidence_strength),
                }}
              >
                {evidence.evidence_strength}
              </span>
              <span className="text-gray-500">
                {evidence.step_count} steps |{' '}
                {evidence.unique_paths} paths |{' '}
                {evidence.unique_edges} edges
              </span>
              {metrics.duration && (
                <span className="text-gray-500">{metrics.duration}</span>
              )}
            </div>
          )}
        </div>
      </header>

      {/* Main content */}
      <div className="max-w-[1800px] mx-auto px-6 py-6">
        <div className="grid grid-cols-[240px_1fr_320px] gap-6">
          {/* Sidebar: Trail list */}
          <aside className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-medium text-gray-400">Saved Trails</h2>
              <button
                onClick={refreshList}
                className="text-xs text-gray-500 hover:text-gray-300"
                disabled={listLoading}
              >
                {listLoading ? '...' : 'Refresh'}
              </button>
            </div>

            {/* Trail list */}
            <div className="space-y-1">
              {trails.length === 0 && !listLoading && (
                <div className="text-sm text-gray-600 italic py-4">
                  No saved trails
                </div>
              )}

              {trails.map((t) => (
                <TrailListItem
                  key={t.trail_id}
                  trail={t}
                  isActive={activeTrailId === t.trail_id}
                  onClick={() => handleSelectTrail(t.trail_id)}
                />
              ))}
            </div>

            {/* Trail Builder */}
            <div className="pt-4 border-t border-gray-800">
              <TrailBuilderPanel onTrailCreated={handleTrailCreated} />
            </div>
          </aside>

          {/* Main: Graph visualization */}
          <main>
            {loading && (
              <div className="h-[600px] flex items-center justify-center bg-gray-900 rounded-lg">
                <div className="text-center">
                  <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
                  <div className="text-gray-400">Loading trail...</div>
                </div>
              </div>
            )}

            {error && (
              <div className="h-[600px] flex items-center justify-center bg-gray-900 rounded-lg">
                <div className="text-center text-red-400">
                  <div className="text-2xl mb-2">!</div>
                  <div>{error}</div>
                </div>
              </div>
            )}

            {!loading && !error && (
              <TrailGraph
                nodes={nodes}
                edges={edges}
                selectedStep={selectedStep}
                onSelectStep={selectStep}
              />
            )}
          </main>

          {/* Right panel: Details */}
          <aside className="space-y-4">
            {/* Reasoning trace */}
            <ReasoningPanel
              steps={trail?.steps.map((s, i) => ({
                index: i,
                source_path: s.source_path,
                edge: s.edge,
                destination_paths: s.destination_paths,
                reasoning: s.reasoning,
                loop_status: s.loop_status,
                created_at: s.created_at,
              })) || []}
              selectedStep={selectedStep}
              onSelectStep={selectStep}
            />

            {/* Explorer presence */}
            <ExplorerPresence
              creator={trail ? 'developer' : undefined}
            />

            {/* Budget ring */}
            <BudgetRing
              consumed={metrics.stepCount}
              total={100} // TODO: Get from trail or config
              label="Exploration Budget"
            />
          </aside>
        </div>
      </div>

      {/* Fork Dialog */}
      {showForkDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-700"
          >
            <h3 className="text-lg font-medium mb-4">Fork Trail</h3>
            <input
              type="text"
              value={forkName}
              onChange={(e) => setForkName(e.target.value)}
              placeholder="Trail name"
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white focus:outline-none focus:border-blue-500"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter') confirmFork();
                if (e.key === 'Escape') setShowForkDialog(false);
              }}
            />
            <div className="flex justify-end gap-2 mt-4">
              <button
                onClick={() => setShowForkDialog(false)}
                className="px-4 py-2 text-sm text-gray-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={confirmFork}
                className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-500 rounded"
              >
                Fork
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface TrailListItemProps {
  trail: TrailSummary;
  isActive: boolean;
  onClick: () => void;
}

function TrailListItem({ trail, isActive, onClick }: TrailListItemProps) {
  return (
    <motion.button
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      onClick={onClick}
      className={`
        w-full text-left px-3 py-2 rounded-lg transition-colors
        ${isActive
          ? 'bg-blue-900/30 border border-blue-700/50'
          : 'hover:bg-gray-800 border border-transparent'}
      `}
    >
      <div className="text-sm font-medium text-gray-200 truncate">
        {trail.name || 'Untitled'}
      </div>
      <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
        <span>{trail.step_count} steps</span>
        {trail.forked_from_id && (
          <span className="text-purple-400">forked</span>
        )}
      </div>
      {trail.topics.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-1.5">
          {trail.topics.slice(0, 3).map((topic) => (
            <span
              key={topic}
              className="px-1.5 py-0.5 bg-gray-800 rounded text-xs text-gray-400"
            >
              {topic}
            </span>
          ))}
        </div>
      )}
    </motion.button>
  );
}
