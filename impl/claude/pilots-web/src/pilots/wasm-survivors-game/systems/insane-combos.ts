/**
 * WASM Survivors - INSANE COMBO SYSTEM
 *
 * "If I have the right combo of other perks and skill, I'll really pop off"
 *
 * This system makes Apex Strike and Auto-Attack work together for DEVASTATING combos.
 * Every perk has combo potential. Every kill feeds the next. Skill gates the ceiling.
 *
 * CORE MECHANICS:
 * 1. BEE BOUNCE - Bounce off bees harder with chained kills, pinball style
 * 2. MOMENTUM STACKING - Speed/damage snowball with consecutive actions
 * 3. CHAIN LIGHTNING - Kills cascade to nearby enemies
 * 4. GRAZE CHAINS - Near-misses power up your next attack
 * 5. COMBO WINDOWS - Tight timing rewards skilled play
 * 6. PERK SYNERGIES - Specific perk combos unlock NEW abilities
 *
 * DESIGN PHILOSOPHY:
 * > "The floor is competent. The ceiling is INSANE."
 * > "Every perk is good. Some perk COMBOS are legendary."
 * > "Skill gates access to the broken stuff."
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 */

import type { Vector2, Enemy } from '../types';
import type { AbilityId, ComputedEffects } from './abilities';

// =============================================================================
// Types
// =============================================================================

/**
 * Combo tier determines power level and rarity
 * - basic: Easy to achieve, modest boost
 * - advanced: Requires skill, significant boost
 * - legendary: Requires mastery, INSANE boost
 * - transcendent: Perfect play only, breaks the game
 */
export type ComboTier = 'basic' | 'advanced' | 'legendary' | 'transcendent';

/**
 * Momentum types for different playstyles
 */
export type MomentumType =
  | 'kill_streak'      // Consecutive kills
  | 'graze_streak'     // Consecutive near-misses
  | 'bounce_streak'    // Consecutive bee bounces
  | 'perfect_timing'   // Perfect combo window hits
  | 'apex_chain';      // Chained apex strikes

/**
 * Bee Bounce state - Pinball physics on apex strike
 */
export interface BeeBounceState {
  /** Current bounce combo count */
  bounceCount: number;
  /** Velocity multiplier from bounce chain */
  velocityMultiplier: number;
  /** Direction after last bounce */
  bounceDirection: Vector2 | null;
  /** Time window to continue bounce chain (ms) */
  bounceWindow: number;
  /** Damage multiplier from bounce chain */
  damageMultiplier: number;
  /** Whether player is currently in bounce state */
  isBouncing: boolean;
  /** Last bounce position for visual effects */
  lastBouncePosition: Vector2 | null;
  /** IDs of enemies bounced off in current chain */
  bouncedEnemyIds: Set<string>;
  /** Bonus speed gained from bounce chain */
  bonusSpeed: number;
}

/**
 * Momentum Stack - Snowballing power
 */
export interface MomentumStack {
  type: MomentumType;
  stacks: number;
  maxStacks: number;
  decayRate: number;      // Stacks lost per second
  lastStackTime: number;  // Timestamp of last stack gain
  bonusPerStack: number;  // Multiplier per stack
  /** Time window to maintain momentum (ms) */
  window: number;
}

/**
 * Complete combo state for the player
 */
export interface InsaneComboState {
  // === BEE BOUNCE ===
  beeBounce: BeeBounceState;

  // === MOMENTUM STACKING ===
  momentum: Record<MomentumType, MomentumStack>;

  // === COMBO WINDOWS ===
  /** Active combo window timer (ms remaining) */
  comboWindowRemaining: number;
  /** Combo window multiplier (increases with perfect timing) */
  comboWindowMultiplier: number;
  /** Consecutive perfect windows hit */
  perfectWindowStreak: number;

  // === GRAZE CHAINS ===
  /** Current graze streak count */
  grazeStreak: number;
  /** Damage bonus from graze streak */
  grazeDamageBonus: number;
  /** Speed bonus from graze streak */
  grazeSpeedBonus: number;
  /** Time since last graze (ms) */
  timeSinceGraze: number;

  // === CHAIN KILLS ===
  /** Enemies marked for chain kill */
  chainTargets: ChainTarget[];
  /** Chain kill damage multiplier */
  chainKillMultiplier: number;
  /** Maximum chain range */
  chainRange: number;

  // === OVERALL COMBO ===
  /** Total combo multiplier (product of all systems) */
  totalComboMultiplier: number;
  /** Highest combo achieved this run */
  highestCombo: number;
  /** Current combo tier */
  currentTier: ComboTier;

  // === PERK SYNERGIES ===
  /** Active synergy bonuses */
  activeSynergies: PerkSynergy[];
  /** Unlocked transcendent abilities */
  transcendentAbilities: TranscendentAbility[];

  // === VISUAL FEEDBACK ===
  /** Screen intensity (0-1) for effects */
  screenIntensity: number;
  /** Time dilation factor (1 = normal, <1 = slow-mo) */
  timeDilation: number;
  /** Active particle multiplier */
  particleMultiplier: number;
}

/**
 * Chain kill target - Enemy marked for chain death
 */
export interface ChainTarget {
  enemyId: string;
  position: Vector2;
  damage: number;
  expiryTime: number;
  chainOrder: number;  // 1st, 2nd, 3rd in chain
}

/**
 * Perk synergy - Two perks that unlock special effects
 */
export interface PerkSynergy {
  id: string;
  name: string;
  perks: [AbilityId, AbilityId];
  description: string;
  effect: SynergyEffect;
  tier: ComboTier;
  visualIndicator: string;
}

