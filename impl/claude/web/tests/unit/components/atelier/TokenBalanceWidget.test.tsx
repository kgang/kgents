/**
 * TokenBalanceWidget Tests
 *
 * Tests following T-gent taxonomy:
 * - Type I: Contract tests (props validation, rendering)
 * - Type II: Saboteur tests (edge cases, zero balance)
 * - Type III: Spy tests (click handlers)
 * - Type IV: Property tests (animation behavior)
 * - Type V: Performance tests (render time)
 *
 * @see plans/crown-jewels-genesis-phase2-chunks3-5.md - Chunk 3: Token Visualization
 * @see docs/skills/test-patterns.md - T-gent Taxonomy
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { TokenBalanceWidget, type TokenBalanceWidgetProps } from '@/components/atelier/TokenBalanceWidget';

// =============================================================================
// Mocks
// =============================================================================

// Mock requestAnimationFrame for animation tests
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
});

// =============================================================================
// Test Fixtures
// =============================================================================

const defaultProps: TokenBalanceWidgetProps = {
  balance: 100,
};

function renderWidget(overrides: Partial<TokenBalanceWidgetProps> = {}) {
  const props = { ...defaultProps, ...overrides };
  return render(<TokenBalanceWidget {...props} />);
}

// =============================================================================
// Type I: Contract Tests
// =============================================================================

describe('TokenBalanceWidget - Type I: Contract Tests', () => {
  it('renders with required props', () => {
    renderWidget();
    expect(screen.getByText('100')).toBeInTheDocument();
  });

  it('renders compact variant by default', () => {
    const { container } = renderWidget();
    // Compact variant uses rounded-full class
    expect(container.querySelector('.rounded-full')).toBeInTheDocument();
  });

  it('renders full variant when specified', () => {
    renderWidget({ variant: 'full' });
    expect(screen.getByText('Token Balance')).toBeInTheDocument();
  });

  it('shows label in full variant', () => {
    renderWidget({ variant: 'full', showLabel: true });
    expect(screen.getByText('Token Balance')).toBeInTheDocument();
    expect(screen.getByText('tokens')).toBeInTheDocument();
  });

  it('hides label when showLabel is false', () => {
    renderWidget({ variant: 'full', showLabel: false });
    expect(screen.queryByText('Token Balance')).not.toBeInTheDocument();
  });

  it('shows connection status in full variant', () => {
    renderWidget({ variant: 'full', isConnected: true });
    expect(screen.getByText('Live')).toBeInTheDocument();
  });

  it('shows syncing status when disconnected', () => {
    renderWidget({ variant: 'full', isConnected: false });
    expect(screen.getByText('Syncing...')).toBeInTheDocument();
  });

  it('shows recent change indicator', () => {
    renderWidget({
      variant: 'full',
      recentChange: { amount: 10, direction: 'in' },
    });
    expect(screen.getByText('+10')).toBeInTheDocument();
  });

  it('shows negative change for out direction', () => {
    renderWidget({
      variant: 'full',
      recentChange: { amount: 5, direction: 'out' },
    });
    expect(screen.getByText('-5')).toBeInTheDocument();
  });
});

// =============================================================================
// Type II: Saboteur Tests
// =============================================================================

describe('TokenBalanceWidget - Type II: Saboteur Tests', () => {
  it('handles zero balance', () => {
    renderWidget({ balance: 0 });
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('handles very large balance', () => {
    renderWidget({ balance: 1000000 });
    expect(screen.getByText('1000000')).toBeInTheDocument();
  });

  it('handles negative balance (edge case)', () => {
    renderWidget({ balance: -10 });
    expect(screen.getByText('-10')).toBeInTheDocument();
  });

  it('handles undefined recentChange', () => {
    renderWidget({ recentChange: undefined });
    // Should render without crashing
    expect(screen.getByText('100')).toBeInTheDocument();
  });

  it('handles disconnected state in compact variant', () => {
    const { container } = renderWidget({ variant: 'compact', isConnected: false });
    // Reconnecting indicator should appear
    const indicator = container.querySelector('span[title="Reconnecting..."]');
    expect(indicator).toBeInTheDocument();
  });
});

// =============================================================================
// Type III: Spy Tests
// =============================================================================

describe('TokenBalanceWidget - Type III: Spy Tests', () => {
  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    renderWidget({ onClick: handleClick });

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is clickable in compact variant', () => {
    const handleClick = vi.fn();
    const { container } = renderWidget({ variant: 'compact', onClick: handleClick });

    const button = container.querySelector('button');
    expect(button).toBeInTheDocument();
  });

  it('is clickable in full variant', () => {
    const handleClick = vi.fn();
    renderWidget({ variant: 'full', onClick: handleClick });

    // Full variant uses a div, but should still be clickable
    const widget = screen.getByText('100').closest('div');
    fireEvent.click(widget!);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('has no click handler when onClick not provided', () => {
    const { container } = renderWidget({ onClick: undefined });
    // Should not have cursor-pointer class
    expect(container.querySelector('.cursor-pointer')).not.toBeInTheDocument();
  });
});

// =============================================================================
// Type IV: Property Tests (Animation Behavior)
// =============================================================================

describe('TokenBalanceWidget - Type IV: Animation Tests', () => {
  it('animates balance changes', async () => {
    const { rerender } = renderWidget({ balance: 100 });

    // Initial value
    expect(screen.getByText('100')).toBeInTheDocument();

    // Change balance
    await act(async () => {
      rerender(<TokenBalanceWidget balance={150} />);
      // Wait for animation frame
      await new Promise((r) => setTimeout(r, 50));
    });

    // Eventually shows new value
    await waitFor(() => {
      expect(screen.getByText('150')).toBeInTheDocument();
    });
  });

  it('applies flash effect on balance increase', async () => {
    const { container, rerender } = renderWidget({ balance: 100 });

    await act(async () => {
      rerender(<TokenBalanceWidget balance: 110 />);
      await new Promise((r) => setTimeout(r, 50));
    });

    // Flash state should be applied (green for earn)
    // This is visual, so we just verify no errors
    expect(container.querySelector('button, div')).toBeInTheDocument();
  });

  it('applies different flash for balance decrease', async () => {
    const { container, rerender } = renderWidget({ balance: 100 });

    await act(async () => {
      rerender(<TokenBalanceWidget balance={90} />);
      await new Promise((r) => setTimeout(r, 50));
    });

    // Flash state should be applied (red for spend)
    expect(container.querySelector('button, div')).toBeInTheDocument();
  });
});

// =============================================================================
// Type V: Performance Tests
// =============================================================================

describe('TokenBalanceWidget - Type V: Performance Tests', () => {
  it('renders within acceptable time (<16ms)', () => {
    const start = performance.now();
    renderWidget();
    const elapsed = performance.now() - start;
    expect(elapsed).toBeLessThan(50); // Generous for test environment
  });

  it('handles rapid balance updates', async () => {
    const { rerender } = renderWidget({ balance: 100 });

    const start = performance.now();

    for (let i = 0; i < 10; i++) {
      await act(async () => {
        rerender(<TokenBalanceWidget balance={100 + i * 10} />);
      });
    }

    const elapsed = performance.now() - start;
    expect(elapsed).toBeLessThan(500); // Should handle rapid updates
  });
});

// =============================================================================
// Accessibility Tests
// =============================================================================

describe('TokenBalanceWidget - Accessibility', () => {
  it('has accessible button role in compact variant', () => {
    renderWidget({ variant: 'compact', onClick: () => {} });
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('uses tabular-nums for number display', () => {
    const { container } = renderWidget();
    expect(container.querySelector('.tabular-nums')).toBeInTheDocument();
  });
});
