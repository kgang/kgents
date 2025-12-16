/**
 * useProjectedStream: React hook for SSE streaming with state machine.
 *
 * Provides unified streaming with:
 * - Explicit state management (IDLE, CONNECTING, STREAMING, DONE, ERROR, REFUSED)
 * - Automatic reconnection with exponential backoff
 * - Backpressure visibility (dropped events)
 * - OTEL-friendly metrics
 *
 * @example
 * const { data, meta, connect, disconnect, retry } = useProjectedStream<MyData>({
 *   endpoint: '/api/stream',
 *   autoConnect: true,
 * });
 */

import { useState, useCallback, useRef, useEffect, useMemo } from 'react';
import type { WidgetMeta, WidgetStatus } from '../reactive/schema';
import { WidgetMetaFactory } from '../reactive/schema';

// =============================================================================
// Types
// =============================================================================

export interface StreamConfig {
  /** SSE endpoint URL */
  endpoint: string;
  /** Auto-connect on mount */
  autoConnect?: boolean;
  /** Auto-reconnect on error */
  autoReconnect?: boolean;
  /** Maximum reconnect attempts */
  maxReconnects?: number;
  /** Base delay for exponential backoff (ms) */
  baseDelayMs?: number;
  /** Maximum delay cap (ms) */
  maxDelayMs?: number;
  /** Maximum queued events before dropping */
  maxQueueSize?: number;
  /** Event type for data updates */
  dataEventType?: string;
  /** Heartbeat timeout (ms) - disconnect if no heartbeat */
  heartbeatTimeoutMs?: number;
}

export interface StreamStats {
  eventsReceived: number;
  eventsDelivered: number;
  eventsDropped: number;
  bytesReceived: number;
  reconnectCount: number;
  lastEventAt: number | null;
}

export interface UseProjectedStreamResult<T> {
  /** Latest data from stream */
  data: T | null;
  /** Stream metadata (status, errors, etc.) */
  meta: WidgetMeta;
  /** Stream statistics */
  stats: StreamStats;
  /** Accumulated events (for batch processing) */
  events: T[];
  /** Connect to stream */
  connect: () => void;
  /** Disconnect from stream */
  disconnect: () => void;
  /** Pause streaming (keep connection) */
  pause: () => void;
  /** Resume from paused */
  resume: () => void;
  /** Retry after error */
  retry: () => void;
  /** Clear accumulated events */
  clearEvents: () => void;
}

// =============================================================================
// Default Configuration
// =============================================================================

const DEFAULT_CONFIG: Required<Omit<StreamConfig, 'endpoint'>> = {
  autoConnect: true,
  autoReconnect: true,
  maxReconnects: 5,
  baseDelayMs: 1000,
  maxDelayMs: 30000,
  maxQueueSize: 100,
  dataEventType: 'data',
  heartbeatTimeoutMs: 60000,
};

// =============================================================================
// Hook Implementation
// =============================================================================

