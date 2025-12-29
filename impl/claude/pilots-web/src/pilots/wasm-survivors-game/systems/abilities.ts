/**
 * WASM Survivors - Simplified Ability System (Run 036 v2)
 *
 * 24 abilities across 4 clear categories. Each ability is:
 * - Immediately understandable (no wiki required)
 * - Clearly impactful (you FEEL the difference)
 * - Simple description (one effect, clearly stated)
 *
 * DESIGN PHILOSOPHY:
 * > "If it needs an explanation, it's too complex."
 * > "Every ability should make you go 'oh hell yes'."
 *
 * @see pilots/wasm-survivors-game/runs/run-036
 */

// =============================================================================
// Types
// =============================================================================

/**
 * Four clear categories
 */
export type AbilityCategory =
  | 'damage'   // Make your bite hurt more
  | 'speed'    // Attack faster, move faster
  | 'defense'  // Take less damage, heal more
  | 'special'; // Unique powerful effects

/**
 * All ability IDs - 24 total (6 per category)
 */
export type AbilityId =
  // DAMAGE (6) - Pure damage increases
  | 'sharpened_mandibles'    // +40% damage
  | 'crushing_bite'          // +75% damage
  | 'venomous_strike'        // +12 poison damage per hit
  | 'double_strike'          // 40% chance to hit twice
  | 'savage_blow'            // +150% damage to low HP enemies
  | 'giant_killer'           // +300% damage to high HP enemies
  // SPEED (6) - Attack and movement speed
  | 'quick_strikes'          // +50% attack speed
  | 'frenzy'                 // +80% attack speed
  | 'swift_wings'            // +40% movement speed
  | 'hunters_rush'           // +60% speed toward enemies
  | 'berserker_pace'         // +35% attack AND move speed
  | 'bullet_time'            // +50% attack AND move speed
  // DEFENSE (6) - Survivability
  | 'thick_carapace'         // +75 max HP
  | 'hardened_shell'         // -40% damage taken
  | 'regeneration'           // +5 HP per second
  | 'lifesteal'              // Heal 25% of damage dealt
  | 'last_stand'             // +90% defense below 30% HP
  | 'second_wind'            // Revive once per run at 75% HP
  // SPECIAL (6) - Unique effects
  | 'critical_sting'         // 30% chance for 2x damage
  | 'execution'              // Instant kill below 20% HP
  | 'sweeping_arc'           // Attack hits 360 degrees
  | 'chain_lightning'        // Kills chain to nearby enemy
  | 'momentum'               // +15% per kill (max 75%)
  | 'glass_cannon'           // +150% damage, -40% HP
  // SPECIAL SKILL-GATED (5) - Overpowered but require mastery
  | 'graze_frenzy'           // Near-misses stack bonuses, hit resets
  | 'thermal_momentum'       // Movement builds heat, release pulse
  | 'execution_chain'        // Kill low-HP chains to wounded
  | 'glass_cannon_mastery'   // 1 HP, 500% damage, 50% faster
  | 'venom_architect';       // Infinite venom stacks, explode on kill

/**
 * Skill demand - how hard to use
 */
export type SkillDemand = 'easy' | 'medium' | 'hard';

/**
 * Base ability definition
 */
export interface Ability {
  id: AbilityId;
  name: string;
  description: string;  // ONE simple sentence
  verb: string;         // Action verb for UI (e.g., "Sharpen", "Strike")
  category: AbilityCategory;
  icon: string;
  color: string;

  // Simple effect values
  effect: AbilityEffect;

  // Optional: stacks with itself?
  stackable?: boolean;
  maxStacks?: number;

  // Risk indicator
  isRiskReward?: boolean;

  // Combo potential (for UI hints)
  comboPotential?: 'low' | 'medium' | 'high';
}

/**
 * What the ability actually does - simplified
 */
export interface AbilityEffect {
  // Damage modifiers
  damagePercent?: number;        // +X% damage
  flatDamage?: number;           // +X flat damage
  lowHpBonusDamage?: number;     // +X% damage to enemies below 50% HP
  highHpBonusDamage?: number;    // +X% damage to enemies above 75% HP
  poisonDamage?: number;         // X damage over 3 seconds
  doubleHitChance?: number;      // X% chance to hit twice

