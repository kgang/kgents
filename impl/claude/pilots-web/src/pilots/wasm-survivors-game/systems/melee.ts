/**
 * WASM Survivors - Melee Attack System (Hornet Siege v3)
 *
 * The Mandible Reaver: A bee-themed pseudo-melee arc attack
 *
 * DESIGN PHILOSOPHY:
 * > "The hornet doesn't shoot - it STRIKES. The mandibles are the weapon."
 *
 * The Mandible Reaver replaces generic projectiles with a visceral arc attack
 * that feels like being a predator, not a turret.
 *
 * KEY FEATURES:
 * - 120-degree arc sweep
 * - 60px range (melee, not ranged)
 * - 150ms active window (brief but deadly)
 * - Visual: Amber/gold arc with mandible trails
 * - Audio: Heavy crunch/snap like breaking chitin
 *
 * NEW ABILITY INTEGRATION:
 * - Serration: Applies bleed on hit
 * - Scissor Grip: Chance to stun
 * - Chitin Crack: Armor reduction per hit
 * - Resonant Strike: Knockback on hit
 * - Sawtooth: Every Nth hit bonus damage
 *
 * @see pilots/wasm-survivors-game/systems/abilities.ts
 */

import type { Vector2 } from '../types';
import type { ActiveAbilities, ComputedEffects } from './abilities';
import { computeAbilityEffects } from './abilities';

// =============================================================================
// Types
// =============================================================================

/**
 * Configuration for the Mandible Reaver attack
 */
export interface MandibleReaverConfig {
  // Core shape
  arcAngle: number;           // Degrees (120 = +-60 from facing)
  range: number;              // Pixels from player center
  activeWindow: number;       // Ms the attack hitbox is active

  // Damage
  baseDamage: number;         // Damage per enemy hit
  maxTargets: number;         // Max enemies hit per swing (0 = unlimited)

  // Timing
  cooldown: number;           // Ms between attacks
  windupTime: number;         // Ms before attack starts (telegraph)
  recoveryTime: number;       // Ms after attack ends (vulnerability)

  // Feel
  hitShake: number;           // Screen shake on hit
  multiKillShake: number;     // Shake on 3+ kills
  massacreShake: number;      // Shake on 5+ kills
  freezeFrameMs: number;      // Hit freeze duration

  // Visual
  trailFadeMs: number;        // How long the visual trail lasts
  particleCount: number;      // Particles spawned on hit
}

/**
 * State of an active melee attack
 */
export interface MeleeAttackState {
  // Is attack active?
  isActive: boolean;
  isInWindup: boolean;
  isInRecovery: boolean;

  // Timing
  startTime: number;
  windupEndTime: number;
  activeEndTime: number;
  recoveryEndTime: number;

  // Direction (normalized vector)
  direction: Vector2;

  // What we've hit this swing (prevent multi-hit)
  hitEnemyIds: Set<string>;

  // Stats for this swing
  enemiesHit: number;
  enemiesKilled: number;
  totalDamageDealt: number;
}

/**
 * Result of processing a melee attack frame
 */
export interface MeleeUpdateResult {
  // Enemies hit this frame
  hits: MeleeHit[];

  // Events for juice/witness
  events: MeleeEvent[];

  // Updated state
  newState: MeleeAttackState;
}

export interface MeleeHit {
  enemyId: string;
  damage: number;
  position: Vector2;
  isKill: boolean;
  overkillDamage: number;

  // New ability effects applied to this hit
  appliedBleed: boolean;
  appliedStun: boolean;
  appliedArmorReduction: number;
  appliedKnockback: number;
  wasSawtoothHit: boolean;
}

export type MeleeEventType =
  | 'attack_start'
  | 'attack_hit'
  | 'attack_kill'
  | 'attack_multikill'
  | 'attack_massacre'
  | 'attack_end'
  | 'attack_whiff';

export interface MeleeEvent {
  type: MeleeEventType;
  timestamp: number;
  data?: {
    enemiesHit?: number;
    enemiesKilled?: number;
    totalDamage?: number;
  };
}

/**
 * Enemy data needed for hit detection
 */
export interface MeleeTarget {
  id: string;
  position: Vector2;
  radius: number;
  health: number;
  maxHealth?: number;  // For bleed calculation
  armor?: number;      // For armor reduction
}

// =============================================================================
// Constants
// =============================================================================

/**
 * Default Mandible Reaver configuration
 * Tuned for "weighty but responsive" feel
 */
