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
 * Six ability categories (v3 expansion with WING and PREDATOR)
 *
 * APEX STRIKE INTEGRATION: WING and PREDATOR abilities synergize with apex strike:
 * - WING: Movement creates effects that enhance strike positioning and recovery
 * - PREDATOR: Kill triggers that boost damage and control flow of battle
 */
export type AbilityCategory =
  | 'damage'    // Make your bite hurt more
  | 'speed'     // Attack faster, move faster
  | 'defense'   // Take less damage, heal more
  | 'special'   // Unique powerful effects
  | 'wing'      // Movement creates effects (apex strike synergy)
  | 'predator'  // Kill triggers (apex strike damage stacking)
  | 'pheromone' // Area denial and enemy debuffs (survival layer)
  | 'chitin';   // Body modifications (emergency and utility)

/**
 * All ability IDs - 36 total (6 per category)
 * v3 expansion: Added WING (6) and PREDATOR (6) abilities
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
  | 'venom_architect'        // Infinite venom stacks, explode on kill

  // ==========================================================================
  // WING (6) - Movement creates effects (apex strike synergy)
  //
  // DESIGN: Wing abilities turn your movement into a weapon. They synergize
  // with apex strike by enhancing positioning, recovery, and damage output.
  // All WING abilities contribute to apex strike damage indirectly through
  // enemy softening, positioning control, or kill-triggered bonuses.
  // ==========================================================================
  | 'draft'                  // Moving near enemies pulls them toward your path
  | 'buzz_field'             // Standing still creates damage aura
  | 'thermal_wake'           // Moving leaves slow trail
  | 'scatter_dust'           // Apex strike leaves obscuring dust cloud
  | 'updraft'                // Kills give speed boost for repositioning
  | 'hover_pressure'         // Being near enemies deals passive DPS

  // ==========================================================================
  // PREDATOR (6) - Kill triggers (apex strike damage stacking)
  //
  // DESIGN: Predator abilities reward aggressive play and chain kills.
  // Each ability creates damage bonuses that STACK with apex strike damage.
  // The more you kill, the more powerful your next strike becomes.
  // ==========================================================================
  | 'feeding_efficiency'     // Kills give stacking attack speed
  | 'territorial_mark'       // Kill zones grant damage bonus
  | 'trophy_scent'           // Unique kills = permanent damage bonus
  | 'pack_signal'            // Kills cause nearby enemies to hesitate
  | 'corpse_heat'            // Standing on kills grants damage bonus
  | 'clean_kill'             // One-hit kills explode for bonus damage

  // ==========================================================================
  // PHEROMONE (6) - Area Denial & Enemy Debuffs
  //
  // DESIGN: Pheromones control space and weaken enemies. They don't boost YOUR
  // damage directly, but make ENEMIES weaker or slower. Best for kiting builds.
  //
  // APEX STRIKE SYNERGY:
  // - Reduces damage from enemies during dash (survival)
  // - Creates slow zones from kills (chain kill setup)
  // - Debuffs attackers (counter-attack layer)
  //
  // STACKING: Most pheromone effects stack additively with each other.
  // threat_aura (5% reduction) + bitter_taste (10% reduction) = 15% total.
  // ==========================================================================
  | 'threat_aura'            // Passive: Enemies within 30px deal 5% less damage
  | 'confusion_cloud'        // On hit: Release cloud (40px, 2s). 10% enemy miss chance
  | 'rally_scent'            // Trail: Movement path (2s) slows enemies 5%
  | 'death_marker'           // On kill: Corpse emits slow field (15px, 3s). 10% slow
  | 'aggro_pulse'            // Every 10s: Pulse (100px) forces targeting for 1s
  | 'bitter_taste'           // Counter: Attackers deal 10% less damage for 2s
  | 'paralytic_microdose'    // Attacks apply brief slow
  | 'scissor_grip'           // Attacks have chance to stun
  | 'trace_venom'            // Enemies take damage over time after being hit

  // ==========================================================================
  // CHITIN (6) - Body Modifications (Survival & Utility)
  //
  // DESIGN: Chitin abilities modify your body for survival and utility. They
  // provide passive defenses, emergency abilities, and enhanced awareness.
  //
  // APEX STRIKE SYNERGY:
  // - Contact damage rewards aggressive dash-through tactics
  // - Speed bonuses at low HP enable clutch escapes/dashes
  // - Emergency burst provides panic button during failed dashes
  // - Enhanced vision helps plan strike angles
  //
  // STACKING: Chitin abilities mostly don't stack with themselves.
  // They provide unique one-time effects or thresholds.
  // ==========================================================================
  | 'barbed_chitin'          // Passive: Enemies touching you take 3 damage/sec
  | 'ablative_shell'         // First hit each wave deals 20% less damage
  | 'heat_retention'         // Threshold: +5% speed when below 50% HP
  | 'compound_eyes'          // Vision: See enemy attack telegraphs 0.1s earlier
  | 'antenna_sensitivity'    // Warning: Enemies highlighted 0.5s before entering screen
  | 'molting_burst';         // Emergency: At 10% HP once per run: invuln + damage burst

/**
 * Skill demand - how hard to use
 */
export type SkillDemand = 'easy' | 'medium' | 'hard';

/**
 * Juice configuration for visual/audio feedback
 */
