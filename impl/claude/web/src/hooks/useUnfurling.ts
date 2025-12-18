/**
 * useUnfurling - Leaf-like panel expansion animation hook
 *
 * Implements "Unfurling" from Crown Jewels Genesis Moodboard.
 * Panels unfurl like leaves, not slide mechanically.
 *
 * @see plans/crown-jewels-genesis.md - Phase 1: Foundation
 * @see constants/town.ts - UNFURLING_ANIMATION constants
 */

import { useState, useCallback, useRef, useMemo, useEffect } from 'react';
import { UNFURLING_ANIMATION } from '@/constants';

// =============================================================================
// Types
// =============================================================================

export type UnfurlDirection = 'down' | 'up' | 'left' | 'right' | 'radial';

export interface UnfurlingOptions {
  /**
   * Enable/disable unfurling animation.
   */
  enabled?: boolean;

  /**
   * Duration of unfurl transition in ms (default: 300)
   */
  duration?: number;

  /**
   * Direction of unfurl (default: 'down')
   */
  direction?: UnfurlDirection;

  /**
   * Custom easing function
   */
  easing?: string;

  /**
   * Initial state: true = unfurled, false = folded
   */
  initialOpen?: boolean;

  /**
   * Delay content fade until unfurl is partially complete (0-1)
   * Default: 0.3 (content fades in at 30% unfurl progress)
   */
  contentFadeDelay?: number;

  /**
   * Respect prefers-reduced-motion media query.
   * Default: true
   */
  respectReducedMotion?: boolean;

  /**
   * Callback when unfurl completes
   */
  onUnfurled?: () => void;

  /**
   * Callback when fold completes
   */
  onFolded?: () => void;
}

export interface UnfurlingState {
  /** Current unfurl progress (0 = folded, 1 = unfurled) */
  progress: number;

  /** Whether panel is currently animating */
  isAnimating: boolean;

  /** Current state: unfurled or folded */
  isOpen: boolean;

  /** Trigger unfurl (open) */
  unfurl: () => void;

  /** Trigger fold (close) */
  fold: () => void;

  /** Toggle between unfurl and fold */
  toggle: () => void;

  /** CSS style object for the container */
  style: React.CSSProperties;

  /** CSS style object for inner content (handles fade-in delay) */
  contentStyle: React.CSSProperties;

  /** Clip path string for non-rectangular unfurls */
  clipPath: string;
}

// =============================================================================
// Direction Configuration
// =============================================================================

type DirectionConfig = {
  clipFolded: string;
  clipUnfurled: string;
  transformOrigin: string;
};

const DIRECTION_CONFIG: Record<UnfurlDirection, DirectionConfig> = {
  down: {
    clipFolded: 'inset(0 0 100% 0)',
    clipUnfurled: 'inset(0 0 0 0)',
    transformOrigin: 'top center',
  },
  up: {
    clipFolded: 'inset(100% 0 0 0)',
    clipUnfurled: 'inset(0 0 0 0)',
    transformOrigin: 'bottom center',
  },
  left: {
    clipFolded: 'inset(0 100% 0 0)',
    clipUnfurled: 'inset(0 0 0 0)',
    transformOrigin: 'center right',
  },
  right: {
    clipFolded: 'inset(0 0 0 100%)',
    clipUnfurled: 'inset(0 0 0 0)',
    transformOrigin: 'center left',
  },
  radial: {
    clipFolded: 'circle(0% at 50% 50%)',
    clipUnfurled: 'circle(100% at 50% 50%)',
    transformOrigin: 'center center',
  },
};

// =============================================================================
// Hook Implementation
// =============================================================================

/**
 * useUnfurling
 *
 * Returns animation state for leaf-like panel expansion.
 *
 * @example
 * ```tsx
 * function CollapsiblePanel({ isOpen, children }) {
 *   const { style, contentStyle, toggle } = useUnfurling({
 *     initialOpen: isOpen,
 *   });
 *
 *   return (
 *     <div className="panel" style={style}>
 *       <div style={contentStyle}>{children}</div>
 *     </div>
 *   );
 * }
 * ```
 *
 * @example With radial unfurl:
 * ```tsx
 * function Modal({ isVisible, children }) {
 *   const { style, contentStyle, unfurl, fold } = useUnfurling({
 *     direction: 'radial',
 *     duration: 400,
 *   });
 *
 *   useEffect(() => {
 *     if (isVisible) unfurl();
 *     else fold();
 *   }, [isVisible]);
 *
 *   return <div style={style}>{children}</div>;
 * }
 * ```
 */
