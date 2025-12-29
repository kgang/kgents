/**
 * WASM Survivors - Death Overlay (DD-8, DD-18, CREATIVE-SPECTACLE)
 *
 * Death clarity: show EXACTLY what killed the player and why.
 * DD-18: Death Narrative - tell a story, enable sharing.
 * CREATIVE-SPECTACLE: Death with DIGNITY - spiral descent, acceptance not despair.
 *
 * Flow:
 * 1. 0.3s white flash (impact)
 * 2. 0.6s spiral descent animation
 * 3. 0.3s impact with honey burst
 * 4. 0.8s rest with dignity
 * 5. Stats fade in with warm amber tint
 * 6. Voice line: "The colony always wins. ...Respect."
 *
 * Dignity Elements:
 * - Acceptance pose, not ragdoll
 * - Colony buzzing calms to peaceful hum
 * - Warm amber tint, not cold
 * - "Wave X reached" not "GAME OVER"
 *
 * @see pilots/wasm-survivors-game/.outline.md (DD-8, DD-18)
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md (Part VII, V3: Dignity)
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import type { EnemyType } from '../types';
import { COLORS } from '../systems/juice';
import {
  getBuildIdentity,
  getGhostSummary,
  ARCHETYPES,
  type UpgradeType,
  type BuildIdentity,
  type ArchetypeId,
} from '../systems/upgrades';
import type { ColonyLearning } from '../systems/colony-memory';
import type { AxiomGuardReport } from '../systems/axiom-guards';

// =============================================================================
// Types
// =============================================================================

// DD-21: Attack types for specific death attribution (bee-themed)
// Mapping: lunge->swarm, charge->sting, stomp->block, projectile->sticky
export type AttackType = 'swarm' | 'sting' | 'block' | 'sticky' | 'combo' | 'contact';

/**
 * Colony learnings summary for death screen
 * V5: WITNESSED - collaborative tone, not accusatory
 */
export interface ColonyLearningSummary {
  headline: string;
  learnings: ColonyLearning[];
  adaptationLevel: number;
  ballsEscaped: number;
  ballsEncountered: number;
}

/**
 * Ghost summary for death screen
 * Shows alternate paths not taken - curious "what if", not regret
 */
export interface GhostSummary {
  ghostArchetypes: ArchetypeId[];
  pivotMoments: number;
  alternateBuilds: string[];
}

export interface DeathInfo {
  killerType: EnemyType;
  attackType?: AttackType;  // DD-21: Which attack killed the player
  killerPosition: { x: number; y: number };
  damageDealt: number;
  healthBefore: number;
  wave: number;
  gameTime: number;
  totalKills: number;
  upgrades: UpgradeType[];
  score: number;
  // V5 WITNESSED: Colony learnings and ghost summary
  colonyLearnings?: ColonyLearningSummary;
  ghostSummary?: GhostSummary;
  buildIdentity?: BuildIdentity;
}

interface DeathOverlayProps {
  death: DeathInfo;
  onPlayAgain: () => void;
  onViewCrystal: () => void;
  // V5 WITNESSED: Can also pass these as props for backwards compatibility
  colonyLearnings?: ColonyLearningSummary;
  ghostSummary?: GhostSummary;
  // Part I: Axiom Guard Report from the Four True Axioms
  axiomReport?: AxiomGuardReport;
}

// CREATIVE-SPECTACLE: Enhanced death animation phases
type Phase =
  | 'flash'      // White impact flash
  | 'spiral'     // Spiral descent animation
  | 'impact'     // Honey burst on impact
  | 'rest'       // Dignified acceptance
  | 'voiceline'  // "The colony always wins..."
  | 'stats'      // Stats fade in
  | 'done';      // Ready for input

// =============================================================================
// Constants
// =============================================================================

// CREATIVE-SPECTACLE: Dramatic death sequence timing
const PHASE_DURATIONS: Record<Phase, number> = {
  flash: 150,       // 0.15s white flash (brief, impactful)
  spiral: 600,      // 0.6s spiral descent (3 rotations)
  impact: 300,      // 0.3s honey burst
  rest: 500,        // 0.5s acceptance pose
  voiceline: 1200,  // 1.2s voice line display
  stats: 400,       // 0.4s stats appear
  done: 0,          // Final state
};

