/**
 * BreathingContainer - Wrapper applying organic breathing to children
 *
 * Implements "Everything Breathes" from Crown Jewels Genesis Moodboard.
 * Unlike the simpler Breathe component, this uses the full useBreathing hook
 * with 4-phase breath cycle (rest → inhale → hold → exhale).
 *
 * @see plans/crown-jewels-genesis.md - Phase 1: Foundation
 * @see hooks/useBreathing.ts - Animation hook
 */

import { type ReactNode, type CSSProperties, useMemo } from 'react';
import { useBreathing, getStaggeredPhaseOffset, type BreathingOptions } from '@/hooks';
import { BREATHING_ANIMATION, LIVING_EARTH } from '@/constants';
import { useMotionPreferences } from './useMotionPreferences';

// =============================================================================
// Types
// =============================================================================

export interface BreathingContainerProps {
  /** Content to wrap with breathing animation */
  children: ReactNode;

  /**
   * Enable/disable breathing.
   * Default: true
   */
  enabled?: boolean;

  /**
   * Whether to pause breathing (e.g., on hover).
   * Default: false
   */
  paused?: boolean;

  /**
   * Breathing period in ms.
   * Default: 3500 (from BREATHING_ANIMATION.period)
   */
  period?: number;

  /**
   * Scale amplitude (0.03 = 3% variation).
   * Default: 0.03 (from BREATHING_ANIMATION.amplitude)
   */
  amplitude?: number;

  /**
   * Stagger index for offsetting breath cycles in lists.
   * Default: 0 (no offset)
   */
  staggerIndex?: number;

  /**
   * Whether to apply glow pulse with breathing.
   * Default: false
   */
  glowPulse?: boolean;

  /**
   * Glow color (only used if glowPulse is true).
   * Default: LIVING_EARTH.amber
   */
  glowColor?: string;

  /**
   * Callback when breath phase changes.
   */
  onPhaseChange?: (phase: 'rest' | 'inhale' | 'hold' | 'exhale') => void;

  /** Additional CSS class */
  className?: string;

  /** Additional inline styles */
  style?: CSSProperties;

  /** HTML element to render as */
  as?: keyof JSX.IntrinsicElements;
}

// =============================================================================
// Component
// =============================================================================

/**
 * BreathingContainer
 *
 * Wraps children with organic breathing animation.
 * Use for elements that should feel alive: cards, buttons, indicators.
 *
 * @example Basic usage:
 * ```tsx
 * <BreathingContainer>
 *   <Card>Content</Card>
 * </BreathingContainer>
 * ```
 *
 * @example With stagger for lists:
 * ```tsx
 * {items.map((item, i) => (
 *   <BreathingContainer key={item.id} staggerIndex={i}>
 *     <ItemCard item={item} />
 *   </BreathingContainer>
 * ))}
 * ```
 *
 * @example With glow pulse:
 * ```tsx
 * <BreathingContainer glowPulse glowColor="#D4A574">
 *   <ActiveIndicator />
 * </BreathingContainer>
 * ```
 */
export function BreathingContainer({
  children,
  enabled = true,
  paused = false,
  period = BREATHING_ANIMATION.period,
  amplitude = BREATHING_ANIMATION.amplitude,
  staggerIndex = 0,
  glowPulse = false,
  glowColor = LIVING_EARTH.amber,
  onPhaseChange,
  className = '',
  style,
  as: Component = 'div',
}: BreathingContainerProps) {
  const { shouldAnimate } = useMotionPreferences();

  // Calculate phase offset for staggering
  const phaseOffset = useMemo(
    () => getStaggeredPhaseOffset(staggerIndex),
    [staggerIndex]
  );

  // Use breathing hook
  const { scale, phase, isBreathing, pause, resume } = useBreathing({
    enabled: enabled && shouldAnimate,
    period,
    amplitude,
    phaseOffset,
    respectReducedMotion: true,
    onPhaseChange,
  });

  // Handle pause state
  useMemo(() => {
    if (paused && isBreathing) {
      pause();
    } else if (!paused && enabled && !isBreathing && shouldAnimate) {
      resume();
    }
  }, [paused, isBreathing, enabled, shouldAnimate, pause, resume]);

  // Calculate glow intensity based on scale
  const glowIntensity = useMemo(() => {
    if (!glowPulse) return 0;
    // Map scale (0.97-1.03) to glow intensity (0-1)
    const normalized = (scale - (1 - amplitude)) / (2 * amplitude);
    return Math.max(0, Math.min(1, normalized));
  }, [glowPulse, scale, amplitude]);

  // Build style object
  const containerStyle: CSSProperties = useMemo(() => {
    const baseStyle: CSSProperties = {
      transform: `scale(${scale.toFixed(4)})`,
      transformOrigin: 'center center',
      willChange: isBreathing ? 'transform' : 'auto',
      transition: isBreathing ? 'none' : `transform 0.2s ${BREATHING_ANIMATION.easing}`,
      ...style,
    };

    if (glowPulse) {
      baseStyle.boxShadow = `0 0 ${12 + glowIntensity * 8}px rgba(${hexToRgb(glowColor)}, ${0.2 + glowIntensity * 0.3})`;
    }

    return baseStyle;
  }, [scale, isBreathing, glowPulse, glowIntensity, glowColor, style]);

  // Render static if not animating
  if (!enabled || !shouldAnimate) {
    return (
      <Component className={className} style={style}>
        {children}
      </Component>
    );
  }

  return (
    <Component
      className={className}
      style={containerStyle}
      data-breathing={isBreathing}
      data-breath-phase={phase}
    >
      {children}
    </Component>
  );
}

// =============================================================================
// Utility
// =============================================================================

/**
 * Convert hex color to RGB values
 */
function hexToRgb(hex: string): string {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return '128, 128, 128';
  return `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}`;
}

// =============================================================================
// Specialized Variants
// =============================================================================

/**
 * BreathingCard - Card with subtle breathing
 */
export function BreathingCard({
  children,
  className = '',
  ...props
}: Omit<BreathingContainerProps, 'as'>) {
  return (
    <BreathingContainer
      className={`rounded-lg ${className}`}
      amplitude={0.02}
      {...props}
    >
      {children}
    </BreathingContainer>
  );
}

/**
 * BreathingButton - Button with more pronounced breathing
 */
export function BreathingButton({
  children,
  className = '',
  ...props
}: Omit<BreathingContainerProps, 'as'>) {
  return (
    <BreathingContainer
      as="button"
      className={className}
      amplitude={0.03}
      glowPulse
      {...props}
    >
      {children}
    </BreathingContainer>
  );
}

/**
 * BreathingIndicator - Status indicator with glow pulse
 */
export function BreathingIndicator({
  children,
  glowColor = LIVING_EARTH.mint,
  className = '',
  ...props
}: BreathingContainerProps) {
  return (
    <BreathingContainer
      className={`inline-flex ${className}`}
      amplitude={0.02}
      glowPulse
      glowColor={glowColor}
      period={2500} // Faster breathing for indicators
      {...props}
    >
      {children}
    </BreathingContainer>
  );
}

// =============================================================================
// Default Export
// =============================================================================

export default BreathingContainer;
