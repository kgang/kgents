/**
 * WASM Survivors - Combat System (Appendix D Mechanics)
 *
 * Core combat mechanics that create MOMENTS, not just damage numbers.
 * Every mechanic here should make players say "holy shit" or "that was CLOSE."
 *
 * Priority 1 (Core Combat Feel):
 * - Venom Stacking: 3 stacks = 1.5s paralysis (TRAP SPRINGING)
 * - Bleeding DoT: 5 DPS x 5 stacks, 8s duration (WATCH THEM BLEED)
 * - Berserker Aura: +5% per nearby enemy (SWARMS MAKE YOU STRONGER)
 * - Hover Brake: 0.3s invuln on instant stop (CLUTCH DODGES)
 *
 * Priority 2 (Risk-Reward):
 * - Execute Threshold: +50% below 25% HP (SETUP -> PAYOFF)
 * - Revenge Buff: +25% damage for 3s after hit (AGGRESSION REWARDED)
 * - Graze Bonus: 30px zone, 5 grazes = +10% (RISK-TAKING REWARDED)
 * - Afterimage Dash: 8 damage per image (SPEED IS YOUR WEAPON)
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md Appendix D
 */

import type { Enemy, Vector2, Player } from '../types';

// =============================================================================
// Combat Constants (Appendix D - Exact Values)
// =============================================================================

/** Venom Stacking - 3 hits = paralysis */
export const VENOM = {
  STACKS_FOR_PARALYSIS: 3,
  STACK_DURATION_MS: 4000,    // 4 seconds per stack
  PARALYSIS_DURATION_MS: 1500, // 1.5 seconds freeze
  COLOR_PER_STACK: ['#7B3F9D', '#9B4FBD', '#BB5FDD'], // Purple gradient
} as const;

/** Bleeding DoT - stacking damage over time */
export const BLEED = {
  DAMAGE_PER_SECOND: 5,
  MAX_STACKS: 5,
  DURATION_MS: 8000,          // 8 seconds
  COLOR: '#CC0000',           // Crimson
  TICK_INTERVAL_MS: 200,      // Tick every 200ms for smooth damage
} as const;

/** Berserker Aura - power from proximity danger */
export const BERSERKER = {
  RANGE_PX: 200,
  DAMAGE_BONUS_PER_ENEMY: 0.05, // +5% per nearby enemy
  MAX_BONUS: 0.50,              // Cap at +50%
  COLOR_GLOW: '#FF4400',        // Fiery orange
} as const;

/** Hover Brake - instant stop with i-frames */
export const HOVER_BRAKE = {
  INVULN_DURATION_MS: 300,     // 0.3 seconds
  COOLDOWN_MS: 3000,           // 3 seconds
  ACTIVATION_THRESHOLD: 0.1,   // Velocity magnitude threshold to detect "stop"
  FLASH_COLOR: '#00FFFF',      // Cyan flash
} as const;

/** Execute Threshold - bonus damage to wounded enemies */
export const EXECUTE = {
  HP_THRESHOLD: 0.25,         // Below 25% HP
  DAMAGE_MULTIPLIER: 1.5,     // +50% damage
  INDICATOR_COLOR: '#FF0000', // Red skull indicator
} as const;

/** Revenge Buff - getting hit makes you stronger */
export const REVENGE = {
  DAMAGE_BONUS: 0.25,         // +25% damage
  DURATION_MS: 3000,          // 3 seconds
  COLOR: '#FF3366',           // Pinkish-red aura (distinct from player orange)
} as const;

/** Graze Bonus - near-miss rewards */
export const GRAZE = {
  ZONE_PX: 15,                // 15px near-miss zone (was 30 - now tighter!)
  GRAZES_FOR_BONUS: 5,        // 5 consecutive grazes
  DAMAGE_BONUS: 0.10,         // +10% damage
  DECAY_TIME_MS: 400,         // Reset chain after 0.4s without graze (Run 038: faster reset)
  COOLDOWN_MS: 500,           // 500ms cooldown per enemy before re-triggering
  SPARK_COLOR: '#00FFFF',     // Cyan spark
} as const;

/** Afterimage Dash - speed creates damage */
export const AFTERIMAGE = {
  DAMAGE_PER_IMAGE: 8,
  SPAWN_INTERVAL_MS: 100,     // 0.1s between images
  IMAGE_DURATION_MS: 300,     // Images linger for 0.3s
  IMAGE_COLOR: '#00D4FF80',   // Semi-transparent cyan
} as const;

// =============================================================================
// Combat State Types
// =============================================================================

/** Venom state on an enemy */
export interface VenomState {
  stacks: number;
  stackTimestamps: number[];  // When each stack was applied
  isParalyzed: boolean;
  paralysisEndTime: number;
}

/** Bleed state on an enemy */
export interface BleedState {
  stacks: number;
  applicationTime: number;    // When most recent stack was applied
  lastTickTime: number;       // For damage ticks
}

/** Player combat state */
export interface PlayerCombatState {
  // Berserker
  nearbyEnemyCount: number;
  berserkerBonus: number;

  // Hover Brake
  hoverBrakeActive: boolean;
  hoverBrakeEndTime: number;
  hoverBrakeCooldownEnd: number;
  previousVelocity: Vector2;

  // Revenge
  revengeActive: boolean;
  revengeEndTime: number;

  // Graze
  grazeChain: number;
  lastGrazeTime: number;
  grazeBonus: number;
  grazeCooldowns: Map<string, number>;  // enemyId -> cooldown end time

  // Afterimage
  afterimages: Afterimage[];
  lastAfterimageTime: number;
  isDashing: boolean;
}

/** Single afterimage for damage trail */
export interface Afterimage {
  id: string;
  position: Vector2;
  spawnTime: number;
  damage: number;
  hasDealtDamage: Set<string>; // Enemy IDs already hit
}

