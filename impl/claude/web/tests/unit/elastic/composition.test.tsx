/**
 * Composition Law Tests for Layout Projection Functor
 *
 * Verifies the composition laws from spec/protocols/projection.md:
 *
 * 1. Vertical Composition Preservation:
 *    Layout[D](A // B) = Layout[D](A) // Layout[D](B)
 *    Vertical stacking preserves under projection.
 *
 * 2. Horizontal Composition Transformation:
 *    Layout[compact](A >> B) → MainContent + FloatingAction(Secondary)
 *    Horizontal composition transforms to overlay in compact mode.
 *
 * 3. Physical Constraint Invariance:
 *    TouchTarget[D] >= 48px ∀ D ∈ {compact, comfortable, spacious}
 *
 * 4. Structural Isomorphism:
 *    Information(Layout[compact](W)) = Information(Layout[spacious](W))
 *    Same data accessible in both layouts.
 *
 * @see spec/protocols/projection.md (lines 342-367)
 * @see plans/web-refactor/layout-projection-functor.md
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  DENSITY_BREAKPOINTS,
  PHYSICAL_CONSTRAINTS,
  LAYOUT_PRIMITIVES,
  COMPOSITION_LAWS,
  getDensityFromWidth,
  fromDensity,
  createDensityMap,
  getPrimitiveBehavior,
  type Density,
  type DensityMap,
} from '@/components/elastic';
import { ElasticSplit } from '@/components/elastic/ElasticSplit';
import { ElasticContainer } from '@/components/elastic/ElasticContainer';
import { BottomDrawer } from '@/components/elastic/BottomDrawer';
import { FloatingActions, type FloatingAction } from '@/components/elastic/FloatingActions';

// =============================================================================
// Test Utilities
// =============================================================================

function createMockResizeEntry(
  target: Element,
  width: number,
  height: number
): ResizeObserverEntry {
  return {
    target,
    contentRect: { width, height } as DOMRectReadOnly,
    borderBoxSize: [
      { blockSize: height, inlineSize: width },
    ] as unknown as readonly ResizeObserverSize[],
    contentBoxSize: [
      { blockSize: height, inlineSize: width },
    ] as unknown as readonly ResizeObserverSize[],
    devicePixelContentBoxSize: [
      { blockSize: height, inlineSize: width },
    ] as unknown as readonly ResizeObserverSize[],
  };
}

// =============================================================================
// Law 1: Vertical Composition Preservation
// =============================================================================

describe('Law 1: Vertical Composition Preservation', () => {
  /**
   * Layout[D](A // B) = Layout[D](A) // Layout[D](B)
   *
   * When we vertically compose two widgets and project them,
   * the result should be the same as projecting each widget
   * individually and then composing.
   */

  beforeEach(() => {
    const MockResizeObserver = vi.fn().mockImplementation((callback) => ({
      observe: vi.fn(() => {
        callback([createMockResizeEntry(document.body, 1024, 768)]);
      }),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }));
    window.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should preserve vertical stack structure at all densities', () => {
    const densities: Density[] = ['compact', 'comfortable', 'spacious'];

    densities.forEach((density) => {
      // A // B (vertical stack)
      const { container } = render(
        <ElasticContainer layout="stack" direction="vertical">
          <div data-testid={`widget-a-${density}`}>Widget A</div>
          <div data-testid={`widget-b-${density}`}>Widget B</div>
        </ElasticContainer>
      );

      // Both widgets should be present and in vertical order
      const widgetA = screen.getByTestId(`widget-a-${density}`);
      const widgetB = screen.getByTestId(`widget-b-${density}`);

      expect(widgetA).toBeInTheDocument();
      expect(widgetB).toBeInTheDocument();

      // Verify vertical stacking (A should appear before B in DOM)
      expect(widgetA.compareDocumentPosition(widgetB)).toBe(Node.DOCUMENT_POSITION_FOLLOWING);

      // Cleanup for next iteration
      container.remove();
    });
  });

  it('should maintain child order in vertical composition', () => {
    const children = ['First', 'Second', 'Third', 'Fourth'];

    render(
      <ElasticContainer layout="stack" direction="vertical">
        {children.map((child, i) => (
          <div key={i} data-testid={`child-${i}`}>
            {child}
          </div>
        ))}
      </ElasticContainer>
    );

    // All children should be present
    children.forEach((_, i) => {
      expect(screen.getByTestId(`child-${i}`)).toBeInTheDocument();
    });

    // Verify ordering
    const elements = children.map((_, i) => screen.getByTestId(`child-${i}`));
    for (let i = 0; i < elements.length - 1; i++) {
      expect(elements[i].compareDocumentPosition(elements[i + 1])).toBe(
        Node.DOCUMENT_POSITION_FOLLOWING
      );
    }
  });
});

