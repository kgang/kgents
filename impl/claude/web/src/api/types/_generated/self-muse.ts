/**
 * Generated types for AGENTESE path: self.muse
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for manifest aspect.
 */
export interface SelfMuseManifestResponse {
  state: string;
  arc_phase: string;
  arc_confidence: number;
  tension: number;
  tension_trend: number;
  crystals_observed: number;
  whispers_made: number;
  whispers_accepted: number;
  whispers_dismissed: number;
  acceptance_rate: number;
  can_whisper: boolean;
  pending_whisper_id: string | null;
  status: string;
}

/**
 * Request for arc aspect - get current story arc.
 */
export interface SelfMuseArcRequest {
  include_history?: boolean;
}

/**
 * Response for arc aspect.
 */
export interface SelfMuseArcResponse {
  phase: string;
  phase_emoji: string;
  confidence: number;
  tension: number;
  momentum: number;
  phase_duration_seconds: number;
  is_rising: boolean;
  is_falling: boolean;
  is_peak: boolean;
}

/**
 * Request for tension aspect.
 */
export interface SelfMuseTensionRequest {
  include_trend?: boolean;
}

/**
 * Response for tension aspect.
 */
export interface SelfMuseTensionResponse {
  level: number;
  trend: number;
  category: string;
  trigger: string | null;
}

/**
 * Request for whisper aspect - get current whisper if any.
 */
export interface SelfMuseWhisperRequest {

}

/**
 * Response for whisper aspect.
 */
export interface SelfMuseWhisperResponse {
  has_whisper: boolean;
  whisper_id?: string | null;
  content?: string | null;
  category?: string | null;
  urgency?: number | null;
  confidence?: number | null;
  timestamp?: string | null;
}

/**
 * Request for encourage aspect - request earned encouragement.
 */
export interface SelfMuseEncourageRequest {
  context?: string;
}

/**
 * Response for encourage aspect.
 */
export interface SelfMuseEncourageResponse {
  whisper_id: string;
  content: string;
  earned: boolean;
  arc_phase: string;
  tension: number;
  timestamp: string;
}

/**
 * Request for reframe aspect - request perspective shift.
 */
export interface SelfMuseReframeRequest {
  context?: string;
  current_perspective?: string;
}

/**
 * Response for reframe aspect.
 */
export interface SelfMuseReframeResponse {
  whisper_id: string;
  content: string;
  original_perspective: string;
  new_perspective: string;
  arc_phase: string;
  timestamp: string;
}

/**
 * Request for summon aspect - force suggestion (bypass timing).
 */
export interface SelfMuseSummonRequest {
  topic?: string;
}

/**
 * Response for summon aspect.
 */
export interface SelfMuseSummonResponse {
  whisper_id: string;
  content: string;
  category: string;
  confidence: number;
  summoned: boolean;
  timestamp: string;
}

/**
 * Request for dismiss aspect - dismiss current whisper.
 */
export interface SelfMuseDismissRequest {
  whisper_id: string;
  reason?: string;
}

/**
 * Response for dismiss aspect.
 */
export interface SelfMuseDismissResponse {
  dismissed: boolean;
  whisper_id: string;
  cooldown_minutes: number;
  timestamp: string;
}

/**
 * Request for accept aspect - accept/acknowledge a whisper.
 */
export interface SelfMuseAcceptRequest {
  whisper_id: string;
  action?: string;
}

/**
 * Response for accept aspect.
 */
export interface SelfMuseAcceptResponse {
  accepted: boolean;
  whisper_id: string;
  action: string;
  timestamp: string;
}

/**
 * Request for history aspect - get whisper history.
 */
export interface SelfMuseHistoryRequest {
  limit?: number;
  category?: string | null;
  accepted_only?: boolean;
}

/**
 * Response for history aspect.
 */
export interface SelfMuseHistoryResponse {
  count: number;
  whispers?: {
    whisper_id: string;
    content: string;
    category: string;
    urgency: number;
    confidence: number;
    arc_phase: string;
    tension: number;
    accepted: boolean;
    dismissed: boolean;
    timestamp: string;
  }[];
}
