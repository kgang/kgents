/**
 * WASM Survivors - Death Overlay (DD-8, DD-18)
 *
 * Death clarity: show EXACTLY what killed the player and why.
 * DD-18: Death Narrative - tell a story, enable sharing.
 *
 * Flow:
 * 1. 0.8s freeze frame
 * 2. Screen dims except killer enemy
 * 3. Text overlay: "KILLED BY: [TYPE]"
 * 4. Quick stats: damage source, health before hit
 * 5. Build identity and narrative
 * 6. Share crystal button
 *
 * @see pilots/wasm-survivors-witnessed-run-lab/.outline.md (DD-8, DD-18)
 * @see tests/INTERFACE_CONTRACTS.md
 */

import { useState, useEffect, useCallback } from 'react';
import type { EnemyType } from '@kgents/shared-primitives';
import { COLORS } from '../systems/juice';
import { getBuildIdentity, type UpgradeType } from '../systems/upgrades';

// =============================================================================
// Types
// =============================================================================

export interface DeathInfo {
  killerType: EnemyType;
  killerPosition: { x: number; y: number };
  damageDealt: number;
  healthBefore: number;
  wave: number;
  gameTime: number;
  totalKills: number;
  upgrades: UpgradeType[];
  score: number;
}

interface DeathOverlayProps {
  death: DeathInfo;
  onPlayAgain: () => void;
  onViewCrystal: () => void;
}

type Phase = 'freeze' | 'dim' | 'text' | 'stats' | 'done';

// =============================================================================
// Constants
// =============================================================================

const PHASE_DURATIONS: Record<Phase, number> = {
  freeze: 800,      // 0.8s freeze frame
  dim: 300,         // 0.3s dim transition
  text: 400,        // 0.4s text appear
  stats: 300,       // 0.3s stats appear
  done: 0,          // Final state
};

const ENEMY_NAMES: Record<EnemyType, string> = {
  basic: 'SWARM',
  fast: 'SPEEDER',
  tank: 'BRUTE',
  boss: 'BOSS',
};

const ENEMY_DESCRIPTIONS: Record<EnemyType, string> = {
  basic: 'Overwhelmed by numbers',
  fast: 'Caught by speed',
  tank: 'Crushed by power',
  boss: 'Slain by the champion',
};

// DD-18: Death narrative generation
function generateDeathNarrative(death: DeathInfo): string {
  const buildName = death.upgrades.length > 0
    ? getBuildIdentity(death.upgrades)
    : 'no upgrades yet';

  // Late game death
  if (death.wave >= 8) {
    return `Your ${buildName} build carried you far. Wave ${death.wave} proved too much.`;
  }

  // Early death with upgrades
  if (death.wave >= 4 && death.upgrades.length >= 2) {
    return `The ${buildName} strategy was developing, but ${ENEMY_NAMES[death.killerType]} found an opening.`;
  }

  // Very early death
  if (death.wave <= 2) {
    return 'An early end. Study the patterns. Return stronger.';
  }

  // Mid-game death
  return `Fell to ${ENEMY_NAMES[death.killerType]} at wave ${death.wave}. The ${buildName} journey ends here.`;
}

// DD-18: Generate shareable crystal text
function generateCrystalShare(death: DeathInfo): string {
  const buildName = death.upgrades.length > 0
    ? getBuildIdentity(death.upgrades)
    : 'Starter';
  const minutes = Math.floor(death.gameTime / 60000);
  const seconds = Math.floor((death.gameTime % 60000) / 1000);
  const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;

  return `🎮 WASM Survivors Run
Wave ${death.wave} | ${timeString} | ${death.totalKills} kills
Build: ${buildName}
Killed by: ${ENEMY_NAMES[death.killerType]}
"${generateDeathNarrative(death)}"`;
}

// =============================================================================
// Component
// =============================================================================

