/**
 * Tests for StateIndicator component.
 *
 * Following T-gent Types taxonomy:
 * - Type I (Contracts): Preconditions, postconditions, rendering contracts
 * - Type II (Saboteurs): Edge cases, invalid inputs, boundary conditions
 * - Type III (Spies): Callback verification, event handling
 *
 * @see impl/claude/web/src/components/categorical/StateIndicator.tsx
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  StateIndicator,
  CitizenPhaseIndicator,
  CrisisPhaseIndicator,
  TimerStateIndicator,
  ConsentDebtIndicator,
  DirectorStateIndicator,
} from '@/components/categorical/StateIndicator';

// =============================================================================
// Type I Tests: Contracts - Basic Rendering
// =============================================================================

describe('StateIndicator - Contracts', () => {
  it('renders label text', () => {
    render(<StateIndicator label="SPROUTING" />);
    expect(screen.getByText('SPROUTING')).toBeInTheDocument();
  });

  it('renders with default medium size', () => {
    const { container } = render(<StateIndicator label="active" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveClass('text-sm', 'px-3', 'py-1');
  });

  it('renders small size correctly', () => {
    const { container } = render(<StateIndicator label="idle" size="sm" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveClass('text-xs', 'px-2', 'py-0.5');
  });

  it('renders large size correctly', () => {
    const { container } = render(<StateIndicator label="critical" size="lg" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveClass('text-base', 'px-4', 'py-1.5');
  });

  it('applies custom color override', () => {
    const { container } = render(<StateIndicator label="custom" color="#ff0000" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#ff0000' });
  });

  it('shows glow effect by default', () => {
    const { container } = render(<StateIndicator label="active" />);
    const element = container.querySelector('[role="status"]');
    const style = window.getComputedStyle(element!);
    expect(style.boxShadow).toBeTruthy();
  });

  it('hides glow when glow=false', () => {
    const { container } = render(<StateIndicator label="active" glow={false} />);
    const element = container.querySelector('[role="status"]') as HTMLElement;
    // When glow=false, boxShadow is not set in inline styles
    expect(element.style.boxShadow).toBe('');
  });
});

// =============================================================================
// Type I Tests: Category Inference
// =============================================================================

describe('StateIndicator - Category Inference', () => {
  it('infers critical category from "critical" label', () => {
    const { container } = render(<StateIndicator label="critical" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#ef4444' });
  });

  it('infers critical category from "expired" label', () => {
    const { container } = render(<StateIndicator label="expired" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#ef4444' });
  });

  it('infers critical category from "incident" label', () => {
    const { container } = render(<StateIndicator label="incident" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#ef4444' });
  });

  it('infers warning category from "warning" label', () => {
    const { container } = render(<StateIndicator label="warning" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#f59e0b' });
  });

  it('infers warning category from "elevated" label', () => {
    const { container } = render(<StateIndicator label="elevated" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#f59e0b' });
  });

  it('infers active category from "active" label', () => {
    const { container } = render(<StateIndicator label="active" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#22c55e' });
  });

  it('infers active category from "working" label', () => {
    const { container } = render(<StateIndicator label="working" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#22c55e' });
  });

  it('infers success category from "healthy" label', () => {
    const { container } = render(<StateIndicator label="healthy" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#22c55e' });
  });

  it('infers neutral category from "resting" label', () => {
    const { container } = render(<StateIndicator label="resting" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#64748b' });
  });

  it('defaults to idle category for unknown labels', () => {
    const { container } = render(<StateIndicator label="unknown_state" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#64748b' });
  });

  it('respects explicit category override', () => {
    const { container } = render(<StateIndicator label="anything" category="critical" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#ef4444' });
  });
});

// =============================================================================
// Type I Tests: Icon Rendering
// =============================================================================

describe('StateIndicator - Icon Rendering', () => {
  it('auto-selects icon for "idle" state', () => {
    const { container } = render(<StateIndicator label="idle" />);
    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('auto-selects icon for "socializing" state', () => {
    const { container } = render(<StateIndicator label="socializing" />);
    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('auto-selects icon for "working" state', () => {
    const { container } = render(<StateIndicator label="working" />);
    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('icon is hidden from screen readers', () => {
    const { container } = render(<StateIndicator label="active" />);
    const icon = container.querySelector('svg');
    expect(icon).toHaveAttribute('aria-hidden', 'true');
  });
});

// =============================================================================
// Type I Tests: Animation
// =============================================================================

describe('StateIndicator - Animation', () => {
  it('does not animate by default', () => {
    const { container } = render(<StateIndicator label="test" />);
    const element = container.querySelector('[role="status"]');
    expect(element).not.toHaveClass('animate-pulse');
  });

  it('applies pulse animation when animate=true', () => {
    const { container } = render(<StateIndicator label="test" animate={true} />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveClass('animate-pulse');
  });

  it('respects reduced motion preferences', () => {
    const { container } = render(<StateIndicator label="test" animate={true} />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveClass('motion-reduce:animate-none');
  });
});

// =============================================================================
// Type II Tests: Saboteurs - Edge Cases
// =============================================================================

describe('StateIndicator - Saboteurs', () => {
  it('handles empty label', () => {
    render(<StateIndicator label="" />);
    expect(screen.queryByRole('status')).toBeInTheDocument();
  });

  it('handles very long labels', () => {
    const longLabel = 'VERY_LONG_STATE_NAME_THAT_MIGHT_OVERFLOW_THE_CONTAINER';
    render(<StateIndicator label={longLabel} />);
    expect(screen.getByText(longLabel)).toBeInTheDocument();
  });

  it('handles special characters in label', () => {
    render(<StateIndicator label="test-state_123!@#" />);
    expect(screen.getByText('test-state_123!@#')).toBeInTheDocument();
  });

  it('handles case-insensitive icon lookup', () => {
    const { container } = render(<StateIndicator label="SOCIALIZING" />);
    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('handles mixed case in category inference', () => {
    const { container } = render(<StateIndicator label="Critical" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#ef4444' });
  });

  it('handles undefined category gracefully', () => {
    const { container } = render(<StateIndicator label="test" category={undefined} />);
    const element = container.querySelector('[role="status"]');
    expect(element).toBeInTheDocument();
  });

  it('applies custom className without breaking styles', () => {
    const { container } = render(<StateIndicator label="test" className="custom-class" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveClass('custom-class');
    expect(element).toHaveClass('inline-flex');
  });
});

// =============================================================================
// Type III Tests: Spies - Event Handling
// =============================================================================

describe('StateIndicator - Spies', () => {
  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(<StateIndicator label="test" onClick={onClick} />);

    const element = screen.getByRole('button');
    fireEvent.click(element);

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('shows role=button when clickable', () => {
    const onClick = vi.fn();
    render(<StateIndicator label="test" onClick={onClick} />);

    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('shows role=status when not clickable', () => {
    render(<StateIndicator label="test" />);

    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('applies hover styles when clickable', () => {
    const onClick = vi.fn();
    const { container } = render(<StateIndicator label="test" onClick={onClick} />);
    const element = container.querySelector('[role="button"]');
    expect(element).toHaveClass('cursor-pointer', 'hover:scale-105');
  });

  it('does not apply hover styles when not clickable', () => {
    const { container } = render(<StateIndicator label="test" />);
    const element = container.querySelector('[role="status"]');
    expect(element).not.toHaveClass('cursor-pointer');
  });

  it('handles Enter key for clickable indicators', () => {
    const onClick = vi.fn();
    render(<StateIndicator label="test" onClick={onClick} />);

    const element = screen.getByRole('button');
    fireEvent.keyDown(element, { key: 'Enter' });

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('handles Space key for clickable indicators', () => {
    const onClick = vi.fn();
    render(<StateIndicator label="test" onClick={onClick} />);

    const element = screen.getByRole('button');
    fireEvent.keyDown(element, { key: ' ' });

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('ignores other keys', () => {
    const onClick = vi.fn();
    render(<StateIndicator label="test" onClick={onClick} />);

    const element = screen.getByRole('button');
    fireEvent.keyDown(element, { key: 'a' });

    expect(onClick).not.toHaveBeenCalled();
  });

  it('sets tabIndex=0 when clickable', () => {
    const onClick = vi.fn();
    render(<StateIndicator label="test" onClick={onClick} />);

    const element = screen.getByRole('button');
    expect(element).toHaveAttribute('tabIndex', '0');
  });

  it('does not set tabIndex when not clickable', () => {
    render(<StateIndicator label="test" />);

    const element = screen.getByRole('status');
    expect(element).not.toHaveAttribute('tabIndex');
  });

  it('prevents default on Space key', () => {
    const onClick = vi.fn();
    render(<StateIndicator label="test" onClick={onClick} />);

    const element = screen.getByRole('button');
    const event = new KeyboardEvent('keydown', { key: ' ', bubbles: true });
    const preventDefaultSpy = vi.spyOn(event, 'preventDefault');

    element.dispatchEvent(event);

    expect(preventDefaultSpy).toHaveBeenCalled();
  });
});

// =============================================================================
// Type I Tests: Accessibility
// =============================================================================

describe('StateIndicator - Accessibility', () => {
  it('includes descriptive aria-label', () => {
    render(<StateIndicator label="active" />);
    const element = screen.getByRole('status');
    expect(element).toHaveAttribute('aria-label', 'active state, active');
  });

  it('includes clickable in aria-label when onClick provided', () => {
    const onClick = vi.fn();
    render(<StateIndicator label="test" onClick={onClick} />);
    const element = screen.getByRole('button');
    expect(element).toHaveAttribute('aria-label');
    expect(element.getAttribute('aria-label')).toContain('clickable');
  });

  it('sets aria-live=polite when animating', () => {
    render(<StateIndicator label="test" animate={true} />);
    const element = screen.getByRole('status');
    expect(element).toHaveAttribute('aria-live', 'polite');
  });

  it('does not set aria-live when not animating', () => {
    render(<StateIndicator label="test" />);
    const element = screen.getByRole('status');
    expect(element).not.toHaveAttribute('aria-live');
  });

  it('has focus-visible outline for keyboard navigation', () => {
    const onClick = vi.fn();
    const { container } = render(<StateIndicator label="test" onClick={onClick} />);
    const element = container.querySelector('[role="button"]');
    expect(element).toHaveClass('focus-visible:outline-blue-500');
  });
});

// =============================================================================
// Preset Indicator Tests
// =============================================================================

describe('CitizenPhaseIndicator', () => {
  it('renders citizen phase', () => {
    render(<CitizenPhaseIndicator state="socializing" />);
    expect(screen.getByText('socializing')).toBeInTheDocument();
  });

  it('infers category correctly', () => {
    const { container } = render(<CitizenPhaseIndicator state="working" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#22c55e' });
  });
});

describe('CrisisPhaseIndicator', () => {
  it('maps NORMAL to success category', () => {
    const { container } = render(<CrisisPhaseIndicator state="NORMAL" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#22c55e' });
  });

  it('maps INCIDENT to critical category', () => {
    const { container } = render(<CrisisPhaseIndicator state="INCIDENT" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#ef4444' });
  });

  it('maps RESPONSE to warning category', () => {
    const { container } = render(<CrisisPhaseIndicator state="RESPONSE" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#f59e0b' });
  });

  it('maps RECOVERY to active category', () => {
    const { container } = render(<CrisisPhaseIndicator state="RECOVERY" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#22c55e' });
  });
});

describe('TimerStateIndicator', () => {
  it('maps PENDING to neutral category', () => {
    const { container } = render(<TimerStateIndicator state="PENDING" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#64748b' });
  });

  it('maps ACTIVE to active category', () => {
    const { container } = render(<TimerStateIndicator state="ACTIVE" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#22c55e' });
  });

  it('maps WARNING to warning category', () => {
    const { container } = render(<TimerStateIndicator state="WARNING" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#f59e0b' });
  });

  it('maps CRITICAL to critical category', () => {
    const { container } = render(<TimerStateIndicator state="CRITICAL" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#ef4444' });
  });

  it('maps EXPIRED to critical category', () => {
    const { container } = render(<TimerStateIndicator state="EXPIRED" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#ef4444' });
  });
});

describe('ConsentDebtIndicator', () => {
  it('maps HEALTHY to success category', () => {
    const { container } = render(<ConsentDebtIndicator state="HEALTHY" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#22c55e' });
  });

  it('maps ELEVATED to warning category', () => {
    const { container } = render(<ConsentDebtIndicator state="ELEVATED" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#f59e0b' });
  });

  it('maps HIGH to warning category', () => {
    const { container } = render(<ConsentDebtIndicator state="HIGH" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#f59e0b' });
  });

  it('maps CRITICAL to critical category', () => {
    const { container } = render(<ConsentDebtIndicator state="CRITICAL" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#ef4444' });
  });
});

describe('DirectorStateIndicator', () => {
  it('maps OBSERVING to neutral category', () => {
    const { container } = render(<DirectorStateIndicator state="OBSERVING" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#64748b' });
  });

  it('maps BUILDING to warning category', () => {
    const { container } = render(<DirectorStateIndicator state="BUILDING" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#f59e0b' });
  });

  it('maps INJECTING to active category', () => {
    const { container } = render(<DirectorStateIndicator state="INJECTING" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#22c55e' });
  });

  it('maps COOLING to neutral category', () => {
    const { container } = render(<DirectorStateIndicator state="COOLING" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#64748b' });
  });

  it('maps INTERVENING to critical category', () => {
    const { container } = render(<DirectorStateIndicator state="INTERVENING" />);
    const element = container.querySelector('[role="status"]');
    expect(element).toHaveStyle({ color: '#ef4444' });
  });
});
