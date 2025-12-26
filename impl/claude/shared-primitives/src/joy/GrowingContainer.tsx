/**
 * GrowingContainer
 *
 * Elements emerge with seed -> sprout -> bloom -> full animation.
 * Implements "Growing" from Crown Jewels Genesis Moodboard.
 *
 * @see plans/crown-jewels-genesis.md - Phase 1: Foundation
 * @see hooks/useGrowing.ts
 */

import React, { useEffect } from 'react';
import { useGrowing, type GrowingOptions } from './useGrowing';

// =============================================================================
// Constants
// =============================================================================

const GROWING_ANIMATION = {
  duration: 400,
  easing: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
};

// =============================================================================
// Types
// =============================================================================

/**
 * Animation duration presets.
 */
export type GrowingDuration = 'quick' | 'normal' | 'deliberate';

export interface GrowingContainerProps {
  /**
   * Animation duration preset.
   * - quick: 250ms (responsive UI elements)
   * - normal: 400ms (default, balanced)
   * - deliberate: 600ms (emphasized entrance)
   *
   * Default: 'normal'
   */
  duration?: GrowingDuration;

  /**
   * Delay before growing starts (in ms).
   * Useful for staggered animations in lists.
   *
   * Default: 0
   */
  delay?: number;

  /**
   * Auto-trigger animation on mount.
   * When true, element grows automatically when component mounts.
   *
   * Default: false
   */
  autoTrigger?: boolean;

  /**
   * Start at full state immediately (skip animation).
   * Useful for already-visible elements.
   *
   * Default: false
   */
  startFull?: boolean;

  /**
   * Callback when growth animation completes.
   */
  onGrown?: () => void;

  /**
   * Additional className for the container.
   */
  className?: string;

  /**
   * Additional inline styles for the container.
   */
  style?: React.CSSProperties;

  /**
   * Content to wrap with growing animation.
   */
  children: React.ReactNode;
}

// =============================================================================
// Configuration
// =============================================================================

/** Duration preset mapping */
const DURATION_MS: Record<GrowingDuration, number> = {
  quick: 250,
  normal: GROWING_ANIMATION.duration, // 400
  deliberate: 600,
};

// =============================================================================
// Component
// =============================================================================

/**
 * GrowingContainer
 *
 * Wraps children with organic seed -> bloom growth animation.
 *
 * @example Auto-grow on mount:
 * ```tsx
 * <GrowingContainer autoTrigger>
 *   <TeachingCallout category="polynomial">
 *     Learn about state machines!
 *   </TeachingCallout>
 * </GrowingContainer>
 * ```
 *
 * @example Delayed staggered growth:
 * ```tsx
 * items.map((item, i) => (
 *   <GrowingContainer key={item.id} autoTrigger delay={i * 50}>
 *     <ItemCard item={item} />
 *   </GrowingContainer>
 * ))
 * ```
 *
 * @example Quick growth for responsive UI:
 * ```tsx
 * <GrowingContainer autoTrigger duration="quick">
 *   <Tooltip>Helpful hint</Tooltip>
 * </GrowingContainer>
 * ```
 */
export function GrowingContainer({
  duration = 'normal',
  delay = 0,
  autoTrigger = false,
  startFull = false,
  onGrown,
  className,
  style: customStyle,
  children,
}: GrowingContainerProps) {
  // Get growing animation state
  const growingOptions: GrowingOptions = {
    duration: DURATION_MS[duration],
    startFull,
    onComplete: onGrown,
  };

  const { style: growingStyle, trigger } = useGrowing(growingOptions);

  // Auto-trigger with optional delay
  useEffect(() => {
    if (!autoTrigger) return;

    if (delay > 0) {
      const timeout = setTimeout(trigger, delay);
      return () => clearTimeout(timeout);
    }
      trigger();

  }, [autoTrigger, delay, trigger]);

  // Merge custom styles with growing styles
  const mergedStyle: React.CSSProperties = {
    ...growingStyle,
    ...customStyle,
  };

  return (
    <div className={className} style={mergedStyle}>
      {children}
    </div>
  );
}

// =============================================================================
// Display Name
// =============================================================================

GrowingContainer.displayName = 'GrowingContainer';

// =============================================================================
// Default Export
// =============================================================================

export default GrowingContainer;
