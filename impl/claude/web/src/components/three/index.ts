/**
 * Three.js components for kgents 3D visualizations.
 *
 * @see plans/3d-visual-clarity.md
 * @see plans/3d-projection-consolidation.md
 */

// =============================================================================
// Primitives (NEW - Unified 3D building blocks)
// =============================================================================

export * from './primitives';

// =============================================================================
// Scene Infrastructure
// =============================================================================

export { SceneLighting, ShadowPlane } from './SceneLighting';
export type { SceneLightingProps, ShadowPlaneProps } from './SceneLighting';

export { SceneEffects } from './SceneEffects';

export { QualitySelector } from './QualitySelector';

// =============================================================================
// Emergence Visualization
// =============================================================================

export { CymaticsField, CoalitionCymaticsField } from './CymaticsField';
export type { CymaticsFieldProps } from './CymaticsField';

export { GrowingEdge, AnimatedGrowingEdge } from './GrowingEdge';
export type { GrowingEdgeProps, AnimatedGrowingEdgeProps } from './GrowingEdge';

// Pattern sampler for design exploration
export { PatternTile, PATTERN_PRESETS, PatternMaterials } from './CymaticsSampler';
export type { PatternConfig, PatternFamily, PatternTileProps } from './CymaticsSampler';
