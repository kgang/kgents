/**
 * VineEdge - Organic Growing Connections
 *
 * Transforms the static, barely-visible lines into organic vine connections.
 * Edges are living tendrils that:
 * - Grow with subtle curves (not straight lines)
 * - Have visible thickness and personality
 * - Show flow direction with animated particles
 * - Glow when active (connected to selected node)
 *
 * Philosophy:
 *   "Dependencies are not wires—they are roots reaching for water."
 *
 * @see docs/creative/emergence-principles.md
 * @see plans/_continuations/gestalt-sprint3.md
 */

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Line } from '@react-three/drei';
import * as THREE from 'three';

// =============================================================================
// Constants - Vine Palette
// =============================================================================

/** Vine colors for different states */
const VINE_PALETTE = {
  // Normal dependencies - forest browns/greens
  normal: {
    base: '#4A5568',      // Muted gray-green
    highlight: '#68D391', // Bright green when active
    glow: '#48BB78',      // Medium green glow
  },
  // Violations - thorny red
  violation: {
    base: '#C53030',      // Dark red
    highlight: '#FC8181', // Light red when active
    glow: '#F56565',      // Red glow
    thorn: '#991B1B',     // Deep thorn red
  },
  // Flow particles
  particle: {
    normal: '#9AE6B4',    // Light green
    violation: '#FEB2B2', // Light red
  },
} as const;

/** Edge width by state */
const VINE_WIDTH = {
  normal: 1.5,          // Visible but not heavy
  active: 2.5,          // Clearly highlighted
  dimmed: 0.8,          // Background edges
  violation: 2.0,       // Violations are thick
  violationActive: 3.0, // Active violations very visible
} as const;

/** Animation configuration */
const VINE_ANIMATION = {
  flowSpeed: 0.6,           // Particle flow speed
  pulseFrequency: 2.0,      // Pulse rate for violations
  particleCount: 4,         // Particles per active edge
  particleSize: 0.03,       // Particle radius
  curveIntensity: 0.15,     // How curved the vines are (0 = straight)
  breatheIntensity: 0.02,   // Subtle breathing amplitude
} as const;

// =============================================================================
// Types
// =============================================================================

export interface VineEdgeProps {
  /** Source position [x, y, z] */
  source: [number, number, number];
  /** Target position [x, y, z] */
  target: [number, number, number];
  /** Whether this edge represents a violation */
  isViolation?: boolean;
  /** Whether animation is enabled globally */
  animationEnabled?: boolean;
  /** Whether this edge is connected to selected node */
  isActive?: boolean;
  /** Whether this edge should be highlighted */
  isHighlighted?: boolean;
  /** Whether this edge should be dimmed */
  isDimmed?: boolean;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Calculate a natural curve control point between source and target.
 * Creates organic, non-straight paths.
 */
function calculateCurveControl(
  source: THREE.Vector3,
  target: THREE.Vector3,
  intensity: number = VINE_ANIMATION.curveIntensity
): THREE.Vector3 {
  const midpoint = source.clone().add(target).multiplyScalar(0.5);

  // Add perpendicular offset for curve
  const direction = target.clone().sub(source).normalize();
  const perpendicular = new THREE.Vector3(-direction.y, direction.x, direction.z * 0.5);

  // Use source/target positions to create consistent but varied curves
  const hash = Math.sin(source.x * 12.9898 + target.y * 78.233) * 43758.5453;
  const offset = (hash % 1) * 2 - 1; // -1 to 1

  const distance = source.distanceTo(target);
  const curveAmount = distance * intensity * offset;

  return midpoint.add(perpendicular.multiplyScalar(curveAmount));
}

/**
 * Generate points along a quadratic bezier curve.
 */
function generateCurvePoints(
  source: THREE.Vector3,
  control: THREE.Vector3,
  target: THREE.Vector3,
  segments: number = 20
): THREE.Vector3[] {
  const points: THREE.Vector3[] = [];
  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    const point = new THREE.Vector3();

    // Quadratic bezier formula: B(t) = (1-t)^2*P0 + 2*(1-t)*t*P1 + t^2*P2
    const mt = 1 - t;
    point.x = mt * mt * source.x + 2 * mt * t * control.x + t * t * target.x;
    point.y = mt * mt * source.y + 2 * mt * t * control.y + t * t * target.y;
    point.z = mt * mt * source.z + 2 * mt * t * control.z + t * t * target.z;

    points.push(point);
  }
  return points;
}