  // Speed modifiers
  attackSpeedPercent?: number;   // +X% attack speed
  moveSpeedPercent?: number;     // +X% movement speed

  // Defense modifiers
  maxHpBonus?: number;           // +X max HP
  damageReduction?: number;      // -X% damage taken
  hpPerSecond?: number;          // +X HP per second
  lifestealPercent?: number;     // Heal X% of damage dealt
  lowHpDefenseBonus?: number;    // +X% defense below 30% HP
  reviveOnce?: boolean;          // Revive at 50% HP once

  // Special effects
  critChance?: number;           // X% chance for 2x damage
  executeThreshold?: number;     // Instant kill below X% HP
  fullArc?: boolean;             // 360 degree attacks
  chainOnKill?: boolean;         // Kills chain to nearby
  killStreakDamage?: number;     // +X% per consecutive kill

  // Glass cannon
  damageMultiplier?: number;     // Xх damage
  hpMultiplier?: number;         // Xх HP (can reduce)

  // Skill-gated special effects
  grazeStackBonus?: boolean;     // Near-misses grant stacking bonuses
  thermalMomentum?: boolean;     // Movement builds heat for damage pulse
  executionChain?: boolean;      // Kill low-HP chains to wounded targets
  glassCannonMastery?: boolean;  // 1 HP, massive damage/speed boost
  venomArchitect?: boolean;      // Infinite venom stacks, explode on kill
}

/**
 * Player's active abilities state
 */
export interface ActiveAbilities {
  owned: AbilityId[];
  levels: Record<AbilityId, number>;  // For stackable abilities

  // Computed effects (sum of all abilities)
  computed: ComputedEffects;
}

/**
 * Aggregated effects from all abilities
 */
export interface ComputedEffects {
  // Damage
  damageMultiplier: number;      // Total damage multiplier
  flatDamage: number;            // Flat damage bonus
  lowHpBonusDamage: number;      // Bonus vs low HP enemies
  highHpBonusDamage: number;     // Bonus vs high HP enemies
  poisonDamage: number;          // Poison damage per hit
  doubleHitChance: number;       // Chance to hit twice

  // Speed
  attackSpeedBonus: number;      // Attack speed multiplier
  speedMultiplier: number;       // Movement speed multiplier

  // Defense
  maxHpBonus: number;            // Flat HP bonus
  damageReduction: number;       // Damage reduction %
  hpPerSecond: number;           // Passive regen
  lifestealPercent: number;      // Lifesteal %
  lowHpDefenseBonus: number;     // Defense when low
  hasRevive: boolean;            // Can revive once

  // Special
  critChance: number;            // Crit chance %
  critDamageMultiplier: number;  // Always 2x for simplicity
  executeThreshold: number;      // Execute HP threshold
  hasFullArc: boolean;           // 360 attacks
  hasChainKill: boolean;         // Chain kills
  killStreakDamage: number;      // Damage per kill streak

  // Status flags
  hasRiskReward: boolean;
  hasDoubleHit: boolean;
  hasExecution: boolean;

  // Skill-gated ability flags
  hasGrazeFrenzy: boolean;         // Near-misses stack bonuses, hit resets
  hasThermalMomentum: boolean;     // Build heat while moving, release damage pulse on stop
  hasExecutionChain: boolean;      // Kill low-HP chains to wounded targets
  hasGlassCannonMastery: boolean;  // 1 HP, 500% damage, 50% faster
  hasVenomArchitect: boolean;      // Infinite venom stacks, explode on kill

  // Legacy compatibility
  diveSpeedMultiplier: number;
  hoverAttackSpeedBonus: number;
  bleedEnabled: boolean;
  bleedDamage: number;
  venomEnabled: boolean;
  venomType: 'none' | 'hemotoxic' | 'neurotoxic';
  heatReduction: number;
  activeFrenzyStacks: number;
  isHollowCarapace: boolean;
  isBerserker: boolean;
}

// =============================================================================
// Damage Cap
// =============================================================================

export const MAX_DAMAGE_MULTIPLIER = 3.0;

