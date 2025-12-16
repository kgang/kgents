/**
 * Three.js components for kgents 3D visualizations.
 *
 * @see plans/3d-visual-clarity.md
 */

export { SceneLighting, ShadowPlane } from './SceneLighting';
export type { SceneLightingProps, ShadowPlaneProps } from './SceneLighting';

// Emergence visualization components
export { CymaticsField, CoalitionCymaticsField } from './CymaticsField';
export type { CymaticsFieldProps } from './CymaticsField';

export { GrowingEdge, AnimatedGrowingEdge } from './GrowingEdge';
export type { GrowingEdgeProps, AnimatedGrowingEdgeProps } from './GrowingEdge';

// Pattern sampler for design exploration
export { PatternTile, PATTERN_PRESETS, PatternMaterials } from './CymaticsSampler';
export type { PatternConfig, PatternFamily, PatternTileProps } from './CymaticsSampler';
