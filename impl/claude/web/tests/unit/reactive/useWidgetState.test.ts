import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useWidgetState, useWidgetStream } from '@/reactive/useWidgetState';
import type { CitizenCardJSON, ColonyDashboardJSON } from '@/reactive/types';

// =============================================================================
// Test Data
// =============================================================================

const createCitizenCard = (overrides: Partial<CitizenCardJSON> = {}): CitizenCardJSON => ({
  type: 'citizen_card',
  citizen_id: 'test-1',
  name: 'Test',
  archetype: 'Builder',
  phase: 'IDLE',
  nphase: 'SENSE',
  activity: [],
  capability: 1,
  entropy: 0,
  region: 'plaza',
  mood: 'calm',
  eigenvectors: { warmth: 0.5, curiosity: 0.5, trust: 0.5 },
  ...overrides,
});

const createDashboard = (overrides: Partial<ColonyDashboardJSON> = {}): ColonyDashboardJSON => ({
  type: 'colony_dashboard',
  colony_id: 'colony-1',
  phase: 'MORNING',
  day: 1,
  metrics: { total_events: 0, total_tokens: 0, entropy_budget: 1 },
  citizens: [],
  grid_cols: 3,
  selected_citizen_id: null,
  ...overrides,
});

// =============================================================================
// useWidgetState Tests
// =============================================================================

describe('useWidgetState', () => {
  it('returns initial state', () => {
    const initial = createCitizenCard({ name: 'Initial' });
    const { result } = renderHook(() => useWidgetState({ initialState: initial }));

    expect(result.current.state.name).toBe('Initial');
    expect(result.current.generation).toBe(0);
  });

  it('updates state with direct value', () => {
    const initial = createCitizenCard({ name: 'Before' });
    const { result } = renderHook(() => useWidgetState({ initialState: initial }));

    act(() => {
      result.current.updateState(createCitizenCard({ name: 'After' }));
    });

    expect(result.current.state.name).toBe('After');
  });

  it('updates state with functional updater', () => {
    const initial = createCitizenCard({ capability: 0.5 });
    const { result } = renderHook(() => useWidgetState({ initialState: initial }));

    act(() => {
      result.current.updateState((prev) => ({
        ...prev,
        capability: prev.capability + 0.1,
      }));
    });

    expect(result.current.state.capability).toBeCloseTo(0.6);
  });

  it('increments generation on update', () => {
    const initial = createCitizenCard();
    const { result } = renderHook(() => useWidgetState({ initialState: initial }));

    expect(result.current.generation).toBe(0);

    act(() => {
      result.current.updateState(createCitizenCard({ name: 'Changed' }));
    });

    expect(result.current.generation).toBe(1);
  });

  it('calls onUpdate callback when state changes', () => {
    const onUpdate = vi.fn();
    const initial = createCitizenCard();
    const { result } = renderHook(() => useWidgetState({ initialState: initial, onUpdate }));

    act(() => {
      result.current.updateState(createCitizenCard({ name: 'Updated' }));
    });

    expect(onUpdate).toHaveBeenCalledTimes(1);
    expect(onUpdate).toHaveBeenCalledWith(expect.objectContaining({ name: 'Updated' }));
  });

  it('does not update if state is equal', () => {
    const onUpdate = vi.fn();
    const initial = createCitizenCard({ name: 'Same' });
    const { result } = renderHook(() => useWidgetState({ initialState: initial, onUpdate }));

    const genBefore = result.current.generation;

    act(() => {
      // Same reference - should not trigger update
      result.current.updateState(result.current.state);
    });

    expect(result.current.generation).toBe(genBefore);
    expect(onUpdate).not.toHaveBeenCalled();
  });

  it('patches state with partial update', () => {
    const initial = createCitizenCard({ name: 'Before', mood: 'calm' });
    const { result } = renderHook(() => useWidgetState({ initialState: initial }));

    act(() => {
      result.current.patchState({ mood: 'excited' });
    });

    expect(result.current.state.name).toBe('Before'); // Unchanged
    expect(result.current.state.mood).toBe('excited'); // Changed
  });

  it('resets to initial state', () => {
    const initial = createCitizenCard({ name: 'Original' });
    const { result } = renderHook(() => useWidgetState({ initialState: initial }));

    act(() => {
      result.current.updateState(createCitizenCard({ name: 'Modified' }));
    });

    expect(result.current.state.name).toBe('Modified');

    act(() => {
      result.current.reset();
    });

    expect(result.current.state.name).toBe('Original');
  });
});

// =============================================================================
// useWidgetStream Tests
// =============================================================================

