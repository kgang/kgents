/**
 * useGestaltStream - SSE streaming hook for live architecture updates.
 *
 * Sprint 1: Basic streaming with connection management.
 *
 * Provides:
 * - Connection management with automatic reconnection
 * - Status indicator state (live/connecting/offline)
 * - Debounced updates to prevent UI thrashing
 *
 * @see plans/_continuations/gestalt-to-100.md
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { gestaltApi } from '../api/client';
import type {
  CodebaseTopologyResponse,
  CodebaseTopologyUpdate,
  GestaltStreamStatus,
} from '../api/types';

/** Configuration for the stream hook */
export interface UseGestaltStreamOptions {
  /** Whether to enable streaming (default: true) */
  enabled?: boolean;
  /** Maximum nodes to return (default: 200) */
  maxNodes?: number;
  /** Minimum health filter (default: 0.0) */
  minHealth?: number;
  /** Server poll interval in seconds (default: 5.0) */
  pollInterval?: number;
  /** Reconnection delay in ms (default: 3000) */
  reconnectDelay?: number;
  /** Debounce interval for updates in ms (default: 100) */
  debounceMs?: number;
}

/** Return type of the hook */
export interface UseGestaltStreamReturn {
  /** Current topology state */
  topology: CodebaseTopologyResponse | null;
  /** Connection status */
  status: GestaltStreamStatus;
  /** Whether currently connected */
  isConnected: boolean;
  /** Whether currently live (receiving updates) */
  isLive: boolean;
  /** Last update timestamp */
  lastUpdate: Date | null;
  /** Manually reconnect */
  reconnect: () => void;
  /** Manually disconnect */
  disconnect: () => void;
  /** Error message if any */
  error: string | null;
}

/**
 * Hook for streaming architecture topology updates.
 *
 * Handles:
 * - Initial topology fetch (fallback)
 * - SSE streaming with full updates
 * - Automatic reconnection with backoff
 * - Debouncing rapid updates
 */
export function useGestaltStream(
  initialTopology?: CodebaseTopologyResponse | null,
  options: UseGestaltStreamOptions = {}
): UseGestaltStreamReturn {
  const {
    enabled = true,
    maxNodes = 200,
    minHealth = 0.0,
    pollInterval = 5.0,
    reconnectDelay = 3000,
    debounceMs = 100,
  } = options;

  // State
  const [topology, setTopology] = useState<CodebaseTopologyResponse | null>(
    initialTopology || null
  );
  const [status, setStatus] = useState<GestaltStreamStatus>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Refs for cleanup and debouncing
  const streamRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const debounceTimeoutRef = useRef<number | null>(null);
  const pendingTopologyRef = useRef<CodebaseTopologyResponse | null>(null);
  const mountedRef = useRef(true);

  // Apply debounced topology update
  const applyPendingTopology = useCallback(() => {
    if (!mountedRef.current) return;

    const pending = pendingTopologyRef.current;
    if (!pending) return;

    pendingTopologyRef.current = null;
    setTopology(pending);
    setLastUpdate(new Date());
  }, []);

  // Queue a topology update with debouncing
  const queueTopologyUpdate = useCallback(
    (newTopology: CodebaseTopologyResponse) => {
      pendingTopologyRef.current = newTopology;

      // Clear existing debounce timer
      if (debounceTimeoutRef.current !== null) {
        window.clearTimeout(debounceTimeoutRef.current);
      }

      // Set new debounce timer
      debounceTimeoutRef.current = window.setTimeout(() => {
        applyPendingTopology();
        debounceTimeoutRef.current = null;
      }, debounceMs);
    },
    [applyPendingTopology, debounceMs]
  );

  // Connect to topology stream
  const connect = useCallback(() => {
    if (!enabled || !mountedRef.current) return;

    // Close existing
    if (streamRef.current) {
      streamRef.current.close();
    }

    setStatus('connecting');
    setError(null);

    try {
      const source = gestaltApi.createTopologyStream({
        maxNodes,
        minHealth,
        pollInterval,
      });
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
          const update = JSON.parse(event.data) as CodebaseTopologyUpdate;

          // Handle error messages from server
          if (update.kind === 'error' && update.error) {
            setError(update.error);
            return;
          }

          // Handle full topology update
          if (update.kind === 'full' && update.topology) {
            queueTopologyUpdate(update.topology);
          }

          // Handle ping (just update timestamp, topology unchanged)
          if (update.kind === 'ping') {
            // Ping indicates we're still connected but no changes
            // Optionally track last ping time
          }

        } catch (e) {
          console.error('Failed to parse topology update:', e);
        }
      };

      source.onerror = () => {
        if (!mountedRef.current) return;

        console.error('Gestalt stream error, reconnecting...');
        setStatus('reconnecting');

        // Close and reconnect
        source.close();
        streamRef.current = null;

        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, reconnectDelay);
      };
    } catch (e) {
      console.error('Failed to create topology stream:', e);
      setStatus('error');
      setError('Failed to connect to architecture stream');
    }
  }, [enabled, maxNodes, minHealth, pollInterval, queueTopologyUpdate, reconnectDelay]);

  // Manual reconnect
  const reconnect = useCallback(() => {
    // Clear any pending reconnect
    if (reconnectTimeoutRef.current !== null) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    connect();
  }, [connect]);

  // Manual disconnect
  const disconnect = useCallback(() => {
    // Clear reconnect timer
    if (reconnectTimeoutRef.current !== null) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Close stream
    if (streamRef.current) {
      streamRef.current.close();
      streamRef.current = null;
    }

    setStatus('disconnected');
  }, []);

  // Initial connection
  useEffect(() => {
    mountedRef.current = true;

    // Connect after a short delay to allow initial topology to load
    const timer = setTimeout(() => {
      connect();
    }, 500);

    return () => {
      mountedRef.current = false;
      clearTimeout(timer);
      disconnect();

      // Clear debounce timer
      if (debounceTimeoutRef.current !== null) {
        window.clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, [connect, disconnect]);

  // Reconnect when options change
  useEffect(() => {
    if (enabled && status === 'connected') {
      // Reconnect with new options
      reconnect();
    }
  }, [maxNodes, minHealth, pollInterval]); // Don't include enabled/status to avoid loops

  return {
    topology,
    status,
    isConnected: status === 'connected',
    isLive: status === 'connected' && topology !== null,
    lastUpdate,
    reconnect,
    disconnect,
    error,
  };
}

export default useGestaltStream;
