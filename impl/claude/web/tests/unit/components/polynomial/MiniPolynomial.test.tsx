/**
 * Tests for MiniPolynomial component
 *
 * Verifies:
 * - Renders all positions
 * - Highlights current position correctly
 * - Shows directions for each position
 * - Handles transition clicks
 * - Respects visual hierarchy
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MiniPolynomial } from '@/components/polynomial/MiniPolynomial';

describe('MiniPolynomial', () => {
  it('renders all positions', () => {
    render(
      <MiniPolynomial
        positions={['idle', 'working', 'done']}
        current="working"
        directions={{
          idle: ['start'],
          working: ['pause', 'finish'],
          done: ['reset'],
        }}
      />
    );

    expect(screen.getByText('idle')).toBeInTheDocument();
    expect(screen.getByText('working')).toBeInTheDocument();
    expect(screen.getByText('done')).toBeInTheDocument();
  });

  it('highlights current position', () => {
    render(
      <MiniPolynomial
        positions={['idle', 'working', 'done']}
        current="working"
        directions={{
          idle: ['start'],
          working: ['pause', 'finish'],
          done: ['reset'],
        }}
      />
    );

    // Current position should have emerald color class
    const workingText = screen.getByText('working');
    expect(workingText).toHaveClass('text-emerald-400');

    // Non-current positions should have gray color
    const idleText = screen.getByText('idle');
    expect(idleText).toHaveClass('text-gray-400');
  });

  it('shows (current) label for current position', () => {
    render(
      <MiniPolynomial
        positions={['idle', 'working']}
        current="working"
        directions={{
          idle: ['start'],
          working: ['pause'],
        }}
      />
    );

    expect(screen.getByText('(current)')).toBeInTheDocument();
  });

  it('displays directions for each position', () => {
    render(
      <MiniPolynomial
        positions={['idle', 'working', 'done']}
        current="working"
        directions={{
          idle: ['start'],
          working: ['pause', 'finish'],
          done: ['reset'],
        }}
      />
    );

    expect(screen.getByText('start')).toBeInTheDocument();
    expect(screen.getByText('pause')).toBeInTheDocument();
    expect(screen.getByText('finish')).toBeInTheDocument();
    expect(screen.getByText('reset')).toBeInTheDocument();
  });

  it('calls onTransitionClick when direction is clicked', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(
      <MiniPolynomial
        positions={['idle', 'working']}
        current="working"
        directions={{
          idle: ['start'],
          working: ['pause', 'finish'],
        }}
        onTransitionClick={handleClick}
      />
    );

    const pauseButton = screen.getByText('pause');
    await user.click(pauseButton);

    expect(handleClick).toHaveBeenCalledWith('working', 'pause');
  });

  it('works without onTransitionClick handler', () => {
    const { container } = render(
      <MiniPolynomial
        positions={['idle']}
        current="idle"
        directions={{ idle: ['start'] }}
      />
    );

    // Should render without errors
    expect(container).toBeInTheDocument();
  });

  it('handles positions with no directions', () => {
    render(
      <MiniPolynomial
        positions={['start', 'end']}
        current="end"
        directions={{
          start: ['begin'],
          end: [], // Terminal state with no directions
        }}
      />
    );

    expect(screen.getByText('start')).toBeInTheDocument();
    expect(screen.getByText('end')).toBeInTheDocument();
    expect(screen.getByText('begin')).toBeInTheDocument();
  });

  it('handles single default position', () => {
    render(
      <MiniPolynomial
        positions={['default']}
        current="default"
        directions={{
          default: ['manifest', 'witness', 'affordances'],
        }}
      />
    );

    expect(screen.getByText('default')).toBeInTheDocument();
    expect(screen.getByText('manifest')).toBeInTheDocument();
    expect(screen.getByText('witness')).toBeInTheDocument();
    expect(screen.getByText('affordances')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <MiniPolynomial
        positions={['idle']}
        current="idle"
        directions={{ idle: [] }}
        className="custom-class"
      />
    );

    const rootDiv = container.firstChild;
    expect(rootDiv).toHaveClass('custom-class');
  });
});
