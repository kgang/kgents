/**
 * useFlowing - Particle stream animation hook
 *
 * Implements "Flowing" from Crown Jewels Genesis Moodboard.
 * Data flows like water through vines - particles travel along bezier paths.
 *
 * @see plans/crown-jewels-genesis.md - Phase 1: Foundation
 * @see constants/town.ts - FLOWING_ANIMATION constants
 */

import { useState, useCallback, useRef, useMemo, useEffect } from 'react';
import { FLOWING_ANIMATION } from '@/constants';

// =============================================================================
// Types
// =============================================================================

export interface Point {
  x: number;
  y: number;
}

export interface FlowParticle {
  /** Unique particle ID */
  id: string;

  /** Position along path (0-1) */
  position: number;

  /** Current X coordinate */
  x: number;

  /** Current Y coordinate */
  y: number;

  /** Particle opacity (fades at ends) */
  opacity: number;

  /** Particle size multiplier */
  size: number;
}

export interface FlowingOptions {
  /**
   * Enable/disable flowing animation.
   */
  enabled?: boolean;

  /**
   * Duration of one flow cycle in ms (default: 2000)
   */
  duration?: number;

  /**
   * Number of particles (default: 4)
   */
  particleCount?: number;

  /**
   * Base particle size (default: 4)
   */
  particleSize?: number;

  /**
   * Flow direction: 'forward' or 'reverse'
   */
  direction?: 'forward' | 'reverse';

  /**
   * Whether particles should loop continuously
   */
  loop?: boolean;

  /**
   * Respect prefers-reduced-motion media query.
   * Default: true
   */
  respectReducedMotion?: boolean;

  /**
   * Callback when a particle completes its journey
   */
  onParticleComplete?: (particleId: string) => void;
}

export interface FlowingState {
  /** Array of current particle states */
  particles: FlowParticle[];

  /** Whether animation is currently running */
  isFlowing: boolean;

  /** Start the flow */
  start: () => void;

  /** Stop the flow */
  stop: () => void;

  /** Pause the flow (particles freeze in place) */
  pause: () => void;

  /** Resume the flow */
  resume: () => void;

  /** Get interpolated point on path at position (0-1) */
  getPointAtPosition: (position: number) => Point;

  /** SVG path string for the flow path */
  pathD: string;
}

// =============================================================================
// Bezier Math Utilities
// =============================================================================

/**
 * Linear interpolation between two points
 */
function lerp(p0: Point, p1: Point, t: number): Point {
  return {
    x: p0.x + (p1.x - p0.x) * t,
    y: p0.y + (p1.y - p0.y) * t,
  };
}

// =============================================================================
// Hook Implementation
// =============================================================================

/**
 * useFlowing
 *
 * Returns particle animation state for flowing effects along paths.
 *
 * @param pathPoints Array of points defining the flow path
 * @param options Configuration options
 *
 * @example
 * ```tsx
 * function FlowingEdge({ from, to }) {
 *   const midpoint = {
 *     x: (from.x + to.x) / 2,
 *     y: (from.y + to.y) / 2 - 20 // Curve upward
 *   };
 *
 *   const { particles, pathD, start } = useFlowing(
 *     [from, midpoint, to],
 *     { particleCount: 3 }
 *   );
 *
 *   useEffect(() => { start(); }, []);
 *
 *   return (
 *     <svg>
 *       <path d={pathD} stroke="rgba(212, 165, 116, 0.3)" fill="none" />
 *       {particles.map(p => (
 *         <circle
 *           key={p.id}
 *           cx={p.x}
 *           cy={p.y}
 *           r={p.size * 2}
 *           fill={`rgba(212, 165, 116, ${p.opacity})`}
 *         />
 *       ))}
 *     </svg>
 *   );
 * }
 * ```
 */
