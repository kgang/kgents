/**
 * WASM Survivors - Upgrade System (DD-6, DD-7)
 *
 * Verb-based upgrades that change HOW you play, not just stats.
 * Synergy detection for emergent 1+1>2 moments.
 *
 * Upgrade Categories:
 * - pierce: Projectiles pass through enemies
 * - orbit: Damage zone orbits player
 * - dash: Space bar = instant dash
 * - multishot: Multiple projectiles per attack
 * - vampiric: Kills heal HP
 * - chain: Projectiles bounce to nearby enemies
 * - burst: Kills trigger AoE explosion
 * - slow_field: Enemies near player are slowed
 *
 * @see pilots/wasm-survivors-witnessed-run-lab/.outline.md
 */

// =============================================================================
// Types
// =============================================================================

export type UpgradeType =
  | 'pierce'
  | 'orbit'
  | 'dash'
  | 'multishot'
  | 'vampiric'
  | 'chain'
  | 'burst'
  | 'slow_field';

export interface UpgradeMechanic {
  type: UpgradeType;
  // Pierce: projectiles pass through N enemies
  pierceCount?: number;
  // Orbit: damage zone with radius and DPS
  orbitRadius?: number;
  orbitDamage?: number;
  // Dash: cooldown and distance
  dashCooldown?: number;
  dashDistance?: number;
  // Multishot: number of projectiles and spread angle
  multishotCount?: number;
  multishotSpread?: number;
  // Vampiric: heal percent on kill
  vampiricPercent?: number;
  // Chain: bounces and range
  chainBounces?: number;
  chainRange?: number;
  // Burst: AoE radius and damage
  burstRadius?: number;
  burstDamage?: number;
  // Slow field: radius and slow percent
  slowRadius?: number;
  slowPercent?: number;
}

export interface VerbUpgrade {
  id: UpgradeType;
  name: string;
  description: string;
  verb: string;
  mechanic: UpgradeMechanic;
  icon: string;
  color: string;
}

export interface Synergy {
  id: string;
  name: string;
  requires: [UpgradeType, UpgradeType];
  description: string;
  announcement: string;
}

export interface ActiveUpgrades {
  upgrades: UpgradeType[];
  synergies: string[];
  // Computed effects
  pierceCount: number;
  orbitActive: boolean;
  orbitRadius: number;
  orbitDamage: number;
  dashCooldown: number;
  dashDistance: number;
  multishotCount: number;
  multishotSpread: number;
  vampiricPercent: number;
  chainBounces: number;
  chainRange: number;
  burstRadius: number;
  burstDamage: number;
  slowRadius: number;
  slowPercent: number;
}

// =============================================================================
// Upgrade Pool (DD-6)
// =============================================================================

export const UPGRADE_POOL: VerbUpgrade[] = [
  {
    id: 'pierce',
    name: 'Piercing Shots',
    description: 'Bullets pass through enemies',
    verb: 'pass through',
    icon: '→→',
    color: '#00D4FF',
    mechanic: {
      type: 'pierce',
      pierceCount: 2,
    },
  },
  {
    id: 'orbit',
    name: 'Orbital Guard',
    description: 'Damage zone circles you',
    verb: 'surround',
    icon: '◎',
    color: '#FFD700',
    mechanic: {
      type: 'orbit',
      orbitRadius: 60,
      orbitDamage: 15,
    },
  },
  {
    id: 'dash',
    name: 'Quick Dash',
    description: 'Press SPACE to dash forward',
    verb: 'reposition',
    icon: '⟹',
    color: '#00FF88',
    mechanic: {
      type: 'dash',
      dashCooldown: 2000,
      dashDistance: 120,
    },
  },
  {
    id: 'multishot',
    name: 'Triple Shot',
    description: 'Fire 3 bullets at once',
    verb: 'spread',
    icon: '⁂',
    color: '#FF3366',
    mechanic: {
      type: 'multishot',
      multishotCount: 3,
      multishotSpread: 15,
    },
  },
  {
    id: 'vampiric',
    name: 'Life Drain',
    description: 'Kills heal 5% max HP',
    verb: 'sustain',
    icon: '♥',
    color: '#FF0044',
    mechanic: {
      type: 'vampiric',
      vampiricPercent: 5,
    },
  },
  {
    id: 'chain',
    name: 'Chain Lightning',
    description: 'Shots jump to nearby enemies',
    verb: 'bounce',
    icon: '⚡',
    color: '#8844FF',
    mechanic: {
      type: 'chain',
      chainBounces: 2,
      chainRange: 80,
    },
  },
  {
    id: 'burst',
    name: 'Explosive Kills',
    description: 'Enemies explode on death',
    verb: 'explode',
    icon: '💥',
    color: '#FF8800',
    mechanic: {
      type: 'burst',
      burstRadius: 40,
      burstDamage: 10,
    },
  },
  {
    id: 'slow_field',
    name: 'Chill Aura',
    description: 'Nearby enemies slowed 30%',
    verb: 'control',
    icon: '❄',
    color: '#44DDFF',
    mechanic: {
      type: 'slow_field',
      slowRadius: 80,
      slowPercent: 30,
    },
  },
];

