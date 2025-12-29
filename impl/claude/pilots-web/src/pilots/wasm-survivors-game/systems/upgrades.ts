/**
 * WASM Survivors - Upgrade System (DD-6, DD-7)
 *
 * Verb-based upgrades that change HOW you play, not just stats.
 * Synergy detection for emergent 1+1>2 moments.
 * Archetype detection for build identity.
 * Ghost tracking for "what if" tension.
 *
 * THE ALCHEMY QUESTION:
 * > "Am I building toward something, or just picking the biggest number?"
 * If BIGGEST NUMBER -> redesign the upgrades.
 *
 * UPGRADE LAWS (from PROTO_SPEC):
 * - U1: Upgrades change HOW you act, not just HOW MUCH
 * - U2: By wave 5, player should have a nameable identity
 * - U3: Synergies exist (1 + 1 > 2 somewhere)
 * - U4: Every choice is meaningful (no obvious "best")
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md Section S5
 */

// =============================================================================
// Types
// =============================================================================

/**
 * All upgrade types - 12 verb-based upgrades
 * Original 8 + 4 new for archetype completion
 */
export type UpgradeType =
  | 'pierce'      // pass through enemies
  | 'orbit'       // damage zone circles player
  | 'dash'        // instant reposition
  | 'multishot'   // spread attack
  | 'vampiric'    // sustain through kills
  | 'chain'       // bouncing attacks
  | 'burst'       // death explosions
  | 'slow_field'  // area control
  | 'venom'       // paralysis stacking (NEW)
  | 'bleed'       // damage over time (NEW)
  | 'fear'        // enemies flee on kills (NEW)
  | 'frenzy';     // speed snowball (NEW)

/**
 * The Six Archetypes from PROTO_SPEC S5
 * Each has a fantasy, core upgrades, and playstyle
 */
export type ArchetypeId =
  | 'executioner'  // Max damage per strike
  | 'survivor'     // Outlast the swarm
  | 'skirmisher'   // Never stop moving
  | 'terror'       // Break their will
  | 'assassin'     // Precision elimination
  | 'berserker';   // Overwhelming offense

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
  // Venom: stacks for paralysis (NEW)
  venomStacksForParalysis?: number;
  venomStackDuration?: number;
  venomParalysisDuration?: number;
  // Bleed: DoT stacking (NEW)
  bleedDamagePerSecond?: number;
  bleedMaxStacks?: number;
  bleedDuration?: number;
  // Fear: enemies flee (NEW)
  fearRadius?: number;
  fearDuration?: number;
  // Frenzy: speed snowball (NEW)
  frenzySpeedBonusPerKill?: number;
  frenzyMaxBonus?: number;
  frenzyDecayPerSecond?: number;
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

/**
 * Synergy tier determines discovery UX
 * - basic: Subtle glow + small text
 * - strong: Screen flash + large announcement
 * - hidden: Shows as "???" until discovered
 */
export type SynergyTier = 'basic' | 'strong' | 'hidden';

export interface Synergy {
  id: string;
  name: string;
  requires: [UpgradeType, UpgradeType];
  description: string;
  announcement: string;
  tier: SynergyTier;
  archetype: ArchetypeId;  // Which archetype this synergy belongs to
  effect: SynergyEffect;   // The actual mechanical effect
}

/**
 * Synergy effects - what 1+1=3 actually means
 * Each synergy modifies combat in a specific way
 */
export interface SynergyEffect {
  // Damage modifiers
  pierceDamageMultiplier?: number;
  burstRadiusMultiplier?: number;
  orbitDamageBonus?: number;
  chainBonusBounces?: number;

