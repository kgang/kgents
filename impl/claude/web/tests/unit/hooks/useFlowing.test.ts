/**
 * Tests for useFlowing animation hook.
 *
 * Following T-gent Types taxonomy:
 * - Type I (Contracts): Preconditions, postconditions, invariants
 * - Type II (Saboteurs): Edge cases, boundary conditions
 *
 * @see impl/claude/web/src/hooks/useFlowing.ts
 * @see docs/skills/test-patterns.md
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import {
  useFlowing,
  createCurvedPath,
  createSCurvePath,
  type Point,
} from '@/hooks/useFlowing';

// =============================================================================
// Test Setup
// =============================================================================

beforeEach(() => {
  // Mock requestAnimationFrame to prevent hanging
  vi.spyOn(window, 'requestAnimationFrame').mockImplementation((cb) => {
    // Don't actually call the callback - just return an ID
    return 1;
  });

  vi.spyOn(window, 'cancelAnimationFrame').mockImplementation(() => {});

  vi.spyOn(window, 'matchMedia').mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));
});

afterEach(() => {
  vi.restoreAllMocks();
});

// Test path data - use stable references to avoid infinite re-renders
const emptyPath: Point[] = [];

const singlePointPath: Point[] = [{ x: 50, y: 50 }];

const simplePath: Point[] = [
  { x: 0, y: 0 },
  { x: 100, y: 0 },
];

const curvedPath: Point[] = [
  { x: 0, y: 0 },
  { x: 50, y: -20 },
  { x: 100, y: 0 },
];

// =============================================================================
// Type I Tests: Contracts - Initial State
// =============================================================================

describe('useFlowing - Contracts: Initial State', () => {
  it('starts with empty particles array', () => {
    const { result } = renderHook(() => useFlowing(simplePath));

    expect(result.current.particles).toEqual([]);
    expect(result.current.isFlowing).toBe(false);
  });

  it('returns pathD string for SVG', () => {
    const { result } = renderHook(() => useFlowing(curvedPath));

    expect(typeof result.current.pathD).toBe('string');
    expect(result.current.pathD.length).toBeGreaterThan(0);
  });

  it('returns getPointAtPosition function', () => {
    const { result } = renderHook(() => useFlowing(simplePath));

    expect(typeof result.current.getPointAtPosition).toBe('function');
  });

  it('returns control functions: start, stop, pause, resume', () => {
    const { result } = renderHook(() => useFlowing(simplePath));

    expect(typeof result.current.start).toBe('function');
    expect(typeof result.current.stop).toBe('function');
    expect(typeof result.current.pause).toBe('function');
    expect(typeof result.current.resume).toBe('function');
  });
});

// =============================================================================
// Type I Tests: Contracts - Path Generation
// =============================================================================

describe('useFlowing - Contracts: Path Generation', () => {
  it('generates line for 2-point path', () => {
    const { result } = renderHook(() => useFlowing(simplePath));

    expect(result.current.pathD).toContain('M 0 0');
    expect(result.current.pathD).toContain('L 100 0');
  });

  it('generates curve for 3+ point path', () => {
    const { result } = renderHook(() => useFlowing(curvedPath));

    expect(result.current.pathD).toContain('M 0 0');
    expect(result.current.pathD).toContain('Q'); // Quadratic bezier
  });

  it('returns empty string for < 2 points', () => {
    const { result } = renderHook(() => useFlowing([{ x: 0, y: 0 }]));

    expect(result.current.pathD).toBe('');
  });

  it('getPointAtPosition returns start point at position=0', () => {
    const { result } = renderHook(() => useFlowing(simplePath));

    const point = result.current.getPointAtPosition(0);

    expect(point.x).toBe(0);
    expect(point.y).toBe(0);
  });

  it('getPointAtPosition returns end point at position=1', () => {
    const { result } = renderHook(() => useFlowing(simplePath));

    const point = result.current.getPointAtPosition(1);

    expect(point.x).toBe(100);
    expect(point.y).toBe(0);
  });

  it('getPointAtPosition returns midpoint at position=0.5', () => {
    const { result } = renderHook(() => useFlowing(simplePath));

    const point = result.current.getPointAtPosition(0.5);

    expect(point.x).toBe(50);
    expect(point.y).toBe(0);
  });
});

// =============================================================================
// Type I Tests: Contracts - Animation Lifecycle
// =============================================================================

describe('useFlowing - Contracts: Animation Lifecycle', () => {
  it('start() initializes particles', () => {
    const { result } = renderHook(() =>
      useFlowing(simplePath, { particleCount: 3 })
    );

    act(() => {
      result.current.start();
    });

    expect(result.current.particles.length).toBe(3);
    expect(result.current.isFlowing).toBe(true);
  });

  it('stop() clears particles', () => {
    const { result } = renderHook(() => useFlowing(simplePath));

    act(() => {
      result.current.start();
    });

    act(() => {
      result.current.stop();
    });

    expect(result.current.particles).toEqual([]);
    expect(result.current.isFlowing).toBe(false);
  });

  it('pause() maintains particles', () => {
    const { result } = renderHook(() => useFlowing(simplePath));

    act(() => {
      result.current.start();
    });

    const particleCount = result.current.particles.length;

    act(() => {
      result.current.pause();
    });

    expect(result.current.particles.length).toBe(particleCount);
  });
});

// =============================================================================
// Type I Tests: Contracts - Particle Properties
// =============================================================================

describe('useFlowing - Contracts: Particle Properties', () => {
  it('particles have required properties', () => {
    const { result } = renderHook(() =>
      useFlowing(simplePath, { particleCount: 2 })
    );

    act(() => {
      result.current.start();
    });

    const particle = result.current.particles[0];

    expect(particle).toHaveProperty('id');
    expect(particle).toHaveProperty('position');
    expect(particle).toHaveProperty('x');
    expect(particle).toHaveProperty('y');
    expect(particle).toHaveProperty('opacity');
    expect(particle).toHaveProperty('size');
  });

  it('particles are evenly spaced initially', () => {
    const particleCount = 4;
    const { result } = renderHook(() =>
      useFlowing(simplePath, { particleCount })
    );

    act(() => {
      result.current.start();
    });

    const positions = result.current.particles.map((p) => p.position);
    const expectedSpacing = 1 / particleCount;

    for (let i = 1; i < positions.length; i++) {
      const diff = Math.abs(positions[i] - positions[i - 1]);
      expect(diff).toBeCloseTo(expectedSpacing, 1);
    }
  });
});

// =============================================================================
// Type II Tests: Saboteurs - Edge Cases
// =============================================================================

describe('useFlowing - Saboteurs: Edge Cases', () => {
  it('handles empty path array', () => {
    // Use stable reference to avoid infinite re-renders
    const { result } = renderHook(() => useFlowing(emptyPath));

    act(() => {
      result.current.start();
    });

    expect(result.current.pathD).toBe('');
  });

  it('handles single point path', () => {
    // Use stable reference to avoid infinite re-renders
    const { result } = renderHook(() => useFlowing(singlePointPath));

    expect(result.current.pathD).toBe('');
  });

  it('handles resume() without pause()', () => {
    const { result } = renderHook(() => useFlowing(simplePath));

    act(() => {
      result.current.resume();
    });

    // Should not throw
    expect(result.current.isFlowing).toBe(false);
  });

  it('handles enabled=false', () => {
    const { result } = renderHook(() =>
      useFlowing(simplePath, { enabled: false })
    );

    act(() => {
      result.current.start();
    });

    expect(result.current.isFlowing).toBe(false);
    expect(window.requestAnimationFrame).not.toHaveBeenCalled();
  });

  it('handles direction=reverse', () => {
    const { result } = renderHook(() =>
      useFlowing(simplePath, { direction: 'reverse', particleCount: 2 })
    );

    act(() => {
      result.current.start();
    });

    // Reverse direction starts particles from end
    const firstPosition = result.current.particles[0].position;
    expect(firstPosition).toBeGreaterThan(0.5);
  });
});

// =============================================================================
// Type II Tests: Saboteurs - Reduced Motion
// =============================================================================

describe('useFlowing - Saboteurs: Reduced Motion', () => {
  it('respects prefers-reduced-motion', () => {
    vi.mocked(window.matchMedia).mockImplementation((query) => ({
      matches: query === '(prefers-reduced-motion: reduce)',
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    const { result } = renderHook(() => useFlowing(simplePath));

    act(() => {
      result.current.start();
    });

    expect(result.current.isFlowing).toBe(false);
    expect(window.requestAnimationFrame).not.toHaveBeenCalled();
  });
});

// =============================================================================
// Utility Function Tests
// =============================================================================

describe('createCurvedPath', () => {
  it('returns array with 3 points', () => {
    const path = createCurvedPath({ x: 0, y: 0 }, { x: 100, y: 0 });

    expect(path.length).toBe(3);
  });

  it('first and last points match input', () => {
    const from = { x: 10, y: 20 };
    const to = { x: 90, y: 80 };
    const path = createCurvedPath(from, to);

    expect(path[0]).toEqual(from);
    expect(path[2]).toEqual(to);
  });

  it('midpoint is offset perpendicular to line', () => {
    const from = { x: 0, y: 0 };
    const to = { x: 100, y: 0 };
    const path = createCurvedPath(from, to, 0.3);

    // For horizontal line, perpendicular offset is vertical
    expect(path[1].x).toBeCloseTo(50, 0);
    expect(path[1].y).not.toBe(0);
  });

  it('curvature=0 creates straight line midpoint', () => {
    const from = { x: 0, y: 0 };
    const to = { x: 100, y: 100 };
    const path = createCurvedPath(from, to, 0);

    expect(path[1].x).toBeCloseTo(50, 0);
    expect(path[1].y).toBeCloseTo(50, 0);
  });
});

describe('createSCurvePath', () => {
  it('returns array with 5 points', () => {
    const path = createSCurvePath({ x: 0, y: 0 }, { x: 100, y: 100 });

    expect(path.length).toBe(5);
  });

  it('first and last points match input', () => {
    const from = { x: 0, y: 0 };
    const to = { x: 100, y: 100 };
    const path = createSCurvePath(from, to);

    expect(path[0]).toEqual(from);
    expect(path[4]).toEqual(to);
  });

  it('creates S-shaped curve with opposite offsets', () => {
    const from = { x: 0, y: 0 };
    const to = { x: 100, y: 0 };
    const amplitude = 30;
    const path = createSCurvePath(from, to, amplitude);

    // Point at 25% should curve up
    expect(path[1].y).toBeLessThan(0);

    // Point at 75% should curve down
    expect(path[3].y).toBeGreaterThan(0);

    // Middle point should be on line
    expect(path[2].y).toBe(0);
  });
});
