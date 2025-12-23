/**
 * Generated types for AGENTESE path: self.fusion
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for fusion manifest.
 */
export interface SelfFusionManifestResponse {
  total_proposals: number;
  total_fusions: number;
  pending_fusions: number;
  synthesized_fusions: number;
  vetoed_fusions: number;
}

/**
 * Request to create a proposal.
 */
export interface SelfFusionProposeRequest {
  agent: string;
  content: string;
  reasoning: string;
  principles?: string[] | null;
}

/**
 * Response after creating a proposal.
 */
export interface SelfFusionProposeResponse {
  proposal_id: string;
  agent: string;
  content: string;
  reasoning: string;
}

/**
 * Request to fuse two proposals.
 */
export interface SelfFusionFuseRequest {
  proposal_a_id: string;
  proposal_b_id: string;
  synthesis_content?: string | null;
  synthesis_reasoning?: string | null;
  incorporates_from_a?: string | null;
  incorporates_from_b?: string | null;
  transcends?: string | null;
}

/**
 * Response after fusion attempt.
 */
export interface SelfFusionFuseResponse {
  fusion_id: string;
  status: string;
  synthesis_content?: string | null;
  synthesis_reasoning?: string | null;
  is_genuine_fusion?: boolean;
}

/**
 * Request to apply disgust veto.
 */
export interface SelfFusionVetoRequest {
  fusion_id: string;
  reason: string;
}

/**
 * Response after fusion attempt.
 */
export interface SelfFusionVetoResponse {
  fusion_id: string;
  status: string;
  synthesis_content?: string | null;
  synthesis_reasoning?: string | null;
  is_genuine_fusion?: boolean;
}
