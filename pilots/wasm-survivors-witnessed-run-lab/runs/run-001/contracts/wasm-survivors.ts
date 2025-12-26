/**
 * Wasm Survivors: Witnessed Run Lab Contracts
 *
 * CANONICAL SOURCE OF TRUTH for run witnessing API.
 * Implements the Galois Loss theory: "The run is the proof. The build is the claim."
 *
 * @layer L4 (Specification)
 * @backend services/witness/run_lab.py
 * @see pilots/wasm-survivors-witnessed-run-lab/PROTO_SPEC.md
 */

// =============================================================================
// Build State (Core Domain Model)
// =============================================================================

/**
 * Current build state at any point during a run.
 * The "claim" in Galois Loss terms.
 */
export interface BuildState {
  /** Active upgrades (e.g., ["speed_boost", "damage_up"]) */
  upgrades: string[];

  /** Active synergies between upgrades */
  synergies: string[];

  /** Current risk level (player's style indicator) */
  risk_level: 'low' | 'medium' | 'high';

  /** Current tempo (pace of decision-making) */
  tempo: 'slow' | 'normal' | 'fast';

  /** Wave number when this state was captured */
  wave: number;
}

/**
 * Type of build shift that occurred.
 */
export type ShiftType =
  | 'upgrade_taken'     // L1: Player took an upgrade
  | 'upgrade_skipped'   // L3: Player skipped (creates ghost)
  | 'build_pivot'       // L1: Major direction change
  | 'risk_taken'        // L4: High-risk choice made
  | 'synergy_formed'    // Passive: Synergy emerged from choices
  | 'synergy_broken';   // Passive: Synergy lost due to change

// =============================================================================
// RunMark (L1: Run Coherence Law)
// =============================================================================

/**
 * A mark capturing a build shift during a run.
 *
 * L1: "A run is valid only if every major build shift is marked and justified."
 *
 * @invariant galois_loss in [0, 1]
 * @invariant is_drift = galois_loss > DRIFT_THRESHOLD
 */
export interface RunMark {
  /** Unique mark ID */
  mark_id: string;

  /** Run this mark belongs to */
  run_id: string;

  /** When the shift occurred */
  timestamp: string;

  // Build transition
  /** Build state before the shift */
  build_before: BuildState;

  /** Build state after the shift */
  build_after: BuildState;

  // Shift metadata
  /** Type of shift */
  shift_type: ShiftType;

  /** Optional justification (for L4 risk transparency) */
  justification?: string;

  /** Was this marked BEFORE effects resolved? (L4) */
  marked_before_resolution: boolean;

  // Galois coherence (L2)
  /** Galois loss for this transition [0, 1] */
  galois_loss: number;

  /** Whether this exceeds drift threshold (L2 surfacing) */
  is_drift: boolean;

  /** Evidence tier based on loss */
  evidence_tier: 'categorical' | 'empirical' | 'aesthetic' | 'somatic';
}

// =============================================================================
// GhostAlternative (L3: Ghost Commitment Law)
// =============================================================================

/**
 * An unchosen path recorded as a ghost.
 *
 * L3: "Unchosen upgrades are recorded as ghost alternatives."
 *
 * QA-4: "Ghost layer should feel like alternate timeline, not error log."
 */
export interface GhostAlternative {
  /** Unique ghost ID */
  ghost_id: string;

  /** Run this ghost belongs to */
  run_id: string;

  /** Links to the decision point (RunMark) where ghost was created */
  decision_point_id: string;

  /** When this ghost was created */
  timestamp: string;

  // What was not taken
  /** The upgrade that was passed on */
  unchosen_upgrade: string;

  /** Potential synergies that were foregone */
  unchosen_synergies: string[];

  // Counterfactual analysis (non-judgmental per QA-2)
  /** Hypothetical impact (descriptive, not punitive) */
  hypothetical_impact: 'beneficial' | 'neutral' | 'harmful' | 'unknown';

  /** Optional reasoning (for player reflection) */
  reasoning?: string;

  // Visual representation
  /** How prominent the ghost should be in UI (1-3) */
  salience: number;
}

// =============================================================================
// RunCrystal (L5: Proof Compression Law)
// =============================================================================

/**
 * Compressed proof of a complete run.
 *
 * L5: "A run crystal must reduce trace length while preserving causal rationale."
 *
 * QA-3: "Failure runs must produce CLEARER crystals than success runs."
 */
export interface RunCrystal {
  /** Unique crystal ID */
  crystal_id: string;

