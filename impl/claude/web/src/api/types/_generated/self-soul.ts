/**
 * Generated types for AGENTESE path: self.soul
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Soul manifest response.
 */
export interface SelfSoulManifestResponse {
  mode: string;
  has_llm: boolean;
  /** Response for eigenvectors aspect. */
  eigenvectors: {
    aesthetic: number;
    categorical: number;
    gratitude: number;
    heterarchy: number;
    generativity: number;
    joy: number;
  };
}

/**
 * Response for eigenvectors aspect.
 */
export interface SelfSoulEigenvectorsResponse {
  aesthetic: number;
  categorical: number;
  gratitude: number;
  heterarchy: number;
  generativity: number;
  joy: number;
}

/**
 * Request for starters, optionally filtered by mode.
 */
export interface SelfSoulStartersRequest {
  mode?: string | null;
}

/**
 * Response for starters aspect.
 */
export interface SelfSoulStartersResponse {
  mode: string | null;
  starters: string[] | Record<string, string[]>;
}

/**
 * Request to get or set dialogue mode.
 */
export interface SelfSoulModeRequest {
  set?: string | null;
}

/**
 * Response for mode aspect.
 */
export interface SelfSoulModeResponse {
  mode: string;
  status?: string;
}

/**
 * Request for dialogue aspect.
 */
export interface SelfSoulDialogueRequest {
  message: string;
  mode?: string | null;
}

/**
 * Response for dialogue aspect.
 */
export interface SelfSoulDialogueResponse {
  response: string;
  mode: string;
  tokens_used: number;
  was_template?: boolean;
}

/**
 * Request for challenge aspect.
 */
export interface SelfSoulChallengeRequest {
  message: string;
}

/**
 * Response for challenge aspect.
 */
export interface SelfSoulChallengeResponse {
  response: string;
  mode: string;
  tokens_used: number;
}

/**
 * Request for reflect aspect.
 */
export interface SelfSoulReflectRequest {
  message: string;
}

/**
 * Response for reflect aspect.
 */
export interface SelfSoulReflectResponse {
  response: string;
  mode: string;
  tokens_used: number;
}

/**
 * Request for why aspect (purpose exploration).
 */
export interface SelfSoulWhyRequest {
  message?: string | null;
  topic?: string | null;
}

/**
 * Response for why aspect.
 */
export interface SelfSoulWhyResponse {
  response: string;
  mode: string;
  depth: string;
  tokens_used: number;
}

/**
 * Request for tension aspect (creative tension exploration).
 */
export interface SelfSoulTensionRequest {
  message?: string | null;
  topic?: string | null;
}

/**
 * Response for tension aspect.
 */
export interface SelfSoulTensionResponse {
  response: string;
  mode: string;
  holding_space: boolean;
  tokens_used: number;
}

/**
 * Request for governance aspect (semantic gatekeeper).
 */
export interface SelfSoulGovernanceRequest {
  action: string;
  context?: Record<string, string>;
  budget?: string;
}

/**
 * Response for governance aspect.
 */
export interface SelfSoulGovernanceResponse {
  approved: boolean;
  reasoning: string;
  alternatives: string[];
  confidence: number;
  tokens_used: number;
  recommendation: string;
  principles: string[];
}
