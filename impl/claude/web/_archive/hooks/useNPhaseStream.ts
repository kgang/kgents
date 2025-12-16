/**
 * useNPhaseStream: N-Phase state extraction from Town SSE stream.
 *
 * Wave 5: N-Phase Native Integration
 * ===================================
 *
 * This hook provides N-Phase state by consuming SSE events from the
 * /v1/town/{id}/live endpoint when nphase_enabled=true.
 *
 * It extracts N-Phase context from:
 * - live.start: Initial N-Phase state
 * - live.nphase: Phase transitions
 * - live.state: Embedded N-Phase context
 * - live.end: Final N-Phase summary
 *
 * Design Decision: This hook manages its own EventSource rather than
 * sharing with useTownStreamWidget to keep concerns separate and allow
 * independent use of N-Phase tracking.
 *
 * Example:
 *   const { nphase, transitions, connect } = useNPhaseStream({
 *     townId: 'abc123',
 *     enabled: true,
 *     autoConnect: true,
 *   });
 */

import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import type {
  NPhaseType,
  NPhaseContext,
  NPhaseTransitionEvent,
  NPhaseState,
  NPhaseSummary,
} from '@/api/types';

// =============================================================================
// Types
// =============================================================================

interface UseNPhaseStreamOptions {
  /** Town ID to connect to */
  townId: string;
  /** Whether N-Phase tracking is enabled */
  enabled?: boolean;
  /** Playback speed multiplier (0.5-4.0) */
  speed?: number;
  /** Number of phases to run */
  phases?: number;
  /** Connect automatically on mount */
  autoConnect?: boolean;
  /** Callback on N-Phase transition */
  onTransition?: (transition: NPhaseTransitionEvent) => void;
  /** Callback when session starts */
  onStart?: (context: NPhaseContext) => void;
  /** Callback when session ends */
  onEnd?: (summary: NPhaseSummary) => void;
  /** Callback on error */
  onError?: (error: Event) => void;
}

interface UseNPhaseStreamResult {
  /** Current N-Phase state */
  nphase: NPhaseState;
  /** All recorded transitions */
  transitions: NPhaseTransitionEvent[];
  /** Whether connected to SSE stream */
  isConnected: boolean;
  /** Connect to stream */
  connect: () => void;
  /** Disconnect from stream */
  disconnect: () => void;
  /** Reset state (clear transitions) */
  reset: () => void;
}

// =============================================================================
// Initial State
// =============================================================================

const INITIAL_NPHASE_STATE: NPhaseState = {
  enabled: false,
  sessionId: null,
  currentPhase: 'UNDERSTAND',
  cycleCount: 0,
  checkpointCount: 0,
  handleCount: 0,
  transitions: [],
  isActive: false,
};

// =============================================================================
// Hook Implementation
// =============================================================================

