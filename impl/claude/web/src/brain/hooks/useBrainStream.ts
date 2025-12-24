/**
 * useBrainStream — Real-time SSE hook for unified Brain stream
 *
 * "Witness everything — marks are cheap, wisdom is expensive."
 *
 * Connects to the explorer SSE endpoint and provides:
 * - Real-time event streaming
 * - Automatic reconnection with exponential backoff
 * - Connection status tracking
 * - Filter-aware subscriptions
 */

import { useCallback, useEffect, useRef, useState } from 'react';

import type { StreamEvent, StreamFilters, UnifiedEvent } from '../types';

// =============================================================================
// Types
// =============================================================================

export interface UseBrainStreamOptions {
  /** Initial filters (optional) */
  filters?: StreamFilters;

  /** Maximum events to keep in memory */
  maxEvents?: number;

  /** Reconnection delay in ms (default: 3000) */
  reconnectDelay?: number;

  /** Maximum reconnection attempts (default: 10) */
  maxReconnectAttempts?: number;

  /** Callback when new event arrives */
  onEvent?: (event: UnifiedEvent) => void;

  /** Callback on connection status change */
  onConnectionChange?: (connected: boolean) => void;

  /** Callback on error */
  onError?: (error: Error) => void;
}

export interface UseBrainStreamResult {
  /** All events received */
  events: UnifiedEvent[];

  /** Whether connected to SSE stream */
  connected: boolean;

  /** Whether currently reconnecting */
  reconnecting: boolean;

  /** Number of reconnection attempts */
  reconnectAttempts: number;

  /** Last error (if any) */
  error: Error | null;

  /** Manually reconnect */
  reconnect: () => void;

  /** Disconnect from stream */
  disconnect: () => void;

  /** Clear all events */
  clearEvents: () => void;

  /** Update filters (reconnects with new filters) */
  setFilters: (filters: StreamFilters) => void;
}

// =============================================================================
// Constants
// =============================================================================

const DEFAULT_MAX_EVENTS = 500;
const DEFAULT_RECONNECT_DELAY = 3000;
const DEFAULT_MAX_RECONNECT_ATTEMPTS = 10;

// =============================================================================
// Hook Implementation
// =============================================================================

