/**
 * useSceneGraph - SSE streaming hook for live SceneGraph updates.
 *
 * WARP Phase 2: React Projection Layer.
 *
 * Provides:
 * - Real-time SceneGraph streaming via SSE
 * - Connection management with automatic reconnection
 * - Graph state management (nodes, edges, layout)
 * - Fallback to REST polling if SSE fails
 *
 * @example
 * const { graph, nodes, edges, status } = useSceneGraph({
 *   pollInterval: 2.0,
 * });
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import type {
  SceneGraph,
  SceneNode,
  SceneEdge,
  WorldSceneryStreamEvent,
} from '../api/types/_generated/world-scenery';

// =============================================================================
// Types
// =============================================================================

export type SceneGraphStatus =
  | 'disconnected'
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'error';

export interface UseSceneGraphOptions {
  /** Whether to enable streaming (default: true) */
  enabled?: boolean;
  /** Polling interval in seconds (default: 1.0) */
  pollInterval?: number;
  /** Maximum events to receive (0 = unlimited) */
  maxEvents?: number;
  /** Reconnection delay in ms (default: 3000) */
  reconnectDelay?: number;
  /** Use REST polling instead of SSE (default: false) */
  usePolling?: boolean;
}

export interface UseSceneGraphReturn {
  /** Current scene graph */
  graph: SceneGraph | null;
  /** All nodes in the graph */
  nodes: SceneNode[];
  /** All edges in the graph */
  edges: SceneEdge[];
  /** Connection status */
  status: SceneGraphStatus;
  /** Whether currently connected and receiving */
  isConnected: boolean;
  /** Last update timestamp */
  lastUpdate: Date | null;
  /** Event count received */
  eventCount: number;
  /** Error message if any */
  error: string | null;
  /** Manually reconnect */
  reconnect: () => void;
  /** Manually disconnect */
  disconnect: () => void;
  /** Fetch latest graph (for polling mode) */
  refresh: () => Promise<void>;
}

// =============================================================================
// Hook Implementation
// =============================================================================

const API_BASE = import.meta.env.VITE_API_URL || '';

