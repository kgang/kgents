/**
 * Witness Components
 *
 * Components for displaying and creating witness marks.
 *
 * @see plans/witness-fusion-ux-implementation.md
 */

export { MarkCard, AgentBadge, PrincipleChip, type MarkDensity, type MarkCardProps } from './MarkCard';
export {
  MarkTimeline,
  DaySeparator,
  SessionSeparator,
  LoadingSkeleton,
  EmptyState,
  ErrorState,
  type GroupBy,
  type MarkTimelineProps,
} from './MarkTimeline';
export { QuickMarkForm, type QuickMarkFormProps } from './QuickMarkForm';
export {
  MarkFilters,
  FilterChip,
  FilterSection,
  createDefaultFilters,
  type MarkFilterState,
  type MarkFiltersProps,
  type AuthorFilter,
} from './MarkFilters';
