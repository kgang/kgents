/**
 * useTownStreamWidget: Widget-focused SSE streaming for Agent Town.
 *
 * Phase 3: SSE Integration
 * ========================
 *
 * This hook provides a clean interface for consuming the `live.state` SSE events
 * that contain full ColonyDashboardJSON projections from the backend.
 *
 * Unlike useTownStream (which builds state incrementally from events),
 * this hook receives pre-rendered widget state from the server.
 *
 * Features:
 * - Receives `live.state` events with full ColonyDashboardJSON
 * - Accumulates `live.event` events for activity timeline
 * - Tracks connection and playback state
 * - Provides connect/disconnect control
 *
 * Example:
 *   const { dashboard, events, isConnected, connect } = useTownStreamWidget({
 *     townId: 'abc123',
 *     autoConnect: true,
 *   });
 *
 * See Also:
 *   - useTownStream.ts: Incremental state building (legacy)
 *   - types.ts: ColonyDashboardJSON type definition
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import type { ColonyDashboardJSON } from '@/reactive/types';
import type { TownEvent } from '@/api/types';

// =============================================================================
// Types
// =============================================================================

interface UseTownStreamWidgetOptions {
  /** Town ID to connect to */
  townId: string;
  /** Playback speed multiplier (0.5-4.0, default 1.0) */
  speed?: number;
  /** Number of phases to run (default 4 = one day) */
  phases?: number;
  /** Connect automatically on mount */
  autoConnect?: boolean;
  /** Callback when an event is received */
  onEvent?: (event: TownEvent) => void;
  /** Callback when dashboard state updates */
  onDashboard?: (dashboard: ColonyDashboardJSON) => void;
  /** Callback on connection open */
  onConnect?: () => void;
  /** Callback on connection close */
  onDisconnect?: () => void;
  /** Callback on error */
  onError?: (error: Event) => void;
}

interface UseTownStreamWidgetResult {
  /** Current dashboard state from live.state events */
  dashboard: ColonyDashboardJSON | null;
  /** Recent events from live.event (most recent first, max 100) */
  events: TownEvent[];
  /** Whether EventSource is connected */
  isConnected: boolean;
  /** Whether simulation is actively playing */
  isPlaying: boolean;
  /** Connect to SSE stream */
  connect: () => void;
  /** Disconnect from SSE stream */
  disconnect: () => void;
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useTownStreamWidget({
  townId,
  speed = 1.0,
  phases = 4,
  autoConnect = false,
  onEvent,
  onDashboard,
  onConnect,
  onDisconnect,
  onError,
}: UseTownStreamWidgetOptions): UseTownStreamWidgetResult {
  // State
  const [dashboard, setDashboard] = useState<ColonyDashboardJSON | null>(null);
  const [events, setEvents] = useState<TownEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  // Refs to avoid stale closures in event handlers
  const eventSourceRef = useRef<EventSource | null>(null);
  const callbacksRef = useRef({ onEvent, onDashboard, onConnect, onDisconnect, onError });
  callbacksRef.current = { onEvent, onDashboard, onConnect, onDisconnect, onError };

  // Connect to SSE stream
  const connect = useCallback(() => {
    if (!townId) {
      console.log('[SSE Widget] No townId, skipping connect');
      return;
    }

    // Close existing connection
    if (eventSourceRef.current) {
      console.log('[SSE Widget] Closing existing connection');
      eventSourceRef.current.close();
    }

    // Build URL with query params
    const url = `/v1/town/${townId}/live?speed=${speed}&phases=${phases}`;
    console.log('[SSE Widget] Connecting to:', url);

    const es = new EventSource(url);
    eventSourceRef.current = es;

    // Connection opened
    es.onopen = () => {
      console.log('[SSE Widget] Connected');
      setIsConnected(true);
      callbacksRef.current.onConnect?.();
    };

    // Handle live.start event
    es.addEventListener('live.start', (e) => {
      const data = JSON.parse(e.data);
      console.log('[SSE Widget] Stream started:', data);
      setIsPlaying(true);
    });

    // Handle live.state event (main dashboard state)
    es.addEventListener('live.state', (e) => {
      const state: ColonyDashboardJSON = JSON.parse(e.data);
      console.log('[SSE Widget] State update:', state.citizens?.length ?? 0, 'citizens');
      setDashboard(state);
      callbacksRef.current.onDashboard?.(state);
    });

    // Handle live.event event (individual simulation events)
    es.addEventListener('live.event', (e) => {
      const event: TownEvent = JSON.parse(e.data);
      console.log('[SSE Widget] Event:', event.operation, event.participants);

      // Prepend to events (most recent first), keep max 100
      setEvents((prev) => [event, ...prev.slice(0, 99)]);
      callbacksRef.current.onEvent?.(event);
    });

    // Handle live.phase event (phase transitions)
    es.addEventListener('live.phase', (e) => {
      const data = JSON.parse(e.data);
      console.log('[SSE Widget] Phase change:', data.phase);
    });

    // Handle live.end event
    es.addEventListener('live.end', (e) => {
      const data = JSON.parse(e.data);
      console.log('[SSE Widget] Stream ended:', data);
      setIsPlaying(false);
      callbacksRef.current.onDisconnect?.();
    });

    // Error handler
    es.onerror = (error) => {
      console.error('[SSE Widget] Error:', error);
      callbacksRef.current.onError?.(error);

      if (es.readyState === EventSource.CLOSED) {
        console.log('[SSE Widget] Connection closed');
        setIsConnected(false);
        setIsPlaying(false);
        callbacksRef.current.onDisconnect?.();
      }
    };
  }, [townId, speed, phases]);

  // Disconnect from SSE stream
  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      console.log('[SSE Widget] Disconnecting');
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
      setIsPlaying(false);
      callbacksRef.current.onDisconnect?.();
    }
  }, []);

  // Auto-connect effect
  useEffect(() => {
    if (autoConnect && townId) {
      connect();
    }

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [autoConnect, townId, connect, disconnect]);

  return {
    dashboard,
    events,
    isConnected,
    isPlaying,
    connect,
    disconnect,
  };
}

// =============================================================================
// Exports
// =============================================================================

export type { UseTownStreamWidgetOptions, UseTownStreamWidgetResult };
