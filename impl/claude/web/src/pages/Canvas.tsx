/**
 * Canvas Page - Collaborative AGENTESE Mind Map.
 *
 * CLI v7 Phase 5: Integration & Polish.
 *
 * This page brings together:
 * - AgentCanvas: Visual mind-map of AGENTESE nodes
 * - PresenceChannel: Real-time agent cursor streaming via SSE
 * - AGENTESE Discovery: Live node data from the backend
 *
 * Voice Anchor:
 * "Agents pretending to be there with their cursors moving,
 *  kinda following my cursor, kinda doing its own thing."
 *
 * Design Philosophy:
 * - Tasteful: Clean visualization that doesn't overwhelm
 * - Joy-Inducing: Animated cursors that feel alive
 * - Composable: Can navigate to any AGENTESE path
 *
 * @see protocols/agentese/presence.py - PresenceChannel source of truth
 * @see plans/cli-v7-implementation.md Phase 4-5
 */

import { useState, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Compass, RefreshCw, Users, Maximize2, Minimize2, Eye, Play, Square, Sun, BookOpen } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { AgentCanvas, PresenceStatusBadge, CursorList, NodeDetailPanel } from '@/components/canvas';
import type { CanvasNode } from '@/components/canvas';
import { useCanvasNodes, usePresenceChannel, useUserFocus, useCircadian } from '@/hooks';
import { useDesignPolynomial } from '@/hooks';
import { useAgenteseMutation } from '@/hooks/useAgentesePath';

// =============================================================================
// Component
// =============================================================================

// Demo mode response type
interface DemoResponse {
  success: boolean;
  action: string;
  message: string;
  agent_ids: string[];
}

