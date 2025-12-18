/**
 * Tests for Interactive Gallery Pilots (Gallery V2).
 *
 * Tests cover:
 * 1. PolynomialPlayground - State machine visualization
 * 2. OperadWiring - Composition diagram
 * 3. TownLive - Streaming simulation
 *
 * @see plans/gallery-pilots-top3.md
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { PolynomialPlayground } from '@/components/projection/gallery/PolynomialPlayground';
import { OperadWiring } from '@/components/projection/gallery/OperadWiring';
import { TownLive } from '@/components/projection/gallery/TownLive';

// =============================================================================
// PolynomialPlayground Tests
// =============================================================================

describe('PolynomialPlayground', () => {
  describe('Full Mode', () => {
    it('renders preset selector', () => {
      render(<PolynomialPlayground />);

      const selector = screen.getByRole('combobox');
      expect(selector).toBeInTheDocument();
    });

    it('renders traffic_light preset by default', () => {
      render(<PolynomialPlayground />);

      // Check for description (unique text)
      expect(screen.getByText('Classic state machine with timed transitions')).toBeInTheDocument();
      // Check for state labels
      expect(screen.getByText('Stop')).toBeInTheDocument(); // Red description
      expect(screen.getByText('Caution')).toBeInTheDocument(); // Yellow description
      expect(screen.getByText('Go')).toBeInTheDocument(); // Green description
    });

    it('shows teaching callout', () => {
      render(<PolynomialPlayground />);

      expect(screen.getByText(/PolyAgent\[S, A, B\]/)).toBeInTheDocument();
    });

    it('renders input buttons for valid transitions', () => {
      render(<PolynomialPlayground />);

      // Traffic light starts at RED, tick is valid
      expect(screen.getByRole('button', { name: /tick/i })).toBeInTheDocument();
    });

    it('executes transition on input button click', async () => {
      const onStateChange = vi.fn();
      render(<PolynomialPlayground onStateChange={onStateChange} />);

      const tickButton = screen.getByRole('button', { name: /tick/i });
      fireEvent.click(tickButton);

      expect(onStateChange).toHaveBeenCalledWith('GREEN', expect.any(Array));
    });

    it('updates trace after transition', async () => {
      render(<PolynomialPlayground />);

      // Click tick to transition
      const tickButton = screen.getByRole('button', { name: /tick/i });
      fireEvent.click(tickButton);

      // Trace should show transition
      await waitFor(() => {
        expect(screen.getByText(/RED --tick--> GREEN/)).toBeInTheDocument();
      });
    });

    it('resets on reset button click', async () => {
      render(<PolynomialPlayground />);

      // Make a transition first
      const tickButton = screen.getByRole('button', { name: /tick/i });
      fireEvent.click(tickButton);

      // Click reset
      const resetButton = screen.getByRole('button', { name: /reset/i });
      fireEvent.click(resetButton);

      // Should be back to RED
      await waitFor(() => {
        expect(screen.getByText(/Click an input to begin/)).toBeInTheDocument();
      });
    });

    it('changes preset when selector changed', () => {
      render(<PolynomialPlayground />);

      const selector = screen.getByRole('combobox') as HTMLSelectElement;
      fireEvent.change(selector, { target: { value: 'vending_machine' } });

      // After change, vending_machine should be selected
      expect(selector.value).toBe('vending_machine');
    });

    it('renders citizen preset with Right to Rest', () => {
      render(<PolynomialPlayground preset="citizen" />);

      // Check for citizen-specific content (multiple elements mention Right to Rest)
      const rightToRestElements = screen.getAllByText(/Right to Rest/);
      expect(rightToRestElements.length).toBeGreaterThan(0);
    });
  });

  describe('Compact Mode', () => {
    it('renders mini state diagram in compact mode', () => {
      render(<PolynomialPlayground compact />);

      // Should have state circles but not full labels
      expect(screen.queryByText('Traffic Light')).not.toBeInTheDocument();
      // Should still show current state
      expect(screen.getByText(/Current:/)).toBeInTheDocument();
    });
  });
});

// =============================================================================
// OperadWiring Tests
// =============================================================================

describe('OperadWiring', () => {
  describe('Full Mode', () => {
    it('renders operad selector', () => {
      render(<OperadWiring />);

      const selector = screen.getByRole('combobox');
      expect(selector).toBeInTheDocument();
    });

    it('renders TOWN_OPERAD by default', () => {
      render(<OperadWiring />);

      // Check for the description (unique)
      expect(screen.getByText('Grammar of citizen interactions in Agent Town')).toBeInTheDocument();
      // Check that TOWN_OPERAD is selected in combobox
      const selector = screen.getByRole('combobox') as HTMLSelectElement;
      expect(selector.value).toBe('TOWN_OPERAD');
    });

    it('shows operation palette', () => {
      render(<OperadWiring />);

      expect(screen.getByText('greet')).toBeInTheDocument();
      expect(screen.getByText('gossip')).toBeInTheDocument();
      expect(screen.getByText('trade')).toBeInTheDocument();
      expect(screen.getByText('solo')).toBeInTheDocument();
    });

    it('shows law verification indicators', () => {
      render(<OperadWiring />);

      expect(screen.getByText('Identity')).toBeInTheDocument();
      expect(screen.getByText('Associativity')).toBeInTheDocument();
    });

    it('shows composition canvas', () => {
      render(<OperadWiring />);

      expect(screen.getByText(/Drag operations here to compose/)).toBeInTheDocument();
    });

    it('shows teaching callout', () => {
      render(<OperadWiring />);

      expect(screen.getByText(/Operads define the grammar of composition/)).toBeInTheDocument();
    });

    it('changes operad when selector changed', () => {
      render(<OperadWiring />);

      const selector = screen.getByRole('combobox');
      fireEvent.change(selector, { target: { value: 'FLOW_OPERAD' } });

      // After change, FLOW_OPERAD should be selected
      expect((selector as HTMLSelectElement).value).toBe('FLOW_OPERAD');
    });

    it('shows arity badges for operations', () => {
      render(<OperadWiring />);

      // greet has arity 2
      const arityBadges = screen.getAllByText('2');
      expect(arityBadges.length).toBeGreaterThan(0);
    });
  });

  describe('Compact Mode', () => {
    it('renders mini operation badges in compact mode', () => {
      render(<OperadWiring compact />);

      // Should show operations but not full canvas
      expect(screen.getByText('greet')).toBeInTheDocument();
      expect(screen.queryByText(/Drag operations here/)).not.toBeInTheDocument();
    });

    it('shows law indicators in compact mode', () => {
      render(<OperadWiring compact />);

      expect(screen.getByText('Identity')).toBeInTheDocument();
    });
  });
});

// =============================================================================
// TownLive Tests
// =============================================================================

describe('TownLive', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('Full Mode', () => {
    it('renders town header with ID', () => {
      render(<TownLive townId="test-town" />);

      expect(screen.getByText(/Town: test-town/)).toBeInTheDocument();
    });

    it('shows phase indicator', () => {
      render(<TownLive phase="MORNING" />);

      expect(screen.getByText('MORNING')).toBeInTheDocument();
    });

    it('shows day counter', () => {
      render(<TownLive day={3} />);

      expect(screen.getByText(/Day 3/)).toBeInTheDocument();
    });

    it('renders default citizens', () => {
      render(<TownLive />);

      expect(screen.getByText('Socrates')).toBeInTheDocument();
      expect(screen.getByText('Hypatia')).toBeInTheDocument();
      expect(screen.getByText('Marcus')).toBeInTheDocument();
    });

    it('shows citizen phases', () => {
      render(<TownLive />);

      // Default demo has various phases
      expect(screen.getByText('active')).toBeInTheDocument();
      expect(screen.getByText('working')).toBeInTheDocument();
    });

    it('shows event feed', () => {
      render(<TownLive />);

      expect(screen.getByText('Event Feed')).toBeInTheDocument();
      expect(screen.getByText(/Socrates greeted Marcus/)).toBeInTheDocument();
    });

    it('shows play/pause button', () => {
      render(<TownLive />);

      expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument();
    });

    it('toggles play state on button click', () => {
      vi.useRealTimers(); // Need real timers for this test
      render(<TownLive />);

      const playButton = screen.getByRole('button', { name: /play/i });
      fireEvent.click(playButton);

      // After click, button should show Pause
      expect(screen.getByRole('button', { name: /pause/i })).toBeInTheDocument();
    });

    it('shows speed selector', () => {
      render(<TownLive />);

      const speedSelector = screen.getByRole('combobox');
      expect(speedSelector).toBeInTheDocument();
      expect(screen.getByText('1x')).toBeInTheDocument();
    });

    it('shows teaching callout', () => {
      render(<TownLive />);

      expect(screen.getByText(/Polynomial agents in motion/)).toBeInTheDocument();
    });

    it('shows connection status', () => {
      render(<TownLive />);

      expect(screen.getByText(/Not connected/)).toBeInTheDocument();
    });
  });

  describe('Compact Mode', () => {
    it('renders mini citizen circles in compact mode', () => {
      render(<TownLive compact />);

      // Should show citizen initials as circles
      expect(screen.getByTitle(/Socrates/)).toBeInTheDocument();
    });

    it('shows phase in compact mode', () => {
      render(<TownLive compact phase="AFTERNOON" />);

      expect(screen.getByText('AFTERNOON')).toBeInTheDocument();
    });

    it('hides event feed in compact mode', () => {
      render(<TownLive compact />);

      expect(screen.queryByText('Event Feed')).not.toBeInTheDocument();
    });
  });

  describe('Streaming Simulation', () => {
    it('starts in paused state with demo events', () => {
      render(<TownLive />);

      // Should show initial demo events
      const events = screen.getAllByText(/\[\d+\]/);
      expect(events.length).toBeGreaterThanOrEqual(3);
    });
  });
});

// =============================================================================
// Integration Tests
// =============================================================================

describe('Interactive Pilots Integration', () => {
  it('all pilots render without errors', () => {
    expect(() => render(<PolynomialPlayground />)).not.toThrow();
    expect(() => render(<OperadWiring />)).not.toThrow();
    expect(() => render(<TownLive />)).not.toThrow();
  });

  it('all pilots support compact mode', () => {
    expect(() => render(<PolynomialPlayground compact />)).not.toThrow();
    expect(() => render(<OperadWiring compact />)).not.toThrow();
    expect(() => render(<TownLive compact />)).not.toThrow();
  });
});
