/**
 * Generated types for AGENTESE path: world.town.citizen
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response type for citizen manifest.
 */
export interface WorldTownCitizenManifestResponse {
  total_citizens: number;
  active_citizens: number;
  archetypes: Record<string, number>;
}

/**
 * Response for citizen list aspect.
 */
export interface WorldTownCitizenListResponse {
  citizens: {
    id: string;
    name: string;
    archetype: string;
    is_active: boolean;
    interaction_count: number;
  }[];
  total: number;
}

/**
 * Response for citizen get aspect.
 */
export interface WorldTownCitizenGetResponse {
  /** Full citizen details. */
  citizen: {
    id: string;
    name: string;
    archetype: string;
    description: string | null;
    traits: Record<string, unknown>;
    is_active: boolean;
    interaction_count: number;
    last_interaction: string | null;
    created_at: string;
  };
}

/**
 * Request to create a new citizen.
 */
export interface WorldTownCitizenCreateRequest {
  name: string;
  archetype?: string;
  description?: string | null;
  traits?: Record<string, unknown> | null;
}

/**
 * Response after creating a citizen.
 */
export interface WorldTownCitizenCreateResponse {
  /** Full citizen details. */
  citizen: {
    id: string;
    name: string;
    archetype: string;
    description: string | null;
    traits: Record<string, unknown>;
    is_active: boolean;
    interaction_count: number;
    last_interaction: string | null;
    created_at: string;
  };
}

/**
 * Request to update a citizen.
 */
export interface WorldTownCitizenUpdateRequest {
  citizen_id: string;
  description?: string | null;
  traits?: Record<string, unknown> | null;
  is_active?: boolean | null;
}

/**
 * Response after updating a citizen.
 */
export interface WorldTownCitizenUpdateResponse {
  /** Full citizen details. */
  citizen: {
    id: string;
    name: string;
    archetype: string;
    description: string | null;
    traits: Record<string, unknown>;
    is_active: boolean;
    interaction_count: number;
    last_interaction: string | null;
    created_at: string;
  };
}