export interface AbilityJuiceConfig {
  visual: string;           // Visual effect description
  audio?: string;           // Sound effect name
  particleType?: string;    // Type of particles to spawn
  triggerText?: string;     // Text to show when ability triggers (e.g., "CRIT!")
}

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

  // Visual/audio feedback config
  juiceConfig: AbilityJuiceConfig;
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

  // ==========================================================================
  // WING ability effects - Movement creates effects
  //
  // APEX STRIKE SYNERGY: All WING abilities enhance positioning and recovery.
  // They contribute to apex strike effectiveness through enemy grouping,
  // passive damage during charge-up, and post-kill mobility.
  // ==========================================================================
  pullStrength?: number;         // draft: Pull toward path (px/frame). Default: 0.5
  pullRadius?: number;           // draft: Trail detection radius (px). Default: 40
  stationaryDelay?: number;      // buzz_field: Delay before aura (s). Default: 0.5
  stationaryRadius?: number;     // buzz_field: Aura radius (px). Default: 20
  stationaryDps?: number;        // buzz_field: Damage per second. Default: 2
  trailDuration?: number;        // thermal_wake: Trail duration (s). Default: 2
  trailSlowPercent?: number;     // thermal_wake: Slow in trail (%). Default: 5
  dustDuration?: number;         // scatter_dust: Cloud duration (s). Default: 0.3
  dustRadius?: number;           // scatter_dust: Cloud radius (px). Default: 30
  killSpeedBoost?: number;       // updraft: Speed boost on kill (%). Default: 3
  killSpeedDuration?: number;    // updraft: Boost duration (s). Default: 1
  pressureRadius?: number;       // hover_pressure: DPS radius (px). Default: 50
  pressureDps?: number;          // hover_pressure: Damage per second. Default: 1

  // ==========================================================================
  // PREDATOR ability effects - Kill triggers that stack damage
  //
  // APEX STRIKE SYNERGY: All PREDATOR bonuses STACK MULTIPLICATIVELY with
  // apex strike damage. Each kill makes the next strike more devastating.
  // ==========================================================================
  feedingSpeedBonus?: number;    // feeding_efficiency: AS per kill (%). Default: 2
  feedingDuration?: number;      // feeding_efficiency: Bonus duration (s). Default: 3
  feedingMaxStacks?: number;     // feeding_efficiency: Max stacks. Default: 5
  markRadius?: number;           // territorial_mark: Zone radius (px). Default: 30
  markDuration?: number;         // territorial_mark: Zone duration (s). Default: 2
  markDamageBonus?: number;      // territorial_mark: Damage bonus (%). Default: 10
  trophyDamageBonus?: number;    // trophy_scent: Permanent damage per type (%). Default: 1
  signalRadius?: number;         // pack_signal: Hesitation radius (px). Default: 60
  signalDuration?: number;       // pack_signal: Hesitation duration (s). Default: 0.1
  predatorCorpseHeatRadius?: number;   // corpse_heat: Detection radius (px). Default: 20
  predatorCorpseHeatBonus?: number;    // corpse_heat: Damage bonus (%). Default: 5
  predatorCorpseHeatDuration?: number; // corpse_heat: Bonus duration (s). Default: 1
  cleanKillRadius?: number;      // clean_kill: Explosion radius (px). Default: 10
  cleanKillDamage?: number;      // clean_kill: Explosion damage. Default: 5

  // ==========================================================================
  // PHEROMONE effects - Area denial and enemy debuffs
  //
  // These effects reduce enemy effectiveness rather than boosting player damage.
  // They synergize with apex strike by creating safer dash conditions.
  // ==========================================================================
  threatAuraRadius?: number;           // Radius for threat aura (px)
  threatAuraDamageReduction?: number;  // % damage reduction for enemies in aura
  confusionCloudRadius?: number;       // Radius of confusion cloud (px)
  confusionCloudMissChance?: number;   // % miss chance for enemies in cloud
  confusionCloudDuration?: number;     // Duration of cloud (seconds)
  rallyScentTrailDuration?: number;    // Duration of slow trail (seconds)
  rallyScentSlowPercent?: number;      // % slow applied by trail
  deathMarkerRadius?: number;          // Radius of death marker slow zone (px)
  deathMarkerSlowPercent?: number;     // % slow in death marker zone
  deathMarkerDuration?: number;        // Duration of death marker (seconds)
  aggroPulseCooldown?: number;         // Cooldown between aggro pulses (seconds)
  aggroPulseRadius?: number;           // Radius of aggro pulse (px)
  aggroPulseDuration?: number;         // How long enemies are forced to target (seconds)
  bitterTasteDamageReduction?: number; // % damage reduction applied to attackers
  bitterTasteDuration?: number;        // Duration of attacker debuff (seconds)

  // ==========================================================================
  // CHITIN effects - Body modifications for survival and utility
  //
  // These effects provide passive defenses, emergency abilities, and awareness.
  // They synergize with apex strike through contact damage and clutch survival.
  // ==========================================================================
  barbedChitinDamage?: number;         // Damage per second to touching enemies
  barbedChitinRadius?: number;         // Contact radius (px)
  ablativeShellReduction?: number;     // % damage reduction on first hit per wave
  heatRetentionThreshold?: number;     // HP threshold for speed bonus (0-1)
  heatRetentionSpeedBonus?: number;    // % speed bonus when below threshold
  compoundEyesTelegraphMs?: number;    // How much earlier to show telegraphs (ms)
  antennaSensitivityMs?: number;       // How early to highlight offscreen enemies (ms)
  moltingBurstThreshold?: number;      // HP threshold to trigger burst (0-1)
  moltingBurstInvulnMs?: number;       // Invulnerability duration (ms)
  moltingBurstDamage?: number;         // Burst damage amount
  moltingBurstRadius?: number;         // Burst damage radius (px)
}

/**
 * Runtime state for abilities (temporary buffs, cooldowns, etc.)
 *
 * PHEROMONE + CHITIN runtime state enables time-based effects:
 * - confusion_cloud: Active clouds with positions and expiry times
 * - bitter_taste: Map of enemy IDs to debuff expiry times
 * - aggro_pulse: Last pulse time for cooldown tracking
 * - death_marker: Active slow zones with positions and expiry times
 * - ablative_shell: Whether first hit protection has been used this wave
 * - molting_burst: Whether emergency burst has been used this run
 */
export interface AbilityRuntime {
  // Updraft (WING ability)
  updraftExpiry: number;
  updraftSpeedBonus: number;

  // Heat retention (CHITIN ability)
  heatRetentionActive: boolean;

  // Sawtooth counter
  sawtoothCounter: number;

  // Trophy scent kills
  trophyScentKills: number;

  // ==========================================================================
  // PHEROMONE runtime state
  // ==========================================================================

  // Confusion Cloud: Active clouds on the field
  confusionClouds: Array<{
    x: number;
    y: number;
    radius: number;
    missChance: number;
    expiry: number;  // Game time when cloud expires
  }>;

  // Bitter Taste: Map of enemy IDs to their debuff expiry time
  bitterTasteDebuffs: Map<string, number>;

  // Aggro Pulse: Last pulse game time (for cooldown)
  aggroPulseLastTime: number;

  // Death Marker: Active slow zones on the field
  deathMarkers: Array<{
    x: number;
    y: number;
    radius: number;
    slowPercent: number;
    expiry: number;  // Game time when marker expires
  }>;

  // ==========================================================================
  // CHITIN runtime state
  // ==========================================================================

  // Ablative Shell: Has first hit protection been consumed this wave?
  ablativeShellUsed: boolean;

  // Molting Burst: Has emergency burst been used this run?
  moltingBurstUsed: boolean;

  // Generic expiry timers (fallback for simple timers)
  [key: string]: number | boolean | Array<unknown> | Map<string, number> | Set<unknown>;
}

/**
 * Player's active abilities state
 */
export interface ActiveAbilities {
  owned: AbilityId[];
  levels: Record<AbilityId, number>;  // For stackable abilities

  // Computed effects (sum of all abilities)
  computed: ComputedEffects;

  // Runtime state (cooldowns, temporary buffs, etc.)
  runtime: AbilityRuntime;
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

  // Advanced ability effects (stubs for future implementation)
  heatRetentionSpeedBonus: number;   // CHITIN speed boost when low HP
  scatterDustEnabled: boolean;        // WING scatter dust on dash
  corpseHeatRadius: number;           // Corpse heat detection radius
  corpseHeatBonus: number;            // Damage bonus near corpses
  sawtoothEveryN: number;             // Sawtooth triggers every N hits
  sawtoothBonus: number;              // Sawtooth damage bonus
  poisonedDamageAmp: number;          // Bonus damage vs poisoned
  histamineDamageAmp: number;         // Histamine damage amplification
  slowPerHit: number;                 // Slow applied per hit
  slowMaxStacks: number;              // Max slow stacks
  freezeChance: number;               // Chance to freeze on hit

  // More stubs for pheromone/chitin system
  armorReductionPerHit: number;       // Armor shred per hit
  knockbackPx: number;                // Knockback distance on hit
  stunChance: number;                 // Chance to stun on hit
  stunDuration: number;               // Stun duration (ms)
  markFullHpTargets: boolean;         // Mark full HP targets for bonus
  bleedDuration: number;              // Bleed effect duration (ms)
  bleedPercent: number;               // Bleed damage as % of attack

