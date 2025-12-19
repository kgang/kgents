/**
 * TypeScript types for Agent Town API.
 *
 * PHASE 7.5: Contract Type Migration (autopoietic-architecture.md)
 *
 * This file contains two categories of types:
 * 1. GENERATED TYPES (re-exported from _generated/) - Contract types from AGENTESE
 * 2. LOCAL TYPES - FE-only types, constants, and UI configurations
 *
 * Migration Guide:
 * - Contract types (responses from /agentese/* endpoints) use generated types
 * - Local types (UI state, constants, configs) stay in this file
 * - New AGENTESE contracts should be added to services/<name>/contracts.py
 *   then run `npm run sync-types` to regenerate
 *
 * @see plans/autopoietic-architecture.md - Phase 7: AGENTESE Contract Protocol
 */

// =============================================================================
// Generated Contract Types (from _generated/)
// Run `npm run sync-types` to regenerate from backend contracts
// =============================================================================

// Export all generated types directly from their source files
export * from './types/_generated/world-town';
export * from './types/_generated/self-memory';
export * from './types/_generated/self-chat';
export * from './types/_generated/world-forge';
export * from './types/_generated/world-codebase';
export * from './types/_generated/world-park';

// Type aliases for backwards compatibility during migration
// These map legacy names to the new generated types
export type {
  WorldTownManifestResponse as TownManifestContract,
  WorldTownCitizenListResponse as TownCitizenListContract,
  WorldTownCitizenGetResponse as TownCitizenGetContract,
} from './types/_generated/world-town';

export type {
  SelfMemoryManifestResponse as BrainManifestContract,
  SelfMemoryTopologyResponse as BrainTopologyContract,
  SelfMemoryCaptureRequest as BrainCaptureRequestContract,
  SelfMemoryCaptureResponse as BrainCaptureResponseContract,
  SelfMemorySearchRequest as BrainSearchRequestContract,
  SelfMemorySearchResponse as BrainSearchResponseContract,
} from './types/_generated/self-memory';

export type {
  SelfChatManifestResponse as ChatManifestContract,
  SelfChatSessionsResponse as ChatSessionsContract,
  SelfChatSendRequest as ChatSendRequestContract,
  SelfChatSendResponse as ChatSendResponseContract,
} from './types/_generated/self-chat';

export type {
  WorldCodebaseManifestResponse as GestaltManifestContract,
  WorldCodebaseTopologyResponse as GestaltTopologyContract,
  WorldCodebaseHealthResponse as GestaltHealthContract,
  WorldCodebaseModuleResponse as GestaltModuleContract,
} from './types/_generated/world-codebase';

export type {
  WorldForgeManifestResponse as ForgeManifestContract,
  WorldForgeWorkshopListResponse as ForgeWorkshopListContract,
} from './types/_generated/world-forge';

export type {
  WorldParkManifestResponse as ParkManifestContract,
  WorldParkHostListResponse as ParkHostListContract,
  WorldParkEpisodeListResponse as ParkEpisodeListContract,
} from './types/_generated/world-park';

export type {
  ConceptGardenerManifestResponse as GardenerManifestContract,
  ConceptGardenerSessionManifestResponse as GardenerSessionContract,
  ConceptGardenerSessionDefineRequest as GardenerDefineRequestContract,
  ConceptGardenerSessionDefineResponse as GardenerDefineResponseContract,
  ConceptGardenerSessionAdvanceRequest as GardenerAdvanceRequestContract,
  ConceptGardenerSessionAdvanceResponse as GardenerAdvanceResponseContract,
  ConceptGardenerPolynomialResponse as GardenerPolynomialContract,
  ConceptGardenerSessionsListResponse as GardenerSessionsListContract,
} from './types/_generated/concept-gardener';

// =============================================================================
// Local Types (FE-only)
// =============================================================================

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
// Dialogue (Phase 5: Town End-to-End)
// =============================================================================

/**
 * Summary of a conversation turn.
 */
