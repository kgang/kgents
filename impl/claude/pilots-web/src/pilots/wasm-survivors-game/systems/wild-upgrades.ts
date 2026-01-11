/**
 * WASM Survivors - WILD UPGRADES SYSTEM
 *
 * "Each upgrade should be SERIOUSLY WILD, not simple stat improvements."
 * "Each upgrade has custom side effects, mechanics, juice."
 * "All upgrades have interesting dynamics with ALL other upgrades."
 *
 * THE EIGHT WILD UPGRADES:
 * 1. ECHO - Ghost hornet repeats all actions 0.5s later
 * 2. GRAVITY_WELL - Enemies orbit you, collide and explode
 * 3. METAMORPHOSIS - Transform into different creatures every 30s
 * 4. BLOOD_PRICE - Spend HP to supercharge; low HP = god mode
 * 5. TEMPORAL_DEBT - Freeze time 3s, then 2x speed for 6s
 * 6. SWARM_MIND - Split into 5 mini-hornets
 * 7. HONEY_TRAP - Sticky zones that chain enemies together
 * 8. ROYAL_DECREE - Mark enemy as "The King" that others attack
 *
 * NO STAT UPGRADES. Every upgrade fundamentally changes gameplay.
 */

import type { Vector2 } from '../types';

// =============================================================================
// Types
// =============================================================================

export type WildUpgradeType =
  | 'echo'
  | 'gravity_well'
  | 'metamorphosis'
  | 'blood_price'
  | 'temporal_debt'
  | 'swarm_mind'
  | 'honey_trap'
  | 'royal_decree';

/**
 * Metamorphosis forms - each is a completely different creature
 */
export type MetamorphForm = 'hornet' | 'spider' | 'mantis' | 'butterfly';

/**
 * Core state for each wild upgrade
 */
export interface WildUpgradeState {
  // ECHO state
  echo: {
    active: boolean;
    ghostPosition: Vector2;
    ghostVelocity: Vector2;
    actionQueue: EchoAction[];
    ghostAlpha: number;
  };

  // GRAVITY WELL state
  gravityWell: {
    active: boolean;
    orbitingEnemies: Map<string, OrbitState>;
    wellStrength: number;
    collisionCooldowns: Map<string, number>;
  };

  // METAMORPHOSIS state
  metamorphosis: {
    active: boolean;
    currentForm: MetamorphForm;
    formTimer: number;
    formDuration: number;
    transitionProgress: number;
    isTransitioning: boolean;
  };

  // BLOOD PRICE state
  bloodPrice: {
    active: boolean;
    bloodDebt: number;
    chargeLevel: number;
    isCharging: boolean;
    bloodGeysers: BloodGeyser[];
    lowHpThreshold: number;
    godModeActive: boolean;
  };

  // TEMPORAL DEBT state
  temporalDebt: {
    active: boolean;
    isFrozen: boolean;
    frozenTimeRemaining: number;
    debtTimeRemaining: number;
    frozenActions: TemporalAction[];
    timeScale: number;
    cooldown: number;
  };

  // SWARM MIND state
  swarmMind: {
    active: boolean;
    hornets: SwarmHornet[];
    deadCount: number;
    powerMultiplier: number;
    formationPattern: 'spread' | 'follow' | 'surround';
  };

  // HONEY TRAP state
  honeyTrap: {
    active: boolean;
    traps: HoneyTrapZone[];
    chains: EnemyChain[];
    maxTraps: number;
    trapCooldown: number;
    lastTrapTime: number;
  };

  // ROYAL DECREE state
  royalDecree: {
    active: boolean;
    currentKingId: string | null;
    kingHealth: number;
    kingMaxHealth: number;
    crownPassCount: number;
    loyalSubjects: Set<string>;
    kingDeathRewards: KingReward[];
  };
}

// =============================================================================
// Sub-types for each upgrade
// =============================================================================

export interface EchoAction {
  type: 'move' | 'attack' | 'dash' | 'ability';
  position: Vector2;
  direction: Vector2;
  timestamp: number;
  data?: unknown;
}

export interface OrbitState {
  enemyId: string;
  angle: number;
  distance: number;
  angularVelocity: number;
  orbitStartTime: number;
}

export interface BloodGeyser {
  id: string;
  position: Vector2;
  radius: number;
  damage: number;
  lifetime: number;
  maxLifetime: number;
}

export interface TemporalAction {
  type: 'attack' | 'move' | 'damage';
  data: unknown;
  scheduledTime: number;
}

export interface SwarmHornet {
  id: string;
  position: Vector2;
  velocity: Vector2;
  health: number;
  maxHealth: number;
  attackCooldown: number;
  isAlive: boolean;
}

export interface HoneyTrapZone {
  id: string;
  position: Vector2;
  radius: number;
  strength: number;
  trappedEnemies: Set<string>;
  lifetime: number;
  maxLifetime: number;
}

export interface EnemyChain {
  id: string;
  enemyIds: string[];
  chainStrength: number;
  breakDamage: number;
}

export interface KingReward {
  type: 'xp' | 'health' | 'upgrade' | 'power_surge';
  amount: number;
}

// =============================================================================
// Upgrade Definitions
// =============================================================================

export interface WildUpgrade {
  id: WildUpgradeType;
  name: string;
  tagline: string;
  description: string;
  icon: string;
  color: string;
  colorSecondary: string;

  // Visual identity
  particleSystem: string;
  screenEffect: string;
  soundTheme: string;

  // Synergy descriptions with every other upgrade
  synergies: Record<WildUpgradeType, SynergyEffect>;
}

export interface SynergyEffect {
  name: string;
  description: string;
  mechanicChange: string;
  juiceEffect: string;
}

// =============================================================================
// THE WILD EIGHT - Definitions
// =============================================================================

