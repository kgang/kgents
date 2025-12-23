/**
 * useTitleScatter — Hidden Delight: Letters Scatter and Reform
 *
 * When the user double-clicks the title, letters briefly scatter
 * and then magnetically reform. A hidden toy for those who explore.
 *
 * "Joy-inducing > merely functional."
 */

import { useCallback, useState, useRef, useEffect, useMemo } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface LetterState {
  char: string;
  index: number;
  offsetX: number;
  offsetY: number;
  rotation: number;
  scale: number;
  opacity: number;
}

export interface TitleScatterOptions {
  /** The title text to scatter */
  text: string;
  /** Duration of scatter animation (ms) */
  scatterDuration?: number;
  /** Duration of reform animation (ms) */
  reformDuration?: number;
  /** Maximum scatter distance (px) */
  maxScatter?: number;
  /** Disable the effect */
  disabled?: boolean;
}

export interface TitleScatterState {
  /** Current state of each letter */
  letters: LetterState[];
  /** Whether scatter animation is active */
  isScattered: boolean;
  /** Whether reform animation is active */
  isReforming: boolean;
  /** Trigger the scatter effect */
  scatter: () => void;
  /** Double-click handler */
  onDoubleClick: () => void;
  /** Get style for a specific letter */
  getLetterStyle: (letter: LetterState) => React.CSSProperties;
}

// =============================================================================
// Physics Constants
// =============================================================================

const SPRING_STIFFNESS = 0.08;
const SPRING_DAMPING = 0.85;
const VELOCITY_THRESHOLD = 0.1;

// =============================================================================
// Hook Implementation
// =============================================================================

/**
 * useTitleScatter — Letters scatter on double-click and magnetically reform
 *
 * @example
 * function Title() {
 *   const { letters, onDoubleClick, getLetterStyle } = useTitleScatter({
 *     text: 'THE MEMBRANE'
 *   });
 *
 *   return (
 *     <h1 onDoubleClick={onDoubleClick}>
 *       {letters.map((letter, i) => (
 *         <span key={i} style={getLetterStyle(letter)}>
 *           {letter.char}
 *         </span>
 *       ))}
 *     </h1>
 *   );
 * }
 */
export function useTitleScatter(options: TitleScatterOptions): TitleScatterState {
  const {
    text,
    scatterDuration = 300,
    // reformDuration controls spring settle time (handled by physics)
    reformDuration: _reformDuration = 800,
    maxScatter = 50,
    disabled = false,
  } = options;

  // Initialize letters
  const initialLetters = useMemo(
    () =>
      text.split('').map((char, index) => ({
        char,
        index,
        offsetX: 0,
        offsetY: 0,
        rotation: 0,
        scale: 1,
        opacity: 1,
      })),
    [text]
  );

  const [letters, setLetters] = useState<LetterState[]>(initialLetters);
  const [isScattered, setIsScattered] = useState(false);
  const [isReforming, setIsReforming] = useState(false);

  // Animation refs
  const animationRef = useRef<number | null>(null);
  const targetRef = useRef<LetterState[]>(initialLetters);
  const velocityRef = useRef<{ x: number; y: number; r: number }[]>(
    initialLetters.map(() => ({ x: 0, y: 0, r: 0 }))
  );

  // Check reduced motion
  const prefersReducedMotion = useMemo(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  // Reset letters when text changes
  useEffect(() => {
    setLetters(initialLetters);
    targetRef.current = initialLetters;
    velocityRef.current = initialLetters.map(() => ({ x: 0, y: 0, r: 0 }));
  }, [initialLetters]);

  // Animation loop
  const animate = useCallback(() => {
    setLetters((prevLetters) => {
      let allSettled = true;

      const newLetters = prevLetters.map((letter, i) => {
        const target = targetRef.current[i];
        const vel = velocityRef.current[i];

        // Spring force toward target
        const forceX = (target.offsetX - letter.offsetX) * SPRING_STIFFNESS;
        const forceY = (target.offsetY - letter.offsetY) * SPRING_STIFFNESS;
        const forceR = (target.rotation - letter.rotation) * SPRING_STIFFNESS;

        // Update velocity with damping
        vel.x = (vel.x + forceX) * SPRING_DAMPING;
        vel.y = (vel.y + forceY) * SPRING_DAMPING;
        vel.r = (vel.r + forceR) * SPRING_DAMPING;

        // Update position
        const newOffsetX = letter.offsetX + vel.x;
        const newOffsetY = letter.offsetY + vel.y;
        const newRotation = letter.rotation + vel.r;

        // Check if still moving
        const totalVel = Math.abs(vel.x) + Math.abs(vel.y) + Math.abs(vel.r);
        const distToTarget =
          Math.abs(target.offsetX - newOffsetX) +
          Math.abs(target.offsetY - newOffsetY) +
          Math.abs(target.rotation - newRotation);

        if (totalVel > VELOCITY_THRESHOLD || distToTarget > 0.5) {
          allSettled = false;
        }

        return {
          ...letter,
          offsetX: newOffsetX,
          offsetY: newOffsetY,
          rotation: newRotation,
          scale: 1 + Math.abs(vel.x + vel.y) * 0.01, // Slight scale on movement
          opacity: 1,
        };
      });

      if (allSettled) {
        // Snap to targets and stop
        animationRef.current = null;
        setIsReforming(false);
        return targetRef.current.map((t) => ({ ...t, scale: 1, opacity: 1 }));
      }

      return newLetters;
    });

    if (animationRef.current !== null) {
      animationRef.current = requestAnimationFrame(animate);
    }
  }, []);

  // Start animation
  const startAnimation = useCallback(() => {
    if (animationRef.current === null) {
      animationRef.current = requestAnimationFrame(animate);
    }
  }, [animate]);

  // Scatter effect
  const scatter = useCallback(() => {
    if (disabled || prefersReducedMotion) return;

    setIsScattered(true);

    // Set random scatter targets
    const scatteredTargets = initialLetters.map((letter) => ({
      ...letter,
      offsetX: (Math.random() - 0.5) * maxScatter * 2,
      offsetY: (Math.random() - 0.5) * maxScatter * 2,
      rotation: (Math.random() - 0.5) * 45,
      scale: 0.8 + Math.random() * 0.4,
      opacity: 0.7 + Math.random() * 0.3,
    }));

    targetRef.current = scatteredTargets;
    startAnimation();

    // After scatter duration, reform
    setTimeout(() => {
      setIsScattered(false);
      setIsReforming(true);

      // Set targets back to original positions
      targetRef.current = initialLetters;
      startAnimation();
    }, scatterDuration);
  }, [disabled, prefersReducedMotion, initialLetters, maxScatter, scatterDuration, startAnimation]);

  // Get style for a letter
  const getLetterStyle = useCallback(
    (letter: LetterState): React.CSSProperties => {
      if (disabled || prefersReducedMotion) {
        return { display: 'inline-block' };
      }

      return {
        display: 'inline-block',
        transform: `translate(${letter.offsetX}px, ${letter.offsetY}px) rotate(${letter.rotation}deg) scale(${letter.scale})`,
        opacity: letter.opacity,
        transition: isScattered || isReforming ? 'none' : 'transform 0.3s ease-out',
        willChange: isScattered || isReforming ? 'transform, opacity' : 'auto',
      };
    },
    [disabled, prefersReducedMotion, isScattered, isReforming]
  );

  return {
    letters,
    isScattered,
    isReforming,
    scatter,
    onDoubleClick: scatter,
    getLetterStyle,
  };
}

export default useTitleScatter;
