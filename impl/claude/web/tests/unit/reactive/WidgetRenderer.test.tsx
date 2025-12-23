import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { WidgetRenderer, Glyph, Bar, Sparkline } from '@/reactive/WidgetRenderer';
import type { GlyphJSON, BarJSON, SparklineJSON, HStackJSON, VStackJSON } from '@/reactive/types';

// Note: CitizenCard, ColonyDashboard tests removed 2025-12-23 (components deleted)

// =============================================================================
// Test Data Factories
// =============================================================================

const createGlyphJSON = (overrides: Partial<GlyphJSON> = {}): GlyphJSON => ({
  type: 'glyph',
  char: '◉',
  phase: 'active',
  entropy: 0,
  animate: 'none',
  ...overrides,
});

const createBarJSON = (overrides: Partial<BarJSON> = {}): BarJSON => ({
  type: 'bar',
  value: 0.75,
  width: 10,
  orientation: 'horizontal',
  style: 'solid',
  entropy: 0,
  glyphs: [],
  ...overrides,
});

const createSparklineJSON = (overrides: Partial<SparklineJSON> = {}): SparklineJSON => ({
  type: 'sparkline',
  values: [0.2, 0.4, 0.6, 0.8, 1.0],
  max_length: 20,
  entropy: 0,
  glyphs: [],
  ...overrides,
});

const createHStackJSON = (overrides: Partial<HStackJSON> = {}): HStackJSON => ({
  type: 'hstack',
  gap: 1,
  separator: null,
  children: [],
  ...overrides,
});

const createVStackJSON = (overrides: Partial<VStackJSON> = {}): VStackJSON => ({
  type: 'vstack',
  gap: 1,
  separator: null,
  children: [],
  ...overrides,
});

// =============================================================================
// Glyph Tests
// =============================================================================

describe('Glyph', () => {
  it('renders the character', () => {
    render(<Glyph {...createGlyphJSON({ char: '◉' })} />);
    expect(screen.getByText('◉')).toBeInTheDocument();
  });

  it('applies foreground color', () => {
    render(<Glyph {...createGlyphJSON({ fg: '#ff0000' })} />);
    const glyph = screen.getByText('◉');
    expect(glyph).toHaveStyle({ color: '#ff0000' });
  });

  it('applies animation class', () => {
    render(<Glyph {...createGlyphJSON({ animate: 'pulse' })} />);
    const glyph = screen.getByText('◉');
    expect(glyph).toHaveClass('animate-pulse');
  });
});

// =============================================================================
// Bar Tests
// =============================================================================

describe('Bar', () => {
  it('renders with correct fill ratio', () => {
    render(<Bar {...createBarJSON({ value: 0.5, width: 10 })} />);
    const bar = document.querySelector('.kgents-bar');
    expect(bar).toBeInTheDocument();
  });

  it('renders label when provided', () => {
    render(<Bar {...createBarJSON({ label: 'CPU' })} />);
    expect(screen.getByText('CPU:')).toBeInTheDocument();
  });
});

// =============================================================================
// Sparkline Tests
// =============================================================================

describe('Sparkline', () => {
  it('renders sparkline characters', () => {
    render(<Sparkline {...createSparklineJSON({ values: [0.2, 0.4, 0.6, 0.8, 1.0] })} />);
    const sparkline = document.querySelector('.kgents-sparkline');
    expect(sparkline).toBeInTheDocument();
  });

  it('renders label when provided', () => {
    render(<Sparkline {...createSparklineJSON({ label: 'Activity' })} />);
    expect(screen.getByText('Activity:')).toBeInTheDocument();
  });
});

// =============================================================================
// HStack Tests
// =============================================================================

describe('HStack', () => {
  it('renders children horizontally', () => {
    const children: GlyphJSON[] = [createGlyphJSON({ char: 'A' }), createGlyphJSON({ char: 'B' })];
    const widget = createHStackJSON({ children });

    render(<WidgetRenderer widget={widget} />);

    expect(screen.getByText('A')).toBeInTheDocument();
    expect(screen.getByText('B')).toBeInTheDocument();
  });
});

// =============================================================================
// VStack Tests
// =============================================================================

describe('VStack', () => {
  it('renders children vertically', () => {
    const children: GlyphJSON[] = [createGlyphJSON({ char: '1' }), createGlyphJSON({ char: '2' })];
    const widget = createVStackJSON({ children });

    render(<WidgetRenderer widget={widget} />);

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
  });
});

// =============================================================================
// WidgetRenderer Dispatch Tests
// =============================================================================

describe('WidgetRenderer', () => {
  it('dispatches to Glyph for type=glyph', () => {
    render(<WidgetRenderer widget={createGlyphJSON({ char: 'G' })} />);
    expect(screen.getByText('G')).toBeInTheDocument();
  });

  it('dispatches to Bar for type=bar', () => {
    render(<WidgetRenderer widget={createBarJSON({ label: 'Test Bar' })} />);
    expect(screen.getByText('Test Bar:')).toBeInTheDocument();
  });

  it('dispatches to Sparkline for type=sparkline', () => {
    render(<WidgetRenderer widget={createSparklineJSON({ label: 'Spark' })} />);
    expect(screen.getByText('Spark:')).toBeInTheDocument();
  });

  it('handles nested composition', () => {
    const nested: VStackJSON = {
      type: 'vstack',
      gap: 1,
      separator: null,
      children: [
        {
          type: 'hstack',
          gap: 1,
          separator: null,
          children: [createGlyphJSON({ char: 'X' }), createGlyphJSON({ char: 'Y' })],
        },
        createGlyphJSON({ char: 'Z' }),
      ],
    };

    render(<WidgetRenderer widget={nested} />);

    expect(screen.getByText('X')).toBeInTheDocument();
    expect(screen.getByText('Y')).toBeInTheDocument();
    expect(screen.getByText('Z')).toBeInTheDocument();
  });
});
