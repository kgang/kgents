/**
 * KBlockProjection Types
 *
 * "Every K-Block is a morphism. Every projection is a functor."
 *
 * The universal K-Block type system for multi-surface projection.
 * K-Blocks can render as graphs, feeds, chats, portals, or proofs—
 * while maintaining identity laws and constitutional coherence.
 */

// =============================================================================
// Core K-Block Structure (matches backend models/kblock.py)
// =============================================================================

export interface KBlock {
  /** Unique identifier */
  id: string;

  /** File path or logical path */
  path: string;

  /** Content (Markdown) */
  content: string;

  /** Original content (for diff) */
  baseContent: string;

  /** Content hash for deduplication */
  contentHash: string;

  /** Isolation state: PRISTINE | DIRTY | STALE | CONFLICTING | ENTANGLED */
  isolation: string;

  /** Zero Seed layer (1-7) or null for regular files */
  zeroSeedLayer: number | null;

  /** Zero Seed kind: "axiom", "value", "goal", etc. */
  zeroSeedKind: string | null;

  /** Parent K-Block IDs (lineage tracking) */
  lineage: string[];

  /** Has Toulmin proof attached */
  hasProof: boolean;

  /** Toulmin proof structure (optional) */
  toulminProof: ToulminProof | null;

  /** Confidence score (0.0 - 1.0) */
  confidence: number;

  /** Incoming edges (cached for graph traversal) */
  incomingEdges: KBlockEdge[];

  /** Outgoing edges (cached for graph traversal) */
  outgoingEdges: KBlockEdge[];

  /** Tags */
  tags: string[];

  /** Created by (user/system) */
  createdBy: string;

  /** Timestamps */
  createdAt: Date;
  updatedAt: Date;

  /** Not ingested into cosmos or sovereign store */
  notIngested: boolean;

  /** Needs analysis before editing */
  analysisRequired: boolean;
}

// =============================================================================
// K-Block Edges
// =============================================================================

export interface KBlockEdge {
  /** Edge ID */
  id: string;

  /** Source K-Block ID */
  sourceId: string;

  /** Target K-Block ID */
  targetId: string;

  /** Edge kind: derives_from, refines, contradicts, evidence_for, implements */
  kind: string;

  /** Human-readable label */
  label: string | null;

  /** Edge metadata */
  metadata: Record<string, unknown>;

  /** Created by */
  createdBy: string;

  /** Timestamps */
  createdAt: Date;
  updatedAt: Date;
}

// =============================================================================
// Toulmin Proof Structure
// =============================================================================

export interface ToulminProof {
  /** Claim being proven */
  claim: string;

  /** Grounds (evidence, data) */
  grounds: string[];

  /** Warrant (inference rule) */
  warrant: string;

  /** Backing (justification for warrant) */
  backing?: string;

  /** Qualifiers (modal strength: "certainly", "probably", etc.) */
  qualifier?: string;

  /** Rebuttals (conditions where claim doesn't hold) */
  rebuttals?: string[];
}

// =============================================================================
// Observer Context
// =============================================================================

/**
 * Observer: The lens through which K-Blocks are perceived.
 * Different observers see different aspects (Umwelt principle).
 */
export interface ObserverContext {
  /** Observer ID */
  id: string;

  /** Observer type: user, agent, system */
  type: 'user' | 'agent' | 'system';

  /** Principles this observer cares about */
  principles: string[];

  /** Permissions/capabilities */
  capabilities: string[];

  /** Density preference (compact/comfortable/spacious) */
  density?: 'compact' | 'comfortable' | 'spacious';

  /** Custom metadata */
  metadata?: Record<string, unknown>;
}

// =============================================================================
// Projection Modes
// =============================================================================

/**
 * ProjectionMode: The surface on which K-Blocks render.
 */
export type ProjectionMode =
  | 'graph'      // Hypergraph node view (force-directed, spatial)
  | 'feed'       // Feed item view (chronological stream)
  | 'chat'       // Chat message view (conversation)
  | 'portal'     // Expanded portal view (full detail)
  | 'genesis'    // Genesis cascade view (Zero Seed lineage)
  | 'card'       // Summary card view (compact)
  | 'inline'     // Inline text view (minimal)
  | 'diff'       // Diff view (content vs. baseContent)
  | 'proof';     // Toulmin proof view (structured argument)

// =============================================================================
// Witness Marks
// =============================================================================

export interface WitnessMark {
  /** Mark ID */
  id: string;

  /** Action being witnessed */
  action: string;

  /** Timestamp */
  timestamp: Date;

  /** Tags */
  tags: string[];

  /** Metadata */
  metadata?: Record<string, unknown>;
}

// =============================================================================
// Constitutional Weights
// =============================================================================

/**
 * ConstitutionalWeights: Principle alignment scores for a K-Block.
 */
export interface ConstitutionalWeights {
  tasteful: number;       // 0-1
  curated: number;
  ethical: number;
  joyInducing: number;
  composable: number;
  heterarchical: number;
  generative: number;
}

