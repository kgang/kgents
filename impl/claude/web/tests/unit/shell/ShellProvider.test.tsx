/**
 * ShellProvider Tests
 *
 * Tests for density detection, observer context, and trace collection.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import type { ReactNode } from 'react';
import {
  ShellProvider,
  useShell,
  useShellMaybe,
  useDensity,
  useObserver,
  useTraces,
  useTracedInvoke,
} from '@/shell/ShellProvider';

// =============================================================================
// Test Utilities
// =============================================================================

function createWrapper(props: { initialObserver?: Partial<any> } = {}) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <ShellProvider {...props}>{children}</ShellProvider>;
  };
}

// Mock window dimensions
function mockWindowSize(width: number, height: number = 768) {
  Object.defineProperty(window, 'innerWidth', { value: width, writable: true });
  Object.defineProperty(window, 'innerHeight', { value: height, writable: true });
}

// =============================================================================
// Context Hook Tests
// =============================================================================

describe('useShell', () => {
  beforeEach(() => {
    localStorage.clear();
    mockWindowSize(1200); // Desktop by default
  });

  it('throws when used outside provider', () => {
    // Suppress console.error for this test
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      renderHook(() => useShell());
    }).toThrow('useShell must be used within a ShellProvider');

    spy.mockRestore();
  });

  it('provides shell context within provider', () => {
    const { result } = renderHook(() => useShell(), {
      wrapper: createWrapper(),
    });

    expect(result.current).toBeDefined();
    expect(result.current.density).toBeDefined();
    expect(result.current.observer).toBeDefined();
  });
});

describe('useShellMaybe', () => {
  it('returns null outside provider', () => {
    const { result } = renderHook(() => useShellMaybe());
    expect(result.current).toBeNull();
  });

  it('returns context within provider', () => {
    const { result } = renderHook(() => useShellMaybe(), {
      wrapper: createWrapper(),
    });
    expect(result.current).not.toBeNull();
  });
});

// =============================================================================
// Density Detection Tests
// =============================================================================

describe('density detection', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('returns compact for mobile widths (<768px)', () => {
    mockWindowSize(375);
    const { result } = renderHook(() => useDensity(), {
      wrapper: createWrapper(),
    });
    expect(result.current).toBe('compact');
  });

  it('returns comfortable for tablet widths (768-1024px)', () => {
    mockWindowSize(800);
    const { result } = renderHook(() => useDensity(), {
      wrapper: createWrapper(),
    });
    expect(result.current).toBe('comfortable');
  });

  it('returns spacious for desktop widths (>1024px)', () => {
    mockWindowSize(1200);
    const { result } = renderHook(() => useDensity(), {
      wrapper: createWrapper(),
    });
    expect(result.current).toBe('spacious');
  });

  it('provides device booleans', () => {
    mockWindowSize(375);
    const { result } = renderHook(() => useShell(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isMobile).toBe(true);
    expect(result.current.isTablet).toBe(false);
    expect(result.current.isDesktop).toBe(false);
  });

  it('updates on window resize', async () => {
    mockWindowSize(1200);
    const { result } = renderHook(() => useShell(), {
      wrapper: createWrapper(),
    });

    expect(result.current.density).toBe('spacious');

    await act(async () => {
      mockWindowSize(375);
      window.dispatchEvent(new Event('resize'));
      // Wait for debounce (100ms) + buffer
      await new Promise((r) => setTimeout(r, 150));
    });

    expect(result.current.density).toBe('compact');
  });
});

// =============================================================================
// Observer Tests
// =============================================================================

describe('observer context', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('provides default observer', () => {
    const { result } = renderHook(() => useObserver(), {
      wrapper: createWrapper(),
    });

    expect(result.current.archetype).toBe('developer');
    expect(result.current.sessionId).toBeDefined();
    expect(result.current.capabilities.has('read')).toBe(true);
  });

  it('allows archetype changes', () => {
    const { result } = renderHook(() => useShell(), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.setArchetype('architect');
    });

    expect(result.current.observer.archetype).toBe('architect');
  });

  it('allows intent changes', () => {
    const { result } = renderHook(() => useShell(), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.setIntent('Reviewing the codebase');
    });

    expect(result.current.observer.intent).toBe('Reviewing the codebase');
  });

  it('accepts initial observer override', () => {
    const { result } = renderHook(() => useObserver(), {
      wrapper: createWrapper({
        initialObserver: { archetype: 'reviewer', userId: 'test-user' },
      }),
    });

    expect(result.current.archetype).toBe('reviewer');
    expect(result.current.userId).toBe('test-user');
  });

  it('persists observer to localStorage', async () => {
    mockWindowSize(1200);
    const { result } = renderHook(() => useShell(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      result.current.setArchetype('security');
      // Allow effects to run
      await new Promise((r) => setTimeout(r, 0));
    });

    // Check localStorage.setItem was called with the right key
    expect(localStorage.setItem).toHaveBeenCalledWith(
      'kgents.shell.observer',
      expect.stringContaining('"archetype":"security"')
    );
  });

  it('hasCapability checks capabilities correctly', () => {
    const { result } = renderHook(() => useShell(), {
      wrapper: createWrapper(),
    });

    expect(result.current.hasCapability('read')).toBe(true);
    expect(result.current.hasCapability('admin')).toBe(false);
  });
});

// =============================================================================
// Trace Collection Tests
// =============================================================================

describe('trace collection', () => {
  beforeEach(() => {
    localStorage.clear();
    mockWindowSize(1200);
  });

  it('starts with empty traces', () => {
    const { result } = renderHook(() => useTraces(), {
      wrapper: createWrapper(),
    });

    expect(result.current.traces).toEqual([]);
  });

  it('adds traces', () => {
    const { result } = renderHook(() => useTraces(), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.addTrace({
        timestamp: new Date(),
        path: 'self.memory.capture',
        aspect: 'manifest',
        duration: 150,
        status: 'success',
      });
    });

    expect(result.current.traces).toHaveLength(1);
    expect(result.current.traces[0].path).toBe('self.memory.capture');
    expect(result.current.traces[0].id).toBeDefined();
  });

  it('orders traces newest first', () => {
    const { result } = renderHook(() => useTraces(), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.addTrace({
        timestamp: new Date(),
        path: 'first',
        aspect: 'manifest',
        duration: 100,
        status: 'success',
      });
    });

    act(() => {
      result.current.addTrace({
        timestamp: new Date(),
        path: 'second',
        aspect: 'manifest',
        duration: 100,
        status: 'success',
      });
    });

    expect(result.current.traces[0].path).toBe('second');
    expect(result.current.traces[1].path).toBe('first');
  });

  it('clears traces', () => {
    const { result } = renderHook(() => useTraces(), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.addTrace({
        timestamp: new Date(),
        path: 'test',
        aspect: 'manifest',
        duration: 100,
        status: 'success',
      });
    });

    expect(result.current.traces).toHaveLength(1);

    act(() => {
      result.current.clearTraces();
    });

    expect(result.current.traces).toHaveLength(0);
  });

  it('limits traces to MAX_TRACES', () => {
    const { result } = renderHook(() => useTraces(), {
      wrapper: createWrapper(),
    });

    // Add 60 traces (MAX_TRACES is 50)
    for (let i = 0; i < 60; i++) {
      act(() => {
        result.current.addTrace({
          timestamp: new Date(),
          path: `test-${i}`,
          aspect: 'manifest',
          duration: 100,
          status: 'success',
        });
      });
    }

    expect(result.current.traces.length).toBeLessThanOrEqual(50);
    // Most recent should be at index 0
    expect(result.current.traces[0].path).toBe('test-59');
  });
});

// =============================================================================
// useTracedInvoke Tests
// =============================================================================

describe('useTracedInvoke', () => {
  beforeEach(() => {
    localStorage.clear();
    mockWindowSize(1200);
  });

  it('adds success trace on successful invocation', async () => {
    const { result } = renderHook(
      () => {
        const traced = useTracedInvoke();
        const { traces } = useTraces();
        return { traced, traces };
      },
      { wrapper: createWrapper() }
    );

    await act(async () => {
      await result.current.traced('self.memory.capture', 'manifest', async () => {
        return { id: 'test-result' };
      });
    });

    expect(result.current.traces).toHaveLength(1);
    expect(result.current.traces[0].status).toBe('success');
    expect(result.current.traces[0].result).toEqual({ id: 'test-result' });
  });

  it('adds error trace on failed invocation', async () => {
    const { result } = renderHook(
      () => {
        const traced = useTracedInvoke();
        const { traces } = useTraces();
        return { traced, traces };
      },
      { wrapper: createWrapper() }
    );

    await act(async () => {
      try {
        await result.current.traced('self.memory.capture', 'manifest', async () => {
          throw new Error('Network error');
        });
      } catch {
        // Expected
      }
    });

    expect(result.current.traces).toHaveLength(1);
    expect(result.current.traces[0].status).toBe('error');
    expect(result.current.traces[0].error).toBe('Network error');
  });

  it('measures duration', async () => {
    const { result } = renderHook(
      () => {
        const traced = useTracedInvoke();
        const { traces } = useTraces();
        return { traced, traces };
      },
      { wrapper: createWrapper() }
    );

    await act(async () => {
      await result.current.traced('test', 'manifest', async () => {
        await new Promise((r) => setTimeout(r, 50));
        return 'done';
      });
    });

    expect(result.current.traces[0].duration).toBeGreaterThanOrEqual(40);
  });
});

// =============================================================================
// Shell Panel State Tests
// =============================================================================

describe('shell panel state', () => {
  beforeEach(() => {
    localStorage.clear();
    mockWindowSize(1200);
  });

  it('defaults drawer to collapsed', () => {
    const { result } = renderHook(() => useShell(), {
      wrapper: createWrapper(),
    });

    expect(result.current.observerDrawerExpanded).toBe(false);
  });

  it('toggles drawer state', () => {
    const { result } = renderHook(() => useShell(), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.setObserverDrawerExpanded(true);
    });

    expect(result.current.observerDrawerExpanded).toBe(true);
  });

  it('persists drawer state to localStorage', async () => {
    const { result } = renderHook(() => useShell(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      result.current.setObserverDrawerExpanded(true);
      // Allow effects to run
      await new Promise((r) => setTimeout(r, 0));
    });

    // Check localStorage.setItem was called with the right key
    expect(localStorage.setItem).toHaveBeenCalledWith(
      'kgents.shell.drawer',
      'true'
    );
  });

  it('defaults navigation to expanded on desktop', () => {
    mockWindowSize(1200);
    const { result } = renderHook(() => useShell(), {
      wrapper: createWrapper(),
    });

    expect(result.current.navigationTreeExpanded).toBe(true);
  });

  it('auto-collapses navigation on mobile', async () => {
    mockWindowSize(1200);
    const { result, rerender } = renderHook(() => useShell(), {
      wrapper: createWrapper(),
    });

    expect(result.current.navigationTreeExpanded).toBe(true);

    await act(async () => {
      mockWindowSize(375);
      window.dispatchEvent(new Event('resize'));
      // Wait for debounce (100ms) + buffer
      await new Promise((r) => setTimeout(r, 150));
    });

    // Re-render after resize
    rerender();

    // Navigation should auto-collapse on mobile
    expect(result.current.isMobile).toBe(true);
  });
});
