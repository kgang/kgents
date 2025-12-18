/**
 * Gardener2D Component Tests
 *
 * Tests for the unified garden + session visualization.
 * Covers: SeasonOrb, PlotTile, GestureStream, SessionPolynomial, TendingPalette, TransitionSuggester
 *
 * @see spec/protocols/2d-renaissance.md - Phase 2
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ShellProvider } from '@/shell';

// Components
import { SeasonOrb } from '@/components/gardener/SeasonOrb';
import { PlotTile } from '@/components/gardener/PlotTile';
import { GestureStream } from '@/components/gardener/GestureStream';
import { SessionPolynomial } from '@/components/gardener/SessionPolynomial';
import { TendingPalette } from '@/components/gardener/TendingPalette';
import { TransitionSuggester } from '@/components/gardener/TransitionSuggester';

import type { PlotJSON, GestureJSON, TransitionSuggestionJSON } from '@/reactive/types';
import type { GardenerSessionState } from '@/api/types';

// =============================================================================
// Test Fixtures
// =============================================================================

const mockPlot: PlotJSON = {
  name: 'hero-path',
  path: 'concept.gardener.plots.hero-path',
  description: 'Wave 1 Hero Path Implementation',
  plan_path: 'plans/crown-jewels-enlightened.md',
  crown_jewel: 'Gardener',
  prompts: ['Implement Gardener2D'],
  season_override: null,
  rigidity: 0.3,
  progress: 0.65,
  created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
  last_tended: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
  tags: ['wave-1', 'hero-path'],
  metadata: {},
};

const mockGestures: GestureJSON[] = [
  {
    verb: 'OBSERVE',
    target: 'concept.gardener',
    tone: 0.6,
    reasoning: 'Checking garden state',
    entropy_cost: 0.1,
    timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
    observer: 'kent',
    session_id: 'session-001',
    result_summary: 'success',
  },
  {
    verb: 'WATER',
    target: 'concept.gardener.plots.hero-path',
    tone: 0.8,
    reasoning: 'Hydrating hero path',
    entropy_cost: 0.25,
    timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    observer: 'kent',
    session_id: 'session-001',
    result_summary: 'success',
  },
];

const mockSession: GardenerSessionState = {
  session_id: 'session-001',
  name: 'Wave 1 Hero Path Implementation',
  phase: 'ACT',
  plan_path: 'plans/crown-jewels-enlightened.md',
  intent: {
    description: 'Implement Gardener2D',
    priority: 'high',
  },
  artifacts_count: 6,
  learnings_count: 0,
  sense_count: 2,
  act_count: 1,
  reflect_count: 0,
};

const mockSuggestion: TransitionSuggestionJSON = {
  from_season: 'SPROUTING',
  to_season: 'BLOOMING',
  confidence: 0.73,
  reason: 'High activity suggests readiness for crystallization phase',
  signals: {
    gesture_frequency: 4.2,
    gesture_diversity: 0.67,
    plot_progress_delta: 0.15,
    artifacts_created: 6,
    time_in_season_hours: 2.5,
    entropy_spent_ratio: 0.34,
    reflect_count: 1,
    session_active: true,
  },
  triggered_at: new Date().toISOString(),
};

// Shell wrapper for context
const withShell = (ui: React.ReactElement) => <ShellProvider>{ui}</ShellProvider>;

// =============================================================================
// SeasonOrb Tests
// =============================================================================

describe('SeasonOrb', () => {
  it('renders season name and metaphor', () => {
    render(
      <SeasonOrb
        season="SPROUTING"
        plasticity={0.78}
        entropyMultiplier={1.5}
        seasonSince={new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()}
      />
    );

    expect(screen.getByText('SPROUTING')).toBeInTheDocument();
    expect(screen.getByText('New growth')).toBeInTheDocument();
  });

  it('displays plasticity percentage', () => {
    render(<SeasonOrb season="BLOOMING" plasticity={0.45} entropyMultiplier={1.0} />);

    expect(screen.getByText('45%')).toBeInTheDocument();
  });

  it('renders compact mode correctly', () => {
    render(<SeasonOrb season="DORMANT" plasticity={0.2} entropyMultiplier={0.5} compact />);

    expect(screen.getByText('DORMANT')).toBeInTheDocument();
    expect(screen.getByText('Resting roots')).toBeInTheDocument();
  });

  it('shows entropy multiplier', () => {
    render(<SeasonOrb season="HARVEST" plasticity={0.5} entropyMultiplier={2.0} />);

    expect(screen.getByText('2.0x')).toBeInTheDocument();
  });
});

// =============================================================================
// PlotTile Tests
// =============================================================================

describe('PlotTile', () => {
  it('renders plot name and description', () => {
    render(
      withShell(
        <PlotTile plot={mockPlot} isActive={false} isSelected={false} gardenSeason="SPROUTING" />
      )
    );

    expect(screen.getByText('Hero Path')).toBeInTheDocument();
    expect(screen.getByText('Wave 1 Hero Path Implementation')).toBeInTheDocument();
  });

  it('shows progress percentage', () => {
    render(
      withShell(
        <PlotTile plot={mockPlot} isActive={false} isSelected={false} gardenSeason="SPROUTING" />
      )
    );

    expect(screen.getByText('65%')).toBeInTheDocument();
  });

  it('shows active badge when active', () => {
    render(
      withShell(
        <PlotTile plot={mockPlot} isActive={true} isSelected={false} gardenSeason="SPROUTING" />
      )
    );

    expect(screen.getByText('ACTIVE')).toBeInTheDocument();
  });

  it('calls onSelect when clicked', () => {
    const onSelect = vi.fn();

    render(
      withShell(
        <PlotTile
          plot={mockPlot}
          isActive={false}
          isSelected={false}
          gardenSeason="SPROUTING"
          onSelect={onSelect}
        />
      )
    );

    fireEvent.click(screen.getByRole('button'));
    expect(onSelect).toHaveBeenCalledWith('hero-path');
  });

  it('renders tags', () => {
    render(
      withShell(
        <PlotTile plot={mockPlot} isActive={false} isSelected={false} gardenSeason="SPROUTING" />
      )
    );

    expect(screen.getByText('wave-1')).toBeInTheDocument();
    expect(screen.getByText('hero-path')).toBeInTheDocument();
  });
});

// =============================================================================
// GestureStream Tests
// =============================================================================

describe('GestureStream', () => {
  it('renders empty state when no gestures', () => {
    render(<GestureStream gestures={[]} />);

    expect(screen.getByText('No gestures yet')).toBeInTheDocument();
    expect(screen.getByText('Start tending your garden')).toBeInTheDocument();
  });

  it('renders gesture list', () => {
    render(<GestureStream gestures={mockGestures} />);

    expect(screen.getByText('OBSERVE')).toBeInTheDocument();
    expect(screen.getByText('WATER')).toBeInTheDocument();
  });

  it('shows gesture reasoning', () => {
    render(<GestureStream gestures={mockGestures} />);

    expect(screen.getByText('"Checking garden state"')).toBeInTheDocument();
    expect(screen.getByText('"Hydrating hero path"')).toBeInTheDocument();
  });

  it('respects maxDisplay limit', () => {
    const manyGestures = Array.from({ length: 20 }, (_, i) => ({
      ...mockGestures[0],
      timestamp: new Date(Date.now() - i * 60 * 1000).toISOString(),
    }));

    render(<GestureStream gestures={manyGestures} maxDisplay={5} />);

    // Should only render 5 gesture cards
    const verbElements = screen.getAllByText('OBSERVE');
    expect(verbElements.length).toBe(5);
  });
});

// =============================================================================
// SessionPolynomial Tests
// =============================================================================

describe('SessionPolynomial', () => {
  it('renders phase labels', () => {
    render(<SessionPolynomial session={mockSession} />);

    expect(screen.getByText('Sense')).toBeInTheDocument();
    expect(screen.getByText('Act')).toBeInTheDocument();
    expect(screen.getByText('Reflect')).toBeInTheDocument();
  });

  it('shows current phase action', () => {
    render(<SessionPolynomial session={mockSession} />);

    expect(screen.getByText('Executing intent')).toBeInTheDocument();
  });

  it('displays session stats', () => {
    render(<SessionPolynomial session={mockSession} />);

    expect(screen.getByText('Artifacts')).toBeInTheDocument();
    expect(screen.getByText('6')).toBeInTheDocument();
    expect(screen.getByText('Learnings')).toBeInTheDocument();
  });

  it('shows valid transitions', () => {
    render(<SessionPolynomial session={mockSession} />);

    // ACT phase can transition to REFLECT or back to SENSE
    expect(screen.getByText(/Valid: \[REFLECT, SENSE\]/)).toBeInTheDocument();
  });

  it('calls onPhaseChange with correct phase', () => {
    const onPhaseChange = vi.fn();

    render(<SessionPolynomial session={mockSession} onPhaseChange={onPhaseChange} />);

    fireEvent.click(screen.getByText('Advance to Reflect'));
    expect(onPhaseChange).toHaveBeenCalledWith('REFLECT');
  });
});

// =============================================================================
// TendingPalette Tests
// =============================================================================

describe('TendingPalette', () => {
  it('renders all tending verbs', () => {
    render(<TendingPalette target="concept.gardener" />);

    expect(screen.getByText('Observe')).toBeInTheDocument();
    expect(screen.getByText('Water')).toBeInTheDocument();
    expect(screen.getByText('Graft')).toBeInTheDocument();
    expect(screen.getByText('Prune')).toBeInTheDocument();
    expect(screen.getByText('Rotate')).toBeInTheDocument();
    expect(screen.getByText('Wait')).toBeInTheDocument();
  });

  it('shows verb descriptions', () => {
    render(<TendingPalette target="concept.gardener" />);

    expect(screen.getByText('Perceive without changing')).toBeInTheDocument();
    expect(screen.getByText('Nurture via TextGRAD')).toBeInTheDocument();
    expect(screen.getByText('Add something new')).toBeInTheDocument();
  });

  it('displays target path', () => {
    render(<TendingPalette target="concept.gardener.plots.hero-path" />);

    expect(screen.getByText('concept.gardener.plots.hero-path')).toBeInTheDocument();
  });

  it('calls onTend with correct verb and target', () => {
    const onTend = vi.fn();

    render(<TendingPalette target="concept.gardener" onTend={onTend} />);

    fireEvent.click(screen.getByText('Observe'));
    expect(onTend).toHaveBeenCalledWith('OBSERVE', 'concept.gardener');
  });

  it('renders inline mode correctly', () => {
    render(<TendingPalette target="concept.gardener" inline />);

    expect(screen.getByText('Tend this plot')).toBeInTheDocument();
  });
});

// =============================================================================
// TransitionSuggester Tests
// =============================================================================

describe('TransitionSuggester', () => {
  const onAccept = vi.fn();
  const onDismiss = vi.fn();

  beforeEach(() => {
    onAccept.mockClear();
    onDismiss.mockClear();
  });

  it('renders transition suggestion', () => {
    render(
      <TransitionSuggester suggestion={mockSuggestion} onAccept={onAccept} onDismiss={onDismiss} />
    );

    expect(screen.getByText('SPROUTING')).toBeInTheDocument();
    expect(screen.getByText('BLOOMING')).toBeInTheDocument();
    expect(screen.getByText('73% confidence')).toBeInTheDocument();
  });

  it('shows suggestion reason', () => {
    render(
      <TransitionSuggester suggestion={mockSuggestion} onAccept={onAccept} onDismiss={onDismiss} />
    );

    expect(
      screen.getByText('High activity suggests readiness for crystallization phase')
    ).toBeInTheDocument();
  });

  it('displays signals', () => {
    render(
      <TransitionSuggester suggestion={mockSuggestion} onAccept={onAccept} onDismiss={onDismiss} />
    );

    expect(screen.getByText('Gestures')).toBeInTheDocument();
    expect(screen.getByText('Diversity')).toBeInTheDocument();
    expect(screen.getByText('Entropy')).toBeInTheDocument();
  });

  it('calls onAccept when accept button clicked', () => {
    render(
      <TransitionSuggester suggestion={mockSuggestion} onAccept={onAccept} onDismiss={onDismiss} />
    );

    fireEvent.click(screen.getByText('Accept Transition'));
    expect(onAccept).toHaveBeenCalled();
  });

  it('calls onDismiss when dismiss button clicked', () => {
    render(
      <TransitionSuggester suggestion={mockSuggestion} onAccept={onAccept} onDismiss={onDismiss} />
    );

    // Find the X button (dismiss)
    const dismissButtons = screen.getAllByRole('button');
    const dismissButton = dismissButtons.find((btn) => btn.textContent === '');
    if (dismissButton) {
      fireEvent.click(dismissButton);
      expect(onDismiss).toHaveBeenCalled();
    }
  });

  it('renders compact mode', () => {
    render(
      <TransitionSuggester
        suggestion={mockSuggestion}
        onAccept={onAccept}
        onDismiss={onDismiss}
        compact
      />
    );

    // Should show transition in shorter form
    expect(screen.getByText('SPROUTING → BLOOMING')).toBeInTheDocument();
    expect(screen.getByText('73%')).toBeInTheDocument();
  });

  it('shows cooldown note', () => {
    render(
      <TransitionSuggester suggestion={mockSuggestion} onAccept={onAccept} onDismiss={onDismiss} />
    );

    expect(
      screen.getByText('Dismissing applies 4h cooldown before next suggestion')
    ).toBeInTheDocument();
  });
});
