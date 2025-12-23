/**
 * Personality Loading Component
 *
 * Jewel-specific loading messages that give personality to wait states.
 * Instead of generic "Loading...", show contextual messages.
 *
 * Uses Lucide icons per visual-system.md - no emojis in kgents-authored copy.
 *
 * Foundation 5: Personality & Joy - Personality Loading States
 *
 * @example
 * ```tsx
 * <PersonalityLoading jewel="brain" />
 * // Shows Brain icon with "Crystallizing memories..."
 *
 * <PersonalityLoading jewel="forge" action="create" />
 * // Shows Palette icon with "Building your artifact..."
 * ```
 */

import { useState, useEffect, useMemo } from 'react';
import type { CSSProperties } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Breathe } from './Breathe';
import { useMotionPreferences } from './useMotionPreferences';
import { JEWEL_ICONS, JEWEL_COLORS, type JewelName } from '../../constants/jewels';
// TreeIcon removed - no longer needed after gestalt removal

export type CrownJewel = 'brain' | 'gardener' | 'forge' | 'domain'; // gestalt, coalition, park removed 2025-12-21

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
  /** Use organic/forest-themed variant */
  organic?: boolean;
}

// =============================================================================
// Jewel Configuration
// =============================================================================

interface JewelConfig {
  messages: string[];
  actionVerbs: Record<string, string>;
  /** Organic/forest-themed messages (optional) */
  organicMessages?: string[];
}

/**
 * Jewel-specific messages for loading states.
 * Icons and colors come from JEWEL_ICONS and JEWEL_COLORS constants.
 */
const JEWEL_CONFIG: Record<CrownJewel, JewelConfig> = {
  brain: {
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
  // gestalt removed 2025-12-21
  gardener: {
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
  forge: {
    messages: [
      'Heating the forge...',
      'Preparing the tools...',
      'Laying out the anvil...',
      'Gathering materials...',
      'Ready to build...',
    ],
    actionVerbs: {
      create: 'Building your artifact...',
      collaborate: 'Coordinating builders...',
      refine: 'Refining the work...',
    },
  },
  // coalition, park removed 2025-12-21
  domain: {
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
    iconSize: 24, // Lucide icon size
    text: 'text-xs',
    gap: 'gap-2',
  },
  md: {
    container: 'p-4',
    iconSize: 40, // Lucide icon size
    text: 'text-sm',
    gap: 'gap-3',
  },
  lg: {
    container: 'p-6',
    iconSize: 64, // Lucide icon size
    text: 'text-base',
    gap: 'gap-4',
  },
};

// =============================================================================
// Component
// =============================================================================

/**
 * Personality loading indicator with jewel-specific messaging.
 * Uses Lucide icons instead of emojis per visual-system.md.
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

  // Get the icon component from JEWEL_ICONS
  const IconComponent = JEWEL_ICONS[jewel as JewelName];
  const iconColor = JEWEL_COLORS[jewel as JewelName]?.primary ?? '#64748B';

  // Use organic messages if available and organic mode is enabled
  const displayMessages =
    organic && config.organicMessages ? config.organicMessages : config.messages;

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

  const currentMessage = typeof getMessage === 'string' ? getMessage : getMessage[messageIndex];

  return (
    <div
      className={`flex flex-col items-center justify-center ${sizeConfig.container} ${sizeConfig.gap} ${className}`}
      style={style}
    >
      {/* Animated icon - uses Lucide icons per visual-system.md */}
      <Breathe intensity={0.4} speed="slow">
        <IconComponent size={sizeConfig.iconSize} color={iconColor} strokeWidth={1.5} />
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
            style={{ color: iconColor }}
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
 * Uses Lucide icons instead of emojis.
 */
export function PersonalityLoadingInline({
  jewel,
  className = '',
}: {
  jewel: CrownJewel;
  className?: string;
}) {
  const config = JEWEL_CONFIG[jewel];
  const IconComponent = JEWEL_ICONS[jewel as JewelName];
  const iconColor = JEWEL_COLORS[jewel as JewelName]?.primary ?? '#64748B';

  const randomMessage = useMemo(
    () => config.messages[Math.floor(Math.random() * config.messages.length)],
    [config]
  );

  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      <Breathe intensity={0.3}>
        <IconComponent size={16} color={iconColor} strokeWidth={1.5} />
      </Breathe>
      <span className="text-gray-400" style={{ color: iconColor }}>
        {randomMessage}
      </span>
    </span>
  );
}

export default PersonalityLoading;
