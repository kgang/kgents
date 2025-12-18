/**
 * TopologyEdge3D - Universal 3D edge primitive
 *
 * The core building block for both Brain (CrystalVine) and Gestalt (VineEdge).
 * Renders organic curved connections between nodes with flow animation.
 *
 * Philosophy:
 *   "Connections are not wires—they are rivers of meaning."
 *
 * This component unifies ~80% duplicated code between CrystalVine and VineEdge.
 *
 * @see plans/3d-projection-consolidation.md
 * @see spec/protocols/projection.md
 */

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Line } from '@react-three/drei';
import * as THREE from 'three';

import type { ThemePalette } from './themes/types';
import { EDGE, FLOW_PARTICLES } from './animation';
import { FlowParticles } from './FlowParticle';

// =============================================================================
// Types
// =============================================================================

export interface TopologyEdge3DProps {
  /** Source position [x, y, z] */
  source: [number, number, number];

  /** Target position [x, y, z] */
  target: [number, number, number];

  /** Theme configuration */
  theme: ThemePalette;

  /** Connection strength (0-1) - affects opacity */
  strength?: number;

  /** Whether this edge is connected to selected node */
  isActive?: boolean;

  /** Whether this edge represents a violation/error */
  isViolation?: boolean;

  /** Whether this edge should be dimmed (background state) */
  isDimmed?: boolean;

  /** Whether to show flow particles */
  showFlowParticles?: boolean;

  /** Whether animation is enabled */
  animationEnabled?: boolean;

  /** Curve intensity (0 = straight, higher = more curved) */
  curveIntensity?: number;

  /** Line width in normal state */
  baseWidth?: number;

  /** Line width when active */
  activeWidth?: number;

  /** Line width when dimmed */
  dimmedWidth?: number;

  /** Number of curve segments (more = smoother) */
  curveSegments?: number;
}

// =============================================================================
// Curve Calculation
// =============================================================================

/**
 * Calculate a natural curve control point between source and target.
 * Creates organic, non-straight paths.
 */
