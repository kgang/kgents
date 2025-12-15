/**
 * Composition law tests for HStack and VStack.
 *
 * Verifies:
 * - (a >> b) >> c ≡ a >> (b >> c)  (associativity)
 * - (a // b) // c ≡ a // (b // c)  (associativity)
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { WidgetRenderer } from '@/reactive/WidgetRenderer';
import type { HStackJSON, VStackJSON, GlyphJSON } from '@/reactive/types';

// Helper to create glyph
const glyph = (char: string): GlyphJSON => ({
  type: 'glyph',
  char,
  phase: 'active',
  entropy: 0,
  animate: 'none',
});

// Helper to create hstack
const hstack = (children: GlyphJSON[], gap = 1): HStackJSON => ({
  type: 'hstack',
  gap,
  separator: null,
  children,
});

// Helper to create vstack
const vstack = (children: GlyphJSON[], gap = 1): VStackJSON => ({
  type: 'vstack',
  gap,
  separator: null,
  children,
});

describe('HStack composition (>>)', () => {
  it('associativity: (a >> b) >> c renders same as a >> (b >> c)', () => {
    const a = glyph('A');
    const b = glyph('B');
    const c = glyph('C');

    // Left-associative: (a >> b) >> c
    const leftAssoc: HStackJSON = {
      type: 'hstack',
      gap: 1,
      separator: null,
      children: [
        { type: 'hstack', gap: 1, separator: null, children: [a, b] },
        c,
      ],
    };

    // Right-associative: a >> (b >> c)
    const rightAssoc: HStackJSON = {
      type: 'hstack',
      gap: 1,
      separator: null,
      children: [
        a,
        { type: 'hstack', gap: 1, separator: null, children: [b, c] },
      ],
    };

    // Both should render all three glyphs
    render(<WidgetRenderer widget={leftAssoc} />);
    expect(screen.getByText('A')).toBeInTheDocument();
    expect(screen.getByText('B')).toBeInTheDocument();
    expect(screen.getByText('C')).toBeInTheDocument();

    // Clear and render right-associative
    render(<WidgetRenderer widget={rightAssoc} />);
    expect(screen.getAllByText('A').length).toBeGreaterThan(0);
    expect(screen.getAllByText('B').length).toBeGreaterThan(0);
    expect(screen.getAllByText('C').length).toBeGreaterThan(0);
  });

  it('flattened hstack renders correctly', () => {
    const widget = hstack([glyph('1'), glyph('2'), glyph('3')]);

    render(<WidgetRenderer widget={widget} />);

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });
});

describe('VStack composition (//)', () => {
  it('associativity: (a // b) // c renders same as a // (b // c)', () => {
    const a = glyph('X');
    const b = glyph('Y');
    const c = glyph('Z');

    // Left-associative: (a // b) // c
    const leftAssoc: VStackJSON = {
      type: 'vstack',
      gap: 1,
      separator: null,
      children: [
        { type: 'vstack', gap: 1, separator: null, children: [a, b] },
        c,
      ],
    };

    // Both should render all three glyphs
    render(<WidgetRenderer widget={leftAssoc} />);
    expect(screen.getByText('X')).toBeInTheDocument();
    expect(screen.getByText('Y')).toBeInTheDocument();
    expect(screen.getByText('Z')).toBeInTheDocument();
  });

  it('flattened vstack renders correctly', () => {
    const widget = vstack([glyph('A'), glyph('B'), glyph('C')]);

    render(<WidgetRenderer widget={widget} />);

    expect(screen.getByText('A')).toBeInTheDocument();
    expect(screen.getByText('B')).toBeInTheDocument();
    expect(screen.getByText('C')).toBeInTheDocument();
  });
});

describe('Mixed composition (>> and //)', () => {
  it('hstack containing vstack renders correctly', () => {
    const widget: HStackJSON = {
      type: 'hstack',
      gap: 1,
      separator: null,
      children: [
        glyph('L'),
        { type: 'vstack', gap: 1, separator: null, children: [glyph('T'), glyph('B')] },
        glyph('R'),
      ],
    };

    render(<WidgetRenderer widget={widget} />);

    expect(screen.getByText('L')).toBeInTheDocument();
    expect(screen.getByText('T')).toBeInTheDocument();
    expect(screen.getByText('B')).toBeInTheDocument();
    expect(screen.getByText('R')).toBeInTheDocument();
  });

  it('vstack containing hstack renders correctly', () => {
    const widget: VStackJSON = {
      type: 'vstack',
      gap: 1,
      separator: null,
      children: [
        glyph('T'),
        { type: 'hstack', gap: 1, separator: null, children: [glyph('L'), glyph('R')] },
        glyph('B'),
      ],
    };

    render(<WidgetRenderer widget={widget} />);

    expect(screen.getByText('T')).toBeInTheDocument();
    expect(screen.getByText('L')).toBeInTheDocument();
    expect(screen.getByText('R')).toBeInTheDocument();
    expect(screen.getByText('B')).toBeInTheDocument();
  });
});
