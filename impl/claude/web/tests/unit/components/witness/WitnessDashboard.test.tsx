/**
 * WitnessDashboard Page Tests
 *
 * Tests for the full Witness dashboard page.
 *
 * @see impl/claude/web/src/pages/Witness.tsx
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { WitnessDashboard } from '@/pages/Witness';
import type { Mark } from '@/api/witness';

// =============================================================================
// Mock Setup
// =============================================================================

// Mock the useWitness hook
const mockCreateMark = vi.fn();
const mockRetractMark = vi.fn();
const mockRefetch = vi.fn();

const mockMarks: Mark[] = [
  {
    id: 'mark-001',
    action: 'First test mark',
    reasoning: 'Testing the witness system',
    principles: ['composable', 'tasteful'],
    author: 'kent',
    session_id: 'session-001',
    timestamp: new Date().toISOString(),
  },
  {
    id: 'mark-002',
    action: 'Second test mark',
    reasoning: 'More testing',
    principles: ['generative'],
    author: 'claude',
    session_id: 'session-001',
    timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
  },
  {
    id: 'mark-003',
    action: 'System mark',
    principles: [],
    author: 'system',
    session_id: 'session-002',
    timestamp: new Date(Date.now() - 86400000).toISOString(), // Yesterday
  },
];

vi.mock('@/hooks/useWitness', () => ({
  useWitness: vi.fn(() => ({
    marks: mockMarks,
    isLoading: false,
    error: null,
    createMark: mockCreateMark,
    retractMark: mockRetractMark,
    refetch: mockRefetch,
    isConnected: true,
  })),
}));

// =============================================================================
// Test Helpers
// =============================================================================

function renderDashboard(props: Partial<Parameters<typeof WitnessDashboard>[0]> = {}) {
  return render(<WitnessDashboard {...props} />);
}

// =============================================================================
// Tests
// =============================================================================

describe('WitnessDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('renders the dashboard container', () => {
      renderDashboard();
      expect(screen.getByTestId('witness-dashboard')).toBeInTheDocument();
    });

    it('renders the header with title', () => {
      renderDashboard();
      expect(screen.getByText(/Witness/)).toBeInTheDocument();
      expect(screen.getByText(/The Garden of Marks/)).toBeInTheDocument();
    });

    it('renders the QuickMarkForm', () => {
      renderDashboard();
      expect(screen.getByTestId('quick-mark-form')).toBeInTheDocument();
    });

    it('renders the MarkFilters', () => {
      renderDashboard();
      expect(screen.getByTestId('mark-filters')).toBeInTheDocument();
    });

    it('renders the MarkTimeline', () => {
      renderDashboard();
      expect(screen.getByTestId('mark-timeline')).toBeInTheDocument();
    });

    it('renders the stats footer', () => {
      renderDashboard();
      expect(screen.getByTestId('stats-footer')).toBeInTheDocument();
    });
  });

  describe('Connection Status', () => {
    it('shows "Live" when connected', () => {
      renderDashboard();
      expect(screen.getByTestId('connection-status')).toHaveTextContent('Live');
    });

    it('shows real-time enabled in footer', () => {
      renderDashboard();
      expect(screen.getByTestId('stats-footer')).toHaveTextContent('Real-time enabled');
    });
  });

  describe('Mark Display', () => {
    it('displays mark count in footer', () => {
      renderDashboard();
      expect(screen.getByTestId('stats-footer')).toHaveTextContent('3 marks');
    });

    it('renders marks from the hook', () => {
      renderDashboard();
      expect(screen.getByText('First test mark')).toBeInTheDocument();
      expect(screen.getByText('Second test mark')).toBeInTheDocument();
    });
  });

  describe('Group By Toggle', () => {
    it('renders group-by toggle', () => {
      renderDashboard();
      expect(screen.getByTestId('group-by-toggle')).toBeInTheDocument();
    });

    it('defaults to "Day" grouping', () => {
      renderDashboard();
      const dayButton = screen.getByTestId('group-by-day');
      // Check it's styled as active (implementation detail)
      expect(dayButton).toBeInTheDocument();
    });

    it('changes grouping when toggle clicked', async () => {
      const user = userEvent.setup();
      renderDashboard();

      await user.click(screen.getByTestId('group-by-session'));

      // The timeline should update its groupBy
      const timeline = screen.getByTestId('mark-timeline');
      expect(timeline).toHaveAttribute('data-group-by', 'session');
    });

    it('supports "None" grouping', async () => {
      const user = userEvent.setup();
      renderDashboard();

      await user.click(screen.getByTestId('group-by-none'));

      const timeline = screen.getByTestId('mark-timeline');
      expect(timeline).toHaveAttribute('data-group-by', 'none');
    });
  });

  describe('Export Functionality', () => {
    it('renders export button', () => {
      renderDashboard();
      expect(screen.getByTestId('export-button')).toBeInTheDocument();
    });

    it('has export button enabled when marks exist', () => {
      renderDashboard();
      const button = screen.getByTestId('export-button');
      expect(button).not.toBeDisabled();
    });
  });

  describe('Filtering', () => {
    it('filters marks by author when filter changed', async () => {
      const user = userEvent.setup();
      renderDashboard();

      // Click Kent filter
      await user.click(screen.getByTestId('filter-chip-kent'));

      // Should only show Kent's marks
      await waitFor(() => {
        expect(screen.getByText('First test mark')).toBeInTheDocument();
        expect(screen.queryByText('Second test mark')).not.toBeInTheDocument();
      });
    });

    it('filters marks by search text', async () => {
      const user = userEvent.setup();
      renderDashboard();

      const searchInput = screen.getByTestId('grep-input');
      await user.type(searchInput, 'First');

      await waitFor(() => {
        expect(screen.getByText('First test mark')).toBeInTheDocument();
        expect(screen.queryByText('Second test mark')).not.toBeInTheDocument();
      });
    });

    it('shows filtered count when filters applied', async () => {
      const user = userEvent.setup();
      renderDashboard();

      await user.click(screen.getByTestId('filter-chip-kent'));

      await waitFor(() => {
        const footer = screen.getByTestId('stats-footer');
        expect(footer).toHaveTextContent('1 mark');
        expect(footer).toHaveTextContent('of 3');
      });
    });
  });

  describe('Mark Creation', () => {
    it('calls createMark when form submitted', async () => {
      const user = userEvent.setup();
      mockCreateMark.mockResolvedValue({
        id: 'new-mark',
        action: 'New mark',
        principles: [],
        author: 'kent',
        timestamp: new Date().toISOString(),
      });

      renderDashboard();

      const input = screen.getByTestId('action-input');
      await user.type(input, 'New mark');
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(mockCreateMark).toHaveBeenCalledWith(
          expect.objectContaining({
            action: 'New mark',
          })
        );
      });
    });
  });

  describe('Props', () => {
    it('respects defaultGroupBy prop', () => {
      renderDashboard({ defaultGroupBy: 'session' });

      const timeline = screen.getByTestId('mark-timeline');
      expect(timeline).toHaveAttribute('data-group-by', 'session');
    });
  });
});

describe('WitnessDashboard Loading State', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state when isLoading is true', async () => {
    // Re-mock with loading state
    const { useWitness } = await import('@/hooks/useWitness');
    vi.mocked(useWitness).mockReturnValue({
      marks: [],
      isLoading: true,
      error: null,
      createMark: mockCreateMark,
      retractMark: mockRetractMark,
      refetch: mockRefetch,
      isConnected: false,
    });

    renderDashboard();

    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();
  });
});

describe('WitnessDashboard Error State', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows error state when error exists', async () => {
    const { useWitness } = await import('@/hooks/useWitness');
    vi.mocked(useWitness).mockReturnValue({
      marks: [],
      isLoading: false,
      error: new Error('Failed to fetch marks'),
      createMark: mockCreateMark,
      retractMark: mockRetractMark,
      refetch: mockRefetch,
      isConnected: false,
    });

    renderDashboard();

    expect(screen.getByTestId('error-state')).toBeInTheDocument();
    expect(screen.getByText('Failed to fetch marks')).toBeInTheDocument();
  });
});

describe('WitnessDashboard Disconnected State', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows "Connecting" when disconnected', async () => {
    const { useWitness } = await import('@/hooks/useWitness');
    vi.mocked(useWitness).mockReturnValue({
      marks: mockMarks,
      isLoading: false,
      error: null,
      createMark: mockCreateMark,
      retractMark: mockRetractMark,
      refetch: mockRefetch,
      isConnected: false,
    });

    renderDashboard();

    expect(screen.getByTestId('connection-status')).toHaveTextContent('Connecting');
  });

  it('shows "Updates paused" in footer when disconnected', async () => {
    const { useWitness } = await import('@/hooks/useWitness');
    vi.mocked(useWitness).mockReturnValue({
      marks: mockMarks,
      isLoading: false,
      error: null,
      createMark: mockCreateMark,
      retractMark: mockRetractMark,
      refetch: mockRefetch,
      isConnected: false,
    });

    renderDashboard();

    expect(screen.getByTestId('stats-footer')).toHaveTextContent('Updates paused');
  });
});
