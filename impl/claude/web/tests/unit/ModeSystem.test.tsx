/**
 * Mode System Tests
 *
 * Tests for the six-mode editing system.
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { ReactNode } from 'react';
import { ModeProvider } from '@/context/ModeContext';
import { useMode } from '@/hooks/useMode';
import type { Mode } from '@/types/mode';

// =============================================================================
// Test Wrapper
// =============================================================================

function createWrapper(initialMode?: Mode) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <ModeProvider initialMode={initialMode}>{children}</ModeProvider>;
  };
}

// =============================================================================
// Tests
// =============================================================================

describe('Mode System', () => {
  describe('Initial State', () => {
    it('should default to NORMAL mode', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper(),
      });

      expect(result.current.mode).toBe('NORMAL');
      expect(result.current.isNormal).toBe(true);
    });

    it('should accept custom initial mode', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper('INSERT'),
      });

      expect(result.current.mode).toBe('INSERT');
      expect(result.current.isInsert).toBe(true);
    });
  });

  describe('Mode Transitions', () => {
    it('should transition to INSERT mode', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.toInsert();
      });

      expect(result.current.mode).toBe('INSERT');
      expect(result.current.isInsert).toBe(true);
      expect(result.current.isNormal).toBe(false);
    });

    it('should transition to EDGE mode', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.toEdge();
      });

      expect(result.current.mode).toBe('EDGE');
      expect(result.current.isEdge).toBe(true);
    });

    it('should transition to VISUAL mode', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.toVisual();
      });

      expect(result.current.mode).toBe('VISUAL');
      expect(result.current.isVisual).toBe(true);
    });

    it('should transition to COMMAND mode', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.toCommand();
      });

      expect(result.current.mode).toBe('COMMAND');
      expect(result.current.isCommand).toBe(true);
    });

    it('should transition to WITNESS mode', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.toWitness();
      });

      expect(result.current.mode).toBe('WITNESS');
      expect(result.current.isWitness).toBe(true);
    });

    it('should return to NORMAL from any mode', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper('INSERT'),
      });

      act(() => {
        result.current.toNormal();
      });

      expect(result.current.mode).toBe('NORMAL');
      expect(result.current.isNormal).toBe(true);
    });
  });

  describe('Mode Metadata', () => {
    it('should provide correct color for each mode', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper(),
      });

      const modes: Mode[] = ['NORMAL', 'INSERT', 'EDGE', 'VISUAL', 'COMMAND', 'WITNESS'];

      modes.forEach((mode) => {
        act(() => {
          result.current.setMode(mode);
        });
        expect(result.current.color).toBeTruthy();
        expect(typeof result.current.color).toBe('string');
      });
    });

    it('should provide label and description', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper(),
      });

      expect(result.current.label).toBe('NORMAL');
      expect(result.current.description).toBeTruthy();

      act(() => {
        result.current.toInsert();
      });

      expect(result.current.label).toBe('INSERT');
      expect(result.current.description).toContain('K-Block');
    });

    it('should indicate when mode captures input', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper(),
      });

      // NORMAL doesn't capture input
      expect(result.current.capturesInput).toBe(false);

      // INSERT captures input
      act(() => {
        result.current.toInsert();
      });
      expect(result.current.capturesInput).toBe(true);

      // COMMAND captures input
      act(() => {
        result.current.toCommand();
      });
      expect(result.current.capturesInput).toBe(true);
    });

    it('should indicate when mode blocks navigation', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper(),
      });

      // NORMAL doesn't block navigation
      expect(result.current.blocksNavigation).toBe(false);

      // WITNESS blocks navigation
      act(() => {
        result.current.toWitness();
      });
      expect(result.current.blocksNavigation).toBe(true);
    });
  });

  describe('Mode History', () => {
    it('should track mode transitions', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.toInsert();
      });

      expect(result.current.history).toHaveLength(1);
      expect(result.current.history[0]).toMatchObject({
        from: 'NORMAL',
        to: 'INSERT',
      });

      act(() => {
        result.current.toNormal();
      });

      expect(result.current.history).toHaveLength(2);
      expect(result.current.history[0]).toMatchObject({
        from: 'INSERT',
        to: 'NORMAL',
      });
    });

    it('should include transition reasons', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.toInsert();
      });

      expect(result.current.history[0].reason).toBe('manual');
    });

    it('should limit history to 10 entries', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper(),
      });

      // Make 15 transitions
      act(() => {
        for (let i = 0; i < 15; i++) {
          result.current.toInsert();
          result.current.toNormal();
        }
      });

      expect(result.current.history.length).toBeLessThanOrEqual(10);
    });
  });

  describe('Callbacks', () => {
    it('should fire onModeChange callback', () => {
      const onModeChange = vi.fn();

      const wrapper = ({ children }: { children: ReactNode }) => (
        <ModeProvider onModeChange={onModeChange}>{children}</ModeProvider>
      );

      const { result } = renderHook(() => useMode(), { wrapper });

      act(() => {
        result.current.toInsert();
      });

      expect(onModeChange).toHaveBeenCalledWith(
        expect.objectContaining({
          from: 'NORMAL',
          to: 'INSERT',
        })
      );
    });
  });

  describe('Mode Checkers', () => {
    it('should have exactly one mode active at a time', () => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper(),
      });

      const modes: Mode[] = ['NORMAL', 'INSERT', 'EDGE', 'VISUAL', 'COMMAND', 'WITNESS'];

      modes.forEach((targetMode) => {
        act(() => {
          result.current.setMode(targetMode);
        });

        // Count how many mode checkers are true
        const activeCount = [
          result.current.isNormal,
          result.current.isInsert,
          result.current.isEdge,
          result.current.isVisual,
          result.current.isCommand,
          result.current.isWitness,
        ].filter(Boolean).length;

        expect(activeCount).toBe(1);
      });
    });
  });
});

describe('N-03 Compliance', () => {
  it('should always allow escape to return to NORMAL', () => {
    const { result } = renderHook(() => useMode(), {
      wrapper: createWrapper('INSERT'),
    });

    act(() => {
      result.current.toNormal();
    });

    expect(result.current.mode).toBe('NORMAL');
  });

  it('should return to NORMAL from any mode', () => {
    const modes: Mode[] = ['INSERT', 'EDGE', 'VISUAL', 'COMMAND', 'WITNESS'];

    modes.forEach((startMode) => {
      const { result } = renderHook(() => useMode(), {
        wrapper: createWrapper(startMode),
      });

      act(() => {
        result.current.toNormal();
      });

      expect(result.current.mode).toBe('NORMAL');
    });
  });
});
