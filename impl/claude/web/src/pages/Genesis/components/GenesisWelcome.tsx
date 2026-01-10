/**
 * GenesisWelcome - Phase 1: Arrival
 *
 * "Genesis is self-description, not interrogation."
 *
 * Features:
 * - Breathing animation for title (4-7-8 breathing pattern)
 * - Philosophy quote fade-in
 * - Ambient particle background
 * - Auto-advance after breathing cycle
 *
 * 4-7-8 Breathing Pattern:
 * - 4s inhale (grow/brighten)
 * - 7s hold (subtle pulse)
 * - 8s exhale (shrink/dim)
 * - Total: 19s per cycle
 *
 * @see spec/protocols/genesis-clean-slate.md
 */

import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';

// =============================================================================
// Types
// =============================================================================

interface GenesisWelcomeProps {
  /** Called when welcome phase completes */
  onComplete: () => void;
  /** Auto-advance delay in ms (default: 6000) */
  autoAdvanceDelay?: number;
}

// =============================================================================
// Philosophy Quotes
// =============================================================================

const PHILOSOPHY_QUOTES = [
  {
    text: 'The system already knows itself.',
    attribution: 'Genesis Axiom',
  },
  {
    text: 'Genesis is self-description, not interrogation.',
    attribution: 'Clean Slate Protocol',
  },
  {
    text: 'Every K-Block derives from constitutional principles.',
    attribution: 'Derivation Law',
  },
];

// =============================================================================
// Animation Variants
// =============================================================================

// 4-7-8 breathing pattern
const breathingVariants = {
  inhale: {
    scale: 1.05,
    opacity: 1,
    textShadow: '0 0 30px rgba(196, 167, 125, 0.6)',
    transition: {
      duration: 4,
      ease: 'easeInOut' as const,
    },
  },
  hold: {
    scale: 1.05,
    opacity: 1,
    textShadow: '0 0 40px rgba(196, 167, 125, 0.8)',
    transition: {
      duration: 7,
      ease: 'linear' as const,
    },
  },
  exhale: {
    scale: 1,
    opacity: 0.9,
    textShadow: '0 0 20px rgba(196, 167, 125, 0.3)',
    transition: {
      duration: 8,
      ease: 'easeInOut' as const,
    },
  },
};

const quoteVariants = {
  hidden: {
    opacity: 0,
    y: 20,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      delay: 1.5,
      duration: 1.5,
      ease: [0.25, 0.46, 0.45, 0.94] as const,
    },
  },
};

const continueVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      delay: 3,
      duration: 1,
    },
  },
};

// =============================================================================
// Particle Background Component
// =============================================================================

interface Particle {
  id: number;
  x: number;
  y: number;
  size: number;
  duration: number;
  delay: number;
}

function ParticleBackground() {
  const [particles] = useState<Particle[]>(() =>
    Array.from({ length: 20 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: 2 + Math.random() * 4,
      duration: 15 + Math.random() * 20,
      delay: Math.random() * 10,
    }))
  );

  return (
    <div className="genesis-welcome__particles">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="genesis-welcome__particle"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.2, 0.6, 0.2],
          }}
          transition={{
            duration: p.duration,
            delay: p.delay,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function GenesisWelcome({ onComplete, autoAdvanceDelay = 6000 }: GenesisWelcomeProps) {
  const [breathState, setBreathState] = useState<'inhale' | 'hold' | 'exhale'>('inhale');
  const [quoteIndex] = useState(() => Math.floor(Math.random() * PHILOSOPHY_QUOTES.length));
  const quote = PHILOSOPHY_QUOTES[quoteIndex];

  // Run breathing cycle
  useEffect(() => {
    const cycle = async () => {
      // Inhale (4s)
      setBreathState('inhale');
      await new Promise<void>((r) => {
        setTimeout(r, 4000);
      });

      // Hold (7s)
      setBreathState('hold');
      await new Promise<void>((r) => {
        setTimeout(r, 7000);
      });

      // Exhale (8s)
      setBreathState('exhale');
      await new Promise<void>((r) => {
        setTimeout(r, 8000);
      });
    };

    cycle();
    const interval = setInterval(cycle, 19000);

    return () => clearInterval(interval);
  }, []);

  // Auto-advance timer
  useEffect(() => {
    const timer = setTimeout(onComplete, autoAdvanceDelay);
    return () => clearTimeout(timer);
  }, [onComplete, autoAdvanceDelay]);

  const handleContinue = useCallback(() => {
    onComplete();
  }, [onComplete]);

  return (
    <div className="genesis-welcome">
      {/* Particle background */}
      <ParticleBackground />

      {/* Main content */}
      <div className="genesis-welcome__content">
        {/* Title with breathing animation */}
        <motion.h1
          className="genesis-welcome__title"
          variants={breathingVariants}
          animate={breathState}
        >
          GENESIS
        </motion.h1>

        {/* Philosophy quote */}
        <motion.div
          className="genesis-welcome__quote"
          variants={quoteVariants}
          initial="hidden"
          animate="visible"
        >
          <p className="genesis-welcome__quote-text">"{quote.text}"</p>
          <p className="genesis-welcome__quote-attribution">- {quote.attribution}</p>
        </motion.div>

        {/* Continue button */}
        <motion.button
          type="button"
          className="genesis-welcome__continue"
          variants={continueVariants}
          initial="hidden"
          animate="visible"
          onClick={handleContinue}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Enter the Graph
        </motion.button>
      </div>

      {/* Skip hint */}
      <motion.p
        className="genesis-welcome__skip-hint"
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.5 }}
        transition={{ delay: 4 }}
      >
        Press any key to continue
      </motion.p>
    </div>
  );
}

export default GenesisWelcome;
