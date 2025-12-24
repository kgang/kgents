/**
 * Brain Explorer Types — Unified Data Explorer
 *
 * "The file is a lie. There is only the graph."
 *
 * Type definitions for the Brain page's unified stream interface,
 * which displays all kgents data constructs in a single chronological feed.
 */

// =============================================================================
// Entity Types
// =============================================================================

/**
 * The six data construct types in kgents.
 *
 * Each type maps to a distinct database domain:
 * - mark: WitnessMark (witnessed behavior)
 * - crystal: Crystal (crystallized knowledge)
 * - trail: TrailRow (exploration journeys)
 * - evidence: TraceWitness, VerificationGraph, CategoricalViolation
 * - teaching: TeachingCrystal (ancestral wisdom)
 * - lemma: VerifiedLemmaModel (ASHC proofs)
 */
export type EntityType = 'mark' | 'crystal' | 'trail' | 'evidence' | 'teaching' | 'lemma';

/**
 * Visual badges for each entity type.
 */
export const ENTITY_BADGES: Record<EntityType, { emoji: string; label: string; color: string }> = {
  mark: { emoji: '🔖', label: 'Mark', color: 'var(--witness-mark)' },
  crystal: { emoji: '💎', label: 'Crystal', color: 'var(--brain-crystal)' },
  trail: { emoji: '🛤️', label: 'Trail', color: 'var(--trail-path)' },
  evidence: { emoji: '✓', label: 'Evidence', color: 'var(--evidence-pass)' },
  teaching: { emoji: '📜', label: 'Teaching', color: 'var(--teaching-wisdom)' },
  lemma: { emoji: '🧪', label: 'Lemma', color: 'var(--lemma-proof)' },
};

// =============================================================================
// Unified Event
// =============================================================================

/**
 * A unified event in the Brain stream.
 *
 * All entity types are normalized to this shape for display in the stream.
 * Type-specific fields are stored in `metadata`.
 */
export interface UnifiedEvent {
  /** Unique event identifier (e.g., "mark-abc123", "crystal-def456") */
  id: string;

  /** Entity type for polymorphic rendering */
  type: EntityType;

  /** Primary display text (action for marks, summary for crystals, etc.) */
  title: string;

  /** Secondary display text with additional context */
  summary: string;

  /** When this event occurred (ISO 8601) */
  timestamp: string;

  /** Type-specific fields for detail views */
  metadata: EventMetadata;
}

/**
 * Type-specific metadata union.
 *
 * Each entity type has its own metadata shape for detail rendering.
 */
export type EventMetadata =
  | MarkMetadata
  | CrystalMetadata
  | TrailMetadata
  | EvidenceMetadata
  | TeachingMetadata
  | LemmaMetadata;

// -----------------------------------------------------------------------------
// Mark Metadata
// -----------------------------------------------------------------------------

export interface MarkMetadata {
  type: 'mark';
  action: string;
  reasoning?: string;
  principles: string[];
  tags: string[];
  author: 'kent' | 'claude' | 'system';
  session_id?: string;
  parent_mark_id?: string;
}

// -----------------------------------------------------------------------------
// Crystal Metadata
// -----------------------------------------------------------------------------

export interface CrystalMetadata {
  type: 'crystal';
  content_hash: string;
  tags: string[];
  access_count: number;
  last_accessed?: string;
  source_type?: string;
  source_ref?: string;
  datum_id?: string;
}

// -----------------------------------------------------------------------------
// Trail Metadata
// -----------------------------------------------------------------------------

export interface TrailMetadata {
  type: 'trail';
  name: string;
  step_count: number;
  topics: string[];
  evidence_strength: 'weak' | 'moderate' | 'strong' | 'definitive';
  forked_from_id?: string;
  is_active: boolean;
}

// -----------------------------------------------------------------------------
// Evidence Metadata
// -----------------------------------------------------------------------------

export type EvidenceSubtype = 'trace_witness' | 'verification_graph' | 'categorical_violation';

export interface EvidenceMetadata {
  type: 'evidence';
  subtype: EvidenceSubtype;
  agent_path?: string;
  status: 'pending' | 'in_progress' | 'success' | 'failure' | 'needs_review';
  violation_type?: string;
  is_resolved?: boolean;
}

