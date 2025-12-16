/**
 * Shimmer Animation Component
 *
 * Loading/processing indicator - a subtle shine effect.
 * Use for loading states, skeleton screens, processing indicators.
 *
 * Foundation 5: Personality & Joy - Animation Primitives
 *
 * @example
 * ```tsx
 * <Shimmer active={isLoading}>
 *   <div className="h-4 bg-gray-700 rounded" />
 * </Shimmer>
 * ```
 */

import { motion } from 'framer-motion';
import type { ReactNode, CSSProperties } from 'react';
import { useMotionPreferences } from './useMotionPreferences';

export interface ShimmerProps {
  /** Content to animate */
  children: ReactNode;
  /** Whether shimmer is active. Default: true */
  active?: boolean;
  /** Animation duration in seconds. Default: 1.5 */
  duration?: number;
  /** Disable animation regardless of motion preferences */
  disabled?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Additional inline styles */
  style?: CSSProperties;
}

/**
 * Shimmer animation wrapper - sweeping shine effect.
 *
 * Perfect for:
 * - Skeleton loading states
 * - Processing indicators
 * - "Working..." states
 */
export function Shimmer({
  children,
  active = true,
  duration = 1.5,
  disabled = false,
  className = '',
  style,
}: ShimmerProps) {
  const { shouldAnimate } = useMotionPreferences();

  // Skip animation if not active, disabled, or user prefers reduced motion
  if (!active || disabled || !shouldAnimate) {
    return (
      <div className={className} style={style}>
        {children}
      </div>
    );
  }

  return (
    <div
      className={`relative overflow-hidden ${className}`}
      style={style}
    >
      {children}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.1) 50%, transparent 100%)',
        }}
        initial={{ x: '-100%' }}
        animate={{ x: '100%' }}
        transition={{
          duration,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
    </div>
  );
}

/**
 * ShimmerBlock - A pre-styled shimmer placeholder for skeleton screens.
 */
export interface ShimmerBlockProps {
  /** Width - can be tailwind class or CSS value */
  width?: string;
  /** Height - can be tailwind class or CSS value */
  height?: string;
  /** Border radius - tailwind class */
  rounded?: 'sm' | 'md' | 'lg' | 'full';
  /** Additional CSS classes */
  className?: string;
}

export function ShimmerBlock({
  width = 'w-full',
  height = 'h-4',
  rounded = 'md',
  className = '',
}: ShimmerBlockProps) {
  const roundedClass = {
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full',
  }[rounded];

  return (
    <Shimmer>
      <div
        className={`bg-gray-700/50 ${width} ${height} ${roundedClass} ${className}`}
      />
    </Shimmer>
  );
}

/**
 * ShimmerText - Shimmer placeholder for text content.
 */
export interface ShimmerTextProps {
  /** Number of lines to show */
  lines?: number;
  /** Width of last line (percentage) */
  lastLineWidth?: number;
  /** Gap between lines */
  gap?: 'sm' | 'md' | 'lg';
}

export function ShimmerText({
  lines = 3,
  lastLineWidth = 60,
  gap = 'sm',
}: ShimmerTextProps) {
  const gapClass = { sm: 'gap-1.5', md: 'gap-2', lg: 'gap-3' }[gap];

  return (
    <div className={`flex flex-col ${gapClass}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <ShimmerBlock
          key={i}
          width={i === lines - 1 ? `w-[${lastLineWidth}%]` : 'w-full'}
          height="h-3"
        />
      ))}
    </div>
  );
}

export default Shimmer;
