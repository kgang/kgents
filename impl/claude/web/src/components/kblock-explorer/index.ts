/**
 * K-Block Explorer Component Exports
 *
 * "K-Blocks organized by layer (L0-L3 for Constitutional, L1-L7 for user)"
 *
 * @see spec/agents/k-block.md
 */

// Main component
export { KBlockExplorer, default } from './KBlockExplorer';

// Sub-components
export { KBlockTree } from './KBlockTree';
export { ConstitutionalSection } from './ConstitutionalSection';
export { LayerGroup } from './LayerGroup';

// Hook
export { useKBlockNavigation } from './hooks/useKBlockNavigation';

// Types
export type {
  KBlockExplorerProps,
  KBlockExplorerItem,
  KBlockLayerGroup,
  KBlockTreeProps,
  ConstitutionalSectionProps,
  LayerGroupProps,
  ConstitutionalLayerConfig,
  UserLayerConfig,
  FocusTarget,
  ExplorerSection,
  NavigationDirection,
  CleanSlateKBlock,
  DerivationEdge,
  DerivationGraphResponse,
} from './types';

// Constants and helpers
export {
  CONSTITUTIONAL_LAYER_CONFIG,
  USER_LAYER_CONFIG,
  getLayerConfig,
  getLayerColor,
  getLayerIcon,
  getLossSeverity,
  getLossColor,
  toExplorerItem,
  groupByLayer,
} from './types';
