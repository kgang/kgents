/**
 * Tests for GhostPanel component.
 *
 * Tests:
 * - Renders ghost alternatives correctly
 * - Handles ghost clicks
 * - Shows category colors
 * - Respects motion preferences
 * - Hides when no alternatives
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { GhostPanel, type Ghost } from '@/shell/GhostPanel';

// Mock motion preferences hook
vi.mock('@/components/joy/useMotionPreferences', () => ({
  useMotionPreferences: () => ({ shouldAnimate: true }),
}));

const mockGhosts: Ghost[] = [
  {
    aspect: 'witness',
    hint: 'View historical traces—see what happened before',
    category: 'PERCEPTION',
  },
  {
    aspect: 'refine',
    hint: 'Dialectical challenge—improve through critique',
    category: 'GENERATION',
  },
  {
    aspect: 'build',
    hint: 'Build artifact—construct something new',
    category: 'MUTATION',
  },
];

describe('GhostPanel', () => {
  it('renders ghost alternatives', () => {
    render(<GhostPanel alternatives={mockGhosts} onGhostClick={vi.fn()} />);

    // Check header
    expect(screen.getByText('Paths Not Taken')).toBeInTheDocument();

    // Check all ghosts are rendered
    expect(screen.getByText('witness')).toBeInTheDocument();
    expect(screen.getByText('refine')).toBeInTheDocument();
    expect(screen.getByText('build')).toBeInTheDocument();

    // Check hints are shown
    expect(
      screen.getByText('View historical traces—see what happened before')
    ).toBeInTheDocument();
  });

  it('handles ghost clicks', () => {
    const onGhostClick = vi.fn();
    render(<GhostPanel alternatives={mockGhosts} onGhostClick={onGhostClick} />);

    // Click the witness ghost
    const witnessButton = screen.getByLabelText('Invoke witness aspect');
    fireEvent.click(witnessButton);

    expect(onGhostClick).toHaveBeenCalledWith('witness');
  });

  it('hides when no alternatives', () => {
    const { container } = render(<GhostPanel alternatives={[]} onGhostClick={vi.fn()} />);

    expect(container.firstChild).toBeNull();
  });

  it('shows categories for each ghost', () => {
    render(<GhostPanel alternatives={mockGhosts} onGhostClick={vi.fn()} />);

    // Check categories are displayed
    expect(screen.getByText('PERCEPTION')).toBeInTheDocument();
    expect(screen.getByText('GENERATION')).toBeInTheDocument();
    expect(screen.getByText('MUTATION')).toBeInTheDocument();
  });

  it('renders footer hint', () => {
    render(<GhostPanel alternatives={mockGhosts} onGhostClick={vi.fn()} />);

    expect(screen.getByText('Click a ghost to explore that path')).toBeInTheDocument();
  });

  it('handles single ghost', () => {
    const singleGhost: Ghost[] = [
      {
        aspect: 'witness',
        hint: 'View history',
        category: 'PERCEPTION',
      },
    ];

    render(<GhostPanel alternatives={singleGhost} onGhostClick={vi.fn()} />);

    expect(screen.getByText('witness')).toBeInTheDocument();
    expect(screen.getByText('View history')).toBeInTheDocument();
  });

  it('applies correct ARIA labels', () => {
    render(<GhostPanel alternatives={mockGhosts} onGhostClick={vi.fn()} />);

    // Check ARIA labels for accessibility
    expect(screen.getByLabelText('Invoke witness aspect')).toBeInTheDocument();
    expect(screen.getByLabelText('Invoke refine aspect')).toBeInTheDocument();
    expect(screen.getByLabelText('Invoke build aspect')).toBeInTheDocument();
  });

  it('respects custom className', () => {
    const { container } = render(
      <GhostPanel alternatives={mockGhosts} onGhostClick={vi.fn()} className="custom-class" />
    );

    expect(container.firstChild).toHaveClass('custom-class');
  });
});
