/**
 * Empathy Error Component
 *
 * Humane error states with personality - not hostile, but helpful.
 * Transforms failures into guidance with warmth.
 *
 * Foundation 5: Personality & Joy - Empathetic Errors
 *
 * @example
 * ```tsx
 * <EmpathyError
 *   type="network"
 *   title="Lost in the void..."
 *   subtitle="The connection wandered off. Let's bring it back."
 *   action="Reconnect"
 *   onAction={handleReconnect}
 * />
 * ```
 */

import type { CSSProperties } from 'react';
import { motion } from 'framer-motion';
import { Shake } from './Shake';
import { Breathe } from './Breathe';
import { useMotionPreferences } from './useMotionPreferences';

export type ErrorType = 'network' | 'notfound' | 'permission' | 'timeout' | 'validation' | 'unknown';

export interface EmpathyErrorProps {
  /** Error type determines default messaging */
  type: ErrorType;
  /** Override default title */
  title?: string;
  /** Override default subtitle */
  subtitle?: string;
  /** Technical details (shown in collapsible) */
  details?: string;
  /** Primary action button text */
  action?: string;
  /** Primary action callback */
  onAction?: () => void;
  /** Secondary action button text */
  secondaryAction?: string;
  /** Secondary action callback */
  onSecondaryAction?: () => void;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Additional CSS classes */
  className?: string;
  /** Additional inline styles */
  style?: CSSProperties;
}

// =============================================================================
// Error Configuration
// =============================================================================

interface ErrorConfig {
  emoji: string;
  title: string;
  subtitle: string;
  suggestion: string;
  actionLabel: string;
}

const ERROR_CONFIG: Record<ErrorType, ErrorConfig> = {
  network: {
    emoji: '📡',
    title: 'Lost in the void...',
    subtitle: 'The connection wandered off. It happens to the best of us.',
    suggestion: 'Check your internet connection and try again.',
    actionLabel: 'Reconnect',
  },
  notfound: {
    emoji: '🗺️',
    title: 'Nothing here...',
    subtitle: "This place doesn't exist yet. Maybe it's waiting to be created.",
    suggestion: 'Double-check the URL or navigate back home.',
    actionLabel: 'Go Home',
  },
  permission: {
    emoji: '🔐',
    title: "Door's locked...",
    subtitle: "You'll need the right key to enter here.",
    suggestion: 'Check your permissions or contact an administrator.',
    actionLabel: 'Request Access',
  },
  timeout: {
    emoji: '⏰',
    title: 'Taking too long...',
    subtitle: 'The universe is slow today. Even servers need a moment sometimes.',
    suggestion: 'Try again, or check back in a moment.',
    actionLabel: 'Try Again',
  },
  validation: {
    emoji: '📝',
    title: 'Something needs fixing...',
    subtitle: "The input wasn't quite right. Let's correct it together.",
    suggestion: 'Review the highlighted fields and try again.',
    actionLabel: 'Review',
  },
  unknown: {
    emoji: '🌀',
    title: 'Something unexpected...',
    subtitle: 'Even the wisest agents encounter mysteries.',
    suggestion: 'Try refreshing, or come back in a moment.',
    actionLabel: 'Refresh',
  },
};

// =============================================================================
// Size Configuration
// =============================================================================

const SIZE_CONFIG = {
  sm: {
    container: 'p-4',
    emoji: 'text-3xl',
    title: 'text-base',
    subtitle: 'text-sm',
    suggestion: 'text-xs',
    button: 'px-3 py-1.5 text-sm',
  },
  md: {
    container: 'p-6',
    emoji: 'text-5xl',
    title: 'text-lg',
    subtitle: 'text-base',
    suggestion: 'text-sm',
    button: 'px-4 py-2 text-sm',
  },
  lg: {
    container: 'p-8',
    emoji: 'text-7xl',
    title: 'text-xl',
    subtitle: 'text-lg',
    suggestion: 'text-base',
    button: 'px-6 py-3 text-base',
  },
};

// =============================================================================
// Component
// =============================================================================

/**
 * Empathetic error display with personality and actionable guidance.
 */
export function EmpathyError({
  type,
  title,
  subtitle,
  details,
  action,
  onAction,
  secondaryAction,
  onSecondaryAction,
  size = 'md',
  className = '',
  style,
}: EmpathyErrorProps) {
  const { shouldAnimate } = useMotionPreferences();
  const config = ERROR_CONFIG[type];
  const sizeConfig = SIZE_CONFIG[size];

  const displayTitle = title || config.title;
  const displaySubtitle = subtitle || config.subtitle;
  const displayAction = action || config.actionLabel;

  return (
    <motion.div
      className={`flex flex-col items-center text-center ${sizeConfig.container} ${className}`}
      style={style}
      initial={shouldAnimate ? { opacity: 0, y: 8 } : undefined}
      animate={shouldAnimate ? { opacity: 1, y: 0 } : undefined}
      transition={{ duration: 0.3 }}
      role="alert"
    >
      {/* Emoji with gentle breathing animation */}
      <Breathe intensity={0.3} speed="slow">
        <span className={`${sizeConfig.emoji} mb-4`}>{config.emoji}</span>
      </Breathe>

      {/* Title */}
      <h2 className={`${sizeConfig.title} font-semibold text-white mb-2`}>
        {displayTitle}
      </h2>

      {/* Subtitle */}
      <p className={`${sizeConfig.subtitle} text-gray-400 mb-2 max-w-md`}>
        {displaySubtitle}
      </p>

      {/* Technical details */}
      {details && (
        <div className={`${sizeConfig.suggestion} text-gray-500 mb-4 font-mono bg-gray-800/50 px-3 py-2 rounded max-w-md break-all`}>
          {details}
        </div>
      )}

      {/* Suggestion */}
      <p className={`${sizeConfig.suggestion} text-gray-500 mb-6 max-w-md`}>
        {config.suggestion}
      </p>

      {/* Actions */}
      <div className="flex gap-3">
        {onAction && (
          <button
            onClick={onAction}
            className={`${sizeConfig.button} bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors`}
          >
            {displayAction}
          </button>
        )}
        {onSecondaryAction && secondaryAction && (
          <button
            onClick={onSecondaryAction}
            className={`${sizeConfig.button} bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg transition-colors`}
          >
            {secondaryAction}
          </button>
        )}
      </div>
    </motion.div>
  );
}

/**
 * Inline error for form fields and small contexts.
 */
export interface InlineErrorProps {
  /** Error message */
  message: string;
  /** Trigger shake animation */
  shake?: boolean;
  /** Additional CSS classes */
  className?: string;
}

export function InlineError({
  message,
  shake = false,
  className = '',
}: InlineErrorProps) {
  return (
    <Shake trigger={shake} intensity="gentle">
      <p className={`text-sm text-red-400 flex items-center gap-1.5 ${className}`}>
        <span>⚠️</span>
        {message}
      </p>
    </Shake>
  );
}

/**
 * Full-page error wrapper.
 */
export function FullPageError(props: EmpathyErrorProps) {
  return (
    <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-gray-900">
      <EmpathyError {...props} size="lg" />
    </div>
  );
}

export default EmpathyError;
