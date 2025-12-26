/**
 * Rap Coach Flow Lab API Contracts
 *
 * CANONICAL SOURCE OF TRUTH for Rap Coach pilot API interfaces.
 * Validates the Joy/Courage integration theory.
 *
 * Personality: "This pilot celebrates the rough voice, not the polished one.
 *              The coach is a witness, never a judge."
 *
 * @layer L4 (Specification)
 * @see pilots/rap-coach-flow-lab/PROTO_SPEC.md
 * @see plans/enlightened-synthesis/04-joy-integration.md
 */

// =============================================================================
// Core Types: Take and Session
// =============================================================================

/**
 * Intent declared BEFORE a take (L1 Intent Declaration Law)
 *
 * @invariant must be declared before take recording
 * @invariant cannot be modified after take begins
 */
export interface TakeIntent {
  /** What the artist is trying to express */
  expression_goal: string;

  /** The register being explored (aggressive, vulnerable, playful, etc.) */
  register: TakeRegister;

  /** Risk level - high risk takes get courage protection */
  risk_level: 'low' | 'medium' | 'high';

  /** Optional principle weights for this take */
  principle_weights?: Record<string, number>;
}

/**
 * Vocal/expressive register being explored
 */
export type TakeRegister =
  | 'aggressive'
  | 'vulnerable'
  | 'playful'
  | 'introspective'
  | 'storytelling'
  | 'technical'
  | 'experimental';

/**
 * A single take with intent and delivery
 *
 * @invariant take_id is unique within session
 * @invariant intent must be non-null
 */
export interface Take {
  /** Unique identifier */
  take_id: string;

  /** Session this take belongs to */
  session_id: string;

  /** Intent declared before recording (L1) */
  intent: TakeIntent;

  /** Timestamp of take start */
  timestamp: string;

  /** Duration in seconds */
  duration_seconds: number;

  /** Audio/text content reference */
  content_ref?: string;

  /** Transcription if available */
  transcription?: string;

  /** Ghost alternatives - roads not taken */
  ghosts?: GhostAlternative[];
}

/**
 * Ghost Alternative: Rejected phrasings that shaped the take
 *
 * From PROTO_SPEC: "Ghosts (rejected phrasings, alternate lines) are
 * part of the proof space. The roads not taken shaped the road taken."
 */
export interface GhostAlternative {
  /** The rejected line/phrasing */
  content: string;

  /** Why it was rejected */
  reason?: string;

  /** When in the take it was considered */
  position?: number;
}

// =============================================================================
// Feedback Types (L2 Feedback Grounding Law)
// =============================================================================

/**
 * Feedback grounded in specific evidence (L2 Law)
 *
 * @invariant All critique must reference a mark or trace segment
 * @invariant anchor_take_id must be valid take in session
 */
export interface GroundedFeedback {
  /** The feedback content */
  content: string;

  /** Reference to the take this feedback is about */
  anchor_take_id: string;

  /** Specific moment in the take (optional) */
  anchor_timestamp?: number;

  /** Mark ID that this feedback is attached to */
  mark_id: string;

  /** Type of feedback */
  feedback_type: FeedbackType;
}

export type FeedbackType =
  | 'voice_observation'    // What we noticed about voice
  | 'technique_note'       // Technical observation (not judgment)
  | 'pattern_recognition'  // Cross-take pattern
  | 'repair_suggestion';   // L5: Repair path, not verdict

// =============================================================================
// Session and Crystal Types
// =============================================================================

/**
 * A practice session containing multiple takes
 */
export interface RapCoachSession {
  /** Unique session identifier */
  session_id: string;

  /** Takes in chronological order */
  takes: Take[];

  /** Session start timestamp */
  started_at: string;

  /** Session end timestamp (null if ongoing) */
  ended_at?: string;

  /** Grounded feedback accumulated */
  feedback: GroundedFeedback[];

  /** Joy observations during session */
  joy_observations: JoyObservation[];
}

/**
 * Voice Crystal: Compressive proof of voice evolution
 *
 * From PROTO_SPEC: "Crystals must state what changed in voice and why,
 * with evidence anchors. The crystal is warm - it sees the artist."
 *
 * L3 Voice Continuity Law: Crystal summaries must identify the
 * through-line of voice across a session.
 */
