/**
 * Constitutional Primitives - Components for visualizing constitutional principles
 *
 * The 7 kgents constitutional principles:
 * 1. Tasteful - clear, justified purpose
 * 2. Curated - intentional selection
 * 3. Ethical - augments human capability
 * 4. Joy-Inducing - delight in interaction
 * 5. Composable - morphisms in a category
 * 6. Heterarchical - flux, not hierarchy
 * 7. Generative - spec is compression
 *
 * Components:
 * - ConstitutionalRadar: 7-spoke radar chart (hero component)
 * - PrincipleScore: Individual principle badge
 * - AllPrincipleScores: Grid of all principle badges
 * - ConstitutionalSummary: Overall score with optional breakdown
 *
 * Design: STARK biome with tier-based color coding (green/yellow/red)
 */

export { ConstitutionalRadar } from './ConstitutionalRadar';
export type { ConstitutionalRadarProps } from './ConstitutionalRadar';

export { PrincipleScore, AllPrincipleScores } from './PrincipleScore';
export type { PrincipleScoreProps, AllPrincipleScoresProps } from './PrincipleScore';

export { ConstitutionalSummary } from './ConstitutionalSummary';
export type { ConstitutionalSummaryProps } from './ConstitutionalSummary';

export type {
  PrincipleKey,
  ConstitutionalScores,
  PrincipleMetadata,
} from './types';

export {
  PRINCIPLES,
  PRINCIPLE_ORDER,
  getScoreTier,
  getScoreColor,
  calculateOverallScore,
  formatScore,
} from './types';
