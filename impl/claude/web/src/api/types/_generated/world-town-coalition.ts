/**
 * Generated types for AGENTESE path: world.town.coalition
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Coalition system health manifest response.
 */
export interface WorldTownCoalitionManifestResponse {
  total_coalitions: number;
  alive_coalitions: number;
  total_members: number;
  bridge_citizens: number;
  avg_strength: number;
}

/**
 * Response for coalition list aspect.
 */
export interface WorldTownCoalitionListResponse {
  coalitions: {
    id: string;
    name: string;
    member_count: number;
    strength: number;
    purpose: string;
  }[];
  total: number;
  bridge_citizens: string[];
}

/**
 * Full coalition details.
 */
export interface WorldTownCoalitionGetResponse {
  id: string;
  name: string;
  members: string[];
  strength: number;
  purpose: string;
  formed_at: string;
  centroid: Record<string, number> | null;
}

/**
 * Response for bridge citizens aspect.
 */
export interface WorldTownCoalitionBridgesResponse {
  bridge_citizens: string[];
  count: number;
}

/**
 * Request to detect coalitions in citizen graph.
 */
export interface WorldTownCoalitionDetectRequest {
  similarity_threshold?: number;
  k?: number;
}

/**
 * Response after coalition detection.
 */
export interface WorldTownCoalitionDetectResponse {
  coalitions: {
    id: string;
    name: string;
    members: string[];
    strength: number;
    purpose: string;
    formed_at: string;
    centroid: Record<string, number> | null;
  }[];
  detected_count: number;
}

/**
 * Response after applying coalition decay.
 */
export interface WorldTownCoalitionDecayResponse {
  pruned_count: number;
  remaining_count: number;
  decay_rate: number;
}