/** Extended enemy with combat state */
export interface EnemyWithCombat extends Enemy {
  venomState?: VenomState;
  bleedState?: BleedState;
}

// =============================================================================
// Combat State Factory
// =============================================================================

/**
 * Create initial player combat state
 */
export function createInitialCombatState(): PlayerCombatState {
  return {
    nearbyEnemyCount: 0,
    berserkerBonus: 0,
    hoverBrakeActive: false,
    hoverBrakeEndTime: 0,
    hoverBrakeCooldownEnd: 0,
    previousVelocity: { x: 0, y: 0 },
    revengeActive: false,
    revengeEndTime: 0,
    grazeChain: 0,
    lastGrazeTime: 0,
    grazeBonus: 0,
    grazeCooldowns: new Map(),
    afterimages: [],
    lastAfterimageTime: 0,
    isDashing: false,
  };
}

/**
 * Create initial venom state for enemy
 */
export function createInitialVenomState(): VenomState {
  return {
    stacks: 0,
    stackTimestamps: [],
    isParalyzed: false,
    paralysisEndTime: 0,
  };
}

/**
 * Create initial bleed state for enemy
 */
export function createInitialBleedState(): BleedState {
  return {
    stacks: 0,
    applicationTime: 0,
    lastTickTime: 0,
  };
}

// =============================================================================
// Venom System
// =============================================================================

/**
 * Apply a venom stack to an enemy
 * Returns updated venom state and whether paralysis was triggered
 */
export function applyVenomStack(
  venomState: VenomState | undefined,
  gameTime: number
): { state: VenomState; paralysisTriggered: boolean } {
  const state = venomState ?? createInitialVenomState();

  // Don't stack while paralyzed
  if (state.isParalyzed && gameTime < state.paralysisEndTime) {
    return { state, paralysisTriggered: false };
  }

  // Clear expired stacks
  const activeStacks = state.stackTimestamps.filter(
    t => gameTime - t < VENOM.STACK_DURATION_MS
  );

  // Add new stack
  activeStacks.push(gameTime);

  // Check for paralysis trigger
  const paralysisTriggered = activeStacks.length >= VENOM.STACKS_FOR_PARALYSIS;

  if (paralysisTriggered) {
    // TRAP SPRINGING MOMENT!
    return {
      state: {
        stacks: 0,
        stackTimestamps: [],
        isParalyzed: true,
        paralysisEndTime: gameTime + VENOM.PARALYSIS_DURATION_MS,
      },
      paralysisTriggered: true,
    };
  }

  return {
    state: {
      ...state,
      stacks: activeStacks.length,
      stackTimestamps: activeStacks,
      isParalyzed: false,
    },
    paralysisTriggered: false,
  };
}

/**
 * Update venom state (called every frame)
 * Returns whether the enemy should be frozen
 */
export function updateVenomState(
  venomState: VenomState | undefined,
  gameTime: number
): { state: VenomState; isFrozen: boolean } {
  if (!venomState) {
    return { state: createInitialVenomState(), isFrozen: false };
  }

  // Check paralysis expiry
  if (venomState.isParalyzed && gameTime >= venomState.paralysisEndTime) {
    return {
      state: {
        ...venomState,
        isParalyzed: false,
        paralysisEndTime: 0,
      },
      isFrozen: false,
    };
  }

  // Clear expired stacks
  const activeStacks = venomState.stackTimestamps.filter(
    t => gameTime - t < VENOM.STACK_DURATION_MS
  );

  return {
    state: {
      ...venomState,
      stacks: activeStacks.length,
      stackTimestamps: activeStacks,
    },
    isFrozen: venomState.isParalyzed,
  };
}

/**
 * Get venom visual color based on stack count
 */
export function getVenomColor(stacks: number): string {
  if (stacks <= 0) return 'transparent';
  const index = Math.min(stacks - 1, VENOM.COLOR_PER_STACK.length - 1);
  return VENOM.COLOR_PER_STACK[index];
}

// =============================================================================
// Bleeding DoT System
// =============================================================================

/**
 * Apply a bleed stack to an enemy
 */
export function applyBleedStack(
  bleedState: BleedState | undefined,
  gameTime: number
): BleedState {
  const state = bleedState ?? createInitialBleedState();

  // Check if existing bleed is expired
  const isExpired = gameTime - state.applicationTime > BLEED.DURATION_MS;
  const currentStacks = isExpired ? 0 : state.stacks;

  return {
    stacks: Math.min(currentStacks + 1, BLEED.MAX_STACKS),
    applicationTime: gameTime,
    lastTickTime: state.lastTickTime,
  };
}

/**
 * Update bleed state and calculate damage this frame
 * Returns updated state and damage to apply
 */
export function updateBleedState(
  bleedState: BleedState | undefined,
  gameTime: number
): { state: BleedState; damage: number } {
  if (!bleedState || bleedState.stacks <= 0) {
    return { state: createInitialBleedState(), damage: 0 };
  }

  // Check expiry
  if (gameTime - bleedState.applicationTime > BLEED.DURATION_MS) {
    return { state: createInitialBleedState(), damage: 0 };
  }

  // Check if we should tick
  const timeSinceLastTick = gameTime - bleedState.lastTickTime;
  if (timeSinceLastTick < BLEED.TICK_INTERVAL_MS) {
    return { state: bleedState, damage: 0 };
  }

  // Calculate damage for this tick
  // DPS * stacks / (1000 / tick_interval) = damage per tick
  const ticksPerSecond = 1000 / BLEED.TICK_INTERVAL_MS;
  const damagePerTick = (BLEED.DAMAGE_PER_SECOND * bleedState.stacks) / ticksPerSecond;

  return {
    state: {
      ...bleedState,
      lastTickTime: gameTime,
    },
    damage: damagePerTick,
  };
}

