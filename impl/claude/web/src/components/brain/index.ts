/**
 * Brain Components - Living Memory Cartography
 *
 * Components for the Holographic Brain Crown Jewel.
 *
 * Design Philosophy:
 *   "Memory isn't a starfield. It's a living library where crystals
 *   form, connect, and surface when needed."
 *
 * 2D Renaissance (2025-12-18): Three.js components mothballed.
 * See _mothballed/three-visualizers/brain/ for preserved components.
 *
 * @see spec/protocols/2d-renaissance.md - Phase 4: Brain2D
 */

// =============================================================================
// Brain2D Components (2D Renaissance)
// =============================================================================

export { Brain2D } from './Brain2D';
export type { Brain2DProps } from './Brain2D';

export { CrystalTree, groupByCategory } from './CrystalTree';
export type { CrystalTreeProps, CategoryCardProps } from './CrystalTree';

export { CaptureForm } from './CaptureForm';
export type { CaptureFormProps } from './CaptureForm';

export { GhostSurface } from './GhostSurface';
export type { GhostSurfaceProps } from './GhostSurface';

export { CrystalDetail } from './CrystalDetail';
export type { CrystalDetailProps } from './CrystalDetail';

// =============================================================================
// MOTHBALLED (2025-12-18): Three.js visualization components
// Preserved in: _mothballed/three-visualizers/brain/
// - BrainCanvas.tsx (1004 lines)
// - OrganicCrystal.tsx
// - CrystalVine.tsx
// Revival condition: VR/AR projections or 3D memory visualization
// =============================================================================
