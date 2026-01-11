/**
 * Constitutional History Types
 *
 * Type definitions for the Constitutional History visualization,
 * showing how the kgents constitution has evolved over time.
 *
 * Week 11-12 of the Self-Reflective OS.
 */

// =============================================================================
// Core History Types
// =============================================================================

/**
 * A moment in constitutional history - a single point of change.
 */
export interface ConstitutionalMoment {
  /** Unique identifier */
  id: string;
  /** When this moment occurred */
  timestamp: string;
  /** Type of constitutional change */
  type: 'genesis' | 'amendment' | 'derivation_added' | 'drift_correction';
  /** Human-readable title */
  title: string;
  /** Extended description of the change */
  description: string;
  /** Constitutional layer affected (0=Axiom, 1=Value, 2=Spec, 3=Tuning, 4=Impl) */
  layer: number;
  /** Path to the affected K-Block */
  kblockPath: string;
  /** Amendment ID if this was an amendment */
  amendmentId?: string;
  /** Git commit SHA linked to this change */
  commitSha?: string;
  /** Impact level of the change */
  impact: 'minor' | 'moderate' | 'significant' | 'constitutional';
  /** Reasoning behind the change */
  reasoning?: string;
  /** Author of the change */
  author?: 'kent' | 'claude' | 'system';
  /** Related witness marks */
  relatedMarks?: string[];
}

/**
 * A snapshot of the constitution at a point in time.
 */
export interface ConstitutionalSnapshot {
  /** When this snapshot was taken */
  timestamp: string;
  /** K-Blocks organized by layer */
  layers: {
    [layer: number]: {
      kblocks: Array<{
        id: string;
        path: string;
        title: string;
        status: 'stable' | 'amended' | 'new' | 'deprecated';
        /** Optional content preview */
        preview?: string;
      }>;
    };
  };
  /** Derivation edges at this point in time */
  derivationEdges: Array<{
    from: string;
    to: string;
    type: 'derives_from' | 'grounds' | 'refines';
  }>;
  /** Total Galois loss across the constitution */
  totalLoss?: number;
}

/**
 * Layer stability data for evolution visualization.
 */
export interface LayerStability {
  /** Layer number (0-4) */
  layer: number;
  /** Layer name */
  name: 'IRREDUCIBLE' | 'PRIMITIVE' | 'DERIVED' | 'ARCHITECTURE' | 'IMPLEMENTATION';
  /** Number of K-Blocks in this layer */
  kblockCount: number;
  /** Number of changes to this layer over the time range */
  changeCount: number;
  /** Stability score (0-1, higher = more stable) */
  stability: number;
  /** Last change timestamp */
  lastChanged?: string;
  /** Expected stability (L0 should be most stable) */
  expectedStability: number;
}

/**
 * Amendment details for viewing in MomentDetail.
 */
export interface AmendmentDetails {
  /** Amendment ID */
  id: string;
  /** Amendment title */
  title: string;
  /** The K-Block being amended */
  targetKBlock: string;
  /** The diff of the amendment (before/after) */
  diff: {
    before: string;
    after: string;
  };
  /** Reasoning for the amendment */
  reasoning: string;
  /** Related decisions/witnesses */
  relatedDecisions?: string[];
  /** Derived from which principles */
  derivedFrom?: string[];
}

/**
 * Derivation tree comparison data.
 */
export interface DerivationComparison {
  /** Timestamp of the "before" state */
  beforeTimestamp: string;
  /** Timestamp of the "after" state */
  afterTimestamp: string;
  /** Nodes in the tree */
  nodes: Array<{
    id: string;
    title: string;
    layer: number;
    /** Status in comparison */
    status: 'unchanged' | 'added' | 'removed' | 'modified';
    /** Position for layout */
    position?: { x: number; y: number };
  }>;
  /** Edges in the tree */
  edges: Array<{
    from: string;
    to: string;
    /** Status in comparison */
    status: 'unchanged' | 'added' | 'removed';
  }>;
  /** Galois loss change */
  lossChange: {
    before: number;
    after: number;
    delta: number;
  };
}

// =============================================================================
// Time Range and Filtering
// =============================================================================

/** Time range zoom levels */
export type TimeZoom = '1D' | '1W' | '1M' | 'ALL';

/** Filter for constitutional moments */
export interface HistoryFilter {
  /** Filter by layers (0-4) */
  layers?: number[];
  /** Filter by moment types */
  types?: ConstitutionalMoment['type'][];
  /** Filter by impact levels */
  impacts?: ConstitutionalMoment['impact'][];
  /** Search query for titles/descriptions */
  searchQuery?: string;
  /** Time range */
  timeRange?: {
    start: string;
    end: string;
  };
}

// =============================================================================
// History State
// =============================================================================

/** State for the Constitutional History view */
export interface HistoryState {
  /** Currently selected moment */
  selectedMoment: string | null;
  /** Current time zoom level */
  timeZoom: TimeZoom;
  /** Current filter */
  filter: HistoryFilter;
  /** Whether moment detail is expanded */
  detailExpanded: boolean;
  /** Comparison mode (for derivation tree comparison) */
  comparisonMode: boolean;
  /** First comparison point */
  compareFrom?: string;
  /** Second comparison point */
  compareTo?: string;
}

// =============================================================================
// Color and Display Constants
// =============================================================================

/**
 * Layer colors for the 5-layer constitutional hierarchy.
 * Extended from the 4-layer system to include L4 (Implementation).
 */
export const HISTORY_LAYER_COLORS = {
  0: '#c4a77d', // L0: IRREDUCIBLE (amber/honey glow)
  1: '#6b8b6b', // L1: PRIMITIVE (sage green)
  2: '#8b7355', // L2: DERIVED (earth brown)
  3: '#a39890', // L3: ARCHITECTURE (warm steel)
  4: '#71717a', // L4: IMPLEMENTATION (cool steel)
} as const;

export const HISTORY_LAYER_NAMES = {
  0: 'IRREDUCIBLE',
  1: 'PRIMITIVE',
  2: 'DERIVED',
  3: 'ARCHITECTURE',
  4: 'IMPLEMENTATION',
} as const;

/**
 * Impact colors for constitutional moments.
 */
export const IMPACT_COLORS = {
  minor: '#71717a', // Steel gray
  moderate: '#8b7355', // Earth brown
  significant: '#c4a77d', // Amber
  constitutional: '#d4b88c', // Bright amber (earned glow)
} as const;

/**
 * Type icons for constitutional moments.
 */
export const MOMENT_TYPE_LABELS = {
  genesis: 'Genesis',
  amendment: 'Amendment',
  derivation_added: 'Derivation',
  drift_correction: 'Drift Fix',
} as const;