/**
 * Get bleed intensity for visual (0-1)
 */
export function getBleedIntensity(bleedState: BleedState | undefined): number {
  if (!bleedState || bleedState.stacks <= 0) return 0;
  return bleedState.stacks / BLEED.MAX_STACKS;
}

// =============================================================================
// Berserker Aura System
// =============================================================================

/**
 * Calculate berserker bonus based on nearby enemies
 */
export function calculateBerserkerBonus(
  playerPos: Vector2,
  enemies: Enemy[]
): { nearbyCount: number; bonus: number } {
  let nearbyCount = 0;

  for (const enemy of enemies) {
    const dx = enemy.position.x - playerPos.x;
    const dy = enemy.position.y - playerPos.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance <= BERSERKER.RANGE_PX) {
      nearbyCount++;
    }
  }

  const rawBonus = nearbyCount * BERSERKER.DAMAGE_BONUS_PER_ENEMY;
  const cappedBonus = Math.min(rawBonus, BERSERKER.MAX_BONUS);

  return {
    nearbyCount,
    bonus: cappedBonus,
  };
}

/**
 * Get berserker glow intensity (0-1 based on bonus)
 */
export function getBerserkerGlowIntensity(bonus: number): number {
  return bonus / BERSERKER.MAX_BONUS;
}

// =============================================================================
// Hover Brake System
// =============================================================================

/**
 * Check if hover brake should activate
 * Triggers when player rapidly decelerates
 */
export function checkHoverBrakeActivation(
  combatState: PlayerCombatState,
  currentVelocity: Vector2,
  gameTime: number
): { state: PlayerCombatState; activated: boolean } {
  // Check cooldown
  if (gameTime < combatState.hoverBrakeCooldownEnd) {
    return {
      state: {
        ...combatState,
        previousVelocity: currentVelocity,
      },
      activated: false,
    };
  }

  // Check if already active
  if (combatState.hoverBrakeActive) {
    // Check if it should end
    if (gameTime >= combatState.hoverBrakeEndTime) {
      return {
        state: {
          ...combatState,
          hoverBrakeActive: false,
          hoverBrakeCooldownEnd: gameTime + HOVER_BRAKE.COOLDOWN_MS,
          previousVelocity: currentVelocity,
        },
        activated: false,
      };
    }
    return {
      state: {
        ...combatState,
        previousVelocity: currentVelocity,
      },
      activated: false,
    };
  }

  // Calculate velocity magnitudes
  const prevMag = Math.sqrt(
    combatState.previousVelocity.x ** 2 + combatState.previousVelocity.y ** 2
  );
  const currMag = Math.sqrt(currentVelocity.x ** 2 + currentVelocity.y ** 2);

  // Check for sudden stop: was moving, now stopped
  const wasMoving = prevMag > 50; // Moving at reasonable speed
  const isStopped = currMag < HOVER_BRAKE.ACTIVATION_THRESHOLD;

  if (wasMoving && isStopped) {
    // CLUTCH DODGE MOMENT!
    return {
      state: {
        ...combatState,
        hoverBrakeActive: true,
        hoverBrakeEndTime: gameTime + HOVER_BRAKE.INVULN_DURATION_MS,
        previousVelocity: currentVelocity,
      },
      activated: true,
    };
  }

  return {
    state: {
      ...combatState,
      previousVelocity: currentVelocity,
    },
    activated: false,
  };
}

/**
 * Check if player is invulnerable from hover brake
 */
export function isHoverBrakeInvulnerable(
  combatState: PlayerCombatState,
  gameTime: number
): boolean {
  return combatState.hoverBrakeActive && gameTime < combatState.hoverBrakeEndTime;
}

// =============================================================================
// Execute Threshold System
// =============================================================================

/**
 * Check if enemy is in execute range
 */
export function isInExecuteRange(enemy: Enemy): boolean {
  return enemy.health / enemy.maxHealth <= EXECUTE.HP_THRESHOLD;
}

/**
 * Calculate execute damage multiplier
 */
export function getExecuteDamageMultiplier(enemy: Enemy): number {
  if (isInExecuteRange(enemy)) {
    return EXECUTE.DAMAGE_MULTIPLIER;
  }
  return 1.0;
}

// =============================================================================
// Revenge Buff System
// =============================================================================

/**
 * Trigger revenge buff when player takes damage
 */
export function triggerRevenge(
  combatState: PlayerCombatState,
  gameTime: number
): PlayerCombatState {
  // AGGRESSION REWARDED!
  return {
    ...combatState,
    revengeActive: true,
    revengeEndTime: gameTime + REVENGE.DURATION_MS,
  };
}

/**
 * Update revenge state
 */
export function updateRevengeState(
  combatState: PlayerCombatState,
  gameTime: number
): PlayerCombatState {
  if (combatState.revengeActive && gameTime >= combatState.revengeEndTime) {
    return {
      ...combatState,
      revengeActive: false,
      revengeEndTime: 0,
    };
  }
  return combatState;
}

/**
 * Get revenge damage bonus (0 or REVENGE.DAMAGE_BONUS)
 */
export function getRevengeDamageBonus(combatState: PlayerCombatState): number {
  return combatState.revengeActive ? REVENGE.DAMAGE_BONUS : 0;
}

// =============================================================================
// Graze System
// =============================================================================

/**
 * Check for graze (near-miss)
 * Returns true if enemy is in graze zone but not touching player
 * AND the enemy is not on cooldown
 */
