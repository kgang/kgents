/**
 * SelectionRing - Reusable selection indicator for 3D nodes
 *
 * A gentle ring that appears around selected nodes.
 * Works with any theme - takes color as a prop.
 *
 * @see plans/3d-projection-consolidation.md
 */

import * as THREE from 'three';
import { SELECTION } from './animation';

export interface SelectionRingProps {
  /** Base node size (ring scales relative to this) */
  size: number;
  /** Ring color */
  color: string;
  /** Opacity override (defaults to animation preset) */
  opacity?: number;
  /** Inner radius multiplier (default: 1.4 × size) */
  innerMultiplier?: number;
  /** Outer radius multiplier (default: 1.6 × size) */
  outerMultiplier?: number;
}

/**
 * Selection ring - appears around selected nodes.
 * Renders as a flat ring in the XZ plane (rotated 90° around X).
 */
export function SelectionRing({
  size,
  color,
  opacity = SELECTION.ringOpacity,
  innerMultiplier = 1.4,
  outerMultiplier = 1.6,
}: SelectionRingProps) {
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

export default SelectionRing;
