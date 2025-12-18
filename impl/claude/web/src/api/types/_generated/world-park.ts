/**
 * Generated types for AGENTESE path: world.park
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Park health status manifest response.
 */
export interface WorldParkManifestResponse {
  total_hosts: number;
  active_hosts: number;
  total_episodes: number;
  active_episodes: number;
  total_memories: number;
  total_locations: number;
  consent_refusal_rate: number;
  storage_backend: string;
}

/**
 * Response for host list aspect.
 */
export interface WorldParkHostListResponse {
  count: number;
  hosts: {
    id: string;
    name: string;
    character: string;
    is_active: boolean;
    location: string | null;
    mood: string | null;
  }[];
}

/**
 * Response for host get aspect.
 */
export interface WorldParkHostGetResponse {
  /** Full host details. */
  host: {
    id: string;
    name: string;
    character: string;
    backstory: string | null;
    traits: string[];
    values: string[];
    boundaries: string[];
    is_active: boolean;
    mood: string | null;
    energy_level: number;
    current_location: string | null;
    interaction_count: number;
    consent_refusal_count: number;
  };
}

/**
 * Response for episode list aspect.
 */
export interface WorldParkEpisodeListResponse {
  count: number;
  episodes: {
    id: string;
    title: string | null;
    status: string;
    visitor_name: string | null;
    interaction_count: number;
    started_at: string;
  }[];
}

/**
 * Response for location list aspect.
 */
export interface WorldParkLocationListResponse {
  count: number;
  locations: {
    id: string;
    name: string;
    description: string | null;
    atmosphere: string | null;
    is_open: boolean;
  }[];
}

/**
 * Request to create a new park host.
 */
export interface WorldParkHostCreateRequest {
  name: string;
  character: string;
  backstory?: string | null;
  traits?: string[] | null;
  values?: string[] | null;
  boundaries?: string[] | null;
  location?: string | null;
}

/**
 * Response after creating a host.
 */
export interface WorldParkHostCreateResponse {
  /** Full host details. */
  host: {
    id: string;
    name: string;
    character: string;
    backstory: string | null;
    traits: string[];
    values: string[];
    boundaries: string[];
    is_active: boolean;
    mood: string | null;
    energy_level: number;
    current_location: string | null;
    interaction_count: number;
    consent_refusal_count: number;
  };
}

/**
 * Request to update host state.
 */
export interface WorldParkHostUpdateRequest {
  host_id: string;
  mood?: string | null;
  energy_level?: number | null;
  location?: string | null;
}

/**
 * Response after updating a host.
 */
export interface WorldParkHostUpdateResponse {
  /** Full host details. */
  host: {
    id: string;
    name: string;
    character: string;
    backstory: string | null;
    traits: string[];
    values: string[];
    boundaries: string[];
    is_active: boolean;
    mood: string | null;
    energy_level: number;
    current_location: string | null;
    interaction_count: number;
    consent_refusal_count: number;
  };
}

/**
 * Request to interact with a host.
 */
export interface WorldParkHostInteractRequest {
  episode_id: string;
  host_id: string;
  input: string;
  type?: string;
  location?: string | null;
  check_consent?: boolean;
}

/**
 * Response after interacting with a host.
 */
export interface WorldParkHostInteractResponse {
  /** Details of an interaction with a host. */
  interaction: {
    id: string;
    host_name: string;
    interaction_type: string;
    visitor_input: string;
    host_response: string | null;
    consent_requested: boolean;
    consent_given: boolean | null;
    consent_reason: string | null;
    host_emotion: string | null;
    location: string | null;
  };
}

/**
 * Request to view host memories.
 */
export interface WorldParkHostWitnessRequest {
  host_id: string;
  memory_type?: string | null;
  min_salience?: number;
  limit?: number;
}

/**
 * Response for host memories.
 */
export interface WorldParkHostWitnessResponse {
  count: number;
  memories: {
    id: string;
    memory_type: string;
    summary: string | null;
    salience: number;
    emotional_valence: number;
  }[];
}

/**
 * Request to start a park episode.
 */
export interface WorldParkEpisodeStartRequest {
  visitor_name?: string | null;
  title?: string | null;
}

/**
 * Response after starting an episode.
 */
export interface WorldParkEpisodeStartResponse {
  /** Full episode details. */
  episode: {
    id: string;
    visitor_id: string;
    visitor_name: string | null;
    title: string | null;
    status: string;
    interaction_count: number;
    hosts_met: string[];
    locations_visited: string[];
    started_at: string;
    ended_at: string | null;
    duration_seconds: number | null;
  };
}

/**
 * Request to end a park episode.
 */
export interface WorldParkEpisodeEndRequest {
  episode_id: string;
  summary?: string | null;
  status?: string;
}

/**
 * Response after ending an episode.
 */
export interface WorldParkEpisodeEndResponse {
  /** Full episode details. */
  episode: {
    id: string;
    visitor_id: string;
    visitor_name: string | null;
    title: string | null;
    status: string;
    interaction_count: number;
    hosts_met: string[];
    locations_visited: string[];
    started_at: string;
    ended_at: string | null;
    duration_seconds: number | null;
  };
}

/**
 * Request to create a location.
 */
export interface WorldParkLocationCreateRequest {
  name: string;
  description?: string | null;
  atmosphere?: string | null;
  x?: number | null;
  y?: number | null;
  capacity?: number | null;
  connected_to?: string[] | null;
}

/**
 * Response after creating a location.
 */
export interface WorldParkLocationCreateResponse {
  id: string;
  name: string;
  description: string | null;
  atmosphere: string | null;
  is_open: boolean;
}
