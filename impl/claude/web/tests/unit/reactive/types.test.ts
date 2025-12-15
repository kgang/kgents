import { describe, it, expect } from 'vitest';
import { isWidgetJSON } from '@/reactive/types';
import type {
  GlyphJSON,
  BarJSON,
  CitizenCardJSON,
  HStackJSON,
  VStackJSON,
  WidgetJSON,
} from '@/reactive/types';

describe('isWidgetJSON', () => {
  it('returns true for glyph type', () => {
    const widget: GlyphJSON = {
      type: 'glyph',
      char: '◉',
      phase: 'active',
      entropy: 0,
      animate: 'none',
    };
    expect(isWidgetJSON(widget)).toBe(true);
  });

  it('returns true for bar type', () => {
    const widget: BarJSON = {
      type: 'bar',
      value: 0.5,
      width: 10,
      orientation: 'horizontal',
      style: 'solid',
      entropy: 0,
      glyphs: [],
    };
    expect(isWidgetJSON(widget)).toBe(true);
  });

  it('returns true for citizen_card type', () => {
    const widget: CitizenCardJSON = {
      type: 'citizen_card',
      citizen_id: 'test',
      name: 'Test',
      archetype: 'Builder',
      phase: 'IDLE',
      nphase: 'SENSE',
      activity: [],
      capability: 1,
      entropy: 0,
      region: 'plaza',
      mood: 'calm',
      eigenvectors: { warmth: 0.5, curiosity: 0.5, trust: 0.5 },
    };
    expect(isWidgetJSON(widget)).toBe(true);
  });

  it('returns true for hstack type', () => {
    const widget: HStackJSON = {
      type: 'hstack',
      gap: 1,
      separator: null,
      children: [],
    };
    expect(isWidgetJSON(widget)).toBe(true);
  });

  it('returns true for vstack type', () => {
    const widget: VStackJSON = {
      type: 'vstack',
      gap: 1,
      separator: null,
      children: [],
    };
    expect(isWidgetJSON(widget)).toBe(true);
  });

  it('returns true for colony_dashboard type', () => {
    const widget: WidgetJSON = {
      type: 'colony_dashboard',
      colony_id: 'test',
      phase: 'MORNING',
      day: 1,
      metrics: { total_events: 0, total_tokens: 0, entropy_budget: 1 },
      citizens: [],
      grid_cols: 3,
      selected_citizen_id: null,
    };
    expect(isWidgetJSON(widget)).toBe(true);
  });

  it('returns false for null', () => {
    expect(isWidgetJSON(null)).toBe(false);
  });

  it('returns false for undefined', () => {
    expect(isWidgetJSON(undefined)).toBe(false);
  });

  it('returns false for string', () => {
    expect(isWidgetJSON('not a widget')).toBe(false);
  });

  it('returns false for number', () => {
    expect(isWidgetJSON(42)).toBe(false);
  });

  it('returns false for object without type', () => {
    expect(isWidgetJSON({ foo: 'bar' })).toBe(false);
  });

  it('returns false for object with unknown type', () => {
    expect(isWidgetJSON({ type: 'unknown_widget' })).toBe(false);
  });

  it('returns false for array', () => {
    expect(isWidgetJSON([{ type: 'glyph' }])).toBe(false);
  });
});

describe('Type Discrimination', () => {
  it('narrows type correctly in switch', () => {
    const widget: WidgetJSON = {
      type: 'citizen_card',
      citizen_id: 'test',
      name: 'Test',
      archetype: 'Builder',
      phase: 'IDLE',
      nphase: 'SENSE',
      activity: [],
      capability: 1,
      entropy: 0,
      region: 'plaza',
      mood: 'calm',
      eigenvectors: { warmth: 0.5, curiosity: 0.5, trust: 0.5 },
    };

    let name = '';
    switch (widget.type) {
      case 'citizen_card':
        // TypeScript should know widget is CitizenCardJSON here
        name = widget.name;
        break;
    }

    expect(name).toBe('Test');
  });

  it('allows nested widget types in composition', () => {
    const nested: HStackJSON = {
      type: 'hstack',
      gap: 1,
      separator: null,
      children: [
        {
          type: 'glyph',
          char: 'A',
          phase: 'idle',
          entropy: 0,
          animate: 'none',
        },
        {
          type: 'citizen_card',
          citizen_id: 'nested',
          name: 'Nested',
          archetype: 'Builder',
          phase: 'IDLE',
          nphase: 'SENSE',
          activity: [],
          capability: 1,
          entropy: 0,
          region: 'plaza',
          mood: 'calm',
          eigenvectors: { warmth: 0.5, curiosity: 0.5, trust: 0.5 },
        },
      ],
    };

    expect(nested.children.length).toBe(2);
    expect(nested.children[0].type).toBe('glyph');
    expect(nested.children[1].type).toBe('citizen_card');
  });
});