export const WILD_UPGRADES: Record<WildUpgradeType, WildUpgrade> = {
  echo: {
    id: 'echo',
    name: 'ECHO',
    tagline: 'Your shadow fights too',
    description: 'A ghost hornet follows you, repeating every action 0.5 seconds later. Two hornets. Double the carnage.',
    icon: '👻',
    color: '#88CCFF',
    colorSecondary: '#4488CC',
    particleSystem: 'ghost_trail',
    screenEffect: 'echo_ripple',
    soundTheme: 'ethereal_double',
    synergies: {
      echo: { name: 'Self', description: '-', mechanicChange: '-', juiceEffect: '-' },
      gravity_well: {
        name: 'ORBITAL ECHO',
        description: 'Ghost creates its own gravity well',
        mechanicChange: 'Two gravity wells, enemies can orbit between them',
        juiceEffect: 'Dual orbit trails, planetary collision sounds',
      },
      metamorphosis: {
        name: 'FORM MEMORY',
        description: 'Ghost stays in previous form',
        mechanicChange: 'Attack with TWO different forms simultaneously',
        juiceEffect: 'Dual-color particle trails, form harmony chime',
      },
      blood_price: {
        name: 'BLOOD ECHO',
        description: 'Ghost attacks cost HP, but deal 3x damage',
        mechanicChange: 'Ghost becomes blood-red, massively empowered',
        juiceEffect: 'Crimson ghost trail, blood splash on hits',
      },
      temporal_debt: {
        name: 'TIME LOOP',
        description: 'In frozen time, ghost catches up to you',
        mechanicChange: 'Ghost actions compressed into freeze window',
        juiceEffect: 'Time distortion waves, convergence flash',
      },
      swarm_mind: {
        name: 'ECHO SWARM',
        description: 'Each swarm member has its own echo',
        mechanicChange: '5 hornets become 10 attackers',
        juiceEffect: 'Cascading ghost trails, harmonic buzz',
      },
      honey_trap: {
        name: 'STICKY MEMORIES',
        description: 'Ghost leaves honey wherever it goes',
        mechanicChange: 'Constant honey trail behind ghost',
        juiceEffect: 'Golden ghost trail, dripping sounds',
      },
      royal_decree: {
        name: 'PHANTOM EXECUTION',
        description: 'Ghost deals 5x damage to The King',
        mechanicChange: 'Ghost fixates on King, relentless pursuit',
        juiceEffect: 'Royal purple ghost aura, execution fanfare',
      },
    },
  },

  gravity_well: {
    id: 'gravity_well',
    name: 'GRAVITY WELL',
    tagline: 'Become the center of destruction',
    description: 'Enemies orbit around you like doomed planets. When they collide, they explode. You are the sun.',
    icon: '🌀',
    color: '#9944FF',
    colorSecondary: '#6622CC',
    particleSystem: 'orbit_rings',
    screenEffect: 'gravity_distortion',
    soundTheme: 'cosmic_hum',
    synergies: {
      echo: {
        name: 'ORBITAL ECHO',
        description: 'Ghost creates its own gravity well',
        mechanicChange: 'Two gravity wells, enemies orbit between them',
        juiceEffect: 'Dual orbit trails, planetary collision sounds',
      },
      gravity_well: { name: 'Self', description: '-', mechanicChange: '-', juiceEffect: '-' },
      metamorphosis: {
        name: 'FORM GRAVITY',
        description: 'Each form has different gravity effect',
        mechanicChange: 'Spider=pull, Mantis=repel, Butterfly=orbit faster',
        juiceEffect: 'Form-colored gravity field, shifting orbit sounds',
      },
      blood_price: {
        name: 'BLOOD ORBIT',
        description: 'Low HP increases gravity strength 5x',
        mechanicChange: 'Enemies spiral in FAST, constant collisions',
        juiceEffect: 'Red gravity field, desperate cosmic sounds',
      },
      temporal_debt: {
        name: 'FROZEN ORBIT',
        description: 'Enemies continue orbiting in frozen time',
        mechanicChange: 'Set up massive collision chains while frozen',
        juiceEffect: 'Blue-shifted orbits, time-stretched sounds',
      },
      swarm_mind: {
        name: 'CONSTELLATION',
        description: 'Each swarm member is a gravity point',
        mechanicChange: '5 mini gravity wells, chaotic orbits',
        juiceEffect: 'Star-like glow on each hornet, cosmic web visuals',
      },
      honey_trap: {
        name: 'HONEY SINGULARITY',
        description: 'Gravity pulls enemies INTO honey traps',
        mechanicChange: 'Honey traps become gravity anchors',
        juiceEffect: 'Black hole honey effect, stretching visuals',
      },
      royal_decree: {
        name: 'ROYAL GRAVITY',
        description: 'The King becomes the gravity center',
        mechanicChange: 'Enemies orbit The King, damaging it constantly',
        juiceEffect: 'Crown-shaped orbit trails, regal destruction sounds',
      },
    },
  },

  metamorphosis: {
    id: 'metamorphosis',
    name: 'METAMORPHOSIS',
    tagline: 'Become something else entirely',
    description: 'Every 30 seconds, transform: SPIDER (web traps), MANTIS (melee slashes), BUTTERFLY (pollen clouds). Adapt or die.',
    icon: '🦋',
    color: '#FF44FF',
    colorSecondary: '#AA22AA',
    particleSystem: 'transformation_burst',
    screenEffect: 'form_shift',
    soundTheme: 'evolution_chord',
    synergies: {
      echo: {
        name: 'FORM MEMORY',
        description: 'Ghost stays in previous form',
        mechanicChange: 'Attack with TWO different forms simultaneously',
        juiceEffect: 'Dual-color particle trails, form harmony chime',
      },
      gravity_well: {
        name: 'FORM GRAVITY',
        description: 'Each form has different gravity effect',
        mechanicChange: 'Spider=pull, Mantis=repel, Butterfly=orbit faster',
        juiceEffect: 'Form-colored gravity field, shifting orbit sounds',
      },
      metamorphosis: { name: 'Self', description: '-', mechanicChange: '-', juiceEffect: '-' },
      blood_price: {
        name: 'BLOOD FORMS',
        description: 'Low HP unlocks SECRET 4th form: WASP',
        mechanicChange: 'Wasp form: pure aggression, massive damage, glass cannon',
        juiceEffect: 'Red-black transformation, rage sounds',
      },
      temporal_debt: {
        name: 'INSTANT EVOLUTION',
        description: 'Form changes happen in frozen time',
        mechanicChange: 'Can cycle through ALL forms during freeze',
        juiceEffect: 'Rapid-fire transformations, time-compressed sounds',
      },
      swarm_mind: {
        name: 'DIVERSE SWARM',
        description: 'Each swarm member is a different form',
        mechanicChange: 'Spider+Mantis+Butterfly+Hornets all at once',
        juiceEffect: 'Rainbow swarm visuals, multi-species sounds',
      },
      honey_trap: {
        name: 'FORM TRAPS',
        description: 'Each form leaves different trap type',
        mechanicChange: 'Spider=web, Mantis=blade, Butterfly=pollen',
        juiceEffect: 'Form-specific trap visuals, varied trap sounds',
      },
      royal_decree: {
        name: 'ROYAL METAMORPHOSIS',
        description: 'Killing The King gives permanent form bonuses',
        mechanicChange: 'Each King death enhances one form permanently',
        juiceEffect: 'Crown absorbed into form, power-up fanfare',
      },
    },
  },

  blood_price: {
    id: 'blood_price',
    name: 'BLOOD PRICE',
    tagline: 'Power costs. Pay in blood.',
    description: 'Spend HP to supercharge any attack. Below 25% HP, enter GOD MODE: 10x damage, attacks create blood geysers.',
    icon: '🩸',
    color: '#CC0000',
    colorSecondary: '#880000',
    particleSystem: 'blood_particles',
    screenEffect: 'blood_vignette',
    soundTheme: 'heartbeat_power',
    synergies: {
      echo: {
        name: 'BLOOD ECHO',
        description: 'Ghost attacks cost HP but deal 3x damage',
        mechanicChange: 'Ghost becomes blood-red, massively empowered',
        juiceEffect: 'Crimson ghost trail, blood splash on hits',
      },
      gravity_well: {
        name: 'BLOOD ORBIT',
        description: 'Low HP increases gravity strength 5x',
        mechanicChange: 'Enemies spiral in FAST, constant collisions',
        juiceEffect: 'Red gravity field, desperate cosmic sounds',
      },
      metamorphosis: {
        name: 'BLOOD FORMS',
        description: 'Low HP unlocks SECRET 4th form: WASP',
        mechanicChange: 'Wasp form: pure aggression, massive damage, glass cannon',
        juiceEffect: 'Red-black transformation, rage sounds',
      },
      blood_price: { name: 'Self', description: '-', mechanicChange: '-', juiceEffect: '-' },
      temporal_debt: {
        name: 'BLOOD TIME',
        description: 'Frozen time costs HP instead of cooldown',
        mechanicChange: 'Unlimited time freezes if you can afford them',
        juiceEffect: 'Blood-red time freeze, heartbeat slowdown',
      },
      swarm_mind: {
        name: 'BLOOD SACRIFICE',
        description: 'Can sacrifice swarm members for massive damage',
        mechanicChange: 'Each sacrifice = screen-wide blood explosion',
        juiceEffect: 'Dramatic sacrifice animation, explosion sound',
      },
      honey_trap: {
        name: 'BLOOD HONEY',
        description: 'Traps drain HP from trapped enemies to you',
        mechanicChange: 'Honey traps become life-steal zones',
        juiceEffect: 'Red honey draining visuals, feeding sounds',
      },
      royal_decree: {
        name: 'BLOOD THRONE',
        description: 'The King bleeds for you - King takes your damage',
        mechanicChange: 'Redirect damage to King, stay in god mode longer',
        juiceEffect: 'Blood tether to King, shared pain visuals',
      },
    },
  },

  temporal_debt: {
    id: 'temporal_debt',
    name: 'TEMPORAL DEBT',
    tagline: 'Borrow from the future. Pay it back.',
    description: 'FREEZE time for 3 seconds. Then time runs at 2x for 6 seconds. What you do frozen echoes forward.',
    icon: '⏱️',
    color: '#00DDFF',
    colorSecondary: '#0088AA',
    particleSystem: 'time_fragments',
    screenEffect: 'time_freeze',
    soundTheme: 'clock_distortion',
    synergies: {
      echo: {
        name: 'TIME LOOP',
        description: 'In frozen time, ghost catches up to you',
        mechanicChange: 'Ghost actions compressed into freeze window',
        juiceEffect: 'Time distortion waves, convergence flash',
      },
      gravity_well: {
        name: 'FROZEN ORBIT',
        description: 'Enemies continue orbiting in frozen time',
        mechanicChange: 'Set up massive collision chains while frozen',
        juiceEffect: 'Blue-shifted orbits, time-stretched sounds',
      },
      metamorphosis: {
        name: 'INSTANT EVOLUTION',
        description: 'Form changes happen in frozen time',
        mechanicChange: 'Can cycle through ALL forms during freeze',
        juiceEffect: 'Rapid-fire transformations, time-compressed sounds',
      },
      blood_price: {
        name: 'BLOOD TIME',
        description: 'Frozen time costs HP instead of cooldown',
        mechanicChange: 'Unlimited time freezes if you can afford them',
        juiceEffect: 'Blood-red time freeze, heartbeat slowdown',
      },
      temporal_debt: { name: 'Self', description: '-', mechanicChange: '-', juiceEffect: '-' },
      swarm_mind: {
        name: 'SWARM FREEZE',
        description: 'Swarm members act independently in frozen time',
        mechanicChange: '5 hornets worth of damage in 3 frozen seconds',
        juiceEffect: 'Multiple action trails, overlapping sounds',
      },
      honey_trap: {
        name: 'AMBER PRISON',
        description: 'Honey traps become permanent during freeze',
        mechanicChange: 'Frozen honey = instant trap for 2x duration',
        juiceEffect: 'Amber crystallization visuals, shattering sounds',
      },
      royal_decree: {
        name: 'ROYAL REWIND',
        description: "King's death rewinds time 3 seconds",
        mechanicChange: 'Kill King repeatedly for infinite value',
        juiceEffect: 'Time reversal wave, repeat death sounds',
      },
    },
  },

  swarm_mind: {
    id: 'swarm_mind',
    name: 'SWARM MIND',
    tagline: 'Divide and conquer',
    description: 'Split into 5 mini-hornets that attack independently. When one dies, the others grow STRONGER.',
    icon: '🐝',
    color: '#FFAA00',
    colorSecondary: '#CC8800',
    particleSystem: 'swarm_trails',
    screenEffect: 'swarm_vision',
    soundTheme: 'buzzing_chorus',
    synergies: {
      echo: {
        name: 'ECHO SWARM',
        description: 'Each swarm member has its own echo',
        mechanicChange: '5 hornets become 10 attackers',
        juiceEffect: 'Cascading ghost trails, harmonic buzz',
      },
      gravity_well: {
        name: 'CONSTELLATION',
        description: 'Each swarm member is a gravity point',
        mechanicChange: '5 mini gravity wells, chaotic orbits',
        juiceEffect: 'Star-like glow on each hornet, cosmic web visuals',
      },
      metamorphosis: {
        name: 'DIVERSE SWARM',
        description: 'Each swarm member is a different form',
        mechanicChange: 'Spider+Mantis+Butterfly+Hornets all at once',
        juiceEffect: 'Rainbow swarm visuals, multi-species sounds',
      },
      blood_price: {
        name: 'BLOOD SACRIFICE',
        description: 'Can sacrifice swarm members for massive damage',
        mechanicChange: 'Each sacrifice = screen-wide blood explosion',
        juiceEffect: 'Dramatic sacrifice animation, explosion sound',
      },
      temporal_debt: {
        name: 'SWARM FREEZE',
        description: 'Swarm members act independently in frozen time',
        mechanicChange: '5 hornets worth of damage in 3 frozen seconds',
        juiceEffect: 'Multiple action trails, overlapping sounds',
      },
      swarm_mind: { name: 'Self', description: '-', mechanicChange: '-', juiceEffect: '-' },
      honey_trap: {
        name: 'HIVE NETWORK',
        description: 'Each swarm member can create honey traps',
        mechanicChange: '5x trap generation rate',
        juiceEffect: 'Distributed honey drops, busy bee sounds',
      },
      royal_decree: {
        name: 'DEMOCRACY',
        description: 'Swarm can designate MULTIPLE Kings',
        mechanicChange: 'Up to 3 Kings at once, chaos ensues',
        juiceEffect: 'Multiple crown visuals, royal battle sounds',
      },
    },
  },

  honey_trap: {
    id: 'honey_trap',
    name: 'HONEY TRAP',
    tagline: 'Stick together. Die together.',
    description: 'Create sticky honey zones. Trapped enemies get CHAINED together. Break the chain = MASSIVE explosion.',
    icon: '🍯',
    color: '#FFCC00',
    colorSecondary: '#CC9900',
    particleSystem: 'honey_drips',
    screenEffect: 'honey_shimmer',
    soundTheme: 'sticky_splat',
    synergies: {
      echo: {
        name: 'STICKY MEMORIES',
        description: 'Ghost leaves honey wherever it goes',
        mechanicChange: 'Constant honey trail behind ghost',
        juiceEffect: 'Golden ghost trail, dripping sounds',
      },
      gravity_well: {
        name: 'HONEY SINGULARITY',
        description: 'Gravity pulls enemies INTO honey traps',
        mechanicChange: 'Honey traps become gravity anchors',
        juiceEffect: 'Black hole honey effect, stretching visuals',
      },
      metamorphosis: {
        name: 'FORM TRAPS',
        description: 'Each form leaves different trap type',
        mechanicChange: 'Spider=web, Mantis=blade, Butterfly=pollen',
        juiceEffect: 'Form-specific trap visuals, varied trap sounds',
      },
      blood_price: {
        name: 'BLOOD HONEY',
        description: 'Traps drain HP from trapped enemies to you',
        mechanicChange: 'Honey traps become life-steal zones',
        juiceEffect: 'Red honey draining visuals, feeding sounds',
      },
      temporal_debt: {
        name: 'AMBER PRISON',
        description: 'Honey traps become permanent during freeze',
        mechanicChange: 'Frozen honey = instant trap for 2x duration',
        juiceEffect: 'Amber crystallization visuals, shattering sounds',
      },
      swarm_mind: {
        name: 'HIVE NETWORK',
        description: 'Each swarm member can create honey traps',
        mechanicChange: '5x trap generation rate',
        juiceEffect: 'Distributed honey drops, busy bee sounds',
      },
      honey_trap: { name: 'Self', description: '-', mechanicChange: '-', juiceEffect: '-' },
      royal_decree: {
        name: 'ROYAL JELLY',
        description: 'The King is permanently stuck in honey',
        mechanicChange: 'King cant move, becomes damage sponge',
        juiceEffect: 'Golden royal prison, regal stuck sounds',
      },
    },
  },

  royal_decree: {
    id: 'royal_decree',
    name: 'ROYAL DECREE',
    tagline: 'Heavy is the head that wears the crown',
    description: 'Designate an enemy as THE KING. All other enemies attack it! When King dies: crown passes + MEGA rewards.',
    icon: '👑',
    color: '#FFD700',
    colorSecondary: '#DAA520',
    particleSystem: 'crown_sparkles',
    screenEffect: 'royal_flash',
    soundTheme: 'fanfare_doom',
    synergies: {
      echo: {
        name: 'PHANTOM EXECUTION',
        description: 'Ghost deals 5x damage to The King',
        mechanicChange: 'Ghost fixates on King, relentless pursuit',
        juiceEffect: 'Royal purple ghost aura, execution fanfare',
      },
      gravity_well: {
        name: 'ROYAL GRAVITY',
        description: 'The King becomes the gravity center',
        mechanicChange: 'Enemies orbit The King, damaging it constantly',
        juiceEffect: 'Crown-shaped orbit trails, regal destruction sounds',
      },
      metamorphosis: {
        name: 'ROYAL METAMORPHOSIS',
        description: 'Killing The King gives permanent form bonuses',
        mechanicChange: 'Each King death enhances one form permanently',
        juiceEffect: 'Crown absorbed into form, power-up fanfare',
      },
      blood_price: {
        name: 'BLOOD THRONE',
        description: 'The King bleeds for you - King takes your damage',
        mechanicChange: 'Redirect damage to King, stay in god mode longer',
        juiceEffect: 'Blood tether to King, shared pain visuals',
      },
      temporal_debt: {
        name: 'ROYAL REWIND',
        description: "King's death rewinds time 3 seconds",
        mechanicChange: 'Kill King repeatedly for infinite value',
        juiceEffect: 'Time reversal wave, repeat death sounds',
      },
      swarm_mind: {
        name: 'DEMOCRACY',
        description: 'Swarm can designate MULTIPLE Kings',
        mechanicChange: 'Up to 3 Kings at once, chaos ensues',
        juiceEffect: 'Multiple crown visuals, royal battle sounds',
      },
      honey_trap: {
        name: 'ROYAL JELLY',
        description: 'The King is permanently stuck in honey',
        mechanicChange: 'King cant move, becomes damage sponge',
        juiceEffect: 'Golden royal prison, regal stuck sounds',
      },
      royal_decree: { name: 'Self', description: '-', mechanicChange: '-', juiceEffect: '-' },
    },
  },
};

// =============================================================================
// Initial State Factory
// =============================================================================

export function createInitialWildUpgradeState(): WildUpgradeState {
  return {
    echo: {
      active: false,
      ghostPosition: { x: 0, y: 0 },
      ghostVelocity: { x: 0, y: 0 },
      actionQueue: [],
      ghostAlpha: 0.6,
    },
    gravityWell: {
      active: false,
      orbitingEnemies: new Map(),
      wellStrength: 150,
      collisionCooldowns: new Map(),
    },
    metamorphosis: {
      active: false,
      currentForm: 'hornet',
      formTimer: 0,
      formDuration: 30000, // 30 seconds
      transitionProgress: 0,
      isTransitioning: false,
    },
    bloodPrice: {
      active: false,
      bloodDebt: 0,
      chargeLevel: 0,
      isCharging: false,
      bloodGeysers: [],
      lowHpThreshold: 25,
      godModeActive: false,
    },
    temporalDebt: {
      active: false,
      isFrozen: false,
      frozenTimeRemaining: 0,
      debtTimeRemaining: 0,
      frozenActions: [],
      timeScale: 1,
      cooldown: 0,
    },
    swarmMind: {
      active: false,
      hornets: [],
      deadCount: 0,
      powerMultiplier: 1,
      formationPattern: 'spread',
    },
    honeyTrap: {
      active: false,
      traps: [],
      chains: [],
      maxTraps: 5,
      trapCooldown: 3000,
      lastTrapTime: 0,
    },
    royalDecree: {
      active: false,
      currentKingId: null,
      kingHealth: 0,
      kingMaxHealth: 0,
      crownPassCount: 0,
      loyalSubjects: new Set(),
      kingDeathRewards: [],
    },
  };
}

// =============================================================================
// Upgrade Pool for Selection
// =============================================================================

export function getWildUpgradePool(): WildUpgrade[] {
  return Object.values(WILD_UPGRADES);
}

export function getWildUpgrade(id: WildUpgradeType): WildUpgrade | undefined {
  return WILD_UPGRADES[id];
}

/**
 * Get synergy effect between two upgrades
 */
export function getWildSynergy(
  upgrade1: WildUpgradeType,
  upgrade2: WildUpgradeType
): SynergyEffect | null {
  if (upgrade1 === upgrade2) return null;
  const upgrade = WILD_UPGRADES[upgrade1];
  return upgrade?.synergies[upgrade2] ?? null;
}

/**
 * Get all active synergies for owned upgrades
 */
export function getActiveWildSynergies(
  ownedUpgrades: WildUpgradeType[]
): Array<{ upgrade1: WildUpgradeType; upgrade2: WildUpgradeType; synergy: SynergyEffect }> {
  const synergies: Array<{ upgrade1: WildUpgradeType; upgrade2: WildUpgradeType; synergy: SynergyEffect }> = [];

  for (let i = 0; i < ownedUpgrades.length; i++) {
    for (let j = i + 1; j < ownedUpgrades.length; j++) {
      const synergy = getWildSynergy(ownedUpgrades[i], ownedUpgrades[j]);
      if (synergy) {
        synergies.push({
          upgrade1: ownedUpgrades[i],
          upgrade2: ownedUpgrades[j],
          synergy,
        });
      }
    }
  }

  return synergies;
}

// =============================================================================
// GRAVITY WELL: Update Mechanics
// "Enemies orbit around you like doomed planets. Collisions = explosions."
// =============================================================================

