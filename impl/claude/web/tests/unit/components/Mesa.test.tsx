import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { useTownStore } from '@/stores/townStore';
import type { CitizenSummary } from '@/api/types';

// Mock @pixi/react - Pixi.js requires WebGL which isn't available in jsdom
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
    <div
      data-testid="pixi-stage"
      data-width={width}
      data-height={height}
      style={{ width, height }}
    >
      {children}
    </div>
  ),
  Container: ({
    children,
    eventMode,
    onclick,
  }: {
    children: React.ReactNode;
    eventMode?: string;
    onclick?: (e: unknown) => void;
  }) => (
    <div data-testid="pixi-container" data-event-mode={eventMode}>
      {children}
    </div>
  ),
  Graphics: ({
    draw,
  }: {
    draw: (g: unknown) => void;
  }) => {
    // Call draw to simulate Pixi behavior with full mock Graphics API
    if (draw) {
      const mockGraphics = {
        clear: vi.fn().mockReturnThis(),
        lineStyle: vi.fn().mockReturnThis(),
        moveTo: vi.fn().mockReturnThis(),
        lineTo: vi.fn().mockReturnThis(),
        beginFill: vi.fn().mockReturnThis(),
        endFill: vi.fn().mockReturnThis(),
        drawCircle: vi.fn().mockReturnThis(),
        quadraticCurveTo: vi.fn().mockReturnThis(),
      };
      draw(mockGraphics);
    }
    return <div data-testid="pixi-graphics" />;
  },
  Text: ({
    text,
    x,
    y,
  }: {
    text: string;
    x: number;
    y: number;
    anchor?: number;
    style?: unknown;
  }) => (
    <div data-testid="pixi-text" data-x={x} data-y={y}>
      {text}
    </div>
  ),
}));

// Mock pixi.js
vi.mock('pixi.js', () => ({
  FederatedPointerEvent: class {},
  Rectangle: class {
    constructor(
      public x: number,
      public y: number,
      public width: number,
      public height: number
    ) {}
  },
  TextStyle: class {
    constructor(public options?: unknown) {}
  },
}));

// Import after mocks
import { Mesa } from '@/components/town/Mesa';

// Helper to create mock citizen
const createMockCitizen = (overrides: Partial<CitizenSummary> = {}): CitizenSummary => ({
  id: `citizen-${Math.random().toString(36).substr(2, 9)}`,
  name: 'Alice',
  archetype: 'Builder',
  region: 'square',
  phase: 'WORKING',
  is_evolving: false,
  ...overrides,
});

