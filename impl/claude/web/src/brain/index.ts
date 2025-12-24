/**
 * Brain Module — Unified Data Explorer
 *
 * "The file is a lie. There is only the graph."
 *
 * Exports components for the Brain page's unified stream interface.
 */

// Types (export before components to avoid name collision)
export type {
  EntityType,
  UnifiedEvent,
  EventMetadata,
  MarkMetadata,
  CrystalMetadata,
  TrailMetadata,
  EvidenceMetadata,
  TeachingMetadata,
  LemmaMetadata,
  StreamFilters,
  BrainPageState,
  ListEventsRequest,
  ListEventsResponse,
  SearchEventsRequest,
  SearchEventsResponse,
  StreamEvent,
} from './types';

export {
  ENTITY_BADGES,
  DEFAULT_FILTERS,
  INITIAL_STATE,
  isMarkMetadata,
  isCrystalMetadata,
  isTrailMetadata,
  isEvidenceMetadata,
  isTeachingMetadata,
  isLemmaMetadata,
} from './types';

// Hooks
export { useBrainStream, useBrainPoll } from './hooks/useBrainStream';

// Components (renamed to avoid collision with StreamFilters type)
export { UnifiedEventCard } from './components/UnifiedEventCard';
export {
  StreamFilters as StreamFiltersBar,
  StreamFiltersCompact,
} from './components/StreamFilters';
export { ConnectionStatus, ConnectionDot } from './components/ConnectionStatus';
export { DetailPreview } from './DetailPreview';