describe('useWidgetStream', () => {
  let mockEventSource: {
    addEventListener: ReturnType<typeof vi.fn>;
    close: ReturnType<typeof vi.fn>;
    readyState: number;
    onopen: ((event: Event) => void) | null;
    onerror: ((event: Event) => void) | null;
  };

  beforeEach(() => {
    mockEventSource = {
      addEventListener: vi.fn(),
      close: vi.fn(),
      readyState: 0,
      onopen: null,
      onerror: null,
    };

    // Mock EventSource constructor
    vi.stubGlobal(
      'EventSource',
      vi.fn().mockImplementation(() => mockEventSource)
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('initializes with initial state', () => {
    const initial = createDashboard({ colony_id: 'stream-test' });
    const { result } = renderHook(() =>
      useWidgetStream({
        url: '/v1/test/live',
        initialState: initial,
        autoConnect: false,
      })
    );

    expect(result.current.state.colony_id).toBe('stream-test');
    expect(result.current.isConnected).toBe(false);
  });

  it('connects when connect() is called', () => {
    const initial = createDashboard();
    const { result } = renderHook(() =>
      useWidgetStream({
        url: '/v1/test/live',
        initialState: initial,
        autoConnect: false,
      })
    );

    act(() => {
      result.current.connect();
    });

    expect(EventSource).toHaveBeenCalledWith('/v1/test/live');
  });

  it('auto-connects when autoConnect is true', () => {
    const initial = createDashboard();
    renderHook(() =>
      useWidgetStream({
        url: '/v1/auto/live',
        initialState: initial,
        autoConnect: true,
      })
    );

    expect(EventSource).toHaveBeenCalledWith('/v1/auto/live');
  });

  it('sets isConnected to true on open', async () => {
    const onConnect = vi.fn();
    const initial = createDashboard();
    const { result } = renderHook(() =>
      useWidgetStream({
        url: '/v1/test/live',
        initialState: initial,
        autoConnect: false,
        onConnect,
      })
    );

    act(() => {
      result.current.connect();
    });

    // Simulate connection
    act(() => {
      mockEventSource.readyState = 1;
      mockEventSource.onopen?.(new Event('open'));
    });

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });
    expect(onConnect).toHaveBeenCalled();
  });

  it('updates state when receiving SSE event', async () => {
    const initial = createDashboard({ day: 1 });
    const { result } = renderHook(() =>
      useWidgetStream({
        url: '/v1/test/live',
        initialState: initial,
        autoConnect: false,
        eventName: 'live.state',
      })
    );

    act(() => {
      result.current.connect();
    });

    // Get the event handler
    const addEventListenerCalls = mockEventSource.addEventListener.mock.calls;
    const stateHandler = addEventListenerCalls.find((call) => call[0] === 'live.state')?.[1];

    expect(stateHandler).toBeDefined();

    // Simulate receiving event
    const newState = createDashboard({ day: 5 });
    act(() => {
      stateHandler({ data: JSON.stringify(newState) });
    });

    await waitFor(() => {
      expect(result.current.state.day).toBe(5);
    });
  });

  it('disconnects when disconnect() is called', () => {
    const onDisconnect = vi.fn();
    const initial = createDashboard();
    const { result } = renderHook(() =>
      useWidgetStream({
        url: '/v1/test/live',
        initialState: initial,
        autoConnect: false,
        onDisconnect,
      })
    );

    act(() => {
      result.current.connect();
    });

    act(() => {
      result.current.disconnect();
    });

    expect(mockEventSource.close).toHaveBeenCalled();
    expect(onDisconnect).toHaveBeenCalled();
  });

  it('cleans up on unmount', () => {
    const initial = createDashboard();
    const { unmount } = renderHook(() =>
      useWidgetStream({
        url: '/v1/test/live',
        initialState: initial,
        autoConnect: true,
      })
    );

    unmount();

    expect(mockEventSource.close).toHaveBeenCalled();
  });

  it('provides correct return interface', () => {
    // Simple test to verify the hook returns expected structure
    const initial = createDashboard();
    const { result } = renderHook(() =>
      useWidgetStream({
        url: '/v1/test/live',
        initialState: initial,
        autoConnect: false,
      })
    );

    // Verify all expected properties exist
    expect(result.current).toHaveProperty('state');
    expect(result.current).toHaveProperty('updateState');
    expect(result.current).toHaveProperty('patchState');
    expect(result.current).toHaveProperty('reset');
    expect(result.current).toHaveProperty('generation');
    expect(result.current).toHaveProperty('connect');
    expect(result.current).toHaveProperty('disconnect');
    expect(result.current).toHaveProperty('isConnected');
  });
});
