/**
 * TypeScript types for Agent Town API.
 * Generated from backend Pydantic models.
 */

// =============================================================================
// Subscription & Tiers
// =============================================================================

export type SubscriptionTier = 'TOURIST' | 'RESIDENT' | 'CITIZEN' | 'FOUNDER';

export type TownPhase = 'MORNING' | 'AFTERNOON' | 'EVENING' | 'NIGHT';

export type CitizenPhase = 'IDLE' | 'WORKING' | 'SOCIALIZING' | 'REFLECTING' | 'RESTING';

export type Archetype = 'Builder' | 'Trader' | 'Healer' | 'Scholar' | 'Watcher';

// =============================================================================
// Town
// =============================================================================

export interface Town {
  id: string;
  name: string;
  citizen_count: number;
  region_count: number;
  coalition_count: number;
  total_token_spend: number;
  status: 'active' | 'paused' | 'stopped';
}

export interface CreateTownRequest {
  name?: string;
  phase?: number;
  similarity_threshold?: number;
  enable_dialogue?: boolean;
}

export type TownResponse = Town;

// =============================================================================
// Citizen
// =============================================================================

export interface Eigenvectors {
  warmth: number;
  curiosity: number;
  trust: number;
  creativity: number;
  patience: number;
  resilience: number;
  ambition: number;
}

export interface CitizenSummary {
  id: string;
  name: string;
  archetype: Archetype;
  region: string;
  phase: CitizenPhase;
  is_evolving: boolean;
}

export interface CitizensResponse {
  citizens: CitizenSummary[];
  total: number;
  by_archetype: Record<string, number>;
  by_region: Record<string, number>;
}

export interface CitizenManifest {
  // LOD 0: Silhouette
  name: string;
  region: string;
  phase: string;
  nphase?: { current: string; cycle_count: number };

  // LOD 1: Posture
  archetype?: string;
  mood?: string;

  // LOD 2: Dialogue
  cosmotechnics?: string;
  metaphor?: string;

  // LOD 3: Memory
  eigenvectors?: Eigenvectors;
  relationships?: Record<string, number>;

  // LOD 4: Psyche
  accursed_surplus?: number;
  id?: string;

  // LOD 5: Abyss
  opacity?: {
    statement: string;
    message: string;
  };
}

export interface CitizenDetailResponse {
  lod: number;
  citizen: CitizenManifest;
  cost_credits: number;
}

// =============================================================================
// Events
// =============================================================================

export interface TownEvent {
  tick: number;
  phase: TownPhase;
  operation: string;
  participants: string[];
  success: boolean;
  message: string;
  tokens_used: number;
  timestamp: string;
  dialogue?: {
    text: string;
    tokens: number;
    model: string;
    was_template: boolean;
    grounded_memories: string[];
  };
}

// =============================================================================
// Coalition
// =============================================================================

export interface Coalition {
  id: string;
  name: string;
  members: string[];
  size: number;
  strength: number;
}

export interface CoalitionsResponse {
  coalitions: Coalition[];
  bridge_citizens: string[];
}

// =============================================================================
// Paywall
// =============================================================================

export interface UpgradeOption {
  type: 'subscription' | 'credits';
  tier?: SubscriptionTier;
  credits?: number;
  price_usd: number;
  unlocks: string;
}

export interface PaywallResult {
  allowed: boolean;
  reason?: string;
  cost_credits: number;
  uses_included: boolean;
  upgrade_options: UpgradeOption[];
}

// =============================================================================
// User & Budget
// =============================================================================

export interface UserBudget {
  user_id: string;
  subscription_tier: SubscriptionTier;
  credits: number;
  monthly_usage: Record<string, number>;
}

// =============================================================================
// INHABIT
// =============================================================================

export interface ConsentState {
  debt: number;
  status: string;
  at_rupture: boolean;
  can_force: boolean;
  cooldown: number;
}

