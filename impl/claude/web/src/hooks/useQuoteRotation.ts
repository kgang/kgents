/**
 * useQuoteRotation — Curated Quote Cycling with Micro-Shimmer
 *
 * Rotates through a curated set of quotes on click, with a brief
 * shimmer animation on reveal. Each quote is a crystallized insight.
 *
 * STARK BIOME: "Earned highlights" — quotes glow briefly when revealed.
 */

import { useCallback, useState, useRef, useEffect } from 'react';

// =============================================================================
// The Curated Quotes
// =============================================================================

/**
 * A curated set of quotes that capture the kgents philosophy.
 * Each quote is a compressed insight worth lingering on.
 */
export const CURATED_QUOTES = [
  'The proof IS the decision.',
  'Daring, bold, creative, opinionated but not gaudy.',
  'The persona is a garden, not a museum.',
  'Tasteful > feature-complete.',
  'Joy-inducing > merely functional.',
  'Agents compose. Monoliths accumulate.',
  'The noun is a lie. There is only the rate of change.',
  'Depth over breadth.',
  'Stillness, then life.',
  'The frame is humble. The content glows.',
] as const;

export type Quote = (typeof CURATED_QUOTES)[number];

// =============================================================================
// Types
// =============================================================================

export interface QuoteRotationOptions {
  /** Initial quote index (default: 0) */
  initialIndex?: number;
  /** Duration of shimmer animation in ms (default: 800) */
  shimmerDuration?: number;
  /** Disable interaction */
  disabled?: boolean;
}

export interface QuoteRotationState {
  /** Current quote text */
  quote: Quote;
  /** Current quote index */
  index: number;
  /** Whether shimmer is active */
  isShimmering: boolean;
  /** Advance to next quote */
  next: () => void;
  /** Go to previous quote */
  prev: () => void;
  /** Go to specific index */
  goTo: (index: number) => void;
  /** Click handler for the quote element */
  onClick: () => void;
  /** CSS class to apply for shimmer */
  shimmerClass: string;
  /** Style for shimmer effect */
  shimmerStyle: React.CSSProperties;
}

// =============================================================================
// Hook Implementation
// =============================================================================

/**
 * useQuoteRotation — Cycle through curated quotes with shimmer reveal
 *
 * @example
 * function QuoteBlock() {
 *   const { quote, onClick, shimmerStyle } = useQuoteRotation();
 *
 *   return (
 *     <blockquote onClick={onClick} style={shimmerStyle}>
 *       "{quote}"
 *     </blockquote>
 *   );
 * }
 */
export function useQuoteRotation(options: QuoteRotationOptions = {}): QuoteRotationState {
  const { initialIndex = 0, shimmerDuration = 800, disabled = false } = options;

  const [index, setIndex] = useState(initialIndex);
  const [isShimmering, setIsShimmering] = useState(false);
  const shimmerTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (shimmerTimeoutRef.current) {
        clearTimeout(shimmerTimeoutRef.current);
      }
    };
  }, []);

  // Trigger shimmer animation
  const triggerShimmer = useCallback(() => {
    if (disabled) return;

    // Clear existing timeout
    if (shimmerTimeoutRef.current) {
      clearTimeout(shimmerTimeoutRef.current);
    }

    setIsShimmering(true);
    shimmerTimeoutRef.current = setTimeout(() => {
      setIsShimmering(false);
    }, shimmerDuration);
  }, [disabled, shimmerDuration]);

  // Navigation functions
  const next = useCallback(() => {
    if (disabled) return;
    setIndex((prev) => (prev + 1) % CURATED_QUOTES.length);
    triggerShimmer();
  }, [disabled, triggerShimmer]);

  const prev = useCallback(() => {
    if (disabled) return;
    setIndex((prev) => (prev - 1 + CURATED_QUOTES.length) % CURATED_QUOTES.length);
    triggerShimmer();
  }, [disabled, triggerShimmer]);

  const goTo = useCallback(
    (newIndex: number) => {
      if (disabled) return;
      const clampedIndex = Math.max(0, Math.min(newIndex, CURATED_QUOTES.length - 1));
      if (clampedIndex !== index) {
        setIndex(clampedIndex);
        triggerShimmer();
      }
    },
    [disabled, index, triggerShimmer]
  );

  // Click handler
  const onClick = useCallback(() => {
    next();
  }, [next]);

  // Compute shimmer style
  const shimmerStyle: React.CSSProperties = isShimmering
    ? {
        animation: `quote-shimmer ${shimmerDuration}ms ease-out`,
        cursor: disabled ? 'default' : 'pointer',
      }
    : {
        cursor: disabled ? 'default' : 'pointer',
      };

  return {
    quote: CURATED_QUOTES[index],
    index,
    isShimmering,
    next,
    prev,
    goTo,
    onClick,
    shimmerClass: isShimmering ? 'quote-shimmering' : '',
    shimmerStyle,
  };
}

// =============================================================================
// CSS Keyframes (inject or use from animations.css)
// =============================================================================

/**
 * Add this to your CSS:
 *
 * @keyframes quote-shimmer {
 *   0% {
 *     filter: brightness(1);
 *     text-shadow: none;
 *   }
 *   30% {
 *     filter: brightness(1.2);
 *     text-shadow: 0 0 8px var(--glow-spore);
 *   }
 *   100% {
 *     filter: brightness(1);
 *     text-shadow: none;
 *   }
 * }
 */

export default useQuoteRotation;
