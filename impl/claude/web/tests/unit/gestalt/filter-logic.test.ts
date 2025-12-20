/**
 * Gestalt Filter Logic Tests
 *
 * Tests for the filter functions in the Gestalt visual showcase.
 *
 * @see plans/gestalt-visual-showcase.md Chunk 1
 */

import { describe, it, expect } from 'vitest';
import type { CodebaseModule } from '../../../src/api/types';
import {
  searchModules,
  calculateGradeDistribution,
  applyFilters,
  HEALTH_GRADES,
  type FilterState,
  DEFAULT_FILTER_STATE,
} from '../../../src/components/gestalt/types';

// =============================================================================
// Test Data
// =============================================================================

const createModule = (overrides: Partial<CodebaseModule> = {}): CodebaseModule => ({
  id: 'test.module',
  label: 'TestModule',
  layer: 'test',
  health_grade: 'A',
  health_score: 0.9,
  lines_of_code: 100,
  coupling: 0.3,
  cohesion: 0.8,
  instability: 0.2,
  x: 0,
  y: 0,
  z: 0,
  ...overrides,
});

const SAMPLE_MODULES: CodebaseModule[] = [
  createModule({ id: 'protocols.api.brain', label: 'brain', layer: 'protocols', health_grade: 'A+' }),
  createModule({ id: 'protocols.api.models', label: 'models', layer: 'protocols', health_grade: 'A' }),
  createModule({ id: 'protocols.gestalt.analysis', label: 'analysis', layer: 'protocols', health_grade: 'B+' }),
  createModule({ id: 'agents.town.citizens', label: 'citizens', layer: 'agents', health_grade: 'B' }),
  createModule({ id: 'agents.town.coalitions', label: 'coalitions', layer: 'agents', health_grade: 'C' }),
  createModule({ id: 'web.pages.Gestalt', label: 'Gestalt', layer: 'web', health_grade: 'A' }),
  createModule({ id: 'legacy.old_module', label: 'old_module', layer: 'legacy', health_grade: 'D' }),
  createModule({ id: 'deprecated.removed', label: 'removed', layer: 'deprecated', health_grade: 'F' }),
];

// =============================================================================
// searchModules Tests
// =============================================================================

describe('searchModules', () => {
  it('returns empty array for empty query', () => {
    expect(searchModules(SAMPLE_MODULES, '')).toEqual([]);
    expect(searchModules(SAMPLE_MODULES, '   ')).toEqual([]);
  });

  it('finds exact match on label', () => {
    const results = searchModules(SAMPLE_MODULES, 'brain');
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].module.label).toBe('brain');
    expect(results[0].matchType).toBe('exact');
  });

  it('finds prefix match on label', () => {
    const results = searchModules(SAMPLE_MODULES, 'ana');
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].module.label).toBe('analysis');
    expect(results[0].matchType).toBe('prefix');
  });

  it('finds contains match in label', () => {
    const results = searchModules(SAMPLE_MODULES, 'odel');
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].module.label).toBe('models');
    expect(results[0].matchType).toBe('contains');
  });

  it('finds match in module id', () => {
    const results = searchModules(SAMPLE_MODULES, 'protocols');
    expect(results.length).toBe(3); // brain, models, analysis
  });

  it('handles multi-token queries', () => {
    const results = searchModules(SAMPLE_MODULES, 'api brain');
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].module.id).toBe('protocols.api.brain');
  });

  it('sorts results by score descending', () => {
    const results = searchModules(SAMPLE_MODULES, 'a');
    // Should have multiple matches
    expect(results.length).toBeGreaterThan(1);
    // Scores should be descending
    for (let i = 1; i < results.length; i++) {
      expect(results[i - 1].score).toBeGreaterThanOrEqual(results[i].score);
    }
  });

  it('returns no results for non-matching query', () => {
    const results = searchModules(SAMPLE_MODULES, 'xyz123notfound');
    expect(results.length).toBe(0);
  });
});

// =============================================================================
// calculateGradeDistribution Tests
// =============================================================================