// =============================================================================
// DAMAGE ABILITIES (6)
// =============================================================================

const DAMAGE_ABILITIES: Ability[] = [
  {
    id: 'sharpened_mandibles',
    name: 'Sharpened Mandibles',
    description: '+40% damage',
    verb: 'Sharpen',
    category: 'damage',
    icon: '🦷',
    color: '#FF6600',
    stackable: true,
    maxStacks: 3,
    comboPotential: 'medium',
    effect: {
      damagePercent: 40,
    },
  },
  {
    id: 'crushing_bite',
    name: 'Crushing Bite',
    description: '+75% damage',
    verb: 'Crush',
    category: 'damage',
    icon: '💪',
    color: '#CC4400',
    comboPotential: 'high',
    effect: {
      damagePercent: 75,
    },
  },
  {
    id: 'venomous_strike',
    name: 'Venomous Strike',
    description: 'Attacks deal +12 poison damage over 3s',
    verb: 'Envenom',
    category: 'damage',
    icon: '☠️',
    color: '#88FF00',
    stackable: true,
    maxStacks: 3,
    comboPotential: 'high',
    effect: {
      poisonDamage: 12,
    },
  },
  {
    id: 'double_strike',
    name: 'Double Strike',
    description: '40% chance to hit twice',
    verb: 'Double',
    category: 'damage',
    icon: '⚔️',
    color: '#FF4488',
    comboPotential: 'high',
    effect: {
      doubleHitChance: 40,
    },
  },
  {
    id: 'savage_blow',
    name: 'Savage Blow',
    description: '+150% damage to enemies below 50% HP',
    verb: 'Savage',
    category: 'damage',
    icon: '🔥',
    color: '#FF0000',
    comboPotential: 'high',
    effect: {
      lowHpBonusDamage: 150,
    },
  },
  {
    id: 'giant_killer',
    name: 'Giant Killer',
    description: '+300% damage to enemies above 75% HP',
    verb: 'Slay',
    category: 'damage',
    icon: '🎯',
    color: '#00AAFF',
    comboPotential: 'medium',
    effect: {
      highHpBonusDamage: 300,
    },
  },
];

// =============================================================================
// SPEED ABILITIES (6)
// =============================================================================

const SPEED_ABILITIES: Ability[] = [
  {
    id: 'quick_strikes',
    name: 'Quick Strikes',
    description: '+50% attack speed',
    verb: 'Quicken',
    category: 'speed',
    icon: '⚡',
    color: '#FFDD00',
    stackable: true,
    maxStacks: 3,
    comboPotential: 'high',
    effect: {
      attackSpeedPercent: 50,
    },
  },
  {
    id: 'frenzy',
    name: 'Frenzy',
    description: '+80% attack speed',
    verb: 'Frenzy',
    category: 'speed',
    icon: '💨',
    color: '#FF8800',
    comboPotential: 'high',
    effect: {
      attackSpeedPercent: 80,
    },
  },
  {
    id: 'swift_wings',
    name: 'Swift Wings',
    description: '+40% movement speed',
    verb: 'Swiften',
    category: 'speed',
    icon: '🦋',
    color: '#88CCFF',
    stackable: true,
    maxStacks: 3,
    comboPotential: 'high',
    effect: {
      moveSpeedPercent: 40,
    },
  },
  {
    id: 'hunters_rush',
    name: "Hunter's Rush",
    description: '+60% speed when moving toward enemies',
    verb: 'Hunt',
    category: 'speed',
    icon: '🏃',
    color: '#FF4444',
    comboPotential: 'high',
    effect: {
      moveSpeedPercent: 60,  // Applied contextually
    },
  },
  {
    id: 'berserker_pace',
    name: 'Berserker Pace',
    description: '+35% attack AND movement speed',
    verb: 'Rampage',
    category: 'speed',
    icon: '🔄',
    color: '#FF6666',
    comboPotential: 'high',
    effect: {
      attackSpeedPercent: 35,
      moveSpeedPercent: 35,
    },
  },
  {
    id: 'bullet_time',
    name: 'Bullet Time',
    description: 'Time slows for enemies, not you (+50% both speeds)',
    verb: 'Slow',
    category: 'speed',
    icon: '⏱️',
    color: '#9999FF',
    comboPotential: 'high',
    effect: {
      attackSpeedPercent: 50,
      moveSpeedPercent: 50,
    },
  },
];