  // Special behaviors
  paralyzedDamageMultiplier?: number;   // Paralysis Execute
  chainAppliesBleed?: boolean;           // Hemorrhage Chain
  piercedExplodeOnDeath?: boolean;       // Executioner's Mark
  healPerSlowedEnemy?: number;           // Drain Tank
  orbitRadiusMatchesSlow?: boolean;      // Fortress
  dashHealPercent?: number;              // Blood Rush
  dashFiresMultishot?: boolean;          // Afterimage Storm
  postDashChainBonus?: number;           // Hit and Run
  frenzyDashCooldownReduction?: number;  // Momentum
  burstTriggersFear?: boolean;           // Panic Cascade
  bleedFearRangeMultiplier?: number;     // Bleeding Terror
  chainTriggersExplosion?: boolean;      // Cascade
  firstPierceDoubleVenom?: boolean;      // Silent Strike
  postDashPierceBonus?: number;          // Shadow Dash
  paralyzedKillHealBonus?: number;       // Surgical Precision
  multishotBurst?: boolean;              // Fireworks
  frenzyAppliesBleed?: boolean;          // Blood Frenzy
  orbitScalesWithFrenzy?: boolean;       // Orbital Carnage
}

/**
 * Archetype definition - the build identity fantasy
 */
export interface Archetype {
  id: ArchetypeId;
  name: string;
  fantasy: string;
  coreUpgrades: UpgradeType[];
  color: string;
  icon: string;
  killSoundVariant: string;
}

/**
 * Ghost upgrade - tracks unchosen paths for "what if" tension
 */
export interface GhostUpgrade {
  decisionPoint: number;     // Game time when choice was made
  wave: number;              // What wave this was
  chosen: UpgradeType;       // What player picked
  unchosen: UpgradeType[];   // What player didn't pick
  potentialArchetypes: ArchetypeId[];  // What archetypes those unchosen could have led to
}

/**
 * Build identity state - tracks current archetype alignment
 */
export interface BuildIdentity {
  dominantArchetype: ArchetypeId | null;
  archetypeScores: Record<ArchetypeId, number>;
  isFullBuild: boolean;  // 5+ aligned upgrades
  ghosts: GhostUpgrade[];
}

export interface ActiveUpgrades {
  upgrades: UpgradeType[];
  synergies: string[];
  buildIdentity: BuildIdentity;

  // Computed effects - original 8
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

  // Computed effects - new 4
  venomStacksForParalysis: number;
  venomStackDuration: number;
  venomParalysisDuration: number;
  bleedDamagePerSecond: number;
  bleedMaxStacks: number;
  bleedDuration: number;
  fearRadius: number;
  fearDuration: number;
  frenzySpeedBonusPerKill: number;
  frenzyMaxBonus: number;
  frenzyDecayPerSecond: number;

  // Active synergy effects (computed from synergies)
  activeSynergyEffects: SynergyEffect;
}

// =============================================================================
// Archetype Definitions (PROTO_SPEC S5)
// =============================================================================

export const ARCHETYPES: Record<ArchetypeId, Archetype> = {
  executioner: {
    id: 'executioner',
    name: 'Executioner',
    fantasy: 'Maximum damage per strike',
    coreUpgrades: ['pierce', 'venom', 'burst', 'chain'],
    color: '#CC0000',
    icon: 'skull',
    killSoundVariant: 'crunch',  // Heavy, satisfying thud
  },
  survivor: {
    id: 'survivor',
    name: 'Survivor',
    fantasy: 'Outlast the swarm',
    coreUpgrades: ['vampiric', 'slow_field', 'orbit', 'dash'],
    color: '#00CC44',
    icon: 'shield',
    killSoundVariant: 'absorb',  // Soft absorption, healing chime
  },
  skirmisher: {
    id: 'skirmisher',
    name: 'Skirmisher',
    fantasy: 'Never stop moving',
    coreUpgrades: ['dash', 'multishot', 'chain', 'frenzy'],
    color: '#0088FF',
    icon: 'wind',
    killSoundVariant: 'snap',  // Quick, whooshing
  },
  terror: {
    id: 'terror',
    name: 'Terror',
    fantasy: 'Break their will',
    coreUpgrades: ['fear', 'burst', 'bleed', 'slow_field'],
    color: '#9900CC',
    icon: 'fear',
    killSoundVariant: 'distort',  // Distorted buzz, fear whine
  },
  assassin: {
    id: 'assassin',
    name: 'Assassin',
    fantasy: 'Precision elimination',
    coreUpgrades: ['pierce', 'venom', 'dash', 'vampiric'],
    color: '#333333',
    icon: 'dagger',
    killSoundVariant: 'precise',  // Clean stinger sound
  },
  berserker: {
    id: 'berserker',
    name: 'Berserker',
    fantasy: 'Overwhelming offense',
    coreUpgrades: ['multishot', 'burst', 'frenzy', 'bleed'],
    color: '#FF6600',
    icon: 'flame',
    killSoundVariant: 'chaos',  // Explosive crackle
  },
};

