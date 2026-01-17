/**
 * Constitutional Graph Types
 *
 * TypeScript types for the ASHC Self-Awareness system's K-Block derivation graph.
 *
 * Philosophy:
 *   "The proof IS the decision. The mark IS the witness."
 *
 * The Constitutional structure has 23 K-Blocks across 4 layers:
 * - L0: Axioms (A1_ENTITY, A2_MORPHISM, A3_MIRROR, G_GALOIS)
 * - L1: Primitives (COMPOSE, JUDGE, GROUND, ID, CONTRADICT, SUBLATE, FIX)
 * - L2: Principles (CONSTITUTION, TASTEFUL, CURATED, ETHICAL, JOY_INDUCING, COMPOSABLE, HETERARCHICAL, GENERATIVE)
 * - L3: Architecture (ASHC, METAPHYSICAL_FULLSTACK, HYPERGRAPH_EDITOR, AGENTESE)
 *
 * @see services/zero_seed/ashc_self_awareness.py
 */

// =============================================================================
// Epistemic Layer Types
// =============================================================================

/**
 * The four epistemic layers in the Constitutional hierarchy.
 * L0 = ground truth axioms, L3 = architectural decisions
 */
export type EpistemicLayer = 0 | 1 | 2 | 3;

export const LAYER_NAMES: Record<EpistemicLayer, string> = {
  0: 'Axioms',
  1: 'Primitives',
  2: 'Principles',
  3: 'Architecture',
};

export const LAYER_DESCRIPTIONS: Record<EpistemicLayer, string> = {
  0: 'Pre-categorical axioms - the irreducible ground',
  1: 'Operational primitives derived from axioms',
  2: 'Constitutional principles for taste and ethics',
  3: 'Architectural blocks implementing principles',
};

// =============================================================================
// Evidence Tier (from Galois loss)
// =============================================================================

/**
 * Evidence tier classification based on Galois loss.
 *
 * Loss thresholds:
 * - CATEGORICAL: L < 0.10 (near-lossless, deductive)
 * - EMPIRICAL: L < 0.38 (moderate loss, inductive)
 * - AESTHETIC: L < 0.45 (taste-based judgment)
 * - SOMATIC: L < 0.65 (intuitive, embodied)
 * - CHAOTIC: L >= 0.65 (high entropy, unreliable)
 */
export type EvidenceTier = 'categorical' | 'empirical' | 'aesthetic' | 'somatic' | 'chaotic';

export const EVIDENCE_TIER_THRESHOLDS: Record<EvidenceTier, number> = {
  categorical: 0.1,
  empirical: 0.38,
  aesthetic: 0.45,
  somatic: 0.65,
  chaotic: 1.0,
};

export const EVIDENCE_TIER_COLORS: Record<EvidenceTier, string> = {
  categorical: '#22c55e', // Green - high confidence
  empirical: '#3b82f6', // Blue - evidence-based
  aesthetic: '#a855f7', // Purple - taste-based
  somatic: '#f59e0b', // Yellow - intuitive
  chaotic: '#ef4444', // Red - unreliable
};

export function getEvidenceTier(loss: number): EvidenceTier {
  if (loss < 0.1) return 'categorical';
  if (loss < 0.38) return 'empirical';
  if (loss < 0.45) return 'aesthetic';
  if (loss < 0.65) return 'somatic';
  return 'chaotic';
}

// =============================================================================
// K-Block Types
// =============================================================================

/**
 * A Constitutional K-Block in the derivation graph.
 */
export interface ConstitutionalKBlock {
  /** Unique identifier (e.g., "A1_ENTITY", "COMPOSABLE") */
  id: string;
  /** Human-readable title */
  title: string;
  /** Epistemic layer (0-3) */
  layer: EpistemicLayer;
  /** Galois loss measuring derivation distance [0.0, 1.0] */
  galoisLoss: number;
  /** Evidence tier derived from loss */
  evidenceTier: EvidenceTier;
  /** Parent K-Block IDs this derives from */
  derivesFrom: string[];
  /** Child K-Block IDs that derive from this */
  dependents: string[];
  /** Semantic tags for filtering */
  tags: string[];
  /** Optional markdown content */
  content?: string;
}

/**
 * A derivation edge between two K-Blocks.
 */
export interface DerivationEdge {
  /** Source K-Block ID (parent) */
  sourceId: string;
  /** Target K-Block ID (child) */
  targetId: string;
  /** Galois loss for this derivation step */
  loss: number;
}

// =============================================================================
// Grounding Result Types (from ASHC API)
// =============================================================================

/**
 * Result of am_i_grounded() query.
 */
export interface GroundingResult {
  /** True if derivation path reaches L0 axioms */
  isGrounded: boolean;
  /** List of block IDs from L0 to this block */
  derivationPath: string[];
  /** Galois loss accumulated at each derivation step */
  lossAtEachStep: number[];
  /** Classification of overall derivation quality */
  evidenceTier: EvidenceTier;
  /** Sum of losses along the derivation path */
  totalLoss: number;
}

/**
 * Result of what_principle_justifies() query.
 */
export interface JustificationResult {
  /** The justifying principle (e.g., "COMPOSABLE") */
  principle: string;
  /** Galois loss measuring alignment with principle */
  lossScore: number;
  /** Human-readable explanation of the justification */
  reasoning: string;
  /** Path from principle to action */
  derivationChain: string[];
  /** Classification based on loss score */
  evidenceTier: EvidenceTier;
}

