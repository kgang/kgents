/**
 * WelcomeView — Initial state when no focus is set
 *
 * A living surface with procedural vitality. Not uniform breathing,
 * but varied, organic micro-interactions that feel alive.
 *
 * STARK BIOME: "Stillness, then life" — 90% calm, 10% delight.
 *
 * @see useVitalityOperad — WFC-inspired token composition
 * @see useSpringTilt — Spring physics hover
 * @see useQuoteRotation — Curated quote cycling
 * @see useTitleScatter — Hidden letter scatter delight
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { useVitalityCollapse, VitalityToken } from '@/hooks/useVitalityOperad';
import { useSpringTilt, useKeyPulse } from '@/hooks/useSpringTilt';
import { useQuoteRotation, CURATED_QUOTES } from '@/hooks/useQuoteRotation';
import { useTitleScatter } from '@/hooks/useTitleScatter';

import './WelcomeView.css';

// =============================================================================
// Constants
// =============================================================================

const HINTS = [
  { key: 'Type', action: 'Start a thought in the dialogue pane', shortcut: 't' },
  { key: 'Mention', action: 'Reference a file path to see it here', shortcut: 'm' },
  { key: 'Crystallize', action: 'Capture decisions to the witness stream', shortcut: 'c' },
] as const;

// =============================================================================
// Sub-Components
// =============================================================================

interface HintCardProps {
  hint: (typeof HINTS)[number];
  index: number;
  onRipple?: (x: number, y: number) => void;
}

function HintCard({ hint, index, onRipple }: HintCardProps) {
  const { style, handlers } = useSpringTilt({ maxTilt: 6, stiffness: 0.12 });
  const { isPulsing } = useKeyPulse(hint.shortcut);
  const cardRef = useRef<HTMLDivElement>(null);

  // Staggered entrance animation
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(
      () => setIsVisible(true),
      150 + index * 100 // Stagger by 100ms
    );
    return () => clearTimeout(timer);
  }, [index]);

  // Trigger ripple on click
  const handleClick = useCallback(
    (e: React.MouseEvent) => {
      if (onRipple && cardRef.current) {
        const rect = cardRef.current.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;
        onRipple(x, y);
      }
    },
    [onRipple]
  );

  return (
    <div
      ref={cardRef}
      className={`welcome-view__hint ${isVisible ? 'welcome-view__hint--visible' : ''}`}
      style={{
        ...style,
        animationDelay: `${index * 100}ms`,
      }}
      onClick={handleClick}
      {...handlers}
    >
      <span
        className={`welcome-view__hint-key ${isPulsing ? 'welcome-view__hint-key--pulsing' : ''}`}
      >
        {hint.key}
      </span>
      <span className="welcome-view__hint-action">{hint.action}</span>
    </div>
  );
}

// =============================================================================
// Vitality Layer — Background Tokens
// =============================================================================

interface VitalityLayerProps {
  tokens: VitalityToken[];
  getTokenStyle: (token: VitalityToken) => React.CSSProperties;
}

function VitalityLayer({ tokens, getTokenStyle }: VitalityLayerProps) {
  return (
    <div className="welcome-view__vitality-layer" aria-hidden="true">
      {tokens.map((token) => (
        <div
          key={token.id}
          className={`welcome-view__vitality-token welcome-view__vitality-token--${token.type}`}
          style={getTokenStyle(token)}
        />
      ))}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function WelcomeView() {
  // Reduced motion check
  const prefersReducedMotion = useMemo(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, []);

  // Vitality tokens (WFC-inspired)
  // Note: triggerPulse available for future interactions
  const { tokens, getTokenStyle, triggerRipple } = useVitalityCollapse({
    maxTokens: prefersReducedMotion ? 0 : 8,
    spawnInterval: 2000,
    density: 0.4,
    paused: prefersReducedMotion,
  });

  // Quote rotation
  const { quote, onClick: onQuoteClick, shimmerClass } = useQuoteRotation();

  // Title scatter (hidden delight)
  const {
    letters,
    onDoubleClick: onTitleDoubleClick,
    getLetterStyle,
    isScattered,
    isReforming,
  } = useTitleScatter({ text: 'The Membrane' });

  // Container ref for positioning
  const containerRef = useRef<HTMLDivElement>(null);

  // Handle ripple from hint cards (normalized coords)
  const handleHintRipple = useCallback(
    (x: number, y: number) => {
      // Convert hint card coords to container coords (rough approximation)
      // Hints are centered in container, so offset accordingly
      triggerRipple(0.3 + x * 0.4, 0.5 + y * 0.15);
    },
    [triggerRipple]
  );

  // Subtle parallax on mouse move (very gentle)
  const [parallaxOffset, setParallaxOffset] = useState({ x: 0, y: 0 });

  useEffect(() => {
    if (prefersReducedMotion) return;

    const handleMouseMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 8; // -4 to +4 px
      const y = (e.clientY / window.innerHeight - 0.5) * 4; // -2 to +2 px
      setParallaxOffset({ x, y });
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [prefersReducedMotion]);

  return (
    <div className="welcome-view" ref={containerRef}>
      {/* Vitality Layer — ambient tokens */}
      <VitalityLayer tokens={tokens} getTokenStyle={getTokenStyle} />

      {/* Content with parallax */}
      <div
        className="welcome-view__content"
        style={{
          transform: prefersReducedMotion
            ? undefined
            : `translate(${parallaxOffset.x}px, ${parallaxOffset.y}px)`,
        }}
      >
        {/* Title with scatter effect */}
        <h1
          className={`welcome-view__title ${isScattered || isReforming ? 'welcome-view__title--animating' : ''}`}
          onDoubleClick={onTitleDoubleClick}
          title="Double-click for a surprise"
        >
          {letters.map((letter, i) => (
            <span key={i} style={getLetterStyle(letter)}>
              {letter.char === ' ' ? '\u00A0' : letter.char}
            </span>
          ))}
        </h1>

        <p className="welcome-view__subtitle">Co-thinking surface</p>

        <div className="welcome-view__description">
          <p>This is where you and K-gent think together. Not a chatbot — a collaborative space.</p>
        </div>

        {/* Hint cards with spring tilt */}
        <div className="welcome-view__hints">
          {HINTS.map((hint, i) => (
            <HintCard key={hint.key} hint={hint} index={i} onRipple={handleHintRipple} />
          ))}
        </div>

        {/* Quote with rotation and shimmer */}
        <div className="welcome-view__quote">
          <blockquote
            className={`welcome-view__quote-text ${shimmerClass}`}
            onClick={onQuoteClick}
            title="Click for another insight"
          >
            "{quote}"
          </blockquote>
          <div className="welcome-view__quote-indicator">
            {CURATED_QUOTES.map((_, i) => (
              <span
                key={i}
                className={`welcome-view__quote-dot ${i === CURATED_QUOTES.indexOf(quote) ? 'welcome-view__quote-dot--active' : ''}`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