// CREATIVE-SPECTACLE: Spiral animation parameters
const SPIRAL_CONFIG = {
  rotations: 3,           // Full rotations during descent
  descentDistance: 60,    // Pixels to descend
  particleCount: 25,      // Pollen particles
  particleColor: '#FFE066', // Soft yellow pollen
};

// CREATIVE-SPECTACLE: Dignity voice lines (respect, not despair)
const DIGNITY_VOICE_LINES = [
  'The colony always wins. ...Respect.',
  'A good death. They earned it.',
  'Tell them I fought well.',
  'A magnificent end.',
];

// Bee-themed enemy names (Run 033+) with legacy type aliases
const ENEMY_NAMES: Record<EnemyType, string> = {
  worker: 'WORKER',
  scout: 'SCOUT',
  guard: 'GUARD',
  propolis: 'PROPOLIS',
  royal: 'ROYAL',
  // Legacy aliases
  basic: 'WORKER',
  fast: 'SCOUT',
  tank: 'GUARD',
  spitter: 'PROPOLIS',
  boss: 'ROYAL',
  colossal_tide: 'COLOSSAL',
};

// Bee-themed enemy descriptions (Run 033+) with legacy type aliases
const ENEMY_DESCRIPTIONS: Record<EnemyType, string> = {
  worker: 'Overwhelmed by the swarm',
  scout: 'Outpaced by the scouts',
  guard: 'Crushed by a guardian',
  propolis: 'Stuck down from afar',
  royal: 'Slain by the royal guard',
  // Legacy aliases
  basic: 'Overwhelmed by the swarm',
  fast: 'Outpaced by the scouts',
  tank: 'Crushed by a guardian',
  spitter: 'Stuck down from afar',
  boss: 'Slain by the royal guard',
  colossal_tide: 'Consumed by the tide',
};

// DD-21: Attack type names for specific death attribution (bee-themed)
const ATTACK_NAMES: Record<AttackType, string> = {
  swarm: 'SWARM',       // Workers swarming
  sting: 'STING',       // Scouts' piercing attack
  block: 'BLOCK',       // Guards blocking and crushing
  sticky: 'STICKY',     // Propolis ranged attack
  combo: 'COMBO',       // Multi-attack sequence
  contact: 'CONTACT',   // Basic touch damage
};

const ATTACK_DESCRIPTIONS: Record<AttackType, string> = {
  swarm: 'Swarmed by the colony',
  sting: 'Stung by a piercing attack',
  block: 'Blocked and crushed by a guardian',
  sticky: 'Hit by propolis from afar',
  combo: 'Overwhelmed by coordinated attacks',
  contact: 'Touched by the hive',
};

// DD-21: Get death cause text
function getDeathCauseText(death: DeathInfo): { title: string; description: string } {
  if (death.attackType && death.attackType !== 'contact') {
    // Specific attack death: "SPEEDER CHARGE"
    return {
      title: `${ENEMY_NAMES[death.killerType]} ${ATTACK_NAMES[death.attackType]}`,
      description: ATTACK_DESCRIPTIONS[death.attackType],
    };
  }
  // Contact damage: "SWARM"
  return {
    title: ENEMY_NAMES[death.killerType],
    description: ENEMY_DESCRIPTIONS[death.killerType],
  };
}

/**
 * DD-18 + CREATIVE-IDENTITY: Death narrative generation.
 *
 * The hornet doesn't "fall" or "lose" - they complete their arc with dignity.
 * Dark humor and swagger, not despair or regret.
 */
function generateDeathNarrative(death: DeathInfo): string {
  const buildName = death.upgrades.length > 0
    ? getBuildIdentity(death.upgrades)
    : null;

  // Late game death (Wave 8+) - Dignified acceptance, respect for the colony
  if (death.wave >= 8) {
    if (death.totalKills >= 100) {
      return `${death.totalKills} souls claimed. Wave ${death.wave} reached. A magnificent hunt.`;
    }
    if (buildName) {
      return `The ${buildName} hunt reached its natural end. The colony earned this.`;
    }
    return `Wave ${death.wave}. The colony always wins. ...Respect.`;
  }

  // Mid-late game (Wave 5-7) - Dark humor, still swagger
  if (death.wave >= 5) {
    if (death.totalKills >= 50) {
      return `${death.totalKills} kills. Not bad. The colony was ready this time.`;
    }
    return `They were learning. How adorable... and effective.`;
  }

  // Mid game (Wave 3-4) - Acknowledging, but with style
  if (death.wave >= 3) {
    if (buildName) {
      return `The ${buildName} strategy was developing. The colony had other plans.`;
    }
    return `${death.totalKills} kills. A warm-up. The real hunt begins next time.`;
  }

  // Very early death (Wave 1-2) - Brief but defiant
  if (death.totalKills >= 10) {
    return `A brief hunt. ${death.totalKills} souls claimed. Return and claim more.`;
  }
  return `The colony was ready. Next time, so will I be.`;
}

