/**
 * CrystalVine - Organic Memory Connections
 *
 * Transforms the static lines into organic vine-like connections between crystals.
 * Connections are living tendrils that:
 * - Grow with subtle curves (not straight lines)
 * - Show flow direction with animated particles
 * - Glow when active (connected to selected crystal)
 * - Opacity based on similarity (stronger = more visible)
 *
 * Philosophy:
 *   "Memories are not linked by wires—they are connected by echoes."
 *
 * @see docs/creative/emergence-principles.md
 * @see impl/claude/web/src/components/gestalt/VineEdge.tsx
 */

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Line } from '@react-three/drei';
import * as THREE from 'three';

// =============================================================================
// Constants - Vine Palette
// =============================================================================

/** Connection colors for different states */
const VINE_PALETTE = {
  // Normal connections - subtle cyan gradient
  normal: {
    base: '#334155',       // Slate - subtle base
    highlight: '#06B6D4',  // Cyan when active
    glow: '#22D3EE',       // Bright cyan glow
  },
  // Strong connections (high similarity)
  strong: {
    base: '#475569',       // Brighter slate
    highlight: '#8B5CF6',  // Purple when active
    glow: '#A78BFA',       // Bright purple glow
  },
  // Particle colors
  particle: {
    normal: '#67E8F9',     // Light cyan
    strong: '#C4B5FD',     // Light purple
  },
} as const;

/** Edge width by state */
const VINE_WIDTH = {
  normal: 1.0,          // Base width
  active: 2.0,          // Highlighted
  dimmed: 0.5,          // Background edges
  strong: 1.5,          // High similarity
} as const;

/** Animation configuration */
const VINE_ANIMATION = {
  flowSpeed: 0.4,           // Particle flow speed
  particleCount: 3,         // Particles per active edge
  particleSize: 0.02,       // Particle radius
  curveIntensity: 0.12,     // How curved the vines are
  glowPulseSpeed: 2.0,      // Pulse rate for glow
} as const;

// =============================================================================
// Types
// =============================================================================

export interface CrystalVineProps {
  /** Source position [x, y, z] */
  source: [number, number, number];
  /** Target position [x, y, z] */
  target: [number, number, number];
  /** Similarity score (0-1) - stronger = more visible */
  similarity: number;
  /** Whether this edge is connected to selected crystal */
  isActive?: boolean;
  /** Whether animation is enabled */
  animationEnabled?: boolean;
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
  segments: number = 16
): THREE.Vector3[] {
  const points: THREE.Vector3[] = [];
  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    const point = new THREE.Vector3();

    // Quadratic bezier formula
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
 * Flow particle that travels along the vine (memory echo).
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
        opacity={0.8}
      />
    </mesh>
  );
}

/**
 * Glow aura for active/highlighted edges.
 */
function VineGlow({
  curvePoints,
  color,
  width,
  similarity,
}: {
  curvePoints: THREE.Vector3[];
  color: string;
  width: number;
  similarity: number;
}) {
  const opacityRef = useRef(0.3);

  useFrame(({ clock }) => {
    // Subtle pulse based on similarity
    const time = clock.getElapsedTime();
    opacityRef.current = 0.2 + similarity * 0.2 + Math.sin(time * VINE_ANIMATION.glowPulseSpeed) * 0.1;
  });

  return (
    <Line
      points={curvePoints}
      color={color}
      lineWidth={width * 2.5}
      transparent
      opacity={opacityRef.current}
    />
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function CrystalVine({
  source,
  target,
  similarity,
  isActive = false,
  animationEnabled = true,
  isDimmed = false,
}: CrystalVineProps) {
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

  // Determine if this is a strong connection
  const isStrong = similarity > 0.7;
  const palette = isStrong ? VINE_PALETTE.strong : VINE_PALETTE.normal;

  // Calculate width based on state and similarity
  const width = useMemo(() => {
    if (isDimmed) return VINE_WIDTH.dimmed;
    if (isActive) return VINE_WIDTH.active;
    if (isStrong) return VINE_WIDTH.strong;
    return VINE_WIDTH.normal;
  }, [isDimmed, isActive, isStrong]);

  // Calculate opacity based on similarity (stronger = more visible)
  const opacity = useMemo(() => {
    if (isDimmed) return 0.1;
    if (isActive) return 0.7 + similarity * 0.2;
    // Base opacity scales with similarity
    return 0.15 + similarity * 0.35;
  }, [isDimmed, isActive, similarity]);

  // Color selection
  const color = useMemo(() => {
    if (isActive) return palette.highlight;
    return palette.base;
  }, [isActive, palette]);

  // Whether to show flow particles (memory echoes)
  const showFlow = animationEnabled && isActive && !isDimmed;

  // Particle offsets (evenly distributed)
  const particleOffsets = useMemo(() => {
    return Array.from(
      { length: VINE_ANIMATION.particleCount },
      (_, i) => i / VINE_ANIMATION.particleCount
    );
  }, []);

  // Particle color based on connection type
  const particleColor = isStrong ? VINE_PALETTE.particle.strong : VINE_PALETTE.particle.normal;

  return (
    <group>
      {/* Glow effect for active edges */}
      {isActive && !isDimmed && (
        <VineGlow
          curvePoints={curvePoints}
          color={palette.glow}
          width={width}
          similarity={similarity}
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

      {/* Flow particles (memory echoes) */}
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
// Smart Vine (Auto-selects rendering complexity)
// =============================================================================

export interface SmartCrystalVineProps extends CrystalVineProps {
  /** Force simple rendering */
  forceSimple?: boolean;
}

/**
 * Smart crystal vine that automatically adjusts rendering complexity.
 *
 * Uses full CrystalVine when:
 * - Edge is active
 * - Edge has high similarity
 *
 * Uses simpler rendering otherwise for performance.
 */
export function SmartCrystalVine({
  source,
  target,
  similarity,
  isActive = false,
  animationEnabled = true,
  isDimmed = false,
  forceSimple = false,
}: SmartCrystalVineProps) {
  // Use full rendering for important edges
  const useFullRendering = !forceSimple && (isActive || similarity > 0.6);

  if (!useFullRendering && isDimmed) {
    // Super simple rendering for dimmed, low-similarity edges
    const points = useMemo(
      () => [new THREE.Vector3(...source), new THREE.Vector3(...target)],
      [source, target]
    );

    return (
      <Line
        points={points}
        color="#1F2937"
        lineWidth={VINE_WIDTH.dimmed}
        transparent
        opacity={0.08}
      />
    );
  }

  return (
    <CrystalVine
      source={source}
      target={target}
      similarity={similarity}
      isActive={isActive}
      animationEnabled={animationEnabled}
      isDimmed={isDimmed}
    />
  );
}

export default CrystalVine;