// =============================================================================
// Upgrade Pool (DD-6) - 12 Verb-Based Upgrades
// =============================================================================

export const UPGRADE_POOL: VerbUpgrade[] = [
  // ORIGINAL 8 UPGRADES
  {
    id: 'pierce',
    name: 'Piercing Shots',
    description: 'Bullets pass through enemies',
    verb: 'pass through',
    icon: '>>',
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
    icon: 'O',
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
    icon: '=>',
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
    icon: '***',
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
    icon: '<3',
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
    icon: '~>',
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
    icon: '*',
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
    icon: '~',
    color: '#44DDFF',
    mechanic: {
      type: 'slow_field',
      slowRadius: 80,
      slowPercent: 30,
    },
  },

  // NEW 4 UPGRADES (for archetype completion)
  {
    id: 'venom',
    name: 'Venom Strike',
    description: '3 hits = 1.5s paralysis',
    verb: 'paralyze',
    icon: '!!',
    color: '#7B3F9D',
    mechanic: {
      type: 'venom',
      venomStacksForParalysis: 3,
      venomStackDuration: 4000,
      venomParalysisDuration: 1500,
    },
  },
  {
    id: 'bleed',
    name: 'Bleeding Edge',
    description: 'Attacks cause stacking bleed',
    verb: 'weaken',
    icon: '///',
    color: '#CC0000',
    mechanic: {
      type: 'bleed',
      bleedDamagePerSecond: 5,
      bleedMaxStacks: 5,
      bleedDuration: 8000,
    },
  },
  {
    id: 'fear',
    name: 'Dread Aura',
    description: 'Kills cause nearby enemies to flee',
    verb: 'scatter',
    icon: '!!',
    color: '#9900CC',
    mechanic: {
      type: 'fear',
      fearRadius: 100,
      fearDuration: 2000,
    },
  },
  {
    id: 'frenzy',
    name: 'Blood Frenzy',
    description: '+10% speed per kill (decays)',
    verb: 'accelerate',
    icon: '++',
    color: '#FF4400',
    mechanic: {
      type: 'frenzy',
      frenzySpeedBonusPerKill: 0.10,
      frenzyMaxBonus: 0.50,
      frenzyDecayPerSecond: 0.05,
    },
  },
];

// =============================================================================
// Synergy Pool (DD-7) - 18 Synergies (3 per Archetype)
// =============================================================================

/**
 * THE SYNERGY DESIGN PRINCIPLE:
 * Every synergy should make players say "oh shit, these combine!"
 * 1 + 1 = 3 is the minimum. Some synergies should feel like 1 + 1 = 5.
 */
