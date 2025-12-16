/**
 * Friendly Error States
 *
 * Empathetic error messages that feel helpful, not hostile.
 * Transform failures into guidance.
 *
 * @see plans/web-refactor/phase5-continuation.md
 */

import { useNavigate } from 'react-router-dom';

// =============================================================================
// Types
// =============================================================================

export type ErrorType = 'network' | 'notFound' | 'permission' | 'unknown' | 'timeout' | 'empty';

interface ErrorContent {
  emoji: string;
  title: string;
  subtitle: string;
  suggestion: string;
}

interface FriendlyErrorProps {
  /** Type of error determines message */
  type: ErrorType;
  /** Custom message to append */
  message?: string;
  /** Retry callback */
  onRetry?: () => void;
  /** Go home callback (defaults to navigate) */
  onGoHome?: () => void;
  /** Additional CSS classes */
  className?: string;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
}

// =============================================================================
// Error Content
// =============================================================================

const ERROR_CONTENT: Record<ErrorType, ErrorContent> = {
  network: {
    emoji: '📡',
    title: 'Lost in the Ether',
    subtitle: 'The connection wandered off. It happens to the best of us.',
    suggestion: 'Check your internet connection and try again.',
  },
  notFound: {
    emoji: '🗺️',
    title: 'Uncharted Territory',
    subtitle: "This place doesn't exist... yet.",
    suggestion: 'Perhaps it was moved, or maybe it\'s waiting to be created.',
  },
  permission: {
    emoji: '🔐',
    title: 'Members Only',
    subtitle: "You'll need the right key to enter here.",
    suggestion: 'Check your permissions or contact an administrator.',
  },
  timeout: {
    emoji: '⏰',
    title: 'Time Stood Still',
    subtitle: 'The request took longer than expected.',
    suggestion: 'Try again, or check if the server is responding.',
  },
  empty: {
    emoji: '🌱',
    title: 'Nothing Here Yet',
    subtitle: 'This space is waiting to be filled.',
    suggestion: 'Create something new, or check back later.',
  },
  unknown: {
    emoji: '🌀',
    title: 'Something Unexpected',
    subtitle: 'Even the wisest agents encounter mysteries.',
    suggestion: 'Try refreshing, or come back in a moment.',
  },
};

// =============================================================================
// Component
// =============================================================================

/**
 * Friendly error display with empathetic messaging.
 *
 * @example
 * ```tsx
 * <FriendlyError type="network" onRetry={() => refetch()} />
 * <FriendlyError type="notFound" size="lg" />
 * ```
 */
export function FriendlyError({
  type,
  message,
  onRetry,
  onGoHome,
  className = '',
  size = 'md',
}: FriendlyErrorProps) {
  const navigate = useNavigate();
  const content = ERROR_CONTENT[type];

  const handleGoHome = () => {
    if (onGoHome) {
      onGoHome();
    } else {
      navigate('/');
    }
  };

  const sizeClasses = {
    sm: {
      container: 'p-4',
      emoji: 'text-4xl',
      title: 'text-lg',
      subtitle: 'text-sm',
      suggestion: 'text-xs',
      button: 'px-3 py-1.5 text-sm',
    },
    md: {
      container: 'p-6',
      emoji: 'text-6xl',
      title: 'text-xl',
      subtitle: 'text-base',
      suggestion: 'text-sm',
      button: 'px-4 py-2 text-sm',
    },
    lg: {
      container: 'p-8',
      emoji: 'text-8xl',
      title: 'text-2xl',
      subtitle: 'text-lg',
      suggestion: 'text-base',
      button: 'px-6 py-3 text-base',
    },
  };

  const classes = sizeClasses[size];

  return (
    <div
      className={`flex flex-col items-center text-center ${classes.container} ${className}`}
      role="alert"
    >
      {/* Emoji with subtle animation */}
      <div className={`${classes.emoji} mb-4 breathe`}>{content.emoji}</div>

      {/* Title */}
      <h2 className={`${classes.title} font-semibold text-white mb-2`}>
        {content.title}
      </h2>

      {/* Subtitle */}
      <p className={`${classes.subtitle} text-gray-400 mb-2 max-w-md`}>
        {content.subtitle}
      </p>

      {/* Custom message if provided */}
      {message && (
        <p className={`${classes.suggestion} text-gray-500 mb-4 font-mono bg-town-surface/50 px-3 py-1 rounded max-w-md break-all`}>
          {message}
        </p>
      )}

      {/* Suggestion */}
      <p className={`${classes.suggestion} text-gray-500 mb-6 max-w-md`}>
        {content.suggestion}
      </p>

      {/* Actions */}
      <div className="flex gap-3">
        {onRetry && (
          <button
            onClick={onRetry}
            className={`${classes.button} bg-town-highlight text-white rounded-lg hover:bg-town-highlight/80 transition-colors elastic-button`}
          >
            Try Again
          </button>
        )}
        <button
          onClick={handleGoHome}
          className={`${classes.button} bg-town-surface text-gray-300 rounded-lg hover:bg-town-accent transition-colors elastic-button`}
        >
          Go Home
        </button>
      </div>
    </div>
  );
}

// =============================================================================
// Specialized Error Components
// =============================================================================

/**
 * 404 Not Found page error.
 */
export function NotFoundError({ onGoHome }: { onGoHome?: () => void }) {
  return (
    <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-town-bg">
      <FriendlyError type="notFound" size="lg" onGoHome={onGoHome} />
    </div>
  );
}

/**
 * Network error with retry.
 */
export function NetworkError({ onRetry }: { onRetry?: () => void }) {
  return <FriendlyError type="network" onRetry={onRetry} />;
}

/**
 * Permission denied error.
 */
export function PermissionError() {
  return <FriendlyError type="permission" />;
}

/**
 * Timeout error with retry.
 */
export function TimeoutError({ onRetry }: { onRetry?: () => void }) {
  return <FriendlyError type="timeout" onRetry={onRetry} />;
}

// =============================================================================
// Empty State (friendly, not an error)
// =============================================================================

interface EmptyStateProps {
  /** Context-specific message */
  message?: string;
  /** Call to action label */
  actionLabel?: string;
  /** Action callback */
  onAction?: () => void;
  /** Custom emoji */
  emoji?: string;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Friendly empty state with optional action.
 */
export function EmptyState({
  message = 'Nothing here yet...',
  actionLabel,
  onAction,
  emoji = '🌱',
  className = '',
}: EmptyStateProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center text-center p-8 ${className}`}
    >
      <div className="text-5xl mb-4 breathe">{emoji}</div>
      <p className="text-gray-400 mb-4">{message}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="px-4 py-2 bg-town-highlight text-white rounded-lg hover:bg-town-highlight/80 transition-colors elastic-button"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}

export default FriendlyError;
