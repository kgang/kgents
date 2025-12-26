/**
 * Loss Primitives
 *
 * Universal coherence thermometer components.
 * Loss 0.00 (axiom) → 1.00 (nonsense)
 *
 * Primitives:
 * - LossIndicator: Single loss value display
 * - LossGradient: Navigation by loss (clickable gradient bar)
 * - LossHeatmap: Multiple items colored by loss
 * - WithLoss: HOC/wrapper to add loss indicator to any component
 */

export { LossIndicator } from './LossIndicator';
export type { LossIndicatorProps } from './LossIndicator';

export { LossGradient } from './LossGradient';
export type { LossGradientProps } from './LossGradient';

export { LossHeatmap } from './LossHeatmap';
export type { LossHeatmapProps, LossHeatmapItem } from './LossHeatmap';

export { WithLoss } from './WithLoss';
export type { WithLossProps } from './WithLoss';