export function useFlowing(pathPoints: Point[], options: FlowingOptions = {}): FlowingState {
  const {
    enabled = true,
    duration = FLOWING_ANIMATION.duration,
    particleCount = 4,
    particleSize = 4,
    direction = 'forward',
    loop = true,
    respectReducedMotion = true,
    onParticleComplete,
  } = options;

  // State
  const [particles, setParticles] = useState<FlowParticle[]>([]);
  const [isFlowing, setIsFlowing] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  // Refs
  const animationRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(0);
  const pauseTimeRef = useRef<number>(0);
  const onCompleteRef = useRef(onParticleComplete);

  // Keep callback ref updated
  useEffect(() => {
    onCompleteRef.current = onParticleComplete;
  }, [onParticleComplete]);

  // Check for reduced motion preference
  const prefersReducedMotion = useMemo(() => {
    if (!respectReducedMotion) return false;
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, [respectReducedMotion]);

  // Generate SVG path from points
  const pathD = useMemo(() => {
    if (pathPoints.length < 2) return '';

    if (pathPoints.length === 2) {
      // Simple line
      return `M ${pathPoints[0].x} ${pathPoints[0].y} L ${pathPoints[1].x} ${pathPoints[1].y}`;
    }

    // Smooth curve through all points using quadratic bezier
    let d = `M ${pathPoints[0].x} ${pathPoints[0].y}`;

    for (let i = 0; i < pathPoints.length - 1; i++) {
      const p0 = pathPoints[i];
      const p1 = pathPoints[i + 1];

      if (i === 0) {
        // First segment: quadratic to first midpoint
        const mid = lerp(p0, p1, 0.5);
        d += ` Q ${p0.x} ${p0.y} ${mid.x} ${mid.y}`;
      } else if (i === pathPoints.length - 2) {
        // Last segment: quadratic to end
        d += ` Q ${p0.x} ${p0.y} ${p1.x} ${p1.y}`;
      } else {
        // Middle segments: smooth curve through point
        const mid = lerp(p0, p1, 0.5);
        d += ` Q ${p0.x} ${p0.y} ${mid.x} ${mid.y}`;
      }
    }

    return d;
  }, [pathPoints]);

  // Get point on path at position (0-1)
  const getPointAtPosition = useCallback(
    (position: number): Point => {
      if (pathPoints.length < 2) return { x: 0, y: 0 };
      if (pathPoints.length === 2) {
        return lerp(pathPoints[0], pathPoints[1], position);
      }

      // Find which segment we're on
      const totalSegments = pathPoints.length - 1;
      const segmentIndex = Math.min(
        Math.floor(position * totalSegments),
        totalSegments - 1
      );
      const segmentPosition = (position * totalSegments) % 1;

      const p0 = pathPoints[segmentIndex];
      const p1 = pathPoints[segmentIndex + 1];

      // Simple linear interpolation per segment
      // (For smoother paths, could use actual bezier math)
      return lerp(p0, p1, segmentPosition);
    },
    [pathPoints]
  );

  // Calculate particle opacity (fades at ends)
  const getParticleOpacity = useCallback((position: number): number => {
    // Fade in at start, fade out at end
    const fadeRange = 0.15;
    if (position < fadeRange) {
      return position / fadeRange;
    }
    if (position > 1 - fadeRange) {
      return (1 - position) / fadeRange;
    }
    return 1;
  }, []);

  // Initialize particles with staggered positions
  const initializeParticles = useCallback(() => {
    const newParticles: FlowParticle[] = [];
    const spacing = 1 / particleCount;

    for (let i = 0; i < particleCount; i++) {
      const pos = direction === 'forward' ? i * spacing : 1 - i * spacing;
      const point = getPointAtPosition(pos);

      newParticles.push({
        id: `particle-${i}`,
        position: pos,
        x: point.x,
        y: point.y,
        opacity: getParticleOpacity(pos),
        size: particleSize * (0.8 + Math.random() * 0.4), // Slight size variation
      });
    }

    setParticles(newParticles);
  }, [particleCount, particleSize, direction, getPointAtPosition, getParticleOpacity]);

  // Animation loop
  const animate = useCallback(
    (timestamp: number) => {
      if (startTimeRef.current === 0) {
        startTimeRef.current = timestamp;
      }

      const elapsed = timestamp - startTimeRef.current;
      const cycleProgress = (elapsed / duration) % 1;

      setParticles((prevParticles) => {
        return prevParticles.map((particle, i) => {
          const spacing = 1 / particleCount;
          const baseOffset = i * spacing;

          // Calculate position with wrap-around
          let newPosition: number;
          if (direction === 'forward') {
            newPosition = (baseOffset + cycleProgress) % 1;
          } else {
            newPosition = (1 - baseOffset - cycleProgress + 1) % 1;
          }

          const point = getPointAtPosition(newPosition);

          // Check for completion (crossed the finish line)
          if (
            loop === false &&
            ((direction === 'forward' && newPosition < particle.position && particle.position > 0.9) ||
              (direction === 'reverse' && newPosition > particle.position && particle.position < 0.1))
          ) {
            onCompleteRef.current?.(particle.id);
          }

          return {
            ...particle,
            position: newPosition,
            x: point.x,
            y: point.y,
            opacity: getParticleOpacity(newPosition),
          };
        });
      });

      if (loop || elapsed < duration * 1.5) {
        animationRef.current = requestAnimationFrame(animate);
      } else {
        setIsFlowing(false);
      }
    },
    [duration, particleCount, direction, loop, getPointAtPosition, getParticleOpacity]
  );

  // Start flow
  const start = useCallback(() => {
    if (!enabled || prefersReducedMotion) return;

    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }

    initializeParticles();
    startTimeRef.current = 0;
    setIsFlowing(true);
    setIsPaused(false);
    animationRef.current = requestAnimationFrame(animate);
  }, [enabled, prefersReducedMotion, initializeParticles, animate]);

  // Stop flow
  const stop = useCallback(() => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }
    setIsFlowing(false);
    setIsPaused(false);
    setParticles([]);
  }, []);

  // Pause flow
  const pause = useCallback(() => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
      pauseTimeRef.current = performance.now();
    }
    setIsPaused(true);
  }, []);

  // Resume flow
  const resume = useCallback(() => {
    if (!isPaused) return;

    // Adjust start time to account for pause
    const pauseDuration = performance.now() - pauseTimeRef.current;
    startTimeRef.current += pauseDuration;

    setIsPaused(false);
    animationRef.current = requestAnimationFrame(animate);
  }, [isPaused, animate]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  // Restart animation when path changes
  useEffect(() => {
    if (isFlowing && !isPaused) {
      initializeParticles();
    }
  }, [pathPoints, isFlowing, isPaused, initializeParticles]);

  return {
    particles,
    isFlowing,
    start,
    stop,
    pause,
    resume,
    getPointAtPosition,
    pathD,
  };
}

