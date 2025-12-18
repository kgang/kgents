/**
 * BidSubmitModal Tests
 *
 * Tests following T-gent taxonomy:
 * - Type I: Contract tests (props validation, rendering)
 * - Type II: Saboteur tests (validation, edge cases)
 * - Type III: Spy tests (callback verification, form submission)
 *
 * @see plans/crown-jewels-genesis-phase2-continuation.md - Chunk 2: BidQueue
 * @see docs/skills/test-patterns.md - T-gent Taxonomy
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { BidSubmitModal, type BidSubmitModalProps } from '@/components/atelier/BidSubmitModal';

// =============================================================================
// Test Fixtures
// =============================================================================

const defaultProps: BidSubmitModalProps = {
  isOpen: true,
  onClose: vi.fn(),
  onSubmit: vi.fn().mockResolvedValue(undefined),
  tokenBalance: 50,
};

function renderModal(overrides: Partial<BidSubmitModalProps> = {}) {
  const props = { ...defaultProps, ...overrides };
  return render(<BidSubmitModal {...props} />);
}

// =============================================================================
// Type I: Contract Tests
// =============================================================================

describe('BidSubmitModal - Type I: Contract Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders when isOpen is true', () => {
    renderModal();
    expect(screen.getByText('Submit Bid')).toBeInTheDocument();
  });

  it('does not render when isOpen is false', () => {
    renderModal({ isOpen: false });
    expect(screen.queryByText('Submit Bid')).not.toBeInTheDocument();
  });

  it('shows token balance', () => {
    renderModal({ tokenBalance: 75 });
    expect(screen.getByText('75')).toBeInTheDocument();
  });

  it('shows all bid type options', () => {
    renderModal();
    expect(screen.getByText('Inject Constraint')).toBeInTheDocument();
    expect(screen.getByText('Request Direction')).toBeInTheDocument();
    expect(screen.getByText('Boost Builder')).toBeInTheDocument();
  });

  it('shows bid type costs', () => {
    renderModal();
    // Costs should be displayed
    expect(screen.getByText('10')).toBeInTheDocument(); // inject_constraint
    expect(screen.getByText('5')).toBeInTheDocument(); // request_direction
    expect(screen.getByText('3')).toBeInTheDocument(); // boost_builder
  });

  it('shows bid type descriptions', () => {
    renderModal();
    expect(
      screen.getByText('Add a creative constraint the artisan must follow')
    ).toBeInTheDocument();
    expect(
      screen.getByText('Suggest a direction for the creation')
    ).toBeInTheDocument();
    expect(
      screen.getByText('Show appreciation and encourage the artisan')
    ).toBeInTheDocument();
  });

  it('has cancel and submit buttons', () => {
    renderModal();
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
  });

  it('shows character count for textarea', () => {
    renderModal();
    expect(screen.getByText('0/500')).toBeInTheDocument();
  });
});

// =============================================================================
// Type II: Saboteur Tests (Validation)
// =============================================================================

describe('BidSubmitModal - Type II: Saboteur Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('disables submit when content is too short', () => {
    renderModal();
    const textarea = screen.getByPlaceholderText(/could you explore/i);
    fireEvent.change(textarea, { target: { value: 'Hi' } }); // 2 chars, min is 3

    const submitButton = screen.getByRole('button', { name: /submit/i });
    expect(submitButton).toBeDisabled();
  });

  it('shows insufficient balance warning', () => {
    renderModal({ tokenBalance: 2 });
    // With only 2 tokens, none of the bids are affordable (min is 3)
    expect(screen.getByText(/insufficient tokens/i)).toBeInTheDocument();
  });

  it('disables bid types user cannot afford', () => {
    renderModal({ tokenBalance: 4 });
    // Can afford boost_builder (3) but not others

    // The inject_constraint button should be disabled/styled differently
    const constraintOption = screen.getByText('Inject Constraint').closest('button');
    expect(constraintOption).toHaveClass('cursor-not-allowed');
  });

  it('updates character count as user types', () => {
    renderModal();
    const textarea = screen.getByPlaceholderText(/could you explore/i);
    fireEvent.change(textarea, { target: { value: 'Hello world' } });

    expect(screen.getByText('11/500')).toBeInTheDocument();
  });

  it('shows error for content exceeding max length', () => {
    renderModal();
    const textarea = screen.getByPlaceholderText(/could you explore/i);
    const longContent = 'A'.repeat(501);
    fireEvent.change(textarea, { target: { value: longContent } });

    // Character count should show red styling (over limit)
    expect(screen.getByText('501/500')).toBeInTheDocument();
  });
});

// =============================================================================
// Type III: Spy Tests (Callbacks)
// =============================================================================

describe('BidSubmitModal - Type III: Spy Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('calls onClose when cancel is clicked', () => {
    const onClose = vi.fn();
    renderModal({ onClose });

    fireEvent.click(screen.getByRole('button', { name: /cancel/i }));
    expect(onClose).toHaveBeenCalled();
  });

  it('calls onClose when clicking outside modal', () => {
    const onClose = vi.fn();
    renderModal({ onClose });

    // Click the backdrop (the outer div with bg-black/50)
    const backdrop = screen.getByText('Submit Bid').closest('.fixed');
    if (backdrop) {
      fireEvent.click(backdrop);
    }
    expect(onClose).toHaveBeenCalled();
  });

  it('calls onClose when clicking X button', () => {
    const onClose = vi.fn();
    renderModal({ onClose });

    // Find and click the X button in the header
    const buttons = screen.getAllByRole('button');
    const closeButton = buttons.find((btn) =>
      btn.querySelector('svg.lucide-x')
    );
    if (closeButton) {
      fireEvent.click(closeButton);
    }
    expect(onClose).toHaveBeenCalled();
  });

  it('calls onSubmit with correct bid data', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    renderModal({ onSubmit });

    // Select a bid type (direction is default, select boost)
    const boostOption = screen.getByText('Boost Builder').closest('button');
    if (boostOption) {
      fireEvent.click(boostOption);
    }

    // Enter content
    const textarea = screen.getByPlaceholderText(/love the direction/i);
    fireEvent.change(textarea, { target: { value: 'Amazing work!' } });

    // Submit
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        bidType: 'boost_builder',
        content: 'Amazing work!',
      });
    });
  });

  it('shows loading state during submission', async () => {
    const onSubmit = vi.fn().mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );
    renderModal({ onSubmit });

    // Enter valid content
    const textarea = screen.getByPlaceholderText(/could you explore/i);
    fireEvent.change(textarea, { target: { value: 'Please explore more colors' } });

    // Submit
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    // Should show "Submitting..."
    expect(screen.getByText('Submitting...')).toBeInTheDocument();
  });

  it('shows error message when submission fails', async () => {
    const onSubmit = vi.fn().mockRejectedValue(new Error('Network error'));
    renderModal({ onSubmit });

    // Enter valid content
    const textarea = screen.getByPlaceholderText(/could you explore/i);
    fireEvent.change(textarea, { target: { value: 'Please explore more colors' } });

    // Submit
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('closes modal on successful submission', async () => {
    const onClose = vi.fn();
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    renderModal({ onClose, onSubmit });

    // Enter valid content
    const textarea = screen.getByPlaceholderText(/could you explore/i);
    fireEvent.change(textarea, { target: { value: 'Please explore more colors' } });

    // Submit
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(onClose).toHaveBeenCalled();
    });
  });

  it('resets form after successful submission', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const { rerender } = renderModal({ onSubmit });

    // Enter content
    const textarea = screen.getByPlaceholderText(/could you explore/i);
    fireEvent.change(textarea, { target: { value: 'Some content here' } });

    // Submit
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalled();
    });

    // Reopen modal to check if form is reset
    rerender(
      <BidSubmitModal
        {...defaultProps}
        onSubmit={onSubmit}
        isOpen={true}
      />
    );

    // Content should be reset (checking character count)
    expect(screen.getByText('0/500')).toBeInTheDocument();
  });
});

// =============================================================================
// Bid Type Selection Tests
// =============================================================================

describe('BidSubmitModal - Bid Type Selection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('defaults to request_direction', () => {
    renderModal();
    const directionOption = screen.getByText('Request Direction').closest('button');
    expect(directionOption).toHaveClass('border-amber-300'); // Selected style
  });

  it('allows selecting different bid types', () => {
    renderModal();

    // Click on inject_constraint
    const constraintOption = screen.getByText('Inject Constraint').closest('button');
    if (constraintOption) {
      fireEvent.click(constraintOption);
    }

    // Should now be selected
    expect(constraintOption).toHaveClass('border-amber-300');
  });

  it('updates submit button cost when type changes', () => {
    renderModal();

    // Default is request_direction (5 tokens)
    expect(screen.getByRole('button', { name: /submit.*5 tokens/i })).toBeInTheDocument();

    // Select boost_builder (3 tokens)
    const boostOption = screen.getByText('Boost Builder').closest('button');
    if (boostOption) {
      fireEvent.click(boostOption);
    }

    expect(screen.getByRole('button', { name: /submit.*3 tokens/i })).toBeInTheDocument();
  });

  it('updates placeholder text when type changes', () => {
    renderModal();

    // Default placeholder for request_direction
    expect(screen.getByPlaceholderText(/could you explore/i)).toBeInTheDocument();

    // Select inject_constraint
    const constraintOption = screen.getByText('Inject Constraint').closest('button');
    if (constraintOption) {
      fireEvent.click(constraintOption);
    }

    // Placeholder should change
    expect(screen.getByPlaceholderText(/include a reference/i)).toBeInTheDocument();
  });
});