/**
 * DD-18 + CREATIVE-IDENTITY: Generate shareable crystal text.
 *
 * The share text should be quotable and have swagger.
 * "The colony always wins" is the catchphrase.
 */
function generateCrystalShare(death: DeathInfo): string {
  const buildName = death.upgrades.length > 0
    ? getBuildIdentity(death.upgrades)
    : null;
  const minutes = Math.floor(death.gameTime / 60000);
  const seconds = Math.floor((death.gameTime % 60000) / 1000);
  const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;

  // Late game - legendary share format
  if (death.wave >= 8) {
    return `"The colony always wins. ...Respect."

${death.totalKills} kills | Wave ${death.wave} | ${timeString}
${buildName ? `Build: ${buildName}` : 'A magnificent hunt.'}

#HornetSiege #TheColonyAlwaysWins`;
  }

  // Mid game - respectable share format
  if (death.wave >= 4) {
    return `Hornet Siege: Wave ${death.wave} | ${death.totalKills} kills | ${timeString}

"${generateDeathNarrative(death)}"

#HornetSiege`;
  }

  // Early death - brief share
  return `Hornet Siege: ${death.totalKills} kills in ${timeString}

The hunt continues.

#HornetSiege`;
}

// =============================================================================
// Component
// =============================================================================

export function DeathOverlay({
  death,
  onPlayAgain,
  onViewCrystal,
  colonyLearnings: colonyLearningsProp,
  ghostSummary: ghostSummaryProp,
  axiomReport,
}: DeathOverlayProps) {
  const [phase, setPhase] = useState<Phase>('flash');
  const [elapsed, setElapsed] = useState(0);
  const [copied, setCopied] = useState(false);

  // CREATIVE-SPECTACLE: Select a random dignity voice line
  const voiceLine = useMemo(() => {
    return DIGNITY_VOICE_LINES[Math.floor(Math.random() * DIGNITY_VOICE_LINES.length)];
  }, []);

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

  // V5 WITNESSED: Compute ghost summary - prop takes precedence, then death.ghostSummary, then compute from buildIdentity
  const ghostSummary = useMemo(() => {
    if (ghostSummaryProp) return ghostSummaryProp;
    if (death.ghostSummary) return death.ghostSummary;
    if (death.buildIdentity) return getGhostSummary(death.buildIdentity);
    return null;
  }, [ghostSummaryProp, death.ghostSummary, death.buildIdentity]);

  // V5 WITNESSED: Get colony learnings - prop takes precedence, then death.colonyLearnings
  const colonyLearnings = colonyLearningsProp ?? death.colonyLearnings;

  // Progress through phases
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed((e) => e + 16);
    }, 16);

    return () => clearInterval(interval);
  }, []);

  // CREATIVE-SPECTACLE: Enhanced phase transitions
  useEffect(() => {
    const phases: Phase[] = ['flash', 'spiral', 'impact', 'rest', 'voiceline', 'stats', 'done'];
    let accumulated = 0;

    for (const p of phases) {
      accumulated += PHASE_DURATIONS[p];
      if (elapsed < accumulated) {
        if (p !== phase) setPhase(p);
        break;
      }
    }
  }, [elapsed, phase]);

  // CREATIVE-SPECTACLE: Calculate spiral animation values
  const spiralProgress = Math.min(1, Math.max(0,
    (elapsed - PHASE_DURATIONS.flash) / PHASE_DURATIONS.spiral
  ));
  const spiralRotation = spiralProgress * SPIRAL_CONFIG.rotations * Math.PI * 2;
  const spiralDescent = spiralProgress * SPIRAL_CONFIG.descentDistance;

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

  // CREATIVE-SPECTACLE: Calculate opacity and effects for each phase
  const flashOpacity = phase === 'flash' ? 1 - (elapsed / PHASE_DURATIONS.flash) : 0;

  const preSpiralTime = PHASE_DURATIONS.flash;
  const preImpactTime = preSpiralTime + PHASE_DURATIONS.spiral;
  const preRestTime = preImpactTime + PHASE_DURATIONS.impact;
  const preVoiceTime = preRestTime + PHASE_DURATIONS.rest;
  const preStatsTime = preVoiceTime + PHASE_DURATIONS.voiceline;

  // Dim layer fades in during spiral and stays
  const dimOpacity = phase === 'flash' ? 0 :
    Math.min(0.75, (elapsed - preSpiralTime) / PHASE_DURATIONS.spiral * 0.75);

  // Impact burst visible during impact phase
  const impactProgress = phase === 'impact' ?
    (elapsed - preImpactTime) / PHASE_DURATIONS.impact : (phase === 'rest' || phase === 'voiceline' || phase === 'stats' || phase === 'done') ? 1 : 0;

  // Voice line fades in during voiceline phase
  const voicelineOpacity = ['voiceline', 'stats', 'done'].includes(phase) ?
    Math.min(1, (elapsed - preVoiceTime) / 300) : 0;

  // Stats fade in during stats phase
  const statsOpacity = ['stats', 'done'].includes(phase) ?
    Math.min(1, (elapsed - preStatsTime) / PHASE_DURATIONS.stats) : 0;

  // CREATIVE-SPECTACLE: Warm amber tint increases during death (dignity, not cold)
  const warmthLevel = phase === 'flash' ? 0 : Math.min(0.15, (elapsed - preSpiralTime) / 2000 * 0.15);

  // Format game time
  const minutes = Math.floor(death.gameTime / 60000);
  const seconds = Math.floor((death.gameTime % 60000) / 1000);
  const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;

  return (
    <div className="fixed inset-0 z-50 pointer-events-none">
      {/* CREATIVE-SPECTACLE: White flash on impact */}
      {flashOpacity > 0 && (
        <div
          className="absolute inset-0"
          style={{
            backgroundColor: `rgba(255, 255, 255, ${flashOpacity})`,
            zIndex: 100,
          }}
        />
      )}

      {/* CREATIVE-SPECTACLE: Warm amber vignette (dignity, not cold red) */}
      <div
        className="absolute inset-0"
        style={{
          background: `radial-gradient(circle at center,
            transparent 20%,
            rgba(244, 163, 0, ${warmthLevel}) 60%,
            rgba(0, 0, 0, ${dimOpacity * 0.4}) 100%)`,
          transition: 'background 0.3s ease-out',
        }}
      />

      {/* Screen dim layer with warm tint */}
      <div
        className="absolute inset-0"
        style={{
          backgroundColor: `rgba(20, 15, 10, ${dimOpacity})`,
          transition: 'background-color 0.3s ease-out',
        }}
      />

      {/* CREATIVE-SPECTACLE: Spiral descent particle hints (CSS approximation) */}
      {phase === 'spiral' && (
        <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
          {Array.from({ length: 12 }).map((_, i) => {
            const angle = (i / 12) * Math.PI * 2 + spiralRotation;
            const radius = 80 - spiralProgress * 30;
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius + spiralDescent;
            const scale = 1 - spiralProgress * 0.5;
            const opacity = 1 - spiralProgress * 0.7;
            return (
              <div
                key={i}
                className="absolute w-3 h-3 rounded-full"
                style={{
                  backgroundColor: SPIRAL_CONFIG.particleColor,
                  transform: `translate(${x}px, ${y}px) scale(${scale})`,
                  opacity,
                  boxShadow: `0 0 8px ${SPIRAL_CONFIG.particleColor}`,
                }}
              />
            );
          })}
        </div>
      )}

      {/* CREATIVE-SPECTACLE: Honey burst on impact */}
      {impactProgress > 0 && impactProgress < 1 && (
        <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
          {Array.from({ length: 16 }).map((_, i) => {
            const angle = (i / 16) * Math.PI * 2;
            const distance = impactProgress * 120;
            const x = Math.cos(angle) * distance;
            const y = Math.sin(angle) * distance + SPIRAL_CONFIG.descentDistance;
            const opacity = 1 - impactProgress;
            return (
              <div
                key={i}
                className="absolute w-2 h-2 rounded-full"
                style={{
                  backgroundColor: '#F4A300', // Honey amber
                  transform: `translate(${x}px, ${y}px)`,
                  opacity,
                  boxShadow: '0 0 6px #F4A300',
                }}
              />
            );
          })}
        </div>
      )}

      {/* Content container */}
      <div
        className="absolute inset-0 flex flex-col items-center justify-center pointer-events-auto"
        style={{ opacity: phase === 'flash' ? 0 : 1 }}
      >
        {/* CREATIVE-SPECTACLE: Dignity voice line (respect, not despair) */}
        {voicelineOpacity > 0 && (
          <div
            className="text-center mb-12"
            style={{
              opacity: voicelineOpacity,
              transform: `translateY(${(1 - voicelineOpacity) * 20}px)`,
            }}
          >
            <div
              className="text-2xl font-serif italic"
              style={{ color: '#F4A300' }} // Warm amber
            >
              "{voiceLine}"
            </div>
          </div>
        )}

        {/* Main death text - Changed from "KILLED BY" to "WAVE X REACHED" (dignity) */}
        <div
          className="text-center mb-8"
          style={{
            opacity: statsOpacity,
            transform: `scale(${0.9 + statsOpacity * 0.1})`,
          }}
        >
          {/* CREATIVE-SPECTACLE: Focus on achievement, not failure */}
          <div
            className="text-5xl font-bold mb-3"
            style={{ color: COLORS.xp }} // Golden, not red
          >
            WAVE {death.wave} REACHED
          </div>
          {/* A2 (ATTRIBUTION): Show exactly WHAT killed the player */}
          <div
            className="text-2xl font-semibold mb-2"
            style={{ color: '#FF6B6B' }} // Red for killer, distinct from golden wave
          >
            {getDeathCauseText(death).title}
          </div>
          <div className="text-lg text-gray-300">
            {getDeathCauseText(death).description}
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

        {/* V5 WITNESSED: Colony Learnings Section */}
        {colonyLearnings && colonyLearnings.learnings.length > 0 && (
          <div
            className="bg-gray-900/90 rounded-lg border border-amber-800/50 p-5 mb-4 min-w-80 max-w-lg"
            style={{ opacity: statsOpacity, transform: `translateY(${(1 - statsOpacity) * 20}px)` }}
          >
            <div className="text-center mb-3">
              <div className="text-amber-400 text-sm font-bold tracking-wider">
                THE COLONY LEARNED:
              </div>
              <div className="text-gray-500 text-xs mt-1">
                {colonyLearnings.headline}
              </div>
            </div>
            <div className="space-y-2">
              {colonyLearnings.learnings.map((learning, index) => (
                <div
                  key={index}
                  className="flex items-start gap-2 text-sm"
                >
                  <span className="text-amber-500 mt-0.5">
                    {learning.usedAgainst ? '!' : '-'}
                  </span>
                  <span className="text-gray-300">
                    {learning.description}
                    {learning.usedAgainst && (
                      <span className="text-amber-600 text-xs ml-2">
                        (they used this)
                      </span>
                    )}
                  </span>
                </div>
              ))}
            </div>
            {/* V5: Respect, not accusation */}
            {colonyLearnings.adaptationLevel >= 6 && (
              <div className="text-center mt-3 pt-3 border-t border-amber-800/30">
                <div className="text-amber-500/80 text-xs italic">
                  "They earned this. ...Respect."
                </div>
              </div>
            )}
            {/* BALL stats if relevant */}
            {colonyLearnings.ballsEncountered > 0 && (
              <div className="text-center mt-3 pt-3 border-t border-amber-800/30">
                <div className="text-gray-500 text-xs">
                  THE BALL: {colonyLearnings.ballsEscaped}/{colonyLearnings.ballsEncountered} escaped
                </div>
              </div>
            )}
          </div>
        )}

        {/* V5 WITNESSED: Ghost Summary Section */}
        {ghostSummary && ghostSummary.ghostArchetypes.length > 0 && (
          <div
            className="bg-gray-900/90 rounded-lg border border-purple-800/50 p-5 mb-6 min-w-80 max-w-lg"
            style={{ opacity: statsOpacity, transform: `translateY(${(1 - statsOpacity) * 20}px)` }}
          >
            <div className="text-center mb-3">
              <div className="text-purple-400 text-sm font-bold tracking-wider">
                PATHS NOT TAKEN:
              </div>
              <div className="text-gray-500 text-xs mt-1">
                What if you had chosen differently?
              </div>
            </div>
            <div className="space-y-2">
              {ghostSummary.ghostArchetypes.slice(0, 2).map((archId) => {
                const arch = ARCHETYPES[archId];
                return (
                  <div
                    key={archId}
                    className="flex items-center gap-3 text-sm"
                  >
                    <span
                      className="w-3 h-3 rounded-full opacity-50"
                      style={{ backgroundColor: arch.color }}
                    />
                    <span className="text-gray-400">
                      You could have been:{' '}
                      <span className="text-purple-300 font-medium">
                        {arch.name}
                      </span>
                    </span>
                  </div>
                );
              })}
            </div>
            {ghostSummary.pivotMoments > 0 && (
              <div className="text-center mt-3 pt-3 border-t border-purple-800/30">
                <div className="text-purple-400/70 text-xs">
                  {ghostSummary.pivotMoments} pivot moment{ghostSummary.pivotMoments > 1 ? 's' : ''} where your path diverged
                </div>
              </div>
            )}
          </div>
        )}

        {/* Part I: Axiom Guard Report - Four True Axioms Verification */}
        {axiomReport && (
          <div
            className="bg-gray-900/90 rounded-lg border border-cyan-800/50 p-5 mb-6 min-w-80 max-w-lg"
            style={{ opacity: statsOpacity, transform: `translateY(${(1 - statsOpacity) * 20}px)` }}
          >
            <div className="text-center mb-3">
              <div className="text-cyan-400 text-sm font-bold tracking-wider">
                AXIOM VERIFICATION
              </div>
              <div className="text-gray-500 text-xs mt-1">
                Quality Score: {(axiomReport.qualityScore * 100).toFixed(0)}%
              </div>
            </div>

            {/* Axiom status grid */}
            <div className="grid grid-cols-2 gap-2 text-xs">
              {(['A1', 'A2', 'A3', 'A4'] as const).map((axiomId) => {
                const passed = axiomReport.passed.includes(axiomId);
                const violation = axiomReport.violations.find(v => v.axiom === axiomId);
                const axiomNames = {
                  A1: 'AGENCY',
                  A2: 'ATTRIBUTION',
                  A3: 'MASTERY',
                  A4: 'COMPOSITION',
                };

                return (
                  <div
                    key={axiomId}
                    className={`p-2 rounded border ${
                      passed
                        ? 'border-green-800/50 bg-green-900/20'
                        : violation?.severity === 'critical'
                          ? 'border-red-800/50 bg-red-900/20'
                          : 'border-yellow-800/50 bg-yellow-900/20'
                    }`}
                  >
                    <div className="flex items-center gap-1">
                      <span className={passed ? 'text-green-400' : violation?.severity === 'critical' ? 'text-red-400' : 'text-yellow-400'}>
                        {passed ? '[OK]' : violation?.severity === 'critical' ? '[!!]' : '[!]'}
                      </span>
                      <span className="text-gray-300 font-medium">
                        {axiomId}: {axiomNames[axiomId]}
                      </span>
                    </div>
                    {violation && (
                      <div className="text-gray-500 text-[10px] mt-1 leading-tight">
                        {violation.message.replace(`${axiomId} `, '').substring(0, 40)}...
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Skill metrics summary if available */}
            {axiomReport.passed.includes('A3') && (
              <div className="mt-3 pt-3 border-t border-cyan-800/30">
                <div className="text-center text-cyan-400/70 text-xs">
                  Skill metrics verified - mastery observable
                </div>
              </div>
            )}

            {/* Causal chain note if A1 passed */}
            {axiomReport.passed.includes('A1') && axiomReport.passed.includes('A2') && (
              <div className="mt-2 text-center">
                <div className="text-green-400/60 text-[10px]">
                  Death traceable to player decisions
                </div>
              </div>
            )}
          </div>
        )}

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