// =============================================================================
// Utility: Create curved path between two points
// =============================================================================

/**
 * Generate a curved path between two points with optional bend.
 *
 * @param from Start point
 * @param to End point
 * @param curvature How much the path curves (0 = straight, positive = curve up/left)
 * @returns Array of points for use with useFlowing
 */
export function createCurvedPath(from: Point, to: Point, curvature: number = 0.3): Point[] {
  const midX = (from.x + to.x) / 2;
  const midY = (from.y + to.y) / 2;

  // Perpendicular offset
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const len = Math.sqrt(dx * dx + dy * dy);

  // Perpendicular unit vector
  const perpX = -dy / len;
  const perpY = dx / len;

  // Control point offset
  const offsetAmount = len * curvature;

  return [
    from,
    {
      x: midX + perpX * offsetAmount,
      y: midY + perpY * offsetAmount,
    },
    to,
  ];
}

/**
 * Generate a smooth S-curve path between two points.
 */
export function createSCurvePath(from: Point, to: Point, amplitude: number = 30): Point[] {
  const dx = to.x - from.x;
  const dy = to.y - from.y;

  return [
    from,
    {
      x: from.x + dx * 0.25,
      y: from.y + dy * 0.25 - amplitude,
    },
    {
      x: from.x + dx * 0.5,
      y: from.y + dy * 0.5,
    },
    {
      x: from.x + dx * 0.75,
      y: from.y + dy * 0.75 + amplitude,
    },
    to,
  ];
}

// =============================================================================
// Default export
// =============================================================================

export default useFlowing;