function calculateCurveControl(
  source: THREE.Vector3,
  target: THREE.Vector3,
  intensity: number
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
  segments: number
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
// Glow Effect Sub-Component
// =============================================================================

interface EdgeGlowProps {
  curvePoints: THREE.Vector3[];
  color: string;
  width: number;
  intensity: number;
}

function EdgeGlow({ curvePoints, color, width, intensity }: EdgeGlowProps) {
  const opacityRef = useRef(intensity);

  useFrame(({ clock }) => {
    // Subtle pulse
    const time = clock.getElapsedTime();
    opacityRef.current = intensity + Math.sin(time * EDGE.glowPulseSpeed) * 0.1;
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
// Violation Thorns (Forest-specific, but exposed as option)
// =============================================================================

interface ViolationThornsProps {
  curvePoints: THREE.Vector3[];
  color: string;
}

function ViolationThorns({ curvePoints, color }: ViolationThornsProps) {
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

/**
 * TopologyEdge3D - Generic 3D edge that works with any theme.
 *
 * This is the unified primitive that replaces both CrystalVine and VineEdge.
 * The visual identity comes from the theme; the behavior is universal.
 */
export function TopologyEdge3D({
  source,
  target,
  theme,
  strength = 0.5,
  isActive = false,
  isViolation = false,
  isDimmed = false,
  showFlowParticles = true,
  animationEnabled = true,
  curveIntensity = EDGE.curveIntensity,
  baseWidth = 1.5,
  activeWidth = 2.5,
  dimmedWidth = 0.8,
  curveSegments = EDGE.curveSegments,
}: TopologyEdge3DProps) {
  // Convert to vectors
  const sourceVec = useMemo(() => new THREE.Vector3(...source), [source]);
  const targetVec = useMemo(() => new THREE.Vector3(...target), [target]);

  // Calculate curve control point
  const controlVec = useMemo(
    () => calculateCurveControl(sourceVec, targetVec, curveIntensity),
    [sourceVec, targetVec, curveIntensity]
  );

  // Generate curve points for rendering
  const curvePoints = useMemo(
    () => generateCurvePoints(sourceVec, controlVec, targetVec, curveSegments),
    [sourceVec, controlVec, targetVec, curveSegments]
  );

  // Determine colors based on state
  const colors = useMemo(() => {
    if (isViolation && theme.edgeColors.violation) {
      return {
        base: theme.edgeColors.violation,
        highlight: theme.edgeColors.violation,
        glow: theme.edgeColors.violation,
      };
    }
    return theme.edgeColors;
  }, [isViolation, theme.edgeColors]);

  // Calculate width based on state
  const width = useMemo(() => {
    if (isDimmed) return dimmedWidth;
    if (isActive) return activeWidth;
    // Strength affects width for non-active edges
    return baseWidth * (0.8 + strength * 0.4);
  }, [isDimmed, isActive, baseWidth, activeWidth, dimmedWidth, strength]);

  // Calculate opacity based on state and strength
  const opacity = useMemo(() => {
    if (isDimmed) return 0.12;
    if (isActive) return 0.75 + strength * 0.15;
    // Base opacity scales with strength
    return 0.2 + strength * 0.35;
  }, [isDimmed, isActive, strength]);

  // Color selection
  const color = useMemo(() => {
    if (isActive) return colors.highlight;
    return colors.base;
  }, [isActive, colors]);

  // Whether to show flow particles
  const showFlow = animationEnabled && showFlowParticles && isActive && !isDimmed;

  // Particle color
  const particleColor = isViolation ? theme.particleColors.active : theme.particleColors.normal;

  return (
    <group>
      {/* Glow effect for active edges */}
      {isActive && !isDimmed && (
        <EdgeGlow
          curvePoints={curvePoints}
          color={colors.glow}
          width={width}
          intensity={0.25 + strength * 0.15}
        />
      )}

      {/* Main line */}
      <Line points={curvePoints} color={color} lineWidth={width} transparent opacity={opacity} />

      {/* Violation thorns (if violation and has violation color) */}
      {isViolation && !isDimmed && theme.edgeColors.violation && (
        <ViolationThorns curvePoints={curvePoints} color={theme.edgeColors.violation} />
      )}

      {/* Flow particles */}
      {showFlow && (
        <FlowParticles
          curvePoints={curvePoints}
          color={particleColor}
          count={FLOW_PARTICLES.count}
          speed={FLOW_PARTICLES.speed}
          size={FLOW_PARTICLES.size}
        />
      )}
    </group>
  );
}

// =============================================================================
// Smart Edge (Auto-selects rendering complexity)
// =============================================================================

export interface SmartTopologyEdge3DProps extends TopologyEdge3DProps {
  /** Force simple rendering (straight line, no animation) */
  forceSimple?: boolean;
  /** Threshold for using full rendering (based on strength) */
  fullRenderingThreshold?: number;
}

/**
 * Smart edge that automatically adjusts rendering complexity.
 *
 * Uses full TopologyEdge3D when:
 * - Edge is active
 * - Edge is a violation
 * - Edge has high strength (above threshold)
 *
 * Uses simpler rendering otherwise for performance.
 */
export function SmartTopologyEdge3D({
  forceSimple = false,
  fullRenderingThreshold = 0.6,
  ...props
}: SmartTopologyEdge3DProps) {
  const { source, target, strength = 0.5, isActive, isViolation, isDimmed } = props;

  // Always compute simple points (hook must be called unconditionally)
  const simplePoints = useMemo(
    () => [new THREE.Vector3(...source), new THREE.Vector3(...target)],
    [source, target]
  );

  // Use full rendering for important edges
  const useFullRendering = !forceSimple && (isActive || isViolation || strength > fullRenderingThreshold);

  if (!useFullRendering && isDimmed) {
    // Super simple rendering for dimmed, low-importance edges
    return <Line points={simplePoints} color="#2D3748" lineWidth={0.5} transparent opacity={0.08} />;
  }

  return <TopologyEdge3D {...props} />;
}

export default TopologyEdge3D;
