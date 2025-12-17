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
import { useBatchedEvents } from './useBatchedEvents';

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
  /** Whether to enable N-Phase tracking */
  nphaseEnabled?: boolean;
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
  /** Event batching delay in ms (default: 50) */
  batchDelay?: number;
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
  nphaseEnabled = false,
  autoConnect = false,
  onEvent,
  onDashboard,
  onConnect,
  onDisconnect,
  onError,
  batchDelay = 50,
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

  // Batched event handler - reduces render frequency by ~50%
  const addBatchedEvent = useBatchedEvents<TownEvent>(
    useCallback((batch) => {
      // Process batch: prepend to events (most recent first), keep max 100
      setEvents((prev) => {
        const combined = [...batch.reverse(), ...prev];
        return combined.slice(0, 100);
      });
      // Call individual callbacks for each event
      batch.forEach((event) => {
        callbacksRef.current.onEvent?.(event);
      });
    }, []),
    batchDelay
  );

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

    // Build URL with query params - uses AUP town events endpoint
    // Include API key as query param since EventSource can't send headers
    const apiKey = localStorage.getItem('api_key') || 'kg_dev_bob';
    const url = `/api/v1/town/${townId}/events?speed=${speed}&phases=${phases}&nphase_enabled=${nphaseEnabled}&api_key=${apiKey}`;
    console.log('[SSE Widget] Connecting to:', url);

    const es = new EventSource(url);
    eventSourceRef.current = es;

    // Connection opened
    es.onopen = () => {
      console.log('[SSE Widget] Connected');
      setIsConnected(true);
      setIsPlaying(true);
      callbacksRef.current.onConnect?.();
    };

    // Handle town.status event (initial status from AUP)
    es.addEventListener('town.status', (e) => {
      const data = JSON.parse(e.data);
      console.log('[SSE Widget] Status:', data);
      // Transform status into partial dashboard state
      setDashboard((prev) => ({
        ...prev,
        phase: data.phase || 'MORNING',
        day: data.day || 1,
        citizens: prev?.citizens || [],
      } as ColonyDashboardJSON));
    });

    // Handle town.isometric event (widget state with citizens from AUP)
    es.addEventListener('town.isometric', (e) => {
      const widget = JSON.parse(e.data);
      console.log('[SSE Widget] Isometric update:', widget.citizens?.length ?? 0, 'citizens');
      // Transform isometric widget data into ColonyDashboardJSON
      const dashboardState: ColonyDashboardJSON = {
        type: 'colony_dashboard',
        colony_id: townId,
        phase: widget.phase || 'MORNING',
        day: widget.day || 1,
        grid_cols: 3,
        selected_citizen_id: null,
        citizens: (widget.citizens || []).map((c: any) => ({
          citizen_id: c.id || c.citizen_id,
          name: c.name,
          archetype: c.archetype,
          region: c.region,
          phase: c.phase,
          position: c.position || { x: 0, y: 0 },
          energy: c.energy ?? 1.0,
          mood: c.mood ?? 0.5,
        })),
        metrics: widget.metrics || { tension: 0, cooperation: 0, accursed_surplus: 0 },
      };
      setDashboard(dashboardState);
      callbacksRef.current.onDashboard?.(dashboardState);
    });

    // Handle town.event event (individual simulation events from AUP)
    // Uses batched handler to reduce render frequency
    es.addEventListener('town.event', (e) => {
      const event: TownEvent = JSON.parse(e.data);
      console.log('[SSE Widget] Event:', event.operation, event.participants);
      addBatchedEvent(event);
    });

    // Legacy event names for compatibility
    es.addEventListener('live.state', (e) => {
      const state: ColonyDashboardJSON = JSON.parse(e.data);
      console.log('[SSE Widget] Live state update:', state.citizens?.length ?? 0, 'citizens');
      setDashboard(state);
      callbacksRef.current.onDashboard?.(state);
    });

    es.addEventListener('live.event', (e) => {
      const event: TownEvent = JSON.parse(e.data);
      addBatchedEvent(event);
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
  }, [townId, speed, phases, nphaseEnabled, addBatchedEvent]);

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
