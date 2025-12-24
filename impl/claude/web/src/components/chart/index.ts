/**
 * Astronomical Chart — Canvas-based spec graph visualization
 *
 * Specs as stars, not boxes. Scale to millions.
 *
 * "The file is a lie. There is only the graph."
 */

// Core components
export { AstronomicalChart } from './AstronomicalChart';
export { ChartControls } from './ChartControls';

// Hooks
export { useAstronomicalData } from './useAstronomicalData';
export { useWitnessedGraphData } from './useWitnessedGraphData';
export { useViewport } from './useViewport';
export { useForceLayout } from './useForceLayout';
export { useChartInteraction } from './useChartInteraction';

// Rendering
export * from './StarRenderer';

// Scale optimization
export { Quadtree, buildQuadtree } from './Quadtree';
export {
  ViewportCuller,
  calculateViewportBounds,
  simpleCull,
  createStarCuller,
} from './ViewportCuller';
export * from './LevelOfDetail';

// Types
export type { StarData, ConnectionData, AstronomicalDataReturn } from './useAstronomicalData';
export type { WitnessedGraphDataOptions, WitnessedGraphDataReturn } from './useWitnessedGraphData';
export type { ViewportState, ViewportActions, ViewportReturn } from './useViewport';
export type { ForceNode, ForceLink, ForceLayoutReturn } from './useForceLayout';
export type {
  InteractionState,
  InteractionActions,
  UseChartInteractionReturn,
} from './useChartInteraction';
export type { Point, Bounds, QuadtreeItem } from './Quadtree';
export type { ViewportBounds, CullResult } from './ViewportCuller';
export type { LODLevel, LODConfig, Cluster, HeatMapCell } from './LevelOfDetail';
