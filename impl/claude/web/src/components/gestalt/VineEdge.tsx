/**
 * VineEdge - Organic Growing Connections
 *
 * Thin wrapper over TopologyEdge3D with forest theme.
 * Edges are living tendrils showing dependencies as roots reaching for water.
 *
 * Philosophy:
 *   "Dependencies are not wires—they are roots reaching for water."
 *
 * @see plans/3d-projection-consolidation.md
 * @see impl/claude/web/src/components/three/primitives/TopologyEdge3D.tsx
 */

import { TopologyEdge3D, SmartTopologyEdge3D } from '../three/primitives';
import { FOREST_THEME } from '../three/primitives/themes/forest';

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
// Main Component
// =============================================================================

/**
 * VineEdge - Dependency connections between modules.
 *
 * This is now a thin wrapper over TopologyEdge3D with:
 * - Forest theme (green/red color palette)
 * - Violation support (thorny red edges)
 * - Flow particles for active edges
 */
export function VineEdge({
  source,
  target,
  isViolation = false,
  animationEnabled = true,
  isActive = false,
  isHighlighted = false,
  isDimmed = false,
}: VineEdgeProps) {
  // Merge isActive and isHighlighted for the primitive
  const isActiveOrHighlighted = isActive || isHighlighted;

  return (
    <TopologyEdge3D
      source={source}
      target={target}
      theme={FOREST_THEME}
      strength={0.5} // Default strength; could be parameterized
      isActive={isActiveOrHighlighted}
      isViolation={isViolation}
      isDimmed={isDimmed}
      showFlowParticles={animationEnabled}
      animationEnabled={animationEnabled}
      // Forest-specific styling
      baseWidth={1.5}
      activeWidth={2.5}
      dimmedWidth={0.8}
      curveIntensity={0.15}
    />
  );
}

// =============================================================================
// Smart Vine Edge
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
  const isActiveOrHighlighted = isActive || isHighlighted;

  return (
    <SmartTopologyEdge3D
      source={source}
      target={target}
      theme={FOREST_THEME}
      strength={0.5}
      isActive={isActiveOrHighlighted}
      isViolation={isViolation}
      isDimmed={isDimmed}
      showFlowParticles={animationEnabled}
      animationEnabled={animationEnabled}
      forceSimple={forceSimple}
      fullRenderingThreshold={0.5}
      // Forest-specific styling
      baseWidth={1.5}
      activeWidth={2.5}
      dimmedWidth={0.8}
      curveIntensity={0.15}
    />
  );
}

export default VineEdge;