/**
 * Configuration for GRAVITY WELL
 */
export const GRAVITY_WELL_CONFIG = {
  // Gravity range - enemies within this start orbiting
  gravityRange: 200,

  // Minimum distance - enemies won't get closer than this
  minOrbitDistance: 40,

  // Maximum orbit distance
  maxOrbitDistance: 180,

  // Base angular velocity (radians per second) - at max distance
  baseAngularVelocity: 1.5,

  // Velocity increase as enemies get closer (multiplier per pixel closer)
  velocityDistanceScale: 0.02,

  // Maximum angular velocity (radians per second)
  maxAngularVelocity: 6.0,

  // Rate at which enemies spiral inward (pixels per second)
  spiralRate: 5,

  // Collision detection radius between orbiting enemies
  collisionRadius: 25,

  // Explosion damage (base)
  explosionDamage: 50,

  // Explosion radius
  explosionRadius: 80,

  // Cooldown between collisions for same enemy pair (ms)
  collisionCooldown: 500,

  // Time before enemy can start orbiting again after being released
  releaseTime: 2000,
} as const;

/**
 * Result of a gravity well collision
 */
export interface GravityCollision {
  enemy1Id: string;
  enemy2Id: string;
  position: Vector2;
  damage: number;
  radius: number;
}

/**
 * Result of gravity well update
 */
export interface GravityWellUpdateResult {
  /** Updated gravity well state */
  gravityWell: WildUpgradeState['gravityWell'];
  /** Enemies that need their positions overridden */
  enemyOverrides: Map<string, { position: Vector2; velocity: Vector2 }>;
  /** Collisions that occurred this frame */
  collisions: GravityCollision[];
  /** Enemies that were damaged by explosions */
  explosionDamage: Map<string, number>;
  /** Enemies released from orbit (too far away) */
  releasedEnemies: string[];
}

/**
 * Update GRAVITY WELL mechanics
 *
 * Enemies within range start orbiting the player like planets around a sun.
 * The closer they get, the faster they orbit. When orbiting enemies collide,
 * they explode dealing damage to nearby enemies.
 */
export function updateGravityWell(
  state: WildUpgradeState['gravityWell'],
  playerPosition: Vector2,
  enemies: Array<{ id: string; position: Vector2; health: number; radius: number }>,
  gameTime: number,
  deltaTime: number
): GravityWellUpdateResult {
  if (!state.active) {
    return {
      gravityWell: state,
      enemyOverrides: new Map(),
      collisions: [],
      explosionDamage: new Map(),
      releasedEnemies: [],
    };
  }

  const config = GRAVITY_WELL_CONFIG;
  const dt = deltaTime / 1000; // Convert to seconds

  const newOrbitingEnemies = new Map(state.orbitingEnemies);
  const newCollisionCooldowns = new Map(state.collisionCooldowns);
  const enemyOverrides = new Map<string, { position: Vector2; velocity: Vector2 }>();
  const collisions: GravityCollision[] = [];
  const explosionDamage = new Map<string, number>();
  const releasedEnemies: string[] = [];

  // Clean up expired collision cooldowns
  for (const [pairKey, cooldownTime] of newCollisionCooldowns) {
    if (gameTime > cooldownTime) {
      newCollisionCooldowns.delete(pairKey);
    }
  }

  // Process each enemy
  for (const enemy of enemies) {
    if (enemy.health <= 0) {
      // Remove dead enemies from orbit
      newOrbitingEnemies.delete(enemy.id);
      continue;
    }

    const dx = enemy.position.x - playerPosition.x;
    const dy = enemy.position.y - playerPosition.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // Check if enemy should start orbiting
    if (!newOrbitingEnemies.has(enemy.id)) {
      if (distance <= config.gravityRange && distance > config.minOrbitDistance) {
        // Capture into orbit!
        const angle = Math.atan2(dy, dx);
        newOrbitingEnemies.set(enemy.id, {
          enemyId: enemy.id,
          angle,
          distance: Math.min(distance, config.maxOrbitDistance),
          angularVelocity: config.baseAngularVelocity,
          orbitStartTime: gameTime,
        });
      }
      continue;
    }

    // Enemy is orbiting - update their orbit
    const orbit = newOrbitingEnemies.get(enemy.id)!;

    // Check if enemy escaped (somehow got too far)
    if (distance > config.gravityRange * 1.5) {
      newOrbitingEnemies.delete(enemy.id);
      releasedEnemies.push(enemy.id);
      continue;
    }

    // Calculate angular velocity based on distance (closer = faster)
    const distanceFactor = 1 + (config.maxOrbitDistance - orbit.distance) * config.velocityDistanceScale;
    const angularVelocity = Math.min(
      config.baseAngularVelocity * distanceFactor,
      config.maxAngularVelocity
    );

    // Update angle
    const newAngle = orbit.angle + angularVelocity * dt;

    // Spiral inward slowly
    const newDistance = Math.max(
      config.minOrbitDistance,
      orbit.distance - config.spiralRate * dt
    );

    // Calculate new position
    const newX = playerPosition.x + Math.cos(newAngle) * newDistance;
    const newY = playerPosition.y + Math.sin(newAngle) * newDistance;

    // Calculate velocity for visual trails (tangential)
    const speed = angularVelocity * newDistance;
    const velocityX = -Math.sin(newAngle) * speed;
    const velocityY = Math.cos(newAngle) * speed;

    // Update orbit state
    newOrbitingEnemies.set(enemy.id, {
      ...orbit,
      angle: newAngle,
      distance: newDistance,
      angularVelocity,
    });

    // Override enemy position
    enemyOverrides.set(enemy.id, {
      position: { x: newX, y: newY },
      velocity: { x: velocityX, y: velocityY },
    });
  }

  // Check for collisions between orbiting enemies
  const orbitingEnemyIds = Array.from(newOrbitingEnemies.keys());
  for (let i = 0; i < orbitingEnemyIds.length; i++) {
    for (let j = i + 1; j < orbitingEnemyIds.length; j++) {
      const id1 = orbitingEnemyIds[i];
      const id2 = orbitingEnemyIds[j];
      const pairKey = id1 < id2 ? `${id1}:${id2}` : `${id2}:${id1}`;

      // Check cooldown
      if (newCollisionCooldowns.has(pairKey)) {
        continue;
      }

      const orbit1 = newOrbitingEnemies.get(id1)!;
      const orbit2 = newOrbitingEnemies.get(id2)!;

      // Get positions
      const pos1 = enemyOverrides.get(id1)?.position ?? {
        x: playerPosition.x + Math.cos(orbit1.angle) * orbit1.distance,
        y: playerPosition.y + Math.sin(orbit1.angle) * orbit1.distance,
      };
      const pos2 = enemyOverrides.get(id2)?.position ?? {
        x: playerPosition.x + Math.cos(orbit2.angle) * orbit2.distance,
        y: playerPosition.y + Math.sin(orbit2.angle) * orbit2.distance,
      };

      // Check distance
      const collisionDx = pos1.x - pos2.x;
      const collisionDy = pos1.y - pos2.y;
      const collisionDist = Math.sqrt(collisionDx * collisionDx + collisionDy * collisionDy);

      if (collisionDist < config.collisionRadius * 2) {
        // COLLISION! Calculate explosion position (midpoint)
        const explosionPos = {
          x: (pos1.x + pos2.x) / 2,
          y: (pos1.y + pos2.y) / 2,
        };

        // Create collision event
        collisions.push({
          enemy1Id: id1,
          enemy2Id: id2,
          position: explosionPos,
          damage: config.explosionDamage,
          radius: config.explosionRadius,
        });

        // Add cooldown
        newCollisionCooldowns.set(pairKey, gameTime + config.collisionCooldown);

        // Remove both enemies from orbit (they exploded!)
        newOrbitingEnemies.delete(id1);
        newOrbitingEnemies.delete(id2);

        // Calculate splash damage to nearby enemies
        for (const enemy of enemies) {
          if (enemy.id === id1 || enemy.id === id2) continue;

          const enemyPos = enemyOverrides.get(enemy.id)?.position ?? enemy.position;
          const splashDx = enemyPos.x - explosionPos.x;
          const splashDy = enemyPos.y - explosionPos.y;
          const splashDist = Math.sqrt(splashDx * splashDx + splashDy * splashDy);

          if (splashDist < config.explosionRadius) {
            // Damage falls off with distance
            const falloff = 1 - (splashDist / config.explosionRadius);
            const damage = Math.floor(config.explosionDamage * falloff);

            const existingDamage = explosionDamage.get(enemy.id) ?? 0;
            explosionDamage.set(enemy.id, existingDamage + damage);
          }
        }
      }
    }
  }

  return {
    gravityWell: {
      ...state,
      orbitingEnemies: newOrbitingEnemies,
      collisionCooldowns: newCollisionCooldowns,
    },
    enemyOverrides,
    collisions,
    explosionDamage,
    releasedEnemies,
  };
}

/**
 * Check if an enemy is currently orbiting
 */
export function isEnemyOrbiting(
  state: WildUpgradeState['gravityWell'],
  enemyId: string
): boolean {
  return state.orbitingEnemies.has(enemyId);
}

/**
 * Get orbit info for an enemy (for rendering)
 */
export function getOrbitInfo(
  state: WildUpgradeState['gravityWell'],
  enemyId: string
): OrbitState | null {
  return state.orbitingEnemies.get(enemyId) ?? null;
}

/**
 * Calculate visual intensity for gravity well effects based on orbiting count
 */
export function getGravityWellIntensity(
  state: WildUpgradeState['gravityWell']
): number {
  const count = state.orbitingEnemies.size;
  if (count === 0) return 0;
  // Intensity scales with orbiting enemies, caps at 1.0 with 5+ enemies
  return Math.min(1.0, count / 5);
}

// =============================================================================
// BLOOD PRICE - Update Logic
// "Power costs. Pay in blood."
// =============================================================================

/**
 * BLOOD PRICE Configuration Constants
 * Tuned for risk/reward to feel EXTREME but fair
 *
 * The fantasy: "Low HP makes you POWERFUL, not desperate"
 */
export const BLOOD_PRICE_CONFIG = {
  // Charging mechanics
  chargeKey: 'Shift',              // Hold Shift to charge
  hpDrainPerSecond: 30,            // HP lost per second while charging
  maxChargeTime: 2000,             // Max 2 seconds of charging
  chargeToMultiplier: 10,          // Max damage multiplier from charging
  minChargeForBonus: 0.3,          // Need 30% charge for any bonus

  // God Mode thresholds
  godModeThreshold: 0.25,          // Below 25% HP = GOD MODE
  godModeDamageMultiplier: 10,     // 10x damage in god mode

  // Blood Geyser mechanics (spawned on kills during god mode)
  geyser: {
    radius: 50,                    // AoE radius
    damagePerSecond: 25,           // Damage per second to enemies
    lifetime: 3000,                // 3 seconds duration
    maxGeysers: 5,                 // Max simultaneous geysers
  },
} as const;

/**
 * Result of blood price update - returned to game loop for integration
 */
export interface BloodPriceUpdateResult {
  // State changes
  hpDrained: number;               // HP that was drained this frame
  damageMultiplier: number;        // Current damage multiplier
  godModeJustActivated: boolean;   // Did we just enter god mode?
  godModeActive: boolean;          // Are we in god mode?

  // Blood geyser info
  newGeysers: BloodGeyser[];       // New geysers to spawn
  geyserDamageEvents: Array<{      // Enemies damaged by geysers
    enemyId: string;
    damage: number;
    geyserPosition: Vector2;
  }>;
  expiredGeyserIds: string[];      // Geysers that just expired

  // Visual/audio cues
  shouldPlayHeartbeat: boolean;    // Low HP heartbeat sound
  chargeLevel: number;             // 0-1 for visual intensity
  isCharging: boolean;             // Currently charging?
}

/**
 * Update BLOOD PRICE state
 *
 * "Spend HP to supercharge any attack. Below 25% HP, enter GOD MODE."
 *
 * @param state - Current blood price state
 * @param deltaTime - Frame delta in milliseconds
 * @param playerHealth - Current player health
 * @param playerMaxHealth - Max player health
 * @param isChargeKeyHeld - Is the charge key (Shift) being held?
 * @param enemies - Current enemies for geyser damage calculations
 * @returns Update result with state changes and events
 */
