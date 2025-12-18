/**
 * CrystalVine - Organic Memory Connections
 *
 * Thin wrapper over TopologyEdge3D with crystal theme.
 * Connections are living tendrils showing the flow of memory echoes.
 *
 * Philosophy:
 *   "Memories are not linked by wires—they are connected by echoes."
 *
 * @see plans/3d-projection-consolidation.md
 * @see impl/claude/web/src/components/three/primitives/TopologyEdge3D.tsx
 */

import { TopologyEdge3D, SmartTopologyEdge3D } from '../three/primitives';
import { CRYSTAL_THEME } from '../three/primitives/themes/crystal';

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
// Main Component
// =============================================================================

/**
 * CrystalVine - Memory echo connections between crystals.
 *
 * This is now a thin wrapper over TopologyEdge3D with:
 * - Crystal theme (cyan/purple color palette)
 * - Similarity-based strength
 * - No violation state (Brain doesn't use violations)
 */
export function CrystalVine({
  source,
  target,
  similarity,
  isActive = false,
  animationEnabled = true,
  isDimmed = false,
}: CrystalVineProps) {
  return (
    <TopologyEdge3D
      source={source}
      target={target}
      theme={CRYSTAL_THEME}
      strength={similarity}
      isActive={isActive}
      isViolation={false}
      isDimmed={isDimmed}
      showFlowParticles={animationEnabled}
      animationEnabled={animationEnabled}
      // Crystal-specific styling
      baseWidth={1.0}
      activeWidth={2.0}
      dimmedWidth={0.5}
      curveIntensity={0.12}
    />
  );
}

// =============================================================================
// Smart Crystal Vine
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
 * - Edge has high similarity (> 0.6)
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
  return (
    <SmartTopologyEdge3D
      source={source}
      target={target}
      theme={CRYSTAL_THEME}
      strength={similarity}
      isActive={isActive}
      isViolation={false}
      isDimmed={isDimmed}
      showFlowParticles={animationEnabled}
      animationEnabled={animationEnabled}
      forceSimple={forceSimple}
      fullRenderingThreshold={0.6}
      // Crystal-specific styling
      baseWidth={1.0}
      activeWidth={2.0}
      dimmedWidth={0.5}
      curveIntensity={0.12}
    />
  );
}

export default CrystalVine;