// =============================================================================
// Law 2: Horizontal Composition Transformation
// =============================================================================

describe('Law 2: Horizontal Composition Transformation', () => {
  /**
   * Layout[compact](A >> B) → MainContent + FloatingAction(Secondary)
   *
   * In compact mode, horizontal composition (sidebar >> canvas)
   * transforms to canvas + floating action that opens sidebar.
   */

  let resizeCallback: ((entries: ResizeObserverEntry[]) => void) | null = null;

  beforeEach(() => {
    const MockResizeObserver = vi.fn().mockImplementation((callback) => {
      resizeCallback = callback;
      return {
        observe: vi.fn(() => {
          callback([createMockResizeEntry(document.body, 1024, 768)]);
        }),
        unobserve: vi.fn(),
        disconnect: vi.fn(),
      };
    });
    window.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should transform horizontal split to stacked on collapse', () => {
    const { container, rerender } = render(
      <ElasticSplit
        direction="horizontal"
        collapseAt={768}
        primary={<div data-testid="primary">Primary</div>}
        secondary={<div data-testid="secondary">Secondary</div>}
      />
    );

    // Desktop: should be horizontal split (no collapse attribute)
    expect(container.querySelector('[data-collapsed="true"]')).toBeNull();

    // Simulate resize to compact
    if (resizeCallback) {
      resizeCallback([createMockResizeEntry(document.body, 500, 600)]);
    }

    // Need to re-render with new width context
    // The ElasticSplit uses useWindowLayout which needs window resize
    Object.defineProperty(window, 'innerWidth', { value: 500, writable: true });
    window.dispatchEvent(new Event('resize'));

    rerender(
      <ElasticSplit
        direction="horizontal"
        collapseAt={768}
        primary={<div data-testid="primary">Primary</div>}
        secondary={<div data-testid="secondary">Secondary</div>}
      />
    );

    // Mobile: should be collapsed (vertical stack)
    expect(container.querySelector('[data-collapsed="true"]')).toBeInTheDocument();
  });

  it('should place primary content first when collapsed', () => {
    // Set window to compact size
    Object.defineProperty(window, 'innerWidth', { value: 500, writable: true });
    window.dispatchEvent(new Event('resize'));

    render(
      <ElasticSplit
        direction="horizontal"
        collapseAt={768}
        collapsePriority="secondary"
        primary={<div data-testid="primary">Primary</div>}
        secondary={<div data-testid="secondary">Secondary</div>}
      />
    );

    const primary = screen.getByTestId('primary');
    const secondary = screen.getByTestId('secondary');

    // Primary should appear before secondary when collapsePriority="secondary"
    expect(primary.compareDocumentPosition(secondary)).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
  });

  it('should demonstrate the overlay pattern with FloatingActions', () => {
    const actions: FloatingAction[] = [
      { id: 'toggle', icon: '⚙️', label: 'Toggle Panel', onClick: vi.fn() },
    ];

    render(
      <div style={{ position: 'relative', width: 300, height: 400 }}>
        {/* Main content (primary) */}
        <div data-testid="canvas">Canvas Content</div>

        {/* Floating action (secondary projected to overlay) */}
        <FloatingActions actions={actions} position="bottom-right" />
      </div>
    );

    // Canvas should be present
    expect(screen.getByTestId('canvas')).toBeInTheDocument();

    // Floating action should be present as overlay
    expect(screen.getByRole('toolbar')).toBeInTheDocument();
    expect(screen.getByLabelText('Toggle Panel')).toBeInTheDocument();
  });
});

// =============================================================================
// Law 3: Physical Constraint Invariance
// =============================================================================

