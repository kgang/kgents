/**
 * WASM Survivors - Combo Announcement Overlay
 *
 * Shows combo discovery with tier-appropriate fanfare.
 * Implements the "moment of discovery should feel like finding a secret passage" principle.
 */

import { useEffect, useState } from 'react';
import type { Combo, ComboTier } from '../systems/combos';

interface ComboAnnouncementProps {
  combo: Combo | null;
  onComplete: () => void;
}

const TIER_STYLES: Record<ComboTier, {
  bg: string;
  text: string;
  glow: string;
  duration: number;
  shake: boolean;
}> = {
  obvious: {
    bg: 'rgba(68, 136, 255, 0.2)',
    text: '#4488FF',
    glow: '0 0 30px rgba(68, 136, 255, 0.5)',
    duration: 1500,
    shake: false,
  },
  common: {
    bg: 'rgba(255, 136, 0, 0.2)',
    text: '#FF8800',
    glow: '0 0 40px rgba(255, 136, 0, 0.6)',
    duration: 2000,
    shake: false,
  },
  rare: {
    bg: 'rgba(136, 68, 255, 0.25)',
    text: '#9944FF',
    glow: '0 0 50px rgba(136, 68, 255, 0.7)',
    duration: 2500,
    shake: true,
  },
  legendary: {
    bg: 'rgba(255, 215, 0, 0.3)',
    text: '#FFD700',
    glow: '0 0 60px rgba(255, 215, 0, 0.8), 0 0 100px rgba(255, 215, 0, 0.4)',
    duration: 3000,
    shake: true,
  },
};

export function ComboAnnouncement({ combo, onComplete }: ComboAnnouncementProps) {
  const [phase, setPhase] = useState<'enter' | 'hold' | 'exit'>('enter');

  useEffect(() => {
    if (!combo) return;

    const style = TIER_STYLES[combo.tier];

    // Enter phase
    setPhase('enter');

    // Hold phase
    const holdTimer = setTimeout(() => {
      setPhase('hold');
    }, 300);

    // Exit phase
    const exitTimer = setTimeout(() => {
      setPhase('exit');
    }, style.duration - 500);

    // Complete
    const completeTimer = setTimeout(() => {
      onComplete();
    }, style.duration);

    // Shake effect for epic tiers
    if (style.shake) {
      document.body.classList.add('combo-shake');
      setTimeout(() => {
        document.body.classList.remove('combo-shake');
      }, 500);
    }

    return () => {
      clearTimeout(holdTimer);
      clearTimeout(exitTimer);
      clearTimeout(completeTimer);
    };
  }, [combo, onComplete]);

  if (!combo) return null;

  const style = TIER_STYLES[combo.tier];

  return (
    <div
      className={`
        fixed inset-0 flex items-center justify-center z-[100]
        pointer-events-none
        ${phase === 'enter' ? 'animate-combo-enter' : ''}
        ${phase === 'exit' ? 'animate-combo-exit' : ''}
      `}
      style={{ backgroundColor: style.bg }}
    >
      <div
        className="text-center"
        style={{
          color: style.text,
          textShadow: style.glow,
        }}
      >
        {/* Icon */}
        <div className="text-8xl mb-4 animate-pulse">
          {combo.icon}
        </div>

        {/* Announcement */}
        <div className="text-5xl font-black mb-4 tracking-wider uppercase">
          {combo.announcement}
        </div>

        {/* Description */}
        <div className="text-2xl font-medium opacity-80 mb-4">
          {combo.description}
        </div>

        {/* Flavor text for hidden combos */}
        {combo.flavorText && (
          <div className="text-lg italic opacity-60 mt-4">
            "{combo.flavorText}"
          </div>
        )}
      </div>

      <style>{`
        @keyframes combo-enter {
          0% {
            opacity: 0;
            transform: scale(0.5) rotateX(90deg);
          }
          50% {
            opacity: 1;
            transform: scale(1.1) rotateX(-5deg);
          }
          100% {
            transform: scale(1) rotateX(0);
          }
        }
        .animate-combo-enter {
          animation: combo-enter 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }

        @keyframes combo-exit {
          0% { opacity: 1; transform: scale(1); }
          100% { opacity: 0; transform: scale(1.5); }
        }
        .animate-combo-exit {
          animation: combo-exit 0.5s ease-in forwards;
        }

        @keyframes combo-shake {
          0%, 100% { transform: translateX(0); }
          10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
          20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
        .combo-shake {
          animation: combo-shake 0.5s ease-in-out;
        }
      `}</style>
    </div>
  );
}

export default ComboAnnouncement;
