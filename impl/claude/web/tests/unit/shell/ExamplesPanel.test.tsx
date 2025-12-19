/**
 * Tests for ExamplesPanel component
 * Part of Habitat 2.0: Priority 2 - Habitat Examples
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ExamplesPanel, type NodeExample } from '@/shell/ExamplesPanel';

describe('ExamplesPanel', () => {
  const mockExamples: NodeExample[] = [
    {
      aspect: 'search',
      kwargs: { query: 'Python tips', limit: 5 },
      label: 'Search for Python',
    },
    {
      aspect: 'recent',
      kwargs: { limit: 10 },
      label: 'Show recent memories',
    },
    {
      aspect: 'capture',
      kwargs: {},
      label: 'Capture content',
    },
  ];

  it('renders nothing when examples array is empty', () => {
    const { container } = render(
      <ExamplesPanel examples={[]} onExampleClick={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders all provided examples', () => {
    render(<ExamplesPanel examples={mockExamples} onExampleClick={vi.fn()} />);

    expect(screen.getByText('Search for Python')).toBeInTheDocument();
    expect(screen.getByText('Show recent memories')).toBeInTheDocument();
    expect(screen.getByText('Capture content')).toBeInTheDocument();
  });

  it('displays aspect names in monospace font', () => {
    render(<ExamplesPanel examples={mockExamples} onExampleClick={vi.fn()} />);

    // Check that aspect names are displayed
    expect(screen.getByText('search')).toBeInTheDocument();
    expect(screen.getByText('recent')).toBeInTheDocument();
    expect(screen.getByText('capture')).toBeInTheDocument();
  });

  it('shows kwargs as JSON when present', () => {
    render(<ExamplesPanel examples={mockExamples} onExampleClick={vi.fn()} />);

    // First example has kwargs - should display JSON
    const firstExample = screen.getByText('Search for Python').closest('button');
    expect(firstExample).toBeInTheDocument();
    expect(firstExample?.textContent).toContain('query');
    expect(firstExample?.textContent).toContain('Python tips');
  });

  it('does not show kwargs section when kwargs is empty', () => {
    const examplesWithEmpty: NodeExample[] = [
      {
        aspect: 'manifest',
        kwargs: {},
        label: 'View status',
      },
    ];

    const { container } = render(
      <ExamplesPanel examples={examplesWithEmpty} onExampleClick={vi.fn()} />
    );

    // Should not have a <pre> tag for JSON when kwargs is empty
    const preElements = container.querySelectorAll('pre');
    expect(preElements.length).toBe(0);
  });

  it('calls onExampleClick with correct example when button is clicked', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(<ExamplesPanel examples={mockExamples} onExampleClick={handleClick} />);

    const firstButton = screen.getByText('Search for Python').closest('button');
    expect(firstButton).toBeInTheDocument();

    await user.click(firstButton!);

    expect(handleClick).toHaveBeenCalledTimes(1);
    expect(handleClick).toHaveBeenCalledWith(mockExamples[0]);
  });

  it('each button has proper aria-label for accessibility', () => {
    render(<ExamplesPanel examples={mockExamples} onExampleClick={vi.fn()} />);

    const buttons = screen.getAllByRole('button');
    expect(buttons[0]).toHaveAttribute('aria-label', 'Run example: Search for Python');
    expect(buttons[1]).toHaveAttribute('aria-label', 'Run example: Show recent memories');
    expect(buttons[2]).toHaveAttribute('aria-label', 'Run example: Capture content');
  });

  it('renders with custom className', () => {
    const { container } = render(
      <ExamplesPanel
        examples={mockExamples}
        onExampleClick={vi.fn()}
        className="custom-class"
      />
    );

    const panel = container.firstChild as HTMLElement;
    expect(panel.className).toContain('custom-class');
  });

  it('displays play icon for each example', () => {
    const { container } = render(
      <ExamplesPanel examples={mockExamples} onExampleClick={vi.fn()} />
    );

    // Check for SVG elements (Lucide icons render as SVG)
    const svgElements = container.querySelectorAll('svg');
    // At least 4 SVGs: 1 for header + 3 for examples
    expect(svgElements.length).toBeGreaterThanOrEqual(4);
  });

  it('handles multiple examples with same aspect name', async () => {
    const user = userEvent.setup();
    const duplicateExamples: NodeExample[] = [
      {
        aspect: 'search',
        kwargs: { query: 'Python' },
        label: 'Search Python',
      },
      {
        aspect: 'search',
        kwargs: { query: 'JavaScript' },
        label: 'Search JavaScript',
      },
    ];

    const handleClick = vi.fn();
    render(
      <ExamplesPanel examples={duplicateExamples} onExampleClick={handleClick} />
    );

    const buttons = screen.getAllByRole('button');
    await user.click(buttons[0]);
    expect(handleClick).toHaveBeenCalledWith(duplicateExamples[0]);

    await user.click(buttons[1]);
    expect(handleClick).toHaveBeenCalledWith(duplicateExamples[1]);
  });
});