/**
 * Synergy effect - What the synergy actually does
 */
export interface SynergyEffect {
  damageMultiplier?: number;
  speedMultiplier?: number;
  attackSpeedMultiplier?: number;
  bounceStrength?: number;
  chainRange?: number;
  grazeWindow?: number;
  specialAbility?: string;
}

/**
 * Transcendent abilities - Unlocked by 3+ perk synergies
 */
export interface TranscendentAbility {
  id: string;
  name: string;
  requiredSynergies: number;
  description: string;
  effect: TranscendentEffect;
}

/**
 * Transcendent effect - Game-breaking power
 */
export interface TranscendentEffect {
  infiniteBounce?: boolean;
  chainReaction?: boolean;
  timeStop?: number;        // Duration in ms
  damageMultiplier?: number;
  invulnerable?: boolean;
}

/**
 * Combo event - For visual/audio feedback
 */
export type ComboEvent =
  | { type: 'bounce_started'; position: Vector2; bounceCount: number }
  | { type: 'bounce_continued'; position: Vector2; bounceCount: number; multiplier: number }
  | { type: 'bounce_ended'; totalBounces: number; damageDealt: number }
  | { type: 'momentum_gained'; momentumType: MomentumType; stacks: number }
  | { type: 'momentum_lost'; momentumType: MomentumType }
  | { type: 'perfect_window'; streak: number; multiplier: number }
  | { type: 'graze_chain'; streak: number; bonus: number }
  | { type: 'chain_kill'; chainLength: number; position: Vector2 }
  | { type: 'synergy_activated'; synergy: PerkSynergy }
  | { type: 'transcendent_unlocked'; ability: TranscendentAbility }
  | { type: 'tier_up'; newTier: ComboTier }
  | { type: 'combo_broken'; wasAt: number };

// =============================================================================
// Constants
// =============================================================================

/**
 * Bee Bounce Configuration
 * "Bees are TRAMPOLINES, not obstacles"
 */
export const BEE_BOUNCE_CONFIG = {
  // Base bounce values
  baseVelocityBoost: 1.3,        // 30% faster per bounce
  baseDamageBoost: 1.25,         // 25% more damage per bounce
  maxBounces: 10,                 // Cap at 10 bounces (but can go higher with perks)
  bounceWindow: 800,              // 800ms to chain bounces
  minBounceAngle: 30,             // Minimum deflection angle (degrees)

  // Scaling
  velocityScaling: 0.15,          // +15% velocity per bounce
  damageScaling: 0.20,            // +20% damage per bounce
  speedDecay: 0.85,               // Speed multiplier per bounce (maintains momentum)

  // Visual thresholds
  flowStateThreshold: 3,          // Bounces needed for flow state
  insaneThreshold: 6,             // Bounces for INSANE mode
  transcendentThreshold: 10,      // Bounces for transcendent

  // Sound
  pitchPerBounce: 0.1,            // Pitch increase per bounce (musical escalation)
} as const;

/**
 * Momentum Stack Configuration
 * "The more you do, the more you CAN do"
 */
export const MOMENTUM_CONFIG: Record<MomentumType, Omit<MomentumStack, 'stacks' | 'lastStackTime'>> = {
  kill_streak: {
    type: 'kill_streak',
    maxStacks: 20,
    decayRate: 2,           // Lose 2 stacks per second without kills
    bonusPerStack: 0.05,    // +5% damage per stack
    window: 2000,           // 2s to continue streak
  },
  graze_streak: {
    type: 'graze_streak',
    maxStacks: 15,
    decayRate: 3,           // Decay faster (skill-gated)
    bonusPerStack: 0.08,    // +8% per graze (higher reward)
    window: 600,            // 600ms (tight!)
  },
  bounce_streak: {
    type: 'bounce_streak',
    maxStacks: 10,
    decayRate: 1,           // Slow decay
    bonusPerStack: 0.12,    // +12% per bounce
    window: 800,            // Matches bounce window
  },
  perfect_timing: {
    type: 'perfect_timing',
    maxStacks: 5,
    decayRate: 0.5,         // Very slow decay
    bonusPerStack: 0.15,    // +15% per perfect
    window: 500,            // 500ms perfect window
  },
  apex_chain: {
    type: 'apex_chain',
    maxStacks: 8,
    decayRate: 1.5,
    bonusPerStack: 0.10,    // +10% per apex chain
    window: 400,            // 400ms chain window
  },
};

/**
 * Combo Window Configuration
 * "Perfect timing = INSANE rewards"
 */
export const COMBO_WINDOW_CONFIG = {
  baseWindow: 300,                // 300ms base window
  perfectWindow: 100,             // 100ms for perfect timing
  perfectMultiplier: 1.5,         // 50% bonus for perfect
  perfectStreakBonus: 0.25,       // +25% per consecutive perfect
  maxStreakBonus: 3.0,            // Cap at 3x from streak
  windowExtensionPerKill: 50,     // +50ms per kill during window
  maxWindowExtension: 500,        // Cap at 500ms extension
} as const;

/**
 * Graze Chain Configuration
 * "Danger = Power"
 */
export const GRAZE_CONFIG = {
  baseGrazeRadius: 25,            // 25px graze zone
  damagePerGraze: 0.08,           // +8% damage per graze
  speedPerGraze: 0.03,            // +3% speed per graze
  maxGrazeStacks: 20,             // Cap at 20 grazes
  grazeDecayTime: 500,            // 500ms to reset
  grazeInvulnWindow: 50,          // 50ms invuln after graze (skill reward)
} as const;

