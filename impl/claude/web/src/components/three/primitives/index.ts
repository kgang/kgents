/**
 * 3D Projection Primitives
 *
 * Shared building blocks for Three.js visualizations.
 * Used by both Brain (crystal theme) and Gestalt (forest theme).
 *
 * Architecture:
 *   P[3D] : State × Theme × Quality → Three.js Scene
 *
 * @see plans/3d-projection-consolidation.md
 * @see spec/protocols/projection.md
 */

// =============================================================================
// Core Primitives
// =============================================================================

export { TopologyNode3D } from './TopologyNode3D';
export type { TopologyNode3DProps } from './TopologyNode3D';

export { TopologyEdge3D, SmartTopologyEdge3D } from './TopologyEdge3D';
export type { TopologyEdge3DProps, SmartTopologyEdge3DProps } from './TopologyEdge3D';

// =============================================================================
// Supporting Primitives
// =============================================================================

export { SelectionRing } from './SelectionRing';
export type { SelectionRingProps } from './SelectionRing';

export { HoverRing } from './HoverRing';
export type { HoverRingProps } from './HoverRing';

export { FlowParticle, FlowParticles } from './FlowParticle';
export type { FlowParticleProps, FlowParticlesProps } from './FlowParticle';

export { NodeLabel3D } from './NodeLabel3D';
export type { NodeLabel3DProps } from './NodeLabel3D';

export { GrowthRings, generateRingSpecs } from './GrowthRings';
export type { GrowthRingsProps, RingSpec } from './GrowthRings';

// =============================================================================
// Animation
// =============================================================================

export {
  ANIMATION_PRESETS,
  BREATHING,
  FLOW_PARTICLES,
  HOVER,
  SELECTION,
  EDGE,
  VIOLATION,
  GROWTH_RINGS,
  PERFORMANCE_TIERS,
} from './animation';
export type { PerformanceTier } from './animation';

// =============================================================================
// Level of Detail (LOD)
// =============================================================================

export { useLOD, LODAwareNode, getEdgeLOD } from './useLOD';
export type {
  LODLevel,
  NodeLOD,
  LODSettings,
  UseLODOptions,
  LODAwareNodeProps,
} from './useLOD';

// =============================================================================
// Touch & Accessibility
// =============================================================================

export {
  useTouchDevice,
  useTouchTargetMultiplier,
  useGesture,
  TOUCH_DEFAULTS,
} from './useTouch';
export type { TouchConfig, GestureResult } from './useTouch';

// =============================================================================
// Themes
// =============================================================================

export * from './themes';