// =============================================================================
// DEFENSE ABILITIES (6)
// =============================================================================

const DEFENSE_ABILITIES: Ability[] = [
  {
    id: 'thick_carapace',
    name: 'Thick Carapace',
    description: '+75 max HP',
    verb: 'Fortify',
    category: 'defense',
    icon: '🛡️',
    color: '#888888',
    stackable: true,
    maxStacks: 3,
    comboPotential: 'high',
    effect: {
      maxHpBonus: 75,
    },
  },
  {
    id: 'hardened_shell',
    name: 'Hardened Shell',
    description: '-40% damage taken',
    verb: 'Harden',
    category: 'defense',
    icon: '🐢',
    color: '#668866',
    comboPotential: 'high',
    effect: {
      damageReduction: 40,
    },
  },
  {
    id: 'regeneration',
    name: 'Regeneration',
    description: '+5 HP per second',
    verb: 'Regenerate',
    category: 'defense',
    icon: '💚',
    color: '#00FF66',
    stackable: true,
    maxStacks: 3,
    comboPotential: 'high',
    effect: {
      hpPerSecond: 5,
    },
  },
  {
    id: 'lifesteal',
    name: 'Lifesteal',
    description: 'Heal 25% of damage dealt',
    verb: 'Drain',
    category: 'defense',
    icon: '🧛',
    color: '#FF0066',
    comboPotential: 'high',
    effect: {
      lifestealPercent: 25,
    },
  },
  {
    id: 'last_stand',
    name: 'Last Stand',
    description: '+90% defense when below 30% HP',
    verb: 'Endure',
    category: 'defense',
    icon: '💀',
    color: '#880000',
    comboPotential: 'high',
    effect: {
      lowHpDefenseBonus: 90,
    },
  },
  {
    id: 'second_wind',
    name: 'Second Wind',
    description: 'Revive once per run at 75% HP',
    verb: 'Revive',
    category: 'defense',
    icon: '✨',
    color: '#FFDD88',
    comboPotential: 'high',
    effect: {
      reviveOnce: true,
    },
  },
];

// =============================================================================
// SPECIAL ABILITIES (6)
// =============================================================================