/**
 * Chain Kill Configuration
 * "Kills cascade like DOMINOES"
 */
export const CHAIN_KILL_CONFIG = {
  baseChainRange: 100,            // 100px chain range
  chainDamageMultiplier: 0.75,    // 75% damage to chained targets
  maxChainLength: 5,              // Up to 5 chain kills
  chainDelayMs: 80,               // 80ms between chains (visual cascade)
  chainRangePerKill: 15,          // +15px range per kill in chain
} as const;

/**
 * Tier thresholds - Total combo multiplier needed
 */
export const TIER_THRESHOLDS = {
  basic: 1.0,
  advanced: 2.0,
  legendary: 4.0,
  transcendent: 8.0,
} as const;

// =============================================================================
// PERK SYNERGIES - Two-perk combos that unlock special effects
// =============================================================================

/**
 * All available perk synergies
 * Each requires TWO specific perks to activate
 */
export const PERK_SYNERGIES: PerkSynergy[] = [
  // === DAMAGE SYNERGIES ===
  {
    id: 'berserker_rage',
    name: 'BERSERKER RAGE',
    perks: ['crushing_bite', 'frenzy'],
    description: 'Attacks deal +50% damage and generate shockwaves',
    effect: { damageMultiplier: 1.5, specialAbility: 'shockwave_on_hit' },
    tier: 'advanced',
    visualIndicator: 'red_aura_pulse',
  },
  {
    id: 'venom_cascade',
    name: 'VENOM CASCADE',
    perks: ['venomous_strike', 'chain_lightning'],
    description: 'Poison spreads to ALL chained enemies',
    effect: { chainRange: 150, specialAbility: 'poison_chain' },
    tier: 'advanced',
    visualIndicator: 'green_lightning',
  },
  {
    id: 'executioner',
    name: 'EXECUTIONER',
    perks: ['savage_blow', 'execution'],
    description: 'Execute threshold raised to 35%, +100% execute damage',
    effect: { damageMultiplier: 2.0, specialAbility: 'enhanced_execute' },
    tier: 'legendary',
    visualIndicator: 'skull_flash',
  },
  {
    id: 'double_trouble',
    name: 'DOUBLE TROUBLE',
    perks: ['double_strike', 'critical_sting'],
    description: 'Double strikes can BOTH crit, crits deal 3x instead of 2x',
    effect: { damageMultiplier: 1.5, specialAbility: 'double_crit' },
    tier: 'legendary',
    visualIndicator: 'twin_orange_burst',
  },

  // === SPEED SYNERGIES ===
  {
    id: 'lightning_reflexes',
    name: 'LIGHTNING REFLEXES',
    perks: ['quick_strikes', 'swift_wings'],
    description: 'Everything is faster. Graze window doubled.',
    effect: { attackSpeedMultiplier: 1.3, speedMultiplier: 1.2, grazeWindow: 2.0 },
    tier: 'advanced',
    visualIndicator: 'blue_speed_lines',
  },
  {
    id: 'time_lord',
    name: 'TIME LORD',
    perks: ['bullet_time', 'berserker_pace'],
    description: 'Time slows for enemies, not you. +25% all speeds.',
    effect: { speedMultiplier: 1.25, attackSpeedMultiplier: 1.25, specialAbility: 'time_bubble' },
    tier: 'legendary',
    visualIndicator: 'purple_time_ripple',
  },

  // === BOUNCE SYNERGIES ===
  {
    id: 'pinball_wizard',
    name: 'PINBALL WIZARD',
    perks: ['swift_wings', 'momentum'],
    description: 'Bounces give +50% velocity, momentum stacks 2x faster',
    effect: { bounceStrength: 1.5, specialAbility: 'double_momentum' },
    tier: 'advanced',
    visualIndicator: 'gold_bounce_trail',
  },
  {
    id: 'ricochet_master',
    name: 'RICOCHET MASTER',
    perks: ['chain_lightning', 'sweeping_arc'],
    description: 'Bounces chain to 2 additional enemies, 360-degree hits',
    effect: { chainRange: 200, specialAbility: 'multi_bounce' },
    tier: 'legendary',
    visualIndicator: 'lightning_circle',
  },

  // === SURVIVAL SYNERGIES ===
  {
    id: 'immortal',
    name: 'IMMORTAL',
    perks: ['hardened_shell', 'regeneration'],
    description: 'Regen doubled, damage reduction applies to DOTs',
    effect: { specialAbility: 'enhanced_regen' },
    tier: 'advanced',
    visualIndicator: 'green_shield_pulse',
  },
  {
    id: 'vampire_lord',
    name: 'VAMPIRE LORD',
    perks: ['lifesteal', 'last_stand'],
    description: 'Lifesteal triples when below 30% HP',
    effect: { specialAbility: 'desperate_lifesteal' },
    tier: 'legendary',
    visualIndicator: 'red_blood_orbs',
  },

  // === GRAZE SYNERGIES ===
  {
    id: 'danger_dancer',
    name: 'DANGER DANCER',
    perks: ['graze_frenzy', 'swift_wings'],
    description: 'Grazes give +5% speed that stacks infinitely (until hit)',
    effect: { speedMultiplier: 1.05, specialAbility: 'infinite_graze_speed' },
    tier: 'legendary',
    visualIndicator: 'magenta_speed_aura',
  },
  {
    id: 'risk_reward',
    name: 'RISK REWARD',
    perks: ['glass_cannon', 'graze_frenzy'],
    description: 'Each graze gives +10% damage (resets on hit). INSANE ceiling.',
    effect: { damageMultiplier: 1.1, specialAbility: 'graze_damage_stack' },
    tier: 'transcendent',
    visualIndicator: 'red_magenta_pulse',
  },

  // === APEX SYNERGIES ===
  {
    id: 'apex_predator',
    name: 'APEX PREDATOR',
    perks: ['trophy_scent', 'clean_kill'],
    description: 'Apex strikes deal +5% permanent damage per unique kill',
    effect: { specialAbility: 'permanent_apex_scaling' },
    tier: 'legendary',
    visualIndicator: 'gold_crown_glow',
  },
  {
    id: 'endless_hunt',
    name: 'ENDLESS HUNT',
    perks: ['feeding_efficiency', 'updraft'],
    description: 'Kills reset apex cooldown, +10% speed per kill (stacks 5x)',
    effect: { speedMultiplier: 1.1, specialAbility: 'apex_reset' },
    tier: 'advanced',
    visualIndicator: 'amber_speed_burst',
  },

  // === WING SYNERGIES ===
  {
    id: 'vortex',
    name: 'VORTEX',
    perks: ['draft', 'buzz_field'],
    description: 'Stationary aura PULLS enemies in AND damages them',
    effect: { specialAbility: 'gravity_well' },
    tier: 'advanced',
    visualIndicator: 'spiral_pull_effect',
  },
  {
    id: 'thermal_reactor',
    name: 'THERMAL REACTOR',
    perks: ['thermal_wake', 'hover_pressure'],
    description: 'Trail and pressure combine for MASSIVE area denial',
    effect: { specialAbility: 'thermal_zone' },
    tier: 'legendary',
    visualIndicator: 'orange_heat_zone',
  },
];

