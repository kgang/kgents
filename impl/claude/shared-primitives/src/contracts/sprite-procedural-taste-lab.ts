/**
 * Sprite Procedural Taste Lab API Contracts
 *
 * CANONICAL SOURCE OF TRUTH for Sprite Taste Lab types.
 * "The mutation is the proof. The canon is the claim. Wild branches are honored guests."
 *
 * @layer L4 (Specification)
 * @backend protocols/api/witness.py (Witness integration)
 * @backend protocols/api/galois.py (Galois loss integration)
 *
 * @see pilots/sprite-procedural-taste-lab/PROTO_SPEC.md
 * @see pilots/CONTRACT_COHERENCE.md
 */

// =============================================================================
// Core Types
// =============================================================================

/**
 * Aesthetic weight for a principle/dimension.
 * Range [0, 1] where 1 = strong preference.
 */
export interface AestheticWeight {
  /** Name of the aesthetic dimension (e.g., "softness", "vibrancy") */
  dimension: string;
  /** Weight value [0, 1] */
  value: number;
  /** User's natural language for this dimension (emerges from use) */
  vocabulary?: string;
}

/**
 * Rationale for accepting or creating a mutation.
 * L3: Mutation Justification Law - Taste is never "just because."
 */
export interface MutationRationale {
  /** Why this mutation was accepted/proposed */
  reason: string;
  /** Which aesthetic dimensions it affects */
  affected_dimensions: string[];
  /** Artist's felt sense (natural language) */
  felt_sense?: string;
}

/**
 * A mutation proposal or applied mutation.
 */
export interface Mutation {
  /** Unique mutation identifier */
  id: string;
  /** Timestamp of mutation */
  timestamp: string;
  /** The specific change (abstract representation) */
  change_description: string;
  /** Aesthetic weights at time of mutation */
  aesthetic_weights: AestheticWeight[];
  /** Rationale for acceptance (required for accepted mutations) */
  rationale?: MutationRationale;
  /** Parent mutation (if any) */
  parent_id?: string;
  /** Galois loss relative to style target */
  galois_loss: number;
  /** Status: proposed, accepted, rejected, or wild */
  status: MutationStatus;
}

/**
 * Status of a mutation in the style evolution.
 */
export type MutationStatus = 'proposed' | 'accepted' | 'rejected' | 'wild';

/**
 * A branch in the style exploration tree.
 * L4: Branch Visibility Law - All branches remain inspectable until collapsed.
 */
export interface StyleBranch {
  /** Unique branch identifier */
  id: string;
  /** Human-readable branch name */
  name: string;
  /** Branch status */
  status: BranchStatus;
  /** Mutations in this branch (in order) */
  mutations: Mutation[];
  /** Parent branch (if not root) */
  parent_branch_id?: string;
  /** When the branch was created */
  created_at: string;
  /** When the branch was collapsed (if applicable) */
  collapsed_at?: string;
  /** Average Galois loss for this branch */
  average_loss: number;
  /** Is this branch considered "wild" (high loss)? */
  is_wild: boolean;
}

/**
 * Status of a style branch.
 */
export type BranchStatus = 'active' | 'canonical' | 'wild' | 'collapsed';

/**
 * The taste attractor - the visible gravity field.
 * L1: Taste Gravity Law - The system must reveal pull toward the style attractor.
 */
export interface TasteAttractor {
  /** Current canonical aesthetic weights */
  canonical_weights: AestheticWeight[];
  /** Drift threshold for "wild" classification */
  wild_threshold: number;
  /** Current stability score [0, 1] */
  stability: number;
  /** Natural language description of the current style */
  style_description: string;
  /** Vocabulary that has emerged from use */
  emergent_vocabulary: string[];
}

/**
 * A compressed proof of style stability.
 * L5: Style Continuity Law - The crystal must justify why the current style is stable.
 */
export interface StyleCrystal {
  /** Unique crystal identifier */
  id: string;
  /** When the crystal was created */
  created_at: string;
  /** Summary of the style journey */
  journey_summary: string;
  /** Why the current style is stable */
  stability_justification: string;
  /** Final aesthetic weights */
  final_weights: AestheticWeight[];
  /** Total mutations explored */
  mutations_explored: number;
  /** Mutations accepted into canon */
  mutations_accepted: number;
  /** Branches explored */
  branches_explored: number;
  /** Wild branches quarantined */
  wild_branches: number;
  /** Overall Galois loss of final style */
  final_loss: number;
  /** Key decision points in the journey */
  key_decisions: string[];
}

/**
 * Style trace - the immutable history.
 */
