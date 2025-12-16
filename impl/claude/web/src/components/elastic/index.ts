/**
 * Elastic Components: Self-arranging UI primitives.
 *
 * These components form the foundation of the elastic layout system.
 * They handle graceful degradation, responsive behavior, and layout
 * awareness automatically.
 *
 * @see plans/web-refactor/elastic-primitives.md
 */

export {
  ElasticContainer,
  type ElasticContainerProps,
  type ElasticLayout,
  type ElasticOverflow,
  type ElasticTransition,
  type ElasticGap,
} from './ElasticContainer';

export {
  ElasticCard,
  ElasticCardHeader,
  ElasticCardContent,
  ElasticCardFooter,
  type ElasticCardProps,
  type ElasticCardHeaderProps,
  type ElasticCardContentProps,
  type ElasticCardFooterProps,
  type CardMinContent,
  type CardShrinkBehavior,
} from './ElasticCard';

export {
  ElasticPlaceholder,
  ElasticSkeleton,
  type ElasticPlaceholderProps,
  type PlaceholderFor,
  type PlaceholderState,
} from './ElasticPlaceholder';

export {
  ElasticSplit,
  type ElasticSplitProps,
  type SplitDirection,
  type CollapsePriority,
} from './ElasticSplit';