export const MANDIBLE_REAVER_CONFIG: MandibleReaverConfig = {
  // Core shape - wider than a sword, narrower than a hammer
  arcAngle: 120,              // 120-degree sweep
  range: 60,                  // Close range - you have to GET IN THERE
  activeWindow: 150,          // 150ms - brief window, commit to swing

  // Damage - balanced with apex strike, abilities scale it
  baseDamage: 18,
  maxTargets: 0,              // Unlimited - crowd clear is the point

  // Timing - fast windup, some recovery
  cooldown: 400,              // 2.5 attacks/second max
  windupTime: 50,             // 50ms windup - just enough to read
  recoveryTime: 100,          // 100ms recovery - slight vulnerability

  // Feel - juicy hits
  hitShake: 2,                // Subtle shake on any hit
  multiKillShake: 4,          // More shake on 3+ kills
  massacreShake: 6,           // Big shake on 5+ kills
  freezeFrameMs: 16,          // One frame freeze on kill

  // Visual - amber/gold theme
  trailFadeMs: 150,           // Trail lasts as long as attack
  particleCount: 5,           // Chitin fragments per hit
};

// =============================================================================
// State Management
// =============================================================================

/**
 * Create initial melee attack state (not attacking)
 */
export function createInitialMeleeState(): MeleeAttackState {
  return {
    isActive: false,
    isInWindup: false,
    isInRecovery: false,
    startTime: 0,
    windupEndTime: 0,
    activeEndTime: 0,
    recoveryEndTime: 0,
    direction: { x: 1, y: 0 },
    hitEnemyIds: new Set(),
    enemiesHit: 0,
    enemiesKilled: 0,
    totalDamageDealt: 0,
  };
}

/**
 * Check if player can start a new attack
 */
export function canAttack(
  state: MeleeAttackState,
  currentTime: number,
  config: MandibleReaverConfig = MANDIBLE_REAVER_CONFIG
): boolean {
  // Can't attack during windup, active, or recovery
  if (state.isActive || state.isInWindup || state.isInRecovery) {
    return false;
  }

  // Check cooldown from last attack
  const cooldownEnd = state.recoveryEndTime + config.cooldown;
  return currentTime >= cooldownEnd;
}

/**
 * Start a new melee attack
 */
export function startAttack(
  _previousState: MeleeAttackState,
  direction: Vector2,
  currentTime: number,
  config: MandibleReaverConfig = MANDIBLE_REAVER_CONFIG
): { newState: MeleeAttackState; event: MeleeEvent } {
  // previousState unused - fresh attack state created each time
  // Normalize direction
  const mag = Math.sqrt(direction.x * direction.x + direction.y * direction.y);
  const normalizedDir = mag > 0
    ? { x: direction.x / mag, y: direction.y / mag }
    : { x: 1, y: 0 };

  const windupEnd = currentTime + config.windupTime;
  const activeEnd = windupEnd + config.activeWindow;
  const recoveryEnd = activeEnd + config.recoveryTime;

  const newState: MeleeAttackState = {
    isActive: false,
    isInWindup: true,
    isInRecovery: false,
    startTime: currentTime,
    windupEndTime: windupEnd,
    activeEndTime: activeEnd,
    recoveryEndTime: recoveryEnd,
    direction: normalizedDir,
    hitEnemyIds: new Set(),
    enemiesHit: 0,
    enemiesKilled: 0,
    totalDamageDealt: 0,
  };

  const event: MeleeEvent = {
    type: 'attack_start',
    timestamp: currentTime,
  };

  return { newState, event };
}

// =============================================================================
// Hit Detection
// =============================================================================

/**
 * Check if a point is within the attack arc
 */
export function isInAttackArc(
  playerPos: Vector2,
  attackDir: Vector2,
  targetPos: Vector2,
  config: MandibleReaverConfig = MANDIBLE_REAVER_CONFIG
): boolean {
  // Vector from player to target
  const dx = targetPos.x - playerPos.x;
  const dy = targetPos.y - playerPos.y;
  const distSq = dx * dx + dy * dy;

  // Range check
  if (distSq > config.range * config.range) {
    return false;
  }

  // Angle check
  const dist = Math.sqrt(distSq);
  if (dist === 0) return true; // On top of player = hit

  // Normalize target direction
  const targetDirX = dx / dist;
  const targetDirY = dy / dist;

  // Dot product gives cos of angle between vectors
  const dot = attackDir.x * targetDirX + attackDir.y * targetDirY;

  // Convert arc angle to radians and get cos threshold
  const halfArcRad = (config.arcAngle / 2) * (Math.PI / 180);
  const cosThreshold = Math.cos(halfArcRad);

  return dot >= cosThreshold;
}

