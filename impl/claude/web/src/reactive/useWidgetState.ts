/**
 * React hook for managing widget JSON projection state.
 *
 * This hook bridges the Python reactive substrate to React:
 * - Receives JSON projections from SSE/WebSocket
 * - Provides type-safe state management
 * - Enables optimistic updates
 *
 * @example
 * ```tsx
 * const [dashboard, updateDashboard] = useWidgetState<ColonyDashboardJSON>({
 *   initialState: initialDashboard,
 *   onUpdate: (state) => console.log('Dashboard updated:', state.colony_id),
 * });
 * ```
 */

import { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import type { WidgetJSON } from './types';

// =============================================================================
// Types
// =============================================================================

export interface UseWidgetStateOptions<T extends WidgetJSON> {
  /** Initial state for the widget */
  initialState: T;
  /** Callback when state changes */
  onUpdate?: (state: T) => void;
  /** Equality function for determining if state changed (default: shallow) */
  isEqual?: (a: T, b: T) => boolean;
}

export interface UseWidgetStateResult<T extends WidgetJSON> {
  /** Current widget state */
  state: T;
  /** Update state (full replacement or functional update) */
  updateState: (updater: T | ((prev: T) => T)) => void;
  /** Patch state (partial update, merged with current) */
  patchState: (patch: Partial<T>) => void;
  /** Reset to initial state */
  reset: () => void;
  /** Generation counter (increments on each update) */
  generation: number;
}

// =============================================================================
// Default Equality
// =============================================================================

/**
 * Shallow equality check for widget state.
 * Sufficient for immutable JSON projections.
 */
function shallowEqual<T extends WidgetJSON>(a: T, b: T): boolean {
  if (a === b) return true;
  if (a.type !== b.type) return false;

  const keysA = Object.keys(a);
  const keysB = Object.keys(b);

  if (keysA.length !== keysB.length) return false;

  for (const key of keysA) {
    // Use unknown intermediate to satisfy TypeScript's strict checks
    if (
      (a as unknown as Record<string, unknown>)[key] !==
      (b as unknown as Record<string, unknown>)[key]
    ) {
      return false;
    }
  }

  return true;
}

// =============================================================================
// Hook Implementation
// =============================================================================

/**
 * Hook for managing widget JSON projection state.
 *
 * Features:
 * - Type-safe state with discriminated union narrowing
 * - Generation counter for change detection
 * - Partial updates via patchState
 * - Reset to initial state
 * - Equality check to prevent unnecessary re-renders
 */
export function useWidgetState<T extends WidgetJSON>(
  options: UseWidgetStateOptions<T>
): UseWidgetStateResult<T> {
  const { initialState, onUpdate, isEqual = shallowEqual } = options;

  const [state, setState] = useState<T>(initialState);
  const [generation, setGeneration] = useState(0);
  const initialRef = useRef(initialState);

  // Update handlers ref to avoid stale closures
  const handlersRef = useRef({ onUpdate, isEqual });
  handlersRef.current = { onUpdate, isEqual };

  const updateState = useCallback((updater: T | ((prev: T) => T)) => {
    setState((prev) => {
      const next = typeof updater === 'function' ? updater(prev) : updater;

      // Skip if equal
      if (handlersRef.current.isEqual(prev, next)) {
        return prev;
      }

      // Increment generation on actual change
      setGeneration((g) => g + 1);

      // Notify callback
      handlersRef.current.onUpdate?.(next);

      return next;
    });
  }, []);

  const patchState = useCallback(
    (patch: Partial<T>) => {
      updateState((prev) => ({ ...prev, ...patch }));
    },
    [updateState]
  );

  const reset = useCallback(() => {
    setState(initialRef.current);
    setGeneration((g) => g + 1);
  }, []);

  return useMemo(
    () => ({
      state,
      updateState,
      patchState,
      reset,
      generation,
    }),
    [state, updateState, patchState, reset, generation]
  );
}

// =============================================================================
// SSE Integration Hook
// =============================================================================

export interface UseWidgetStreamOptions<T extends WidgetJSON> {
  /** URL for SSE endpoint */
  url: string;
  /** Initial state before first SSE message */
  initialState: T;
  /** SSE event name for state updates (default: 'live.state') */
  eventName?: string;
  /** Auto-connect on mount */
  autoConnect?: boolean;
  /** Callback on connection */
  onConnect?: () => void;
  /** Callback on disconnect */
  onDisconnect?: () => void;
  /** Callback on error */
  onError?: (error: Event) => void;
}

export interface UseWidgetStreamResult<T extends WidgetJSON> extends UseWidgetStateResult<T> {
  /** Connect to SSE stream */
  connect: () => void;
  /** Disconnect from SSE stream */
  disconnect: () => void;
  /** Whether currently connected */
  isConnected: boolean;
}

/**
 * Hook for streaming widget state via SSE.
 *
 * Combines useWidgetState with SSE streaming:
 * - Connects to SSE endpoint
 * - Parses JSON projection events
 * - Updates state on each event
 *
 * @example
 * ```tsx
 * const { state, isConnected, connect, disconnect } = useWidgetStream<ColonyDashboardJSON>({
 *   url: `/v1/town/${townId}/live`,
 *   initialState: emptyDashboard,
 *   eventName: 'live.state',
 * });
 * ```
 */
export function useWidgetStream<T extends WidgetJSON>(
  options: UseWidgetStreamOptions<T>
): UseWidgetStreamResult<T> {
  const {
    url,
    initialState,
    eventName = 'live.state',
    autoConnect = false,
    onConnect,
    onDisconnect,
    onError,
  } = options;

  const widgetState = useWidgetState<T>({ initialState });
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Store handlers in ref to avoid stale closures
  const handlersRef = useRef({ onConnect, onDisconnect, onError });
  handlersRef.current = { onConnect, onDisconnect, onError };

  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      handlersRef.current.onConnect?.();
    };

    eventSource.addEventListener(eventName, (e) => {
      try {
        const data = JSON.parse(e.data) as T;
        widgetState.updateState(data);
      } catch (err) {
        console.error('[useWidgetStream] Failed to parse event:', err);
      }
    });

    eventSource.onerror = (error) => {
      handlersRef.current.onError?.(error);
      if (eventSource.readyState === EventSource.CLOSED) {
        setIsConnected(false);
        handlersRef.current.onDisconnect?.();
      }
    };
  }, [url, eventName, widgetState]);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
      handlersRef.current.onDisconnect?.();
    }
  }, []);

  // Auto-connect on mount if enabled
  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return useMemo(
    () => ({
      ...widgetState,
      connect,
      disconnect,
      isConnected,
    }),
    [widgetState, connect, disconnect, isConnected]
  );
}
