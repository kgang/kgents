/**
 * Tests for TeachingCallout component.
 *
 * Following T-gent Types taxonomy:
 * - Type I (Contracts): Preconditions, postconditions, rendering contracts
 * - Type II (Saboteurs): Edge cases, invalid inputs, boundary conditions
 * - Type III (Spies): Callback verification, event handling
 *
 * @see impl/claude/web/src/components/categorical/TeachingCallout.tsx
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  TeachingCallout,
  getTeachingMessage,
  TEACHING_MESSAGES,
} from '@/components/categorical/TeachingCallout';

// =============================================================================
// Type I Tests: Contracts - Basic Rendering
// =============================================================================

describe('TeachingCallout - Contracts', () => {
  it('renders children content', () => {
    render(<TeachingCallout>Test content</TeachingCallout>);
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('renders default category (insight)', () => {
    render(<TeachingCallout>Content</TeachingCallout>);
    expect(screen.getByText('Insight')).toBeInTheDocument();
  });

  it('renders categorical category', () => {
    render(<TeachingCallout category="categorical">Content</TeachingCallout>);
    expect(screen.getByText('Categorical')).toBeInTheDocument();
  });

  it('renders operational category', () => {
    render(<TeachingCallout category="operational">Content</TeachingCallout>);
    expect(screen.getByText('Operation')).toBeInTheDocument();
  });

  it('renders conceptual category', () => {
    render(<TeachingCallout category="conceptual">Content</TeachingCallout>);
    expect(screen.getByText('Concept')).toBeInTheDocument();
  });

  it('renders custom title override', () => {
    render(<TeachingCallout title="Custom Title">Content</TeachingCallout>);
    expect(screen.getByText('Custom Title')).toBeInTheDocument();
  });

  it('has note role for accessibility', () => {
    render(<TeachingCallout>Content</TeachingCallout>);
    expect(screen.getByRole('note')).toBeInTheDocument();
  });

  it('has descriptive aria-label', () => {
    render(<TeachingCallout category="categorical">Content</TeachingCallout>);
    const note = screen.getByRole('note');
    expect(note).toHaveAttribute('aria-label', 'Categorical teaching callout');
  });

  it('renders icon based on category', () => {
    const { container } = render(<TeachingCallout category="categorical">Content</TeachingCallout>);
    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('icon is hidden from screen readers', () => {
    const { container } = render(<TeachingCallout>Content</TeachingCallout>);
    const icon = container.querySelector('svg');
    expect(icon).toHaveAttribute('aria-hidden', 'true');
  });
});

// =============================================================================
// Type I Tests: Category Gradients
// =============================================================================

describe('TeachingCallout - Category Gradients', () => {
  it('applies categorical gradient (blue-purple)', () => {
    const { container } = render(<TeachingCallout category="categorical">Content</TeachingCallout>);
    const callout = container.querySelector('[role="note"]');
    expect(callout).toHaveClass('bg-gradient-to-r');
    expect(callout).toHaveClass('from-blue-500/20');
    expect(callout).toHaveClass('to-purple-500/20');
  });

  it('applies operational gradient (amber-pink)', () => {
    const { container } = render(<TeachingCallout category="operational">Content</TeachingCallout>);
    const callout = container.querySelector('[role="note"]');
    expect(callout).toHaveClass('bg-gradient-to-r');
    expect(callout).toHaveClass('from-amber-500/20');
    expect(callout).toHaveClass('to-pink-500/20');
  });

  it('applies conceptual gradient (green-blue)', () => {
    const { container } = render(<TeachingCallout category="conceptual">Content</TeachingCallout>);
    const callout = container.querySelector('[role="note"]');
    expect(callout).toHaveClass('bg-gradient-to-r');
    expect(callout).toHaveClass('from-green-500/20');
    expect(callout).toHaveClass('to-blue-500/20');
  });

  it('applies insight gradient (cyan-indigo)', () => {
    const { container } = render(<TeachingCallout category="insight">Content</TeachingCallout>);
    const callout = container.querySelector('.from-cyan-500\\/20.to-indigo-500\\/20');
    expect(callout).toBeInTheDocument();
  });

  it('applies categorical border color', () => {
    const { container } = render(<TeachingCallout category="categorical">Content</TeachingCallout>);
    const callout = container.querySelector('.border-purple-500');
    expect(callout).toBeInTheDocument();
  });

  it('applies operational border color', () => {
    const { container } = render(<TeachingCallout category="operational">Content</TeachingCallout>);
    const callout = container.querySelector('.border-amber-500');
    expect(callout).toBeInTheDocument();
  });

  it('applies conceptual border color', () => {
    const { container } = render(<TeachingCallout category="conceptual">Content</TeachingCallout>);
    const callout = container.querySelector('.border-green-500');
    expect(callout).toBeInTheDocument();
  });

  it('applies insight border color', () => {
    const { container } = render(<TeachingCallout category="insight">Content</TeachingCallout>);
    const callout = container.querySelector('.border-cyan-500');
    expect(callout).toBeInTheDocument();
  });
});

// =============================================================================
// Type I Tests: Compact Mode
// =============================================================================

describe('TeachingCallout - Compact Mode', () => {
  it('renders compact layout', () => {
    render(<TeachingCallout compact={true}>Test content</TeachingCallout>);
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('does not show title in compact mode', () => {
    render(<TeachingCallout compact={true} title="Title">Content</TeachingCallout>);
    expect(screen.queryByText('Title')).not.toBeInTheDocument();
  });

  it('shows icon in compact mode', () => {
    const { container } = render(<TeachingCallout compact={true}>Content</TeachingCallout>);
    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('applies compact text size', () => {
    const { container } = render(<TeachingCallout compact={true}>Content</TeachingCallout>);
    const callout = container.querySelector('.text-sm');
    expect(callout).toBeInTheDocument();
  });

  it('does not show gradient in compact mode', () => {
    const { container } = render(<TeachingCallout compact={true}>Content</TeachingCallout>);
    const gradient = container.querySelector('.bg-gradient-to-r');
    expect(gradient).not.toBeInTheDocument();
  });

  it('does not show dismiss button in compact mode', () => {
    const onDismiss = vi.fn();
    render(
      <TeachingCallout compact={true} dismissible={true} onDismiss={onDismiss}>
        Content
      </TeachingCallout>
    );
    expect(screen.queryByLabelText('Dismiss teaching callout')).not.toBeInTheDocument();
  });

  it('has note role in compact mode', () => {
    render(<TeachingCallout compact={true}>Content</TeachingCallout>);
    expect(screen.getByRole('note')).toBeInTheDocument();
  });
});

// =============================================================================
// Type I Tests: Dismissible
// =============================================================================

describe('TeachingCallout - Dismissible', () => {
  it('does not show dismiss button by default', () => {
    render(<TeachingCallout>Content</TeachingCallout>);
    expect(screen.queryByLabelText('Dismiss teaching callout')).not.toBeInTheDocument();
  });

  it('shows dismiss button when dismissible=true and onDismiss provided', () => {
    const onDismiss = vi.fn();
    render(
      <TeachingCallout dismissible={true} onDismiss={onDismiss}>
        Content
      </TeachingCallout>
    );
    expect(screen.getByLabelText('Dismiss teaching callout')).toBeInTheDocument();
  });

  it('does not show dismiss button if dismissible but no onDismiss', () => {
    render(<TeachingCallout dismissible={true}>Content</TeachingCallout>);
    expect(screen.queryByLabelText('Dismiss teaching callout')).not.toBeInTheDocument();
  });

  it('dismiss button has proper accessibility', () => {
    const onDismiss = vi.fn();
    render(
      <TeachingCallout dismissible={true} onDismiss={onDismiss}>
        Content
      </TeachingCallout>
    );
    const button = screen.getByLabelText('Dismiss teaching callout');
    expect(button).toHaveClass('focus-visible:outline-blue-500');
  });

  it('dismiss button respects reduced motion', () => {
    const onDismiss = vi.fn();
    render(
      <TeachingCallout dismissible={true} onDismiss={onDismiss}>
        Content
      </TeachingCallout>
    );
    const button = screen.getByLabelText('Dismiss teaching callout');
    expect(button).toHaveClass('motion-reduce:transition-none');
  });
});

// =============================================================================
// Type III Tests: Spies - Event Handling
// =============================================================================

describe('TeachingCallout - Spies', () => {
  it('calls onDismiss when dismiss button clicked', () => {
    const onDismiss = vi.fn();
    render(
      <TeachingCallout dismissible={true} onDismiss={onDismiss}>
        Content
      </TeachingCallout>
    );

    fireEvent.click(screen.getByLabelText('Dismiss teaching callout'));
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it('does not call onDismiss when content clicked', () => {
    const onDismiss = vi.fn();
    render(
      <TeachingCallout dismissible={true} onDismiss={onDismiss}>
        Content
      </TeachingCallout>
    );

    fireEvent.click(screen.getByText('Content'));
    expect(onDismiss).not.toHaveBeenCalled();
  });
});

// =============================================================================
// Type II Tests: Saboteurs - Edge Cases
// =============================================================================

describe('TeachingCallout - Saboteurs', () => {
  it('handles very long content', () => {
    const longContent =
      'This is a very long teaching message that might wrap to multiple lines and test how the component handles extensive content that could potentially overflow or cause layout issues.';
    render(<TeachingCallout>{longContent}</TeachingCallout>);
    expect(screen.getByText(longContent)).toBeInTheDocument();
  });

  it('handles React elements as children', () => {
    render(
      <TeachingCallout>
        <div>
          <strong>Bold text</strong> and <em>italic text</em>
        </div>
      </TeachingCallout>
    );
    expect(screen.getByText('Bold text')).toBeInTheDocument();
    expect(screen.getByText('italic text')).toBeInTheDocument();
  });

  it('handles undefined onDismiss gracefully', () => {
    render(
      <TeachingCallout dismissible={true} onDismiss={undefined}>
        Content
      </TeachingCallout>
    );
    expect(screen.queryByLabelText('Dismiss teaching callout')).not.toBeInTheDocument();
  });

  it('handles undefined title gracefully', () => {
    render(<TeachingCallout title={undefined}>Content</TeachingCallout>);
    expect(screen.getByText('Insight')).toBeInTheDocument();
  });

  it('applies custom className without breaking styles', () => {
    const { container } = render(
      <TeachingCallout className="custom-class">Content</TeachingCallout>
    );
    const callout = container.querySelector('.custom-class');
    expect(callout).toBeInTheDocument();
    expect(callout).toHaveClass('bg-gradient-to-r');
  });

  it('handles empty string as children', () => {
    render(<TeachingCallout>{''}</TeachingCallout>);
    const callout = screen.getByRole('note');
    expect(callout).toBeInTheDocument();
  });
});

// =============================================================================
// Teaching Messages Tests
// =============================================================================

describe('Teaching Messages', () => {
  it('TEACHING_MESSAGES contains right_to_rest', () => {
    expect(TEACHING_MESSAGES.right_to_rest).toBeDefined();
    expect(TEACHING_MESSAGES.right_to_rest).toContain('RESTING');
  });

  it('TEACHING_MESSAGES contains operad_arity', () => {
    expect(TEACHING_MESSAGES.operad_arity).toBeDefined();
    expect(TEACHING_MESSAGES.operad_arity).toContain('Operad');
  });

  it('TEACHING_MESSAGES contains citizen_polynomial', () => {
    expect(TEACHING_MESSAGES.citizen_polynomial).toBeDefined();
    expect(TEACHING_MESSAGES.citizen_polynomial).toContain('5 phases');
  });

  it('TEACHING_MESSAGES contains consent_debt', () => {
    expect(TEACHING_MESSAGES.consent_debt).toBeDefined();
    expect(TEACHING_MESSAGES.consent_debt).toContain('Consent debt');
  });

  it('TEACHING_MESSAGES contains invisible_director', () => {
    expect(TEACHING_MESSAGES.invisible_director).toBeDefined();
    expect(TEACHING_MESSAGES.invisible_director).toContain('invisible');
  });

  it('TEACHING_MESSAGES contains timer_polynomial', () => {
    expect(TEACHING_MESSAGES.timer_polynomial).toBeDefined();
    expect(TEACHING_MESSAGES.timer_polynomial).toContain('Timers');
  });

  it('TEACHING_MESSAGES contains polynomial_intro', () => {
    expect(TEACHING_MESSAGES.polynomial_intro).toBeDefined();
    expect(TEACHING_MESSAGES.polynomial_intro).toContain('PolyAgent');
  });

  it('TEACHING_MESSAGES contains operad_intro', () => {
    expect(TEACHING_MESSAGES.operad_intro).toBeDefined();
    expect(TEACHING_MESSAGES.operad_intro).toContain('Operads');
  });

  it('TEACHING_MESSAGES contains witness_trace', () => {
    expect(TEACHING_MESSAGES.witness_trace).toBeDefined();
    expect(TEACHING_MESSAGES.witness_trace).toContain('witness');
  });

  it('TEACHING_MESSAGES contains observer_dependent', () => {
    expect(TEACHING_MESSAGES.observer_dependent).toBeDefined();
    expect(TEACHING_MESSAGES.observer_dependent).toContain('observer');
  });

  it('getTeachingMessage returns correct message', () => {
    const message = getTeachingMessage('right_to_rest');
    expect(message).toBe(TEACHING_MESSAGES.right_to_rest);
  });

  it('getTeachingMessage works for all keys', () => {
    const keys = Object.keys(TEACHING_MESSAGES) as Array<keyof typeof TEACHING_MESSAGES>;
    keys.forEach((key) => {
      const message = getTeachingMessage(key);
      expect(message).toBeDefined();
      expect(typeof message).toBe('string');
      expect(message.length).toBeGreaterThan(0);
    });
  });
});

// =============================================================================
// Integration Tests
// =============================================================================

describe('TeachingCallout - Integration', () => {
  it('renders with preset message and category', () => {
    render(
      <TeachingCallout category="categorical" dismissible={true} onDismiss={vi.fn()}>
        {TEACHING_MESSAGES.polynomial_intro}
      </TeachingCallout>
    );

    expect(screen.getByText(/PolyAgent/)).toBeInTheDocument();
    expect(screen.getByText('Categorical')).toBeInTheDocument();
    expect(screen.getByLabelText('Dismiss teaching callout')).toBeInTheDocument();
  });

  it('renders compact with preset message', () => {
    render(
      <TeachingCallout compact={true} category="operational">
        {TEACHING_MESSAGES.operad_intro}
      </TeachingCallout>
    );

    expect(screen.getByText(/Operads/)).toBeInTheDocument();
  });

  it('renders multiple callouts independently', () => {
    const { container } = render(
      <div>
        <TeachingCallout category="categorical">First</TeachingCallout>
        <TeachingCallout category="operational">Second</TeachingCallout>
        <TeachingCallout category="conceptual">Third</TeachingCallout>
      </div>
    );

    const callouts = container.querySelectorAll('[role="note"]');
    expect(callouts).toHaveLength(3);
  });
});
