import { describe, it, expect, beforeEach, vi, type Mock } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { CitizenPanel } from '@/components/town/CitizenPanel';
import { useTownStore } from '@/stores/townStore';
import { useUserStore } from '@/stores/userStore';
import { townApi } from '@/api/client';
import type { CitizenSummary, CitizenManifest, Eigenvectors } from '@/api/types';

// Mock API client
vi.mock('@/api/client', () => ({
  townApi: {
    getCitizen: vi.fn(),
  },
}));

// Mock LODGate - pass through children when unlocked, show paywall otherwise
vi.mock('@/components/paywall/LODGate', () => ({
  LODGate: ({ children, level }: { children: React.ReactNode; level: number }) => {
    // In tests, we'll treat LOD 0-2 as always unlocked, 3+ as gated
    if (level <= 2) {
      return <>{children}</>;
    }
    // For gated content, render a test-friendly paywall
    return (
      <div data-testid={`lod-gate-${level}`}>
        <div data-testid="paywall">LOD {level} Locked</div>
        {children}
      </div>
    );
  },
}));

// Helper to create mock citizen summary
const createMockCitizenSummary = (overrides: Partial<CitizenSummary> = {}): CitizenSummary => ({
  id: 'citizen-1',
  name: 'Alice',
  archetype: 'Builder',
  region: 'square',
  phase: 'WORKING',
  is_evolving: false,
  ...overrides,
});

// Helper to create mock manifest
const createMockManifest = (overrides: Partial<CitizenManifest> = {}): CitizenManifest => ({
  name: 'Alice',
  region: 'square',
  phase: 'WORKING',
  nphase: { current: 'IMPLEMENT', cycle_count: 3 },
  archetype: 'Builder',
  mood: 'focused',
  cosmotechnics: 'efficiency',
  metaphor: 'The mind is a forge.',
  eigenvectors: {
    warmth: 0.6,
    curiosity: 0.8,
    trust: 0.7,
    creativity: 0.9,
    patience: 0.5,
    resilience: 0.75,
    ambition: 0.85,
  },
  relationships: {
    Bob: 0.8,
    Carol: -0.3,
    Dave: 0.5,
    Eve: 0.2,
    Frank: 0.1,
    Grace: -0.1,
  },
  accursed_surplus: 0.123,
  id: 'citizen-1',
  opacity: {
    statement: 'The abyss gazes back.',
    message: 'In the depths, truth emerges.',
  },
  ...overrides,
});

