/**
 * Gestalt Filter Types
 *
 * Shared types for the Gestalt visual showcase filter system.
 *
 * @see plans/gestalt-visual-showcase.md
 */

import type { CodebaseModule } from '../../api/types';

// =============================================================================
// Density (shared with main Gestalt page and primitives)
// =============================================================================

// Re-export Density from primitives for backward compatibility
export type { Density } from '../three/primitives/themes/types';

// =============================================================================
// Filter State
// =============================================================================

/**
 * Complete filter state for the Gestalt visualization.
 * Used by FilterPanel and consumed by Scene.
 */
export interface FilterState {
  // Layer filtering (existing)
  layerFilter: string | null;

  // Health grade filtering (Chunk 1)
  enabledGrades: Set<string>;

  // Search (Chunk 1)
  searchQuery: string;
  focusedModuleId: string | null;

  // View presets (Chunk 1)
  activePreset: string | null;

  // Display toggles (existing)
  showEdges: boolean;
  showViolations: boolean;
  showLabels: boolean;

  // Animation toggle (Chunk 3)
  showAnimation: boolean;

  // Node limit (existing)
  maxNodes: number;

  // Sprint 3: Organic/Forest theme toggle
  organicTheme: boolean;
}

/**
 * Default filter state - all grades enabled, no filters active.
 */
export const DEFAULT_FILTER_STATE: FilterState = {
  layerFilter: null,
  enabledGrades: new Set(['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F']),
  searchQuery: '',
  focusedModuleId: null,
  activePreset: null,
  showEdges: true,
  showViolations: true,
  showLabels: true,
  showAnimation: true, // Chunk 3: Flow animation enabled by default
  maxNodes: 150,
  organicTheme: true, // Sprint 3: Forest theme enabled by default
};

// =============================================================================
// View Presets
// =============================================================================

/**
 * A view preset applies a combination of filters with one click.
 */
export interface ViewPreset {
  id: string;
  name: string;
  icon: string;
  description: string;
  filters: Partial<FilterState>;
}

/**
 * Built-in view presets for common exploration patterns.
 */
export const VIEW_PRESETS: ViewPreset[] = [
  {
    id: 'all',
    name: 'All',
    icon: '🌐',
    description: 'Show all modules',
    filters: {
      enabledGrades: new Set(['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F']),
      layerFilter: null,
      activePreset: 'all',
    },
  },
  {
    id: 'healthy',
    name: 'Healthy',
    icon: '💚',
    description: 'Show A and B grades only',
    filters: {
      enabledGrades: new Set(['A+', 'A', 'B+', 'B']),
      activePreset: 'healthy',
    },
  },
  {
    id: 'at-risk',
    name: 'At Risk',
    icon: '⚠️',
    description: 'Show C, D, and F grades',
    filters: {
      enabledGrades: new Set(['C+', 'C', 'D', 'F']),
      activePreset: 'at-risk',
    },
  },
  {
    id: 'violations',
    name: 'Violations',
    icon: '🔴',
    description: 'Focus on violation edges',
    filters: {
      showViolations: true,
      showEdges: true,
      activePreset: 'violations',
    },
  },
  {
    id: 'core',
    name: 'Core',
    icon: '⭐',
    description: 'Show protocols and agents',
    filters: {
      layerFilter: null, // We'll handle this specially with multi-layer
      activePreset: 'core',
    },
  },
];

// =============================================================================
// Health Grades
// =============================================================================

/**
 * All possible health grades in order from best to worst.
 */
export const HEALTH_GRADES = ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F'] as const;

export type HealthGrade = (typeof HEALTH_GRADES)[number];

/**
 * Grade distribution - count of modules per grade.
 */
export type GradeDistribution = Record<HealthGrade, number>;

/**
 * Calculate grade distribution from modules.
 */
export function calculateGradeDistribution(modules: CodebaseModule[]): GradeDistribution {
  const distribution: GradeDistribution = {
    'A+': 0,
    A: 0,
    'B+': 0,
    B: 0,
    'C+': 0,
    C: 0,
    D: 0,
    F: 0,
  };

  for (const module of modules) {
    const grade = module.health_grade as HealthGrade;
    if (grade in distribution) {
      distribution[grade]++;
    }
  }

  return distribution;
}

// =============================================================================
// Search
// =============================================================================

/**
 * Search result with match score.
 */
export interface SearchResult {
  module: CodebaseModule;
  score: number;
  matchType: 'exact' | 'prefix' | 'contains' | 'fuzzy';
}