export interface VoiceCrystal {
  /** Crystal identifier */
  crystal_id: string;

  /** Session this crystal is for */
  session_id: string;

  /** What changed in voice (the insight) */
  voice_delta: string;

  /** The through-line identified (L3) */
  voice_throughline: string;

  /** Evidence anchors (take IDs) */
  evidence_anchors: string[];

  /** Courage moments preserved (L4) */
  courage_moments: CourageMoment[];

  /** Mood of the session */
  mood: MoodVector;

  /** Warmth disclosure (never cold) */
  warmth_disclosure: string;

  /** Compression honesty */
  compression_honesty: CompressionHonesty;

  /** Galois loss for this crystal */
  galois_loss: number;
}

/**
 * Courage Moment: High-risk take that was protected (L4)
 *
 * L4 Courage Preservation Law: High-risk takes are protected from
 * negative weighting by default. Courage is rewarded, not punished.
 */
export interface CourageMoment {
  /** Take that showed courage */
  take_id: string;

  /** What made it courageous */
  courage_description: string;

  /** The risk that was taken */
  risk_taken: string;

  /** Whether it "worked" (optional - courage is valued regardless) */
  outcome?: 'landed' | 'missed' | 'evolving';
}

// =============================================================================
// Joy Integration Types
// =============================================================================

/**
 * Joy observation during practice
 *
 * Joy calibration for rap-coach:
 *   WARMTH:   0.9 (primary - the kind coach)
 *   SURPRISE: 0.3 (secondary - unexpected voice breakthroughs)
 *   FLOW:     0.7 (tertiary - creative momentum)
 */
export interface JoyObservation {
  /** Dominant joy mode */
  mode: JoyMode;

  /** Intensity [0, 1] */
  intensity: number;

  /** What triggered this observation */
  trigger: string;

  /** Timestamp */
  timestamp: string;

  /** Optional take reference */
  take_id?: string;
}

export type JoyMode = 'warmth' | 'surprise' | 'flow';

/**
 * Seven-dimensional affective signature
 */
export interface MoodVector {
  warmth: number;      // Cold/clinical <-> Warm/engaging
  weight: number;      // Light/playful <-> Heavy/serious
  tempo: number;       // Slow/deliberate <-> Fast/urgent
  texture: number;     // Smooth/flowing <-> Rough/struggling
  brightness: number;  // Dim/frustrated <-> Bright/joyful
  saturation: number;  // Muted/routine <-> Vivid/intense
  complexity: number;  // Simple/focused <-> Complex/branching
}

// =============================================================================
// Repair Path Types (L5)
// =============================================================================

/**
 * Repair Path: Navigable path forward, not a verdict
 *
 * L5 Repair Path Law: If loss is high, the system proposes a repair
 * path - not a verdict. Failure is navigable, not final.
 */
export interface RepairPath {
  /** What needs attention */
  observation: string;

  /** Specific, actionable suggestion */
  suggestion: string;

  /** Reference take */
  reference_take_id: string;

  /** Difficulty of the repair */
  difficulty: 'quick_fix' | 'practice_focus' | 'longer_journey';

  /** Optional example from the session */
  positive_example_take_id?: string;
}

// =============================================================================
// Compression Honesty
// =============================================================================

/**
 * Transparency about what was compressed
 */
export interface CompressionHonesty {
  galois_loss: number;
  dropped_tags: string[];
  dropped_summaries: string[];
  preserved_ratio: number;
  warm_disclosure: string;
}

// =============================================================================
// API Request/Response Types
// =============================================================================

/**
 * POST /api/rap-coach/session/start
 */
export interface StartSessionRequest {
  /** Optional session name */
  name?: string;
}

export interface StartSessionResponse {
  session_id: string;
  started_at: string;
  warmth_message: string;  // "Let's flow. The mic is yours."
}

/**
 * POST /api/rap-coach/take/start
 */
export interface StartTakeRequest {
  session_id: string;
  intent: TakeIntent;
}

export interface StartTakeResponse {
  take_id: string;
  mark_id: string;
  timestamp: string;
  encouragement: string;  // Warmth response
}

/**
 * POST /api/rap-coach/take/end
 */
