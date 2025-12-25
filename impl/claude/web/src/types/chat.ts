/**
 * Chat System Types
 *
 * Core TypeScript types for the web-native chat protocol v4.1b.
 * Implements ChatKBlock pattern with branching, evidence accumulation,
 * and witness integration.
 *
 * @see spec/protocols/chat-web.md
 */

// =============================================================================
// ChatState Polynomial (Part II: Categorical Foundation)
// =============================================================================

/**
 * Chat polynomial state machine states.
 * Maps to ChatPolynomial = PolyAgent[ChatState, Message, Response]
 */
export type ChatState = 'IDLE' | 'PROCESSING' | 'AWAITING_TOOL' | 'BRANCHING' | 'COMPRESSING';

// =============================================================================
// Branching & Session Management (Part IV: Multi-Session Architecture)
// =============================================================================

/**
 * Branch merge strategies.
 */
export type MergeStrategy = 'sequential' | 'interleave' | 'manual';

/**
 * Session node in the branch DAG.
 */
export interface SessionNode {
  id: string;
  parent_id: string | null;
  fork_point: number | null; // Turn number where fork occurred
  branch_name: string;
  created_at: string;
  last_active: string;
  turn_count: number;
  is_merged: boolean;
  merged_into: string | null;
}

// =============================================================================
// Context Management (Part V: Context Management)
// =============================================================================

/**
 * Linearity tags for compression priority.
 * Messages tagged REQUIRED are never dropped.
 */
export type LinearityTag = 'REQUIRED' | 'PRESERVED' | 'DROPPABLE';

// =============================================================================
// Evidence & Bayesian State (Part II.4: Evidence Accumulation)
// =============================================================================

/**
 * Bayesian prior for evidence accumulation.
 * Follows ASHC BetaPrior pattern.
 */
export interface BetaPrior {
  alpha: number;
  beta: number;
}

/**
 * Stopping decision state from ASHC adaptive stopping.
 */
export type StoppingDecision = 'CONTINUE' | 'STOP' | 'USER_OVERRIDE';

/**
 * Evidence accumulated during a chat turn.
 * Uses ASHC-inspired Bayesian primitives.
 */
export interface TurnEvidence {
  // Bayesian state (ASHC BetaPrior)
  prior: BetaPrior;
  posterior: BetaPrior;

  // Stopping state (ASHC StoppingState)
  stopping: StoppingDecision;

  // Evidence components
  tools_executed: ToolResult[];
  tests_run: TestResult[];
  claims_made: Claim[];

  // Computed confidence (Bayesian posterior mean)
  confidence: number;
}

/**
 * Chat-level evidence state (simplified from ASHC).
 * Used when not editing specs (no chaos testing).
 */
export interface ChatEvidence {
  // Bayesian state
  prior_alpha: number;
  prior_beta: number;

  // Computed metrics
  confidence: number; // P(goal_achieved) under posterior
  should_stop: boolean; // Stopping criterion met

  // Evidence counts
  tools_succeeded: number;
  tools_failed: number;

  // Optional ASHC equivalence (when spec edited)
  ashc_equivalence?: number;
}

/**
 * Tool execution result.
 */
export interface ToolResult {
  name: string;
  success: boolean;
  output?: string;
  error?: string;
}

/**
 * Test result (if code generated).
 */
export interface TestResult {
  name: string;
  passed: boolean;
  duration_ms: number;
}

/**
 * Claim made by assistant.
 */
export interface Claim {
  statement: string;
  confidence: number;
  verified: boolean;
}

// =============================================================================
// Messages & Turns (Part X: Frontend Components)
// =============================================================================

/**
 * @Mention types for context injection (Part VI: Context Injection).
 */
export type MentionType =
  | 'file'
  | 'symbol'
  | 'spec'
  | 'witness'
  | 'web'
  | 'terminal'
  | 'project';

/**
 * Injected mention reference.
 */
export interface Mention {
  type: MentionType;
  target: string; // file path, URL, symbol name, etc.
  display_text: string;
}

/**
 * Chat message.
 */