/**
 * Find all enemies within the attack arc
 */
export function findTargetsInArc(
  playerPos: Vector2,
  attackDir: Vector2,
  enemies: MeleeTarget[],
  config: MandibleReaverConfig = MANDIBLE_REAVER_CONFIG,
  excludeIds: Set<string> = new Set()
): MeleeTarget[] {
  const targets: MeleeTarget[] = [];

  for (const enemy of enemies) {
    // Skip already-hit enemies
    if (excludeIds.has(enemy.id)) continue;

    // Check if enemy center is in arc
    if (isInAttackArc(playerPos, attackDir, enemy.position, config)) {
      targets.push(enemy);
      continue;
    }

    // Check if enemy edge overlaps arc (for large enemies)
    // Simple approximation: check if distance is within range + radius
    const dx = enemy.position.x - playerPos.x;
    const dy = enemy.position.y - playerPos.y;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist - enemy.radius <= config.range) {
      // Edge might be in arc - check angle to closest point
      const closestX = playerPos.x + (dx / dist) * (dist - enemy.radius);
      const closestY = playerPos.y + (dy / dist) * (dist - enemy.radius);

      if (isInAttackArc(playerPos, attackDir, { x: closestX, y: closestY }, config)) {
        targets.push(enemy);
      }
    }
  }

  // Sort by distance (hit closest first)
  targets.sort((a, b) => {
    const distA = Math.hypot(a.position.x - playerPos.x, a.position.y - playerPos.y);
    const distB = Math.hypot(b.position.x - playerPos.x, b.position.y - playerPos.y);
    return distA - distB;
  });

  // Limit targets if configured
  if (config.maxTargets > 0 && targets.length > config.maxTargets) {
    return targets.slice(0, config.maxTargets);
  }

  return targets;
}

// =============================================================================
// Damage Calculation
// =============================================================================

/**
 * Calculate damage for a melee hit, applying new ability effects
 */
export function calculateMeleeDamage(
  _baseDamage: number,
  computed: ComputedEffects | null,
  target: MeleeTarget,
  config: MandibleReaverConfig = MANDIBLE_REAVER_CONFIG,
  hitCounter: number = 0,
  killStreak: number = 0  // For momentum ability: current consecutive kills
): {
  damage: number;
  appliedBleed: boolean;
  appliedStun: boolean;
  appliedArmorReduction: number;
  appliedKnockback: number;
  wasSawtoothHit: boolean;
} {
  let damage = config.baseDamage;
  let appliedBleed = false;
  let appliedStun = false;
  let appliedArmorReduction = 0;
  let appliedKnockback = 0;
  let wasSawtoothHit = false;

  if (computed) {
    // Base damage multiplier (from legacy compat + trophy scent)
    damage *= computed.damageMultiplier;

    // MANDIBLE: Serration bleed
    if (computed.bleedEnabled) {
      appliedBleed = true;
      // Bleed damage is applied separately by combat system
    }

    // MANDIBLE: Scissor Grip stun
    if (computed.stunChance > 0 && Math.random() < computed.stunChance) {
      appliedStun = true;
    }

    // MANDIBLE: Chitin Crack armor reduction
    if (computed.armorReductionPerHit > 0) {
      appliedArmorReduction = computed.armorReductionPerHit;
      // Apply armor reduction bonus to this hit
      const armorMod = target.armor ? Math.max(0, target.armor - appliedArmorReduction) / 100 : 1;
      damage *= (1 + (1 - armorMod) * 0.5); // Up to 50% more damage on 0 armor
    }

    // MANDIBLE: Resonant Strike knockback
    if (computed.knockbackPx > 0) {
      appliedKnockback = computed.knockbackPx;
    }

    // MANDIBLE: Sawtooth every Nth hit bonus
    if (computed.sawtoothEveryN > 0) {
      if ((hitCounter + 1) % computed.sawtoothEveryN === 0) {
        damage *= (1 + computed.sawtoothBonus / 100);
        wasSawtoothHit = true;
      }
    }

    // VENOM: Melittin damage amp (if target already poisoned)
    if (computed.poisonedDamageAmp > 0) {
      // Combat system tracks which enemies are poisoned
      // For now, this is applied separately
    }

    // Legacy: Crit chance (kept for backwards compat)
    if (computed.critChance > 0 && Math.random() * 100 < computed.critChance) {
      damage *= computed.critDamageMultiplier;
    }

    // MOMENTUM: Kill streak damage bonus (+15% per consecutive kill, max 75%)
    if (computed.killStreakDamage > 0 && killStreak > 0) {
      const streakBonus = Math.min(killStreak * computed.killStreakDamage, 75) / 100;
      damage *= (1 + streakBonus);
    }
  }

  return {
    damage: Math.floor(damage),
    appliedBleed,
    appliedStun,
    appliedArmorReduction,
    appliedKnockback,
    wasSawtoothHit,
  };
}