export function DeathOverlay({ death, onPlayAgain, onViewCrystal }: DeathOverlayProps) {
  const [phase, setPhase] = useState<Phase>('freeze');
  const [elapsed, setElapsed] = useState(0);
  const [copied, setCopied] = useState(false);

  // DD-18: Share to clipboard
  const handleShareCrystal = useCallback(async () => {
    const shareText = generateCrystalShare(death);
    try {
      await navigator.clipboard.writeText(shareText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      console.log('Share text:', shareText);
    }
  }, [death]);

  // DD-18: Get narrative and build
  const narrative = generateDeathNarrative(death);
  const buildName = death.upgrades.length > 0
    ? getBuildIdentity(death.upgrades)
    : null;

  // Progress through phases
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed((e) => e + 16);
    }, 16);

    return () => clearInterval(interval);
  }, []);

  // Phase transitions
  useEffect(() => {
    const phases: Phase[] = ['freeze', 'dim', 'text', 'stats', 'done'];
    let accumulated = 0;

    for (const p of phases) {
      accumulated += PHASE_DURATIONS[p];
      if (elapsed < accumulated) {
        if (p !== phase) setPhase(p);
        break;
      }
    }
  }, [elapsed, phase]);

  // Keyboard handler
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (phase !== 'done') return;

      switch (e.key.toLowerCase()) {
        case 'r':
          onPlayAgain();
          break;
        case 'c':
          onViewCrystal();
          break;
        case ' ':
        case 'enter':
          onPlayAgain();
          break;
      }
    };

    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [phase, onPlayAgain, onViewCrystal]);

  // Calculate opacity for each element
  const dimOpacity = phase === 'freeze' ? 0 : Math.min((elapsed - PHASE_DURATIONS.freeze) / PHASE_DURATIONS.dim, 1);
  const textOpacity = phase === 'freeze' || phase === 'dim' ? 0 :
    Math.min((elapsed - PHASE_DURATIONS.freeze - PHASE_DURATIONS.dim) / PHASE_DURATIONS.text, 1);
  const statsOpacity = ['freeze', 'dim', 'text'].includes(phase) ? 0 :
    Math.min((elapsed - PHASE_DURATIONS.freeze - PHASE_DURATIONS.dim - PHASE_DURATIONS.text) / PHASE_DURATIONS.stats, 1);

  // Format game time
  const minutes = Math.floor(death.gameTime / 60000);
  const seconds = Math.floor((death.gameTime % 60000) / 1000);
  const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;

  return (
    <div className="fixed inset-0 z-50 pointer-events-none">
      {/* Red vignette effect */}
      <div
        className="absolute inset-0"
        style={{
          background: `radial-gradient(circle at center, transparent 30%, rgba(255, 0, 0, ${dimOpacity * 0.3}) 100%)`,
          transition: 'background 0.3s ease-out',
        }}
      />

      {/* Screen dim layer */}
      <div
        className="absolute inset-0"
        style={{
          backgroundColor: `rgba(0, 0, 0, ${dimOpacity * 0.7})`,
          transition: 'background-color 0.3s ease-out',
        }}
      />

      {/* Content container */}
      <div
        className="absolute inset-0 flex flex-col items-center justify-center pointer-events-auto"
        style={{ opacity: phase === 'freeze' ? 0 : 1 }}
      >
        {/* Main death text */}
        <div
          className="text-center mb-8"
          style={{ opacity: textOpacity, transform: `scale(${0.8 + textOpacity * 0.2})` }}
        >
          <div
            className="text-6xl font-bold mb-2"
            style={{ color: COLORS.enemy }}
          >
            KILLED BY
          </div>
          <div
            className="text-4xl font-bold"
            style={{ color: '#FFFFFF' }}
          >
            {ENEMY_NAMES[death.killerType]}
          </div>
          <div className="text-lg text-gray-400 mt-2">
            {ENEMY_DESCRIPTIONS[death.killerType]}
          </div>
        </div>

        {/* Stats card */}
        <div
          className="bg-gray-900/90 rounded-lg border border-gray-700 p-6 mb-6 min-w-80 max-w-lg"
          style={{ opacity: statsOpacity, transform: `translateY(${(1 - statsOpacity) * 20}px)` }}
        >
          <div className="grid grid-cols-2 gap-4 text-center mb-4">
            <div>
              <div className="text-gray-500 text-sm">WAVE REACHED</div>
              <div className="text-2xl font-bold" style={{ color: COLORS.player }}>
                {death.wave}
              </div>
            </div>
            <div>
              <div className="text-gray-500 text-sm">SURVIVED</div>
              <div className="text-2xl font-bold" style={{ color: COLORS.health }}>
                {timeString}
              </div>
            </div>
            <div>
              <div className="text-gray-500 text-sm">KILLS</div>
              <div className="text-2xl font-bold" style={{ color: COLORS.xp }}>
                {death.totalKills}
              </div>
            </div>
            <div>
              <div className="text-gray-500 text-sm">SCORE</div>
              <div className="text-2xl font-bold text-gray-300">
                {death.score}
              </div>
            </div>
          </div>

          {/* DD-18: Build identity */}
          {buildName && (
            <div className="border-t border-gray-700 pt-4 mt-4 text-center">
              <div className="text-gray-500 text-sm mb-1">YOUR BUILD</div>
              <div className="text-xl font-bold" style={{ color: COLORS.xp }}>
                {buildName}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {death.upgrades.join(' + ')}
              </div>
            </div>
          )}

          {/* DD-18: Narrative */}
          <div className="border-t border-gray-700 pt-4 mt-4">
            <div className="text-gray-400 italic text-center">
              "{narrative}"
            </div>
          </div>
        </div>

        {/* Action buttons */}
        <div
          className="flex gap-3 flex-wrap justify-center"
          style={{ opacity: statsOpacity }}
        >
          <button
            onClick={onPlayAgain}
            className="px-6 py-3 rounded-lg font-bold text-lg transition-all hover:scale-105"
            style={{ backgroundColor: COLORS.player, color: '#000' }}
          >
            PLAY AGAIN (R)
          </button>
          <button
            onClick={onViewCrystal}
            className="px-6 py-3 rounded-lg font-bold text-lg transition-all hover:scale-105 bg-gray-700 text-white hover:bg-gray-600"
          >
            VIEW CRYSTAL (C)
          </button>
          {/* DD-18: Share button */}
          <button
            onClick={handleShareCrystal}
            className="px-6 py-3 rounded-lg font-bold text-lg transition-all hover:scale-105"
            style={{
              backgroundColor: copied ? COLORS.health : COLORS.xp,
              color: '#000',
            }}
          >
            {copied ? '✓ COPIED!' : 'SHARE'}
          </button>
        </div>

        {/* Hint text */}
        <div
          className="absolute bottom-8 text-gray-600 text-sm"
          style={{ opacity: statsOpacity }}
        >
          Press SPACE or ENTER to restart quickly
        </div>
      </div>
    </div>
  );
}

export default DeathOverlay;
