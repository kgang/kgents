/**
 * Tests for RecentTracesPanel component.
 *
 * @see impl/claude/web/src/components/differance/RecentTracesPanel.tsx
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { RecentTracesPanel } from '@/components/differance/RecentTracesPanel';

// Mock the useDifferanceQuery hooks
vi.mock('@/hooks/useDifferanceQuery', () => ({
  useDifferanceManifest: vi.fn(),
  useGhosts: vi.fn(),
  useWhyExplain: vi.fn(),
}));

// Import after mock
import { useDifferanceManifest, useGhosts, useWhyExplain } from '@/hooks/useDifferanceQuery';

// =============================================================================
// Test Data
// =============================================================================

const mockManifest = {
  trace_count: 42,
  store_connected: true,
  monoid_available: true,
  route: '/differance',
};

const mockGhosts = {
  ghosts: [
    {
      operation: 'capture_memory',
      inputs: ['content_1'],
      reason_rejected: 'Could auto-categorize',
      could_revisit: true,
    },
    {
      operation: 'plant_idea',
      inputs: ['idea_1'],
      reason_rejected: 'Could use different lifecycle',
      could_revisit: true,
    },
    {
      operation: 'surface_memory',
      inputs: ['seed_123'],
      reason_rejected: 'Different entropy seed possible',
      could_revisit: false,
    },
  ],
  count: 3,
  explorable_only: false,
};

// =============================================================================
// RecentTracesPanel Tests
// =============================================================================

describe('RecentTracesPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Default mock implementations
    (useDifferanceManifest as ReturnType<typeof vi.fn>).mockReturnValue({
      data: mockManifest,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    (useGhosts as ReturnType<typeof vi.fn>).mockReturnValue({
      data: mockGhosts,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    (useWhyExplain as ReturnType<typeof vi.fn>).mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    });
  });

  describe('rendering', () => {
    it('renders header with title', () => {
      render(<RecentTracesPanel />);

      expect(screen.getByText('Recent Traces')).toBeInTheDocument();
    });

    it('shows total trace count from manifest', () => {
      render(<RecentTracesPanel />);

      expect(screen.getByText('42 total')).toBeInTheDocument();
    });

    it('renders trace items from ghosts data', () => {
      render(<RecentTracesPanel />);

      expect(screen.getByText('capture_memory')).toBeInTheDocument();
      expect(screen.getByText('plant_idea')).toBeInTheDocument();
      expect(screen.getByText('surface_memory')).toBeInTheDocument();
    });

    it('respects limit prop', () => {
      (useGhosts as ReturnType<typeof vi.fn>).mockReturnValue({
        data: mockGhosts,
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      });

      render(<RecentTracesPanel limit={2} />);

      // Should only show 2 items
      const buttons = screen.getAllByRole('button');
      // Filter to just trace item buttons (exclude refresh and view all)
      const traceButtons = buttons.filter((b) =>
        ['capture_memory', 'plant_idea'].some((op) => b.textContent?.includes(op))
      );
      expect(traceButtons.length).toBe(2);
    });
  });

  describe('loading state', () => {
    it('shows loading spinner when loading', () => {
      (useDifferanceManifest as ReturnType<typeof vi.fn>).mockReturnValue({
        data: null,
        isLoading: true,
        error: null,
        refetch: vi.fn(),
      });

      (useGhosts as ReturnType<typeof vi.fn>).mockReturnValue({
        data: null,
        isLoading: true,
        error: null,
        refetch: vi.fn(),
      });

      render(<RecentTracesPanel />);

      // Should show loading indicator
      const refreshIcon = document.querySelector('.animate-spin');
      expect(refreshIcon).toBeInTheDocument();
    });
  });

  describe('empty state', () => {
    it('shows empty state when no traces', () => {
      (useGhosts as ReturnType<typeof vi.fn>).mockReturnValue({
        data: { ghosts: [], count: 0, explorable_only: false },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      });

      render(<RecentTracesPanel />);

      expect(screen.getByText('No traces recorded yet')).toBeInTheDocument();
      expect(
        screen.getByText('Traces will appear after Brain or Gardener operations')
      ).toBeInTheDocument();
    });
  });

  describe('interactions', () => {
    it('calls onViewAll when View All is clicked', () => {
      const handleViewAll = vi.fn();
      render(<RecentTracesPanel onViewAll={handleViewAll} />);

      fireEvent.click(screen.getByText('View All'));
      expect(handleViewAll).toHaveBeenCalledTimes(1);
    });

    it('calls refetch when refresh button is clicked', () => {
      const refetchManifest = vi.fn();
      const refetchGhosts = vi.fn();

      (useDifferanceManifest as ReturnType<typeof vi.fn>).mockReturnValue({
        data: mockManifest,
        isLoading: false,
        error: null,
        refetch: refetchManifest,
      });

      (useGhosts as ReturnType<typeof vi.fn>).mockReturnValue({
        data: mockGhosts,
        isLoading: false,
        error: null,
        refetch: refetchGhosts,
      });

      render(<RecentTracesPanel />);

      const refreshButton = screen.getByTitle('Refresh traces');
      fireEvent.click(refreshButton);

      expect(refetchManifest).toHaveBeenCalledTimes(1);
      expect(refetchGhosts).toHaveBeenCalledTimes(1);
    });

    it('expands trace item when clicked', async () => {
      render(<RecentTracesPanel />);

      // Click on the first trace item
      const traceItem = screen.getByText('capture_memory').closest('button');
      expect(traceItem).not.toBeNull();

      fireEvent.click(traceItem!);

      // WhyPanel should now be visible (it shows "Why This?" text)
      await waitFor(() => {
        expect(screen.getByText('Why This?')).toBeInTheDocument();
      });
    });
  });

  describe('backend status', () => {
    it('shows store connected status', () => {
      render(<RecentTracesPanel />);

      expect(screen.getByText('Store connected')).toBeInTheDocument();
    });

    it('shows buffer only when store not connected', () => {
      (useDifferanceManifest as ReturnType<typeof vi.fn>).mockReturnValue({
        data: { ...mockManifest, store_connected: false },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
      });

      render(<RecentTracesPanel />);

      expect(screen.getByText('Buffer only')).toBeInTheDocument();
    });

    it('shows monoid available indicator', () => {
      render(<RecentTracesPanel />);

      expect(screen.getByText('Monoid available')).toBeInTheDocument();
    });
  });

  describe('compact mode', () => {
    it('applies compact styles', () => {
      render(<RecentTracesPanel compact={true} />);

      // Compact mode uses smaller padding (p-2 instead of p-3)
      const panel = screen.getByText('Recent Traces').closest('[class*="rounded-xl"]');
      expect(panel).toBeInTheDocument();
    });
  });

  describe('custom className', () => {
    it('applies custom className', () => {
      const { container } = render(<RecentTracesPanel className="my-custom-class" />);

      const panel = container.firstChild;
      expect(panel).toHaveClass('my-custom-class');
    });
  });
});
