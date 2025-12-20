/**
 * Tests for usePresenceChannel hook.
 *
 * CLI v7 Phase 4: Collaborative Canvas.
 *
 * Tests:
 * - SSE connection lifecycle
 * - Cursor state updates
 * - Reconnection logic
 * - Helper functions
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import {
  usePresenceChannel,
  getCursorColor,
  getCursorEmoji,
  formatCursorStatus,
  type AgentCursor,
  type CursorState,
  type PresenceEvent,
} from '@/hooks/usePresenceChannel';

// =============================================================================
// Mock EventSource
// =============================================================================

class MockEventSource {
  static instances: MockEventSource[] = [];

  url: string;
  onopen: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onerror: (() => void) | null = null;
  readyState: number = 0; // CONNECTING

  constructor(url: string) {
    this.url = url;
    MockEventSource.instances.push(this);
  }

  close() {
    this.readyState = 2; // CLOSED
  }

  // Test helper: simulate connection
  simulateOpen() {
    this.readyState = 1; // OPEN
    this.onopen?.();
  }

  // Test helper: simulate message
  simulateMessage(event: PresenceEvent) {
    this.onmessage?.({ data: JSON.stringify(event) });
  }

  // Test helper: simulate error
  simulateError() {
    this.onerror?.();
  }
}

// =============================================================================
// Test Setup
// =============================================================================

describe('usePresenceChannel', () => {
  beforeEach(() => {
    MockEventSource.instances = [];
    vi.stubGlobal('EventSource', MockEventSource);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  // ===========================================================================
  // Connection Tests
  // ===========================================================================

  describe('connection lifecycle', () => {
    it('initializes in disconnected state when autoConnect is false', () => {
      const { result } = renderHook(() => usePresenceChannel({ autoConnect: false }));

      expect(result.current.status).toBe('disconnected');
      expect(result.current.isConnected).toBe(false);
      expect(MockEventSource.instances).toHaveLength(0);
    });

    it('auto-connects when autoConnect is true', async () => {
      vi.useFakeTimers();

      const { result } = renderHook(() => usePresenceChannel({ autoConnect: true }));

      // Fast-forward past connection delay
      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      expect(MockEventSource.instances).toHaveLength(1);
      expect(result.current.status).toBe('connecting');
    });

    it('transitions to connected on open', async () => {
      vi.useFakeTimers();

      const { result } = renderHook(() => usePresenceChannel({ autoConnect: true }));

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const source = MockEventSource.instances[0];
      await act(async () => {
        source.simulateOpen();
      });

      expect(result.current.status).toBe('connected');
      expect(result.current.isConnected).toBe(true);
    });

    it('calls onConnect callback when connected', async () => {
      vi.useFakeTimers();
      const onConnect = vi.fn();

      renderHook(() => usePresenceChannel({ autoConnect: true, onConnect }));

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const source = MockEventSource.instances[0];
      await act(async () => {
        source.simulateOpen();
      });

      expect(onConnect).toHaveBeenCalledTimes(1);
    });
  });

  // ===========================================================================
  // Cursor Updates Tests
  // ===========================================================================

  describe('cursor updates', () => {
    it('updates cursors map on cursor_update event', async () => {
      vi.useFakeTimers();

      const { result } = renderHook(() => usePresenceChannel({ autoConnect: true }));

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const source = MockEventSource.instances[0];
      await act(async () => {
        source.simulateOpen();
      });

      const cursor: AgentCursor = {
        agent_id: 'kgent',
        display_name: 'K-gent',
        cursor_id: 'abc123',
        state: 'exploring',
        behavior: 'assistant',
        focus_path: 'self.memory',
        activity: 'Exploring...',
        last_updated: new Date().toISOString(),
      };

      await act(async () => {
        source.simulateMessage({
          type: 'cursor_update',
          cursor,
          timestamp: new Date().toISOString(),
        });
      });

      expect(result.current.cursors.size).toBe(1);
      expect(result.current.cursors.get('kgent')).toEqual(cursor);
      expect(result.current.latestCursor).toEqual(cursor);
    });

    it('removes cursor on cursor_removed event', async () => {
      vi.useFakeTimers();

      const { result } = renderHook(() => usePresenceChannel({ autoConnect: true }));

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const source = MockEventSource.instances[0];
      await act(async () => {
        source.simulateOpen();
      });

      // First add a cursor
      const cursor: AgentCursor = {
        agent_id: 'kgent',
        display_name: 'K-gent',
        cursor_id: 'abc123',
        state: 'exploring',
        behavior: 'assistant',
        focus_path: 'self.memory',
        activity: 'Exploring...',
        last_updated: new Date().toISOString(),
      };

      await act(async () => {
        source.simulateMessage({
          type: 'cursor_update',
          cursor,
          timestamp: new Date().toISOString(),
        });
      });

      expect(result.current.cursors.size).toBe(1);

      // Now remove it
      await act(async () => {
        source.simulateMessage({
          type: 'cursor_removed',
          agent_id: 'kgent',
          timestamp: new Date().toISOString(),
        });
      });

      expect(result.current.cursors.size).toBe(0);
    });

    it('calls onCursorUpdate callback', async () => {
      vi.useFakeTimers();
      const onCursorUpdate = vi.fn();

      renderHook(() => usePresenceChannel({ autoConnect: true, onCursorUpdate }));

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const source = MockEventSource.instances[0];
      await act(async () => {
        source.simulateOpen();
      });

      const cursor: AgentCursor = {
        agent_id: 'kgent',
        display_name: 'K-gent',
        cursor_id: 'abc123',
        state: 'exploring',
        behavior: 'assistant',
        focus_path: 'self.memory',
        activity: 'Exploring...',
        last_updated: new Date().toISOString(),
      };

      await act(async () => {
        source.simulateMessage({
          type: 'cursor_update',
          cursor,
          timestamp: new Date().toISOString(),
        });
      });

      expect(onCursorUpdate).toHaveBeenCalledWith(cursor);
    });
  });

  // ===========================================================================
  // Reconnection Tests
  // ===========================================================================

  describe('reconnection', () => {
    it('attempts to reconnect on error', async () => {
      vi.useFakeTimers();

      const { result } = renderHook(() =>
        usePresenceChannel({
          autoConnect: true,
          reconnectDelay: 1000,
          maxReconnectAttempts: 3,
        })
      );

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const source = MockEventSource.instances[0];
      await act(async () => {
        source.simulateOpen();
      });

      // Simulate error
      await act(async () => {
        source.simulateError();
      });

      expect(result.current.status).toBe('reconnecting');

      // Wait for reconnect attempt
      await act(async () => {
        vi.advanceTimersByTime(1000);
      });

      expect(MockEventSource.instances).toHaveLength(2);
    });

    it('gives up after max reconnect attempts', async () => {
      vi.useFakeTimers();

      const { result } = renderHook(() =>
        usePresenceChannel({
          autoConnect: true,
          reconnectDelay: 100,
          maxReconnectAttempts: 2,
        })
      );

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      // First connection
      const source1 = MockEventSource.instances[0];
      await act(async () => {
        source1.simulateError();
      });

      // First reconnect
      await act(async () => {
        vi.advanceTimersByTime(200);
      });
      const source2 = MockEventSource.instances[1];
      await act(async () => {
        source2.simulateError();
      });

      // Second reconnect
      await act(async () => {
        vi.advanceTimersByTime(400);
      });
      const source3 = MockEventSource.instances[2];
      await act(async () => {
        source3.simulateError();
      });

      // Should be in error state after max attempts
      expect(result.current.status).toBe('error');
      expect(result.current.error).toContain('Max reconnection attempts');
    });
  });

  // ===========================================================================
  // cursorList Derived State Tests
  // ===========================================================================

  describe('cursorList', () => {
    it('returns array from cursors map', async () => {
      vi.useFakeTimers();

      const { result } = renderHook(() => usePresenceChannel({ autoConnect: true }));

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const source = MockEventSource.instances[0];
      await act(async () => {
        source.simulateOpen();
      });

      const cursor1: AgentCursor = {
        agent_id: 'kgent',
        display_name: 'K-gent',
        cursor_id: 'abc123',
        state: 'exploring',
        behavior: 'assistant',
        focus_path: 'self.memory',
        activity: '',
        last_updated: new Date().toISOString(),
      };

      const cursor2: AgentCursor = {
        agent_id: 'explorer',
        display_name: 'Explorer',
        cursor_id: 'def456',
        state: 'working',
        behavior: 'explorer',
        focus_path: 'world.file',
        activity: '',
        last_updated: new Date().toISOString(),
      };

      await act(async () => {
        source.simulateMessage({
          type: 'cursor_update',
          cursor: cursor1,
          timestamp: new Date().toISOString(),
        });
        source.simulateMessage({
          type: 'cursor_update',
          cursor: cursor2,
          timestamp: new Date().toISOString(),
        });
      });

      expect(result.current.cursorList).toHaveLength(2);
      expect(result.current.cursorList.map((c) => c.agent_id)).toEqual(
        expect.arrayContaining(['kgent', 'explorer'])
      );
    });
  });
});

// =============================================================================
// Helper Function Tests
// =============================================================================

describe('getCursorColor', () => {
  it('returns correct colors for each state', () => {
    expect(getCursorColor('following')).toBe('cyan');
    expect(getCursorColor('exploring')).toBe('blue');
    expect(getCursorColor('working')).toBe('yellow');
    expect(getCursorColor('suggesting')).toBe('green');
    expect(getCursorColor('waiting')).toBe('gray');
  });
});

describe('getCursorEmoji', () => {
  it('returns correct emojis for each state', () => {
    expect(getCursorEmoji('following')).toContain('👁');
    expect(getCursorEmoji('exploring')).toContain('🔍');
    expect(getCursorEmoji('working')).toContain('⚡');
    expect(getCursorEmoji('suggesting')).toContain('💡');
    expect(getCursorEmoji('waiting')).toContain('⏳');
  });
});

describe('formatCursorStatus', () => {
  const makeCursor = (state: CursorState, focusPath: string | null = null): AgentCursor => ({
    agent_id: 'kgent',
    display_name: 'K-gent',
    cursor_id: 'abc123',
    state,
    behavior: 'assistant',
    focus_path: focusPath,
    activity: '',
    last_updated: new Date().toISOString(),
  });

  it('formats exploring state', () => {
    const cursor = makeCursor('exploring', 'self.memory');
    expect(formatCursorStatus(cursor)).toBe('K-gent is exploring self.memory...');
  });

  it('formats working state', () => {
    const cursor = makeCursor('working', 'world.file.edit');
    expect(formatCursorStatus(cursor)).toBe('K-gent is working on world.file.edit...');
  });

  it('formats suggesting state', () => {
    const cursor = makeCursor('suggesting', 'self.soul.reflect');
    expect(formatCursorStatus(cursor)).toBe('K-gent suggests: self.soul.reflect');
  });

  it('formats following state', () => {
    const cursor = makeCursor('following');
    expect(formatCursorStatus(cursor)).toBe('K-gent is following...');
  });

  it('formats waiting state', () => {
    const cursor = makeCursor('waiting');
    expect(formatCursorStatus(cursor)).toBe('K-gent is ready');
  });
});
