/**
 * Generated types for AGENTESE path: world.town
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Town health status manifest response.
 */
export interface WorldTownManifestResponse {
  total_citizens: number;
  active_citizens: number;
  total_conversations: number;
  active_conversations: number;
  total_relationships: number;
  storage_backend: string;
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
 * Request for citizen relationships.
 */
export interface WorldTownRelationshipsRequest {
  citizen_id?: string | null;
  name?: string | null;
}

/**
 * Response for citizen relationships.
 */
export interface WorldTownRelationshipsResponse {
  citizen_id: string;
  count: number;
  relationships: {
    id: string;
    citizen_a_id: string;
    citizen_b_id: string;
    relationship_type: string;
    strength: number;
    interaction_count: number;
    notes: string | null;
  }[];
}

/**
 * Request for dialogue history.
 */
export interface WorldTownHistoryRequest {
  citizen_id?: string | null;
  name?: string | null;
  limit?: number;
}

/**
 * Response for dialogue history.
 */
export interface WorldTownHistoryResponse {
  citizen_id: string;
  conversations: {
    id: string;
    topic: string | null;
    summary: string | null;
    turn_count: number;
    is_active: boolean;
    created_at: string;
  }[];
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

/**
 * Request to start a conversation with a citizen.
 */
export interface WorldTownConverseRequest {
  citizen_id?: string | null;
  name?: string | null;
  topic?: string | null;
}

/**
 * Response after starting a conversation.
 */
export interface WorldTownConverseResponse {
  /** Full conversation details. */
  conversation: {
    id: string;
    citizen_id: string;
    citizen_name: string;
    topic: string | null;
    summary: string | null;
    turn_count: number;
    is_active: boolean;
    created_at: string;
    turns?: {
      id: string;
      turn_number: number;
      role: string;
      content: string;
      sentiment: string | null;
      emotion: string | null;
      created_at: string;
    }[];
  };
}

/**
 * Request to add a turn to a conversation.
 */
export interface WorldTownTurnRequest {
  conversation_id: string;
  content: string;
  role?: string;
  sentiment?: string | null;
  emotion?: string | null;
}

/**
 * Response after adding a turn.
 */
export interface WorldTownTurnResponse {
  /** Summary of a conversation turn. */
  turn: {
    id: string;
    turn_number: number;
    role: string;
    content: string;
    sentiment: string | null;
    emotion: string | null;
    created_at: string;
  };
}