export interface StyleTrace {
  /** Trace identifier */
  id: string;
  /** Style/sprite being evolved */
  style_name: string;
  /** All branches (canonical, wild, collapsed) */
  branches: StyleBranch[];
  /** Current attractor */
  attractor: TasteAttractor;
  /** All crystals created for this style */
  crystals: StyleCrystal[];
  /** Created timestamp */
  created_at: string;
  /** Last updated timestamp */
  updated_at: string;
}

// =============================================================================
// Sprite Representation
// =============================================================================

/**
 * A simple sprite representation for the lab.
 * Focuses on aesthetic properties, not game integration.
 */
export interface Sprite {
  /** Unique sprite identifier */
  id: string;
  /** Sprite name */
  name: string;
  /** Canvas width (pixels) */
  width: number;
  /** Canvas height (pixels) */
  height: number;
  /** Palette colors (hex) */
  palette: string[];
  /** Pixel data as flattened array (color indices) */
  pixels: number[];
  /** Current aesthetic weights */
  weights: AestheticWeight[];
  /** Trace of this sprite's evolution */
  trace_id?: string;
}

// =============================================================================
// API Request/Response Types
// =============================================================================

/**
 * Request to propose a mutation.
 */
export interface ProposeMutationRequest {
  /** Sprite ID to mutate */
  sprite_id: string;
  /** Description of proposed change */
  change_description: string;
  /** Affected aesthetic dimensions */
  affected_dimensions: string[];
}

/**
 * Response from mutation proposal.
 */
export interface ProposeMutationResponse {
  /** The proposed mutation */
  mutation: Mutation;
  /** Preview of result (new pixel data) */
  preview_pixels?: number[];
  /** Galois loss relative to current attractor */
  galois_loss: number;
  /** Whether this would be classified as "wild" */
  is_wild: boolean;
  /** Drift description in natural language */
  drift_description: string;
}

/**
 * Request to accept a mutation.
 */
export interface AcceptMutationRequest {
  /** Mutation ID to accept */
  mutation_id: string;
  /** Required: reason for acceptance (L3) */
  rationale: MutationRationale;
  /** Optional: branch to accept into (default: current canonical) */
  target_branch_id?: string;
}

/**
 * Request to create a wild branch.
 */
export interface CreateWildBranchRequest {
  /** Branch name */
  name: string;
  /** Starting mutation IDs (optional) */
  starting_mutations?: string[];
}

/**
 * Request to collapse a branch.
 */
export interface CollapseBranchRequest {
  /** Branch ID to collapse */
  branch_id: string;
  /** Whether to archive (true) or merge into canonical (false) */
  archive: boolean;
}

/**
 * Request to crystallize the current style.
 */
export interface CrystallizeRequest {
  /** Style trace ID */
  trace_id: string;
  /** Optional: custom stability justification */
  stability_justification?: string;
}

// =============================================================================
// Demo Corpus (HQ-4 Compliance)
// =============================================================================

/**
 * Demo sprites for cold-start experience.
 * These provide immediate exploration without requiring user creation.
 */
export const DEMO_SPRITES: Sprite[] = [
  {
    id: 'demo-sprite-1',
    name: 'Forest Wanderer',
    width: 8,
    height: 8,
    palette: ['#1a1c2c', '#5d275d', '#b13e53', '#ef7d57', '#ffcd75', '#a7f070', '#38b764', '#257179'],
    pixels: [
      0,0,0,3,3,0,0,0,
      0,0,3,4,4,3,0,0,
      0,0,2,4,4,2,0,0,
      0,3,1,2,2,1,3,0,
      0,3,3,1,1,3,3,0,
      0,0,5,5,5,5,0,0,
      0,5,6,5,5,6,5,0,
      0,7,0,5,5,0,7,0,
    ],
    weights: [
      { dimension: 'warmth', value: 0.7, vocabulary: 'cozy' },
      { dimension: 'softness', value: 0.6, vocabulary: 'rounded edges' },
      { dimension: 'vibrancy', value: 0.4, vocabulary: 'muted' },
    ],
  },
  {
    id: 'demo-sprite-2',
    name: 'Ocean Drifter',
    width: 8,
    height: 8,
    palette: ['#0d2b45', '#203c56', '#544e68', '#8d697a', '#d08159', '#ffaa5e', '#ffd4a3', '#ffecd6'],
    pixels: [
      0,0,1,1,1,1,0,0,
      0,1,2,2,2,2,1,0,
      1,2,3,7,7,3,2,1,
      1,2,3,4,4,3,2,1,
      1,2,3,4,4,3,2,1,
      0,1,2,3,3,2,1,0,
      0,0,1,2,2,1,0,0,
      0,0,0,1,1,0,0,0,
    ],
    weights: [
      { dimension: 'warmth', value: 0.3, vocabulary: 'cool depths' },
      { dimension: 'softness', value: 0.8, vocabulary: 'flowing' },
      { dimension: 'vibrancy', value: 0.5, vocabulary: 'gentle glow' },
    ],
  },
];

