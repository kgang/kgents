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

// Contract-driven components (Phase: Town Frontend Implementation)
export { TownOverview, default as TownOverviewDefault } from './TownOverview';
export { CitizenBrowser, default as CitizenBrowserDefault } from './CitizenBrowser';
export { CoalitionGraph, default as CoalitionGraphDefault } from './CoalitionGraph';

// 3D Projection (Town Renaissance)
export { TownCanvas3D, default as TownCanvas3DDefault } from './TownCanvas3D';
export type { TownCanvas3DProps } from './TownCanvas3D';
