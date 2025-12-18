/**
 * Brain Components - Holographic Memory UI
 *
 * Components for the Holographic Brain Crown Jewel.
 *
 * Design Philosophy:
 *   "Memories are not data points—they are living crystallizations of thought."
 *
 * 2D Renaissance (2025-12-18): Three.js components mothballed.
 * See _mothballed/three-visualizers/brain/ for preserved components.
 *
 * What remains: CrystalDetail - reusable in Brain2D.
 *
 * @see spec/protocols/2d-renaissance.md
 */

// KEEP: CrystalDetail (no Three.js dependency)
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
