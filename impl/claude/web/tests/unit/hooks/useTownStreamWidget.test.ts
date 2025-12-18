/**
 * Tests for useTownStreamWidget hook.
 *
 * Phase 3: SSE Integration
 * ========================
 *
 * Test Categories:
 * - Initialization: hook starts with null/empty state
 * - Connection: connect/disconnect behavior
 * - Events: handling live.start, live.event, live.state, live.end
 * - State Management: dashboard and events state updates
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useTownStreamWidget } from '@/hooks/useTownStreamWidget';
import type { ColonyDashboardJSON } from '@/reactive/types';

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

describe('useTownStreamWidget', () => {
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
    it('initializes with null dashboard', () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town' })
      );
      expect(result.current.dashboard).toBeNull();
    });

    it('initializes with empty events array', () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town' })
      );
      expect(result.current.events).toEqual([]);
    });

    it('initializes with isConnected=false', () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town' })
      );
      expect(result.current.isConnected).toBe(false);
    });

    it('initializes with isPlaying=false', () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town' })
      );
      expect(result.current.isPlaying).toBe(false);
    });
  });

  // ===========================================================================
  // Connection Tests
  // ===========================================================================

  describe('connection', () => {
    it('connects when connect() is called', () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town' })
      );

      act(() => result.current.connect());

      expect(MockEventSource.instances).toHaveLength(1);
      expect(MockEventSource.instances[0].url).toContain('test-town');
    });

    it('includes speed and phases in URL', () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town', speed: 2.0, phases: 8 })
      );

      act(() => result.current.connect());

      const url = MockEventSource.instances[0].url;
      expect(url).toContain('speed=2');
      expect(url).toContain('phases=8');
    });

    it('sets isConnected=true when connection opens', async () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town' })
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
        useTownStreamWidget({ townId: 'test-town', autoConnect: true })
      );

      expect(MockEventSource.instances).toHaveLength(1);
    });

    it('does not auto-connect when autoConnect=false', () => {
      renderHook(() =>
        useTownStreamWidget({ townId: 'test-town', autoConnect: false })
      );

      expect(MockEventSource.instances).toHaveLength(0);
    });

    it('disconnects when disconnect() is called', () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town' })
      );

      act(() => result.current.connect());
      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      act(() => result.current.disconnect());

      expect(es.readyState).toBe(MockEventSource.CLOSED);
    });

    it('sets isConnected=false after disconnect', async () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town' })
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
    it('sets isPlaying=true on live.start', async () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());
      act(() => es.emit('live.start', { town_id: 'test-town', phases: 4, speed: 1.0 }));

      await waitFor(() => {
        expect(result.current.isPlaying).toBe(true);
      });
    });

    // TODO: live.end handler not implemented in useTownStreamWidget yet
    it.skip('sets isPlaying=false on live.end', async () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());
      act(() => es.emit('live.start', { town_id: 'test-town' }));

      await waitFor(() => expect(result.current.isPlaying).toBe(true));

      act(() => es.emit('live.end', { status: 'completed' }));

      await waitFor(() => {
        expect(result.current.isPlaying).toBe(false);
      });
    });

    it('updates dashboard on live.state', async () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      const mockDashboard: ColonyDashboardJSON = {
        type: 'colony_dashboard',
        colony_id: 'test-town',
        phase: 'MORNING',
        day: 1,
        metrics: { total_events: 10, total_tokens: 100, entropy_budget: 1.0 },
        citizens: [],
        grid_cols: 5,
        selected_citizen_id: null,
      };

      act(() => es.emit('live.state', mockDashboard));

      await waitFor(() => {
        expect(result.current.dashboard).toEqual(mockDashboard);
      });
    });

    it('accumulates events from live.event', async () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      act(() => {
        es.emit('live.event', { tick: 1, operation: 'greet', participants: ['a', 'b'] });
        es.emit('live.event', { tick: 2, operation: 'trade', participants: ['b', 'c'] });
      });

      await waitFor(() => {
        expect(result.current.events).toHaveLength(2);
      });
    });

    it('prepends new events (most recent first)', async () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      act(() => {
        es.emit('live.event', { tick: 1, operation: 'greet', participants: ['a'] });
        es.emit('live.event', { tick: 2, operation: 'trade', participants: ['b'] });
      });

      await waitFor(() => {
        expect(result.current.events[0].tick).toBe(2);
        expect(result.current.events[1].tick).toBe(1);
      });
    });

    it('limits events to 100', async () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      // Emit 110 events
      act(() => {
        for (let i = 0; i < 110; i++) {
          es.emit('live.event', { tick: i, operation: 'greet', participants: ['a'] });
        }
      });

      await waitFor(() => {
        expect(result.current.events.length).toBeLessThanOrEqual(100);
      });
    });
  });

  // ===========================================================================
  // Callback Tests
  // ===========================================================================

  describe('callbacks', () => {
    it('calls onConnect when connection opens', async () => {
      const onConnect = vi.fn();
      renderHook(() =>
        useTownStreamWidget({ townId: 'test-town', autoConnect: true, onConnect })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      await waitFor(() => {
        expect(onConnect).toHaveBeenCalledTimes(1);
      });
    });

    it('calls onDisconnect when connection closes', async () => {
      const onDisconnect = vi.fn();
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town', onDisconnect })
      );

      act(() => result.current.connect());
      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      act(() => result.current.disconnect());

      await waitFor(() => {
        expect(onDisconnect).toHaveBeenCalled();
      });
    });

    it('calls onEvent for each live.event', async () => {
      const onEvent = vi.fn();
      renderHook(() =>
        useTownStreamWidget({ townId: 'test-town', autoConnect: true, onEvent })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      act(() => {
        es.emit('live.event', { tick: 1, operation: 'greet', participants: ['a'] });
        es.emit('live.event', { tick: 2, operation: 'trade', participants: ['b'] });
      });

      await waitFor(() => {
        expect(onEvent).toHaveBeenCalledTimes(2);
      });
    });

    it('calls onDashboard for each live.state', async () => {
      const onDashboard = vi.fn();
      renderHook(() =>
        useTownStreamWidget({ townId: 'test-town', autoConnect: true, onDashboard })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      const mockDashboard: ColonyDashboardJSON = {
        type: 'colony_dashboard',
        colony_id: 'test-town',
        phase: 'MORNING',
        day: 1,
        metrics: { total_events: 10, total_tokens: 100, entropy_budget: 1.0 },
        citizens: [],
        grid_cols: 5,
        selected_citizen_id: null,
      };

      act(() => es.emit('live.state', mockDashboard));

      await waitFor(() => {
        expect(onDashboard).toHaveBeenCalledWith(mockDashboard);
      });
    });

    it('calls onError on connection error', async () => {
      const onError = vi.fn();
      renderHook(() =>
        useTownStreamWidget({ townId: 'test-town', autoConnect: true, onError })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateError());

      await waitFor(() => {
        expect(onError).toHaveBeenCalled();
      });
    });
  });

  // ===========================================================================
  // Edge Cases
  // ===========================================================================

  describe('edge cases', () => {
    it('does not connect when townId is empty', () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: '' })
      );

      act(() => result.current.connect());

      expect(MockEventSource.instances).toHaveLength(0);
    });

    it('closes existing connection before reconnecting', () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town' })
      );

      act(() => result.current.connect());
      const firstEs = MockEventSource.instances[0];

      act(() => result.current.connect());

      expect(firstEs.readyState).toBe(MockEventSource.CLOSED);
      expect(MockEventSource.instances).toHaveLength(2);
    });

    it('handles dashboard with citizens', async () => {
      const { result } = renderHook(() =>
        useTownStreamWidget({ townId: 'test-town', autoConnect: true })
      );

      const es = MockEventSource.instances[0];
      act(() => es.simulateOpen());

      const mockDashboard: ColonyDashboardJSON = {
        type: 'colony_dashboard',
        colony_id: 'test-town',
        phase: 'AFTERNOON',
        day: 2,
        metrics: { total_events: 50, total_tokens: 500, entropy_budget: 0.8 },
        citizens: [
          {
            type: 'citizen_card',
            citizen_id: 'alice-123',
            name: 'Alice',
            archetype: 'builder',
            phase: 'WORKING',
            nphase: 'ACT',
            activity: [0.5, 0.6, 0.7],
            capability: 0.9,
            entropy: 0.1,
            region: 'plaza',
            mood: 'happy',
            eigenvectors: { warmth: 0.7, curiosity: 0.8, trust: 0.6 },
          },
        ],
        grid_cols: 5,
        selected_citizen_id: null,
      };

      act(() => es.emit('live.state', mockDashboard));

      await waitFor(() => {
        expect(result.current.dashboard?.citizens).toHaveLength(1);
        expect(result.current.dashboard?.citizens[0].name).toBe('Alice');
      });
    });
  });
});
