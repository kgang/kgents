/**
 * GestaltTree Types
 *
 * Type definitions for the hierarchical codebase navigator.
 * Extends NavigationTree's TreeNode pattern with health metrics.
 *
 * @see impl/claude/web/src/shell/NavigationTree.tsx - Pattern source
 * @see creative/crown-jewels-genesis-moodboard.md - Living Earth aesthetic
 */

import type { CodebaseModule, DependencyLink } from '@/api/types';

// =============================================================================
// Core Types
// =============================================================================

/**
 * GestaltNode - Hierarchical tree node with health metrics.
 *
 * Key insight: Health aggregates upward. A parent node's health is the worst
 * health of its children. Violations bubble up as hasViolation flags.
 */
export interface GestaltNode {
  // Tree structure (from NavigationTree pattern)
  /** Node path segment (e.g., "protocols", "gateway.py") */
  segment: string;
  /** Full dot-separated path (e.g., "protocols.agentese.gateway") */
  path: string;
  /** Child nodes - Map for O(1) lookup */
  children: Map<string, GestaltNode>;
  /** true = actual module file, false = virtual group/directory */
  isLeaf: boolean;

  // Health metrics (aggregated for non-leaves)
  /** Worst grade in subtree: A+ → F */
  healthGrade: string;
  /** Weighted average by LoC: 0.0 - 1.0 */
  healthScore: number;
  /** Count of leaf modules in subtree */
  moduleCount: number;

  // Violation tracking (bubbles up)
  /** true if ANY descendant has a violation */
  hasViolation: boolean;
  /** Sum of violations in subtree */
  violationCount: number;

  // Display metrics (aggregated for non-leaves)
  /** Sum of lines of code in subtree */
  linesOfCode: number;

  // Original module data (leaf nodes only)
  /** The CodebaseModule this node represents (only for leaves) */
  module?: CodebaseModule;
}

/**
 * Tree display mode - layer-grouped vs full-path hierarchy.
 */
export type TreeMode = 'layer' | 'path';

// =============================================================================
// Component Props
// =============================================================================

/**
 * Props for GestaltTree main container.
 */
export interface GestaltTreeProps {
  /** Flat list of modules from AGENTESE world.codebase.topology */
  modules: CodebaseModule[];
  /** Links for violation tracking */
  links: DependencyLink[];
  /** Currently selected module ID */
  selectedModule: string | null;
  /** Selection callback */
  onModuleSelect: (moduleId: string) => void;
  /** Compact mode for mobile */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

/**
 * Props for individual tree node.
 */
export interface GestaltTreeNodeProps {
  node: GestaltNode;
  level: number;
  expandedPaths: Set<string>;
  selectedModule: string | null;
  onToggle: (path: string) => void;
  onSelect: (moduleId: string) => void;
  compact?: boolean;
}

/**
 * Props for HealthBadge component.
 */
export interface HealthBadgeProps {
  /** Health grade: A+, A, B+, B, C+, C, D, F */
  grade: string;
  /** Health score 0-1 for progress bar */
  score: number;
  /** Whether this node or descendants have violations */
  hasViolation: boolean;
  /** Enable breathing animation for healthy nodes */
  breathing?: boolean;
  /** Compact mode - smaller display */
  compact?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

/**
 * Grade ordering from best to worst.
 * Used for aggregation (worst grade bubbles up).
 */
export const GRADE_ORDER = ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F', '?'] as const;

/**
 * Convert grade to numeric value for comparison.
 * Higher = worse (F=8, A+=0)
 */
export function gradeToNumber(grade: string): number {
  const index = GRADE_ORDER.indexOf(grade as (typeof GRADE_ORDER)[number]);
  return index === -1 ? GRADE_ORDER.length - 1 : index;
}

/**
 * Convert numeric value back to grade.
 */
export function numberToGrade(num: number): string {
  return GRADE_ORDER[Math.min(num, GRADE_ORDER.length - 1)] || '?';
}

/**
 * Get the worst grade from a list.
 */
export function getWorstGrade(grades: string[]): string {
  if (grades.length === 0) return '?';
  const indices = grades.map(gradeToNumber);
  const worst = Math.max(...indices);
  return numberToGrade(worst);
}
