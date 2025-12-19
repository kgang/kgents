/**
 * ContextBadge - AGENTESE Context Indicator
 *
 * A visual badge showing which AGENTESE context a path belongs to.
 * Uses context-specific colors and icons from the design system.
 *
 * "Five Contexts: world, self, concept, void, time — no kitchen-sink anti-pattern"
 *
 * @see spec/protocols/agentese.md
 * @see spec/principles.md - AD-010: The Habitat Guarantee
 */

import { memo } from 'react';
import type { AGENTESEContext } from '@/lib/habitat';
import { CONTEXT_INFO, getContextInfo } from '@/constants/contexts';

// =============================================================================
// Types
// =============================================================================

export interface ContextBadgeProps {
  /** AGENTESE context to display */
  context: AGENTESEContext;
  /** Badge size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Show label text alongside icon */
  showLabel?: boolean;
  /** Show description tooltip */
  showTooltip?: boolean;
  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Size Configurations
// =============================================================================

const SIZE_CONFIG = {
  sm: {
    container: 'px-1.5 py-0.5 text-xs gap-1',
    icon: 'w-3 h-3',
  },
  md: {
    container: 'px-2 py-1 text-sm gap-1.5',
    icon: 'w-4 h-4',
  },
  lg: {
    container: 'px-3 py-1.5 text-base gap-2',
    icon: 'w-5 h-5',
  },
} as const;

// =============================================================================
// Component
// =============================================================================

/**
 * ContextBadge displays the AGENTESE context with icon and optional label.
 *
 * @example
 * ```tsx
 * // Icon only (compact)
 * <ContextBadge context="world" />
 *
 * // With label
 * <ContextBadge context="self" showLabel />
 *
 * // Large size with tooltip
 * <ContextBadge context="concept" size="lg" showLabel showTooltip />
 * ```
 */
export const ContextBadge = memo(function ContextBadge({
  context,
  size = 'md',
  showLabel = false,
  showTooltip = true,
  className = '',
}: ContextBadgeProps) {
  const info = getContextInfo(context);
  const Icon = info.icon;
  const sizeConfig = SIZE_CONFIG[size];

  return (
    <span
      className={`
        inline-flex items-center rounded-full font-medium
        ${info.bgColor} ${info.color}
        ${sizeConfig.container}
        ${className}
      `}
      title={showTooltip ? info.description : undefined}
      aria-label={`${info.label} context: ${info.description}`}
    >
      <Icon className={sizeConfig.icon} aria-hidden="true" />
      {showLabel && <span>{info.label}</span>}
    </span>
  );
});

// =============================================================================
// Exports
// =============================================================================

export default ContextBadge;

/**
 * All available contexts for iteration.
 */
export const ALL_CONTEXTS: AGENTESEContext[] = Object.keys(CONTEXT_INFO) as AGENTESEContext[];