export function useProjectedStream<T>(config: StreamConfig): UseProjectedStreamResult<T> {
  const fullConfig = useMemo(() => ({ ...DEFAULT_CONFIG, ...config }), [config]);

  // State
  const [data, setData] = useState<T | null>(null);
  const [meta, setMeta] = useState<WidgetMeta>(WidgetMetaFactory.idle());
  const [stats, setStats] = useState<StreamStats>({
    eventsReceived: 0,
    eventsDelivered: 0,
    eventsDropped: 0,
    bytesReceived: 0,
    reconnectCount: 0,
    lastEventAt: null,
  });
  const [events, setEvents] = useState<T[]>([]);

  // Refs for mutable state
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pausedRef = useRef(false);

  // ==========================================================================
  // Helpers
  // ==========================================================================

  const computeBackoffDelay = useCallback(
    (attempt: number): number => {
      const base = fullConfig.baseDelayMs * Math.pow(2, attempt);
      const capped = Math.min(base, fullConfig.maxDelayMs);
      // Add jitter (+/- 20%)
      const jitter = capped * 0.2 * (Math.random() * 2 - 1);
      return Math.max(0, capped + jitter);
    },
    [fullConfig.baseDelayMs, fullConfig.maxDelayMs]
  );

  const updateStreamMeta = useCallback((received: number, totalExpected: number | null = null) => {
    setMeta((prev) => ({
      ...prev,
      stream: {
        totalExpected,
        received,
        startedAt: prev.stream?.startedAt ?? new Date().toISOString(),
        lastChunkAt: new Date().toISOString(),
      },
    }));
  }, []);

  const resetHeartbeatTimer = useCallback(() => {
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
    }
    heartbeatTimeoutRef.current = setTimeout(() => {
      // Heartbeat timeout - disconnect
      console.warn('[useProjectedStream] Heartbeat timeout');
      disconnect();
      if (fullConfig.autoReconnect) {
        scheduleReconnect();
      }
    }, fullConfig.heartbeatTimeoutMs);
  }, [fullConfig.heartbeatTimeoutMs, fullConfig.autoReconnect]);

  // ==========================================================================
  // Connection Management
  // ==========================================================================

  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setMeta(WidgetMetaFactory.loading());
    pausedRef.current = false;

    const es = new EventSource(fullConfig.endpoint);
    eventSourceRef.current = es;

    es.onopen = () => {
      reconnectCountRef.current = 0;
      setMeta(
        WidgetMetaFactory.streaming({
          totalExpected: null,
          received: 0,
          startedAt: new Date().toISOString(),
          lastChunkAt: null,
        })
      );
      resetHeartbeatTimer();
    };

    // Data events
    es.addEventListener(fullConfig.dataEventType, (e: MessageEvent) => {
      if (pausedRef.current) return;

      try {
        const envelope = JSON.parse(e.data);
        const parsedData = envelope.data as T;

        // Update data
        setData(parsedData);

        // Update stats
        setStats((prev) => ({
          ...prev,
          eventsReceived: prev.eventsReceived + 1,
          eventsDelivered: prev.eventsDelivered + 1,
          bytesReceived: prev.bytesReceived + e.data.length,
          lastEventAt: Date.now(),
        }));

        // Update meta
        updateStreamMeta(stats.eventsReceived + 1);

        // Accumulate events (with backpressure)
        setEvents((prev) => {
          if (prev.length >= fullConfig.maxQueueSize) {
            // Drop oldest
            setStats((s) => ({
              ...s,
              eventsDropped: s.eventsDropped + 1,
            }));
            return [...prev.slice(1), parsedData];
          }
          return [...prev, parsedData];
        });

        resetHeartbeatTimer();
      } catch (err) {
        console.error('[useProjectedStream] Parse error:', err);
      }
    });

    // Heartbeat events
    es.addEventListener('heartbeat', () => {
      resetHeartbeatTimer();
    });

    // Complete event
    es.addEventListener('complete', (_e: MessageEvent) => {
      setMeta(WidgetMetaFactory.done());
      es.close();
    });

    // Error event from server
    es.addEventListener('error', (e: MessageEvent) => {
      if (e.data) {
        try {
          const envelope = JSON.parse(e.data);
          if (envelope.meta?.error) {
            setMeta(WidgetMetaFactory.withError(envelope.meta.error));
            es.close();
            return;
          }
          if (envelope.meta?.refusal) {
            setMeta(WidgetMetaFactory.withRefusal(envelope.meta.refusal));
            es.close();
          }
        } catch {
          // Ignore parse errors
        }
      }
    });

    // Refusal event
    es.addEventListener('refusal', (e: MessageEvent) => {
      try {
        const envelope = JSON.parse(e.data);
        if (envelope.meta?.refusal) {
          setMeta(WidgetMetaFactory.withRefusal(envelope.meta.refusal));
        }
      } catch {
        setMeta(
          WidgetMetaFactory.withRefusal({
            reason: 'Stream refused',
            consentRequired: null,
            appealTo: null,
            overrideCost: null,
          })
        );
      }
      es.close();
    });

    // Connection error
    es.onerror = () => {
      if (heartbeatTimeoutRef.current) {
        clearTimeout(heartbeatTimeoutRef.current);
      }

      setMeta(
        WidgetMetaFactory.withError({
          category: 'network',
          code: 'SSE_ERROR',
          message: 'Stream connection failed',
          retryAfterSeconds: fullConfig.autoReconnect
            ? Math.round(computeBackoffDelay(reconnectCountRef.current) / 1000)
            : null,
          fallbackAction: null,
          traceId: null,
        })
      );

      es.close();

      // Auto-reconnect
      if (fullConfig.autoReconnect && reconnectCountRef.current < fullConfig.maxReconnects) {
        scheduleReconnect();
      }
    };
  }, [
    fullConfig,
    computeBackoffDelay,
    updateStreamMeta,
    resetHeartbeatTimer,
    stats.eventsReceived,
  ]);

  const scheduleReconnect = useCallback(() => {
    const delay = computeBackoffDelay(reconnectCountRef.current);
    reconnectCountRef.current++;

    setStats((prev) => ({
      ...prev,
      reconnectCount: prev.reconnectCount + 1,
    }));

    reconnectTimeoutRef.current = setTimeout(() => {
      connect();
    }, delay);
  }, [computeBackoffDelay, connect]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
      heartbeatTimeoutRef.current = null;
    }
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setMeta(WidgetMetaFactory.idle());
  }, []);

  const pause = useCallback(() => {
    pausedRef.current = true;
    setMeta((prev) => ({ ...prev, status: 'stale' as WidgetStatus }));
  }, []);

  const resume = useCallback(() => {
    pausedRef.current = false;
    setMeta((prev) => ({ ...prev, status: 'streaming' as WidgetStatus }));
  }, []);

  const retry = useCallback(() => {
    reconnectCountRef.current = 0;
    connect();
  }, [connect]);

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  // ==========================================================================
  // Lifecycle
  // ==========================================================================

  useEffect(() => {
    if (fullConfig.autoConnect) {
      connect();
    }
    return () => {
      disconnect();
    };
  }, [fullConfig.autoConnect, fullConfig.endpoint]);

  return {
    data,
    meta,
    stats,
    events,
    connect,
    disconnect,
    pause,
    resume,
    retry,
    clearEvents,
  };
}

export default useProjectedStream;
