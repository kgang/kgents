/**
 * useWitnessStream — Real-time SSE connection to witness events
 *
 * Connects to /api/witness/stream and emits events as they arrive.
 * Handles reconnection and connection status.
 *
 * "The proof IS the decision."
 */

import { useCallback, useEffect, useRef, useState } from 'react';

// =============================================================================
// Types
// =============================================================================

export type WitnessEventType = 'mark' | 'thought' | 'crystal' | 'heartbeat' | 'connected';

export interface WitnessEvent {
  id: string;
  type: WitnessEventType;
  timestamp: Date;

  // Mark fields
  action?: string;
  reasoning?: string;
  principles?: string[];
  author?: string;

  // Thought fields
  content?: string;
  source?: string;
  tags?: string[];

  // Crystal fields
  level?: string;
  insight?: string;
  significance?: number;
}

export interface UseWitnessStream {
  events: WitnessEvent[];
  connected: boolean;
  reconnect: () => void;
  clear: () => void;
}

// =============================================================================
// Hook
// =============================================================================

const MAX_EVENTS = 100;
const RECONNECT_DELAY = 3000;

export function useWitnessStream(): UseWitnessStream {
  const [events, setEvents] = useState<WitnessEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    // Clean up existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    const eventSource = new EventSource('/api/witness/stream');
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setConnected(true);
      // Add connection event
      const connectionEvent: WitnessEvent = {
        id: `conn-${Date.now()}`,
        type: 'connected',
        timestamp: new Date(),
        content: 'Witness stream connected',
      };
      setEvents((prev) => [connectionEvent, ...prev].slice(0, MAX_EVENTS));
    };

    eventSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);

        // Skip heartbeats in the event list (but they confirm connection)
        if (data.type === 'heartbeat') {
          return;
        }

        const event: WitnessEvent = {
          id: data.id || `evt-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
          type: data.type || 'mark',
          timestamp: new Date(data.timestamp || Date.now()),
          action: data.action,
          reasoning: data.reasoning,
          principles: data.principles,
          author: data.author,
          content: data.content,
          source: data.source,
          tags: data.tags,
          level: data.level,
          insight: data.insight,
          significance: data.significance,
        };

        setEvents((prev) => [event, ...prev].slice(0, MAX_EVENTS));
      } catch (error) {
        console.error('Failed to parse witness event:', error);
      }
    };

    eventSource.onerror = () => {
      setConnected(false);
      eventSource.close();

      // Attempt reconnection
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, RECONNECT_DELAY);
    };
  }, []);

  const reconnect = useCallback(() => {
    connect();
  }, [connect]);

  const clear = useCallback(() => {
    setEvents([]);
  }, []);

  // Connect on mount
  useEffect(() => {
    connect();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  return {
    events,
    connected,
    reconnect,
    clear,
  };
}