// =============================================================================
// Galois Loss Indicator
// =============================================================================

/**
 * Galois loss: Coherence drift across layers (0 = perfect, 1 = max drift).
 */
export interface GaloisLoss {
  /** Overall loss score */
  loss: number;

  /** Layer where loss originates (if known) */
  sourceLayer?: number;

  /** Layer where loss is observed */
  targetLayer?: number;

  /** Loss direction: 'lower' (down the stack) or 'higher' (up the stack) */
  direction?: 'lower' | 'higher';
}

// =============================================================================
// Contradiction Detection
// =============================================================================

export interface Contradiction {
  /** Contradiction ID */
  id: string;

  /** K-Block IDs involved */
  kblockIds: string[];

  /** Contradiction type: logical, temporal, constitutional */
  type: 'logical' | 'temporal' | 'constitutional';

  /** Severity: minor, major, critical */
  severity: 'minor' | 'major' | 'critical';

  /** Description */
  description: string;

  /** Suggested resolution */
  resolution?: string;
}

// =============================================================================
// Component Props
// =============================================================================

export interface KBlockProjectionProps {
  /** The K-Block to render */
  kblock: KBlock;

  /** Observer context (who's viewing this) */
  observer: ObserverContext;

  /** Projection mode (how to render) */
  projection: ProjectionMode;

  /** Depth in graph (for recursion limits) */
  depth?: number;

  /** Callback when witness mark is created */
  onWitness?: (mark: WitnessMark) => void;

  /** Callback when navigating Galois loss (up/down layers) */
  onNavigateLoss?: (direction: 'lower' | 'higher') => void;

  /** Constitutional weights (optional, calculated if not provided) */
  constitutionalWeights?: ConstitutionalWeights;

  /** Contradiction badge (optional) */
  contradiction?: Contradiction;

  /** Custom className */
  className?: string;
}

// =============================================================================
// Individual Projection Props
// =============================================================================

export interface ProjectionComponentProps {
  kblock: KBlock;
  observer: ObserverContext;
  depth?: number;
  onWitness?: (mark: WitnessMark) => void;
  onNavigateLoss?: (direction: 'lower' | 'higher') => void;
  constitutionalWeights?: ConstitutionalWeights;
  contradiction?: Contradiction;
  className?: string;
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Calculate Galois loss for a K-Block (simplified heuristic).
 */
export function calculateGaloisLoss(kblock: KBlock): GaloisLoss {
  // If K-Block has high drift between content and baseContent, loss is high
  const contentDrift = kblock.content !== kblock.baseContent ? 0.3 : 0.0;

  // If confidence is low, loss increases
  const confidencePenalty = (1.0 - kblock.confidence) * 0.5;

  // If isolation is CONFLICTING or ENTANGLED, loss is high
  const isolationPenalty =
    kblock.isolation === 'CONFLICTING' || kblock.isolation === 'ENTANGLED'
      ? 0.4
      : kblock.isolation === 'DIRTY'
      ? 0.2
      : 0.0;

  const totalLoss = Math.min(1.0, contentDrift + confidencePenalty + isolationPenalty);

  return {
    loss: totalLoss,
    sourceLayer: kblock.zeroSeedLayer ?? undefined,
    direction: totalLoss > 0.5 ? 'lower' : undefined,
  };
}

/**
 * Get default constitutional weights for a K-Block.
 */
export function getDefaultConstitutionalWeights(kblock: KBlock): ConstitutionalWeights {
  // Heuristic: tags and principles drive weights
  const hasPrinciple = (key: string) =>
    kblock.tags.some((tag) => tag.toLowerCase().includes(key.toLowerCase()));

  return {
    tasteful: hasPrinciple('tasteful') ? 0.9 : 0.5,
    curated: hasPrinciple('curated') ? 0.9 : 0.5,
    ethical: hasPrinciple('ethical') ? 0.9 : 0.5,
    joyInducing: hasPrinciple('joy') ? 0.9 : 0.5,
    composable: hasPrinciple('composable') ? 0.9 : 0.5,
    heterarchical: hasPrinciple('heterarchical') ? 0.9 : 0.5,
    generative: hasPrinciple('generative') ? 0.9 : 0.5,
  };
}

/**
 * Get layer name (matches Feed primitive).
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
 * Get layer color (matches Feed primitive).
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

/**
 * Get loss color based on severity.
 */
export const LOSS_COLORS = {
  HEALTHY: '#22c55e',    // < 0.2
  WARNING: '#f59e0b',    // 0.2-0.5
  CRITICAL: '#ef4444',   // 0.5-0.8
  EMERGENCY: '#dc2626',  // > 0.8
};

export function getLossColor(loss: number): string {
  if (loss < 0.2) return LOSS_COLORS.HEALTHY;
  if (loss < 0.5) return LOSS_COLORS.WARNING;
  if (loss < 0.8) return LOSS_COLORS.CRITICAL;
  return LOSS_COLORS.EMERGENCY;
}
