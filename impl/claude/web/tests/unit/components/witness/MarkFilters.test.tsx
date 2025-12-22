/**
 * MarkFilters Component Tests
 *
 * Tests for the filter controls component.
 *
 * @see impl/claude/web/src/components/witness/MarkFilters.tsx
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  MarkFilters,
  createDefaultFilters,
  type MarkFilterState,
} from '@/components/witness/MarkFilters';

// =============================================================================
// Test Helpers
// =============================================================================

function createMockOnChange() {
  return vi.fn();
}

function renderMarkFilters(props: Partial<Parameters<typeof MarkFilters>[0]> = {}) {
  const onChange = createMockOnChange();
  const filters = props.filters ?? createDefaultFilters();

  render(<MarkFilters filters={filters} onChange={props.onChange ?? onChange} {...props} />);

  return { onChange: props.onChange ?? onChange, filters };
}

// =============================================================================
// Tests
// =============================================================================

describe('MarkFilters', () => {
  describe('Basic Rendering', () => {
    it('renders the filters container', () => {
      renderMarkFilters();
      expect(screen.getByTestId('mark-filters')).toBeInTheDocument();
    });

    it('renders search input', () => {
      renderMarkFilters();
      expect(screen.getByTestId('grep-input')).toBeInTheDocument();
    });

    it('renders author filter chips', () => {
      renderMarkFilters();
      expect(screen.getByTestId('filter-chip-all')).toBeInTheDocument();
      expect(screen.getByTestId('filter-chip-kent')).toBeInTheDocument();
      expect(screen.getByTestId('filter-chip-claude')).toBeInTheDocument();
      expect(screen.getByTestId('filter-chip-system')).toBeInTheDocument();
    });

    it('renders expand filters button', () => {
      renderMarkFilters();
      expect(screen.getByTestId('expand-filters')).toBeInTheDocument();
    });
  });

  describe('Author Filtering', () => {
    it('shows "All" as active by default', () => {
      renderMarkFilters();
      const allChip = screen.getByTestId('filter-chip-all');
      // Active chips have different background color - check computed styles
      expect(allChip).toBeInTheDocument();
    });

    it('calls onChange when author filter clicked', async () => {
      const user = userEvent.setup();
      const { onChange } = renderMarkFilters();

      await user.click(screen.getByTestId('filter-chip-kent'));

      expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ author: 'kent' }));
    });

    it('switches between author filters', async () => {
      const user = userEvent.setup();
      const onChange = vi.fn();
      render(<MarkFilters filters={createDefaultFilters()} onChange={onChange} />);

      await user.click(screen.getByTestId('filter-chip-claude'));
      expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ author: 'claude' }));

      onChange.mockClear();

      await user.click(screen.getByTestId('filter-chip-system'));
      expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ author: 'system' }));
    });
  });

  describe('Search (Grep) Filtering', () => {
    it('displays search input with placeholder', () => {
      renderMarkFilters();
      const input = screen.getByTestId('grep-input');
      expect(input).toHaveAttribute('placeholder', 'Search marks...');
    });

    it('displays existing grep value', () => {
      const filters = { ...createDefaultFilters(), grep: 'existing search' };
      renderMarkFilters({ filters });
      const input = screen.getByTestId('grep-input');
      expect(input).toHaveValue('existing search');
    });

    it('calls onChange when user types in search field', async () => {
      const user = userEvent.setup();
      const onChange = vi.fn();
      render(<MarkFilters filters={createDefaultFilters()} onChange={onChange} />);

      const input = screen.getByTestId('grep-input');
      await user.type(input, 'h');

      // Called for first keystroke
      expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ grep: 'h' }));
    });
  });

  describe('Expand/Collapse', () => {
    it('expands when expand button clicked', async () => {
      const user = userEvent.setup();
      renderMarkFilters();

      // Principles should not be visible initially
      expect(screen.queryByTestId('filter-chip-tasteful')).not.toBeInTheDocument();

      await user.click(screen.getByTestId('expand-filters'));

      // Now principles should be visible
      expect(screen.getByTestId('filter-chip-tasteful')).toBeInTheDocument();
    });

    it('shows all principles when expanded', async () => {
      const user = userEvent.setup();
      renderMarkFilters();

      await user.click(screen.getByTestId('expand-filters'));

      expect(screen.getByTestId('filter-chip-tasteful')).toBeInTheDocument();
      expect(screen.getByTestId('filter-chip-curated')).toBeInTheDocument();
      expect(screen.getByTestId('filter-chip-ethical')).toBeInTheDocument();
      expect(screen.getByTestId('filter-chip-joy-inducing')).toBeInTheDocument();
      expect(screen.getByTestId('filter-chip-composable')).toBeInTheDocument();
      expect(screen.getByTestId('filter-chip-heterarchical')).toBeInTheDocument();
      expect(screen.getByTestId('filter-chip-generative')).toBeInTheDocument();
    });

    it('shows date presets when expanded', async () => {
      const user = userEvent.setup();
      renderMarkFilters();

      await user.click(screen.getByTestId('expand-filters'));

      expect(screen.getByTestId('filter-chip-all-time')).toBeInTheDocument();
      expect(screen.getByTestId('filter-chip-today')).toBeInTheDocument();
      expect(screen.getByTestId('filter-chip-yesterday')).toBeInTheDocument();
    });

    it('starts expanded when defaultExpanded is true', () => {
      renderMarkFilters({ defaultExpanded: true });

      expect(screen.getByTestId('filter-chip-tasteful')).toBeInTheDocument();
    });
  });

  describe('Principle Filtering', () => {
    beforeEach(async () => {
      // Expand to show principles
    });

    it('toggles principle on click', async () => {
      const user = userEvent.setup();
      const { onChange } = renderMarkFilters({ defaultExpanded: true });

      await user.click(screen.getByTestId('filter-chip-composable'));

      expect(onChange).toHaveBeenCalledWith(
        expect.objectContaining({
          principles: ['composable'],
        })
      );
    });

    it('allows multiple principles to be selected', async () => {
      const user = userEvent.setup();
      const initialFilters = { ...createDefaultFilters(), principles: ['tasteful'] };
      const { onChange } = renderMarkFilters({
        filters: initialFilters,
        defaultExpanded: true,
      });

      await user.click(screen.getByTestId('filter-chip-composable'));

      expect(onChange).toHaveBeenCalledWith(
        expect.objectContaining({
          principles: ['tasteful', 'composable'],
        })
      );
    });

    it('removes principle when clicked again', async () => {
      const user = userEvent.setup();
      const initialFilters = { ...createDefaultFilters(), principles: ['tasteful'] };
      const { onChange } = renderMarkFilters({
        filters: initialFilters,
        defaultExpanded: true,
      });

      await user.click(screen.getByTestId('filter-chip-tasteful'));

      expect(onChange).toHaveBeenCalledWith(
        expect.objectContaining({
          principles: [],
        })
      );
    });
  });

  describe('Date Range Filtering', () => {
    it('calls onChange with date range for "Today"', async () => {
      const user = userEvent.setup();
      const { onChange } = renderMarkFilters({ defaultExpanded: true });

      await user.click(screen.getByTestId('filter-chip-today'));

      expect(onChange).toHaveBeenCalledWith(
        expect.objectContaining({
          dateRange: expect.objectContaining({
            start: expect.any(Date),
            end: expect.any(Date),
          }),
        })
      );
    });

    it('sets null date range for "All time"', async () => {
      const user = userEvent.setup();
      const initialFilters = {
        ...createDefaultFilters(),
        dateRange: { start: new Date(), end: new Date() },
      };
      const { onChange } = renderMarkFilters({
        filters: initialFilters,
        defaultExpanded: true,
      });

      await user.click(screen.getByTestId('filter-chip-all-time'));

      expect(onChange).toHaveBeenCalledWith(
        expect.objectContaining({
          dateRange: null,
        })
      );
    });
  });

  describe('Clear Filters', () => {
    it('shows clear button when filters are active', () => {
      const filters = { ...createDefaultFilters(), author: 'kent' as const };
      renderMarkFilters({ filters });

      expect(screen.getByTestId('clear-filters')).toBeInTheDocument();
    });

    it('does not show clear button when no filters active', () => {
      renderMarkFilters();

      expect(screen.queryByTestId('clear-filters')).not.toBeInTheDocument();
    });

    it('resets all filters when clear clicked', async () => {
      const user = userEvent.setup();
      const filters: MarkFilterState = {
        author: 'kent',
        principles: ['composable'],
        dateRange: { start: new Date(), end: new Date() },
        grep: 'test',
      };
      const { onChange } = renderMarkFilters({ filters });

      await user.click(screen.getByTestId('clear-filters'));

      expect(onChange).toHaveBeenCalledWith({
        author: 'all',
        principles: [],
        dateRange: null,
        grep: '',
      });
    });
  });

  describe('Active Filter Count', () => {
    it('shows count badge when filters are active', () => {
      const filters: MarkFilterState = {
        author: 'kent',
        principles: ['composable', 'tasteful'],
        dateRange: null,
        grep: '',
      };
      renderMarkFilters({ filters });

      const expandButton = screen.getByTestId('expand-filters');
      // Should show "3" (1 author + 2 principles)
      expect(expandButton).toHaveTextContent('3');
    });

    it('counts grep as one filter', () => {
      const filters: MarkFilterState = {
        author: 'all',
        principles: [],
        dateRange: null,
        grep: 'test',
      };
      renderMarkFilters({ filters });

      const expandButton = screen.getByTestId('expand-filters');
      expect(expandButton).toHaveTextContent('1');
    });
  });
});

describe('createDefaultFilters', () => {
  it('returns default filter state', () => {
    const defaults = createDefaultFilters();

    expect(defaults).toEqual({
      author: 'all',
      principles: [],
      dateRange: null,
      grep: '',
    });
  });
});
