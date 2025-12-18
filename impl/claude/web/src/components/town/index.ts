/**
 * Town Components
 *
 * Agent Town visualization components for the Crown Jewel.
 *
 * 2D Renaissance (2025-12-18): TownCanvas3D mothballed.
 * See _mothballed/three-visualizers/town/ for preserved component.
 *
 * What remains: Mesa (2D), all panel components - the real UI.
 *
 * @see spec/protocols/2d-renaissance.md
 */

// Core visualization (projection-first, 2D)
export { TownVisualization, default as TownVisualizationDefault } from './TownVisualization';
export type { TownVisualizationProps } from './TownVisualization';

// Sub-components (ALL KEEP - 2D first)
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

// =============================================================================
// MOTHBALLED (2025-12-18): Three.js visualization component
// Preserved in: _mothballed/three-visualizers/town/
// - TownCanvas3D.tsx (383 lines)
// Revival condition: VR/AR projections or 3D town visualization
// =============================================================================
