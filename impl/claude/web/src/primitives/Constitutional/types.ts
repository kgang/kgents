/**
 * Constitutional Types - Shared types for constitutional principle scoring
 *
 * The 7 kgents constitutional principles from spec/principles.md:
 * 1. Tasteful - clear, justified purpose
 * 2. Curated - intentional selection
 * 3. Ethical - augments human capability
 * 4. Joy-Inducing - delight in interaction
 * 5. Composable - morphisms in a category
 * 6. Heterarchical - flux, not hierarchy
 * 7. Generative - spec is compression
 */

// =============================================================================
// Core Types
// =============================================================================

/** Individual principle identifier */
export type PrincipleKey =
  | 'tasteful'
  | 'curated'
  | 'ethical'
  | 'joyInducing'
  | 'composable'
  | 'heterarchical'
  | 'generative';

/** Constitutional principle scores (0-1 range) */
export interface ConstitutionalScores {
  tasteful: number;
  curated: number;
  ethical: number;
  joyInducing: number;
  composable: number;
  heterarchical: number;
  generative: number;
}

/** Principle metadata */
export interface PrincipleMetadata {
  key: PrincipleKey;
  label: string;
  shortLabel: string;
  description: string;
  color: string;
}

// =============================================================================
// Constants
// =============================================================================

/** Principle metadata lookup */
export const PRINCIPLES: Record<PrincipleKey, PrincipleMetadata> = {
  tasteful: {
    key: 'tasteful',
    label: 'Tasteful',
    shortLabel: 'Taste',
    description: 'Clear, justified purpose',
    color: 'var(--color-glow-spore)',
  },
  curated: {
    key: 'curated',
    label: 'Curated',
    shortLabel: 'Curate',
    description: 'Intentional selection',
    color: 'var(--color-life-sage)',
  },
  ethical: {
    key: 'ethical',
    label: 'Ethical',
    shortLabel: 'Ethics',
    description: 'Augments human capability',
    color: 'var(--color-glow-lichen)',
  },
  joyInducing: {
    key: 'joyInducing',
    label: 'Joy-Inducing',
    shortLabel: 'Joy',
    description: 'Delight in interaction',
    color: 'var(--color-glow-amber)',
  },
  composable: {
    key: 'composable',
    label: 'Composable',
    shortLabel: 'Compose',
    description: 'Morphisms in a category',
    color: 'var(--color-life-mint)',
  },
  heterarchical: {
    key: 'heterarchical',
    label: 'Heterarchical',
    shortLabel: 'Hetero',
    description: 'Flux, not hierarchy',
    color: 'var(--color-glow-light)',
  },
  generative: {
    key: 'generative',
    label: 'Generative',
    shortLabel: 'Generate',
    description: 'Spec is compression',
    color: 'var(--color-life-sprout)',
  },
};

/** Principle keys in display order (clockwise from top) */
export const PRINCIPLE_ORDER: PrincipleKey[] = [
  'tasteful',
  'curated',
  'ethical',
  'joyInducing',
  'composable',
  'heterarchical',
  'generative',
];

// =============================================================================
// Score Utilities
// =============================================================================

/** Get score tier (high/medium/low) */
export function getScoreTier(score: number): 'high' | 'medium' | 'low' {
  if (score > 0.8) return 'high';
  if (score >= 0.5) return 'medium';
  return 'low';
}

/** Get score color (green/yellow/red) */
export function getScoreColor(score: number): string {
  const tier = getScoreTier(score);
  switch (tier) {
    case 'high':
      return 'var(--health-healthy)';
    case 'medium':
      return 'var(--health-degraded)';
    case 'low':
      return 'var(--health-critical)';
  }
}

/** Calculate overall constitutional score (average) */
export function calculateOverallScore(scores: ConstitutionalScores): number {
  const values = Object.values(scores);
  return values.reduce((sum, score) => sum + score, 0) / values.length;
}

/** Format score as percentage */
export function formatScore(score: number): string {
  return `${Math.round(score * 100)}%`;
}