/**
 * Demo style trace for cold-start.
 */
export const DEMO_TRACE: StyleTrace = {
  id: 'demo-trace',
  style_name: 'Wanderer Series',
  branches: [
    {
      id: 'branch-canonical',
      name: 'Main Path',
      status: 'canonical',
      mutations: [
        {
          id: 'mut-1',
          timestamp: new Date(Date.now() - 86400000 * 2).toISOString(),
          change_description: 'Softened palette edges',
          aesthetic_weights: [{ dimension: 'softness', value: 0.6 }],
          rationale: { reason: 'The hard edges felt too stark', affected_dimensions: ['softness'] },
          galois_loss: 0.08,
          status: 'accepted',
        },
        {
          id: 'mut-2',
          timestamp: new Date(Date.now() - 86400000).toISOString(),
          change_description: 'Added warmth to mid-tones',
          aesthetic_weights: [{ dimension: 'warmth', value: 0.7 }],
          rationale: { reason: 'Needed more life in the character', affected_dimensions: ['warmth'] },
          galois_loss: 0.05,
          status: 'accepted',
        },
      ],
      parent_branch_id: undefined,
      created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
      average_loss: 0.065,
      is_wild: false,
    },
    {
      id: 'branch-wild-1',
      name: 'Neon Experiment',
      status: 'wild',
      mutations: [
        {
          id: 'mut-wild-1',
          timestamp: new Date(Date.now() - 43200000).toISOString(),
          change_description: 'Pushed vibrancy to maximum',
          aesthetic_weights: [{ dimension: 'vibrancy', value: 0.95 }],
          rationale: { reason: 'Exploring what happens at the edge', affected_dimensions: ['vibrancy'] },
          galois_loss: 0.42,
          status: 'wild',
        },
      ],
      parent_branch_id: 'branch-canonical',
      created_at: new Date(Date.now() - 43200000).toISOString(),
      average_loss: 0.42,
      is_wild: true,
    },
  ],
  attractor: {
    canonical_weights: [
      { dimension: 'warmth', value: 0.7, vocabulary: 'cozy' },
      { dimension: 'softness', value: 0.6, vocabulary: 'rounded' },
      { dimension: 'vibrancy', value: 0.4, vocabulary: 'subtle' },
    ],
    wild_threshold: 0.3,
    stability: 0.82,
    style_description: 'A warm, approachable character style with soft edges and muted colors.',
    emergent_vocabulary: ['cozy', 'rounded', 'subtle', 'approachable', 'gentle'],
  },
  crystals: [],
  created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
  updated_at: new Date().toISOString(),
};

// =============================================================================
// Contract Invariants
// =============================================================================

/**
 * Invariant checks for Mutation.
 */
export const MUTATION_INVARIANTS = {
  'has id': (m: Mutation) => typeof m.id === 'string' && m.id.length > 0,
  'has timestamp': (m: Mutation) => typeof m.timestamp === 'string',
  'has status': (m: Mutation) => ['proposed', 'accepted', 'rejected', 'wild'].includes(m.status),
  'galois_loss in range': (m: Mutation) => m.galois_loss >= 0 && m.galois_loss <= 1,
  'accepted has rationale (L3)': (m: Mutation) =>
    m.status !== 'accepted' || (m.rationale !== undefined && m.rationale.reason.length > 0),
} as const;

/**
 * Invariant checks for StyleBranch.
 */
export const BRANCH_INVARIANTS = {
  'has id': (b: StyleBranch) => typeof b.id === 'string' && b.id.length > 0,
  'has status': (b: StyleBranch) => ['active', 'canonical', 'wild', 'collapsed'].includes(b.status),
  'collapsed has timestamp (L4)': (b: StyleBranch) =>
    b.status !== 'collapsed' || typeof b.collapsed_at === 'string',
  'mutations is array': (b: StyleBranch) => Array.isArray(b.mutations),
} as const;

/**
 * Invariant checks for StyleCrystal.
 */
export const STYLE_CRYSTAL_INVARIANTS = {
  'has id': (c: StyleCrystal) => typeof c.id === 'string' && c.id.length > 0,
  'has stability justification (L5)': (c: StyleCrystal) =>
    typeof c.stability_justification === 'string' && c.stability_justification.length > 0,
  'final_loss in range': (c: StyleCrystal) => c.final_loss >= 0 && c.final_loss <= 1,
} as const;

