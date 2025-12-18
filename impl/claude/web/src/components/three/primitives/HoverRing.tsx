/**
 * HoverRing - Reusable hover indicator for 3D nodes
 *
 * A softer ring that appears when hovering over nodes.
 * Slightly smaller than selection ring to create visual hierarchy.
 *
 * @see plans/3d-projection-consolidation.md
 */

import * as THREE from 'three';

export interface HoverRingProps {
  /** Base node size (ring scales relative to this) */
  size: number;
  /** Ring color (typically from theme's glow color) */
  color: string;
  /** Opacity (softer than selection) */
  opacity?: number;
  /** Inner radius multiplier (default: 1.2 × size) */
  innerMultiplier?: number;
  /** Outer radius multiplier (default: 1.35 × size) */
  outerMultiplier?: number;
}

/**
 * Hover ring - appears when hovering over nodes.
 * Renders as a flat ring in the XZ plane.
 */
export function HoverRing({
  size,
  color,
  opacity = 0.35,
  innerMultiplier = 1.2,
  outerMultiplier = 1.35,
}: HoverRingProps) {
  return (
    <mesh rotation={[Math.PI / 2, 0, 0]}>
      <ringGeometry args={[size * innerMultiplier, size * outerMultiplier, 32]} />
      <meshBasicMaterial
        color={color}
        transparent
        opacity={opacity}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

export default HoverRing;
