/**
 * Differance Components - The Ghost Heritage Graph
 *
 * Visualizations for the Differance Engine: seeing what almost was alongside what is.
 *
 * Components:
 * - GhostHeritageGraph: Full DAG visualization
 * - GhostBadge: Compact ghost count badge
 * - WhyPanel: Inline "why did this happen?" explanation
 * - TraceTimeline: Real trace timeline (replaces RecentTracesPanel)
 * - RecentTracesPanel: Recent traces list for Cockpit (deprecated, use TraceTimeline)
 *
 * @see spec/protocols/differance.md - The specification
 * @see plans/differance-devex-enlightenment.md - Phase 7: DevEx
 */

// Full heritage graph visualization
export { GhostHeritageGraph } from './GhostHeritageGraph';
export type { GhostHeritageGraphProps } from './GhostHeritageGraph';

// Compact ghost count badge
export { GhostBadge } from './GhostBadge';
export type { GhostBadgeProps } from './GhostBadge';

// Inline "why?" explanation panel
export { WhyPanel } from './WhyPanel';
export type { WhyPanelProps } from './WhyPanel';

// Trace timeline (Phase 7A - replaces RecentTracesPanel)
export { TraceTimeline } from './TraceTimeline';
export type { TraceTimelineProps } from './TraceTimeline';

// Trace inspector (Phase 7B - detailed trace view)
export { TraceInspector } from './TraceInspector';
export type { TraceInspectorProps } from './TraceInspector';

// Ghost exploration modal (Phase 7C - explore roads not taken)
export { GhostExplorationModal } from './GhostExplorationModal';
export type {
  GhostExplorationModalProps,
  GhostInfo,
  ChosenPathInfo,
} from './GhostExplorationModal';

// Recent traces panel for Cockpit (deprecated - use TraceTimeline)
export { RecentTracesPanel } from './RecentTracesPanel';
export type { RecentTracesPanelProps } from './RecentTracesPanel';

// Recording controls (Phase 7D - session recording)
export { RecordingControls, useSessionRecording } from './RecordingControls';
export type {
  RecordingControlsProps,
  RecordingSession,
  DecisionMarker,
  UseSessionRecordingOptions,
  UseSessionRecordingReturn,
} from './RecordingControls';

// Export panel (Phase 7E - export & share)
export { ExportPanel } from './ExportPanel';
export type { ExportPanelProps, ExportFormat, ExportedSession, ExportedTrace } from './ExportPanel';
