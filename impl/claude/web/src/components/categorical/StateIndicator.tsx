/**
 * StateIndicator: Unified phase badge with glow and animation.
 *
 * A reusable component for displaying polynomial agent state across
 * Town citizens, Park crisis phases, timers, and consent debt levels.
 *
 * Uses centralized PHASE_GLOW design tokens for visual consistency.
 *
 * @see plans/park-town-design-overhaul.md
 * @see constants/colors.ts - PHASE_GLOW tokens
 */

import { cn } from '@/lib/utils';
import type { LucideIcon } from 'lucide-react';
import {
  Circle,
  Users,
  Briefcase,
  Brain,
  Moon,
  AlertTriangle,
  Activity,
  RefreshCw,
  CheckCircle,
  Clock,
  Timer,
  Zap,
  Eye,
  Flame,
  Snowflake,
  Target,
} from 'lucide-react';
import { PHASE_GLOW } from '@/constants';

// =============================================================================
// Types
// =============================================================================

export type StateCategory = 'idle' | 'active' | 'warning' | 'critical' | 'success' | 'neutral';

export interface StateIndicatorProps {
  /** The state/phase label to display */
  label: string;
  /** State category determines color and glow */
  category?: StateCategory;
  /** Custom color override (hex or CSS color) */
  color?: string;
  /** Optional icon to display */
  icon?: LucideIcon;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Whether to show the glow effect */
  glow?: boolean;
  /** Whether to animate (pulse) */
  animate?: boolean;
  /** Additional className */
  className?: string;
  /** Click handler */
  onClick?: () => void;
}

// =============================================================================
// Configuration
// =============================================================================

const CATEGORY_COLORS: Record<StateCategory, string> = {
  idle: '#64748b', // slate
  active: '#22c55e', // green
  warning: '#f59e0b', // amber
  critical: '#ef4444', // red
  success: '#22c55e', // green
  neutral: '#64748b', // slate
};

/**
 * Map state categories to centralized PHASE_GLOW tokens.
 * This ensures visual consistency across all state indicators.
 */
const GLOW_SHADOWS: Record<StateCategory, string> = PHASE_GLOW;

const SIZE_CONFIG = {
  sm: {
    padding: 'px-2 py-0.5',
    text: 'text-xs',
    icon: 'w-3 h-3',
    gap: 'gap-1',
  },
  md: {
    padding: 'px-3 py-1',
    text: 'text-sm',
    icon: 'w-4 h-4',
    gap: 'gap-1.5',
  },
  lg: {
    padding: 'px-4 py-1.5',
    text: 'text-base',
    icon: 'w-5 h-5',
    gap: 'gap-2',
  },
};

// =============================================================================
// State-to-Icon Mapping
// =============================================================================

/** Default icons for common state names */
const STATE_ICONS: Record<string, LucideIcon> = {
  // Citizen phases
  idle: Circle,
  socializing: Users,
  working: Briefcase,
  reflecting: Brain,
  resting: Moon,

  // Crisis phases
  normal: CheckCircle,
  incident: AlertTriangle,
  response: Activity,
  recovery: RefreshCw,

  // Timer states
  pending: Clock,
  active: Timer,
  warning: AlertTriangle,
  critical: Zap,
  expired: AlertTriangle,

  // Consent debt
  healthy: CheckCircle,
  elevated: AlertTriangle,
  high: Flame,

  // Director states
  observing: Eye,
  building: Flame,
  injecting: Zap,
  cooling: Snowflake,
  intervening: Target,
};

/** Get icon for a state name (case-insensitive) */
function getStateIcon(label: string): LucideIcon | undefined {
  const key = label.toLowerCase().replace(/[^a-z]/g, '');
  return STATE_ICONS[key];
}

/** Infer category from state name */
function inferCategory(label: string): StateCategory {
  const lower = label.toLowerCase();

  // Critical states
  if (lower.includes('critical') || lower.includes('expired') || lower.includes('incident')) {
    return 'critical';
  }

  // Warning states
  if (lower.includes('warning') || lower.includes('elevated') || lower.includes('high')) {
    return 'warning';
  }

  // Active states
  if (
    lower.includes('active') ||
    lower.includes('working') ||
    lower.includes('socializing') ||
    lower.includes('response') ||
    lower.includes('building') ||
    lower.includes('injecting')
  ) {
    return 'active';
  }

  // Success states
  if (
    lower.includes('healthy') ||
    lower.includes('normal') ||
    lower.includes('recovery') ||
    lower.includes('success')
  ) {
    return 'success';
  }

  // Rest states
  if (lower.includes('resting') || lower.includes('cooling')) {
    return 'neutral';
  }

  return 'idle';
}

