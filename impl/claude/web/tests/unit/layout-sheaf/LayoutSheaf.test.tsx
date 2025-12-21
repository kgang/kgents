/**
 * Tests for Layout Sheaf - Global Coherence from Local Components
 *
 * Verifies the four sheaf laws:
 * 1. Stability - Height doesn't change on re-render
 * 2. Containment - All claims fit (max wins)
 * 3. Monotonicity - Adding claims only increases height
 * 4. Idempotence - Duplicate claims have no effect
 *
 * @see spec/ui/layout-sheaf.md
 */

import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { render, screen } from '@testing-library/react';
import type { ReactNode } from 'react';
import {
  LayoutSheafProvider,
  useLayoutSheaf,
  useLayoutClaim,
  ReservedSlot,
  FadeTransition,
} from '@/components/layout-sheaf';

// =============================================================================
// Test Wrapper
// =============================================================================

function TestWrapper({ children }: { children: ReactNode }) {
  return <LayoutSheafProvider>{children}</LayoutSheafProvider>;
}

// =============================================================================
// Law 1: Stability
// =============================================================================

describe('Law 1: Stability', () => {
  it('maintains height across re-renders', () => {
    const { result, rerender } = renderHook(
      () => {
        const sheaf = useLayoutSheaf();
        useLayoutClaim('slot-a', 16);
        return sheaf.getSlotHeight('slot-a');
      },
      { wrapper: TestWrapper }
    );

    const initialHeight = result.current;
    rerender();
    expect(result.current).toBe(initialHeight);
  });

  it('slot height is stable when claims are unchanged', () => {
    const heights: number[] = [];

    const { rerender } = renderHook(
      () => {
        const sheaf = useLayoutSheaf();
        useLayoutClaim('stable-slot', 24);
        heights.push(sheaf.getSlotHeight('stable-slot'));
        return null;
      },
      { wrapper: TestWrapper }
    );

    // Re-render multiple times
    rerender();
    rerender();
    rerender();

    // All heights should be identical
    expect(heights.every((h) => h === heights[0])).toBe(true);
    expect(heights[0]).toBe(24);
  });
});

// =============================================================================
// Law 2: Containment
// =============================================================================

describe('Law 2: Containment', () => {
  it('resolves multiple claims to maximum (all must fit)', () => {
    const { result } = renderHook(
      () => {
        const sheaf = useLayoutSheaf();
        useLayoutClaim('slot-a', 16);
        useLayoutClaim('slot-a', 24);
        return sheaf.getSlotHeight('slot-a');
      },
      { wrapper: TestWrapper }
    );

    // Maximum claim wins
    expect(result.current).toBe(24);
  });

  it('all claims fit within resolved height', () => {
    const claims = [12, 20, 16, 8];
    const { result } = renderHook(
      () => {
        const sheaf = useLayoutSheaf();
        claims.forEach((h) => useLayoutClaim('multi-claim', h));
        return sheaf.getSlotHeight('multi-claim');
      },
      { wrapper: TestWrapper }
    );

    // Height should be max of all claims
    expect(result.current).toBe(Math.max(...claims));
    // All claims should fit
    claims.forEach((claim) => {
      expect(claim).toBeLessThanOrEqual(result.current);
    });
  });

  it('applies maxHeight constraint', () => {
    const { result } = renderHook(
      () => {
        const sheaf = useLayoutSheaf();
        sheaf.registerSlot({
          id: 'constrained-slot',
          constraints: { maxHeight: 20 },
          priority: 0,
        });
        useLayoutClaim('constrained-slot', 30);
        return sheaf.getSlotHeight('constrained-slot');
      },
      { wrapper: TestWrapper }
    );

    // Should be capped at maxHeight
    expect(result.current).toBe(20);
  });

  it('applies minHeight constraint', () => {
    const { result } = renderHook(
      () => {
        const sheaf = useLayoutSheaf();
        sheaf.registerSlot({
          id: 'min-slot',
          constraints: { minHeight: 16 },
          priority: 0,
        });
        return sheaf.getSlotHeight('min-slot');
      },
      { wrapper: TestWrapper }
    );

    // Should be at least minHeight even with no claims
    expect(result.current).toBe(16);
  });
});

// =============================================================================
// Law 3: Monotonicity
// =============================================================================

