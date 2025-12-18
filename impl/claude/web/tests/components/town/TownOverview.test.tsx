/**
 * Tests for TownOverview component.
 *
 * T-gent Type I: Contracts - Component renders expected content
 * T-gent Type II: Saboteurs - Component handles bad data
 * T-gent Type III: Spies - Component navigation and interactions
 *
 * @see impl/claude/web/src/components/town/TownOverview.tsx
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { TownOverview } from '@/components/town/TownOverview';
import * as hooks from '@/hooks';

// Mock hooks
vi.mock('@/hooks', () => ({
  useTownManifest: vi.fn(),
  useCitizens: vi.fn(),
  useCoalitionManifest: vi.fn(),
  useCoalitions: vi.fn(),
}));

// Mock router
const mockNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}));

// Mock shell provider
vi.mock('@/shell/ShellProvider', () => ({
  useShell: () => ({ density: 'comfortable' }),
}));

// =============================================================================
// Test Fixtures
// =============================================================================

const mockTownManifest = {
  total_citizens: 10,
  active_citizens: 7,
  total_conversations: 25,
  active_conversations: 5,
  total_relationships: 30,
  storage_backend: 'sqlite',
};

const mockCitizens = {
  citizens: [
    {
      id: 'citizen-1',
      name: 'Alice',
      archetype: 'builder',
      is_active: true,
      interaction_count: 15,
    },
    {
      id: 'citizen-2',
      name: 'Bob',
      archetype: 'trader',
      is_active: true,
      interaction_count: 20,
    },
    {
      id: 'citizen-3',
      name: 'Charlie',
      archetype: 'healer',
      is_active: false,
      interaction_count: 8,
    },
  ],
};

const mockCoalitionManifest = {
  total_coalitions: 3,
  bridge_citizens: 2,
  avg_strength: 0.75,
};

const mockCoalitions = {
  coalitions: [
    {
      id: 'coalition-1',
      name: 'Builders Guild',
      member_count: 4,
      strength: 0.85,
      purpose: 'Building and creating',
    },
    {
      id: 'coalition-2',
      name: 'Trade Network',
      member_count: 3,
      strength: 0.65,
      purpose: 'Trading and exchange',
    },
  ],
};

// =============================================================================
// T-gent Type I: Contracts - Component renders expected content
// =============================================================================

describe('TownOverview - Contracts', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    (hooks.useTownManifest as any).mockReturnValue({
      data: mockTownManifest,
      isLoading: false,
      error: null,
    });

    (hooks.useCitizens as any).mockReturnValue({
      data: mockCitizens,
      isLoading: false,
      error: null,
    });

    (hooks.useCoalitionManifest as any).mockReturnValue({
      data: mockCoalitionManifest,
      isLoading: false,
      error: null,
    });

    (hooks.useCoalitions as any).mockReturnValue({
      data: mockCoalitions,
      isLoading: false,
      error: null,
    });
  });

  it('renders page header', () => {
    render(<TownOverview />);

    expect(screen.getByText('Agent Town')).toBeInTheDocument();
    expect(screen.getByText('Coalition Crown Jewel')).toBeInTheDocument();
  });

  it('displays total citizens stat', () => {
    render(<TownOverview />);

    expect(screen.getByText('Total Citizens')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
    expect(screen.getByText('7 active')).toBeInTheDocument();
  });

  it('displays conversations stat', () => {
    render(<TownOverview />);

    expect(screen.getByText('Conversations')).toBeInTheDocument();
    expect(screen.getByText('25')).toBeInTheDocument();
    expect(screen.getByText('5 active')).toBeInTheDocument();
  });

  it('displays coalitions stat', () => {
    render(<TownOverview />);

    expect(screen.getByText('Coalitions')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('2 bridges')).toBeInTheDocument();
  });

  it('displays relationships stat', () => {
    render(<TownOverview />);

    expect(screen.getByText('Relationships')).toBeInTheDocument();
    expect(screen.getByText('30')).toBeInTheDocument();
    expect(screen.getByText(/Avg strength: 75%/)).toBeInTheDocument();
  });

  it('renders citizen list section', () => {
    render(<TownOverview />);

    expect(screen.getByText('Citizens')).toBeInTheDocument();
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Bob')).toBeInTheDocument();
    expect(screen.getByText('Charlie')).toBeInTheDocument();
  });

  it('shows citizen archetype for each citizen', () => {
    render(<TownOverview />);

    expect(screen.getByText('builder')).toBeInTheDocument();
    expect(screen.getByText('trader')).toBeInTheDocument();
    expect(screen.getByText('healer')).toBeInTheDocument();
  });

  it('displays citizen interaction counts', () => {
    render(<TownOverview />);

    expect(screen.getByText('15')).toBeInTheDocument();
    expect(screen.getByText('20')).toBeInTheDocument();
    expect(screen.getByText('8')).toBeInTheDocument();
  });

  it('shows active status for citizens', () => {
    const { container } = render(<TownOverview />);

    // Check for active/inactive indicators (green/gray dots)
    const dots = container.querySelectorAll('.bg-green-400, .bg-gray-500');
    expect(dots.length).toBeGreaterThan(0);
  });

  it('renders coalition list section', () => {
    render(<TownOverview />);

    expect(screen.getByText('Coalitions')).toBeInTheDocument();
    expect(screen.getByText('Builders Guild')).toBeInTheDocument();
    expect(screen.getByText('Trade Network')).toBeInTheDocument();
  });

  it('shows coalition member counts', () => {
    render(<TownOverview />);

    expect(screen.getByText('4 members')).toBeInTheDocument();
    expect(screen.getByText('3 members')).toBeInTheDocument();
  });

  it('displays coalition purposes', () => {
    render(<TownOverview />);

    expect(screen.getByText('Building and creating')).toBeInTheDocument();
    expect(screen.getByText('Trading and exchange')).toBeInTheDocument();
  });

  it('shows coalition strength percentages', () => {
    render(<TownOverview />);

    expect(screen.getByText('85%')).toBeInTheDocument();
    expect(screen.getByText('65%')).toBeInTheDocument();
  });

  it('displays storage backend info', () => {
    render(<TownOverview />);

    expect(screen.getByText(/Storage:/)).toBeInTheDocument();
    expect(screen.getByText('sqlite')).toBeInTheDocument();
  });

  it('shows Run Simulation button', () => {
    render(<TownOverview />);

    expect(screen.getByText('Run Simulation')).toBeInTheDocument();
  });

  it('limits citizen list to 5 items', () => {
    const manyCitizens = {
      citizens: Array(10).fill(null).map((_, i) => ({
        id: `citizen-${i}`,
        name: `Citizen ${i}`,
        archetype: 'builder',
        is_active: true,
        interaction_count: 10,
      })),
    };

    (hooks.useCitizens as any).mockReturnValue({
      data: manyCitizens,
      isLoading: false,
      error: null,
    });

    render(<TownOverview />);

    // Should only render first 5
    expect(screen.getByText('Citizen 0')).toBeInTheDocument();
    expect(screen.getByText('Citizen 4')).toBeInTheDocument();
    expect(screen.queryByText('Citizen 5')).not.toBeInTheDocument();
  });

  it('limits coalition list to 4 items', () => {
    const manyCoalitions = {
      coalitions: Array(8).fill(null).map((_, i) => ({
        id: `coalition-${i}`,
        name: `Coalition ${i}`,
        member_count: 3,
        strength: 0.7,
        purpose: `Purpose ${i}`,
      })),
    };

    (hooks.useCoalitions as any).mockReturnValue({
      data: manyCoalitions,
      isLoading: false,
      error: null,
    });

    render(<TownOverview />);

    // Should only render first 4
    expect(screen.getByText('Coalition 0')).toBeInTheDocument();
    expect(screen.getByText('Coalition 3')).toBeInTheDocument();
    expect(screen.queryByText('Coalition 4')).not.toBeInTheDocument();
  });
});

// =============================================================================
// T-gent Type II: Saboteurs - Component handles bad data
// =============================================================================

describe('TownOverview - Saboteurs', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading skeleton while data loads', () => {
    (hooks.useTownManifest as any).mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    });

    (hooks.useCitizens as any).mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    });

    (hooks.useCoalitionManifest as any).mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    });

    (hooks.useCoalitions as any).mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    });

    const { container } = render(<TownOverview />);

    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('displays error banner when manifest fails to load', () => {
    (hooks.useTownManifest as any).mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error('Failed to fetch manifest'),
    });

    (hooks.useCitizens as any).mockReturnValue({
      data: mockCitizens,
      isLoading: false,
      error: null,
    });

    (hooks.useCoalitionManifest as any).mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    });

    (hooks.useCoalitions as any).mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    });

    render(<TownOverview />);

    expect(screen.getByText('Error loading data')).toBeInTheDocument();
    expect(screen.getByText('Failed to fetch manifest')).toBeInTheDocument();
  });

  it('shows empty state when no citizens exist', () => {
    (hooks.useTownManifest as any).mockReturnValue({
      data: mockTownManifest,
      isLoading: false,
      error: null,
    });

    (hooks.useCitizens as any).mockReturnValue({
      data: { citizens: [] },
      isLoading: false,
      error: null,
    });

    (hooks.useCoalitionManifest as any).mockReturnValue({
      data: mockCoalitionManifest,
      isLoading: false,
      error: null,
    });

    (hooks.useCoalitions as any).mockReturnValue({
      data: mockCoalitions,
      isLoading: false,
      error: null,
    });

    render(<TownOverview />);

    expect(screen.getByText('No citizens yet')).toBeInTheDocument();
    expect(screen.getByText('Run a simulation to create citizens')).toBeInTheDocument();
  });

  it('shows empty state when no coalitions exist', () => {
    (hooks.useTownManifest as any).mockReturnValue({
      data: mockTownManifest,
      isLoading: false,
      error: null,
    });

    (hooks.useCitizens as any).mockReturnValue({
      data: mockCitizens,
      isLoading: false,
      error: null,
    });

    (hooks.useCoalitionManifest as any).mockReturnValue({
      data: mockCoalitionManifest,
      isLoading: false,
      error: null,
    });

    (hooks.useCoalitions as any).mockReturnValue({
      data: { coalitions: [] },
      isLoading: false,
      error: null,
    });

    render(<TownOverview />);

    expect(screen.getByText('No coalitions detected')).toBeInTheDocument();
    expect(screen.getByText('Coalitions form from citizen interactions')).toBeInTheDocument();
  });

  it('handles missing optional data gracefully', () => {
    (hooks.useTownManifest as any).mockReturnValue({
      data: {
        total_citizens: 5,
        // Missing optional fields
      },
      isLoading: false,
      error: null,
    });

    (hooks.useCitizens as any).mockReturnValue({
      data: mockCitizens,
      isLoading: false,
      error: null,
    });

    (hooks.useCoalitionManifest as any).mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    });

    (hooks.useCoalitions as any).mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    });

    render(<TownOverview />);

    expect(screen.getByText('Agent Town')).toBeInTheDocument();
  });
});

// =============================================================================
// T-gent Type III: Spies - Component navigation and interactions
// =============================================================================

describe('TownOverview - Spies', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    (hooks.useTownManifest as any).mockReturnValue({
      data: mockTownManifest,
      isLoading: false,
      error: null,
    });

    (hooks.useCitizens as any).mockReturnValue({
      data: mockCitizens,
      isLoading: false,
      error: null,
    });

    (hooks.useCoalitionManifest as any).mockReturnValue({
      data: mockCoalitionManifest,
      isLoading: false,
      error: null,
    });

    (hooks.useCoalitions as any).mockReturnValue({
      data: mockCoalitions,
      isLoading: false,
      error: null,
    });
  });

  it('navigates to simulation page when Run Simulation clicked', () => {
    render(<TownOverview />);

    const simulationButton = screen.getByText('Run Simulation');
    fireEvent.click(simulationButton);

    expect(mockNavigate).toHaveBeenCalledWith('/town/simulation');
  });

  it('navigates to citizen detail page when citizen clicked', () => {
    render(<TownOverview />);

    const aliceCard = screen.getByText('Alice').closest('button');
    if (aliceCard) {
      fireEvent.click(aliceCard);
    }

    expect(mockNavigate).toHaveBeenCalledWith('/town/citizens/citizen-1');
  });

  it('navigates to coalition detail page when coalition clicked', () => {
    render(<TownOverview />);

    const coalitionCard = screen.getByText('Builders Guild').closest('button');
    if (coalitionCard) {
      fireEvent.click(coalitionCard);
    }

    expect(mockNavigate).toHaveBeenCalledWith('/town/coalitions/coalition-1');
  });

  it('navigates to citizens list when View all clicked in Citizens section', () => {
    render(<TownOverview />);

    const viewAllButtons = screen.getAllByText('View all');
    fireEvent.click(viewAllButtons[0]); // First "View all" is for Citizens

    expect(mockNavigate).toHaveBeenCalledWith('/town/citizens');
  });

  it('navigates to coalitions list when View all clicked in Coalitions section', () => {
    render(<TownOverview />);

    const viewAllButtons = screen.getAllByText('View all');
    fireEvent.click(viewAllButtons[1]); // Second "View all" is for Coalitions

    expect(mockNavigate).toHaveBeenCalledWith('/town/coalitions');
  });

  it('navigates to citizens list when Total Citizens stat clicked', () => {
    render(<TownOverview />);

    const citizensStat = screen.getByText('Total Citizens').closest('div');
    if (citizensStat) {
      fireEvent.click(citizensStat);
    }

    expect(mockNavigate).toHaveBeenCalledWith('/town/citizens');
  });

  it('navigates to coalitions list when Coalitions stat clicked', () => {
    render(<TownOverview />);

    const coalitionsStat = screen.getByText('Coalitions').closest('div');
    if (coalitionsStat) {
      fireEvent.click(coalitionsStat);
    }

    expect(mockNavigate).toHaveBeenCalledWith('/town/coalitions');
  });
});