describe('calculateGradeDistribution', () => {
  it('counts modules by grade', () => {
    const distribution = calculateGradeDistribution(SAMPLE_MODULES);
    expect(distribution['A+']).toBe(1);
    expect(distribution.A).toBe(2);
    expect(distribution['B+']).toBe(1);
    expect(distribution.B).toBe(1);
    expect(distribution.C).toBe(1);
    expect(distribution.D).toBe(1);
    expect(distribution.F).toBe(1);
  });

  it('returns zeros for empty array', () => {
    const distribution = calculateGradeDistribution([]);
    HEALTH_GRADES.forEach((grade) => {
      expect(distribution[grade]).toBe(0);
    });
  });

  it('handles modules with unknown grades gracefully', () => {
    const modulesWithUnknown = [
      createModule({ health_grade: '?' }),
      createModule({ health_grade: 'A' }),
    ];
    const distribution = calculateGradeDistribution(modulesWithUnknown);
    expect(distribution.A).toBe(1);
    // Unknown grade not counted in standard distribution
  });
});

// =============================================================================
// applyFilters Tests
// =============================================================================

describe('applyFilters', () => {
  it('returns all modules with default filters', () => {
    const result = applyFilters(SAMPLE_MODULES, DEFAULT_FILTER_STATE);
    expect(result.length).toBe(SAMPLE_MODULES.length);
  });

  it('filters by layer', () => {
    const filters: FilterState = {
      ...DEFAULT_FILTER_STATE,
      layerFilter: 'protocols',
    };
    const result = applyFilters(SAMPLE_MODULES, filters);
    expect(result.length).toBe(3);
    expect(result.every((m) => m.layer === 'protocols')).toBe(true);
  });

  it('filters by enabled grades', () => {
    const filters: FilterState = {
      ...DEFAULT_FILTER_STATE,
      enabledGrades: new Set(['A+', 'A']),
    };
    const result = applyFilters(SAMPLE_MODULES, filters);
    expect(result.length).toBe(3); // 1 A+ and 2 A
    expect(result.every((m) => ['A+', 'A'].includes(m.health_grade))).toBe(true);
  });

  it('filters by search query', () => {
    const filters: FilterState = {
      ...DEFAULT_FILTER_STATE,
      searchQuery: 'brain',
    };
    const result = applyFilters(SAMPLE_MODULES, filters);
    expect(result.length).toBe(1);
    expect(result[0].id).toBe('protocols.api.brain');
  });

  it('combines multiple filters', () => {
    const filters: FilterState = {
      ...DEFAULT_FILTER_STATE,
      layerFilter: 'protocols',
      enabledGrades: new Set(['A+', 'A']),
    };
    const result = applyFilters(SAMPLE_MODULES, filters);
    expect(result.length).toBe(2); // brain (A+) and models (A) in protocols
  });

  it('returns empty array when no modules match', () => {
    const filters: FilterState = {
      ...DEFAULT_FILTER_STATE,
      enabledGrades: new Set(['C+', 'C', 'D', 'F']),
      layerFilter: 'protocols',
    };
    const result = applyFilters(SAMPLE_MODULES, filters);
    expect(result.length).toBe(0);
  });
});

// =============================================================================
// HEALTH_GRADES Tests
// =============================================================================

describe('HEALTH_GRADES', () => {
  it('contains all grades in order from best to worst', () => {
    expect(HEALTH_GRADES).toEqual(['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F']);
  });

  it('has 8 grades total', () => {
    expect(HEALTH_GRADES.length).toBe(8);
  });
});

// =============================================================================
// DEFAULT_FILTER_STATE Tests
// =============================================================================

describe('DEFAULT_FILTER_STATE', () => {
  it('has all grades enabled by default', () => {
    expect(DEFAULT_FILTER_STATE.enabledGrades.size).toBe(HEALTH_GRADES.length);
    HEALTH_GRADES.forEach((grade) => {
      expect(DEFAULT_FILTER_STATE.enabledGrades.has(grade)).toBe(true);
    });
  });

  it('has no layer filter by default', () => {
    expect(DEFAULT_FILTER_STATE.layerFilter).toBeNull();
  });

  it('has no search query by default', () => {
    expect(DEFAULT_FILTER_STATE.searchQuery).toBe('');
  });

  it('has all display options enabled by default', () => {
    expect(DEFAULT_FILTER_STATE.showEdges).toBe(true);
    expect(DEFAULT_FILTER_STATE.showViolations).toBe(true);
    expect(DEFAULT_FILTER_STATE.showLabels).toBe(true);
    expect(DEFAULT_FILTER_STATE.showAnimation).toBe(true);
  });

  it('has reasonable max nodes default', () => {
    expect(DEFAULT_FILTER_STATE.maxNodes).toBeGreaterThanOrEqual(50);
    expect(DEFAULT_FILTER_STATE.maxNodes).toBeLessThanOrEqual(500);
  });
});