export interface ForceState {
  enabled: boolean;
  used: number;
  remaining: number;
  limit: number;
}

export interface InhabitStatus {
  citizen: string;
  tier: string;
  duration: number;
  time_remaining: number;
  consent: ConsentState;
  force: ForceState;
  expired: boolean;
  actions_count: number;
}

export interface InhabitActionResult {
  success: boolean;
  action: string;
  message: string;
  debt?: number;
  forces_remaining?: number;
}

// =============================================================================
// Payments
// =============================================================================

export interface CheckoutSession {
  session_id: string;
  session_url: string;
  expires_at: string;
}

export interface CreditPack {
  name: string;
  credits: number;
  price_usd: number;
}

export const CREDIT_PACKS: CreditPack[] = [
  { name: 'Starter', credits: 500, price_usd: 4.99 },
  { name: 'Explorer', credits: 2500, price_usd: 19.99 },
  { name: 'Adventurer', credits: 10000, price_usd: 59.99 },
];

export const SUBSCRIPTION_TIERS = {
  TOURIST: { price: 0, lod: [0, 1], inhabit: false, branching: false },
  RESIDENT: { price: 9.99, lod: [0, 1, 2, 3], inhabit: 'basic', branching: false },
  CITIZEN: { price: 29.99, lod: [0, 1, 2, 3, 4], inhabit: 'full', branching: 3 },
  FOUNDER: { price: 99.99, lod: [0, 1, 2, 3, 4, 5], inhabit: 'unlimited', branching: 'unlimited' },
} as const;

// =============================================================================
// LOD Credit Costs (from unified-v2.md)
// =============================================================================

export const LOD_COSTS: Record<number, number> = {
  0: 0,
  1: 0,
  2: 0,
  3: 10,
  4: 100,
  5: 400,
};

export const LOD_INCLUDED_BY_TIER: Record<SubscriptionTier, number[]> = {
  TOURIST: [0, 1],
  RESIDENT: [0, 1, 2, 3],
  CITIZEN: [0, 1, 2, 3, 4],
  FOUNDER: [0, 1, 2, 3, 4, 5],
};

// =============================================================================
// Workshop
// =============================================================================

export type WorkshopPhase =
  | 'IDLE'
  | 'EXPLORING'
  | 'DESIGNING'
  | 'PROTOTYPING'
  | 'REFINING'
  | 'INTEGRATING'
  | 'COMPLETE';

export type BuilderArchetype = 'Scout' | 'Sage' | 'Spark' | 'Steady' | 'Sync';

export type BuilderPhase =
  | 'IDLE'
  | 'EXPLORING'
  | 'DESIGNING'
  | 'PROTOTYPING'
  | 'REFINING'
  | 'INTEGRATING';

export interface BuilderSummary {
  archetype: BuilderArchetype;
  name: string;
  phase: BuilderPhase;
  is_active: boolean;
  is_in_specialty: boolean;
}

export interface WorkshopTask {
  id: string;
  description: string;
  priority: number;
  created_at: string;
}

export interface WorkshopArtifact {
  id: string;
  task_id: string;
  builder: string;
  phase: WorkshopPhase;
  content: unknown;
  created_at: string;
}

export interface WorkshopMetrics {
  total_steps: number;
  total_events: number;
  total_tokens: number;
  dialogue_tokens: number;
  artifacts_produced: number;
  phases_completed: number;
  handoffs: number;
  perturbations: number;
  duration_seconds: number;
}

export interface WorkshopPlan {
  task: WorkshopTask;
  assignments: Record<string, string[]>;
  estimated_phases: WorkshopPhase[];
  lead_builder: string;
}

export interface WorkshopStatus {
  id: string;
  phase: WorkshopPhase;
  active_task: WorkshopTask | null;
  builders: BuilderSummary[];
  artifacts: WorkshopArtifact[];
  metrics: WorkshopMetrics;
  is_running: boolean;
}