// =============================================================================
// TRANSCENDENT ABILITIES - Unlocked by having multiple synergies active
// =============================================================================

export const TRANSCENDENT_ABILITIES: TranscendentAbility[] = [
  {
    id: 'infinite_bounce',
    name: 'INFINITE BOUNCE',
    requiredSynergies: 3,
    description: 'Bounces never end as long as enemies exist',
    effect: { infiniteBounce: true, damageMultiplier: 2.0 },
  },
  {
    id: 'chain_reaction',
    name: 'CHAIN REACTION',
    requiredSynergies: 4,
    description: 'Every kill chains to ALL enemies in range',
    effect: { chainReaction: true, damageMultiplier: 1.5 },
  },
  {
    id: 'time_stop',
    name: 'TIME STOP',
    requiredSynergies: 5,
    description: 'On combo tier-up, freeze time for 2 seconds',
    effect: { timeStop: 2000, invulnerable: true },
  },
  {
    id: 'omega_strike',
    name: 'OMEGA STRIKE',
    requiredSynergies: 6,
    description: 'Apex strike deals 10x damage, no cooldown',
    effect: { damageMultiplier: 10.0 },
  },
];

// =============================================================================
// State Factory
// =============================================================================

/**
 * Create initial bee bounce state
 */
export function createInitialBeeBounceState(): BeeBounceState {
  return {
    bounceCount: 0,
    velocityMultiplier: 1.0,
    bounceDirection: null,
    bounceWindow: 0,
    damageMultiplier: 1.0,
    isBouncing: false,
    lastBouncePosition: null,
    bouncedEnemyIds: new Set(),
    bonusSpeed: 0,
  };
}

/**
 * Create initial momentum stacks
 */
export function createInitialMomentumStacks(): Record<MomentumType, MomentumStack> {
  const stacks: Partial<Record<MomentumType, MomentumStack>> = {};
  for (const [type, config] of Object.entries(MOMENTUM_CONFIG)) {
    stacks[type as MomentumType] = {
      ...config,
      stacks: 0,
      lastStackTime: 0,
    };
  }
  return stacks as Record<MomentumType, MomentumStack>;
}

/**
 * Create initial insane combo state
 */
export function createInitialInsaneComboState(): InsaneComboState {
  return {
    beeBounce: createInitialBeeBounceState(),
    momentum: createInitialMomentumStacks(),
    comboWindowRemaining: 0,
    comboWindowMultiplier: 1.0,
    perfectWindowStreak: 0,
    grazeStreak: 0,
    grazeDamageBonus: 0,
    grazeSpeedBonus: 0,
    timeSinceGraze: 0,
    chainTargets: [],
    chainKillMultiplier: 1.0,
    chainRange: CHAIN_KILL_CONFIG.baseChainRange,
    totalComboMultiplier: 1.0,
    highestCombo: 1.0,
    currentTier: 'basic',
    activeSynergies: [],
    transcendentAbilities: [],
    screenIntensity: 0,
    timeDilation: 1.0,
    particleMultiplier: 1.0,
  };
}

// =============================================================================
// Bee Bounce System
// =============================================================================

/**
 * Calculate bounce direction based on collision
 */
export function calculateBounceDirection(
  playerVelocity: Vector2,
  enemyPosition: Vector2,
  playerPosition: Vector2
): Vector2 {
  // Calculate collision normal (from enemy to player)
  const dx = playerPosition.x - enemyPosition.x;
  const dy = playerPosition.y - enemyPosition.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  const normalX = dx / dist;
  const normalY = dy / dist;

  // Reflect velocity off the normal (like a pinball bounce)
  const dot = playerVelocity.x * normalX + playerVelocity.y * normalY;
  const reflectX = playerVelocity.x - 2 * dot * normalX;
  const reflectY = playerVelocity.y - 2 * dot * normalY;

  // Normalize
  const reflectDist = Math.sqrt(reflectX * reflectX + reflectY * reflectY);
  if (reflectDist < 0.001) {
    // Fallback: bounce directly away from enemy
    return { x: normalX, y: normalY };
  }

  return { x: reflectX / reflectDist, y: reflectY / reflectDist };
}