const SPECIAL_ABILITIES: Ability[] = [
  {
    id: 'critical_sting',
    name: 'Critical Sting',
    description: '30% chance for 2x damage',
    verb: 'Crit',
    category: 'special',
    icon: '💥',
    color: '#FFAA00',
    stackable: true,
    maxStacks: 3,
    comboPotential: 'high',
    effect: {
      critChance: 30,
    },
  },
  {
    id: 'execution',
    name: 'Execution',
    description: 'Instant kill enemies below 20% HP',
    verb: 'Execute',
    category: 'special',
    icon: '⚰️',
    color: '#440000',
    comboPotential: 'high',
    effect: {
      executeThreshold: 20,
    },
  },
  {
    id: 'sweeping_arc',
    name: 'Sweeping Arc',
    description: 'Attack hits all around you (360°)',
    verb: 'Sweep',
    category: 'special',
    icon: '🌀',
    color: '#FF8844',
    comboPotential: 'high',
    effect: {
      fullArc: true,
    },
  },
  {
    id: 'chain_lightning',
    name: 'Chain Lightning',
    description: 'Kills chain to a nearby enemy',
    verb: 'Chain',
    category: 'special',
    icon: '⚡',
    color: '#4488FF',
    comboPotential: 'high',
    effect: {
      chainOnKill: true,
    },
  },
  {
    id: 'momentum',
    name: 'Momentum',
    description: '+15% damage per consecutive kill (max 75%)',
    verb: 'Build',
    category: 'special',
    icon: '🚀',
    color: '#FF44FF',
    comboPotential: 'high',
    effect: {
      killStreakDamage: 15,
    },
  },
  {
    id: 'glass_cannon',
    name: 'Glass Cannon',
    description: '+150% damage, but -40% max HP',
    verb: 'Risk',
    category: 'special',
    icon: '💎',
    color: '#FF0000',
    isRiskReward: true,
    comboPotential: 'high',
    effect: {
      damageMultiplier: 2.5,
      hpMultiplier: 0.6,
    },
  },
  // =========================================================================
  // SKILL-GATED ABILITIES (5) - Overpowered but require mastery
  // =========================================================================
  {
    id: 'graze_frenzy',
    name: 'Graze Frenzy',
    description: 'Near-misses grant stacking attack speed and damage. Getting hit resets all stacks.',
    verb: 'Graze',
    category: 'special',
    icon: '💫',
    color: '#FF00FF',
    isRiskReward: true,
    comboPotential: 'high',
    effect: {
      grazeStackBonus: true,
    },
  },
  {
    id: 'thermal_momentum',
    name: 'Thermal Momentum',
    description: 'Build heat while moving. Stop to release a damage pulse.',
    verb: 'Heat',
    category: 'special',
    icon: '🔥',
    color: '#FF4400',
    comboPotential: 'high',
    effect: {
      thermalMomentum: true,
    },
  },
  {
    id: 'execution_chain',
    name: 'Execution Chain',
    description: 'Killing low-HP enemies chains to the next wounded target.',
    verb: 'Chain',
    category: 'special',
    icon: '⛓️',
    color: '#880000',
    comboPotential: 'high',
    effect: {
      executionChain: true,
    },
  },
  {
    id: 'glass_cannon_mastery',
    name: 'Glass Cannon Mastery',
    description: 'Set HP to 1. Deal 500% damage and move 50% faster.',
    verb: 'Master',
    category: 'special',
    icon: '💀',
    color: '#FF0000',
    isRiskReward: true,
    comboPotential: 'high',
    effect: {
      glassCannonMastery: true,
    },
  },
  {
    id: 'venom_architect',
    name: 'Venom Architect',
    description: 'Venom stacks infinitely. Enemies killed BY venom explode.',
    verb: 'Architect',
    category: 'special',
    icon: '☠️',
    color: '#00FF00',
    comboPotential: 'high',
    effect: {
      venomArchitect: true,
    },
  },
];

// =============================================================================
// Combined Ability Pool
// =============================================================================

const ALL_ABILITIES: Ability[] = [
  ...DAMAGE_ABILITIES,
  ...SPEED_ABILITIES,
  ...DEFENSE_ABILITIES,
  ...SPECIAL_ABILITIES,
];

// Lookup map
const ABILITY_MAP = new Map<AbilityId, Ability>(
  ALL_ABILITIES.map(a => [a.id, a])
);

// =============================================================================
// Ability Functions
// =============================================================================

/**
 * Get ability by ID
 */
export function getAbility(id: AbilityId): Ability | undefined {
  return ABILITY_MAP.get(id);
}

/**
 * Get all abilities
 */
export function getAllAbilities(): Ability[] {
  return [...ALL_ABILITIES];
}

/**
 * Get abilities by category
 */
export function getAbilitiesByCategory(category: AbilityCategory): Ability[] {
  return ALL_ABILITIES.filter(a => a.category === category);
}

/**
 * Create initial abilities state
 */
export function createInitialAbilities(): ActiveAbilities {
  return {
    owned: [],
    levels: {} as Record<AbilityId, number>,
    computed: createDefaultComputed(),
  };
}

/**
 * Create default computed effects
 */
function createDefaultComputed(): ComputedEffects {
  return {
    // Damage
    damageMultiplier: 1.0,
    flatDamage: 0,
    lowHpBonusDamage: 0,
    highHpBonusDamage: 0,
    poisonDamage: 0,
    doubleHitChance: 0,

    // Speed
    attackSpeedBonus: 0,
    speedMultiplier: 1.0,

    // Defense
    maxHpBonus: 0,
    damageReduction: 0,
    hpPerSecond: 0,
    lifestealPercent: 0,
    lowHpDefenseBonus: 0,
    hasRevive: false,

    // Special
    critChance: 0,
    critDamageMultiplier: 2.0,  // Always 2x
    executeThreshold: 0,
    hasFullArc: false,
    hasChainKill: false,
    killStreakDamage: 0,

    // Status
    hasRiskReward: false,
    hasDoubleHit: false,
    hasExecution: false,

    // Skill-gated ability flags
    hasGrazeFrenzy: false,
    hasThermalMomentum: false,
    hasExecutionChain: false,
    hasGlassCannonMastery: false,
    hasVenomArchitect: false,

    // Legacy compatibility
    diveSpeedMultiplier: 1.0,
    hoverAttackSpeedBonus: 0,
    bleedEnabled: false,
    bleedDamage: 0,
    venomEnabled: false,
    venomType: 'none',
    heatReduction: 0,
    activeFrenzyStacks: 0,
    isHollowCarapace: false,
    isBerserker: false,
  };
}