describe('Mesa', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useTownStore.getState().reset();
  });

  describe('rendering', () => {
    it('should render Pixi Stage with default dimensions', () => {
      render(<Mesa />);

      const stage = screen.getByTestId('pixi-stage');
      expect(stage).toBeInTheDocument();
      expect(stage).toHaveAttribute('data-width', '800');
      expect(stage).toHaveAttribute('data-height', '600');
    });

    it('should render Pixi Stage with custom dimensions', () => {
      render(<Mesa width={1200} height={900} />);

      const stage = screen.getByTestId('pixi-stage');
      expect(stage).toHaveAttribute('data-width', '1200');
      expect(stage).toHaveAttribute('data-height', '900');
    });

    it('should render container with event mode', () => {
      render(<Mesa />);

      const container = screen.getByTestId('pixi-container');
      expect(container).toHaveAttribute('data-event-mode', 'static');
    });
  });

  describe('citizens display', () => {
    it('should render citizen archetype letters', () => {
      const citizens = [
        createMockCitizen({ name: 'Alice', archetype: 'Builder' }),
        createMockCitizen({ name: 'Bob', archetype: 'Trader' }),
        createMockCitizen({ name: 'Carol', archetype: 'Healer' }),
      ];

      useTownStore.setState({ citizens });

      render(<Mesa />);

      // Should render archetype initial letters (B, T, H)
      const textElements = screen.getAllByTestId('pixi-text');
      const textContents = textElements.map((el) => el.textContent);

      expect(textContents).toContain('B'); // Builder
      expect(textContents).toContain('T'); // Trader
      expect(textContents).toContain('H'); // Healer
    });

    it('should render citizen names when hovered', () => {
      const citizen = createMockCitizen({ id: 'c-1', name: 'Alice' });
      useTownStore.setState({
        citizens: [citizen],
        hoveredCitizenId: 'c-1',
      });

      render(<Mesa />);

      // When hovered, name should be visible
      const textElements = screen.getAllByTestId('pixi-text');
      const textContents = textElements.map((el) => el.textContent);

      expect(textContents).toContain('Alice');
    });

    it('should render citizen names when selected', () => {
      const citizen = createMockCitizen({ id: 'c-1', name: 'Bob' });
      useTownStore.setState({
        citizens: [citizen],
        selectedCitizenId: 'c-1',
      });

      render(<Mesa />);

      const textElements = screen.getAllByTestId('pixi-text');
      const textContents = textElements.map((el) => el.textContent);

      expect(textContents).toContain('Bob');
    });

    it('should not render names for non-hovered, non-selected citizens', () => {
      const citizens = [
        createMockCitizen({ id: 'c-1', name: 'Alice' }),
        createMockCitizen({ id: 'c-2', name: 'Bob' }),
      ];

      useTownStore.setState({
        citizens,
        selectedCitizenId: null,
        hoveredCitizenId: null,
      });

      render(<Mesa />);

      const textElements = screen.getAllByTestId('pixi-text');
      const textContents = textElements.map((el) => el.textContent);

      // Should only have archetype letters, not names
      expect(textContents).not.toContain('Alice');
      expect(textContents).not.toContain('Bob');
    });
  });

  describe('citizen positioning', () => {
    it('should position citizens by region', () => {
      const citizens = [
        createMockCitizen({ name: 'Alice', region: 'market' }),
        createMockCitizen({ name: 'Bob', region: 'temple' }),
      ];

      useTownStore.setState({ citizens });

      render(<Mesa />);

      const textElements = screen.getAllByTestId('pixi-text');

      // Each text element should have position data
      textElements.forEach((el) => {
        expect(el).toHaveAttribute('data-x');
        expect(el).toHaveAttribute('data-y');
      });
    });

    it('should offset multiple citizens in same region', () => {
      const citizens = [
        createMockCitizen({ id: 'c-1', name: 'Alice', region: 'square' }),
        createMockCitizen({ id: 'c-2', name: 'Bob', region: 'square' }),
        createMockCitizen({ id: 'c-3', name: 'Carol', region: 'square' }),
      ];

      useTownStore.setState({ citizens });

      render(<Mesa />);

      const textElements = screen.getAllByTestId('pixi-text');

      // Get positions (exclude names, just get archetype letters)
      const positions = textElements
        .filter((el) => el.textContent?.length === 1) // Archetype letters
        .map((el) => ({
          x: parseFloat(el.getAttribute('data-x') || '0'),
          y: parseFloat(el.getAttribute('data-y') || '0'),
        }));

      // All positions should be different
      const uniquePositions = new Set(positions.map((p) => `${p.x},${p.y}`));
      expect(uniquePositions.size).toBe(3);
    });
  });

  describe('graphics layers', () => {
    it('should render multiple graphics layers', () => {
      render(<Mesa />);

      const graphics = screen.getAllByTestId('pixi-graphics');

      // Should have: grid, regions, interactions, and one per citizen
      expect(graphics.length).toBeGreaterThanOrEqual(3);
    });
  });

  describe('empty state', () => {
    it('should render correctly with no citizens', () => {
      useTownStore.setState({ citizens: [] });

      render(<Mesa />);

      const stage = screen.getByTestId('pixi-stage');
      expect(stage).toBeInTheDocument();

      // Should still render grid and region graphics
      const graphics = screen.getAllByTestId('pixi-graphics');
      expect(graphics.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe('store integration', () => {
    it('should read citizens from town store', () => {
      const citizens = [
        createMockCitizen({ archetype: 'Scholar' }),
        createMockCitizen({ archetype: 'Watcher' }),
      ];

      useTownStore.setState({ citizens });

      render(<Mesa />);

      const textElements = screen.getAllByTestId('pixi-text');
      const textContents = textElements.map((el) => el.textContent);

      expect(textContents).toContain('S'); // Scholar
      expect(textContents).toContain('W'); // Watcher
    });

    it('should read selection state from town store', () => {
      const citizen = createMockCitizen({ id: 'selected-one', name: 'TestCitizen' });
      useTownStore.setState({
        citizens: [citizen],
        selectedCitizenId: 'selected-one',
      });

      render(<Mesa />);

      // Should show name when selected
      const textElements = screen.getAllByTestId('pixi-text');
      expect(textElements.some((el) => el.textContent === 'TestCitizen')).toBe(true);
    });
  });

  describe('archetypes', () => {
    const archetypes = ['Builder', 'Trader', 'Healer', 'Scholar', 'Watcher'] as const;

    it.each(archetypes)('should render %s archetype initial', (archetype) => {
      const citizen = createMockCitizen({ archetype });
      useTownStore.setState({ citizens: [citizen] });

      render(<Mesa />);

      const textElements = screen.getAllByTestId('pixi-text');
      const textContents = textElements.map((el) => el.textContent);

      expect(textContents).toContain(archetype[0]);
    });
  });
});
