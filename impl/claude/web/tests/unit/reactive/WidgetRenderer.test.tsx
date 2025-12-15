import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  WidgetRenderer,
  Glyph,
  Bar,
  Sparkline,
  CitizenCard,
  ColonyDashboard,
} from '@/reactive/WidgetRenderer';
import type {
  GlyphJSON,
  BarJSON,
  SparklineJSON,
  CitizenCardJSON,
  HStackJSON,
  VStackJSON,
  ColonyDashboardJSON,
} from '@/reactive/types';

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

const createCitizenCardJSON = (overrides: Partial<CitizenCardJSON> = {}): CitizenCardJSON => ({
  type: 'citizen_card',
  citizen_id: 'alice-123',
  name: 'Alice',
  archetype: 'Builder',
  phase: 'WORKING',
  nphase: 'ACT',
  activity: [0.3, 0.5, 0.7, 0.6, 0.8],
  capability: 0.85,
  entropy: 0.1,
  region: 'plaza',
  mood: 'focused',
  eigenvectors: {
    warmth: 0.7,
    curiosity: 0.8,
    trust: 0.6,
  },
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

const createColonyDashboardJSON = (
  overrides: Partial<ColonyDashboardJSON> = {}
): ColonyDashboardJSON => ({
  type: 'colony_dashboard',
  colony_id: 'colony-001',
  phase: 'AFTERNOON',
  day: 5,
  metrics: {
    total_events: 142,
    total_tokens: 5000,
    entropy_budget: 0.75,
  },
  citizens: [],
  grid_cols: 3,
  selected_citizen_id: null,
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

  it('applies background color', () => {
    render(<Glyph {...createGlyphJSON({ bg: '#0000ff' })} />);
    const glyph = screen.getByText('◉');
    expect(glyph).toHaveStyle({ backgroundColor: '#0000ff' });
  });

  it('applies animation class', () => {
    render(<Glyph {...createGlyphJSON({ animate: 'pulse' })} />);
    const glyph = screen.getByText('◉');
    expect(glyph).toHaveClass('animate-pulse');
  });

  it('applies distortion transform', () => {
    render(
      <Glyph
        {...createGlyphJSON({
          distortion: {
            blur: 0,
            skew: 5,
            jitter_x: 2,
            jitter_y: 3,
            pulse: 1,
          },
        })}
      />
    );
    const glyph = screen.getByText('◉');
    expect(glyph.style.transform).toContain('skewX(5deg)');
    expect(glyph.style.transform).toContain('translate(2px, 3px)');
  });

  it('sets data-phase attribute', () => {
    render(<Glyph {...createGlyphJSON({ phase: 'thinking' })} />);
    const glyph = screen.getByText('◉');
    expect(glyph).toHaveAttribute('data-phase', 'thinking');
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
    // 5 filled, 5 empty
    expect(bar?.textContent).toContain('█████');
    expect(bar?.textContent).toContain('░░░░░');
  });

  it('renders with dots style', () => {
    render(<Bar {...createBarJSON({ value: 0.3, width: 10, style: 'dots' })} />);
    const bar = document.querySelector('.kgents-bar');
    expect(bar?.textContent).toContain('●●●');
    expect(bar?.textContent).toContain('○○○○○○○');
  });

  it('renders label when provided', () => {
    render(<Bar {...createBarJSON({ label: 'CPU' })} />);
    expect(screen.getByText('CPU:')).toBeInTheDocument();
  });

  it('applies foreground color', () => {
    render(<Bar {...createBarJSON({ fg: '#00ff00' })} />);
    const bar = document.querySelector('.kgents-bar');
    expect(bar).toHaveStyle({ color: '#00ff00' });
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
    // Should contain vertical bar characters
    expect(sparkline?.textContent).toMatch(/[▁▂▃▄▅▆▇█]+/);
  });

  it('renders label when provided', () => {
    render(<Sparkline {...createSparklineJSON({ label: 'Activity' })} />);
    expect(screen.getByText('Activity:')).toBeInTheDocument();
  });

  it('applies foreground color', () => {
    render(<Sparkline {...createSparklineJSON({ fg: '#ff00ff' })} />);
    const sparkline = document.querySelector('.kgents-sparkline');
    expect(sparkline).toHaveStyle({ color: '#ff00ff' });
  });
});

// =============================================================================
// CitizenCard Tests
// =============================================================================

describe('CitizenCard', () => {
  it('renders citizen name', () => {
    render(<CitizenCard {...createCitizenCardJSON({ name: 'Bob' })} />);
    expect(screen.getByText('Bob')).toBeInTheDocument();
  });

  it('renders phase glyph', () => {
    render(<CitizenCard {...createCitizenCardJSON({ phase: 'WORKING' })} />);
    expect(screen.getByText('●')).toBeInTheDocument();
  });

  it('renders archetype', () => {
    render(<CitizenCard {...createCitizenCardJSON({ archetype: 'Healer' })} />);
    expect(screen.getByText('Healer')).toBeInTheDocument();
  });

  it('renders N-Phase indicator', () => {
    render(<CitizenCard {...createCitizenCardJSON({ nphase: 'SENSE' })} />);
    expect(screen.getByText('[S]')).toBeInTheDocument();
  });

  it('renders mood', () => {
    render(<CitizenCard {...createCitizenCardJSON({ mood: 'contemplative' })} />);
    expect(screen.getByText('contemplative')).toBeInTheDocument();
  });

  it('renders activity sparkline when present', () => {
    render(<CitizenCard {...createCitizenCardJSON({ activity: [0.5, 0.6, 0.7] })} />);
    const card = document.querySelector('.kgents-citizen-card');
    // Activity sparkline should be rendered
    expect(card?.textContent).toMatch(/[▁▂▃▄▅▆▇█]+/);
  });

  it('calls onSelect with citizen_id when clicked', () => {
    const onSelect = vi.fn();
    render(<CitizenCard {...createCitizenCardJSON({ citizen_id: 'test-id' })} onSelect={onSelect} />);

    const card = screen.getByTestId('citizen-card');
    fireEvent.click(card);

    expect(onSelect).toHaveBeenCalledWith('test-id');
  });

  it('applies selected styling when isSelected is true', () => {
    render(<CitizenCard {...createCitizenCardJSON()} isSelected={true} />);
    const card = screen.getByTestId('citizen-card');
    expect(card).toHaveClass('border-blue-500');
    expect(card).toHaveClass('bg-blue-50');
  });

  it('sets data-citizen-id attribute', () => {
    render(<CitizenCard {...createCitizenCardJSON({ citizen_id: 'xyz-456' })} />);
    const card = screen.getByTestId('citizen-card');
    expect(card).toHaveAttribute('data-citizen-id', 'xyz-456');
  });
});

// =============================================================================
// HStack Tests
// =============================================================================

describe('HStack', () => {
  it('renders children horizontally (via WidgetRenderer)', () => {
    const children: GlyphJSON[] = [
      createGlyphJSON({ char: 'A' }),
      createGlyphJSON({ char: 'B' }),
      createGlyphJSON({ char: 'C' }),
    ];
    const widget = createHStackJSON({ children });

    render(<WidgetRenderer widget={widget} />);

    expect(screen.getByText('A')).toBeInTheDocument();
    expect(screen.getByText('B')).toBeInTheDocument();
    expect(screen.getByText('C')).toBeInTheDocument();
  });

  it('renders separator between children', () => {
    const children: GlyphJSON[] = [
      createGlyphJSON({ char: 'X' }),
      createGlyphJSON({ char: 'Y' }),
    ];
    const widget = createHStackJSON({ children, separator: '|' });

    render(<WidgetRenderer widget={widget} />);

    expect(screen.getByText('|')).toBeInTheDocument();
  });

  it('applies gap styling', () => {
    const children: GlyphJSON[] = [createGlyphJSON({ char: 'Z' })];
    const widget = createHStackJSON({ children, gap: 2 });

    render(<WidgetRenderer widget={widget} />);

    const hstack = document.querySelector('.kgents-hstack');
    expect(hstack).toHaveStyle({ gap: '16px' }); // gap * 8
  });

  it('passes onSelect to children', () => {
    const onSelect = vi.fn();
    const children: CitizenCardJSON[] = [createCitizenCardJSON({ citizen_id: 'child-1' })];
    const widget = createHStackJSON({ children });

    render(<WidgetRenderer widget={widget} onSelect={onSelect} />);

    fireEvent.click(screen.getByTestId('citizen-card'));
    expect(onSelect).toHaveBeenCalledWith('child-1');
  });
});

// =============================================================================
// VStack Tests
// =============================================================================

describe('VStack', () => {
  it('renders children vertically (via WidgetRenderer)', () => {
    const children: GlyphJSON[] = [
      createGlyphJSON({ char: '1' }),
      createGlyphJSON({ char: '2' }),
      createGlyphJSON({ char: '3' }),
    ];
    const widget = createVStackJSON({ children });

    render(<WidgetRenderer widget={widget} />);

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('applies gap styling', () => {
    const children: GlyphJSON[] = [createGlyphJSON({ char: 'V' })];
    const widget = createVStackJSON({ children, gap: 2 });

    render(<WidgetRenderer widget={widget} />);

    const vstack = document.querySelector('.kgents-vstack');
    expect(vstack).toHaveStyle({ gap: '32px' }); // gap * 16
  });

  it('renders separator between children', () => {
    const children: GlyphJSON[] = [
      createGlyphJSON({ char: 'A' }),
      createGlyphJSON({ char: 'B' }),
    ];
    const widget = createVStackJSON({ children, separator: '---' });

    render(<WidgetRenderer widget={widget} />);

    expect(screen.getByText('---')).toBeInTheDocument();
  });
});

// =============================================================================
// ColonyDashboard Tests
// =============================================================================

describe('ColonyDashboard', () => {
  it('renders header with phase and day', () => {
    render(<ColonyDashboard {...createColonyDashboardJSON({ phase: 'EVENING', day: 10 })} />);

    expect(screen.getByText('AGENT TOWN DASHBOARD')).toBeInTheDocument();
    expect(screen.getByText(/EVENING/)).toBeInTheDocument();
    expect(screen.getByText(/Day 10/)).toBeInTheDocument();
  });

  it('renders status bar with metrics', () => {
    render(
      <ColonyDashboard
        {...createColonyDashboardJSON({
          metrics: { total_events: 200, total_tokens: 8000, entropy_budget: 0.5 },
        })}
      />
    );

    expect(screen.getByText(/Events:/)).toBeInTheDocument();
    expect(screen.getByText('200')).toBeInTheDocument();
  });

  it('renders citizens in grid', () => {
    const citizens: CitizenCardJSON[] = [
      createCitizenCardJSON({ citizen_id: 'c1', name: 'Alice' }),
      createCitizenCardJSON({ citizen_id: 'c2', name: 'Bob' }),
      createCitizenCardJSON({ citizen_id: 'c3', name: 'Carol' }),
    ];

    render(<ColonyDashboard {...createColonyDashboardJSON({ citizens, grid_cols: 2 })} />);

    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Bob')).toBeInTheDocument();
    expect(screen.getByText('Carol')).toBeInTheDocument();
  });

  it('renders footer with entropy and tokens', () => {
    render(
      <ColonyDashboard
        {...createColonyDashboardJSON({
          metrics: { total_events: 100, total_tokens: 5000, entropy_budget: 0.33 },
        })}
      />
    );

    expect(screen.getByText(/Entropy: 0\.33/)).toBeInTheDocument();
    expect(screen.getByText(/Tokens: 5000/)).toBeInTheDocument();
  });

  it('highlights selected citizen', () => {
    const citizens: CitizenCardJSON[] = [
      createCitizenCardJSON({ citizen_id: 'selected-one', name: 'Selected' }),
      createCitizenCardJSON({ citizen_id: 'other', name: 'Other' }),
    ];

    render(
      <ColonyDashboard
        {...createColonyDashboardJSON({ citizens, selected_citizen_id: 'selected-one' })}
      />
    );

    const cards = screen.getAllByTestId('citizen-card');
    expect(cards[0]).toHaveClass('border-blue-500');
    expect(cards[1]).not.toHaveClass('border-blue-500');
  });

  it('calls onSelectCitizen when citizen clicked', () => {
    const onSelectCitizen = vi.fn();
    const citizens: CitizenCardJSON[] = [createCitizenCardJSON({ citizen_id: 'click-me' })];

    render(
      <ColonyDashboard
        {...createColonyDashboardJSON({ citizens })}
        onSelectCitizen={onSelectCitizen}
      />
    );

    fireEvent.click(screen.getByTestId('citizen-card'));
    expect(onSelectCitizen).toHaveBeenCalledWith('click-me');
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

  it('dispatches to CitizenCard for type=citizen_card', () => {
    render(<WidgetRenderer widget={createCitizenCardJSON({ name: 'Dispatch Test' })} />);
    expect(screen.getByText('Dispatch Test')).toBeInTheDocument();
  });

  it('dispatches to HStack for type=hstack', () => {
    const widget = createHStackJSON({
      children: [createGlyphJSON({ char: 'H' })],
    });
    render(<WidgetRenderer widget={widget} />);
    expect(screen.getByText('H')).toBeInTheDocument();
  });

  it('dispatches to VStack for type=vstack', () => {
    const widget = createVStackJSON({
      children: [createGlyphJSON({ char: 'V' })],
    });
    render(<WidgetRenderer widget={widget} />);
    expect(screen.getByText('V')).toBeInTheDocument();
  });

  it('dispatches to ColonyDashboard for type=colony_dashboard', () => {
    render(<WidgetRenderer widget={createColonyDashboardJSON()} />);
    expect(screen.getByText('AGENT TOWN DASHBOARD')).toBeInTheDocument();
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
          children: [
            createCitizenCardJSON({ name: 'Nested Alice' }),
            createCitizenCardJSON({ name: 'Nested Bob' }),
          ],
        },
        createCitizenCardJSON({ name: 'Nested Carol' }),
      ],
    };

    render(<WidgetRenderer widget={nested} />);

    expect(screen.getByText('Nested Alice')).toBeInTheDocument();
    expect(screen.getByText('Nested Bob')).toBeInTheDocument();
    expect(screen.getByText('Nested Carol')).toBeInTheDocument();
  });

  it('propagates onSelect through nested structure', () => {
    const onSelect = vi.fn();
    const nested: HStackJSON = {
      type: 'hstack',
      gap: 1,
      separator: null,
      children: [createCitizenCardJSON({ citizen_id: 'deep-nested' })],
    };

    render(<WidgetRenderer widget={nested} onSelect={onSelect} />);

    fireEvent.click(screen.getByTestId('citizen-card'));
    expect(onSelect).toHaveBeenCalledWith('deep-nested');
  });

  it('propagates selectedId through nested structure', () => {
    const nested: HStackJSON = {
      type: 'hstack',
      gap: 1,
      separator: null,
      children: [
        createCitizenCardJSON({ citizen_id: 'sel-1' }),
        createCitizenCardJSON({ citizen_id: 'sel-2' }),
      ],
    };

    render(<WidgetRenderer widget={nested} selectedId="sel-1" />);

    const cards = screen.getAllByTestId('citizen-card');
    expect(cards[0]).toHaveClass('border-blue-500');
    expect(cards[1]).not.toHaveClass('border-blue-500');
  });
});
