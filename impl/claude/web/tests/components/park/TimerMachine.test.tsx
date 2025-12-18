/**
 * Tests for TimerMachine component.
 *
 * T-gent Type I: Contract tests (required props, defaults)
 * T-gent Type II: Saboteur tests (edge cases, boundary values)
 * T-gent Type III: Spy tests (callback verification)
 *
 * @see impl/claude/web/src/components/park/TimerMachine.tsx
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TimerMachine, TimerMachineGrid } from '@/components/park/TimerMachine';
import type { ParkTimerInfo, ParkTimerStatus } from '@/api/types';

// =============================================================================
// Test Fixtures
// =============================================================================

const createMockTimer = (overrides?: Partial<ParkTimerInfo>): ParkTimerInfo => ({
  name: 'GDPR Timer',
  countdown: '02:15:30',
  status: 'ACTIVE' as ParkTimerStatus,
  progress: 0.35,
  remaining_seconds: 8130,
  ...overrides,
});

const defaultProps = {
  timer: createMockTimer(),
};

// =============================================================================
// Type I: Contract Tests
// =============================================================================

describe('TimerMachine - Contracts', () => {
  it('renders with required timer prop', () => {
    render(<TimerMachine {...defaultProps} />);

    expect(screen.getByText('GDPR Timer')).toBeInTheDocument();
    expect(screen.getByText('02:15:30')).toBeInTheDocument();
  });

  it('applies default accelerated prop (false)', () => {
    render(<TimerMachine {...defaultProps} />);

    // Should not show 60x badge when not accelerated
    expect(screen.queryByText('60x')).not.toBeInTheDocument();
  });

  it('applies default showStateMachine prop (true)', () => {
    render(<TimerMachine {...defaultProps} />);

    // State machine section should be visible
    expect(screen.getByText('State Machine')).toBeInTheDocument();
  });

  it('applies default showTeaching prop (false)', () => {
    render(<TimerMachine {...defaultProps} />);

    // Teaching should not be shown by default
    expect(screen.queryByText(/polynomial/i)).not.toBeInTheDocument();
  });

  it('applies default compact prop (false)', () => {
    render(<TimerMachine {...defaultProps} />);

    // Full mode shows progress percentage
    expect(screen.getByText(/elapsed/)).toBeInTheDocument();
  });
});

// =============================================================================
// Type II: Saboteur Tests (Edge Cases)
// =============================================================================

describe('TimerMachine - Saboteurs', () => {
  it('handles all timer statuses', () => {
    const statuses: ParkTimerStatus[] = [
      'PENDING',
      'ACTIVE',
      'WARNING',
      'CRITICAL',
      'EXPIRED',
      'COMPLETED',
      'PAUSED',
    ];

    statuses.forEach(status => {
      const { unmount } = render(
        <TimerMachine
          timer={createMockTimer({ status })}
        />
      );

      expect(screen.getByText('GDPR Timer')).toBeInTheDocument();
      unmount();
    });
  });

  it('shows green progress bar at low progress (0-30%)', () => {
    const { container } = render(
      <TimerMachine
        timer={createMockTimer({ progress: 0.25 })}
      />
    );

    const progressBar = container.querySelector('[style*="width: 25%"]');
    expect(progressBar).toHaveStyle({ backgroundColor: '#22c55e' });
  });

  it('shows amber progress bar at medium progress (30-60%)', () => {
    const { container } = render(
      <TimerMachine
        timer={createMockTimer({ progress: 0.45 })}
      />
    );

    const progressBar = container.querySelector('[style*="width: 45%"]');
    expect(progressBar).toHaveStyle({ backgroundColor: '#f59e0b' });
  });

  it('shows orange progress bar at high progress (60-85%)', () => {
    const { container } = render(
      <TimerMachine
        timer={createMockTimer({ progress: 0.75 })}
      />
    );

    const progressBar = container.querySelector('[style*="width: 75%"]');
    expect(progressBar).toHaveStyle({ backgroundColor: '#f97316' });
  });

  it('shows red progress bar at critical progress (>85%)', () => {
    const { container } = render(
      <TimerMachine
        timer={createMockTimer({ progress: 0.95 })}
      />
    );

    const progressBar = container.querySelector('[style*="width: 95%"]');
    expect(progressBar).toHaveStyle({ backgroundColor: '#ef4444' });
  });

  it('handles 0% progress', () => {
    const { container } = render(
      <TimerMachine
        timer={createMockTimer({ progress: 0 })}
      />
    );

    const progressBar = container.querySelector('[style*="width: 0%"]');
    expect(progressBar).toBeInTheDocument();
  });

  it('handles 100% progress', () => {
    const { container } = render(
      <TimerMachine
        timer={createMockTimer({ progress: 1.0, status: 'EXPIRED' })}
      />
    );

    const progressBar = container.querySelector('[style*="width: 100%"]');
    expect(progressBar).toBeInTheDocument();
  });

  it('applies animate-pulse for CRITICAL status', () => {
    const { container } = render(
      <TimerMachine
        timer={createMockTimer({ status: 'CRITICAL' })}
      />
    );

    const animatedElements = container.querySelectorAll('.animate-pulse');
    expect(animatedElements.length).toBeGreaterThan(0);
  });

  it('applies animate-pulse for EXPIRED status', () => {
    const { container } = render(
      <TimerMachine
        timer={createMockTimer({ status: 'EXPIRED' })}
      />
    );

    const animatedElements = container.querySelectorAll('.animate-pulse');
    expect(animatedElements.length).toBeGreaterThan(0);
  });

  it('shows accelerated badge when accelerated is true', () => {
    render(
      <TimerMachine
        timer={createMockTimer()}
        accelerated={true}
      />
    );

    expect(screen.getByText('60x')).toBeInTheDocument();
  });

  it('displays remaining seconds correctly', () => {
    render(
      <TimerMachine
        timer={createMockTimer({ remaining_seconds: 3661, countdown: '01:01:01' })}
      />
    );

    expect(screen.getByText('01:01:01')).toBeInTheDocument();
  });
});

// =============================================================================
// Rendering Mode Tests
// =============================================================================

describe('TimerMachine - Rendering Modes', () => {
  it('renders compact mode with smaller size', () => {
    render(
      <TimerMachine
        timer={createMockTimer()}
        compact={true}
      />
    );

    // Compact mode should still show timer name
    expect(screen.getByText('GDPR Timer')).toBeInTheDocument();
    // But not show "elapsed" label
    expect(screen.queryByText(/elapsed/)).not.toBeInTheDocument();
  });

  it('hides state machine when showStateMachine is false', () => {
    render(
      <TimerMachine
        timer={createMockTimer()}
        showStateMachine={false}
      />
    );

    expect(screen.queryByText('State Machine')).not.toBeInTheDocument();
  });

  it('shows teaching callout for CRITICAL status when enabled', () => {
    render(
      <TimerMachine
        timer={createMockTimer({ status: 'CRITICAL' })}
        showTeaching={true}
      />
    );

    expect(screen.getByText(/polynomial/i)).toBeInTheDocument();
  });

  it('shows teaching callout for EXPIRED status when enabled', () => {
    render(
      <TimerMachine
        timer={createMockTimer({ status: 'EXPIRED' })}
        showTeaching={true}
      />
    );

    expect(screen.getByText(/polynomial/i)).toBeInTheDocument();
  });

  it('does not show teaching for non-critical statuses', () => {
    render(
      <TimerMachine
        timer={createMockTimer({ status: 'ACTIVE' })}
        showTeaching={true}
      />
    );

    expect(screen.queryByText(/polynomial/i)).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <TimerMachine
        timer={createMockTimer()}
        className="custom-timer"
      />
    );

    expect(container.querySelector('.custom-timer')).toBeInTheDocument();
  });
});

// =============================================================================
// TimerMachineGrid Tests
// =============================================================================

describe('TimerMachineGrid - Contracts', () => {
  it('renders multiple timers in grid', () => {
    const timers = [
      createMockTimer({ name: 'GDPR Timer' }),
      createMockTimer({ name: 'SLA Timer' }),
      createMockTimer({ name: 'HIPAA Timer' }),
    ];

    render(<TimerMachineGrid timers={timers} />);

    expect(screen.getByText('GDPR Timer')).toBeInTheDocument();
    expect(screen.getByText('SLA Timer')).toBeInTheDocument();
    expect(screen.getByText('HIPAA Timer')).toBeInTheDocument();
  });

  it('shows empty state when no timers', () => {
    render(<TimerMachineGrid timers={[]} />);

    expect(screen.getByText('No active timers')).toBeInTheDocument();
  });

  it('applies grid layout for multiple timers', () => {
    const timers = [
      createMockTimer({ name: 'Timer 1' }),
      createMockTimer({ name: 'Timer 2' }),
    ];

    const { container } = render(<TimerMachineGrid timers={timers} />);

    const grid = container.querySelector('.grid');
    expect(grid).toBeInTheDocument();
  });

  it('uses single column for one timer', () => {
    const timers = [createMockTimer()];

    const { container } = render(<TimerMachineGrid timers={timers} />);

    const grid = container.querySelector('.grid-cols-1');
    expect(grid).toBeInTheDocument();
  });

  it('passes accelerated prop to child timers', () => {
    const timers = [createMockTimer()];

    render(<TimerMachineGrid timers={timers} accelerated={true} />);

    expect(screen.getByText('60x')).toBeInTheDocument();
  });

  it('passes showStateMachine prop to child timers', () => {
    const timers = [createMockTimer()];

    render(<TimerMachineGrid timers={timers} showStateMachine={false} />);

    expect(screen.queryByText('State Machine')).not.toBeInTheDocument();
  });

  it('applies compact mode to grid', () => {
    const timers = [createMockTimer(), createMockTimer({ name: 'Timer 2' })];

    const { container } = render(<TimerMachineGrid timers={timers} compact={true} />);

    // Compact grid should use 2 columns
    const grid = container.querySelector('.grid-cols-2');
    expect(grid).toBeInTheDocument();
  });
});

// =============================================================================
// Visual Indicator Tests
// =============================================================================

describe('TimerMachine - Visual Indicators', () => {
  it('displays TimerStateIndicator', () => {
    render(<TimerMachine timer={createMockTimer({ status: 'WARNING' })} />);

    // Indicator should show status
    expect(screen.getAllByText(/WARNING/i).length).toBeGreaterThan(0);
  });

  it('shows valid inputs for current state', () => {
    render(<TimerMachine timer={createMockTimer()} />);

    expect(screen.getByText('Valid:')).toBeInTheDocument();
  });

  it('displays progress percentage', () => {
    render(<TimerMachine timer={createMockTimer({ progress: 0.35 })} />);

    expect(screen.getByText('35% elapsed')).toBeInTheDocument();
  });

  it('shows threshold markers on progress bar', () => {
    const { container } = render(<TimerMachine timer={createMockTimer()} />);

    // Should have visual markers for warning/critical thresholds
    const markers = container.querySelectorAll('[title*="threshold"]');
    expect(markers.length).toBeGreaterThan(0);
  });

  it('displays countdown in monospace font', () => {
    const { container } = render(<TimerMachine timer={createMockTimer()} />);

    const countdown = container.querySelector('.font-mono');
    expect(countdown).toHaveTextContent('02:15:30');
  });
});
