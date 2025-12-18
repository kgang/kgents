/**
 * VoiceAnchor — Kent's authentic voice, rotating and breathing
 *
 * Displays a voice anchor quote prominently with subtle breathing animation.
 * Rotates periodically to keep the garden alive.
 *
 * @see constants/voiceAnchors.ts
 * @see CLAUDE.md Anti-Sausage Protocol
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Quote } from 'lucide-react';
import { Breathe } from '@/components/joy';
import { VOICE_ANCHORS, getRandomAnchor, type VoiceAnchor as VoiceAnchorType } from '@/constants/voiceAnchors';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';

export interface VoiceAnchorProps {
  /** Time between rotations in ms. Default: 30000 (30s) */
  rotationInterval?: number;
  /** Show the "use" context below quote. Default: true */
  showContext?: boolean;
  /** Callback when anchor changes */
  onAnchorChange?: (anchor: VoiceAnchorType) => void;
  /** Additional CSS classes */
  className?: string;
}

/**
 * VoiceAnchor component — Kent's voice manifest
 *
 * @example
 * ```tsx
 * <VoiceAnchor rotationInterval={20000} />
 * ```
 */
export function VoiceAnchor({
  rotationInterval = 30000,
  showContext = true,
  onAnchorChange,
  className = '',
}: VoiceAnchorProps) {
  const { shouldAnimate } = useMotionPreferences();
  const [currentAnchor, setCurrentAnchor] = useState<VoiceAnchorType>(() =>
    VOICE_ANCHORS[Math.floor(Math.random() * VOICE_ANCHORS.length)]
  );
  const [isHovered, setIsHovered] = useState(false);

  // Rotate anchor periodically (pause on hover)
  useEffect(() => {
    if (isHovered) return;

    const timer = setInterval(() => {
      const nextAnchor = getRandomAnchor(currentAnchor.quote);
      setCurrentAnchor(nextAnchor);
      onAnchorChange?.(nextAnchor);
    }, rotationInterval);

    return () => clearInterval(timer);
  }, [rotationInterval, currentAnchor.quote, isHovered, onAnchorChange]);

  // Manual rotation on click
  const handleClick = useCallback(() => {
    const nextAnchor = getRandomAnchor(currentAnchor.quote);
    setCurrentAnchor(nextAnchor);
    onAnchorChange?.(nextAnchor);
  }, [currentAnchor.quote, onAnchorChange]);

  return (
    <div
      className={`relative ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Breathe intensity={0.2} speed="slow">
        <button
          onClick={handleClick}
          className="w-full text-left group cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500/50 rounded-xl"
          aria-label="Click to show next voice anchor"
        >
          <div className="relative bg-gray-800/60 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6 hover:border-cyan-500/30 transition-colors">
            {/* Quote icon */}
            <div className="absolute -top-3 -left-2 text-cyan-500/40">
              <Quote className="w-8 h-8" />
            </div>

            {/* Quote text */}
            <AnimatePresence mode="wait">
              <motion.blockquote
                key={currentAnchor.quote}
                initial={shouldAnimate ? { opacity: 0, y: 10 } : undefined}
                animate={{ opacity: 1, y: 0 }}
                exit={shouldAnimate ? { opacity: 0, y: -10 } : undefined}
                transition={{ duration: 0.3 }}
                className="text-xl md:text-2xl font-medium text-gray-100 italic pl-4"
              >
                "{currentAnchor.quote}"
              </motion.blockquote>
            </AnimatePresence>

            {/* Context and source */}
            <AnimatePresence mode="wait">
              <motion.div
                key={`${currentAnchor.quote}-meta`}
                initial={shouldAnimate ? { opacity: 0 } : undefined}
                animate={{ opacity: 1 }}
                exit={shouldAnimate ? { opacity: 0 } : undefined}
                transition={{ duration: 0.2, delay: 0.1 }}
                className="mt-4 pl-4 flex items-center justify-between text-sm"
              >
                {showContext && (
                  <span className="text-gray-400">
                    Use when: <span className="text-cyan-400">{currentAnchor.use}</span>
                  </span>
                )}
                <span className="text-gray-500 font-mono text-xs">
                  — {currentAnchor.source}
                </span>
              </motion.div>
            </AnimatePresence>

            {/* Rotation hint */}
            <div className="absolute bottom-2 right-3 text-gray-600 text-xs opacity-0 group-hover:opacity-100 transition-opacity">
              click to rotate
            </div>
          </div>
        </button>
      </Breathe>
    </div>
  );
}

export default VoiceAnchor;
