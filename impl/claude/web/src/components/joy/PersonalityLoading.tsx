/**
 * Personality Loading Component
 *
 * Jewel-specific loading messages that give personality to wait states.
 * Instead of generic "Loading...", show contextual messages.
 *
 * Foundation 5: Personality & Joy - Personality Loading States
 *
 * @example
 * ```tsx
 * <PersonalityLoading jewel="brain" />
 * // "Crystallizing memories..."
 *
 * <PersonalityLoading jewel="gestalt" action="analyzing" />
 * // "Analyzing architecture..."
 * ```
 */

import { useState, useEffect, useMemo } from 'react';
import type { CSSProperties } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Breathe } from './Breathe';
import { useMotionPreferences } from './useMotionPreferences';

export type CrownJewel = 'brain' | 'gestalt' | 'gardener' | 'atelier' | 'coalition' | 'park' | 'domain';

export interface PersonalityLoadingProps {
  /** Which jewel context */
  jewel: CrownJewel;
  /** Optional specific action being performed */
  action?: string;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Rotate through messages */
  rotate?: boolean;
  /** Rotation interval in ms. Default: 3000 */
  rotateInterval?: number;
  /** Additional CSS classes */
  className?: string;
  /** Additional inline styles */
  style?: CSSProperties;
  /** Use organic/forest-themed variant (for Gestalt forest mode) */
  organic?: boolean;
}

// =============================================================================
// Jewel Configuration
// =============================================================================

interface JewelConfig {
  emoji: string;
  color: string;
  messages: string[];
  actionVerbs: Record<string, string>;
  /** Organic/forest-themed messages (optional) */
  organicMessages?: string[];
  /** Organic emoji override */
  organicEmoji?: string;
}

const JEWEL_CONFIG: Record<CrownJewel, JewelConfig> = {
  brain: {
    emoji: '🧠',
    color: '#06B6D4', // cyan-500
    messages: [
      'Crystallizing memories...',
      'Traversing the hologram...',
      'Surfacing forgotten thoughts...',
      'Weaving neural pathways...',
      'Mapping cognitive terrain...',
    ],
    actionVerbs: {
      capture: 'Capturing into crystal...',
      search: 'Searching neural networks...',
      surface: 'Surfacing ghost memories...',
      analyze: 'Analyzing memory topology...',
    },
  },
  gestalt: {
    emoji: '🏗️',
    color: '#22C55E', // green-500
    messages: [
      'Analyzing architecture...',
      'Computing health metrics...',
      'Detecting drift patterns...',
      'Mapping module topology...',
      'Evaluating dependencies...',
    ],
    actionVerbs: {
      scan: 'Scanning codebase structure...',
      analyze: 'Analyzing module health...',
      detect: 'Detecting violations...',
      compute: 'Computing health grades...',
    },
    // Forest-themed messages for organic mode
    organicEmoji: '🌲',
    organicMessages: [
      'Surveying the forest canopy...',
      'Tracing root systems...',
      'Sensing ecosystem health...',
      'Mapping the growth rings...',
      'Feeling the pulse of the grove...',
    ],
  },
  gardener: {
    emoji: '🌱',
    color: '#84CC16', // lime-500
    messages: [
      'Preparing the garden...',
      'Gathering context...',
      'Sensing the forest...',
      'Tending to the growth...',
      'Nurturing ideas...',
    ],
    actionVerbs: {
      plan: 'Planning the session...',
      research: 'Researching context...',
      develop: 'Cultivating ideas...',
      implement: 'Planting seeds...',
    },
  },
  atelier: {
    emoji: '🎨',
    color: '#F59E0B', // amber-500
    messages: [
      'Mixing the palette...',
      'Consulting the muses...',
      'Preparing the canvas...',
      'Gathering inspiration...',
      'Awakening creativity...',
    ],
    actionVerbs: {
      create: 'Creating your piece...',
      collaborate: 'Coordinating artisans...',
      bid: 'Processing auction...',
      refine: 'Refining the work...',
    },
  },
  coalition: {
    emoji: '🤝',
    color: '#8B5CF6', // violet-500
    messages: [
      'Assembling the team...',
      'Coordinating specialists...',
      'Forming consensus...',
      'Aligning perspectives...',
      'Building bridges...',
    ],
    actionVerbs: {
      form: 'Forming coalition...',
      coordinate: 'Coordinating members...',
      discuss: 'Facilitating discussion...',
      decide: 'Building consensus...',
    },
  },
  park: {
    emoji: '🎭',
    color: '#EC4899', // pink-500
    messages: [
      'Setting the stage...',
      'Preparing the scene...',
      'Summoning characters...',
      'Writing the script...',
      'Dimming the lights...',
    ],
    actionVerbs: {
      inhabit: 'Entering the scenario...',
      interact: 'Processing dialogue...',
      explore: 'Exploring possibilities...',
      conclude: 'Closing the curtain...',
    },
  },
  domain: {
    emoji: '🏛️',
    color: '#EF4444', // red-500
    messages: [
      'Initializing simulation...',
      'Loading scenarios...',
      'Calibrating timers...',
      'Preparing drill...',
      'Setting conditions...',
    ],
    actionVerbs: {
      simulate: 'Running simulation...',
      drill: 'Executing drill...',
      assess: 'Assessing response...',
      evaluate: 'Evaluating outcomes...',
    },
  },
};

