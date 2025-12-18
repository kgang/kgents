/**
 * GestaltTree - Living Architecture Navigator
 *
 * A hierarchical tree view of codebase modules with health metrics.
 *
 * @example
 * ```tsx
 * import { GestaltTree } from '@/components/gestalt/GestaltTree';
 *
 * <GestaltTree
 *   modules={topology.nodes}
 *   links={topology.links}
 *   selectedModule={selectedId}
 *   onModuleSelect={handleSelect}
 * />
 * ```
 */

// Main components
export { GestaltTree, default } from './GestaltTree';
export { GestaltTreeNode } from './GestaltTreeNode';
export { HealthBadge, HealthBadgeLarge } from './HealthBadge';

// Tree building utilities
export {
  buildGestaltTree,
  buildLayerTree,
  buildPathTree,
  getViolationMap,
} from './buildGestaltTree';

// Types
export type {
  GestaltNode,
  GestaltTreeProps,
  GestaltTreeNodeProps,
  HealthBadgeProps,
  TreeMode,
} from './types';

// Type utilities
export { GRADE_ORDER, gradeToNumber, numberToGrade, getWorstGrade } from './types';