/**
 * Add ability and recompute effects
 */
export function addAbility(
  abilities: ActiveAbilities,
  abilityId: AbilityId
): ActiveAbilities {
  const ability = getAbility(abilityId);
  if (!ability) return abilities;

  // Check if already owned (and not stackable)
  if (abilities.owned.includes(abilityId) && !ability.stackable) {
    return abilities;
  }

  // Check stack limit
  const currentLevel = abilities.levels[abilityId] || 0;
  if (ability.stackable && ability.maxStacks && currentLevel >= ability.maxStacks) {
    return abilities;
  }

  // Add or stack
  const newOwned = abilities.owned.includes(abilityId)
    ? abilities.owned
    : [...abilities.owned, abilityId];

  const newLevels = {
    ...abilities.levels,
    [abilityId]: currentLevel + 1,
  };

  // Recompute effects
  const computed = computeEffects(newOwned, newLevels);

  return {
    owned: newOwned,
    levels: newLevels,
    computed,
  };
}

/**
 * Compute aggregated effects from all abilities
 */
function computeEffects(
  owned: AbilityId[],
  levels: Record<AbilityId, number>
): ComputedEffects {
  const computed = createDefaultComputed();

  for (const id of owned) {
    const ability = getAbility(id);
    if (!ability) continue;

    const level = levels[id] || 1;
    const effect = ability.effect;

    // Apply effects (multiply by level for stackable)
    if (effect.damagePercent) {
      computed.damageMultiplier += (effect.damagePercent / 100) * level;
    }
    if (effect.flatDamage) {
      computed.flatDamage += effect.flatDamage * level;
    }
    if (effect.lowHpBonusDamage) {
      computed.lowHpBonusDamage += effect.lowHpBonusDamage;
    }
    if (effect.highHpBonusDamage) {
      computed.highHpBonusDamage += effect.highHpBonusDamage;
    }
    if (effect.poisonDamage) {
      computed.poisonDamage += effect.poisonDamage * level;
    }
    if (effect.doubleHitChance) {
      computed.doubleHitChance += effect.doubleHitChance;
      computed.hasDoubleHit = true;
    }
    if (effect.attackSpeedPercent) {
      computed.attackSpeedBonus += (effect.attackSpeedPercent / 100) * level;
    }
    if (effect.moveSpeedPercent) {
      computed.speedMultiplier += (effect.moveSpeedPercent / 100) * level;
    }
    if (effect.maxHpBonus) {
      computed.maxHpBonus += effect.maxHpBonus * level;
    }
    if (effect.damageReduction) {
      // Stack diminishingly
      computed.damageReduction = 1 - (1 - computed.damageReduction / 100) * (1 - effect.damageReduction / 100);
      computed.damageReduction *= 100;
    }
    if (effect.hpPerSecond) {
      computed.hpPerSecond += effect.hpPerSecond * level;
    }
    if (effect.lifestealPercent) {
      computed.lifestealPercent += effect.lifestealPercent;
    }
    if (effect.lowHpDefenseBonus) {
      computed.lowHpDefenseBonus += effect.lowHpDefenseBonus;
    }
    if (effect.reviveOnce) {
      computed.hasRevive = true;
    }
    if (effect.critChance) {
      computed.critChance += effect.critChance * level;
    }
    if (effect.executeThreshold) {
      computed.executeThreshold = Math.max(computed.executeThreshold, effect.executeThreshold);
      computed.hasExecution = true;
    }
    if (effect.fullArc) {
      computed.hasFullArc = true;
    }
    if (effect.chainOnKill) {
      computed.hasChainKill = true;
    }
    if (effect.killStreakDamage) {
      computed.killStreakDamage += effect.killStreakDamage;
    }
    if (effect.damageMultiplier) {
      computed.damageMultiplier *= effect.damageMultiplier;
      computed.hasRiskReward = true;
    }
    if (effect.hpMultiplier) {
      computed.isHollowCarapace = true;  // Track glass cannon
    }
    // Skill-gated ability flags
    if (effect.grazeStackBonus) {
      computed.hasGrazeFrenzy = true;
    }
    if (effect.thermalMomentum) {
      computed.hasThermalMomentum = true;
    }
    if (effect.executionChain) {
      computed.hasExecutionChain = true;
    }
    if (effect.glassCannonMastery) {
      computed.hasGlassCannonMastery = true;
      computed.hasRiskReward = true;  // Also a risk/reward ability
    }
    if (effect.venomArchitect) {
      computed.hasVenomArchitect = true;
    }
  }

  // Apply damage cap
  computed.damageMultiplier = Math.min(computed.damageMultiplier, MAX_DAMAGE_MULTIPLIER);

  // Cap crit chance at 100%
  computed.critChance = Math.min(computed.critChance, 100);

  return computed;
}