// =============================================================================
// Component
// =============================================================================

export function StateIndicator({
  label,
  category,
  color,
  icon,
  size = 'md',
  glow = true,
  animate = false,
  className,
  onClick,
}: StateIndicatorProps) {
  // Infer category if not provided
  const effectiveCategory = category ?? inferCategory(label);
  const effectiveColor = color ?? CATEGORY_COLORS[effectiveCategory];
  const Icon = icon ?? getStateIcon(label);
  const sizeConfig = SIZE_CONFIG[size];

  const isClickable = !!onClick;

  // Handle keyboard navigation for clickable indicators
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!onClick) return;
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick();
    }
  };

  // Generate descriptive aria-label for screen readers
  const ariaLabel = `${label} state${effectiveCategory !== 'neutral' ? `, ${effectiveCategory}` : ''}${isClickable ? ', clickable' : ''}`;

  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full font-medium transition-all duration-200',
        // Reduced motion support: disable transitions and hover effects
        'motion-reduce:transition-none',
        sizeConfig.padding,
        sizeConfig.text,
        sizeConfig.gap,
        isClickable &&
          'cursor-pointer hover:scale-105 motion-reduce:hover:scale-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500',
        animate && 'animate-pulse motion-reduce:animate-none',
        className
      )}
      style={{
        backgroundColor: `${effectiveColor}22`,
        color: effectiveColor,
        boxShadow: glow ? GLOW_SHADOWS[effectiveCategory] : undefined,
        border: `1px solid ${effectiveColor}40`,
      }}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      role={isClickable ? 'button' : 'status'}
      tabIndex={isClickable ? 0 : undefined}
      aria-label={ariaLabel}
      aria-live={animate ? 'polite' : undefined}
    >
      {Icon && <Icon className={sizeConfig.icon} aria-hidden="true" />}
      <span>{label}</span>
    </div>
  );
}

// =============================================================================
// Preset State Indicators
// =============================================================================

interface PresetIndicatorProps {
  state: string;
  size?: 'sm' | 'md' | 'lg';
  glow?: boolean;
  className?: string;
  onClick?: () => void;
}

/** Citizen phase indicator for Town */
export function CitizenPhaseIndicator({ state, ...props }: PresetIndicatorProps) {
  const category = inferCategory(state);
  return <StateIndicator label={state} category={category} {...props} />;
}

/** Crisis phase indicator for Park */
export function CrisisPhaseIndicator({ state, ...props }: PresetIndicatorProps) {
  const categoryMap: Record<string, StateCategory> = {
    NORMAL: 'success',
    INCIDENT: 'critical',
    RESPONSE: 'warning',
    RECOVERY: 'active',
  };
  return <StateIndicator label={state} category={categoryMap[state] ?? 'neutral'} {...props} />;
}

/** Timer state indicator */
export function TimerStateIndicator({ state, ...props }: PresetIndicatorProps) {
  const categoryMap: Record<string, StateCategory> = {
    PENDING: 'neutral',
    ACTIVE: 'active',
    WARNING: 'warning',
    CRITICAL: 'critical',
    EXPIRED: 'critical',
  };
  return <StateIndicator label={state} category={categoryMap[state] ?? 'neutral'} {...props} />;
}

/** Consent debt indicator */
export function ConsentDebtIndicator({ state, ...props }: PresetIndicatorProps) {
  const categoryMap: Record<string, StateCategory> = {
    HEALTHY: 'success',
    ELEVATED: 'warning',
    HIGH: 'warning',
    CRITICAL: 'critical',
  };
  return <StateIndicator label={state} category={categoryMap[state] ?? 'neutral'} {...props} />;
}

/** Director state indicator */
export function DirectorStateIndicator({ state, ...props }: PresetIndicatorProps) {
  const categoryMap: Record<string, StateCategory> = {
    OBSERVING: 'neutral',
    BUILDING: 'warning',
    INJECTING: 'active',
    COOLING: 'neutral',
    INTERVENING: 'critical',
  };
  return <StateIndicator label={state} category={categoryMap[state] ?? 'neutral'} {...props} />;
}

export default StateIndicator;