export type WorkshopEventType =
  | 'TASK_ASSIGNED'
  | 'PLAN_CREATED'
  | 'PHASE_STARTED'
  | 'PHASE_COMPLETED'
  | 'HANDOFF'
  | 'ARTIFACT_PRODUCED'
  | 'USER_QUERY'
  | 'USER_RESPONSE'
  | 'TASK_COMPLETED'
  | 'ERROR';

export interface WorkshopEvent {
  type: WorkshopEventType;
  builder: string | null;
  phase: WorkshopPhase;
  message: string;
  artifact: unknown | null;
  timestamp: string;
  metadata: {
    dialogue?: string;
    perturbation?: boolean;
    [key: string]: unknown;
  };
}

// Builder visual config
export const BUILDER_COLORS: Record<BuilderArchetype, string> = {
  Scout: '#22c55e',  // green
  Sage: '#8b5cf6',   // purple
  Spark: '#f59e0b',  // amber
  Steady: '#3b82f6', // blue
  Sync: '#ec4899',   // pink
};

export const BUILDER_ICONS: Record<BuilderArchetype, string> = {
  Scout: '🔍',
  Sage: '📐',
  Spark: '⚡',
  Steady: '🔧',
  Sync: '🔗',
};

// =============================================================================
// Workshop History & Metrics (Chunk 9)
// =============================================================================

export interface TaskHistoryItem {
  id: string;
  description: string;
  status: 'completed' | 'interrupted';
  lead_builder: string;
  builder_sequence: string[];
  artifacts_count: number;
  tokens_used: number;
  handoffs: number;
  duration_seconds: number;
  created_at: string;
  completed_at: string | null;
}

