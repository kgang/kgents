/**
 * Generated types for AGENTESE path: time.witness
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Manifest response for time.witness.
 */
export interface TimeWitnessManifestResponse {
  active_session: string | null;
  session_started_at: string | null;
  total_crystals: number;
  crystals_this_session: number;
  pending_observations: number;
  last_crystallization: string | null;
  status: string;
}

/**
 * Request for attune aspect - start observation session.
 */
export interface TimeWitnessAttuneRequest {
  session_name?: string;
  context?: string;
}

/**
 * Response for attune aspect.
 */
export interface TimeWitnessAttuneResponse {
  session_id: string;
  started_at: string;
  attuned: boolean;
}

/**
 * Request for mark aspect - create user marker.
 */
export interface TimeWitnessMarkRequest {
  content: string;
  tags?: string[];
}

/**
 * Response for mark aspect.
 */
export interface TimeWitnessMarkResponse {
  marker_id: string;
  content: string;
  tags: string[];
  timestamp: string;
}

/**
 * Request for crystallize aspect - trigger experience crystallization.
 */
export interface TimeWitnessCrystallizeRequest {
  session_id?: string;
  markers?: string[];
  force?: boolean;
}

/**
 * Response for crystallize aspect.
 */
export interface TimeWitnessCrystallizeResponse {
  crystal_id: string;
  session_id: string;
  thought_count: number;
  topics: string[];
  mood: Record<string, number>;
  narrative_summary: string;
  crystallized_at: string;
}

/**
 * Request for timeline aspect - get crystallization timeline.
 */
export interface TimeWitnessTimelineRequest {
  limit?: number;
  since?: string | null;
  session_id?: string | null;
}

/**
 * Response for timeline aspect.
 */
export interface TimeWitnessTimelineResponse {
  count: number;
  crystals?: {
    crystal_id: string;
    session_id: string;
    thought_count: number;
    started_at: string | null;
    ended_at: string | null;
    duration_minutes: number | null;
    topics: string[];
    mood_brightness: number;
    mood_dominant_quality: string;
    narrative_summary: string;
    crystallized_at: string;
  }[];
}

/**
 * Request for crystal aspect - retrieve specific crystal.
 */
export interface TimeWitnessCrystalRequest {
  crystal_id?: string | null;
  session_id?: string | null;
  topics?: string[];
}

/**
 * Response for crystal aspect - full crystal detail.
 */
export interface TimeWitnessCrystalResponse {
  found: boolean;
  /** A crystal summary for list responses. */
  crystal?: {
    crystal_id: string;
    session_id: string;
    thought_count: number;
    started_at: string | null;
    ended_at: string | null;
    duration_minutes: number | null;
    topics: string[];
    mood_brightness: number;
    mood_dominant_quality: string;
    narrative_summary: string;
    crystallized_at: string;
  } | null;
  thoughts?: {
    content: string;
    source: string;
    tags: string[];
    timestamp: string | null;
  }[];
  topology?: Record<string, unknown>;
  mood?: Record<string, number>;
  narrative?: Record<string, unknown>;
}

/**
 * Request for territory aspect - codebase heat map.
 */
export interface TimeWitnessTerritoryRequest {
  session_id?: string | null;
  hours?: number;
}

/**
 * Response for territory aspect - codebase activity map.
 */
export interface TimeWitnessTerritoryResponse {
  primary_path: string;
  heat: Record<string, number>;
  total_crystals: number;
  time_window_hours: number;
}
