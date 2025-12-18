/**
 * OrganicToast
 *
 * Toast notification that grows from a seed point.
 * Implements "Growing" animation with Living Earth color palette.
 *
 * @see plans/crown-jewels-genesis.md - Phase 1: Foundation
 * @see hooks/useGrowing.ts
 */

import React, { useEffect } from 'react';
import { useGrowing } from '@/hooks/useGrowing';
import { LIVING_EARTH } from '@/constants';

// =============================================================================
// Types
// =============================================================================

/**
 * Toast type - determines Living Earth color.
 */
export type OrganicToastType = 'info' | 'success' | 'warning' | 'learning';

/**
 * Origin direction for growth animation.
 */
export type ToastOrigin = 'top' | 'bottom' | 'left' | 'right';

export interface OrganicToastProps {
  /**
   * Toast type - determines Living Earth color.
   * - info: Amber (warm, informative glow)
   * - success: Sage (nature, growth, completion)
   * - warning: Copper (urgent attention)
   * - learning: Honey (soft, inviting glow)
   */
  type: OrganicToastType;

  /**
   * Origin direction for growth.
   * Determines transform-origin for the growth animation.
   *
   * Default: 'top'
   */
  origin?: ToastOrigin;

  /**
   * Auto-dismiss duration in ms.
   * Set to 0 to prevent auto-dismiss.
   *
   * Default: 5000
   */
  duration?: number;

  /**
   * Callback when toast is dismissed (either auto or manual).
   */
  onDismiss?: () => void;

  /**
   * Additional className for the toast container.
   */
  className?: string;

  /**
   * Toast content.
   */
  children: React.ReactNode;
}

// =============================================================================
// Configuration
// =============================================================================

/** Type to Living Earth color mapping */
const TYPE_COLORS: Record<OrganicToastType, { bg: string; border: string; text: string }> = {
  info: {
    bg: LIVING_EARTH.bark, // Warm surface
    border: LIVING_EARTH.amber, // Amber glow
    text: LIVING_EARTH.lantern, // Warm white
  },
  success: {
    bg: LIVING_EARTH.moss, // Deep forest
    border: LIVING_EARTH.sage, // Nature green
    text: LIVING_EARTH.lantern, // Warm white
  },
  warning: {
    bg: LIVING_EARTH.wood, // Elevated surface
    border: LIVING_EARTH.copper, // Urgent copper
    text: LIVING_EARTH.lantern, // Warm white
  },
  learning: {
    bg: LIVING_EARTH.bark, // Warm surface
    border: LIVING_EARTH.honey, // Soft honey glow
    text: LIVING_EARTH.lantern, // Warm white
  },
};

/** Origin to transform-origin mapping */
const ORIGIN_TRANSFORM: Record<ToastOrigin, string> = {
  top: 'top center',
  bottom: 'bottom center',
  left: 'center left',
  right: 'center right',
};

// =============================================================================
// Component
// =============================================================================

/**
 * OrganicToast
 *
 * Toast notification with organic growth animation and Living Earth colors.
 *
 * @example Info toast:
 * ```tsx
 * <OrganicToast type="info" onDismiss={handleDismiss}>
 *   Citizen joined the town!
 * </OrganicToast>
 * ```
 *
 * @example Success toast (no auto-dismiss):
 * ```tsx
 * <OrganicToast type="success" duration={0} origin="bottom">
 *   Coalition successfully formed.
 * </OrganicToast>
 * ```
 *
 * @example Learning callout:
 * ```tsx
 * <OrganicToast type="learning" origin="right" duration={8000}>
 *   💡 Tip: Use staggered breathing for visual rhythm in lists.
 * </OrganicToast>
 * ```
 */
export function OrganicToast({
  type,
  origin = 'top',
  duration = 5000,
  onDismiss,
  className = '',
  children,
}: OrganicToastProps) {
  // Get growing animation state
  const { style: growingStyle, trigger } = useGrowing({
    duration: 300,
    onComplete: () => {
      // Start auto-dismiss timer after growth completes
      if (duration > 0 && onDismiss) {
        setTimeout(onDismiss, duration);
      }
    },
  });

  // Trigger growth on mount
  useEffect(() => {
    trigger();
  }, [trigger]);

  // Get colors for type
  const colors = TYPE_COLORS[type];

  // Merge styles
  const mergedStyle: React.CSSProperties = {
    ...growingStyle,
    backgroundColor: colors.bg,
    borderColor: colors.border,
    color: colors.text,
    transformOrigin: ORIGIN_TRANSFORM[origin],
  };

  return (
    <div
      className={`
        rounded-lg border-2 px-4 py-3 shadow-lg
        ${className}
      `}
      style={mergedStyle}
    >
      {children}
    </div>
  );
}

// =============================================================================
// Display Name
// =============================================================================

OrganicToast.displayName = 'OrganicToast';

// =============================================================================
// Default Export
// =============================================================================

export default OrganicToast;
