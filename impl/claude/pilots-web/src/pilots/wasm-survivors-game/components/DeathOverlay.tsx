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

import { useState, useEffect, useMemo } from 'react';
import type { EnemyType } from '../types';
import { COLORS } from '../systems/juice';
import {
  type WildUpgradeType,
  WILD_UPGRADES,
} from '../systems/wild-upgrades';
import type { ColonyLearning } from '../systems/colony-memory';
import type { AxiomGuardReport } from '../systems/axiom-guards';
import { HornetIcon, SkullIcon, ChartIcon, MaskIcon, GhostIcon, WarningIcon } from './Icons';

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
  ghostUpgrades: WildUpgradeType[];
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
  upgrades: WildUpgradeType[];
  score: number;
  // V5 WITNESSED: Colony learnings and ghost summary
  colonyLearnings?: ColonyLearningSummary;
  ghostSummary?: GhostSummary;
}

interface DeathOverlayProps {
  death: DeathInfo;
  onPlayAgain: () => void;
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

// Random bee facts for the death screen
const BEE_FACTS = [
  'Honeybees can fly up to 15 miles per hour and visit 50-100 flowers in one trip.',
  'A single bee colony can contain up to 60,000 bees in peak summer.',
  'Bees communicate through dance. The "waggle dance" tells others where food is.',
  'Worker bees are all female. Male bees (drones) exist only to mate with the queen.',
  'Bees have five eyes - two compound eyes and three simple eyes on top of their head.',
  'A queen bee can lay up to 2,000 eggs per day during peak season.',
  'Honey never spoils. Edible honey has been found in 3,000-year-old Egyptian tombs.',
  'Bees must visit about 2 million flowers to make one pound of honey.',
  'A bee\'s wings beat 200 times per second, creating their distinctive buzz.',
  'Bees can recognize human faces and remember them for at least two days.',
  'The "hot bee ball" defense can raise temperatures to 117°F, cooking attackers alive.',
  'Honeybees are the only insects that produce food eaten by humans.',
  'A forager bee will fly roughly 500 miles in her lifetime before her wings give out.',
  'Bees have been producing honey for at least 150 million years.',
  'The hexagonal honeycomb is the most efficient shape for storing honey.',
  'Bees can detect bombs and landmines - they\'re trained by the US military.',
  'A bee\'s brain is the size of a sesame seed but can count up to four.',
  'Queen bees can live 3-5 years, while workers live only 6 weeks in summer.',
  'Bees are responsible for pollinating about 1/3 of all food we eat.',
  'When a bee stings, it releases pheromones that signal other bees to attack.',
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
 * Get a descriptive build name from wild upgrades.
 * Wild upgrades are so unique that even one defines a build.
 */
function getBuildName(upgrades: WildUpgradeType[]): string | null {
  if (upgrades.length === 0) return null;

  // With wild upgrades, each one is so distinctive it defines the build
  const primaryUpgrade = upgrades[0];
  const upgrade = WILD_UPGRADES[primaryUpgrade];
  if (!upgrade) return null;

  // If multiple upgrades, note the combination
  if (upgrades.length > 1) {
    return `${upgrade.name} + ${upgrades.length - 1} more`;
  }

  return upgrade.name;
}

/**
 * DD-18 + CREATIVE-IDENTITY: Death narrative generation.
 *
 * The hornet doesn't "fall" or "lose" - they complete their arc with dignity.
 * Dark humor and swagger, not despair or regret.
 */
function generateDeathNarrative(death: DeathInfo): string {
  const buildName = getBuildName(death.upgrades);

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

// =============================================================================
// Component
// =============================================================================

export function DeathOverlay({
  death,
  onPlayAgain,
  colonyLearnings: colonyLearningsProp,
  ghostSummary: ghostSummaryProp,
}: DeathOverlayProps) {
  const [phase, setPhase] = useState<Phase>('flash');
  const [elapsed, setElapsed] = useState(0);
  const [showDetails, setShowDetails] = useState(false);

  // CREATIVE-SPECTACLE: Select a random dignity voice line
  const voiceLine = useMemo(() => {
    return DIGNITY_VOICE_LINES[Math.floor(Math.random() * DIGNITY_VOICE_LINES.length)];
  }, []);

  // Select a random bee fact
  const beeFact = useMemo(() => {
    return BEE_FACTS[Math.floor(Math.random() * BEE_FACTS.length)];
  }, []);

  // DD-18: Get narrative and build
  const narrative = generateDeathNarrative(death);
  const buildName = getBuildName(death.upgrades);

  // V5 WITNESSED: Compute ghost summary - prop takes precedence, then death.ghostSummary
  const ghostSummary = useMemo(() => {
    if (ghostSummaryProp) return ghostSummaryProp;
    if (death.ghostSummary) return death.ghostSummary;
    return null;
  }, [ghostSummaryProp, death.ghostSummary]);

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
  // Allow restart hotkeys after 'rest' phase (don't require waiting for full animation)
  // Details view toggles with 'D' key
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      // Allow restart keys after rest phase (~1.5s into death sequence)
      // This lets players restart faster without skipping the dignity moment
      const canRestart = ['rest', 'voiceline', 'stats', 'done'].includes(phase);
      const canViewDetails = phase === 'done';

      switch (e.key.toLowerCase()) {
        case 'r':
        case ' ':
        case 'enter':
          if (canRestart && !showDetails) {
            e.preventDefault();
            onPlayAgain();
          }
          break;
        case 'd':
          if (canViewDetails) {
            setShowDetails(prev => !prev);
          }
          break;
        case 'escape':
          if (showDetails) {
            setShowDetails(false);
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [phase, onPlayAgain, showDetails]);

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
            className="text-center mb-4"
            style={{
              opacity: voicelineOpacity,
              transform: `translateY(${(1 - voicelineOpacity) * 10}px)`,
            }}
          >
            <div
              className="text-lg font-serif italic"
              style={{ color: '#F4A300' }} // Warm amber
            >
              "{voiceLine}"
            </div>
          </div>
        )}

        {/* Main death text - Changed from "KILLED BY" to "WAVE X REACHED" (dignity) */}
        <div
          className="text-center mb-4"
          style={{
            opacity: statsOpacity,
            transform: `scale(${0.95 + statsOpacity * 0.05})`,
          }}
        >
          {/* CREATIVE-SPECTACLE: Focus on achievement, not failure */}
          <div
            className="text-3xl font-bold mb-1"
            style={{ color: COLORS.xp }} // Golden, not red
          >
            WAVE {death.wave} REACHED
          </div>
          {/* A2 (ATTRIBUTION): Show exactly WHAT killed the player */}
          <div
            className="text-lg font-semibold mb-1"
            style={{ color: '#FF6B6B' }} // Red for killer, distinct from golden wave
          >
            {getDeathCauseText(death).title}
          </div>
          <div className="text-sm text-gray-300">
            {getDeathCauseText(death).description}
          </div>
        </div>

        {/* Stats card - compact honeycomb aesthetic */}
        <div
          className="bg-gradient-to-b from-gray-900/95 to-gray-950/95 rounded-xl border border-amber-800/30 p-4 mb-4 min-w-72 max-w-md shadow-xl shadow-amber-900/20 backdrop-blur-sm"
          style={{ opacity: statsOpacity, transform: `translateY(${(1 - statsOpacity) * 10}px)` }}
        >
          {/* Stats grid - compact 4-column layout */}
          <div className="grid grid-cols-4 gap-2 text-center mb-3">
            <div className="bg-amber-950/30 rounded-lg p-2 border border-amber-800/20">
              <div className="text-amber-600/80 text-[10px] font-semibold tracking-wider">WAVE</div>
              <div className="text-xl font-bold" style={{ color: COLORS.player }}>
                {death.wave}
              </div>
            </div>
            <div className="bg-amber-950/30 rounded-lg p-2 border border-amber-800/20">
              <div className="text-amber-600/80 text-[10px] font-semibold tracking-wider">TIME</div>
              <div className="text-xl font-bold" style={{ color: COLORS.health }}>
                {timeString}
              </div>
            </div>
            <div className="bg-amber-950/30 rounded-lg p-2 border border-amber-800/20">
              <div className="text-amber-600/80 text-[10px] font-semibold tracking-wider">KILLS</div>
              <div className="text-xl font-bold" style={{ color: COLORS.xp }}>
                {death.totalKills}
              </div>
            </div>
            <div className="bg-amber-950/30 rounded-lg p-2 border border-amber-800/20">
              <div className="text-amber-600/80 text-[10px] font-semibold tracking-wider">SCORE</div>
              <div className="text-xl font-bold text-amber-100">
                {death.score}
              </div>
            </div>
          </div>

          {/* Build identity - compact */}
          {buildName && (
            <div className="border-t border-amber-800/20 pt-2 mt-2 text-center">
              <div className="text-amber-600/70 text-[10px] font-semibold tracking-wider">BUILD: <span className="text-amber-300 font-bold text-xs">{buildName}</span></div>
              <div className="text-[10px] text-amber-700/60 mt-0.5">
                {death.upgrades.join(' • ')}
              </div>
            </div>
          )}

          {/* Narrative - compact */}
          <div className="border-t border-amber-800/20 pt-2 mt-2">
            <div className="text-amber-200/70 italic text-center text-xs leading-relaxed">
              "{narrative}"
            </div>
          </div>
        </div>

        {/* Bee Fact - compact panel */}
        <div
          className="bg-gradient-to-b from-amber-950/60 to-amber-900/40 rounded-lg border border-amber-700/30 p-3 mb-4 max-w-sm backdrop-blur-sm"
          style={{ opacity: statsOpacity, transform: `translateY(${(1 - statsOpacity) * 15}px)` }}
        >
          <div className="flex items-start gap-2">
            <HornetIcon size={20} color="#FBBF24" />
            <div>
              <div className="text-amber-300/80 text-[10px] font-semibold tracking-wider mb-1">
                DID YOU KNOW?
              </div>
              <div className="text-amber-100/90 text-xs leading-snug">
                {beeFact}
              </div>
            </div>
          </div>
        </div>

        {/* Action buttons - compact styling */}
        <div
          className="flex gap-3 flex-wrap justify-center"
          style={{ opacity: statsOpacity }}
        >
          <button
            onClick={onPlayAgain}
            className="px-5 py-2 rounded-lg font-bold text-sm transition-all duration-200 hover:scale-105 hover:shadow-lg hover:shadow-amber-500/20 border border-amber-500/50"
            style={{ backgroundColor: COLORS.player, color: '#000' }}
          >
            HUNT AGAIN
          </button>
          <button
            onClick={() => setShowDetails(true)}
            className="px-5 py-2 rounded-lg font-bold text-sm transition-all duration-200 hover:scale-105 hover:shadow-lg hover:shadow-amber-400/10 bg-gradient-to-b from-gray-800/80 to-gray-900/90 text-gray-200 border border-gray-600/40"
          >
            VIEW DETAILS
          </button>
        </div>

        {/* Compact hint text */}
        <div
          className="absolute bottom-4 text-amber-700/60 text-xs tracking-wide"
          style={{ opacity: statsOpacity * 0.8 }}
        >
          R/SPACE: hunt again • D: details
        </div>
      </div>

      {/* Details Modal - Tree/Outline View */}
      {showDetails && (
        <div
          className="fixed inset-0 z-[60] flex items-center justify-center bg-black/80 backdrop-blur-sm"
          onClick={() => setShowDetails(false)}
        >
          <div
            className="bg-gradient-to-b from-gray-900 to-gray-950 rounded-xl border border-amber-800/40 p-6 max-w-lg w-full mx-4 max-h-[80vh] overflow-y-auto shadow-2xl"
            onClick={e => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-amber-100">Run Details</h2>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowDetails(false);
                }}
                className="w-8 h-8 flex items-center justify-center rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-gray-200 transition-colors text-lg font-bold"
                aria-label="Close details"
              >
                ✕
              </button>
            </div>

            {/* Tree View */}
            <div className="space-y-4 font-mono text-sm">

              {/* Run Overview */}
              <div className="space-y-1">
                <div className="text-amber-400 font-bold flex items-center gap-2">
                  <ChartIcon size={16} color="#FBBF24" />
                  RUN OVERVIEW
                </div>
                <div className="pl-4 border-l-2 border-amber-800/30 space-y-0.5">
                  <div className="text-gray-300">├─ Wave: <span className="text-amber-200">{death.wave}</span></div>
                  <div className="text-gray-300">├─ Time: <span className="text-amber-200">{timeString}</span></div>
                  <div className="text-gray-300">├─ Kills: <span className="text-amber-200">{death.totalKills}</span></div>
                  <div className="text-gray-300">└─ Score: <span className="text-amber-200">{death.score}</span></div>
                </div>
              </div>

              {/* Build Identity */}
              {buildName && (
                <div className="space-y-1">
                  <div className="text-purple-400 font-bold flex items-center gap-2">
                    <MaskIcon size={16} color="#C084FC" />
                    BUILD IDENTITY
                  </div>
                  <div className="pl-4 border-l-2 border-purple-800/30 space-y-0.5">
                    <div className="text-gray-300">├─ Archetype: <span className="text-purple-200">{buildName}</span></div>
                    <div className="text-gray-300">└─ Upgrades:</div>
                    <div className="pl-4 space-y-0.5">
                      {death.upgrades.map((upgrade, i) => (
                        <div key={i} className="text-gray-400">
                          {i === death.upgrades.length - 1 ? '└─' : '├─'} {upgrade}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Death Cause */}
              <div className="space-y-1">
                <div className="text-red-400 font-bold flex items-center gap-2">
                  <SkullIcon size={16} color="#F87171" />
                  CAUSE OF DEATH
                </div>
                <div className="pl-4 border-l-2 border-red-800/30 space-y-0.5">
                  <div className="text-gray-300">├─ Enemy: <span className="text-red-200">{ENEMY_NAMES[death.killerType]}</span></div>
                  {death.attackType && death.attackType !== 'contact' && (
                    <div className="text-gray-300">├─ Attack: <span className="text-red-200">{ATTACK_NAMES[death.attackType]}</span></div>
                  )}
                  <div className="text-gray-300">├─ Damage: <span className="text-red-200">{death.damageDealt}</span></div>
                  <div className="text-gray-300">└─ Health: <span className="text-red-200">{death.healthBefore} → 0</span></div>
                </div>
              </div>

              {/* Ghost Paths - Paths Not Taken */}
              {ghostSummary && ghostSummary.ghostUpgrades.length > 0 && (
                <div className="space-y-1">
                  <div className="text-cyan-400 font-bold flex items-center gap-2">
                    <GhostIcon size={16} color="#22D3EE" />
                    PATHS NOT TAKEN
                  </div>
                  <div className="pl-4 border-l-2 border-cyan-800/30 space-y-0.5">
                    {ghostSummary.ghostUpgrades.map((upgradeId, i) => {
                      const upgrade = WILD_UPGRADES[upgradeId];
                      const isLast = i === ghostSummary.ghostUpgrades.length - 1;
                      if (!upgrade) return null;
                      return (
                        <div key={upgradeId} className="text-gray-300">
                          {isLast ? '└─' : '├─'}{' '}
                          <span
                            className="inline-block w-2 h-2 rounded-full mr-1.5"
                            style={{ backgroundColor: '#22D3EE' }}
                          />
                          <span style={{ color: '#22D3EE' }}>{upgrade.name}</span>
                          <span className="text-gray-500 text-xs ml-2">— {upgrade.tagline}</span>
                        </div>
                      );
                    })}
                    {ghostSummary.pivotMoments > 0 && (
                      <div className="text-cyan-600/70 text-xs mt-2 italic">
                        {ghostSummary.pivotMoments} pivot moment{ghostSummary.pivotMoments > 1 ? 's' : ''} where your path diverged
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Colony Learnings */}
              {colonyLearnings && colonyLearnings.learnings.length > 0 && (
                <div className="space-y-1">
                  <div className="text-amber-400 font-bold flex items-center gap-2">
                    <HornetIcon size={16} color="#FBBF24" />
                    COLONY LEARNINGS
                  </div>
                  <div className="pl-4 border-l-2 border-amber-800/30 space-y-0.5">
                    {colonyLearnings.learnings.map((learning, i) => {
                      const isLast = i === colonyLearnings.learnings.length - 1;
                      return (
                        <div key={i} className="text-gray-300">
                          {isLast ? '└─' : '├─'}{' '}
                          {learning.usedAgainst && <WarningIcon size={12} color="#F59E0B" className="inline-block mr-1" />}
                          {learning.description}
                        </div>
                      );
                    })}
                    {colonyLearnings.adaptationLevel >= 6 && (
                      <div className="text-amber-500/70 text-xs mt-2 italic">
                        "They earned this. ...Respect."
                      </div>
                    )}
                  </div>
                </div>
              )}


            </div>

            {/* Close Button */}
            <div className="mt-6 pt-4 border-t border-gray-800 flex justify-center">
              <button
                onClick={() => setShowDetails(false)}
                className="px-6 py-2 rounded-lg font-bold text-sm bg-gray-800 hover:bg-gray-700 text-gray-200 transition-colors"
              >
                CLOSE
              </button>
            </div>

            {/* Hint */}
            <div className="text-center mt-3 text-gray-600 text-xs">
              Press ESC or click outside to close
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DeathOverlay;
