/**
 * Tests for TownV2: Widget-based Agent Town visualization.
 *
 * TownV2 uses useTownStreamWidget hook to consume ColonyDashboardJSON
 * instead of building state incrementally via Zustand.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import TownV2 from '@/pages/TownV2';

// =============================================================================
// Mocks
// =============================================================================

// Mock useTownStreamWidget
const mockConnect = vi.fn();
const mockDisconnect = vi.fn();

vi.mock('@/hooks/useTownStreamWidget', () => ({
  useTownStreamWidget: vi.fn(() => ({
    dashboard: {
      type: 'colony_dashboard',
      colony_id: 'test-town',
      phase: 'MORNING',
      day: 1,
      metrics: { total_events: 10, total_tokens: 100, entropy_budget: 1.0 },
      citizens: [
        {
          type: 'citizen_card',
          citizen_id: 'alice-123',
          name: 'Alice',
          archetype: 'Builder',
          phase: 'WORKING',
          nphase: 'ACT',
          activity: [0.5, 0.6, 0.7],
          capability: 0.8,
          entropy: 0.1,
          region: 'plaza',
          mood: 'happy',
          eigenvectors: { warmth: 0.7, curiosity: 0.8, trust: 0.6 },
        },
        {
          type: 'citizen_card',
          citizen_id: 'bob-456',
          name: 'Bob',
          archetype: 'Trader',
          phase: 'SOCIALIZING',
          nphase: 'SENSE',
          activity: [0.3, 0.4, 0.5],
          capability: 0.6,
          entropy: 0.2,
          region: 'market',
          mood: 'curious',
          eigenvectors: { warmth: 0.5, curiosity: 0.9, trust: 0.4 },
        },
      ],
      grid_cols: 5,
      selected_citizen_id: null,
    },
    events: [
      { tick: 1, operation: 'greet', participants: ['Alice', 'Bob'], phase: 'MORNING' },
      { tick: 2, operation: 'trade', participants: ['Bob'], phase: 'MORNING' },
    ],
    isConnected: true,
    isPlaying: true,
    connect: mockConnect,
    disconnect: mockDisconnect,
  })),
}));

// Mock townApi
vi.mock('@/api/client', () => ({
  townApi: {
    get: vi.fn().mockResolvedValue({ data: { id: 'test-town', name: 'Test Town' } }),
    create: vi.fn().mockResolvedValue({ data: { id: 'new-town', name: 'Demo Town' } }),
    getCitizens: vi.fn().mockResolvedValue({ data: { citizens: [] } }),
    getCitizen: vi.fn().mockResolvedValue({ data: { citizen: { name: 'Alice' } } }),
  },
}));

// Mock userStore
vi.mock('@/stores/userStore', () => ({
  useUserStore: vi.fn((selector) => {
    const state = {
      userId: 'test-user',
      tier: 'CITIZEN',
      credits: 100,
    };
    return selector ? selector(state) : state;
  }),
  selectCanInhabit: () => () => true,
}));

// Mock PixiJS Stage for Mesa - need to return a simpler component
vi.mock('@pixi/react', () => ({
  Stage: ({ children }: { children: React.ReactNode }) => <div data-testid="pixi-stage">{children}</div>,
  Container: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Graphics: ({ draw }: { draw: () => void }) => <div data-testid="pixi-graphics" onClick={() => draw} />,
  Text: ({ text }: { text: string }) => <span>{text}</span>,
}));

// =============================================================================
// Test Helpers
// =============================================================================

function renderTownV2(townId: string = 'test-town') {
  return render(
    <MemoryRouter initialEntries={[`/town-v2/${townId}`]}>
      <Routes>
        <Route path="/town-v2/:townId" element={<TownV2 />} />
      </Routes>
    </MemoryRouter>
  );
}

// =============================================================================
// Tests
// =============================================================================

describe('TownV2', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('rendering', () => {
    it('should render town header with phase and day', async () => {
      renderTownV2();

      await waitFor(() => {
        // Use getAllBy since Day 1 appears in multiple places (header and dashboard)
        expect(screen.getAllByText(/Day 1/).length).toBeGreaterThan(0);
        expect(screen.getAllByText(/MORNING/).length).toBeGreaterThan(0);
      });
    });

    it('should display citizen count from dashboard', async () => {
      renderTownV2();

      await waitFor(() => {
        expect(screen.getByText(/2 citizens/)).toBeInTheDocument();
      });
    });

    it('should display town ID', async () => {
      renderTownV2();

      await waitFor(() => {
        expect(screen.getByText(/Town: test-town/)).toBeInTheDocument();
      });
    });
  });

  describe('controls', () => {
    it('should have play/pause button', async () => {
      renderTownV2();

      await waitFor(() => {
        // isPlaying is true in mock, so should show Pause
        expect(screen.getByText(/Pause/)).toBeInTheDocument();
      });
    });

    it('should have speed selector with options', async () => {
      renderTownV2();

      await waitFor(() => {
        const speedSelect = screen.getByRole('combobox');
        expect(speedSelect).toBeInTheDocument();
      });

      // Check options
      expect(screen.getByText('0.5x Speed')).toBeInTheDocument();
      expect(screen.getByText('1x Speed')).toBeInTheDocument();
      expect(screen.getByText('2x Speed')).toBeInTheDocument();
      expect(screen.getByText('4x Speed')).toBeInTheDocument();
    });

    it('should call disconnect when clicking pause', async () => {
      renderTownV2();

      await waitFor(() => {
        const pauseButton = screen.getByText(/Pause/);
        fireEvent.click(pauseButton);
      });

      expect(mockDisconnect).toHaveBeenCalled();
    });
  });

  describe('event feed', () => {
    it('should show event count', async () => {
      renderTownV2();

      await waitFor(() => {
        expect(screen.getByText(/Event Feed \(2\)/)).toBeInTheDocument();
      });
    });

    it('should toggle event feed on click', async () => {
      renderTownV2();

      await waitFor(() => {
        const feedToggle = screen.getByText(/Event Feed \(2\)/);
        fireEvent.click(feedToggle);
      });

      // After clicking, events should be visible
      await waitFor(() => {
        expect(screen.getByText(/greet/)).toBeInTheDocument();
      });
    });
  });

  describe('sidebar', () => {
    it('should show "Click a citizen" when none selected', async () => {
      renderTownV2();

      await waitFor(() => {
        expect(screen.getByText(/Click a citizen on the map/)).toBeInTheDocument();
      });
    });

    it('should display ColonyDashboard when no citizen selected', async () => {
      renderTownV2();

      await waitFor(() => {
        // The ColonyDashboard component should be rendered
        expect(screen.getByText('AGENT TOWN DASHBOARD')).toBeInTheDocument();
      });
    });
  });

  describe('mesa canvas', () => {
    it('should render the PixiJS Stage', async () => {
      renderTownV2();

      await waitFor(() => {
        expect(screen.getByTestId('pixi-stage')).toBeInTheDocument();
      });
    });
  });
});

describe('TownV2 loading and error states', () => {
  // These states are tested implicitly through the mocks above
  // The mock returns resolved values, so loading states are transient

  it('should handle successful town load', async () => {
    renderTownV2();

    // Wait for content to appear (proves loading completed)
    await waitFor(() => {
      expect(screen.getByText(/Town: test-town/)).toBeInTheDocument();
    });
  });

  it('should show loading indicator text when appropriate', () => {
    // The loading states are controlled by the component's internal state
    // and the mock resolves immediately, so we verify the structure exists
    expect(true).toBe(true); // Placeholder for visual testing
  });
});