/**
 * Get random ability choices for level up
 */
export function getAbilityChoices(
  abilities: ActiveAbilities,
  count: number = 3
): AbilityId[] {
  const available: AbilityId[] = [];

  for (const ability of ALL_ABILITIES) {
    const currentLevel = abilities.levels[ability.id] || 0;

    // Can offer if: not owned, or stackable and below max
    if (!abilities.owned.includes(ability.id)) {
      available.push(ability.id);
    } else if (ability.stackable && ability.maxStacks && currentLevel < ability.maxStacks) {
      available.push(ability.id);
    }
  }

  // Shuffle and take count
  const shuffled = available.sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
}

/**
 * Check if player can take ability
 */
export function canTakeAbility(
  abilities: ActiveAbilities,
  abilityId: AbilityId
): boolean {
  const ability = getAbility(abilityId);
  if (!ability) return false;

  if (!abilities.owned.includes(abilityId)) return true;

  if (ability.stackable && ability.maxStacks) {
    const level = abilities.levels[abilityId] || 0;
    return level < ability.maxStacks;
  }

  return false;
}

// =============================================================================
// Legacy Compatibility - Empty conflict system (simplified)
// =============================================================================

export const HARD_CONFLICTS: [AbilityId, AbilityId][] = [];

export function hasConflict(_id1: AbilityId, _id2: AbilityId): boolean {
  return false;  // No conflicts in simplified system
}

export function getConflicts(_id: AbilityId): AbilityId[] {
  return [];
}

export function wouldConflict(
  _abilities: ActiveAbilities,
  _newAbility: AbilityId
): AbilityId | null {
  return null;
}

// =============================================================================
// Legacy Compatibility - Exports
// =============================================================================

// Alias for backward compatibility
export const generateAbilityChoices = getAbilityChoices;

// Export types that other systems may use
export type ComboPotential = 'low' | 'medium' | 'high';
export type RiskLevel = 'none' | 'moderate' | 'high';

// Stub types for legacy compatibility
export interface AbilityMechanic {
  [key: string]: unknown;
}
export interface AbilityCurse {
  [key: string]: unknown;
}
export interface CurseEffect {
  [key: string]: unknown;
}

// Export pool for direct access
export const ABILITY_POOL = ALL_ABILITIES;

// Stub functions for legacy compatibility
export function getRiskRewardAbilities(): Ability[] {
  return ALL_ABILITIES.filter(a => a.isRiskReward);
}

export function getKeystoneAbilities(): Ability[] {
  return [];  // No keystones in simplified system
}

export function hasAbility(abilities: ActiveAbilities, id: AbilityId): boolean {
  return abilities.owned.includes(id);
}

export function getAbilityLevel(abilities: ActiveAbilities, id: AbilityId): number {
  return abilities.levels[id] || 0;
}
