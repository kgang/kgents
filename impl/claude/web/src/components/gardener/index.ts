/**
 * Gardener Components - 2D Renaissance Edition
 *
 * Unified garden + session visualization with Living Earth aesthetic.
 * Replaces separate GardenVisualization and GardenerVisualization.
 *
 * @see spec/protocols/2d-renaissance.md - Phase 2: Gardener2D
 * @see spec/protocols/os-shell.md - Gallery Primitive Reliance
 */

// =============================================================================
// Main Component (2D Renaissance)
// =============================================================================

export { Gardener2D } from './Gardener2D';
export type { Gardener2DProps } from './Gardener2D';

// =============================================================================
// Sub-Components
// =============================================================================

export { SeasonOrb, SeasonBadge2D } from './SeasonOrb';
export type { SeasonOrbProps } from './SeasonOrb';

export { PlotTile } from './PlotTile';
export type { PlotTileProps } from './PlotTile';

export { GestureStream, GestureList } from './GestureStream';
export type { GestureStreamProps } from './GestureStream';

export { SessionPolynomial } from './SessionPolynomial';
export type { SessionPolynomialProps } from './SessionPolynomial';

export { TendingPalette } from './TendingPalette';
export type { TendingPaletteProps } from './TendingPalette';

export { TransitionSuggester } from './TransitionSuggester';
export type { TransitionSuggesterProps } from './TransitionSuggester';

export { NurseryBed } from './NurseryBed';
export type { NurseryBedProps } from './NurseryBed';

// =============================================================================
// Legacy Components (kept for backward compatibility)
// =============================================================================

export { GardenerVisualization } from './GardenerVisualization';
export type { GardenerVisualizationProps } from './GardenerVisualization';