export interface TaskHistoryResponse {
  tasks: TaskHistoryItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface BuilderContribution {
  archetype: string;
  phases_worked: string[];
  artifacts_produced: number;
  tokens_used: number;
  duration_seconds: number;
}

export interface TaskDetailResponse {
  task: TaskHistoryItem;
  artifacts: WorkshopArtifact[];
  events: WorkshopEvent[];
  builder_contributions: Record<string, BuilderContribution>;
}

export interface DayMetric {
  date: string;
  value: number;
}

export interface AggregateMetrics {
  period: string;
  total_tasks: number;
  completed_tasks: number;
  interrupted_tasks: number;
  total_artifacts: number;
  total_tokens: number;
  total_handoffs: number;
  avg_duration_seconds: number;
  tasks_by_day: DayMetric[];
  artifacts_by_day: DayMetric[];
  tokens_by_day: DayMetric[];
}

export interface BuilderPerformanceMetrics {
  archetype: string;
  period: string;
  tasks_participated: number;
  tasks_led: number;
  artifacts_produced: number;
  tokens_used: number;
  avg_duration_seconds: number;
  specialty_efficiency: number;
  handoffs_initiated: number;
  handoffs_received: number;
}

export interface HandoffFlow {
  from_builder: string;
  to_builder: string;
  count: number;
}

export interface FlowMetrics {
  flows: HandoffFlow[];
  total_handoffs: number;
}

// Replay state
export interface ReplayState {
  taskId: string;
  events: WorkshopEvent[];
  currentIndex: number;
  isPlaying: boolean;
  playbackSpeed: number;
  duration: number;
  elapsed: number;
}

// =============================================================================
// N-Phase (Wave 5)
// =============================================================================

/**
 * N-Phase development cycle: UNDERSTAND → ACT → REFLECT
 */
export type NPhaseType = 'UNDERSTAND' | 'ACT' | 'REFLECT';

/**
 * N-Phase context embedded in SSE events.
 * Maps to backend NPhaseSession state.
 */
export interface NPhaseContext {
  session_id: string;
  current_phase: NPhaseType;
  cycle_count: number;
  checkpoint_count: number;
  handle_count: number;
}

/**
 * N-Phase transition event from live.nphase SSE.
 */
export interface NPhaseTransitionEvent {
  tick: number;
  from_phase: NPhaseType;
  to_phase: NPhaseType;
  session_id: string;
  cycle_count: number;
  trigger: string;
  timestamp?: Date;
}

/**
 * N-Phase summary in live.end event.
 */
export interface NPhaseSummary extends NPhaseContext {
  final_phase: NPhaseType;
  ledger_entries: number;
}

/**
 * Extended live.start event with N-Phase.
 */
export interface LiveStartEvent {
  town_id: string;
  phases: number;
  speed: number;
  nphase_enabled: boolean;
  nphase?: NPhaseContext;
}

/**
 * Extended live.end event with N-Phase.
 */
export interface LiveEndEvent {
  town_id: string;
  total_ticks: number;
  status: string;
  nphase_summary?: NPhaseSummary;
}

/**
 * N-Phase state for React components.
 */
export interface NPhaseState {
  enabled: boolean;
  sessionId: string | null;
  currentPhase: NPhaseType;
  cycleCount: number;
  checkpointCount: number;
  handleCount: number;
  transitions: NPhaseTransitionEvent[];
  isActive: boolean;
}

/**
 * N-Phase visual configuration.
 */
export const NPHASE_CONFIG = {
  colors: {
    UNDERSTAND: '#3b82f6', // blue - gathering info
    ACT: '#f59e0b',        // amber - executing
    REFLECT: '#8b5cf6',    // purple - reviewing
  },
  icons: {
    UNDERSTAND: '🔍',
    ACT: '⚡',
    REFLECT: '💭',
  },
  descriptions: {
    UNDERSTAND: 'Gathering context and analyzing the situation',
    ACT: 'Executing actions and making changes',
    REFLECT: 'Reviewing outcomes and learning',
  },
  // Town phase → N-Phase mapping
  townPhaseMapping: {
    MORNING: 'UNDERSTAND',
    AFTERNOON: 'UNDERSTAND',
    EVENING: 'ACT',
    NIGHT: 'REFLECT',
  } as Record<TownPhase, NPhaseType>,
} as const;

// =============================================================================
// Projection Gallery
// =============================================================================

/**
 * Gallery pilot categories.
 */
export type GalleryCategory =
  | 'PRIMITIVES'
  | 'CARDS'
  | 'CHROME'
  | 'STREAMING'
  | 'COMPOSITION'
  | 'ADAPTERS'
  | 'SPECIALIZED';

/**
 * Projections for a single pilot across targets.
 */
export interface PilotProjections {
  cli: string;
  html: string;
  json: Record<string, unknown>;
}

/**
 * Single pilot response from the gallery API.
 */
export interface PilotResponse {
  name: string;
  category: GalleryCategory;
  description: string;
  tags: string[];
  projections: PilotProjections;
}

/**
 * Full gallery response with all pilots.
 */
export interface GalleryResponse {
  pilots: PilotResponse[];
  categories: GalleryCategory[];
  total: number;
}

/**
 * Category metadata.
 */
export interface GalleryCategoryInfo {
  name: GalleryCategory;
  pilot_count: number;
  pilots: string[];
}

/**
 * Gallery override parameters.
 */
export interface GalleryOverrides {
  entropy?: number;
  seed?: number;
  phase?: string;
  time_ms?: number;
}

/**
 * Gallery category visual config.
 */
export const GALLERY_CATEGORY_CONFIG: Record<GalleryCategory, { icon: string; color: string }> = {
  PRIMITIVES: { icon: '○', color: '#22c55e' },
  CARDS: { icon: '▦', color: '#3b82f6' },
  CHROME: { icon: '◻', color: '#f59e0b' },
  STREAMING: { icon: '▸', color: '#8b5cf6' },
  COMPOSITION: { icon: '⊞', color: '#ec4899' },
  ADAPTERS: { icon: '⇄', color: '#06b6d4' },
  SPECIALIZED: { icon: '◈', color: '#ef4444' },
};