// =============================================================================
// Sub-Components
// =============================================================================

/**
 * Flow particle that travels along the vine
 */
function FlowParticle({
  curvePoints,
  color,
  offset,
  speed,
  size,
}: {
  curvePoints: THREE.Vector3[];
  color: string;
  offset: number;
  speed: number;
  size: number;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const progressRef = useRef(offset);

  useFrame((_, delta) => {
    if (!meshRef.current || curvePoints.length < 2) return;

    // Update progress along curve
    progressRef.current += delta * speed;
    if (progressRef.current > 1) {
      progressRef.current = progressRef.current % 1;
    }

    // Find position along curve
    const totalPoints = curvePoints.length - 1;
    const exactIndex = progressRef.current * totalPoints;
    const index = Math.floor(exactIndex);
    const fraction = exactIndex - index;

    const p1 = curvePoints[Math.min(index, totalPoints)];
    const p2 = curvePoints[Math.min(index + 1, totalPoints)];

    meshRef.current.position.lerpVectors(p1, p2, fraction);
  });

  // Initial position
  const initialPos = useMemo(() => {
    if (curvePoints.length < 2) return new THREE.Vector3();
    const index = Math.floor(offset * (curvePoints.length - 1));
    return curvePoints[index] || curvePoints[0];
  }, [curvePoints, offset]);

  return (
    <mesh ref={meshRef} position={initialPos}>
      <sphereGeometry args={[size, 8, 8]} />
      <meshBasicMaterial
        color={color}
        transparent
        opacity={0.9}
      />
    </mesh>
  );
}

/**
 * Glow aura for active/highlighted edges
 */
function VineGlow({
  curvePoints,
  color,
  width,
  intensity,
}: {
  curvePoints: THREE.Vector3[];
  color: string;
  width: number;
  intensity: number;
}) {
  const opacityRef = useRef(intensity);

  useFrame(({ clock }) => {
    // Subtle pulse
    const time = clock.getElapsedTime();
    opacityRef.current = intensity + Math.sin(time * 3) * 0.1;
  });

  return (
    <Line
      points={curvePoints}
      color={color}
      lineWidth={width * 2}
      transparent
      opacity={opacityRef.current}
    />
  );
}

/**
 * Violation thorns - small spikes on violation edges
 */
function ViolationThorns({
  curvePoints,
  color,
}: {
  curvePoints: THREE.Vector3[];
  color: string;
}) {
  // Place thorns at intervals along the curve
  const thornPositions = useMemo(() => {
    const positions: THREE.Vector3[] = [];
    const thornCount = Math.min(Math.floor(curvePoints.length / 5), 4);
    for (let i = 1; i <= thornCount; i++) {
      const index = Math.floor((i / (thornCount + 1)) * curvePoints.length);
      if (curvePoints[index]) {
        positions.push(curvePoints[index]);
      }
    }
    return positions;
  }, [curvePoints]);

  return (
    <>
      {thornPositions.map((pos, i) => (
        <mesh key={i} position={pos}>
          <tetrahedronGeometry args={[0.04, 0]} />
          <meshBasicMaterial color={color} transparent opacity={0.7} />
        </mesh>
      ))}
    </>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function VineEdge({
  source,
  target,
  isViolation = false,
  animationEnabled = true,
  isActive = false,
  isHighlighted = false,
  isDimmed = false,
}: VineEdgeProps) {
  // Convert to vectors
  const sourceVec = useMemo(() => new THREE.Vector3(...source), [source]);
  const targetVec = useMemo(() => new THREE.Vector3(...target), [target]);

  // Calculate curve control point
  const controlVec = useMemo(
    () => calculateCurveControl(sourceVec, targetVec),
    [sourceVec, targetVec]
  );

  // Generate curve points for rendering
  const curvePoints = useMemo(
    () => generateCurvePoints(sourceVec, controlVec, targetVec),
    [sourceVec, controlVec, targetVec]
  );

  // Determine visual state
  const palette = isViolation ? VINE_PALETTE.violation : VINE_PALETTE.normal;

  // Calculate width
  const width = useMemo(() => {
    if (isDimmed) return VINE_WIDTH.dimmed;
    if (isViolation) {
      return isActive || isHighlighted ? VINE_WIDTH.violationActive : VINE_WIDTH.violation;
    }
    return isActive || isHighlighted ? VINE_WIDTH.active : VINE_WIDTH.normal;
  }, [isDimmed, isViolation, isActive, isHighlighted]);

  // Calculate opacity
  const opacity = useMemo(() => {
    if (isDimmed) return 0.15;
    if (isActive || isHighlighted) return 0.85;
    return isViolation ? 0.7 : 0.45;
  }, [isDimmed, isActive, isHighlighted, isViolation]);

  // Color selection
  const color = useMemo(() => {
    if (isActive || isHighlighted) return palette.highlight;
    return palette.base;
  }, [isActive, isHighlighted, palette]);

  // Whether to show flow particles
  const showFlow = animationEnabled && (isActive || isHighlighted) && !isDimmed;

  // Particle offsets (evenly distributed)
  const particleOffsets = useMemo(() => {
    return Array.from(
      { length: VINE_ANIMATION.particleCount },
      (_, i) => i / VINE_ANIMATION.particleCount
    );
  }, []);

  // Particle color
  const particleColor = isViolation ? VINE_PALETTE.particle.violation : VINE_PALETTE.particle.normal;

  return (
    <group>
      {/* Glow effect for active/highlighted edges */}
      {(isActive || isHighlighted) && !isDimmed && (
        <VineGlow
          curvePoints={curvePoints}
          color={palette.glow}
          width={width}
          intensity={0.3}
        />
      )}

      {/* Main vine line */}
      <Line
        points={curvePoints}
        color={color}
        lineWidth={width}
        transparent
        opacity={opacity}
      />

      {/* Violation thorns */}
      {isViolation && !isDimmed && (
        <ViolationThorns
          curvePoints={curvePoints}
          color={VINE_PALETTE.violation.thorn}
        />
      )}

      {/* Flow particles */}
      {showFlow &&
        particleOffsets.map((offset, i) => (
          <FlowParticle
            key={i}
            curvePoints={curvePoints}
            color={particleColor}
            offset={offset}
            speed={VINE_ANIMATION.flowSpeed}
            size={VINE_ANIMATION.particleSize}
          />
        ))}
    </group>
  );
}

// =============================================================================
// Smart Vine Edge (Auto-selects rendering complexity)
// =============================================================================

export interface SmartVineEdgeProps extends VineEdgeProps {
  /** Force simple rendering (no curves, no animation) */
  forceSimple?: boolean;
}

/**
 * Smart vine edge that automatically adjusts rendering complexity.
 *
 * Uses full VineEdge when:
 * - Edge is active/highlighted
 * - Edge is a violation
 *
 * Uses simpler rendering otherwise for performance.
 */
export function SmartVineEdge({
  source,
  target,
  isViolation = false,
  animationEnabled = true,
  isActive = false,
  isHighlighted = false,
  isDimmed = false,
  forceSimple = false,
}: SmartVineEdgeProps) {
  // Use full rendering for important edges
  const useFullRendering = !forceSimple && (isActive || isHighlighted || isViolation);

  if (!useFullRendering && isDimmed) {
    // Super simple rendering for dimmed, unimportant edges
    const points = useMemo(
      () => [new THREE.Vector3(...source), new THREE.Vector3(...target)],
      [source, target]
    );

    return (
      <Line
        points={points}
        color="#3D4852"
        lineWidth={VINE_WIDTH.dimmed}
        transparent
        opacity={0.12}
      />
    );
  }

  return (
    <VineEdge
      source={source}
      target={target}
      isViolation={isViolation}
      animationEnabled={animationEnabled}
      isActive={isActive}
      isHighlighted={isHighlighted}
      isDimmed={isDimmed}
    />
  );
}

export default VineEdge;
