/**
 * Brain Page - Holographic Memory Interface
 *
 * Provides UI for:
 * - Capturing content to memory
 * - Surfacing ghost memories
 * - Viewing 3D memory topology (Spike 3B: Cartography 3D Enhancement)
 * - Checking brain status
 *
 * Session 6: Crown Jewel Brain Web UI
 * Session 7: 3D Topology Visualization
 * Session 8: Elastic UI Refactor (matching Gestalt patterns)
 *
 * Layout Modes:
 * - Desktop (>1024px): Canvas | Controls panel (resizable)
 * - Tablet (768-1024px): Canvas | Controls (collapsible)
 * - Mobile (<768px): Full canvas + floating actions + drawer panels
 *
 * @see plans/web-refactor/elastic-audit-report.md
 */

import { useState, useEffect, Suspense, useCallback } from 'react';
import { brainApi } from '../api/client';
import type {
  BrainStatusResponse,
  BrainMapResponse,
  BrainTopologyResponse,
  GhostMemory,
  TopologyNode,
} from '../api/types';
import { BrainTopology } from '../components/BrainTopology';
import { ErrorBoundary } from '../components/error/ErrorBoundary';
import { ElasticSplit } from '../components/elastic/ElasticSplit';
import { BottomDrawer } from '../components/elastic/BottomDrawer';
import { FloatingActions } from '../components/elastic/FloatingActions';
import { useWindowLayout } from '../hooks/useLayoutContext';
import {
  ObserverSwitcher,
  useObserverState,
  DEFAULT_OBSERVERS,
} from '../components/path';
import {
  PersonalityLoading,
  Breathe,
  PopOnMount,
  celebrate,
} from '../components/joy';
import { CrystalDetail } from '../components/brain';
import { useSynergyToast } from '../components/synergy';
import { getEmptyState, getLoadingMessage } from '../constants';

// =============================================================================
// Constants - Density-aware scaling
// =============================================================================

type Density = 'compact' | 'comfortable' | 'spacious';

/** Panel collapse breakpoint */
const PANEL_COLLAPSE_BREAKPOINT = 768;

/** Maximum ghost results by density */
const MAX_GHOST_RESULTS = {
  compact: 3,
  comfortable: 5,
  spacious: 10,
} as const;

/** Default showLabels by density (off on mobile for performance) */
const DEFAULT_SHOW_LABELS = {
  compact: false,
  comfortable: true,
  spacious: true,
} as const;

interface PanelState {
  controls: boolean;
  capture: boolean;
}

// =============================================================================
// Loading & Error States (Pattern: Contextual loading > spinner)
// =============================================================================

/**
 * Contextual loading state for 3D topology.
 * Shows brain-specific animation with personality.
 * Foundation 5: Personality & Joy
 */
function TopologyLoading() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900">
      <PersonalityLoading jewel="brain" size="lg" action="analyze" />
      <p className="text-gray-600 text-xs mt-2">Initializing 3D renderer</p>
    </div>
  );
}

/**
 * Error fallback for 3D rendering failures.
 * Gracefully degrades to 2D stats view.
 */
function TopologyErrorFallback({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900 p-8">
      <div className="text-5xl mb-4">⚠️</div>
      <h3 className="text-lg font-semibold text-gray-300 mb-2">3D Rendering Failed</h3>
      <p className="text-gray-500 text-sm text-center mb-4 max-w-md">
        The 3D topology couldn't be rendered. This can happen on devices without WebGL support
        or when GPU memory is limited.
      </p>
      <div className="flex gap-3">
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded text-sm font-medium transition-colors"
        >
          Try Again
        </button>
        <button
          onClick={() => window.location.href = '#panels'}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
        >
          Use 2D View
        </button>
      </div>
    </div>
  );
}

/**
 * Connection error display.
 * Shows when the backend API isn't reachable.
 */
function ConnectionError({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900 p-8">
      <div className="text-5xl mb-4">🔌</div>
      <h3 className="text-lg font-semibold text-gray-300 mb-2">Backend Not Connected</h3>
      <pre className="text-gray-500 text-sm text-center mb-4 max-w-lg whitespace-pre-wrap font-mono bg-gray-800 p-4 rounded-lg">
        {error}
      </pre>
      <div className="flex gap-3">
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded text-sm font-medium transition-colors"
        >
          🔄 Retry Connection
        </button>
      </div>
      <p className="text-gray-600 text-xs mt-4 max-w-md text-center">
        The Brain stores data in <code className="text-cyan-400">~/.kgents/brain/patterns.json</code> and will restore your data when the server starts.
      </p>
    </div>
  );
}

