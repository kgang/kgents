/**
 * Tests for WhyPanel component.
 *
 * @see impl/claude/web/src/components/differance/WhyPanel.tsx
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { WhyPanel } from '@/components/differance/WhyPanel';

// Mock the useDifferanceQuery hook
vi.mock('@/hooks/useDifferanceQuery', () => ({
  useWhyExplain: vi.fn(),
}));

// Import after mock
import { useWhyExplain } from '@/hooks/useDifferanceQuery';

// =============================================================================
// Test Data
// =============================================================================

const mockWhyResponse = {
  output_id: 'crystal_123',
  lineage_length: 3,
  decisions_made: 3,
  alternatives_considered: 5,
  summary: 'Output resulted from 3 decisions, starting with capture and ending with store.',
  chosen_path: [
    {
      id: 'trace_001',
      operation: 'capture',
      inputs: ['content'],
      output: 'crystal_123',
      ghosts: [
        { operation: 'auto_tag', reason: 'Could auto-categorize', explorable: true },
        { operation: 'defer', reason: 'Could defer embedding', explorable: false },
      ],
    },
    {
      id: 'trace_002',
      operation: 'embed',
      inputs: ['crystal_123'],
      output: 'embedding_456',
      ghosts: [],
    },
    {
      id: 'trace_003',
      operation: 'store',
      inputs: ['embedding_456'],
      output: 'stored',
      ghosts: [{ operation: 'cache', reason: 'Could cache only', explorable: true }],
    },
  ],
};

// =============================================================================
// WhyPanel Tests
// =============================================================================

describe('WhyPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('collapsed state', () => {
    it('renders collapsed by default', () => {
      (useWhyExplain as ReturnType<typeof vi.fn>).mockReturnValue({
        data: null,
        isLoading: false,
        error: null,
      });

      render(<WhyPanel outputId="crystal_123" />);

      expect(screen.getByText('Why This?')).toBeInTheDocument();
      // Content should not be visible when collapsed
      expect(screen.queryByText(/Output resulted from/)).not.toBeInTheDocument();
    });

    it('expands when header is clicked', async () => {
      (useWhyExplain as ReturnType<typeof vi.fn>).mockReturnValue({
        data: mockWhyResponse,
        isLoading: false,
        error: null,
      });

      render(<WhyPanel outputId="crystal_123" />);

      fireEvent.click(screen.getByText('Why This?'));

      await waitFor(() => {
        expect(screen.getByText(mockWhyResponse.summary!)).toBeInTheDocument();
      });
    });

    it('renders expanded when defaultExpanded is true', () => {
      (useWhyExplain as ReturnType<typeof vi.fn>).mockReturnValue({
        data: mockWhyResponse,
        isLoading: false,
        error: null,
      });

      render(<WhyPanel outputId="crystal_123" defaultExpanded={true} />);

      expect(screen.getByText(mockWhyResponse.summary!)).toBeInTheDocument();
    });
  });

  describe('loading state', () => {
    it('shows loading indicator while fetching', async () => {
      (useWhyExplain as ReturnType<typeof vi.fn>).mockReturnValue({
        data: null,
        isLoading: true,
        error: null,
      });

      render(<WhyPanel outputId="crystal_123" defaultExpanded={true} />);

      expect(screen.getByText('Tracing lineage...')).toBeInTheDocument();
    });
  });

  describe('error state', () => {
    it('shows error message when fetch fails', async () => {
      (useWhyExplain as ReturnType<typeof vi.fn>).mockReturnValue({
        data: null,
        isLoading: false,
        error: new Error('Network error'),
      });

      render(<WhyPanel outputId="crystal_123" defaultExpanded={true} />);

      expect(screen.getByText(/Could not trace lineage/)).toBeInTheDocument();
      expect(screen.getByText(/Network error/)).toBeInTheDocument();
    });
  });

  describe('data display', () => {
    it('displays summary when available', () => {
      (useWhyExplain as ReturnType<typeof vi.fn>).mockReturnValue({
        data: mockWhyResponse,
        isLoading: false,
        error: null,
      });

      render(<WhyPanel outputId="crystal_123" defaultExpanded={true} />);

      expect(screen.getByText(mockWhyResponse.summary!)).toBeInTheDocument();
    });

    it('displays chosen path steps', () => {
      (useWhyExplain as ReturnType<typeof vi.fn>).mockReturnValue({
        data: mockWhyResponse,
        isLoading: false,
        error: null,
      });

      render(<WhyPanel outputId="crystal_123" defaultExpanded={true} />);

      expect(screen.getByText('capture')).toBeInTheDocument();
      expect(screen.getByText('embed')).toBeInTheDocument();
      expect(screen.getByText('store')).toBeInTheDocument();
    });

    it('shows ghost count badge on steps with ghosts', () => {
      (useWhyExplain as ReturnType<typeof vi.fn>).mockReturnValue({
        data: mockWhyResponse,
        isLoading: false,
        error: null,
      });

      render(<WhyPanel outputId="crystal_123" defaultExpanded={true} />);

      // capture has 2 ghosts, store has 1 ghost
      const ghostButtons = screen.getAllByRole('button', { name: /2|1/ });
      expect(ghostButtons.length).toBeGreaterThanOrEqual(1);
    });

    it('shows empty state when no lineage', () => {
      (useWhyExplain as ReturnType<typeof vi.fn>).mockReturnValue({
        data: {
          output_id: 'crystal_123',
          lineage_length: 0,
          decisions_made: 0,
          alternatives_considered: 0,
          chosen_path: [],
        },
        isLoading: false,
        error: null,
      });

      render(<WhyPanel outputId="crystal_123" defaultExpanded={true} />);

      expect(screen.getByText('No lineage recorded for this output.')).toBeInTheDocument();
    });
  });

  describe('explore heritage callback', () => {
    it('shows explore link when callback provided', () => {
      const handleExplore = vi.fn();
      (useWhyExplain as ReturnType<typeof vi.fn>).mockReturnValue({
        data: mockWhyResponse,
        isLoading: false,
        error: null,
      });

      render(
        <WhyPanel outputId="crystal_123" defaultExpanded={true} onExploreHeritage={handleExplore} />
      );

      expect(screen.getByText('Explore full heritage graph')).toBeInTheDocument();
    });

    it('calls onExploreHeritage when link is clicked', () => {
      const handleExplore = vi.fn();
      (useWhyExplain as ReturnType<typeof vi.fn>).mockReturnValue({
        data: mockWhyResponse,
        isLoading: false,
        error: null,
      });

      render(
        <WhyPanel outputId="crystal_123" defaultExpanded={true} onExploreHeritage={handleExplore} />
      );

      fireEvent.click(screen.getByText('Explore full heritage graph'));
      expect(handleExplore).toHaveBeenCalledWith('crystal_123');
    });
  });

  describe('compact mode', () => {
    it('applies compact styles', () => {
      (useWhyExplain as ReturnType<typeof vi.fn>).mockReturnValue({
        data: mockWhyResponse,
        isLoading: false,
        error: null,
      });

      render(<WhyPanel outputId="crystal_123" defaultExpanded={true} compact={true} />);

      // Compact mode should use smaller font sizes
      const summary = screen.getByText(mockWhyResponse.summary!);
      expect(summary.className).toContain('text-xs');
    });
  });
});
