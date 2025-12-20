/**
 * Generated types for AGENTESE path: self.witness
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for manifest aspect.
 */
export interface SelfWitnessManifestResponse {
  total_thoughts: number;
  total_actions: number;
  trust_count: number;
  reversible_actions: number;
  storage_backend: string;
}

/**
 * Request for thoughts aspect.
 */
export interface SelfWitnessThoughtsRequest {
  limit?: number;
  source?: string | null;
  since?: string | null;
}

/**
 * Response for thoughts aspect.
 */
export interface SelfWitnessThoughtsResponse {
  count: number;
  thoughts?: {
    content: string;
    source: string;
    tags: string[];
    timestamp: string | null;
  }[];
}

/**
 * Request for trust aspect.
 */
export interface SelfWitnessTrustRequest {
  git_email: string;
  apply_decay?: boolean;
}

/**
 * Response for trust aspect.
 */
export interface SelfWitnessTrustResponse {
  trust_level: string;
  trust_level_value: number;
  raw_level: number;
  last_active: string | null;
  observation_count: number;
  successful_operations: number;
  confirmed_suggestions: number;
  total_suggestions: number;
  acceptance_rate: number;
  decay_applied: boolean;
}

/**
 * Request for capture aspect.
 */
export interface SelfWitnessCaptureRequest {
  content: string;
  source?: string;
  tags?: string[];
}

/**
 * Response for capture aspect.
 */
export interface SelfWitnessCaptureResponse {
  thought_id: string;
  content: string;
  source: string;
  tags: string[];
  timestamp: string | null;
  datum_id: string | null;
}

/**
 * Request for action aspect.
 */
export interface SelfWitnessActionRequest {
  action: string;
  success?: boolean;
  message?: string;
  reversible?: boolean;
  inverse_action?: string | null;
  git_stash_ref?: string | null;
}

/**
 * Response for action aspect.
 */
export interface SelfWitnessActionResponse {
  action_id: string;
  action: string;
  success: boolean;
  message: string;
  reversible: boolean;
  git_stash_ref: string | null;
  timestamp: string | null;
}

/**
 * Request for rollback aspect.
 */
export interface SelfWitnessRollbackRequest {
  hours?: number;
  limit?: number;
  reversible_only?: boolean;
}

/**
 * Response for rollback aspect.
 */
export interface SelfWitnessRollbackResponse {
  hours: number;
  count: number;
  actions?: {
    action_id: string;
    action: string;
    success: boolean;
    reversible: boolean;
    inverse_action: string | null;
    timestamp: string | null;
  }[];
}

/**
 * Request for escalate aspect.
 */
export interface SelfWitnessEscalateRequest {
  git_email: string;
  from_level: number;
  to_level: number;
  reason?: string;
}

/**
 * Response for escalate aspect.
 */
export interface SelfWitnessEscalateResponse {
  escalation_id: number;
  from_level: string;
  to_level: string;
  reason: string;
  timestamp: string | null;
}

/**
 * Request for invoke aspect (cross-jewel invocation).
 */
export interface SelfWitnessInvokeRequest {
  path: string;
  kwargs?: Record<string, unknown>;
}

/**
 * Response for invoke aspect.
 */
export interface SelfWitnessInvokeResponse {
  path: string;
  success: boolean;
  result: unknown;
  error: string | null;
  gate_decision: string | null;
  timestamp: string | null;
}

/**
 * Request for pipeline aspect (cross-jewel pipeline).
 */
export interface SelfWitnessPipelineRequest {
  steps?: {
    path: string;
    kwargs?: Record<string, unknown>;
  }[];
}

/**
 * Response for pipeline aspect.
 */
export interface SelfWitnessPipelineResponse {
  status: string;
  success: boolean;
  step_results?: {
    step_index: number;
    path: string;
    success: boolean;
    result: unknown;
    error: string | null;
    duration_ms: number;
  }[];
  final_result?: unknown;
  error?: string | null;
  total_duration_ms?: number;
  aborted_at_step?: number | null;
}
