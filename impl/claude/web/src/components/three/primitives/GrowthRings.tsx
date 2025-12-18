/**
 * GrowthRings - Tree ring aesthetic for forest theme
 *
 * Renders concentric rings around a node like tree growth rings.
 * Used by Gestalt's OrganicNode to show module size/age.
 *
 * @see plans/3d-projection-consolidation.md
 */

import * as THREE from 'three';
import { GROWTH_RINGS } from './animation';

export interface RingSpec {
  inner: number;
  outer: number;
  opacity: number;
}

export interface GrowthRingsProps {
  /** Ring specifications (inner/outer radius and opacity) */
  rings: RingSpec[];
  /** Ring color */
  color: string;
  /** Additional opacity multiplier (e.g., based on health) */
  opacityMultiplier?: number;
}

/**
 * Growth rings - concentric rings like tree rings.
 * Renders in the XZ plane (rotated 90° around X).
 */
export function GrowthRings({ rings, color, opacityMultiplier = 1 }: GrowthRingsProps) {
  return (
    <group rotation={[Math.PI / 2, 0, 0]}>
      {rings.map((ring, i) => (
        <mesh key={i}>
          <ringGeometry args={[ring.inner, ring.outer, 32]} />
          <meshBasicMaterial
            color={color}
            transparent
            opacity={ring.opacity * opacityMultiplier}
            side={THREE.DoubleSide}
          />
        </mesh>
      ))}
    </group>
  );
}

// =============================================================================
// Ring Generation Helper
// =============================================================================

/**
 * Generate growth ring specs based on base size and count.
 * Uses animation presets for consistent appearance.
 *
 * @param baseSize - Base node size
 * @param ringCount - Number of rings to generate
 */
export function generateRingSpecs(baseSize: number, ringCount: number): RingSpec[] {
  const rings: RingSpec[] = [];
  for (let i = 0; i < ringCount; i++) {
    const innerRadius = baseSize * (1 + i * GROWTH_RINGS.spacing);
    const outerRadius = innerRadius + baseSize * GROWTH_RINGS.thickness;
    // Outer rings are more transparent
    const opacity = GROWTH_RINGS.baseOpacity - i * GROWTH_RINGS.opacityFalloff;
    rings.push({
      inner: innerRadius,
      outer: outerRadius,
      opacity: Math.max(opacity, GROWTH_RINGS.minOpacity),
    });
  }
  return rings;
}

export default GrowthRings;