export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  mentions: Mention[];
  linearity_tag: LinearityTag;
}

/**
 * Tool use transparency (Part VII: Tool Transparency).
 */
export interface ToolUse {
  tool_name: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  input?: Record<string, unknown>;
  output?: unknown;
  error?: string;
  started_at: string;
  completed_at?: string;
}

/**
 * Evidence delta for a turn.
 */
export interface EvidenceDelta {
  prior_before: BetaPrior;
  prior_after: BetaPrior;
  success: boolean;
}

/**
 * Constitutional principle scores (0-1 range).
 * Based on the 7 core kgents principles.
 */
export interface PrincipleScore {
  tasteful: number;
  curated: number;
  ethical: number;
  joy_inducing: number;
  composable: number;
  heterarchical: number;
  generative: number;
}

/**
 * Portal emission in chat turn.
 * Represents content emitted to a destination via portal token.
 */
export interface PortalEmission {
  portal_id: string;
  destination: string;
  edge_type: string;
  access: 'read' | 'readwrite';
  content_preview: string | null;
  content_full: string | null;
  line_count: number;
  exists: boolean;
  auto_expand: boolean;
  emitted_at: string;
}

/**
 * Chat turn (message pair + metadata).
 */
export interface Turn {
  turn_number: number;
  user_message: Message;
  assistant_response: Message;
  tools_used: ToolUse[];
  evidence_delta: EvidenceDelta;
  confidence: number; // Turn-level confidence
  constitutional_score?: PrincipleScore; // Constitutional adherence (optional)
  portal_emissions?: PortalEmission[]; // Portal content emitted in this turn
  started_at: string;
  completed_at: string;
}

// =============================================================================
// Chat Sessions (Part I: Core Insight - ChatKBlock)
// =============================================================================

/**
 * Chat session as a K-Block.
 * Represents transactional conversation with fork/merge/rewind.
 */
export interface ChatSession {
  id: string;
  project_id: string | null;
  branch_name: string;
  parent_id: string | null;
  fork_point: number | null;

  // Turns
  turns: Turn[];
  turn_count: number;

  // Context state
  context_size: number; // Current token count
  context_window: number; // Max tokens (200k for Opus 4.5)
  compression_active: boolean;

  // Evidence
  evidence: ChatEvidence;

  // State machine
  state: ChatState;
  valid_directions: string[]; // Valid inputs for current state

  // Metadata
  created_at: string;
  last_active: string;
}

// =============================================================================
// Branches (Part IV: Multi-Session Architecture)
// =============================================================================

/**
 * Branch metadata for visualization.
 */
export interface Branch {
  id: string;
  name: string;
  parent_id: string | null;
  fork_point: number;
  turn_count: number;
  is_active: boolean;
  is_merged: boolean;
  created_at: string;
}

// =============================================================================
// Crystallization (Part IX: Evidence & Witness)
// =============================================================================

/**
 * Crystallized session summary.
 * Created when session ends or context overflows.
 */
export interface SessionCrystal {
  session_id: string;
  title: string; // Auto-generated or user-provided
  summary: string; // LLM-generated summary
  key_decisions: string[]; // Extracted decisions
  artifacts: string[]; // Created files, specs
  final_evidence: ChatEvidence;
  created_at: string;
  turn_count: number;
  crystallized_at: string;
}

/**
 * Trailing session state (Part IX.4b: Trailing Session Affordance).
 * Session that has crystallized but remains visible.
 */
export interface TrailingSession {
  session_id: string;
  crystal: SessionCrystal;
  trailing_turns: Turn[]; // Visible but not in context
  crystallized_at: string;

  // User actions
  can_continue: boolean; // Re-activate
  can_fork: boolean; // Start new session referencing this
  can_dismiss: boolean; // Hide trailing section
}

// =============================================================================
// Tool Transparency (Part VII: Tool Transparency)
// =============================================================================

/**
 * Tool transparency modes (Part VII.2: Asymmetric Design).
 * Reads can be silent; mutations must be acknowledged.
 */
export type TransparencyLevel = 'minimal' | 'approval' | 'detailed';

