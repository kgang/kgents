/**
 * useWitnessStream - SSE streaming hook for live Witness thoughts.
 *
 * Phase 2: Witness Integration for Self.Garden.
 *
 * Provides:
 * - Real-time thought streaming via SSE
 * - Connection management with automatic reconnection
 * - Source filtering (gardener, git, etc.)
 * - Latest thought tracking
 *
 * @example
 * const { thoughts, isWitnessing, latestThought } = useWitnessStream({
 *   sources: ['gardener', 'git'],
 * });
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface WitnessThought {
  type: 'thought';
  content: string;
  source: string;
  tags: string[];
  timestamp: string | null;
}

export type WitnessStreamStatus =
  | 'disconnected'
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'error';

export interface UseWitnessStreamOptions {
  /** Whether to enable streaming (default: true) */
  enabled?: boolean;
  /** Maximum thoughts to fetch initially (default: 50) */
  limit?: number;
  /** Filter by sources (e.g., ['gardener', 'git']) */
  sources?: string[];
  /** Reconnection delay in ms (default: 3000) */
  reconnectDelay?: number;
  /** Maximum thoughts to keep in memory (default: 100) */
  maxThoughts?: number;
  /** Server poll interval in seconds (default: 2.0) */
  pollInterval?: number;
}

export interface UseWitnessStreamReturn {
  /** All thoughts received */
  thoughts: WitnessThought[];
  /** Connection status */
  status: WitnessStreamStatus;
  /** Whether currently connected and receiving */
  isWitnessing: boolean;
  /** Most recent thought */
  latestThought: WitnessThought | null;
  /** Last update timestamp */
  lastUpdate: Date | null;
  /** Error message if any */
  error: string | null;
  /** Manually reconnect */
  reconnect: () => void;
  /** Manually disconnect */
  disconnect: () => void;
  /** Clear all thoughts */
  clearThoughts: () => void;
}

// =============================================================================
// Hook Implementation
// =============================================================================

const API_BASE = import.meta.env.VITE_API_URL || '';

export function useWitnessStream(options: UseWitnessStreamOptions = {}): UseWitnessStreamReturn {
  const {
    enabled = true,
    limit = 50,
    sources,
    reconnectDelay = 3000,
    maxThoughts = 100,
    pollInterval = 2.0,
  } = options;

  // State
  const [thoughts, setThoughts] = useState<WitnessThought[]>([]);
  const [status, setStatus] = useState<WitnessStreamStatus>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Refs for cleanup
  const streamRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const mountedRef = useRef(true);

  // Build endpoint URL with query params
  const buildEndpoint = useCallback(() => {
    const params = new URLSearchParams();
    params.set('limit', String(limit));
    params.set('poll_interval', String(pollInterval));
    if (sources && sources.length > 0) {
      params.set('sources', sources.join(','));
    }
    return `${API_BASE}/agentese/self/witness/stream?${params.toString()}`;
  }, [limit, sources, pollInterval]);

  // Add thought with deduplication and max limit
  const addThought = useCallback(
    (thought: WitnessThought) => {
      setThoughts((prev) => {
        // Check for duplicates by timestamp + content
        const isDuplicate = prev.some(
          (t) => t.timestamp === thought.timestamp && t.content === thought.content
        );
        if (isDuplicate) return prev;

        // Add new thought, trim to maxThoughts
        const updated = [...prev, thought];
        if (updated.length > maxThoughts) {
          return updated.slice(-maxThoughts);
        }
        return updated;
      });
      setLastUpdate(new Date());
    },
    [maxThoughts]
  );

  // Connect to stream
  const connect = useCallback(() => {
    if (!enabled || !mountedRef.current) return;

    // Close existing
    if (streamRef.current) {
      streamRef.current.close();
    }

    setStatus('connecting');
    setError(null);

    try {
      const endpoint = buildEndpoint();
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
          const data = JSON.parse(event.data) as WitnessThought;

          // Handle error responses
          if ('error' in data) {
            setError((data as unknown as { error: string }).error);
            return;
          }

          // Handle thought
          if (data.type === 'thought') {
            addThought(data);
          }
        } catch (e) {
          console.error('[useWitnessStream] Failed to parse event:', e);
        }
      };

      source.onerror = () => {
        if (!mountedRef.current) return;

        console.warn('[useWitnessStream] Stream error, reconnecting...');
        setStatus('reconnecting');

        source.close();
        streamRef.current = null;

        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, reconnectDelay);
      };
    } catch (e) {
      console.error('[useWitnessStream] Failed to create stream:', e);
      setStatus('error');
      setError('Failed to connect to witness stream');
    }
  }, [enabled, buildEndpoint, addThought, reconnectDelay]);

  // Manual reconnect
  const reconnect = useCallback(() => {
    if (reconnectTimeoutRef.current !== null) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    connect();
  }, [connect]);

  // Manual disconnect
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current !== null) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.close();
      streamRef.current = null;
    }
    setStatus('disconnected');
  }, []);

  // Clear all thoughts
  const clearThoughts = useCallback(() => {
    setThoughts([]);
  }, []);

  // Lifecycle
  useEffect(() => {
    mountedRef.current = true;

    // Connect after short delay to allow component mount
    const timer = setTimeout(() => {
      connect();
    }, 500);

    return () => {
      mountedRef.current = false;
      clearTimeout(timer);
      disconnect();
    };
  }, [connect, disconnect]);

  // Reconnect when options change
  useEffect(() => {
    if (enabled && status === 'connected') {
      reconnect();
    }
  }, [sources?.join(','), limit, pollInterval]);

  // Derived state
  const latestThought = thoughts.length > 0 ? thoughts[thoughts.length - 1] : null;
  const isWitnessing = status === 'connected' && thoughts.length > 0;

  return {
    thoughts,
    status,
    isWitnessing,
    latestThought,
    lastUpdate,
    error,
    reconnect,
    disconnect,
    clearThoughts,
  };
}

export default useWitnessStream;
