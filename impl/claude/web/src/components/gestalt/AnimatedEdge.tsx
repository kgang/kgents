/**
 * AnimatedEdge - Living Data Flow Visualization
 *
 * Chunk 3: Transform static edges into animated data flows.
 *
 * Features:
 * - Semantic color/width based on edge type
 * - Particle flow animation on selected node's edges
 * - Violation pulse effect (subtle red glow)
 * - Performance optimized (only animate visible/selected edges)
 *
 * @see plans/_continuations/gestalt-visual-showcase-chunk3.md
 */

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Line } from '@react-three/drei';
import * as THREE from 'three';
import {
  getEdgeStyle,
  getHighlightedStyle,
  getDimmedStyle,
  getFlowConfig,
  calculatePulseGlow,
  type EdgeStyle,
  type FlowAnimationConfig,
} from './EdgeStyles';

// =============================================================================
// Types
// =============================================================================

export interface AnimatedEdgeProps {
  /** Source position [x, y, z] */
  source: [number, number, number];
  /** Target position [x, y, z] */
  target: [number, number, number];
  /** Whether this edge represents a violation */
  isViolation?: boolean;
  /** Edge type for semantic styling */
  edgeType?: string;
  /** Whether animation is enabled globally */
  animationEnabled?: boolean;
  /** Whether this edge should be animated (connected to selected node) */
  isActive?: boolean;
  /** Whether this edge should be highlighted */
  isHighlighted?: boolean;
  /** Whether this edge should be dimmed (not in focus) */
  isDimmed?: boolean;
}

interface FlowParticleProps {
  source: THREE.Vector3;
  target: THREE.Vector3;
  config: FlowAnimationConfig;
  color: string;
  offset: number;
  speed: number;
}

// =============================================================================
// Flow Particle Component
// =============================================================================

/**
 * Single particle flowing along an edge.
 * Uses useFrame for smooth animation at 60fps.
 */
function FlowParticle({ source, target, config, color, offset, speed }: FlowParticleProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const progressRef = useRef(offset);

  useFrame((_, delta) => {
    if (!meshRef.current) return;

    // Update progress (loop from 0 to 1)
    progressRef.current += delta * config.baseSpeed * speed;
    if (progressRef.current > 1) {
      progressRef.current = progressRef.current % 1;
    }

    // Lerp position along edge
    const pos = new THREE.Vector3().lerpVectors(source, target, progressRef.current);
    meshRef.current.position.copy(pos);
  });

  // Initial position
  const initialPos = useMemo(
    () => new THREE.Vector3().lerpVectors(source, target, offset),
    [source, target, offset]
  );

  return (
    <mesh ref={meshRef} position={initialPos}>
      <sphereGeometry args={[config.particleRadius, 8, 8]} />
      <meshStandardMaterial
        color={color}
        emissive={config.emissive ? color : undefined}
        emissiveIntensity={config.emissive ? 0.8 : 0}
        transparent
        opacity={0.9}
      />
    </mesh>
  );
}

// =============================================================================
// Violation Glow Component
// =============================================================================

interface ViolationGlowProps {
  source: THREE.Vector3;
  target: THREE.Vector3;
  style: EdgeStyle;
}

/**
 * Pulsing glow effect for violation edges.
 * Creates a subtle red aura that draws attention.
 * Uses wider line with animated opacity for the glow effect.
 */
function ViolationGlow({ source, target, style }: ViolationGlowProps) {
  const opacityRef = useRef(style.glowIntensity || 0.3);

  useFrame(({ clock }) => {
    const time = clock.getElapsedTime();
    opacityRef.current = calculatePulseGlow(time);
  });

  const points = useMemo(() => [source, target], [source, target]);

  return (
    <Line
      points={points}
      color={style.glowColor || style.color}
      lineWidth={style.width * 2.5}
      transparent
      opacity={opacityRef.current}
    />
  );
}

// =============================================================================
// Main AnimatedEdge Component
// =============================================================================

/**
 * Animated edge with semantic styling and particle flow.
 *
 * Performance optimizations:
 * - Particles only rendered when isActive && animationEnabled
 * - Glow only rendered for violations
 * - Static edges use simple Line component
 */