// =============================================================================
// Type Guards
// =============================================================================

/**
 * Type guard for Mutation.
 */
export function isMutation(data: unknown): data is Mutation {
  if (!data || typeof data !== 'object') return false;
  const m = data as Record<string, unknown>;
  return (
    typeof m.id === 'string' &&
    typeof m.timestamp === 'string' &&
    typeof m.change_description === 'string' &&
    typeof m.galois_loss === 'number' &&
    typeof m.status === 'string'
  );
}

/**
 * Type guard for StyleBranch.
 */
export function isStyleBranch(data: unknown): data is StyleBranch {
  if (!data || typeof data !== 'object') return false;
  const b = data as Record<string, unknown>;
  return (
    typeof b.id === 'string' &&
    typeof b.name === 'string' &&
    typeof b.status === 'string' &&
    Array.isArray(b.mutations)
  );
}

/**
 * Type guard for TasteAttractor.
 */
export function isTasteAttractor(data: unknown): data is TasteAttractor {
  if (!data || typeof data !== 'object') return false;
  const t = data as Record<string, unknown>;
  return (
    Array.isArray(t.canonical_weights) &&
    typeof t.wild_threshold === 'number' &&
    typeof t.stability === 'number'
  );
}

// =============================================================================
// Normalizers
// =============================================================================

/**
 * Normalize a potentially malformed Mutation.
 */
export function normalizeMutation(data: unknown): Mutation {
  const m = data as Partial<Mutation>;
  return {
    id: typeof m.id === 'string' ? m.id : `mut-${Date.now()}`,
    timestamp: typeof m.timestamp === 'string' ? m.timestamp : new Date().toISOString(),
    change_description: typeof m.change_description === 'string' ? m.change_description : '',
    aesthetic_weights: Array.isArray(m.aesthetic_weights) ? m.aesthetic_weights : [],
    rationale: m.rationale,
    parent_id: m.parent_id,
    galois_loss: typeof m.galois_loss === 'number' ? Math.max(0, Math.min(1, m.galois_loss)) : 0.5,
    status: isValidMutationStatus(m.status) ? m.status : 'proposed',
  };
}

/**
 * Normalize a potentially malformed TasteAttractor.
 */
export function normalizeTasteAttractor(data: unknown): TasteAttractor {
  const t = data as Partial<TasteAttractor>;
  return {
    canonical_weights: Array.isArray(t.canonical_weights) ? t.canonical_weights : [],
    wild_threshold: typeof t.wild_threshold === 'number' ? t.wild_threshold : 0.3,
    stability: typeof t.stability === 'number' ? Math.max(0, Math.min(1, t.stability)) : 0.5,
    style_description: typeof t.style_description === 'string' ? t.style_description : '',
    emergent_vocabulary: Array.isArray(t.emergent_vocabulary) ? t.emergent_vocabulary : [],
  };
}

/**
 * Check if value is a valid MutationStatus.
 */
function isValidMutationStatus(status: unknown): status is MutationStatus {
  return (
    typeof status === 'string' &&
    ['proposed', 'accepted', 'rejected', 'wild'].includes(status)
  );
}

// =============================================================================
// Aesthetic Baseline (HQ-3 Compliance)
// =============================================================================

/**
 * Baseline aesthetic dimensions that are always valid.
 * These should never be rejected by the system.
 */
export const BASELINE_AESTHETIC_DIMENSIONS = [
  'warmth',
  'softness',
  'vibrancy',
  'contrast',
  'complexity',
  'harmony',
  'weight',
  'movement',
  'balance',
  'rhythm',
] as const;

/**
 * Natural language vocabulary that maps to dimensions.
 * QA-4: System surfaces taste language without forcing jargon.
 */
export const AESTHETIC_VOCABULARY: Record<string, string[]> = {
  warmth: ['cozy', 'inviting', 'cold', 'distant', 'friendly'],
  softness: ['rounded', 'flowing', 'sharp', 'crisp', 'gentle'],
  vibrancy: ['punchy', 'muted', 'loud', 'quiet', 'subtle'],
  contrast: ['bold', 'gentle', 'stark', 'blended', 'dramatic'],
  complexity: ['busy', 'simple', 'intricate', 'minimal', 'layered'],
  harmony: ['unified', 'discordant', 'cohesive', 'clashing', 'balanced'],
  weight: ['heavy', 'light', 'grounded', 'floating', 'solid'],
  movement: ['dynamic', 'static', 'flowing', 'frozen', 'energetic'],
  balance: ['centered', 'off-kilter', 'stable', 'tense', 'relaxed'],
  rhythm: ['regular', 'syncopated', 'pulsing', 'steady', 'chaotic'],
};
