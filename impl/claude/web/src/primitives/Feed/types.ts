/**
 * Feed Primitive — Type Definitions
 *
 * "The feed is not a view of data. The feed IS the primary interface."
 *
 * From Zero Seed Genesis Grand Strategy:
 * - Chronological truth streams
 * - Filterable by lens (layer, loss, author, principle)
 * - Algorithmic (attention + principles alignment)
 * - Recursive (users create feedback systems with feeds)
 */

// =============================================================================
// K-Block (Feed Item)
// =============================================================================

/**
 * K-Block: The universal unit of knowledge in kgents.
 * Files, decisions, goals, axioms — all are K-Blocks.
 */
export interface KBlock {
  /** Unique identifier */
  id: string;

  /** Human-readable title */
  title: string;

  /** Content body (Markdown) */
  content: string;

  /** Galois layer (1-7: Axiom → Implementation) */
  layer: number;

  /** Loss indicator (0.0 = perfect coherence, 1.0 = max drift) */
  loss: number;

  /** Author/creator */
  author: string;

  /** Timestamp of creation */
  createdAt: Date;

  /** Timestamp of last update */
  updatedAt: Date;

  /** Tags/labels */
  tags: string[];

  /** Principle alignments (from CONSTITUTION.md) */
  principles: string[];

  /** Edge count (relationships to other K-Blocks) */
  edgeCount: number;

  /** Preview text (first 200 chars) */
  preview?: string;
}

// =============================================================================
// Feed Configuration
// =============================================================================

/**
 * Feed source types.
 * Feeds can pull from different sources and combine them.
 */
export type FeedSourceType =
  | 'all'              // All K-Blocks
  | 'layer'            // Specific Galois layer
  | 'tag'              // Tagged items
  | 'principle'        // Aligned to principle
  | 'author'           // By author
  | 'recent'           // Recently modified
  | 'starred'          // User-starred items
  | 'contradictions';  // Detected contradictions

/**
 * A source for a feed.
 */
export interface FeedSource {
  type: FeedSourceType;
  value?: string | number;  // layer number, tag name, author, etc.
}

/**
 * Filter criteria for feeds.
 */
export interface FeedFilter {
  /** Filter type */
  type: 'layer' | 'loss-range' | 'author' | 'time-range' | 'tag' | 'principle';

  /** Filter value (varies by type) */
  value: FeedFilterValue;

  /** Display label */
  label: string;

  /** Is this filter active? */
  active: boolean;
}

/**
 * Filter value (union type for different filter types).
 */
export type FeedFilterValue =
  | number                        // layer (1-7)
  | [number, number]              // loss-range [min, max]
  | string                        // author, tag, principle
  | [Date, Date];                 // time-range [start, end]

/**
 * Feed ranking/sorting modes.
 */
export type FeedRanking =
  | 'chronological'       // Newest first
  | 'loss-ascending'      // Lowest loss first (most coherent)
  | 'loss-descending'     // Highest loss first (needs attention)
  | 'engagement'          // Most viewed/engaged
  | 'algorithmic';        // Principles-aligned + attention

/**
 * Complete feed configuration.
 */
export interface Feed {
  /** Feed identifier */
  id: string;

  /** Feed name */
  name: string;

  /** Feed sources */
  sources: FeedSource[];

  /** Active filters */
  filters: FeedFilter[];

  /** Ranking/sorting mode */
  ranking: FeedRanking;
}

// =============================================================================
// Feed Component Props
// =============================================================================

/**
 * Props for Feed component.
 */
export interface FeedProps {
  /** Feed ID (or 'default' for global feed) */
  feedId: string;

  /** Callback when item is clicked */
  onItemClick: (kblock: KBlock) => void;

  /** Callback when contradiction is detected between two items */
  onContradiction?: (a: KBlock, b: KBlock) => void;

  /** Initial filters (optional) */
  initialFilters?: FeedFilter[];

  /** Initial ranking (optional, defaults to 'chronological') */
  initialRanking?: FeedRanking;

