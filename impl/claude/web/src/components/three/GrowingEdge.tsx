/**
 * GrowingEdge - Organic edge growth visualization
 *
 * A Three.js component that animates edges growing organically between nodes.
 * Edges don't teleport—they grow from source to target with subtle curves.
 *
 * Philosophy:
 *   "The structure is not designed—it emerges from rules.
 *    We do not design the flower; we design the soil and the season."
 *
 * Usage in kgents:
 * - BrainTopology edge connections
 * - Coalition formation visualization
 * - Knowledge graph building
 *
 * @see impl/claude/agents/i/reactive/animation/growth.py (Python isomorphism)
 * @see impl/claude/web/src/hooks/useGrowthAnimation.ts
 */

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Line } from '@react-three/drei';
import * as THREE from 'three';
import { GROWTH_PRESETS } from '../../types/emergence';

// =============================================================================
// Types
// =============================================================================

export interface GrowingEdgeProps {
  /** Unique edge identifier */
  id: string;
  /** Source position */
  source: [number, number, number];
  /** Target position */
  target: [number, number, number];
  /** Growth progress (0 = none, 1 = complete) */
  progress: number;
  /** Waypoints for organic path */
  waypoints?: Array<[number, number, number]>;
  /** Edge color */
  color?: string;
  /** Edge thickness */
  thickness?: number;
  /** Whether to show growth trail (glowing tip) */
  showTrail?: boolean;
  /** Trail color (defaults to brighter version of color) */
  trailColor?: string;
  /** Trail length as fraction of edge */
  trailLength?: number;
  /** Growth rules preset */
  preset?: keyof typeof GROWTH_PRESETS;
  /** Opacity */
  opacity?: number;
  /** Whether edge is selected */
  selected?: boolean;
  /** Click handler */
  onClick?: () => void;
}