// =============================================================================
// Synergy Pool (DD-7)
// =============================================================================

export const SYNERGY_POOL: Synergy[] = [
  {
    id: 'shotgun_drill',
    name: 'Shotgun Drill',
    requires: ['pierce', 'multishot'],
    description: 'Piercing damage +50%',
    announcement: 'SYNERGY: Shotgun Drill!',
  },
  {
    id: 'whirlwind',
    name: 'Whirlwind',
    requires: ['orbit', 'dash'],
    description: 'Orbit triggers on dash',
    announcement: 'SYNERGY: Whirlwind!',
  },
  {
    id: 'blood_rush',
    name: 'Blood Rush',
    requires: ['dash', 'vampiric'],
    description: 'Dash through enemies = heal 10%',
    announcement: 'SYNERGY: Blood Rush!',
  },
  {
    id: 'cascade',
    name: 'Cascade',
    requires: ['chain', 'burst'],
    description: 'Chain triggers explosion',
    announcement: 'SYNERGY: Cascade!',
  },
  {
    id: 'fireworks',
    name: 'Fireworks',
    requires: ['multishot', 'burst'],
    description: 'Each projectile can burst',
    announcement: 'SYNERGY: Fireworks!',
  },
];

// =============================================================================
// Upgrade Logic
// =============================================================================

/**
 * Get upgrade definition by ID
 */
export function getUpgrade(id: UpgradeType): VerbUpgrade | undefined {
  return UPGRADE_POOL.find((u) => u.id === id);
}

/**
 * Generate upgrade choices for level up
 * Returns 3 random upgrades from pool, excluding already owned
 */
export function generateUpgradeChoices(
  ownedUpgrades: UpgradeType[],
  count: number = 3
): VerbUpgrade[] {
  // Filter out already owned upgrades
  const available = UPGRADE_POOL.filter((u) => !ownedUpgrades.includes(u.id));

  // If not enough available, include owned for stacking (future feature)
  if (available.length < count) {
    return available;
  }

  // Shuffle and pick
  const shuffled = [...available].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
}

/**
 * Check for newly activated synergies
 * Returns synergies that just became active
 */
export function detectNewSynergies(
  ownedUpgrades: UpgradeType[],
  existingSynergies: string[]
): Synergy[] {
  const newSynergies: Synergy[] = [];

  for (const synergy of SYNERGY_POOL) {
    // Skip if already discovered
    if (existingSynergies.includes(synergy.id)) continue;

    // Check if both required upgrades are owned
    const [req1, req2] = synergy.requires;
    if (ownedUpgrades.includes(req1) && ownedUpgrades.includes(req2)) {
      newSynergies.push(synergy);
    }
  }

  return newSynergies;
}

/**
 * Create initial active upgrades state
 */
export function createInitialActiveUpgrades(): ActiveUpgrades {
  return {
    upgrades: [],
    synergies: [],
    pierceCount: 0,
    orbitActive: false,
    orbitRadius: 0,
    orbitDamage: 0,
    dashCooldown: 0,
    dashDistance: 0,
    multishotCount: 1,
    multishotSpread: 0,
    vampiricPercent: 0,
    chainBounces: 0,
    chainRange: 0,
    burstRadius: 0,
    burstDamage: 0,
    slowRadius: 0,
    slowPercent: 0,
  };
}

/**
 * Apply an upgrade and return updated active upgrades
 */
