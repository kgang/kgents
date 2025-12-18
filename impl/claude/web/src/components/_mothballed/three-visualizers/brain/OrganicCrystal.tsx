/**
 * OrganicCrystal - Living Memory Crystal Visualization
 *
 * Thin wrapper over TopologyNode3D with crystal theme.
 * Transforms memory nodes into glowing crystalline structures.
 *
 * Philosophy:
 *   "Memories are not data points—they are living crystallizations of thought."
 *
 * @see plans/3d-projection-consolidation.md
 * @see impl/claude/web/src/components/three/primitives/TopologyNode3D.tsx
 */

import { TopologyNode3D } from '../three/primitives';
import {
  CRYSTAL_THEME,
  getCrystalTier,
  calculateCrystalSize,
} from '../three/primitives/themes/crystal';
import type { Density } from '../three/primitives/themes/types';
import type { TopologyNode } from '../../api/types';

// =============================================================================
// Types
// =============================================================================

export interface OrganicCrystalProps {
  /** Crystal node data */
  node: TopologyNode;
  /** Whether this node is a hub */
  isHub: boolean;
  /** Whether this node is selected */
  isSelected: boolean;
  /** Click handler */
  onClick: () => void;
  /** Whether to show the label */
  showLabel?: boolean;
  /** Layout density */
  density?: Density;
  /** Animation speed multiplier (0 = frozen, 1 = normal) */
  animationSpeed?: number;
}

// =============================================================================
// Domain-Specific Adapters
// =============================================================================

/**
 * Get tier from TopologyNode data.
 * Maps resolution and hot state to crystal tier.
 */
function getNodeTier(node: TopologyNode): string {
  return getCrystalTier(node.resolution, node.is_hot);
}

/**
 * Get size from TopologyNode data.
 * Uses access count and resolution for sizing.
 */
function getNodeSize(node: TopologyNode, density: Density): number {
  return calculateCrystalSize(node.access_count, node.resolution, false, density);
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * OrganicCrystal - A living memory crystal in the holographic brain.
 *
 * This is now a thin wrapper over TopologyNode3D with:
 * - Crystal theme (cyan/purple/amber color palette)
 * - Resolution-based tier calculation
 * - Access count-based sizing
 */
export function OrganicCrystal({
  node,
  isHub,
  isSelected,
  onClick,
  showLabel = true,
  density = 'comfortable',
  animationSpeed = 1,
}: OrganicCrystalProps) {
  return (
    <TopologyNode3D
      position={[node.x, node.y, node.z]}
      theme={CRYSTAL_THEME}
      data={node}
      getTier={getNodeTier}
      getSize={getNodeSize}
      isSelected={isSelected}
      isHub={isHub}
      onClick={onClick}
      showLabel={showLabel}
      label={node.label}
      density={density}
      animationSpeed={animationSpeed}
      // Crystal-specific styling
      roughness={0.3}
      metalness={0.2}
      segments={32}
      // No growth rings for crystals
      showGrowthRings={false}
    />
  );
}

export default OrganicCrystal;