/**
 * Process a bee bounce event
 */
export function processBeeBounce(
  state: InsaneComboState,
  enemy: Enemy,
  playerPosition: Vector2,
  playerVelocity: Vector2,
  gameTime: number,
  config = BEE_BOUNCE_CONFIG
): { state: InsaneComboState; events: ComboEvent[]; newVelocity: Vector2; damage: number } {
  const events: ComboEvent[] = [];
  const { beeBounce } = state;

  // Calculate new bounce direction
  const bounceDir = calculateBounceDirection(playerVelocity, enemy.position, playerPosition);

  // Check if continuing or starting bounce chain
  const isContinuing = beeBounce.isBouncing && beeBounce.bounceWindow > 0;
  const newBounceCount = isContinuing ? beeBounce.bounceCount + 1 : 1;

  // Can't bounce off same enemy twice in a chain
  if (beeBounce.bouncedEnemyIds.has(enemy.id)) {
    // Still deal damage but don't count as new bounce
    const damage = Math.floor(25 * beeBounce.damageMultiplier);
    return { state, events: [], newVelocity: playerVelocity, damage };
  }

  // Calculate multipliers
  const velocityMult = config.baseVelocityBoost + (config.velocityScaling * (newBounceCount - 1));
  const damageMult = config.baseDamageBoost + (config.damageScaling * (newBounceCount - 1));

  // Calculate new velocity magnitude
  const speed = Math.sqrt(playerVelocity.x ** 2 + playerVelocity.y ** 2);
  const newSpeed = speed * velocityMult * config.speedDecay;

  // New velocity
  const newVelocity: Vector2 = {
    x: bounceDir.x * newSpeed,
    y: bounceDir.y * newSpeed,
  };

  // Calculate damage
  const damage = Math.floor(25 * damageMult);

  // Update bounced enemies
  const newBouncedIds = new Set(beeBounce.bouncedEnemyIds);
  newBouncedIds.add(enemy.id);

  // Update state
  const newBeeBounce: BeeBounceState = {
    bounceCount: newBounceCount,
    velocityMultiplier: velocityMult,
    bounceDirection: bounceDir,
    bounceWindow: config.bounceWindow,
    damageMultiplier: damageMult,
    isBouncing: true,
    lastBouncePosition: { ...enemy.position },
    bouncedEnemyIds: newBouncedIds,
    bonusSpeed: newSpeed - speed,
  };

  // Generate events
  if (!isContinuing) {
    events.push({ type: 'bounce_started', position: enemy.position, bounceCount: 1 });
  } else {
    events.push({
      type: 'bounce_continued',
      position: enemy.position,
      bounceCount: newBounceCount,
      multiplier: damageMult,
    });
  }

  // Add momentum stack
  const newMomentum = addMomentumStack(state.momentum, 'bounce_streak', gameTime);

  // Check for tier change
  const newState: InsaneComboState = {
    ...state,
    beeBounce: newBeeBounce,
    momentum: newMomentum,
  };

  return {
    state: recalculateTotalMultiplier(newState),
    events,
    newVelocity,
    damage,
  };
}

/**
 * Update bee bounce state (decay)
 */
export function updateBeeBounce(
  state: InsaneComboState,
  deltaTime: number
): { state: InsaneComboState; events: ComboEvent[] } {
  const events: ComboEvent[] = [];
  const { beeBounce } = state;

  if (!beeBounce.isBouncing) {
    return { state, events };
  }

  // Decay bounce window
  const newWindow = beeBounce.bounceWindow - deltaTime;

  if (newWindow <= 0) {
    // Bounce chain ended
    events.push({
      type: 'bounce_ended',
      totalBounces: beeBounce.bounceCount,
      damageDealt: 0, // Would need to track this
    });

    return {
      state: {
        ...state,
        beeBounce: createInitialBeeBounceState(),
      },
      events,
    };
  }

  return {
    state: {
      ...state,
      beeBounce: {
        ...beeBounce,
        bounceWindow: newWindow,
      },
    },
    events,
  };
}

// =============================================================================
// Momentum System
// =============================================================================

/**
 * Add a momentum stack
 */
export function addMomentumStack(
  momentum: Record<MomentumType, MomentumStack>,
  type: MomentumType,
  gameTime: number
): Record<MomentumType, MomentumStack> {
  const stack = momentum[type];
  const newStacks = Math.min(stack.stacks + 1, stack.maxStacks);

  return {
    ...momentum,
    [type]: {
      ...stack,
      stacks: newStacks,
      lastStackTime: gameTime,
    },
  };
}

/**
 * Update momentum stacks (decay)
 */
export function updateMomentum(
  momentum: Record<MomentumType, MomentumStack>,
  deltaTime: number,
  gameTime: number
): { momentum: Record<MomentumType, MomentumStack>; events: ComboEvent[] } {
  const events: ComboEvent[] = [];
  const newMomentum = { ...momentum };

  for (const type of Object.keys(momentum) as MomentumType[]) {
    const stack = momentum[type];
    if (stack.stacks <= 0) continue;

    // Check if within window
    const timeSinceStack = gameTime - stack.lastStackTime;
    if (timeSinceStack > stack.window) {
      // Decay stacks
      const decay = stack.decayRate * (deltaTime / 1000);
      const newStacks = Math.max(0, stack.stacks - decay);

      if (newStacks <= 0 && stack.stacks > 0) {
        events.push({ type: 'momentum_lost', momentumType: type });
      }

      newMomentum[type] = {
        ...stack,
        stacks: newStacks,
      };
    }
  }

  return { momentum: newMomentum, events };
}

