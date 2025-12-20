/**
 * useMuseStream - SSE streaming hook for live Muse whispers.
 *
 * Phase 3: Muse Integration for Self.Garden.
 *
 * Provides:
 * - Real-time whisper streaming via SSE
 * - Connection management with automatic reconnection
 * - Current whisper tracking
 * - Dismiss/accept actions
 *
 * @example
 * const { currentWhisper, dismiss, accept, isListening } = useMuseStream();
 *
 * if (currentWhisper) {
 *   console.log(currentWhisper.content);
 * }
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface MuseWhisper {
  type: 'whisper';
  whisper_id: string;
  content: string;
  category: string;
  confidence: number;
  urgency: number;
  arc_phase: string;
  tension: number;
  timestamp: string;
}

export type MuseStreamStatus =
  | 'disconnected'
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'error';

export interface UseMuseStreamOptions {
  /** Whether to enable streaming (default: true) */
  enabled?: boolean;
  /** Server poll interval in seconds (default: 30.0) */
  pollInterval?: number;
  /** Reconnection delay in ms (default: 5000) */
  reconnectDelay?: number;
  /** Maximum whispers to keep in history (default: 20) */
  maxWhispers?: number;
}

export interface UseMuseStreamReturn {
  /** Current (most recent) whisper */
  currentWhisper: MuseWhisper | null;
  /** All whispers received */
  whispers: MuseWhisper[];
  /** Connection status */
  status: MuseStreamStatus;
  /** Whether currently connected and listening */
  isListening: boolean;
  /** Last update timestamp */
  lastUpdate: Date | null;
  /** Error message if any */
  error: string | null;
  /** Dismiss the current whisper */
  dismiss: (whisperId: string, reason?: string) => Promise<void>;
  /** Accept/acknowledge the current whisper */
  accept: (whisperId: string, action?: string) => Promise<void>;
  /** Manually reconnect */
  reconnect: () => void;
  /** Manually disconnect */
  disconnect: () => void;
}

// =============================================================================
// Hook Implementation
// =============================================================================

const API_BASE = import.meta.env.VITE_API_URL || '';

export function useMuseStream(options: UseMuseStreamOptions = {}): UseMuseStreamReturn {
  const { enabled = true, pollInterval = 30.0, reconnectDelay = 5000, maxWhispers = 20 } = options;

  // State
  const [whispers, setWhispers] = useState<MuseWhisper[]>([]);
  const [status, setStatus] = useState<MuseStreamStatus>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Refs for cleanup
  const streamRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const mountedRef = useRef(true);

  // Build endpoint URL with query params
  const buildEndpoint = useCallback(() => {
    const params = new URLSearchParams();
    params.set('poll_interval', String(pollInterval));
    return `${API_BASE}/agentese/self/muse/stream?${params.toString()}`;
  }, [pollInterval]);

  // Add whisper with deduplication and max limit
  const addWhisper = useCallback(
    (whisper: MuseWhisper) => {
      setWhispers((prev) => {
        // Check for duplicates by whisper_id
        const isDuplicate = prev.some((w) => w.whisper_id === whisper.whisper_id);
        if (isDuplicate) return prev;

        // Add new whisper, trim to maxWhispers
        const updated = [...prev, whisper];
        if (updated.length > maxWhispers) {
          return updated.slice(-maxWhispers);
        }
        return updated;
      });
      setLastUpdate(new Date());
    },
    [maxWhispers]
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
          const data = JSON.parse(event.data) as MuseWhisper;

          // Handle error responses
          if ('error' in data) {
            setError((data as unknown as { error: string }).error);
            return;
          }

          // Handle whisper
          if (data.type === 'whisper') {
            addWhisper(data);
          }
        } catch (e) {
          console.error('[useMuseStream] Failed to parse event:', e);
        }
      };

      source.onerror = () => {
        if (!mountedRef.current) return;

        console.warn('[useMuseStream] Stream error, reconnecting...');
        setStatus('reconnecting');

        source.close();
        streamRef.current = null;

        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, reconnectDelay);
      };
    } catch (e) {
      console.error('[useMuseStream] Failed to create stream:', e);
      setStatus('error');
      setError('Failed to connect to muse stream');
    }
  }, [enabled, buildEndpoint, addWhisper, reconnectDelay]);

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

  // Dismiss a whisper
  const dismiss = useCallback(async (whisperId: string, reason?: string) => {
    try {
      await fetch(`${API_BASE}/agentese/self/muse/dismiss`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ whisper_id: whisperId, reason: reason || '' }),
      });
      // Remove from local state
      setWhispers((prev) => prev.filter((w) => w.whisper_id !== whisperId));
    } catch (e) {
      console.error('[useMuseStream] Failed to dismiss whisper:', e);
    }
  }, []);

  // Accept a whisper
  const accept = useCallback(async (whisperId: string, action?: string) => {
    try {
      await fetch(`${API_BASE}/agentese/self/muse/accept`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ whisper_id: whisperId, action: action || 'acknowledged' }),
      });
      // Remove from local state (it's been acknowledged)
      setWhispers((prev) => prev.filter((w) => w.whisper_id !== whisperId));
    } catch (e) {
      console.error('[useMuseStream] Failed to accept whisper:', e);
    }
  }, []);

  // Lifecycle
  useEffect(() => {
    mountedRef.current = true;

    // Connect after short delay to allow component mount
    const timer = setTimeout(() => {
      connect();
    }, 1000);

    return () => {
      mountedRef.current = false;
      clearTimeout(timer);
      disconnect();
    };
  }, [connect, disconnect]);

  // Derived state
  const currentWhisper = whispers.length > 0 ? whispers[whispers.length - 1] : null;
  const isListening = status === 'connected';

  return {
    currentWhisper,
    whispers,
    status,
    isListening,
    lastUpdate,
    error,
    dismiss,
    accept,
    reconnect,
    disconnect,
  };
}

export default useMuseStream;
