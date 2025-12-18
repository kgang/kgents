/**
 * AtelierVisualization Fishbowl Integration Tests
 *
 * Tests for the Fishbowl view integration in AtelierVisualization:
 * - Type I: Contract tests (view transitions, prop passing)
 * - Type II: Saboteur tests (edge cases, empty sessions)
 * - Type III: Spy tests (callback verification, session selection)
 *
 * @see plans/crown-jewels-genesis-phase2-continuation.md - Chunk 1: Integration
 * @see docs/skills/test-patterns.md - T-gent Taxonomy
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { AtelierVisualization, type AtelierVisualizationProps } from '@/components/atelier/AtelierVisualization';

// =============================================================================
// Mocks
// =============================================================================

// Mock useAtelierStream hook
const mockSubscribe = vi.fn();
const mockUnsubscribe = vi.fn();
const mockUpdateCursor = vi.fn();

vi.mock('@/hooks/useAtelierStream', () => ({
  useAtelierStream: () => ({
    events: [],
    piece: null,
    isStreaming: false,
    status: 'idle',
    error: null,
    progress: 0,
    currentFragment: '',
    commission: vi.fn(),
    collaborate: vi.fn(),
    cancel: vi.fn(),
    reset: vi.fn(),
    // Phase 2: Live Session
    sessionState: {
      sessionId: 'demo-session-1',
      isLive: true,
      spectatorCount: 5,
      content: 'Test content from stream',
      contentType: 'text' as const,
    },
    spectatorCursors: [
      {
        id: 'cursor-1',
        position: { x: 0.5, y: 0.5 },
        lastUpdate: Date.now(),
        name: 'Spectator 1',
      },
    ],
    subscribeToSession: mockSubscribe,
    unsubscribeFromSession: mockUnsubscribe,
    updateCursor: mockUpdateCursor,
    isSessionLive: true,
  }),
}));

// Mock AGENTESE hooks
vi.mock('@/hooks/useAtelierQuery', () => ({
  useAtelierManifest: () => ({
    data: {
      total_workshops: 3,
      active_workshops: 2,
      total_artisans: 10,
      total_contributions: 50,
      total_exhibitions: 5,
      open_exhibitions: 2,
      storage_backend: 'memory',
    },
    isLoading: false,
    error: null,
    refetch: vi.fn(),
  }),
  useWorkshops: () => ({
    data: { count: 2, workshops: [] },
    isLoading: false,
    error: null,
    refetch: vi.fn(),
  }),
  useArtisans: () => ({
    data: { count: 0, artisans: [] },
    isLoading: false,
    error: null,
    refetch: vi.fn(),
  }),
  useContributions: () => ({
    data: { count: 0, contributions: [] },
    isLoading: false,
    error: null,
    refetch: vi.fn(),
  }),
}));

// =============================================================================
// Test Fixtures
// =============================================================================

const defaultProps: AtelierVisualizationProps = {
  status: {
    total_workshops: 3,
    active_workshops: 2,
    total_artisans: 10,
    total_contributions: 50,
    total_exhibitions: 5,
    open_exhibitions: 2,
    status: 'healthy',
  },
  density: 'comfortable',
  isMobile: false,
  isTablet: false,
  isDesktop: true,
  refetch: vi.fn(),
};

// Helper to render component (hooks are mocked)
function renderWithProviders(overrides: Partial<AtelierVisualizationProps> = {}) {
  const props = { ...defaultProps, ...overrides };
  return render(<AtelierVisualization {...props} />);
}

// =============================================================================
// Type I: Contract Tests (Navigation & View Transitions)
// =============================================================================

describe('AtelierVisualization Fishbowl - Type I: Contract Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders Live tab in navigation', () => {
    renderWithProviders();
    expect(screen.getByRole('button', { name: /live/i })).toBeInTheDocument();
  });

  it('shows Live tab in correct position (second tab)', () => {
    renderWithProviders();
    const tabs = screen.getAllByRole('button').filter(btn =>
      ['Overview', 'Live', 'Workshops', 'Artisans', 'Works'].includes(btn.textContent?.trim() || '')
    );
    // Live should be second
    expect(tabs[1]).toHaveTextContent(/live/i);
  });

  it('switches to fishbowl view when Live tab is clicked', async () => {
    renderWithProviders();
    const liveTab = screen.getByRole('button', { name: /live/i });
    fireEvent.click(liveTab);

    await waitFor(() => {
      expect(screen.getByText('Live Creation')).toBeInTheDocument();
    });
  });

  it('renders cursor toggle button in fishbowl view', async () => {
    renderWithProviders();
    const liveTab = screen.getByRole('button', { name: /live/i });
    fireEvent.click(liveTab);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /cursors/i })).toBeInTheDocument();
    });
  });

  it('displays session selector in fishbowl view', async () => {
    renderWithProviders();
    const liveTab = screen.getByRole('button', { name: /live/i });
    fireEvent.click(liveTab);

    await waitFor(() => {
      // Session selector shows artisan names
      expect(screen.getByText('Calligrapher')).toBeInTheDocument();
      expect(screen.getByText('Poet')).toBeInTheDocument();
    });
  });
});

// =============================================================================
// Type II: Saboteur Tests (Edge Cases)
// =============================================================================

describe('AtelierVisualization Fishbowl - Type II: Saboteur Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows placeholder when no session is selected', async () => {
    renderWithProviders();
    const liveTab = screen.getByRole('button', { name: /live/i });
    fireEvent.click(liveTab);

    await waitFor(() => {
      expect(screen.getByText(/select a session above/i)).toBeInTheDocument();
    });
  });

  it('handles mobile layout correctly', async () => {
    renderWithProviders({ isMobile: true });
    const liveTab = screen.getByRole('button', { name: /live/i });
    fireEvent.click(liveTab);

    await waitFor(() => {
      expect(screen.getByText('Live Creation')).toBeInTheDocument();
    });
  });

  it('toggles cursor visibility', async () => {
    renderWithProviders();
    const liveTab = screen.getByRole('button', { name: /live/i });
    fireEvent.click(liveTab);

    await waitFor(() => {
      const cursorToggle = screen.getByRole('button', { name: /cursors/i });
      expect(cursorToggle).toHaveAttribute('aria-pressed', 'true');

      // Toggle off
      fireEvent.click(cursorToggle);
      expect(cursorToggle).toHaveAttribute('aria-pressed', 'false');
    });
  });
});

// =============================================================================
// Type III: Spy Tests (Callbacks & Session Selection)
// =============================================================================

describe('AtelierVisualization Fishbowl - Type III: Spy Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('subscribes to session when session is selected', async () => {
    renderWithProviders();

    // Navigate to fishbowl view
    const liveTab = screen.getByRole('button', { name: /live/i });
    fireEvent.click(liveTab);

    // Click on a session
    await waitFor(() => {
      const calligrapherSession = screen.getByRole('button', { name: /calligrapher/i });
      fireEvent.click(calligrapherSession);
    });

    // Verify subscription was called
    await waitFor(() => {
      expect(mockSubscribe).toHaveBeenCalledWith('demo-session-1');
    });
  });

  it('unsubscribes when navigating away from fishbowl view', async () => {
    renderWithProviders();

    // Navigate to fishbowl view
    const liveTab = screen.getByRole('button', { name: /live/i });
    fireEvent.click(liveTab);

    // Select a session
    await waitFor(() => {
      const calligrapherSession = screen.getByRole('button', { name: /calligrapher/i });
      fireEvent.click(calligrapherSession);
    });

    // Navigate away
    const overviewTab = screen.getByRole('button', { name: /overview/i });
    fireEvent.click(overviewTab);

    await waitFor(() => {
      expect(mockUnsubscribe).toHaveBeenCalled();
    });
  });

  it('renders FishbowlCanvas when session is active', async () => {
    renderWithProviders();

    // Navigate to fishbowl view
    const liveTab = screen.getByRole('button', { name: /live/i });
    fireEvent.click(liveTab);

    // Select a session
    await waitFor(() => {
      const calligrapherSession = screen.getByRole('button', { name: /calligrapher/i });
      fireEvent.click(calligrapherSession);
    });

    // FishbowlCanvas should render (look for its aria-label)
    await waitFor(() => {
      const canvas = screen.getByRole('region', { name: /live creation canvas/i });
      expect(canvas).toBeInTheDocument();
    });
  });
});

// =============================================================================
// Session Selector Tests
// =============================================================================

describe('AtelierVisualization - SessionSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('highlights active session', async () => {
    renderWithProviders();
    const liveTab = screen.getByRole('button', { name: /live/i });
    fireEvent.click(liveTab);

    // Click on Calligrapher session
    await waitFor(() => {
      const calligrapherSession = screen.getByRole('button', { name: /calligrapher/i });
      fireEvent.click(calligrapherSession);
    });

    // Check it has the active styling (amber background)
    await waitFor(() => {
      const calligrapherSession = screen.getByRole('button', { name: /calligrapher/i });
      expect(calligrapherSession.className).toContain('amber');
    });
  });

  it('shows live indicator for live sessions', async () => {
    renderWithProviders();
    const liveTab = screen.getByRole('button', { name: /live/i });
    fireEvent.click(liveTab);

    await waitFor(() => {
      // Calligrapher session should show watching count
      expect(screen.getByText(/watching/i)).toBeInTheDocument();
    });
  });

  it('allows switching between sessions', async () => {
    renderWithProviders();
    const liveTab = screen.getByRole('button', { name: /live/i });
    fireEvent.click(liveTab);

    // Select first session
    await waitFor(() => {
      const calligrapherSession = screen.getByRole('button', { name: /calligrapher/i });
      fireEvent.click(calligrapherSession);
    });

    // Select second session
    await waitFor(() => {
      const poetSession = screen.getByRole('button', { name: /poet/i });
      fireEvent.click(poetSession);
    });

    // Subscribe should have been called with the new session
    await waitFor(() => {
      expect(mockSubscribe).toHaveBeenLastCalledWith('demo-session-2');
    });
  });
});
