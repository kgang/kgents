/**
 * SpectatorOverlay Tests
 *
 * Tests for the SpectatorOverlay component.
 *
 * @see plans/crown-jewels-genesis-phase2.md - Week 3: SpectatorOverlay
 */

import { render, screen } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import {
  SpectatorOverlay,
  eigenvectorToColor,
  getColorForId,
  type SpectatorCursor,
} from '@/components/atelier/SpectatorOverlay';
import { LIVING_EARTH } from '@/constants/colors';

// =============================================================================
// Test Fixtures
// =============================================================================

const mockCursors: SpectatorCursor[] = [
  {
    id: 'spectator-1',
    position: { x: 0.5, y: 0.5 },
    lastUpdate: Date.now(),
    name: 'Alice',
  },
  {
    id: 'spectator-2',
    position: { x: 0.3, y: 0.7 },
    citizenId: 'citizen-1',
    eigenvector: [0.5, -0.3, 0.2],
    lastUpdate: Date.now(),
    name: 'Bob',
  },
];

// =============================================================================
// SpectatorOverlay Component Tests
// =============================================================================

describe('SpectatorOverlay - Rendering', () => {
  it('renders nothing when showCursors is false', () => {
    const { container } = render(
      <SpectatorOverlay spectators={mockCursors} showCursors={false} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders nothing when spectators is empty', () => {
    const { container } = render(
      <SpectatorOverlay spectators={[]} showCursors={true} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders cursor dots for each spectator', () => {
    const { container } = render(
      <SpectatorOverlay spectators={mockCursors} showCursors={true} />
    );
    // Each cursor should have a dot
    const dots = container.querySelectorAll('.rounded-full');
    expect(dots.length).toBeGreaterThanOrEqual(mockCursors.length);
  });

  it('positions cursors based on normalized coordinates', () => {
    const { container } = render(
      <SpectatorOverlay spectators={mockCursors} showCursors={true} />
    );
    // Look for positioned elements
    const positioned = container.querySelectorAll('[style*="left"]');
    expect(positioned.length).toBeGreaterThan(0);
  });

  it('shows names when showNames is true', () => {
    render(
      <SpectatorOverlay spectators={mockCursors} showCursors={true} showNames={true} />
    );
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Bob')).toBeInTheDocument();
  });

  it('hides names when showNames is false', () => {
    render(
      <SpectatorOverlay spectators={mockCursors} showCursors={true} showNames={false} />
    );
    expect(screen.queryByText('Alice')).not.toBeInTheDocument();
    expect(screen.queryByText('Bob')).not.toBeInTheDocument();
  });

  it('has pointer-events-none to not interfere with canvas clicks', () => {
    const { container } = render(
      <SpectatorOverlay spectators={mockCursors} showCursors={true} />
    );
    expect(container.firstChild).toHaveClass('pointer-events-none');
  });
});

describe('SpectatorOverlay - Cursor Age', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('filters out stale cursors based on maxAge', () => {
    const staleCursor: SpectatorCursor = {
      id: 'stale',
      position: { x: 0.1, y: 0.1 },
      lastUpdate: Date.now() - 10000, // 10 seconds ago
    };

    const freshCursor: SpectatorCursor = {
      id: 'fresh',
      position: { x: 0.9, y: 0.9 },
      lastUpdate: Date.now(),
    };

    const { container } = render(
      <SpectatorOverlay
        spectators={[staleCursor, freshCursor]}
        showCursors={true}
        maxAge={5000} // 5 second max age
      />
    );

    // Should only show fresh cursor (stale one is filtered out)
    const dots = container.querySelectorAll('.rounded-full');
    expect(dots.length).toBe(1);
  });

  it('fades cursors as they age', () => {
    const halfAgeCursor: SpectatorCursor = {
      id: 'fading',
      position: { x: 0.5, y: 0.5 },
      lastUpdate: Date.now() - 3000, // 3 seconds ago
    };

    const { container } = render(
      <SpectatorOverlay
        spectators={[halfAgeCursor]}
        showCursors={true}
        maxAge={5000}
      />
    );

    // Cursor should exist but have reduced opacity
    const positioned = container.querySelector('[style*="opacity"]');
    expect(positioned).toBeInTheDocument();
  });
});

// =============================================================================
// Helper Function Tests
// =============================================================================

describe('eigenvectorToColor', () => {
  it('returns amber fallback for undefined eigenvector', () => {
    const color = eigenvectorToColor(undefined);
    expect(color).toBe(LIVING_EARTH.amber);
  });

  it('returns amber fallback for short eigenvector', () => {
    const color = eigenvectorToColor([0.5, 0.3]); // Only 2 components
    expect(color).toBe(LIVING_EARTH.amber);
  });

  it('returns HSL color for valid eigenvector', () => {
    const color = eigenvectorToColor([0.5, -0.3, 0.2]);
    expect(color).toMatch(/^hsl\(\d+,\s*\d+%,\s*\d+%\)$/);
  });

  it('produces different colors for different eigenvectors', () => {
    const color1 = eigenvectorToColor([1, 1, 1]);
    const color2 = eigenvectorToColor([-1, -1, -1]);
    expect(color1).not.toBe(color2);
  });
});

describe('getColorForId', () => {
  it('returns consistent color for same ID', () => {
    const colorA = getColorForId('test-id-123');
    const colorB = getColorForId('test-id-123');
    expect(colorA).toBe(colorB);
  });

  it('returns different colors for different IDs', () => {
    // May occasionally collide due to hash, but usually different
    // This is a probabilistic test - run multiple times
    const colors = new Set([
      getColorForId('a'),
      getColorForId('b'),
      getColorForId('c'),
      getColorForId('d'),
    ]);
    expect(colors.size).toBeGreaterThan(1);
  });

  it('returns a valid color from LIVING_EARTH palette', () => {
    const color = getColorForId('any-id');
    expect(Object.values(LIVING_EARTH)).toContain(color);
  });
});

// =============================================================================
// Accessibility Tests
// =============================================================================

describe('SpectatorOverlay - Accessibility', () => {
  it('has role="presentation" for decorative overlay', () => {
    const { container } = render(
      <SpectatorOverlay spectators={mockCursors} showCursors={true} />
    );
    expect(container.firstChild).toHaveAttribute('role', 'presentation');
  });

  it('has aria-label with spectator count', () => {
    const { container } = render(
      <SpectatorOverlay spectators={mockCursors} showCursors={true} />
    );
    expect(container.firstChild).toHaveAttribute('aria-label');
    const element = container.firstChild as HTMLElement;
    const label = element?.getAttribute('aria-label') || '';
    expect(label).toContain('2'); // 2 spectators
  });

  it('marks cursor dots as aria-hidden', () => {
    const { container } = render(
      <SpectatorOverlay spectators={mockCursors} showCursors={true} />
    );
    const dots = container.querySelectorAll('[aria-hidden="true"]');
    expect(dots.length).toBeGreaterThan(0);
  });
});
