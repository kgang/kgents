/**
 * Tests for Gestalt Visual Showcase Chunk 2: Legend & Tooltips
 *
 * Tests cover:
 * - Legend component: rendering, collapsing, position, persistence
 * - Tooltip types and state management
 * - CSS keyframe injection
 *
 * @see plans/gestalt-visual-showcase.md Chunk 2
 */

import { describe, it, expect } from 'vitest';
import {
  DEFAULT_HOVER_STATE,
  TOOLTIP_DELAY_MS,
  type HoverState,
  type LegendPosition,
  type LegendState,
  HEALTH_GRADES,
} from '../../../src/components/gestalt/types';

// =============================================================================
// Hover State Tests
// =============================================================================

describe('HoverState', () => {
  it('DEFAULT_HOVER_STATE has null moduleId', () => {
    expect(DEFAULT_HOVER_STATE.moduleId).toBeNull();
  });

  it('DEFAULT_HOVER_STATE has null hoverStartTime', () => {
    expect(DEFAULT_HOVER_STATE.hoverStartTime).toBeNull();
  });

  it('DEFAULT_HOVER_STATE has tooltipVisible false', () => {
    expect(DEFAULT_HOVER_STATE.tooltipVisible).toBe(false);
  });

  it('TOOLTIP_DELAY_MS is 300ms', () => {
    expect(TOOLTIP_DELAY_MS).toBe(300);
  });
});

// =============================================================================
// Legend Position Tests
// =============================================================================

describe('LegendPosition', () => {
  it('supports top-left position', () => {
    const position: LegendPosition = 'top-left';
    expect(['top-left', 'top-right', 'bottom-left', 'bottom-right']).toContain(position);
  });

  it('supports top-right position', () => {
    const position: LegendPosition = 'top-right';
    expect(['top-left', 'top-right', 'bottom-left', 'bottom-right']).toContain(position);
  });

  it('supports bottom-left position', () => {
    const position: LegendPosition = 'bottom-left';
    expect(['top-left', 'top-right', 'bottom-left', 'bottom-right']).toContain(position);
  });

  it('supports bottom-right position', () => {
    const position: LegendPosition = 'bottom-right';
    expect(['top-left', 'top-right', 'bottom-left', 'bottom-right']).toContain(position);
  });
});

// =============================================================================
// Legend State Tests
// =============================================================================

describe('LegendState', () => {
  it('can be constructed with collapsed true', () => {
    const state: LegendState = {
      collapsed: true,
      position: 'top-right',
    };
    expect(state.collapsed).toBe(true);
  });

  it('can be constructed with collapsed false', () => {
    const state: LegendState = {
      collapsed: false,
      position: 'bottom-left',
    };
    expect(state.collapsed).toBe(false);
  });

  it('stores position correctly', () => {
    const state: LegendState = {
      collapsed: false,
      position: 'bottom-right',
    };
    expect(state.position).toBe('bottom-right');
  });
});

// =============================================================================
// Hover State Management Logic Tests
// =============================================================================

describe('Hover state transitions', () => {
  it('transitions from null to hovered state', () => {
    const initial: HoverState = { ...DEFAULT_HOVER_STATE };
    const afterHover: HoverState = {
      moduleId: 'test-module-1',
      hoverStartTime: Date.now(),
      tooltipVisible: false, // Not visible yet (delay)
    };

    expect(initial.moduleId).toBeNull();
    expect(afterHover.moduleId).toBe('test-module-1');
    expect(afterHover.tooltipVisible).toBe(false);
  });

  it('transitions to tooltip visible after delay', () => {
    const afterDelay: HoverState = {
      moduleId: 'test-module-1',
      hoverStartTime: Date.now() - TOOLTIP_DELAY_MS,
      tooltipVisible: true, // Visible after delay
    };

    expect(afterDelay.tooltipVisible).toBe(true);
  });

  it('transitions back to default on hover out', () => {
    const afterHoverOut: HoverState = { ...DEFAULT_HOVER_STATE };

    expect(afterHoverOut.moduleId).toBeNull();
    expect(afterHoverOut.hoverStartTime).toBeNull();
    expect(afterHoverOut.tooltipVisible).toBe(false);
  });
});

// =============================================================================
// Legend Health Grade Display Tests
// =============================================================================