  /** Run this crystal summarizes */
  run_id: string;

  // Temporal bounds
  started_at: string;
  ended_at: string;

  // Outcome (descriptive, not judgmental)
  /** How the run ended */
  outcome: 'victory' | 'defeat' | 'abandoned';

  /** Waves survived */
  waves_survived: number;

  // Build identity claim (the "claim" in Galois terms)
  /**
   * One-sentence description of the build's identity.
   * e.g., "Aggressive glass cannon with late defensive pivot"
   *
   * This is the proof claim that the crystal justifies.
   */
  build_claim: string;

  // Causal summary
  /** Key pivot points that defined the run */
  key_pivots: RunMarkSummary[];

  /** Number of ghost alternatives recorded */
  ghost_count: number;

  // Coherence metrics
  /** Average Galois loss across all marks */
  average_galois_loss: number;

  /** Total drift events (L2 violations) */
  total_drift_events: number;

  // Constitutional alignment (QA-2: descriptive, not punitive)
  /** Style descriptors (e.g., ["aggressive", "adaptive", "synergy-focused"]) */
  style_descriptors: string[];

  // Compression metadata (Amendment G)
  /** How many marks were compressed */
  source_mark_count: number;

  /** Compression ratio (marks / 1) */
  compression_ratio: number;

  /** What was dropped in compression */
  compression_disclosure: string;
}

/**
 * Summary of a RunMark for inclusion in crystals.
 */
export interface RunMarkSummary {
  mark_id: string;
  wave: number;
  shift_type: ShiftType;
  galois_loss: number;
  brief: string;  // One-line summary
}

// =============================================================================
// Value Compass (Style Mirror)
// =============================================================================

/**
 * Value compass showing playstyle constitution.
 *
 * QA-2: "Players should feel their style is SEEN, not judged."
 */
export interface ValueCompass {
  run_id: string;

  // Style dimensions (all in [0, 1])
  /** Aggressive vs. Defensive play */
  aggression: number;

  /** Risk-taking tendency */
  risk_tolerance: number;

  /** Synergy-seeking behavior */
  synergy_focus: number;

  /** Adaptation frequency */
  adaptability: number;

  /** Tempo consistency */
  tempo_stability: number;

  // Dominant style (descriptive label)
  dominant_style: string;

  // Style consistency (Galois coherence of style)
  style_coherence: number;
}

// =============================================================================
// API Request/Response Types
// =============================================================================

/**
 * POST /api/witness/run/mark request
 */
export interface RunMarkRequest {
  run_id: string;
  build_before: BuildState;
  build_after: BuildState;
  shift_type: ShiftType;
  justification?: string;
  marked_before_resolution?: boolean;
}

/**
 * POST /api/witness/run/mark response
 */
export interface RunMarkResponse {
  mark: RunMark;
  warmth_response: string;  // WARMTH-calibrated feedback
}

/**
 * POST /api/witness/run/ghost request
 */
export interface GhostRequest {
  run_id: string;
  decision_point_id: string;
  unchosen_upgrade: string;
  unchosen_synergies?: string[];
  reasoning?: string;
}

/**
 * POST /api/witness/run/ghost response
 */
export interface GhostResponse {
  ghost: GhostAlternative;
  warmth_response: string;
}

/**
 * POST /api/witness/run/crystallize request
 */
export interface CrystallizeRunRequest {
  run_id: string;
}

/**
 * POST /api/witness/run/crystallize response
 */
export interface CrystallizeRunResponse {
  crystal: RunCrystal;
  compass: ValueCompass;
  warmth_response: string;
}

/**
 * GET /api/witness/run/{run_id}/trail response
 */
export interface RunTrailResponse {
  run_id: string;
  marks: RunMark[];
  ghosts: GhostAlternative[];
  current_build: BuildState;
  elapsed_time_ms: number;
}

// =============================================================================
// Constants (match Python backend)
// =============================================================================

/** Drift threshold (L2: surface when exceeded) */
export const DRIFT_THRESHOLD = 0.3;

/** High-risk threshold (L4: requires pre-marking) */
export const HIGH_RISK_THRESHOLD = 0.7;

/** Minimum marks for crystallization */
export const MIN_MARKS_FOR_CRYSTAL = 3;

/** Maximum latency for witness layer (QA-1, Anti-Success: Speed tax) */
export const MAX_WITNESS_LATENCY_MS = 5;

// =============================================================================
// Type Guards
// =============================================================================

