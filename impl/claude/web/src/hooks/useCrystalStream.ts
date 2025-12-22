/**
 * useCrystalStream - Real-time crystal event subscription hook.
 *
 * Subscribes to the witness crystal stream via SSE and provides
 * a reactive interface for new crystal events.
 *
 * Features:
 * - Auto-reconnect on connection loss
 * - Level filtering
 * - Event buffering for batch updates
 * - Connection status tracking
 *
 * @see spec/protocols/witness-crystallization.md
 * @see services/witness/stream.py
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  subscribeToCrystalStream,
  type CrystalEvent,
  type CrystalLevel,
} from '../api/crystal';

// =============================================================================
// Types
// =============================================================================

export type StreamStatus = 'disconnected' | 'connecting' | 'connected' | 'reconnecting' | 'error';

export interface CrystalStreamState {
  /** Connection status */
  status: StreamStatus;
  /** Recent events (limited buffer) */
  events: CrystalEvent[];
  /** Last event received */
  lastEvent: CrystalEvent | null;
  /** Error message if status is 'error' */
  error: string | null;
  /** Total events received this session */
  eventCount: number;
  /** Last heartbeat timestamp */
  lastHeartbeat: Date | null;
}

export interface UseCrystalStreamOptions {
  /** Filter to specific level */
  level?: CrystalLevel;
  /** Max events to keep in buffer (default: 50) */
  bufferSize?: number;
  /** Auto-connect on mount (default: true) */
  autoConnect?: boolean;
  /** Reconnect delay in ms (default: 3000) */
  reconnectDelay?: number;
}

export interface UseCrystalStreamReturn extends CrystalStreamState {
  /** Connect to stream */
  connect: () => void;
  /** Disconnect from stream */
  disconnect: () => void;
  /** Clear event buffer */
  clearEvents: () => void;
  /** Whether currently connected */
  isConnected: boolean;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook for subscribing to crystal stream.
 *
 * @example
 * ```tsx
 * const { status, events, lastEvent, connect, disconnect } = useCrystalStream({
 *   level: 'SESSION',
 *   bufferSize: 100,
 * });
 *
 * useEffect(() => {
 *   if (lastEvent?.type === 'crystal.created') {
 *     console.log('New crystal:', lastEvent.data);
 *   }
 * }, [lastEvent]);
 * ```
 */
export function useCrystalStream(
  options: UseCrystalStreamOptions = {}
): UseCrystalStreamReturn {
  const {
    level,
    bufferSize = 50,
    autoConnect = true,
    reconnectDelay = 3000,
  } = options;

  // State
  const [state, setState] = useState<CrystalStreamState>({
    status: 'disconnected',
    events: [],
    lastEvent: null,
    error: null,
    eventCount: 0,
    lastHeartbeat: null,
  });

  // Refs for cleanup and reconnection
  const cleanupRef = useRef<(() => void) | null>(null);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  /**
   * Handle incoming event.
   */
  const handleEvent = useCallback((event: CrystalEvent) => {
    if (!mountedRef.current) return;

    setState((prev) => {
      // Update heartbeat if it's a heartbeat event
      if (event.type === 'heartbeat') {
        return {
          ...prev,
          status: 'connected',
          lastHeartbeat: new Date(),
        };
      }

      // Add to buffer (newest first)
      const newEvents = [event, ...prev.events].slice(0, bufferSize);

      return {
        ...prev,
        status: 'connected',
        events: newEvents,
        lastEvent: event,
        eventCount: prev.eventCount + 1,
        error: null,
      };
    });
  }, [bufferSize]);

  /**
   * Handle connection error.
   */
  const handleError = useCallback((error: Error) => {
    if (!mountedRef.current) return;

    setState((prev) => ({
      ...prev,
      status: 'error',
      error: error.message,
    }));

    // Schedule reconnection
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
    }

    reconnectTimerRef.current = setTimeout(() => {
      if (mountedRef.current) {
        setState((prev) => ({ ...prev, status: 'reconnecting' }));
        connect();
      }
    }, reconnectDelay);
  }, [reconnectDelay]);

  /**
   * Connect to stream.
   */
  const connect = useCallback(() => {
    // Cleanup existing connection
    if (cleanupRef.current) {
      cleanupRef.current();
      cleanupRef.current = null;
    }

    // Clear any pending reconnect
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }

    setState((prev) => ({
      ...prev,
      status: 'connecting',
      error: null,
    }));

    // Subscribe to stream
    cleanupRef.current = subscribeToCrystalStream(
      handleEvent,
      handleError,
      level
    );
  }, [level, handleEvent, handleError]);

  /**
   * Disconnect from stream.
   */
  const disconnect = useCallback(() => {
    if (cleanupRef.current) {
      cleanupRef.current();
      cleanupRef.current = null;
    }

    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }

    setState((prev) => ({
      ...prev,
      status: 'disconnected',
      error: null,
    }));
  }, []);

  /**
   * Clear event buffer.
   */
  const clearEvents = useCallback(() => {
    setState((prev) => ({
      ...prev,
      events: [],
      lastEvent: null,
      eventCount: 0,
    }));
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    mountedRef.current = true;

    if (autoConnect) {
      connect();
    }

    return () => {
      mountedRef.current = false;
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  // Reconnect when level filter changes
  useEffect(() => {
    if (state.status === 'connected' || state.status === 'connecting') {
      connect();
    }
  }, [level]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    ...state,
    connect,
    disconnect,
    clearEvents,
    isConnected: state.status === 'connected',
  };
}

// =============================================================================
// Exports
// =============================================================================

export default useCrystalStream;