export function useUnfurling(options: UnfurlingOptions = {}): UnfurlingState {
  const {
    enabled = true,
    duration = UNFURLING_ANIMATION.duration,
    direction = 'down',
    easing = UNFURLING_ANIMATION.easing,
    initialOpen = false,
    contentFadeDelay = 0.3,
    respectReducedMotion = true,
    onUnfurled,
    onFolded,
  } = options;

  // State
  const [progress, setProgress] = useState(initialOpen ? 1 : 0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [isOpen, setIsOpen] = useState(initialOpen);
  const [targetOpen, setTargetOpen] = useState(initialOpen);

  // Refs
  const animationRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(0);
  const startProgressRef = useRef<number>(initialOpen ? 1 : 0);
  const onUnfurledRef = useRef(onUnfurled);
  const onFoldedRef = useRef(onFolded);

  // Keep callback refs updated
  useEffect(() => {
    onUnfurledRef.current = onUnfurled;
    onFoldedRef.current = onFolded;
  }, [onUnfurled, onFolded]);

  // Check for reduced motion preference
  const prefersReducedMotion = useMemo(() => {
    if (!respectReducedMotion) return false;
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, [respectReducedMotion]);

  // Direction config
  const dirConfig = DIRECTION_CONFIG[direction];

  // Animation loop
  const animate = useCallback(
    (timestamp: number) => {
      if (startTimeRef.current === 0) {
        startTimeRef.current = timestamp;
      }

      const elapsed = timestamp - startTimeRef.current;
      const rawProgress = Math.min(1, elapsed / duration);

      // Calculate current progress based on direction and target
      const startP = startProgressRef.current;
      const endP = targetOpen ? 1 : 0;
      const currentProgress = startP + (endP - startP) * rawProgress;

      setProgress(currentProgress);

      if (rawProgress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      } else {
        // Animation complete
        setIsAnimating(false);
        setIsOpen(targetOpen);
        setProgress(targetOpen ? 1 : 0);

        if (targetOpen) {
          onUnfurledRef.current?.();
        } else {
          onFoldedRef.current?.();
        }
      }
    },
    [duration, targetOpen]
  );

  // Start animation when targetOpen changes
  useEffect(() => {
    if (!enabled) {
      setProgress(targetOpen ? 1 : 0);
      setIsOpen(targetOpen);
      return;
    }

    if (prefersReducedMotion) {
      setProgress(targetOpen ? 1 : 0);
      setIsOpen(targetOpen);
      if (targetOpen) onUnfurledRef.current?.();
      else onFoldedRef.current?.();
      return;
    }

    // Cancel existing animation
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }

    // Start new animation
    startProgressRef.current = progress;
    startTimeRef.current = 0;
    setIsAnimating(true);
    animationRef.current = requestAnimationFrame(animate);
  }, [targetOpen, enabled, prefersReducedMotion, animate, progress]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  // Actions
  const unfurl = useCallback(() => {
    setTargetOpen(true);
  }, []);

  const fold = useCallback(() => {
    setTargetOpen(false);
  }, []);

  const toggle = useCallback(() => {
    setTargetOpen((prev) => !prev);
  }, []);

  // Calculate clip path based on progress
  const clipPath = useMemo(() => {
    if (direction === 'radial') {
      const radius = progress * 100;
      return `circle(${radius}% at 50% 50%)`;
    }

    // For directional unfurls, interpolate inset values
    const inset = (1 - progress) * 100;
    switch (direction) {
      case 'down':
        return `inset(0 0 ${inset}% 0)`;
      case 'up':
        return `inset(${inset}% 0 0 0)`;
      case 'left':
        return `inset(0 ${inset}% 0 0)`;
      case 'right':
        return `inset(0 0 0 ${inset}%)`;
      default:
        return 'none';
    }
  }, [direction, progress]);

  // Container style
  const style: React.CSSProperties = useMemo(
    () => ({
      clipPath,
      WebkitClipPath: clipPath,
      transformOrigin: dirConfig.transformOrigin,
      willChange: isAnimating ? 'clip-path' : 'auto',
      // Ensure container is visible even when folded (for layout)
      visibility: progress === 0 && !isAnimating ? 'hidden' : 'visible',
    }),
    [clipPath, dirConfig.transformOrigin, isAnimating, progress]
  );

  // Content style (fades in after delay)
  const contentStyle: React.CSSProperties = useMemo(() => {
    // Content starts fading in after contentFadeDelay progress
    const contentProgress = Math.max(0, (progress - contentFadeDelay) / (1 - contentFadeDelay));
    const contentOpacity = Math.min(1, contentProgress);

    return {
      opacity: contentOpacity,
      transition: isAnimating ? 'none' : `opacity 0.15s ${easing}`,
    };
  }, [progress, contentFadeDelay, isAnimating, easing]);

  return {
    progress,
    isAnimating,
    isOpen,
    unfurl,
    fold,
    toggle,
    style,
    contentStyle,
    clipPath,
  };
}

// =============================================================================
// Utility: CSS-only unfurl classes
// =============================================================================

/**
 * Generate CSS keyframes for unfurl animation.
 */
export function getUnfurlingKeyframes(direction: UnfurlDirection = 'down'): string {
  const config = DIRECTION_CONFIG[direction];

  if (direction === 'radial') {
    return `
      @keyframes unfurl-radial {
        from { clip-path: circle(0% at 50% 50%); }
        to { clip-path: circle(100% at 50% 50%); }
      }
    `;
  }

  return `
    @keyframes unfurl-${direction} {
      from { clip-path: ${config.clipFolded}; }
      to { clip-path: ${config.clipUnfurled}; }
    }
  `;
}

/**
 * Get CSS animation property string for unfurl effect.
 */
export function getUnfurlingAnimation(
  duration: number = UNFURLING_ANIMATION.duration,
  direction: UnfurlDirection = 'down'
): string {
  return `unfurl-${direction} ${duration}ms ${UNFURLING_ANIMATION.easing} forwards`;
}

// =============================================================================
// Default export
// =============================================================================

export default useUnfurling;
