/**
 * WASM Survivors - Core Game Loop Hook
 *
 * 16ms frame budget (60 FPS target):
 * - Input: < 1ms
 * - Physics: < 5ms
 * - Collision: < 3ms
 * - Render: < 7ms (handled by React/Canvas)
 *
 * @see pilots/wasm-survivors-game/.outline.md
 */

import { useRef, useEffect, useCallback } from 'react';
import type { GameState, Enemy } from '../types';
import { updatePhysics, checkCollisions } from '../systems/physics';

// InputState interface for this module - matches types.ts InputState with extensions
// Note: The fields use `up`/`down`/`left`/`right` to match the types.ts definition
// Extended with dash support (DD-10) and Apex Strike support
interface InputState {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
  // Dash support (DD-10)
  dashPressed?: boolean;
  dashConsumed?: boolean;
  // Apex Strike support
  spaceDown?: boolean;           // Is space currently held?
  spaceJustPressed?: boolean;    // Did space just go down this frame?
  spaceJustReleased?: boolean;   // Did space just come up this frame?
  spaceHoldDuration?: number;    // How long has space been held (ms)
  aimDirection?: { x: number; y: number }; // Current WASD aim direction
}
import { updateSpawner, type SpawnResult } from '../systems/spawn';
import { processJuice, type JuiceSystem, checkClutchMoment, getEffectiveTimeScale } from '../systems/juice';
import { emitWitnessMark, type WitnessContext } from '../systems/witness';
import { type ActiveUpgrades } from '../systems/upgrades';
// STUB: Metamorphosis system removed in bee theme migration
// Legacy colossal_tide mechanic is NOT part of bee theme
type MetamorphosisResult = {
  enemies: Enemy[];
  isFirstMetamorphosis: boolean;
};
function updateMetamorphosis(
  enemies: Enemy[],
  _deltaSeconds: number,
  _hasWitnessed: boolean
): MetamorphosisResult {
  return { enemies, isFirstMetamorphosis: false };
}

// THE BALL Formation System (the CORE mechanic!)
import {
  createBallState,
  forceBallStart,
  createBallManagerState,
  updateBallManager,
  type BallState,
  type BallUpdateResult,
  type FormationEvent,
  type BallManagerState,
} from '../systems/formation';
import {
  updateCombatSystem,
  createInitialCombatState,
  isHoverBrakeInvulnerable,
  startDash,
  endDash,
  spawnAfterimage,
  type PlayerCombatState,
  type EnemyWithCombat,
  type CombatEvent,
  // Venom Architect system
  type VenomArchitectState,
  applyVenomArchitectStack,
  updateVenomArchitectState,
  calculateVenomArchitectExplosionDamage,
  VENOM_ARCHITECT,
} from '../systems/combat';
import {
  updateEmotionalState,
  createEmotionalState,
  triggerVoiceLine,
  recordArcClosure,
  type EmotionalState,
  type EmotionalEvent,
  type VoiceLine,
  type ArcPhase,
} from '../systems/contrast';
import {
  createGuardianState,
  // recordPlayerDecision, // TODO: Use when upgrade selection is tracked
  recordAttackEncounter,
  recordDamageDealt,
  recordDamageReceived,
  // recordArcPhase, // TODO: Use when arc phase transitions are tracked
  buildSkillMetrics,
  buildArcHistory,
  buildDeathContext,
  runAxiomGuards,
  logAxiomReport,
  type AxiomGuardianState,
  type AxiomGuardReport,
} from '../systems/axiom-guards';
import {
  createColonyIntelligence,
  updateColonyIntelligence,
  onEnemyKill,
  getBeeIntelligence,
  type ColonyIntelligence,
  type ColonyEvent,
} from '../systems/colony-intelligence';
import { ARENA_WIDTH, ARENA_HEIGHT, type Enemy as LocalEnemy } from '../types';
import { PerformanceMonitor, type PerformanceMetrics } from '../systems/performance';
import {
  type ActiveAbilities,
  createInitialAbilities,
  addAbility,
  generateAbilityChoices,
  recordKillForTrophyScent,
  incrementSawtoothCounter,
  resetRuntimeForWave,
  type AbilityId,
  // Movement Trail System (Run 043: thermal_wake, rally_scent, draft)
  type TrailPoint,
  processMovementTrail,
  // Passive Aura System (Run 043: hover_pressure, buzz_field, barbed_chitin, threat_aura)
  processPassiveAuras,
  type AuraResult,
  // On-Kill Ability System (Run 044: territorial_mark, death_marker, clean_kill, pack_signal, etc.)
  type TerritorialMark,
  type DeathMarker,
  processOnKill,
  expireZones,
  getDeathMarkerSlow,
  getTerritorialMarkBonus,
  isNearCorpse,
  // On-Damaged/Threshold/Periodic Ability System (Run 045)
  processOnDamaged,
  processThresholds,
  processPeriodicEffects,
  checkConfusionCloudMiss,
  cleanupExpiredEffects,
  getBitterTasteDebuff,
  getThreatAuraReduction,
  // Apex Strike PREDATOR ability integration (Run 048)
  computeAbilityEffects,
  type ComputedEffects,
} from '../systems/abilities';
import {
  type MeleeAttackState,
  createInitialMeleeState,
  canAttack,
  startAttack,
  updateMeleeAttack,
  getModifiedConfig,
  MANDIBLE_REAVER_CONFIG,
  type MeleeEvent,
} from '../systems/melee';
import {
  type ComboState,
  createInitialComboState,
  checkForCombos,
  applyComboDiscovery,
  trackAbilityOrder,
  type Combo,
} from '../systems/combos';
// Apex Strike - The hornet's signature predator dash
// "The hornet doesn't dash - it HUNTS. The strike is commitment."
import {
  type ApexStrikeState,
  type ApexEvent,
  type ApexTarget,
  createInitialApexState,
  canApex,
  canChain,
  initiateLock,
  updateLockDirection,
  updateCharge,
  executeStrike,
  checkStrikeHit,
  attemptChain,
  updateApexStrike,
  isStriking,
  isLocking,
  APEX_CONFIG,
} from '../systems/apex-strike';

// Run 039: Bumper-Rail Combo System
// "Bees are not obstacles. Bees are terrain."
import {
  type RailChainState,
  type FlowState,
  createInitialRailChainState,
  createInitialFlowState,
  processBumperHit,
  hasChainTimedOut,
  resetChainState,
  resetFlowState,
  updateBumperState,
} from '../systems/bumper-rail';

// =============================================================================
// Constants
// =============================================================================

const TARGET_FRAME_TIME = 16; // ~60 FPS
const MAX_FRAME_TIME = 100; // Cap delta to prevent spiral of death

// =============================================================================
// Types
// =============================================================================

export interface GameLoopCallbacks {
  onStateUpdate: (state: GameState) => void;
  onGameOver: (finalState: GameState, axiomReport?: AxiomGuardReport) => void;
  onLevelUp: (state: GameState, choices: string[]) => void;
  onWaveComplete: (wave: number) => void;
  // Sound callbacks (DD-5, Run 036: ASMR Audio Transformation)
  onEnemyKilled?: (
    enemyType: import('../types').EnemyType,
    tier: import('../types').KillTier,
    comboCount: number,
    position: import('../types').Vector2
  ) => void;
  onPlayerDamaged?: (damage: number) => void;
  // Run 036: Graze sound callback
  onGraze?: (chainCount: number) => void;
  // DD-21: Telegraph callbacks for rendering
  onTelegraphsUpdate?: (telegraphs: import('../systems/enemies').TelegraphData[]) => void;
  // Combat system callbacks (Appendix D)
  onCombatEvent?: (event: CombatEvent) => void;
  onCombatStateUpdate?: (state: PlayerCombatState) => void;
  // Contrast system callbacks (Part VI: Arc Grammar)
  onEmotionalEvent?: (event: EmotionalEvent) => void;
  onVoiceLine?: (line: VoiceLine) => void;
  onPhaseTransition?: (phase: ArcPhase) => void;
  onEmotionalStateUpdate?: (state: EmotionalState) => void;
  // Colony Intelligence callbacks (Part XI Phase 4)
  onColonyEvent?: (event: ColonyEvent) => void;
  onColonyIntelligenceUpdate?: (intelligence: ColonyIntelligence) => void;
  // THE BALL Formation callbacks (Run 036: The signature mechanic!)
  onBallEvent?: (event: FormationEvent) => void;
  onBallStateUpdate?: (state: BallState) => void;
  // Performance monitoring callbacks (Run 036)
  onPerformanceMetrics?: (metrics: PerformanceMetrics) => void;
  // Melee/Abilities/Combos callbacks (Run 036: Ability system integration)
  onMeleeEvent?: (event: MeleeEvent) => void;
  onMeleeStateUpdate?: (state: MeleeAttackState) => void;
  onAbilitiesUpdate?: (abilities: ActiveAbilities) => void;
  onComboDiscovered?: (combo: Combo) => void;
  onComboStateUpdate?: (state: ComboState) => void;
  // Apex Strike callbacks (Run 036: The hornet's predator dash)
  onApexEvent?: (event: ApexEvent) => void;
  onApexStateUpdate?: (state: ApexStrikeState) => void;
}

export interface GameLoopControls {
  start: () => void;
  stop: () => void;
  pause: () => void;
  resume: () => void;
  reset: () => void;
  setState: (state: GameState) => void;
  isRunning: boolean;
  // THE BALL debug controls (Run 036)
  forceBall: () => void;
  getBallState: () => BallState;
  getAllBalls: () => BallState[];  // Run 042: Multi-ball rendering
  // Abilities/Combos controls (Run 036)
  selectAbility: (abilityId: AbilityId) => void;
  getAbilities: () => ActiveAbilities;
  getComboState: () => ComboState;
  getMeleeState: () => MeleeAttackState;
  // Apex Strike controls (Run 036: The hornet's predator dash)
  getApexState: () => ApexStrikeState;
  // Attack speed visualization (Run 039)
  getAttackCooldownPercent: () => number;
  getKillStreak: () => number;
  isDoubleStrikeReady: () => boolean;
  // Ability zones (territorial marks, death markers)
  getTerritorialMarks: () => TerritorialMark[];
  getDeathMarkers: () => DeathMarker[];
}

// =============================================================================
// Hook
// =============================================================================

