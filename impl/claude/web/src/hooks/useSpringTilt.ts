/**
 * useSpringTilt — Spring Physics for Hover Interactions
 *
 * Provides a gentle tilt effect when hovering over elements.
 * Uses simplified spring physics for organic, playful motion.
 *
 * STARK BIOME: "Stillness, then life" — motion is earned through interaction.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

// =============================================================================
// Spring Physics Constants
// =============================================================================

/** Spring stiffness (higher = snappier) */
const STIFFNESS = 0.15;

/** Damping factor (higher = less bouncy) */
const DAMPING = 0.7;

/** Minimum velocity to continue animation */
const VELOCITY_THRESHOLD = 0.001;

/** Maximum tilt angle in degrees */
const MAX_TILT = 8;

// =============================================================================
// Types
// =============================================================================

export interface SpringTiltOptions {
  /** Maximum tilt angle in degrees (default: 8) */
  maxTilt?: number;
  /** Spring stiffness, 0-1 (default: 0.15) */
  stiffness?: number;
  /** Damping factor, 0-1 (default: 0.7) */
  damping?: number;
  /** Disable the effect */
  disabled?: boolean;
  /** Respect prefers-reduced-motion */
  respectReducedMotion?: boolean;
}

export interface SpringTiltState {
  /** Current rotation X (degrees) */
  rotateX: number;
  /** Current rotation Y (degrees) */
  rotateY: number;
  /** Whether currently animating */
  isAnimating: boolean;
  /** Style object to apply to element */
  style: React.CSSProperties;
  /** Props to spread on the element */
  handlers: {
    onMouseMove: (e: React.MouseEvent<HTMLElement>) => void;
    onMouseLeave: () => void;
    onMouseEnter: () => void;
  };
}

// =============================================================================
// Hook Implementation
// =============================================================================

/**
 * useSpringTilt — Add spring-physics tilt on hover
 *
 * @example
 * function HintCard({ children }) {
 *   const { style, handlers } = useSpringTilt({ maxTilt: 6 });
 *
 *   return (
 *     <div className="hint-card" style={style} {...handlers}>
 *       {children}
 *     </div>
 *   );
 * }
 */
export function useSpringTilt(options: SpringTiltOptions = {}): SpringTiltState {
  const {
    maxTilt = MAX_TILT,
    stiffness = STIFFNESS,
    damping = DAMPING,
    disabled = false,
    respectReducedMotion = true,
  } = options;

  // State
  const [rotateX, setRotateX] = useState(0);
  const [rotateY, setRotateY] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [isHovering, setIsHovering] = useState(false);

  // Refs for animation
  const targetRef = useRef({ x: 0, y: 0 });
  const velocityRef = useRef({ x: 0, y: 0 });
  const animationRef = useRef<number | null>(null);
  const elementRef = useRef<HTMLElement | null>(null);

  // Check reduced motion preference
  const prefersReducedMotion =
    typeof window !== 'undefined' && respectReducedMotion
      ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
      : false;

  // Animation loop using spring physics
  const animate = useCallback(() => {
    const targetX = targetRef.current.x;
    const targetY = targetRef.current.y;

    // Spring force
    const forceX = (targetX - rotateX) * stiffness;
    const forceY = (targetY - rotateY) * stiffness;

    // Update velocity with damping
    velocityRef.current.x = (velocityRef.current.x + forceX) * damping;
    velocityRef.current.y = (velocityRef.current.y + forceY) * damping;

    // Update position
    const newX = rotateX + velocityRef.current.x;
    const newY = rotateY + velocityRef.current.y;

    setRotateX(newX);
    setRotateY(newY);

    // Check if animation should continue
    const totalVelocity = Math.abs(velocityRef.current.x) + Math.abs(velocityRef.current.y);
    const distanceToTarget = Math.abs(targetX - newX) + Math.abs(targetY - newY);

    if (totalVelocity > VELOCITY_THRESHOLD || distanceToTarget > 0.1) {
      animationRef.current = requestAnimationFrame(animate);
    } else {
      // Snap to target and stop
      setRotateX(targetX);
      setRotateY(targetY);
      setIsAnimating(false);
    }
  }, [rotateX, rotateY, stiffness, damping]);

  // Start animation if not running
  useEffect(() => {
    if (disabled || prefersReducedMotion) return;

    if (isAnimating && !animationRef.current) {
      animationRef.current = requestAnimationFrame(animate);
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
    };
  }, [isAnimating, animate, disabled, prefersReducedMotion]);

  // Mouse move handler
  const onMouseMove = useCallback(
    (e: React.MouseEvent<HTMLElement>) => {
      if (disabled || prefersReducedMotion) return;

      const element = e.currentTarget;
      elementRef.current = element;

      const rect = element.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      // Calculate mouse position relative to center (-1 to 1)
      const relativeX = (e.clientX - centerX) / (rect.width / 2);
      const relativeY = (e.clientY - centerY) / (rect.height / 2);

      // Set target rotation (inverted for natural feel)
      targetRef.current = {
        x: -relativeY * maxTilt, // Tilt up when mouse is below center
        y: relativeX * maxTilt, // Tilt right when mouse is right of center
      };

      if (!isAnimating) {
        setIsAnimating(true);
      }
    },
    [disabled, prefersReducedMotion, maxTilt, isAnimating]
  );

  // Mouse leave handler
  const onMouseLeave = useCallback(() => {
    setIsHovering(false);
    targetRef.current = { x: 0, y: 0 };

    if (!isAnimating) {
      setIsAnimating(true);
    }
  }, [isAnimating]);

  // Mouse enter handler
  const onMouseEnter = useCallback(() => {
    setIsHovering(true);
  }, []);

  // Compute style
  const style: React.CSSProperties =
    disabled || prefersReducedMotion
      ? {}
      : {
          transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
          transformStyle: 'preserve-3d',
          transition: isHovering ? 'none' : 'transform 0.3s ease-out',
        };

  return {
    rotateX,
    rotateY,
    isAnimating,
    style,
    handlers: {
      onMouseMove,
      onMouseLeave,
      onMouseEnter,
    },
  };
}

// =============================================================================
// Utility: Keyboard Shortcut Pulse
// =============================================================================

/**
 * useKeyPulse — Pulse animation when a keyboard shortcut is pressed
 *
 * @example
 * function ShortcutHint({ shortcut }) {
 *   const { isPulsing, triggerPulse } = useKeyPulse(shortcut);
 *
 *   useEffect(() => {
 *     const handler = (e) => {
 *       if (e.key === shortcut) triggerPulse();
 *     };
 *     window.addEventListener('keydown', handler);
 *     return () => window.removeEventListener('keydown', handler);
 *   }, [shortcut, triggerPulse]);
 *
 *   return <kbd className={isPulsing ? 'pulse' : ''}>{shortcut}</kbd>;
 * }
 */
export function useKeyPulse(targetKey?: string) {
  const [isPulsing, setIsPulsing] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const triggerPulse = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    setIsPulsing(true);
    timeoutRef.current = setTimeout(() => {
      setIsPulsing(false);
    }, 300);
  }, []);

  // Auto-listen for key if targetKey provided
  useEffect(() => {
    if (!targetKey) return;

    const handler = (e: KeyboardEvent) => {
      if (e.key.toLowerCase() === targetKey.toLowerCase()) {
        triggerPulse();
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [targetKey, triggerPulse]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return { isPulsing, triggerPulse };
}

export default useSpringTilt;