/**
 * Calculate total momentum multiplier
 */
export function calculateMomentumMultiplier(momentum: Record<MomentumType, MomentumStack>): number {
  let multiplier = 1.0;

  for (const type of Object.keys(momentum) as MomentumType[]) {
    const stack = momentum[type];
    if (stack.stacks > 0) {
      multiplier *= 1 + (stack.stacks * stack.bonusPerStack);
    }
  }

  return multiplier;
}

// =============================================================================
// Graze Chain System
// =============================================================================

/**
 * Process a graze event
 */
export function processGraze(
  state: InsaneComboState,
  enemyPosition: Vector2,
  gameTime: number
): { state: InsaneComboState; events: ComboEvent[] } {
  const events: ComboEvent[] = [];

  // Check if continuing streak
  const isContinuing = state.timeSinceGraze < GRAZE_CONFIG.grazeDecayTime;
  const newStreak = isContinuing ? state.grazeStreak + 1 : 1;

  // Calculate bonuses
  const damageBonus = Math.min(
    newStreak * GRAZE_CONFIG.damagePerGraze,
    GRAZE_CONFIG.maxGrazeStacks * GRAZE_CONFIG.damagePerGraze
  );
  const speedBonus = Math.min(
    newStreak * GRAZE_CONFIG.speedPerGraze,
    GRAZE_CONFIG.maxGrazeStacks * GRAZE_CONFIG.speedPerGraze
  );

  events.push({
    type: 'graze_chain',
    streak: newStreak,
    bonus: damageBonus,
  });

  // Add momentum
  const newMomentum = addMomentumStack(state.momentum, 'graze_streak', gameTime);

  const newState: InsaneComboState = {
    ...state,
    grazeStreak: newStreak,
    grazeDamageBonus: damageBonus,
    grazeSpeedBonus: speedBonus,
    timeSinceGraze: 0,
    momentum: newMomentum,
  };

  return {
    state: recalculateTotalMultiplier(newState),
    events,
  };
}

/**
 * Update graze state (decay)
 */
export function updateGraze(
  state: InsaneComboState,
  deltaTime: number
): InsaneComboState {
  const newTimeSinceGraze = state.timeSinceGraze + deltaTime;

  if (newTimeSinceGraze > GRAZE_CONFIG.grazeDecayTime && state.grazeStreak > 0) {
    // Reset graze streak
    return {
      ...state,
      grazeStreak: 0,
      grazeDamageBonus: 0,
      grazeSpeedBonus: 0,
      timeSinceGraze: newTimeSinceGraze,
    };
  }

  return {
    ...state,
    timeSinceGraze: newTimeSinceGraze,
  };
}

// =============================================================================
// Chain Kill System
// =============================================================================

/**
 * Mark enemies for chain kill
 */
export function markChainTargets(
  state: InsaneComboState,
  killedPosition: Vector2,
  enemies: Enemy[],
  gameTime: number
): { state: InsaneComboState; targets: ChainTarget[] } {
  const { chainRange } = state;
  const targets: ChainTarget[] = [];
  let chainOrder = 1;

  // Find enemies in range, sorted by distance
  const inRange = enemies
    .filter(e => {
      const dx = e.position.x - killedPosition.x;
      const dy = e.position.y - killedPosition.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      return dist <= chainRange && e.health > 0;
    })
    .sort((a, b) => {
      const distA = Math.sqrt((a.position.x - killedPosition.x) ** 2 + (a.position.y - killedPosition.y) ** 2);
      const distB = Math.sqrt((b.position.x - killedPosition.x) ** 2 + (b.position.y - killedPosition.y) ** 2);
      return distA - distB;
    })
    .slice(0, CHAIN_KILL_CONFIG.maxChainLength);

  // Create chain targets
  for (const enemy of inRange) {
    targets.push({
      enemyId: enemy.id,
      position: { ...enemy.position },
      damage: Math.floor(25 * CHAIN_KILL_CONFIG.chainDamageMultiplier * state.chainKillMultiplier),
      expiryTime: gameTime + (chainOrder * CHAIN_KILL_CONFIG.chainDelayMs) + 500,
      chainOrder,
    });
    chainOrder++;
  }

  return {
    state: {
      ...state,
      chainTargets: [...state.chainTargets, ...targets],
      chainRange: chainRange + (targets.length * CHAIN_KILL_CONFIG.chainRangePerKill),
    },
    targets,
  };
}

/**
 * Process chain kills (called each frame)
 */
export function processChainKills(
  state: InsaneComboState,
  enemies: Enemy[],
  gameTime: number
): { state: InsaneComboState; killEvents: Array<{ enemyId: string; damage: number }>; events: ComboEvent[] } {
  const killEvents: Array<{ enemyId: string; damage: number }> = [];
  const events: ComboEvent[] = [];
  const remainingTargets: ChainTarget[] = [];

  for (const target of state.chainTargets) {
    // Check if this chain should trigger
    const triggerTime = target.expiryTime - 500 + (target.chainOrder * CHAIN_KILL_CONFIG.chainDelayMs);
    if (gameTime >= triggerTime) {
      // Find the enemy
      const enemy = enemies.find(e => e.id === target.enemyId);
      if (enemy && enemy.health > 0) {
        killEvents.push({ enemyId: target.enemyId, damage: target.damage });
        events.push({
          type: 'chain_kill',
          chainLength: target.chainOrder,
          position: target.position,
        });
      }
    } else if (gameTime < target.expiryTime) {
      remainingTargets.push(target);
    }
  }

  return {
    state: {
      ...state,
      chainTargets: remainingTargets,
    },
    killEvents,
    events,
  };
}

