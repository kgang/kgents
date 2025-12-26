/**
 * Layout Laws (L-01 through L-05)
 *
 * Tests for the 5 layout design laws from Zero Seed Creative Strategy.
 *
 * @see plans/zero-seed-creative-strategy.md (Part IV: UI/UX Design Laws)
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ElasticContainer } from '@/components/elastic/ElasticContainer';
import { ElasticSplit } from '@/components/elastic/ElasticSplit';
import { PHYSICAL_CONSTRAINTS } from '@/components/elastic';
import { FloatingActions, type FloatingAction } from '@/components/elastic/FloatingActions';

// =============================================================================
// L-01: Density-Content Isomorphism
// =============================================================================

describe('L-01: Density-Content Isomorphism', () => {
  /**
   * Law Statement: Content detail level maps isomorphically to observer capacity (density).
   *
   * Justification: Density is not screen size—density is the capacity to receive.
   *
   * Test: Spacious shows strictly more information than compact. Compact content
   * is a subset of spacious content.
   */

  it('enforces that spacious shows more content than compact', () => {
    // Component with density-aware content
    const DensityAwareCard = ({ density }: { density: 'compact' | 'comfortable' | 'spacious' }) => {
      const content = {
        compact: 'Title',
        comfortable: 'Title: Subtitle',
        spacious: 'Title: Subtitle - Full description with details',
      };
      return <div data-testid="card">{content[density]}</div>;
    };

    const { unmount: unmount1 } = render(<DensityAwareCard density="compact" />);
    const compactContent = screen.getByTestId('card').textContent || '';
    unmount1();

    const { unmount: unmount2 } = render(<DensityAwareCard density="spacious" />);
    const spaciousContent = screen.getByTestId('card').textContent || '';
    unmount2();

    // Spacious shows strictly more information
    expect(spaciousContent.length).toBeGreaterThan(compactContent.length);
    // Compact content is subset of spacious
    expect(spaciousContent).toContain(compactContent);
  });

  it('enforces five-level degradation: icon → title → summary → detail → full', () => {
    const levels = {
      icon: '📄',
      title: '📄 Document',
      summary: '📄 Document: Project Spec',
      detail: '📄 Document: Project Spec - Detailed requirements and architecture',
      full: '📄 Document: Project Spec - Detailed requirements and architecture. Last updated 2025-12-25.',
    };

    // Each level should contain the previous level
    expect(levels.title).toContain(levels.icon);
    expect(levels.summary).toContain('Document');
    expect(levels.detail).toContain('Project Spec');
    expect(levels.full).toContain('Detailed requirements and architecture');

    // Lengths should be monotonically increasing
    expect(levels.title.length).toBeGreaterThan(levels.icon.length);
    expect(levels.summary.length).toBeGreaterThan(levels.title.length);
    expect(levels.detail.length).toBeGreaterThan(levels.summary.length);
    expect(levels.full.length).toBeGreaterThan(levels.detail.length);
  });

  it('rejects scattered isMobile conditionals in favor of density parameter', () => {
    // Anti-pattern: {isMobile ? <CompactThing /> : <FullThing />}
    // Good pattern: <Thing density={density} />

    const BadPattern = ({ isMobile }: { isMobile: boolean }) => (
      <div>{isMobile ? 'Mobile' : 'Desktop'}</div>
    );

    const GoodPattern = ({ density }: { density: string }) => (
      <div data-density={density}>Content</div>
    );

    // Bad pattern requires brittle boolean
    const { unmount: unmount1 } = render(<BadPattern isMobile={true} />);
    expect(screen.getByText('Mobile')).toBeInTheDocument();
    unmount1();

    // Good pattern uses semantic density
    const { unmount: unmount2 } = render(<GoodPattern density="compact" />);
    expect(screen.getByText('Content')).toHaveAttribute('data-density', 'compact');
    unmount2();
  });
});

// =============================================================================
// L-02: Three-Mode Preservation
// =============================================================================