export function AnimatedEdge({
  source,
  target,
  isViolation = false,
  edgeType,
  animationEnabled = true,
  isActive = false,
  isHighlighted = false,
  isDimmed = false,
}: AnimatedEdgeProps) {
  // Calculate style based on state
  const baseStyle = useMemo(() => getEdgeStyle(isViolation, edgeType), [isViolation, edgeType]);

  const style = useMemo(() => {
    if (isHighlighted) return getHighlightedStyle(baseStyle);
    if (isDimmed) return getDimmedStyle(baseStyle);
    return baseStyle;
  }, [baseStyle, isHighlighted, isDimmed]);

  const flowConfig = useMemo(() => getFlowConfig(isViolation), [isViolation]);

  // Convert to THREE.Vector3 for calculations
  const sourceVec = useMemo(() => new THREE.Vector3(...source), [source]);
  const targetVec = useMemo(() => new THREE.Vector3(...target), [target]);

  const points = useMemo(
    () => [new THREE.Vector3(...source), new THREE.Vector3(...target)],
    [source, target]
  );

  // Should we show particles?
  const showParticles = animationEnabled && isActive && style.animated && !isDimmed;

  // Generate particle offsets (spread evenly along edge)
  const particleOffsets = useMemo(() => {
    return Array.from({ length: flowConfig.particleCount }, (_, i) => i / flowConfig.particleCount);
  }, [flowConfig.particleCount]);

  return (
    <group>
      {/* Main edge line */}
      <Line
        points={points}
        color={style.color}
        lineWidth={style.width}
        transparent
        opacity={style.opacity}
        dashed={style.dash}
        dashScale={style.dashArray ? 1 : undefined}
        dashSize={style.dashArray?.[0]}
        gapSize={style.dashArray?.[1]}
      />

      {/* Violation glow effect */}
      {isViolation && !isDimmed && <ViolationGlow source={sourceVec} target={targetVec} style={style} />}

      {/* Flow particles */}
      {showParticles &&
        particleOffsets.map((offset, i) => (
          <FlowParticle
            key={i}
            source={sourceVec}
            target={targetVec}
            config={flowConfig}
            color={style.color}
            offset={offset}
            speed={style.animationSpeed || 1}
          />
        ))}
    </group>
  );
}

// =============================================================================
// Static Edge Component (Performance Fallback)
// =============================================================================

export interface StaticEdgeProps {
  source: [number, number, number];
  target: [number, number, number];
  isViolation?: boolean;
  edgeType?: string;
  isDimmed?: boolean;
}

/**
 * Non-animated edge for maximum performance.
 * Use when animation is disabled or for background edges.
 */
export function StaticEdge({
  source,
  target,
  isViolation = false,
  edgeType,
  isDimmed = false,
}: StaticEdgeProps) {
  const baseStyle = useMemo(() => getEdgeStyle(isViolation, edgeType), [isViolation, edgeType]);
  const style = useMemo(() => (isDimmed ? getDimmedStyle(baseStyle) : baseStyle), [baseStyle, isDimmed]);

  const points = useMemo(
    () => [new THREE.Vector3(...source), new THREE.Vector3(...target)],
    [source, target]
  );

  return (
    <Line
      points={points}
      color={style.color}
      lineWidth={style.width}
      transparent
      opacity={style.opacity}
      dashed={style.dash}
      dashScale={style.dashArray ? 1 : undefined}
      dashSize={style.dashArray?.[0]}
      gapSize={style.dashArray?.[1]}
    />
  );
}

// =============================================================================
// Smart Edge Component (Auto-selects rendering mode)
// =============================================================================

export interface SmartEdgeProps extends AnimatedEdgeProps {
  /** Force static rendering (ignore other animation settings) */
  forceStatic?: boolean;
}

/**
 * Smart edge that automatically chooses rendering mode.
 *
 * Uses AnimatedEdge when:
 * - Animation is enabled AND
 * - Edge is active (connected to selected node) OR is a violation
 *
 * Uses StaticEdge otherwise for performance.
 */
export function SmartEdge({
  source,
  target,
  isViolation = false,
  edgeType,
  animationEnabled = true,
  isActive = false,
  isHighlighted = false,
  isDimmed = false,
  forceStatic = false,
}: SmartEdgeProps) {
  // Decide rendering mode
  const shouldAnimate = !forceStatic && animationEnabled && (isActive || isViolation);

  if (!shouldAnimate) {
    return (
      <StaticEdge source={source} target={target} isViolation={isViolation} edgeType={edgeType} isDimmed={isDimmed} />
    );
  }

  return (
    <AnimatedEdge
      source={source}
      target={target}
      isViolation={isViolation}
      edgeType={edgeType}
      animationEnabled={animationEnabled}
      isActive={isActive}
      isHighlighted={isHighlighted}
      isDimmed={isDimmed}
    />
  );
}
