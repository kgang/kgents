/**
 * BreathingContainer
 *
 * Wraps any element with subtle breathing animation for idle states.
 * Implements "Everything Breathes" from Crown Jewels Genesis Moodboard.
 *
 * @see plans/crown-jewels-genesis.md - Phase 1: Foundation
 * @see hooks/useBreathing.ts
 */

import React from 'react';
import { useBreathing, type BreathingOptions } from '@/hooks/useBreathing';
import { BREATHING_ANIMATION } from '@/constants';

// =============================================================================
// Types
// =============================================================================

/**
 * Breathing intensity levels.
 * Maps to amplitude multipliers.
 */
export type BreathingIntensity = 'subtle' | 'normal' | 'emphatic';

/**
 * Breathing period presets for urgency states.
 * Maps to period values in ms.
 */
export type BreathingPeriod = 'calm' | 'normal' | 'elevated' | 'urgent' | 'critical';

export interface BreathingContainerProps {
  /**
   * Breathing intensity.
   * - subtle: 1.5% amplitude (barely perceptible, resting state)
   * - normal: 3% amplitude (default, idle state)
   * - emphatic: 5% amplitude (demands attention)
   *
   * Default: 'normal'
   */
  intensity?: BreathingIntensity;

  /**
   * Override breathing period for urgency states.
   * - calm: 5000ms (slow, meditative)
   * - normal: 3500ms (default)
   * - elevated: 2500ms (slightly anxious)
   * - urgent: 1500ms (demanding attention)
   * - critical: 800ms (flashing urgency)
   *
   * Default: 'normal'
   */
  period?: BreathingPeriod;

  /**
   * Disable animation entirely (for static screenshots, etc.)
   * Default: false
   */
  static?: boolean;

  /**
   * Phase offset for staggered animation (0-1).
   * Allows multiple elements to breathe out of sync.
   * Default: 0
   */
  phaseOffset?: number;

  /**
   * Additional className for the container.
   */
  className?: string;

  /**
   * Additional inline styles for the container.
   */
  style?: React.CSSProperties;

  /**
   * Content to wrap with breathing animation.
   */
  children: React.ReactNode;
}

// =============================================================================
// Configuration
// =============================================================================

/** Intensity to amplitude mapping */
const INTENSITY_AMPLITUDE: Record<BreathingIntensity, number> = {
  subtle: 0.015, // 1.5%
  normal: BREATHING_ANIMATION.amplitude, // 3%
  emphatic: 0.05, // 5%
};

/** Period preset mapping */
const PERIOD_MS: Record<BreathingPeriod, number> = {
  calm: 5000,
  normal: BREATHING_ANIMATION.period, // 3500
  elevated: 2500,
  urgent: 1500,
  critical: 800,
};

// =============================================================================
// Component
// =============================================================================

/**
 * BreathingContainer
 *
 * Wraps children with Ghibli-inspired breathing animation.
 *
 * @example Basic usage (idle state):
 * ```tsx
 * <BreathingContainer>
 *   <CitizenCard citizen={sage} />
 * </BreathingContainer>
 * ```
 *
 * @example Urgent breathing for consent debt:
 * ```tsx
 * <BreathingContainer period="urgent" intensity="emphatic">
 *   <ConsentDebtMeter debt={0.85} />
 * </BreathingContainer>
 * ```
 *
 * @example Staggered breathing in list:
 * ```tsx
 * citizens.map((citizen, i) => (
 *   <BreathingContainer key={citizen.id} phaseOffset={i * 0.1}>
 *     <CitizenNode citizen={citizen} />
 *   </BreathingContainer>
 * ))
 * ```
 */
export function BreathingContainer({
  intensity = 'normal',
  period = 'normal',
  static: isStatic = false,
  phaseOffset = 0,
  className,
  style: customStyle,
  children,
}: BreathingContainerProps) {
  // Get breathing animation state
  const breathingOptions: BreathingOptions = {
    enabled: !isStatic,
    amplitude: INTENSITY_AMPLITUDE[intensity],
    period: PERIOD_MS[period],
    phaseOffset,
  };

  const { style: breathingStyle } = useBreathing(breathingOptions);

  // Merge custom styles with breathing styles
  const mergedStyle: React.CSSProperties = {
    ...breathingStyle,
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

BreathingContainer.displayName = 'BreathingContainer';

// =============================================================================
// Default Export
// =============================================================================

export default BreathingContainer;
