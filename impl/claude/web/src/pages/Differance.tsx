/**
 * Differance — Ghost Heritage Graph Explorer (Enhanced DevEx)
 *
 * The dedicated page for deep heritage exploration. Implements Phase 7 of
 * differance-devex-enlightenment.md: battle-tested, generative developer experience.
 *
 * "Seeing what almost was alongside what is."
 *
 * Features:
 * - TraceTimeline: Real trace data with jewel filtering
 * - TraceInspector: Detailed view of selected trace
 * - GhostExplorationModal: Explore roads not taken
 * - GhostHeritageGraph: Full DAG visualization
 * - Progressive disclosure: Timeline → Inspector → Modal → Full Graph
 *
 * Design Principles:
 * - "Ghosts Are Friends": Roads not taken feel inviting, not haunting
 * - "Temporal Intuition": Time flows left-to-right
 * - "Generative, Not Archival": Answer "What should I do next?"
 *
 * @see spec/protocols/differance.md
 * @see plans/differance-devex-enlightenment.md - Phase 7
 */

import { useState, useCallback, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { GitBranch, Search, ArrowLeft, RefreshCw, Home } from 'lucide-react';
import { Breathe } from '@/components/joy';
import {
  GhostHeritageGraph,
  TraceTimeline,
  TraceInspector,
  GhostExplorationModal,
  RecordingControls,
  ExportPanel,
  useSessionRecording,
  type GhostInfo,
  type ChosenPathInfo,
} from '@/components/differance';
import {
  useHeritageDAG,
  useWhyExplain,
  useDifferanceManifest,
  useTraceAt,
  useRecentTraces,
  type TracePreview,
} from '@/hooks/useDifferanceQuery';
import { EARTH, GREEN, GLOW } from '@/constants/livingEarth';
import { useShell } from '@/shell/ShellProvider';

// =============================================================================
// Types
// =============================================================================

interface DifferancePageState {
  selectedTraceId: string | null;
  inspectorTraceId: string | null;
  searchQuery: string;
  explorationModal: {
    isOpen: boolean;
    ghost: GhostInfo | null;
    chosenPath: ChosenPathInfo | null;
  };
  viewMode: 'split' | 'full-graph' | 'full-timeline';
}

// =============================================================================
// Main Component
// =============================================================================

export default function Differance() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { density } = useShell();
  const isMobile = density === 'compact';

  // State
  const [state, setState] = useState<DifferancePageState>({
    selectedTraceId: searchParams.get('trace'),
    inspectorTraceId: null,
    searchQuery: searchParams.get('trace') || '',
    explorationModal: { isOpen: false, ghost: null, chosenPath: null },
    viewMode: 'split',
  });

  // Fetch manifest for overall status
  const { data: manifest } = useDifferanceManifest();

  // Session recording hook (Phase 7D)
  const {
    session: recordingSession,
    startSession,
    stopSession,
    togglePause,
    markDecision,
    updateSessionName,
    // These will be used when we wire up real-time trace counting:
    // incrementTraceCount,
    // incrementGhostCount,
  } = useSessionRecording({
    autoStopIdleMs: 5 * 60 * 1000, // Auto-stop after 5 minutes idle
  });

  // Fetch recent traces for export
  const { data: recentTracesData } = useRecentTraces({ limit: 50 });

  // Fetch full trace details for export when inspectorTraceId is set
  const { data: fullTraceDetails } = useTraceAt(state.inspectorTraceId || '', {
    enabled: !!state.inspectorTraceId,
  });

  // Fetch heritage DAG when trace is selected
  const {
    data: heritage,
    isLoading: heritageLoading,
    refetch: refetchHeritage,
  } = useHeritageDAG(state.selectedTraceId || '', {
    enabled: !!state.selectedTraceId,
    depth: 15,
  });

  // Fetch why explanation
  const { data: why, isLoading: whyLoading } = useWhyExplain(state.selectedTraceId || '', {
    enabled: !!state.selectedTraceId,
    format: 'full',
  });

  // Replay hook available for future use
  // const { data: replayData } = useReplay(state.selectedTraceId || '', {
  //   enabled: false, // Only fetch on demand
  // });

  // Handle URL trace param changes
  useEffect(() => {
    const traceFromUrl = searchParams.get('trace');
    if (traceFromUrl && traceFromUrl !== state.selectedTraceId) {
      setState((s) => ({
        ...s,
        selectedTraceId: traceFromUrl,
        inspectorTraceId: traceFromUrl,
        searchQuery: traceFromUrl,
      }));
    }
  }, [searchParams, state.selectedTraceId]);

  // Search/select trace
  const handleSearch = useCallback(() => {
    if (state.searchQuery.trim()) {
      const traceId = state.searchQuery.trim();
      setState((s) => ({
        ...s,
        selectedTraceId: traceId,
        inspectorTraceId: traceId,
      }));
      setSearchParams({ trace: traceId });
    }
  }, [state.searchQuery, setSearchParams]);

  const handleSelectTrace = useCallback(
    (traceId: string) => {
      setState((s) => ({
        ...s,
        selectedTraceId: traceId,
        inspectorTraceId: traceId,
        searchQuery: traceId,
      }));
      setSearchParams({ trace: traceId });
    },
    [setSearchParams]
  );

  // Handle trace inspection from timeline
  const handleInspectTrace = useCallback((trace: TracePreview) => {
    setState((s) => ({
      ...s,
      inspectorTraceId: trace.id,
    }));
  }, []);

  // Clear selection
  const handleClear = useCallback(() => {
    setState((s) => ({
      ...s,
      selectedTraceId: null,
      inspectorTraceId: null,
      searchQuery: '',
    }));
    setSearchParams({});
  }, [setSearchParams]);

  // Close inspector
  const handleCloseInspector = useCallback(() => {
    setState((s) => ({ ...s, inspectorTraceId: null }));
  }, []);

  // Node click handler in heritage graph
  const handleNodeClick = useCallback((nodeId: string) => {
    setState((s) => ({ ...s, inspectorTraceId: nodeId }));
  }, []);

  // Open ghost exploration modal
  const handleExploreGhost = useCallback(
    (operation: string, inputs: string[]) => {
      // Find ghost info from heritage
      const ghostNode = heritage?.nodes
        ? Object.values(heritage.nodes).find((n) => n.type === 'ghost' && n.operation === operation)
        : null;

      // Find the chosen path that was taken instead
      const chosenNode = heritage?.nodes
        ? Object.values(heritage.nodes).find((n) => n.type === 'chosen')
        : null;

      setState((s) => ({
        ...s,
        explorationModal: {
          isOpen: true,
          ghost: {
            operation,
            inputs,
            reason: ghostNode?.reason || 'Road not taken',
            explorable: ghostNode?.explorable ?? true,
          },
          chosenPath: chosenNode
            ? {
                traceId: chosenNode.id,
                operation: chosenNode.operation,
                output: chosenNode.output,
              }
            : null,
        },
      }));
    },
    [heritage]
  );

  // Close ghost exploration modal
  const handleCloseExplorationModal = useCallback(() => {
    setState((s) => ({
      ...s,
      explorationModal: { isOpen: false, ghost: null, chosenPath: null },
    }));
  }, []);

  // Handle successful ghost exploration
  const handleGhostExplored = useCallback(
    (branchId: string) => {
      console.log('[Differance] Ghost explored on branch:', branchId);
      refetchHeritage();
    },
    [refetchHeritage]
  );

  // Replay from trace
  const handleReplayFrom = useCallback((traceId: string) => {
    console.log('[Differance] Replay from:', traceId);
    // TODO: Implement replay UI
  }, []);

  // Navigate to parent trace
  const handleNavigateToParent = useCallback(
    (parentTraceId: string) => {
      handleSelectTrace(parentTraceId);
    },
    [handleSelectTrace]
  );

  const isLoading = heritageLoading || whyLoading;

  return (
    <div className="min-h-screen" style={{ backgroundColor: EARTH.soil }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-6"
        >
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/')}
              className="p-2 rounded-lg transition-colors"
              style={{ backgroundColor: `${EARTH.bark}60` }}
              title="Back to Cockpit"
            >
              <ArrowLeft className="w-5 h-5" style={{ color: EARTH.sand }} />
            </button>
            <Breathe intensity={0.3} speed="slow">
              <div
                className="p-2 rounded-lg"
                style={{ backgroundColor: `${GREEN.sage}30`, border: `1px solid ${GREEN.sage}50` }}
              >
                <GitBranch className="w-6 h-6" style={{ color: GREEN.sprout }} />
              </div>
            </Breathe>
            <div>
              <h1 className="text-xl font-bold" style={{ color: GLOW.lantern }}>
                Différance Explorer
              </h1>
              <p className="text-xs" style={{ color: EARTH.sand }}>
                Seeing what almost was alongside what is
              </p>
            </div>
          </div>

          {/* Status badge */}
          <div className="flex items-center gap-3">
            {manifest && (
              <div
                className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs"
                style={{ backgroundColor: `${EARTH.bark}60`, color: EARTH.sand }}
              >
                <span>{manifest.trace_count} traces</span>
                <div
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: manifest.store_connected ? GREEN.mint : GLOW.copper }}
                />
              </div>
            )}

            {/* View mode toggle (desktop only) */}
            {!isMobile && (
              <div
                className="flex gap-1 p-1 rounded-lg"
                style={{ backgroundColor: `${EARTH.bark}60` }}
              >
                {(['split', 'full-timeline', 'full-graph'] as const).map((mode) => (
                  <button
                    key={mode}
                    onClick={() => setState((s) => ({ ...s, viewMode: mode }))}
                    className="px-2.5 py-1 rounded text-xs transition-colors"
                    style={{
                      backgroundColor: state.viewMode === mode ? GREEN.sage : 'transparent',
                      color: state.viewMode === mode ? GLOW.lantern : EARTH.sand,
                    }}
                  >
                    {mode === 'split' ? 'Split' : mode === 'full-timeline' ? 'Timeline' : 'Graph'}
                  </button>
                ))}
              </div>
            )}
          </div>
        </motion.header>

        {/* Recording Controls (Phase 7D) */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="mb-4"
        >
          <RecordingControls
            session={recordingSession}
            onStartSession={startSession}
            onStopSession={stopSession}
            onTogglePause={togglePause}
            onMarkDecision={markDecision}
            onUpdateSessionName={updateSessionName}
            suggestedName={`Session ${new Date().toLocaleDateString()}`}
            compact={isMobile}
          />
        </motion.div>

        {/* Search Bar & Export */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6 flex gap-4"
        >
          {/* Search */}
          <div
            className="flex-1 flex items-center gap-2 p-2 rounded-xl"
            style={{ backgroundColor: `${EARTH.bark}60`, border: `1px solid ${EARTH.wood}` }}
          >
            <Search className="w-5 h-5 ml-2" style={{ color: EARTH.clay }} />
            <input
              type="text"
              value={state.searchQuery}
              onChange={(e) => setState((s) => ({ ...s, searchQuery: e.target.value }))}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Enter trace or output ID..."
              className="flex-1 bg-transparent text-sm outline-none"
              style={{ color: GLOW.lantern }}
            />
            {state.selectedTraceId && (
              <button
                onClick={handleClear}
                className="px-3 py-1.5 rounded-lg text-xs"
                style={{ backgroundColor: `${EARTH.wood}60`, color: EARTH.sand }}
              >
                Clear
              </button>
            )}
            <button
              onClick={handleSearch}
              className="px-4 py-1.5 rounded-lg text-sm font-medium"
              style={{ backgroundColor: GREEN.sage, color: GLOW.lantern }}
            >
              Search
            </button>
          </div>

          {/* Export Panel (Phase 7E) */}
          {!isMobile && (
            <ExportPanel
              session={recordingSession}
              selectedTrace={fullTraceDetails}
              whyResponse={why}
              recentTraces={recentTracesData?.traces}
              compact={isMobile}
              className="w-64"
            />
          )}
        </motion.div>

        {/* Main Content */}
        <div
          className={`grid gap-6 ${
            isMobile
              ? 'grid-cols-1'
              : state.viewMode === 'full-timeline'
                ? 'grid-cols-1'
                : state.viewMode === 'full-graph'
                  ? 'grid-cols-1'
                  : 'grid-cols-12'
          }`}
        >
          {/* Left: Trace Timeline */}
          {(state.viewMode === 'split' || state.viewMode === 'full-timeline') && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className={
                isMobile ? 'order-2' : state.viewMode === 'full-timeline' ? '' : 'col-span-4'
              }
            >
              <TraceTimeline
                limit={20}
                onViewAll={() => setState((s) => ({ ...s, viewMode: 'full-timeline' }))}
                onExploreHeritage={handleSelectTrace}
                onInspect={handleInspectTrace}
                compact={isMobile}
              />
            </motion.div>
          )}

          {/* Center/Right: Heritage Graph or Inspector */}
          {(state.viewMode === 'split' || state.viewMode === 'full-graph') && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className={
                isMobile
                  ? 'order-1'
                  : state.viewMode === 'full-graph'
                    ? ''
                    : state.inspectorTraceId
                      ? 'col-span-5'
                      : 'col-span-8'
              }
            >
              {/* No trace selected */}
              {!state.selectedTraceId && (
                <div
                  className="flex flex-col items-center justify-center py-16 rounded-xl"
                  style={{ backgroundColor: `${EARTH.bark}40`, border: `1px solid ${EARTH.wood}` }}
                >
                  <Breathe intensity={0.3} speed="slow">
                    <GitBranch className="w-12 h-12 mb-4" style={{ color: EARTH.clay }} />
                  </Breathe>
                  <h2 className="text-lg font-medium mb-2" style={{ color: GLOW.lantern }}>
                    Select a trace to explore
                  </h2>
                  <p className="text-sm text-center max-w-md" style={{ color: EARTH.sand }}>
                    Choose a trace from the timeline or search by ID to see its full heritage graph.
                  </p>
                </div>
              )}

              {/* Loading */}
              {state.selectedTraceId && isLoading && (
                <div
                  className="flex flex-col items-center justify-center py-16 rounded-xl"
                  style={{ backgroundColor: `${EARTH.bark}40`, border: `1px solid ${EARTH.wood}` }}
                >
                  <Breathe intensity={0.5} speed="fast">
                    <RefreshCw
                      className="w-8 h-8 animate-spin mb-4"
                      style={{ color: GREEN.sprout }}
                    />
                  </Breathe>
                  <p className="text-sm" style={{ color: EARTH.sand }}>
                    Building heritage graph...
                  </p>
                </div>
              )}

              {/* Heritage Graph */}
              {state.selectedTraceId && heritage && !isLoading && (
                <GhostHeritageGraph
                  heritage={heritage}
                  why={why}
                  onNodeClick={handleNodeClick}
                  onExploreGhost={(nodeId) => {
                    const node = heritage.nodes[nodeId];
                    if (node) {
                      handleExploreGhost(node.operation, node.inputs);
                    }
                  }}
                  onRefetch={refetchHeritage}
                  isLoading={isLoading}
                />
              )}

              {/* No heritage found */}
              {state.selectedTraceId && !heritage && !isLoading && (
                <div
                  className="flex flex-col items-center justify-center py-16 rounded-xl"
                  style={{ backgroundColor: `${EARTH.bark}40`, border: `1px solid ${EARTH.wood}` }}
                >
                  <GitBranch className="w-12 h-12 mb-4" style={{ color: GLOW.copper }} />
                  <h2 className="text-lg font-medium mb-2" style={{ color: GLOW.lantern }}>
                    No heritage found
                  </h2>
                  <p className="text-sm text-center max-w-md" style={{ color: EARTH.sand }}>
                    No trace data found for "{state.selectedTraceId}".
                    <br />
                    Try a different trace ID or wait for more operations to be recorded.
                  </p>
                  <button
                    onClick={handleClear}
                    className="mt-4 px-4 py-2 rounded-lg text-sm flex items-center gap-2"
                    style={{ backgroundColor: GREEN.sage, color: GLOW.lantern }}
                  >
                    <Home className="w-4 h-4" />
                    Clear selection
                  </button>
                </div>
              )}
            </motion.div>
          )}

          {/* Right: Trace Inspector (when trace selected) */}
          <AnimatePresence>
            {state.inspectorTraceId && state.viewMode === 'split' && !isMobile && (
              <motion.div
                initial={{ opacity: 0, x: 20, width: 0 }}
                animate={{ opacity: 1, x: 0, width: 'auto' }}
                exit={{ opacity: 0, x: 20, width: 0 }}
                className="col-span-3"
              >
                <TraceInspector
                  traceId={state.inspectorTraceId}
                  onClose={handleCloseInspector}
                  onExploreGhost={(operation, inputs) => handleExploreGhost(operation, inputs)}
                  onReplayFrom={handleReplayFrom}
                  onNavigateToParent={handleNavigateToParent}
                  onViewHeritage={handleSelectTrace}
                  compact
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Mobile: Inspector as bottom sheet would go here */}
        {/* For now, just show inline on mobile */}
        <AnimatePresence>
          {state.inspectorTraceId && isMobile && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="mt-6"
            >
              <TraceInspector
                traceId={state.inspectorTraceId}
                onClose={handleCloseInspector}
                onExploreGhost={(operation, inputs) => handleExploreGhost(operation, inputs)}
                onReplayFrom={handleReplayFrom}
                onNavigateToParent={handleNavigateToParent}
                onViewHeritage={handleSelectTrace}
                compact
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Mobile Export Panel (Phase 7E) */}
        {isMobile && (recordingSession || fullTraceDetails) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6"
          >
            <ExportPanel
              session={recordingSession}
              selectedTrace={fullTraceDetails}
              whyResponse={why}
              recentTraces={recentTracesData?.traces}
              compact
            />
          </motion.div>
        )}

        {/* Ghost Exploration Modal */}
        <GhostExplorationModal
          isOpen={state.explorationModal.isOpen}
          onClose={handleCloseExplorationModal}
          ghost={state.explorationModal.ghost}
          chosenPath={state.explorationModal.chosenPath}
          onExplored={handleGhostExplored}
        />

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center text-xs pt-8"
          style={{ color: EARTH.clay }}
        >
          <p>
            "The ghost heritage graph is the UI innovation: seeing what almost was alongside what
            is."
          </p>
        </motion.footer>
      </div>
    </div>
  );
}
