/**
 * Town Components
 *
 * Agent Town visualization components for the Crown Jewel.
 *
 * @see spec/protocols/os-shell.md - Part IV: Gallery Primitive Reliance
 */

// Core visualization (projection-first)
export { TownVisualization, default as TownVisualizationDefault } from './TownVisualization';
export type { TownVisualizationProps } from './TownVisualization';

// Sub-components
export { Mesa } from './Mesa';
export { CitizenPanel } from './CitizenPanel';
export { VirtualizedCitizenList } from './VirtualizedCitizenList';