export interface EndTakeRequest {
  session_id: string;
  take_id: string;
  content_ref?: string;
  transcription?: string;
  ghosts?: GhostAlternative[];
}

export interface EndTakeResponse {
  take_id: string;
  duration_seconds: number;
  mark_id: string;
  joy_observation?: JoyObservation;
  warmth_response: string;
}

/**
 * POST /api/rap-coach/session/crystallize
 */
export interface CrystallizeRequest {
  session_id: string;
}

export interface CrystallizeResponse {
  crystal: VoiceCrystal;
  repair_paths: RepairPath[];
  success: boolean;
}

/**
 * GET /api/rap-coach/session/:session_id
 */
export interface GetSessionResponse {
  session: RapCoachSession;
  crystal?: VoiceCrystal;
}

// =============================================================================
// Contract Invariants
// =============================================================================

/**
 * Runtime invariant checks for TakeIntent
 */
export const TAKE_INTENT_INVARIANTS = {
  'has expression_goal': (i: TakeIntent) =>
    typeof i.expression_goal === 'string' && i.expression_goal.length > 0,
  'has valid register': (i: TakeIntent) =>
    ['aggressive', 'vulnerable', 'playful', 'introspective',
     'storytelling', 'technical', 'experimental'].includes(i.register),
  'has valid risk_level': (i: TakeIntent) =>
    ['low', 'medium', 'high'].includes(i.risk_level),
} as const;

/**
 * Runtime invariant checks for VoiceCrystal
 */
export const VOICE_CRYSTAL_INVARIANTS = {
  'has crystal_id': (c: VoiceCrystal) =>
    typeof c.crystal_id === 'string' && c.crystal_id.length > 0,
  'has voice_delta': (c: VoiceCrystal) =>
    typeof c.voice_delta === 'string' && c.voice_delta.length > 0,
  'has voice_throughline (L3)': (c: VoiceCrystal) =>
    typeof c.voice_throughline === 'string' && c.voice_throughline.length > 0,
  'has warmth_disclosure': (c: VoiceCrystal) =>
    typeof c.warmth_disclosure === 'string' && c.warmth_disclosure.length > 0,
  'galois_loss in range': (c: VoiceCrystal) =>
    typeof c.galois_loss === 'number' && c.galois_loss >= 0 && c.galois_loss <= 1,
} as const;

/**
 * Runtime invariant checks for CourageMoment (L4)
 */
export const COURAGE_MOMENT_INVARIANTS = {
  'has take_id': (m: CourageMoment) =>
    typeof m.take_id === 'string' && m.take_id.length > 0,
  'has courage_description': (m: CourageMoment) =>
    typeof m.courage_description === 'string' && m.courage_description.length > 0,
  'has risk_taken': (m: CourageMoment) =>
    typeof m.risk_taken === 'string' && m.risk_taken.length > 0,
} as const;

// =============================================================================
// Type Guards
// =============================================================================

export function isTakeIntent(data: unknown): data is TakeIntent {
  if (!data || typeof data !== 'object') return false;
  const i = data as Record<string, unknown>;
  return (
    typeof i.expression_goal === 'string' &&
    typeof i.register === 'string' &&
    typeof i.risk_level === 'string'
  );
}

export function isVoiceCrystal(data: unknown): data is VoiceCrystal {
  if (!data || typeof data !== 'object') return false;
  const c = data as Record<string, unknown>;
  return (
    typeof c.crystal_id === 'string' &&
    typeof c.voice_delta === 'string' &&
    typeof c.voice_throughline === 'string' &&
    typeof c.galois_loss === 'number'
  );
}

// =============================================================================
// Joy Constants for Rap Coach Domain
// =============================================================================

/**
 * Joy calibration for rap-coach pilot
 *
 * From 04-joy-integration.md:
 *   Primary: WARMTH (0.9) - the kind coach
 *   Secondary: FLOW (0.7) - creative momentum
 *   Tertiary: SURPRISE (0.3) - unexpected breakthroughs
 */
export const RAP_COACH_JOY_WEIGHTS = {
  warmth: 0.9,
  flow: 0.7,
  surprise: 0.3,
} as const;

/**
 * Galois target for rap-coach
 * L < 0.20 indicates flow state with courage preserved
 */
export const RAP_COACH_GALOIS_TARGET = 0.20;