export function applyUpgrade(
  current: ActiveUpgrades,
  upgradeId: UpgradeType
): { active: ActiveUpgrades; newSynergies: Synergy[] } {
  const upgrade = getUpgrade(upgradeId);
  if (!upgrade) {
    return { active: current, newSynergies: [] };
  }

  const newUpgrades = [...current.upgrades, upgradeId];
  const newSynergies = detectNewSynergies(newUpgrades, current.synergies);
  const synergyIds = [...current.synergies, ...newSynergies.map((s) => s.id)];

  // Apply mechanic effects
  const mechanic = upgrade.mechanic;
  const active: ActiveUpgrades = {
    ...current,
    upgrades: newUpgrades,
    synergies: synergyIds,
  };

  switch (mechanic.type) {
    case 'pierce':
      active.pierceCount = (current.pierceCount || 0) + (mechanic.pierceCount || 2);
      break;
    case 'orbit':
      active.orbitActive = true;
      active.orbitRadius = Math.max(current.orbitRadius, mechanic.orbitRadius || 60);
      active.orbitDamage = (current.orbitDamage || 0) + (mechanic.orbitDamage || 15);
      break;
    case 'dash':
      active.dashCooldown = mechanic.dashCooldown || 2000;
      active.dashDistance = mechanic.dashDistance || 120;
      break;
    case 'multishot':
      active.multishotCount = Math.max(current.multishotCount, mechanic.multishotCount || 3);
      active.multishotSpread = mechanic.multishotSpread || 15;
      break;
    case 'vampiric':
      active.vampiricPercent = (current.vampiricPercent || 0) + (mechanic.vampiricPercent || 5);
      break;
    case 'chain':
      active.chainBounces = (current.chainBounces || 0) + (mechanic.chainBounces || 2);
      active.chainRange = Math.max(current.chainRange, mechanic.chainRange || 80);
      break;
    case 'burst':
      active.burstRadius = Math.max(current.burstRadius, mechanic.burstRadius || 40);
      active.burstDamage = (current.burstDamage || 0) + (mechanic.burstDamage || 10);
      break;
    case 'slow_field':
      active.slowRadius = Math.max(current.slowRadius, mechanic.slowRadius || 80);
      active.slowPercent = Math.min(current.slowPercent + (mechanic.slowPercent || 30), 80);
      break;
  }

  // Apply synergy bonuses
  for (const synergy of newSynergies) {
    applySynergyBonus(active, synergy);
  }

  return { active, newSynergies };
}

/**
 * Apply synergy bonus effects
 */
function applySynergyBonus(active: ActiveUpgrades, synergy: Synergy): void {
  switch (synergy.id) {
    case 'shotgun_drill':
      // Pierce damage bonus handled in combat
      break;
    case 'whirlwind':
      // Orbit on dash handled in dash logic
      active.orbitDamage = Math.floor(active.orbitDamage * 1.3);
      break;
    case 'blood_rush':
      // Dash heal handled in dash logic
      active.vampiricPercent += 5;
      break;
    case 'cascade':
      // Chain triggers burst handled in combat
      active.burstDamage = Math.floor(active.burstDamage * 1.25);
      break;
    case 'fireworks':
      // Each projectile can burst handled in combat
      break;
  }
}

/**
 * Get build identity name based on upgrades
 * Returns a descriptive name for the player's build
 */
export function getBuildIdentity(upgrades: UpgradeType[]): string {
  if (upgrades.length === 0) return 'Starter';
  if (upgrades.length === 1) return getUpgrade(upgrades[0])?.name || 'Custom';

  // Check for dominant playstyle
  const hasAggro = upgrades.some((u) => ['pierce', 'multishot', 'burst', 'chain'].includes(u));
  const hasDefense = upgrades.some((u) => ['orbit', 'slow_field', 'vampiric'].includes(u));
  const hasMobility = upgrades.includes('dash');

  if (hasAggro && hasDefense && hasMobility) return 'All-Rounder';
  if (hasAggro && !hasDefense) return 'Glass Cannon';
  if (hasDefense && !hasAggro) return 'Tank';
  if (hasMobility && hasAggro) return 'Speed Demon';
  if (upgrades.includes('orbit')) return 'Orbit Master';

  // Check for synergy-based names
  if (upgrades.includes('pierce') && upgrades.includes('multishot')) return 'Shotgun Drill';
  if (upgrades.includes('chain') && upgrades.includes('burst')) return 'Cascade';
  if (upgrades.includes('multishot') && upgrades.includes('burst')) return 'Fireworks';

  return 'Custom Build';
}

export default {
  UPGRADE_POOL,
  SYNERGY_POOL,
  getUpgrade,
  generateUpgradeChoices,
  detectNewSynergies,
  createInitialActiveUpgrades,
  applyUpgrade,
  getBuildIdentity,
};