// =============================================================================
// Main Update Loop
// =============================================================================

/**
 * Update melee attack state and process hits
 */
export function updateMeleeAttack(
  currentState: MeleeAttackState,
  playerPos: Vector2,
  enemies: MeleeTarget[],
  abilities: ActiveAbilities | null,
  currentTime: number,
  config: MandibleReaverConfig = MANDIBLE_REAVER_CONFIG,
  hitCounter: number = 0,
  killStreak: number = 0  // For momentum ability
): MeleeUpdateResult & { newHitCounter: number } {
  const hits: MeleeHit[] = [];
  const events: MeleeEvent[] = [];
  let newState = { ...currentState, hitEnemyIds: new Set(currentState.hitEnemyIds) };
  let newHitCounter = hitCounter;

  // Compute effects from abilities
  const computed = abilities ? computeAbilityEffects(abilities) : null;

  // Check phase transitions
  if (currentState.isInWindup && currentTime >= currentState.windupEndTime) {
    newState.isInWindup = false;
    newState.isActive = true;
  }

  if (currentState.isActive && currentTime >= currentState.activeEndTime) {
    newState.isActive = false;
    newState.isInRecovery = true;

    // Check if we hit anything
    if (currentState.enemiesHit === 0) {
      events.push({
        type: 'attack_whiff',
        timestamp: currentTime,
      });
    }
  }

  if (currentState.isInRecovery && currentTime >= currentState.recoveryEndTime) {
    newState.isInRecovery = false;

    // Attack complete event
    events.push({
      type: 'attack_end',
      timestamp: currentTime,
      data: {
        enemiesHit: currentState.enemiesHit,
        enemiesKilled: currentState.enemiesKilled,
        totalDamage: currentState.totalDamageDealt,
      },
    });
  }

  // Process hits during active window
  if (newState.isActive) {
    const targets = findTargetsInArc(
      playerPos,
      currentState.direction,
      enemies,
      config,
      newState.hitEnemyIds
    );

    for (const target of targets) {
      const damageResult = calculateMeleeDamage(
        config.baseDamage,
        computed,
        target,
        config,
        newHitCounter,
        killStreak
      );

      const isKill = damageResult.damage >= target.health;
      const overkill = Math.max(0, damageResult.damage - target.health);

      hits.push({
        enemyId: target.id,
        damage: damageResult.damage,
        position: target.position,
        isKill,
        overkillDamage: overkill,
        appliedBleed: damageResult.appliedBleed,
        appliedStun: damageResult.appliedStun,
        appliedArmorReduction: damageResult.appliedArmorReduction,
        appliedKnockback: damageResult.appliedKnockback,
        wasSawtoothHit: damageResult.wasSawtoothHit,
      });

      // Track hit
      newState.hitEnemyIds.add(target.id);
      newState.enemiesHit++;
      newState.totalDamageDealt += damageResult.damage;
      newHitCounter++;

      // Hit event
      events.push({
        type: 'attack_hit',
        timestamp: currentTime,
      });

      if (isKill) {
        newState.enemiesKilled++;
        events.push({
          type: 'attack_kill',
          timestamp: currentTime,
        });
      }
    }

    // Multi-kill events
    if (newState.enemiesKilled >= 5 && currentState.enemiesKilled < 5) {
      events.push({
        type: 'attack_massacre',
        timestamp: currentTime,
        data: { enemiesKilled: newState.enemiesKilled },
      });
    } else if (newState.enemiesKilled >= 3 && currentState.enemiesKilled < 3) {
      events.push({
        type: 'attack_multikill',
        timestamp: currentTime,
        data: { enemiesKilled: newState.enemiesKilled },
      });
    }
  }

  return { hits, events, newState, newHitCounter };
}

// =============================================================================
// Ability Interactions
// =============================================================================

/**
 * Apply ability modifiers to melee config
 */
