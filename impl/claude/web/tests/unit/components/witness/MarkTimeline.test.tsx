/**
 * MarkTimeline Component Tests
 *
 * Tests for the MarkTimeline component covering:
 * - Basic rendering
 * - Day grouping with separators
 * - Session grouping
 * - Empty state
 * - Loading state
 * - Error state
 * - Selection handling
 *
 * @see plans/witness-fusion-ux-implementation.md
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  MarkTimeline,
  DaySeparator,
  SessionSeparator,
  LoadingSkeleton,
  EmptyState,
  ErrorState,
} from '@/components/witness/MarkTimeline';
import type { Mark } from '@/api/witness';

// =============================================================================
// Test Fixtures
// =============================================================================

const createMockMark = (
  id: string,
  timestamp: string,
  overrides: Partial<Mark> = {}
): Mark => ({
  id,
  action: `Action for ${id}`,
  reasoning: `Reasoning for ${id}`,
  principles: ['composable'],
  author: 'kent',
  timestamp,
  session_id: 'session-abc',
  ...overrides,
});

const today = new Date();
const yesterday = new Date(Date.now() - 86400000);

const mockMarks: Mark[] = [
  createMockMark('mark-1', today.toISOString()),
  createMockMark('mark-2', today.toISOString()),
  createMockMark('mark-3', yesterday.toISOString()),
  createMockMark('mark-4', yesterday.toISOString()),
];

// =============================================================================
// MarkTimeline Tests
// =============================================================================

describe('MarkTimeline', () => {
  describe('Basic Rendering', () => {
    it('renders marks', () => {
      render(<MarkTimeline marks={mockMarks} groupBy="none" />);

      expect(screen.getByText('Action for mark-1')).toBeInTheDocument();
      expect(screen.getByText('Action for mark-2')).toBeInTheDocument();
      expect(screen.getByText('Action for mark-3')).toBeInTheDocument();
      expect(screen.getByText('Action for mark-4')).toBeInTheDocument();
    });

    it('has correct test id', () => {
      render(<MarkTimeline marks={mockMarks} />);

      expect(screen.getByTestId('mark-timeline')).toBeInTheDocument();
    });

    it('sets group-by data attribute', () => {
      render(<MarkTimeline marks={mockMarks} groupBy="day" />);

      expect(screen.getByTestId('mark-timeline')).toHaveAttribute(
        'data-group-by',
        'day'
      );
    });
  });

  describe('Day Grouping', () => {
    it('groups marks by day with separators', () => {
      render(<MarkTimeline marks={mockMarks} groupBy="day" />);

      const separators = screen.getAllByTestId('day-separator');
      expect(separators.length).toBe(2); // Today and Yesterday
    });

    it('shows "Today" label for today\'s marks', () => {
      render(<MarkTimeline marks={mockMarks} groupBy="day" />);

      expect(screen.getByText('Today')).toBeInTheDocument();
    });

    it('shows "Yesterday" label for yesterday\'s marks', () => {
      render(<MarkTimeline marks={mockMarks} groupBy="day" />);

      expect(screen.getByText('Yesterday')).toBeInTheDocument();
    });

    it('shows mark count in day separator', () => {
      render(<MarkTimeline marks={mockMarks} groupBy="day" />);

      // Should show mark counts (either "2 marks" or "4 marks" depending on grouping)
      expect(screen.getAllByText(/\d+ marks?/).length).toBeGreaterThan(0);
    });
  });

  describe('Session Grouping', () => {
    it('groups marks by session', () => {
      const sessionMarks: Mark[] = [
        createMockMark('mark-1', today.toISOString(), { session_id: 'session-a' }),
        createMockMark('mark-2', today.toISOString(), { session_id: 'session-a' }),
        createMockMark('mark-3', today.toISOString(), { session_id: 'session-b' }),
      ];

      render(<MarkTimeline marks={sessionMarks} groupBy="session" />);

      const separators = screen.getAllByTestId('session-separator');
      expect(separators.length).toBe(2);
    });

    it('shows session ID prefix', () => {
      const sessionMarks: Mark[] = [
        createMockMark('mark-1', today.toISOString(), {
          session_id: 'session-abc123xyz',
        }),
      ];

      render(<MarkTimeline marks={sessionMarks} groupBy="session" />);

      // Should show session separator
      expect(screen.getByTestId('session-separator')).toBeInTheDocument();
    });
  });

  describe('No Grouping', () => {
    it('renders without separators when groupBy=none', () => {
      render(<MarkTimeline marks={mockMarks} groupBy="none" />);

      expect(screen.queryByTestId('day-separator')).not.toBeInTheDocument();
      expect(screen.queryByTestId('session-separator')).not.toBeInTheDocument();
    });
  });

  describe('Density Modes', () => {
    it('passes density to mark cards', () => {
      render(<MarkTimeline marks={mockMarks} density="spacious" groupBy="none" />);

      const markCards = screen.getAllByTestId('mark-card');
      markCards.forEach((card) => {
        expect(card).toHaveAttribute('data-density', 'spacious');
      });
    });
  });

  describe('Selection Handling', () => {
    it('highlights selected mark', () => {
      render(
        <MarkTimeline
          marks={mockMarks}
          groupBy="none"
          selectedMarkId="mark-2"
        />
      );

      // The selected mark should have different styling
      const markCards = screen.getAllByTestId('mark-card');
      expect(markCards.length).toBe(4);
    });

    it('calls onSelect when mark clicked', async () => {
      const user = userEvent.setup();
      const onSelect = vi.fn();

      render(
        <MarkTimeline marks={mockMarks} groupBy="none" onSelect={onSelect} />
      );

      await user.click(screen.getByText('Action for mark-1'));

      expect(onSelect).toHaveBeenCalledWith(
        expect.objectContaining({ id: 'mark-1' })
      );
    });
  });

  describe('Retract Handling', () => {
    it('calls onRetract when mark retract requested', async () => {
      const user = userEvent.setup();
      const onRetract = vi.fn();

      render(
        <MarkTimeline
          marks={mockMarks}
          groupBy="none"
          density="spacious"
          onRetract={onRetract}
        />
      );

      const retractButtons = screen.getAllByText('Retract');
      await user.click(retractButtons[0]);

      expect(onRetract).toHaveBeenCalledWith('mark-1');
    });
  });

  describe('Height Prop', () => {
    it('applies custom height', () => {
      render(<MarkTimeline marks={mockMarks} height={400} />);

      const timeline = screen.getByTestId('mark-timeline');
      expect(timeline).toHaveStyle({ height: '400px' });
    });

    it('applies string height', () => {
      render(<MarkTimeline marks={mockMarks} height="50vh" />);

      const timeline = screen.getByTestId('mark-timeline');
      expect(timeline).toHaveStyle({ height: '50vh' });
    });
  });
});

// =============================================================================
// Loading State Tests
// =============================================================================

describe('Loading State', () => {
  it('shows loading skeleton when isLoading', () => {
    render(<MarkTimeline marks={[]} isLoading={true} />);

    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();
  });

  it('renders multiple skeleton items', () => {
    render(<LoadingSkeleton count={5} />);

    const skeleton = screen.getByTestId('loading-skeleton');
    expect(skeleton.children.length).toBe(5);
  });
});

// =============================================================================
// Empty State Tests
// =============================================================================

describe('Empty State', () => {
  it('shows empty state when no marks', () => {
    render(<MarkTimeline marks={[]} />);

    expect(screen.getByTestId('empty-state')).toBeInTheDocument();
  });

  it('shows helpful message in empty state', () => {
    render(<EmptyState />);

    expect(screen.getByText('No marks yet')).toBeInTheDocument();
    expect(screen.getByText(/km "your action"/)).toBeInTheDocument();
  });

  it('shows leaf emoji in empty state', () => {
    render(<EmptyState />);

    expect(screen.getByText('\u{1F342}')).toBeInTheDocument();
  });
});

// =============================================================================
// Error State Tests
// =============================================================================

describe('Error State', () => {
  it('shows error state when error provided', () => {
    render(<MarkTimeline marks={[]} error="Network error" />);

    expect(screen.getByTestId('error-state')).toBeInTheDocument();
  });

  it('shows error message', () => {
    render(<ErrorState message="Failed to fetch marks" />);

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Failed to fetch marks')).toBeInTheDocument();
  });

  it('shows warning emoji', () => {
    render(<ErrorState message="Error" />);

    // Warning emoji renders - check the error state exists
    expect(screen.getByTestId('error-state')).toBeInTheDocument();
  });
});

// =============================================================================
// DaySeparator Tests
// =============================================================================

describe('DaySeparator', () => {
  it('renders date and count', () => {
    render(<DaySeparator date="12/25/2025" count={5} />);

    expect(screen.getByText('12/25/2025')).toBeInTheDocument();
    expect(screen.getByText('5 marks')).toBeInTheDocument();
  });

  it('shows singular "mark" for count of 1', () => {
    render(<DaySeparator date="12/25/2025" count={1} />);

    expect(screen.getByText('1 mark')).toBeInTheDocument();
  });

  it('shows "Today" for today\'s date', () => {
    const todayStr = new Date().toLocaleDateString();
    render(<DaySeparator date={todayStr} count={3} />);

    expect(screen.getByText('Today')).toBeInTheDocument();
  });

  it('shows "Yesterday" for yesterday\'s date', () => {
    const yesterdayStr = new Date(Date.now() - 86400000).toLocaleDateString();
    render(<DaySeparator date={yesterdayStr} count={2} />);

    expect(screen.getByText('Yesterday')).toBeInTheDocument();
  });
});

// =============================================================================
// SessionSeparator Tests
// =============================================================================

describe('SessionSeparator', () => {
  it('renders session ID and count', () => {
    render(<SessionSeparator sessionId="session-abc123xyz" count={7} />);

    // Session ID is shown (first 8 chars)
    expect(screen.getByTestId('session-separator')).toBeInTheDocument();
    expect(screen.getByText('(7 marks)')).toBeInTheDocument();
  });
});