// =============================================================================
// Combo Window System
// =============================================================================

/**
 * Start a combo window
 */
export function startComboWindow(
  state: InsaneComboState,
  _gameTime: number
): InsaneComboState {
  return {
    ...state,
    comboWindowRemaining: COMBO_WINDOW_CONFIG.baseWindow,
    comboWindowMultiplier: 1.0,
  };
}

/**
 * Process action during combo window
 */
export function processComboWindow(
  state: InsaneComboState,
  isPerfect: boolean,
  gameTime: number
): { state: InsaneComboState; events: ComboEvent[] } {
  const events: ComboEvent[] = [];

  if (state.comboWindowRemaining <= 0) {
    // Not in combo window
    return { state: startComboWindow(state, gameTime), events };
  }

  // Check if perfect timing
  const perfectWindow = COMBO_WINDOW_CONFIG.perfectWindow;
  const timingPerfect = isPerfect || state.comboWindowRemaining > (COMBO_WINDOW_CONFIG.baseWindow - perfectWindow);

  if (timingPerfect) {
    const newStreak = state.perfectWindowStreak + 1;
    const streakBonus = Math.min(
      1 + (newStreak * COMBO_WINDOW_CONFIG.perfectStreakBonus),
      COMBO_WINDOW_CONFIG.maxStreakBonus
    );

    events.push({
      type: 'perfect_window',
      streak: newStreak,
      multiplier: streakBonus,
    });

    // Add momentum
    const newMomentum = addMomentumStack(state.momentum, 'perfect_timing', gameTime);

    return {
      state: {
        ...state,
        perfectWindowStreak: newStreak,
        comboWindowMultiplier: streakBonus,
        comboWindowRemaining: COMBO_WINDOW_CONFIG.baseWindow + COMBO_WINDOW_CONFIG.windowExtensionPerKill,
        momentum: newMomentum,
      },
      events,
    };
  }

  // Normal window hit (not perfect)
  return {
    state: {
      ...state,
      perfectWindowStreak: 0,
      comboWindowRemaining: state.comboWindowRemaining + COMBO_WINDOW_CONFIG.windowExtensionPerKill,
    },
    events,
  };
}

/**
 * Update combo window (decay)
 */
export function updateComboWindow(
  state: InsaneComboState,
  deltaTime: number
): { state: InsaneComboState; events: ComboEvent[] } {
  const events: ComboEvent[] = [];

  if (state.comboWindowRemaining <= 0) {
    return { state, events };
  }

  const newRemaining = state.comboWindowRemaining - deltaTime;

  if (newRemaining <= 0) {
    // Combo window expired
    if (state.perfectWindowStreak > 0) {
      events.push({
        type: 'combo_broken',
        wasAt: state.totalComboMultiplier,
      });
    }

    return {
      state: {
        ...state,
        comboWindowRemaining: 0,
        comboWindowMultiplier: 1.0,
        perfectWindowStreak: 0,
      },
      events,
    };
  }

  return {
    state: {
      ...state,
      comboWindowRemaining: newRemaining,
    },
    events,
  };
}

// =============================================================================
// Perk Synergy System
// =============================================================================

/**
 * Check for active perk synergies
 */
export function checkPerkSynergies(
  ownedAbilities: AbilityId[]
): PerkSynergy[] {
  const activeSynergies: PerkSynergy[] = [];

  for (const synergy of PERK_SYNERGIES) {
    const [perk1, perk2] = synergy.perks;
    if (ownedAbilities.includes(perk1) && ownedAbilities.includes(perk2)) {
      activeSynergies.push(synergy);
    }
  }

  return activeSynergies;
}

/**
 * Check for unlocked transcendent abilities
 */
export function checkTranscendentAbilities(
  activeSynergies: PerkSynergy[]
): TranscendentAbility[] {
  const unlocked: TranscendentAbility[] = [];

  for (const ability of TRANSCENDENT_ABILITIES) {
    if (activeSynergies.length >= ability.requiredSynergies) {
      unlocked.push(ability);
    }
  }

  return unlocked;
}

/**
 * Update synergies when abilities change
 */
export function updateSynergies(
  state: InsaneComboState,
  ownedAbilities: AbilityId[]
): { state: InsaneComboState; events: ComboEvent[] } {
  const events: ComboEvent[] = [];

  const newSynergies = checkPerkSynergies(ownedAbilities);
  const newTranscendent = checkTranscendentAbilities(newSynergies);

  // Check for newly activated synergies
  for (const synergy of newSynergies) {
    if (!state.activeSynergies.find(s => s.id === synergy.id)) {
      events.push({ type: 'synergy_activated', synergy });
    }
  }

  // Check for newly unlocked transcendent abilities
  for (const ability of newTranscendent) {
    if (!state.transcendentAbilities.find(a => a.id === ability.id)) {
      events.push({ type: 'transcendent_unlocked', ability });
    }
  }

  return {
    state: {
      ...state,
      activeSynergies: newSynergies,
      transcendentAbilities: newTranscendent,
    },
    events,
  };
}

// =============================================================================
// Total Multiplier Calculation
// =============================================================================

/**
 * Recalculate total combo multiplier
 */