export function useBrainStream(options: UseBrainStreamOptions = {}): UseBrainStreamResult {
  const {
    filters: initialFilters,
    maxEvents = DEFAULT_MAX_EVENTS,
    reconnectDelay = DEFAULT_RECONNECT_DELAY,
    maxReconnectAttempts = DEFAULT_MAX_RECONNECT_ATTEMPTS,
    onEvent,
    onConnectionChange,
    onError,
  } = options;

  // State
  const [events, setEvents] = useState<UnifiedEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const [reconnecting, setReconnecting] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [error, setError] = useState<Error | null>(null);
  const [filters, setFiltersState] = useState<StreamFilters>(initialFilters ?? { types: [] });

  // Refs for cleanup
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const isCleanedUpRef = useRef(false);

  // Build SSE URL with filters
  const buildStreamUrl = useCallback((streamFilters: StreamFilters): string => {
    const API_BASE = import.meta.env.VITE_API_URL || '';
    const params = new URLSearchParams();

    if (streamFilters.types.length > 0) {
      params.set('types', streamFilters.types.join(','));
    }
    if (streamFilters.author) {
      params.set('author', streamFilters.author);
    }
    if (streamFilters.searchQuery) {
      params.set('query', streamFilters.searchQuery);
    }
    if (streamFilters.tags && streamFilters.tags.length > 0) {
      params.set('tags', streamFilters.tags.join(','));
    }
    if (streamFilters.dateRange) {
      params.set('start', streamFilters.dateRange.start.toISOString());
      params.set('end', streamFilters.dateRange.end.toISOString());
    }

    const query = params.toString();
    return `${API_BASE}/api/explorer/stream${query ? `?${query}` : ''}`;
  }, []);

  // Connect to SSE stream
  const connect = useCallback(() => {
    if (isCleanedUpRef.current) return;

    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const url = buildStreamUrl(filters);
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setConnected(true);
      setReconnecting(false);
      setReconnectAttempts(0);
      setError(null);
      onConnectionChange?.(true);
    };

    eventSource.onmessage = (messageEvent) => {
      try {
        const data = JSON.parse(messageEvent.data) as StreamEvent;

        switch (data.type) {
          case 'event':
            setEvents((prev) => {
              const updated = [data.event, ...prev];
              return updated.slice(0, maxEvents);
            });
            onEvent?.(data.event);
            break;

          case 'batch':
            setEvents((prev) => {
              const updated = [...data.events, ...prev];
              return updated.slice(0, maxEvents);
            });
            data.events.forEach((event) => onEvent?.(event));
            break;

          case 'connected':
            // Connection confirmed
            break;

          case 'heartbeat':
            // Keep-alive, ignore
            break;
        }
      } catch (parseError) {
        console.error('[useBrainStream] Failed to parse event:', parseError);
      }
    };

    eventSource.onerror = () => {
      setConnected(false);
      onConnectionChange?.(false);
      eventSource.close();
      eventSourceRef.current = null;

      // Attempt reconnection with exponential backoff
      if (!isCleanedUpRef.current && reconnectAttempts < maxReconnectAttempts) {
        setReconnecting(true);
        const delay = reconnectDelay * Math.pow(2, reconnectAttempts);

        reconnectTimeoutRef.current = window.setTimeout(() => {
          setReconnectAttempts((prev) => prev + 1);
          connect();
        }, delay);
      } else if (reconnectAttempts >= maxReconnectAttempts) {
        const maxAttemptsError = new Error(
          `Failed to connect after ${maxReconnectAttempts} attempts`
        );
        setError(maxAttemptsError);
        setReconnecting(false);
        onError?.(maxAttemptsError);
      }
    };
  }, [
    filters,
    buildStreamUrl,
    maxEvents,
    reconnectDelay,
    maxReconnectAttempts,
    reconnectAttempts,
    onEvent,
    onConnectionChange,
    onError,
  ]);

  // Disconnect from stream
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current !== null) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setConnected(false);
    setReconnecting(false);
    onConnectionChange?.(false);
  }, [onConnectionChange]);

  // Manual reconnect
  const reconnect = useCallback(() => {
    setReconnectAttempts(0);
    setError(null);
    disconnect();
    connect();
  }, [connect, disconnect]);

  // Clear events
  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  // Update filters (triggers reconnection)
  const setFilters = useCallback(
    (newFilters: StreamFilters) => {
      setFiltersState(newFilters);
      // Will trigger reconnect via useEffect
    },
    []
  );

  // Connect on mount and filter changes
  useEffect(() => {
    isCleanedUpRef.current = false;
    connect();

    return () => {
      isCleanedUpRef.current = true;
      disconnect();
    };
  }, [filters]); // eslint-disable-line react-hooks/exhaustive-deps -- connect/disconnect are stable

  return {
    events,
    connected,
    reconnecting,
    reconnectAttempts,
    error,
    reconnect,
    disconnect,
    clearEvents,
    setFilters,
  };
}

// =============================================================================
// Fallback: Poll-based stream for when SSE is unavailable
// =============================================================================

export interface UseBrainPollOptions {
  /** Polling interval in ms (default: 5000) */
  pollInterval?: number;

  /** Initial filters */
  filters?: StreamFilters;

  /** Maximum events to keep */
  maxEvents?: number;
}

/**
 * Fallback hook that polls instead of using SSE.
 * Use this during development or when SSE endpoint isn't available.
 */
export function useBrainPoll(options: UseBrainPollOptions = {}): UseBrainStreamResult {
  const {
    pollInterval = 5000,
    filters: initialFilters,
    maxEvents = DEFAULT_MAX_EVENTS,
  } = options;

  const [events, setEvents] = useState<UnifiedEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [filters, setFiltersState] = useState<StreamFilters>(initialFilters ?? { types: [] });

  const intervalRef = useRef<number | null>(null);

  const fetchEvents = useCallback(async () => {
    try {
      const API_BASE = import.meta.env.VITE_API_URL || '';
      const params = new URLSearchParams();

      if (filters.types.length > 0) {
        params.set('types', filters.types.join(','));
      }
      params.set('limit', String(maxEvents));

      const url = `${API_BASE}/api/explorer/list${params.toString() ? `?${params}` : ''}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setEvents(data.events ?? []);
      setConnected(true);
      setError(null);
    } catch (fetchError) {
      setConnected(false);
      setError(fetchError instanceof Error ? fetchError : new Error(String(fetchError)));
    }
  }, [filters, maxEvents]);

  useEffect(() => {
    fetchEvents();
    intervalRef.current = window.setInterval(fetchEvents, pollInterval);

    return () => {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
      }
    };
  }, [fetchEvents, pollInterval]);

  return {
    events,
    connected,
    reconnecting: false,
    reconnectAttempts: 0,
    error,
    reconnect: fetchEvents,
    disconnect: () => {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      setConnected(false);
    },
    clearEvents: () => setEvents([]),
    setFilters: setFiltersState,
  };
}

export default useBrainStream;