export function Canvas() {
  const navigate = useNavigate();
  const { state: designState } = useDesignPolynomial();
  const { density } = designState;

  // Canvas nodes from AGENTESE discovery
  const { nodes, loading, error, toggleExpanded, refetch, stats } = useCanvasNodes({
    maxDepth: 3,
    initialExpanded: new Set(['self', 'world']),
    radius: density === 'compact' ? 200 : density === 'comfortable' ? 250 : 300,
  });

  // Presence channel for agent cursors
  const { cursorList, isConnected, status, latestCursor, reconnect } = usePresenceChannel({
    autoConnect: true,
    reconnectDelay: 3000,
    maxReconnectAttempts: 5,
  });

  // Circadian warmth (Pattern #11: time-of-day modulation)
  const { data: circadian, backgroundStyle: circadianBackground } = useCircadian();

  // Demo mode mutation
  const { mutate: toggleDemo, isLoading: demoLoading } = useAgenteseMutation<
    { action: string; agent_count?: number },
    DemoResponse
  >('self.presence:demo');

  // UI state
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [detailNode, setDetailNode] = useState<CanvasNode | null>(null);
  const [showPresencePanel, setShowPresencePanel] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [trackingEnabled, setTrackingEnabled] = useState(true);
  const [demoActive, setDemoActive] = useState(false);
  const [teachingMode, setTeachingMode] = useState(false);

  // User focus tracking for agent cursor following
  const { focusPath, isHovering, idleTime } = useUserFocus({
    nodes,
    enabled: trackingEnabled,
    focusThreshold: 80,
    debounceDelay: 150,
    onFocusChange: (path) => {
      // When user focus changes, we could broadcast to backend
      // for agent cursors to follow. For now, just update selection.
      if (path) {
        setSelectedNode(path);
      }
    },
  });

  // Memoized user focus indicator
  const userFocusIndicator = useMemo(() => {
    if (!trackingEnabled) return null;
    if (!isHovering) return 'Not tracking';
    if (focusPath) return `Focusing: ${focusPath}`;
    if (idleTime > 3000) return 'Idle';
    return 'Exploring...';
  }, [trackingEnabled, isHovering, focusPath, idleTime]);

  // Handle node click - select and open detail panel
  const handleNodeClick = useCallback((node: CanvasNode) => {
    setSelectedNode(node.id);
    setDetailNode(node);
  }, []);

  // Close detail panel
  const handleCloseDetail = useCallback(() => {
    setDetailNode(null);
  }, []);

  // Invoke an aspect from the detail panel
  const handleInvokeAspect = useCallback((path: string, aspect: string) => {
    console.log(`[Canvas] Invoking ${path}:${aspect}`);
    // Navigate directly to AGENTESE path - "The URL IS the AGENTESE path"
    const url = aspect === 'manifest' ? `/${path}` : `/${path}:${aspect}`;
    navigate(url);
  }, [navigate]);

  // Handle node navigation (double-click)
  const handleNodeNavigate = useCallback(
    (path: string) => {
      // Navigate directly to AGENTESE path - "The URL IS the AGENTESE path"
      navigate(`/${path}`);
    },
    [navigate]
  );

  // Handle node expand/collapse
  const handleNodeToggle = useCallback(
    (node: { id: string }) => {
      toggleExpanded(node.id);
    },
    [toggleExpanded]
  );

  // Toggle fullscreen
  const toggleFullscreen = useCallback(() => {
    setIsFullscreen((prev) => !prev);
  }, []);

  // Toggle demo mode - spawn/remove demo agent cursors
  const handleDemoToggle = useCallback(async () => {
    const action = demoActive ? 'stop' : 'start';
    console.log('[Canvas] Toggling demo mode:', action);
    try {
      const result = await toggleDemo({ action, agent_count: 2 });
      console.log('[Canvas] Demo toggle result:', result);
      if (result?.success) {
        setDemoActive(action === 'start');
        // Force reconnect to SSE stream to pick up new cursors immediately
        reconnect();
      }
    } catch (e) {
      console.error('[Canvas] Demo toggle error:', e);
    }
  }, [demoActive, toggleDemo, reconnect]);

  // Render loading state
  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center">
          <RefreshCw className="w-8 h-8 text-blue-400 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Discovering AGENTESE paths...</p>
        </motion.div>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900">
        <div className="text-center max-w-md p-6">
          <div className="text-4xl mb-4">🌐</div>
          <h2 className="text-xl font-semibold text-white mb-2">Discovery Failed</h2>
          <p className="text-gray-400 mb-4">{error}</p>
          <button
            onClick={refetch}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-white transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`h-full flex flex-col ${isFullscreen ? 'fixed inset-0 z-50' : ''}`}
      style={circadianBackground}
    >
      {/* Header */}
      <header className="flex-shrink-0 flex items-center justify-between px-4 py-3 border-b border-gray-800 bg-gray-900/80 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <Compass className="w-5 h-5 text-blue-400" />
          <h1 className="text-lg font-medium text-white">AGENTESE Canvas</h1>
          {stats && (
            <span className="text-xs text-gray-500">
              {stats.total_paths} paths • {stats.contexts.length} contexts
            </span>
          )}
          {/* Circadian phase indicator */}
          {circadian && (
            <span
              className="text-xs text-gray-600 flex items-center gap-1"
              title={`Warmth: ${(circadian.warmth * 100).toFixed(0)}%`}
            >
              <Sun className="w-3 h-3" style={{ opacity: 0.5 + circadian.warmth * 0.5 }} />
              {circadian.phase.toLowerCase()}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Presence status */}
          <PresenceStatusBadge
            cursorCount={cursorList.length}
            isConnected={isConnected}
            className="mr-2"
          />

          {/* Demo mode toggle - spawn virtual agent cursors */}
          <button
            onClick={handleDemoToggle}
            disabled={demoLoading}
            className={`
              p-2 rounded-lg transition-colors flex items-center gap-1.5
              ${demoActive ? 'bg-green-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-white'}
              ${demoLoading ? 'opacity-50 cursor-wait' : ''}
            `}
            title={demoActive ? 'Stop demo agents' : 'Start demo agents'}
          >
            {demoActive ? <Square className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            <span className="text-xs hidden sm:inline">
              {demoLoading ? '...' : demoActive ? 'Stop' : 'Demo'}
            </span>
          </button>

          {/* Toggle focus tracking */}
          <button
            onClick={() => setTrackingEnabled((t) => !t)}
            className={`
              p-2 rounded-lg transition-colors
              ${trackingEnabled ? 'bg-cyan-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-white'}
            `}
            title={trackingEnabled ? 'Disable focus tracking' : 'Enable focus tracking'}
          >
            <Eye className="w-4 h-4" />
          </button>

          {/* Toggle presence panel */}
          <button
            onClick={() => setShowPresencePanel((p) => !p)}
            className={`
              p-2 rounded-lg transition-colors
              ${showPresencePanel ? 'bg-violet-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-white'}
            `}
            title={showPresencePanel ? 'Hide agents' : 'Show agents'}
          >
            <Users className="w-4 h-4" />
          </button>

          {/* Toggle teaching mode */}
          <button
            onClick={() => setTeachingMode((t) => !t)}
            className={`
              p-2 rounded-lg transition-colors
              ${teachingMode ? 'bg-amber-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-white'}
            `}
            title={teachingMode ? 'Disable teaching mode' : 'Enable teaching mode'}
          >
            <BookOpen className="w-4 h-4" />
          </button>

          {/* Refresh */}
          <button
            onClick={refetch}
            className="p-2 rounded-lg bg-gray-800 text-gray-400 hover:text-white transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          {/* Fullscreen toggle */}
          <button
            onClick={toggleFullscreen}
            className="p-2 rounded-lg bg-gray-800 text-gray-400 hover:text-white transition-colors"
            title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Canvas */}
        <div className="flex-1 relative">
          <AgentCanvas
            nodes={nodes}
            cursors={cursorList}
            selectedNode={selectedNode}
            onNodeClick={handleNodeClick}
            onNodeNavigate={handleNodeNavigate}
            onNodeToggle={handleNodeToggle}
            showConnections={true}
            enablePan={true}
            enableZoom={true}
            circadianTempo={circadian?.tempo_modifier ?? 1.0}
            className="w-full h-full"
          />

          {/* Empty state overlay */}
          {nodes.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="text-center">
                <div className="text-4xl mb-4">🌐</div>
                <p className="text-gray-400">No nodes discovered</p>
                <p className="text-xs text-gray-600 mt-1">
                  Start the backend to explore AGENTESE paths
                </p>
              </div>
            </div>
          )}

          {/* User focus indicator */}
          {trackingEnabled && userFocusIndicator && (
            <div className="absolute top-4 left-4 bg-gray-800/80 border border-gray-700 rounded-lg px-3 py-1.5 text-xs text-gray-400">
              <Eye className="w-3 h-3 inline-block mr-1.5 text-cyan-400" />
              {userFocusIndicator}
            </div>
          )}

          {/* Latest cursor activity (toast-like) */}
          {latestCursor && latestCursor.state !== 'waiting' && (
            <motion.div
              key={latestCursor.cursor_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="absolute bottom-4 left-4 bg-gray-800/90 border border-gray-700 rounded-lg px-3 py-2 text-sm"
            >
              <span className="text-gray-400">{latestCursor.display_name}</span>
              <span className="text-gray-500 mx-1">is</span>
              <span className="text-white">{latestCursor.state}</span>
              {latestCursor.focus_path && (
                <>
                  <span className="text-gray-500 mx-1">at</span>
                  <code className="text-blue-400">{latestCursor.focus_path}</code>
                </>
              )}
            </motion.div>
          )}
        </div>

        {/* Presence panel (sidebar) */}
        {showPresencePanel && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="flex-shrink-0 border-l border-gray-800 bg-gray-900/50 overflow-y-auto"
          >
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-medium text-gray-300">Agent Presence</h2>
                {status !== 'connected' && (
                  <button onClick={reconnect} className="text-xs text-blue-400 hover:text-blue-300">
                    Reconnect
                  </button>
                )}
              </div>

              {/* Connection status */}
              <div className="mb-4 text-xs">
                <span
                  className={`
                  inline-flex items-center gap-1.5 px-2 py-1 rounded-full
                  ${
                    status === 'connected'
                      ? 'bg-green-900/30 text-green-400'
                      : status === 'connecting' || status === 'reconnecting'
                        ? 'bg-yellow-900/30 text-yellow-400'
                        : 'bg-red-900/30 text-red-400'
                  }
                `}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      status === 'connected'
                        ? 'bg-green-400'
                        : status === 'connecting' || status === 'reconnecting'
                          ? 'bg-yellow-400 animate-pulse'
                          : 'bg-red-400'
                    }`}
                  />
                  {status}
                </span>
              </div>

              {/* Cursor list */}
              <CursorList
                cursors={cursorList}
                onCursorClick={(cursor) => {
                  if (cursor.focus_path) {
                    setSelectedNode(cursor.focus_path);
                  }
                }}
              />

              {/* Hint when no cursors */}
              {cursorList.length === 0 && isConnected && (
                <p className="text-xs text-gray-600 mt-4">
                  Agent cursors will appear here when they're active.
                  <br />
                  <button
                    onClick={handleDemoToggle}
                    className="text-blue-400 hover:text-blue-300 underline mt-1"
                  >
                    Start demo agents
                  </button>{' '}
                  to see the coworking feel.
                </p>
              )}
            </div>
          </motion.aside>
        )}
      </div>

      {/* Node detail panel (slides in from right when node clicked) */}
      <NodeDetailPanel
        node={detailNode}
        onClose={handleCloseDetail}
        onInvoke={handleInvokeAspect}
        teachingMode={teachingMode}
      />
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default Canvas;
