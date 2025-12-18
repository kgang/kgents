/**
 * Tests for PhaseVisualization component.
 *
 * T-gent Type I: Contract tests (required props, defaults)
 * T-gent Type II: Saboteur tests (edge cases, boundary values)
 * T-gent Type III: Spy tests (callback verification)
 *
 * @see impl/claude/web/src/components/park/PhaseVisualization.tsx
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PhaseVisualization } from '@/components/park/PhaseVisualization';
import type { ParkCrisisPhase } from '@/api/types';

// =============================================================================
// Test Fixtures
// =============================================================================

const mockPhaseTransitions = [
  {
    from: 'NORMAL' as ParkCrisisPhase,
    to: 'INCIDENT' as ParkCrisisPhase,
    consent_debt: 0.1,
    timestamp: '2024-12-16T10:00:00Z',
  },
  {
    from: 'INCIDENT' as ParkCrisisPhase,
    to: 'RESPONSE' as ParkCrisisPhase,
    consent_debt: 0.25,
    timestamp: '2024-12-16T10:05:00Z',
  },
];

const defaultProps = {
  currentPhase: 'NORMAL' as ParkCrisisPhase,
  availableTransitions: ['INCIDENT'] as ParkCrisisPhase[],
  phaseTransitions: mockPhaseTransitions,
  consentDebt: 0.1,
};

// =============================================================================
// Type I: Contract Tests
// =============================================================================

describe('PhaseVisualization - Contracts', () => {
  it('renders with required props', () => {
    render(<PhaseVisualization {...defaultProps} />);

    expect(screen.getByText('Crisis Phase Machine')).toBeInTheDocument();
  });

  it('applies default disabled prop (false)', () => {
    render(<PhaseVisualization {...defaultProps} />);

    // Available transitions should be clickable when not disabled
    const transitionButtons = screen.getAllByRole('button');
    const availableButton = transitionButtons.find(btn =>
      btn.textContent?.includes('Incident')
    );
    expect(availableButton).not.toBeDisabled();
  });

  it('applies default compact prop (false)', () => {
    const { container } = render(<PhaseVisualization {...defaultProps} />);

    // Full view should show transition history
    expect(screen.getByText(/Transition History/)).toBeInTheDocument();
  });

  it('applies default showTeaching prop (true)', () => {
    render(<PhaseVisualization {...defaultProps} />);

    // Teaching callout should be visible
    expect(screen.getByText(/polynomial/i)).toBeInTheDocument();
  });

  it('handles empty availableTransitions', () => {
    render(
      <PhaseVisualization
        {...defaultProps}
        availableTransitions={[]}
      />
    );

    expect(screen.getByText('No valid transitions')).toBeInTheDocument();
  });

  it('handles empty phaseTransitions', () => {
    render(
      <PhaseVisualization
        {...defaultProps}
        phaseTransitions={[]}
      />
    );

    // Should not show transition history section
    expect(screen.queryByText(/Transition History/)).not.toBeInTheDocument();
  });
});

// =============================================================================
// Type II: Saboteur Tests (Edge Cases)
// =============================================================================

describe('PhaseVisualization - Saboteurs', () => {
  it('handles all crisis phases', () => {
    const phases: ParkCrisisPhase[] = ['NORMAL', 'INCIDENT', 'RESPONSE', 'RECOVERY'];

    phases.forEach(phase => {
      const { unmount } = render(
        <PhaseVisualization
          {...defaultProps}
          currentPhase={phase}
        />
      );

      // Should render without crashing
      expect(screen.getByText('Crisis Phase Machine')).toBeInTheDocument();
      unmount();
    });
  });

  it('highlights current phase with glow effect', () => {
    const { container } = render(
      <PhaseVisualization
        {...defaultProps}
        currentPhase="INCIDENT"
      />
    );

    // Current phase should have animate-pulse class
    const pulseElements = container.querySelectorAll('.animate-pulse');
    expect(pulseElements.length).toBeGreaterThan(0);
  });

  it('disables unavailable phase transitions', () => {
    render(
      <PhaseVisualization
        {...defaultProps}
        currentPhase="NORMAL"
        availableTransitions={['INCIDENT']}
      />
    );

    const buttons = screen.getAllByRole('button');

    // Find phase nodes (not transition buttons)
    const phaseButtons = buttons.filter(btn =>
      btn.className.includes('flex-col') && btn.className.includes('items-center')
    );

    // RESPONSE and RECOVERY should be disabled/unavailable
    const unavailableButtons = phaseButtons.filter(btn =>
      btn.className.includes('opacity-40')
    );
    expect(unavailableButtons.length).toBeGreaterThan(0);
  });

  it('shows high debt warning at >60% consent debt', () => {
    render(
      <PhaseVisualization
        {...defaultProps}
        consentDebt={0.7}
      />
    );

    expect(screen.getByText(/High consent debt is constraining options/)).toBeInTheDocument();
  });

  it('does not show debt warning at low debt', () => {
    render(
      <PhaseVisualization
        {...defaultProps}
        consentDebt={0.2}
      />
    );

    expect(screen.queryByText(/High consent debt/)).not.toBeInTheDocument();
  });

  it('handles 0% consent debt', () => {
    render(
      <PhaseVisualization
        {...defaultProps}
        consentDebt={0}
      />
    );

    // Should show low debt level
    expect(screen.queryByText(/High consent debt/)).not.toBeInTheDocument();
  });

  it('handles 100% consent debt', () => {
    render(
      <PhaseVisualization
        {...defaultProps}
        consentDebt={1.0}
      />
    );

    // Should show high debt warning
    expect(screen.getByText(/High consent debt/)).toBeInTheDocument();
  });

  it('limits transition history to 5 most recent', () => {
    const manyTransitions = Array.from({ length: 10 }, (_, i) => ({
      from: 'NORMAL' as ParkCrisisPhase,
      to: 'INCIDENT' as ParkCrisisPhase,
      consent_debt: 0.1 + i * 0.05,
      timestamp: `2024-12-16T10:${String(i).padStart(2, '0')}:00Z`,
    }));

    render(
      <PhaseVisualization
        {...defaultProps}
        phaseTransitions={manyTransitions}
      />
    );

    // Should only show last 5 transitions
    const debtDisplays = screen.getAllByText(/debt:/);
    expect(debtDisplays.length).toBeLessThanOrEqual(5);
  });
});

// =============================================================================
// Type III: Spy Tests (Callbacks)
// =============================================================================

describe('PhaseVisualization - Spies', () => {
  it('calls onTransition when available phase clicked', () => {
    const onTransition = vi.fn();

    render(
      <PhaseVisualization
        {...defaultProps}
        currentPhase="NORMAL"
        availableTransitions={['INCIDENT']}
        onTransition={onTransition}
      />
    );

    // Click on available transition button
    const incidentButton = screen.getByText('Incident');
    fireEvent.click(incidentButton);

    expect(onTransition).toHaveBeenCalledWith('INCIDENT');
  });

  it('does not call onTransition when disabled', () => {
    const onTransition = vi.fn();

    render(
      <PhaseVisualization
        {...defaultProps}
        disabled={true}
        onTransition={onTransition}
      />
    );

    const buttons = screen.getAllByRole('button');
    buttons.forEach(btn => {
      if (!btn.disabled) {
        fireEvent.click(btn);
      }
    });

    expect(onTransition).not.toHaveBeenCalled();
  });

  it('does not call onTransition for unavailable phases', () => {
    const onTransition = vi.fn();

    render(
      <PhaseVisualization
        {...defaultProps}
        currentPhase="NORMAL"
        availableTransitions={['INCIDENT']}
        onTransition={onTransition}
      />
    );

    // Try to click on unavailable phase nodes (should be disabled)
    const buttons = screen.getAllByRole('button');
    const unavailableButtons = buttons.filter(btn =>
      btn.disabled && btn.className.includes('opacity-40')
    );

    unavailableButtons.forEach(btn => {
      fireEvent.click(btn);
    });

    expect(onTransition).not.toHaveBeenCalled();
  });

  it('handles onTransition undefined gracefully', () => {
    render(
      <PhaseVisualization
        {...defaultProps}
        availableTransitions={['INCIDENT']}
      />
    );

    // Should not crash when clicking without callback
    const incidentButton = screen.getByText('Incident');
    expect(() => fireEvent.click(incidentButton)).not.toThrow();
  });
});

// =============================================================================
// Rendering Mode Tests
// =============================================================================

describe('PhaseVisualization - Rendering Modes', () => {
  it('renders compact mode without transition history', () => {
    render(
      <PhaseVisualization
        {...defaultProps}
        compact={true}
      />
    );

    // Should not show transition history in compact mode
    expect(screen.queryByText(/Transition History/)).not.toBeInTheDocument();
  });

  it('renders compact mode without teaching callout', () => {
    render(
      <PhaseVisualization
        {...defaultProps}
        compact={true}
      />
    );

    // Teaching should be hidden in compact mode
    expect(screen.queryByText(/polynomial/i)).not.toBeInTheDocument();
  });

  it('hides teaching callout when showTeaching is false', () => {
    render(
      <PhaseVisualization
        {...defaultProps}
        showTeaching={false}
      />
    );

    expect(screen.queryByText(/polynomial/i)).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <PhaseVisualization
        {...defaultProps}
        className="custom-phase-viz"
      />
    );

    expect(container.querySelector('.custom-phase-viz')).toBeInTheDocument();
  });
});

// =============================================================================
// Visual Indicator Tests
// =============================================================================

describe('PhaseVisualization - Visual Indicators', () => {
  it('shows phase indicator for current phase', () => {
    render(
      <PhaseVisualization
        {...defaultProps}
        currentPhase="RESPONSE"
      />
    );

    // CrisisPhaseIndicator should be rendered
    const indicators = screen.getAllByText(/RESPONSE/i);
    expect(indicators.length).toBeGreaterThan(0);
  });

  it('displays valid inputs for current phase', () => {
    render(
      <PhaseVisualization
        {...defaultProps}
        currentPhase="NORMAL"
      />
    );

    // Should show "Valid:" label
    expect(screen.getByText('Valid:')).toBeInTheDocument();
  });

  it('shows transition arrows between phases', () => {
    const { container } = render(<PhaseVisualization {...defaultProps} />);

    // SVG arrows should be present
    const arrows = container.querySelectorAll('svg');
    expect(arrows.length).toBeGreaterThan(0);
  });

  it('highlights active transition arrow', () => {
    const { container } = render(
      <PhaseVisualization
        {...defaultProps}
        currentPhase="INCIDENT"
      />
    );

    // Active arrow should use green stroke
    const arrows = container.querySelectorAll('path[stroke="#22c55e"]');
    expect(arrows.length).toBeGreaterThan(0);
  });

  it('displays consent debt percentage in transition history', () => {
    render(<PhaseVisualization {...defaultProps} />);

    // Should show debt percentages like "debt: 10%"
    expect(screen.getByText(/debt: 10%/)).toBeInTheDocument();
  });
});