  // ==========================================================================
  // WING ability computed effects
  // ==========================================================================
  draftEnabled: boolean;              // draft: Pull enemies toward path
  draftPullStrength: number;          // draft: Pull strength (px/frame)
  draftPullRadius: number;            // draft: Trail detection radius
  buzzFieldEnabled: boolean;          // buzz_field: Stationary aura active
  buzzFieldDelay: number;             // buzz_field: Delay before activation (s)
  buzzFieldRadius: number;            // buzz_field: Aura radius (px)
  buzzFieldDps: number;               // buzz_field: Damage per second
  thermalWakeEnabled: boolean;        // thermal_wake: Trail slow active
  thermalWakeDuration: number;        // thermal_wake: Trail duration (s)
  thermalWakeSlow: number;            // thermal_wake: Slow percent
  scatterDustDuration: number;        // scatter_dust: Cloud duration (s)
  scatterDustRadius: number;          // scatter_dust: Cloud radius (px)
  updraftEnabled: boolean;            // updraft: Kill speed boost active
  updraftSpeedBoost: number;          // updraft: Speed boost percent
  updraftDuration: number;            // updraft: Boost duration (s)
  hoverPressureEnabled: boolean;      // hover_pressure: Passive DPS active
  hoverPressureRadius: number;        // hover_pressure: Aura radius (px)
  hoverPressureDps: number;           // hover_pressure: Damage per second

