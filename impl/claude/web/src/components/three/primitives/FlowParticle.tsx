/**
 * FlowParticle - Animated particle that travels along edges
 *
 * Creates the sense of data/memory flowing between nodes.
 * Used by both CrystalVine (memory echoes) and VineEdge (dependency flow).
 *
 * @see plans/3d-projection-consolidation.md
 */

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { FLOW_PARTICLES } from './animation';

export interface FlowParticleProps {
  /** Array of points defining the path (typically from a bezier curve) */
  curvePoints: THREE.Vector3[];
  /** Particle color */
  color: string;
  /** Starting offset along the curve (0-1) */
  offset: number;
  /** Movement speed (0-1 progress per second) */
  speed?: number;
  /** Particle radius */
  size?: number;
  /** Particle opacity */
  opacity?: number;
}

/**
 * A single flow particle that travels along a curve path.
 * Multiple particles with different offsets create a flowing effect.
 */
export function FlowParticle({
  curvePoints,
  color,
  offset,
  speed = FLOW_PARTICLES.speed,
  size = FLOW_PARTICLES.size,
  opacity = FLOW_PARTICLES.opacity,
}: FlowParticleProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const progressRef = useRef(offset);

  useFrame((_, delta) => {
    if (!meshRef.current || curvePoints.length < 2) return;

    // Update progress along curve
    progressRef.current += delta * speed;
    if (progressRef.current > 1) {
      progressRef.current = progressRef.current % 1;
    }

    // Find position along curve via linear interpolation between points
    const totalPoints = curvePoints.length - 1;
    const exactIndex = progressRef.current * totalPoints;
    const index = Math.floor(exactIndex);
    const fraction = exactIndex - index;

    const p1 = curvePoints[Math.min(index, totalPoints)];
    const p2 = curvePoints[Math.min(index + 1, totalPoints)];

    meshRef.current.position.lerpVectors(p1, p2, fraction);
  });

  // Initial position based on offset
  const initialPos = useMemo(() => {
    if (curvePoints.length < 2) return new THREE.Vector3();
    const index = Math.floor(offset * (curvePoints.length - 1));
    return curvePoints[index] || curvePoints[0];
  }, [curvePoints, offset]);

  return (
    <mesh ref={meshRef} position={initialPos}>
      <sphereGeometry args={[size, FLOW_PARTICLES.segments, FLOW_PARTICLES.segments]} />
      <meshBasicMaterial color={color} transparent opacity={opacity} />
    </mesh>
  );
}

// =============================================================================
// Multi-Particle Helper
// =============================================================================

export interface FlowParticlesProps {
  /** Array of points defining the path */
  curvePoints: THREE.Vector3[];
  /** Particle color */
  color: string;
  /** Number of particles (defaults to animation preset) */
  count?: number;
  /** Movement speed */
  speed?: number;
  /** Particle radius */
  size?: number;
}

/**
 * Renders multiple flow particles evenly distributed along a curve.
 * Convenience wrapper for common use case.
 */
export function FlowParticles({
  curvePoints,
  color,
  count = FLOW_PARTICLES.count,
  speed,
  size,
}: FlowParticlesProps) {
  // Generate evenly distributed offsets
  const offsets = useMemo(
    () => Array.from({ length: count }, (_, i) => i / count),
    [count]
  );

  return (
    <>
      {offsets.map((offset, i) => (
        <FlowParticle
          key={i}
          curvePoints={curvePoints}
          color={color}
          offset={offset}
          speed={speed}
          size={size}
        />
      ))}
    </>
  );
}

export default FlowParticle;