// -----------------------------------------------------------------------------
// Teaching Metadata
// -----------------------------------------------------------------------------

export interface TeachingMetadata {
  type: 'teaching';
  insight: string;
  severity: 'info' | 'warning' | 'critical';
  source_module: string;
  source_symbol: string;
  is_alive: boolean;
  died_at?: string;
  successor_module?: string;
  extinction_id?: string;
}

// -----------------------------------------------------------------------------
// Lemma Metadata
// -----------------------------------------------------------------------------

export interface LemmaMetadata {
  type: 'lemma';
  statement: string;
  checker: 'dafny' | 'lean4' | 'verus';
  usage_count: number;
  obligation_id: string;
  dependencies: string[];
}

// =============================================================================
// Filter State
// =============================================================================

/**
 * Filter state for the Brain stream.
 */
export interface StreamFilters {
  /** Entity types to include (empty = all) */
  types: EntityType[];

  /** Filter by author (for marks) */
  author?: 'kent' | 'claude' | 'system';

  /** Date range filter */
  dateRange?: {
    start: Date;
    end: Date;
  };

  /** Tag filter (any match) */
  tags?: string[];

  /** Full-text search query */
  searchQuery?: string;
}

/**
 * Default filters (show everything).
 */
export const DEFAULT_FILTERS: StreamFilters = {
  types: [],
};

// =============================================================================
// Page State
// =============================================================================

/**
 * Brain page state.
 */
export interface BrainPageState {
  /** Events in the stream */
  events: UnifiedEvent[];

  /** Currently selected event (for detail drawer) */
  selectedEvent: UnifiedEvent | null;

  /** Whether the detail drawer is open */
  drawerOpen: boolean;

  /** Current filter state */
  filters: StreamFilters;

  /** Loading state */
  loading: boolean;

  /** Whether more events are available */
  hasMore: boolean;

  /** SSE connection status */
  connected: boolean;
}

/**
 * Initial page state.
 */
export const INITIAL_STATE: BrainPageState = {
  events: [],
  selectedEvent: null,
  drawerOpen: false,
  filters: DEFAULT_FILTERS,
  loading: true,
  hasMore: true,
  connected: false,
};

// =============================================================================
// API Types
// =============================================================================

/**
 * Request for listing events.
 */
export interface ListEventsRequest {
  filters?: StreamFilters;
  limit?: number;
  offset?: number;
}

/**
 * Response from listing events.
 */
export interface ListEventsResponse {
  events: UnifiedEvent[];
  total: number;
  hasMore: boolean;
}

/**
 * Request for searching events.
 */
export interface SearchEventsRequest {
  query: string;
  types?: EntityType[];
  limit?: number;
}

/**
 * Response from searching events.
 */
export interface SearchEventsResponse {
  results: Array<UnifiedEvent & { score: number }>;
  total: number;
  facets: Record<EntityType, number>;
}

// =============================================================================
// SSE Event Types
// =============================================================================

/**
 * SSE event from the explorer stream.
 */
export type StreamEvent =
  | { type: 'event'; event: UnifiedEvent }
  | { type: 'batch'; events: UnifiedEvent[] }
  | { type: 'connected' }
  | { type: 'heartbeat' };

// =============================================================================
// Type Guards
// =============================================================================

export function isMarkMetadata(m: EventMetadata): m is MarkMetadata {
  return m.type === 'mark';
}

export function isCrystalMetadata(m: EventMetadata): m is CrystalMetadata {
  return m.type === 'crystal';
}

export function isTrailMetadata(m: EventMetadata): m is TrailMetadata {
  return m.type === 'trail';
}

export function isEvidenceMetadata(m: EventMetadata): m is EvidenceMetadata {
  return m.type === 'evidence';
}

export function isTeachingMetadata(m: EventMetadata): m is TeachingMetadata {
  return m.type === 'teaching';
}

export function isLemmaMetadata(m: EventMetadata): m is LemmaMetadata {
  return m.type === 'lemma';
}