  // ==========================================================================
  // PREDATOR ability computed effects
  // ==========================================================================
  feedingEfficiencyEnabled: boolean;  // feeding_efficiency: Attack speed on kill
  feedingEfficiencyBonus: number;     // feeding_efficiency: Speed bonus per kill (%)
  feedingEfficiencyDuration: number;  // feeding_efficiency: Duration (s)
  feedingEfficiencyMaxStacks: number; // feeding_efficiency: Max stacks
  territorialMarkEnabled: boolean;    // territorial_mark: Kill zones active
  territorialMarkRadius: number;      // territorial_mark: Zone radius (px)
  territorialMarkDuration: number;    // territorial_mark: Zone duration (s)
  territorialMarkBonus: number;       // territorial_mark: Damage bonus (%)
  trophyScentEnabled: boolean;        // trophy_scent: Unique kill tracking
  trophyScentBonus: number;           // trophy_scent: Permanent damage bonus (%)
  packSignalEnabled: boolean;         // pack_signal: Hesitation on kill
  packSignalRadius: number;           // pack_signal: Hesitation radius (px)
  packSignalDuration: number;         // pack_signal: Hesitation duration (s)
  predatorCorpseHeatEnabled: boolean; // corpse_heat: Damage bonus near kills
  predatorCorpseHeatRadius: number;   // corpse_heat: Detection radius (px)
  predatorCorpseHeatBonus: number;    // corpse_heat: Damage bonus (%)
  predatorCorpseHeatDuration: number; // corpse_heat: Bonus duration (s)
  cleanKillEnabled: boolean;          // clean_kill: One-hit explosions
  cleanKillRadius: number;            // clean_kill: Explosion radius (px)
  cleanKillDamage: number;            // clean_kill: Explosion damage
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
    color: '#FF8844',  // Bright orange-red for damage (distinct from player #CC5500)
    stackable: true,
    maxStacks: 3,
    comboPotential: 'medium',
    effect: {
      damagePercent: 40,
    },
    juiceConfig: {
      visual: 'Orange slash marks trail from bite, damage numbers glow orange',
      audio: 'sharpen_slice',
      particleType: 'slash_marks',
      triggerText: 'SHARP!',
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
    juiceConfig: {
      visual: 'Heavy impact burst with dark orange shockwave ring',
      audio: 'crush_impact',
      particleType: 'impact_burst',
      triggerText: 'CRUSH!',
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
    juiceConfig: {
      visual: 'Green venom drips from enemy, poison tick numbers float up',
      audio: 'venom_drip',
      particleType: 'poison_drip',
      triggerText: 'POISON!',
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
    juiceConfig: {
      visual: 'Twin pink slash arcs appear, second hit slightly delayed',
      audio: 'double_hit',
      particleType: 'twin_slash',
      triggerText: 'DOUBLE!',
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
    juiceConfig: {
      visual: 'Red fire burst on low-HP enemy, screen flash on execute',
      audio: 'savage_roar',
      particleType: 'fire_burst',
      triggerText: 'SAVAGE!',
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
    juiceConfig: {
      visual: 'Blue crosshair locks on full-HP target, massive cyan impact',
      audio: 'sniper_hit',
      particleType: 'sniper_lock',
      triggerText: 'SLAYER!',
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
    juiceConfig: {
      visual: 'Yellow lightning crackles around player during attacks',
      audio: 'speed_zap',
      particleType: 'lightning_spark',
      triggerText: 'QUICK!',
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
    juiceConfig: {
      visual: 'Orange blur lines stream from player, attack arc afterimages',
      audio: 'frenzy_whoosh',
      particleType: 'speed_blur',
      triggerText: 'FRENZY!',
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
    juiceConfig: {
      visual: 'Cyan wing trails follow player movement',
      audio: 'wing_flutter',
      particleType: 'wing_trail',
      triggerText: 'SWIFT!',
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
    juiceConfig: {
      visual: 'Red speed lines point toward nearest enemy, player glows red',
      audio: 'hunt_dash',
      particleType: 'hunt_lines',
      triggerText: 'HUNT!',
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
    juiceConfig: {
      visual: 'Red-pink aura pulses around player, both attack and move leave trails',
      audio: 'berserker_roar',
      particleType: 'berserker_aura',
      triggerText: 'RAMPAGE!',
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
    juiceConfig: {
      visual: 'Purple time distortion effect, enemies have slow-motion blur',
      audio: 'time_warp',
      particleType: 'time_ripple',
      triggerText: 'BULLET TIME!',
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
    juiceConfig: {
      visual: 'Grey armor plates flash around player, HP bar pulses larger',
      audio: 'armor_clank',
      particleType: 'armor_plate',
      triggerText: 'FORTIFIED!',
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
    juiceConfig: {
      visual: 'Green shield shimmer when taking damage, reduced numbers',
      audio: 'shield_deflect',
      particleType: 'shield_shimmer',
      triggerText: 'BLOCKED!',
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
    juiceConfig: {
      visual: 'Green healing particles rise from player, +HP numbers tick',
      audio: 'heal_tick',
      particleType: 'heal_sparkle',
      triggerText: '+HP',
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
    juiceConfig: {
      visual: 'Red health orbs fly from enemy to player on hit',
      audio: 'lifesteal_drain',
      particleType: 'blood_orb',
      triggerText: 'DRAIN!',
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
    juiceConfig: {
      visual: 'Dark red aura pulses, screen edge vignette, damage heavily reduced',
      audio: 'last_stand_activate',
      particleType: 'rage_aura',
      triggerText: 'LAST STAND!',
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
    juiceConfig: {
      visual: 'Golden resurrection burst, screen flash white, dramatic pause',
      audio: 'revive_chime',
      particleType: 'golden_burst',
      triggerText: 'REVIVED!',
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
    juiceConfig: {
      visual: 'Orange explosion burst on crit, enlarged damage number flies up',
      audio: 'crit_boom',
      particleType: 'crit_burst',
      triggerText: 'CRIT!',
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
    juiceConfig: {
      visual: 'Dark red slash through enemy, instant death animation',
      audio: 'execute_slash',
      particleType: 'death_slash',
      triggerText: 'EXECUTED!',
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
    juiceConfig: {
      visual: 'Full orange circle arc around player, hits all enemies',
      audio: 'sweep_whoosh',
      particleType: 'full_circle',
      triggerText: 'SWEEP!',
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
    juiceConfig: {
      visual: 'Blue lightning bolt arcs to next target on kill',
      audio: 'chain_zap',
      particleType: 'lightning_arc',
      triggerText: 'CHAIN!',
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
    juiceConfig: {
      visual: 'Pink momentum counter builds, aura intensifies with kills',
      audio: 'momentum_build',
      particleType: 'momentum_aura',
      triggerText: 'MOMENTUM!',
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
    juiceConfig: {
      visual: 'Red crystalline aura, massive damage numbers, HP bar shrinks',
      audio: 'glass_shatter',
      particleType: 'crystal_shards',
      triggerText: 'GLASS CANNON!',
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
    juiceConfig: {
      visual: 'Magenta sparks on near-miss, stack counter pulses brighter',
      audio: 'graze_spark',
      particleType: 'graze_spark',
      triggerText: 'GRAZE!',
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
    juiceConfig: {
      visual: 'Orange heat meter builds while moving, fire explosion on stop',
      audio: 'heat_release',
      particleType: 'heat_pulse',
      triggerText: 'THERMAL RELEASE!',
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
    juiceConfig: {
      visual: 'Dark red chain links connect executed enemies',
      audio: 'chain_execution',
      particleType: 'chain_link',
      triggerText: 'CHAIN EXECUTE!',
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
    juiceConfig: {
      visual: 'Pure red aura, screen pulses with danger, massive damage numbers',
      audio: 'mastery_activate',
      particleType: 'death_aura',
      triggerText: 'MASTERY!',
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
    juiceConfig: {
      visual: 'Green venom stacks visible on enemy, green explosion on venom kill',
      audio: 'venom_explode',
      particleType: 'venom_explosion',
      triggerText: 'VENOM EXPLODE!',
    },
  },
];

// =============================================================================
// WING ABILITIES (6) - Movement creates effects
// APEX STRIKE SYNERGY: Enhance positioning, recovery, and damage during movement
// =============================================================================

const WING_ABILITIES: Ability[] = [
  {
    id: 'draft',
    name: 'Draft',
    description: 'Moving near enemies (40px) pulls them toward your path. Groups enemies for apex strikes.',
    verb: 'Pull',
    category: 'wing',
    icon: '💨',
    color: '#88CCFF',
    comboPotential: 'high',
    effect: { pullStrength: 0.5, pullRadius: 40 },
    juiceConfig: { visual: 'Air disturbance lines, enemies drift toward path', audio: 'soft_whoosh', particleType: 'wind_lines' },
  },
  {
    id: 'buzz_field',
    name: 'Buzz Field',
    description: 'Standing still for 0.5s creates 20px damage aura (2 DPS). Perfect for apex charge-up.',
    verb: 'Buzz',
    category: 'wing',
    icon: '🔊',
    color: '#FFB800',
    comboPotential: 'medium',
    effect: { stationaryDelay: 0.5, stationaryRadius: 20, stationaryDps: 2 },
    juiceConfig: { visual: 'Pulsing amber circle when active', audio: 'low_buzz_hum', particleType: 'vibration_rings', triggerText: 'BUZZ!' },
  },
  {
    id: 'thermal_wake',
    name: 'Thermal Wake',
    description: 'Moving leaves warmth trail (2s). Enemies in trail move 5% slower.',
    verb: 'Heat',
    category: 'wing',
    icon: '🌡️',
    color: '#FF6600',
    comboPotential: 'medium',
    effect: { trailDuration: 2, trailSlowPercent: 5 },
    juiceConfig: { visual: 'Heat shimmer waves behind player', audio: 'heat_hiss', particleType: 'heat_shimmer' },
  },
  {
    id: 'scatter_dust',
    name: 'Scatter Dust',
    description: 'Apex strike leaves dust cloud (30px, 0.3s) obscuring enemy vision. Miss recovery.',
    verb: 'Scatter',
    category: 'wing',
    icon: '✨',
    color: '#DDCC77',
    comboPotential: 'low',
    effect: { dustDuration: 0.3, dustRadius: 30 },
    juiceConfig: { visual: 'Golden pollen puff on dash', audio: 'soft_puff', particleType: 'dust_particles' },
  },
  {
    id: 'updraft',
    name: 'Updraft',
    description: 'Kills give +3% move speed for 1s. Helps chain apex strikes together.',
    verb: 'Lift',
    category: 'wing',
    icon: '⬆️',
    color: '#88DDFF',
    comboPotential: 'high',
    effect: { killSpeedBoost: 3, killSpeedDuration: 1 },
    juiceConfig: { visual: 'Brief upward lift animation', audio: 'rising_whoosh', particleType: 'lift_particles', triggerText: 'UPDRAFT!' },
  },
  {
    id: 'hover_pressure',
    name: 'Hover Pressure',
    description: 'Being near enemies (50px) deals 1 DPS. Softens targets before apex strike.',
    verb: 'Press',
    category: 'wing',
    icon: '💫',
    color: '#AADDFF',
    comboPotential: 'medium',
    effect: { pressureRadius: 50, pressureDps: 1 },
    juiceConfig: { visual: 'Subtle pressure wave ripples around player', audio: 'bass_pulse', particleType: 'pressure_waves' },
  },
];

// =============================================================================
// PREDATOR ABILITIES (6) - Kill triggers that stack damage
// APEX STRIKE SYNERGY: All bonuses STACK with apex strike damage multiplicatively
// =============================================================================

const PREDATOR_ABILITIES: Ability[] = [
  {
    id: 'feeding_efficiency',
    name: 'Feeding Efficiency',
    description: 'Kills give +2% attack speed for 3s (stacks 5x). More kills = faster apex charges.',
    verb: 'Feed',
    category: 'predator',
    icon: '⚡',
    color: '#FFCC00',
    comboPotential: 'high',
    effect: { feedingSpeedBonus: 2, feedingDuration: 3, feedingMaxStacks: 5 },
    juiceConfig: { visual: 'Speed lines on kill, stack counter 1-5', audio: 'tempo_increase', particleType: 'speed_lines', triggerText: 'FEED!' },
  },
  {
    id: 'territorial_mark',
    name: 'Territorial Mark',
    description: 'Where enemies die, you deal +10% damage for 2s. Kill zones boost apex damage.',
    verb: 'Mark',
    category: 'predator',
    icon: '🎯',
    color: '#AA4400',
    comboPotential: 'high',
    effect: { markRadius: 30, markDuration: 2, markDamageBonus: 10 },
    juiceConfig: { visual: 'Dark orange ground stain at kill', audio: 'territorial_splat', particleType: 'ground_mark', triggerText: 'MARKED!' },
  },
  {
    id: 'trophy_scent',
    name: 'Trophy Scent',
    description: 'Each unique enemy type killed = +1% PERMANENT damage. Rewards exploration.',
    verb: 'Track',
    category: 'predator',
    icon: '🏆',
    color: '#FFD700',
    comboPotential: 'high',
    effect: { trophyDamageBonus: 1 },
    juiceConfig: { visual: 'Golden trophy flash on new type', audio: 'trophy_chime', particleType: 'trophy_sparkle', triggerText: 'TROPHY!' },
  },
  {
    id: 'pack_signal',
    name: 'Pack Signal',
    description: 'Kills cause nearby enemies (60px) to hesitate 0.1s. Follow-up windows.',
    verb: 'Signal',
    category: 'predator',
    icon: '📢',
    color: '#884400',
    comboPotential: 'medium',
    effect: { signalRadius: 60, signalDuration: 0.1 },
    juiceConfig: { visual: 'Fear ripple from kill, enemies freeze briefly', audio: 'fear_pulse', particleType: 'fear_ripple' },
  },
  {
    id: 'corpse_heat',
    name: 'Corpse Heat',
    description: 'Standing on recent kills (20px) grants +5% damage for 1s. Aggressive positioning.',
    verb: 'Consume',
    category: 'predator',
    icon: '🔥',
    color: '#FF4400',
    comboPotential: 'medium',
    effect: { predatorCorpseHeatRadius: 20, predatorCorpseHeatBonus: 5, predatorCorpseHeatDuration: 1 },
    juiceConfig: { visual: 'Heat wisps rise from corpses', audio: 'heat_absorption', particleType: 'heat_wisps', triggerText: 'HEAT!' },
  },
  {
    id: 'clean_kill',
    name: 'Clean Kill',
    description: 'Enemies killed in one hit explode (10px, 5 dmg). Chains with apex crits.',
    verb: 'Execute',
    category: 'predator',
    icon: '💥',
    color: '#FF0044',
    comboPotential: 'high',
    effect: { cleanKillRadius: 10, cleanKillDamage: 5 },
    juiceConfig: { visual: 'Mini pop explosion on one-hit kill', audio: 'clean_pop', particleType: 'mini_explosion', triggerText: 'CLEAN!' },
  },
];

// =============================================================================
// PHEROMONE Abilities - Area Denial & Enemy Debuffs
//
// DESIGN: Pheromones control space and weaken enemies. They don't boost YOUR
// damage directly, but make ENEMIES weaker or slower. Best for kiting builds.
//
// APEX STRIKE SYNERGY:
// - threat_aura: Reduces contact damage during dash-through (passive defense)
// - confusion_cloud: Creates safe zones after taking hits (escape tool)
// - rally_scent: Slows enemies in your wake (kiting during recovery)
// - death_marker: Apex kills create slow zones (chain kill setup)
// - aggro_pulse: Gathers enemies for multi-hit dashes (combo setup)
// - bitter_taste: Attacker debuff stacks with threat_aura (layered defense)
//
// STACKING: Most pheromone effects stack additively with each other.
// threat_aura (5%) + bitter_taste (10%) = 15% total damage reduction.
// =============================================================================

const PHEROMONE_ABILITIES: Ability[] = [
  {
    id: 'threat_aura',
    name: 'Threat Aura',
    description: 'Enemies within 30px deal 5% less damage to you.',
    verb: 'Intimidate',
    category: 'pheromone',
    icon: '🟠',
    color: '#FF9900',
    comboPotential: 'medium',
    effect: {
      threatAuraRadius: 30,
      threatAuraDamageReduction: 5,
    },
    juiceConfig: {
      visual: 'Orange pulse ring at 30px, brightens when reducing damage',
      audio: 'threat_hum',
      particleType: 'threat_motes',
      triggerText: 'THREAT!',
    },
  },
  {
    id: 'confusion_cloud',
    name: 'Confusion Cloud',
    description: 'Taking damage releases a cloud. Enemies inside have 10% miss chance.',
    verb: 'Confuse',
    category: 'pheromone',
    icon: '☁️',
    color: '#9966FF',
    comboPotential: 'medium',
    effect: {
      confusionCloudRadius: 40,
      confusionCloudMissChance: 10,
      confusionCloudDuration: 2,
    },
    juiceConfig: {
      visual: 'Purple-orange swirling mist, enemies show ? marks',
      audio: 'cloud_hiss',
      particleType: 'confusion_swirl',
      triggerText: 'CONFUSION!',
    },
  },
  {
    id: 'rally_scent',
    name: 'Rally Scent',
    description: 'Your movement path slows enemies inside by 5% for 2s.',
    verb: 'Mark',
    category: 'pheromone',
    icon: '👣',
    color: '#FFAA33',
    comboPotential: 'medium',
    effect: {
      rallyScentTrailDuration: 2,
      rallyScentSlowPercent: 5,
    },
    juiceConfig: {
      visual: 'Fading amber trail line, pulses when slowing enemies',
      audio: 'trail_sizzle',
      particleType: 'scent_trail',
      triggerText: 'TRAIL!',
    },
  },
  {
    id: 'death_marker',
    name: 'Death Marker',
    description: 'Kills create a slow zone (15px, 3s). Enemies slowed 10%.',
    verb: 'Mark',
    category: 'pheromone',
    icon: '💀',
    color: '#332244',
    comboPotential: 'high',
    effect: {
      deathMarkerRadius: 15,
      deathMarkerSlowPercent: 10,
      deathMarkerDuration: 3,
    },
    juiceConfig: {
      visual: 'Dark seeping circle at corpse, pulses on slow',
      audio: 'death_ooze',
      particleType: 'death_seep',
      triggerText: 'MARKED!',
    },
  },
  {
    id: 'aggro_pulse',
    name: 'Aggro Pulse',
    description: 'Every 10s: pulse forces enemies (100px) to target you for 1s.',
    verb: 'Command',
    category: 'pheromone',
    icon: '📣',
    color: '#FFD700',
    comboPotential: 'high',
    effect: {
      aggroPulseCooldown: 10,
      aggroPulseRadius: 100,
      aggroPulseDuration: 1,
    },
    juiceConfig: {
      visual: 'Golden expanding ring, affected enemies show ! marks',
      audio: 'command_horn',
      particleType: 'command_ring',
      triggerText: 'COME!',
    },
  },
  {
    id: 'bitter_taste',
    name: 'Bitter Taste',
    description: 'Enemies that hit you deal 10% less damage for 2s.',
    verb: 'Deter',
    category: 'pheromone',
    icon: '😖',
    color: '#88CC44',
    comboPotential: 'medium',
    effect: {
      bitterTasteDamageReduction: 10,
      bitterTasteDuration: 2,
    },
    juiceConfig: {
      visual: 'Enemy shows green sick tint, damage numbers show debuff',
      audio: 'bitter_grunt',
      particleType: 'bitter_spray',
      triggerText: 'BITTER!',
    },
  },
];

// =============================================================================
// CHITIN Abilities - Body Modifications (Survival & Utility)
//
// DESIGN: Chitin abilities modify your body for survival and utility. They
// provide passive defenses, emergency abilities, and enhanced awareness.
//
// APEX STRIKE SYNERGY:
// - barbed_chitin: Contact damage rewards aggressive dash-through
// - ablative_shell: First hit protection gives confidence to commit
// - heat_retention: Speed bonus at low HP enables clutch escapes/dashes
// - compound_eyes: Better telegraph vision helps plan strike angles
// - antenna_sensitivity: Early warning helps position for dashes
// - molting_burst: Emergency panic button during failed dashes
//
// STACKING: Chitin abilities mostly don't stack with themselves.
// They provide unique one-time effects or threshold-based bonuses.
// =============================================================================

const CHITIN_ABILITIES: Ability[] = [
  {
    id: 'barbed_chitin',
    name: 'Barbed Chitin',
    description: 'Enemies touching you take 3 damage per second.',
    verb: 'Spike',
    category: 'chitin',
    icon: '🦔',
    color: '#8B4513',
    comboPotential: 'medium',
    effect: {
      barbedChitinDamage: 3,
      barbedChitinRadius: 25,
    },
    juiceConfig: {
      visual: 'Small spike sprites around player, red flash on contact damage',
      audio: 'spike_plink',
      particleType: 'spike_burst',
      triggerText: 'BARBED!',
    },
  },
  {
    id: 'ablative_shell',
    name: 'Ablative Shell',
    description: 'First hit each wave deals 20% less damage.',
    verb: 'Shield',
    category: 'chitin',
    icon: '🛡️',
    color: '#C0C0C0',
    comboPotential: 'low',
    effect: {
      ablativeShellReduction: 20,
    },
    juiceConfig: {
      visual: 'Silver shell layer visible, shatters on first hit',
      audio: 'shell_crack',
      particleType: 'shell_shards',
      triggerText: 'ABLATIVE!',
    },
  },
  {
    id: 'heat_retention',
    name: 'Heat Retention',
    description: '+5% speed when below 50% HP.',
    verb: 'Heat',
    category: 'chitin',
    icon: '🔥',
    color: '#FF4400',
    comboPotential: 'medium',
    effect: {
      heatRetentionThreshold: 0.5,
      heatRetentionSpeedBonus: 5,
    },
    juiceConfig: {
      visual: 'Red-orange heat shimmer around player when active',
      audio: 'heat_pulse',
      particleType: 'heat_waves',
      triggerText: 'HEATED!',
    },
  },
  {
    id: 'compound_eyes',
    name: 'Compound Eyes',
    description: 'See enemy attack telegraphs 0.1s earlier.',
    verb: 'See',
    category: 'chitin',
    icon: '👁️',
    color: '#00FFFF',
    comboPotential: 'medium',
    effect: {
      compoundEyesTelegraphMs: 100,
    },
    juiceConfig: {
      visual: 'Attack telegraphs appear slightly earlier with cyan tint',
      audio: 'vision_ping',
      particleType: 'vision_pulse',
      triggerText: 'SEEN!',
    },
  },
  {
    id: 'antenna_sensitivity',
    name: 'Antenna Sensitivity',
    description: 'Enemies highlighted 0.5s before entering screen.',
    verb: 'Sense',
    category: 'chitin',
    icon: '📡',
    color: '#FFFF00',
    comboPotential: 'low',
    effect: {
      antennaSensitivityMs: 500,
    },
    juiceConfig: {
      visual: 'Yellow edge glow warning arrows pointing to incoming enemies',
      audio: 'sense_beep',
      particleType: 'warning_arrows',
      triggerText: 'INCOMING!',
    },
  },
  {
    id: 'molting_burst',
    name: 'Molting Burst',
    description: 'At 10% HP (once per run): 0.5s invuln + 20 damage burst.',
    verb: 'Molt',
    category: 'chitin',
    icon: '🦎',
    color: '#FF00FF',
    comboPotential: 'high',
    isRiskReward: true,
    effect: {
      moltingBurstThreshold: 0.1,
      moltingBurstInvulnMs: 500,
      moltingBurstDamage: 20,
      moltingBurstRadius: 50,
    },
    juiceConfig: {
      visual: 'Shell explodes outward, player briefly glows white invuln',
      audio: 'molt_explosion',
      particleType: 'molt_shards',
      triggerText: 'MOLT!',
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
  ...WING_ABILITIES,
  ...PREDATOR_ABILITIES,
  ...PHEROMONE_ABILITIES,
  ...CHITIN_ABILITIES,
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
 * Create default runtime state
 */
function createDefaultRuntime(): AbilityRuntime {
  return {
    // WING runtime
    updraftExpiry: 0,
    updraftSpeedBonus: 0,

    // CHITIN runtime
    heatRetentionActive: false,
    ablativeShellUsed: false,
    moltingBurstUsed: false,

    // PREDATOR runtime
    sawtoothCounter: 0,
    trophyScentKills: 0,

    // PHEROMONE runtime
    confusionClouds: [],
    bitterTasteDebuffs: new Map(),
    aggroPulseLastTime: 0,
    deathMarkers: [],
  };
}

export function createInitialAbilities(): ActiveAbilities {
  return {
    owned: [],
    levels: {} as Record<AbilityId, number>,
    computed: createDefaultComputed(),
    runtime: createDefaultRuntime(),
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

    // Advanced ability effects (stubs)
    heatRetentionSpeedBonus: 0,
    scatterDustEnabled: false,
    corpseHeatRadius: 0,
    corpseHeatBonus: 0,
    sawtoothEveryN: 0,
    sawtoothBonus: 0,
    poisonedDamageAmp: 0,
    histamineDamageAmp: 0,
    slowPerHit: 0,
    slowMaxStacks: 0,
    freezeChance: 0,
    armorReductionPerHit: 0,
    knockbackPx: 0,
    stunChance: 0,
    stunDuration: 0,
    markFullHpTargets: false,
    bleedDuration: 0,
    bleedPercent: 0,

    // WING ability computed effects
    draftEnabled: false,
    draftPullStrength: 0,
    draftPullRadius: 0,
    buzzFieldEnabled: false,
    buzzFieldDelay: 0,
    buzzFieldRadius: 0,
    buzzFieldDps: 0,
    thermalWakeEnabled: false,
    thermalWakeDuration: 0,
    thermalWakeSlow: 0,
    scatterDustDuration: 0,
    scatterDustRadius: 0,
    updraftEnabled: false,
    updraftSpeedBoost: 0,
    updraftDuration: 0,
    hoverPressureEnabled: false,
    hoverPressureRadius: 0,
    hoverPressureDps: 0,

    // PREDATOR ability computed effects
    feedingEfficiencyEnabled: false,
    feedingEfficiencyBonus: 0,
    feedingEfficiencyDuration: 0,
    feedingEfficiencyMaxStacks: 0,
    territorialMarkEnabled: false,
    territorialMarkRadius: 0,
    territorialMarkDuration: 0,
    territorialMarkBonus: 0,
    trophyScentEnabled: false,
    trophyScentBonus: 0,
    packSignalEnabled: false,
    packSignalRadius: 0,
    packSignalDuration: 0,
    predatorCorpseHeatEnabled: false,
    predatorCorpseHeatRadius: 0,
    predatorCorpseHeatBonus: 0,
    predatorCorpseHeatDuration: 0,
    cleanKillEnabled: false,
    cleanKillRadius: 0,
    cleanKillDamage: 0,
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
    runtime: abilities.runtime,  // Preserve runtime state
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

    // WING ability effects - Movement creates effects
    if (effect.pullStrength !== undefined) {
      computed.draftEnabled = true;
      computed.draftPullStrength = effect.pullStrength;
      computed.draftPullRadius = effect.pullRadius ?? 40;
    }
    if (effect.stationaryDps !== undefined) {
      computed.buzzFieldEnabled = true;
      computed.buzzFieldDelay = effect.stationaryDelay ?? 0.5;
      computed.buzzFieldRadius = effect.stationaryRadius ?? 20;
      computed.buzzFieldDps = effect.stationaryDps;
    }
    if (effect.trailSlowPercent !== undefined) {
      computed.thermalWakeEnabled = true;
      computed.thermalWakeDuration = effect.trailDuration ?? 2;
      computed.thermalWakeSlow = effect.trailSlowPercent;
    }
    if (effect.dustDuration !== undefined) {
      computed.scatterDustEnabled = true;
      computed.scatterDustDuration = effect.dustDuration;
      computed.scatterDustRadius = effect.dustRadius ?? 30;
    }
    if (effect.killSpeedBoost !== undefined) {
      computed.updraftEnabled = true;
      computed.updraftSpeedBoost = effect.killSpeedBoost;
      computed.updraftDuration = effect.killSpeedDuration ?? 1;
    }
    if (effect.pressureDps !== undefined) {
      computed.hoverPressureEnabled = true;
      computed.hoverPressureRadius = effect.pressureRadius ?? 50;
      computed.hoverPressureDps = effect.pressureDps;
    }

    // PREDATOR ability effects - Kill triggers that stack damage
    if (effect.feedingSpeedBonus !== undefined) {
      computed.feedingEfficiencyEnabled = true;
      computed.feedingEfficiencyBonus = effect.feedingSpeedBonus;
      computed.feedingEfficiencyDuration = effect.feedingDuration ?? 3;
      computed.feedingEfficiencyMaxStacks = effect.feedingMaxStacks ?? 5;
    }
    if (effect.markDamageBonus !== undefined) {
      computed.territorialMarkEnabled = true;
      computed.territorialMarkRadius = effect.markRadius ?? 30;
      computed.territorialMarkDuration = effect.markDuration ?? 2;
      computed.territorialMarkBonus = effect.markDamageBonus;
    }
    if (effect.trophyDamageBonus !== undefined) {
      computed.trophyScentEnabled = true;
      computed.trophyScentBonus = effect.trophyDamageBonus;
    }
    if (effect.signalDuration !== undefined) {
      computed.packSignalEnabled = true;
      computed.packSignalRadius = effect.signalRadius ?? 60;
      computed.packSignalDuration = effect.signalDuration;
    }
    if (effect.predatorCorpseHeatBonus !== undefined) {
      computed.predatorCorpseHeatEnabled = true;
      computed.predatorCorpseHeatRadius = effect.predatorCorpseHeatRadius ?? 20;
      computed.predatorCorpseHeatBonus = effect.predatorCorpseHeatBonus;
      computed.predatorCorpseHeatDuration = effect.predatorCorpseHeatDuration ?? 1;
    }
    if (effect.cleanKillDamage !== undefined) {
      computed.cleanKillEnabled = true;
      computed.cleanKillRadius = effect.cleanKillRadius ?? 10;
      computed.cleanKillDamage = effect.cleanKillDamage;
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

/**
 * Get computed effects from an ActiveAbilities object.
 * This is the primary way to access aggregated ability effects.
 *
 * @param abilities - The player's active abilities state
 * @returns The pre-computed aggregated effects
 */
export function computeAbilityEffects(abilities: ActiveAbilities): ComputedEffects {
  return abilities.computed;
}

// =============================================================================
// STUB EXPORTS: Advanced Ability System (Not Yet Implemented)
// These are placeholder exports for the advanced ability runtime system.
// The game loop imports these but they're not fully implemented yet.
// =============================================================================

import type { Vector2 } from '../types';

/**
 * Trail point for movement-based abilities
 */
export interface TrailPoint {
  x: number;
  y: number;
  timestamp: number;
}

/**
 * Aura processing result
 */
export interface AuraResult {
  damageDealt: number;
  enemiesAffected: string[];
  // Extended results used by useGameLoop
  enemyDamage: Map<string, number>;
  enemyDebuffs: Map<string, number>;
}

/**
 * Territorial mark zone
 */
export interface TerritorialMark {
  id: string;
  position: Vector2;
  radius: number;
  expiryTime: number;
}

/**
 * Death marker for corpse-based abilities
 */
export interface DeathMarker {
  id: string;
  position: Vector2;
  expiryTime: number;
}

// Stub functions - return no-op values

export function recordKillForTrophyScent(_abilities: ActiveAbilities, _enemyType?: string): ActiveAbilities {
  return _abilities;
}

/**
 * Increment sawtooth counter and check if bonus hit triggered
 * Returns object with updated state and bonus hit flag
 */
export function incrementSawtoothCounter(_abilities: ActiveAbilities): { state: ActiveAbilities; isBonusHit: boolean } {
  // Increment counter
  const newCounter = (_abilities.runtime.sawtoothCounter || 0) + 1;
  const sawtoothEveryN = _abilities.computed.sawtoothEveryN || 0;

  // Check if this hit triggers bonus
  const isBonusHit = sawtoothEveryN > 0 && newCounter >= sawtoothEveryN;

  return {
    state: {
      ..._abilities,
      runtime: {
        ..._abilities.runtime,
        sawtoothCounter: isBonusHit ? 0 : newCounter,
      },
    },
    isBonusHit,
  };
}

export function resetRuntimeForWave(_abilities: ActiveAbilities): ActiveAbilities {
  return _abilities;
}

/**
 * Process movement trail for thermal_wake, rally_scent, draft abilities
 * @param _abilities - Player's abilities state
 * @param _trail - Array of trail points with x, y, timestamp
 * @param _enemies - Array of enemy positions with id, x, y
 * @param _gameTime - Current game time
 * @param _trailDuration - How long trail points last
 */
export function processMovementTrail(
  _abilities: ActiveAbilities,
  _trail: TrailPoint[],
  _enemies: Array<{ id: string; x: number; y: number }>,
  _gameTime: number,
  _trailDuration?: number
): { abilities: ActiveAbilities; trail: TrailPoint[]; enemiesToSlow: Map<string, number>; enemiesToPull: Map<string, { x: number; y: number }> } {
  return {
    abilities: _abilities,
    trail: [],
    enemiesToSlow: new Map(),
    enemiesToPull: new Map(),
  };
}

/**
 * Process passive auras (hover_pressure, buzz_field, threat_aura)
 * @param _abilities - Player's abilities state
 * @param _playerPos - Player position
 * @param _playerVelocity - Player velocity
 * @param _enemies - Array of enemy positions
 * @param _deltaTime - Time since last update
 * @param _stationaryTime - Time player has been stationary
 */
export function processPassiveAuras(
  _abilities: ActiveAbilities,
  _playerPos: Vector2,
  _playerVelocity: Vector2,
  _enemies: Array<{ id: string; position: Vector2; x: number; y: number }>,
  _deltaTime: number,
  _stationaryTime?: number
): AuraResult {
  return {
    damageDealt: 0,
    enemiesAffected: [],
    enemyDamage: new Map(),
    enemyDebuffs: new Map(),
  };
}

/**
 * Process on-kill effects (territorial_mark, death_marker, pack_signal, etc.)
 * @param _abilities - Player's abilities state
 * @param _enemyPos - Killed enemy position
 * @param _cleanKillValue - Damage dealt (for clean kill detection)
 * @param _maxHealth - Enemy max health
 * @param _enemyType - Type of enemy killed
 * @param _enemies - All current enemies (for pack_signal hesitation)
 * @param _gameTime - Current game time
 */
export function processOnKill(
  _abilities: ActiveAbilities,
  _enemyPos: Vector2,
  _cleanKillValue: number,
  _maxHealth: number,
  _enemyType: string,
  _enemies: Array<{ id: string; x: number; y: number }>,
  _gameTime: number
): {
  abilities: ActiveAbilities;
  marks: TerritorialMark[];
  deathMarkers: DeathMarker[];
  updatedAbilities: ActiveAbilities;
  newTerritorialMarks: TerritorialMark[];
  newDeathMarkers: DeathMarker[];
  explosions: Array<{ x: number; y: number; radius: number; damage: number }>;
  hesitateEnemyIds: string[];
  speedBoostPercent: number;
} {
  return {
    abilities: _abilities,
    marks: [],
    deathMarkers: [],
    updatedAbilities: _abilities,
    newTerritorialMarks: [],
    newDeathMarkers: [],
    explosions: [],
    hesitateEnemyIds: [],
    speedBoostPercent: 0,
  };
}

/**
 * Expire old zones (territorial marks and death markers)
 */
export function expireZones(
  _marks: TerritorialMark[],
  _deathMarkers: DeathMarker[],
  _gameTime: number
): { marks: TerritorialMark[]; deathMarkers: DeathMarker[]; territorialMarks: TerritorialMark[] } {
  return { marks: _marks, deathMarkers: _deathMarkers, territorialMarks: _marks };
}

/**
 * Get slow percent from death markers at enemy position
 * @param _x - Enemy X position
 * @param _y - Enemy Y position
 * @param _deathMarkers - Active death markers
 * @param _gameTime - Current game time
 */
export function getDeathMarkerSlow(
  _x: number,
  _y: number,
  _deathMarkers: DeathMarker[],
  _gameTime: number
): number {
  return 0;
}

/**
 * Get territorial mark damage bonus at player position
 * @param _x - Player X position
 * @param _y - Player Y position
 * @param _marks - Active territorial marks
 * @param _gameTime - Current game time
 */
export function getTerritorialMarkBonus(
  _x: number,
  _y: number,
  _marks: TerritorialMark[],
  _gameTime: number
): number {
  return 0;
}

/**
 * Check if player is near a corpse (death marker)
 * @param _x - Player X position
 * @param _y - Player Y position
 * @param _deathMarkers - Active death markers
 * @param _gameTime - Current game time
 * @param _radius - Proximity radius to check
 */
export function isNearCorpse(
  _x: number,
  _y: number,
  _deathMarkers: DeathMarker[],
  _gameTime: number,
  _radius: number
): boolean {
  return false;
}

/**
 * Process on-damaged abilities (ablative_shell, confusion_cloud counter, bitter_taste)
 * @param _abilities - Player's abilities state
 * @param _playerPos - Player position
 * @param _attackerId - ID of attacking enemy (or null)
 * @param _damage - Incoming damage amount
 * @param _gameTime - Current game time
 * @param _wave - Current wave number
 */
export function processOnDamaged(
  _abilities: ActiveAbilities,
  _playerPos: Vector2,
  _attackerId: string | null,
  _damage: number,
  _gameTime: number,
  _wave: number
): {
  damageReduction: number;
  updatedAbilities: ActiveAbilities;
  newConfusionClouds: Array<{ x: number; y: number; radius: number }>;
  bitterTasteTargets: string[];
} {
  return {
    damageReduction: 1, // No reduction
    updatedAbilities: _abilities,
    newConfusionClouds: [],
    bitterTasteTargets: [],
  };
}

/**
 * Process threshold abilities (heat_retention, molting_burst)
 * @param _abilities - Player's abilities state
 * @param _currentHp - Current player HP
 * @param _maxHp - Max player HP
 * @param _gameTime - Current game time
 */
export function processThresholds(
  _abilities: ActiveAbilities,
  _currentHp: number,
  _maxHp: number,
  _gameTime: number
): {
  updatedAbilities: ActiveAbilities;
  moltingBurstTriggered: boolean;
  moltingBurstRadius: number;
  moltingBurstDamage: number;
  moltingBurstInvulnMs: number;
} {
  return {
    updatedAbilities: _abilities,
    moltingBurstTriggered: false,
    moltingBurstRadius: 0,
    moltingBurstDamage: 0,
    moltingBurstInvulnMs: 0,
  };
}

/**
 * Process periodic abilities (aggro_pulse)
 * @param _abilities - Player's abilities state
 * @param _playerPos - Player position
 * @param _enemies - All enemies on field
 * @param _gameTime - Current game time
 */
export function processPeriodicEffects(
  _abilities: ActiveAbilities,
  _playerPos: Vector2,
  _enemies: Array<{ id: string; position: Vector2 }>,
  _gameTime: number
): {
  updatedAbilities: ActiveAbilities;
  aggroPulseTriggered: boolean;
  aggroEnemyIds: string[];
  aggroDurationMs: number;
} {
  return {
    updatedAbilities: _abilities,
    aggroPulseTriggered: false,
    aggroEnemyIds: [],
    aggroDurationMs: 0,
  };
}

/**
 * Check if enemy attack misses due to confusion cloud
 * @param _attackerPos - Position of attacking enemy
 * @param _abilities - Player's abilities state
 * @param _gameTime - Current game time
 */
export function checkConfusionCloudMiss(
  _attackerPos: Vector2,
  _abilities: ActiveAbilities,
  _gameTime: number
): boolean {
  return false;
}

export function cleanupExpiredEffects(
  _abilities: ActiveAbilities,
  _gameTime: number
): ActiveAbilities {
  return _abilities;
}

/**
 * Get bitter taste damage reduction for an attacker
 * @param _attackerId - ID of attacking enemy
 * @param _abilities - Player's abilities state
 * @param _gameTime - Current game time
 */
export function getBitterTasteDebuff(
  _attackerId: string,
  _abilities: ActiveAbilities,
  _gameTime: number
): number {
  return 1; // No reduction (1 = full damage)
}

/**
 * Get threat aura damage reduction for an attack
 * @param _attackerPos - Position of attacking enemy
 * @param _playerPos - Player position
 * @param _abilities - Player's abilities state
 */
export function getThreatAuraReduction(
  _attackerPos: Vector2,
  _playerPos: Vector2,
  _abilities: ActiveAbilities
): number {
  return 1; // No reduction (1 = full damage)
}
