/**
 * Town Components
 *
 * Agent Town visualization components for the Crown Jewel.
 *
 * @see spec/protocols/os-shell.md - Part IV: Gallery Primitive Reliance
 * @see plans/park-town-design-overhaul.md - Phase 2 enhancements
 */

// Core visualization (projection-first)
export { TownVisualization, default as TownVisualizationDefault } from './TownVisualization';
export type { TownVisualizationProps } from './TownVisualization';

// Sub-components
export { Mesa } from './Mesa';
export { CitizenPanel } from './CitizenPanel';
export { VirtualizedCitizenList } from './VirtualizedCitizenList';

// Phase 2: N-gent witness and observer components
export { TownTracePanel } from './TownTracePanel';
export type { TownTracePanelProps } from './TownTracePanel';
export { ObserverSelector, OBSERVERS } from './ObserverSelector';
export type { ObserverSelectorProps, ObserverUmwelt, ObserverConfig } from './ObserverSelector';
