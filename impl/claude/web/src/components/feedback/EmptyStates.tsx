/**
 * Empty States with Personality
 *
 * Transform empty states from boring to inviting.
 * Each context gets a tailored message that feels appropriate.
 *
 * @see plans/web-refactor/phase5-continuation.md
 */

import { type ReactNode } from 'react';

// =============================================================================
// Types
// =============================================================================

export type EmptyStateContext =
  | 'town'
  | 'workshop'
  | 'event-feed'
  | 'pipeline'
  | 'artifacts'
  | 'history'
  | 'citizens'
  | 'search'
  | 'general';

interface EmptyStateConfig {
  emoji: string;
  title: string;
  message: string;
  actionLabel?: string;
}

interface EmptyStateProps {
  /** Context determines the message */
  context?: EmptyStateContext;
  /** Override the default title */
  title?: string;
  /** Override the default message */
  message?: string;
  /** Custom emoji */
  emoji?: string;
  /** Action button label */
  actionLabel?: string;
  /** Action callback */
  onAction?: () => void;
  /** Additional CSS classes */
  className?: string;
  /** Custom content to render below message */
  children?: ReactNode;
}

// =============================================================================
// Empty State Configurations
// =============================================================================

const EMPTY_STATES: Record<EmptyStateContext, EmptyStateConfig> = {
  town: {
    emoji: '🏘️',
    title: 'A Quiet Town',
    message: 'The streets are empty, awaiting their first inhabitants...',
    actionLabel: 'Spawn Citizens',
  },
  workshop: {
    emoji: '🔧',
    title: 'The Workshop is Ready',
    message: 'What shall we build today?',
    actionLabel: 'Start a Task',
  },
  'event-feed': {
    emoji: '🌅',
    title: 'All is Peaceful',
    message: 'No events yet... for now.',
  },
  pipeline: {
    emoji: '✨',
    title: 'An Empty Canvas',
    message: 'Every masterpiece starts here. Drag agents to compose them.',
    actionLabel: 'Add First Agent',
  },
  artifacts: {
    emoji: '🌱',
    title: 'Nothing Created Yet',
    message: "The builders haven't crafted anything yet. Give them a task!",
    actionLabel: 'Start Building',
  },
  history: {
    emoji: '📜',
    title: 'No History Yet',
    message: 'The story is just beginning...',
  },
  citizens: {
    emoji: '👥',
    title: 'No Citizens',
    message: 'The town awaits its first residents.',
    actionLabel: 'Spawn a Citizen',
  },
  search: {
    emoji: '🔍',
    title: 'No Results',
    message: 'Try adjusting your search or filters.',
  },
  general: {
    emoji: '🌿',
    title: 'Nothing Here Yet',
    message: 'This space is waiting to be filled.',
  },
};

// =============================================================================
// Component
// =============================================================================

/**
 * Empty state with personality.
 *
 * @example
 * ```tsx
 * // Context-aware
 * <EmptyState context="workshop" onAction={startTask} />
 *
 * // Custom
 * <EmptyState
 *   emoji="🎨"
 *   title="No Themes"
 *   message="Create your first theme to customize the experience."
 *   actionLabel="Create Theme"
 *   onAction={createTheme}
 * />
 * ```
 */
export function EmptyState({
  context = 'general',
  title,
  message,
  emoji,
  actionLabel,
  onAction,
  className = '',
  children,
}: EmptyStateProps) {
  const config = EMPTY_STATES[context];

  const displayEmoji = emoji ?? config.emoji;
  const displayTitle = title ?? config.title;
  const displayMessage = message ?? config.message;
  const displayActionLabel = actionLabel ?? config.actionLabel;

  return (
    <div className={`empty-state ${className}`} role="status">
      {/* Animated emoji */}
      <div className="empty-state-emoji">{displayEmoji}</div>

      {/* Title */}
      <h3 className="empty-state-title">{displayTitle}</h3>

      {/* Message */}
      <p className="empty-state-message">{displayMessage}</p>

      {/* Custom content */}
      {children}

      {/* Action button */}
      {displayActionLabel && onAction && (
        <button
          onClick={onAction}
          className="mt-4 px-4 py-2 bg-town-highlight text-white rounded-lg hover:bg-town-highlight/80 transition-colors elastic-button"
        >
          {displayActionLabel}
        </button>
      )}
    </div>
  );
}

// =============================================================================
// Pre-configured Empty States
// =============================================================================

/**
 * Empty state for Town page (no citizens).
 */
export function TownEmptyState({ onSpawn }: { onSpawn?: () => void }) {
  return <EmptyState context="town" onAction={onSpawn} />;
}

/**
 * Empty state for Workshop (no active task).
 */
export function WorkshopEmptyState({ onStart }: { onStart?: () => void }) {
  return <EmptyState context="workshop" onAction={onStart} />;
}

/**
 * Empty state for Event Feed.
 */
export function EventFeedEmptyState() {
  return <EmptyState context="event-feed" />;
}

/**
 * Empty state for Pipeline Canvas.
 */
export function PipelineEmptyState({ onAdd }: { onAdd?: () => void }) {
  return <EmptyState context="pipeline" onAction={onAdd} />;
}

/**
 * Empty state for Artifacts.
 */
export function ArtifactsEmptyState({ onStart }: { onStart?: () => void }) {
  return <EmptyState context="artifacts" onAction={onStart} />;
}

/**
 * Empty state for History view.
 */
export function HistoryEmptyState() {
  return <EmptyState context="history" />;
}

/**
 * Empty state for Search results.
 */
export function SearchEmptyState({ query }: { query?: string }) {
  return (
    <EmptyState
      context="search"
      message={query ? `No results for "${query}"` : 'Try searching for something.'}
    />
  );
}

// =============================================================================
// Inline Empty State (smaller)
// =============================================================================

interface InlineEmptyStateProps {
  message: string;
  emoji?: string;
  className?: string;
}

/**
 * Smaller inline empty state for use in cards/panels.
 */
export function InlineEmptyState({
  message,
  emoji = '🌱',
  className = '',
}: InlineEmptyStateProps) {
  return (
    <div className={`flex items-center justify-center gap-2 py-4 text-gray-500 ${className}`}>
      <span>{emoji}</span>
      <span className="text-sm">{message}</span>
    </div>
  );
}

export default EmptyState;
