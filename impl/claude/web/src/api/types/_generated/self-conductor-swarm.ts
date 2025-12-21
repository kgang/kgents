/**
 * Generated types for AGENTESE path: self.conductor.swarm
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for manifest aspect.
 */
export interface SelfConductorSwarmManifestResponse {
  active_count: number;
  max_agents: number;
  agents: Record<string, unknown>[];
  at_capacity: boolean;
}

/**
 * Response from list.
 */
export interface SelfConductorSwarmListResponse {
  agents: Record<string, unknown>[];
  count: number;
}

/**
 * Response from roles.
 */
export interface SelfConductorSwarmRolesResponse {
  roles: Record<string, unknown>[];
  count: number;
}

/**
 * Request to spawn an agent.
 */
export interface SelfConductorSwarmSpawnRequest {
  task: string;
  role?: string | null;
}

/**
 * Response from spawn.
 */
export interface SelfConductorSwarmSpawnResponse {
  success: boolean;
  agent_id: string | null;
  role: string | null;
  reasons: string[];
}

/**
 * Request to delegate task.
 */
export interface SelfConductorSwarmDelegateRequest {
  from_agent: string;
  to_agent: string;
  task: Record<string, unknown>;
}

/**
 * Response from delegate.
 */
export interface SelfConductorSwarmDelegateResponse {
  success: boolean;
  delegation_id: string;
  from_agent: string;
  to_agent: string;
}

/**
 * Request to hand off context.
 */
export interface SelfConductorSwarmHandoffRequest {
  from_agent: string;
  to_agent: string;
  context: Record<string, unknown>;
  conversation?: Record<string, unknown>[] | null;
}

/**
 * Response from handoff.
 */
export interface SelfConductorSwarmHandoffResponse {
  success: boolean;
  handoff_id: string;
  from_despawned: boolean;
}

/**
 * Request to despawn an agent.
 */
export interface SelfConductorSwarmDespawnRequest {
  agent_id: string;
}

/**
 * Response from despawn.
 */
export interface SelfConductorSwarmDespawnResponse {
  success: boolean;
  agent_id: string;
}
