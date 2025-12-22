/**
 * Derivation Framework Visualization Components
 *
 * Phase 5: Derivation Framework (spec/protocols/derivation-framework.md)
 *
 * These components visualize the agent derivation DAG:
 * - DerivationDAG: Full DAG with tier layers and edges
 * - ConfidenceBreakdown: Stacked bar of confidence components
 * - ConfidenceTimeline: Line chart of confidence over time
 * - PrincipleRadar: Radar chart of 7 principle draws
 * - DerivationPortal: Expandable navigation token
 *
 * Integration points:
 * - AGENTESE: concept.derivation.* paths
 * - typed-hypergraph: DAG as hypergraph
 * - portal-token: Nodes as expandable portals
 *
 * @example
 * ```tsx
 * import {
 *   DerivationDAG,
 *   ConfidenceBreakdown,
 *   PrincipleRadar,
 *   DerivationPortal,
 * } from '@/components/derivation';
 *
 * function DerivationView({ data }) {
 *   return (
 *     <div className="grid grid-cols-2 gap-4">
 *       <DerivationDAG data={data.dag} />
 *       <div className="space-y-4">
 *         <ConfidenceBreakdown data={data.confidence} />
 *         <PrincipleRadar data={data.principles} />
 *       </div>
 *     </div>
 *   );
 * }
 * ```
 */

// Main DAG visualization
export { DerivationDAG } from './DerivationDAG';
export type { DerivationDAGProps, DerivationDAGData } from './DerivationDAG';

// Confidence breakdown (stacked bar)
export { ConfidenceBreakdown } from './ConfidenceBreakdown';
export type { ConfidenceBreakdownProps } from './ConfidenceBreakdown';

// Confidence timeline (line chart)
export { ConfidenceTimeline } from './ConfidenceTimeline';
export type { ConfidenceTimelineProps } from './ConfidenceTimeline';

// Principle radar chart
export { PrincipleRadar } from './PrincipleRadar';
export type { PrincipleRadarProps } from './PrincipleRadar';

// Portal tokens for navigation
export { DerivationPortal, DerivationPortalList } from './DerivationPortal';
export type {
  DerivationPortalProps,
  DerivationPortalListProps,
} from './DerivationPortal';