export function useNPhaseStream({
  townId,
  enabled = true,
  speed = 1.0,
  phases = 4,
  autoConnect = false,
  onTransition,
  onStart,
  onEnd,
  onError,
}: UseNPhaseStreamOptions): UseNPhaseStreamResult {
  // State
  const [nphaseState, setNPhaseState] = useState<NPhaseState>(INITIAL_NPHASE_STATE);
  const [transitions, setTransitions] = useState<NPhaseTransitionEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  // Refs to avoid stale closures
  const eventSourceRef = useRef<EventSource | null>(null);
  const callbacksRef = useRef({ onTransition, onStart, onEnd, onError });
  callbacksRef.current = { onTransition, onStart, onEnd, onError };

  // Connect to SSE stream
  const connect = useCallback(() => {
    if (!townId || !enabled) {
      console.log('[N-Phase SSE] Skipping connect: townId or enabled missing');
      return;
    }

    // Close existing connection
    if (eventSourceRef.current) {
      console.log('[N-Phase SSE] Closing existing connection');
      eventSourceRef.current.close();
    }

    // Build URL with N-Phase enabled
    const url = `/v1/town/${townId}/live?speed=${speed}&phases=${phases}&nphase_enabled=true`;
    console.log('[N-Phase SSE] Connecting to:', url);

    const es = new EventSource(url);
    eventSourceRef.current = es;

    // Connection opened
    es.onopen = () => {
      console.log('[N-Phase SSE] Connected');
      setIsConnected(true);
    };

    // Handle live.start - extract initial N-Phase context
    es.addEventListener('live.start', (e) => {
      const data = JSON.parse(e.data);
      console.log('[N-Phase SSE] Start:', data);

      if (data.nphase) {
        const ctx: NPhaseContext = data.nphase;
        setNPhaseState({
          enabled: true,
          sessionId: ctx.session_id,
          currentPhase: ctx.current_phase,
          cycleCount: ctx.cycle_count,
          checkpointCount: ctx.checkpoint_count,
          handleCount: ctx.handle_count,
          transitions: [],
          isActive: true,
        });
        callbacksRef.current.onStart?.(ctx);
      }
    });

    // Handle live.nphase - phase transitions
    es.addEventListener('live.nphase', (e) => {
      const data = JSON.parse(e.data);
      console.log('[N-Phase SSE] Transition:', data);

      const transition: NPhaseTransitionEvent = {
        tick: data.tick,
        from_phase: data.from_phase as NPhaseType,
        to_phase: data.to_phase as NPhaseType,
        session_id: data.session_id,
        cycle_count: data.cycle_count,
        trigger: data.trigger,
        timestamp: new Date(),
      };

      // Update state
      setNPhaseState((prev) => ({
        ...prev,
        currentPhase: transition.to_phase,
        cycleCount: transition.cycle_count,
        transitions: [...prev.transitions, transition],
      }));

      // Add to transitions list
      setTransitions((prev) => [...prev, transition]);

      callbacksRef.current.onTransition?.(transition);
    });

    // Handle live.state - extract embedded N-Phase context
    es.addEventListener('live.state', (e) => {
      const data = JSON.parse(e.data);

      if (data.nphase) {
        const ctx = data.nphase;
        setNPhaseState((prev) => ({
          ...prev,
          currentPhase: ctx.current_phase,
          cycleCount: ctx.cycle_count,
          checkpointCount: ctx.checkpoint_count,
          handleCount: ctx.handle_count,
        }));
      }
    });

    // Handle live.end - final summary
    es.addEventListener('live.end', (e) => {
      const data = JSON.parse(e.data);
      console.log('[N-Phase SSE] End:', data);

      if (data.nphase_summary) {
        const summary: NPhaseSummary = data.nphase_summary;
        setNPhaseState((prev) => ({
          ...prev,
          currentPhase: summary.final_phase,
          cycleCount: summary.cycle_count,
          checkpointCount: summary.checkpoint_count,
          handleCount: summary.handle_count,
          isActive: false,
        }));
        callbacksRef.current.onEnd?.(summary);
      } else {
        setNPhaseState((prev) => ({ ...prev, isActive: false }));
      }
    });

    // Error handler
    es.onerror = (error) => {
      console.error('[N-Phase SSE] Error:', error);
      callbacksRef.current.onError?.(error);

      if (es.readyState === EventSource.CLOSED) {
        console.log('[N-Phase SSE] Connection closed');
        setIsConnected(false);
        setNPhaseState((prev) => ({ ...prev, isActive: false }));
      }
    };
  }, [townId, enabled, speed, phases]);

  // Disconnect from stream
  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      console.log('[N-Phase SSE] Disconnecting');
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
      setNPhaseState((prev) => ({ ...prev, isActive: false }));
    }
  }, []);

  // Reset state
  const reset = useCallback(() => {
    setNPhaseState(INITIAL_NPHASE_STATE);
    setTransitions([]);
  }, []);

  // Auto-connect effect
  useEffect(() => {
    if (autoConnect && townId && enabled) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, townId, enabled, connect, disconnect]);

  // Memoized result
  const result = useMemo(
    () => ({
      nphase: nphaseState,
      transitions,
      isConnected,
      connect,
      disconnect,
      reset,
    }),
    [nphaseState, transitions, isConnected, connect, disconnect, reset]
  );

  return result;
}

// =============================================================================
// Utility Hook: Extract N-Phase from existing Town stream
// =============================================================================

/**
 * Extract N-Phase state from ColonyDashboardJSON.
 *
 * Use this when you already have a useTownStreamWidget connection
 * and want to extract N-Phase data from live.state events.
 */
export function useNPhaseFromDashboard(
  dashboard: { nphase?: NPhaseContext } | null
): NPhaseState | null {
  const [state, setState] = useState<NPhaseState | null>(null);

  useEffect(() => {
    if (dashboard?.nphase) {
      const ctx = dashboard.nphase;
      setState((prev) => ({
        enabled: true,
        sessionId: ctx.session_id,
        currentPhase: ctx.current_phase,
        cycleCount: ctx.cycle_count,
        checkpointCount: ctx.checkpoint_count,
        handleCount: ctx.handle_count,
        transitions: prev?.transitions || [],
        isActive: true,
      }));
    }
  }, [dashboard]);

  return state;
}

// =============================================================================
// Exports
// =============================================================================

export type { UseNPhaseStreamOptions, UseNPhaseStreamResult };
export { INITIAL_NPHASE_STATE };
