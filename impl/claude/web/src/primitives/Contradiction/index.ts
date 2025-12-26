/**
 * Contradiction Primitive
 *
 * "Contradictions aren't bugs—they're opportunities for synthesis."
 *
 * Three components for visualizing and resolving contradictions:
 * 1. ContradictionBadge — Lightning bolt indicator
 * 2. ContradictionPolaroid — Side-by-side comparison
 * 3. ResolutionPanel — Five resolution strategies
 *
 * Philosophy:
 * - Make tension visible
 * - Make synthesis inviting
 * - Productive contradictions > forced consistency
 */

export { ContradictionBadge } from './ContradictionBadge';
export { ContradictionPolaroid } from './ContradictionPolaroid';
export { ResolutionPanel } from './ResolutionPanel';

export type {
  ContradictionBadgeProps,
  ContradictionSeverity,
} from './ContradictionBadge';

export type {
  ContradictionPolaroidProps,
  ContradictionType,
} from './ContradictionPolaroid';

export type {
  ResolutionPanelProps,
} from './ResolutionPanel';

export type {
  ResolutionStrategy,
  Contradiction,
} from './types';
