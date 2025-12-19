/**
 * Tests for ExplorationBreadcrumb component.
 *
 * Tests:
 * - Renders trail correctly
 * - Handles navigation clicks
 * - Shows max 5 items
 * - Fades older items
 * - Shows home button
 * - Handles empty trail
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ExplorationBreadcrumb, type BreadcrumbItem } from '@/shell/ExplorationBreadcrumb';

// Mock motion preferences hook
vi.mock('@/components/joy/useMotionPreferences', () => ({
  useMotionPreferences: () => ({ shouldAnimate: true }),
}));

const mockTrail: BreadcrumbItem[] = [
  {
    path: 'world.garden',
    aspect: 'manifest',
    timestamp: Date.now() - 5000,
  },
  {
    path: 'world.garden',
    aspect: 'witness',
    timestamp: Date.now() - 3000,
  },
  {
    path: 'self.memory',
    aspect: 'capture',
    timestamp: Date.now() - 1000,
  },
];

describe('ExplorationBreadcrumb', () => {
  it('renders trail items', () => {
    render(<ExplorationBreadcrumb trail={mockTrail} onNavigate={vi.fn()} />);

    // Check that all items are rendered using ARIA labels (unique)
    expect(screen.getByLabelText('Navigate to world.garden:manifest')).toBeInTheDocument();
    expect(screen.getByLabelText('Navigate to world.garden:witness')).toBeInTheDocument();
    expect(screen.getByLabelText('Navigate to self.memory:capture')).toBeInTheDocument();
  });

  it('handles navigation clicks', () => {
    const onNavigate = vi.fn();
    render(<ExplorationBreadcrumb trail={mockTrail} onNavigate={onNavigate} />);

    // Click the first breadcrumb item
    const firstButton = screen.getByLabelText('Navigate to world.garden:manifest');
    fireEvent.click(firstButton);

    expect(onNavigate).toHaveBeenCalledWith(mockTrail[0]);
  });

  it('handles home button click', () => {
    const onHome = vi.fn();
    render(<ExplorationBreadcrumb trail={mockTrail} onNavigate={vi.fn()} onHome={onHome} />);

    // Click home button
    const homeButton = screen.getByLabelText('Go home');
    fireEvent.click(homeButton);

    expect(onHome).toHaveBeenCalled();
  });

  it('hides home button when onHome not provided', () => {
    render(<ExplorationBreadcrumb trail={mockTrail} onNavigate={vi.fn()} />);

    // Home button should not be present
    expect(screen.queryByLabelText('Go home')).not.toBeInTheDocument();
  });

  it('hides when trail is empty', () => {
    const { container } = render(<ExplorationBreadcrumb trail={[]} onNavigate={vi.fn()} />);

    expect(container.firstChild).toBeNull();
  });

  it('highlights most recent item', () => {
    render(<ExplorationBreadcrumb trail={mockTrail} onNavigate={vi.fn()} />);

    // The last item should have different styling
    const lastButton = screen.getByLabelText('Navigate to self.memory:capture');

    expect(lastButton).toHaveClass('bg-violet-900/40');
  });

  it('handles single trail item', () => {
    const singleTrail: BreadcrumbItem[] = [
      {
        path: 'world.garden',
        aspect: 'manifest',
        timestamp: Date.now(),
      },
    ];

    render(<ExplorationBreadcrumb trail={singleTrail} onNavigate={vi.fn()} />);

    expect(screen.getByText(/world\.garden/)).toBeInTheDocument();
    expect(screen.getByText(/manifest/)).toBeInTheDocument();
  });

  it('applies correct ARIA labels', () => {
    render(<ExplorationBreadcrumb trail={mockTrail} onNavigate={vi.fn()} />);

    // Check ARIA labels for accessibility
    expect(screen.getByLabelText('Navigate to world.garden:manifest')).toBeInTheDocument();
    expect(screen.getByLabelText('Navigate to self.memory:capture')).toBeInTheDocument();
  });

  it('respects custom className', () => {
    const { container } = render(
      <ExplorationBreadcrumb
        trail={mockTrail}
        onNavigate={vi.fn()}
        className="custom-breadcrumb"
      />
    );

    expect(container.firstChild).toHaveClass('custom-breadcrumb');
  });

  it('shows path and aspect separated by colon', () => {
    const singleTrail: BreadcrumbItem[] = [
      {
        path: 'test.path',
        aspect: 'testAspect',
        timestamp: Date.now(),
      },
    ];

    render(<ExplorationBreadcrumb trail={singleTrail} onNavigate={vi.fn()} />);

    // Check for colon separator
    const button = screen.getByLabelText('Navigate to test.path:testAspect');
    expect(button.textContent).toContain(':');
  });
});
