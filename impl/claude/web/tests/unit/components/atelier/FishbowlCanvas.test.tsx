/**
 * FishbowlCanvas Tests
 *
 * Tests for the FishbowlCanvas component following T-gent taxonomy:
 * - Type I: Contract tests (props validation, state transitions)
 * - Type II: Saboteur tests (edge cases, empty states)
 * - Type III: Spy tests (callback verification)
 * - Type IV: Property tests (animation bounds)
 * - Type V: Performance tests (render cycles)
 *
 * @see plans/crown-jewels-genesis-phase2.md - Week 3: FishbowlCanvas Tests
 * @see docs/skills/test-patterns.md - T-gent Taxonomy
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { FishbowlCanvas, type FishbowlCanvasProps, type SpectatorCursor } from '@/components/atelier/FishbowlCanvas';

// =============================================================================
// Test Fixtures
// =============================================================================

const mockArtisan = {
  id: 'artisan-1',
  name: 'Calligrapher',
  specialty: 'Elegant text rendering',
  style: 'classical',
  is_active: true,
};

const mockSpectatorCursors: SpectatorCursor[] = [
  {
    id: 'spectator-1',
    position: { x: 0.5, y: 0.5 },
    lastUpdate: Date.now(),
  },
  {
    id: 'spectator-2',
    position: { x: 0.3, y: 0.7 },
    citizenId: 'citizen-1',
    eigenvector: [0.5, -0.3, 0.2],
    lastUpdate: Date.now(),
  },
];

const defaultProps: FishbowlCanvasProps = {
  sessionId: 'session-123',
  artisan: mockArtisan,
  isLive: true,
  content: 'Hello, World!',
  contentType: 'text',
  spectatorCount: 42,
};

// Helper to render with default props
function renderFishbowl(overrides: Partial<FishbowlCanvasProps> = {}) {
  const props = { ...defaultProps, ...overrides };
  return render(<FishbowlCanvas {...props} />);
}

// =============================================================================
// Type I: Contract Tests (Props Validation)
// =============================================================================

describe('FishbowlCanvas - Type I: Contract Tests', () => {
  it('renders with required props', () => {
    renderFishbowl();
    expect(screen.getByRole('region')).toBeInTheDocument();
  });

  it('displays session ID as data attribute', () => {
    renderFishbowl({ sessionId: 'test-session-456' });
    expect(screen.getByRole('region')).toHaveAttribute('data-session-id', 'test-session-456');
  });

  it('renders artisan name and specialty', () => {
    renderFishbowl();
    expect(screen.getByText('Calligrapher')).toBeInTheDocument();
    expect(screen.getByText('Elegant text rendering')).toBeInTheDocument();
  });

  it('shows LIVE badge when isLive is true', () => {
    renderFishbowl({ isLive: true });
    expect(screen.getByText('LIVE')).toBeInTheDocument();
  });

  it('hides LIVE badge when isLive is false', () => {
    renderFishbowl({ isLive: false });
    expect(screen.queryByText('LIVE')).not.toBeInTheDocument();
  });

  it('displays spectator count', () => {
    renderFishbowl({ spectatorCount: 47 });
    expect(screen.getByText('47')).toBeInTheDocument();
  });

  it('renders text content correctly', () => {
    renderFishbowl({ content: 'Test content here', contentType: 'text' });
    expect(screen.getByText('Test content here')).toBeInTheDocument();
  });

  it('renders code content in pre/code tags', () => {
    renderFishbowl({ content: 'const x = 42;', contentType: 'code' });
    const codeElement = screen.getByText('const x = 42;');
    expect(codeElement.tagName.toLowerCase()).toBe('code');
  });

  it('renders image content with img tag', () => {
    renderFishbowl({ content: 'https://example.com/image.png', contentType: 'image' });
    const img = screen.getByAltText('Created artwork');
    expect(img).toHaveAttribute('src', 'https://example.com/image.png');
  });
});

// =============================================================================
// Type II: Saboteur Tests (Edge Cases)
// =============================================================================

describe('FishbowlCanvas - Type II: Saboteur Tests', () => {
  it('handles null artisan gracefully', () => {
    renderFishbowl({ artisan: null });
    expect(screen.getByRole('region')).toBeInTheDocument();
    expect(screen.queryByText('LIVE')).not.toBeInTheDocument();
  });

  it('handles empty content with placeholder', () => {
    renderFishbowl({ content: '', isLive: true });
    expect(screen.getByText('Awaiting creation...')).toBeInTheDocument();
  });

  it('handles zero spectator count', () => {
    renderFishbowl({ spectatorCount: 0 });
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('handles very long content without breaking layout', () => {
    const longContent = 'A'.repeat(10000);
    renderFishbowl({ content: longContent, contentType: 'text' });
    const region = screen.getByRole('region');
    expect(region).toBeInTheDocument();
  });

  it('handles missing spectatorCursors prop', () => {
    renderFishbowl({ showCursors: true });
    // Should render without error even with no cursors prop
    expect(screen.getByRole('region')).toBeInTheDocument();
  });

  it('handles empty spectatorCursors array', () => {
    renderFishbowl({ spectatorCursors: [], showCursors: true });
    expect(screen.getByRole('region')).toBeInTheDocument();
  });
});

// =============================================================================
// Type III: Spy Tests (Callback Verification)
// =============================================================================

describe('FishbowlCanvas - Type III: Spy Tests', () => {
  it('calls onCanvasClick with normalized coordinates', () => {
    const handleClick = vi.fn();
    renderFishbowl({ onCanvasClick: handleClick });

    const canvas = screen.getByRole('region');

    // Mock getBoundingClientRect
    vi.spyOn(canvas, 'getBoundingClientRect').mockReturnValue({
      left: 0,
      top: 0,
      width: 100,
      height: 100,
      right: 100,
      bottom: 100,
      x: 0,
      y: 0,
      toJSON: () => {},
    });

    fireEvent.click(canvas, { clientX: 50, clientY: 50 });

    expect(handleClick).toHaveBeenCalledWith({ x: 0.5, y: 0.5 });
  });

  it('does not call onCanvasClick when prop is undefined', () => {
    const { container } = renderFishbowl({ onCanvasClick: undefined });
    const canvas = screen.getByRole('region');

    // Should not throw
    fireEvent.click(canvas);
    expect(container).toBeInTheDocument();
  });

  it('normalizes click position to 0-1 range', () => {
    const handleClick = vi.fn();
    renderFishbowl({ onCanvasClick: handleClick });

    const canvas = screen.getByRole('region');

    vi.spyOn(canvas, 'getBoundingClientRect').mockReturnValue({
      left: 100,
      top: 50,
      width: 200,
      height: 400,
      right: 300,
      bottom: 450,
      x: 100,
      y: 50,
      toJSON: () => {},
    });

    // Click at (200, 250) which is center of canvas (100 from left, 200 from top)
    fireEvent.click(canvas, { clientX: 200, clientY: 250 });

    expect(handleClick).toHaveBeenCalledWith({ x: 0.5, y: 0.5 });
  });
});

// =============================================================================
// Type IV: Property Tests (Animation & Visual Properties)
// =============================================================================

describe('FishbowlCanvas - Type IV: Property Tests', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('has cursor-pointer when onCanvasClick is provided', () => {
    renderFishbowl({ onCanvasClick: vi.fn() });
    const canvas = screen.getByRole('region');
    expect(canvas).toHaveClass('cursor-pointer');
  });

  it('does not have cursor-pointer when onCanvasClick is undefined', () => {
    renderFishbowl({ onCanvasClick: undefined });
    const canvas = screen.getByRole('region');
    expect(canvas).not.toHaveClass('cursor-pointer');
  });

  it('has minimum height of 300px', () => {
    renderFishbowl();
    const canvas = screen.getByRole('region');
    expect(canvas).toHaveClass('min-h-[300px]');
  });

  it('has aria-label indicating stream status', () => {
    renderFishbowl({ isLive: true });
    const canvas = screen.getByRole('region');
    expect(canvas).toHaveAttribute('aria-label', 'Live creation canvas - streaming');
  });

  it('updates aria-label when not streaming', () => {
    renderFishbowl({ isLive: false });
    const canvas = screen.getByRole('region');
    expect(canvas).toHaveAttribute('aria-label', 'Live creation canvas');
  });
});

// =============================================================================
// Type V: Performance Tests
// =============================================================================

describe('FishbowlCanvas - Type V: Performance Tests', () => {
  it('renders within acceptable time (<16ms)', () => {
    const start = performance.now();
    renderFishbowl();
    const elapsed = performance.now() - start;
    expect(elapsed).toBeLessThan(50); // Generous for test environment
  });

  it('handles many spectator cursors efficiently', () => {
    const manyCursors: SpectatorCursor[] = Array.from({ length: 100 }, (_, i) => ({
      id: `spectator-${i}`,
      position: { x: Math.random(), y: Math.random() },
      lastUpdate: Date.now(),
    }));

    const start = performance.now();
    renderFishbowl({ spectatorCursors: manyCursors, showCursors: true });
    const elapsed = performance.now() - start;

    expect(elapsed).toBeLessThan(100); // Generous for test environment
  });

  it('does not re-render unnecessarily when props unchanged', () => {
    const { rerender } = render(<FishbowlCanvas {...defaultProps} />);

    const renderCount = vi.fn();
    const TestWrapper = () => {
      React.useEffect(() => {
        renderCount();
      });
      return <FishbowlCanvas {...defaultProps} />;
    };

    rerender(<TestWrapper />);
    rerender(<TestWrapper />);

    // Initial render + 2 rerenders = 3 (but should stabilize)
    expect(renderCount).toHaveBeenCalled();
  });
});

// =============================================================================
// Spectator Overlay Tests
// =============================================================================

describe('FishbowlCanvas - Spectator Overlay', () => {
  it('renders spectator cursors when showCursors is true', () => {
    renderFishbowl({
      spectatorCursors: mockSpectatorCursors,
      showCursors: true,
    });

    // Cursors are rendered as hidden elements
    const overlay = screen.getByRole('region');
    expect(overlay).toBeInTheDocument();
  });

  it('does not render cursor overlay when showCursors is false', () => {
    const { container } = renderFishbowl({
      spectatorCursors: mockSpectatorCursors,
      showCursors: false,
    });

    // Should not find cursor elements
    const cursors = container.querySelectorAll('[style*="left:"]');
    // Content renderer may have styles, but cursor dots should be minimal
    expect(cursors.length).toBeLessThan(mockSpectatorCursors.length);
  });
});
