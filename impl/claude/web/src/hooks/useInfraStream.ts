/**
 * useInfraStream - SSE streaming hook for live infrastructure updates.
 *
 * Provides:
 * - Connection management with automatic reconnection
 * - Status indicator state
 * - Debounced updates to prevent UI thrashing
 *
 * @see plans/_continuations/gestalt-live-infra-phase2.md
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { infraApi } from '../api/client';
import type {
  TopologyUpdate,
  InfraTopologyResponse,
  InfraEvent,
  StreamConnectionStatus,
} from '../api/types';
import { applyTopologyUpdate } from '../utils/topologyDiff';

/** Configuration for the stream hook */
interface UseInfraStreamOptions {
  /** Whether to enable topology streaming (default: true) */
  enableTopology?: boolean;
  /** Whether to enable event streaming (default: true) */
  enableEvents?: boolean;
  /** Reconnection delay in ms (default: 3000) */
  reconnectDelay?: number;
  /** Maximum events to keep (default: 100) */
  maxEvents?: number;
  /** Debounce interval for updates in ms (default: 100) */
  debounceMs?: number;
}

/** Return type of the hook */
interface UseInfraStreamReturn {
  /** Current topology state */
  topology: InfraTopologyResponse | null;
  /** Recent events */
  events: InfraEvent[];
  /** Connection status */
  status: StreamConnectionStatus;
  /** Whether currently connected */
  isConnected: boolean;
  /** Manually reconnect */
  reconnect: () => void;
  /** Manually disconnect */
  disconnect: () => void;
  /** Error message if any */
  error: string | null;
}

/**
 * Hook for streaming infrastructure topology and events.
 *
 * Handles:
 * - Initial topology fetch
 * - SSE streaming with incremental updates
 * - Automatic reconnection with backoff
 * - Debouncing rapid updates
 */
