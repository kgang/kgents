/**
 * Agent Details: Deep dive views for citizen state.
 *
 * Components provide three detail levels:
 * - Compact: Hover card with phase + sparkline
 * - Expanded: Sidebar with eigenvector bars + tabs
 * - Full: Modal with full-width charts + JSON viewer
 *
 * @see plans/web-refactor/user-flows.md
 */

export { AgentDetails, type AgentDetailsProps, type DetailLevel } from './AgentDetails';
export { OverviewTab, type OverviewTabProps } from './OverviewTab';
export { MetricsTab, type MetricsTabProps } from './MetricsTab';
export { RelationshipsTab, type RelationshipsTabProps } from './RelationshipsTab';
export { StateTab, type StateTabProps } from './StateTab';
export { HistoryTab, type HistoryTabProps } from './HistoryTab';
export { ExportButton, type ExportButtonProps } from './ExportButton';