export function useGameLoop(
  initialState: GameState,
  inputRef: React.RefObject<InputState>,
  callbacks: GameLoopCallbacks,
  juiceSystem: JuiceSystem
): GameLoopControls {
  const stateRef = useRef<GameState>(initialState);
  const animationFrameRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number>(0);
  const isRunningRef = useRef<boolean>(false);
  const isPausedRef = useRef<boolean>(false);
  const witnessContextRef = useRef<WitnessContext>({
    runId: `run-${Date.now()}`,
    marks: [],
    ghosts: [],
    startTime: Date.now(),
    pendingIntents: new Map(),
  });

  // Combat system state (Appendix D mechanics)
  const combatStateRef = useRef<PlayerCombatState>(createInitialCombatState());
  const wasDashingRef = useRef<boolean>(false);

  // Emotional state (Part VI: Arc Grammar, Seven Contrasts)
  const emotionalStateRef = useRef<EmotionalState>(createEmotionalState());

  // Axiom Guardian state (Part I: The Axiom Layer - Four True Axioms)
  const axiomGuardianRef = useRef<AxiomGuardianState>(createGuardianState());

  // Performance monitoring (Run 036: 60fps with per-system timing)
  const perfMonitorRef = useRef<PerformanceMonitor>(new PerformanceMonitor());

  // Colony Intelligence state (Part XI Phase 4: The Superorganism)
  // "They learned my patterns. They EARNED this kill."
  const colonyIntelligenceRef = useRef<ColonyIntelligence | null>(null);
  const dashStartPositionRef = useRef<{ x: number; y: number } | null>(null);

  // THE BALL Formation state (Run 036: The signature mechanic!)
  // "When they form THE BALL, you WILL feel it."
  const ballStateRef = useRef<BallState>(createBallState());
  // RUN 041: Ball manager for multi-ball and bee cooldowns
  const ballManagerRef = useRef<BallManagerState>(createBallManagerState());

  // Abilities/Melee/Combos state (Run 036: Ability system integration)
  // "The hornet doesn't shoot - it STRIKES. The mandibles are the weapon."
  const abilitiesRef = useRef<ActiveAbilities>(createInitialAbilities());
  const meleeStateRef = useRef<MeleeAttackState>(createInitialMeleeState());
  const comboStateRef = useRef<ComboState>(createInitialComboState());
  const runNumberRef = useRef<number>(1);  // Track run number for combo discovery

  // Attack speed visualization (Run 039: Ability audit)
  const killStreakRef = useRef<number>(0);  // Current momentum kill streak
  const lastKillTimeRef = useRef<number>(0);  // Timestamp of last kill (for momentum timeout)
  const effectiveCooldownRef = useRef<number>(MANDIBLE_REAVER_CONFIG.cooldown);  // Current attack cooldown (ms)

  // Run 044: Lifesteal healing accumulator (applied after hit processing)
  const lifestealHealingRef = useRef<number>(0);

  // Run 044: Regeneration accumulator (tracks fractional HP for per-second healing)
  const regenAccumulatorRef = useRef<number>(0);

  // Second Wind revive tracking - only triggers once per run
  // Note: Second Wind ability removed in bee theme, ref kept for potential future re-implementation
  const reviveUsedRef = useRef<boolean>(false);
  // Touch ref to avoid unused error (feature disabled but may return)
  void reviveUsedRef;

  // Run 040: Double Strike pre-roll - tracks if next attack will be a double strike
  const nextAttackDoubleStrikeRef = useRef<boolean>(false);

  // Apex Strike state (Run 036: The hornet's signature predator dash)
  // "The hornet doesn't dash - it HUNTS. The strike is commitment."
  const apexStrikeRef = useRef<ApexStrikeState>(createInitialApexState());

  // Run 039: Bumper-Rail Combo System
  // "Bees are not obstacles. Bees are terrain."
  const railChainRef = useRef<RailChainState>(createInitialRailChainState());
  const flowStateRef = useRef<FlowState>(createInitialFlowState());
  // Active bumper boost - applied to velocity during strike
  const bumperBoostRef = useRef<{
    speedMultiplier: number;
    directionNudge: { x: number; y: number };
  }>({ speedMultiplier: 1.0, directionNudge: { x: 0, y: 0 } });

  // Venom Architect state (Special Ability: Infinite venom stacks, explode on venom-kill)
  // Map of enemyId -> VenomArchitectState
  const venomArchitectRef = useRef<Map<string, VenomArchitectState>>(new Map());

  // On-Kill Ability Zones (Run 044: territorial_mark, death_marker, etc.)
  // "Where enemies die, the ground remembers."
  const territorialMarksRef = useRef<TerritorialMark[]>([]);
  const deathMarkersRef = useRef<DeathMarker[]>([]);
  // Enemy hesitation timers (pack_signal ability)
  // Map of enemyId -> hesitation end time
  const enemyHesitationRef = useRef<Map<string, number>>(new Map());

  // GRAZE FRENZY state (Run 042: Near-miss stacking mechanic)
  // "Risk is rewarded. Each graze = +5% attack speed, +3% damage. Max 20 stacks. Getting hit resets ALL."
  const grazeFrenzyRef = useRef<{
    stacks: number;
    lastGrazeTime: number;
    grazedEnemyIds: Map<string, number>;  // Track which enemies have been grazed and when (prevent spam)
  }>({
    stacks: 0,
    lastGrazeTime: 0,
    grazedEnemyIds: new Map(),
  });

  // Graze Frenzy constants (TODO: Wire up when graze_frenzy ability is implemented)
  const _GRAZE_FRENZY = {
    NEAR_MISS_DISTANCE: 10,      // Pixels - attack must pass within this distance WITHOUT hitting
    ATTACK_SPEED_PER_STACK: 0.05, // +5% attack speed per stack
    DAMAGE_PER_STACK: 0.03,       // +3% damage per stack
    MAX_STACKS: 20,               // Maximum stacks
    DECAY_RATE: 1,                // Stacks lost per second if not grazing
    GRAZE_COOLDOWN: 500,          // ms - cooldown per enemy before they can grant another stack
  };
  void _GRAZE_FRENZY; // Suppresses unused variable warning - will be used when graze_frenzy is implemented

  // THERMAL MOMENTUM state (Run 042: Movement-based heat mechanic)
  // "Build heat while moving. Stop to release a damage pulse."
  const thermalMomentumRef = useRef<{
    currentHeat: number;           // Current heat level (0-100)
    lastPosition: { x: number; y: number } | null;  // Last frame position for distance calculation
    stoppedTime: number;           // Timestamp when player stopped (for release window)
    hasReleased: boolean;          // Whether heat was released this stop
  }>({
    currentHeat: 0,
    lastPosition: null,
    stoppedTime: 0,
    hasReleased: false,
  });

  // Thermal Momentum constants
  const THERMAL_MOMENTUM = {
    HEAT_PER_PIXEL: 1 / 20,        // 1 heat per 20 pixels traveled
    MAX_HEAT: 100,                  // Heat cap
    DAMAGE_PER_HEAT: 2,             // Damage = heat × 2
    PULSE_RADIUS: 80,               // Damage pulse radius in pixels
    RELEASE_WINDOW: 300,            // ms - window to get value from heat on stop
    DECAY_RATE: 300,                // Heat decay per second after release window
    VELOCITY_THRESHOLD: 5,          // Velocity magnitude below this = "stopped"
  };

  // MOVEMENT TRAIL state (Run 043: thermal_wake, rally_scent, draft)
  // "Your path becomes a weapon. Where you've been slows and pulls enemies."
  const playerTrailRef = useRef<TrailPoint[]>([]);
  const lastTrailRecordRef = useRef<number>(0);
  const TRAIL_RECORD_INTERVAL = 50;  // Record position every 50ms
  const TRAIL_DURATION = 2000;        // Trail persists for 2 seconds

  // PASSIVE AURA state (Run 043: hover_pressure, buzz_field, barbed_chitin, threat_aura)
  // Tracks how long player has been stationary for buzz_field ability
  const stationaryTimeRef = useRef<number>(0);
  const STATIONARY_VELOCITY_THRESHOLD = 5; // Velocity magnitude below this = "stationary"

  // Core game tick - processes one frame
  const tick = useCallback(
    (currentTime: number) => {
      if (!isRunningRef.current || isPausedRef.current) {
        animationFrameRef.current = requestAnimationFrame(tick);
        return;
      }

      // Calculate delta time
      const rawDeltaTime = lastTimeRef.current
        ? Math.min(currentTime - lastTimeRef.current, MAX_FRAME_TIME)
        : TARGET_FRAME_TIME;
      lastTimeRef.current = currentTime;

      // DD-16: Apply clutch moment time scale (slow motion during clutch)
      const timeScale = getEffectiveTimeScale(juiceSystem);
      const deltaTime = rawDeltaTime * timeScale;

      const state = stateRef.current;
      const input = inputRef.current;

      // Skip if in non-playing state
      if (state.status !== 'playing') {
        animationFrameRef.current = requestAnimationFrame(tick);
        return;
      }

      // Start performance frame timing
      const perfMonitor = perfMonitorRef.current;
      perfMonitor.beginFrame();

      // =======================================================================
      // PHASE 1: Input (< 1ms)
      // =======================================================================
      perfMonitor.beginSystem('input');

      // =======================================================================
      // Run 038: Handle knockback animation (player loses control, slides to destination)
      // =======================================================================
      let knockbackHandledState = state;
      const knockbackState = state.player.knockback;

      if (knockbackState) {
        const elapsed = state.gameTime - knockbackState.startTime;
        const progress = Math.min(1, elapsed / knockbackState.duration);

        if (progress >= 1) {
          // Knockback complete - snap to end position and clear state
          knockbackHandledState = {
            ...state,
            player: {
              ...state.player,
              position: { ...knockbackState.endPos },
              knockback: null,
            },
          };
        } else {
          // Knockback in progress - interpolate position with ease-out for "hit and slow" feel
          const easedProgress = 1 - Math.pow(1 - progress, 2);  // Ease-out quad
          const currentX = knockbackState.startPos.x +
            (knockbackState.endPos.x - knockbackState.startPos.x) * easedProgress;
          const currentY = knockbackState.startPos.y +
            (knockbackState.endPos.y - knockbackState.startPos.y) * easedProgress;

          knockbackHandledState = {
            ...state,
            player: {
              ...state.player,
              position: { x: currentX, y: currentY },
            },
          };
        }
      }

      // Player velocity - zero if being knocked back (loss of control)
      const playerVelocity = {
        x: 0,
        y: 0,
      };

      // Only process input if NOT being knocked back
      if (input && !knockbackHandledState.player.knockback) {
        if (input.up) playerVelocity.y -= 1;
        if (input.down) playerVelocity.y += 1;
        if (input.left) playerVelocity.x -= 1;
        if (input.right) playerVelocity.x += 1;

        // Normalize diagonal movement
        const magnitude = Math.sqrt(
          playerVelocity.x * playerVelocity.x + playerVelocity.y * playerVelocity.y
        );
        if (magnitude > 0) {
          // Base move speed
          let effectiveMoveSpeed = knockbackHandledState.player.moveSpeed;

          // Apply updraft speed boost (WING ability: +3% move speed for 1s after kill)
          const abilities = abilitiesRef.current;
          if (abilities.runtime.updraftExpiry > knockbackHandledState.gameTime && abilities.runtime.updraftSpeedBonus > 0) {
            effectiveMoveSpeed *= (1 + abilities.runtime.updraftSpeedBonus / 100);
          }

          // Apply heat_retention speed boost (CHITIN ability: +5% speed when below 50% HP)
          if (abilities.runtime.heatRetentionActive) {
            const computed = computeAbilityEffects(abilities);
            effectiveMoveSpeed *= (1 + computed.heatRetentionSpeedBonus / 100);
          }

          playerVelocity.x = (playerVelocity.x / magnitude) * effectiveMoveSpeed;
          playerVelocity.y = (playerVelocity.y / magnitude) * effectiveMoveSpeed;
        }
      }

      // =======================================================================
      // PHASE 1.5: Legacy Dash (DD-10) - DISABLED, replaced by Apex Strike
      // =======================================================================
      // The old instant dash is replaced by the Apex Strike predator dash.
      // Apex Strike uses: space to lock, WASD to aim, release to strike.
      // This provides more skill expression and "call your shot" gameplay.
      const dashState = knockbackHandledState;
      perfMonitor.endSystem('input');

      // =======================================================================
      // PHASE 1.6: Apex Strike (Run 036: The hornet's predator dash)
      // "The hornet doesn't dash - it HUNTS. The strike is commitment."
      // =======================================================================
      perfMonitor.beginSystem('apex');
      let apexState = dashState;
      let apexVelocity: { x: number; y: number } | null = null;

      // Cast input for Apex Strike fields
      const apexInput = input as {
        spaceJustPressed?: boolean;
        spaceJustReleased?: boolean;
        spaceDown?: boolean;
        spaceHoldDuration?: number;
        aimDirection?: { x: number; y: number };
      } | null;

      // CRITICAL: Capture and immediately clear frame flags to prevent re-triggering
      const spaceJustPressed = apexInput?.spaceJustPressed ?? false;
      const spaceJustReleased = apexInput?.spaceJustReleased ?? false;
      if (apexInput) {
        apexInput.spaceJustPressed = false;
        apexInput.spaceJustReleased = false;
      }

      // Can't apex while being knocked back
      const canDoApex = !dashState.player.knockback;

      if (canDoApex && apexInput) {
        const currentApex = apexStrikeRef.current;
        const aimDir = apexInput.aimDirection || { x: 1, y: 0 };
        // holdDuration tracked internally via updateCharge

        // Handle LOCK initiation (space just pressed while ready)
        if (spaceJustPressed && canApex(currentApex)) {
          const lockResult = initiateLock(
            currentApex,
            aimDir,
            dashState.player.position,
            dashState.gameTime
          );
          apexStrikeRef.current = lockResult.state;

          // Emit lock events
          for (const event of lockResult.events) {
            callbacks.onApexEvent?.(event);
          }

          // Emit lock visual effects
          juiceSystem.emitApexLock?.(dashState.player.position);
        }

        // Handle LOCK direction updates (during lock phase)
        if (isLocking(apexStrikeRef.current)) {
          // Update direction
          const dirResult = updateLockDirection(apexStrikeRef.current, aimDir);
          apexStrikeRef.current = dirResult.state;

          // Update charge level (updates chargeTime and chargeLevel in state)
          apexStrikeRef.current = updateCharge(
            apexStrikeRef.current,
            deltaTime,
            undefined,  // cursorPos - not used currently
            undefined,  // wasdInput - direction already handled above
            APEX_CONFIG
          );

          // Get charge from state (now properly updated)
          const chargePercent = apexStrikeRef.current.chargeLevel;
          const minDistance = APEX_CONFIG.minDistance;
          const maxDistance = APEX_CONFIG.maxDistance;
          const chargedDistance = minDistance + (maxDistance - minDistance) * chargePercent;

          // Update lock visual effects with charge progress
          juiceSystem.updateApexLock?.(dashState.player.position, chargePercent);

          // Handle STRIKE execution (space released)
          if (spaceJustReleased) {
            // Override strike distance based on charge
            const chargedConfig = { ...APEX_CONFIG, strikeDistance: chargedDistance };

            const strikeResult = executeStrike(
              apexStrikeRef.current,
              dashState.player.position,
              aimDir,
              dashState.gameTime,
              chargedConfig
            );
            apexStrikeRef.current = strikeResult.state;

            // Run 039: Reset bumper chain for new dash (fresh combo opportunity)
            railChainRef.current = resetChainState();
            flowStateRef.current = resetFlowState();
            bumperBoostRef.current = { speedMultiplier: 1.0, directionNudge: { x: 0, y: 0 } };
            // Clear hit-during-chain flags on all enemies
            dashState.enemies = dashState.enemies.map(e => ({
              ...e,
              hitDuringCurrentChain: false,
            }));

            // Emit strike events
            for (const event of strikeResult.events) {
              callbacks.onApexEvent?.(event);
            }

            // Emit strike visual effects
            juiceSystem.emitApexStrikeStart?.(
              dashState.player.position,
              aimDir,
              apexStrikeRef.current.bloodlust
            );

            // Trigger scatter_dust ability on dash (WING ability: particles obscure enemy vision)
            const scatterDustComputed = computeAbilityEffects(abilitiesRef.current);
            if (scatterDustComputed.scatterDustEnabled) {
              juiceSystem.emitAbilityJuice?.('scatter_dust', {
                position: dashState.player.position,
                intensity: 1.0
              });
              // Note: Enemy vision obscuring would be handled by the enemy AI system
              // based on proximity to the scatter_dust effect
            }
          }
        }

        // Handle CHAIN attempt (space pressed during chain window)
        if (spaceJustPressed && canChain(apexStrikeRef.current)) {
          const chainResult = attemptChain(
            apexStrikeRef.current,
            aimDir,
            dashState.player.position,
            dashState.gameTime
          );
          apexStrikeRef.current = chainResult.state;

          // Emit chain events
          for (const event of chainResult.events) {
            callbacks.onApexEvent?.(event);
          }
        }

        // Handle STRIKE hit detection (during strike phase)
        if (isStriking(apexStrikeRef.current)) {
          // Convert enemies to ApexTarget format
          const targets: ApexTarget[] = dashState.enemies.map(e => ({
            id: e.id,
            position: e.position,
            radius: e.radius ?? 15,
            health: e.health,
          }));

          const hitResult = checkStrikeHit(
            apexStrikeRef.current,
            dashState.player.position,
            targets,
            dashState.gameTime,
            APEX_CONFIG
          );
          apexStrikeRef.current = hitResult.state;

          // Run 038+039: Process ALL hit enemies (multi-hit + bumper-rail unified)
          if (hitResult.hitEnemies && hitResult.hitEnemies.length > 0) {
            // Emit hit events
            for (const event of hitResult.events) {
              callbacks.onApexEvent?.(event);
            }

            // Emit single hit visual effect
            juiceSystem.emitApexHit?.(
              dashState.player.position,
              hitResult.damage,
              hitResult.state.canChain
            );

            // Run 038: Emit multi-hit effect for 2+ simultaneous hits (freeze frame + circle inversion)
            if (hitResult.hitEnemies.length >= 2 && hitResult.state.multiHitPosition) {
              juiceSystem.emitMultiHit?.(
                hitResult.state.multiHitPosition,
                hitResult.hitEnemies.length,
                dashState.player.position
              );
            }

            // Run 039: Process bumper-rail for each hit enemy
            const dashDirection = apexStrikeRef.current.lockDirection || { x: 1, y: 0 };
            let bumperSpeedBoost = 1.0;
            let bumperDirectionNudge = { x: 0, y: 0 };
            let bumperDamageBonus = 0;
            let chargedBeeDamage = 0;

            for (const hitEnemy of hitResult.hitEnemies) {
              // Find full enemy object
              const fullEnemy = dashState.enemies.find(e => e.id === hitEnemy.id);
              if (!fullEnemy) continue;


              // Track previous flow state for change detection
              const wasFlowActive = flowStateRef.current.active;

              // Process through bumper system
              const bumperResult = processBumperHit(
                fullEnemy,
                railChainRef.current,
                flowStateRef.current,
                dashState.player.position,
                dashDirection,
                dashState.enemies,
                dashState.gameTime
              );

              // Update rail chain and flow state
              railChainRef.current = bumperResult.newRailState;
              flowStateRef.current = bumperResult.newFlowState;

              // Emit flow state change juice effect
              if (flowStateRef.current.active !== wasFlowActive) {
                juiceSystem.setFlowState?.(flowStateRef.current.active);
              }

              // Accumulate speed boost and direction nudge
              if (bumperResult.result.speedBoost > 1.0) {
                bumperSpeedBoost *= bumperResult.result.speedBoost;
                // Accumulate direction nudge (last nudge wins, but weighted by chain)
                const nudge = bumperResult.result.directionNudge;
                bumperDirectionNudge.x += nudge.x;
                bumperDirectionNudge.y += nudge.y;
                juiceSystem.emitBumperPing?.(fullEnemy.position, bumperResult.result.comboCount);
              }

              // Track charged bee damage (counterplay!)
              if (bumperResult.result.hitChargedBee) {
                chargedBeeDamage += bumperResult.result.chargedBeeDamage;
                juiceSystem.emitChargedBeeHit?.(fullEnemy.position, bumperResult.result.chargedBeeDamage);
              }

              // Check for chain break
              if (bumperResult.result.chainBroken) {
                const breakReason = bumperResult.result.chainBreakReason === 'charged_bee' ? 'charged' :
                                   bumperResult.result.chainBreakReason === 'guard' ? 'guard' : 'timeout';
                juiceSystem.emitChainBreak?.(fullEnemy.position, breakReason);
                railChainRef.current = resetChainState();
                flowStateRef.current = resetFlowState();
              }

              // Update enemy's bumper state
              const enemyIdx = dashState.enemies.findIndex(e => e.id === hitEnemy.id);
              if (enemyIdx >= 0) {
                dashState.enemies[enemyIdx] = bumperResult.updatedEnemy;
              }
            }

            // Run 039: Store accumulated boost for velocity application
            // This will be applied to the apex velocity after updateApexStrike
            bumperBoostRef.current = {
              speedMultiplier: bumperSpeedBoost,
              directionNudge: bumperDirectionNudge,
            };

            // Run 039 FIX: Apply bumper boost DIRECTLY to apex strike momentum!
            // The boost was being stored in a ref for later, but hitBoostMomentum expires in 120ms
            // so by the time physics phase applies the boost, momentum is gone.
            // This applies boost immediately to the apex strike state.
            if (bumperSpeedBoost > 1.0 && apexStrikeRef.current.hitBoostMomentum > 0) {
              const normalizedNudge = bumperDirectionNudge.x !== 0 || bumperDirectionNudge.y !== 0
                ? {
                    x: bumperDirectionNudge.x / Math.sqrt(bumperDirectionNudge.x ** 2 + bumperDirectionNudge.y ** 2 + 0.001),
                    y: bumperDirectionNudge.y / Math.sqrt(bumperDirectionNudge.x ** 2 + bumperDirectionNudge.y ** 2 + 0.001),
                  }
                : { x: 0, y: 0 };

              // Calculate new direction with nudge (30% influence toward next target)
              let newDirection = apexStrikeRef.current.hitBoostDirection;
              if (newDirection && (normalizedNudge.x !== 0 || normalizedNudge.y !== 0)) {
                const rawX = newDirection.x + normalizedNudge.x * 0.3;
                const rawY = newDirection.y + normalizedNudge.y * 0.3;
                const mag = Math.sqrt(rawX * rawX + rawY * rawY);
                newDirection = mag > 0.01 ? { x: rawX / mag, y: rawY / mag } : newDirection;
              }

              apexStrikeRef.current = {
                ...apexStrikeRef.current,
                // Boost the hit momentum directly (pinball acceleration)
                hitBoostMomentum: apexStrikeRef.current.hitBoostMomentum * bumperSpeedBoost,
                // Extend the boost timer so momentum doesn't expire mid-chain (150ms per chain link)
                hitBoostTimer: Math.min(600, apexStrikeRef.current.hitBoostTimer + 150),
                // Apply normalized direction (steers toward next target)
                hitBoostDirection: newDirection,
              };

              // Reset boost ref since we've applied it directly to momentum
              // This prevents double-boosting in physics phase
              bumperBoostRef.current = { speedMultiplier: 1.0, directionNudge: { x: 0, y: 0 } };
            }

            // Run 039: Emit combo chain visual if chain is active
            if (railChainRef.current.active && railChainRef.current.chainLength >= 2) {
              juiceSystem.emitComboChain?.(
                dashState.player.position,
                railChainRef.current.chainLength,
                flowStateRef.current.active
              );

              // Update rail line visual (lightning trail)
              if (railChainRef.current.hitPositions.length >= 2) {
                juiceSystem.updateRailLine?.(
                  railChainRef.current.hitPositions,
                  flowStateRef.current.active
                );
              }
            }

            // Apply bumper damage bonus from chain/flow
            if (railChainRef.current.active) {
              bumperDamageBonus = railChainRef.current.damageBonus;
            }
            if (flowStateRef.current.active) {
              bumperDamageBonus += (flowStateRef.current.comboMultiplier - 1.0);
            }

            // Apply charged bee damage to player (counterplay consequence!)
            if (chargedBeeDamage > 0) {
              dashState.player.health -= chargedBeeDamage;
              callbacks.onPlayerDamaged?.(chargedBeeDamage);
              // Break chain on taking damage - reset all bumper state
              railChainRef.current = resetChainState();
              flowStateRef.current = resetFlowState();
              bumperBoostRef.current = { speedMultiplier: 1.0, directionNudge: { x: 0, y: 0 } };
              juiceSystem.setFlowState?.(false);
            }

            // A3: Record total damage dealt
            const totalDamage = hitResult.damage * hitResult.hitEnemies.length;
            recordDamageDealt(axiomGuardianRef.current, totalDamage);

            // Apply damage to ALL hit enemies
            let enemiesKilled = 0;
            let xpGained = 0;

            // =======================================================================
            // PREDATOR ABILITY DAMAGE BONUSES (Run 048: Apex Strike Integration)
            // Applies: trophy_scent, territorial_mark, corpse_heat to apex strike
            // =======================================================================
            const playerPos = dashState.player.position;
            const computed = computeAbilityEffects(abilitiesRef.current);

            // 1. Trophy Scent: +1% permanent damage per unique enemy type killed
            // Applied via computed.damageMultiplier (base 1.0 + trophy bonus)
            const trophyScentMultiplier = computed.damageMultiplier;

            // 2. Territorial Mark: +10% damage when attacking in kill zones
            // Check if player is in any active territorial mark zone
            const territorialBonus = getTerritorialMarkBonus(
              playerPos.x,
              playerPos.y,
              territorialMarksRef.current,
              dashState.gameTime
            );
            const territorialMultiplier = 1 + (territorialBonus / 100);

            // 3. Corpse Heat: +5% damage when near recent kills
            // Check if player is near any death marker (corpse location)
            const nearCorpse = isNearCorpse(
              playerPos.x,
              playerPos.y,
              deathMarkersRef.current,
              dashState.gameTime,
              computed.corpseHeatRadius || 20
            );
            const corpseHeatMultiplier = nearCorpse ? 1 + (computed.corpseHeatBonus / 100) : 1;

            // =======================================================================
            // MANDIBLE ABILITY INTEGRATION (Run 049: Apex Strike + Mandible)
            // Applies the 6 MANDIBLE abilities to apex strike damage:
            // - sawtooth: every 5th hit +30% damage (applied to base damage)
            // - chitin_crack: armor reduction per hit (applied per-enemy)
            // - serration: bleed (handled by combat system via computed.bleedEnabled)
            // - scissor_grip: stun chance (applied per-enemy below)
            // - resonant_strike: knockback (applied per-enemy below)
            // - nectar_sense: mark full HP targets (applied per-enemy below)
            // =======================================================================

            // MANDIBLE: Sawtooth - increment counter for EACH hit enemy
            let sawtoothBonusTriggered = false;
            if (computed.sawtoothEveryN > 0) {
              for (let i = 0; i < hitResult.hitEnemies.length; i++) {
                const sawtoothResult = incrementSawtoothCounter(abilitiesRef.current);
                abilitiesRef.current = sawtoothResult.state;
                if (sawtoothResult.isBonusHit) {
                  sawtoothBonusTriggered = true;
                }
              }
            }

            // Apply sawtooth damage bonus if ANY hit triggered it
            const sawtoothMultiplier = sawtoothBonusTriggered
              ? 1 + (computed.sawtoothBonus / 100)
              : 1;

            // Calculate final damage with all PREDATOR + MANDIBLE bonuses
            // Base damage * trophy_scent * territorial_mark * corpse_heat * sawtooth + bumper bonus
            const baseDamageWithAbilities = Math.floor(
              hitResult.damage * trophyScentMultiplier * territorialMultiplier * corpseHeatMultiplier * sawtoothMultiplier
            );
            const baseDamage = baseDamageWithAbilities + bumperDamageBonus;

            apexState = {
              ...dashState,
              enemies: dashState.enemies.map(e => {
                const wasHit = hitResult.hitEnemies.some(he => he.id === e.id);
                if (wasHit) {
                  // =======================================================================
                  // VENOM ABILITY EFFECTS (Run 049: Apex Strike Venom Integration)
                  // melittin_traces: +5% damage to poisoned/slowed enemies
                  // histamine_burst: +8% damage to slowed enemies (jittery = vulnerable)
                  // trace_venom: Apply slow stacks on hit
                  // paralytic_microdose: Chance to freeze on hit
                  // =======================================================================
                  let finalDamage = baseDamage;
                  let updatedEnemy = { ...e };

                  // melittin_traces: +5% damage per stack to enemies with venom-related status
                  // Enemy is considered "poisoned" if they have slowStacks, poisonStacks, or venomArchitectStacks
                  const isPoisoned = (e.slowStacks && e.slowStacks > 0) ||
                                    (e.poisonStacks && e.poisonStacks > 0) ||
                                    (e.venomArchitectStacks && e.venomArchitectStacks > 0);
                  if (computed.poisonedDamageAmp > 0 && isPoisoned) {
                    finalDamage *= (1 + computed.poisonedDamageAmp / 100);
                  }

                  // histamine_burst: +8% damage to slowed enemies
                  // The slow from trace_venom makes enemies "jittery" and vulnerable
                  if (computed.histamineDamageAmp > 0 && e.slowStacks && e.slowStacks > 0) {
                    finalDamage *= (1 + computed.histamineDamageAmp / 100);
                  }

                  // trace_venom: Apply slow stacks on apex strike hit
                  if (computed.slowPerHit > 0) {
                    const currentSlowStacks = updatedEnemy.slowStacks || 0;
                    const newSlowStacks = Math.min(
                      currentSlowStacks + Math.ceil(computed.slowPerHit),
                      computed.slowMaxStacks
                    );
                    updatedEnemy = { ...updatedEnemy, slowStacks: newSlowStacks };
                  }

                  // paralytic_microdose: Roll for freeze on apex strike hit
                  if (computed.freezeChance > 0 && Math.random() < computed.freezeChance) {
                    // Apply freeze by maxing out slow stacks (visual: frozen blue)
                    updatedEnemy = {
                      ...updatedEnemy,
                      slowStacks: computed.slowMaxStacks || 30,
                    };
                    // Emit freeze juice effect
                    juiceSystem.emitAbilityJuice?.('paralytic_microdose', {
                      position: e.position,
                      intensity: 1.0
                    });
                  }

                  // =======================================================================
                  // MANDIBLE ABILITY EFFECTS (Run 049: Apex Strike + Mandible)
                  // Per-enemy effects for the 6 MANDIBLE abilities
                  // =======================================================================

                  // MANDIBLE: Chitin Crack - armor reduction per hit (stacking)
                  // Reduces enemy armor by 5% per hit, increasing damage dealt
                  if (computed.armorReductionPerHit > 0) {
                    const enemyArmor = (updatedEnemy as { armor?: number }).armor ?? 0;
                    const reducedArmor = Math.max(0, enemyArmor - computed.armorReductionPerHit);
                    // Up to 50% more damage on 0 armor
                    const armorDamageBonus = 1 + (1 - reducedArmor / 100) * 0.5;
                    finalDamage *= armorDamageBonus;
                  }

                  // MANDIBLE: Resonant Strike - knockback (5px)
                  // Pushes enemy away from player on hit
                  if (computed.knockbackPx > 0) {
                    const dx = updatedEnemy.position.x - playerPos.x;
                    const dy = updatedEnemy.position.y - playerPos.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist > 0) {
                      const knockbackDir = { x: dx / dist, y: dy / dist };
                      updatedEnemy = {
                        ...updatedEnemy,
                        position: {
                          x: updatedEnemy.position.x + knockbackDir.x * computed.knockbackPx,
                          y: updatedEnemy.position.y + knockbackDir.y * computed.knockbackPx,
                        },
                      };
                    }
                  }

                  // MANDIBLE: Scissor Grip - 10% chance to stun (0.3s)
                  // Holds enemy still briefly on hit
                  if (computed.stunChance > 0 && Math.random() < computed.stunChance) {
                    updatedEnemy = {
                      ...updatedEnemy,
                      stunUntil: dashState.gameTime + computed.stunDuration,
                    } as typeof updatedEnemy & { stunUntil: number };
                    // Emit stun juice effect
                    juiceSystem.emitAbilityJuice?.('scissor_grip', {
                      position: updatedEnemy.position,
                      intensity: 1.0
                    });
                  }

                  // MANDIBLE: Nectar Sense - mark full HP targets for visibility
                  // Full HP enemies become visible through fog
                  if (computed.markFullHpTargets && updatedEnemy.health >= (updatedEnemy.maxHealth ?? updatedEnemy.health)) {
                    updatedEnemy = {
                      ...updatedEnemy,
                      nectarMarked: true,
                    } as typeof updatedEnemy & { nectarMarked: boolean };
                  }

                  // MANDIBLE: Serration - bleed damage
                  // Combat system handles bleed ticks via computed.bleedEnabled
                  // We just need to mark the enemy as bleeding if the ability is active
                  if (computed.bleedEnabled) {
                    updatedEnemy = {
                      ...updatedEnemy,
                      bleeding: true,
                      bleedDuration: computed.bleedDuration,
                      bleedPercent: computed.bleedPercent,
                    } as typeof updatedEnemy & { bleeding: boolean; bleedDuration: number; bleedPercent: number };
                  }

                  finalDamage = Math.floor(finalDamage);
                  const newHealth = updatedEnemy.health - finalDamage;
                  if (newHealth <= 0) {
                    enemiesKilled++;
                    xpGained += e.xpValue ?? 10;  // Grant XP for each kill
                    juiceSystem.emitKill(e.position, e.type);
                    callbacks.onEnemyKilled?.(
                      e.type,
                      hitResult.hitEnemies.length >= 2 ? 'multi' : 'single',
                      hitResult.hitEnemies.length,
                      e.position
                    );
                  }
                  return { ...updatedEnemy, health: newHealth };
                }
                return e;
              }).filter(e => e.health > 0),
              totalEnemiesKilled: dashState.totalEnemiesKilled + enemiesKilled,
              score: dashState.score + xpGained * 10,  // Add score for kills
              player: {
                ...dashState.player,
                xp: dashState.player.xp + xpGained,  // Grant XP to player
              },
            };

            // Check for bloodlust max
            if (hitResult.state.bloodlust >= APEX_CONFIG.bloodlustMax) {
              juiceSystem.emitBloodlustMax?.(dashState.player.position);
            }
          }


          // Emit trail effect during strike
          if (apexStrikeRef.current.lockDirection) {
            juiceSystem.emitApexStrikeTrail?.(
              dashState.player.position,
              apexStrikeRef.current.lockDirection
            );
          }
        }

        // Update apex strike state (timers, cooldowns, bloodlust decay)
        const updateResult = updateApexStrike(
          apexStrikeRef.current,
          deltaTime,
          apexState.player.position,
          apexState.gameTime,
          APEX_CONFIG
        );
        apexStrikeRef.current = updateResult.state;

        // Emit update events
        for (const event of updateResult.events) {
          callbacks.onApexEvent?.(event);

          // Handle miss event
          if (event.type === 'strike_miss') {
            juiceSystem.emitApexMiss?.(apexState.player.position, apexStrikeRef.current.lockDirection || { x: 1, y: 0 });
          }
        }

        // ONLY use velocity from update result - this ensures velocity is null when strike ends
        // The update function returns null velocity when not actively striking
        apexVelocity = updateResult.velocity;
      }

      // Notify listeners of apex state
      callbacks.onApexStateUpdate?.(apexStrikeRef.current);
      perfMonitor.endSystem('apex');

      // =======================================================================
      // PHASE 2: Physics (< 5ms)
      // =======================================================================
      perfMonitor.beginSystem('physics');

      // Determine final velocity based on apex state
      // CRITICAL: Block normal movement during ALL apex phases except 'ready'
      let finalVelocity = { ...playerVelocity };
      const currentApexPhase = apexStrikeRef.current.phase;

      // RUN 042: Check stun state using current state (before newState exists)
      // Note: stunBounce state will be checked again after collision phase when newState is available
      const currentState = stateRef.current;
      const isCurrentlyStunned = currentState.player.stunBounce?.active &&
        currentState.gameTime < (currentState.player.stunBounce?.endTime ?? 0);
      if (isCurrentlyStunned) {
        finalVelocity = { x: 0, y: 0 };
      }
      // During STRIKE or HIT phase: use apex strike velocity exclusively
      if (apexVelocity && (currentApexPhase === 'strike' || currentApexPhase === 'hit')) {
        // Run 039: Apply bumper boost and direction nudge!
        // Speed multiplier makes you go faster through chains
        // Direction nudge steers you toward the next target (pinball/rail effect)
        const boost = bumperBoostRef.current;
        const boostedSpeed = boost.speedMultiplier;
        const nudge = boost.directionNudge;

        // Apply speed boost
        let vx = apexVelocity.x * boostedSpeed;
        let vy = apexVelocity.y * boostedSpeed;

        // Apply direction nudge (blend toward next target)
        if (nudge.x !== 0 || nudge.y !== 0) {
          // Get current velocity magnitude
          const speed = Math.sqrt(vx * vx + vy * vy);
          if (speed > 0) {
            // Normalize current direction
            const dirX = vx / speed;
            const dirY = vy / speed;
            // Apply nudge to direction
            const newDirX = dirX + nudge.x;
            const newDirY = dirY + nudge.y;
            // Renormalize and apply speed
            const newLen = Math.sqrt(newDirX * newDirX + newDirY * newDirY);
            if (newLen > 0) {
              vx = (newDirX / newLen) * speed;
              vy = (newDirY / newLen) * speed;
            }
          }
        }

        finalVelocity = { x: vx, y: vy };

      }
      // During LOCK, HIT, or MISS_RECOVERY phases: player cannot move (zero velocity)
      // This prevents involuntary movement during apex mechanics
      else if (currentApexPhase !== 'ready') {
        finalVelocity = { x: 0, y: 0 };
      }
      // Only 'ready' phase allows normal WASD movement (already in finalVelocity)

      const physicsResult = updatePhysics(apexState, finalVelocity, deltaTime);

      // DD-21: Emit telegraph updates for rendering
      if (physicsResult.telegraphs && physicsResult.telegraphs.length > 0) {
        callbacks.onTelegraphsUpdate?.(physicsResult.telegraphs);
      }

      // Run 039: Update enemy bumper states (charged → recovering → neutral)
      physicsResult.state.enemies = physicsResult.state.enemies.map(enemy =>
        updateBumperState(enemy, deltaTime, physicsResult.state.gameTime)
      );

      // Run 039: Check for bumper chain timeout (silent reset)
      if (railChainRef.current.active && hasChainTimedOut(railChainRef.current, physicsResult.state.gameTime)) {
        railChainRef.current = resetChainState();
        flowStateRef.current = resetFlowState();
        bumperBoostRef.current = { speedMultiplier: 1.0, directionNudge: { x: 0, y: 0 } };
        juiceSystem.setFlowState?.(false);
      }

      // =======================================================================
      // PHASE 2.5: Movement Trail (Run 043: thermal_wake, rally_scent, draft)
      // "Your path becomes a weapon. Where you've been slows and pulls enemies."
      // =======================================================================

      // Record player position for trail every TRAIL_RECORD_INTERVAL ms
      const playerPos = physicsResult.state.player.position;
      if (physicsResult.state.gameTime - lastTrailRecordRef.current >= TRAIL_RECORD_INTERVAL) {
        playerTrailRef.current.push({
          x: playerPos.x,
          y: playerPos.y,
          timestamp: physicsResult.state.gameTime,
        });
        lastTrailRecordRef.current = physicsResult.state.gameTime;

        // Prune old trail points (keep only recent trail within duration)
        playerTrailRef.current = playerTrailRef.current.filter(
          p => physicsResult.state.gameTime - p.timestamp < TRAIL_DURATION
        );

        // =======================================================================
        // SWIFT WINGS TRAIL: Emit cyan trail particles when moving (Run 044)
        // =======================================================================
        const hasSwiftWings = abilitiesRef.current?.owned.includes('swift_wings') ?? false;
        const isMoving = Math.abs(finalVelocity.x) > 0.1 || Math.abs(finalVelocity.y) > 0.1;
        if (hasSwiftWings && isMoving) {
          // Emit cyan wing trail particle behind player
          juiceSystem.emitAbilityJuice?.('swift_wings', {
            position: { x: playerPos.x, y: playerPos.y },
            intensity: 0.7
          });
        }
      }

      // Process trail effects on enemies (slow + pull)
      const trailResult = processMovementTrail(
        abilitiesRef.current,
        playerTrailRef.current,
        physicsResult.state.enemies.map(e => ({
          id: e.id,
          x: e.position.x,
          y: e.position.y,
        })),
        physicsResult.state.gameTime,
        TRAIL_DURATION
      );

      // Apply trail slow to enemies (stored on enemy for physics to use)
      // Apply pull directly to enemy position (immediate displacement)
      physicsResult.state.enemies = physicsResult.state.enemies.map(enemy => {
        let updatedEnemy = { ...enemy };

        // Apply trail slow percent (used by physics for speed reduction)
        const slowPercent = trailResult.enemiesToSlow.get(enemy.id);
        if (slowPercent !== undefined) {
          updatedEnemy.trailSlowPercent = slowPercent;
        } else {
          // Clear slow if not in trail
          updatedEnemy.trailSlowPercent = undefined;
        }

        // Apply draft pull (immediate position adjustment)
        const pullVector = trailResult.enemiesToPull.get(enemy.id);
        if (pullVector) {
          updatedEnemy.position = {
            x: enemy.position.x + pullVector.x,
            y: enemy.position.y + pullVector.y,
          };
        }

        return updatedEnemy;
      });

      // =======================================================================
      // ON-KILL ZONE PROCESSING (Run 044)
      // Expire old zones, apply death marker slow, process hesitation
      // =======================================================================

      // 1. Expire old territorial marks and death markers
      const expiredZones = expireZones(
        territorialMarksRef.current,
        deathMarkersRef.current,
        physicsResult.state.gameTime
      );
      territorialMarksRef.current = expiredZones.territorialMarks;
      deathMarkersRef.current = expiredZones.deathMarkers;

      // 2. Clear expired enemy hesitations
      const hesitationMap = enemyHesitationRef.current;
      for (const [enemyId, expiry] of hesitationMap.entries()) {
        if (physicsResult.state.gameTime >= expiry) {
          hesitationMap.delete(enemyId);
        }
      }

      // 3. Apply death marker slow to enemies and check hesitation
      physicsResult.state.enemies = physicsResult.state.enemies.map(enemy => {
        let updatedEnemy = { ...enemy };

        // Apply death marker slow (corpse zones slow nearby enemies)
        const deathMarkerSlow = getDeathMarkerSlow(
          enemy.position.x,
          enemy.position.y,
          deathMarkersRef.current,
          physicsResult.state.gameTime
        );
        if (deathMarkerSlow > 0) {
          // Combine with any existing slow (trail slow)
          const existingSlow = updatedEnemy.trailSlowPercent ?? 0;
          updatedEnemy.trailSlowPercent = existingSlow + deathMarkerSlow;
        }

        // Check if enemy is hesitating (pack_signal effect)
        const hesitationExpiry = hesitationMap.get(enemy.id);
        if (hesitationExpiry !== undefined && physicsResult.state.gameTime < hesitationExpiry) {
          // Enemy is hesitating - apply 100% slow (freeze in place)
          updatedEnemy.trailSlowPercent = 100;
        }

        return updatedEnemy;
      });

      perfMonitor.endSystem('physics');

      // =======================================================================
      // PHASE 3: Collision Detection (< 3ms)
      // =======================================================================
      perfMonitor.beginSystem('collision');
      const collisionResult = checkCollisions(physicsResult.state);

      let newState = collisionResult.state;

      // DD-21: Apply enemy attack damage (separate from contact damage)
      // Appendix D: Check hover brake invulnerability
      if (physicsResult.enemyDamageDealt > 0 &&
          !isHoverBrakeInvulnerable(combatStateRef.current, newState.gameTime)) {
        // A3: Record attack encounter (not evaded - player took damage)
        recordAttackEncounter(axiomGuardianRef.current, false);
        recordDamageReceived(axiomGuardianRef.current, physicsResult.enemyDamageDealt);

        const healthBeforeAttack = newState.player.health;
        newState = {
          ...newState,
          player: {
            ...newState.player,
            health: Math.max(0, newState.player.health - physicsResult.enemyDamageDealt),
          },
        };

        // Trigger damage juice
        juiceSystem.emitDamage(newState.player.position, physicsResult.enemyDamageDealt);

        // Trigger damage sound callback
        callbacks.onPlayerDamaged?.(physicsResult.enemyDamageDealt);

        // GRAZE FRENZY: System disabled - no reset needed

        // Check for game over from attack damage
        if (newState.player.health <= 0) {
          newState = { ...newState, status: 'gameover' };

          // Part VII: Death voice line and record arc closure
          const deathLine = triggerVoiceLine(emotionalStateRef.current, 'death', newState.gameTime);
          if (deathLine) callbacks.onVoiceLine?.(deathLine);
          emotionalStateRef.current.arc = recordArcClosure(
            emotionalStateRef.current.arc,
            'enemy_attack'
          );

          // Run Axiom Guards on death (Part I: Four True Axioms)
          const deathContext = buildDeathContext(
            axiomGuardianRef.current,
            'combat',
            'Killed by enemy attack',
            'enemy',
            'attack',
            newState.wave,
            newState.gameTime,
            healthBeforeAttack,
            newState.player.health,
            false
          );
          const skillMetrics = buildSkillMetrics(
            axiomGuardianRef.current,
            newState.gameTime,
            newState.totalEnemiesKilled,
            newState.player.upgrades.length,
            (newState.player.synergies ?? []).length
          );
          const arcHistory = buildArcHistory(
            axiomGuardianRef.current,
            true,
            'dignity'
          );
          const axiomReport = runAxiomGuards(deathContext, skillMetrics, arcHistory);

          if (process.env.NODE_ENV === 'development') {
            logAxiomReport(axiomReport);
          }

          callbacks.onGameOver(newState, axiomReport);

          emitWitnessMark(witnessContextRef.current, {
            type: 'run_ended',
            gameTime: newState.gameTime,
            context: buildWitnessContext(newState),
            deathCause: 'enemy_attack',  // DD-21: More specific death cause
          });
        }
      } else if (physicsResult.enemyDamageDealt > 0) {
        // A3: Attack was evaded (hover brake saved us)
        recordAttackEncounter(axiomGuardianRef.current, true);
      }

      // Process collision events
      for (const event of collisionResult.events) {
        switch (event.type) {
          case 'enemy_killed': {
            // A3: Record damage dealt for skill metrics
            const enemyMaxHealth = (event as { enemyMaxHealth?: number }).enemyMaxHealth ?? 30;
            recordDamageDealt(axiomGuardianRef.current, enemyMaxHealth);

            // Add XP
            const xpValue = event.xpValue ?? 10;
            const enemyType = event.enemyType ?? 'worker';

            // DD-12: Vampiric - heal on kill
            const activeUpgrades = newState.player.activeUpgrades as ActiveUpgrades | undefined;
            const vampiricPercent = activeUpgrades?.vampiricPercent ?? 0;
            let newHealth = newState.player.health;

            if (vampiricPercent > 0) {
              const healAmount = Math.floor(
                newState.player.maxHealth * (vampiricPercent / 100)
              );
              newHealth = Math.min(
                newState.player.maxHealth,
                newState.player.health + healAmount
              );

              // TODO: Add emitHeal to juice system for vampiric visual feedback
              // juiceSystem.emitHeal?.(event.position, healAmount);
            }

            newState = {
              ...newState,
              player: {
                ...newState.player,
                xp: newState.player.xp + xpValue,
                health: newHealth,
              },
              totalEnemiesKilled: newState.totalEnemiesKilled + 1,
              score: newState.score + xpValue * 10,
            };

            // Trigger juice (DD-5: Fun Floor - kill = particles + sound + XP)
            juiceSystem.emitKill(event.position, enemyType);

            // Trigger kill sound callback (DD-5)
            // Run 036: ASMR Audio - Determine kill tier and combo
            const recentKills = juiceSystem.killTracker.recentKills;
            const killTier: import("../types").KillTier = recentKills >= 10 ? "massacre" : recentKills >= 3 ? "multi" : "single";
            const beeTypeMap: Record<string, import("../types").EnemyType> = { basic: "worker", fast: "scout", tank: "guard", boss: "royal", spitter: "propolis", colossal_tide: "royal" };
            const beeEnemyType = beeTypeMap[enemyType] ?? "worker";
            callbacks.onEnemyKilled?.(beeEnemyType, killTier, recentKills, event.position);

            // Part VII: Trigger voice lines for kills
            // Check for first kill (totalEnemiesKilled was just incremented)
            if (newState.totalEnemiesKilled === 1) {
              const line = triggerVoiceLine(emotionalStateRef.current, 'first_kill', newState.gameTime);
              if (line) callbacks.onVoiceLine?.(line);
            }
            // Check for massacre (5+ kills tracked by juice system's killTracker)
            // recentKills already computed above for ASMR audio
            if (recentKills >= 10) {
              const line = triggerVoiceLine(emotionalStateRef.current, 'massacre', newState.gameTime);
              if (line) callbacks.onVoiceLine?.(line);
            } else if (recentKills >= 3) {
              const line = triggerVoiceLine(emotionalStateRef.current, 'multi_kill', newState.gameTime);
              if (line) callbacks.onVoiceLine?.(line);
            }

            // DD-14: Burst - AoE damage on kill
            if (activeUpgrades?.burstRadius && activeUpgrades.burstRadius > 0) {
              const burstDamage = activeUpgrades.burstDamage ?? 10;
              const burstRadius = activeUpgrades.burstRadius;

              // Apply damage to enemies within burst radius
              newState = {
                ...newState,
                enemies: newState.enemies.map((enemy) => {
                  const dx = enemy.position.x - event.position.x;
                  const dy = enemy.position.y - event.position.y;
                  const distance = Math.sqrt(dx * dx + dy * dy);

                  if (distance < burstRadius && distance > 0) {
                    return { ...enemy, health: enemy.health - burstDamage };
                  }
                  return enemy;
                }),
              };
            }

            // Async witness mark (non-blocking)
            emitWitnessMark(witnessContextRef.current, {
              type: 'enemy_killed',
              gameTime: newState.gameTime,
              context: buildWitnessContext(newState),
            });

            // Colony Intelligence: Record kill for death pheromone deposit
            // This creates a "danger zone" that other bees will avoid
            if (colonyIntelligenceRef.current) {
              const enemyId = (event as { enemyId?: string }).enemyId ?? `enemy-${Date.now()}`;
              colonyIntelligenceRef.current = onEnemyKill(
                colonyIntelligenceRef.current,
                event.position,
                enemyId,
                newState.gameTime
              );
            }

            // Trophy Scent: Track unique enemy types killed for permanent damage bonus
            abilitiesRef.current = recordKillForTrophyScent(abilitiesRef.current, enemyType);
            break;
          }

          case 'player_hit': {
            // Appendix D: Check hover brake invulnerability
            if (isHoverBrakeInvulnerable(combatStateRef.current, newState.gameTime)) {
              // CLUTCH DODGE! A3: Attack was evaded
              recordAttackEncounter(axiomGuardianRef.current, true);
              break;
            }

            // Run 045: Check confusion cloud miss chance
            const attackerPos = event.position;
            if (checkConfusionCloudMiss(attackerPos, abilitiesRef.current, newState.gameTime)) {
              recordAttackEncounter(axiomGuardianRef.current, true);
              break;
            }

            // A3: Record attack encounter (not evaded - player took damage)
            recordAttackEncounter(axiomGuardianRef.current, false);
            let damageAmount = event.damage ?? 10;

            // Run 045: Process on-damaged abilities
            const attackerId = (event as { enemyId?: string }).enemyId ?? null;
            const onDamagedResult = processOnDamaged(
              abilitiesRef.current,
              newState.player.position,
              attackerId,
              damageAmount,
              newState.gameTime,
              newState.wave
            );
            damageAmount = Math.floor(damageAmount * onDamagedResult.damageReduction);
            if (attackerId) {
              damageAmount = Math.floor(damageAmount * getBitterTasteDebuff(attackerId, abilitiesRef.current, newState.gameTime));
            }
            // Run 048: Apply threat_aura damage reduction
            // "Enemies within 30px deal 5% less damage"
            const threatAuraReduction = getThreatAuraReduction(
              attackerPos,
              newState.player.position,
              abilitiesRef.current
            );
            damageAmount = Math.floor(damageAmount * threatAuraReduction);
            abilitiesRef.current = onDamagedResult.updatedAbilities;

            // Emit VFX for on-damaged abilities
            if (onDamagedResult.damageReduction < 1) {
              // Ablative shell triggered
              juiceSystem.emitAbilityJuice?.('ablative_shell', {
                position: newState.player.position,
                intensity: 1 - onDamagedResult.damageReduction
              });
            }
            if (onDamagedResult.newConfusionClouds.length > 0) {
              juiceSystem.emitAbilityJuice?.('confusion_cloud', {
                position: newState.player.position,
                intensity: 1.0
              });
            }
            if (onDamagedResult.bitterTasteTargets.length > 0) {
              juiceSystem.emitAbilityJuice?.('bitter_taste', {
                position: event.position,
                intensity: 1.0
              });
            }
            if (threatAuraReduction < 1) {
              // Threat aura reduced enemy damage
              juiceSystem.emitAbilityJuice?.('threat_aura', {
                position: newState.player.position,
                intensity: 1 - threatAuraReduction
              });
            }

            recordDamageReceived(axiomGuardianRef.current, damageAmount);

            const healthBeforeHit = newState.player.health;
            newState = {
              ...newState,
              player: {
                ...newState.player,
                health: Math.max(0, newState.player.health - damageAmount),
              },
            };

            // Trigger damage juice
            juiceSystem.emitDamage(newState.player.position, damageAmount);

            // Trigger damage sound callback (DD-5)
            callbacks.onPlayerDamaged?.(damageAmount);

            // GRAZE FRENZY: System disabled - no reset needed

            // DD-16: Check for clutch moment (survived near-death)
            if (newState.player.health > 0) {
              const healthFraction = newState.player.health / newState.player.maxHealth;
              // Count threats within 100 pixels of player
              const threatCount = newState.enemies.filter((enemy) => {
                const dx = enemy.position.x - newState.player.position.x;
                const dy = enemy.position.y - newState.player.position.y;
                return Math.sqrt(dx * dx + dy * dy) < 100;
              }).length;

              const clutchConfig = checkClutchMoment(healthFraction, threatCount);
              if (clutchConfig) {
                // Determine clutch level based on config
                const clutchLevel =
                  clutchConfig.timeScale <= 0.2
                    ? 'full'
                    : clutchConfig.timeScale <= 0.5
                      ? 'medium'
                      : 'critical';
                juiceSystem.triggerClutch(clutchLevel, clutchConfig.durationMs);
              }
            }

            // Check for game over
            if (newState.player.health <= 0) {
              newState = { ...newState, status: 'gameover' };

              // Part VII: Death voice line and record arc closure
              const deathLine = triggerVoiceLine(emotionalStateRef.current, 'death', newState.gameTime);
              if (deathLine) callbacks.onVoiceLine?.(deathLine);
              emotionalStateRef.current.arc = recordArcClosure(
                emotionalStateRef.current.arc,
                'enemy_damage'
              );

              // Run Axiom Guards on death (Part I: Four True Axioms)
              const killerType = (event as { enemyType?: string }).enemyType || 'contact';
              const deathContext = buildDeathContext(
                axiomGuardianRef.current,
                'combat',
                `Killed by ${killerType} contact`,
                killerType,
                'contact',
                newState.wave,
                newState.gameTime,
                healthBeforeHit,
                newState.player.health,
                false
              );
              const skillMetrics = buildSkillMetrics(
                axiomGuardianRef.current,
                newState.gameTime,
                newState.totalEnemiesKilled,
                newState.player.upgrades.length,
                (newState.player.synergies ?? []).length
              );
              const arcHistory = buildArcHistory(
                axiomGuardianRef.current,
                true,
                'dignity'
              );
              const axiomReport = runAxiomGuards(deathContext, skillMetrics, arcHistory);

              if (process.env.NODE_ENV === 'development') {
                logAxiomReport(axiomReport);
              }

              callbacks.onGameOver(newState, axiomReport);

              // Seal witness trace
              emitWitnessMark(witnessContextRef.current, {
                type: 'run_ended',
                gameTime: newState.gameTime,
                context: buildWitnessContext(newState),
                deathCause: 'enemy_damage',
              });
            }
            break;
          }
        }
      }
      perfMonitor.endSystem('collision');

      // =======================================================================
      // PHASE 3.5: Combat System (Appendix D Mechanics)
      // =======================================================================
      perfMonitor.beginSystem('combat');
      // Track if player took damage this frame for revenge buff
      const playerTookDamage = collisionResult.events.some(e => e.type === 'player_hit') ||
                                physicsResult.enemyDamageDealt > 0;

      // Handle afterimage dash - spawn images while in apex strike phase
      // (Uses Apex Strike state instead of legacy dash input)
      const isDashing = isStriking(apexStrikeRef.current);
      if (isDashing && !wasDashingRef.current) {
        combatStateRef.current = startDash(combatStateRef.current);
      } else if (!isDashing && wasDashingRef.current) {
        combatStateRef.current = endDash(combatStateRef.current);
      }
      wasDashingRef.current = isDashing;

      // Spawn afterimages during dash
      if (combatStateRef.current.isDashing) {
        combatStateRef.current = spawnAfterimage(
          combatStateRef.current,
          newState.player.position,
          newState.gameTime
        );
      }

      // Update combat system
      const combatResult = updateCombatSystem(
        combatStateRef.current,
        newState.player,
        newState.enemies as EnemyWithCombat[],
        newState.gameTime,
        playerTookDamage
      );
      combatStateRef.current = combatResult.combatState;

      // Apply bleed damage and afterimage damage to enemies
      let enemiesWithCombat = combatResult.enemies;
      for (const event of combatResult.events) {
        callbacks.onCombatEvent?.(event);

        if (event.type === 'bleed_tick') {
          // Bleed damage already applied in updateCombatSystem
        } else if (event.type === 'afterimage_damage') {
          // Afterimage damage already tracked, apply to enemy
          enemiesWithCombat = enemiesWithCombat.map(e => {
            if (e.id === event.enemyId) {
              return { ...e, health: e.health - event.damage };
            }
            return e;
          });
        } else if (event.type === 'venom_paralysis') {
          // Emit juice for paralysis (trap springing!)
          // juiceSystem.emitVenomTrigger?.(event.position);
        } else if (event.type === 'graze') {
          // GRAZE SYSTEM: Detection preserved, surface (sound/visuals/bonuses) DISABLED
          // The underlying graze detection still runs in combat.ts for potential future use
          // No particles, no sound, no frenzy stacks - silent tracking only
        } else if (event.type === 'graze_bonus_triggered') {
          // GRAZE BONUS: Surface disabled (no visual ring effect)
        } else if (event.type === 'hover_brake_activated') {
          // Emit hover brake flash
          // juiceSystem.emitHoverBrake?.(event.position);
        }
      }

      // Apply combat-modified enemies back to state
      newState = {
        ...newState,
        enemies: enemiesWithCombat,
      };

      // Update state with combat state for rendering
      callbacks.onCombatStateUpdate?.(combatStateRef.current);
      perfMonitor.endSystem('combat');

      // =======================================================================
      // PHASE 3.6: Melee Attack System (Run 036: Mandible Reaver)
      // =======================================================================
      // "The hornet doesn't shoot - it STRIKES. The mandibles are the weapon."
      perfMonitor.beginSystem('melee');

      // Get ability-modified config
      let meleeConfig = getModifiedConfig(MANDIBLE_REAVER_CONFIG, abilitiesRef.current);

      // GRAZE FRENZY: System preserved but bonuses DISABLED
      // The underlying graze tracking remains for potential future use, but no gameplay bonuses are applied

      // Auto-attack: Check if player can start a new attack
      // Run 039: Disable melee during apex strike - don't steal bumper combo kills!
      const isInApexStrike = apexStrikeRef.current.phase !== 'ready';
      if (!isInApexStrike && canAttack(meleeStateRef.current, currentTime, meleeConfig)) {
        // Get attack direction - ALWAYS toward nearest enemy (even if out of range)
        let attackDir = { x: 1, y: 0 };

        // Find nearest enemy for attack direction (regardless of range)
        if (newState.enemies.length > 0) {
          let nearestDist = Infinity;
          let nearestEnemy = newState.enemies[0];
          for (const enemy of newState.enemies) {
            const dx = enemy.position.x - newState.player.position.x;
            const dy = enemy.position.y - newState.player.position.y;
            const dist = dx * dx + dy * dy;
            if (dist < nearestDist) {
              nearestDist = dist;
              nearestEnemy = enemy;
            }
          }
          // Always point toward nearest enemy, even if far away
          const dx = nearestEnemy.position.x - newState.player.position.x;
          const dy = nearestEnemy.position.y - newState.player.position.y;
          const mag = Math.sqrt(dx * dx + dy * dy);
          if (mag > 0) {
            attackDir = { x: dx / mag, y: dy / mag };
          }
        }

        // Start the attack
        const attackResult = startAttack(
          meleeStateRef.current,
          attackDir,
          currentTime,
          meleeConfig
        );
        meleeStateRef.current = attackResult.newState;
        callbacks.onMeleeEvent?.(attackResult.event);
      }

      // Update active melee attack and process hits
      if (meleeStateRef.current.isActive || meleeStateRef.current.isInWindup || meleeStateRef.current.isInRecovery) {
        const meleeTargets = newState.enemies.map(e => ({
          id: e.id,
          position: e.position,
          radius: e.radius ?? 15,
          health: e.health,
        }));

        const meleeResult = updateMeleeAttack(
          meleeStateRef.current,
          newState.player.position,
          meleeTargets,
          abilitiesRef.current,
          currentTime,
          meleeConfig,
          0,  // hitCounter - will be tracked separately
          killStreakRef.current  // For momentum ability damage bonus
        );

        // Apply damage to enemies and handle kills
        let meleeModifiedEnemies = [...newState.enemies];
        const meleeKills: Array<{
          enemy: typeof newState.enemies[0];
          position: { x: number; y: number };
          healthPercentBeforeKill: number;  // For execution chain check
        }> = [];

        // Check if player has Venom Architect ability (now 'trace_venom' in new system)
        const hasVenomArchitect = abilitiesRef.current?.owned.includes('trace_venom') ?? false;

        for (const hit of meleeResult.hits) {
          // Sawtooth: Track hit count for every 5th hit bonus damage
          const sawtoothResult = incrementSawtoothCounter(abilitiesRef.current);
          abilitiesRef.current = sawtoothResult.state;
          // Note: sawtoothResult.isBonusHit can be used for visual/audio feedback

          meleeModifiedEnemies = meleeModifiedEnemies.map(e => {
            if (e.id === hit.enemyId) {
              const newHealth = e.health - hit.damage;

              // A3: Record damage dealt
              recordDamageDealt(axiomGuardianRef.current, hit.damage);

              // VENOM ARCHITECT: Apply venom stack on hit (if ability owned)
              if (hasVenomArchitect) {
                const currentVenomState = venomArchitectRef.current.get(e.id);
                const newVenomState = applyVenomArchitectStack(currentVenomState, newState.gameTime);
                venomArchitectRef.current.set(e.id, newVenomState);
              }

              // =======================================================================
              // ON-HIT ABILITY JUICE (Run 044)
              // =======================================================================
              const computed = computeAbilityEffects(abilitiesRef.current);

              // Venomous Strike: Green venom drip on poison damage
              if (computed.poisonDamage > 0) {
                juiceSystem.emitAbilityJuice?.('venomous_strike', {
                  position: hit.position,
                  intensity: 0.6
                });
              }

              // Critical Sting: Yellow crit flash (check if this hit was a crit)
              // Note: We can't easily detect crits here since calculateDamage is in melee.ts
              // But we can trigger on high damage hits (proxy for crits)
              if (computed.critChance > 0 && hit.damage > (newState.player.damage * 1.8)) {
                juiceSystem.emitAbilityJuice?.('critical_sting', {
                  position: hit.position,
                  intensity: 1.0
                });
              }

              // =======================================================================
              // LIFESTEAL: Heal player for % of damage dealt
              // =======================================================================
              if (computed.lifestealPercent > 0) {
                const healAmount = Math.floor(hit.damage * (computed.lifestealPercent / 100));
                if (healAmount > 0) {
                  // Store healing to apply after the map (we're inside a map so can't modify newState directly)
                  lifestealHealingRef.current += healAmount;

                  // Emit lifesteal juice - red health orbs from enemy to player
                  juiceSystem.emitAbilityJuice?.('lifesteal', {
                    position: hit.position,
                    intensity: Math.min(healAmount / 5, 1.0)
                  });
                }
              }

              // Track kills for processing
              if (newHealth <= 0) {
                // Calculate health % BEFORE the kill for execution chain
                const healthPercentBeforeKill = (e.health / e.maxHealth) * 100;
                meleeKills.push({ enemy: e, position: hit.position, healthPercentBeforeKill });
              }

              return { ...e, health: newHealth };
            }
            return e;
          });
        }

        // =======================================================================
        // LIFESTEAL: Apply accumulated healing from all hits this frame
        // =======================================================================
        if (lifestealHealingRef.current > 0) {
          const maxHealth = newState.player.maxHealth;
          const newPlayerHealth = Math.min(
            newState.player.health + lifestealHealingRef.current,
            maxHealth
          );
          newState = {
            ...newState,
            player: {
              ...newState.player,
              health: newPlayerHealth,
            },
          };
          lifestealHealingRef.current = 0;  // Reset for next frame
        }

        // Remove dead enemies and process kills
        const survivingEnemies = meleeModifiedEnemies.filter(e => e.health > 0);

        // Process each kill (XP, score, juice, callbacks)
        for (const kill of meleeKills) {
          const xpValue = kill.enemy.xpValue ?? 10;

          // NOTE: Vampiric healing on kill removed - lifesteal now heals on HIT above
          let newHealth = newState.player.health;

          newState = {
            ...newState,
            player: {
              ...newState.player,
              xp: newState.player.xp + xpValue,
              health: newHealth,
            },
            totalEnemiesKilled: newState.totalEnemiesKilled + 1,
            score: newState.score + xpValue * 10,
          };

          // Trigger juice (DD-5: Fun Floor - kill = particles + sound + XP)
          juiceSystem.emitKill(kill.position, kill.enemy.type);

          // =======================================================================
          // MOMENTUM: Build kill streak for damage bonus (Run 044)
          // +15% damage per consecutive kill, max 75% (5 stacks)
          // Streak resets after 3 seconds without a kill
          // =======================================================================
          const momentumComputed = computeAbilityEffects(abilitiesRef.current);
          if (momentumComputed.killStreakDamage > 0) {
            const MOMENTUM_TIMEOUT = 3000;  // 3 seconds to maintain streak
            const MAX_MOMENTUM_STACKS = 5;

            // Check if streak should reset (too long since last kill)
            const timeSinceLastKill = newState.gameTime - lastKillTimeRef.current;
            if (timeSinceLastKill > MOMENTUM_TIMEOUT) {
              killStreakRef.current = 0;
            }

            // Increment streak (capped)
            if (killStreakRef.current < MAX_MOMENTUM_STACKS) {
              killStreakRef.current++;

              // Emit momentum juice - orange aura buildup
              juiceSystem.emitAbilityJuice?.('momentum', {
                position: newState.player.position,
                intensity: killStreakRef.current / MAX_MOMENTUM_STACKS
              });
            }

            // Update last kill time
            lastKillTimeRef.current = newState.gameTime;
          }

          // Trigger kill sound callback (DD-5)
          const recentKills = juiceSystem.killTracker.recentKills;
          const killTier: import("../types").KillTier = recentKills >= 10 ? "massacre" : recentKills >= 3 ? "multi" : "single";
          callbacks.onEnemyKilled?.(kill.enemy.type, killTier, recentKills, kill.position);

          // Colony intelligence: track enemy kill
          if (colonyIntelligenceRef.current) {
            colonyIntelligenceRef.current = onEnemyKill(
              colonyIntelligenceRef.current,
              kill.position,
              kill.enemy.id,
              newState.gameTime
            );
          }

          // =======================================================================
          // ON-KILL ABILITY PROCESSING (Run 044)
          // territorial_mark, death_marker, clean_kill, pack_signal,
          // feeding_efficiency, updraft, corpse_heat, trophy_scent
          // =======================================================================
          const onKillResult = processOnKill(
            abilitiesRef.current,
            kill.position,
            kill.healthPercentBeforeKill >= 100 ? kill.enemy.maxHealth : kill.enemy.maxHealth - kill.enemy.health + 1,
            kill.enemy.maxHealth,
            kill.enemy.type,
            // Convert surviving enemies to OnKillEnemyInfo format
            survivingEnemies.map(e => ({ id: e.id, x: e.position.x, y: e.position.y })),
            newState.gameTime
          );

          // Update abilities state with runtime changes (trophy_scent, feeding_efficiency, updraft, corpse_heat)
          abilitiesRef.current = onKillResult.updatedAbilities;

          // Add new territorial marks
          if (onKillResult.newTerritorialMarks.length > 0) {
            territorialMarksRef.current = [
              ...territorialMarksRef.current,
              ...onKillResult.newTerritorialMarks,
            ];
          }

          // Add new death markers
          if (onKillResult.newDeathMarkers.length > 0) {
            deathMarkersRef.current = [
              ...deathMarkersRef.current,
              ...onKillResult.newDeathMarkers,
            ];
          }

          // Process clean kill explosions
          for (const explosion of onKillResult.explosions) {
            // Find enemies in explosion radius and damage them
            survivingEnemies.forEach(enemy => {
              const dx = enemy.position.x - explosion.x;
              const dy = enemy.position.y - explosion.y;
              const dist = Math.sqrt(dx * dx + dy * dy);
              if (dist <= explosion.radius) {
                enemy.health -= explosion.damage;
                // Emit visual effect for explosion
                juiceSystem.emitDamage(enemy.position, explosion.damage);
              }
            });
            // Emit ability-specific VFX for clean_kill
            juiceSystem.emitAbilityJuice?.('clean_kill', {
              position: { x: explosion.x, y: explosion.y },
              intensity: 1.0
            });
          }

          // Emit VFX for on-kill abilities
          if (onKillResult.newTerritorialMarks.length > 0) {
            juiceSystem.emitAbilityJuice?.('territorial_mark', {
              position: kill.position,
              intensity: 1.0
            });
          }
          if (onKillResult.newDeathMarkers.length > 0) {
            juiceSystem.emitAbilityJuice?.('death_marker', {
              position: kill.position,
              intensity: 1.0
            });
          }
          if (onKillResult.hesitateEnemyIds.length > 0) {
            juiceSystem.emitAbilityJuice?.('pack_signal', {
              position: kill.position,
              intensity: 1.0
            });
          }
          if (onKillResult.speedBoostPercent > 0) {
            juiceSystem.emitAbilityJuice?.('updraft', {
              position: newState.player.position,
              intensity: 1.0
            });
          }

          // Apply pack signal hesitation to nearby enemies
          for (const enemyId of onKillResult.hesitateEnemyIds) {
            // Store hesitation end time (0.1s = 100ms)
            enemyHesitationRef.current.set(enemyId, newState.gameTime + 100);
          }

          // =======================================================================
          // CHAIN LIGHTNING: On kill, damage nearest enemy within 100px
          // =======================================================================
          const chainComputed = computeAbilityEffects(abilitiesRef.current);
          if (chainComputed.hasChainKill && survivingEnemies.length > 0) {
            // Find nearest enemy within chain range (100px)
            const CHAIN_RANGE = 100;
            const CHAIN_DAMAGE_PERCENT = 0.5;  // 50% of player damage

            let nearestEnemy: typeof survivingEnemies[0] | null = null;
            let nearestDist = CHAIN_RANGE;

            for (const enemy of survivingEnemies) {
              const dx = enemy.position.x - kill.position.x;
              const dy = enemy.position.y - kill.position.y;
              const dist = Math.sqrt(dx * dx + dy * dy);
              if (dist < nearestDist) {
                nearestDist = dist;
                nearestEnemy = enemy;
              }
            }

            if (nearestEnemy) {
              // Deal chain damage
              const chainDamage = Math.floor(newState.player.damage * CHAIN_DAMAGE_PERCENT);
              nearestEnemy.health -= chainDamage;

              // Emit chain lightning juice - blue lightning arc
              juiceSystem.emitAbilityJuice?.('chain_lightning', {
                position: nearestEnemy.position,
                intensity: 1.0
              });

              // Also emit damage numbers
              juiceSystem.emitDamage(nearestEnemy.position, chainDamage);
            }
          }
        }

        // Filter out enemies killed by clean_kill explosions
        const postExplosionSurvivors = survivingEnemies.filter(e => e.health > 0);

        // Update enemies with survivors only
        newState = {
          ...newState,
          enemies: postExplosionSurvivors,
        };

        // Update melee state
        meleeStateRef.current = meleeResult.newState;

        // =======================================================================
        // EXECUTION CHAIN MECHANIC
        // When killing an enemy below 20% HP with melee and hasExecutionChain:
        // 1. Instantly refresh attack cooldown
        // 2. Dash to nearest enemy below 30% HP (within ~50px)
        // =======================================================================
        // Note: hasExecutionChain removed in new ability system - feature disabled
        const hasExecutionChain = false;
        if (hasExecutionChain && meleeKills.length > 0) {
          // Check if any kill was on an enemy below 20% HP
          const executionKill = meleeKills.find(kill => kill.healthPercentBeforeKill < 20);

          if (executionKill) {
            // 1. Reset melee attack cooldown - clear all attack state flags and set recovery to past
            meleeStateRef.current = {
              ...meleeStateRef.current,
              isActive: false,
              isInWindup: false,
              isInRecovery: false,
              recoveryEndTime: 0,  // Setting to 0 means cooldown check will pass immediately
              hitEnemyIds: new Set(),  // Clear hit tracking for next attack
            };

            // 2. Find nearest enemy with health < 30% of maxHealth
            let nearestWoundedEnemy: typeof newState.enemies[0] | null = null;
            let nearestDistance = Infinity;

            for (const enemy of survivingEnemies) {
              const healthPercent = (enemy.health / enemy.maxHealth) * 100;
              if (healthPercent < 30) {
                const dx = enemy.position.x - newState.player.position.x;
                const dy = enemy.position.y - newState.player.position.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < nearestDistance) {
                  nearestDistance = distance;
                  nearestWoundedEnemy = enemy;
                }
              }
            }

            // 3. If found, dash player toward that enemy (within ~50px)
            if (nearestWoundedEnemy) {
              const targetX = nearestWoundedEnemy.position.x;
              const targetY = nearestWoundedEnemy.position.y;
              const playerX = newState.player.position.x;
              const playerY = newState.player.position.y;

              // Calculate direction to target
              const dx = targetX - playerX;
              const dy = targetY - playerY;
              const distance = Math.sqrt(dx * dx + dy * dy);

              if (distance > 0) {
                // Dash to within ~50px of the target enemy
                const dashDistance = Math.max(0, distance - 50);
                const dirX = dx / distance;
                const dirY = dy / distance;

                let newPlayerX = playerX + dirX * dashDistance;
                let newPlayerY = playerY + dirY * dashDistance;

                // Clamp to arena bounds
                const playerRadius = newState.player.radius ?? 12;
                newPlayerX = Math.max(playerRadius, Math.min(ARENA_WIDTH - playerRadius, newPlayerX));
                newPlayerY = Math.max(playerRadius, Math.min(ARENA_HEIGHT - playerRadius, newPlayerY));

                newState = {
                  ...newState,
                  player: {
                    ...newState.player,
                    position: { x: newPlayerX, y: newPlayerY },
                  },
                };

                // Visual feedback for the execution chain dash
                juiceSystem.emitGrazeSpark(
                  { x: playerX, y: playerY },
                  { x: newPlayerX, y: newPlayerY },
                  1
                );

                const woundedHealthPercent = (nearestWoundedEnemy.health / nearestWoundedEnemy.maxHealth) * 100;
                if (process.env.NODE_ENV === 'development') {
                  console.log('[EXECUTION CHAIN] Triggered! Dashed', dashDistance.toFixed(0), 'px to wounded enemy at', woundedHealthPercent.toFixed(0), '% HP');
                }
              }
            } else if (process.env.NODE_ENV === 'development') {
              console.log('[EXECUTION CHAIN] Cooldown reset, but no wounded (<30% HP) enemy found');
            }
          }
        }

        // Emit melee events
        for (const event of meleeResult.events) {
          callbacks.onMeleeEvent?.(event);

          // Special juice for multi-kills
          if (event.type === 'attack_massacre') {
            // Big screen shake for 5+ kills in one swing
            juiceSystem.triggerShake(meleeConfig.massacreShake, 300);
          } else if (event.type === 'attack_multikill') {
            juiceSystem.triggerShake(meleeConfig.multiKillShake, 200);
          }
        }

        // Notify listeners of melee state update
        callbacks.onMeleeStateUpdate?.(meleeStateRef.current);
      }

      perfMonitor.endSystem('melee');

      // =======================================================================
      // PHASE 3.65: Passive Aura Processing (Run 043)
      // hover_pressure, buzz_field, barbed_chitin, threat_aura
      // =======================================================================
      // "You exist near them and they dissolve."

      // Update stationary time tracking for buzz_field
      const playerSpeed = Math.sqrt(playerVelocity.x * playerVelocity.x + playerVelocity.y * playerVelocity.y);
      if (playerSpeed < STATIONARY_VELOCITY_THRESHOLD) {
        stationaryTimeRef.current += deltaTime;
      } else {
        stationaryTimeRef.current = 0;
      }

      // Process passive auras - apply damage to nearby enemies
      const auraResult: AuraResult = processPassiveAuras(
        abilitiesRef.current,
        newState.player.position,
        playerVelocity,
        newState.enemies.map(e => ({
          id: e.id,
          position: e.position,
          x: e.position.x,
          y: e.position.y,
        })),
        deltaTime,
        stationaryTimeRef.current
      );

      // Apply aura damage to enemies
      if (auraResult.enemyDamage.size > 0 || auraResult.enemyDebuffs.size > 0) {
        let auraModifiedEnemies = [...newState.enemies];
        const auraKills: Array<{
          enemy: typeof newState.enemies[0];
          position: { x: number; y: number };
        }> = [];

        // Track which aura VFX we've emitted this frame (to avoid spam)
        let emittedAuraVfx = false;

        for (const [enemyId, damage] of auraResult.enemyDamage) {
          auraModifiedEnemies = auraModifiedEnemies.map(e => {
            if (e.id === enemyId) {
              const newHealth = e.health - damage;

              // Record damage dealt
              recordDamageDealt(axiomGuardianRef.current, damage);

              // Emit aura VFX at enemy position (once per frame to avoid spam)
              if (!emittedAuraVfx) {
                juiceSystem.emitAbilityJuice?.('hover_pressure', {
                  position: e.position,
                  intensity: 0.3
                });
                emittedAuraVfx = true;
              }

              // Track kills from aura damage
              if (newHealth <= 0 && e.health > 0) {
                auraKills.push({
                  enemy: e,
                  position: e.position,
                });
              }

              return { ...e, health: newHealth };
            }
            return e;
          });
        }

        // Emit buzz_field VFX if stationary aura is active (player standing still)
        if (stationaryTimeRef.current >= 500 && auraResult.enemyDamage.size > 0) {
          juiceSystem.emitAbilityJuice?.('buzz_field', {
            position: newState.player.position,
            intensity: Math.min(1, stationaryTimeRef.current / 2000)
          });
        }

        // Process aura kills - grant XP, emit juice
        for (const auraKill of auraKills) {
          const xpValue = auraKill.enemy.xpValue ?? 10;
          newState = {
            ...newState,
            player: {
              ...newState.player,
              xp: newState.player.xp + xpValue,
            },
            totalEnemiesKilled: newState.totalEnemiesKilled + 1,
            score: newState.score + xpValue * 10,
          };

          // Trigger kill juice
          juiceSystem.emitKill(auraKill.position, auraKill.enemy.type);

          // Trigger kill callback
          const recentKills = juiceSystem.killTracker.recentKills;
          const killTier: import("../types").KillTier = recentKills >= 10 ? "massacre" : recentKills >= 3 ? "multi" : "single";
          callbacks.onEnemyKilled?.(auraKill.enemy.type, killTier, recentKills, auraKill.position);

          // Colony intelligence: track kill
          if (colonyIntelligenceRef.current) {
            colonyIntelligenceRef.current = onEnemyKill(
              colonyIntelligenceRef.current,
              auraKill.position,
              auraKill.enemy.id,
              newState.gameTime
            );
          }
        }

        // Remove dead enemies from aura damage
        const survivingAfterAura = auraModifiedEnemies.filter(e => e.health > 0);

        newState = {
          ...newState,
          enemies: survivingAfterAura,
        };

        // Note: threat_aura debuffs are applied in player_hit event handler
        // using getThreatAuraReduction() - see Run 048 integration
      }

      // =======================================================================
      // REGENERATION: Heal HP per second (Run 044)
      // =======================================================================
      const regenComputed = computeAbilityEffects(abilitiesRef.current);
      if (regenComputed.hpPerSecond > 0 && newState.player.health < newState.player.maxHealth) {
        // Convert HP/second to HP/frame based on deltaTime
        const hpPerFrame = regenComputed.hpPerSecond * (deltaTime / 1000);

        // Track accumulated regen to avoid floating point issues
        if (!regenAccumulatorRef.current) {
          regenAccumulatorRef.current = 0;
        }
        regenAccumulatorRef.current += hpPerFrame;

        // Apply whole HP points when accumulated enough
        if (regenAccumulatorRef.current >= 1) {
          const healAmount = Math.floor(regenAccumulatorRef.current);
          regenAccumulatorRef.current -= healAmount;

          const newPlayerHealth = Math.min(
            newState.player.health + healAmount,
            newState.player.maxHealth
          );
          newState = {
            ...newState,
            player: {
              ...newState.player,
              health: newPlayerHealth,
            },
          };

          // Emit regeneration juice - green healing sparkles (throttled to every ~1 HP)
          juiceSystem.emitAbilityJuice?.('regeneration', {
            position: newState.player.position,
            intensity: 0.3
          });
        }
      }

      // =======================================================================
      // PHASE 3.66: Threshold & Periodic Abilities (Run 045)
      // =======================================================================
      // Process heat_retention, molting_burst, aggro_pulse

      // Clean up expired confusion clouds and bitter taste debuffs
      abilitiesRef.current = cleanupExpiredEffects(abilitiesRef.current, newState.gameTime);

      // Process threshold abilities (heat_retention, molting_burst)
      const thresholdResult = processThresholds(
        abilitiesRef.current,
        newState.player.health,
        newState.player.maxHealth,
        newState.gameTime
      );
      abilitiesRef.current = thresholdResult.updatedAbilities;

      // Handle molting burst trigger
      if (thresholdResult.moltingBurstTriggered) {
        // Apply damage burst to enemies in radius
        newState = {
          ...newState,
          enemies: newState.enemies.map(enemy => {
            const dx = enemy.position.x - newState.player.position.x;
            const dy = enemy.position.y - newState.player.position.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist <= thresholdResult.moltingBurstRadius) {
              return { ...enemy, health: enemy.health - thresholdResult.moltingBurstDamage };
            }
            return enemy;
          }),
        };

        // Grant invulnerability (use existing invincibilityEndTime field)
        newState = {
          ...newState,
          player: {
            ...newState.player,
            invincible: true,
            invincibilityEndTime: newState.gameTime + thresholdResult.moltingBurstInvulnMs,
          },
        };

        // Remove dead enemies
        newState = {
          ...newState,
          enemies: newState.enemies.filter(e => e.health > 0),
        };

        juiceSystem.emitDamage(newState.player.position, thresholdResult.moltingBurstDamage);
        // Emit ability-specific VFX for molting_burst
        juiceSystem.emitAbilityJuice?.('molting_burst', {
          position: newState.player.position,
          intensity: 1.0
        });
        juiceSystem.triggerShake(5, 300);
      }

      // Process periodic abilities (aggro_pulse)
      const periodicResult = processPeriodicEffects(
        abilitiesRef.current,
        newState.player.position,
        newState.enemies,
        newState.gameTime
      );
      abilitiesRef.current = periodicResult.updatedAbilities;

      // Apply aggro pulse to enemies (force targeting player)
      if (periodicResult.aggroPulseTriggered && periodicResult.aggroEnemyIds.length > 0) {
        const aggroExpiry = newState.gameTime + periodicResult.aggroDurationMs;
        newState = {
          ...newState,
          enemies: newState.enemies.map(enemy => {
            if (periodicResult.aggroEnemyIds.includes(enemy.id)) {
              return { ...enemy, aggroUntil: aggroExpiry };
            }
            return enemy;
          }),
        };
        // Emit ability-specific VFX for aggro_pulse
        juiceSystem.emitAbilityJuice?.('aggro_pulse', {
          position: newState.player.position,
          intensity: periodicResult.aggroEnemyIds.length / 10 // Scale by affected count
        });
      }

      // =======================================================================
      // PHASE 3.7: Thermal Momentum (Run 042: Movement-based heat mechanic)
      // =======================================================================
      // "Build heat while moving. Stop to release a damage pulse."
      // Note: hasThermalMomentum removed in new ability system - feature disabled
      if (false) { // TODO: Re-enable when thermal momentum ability is added to new system
        const thermal = thermalMomentumRef.current;
        const currentPos = newState.player.position;

        // Calculate velocity magnitude from playerVelocity
        const velocityMag = Math.sqrt(playerVelocity.x * playerVelocity.x + playerVelocity.y * playerVelocity.y);
        const isMoving = velocityMag > THERMAL_MOMENTUM.VELOCITY_THRESHOLD;

        if (isMoving) {
          // Player is moving - build heat
          const lastPos = thermal.lastPosition;
          if (lastPos != null) {
            // Non-null assertion safe: within null check block
            const dx = currentPos.x - lastPos!.x;
            const dy = currentPos.y - lastPos!.y;
            const distanceTraveled = Math.sqrt(dx * dx + dy * dy);

            // Add heat based on distance
            thermal.currentHeat = Math.min(
              THERMAL_MOMENTUM.MAX_HEAT,
              thermal.currentHeat + distanceTraveled * THERMAL_MOMENTUM.HEAT_PER_PIXEL
            );
          }

          // Update last position and reset stop state
          thermal.lastPosition = { x: currentPos.x, y: currentPos.y };
          thermal.stoppedTime = 0;
          thermal.hasReleased = false;
        } else {
          // Player stopped - check for heat release
          if (!thermal.hasReleased && thermal.currentHeat > 0) {
            // First frame of stopping - record stop time
            if (thermal.stoppedTime === 0) {
              thermal.stoppedTime = newState.gameTime;
            }

            const timeStopped = newState.gameTime - thermal.stoppedTime;

            if (timeStopped < THERMAL_MOMENTUM.RELEASE_WINDOW) {
              // Within release window - RELEASE THE PULSE!
              const pulseDamage = Math.floor(thermal.currentHeat * THERMAL_MOMENTUM.DAMAGE_PER_HEAT);

              if (pulseDamage > 0) {
                // Apply damage to enemies within pulse radius
                newState = {
                  ...newState,
                  enemies: newState.enemies.map((enemy) => {
                    const dx = enemy.position.x - currentPos.x;
                    const dy = enemy.position.y - currentPos.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < THERMAL_MOMENTUM.PULSE_RADIUS) {
                      return { ...enemy, health: enemy.health - pulseDamage };
                    }
                    return enemy;
                  }),
                };

                // Visual feedback - emit pulse effect
                juiceSystem.emitDamage(currentPos, pulseDamage);
                juiceSystem.triggerShake(thermal.currentHeat / 20, 150);

                // Process kills from thermal pulse
                const thermalDeadEnemies = newState.enemies.filter(e => e.health <= 0);
                for (const deadEnemy of thermalDeadEnemies) {
                  const xpValue = deadEnemy.xpValue ?? 10;
                  newState = {
                    ...newState,
                    player: {
                      ...newState.player,
                      xp: newState.player.xp + xpValue,
                    },
                    totalEnemiesKilled: newState.totalEnemiesKilled + 1,
                    score: newState.score + xpValue * 10,
                  };
                  juiceSystem.emitKill(deadEnemy.position, deadEnemy.type);
                  callbacks.onEnemyKilled?.(deadEnemy.type, 'single', 1, deadEnemy.position);
                }

                // Remove dead enemies
                newState = {
                  ...newState,
                  enemies: newState.enemies.filter(e => e.health > 0),
                };
              }

              // Mark as released
              thermal.hasReleased = true;
              thermal.currentHeat = 0;
            } else {
              // Past release window - decay heat rapidly
              const decayAmount = (THERMAL_MOMENTUM.DECAY_RATE * deltaTime) / 1000;
              thermal.currentHeat = Math.max(0, thermal.currentHeat - decayAmount);
            }
          }

          // Update last position even when stopped
          thermal.lastPosition = { x: currentPos.x, y: currentPos.y };
        }
      }


      // =======================================================================
      // PHASE 3.7: Venom Architect DOT Processing
      // =======================================================================
      // Process venom damage ticks and handle venom-kill explosions
      // Only runs if player has the venom_architect ability (now 'trace_venom' in new system)
      const hasVenomArchitectAbility = abilitiesRef.current?.owned.includes('trace_venom') ?? false;

      if (hasVenomArchitectAbility && venomArchitectRef.current.size > 0) {
        let venomModifiedEnemies = [...newState.enemies];
        const venomKills: Array<{
          enemy: typeof newState.enemies[0];
          position: { x: number; y: number };
          venomStacks: number;
        }> = [];

        // Process venom damage for each enemy
        for (const enemy of venomModifiedEnemies) {
          const venomState = venomArchitectRef.current.get(enemy.id);
          if (!venomState || venomState.stacks <= 0) continue;

          // Update venom state and get damage
          const venomResult = updateVenomArchitectState(venomState, newState.gameTime);
          venomArchitectRef.current.set(enemy.id, venomResult.state);

          if (venomResult.damage > 0) {
            // Apply venom damage
            const newHealth = enemy.health - venomResult.damage;

            // Emit poison tick juice - green floating damage number (Run 044)
            juiceSystem.emitPoisonTick(enemy.position, venomResult.damage, venomResult.state.stacks);

            // Check if this VENOM damage killed the enemy (not direct attack)
            if (newHealth <= 0 && enemy.health > 0) {
              // VENOM KILL! This triggers explosion
              venomKills.push({
                enemy,
                position: enemy.position,
                venomStacks: venomResult.state.stacks,
              });
            }

            // Update enemy health
            venomModifiedEnemies = venomModifiedEnemies.map(e =>
              e.id === enemy.id ? { ...e, health: newHealth } : e
            );
          }
        }

        // Process venom kills - they EXPLODE!
        for (const venomKill of venomKills) {
          // Calculate explosion damage: stacks x 10
          const explosionDamage = calculateVenomArchitectExplosionDamage(venomKill.venomStacks);

          // Find enemies within explosion radius (80px)
          const nearbyEnemies = venomModifiedEnemies.filter(e => {
            if (e.id === venomKill.enemy.id) return false;
            if (e.health <= 0) return false;

            const dx = e.position.x - venomKill.position.x;
            const dy = e.position.y - venomKill.position.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            return distance <= VENOM_ARCHITECT.EXPLOSION_RADIUS;
          });

          // Apply explosion damage to nearby enemies
          for (const nearbyEnemy of nearbyEnemies) {
            venomModifiedEnemies = venomModifiedEnemies.map(e => {
              if (e.id === nearbyEnemy.id) {
                return { ...e, health: e.health - explosionDamage };
              }
              return e;
            });

            // Record damage dealt
            recordDamageDealt(axiomGuardianRef.current, explosionDamage);
          }

          // Clean up venom state for dead enemy
          venomArchitectRef.current.delete(venomKill.enemy.id);

          // Emit venom explosion juice (purple explosion particles)
          juiceSystem.emitKill(venomKill.position, 'royal'); // Use royal particles for venom explosion

          // Emit venom_architect ability juice for green venom burst
          juiceSystem.emitAbilityJuice?.('venom_architect', {
            position: venomKill.position,
            intensity: Math.min(venomKill.venomStacks / 10, 1.0)
          });

          // Add XP and score for venom kill
          const xpValue = venomKill.enemy.xpValue ?? 10;
          newState = {
            ...newState,
            player: {
              ...newState.player,
              xp: newState.player.xp + xpValue,
            },
            totalEnemiesKilled: newState.totalEnemiesKilled + 1,
            score: newState.score + xpValue * 10 + explosionDamage, // Bonus score for explosion damage
          };

          // Trigger kill callback
          const recentKills = juiceSystem.killTracker.recentKills;
          const killTier: import("../types").KillTier = recentKills >= 10 ? "massacre" : recentKills >= 3 ? "multi" : "single";
          callbacks.onEnemyKilled?.(venomKill.enemy.type, killTier, recentKills, venomKill.position);

          // Log explosion for debugging
          if (process.env.NODE_ENV === 'development') {
            console.log(
              `[VENOM] Explosion! ${venomKill.venomStacks} stacks = ${explosionDamage} damage to ${nearbyEnemies.length} enemies`
            );
          }
        }

        // Remove dead enemies (from venom damage AND explosions)
        const survivingAfterVenom = venomModifiedEnemies.filter(e => e.health > 0);

        // Clean up venom state for dead enemies
        for (const enemy of venomModifiedEnemies) {
          if (enemy.health <= 0) {
            venomArchitectRef.current.delete(enemy.id);
          }
        }

        newState = {
          ...newState,
          enemies: survivingAfterVenom,
        };
      }

      // =======================================================================
      // PHASE 4: Spawning
      // =======================================================================
      perfMonitor.beginSystem('spawn');
      const spawnResult: SpawnResult = updateSpawner(newState, deltaTime);
      // Cast required: spawn.ts uses minimal GameState stub to avoid circular imports
      newState = spawnResult.state as unknown as GameState;

      // Wave complete event
      if (spawnResult.waveComplete) {
        juiceSystem.emitWaveComplete(newState.wave);
        callbacks.onWaveComplete(newState.wave);

        // Reset ability runtime state for new wave (e.g., ablativeShellTriggered)
        abilitiesRef.current = resetRuntimeForWave(abilitiesRef.current);

        emitWitnessMark(witnessContextRef.current, {
          type: 'wave_completed',
          gameTime: newState.gameTime,
          context: buildWitnessContext(newState),
          wave: newState.wave,
        });
      }

      // =======================================================================
      // PHASE 4.5: Metamorphosis (DD-030)
      // =======================================================================
      // Update enemy survival times and pulsing states
      // deltaTime is in ms, but survivalTime and thresholds are in seconds
      const metamorphResult: MetamorphosisResult = updateMetamorphosis(
        newState.enemies,
        deltaTime / 1000, // Convert ms to seconds
        newState.hasWitnessedFirstMetamorphosis ?? false
      );

      // Replace enemies with updated versions
      // Note: metamorphResult.enemies already includes any new colossals
      newState = {
        ...newState,
        enemies: metamorphResult.enemies,
        hasWitnessedFirstMetamorphosis:
          (newState.hasWitnessedFirstMetamorphosis ?? false) ||
          metamorphResult.isFirstMetamorphosis,
      };

      // Handle first metamorphosis revelation (DD-030-3)
      if (metamorphResult.isFirstMetamorphosis) {
        // Emit witness mark for the revelation
        emitWitnessMark(witnessContextRef.current, {
          type: 'first_metamorphosis',
          gameTime: newState.gameTime,
          context: buildWitnessContext(newState),
        });

        // Trigger revelation visual (if juice system supports it)
        // juiceSystem.triggerRevelation?.();
      }

      // =======================================================================
      // PHASE 4.6: Colossal Behavior (DD-030-4) - DISABLED in bee theme
      // =======================================================================
      // NOTE: colossal_tide enemy type does not exist in bee theme
      // This entire block is preserved but disabled for future reference
      // The bee theme uses THE BALL formation mechanic instead of colossals
      perfMonitor.endSystem('spawn');

      // =======================================================================
      // PHASE 4.7: Colony Intelligence (Part XI Phase 4)
      // =======================================================================
      // "They learned my patterns. They EARNED this kill."
      // Note: Colony intelligence runs within the 'spawn' system budget

      // Initialize colony intelligence if not already done
      if (!colonyIntelligenceRef.current) {
        colonyIntelligenceRef.current = createColonyIntelligence(
          ARENA_WIDTH,
          ARENA_HEIGHT,
          newState.gameTime
        );
      }

      // Update colony intelligence every frame
      const colonyResult = updateColonyIntelligence(
        colonyIntelligenceRef.current,
        newState.player.position,
        playerVelocity,
        ARENA_WIDTH,
        ARENA_HEIGHT,
        newState.gameTime,
        deltaTime
      );
      colonyIntelligenceRef.current = colonyResult.intelligence;

      // Emit colony events
      for (const colonyEvent of colonyResult.events) {
        callbacks.onColonyEvent?.(colonyEvent);
      }

      // Notify listeners of intelligence update
      callbacks.onColonyIntelligenceUpdate?.(colonyIntelligenceRef.current);

      // Apply bee intelligence to enemy movement
      // Each bee reads pheromones and adjusts its targeting
      newState = {
        ...newState,
        enemies: newState.enemies.map(enemy => {
          // Cast to local Enemy type which has 'speed' field
          const localEnemy = enemy as unknown as LocalEnemy;

          const beeIntel = getBeeIntelligence(
            colonyIntelligenceRef.current!,
            enemy.position,
            newState.player.position,
            playerVelocity
          );

          // Apply speed modifier from pheromones (alarm = faster)
          // Use local enemy speed or default to 1 if not present
          const baseSpeed = localEnemy.speed ?? 50;
          const modifiedSpeed = baseSpeed * beeIntel.speedMultiplier;

          // Apply avoidance vector (death pheromones = avoid)
          const avoidX = beeIntel.avoidanceVector.x * 10;
          const avoidY = beeIntel.avoidanceVector.y * 10;

          // Apply coordination pull (towards THE BALL formation)
          const coordX = beeIntel.coordinationPull.x * 15;
          const coordY = beeIntel.coordinationPull.y * 15;

          // Calculate direction to anticipated target (not just current player pos)
          const targetX = beeIntel.anticipatedTarget.x;
          const targetY = beeIntel.anticipatedTarget.y;

          return {
            ...enemy,
            speed: modifiedSpeed,
            // Store intelligence data for formation system to use
            beeIntelligence: {
              shouldJoinBall: beeIntel.shouldJoinBall,
              shouldBeCautious: beeIntel.shouldBeCautious,
              anticipatedTarget: { x: targetX, y: targetY },
              avoidanceOffset: { x: avoidX, y: avoidY },
              coordinationOffset: { x: coordX, y: coordY },
            },
          };
        }),
      };

      // =======================================================================
      // PHASE 4.8: THE BALL Formation (Run 036: The Signature Mechanic!)
      // RUN 041: Multi-ball with bee cooldowns
      // =======================================================================
      // "When they form THE BALL, surrounding you, vibrating, raising the
      //  temperature until you cook — you'll understand: sometimes the invader loses."
      perfMonitor.beginSystem('formation');

      // Update all balls via the manager (handles cooldowns, multi-ball)
      const managerResult = updateBallManager(
        ballManagerRef.current,
        newState.player.position,
        newState.enemies,
        newState.gameTime,
        deltaTime,
        newState.wave
      );

      // Update manager state
      ballManagerRef.current = managerResult.manager;

      // Get primary ball for backwards compatibility (first ball or empty)
      const primaryBall = managerResult.manager.balls[0] ?? createBallState();
      ballStateRef.current = primaryBall;

      // Combine results from all balls
      const ballResult: BallUpdateResult = {
        state: primaryBall,
        events: managerResult.allEvents,
        damageToPlayer: managerResult.totalDamage,
        knockback: managerResult.combinedKnockback,
        knockbackSources: managerResult.ballResults.flatMap(r => r.knockbackSources),
      };

      // Notify listeners (primary ball for UI compatibility)
      callbacks.onBallStateUpdate?.(primaryBall);

      // Emit ball events
      for (const ballEvent of ballResult.events) {
        callbacks.onBallEvent?.(ballEvent);

        // Special handling for specific events
        if (ballEvent.type === 'ball_forming_started') {
          // Part VII: Voice line when BALL starts forming
          const ballLine = triggerVoiceLine(emotionalStateRef.current, 'ball_forming', newState.gameTime);
          if (ballLine) callbacks.onVoiceLine?.(ballLine);

          emitWitnessMark(witnessContextRef.current, {
            type: 'ball_forming',
            gameTime: newState.gameTime,
            context: buildWitnessContext(newState),
          });
        } else if (ballEvent.type === 'ball_escaped') {
          // Player escaped THE BALL! Record this achievement
          const escapeCount = ballResult.state.escapeCount;
          const escapeLine = triggerVoiceLine(emotionalStateRef.current, 'survived_ball', newState.gameTime);
          if (escapeLine) callbacks.onVoiceLine?.(escapeLine);

          emitWitnessMark(witnessContextRef.current, {
            type: 'ball_escaped',
            gameTime: newState.gameTime,
            context: { ...buildWitnessContext(newState), escapeCount },
          });
        }
      }

      // Apply BALL damage to player
      if (ballResult.damageToPlayer > 0) {
        const healthBeforeBall = newState.player.health;
        newState = {
          ...newState,
          player: {
            ...newState.player,
            health: Math.max(0, newState.player.health - ballResult.damageToPlayer),
          },
        };

        // Trigger damage juice
        juiceSystem.emitDamage(newState.player.position, ballResult.damageToPlayer);
        callbacks.onPlayerDamaged?.(ballResult.damageToPlayer);

        // Check for game over from THE BALL cooking
        if (newState.player.health <= 0) {
          newState = { ...newState, status: 'gameover' };

          // The colony always wins.
          const deathLine = triggerVoiceLine(emotionalStateRef.current, 'death', newState.gameTime);
          if (deathLine) callbacks.onVoiceLine?.(deathLine);
          emotionalStateRef.current.arc = recordArcClosure(emotionalStateRef.current.arc, 'ball_cooked');

          // Run Axiom Guards
          const deathContext = buildDeathContext(
            axiomGuardianRef.current,
            'ball',  // Death cause type
            'Cooked alive by THE BALL',
            'ball',  // Killer type
            'heat',  // Attack type
            newState.wave,
            newState.gameTime,
            healthBeforeBall,
            newState.player.health,
            true // THE BALL death is ALWAYS dignified - the colony earned it
          );
          const skillMetrics = buildSkillMetrics(
            axiomGuardianRef.current,
            newState.gameTime,
            newState.totalEnemiesKilled,
            newState.player.upgrades.length,
            (newState.player.synergies ?? []).length
          );
          const arcHistory = buildArcHistory(axiomGuardianRef.current, true, 'dignity');
          const axiomReport = runAxiomGuards(deathContext, skillMetrics, arcHistory);

          if (process.env.NODE_ENV === 'development') {
            logAxiomReport(axiomReport);
          }

          callbacks.onGameOver(newState, axiomReport);

          emitWitnessMark(witnessContextRef.current, {
            type: 'run_ended',
            gameTime: newState.gameTime,
            context: buildWitnessContext(newState),
            deathCause: 'ball_cooking', // THE BALL got them!
          });
        }
      }

      // Run 036: Apply BALL knockback to player (lunge attacks + boundary + outside bee punches)
      // Run 038: Knockback is now ANIMATED - player loses control and slides to destination
      // RUN 042: Soft clamp - lunge knockback keeps player inside the ball (bounce effect)
      // Multiple knockback sources (e.g., punch + boundary) combine into one slide to final position
      if (ballResult.knockback && !newState.player.knockback) {
        const kb = ballResult.knockback;
        const isLungeHit = ballResult.knockbackSources.some(s => s.type === 'lunge');

        // Calculate knockback destination
        let newPlayerX = newState.player.position.x + kb.direction.x * kb.force;
        let newPlayerY = newState.player.position.y + kb.direction.y * kb.force;

        // RUN 042: Soft clamp for lunge hits - keep player bouncing inside the ball
        // This prevents "clipping" escapes where knockback pushes player out
        if (isLungeHit && ballResult.state.phase !== 'inactive') {
          const ballCenter = ballResult.state.center;
          const ballRadius = ballResult.state.currentRadius;
          const safeMargin = 20; // Keep player this far inside the ball edge

          // Calculate distance from ball center to knockback destination
          const dxFromCenter = newPlayerX - ballCenter.x;
          const dyFromCenter = newPlayerY - ballCenter.y;
          const distFromCenter = Math.sqrt(dxFromCenter * dxFromCenter + dyFromCenter * dyFromCenter);

          // If destination would be outside ball (or too close to edge), bounce back
          const maxSafeRadius = ballRadius - safeMargin;
          if (distFromCenter > maxSafeRadius) {
            // Reflect/clamp: push toward ball center instead
            // Calculate direction from center to destination
            const normX = dxFromCenter / distFromCenter;
            const normY = dyFromCenter / distFromCenter;

            // Bounce: reflect off the boundary back into the ball
            // New position is inside ball, offset from center toward original direction
            const bounceRadius = maxSafeRadius * 0.7; // Bounce to 70% of safe radius
            newPlayerX = ballCenter.x + normX * bounceRadius;
            newPlayerY = ballCenter.y + normY * bounceRadius;

            console.log('[BALL] Soft clamp! Player bounced inside ball instead of escaping');
          }

          // RUN 042: Stun player for 200ms after lunge hit (lose control)
          const LUNGE_STUN_DURATION = 200;
          newState = {
            ...newState,
            player: {
              ...newState.player,
              stunBounce: {
                active: true,
                velocity: { x: 0, y: 0 },
                endTime: newState.gameTime + LUNGE_STUN_DURATION,
                bounceCount: 0,
                maxBounces: 0,
                ballCenter: ballCenter,
                ballRadius: ballRadius,
              },
            },
          };

          // RUN 042: Reset apex strike charge on lunge hit
          // Getting hit by a bee lunge interrupts your dash charge
          if (apexStrikeRef.current.chargeLevel > 0 || apexStrikeRef.current.phase === 'lock') {
            console.log('[BALL] Lunge hit! Resetting apex charge from', apexStrikeRef.current.chargeLevel.toFixed(2));
            apexStrikeRef.current = {
              ...apexStrikeRef.current,
              phase: 'ready',
              chargeLevel: 0,
              chargeTime: 0,
              lockDirection: null,
              lockTimer: 0,
            };
          }
        }

        // Clamp to arena bounds
        const playerRadius = newState.player.radius ?? 12;
        const clampedX = Math.max(playerRadius, Math.min(ARENA_WIDTH - playerRadius, newPlayerX));
        const clampedY = Math.max(playerRadius, Math.min(ARENA_HEIGHT - playerRadius, newPlayerY));

        // Duration based on distance, but compressed (fast slide, not slow drift)
        // ~100-150ms feels punchy - enough to see the movement but not sluggish
        const knockbackDuration = Math.min(150, Math.max(80, kb.force * 1.5));

        // Set knockback state - player will animate to destination
        newState = {
          ...newState,
          player: {
            ...newState.player,
            knockback: {
              startPos: { ...newState.player.position },
              endPos: { x: clampedX, y: clampedY },
              startTime: newState.gameTime,
              duration: knockbackDuration,
            },
          },
        };

        // Visual feedback for knockback - emit damage particles
        juiceSystem.emitDamage(newState.player.position, Math.ceil(kb.force / 50));

        // Screen shake for heavy hits
        if (kb.force >= 100) {
          juiceSystem.triggerShake(kb.force / 20, 150);
        }

        // RUN 038: Play sound effects for each knockback source
        // Even though player slides to final position, each hit plays its sound
        for (const source of ballResult.knockbackSources) {
          // Emit knockback sound event based on source type
          const knockbackEventType = source.type === 'lunge' ? 'lunge_hit' :
                                     source.type === 'boundary' ? 'boundary_touch' :
                                     'outside_punch';
          callbacks.onBallEvent?.({
            type: knockbackEventType,
            timestamp: newState.gameTime,
            position: newState.player.position,
            data: {
              knockbackForce: source.force,
              knockbackDirection: source.direction,
            },
          });
        }

        const sourceTypes = ballResult.knockbackSources.map(s => s.type).join(' + ');
        console.log('[BALL] Player knockback started:', kb.force.toFixed(0), 'px over', knockbackDuration.toFixed(0), 'ms from:', sourceTypes);
      }

      // Apply formation positions to enemies (move bees into THE BALL)
      if (ballResult.state.phase !== 'inactive' && ballResult.state.formationPositions.size > 0) {
        const activeLunge = ballResult.state.activeLunge;

        newState = {
          ...newState,
          enemies: newState.enemies.map(enemy => {
            // Run 036: Special handling for lunging bee with phases
            if (activeLunge && enemy.id === activeLunge.beeId) {
              if (activeLunge.phase === 'windup') {
                // WINDUP: Bee pulls back slightly (anticipation)
                const windupElapsed = newState.gameTime - activeLunge.windupStartTime;
                const windupDuration = 350;  // Match BALL_CONFIG.lungeWindupDuration
                const windupProgress = Math.min(1, windupElapsed / windupDuration);

                // Pull back from formation position (opposite of lunge direction)
                const toLungeDx = activeLunge.targetPos.x - activeLunge.startPos.x;
                const toLungeDy = activeLunge.targetPos.y - activeLunge.startPos.y;
                const toLungeDist = Math.sqrt(toLungeDx * toLungeDx + toLungeDy * toLungeDy);

                if (toLungeDist > 1) {
                  // Pull back 15px in opposite direction
                  const pullbackX = activeLunge.startPos.x - (toLungeDx / toLungeDist) * 15 * windupProgress;
                  const pullbackY = activeLunge.startPos.y - (toLungeDy / toLungeDist) * 15 * windupProgress;

                  return {
                    ...enemy,
                    position: { x: pullbackX, y: pullbackY },
                  };
                }
              } else if (activeLunge.phase === 'lunge') {
                // LUNGE: Aggressive dash toward target
                const lungeElapsed = newState.gameTime - activeLunge.lungeStartTime;
                const lungeProgress = Math.min(1, lungeElapsed / activeLunge.duration);

                // Ease-out for aggressive, snappy lunge feel
                const easedProgress = 1 - Math.pow(1 - lungeProgress, 3);

                // Start from pullback position (-15px) to target
                const toLungeDx = activeLunge.targetPos.x - activeLunge.startPos.x;
                const toLungeDy = activeLunge.targetPos.y - activeLunge.startPos.y;
                const toLungeDist = Math.sqrt(toLungeDx * toLungeDx + toLungeDy * toLungeDy);

                if (toLungeDist > 1) {
                  const pullbackX = activeLunge.startPos.x - (toLungeDx / toLungeDist) * 15;
                  const pullbackY = activeLunge.startPos.y - (toLungeDy / toLungeDist) * 15;

                  const lungeX = pullbackX + (activeLunge.targetPos.x - pullbackX) * easedProgress;
                  const lungeY = pullbackY + (activeLunge.targetPos.y - pullbackY) * easedProgress;

                  return {
                    ...enemy,
                    position: { x: lungeX, y: lungeY },
                  };
                }
              } else if (activeLunge.phase === 'return') {
                // RETURN: Bee returns to formation position (slower)
                const returnElapsed = newState.gameTime - activeLunge.lungeStartTime;
                const returnDuration = activeLunge.duration * 1.5;
                const returnProgress = Math.min(1, returnElapsed / returnDuration);

                // Ease-in for smooth return
                const easedProgress = returnProgress * returnProgress;

                const returnX = activeLunge.targetPos.x + (activeLunge.startPos.x - activeLunge.targetPos.x) * easedProgress;
                const returnY = activeLunge.targetPos.y + (activeLunge.startPos.y - activeLunge.targetPos.y) * easedProgress;

                return {
                  ...enemy,
                  position: { x: returnX, y: returnY },
                };
              }
            }

            const targetPos = ballResult.state.formationPositions.get(enemy.id);
            if (!targetPos) return enemy;

            // Smoothly move toward formation position
            const dx = targetPos.x - enemy.position.x;
            const dy = targetPos.y - enemy.position.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < 2) {
              // Already at position
              return { ...enemy, position: targetPos };
            }

            // Move toward target (faster in later phases)
            const speed = ballResult.state.phase === 'forming' ? 3 : 5;
            const moveX = (dx / dist) * Math.min(speed, dist);
            const moveY = (dy / dist) * Math.min(speed, dist);

            return {
              ...enemy,
              position: {
                x: enemy.position.x + moveX,
                y: enemy.position.y + moveY,
              },
            };
          }),
        };
      }

      perfMonitor.endSystem('formation');

      // =======================================================================
      // PHASE 5: Level Up Check
      // =======================================================================
      if (newState.player.xp >= newState.player.xpToNextLevel) {
        // Level up!
        const newLevel = newState.player.level + 1;
        const xpOverflow = newState.player.xp - newState.player.xpToNextLevel;
        const newXpRequired = Math.floor(newState.player.xpToNextLevel * 1.5);

        // Generate upgrade choices (DD-6: verb-based upgrades)
        const choices = generateUpgradeChoicesForState(newState);

        // Only pause for upgrade selection if there are choices available
        // When all upgrades are owned, skip the upgrade UI and continue playing
        const shouldPause = choices.length > 0;

        newState = {
          ...newState,
          status: shouldPause ? 'upgrade' : 'playing',
          player: {
            ...newState.player,
            level: newLevel,
            xp: xpOverflow,
            xpToNextLevel: newXpRequired,
          },
        };

        // Emit level up juice (DD-5: level-up = pause + fanfare)
        juiceSystem.emitLevelUp(newLevel);

        // Part VII: Trigger level up voice line
        const levelUpLine = triggerVoiceLine(emotionalStateRef.current, 'level_up', newState.gameTime);
        if (levelUpLine) callbacks.onVoiceLine?.(levelUpLine);

        // Record for ghost system
        emitWitnessMark(witnessContextRef.current, {
          type: 'level_up',
          gameTime: newState.gameTime,
          context: buildWitnessContext(newState),
          level: newLevel,
          choices,
        });

        // Only show upgrade UI if there are choices
        if (shouldPause) {
          callbacks.onLevelUp(newState, choices);
        }
      }

      // =======================================================================
      // PHASE 6: Update Game Time
      // =======================================================================
      newState = {
        ...newState,
        gameTime: newState.gameTime + deltaTime,
      };

      // =======================================================================
      // PHASE 6.5: Graze Frenzy Stack Decay (DISABLED)
      // =======================================================================
      // GRAZE FRENZY: System preserved but surface disabled - no stack tracking needed

      // =======================================================================
      // PHASE 7: Process Juice System
      // =======================================================================
      perfMonitor.beginSystem('particles');
      processJuice(juiceSystem, deltaTime, newState);
      perfMonitor.endSystem('particles');

      // =======================================================================
      // PHASE 7.5: Update Emotional State (Part VI: Arc Grammar)
      // =======================================================================
      // Order matters: combat -> juice -> contrast (effects flow upward)
      const emotionalResult = updateEmotionalState(emotionalStateRef.current, newState);
      emotionalStateRef.current = emotionalResult.state;

      // Emit emotional events
      for (const event of emotionalResult.events) {
        callbacks.onEmotionalEvent?.(event);

        // Handle specific event types
        if (event.type === 'voice_line' && event.data.line) {
          callbacks.onVoiceLine?.(event.data.line);
        }
        if (event.type === 'phase_transition' && event.data.phase) {
          callbacks.onPhaseTransition?.(event.data.phase);
        }
      }

      // Update emotional state callback
      callbacks.onEmotionalStateUpdate?.(emotionalStateRef.current);

      // =======================================================================
      // PHASE 8: Emit State Update
      // =======================================================================
      stateRef.current = newState;
      callbacks.onStateUpdate(newState);

      // =======================================================================
      // PHASE 9: End Frame Performance Timing
      // =======================================================================
      const perfMetrics = perfMonitor.endFrame({
        enemies: newState.enemies.length,
        particles: juiceSystem.particles?.length ?? 0,
        projectiles: 0,  // No projectiles in current implementation
      });
      callbacks.onPerformanceMetrics?.(perfMetrics);

      // Schedule next frame
      animationFrameRef.current = requestAnimationFrame(tick);
    },
    [inputRef, callbacks, juiceSystem]
  );

  // Start the game loop
  const start = useCallback(() => {
    if (isRunningRef.current) return;

    isRunningRef.current = true;
    isPausedRef.current = false;
    lastTimeRef.current = 0;

    // Initialize witness context for new run
    witnessContextRef.current = {
      runId: `run-${Date.now()}`,
      marks: [],
      ghosts: [],
      startTime: Date.now(),
      pendingIntents: new Map(),
    };

    // Reset combat state for new run
    combatStateRef.current = createInitialCombatState();
    wasDashingRef.current = false;

    // Reset emotional state for new run (Part VI: fresh arc)
    emotionalStateRef.current = createEmotionalState();

    // Reset axiom guardian state for new run (Part I: Four True Axioms)
    axiomGuardianRef.current = createGuardianState();

    // Reset colony intelligence for new run (Part XI Phase 4: The Superorganism)
    // Colony learns fresh each run - "They earned this kill"
    colonyIntelligenceRef.current = null;
    dashStartPositionRef.current = null;

    // Reset graze frenzy state for new run
    grazeFrenzyRef.current = {
      stacks: 0,
      lastGrazeTime: 0,
      grazedEnemyIds: new Map(),
    };

    // Reset apex strike state for new run (Run 036: The hornet's predator dash)
    apexStrikeRef.current = createInitialApexState();

    animationFrameRef.current = requestAnimationFrame(tick);
  }, [tick]);

  // Stop the game loop completely
  const stop = useCallback(() => {
    isRunningRef.current = false;
    isPausedRef.current = false;
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  }, []);

  // Pause (keep loop running but don't process)
  const pause = useCallback(() => {
    isPausedRef.current = true;
  }, []);

  // Resume from pause
  const resume = useCallback(() => {
    isPausedRef.current = false;
    lastTimeRef.current = 0; // Reset delta to prevent time jump
  }, []);

  // Reset game state
  const reset = useCallback(() => {
    stateRef.current = initialState;
    witnessContextRef.current = {
      runId: `run-${Date.now()}`,
      marks: [],
      ghosts: [],
      startTime: Date.now(),
      pendingIntents: new Map(),
    };
    // Reset combat state
    combatStateRef.current = createInitialCombatState();
    wasDashingRef.current = false;
    // Reset emotional state
    emotionalStateRef.current = createEmotionalState();
    // Reset axiom guardian state
    axiomGuardianRef.current = createGuardianState();
    // Reset colony intelligence state
    colonyIntelligenceRef.current = null;
    dashStartPositionRef.current = null;
    // Reset abilities/melee/combos state (Run 036)
    abilitiesRef.current = createInitialAbilities();
    meleeStateRef.current = createInitialMeleeState();
    comboStateRef.current = createInitialComboState();
    runNumberRef.current++;  // Increment run number for combo discovery tracking
    // Reset apex strike state (Run 036: The hornet's predator dash)
    apexStrikeRef.current = createInitialApexState();
    // Reset graze frenzy state
    grazeFrenzyRef.current = {
      stacks: 0,
      lastGrazeTime: 0,
      grazedEnemyIds: new Map(),
    };
  }, [initialState]);

  // Set game state directly (for starting with specific state)
  const setState = useCallback((state: GameState) => {
    stateRef.current = state;
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  // Force THE BALL to start forming (debug/testing)
  const forceBall = useCallback(() => {
    const state = stateRef.current;
    if (state.status !== 'playing') {
      console.log('[BALL] Cannot force - game not playing');
      return;
    }

    // Create a new ball with the manager's next ID
    const manager = ballManagerRef.current;
    const newBallState = forceBallStart(
      createBallState(manager.nextBallId, 1),
      state.player.position,
      state.enemies,
      state.gameTime
    );

    // Add to manager
    ballManagerRef.current = {
      ...manager,
      balls: [...manager.balls.filter(b => b.phase !== 'inactive'), newBallState],
      nextBallId: manager.nextBallId + 1,
    };
    ballStateRef.current = newBallState;

    // Notify listeners
    callbacks.onBallStateUpdate?.(newBallState);
  }, [callbacks]);

  // Get current BALL state
  const getBallState = useCallback(() => {
    return ballStateRef.current;
  }, []);

  // =======================================================================
  // Abilities/Melee/Combos Controls (Run 036)
  // =======================================================================

  /**
   * Select an ability when leveling up
   * This adds the ability, tracks order for combos, and checks for new combos
   */
  const selectAbility = useCallback((abilityId: AbilityId) => {
    // Add ability to player's active abilities
    abilitiesRef.current = addAbility(abilitiesRef.current, abilityId);

    // Track ability order for order-dependent combos
    comboStateRef.current = trackAbilityOrder(comboStateRef.current, abilityId);

    // Check for new combos
    const { newCombos } = checkForCombos(
      abilitiesRef.current,
      comboStateRef.current,
      runNumberRef.current,
      Date.now()
    );

    // Apply any discovered combos
    for (const combo of newCombos) {
      comboStateRef.current = applyComboDiscovery(
        comboStateRef.current,
        combo,
        runNumberRef.current
      );
      callbacks.onComboDiscovered?.(combo);
    }

    // Notify listeners
    callbacks.onAbilitiesUpdate?.(abilitiesRef.current);
    callbacks.onComboStateUpdate?.(comboStateRef.current);

    // Log for debugging
    if (process.env.NODE_ENV === 'development') {
      console.log('[ABILITIES] Selected:', abilityId);
      console.log('[ABILITIES] Owned:', abilitiesRef.current.owned);
      if (newCombos.length > 0) {
        console.log('[COMBOS] Discovered:', newCombos.map(c => c.name));
      }
    }
  }, [callbacks]);

  /**
   * Get current abilities state
   */
  const getAbilities = useCallback(() => {
    return abilitiesRef.current;
  }, []);

  /**
   * Get current combo state
   */
  const getComboState = useCallback(() => {
    return comboStateRef.current;
  }, []);

  /**
   * Get current melee attack state
   */
  const getMeleeState = useCallback(() => {
    return meleeStateRef.current;
  }, []);

  /**
   * Get current apex strike state
   */
  const getApexState = useCallback(() => {
    return apexStrikeRef.current;
  }, []);

  /**
   * Get all ball states (for multi-ball rendering)
   */
  const getAllBalls = useCallback((): BallState[] => {
    // Return array of all ball states from ball manager
    return ballManagerRef.current.balls || [ballStateRef.current];
  }, []);

  /**
   * Get attack cooldown percent (for UI visualization)
   */
  const getAttackCooldownPercent = useCallback((): number => {
    const melee = meleeStateRef.current;
    if (!melee.recoveryEndTime || melee.recoveryEndTime === 0) return 1;
    const now = Date.now();
    const cooldownStart = melee.recoveryEndTime - effectiveCooldownRef.current;
    if (now >= melee.recoveryEndTime) return 1;
    return (now - cooldownStart) / effectiveCooldownRef.current;
  }, []);

  /**
   * Get current kill streak count
   */
  const getKillStreak = useCallback((): number => {
    return killStreakRef.current;
  }, []);

  /**
   * Check if next attack will be a double strike
   */
  const isDoubleStrikeReady = useCallback((): boolean => {
    return nextAttackDoubleStrikeRef.current;
  }, []);

  /**
   * Get current territorial marks (kill zones that grant damage bonus)
   */
  const getTerritorialMarks = useCallback((): TerritorialMark[] => {
    return territorialMarksRef.current;
  }, []);

  /**
   * Get current death markers (corpse locations for abilities)
   */
  const getDeathMarkers = useCallback((): DeathMarker[] => {
    return deathMarkersRef.current;
  }, []);

  return {
    start,
    stop,
    pause,
    resume,
    reset,
    setState,
    isRunning: isRunningRef.current,
    forceBall,
    getBallState,
    getAllBalls,
    selectAbility,
    getAbilities,
    getComboState,
    getMeleeState,
    getApexState,
    getAttackCooldownPercent,
    getKillStreak,
    isDoubleStrikeReady,
    getTerritorialMarks,
    getDeathMarkers,
  };
}

// =============================================================================
// Helpers
// =============================================================================

function buildWitnessContext(state: GameState): {
  wave: number;
  health: number;
  maxHealth: number;
  upgrades: string[];
  synergies: string[];
  xp: number;
  enemiesKilled: number;
} {
  return {
    wave: state.wave,
    health: state.player.health,
    maxHealth: state.player.maxHealth,
    upgrades: state.player.upgrades,
    synergies: state.player.synergies ?? [],
    xp: state.player.xp,
    enemiesKilled: state.totalEnemiesKilled,
  };
}

function generateUpgradeChoicesForState(state: GameState): string[] {
  // Use the new abilities system (Run 036: simplified abilities)
  const ownedAbilities = state.player.upgrades as AbilityId[];
  // Create a minimal ActiveAbilities for choice generation
  const mockAbilities: ActiveAbilities = {
    owned: ownedAbilities,
    levels: {} as Record<AbilityId, number>,
    computed: {} as ComputedEffects,
    runtime: {
      sawtoothCounter: 0,
      trophyScentKills: 0,
      updraftSpeedBonus: 0,
      updraftExpiry: 0,
      aggroPulseLastTime: 0,
      moltingBurstUsed: false,
      ablativeShellUsed: false,
      confusionClouds: [],
      deathMarkers: [],
      bitterTasteDebuffs: new Map(),
      heatRetentionActive: false,
    },
  };
  // generateAbilityChoices returns AbilityId[] directly
  return generateAbilityChoices(mockAbilities, 3);
}

// Re-export axiom types for consumers
export type { AxiomGuardReport } from '../systems/axiom-guards';

export default useGameLoop;
