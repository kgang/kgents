/**
 * Type definitions for DP visualization components
 *
 * Mirrors the backend dp_bridge.py structure:
 * - Principle (7 core kgents principles)
 * - PrincipleScore (per-principle evaluation)
 * - ValueScore (aggregated score)
 * - TraceEntry (single step in policy trace)
 * - PolicyTrace (complete solution path)
 */

export enum Principle {
  TASTEFUL = 'TASTEFUL',
  CURATED = 'CURATED',
  ETHICAL = 'ETHICAL',
  JOY_INDUCING = 'JOY_INDUCING',
  COMPOSABLE = 'COMPOSABLE',
  HETERARCHICAL = 'HETERARCHICAL',
  GENERATIVE = 'GENERATIVE',
}

export const PRINCIPLE_LABELS: Record<Principle, string> = {
  [Principle.TASTEFUL]: 'Tasteful',
  [Principle.CURATED]: 'Curated',
  [Principle.ETHICAL]: 'Ethical',
  [Principle.JOY_INDUCING]: 'Joy-Inducing',
  [Principle.COMPOSABLE]: 'Composable',
  [Principle.HETERARCHICAL]: 'Heterarchical',
  [Principle.GENERATIVE]: 'Generative',
};

export const PRINCIPLE_DESCRIPTIONS: Record<Principle, string> = {
  [Principle.TASTEFUL]: 'Clear, justified purpose',
  [Principle.CURATED]: 'Intentional selection',
  [Principle.ETHICAL]: 'Augments, never replaces',
  [Principle.JOY_INDUCING]: 'Delight in interaction',
  [Principle.COMPOSABLE]: 'Morphisms in a category',
  [Principle.HETERARCHICAL]: 'Flux, not hierarchy',
  [Principle.GENERATIVE]: 'Spec as compression',
};

export interface PrincipleScore {
  principle: Principle;
  score: number; // 0.0 to 1.0
  evidence: string;
  weight: number;
  weighted_score: number;
}

export interface ValueScore {
  agent_name: string;
  principle_scores: PrincipleScore[];
  total_score: number;
  min_score: number;
  timestamp: string;
}

export interface TraceEntry {
  state_before: unknown;
  action: string;
  state_after: unknown;
  value: number;
  rationale: string;
  timestamp: string;
}

export interface PolicyTrace {
  value: unknown;
  log: TraceEntry[];
  total_value?: number;
}

export interface ConstitutionHealth {
  overall: number; // 0-1
  per_principle: Record<Principle, number>;
  violations: Array<{
    principle: Principle;
    severity: 'critical' | 'warning' | 'minor';
    description: string;
  }>;
}
