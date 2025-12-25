/**
 * Theory Integration Types
 *
 * Constitutional principles, policy traces, and personality attractors
 * for the kgents value system.
 */

export interface ConstitutionScores {
  tasteful: number;      // 0-1
  curated: number;
  ethical: number;
  joyInducing: number;
  composable: number;
  heterarchical: number;
  generative: number;
}

export interface Decision {
  id: string;
  action: string;
  principleScores: ConstitutionScores;
  timestamp: number;
}

export interface PolicyTrace {
  decisions: Decision[];
  compressionRatio: number;
  trajectory: ConstitutionScores[];
}

export interface PersonalityAttractor {
  coordinates: ConstitutionScores;
  basin: ConstitutionScores[];
  stability: number;
}

// Principle metadata
export const PRINCIPLES = [
  { key: 'tasteful', label: 'Tasteful', angle: 0 },
  { key: 'curated', label: 'Curated', angle: 51.43 },
  { key: 'ethical', label: 'Ethical', angle: 102.86 },
  { key: 'joyInducing', label: 'Joy-Inducing', angle: 154.29 },
  { key: 'composable', label: 'Composable', angle: 205.71 },
  { key: 'heterarchical', label: 'Heterarchical', angle: 257.14 },
  { key: 'generative', label: 'Generative', angle: 308.57 },
] as const;

export type PrincipleKey = keyof ConstitutionScores;

// =============================================================================
// Evidence Types (for Witness primitive)
// =============================================================================

export type EvidenceTier = "confident" | "uncertain" | "speculative";

export interface Evidence {
  id: string;
  content: string;
  confidence: number;
  source: string;
}

export interface CausalEdge {
  from: string;
  to: string;
  influence: number;
}

export interface EvidenceCorpus {
  tier: EvidenceTier;
  items: Evidence[];
  causalGraph: CausalEdge[];
}
