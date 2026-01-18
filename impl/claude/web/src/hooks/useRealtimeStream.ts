/**
 * useRealtimeStream — Hook for SSE real-time updates
 *
 * Grounded in: docs/skills/metaphysical-fullstack.md
 * "Streaming through SSE, not WebSockets."
 *
 * Connects to the Witness SSE stream at /api/witness/stream for real-time updates:
 * - Mark events (created, retracted)
 * - K-Block events (edited, saved, discarded)
 * - Constitutional evaluations
 * - Heartbeats (30s keepalive)
 *
 * See: services/witness/bus.py for WitnessTopics
 */

import { useState, useEffect, useCallback, useRef } from 'react';

/** Witness event types from WitnessTopics (services/witness/bus.py) */
type WitnessEventType =
  | 'connected'
  | 'disconnected'
  | 'heartbeat'
  | 'mark_created'
  | 'mark_retracted'
  | 'kblock_edited'
  | 'kblock_saved'
  | 'kblock_discarded'
  | 'constitutional_evaluated'
  | 'thought_captured'
  | 'trail_captured'
  | 'error';

interface StreamEvent {
  /** Event type from WitnessTopics */
  type: WitnessEventType | string;

  /** Event data */
  data: unknown;

  /** Timestamp */
  timestamp: string;

  /** Original topic (for debugging) */
  topic?: string;
}

interface UseRealtimeStreamResult {
  /** Connection status */
  status: 'connected' | 'connecting' | 'disconnected';

  /** Last received event */
  lastEvent: StreamEvent | null;

  /** Error (if any) */
  error: string | null;

  /** Connect to the stream */
  connect: () => void;

  /** Disconnect from the stream */
  disconnect: () => void;
}

interface StreamHandlers {
  /** Called when a mark is created */
  onMarkCreated?: (data: unknown) => void;
  /** Called when a K-Block is edited/saved */
  onKBlockChange?: (data: unknown) => void;
  /** Called for any witness event */
  onWitnessEvent?: (event: StreamEvent) => void;
}

/**
 * Hook for SSE real-time updates from the Witness stream.
 *
 * @param url - SSE endpoint URL (default: /api/witness/stream)
 * @param handlers - Optional event handlers
 */
export function useRealtimeStream(
  url: string = '/api/witness/stream',
  handlers?: StreamHandlers
): UseRealtimeStreamResult {
  const [status, setStatus] = useState<'connected' | 'connecting' | 'disconnected'>('disconnected');
  const [lastEvent, setLastEvent] = useState<StreamEvent | null>(null);
  const [error, setError] = useState<string | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const reconnectAttempts = useRef(0);

  /**
   * Connect to the SSE stream.
   */
  const connect = useCallback(() => {
    // Clean up existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setStatus('connecting');
    setError(null);

    try {
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setStatus('connected');
        setError(null);
        reconnectAttempts.current = 0;
      };

      eventSource.onerror = () => {
        setStatus('disconnected');
        setError('Connection lost');
        eventSource.close();

        // Exponential backoff reconnection
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
        reconnectAttempts.current += 1;

        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, delay);
      };

      // Handle connection event
      eventSource.addEventListener('connected', (e) => {
        const data = JSON.parse(e.data);
        const event: StreamEvent = {
          type: 'connected',
          data,
          timestamp: new Date().toISOString(),
        };
        setLastEvent(event);
        handlers?.onWitnessEvent?.(event);
      });

      // Handle mark events
      eventSource.addEventListener('mark_created', (e) => {
        const data = JSON.parse(e.data);
        const event: StreamEvent = {
          type: 'mark_created',
          data,
          timestamp: new Date().toISOString(),
          topic: data.topic,
        };
        setLastEvent(event);
        handlers?.onMarkCreated?.(data);
        handlers?.onWitnessEvent?.(event);
      });

      eventSource.addEventListener('mark_retracted', (e) => {
        const data = JSON.parse(e.data);
        const event: StreamEvent = {
          type: 'mark_retracted',
          data,
          timestamp: new Date().toISOString(),
          topic: data.topic,
        };
        setLastEvent(event);
        handlers?.onWitnessEvent?.(event);
      });

      // Handle K-Block events
      const kblockHandler = (eventType: string) => (e: MessageEvent) => {
        const data = JSON.parse(e.data);
        const event: StreamEvent = {
          type: eventType,
          data,
          timestamp: new Date().toISOString(),
          topic: data.topic,
        };
        setLastEvent(event);
        handlers?.onKBlockChange?.(data);
        handlers?.onWitnessEvent?.(event);
      };

      eventSource.addEventListener('kblock_edited', kblockHandler('kblock_edited'));
      eventSource.addEventListener('kblock_saved', kblockHandler('kblock_saved'));
      eventSource.addEventListener('kblock_discarded', kblockHandler('kblock_discarded'));

      // Handle constitutional evaluation events
      eventSource.addEventListener('constitutional_evaluated', (e) => {
        const data = JSON.parse(e.data);
        const event: StreamEvent = {
          type: 'constitutional_evaluated',
          data,
          timestamp: new Date().toISOString(),
          topic: data.topic,
        };
        setLastEvent(event);
        handlers?.onWitnessEvent?.(event);
      });

      // Handle heartbeat
      eventSource.addEventListener('heartbeat', (e) => {
        const data = JSON.parse(e.data);
        setLastEvent({
          type: 'heartbeat',
          data,
          timestamp: new Date().toISOString(),
        });
      });

      // Generic message handler for any other events
      eventSource.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          const event: StreamEvent = {
            type: data.type || 'unknown',
            data: data.payload || data,
            timestamp: new Date().toISOString(),
            topic: data.topic,
          };
          setLastEvent(event);
          handlers?.onWitnessEvent?.(event);
        } catch {
          // Ignore parse errors for non-JSON messages
        }
      };
    } catch (err) {
      setStatus('disconnected');
      setError(err instanceof Error ? err.message : 'Failed to connect');
    }
  }, [url, handlers]);

  /**
   * Disconnect from the SSE stream.
   */
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    setStatus('disconnected');
  }, []);

  // Auto-connect on mount, cleanup on unmount
  // Connects to /api/witness/stream (the canonical SSE endpoint)
  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    status,
    lastEvent,
    error,
    connect,
    disconnect,
  };
}

export default useRealtimeStream;

// Export types for consumers
export type { StreamEvent, StreamHandlers, UseRealtimeStreamResult, WitnessEventType };
