/**
 * Generated types for AGENTESE path: time.coffee
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for manifest aspect.
 */
export interface TimeCoffeeManifestResponse {
  state: string;
  is_active: boolean;
  current_movement: string | null;
  today_voice: Record<string, unknown> | null;
  last_ritual: string | null;
  movements: Record<string, unknown>[];
}

/**
 * Response for garden aspect.
 */
export interface TimeCoffeeGardenResponse {
  harvest: Record<string, unknown>[];
  growing: Record<string, unknown>[];
  sprouting: Record<string, unknown>[];
  seeds: Record<string, unknown>[];
  generated_at: string;
}

/**
 * Response for weather aspect.
 */
export interface TimeCoffeeWeatherResponse {
  refactoring: Record<string, unknown>[];
  emerging: Record<string, unknown>[];
  scaffolding: Record<string, unknown>[];
  tension: Record<string, unknown>[];
  generated_at: string;
}

/**
 * Response for menu aspect.
 */
export interface TimeCoffeeMenuResponse {
  gentle: Record<string, unknown>[];
  focused: Record<string, unknown>[];
  intense: Record<string, unknown>[];
  serendipitous_prompt: string;
  generated_at: string;
}

/**
 * Request for capture aspect.
 */
export interface TimeCoffeeCaptureRequest {
  non_code_thought?: string | null;
  eye_catch?: string | null;
  success_criteria?: string | null;
  raw_feeling?: string | null;
  chosen_challenge?: string | null;
}

/**
 * Response for capture aspect.
 */
export interface TimeCoffeeCaptureResponse {
  captured: boolean;
  voice: Record<string, unknown> | null;
  saved_path: string | null;
}

/**
 * Response for begin aspect.
 */
export interface TimeCoffeeBeginResponse {
  transitioned: boolean;
  message: string;
}

/**
 * Request for history aspect.
 */
export interface TimeCoffeeHistoryRequest {
  limit?: number;
  capture_date?: string | null;
}

/**
 * Response for history aspect.
 */
export interface TimeCoffeeHistoryResponse {
  voices: Record<string, unknown>[];
  patterns: Record<string, unknown> | null;
}