/**
 * Empty state when brain has no data.
 */
function EmptyBrainState() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900 p-8">
      <div className="text-5xl mb-4">🧠</div>
      <h3 className="text-lg font-semibold text-gray-300 mb-2">Your Brain is Empty</h3>
      <p className="text-gray-500 text-sm text-center mb-4 max-w-md">
        Start capturing thoughts, notes, or information using the "Quick Capture" panel.
        Your brain data will persist across server restarts.
      </p>
      <div className="text-xs text-gray-600 mt-4">
        Data stored in: <code className="text-cyan-400">~/.kgents/brain/patterns.json</code>
      </div>
    </div>
  );
}

// =============================================================================
// Control Panel - Density-aware
// =============================================================================

interface ControlPanelProps {
  showEdges: boolean;
  setShowEdges: (v: boolean) => void;
  showGaps: boolean;
  setShowGaps: (v: boolean) => void;
  showLabels: boolean;
  setShowLabels: (v: boolean) => void;
  density: Density;
  isDrawer?: boolean;
  // Observer state (Wave 0 Foundation 2)
  observer: string;
  setObserver: (v: string) => void;
}

function ControlPanel({
  showEdges,
  setShowEdges,
  showGaps,
  setShowGaps,
  showLabels,
  setShowLabels,
  density,
  isDrawer,
  observer,
  setObserver,
}: ControlPanelProps) {
  const isCompact = density === 'compact';

  return (
    <div
      className={`
        ${isCompact ? 'p-3' : 'p-4'}
        ${isDrawer ? 'rounded-t-xl' : ''}
      `}
    >
      {/* Observer Switcher - Wave 0 Foundation 2 */}
      <div className="mb-4">
        <ObserverSwitcher
          current={observer}
          available={DEFAULT_OBSERVERS.brain}
          onChange={setObserver}
          variant={isCompact ? 'minimal' : 'pills'}
          size={isCompact ? 'sm' : 'md'}
        />
      </div>

      <h3 className={`font-semibold text-gray-400 mb-2 uppercase tracking-wide ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
        Display
      </h3>
      <div className={isCompact ? 'flex flex-wrap gap-4' : 'space-y-2'}>
        {[
          { label: 'Connections', checked: showEdges, onChange: setShowEdges },
          { label: 'Knowledge gaps', checked: showGaps, onChange: setShowGaps },
          { label: 'Labels', checked: showLabels, onChange: setShowLabels },
        ].map((opt) => (
          <label key={opt.label} className="flex items-center gap-2 cursor-pointer group">
            <input
              type="checkbox"
              checked={opt.checked}
              onChange={(e) => opt.onChange(e.target.checked)}
              className={`${isCompact ? 'w-3 h-3' : 'w-4 h-4'} rounded bg-gray-700 border-gray-600`}
            />
            <span className={`text-gray-300 group-hover:text-white transition-colors ${isCompact ? 'text-xs' : 'text-sm'}`}>
              {opt.label}
            </span>
          </label>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// Capture Panel - Density-aware
// =============================================================================

interface CapturePanelProps {
  captureContent: string;
  setCaptureContent: (v: string) => void;
  ghostContext: string;
  setGhostContext: (v: string) => void;
  ghostResults: GhostMemory[];
  onCapture: () => void;
  onGhostSurface: () => void;
  loading: boolean;
  density: Density;
  isDrawer?: boolean;
}

function CapturePanel({
  captureContent,
  setCaptureContent,
  ghostContext,
  setGhostContext,
  ghostResults,
  onCapture,
  onGhostSurface,
  loading,
  density,
  isDrawer,
}: CapturePanelProps) {
  const isCompact = density === 'compact';
  const maxResults = MAX_GHOST_RESULTS[density];

  return (
    <div
      className={`
        ${isCompact ? 'p-3 space-y-4' : 'p-4 space-y-6'}
        ${isDrawer ? 'rounded-t-xl' : ''}
      `}
    >
      {/* Quick capture */}
      <div>
        <h3 className={`font-semibold text-gray-400 mb-2 uppercase tracking-wide ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
          Quick Capture
        </h3>
        <textarea
          value={captureContent}
          onChange={(e) => setCaptureContent(e.target.value)}
          placeholder="Enter content to capture..."
          className={`w-full bg-gray-800 rounded px-3 py-2 text-white placeholder-gray-500 resize-none mb-2 ${isCompact ? 'text-xs' : 'text-sm'}`}
          rows={isCompact ? 2 : 3}
        />
        <button
          onClick={onCapture}
          disabled={loading || !captureContent.trim()}
          className={`w-full py-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-gray-700 rounded font-medium transition-colors ${isCompact ? 'text-xs' : 'text-sm'}`}
        >
          {loading ? 'Capturing...' : 'Capture Crystal'}
        </button>
      </div>

      {/* Ghost surfacing */}
      <div>
        <h3 className={`font-semibold text-gray-400 mb-2 uppercase tracking-wide ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
          Ghost Surfacing
        </h3>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={ghostContext}
            onChange={(e) => setGhostContext(e.target.value)}
            placeholder="Context..."
            className={`flex-1 bg-gray-800 rounded px-3 py-2 text-white placeholder-gray-500 ${isCompact ? 'text-xs' : 'text-sm'}`}
            onKeyDown={(e) => e.key === 'Enter' && onGhostSurface()}
          />
          <button
            onClick={onGhostSurface}
            disabled={loading || !ghostContext.trim()}
            className={`px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 rounded transition-colors ${isCompact ? 'text-xs' : 'text-sm'}`}
          >
            Surface
          </button>
        </div>
        {/* Ghost results */}
        {ghostResults.length > 0 && (
          <div className="space-y-2 mt-3">
            {ghostResults.slice(0, maxResults).map((memory) => (
              <div
                key={memory.concept_id}
                className={`bg-gray-800 rounded p-2 border-l-2 border-purple-500 ${isCompact ? 'text-[10px]' : 'text-xs'}`}
              >
                <div className="flex justify-between mb-1">
                  <span className="text-gray-400 font-mono truncate">
                    {memory.concept_id}
                  </span>
                  <span className="text-purple-400">
                    {(memory.relevance * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-gray-300 line-clamp-2">{memory.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function Brain() {
  // Layout context
  const { density, isMobile, isTablet, isDesktop } = useWindowLayout();

  // Data state
  const [status, setStatus] = useState<BrainStatusResponse | null>(null);
  const [map, setMap] = useState<BrainMapResponse | null>(null);
  const [topology, setTopology] = useState<BrainTopologyResponse | null>(null);
  const [captureContent, setCaptureContent] = useState('');
  const [ghostContext, setGhostContext] = useState('');
  const [ghostResults, setGhostResults] = useState<GhostMemory[]>([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [viewMode, setViewMode] = useState<'topology' | 'panels'>('topology');
  const [showEdges, setShowEdges] = useState(true);
  const [showGaps, setShowGaps] = useState(true);
  const [showLabels, setShowLabels] = useState(() => DEFAULT_SHOW_LABELS[density]);
  const [topologyKey, setTopologyKey] = useState(0); // For ErrorBoundary reset

  // Panel state (mobile drawers)
  const [panelState, setPanelState] = useState<PanelState>({
    controls: false,
    capture: false,
  });

  // Selected crystal for detail view (Wave 1: Hero Path Polish)
  const [selectedCrystal, setSelectedCrystal] = useState<TopologyNode | null>(null);

  // Observer state (Wave 0 Foundation 2)
  const [observer, setObserver] = useObserverState('brain', 'technical');

  // Synergy toasts (Wave 4: Cross-jewel notifications)
  const { crystalFormed } = useSynergyToast();

  // Load all brain data
  const loadAllData = useCallback(async () => {
    setInitialLoading(true);
    setConnectionError(null);

    try {
      // Load all in parallel
      const [statusRes, mapRes, topologyRes] = await Promise.all([
        brainApi.getStatus(),
        brainApi.getMap(),
        brainApi.getTopology(0.3),
      ]);

      setStatus(statusRes.data);
      setMap(mapRes.data);
      setTopology(topologyRes.data);
      setConnectionError(null);
    } catch (error: unknown) {
      console.error('Failed to load brain data:', error);

      // Provide helpful error message
      if (error && typeof error === 'object' && 'code' in error) {
        const axiosError = error as { code?: string; message?: string };
        if (axiosError.code === 'ERR_NETWORK' || axiosError.code === 'ECONNREFUSED') {
          setConnectionError(
            'Cannot connect to backend. Make sure the API server is running:\n\n' +
            'cd impl/claude && uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000'
          );
        } else {
          setConnectionError(`Connection error: ${axiosError.message || 'Unknown error'}`);
        }
      } else {
        setConnectionError('Failed to connect to Brain API');
      }
    } finally {
      setInitialLoading(false);
    }
  }, []);

  // Load on mount
  useEffect(() => {
    loadAllData();
  }, [loadAllData]);

  // Refresh all data after capture
  const refreshAfterCapture = async () => {
    try {
      const [statusRes, mapRes, topologyRes] = await Promise.all([
        brainApi.getStatus(),
        brainApi.getMap(),
        brainApi.getTopology(0.3),
      ]);
      setStatus(statusRes.data);
      setMap(mapRes.data);
      setTopology(topologyRes.data);
    } catch (error) {
      console.error('Failed to refresh after capture:', error);
    }
  };

  const handleNodeClick = useCallback((node: TopologyNode) => {
    setSelectedCrystal(node);
  }, []);

  const handleCloseCrystalDetail = useCallback(() => {
    setSelectedCrystal(null);
  }, []);

  // Retry handler for 3D rendering failures
  const handleTopologyRetry = useCallback(() => {
    setTopologyKey((k) => k + 1); // Force remount
    loadAllData(); // Refresh all data
  }, [loadAllData]);

  // Log 3D errors for telemetry
  const handleTopologyError = useCallback((error: Error) => {
    console.error('[Brain] 3D topology rendering failed:', error);
    // Could send to OTEL here
  }, []);

  const handleCapture = async () => {
    if (!captureContent.trim()) return;

    setLoading(true);
    setMessage(null);

    try {
      const response = await brainApi.capture({ content: captureContent });
      setCaptureContent('');

      // Refresh all data to show new content
      await refreshAfterCapture();

      setMessage({
        type: 'success',
        text: `Captured: ${response.data.concept_id}`,
      });

      // Foundation 5: Celebrate successful capture!
      celebrate({ intensity: 'subtle' });

      // Wave 4: Show synergy toast notification
      crystalFormed(response.data.concept_id);
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Failed to capture content',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGhostSurface = async () => {
    if (!ghostContext.trim()) return;

    setLoading(true);
    setMessage(null);

    try {
      const response = await brainApi.ghost({
        context: ghostContext,
        limit: 10,
      });
      setGhostResults(response.data.surfaced);
      if (response.data.count === 0) {
        setMessage({
          type: 'success',
          text: getEmptyState('noResults').description,
        });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Failed to surface memories',
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (s: string) => {
    switch (s) {
      case 'healthy':
        return 'text-green-400';
      case 'degraded':
        return 'text-yellow-400';
      default:
        return 'text-red-400';
    }
  };

  // ==========================================================================
  // Render: 3D Canvas
  // ==========================================================================

  // Determine what to show in the canvas area
  const renderCanvas = () => {
    // Initial loading state
    if (initialLoading) {
      return <TopologyLoading />;
    }

    // Connection error state
    if (connectionError) {
      return <ConnectionError error={connectionError} onRetry={loadAllData} />;
    }

    // Empty brain state (connected but no data)
    if (topology && topology.nodes.length === 0) {
      return <EmptyBrainState />;
    }

    // Normal 3D topology
    return (
      <ErrorBoundary
        key={topologyKey}
        fallback={<TopologyErrorFallback onRetry={handleTopologyRetry} />}
        onError={handleTopologyError}
        resetKeys={[topologyKey]}
      >
        <Suspense fallback={<TopologyLoading />}>
          <BrainTopology
            topology={topology}
            onNodeClick={handleNodeClick}
            showEdges={showEdges}
            showGaps={showGaps}
            showLabels={showLabels}
          />
        </Suspense>
      </ErrorBoundary>
    );
  };

  const canvas3D = renderCanvas();

  // ==========================================================================
  // Render: Stats Overlay
  // ==========================================================================

  const statsOverlay = status && (
    <div className={`absolute top-3 left-3 bg-gray-800/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow-lg ${isMobile ? 'text-[10px]' : 'text-xs'} text-gray-300`}>
      {/* Foundation 5: Breathe animation for healthy status */}
      <Breathe intensity={status.status === 'healthy' ? 0.3 : 0} speed="slow">
        <span className={`font-semibold ${getStatusColor(status.status)}`}>{status.status}</span>
      </Breathe>
      {!isMobile && (
        <>
          {' • '}
          <span className="text-cyan-400 font-semibold">{status.concept_count}</span> concepts
        </>
      )}
    </div>
  );

  // ==========================================================================
  // Render: Mobile Layout
  // ==========================================================================

  if (isMobile) {
    return (
      <div className="h-screen flex flex-col bg-gray-900 text-white overflow-hidden">
        {/* Compact header */}
        <header className="flex-shrink-0 border-b border-gray-800 px-3 py-2 bg-gray-900 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">🧠</span>
            <span className="font-semibold">Brain</span>
            {connectionError ? (
              <span className="text-xs text-red-400">⚠️</span>
            ) : status ? (
              <span className={`text-xs ${getStatusColor(status.status)}`}>
                {status.concept_count}
              </span>
            ) : null}
          </div>
          {/* Refresh button */}
          <button
            onClick={loadAllData}
            disabled={initialLoading}
            className="text-gray-500 hover:text-cyan-400 transition-colors disabled:opacity-50 p-1"
            title="Refresh"
          >
            <span className={`text-sm ${initialLoading ? 'animate-spin' : ''}`}>🔄</span>
          </button>
        </header>

        {/* Main content */}
        <div className="flex-1 relative">
          {viewMode === 'topology' ? (
            <>
              {canvas3D}
              {statsOverlay}
            </>
          ) : (
            <PanelsView
              status={status}
              map={map}
              captureContent={captureContent}
              setCaptureContent={setCaptureContent}
              ghostContext={ghostContext}
              setGhostContext={setGhostContext}
              ghostResults={ghostResults}
              onCapture={handleCapture}
              onGhostSurface={handleGhostSurface}
              loading={loading}
              getStatusColor={getStatusColor}
              density={density}
            />
          )}

          {/* Floating actions */}
          <FloatingActions
            actions={[
              {
                id: 'view',
                icon: viewMode === 'topology' ? '📊' : '🧠',
                label: viewMode === 'topology' ? 'Switch to panels' : 'Switch to 3D',
                onClick: () => setViewMode((v) => (v === 'topology' ? 'panels' : 'topology')),
                variant: 'primary',
              },
              {
                id: 'capture',
                icon: '✨',
                label: 'Capture & Ghost',
                onClick: () => setPanelState((s) => ({ ...s, capture: !s.capture })),
                isActive: panelState.capture,
              },
              {
                id: 'controls',
                icon: '⚙️',
                label: 'Toggle controls',
                onClick: () => setPanelState((s) => ({ ...s, controls: !s.controls })),
                isActive: panelState.controls,
              },
            ]}
            position="bottom-right"
          />
        </div>

        {/* Control drawer */}
        <BottomDrawer
          isOpen={panelState.controls}
          onClose={() => setPanelState((s) => ({ ...s, controls: false }))}
          title="Display Options"
        >
          <ControlPanel
            showEdges={showEdges}
            setShowEdges={setShowEdges}
            showGaps={showGaps}
            setShowGaps={setShowGaps}
            showLabels={showLabels}
            setShowLabels={setShowLabels}
            density={density}
            isDrawer
            observer={observer}
            setObserver={setObserver}
          />
        </BottomDrawer>

        {/* Capture drawer */}
        <BottomDrawer
          isOpen={panelState.capture}
          onClose={() => setPanelState((s) => ({ ...s, capture: false }))}
          title="Capture & Surface"
        >
          <CapturePanel
            captureContent={captureContent}
            setCaptureContent={setCaptureContent}
            ghostContext={ghostContext}
            setGhostContext={setGhostContext}
            ghostResults={ghostResults}
            onCapture={handleCapture}
            onGhostSurface={handleGhostSurface}
            loading={loading}
            density={density}
            isDrawer
          />
        </BottomDrawer>

        {/* Crystal Detail Modal - Wave 1: Hero Path Polish */}
        {selectedCrystal && (
          <CrystalDetail
            crystal={selectedCrystal}
            onClose={handleCloseCrystalDetail}
            observer={observer}
            onObserverChange={setObserver}
            variant="modal"
          />
        )}

        {/* Message Toast - Foundation 5: Pop animation */}
        {message && (
          <PopOnMount scale={1.05} duration={200}>
            <div
              className={`fixed bottom-20 right-4 px-4 py-2 rounded shadow-lg z-30 ${
                message.type === 'success' ? 'bg-green-600' : 'bg-red-600'
              }`}
            >
              {message.text}
            </div>
          </PopOnMount>
        )}
      </div>
    );
  }

  // ==========================================================================
  // Render: Tablet/Desktop Layout (ElasticSplit)
  // ==========================================================================

  // Build side panel content
  const sidePanel = (
    <div className="h-full flex flex-col bg-gray-800/50 border-l border-gray-700 overflow-y-auto">
      <ControlPanel
        showEdges={showEdges}
        setShowEdges={setShowEdges}
        showGaps={showGaps}
        setShowGaps={setShowGaps}
        showLabels={showLabels}
        setShowLabels={setShowLabels}
        density={density}
        observer={observer}
        setObserver={setObserver}
      />
      <div className="border-t border-gray-700">
        <CapturePanel
          captureContent={captureContent}
          setCaptureContent={setCaptureContent}
          ghostContext={ghostContext}
          setGhostContext={setGhostContext}
          ghostResults={ghostResults}
          onCapture={handleCapture}
          onGhostSurface={handleGhostSurface}
          loading={loading}
          density={density}
        />
      </div>
    </div>
  );

  return (
    <div className="h-screen flex flex-col bg-gray-900 text-white overflow-hidden">
      {/* Header */}
      <header className="flex-shrink-0 border-b border-gray-800 px-4 py-3 bg-gray-900">
        <div className="flex justify-between items-center">
          <div>
            <h1 className={`font-bold flex items-center gap-2 ${isTablet ? 'text-lg' : 'text-xl'}`}>
              <span>🧠</span>
              <span>Holographic Brain</span>
              {/* Refresh button */}
              <button
                onClick={loadAllData}
                disabled={initialLoading}
                className="text-gray-500 hover:text-cyan-400 transition-colors disabled:opacity-50"
                title="Refresh brain data"
              >
                <span className={`text-sm ${initialLoading ? 'animate-spin' : ''}`}>🔄</span>
              </button>
            </h1>
            <p className={`text-gray-400 mt-0.5 ${isTablet ? 'text-xs' : 'text-sm'}`}>
              {connectionError ? (
                <span className="text-red-400">⚠️ Not connected</span>
              ) : status ? (
                <>
                  <span className={getStatusColor(status.status)}>{status.status}</span>
                  {' • '}
                  <span className="text-cyan-400">{status.concept_count}</span> concepts
                  {' • '}
                  {status.embedder_type}
                </>
              ) : initialLoading ? (
                getLoadingMessage('brain')
              ) : (
                getLoadingMessage('brain')
              )}
            </p>
          </div>

          {/* View mode toggle */}
          <div className="flex bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setViewMode('topology')}
              className={`px-3 py-1 rounded transition-colors ${isTablet ? 'text-xs' : 'text-sm'} ${
                viewMode === 'topology'
                  ? 'bg-cyan-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {isDesktop ? '3D Topology' : '3D'}
            </button>
            <button
              onClick={() => setViewMode('panels')}
              className={`px-3 py-1 rounded transition-colors ${isTablet ? 'text-xs' : 'text-sm'} ${
                viewMode === 'panels'
                  ? 'bg-cyan-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Panels
            </button>
          </div>
        </div>
      </header>

      {/* Main content */}
      {viewMode === 'topology' ? (
        <div className="flex-1 overflow-hidden">
          <ElasticSplit
            direction="horizontal"
            defaultRatio={0.75}
            collapseAt={PANEL_COLLAPSE_BREAKPOINT}
            collapsePriority="secondary"
            minPaneSize={isTablet ? 200 : 280}
            resizable={isDesktop}
            primary={
              <div className="h-full relative">
                {canvas3D}
                {statsOverlay}
                {/* Hints overlay - desktop only */}
                {isDesktop && (
                  <div className="absolute bottom-3 left-3 bg-gray-800/90 backdrop-blur-sm rounded-lg px-3 py-2 text-xs text-gray-500 shadow-lg">
                    Drag to rotate • Scroll to zoom • Click crystal for details
                  </div>
                )}
              </div>
            }
            secondary={sidePanel}
          />
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto">
          <PanelsView
            status={status}
            map={map}
            captureContent={captureContent}
            setCaptureContent={setCaptureContent}
            ghostContext={ghostContext}
            setGhostContext={setGhostContext}
            ghostResults={ghostResults}
            onCapture={handleCapture}
            onGhostSurface={handleGhostSurface}
            loading={loading}
            getStatusColor={getStatusColor}
            density={density}
          />
        </div>
      )}

      {/* Crystal Detail Modal - Wave 1: Hero Path Polish */}
      {selectedCrystal && (
        <CrystalDetail
          crystal={selectedCrystal}
          onClose={handleCloseCrystalDetail}
          observer={observer}
          onObserverChange={setObserver}
          variant="modal"
        />
      )}

      {/* Message Toast - Foundation 5: Pop animation */}
      {message && (
        <PopOnMount scale={1.05} duration={200}>
          <div
            className={`fixed bottom-4 right-4 px-4 py-2 rounded shadow-lg z-50 ${
              message.type === 'success' ? 'bg-green-600' : 'bg-red-600'
            }`}
          >
            {message.text}
          </div>
        </PopOnMount>
      )}
    </div>
  );
}

// =============================================================================
// Panels View - Density-aware
// =============================================================================

interface PanelsViewProps {
  status: BrainStatusResponse | null;
  map: BrainMapResponse | null;
  captureContent: string;
  setCaptureContent: (v: string) => void;
  ghostContext: string;
  setGhostContext: (v: string) => void;
  ghostResults: GhostMemory[];
  onCapture: () => void;
  onGhostSurface: () => void;
  loading: boolean;
  getStatusColor: (s: string) => string;
  density: Density;
}

function PanelsView({
  status,
  map,
  captureContent,
  setCaptureContent,
  ghostContext,
  setGhostContext,
  ghostResults,
  onCapture,
  onGhostSurface,
  loading,
  getStatusColor,
  density,
}: PanelsViewProps) {
  const isCompact = density === 'compact';
  const maxResults = MAX_GHOST_RESULTS[density];

  return (
    <div className={`${isCompact ? 'p-3' : 'max-w-4xl mx-auto p-6'}`}>
      {/* Status Panel */}
      <div className={`bg-gray-800 rounded-lg ${isCompact ? 'p-3 mb-3' : 'p-4 mb-6'}`}>
        <h2 className={`font-semibold ${isCompact ? 'text-sm mb-2' : 'text-lg mb-3'}`}>Brain Status</h2>
        {status ? (
          <div className={`grid ${isCompact ? 'grid-cols-2 gap-2 text-xs' : 'grid-cols-2 md:grid-cols-4 gap-4 text-sm'}`}>
            <div>
              <span className="text-gray-400">Status:</span>
              <span className={`ml-2 ${getStatusColor(status.status)}`}>{status.status}</span>
            </div>
            <div>
              <span className="text-gray-400">Concepts:</span>
              <span className="ml-2">{status.concept_count}</span>
            </div>
            {!isCompact && (
              <>
                <div>
                  <span className="text-gray-400">Embedder:</span>
                  <span className="ml-2">{status.embedder_type}</span>
                </div>
                <div>
                  <span className="text-gray-400">Dimension:</span>
                  <span className="ml-2">{status.embedder_dimension}</span>
                </div>
              </>
            )}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">Loading status...</p>
        )}
      </div>

      {/* Topology Stats Panel */}
      <div className={`bg-gray-800 rounded-lg ${isCompact ? 'p-3 mb-3' : 'p-4 mb-6'}`}>
        <h2 className={`font-semibold ${isCompact ? 'text-sm mb-2' : 'text-lg mb-3'}`}>Memory Topology</h2>
        {map ? (
          <div className={`grid ${isCompact ? 'grid-cols-2 gap-2 text-xs' : 'grid-cols-2 md:grid-cols-4 gap-4 text-sm'}`}>
            <div>
              <span className="text-gray-400">Concepts:</span>
              <span className="ml-2">{map.concept_count}</span>
            </div>
            <div>
              <span className="text-gray-400">Hot:</span>
              <span className="ml-2 text-orange-400">{map.hot_patterns}</span>
            </div>
            {!isCompact && (
              <>
                <div>
                  <span className="text-gray-400">Landmarks:</span>
                  <span className="ml-2">{map.landmarks}</span>
                </div>
                <div>
                  <span className="text-gray-400">Dimension:</span>
                  <span className="ml-2">{map.dimension}</span>
                </div>
              </>
            )}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">Loading topology...</p>
        )}
      </div>

      {/* Capture Panel */}
      <div className={`bg-gray-800 rounded-lg ${isCompact ? 'p-3 mb-3' : 'p-4 mb-6'}`}>
        <h2 className={`font-semibold ${isCompact ? 'text-sm mb-2' : 'text-lg mb-3'}`}>Capture Content</h2>
        <div className={isCompact ? 'space-y-2' : 'flex gap-3'}>
          <textarea
            value={captureContent}
            onChange={(e) => setCaptureContent(e.target.value)}
            placeholder="Enter content to capture to memory..."
            className={`${isCompact ? 'w-full' : 'flex-1'} bg-gray-700 rounded px-3 py-2 text-white placeholder-gray-500 resize-none ${isCompact ? 'text-xs' : ''}`}
            rows={isCompact ? 2 : 3}
          />
          <button
            onClick={onCapture}
            disabled={loading || !captureContent.trim()}
            className={`${isCompact ? 'w-full' : ''} px-4 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-gray-600 rounded font-medium transition-colors ${isCompact ? 'text-xs' : ''}`}
          >
            {loading ? 'Capturing...' : 'Capture'}
          </button>
        </div>
      </div>

      {/* Ghost Surface Panel */}
      <div className={`bg-gray-800 rounded-lg ${isCompact ? 'p-3' : 'p-4'}`}>
        <h2 className={`font-semibold ${isCompact ? 'text-sm mb-2' : 'text-lg mb-3'}`}>Ghost Surfacing</h2>
        <div className={`flex gap-2 ${isCompact ? 'mb-2' : 'mb-4'}`}>
          <input
            type="text"
            value={ghostContext}
            onChange={(e) => setGhostContext(e.target.value)}
            placeholder={isCompact ? 'Context...' : 'Enter context to surface related memories...'}
            className={`flex-1 bg-gray-700 rounded px-3 py-2 text-white placeholder-gray-500 ${isCompact ? 'text-xs' : ''}`}
            onKeyDown={(e) => e.key === 'Enter' && onGhostSurface()}
          />
          <button
            onClick={onGhostSurface}
            disabled={loading || !ghostContext.trim()}
            className={`px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded font-medium transition-colors ${isCompact ? 'text-xs' : ''}`}
          >
            {loading ? '...' : 'Surface'}
          </button>
        </div>

        {/* Ghost Results */}
        {ghostResults.length > 0 && (
          <div className="space-y-2">
            <h3 className={`text-gray-400 mb-2 ${isCompact ? 'text-[10px]' : 'text-sm'}`}>
              Surfaced Memories ({ghostResults.length})
            </h3>
            {ghostResults.slice(0, maxResults).map((memory) => (
              <div
                key={memory.concept_id}
                className={`bg-gray-700 rounded p-2 border-l-2 border-purple-500 ${isCompact ? 'text-[10px]' : ''}`}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className={`text-gray-400 font-mono ${isCompact ? '' : 'text-xs'}`}>{memory.concept_id}</span>
                  <span className={`px-1.5 py-0.5 bg-purple-900 rounded ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
                    {(memory.relevance * 100).toFixed(0)}%
                  </span>
                </div>
                <p className={`${isCompact ? 'line-clamp-1' : 'text-sm'}`}>
                  {memory.content || <span className="text-gray-500 italic">{getEmptyState('noData').title}</span>}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
