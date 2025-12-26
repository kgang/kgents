/**
 * Contradiction primitive types
 *
 * Shared type definitions for contradiction primitives.
 */

// =============================================================================
// Resolution Strategies
// =============================================================================

/**
 * Five strategies for resolving contradictions
 *
 * - synthesis: Hegelian synthesis (third thing better than either)
 * - scope: Limit scope of one or both claims
 * - temporal: True at different times
 * - context: True in different contexts
 * - supersede: One claim supersedes the other
 */
export type ResolutionStrategy =
  | 'synthesis'
  | 'scope'
  | 'temporal'
  | 'context'
  | 'supersede';

// =============================================================================
// Contradiction Types
// =============================================================================

/**
 * Type of contradiction
 *
 * - genuine: True logical contradiction (needs resolution)
 * - productive: Productive tension (valuable, but needs synthesis)
 * - apparent: Appears contradictory but isn't (clarification needed)
 */
export type ContradictionType = 'genuine' | 'productive' | 'apparent';

// =============================================================================
// Severity Levels
// =============================================================================

/**
 * Severity of contradiction
 *
 * - low: Minor, apparent contradiction
 * - medium: Productive tension worth exploring
 * - high: Genuine contradiction requiring resolution
 */
export type ContradictionSeverity = 'low' | 'medium' | 'high';

// =============================================================================
// Contradiction Data
// =============================================================================

/**
 * Core contradiction data structure
 */
export interface Contradiction {
  /** Unique identifier */
  id: string;
  /** Thesis statement */
  thesis: {
    content: string;
    source?: string;
    location?: string;
  };
  /** Antithesis statement */
  antithesis: {
    content: string;
    source?: string;
    location?: string;
  };
  /** Type of contradiction */
  type: ContradictionType;
  /** Severity level */
  severity: ContradictionSeverity;
  /** Whether contradiction has been resolved */
  resolved: boolean;
  /** Resolution strategy used (if resolved) */
  resolution?: {
    strategy: ResolutionStrategy;
    synthesis?: string;
    note?: string;
  };
  /** Timestamp of detection */
  detectedAt: string;
  /** Timestamp of resolution (if resolved) */
  resolvedAt?: string;
}