describe('Law 3: Monotonicity', () => {
  it('adding claims only increases height, never decreases', () => {
    const { result } = renderHook(
      () => {
        const sheaf = useLayoutSheaf();
        return {
          claim: sheaf.claim,
          getHeight: () => sheaf.getSlotHeight('mono-slot'),
        };
      },
      { wrapper: TestWrapper }
    );

    // Start with one claim
    act(() => {
      result.current.claim('mono-slot', 16);
    });
    const h1 = result.current.getHeight();

    // Add a larger claim
    act(() => {
      result.current.claim('mono-slot', 24);
    });
    const h2 = result.current.getHeight();

    // Height should only increase
    expect(h2).toBeGreaterThanOrEqual(h1);
    expect(h2).toBe(24);
  });

  it('adding smaller claim does not decrease height', () => {
    const { result } = renderHook(
      () => {
        const sheaf = useLayoutSheaf();
        return {
          claim: sheaf.claim,
          getHeight: () => sheaf.getSlotHeight('mono-slot-2'),
        };
      },
      { wrapper: TestWrapper }
    );

    // Start with larger claim
    act(() => {
      result.current.claim('mono-slot-2', 32);
    });
    const h1 = result.current.getHeight();

    // Add a smaller claim
    act(() => {
      result.current.claim('mono-slot-2', 16);
    });
    const h2 = result.current.getHeight();

    // Height should not decrease
    expect(h2).toBe(h1);
    expect(h2).toBe(32);
  });
});

// =============================================================================
// Law 4: Idempotence
// =============================================================================

describe('Law 4: Idempotence', () => {
  it('duplicate claims have no additional effect', () => {
    const { result } = renderHook(
      () => {
        const sheaf = useLayoutSheaf();
        return {
          claim: sheaf.claim,
          getHeight: () => sheaf.getSlotHeight('idem-slot'),
        };
      },
      { wrapper: TestWrapper }
    );

    // First claim
    act(() => {
      result.current.claim('idem-slot', 16);
    });
    const h1 = result.current.getHeight();

    // Duplicate claim (same height)
    act(() => {
      result.current.claim('idem-slot', 16);
    });
    const h2 = result.current.getHeight();

    // Height should be unchanged
    expect(h2).toBe(h1);
    expect(h2).toBe(16);
  });

  it('multiple identical claims resolve to same height', () => {
    const { result } = renderHook(
      () => {
        const sheaf = useLayoutSheaf();
        return {
          claim: sheaf.claim,
          getHeight: () => sheaf.getSlotHeight('idem-slot-2'),
        };
      },
      { wrapper: TestWrapper }
    );

    // Add many identical claims
    act(() => {
      for (let i = 0; i < 10; i++) {
        result.current.claim('idem-slot-2', 20);
      }
    });

    // Height should be just the claimed value
    expect(result.current.getHeight()).toBe(20);
  });
});

// =============================================================================
// Claim Lifecycle
// =============================================================================

describe('Claim Lifecycle', () => {
  it('releases claim correctly', () => {
    const { result } = renderHook(
      () => {
        const sheaf = useLayoutSheaf();
        return {
          claim: sheaf.claim,
          getHeight: () => sheaf.getSlotHeight('lifecycle-slot'),
        };
      },
      { wrapper: TestWrapper }
    );

    let handle1: ReturnType<typeof result.current.claim>;
    let handle2: ReturnType<typeof result.current.claim>;

    // Add two claims
    act(() => {
      handle1 = result.current.claim('lifecycle-slot', 16);
      handle2 = result.current.claim('lifecycle-slot', 24);
    });

    expect(result.current.getHeight()).toBe(24);

    // Release the larger claim
    act(() => {
      handle2!.release();
    });

    // Height should drop to the remaining claim
    expect(result.current.getHeight()).toBe(16);

    // Release the remaining claim
    act(() => {
      handle1!.release();
    });

    // Height should be 0 (no claims)
    expect(result.current.getHeight()).toBe(0);
  });

  it('updates claim height dynamically', () => {
    const { result } = renderHook(
      () => {
        const sheaf = useLayoutSheaf();
        return {
          claim: sheaf.claim,
          getHeight: () => sheaf.getSlotHeight('update-slot'),
        };
      },
      { wrapper: TestWrapper }
    );

    let handle: ReturnType<typeof result.current.claim>;

    act(() => {
      handle = result.current.claim('update-slot', 16);
    });

    expect(result.current.getHeight()).toBe(16);

    // Update the claim
    act(() => {
      handle!.update(32);
    });

    expect(result.current.getHeight()).toBe(32);
  });
});