/**
 * Simple fuzzy search implementation (no external dependency).
 * Matches query tokens against module id and label.
 *
 * Scoring:
 * - Exact match on label: 100
 * - Prefix match on label: 80
 * - Contains in label: 60
 * - Exact in id: 50
 * - Contains in id: 40
 * - Fuzzy match: 20
 */
export function searchModules(modules: CodebaseModule[], query: string): SearchResult[] {
  if (!query.trim()) return [];

  const normalizedQuery = query.toLowerCase().trim();
  const queryTokens = normalizedQuery.split(/\s+/);

  const results: SearchResult[] = [];

  for (const module of modules) {
    const label = module.label.toLowerCase();
    const id = module.id.toLowerCase();

    let score = 0;
    let matchType: SearchResult['matchType'] = 'fuzzy';

    // Check each token
    for (const token of queryTokens) {
      // Exact match on label
      if (label === token) {
        score += 100;
        matchType = 'exact';
      }
      // Prefix match on label
      else if (label.startsWith(token)) {
        score += 80;
        if (matchType !== 'exact') matchType = 'prefix';
      }
      // Contains in label
      else if (label.includes(token)) {
        score += 60;
        if (matchType !== 'exact' && matchType !== 'prefix') matchType = 'contains';
      }
      // Exact match in id segment
      else if (id.split('.').some((seg) => seg === token)) {
        score += 50;
        if (matchType === 'fuzzy') matchType = 'contains';
      }
      // Contains in id
      else if (id.includes(token)) {
        score += 40;
        if (matchType === 'fuzzy') matchType = 'contains';
      }
      // Fuzzy: check if letters appear in order
      else {
        let tokenIdx = 0;
        for (const char of id + label) {
          if (char === token[tokenIdx]) {
            tokenIdx++;
            if (tokenIdx === token.length) {
              score += 20;
              break;
            }
          }
        }
      }
    }

    if (score > 0) {
      results.push({ module, score, matchType });
    }
  }

  // Sort by score descending
  return results.sort((a, b) => b.score - a.score);
}

// =============================================================================
// Filter Application
// =============================================================================

/**
 * Apply all filters to a list of modules.
 * Returns filtered modules ready for rendering.
 */
export function applyFilters(modules: CodebaseModule[], filters: FilterState): CodebaseModule[] {
  let filtered = modules;

  // Apply layer filter
  if (filters.layerFilter) {
    filtered = filtered.filter((m) => m.layer === filters.layerFilter);
  }

  // Apply health grade filter
  if (filters.enabledGrades.size < HEALTH_GRADES.length) {
    filtered = filtered.filter((m) => filters.enabledGrades.has(m.health_grade));
  }

  // Apply search filter (show only matching modules)
  if (filters.searchQuery.trim()) {
    const searchResults = searchModules(filtered, filters.searchQuery);
    const matchingIds = new Set(searchResults.map((r) => r.module.id));
    filtered = filtered.filter((m) => matchingIds.has(m.id));
  }

  return filtered;
}

/**
 * Get the "core" layers for the Core preset.
 * These are the most important architectural layers.
 */
export const CORE_LAYERS = ['protocols', 'agents'] as const;

/**
 * Check if a module is in a core layer.
 */
export function isCoreLayer(module: CodebaseModule): boolean {
  if (!module.layer) return false;
  return CORE_LAYERS.some((core) => module.layer?.startsWith(core));
}

// =============================================================================
// Tooltip State (Chunk 2)
// =============================================================================

/**
 * State for node hover tooltip.
 */
export interface HoverState {
  /** ID of hovered module (null if none) */
  moduleId: string | null;
  /** Timestamp when hover started (for delay) */
  hoverStartTime: number | null;
  /** Whether tooltip should be visible (after delay) */
  tooltipVisible: boolean;
}

/**
 * Default hover state.
 */
export const DEFAULT_HOVER_STATE: HoverState = {
  moduleId: null,
  hoverStartTime: null,
  tooltipVisible: false,
};

/**
 * Tooltip display delay in milliseconds.
 */
export const TOOLTIP_DELAY_MS = 300;

// =============================================================================
// Legend Configuration (Chunk 2)
// =============================================================================

/**
 * Position options for the legend overlay.
 */
export type LegendPosition = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';

/**
 * Legend state (persisted to localStorage).
 */
export interface LegendState {
  collapsed: boolean;
  position: LegendPosition;
}
