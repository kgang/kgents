/**
 * Tests for ConsentDebtMachine component.
 *
 * T-gent Type I: Contract tests (required props, defaults)
 * T-gent Type II: Saboteur tests (edge cases, boundary values)
 * T-gent Type III: Spy tests (callback verification)
 *
 * @see impl/claude/web/src/components/park/ConsentDebtMachine.tsx
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ConsentDebtMachine } from '@/components/park/ConsentDebtMachine';

// =============================================================================
// Test Fixtures
// =============================================================================

const defaultProps = {
  consentDebt: 0.3,
  forcesUsed: 0,
  forcesRemaining: 3,
};

// =============================================================================
// Type I: Contract Tests
// =============================================================================

describe('ConsentDebtMachine - Contracts', () => {
  it('renders with required props', () => {
    render(<ConsentDebtMachine {...defaultProps} />);

    expect(screen.getByText('Consent Debt Machine')).toBeInTheDocument();
  });

  it('applies default forceDisabled prop (false)', () => {
    render(<ConsentDebtMachine {...defaultProps} onForce={vi.fn()} />);

    const forceButton = screen.getByText('Use Force');
    expect(forceButton).not.toBeDisabled();
  });

  it('applies default showStateMachine prop (true)', () => {
    render(<ConsentDebtMachine {...defaultProps} />);

    expect(screen.getByText('Debt Levels')).toBeInTheDocument();
  });

  it('applies default showTeaching prop (true)', () => {
    render(<ConsentDebtMachine {...defaultProps} />);

    // Teaching callout should be visible
    expect(screen.getByText(/consent/i)).toBeInTheDocument();
  });

  it('applies default compact prop (false)', () => {
    render(<ConsentDebtMachine {...defaultProps} />);

    // Full mode shows constraints section
    expect(screen.getByText(/Constraints at/)).toBeInTheDocument();
  });
});

// =============================================================================
// Type II: Saboteur Tests (Edge Cases)
// =============================================================================

describe('ConsentDebtMachine - Saboteurs', () => {
  it('categorizes debt as HEALTHY (0-25%)', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={0.2} />);

    expect(screen.getByText(/All operations available/)).toBeInTheDocument();
  });

  it('categorizes debt as ELEVATED (25-50%)', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={0.4} />);

    expect(screen.getByText(/Minor serendipity reduction/)).toBeInTheDocument();
  });

  it('categorizes debt as HIGH (50-75%)', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={0.6} />);

    expect(screen.getByText(/Force costs 3x tokens/)).toBeInTheDocument();
  });

  it('categorizes debt as CRITICAL (>75%)', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={0.9} />);

    expect(screen.getByText(/Forces blocked/)).toBeInTheDocument();
  });

  it('handles 0% consent debt', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={0} />);

    expect(screen.getByText('0%')).toBeInTheDocument();
    expect(screen.getByText(/All operations available/)).toBeInTheDocument();
  });

  it('handles 100% consent debt', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={1.0} />);

    expect(screen.getByText('100%')).toBeInTheDocument();
    expect(screen.getByText(/Forces blocked/)).toBeInTheDocument();
  });

  it('shows "High Debt!" warning at HIGH level', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={0.65} />);

    expect(screen.getByText('High Debt!')).toBeInTheDocument();
  });

  it('shows "High Debt!" warning at CRITICAL level', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={0.85} />);

    expect(screen.getByText('High Debt!')).toBeInTheDocument();
  });

  it('does not show "High Debt!" at ELEVATED level', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={0.4} />);

    expect(screen.queryByText('High Debt!')).not.toBeInTheDocument();
  });

  it('displays force tokens correctly', () => {
    render(<ConsentDebtMachine {...defaultProps} forcesUsed={1} forcesRemaining={2} />);

    // Should show 3 total tokens
    const { container } = render(<ConsentDebtMachine {...defaultProps} forcesUsed={1} forcesRemaining={2} />);
    const tokens = container.querySelectorAll('[class*="rounded-full"][class*="border-2"]');
    expect(tokens.length).toBe(3);
  });

  it('handles all forces used', () => {
    render(<ConsentDebtMachine {...defaultProps} forcesUsed={3} forcesRemaining={0} onForce={vi.fn()} />);

    const forceButton = screen.getByText('Use Force');
    expect(forceButton).toBeDisabled();
  });

  it('handles no forces used', () => {
    render(<ConsentDebtMachine {...defaultProps} forcesUsed={0} forcesRemaining={3} />);

    expect(screen.getByText('3/3')).toBeInTheDocument();
  });

  it('blocks force button at CRITICAL debt', () => {
    render(
      <ConsentDebtMachine
        {...defaultProps}
        consentDebt={0.9}
        forcesRemaining={3}
        onForce={vi.fn()}
      />
    );

    const forceButton = screen.getByText('Blocked');
    expect(forceButton).toBeDisabled();
  });

  it('shows rupture warning at CRITICAL debt', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={0.85} />);

    expect(screen.getByText(/At rupture point/)).toBeInTheDocument();
  });

  it('shows 3x token cost warning at HIGH debt', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={0.65} onForce={vi.fn()} />);

    expect(screen.getByText(/Force costs 3x tokens at HIGH debt/)).toBeInTheDocument();
  });

  it('does not show 3x warning at ELEVATED debt', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={0.4} onForce={vi.fn()} />);

    expect(screen.queryByText(/Force costs 3x/)).not.toBeInTheDocument();
  });
});

// =============================================================================
// Type III: Spy Tests (Callbacks)
// =============================================================================

describe('ConsentDebtMachine - Spies', () => {
  it('calls onForce when Use Force button clicked', () => {
    const onForce = vi.fn();

    render(
      <ConsentDebtMachine
        {...defaultProps}
        forcesRemaining={3}
        onForce={onForce}
      />
    );

    const forceButton = screen.getByText('Use Force');
    fireEvent.click(forceButton);

    expect(onForce).toHaveBeenCalledTimes(1);
  });

  it('does not call onForce when disabled', () => {
    const onForce = vi.fn();

    render(
      <ConsentDebtMachine
        {...defaultProps}
        forceDisabled={true}
        onForce={onForce}
      />
    );

    const forceButton = screen.getByText('Use Force');
    expect(forceButton).toBeDisabled();

    fireEvent.click(forceButton);
    expect(onForce).not.toHaveBeenCalled();
  });

  it('does not call onForce when no forces remaining', () => {
    const onForce = vi.fn();

    render(
      <ConsentDebtMachine
        {...defaultProps}
        forcesRemaining={0}
        forcesUsed={3}
        onForce={onForce}
      />
    );

    const forceButton = screen.getByText('Use Force');
    expect(forceButton).toBeDisabled();

    fireEvent.click(forceButton);
    expect(onForce).not.toHaveBeenCalled();
  });

  it('does not call onForce at CRITICAL debt level', () => {
    const onForce = vi.fn();

    render(
      <ConsentDebtMachine
        {...defaultProps}
        consentDebt={0.9}
        forcesRemaining={3}
        onForce={onForce}
      />
    );

    const forceButton = screen.getByText('Blocked');
    expect(forceButton).toBeDisabled();

    fireEvent.click(forceButton);
    expect(onForce).not.toHaveBeenCalled();
  });

  it('handles onForce undefined gracefully', () => {
    render(<ConsentDebtMachine {...defaultProps} />);

    // Should not render force button when no callback provided
    expect(screen.queryByText('Use Force')).not.toBeInTheDocument();
  });
});

// =============================================================================
// Rendering Mode Tests
// =============================================================================

describe('ConsentDebtMachine - Rendering Modes', () => {
  it('renders compact mode with minimal info', () => {
    render(<ConsentDebtMachine {...defaultProps} compact={true} />);

    expect(screen.getByText('Consent Debt')).toBeInTheDocument();
    // Should not show constraints in compact mode
    expect(screen.queryByText(/Constraints at/)).not.toBeInTheDocument();
  });

  it('hides state machine when showStateMachine is false', () => {
    render(<ConsentDebtMachine {...defaultProps} showStateMachine={false} />);

    expect(screen.queryByText('Debt Levels')).not.toBeInTheDocument();
  });

  it('hides teaching callout when showTeaching is false', () => {
    render(<ConsentDebtMachine {...defaultProps} showTeaching={false} />);

    // Should not show conceptual teaching
    expect(screen.queryByText(/Conceptual:/)).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <ConsentDebtMachine
        {...defaultProps}
        className="custom-debt-machine"
      />
    );

    expect(container.querySelector('.custom-debt-machine')).toBeInTheDocument();
  });

  it('shows compact force tokens in compact mode', () => {
    const { container } = render(
      <ConsentDebtMachine
        {...defaultProps}
        compact={true}
      />
    );

    // Compact tokens should be smaller
    const tokens = container.querySelectorAll('.w-5.h-5');
    expect(tokens.length).toBeGreaterThan(0);
  });
});

// =============================================================================
// Visual Indicator Tests
// =============================================================================

describe('ConsentDebtMachine - Visual Indicators', () => {
  it('displays ConsentDebtIndicator', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={0.6} />);

    // Indicator badge should be present
    const indicators = screen.getAllByText(/HIGH/i);
    expect(indicators.length).toBeGreaterThan(0);
  });

  it('shows debt bar with correct fill percentage', () => {
    const { container } = render(
      <ConsentDebtMachine {...defaultProps} consentDebt={0.5} />
    );

    const debtBar = container.querySelector('[style*="width: 50%"]');
    expect(debtBar).toBeInTheDocument();
  });

  it('shows threshold markers on debt bar', () => {
    const { container } = render(<ConsentDebtMachine {...defaultProps} />);

    // Should have 4 threshold markers (25%, 50%, 75%, 100%)
    const thresholds = container.querySelectorAll('[class*="border-r"]');
    expect(thresholds.length).toBeGreaterThanOrEqual(3);
  });

  it('displays valid inputs for current debt level', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={0.4} />);

    expect(screen.getByText('Valid:')).toBeInTheDocument();
  });

  it('shows used force tokens with × mark', () => {
    const { container } = render(
      <ConsentDebtMachine
        {...defaultProps}
        forcesUsed={1}
        forcesRemaining={2}
      />
    );

    expect(screen.getByText('×')).toBeInTheDocument();
  });

  it('shows constraints with warning icons at HIGH debt', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={0.65} />);

    // Should show ⚠ warning icon
    const warnings = screen.getAllByText('⚠');
    expect(warnings.length).toBeGreaterThan(0);
  });

  it('shows constraints with check marks at HEALTHY debt', () => {
    render(<ConsentDebtMachine {...defaultProps} consentDebt={0.15} />);

    // Should show ✓ check icon
    const checks = screen.getAllByText('✓');
    expect(checks.length).toBeGreaterThan(0);
  });

  it('displays forces remaining count', () => {
    render(<ConsentDebtMachine {...defaultProps} forcesRemaining={2} forcesUsed={1} />);

    expect(screen.getByText('2/3')).toBeInTheDocument();
  });

  it('shows state machine with 4 debt levels', () => {
    const { container } = render(<ConsentDebtMachine {...defaultProps} />);

    // Should show HEALTHY, ELEVATED, HIGH, CRITICAL
    const stateMachine = container.querySelector('[class*="justify-center"]');
    expect(stateMachine).toBeInTheDocument();
  });

  it('highlights current debt level in state machine', () => {
    const { container } = render(
      <ConsentDebtMachine {...defaultProps} consentDebt={0.4} />
    );

    // ELEVATED level should be highlighted (scale-105)
    const highlighted = container.querySelectorAll('.scale-105');
    expect(highlighted.length).toBeGreaterThan(0);
  });
});