export interface GrowingEdgeGroupProps {
  /** Edges to render */
  edges: Array<{
    id: string;
    source: [number, number, number];
    target: [number, number, number];
    progress: number;
    waypoints?: Array<[number, number, number]>;
  }>;
  /** Shared configuration */
  config?: Partial<Omit<GrowingEdgeProps, 'id' | 'source' | 'target' | 'progress' | 'waypoints'>>;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Generate a smooth curve path from source through waypoints to target.
 */
function generateCurvePath(
  source: THREE.Vector3,
  target: THREE.Vector3,
  waypoints: THREE.Vector3[],
  progress: number,
  segments: number = 32
): THREE.Vector3[] {
  if (progress <= 0) return [source];
  if (waypoints.length === 0) {
    // Direct line
    const end = source.clone().lerp(target, progress);
    return [source, end];
  }

  // Build full path with waypoints
  const allPoints = [source, ...waypoints, target];

  // Create CatmullRom curve for smooth interpolation
  const curve = new THREE.CatmullRomCurve3(allPoints, false, 'centripetal', 0.5);

  // Sample points along the curve up to current progress
  const points: THREE.Vector3[] = [];
  const actualSegments = Math.max(2, Math.ceil(segments * progress));

  for (let i = 0; i <= actualSegments; i++) {
    const t = (i / actualSegments) * progress;
    points.push(curve.getPoint(t));
  }

  return points;
}

/**
 * Generate trail gradient points (glowing growth tip).
 */
function generateTrailPoints(
  path: THREE.Vector3[],
  trailLength: number
): { point: THREE.Vector3; alpha: number }[] {
  if (path.length < 2) return [];

  const result: { point: THREE.Vector3; alpha: number }[] = [];
  const totalPoints = path.length;
  const trailPoints = Math.max(2, Math.ceil(totalPoints * trailLength));

  // Only include trail at the growth front
  const startIndex = Math.max(0, totalPoints - trailPoints);

  for (let i = startIndex; i < totalPoints; i++) {
    // Alpha increases toward the tip
    const normalizedPos = (i - startIndex) / (totalPoints - startIndex - 1);
    const alpha = normalizedPos; // 0 at start of trail, 1 at tip

    result.push({
      point: path[i],
      alpha,
    });
  }

  return result;
}

// =============================================================================
// Main Component
// =============================================================================

export function GrowingEdge({
  source,
  target,
  progress,
  waypoints = [],
  color = '#4a5568',
  thickness = 1,
  showTrail = true,
  trailColor,
  trailLength = 0.15,
  opacity = 0.7,
  selected = false,
  onClick,
}: GrowingEdgeProps) {

  // Convert to Three.js vectors
  const sourceVec = useMemo(() => new THREE.Vector3(...source), [source]);
  const targetVec = useMemo(() => new THREE.Vector3(...target), [target]);
  const waypointVecs = useMemo(
    () => waypoints.map((wp) => new THREE.Vector3(...wp)),
    [waypoints]
  );

  // Generate curve path
  const pathPoints = useMemo(
    () => generateCurvePath(sourceVec, targetVec, waypointVecs, progress),
    [sourceVec, targetVec, waypointVecs, progress]
  );

  // Effective trail color (brighter version of main color by default)
  const effectiveTrailColor = useMemo(() => {
    if (trailColor) return trailColor;
    const baseColor = new THREE.Color(color);
    // Make it brighter for the trail
    return baseColor.offsetHSL(0, 0.2, 0.3).getHexString();
  }, [color, trailColor]);

  // Generate trail points for the glowing tip
  const trailPoints = useMemo(
    () => (showTrail && progress > 0 && progress < 1 ? generateTrailPoints(pathPoints, trailLength) : []),
    [pathPoints, showTrail, progress, trailLength]
  );

  // Don't render if no progress
  if (progress <= 0 || pathPoints.length < 2) {
    return null;
  }

  return (
    <group>
      {/* Main edge line */}
      <Line
        points={pathPoints}
        color={selected ? '#00ffff' : color}
        lineWidth={selected ? thickness * 1.5 : thickness}
        transparent
        opacity={opacity}
        onClick={onClick}
      />

      {/* Growth trail (glowing tip) */}
      {showTrail && trailPoints.length >= 2 && (
        <Line
          points={trailPoints.map((tp) => tp.point)}
          color={`#${effectiveTrailColor}`}
          lineWidth={thickness * 2}
          transparent
          opacity={0.8}
        />
      )}

      {/* Tip glow sphere */}
      {showTrail && progress > 0 && progress < 1 && pathPoints.length > 0 && (
        <mesh position={pathPoints[pathPoints.length - 1]}>
          <sphereGeometry args={[thickness * 0.03, 8, 8]} />
          <meshBasicMaterial
            color={`#${effectiveTrailColor}`}
            transparent
            opacity={0.9}
          />
        </mesh>
      )}
    </group>
  );
}

// =============================================================================
// Group Component (for efficiency with many edges)
// =============================================================================

export function GrowingEdgeGroup({ edges, config = {} }: GrowingEdgeGroupProps) {
  return (
    <group>
      {edges.map((edge) => (
        <GrowingEdge
          key={edge.id}
          id={edge.id}
          source={edge.source}
          target={edge.target}
          progress={edge.progress}
          waypoints={edge.waypoints}
          {...config}
        />
      ))}
    </group>
  );
}

// =============================================================================
// Animated Wrapper (uses internal animation)
// =============================================================================

export interface AnimatedGrowingEdgeProps extends Omit<GrowingEdgeProps, 'progress'> {
  /** Animation duration in ms */
  duration?: number;
  /** Delay before starting in ms */
  delay?: number;
  /** Easing function */
  easing?: 'linear' | 'easeIn' | 'easeOut' | 'easeInOut';
  /** Called when animation completes */
  onComplete?: () => void;
}

export function AnimatedGrowingEdge({
  duration = 1500,
  delay = 0,
  easing = 'easeInOut',
  onComplete,
  ...props
}: AnimatedGrowingEdgeProps) {
  const startTimeRef = useRef<number | null>(null);
  const completedRef = useRef(false);
  const progressRef = useRef(0);
  const [progress, setProgress] = React.useState(0);

  // Easing functions
  const easingFns: Record<string, (t: number) => number> = {
    linear: (t) => t,
    easeIn: (t) => t * t,
    easeOut: (t) => 1 - (1 - t) * (1 - t),
    easeInOut: (t) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2),
  };

  useFrame(({ clock }) => {
    if (completedRef.current) return;

    // Initialize start time
    if (startTimeRef.current === null) {
      startTimeRef.current = clock.elapsedTime * 1000;
    }

    const elapsed = clock.elapsedTime * 1000 - startTimeRef.current - delay;

    if (elapsed < 0) return; // Still in delay

    const rawProgress = Math.min(elapsed / duration, 1);
    const easedProgress = easingFns[easing](rawProgress);

    // Only update if changed significantly
    if (Math.abs(easedProgress - progressRef.current) > 0.005) {
      progressRef.current = easedProgress;
      setProgress(easedProgress);
    }

    // Check for completion
    if (rawProgress >= 1 && !completedRef.current) {
      completedRef.current = true;
      onComplete?.();
    }
  });

  return <GrowingEdge {...props} progress={progress} />;
}

// Import React for AnimatedGrowingEdge useState
import React from 'react';

// =============================================================================
// Exports
// =============================================================================

export default GrowingEdge;
