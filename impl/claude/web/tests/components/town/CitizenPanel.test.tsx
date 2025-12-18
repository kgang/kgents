/**
 * Tests for CitizenPanel component.
 *
 * T-gent Type I: Contracts - Component renders expected content
 * T-gent Type II: Saboteurs - Component handles bad data
 * T-gent Type III: Spies - Component emits correct events
 *
 * @see impl/claude/web/src/components/town/CitizenPanel.tsx
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CitizenPanel } from '@/components/town/CitizenPanel';
import { townApi } from '@/api/client';
import type { CitizenCardJSON } from '@/reactive/types';

// Mock API client
vi.mock('@/api/client', () => ({
  townApi: {
    getCitizen: vi.fn(),
  },
}));

// =============================================================================
// Test Fixtures
// =============================================================================

const mockCitizen: CitizenCardJSON = {
  type: 'citizen_card',
  citizen_id: 'citizen-001',
  name: 'Alice',
  archetype: 'builder',
  region: 'North',
  phase: 'IDLE',
  nphase: 'UNDERSTAND',
  mood: 'curious',
  capability: 0.75,
  entropy: 0.3,
  eigenvectors: {
    warmth: 0.8,
    curiosity: 0.9,
    trust: 0.7,
  },
};

const mockManifest = {
  citizen: {
    id: 'citizen-001',
    name: 'Alice',
    archetype: 'builder',
    phase: 'IDLE',
    eigenvectors: {
      warmth: 0.8,
      curiosity: 0.9,
      trust: 0.7,
      creativity: 0.85,
      patience: 0.6,
      resilience: 0.75,
      ambition: 0.9,
    },
    relationships: {
      'Bob': 0.5,
      'Charlie': -0.2,
      'Diana': 0.8,
    },
    cosmotechnics: 'Builder archetype focused on creation',
    metaphor: 'A gardener tending to digital flowers',
    accursed_surplus: 0.15,
    opacity: {
      statement: 'I am more than what you see',
      message: 'There are hidden depths',
    },
  },
};

// =============================================================================
// T-gent Type I: Contracts - Component renders expected content
// =============================================================================

describe('CitizenPanel - Contracts', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (townApi.getCitizen as any).mockResolvedValue(mockManifest);
  });

  it('renders citizen name in header', async () => {
    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeInTheDocument();
    });
  });

  it('displays LOD 0 silhouette information', async () => {
    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Silhouette')).toBeInTheDocument();
      expect(screen.getByText('Region')).toBeInTheDocument();
      expect(screen.getByText('North')).toBeInTheDocument();
      expect(screen.getByText('Phase')).toBeInTheDocument();
      expect(screen.getByText('IDLE')).toBeInTheDocument();
    });
  });

  it('displays LOD 1 posture information', async () => {
    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Posture')).toBeInTheDocument();
      expect(screen.getByText('Archetype')).toBeInTheDocument();
      expect(screen.getByText('builder')).toBeInTheDocument();
      expect(screen.getByText('Mood')).toBeInTheDocument();
      expect(screen.getByText('curious')).toBeInTheDocument();
    });
  });

  it('displays LOD 2 dialogue section', async () => {
    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Dialogue')).toBeInTheDocument();
      expect(screen.getByText('Builder archetype focused on creation')).toBeInTheDocument();
      expect(screen.getByText('"A gardener tending to digital flowers"')).toBeInTheDocument();
    });
  });

  it('displays LOD 3 memory eigenvectors', async () => {
    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Memory')).toBeInTheDocument();
      expect(screen.getByText('Eigenvectors')).toBeInTheDocument();
      expect(screen.getByText('Warmth')).toBeInTheDocument();
      expect(screen.getByText('Curiosity')).toBeInTheDocument();
      expect(screen.getByText('Trust')).toBeInTheDocument();
    });
  });

  it('displays relationships when available', async () => {
    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Relationships')).toBeInTheDocument();
      expect(screen.getByText('Bob')).toBeInTheDocument();
      expect(screen.getByText('Charlie')).toBeInTheDocument();
      expect(screen.getByText('Diana')).toBeInTheDocument();
    });
  });

  it('displays LOD 4 psyche information', async () => {
    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Psyche')).toBeInTheDocument();
      expect(screen.getByText('Capability')).toBeInTheDocument();
      expect(screen.getByText('75%')).toBeInTheDocument();
      expect(screen.getByText('Entropy')).toBeInTheDocument();
    });
  });

  it('displays LOD 5 abyss section when opacity is available', async () => {
    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Abyss')).toBeInTheDocument();
      expect(screen.getByText('"I am more than what you see"')).toBeInTheDocument();
      expect(screen.getByText('There are hidden depths')).toBeInTheDocument();
    });
  });

  it('renders all LOD selector buttons', async () => {
    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      const lodButtons = screen.getAllByRole('button').filter(btn =>
        ['0', '1', '2', '3', '4', '5'].includes(btn.textContent || '')
      );
      expect(lodButtons.length).toBe(6);
    });
  });

  it('shows state machine visualization', async () => {
    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Polynomial State')).toBeInTheDocument();
    });
  });
});

// =============================================================================
// T-gent Type II: Saboteurs - Component handles bad data
// =============================================================================

describe('CitizenPanel - Saboteurs', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state while fetching manifest', () => {
    (townApi.getCitizen as any).mockImplementation(() => new Promise(() => {}));

    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    expect(screen.getByText(/manifest/i)).toBeInTheDocument();
  });

  it('handles API error gracefully', async () => {
    (townApi.getCitizen as any).mockRejectedValue(new Error('Network error'));

    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load citizen details')).toBeInTheDocument();
    });
  });

  it('handles missing eigenvectors gracefully', async () => {
    const citizenWithoutEigenvectors: CitizenCardJSON = {
      ...mockCitizen,
      eigenvectors: undefined,
    };

    (townApi.getCitizen as any).mockResolvedValue({
      citizen: {
        ...mockManifest.citizen,
        eigenvectors: undefined,
      },
    });

    render(<CitizenPanel citizen={citizenWithoutEigenvectors} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeInTheDocument();
    });
  });

  it('handles missing relationships gracefully', async () => {
    (townApi.getCitizen as any).mockResolvedValue({
      citizen: {
        ...mockManifest.citizen,
        relationships: {},
      },
    });

    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeInTheDocument();
    });
  });

  it('handles missing opacity section gracefully', async () => {
    (townApi.getCitizen as any).mockResolvedValue({
      citizen: {
        ...mockManifest.citizen,
        opacity: undefined,
      },
    });

    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeInTheDocument();
      expect(screen.queryByText('Abyss')).not.toBeInTheDocument();
    });
  });

  it('provides reset button on error', async () => {
    (townApi.getCitizen as any).mockRejectedValue(new Error('Network error'));

    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Reset to LOD 0')).toBeInTheDocument();
    });
  });
});

// =============================================================================
// T-gent Type III: Spies - Component emits correct events
// =============================================================================

describe('CitizenPanel - Spies', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (townApi.getCitizen as any).mockResolvedValue(mockManifest);
  });

  it('calls onClose when close button clicked', async () => {
    const onClose = vi.fn();

    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={onClose} />);

    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeInTheDocument();
    });

    const closeButton = screen.getByText('✕');
    fireEvent.click(closeButton);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('fetches manifest with correct parameters', async () => {
    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(townApi.getCitizen).toHaveBeenCalledWith('town-001', 'Alice', 0, 'anonymous');
    });
  });

  it('refetches manifest when LOD changes', async () => {
    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(townApi.getCitizen).toHaveBeenCalledWith('town-001', 'Alice', 0, 'anonymous');
    });

    // Click LOD 2 button
    const lod2Button = screen.getByRole('button', { name: '2' });
    fireEvent.click(lod2Button);

    await waitFor(() => {
      expect(townApi.getCitizen).toHaveBeenCalledWith('town-001', 'Alice', 2, 'anonymous');
    });
  });

  it('resets to LOD 0 when reset button clicked after error', async () => {
    (townApi.getCitizen as any).mockRejectedValueOnce(new Error('Network error'));

    render(<CitizenPanel citizen={mockCitizen} townId="town-001" onClose={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Reset to LOD 0')).toBeInTheDocument();
    });

    (townApi.getCitizen as any).mockResolvedValue(mockManifest);

    const resetButton = screen.getByText('Reset to LOD 0');
    fireEvent.click(resetButton);

    await waitFor(() => {
      expect(townApi.getCitizen).toHaveBeenLastCalledWith('town-001', 'Alice', 0, 'anonymous');
    });
  });
});
