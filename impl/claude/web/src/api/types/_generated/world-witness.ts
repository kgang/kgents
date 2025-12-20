/**
 * Generated types for AGENTESE path: world.witness
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for world.witness.manifest - orchestration status.
 */
export interface WorldWitnessManifestResponse {
  orchestrator_status: string;
  trust_level: string;
  trust_level_value: number;
  available_jewels: string[];
  pending_schedules: number;
  active_workflows: number;
  last_invocation: string | null;
}

/**
 * Request for listing available workflows.
 */
export interface WorldWitnessWorkflowsRequest {
  category?: string | null;
  max_trust?: number | null;
}

/**
 * Response for workflow listing.
 */
export interface WorldWitnessWorkflowsResponse {
  count: number;
  workflows?: {
    name: string;
    description: string;
    category: string;
    required_trust: number;
    tags: string[];
    step_count: number;
  }[];
}

/**
 * Request for running a workflow template.
 */
export interface WorldWitnessRunRequest {
  workflow_name: string;
  initial_kwargs?: Record<string, unknown>;
}

/**
 * Response for workflow execution.
 */
export interface WorldWitnessRunResponse {
  workflow_name: string;
  status: string;
  success: boolean;
  step_count: number;
  final_result?: unknown;
  error?: string | null;
  duration_ms?: number;
}