export function useSceneGraph(options: UseSceneGraphOptions = {}): UseSceneGraphReturn {
  const {
    enabled = true,
    pollInterval = 1.0,
    maxEvents = 0,
    reconnectDelay = 3000,
    usePolling = false,
  } = options;

  // State
  const [graph, setGraph] = useState<SceneGraph | null>(null);
  const [status, setStatus] = useState<SceneGraphStatus>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [eventCount, setEventCount] = useState(0);

  // Refs for cleanup
  const streamRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const pollingTimeoutRef = useRef<number | null>(null);
  const mountedRef = useRef(true);

  // Derived state
  const nodes = useMemo(() => graph?.nodes ?? [], [graph]);
  const edges = useMemo(() => graph?.edges ?? [], [graph]);
  const isConnected = status === 'connected';

  // ==========================================================================
  // SSE Streaming
  // ==========================================================================

  const buildStreamEndpoint = useCallback(() => {
    const params = new URLSearchParams();
    params.set('poll_interval', String(pollInterval));
    if (maxEvents > 0) {
      params.set('max_events', String(maxEvents));
    }
    return `${API_BASE}/agentese/world/scenery/stream?${params.toString()}`;
  }, [pollInterval, maxEvents]);

  const handleStreamEvent = useCallback((data: WorldSceneryStreamEvent) => {
    if (!mountedRef.current) return;

    if (data.type === 'scene' && data.graph) {
      setGraph(data.graph);
      setEventCount(data.event_count);
      setLastUpdate(new Date());
    }
  }, []);

  const connectStream = useCallback(() => {
    if (!enabled || !mountedRef.current || usePolling) return;

    // Close existing
    if (streamRef.current) {
      streamRef.current.close();
    }

    setStatus('connecting');
    setError(null);

    try {
      const endpoint = buildStreamEndpoint();
      const source = new EventSource(endpoint);
      streamRef.current = source;

      source.onopen = () => {
        if (mountedRef.current) {
          setStatus('connected');
          setError(null);
        }
      };

      source.onmessage = (event) => {
        if (!mountedRef.current) return;

        try {
          const data = JSON.parse(event.data);

          // Handle error responses
          if (data.error) {
            setError(data.error);
            return;
          }

          // Handle scene event
          handleStreamEvent(data as WorldSceneryStreamEvent);
        } catch (e) {
          console.error('[useSceneGraph] Failed to parse event:', e);
        }
      };

      source.onerror = () => {
        if (!mountedRef.current) return;

        console.warn('[useSceneGraph] Stream error, reconnecting...');
        setStatus('reconnecting');

        source.close();
        streamRef.current = null;

        reconnectTimeoutRef.current = window.setTimeout(() => {
          connectStream();
        }, reconnectDelay);
      };
    } catch (e) {
      console.error('[useSceneGraph] Failed to create stream:', e);
      setStatus('error');
      setError('Failed to connect to scene stream');
    }
  }, [enabled, usePolling, buildStreamEndpoint, handleStreamEvent, reconnectDelay]);

  // ==========================================================================
  // REST Polling
  // ==========================================================================

  const fetchManifest = useCallback(async () => {
    if (!enabled || !mountedRef.current) return;

    try {
      const response = await fetch(`${API_BASE}/agentese/world/scenery/manifest`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      if (mountedRef.current && data.result?.scene) {
        setGraph(data.result.scene);
        setLastUpdate(new Date());
        setStatus('connected');
      }
    } catch (e) {
      console.error('[useSceneGraph] Fetch error:', e);
      setError(e instanceof Error ? e.message : 'Fetch failed');
      setStatus('error');
    }
  }, [enabled]);

  const startPolling = useCallback(() => {
    if (!enabled || !mountedRef.current || !usePolling) return;

    setStatus('connecting');

    const poll = async () => {
      await fetchManifest();

      if (mountedRef.current && usePolling) {
        pollingTimeoutRef.current = window.setTimeout(poll, pollInterval * 1000);
      }
    };

    poll();
  }, [enabled, usePolling, pollInterval, fetchManifest]);

  // ==========================================================================
  // Control Functions
  // ==========================================================================

  const reconnect = useCallback(() => {
    // Clear timeouts
    if (reconnectTimeoutRef.current !== null) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (pollingTimeoutRef.current !== null) {
      window.clearTimeout(pollingTimeoutRef.current);
      pollingTimeoutRef.current = null;
    }

    if (usePolling) {
      startPolling();
    } else {
      connectStream();
    }
  }, [usePolling, startPolling, connectStream]);

  const disconnect = useCallback(() => {
    // Clear timeouts
    if (reconnectTimeoutRef.current !== null) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (pollingTimeoutRef.current !== null) {
      window.clearTimeout(pollingTimeoutRef.current);
      pollingTimeoutRef.current = null;
    }

    // Close stream
    if (streamRef.current) {
      streamRef.current.close();
      streamRef.current = null;
    }

    setStatus('disconnected');
  }, []);

  const refresh = useCallback(async () => {
    await fetchManifest();
  }, [fetchManifest]);

  // ==========================================================================
  // Lifecycle
  // ==========================================================================

  useEffect(() => {
    mountedRef.current = true;

    // Delay initial connection to allow component mount
    const timer = setTimeout(() => {
      if (usePolling) {
        startPolling();
      } else {
        connectStream();
      }
    }, 500);

    return () => {
      mountedRef.current = false;
      clearTimeout(timer);
      disconnect();
    };
  }, [usePolling, startPolling, connectStream, disconnect]);

  // Reconnect when options change
  useEffect(() => {
    if (enabled && status === 'connected') {
      reconnect();
    }
  }, [pollInterval, maxEvents]);

  return {
    graph,
    nodes,
    edges,
    status,
    isConnected,
    lastUpdate,
    eventCount,
    error,
    reconnect,
    disconnect,
    refresh,
  };
}

export default useSceneGraph;
