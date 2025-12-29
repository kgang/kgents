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
  type AbilityId,
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
  executeStrike,
  checkStrikeHit,
  attemptChain,
  updateApexStrike,
  isStriking,
  isLocking,
  APEX_CONFIG,
} from '../systems/apex-strike';

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
  // Abilities/Combos controls (Run 036)
  selectAbility: (abilityId: AbilityId) => void;
  getAbilities: () => ActiveAbilities;
  getComboState: () => ComboState;
  getMeleeState: () => MeleeAttackState;
  // Apex Strike controls (Run 036: The hornet's predator dash)
  getApexState: () => ApexStrikeState;
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

  // Apex Strike state (Run 036: The hornet's signature predator dash)
  // "The hornet doesn't dash - it HUNTS. The strike is commitment."
  const apexStrikeRef = useRef<ApexStrikeState>(createInitialApexState());

  // Venom Architect state (Special Ability: Infinite venom stacks, explode on venom-kill)
  // Map of enemyId -> VenomArchitectState
  const venomArchitectRef = useRef<Map<string, VenomArchitectState>>(new Map());

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

  // Graze Frenzy constants
  const GRAZE_FRENZY = {
    NEAR_MISS_DISTANCE: 10,      // Pixels - attack must pass within this distance WITHOUT hitting
    ATTACK_SPEED_PER_STACK: 0.05, // +5% attack speed per stack
    DAMAGE_PER_STACK: 0.03,       // +3% damage per stack
    MAX_STACKS: 20,               // Maximum stacks
    DECAY_RATE: 1,                // Stacks lost per second if not grazing
    GRAZE_COOLDOWN: 500,          // ms - cooldown per enemy before they can grant another stack
  };

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
          playerVelocity.x = (playerVelocity.x / magnitude) * knockbackHandledState.player.moveSpeed;
          playerVelocity.y = (playerVelocity.y / magnitude) * knockbackHandledState.player.moveSpeed;
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
        const holdDuration = apexInput.spaceHoldDuration ?? 0;

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
          const dirResult = updateLockDirection(apexStrikeRef.current, aimDir);
          apexStrikeRef.current = dirResult.state;

          // Calculate charge-based distance (min 60px, max 360px based on hold time)
          // Full charge at 500ms hold time
          const chargePercent = Math.min(1, holdDuration / 500);
          const minDistance = 60;
          const maxDistance = APEX_CONFIG.strikeDistance;
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

          // If we hit an enemy, apply damage
          if (hitResult.hitEnemy) {
            // Emit hit events
            for (const event of hitResult.events) {
              callbacks.onApexEvent?.(event);
            }

            // Emit hit visual effects
            juiceSystem.emitApexHit?.(
              dashState.player.position,
              hitResult.damage,
              hitResult.state.canChain
            );

            // A3: Record damage dealt
            recordDamageDealt(axiomGuardianRef.current, hitResult.damage);

            // Apply damage to enemy
            const hitEnemyId = hitResult.hitEnemy.id;
            const hitEnemyData = dashState.enemies.find(e => e.id === hitEnemyId);
            const enemyWasKilled = hitEnemyData ? hitEnemyData.health <= hitResult.damage : false;

            apexState = {
              ...dashState,
              enemies: dashState.enemies.map(e => {
                if (e.id === hitEnemyId) {
                  const newHealth = e.health - hitResult.damage;
                  if (newHealth <= 0) {
                    // Enemy killed - emit kill events
                    juiceSystem.emitKill(e.position, e.type);
                    callbacks.onEnemyKilled?.(e.type, 'single', 1, e.position);
                  }
                  return { ...e, health: newHealth };
                }
                return e;
              }).filter(e => e.health > 0),
              totalEnemiesKilled: enemyWasKilled
                ? dashState.totalEnemiesKilled + 1
                : dashState.totalEnemiesKilled,
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

      // During STRIKE phase: use apex strike velocity exclusively
      // apexVelocity is only non-null when actively striking (from updateApexStrike)
      if (apexVelocity && currentApexPhase === 'strike') {
        finalVelocity = apexVelocity;
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

        // GRAZE FRENZY: Reset ALL stacks when player takes damage
        if (abilitiesRef.current.computed.hasGrazeFrenzy && grazeFrenzyRef.current.stacks > 0) {
          console.log('[GRAZE FRENZY] Player HIT! Resetting', grazeFrenzyRef.current.stacks, 'stacks to 0');
          grazeFrenzyRef.current.stacks = 0;
          grazeFrenzyRef.current.grazedEnemyIds.clear();
        }

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
            break;
          }

          case 'player_hit': {
            // Appendix D: Check hover brake invulnerability
            if (isHoverBrakeInvulnerable(combatStateRef.current, newState.gameTime)) {
              // CLUTCH DODGE! A3: Attack was evaded
              recordAttackEncounter(axiomGuardianRef.current, true);
              break;
            }

            // A3: Record attack encounter (not evaded - player took damage)
            recordAttackEncounter(axiomGuardianRef.current, false);
            const damageAmount = event.damage ?? 10;
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

            // GRAZE FRENZY: Reset ALL stacks when player takes damage
            if (abilitiesRef.current.computed.hasGrazeFrenzy && grazeFrenzyRef.current.stacks > 0) {
              console.log('[GRAZE FRENZY] Player HIT (contact)! Resetting', grazeFrenzyRef.current.stacks, 'stacks to 0');
              grazeFrenzyRef.current.stacks = 0;
              grazeFrenzyRef.current.grazedEnemyIds.clear();
            }

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
          // RISK-TAKING REWARDED: Emit graze spark particles
          juiceSystem.emitGrazeSpark(
            newState.player.position,
            event.position,
            event.chainCount
          );

          // GRAZE FRENZY: Increment stacks on graze (if ability is active)
          if (abilitiesRef.current.computed.hasGrazeFrenzy) {
            const gf = grazeFrenzyRef.current;
            if (gf.stacks < GRAZE_FRENZY.MAX_STACKS) {
              gf.stacks++;
              gf.lastGrazeTime = newState.gameTime;
              console.log('[GRAZE FRENZY] Graze! Stacks:', gf.stacks, '/', GRAZE_FRENZY.MAX_STACKS,
                '| +' + (gf.stacks * GRAZE_FRENZY.ATTACK_SPEED_PER_STACK * 100).toFixed(0) + '% ATK SPD,',
                '+' + (gf.stacks * GRAZE_FRENZY.DAMAGE_PER_STACK * 100).toFixed(0) + '% DMG');

              // Trigger graze sound callback
              callbacks.onGraze?.(gf.stacks);
            }
          }
        } else if (event.type === 'graze_bonus_triggered') {
          // Graze chain complete: +10% DAMAGE bonus ring effect
          juiceSystem.emitGrazeBonus(newState.player.position);
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

      // GRAZE FRENZY: Apply stacking bonuses to attack speed and damage
      if (abilitiesRef.current.computed.hasGrazeFrenzy && grazeFrenzyRef.current.stacks > 0) {
        const stacks = grazeFrenzyRef.current.stacks;
        const attackSpeedBonus = stacks * GRAZE_FRENZY.ATTACK_SPEED_PER_STACK;
        const damageBonus = stacks * GRAZE_FRENZY.DAMAGE_PER_STACK;

        meleeConfig = {
          ...meleeConfig,
          // Reduce cooldown based on attack speed bonus (1 / (1 + bonus))
          cooldown: Math.max(100, meleeConfig.cooldown / (1 + attackSpeedBonus)),
          // Increase damage based on damage bonus
          baseDamage: Math.floor(meleeConfig.baseDamage * (1 + damageBonus)),
        };
      }

      // Auto-attack: Check if player can start a new attack
      if (canAttack(meleeStateRef.current, currentTime, meleeConfig)) {
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
          meleeConfig
        );

        // Apply damage to enemies and handle kills
        let meleeModifiedEnemies = [...newState.enemies];
        const meleeKills: Array<{
          enemy: typeof newState.enemies[0];
          position: { x: number; y: number };
          healthPercentBeforeKill: number;  // For execution chain check
        }> = [];

        // Check if player has Venom Architect ability
        const hasVenomArchitect = abilitiesRef.current?.owned.includes('venom_architect') ?? false;

        for (const hit of meleeResult.hits) {
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

        // Remove dead enemies and process kills
        const survivingEnemies = meleeModifiedEnemies.filter(e => e.health > 0);

        // Process each kill (XP, score, juice, callbacks)
        for (const kill of meleeKills) {
          const xpValue = kill.enemy.xpValue ?? 10;

          // DD-12: Vampiric - heal on kill (now uses ability lifesteal)
          const lifestealPercent = abilitiesRef.current?.computed.lifestealPercent ?? 0;
          let newHealth = newState.player.health;
          if (lifestealPercent > 0) {
            const healAmount = Math.floor(newState.player.maxHealth * (lifestealPercent / 100));
            newHealth = Math.min(newState.player.maxHealth, newState.player.health + healAmount);
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
          juiceSystem.emitKill(kill.position, kill.enemy.type);

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
        }

        // Update enemies with survivors only
        newState = {
          ...newState,
          enemies: survivingEnemies,
        };

        // Update melee state
        meleeStateRef.current = meleeResult.newState;

        // =======================================================================
        // EXECUTION CHAIN MECHANIC
        // When killing an enemy below 20% HP with melee and hasExecutionChain:
        // 1. Instantly refresh attack cooldown
        // 2. Dash to nearest enemy below 30% HP (within ~50px)
        // =======================================================================
        const hasExecutionChain = abilitiesRef.current?.computed.hasExecutionChain ?? false;
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
      // PHASE 3.7: Thermal Momentum (Run 042: Movement-based heat mechanic)
      // =======================================================================
      // "Build heat while moving. Stop to release a damage pulse."
      if (abilitiesRef.current.computed.hasThermalMomentum) {
        const thermal = thermalMomentumRef.current;
        const currentPos = newState.player.position;

        // Calculate velocity magnitude from playerVelocity
        const velocityMag = Math.sqrt(playerVelocity.x * playerVelocity.x + playerVelocity.y * playerVelocity.y);
        const isMoving = velocityMag > THERMAL_MOMENTUM.VELOCITY_THRESHOLD;

        if (isMoving) {
          // Player is moving - build heat
          if (thermal.lastPosition) {
            const dx = currentPos.x - thermal.lastPosition.x;
            const dy = currentPos.y - thermal.lastPosition.y;
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
      // Only runs if player has the venom_architect ability
      const hasVenomArchitectAbility = abilitiesRef.current?.owned.includes('venom_architect') ?? false;

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
      // Multiple knockback sources (e.g., punch + boundary) combine into one slide to final position
      if (ballResult.knockback && !newState.player.knockback) {
        const kb = ballResult.knockback;

        // Calculate knockback destination
        const newPlayerX = newState.player.position.x + kb.direction.x * kb.force;
        const newPlayerY = newState.player.position.y + kb.direction.y * kb.force;

        // Clamp to arena bounds
        const playerRadius = newState.player.radius ?? 12;
        const clampedX = Math.max(playerRadius, Math.min(800 - playerRadius, newPlayerX));
        const clampedY = Math.max(playerRadius, Math.min(600 - playerRadius, newPlayerY));

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
      // PHASE 6.5: Graze Frenzy Stack Decay
      // =======================================================================
      // Stacks decay 1 per second if not actively grazing
      if (abilitiesRef.current.computed.hasGrazeFrenzy) {
        const gf = grazeFrenzyRef.current;
        if (gf.stacks > 0) {
          const timeSinceLastGraze = newState.gameTime - gf.lastGrazeTime;
          // Decay 1 stack per second (1000ms)
          const expectedStacks = gf.stacks - Math.floor(timeSinceLastGraze / 1000);
          const newStacks = Math.max(0, expectedStacks);

          if (newStacks < gf.stacks) {
            console.log('[GRAZE FRENZY] Stack decay:', gf.stacks, '->', newStacks);
            gf.stacks = newStacks;
            if (newStacks === 0) {
              gf.grazedEnemyIds.clear();
            }
          }
        }
      }

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
    selectAbility,
    getAbilities,
    getComboState,
    getMeleeState,
    getApexState,
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
  const mockAbilities = {
    owned: ownedAbilities,
    levels: {} as Record<AbilityId, number>,
    computed: {} as any, // Not needed for choice generation
  };
  // generateAbilityChoices returns AbilityId[] directly
  return generateAbilityChoices(mockAbilities, 3);
}

// Re-export axiom types for consumers
export type { AxiomGuardReport } from '../systems/axiom-guards';

export default useGameLoop;
