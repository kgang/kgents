/**
 * Toast: Individual notification toast component.
 *
 * Displays a notification with personality (emojis, colors by type).
 * Auto-dismisses after duration if set.
 *
 * @see plans/web-refactor/defensive-lifecycle.md
 */

import { useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  duration?: number;
}

export interface ToastProps {
  notification: Notification;
  onDismiss: () => void;
}

// =============================================================================
// Constants
// =============================================================================

const typeEmojis: Record<NotificationType, string> = {
  info: '💡',
  success: '✅',
  warning: '⚠️',
  error: '🚫',
};

const typeClasses: Record<NotificationType, string> = {
  info: 'bg-blue-900/90 border-blue-500/50 text-blue-100',
  success: 'bg-green-900/90 border-green-500/50 text-green-100',
  warning: 'bg-yellow-900/90 border-yellow-500/50 text-yellow-100',
  error: 'bg-red-900/90 border-red-500/50 text-red-100',
};

// =============================================================================
// Component
// =============================================================================

/**
 * Individual toast notification.
 *
 * @example
 * ```tsx
 * <Toast
 *   notification={{
 *     id: '1',
 *     type: 'success',
 *     title: 'Town created!',
 *     message: 'Your new town is ready.',
 *     duration: 3000,
 *   }}
 *   onDismiss={() => removeNotification('1')}
 * />
 * ```
 */
export function Toast({ notification, onDismiss }: ToastProps) {
  const { type, title, message, duration } = notification;

  // Auto-dismiss after duration
  useEffect(() => {
    if (duration && duration > 0) {
      const timer = setTimeout(onDismiss, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onDismiss]);

  // Handle keyboard dismiss
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      if (event.key === 'Escape') {
        onDismiss();
      }
    },
    [onDismiss]
  );

  return (
    <div
      className={cn(
        'flex items-start gap-3 p-4 rounded-lg border shadow-lg backdrop-blur-sm',
        'animate-in slide-in-from-right-full duration-300',
        'min-w-[280px] max-w-[380px]',
        typeClasses[type]
      )}
      role="alert"
      aria-live="polite"
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      {/* Icon */}
      <span className="text-xl flex-shrink-0" aria-hidden="true">
        {typeEmojis[type]}
      </span>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p className="font-medium">{title}</p>
        {message && <p className="text-sm opacity-80 mt-1">{message}</p>}
      </div>

      {/* Dismiss button */}
      <button
        onClick={onDismiss}
        className="flex-shrink-0 opacity-60 hover:opacity-100 transition-opacity p-1 -m-1"
        aria-label="Dismiss notification"
      >
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>
  );
}

export default Toast;