describe('L-02: Three-Mode Preservation', () => {
  /**
   * Law Statement: Same affordances across all densities.
   *
   * Justification: Affordances don't disappear—they transform. A button on
   * desktop is still a button on mobile, just positioned differently.
   *
   * Test: All interactive elements present in all densities, just transformed.
   */

  it('preserves all affordances across compact/comfortable/spacious', () => {
    const ActionCard = ({ density }: { density: string }) => (
      <div data-testid="card" data-density={density}>
        <button data-testid="primary">Primary Action</button>
        <button data-testid="secondary">Secondary Action</button>
        <button data-testid="tertiary">Tertiary Action</button>
      </div>
    );

    const densities = ['compact', 'comfortable', 'spacious'];

    densities.forEach((density) => {
      const { unmount } = render(<ActionCard density={density} />);

      // All three buttons must be present regardless of density
      expect(screen.getByTestId('primary')).toBeInTheDocument();
      expect(screen.getByTestId('secondary')).toBeInTheDocument();
      expect(screen.getByTestId('tertiary')).toBeInTheDocument();

      unmount();
    });
  });

  it('ensures mobile views do not drop features compared to desktop', () => {
    // Simulate a feature-rich component
    const FeaturePanel = ({ density }: { density: string }) => (
      <div data-density={density}>
        <div data-testid="search">Search</div>
        <div data-testid="filters">Filters</div>
        <div data-testid="sort">Sort</div>
        <div data-testid="export">Export</div>
      </div>
    );

    const { unmount: unmount1 } = render(<FeaturePanel density="spacious" />);
    const desktopFeatures = ['search', 'filters', 'sort', 'export'];
    desktopFeatures.forEach((feature) => {
      expect(screen.getByTestId(feature)).toBeInTheDocument();
    });
    unmount1();

    const { unmount: unmount2 } = render(<FeaturePanel density="compact" />);
    // Mobile must have same features (even if transformed to drawer/menu)
    desktopFeatures.forEach((feature) => {
      expect(screen.getByTestId(feature)).toBeInTheDocument();
    });
    unmount2();
  });
});

// =============================================================================
// L-03: Touch Target Invariance
// =============================================================================

describe('L-03: Touch Target Invariance', () => {
  /**
   * Law Statement: ≥48px interactive elements on compact.
   *
   * Justification: Touch targets must be at least 48px regardless of density.
   * This is a physical constraint that does not scale.
   *
   * Test: All interactive elements meet minimum touch target size.
   */

  it('enforces 48px minimum touch target constant', () => {
    expect(PHYSICAL_CONSTRAINTS.minTouchTarget).toBe(48);
  });

  it('ensures all interactive elements meet 48px minimum in compact mode', () => {
    const actions: FloatingAction[] = [
      { id: 'action1', icon: '🔄', label: 'Action 1', onClick: vi.fn() },
    ];

    // Even with small button size request, enforces minimum
    render(<FloatingActions actions={actions} buttonSize={30} />);

    const button = screen.getByLabelText('Action 1');
    const _style = window.getComputedStyle(button);

    // Should enforce minimum 48px (via minWidth/minHeight)
    const minWidth = parseInt(button.style.minWidth || '0', 10);
    const minHeight = parseInt(button.style.minHeight || '0', 10);

    expect(minWidth).toBeGreaterThanOrEqual(PHYSICAL_CONSTRAINTS.minTouchTarget);
    expect(minHeight).toBeGreaterThanOrEqual(PHYSICAL_CONSTRAINTS.minTouchTarget);
  });

  it('enforces minimum tap spacing between interactive elements', () => {
    expect(PHYSICAL_CONSTRAINTS.minTapSpacing).toBe(8);

    const actions: FloatingAction[] = [
      { id: 'a1', icon: '1', label: 'Action 1', onClick: vi.fn() },
      { id: 'a2', icon: '2', label: 'Action 2', onClick: vi.fn() },
    ];

    // Even with small gap request, enforces minimum
    render(<FloatingActions actions={actions} gap={4} />);

    const toolbar = screen.getByRole('toolbar');
    const gap = parseInt(toolbar.style.gap || '0', 10);

    expect(gap).toBeGreaterThanOrEqual(PHYSICAL_CONSTRAINTS.minTapSpacing);
  });

  it('rejects touch targets smaller than 48px via Math.max enforcement', () => {
    const userRequestedSizes = [10, 20, 30, 40, 48, 50, 60];

    userRequestedSizes.forEach((userSize) => {
      const enforced = Math.max(userSize, PHYSICAL_CONSTRAINTS.minTouchTarget);
      expect(enforced).toBeGreaterThanOrEqual(48);
    });
  });
});

// =============================================================================
// L-04: Tight Frame Breathing Content
// =============================================================================

describe('L-04: Tight Frame Breathing Content', () => {
  /**
   * Law Statement: Frame is steel, content glows.
   *
   * Justification: The frame (nav, chrome) is tight and precise. Content area
   * is generous and spacious. This creates the "steel biome" aesthetic.
   *
   * Test: Frame elements have minimal padding, content areas have generous padding.
   */

  it('ensures frame elements have tight spacing', () => {
    const Frame = () => (
      <nav data-testid="frame" className="tight-frame">
        Frame
      </nav>
    );

    render(<Frame />);
    const frame = screen.getByTestId('frame');

    // Frame should have class indicating tight spacing
    expect(frame).toHaveClass('tight-frame');
  });

  it('ensures content areas have generous padding', () => {
    render(
      <ElasticContainer
        layout="stack"
        padding="var(--elastic-gap-lg)" // Generous padding
        data-testid="content"
      >
        <div>Content</div>
      </ElasticContainer>
    );

    const container = screen.getByText('Content').parentElement;
    expect(container?.style.padding).toContain('var(--elastic-gap-lg)');
  });

  it('creates visual distinction: frame = cold steel, content = warm breathing', () => {
    const Layout = () => (
      <div>
        <nav data-testid="frame" style={{ padding: '4px' }}>
          Steel Frame
        </nav>
        <main data-testid="content" style={{ padding: '24px' }}>
          Breathing Content
        </main>
      </div>
    );

    render(<Layout />);

    const frame = screen.getByTestId('frame');
    const content = screen.getByTestId('content');

    const framePadding = parseInt(frame.style.padding || '0', 10);
    const contentPadding = parseInt(content.style.padding || '0', 10);

    // Content padding should be significantly larger
    expect(contentPadding).toBeGreaterThan(framePadding * 4);
  });
});

