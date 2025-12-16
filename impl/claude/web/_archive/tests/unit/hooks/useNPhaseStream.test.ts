/**
 * Tests for useNPhaseStream hook.
 *
 * Wave 5: N-Phase Native Integration
 * ==================================
 *
 * Test Categories:
 * - Initialization: hook starts with correct initial state
 * - Connection: connect/disconnect behavior
 * - Events: handling live.start, live.nphase, live.state, live.end
 * - State Management: N-Phase state and transitions
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useNPhaseStream, INITIAL_NPHASE_STATE } from '@/hooks/useNPhaseStream';
import type { NPhaseContext, NPhaseSummary } from '@/api/types';

// =============================================================================
// Mock EventSource
// =============================================================================

type EventListener = (e: MessageEvent) => void;

class MockEventSource {
  static instances: MockEventSource[] = [];

  url: string;
  listeners: Map<string, EventListener[]> = new Map();
  onopen: (() => void) | null = null;
  onerror: ((e: Event) => void) | null = null;
  readyState = 0; // CONNECTING

  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSED = 2;

  constructor(url: string) {
    this.url = url;
    MockEventSource.instances.push(this);
  }

  addEventListener(type: string, listener: EventListener) {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type)!.push(listener);
  }

  emit(type: string, data: unknown) {
    const event = { data: JSON.stringify(data) } as MessageEvent;
    this.listeners.get(type)?.forEach((l) => l(event));
  }

  simulateOpen() {
    this.readyState = MockEventSource.OPEN;
    this.onopen?.();
  }

  simulateError() {
    this.readyState = MockEventSource.CLOSED;
    this.onerror?.({} as Event);
  }

  close() {
    this.readyState = MockEventSource.CLOSED;
  }
}

// =============================================================================
// Test Setup
// =============================================================================

describe('useNPhaseStream', () => {
  beforeEach(() => {
    MockEventSource.instances = [];
    vi.stubGlobal('EventSource', MockEventSource);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  // ===========================================================================
  // Initialization Tests
  // ===========================================================================

  describe('initialization', () => {
    it('initializes with default N-Phase state', () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town' })
      );

      expect(result.current.nphase).toEqual(INITIAL_NPHASE_STATE);
    });

    it('initializes with empty transitions array', () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town' })
      );

      expect(result.current.transitions).toEqual([]);
    });

    it('initializes with isConnected=false', () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town' })
      );

      expect(result.current.isConnected).toBe(false);
    });

    it('initializes with isActive=false', () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town' })
      );

      expect(result.current.nphase.isActive).toBe(false);
    });
  });

  // ===========================================================================
  // Connection Tests
  // ===========================================================================

  describe('connection', () => {
    it('connects when connect() is called', () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town' })
      );

      act(() => result.current.connect());

      expect(MockEventSource.instances).toHaveLength(1);
      expect(MockEventSource.instances[0].url).toContain('test-town');
    });

    it('includes nphase_enabled=true in URL', () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town' })
      );

      act(() => result.current.connect());

      const url = MockEventSource.instances[0].url;
      expect(url).toContain('nphase_enabled=true');
    });

    it('includes speed and phases in URL', () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town', speed: 2.0, phases: 8 })
      );

      act(() => result.current.connect());

      const url = MockEventSource.instances[0].url;
      expect(url).toContain('speed=2');
      expect(url).toContain('phases=8');
    });

    it('sets isConnected=true when connection opens', async () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town' })
      );

      act(() => result.current.connect());

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      await waitFor(() => {
        expect(result.current.isConnected).toBe(true);
      });
    });

    it('auto-connects when autoConnect=true', () => {
      renderHook(() =>
        useNPhaseStream({ townId: 'test-town', autoConnect: true })
      );

      expect(MockEventSource.instances).toHaveLength(1);
    });

    it('does not auto-connect when autoConnect=false', () => {
      renderHook(() =>
        useNPhaseStream({ townId: 'test-town', autoConnect: false })
      );

      expect(MockEventSource.instances).toHaveLength(0);
    });

    it('does not connect when enabled=false', () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town', enabled: false })
      );

      act(() => result.current.connect());

      expect(MockEventSource.instances).toHaveLength(0);
    });

    it('disconnects when disconnect() is called', () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town' })
      );

      act(() => result.current.connect());
      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      act(() => result.current.disconnect());

      expect(es.readyState).toBe(MockEventSource.CLOSED);
    });

    it('sets isConnected=false after disconnect', async () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town' })
      );

      act(() => result.current.connect());
      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      await waitFor(() => expect(result.current.isConnected).toBe(true));

      act(() => result.current.disconnect());

      await waitFor(() => {
        expect(result.current.isConnected).toBe(false);
      });
    });
  });

  // ===========================================================================
  // Event Handling Tests
  // ===========================================================================

  describe('event handling', () => {
    it('updates state on live.start with N-Phase context', async () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      const nphaseContext: NPhaseContext = {
        session_id: 'session-123',
        current_phase: 'UNDERSTAND',
        cycle_count: 1,
        checkpoint_count: 0,
        handle_count: 5,
      };

      act(() =>
        es.emit('live.start', {
          town_id: 'test-town',
          nphase: nphaseContext,
        })
      );

      await waitFor(() => {
        expect(result.current.nphase.enabled).toBe(true);
        expect(result.current.nphase.sessionId).toBe('session-123');
        expect(result.current.nphase.currentPhase).toBe('UNDERSTAND');
        expect(result.current.nphase.isActive).toBe(true);
      });
    });

    it('updates state on live.nphase transition', async () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      // First, set initial state
      act(() =>
        es.emit('live.start', {
          town_id: 'test-town',
          nphase: {
            session_id: 'session-123',
            current_phase: 'UNDERSTAND',
            cycle_count: 1,
            checkpoint_count: 0,
            handle_count: 5,
          },
        })
      );

      // Then emit transition
      act(() =>
        es.emit('live.nphase', {
          tick: 10,
          from_phase: 'UNDERSTAND',
          to_phase: 'ACT',
          session_id: 'session-123',
          cycle_count: 2,
          trigger: 'checkpoint',
        })
      );

      await waitFor(() => {
        expect(result.current.nphase.currentPhase).toBe('ACT');
        expect(result.current.nphase.cycleCount).toBe(2);
        expect(result.current.transitions).toHaveLength(1);
        expect(result.current.transitions[0].from_phase).toBe('UNDERSTAND');
        expect(result.current.transitions[0].to_phase).toBe('ACT');
      });
    });

    it('accumulates transitions', async () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      act(() => {
        es.emit('live.nphase', {
          tick: 10,
          from_phase: 'UNDERSTAND',
          to_phase: 'ACT',
          session_id: 'session-123',
          cycle_count: 1,
          trigger: 'checkpoint',
        });
        es.emit('live.nphase', {
          tick: 20,
          from_phase: 'ACT',
          to_phase: 'REFLECT',
          session_id: 'session-123',
          cycle_count: 1,
          trigger: 'completion',
        });
      });

      await waitFor(() => {
        expect(result.current.transitions).toHaveLength(2);
      });
    });

    it('updates counters on live.state', async () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      act(() =>
        es.emit('live.state', {
          nphase: {
            current_phase: 'ACT',
            cycle_count: 3,
            checkpoint_count: 5,
            handle_count: 10,
          },
        })
      );

      await waitFor(() => {
        expect(result.current.nphase.currentPhase).toBe('ACT');
        expect(result.current.nphase.cycleCount).toBe(3);
        expect(result.current.nphase.checkpointCount).toBe(5);
        expect(result.current.nphase.handleCount).toBe(10);
      });
    });

    it('updates state on live.end with summary', async () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      const summary: NPhaseSummary = {
        session_id: 'session-123',
        current_phase: 'REFLECT',
        final_phase: 'REFLECT',
        cycle_count: 4,
        checkpoint_count: 10,
        handle_count: 25,
        ledger_entries: 50,
      };

      act(() =>
        es.emit('live.end', {
          town_id: 'test-town',
          nphase_summary: summary,
        })
      );

      await waitFor(() => {
        expect(result.current.nphase.currentPhase).toBe('REFLECT');
        expect(result.current.nphase.cycleCount).toBe(4);
        expect(result.current.nphase.isActive).toBe(false);
      });
    });

    it('sets isActive=false on live.end without summary', async () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      // First activate
      act(() =>
        es.emit('live.start', {
          town_id: 'test-town',
          nphase: {
            session_id: 'session-123',
            current_phase: 'UNDERSTAND',
            cycle_count: 1,
            checkpoint_count: 0,
            handle_count: 5,
          },
        })
      );

      await waitFor(() => expect(result.current.nphase.isActive).toBe(true));

      act(() => es.emit('live.end', { status: 'completed' }));

      await waitFor(() => {
        expect(result.current.nphase.isActive).toBe(false);
      });
    });
  });

  // ===========================================================================
  // Callback Tests
  // ===========================================================================

  describe('callbacks', () => {
    it('calls onStart when live.start received with N-Phase', async () => {
      const onStart = vi.fn();
      renderHook(() =>
        useNPhaseStream({ townId: 'test-town', autoConnect: true, onStart })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      const nphaseContext: NPhaseContext = {
        session_id: 'session-123',
        current_phase: 'UNDERSTAND',
        cycle_count: 1,
        checkpoint_count: 0,
        handle_count: 5,
      };

      act(() =>
        es.emit('live.start', {
          town_id: 'test-town',
          nphase: nphaseContext,
        })
      );

      await waitFor(() => {
        expect(onStart).toHaveBeenCalledWith(nphaseContext);
      });
    });

    it('calls onTransition for each live.nphase event', async () => {
      const onTransition = vi.fn();
      renderHook(() =>
        useNPhaseStream({ townId: 'test-town', autoConnect: true, onTransition })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      act(() =>
        es.emit('live.nphase', {
          tick: 10,
          from_phase: 'UNDERSTAND',
          to_phase: 'ACT',
          session_id: 'session-123',
          cycle_count: 1,
          trigger: 'checkpoint',
        })
      );

      await waitFor(() => {
        expect(onTransition).toHaveBeenCalledTimes(1);
        expect(onTransition).toHaveBeenCalledWith(
          expect.objectContaining({
            from_phase: 'UNDERSTAND',
            to_phase: 'ACT',
          })
        );
      });
    });

    it('calls onEnd when live.end received with summary', async () => {
      const onEnd = vi.fn();
      renderHook(() =>
        useNPhaseStream({ townId: 'test-town', autoConnect: true, onEnd })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      const summary: NPhaseSummary = {
        session_id: 'session-123',
        current_phase: 'REFLECT',
        final_phase: 'REFLECT',
        cycle_count: 4,
        checkpoint_count: 10,
        handle_count: 25,
        ledger_entries: 50,
      };

      act(() =>
        es.emit('live.end', {
          town_id: 'test-town',
          nphase_summary: summary,
        })
      );

      await waitFor(() => {
        expect(onEnd).toHaveBeenCalledWith(summary);
      });
    });

    it('calls onError when connection error occurs', async () => {
      const onError = vi.fn();
      renderHook(() =>
        useNPhaseStream({ townId: 'test-town', autoConnect: true, onError })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateError());

      await waitFor(() => {
        expect(onError).toHaveBeenCalled();
      });
    });
  });

  // ===========================================================================
  // Reset Tests
  // ===========================================================================

  describe('reset', () => {
    it('resets state and transitions', async () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      // Add some state
      act(() =>
        es.emit('live.start', {
          town_id: 'test-town',
          nphase: {
            session_id: 'session-123',
            current_phase: 'ACT',
            cycle_count: 2,
            checkpoint_count: 5,
            handle_count: 10,
          },
        })
      );

      await waitFor(() => expect(result.current.nphase.isActive).toBe(true));

      // Reset
      act(() => result.current.reset());

      expect(result.current.nphase).toEqual(INITIAL_NPHASE_STATE);
      expect(result.current.transitions).toEqual([]);
    });
  });

  // ===========================================================================
  // Edge Cases
  // ===========================================================================

  describe('edge cases', () => {
    it('does not connect when townId is empty', () => {
      const { result } = renderHook(() => useNPhaseStream({ townId: '' }));

      act(() => result.current.connect());

      expect(MockEventSource.instances).toHaveLength(0);
    });

    it('closes existing connection before reconnecting', () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town' })
      );

      act(() => result.current.connect());
      const firstEs = MockEventSource.instances[0];

      act(() => result.current.connect());

      expect(firstEs.readyState).toBe(MockEventSource.CLOSED);
      expect(MockEventSource.instances).toHaveLength(2);
    });

    it('handles live.start without N-Phase context gracefully', async () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      // Emit live.start without nphase
      act(() =>
        es.emit('live.start', {
          town_id: 'test-town',
          phases: 4,
          speed: 1.0,
        })
      );

      // State should remain at initial
      await waitFor(() => {
        expect(result.current.nphase.enabled).toBe(false);
      });
    });

    it('handles live.state without N-Phase context gracefully', async () => {
      const { result } = renderHook(() =>
        useNPhaseStream({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      // Emit live.state without nphase
      act(() =>
        es.emit('live.state', {
          citizens: [],
          phase: 'MORNING',
        })
      );

      // Should not crash, state unchanged
      expect(result.current.nphase.currentPhase).toBe('UNDERSTAND');
    });
  });
});
