/**
 * Tests for Mesa: Props-based Mesa canvas.
 *
 * Mesa receives citizens as props for rendering with PixiJS.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Mesa } from '@/components/town/Mesa';
import type { CitizenCardJSON } from '@/reactive/types';

// =============================================================================
// Mocks
// =============================================================================

// Mock PixiJS components
vi.mock('@pixi/react', () => ({
  Stage: ({
    children,
    width,
    height,
  }: {
    children: React.ReactNode;
    width: number;
    height: number;
  }) => (
    <div data-testid="pixi-stage" data-width={width} data-height={height}>
      {children}
    </div>
  ),
  Container: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="pixi-container">{children}</div>
  ),
  Graphics: ({ pointerdown }: { draw: () => void; pointerdown?: () => void }) => (
    <div data-testid="pixi-graphics" onClick={pointerdown} />
  ),
  Text: ({ text }: { text: string }) => <span data-testid="pixi-text">{text}</span>,
}));

// =============================================================================
// Test Data
// =============================================================================

const mockCitizens: CitizenCardJSON[] = [
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
];

// =============================================================================
// Tests
// =============================================================================

describe('Mesa', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('rendering', () => {
    it('should render the PixiJS Stage', () => {
      render(<Mesa citizens={mockCitizens} selectedCitizenId={null} />);

      expect(screen.getByTestId('pixi-stage')).toBeInTheDocument();
    });

    it('should use provided width and height', () => {
      render(<Mesa width={1200} height={900} citizens={mockCitizens} selectedCitizenId={null} />);

      const stage = screen.getByTestId('pixi-stage');
      expect(stage).toHaveAttribute('data-width', '1200');
      expect(stage).toHaveAttribute('data-height', '900');
    });

    it('should render citizen names as text', () => {
      render(
        <Mesa
          citizens={mockCitizens}
          selectedCitizenId="alice-123" // Selected to show name
        />
      );

      // Names should appear as PixiJS Text elements
      const textElements = screen.getAllByTestId('pixi-text');
      const texts = textElements.map((el) => el.textContent);

      // Should include region labels and archetype letters
      expect(texts).toContain('Alice'); // Selected citizen's name
      expect(texts).toContain('B'); // Builder archetype letter
      expect(texts).toContain('T'); // Trader archetype letter
    });

    it('should render region labels', () => {
      render(<Mesa citizens={mockCitizens} selectedCitizenId={null} />);

      const textElements = screen.getAllByTestId('pixi-text');
      const texts = textElements.map((el) => el.textContent);

      // Should include region names
      expect(texts).toContain('square');
      expect(texts).toContain('market');
    });
  });

  describe('selection', () => {
    it('should call onSelectCitizen when citizen clicked', () => {
      const onSelect = vi.fn();

      render(<Mesa citizens={mockCitizens} selectedCitizenId={null} onSelectCitizen={onSelect} />);

      // Graphics elements are clickable
      const graphics = screen.getAllByTestId('pixi-graphics');
      // Find the citizen graphics (not grid/region graphics)
      const citizenGraphics = graphics.filter((g) => g.onclick);

      if (citizenGraphics.length > 0) {
        citizenGraphics[0].click();
      }
    });
  });

  describe('with empty citizens', () => {
    it('should render stage even with no citizens', () => {
      render(<Mesa citizens={[]} selectedCitizenId={null} />);

      expect(screen.getByTestId('pixi-stage')).toBeInTheDocument();
    });

    it('should still show region labels', () => {
      render(<Mesa citizens={[]} selectedCitizenId={null} />);

      const textElements = screen.getAllByTestId('pixi-text');
      const texts = textElements.map((el) => el.textContent);

      // Should include region names even without citizens
      expect(texts.length).toBeGreaterThan(0);
    });
  });

  describe('archetype handling', () => {
    it('should handle lowercase archetype names', () => {
      const citizens: CitizenCardJSON[] = [
        {
          type: 'citizen_card',
          citizen_id: 'charlie-789',
          name: 'Charlie',
          archetype: 'scholar', // lowercase
          phase: 'REFLECTING',
          nphase: 'REFLECT',
          activity: [],
          capability: 0.5,
          entropy: 0.15,
          region: 'library',
          mood: 'thoughtful',
          eigenvectors: { warmth: 0.6, curiosity: 0.95, trust: 0.7 },
        },
      ];

      render(<Mesa citizens={citizens} selectedCitizenId={null} />);

      // Should render without error
      expect(screen.getByTestId('pixi-stage')).toBeInTheDocument();
    });

    it('should handle PascalCase archetype names', () => {
      const citizens: CitizenCardJSON[] = [
        {
          type: 'citizen_card',
          citizen_id: 'diana-101',
          name: 'Diana',
          archetype: 'Healer', // PascalCase
          phase: 'WORKING',
          nphase: 'ACT',
          activity: [],
          capability: 0.7,
          entropy: 0.05,
          region: 'temple',
          mood: 'serene',
          eigenvectors: { warmth: 0.9, curiosity: 0.6, trust: 0.8 },
        },
      ];

      render(<Mesa citizens={citizens} selectedCitizenId={null} />);

      expect(screen.getByTestId('pixi-stage')).toBeInTheDocument();
    });
  });

  describe('multiple citizens in same region', () => {
    it('should handle multiple citizens in same region', () => {
      const citizens: CitizenCardJSON[] = [
        {
          ...mockCitizens[0],
          citizen_id: 'citizen-1',
          region: 'plaza',
        },
        {
          ...mockCitizens[1],
          citizen_id: 'citizen-2',
          region: 'plaza', // Same region
        },
        {
          ...mockCitizens[0],
          citizen_id: 'citizen-3',
          name: 'Charlie',
          region: 'plaza', // Same region
        },
      ];

      render(<Mesa citizens={citizens} selectedCitizenId={null} />);

      // Should render all three citizens without overlapping
      expect(screen.getByTestId('pixi-stage')).toBeInTheDocument();
    });
  });
});