// =============================================================================
// Component Integration
// =============================================================================

describe('ReservedSlot Component', () => {
  it('renders with stable height from claim', () => {
    function TestComponent() {
      useLayoutClaim('test-slot', 40);
      return (
        <ReservedSlot id="test-slot" testId="reserved">
          <div>Content</div>
        </ReservedSlot>
      );
    }

    render(
      <LayoutSheafProvider>
        <TestComponent />
      </LayoutSheafProvider>
    );

    const slot = screen.getByTestId('reserved');
    expect(slot).toHaveStyle({ height: '40px', minHeight: '40px' });
  });

  it('renders fallback when no children', () => {
    function TestComponent() {
      useLayoutClaim('fallback-slot', 24);
      return (
        <ReservedSlot id="fallback-slot" fallback={<span>Fallback</span>}>
          {null}
        </ReservedSlot>
      );
    }

    render(
      <LayoutSheafProvider>
        <TestComponent />
      </LayoutSheafProvider>
    );

    expect(screen.getByText('Fallback')).toBeInTheDocument();
  });

  it('applies constraints from props', () => {
    function TestComponent() {
      useLayoutClaim('constrained-component', 50);
      return (
        <ReservedSlot
          id="constrained-component"
          constraints={{ maxHeight: 30 }}
          testId="constrained"
        >
          <div>Content</div>
        </ReservedSlot>
      );
    }

    render(
      <LayoutSheafProvider>
        <TestComponent />
      </LayoutSheafProvider>
    );

    const slot = screen.getByTestId('constrained');
    // Should be capped at maxHeight
    expect(slot).toHaveStyle({ height: '30px' });
  });
});

describe('FadeTransition Component', () => {
  it('shows content when show is true', () => {
    render(
      <FadeTransition show={true}>
        <span>Visible</span>
      </FadeTransition>
    );

    const container = screen.getByText('Visible').parentElement;
    expect(container).toHaveStyle({ opacity: '1' });
  });

  it('hides content when show is false', () => {
    render(
      <FadeTransition show={false}>
        <span>Hidden</span>
      </FadeTransition>
    );

    const container = screen.getByText('Hidden').parentElement;
    expect(container).toHaveStyle({ opacity: '0' });
  });

  it('disables pointer events when hidden', () => {
    render(
      <FadeTransition show={false}>
        <span>Hidden</span>
      </FadeTransition>
    );

    const container = screen.getByText('Hidden').parentElement;
    expect(container).toHaveStyle({ pointerEvents: 'none' });
  });

  it('applies custom duration', () => {
    render(
      <FadeTransition show={true} duration={300}>
        <span>Slow fade</span>
      </FadeTransition>
    );

    const container = screen.getByText('Slow fade').parentElement;
    expect(container).toHaveStyle({ transition: 'opacity 300ms ease-out' });
  });
});

// =============================================================================
// Edge Cases
// =============================================================================

describe('Edge Cases', () => {
  it('handles slot with no claims', () => {
    const { result } = renderHook(
      () => {
        const sheaf = useLayoutSheaf();
        sheaf.registerSlot({
          id: 'empty-slot',
          constraints: {},
          priority: 0,
        });
        return sheaf.getSlotHeight('empty-slot');
      },
      { wrapper: TestWrapper }
    );

    expect(result.current).toBe(0);
  });

  it('handles unregistered slot gracefully', () => {
    const { result } = renderHook(
      () => {
        const sheaf = useLayoutSheaf();
        return sheaf.getSlotHeight('nonexistent-slot');
      },
      { wrapper: TestWrapper }
    );

    expect(result.current).toBe(0);
  });

  it('throws when used outside provider', () => {
    expect(() => {
      renderHook(() => useLayoutSheaf());
    }).toThrow('useLayoutSheaf must be used within LayoutSheafProvider');
  });

  it('handles rapid claim/release cycles', () => {
    const { result } = renderHook(
      () => {
        const sheaf = useLayoutSheaf();
        return {
          claim: sheaf.claim,
          getHeight: () => sheaf.getSlotHeight('rapid-slot'),
        };
      },
      { wrapper: TestWrapper }
    );

    // Rapid claim/release
    act(() => {
      for (let i = 0; i < 100; i++) {
        const handle = result.current.claim('rapid-slot', 16);
        handle.release();
      }
    });

    // Should be back to 0
    expect(result.current.getHeight()).toBe(0);
  });
});