export function updateBloodPrice(
  state: WildUpgradeState['bloodPrice'],
  deltaTime: number,
  playerHealth: number,
  playerMaxHealth: number,
  isChargeKeyHeld: boolean,
  enemies: Array<{ id: string; position: Vector2 }>
): BloodPriceUpdateResult {
  const result: BloodPriceUpdateResult = {
    hpDrained: 0,
    damageMultiplier: 1,
    godModeJustActivated: false,
    godModeActive: false,
    newGeysers: [],
    geyserDamageEvents: [],
    expiredGeyserIds: [],
    shouldPlayHeartbeat: false,
    chargeLevel: 0,
    isCharging: false,
  };

  if (!state.active) return result;

  const config = BLOOD_PRICE_CONFIG;
  const healthFraction = playerHealth / playerMaxHealth;

  // ==========================================================================
  // GOD MODE CHECK
  // "Below 25% HP, enter GOD MODE: 10x damage, attacks create blood geysers."
  // Low HP feels POWERFUL, not desperate!
  // ==========================================================================
  const wasInGodMode = state.godModeActive;
  state.godModeActive = healthFraction <= config.godModeThreshold && healthFraction > 0;
  result.godModeActive = state.godModeActive;
  result.godModeJustActivated = state.godModeActive && !wasInGodMode;

  // Low HP heartbeat cue - plays when under threshold
  // Start heartbeat slightly before god mode for anticipation
  result.shouldPlayHeartbeat = healthFraction <= config.godModeThreshold * 1.5;

  // ==========================================================================
  // CHARGING MECHANICS
  // "HOLD Shift to spend HP to charge attacks"
  // ==========================================================================
  if (isChargeKeyHeld && playerHealth > 1) {
    state.isCharging = true;
    result.isCharging = true;

    // Drain HP while charging
    const hpToDrain = (config.hpDrainPerSecond * deltaTime) / 1000;
    result.hpDrained = Math.min(hpToDrain, playerHealth - 1); // Never drain to 0 from charging

    // Accumulate charge level
    state.chargeLevel = Math.min(1, state.chargeLevel + deltaTime / config.maxChargeTime);
    state.bloodDebt += result.hpDrained;
  } else {
    // Release charge - it persists for one attack then resets
    state.isCharging = false;
    result.isCharging = false;
  }

  result.chargeLevel = state.chargeLevel;

  // ==========================================================================
  // DAMAGE MULTIPLIER CALCULATION
  // ==========================================================================
  if (state.godModeActive) {
    // GOD MODE: Always 10x damage - you earned it!
    result.damageMultiplier = config.godModeDamageMultiplier;
  } else if (state.chargeLevel >= config.minChargeForBonus) {
    // Charged: Scale from 1x to maxMultiplier based on charge
    const chargeBonus = state.chargeLevel * (config.chargeToMultiplier - 1);
    result.damageMultiplier = 1 + chargeBonus;
  }

  // ==========================================================================
  // BLOOD GEYSER UPDATE
  // "Attacks create blood geysers at kill locations"
  // ==========================================================================
  const updatedGeysers: BloodGeyser[] = [];

  for (const geyser of state.bloodGeysers) {
    // Update lifetime
    geyser.lifetime -= deltaTime;

    if (geyser.lifetime <= 0) {
      // Geyser expired
      result.expiredGeyserIds.push(geyser.id);
    } else {
      // Geyser still active - check for enemy damage
      for (const enemy of enemies) {
        const dx = enemy.position.x - geyser.position.x;
        const dy = enemy.position.y - geyser.position.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance <= geyser.radius) {
          // Enemy in geyser - deal damage
          const damageThisFrame = (config.geyser.damagePerSecond * deltaTime) / 1000;
          result.geyserDamageEvents.push({
            enemyId: enemy.id,
            damage: damageThisFrame,
            geyserPosition: geyser.position,
          });
        }
      }

      updatedGeysers.push(geyser);
    }
  }

  state.bloodGeysers = updatedGeysers;

  return result;
}

/**
 * Spawn a blood geyser at kill location
 * Called by game loop when enemy is killed during god mode
 */