  /** Enable infinite scroll (default: true) */
  infiniteScroll?: boolean;

  /** Enable virtualization for large lists (default: true) */
  virtualized?: boolean;

  /** Height of feed container (for virtualization) */
  height?: number;

  /** Custom CSS class */
  className?: string;
}

/**
 * Props for FeedItem component.
 */
export interface FeedItemProps {
  /** K-Block to display */
  kblock: KBlock;

  /** Is this item expanded/focused? */
  isExpanded: boolean;

  /** Click handler */
  onClick: () => void;

  /** Feedback handlers */
  onView?: () => void;
  onEngage?: () => void;
  onDismiss?: () => void;

  /** Contradiction handler - called when user clicks on a contradiction badge */
  onContradictionClick?: (contradictingKBlock: KBlock) => void;

  /** Custom CSS class */
  className?: string;
}

/**
 * Props for FeedFilters component.
 */
export interface FeedFiltersProps {
  /** Current active filters */
  filters: FeedFilter[];

  /** Callback when filters change */
  onFiltersChange: (filters: FeedFilter[]) => void;

  /** Current ranking mode */
  ranking: FeedRanking;

  /** Callback when ranking changes */
  onRankingChange: (ranking: FeedRanking) => void;

  /** Custom CSS class */
  className?: string;
}

// =============================================================================
// Feedback System
// =============================================================================

/**
 * Feedback action types.
 * These actions are tracked to improve feed ranking.
 */
export type FeedbackAction = 'view' | 'engage' | 'dismiss' | 'contradict';

/**
 * Feedback event for analytics.
 */
export interface FeedbackEvent {
  /** K-Block ID */
  kblockId: string;

  /** Action type */
  action: FeedbackAction;

  /** Timestamp */
  timestamp: Date;

  /** Optional metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Return type for useFeedFeedback hook.
 */
export interface UseFeedFeedback {
  /** Track view event */
  onView: (kblock: KBlock) => void;

  /** Track engagement (click, expand, edit) */
  onEngage: (kblock: KBlock) => void;

  /** Track dismissal (hide, archive) */
  onDismiss: (kblock: KBlock) => void;

  /** Track contradiction (conflict with another K-Block) */
  onContradict: (kblockA: KBlock, kblockB: KBlock) => void;

  /** Get feedback history for a K-Block */
  getFeedback: (kblockId: string) => FeedbackEvent[];

  /** Clear all feedback */
  clearFeedback: () => void;
}

// =============================================================================
// Layer Metadata
// =============================================================================

/**
 * Galois layer names (1-7).
 */
export const LAYER_NAMES: Record<number, string> = {
  1: 'Axiom',
  2: 'Value',
  3: 'Capability',
  4: 'Domain',
  5: 'Service',
  6: 'Construction',
  7: 'Implementation',
};

/**
 * Galois layer colors (for visual consistency).
 */
export const LAYER_COLORS: Record<number, string> = {
  1: '#440154',  // Deep purple - Axiom
  2: '#31688e',  // Blue - Value
  3: '#35b779',  // Green - Capability
  4: '#fde724',  // Yellow - Domain
  5: '#f59e0b',  // Amber - Service
  6: '#ef4444',  // Red - Construction
  7: '#8b5cf6',  // Violet - Implementation
};

// =============================================================================
// Loss Thresholds
// =============================================================================

/**
 * Loss threshold for visual indicators.
 */
export const LOSS_THRESHOLDS = {
  HEALTHY: 0.2,      // < 0.2: Coherent, stable
  WARNING: 0.5,      // 0.2-0.5: Some drift, watch
  CRITICAL: 0.8,     // 0.5-0.8: Significant drift
  EMERGENCY: 1.0,    // > 0.8: Maximum drift, needs attention
};

/**
 * Loss color mapping.
 */
export const LOSS_COLORS = {
  HEALTHY: '#22c55e',    // Green
  WARNING: '#f59e0b',    // Amber
  CRITICAL: '#ef4444',   // Red
  EMERGENCY: '#dc2626',  // Dark red
};
