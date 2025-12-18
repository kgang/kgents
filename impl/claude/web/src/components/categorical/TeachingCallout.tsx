/**
 * TeachingCallout: Pedagogical element for categorical concepts.
 *
 * Displays teaching content with gradient backgrounds categorized by type.
 * Used throughout Town and Park to explain the underlying categorical model.
 *
 * @see plans/park-town-design-overhaul.md
 */

import { Lightbulb, BookOpen, Sparkles, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

export type TeachingCategory = 'categorical' | 'operational' | 'conceptual' | 'insight';

export interface TeachingCalloutProps {
  /** The teaching content to display */
  children: React.ReactNode;
  /** Category determines gradient and icon */
  category?: TeachingCategory;
  /** Optional title override */
  title?: string;
  /** Compact mode for inline use */
  compact?: boolean;
  /** Whether this callout can be dismissed */
  dismissible?: boolean;
  /** Callback when dismissed */
  onDismiss?: () => void;
  /** Additional className */
  className?: string;
}

// =============================================================================
// Configuration
// =============================================================================

const CATEGORY_CONFIG: Record<
  TeachingCategory,
  {
    gradient: string;
    borderColor: string;
    iconColor: string;
    icon: typeof Lightbulb;
    defaultTitle: string;
  }
> = {
  categorical: {
    gradient: 'from-blue-500/20 to-purple-500/20',
    borderColor: 'border-purple-500',
    iconColor: 'text-purple-400',
    icon: Sparkles,
    defaultTitle: 'Categorical',
  },
  operational: {
    gradient: 'from-amber-500/20 to-pink-500/20',
    borderColor: 'border-amber-500',
    iconColor: 'text-amber-400',
    icon: Zap,
    defaultTitle: 'Operation',
  },
  conceptual: {
    gradient: 'from-green-500/20 to-blue-500/20',
    borderColor: 'border-green-500',
    iconColor: 'text-green-400',
    icon: BookOpen,
    defaultTitle: 'Concept',
  },
  insight: {
    gradient: 'from-cyan-500/20 to-indigo-500/20',
    borderColor: 'border-cyan-500',
    iconColor: 'text-cyan-400',
    icon: Lightbulb,
    defaultTitle: 'Insight',
  },
};

// =============================================================================
// Component
// =============================================================================

export function TeachingCallout({
  children,
  category = 'insight',
  title,
  compact = false,
  dismissible = false,
  onDismiss,
  className,
}: TeachingCalloutProps) {
  const config = CATEGORY_CONFIG[category];
  const Icon = config.icon;
  const displayTitle = title ?? config.defaultTitle;

  if (compact) {
    return (
      <div
        className={cn(
          'flex items-start gap-2 text-sm',
          config.iconColor,
          className
        )}
      >
        <Icon className="w-4 h-4 mt-0.5 flex-shrink-0" />
        <span className="text-gray-300">{children}</span>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'relative bg-gradient-to-r rounded-r-lg p-4 border-l-4',
        config.gradient,
        config.borderColor,
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-1">
        <div className={cn('flex items-center gap-2 text-xs uppercase tracking-wider', config.iconColor)}>
          <Icon className="w-3 h-3" />
          {displayTitle}
        </div>
        {dismissible && onDismiss && (
          <button
            onClick={onDismiss}
            className="text-gray-500 hover:text-gray-300 transition-colors"
            aria-label="Dismiss"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Content */}
      <div className="text-sm text-gray-200">{children}</div>
    </div>
  );
}

// =============================================================================
// Preset Teaching Messages
// =============================================================================

export const TEACHING_MESSAGES = {
  // Town
  right_to_rest: "RESTING only accepts 'wake' - the Right to Rest enforced by directions. Citizens cannot be disturbed while resting.",
  operad_arity: 'Operad operations have arity - greet takes 2 citizens, solo takes 1. TOWN_OPERAD defines which compositions are valid.',
  citizen_polynomial: 'Each citizen follows a state machine with 5 phases. The polynomial functor maps each phase to valid inputs.',

  // Park
  consent_debt: 'Consent debt constrains the director. High debt blocks injection until the guest has time to process.',
  invisible_director: 'The director is invisible - guests never feel directed. Serendipity appears as lucky coincidence, not orchestration.',
  timer_polynomial: 'Timers are polynomial agents - their phase determines valid operations. At CRITICAL, force becomes more expensive.',
  crisis_polynomial: 'The crisis polynomial defines when transitions are valid. Force spending affects consent debt.',

  // General
  polynomial_intro: 'PolyAgent[S, A, B] captures mode-dependent behavior. Each state determines what inputs are valid.',
  operad_intro: 'Operads define the grammar of valid operations. Laws ensure compositions preserve meaning.',
  witness_trace: 'Every state change is recorded. time.*.witness reveals the narrative arc of your session.',
  observer_dependent: 'Different observers see different affordances. This is AGENTESE in action - the handle yields based on who is grasping.',
} as const;

export type TeachingMessageKey = keyof typeof TEACHING_MESSAGES;

/** Helper to get a teaching message */
export function getTeachingMessage(key: TeachingMessageKey): string {
  return TEACHING_MESSAGES[key];
}

export default TeachingCallout;
