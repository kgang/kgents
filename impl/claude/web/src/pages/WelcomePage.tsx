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
import { useNavigate } from 'react-router-dom';

import { useVitalityCollapse, VitalityToken } from '@/hooks/useVitalityOperad';
import { useSpringTilt, useKeyPulse } from '@/hooks/useSpringTilt';
import { useQuoteRotation, CURATED_QUOTES } from '@/hooks/useQuoteRotation';
import { useTitleScatter } from '@/hooks/useTitleScatter';
import { WitnessStream } from '@/components/welcome/WitnessStream';
import { AxiomGarden } from '@/components/welcome/AxiomGarden';

import './WelcomePage.css';

// =============================================================================
// Constants — The Seven Principles
// =============================================================================

/**
 * The seven kgents principles, expressed as invitations.
 * Each is clickable, triggering a ripple of vitality.
 */
const PRINCIPLES = [
  {
    key: 'Tasteful',
    essence: 'Every element earns its place',
    shortcut: '1',
    glyph: '◇',
  },
  {
    key: 'Curated',
    essence: 'Intentional selection, not exhaustive cataloging',
    shortcut: '2',
    glyph: '◈',
  },
  {
    key: 'Ethical',
    essence: 'Augment capability, never replace judgment',
    shortcut: '3',
    glyph: '◉',
  },
  {
    key: 'Joy-Inducing',
    essence: 'Delight in interaction; personality matters',
    shortcut: '4',
    glyph: '✧',
  },
  {
    key: 'Composable',
    essence: 'Agents combine like morphisms in a category',
    shortcut: '5',
    glyph: '⊛',
  },
  {
    key: 'Heterarchical',
    essence: 'Leadership is contextual, not fixed',
    shortcut: '6',
    glyph: '⊕',
  },
  {
    key: 'Generative',
    essence: 'Spec is compression; design generates implementation',
    shortcut: '7',
    glyph: '❋',
  },
] as const;

// =============================================================================
// Sub-Components
// =============================================================================

interface PrincipleCardProps {
  principle: (typeof PRINCIPLES)[number];
  index: number;
  onRipple?: (x: number, y: number) => void;
}

function PrincipleCard({ principle, index, onRipple }: PrincipleCardProps) {
  const { style, handlers } = useSpringTilt({ maxTilt: 8, stiffness: 0.15 });
  const { isPulsing } = useKeyPulse(principle.shortcut);
  const cardRef = useRef<HTMLDivElement>(null);

  // Staggered entrance animation
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(
      () => setIsVisible(true),
      200 + index * 60 // Stagger by 60ms for snappier cascade
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
      className={`welcome-view__principle ${isVisible ? 'welcome-view__principle--visible' : ''}`}
      style={{
        ...style,
        animationDelay: `${index * 60}ms`,
      }}
      onClick={handleClick}
      {...handlers}
    >
      <span
        className={`welcome-view__principle-glyph ${isPulsing ? 'welcome-view__principle-glyph--pulsing' : ''}`}
      >
        {principle.glyph}
      </span>
      <div className="welcome-view__principle-content">
        <span className="welcome-view__principle-key">{principle.key}</span>
        <span className="welcome-view__principle-essence">{principle.essence}</span>
      </div>
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
  const navigate = useNavigate();

  // Easter egg state
  const [showEasterEgg, setShowEasterEgg] = useState(false);
  const konamiRef = useRef<string[]>([]);

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
  } = useTitleScatter({ text: 'kgents' });

  // Container ref for positioning
  const containerRef = useRef<HTMLDivElement>(null);

  // Handle ripple from principle cards (normalized coords)
  const handlePrincipleRipple = useCallback(
    (x: number, y: number) => {
      // Convert principle card coords to container coords (rough approximation)
      // Principles are centered in container, so offset accordingly
      triggerRipple(0.3 + x * 0.4, 0.4 + y * 0.3);
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

  // Easter egg: Type "zero" to trigger whimsical animation
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Ignore if typing in input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

      konamiRef.current = [...konamiRef.current, e.key.toLowerCase()].slice(-4);

      if (konamiRef.current.join('') === 'zero') {
        setShowEasterEgg(true);
        // Auto-hide after 3 seconds
        setTimeout(() => setShowEasterEgg(false), 3000);
        // Navigate to void.telescope (AGENTESE path) after a delay
        setTimeout(() => navigate('/void.telescope'), 1500);
        konamiRef.current = [];
      }
    };

    window.addEventListener('keypress', handleKeyPress);
    return () => window.removeEventListener('keypress', handleKeyPress);
  }, [navigate]);

  return (
    <div className="welcome-view" ref={containerRef}>
      {/* Easter egg overlay */}
      {showEasterEgg && (
        <div className="welcome-view__easter-egg">
          <div className="welcome-view__easter-egg-content">
            <span className="welcome-view__easter-egg-glyph">◇</span>
            <span className="welcome-view__easter-egg-text">
              "The seed is not the garden. The seed is the capacity for gardening."
            </span>
          </div>
        </div>
      )}

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

        <p className="welcome-view__subtitle">Ideas that want to help you think</p>

        <div className="welcome-view__description">
          <p>
            Not chatbots. Not tools. <em>Collaborators.</em>
            <br />
            <span className="welcome-view__whisper">Agents that compose, grow, and remember.</span>
          </p>
        </div>

        {/* Seven Principles — the generative core */}
        <div className="welcome-view__principles">
          {PRINCIPLES.map((principle, i) => (
            <PrincipleCard
              key={principle.key}
              principle={principle}
              index={i}
              onRipple={handlePrincipleRipple}
            />
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

        {/* Keyboard hints — visible but subtle */}
        <p className="welcome-view__invitation">
          Press <kbd>1</kbd>-<kbd>7</kbd> to feel each principle
        </p>

        {/* Proof Engine Interactive Components */}
        <AxiomGarden />
        <WitnessStream />

        {/* CTA Buttons — AGENTESE Navigation
            Three tiers: Primary (Document), Secondary (Chat/Director/Memory), Signature (Telescope)
            "Every element earns its place" — no Chart, it's not a core surface */}
        <div className="welcome-view__cta">
          <button
            className="welcome-view__cta-button welcome-view__cta-button--primary"
            onClick={() => navigate('/world.document')}
          >
            Enter the Hypergraph
          </button>
        </div>
        <div className="welcome-view__cta welcome-view__cta--secondary">
          <button
            className="welcome-view__cta-button welcome-view__cta-button--chat"
            onClick={() => navigate('/self.chat')}
          >
            Chat
          </button>
          <button
            className="welcome-view__cta-button"
            onClick={() => navigate('/self.director')}
          >
            Director
          </button>
          <button
            className="welcome-view__cta-button"
            onClick={() => navigate('/self.memory')}
          >
            Memory
          </button>
          <button
            className="welcome-view__cta-button welcome-view__cta-button--proof-engine"
            onClick={() => navigate('/zero-seed')}
            title="Five-level epistemic architecture"
          >
            Zero Seed
          </button>
        </div>
      </div>
    </div>
  );
}

export default WelcomeView;