// =============================================================================
// Size Configuration
// =============================================================================

const SIZE_CONFIG = {
  sm: {
    container: 'p-3',
    emoji: 'text-2xl',
    text: 'text-xs',
    gap: 'gap-2',
  },
  md: {
    container: 'p-4',
    emoji: 'text-4xl',
    text: 'text-sm',
    gap: 'gap-3',
  },
  lg: {
    container: 'p-6',
    emoji: 'text-6xl',
    text: 'text-base',
    gap: 'gap-4',
  },
};

// =============================================================================
// Component
// =============================================================================

/**
 * Personality loading indicator with jewel-specific messaging.
 */
export function PersonalityLoading({
  jewel,
  action,
  size = 'md',
  rotate = true,
  rotateInterval = 3000,
  className = '',
  style,
  organic = false,
}: PersonalityLoadingProps) {
  const { shouldAnimate } = useMotionPreferences();
  const config = JEWEL_CONFIG[jewel];
  const sizeConfig = SIZE_CONFIG[size];

  // Use organic emoji/messages if available and organic mode is enabled
  const displayEmoji = organic && config.organicEmoji ? config.organicEmoji : config.emoji;
  const displayMessages = organic && config.organicMessages ? config.organicMessages : config.messages;

  // Get the message to display
  const getMessage = useMemo(() => {
    if (action && config.actionVerbs[action]) {
      return config.actionVerbs[action];
    }
    return displayMessages;
  }, [action, config, displayMessages]);

  // State for rotating messages
  const [messageIndex, setMessageIndex] = useState(0);

  // Rotate through messages
  useEffect(() => {
    if (!rotate || typeof getMessage === 'string') return;

    const timer = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % getMessage.length);
    }, rotateInterval);

    return () => clearInterval(timer);
  }, [rotate, getMessage, rotateInterval]);

  const currentMessage = typeof getMessage === 'string'
    ? getMessage
    : getMessage[messageIndex];

  return (
    <div
      className={`flex flex-col items-center justify-center ${sizeConfig.container} ${sizeConfig.gap} ${className}`}
      style={style}
    >
      {/* Animated emoji - uses organic variant if enabled */}
      <Breathe intensity={0.4} speed="slow">
        <span className={sizeConfig.emoji}>{displayEmoji}</span>
      </Breathe>

      {/* Message with fade transition */}
      {shouldAnimate ? (
        <AnimatePresence mode="wait">
          <motion.p
            key={currentMessage}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.2 }}
            className={`text-gray-400 ${sizeConfig.text}`}
            style={{ color: config.color }}
          >
            {currentMessage}
          </motion.p>
        </AnimatePresence>
      ) : (
        <p className={`text-gray-400 ${sizeConfig.text}`}>{currentMessage}</p>
      )}
    </div>
  );
}

/**
 * Inline personality loading for smaller contexts.
 */
export function PersonalityLoadingInline({
  jewel,
  className = '',
}: {
  jewel: CrownJewel;
  className?: string;
}) {
  const config = JEWEL_CONFIG[jewel];
  const randomMessage = useMemo(
    () => config.messages[Math.floor(Math.random() * config.messages.length)],
    [config]
  );

  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      <Breathe intensity={0.3}>
        <span>{config.emoji}</span>
      </Breathe>
      <span className="text-gray-400" style={{ color: config.color }}>
        {randomMessage}
      </span>
    </span>
  );
}

export default PersonalityLoading;