export function checkGraze(
  playerPos: Vector2,
  playerRadius: number,
  enemy: Enemy,
  grazeCooldowns: Map<string, number>,
  gameTime: number
): boolean {
  // Check cooldown first - skip if this enemy was grazed recently
  const cooldownEnd = grazeCooldowns.get(enemy.id);
  if (cooldownEnd !== undefined && gameTime < cooldownEnd) {
    return false;  // Still on cooldown
  }

  const dx = enemy.position.x - playerPos.x;
  const dy = enemy.position.y - playerPos.y;
  const distance = Math.sqrt(dx * dx + dy * dy);

  const contactDistance = playerRadius + enemy.radius;
  const grazeDistance = contactDistance + GRAZE.ZONE_PX;

  // Graze = within graze zone but NOT touching
  return distance > contactDistance && distance <= grazeDistance;
}

/**
 * Register a graze and update combat state
 * Sets cooldown for the grazed enemy
 */
export function registerGraze(
  combatState: PlayerCombatState,
  enemyId: string,
  gameTime: number
): { state: PlayerCombatState; bonusTriggered: boolean } {
  // Check if chain has decayed
  const chainDecayed = gameTime - combatState.lastGrazeTime > GRAZE.DECAY_TIME_MS;
  const currentChain = chainDecayed ? 0 : combatState.grazeChain;

  const newChain = currentChain + 1;
  const bonusTriggered = newChain >= GRAZE.GRAZES_FOR_BONUS &&
                         combatState.grazeChain < GRAZE.GRAZES_FOR_BONUS;

  // Set cooldown for this enemy
  const newCooldowns = new Map(combatState.grazeCooldowns);
  newCooldowns.set(enemyId, gameTime + GRAZE.COOLDOWN_MS);

  // Clean up expired cooldowns (keep map from growing indefinitely)
  for (const [id, endTime] of newCooldowns.entries()) {
    if (gameTime > endTime) {
      newCooldowns.delete(id);
    }
  }

  // RISK-TAKING REWARDED!
  return {
    state: {
      ...combatState,
      grazeChain: newChain,
      lastGrazeTime: gameTime,
      grazeBonus: newChain >= GRAZE.GRAZES_FOR_BONUS ? GRAZE.DAMAGE_BONUS : 0,
      grazeCooldowns: newCooldowns,
    },
    bonusTriggered,
  };
}

/**
 * Update graze state (decay check)
 */
export function updateGrazeState(
  combatState: PlayerCombatState,
  gameTime: number
): PlayerCombatState {
  // Check for chain decay
  if (gameTime - combatState.lastGrazeTime > GRAZE.DECAY_TIME_MS) {
    return {
      ...combatState,
      grazeChain: 0,
      grazeBonus: 0,
    };
  }
  return combatState;
}

// =============================================================================
// Afterimage Dash System
// =============================================================================

/**
 * Start tracking dash for afterimages
 */
export function startDash(combatState: PlayerCombatState): PlayerCombatState {
  return {
    ...combatState,
    isDashing: true,
    lastAfterimageTime: 0, // Will spawn immediately
  };
}

/**
 * Stop dash tracking
 */
export function endDash(combatState: PlayerCombatState): PlayerCombatState {
  return {
    ...combatState,
    isDashing: false,
  };
}

/**
 * Spawn afterimage during dash
 */
