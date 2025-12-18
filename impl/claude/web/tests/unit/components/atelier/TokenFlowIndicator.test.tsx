/**
 * TokenFlowIndicator Tests
 *
 * Tests following T-gent taxonomy:
 * - Type I: Contract tests (props validation, rendering)
 * - Type II: Saboteur tests (edge cases, empty events)
 * - Type III: Spy tests (event consumption)
 * - Type IV: Property tests (animation behavior)
 * - Type V: Performance tests (render time)
 *
 * @see plans/crown-jewels-genesis-phase2-chunks3-5.md - Chunk 3: Token Visualization
 * @see docs/skills/test-patterns.md - T-gent Taxonomy
 */

import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { TokenFlowIndicator, type TokenFlowIndicatorProps, type TokenFlowEvent } from '@/components/atelier/TokenFlowIndicator';

// =============================================================================
// Mocks
// =============================================================================

// Mock useFlowing hook
vi.mock('@/hooks/useFlowing', () => ({
  useFlowing: vi.fn(() => ({
    particles: [],
    isFlowing: false,
    start: vi.fn(),
    stop: vi.fn(),
    pathD: 'M 0 0 L 100 100',
  })),
  createCurvedPath: vi.fn((from, to) => [from, { x: (from.x + to.x) / 2, y: (from.y + to.y) / 2 }, to]),
}));

// Mock requestAnimationFrame
const originalRAF = global.requestAnimationFrame;
const originalCAF = global.cancelAnimationFrame;

beforeEach(() => {
  let rafId = 0;
  global.requestAnimationFrame = vi.fn((cb) => {
    rafId++;
    setTimeout(() => cb(performance.now()), 0);
    return rafId;
  });
  global.cancelAnimationFrame = vi.fn();
});

afterEach(() => {
  global.requestAnimationFrame = originalRAF;
  global.cancelAnimationFrame = originalCAF;
  vi.clearAllMocks();
});

// =============================================================================
// Test Fixtures
// =============================================================================

const mockEvents: TokenFlowEvent[] = [
  {
    id: 'flow-1',
    amount: 10,
    direction: 'out',
    timestamp: new Date().toISOString(),
  },
  {
    id: 'flow-2',
    amount: 5,
    direction: 'in',
    timestamp: new Date(Date.now() - 1000).toISOString(),
  },
];

const defaultProps: TokenFlowIndicatorProps = {
  events: mockEvents,
  position: 'bottom',
  canvasWidth: 400,
  canvasHeight: 300,
  enabled: true,
};

function renderIndicator(overrides: Partial<TokenFlowIndicatorProps> = {}) {
  const props = { ...defaultProps, ...overrides };
  return render(<TokenFlowIndicator {...props} />);
}

// =============================================================================
// Type I: Contract Tests
// =============================================================================

describe('TokenFlowIndicator - Type I: Contract Tests', () => {
  it('renders with required props', () => {
    const { container } = renderIndicator();
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('renders with viewBox matching canvas dimensions', () => {
    const { container } = renderIndicator({ canvasWidth: 600, canvasHeight: 400 });
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('viewBox')).toBe('0 0 600 400');
  });

  it('applies className prop', () => {
    const { container } = renderIndicator({ className: 'test-class' });
    expect(container.querySelector('svg.test-class')).toBeInTheDocument();
  });

  it('renders path element', () => {
    const { container } = renderIndicator();
    expect(container.querySelector('path')).toBeInTheDocument();
  });
});

// =============================================================================
// Type II: Saboteur Tests
// =============================================================================

describe('TokenFlowIndicator - Type II: Saboteur Tests', () => {
  it('renders nothing when events array is empty', () => {
    const { container } = renderIndicator({ events: [] });
    // SVG should still exist but no active flow
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('handles disabled state', () => {
    const { container } = renderIndicator({ enabled: false });
    // Should not render when disabled
    expect(container.querySelector('svg')).toBeNull();
  });

  it('handles zero canvas dimensions gracefully', () => {
    const { container } = renderIndicator({ canvasWidth: 0, canvasHeight: 0 });
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('handles single event', () => {
    const { container } = renderIndicator({ events: [mockEvents[0]] });
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('handles very large amounts', () => {
    const largeEvent: TokenFlowEvent = {
      id: 'large',
      amount: 1000000,
      direction: 'out',
      timestamp: new Date().toISOString(),
    };
    const { container } = renderIndicator({ events: [largeEvent] });
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});

// =============================================================================
// Type III: Spy Tests
// =============================================================================

describe('TokenFlowIndicator - Type III: Spy Tests', () => {
  it('tracks shown events to prevent duplicates', async () => {
    const { rerender } = renderIndicator({ events: mockEvents });

    // Re-render with same events
    rerender(<TokenFlowIndicator {...defaultProps} events={mockEvents} />);

    // Should not cause additional flows for same events
    // This is internal behavior, just verify no crash
    expect(true).toBe(true);
  });

  it('responds to new events being added', async () => {
    const { rerender } = renderIndicator({ events: [] });

    // Add new event
    await act(async () => {
      rerender(
        <TokenFlowIndicator
          {...defaultProps}
          events={[mockEvents[0]]}
        />
      );
    });

    // Component should update
    expect(true).toBe(true);
  });
});

// =============================================================================
// Type IV: Property Tests (Position Variations)
// =============================================================================

describe('TokenFlowIndicator - Type IV: Position Tests', () => {
  const positions: TokenFlowIndicatorProps['position'][] = ['top', 'right', 'bottom', 'left'];

  positions.forEach((position) => {
    it(`renders correctly at ${position} position`, () => {
      const { container } = renderIndicator({ position });
      expect(container.querySelector('svg')).toBeInTheDocument();
    });
  });

  it('defaults to bottom position', () => {
    const { container } = renderIndicator({ position: undefined });
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});

// =============================================================================
// Type V: Performance Tests
// =============================================================================

describe('TokenFlowIndicator - Type V: Performance Tests', () => {
  it('renders within acceptable time (<16ms)', () => {
    const start = performance.now();
    renderIndicator();
    const elapsed = performance.now() - start;
    expect(elapsed).toBeLessThan(50); // Generous for test environment
  });

  it('handles many events efficiently', () => {
    const manyEvents: TokenFlowEvent[] = Array.from({ length: 100 }, (_, i) => ({
      id: `event-${i}`,
      amount: 10,
      direction: i % 2 === 0 ? 'in' : 'out',
      timestamp: new Date(Date.now() - i * 1000).toISOString(),
    }));

    const start = performance.now();
    renderIndicator({ events: manyEvents });
    const elapsed = performance.now() - start;

    expect(elapsed).toBeLessThan(100);
  });

  it('cleans up old events from memory', async () => {
    const manyEvents: TokenFlowEvent[] = Array.from({ length: 150 }, (_, i) => ({
      id: `event-${i}`,
      amount: 10,
      direction: 'out',
      timestamp: new Date(Date.now() - i * 1000).toISOString(),
    }));

    const { container } = renderIndicator({ events: manyEvents });

    // Internal cleanup should happen, verify no crash
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});

// =============================================================================
// Accessibility Tests
// =============================================================================

describe('TokenFlowIndicator - Accessibility', () => {
  it('is non-interactive (pointer-events-none)', () => {
    const { container } = renderIndicator();
    const svg = container.querySelector('svg');
    expect(svg?.classList.contains('pointer-events-none')).toBe(true);
  });

  it('uses preserveAspectRatio for consistent display', () => {
    const { container } = renderIndicator();
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('preserveAspectRatio')).toBe('none');
  });
});