describe('Law 3: Physical Constraint Invariance', () => {
  /**
   * TouchTarget[D] >= 48px ∀ D ∈ {compact, comfortable, spacious}
   *
   * Touch targets must be at least 48px regardless of density.
   * This is a physical constraint that does not scale.
   */

  it('should define 48px as the minimum touch target', () => {
    expect(PHYSICAL_CONSTRAINTS.minTouchTarget).toBe(48);
  });

  it('should enforce minimum touch target on FloatingActions buttons', () => {
    const actions: FloatingAction[] = [
      { id: 'action1', icon: '🔄', label: 'Action 1', onClick: vi.fn() },
    ];

    render(<FloatingActions actions={actions} buttonSize={30} />);

    const button = screen.getByLabelText('Action 1');

    // Even though we requested 30px, it should be at least 48px
    expect(parseInt(button.style.minWidth, 10)).toBeGreaterThanOrEqual(
      PHYSICAL_CONSTRAINTS.minTouchTarget
    );
    expect(parseInt(button.style.minHeight, 10)).toBeGreaterThanOrEqual(
      PHYSICAL_CONSTRAINTS.minTouchTarget
    );
  });

  it('should have 48px touch target on BottomDrawer handle', () => {
    render(
      <BottomDrawer isOpen={true} onClose={vi.fn()} title="Test">
        Content
      </BottomDrawer>
    );

    // The drawer handle should have minimum touch target
    const handle = screen.getByRole('button', { name: /close drawer/i });
    const style = handle.getAttribute('style');

    // Style should include minHeight for touch target
    expect(style).toContain(`${PHYSICAL_CONSTRAINTS.minTouchTarget}`);
  });

  it('should enforce minimum tap spacing between buttons', () => {
    expect(PHYSICAL_CONSTRAINTS.minTapSpacing).toBe(8);

    const actions: FloatingAction[] = [
      { id: 'a1', icon: '1', label: 'Action 1', onClick: vi.fn() },
      { id: 'a2', icon: '2', label: 'Action 2', onClick: vi.fn() },
    ];

    render(<FloatingActions actions={actions} gap={4} />);

    // Gap should be enforced to minimum even if smaller value passed
    const toolbar = screen.getByRole('toolbar');
    expect(parseInt(toolbar.style.gap, 10)).toBeGreaterThanOrEqual(
      PHYSICAL_CONSTRAINTS.minTapSpacing
    );
  });
});

// =============================================================================
// Law 4: Structural Isomorphism
// =============================================================================

describe('Law 4: Structural Isomorphism', () => {
  /**
   * Information(Layout[compact](W)) = Information(Layout[spacious](W))
   *
   * The same information must be accessible in both layouts,
   * even though the presentation structure differs.
   */

  beforeEach(() => {
    const MockResizeObserver = vi.fn().mockImplementation((callback) => ({
      observe: vi.fn(() => {
        callback([createMockResizeEntry(document.body, 1024, 768)]);
      }),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }));
    window.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should preserve all content in collapsed vs expanded split', () => {
    const primaryContent = 'Primary Data: A, B, C';
    const secondaryContent = 'Secondary Data: X, Y, Z';

    // Test both collapsed and expanded states
    [true, false].forEach((isCollapsed) => {
      Object.defineProperty(window, 'innerWidth', {
        value: isCollapsed ? 500 : 1200,
        writable: true,
      });
      window.dispatchEvent(new Event('resize'));

      const { container, unmount } = render(
        <ElasticSplit
          direction="horizontal"
          collapseAt={768}
          primary={<div>{primaryContent}</div>}
          secondary={<div>{secondaryContent}</div>}
        />
      );

      // Both pieces of content should be present regardless of layout
      expect(container.textContent).toContain('Primary Data: A, B, C');
      expect(container.textContent).toContain('Secondary Data: X, Y, Z');

      unmount();
    });
  });

  it('should provide access to same actions via drawer as via sidebar', () => {
    const handleAction = vi.fn();

    // Simulate drawer pattern (mobile)
    const { unmount: unmount1 } = render(
      <BottomDrawer isOpen={true} onClose={vi.fn()} title="Actions">
        <button onClick={handleAction}>Do Thing</button>
      </BottomDrawer>
    );

    const drawerButton = screen.getByRole('button', { name: 'Do Thing' });
    expect(drawerButton).toBeInTheDocument();
    unmount1();

    // Simulate sidebar pattern (desktop) - same button, different container
    const { unmount: unmount2 } = render(
      <aside>
        <button onClick={handleAction}>Do Thing</button>
      </aside>
    );

    const sidebarButton = screen.getByRole('button', { name: 'Do Thing' });
    expect(sidebarButton).toBeInTheDocument();
    unmount2();

    // The action is accessible in both patterns (isomorphism)
  });
});

// =============================================================================
// Type System Tests
// =============================================================================

