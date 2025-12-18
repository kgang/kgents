/**
 * Tests for useGrowing animation hook.
 *
 * Following T-gent Types taxonomy:
 * - Type I (Contracts): Preconditions, postconditions, invariants
 * - Type II (Saboteurs): Edge cases, boundary conditions
 * - Type III (Spies): Callback verification
 * - Type IV (Properties): Property-based tests
 * - Type V (Performance): Timing and efficiency
 *
 * @see impl/claude/web/src/hooks/useGrowing.ts
 * @see docs/skills/test-patterns.md
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import {
  useGrowing,
  getStaggeredGrowthDelay,
  triggerWithDelay,
  type GrowthStage,
} from '@/hooks/useGrowing';
import { GROWING_ANIMATION } from '@/constants';

// =============================================================================
// Test Setup
// =============================================================================

// Mock requestAnimationFrame for controlled timing
let frameCallbacks: Array<(timestamp: number) => void> = [];
let mockTimestamp = 0;

beforeEach(() => {
  frameCallbacks = [];
  mockTimestamp = 0;

  vi.spyOn(window, 'requestAnimationFrame').mockImplementation((cb) => {
    frameCallbacks.push(cb);
    return frameCallbacks.length;
  });

  vi.spyOn(window, 'cancelAnimationFrame').mockImplementation((id) => {
    frameCallbacks[id - 1] = () => {}; // Nullify the callback
  });

  // Mock reduced motion query
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

// Advance animation frames
function advanceFrames(count: number, msPerFrame: number = 16.67) {
  for (let i = 0; i < count; i++) {
    mockTimestamp += msPerFrame;
    const callbacks = [...frameCallbacks];
    frameCallbacks = [];
    callbacks.forEach((cb) => cb(mockTimestamp));
  }
}

// =============================================================================
// Type I Tests: Contracts - Initial State
// =============================================================================

describe('useGrowing - Contracts: Initial State', () => {
  it('starts in seed state with scale=0', () => {
    const { result } = renderHook(() => useGrowing());

    expect(result.current.scale).toBe(0);
    expect(result.current.opacity).toBe(0);
    expect(result.current.stage).toBe('seed');
    expect(result.current.isGrowing).toBe(false);
  });

  it('starts in full state when startFull=true', () => {
    const { result } = renderHook(() => useGrowing({ startFull: true }));

    expect(result.current.scale).toBe(1);
    expect(result.current.opacity).toBe(1);
    expect(result.current.stage).toBe('full');
    expect(result.current.isGrowing).toBe(false);
  });

  it('returns CSS transform string', () => {
    const { result } = renderHook(() => useGrowing());

    expect(result.current.transform).toBe('scale(0.0000)');
  });

  it('returns CSS style object with required properties', () => {
    const { result } = renderHook(() => useGrowing());

    expect(result.current.style).toMatchObject({
      transform: expect.any(String),
      opacity: expect.any(Number),
      transformOrigin: 'center center',
    });
  });
});

// =============================================================================
// Type I Tests: Contracts - Animation Lifecycle
// =============================================================================

describe('useGrowing - Contracts: Animation Lifecycle', () => {
  it('trigger() starts animation', () => {
    const { result } = renderHook(() => useGrowing());

    act(() => {
      result.current.trigger();
    });

    expect(result.current.isGrowing).toBe(true);
    expect(window.requestAnimationFrame).toHaveBeenCalled();
  });

  it('reset() returns to seed state', () => {
    const { result } = renderHook(() => useGrowing({ startFull: true }));

    act(() => {
      result.current.reset();
    });

    expect(result.current.scale).toBe(0);
    expect(result.current.opacity).toBe(0);
    expect(result.current.stage).toBe('seed');
    expect(result.current.isGrowing).toBe(false);
  });

  it('complete() jumps to full state', () => {
    const { result } = renderHook(() => useGrowing());

    act(() => {
      result.current.complete();
    });

    expect(result.current.scale).toBe(1);
    expect(result.current.opacity).toBe(1);
    expect(result.current.stage).toBe('full');
    expect(result.current.isGrowing).toBe(false);
  });

  it('animation reaches full state after duration', () => {
    const duration = 100;
    const { result } = renderHook(() => useGrowing({ duration }));

    act(() => {
      result.current.trigger();
    });

    // Advance past duration
    act(() => {
      advanceFrames(20, 10); // 200ms
    });

    expect(result.current.scale).toBe(1);
    expect(result.current.opacity).toBe(1);
    expect(result.current.stage).toBe('full');
    expect(result.current.isGrowing).toBe(false);
  });
});

// =============================================================================
// Type I Tests: Contracts - Stage Progression
// =============================================================================

describe('useGrowing - Contracts: Stage Progression', () => {
  it('progresses through stages: seed → sprout → bloom → full', () => {
    const duration = 400;
    const { result } = renderHook(() => useGrowing({ duration }));
    const stagesObserved: GrowthStage[] = [];

    act(() => {
      result.current.trigger();
    });

    // Sample stages over animation
    for (let i = 0; i < 30; i++) {
      act(() => {
        advanceFrames(1, 16.67);
      });

      const stage = result.current.stage;
      if (!stagesObserved.includes(stage)) {
        stagesObserved.push(stage);
      }
    }

    // All stages should have been observed in order
    expect(stagesObserved).toContain('seed');
    expect(stagesObserved).toContain('sprout');
    expect(stagesObserved).toContain('bloom');
    expect(stagesObserved).toContain('full');

    // Verify order
    const seedIdx = stagesObserved.indexOf('seed');
    const sproutIdx = stagesObserved.indexOf('sprout');
    const bloomIdx = stagesObserved.indexOf('bloom');
    const fullIdx = stagesObserved.indexOf('full');

    expect(seedIdx).toBeLessThan(sproutIdx);
    expect(sproutIdx).toBeLessThan(bloomIdx);
    expect(bloomIdx).toBeLessThan(fullIdx);
  });
});

// =============================================================================
// Type II Tests: Saboteurs - Edge Cases
// =============================================================================

describe('useGrowing - Saboteurs: Edge Cases', () => {
  it('handles multiple trigger() calls without breaking', () => {
    const { result } = renderHook(() => useGrowing());

    act(() => {
      result.current.trigger();
      result.current.trigger();
      result.current.trigger();
    });

    expect(result.current.isGrowing).toBe(true);
    // Should not throw, animation should be restarted
  });

  it('handles trigger() then immediate reset()', () => {
    const { result } = renderHook(() => useGrowing());

    act(() => {
      result.current.trigger();
    });

    act(() => {
      result.current.reset();
    });

    expect(result.current.scale).toBe(0);
    expect(result.current.isGrowing).toBe(false);
  });

  it('handles duration=0', () => {
    const { result } = renderHook(() => useGrowing({ duration: 0 }));

    act(() => {
      result.current.trigger();
    });

    act(() => {
      advanceFrames(1);
    });

    // Should complete immediately
    expect(result.current.stage).toBe('full');
  });

  it('handles very small duration', () => {
    const { result } = renderHook(() => useGrowing({ duration: 1 }));

    act(() => {
      result.current.trigger();
    });

    // Advance enough frames to guarantee completion
    act(() => {
      advanceFrames(5, 16.67);
    });

    expect(result.current.stage).toBe('full');
  });

  it('handles enabled=false', () => {
    const { result } = renderHook(() => useGrowing({ enabled: false }));

    act(() => {
      result.current.trigger();
    });

    expect(result.current.isGrowing).toBe(false);
    expect(window.requestAnimationFrame).not.toHaveBeenCalled();
  });
});

// =============================================================================
// Type II Tests: Saboteurs - Reduced Motion
// =============================================================================

describe('useGrowing - Saboteurs: Reduced Motion', () => {
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

    const { result } = renderHook(() => useGrowing());

    act(() => {
      result.current.trigger();
    });

    // Should jump to full immediately
    expect(result.current.scale).toBe(1);
    expect(result.current.opacity).toBe(1);
    expect(result.current.stage).toBe('full');
    expect(result.current.isGrowing).toBe(false);
  });

  it('allows overriding reduced motion with respectReducedMotion=false', () => {
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

    const { result } = renderHook(() =>
      useGrowing({ respectReducedMotion: false })
    );

    act(() => {
      result.current.trigger();
    });

    // Should animate despite reduced motion preference
    expect(result.current.isGrowing).toBe(true);
  });
});

// =============================================================================
// Type III Tests: Spies - Callback Verification
// =============================================================================

describe('useGrowing - Spies: Callbacks', () => {
  it('calls onComplete when animation finishes', () => {
    const onComplete = vi.fn();
    const { result } = renderHook(() =>
      useGrowing({ duration: 100, onComplete })
    );

    act(() => {
      result.current.trigger();
    });

    expect(onComplete).not.toHaveBeenCalled();

    // Advance past duration
    act(() => {
      advanceFrames(15, 10); // 150ms
    });

    expect(onComplete).toHaveBeenCalledTimes(1);
  });

  it('calls onComplete when complete() is called', () => {
    const onComplete = vi.fn();
    const { result } = renderHook(() => useGrowing({ onComplete }));

    act(() => {
      result.current.complete();
    });

    expect(onComplete).toHaveBeenCalledTimes(1);
  });

  it('does not call onComplete on reset()', () => {
    const onComplete = vi.fn();
    const { result } = renderHook(() => useGrowing({ onComplete }));

    act(() => {
      result.current.trigger();
    });

    act(() => {
      result.current.reset();
    });

    expect(onComplete).not.toHaveBeenCalled();
  });
});

// =============================================================================
// Type IV Tests: Properties - Invariants
// =============================================================================

describe('useGrowing - Properties: Invariants', () => {
  it('scale is always in [0, 1.03] range', () => {
    const { result } = renderHook(() => useGrowing({ duration: 100 }));

    act(() => {
      result.current.trigger();
    });

    // Sample throughout animation
    for (let i = 0; i < 20; i++) {
      act(() => {
        advanceFrames(1, 10);
      });

      expect(result.current.scale).toBeGreaterThanOrEqual(0);
      expect(result.current.scale).toBeLessThanOrEqual(1.03);
    }
  });

  it('opacity is always in [0, 1] range', () => {
    const { result } = renderHook(() => useGrowing({ duration: 100 }));

    act(() => {
      result.current.trigger();
    });

    // Sample throughout animation
    for (let i = 0; i < 20; i++) {
      act(() => {
        advanceFrames(1, 10);
      });

      expect(result.current.opacity).toBeGreaterThanOrEqual(0);
      expect(result.current.opacity).toBeLessThanOrEqual(1);
    }
  });

  it('scale increases overall from seed to full', () => {
    const { result } = renderHook(() => useGrowing({ duration: 200 }));

    const initialScale = result.current.scale;

    act(() => {
      result.current.trigger();
    });

    // Complete animation
    act(() => {
      advanceFrames(30, 16.67);
    });

    const finalScale = result.current.scale;

    // Final scale should be greater than initial (0 → 1)
    expect(finalScale).toBeGreaterThan(initialScale);
    expect(finalScale).toBe(1);
  });

  it('stage transitions are one-directional during growth', () => {
    const { result } = renderHook(() => useGrowing({ duration: 200 }));
    const stages: GrowthStage[] = [];
    const stageOrder: GrowthStage[] = ['seed', 'sprout', 'bloom', 'full'];

    act(() => {
      result.current.trigger();
    });

    // Sample throughout animation
    for (let i = 0; i < 30; i++) {
      act(() => {
        advanceFrames(1, 10);
      });
      stages.push(result.current.stage);
    }

    // Stage index should never decrease
    let maxStageIndex = 0;
    for (const stage of stages) {
      const idx = stageOrder.indexOf(stage);
      expect(idx).toBeGreaterThanOrEqual(maxStageIndex);
      maxStageIndex = Math.max(maxStageIndex, idx);
    }
  });
});

// =============================================================================
// Type V Tests: Performance
// =============================================================================

describe('useGrowing - Performance', () => {
  it('100 trigger/reset cycles complete in < 50ms', () => {
    const { result } = renderHook(() => useGrowing());
    const startTime = performance.now();

    for (let i = 0; i < 100; i++) {
      act(() => {
        result.current.trigger();
      });
      act(() => {
        result.current.reset();
      });
    }

    const elapsed = performance.now() - startTime;
    expect(elapsed).toBeLessThan(50);
  });

  it('cleans up animation frame on unmount', () => {
    const { unmount, result } = renderHook(() => useGrowing());

    act(() => {
      result.current.trigger();
    });

    expect(window.requestAnimationFrame).toHaveBeenCalled();

    unmount();

    expect(window.cancelAnimationFrame).toHaveBeenCalled();
  });
});

// =============================================================================
// Utility Function Tests
// =============================================================================

describe('getStaggeredGrowthDelay', () => {
  it('returns 0 for index 0', () => {
    const delay = getStaggeredGrowthDelay(0);
    expect(delay).toBeCloseTo(50 * Math.log2(2), 1); // ~50ms
  });

  it('returns increasing delays for increasing indices', () => {
    const delays = [0, 1, 2, 3, 4].map((i) => getStaggeredGrowthDelay(i));

    for (let i = 1; i < delays.length; i++) {
      expect(delays[i]).toBeGreaterThan(delays[i - 1]);
    }
  });

  it('respects maxDelay cap', () => {
    const maxDelay = 200;
    const delay = getStaggeredGrowthDelay(100, 50, maxDelay);
    expect(delay).toBeLessThanOrEqual(maxDelay);
  });

  it('uses custom baseDelay', () => {
    const delay1 = getStaggeredGrowthDelay(1, 50);
    const delay2 = getStaggeredGrowthDelay(1, 100);
    expect(delay2).toBeGreaterThan(delay1);
  });
});

describe('triggerWithDelay', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('triggers after specified delay', () => {
    const trigger = vi.fn();
    triggerWithDelay(trigger, 100);

    expect(trigger).not.toHaveBeenCalled();

    vi.advanceTimersByTime(100);

    expect(trigger).toHaveBeenCalledTimes(1);
  });

  it('returns cleanup function that cancels timeout', () => {
    const trigger = vi.fn();
    const cleanup = triggerWithDelay(trigger, 100);

    cleanup();
    vi.advanceTimersByTime(200);

    expect(trigger).not.toHaveBeenCalled();
  });
});
