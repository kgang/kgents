/**
 * Contextual Loading States
 *
 * Delightful loading states with personality that rotate through
 * context-appropriate messages.
 *
 * @see plans/web-refactor/phase5-continuation.md
 */

import { useState, useEffect } from 'react';

// =============================================================================
// Types
// =============================================================================

export type LoadingContext = 'town' | 'workshop' | 'inhabit' | 'pipeline' | 'general';

interface LoadingMessage {
  emoji: string;
  text: string;
}

// =============================================================================
// Message Collections
// =============================================================================

const TOWN_LOADING_MESSAGES: LoadingMessage[] = [
  { emoji: '🏘️', text: 'Waking up the citizens...' },
  { emoji: '☕', text: 'Brewing morning coffee...' },
  { emoji: '🌅', text: 'The sun is rising over Agent Town...' },
  { emoji: '🐓', text: 'The rooster crows...' },
  { emoji: '🌳', text: 'The trees rustle gently...' },
];

const WORKSHOP_LOADING_MESSAGES: LoadingMessage[] = [
  { emoji: '🔧', text: 'Sharpening the tools...' },
  { emoji: '📐', text: 'Measuring twice...' },
  { emoji: '🎨', text: 'Mixing the paints...' },
  { emoji: '🔨', text: 'Setting up the workbench...' },
  { emoji: '💡', text: 'Sparking ideas...' },
];

const INHABIT_LOADING_MESSAGES: LoadingMessage[] = [
  { emoji: '🧘', text: 'Establishing connection...' },
  { emoji: '💭', text: 'Synchronizing thoughts...' },
  { emoji: '🤝', text: 'Building rapport...' },
  { emoji: '✨', text: 'Aligning frequencies...' },
  { emoji: '🌊', text: 'Finding the flow...' },
];

const PIPELINE_LOADING_MESSAGES: LoadingMessage[] = [
  { emoji: '🔗', text: 'Connecting the nodes...' },
  { emoji: '⚡', text: 'Energizing the pipeline...' },
  { emoji: '🌊', text: 'Data flows like water...' },
  { emoji: '🏗️', text: 'Assembling the pieces...' },
];

const GENERAL_LOADING_MESSAGES: LoadingMessage[] = [
  { emoji: '⏳', text: 'Just a moment...' },
  { emoji: '🔄', text: 'Working on it...' },
  { emoji: '✨', text: 'Almost there...' },
  { emoji: '🌟', text: 'Gathering the bits...' },
];

const MESSAGES_BY_CONTEXT: Record<LoadingContext, LoadingMessage[]> = {
  town: TOWN_LOADING_MESSAGES,
  workshop: WORKSHOP_LOADING_MESSAGES,
  inhabit: INHABIT_LOADING_MESSAGES,
  pipeline: PIPELINE_LOADING_MESSAGES,
  general: GENERAL_LOADING_MESSAGES,
};

// =============================================================================
// Components
// =============================================================================

interface ContextualLoaderProps {
  /** Loading context determines message theme */
  context?: LoadingContext;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Additional CSS classes */
  className?: string;
  /** Interval for rotating messages (ms) */
  rotationInterval?: number;
}

/**
 * Contextual loader with rotating messages.
 *
 * @example
 * ```tsx
 * <ContextualLoader context="town" />
 * <ContextualLoader context="workshop" size="lg" />
 * ```
 */
export function ContextualLoader({
  context = 'general',
  size = 'md',
  className = '',
  rotationInterval = 2000,
}: ContextualLoaderProps) {
  const messages = MESSAGES_BY_CONTEXT[context];
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex((i) => (i + 1) % messages.length);
    }, rotationInterval);
    return () => clearInterval(interval);
  }, [messages.length, rotationInterval]);

  const { emoji, text } = messages[messageIndex];

  const sizeClasses = {
    sm: 'text-3xl gap-2',
    md: 'text-5xl gap-4',
    lg: 'text-7xl gap-6',
  };

  const textClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  };

  return (
    <div
      className={`flex flex-col items-center justify-center ${sizeClasses[size]} ${className}`}
      role="status"
      aria-live="polite"
    >
      <div className="loader-bounce">{emoji}</div>
      <p className={`text-gray-400 ${textClasses[size]}`}>{text}</p>
    </div>
  );
}

// =============================================================================
// Skeleton Loaders
// =============================================================================

interface SkeletonProps {
  /** Width (CSS value or tailwind class) */
  width?: string;
  /** Height (CSS value or tailwind class) */
  height?: string;
  /** Additional CSS classes */
  className?: string;
  /** Shape variant */
  variant?: 'text' | 'circular' | 'rectangular';
}

/**
 * Skeleton placeholder with shimmer animation.
 */
export function Skeleton({
  width = '100%',
  height = '1rem',
  className = '',
  variant = 'rectangular',
}: SkeletonProps) {
  const variantClasses = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  };

  return (
    <div
      className={`skeleton-shimmer ${variantClasses[variant]} ${className}`}
      style={{ width, height }}
      aria-hidden="true"
    />
  );
}

/**
 * Skeleton for a citizen card.
 */
export function CitizenCardSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`p-4 bg-town-surface rounded-lg ${className}`}>
      <div className="flex items-center gap-3 mb-3">
        <Skeleton variant="circular" width="40px" height="40px" />
        <div className="flex-1">
          <Skeleton width="60%" height="1rem" className="mb-2" />
          <Skeleton width="40%" height="0.75rem" />
        </div>
      </div>
      <Skeleton width="100%" height="3rem" />
    </div>
  );
}

/**
 * Skeleton for event feed item.
 */
export function EventItemSkeleton() {
  return (
    <div className="flex items-start gap-2 p-2">
      <Skeleton variant="circular" width="24px" height="24px" />
      <div className="flex-1">
        <Skeleton width="80%" height="0.875rem" className="mb-1" />
        <Skeleton width="50%" height="0.75rem" />
      </div>
    </div>
  );
}

// =============================================================================
// Page Loading
// =============================================================================

interface PageLoaderProps {
  context?: LoadingContext;
  message?: string;
}

/**
 * Full-page loading state with contextual message.
 */
export function PageLoader({ context = 'general', message }: PageLoaderProps) {
  return (
    <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-town-bg">
      <ContextualLoader context={context} size="lg" />
      {message && <p className="mt-4 text-gray-500 text-sm">{message}</p>}
    </div>
  );
}

// =============================================================================
// Inline Loading
// =============================================================================

/**
 * Inline loading indicator (three bouncing dots).
 */
export function InlineLoader({ className = '' }: { className?: string }) {
  return (
    <span className={`inline-flex items-center gap-1 ${className}`} role="status">
      <span className="w-1.5 h-1.5 bg-current rounded-full loader-bounce" />
      <span className="w-1.5 h-1.5 bg-current rounded-full loader-bounce loader-bounce-delay-1" />
      <span className="w-1.5 h-1.5 bg-current rounded-full loader-bounce loader-bounce-delay-2" />
      <span className="sr-only">Loading...</span>
    </span>
  );
}

export default ContextualLoader;