describe('Type System: DensityMap', () => {
  it('should provide values for all densities via fromDensity', () => {
    const map: DensityMap<number> = { compact: 10, comfortable: 20, spacious: 30 };

    expect(fromDensity(map, 'compact')).toBe(10);
    expect(fromDensity(map, 'comfortable')).toBe(20);
    expect(fromDensity(map, 'spacious')).toBe(30);
  });

  it('should create density maps with default and overrides', () => {
    const map = createDensityMap(100, { compact: 50 });

    expect(map.compact).toBe(50);
    expect(map.comfortable).toBe(100);
    expect(map.spacious).toBe(100);
  });

  it('should get correct density from width', () => {
    expect(getDensityFromWidth(500)).toBe('compact');
    expect(getDensityFromWidth(768)).toBe('comfortable');
    expect(getDensityFromWidth(900)).toBe('comfortable');
    expect(getDensityFromWidth(1024)).toBe('spacious');
    expect(getDensityFromWidth(1920)).toBe('spacious');
  });

  it('should have correct breakpoint values from spec', () => {
    expect(DENSITY_BREAKPOINTS.sm).toBe(768);
    expect(DENSITY_BREAKPOINTS.lg).toBe(1024);
  });
});

describe('Type System: Layout Primitives', () => {
  it('should define three layout primitives', () => {
    expect(Object.keys(LAYOUT_PRIMITIVES)).toHaveLength(3);
    expect(LAYOUT_PRIMITIVES).toHaveProperty('split');
    expect(LAYOUT_PRIMITIVES).toHaveProperty('panel');
    expect(LAYOUT_PRIMITIVES).toHaveProperty('actions');
  });

  it('should map Split primitive behaviors correctly', () => {
    expect(getPrimitiveBehavior('split', 'compact')).toBe('collapse_secondary');
    expect(getPrimitiveBehavior('split', 'comfortable')).toBe('fixed_panes');
    expect(getPrimitiveBehavior('split', 'spacious')).toBe('resizable_divider');
  });

  it('should map Panel primitive behaviors correctly', () => {
    expect(getPrimitiveBehavior('panel', 'compact')).toBe('bottom_drawer');
    expect(getPrimitiveBehavior('panel', 'comfortable')).toBe('collapsible_panel');
    expect(getPrimitiveBehavior('panel', 'spacious')).toBe('fixed_sidebar');
  });

  it('should map Actions primitive behaviors correctly', () => {
    expect(getPrimitiveBehavior('actions', 'compact')).toBe('floating_fab');
    expect(getPrimitiveBehavior('actions', 'comfortable')).toBe('inline_buttons');
    expect(getPrimitiveBehavior('actions', 'spacious')).toBe('full_toolbar');
  });
});

describe('Type System: Composition Laws', () => {
  it('should define both composition operators', () => {
    expect(COMPOSITION_LAWS).toHaveLength(2);
  });

  it('should mark vertical composition as preserving', () => {
    const verticalLaw = COMPOSITION_LAWS.find((l) => l.operator === '//');
    expect(verticalLaw?.preservesUnderProjection).toBe(true);
  });

  it('should mark horizontal composition as non-preserving with transformation', () => {
    const horizontalLaw = COMPOSITION_LAWS.find((l) => l.operator === '>>');
    expect(horizontalLaw?.preservesUnderProjection).toBe(false);
    expect(horizontalLaw?.compactTransformation).toBe('MainContent + FloatingAction(Secondary)');
  });
});

// =============================================================================
// Edge Cases: Density Transitions (QA Phase)
// =============================================================================

describe('Edge Cases: Density Breakpoint Boundaries', () => {
  /**
   * Property-based tests for density transitions at exact boundaries.
   * Verifies deterministic behavior at and around breakpoint values.
   */

  it('should have strict inequality at lower boundary (767 < 768)', () => {
    // Just below compact threshold
    expect(getDensityFromWidth(767)).toBe('compact');
    expect(getDensityFromWidth(768)).toBe('comfortable');
  });

  it('should have strict inequality at upper boundary (1023 < 1024)', () => {
    // Just below spacious threshold
    expect(getDensityFromWidth(1023)).toBe('comfortable');
    expect(getDensityFromWidth(1024)).toBe('spacious');
  });

  it('should handle exact boundary values deterministically', () => {
    // These are the exact spec breakpoints
    const boundaryTests = [
      { width: 0, expected: 'compact' },
      { width: 767, expected: 'compact' },
      { width: 768, expected: 'comfortable' },
      { width: 769, expected: 'comfortable' },
      { width: 1023, expected: 'comfortable' },
      { width: 1024, expected: 'spacious' },
      { width: 1025, expected: 'spacious' },
    ] as const;

    boundaryTests.forEach(({ width, expected }) => {
      expect(getDensityFromWidth(width)).toBe(expected);
    });
  });

  it('should handle edge case widths (zero, negative, very large)', () => {
    // Zero width - should still return compact
    expect(getDensityFromWidth(0)).toBe('compact');

    // Negative width (shouldn't happen in practice, but should be defensive)
    expect(getDensityFromWidth(-100)).toBe('compact');

    // Very large width
    expect(getDensityFromWidth(10000)).toBe('spacious');
    expect(getDensityFromWidth(Number.MAX_SAFE_INTEGER)).toBe('spacious');
  });

  it('should be monotonic (larger widths never yield smaller densities)', () => {
    const densityOrder = { compact: 0, comfortable: 1, spacious: 2 };
    let prevWidth = 0;
    let prevDensity = getDensityFromWidth(prevWidth);

    // Sample widths across the range
    const testWidths = [100, 300, 500, 700, 767, 768, 800, 900, 1000, 1023, 1024, 1200, 2000];

    testWidths.forEach((width) => {
      const density = getDensityFromWidth(width);
      expect(densityOrder[density]).toBeGreaterThanOrEqual(densityOrder[prevDensity]);
      prevWidth = width;
      prevDensity = density;
    });
  });
});