const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('CitizenPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Reset stores to initial state
    useTownStore.getState().reset();

    // Default user store mock
    useUserStore.setState({
      userId: 'user-1',
      tier: 'RESIDENT',
      credits: 100,
    });
  });

  describe('empty state', () => {
    it('should show prompt when no citizen is selected', () => {
      renderWithRouter(<CitizenPanel />);

      expect(screen.getByText(/Click a citizen/)).toBeInTheDocument();
    });
  });

  describe('loading state', () => {
    it('should show loading when fetching citizen data', async () => {
      // Setup: Select a citizen and provide delayed API response
      const citizen = createMockCitizenSummary();
      useTownStore.setState({
        selectedCitizenId: 'citizen-1',
        citizens: [citizen],
        townId: 'town-1',
      });

      // Never-resolving promise to keep loading
      (townApi.getCitizen as Mock).mockReturnValue(new Promise(() => {}));

      renderWithRouter(<CitizenPanel />);

      expect(screen.getByText(/Loading/)).toBeInTheDocument();
    });
  });

  describe('error state', () => {
    it('should show error when API fails', async () => {
      const citizen = createMockCitizenSummary();
      useTownStore.setState({
        selectedCitizenId: 'citizen-1',
        citizens: [citizen],
        townId: 'town-1',
      });

      (townApi.getCitizen as Mock).mockRejectedValueOnce(new Error('Network error'));

      renderWithRouter(<CitizenPanel />);

      await waitFor(() => {
        expect(screen.getByText(/Failed to load/)).toBeInTheDocument();
      });

      // Should show reset button
      expect(screen.getByText(/Reset to LOD 0/)).toBeInTheDocument();
    });
  });

  describe('LOD 0: Silhouette', () => {
    it('should display basic info (region, phase)', async () => {
      const citizen = createMockCitizenSummary();
      const manifest = createMockManifest();

      useTownStore.setState({
        selectedCitizenId: 'citizen-1',
        citizens: [citizen],
        townId: 'town-1',
        currentLOD: 0,
      });

      (townApi.getCitizen as Mock).mockResolvedValueOnce({
        data: { citizen: manifest, lod: 0, cost_credits: 0 },
      });

      renderWithRouter(<CitizenPanel />);

      await waitFor(() => {
        expect(screen.getByText('Alice')).toBeInTheDocument();
      });

      // LOD 0 content
      expect(screen.getByText('Silhouette')).toBeInTheDocument();
      expect(screen.getByText('square')).toBeInTheDocument();
      expect(screen.getByText('WORKING')).toBeInTheDocument();
    });

    it('should display N-Phase information when available', async () => {
      const citizen = createMockCitizenSummary();
      const manifest = createMockManifest();

      useTownStore.setState({
        selectedCitizenId: 'citizen-1',
        citizens: [citizen],
        townId: 'town-1',
      });

      (townApi.getCitizen as Mock).mockResolvedValueOnce({
        data: { citizen: manifest, lod: 0, cost_credits: 0 },
      });

      renderWithRouter(<CitizenPanel />);

      await waitFor(() => {
        expect(screen.getByText(/IMPLEMENT/)).toBeInTheDocument();
        expect(screen.getByText(/cycle 3/)).toBeInTheDocument();
      });
    });
  });

  describe('LOD 1: Posture', () => {
    it('should display archetype and mood', async () => {
      const citizen = createMockCitizenSummary();
      const manifest = createMockManifest();

      useTownStore.setState({
        selectedCitizenId: 'citizen-1',
        citizens: [citizen],
        townId: 'town-1',
        currentLOD: 1,
      });

      (townApi.getCitizen as Mock).mockResolvedValueOnce({
        data: { citizen: manifest, lod: 1, cost_credits: 0 },
      });

      renderWithRouter(<CitizenPanel />);

      await waitFor(() => {
        expect(screen.getByText('Posture')).toBeInTheDocument();
      });

      expect(screen.getByText('Builder')).toBeInTheDocument();
      expect(screen.getByText('focused')).toBeInTheDocument();
    });
  });

  describe('LOD 2: Dialogue', () => {
    it('should display cosmotechnics and metaphor', async () => {
      const citizen = createMockCitizenSummary();
      const manifest = createMockManifest();

      useTownStore.setState({
        selectedCitizenId: 'citizen-1',
        citizens: [citizen],
        townId: 'town-1',
        currentLOD: 2,
      });

      (townApi.getCitizen as Mock).mockResolvedValueOnce({
        data: { citizen: manifest, lod: 2, cost_credits: 0 },
      });

      renderWithRouter(<CitizenPanel />);

      await waitFor(() => {
        expect(screen.getByText('Dialogue')).toBeInTheDocument();
      });

      expect(screen.getByText('efficiency')).toBeInTheDocument();
      expect(screen.getByText(/"The mind is a forge\."/)).toBeInTheDocument();
    });
  });

  describe('LOD 3: Memory (gated)', () => {
    it('should display eigenvectors and relationships', async () => {
      const citizen = createMockCitizenSummary();
      const manifest = createMockManifest();

      useTownStore.setState({
        selectedCitizenId: 'citizen-1',
        citizens: [citizen],
        townId: 'town-1',
        currentLOD: 3,
      });

      (townApi.getCitizen as Mock).mockResolvedValueOnce({
        data: { citizen: manifest, lod: 3, cost_credits: 10 },
      });

      renderWithRouter(<CitizenPanel />);

      await waitFor(() => {
        expect(screen.getByText('Memory')).toBeInTheDocument();
      });

      // Eigenvectors section
      expect(screen.getByText('Eigenvectors')).toBeInTheDocument();
      expect(screen.getByText('Warmth')).toBeInTheDocument();
      expect(screen.getByText('0.60')).toBeInTheDocument();
      expect(screen.getByText('Curiosity')).toBeInTheDocument();
      expect(screen.getByText('0.80')).toBeInTheDocument();

      // Relationships section (sorted by value desc, top 5 shown)
      expect(screen.getByText('Relationships')).toBeInTheDocument();
      expect(screen.getByText('Bob')).toBeInTheDocument(); // +0.80 (highest)
      expect(screen.getByText('+0.80')).toBeInTheDocument();
      expect(screen.getByText('Dave')).toBeInTheDocument(); // +0.50
      // Carol at -0.30 is outside top 5, so not shown
      expect(screen.getByText(/\+1 more/)).toBeInTheDocument();
    });

    it('should truncate relationships list to 5 with count', async () => {
      const citizen = createMockCitizenSummary();
      const manifest = createMockManifest({
        relationships: {
          A: 0.9,
          B: 0.8,
          C: 0.7,
          D: 0.6,
          E: 0.5,
          F: 0.4,
          G: 0.3,
        },
      });

      useTownStore.setState({
        selectedCitizenId: 'citizen-1',
        citizens: [citizen],
        townId: 'town-1',
        currentLOD: 3,
      });

      (townApi.getCitizen as Mock).mockResolvedValueOnce({
        data: { citizen: manifest, lod: 3, cost_credits: 10 },
      });

      renderWithRouter(<CitizenPanel />);

      await waitFor(() => {
        expect(screen.getByText(/\+2 more/)).toBeInTheDocument();
      });
    });
  });

  describe('LOD 4: Psyche (gated)', () => {
    it('should display accursed surplus and ID', async () => {
      const citizen = createMockCitizenSummary();
      const manifest = createMockManifest();

      useTownStore.setState({
        selectedCitizenId: 'citizen-1',
        citizens: [citizen],
        townId: 'town-1',
        currentLOD: 4,
      });

      (townApi.getCitizen as Mock).mockResolvedValueOnce({
        data: { citizen: manifest, lod: 4, cost_credits: 100 },
      });

      renderWithRouter(<CitizenPanel />);

      await waitFor(() => {
        expect(screen.getByText('Psyche')).toBeInTheDocument();
      });

      expect(screen.getByText('Accursed Surplus')).toBeInTheDocument();
      expect(screen.getByText('0.123')).toBeInTheDocument();
      expect(screen.getByText('citizen-1')).toBeInTheDocument();
    });
  });

  describe('LOD 5: Abyss (gated)', () => {
    it('should display opacity statement and message', async () => {
      const citizen = createMockCitizenSummary();
      const manifest = createMockManifest();

      useTownStore.setState({
        selectedCitizenId: 'citizen-1',
        citizens: [citizen],
        townId: 'town-1',
        currentLOD: 5,
      });

      (townApi.getCitizen as Mock).mockResolvedValueOnce({
        data: { citizen: manifest, lod: 5, cost_credits: 400 },
      });

      renderWithRouter(<CitizenPanel />);

      await waitFor(() => {
        expect(screen.getByText('Abyss')).toBeInTheDocument();
      });

      expect(screen.getByText(/"The abyss gazes back\."/)).toBeInTheDocument();
      expect(screen.getByText('In the depths, truth emerges.')).toBeInTheDocument();
    });
  });

  describe('INHABIT action', () => {
    it('should show INHABIT button for RESIDENT+ tier', async () => {
      const citizen = createMockCitizenSummary();
      const manifest = createMockManifest();

      useTownStore.setState({
        selectedCitizenId: 'citizen-1',
        citizens: [citizen],
        townId: 'town-1',
      });

      // RESIDENT can inhabit
      useUserStore.setState({
        userId: 'user-1',
        tier: 'RESIDENT',
        credits: 100,
      });

      (townApi.getCitizen as Mock).mockResolvedValueOnce({
        data: { citizen: manifest, lod: 0, cost_credits: 0 },
      });

      renderWithRouter(<CitizenPanel />);

      await waitFor(() => {
        expect(screen.getByText(/INHABIT Alice/)).toBeInTheDocument();
      });
    });

    it('should show upgrade prompt for TOURIST tier', async () => {
      const citizen = createMockCitizenSummary();
      const manifest = createMockManifest();

      useTownStore.setState({
        selectedCitizenId: 'citizen-1',
        citizens: [citizen],
        townId: 'town-1',
      });

      // TOURIST cannot inhabit
      useUserStore.setState({
        userId: 'user-1',
        tier: 'TOURIST',
        credits: 0,
      });

      (townApi.getCitizen as Mock).mockResolvedValueOnce({
        data: { citizen: manifest, lod: 0, cost_credits: 0 },
      });

      renderWithRouter(<CitizenPanel />);

      await waitFor(() => {
        expect(screen.getByText(/Upgrade to RESIDENT/)).toBeInTheDocument();
      });
    });
  });

  describe('close button', () => {
    it('should clear selection when close button clicked', async () => {
      const citizen = createMockCitizenSummary();
      const manifest = createMockManifest();

      useTownStore.setState({
        selectedCitizenId: 'citizen-1',
        citizens: [citizen],
        townId: 'town-1',
      });

      (townApi.getCitizen as Mock).mockResolvedValueOnce({
        data: { citizen: manifest, lod: 0, cost_credits: 0 },
      });

      renderWithRouter(<CitizenPanel />);

      await waitFor(() => {
        expect(screen.getByText('Alice')).toBeInTheDocument();
      });

      const closeButton = screen.getByText('✕');
      closeButton.click();

      // Selection should be cleared (component will show empty state)
      expect(useTownStore.getState().selectedCitizenId).toBeNull();
    });
  });

  describe('API integration', () => {
    it('should call API with correct parameters', async () => {
      const citizen = createMockCitizenSummary({ name: 'Bob' });
      const manifest = createMockManifest({ name: 'Bob' });

      useTownStore.setState({
        selectedCitizenId: 'citizen-1',
        citizens: [citizen],
        townId: 'my-town',
        currentLOD: 2,
      });

      useUserStore.setState({
        userId: 'user-123',
        tier: 'CITIZEN',
        credits: 500,
      });

      (townApi.getCitizen as Mock).mockResolvedValueOnce({
        data: { citizen: manifest, lod: 2, cost_credits: 0 },
      });

      renderWithRouter(<CitizenPanel />);

      await waitFor(() => {
        expect(townApi.getCitizen).toHaveBeenCalledWith('my-town', 'Bob', 2, 'user-123');
      });
    });

    it('should refetch when LOD changes', async () => {
      const citizen = createMockCitizenSummary();
      const manifest = createMockManifest();

      useTownStore.setState({
        selectedCitizenId: 'citizen-1',
        citizens: [citizen],
        townId: 'town-1',
        currentLOD: 0,
      });

      (townApi.getCitizen as Mock).mockResolvedValue({
        data: { citizen: manifest, lod: 0, cost_credits: 0 },
      });

      const { rerender } = renderWithRouter(<CitizenPanel />);

      await waitFor(() => {
        expect(townApi.getCitizen).toHaveBeenCalledTimes(1);
      });

      // Change LOD
      useTownStore.setState({ currentLOD: 3 });
      rerender(<BrowserRouter><CitizenPanel /></BrowserRouter>);

      await waitFor(() => {
        expect(townApi.getCitizen).toHaveBeenCalledTimes(2);
      });
    });
  });
});
