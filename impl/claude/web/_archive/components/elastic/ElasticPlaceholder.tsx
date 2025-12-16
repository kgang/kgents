/**
 * ElasticPlaceholder: Intelligent placeholder for loading/empty/error states.
 *
 * Provides consistent, personality-filled placeholders across the application.
 * Supports skeleton loading animations, friendly error messages, and retry actions.
 *
 * @see plans/web-refactor/elastic-primitives.md
 * @see plans/web-refactor/polish-and-delight.md
 */

import { type ReactNode } from 'react';
import { cn } from '@/lib/utils';

export type PlaceholderFor = 'agent' | 'metric' | 'chart' | 'list' | 'card' | 'custom';
export type PlaceholderState = 'loading' | 'empty' | 'error';

export interface ElasticPlaceholderProps {
  /** What's being loaded/shown */
  for?: PlaceholderFor;

  /** Current state */
  state: PlaceholderState;

  /** Error message (for error state) */
  error?: string;

  /** Retry action */
  onRetry?: () => void;

  /** Match dimensions of expected content */
  expectedSize?: { width: string; height: string };

  /** Custom empty state content */
  emptyContent?: ReactNode;

  /** Custom loading content */
  loadingContent?: ReactNode;

  /** Additional class names */
  className?: string;
}

// Friendly error messages with personality
const ERROR_MESSAGES: Record<string, { emoji: string; message: string; hint: string }> = {
  NETWORK_ERROR: {
    emoji: '🌐',
    message: 'Lost connection',
    hint: 'Check your internet and try again',
  },
  NOT_FOUND: {
    emoji: '🔍',
    message: 'Nothing here',
    hint: "We looked everywhere but couldn't find it",
  },
  RATE_LIMITED: {
    emoji: '🐢',
    message: 'Slow down there!',
    hint: 'Take a breath and try again shortly',
  },
  SERVER_ERROR: {
    emoji: '🔧',
    message: 'Something went sideways',
    hint: "We're looking into it",
  },
  DEFAULT: {
    emoji: '🤷',
    message: 'That was unexpected',
    hint: 'Try again or refresh the page',
  },
};

// Empty state content by type
const EMPTY_STATES: Record<PlaceholderFor, { emoji: string; message: string }> = {
  agent: { emoji: '🌱', message: 'No agents yet' },
  metric: { emoji: '📊', message: 'No data available' },
  chart: { emoji: '📈', message: 'Nothing to display' },
  list: { emoji: '📋', message: 'The list is empty' },
  card: { emoji: '🎴', message: 'Nothing to show' },
  custom: { emoji: '✨', message: 'Nothing here yet' },
};

/**
 * Skeleton component for loading state
 */
function Skeleton({ type, className }: { type: PlaceholderFor; className?: string }) {
  switch (type) {
    case 'agent':
      return (
        <div className={cn('animate-pulse', className)}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-town-accent/30" />
            <div className="flex-1">
              <div className="h-4 w-24 rounded bg-town-accent/30 mb-2" />
              <div className="h-3 w-16 rounded bg-town-accent/20" />
            </div>
          </div>
          <div className="h-8 mt-3 rounded bg-town-accent/20" />
        </div>
      );

    case 'metric':
      return (
        <div className={cn('animate-pulse', className)}>
          <div className="h-3 w-16 rounded bg-town-accent/20 mb-2" />
          <div className="h-8 w-24 rounded bg-town-accent/30" />
        </div>
      );

    case 'chart':
      return (
        <div className={cn('animate-pulse', className)}>
          <div className="h-32 rounded bg-town-accent/20" />
        </div>
      );

    case 'list':
      return (
        <div className={cn('animate-pulse space-y-2', className)}>
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-8 rounded bg-town-accent/20" />
          ))}
        </div>
      );

    case 'card':
      return (
        <div className={cn('animate-pulse p-4 rounded-lg bg-town-surface/50', className)}>
          <div className="h-4 w-32 rounded bg-town-accent/30 mb-3" />
          <div className="h-3 w-full rounded bg-town-accent/20 mb-2" />
          <div className="h-3 w-2/3 rounded bg-town-accent/20" />
        </div>
      );

    default:
      return (
        <div className={cn('animate-pulse', className)}>
          <div className="h-20 rounded bg-town-accent/20" />
        </div>
      );
  }
}

/**
 * Get error info from error string
 */
function getErrorInfo(error?: string): { emoji: string; message: string; hint: string } {
  if (!error) return ERROR_MESSAGES.DEFAULT;

  const upperError = error.toUpperCase();
  if (upperError.includes('NETWORK')) return ERROR_MESSAGES.NETWORK_ERROR;
  if (upperError.includes('NOT FOUND') || upperError.includes('404')) return ERROR_MESSAGES.NOT_FOUND;
  if (upperError.includes('RATE') || upperError.includes('429')) return ERROR_MESSAGES.RATE_LIMITED;
  if (upperError.includes('SERVER') || upperError.includes('500')) return ERROR_MESSAGES.SERVER_ERROR;

  return { ...ERROR_MESSAGES.DEFAULT, message: error };
}

export function ElasticPlaceholder({
  for: placeholderFor = 'custom',
  state,
  error,
  onRetry,
  expectedSize,
  emptyContent,
  loadingContent,
  className,
}: ElasticPlaceholderProps) {
  const sizeStyle = expectedSize
    ? { width: expectedSize.width, height: expectedSize.height }
    : undefined;

  // Loading state
  if (state === 'loading') {
    return (
      <div className={cn('p-4', className)} style={sizeStyle}>
        {loadingContent || <Skeleton type={placeholderFor} />}
      </div>
    );
  }

  // Empty state
  if (state === 'empty') {
    const emptyState = EMPTY_STATES[placeholderFor];
    return (
      <div
        className={cn(
          'flex flex-col items-center justify-center p-6 text-center',
          className
        )}
        style={sizeStyle}
      >
        {emptyContent || (
          <>
            <div className="text-4xl mb-2">{emptyState.emoji}</div>
            <p className="text-gray-400">{emptyState.message}</p>
          </>
        )}
      </div>
    );
  }

  // Error state
  const errorInfo = getErrorInfo(error);
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-6 text-center',
        className
      )}
      style={sizeStyle}
    >
      <div className="text-4xl mb-2">{errorInfo.emoji}</div>
      <h3 className="text-lg font-semibold mb-1">{errorInfo.message}</h3>
      <p className="text-sm text-gray-400 mb-4">{errorInfo.hint}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-town-highlight hover:bg-town-highlight/80 rounded-lg text-sm font-medium transition-colors elastic-button"
        >
          Try Again
        </button>
      )}
    </div>
  );
}

/**
 * Simple skeleton for inline use
 */
export function ElasticSkeleton({
  width = 'w-full',
  height = 'h-4',
  className,
}: {
  width?: string;
  height?: string;
  className?: string;
}) {
  return (
    <div
      className={cn('animate-pulse rounded bg-town-accent/30', width, height, className)}
    />
  );
}

export default ElasticPlaceholder;