export function useInfraStream(
  initialTopology?: InfraTopologyResponse | null,
  options: UseInfraStreamOptions = {}
): UseInfraStreamReturn {
  const {
    enableTopology = true,
    enableEvents = true,
    reconnectDelay = 3000,
    maxEvents = 100,
    debounceMs = 100,
  } = options;

  // State
  const [topology, setTopology] = useState<InfraTopologyResponse | null>(
    initialTopology || null
  );
  const [events, setEvents] = useState<InfraEvent[]>([]);
  const [status, setStatus] = useState<StreamConnectionStatus>('disconnected');
  const [error, setError] = useState<string | null>(null);

  // Refs for cleanup and debouncing
  const topologyStreamRef = useRef<EventSource | null>(null);
  const eventsStreamRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const debounceTimeoutRef = useRef<number | null>(null);
  const pendingUpdatesRef = useRef<TopologyUpdate[]>([]);
  const mountedRef = useRef(true);

  // Apply debounced updates
  const applyPendingUpdates = useCallback(() => {
    if (!mountedRef.current) return;

    const updates = pendingUpdatesRef.current;
    if (updates.length === 0) return;

    // Clear pending
    pendingUpdatesRef.current = [];

    // Apply all pending updates
    setTopology((prev) => {
      let result = prev;
      for (const update of updates) {
        result = applyTopologyUpdate(result, update);
      }
      return result;
    });
  }, []);

  // Queue an update with debouncing
  const queueUpdate = useCallback(
    (update: TopologyUpdate) => {
      pendingUpdatesRef.current.push(update);

      // Clear existing debounce timer
      if (debounceTimeoutRef.current !== null) {
        window.clearTimeout(debounceTimeoutRef.current);
      }

      // Set new debounce timer
      debounceTimeoutRef.current = window.setTimeout(() => {
        applyPendingUpdates();
        debounceTimeoutRef.current = null;
      }, debounceMs);
    },
    [applyPendingUpdates, debounceMs]
  );

  // Connect to topology stream
  const connectTopologyStream = useCallback(() => {
    if (!enableTopology || !mountedRef.current) return;

    // Close existing
    if (topologyStreamRef.current) {
      topologyStreamRef.current.close();
    }

    setStatus('connecting');
    setError(null);

    try {
      const source = infraApi.createTopologyStream();
      topologyStreamRef.current = source;

      source.onopen = () => {
        if (mountedRef.current) {
          setStatus('connected');
          setError(null);
        }
      };

      source.onmessage = (event) => {
        if (!mountedRef.current) return;

        try {
          const update = JSON.parse(event.data) as TopologyUpdate;

          // Handle error messages from server
          if ('error' in update) {
            setError(String((update as unknown as { error: string }).error));
            return;
          }

          // Full topology replaces everything immediately
          if (update.kind === 'full' && update.topology) {
            setTopology(update.topology);
          } else {
            // Queue incremental updates for debouncing
            queueUpdate(update);
          }
        } catch (e) {
          console.error('Failed to parse topology update:', e);
        }
      };

      source.onerror = () => {
        if (!mountedRef.current) return;

        console.error('Topology stream error, reconnecting...');
        setStatus('reconnecting');

        // Close and reconnect
        source.close();
        topologyStreamRef.current = null;

        reconnectTimeoutRef.current = window.setTimeout(() => {
          connectTopologyStream();
        }, reconnectDelay);
      };
    } catch (e) {
      console.error('Failed to create topology stream:', e);
      setStatus('error');
      setError('Failed to connect to topology stream');
    }
  }, [enableTopology, queueUpdate, reconnectDelay]);

  // Connect to events stream
  const connectEventsStream = useCallback(() => {
    if (!enableEvents || !mountedRef.current) return;

    // Close existing
    if (eventsStreamRef.current) {
      eventsStreamRef.current.close();
    }

    try {
      const source = infraApi.createEventsStream();
      eventsStreamRef.current = source;

      source.onmessage = (event) => {
        if (!mountedRef.current) return;

        try {
          const infraEvent = JSON.parse(event.data) as InfraEvent;

          // Ignore error messages
          if ('error' in infraEvent) return;

          setEvents((prev) => {
            // Deduplicate by id to avoid React key warnings
            const seen = new Set(prev.map((e) => e.id));
            if (seen.has(infraEvent.id)) {
              return prev; // Skip duplicate
            }
            return [infraEvent, ...prev].slice(0, maxEvents);
          });
        } catch (e) {
          console.error('Failed to parse event:', e);
        }
      };

      source.onerror = () => {
        if (!mountedRef.current) return;

        // Silently reconnect events stream
        source.close();
        eventsStreamRef.current = null;

        setTimeout(() => {
          connectEventsStream();
        }, reconnectDelay);
      };
    } catch (e) {
      console.error('Failed to create events stream:', e);
    }
  }, [enableEvents, maxEvents, reconnectDelay]);

  // Manual reconnect
  const reconnect = useCallback(() => {
    // Clear any pending reconnect
    if (reconnectTimeoutRef.current !== null) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    connectTopologyStream();
    connectEventsStream();
  }, [connectTopologyStream, connectEventsStream]);

  // Manual disconnect
  const disconnect = useCallback(() => {
    // Clear reconnect timer
    if (reconnectTimeoutRef.current !== null) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Close streams
    if (topologyStreamRef.current) {
      topologyStreamRef.current.close();
      topologyStreamRef.current = null;
    }
    if (eventsStreamRef.current) {
      eventsStreamRef.current.close();
      eventsStreamRef.current = null;
    }

    setStatus('disconnected');
  }, []);

  // Initial connection
  useEffect(() => {
    mountedRef.current = true;

    // Connect after a short delay to allow initial topology to load
    const timer = setTimeout(() => {
      reconnect();
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
  }, [reconnect, disconnect]);

  return {
    topology,
    events,
    status,
    isConnected: status === 'connected',
    reconnect,
    disconnect,
    error,
  };
}

export default useInfraStream;