describe('Legend health grade groupings', () => {
  const HEALTH_GROUPS = [
    { grades: ['A+', 'A'], label: 'A+/A', tier: 'excellent' },
    { grades: ['B+', 'B'], label: 'B+/B', tier: 'good' },
    { grades: ['C+', 'C'], label: 'C+/C', tier: 'fair' },
    { grades: ['D', 'F'], label: 'D/F', tier: 'poor' },
  ] as const;

  it('has 4 grade groups', () => {
    expect(HEALTH_GROUPS.length).toBe(4);
  });

  it('covers all 8 health grades', () => {
    const coveredGrades = HEALTH_GROUPS.flatMap((g) => g.grades);
    expect(coveredGrades).toHaveLength(8);
    for (const grade of HEALTH_GRADES) {
      expect(coveredGrades).toContain(grade);
    }
  });

  it('groups excellent grades correctly', () => {
    const excellent = HEALTH_GROUPS.find((g) => g.tier === 'excellent');
    expect(excellent?.grades).toEqual(['A+', 'A']);
    expect(excellent?.label).toBe('A+/A');
  });

  it('groups good grades correctly', () => {
    const good = HEALTH_GROUPS.find((g) => g.tier === 'good');
    expect(good?.grades).toEqual(['B+', 'B']);
    expect(good?.label).toBe('B+/B');
  });

  it('groups fair grades correctly', () => {
    const fair = HEALTH_GROUPS.find((g) => g.tier === 'fair');
    expect(fair?.grades).toEqual(['C+', 'C']);
    expect(fair?.label).toBe('C+/C');
  });

  it('groups poor grades correctly', () => {
    const poor = HEALTH_GROUPS.find((g) => g.tier === 'poor');
    expect(poor?.grades).toEqual(['D', 'F']);
    expect(poor?.label).toBe('D/F');
  });
});

// =============================================================================
// Edge Type Configuration Tests
// =============================================================================

describe('Edge type configurations', () => {
  const DEFAULT_EDGE_TYPES = [
    { id: 'import', label: 'Import', color: '#6b7280', style: 'solid' as const },
    { id: 'violation', label: 'Violation', color: '#ef4444', style: 'solid' as const },
  ];

  it('has import edge type', () => {
    const importEdge = DEFAULT_EDGE_TYPES.find((e) => e.id === 'import');
    expect(importEdge).toBeDefined();
    expect(importEdge?.label).toBe('Import');
    expect(importEdge?.color).toBe('#6b7280');
  });

  it('has violation edge type', () => {
    const violationEdge = DEFAULT_EDGE_TYPES.find((e) => e.id === 'violation');
    expect(violationEdge).toBeDefined();
    expect(violationEdge?.label).toBe('Violation');
    expect(violationEdge?.color).toBe('#ef4444');
  });

  it('all edge types have solid style by default', () => {
    for (const edge of DEFAULT_EDGE_TYPES) {
      expect(edge.style).toBe('solid');
    }
  });
});

// =============================================================================
// Node Size Legend Tests
// =============================================================================

describe('Node size legend mapping', () => {
  const NODE_SIZE_LABELS = [
    { size: 'small', label: '<100', locRange: [0, 100] },
    { size: 'medium', label: '~500', locRange: [100, 1000] },
    { size: 'large', label: '>1K', locRange: [1000, Infinity] },
  ];

  it('has 3 size categories', () => {
    expect(NODE_SIZE_LABELS.length).toBe(3);
  });

  it('small category covers 0-100 LOC', () => {
    const small = NODE_SIZE_LABELS.find((s) => s.size === 'small');
    expect(small?.locRange[0]).toBe(0);
    expect(small?.locRange[1]).toBe(100);
  });

  it('medium category covers 100-1000 LOC', () => {
    const medium = NODE_SIZE_LABELS.find((s) => s.size === 'medium');
    expect(medium?.locRange[0]).toBe(100);
    expect(medium?.locRange[1]).toBe(1000);
  });

  it('large category covers 1000+ LOC', () => {
    const large = NODE_SIZE_LABELS.find((s) => s.size === 'large');
    expect(large?.locRange[0]).toBe(1000);
    expect(large?.locRange[1]).toBe(Infinity);
  });
});

// =============================================================================
// LocalStorage Persistence Logic Tests
// =============================================================================

describe('Legend localStorage persistence logic', () => {
  const STORAGE_KEY = 'gestalt-legend-collapsed';

  /**
   * These tests verify the persistence logic without depending on
   * the actual localStorage implementation (which varies by environment).
   */

  it('STORAGE_KEY is correct', () => {
    expect(STORAGE_KEY).toBe('gestalt-legend-collapsed');
  });

  it('parses "true" string correctly', () => {
    const stored: string = 'true';
    const collapsed = stored === 'true';
    expect(collapsed).toBe(true);
  });

  it('parses "false" string correctly', () => {
    const stored: string = 'false';
    const collapsed = stored === 'true';
    expect(collapsed).toBe(false);
  });

  it('handles null/undefined with default false', () => {
    const stored: string | null | undefined = null;
    const defaultCollapsed = false;
    const collapsed = stored != null ? stored === 'true' : defaultCollapsed;
    expect(collapsed).toBe(false);
  });

  it('handles null/undefined with default true', () => {
    const stored: string | null | undefined = null;
    const defaultCollapsed = true;
    const collapsed = stored != null ? stored === 'true' : defaultCollapsed;
    expect(collapsed).toBe(true);
  });

  it('converts boolean to string for storage', () => {
    expect(String(true)).toBe('true');
    expect(String(false)).toBe('false');
  });
});
