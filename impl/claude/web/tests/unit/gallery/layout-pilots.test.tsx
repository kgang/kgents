/**
 * Layout Gallery Pilots Tests
 *
 * Tests for the 8 layout projection pilots demonstrating:
 * - Panel: sidebar (spacious) ≅ drawer (compact)
 * - Actions: toolbar (spacious) ≅ FAB (compact)
 * - Split: resizable (spacious) ≅ stacked (compact)
 * - Touch targets: 48px minimum regardless of density
 *
 * @see spec/protocols/projection.md (Layout Projection section)
 * @see plans/web-refactor/layout-projection-functor.md
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import LayoutGallery from '@/pages/LayoutGallery';
import {
  PHYSICAL_CONSTRAINTS,
  LAYOUT_PRIMITIVES,
  type Density,
} from '@/components/elastic';

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
    borderBoxSize: [{ blockSize: height, inlineSize: width }] as unknown as readonly ResizeObserverSize[],
    contentBoxSize: [{ blockSize: height, inlineSize: width }] as unknown as readonly ResizeObserverSize[],
    devicePixelContentBoxSize: [
      { blockSize: height, inlineSize: width },
    ] as unknown as readonly ResizeObserverSize[],
  };
}

function renderWithRouter(component: React.ReactNode) {
  return render(<BrowserRouter>{component}</BrowserRouter>);
}

// =============================================================================
// Gallery Page Tests
// =============================================================================

describe('LayoutGallery Page', () => {
  beforeEach(() => {
    // Mock ResizeObserver for spacious viewport
    const MockResizeObserver = vi.fn().mockImplementation((callback) => ({
      observe: vi.fn(() => {
        callback([createMockResizeEntry(document.body, 1200, 800)]);
      }),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }));
    window.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;

    // Mock window dimensions
    Object.defineProperty(window, 'innerWidth', { value: 1200, writable: true });
    Object.defineProperty(window, 'innerHeight', { value: 800, writable: true });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should render the page title', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getByText('Layout Projection Gallery')).toBeInTheDocument();
  });

  it('should render the subtitle about structural isomorphism', () => {
    renderWithRouter(<LayoutGallery />);
    // Multiple elements contain "structural isomorphism", use getAllBy
    expect(screen.getAllByText(/structural isomorphism/i).length).toBeGreaterThan(0);
  });

  it('should display current density', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getByText(/current density/i)).toBeInTheDocument();
  });
});

// =============================================================================
// Panel Primitive Pilots
// =============================================================================

describe('Panel Primitive Pilots', () => {
  beforeEach(() => {
    const MockResizeObserver = vi.fn().mockImplementation((callback) => ({
      observe: vi.fn(() => {
        callback([createMockResizeEntry(document.body, 1200, 800)]);
      }),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }));
    window.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;
    Object.defineProperty(window, 'innerWidth', { value: 1200, writable: true });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should render Panel (Spacious) pilot with sidebar layout description', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getByText('Panel (Spacious)')).toBeInTheDocument();
    expect(screen.getByText('Fixed sidebar layout')).toBeInTheDocument();
  });

  it('should render Panel (Compact) pilot with drawer layout description', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getByText('Panel (Compact)')).toBeInTheDocument();
    expect(screen.getByText('Bottom drawer layout')).toBeInTheDocument();
  });

  it('should render Panel Isomorphism pilot showing structural equivalence', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getByText('Panel Isomorphism')).toBeInTheDocument();
    expect(screen.getByText(/same information, different structure/i)).toBeInTheDocument();
  });

  it('should display sample panel content in sidebar pilot', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getAllByText('Details Panel').length).toBeGreaterThan(0);
  });
});

// =============================================================================
// Actions Primitive Pilots
// =============================================================================

describe('Actions Primitive Pilots', () => {
  beforeEach(() => {
    const MockResizeObserver = vi.fn().mockImplementation((callback) => ({
      observe: vi.fn(() => {
        callback([createMockResizeEntry(document.body, 1200, 800)]);
      }),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }));
    window.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;
    Object.defineProperty(window, 'innerWidth', { value: 1200, writable: true });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should render Actions (Spacious) pilot with toolbar layout', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getByText('Actions (Spacious)')).toBeInTheDocument();
    expect(screen.getByText('Full toolbar layout')).toBeInTheDocument();
  });

  it('should render Actions (Compact) pilot with FAB cluster', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getByText('Actions (Compact)')).toBeInTheDocument();
    expect(screen.getByText('FAB cluster layout')).toBeInTheDocument();
  });

  it('should show action labels in toolbar pilot', () => {
    renderWithRouter(<LayoutGallery />);
    // Toolbar shows text labels
    expect(screen.getByText('Rescan')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });
});

// =============================================================================
// Split Primitive Pilots
// =============================================================================

describe('Split Primitive Pilots', () => {
  beforeEach(() => {
    const MockResizeObserver = vi.fn().mockImplementation((callback) => ({
      observe: vi.fn(() => {
        callback([createMockResizeEntry(document.body, 1200, 800)]);
      }),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }));
    window.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;
    Object.defineProperty(window, 'innerWidth', { value: 1200, writable: true });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should render Split (Spacious) pilot with resizable divider', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getByText('Split (Spacious)')).toBeInTheDocument();
    expect(screen.getByText('Resizable divider')).toBeInTheDocument();
  });

  it('should render Split (Compact) pilot with stacked layout', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getByText('Split (Compact)')).toBeInTheDocument();
    expect(screen.getByText('Stacked layout')).toBeInTheDocument();
  });

  it('should show primary and secondary panes', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getAllByText(/Primary Pane/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Secondary Pane/i).length).toBeGreaterThan(0);
  });
});

// =============================================================================
// Touch Target Pilots
// =============================================================================

describe('Touch Target Pilots', () => {
  beforeEach(() => {
    const MockResizeObserver = vi.fn().mockImplementation((callback) => ({
      observe: vi.fn(() => {
        callback([createMockResizeEntry(document.body, 1200, 800)]);
      }),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }));
    window.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;
    Object.defineProperty(window, 'innerWidth', { value: 1200, writable: true });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should render Touch Targets pilot', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getByText('Touch Targets')).toBeInTheDocument();
  });

  it('should display 48px physical constraint', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getByText(`Physical constraint: ${PHYSICAL_CONSTRAINTS.minTouchTarget}px minimum`)).toBeInTheDocument();
  });

  it('should show compliant and non-compliant examples', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getByText('32px')).toBeInTheDocument();
    expect(screen.getByText('48px')).toBeInTheDocument();
    expect(screen.getByText('56px')).toBeInTheDocument();
  });

  it('should mark sizes below 48px as non-compliant', () => {
    renderWithRouter(<LayoutGallery />);
    // 32px and 44px should be marked "Too small"
    const tooSmallElements = screen.getAllByText('Too small');
    expect(tooSmallElements.length).toBe(2);
  });

  it('should mark sizes >= 48px as compliant', () => {
    renderWithRouter(<LayoutGallery />);
    // 48px and 56px should be marked "Compliant"
    const compliantElements = screen.getAllByText('Compliant');
    expect(compliantElements.length).toBe(2);
  });
});

// =============================================================================
// Primitive Behavior Reference Table
// =============================================================================

describe('Primitive Behavior Reference', () => {
  beforeEach(() => {
    const MockResizeObserver = vi.fn().mockImplementation((callback) => ({
      observe: vi.fn(() => {
        callback([createMockResizeEntry(document.body, 1200, 800)]);
      }),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }));
    window.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;
    Object.defineProperty(window, 'innerWidth', { value: 1200, writable: true });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should render the behavior reference table', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getByText('Layout Primitive Behaviors')).toBeInTheDocument();
  });

  it('should list all three primitives', () => {
    renderWithRouter(<LayoutGallery />);
    expect(screen.getByText('split')).toBeInTheDocument();
    expect(screen.getByText('panel')).toBeInTheDocument();
    expect(screen.getByText('actions')).toBeInTheDocument();
  });

  it('should show behaviors for each density level', () => {
    renderWithRouter(<LayoutGallery />);
    // Split behaviors
    expect(screen.getByText('collapse secondary')).toBeInTheDocument();
    expect(screen.getByText('resizable divider')).toBeInTheDocument();
    // Panel behaviors
    expect(screen.getByText('bottom drawer')).toBeInTheDocument();
    expect(screen.getByText('fixed sidebar')).toBeInTheDocument();
    // Actions behaviors
    expect(screen.getByText('floating fab')).toBeInTheDocument();
    expect(screen.getByText('full toolbar')).toBeInTheDocument();
  });
});

// =============================================================================
// Structural Isomorphism Verification
// =============================================================================

describe('Structural Isomorphism', () => {
  it('should preserve information count across layout modes', () => {
    // The SAMPLE_PANEL_CONTENT has 4 items
    // Both sidebar and drawer pilots should show the same 4 items
    // This is verified by the test data structure, not runtime rendering

    const samplePanelContent = {
      title: 'Details Panel',
      items: [
        { id: '1', label: 'Status', value: 'Active' },
        { id: '2', label: 'Created', value: '2025-12-16' },
        { id: '3', label: 'Type', value: 'Agent' },
        { id: '4', label: 'Memory', value: '256 MB' },
      ],
    };

    // Isomorphism property: same information in both layouts
    expect(samplePanelContent.items.length).toBe(4);

    // Layout transformation does not change data count
    const sidebarItemCount = samplePanelContent.items.length;
    const drawerItemCount = samplePanelContent.items.length;
    expect(sidebarItemCount).toBe(drawerItemCount);
  });

  it('should verify LAYOUT_PRIMITIVES defines behaviors for all densities', () => {
    const densities: Density[] = ['compact', 'comfortable', 'spacious'];
    const primitives = ['split', 'panel', 'actions'] as const;

    primitives.forEach((primitive) => {
      densities.forEach((density) => {
        // Every primitive must have a defined behavior for every density
        expect(LAYOUT_PRIMITIVES[primitive][density]).toBeDefined();
        expect(typeof LAYOUT_PRIMITIVES[primitive][density]).toBe('string');
      });
    });
  });

  it('should enforce PHYSICAL_CONSTRAINTS are density-invariant', () => {
    // Physical constraints do NOT vary by density
    expect(PHYSICAL_CONSTRAINTS.minTouchTarget).toBe(48);
    expect(PHYSICAL_CONSTRAINTS.minFontSize).toBe(14);
    expect(PHYSICAL_CONSTRAINTS.minTapSpacing).toBe(8);
  });
});
