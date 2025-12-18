/**
 * Tests for buildGestaltTree and health aggregation logic.
 *
 * @see ../buildGestaltTree.ts
 */

import { describe, it, expect } from 'vitest';
import {
  buildLayerTree,
  buildPathTree,
  getViolationMap,
  gradeToNumber,
  getWorstGrade,
} from '@/components/gestalt/GestaltTree';
import type { CodebaseModule, DependencyLink } from '@/api/types';

// =============================================================================
// Test Fixtures
// =============================================================================

const createModule = (
  id: string,
  layer: string,
  grade: string,
  score: number,
  loc: number
): CodebaseModule => ({
  id,
  label: id.split('.').pop() || id,
  layer,
  health_grade: grade,
  health_score: score,
  lines_of_code: loc,
  coupling: 0.3,
  cohesion: 0.7,
  instability: null,
  x: 0,
  y: 0,
  z: 0,
});

const createLink = (
  source: string,
  target: string,
  isViolation: boolean = false
): DependencyLink => ({
  source,
  target,
  import_type: 'import',
  is_violation: isViolation,
  violation_severity: isViolation ? 'medium' : null,
});

// =============================================================================
// Grade Utilities
// =============================================================================

describe('gradeToNumber', () => {
  it('converts A+ to 0 (best)', () => {
    expect(gradeToNumber('A+')).toBe(0);
  });

  it('converts F to 7 (worst)', () => {
    expect(gradeToNumber('F')).toBe(7);
  });

  it('handles unknown grades', () => {
    expect(gradeToNumber('X')).toBe(8); // Falls back to last position
  });
});

describe('getWorstGrade', () => {
  it('returns worst grade from list', () => {
    expect(getWorstGrade(['A+', 'B', 'C'])).toBe('C');
    expect(getWorstGrade(['A+', 'A', 'B+'])).toBe('B+');
    expect(getWorstGrade(['F', 'A+'])).toBe('F');
  });

  it('returns ? for empty list', () => {
    expect(getWorstGrade([])).toBe('?');
  });
});

// =============================================================================
// Violation Mapping
// =============================================================================

describe('getViolationMap', () => {
  it('counts violations per source module', () => {
    const links = [
      createLink('a', 'b', true),
      createLink('a', 'c', true),
      createLink('b', 'c', false),
      createLink('c', 'd', true),
    ];

    const map = getViolationMap(links);

    expect(map.get('a')).toBe(2);
    expect(map.get('c')).toBe(1);
    expect(map.get('b')).toBeUndefined(); // No violations
  });

  it('returns empty map for no violations', () => {
    const links = [createLink('a', 'b', false)];
    const map = getViolationMap(links);
    expect(map.size).toBe(0);
  });
});

// =============================================================================
// Layer Tree Building
// =============================================================================

describe('buildLayerTree', () => {
  it('groups modules by layer', () => {
    const modules = [
      createModule('impl.protocols.api', 'protocols', 'A+', 0.95, 100),
      createModule('impl.protocols.gateway', 'protocols', 'A', 0.9, 200),
      createModule('impl.services.brain', 'services', 'B+', 0.8, 150),
    ];

    const tree = buildLayerTree(modules, []);

    expect(tree.size).toBe(2); // protocols, services
    expect(tree.has('protocols')).toBe(true);
    expect(tree.has('services')).toBe(true);

    const protocols = tree.get('protocols')!;
    expect(protocols.moduleCount).toBe(2);
    expect(protocols.linesOfCode).toBe(300);
  });

  it('aggregates health grade (worst bubbles up)', () => {
    const modules = [
      createModule('impl.protocols.api', 'protocols', 'A+', 0.95, 100),
      createModule('impl.protocols.gateway', 'protocols', 'C', 0.6, 200),
    ];

    const tree = buildLayerTree(modules, []);
    const protocols = tree.get('protocols')!;

    expect(protocols.healthGrade).toBe('C'); // Worst grade
  });

  it('propagates violations up', () => {
    const modules = [
      createModule('impl.protocols.api', 'protocols', 'A+', 0.95, 100),
      createModule('impl.protocols.gateway', 'protocols', 'A', 0.9, 200),
    ];
    const links = [createLink('impl.protocols.api', 'impl.services.brain', true)];

    const tree = buildLayerTree(modules, links);
    const protocols = tree.get('protocols')!;

    expect(protocols.hasViolation).toBe(true);
    expect(protocols.violationCount).toBe(1);
  });

  it('calculates weighted average score by LoC', () => {
    const modules = [
      createModule('impl.protocols.api', 'protocols', 'A', 1.0, 100), // 100 LoC * 1.0 = 100
      createModule('impl.protocols.gateway', 'protocols', 'B', 0.5, 300), // 300 LoC * 0.5 = 150
    ];
    // Total = 250 / 400 = 0.625

    const tree = buildLayerTree(modules, []);
    const protocols = tree.get('protocols')!;

    expect(protocols.healthScore).toBeCloseTo(0.625, 2);
  });
});

// =============================================================================
// Path Tree Building
// =============================================================================

describe('buildPathTree', () => {
  it('creates full hierarchical structure', () => {
    const modules = [
      createModule('impl.claude.protocols.api', 'protocols', 'A+', 0.95, 100),
      createModule('impl.claude.protocols.gateway', 'protocols', 'A', 0.9, 200),
    ];

    const tree = buildPathTree(modules, []);

    expect(tree.has('impl')).toBe(true);

    const impl = tree.get('impl')!;
    expect(impl.children.has('claude')).toBe(true);

    const claude = impl.children.get('claude')!;
    expect(claude.children.has('protocols')).toBe(true);

    const protocols = claude.children.get('protocols')!;
    expect(protocols.children.size).toBe(2); // api, gateway
  });

  it('marks leaf nodes correctly', () => {
    const modules = [
      createModule('impl.claude.protocols.api', 'protocols', 'A+', 0.95, 100),
    ];

    const tree = buildPathTree(modules, []);

    const impl = tree.get('impl')!;
    expect(impl.isLeaf).toBe(false);

    const api = impl.children.get('claude')!.children.get('protocols')!.children.get('api')!;
    expect(api.isLeaf).toBe(true);
    expect(api.module).toBeDefined();
  });

  it('aggregates health through full hierarchy', () => {
    const modules = [
      createModule('impl.claude.protocols.api', 'protocols', 'A+', 0.95, 100),
      createModule('impl.claude.protocols.gateway', 'protocols', 'D', 0.3, 200),
    ];

    const tree = buildPathTree(modules, []);

    // Root should have worst grade
    const impl = tree.get('impl')!;
    expect(impl.healthGrade).toBe('D');
    expect(impl.moduleCount).toBe(2);
  });
});

// =============================================================================
// Edge Cases
// =============================================================================

describe('edge cases', () => {
  it('handles empty module list', () => {
    const tree = buildLayerTree([], []);
    expect(tree.size).toBe(0);
  });

  it('handles modules with null layer', () => {
    const modules = [
      createModule('impl.unknown', null as unknown as string, 'B', 0.7, 100),
    ];

    const tree = buildLayerTree(modules, []);
    expect(tree.has('unknown')).toBe(true); // Falls back to 'unknown'
  });

  it('handles single-segment module IDs', () => {
    const modules = [createModule('standalone', 'core', 'A', 0.9, 50)];

    const tree = buildLayerTree(modules, []);
    expect(tree.has('core')).toBe(true);

    const core = tree.get('core')!;
    expect(core.children.has('standalone')).toBe(true);
  });
});
