/**
 * Tests for FirstVisitOverlay component.
 *
 * Following T-gent Types taxonomy:
 * - Type I (Contracts): Preconditions, postconditions, rendering contracts
 * - Type II (Saboteurs): Edge cases, invalid inputs, boundary conditions
 * - Type III (Spies): Callback verification, event handling, localStorage sync
 *
 * @see impl/claude/web/src/components/categorical/FirstVisitOverlay.tsx
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { FirstVisitOverlay, useResetFirstVisit } from '@/components/categorical/FirstVisitOverlay';

// =============================================================================
// Test Setup
// =============================================================================

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

// =============================================================================
// Type I Tests: Contracts - Basic Rendering
// =============================================================================

describe('FirstVisitOverlay - Contracts', () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  it('shows overlay on first visit', async () => {
    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      expect(screen.getByText('Welcome to Agent Town')).toBeInTheDocument();
    });
  });

  it('does not show overlay on subsequent visits', async () => {
    localStorageMock.setItem('kgents_first_visit_town', 'true');

    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      expect(screen.queryByText('Welcome to Agent Town')).not.toBeInTheDocument();
    });
  });

  it('shows overlay when forceShow is true', async () => {
    localStorageMock.setItem('kgents_first_visit_town', 'true');

    render(<FirstVisitOverlay jewel="town" forceShow={true} />);

    await waitFor(() => {
      expect(screen.getByText('Welcome to Agent Town')).toBeInTheDocument();
    });
  });

  it('renders jewel-specific title', async () => {
    render(<FirstVisitOverlay jewel="park" />);

    await waitFor(() => {
      expect(screen.getByText('Welcome to Punchdrunk Park')).toBeInTheDocument();
    });
  });

  it('renders jewel-specific subtitle', async () => {
    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      expect(screen.getByText('A living simulation of polynomial agents')).toBeInTheDocument();
    });
  });

  it('renders jewel-specific description', async () => {
    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      expect(screen.getByText(/Each citizen follows a state machine/)).toBeInTheDocument();
    });
  });

  it('renders jewel-specific icon', async () => {
    const { container } = render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  it('renders feature list', async () => {
    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      expect(screen.getByText('Citizens with 5-phase lifecycles')).toBeInTheDocument();
      expect(screen.getByText('Operad-defined interactions')).toBeInTheDocument();
      expect(screen.getByText('Coalition formation')).toBeInTheDocument();
      expect(screen.getByText('Real-time streaming')).toBeInTheDocument();
    });
  });

  it('renders Got it button', async () => {
    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      expect(screen.getByText('Got it')).toBeInTheDocument();
    });
  });

  it('renders Show me how button when onShowTutorial provided', async () => {
    const onShowTutorial = vi.fn();
    render(<FirstVisitOverlay jewel="town" onShowTutorial={onShowTutorial} />);

    await waitFor(() => {
      expect(screen.getByText('Show me how')).toBeInTheDocument();
    });
  });

  it('does not render Show me how button without onShowTutorial', async () => {
    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      expect(screen.queryByText('Show me how')).not.toBeInTheDocument();
    });
  });

  it('renders close button', async () => {
    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      expect(screen.getByLabelText('Close')).toBeInTheDocument();
    });
  });

  it('renders backdrop', async () => {
    const { container } = render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      const backdrop = container.querySelector('.bg-black\\/60.backdrop-blur-sm');
      expect(backdrop).toBeInTheDocument();
    });
  });

  it('renders children when overlay not shown', async () => {
    localStorageMock.setItem('kgents_first_visit_town', 'true');

    render(
      <FirstVisitOverlay jewel="town">
        <div>Child content</div>
      </FirstVisitOverlay>
    );

    await waitFor(() => {
      expect(screen.getByText('Child content')).toBeInTheDocument();
    });
  });

  it('renders children alongside overlay', async () => {
    render(
      <FirstVisitOverlay jewel="town">
        <div>Child content</div>
      </FirstVisitOverlay>
    );

    await waitFor(() => {
      expect(screen.getByText('Child content')).toBeInTheDocument();
      expect(screen.getByText('Welcome to Agent Town')).toBeInTheDocument();
    });
  });
});

// =============================================================================
// Type I Tests: All Jewel Types
// =============================================================================

describe('FirstVisitOverlay - All Jewel Types', () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  it('renders town jewel correctly', async () => {
    render(<FirstVisitOverlay jewel="town" />);
    await waitFor(() => {
      expect(screen.getByText('Welcome to Agent Town')).toBeInTheDocument();
    });
  });

  it('renders park jewel correctly', async () => {
    render(<FirstVisitOverlay jewel="park" />);
    await waitFor(() => {
      expect(screen.getByText('Welcome to Punchdrunk Park')).toBeInTheDocument();
    });
  });

  it('renders atelier jewel correctly', async () => {
    render(<FirstVisitOverlay jewel="atelier" />);
    await waitFor(() => {
      expect(screen.getByText('Welcome to Atelier')).toBeInTheDocument();
    });
  });

  it('renders coalition jewel correctly', async () => {
    render(<FirstVisitOverlay jewel="coalition" />);
    await waitFor(() => {
      expect(screen.getByText('Welcome to Coalition Forge')).toBeInTheDocument();
    });
  });

  it('renders brain jewel correctly', async () => {
    render(<FirstVisitOverlay jewel="brain" />);
    await waitFor(() => {
      expect(screen.getByText('Welcome to Holographic Brain')).toBeInTheDocument();
    });
  });

  it('renders gardener jewel correctly', async () => {
    render(<FirstVisitOverlay jewel="gardener" />);
    await waitFor(() => {
      expect(screen.getByText('Welcome to The Gardener')).toBeInTheDocument();
    });
  });

  it('renders gestalt jewel correctly', async () => {
    render(<FirstVisitOverlay jewel="gestalt" />);
    await waitFor(() => {
      expect(screen.getByText('Welcome to Gestalt Visualizer')).toBeInTheDocument();
    });
  });
});

// =============================================================================
// Type III Tests: Spies - Event Handling
// =============================================================================

describe('FirstVisitOverlay - Spies', () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  it('calls onDismiss when Got it button clicked', async () => {
    const onDismiss = vi.fn();
    render(<FirstVisitOverlay jewel="town" onDismiss={onDismiss} />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('Got it'));
    });

    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it('calls onDismiss when close button clicked', async () => {
    const onDismiss = vi.fn();
    render(<FirstVisitOverlay jewel="town" onDismiss={onDismiss} />);

    await waitFor(() => {
      fireEvent.click(screen.getByLabelText('Close'));
    });

    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it('calls onShowTutorial when Show me how button clicked', async () => {
    const onShowTutorial = vi.fn();
    render(<FirstVisitOverlay jewel="town" onShowTutorial={onShowTutorial} />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('Show me how'));
    });

    expect(onShowTutorial).toHaveBeenCalledTimes(1);
  });

  it('marks visit as completed when Got it clicked', async () => {
    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('Got it'));
    });

    expect(localStorageMock.getItem('kgents_first_visit_town')).toBe('true');
  });

  it('marks visit as completed when close clicked', async () => {
    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      fireEvent.click(screen.getByLabelText('Close'));
    });

    expect(localStorageMock.getItem('kgents_first_visit_town')).toBe('true');
  });

  it('marks visit as completed when Show me how clicked', async () => {
    const onShowTutorial = vi.fn();
    render(<FirstVisitOverlay jewel="town" onShowTutorial={onShowTutorial} />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('Show me how'));
    });

    expect(localStorageMock.getItem('kgents_first_visit_town')).toBe('true');
  });

  it('hides overlay after dismissal', async () => {
    const { rerender } = render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('Got it'));
    });

    // Force re-render to check if overlay is gone
    rerender(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      expect(screen.queryByText('Welcome to Agent Town')).not.toBeInTheDocument();
    });
  });
});

// =============================================================================
// Type III Tests: localStorage Integration
// =============================================================================

describe('FirstVisitOverlay - localStorage', () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  it('uses correct localStorage key for town', async () => {
    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('Got it'));
    });

    expect(localStorageMock.getItem('kgents_first_visit_town')).toBe('true');
  });

  it('uses correct localStorage key for park', async () => {
    render(<FirstVisitOverlay jewel="park" />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('Got it'));
    });

    expect(localStorageMock.getItem('kgents_first_visit_park')).toBe('true');
  });

  it('stores independent keys for different jewels', async () => {
    const { rerender } = render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('Got it'));
    });

    rerender(<FirstVisitOverlay jewel="park" />);

    await waitFor(() => {
      expect(screen.getByText('Welcome to Punchdrunk Park')).toBeInTheDocument();
    });

    expect(localStorageMock.getItem('kgents_first_visit_town')).toBe('true');
    expect(localStorageMock.getItem('kgents_first_visit_park')).toBeNull();
  });

  it('respects existing localStorage value', async () => {
    localStorageMock.setItem('kgents_first_visit_town', 'true');

    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      expect(screen.queryByText('Welcome to Agent Town')).not.toBeInTheDocument();
    });
  });
});

// =============================================================================
// Type II Tests: Saboteurs - Edge Cases
// =============================================================================

describe('FirstVisitOverlay - Saboteurs', () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  it('handles missing onDismiss gracefully', async () => {
    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('Got it'));
    });

    // Should not throw
    expect(screen.queryByText('Welcome to Agent Town')).not.toBeInTheDocument();
  });

  it('handles missing onShowTutorial gracefully', async () => {
    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      expect(screen.queryByText('Show me how')).not.toBeInTheDocument();
    });
  });

  it('handles forceShow with existing localStorage', async () => {
    localStorageMock.setItem('kgents_first_visit_town', 'true');

    render(<FirstVisitOverlay jewel="town" forceShow={true} />);

    await waitFor(() => {
      expect(screen.getByText('Welcome to Agent Town')).toBeInTheDocument();
    });
  });

  it('handles forceShow=false with existing localStorage', async () => {
    localStorageMock.setItem('kgents_first_visit_town', 'true');

    render(<FirstVisitOverlay jewel="town" forceShow={false} />);

    await waitFor(() => {
      expect(screen.queryByText('Welcome to Agent Town')).not.toBeInTheDocument();
    });
  });

  it('handles undefined children', async () => {
    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      expect(screen.getByText('Welcome to Agent Town')).toBeInTheDocument();
    });
  });

  it('renders custom content when provided', async () => {
    const customContent = <div>Custom overlay content</div>;
    render(<FirstVisitOverlay jewel="town" customContent={customContent} />);

    await waitFor(() => {
      expect(screen.getByText('Custom overlay content')).toBeInTheDocument();
      expect(screen.queryByText('Welcome to Agent Town')).not.toBeInTheDocument();
    });
  });

  it('handles rapid dismiss clicks', async () => {
    const onDismiss = vi.fn();
    render(<FirstVisitOverlay jewel="town" onDismiss={onDismiss} />);

    await waitFor(async () => {
      const button = screen.getByText('Got it');
      fireEvent.click(button);
      fireEvent.click(button);
      fireEvent.click(button);
    });

    // Should only be called once since component unmounts
    expect(onDismiss).toHaveBeenCalled();
  });
});

// =============================================================================
// useResetFirstVisit Hook Tests
// =============================================================================

describe('useResetFirstVisit', () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  it('resets specific jewel', async () => {
    localStorageMock.setItem('kgents_first_visit_town', 'true');
    localStorageMock.setItem('kgents_first_visit_park', 'true');

    const TestComponent = () => {
      const reset = useResetFirstVisit();
      return <button onClick={() => reset('town')}>Reset</button>;
    };

    render(<TestComponent />);
    fireEvent.click(screen.getByText('Reset'));

    expect(localStorageMock.getItem('kgents_first_visit_town')).toBeNull();
    expect(localStorageMock.getItem('kgents_first_visit_park')).toBe('true');
  });

  it('resets all jewels when no argument provided', async () => {
    localStorageMock.setItem('kgents_first_visit_town', 'true');
    localStorageMock.setItem('kgents_first_visit_park', 'true');
    localStorageMock.setItem('kgents_first_visit_atelier', 'true');

    const TestComponent = () => {
      const reset = useResetFirstVisit();
      return <button onClick={() => reset()}>Reset All</button>;
    };

    render(<TestComponent />);
    fireEvent.click(screen.getByText('Reset All'));

    expect(localStorageMock.getItem('kgents_first_visit_town')).toBeNull();
    expect(localStorageMock.getItem('kgents_first_visit_park')).toBeNull();
    expect(localStorageMock.getItem('kgents_first_visit_atelier')).toBeNull();
  });
});

// =============================================================================
// Type I Tests: Accessibility
// =============================================================================

describe('FirstVisitOverlay - Accessibility', () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  it('backdrop is fixed and full screen', async () => {
    const { container } = render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      const backdrop = container.querySelector('.fixed.inset-0');
      expect(backdrop).toBeInTheDocument();
    });
  });

  it('modal is centered', async () => {
    const { container } = render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      const backdrop = container.querySelector('.flex.items-center.justify-center');
      expect(backdrop).toBeInTheDocument();
    });
  });

  it('has proper z-index', async () => {
    const { container } = render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      const backdrop = container.querySelector('.z-50');
      expect(backdrop).toBeInTheDocument();
    });
  });

  it('close button has aria-label', async () => {
    render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      const closeButton = screen.getByLabelText('Close');
      expect(closeButton).toBeInTheDocument();
    });
  });

  it('applies animation classes', async () => {
    const { container } = render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      const backdrop = container.querySelector('.animate-in.fade-in');
      expect(backdrop).toBeInTheDocument();
    });
  });

  it('modal has zoom animation', async () => {
    const { container } = render(<FirstVisitOverlay jewel="town" />);

    await waitFor(() => {
      const modal = container.querySelector('.animate-in.zoom-in-95');
      expect(modal).toBeInTheDocument();
    });
  });
});