/**
 * Mutation acknowledgment (Part VII.2: Acknowledgment Semantics).
 */
export interface MutationAcknowledgment {
  mutation_id: string;
  acknowledged_at: string;
  mode: 'click' | 'keyboard' | 'timeout_accept';
}

/**
 * Tool manifest entry.
 */
export interface ToolManifest {
  name: string;
  description: string;
  status: 'available' | 'limited' | 'gated'; // Status indicator
  is_pure_read: boolean; // Non-destructive read
  is_destructive: boolean; // Irrecoverable mutation
  rate_limit?: {
    current: number;
    limit: number;
    reset_at: string;
  };
}

// =============================================================================
// Confidence Indicators (Part VII.3: Confidence Indicators)
// =============================================================================

/**
 * Confidence level for visual display.
 */
export type ConfidenceLevel = 'high' | 'medium' | 'low';

/**
 * Get confidence level from Bayesian probability.
 */
export function getConfidenceLevel(probability: number): ConfidenceLevel {
  if (probability > 0.8) return 'high';
  if (probability > 0.5) return 'medium';
  return 'low';
}

// =============================================================================
// API Request/Response Types (Part XIII: Implementation Reference)
// =============================================================================

/**
 * Request to create a new chat session.
 */
export interface CreateSessionRequest {
  project_id?: string;
  initial_message?: string;
}

/**
 * Request to send a message.
 */
export interface SendMessageRequest {
  message: string;
  mentions?: Mention[];
}

/**
 * Request to fork a session.
 */
export interface ForkSessionRequest {
  branch_name: string;
  fork_from_turn?: number; // Default: current turn
}

/**
 * Request to merge sessions.
 */
export interface MergeSessionRequest {
  other_id: string;
  strategy: MergeStrategy;
}

/**
 * Request to rewind session.
 */
export interface RewindSessionRequest {
  turns: number;
}

/**
 * Turn result from backend (streaming).
 */
export interface TurnResult {
  turn: Turn;
  session_state: {
    context_size: number;
    compression_active: boolean;
    evidence: ChatEvidence;
  };
  stopping_suggestion?: string; // If should_stop == true
}

// =============================================================================
// Configuration (Appendix A: Configuration Schema)
// =============================================================================

/**
 * Chat system configuration.
 */
export interface ChatConfig {
  // Context management
  context_window: number;
  compress_at: number; // Fraction (0.8 = 80%)
  resume_at: number; // Hysteresis threshold (0.7 = 70%)
  compression_strategy: 'incremental' | 'galois';
  galois_tolerance: number; // Semantic loss tolerance

  // Branching
  max_branches: number; // Cognitive limit (default 3)
  auto_merge_threshold: number; // Turns before suggesting merge

  // Evidence & stopping
  enable_evidence: boolean;
  stopping_confidence: number; // P(goal_achieved) threshold (0.95)
  min_turns_before_stop: number; // Minimum turns before suggesting stop

  // Tool transparency
  default_transparency: TransparencyLevel;

  // Witness
  auto_mark: boolean; // Auto-create ChatMark per turn
  auto_crystallize: boolean; // Auto-crystallize on inactivity
  crystallization_delay: number; // Seconds after last turn (default 300)

  // UI
  show_context_indicator: boolean;
  show_confidence_scores: boolean;
  show_action_panel: boolean;
  enable_branch_tree: boolean;
}

/**
 * Default chat configuration.
 */
export const DEFAULT_CHAT_CONFIG: ChatConfig = {
  context_window: 200_000,
  compress_at: 0.8,
  resume_at: 0.7,
  compression_strategy: 'incremental',
  galois_tolerance: 0.05,
  max_branches: 3,
  auto_merge_threshold: 100,
  enable_evidence: true,
  stopping_confidence: 0.95,
  min_turns_before_stop: 3,
  default_transparency: 'approval',
  auto_mark: true,
  auto_crystallize: true,
  crystallization_delay: 300,
  show_context_indicator: true,
  show_confidence_scores: true,
  show_action_panel: true,
  enable_branch_tree: true,
};