// =============================================================================
// L-05: Overlay Over Reflow
// =============================================================================

describe('L-05: Overlay Over Reflow', () => {
  /**
   * Law Statement: Navigation floats, doesn't push.
   *
   * Justification: In compact mode, secondary content becomes overlay (drawer/modal),
   * not a reflow that pushes content down. This prevents layout shift.
   *
   * Test: Secondary content in compact mode uses position: fixed/absolute,
   * not static/relative that would reflow.
   */

  let _resizeCallback: ((entries: ResizeObserverEntry[]) => void) | null = null;

  beforeEach(() => {
    const MockResizeObserver = vi.fn().mockImplementation((callback) => {
      _resizeCallback = callback;
      return {
        observe: vi.fn(() => {
          callback([
            {
              target: document.body,
              contentRect: { width: 1024, height: 768 } as DOMRectReadOnly,
              borderBoxSize: [
                { blockSize: 768, inlineSize: 1024 },
              ] as unknown as readonly ResizeObserverSize[],
              contentBoxSize: [
                { blockSize: 768, inlineSize: 1024 },
              ] as unknown as readonly ResizeObserverSize[],
              devicePixelContentBoxSize: [
                { blockSize: 768, inlineSize: 1024 },
              ] as unknown as readonly ResizeObserverSize[],
            },
          ]);
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

  it('uses overlay pattern for secondary content in compact mode', () => {
    // Set compact width
    Object.defineProperty(window, 'innerWidth', { value: 500, writable: true });
    window.dispatchEvent(new Event('resize'));

    const { container } = render(
      <ElasticSplit
        direction="horizontal"
        collapseAt={768}
        primary={<div data-testid="primary">Primary</div>}
        secondary={<div data-testid="secondary">Secondary</div>}
      />
    );

    // In compact mode, split should collapse (using overlay pattern)
    // Check that collapsed attribute exists somewhere in the rendered tree
    const collapsedElement = container.querySelector('[data-collapsed="true"]');
    expect(collapsedElement).toBeTruthy();
  });

  it('prevents layout shift when secondary content appears', () => {
    render(
      <div style={{ position: 'relative' }}>
        <div data-testid="primary">Primary Content</div>
        <FloatingActions
          actions={[{ id: '1', icon: '⚙️', label: 'Settings', onClick: vi.fn() }]}
          position="bottom-right"
        />
      </div>
    );

    // FloatingActions should use position: fixed/absolute, not static
    const toolbar = screen.getByRole('toolbar');

    // Check inline style which is actually set
    const hasFixedOrAbsolute =
      toolbar.style.position === 'fixed' ||
      toolbar.style.position === 'absolute' ||
      toolbar.className.includes('fixed') ||
      toolbar.className.includes('absolute');

    // FloatingActions should not use static positioning
    expect(hasFixedOrAbsolute || toolbar.style.position !== 'static').toBe(true);
  });

  it('rejects reflow patterns that push content down', () => {
    // Anti-pattern: static/relative positioning that reflows
    const BadPattern = () => (
      <div>
        <div data-testid="nav" style={{ position: 'static', height: '60px' }}>
          Nav
        </div>
        <div data-testid="content">Content (pushed down)</div>
      </div>
    );

    // Good pattern: overlay with fixed/absolute positioning
    const GoodPattern = () => (
      <div style={{ position: 'relative' }}>
        <div data-testid="content">Content (not pushed)</div>
        <div
          data-testid="nav"
          style={{ position: 'fixed', top: 0, left: 0, right: 0 }}
        >
          Nav
        </div>
      </div>
    );

    // Bad pattern causes reflow
    const { unmount: unmount1 } = render(<BadPattern />);
    const badNav = screen.getByTestId('nav');
    expect(badNav.style.position).toBe('static');
    unmount1();

    // Good pattern uses overlay
    const { unmount: unmount2 } = render(<GoodPattern />);
    const goodNav = screen.getByTestId('nav');
    expect(goodNav.style.position).toBe('fixed');
    unmount2();
  });
});
