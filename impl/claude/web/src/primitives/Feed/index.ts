/**
 * Feed Primitive
 *
 * "The feed is not a view of data. The feed IS the primary interface."
 *
 * Universal chronological truth stream for kgents.
 * Everything is a K-Block. The feed is how you navigate them.
 *
 * From Zero Seed Genesis Grand Strategy (LAW 1: Feed Is Primitive):
 * - Chronological truth streams
 * - Filterable by lens (layer, loss, author, principle)
 * - Algorithmic (attention + principles alignment)
 * - Recursive (users create feedback systems with feeds)
 */

export { Feed } from './Feed';
export { FeedItem } from './FeedItem';
export { FeedFilters } from './FeedFilters';
export { useFeedFeedback, calculateEngagementScore, calculateAlgorithmicScore } from './useFeedFeedback';

export type {
  KBlock,
  FeedSource,
  FeedSourceType,
  FeedFilter,
  FeedFilterValue,
  FeedRanking,
  Feed as FeedConfig,
  FeedProps,
  FeedItemProps,
  FeedFiltersProps,
  FeedbackAction,
  FeedbackEvent,
  UseFeedFeedback,
} from './types';

export {
  LAYER_NAMES,
  LAYER_COLORS,
  LOSS_THRESHOLDS,
  LOSS_COLORS,
} from './types';
