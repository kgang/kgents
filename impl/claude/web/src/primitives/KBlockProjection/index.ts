/**
 * KBlockProjection Primitive
 *
 * "The projection is not a view. The projection IS the reality."
 *
 * Universal K-Block renderer with multi-surface projection.
 * Every K-Block can render as graph, feed, chat, portal, genesis, card,
 * inline, diff, or proof—while maintaining identity laws and constitutional coherence.
 *
 * Design: STARK BIOME (90% steel, 10% earned glow)
 *
 * Usage:
 * ```tsx
 * import { KBlockProjection } from '@/primitives/KBlockProjection';
 *
 * <KBlockProjection
 *   kblock={myKBlock}
 *   observer={observerContext}
 *   projection="feed"
 *   onWitness={(mark) => console.log('Witnessed:', mark)}
 *   onNavigateLoss={(direction) => console.log('Navigate:', direction)}
 * />
 * ```
 */

// Main component
export { KBlockProjection } from './KBlockProjection';

// Types
export type {
  KBlock,
  KBlockEdge,
  ToulminProof,
  ObserverContext,
  ProjectionMode,
  WitnessMark,
  ConstitutionalWeights,
  GaloisLoss,
  Contradiction,
  KBlockProjectionProps,
  ProjectionComponentProps,
} from './types';

// Helpers
export {
  calculateGaloisLoss,
  getDefaultConstitutionalWeights,
  getLossColor,
  LAYER_NAMES,
  LAYER_COLORS,
  LOSS_COLORS,
} from './types';

// Individual projection components (for direct use if needed)
export { GraphProjection } from './projections/GraphProjection';
export { FeedProjection } from './projections/FeedProjection';
export { ChatProjection } from './projections/ChatProjection';
export { PortalProjection } from './projections/PortalProjection';
export { GenesisProjection } from './projections/GenesisProjection';
export { CardProjection } from './projections/CardProjection';
export { InlineProjection } from './projections/InlineProjection';
export { DiffProjection } from './projections/DiffProjection';
export { ProofProjection } from './projections/ProofProjection';