export function recalculateTotalMultiplier(state: InsaneComboState): InsaneComboState {
  let total = 1.0;

  // Momentum stacks
  total *= calculateMomentumMultiplier(state.momentum);

  // Bee bounce
  if (state.beeBounce.isBouncing) {
    total *= state.beeBounce.damageMultiplier;
  }

  // Graze bonus
  total *= 1 + state.grazeDamageBonus;

  // Combo window bonus
  total *= state.comboWindowMultiplier;

  // Synergy bonuses
  for (const synergy of state.activeSynergies) {
    if (synergy.effect.damageMultiplier) {
      total *= synergy.effect.damageMultiplier;
    }
  }

  // Transcendent bonuses
  for (const ability of state.transcendentAbilities) {
    if (ability.effect.damageMultiplier) {
      total *= ability.effect.damageMultiplier;
    }
  }

  // Determine tier
  let newTier: ComboTier = 'basic';
  if (total >= TIER_THRESHOLDS.transcendent) {
    newTier = 'transcendent';
  } else if (total >= TIER_THRESHOLDS.legendary) {
    newTier = 'legendary';
  } else if (total >= TIER_THRESHOLDS.advanced) {
    newTier = 'advanced';
  }

  // Calculate visual intensity
  const intensity = Math.min(1, (total - 1) / 7); // 0-1 based on multiplier

  // Time dilation (slow-mo at high combo)
  const timeDilation = newTier === 'transcendent' ? 0.7 : newTier === 'legendary' ? 0.85 : 1.0;

  // Particle multiplier
  const particleMult = 1 + (total - 1) * 0.5;

  return {
    ...state,
    totalComboMultiplier: total,
    highestCombo: Math.max(state.highestCombo, total),
    currentTier: newTier,
    screenIntensity: intensity,
    timeDilation,
    particleMultiplier: particleMult,
  };
}

// =============================================================================
// Main Update Function
// =============================================================================

/**
 * Update the entire insane combo system
 */
export function updateInsaneComboSystem(
  state: InsaneComboState,
  deltaTime: number,
  gameTime: number
): { state: InsaneComboState; events: ComboEvent[] } {
  let currentState = state;
  const allEvents: ComboEvent[] = [];

  // Update bee bounce
  const bounceResult = updateBeeBounce(currentState, deltaTime);
  currentState = bounceResult.state;
  allEvents.push(...bounceResult.events);

  // Update momentum
  const momentumResult = updateMomentum(currentState.momentum, deltaTime, gameTime);
  currentState = { ...currentState, momentum: momentumResult.momentum };
  allEvents.push(...momentumResult.events);

  // Update graze
  currentState = updateGraze(currentState, deltaTime);

  // Update combo window
  const windowResult = updateComboWindow(currentState, deltaTime);
  currentState = windowResult.state;
  allEvents.push(...windowResult.events);

  // Recalculate total
  currentState = recalculateTotalMultiplier(currentState);

  // Check for tier change
  if (currentState.currentTier !== state.currentTier) {
    allEvents.push({ type: 'tier_up', newTier: currentState.currentTier });
  }

  return { state: currentState, events: allEvents };
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Get combo tier display name
 */
export function getComboTierDisplayName(tier: ComboTier): string {
  switch (tier) {
    case 'basic': return 'COMBO';
    case 'advanced': return 'SUPER COMBO';
    case 'legendary': return 'LEGENDARY COMBO';
    case 'transcendent': return 'TRANSCENDENT';
  }
}

/**
 * Get combo tier color
 */
export function getComboTierColor(tier: ComboTier): string {
  switch (tier) {
    case 'basic': return '#FFFFFF';
    case 'advanced': return '#FFD700';
    case 'legendary': return '#FF6600';
    case 'transcendent': return '#FF00FF';
  }
}

/**
 * Apply combo multiplier to damage
 */
export function applyComboMultiplier(
  baseDamage: number,
  state: InsaneComboState
): number {
  return Math.floor(baseDamage * state.totalComboMultiplier);
}

/**
 * Apply combo speed bonus
 */
export function applyComboSpeedBonus(
  baseSpeed: number,
  state: InsaneComboState
): number {
  let speed = baseSpeed;

  // Graze speed bonus
  speed *= 1 + state.grazeSpeedBonus;

  // Bounce speed bonus
  if (state.beeBounce.isBouncing) {
    speed += state.beeBounce.bonusSpeed;
  }

  // Synergy speed bonuses
  for (const synergy of state.activeSynergies) {
    if (synergy.effect.speedMultiplier) {
      speed *= synergy.effect.speedMultiplier;
    }
  }

  return speed;
}

// =============================================================================
// Export
// =============================================================================

export default {
  // Constants
  BEE_BOUNCE_CONFIG,
  MOMENTUM_CONFIG,
  COMBO_WINDOW_CONFIG,
  GRAZE_CONFIG,
  CHAIN_KILL_CONFIG,
  TIER_THRESHOLDS,
  PERK_SYNERGIES,
  TRANSCENDENT_ABILITIES,

  // Factories
  createInitialInsaneComboState,
  createInitialBeeBounceState,
  createInitialMomentumStacks,

  // Bee Bounce
  calculateBounceDirection,
  processBeeBounce,
  updateBeeBounce,

  // Momentum
  addMomentumStack,
  updateMomentum,
  calculateMomentumMultiplier,

  // Graze
  processGraze,
  updateGraze,

  // Chain Kill
  markChainTargets,
  processChainKills,

  // Combo Window
  startComboWindow,
  processComboWindow,
  updateComboWindow,

  // Synergies
  checkPerkSynergies,
  checkTranscendentAbilities,
  updateSynergies,

  // Total
  recalculateTotalMultiplier,
  updateInsaneComboSystem,

  // Utilities
  getComboTierDisplayName,
  getComboTierColor,
  applyComboMultiplier,
  applyComboSpeedBonus,
};