/**
 * A specific consistency violation.
 */
export interface ConsistencyViolation {
  /** Type of violation */
  kind: 'circular' | 'orphan' | 'layer_violation' | 'missing_parent';
  /** K-Block ID with the violation */
  blockId: string;
  /** Human-readable description */
  description: string;
  /** Related K-Block IDs */
  relatedBlocks: string[];
}

/**
 * Result of verify_self_consistency() query.
 */
export interface ConsistencyReport {
  /** True if no violations found */
  isConsistent: boolean;
  /** List of specific issues */
  violations: ConsistencyViolation[];
  /** Detected cycles */
  circularDependencies: [string, string][];
  /** Blocks not reaching L0 */
  orphanBlocks: string[];
  /** Total number of blocks */
  totalBlocks: number;
  /** Number of grounded blocks */
  groundedBlocks: number;
  /** Computed consistency score */
  consistencyScore: number;
}

// =============================================================================
// Graph Layout Types
// =============================================================================

/**
 * Position of a node in the graph visualization.
 */
export interface NodePosition {
  x: number;
  y: number;
}

/**
 * Visual state of a K-Block in the graph.
 */
export interface KBlockVisualState {
  /** The K-Block data */
  block: ConstitutionalKBlock;
  /** Position in the graph */
  position: NodePosition;
  /** Whether this block is selected */
  isSelected: boolean;
  /** Whether this block is highlighted (part of derivation path) */
  isHighlighted: boolean;
  /** Whether this block is an orphan */
  isOrphan: boolean;
}

/**
 * UI density mode from elastic-ui-patterns.
 */
export type DensityMode = 'compact' | 'comfortable' | 'spacious';

/**
 * Density-aware size constants.
 */
export const DENSITY_SIZES: Record<
  DensityMode,
  {
    nodeWidth: number;
    nodeHeight: number;
    layerGap: number;
    nodeGap: number;
    fontSize: number;
    padding: number;
  }
> = {
  compact: {
    nodeWidth: 100,
    nodeHeight: 32,
    layerGap: 80,
    nodeGap: 12,
    fontSize: 10,
    padding: 4,
  },
  comfortable: {
    nodeWidth: 140,
    nodeHeight: 40,
    layerGap: 100,
    nodeGap: 16,
    fontSize: 11,
    padding: 6,
  },
  spacious: {
    nodeWidth: 180,
    nodeHeight: 48,
    layerGap: 120,
    nodeGap: 20,
    fontSize: 12,
    padding: 8,
  },
};

// =============================================================================
// Constitutional Block Constants
// =============================================================================

/**
 * L0 Axioms - The irreducible ground
 */
export const L0_AXIOMS = ['A1_ENTITY', 'A2_MORPHISM', 'A3_MIRROR', 'G_GALOIS'] as const;

/**
 * L1 Kernel Primitives
 */
export const L1_KERNEL = ['COMPOSE', 'JUDGE', 'GROUND'] as const;

/**
 * L1 Derived Primitives
 */
export const L1_DERIVED = ['ID', 'CONTRADICT', 'SUBLATE', 'FIX'] as const;

/**
 * All L1 blocks (kernel + derived)
 */
export const L1_PRIMITIVES = [...L1_KERNEL, ...L1_DERIVED] as const;

/**
 * L2 Constitutional Principles (with CONSTITUTION as root)
 */
export const L2_PRINCIPLES = [
  'CONSTITUTION',
  'TASTEFUL',
  'CURATED',
  'ETHICAL',
  'JOY_INDUCING',
  'COMPOSABLE',
  'HETERARCHICAL',
  'GENERATIVE',
] as const;

/**
 * L3 Architecture Blocks
 */
export const L3_ARCHITECTURE = [
  'ASHC',
  'METAPHYSICAL_FULLSTACK',
  'HYPERGRAPH_EDITOR',
  'AGENTESE',
] as const;

/**
 * All Constitutional block IDs
 */
export const ALL_CONSTITUTIONAL_BLOCKS = [
  ...L0_AXIOMS,
  ...L1_PRIMITIVES,
  ...L2_PRINCIPLES,
  ...L3_ARCHITECTURE,
] as const;

export type ConstitutionalBlockId = (typeof ALL_CONSTITUTIONAL_BLOCKS)[number];

/**
 * Layer colors for visual distinction
 */
export const LAYER_COLORS: Record<EpistemicLayer, string> = {
  0: '#8b5cf6', // Purple - axioms
  1: '#3b82f6', // Blue - primitives
  2: '#10b981', // Green - principles
  3: '#f59e0b', // Yellow - architecture
};

/**
 * Principle colors (matching NavigationConstitutionalBadge)
 */
export const PRINCIPLE_COLORS: Record<string, string> = {
  TASTEFUL: '#8ba98b', // glow-lichen
  CURATED: '#c4a77d', // glow-spore
  ETHICAL: '#4a6b4a', // life-sage (paramount)
  JOY_INDUCING: '#d4b88c', // glow-amber
  COMPOSABLE: '#6b8b6b', // life-mint
  HETERARCHICAL: '#8bab8b', // life-sprout
  GENERATIVE: '#e5c99d', // glow-light
  CONSTITUTION: '#8b5cf6', // Purple (root)
};