export function isRunMark(data: unknown): data is RunMark {
  if (!data || typeof data !== 'object') return false;
  const r = data as Record<string, unknown>;
  return (
    typeof r.mark_id === 'string' &&
    typeof r.run_id === 'string' &&
    typeof r.timestamp === 'string' &&
    typeof r.galois_loss === 'number' &&
    typeof r.is_drift === 'boolean'
  );
}

export function isGhostAlternative(data: unknown): data is GhostAlternative {
  if (!data || typeof data !== 'object') return false;
  const r = data as Record<string, unknown>;
  return (
    typeof r.ghost_id === 'string' &&
    typeof r.run_id === 'string' &&
    typeof r.decision_point_id === 'string' &&
    typeof r.unchosen_upgrade === 'string'
  );
}

export function isRunCrystal(data: unknown): data is RunCrystal {
  if (!data || typeof data !== 'object') return false;
  const r = data as Record<string, unknown>;
  return (
    typeof r.crystal_id === 'string' &&
    typeof r.run_id === 'string' &&
    typeof r.build_claim === 'string' &&
    typeof r.average_galois_loss === 'number'
  );
}

// =============================================================================
// Normalizers (Defensive Coding)
// =============================================================================

export function normalizeRunMark(data: unknown): RunMark {
  const r = data as Partial<RunMark>;
  return {
    mark_id: r.mark_id || '',
    run_id: r.run_id || '',
    timestamp: r.timestamp || new Date().toISOString(),
    build_before: normalizeBuildState(r.build_before),
    build_after: normalizeBuildState(r.build_after),
    shift_type: r.shift_type || 'upgrade_taken',
    justification: r.justification,
    marked_before_resolution: r.marked_before_resolution ?? false,
    galois_loss: typeof r.galois_loss === 'number' ? Math.max(0, Math.min(1, r.galois_loss)) : 0.5,
    is_drift: r.is_drift ?? false,
    evidence_tier: r.evidence_tier || 'empirical',
  };
}

export function normalizeBuildState(data: unknown): BuildState {
  const r = data as Partial<BuildState> | undefined;
  return {
    upgrades: Array.isArray(r?.upgrades) ? r.upgrades : [],
    synergies: Array.isArray(r?.synergies) ? r.synergies : [],
    risk_level: r?.risk_level || 'medium',
    tempo: r?.tempo || 'normal',
    wave: typeof r?.wave === 'number' ? r.wave : 0,
  };
}

export function normalizeGhostAlternative(data: unknown): GhostAlternative {
  const r = data as Partial<GhostAlternative>;
  return {
    ghost_id: r.ghost_id || '',
    run_id: r.run_id || '',
    decision_point_id: r.decision_point_id || '',
    timestamp: r.timestamp || new Date().toISOString(),
    unchosen_upgrade: r.unchosen_upgrade || '',
    unchosen_synergies: Array.isArray(r.unchosen_synergies) ? r.unchosen_synergies : [],
    hypothetical_impact: r.hypothetical_impact || 'unknown',
    reasoning: r.reasoning,
    salience: typeof r.salience === 'number' ? r.salience : 1,
  };
}

// =============================================================================
// Contract Invariants (for test verification)
// =============================================================================

export const RUN_MARK_INVARIANTS = {
  'galois_loss in range': (r: RunMark) => r.galois_loss >= 0 && r.galois_loss <= 1,
  'has mark_id': (r: RunMark) => typeof r.mark_id === 'string' && r.mark_id.length > 0,
  'has run_id': (r: RunMark) => typeof r.run_id === 'string' && r.run_id.length > 0,
  'drift consistency': (r: RunMark) => r.is_drift === (r.galois_loss > DRIFT_THRESHOLD),
} as const;

export const RUN_CRYSTAL_INVARIANTS = {
  'average_galois_loss in range': (r: RunCrystal) => r.average_galois_loss >= 0 && r.average_galois_loss <= 1,
  'has build_claim': (r: RunCrystal) => typeof r.build_claim === 'string' && r.build_claim.length > 0,
  'compression_ratio positive': (r: RunCrystal) => r.compression_ratio > 0,
} as const;

export const GHOST_INVARIANTS = {
  'has unchosen_upgrade': (g: GhostAlternative) => typeof g.unchosen_upgrade === 'string' && g.unchosen_upgrade.length > 0,
  'salience in range': (g: GhostAlternative) => g.salience >= 1 && g.salience <= 3,
} as const;