export function spawnAfterimage(
  combatState: PlayerCombatState,
  position: Vector2,
  gameTime: number
): PlayerCombatState {
  // Check if we should spawn (based on interval)
  if (gameTime - combatState.lastAfterimageTime < AFTERIMAGE.SPAWN_INTERVAL_MS) {
    return combatState;
  }

  const newImage: Afterimage = {
    id: `afterimage-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    spawnTime: gameTime,
    damage: AFTERIMAGE.DAMAGE_PER_IMAGE,
    hasDealtDamage: new Set(),
  };

  // SPEED IS YOUR WEAPON!
  return {
    ...combatState,
    afterimages: [...combatState.afterimages, newImage],
    lastAfterimageTime: gameTime,
  };
}

/**
 * Update afterimages (remove expired, check collisions)
 * Returns updated state and damage events
 */
export function updateAfterimages(
  combatState: PlayerCombatState,
  enemies: Enemy[],
  gameTime: number
): { state: PlayerCombatState; damageEvents: Array<{ enemyId: string; damage: number }> } {
  const damageEvents: Array<{ enemyId: string; damage: number }> = [];

  // Filter out expired images and check for collisions
  const activeImages = combatState.afterimages
    .filter(img => gameTime - img.spawnTime < AFTERIMAGE.IMAGE_DURATION_MS)
    .map(img => {
      // Check collision with enemies
      for (const enemy of enemies) {
        if (img.hasDealtDamage.has(enemy.id)) continue;

        const dx = enemy.position.x - img.position.x;
        const dy = enemy.position.y - img.position.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // Afterimage has ~15px radius for collision
        if (distance < enemy.radius + 15) {
          img.hasDealtDamage.add(enemy.id);
          damageEvents.push({
            enemyId: enemy.id,
            damage: img.damage,
          });
        }
      }
      return img;
    });

  return {
    state: {
      ...combatState,
      afterimages: activeImages,
    },
    damageEvents,
  };
}

// =============================================================================
// Combat Damage Calculator
// =============================================================================

/**
 * Calculate total damage multiplier from all combat systems
 */
export function calculateTotalDamageMultiplier(
  combatState: PlayerCombatState,
  targetEnemy: Enemy
): number {
  let multiplier = 1.0;

  // Berserker bonus
  multiplier += combatState.berserkerBonus;

  // Revenge bonus
  multiplier += getRevengeDamageBonus(combatState);

  // Graze bonus
  multiplier += combatState.grazeBonus;

  // Execute bonus (applied to enemy, not player state)
  multiplier *= getExecuteDamageMultiplier(targetEnemy);

  return multiplier;
}

/**
 * Calculate final damage to deal
 */
export function calculateFinalDamage(
  baseDamage: number,
  combatState: PlayerCombatState,
  targetEnemy: Enemy
): number {
  const multiplier = calculateTotalDamageMultiplier(combatState, targetEnemy);
  return Math.floor(baseDamage * multiplier);
}

// =============================================================================
// Main Combat Update (Called Each Frame)
// =============================================================================

export interface CombatUpdateResult {
  combatState: PlayerCombatState;
  enemies: EnemyWithCombat[];
  events: CombatEvent[];
}

export type CombatEvent =
  | { type: 'venom_paralysis'; enemyId: string; position: Vector2 }
  | { type: 'bleed_tick'; enemyId: string; damage: number }
  | { type: 'graze'; position: Vector2; chainCount: number }
  | { type: 'graze_bonus_triggered'; bonus: number }
  | { type: 'hover_brake_activated'; position: Vector2 }
  | { type: 'revenge_triggered' }
  | { type: 'execute_ready'; enemyId: string }
  | { type: 'afterimage_damage'; enemyId: string; damage: number };

/**
 * Main combat system update
 * Called each frame to update all combat mechanics
 */
export function updateCombatSystem(
  combatState: PlayerCombatState,
  player: Player,
  enemies: EnemyWithCombat[],
  gameTime: number,
  playerTookDamage: boolean
): CombatUpdateResult {
  const events: CombatEvent[] = [];
  let newCombatState = { ...combatState };

  // 1. Update berserker aura
  const berserkerResult = calculateBerserkerBonus(player.position, enemies);
  newCombatState.nearbyEnemyCount = berserkerResult.nearbyCount;
  newCombatState.berserkerBonus = berserkerResult.bonus;

  // 2. Update hover brake
  const hoverResult = checkHoverBrakeActivation(
    newCombatState,
    player.velocity,
    gameTime
  );
  newCombatState = hoverResult.state;
  if (hoverResult.activated) {
    events.push({ type: 'hover_brake_activated', position: player.position });
  }

  // 3. Update revenge
  if (playerTookDamage) {
    newCombatState = triggerRevenge(newCombatState, gameTime);
    events.push({ type: 'revenge_triggered' });
  }
  newCombatState = updateRevengeState(newCombatState, gameTime);

  // 4. Update graze state
  newCombatState = updateGrazeState(newCombatState, gameTime);

  // 5. Check for grazes against all enemies
  for (const enemy of enemies) {
    if (checkGraze(player.position, player.radius ?? 15, enemy, newCombatState.grazeCooldowns, gameTime)) {
      const grazeResult = registerGraze(newCombatState, enemy.id, gameTime);
      newCombatState = grazeResult.state;
      events.push({
        type: 'graze',
        position: enemy.position,
        chainCount: newCombatState.grazeChain,
      });
      if (grazeResult.bonusTriggered) {
        events.push({ type: 'graze_bonus_triggered', bonus: GRAZE.DAMAGE_BONUS });
      }
    }
  }

  // 6. Update afterimages
  const afterimageResult = updateAfterimages(newCombatState, enemies, gameTime);
  newCombatState = afterimageResult.state;
  for (const dmg of afterimageResult.damageEvents) {
    events.push({ type: 'afterimage_damage', ...dmg });
  }

  // 7. Update enemy status effects
  const updatedEnemies = enemies.map(enemy => {
    let updatedEnemy = { ...enemy };

    // Update venom
    const venomResult = updateVenomState(enemy.venomState, gameTime);
    updatedEnemy.venomState = venomResult.state;
    // Frozen enemies don't move (handled by caller)

    // Update bleed
    const bleedResult = updateBleedState(enemy.bleedState, gameTime);
    updatedEnemy.bleedState = bleedResult.state;
    if (bleedResult.damage > 0) {
      events.push({
        type: 'bleed_tick',
        enemyId: enemy.id,
        damage: bleedResult.damage,
      });
      // Apply damage
      updatedEnemy.health -= bleedResult.damage;
    }

    // Check execute threshold (for visual indicator)
    if (isInExecuteRange(updatedEnemy) && !isInExecuteRange(enemy)) {
      events.push({ type: 'execute_ready', enemyId: enemy.id });
    }

    return updatedEnemy;
  });

  return {
    combatState: newCombatState,
    enemies: updatedEnemies,
    events,
  };
}

// =============================================================================
// Venom Architect System (Special Ability)
// =============================================================================
// Different from the base venom system (which is about paralysis stacking)
// Venom Architect: Infinite stacks, 1 DPS per stack, 10s duration, explosion on venom-kill

/** Venom Architect constants */
export const VENOM_ARCHITECT = {
  DAMAGE_PER_STACK_PER_SECOND: 1, // 1 DPS per stack
  STACK_DURATION_MS: 10000,        // 10 seconds per stack
  EXPLOSION_DAMAGE_PER_STACK: 10,  // Each stack adds 10 damage to explosion
  EXPLOSION_RADIUS: 80,             // 80px AoE
  TICK_INTERVAL_MS: 200,            // Tick every 200ms for smooth damage
  COLOR: '#8B00FF',                 // Violet for venom architect
} as const;

/** Venom Architect state on an enemy */
export interface VenomArchitectState {
  stacks: number;
  stackTimestamps: number[];  // When each stack was applied (for duration tracking)
  lastTickTime: number;       // For damage ticks
}

/**
 * Create initial venom architect state for enemy
 */
export function createInitialVenomArchitectState(): VenomArchitectState {
  return {
    stacks: 0,
    stackTimestamps: [],
    lastTickTime: 0,
  };
}

/**
 * Apply a venom architect stack to an enemy
 * Venom architect stacks INFINITELY - no cap!
 */
export function applyVenomArchitectStack(
  state: VenomArchitectState | undefined,
  gameTime: number
): VenomArchitectState {
  const currentState = state ?? createInitialVenomArchitectState();

  // Clear expired stacks
  const activeStacks = currentState.stackTimestamps.filter(
    t => gameTime - t < VENOM_ARCHITECT.STACK_DURATION_MS
  );

  // Add new stack (infinite stacking!)
  activeStacks.push(gameTime);

  return {
    stacks: activeStacks.length,
    stackTimestamps: activeStacks,
    lastTickTime: currentState.lastTickTime,
  };
}

/**
 * Update venom architect state and calculate damage this frame
 * Returns updated state and damage to apply
 */
export function updateVenomArchitectState(
  state: VenomArchitectState | undefined,
  gameTime: number
): { state: VenomArchitectState; damage: number } {
  if (!state || state.stacks <= 0) {
    return { state: createInitialVenomArchitectState(), damage: 0 };
  }

  // Clear expired stacks
  const activeStacks = state.stackTimestamps.filter(
    t => gameTime - t < VENOM_ARCHITECT.STACK_DURATION_MS
  );

  // If all stacks expired, return no damage
  if (activeStacks.length === 0) {
    return { state: createInitialVenomArchitectState(), damage: 0 };
  }

  // Check if we should tick
  const timeSinceLastTick = gameTime - state.lastTickTime;
  if (timeSinceLastTick < VENOM_ARCHITECT.TICK_INTERVAL_MS) {
    return {
      state: {
        stacks: activeStacks.length,
        stackTimestamps: activeStacks,
        lastTickTime: state.lastTickTime,
      },
      damage: 0,
    };
  }

  // Calculate damage for this tick
  // DPS * stacks / (1000 / tick_interval) = damage per tick
  const ticksPerSecond = 1000 / VENOM_ARCHITECT.TICK_INTERVAL_MS;
  const damagePerTick = (VENOM_ARCHITECT.DAMAGE_PER_STACK_PER_SECOND * activeStacks.length) / ticksPerSecond;

  return {
    state: {
      stacks: activeStacks.length,
      stackTimestamps: activeStacks,
      lastTickTime: gameTime,
    },
    damage: damagePerTick,
  };
}

/**
 * Calculate explosion damage based on stacks
 * Called when enemy dies from venom damage
 */
export function calculateVenomArchitectExplosionDamage(stacks: number): number {
  return stacks * VENOM_ARCHITECT.EXPLOSION_DAMAGE_PER_STACK;
}

/**
 * Get enemies within explosion radius
 */
export function getEnemiesInVenomExplosionRadius(
  explosionPosition: Vector2,
  enemies: Enemy[],
  excludeId: string
): Enemy[] {
  return enemies.filter(enemy => {
    if (enemy.id === excludeId) return false;

    const dx = enemy.position.x - explosionPosition.x;
    const dy = enemy.position.y - explosionPosition.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    return distance <= VENOM_ARCHITECT.EXPLOSION_RADIUS;
  });
}

/**
 * Get venom architect visual intensity (0-1 based on stack count)
 * More stacks = more intense visual
 */
export function getVenomArchitectIntensity(stacks: number): number {
  // Normalize to 0-1, with 20+ stacks being max intensity
  return Math.min(1, stacks / 20);
}

/**
 * Get venom architect color based on stack count
 * Deeper purple with more stacks
 */
export function getVenomArchitectColor(stacks: number): string {
  if (stacks <= 0) return 'transparent';
  // Interpolate from light violet to deep purple based on stacks
  const intensity = Math.min(1, stacks / 15);
  const r = Math.floor(139 - 80 * intensity);
  const g = Math.floor(0);
  const b = Math.floor(255);
  return `rgb(${r}, ${g}, ${b})`;
}

// =============================================================================
// Status Effect Color System - Visual feedback for status effects
// =============================================================================

/**
 * Status effect tint colors - used for visual feedback
 */
export const STATUS_TINT = {
  POISON: '#00FF00',    // Green for poison
  BURNING: '#FF3333',   // Pure red for burning (distinct from player orange)
  FROZEN: '#00CCFF',    // Blue for frozen/slow
  BLEEDING: '#CC0000',  // Red for bleeding
} as const;

/**
 * Calculate the tint opacity based on stack count
 * More stacks = more visible tint
 * @param stacks - Current number of stacks
 * @param maxStacks - Maximum possible stacks
 * @param baseOpacity - Base opacity at 1 stack (default 0.3)
 */
export function calculateStatusTintOpacity(
  stacks: number,
  maxStacks: number,
  baseOpacity: number = 0.3
): number {
  if (stacks <= 0) return 0;
  // Scale from baseOpacity at 1 stack to 0.6 at max stacks
  const normalizedStacks = Math.min(stacks, maxStacks) / maxStacks;
  return baseOpacity + (0.3 * normalizedStacks);
}

/**
 * Get the CSS rgba color string for a status effect
 * @param hexColor - Hex color (e.g., '#00FF00')
 * @param opacity - Opacity 0-1
 */
export function getStatusTintRgba(hexColor: string, opacity: number): string {
  // Parse hex color
  const r = parseInt(hexColor.slice(1, 3), 16);
  const g = parseInt(hexColor.slice(3, 5), 16);
  const b = parseInt(hexColor.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

// =============================================================================
// Chain Lightning System - Damage chains to nearby enemies on kill
// =============================================================================

/** Chain Lightning constants */
export const CHAIN_LIGHTNING = {
  DEFAULT_RANGE_PX: 100,            // Default range for chain
  DEFAULT_DAMAGE_PERCENT: 50,       // 50% damage per bounce
  DEFAULT_MAX_BOUNCES: 3,           // Default max bounces
  ARC_COLOR: '#4488FF',             // Lightning arc color
  ARC_SECONDARY_COLOR: '#88CCFF',   // Secondary arc color for glow
  ARC_DURATION_MS: 150,             // How long the arc visual lasts
} as const;

/** Lightning arc visual effect */
export interface LightningArc {
  id: string;
  fromPosition: Vector2;
  toPosition: Vector2;
  spawnTime: number;
  damage: number;
}

/**
 * Find the nearest enemy within range for chain lightning
 * @param position - Position to search from
 * @param enemies - List of enemies to search
 * @param range - Maximum range in pixels
 * @param excludeIds - Enemy IDs to exclude (already hit)
 */
export function findChainLightningTarget(
  position: Vector2,
  enemies: Enemy[],
  range: number,
  excludeIds: Set<string>
): Enemy | null {
  let nearestEnemy: Enemy | null = null;
  let nearestDistance = Infinity;

  for (const enemy of enemies) {
    // Skip excluded enemies
    if (excludeIds.has(enemy.id)) continue;

    const dx = enemy.position.x - position.x;
    const dy = enemy.position.y - position.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance <= range && distance < nearestDistance) {
      nearestDistance = distance;
      nearestEnemy = enemy;
    }
  }

  return nearestEnemy;
}

/**
 * Process chain lightning on enemy kill
 * Returns damage events and lightning arc visuals
 * @param killedEnemy - The enemy that was killed
 * @param baseDamage - Original damage dealt
 * @param enemies - All enemies
 * @param maxBounces - Maximum number of bounces
 * @param range - Chain range in pixels
 * @param damagePercent - Damage percentage per bounce
 * @param gameTime - Current game time
 */
export function processChainLightning(
  killedEnemy: Enemy,
  baseDamage: number,
  enemies: Enemy[],
  maxBounces: number,
  range: number = CHAIN_LIGHTNING.DEFAULT_RANGE_PX,
  damagePercent: number = CHAIN_LIGHTNING.DEFAULT_DAMAGE_PERCENT,
  gameTime: number = 0
): {
  damageEvents: Array<{ enemyId: string; damage: number }>;
  lightningArcs: LightningArc[];
} {
  const damageEvents: Array<{ enemyId: string; damage: number }> = [];
  const lightningArcs: LightningArc[] = [];
  const hitEnemies = new Set<string>([killedEnemy.id]);

  let currentPosition = killedEnemy.position;
  let currentDamage = baseDamage * (damagePercent / 100);
  let bouncesRemaining = maxBounces;

  while (bouncesRemaining > 0) {
    // Find nearest enemy within range
    const target = findChainLightningTarget(
      currentPosition,
      enemies,
      range,
      hitEnemies
    );

    if (!target) break;  // No valid target found

    // Create damage event
    damageEvents.push({
      enemyId: target.id,
      damage: Math.floor(currentDamage),
    });

    // Create lightning arc visual
    lightningArcs.push({
      id: `lightning-${gameTime}-${bouncesRemaining}`,
      fromPosition: { ...currentPosition },
      toPosition: { ...target.position },
      spawnTime: gameTime,
      damage: Math.floor(currentDamage),
    });

    // Update for next bounce
    hitEnemies.add(target.id);
    currentPosition = target.position;
    currentDamage *= (damagePercent / 100);  // Reduce damage for next bounce
    bouncesRemaining--;
  }

  return { damageEvents, lightningArcs };
}

// =============================================================================
// Infectious Poison System - Poison spreads on death
// =============================================================================

/** Infectious Poison constants */
export const INFECTIOUS_POISON = {
  DEFAULT_SPREAD_RADIUS_PX: 60,     // Default spread radius
  DEFAULT_SPREAD_PERCENT: 50,       // Default % of stacks that spread
  DEFAULT_DPS_PER_STACK: 4,         // Legacy flat DPS (now uses 3% max HP per stack)
  DEFAULT_MAX_STACKS: 5,            // Default max stacks
  TICK_INTERVAL_MS: 200,            // Tick every 200ms (5 ticks per second)
  TINT_COLOR: '#00FF00',            // Green tint
  TINT_BASE_OPACITY: 0.3,           // Base opacity
  // NEW: Percent-based damage - 3% of enemy max HP per second per stack
  // With 5 stacks = 15% max HP per second, kills any enemy in ~6.7 seconds
} as const;

/** Infectious poison state on an enemy */
export interface InfectiousPoisonState {
  stacks: number;
  maxStacks: number;
  dpsPerStack: number;
  lastTickTime: number;
  isInfectious: boolean;  // Whether this poison spreads on death
  spreadRadius: number;
  spreadPercent: number;
}

/**
 * Create initial infectious poison state
 */
export function createInitialInfectiousPoisonState(): InfectiousPoisonState {
  return {
    stacks: 0,
    maxStacks: INFECTIOUS_POISON.DEFAULT_MAX_STACKS,
    dpsPerStack: INFECTIOUS_POISON.DEFAULT_DPS_PER_STACK,
    lastTickTime: 0,
    isInfectious: false,
    spreadRadius: INFECTIOUS_POISON.DEFAULT_SPREAD_RADIUS_PX,
    spreadPercent: INFECTIOUS_POISON.DEFAULT_SPREAD_PERCENT,
  };
}

/**
 * Apply poison stacks to an enemy
 * @param state - Current poison state (or undefined for new)
 * @param stacksToAdd - Number of stacks to add
 * @param isInfectious - Whether this poison is infectious
 * @param config - Optional configuration overrides
 */
export function applyInfectiousPoisonStacks(
  state: InfectiousPoisonState | undefined,
  stacksToAdd: number,
  isInfectious: boolean,
  config?: {
    maxStacks?: number;
    dpsPerStack?: number;
    spreadRadius?: number;
    spreadPercent?: number;
  }
): InfectiousPoisonState {
  const currentState = state ?? createInitialInfectiousPoisonState();

  const maxStacks = config?.maxStacks ?? currentState.maxStacks;
  const newStacks = Math.min(currentState.stacks + stacksToAdd, maxStacks);

  return {
    stacks: newStacks,
    maxStacks,
    dpsPerStack: config?.dpsPerStack ?? currentState.dpsPerStack,
    lastTickTime: currentState.lastTickTime,
    isInfectious: isInfectious || currentState.isInfectious,
    spreadRadius: config?.spreadRadius ?? currentState.spreadRadius,
    spreadPercent: config?.spreadPercent ?? currentState.spreadPercent,
  };
}

/**
 * Poison damage constants
 */
export const POISON_PERCENT_PER_STACK_PER_SECOND = 0.03;  // 3% of max HP per second per stack
export const POISON_MIN_DPS_PER_STACK = 4;                 // Minimum 4 DPS per stack

/**
 * Update infectious poison state and calculate damage this frame
 * @param state - Current poison state
 * @param gameTime - Current game time in ms
 * @param enemyMaxHealth - Enemy's max health for percent-based damage calculation
 *                         If not provided, falls back to flat dpsPerStack damage
 */
export function updateInfectiousPoisonState(
  state: InfectiousPoisonState | undefined,
  gameTime: number,
  enemyMaxHealth?: number
): { state: InfectiousPoisonState; damage: number } {
  if (!state || state.stacks <= 0) {
    return { state: createInitialInfectiousPoisonState(), damage: 0 };
  }

  // Check if we should tick
  const timeSinceLastTick = gameTime - state.lastTickTime;
  if (timeSinceLastTick < INFECTIOUS_POISON.TICK_INTERVAL_MS) {
    return { state, damage: 0 };
  }

  // Calculate damage for this tick
  const ticksPerSecond = 1000 / INFECTIOUS_POISON.TICK_INTERVAL_MS;

  let dps: number;
  if (enemyMaxHealth !== undefined && enemyMaxHealth > 0) {
    // Percent-based damage: 3% of max HP per second per stack
    const percentDps = enemyMaxHealth * POISON_PERCENT_PER_STACK_PER_SECOND * state.stacks;
    // Minimum floor: 4 DPS per stack
    const minDps = POISON_MIN_DPS_PER_STACK * state.stacks;
    // Use the higher of the two
    dps = Math.max(percentDps, minDps);
  } else {
    // Fallback: Flat DPS per stack
    dps = state.dpsPerStack * state.stacks;
  }

  const damagePerTick = dps / ticksPerSecond;

  return {
    state: {
      ...state,
      lastTickTime: gameTime,
    },
    damage: damagePerTick,
  };
}

/**
 * Process poison spread when an enemy dies
 * @param deadEnemy - The enemy that died
 * @param poisonState - The poison state on the dead enemy
 * @param enemies - All enemies
 */
export function processInfectiousPoisonSpread(
  deadEnemy: Enemy,
  poisonState: InfectiousPoisonState,
  enemies: Enemy[]
): Array<{ enemyId: string; stacks: number }> {
  if (!poisonState.isInfectious || poisonState.stacks <= 0) {
    return [];
  }

  const spreadEvents: Array<{ enemyId: string; stacks: number }> = [];
  const spreadStacks = Math.floor(poisonState.stacks * (poisonState.spreadPercent / 100));

  if (spreadStacks <= 0) return [];

  // Find enemies within spread radius
  for (const enemy of enemies) {
    if (enemy.id === deadEnemy.id) continue;

    const dx = enemy.position.x - deadEnemy.position.x;
    const dy = enemy.position.y - deadEnemy.position.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance <= poisonState.spreadRadius) {
      spreadEvents.push({
        enemyId: enemy.id,
        stacks: spreadStacks,
      });
    }
  }

  return spreadEvents;
}

/**
 * Get poison tint color and opacity for rendering
 * @param state - Current poison state
 */
export function getInfectiousPoisonTint(state: InfectiousPoisonState | undefined): {
  color: string;
  opacity: number;
} {
  if (!state || state.stacks <= 0) {
    return { color: 'transparent', opacity: 0 };
  }

  const opacity = calculateStatusTintOpacity(
    state.stacks,
    state.maxStacks,
    INFECTIOUS_POISON.TINT_BASE_OPACITY
  );

  return {
    color: INFECTIOUS_POISON.TINT_COLOR,
    opacity,
  };
}

// =============================================================================
// Export Default
// =============================================================================

export default {
  // Constants
  VENOM,
  BLEED,
  BERSERKER,
  HOVER_BRAKE,
  EXECUTE,
  REVENGE,
  GRAZE,
  AFTERIMAGE,
  VENOM_ARCHITECT,
  STATUS_TINT,
  CHAIN_LIGHTNING,
  INFECTIOUS_POISON,
  // Factory
  createInitialCombatState,
  createInitialVenomState,
  createInitialBleedState,
  createInitialVenomArchitectState,
  createInitialInfectiousPoisonState,
  // Systems
  applyVenomStack,
  updateVenomState,
  applyBleedStack,
  updateBleedState,
  applyVenomArchitectStack,
  updateVenomArchitectState,
  calculateVenomArchitectExplosionDamage,
  getEnemiesInVenomExplosionRadius,
  getVenomArchitectIntensity,
  getVenomArchitectColor,
  calculateBerserkerBonus,
  checkHoverBrakeActivation,
  isHoverBrakeInvulnerable,
  isInExecuteRange,
  getExecuteDamageMultiplier,
  triggerRevenge,
  updateRevengeState,
  checkGraze,
  registerGraze,
  updateGrazeState,
  startDash,
  endDash,
  spawnAfterimage,
  updateAfterimages,
  // Status Effect Tinting
  calculateStatusTintOpacity,
  getStatusTintRgba,
  // Chain Lightning
  findChainLightningTarget,
  processChainLightning,
  // Infectious Poison
  applyInfectiousPoisonStacks,
  updateInfectiousPoisonState,
  processInfectiousPoisonSpread,
  getInfectiousPoisonTint,
  // Damage
  calculateTotalDamageMultiplier,
  calculateFinalDamage,
  // Main update
  updateCombatSystem,
};