export function getModifiedConfig(
  baseConfig: MandibleReaverConfig,
  abilities: ActiveAbilities | null
): MandibleReaverConfig {
  if (!abilities) return baseConfig;

  const computed = computeAbilityEffects(abilities);
  const config = { ...baseConfig };

  // Attack speed bonus reduces cooldown (from legacy compat)
  if (computed.attackSpeedBonus > 0) {
    config.cooldown = Math.max(200, config.cooldown * (1 - computed.attackSpeedBonus));
  }

  // Feeding Efficiency: Attack speed bonus is tracked in runtime state
  // and applied dynamically via abilities.runtime.feedingEfficiency

  // Damage multiplier affects base damage
  if (computed.damageMultiplier > 1) {
    config.baseDamage = Math.floor(config.baseDamage * computed.damageMultiplier);
  }

  // Full arc (legacy compat) expands arc angle
  if (computed.hasFullArc) {
    config.arcAngle = 360; // Full circle attack
  }

  return config;
}

/**
 * Generate multishot arc directions
 * Returns array of direction vectors for multi-arc attacks
 */
export function getMultishotDirections(
  baseDirection: Vector2,
  count: number,
  spreadAngle: number = 40
): Vector2[] {
  if (count <= 1) return [baseDirection];

  const directions: Vector2[] = [];
  const spreadRad = (spreadAngle * Math.PI) / 180;
  const baseAngle = Math.atan2(baseDirection.y, baseDirection.x);

  // Center arc
  directions.push(baseDirection);

  // Side arcs
  const halfCount = Math.floor((count - 1) / 2);
  for (let i = 1; i <= halfCount; i++) {
    const offset = (i * spreadRad) / halfCount;

    // Left
    directions.push({
      x: Math.cos(baseAngle - offset),
      y: Math.sin(baseAngle - offset),
    });

    // Right
    directions.push({
      x: Math.cos(baseAngle + offset),
      y: Math.sin(baseAngle + offset),
    });
  }

  return directions.slice(0, count);
}

// =============================================================================
// Visual Helpers
// =============================================================================

/**
 * Get points for rendering the attack arc
 * Returns array of points forming the arc outline
 */
export function getArcRenderPoints(
  playerPos: Vector2,
  direction: Vector2,
  config: MandibleReaverConfig = MANDIBLE_REAVER_CONFIG,
  segments: number = 12
): Vector2[] {
  const points: Vector2[] = [];
  const baseAngle = Math.atan2(direction.y, direction.x);
  const halfArcRad = (config.arcAngle / 2) * (Math.PI / 180);

  // Start at player
  points.push({ ...playerPos });

  // Arc points
  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    const angle = baseAngle - halfArcRad + (t * config.arcAngle * Math.PI) / 180;

    points.push({
      x: playerPos.x + Math.cos(angle) * config.range,
      y: playerPos.y + Math.sin(angle) * config.range,
    });
  }

  // Close back to player
  points.push({ ...playerPos });

  return points;
}

/**
 * Get attack progress (0-1) for animations
 */
export function getAttackProgress(
  state: MeleeAttackState,
  currentTime: number
): { phase: 'idle' | 'windup' | 'active' | 'recovery'; progress: number } {
  if (!state.isInWindup && !state.isActive && !state.isInRecovery) {
    return { phase: 'idle', progress: 0 };
  }

  if (state.isInWindup) {
    const duration = state.windupEndTime - state.startTime;
    const elapsed = currentTime - state.startTime;
    return { phase: 'windup', progress: Math.min(1, elapsed / duration) };
  }

  if (state.isActive) {
    const duration = state.activeEndTime - state.windupEndTime;
    const elapsed = currentTime - state.windupEndTime;
    return { phase: 'active', progress: Math.min(1, elapsed / duration) };
  }

  // Recovery
  const duration = state.recoveryEndTime - state.activeEndTime;
  const elapsed = currentTime - state.activeEndTime;
  return { phase: 'recovery', progress: Math.min(1, elapsed / duration) };
}

// =============================================================================
// Exports
// =============================================================================

export default {
  // Config
  MANDIBLE_REAVER_CONFIG,

  // State
  createInitialMeleeState,
  canAttack,
  startAttack,

  // Hit detection
  isInAttackArc,
  findTargetsInArc,

  // Damage
  calculateMeleeDamage,

  // Update
  updateMeleeAttack,

  // Ability interactions
  getModifiedConfig,
  getMultishotDirections,

  // Visual
  getArcRenderPoints,
  getAttackProgress,
};