export function spawnBloodGeyser(
  state: WildUpgradeState['bloodPrice'],
  position: Vector2
): BloodGeyser | null {
  if (!state.active || !state.godModeActive) return null;

  const config = BLOOD_PRICE_CONFIG;

  // Check geyser limit
  if (state.bloodGeysers.length >= config.geyser.maxGeysers) {
    // Remove oldest geyser to make room
    state.bloodGeysers.shift();
  }

  const geyser: BloodGeyser = {
    id: `geyser-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    radius: config.geyser.radius,
    damage: config.geyser.damagePerSecond,
    lifetime: config.geyser.lifetime,
    maxLifetime: config.geyser.lifetime,
  };

  state.bloodGeysers.push(geyser);
  return geyser;
}

/**
 * Consume charge after an attack
 * Resets charge level but keeps god mode active
 */
export function consumeBloodCharge(state: WildUpgradeState['bloodPrice']): void {
  state.chargeLevel = 0;
  state.bloodDebt = 0;
  state.isCharging = false;
}

/**
 * Activate BLOOD PRICE upgrade
 */
export function activateBloodPrice(state: WildUpgradeState['bloodPrice']): void {
  state.active = true;
  state.lowHpThreshold = BLOOD_PRICE_CONFIG.godModeThreshold * 100;
}

/**
 * Get the effective damage multiplier for display/UI
 */
export function getBloodPriceDamageMultiplier(
  state: WildUpgradeState['bloodPrice'],
  playerHealth: number,
  playerMaxHealth: number
): number {
  if (!state.active) return 1;

  const config = BLOOD_PRICE_CONFIG;
  const healthFraction = playerHealth / playerMaxHealth;

  // God mode check
  if (healthFraction <= config.godModeThreshold && healthFraction > 0) {
    return config.godModeDamageMultiplier;
  }

  // Charge bonus
  if (state.chargeLevel >= config.minChargeForBonus) {
    return 1 + state.chargeLevel * (config.chargeToMultiplier - 1);
  }

  return 1;
}

// =============================================================================
// SWARM MIND MECHANICS
// "Divide and conquer. The hive is one mind, many bodies."
// =============================================================================

/**
 * Configuration for SWARM MIND upgrade
 */
export const SWARM_MIND_CONFIG = {
  // Hornet count and health
  INITIAL_HORNET_COUNT: 5,
  HORNET_HEALTH: 30,
  HORNET_RADIUS: 8,

  // Movement behavior
  FOLLOW_DISTANCE: 40,           // Base distance hornets try to maintain from player
  FOLLOW_SPEED: 0.08,            // Lerp speed toward target position (0-1)
  ORBIT_SPEED: 0.002,            // Angular velocity for orbit pattern (rad/ms)
  POSITION_JITTER: 15,           // Random offset range for natural movement

  // Combat behavior
  ATTACK_RANGE: 60,              // Range at which hornets auto-attack enemies
  ATTACK_COOLDOWN: 400,          // ms between attacks per hornet
  BASE_DAMAGE: 15,               // Base damage per hornet attack

  // Death empowerment - "When one falls, the others rise"
  DAMAGE_BONUS_PER_DEATH: 0.25,  // +25% damage per dead hornet
  SIZE_BONUS_PER_DEATH: 0.1,     // +10% size per dead hornet
  FINAL_HORNET_DAMAGE_MULT: 5,   // 5x damage when only 1 hornet remains
  FINAL_HORNET_SIZE_MULT: 2,     // 2x size when only 1 hornet remains

  // Formation patterns
  SPREAD_RADIUS: 50,             // Radius for spread formation
  SURROUND_RADIUS: 35,           // Radius for surround formation
} as const;

/**
 * Initialize SWARM MIND state when upgrade is acquired
 */
export function initializeSwarmMind(
  playerPosition: Vector2
): WildUpgradeState['swarmMind'] {
  const hornets: SwarmHornet[] = [];

  for (let i = 0; i < SWARM_MIND_CONFIG.INITIAL_HORNET_COUNT; i++) {
    // Distribute hornets in a pentagon around player
    const angle = (i / SWARM_MIND_CONFIG.INITIAL_HORNET_COUNT) * Math.PI * 2;
    const offsetX = Math.cos(angle) * SWARM_MIND_CONFIG.SPREAD_RADIUS;
    const offsetY = Math.sin(angle) * SWARM_MIND_CONFIG.SPREAD_RADIUS;

    hornets.push({
      id: `swarm-hornet-${i}`,
      position: {
        x: playerPosition.x + offsetX,
        y: playerPosition.y + offsetY,
      },
      velocity: { x: 0, y: 0 },
      health: SWARM_MIND_CONFIG.HORNET_HEALTH,
      maxHealth: SWARM_MIND_CONFIG.HORNET_HEALTH,
      attackCooldown: i * 80, // Stagger initial attacks for visual variety
      isAlive: true,
    });
  }

  return {
    active: true,
    hornets,
    deadCount: 0,
    powerMultiplier: 1,
    formationPattern: 'spread',
  };
}

/**
 * Result of swarm mind update
 */
export interface SwarmMindUpdateResult {
  state: WildUpgradeState['swarmMind'];
  attacks: SwarmAttack[];
  deaths: SwarmDeath[];
}

export interface SwarmAttack {
  hornetId: string;
  enemyId: string;
  damage: number;
  position: Vector2;      // Enemy position (for particles)
  hornetPosition: Vector2; // Hornet position (for attack line)
}

export interface SwarmDeath {
  hornetId: string;
  position: Vector2;
  remainingHornets: number;
}

/**
 * Update SWARM MIND state each frame
 *
 * Handles:
 * - Hornet movement (following player with offset)
 * - Auto-attack nearest enemies
 * - Death tracking and power scaling
 */
export function updateSwarmMind(
  state: WildUpgradeState['swarmMind'],
  playerPosition: Vector2,
  playerVelocity: Vector2,
  enemies: Array<{ id: string; position: Vector2; health: number; radius: number }>,
  deltaTime: number,
  gameTime: number
): SwarmMindUpdateResult {
  if (!state.active) {
    return {
      state,
      attacks: [],
      deaths: [],
    };
  }

  const attacks: SwarmAttack[] = [];

  // Calculate alive hornets for formation
  const aliveHornets = state.hornets.filter(h => h.isAlive);
  const aliveCount = aliveHornets.length;

  if (aliveCount === 0) {
    // All hornets dead - swarm mind is deactivated
    return {
      state: { ...state, active: false },
      attacks: [],
      deaths: [],
    };
  }

  // Calculate power multiplier based on dead hornets
  // When one dies, others get +25% damage each
  // At 1 hornet remaining: 5x damage
  let powerMultiplier = 1;
  const deadCount = SWARM_MIND_CONFIG.INITIAL_HORNET_COUNT - aliveCount;

  if (aliveCount === 1) {
    powerMultiplier = SWARM_MIND_CONFIG.FINAL_HORNET_DAMAGE_MULT;
  } else {
    powerMultiplier = 1 + (deadCount * SWARM_MIND_CONFIG.DAMAGE_BONUS_PER_DEATH);
  }

  // Update each hornet
  const updatedHornets = state.hornets.map((hornet, _index) => {
    if (!hornet.isAlive) return hornet;

    // Calculate target position based on formation
    const aliveIndex = aliveHornets.findIndex(h => h.id === hornet.id);
    const targetPos = calculateSwarmPosition(
      playerPosition,
      playerVelocity,
      aliveIndex,
      aliveCount,
      state.formationPattern,
      gameTime
    );

    // Smooth movement toward target position (with some lag for organic feel)
    const followSpeed = SWARM_MIND_CONFIG.FOLLOW_SPEED;
    const newPosition = {
      x: hornet.position.x + (targetPos.x - hornet.position.x) * followSpeed * (deltaTime / 16),
      y: hornet.position.y + (targetPos.y - hornet.position.y) * followSpeed * (deltaTime / 16),
    };

    // Calculate velocity for visual purposes
    const newVelocity = {
      x: (newPosition.x - hornet.position.x) / (deltaTime / 1000 || 1),
      y: (newPosition.y - hornet.position.y) / (deltaTime / 1000 || 1),
    };

    // Update attack cooldown
    let newCooldown = Math.max(0, hornet.attackCooldown - deltaTime);

    // Auto-attack nearest enemy in range
    if (newCooldown <= 0 && enemies.length > 0) {
      const nearestEnemy = findNearestSwarmEnemy(newPosition, enemies, SWARM_MIND_CONFIG.ATTACK_RANGE);

      if (nearestEnemy) {
        // Attack!
        const damage = SWARM_MIND_CONFIG.BASE_DAMAGE * powerMultiplier;
        attacks.push({
          hornetId: hornet.id,
          enemyId: nearestEnemy.id,
          damage,
          position: nearestEnemy.position,
          hornetPosition: newPosition,
        });
        newCooldown = SWARM_MIND_CONFIG.ATTACK_COOLDOWN;
      }
    }

    return {
      ...hornet,
      position: newPosition,
      velocity: newVelocity,
      attackCooldown: newCooldown,
    };
  });

  return {
    state: {
      ...state,
      hornets: updatedHornets,
      deadCount,
      powerMultiplier,
    },
    attacks,
    deaths: [],
  };
}

/**
 * Calculate target position for a swarm hornet based on formation pattern
 */
function calculateSwarmPosition(
  playerPosition: Vector2,
  playerVelocity: Vector2,
  hornetIndex: number,
  totalHornets: number,
  pattern: 'spread' | 'follow' | 'surround',
  gameTime: number
): Vector2 {
  // Base angle distributes hornets evenly
  const baseAngle = (hornetIndex / totalHornets) * Math.PI * 2;

  // Add time-based orbital motion for natural feel
  const orbitOffset = gameTime * SWARM_MIND_CONFIG.ORBIT_SPEED;

  // Add player-velocity-based offset (hornets trail behind when moving)
  const velocityMagnitude = Math.sqrt(playerVelocity.x ** 2 + playerVelocity.y ** 2);
  const velocityAngle = Math.atan2(-playerVelocity.y, -playerVelocity.x);

  let radius: number;
  let angle: number;

  switch (pattern) {
    case 'spread':
      // Hornets spread in a wider arc behind the player
      radius = SWARM_MIND_CONFIG.SPREAD_RADIUS;
      angle = baseAngle + orbitOffset;
      // Bias toward behind player when moving
      if (velocityMagnitude > 10) {
        const bias = Math.sin(baseAngle - velocityAngle);
        angle += bias * 0.3;
      }
      break;

    case 'follow':
      // Hornets form a tight V-formation behind player
      radius = SWARM_MIND_CONFIG.FOLLOW_DISTANCE + hornetIndex * 10;
      angle = velocityAngle + (hornetIndex - totalHornets / 2) * 0.2;
      break;

    case 'surround':
      // Hornets surround player in tight orbit
      radius = SWARM_MIND_CONFIG.SURROUND_RADIUS;
      angle = baseAngle + orbitOffset * 2; // Faster orbit when surrounding
      break;

    default:
      radius = SWARM_MIND_CONFIG.SPREAD_RADIUS;
      angle = baseAngle + orbitOffset;
  }

  // Add subtle jitter for organic movement
  const jitter = {
    x: (Math.sin(gameTime * 0.01 + hornetIndex * 100) * SWARM_MIND_CONFIG.POSITION_JITTER) * 0.3,
    y: (Math.cos(gameTime * 0.012 + hornetIndex * 100) * SWARM_MIND_CONFIG.POSITION_JITTER) * 0.3,
  };

  return {
    x: playerPosition.x + Math.cos(angle) * radius + jitter.x,
    y: playerPosition.y + Math.sin(angle) * radius + jitter.y,
  };
}

/**
 * Find the nearest enemy within attack range for swarm hornets
 */
function findNearestSwarmEnemy(
  hornetPosition: Vector2,
  enemies: Array<{ id: string; position: Vector2; health: number; radius: number }>,
  range: number
): { id: string; position: Vector2 } | null {
  let nearest: { id: string; position: Vector2 } | null = null;
  let nearestDist = range;

  for (const enemy of enemies) {
    if (enemy.health <= 0) continue;

    const dx = enemy.position.x - hornetPosition.x;
    const dy = enemy.position.y - hornetPosition.y;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist < nearestDist) {
      nearestDist = dist;
      nearest = { id: enemy.id, position: enemy.position };
    }
  }

  return nearest;
}

/**
 * Apply damage to a swarm hornet (from enemy collision or attack)
 * Returns updated state and any death events
 */
export function damageSwarmHornet(
  state: WildUpgradeState['swarmMind'],
  hornetId: string,
  damage: number
): { state: WildUpgradeState['swarmMind']; death: SwarmDeath | null } {
  const hornetIndex = state.hornets.findIndex(h => h.id === hornetId);
  if (hornetIndex === -1) return { state, death: null };

  const hornet = state.hornets[hornetIndex];
  if (!hornet.isAlive) return { state, death: null };

  const newHealth = hornet.health - damage;
  const isDead = newHealth <= 0;

  const updatedHornets = [...state.hornets];
  updatedHornets[hornetIndex] = {
    ...hornet,
    health: Math.max(0, newHealth),
    isAlive: !isDead,
  };

  const death: SwarmDeath | null = isDead
    ? {
        hornetId,
        position: hornet.position,
        remainingHornets: state.hornets.filter(h => h.isAlive && h.id !== hornetId).length,
      }
    : null;

  return {
    state: {
      ...state,
      hornets: updatedHornets,
      deadCount: isDead ? state.deadCount + 1 : state.deadCount,
    },
    death,
  };
}

/**
 * Get the scale multiplier for swarm hornets based on deaths
 * At 1 hornet remaining: 2x size
 */
export function getSwarmHornetScale(state: WildUpgradeState['swarmMind']): number {
  const aliveCount = state.hornets.filter(h => h.isAlive).length;

  if (aliveCount === 1) {
    return SWARM_MIND_CONFIG.FINAL_HORNET_SIZE_MULT;
  }

  const deadCount = SWARM_MIND_CONFIG.INITIAL_HORNET_COUNT - aliveCount;
  return 1 + (deadCount * SWARM_MIND_CONFIG.SIZE_BONUS_PER_DEATH);
}

/**
 * Check if swarm mind is active and has living hornets
 */
export function isSwarmActive(state: WildUpgradeState['swarmMind']): boolean {
  return state.active && state.hornets.some(h => h.isAlive);
}

/**
 * Get living hornets for rendering
 */
export function getAliveSwarmHornets(state: WildUpgradeState['swarmMind']): SwarmHornet[] {
  return state.hornets.filter(h => h.isAlive);
}

// =============================================================================
// METAMORPHOSIS: Form Configurations
// "Every 30 seconds, transform into a different creature."
// =============================================================================

/**
 * Each form is a COMPLETELY different creature with unique abilities.
 * "Adapt or die." - The upgrade that makes you master four playstyles.
 */
export const METAMORPH_FORMS: Record<MetamorphForm, MetamorphFormConfig> = {
  hornet: {
    name: 'HORNET',
    color: '#FF8C00',        // Strike Orange - the original
    colorSecondary: '#CC5500',
    glowColor: 'rgba(255, 140, 0, 0.4)',
    description: 'Default form. Balanced melee strikes.',
    attackType: 'melee',
    attackCooldown: 800,     // ms
    attackDamage: 15,
    attackRange: 40,
    moveSpeedMultiplier: 1.0,
    passiveEffect: 'none',
    bodyShape: 'oval',       // Pointed oval for hornet
    wingStyle: 'blur',       // Fast wing blur
  },
  spider: {
    name: 'SPIDER',
    color: '#8B4513',        // Saddle Brown - earthy, predatory
    colorSecondary: '#5D2E0C',
    glowColor: 'rgba(139, 69, 19, 0.4)',
    description: 'Place web traps that immobilize enemies.',
    attackType: 'web_trap',
    attackCooldown: 2000,    // 2s between web placements
    attackDamage: 5,         // Webs do minor damage
    attackRange: 60,         // Web trap radius
    moveSpeedMultiplier: 0.85, // Slightly slower
    passiveEffect: 'web_sense',
    bodyShape: 'bulb',       // Round body with legs
    wingStyle: 'none',       // Spiders don't fly
  },
  mantis: {
    name: 'MANTIS',
    color: '#228B22',        // Forest Green - deadly precision
    colorSecondary: '#145A14',
    glowColor: 'rgba(34, 139, 34, 0.4)',
    description: 'Powerful melee slash attacks with short range.',
    attackType: 'melee_slash',
    attackCooldown: 1200,    // Slower but devastating
    attackDamage: 40,        // BIG damage
    attackRange: 50,         // Cone attack range
    moveSpeedMultiplier: 1.1, // Slightly faster
    passiveEffect: 'ambush',
    bodyShape: 'triangle',   // Angular, predatory
    wingStyle: 'folded',     // Wings folded back
  },
  butterfly: {
    name: 'BUTTERFLY',
    color: '#DA70D6',        // Orchid - beautiful but deadly
    colorSecondary: '#BA55D3',
    glowColor: 'rgba(218, 112, 214, 0.4)',
    description: 'Leaves pollen clouds that damage over time.',
    attackType: 'pollen_cloud',
    attackCooldown: 1500,    // Moderate cooldown
    attackDamage: 8,         // Damage per tick
    attackRange: 80,         // Cloud radius
    moveSpeedMultiplier: 1.2, // Fastest form - evasive
    passiveEffect: 'flutter',
    bodyShape: 'wings',      // Wing-shaped body
    wingStyle: 'large',      // Big beautiful wings
  },
};

export interface MetamorphFormConfig {
  name: string;
  color: string;
  colorSecondary: string;
  glowColor: string;
  description: string;
  attackType: 'melee' | 'web_trap' | 'melee_slash' | 'pollen_cloud';
  attackCooldown: number;
  attackDamage: number;
  attackRange: number;
  moveSpeedMultiplier: number;
  passiveEffect: string;
  bodyShape: 'oval' | 'bulb' | 'triangle' | 'wings';
  wingStyle: 'blur' | 'none' | 'folded' | 'large';
}

// =============================================================================
// METAMORPHOSIS: Ability Entities
// =============================================================================

/**
 * Web Trap - Spider form ability
 * Sticky web that immobilizes enemies who walk into it
 */
export interface WebTrap {
  id: string;
  position: Vector2;
  radius: number;
  duration: number;        // How long trap lasts
  maxDuration: number;
  immobilizeDuration: number; // How long enemies are stuck
  trappedEnemies: Set<string>;
  damage: number;          // Damage when trap triggers
  webStrands: number;      // Visual: number of strands (more = older trap)
}

/**
 * Melee Slash - Mantis form ability
 * Cone attack that hits all enemies in arc
 */
export interface MeleeSlash {
  id: string;
  position: Vector2;
  direction: Vector2;      // Direction of slash
  arcAngle: number;        // 90 degrees = quarter circle
  range: number;
  damage: number;
  lifetime: number;        // Visual duration
  maxLifetime: number;
  hitEnemies: Set<string>; // Track what we've hit
}

/**
 * Pollen Cloud - Butterfly form ability
 * DoT zone that damages enemies over time
 */
export interface PollenCloud {
  id: string;
  position: Vector2;
  radius: number;
  damagePerTick: number;
  tickInterval: number;    // ms between damage ticks
  lastTickTime: number;
  duration: number;
  maxDuration: number;
  affectedEnemies: Set<string>;
  particleIntensity: number; // Visual: more particles over time
}

// =============================================================================
// METAMORPHOSIS: Configuration
// =============================================================================

export const METAMORPHOSIS_CONFIG = {
  // Form cycle
  formDuration: 30000,       // 30 seconds per form
  transitionDuration: 500,   // 0.5s form shift animation
  formOrder: ['hornet', 'spider', 'mantis', 'butterfly'] as MetamorphForm[],

  // Web Trap (Spider)
  webTrap: {
    maxTraps: 5,             // Maximum concurrent traps
    trapDuration: 8000,      // 8 seconds
    immobilizeDuration: 2000, // 2 seconds stuck
    triggerDamage: 5,        // Damage on trap trigger
    slowAmount: 0.5,         // 50% slow while trapped
  },

  // Melee Slash (Mantis)
  meleeSlash: {
    arcAngle: Math.PI / 2,   // 90 degree arc
    slashDuration: 200,      // 0.2s slash animation
    damageMultiplier: 2.5,   // 2.5x base damage
  },

  // Pollen Cloud (Butterfly)
  pollenCloud: {
    maxClouds: 3,            // Maximum concurrent clouds
    cloudDuration: 5000,     // 5 seconds
    tickInterval: 500,       // Damage every 0.5s
    cloudGrowthTime: 1000,   // Time to reach full size
  },
};

// =============================================================================
// METAMORPHOSIS: Update Function
// =============================================================================

const METAMORPH_FORM_ORDER = METAMORPHOSIS_CONFIG.formOrder;
const METAMORPH_TRANSITION_DURATION = METAMORPHOSIS_CONFIG.transitionDuration;

export interface MetamorphosisUpdateResult {
  state: WildUpgradeState['metamorphosis'];
  formChanged: boolean;
  newForm: MetamorphForm | null;
  webTraps: WebTrap[];
  meleeSlashes: MeleeSlash[];
  pollenClouds: PollenCloud[];
  damageEvents: Array<{ enemyId: string; damage: number; type: 'web' | 'slash' | 'pollen' }>;
  immobilizedEnemies: Set<string>;
  attackTriggered: boolean;
}

/**
 * Update METAMORPHOSIS state - handles form cycling and abilities
 *
 * @param state - Current metamorphosis state
 * @param deltaMs - Time since last frame in ms
 * @param playerPosition - Current player position
 * @param playerDirection - Direction player is facing
 * @param attackInput - Whether attack button is pressed
 * @param enemies - Current enemies for ability targeting
 * @param webTraps - Existing web traps
 * @param meleeSlashes - Existing melee slashes
 * @param pollenClouds - Existing pollen clouds
 * @param gameTime - Current game time in ms
 * @param lastAttackTime - Time of last attack
 */
export function updateMetamorphosisState(
  state: WildUpgradeState['metamorphosis'],
  deltaMs: number,
  playerPosition: Vector2,
  playerDirection: Vector2,
  attackInput: boolean,
  enemies: Array<{ id: string; position: Vector2; health: number }>,
  webTraps: WebTrap[],
  meleeSlashes: MeleeSlash[],
  pollenClouds: PollenCloud[],
  gameTime: number,
  lastAttackTime: number
): MetamorphosisUpdateResult {
  if (!state.active) {
    return {
      state,
      formChanged: false,
      newForm: null,
      webTraps,
      meleeSlashes,
      pollenClouds,
      damageEvents: [],
      immobilizedEnemies: new Set(),
      attackTriggered: false,
    };
  }

  const damageEvents: MetamorphosisUpdateResult['damageEvents'] = [];
  const immobilizedEnemies = new Set<string>();
  let newWebTraps = [...webTraps];
  let newMeleeSlashes = [...meleeSlashes];
  let newPollenClouds = [...pollenClouds];
  let attackTriggered = false;

  // Update form timer
  let newFormTimer = state.formTimer + deltaMs;
  let newCurrentForm = state.currentForm;
  let newTransitionProgress = state.transitionProgress;
  let newIsTransitioning = state.isTransitioning;
  let formChanged = false;

  // Check for form transition
  if (newFormTimer >= state.formDuration) {
    // Start transition to next form
    newFormTimer = 0;
    newIsTransitioning = true;
    newTransitionProgress = 0;
    formChanged = true;

    // Cycle to next form
    const currentIndex = METAMORPH_FORM_ORDER.indexOf(state.currentForm);
    const nextIndex = (currentIndex + 1) % METAMORPH_FORM_ORDER.length;
    newCurrentForm = METAMORPH_FORM_ORDER[nextIndex];
  }

  // Handle transition animation
  if (newIsTransitioning) {
    newTransitionProgress += deltaMs / METAMORPH_TRANSITION_DURATION;
    if (newTransitionProgress >= 1) {
      newTransitionProgress = 0;
      newIsTransitioning = false;
    }
  }

  // Get current form config
  const formConfig = METAMORPH_FORMS[newCurrentForm];
  const canAttack = attackInput && (gameTime - lastAttackTime) >= formConfig.attackCooldown && !newIsTransitioning;

  // Handle form-specific attacks
  if (canAttack) {
    attackTriggered = true;

    switch (formConfig.attackType) {
      case 'web_trap': {
        // Spider: Place web trap at position (respect max traps)
        if (newWebTraps.length < METAMORPHOSIS_CONFIG.webTrap.maxTraps) {
          const newTrap: WebTrap = {
            id: `web-${Date.now()}-${Math.random().toString(36).slice(2, 5)}`,
            position: { ...playerPosition },
            radius: formConfig.attackRange,
            duration: METAMORPHOSIS_CONFIG.webTrap.trapDuration,
            maxDuration: METAMORPHOSIS_CONFIG.webTrap.trapDuration,
            immobilizeDuration: METAMORPHOSIS_CONFIG.webTrap.immobilizeDuration,
            trappedEnemies: new Set(),
            damage: METAMORPHOSIS_CONFIG.webTrap.triggerDamage,
            webStrands: 8,
          };
          newWebTraps.push(newTrap);
        }
        break;
      }

      case 'melee_slash': {
        // Mantis: Create slash cone
        const normalizedDir = normalizeMetamorphVector(playerDirection);
        const newSlash: MeleeSlash = {
          id: `slash-${Date.now()}-${Math.random().toString(36).slice(2, 5)}`,
          position: { ...playerPosition },
          direction: normalizedDir,
          arcAngle: METAMORPHOSIS_CONFIG.meleeSlash.arcAngle,
          range: formConfig.attackRange,
          damage: Math.floor(formConfig.attackDamage * METAMORPHOSIS_CONFIG.meleeSlash.damageMultiplier),
          lifetime: METAMORPHOSIS_CONFIG.meleeSlash.slashDuration,
          maxLifetime: METAMORPHOSIS_CONFIG.meleeSlash.slashDuration,
          hitEnemies: new Set(),
        };
        newMeleeSlashes.push(newSlash);
        break;
      }

      case 'pollen_cloud': {
        // Butterfly: Create pollen cloud (respect max clouds)
        if (newPollenClouds.length < METAMORPHOSIS_CONFIG.pollenCloud.maxClouds) {
          const newCloud: PollenCloud = {
            id: `pollen-${Date.now()}-${Math.random().toString(36).slice(2, 5)}`,
            position: { ...playerPosition },
            radius: formConfig.attackRange,
            damagePerTick: formConfig.attackDamage,
            tickInterval: METAMORPHOSIS_CONFIG.pollenCloud.tickInterval,
            lastTickTime: gameTime,
            duration: METAMORPHOSIS_CONFIG.pollenCloud.cloudDuration,
            maxDuration: METAMORPHOSIS_CONFIG.pollenCloud.cloudDuration,
            affectedEnemies: new Set(),
            particleIntensity: 0.2,
          };
          newPollenClouds.push(newCloud);
        }
        break;
      }
    }
  }

  // Update web traps
  newWebTraps = newWebTraps
    .map(trap => {
      trap.duration -= deltaMs;

      // Check for enemies in trap
      for (const enemy of enemies) {
        const dx = enemy.position.x - trap.position.x;
        const dy = enemy.position.y - trap.position.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < trap.radius) {
          if (!trap.trappedEnemies.has(enemy.id)) {
            // New enemy trapped!
            trap.trappedEnemies.add(enemy.id);
            damageEvents.push({ enemyId: enemy.id, damage: trap.damage, type: 'web' });
          }
          // Track immobilization
          immobilizedEnemies.add(enemy.id);
        }
      }

      // Visual: web strands increase as trap ages
      const agePercent = 1 - (trap.duration / trap.maxDuration);
      trap.webStrands = Math.floor(8 + agePercent * 8); // 8-16 strands

      return trap;
    })
    .filter(trap => trap.duration > 0);

  // Update melee slashes
  newMeleeSlashes = newMeleeSlashes
    .map(slash => {
      slash.lifetime -= deltaMs;

      // Check for enemies in slash arc
      for (const enemy of enemies) {
        if (slash.hitEnemies.has(enemy.id)) continue;

        const dx = enemy.position.x - slash.position.x;
        const dy = enemy.position.y - slash.position.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < slash.range) {
          // Check if enemy is within arc angle
          const enemyAngle = Math.atan2(dy, dx);
          const slashAngle = Math.atan2(slash.direction.y, slash.direction.x);
          let angleDiff = Math.abs(enemyAngle - slashAngle);
          if (angleDiff > Math.PI) angleDiff = 2 * Math.PI - angleDiff;

          if (angleDiff < slash.arcAngle / 2) {
            slash.hitEnemies.add(enemy.id);
            damageEvents.push({ enemyId: enemy.id, damage: slash.damage, type: 'slash' });
          }
        }
      }

      return slash;
    })
    .filter(slash => slash.lifetime > 0);

  // Update pollen clouds
  newPollenClouds = newPollenClouds
    .map(cloud => {
      cloud.duration -= deltaMs;

      // Grow particle intensity over time
      const ageMs = cloud.maxDuration - cloud.duration;
      if (ageMs < METAMORPHOSIS_CONFIG.pollenCloud.cloudGrowthTime) {
        cloud.particleIntensity = 0.2 + 0.8 * (ageMs / METAMORPHOSIS_CONFIG.pollenCloud.cloudGrowthTime);
      } else {
        cloud.particleIntensity = 1.0;
      }

      // Apply tick damage
      if (gameTime - cloud.lastTickTime >= cloud.tickInterval) {
        cloud.lastTickTime = gameTime;

        for (const enemy of enemies) {
          const dx = enemy.position.x - cloud.position.x;
          const dy = enemy.position.y - cloud.position.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < cloud.radius) {
            cloud.affectedEnemies.add(enemy.id);
            damageEvents.push({ enemyId: enemy.id, damage: cloud.damagePerTick, type: 'pollen' });
          }
        }
      }

      return cloud;
    })
    .filter(cloud => cloud.duration > 0);

  return {
    state: {
      ...state,
      currentForm: newCurrentForm,
      formTimer: newFormTimer,
      transitionProgress: newTransitionProgress,
      isTransitioning: newIsTransitioning,
    },
    formChanged,
    newForm: formChanged ? newCurrentForm : null,
    webTraps: newWebTraps,
    meleeSlashes: newMeleeSlashes,
    pollenClouds: newPollenClouds,
    damageEvents,
    immobilizedEnemies,
    attackTriggered,
  };
}

/**
 * Get the next form in the cycle
 */
export function getNextMetamorphForm(currentForm: MetamorphForm): MetamorphForm {
  const currentIndex = METAMORPH_FORM_ORDER.indexOf(currentForm);
  const nextIndex = (currentIndex + 1) % METAMORPH_FORM_ORDER.length;
  return METAMORPH_FORM_ORDER[nextIndex];
}

/**
 * Get form config by form type
 */
export function getMetamorphFormConfig(form: MetamorphForm): MetamorphFormConfig {
  return METAMORPH_FORMS[form];
}

/**
 * Check if an enemy is trapped in any web
 */
export function isEnemyWebbed(enemyId: string, webTraps: WebTrap[]): boolean {
  return webTraps.some(trap => trap.trappedEnemies.has(enemyId));
}

/**
 * Get time until next form change (for UI display)
 */
export function getTimeToNextForm(state: WildUpgradeState['metamorphosis']): number {
  return Math.max(0, state.formDuration - state.formTimer);
}

/**
 * Get progress toward next form (0-1)
 */
export function getFormProgress(state: WildUpgradeState['metamorphosis']): number {
  return state.formTimer / state.formDuration;
}

// Helper function for metamorphosis
function normalizeMetamorphVector(v: Vector2): Vector2 {
  const mag = Math.sqrt(v.x * v.x + v.y * v.y);
  if (mag === 0) return { x: 1, y: 0 };
  return { x: v.x / mag, y: v.y / mag };
}

// =============================================================================
// ROYAL DECREE: Update Mechanics
// "Designate an enemy as THE KING. All other enemies attack it!"
// =============================================================================

/**
 * Configuration for ROYAL DECREE
 */
export const ROYAL_DECREE_CONFIG = {
  // Range to target nearest enemy for crowning
  crownTargetRange: 300,

  // Health multiplier for The King (2x base health)
  kingHealthMultiplier: 2.0,

  // Range at which enemies will pathfind to The King
  subjectAggroRange: 500,

  // Range at which enemies attack The King
  attackRange: 30,

  // Damage enemies deal to The King per second
  subjectDamagePerSecond: 15,

  // Base rewards on King death
  baseXpReward: 50,
  baseHealthReward: 10,

  // Scaling per crown pass (1 = first king death, 2 = second, etc.)
  xpScalePerPass: 1.5,
  healthScalePerPass: 1.2,

  // Power surge duration on King death (ms)
  powerSurgeDuration: 3000,
  powerSurgeDamageMultiplier: 1.5,

  // Minimum time between crown designations (ms)
  crownCooldown: 500,
};

/**
 * Input for ROYAL DECREE system
 */
export interface RoyalDecreeInput {
  playerPosition: Vector2;
  crownKeyJustPressed: boolean;
  enemies: Array<{
    id: string;
    position: Vector2;
    health: number;
    maxHealth: number;
    type: string;
  }>;
  deltaTime: number;
  gameTime: number;
}

/**
 * Result of ROYAL DECREE update
 */
export interface RoyalDecreeResult {
  state: WildUpgradeState['royalDecree'];
  // Modified enemies (with new health, target position, etc.)
  modifiedEnemies: Map<string, {
    targetPosition?: Vector2;
    damageDealt?: number;
  }>;
  // Events that occurred
  events: RoyalDecreeEvent[];
  // Player rewards
  rewards: {
    xp: number;
    health: number;
    powerSurge: boolean;
    powerSurgeDuration: number;
  };
}

export type RoyalDecreeEvent =
  | { type: 'crown_designated'; kingId: string; position: Vector2 }
  | { type: 'crown_passed'; fromKingId: string; toKingId: string; passCount: number }
  | { type: 'king_damaged'; kingId: string; damage: number; healthRemaining: number }
  | { type: 'king_died'; kingId: string; rewards: KingReward[] };

/**
 * Find the nearest enemy to the player
 */
function findNearestEnemyForCrown(
  playerPos: Vector2,
  enemies: RoyalDecreeInput['enemies'],
  maxRange: number,
  excludeId?: string
): RoyalDecreeInput['enemies'][0] | null {
  let nearest: RoyalDecreeInput['enemies'][0] | null = null;
  let nearestDist = maxRange;

  for (const enemy of enemies) {
    if (excludeId && enemy.id === excludeId) continue;
    const dx = enemy.position.x - playerPos.x;
    const dy = enemy.position.y - playerPos.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist < nearestDist) {
      nearestDist = dist;
      nearest = enemy;
    }
  }

  return nearest;
}

/**
 * Find the strongest enemy (highest health)
 */
function findStrongestEnemyForCrown(
  enemies: RoyalDecreeInput['enemies'],
  excludeId?: string
): RoyalDecreeInput['enemies'][0] | null {
  let strongest: RoyalDecreeInput['enemies'][0] | null = null;
  let maxHealth = 0;

  for (const enemy of enemies) {
    if (excludeId && enemy.id === excludeId) continue;
    if (enemy.health > maxHealth) {
      maxHealth = enemy.health;
      strongest = enemy;
    }
  }

  return strongest;
}

// Track last crown designation time
let lastCrownTime = 0;

/**
 * Update ROYAL DECREE state
 * - Detects crown key (R) and targets nearest enemy
 * - Makes other enemies pathfind TO The King
 * - Enemies in range attack The King
 * - On King death: find strongest enemy, pass crown, generate rewards
 */
export function updateRoyalDecree(
  state: WildUpgradeState['royalDecree'],
  input: RoyalDecreeInput,
  config = ROYAL_DECREE_CONFIG
): RoyalDecreeResult {
  const events: RoyalDecreeEvent[] = [];
  const modifiedEnemies = new Map<string, { targetPosition?: Vector2; damageDealt?: number }>();
  let rewards = { xp: 0, health: 0, powerSurge: false, powerSurgeDuration: 0 };

  // Copy state for modification
  const newState = { ...state };

  // Handle crown designation (R key pressed)
  if (input.crownKeyJustPressed && input.gameTime - lastCrownTime > config.crownCooldown) {
    const target = findNearestEnemyForCrown(input.playerPosition, input.enemies, config.crownTargetRange);

    if (target) {
      // Designate new King
      newState.currentKingId = target.id;
      newState.kingMaxHealth = target.maxHealth * config.kingHealthMultiplier;
      newState.kingHealth = newState.kingMaxHealth;
      newState.loyalSubjects = new Set(input.enemies.filter(e => e.id !== target.id).map(e => e.id));

      lastCrownTime = input.gameTime;

      events.push({
        type: 'crown_designated',
        kingId: target.id,
        position: target.position,
      });
    }
  }

  // Auto-crown: If no King but enemies exist, automatically crown a random one
  // This handles the case when ROYAL_DECREE was activated with no enemies
  if (!newState.currentKingId && input.enemies.length > 0) {
    const randomIndex = Math.floor(Math.random() * input.enemies.length);
    const target = input.enemies[randomIndex];

    newState.currentKingId = target.id;
    newState.kingMaxHealth = target.maxHealth * config.kingHealthMultiplier;
    newState.kingHealth = newState.kingMaxHealth;
    newState.loyalSubjects = new Set(input.enemies.filter(e => e.id !== target.id).map(e => e.id));

    events.push({
      type: 'crown_designated',
      kingId: target.id,
      position: target.position,
    });
  }

  // If we have a King, process the court dynamics
  if (newState.currentKingId) {
    const king = input.enemies.find(e => e.id === newState.currentKingId);

    if (!king) {
      // King was killed externally - need to pass crown
      const newKing = findStrongestEnemyForCrown(input.enemies);

      if (newKing) {
        // Crown passes to strongest remaining enemy
        newState.crownPassCount += 1;
        const oldKingId = newState.currentKingId;
        newState.currentKingId = newKing.id;
        newState.kingMaxHealth = newKing.maxHealth * config.kingHealthMultiplier;
        newState.kingHealth = newState.kingMaxHealth;
        newState.loyalSubjects = new Set(input.enemies.filter(e => e.id !== newKing.id).map(e => e.id));

        // Generate scaled rewards
        const passScale = Math.pow(config.xpScalePerPass, newState.crownPassCount - 1);
        const healthScale = Math.pow(config.healthScalePerPass, newState.crownPassCount - 1);

        rewards = {
          xp: Math.floor(config.baseXpReward * passScale),
          health: Math.floor(config.baseHealthReward * healthScale),
          powerSurge: true,
          powerSurgeDuration: config.powerSurgeDuration,
        };

        newState.kingDeathRewards = [
          { type: 'xp', amount: rewards.xp },
          { type: 'health', amount: rewards.health },
          { type: 'power_surge', amount: config.powerSurgeDamageMultiplier },
        ];

        events.push({
          type: 'king_died',
          kingId: oldKingId,
          rewards: newState.kingDeathRewards,
        });

        events.push({
          type: 'crown_passed',
          fromKingId: oldKingId,
          toKingId: newKing.id,
          passCount: newState.crownPassCount,
        });
      } else {
        // No enemies left - clear the King
        newState.currentKingId = null;
        newState.kingHealth = 0;
        newState.kingMaxHealth = 0;
        newState.loyalSubjects.clear();
      }
    } else {
      // King is alive - make subjects attack it
      const deltaSeconds = input.deltaTime / 1000;
      let totalDamageToKing = 0;

      for (const enemy of input.enemies) {
        if (enemy.id === newState.currentKingId) continue;

        const dx = king.position.x - enemy.position.x;
        const dy = king.position.y - enemy.position.y;
        const distToKing = Math.sqrt(dx * dx + dy * dy);

        if (distToKing < config.subjectAggroRange) {
          // Enemy is in range to pathfind to King
          modifiedEnemies.set(enemy.id, {
            targetPosition: king.position,
          });

          // If close enough, deal damage
          if (distToKing < config.attackRange) {
            const damage = config.subjectDamagePerSecond * deltaSeconds;
            totalDamageToKing += damage;

            const existing = modifiedEnemies.get(enemy.id);
            modifiedEnemies.set(enemy.id, {
              ...existing,
              damageDealt: damage,
            });
          }
        }
      }

      // Apply damage to King
      if (totalDamageToKing > 0) {
        newState.kingHealth = Math.max(0, newState.kingHealth - totalDamageToKing);

        events.push({
          type: 'king_damaged',
          kingId: newState.currentKingId,
          damage: totalDamageToKing,
          healthRemaining: newState.kingHealth,
        });

        // Check if King died from subject attacks
        if (newState.kingHealth <= 0) {
          const newKing = findStrongestEnemyForCrown(input.enemies, newState.currentKingId);

          if (newKing) {
            newState.crownPassCount += 1;
            const oldKingId = newState.currentKingId;
            newState.currentKingId = newKing.id;
            newState.kingMaxHealth = newKing.maxHealth * config.kingHealthMultiplier;
            newState.kingHealth = newState.kingMaxHealth;
            newState.loyalSubjects = new Set(input.enemies.filter(e => e.id !== newKing.id).map(e => e.id));

            // Generate scaled rewards
            const passScale = Math.pow(config.xpScalePerPass, newState.crownPassCount - 1);
            const healthScale = Math.pow(config.healthScalePerPass, newState.crownPassCount - 1);

            rewards = {
              xp: Math.floor(config.baseXpReward * passScale),
              health: Math.floor(config.baseHealthReward * healthScale),
              powerSurge: true,
              powerSurgeDuration: config.powerSurgeDuration,
            };

            newState.kingDeathRewards = [
              { type: 'xp', amount: rewards.xp },
              { type: 'health', amount: rewards.health },
              { type: 'power_surge', amount: config.powerSurgeDamageMultiplier },
            ];

            events.push({
              type: 'king_died',
              kingId: oldKingId,
              rewards: newState.kingDeathRewards,
            });

            events.push({
              type: 'crown_passed',
              fromKingId: oldKingId,
              toKingId: newKing.id,
              passCount: newState.crownPassCount,
            });
          } else {
            // No enemies left - clear the state
            newState.currentKingId = null;
            newState.kingHealth = 0;
            newState.kingMaxHealth = 0;
            newState.loyalSubjects.clear();
          }
        }
      }
    }
  }

  return {
    state: newState,
    modifiedEnemies,
    events,
    rewards,
  };
}

/**
 * Check if an enemy is The King
 */
export function isTheKing(enemyId: string, state: WildUpgradeState['royalDecree']): boolean {
  return state.active && state.currentKingId === enemyId;
}

/**
 * Get The King's health percentage
 */
export function getKingHealthPercent(state: WildUpgradeState['royalDecree']): number {
  if (!state.currentKingId || state.kingMaxHealth <= 0) return 0;
  return state.kingHealth / state.kingMaxHealth;
}

/**
 * Check if an enemy is a loyal subject (attacking The King)
 */
export function isLoyalSubject(enemyId: string, state: WildUpgradeState['royalDecree']): boolean {
  return state.active && state.loyalSubjects.has(enemyId);
}

/**
 * Initialize ROYAL DECREE state when upgrade is acquired
 * Automatically crowns a random enemy as The King
 */
export function initializeRoyalDecree(
  enemies: Array<{ id: string; health: number; maxHealth: number }>,
  config = ROYAL_DECREE_CONFIG
): WildUpgradeState['royalDecree'] {
  // No enemies to crown - set active but wait for enemies
  if (enemies.length === 0) {
    return {
      active: true,
      currentKingId: null,
      kingHealth: 0,
      kingMaxHealth: 0,
      crownPassCount: 0,
      loyalSubjects: new Set(),
      kingDeathRewards: [],
    };
  }

  // Pick a random enemy to be the first King
  const randomIndex = Math.floor(Math.random() * enemies.length);
  const king = enemies[randomIndex];

  // All other enemies become loyal subjects
  const subjects = new Set(
    enemies.filter(e => e.id !== king.id).map(e => e.id)
  );

  return {
    active: true,
    currentKingId: king.id,
    kingHealth: king.maxHealth * config.kingHealthMultiplier,
    kingMaxHealth: king.maxHealth * config.kingHealthMultiplier,
    crownPassCount: 0,
    loyalSubjects: subjects,
    kingDeathRewards: [],
  };
}

// =============================================================================
// ECHO SYSTEM - "Your shadow fights too"
// A ghost hornet follows the player, repeating every action 0.5 seconds later.
// Two hornets = double the carnage.
// =============================================================================

/**
 * ECHO constants - the ghost hornet that repeats your actions
 */
export const ECHO_CONFIG = {
  /** Delay before ghost replays actions (ms) */
  DELAY_MS: 500,
  /** Ghost visual alpha (transparency) */
  GHOST_ALPHA: 0.6,
  /** Maximum actions to buffer */
  MAX_ACTION_QUEUE: 60, // ~1 second at 60fps
  /** Ghost trail particle interval (ms) */
  TRAIL_INTERVAL: 50,
  /** Ghost attack damage multiplier */
  GHOST_DAMAGE_MULT: 1.0,
  /** Ghost movement smoothing factor */
  SMOOTHING: 0.15,
  /** Ethereal blue color for ghost */
  GHOST_COLOR: '#88CCFF',
  /** Secondary ghost color */
  GHOST_COLOR_SECONDARY: '#4488CC',
  /** Trail history length for particle rendering */
  TRAIL_HISTORY_LENGTH: 8,
} as const;

/**
 * Record a player action for the ghost to replay later
 */
export function recordEchoAction(
  echoState: WildUpgradeState['echo'],
  action: Omit<EchoAction, 'timestamp'>,
  currentTime: number
): WildUpgradeState['echo'] {
  if (!echoState.active) return echoState;

  const newAction: EchoAction = {
    ...action,
    timestamp: currentTime,
  };

  // Add to queue and trim if too large
  const actionQueue = [...echoState.actionQueue, newAction];
  if (actionQueue.length > ECHO_CONFIG.MAX_ACTION_QUEUE) {
    actionQueue.shift();
  }

  return {
    ...echoState,
    actionQueue,
  };
}

/**
 * Get actions that the ghost should execute now (0.5s delayed)
 */
export function getReplayableActions(
  echoState: WildUpgradeState['echo'],
  currentTime: number
): EchoAction[] {
  if (!echoState.active) return [];

  const replayTime = currentTime - ECHO_CONFIG.DELAY_MS;
  return echoState.actionQueue.filter(
    action => action.timestamp <= replayTime
  );
}

/**
 * Remove actions that have been replayed
 */
export function pruneReplayedActions(
  echoState: WildUpgradeState['echo'],
  currentTime: number
): WildUpgradeState['echo'] {
  const replayTime = currentTime - ECHO_CONFIG.DELAY_MS;
  // Keep only actions that haven't been replayed yet
  const actionQueue = echoState.actionQueue.filter(
    action => action.timestamp > replayTime
  );

  return {
    ...echoState,
    actionQueue,
  };
}

/**
 * Ghost rendering state for the canvas
 */
export interface EchoGhostRenderState {
  position: Vector2;
  velocity: Vector2;
  alpha: number;
  isAttacking: boolean;
  attackDirection: Vector2 | null;
  attackProgress: number; // 0-1 for attack animation
  trailHistory: Vector2[]; // Recent positions for ghost trail effect
  isDashing: boolean;
  dashDirection: Vector2 | null;
}

/**
 * Result of updating the ECHO system
 */
export interface EchoUpdateResult {
  state: WildUpgradeState['echo'];
  ghostRender: EchoGhostRenderState;
  /** Attacks the ghost should perform (hit detection needed) */
  attacks: Array<{
    position: Vector2;
    direction: Vector2;
    damage: number;
  }>;
  /** Dashes the ghost should perform */
  dashEvents: Array<{
    startPosition: Vector2;
    endPosition: Vector2;
    direction: Vector2;
  }>;
  /** Did the ghost perform any action this frame (for juice) */
  didAction: boolean;
}

// Internal trail history tracking (not in state to avoid serialization issues)
let echoTrailHistory: Vector2[] = [];

/**
 * Main ECHO update function - call each frame
 *
 * This handles:
 * 1. Recording player actions with timestamps
 * 2. Replaying actions 0.5s later for the ghost
 * 3. Updating ghost position/velocity
 * 4. Generating attack/dash events from replayed actions
 * 5. Tracking trail points for particles
 */
export function updateEchoSystem(
  echoState: WildUpgradeState['echo'],
  playerPosition: Vector2,
  playerVelocity: Vector2,
  currentTime: number,
  _deltaTime: number,
  isAttacking: boolean,
  attackDirection: Vector2 | null,
  isDashing: boolean,
  dashDirection: Vector2 | null,
  baseDamage: number
): EchoUpdateResult {
  // If not active, return minimal result
  if (!echoState.active) {
    echoTrailHistory = [];
    return {
      state: echoState,
      ghostRender: {
        position: { x: 0, y: 0 },
        velocity: { x: 0, y: 0 },
        alpha: 0,
        isAttacking: false,
        attackDirection: null,
        attackProgress: 0,
        trailHistory: [],
        isDashing: false,
        dashDirection: null,
      },
      attacks: [],
      dashEvents: [],
      didAction: false,
    };
  }

  // Step 1: Record current player actions
  let updatedState = echoState;

  // Record movement continuously
  updatedState = recordEchoAction(updatedState, {
    type: 'move',
    position: { ...playerPosition },
    direction: { ...playerVelocity },
  }, currentTime);

  // Record attack if player is attacking
  if (isAttacking && attackDirection) {
    updatedState = recordEchoAction(updatedState, {
      type: 'attack',
      position: { ...playerPosition },
      direction: { ...attackDirection },
      data: { damage: baseDamage },
    }, currentTime);
  }

  // Record dash if player is dashing
  if (isDashing && dashDirection) {
    updatedState = recordEchoAction(updatedState, {
      type: 'dash',
      position: { ...playerPosition },
      direction: { ...dashDirection },
    }, currentTime);
  }

  // Step 2: Get actions to replay
  const replayableActions = getReplayableActions(updatedState, currentTime);

  // Step 3: Process movement actions for ghost position
  const moveActions = replayableActions.filter(a => a.type === 'move');
  let targetPosition = updatedState.ghostPosition;
  let targetVelocity = updatedState.ghostVelocity;

  if (moveActions.length > 0) {
    // Get the most recent movement action
    const latestMove = moveActions[moveActions.length - 1];
    targetPosition = latestMove.position;
    targetVelocity = latestMove.direction;
  }

  // Smooth interpolation to target position
  const smoothing = ECHO_CONFIG.SMOOTHING;
  const newGhostPosition: Vector2 = {
    x: updatedState.ghostPosition.x + (targetPosition.x - updatedState.ghostPosition.x) * smoothing,
    y: updatedState.ghostPosition.y + (targetPosition.y - updatedState.ghostPosition.y) * smoothing,
  };
  const newGhostVelocity: Vector2 = {
    x: updatedState.ghostVelocity.x + (targetVelocity.x - updatedState.ghostVelocity.x) * smoothing,
    y: updatedState.ghostVelocity.y + (targetVelocity.y - updatedState.ghostVelocity.y) * smoothing,
  };

  // Step 4: Update trail history
  echoTrailHistory.push({ ...newGhostPosition });
  if (echoTrailHistory.length > ECHO_CONFIG.TRAIL_HISTORY_LENGTH) {
    echoTrailHistory.shift();
  }

  // Step 5: Generate attack events from replayed actions
  const attacks: EchoUpdateResult['attacks'] = [];
  const attackActions = replayableActions.filter(a => a.type === 'attack');
  for (const attack of attackActions) {
    attacks.push({
      position: attack.position,
      direction: attack.direction,
      damage: (attack.data as { damage: number })?.damage ?? baseDamage * ECHO_CONFIG.GHOST_DAMAGE_MULT,
    });
  }

  // Step 6: Generate dash events from replayed actions
  const dashEvents: EchoUpdateResult['dashEvents'] = [];
  const dashActions = replayableActions.filter(a => a.type === 'dash');
  for (const dash of dashActions) {
    // Estimate end position based on dash direction
    const dashDistance = 100; // Approximate dash distance
    dashEvents.push({
      startPosition: dash.position,
      endPosition: {
        x: dash.position.x + dash.direction.x * dashDistance,
        y: dash.position.y + dash.direction.y * dashDistance,
      },
      direction: dash.direction,
    });
  }

  // Step 7: Check for actions in current replay window for animation
  const isGhostAttacking = attackActions.length > 0;
  const ghostAttackDirection = isGhostAttacking ? attackActions[0].direction : null;
  const isGhostDashing = dashActions.length > 0;
  const ghostDashDirection = isGhostDashing ? dashActions[0].direction : null;

  // Step 8: Prune replayed actions
  updatedState = pruneReplayedActions(updatedState, currentTime);

  // Step 9: Update state with new ghost position
  updatedState = {
    ...updatedState,
    ghostPosition: newGhostPosition,
    ghostVelocity: newGhostVelocity,
  };

  const didAction = isGhostAttacking || isGhostDashing;

  return {
    state: updatedState,
    ghostRender: {
      position: newGhostPosition,
      velocity: newGhostVelocity,
      alpha: ECHO_CONFIG.GHOST_ALPHA,
      isAttacking: isGhostAttacking,
      attackDirection: ghostAttackDirection,
      attackProgress: isGhostAttacking ? 0.5 : 0, // Middle of attack animation
      trailHistory: [...echoTrailHistory],
      isDashing: isGhostDashing,
      dashDirection: ghostDashDirection,
    },
    attacks,
    dashEvents,
    didAction,
  };
}

/**
 * Activate the ECHO upgrade
 */
export function activateEcho(
  state: WildUpgradeState,
  playerPosition: Vector2
): WildUpgradeState {
  echoTrailHistory = []; // Reset trail on activation
  return {
    ...state,
    echo: {
      active: true,
      ghostPosition: { ...playerPosition },
      ghostVelocity: { x: 0, y: 0 },
      actionQueue: [],
      ghostAlpha: ECHO_CONFIG.GHOST_ALPHA,
    },
  };
}

/**
 * Deactivate the ECHO upgrade
 */
export function deactivateEcho(state: WildUpgradeState): WildUpgradeState {
  echoTrailHistory = [];
  return {
    ...state,
    echo: {
      active: false,
      ghostPosition: { x: 0, y: 0 },
      ghostVelocity: { x: 0, y: 0 },
      actionQueue: [],
      ghostAlpha: 0,
    },
  };
}

/**
 * Check if ghost attack hits any enemies
 * Returns list of enemy IDs that were hit with damage
 */
export function checkEchoAttackHits(
  ghostAttack: { position: Vector2; direction: Vector2; damage: number },
  enemies: Array<{ id: string; position: Vector2; radius: number; health: number }>,
  attackRange: number = 60
): Array<{ enemyId: string; damage: number }> {
  const hits: Array<{ enemyId: string; damage: number }> = [];

  for (const enemy of enemies) {
    if (enemy.health <= 0) continue;

    // Simple arc check in attack direction
    const dx = enemy.position.x - ghostAttack.position.x;
    const dy = enemy.position.y - ghostAttack.position.y;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist > attackRange + enemy.radius) continue;

    // Check if enemy is roughly in attack direction (120 degree arc)
    const enemyAngle = Math.atan2(dy, dx);
    const attackAngle = Math.atan2(ghostAttack.direction.y, ghostAttack.direction.x);
    let angleDiff = Math.abs(enemyAngle - attackAngle);
    if (angleDiff > Math.PI) angleDiff = 2 * Math.PI - angleDiff;

    if (angleDiff < Math.PI / 3) { // 60 degrees either side = 120 degree arc
      hits.push({
        enemyId: enemy.id,
        damage: ghostAttack.damage,
      });
    }
  }

  return hits;
}

/**
 * Check if ghost dash hits any enemies (for dash damage)
 */
export function checkEchoDashHits(
  dashEvent: { startPosition: Vector2; endPosition: Vector2; direction: Vector2 },
  enemies: Array<{ id: string; position: Vector2; radius: number; health: number }>,
  dashWidth: number = 30
): Array<{ enemyId: string }> {
  const hits: Array<{ enemyId: string }> = [];

  // Check enemies along dash path
  for (const enemy of enemies) {
    if (enemy.health <= 0) continue;

    // Point-to-line-segment distance check
    const { startPosition, endPosition } = dashEvent;
    const enemyPos = enemy.position;

    // Vector from start to end
    const dx = endPosition.x - startPosition.x;
    const dy = endPosition.y - startPosition.y;
    const lengthSq = dx * dx + dy * dy;

    if (lengthSq === 0) continue; // Degenerate dash

    // Project enemy position onto dash line
    const t = Math.max(0, Math.min(1,
      ((enemyPos.x - startPosition.x) * dx + (enemyPos.y - startPosition.y) * dy) / lengthSq
    ));

    // Closest point on dash line
    const closestX = startPosition.x + t * dx;
    const closestY = startPosition.y + t * dy;

    // Distance from enemy to closest point
    const distX = enemyPos.x - closestX;
    const distY = enemyPos.y - closestY;
    const dist = Math.sqrt(distX * distX + distY * distY);

    if (dist <= dashWidth + enemy.radius) {
      hits.push({ enemyId: enemy.id });
    }
  }

  return hits;
}

/**
 * Get the ECHO ghost's current render info (for canvas drawing)
 */
export function getEchoRenderInfo(state: WildUpgradeState['echo']): {
  active: boolean;
  position: Vector2;
  alpha: number;
  color: string;
  colorSecondary: string;
} {
  return {
    active: state.active,
    position: state.ghostPosition,
    alpha: state.ghostAlpha,
    color: ECHO_CONFIG.GHOST_COLOR,
    colorSecondary: ECHO_CONFIG.GHOST_COLOR_SECONDARY,
  };
}

/**
 * Reset ECHO trail history (call on game restart)
 */
export function resetEchoTrailHistory(): void {
  echoTrailHistory = [];
}

// =============================================================================
// HONEY TRAP MECHANICS
// =============================================================================
// "Stick together. Die together."
// Place honey zones, trap enemies, chain them together, break chain = EXPLOSION

export const HONEY_TRAP_CONFIG = {
  ZONE_RADIUS: 60,
  ZONE_DURATION: 8000,
  MAX_ZONES: 5,
  COOLDOWN: 3000,
  SLOW_MULTIPLIER: 0.2,
  CHAIN_MIN_ENEMIES: 2,
  CHAIN_BREAK_RADIUS: 80,
  BASE_EXPLOSION_DAMAGE: 50,
  DAMAGE_PER_CHAIN_MEMBER: 25,
  EXPLOSION_RADIUS: 80,
  HONEY_COLOR: '#FFCC00',
  HONEY_COLOR_DARK: '#CC9900',
  CHAIN_COLOR: '#FFD700',
  EXPLOSION_COLOR: '#FF8800',
};

export interface HoneyTrapUpdateResult {
  state: WildUpgradeState['honeyTrap'];
  trapPlaced: { position: Vector2; id: string } | null;
  chainBreaks: Array<{
    chainId: string;
    position: Vector2;
    memberCount: number;
    damage: number;
    affectedEnemyIds: string[];
  }>;
  slowedEnemies: Map<string, number>;
}

export function placeHoneyTrap(
  state: WildUpgradeState['honeyTrap'],
  playerPosition: Vector2,
  currentTime: number
): { state: WildUpgradeState['honeyTrap']; placed: boolean; trapId: string | null } {
  const timeSinceLastTrap = currentTime - state.lastTrapTime;
  if (timeSinceLastTrap < state.trapCooldown) {
    return { state, placed: false, trapId: null };
  }
  let traps = [...state.traps];
  if (traps.length >= state.maxTraps) {
    traps = traps.slice(1);
  }
  const trapId = `honey-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
  const newTrap: HoneyTrapZone = {
    id: trapId,
    position: { ...playerPosition },
    radius: HONEY_TRAP_CONFIG.ZONE_RADIUS,
    strength: 1.0,
    trappedEnemies: new Set(),
    lifetime: 0,
    maxLifetime: HONEY_TRAP_CONFIG.ZONE_DURATION,
  };
  return {
    state: { ...state, traps: [...traps, newTrap], lastTrapTime: currentTime },
    placed: true,
    trapId,
  };
}

export function updateHoneyTrap(
  state: WildUpgradeState['honeyTrap'],
  enemies: Array<{ id: string; position: Vector2; health: number }>,
  deltaTime: number,
  currentTime: number
): HoneyTrapUpdateResult {
  if (!state.active) {
    return { state, trapPlaced: null, chainBreaks: [], slowedEnemies: new Map() };
  }
  const chainBreaks: HoneyTrapUpdateResult['chainBreaks'] = [];
  const slowedEnemies = new Map<string, number>();
  let traps = state.traps
    .map(trap => ({ ...trap, lifetime: trap.lifetime + deltaTime, trappedEnemies: new Set(trap.trappedEnemies) }))
    .filter(trap => trap.lifetime < trap.maxLifetime);
  const enemyMap = new Map(enemies.map(e => [e.id, e]));
  const deadEnemyIds = new Set<string>();
  const enemyToZone = new Map<string, string>();

  for (const trap of traps) {
    const previouslyTrapped = new Set(trap.trappedEnemies);
    trap.trappedEnemies.clear();
    for (const enemy of enemies) {
      const dx = enemy.position.x - trap.position.x;
      const dy = enemy.position.y - trap.position.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      if (distance <= trap.radius) {
        trap.trappedEnemies.add(enemy.id);
        enemyToZone.set(enemy.id, trap.id);
        slowedEnemies.set(enemy.id, HONEY_TRAP_CONFIG.SLOW_MULTIPLIER);
      }
    }
    for (const trappedId of previouslyTrapped) {
      if (!enemyMap.has(trappedId)) deadEnemyIds.add(trappedId);
    }
  }

  let chains = [...state.chains];
  const zoneChains = new Map<string, Set<string>>();
  for (const trap of traps) {
    if (trap.trappedEnemies.size >= HONEY_TRAP_CONFIG.CHAIN_MIN_ENEMIES) {
      zoneChains.set(trap.id, new Set(trap.trappedEnemies));
    }
  }

  const chainsToBreak: EnemyChain[] = [];
  const chainsToKeep: EnemyChain[] = [];
  for (const chain of chains) {
    const memberZones = new Set<string>();
    let hasDeadMember = false;
    let hasMemberOutsideZone = false;
    for (const enemyId of chain.enemyIds) {
      if (deadEnemyIds.has(enemyId) || !enemyMap.has(enemyId)) { hasDeadMember = true; break; }
      const zone = enemyToZone.get(enemyId);
      if (zone) memberZones.add(zone);
      else { hasMemberOutsideZone = true; break; }
    }
    if (hasDeadMember || hasMemberOutsideZone || memberZones.size > 1) chainsToBreak.push(chain);
    else if (memberZones.size === 1) chainsToKeep.push(chain);
  }

  for (const chain of chainsToBreak) {
    let centerX = 0, centerY = 0, validMembers = 0;
    for (const enemyId of chain.enemyIds) {
      const enemy = enemyMap.get(enemyId);
      if (enemy) { centerX += enemy.position.x; centerY += enemy.position.y; validMembers++; }
    }
    if (validMembers > 0) {
      centerX /= validMembers;
      centerY /= validMembers;
      const damage = HONEY_TRAP_CONFIG.BASE_EXPLOSION_DAMAGE + HONEY_TRAP_CONFIG.DAMAGE_PER_CHAIN_MEMBER * chain.enemyIds.length;
      chainBreaks.push({ chainId: chain.id, position: { x: centerX, y: centerY }, memberCount: chain.enemyIds.length, damage, affectedEnemyIds: chain.enemyIds });
    }
  }

  const existingChainEnemies = new Set(chainsToKeep.flatMap(c => c.enemyIds));
  const newChains: EnemyChain[] = [];
  for (const [zoneId, enemyIds] of zoneChains) {
    const unchained = [...enemyIds].filter(id => !existingChainEnemies.has(id));
    if (unchained.length >= HONEY_TRAP_CONFIG.CHAIN_MIN_ENEMIES) {
      const chainId = `chain-${zoneId}-${currentTime}`;
      newChains.push({ id: chainId, enemyIds: unchained, chainStrength: 1.0, breakDamage: HONEY_TRAP_CONFIG.BASE_EXPLOSION_DAMAGE + HONEY_TRAP_CONFIG.DAMAGE_PER_CHAIN_MEMBER * unchained.length });
      unchained.forEach(id => existingChainEnemies.add(id));
    }
  }
  chains = [...chainsToKeep, ...newChains];
  return { state: { ...state, traps, chains }, trapPlaced: null, chainBreaks, slowedEnemies };
}

export function getHoneyTrapSlow(state: WildUpgradeState['honeyTrap'], enemyPosition: Vector2): number {
  if (!state.active) return 1.0;
  for (const trap of state.traps) {
    const dx = enemyPosition.x - trap.position.x;
    const dy = enemyPosition.y - trap.position.y;
    if (Math.sqrt(dx * dx + dy * dy) <= trap.radius) return HONEY_TRAP_CONFIG.SLOW_MULTIPLIER;
  }
  return 1.0;
}

export function isEnemyTrapped(state: WildUpgradeState['honeyTrap'], enemyId: string): boolean {
  return state.traps.some(trap => trap.trappedEnemies.has(enemyId));
}

export function getHoneyZones(state: WildUpgradeState['honeyTrap']): HoneyTrapZone[] {
  return state.traps;
}

export function getHoneyChains(state: WildUpgradeState['honeyTrap']): EnemyChain[] {
  return state.chains;
}

export function isHoneyTrapReady(state: WildUpgradeState['honeyTrap'], currentTime: number): boolean {
  return currentTime - state.lastTrapTime >= state.trapCooldown;
}

export function getHoneyTrapCooldownProgress(state: WildUpgradeState['honeyTrap'], currentTime: number): number {
  return Math.min(1, (currentTime - state.lastTrapTime) / state.trapCooldown);
}

export function activateHoneyTrap(state: WildUpgradeState['honeyTrap']): WildUpgradeState['honeyTrap'] {
  return { ...state, active: true };
}

// =============================================================================
// Export
// =============================================================================

export default {
  WILD_UPGRADES,
  createInitialWildUpgradeState,
  getWildUpgradePool,
  getWildUpgrade,
  getWildSynergy,
  getActiveWildSynergies,
  // GRAVITY WELL exports
  GRAVITY_WELL_CONFIG,
  updateGravityWell,
  isEnemyOrbiting,
  getOrbitInfo,
  getGravityWellIntensity,
  // BLOOD PRICE exports
  BLOOD_PRICE_CONFIG,
  updateBloodPrice,
  spawnBloodGeyser,
  consumeBloodCharge,
  activateBloodPrice,
  getBloodPriceDamageMultiplier,
  // SWARM MIND exports
  SWARM_MIND_CONFIG,
  initializeSwarmMind,
  updateSwarmMind,
  damageSwarmHornet,
  getSwarmHornetScale,
  isSwarmActive,
  getAliveSwarmHornets,
  // METAMORPHOSIS exports
  METAMORPH_FORMS,
  METAMORPHOSIS_CONFIG,
  updateMetamorphosisState,
  getNextMetamorphForm,
  getMetamorphFormConfig,
  isEnemyWebbed,
  getTimeToNextForm,
  getFormProgress,
  // ROYAL DECREE exports
  ROYAL_DECREE_CONFIG,
  updateRoyalDecree,
  isTheKing,
  getKingHealthPercent,
  isLoyalSubject,
  // ECHO exports
  ECHO_CONFIG,
  recordEchoAction,
  getReplayableActions,
  pruneReplayedActions,
  updateEchoSystem,
  activateEcho,
  deactivateEcho,
  checkEchoAttackHits,
  checkEchoDashHits,
  getEchoRenderInfo,
  resetEchoTrailHistory,
  // HONEY TRAP exports
  HONEY_TRAP_CONFIG,
  placeHoneyTrap,
  updateHoneyTrap,
  getHoneyTrapSlow,
  isEnemyTrapped,
  getHoneyZones,
  getHoneyChains,
  isHoneyTrapReady,
  getHoneyTrapCooldownProgress,
  activateHoneyTrap,
};