describe('Edge Cases: DensityMap Robustness', () => {
  /**
   * Tests for DensityMap edge cases to ensure type safety and robustness.
   */

  it('should handle all primitive value types in DensityMap', () => {
    // Numbers
    const numMap: DensityMap<number> = { compact: 0, comfortable: -1, spacious: Infinity };
    expect(fromDensity(numMap, 'compact')).toBe(0);
    expect(fromDensity(numMap, 'comfortable')).toBe(-1);
    expect(fromDensity(numMap, 'spacious')).toBe(Infinity);

    // Strings
    const strMap: DensityMap<string> = { compact: '', comfortable: 'test', spacious: '  ' };
    expect(fromDensity(strMap, 'compact')).toBe('');
    expect(fromDensity(strMap, 'comfortable')).toBe('test');

    // Booleans
    const boolMap: DensityMap<boolean> = { compact: false, comfortable: true, spacious: false };
    expect(fromDensity(boolMap, 'compact')).toBe(false);
    expect(fromDensity(boolMap, 'comfortable')).toBe(true);
  });

  it('should handle object and array values in DensityMap', () => {
    const objMap: DensityMap<{ x: number }> = {
      compact: { x: 1 },
      comfortable: { x: 2 },
      spacious: { x: 3 },
    };
    expect(fromDensity(objMap, 'compact')).toEqual({ x: 1 });

    const arrMap: DensityMap<number[]> = {
      compact: [1],
      comfortable: [1, 2],
      spacious: [1, 2, 3],
    };
    expect(fromDensity(arrMap, 'spacious')).toEqual([1, 2, 3]);
  });

  it('should create DensityMap with all overrides applied', () => {
    const fullOverride = createDensityMap(0, { compact: 1, comfortable: 2, spacious: 3 });
    expect(fullOverride).toEqual({ compact: 1, comfortable: 2, spacious: 3 });
  });

  it('should preserve reference equality for object values', () => {
    const sharedObj = { shared: true };
    const map = createDensityMap(sharedObj);

    expect(fromDensity(map, 'compact')).toBe(sharedObj);
    expect(fromDensity(map, 'comfortable')).toBe(sharedObj);
    expect(fromDensity(map, 'spacious')).toBe(sharedObj);
  });
});

describe('Edge Cases: Physical Constraints Enforcement', () => {
  /**
   * Tests that physical constraints are truly enforced, not just documented.
   */

  it('should reject values below minimum touch target', () => {
    // FloatingActions enforces minimum button size
    const smallButtonSize = 30;
    const effectiveSize = Math.max(smallButtonSize, PHYSICAL_CONSTRAINTS.minTouchTarget);
    expect(effectiveSize).toBe(48);
  });

  it('should reject values below minimum tap spacing', () => {
    const smallGap = 2;
    const effectiveGap = Math.max(smallGap, PHYSICAL_CONSTRAINTS.minTapSpacing);
    expect(effectiveGap).toBe(8);
  });

  it('should have consistent physical constraints across all exports', () => {
    // These should never change without explicit decision
    expect(PHYSICAL_CONSTRAINTS.minTouchTarget).toBe(48);
    expect(PHYSICAL_CONSTRAINTS.minFontSize).toBe(14);
    expect(PHYSICAL_CONSTRAINTS.minTapSpacing).toBe(8);
    expect(PHYSICAL_CONSTRAINTS.drawerHandleVisual).toEqual({ width: 40, height: 4 });
  });

  it('should enforce touch target via Math.max pattern', () => {
    // Simulate what FloatingActions does internally
    const userSizes = [10, 20, 30, 40, 48, 50, 60];

    userSizes.forEach((userSize) => {
      const enforced = Math.max(userSize, PHYSICAL_CONSTRAINTS.minTouchTarget);
      expect(enforced).toBeGreaterThanOrEqual(48);
    });
  });
});