export const SYNERGY_POOL: Synergy[] = [
  // =========================================================================
  // EXECUTIONER SYNERGIES (Max Damage Per Strike)
  // =========================================================================
  {
    id: 'paralysis_execute',
    name: 'Paralysis Execute',
    requires: ['venom', 'pierce'],
    description: 'Paralyzed enemies take 2x pierce damage',
    announcement: 'SYNERGY: PARALYSIS EXECUTE!',
    tier: 'strong',
    archetype: 'executioner',
    effect: { paralyzedDamageMultiplier: 2.0 },
  },
  {
    id: 'hemorrhage_chain',
    name: 'Hemorrhage Chain',
    requires: ['bleed', 'chain'],
    description: 'Chain hits apply bleed stacks',
    announcement: 'SYNERGY: HEMORRHAGE CHAIN!',
    tier: 'strong',
    archetype: 'executioner',
    effect: { chainAppliesBleed: true },
  },
  {
    id: 'executioner_mark',
    name: "Executioner's Mark",
    requires: ['pierce', 'burst'],
    description: 'Pierced enemies explode with 2x radius',
    announcement: "SYNERGY: EXECUTIONER'S MARK!",
    tier: 'hidden',
    archetype: 'executioner',
    effect: { piercedExplodeOnDeath: true, burstRadiusMultiplier: 2.0 },
  },

  // =========================================================================
  // SURVIVOR SYNERGIES (Outlast the Swarm)
  // =========================================================================
  {
    id: 'drain_tank',
    name: 'Drain Tank',
    requires: ['vampiric', 'slow_field'],
    description: 'Heal 2% per enemy in slow field',
    announcement: 'SYNERGY: DRAIN TANK!',
    tier: 'strong',
    archetype: 'survivor',
    effect: { healPerSlowedEnemy: 0.02 },
  },
  {
    id: 'fortress',
    name: 'Fortress',
    requires: ['orbit', 'slow_field'],
    description: 'Orbit matches slow field, +50% orbit damage',
    announcement: 'SYNERGY: FORTRESS!',
    tier: 'strong',
    archetype: 'survivor',
    effect: { orbitRadiusMatchesSlow: true, orbitDamageBonus: 0.5 },
  },
  {
    id: 'blood_rush',
    name: 'Blood Rush',
    requires: ['dash', 'vampiric'],
    description: 'Dash through enemies = heal 10%',
    announcement: 'SYNERGY: BLOOD RUSH!',
    tier: 'basic',
    archetype: 'survivor',
    effect: { dashHealPercent: 0.10 },
  },

  // =========================================================================
  // SKIRMISHER SYNERGIES (Never Stop Moving)
  // =========================================================================
  {
    id: 'afterimage_storm',
    name: 'Afterimage Storm',
    requires: ['dash', 'multishot'],
    description: 'Dashing fires a spread shot behind you',
    announcement: 'SYNERGY: AFTERIMAGE STORM!',
    tier: 'strong',
    archetype: 'skirmisher',
    effect: { dashFiresMultishot: true },
  },
  {
    id: 'hit_and_run',
    name: 'Hit and Run',
    requires: ['dash', 'chain'],
    description: 'First hit after dash chains to 4 enemies',
    announcement: 'SYNERGY: HIT AND RUN!',
    tier: 'basic',
    archetype: 'skirmisher',
    effect: { postDashChainBonus: 2 },
  },
  {
    id: 'momentum',
    name: 'Momentum',
    requires: ['frenzy', 'dash'],
    description: 'Dash cooldown -50% while frenzy active',
    announcement: 'SYNERGY: MOMENTUM!',
    tier: 'hidden',
    archetype: 'skirmisher',
    effect: { frenzyDashCooldownReduction: 0.5 },
  },

  // =========================================================================
  // TERROR SYNERGIES (Break Their Will)
  // =========================================================================
  {
    id: 'panic_cascade',
    name: 'Panic Cascade',
    requires: ['fear', 'burst'],
    description: 'Explosions trigger fear on all nearby enemies',
    announcement: 'SYNERGY: PANIC CASCADE!',
    tier: 'strong',
    archetype: 'terror',
    effect: { burstTriggersFear: true },
  },
  {
    id: 'bleeding_terror',
    name: 'Bleeding Terror',
    requires: ['bleed', 'fear'],
    description: 'Bleeding enemies have 2x fear range',
    announcement: 'SYNERGY: BLEEDING TERROR!',
    tier: 'hidden',
    archetype: 'terror',
    effect: { bleedFearRangeMultiplier: 2.0 },
  },
  {
    id: 'cascade',
    name: 'Cascade',
    requires: ['chain', 'burst'],
    description: 'Chain hits trigger explosions',
    announcement: 'SYNERGY: CASCADE!',
    tier: 'strong',
    archetype: 'terror',
    effect: { chainTriggersExplosion: true },
  },

  // =========================================================================
  // ASSASSIN SYNERGIES (Precision Elimination)
  // =========================================================================
  {
    id: 'silent_strike',
    name: 'Silent Strike',
    requires: ['pierce', 'venom'],
    description: 'First pierce applies 2 venom stacks',
    announcement: 'SYNERGY: SILENT STRIKE!',
    tier: 'strong',
    archetype: 'assassin',
    effect: { firstPierceDoubleVenom: true },
  },
  {
    id: 'shadow_dash',
    name: 'Shadow Dash',
    requires: ['dash', 'pierce'],
    description: 'Dash makes next shot pierce +3 enemies',
    announcement: 'SYNERGY: SHADOW DASH!',
    tier: 'basic',
    archetype: 'assassin',
    effect: { postDashPierceBonus: 3 },
  },
  {
    id: 'surgical_precision',
    name: 'Surgical Precision',
    requires: ['venom', 'vampiric'],
    description: 'Killing paralyzed enemies heals 15%',
    announcement: 'SYNERGY: SURGICAL PRECISION!',
    tier: 'hidden',
    archetype: 'assassin',
    effect: { paralyzedKillHealBonus: 0.15 },
  },

  // =========================================================================
  // BERSERKER SYNERGIES (Overwhelming Offense)
  // =========================================================================
  {
    id: 'fireworks',
    name: 'Fireworks',
    requires: ['multishot', 'burst'],
    description: 'Each projectile can trigger explosion',
    announcement: 'SYNERGY: FIREWORKS!',
    tier: 'strong',
    archetype: 'berserker',
    effect: { multishotBurst: true },
  },
  {
    id: 'blood_frenzy',
    name: 'Blood Frenzy',
    requires: ['frenzy', 'bleed'],
    description: 'Frenzy stacks apply bleed on hit',
    announcement: 'SYNERGY: BLOOD FRENZY!',
    tier: 'hidden',
    archetype: 'berserker',
    effect: { frenzyAppliesBleed: true },
  },
  {
    id: 'orbital_carnage',
    name: 'Orbital Carnage',
    requires: ['orbit', 'frenzy'],
    description: 'Orbit damage scales with frenzy stacks',
    announcement: 'SYNERGY: ORBITAL CARNAGE!',
    tier: 'strong',
    archetype: 'berserker',
    effect: { orbitScalesWithFrenzy: true },
  },

  // =========================================================================
  // CROSS-ARCHETYPE SYNERGIES (Bonus discoveries)
  // =========================================================================
  {
    id: 'shotgun_drill',
    name: 'Shotgun Drill',
    requires: ['pierce', 'multishot'],
    description: 'Piercing damage +50%',
    announcement: 'SYNERGY: SHOTGUN DRILL!',
    tier: 'basic',
    archetype: 'berserker',  // Fits berserker fantasy
    effect: { pierceDamageMultiplier: 1.5 },
  },
  {
    id: 'whirlwind',
    name: 'Whirlwind',
    requires: ['orbit', 'dash'],
    description: 'Orbit triggers damage burst on dash',
    announcement: 'SYNERGY: WHIRLWIND!',
    tier: 'basic',
    archetype: 'survivor',
    effect: { orbitDamageBonus: 0.3 },
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
 * Get synergy definition by ID
 */
export function getSynergy(id: string): Synergy | undefined {
  return SYNERGY_POOL.find((s) => s.id === id);
}

/**
 * Generate upgrade choices for level up
 * Returns 3 random upgrades from pool, excluding already owned
 * Weights toward synergy-completing upgrades for discovery moments
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

  // Weight upgrades that would complete a synergy
  const weighted = available.map((upgrade) => {
    let weight = 1;
    // Check if this upgrade would complete any synergy
    for (const synergy of SYNERGY_POOL) {
      const [req1, req2] = synergy.requires;
      const hasOne = ownedUpgrades.includes(req1) || ownedUpgrades.includes(req2);
      const wouldComplete =
        (upgrade.id === req1 && ownedUpgrades.includes(req2)) ||
        (upgrade.id === req2 && ownedUpgrades.includes(req1));
      if (wouldComplete) {
        weight += 2; // Higher chance for synergy completion
      } else if (hasOne && (upgrade.id === req1 || upgrade.id === req2)) {
        weight += 1; // Slightly higher for partial synergy
      }
    }
    return { upgrade, weight };
  });

  // Weighted shuffle
  const shuffled = weighted
    .map((w) => ({
      ...w,
      sortKey: Math.random() * w.weight,
    }))
    .sort((a, b) => b.sortKey - a.sortKey);

  return shuffled.slice(0, count).map((w) => w.upgrade);
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
 * Calculate archetype scores based on owned upgrades
 * Returns which archetype the player is building toward
 */
export function calculateArchetypeScores(
  ownedUpgrades: UpgradeType[]
): Record<ArchetypeId, number> {
  const scores: Record<ArchetypeId, number> = {
    executioner: 0,
    survivor: 0,
    skirmisher: 0,
    terror: 0,
    assassin: 0,
    berserker: 0,
  };

  for (const upgradeId of ownedUpgrades) {
    for (const [archId, arch] of Object.entries(ARCHETYPES)) {
      if (arch.coreUpgrades.includes(upgradeId)) {
        scores[archId as ArchetypeId] += 1;
      }
    }
  }

  return scores;
}

/**
 * Determine dominant archetype from scores
 * Returns null if no clear winner (tie or all zero)
 */
export function getDominantArchetype(
  scores: Record<ArchetypeId, number>
): ArchetypeId | null {
  const entries = Object.entries(scores) as [ArchetypeId, number][];
  const maxScore = Math.max(...entries.map(([, score]) => score));

  if (maxScore === 0) return null;

  const leaders = entries.filter(([, score]) => score === maxScore);

  // If tie, no dominant archetype
  if (leaders.length > 1) return null;

  // Need at least 2 aligned upgrades to be considered "building toward"
  if (maxScore < 2) return null;

  return leaders[0][0];
}

/**
 * Create initial build identity state
 */
export function createInitialBuildIdentity(): BuildIdentity {
  return {
    dominantArchetype: null,
    archetypeScores: {
      executioner: 0,
      survivor: 0,
      skirmisher: 0,
      terror: 0,
      assassin: 0,
      berserker: 0,
    },
    isFullBuild: false,
    ghosts: [],
  };
}

/**
 * Create initial active upgrades state
 */
export function createInitialActiveUpgrades(): ActiveUpgrades {
  return {
    upgrades: [],
    synergies: [],
    buildIdentity: createInitialBuildIdentity(),

    // Original 8
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

    // New 4
    venomStacksForParalysis: 0,
    venomStackDuration: 0,
    venomParalysisDuration: 0,
    bleedDamagePerSecond: 0,
    bleedMaxStacks: 0,
    bleedDuration: 0,
    fearRadius: 0,
    fearDuration: 0,
    frenzySpeedBonusPerKill: 0,
    frenzyMaxBonus: 0,
    frenzyDecayPerSecond: 0,

    // Synergy effects
    activeSynergyEffects: {},
  };
}

/**
 * Apply an upgrade and return updated active upgrades
 * Also updates build identity and creates ghost for unchosen upgrades
 */
export function applyUpgrade(
  current: ActiveUpgrades,
  upgradeId: UpgradeType,
  unchosenUpgrades: UpgradeType[] = [],
  gameTime: number = 0,
  wave: number = 1
): { active: ActiveUpgrades; newSynergies: Synergy[] } {
  const upgrade = getUpgrade(upgradeId);
  if (!upgrade) {
    return { active: current, newSynergies: [] };
  }

  const newUpgrades = [...current.upgrades, upgradeId];
  const newSynergies = detectNewSynergies(newUpgrades, current.synergies);
  const synergyIds = [...current.synergies, ...newSynergies.map((s) => s.id)];

  // Update archetype scores
  const archetypeScores = calculateArchetypeScores(newUpgrades);
  const dominantArchetype = getDominantArchetype(archetypeScores);
  const isFullBuild = Math.max(...Object.values(archetypeScores)) >= 3;

  // Calculate what archetypes the unchosen upgrades could have led to
  const potentialArchetypes: ArchetypeId[] = [];
  for (const unchosen of unchosenUpgrades) {
    for (const [archId, arch] of Object.entries(ARCHETYPES)) {
      if (arch.coreUpgrades.includes(unchosen) && !potentialArchetypes.includes(archId as ArchetypeId)) {
        potentialArchetypes.push(archId as ArchetypeId);
      }
    }
  }

  // Create ghost for this decision
  const newGhost: GhostUpgrade = {
    decisionPoint: gameTime,
    wave,
    chosen: upgradeId,
    unchosen: unchosenUpgrades,
    potentialArchetypes,
  };

  // Apply mechanic effects
  const mechanic = upgrade.mechanic;
  const active: ActiveUpgrades = {
    ...current,
    upgrades: newUpgrades,
    synergies: synergyIds,
    buildIdentity: {
      dominantArchetype,
      archetypeScores,
      isFullBuild,
      ghosts: [...current.buildIdentity.ghosts, newGhost],
    },
  };

  // Apply original 8 upgrade mechanics
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

    // NEW 4 upgrade mechanics
    case 'venom':
      active.venomStacksForParalysis = mechanic.venomStacksForParalysis || 3;
      active.venomStackDuration = mechanic.venomStackDuration || 4000;
      active.venomParalysisDuration = mechanic.venomParalysisDuration || 1500;
      break;
    case 'bleed':
      active.bleedDamagePerSecond = (current.bleedDamagePerSecond || 0) + (mechanic.bleedDamagePerSecond || 5);
      active.bleedMaxStacks = Math.max(current.bleedMaxStacks, mechanic.bleedMaxStacks || 5);
      active.bleedDuration = mechanic.bleedDuration || 8000;
      break;
    case 'fear':
      active.fearRadius = Math.max(current.fearRadius, mechanic.fearRadius || 100);
      active.fearDuration = mechanic.fearDuration || 2000;
      break;
    case 'frenzy':
      active.frenzySpeedBonusPerKill = mechanic.frenzySpeedBonusPerKill || 0.10;
      active.frenzyMaxBonus = mechanic.frenzyMaxBonus || 0.50;
      active.frenzyDecayPerSecond = mechanic.frenzyDecayPerSecond || 0.05;
      break;
  }

  // Merge synergy effects
  const mergedEffects: SynergyEffect = { ...current.activeSynergyEffects };
  for (const synergy of newSynergies) {
    Object.assign(mergedEffects, synergy.effect);
  }
  active.activeSynergyEffects = mergedEffects;

  // Apply synergy stat bonuses
  for (const synergy of newSynergies) {
    applySynergyBonus(active, synergy);
  }

  return { active, newSynergies };
}

/**
 * Apply synergy bonus effects to stats
 */
function applySynergyBonus(active: ActiveUpgrades, synergy: Synergy): void {
  const effect = synergy.effect;

  // Stat modifications
  if (effect.orbitDamageBonus) {
    active.orbitDamage = Math.floor(active.orbitDamage * (1 + effect.orbitDamageBonus));
  }
  if (effect.chainBonusBounces) {
    active.chainBounces += effect.chainBonusBounces;
  }
  if (effect.burstRadiusMultiplier) {
    active.burstRadius = Math.floor(active.burstRadius * effect.burstRadiusMultiplier);
  }

  // Special case: Blood Rush adds vampiric %
  if (synergy.id === 'blood_rush') {
    active.vampiricPercent += 5;
  }

  // Special case: Fortress makes orbit match slow field
  if (effect.orbitRadiusMatchesSlow && active.slowRadius > 0) {
    active.orbitRadius = Math.max(active.orbitRadius, active.slowRadius);
  }
}

/**
 * Get build identity name based on current archetype
 * Returns the archetype name if building toward one, otherwise descriptive name
 */
export function getBuildIdentity(upgrades: UpgradeType[]): string {
  if (upgrades.length === 0) return 'Starter';
  if (upgrades.length === 1) return getUpgrade(upgrades[0])?.name || 'Custom';

  const scores = calculateArchetypeScores(upgrades);
  const dominant = getDominantArchetype(scores);

  if (dominant) {
    const archetype = ARCHETYPES[dominant];
    const maxScore = scores[dominant];
    if (maxScore >= 3) {
      return `Full ${archetype.name}`;
    }
    return `Building ${archetype.name}`;
  }

  // Check for synergy-based names
  for (const synergy of SYNERGY_POOL) {
    const [req1, req2] = synergy.requires;
    if (upgrades.includes(req1) && upgrades.includes(req2)) {
      return synergy.name;
    }
  }

  return 'Hybrid Build';
}

/**
 * Get ghost summary for death screen
 * Returns what archetypes player could have been
 */
export function getGhostSummary(
  buildIdentity: BuildIdentity
): {
  ghostArchetypes: ArchetypeId[];
  pivotMoments: number;
  alternateBuilds: string[];
} {
  const ghostArchetypes = new Set<ArchetypeId>();
  let pivotMoments = 0;

  for (const ghost of buildIdentity.ghosts) {
    for (const arch of ghost.potentialArchetypes) {
      ghostArchetypes.add(arch);
    }
    // Count pivot moments (where unchosen led to different archetype than current)
    if (
      buildIdentity.dominantArchetype &&
      ghost.potentialArchetypes.length > 0 &&
      !ghost.potentialArchetypes.includes(buildIdentity.dominantArchetype)
    ) {
      pivotMoments++;
    }
  }

  // Remove current archetype from ghosts
  if (buildIdentity.dominantArchetype) {
    ghostArchetypes.delete(buildIdentity.dominantArchetype);
  }

  const alternateBuilds = Array.from(ghostArchetypes).map((archId) => {
    const arch = ARCHETYPES[archId];
    return `You could have been: ${arch.name}`;
  });

  return {
    ghostArchetypes: Array.from(ghostArchetypes),
    pivotMoments,
    alternateBuilds,
  };
}

/**
 * Check if an upgrade would complete a synergy
 * Used for UI highlighting
 */
export function wouldCompleteSynergy(
  upgradeId: UpgradeType,
  ownedUpgrades: UpgradeType[],
  existingSynergies: string[]
): Synergy | null {
  for (const synergy of SYNERGY_POOL) {
    if (existingSynergies.includes(synergy.id)) continue;

    const [req1, req2] = synergy.requires;
    const wouldComplete =
      (upgradeId === req1 && ownedUpgrades.includes(req2)) ||
      (upgradeId === req2 && ownedUpgrades.includes(req1));

    if (wouldComplete) {
      return synergy;
    }
  }
  return null;
}

/**
 * Get all synergies for a specific archetype
 */
export function getSynergiesForArchetype(archetype: ArchetypeId): Synergy[] {
  return SYNERGY_POOL.filter((s) => s.archetype === archetype);
}

export default {
  // Constants
  UPGRADE_POOL,
  SYNERGY_POOL,
  ARCHETYPES,

  // Getters
  getUpgrade,
  getSynergy,
  getSynergiesForArchetype,

  // Generation
  generateUpgradeChoices,
  detectNewSynergies,
  wouldCompleteSynergy,

  // State management
  createInitialActiveUpgrades,
  createInitialBuildIdentity,
  applyUpgrade,

  // Archetype system
  calculateArchetypeScores,
  getDominantArchetype,
  getBuildIdentity,
  getGhostSummary,
};
