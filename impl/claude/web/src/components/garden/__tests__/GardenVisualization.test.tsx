/**
 * Tests for Garden visualization components.
 *
 * @see impl/claude/web/src/components/garden/
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { GardenVisualization, GardenCompact } from '../GardenVisualization';
import { SeasonIndicator, SeasonBadge } from '../SeasonIndicator';
import { PlotCard, PlotListItem } from '../PlotCard';
import { GestureHistory, GestureList } from '../GestureHistory';
import type { GardenJSON, PlotJSON, GestureJSON } from '@/reactive/types';

// =============================================================================
// Test Fixtures
// =============================================================================

const mockPlot: PlotJSON = {
  name: 'forge',
  path: 'world.atelier',
  description: 'Creative workshop for artifact creation',
  plan_path: null,
  crown_jewel: 'Atelier',
  prompts: [],
  season_override: null,
  rigidity: 0.4,
  progress: 0.65,
  created_at: '2024-12-15T10:00:00Z',
  last_tended: '2024-12-16T09:30:00Z',
  tags: ['creation', 'artifacts'],
  metadata: {},
};

const mockGesture: GestureJSON = {
  verb: 'WATER',
  target: 'concept.prompt.task.improve',
  tone: 0.7,
  reasoning: 'Nurturing the prompt with TextGRAD',
  entropy_cost: 0.1,
  timestamp: '2024-12-16T10:30:00Z',
  observer: 'default',
  session_id: null,
  result_summary: 'success',
};

const mockGarden: GardenJSON = {
  type: 'garden',
  garden_id: 'test-garden-001',
  name: 'Test Garden',
  created_at: '2024-12-10T08:00:00Z',
  season: 'SPROUTING',
  season_since: '2024-12-15T12:00:00Z',
  plots: { atelier: mockPlot },
  active_plot: null,
  session_id: null,
  memory_crystals: [],
  prompt_count: 5,
  prompt_types: { task: 3, system: 2 },
  recent_gestures: [mockGesture],
  last_tended: '2024-12-16T10:30:00Z',
  metrics: {
    health_score: 0.75,
    total_prompts: 5,
    active_plots: 1,
    entropy_spent: 0.3,
    entropy_budget: 1.0,
  },
  computed: {
    health_score: 0.75,
    entropy_remaining: 0.7,
    entropy_percentage: 0.7,
    active_plot_count: 1,
    total_plot_count: 1,
    season_plasticity: 0.9,
    season_entropy_multiplier: 1.5,
  },
};

// =============================================================================
// SeasonIndicator Tests
// =============================================================================

describe('SeasonIndicator', () => {
  it('renders season name and emoji', () => {
    render(
      <SeasonIndicator
        season="SPROUTING"
        plasticity={0.9}
        entropyMultiplier={1.5}
      />
    );

    expect(screen.getByText('SPROUTING')).toBeInTheDocument();
    expect(screen.getByText('New ideas emerging')).toBeInTheDocument();
  });

  it('displays plasticity percentage', () => {
    render(
      <SeasonIndicator
        season="DORMANT"
        plasticity={0.1}
        entropyMultiplier={0.5}
      />
    );

    expect(screen.getByText('10%')).toBeInTheDocument();
  });

  it('displays entropy multiplier', () => {
    render(
      <SeasonIndicator
        season="BLOOMING"
        plasticity={0.3}
        entropyMultiplier={1.0}
      />
    );

    expect(screen.getByText('1.0x')).toBeInTheDocument();
  });

  it('shows time in season when provided', () => {
    const recentDate = new Date();
    recentDate.setHours(recentDate.getHours() - 2);

    render(
      <SeasonIndicator
        season="HARVEST"
        plasticity={0.2}
        entropyMultiplier={0.8}
        seasonSince={recentDate.toISOString()}
      />
    );

    expect(screen.getByText('In season')).toBeInTheDocument();
  });
});

describe('SeasonBadge', () => {
  it('renders compact season badge', () => {
    render(<SeasonBadge season="COMPOSTING" />);

    expect(screen.getByText('COMPOSTING')).toBeInTheDocument();
  });
});

// =============================================================================
// PlotCard Tests
// =============================================================================

describe('PlotCard', () => {
  it('renders plot information', () => {
    render(
      <PlotCard
        plot={mockPlot}
        isActive={false}
        gardenSeason="SPROUTING"
      />
    );

    expect(screen.getByText('Atelier')).toBeInTheDocument();
    expect(screen.getByText('Creative workshop for artifact creation')).toBeInTheDocument();
  });

  it('shows crown jewel indicator', () => {
    render(
      <PlotCard
        plot={mockPlot}
        isActive={false}
        gardenSeason="SPROUTING"
      />
    );

    expect(screen.getByText(/Crown Jewel: Atelier/)).toBeInTheDocument();
  });

  it('displays progress percentage', () => {
    render(
      <PlotCard
        plot={mockPlot}
        isActive={false}
        gardenSeason="SPROUTING"
      />
    );

    expect(screen.getByText('65%')).toBeInTheDocument();
  });

  it('highlights active plot', () => {
    const { container } = render(
      <PlotCard
        plot={mockPlot}
        isActive={true}
        gardenSeason="SPROUTING"
      />
    );

    const button = container.querySelector('button');
    expect(button).toHaveClass('border-green-500');
  });

  it('calls onSelect when clicked', () => {
    const onSelect = vi.fn();

    render(
      <PlotCard
        plot={mockPlot}
        isActive={false}
        gardenSeason="SPROUTING"
        onSelect={onSelect}
      />
    );

    fireEvent.click(screen.getByRole('button'));
    expect(onSelect).toHaveBeenCalledWith('forge');
  });

  it('shows tags', () => {
    render(
      <PlotCard
        plot={mockPlot}
        isActive={false}
        gardenSeason="SPROUTING"
      />
    );

    expect(screen.getByText('creation')).toBeInTheDocument();
    expect(screen.getByText('artifacts')).toBeInTheDocument();
  });
});

describe('PlotListItem', () => {
  it('renders compact plot info', () => {
    render(
      <PlotListItem
        plot={mockPlot}
        isActive={false}
      />
    );

    expect(screen.getByText('Atelier')).toBeInTheDocument();
    expect(screen.getByText('65%')).toBeInTheDocument();
  });
});

// =============================================================================
// GestureHistory Tests
// =============================================================================

describe('GestureHistory', () => {
  it('renders gesture list', () => {
    render(<GestureHistory gestures={[mockGesture]} />);

    expect(screen.getByText('WATER')).toBeInTheDocument();
    expect(screen.getByText('concept.prompt.task.improve')).toBeInTheDocument();
  });

  it('shows empty state when no gestures', () => {
    render(<GestureHistory gestures={[]} />);

    expect(screen.getByText('No gestures yet')).toBeInTheDocument();
    expect(screen.getByText('Start tending your garden')).toBeInTheDocument();
  });

  it('displays gesture reasoning', () => {
    render(<GestureHistory gestures={[mockGesture]} />);

    expect(screen.getByText('Nurturing the prompt with TextGRAD')).toBeInTheDocument();
  });

  it('shows gesture metrics', () => {
    render(<GestureHistory gestures={[mockGesture]} />);

    expect(screen.getByText('Tone: 70%')).toBeInTheDocument();
    expect(screen.getByText('Entropy: 0.100')).toBeInTheDocument();
  });

  it('limits displayed gestures', () => {
    const gestures = Array(15)
      .fill(null)
      .map((_, i) => ({
        ...mockGesture,
        timestamp: new Date(Date.now() - i * 60000).toISOString(),
      }));

    render(<GestureHistory gestures={gestures} maxDisplay={5} />);

    // Should only show 5 items
    const items = screen.getAllByText('WATER');
    expect(items.length).toBe(5);
  });
});

describe('GestureList', () => {
  it('renders compact gesture list', () => {
    render(<GestureList gestures={[mockGesture]} />);

    expect(screen.getByText('water')).toBeInTheDocument();
  });

  it('shows empty state for no gestures', () => {
    render(<GestureList gestures={[]} />);

    expect(screen.getByText('No recent gestures')).toBeInTheDocument();
  });
});

// =============================================================================
// GardenVisualization Tests
// =============================================================================

describe('GardenVisualization', () => {
  it('renders garden header with name', () => {
    render(<GardenVisualization garden={mockGarden} />);

    expect(screen.getByText('Test Garden')).toBeInTheDocument();
  });

  it('displays health score', () => {
    render(<GardenVisualization garden={mockGarden} />);

    // Health should appear in header and metrics
    expect(screen.getAllByText('75%').length).toBeGreaterThan(0);
  });

  it('shows season badge', () => {
    render(<GardenVisualization garden={mockGarden} />);

    expect(screen.getByText('SPROUTING')).toBeInTheDocument();
  });

  it('renders season indicator with metrics', () => {
    render(<GardenVisualization garden={mockGarden} />);

    // Plasticity should be shown
    expect(screen.getByText('90%')).toBeInTheDocument();
  });

  it('displays entropy budget', () => {
    render(<GardenVisualization garden={mockGarden} />);

    expect(screen.getByText('0.70 / 1.0')).toBeInTheDocument();
  });

  it('renders plot grid', () => {
    render(<GardenVisualization garden={mockGarden} />);

    expect(screen.getByText('Plots (1/1 active)')).toBeInTheDocument();
  });

  it('shows gesture history', () => {
    render(<GardenVisualization garden={mockGarden} />);

    expect(screen.getByText('Recent Gestures')).toBeInTheDocument();
  });

  it('calls onTend when tending action clicked', async () => {
    const onTend = vi.fn();

    render(<GardenVisualization garden={mockGarden} onTend={onTend} />);

    // Click on the OBSERVE action
    const observeButton = screen.getByText('Observe');
    fireEvent.click(observeButton);

    expect(onTend).toHaveBeenCalledWith('OBSERVE', 'concept.gardener', undefined);
  });

  it('calls onPlotSelect when plot clicked', () => {
    const onPlotSelect = vi.fn();

    render(<GardenVisualization garden={mockGarden} onPlotSelect={onPlotSelect} />);

    // Click on the plot card
    fireEvent.click(screen.getByText('Atelier'));

    expect(onPlotSelect).toHaveBeenCalledWith('forge');
  });
});

describe('GardenCompact', () => {
  it('renders compact garden widget', () => {
    render(<GardenCompact garden={mockGarden} />);

    expect(screen.getByText('Test Garden')).toBeInTheDocument();
    expect(screen.getByText('SPROUTING')).toBeInTheDocument();
    expect(screen.getByText(/Health: 75%/)).toBeInTheDocument();
  });

  it('shows plot list', () => {
    render(<GardenCompact garden={mockGarden} />);

    expect(screen.getByText('Atelier')).toBeInTheDocument();
  });

  it('shows recent gestures section', () => {
    render(<GardenCompact garden={mockGarden} />);

    expect(screen.getByText('Recent gestures')).toBeInTheDocument();
  });
});