export interface TurnSummary {
  id: string;
  turn_number: number;
  role: 'user' | 'citizen';
  content: string;
  sentiment: string | null;
  emotion: string | null;
  created_at: string;
}

/**
 * Full conversation details with turns.
 */
export interface ConversationDetail {
  id: string;
  citizen_id: string;
  citizen_name: string;
  topic: string | null;
  summary: string | null;
  turn_count: number;
  is_active: boolean;
  created_at: string;
  turns: TurnSummary[];
}

/**
 * Summary of a conversation for history views.
 */
export interface ConversationSummary {
  id: string;
  topic: string | null;
  summary: string | null;
  turn_count: number;
  is_active: boolean;
  created_at: string;
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
  Scout: '#22c55e', // green
  Sage: '#8b5cf6', // purple
  Spark: '#f59e0b', // amber
  Steady: '#3b82f6', // blue
  Sync: '#ec4899', // pink
};

/**
 * @deprecated Use BUILDER_ICONS_LUCIDE from '@/constants' instead.
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 */
export const BUILDER_ICONS: Record<BuilderArchetype, string> = {
  Scout: 'compass',
  Sage: 'graduation-cap',
  Spark: 'zap',
  Steady: 'hammer',
  Sync: 'link',
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
 *
 * NOTE: For icons, import PHASE_ICONS from '@/constants' instead of using emoji strings.
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 */
export const NPHASE_CONFIG = {
  colors: {
    UNDERSTAND: '#3b82f6', // blue - gathering info
    ACT: '#f59e0b', // amber - executing
    REFLECT: '#8b5cf6', // purple - reviewing
  },
  /**
   * @deprecated Use PHASE_ICONS from '@/constants' instead.
   * Kept for backward compatibility - values are now Lucide icon names.
   */
  icons: {
    UNDERSTAND: 'eye',
    ACT: 'zap',
    REFLECT: 'message-circle',
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
  | 'SPECIALIZED'
  // Gallery V2 categories (AD-009 Vertical Slice)
  | 'POLYNOMIAL'
  | 'OPERAD'
  | 'CROWN_JEWELS'
  | 'LAYOUT'
  | 'INTERACTIVE'; // Flagship interactive pilots

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
  // Gallery V2 categories (AD-009 Vertical Slice)
  POLYNOMIAL: { icon: '◉', color: '#14b8a6' }, // teal - state machines
  OPERAD: { icon: '⊛', color: '#a855f7' }, // purple - composition grammar
  CROWN_JEWELS: { icon: '♦', color: '#eab308' }, // yellow - vertical slices
  LAYOUT: { icon: '▣', color: '#64748b' }, // slate - design system
  INTERACTIVE: { icon: '⚡', color: '#10b981' }, // emerald - flagship interactive
};

// =============================================================================
// Brain (Holographic Brain)
// =============================================================================

/**
 * Request to capture content to holographic memory.
 */
export interface BrainCaptureRequest {
  content: string;
  concept_id?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Response from brain capture operation.
 */
export interface BrainCaptureResponse {
  status: string;
  concept_id: string;
  storage: string;
}

/**
 * Request to surface ghost memories.
 */
export interface BrainGhostRequest {
  context: string;
  limit?: number;
}

/**
 * A surfaced ghost memory.
 */
export interface GhostMemory {
  concept_id: string;
  content: string | null;
  relevance: number;
}

/**
 * Response from ghost surfacing.
 */
export interface BrainGhostResponse {
  status: string;
  context: string;
  surfaced: GhostMemory[];
  count: number;
}

/**
 * Brain map/topology response.
 */
export interface BrainMapResponse {
  summary: string;
  concept_count: number;
  landmarks: number;
  hot_patterns: number;
  dimension: number;
}

/**
 * Brain status response.
 */
export interface BrainStatusResponse {
  status: 'healthy' | 'degraded' | 'unavailable';
  embedder_type: string;
  embedder_dimension: number;
  concept_count: number;
  has_cartographer: boolean;
}

// =============================================================================
// Brain Topology (3D Visualization)
// =============================================================================

/**
 * A crystal node in the 3D topology.
 */
export interface TopologyNode {
  id: string;
  label: string;
  x: number;
  y: number;
  z: number;
  resolution: number; // 0.01-1.0, maps to opacity
  is_hot: boolean;
  access_count: number;
  age_seconds: number;
  content_preview: string | null;
}

/**
 * An edge between similar crystals.
 */
export interface TopologyEdge {
  source: string;
  target: string;
  similarity: number;
}

/**
 * A detected gap (sparse region) in knowledge.
 */
export interface TopologyGap {
  x: number;
  y: number;
  z: number;
  radius: number;
  nearest_concepts: string[];
}

/**
 * Full topology response for 3D visualization.
 */
export interface BrainTopologyResponse {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  gaps: TopologyGap[];
  hub_ids: string[];
  stats: {
    concept_count: number;
    edge_count: number;
    hub_count: number;
    gap_count: number;
    avg_resolution: number;
  };
}

// =============================================================================
// Gestalt (Living Architecture Visualizer)
// =============================================================================

/**
 * A module node in the architecture graph.
 */
export interface CodebaseModule {
  id: string;
  label: string;
  layer: string | null;
  health_grade: string;
  health_score: number;
  lines_of_code: number;
  coupling: number;
  cohesion: number;
  instability: number | null;
  x: number;
  y: number;
  z: number;
}

/**
 * A dependency link between modules.
 */
export interface DependencyLink {
  source: string;
  target: string;
  import_type: string;
  is_violation: boolean;
  violation_severity: string | null;
}

/**
 * Graph topology response for visualization.
 */
export interface CodebaseTopologyResponse {
  nodes: CodebaseModule[];
  links: DependencyLink[];
  layers: string[];
  stats: {
    node_count: number;
    link_count: number;
    layer_count: number;
    violation_count: number;
    avg_health: number;
    overall_grade: string;
  };
  /** Sprint 2: Applied umwelt configuration */
  umwelt?: {
    role: string;
    config: Record<string, number | boolean | string[]>;
    emphasized_layers: string[];
  };
}

/**
 * Architecture manifest response.
 */
export interface CodebaseManifestResponse {
  module_count: number;
  edge_count: number;
  language: string;
  average_health: number;
  overall_grade: string;
  drift_count: number;
  modules: Array<{
    name: string;
    lines_of_code: number;
    layer: string | null;
    health_grade: string;
    health_score: number;
  }>;
}

/**
 * Health metrics response.
 */
export interface CodebaseHealthResponse {
  average_health: number;
  overall_grade: string;
  grade_distribution: Record<string, number>;
  worst_modules: Array<{
    name: string;
    grade: string;
    coupling: number;
    cohesion: number;
    drift: number;
    complexity: number;
  }>;
  best_modules: Array<{
    name: string;
    grade: string;
  }>;
}

/**
 * Drift violations response.
 */
export interface CodebaseDriftResponse {
  total_violations: number;
  unsuppressed: number;
  suppressed: number;
  violations: Array<{
    rule: string;
    source: string;
    target: string;
    severity: string;
    suppressed: boolean;
    line: number;
  }>;
}

/**
 * Module details response.
 */
export interface CodebaseModuleResponse {
  name: string;
  path: string | null;
  lines_of_code: number;
  layer: string | null;
  exports: string[];
  health: {
    grade: string;
    score: number;
    coupling: number;
    cohesion: number;
    drift: number;
    complexity: number;
    instability: number | null;
  } | null;
  dependencies: string[];
  dependents: string[];
  violations: Array<{
    rule: string;
    target: string;
  }>;
}

/**
 * Scan response.
 */
export interface CodebaseScanResponse {
  status: string;
  module_count: number;
  edge_count: number;
  overall_grade: string;
}

/**
 * SSE topology update (Sprint 1: Live Architecture).
 *
 * Update kinds:
 * - full: Complete topology replacement
 * - ping: Keepalive (no change detected)
 * - error: Error message
 */
export interface CodebaseTopologyUpdate {
  kind: 'full' | 'ping' | 'error' | 'add' | 'remove' | 'update';
  topology?: CodebaseTopologyResponse;
  node?: CodebaseModule;
  link?: DependencyLink;
  error?: string;
  timestamp: string;
}

/**
 * Connection status for SSE stream.
 */
export type GestaltStreamStatus =
  | 'disconnected'
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'error';

/**
 * Health grade visual config.
 */
export const HEALTH_GRADE_CONFIG: Record<string, { color: string; bgColor: string }> = {
  'A+': { color: '#22c55e', bgColor: 'bg-green-500/20' },
  A: { color: '#4ade80', bgColor: 'bg-green-400/20' },
  'B+': { color: '#a3e635', bgColor: 'bg-lime-400/20' },
  B: { color: '#facc15', bgColor: 'bg-yellow-400/20' },
  'C+': { color: '#fb923c', bgColor: 'bg-orange-400/20' },
  C: { color: '#f97316', bgColor: 'bg-orange-500/20' },
  D: { color: '#ef4444', bgColor: 'bg-red-500/20' },
  F: { color: '#dc2626', bgColor: 'bg-red-600/20' },
  '?': { color: '#6b7280', bgColor: 'bg-gray-500/20' },
};

// =============================================================================
// Polynomial Visualization (Foundation 3: Visible Polynomial State)
// =============================================================================

/**
 * A position (state) in a polynomial agent's state machine.
 */
export interface PolynomialPosition {
  id: string;
  label: string;
  description?: string;
  /** @deprecated Use `icon` instead. Per visual-system.md, kgents uses Lucide icons. */
  emoji?: string;
  /** Lucide icon name (lowercase, hyphenated). Use with icon constants from '@/constants/icons'. */
  icon?: string;
  is_current: boolean;
  is_terminal: boolean;
  color?: string;
}

/**
 * A valid transition edge between positions.
 */
export interface PolynomialEdge {
  source: string;
  target: string;
  label?: string;
  is_valid: boolean;
}

/**
 * A historical transition in the polynomial's execution.
 */
export interface PolynomialHistoryEntry {
  from_position: string;
  to_position: string;
  input_summary?: string;
  output_summary?: string;
  timestamp?: string;
}

/**
 * Complete visualization data for a polynomial agent's state machine.
 *
 * This enables Foundation 3 (Visible Polynomial State) by providing
 * all data needed to render a state machine diagram.
 */
export interface PolynomialVisualization {
  id: string;
  name: string;
  positions: PolynomialPosition[];
  edges: PolynomialEdge[];
  current?: string;
  valid_directions: string[];
  history: PolynomialHistoryEntry[];
  metadata: Record<string, unknown>;
}

/**
 * API response wrapper for polynomial visualization.
 */
export interface PolynomialVisualizationResponse {
  visualization: PolynomialVisualization;
  agentese_path?: string;
}

/**
 * Configuration for polynomial visualization styling.
 *
 * NOTE: For icons, import from '@/constants' (GARDENER_PHASE_ICONS, PHASE_ICONS, CITIZEN_PHASE_ICONS).
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 * The 'icon' field contains Lucide icon names (lowercase, hyphenated).
 */
export const POLYNOMIAL_CONFIG = {
  // Default colors for positions
  colors: {
    default: '#3b82f6', // blue
    current: '#22c55e', // green
    terminal: '#ef4444', // red
    available: '#f59e0b', // amber
  },
  // Gardener session phases
  gardener: {
    SENSE: { color: '#3b82f6', icon: 'eye', label: 'Sense' },
    ACT: { color: '#f59e0b', icon: 'zap', label: 'Act' },
    REFLECT: { color: '#8b5cf6', icon: 'message-circle', label: 'Reflect' },
  },
  // N-Phase development phases
  nphase: {
    PLAN: { color: '#94a3b8', icon: 'clipboard-list', label: 'Plan' },
    RESEARCH: { color: '#3b82f6', icon: 'search', label: 'Research' },
    DEVELOP: { color: '#22c55e', icon: 'wrench', label: 'Develop' },
    STRATEGIZE: { color: '#8b5cf6', icon: 'target', label: 'Strategize' },
    'CROSS-SYNERGIZE': { color: '#ec4899', icon: 'link', label: 'Cross-Synergize' },
    IMPLEMENT: { color: '#f59e0b', icon: 'cog', label: 'Implement' },
    QA: { color: '#06b6d4', icon: 'microscope', label: 'QA' },
    TEST: { color: '#10b981', icon: 'test-tube', label: 'Test' },
    EDUCATE: { color: '#a855f7', icon: 'graduation-cap', label: 'Educate' },
    MEASURE: { color: '#f97316', icon: 'bar-chart-3', label: 'Measure' },
    REFLECT: { color: '#6366f1', icon: 'book-open', label: 'Reflect' },
  },
  // Citizen polynomial phases
  citizen: {
    IDLE: { color: '#94a3b8', icon: 'circle-dot', label: 'Idle' },
    SOCIALIZING: { color: '#ec4899', icon: 'message-circle', label: 'Socializing' },
    WORKING: { color: '#f59e0b', icon: 'wrench', label: 'Working' },
    REFLECTING: { color: '#8b5cf6', icon: 'book-open', label: 'Reflecting' },
    RESTING: { color: '#22c55e', icon: 'cloud', label: 'Resting' },
  },
} as const;

/**
 * Session phase type for Gardener.
 */
export type GardenerPhase = 'SENSE' | 'ACT' | 'REFLECT';

/**
 * GardenerSession state for visualization.
 */
export interface GardenerSessionState {
  session_id: string;
  name: string;
  phase: GardenerPhase;
  plan_path?: string;
  intent?: {
    description: string;
    priority: string;
  };
  artifacts_count: number;
  learnings_count: number;
  sense_count: number;
  act_count: number;
  reflect_count: number;
}

// =============================================================================
// Infrastructure (Gestalt Live)
// =============================================================================

/**
 * Infrastructure entity kinds.
 */
export type InfraEntityKind =
  | 'namespace'
  | 'node'
  | 'pod'
  | 'service'
  | 'deployment'
  | 'container'
  | 'nats_subject'
  | 'nats_stream'
  | 'database'
  | 'volume'
  | 'custom';

/**
 * Infrastructure entity status.
 */
export type InfraEntityStatus =
  | 'running'
  | 'pending'
  | 'succeeded'
  | 'failed'
  | 'terminating'
  | 'unknown';

/**
 * Infrastructure connection kinds.
 */
export type InfraConnectionKind =
  | 'network'
  | 'http'
  | 'grpc'
  | 'nats'
  | 'volume'
  | 'owns'
  | 'selects'
  | 'depends';

/**
 * Infrastructure entity for visualization.
 */
export interface InfraEntity {
  id: string;
  kind: InfraEntityKind;
  name: string;
  namespace: string | null;
  status: InfraEntityStatus;
  status_message: string | null;
  health: number;
  health_grade: string;
  cpu_percent: number;
  memory_bytes: number;
  memory_limit: number | null;
  memory_percent: number | null;
  custom_metrics: Record<string, number>;
  x: number;
  y: number;
  z: number;
  labels: Record<string, string>;
  source: string;
  created_at: string | null;
}

/**
 * Infrastructure connection between entities.
 */
export interface InfraConnection {
  id: string;
  source_id: string;
  target_id: string;
  kind: InfraConnectionKind;
  requests_per_sec: number;
  bytes_per_sec: number;
  error_rate: number;
  is_healthy: boolean;
}

/**
 * Infrastructure topology snapshot.
 */
export interface InfraTopologyResponse {
  entities: InfraEntity[];
  connections: InfraConnection[];
  timestamp: string;
  total_entities: number;
  healthy_count: number;
  warning_count: number;
  critical_count: number;
  overall_health: number;
  entities_by_kind: Record<string, number>;
  entities_by_namespace: Record<string, number>;
}

/**
 * Infrastructure health summary.
 */
export interface InfraHealthResponse {
  overall: number;
  overall_grade: string;
  healthy: number;
  warning: number;
  critical: number;
  total: number;
  by_kind: Record<string, { count: number; average_health: number }>;
  by_namespace: Record<string, { count: number; average_health: number }>;
  worst_entities: Array<{
    id: string;
    name: string;
    kind: string;
    health: number;
    status: string;
  }>;
}

/**
 * Infrastructure event.
 */
export interface InfraEvent {
  id: string;
  type: string;
  reason: string;
  message: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  entity_id: string;
  entity_kind: InfraEntityKind;
  entity_name: string;
  entity_namespace: string | null;
  timestamp: string;
  count: number;
}

/**
 * Infrastructure collector status.
 */
export interface InfraStatusResponse {
  connected: boolean;
  collector_type: string;
  health_check: boolean;
}

// =============================================================================
// Topology Streaming (Phase 2)
// =============================================================================

/**
 * Types of topology updates from SSE stream.
 */
export type TopologyUpdateKind =
  | 'full'
  | 'entity_added'
  | 'entity_updated'
  | 'entity_removed'
  | 'connection_added'
  | 'connection_updated'
  | 'connection_removed'
  | 'metrics';

/**
 * Incremental topology update from SSE stream.
 */
export interface TopologyUpdate {
  kind: TopologyUpdateKind;
  timestamp: string;
  entity?: InfraEntity;
  connection?: InfraConnection;
  topology?: InfraTopologyResponse;
  metrics?: Record<string, Record<string, number>>;
}

/**
 * Connection status for SSE streams.
 */
export type StreamConnectionStatus =
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'disconnected'
  | 'error';

/**
 * Entity animation state for smooth transitions.
 */
export interface EntityAnimationState {
  opacity: number; // 0-1, for fade in/out
  scale: number; // base scale multiplier
  pulseIntensity: number; // 0-1, for update flash
  isNew: boolean; // just added (fade in)
  isRemoving: boolean; // marked for removal (fade out)
  lastUpdated: number; // timestamp for pulse decay
}

/**
 * Entity kind visual config.
 *
 * NOTE: For icons, import INFRA_ENTITY_ICONS from '@/constants'.
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 */
export const INFRA_ENTITY_CONFIG: Record<
  InfraEntityKind,
  {
    icon: string;
    color: string;
    shape: 'sphere' | 'octahedron' | 'dodecahedron' | 'box' | 'cone' | 'cylinder' | 'torus';
  }
> = {
  namespace: { icon: 'box', color: '#6366f1', shape: 'torus' },
  node: { icon: 'monitor', color: '#8b5cf6', shape: 'box' },
  pod: { icon: 'server', color: '#22c55e', shape: 'sphere' },
  service: { icon: 'link', color: '#3b82f6', shape: 'octahedron' },
  deployment: { icon: 'play', color: '#f59e0b', shape: 'dodecahedron' },
  container: { icon: 'box', color: '#06b6d4', shape: 'box' },
  nats_subject: { icon: 'mail', color: '#a855f7', shape: 'cone' },
  nats_stream: { icon: 'wind', color: '#ec4899', shape: 'cylinder' },
  database: { icon: 'database', color: '#ef4444', shape: 'cylinder' },
  volume: { icon: 'hard-drive', color: '#f97316', shape: 'box' },
  custom: { icon: 'cog', color: '#6b7280', shape: 'sphere' },
};

/**
 * Event severity visual config.
 *
 * NOTE: For icons, import SEVERITY_ICONS from '@/constants'.
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 */
export const INFRA_SEVERITY_CONFIG: Record<
  InfraEvent['severity'],
  { icon: string; color: string }
> = {
  info: { icon: 'info', color: '#3b82f6' },
  warning: { icon: 'alert-triangle', color: '#f59e0b' },
  error: { icon: 'x-circle', color: '#ef4444' },
  critical: { icon: 'alert-triangle', color: '#dc2626' },
};

// =============================================================================
// Park (Punchdrunk Park - Wave 3)
// =============================================================================

/**
 * Crisis phases for polynomial state machine.
 */
export type ParkCrisisPhase = 'NORMAL' | 'INCIDENT' | 'RESPONSE' | 'RECOVERY';

/**
 * Timer status values.
 */
export type ParkTimerStatus =
  | 'PENDING'
  | 'ACTIVE'
  | 'WARNING'
  | 'CRITICAL'
  | 'EXPIRED'
  | 'COMPLETED'
  | 'PAUSED';

/**
 * Mask archetype categories.
 */
export type ParkMaskArchetype =
  | 'TRICKSTER'
  | 'DREAMER'
  | 'SKEPTIC'
  | 'ARCHITECT'
  | 'CHILD'
  | 'SAGE'
  | 'WARRIOR'
  | 'HEALER';

/**
 * Integrated scenario types.
 */
export type ParkScenarioType =
  | 'MYSTERY'
  | 'COLLABORATION'
  | 'CONFLICT'
  | 'EMERGENCE'
  | 'CRISIS_PRACTICE'
  | 'COMPLIANCE_DRILL'
  | 'TABLETOP'
  | 'INCIDENT_RESPONSE';

/**
 * Timer state information.
 */
export interface ParkTimerInfo {
  name: string;
  countdown: string;
  status: ParkTimerStatus;
  progress: number;
  remaining_seconds: number;
}

/**
 * Eigenvector transform deltas.
 */
export interface ParkEigenvectorTransform {
  creativity: number;
  trust: number;
  empathy: number;
  authority: number;
  playfulness: number;
  wisdom: number;
  directness: number;
  warmth: number;
}

/**
 * Dialogue mask information.
 */
export interface ParkMaskInfo {
  name: string;
  archetype: ParkMaskArchetype;
  description: string;
  flavor_text: string | null;
  intensity: number;
  transform: ParkEigenvectorTransform;
  special_abilities: string[];
  restrictions: string[];
}

/**
 * Eigenvector state with optional mask transform.
 */
export interface ParkEigenvectorState {
  base: Record<string, number>;
  transformed: Record<string, number>;
  mask_applied: string | null;
}

/**
 * Full scenario state.
 */
export interface ParkScenarioState {
  scenario_id: string;
  name: string;
  scenario_type: ParkScenarioType;
  is_active: boolean;

  // Timers
  timers: ParkTimerInfo[];
  any_timer_critical: boolean;
  any_timer_expired: boolean;

  // Crisis phase
  crisis_phase: ParkCrisisPhase;
  available_transitions: ParkCrisisPhase[];
  phase_transitions: Array<{
    timestamp: string;
    from: ParkCrisisPhase;
    to: ParkCrisisPhase;
    consent_debt: number;
    forces_used: number;
  }>;

  // Consent mechanics
  consent_debt: number;
  forces_used: number;
  forces_remaining: number;

  // Mask state
  mask: ParkMaskInfo | null;
  eigenvectors: ParkEigenvectorState | null;

  // Timing
  started_at: string | null;
  accelerated: boolean;
}

/**
 * Request to start a new scenario.
 */
export interface ParkStartScenarioRequest {
  template?: 'data-breach' | 'service-outage';
  timer_type?: 'gdpr' | 'sec' | 'hipaa' | 'sla' | 'custom';
  accelerated?: boolean;
  mask_name?: string;
}

/**
 * Request to tick timers.
 */
export interface ParkTickRequest {
  count?: number;
}

/**
 * Request to transition crisis phase.
 */
export interface ParkTransitionPhaseRequest {
  phase: 'normal' | 'incident' | 'response' | 'recovery';
}

/**
 * Request for mask action.
 */
export interface ParkMaskActionRequest {
  action: 'don' | 'doff';
  mask_name?: string;
}

/**
 * Request to complete scenario.
 */
export interface ParkCompleteRequest {
  outcome?: 'success' | 'failure' | 'abandon';
}

/**
 * Scenario completion summary.
 */
export interface ParkScenarioSummary {
  scenario_id: string;
  name: string;
  scenario_type: ParkScenarioType;
  outcome: string;
  duration_seconds: number;
  consent_debt_final: number;
  forces_used: number;
  timer_outcomes: Record<
    string,
    {
      status: ParkTimerStatus;
      elapsed_seconds: number;
      expired: boolean;
    }
  >;
  phase_transitions: Array<{
    timestamp: string;
    from: ParkCrisisPhase;
    to: ParkCrisisPhase;
    consent_debt: number;
    forces_used: number;
  }>;
  injections_count: number;
}

/**
 * Park system status.
 */
export interface ParkStatusResponse {
  running: boolean;
  scenario_id: string | null;
  scenario_name: string | null;
  masks_available: number;
}

/**
 * Crisis phase visual config.
 *
 * NOTE: For icons, import CRISIS_PHASE_ICONS from '@/constants'.
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 */
export const PARK_PHASE_CONFIG: Record<
  ParkCrisisPhase,
  { color: string; icon: string; label: string }
> = {
  NORMAL: { color: '#22c55e', icon: 'check-circle', label: 'Normal' },
  INCIDENT: { color: '#f59e0b', icon: 'alert-triangle', label: 'Incident' },
  RESPONSE: { color: '#ef4444', icon: 'zap', label: 'Response' },
  RECOVERY: { color: '#3b82f6', icon: 'refresh-cw', label: 'Recovery' },
};

/**
 * Timer status visual config.
 *
 * NOTE: For icons, import TIMER_STATUS_ICONS from '@/constants'.
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 */
export const PARK_TIMER_CONFIG: Record<ParkTimerStatus, { color: string; icon: string }> = {
  PENDING: { color: '#6b7280', icon: 'circle' },
  ACTIVE: { color: '#22c55e', icon: 'play' },
  WARNING: { color: '#f59e0b', icon: 'alert-triangle' },
  CRITICAL: { color: '#ef4444', icon: 'x-circle' },
  EXPIRED: { color: '#dc2626', icon: 'x-circle' },
  COMPLETED: { color: '#22c55e', icon: 'check-circle' },
  PAUSED: { color: '#6b7280', icon: 'pause' },
};

/**
 * Mask archetype visual config.
 *
 * NOTE: For icons, import MASK_ARCHETYPE_ICONS from '@/constants'.
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 */
export const PARK_MASK_CONFIG: Record<ParkMaskArchetype, { color: string; icon: string }> = {
  TRICKSTER: { color: '#f59e0b', icon: 'sparkles' },
  DREAMER: { color: '#a855f7', icon: 'cloud' },
  SKEPTIC: { color: '#6366f1', icon: 'search' },
  ARCHITECT: { color: '#3b82f6', icon: 'building-2' },
  CHILD: { color: '#ec4899', icon: 'star' },
  SAGE: { color: '#8b5cf6', icon: 'owl' },
  WARRIOR: { color: '#ef4444', icon: 'swords' },
  HEALER: { color: '#22c55e', icon: 'heart' },
};

/**
 * Eigenvector dimension config for radar chart.
 */
export const PARK_EIGENVECTOR_CONFIG: Record<string, { label: string; color: string }> = {
  creativity: { label: 'Creativity', color: '#f59e0b' },
  trust: { label: 'Trust', color: '#22c55e' },
  empathy: { label: 'Empathy', color: '#ec4899' },
  authority: { label: 'Authority', color: '#ef4444' },
  playfulness: { label: 'Playfulness', color: '#a855f7' },
  wisdom: { label: 'Wisdom', color: '#8b5cf6' },
  directness: { label: 'Directness', color: '#3b82f6' },
  warmth: { label: 'Warmth', color: '#f97316' },
};
