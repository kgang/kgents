/**
 * Generated types for AGENTESE path: world.town.workshop
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for workshop status aspect.
 */
export interface WorldTownWorkshopManifestResponse {
  phase: string;
  is_idle: boolean;
  is_complete: boolean;
  active_task: string | null;
  active_builder: string | null;
  builders: string[];
  artifacts_count: number;
}

/**
 * Response listing available builders.
 */
export interface WorldTownWorkshopBuildersResponse {
  builders: string[];
  count: number;
}

/**
 * Request to assign task to workshop builders.
 */
export interface WorldTownWorkshopAssignRequest {
  task: string;
  priority?: number;
}

/**
 * Response after workshop task assignment.
 */
export interface WorldTownWorkshopAssignResponse {
  task_id: string;
  task_description: string;
  lead_builder: string;
  estimated_phases: string[];
  assignments: Record<string, string[]>;
}

/**
 * Response for workshop event (advance, complete).
 */
export interface WorldTownWorkshopAdvanceResponse {
  type: string;
  timestamp: string;
  builder: string | null;
  phase: string;
  message: string;
  artifact: unknown;
  metadata: Record<string, unknown>;
}

/**
 * Response for workshop event (advance, complete).
 */
export interface WorldTownWorkshopCompleteResponse {
  type: string;
  timestamp: string;
  builder: string | null;
  phase: string;
  message: string;
  artifact: unknown;
  metadata: Record<string, unknown>;
}
