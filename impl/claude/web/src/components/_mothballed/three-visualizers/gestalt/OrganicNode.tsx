/**
 * OrganicNode - Plant-like Module Visualization
 *
 * Thin wrapper over TopologyNode3D with forest theme.
 * Each module is represented as a growing organism with growth rings.
 *
 * Philosophy:
 *   "We do not design the flower—we design the soil and the season."
 *   The visualization emerges from rules, not placement.
 *
 * @see plans/3d-projection-consolidation.md
 * @see impl/claude/web/src/components/three/primitives/TopologyNode3D.tsx
 */

import { TopologyNode3D } from '../three/primitives';
import {
  FOREST_THEME,
  getForestTier,
  calculateOrganicSize,
  calculateRingCount,
} from '../three/primitives/themes/forest';
import type { Density } from '../three/primitives/themes/types';
import type { CodebaseModule } from '../../api/types';

// Re-export Density type for backward compatibility
export type { Density } from '../three/primitives/themes/types';

// =============================================================================
// Types
// =============================================================================

export interface OrganicNodeProps {
  /** Module data */
  node: CodebaseModule;
  /** Whether this node is selected */
  isSelected: boolean;
  /** Click handler */
  onClick: () => void;
  /** Whether to show the label */
  showLabel: boolean;
  /** Layout density */
  density: Density;
  /** Whether tooltips are enabled (currently unused - for future) */
  enableTooltip?: boolean;
  /** Animation speed multiplier (0 = frozen, 1 = normal) */
  animationSpeed?: number;
}

// =============================================================================
// Domain-Specific Adapters
// =============================================================================

/**
 * Get tier from CodebaseModule data.
 * Maps health_score to forest tier.
 */
function getModuleTier(module: CodebaseModule): string {
  return getForestTier(module.health_score);
}

/**
 * Get size from CodebaseModule data.
 * Uses lines of code and health score for sizing.
 */
function getModuleSize(module: CodebaseModule, density: Density): number {
  return calculateOrganicSize(module.lines_of_code, module.health_score, density);
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * OrganicNode - A living plant-like module in the code garden.
 *
 * This is now a thin wrapper over TopologyNode3D with:
 * - Forest theme (green/yellow/red color palette)
 * - Health-based tier calculation
 * - Lines of code-based sizing
 * - Growth rings showing module size/age
 */
export function OrganicNode({
  node,
  isSelected,
  onClick,
  showLabel,
  density,
  enableTooltip: _enableTooltip = true,
  animationSpeed = 1,
}: OrganicNodeProps) {
  void _enableTooltip; // Suppress unused variable warning (reserved for future tooltip support)
  // Calculate ring count based on lines of code
  const ringCount = calculateRingCount(node.lines_of_code);

  return (
    <TopologyNode3D
      position={[node.x, node.y, node.z]}
      theme={FOREST_THEME}
      data={node}
      getTier={getModuleTier}
      getSize={getModuleSize}
      isSelected={isSelected}
      isHub={false}
      onClick={onClick}
      showLabel={showLabel}
      label={node.label}
      density={density}
      animationSpeed={animationSpeed}
      // Forest-specific styling
      roughness={0.6}
      metalness={0.1}
      segments={24}
      // Growth rings for forest theme
      showGrowthRings={true}
      ringCount={ringCount}
    />
  );
}

export default OrganicNode;
