/**
 * ElasticPlaceholder: Intelligent placeholder for loading/empty/error states.
 *
 * Provides contextual placeholders with:
 * - Skeleton animation for loading
 * - Friendly empty states per content type
 * - Error display with retry capability
 *
 * @see plans/web-refactor/elastic-primitives.md
 */

import { type CSSProperties } from 'react';

export type PlaceholderFor = 'agent' | 'metric' | 'chart' | 'list' | 'custom';
export type PlaceholderState = 'loading' | 'empty' | 'error';

export interface ElasticPlaceholderProps {
  /** What's being loaded */
  for: PlaceholderFor;

  /** Current state */
  state: PlaceholderState;

  /** Error message (for error state) */
  error?: string;

  /** Retry action */
  onRetry?: () => void;

  /** Match dimensions of expected content */
  expectedSize?: { width: string; height: string };

  /** Custom empty message */
  emptyMessage?: string;

  /** Custom empty icon/emoji */
  emptyIcon?: string;

  /** Custom class name */
  className?: string;

  /** Custom styles */
  style?: CSSProperties;
}

/**
 * Default empty state content per type
 */
const EMPTY_DEFAULTS: Record<PlaceholderFor, { icon: string; title: string; message: string }> = {
  agent: {
    icon: '◎',
    title: 'No agents yet',
    message: 'Create an agent to get started',
  },
  metric: {
    icon: '◉',
    title: 'No data',
    message: 'Metrics will appear once activity begins',
  },
  chart: {
    icon: '◆',
    title: 'Nothing to visualize',
    message: 'Data will populate as events occur',
  },
  list: {
    icon: '○',
    title: 'Empty list',
    message: 'Items will appear here',
  },
  custom: {
    icon: '◇',
    title: 'Nothing here',
    message: 'Content will appear when available',
  },
};

/**
 * Skeleton shapes for different content types
 */
function SkeletonForType({ type }: { type: PlaceholderFor }) {
  switch (type) {
    case 'agent':
      return (
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="elastic-skeleton w-10 h-10 rounded-full" />
            <div className="space-y-2 flex-1">
              <div className="elastic-skeleton h-4 w-3/4" />
              <div className="elastic-skeleton h-3 w-1/2" />
            </div>
          </div>
          <div className="elastic-skeleton h-3 w-full" />
          <div className="elastic-skeleton h-3 w-5/6" />
        </div>
      );

    case 'metric':
      return (
        <div className="space-y-2">
          <div className="elastic-skeleton h-8 w-24" />
          <div className="elastic-skeleton h-4 w-16" />
        </div>
      );

    case 'chart':
      return (
        <div className="space-y-2">
          <div className="flex items-end gap-1 h-24">
            {[40, 60, 30, 80, 50, 70, 45].map((h, i) => (
              <div key={i} className="elastic-skeleton flex-1" style={{ height: `${h}%` }} />
            ))}
          </div>
          <div className="flex justify-between">
            <div className="elastic-skeleton h-3 w-8" />
            <div className="elastic-skeleton h-3 w-8" />
            <div className="elastic-skeleton h-3 w-8" />
          </div>
        </div>
      );

    case 'list':
      return (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center gap-2">
              <div className="elastic-skeleton w-4 h-4 rounded" />
              <div className="elastic-skeleton h-4 flex-1" />
            </div>
          ))}
        </div>
      );

    case 'custom':
    default:
      return (
        <div className="space-y-3">
          <div className="elastic-skeleton h-4 w-full" />
          <div className="elastic-skeleton h-4 w-4/5" />
          <div className="elastic-skeleton h-4 w-3/5" />
        </div>
      );
  }
}

export function ElasticPlaceholder({
  for: forType,
  state,
  error,
  onRetry,
  expectedSize,
  emptyMessage,
  emptyIcon,
  className = '',
  style,
}: ElasticPlaceholderProps) {
  const defaults = EMPTY_DEFAULTS[forType];

  // Build container styles
  const containerStyle: CSSProperties = {
    minWidth: expectedSize?.width,
    minHeight: expectedSize?.height,
    ...style,
  };

  // Loading state: show skeleton
  if (state === 'loading') {
    return (
      <div
        className={`p-4 ${className}`}
        style={containerStyle}
        role="status"
        aria-label="Loading"
      >
        <SkeletonForType type={forType} />
      </div>
    );
  }

  // Error state: show error with retry
  if (state === 'error') {
    return (
      <div
        className={`p-4 rounded-lg border ${className}`}
        style={{
          ...containerStyle,
          background: 'rgba(166, 93, 74, 0.1)',
          borderColor: 'var(--accent-error)',
        }}
        role="alert"
      >
        <div className="flex flex-col items-center text-center gap-3">
          <span className="text-2xl">◆</span>
          <div>
            <p className="font-medium" style={{ color: 'var(--accent-error)' }}>
              Something went wrong
            </p>
            {error && (
              <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
                {error}
              </p>
            )}
          </div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="elastic-button px-4 py-2 rounded-md text-sm font-medium transition-colors"
              style={{
                background: 'rgba(166, 93, 74, 0.2)',
                color: 'var(--accent-error)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(166, 93, 74, 0.3)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(166, 93, 74, 0.2)';
              }}
            >
              Try again
            </button>
          )}
        </div>
      </div>
    );
  }

  // Empty state: show friendly message
  return (
    <div
      className={`empty-state ${className}`}
      style={containerStyle}
      role="status"
      aria-label="Empty"
    >
      <span className="empty-state-emoji">{emptyIcon || defaults.icon}</span>
      <p className="empty-state-title">{defaults.title}</p>
      <p className="empty-state-message">{emptyMessage || defaults.message}</p>
    </div>
  );
}

export default ElasticPlaceholder;
