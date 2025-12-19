/**
 * FriendlyError - DEPRECATED
 *
 * Use ProjectionError from @/shell/projections/ProjectionError instead.
 * This file is kept for backwards compatibility only.
 *
 * @deprecated Use ProjectionError for new code
 * @see shell/projections/ProjectionError.tsx — canonical error component
 */

import { useNavigate } from 'react-router-dom';
import { Wifi, MapPin, Lock, Clock, Leaf, HelpCircle } from 'lucide-react';
import { ERROR_TITLES, ERROR_HINTS } from '@/constants/messages';

// =============================================================================
// Types — Kept for backwards compatibility
// =============================================================================

export type ErrorType = 'network' | 'notFound' | 'permission' | 'unknown' | 'timeout' | 'empty';

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
// Map old types to new ErrorCategory
// =============================================================================

const TYPE_TO_CATEGORY: Record<ErrorType, string> = {
  network: 'network',
  notFound: 'notFound',
  permission: 'permission',
  timeout: 'timeout',
  empty: 'unknown', // No direct mapping
  unknown: 'unknown',
};

const TYPE_TO_ICON = {
  network: Wifi,
  notFound: MapPin,
  permission: Lock,
  timeout: Clock,
  empty: Leaf,
  unknown: HelpCircle,
};

// =============================================================================
// Component — Uses neutral messaging from messages.ts
// =============================================================================

/**
 * @deprecated Use ProjectionError from @/shell/projections/ProjectionError
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
  const category = TYPE_TO_CATEGORY[type];
  const IconComponent = TYPE_TO_ICON[type];

  // Get neutral titles/hints from centralized messages
  const title = ERROR_TITLES[category] || 'Error';
  const hint = ERROR_HINTS[category] || 'An error occurred.';

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
      iconSize: 32,
      title: 'text-lg',
      subtitle: 'text-sm',
      button: 'px-3 py-1.5 text-sm',
    },
    md: {
      container: 'p-6',
      iconSize: 48,
      title: 'text-xl',
      subtitle: 'text-base',
      button: 'px-4 py-2 text-sm',
    },
    lg: {
      container: 'p-8',
      iconSize: 64,
      title: 'text-2xl',
      subtitle: 'text-lg',
      button: 'px-6 py-3 text-base',
    },
  };

  const classes = sizeClasses[size];

  return (
    <div
      className={`flex flex-col items-center text-center ${classes.container} ${className}`}
      role="alert"
    >
      {/* Icon — Lucide, not emoji */}
      <IconComponent size={classes.iconSize} className="mb-4 text-gray-500" strokeWidth={1.5} />

      {/* Title — neutral */}
      <h2 className={`${classes.title} font-semibold text-white mb-2`}>{title}</h2>

      {/* Hint — actionable */}
      <p className={`${classes.subtitle} text-gray-400 mb-2 max-w-md`}>{hint}</p>

      {/* Custom message if provided */}
      {message && (
        <p className="text-sm text-gray-500 mb-4 font-mono bg-gray-800/50 px-3 py-1 rounded max-w-md break-all">
          {message}
        </p>
      )}

      {/* Actions */}
      <div className="flex gap-3 mt-4">
        {onRetry && (
          <button
            onClick={onRetry}
            className={`${classes.button} bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition-colors`}
          >
            Try Again
          </button>
        )}
        <button
          onClick={handleGoHome}
          className={`${classes.button} bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors`}
        >
          Go Home
        </button>
      </div>
    </div>
  );
}

// =============================================================================
// Specialized Error Components — Kept for backwards compatibility
// =============================================================================

/**
 * @deprecated Use ProjectionError
 */
export function NotFoundError({ onGoHome }: { onGoHome?: () => void }) {
  return (
    <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-gray-900">
      <FriendlyError type="notFound" size="lg" onGoHome={onGoHome} />
    </div>
  );
}

/**
 * @deprecated Use ProjectionError
 */
export function NetworkError({ onRetry }: { onRetry?: () => void }) {
  return <FriendlyError type="network" onRetry={onRetry} />;
}

/**
 * @deprecated Use ProjectionError
 */
export function PermissionError() {
  return <FriendlyError type="permission" />;
}

/**
 * @deprecated Use ProjectionError
 */
export function TimeoutError({ onRetry }: { onRetry?: () => void }) {
  return <FriendlyError type="timeout" onRetry={onRetry} />;
}

// =============================================================================
// Empty State — Kept for backwards compatibility
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
 * Empty state with optional action.
 * Uses Leaf icon instead of emoji.
 */
export function EmptyState({
  message = 'Nothing here yet',
  actionLabel,
  onAction,
  className = '',
}: EmptyStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center text-center p-8 ${className}`}>
      <Leaf size={48} className="mb-4 text-gray-500" strokeWidth={1.5} />
      <p className="text-gray-400 mb-4">{message}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition-colors"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}

export default FriendlyError;
