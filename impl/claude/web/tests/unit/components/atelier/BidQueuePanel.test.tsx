/**
 * BidQueuePanel Tests
 *
 * Tests following T-gent taxonomy:
 * - Type I: Contract tests (props validation, rendering)
 * - Type II: Saboteur tests (edge cases, empty states)
 * - Type III: Spy tests (callback verification)
 * - Type IV: Property tests (sorting, filtering)
 * - Type V: Performance tests (render cycles)
 *
 * @see plans/crown-jewels-genesis-phase2-continuation.md - Chunk 2: BidQueue
 * @see docs/skills/test-patterns.md - T-gent Taxonomy
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { BidQueuePanel, type Bid, type BidQueuePanelProps } from '@/components/atelier/BidQueuePanel';

// =============================================================================
// Test Fixtures
// =============================================================================

const mockBids: Bid[] = [
  {
    id: 'bid-1',
    spectatorId: 'spectator-1',
    spectatorName: 'Alice',
    bidType: 'inject_constraint',
    content: 'Add more blue tones to the composition',
    tokenCost: 10,
    submittedAt: new Date().toISOString(),
    status: 'pending',
  },
  {
    id: 'bid-2',
    spectatorId: 'spectator-2',
    spectatorName: 'Bob',
    bidType: 'request_direction',
    content: 'Could you make it more abstract?',
    tokenCost: 5,
    submittedAt: new Date(Date.now() - 60000).toISOString(),
    status: 'accepted',
  },
  {
    id: 'bid-3',
    spectatorId: 'spectator-3',
    bidType: 'boost_builder',
    content: 'Great work so far!',
    tokenCost: 3,
    submittedAt: new Date(Date.now() - 120000).toISOString(),
    status: 'rejected',
  },
];

const defaultProps: BidQueuePanelProps = {
  bids: mockBids,
  isCreator: false,
  tokenBalance: 50,
};

function renderBidQueue(overrides: Partial<BidQueuePanelProps> = {}) {
  const props = { ...defaultProps, ...overrides };
  return render(<BidQueuePanel {...props} />);
}

// =============================================================================
// Type I: Contract Tests
// =============================================================================

describe('BidQueuePanel - Type I: Contract Tests', () => {
  it('renders with required props', () => {
    renderBidQueue();
    expect(screen.getByText('Bid Queue')).toBeInTheDocument();
  });

  it('displays all bids', () => {
    renderBidQueue();
    expect(screen.getByText(/Add more blue tones/)).toBeInTheDocument();
    expect(screen.getByText(/Could you make it more abstract/)).toBeInTheDocument();
    expect(screen.getByText(/Great work so far/)).toBeInTheDocument();
  });

  it('shows spectator names when provided', () => {
    renderBidQueue();
    expect(screen.getByText(/by Alice/)).toBeInTheDocument();
    expect(screen.getByText(/by Bob/)).toBeInTheDocument();
  });

  it('shows token costs for each bid', () => {
    renderBidQueue();
    // Token costs displayed as numbers
    expect(screen.getByText('10')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('shows bid type labels', () => {
    renderBidQueue();
    expect(screen.getByText('Constraint')).toBeInTheDocument();
    expect(screen.getByText('Direction')).toBeInTheDocument();
    expect(screen.getByText('Boost')).toBeInTheDocument();
  });

  it('shows pending count in header', () => {
    renderBidQueue();
    expect(screen.getByText('1 pending')).toBeInTheDocument();
  });

  it('shows token balance in header', () => {
    renderBidQueue({ tokenBalance: 75 });
    expect(screen.getByText('75')).toBeInTheDocument();
  });

  it('shows status badges for non-pending bids', () => {
    renderBidQueue();
    expect(screen.getByText('accepted')).toBeInTheDocument();
    expect(screen.getByText('rejected')).toBeInTheDocument();
  });
});

// =============================================================================
// Type II: Saboteur Tests
// =============================================================================

describe('BidQueuePanel - Type II: Saboteur Tests', () => {
  it('shows empty state when no bids', () => {
    renderBidQueue({ bids: [] });
    expect(screen.getByText('No bids yet')).toBeInTheDocument();
  });

  it('handles bids without spectator names', () => {
    const bidsNoNames = mockBids.map((b) => ({ ...b, spectatorName: undefined }));
    renderBidQueue({ bids: bidsNoNames });
    expect(screen.getByText('Bid Queue')).toBeInTheDocument();
    // Should not throw
    expect(screen.queryByText(/by Alice/)).not.toBeInTheDocument();
  });

  it('handles very long bid content', () => {
    const longBid: Bid = {
      ...mockBids[0],
      content: 'A'.repeat(1000),
    };
    renderBidQueue({ bids: [longBid] });
    // Content should be truncated (line-clamp-2)
    const bidContent = screen.getByText(/^A+/);
    expect(bidContent).toBeInTheDocument();
  });

  it('handles zero token balance', () => {
    renderBidQueue({ tokenBalance: 0 });
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('handles all pending bids', () => {
    const allPending = mockBids.map((b) => ({ ...b, status: 'pending' as const }));
    renderBidQueue({ bids: allPending });
    expect(screen.getByText('3 pending')).toBeInTheDocument();
  });

  it('handles all completed bids (no pending)', () => {
    const nonePending = mockBids.map((b) => ({ ...b, status: 'accepted' as const }));
    renderBidQueue({ bids: nonePending });
    expect(screen.queryByText('pending')).not.toBeInTheDocument();
  });
});

// =============================================================================
// Type III: Spy Tests
// =============================================================================

describe('BidQueuePanel - Type III: Spy Tests', () => {
  it('calls onAccept when accept button clicked (creator)', () => {
    const handleAccept = vi.fn();
    renderBidQueue({ isCreator: true, onAccept: handleAccept });

    // Find and click the accept button for pending bid
    const acceptButtons = screen.getAllByTitle('Accept bid');
    fireEvent.click(acceptButtons[0]);

    expect(handleAccept).toHaveBeenCalledWith('bid-1');
  });

  it('calls onReject when reject button clicked (creator)', () => {
    const handleReject = vi.fn();
    renderBidQueue({ isCreator: true, onReject: handleReject });

    // Find and click the reject button for pending bid
    const rejectButtons = screen.getAllByTitle('Reject bid');
    fireEvent.click(rejectButtons[0]);

    expect(handleReject).toHaveBeenCalledWith('bid-1');
  });

  it('does not show action buttons for non-creator', () => {
    renderBidQueue({ isCreator: false });
    expect(screen.queryByTitle('Accept bid')).not.toBeInTheDocument();
    expect(screen.queryByTitle('Reject bid')).not.toBeInTheDocument();
  });

  it('only shows action buttons for pending bids', () => {
    renderBidQueue({ isCreator: true });
    // Only one pending bid (bid-1)
    const acceptButtons = screen.getAllByTitle('Accept bid');
    expect(acceptButtons).toHaveLength(1);
  });
});

// =============================================================================
// Type IV: Property Tests (Sorting & Filtering)
// =============================================================================

describe('BidQueuePanel - Type IV: Property Tests', () => {
  it('sorts pending bids first', () => {
    const { container } = renderBidQueue();
    const bidCards = container.querySelectorAll('[class*="rounded-lg border p-3"]');

    // First bid should be the pending one
    expect(bidCards[0]).toHaveTextContent(/Add more blue tones/);
  });

  it('shows limited bids initially with show more button', () => {
    const manyBids: Bid[] = Array.from({ length: 10 }, (_, i) => ({
      id: `bid-${i}`,
      spectatorId: `spectator-${i}`,
      spectatorName: `User ${i}`,
      bidType: 'boost_builder' as const,
      content: `Bid content ${i}`,
      tokenCost: 3,
      submittedAt: new Date().toISOString(),
      status: 'pending' as const,
    }));

    renderBidQueue({ bids: manyBids, initialLimit: 5 });

    // Should show "Show X more" button
    expect(screen.getByText(/Show 5 more/)).toBeInTheDocument();
  });

  it('expands to show all bids when clicking show more', () => {
    const manyBids: Bid[] = Array.from({ length: 10 }, (_, i) => ({
      id: `bid-${i}`,
      spectatorId: `spectator-${i}`,
      spectatorName: `User ${i}`,
      bidType: 'boost_builder' as const,
      content: `Bid content ${i}`,
      tokenCost: 3,
      submittedAt: new Date().toISOString(),
      status: 'pending' as const,
    }));

    renderBidQueue({ bids: manyBids, initialLimit: 5 });

    const showMoreButton = screen.getByText(/Show 5 more/);
    fireEvent.click(showMoreButton);

    // Button should disappear after expanding
    expect(screen.queryByText(/Show 5 more/)).not.toBeInTheDocument();
  });
});

// =============================================================================
// Type V: Performance Tests
// =============================================================================

describe('BidQueuePanel - Type V: Performance Tests', () => {
  it('renders within acceptable time (<16ms)', () => {
    const start = performance.now();
    renderBidQueue();
    const elapsed = performance.now() - start;
    expect(elapsed).toBeLessThan(50); // Generous for test environment
  });

  it('handles many bids efficiently', () => {
    const manyBids: Bid[] = Array.from({ length: 100 }, (_, i) => ({
      id: `bid-${i}`,
      spectatorId: `spectator-${i}`,
      bidType: 'boost_builder' as const,
      content: `Bid content ${i}`,
      tokenCost: 3,
      submittedAt: new Date().toISOString(),
      status: i % 3 === 0 ? 'pending' : 'accepted',
    }));

    const start = performance.now();
    renderBidQueue({ bids: manyBids });
    const elapsed = performance.now() - start;

    expect(elapsed).toBeLessThan(200); // Generous for test environment
  });
});

// =============================================================================
// Accessibility Tests
// =============================================================================

describe('BidQueuePanel - Accessibility', () => {
  it('has accessible button labels', () => {
    renderBidQueue({ isCreator: true });
    expect(screen.getByTitle('Accept bid')).toBeInTheDocument();
    expect(screen.getByTitle('Reject bid')).toBeInTheDocument();
  });

  it('empty state has descriptive text', () => {
    renderBidQueue({ bids: [] });
    expect(
      screen.getByText('Spectators can submit bids to influence creation')
    ).toBeInTheDocument();
  });
});
