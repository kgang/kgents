/**
 * WASM Survivors - ENHANCED PERKS SYSTEM
 *
 * "If I have the right combo of perks and skill, I'll really pop off"
 *
 * DESIGN PRINCIPLE: Every perk must be:
 * 1. IMPACTFUL on its own - you feel the difference immediately
 * 2. VISUALLY DISTINCT - you can SEE the perk is active
 * 3. SYNERGY-READY - combines with other perks for INSANE moments
 * 4. SKILL-REWARDING - better players get more out of it
 *
 * Players typically get 4-5 perks before dying.
 * EVERY perk must matter. EVERY combo must be tempting.
 *
 * @see pilots/wasm-survivors-game/systems/insane-combos.ts
 */

import type { AbilityId } from './abilities';
import type { ComboTier } from './insane-combos';

// =============================================================================
// Types
// =============================================================================

/**
 * Enhanced perk with full combo integration
 */
export interface EnhancedPerk {
  id: AbilityId;
  name: string;
  /** One-line description visible in UI */
  description: string;
  /** Hidden depth - what players discover */
  hiddenDepth: string;

  // === CORE MECHANICS ===
  /** Primary effect values */
  effect: EnhancedPerkEffect;
  /** Passive effect that's always active */
  passiveEffect?: PassiveEffect;
  /** On-kill trigger effect */
  onKillEffect?: OnKillEffect;
  /** On-hit trigger effect */
  onHitEffect?: OnHitEffect;
  /** Conditional effect (e.g., when low HP) */
  conditionalEffect?: ConditionalEffect;

  // === VISUAL IDENTITY ===
  /** Color for the perk's visual effects */
  color: string;
  /** Secondary color for gradients/accents */
  colorSecondary?: string;
  /** Icon/symbol for the perk */
  icon: string;
  /** Particle system to use */
  particleSystem: ParticleSystemType;
  /** Screen effect when perk triggers */
  screenEffect?: ScreenEffectType;
  /** Trigger text shown on activation */
  triggerText: string;

  // === COMBO POTENTIAL ===
  /** Synergies with other perks (unlocks special effects) */
  synergizesWith: AbilityId[];
  /** What this perk does when synergized */
  synergyBonus: string;
  /** Combo tier this perk enables */
  comboTier: ComboTier;
  /** Does this perk scale with skill? */
  skillScaling: SkillScalingType;

  // === APEX STRIKE INTEGRATION ===
  /** How this perk affects apex strike */
  apexIntegration?: ApexIntegration;
}

/**
 * Enhanced perk effect values
 */
export interface EnhancedPerkEffect {
  // Damage
  damagePercent?: number;
  flatDamage?: number;
  critChance?: number;
  critMultiplier?: number;
  executeThreshold?: number;
  poisonDps?: number;
  bleedDps?: number;

  // Speed
  moveSpeedPercent?: number;
  attackSpeedPercent?: number;
  apexCooldownReduction?: number;

  // Defense
  maxHpBonus?: number;
  damageReduction?: number;
  hpRegenPerSecond?: number;
  lifestealPercent?: number;
  shieldAmount?: number;

  // Special
  chainRange?: number;
  bounceStrength?: number;
  grazeWindow?: number;
  momentumGain?: number;
}

/**
 * Passive effect - always active
 */
export interface PassiveEffect {
  type: 'aura' | 'trail' | 'proximity' | 'constant';
  radius?: number;
  damagePerSecond?: number;
  slowPercent?: number;
  pullStrength?: number;
  description: string;
}

/**
 * On-kill effect - triggers on enemy death
 */
export interface OnKillEffect {
  type: 'explosion' | 'chain' | 'heal' | 'speed_burst' | 'damage_stack';
  radius?: number;
  damage?: number;
  healPercent?: number;
  speedBonus?: number;
  duration?: number;
  stackable?: boolean;
  maxStacks?: number;
  description: string;
}

/**
 * On-hit effect - triggers when dealing damage
 */
export interface OnHitEffect {
  type: 'poison' | 'bleed' | 'slow' | 'mark' | 'weaken' | 'double_hit';
  chance?: number;
  duration?: number;
  stacks?: number;
  description: string;
}

/**
 * Conditional effect - active under certain conditions
 */
export interface ConditionalEffect {
  condition: 'low_hp' | 'high_combo' | 'near_enemies' | 'graze_streak' | 'bouncing';
  threshold?: number;
  effect: Partial<EnhancedPerkEffect>;
  description: string;
}

/**
 * Particle system types
 */
export type ParticleSystemType =
  | 'slash_marks'
  | 'impact_burst'
  | 'poison_drip'
  | 'twin_slash'
  | 'fire_burst'
  | 'sniper_lock'
  | 'lightning_spark'
  | 'speed_blur'
  | 'wing_trail'
  | 'hunt_lines'
  | 'berserker_aura'
  | 'time_ripple'
  | 'armor_plate'
  | 'shield_shimmer'
  | 'heal_sparkle'
  | 'blood_orb'
  | 'rage_aura'
  | 'golden_burst'
  | 'crit_burst'
  | 'death_slash'
  | 'full_circle'
  | 'lightning_arc'
  | 'momentum_aura'
  | 'crystal_shards'
  | 'graze_spark'
  | 'heat_pulse'
  | 'chain_link'
  | 'venom_explosion'
  | 'wind_lines'
  | 'vibration_rings'
  | 'heat_shimmer'
  | 'dust_particles'
  | 'lift_particles'
  | 'pressure_pulse'
  | 'feeding_glow'
  | 'mark_zone'
  | 'trophy_gleam'
  | 'hesitation_wave'
  | 'corpse_glow'
  | 'explosion_mini'
  | 'threat_pulse'
  | 'confusion_swirl'
  | 'pheromone_trail'
  | 'death_zone'
  | 'aggro_ring'
  | 'bitter_flash'
  | 'chitin_spike'
  | 'ablative_flash'
  | 'heat_aura'
  | 'compound_highlight'
  | 'antenna_ping'
  | 'molting_burst';

/**
 * Screen effect types
 */
export type ScreenEffectType =
  | 'flash'
  | 'pulse'
  | 'shake'
  | 'vignette'
  | 'chromatic'
  | 'slow_mo'
  | 'freeze_frame';

/**
 * Skill scaling types
 */
export type SkillScalingType =
  | 'none'           // Same for all players
  | 'moderate'       // Better players get ~50% more
  | 'high'           // Better players get ~100% more
  | 'extreme';       // Skill ceiling is INSANE

/**
 * Apex strike integration
 */
export interface ApexIntegration {
  /** Bonus during apex charge */
  duringCharge?: Partial<EnhancedPerkEffect>;
  /** Bonus during apex strike */
  duringStrike?: Partial<EnhancedPerkEffect>;
  /** Bonus on apex hit */
  onApexHit?: Partial<OnKillEffect>;
  /** Bonus on apex kill */
  onApexKill?: Partial<OnKillEffect>;
  /** Description */
  description: string;
}

// =============================================================================
// ENHANCED PERK POOL - Every perk audited and enhanced
// =============================================================================

export const ENHANCED_PERKS: EnhancedPerk[] = [
  // =========================================================================
  // DAMAGE PERKS - Make each attack matter more
  // =========================================================================
  {
    id: 'sharpened_mandibles',
    name: 'Sharpened Mandibles',
    description: '+40% damage. Crits deal +20% more.',
    hiddenDepth: 'Stacks 3x. At max stacks, attacks leave bleeding wounds.',
    effect: { damagePercent: 40, critMultiplier: 0.2 },
    onHitEffect: {
      type: 'bleed',
      chance: 100, // At max stacks
      duration: 3000,
      description: 'Max stacks cause bleeding',
    },
    color: '#FF6600',
    colorSecondary: '#CC3300',
    icon: '🦷',
    particleSystem: 'slash_marks',
    screenEffect: 'flash',
    triggerText: 'SHARP!',
    synergizesWith: ['crushing_bite', 'critical_sting', 'savage_blow'],
    synergyBonus: 'Attacks have 15% chance to strike TWICE at full damage',
    comboTier: 'advanced',
    skillScaling: 'moderate',
    apexIntegration: {
      duringStrike: { damagePercent: 20 },
      description: 'Apex strikes deal +20% damage',
    },
  },
  {
    id: 'crushing_bite',
    name: 'Crushing Bite',
    description: '+75% damage. Kills cause small explosion.',
    hiddenDepth: 'Explosion damage scales with overkill damage.',
    effect: { damagePercent: 75 },
    onKillEffect: {
      type: 'explosion',
      radius: 40,
      damage: 15,
      description: 'Kills explode for 15 + overkill damage',
    },
    color: '#CC3300',
    colorSecondary: '#990000',
    icon: '💪',
    particleSystem: 'impact_burst',
    screenEffect: 'shake',
    triggerText: 'CRUSH!',
    synergizesWith: ['sharpened_mandibles', 'execution', 'chain_lightning'],
    synergyBonus: 'Explosions chain to nearby enemies',
    comboTier: 'advanced',
    skillScaling: 'moderate',
    apexIntegration: {
      onApexKill: { type: 'explosion', radius: 60, damage: 25, description: 'Apex kills explode bigger' },
      description: 'Apex kills create larger explosions',
    },
  },
  {
    id: 'venomous_strike',
    name: 'Venomous Strike',
    description: '+12 poison DPS for 3s. Stacks infinitely.',
    hiddenDepth: 'Poisoned enemies take +15% damage from all sources.',
    effect: { poisonDps: 12 },
    onHitEffect: {
      type: 'poison',
      stacks: 1,
      duration: 3000,
      description: 'Applies stacking poison',
    },
    passiveEffect: {
      type: 'constant',
      description: 'Poisoned enemies take +15% damage',
    },
    color: '#88FF00',
    colorSecondary: '#44AA00',
    icon: '☠️',
    particleSystem: 'poison_drip',
    triggerText: 'POISON!',
    synergizesWith: ['chain_lightning', 'sweeping_arc', 'venom_architect'],
    synergyBonus: 'Poison spreads on enemy death',
    comboTier: 'advanced',
    skillScaling: 'moderate',
    apexIntegration: {
      duringStrike: { poisonDps: 24 },
      description: 'Apex strikes apply double poison',
    },
  },
  {
    id: 'double_strike',
    name: 'Double Strike',
    description: '40% chance to hit twice. Second hit is 80% damage.',
    hiddenDepth: 'Both hits can trigger on-hit effects independently.',
    effect: { damagePercent: 0 }, // Handled by on-hit
    onHitEffect: {
      type: 'double_hit',
      chance: 40,
      description: '40% chance for second hit at 80% damage',
    },
    color: '#FF4488',
    colorSecondary: '#CC2266',
    icon: '⚔️',
    particleSystem: 'twin_slash',
    screenEffect: 'flash',
    triggerText: 'DOUBLE!',
    synergizesWith: ['critical_sting', 'venomous_strike', 'lifesteal'],
    synergyBonus: 'Second hit always crits if first hit crits',
    comboTier: 'legendary',
    skillScaling: 'moderate',
    apexIntegration: {
      onApexHit: { type: 'damage_stack', damage: 10, stackable: true, maxStacks: 5, description: 'Apex double hits stack damage' },
      description: 'Apex double hits grant stacking damage',
    },
  },
  {
    id: 'savage_blow',
    name: 'Savage Blow',
    description: '+150% damage to enemies below 50% HP.',
    hiddenDepth: 'Killing low-HP enemies grants 2s of +25% attack speed.',
    effect: { damagePercent: 0 }, // Conditional
    conditionalEffect: {
      condition: 'low_hp',
      threshold: 50,
      effect: { damagePercent: 150 },
      description: '+150% damage to low HP enemies',
    },
    onKillEffect: {
      type: 'speed_burst',
      speedBonus: 25,
      duration: 2000,
      description: 'Low-HP kills grant attack speed',
    },
    color: '#FF0000',
    colorSecondary: '#AA0000',
    icon: '🔥',
    particleSystem: 'fire_burst',
    screenEffect: 'shake',
    triggerText: 'SAVAGE!',
    synergizesWith: ['execution', 'chain_lightning', 'frenzy'],
    synergyBonus: 'Speed boost stacks up to 3x',
    comboTier: 'advanced',
    skillScaling: 'high',
    apexIntegration: {
      duringStrike: { damagePercent: 50 },
      description: 'Apex always gets +50% to low HP enemies',
    },
  },
  {
    id: 'giant_killer',
    name: 'Giant Killer',
    description: '+300% damage to enemies above 75% HP.',
    hiddenDepth: 'First hit on full-HP enemies is always a crit.',
    effect: { damagePercent: 0 }, // Conditional
    conditionalEffect: {
      condition: 'low_hp', // Actually checks enemy high HP
      threshold: 75,
      effect: { damagePercent: 300, critChance: 100 },
      description: '+300% and guaranteed crit on high HP enemies',
    },
    color: '#00AAFF',
    colorSecondary: '#0066CC',
    icon: '🎯',
    particleSystem: 'sniper_lock',
    screenEffect: 'freeze_frame',
    triggerText: 'GIANT SLAYER!',
    synergizesWith: ['critical_sting', 'execution', 'momentum'],
    synergyBonus: 'Overkill damage chains to next target',
    comboTier: 'legendary',
    skillScaling: 'high',
    apexIntegration: {
      onApexHit: { type: 'chain', radius: 100, damage: 50, description: 'First apex hit chains damage' },
      description: 'First apex hit of a fight deals massive bonus damage',
    },
  },

  // =========================================================================
  // SPEED PERKS - Make you feel FAST
  // =========================================================================
  {
    id: 'quick_strikes',
    name: 'Quick Strikes',
    description: '+50% attack speed. +10% more per graze.',
    hiddenDepth: 'At 5 graze stacks, attacks become instant.',
    effect: { attackSpeedPercent: 50 },
    conditionalEffect: {
      condition: 'graze_streak',
      threshold: 1,
      effect: { attackSpeedPercent: 10 }, // Per graze
      description: '+10% attack speed per graze stack',
    },
    color: '#FFDD00',
    colorSecondary: '#CC9900',
    icon: '⚡',
    particleSystem: 'lightning_spark',
    triggerText: 'QUICK!',
    synergizesWith: ['swift_wings', 'frenzy', 'graze_frenzy'],
    synergyBonus: 'Graze stacks decay 50% slower',
    comboTier: 'advanced',
    skillScaling: 'high',
    apexIntegration: {
      duringCharge: { attackSpeedPercent: 25 },
      description: 'Faster apex charge-up',
    },
  },
  {
    id: 'frenzy',
    name: 'Frenzy',
    description: '+80% attack speed. +5% per kill (decays).',
    hiddenDepth: 'At 10 kill stacks, screen tints red and damage +20%.',
    effect: { attackSpeedPercent: 80 },
    onKillEffect: {
      type: 'damage_stack',
      stackable: true,
      maxStacks: 10,
      duration: 3000,
      description: '+5% attack speed per kill, +20% damage at max',
    },
    color: '#FF6600',
    colorSecondary: '#CC3300',
    icon: '💨',
    particleSystem: 'speed_blur',
    screenEffect: 'chromatic',
    triggerText: 'FRENZY!',
    synergizesWith: ['quick_strikes', 'berserker_pace', 'lifesteal'],
    synergyBonus: 'Kill stacks also heal 1% HP each',
    comboTier: 'legendary',
    skillScaling: 'extreme',
    apexIntegration: {
      onApexKill: { type: 'speed_burst', speedBonus: 15, duration: 500, description: 'Apex kills boost speed' },
      description: 'Apex kills add 3 frenzy stacks',
    },
  },
  {
    id: 'swift_wings',
    name: 'Swift Wings',
    description: '+40% movement speed. Leave speed trail that damages.',
    hiddenDepth: 'Trail deals 2 DPS to enemies and slows them 10%.',
    effect: { moveSpeedPercent: 40 },
    passiveEffect: {
      type: 'trail',
      damagePerSecond: 2,
      slowPercent: 10,
      description: 'Speed trail damages and slows enemies',
    },
    color: '#88CCFF',
    colorSecondary: '#4488CC',
    icon: '🦋',
    particleSystem: 'wing_trail',
    triggerText: 'SWIFT!',
    synergizesWith: ['quick_strikes', 'hunters_rush', 'thermal_wake'],
    synergyBonus: 'Trail duration doubled',
    comboTier: 'advanced',
    skillScaling: 'moderate',
    apexIntegration: {
      duringStrike: { moveSpeedPercent: 50 },
      description: 'Apex dashes leave longer trail',
    },
  },
  {
    id: 'hunters_rush',
    name: "Hunter's Rush",
    description: '+60% speed toward enemies. +20% damage while rushing.',
    hiddenDepth: 'First hit after rush deals double damage.',
    effect: { moveSpeedPercent: 60, damagePercent: 20 },
    color: '#FF4444',
    colorSecondary: '#CC2222',
    icon: '🏃',
    particleSystem: 'hunt_lines',
    screenEffect: 'vignette',
    triggerText: 'HUNT!',
    synergizesWith: ['swift_wings', 'savage_blow', 'momentum'],
    synergyBonus: 'Rush bonus never decays while enemies nearby',
    comboTier: 'advanced',
    skillScaling: 'high',
    apexIntegration: {
      duringCharge: { damagePercent: 30 },
      description: 'Apex charged while rushing deals +30%',
    },
  },
  {
    id: 'berserker_pace',
    name: 'Berserker Pace',
    description: '+35% attack AND movement speed. +10% more when hit.',
    hiddenDepth: 'Being hit grants 2s of additional +25% both speeds.',
    effect: { attackSpeedPercent: 35, moveSpeedPercent: 35 },
    conditionalEffect: {
      condition: 'near_enemies',
      threshold: 3,
      effect: { attackSpeedPercent: 10, moveSpeedPercent: 10 },
      description: '+10% both when near 3+ enemies',
    },
    color: '#FF6666',
    colorSecondary: '#CC4444',
    icon: '🔄',
    particleSystem: 'berserker_aura',
    screenEffect: 'pulse',
    triggerText: 'RAMPAGE!',
    synergizesWith: ['frenzy', 'hardened_shell', 'last_stand'],
    synergyBonus: 'Damage taken also grants damage dealt',
    comboTier: 'legendary',
    skillScaling: 'high',
    apexIntegration: {
      duringStrike: { attackSpeedPercent: 20, moveSpeedPercent: 20 },
      description: 'Apex always has berserker bonus',
    },
  },
  {
    id: 'bullet_time',
    name: 'Bullet Time',
    description: '+50% both speeds. Enemies move 15% slower near you.',
    hiddenDepth: 'At high combo, time literally slows for enemies.',
    effect: { attackSpeedPercent: 50, moveSpeedPercent: 50 },
    passiveEffect: {
      type: 'aura',
      radius: 100,
      slowPercent: 15,
      description: 'Enemies near you are slowed 15%',
    },
    color: '#9999FF',
    colorSecondary: '#6666CC',
    icon: '⏱️',
    particleSystem: 'time_ripple',
    screenEffect: 'slow_mo',
    triggerText: 'BULLET TIME!',
    synergizesWith: ['berserker_pace', 'graze_frenzy', 'glass_cannon'],
    synergyBonus: 'Time slow increases with combo tier',
    comboTier: 'legendary',
    skillScaling: 'extreme',
    apexIntegration: {
      duringStrike: { moveSpeedPercent: 100 },
      description: 'Apex moves at double speed relative to enemies',
    },
  },

  // =========================================================================
  // DEFENSE PERKS - Survive to combo more
  // =========================================================================
  {
    id: 'thick_carapace',
    name: 'Thick Carapace',
    description: '+75 max HP. +25 more per combo tier.',
    hiddenDepth: 'At legendary combo, gain temporary shield on kill.',
    effect: { maxHpBonus: 75 },
    conditionalEffect: {
      condition: 'high_combo',
      threshold: 2, // Combo tier
      effect: { maxHpBonus: 25 }, // Per tier
      description: '+25 HP per combo tier',
    },
    color: '#888888',
    colorSecondary: '#555555',
    icon: '🛡️',
    particleSystem: 'armor_plate',
    triggerText: 'FORTIFIED!',
    synergizesWith: ['hardened_shell', 'regeneration', 'last_stand'],
    synergyBonus: 'Kills grant 3s of +20% damage reduction',
    comboTier: 'basic',
    skillScaling: 'none',
    apexIntegration: {
      duringCharge: { damageReduction: 20 },
      description: 'Reduced damage while charging apex',
    },
  },
  {
    id: 'hardened_shell',
    name: 'Hardened Shell',
    description: '-40% damage taken. -5% more per nearby enemy (max -60%).',
    hiddenDepth: 'When surrounded by 5+ enemies, reflect 10% damage.',
    effect: { damageReduction: 40 },
    conditionalEffect: {
      condition: 'near_enemies',
      threshold: 1,
      effect: { damageReduction: 5 }, // Per nearby
      description: '-5% damage per nearby enemy',
    },
    color: '#668866',
    colorSecondary: '#446644',
    icon: '🐢',
    particleSystem: 'shield_shimmer',
    screenEffect: 'flash',
    triggerText: 'BLOCKED!',
    synergizesWith: ['thick_carapace', 'berserker_pace', 'revenge'],
    synergyBonus: 'Blocked damage adds to next attack',
    comboTier: 'advanced',
    skillScaling: 'moderate',
    apexIntegration: {
      duringStrike: { damageReduction: 80 },
      description: 'Near-invulnerable during apex strike',
    },
  },
  {
    id: 'regeneration',
    name: 'Regeneration',
    description: '+5 HP/s. Doubles when not taking damage for 3s.',
    hiddenDepth: 'At full HP, excess regen adds to damage.',
    effect: { hpRegenPerSecond: 5 },
    color: '#00FF66',
    colorSecondary: '#00CC44',
    icon: '💚',
    particleSystem: 'heal_sparkle',
    triggerText: '+HP',
    synergizesWith: ['thick_carapace', 'lifesteal', 'graze_frenzy'],
    synergyBonus: 'Grazes trigger instant heal tick',
    comboTier: 'basic',
    skillScaling: 'moderate',
    apexIntegration: {
      onApexKill: { type: 'heal', healPercent: 5, description: 'Apex kills heal 5%' },
      description: 'Apex kills heal 5% max HP',
    },
  },
  {
    id: 'lifesteal',
    name: 'Lifesteal',
    description: 'Heal 25% of damage dealt. +5% per combo tier.',
    hiddenDepth: 'At transcendent combo, lifesteal exceeds 100%.',
    effect: { lifestealPercent: 25 },
    conditionalEffect: {
      condition: 'high_combo',
      threshold: 1,
      effect: { lifestealPercent: 5 },
      description: '+5% lifesteal per combo tier',
    },
    color: '#FF0066',
    colorSecondary: '#CC0044',
    icon: '🧛',
    particleSystem: 'blood_orb',
    triggerText: 'DRAIN!',
    synergizesWith: ['savage_blow', 'frenzy', 'glass_cannon'],
    synergyBonus: 'Overkill damage is also healed',
    comboTier: 'advanced',
    skillScaling: 'high',
    apexIntegration: {
      onApexHit: { type: 'heal', healPercent: 10, description: 'Apex hits heal 10%' },
      description: 'Apex hits heal 10% of damage dealt',
    },
  },
  {
    id: 'last_stand',
    name: 'Last Stand',
    description: '+90% defense below 30% HP. +30% damage.',
    hiddenDepth: 'Below 15% HP, become invulnerable for 0.5s (once per fight).',
    effect: { damageReduction: 90, damagePercent: 30 },
    conditionalEffect: {
      condition: 'low_hp',
      threshold: 30,
      effect: { damageReduction: 90, damagePercent: 30 },
      description: 'Massive bonuses when low HP',
    },
    color: '#880000',
    colorSecondary: '#550000',
    icon: '💀',
    particleSystem: 'rage_aura',
    screenEffect: 'vignette',
    triggerText: 'LAST STAND!',
    synergizesWith: ['glass_cannon', 'lifesteal', 'berserker_pace'],
    synergyBonus: 'Kills extend invulnerability window',
    comboTier: 'legendary',
    skillScaling: 'extreme',
    apexIntegration: {
      duringStrike: { damagePercent: 50 },
      description: 'Low HP apex strikes deal +50%',
    },
  },
  {
    id: 'second_wind',
    name: 'Second Wind',
    description: 'Revive at 75% HP once. Revive grants 3s invuln.',
    hiddenDepth: 'Each legendary combo adds another revive (max 3).',
    effect: { maxHpBonus: 0 }, // Revive handled specially
    color: '#FFDD88',
    colorSecondary: '#CCAA44',
    icon: '✨',
    particleSystem: 'golden_burst',
    screenEffect: 'freeze_frame',
    triggerText: 'REVIVED!',
    synergizesWith: ['last_stand', 'thick_carapace', 'regeneration'],
    synergyBonus: 'Revive also clears all combo stacks (fresh start)',
    comboTier: 'legendary',
    skillScaling: 'none',
    apexIntegration: {
      description: 'Revive grants instant apex cooldown reset',
    },
  },

  // =========================================================================
  // SPECIAL PERKS - Unique powerful effects
  // =========================================================================
  {
    id: 'critical_sting',
    name: 'Critical Sting',
    description: '30% crit chance for 2x damage. +10% chance per graze.',
    hiddenDepth: 'Consecutive crits increase crit multiplier (caps at 4x).',
    effect: { critChance: 30 },
    conditionalEffect: {
      condition: 'graze_streak',
      threshold: 1,
      effect: { critChance: 10 },
      description: '+10% crit chance per graze',
    },
    color: '#FFAA00',
    colorSecondary: '#CC8800',
    icon: '💥',
    particleSystem: 'crit_burst',
    screenEffect: 'shake',
    triggerText: 'CRIT!',
    synergizesWith: ['double_strike', 'sharpened_mandibles', 'momentum'],
    synergyBonus: 'Crits grant +1 momentum stack',
    comboTier: 'legendary',
    skillScaling: 'high',
    apexIntegration: {
      onApexHit: { type: 'damage_stack', damage: 20, stackable: true, maxStacks: 3, description: 'Apex crits stack' },
      description: 'Apex hits always crit at combo tier 2+',
    },
  },
  {
    id: 'execution',
    name: 'Execution',
    description: 'Instant kill below 20% HP. +5% threshold per combo tier.',
    hiddenDepth: 'Executions dont break momentum and grant +50% combo.',
    effect: { executeThreshold: 20 },
    conditionalEffect: {
      condition: 'high_combo',
      threshold: 1,
      effect: { executeThreshold: 5 },
      description: '+5% execute threshold per combo tier',
    },
    color: '#440000',
    colorSecondary: '#220000',
    icon: '⚰️',
    particleSystem: 'death_slash',
    screenEffect: 'freeze_frame',
    triggerText: 'EXECUTED!',
    synergizesWith: ['savage_blow', 'chain_lightning', 'giant_killer'],
    synergyBonus: 'Executions chain to other low-HP enemies',
    comboTier: 'legendary',
    skillScaling: 'moderate',
    apexIntegration: {
      duringStrike: { executeThreshold: 10 },
      description: 'Apex execute threshold +10%',
    },
  },
  {
    id: 'sweeping_arc',
    name: 'Sweeping Arc',
    description: 'Attack hits 360 degrees. Each enemy hit adds +5% damage.',
    hiddenDepth: 'Hitting 5+ enemies at once triggers screen-wide pulse.',
    effect: { damagePercent: 5 }, // Per enemy hit
    color: '#FF8844',
    colorSecondary: '#CC6622',
    icon: '🌀',
    particleSystem: 'full_circle',
    screenEffect: 'pulse',
    triggerText: 'SWEEP!',
    synergizesWith: ['chain_lightning', 'crushing_bite', 'frenzy'],
    synergyBonus: 'Pulse deals 50% of total damage dealt',
    comboTier: 'legendary',
    skillScaling: 'high',
    apexIntegration: {
      duringStrike: { damagePercent: 100 },
      description: 'Apex hits all enemies in path',
    },
  },
  {
    id: 'chain_lightning',
    name: 'Chain Lightning',
    description: 'Kills chain to nearby enemy. +1 chain per combo tier.',
    hiddenDepth: 'Chains deal 75% damage. At legendary combo, chains explode.',
    effect: { chainRange: 100 },
    conditionalEffect: {
      condition: 'high_combo',
      threshold: 1,
      effect: { chainRange: 25 },
      description: '+25 chain range per combo tier',
    },
    color: '#4488FF',
    colorSecondary: '#2266CC',
    icon: '⚡',
    particleSystem: 'lightning_arc',
    screenEffect: 'flash',
    triggerText: 'CHAIN!',
    synergizesWith: ['crushing_bite', 'venomous_strike', 'sweeping_arc'],
    synergyBonus: 'Chains spread poison/explosions',
    comboTier: 'legendary',
    skillScaling: 'high',
    apexIntegration: {
      onApexKill: { type: 'chain', radius: 150, damage: 50, description: 'Apex kills chain' },
      description: 'Apex kills chain to 2 additional enemies',
    },
  },
  {
    id: 'momentum',
    name: 'Momentum',
    description: '+15% damage per consecutive kill (max 75%).',
    hiddenDepth: 'At max momentum, attacks generate shockwaves.',
    effect: { damagePercent: 15 }, // Per kill
    onKillEffect: {
      type: 'damage_stack',
      stackable: true,
      maxStacks: 5,
      duration: 2000,
      description: '+15% damage per kill, stacks 5x',
    },
    color: '#FF44FF',
    colorSecondary: '#CC22CC',
    icon: '🚀',
    particleSystem: 'momentum_aura',
    screenEffect: 'chromatic',
    triggerText: 'MOMENTUM!',
    synergizesWith: ['chain_lightning', 'hunters_rush', 'critical_sting'],
    synergyBonus: 'Momentum decays 50% slower',
    comboTier: 'advanced',
    skillScaling: 'extreme',
    apexIntegration: {
      duringStrike: { damagePercent: 25 },
      description: 'Apex strikes maintain momentum',
    },
  },
  {
    id: 'glass_cannon',
    name: 'Glass Cannon',
    description: '+150% damage, -40% max HP. Die in style.',
    hiddenDepth: 'Each graze adds +10% damage. Getting hit resets all.',
    effect: { damagePercent: 150, maxHpBonus: -40 },
    conditionalEffect: {
      condition: 'graze_streak',
      threshold: 1,
      effect: { damagePercent: 10 },
      description: '+10% damage per graze (resets on hit)',
    },
    color: '#FF0000',
    colorSecondary: '#AA0000',
    icon: '💎',
    particleSystem: 'crystal_shards',
    screenEffect: 'vignette',
    triggerText: 'GLASS CANNON!',
    synergizesWith: ['graze_frenzy', 'lifesteal', 'last_stand'],
    synergyBonus: 'Grazes heal 1% HP each',
    comboTier: 'transcendent',
    skillScaling: 'extreme',
    apexIntegration: {
      duringStrike: { damagePercent: 100 },
      description: 'Apex strikes deal +100% on top',
    },
  },

  // =========================================================================
  // SKILL-GATED PERKS - INSANE potential for skilled players
  // =========================================================================
  {
    id: 'graze_frenzy',
    name: 'Graze Frenzy',
    description: 'Near-misses grant +8% attack speed and +5% damage. Hit resets.',
    hiddenDepth: 'At 10 graze stacks, enter bullet-time for 2s.',
    effect: { attackSpeedPercent: 8, damagePercent: 5 },
    conditionalEffect: {
      condition: 'graze_streak',
      threshold: 10,
      effect: { attackSpeedPercent: 100, damagePercent: 50 },
      description: 'Bullet-time at 10 graze stacks',
    },
    color: '#FF00FF',
    colorSecondary: '#AA00AA',
    icon: '💫',
    particleSystem: 'graze_spark',
    screenEffect: 'slow_mo',
    triggerText: 'GRAZE!',
    synergizesWith: ['quick_strikes', 'glass_cannon', 'swift_wings'],
    synergyBonus: 'Graze window increased 50%',
    comboTier: 'transcendent',
    skillScaling: 'extreme',
    apexIntegration: {
      duringStrike: { grazeWindow: 50 },
      description: 'Apex strike grazes more easily',
    },
  },
  {
    id: 'venom_architect',
    name: 'Venom Architect',
    description: 'Venom stacks INFINITELY. Venom kills explode.',
    hiddenDepth: 'Explosion damage = 10 x venom stacks. No cap.',
    effect: { poisonDps: 1 }, // Per stack
    onKillEffect: {
      type: 'explosion',
      radius: 80,
      damage: 10, // x stacks
      description: 'Venom kills explode (10 damage x stacks)',
    },
    color: '#00FF00',
    colorSecondary: '#00AA00',
    icon: '☠️',
    particleSystem: 'venom_explosion',
    screenEffect: 'shake',
    triggerText: 'VENOM EXPLODE!',
    synergizesWith: ['venomous_strike', 'chain_lightning', 'sweeping_arc'],
    synergyBonus: 'Explosions apply venom to survivors',
    comboTier: 'transcendent',
    skillScaling: 'extreme',
    apexIntegration: {
      onApexHit: { type: 'poison', stacks: 5, duration: 999999, description: 'Apex applies 5 venom' },
      description: 'Apex strikes apply 5 venom stacks',
    },
  },
  {
    id: 'glass_cannon_mastery',
    name: 'Glass Cannon Mastery',
    description: 'Set HP to 1. +500% damage. +50% move speed.',
    hiddenDepth: 'Perfect grazes grant 0.1s invulnerability.',
    effect: { damagePercent: 500, moveSpeedPercent: 50, maxHpBonus: -999 },
    color: '#FF0000',
    colorSecondary: '#880000',
    icon: '💀',
    particleSystem: 'rage_aura',
    screenEffect: 'vignette',
    triggerText: 'MASTERY!',
    synergizesWith: ['graze_frenzy', 'swift_wings', 'lifesteal'],
    synergyBonus: 'Perfect grazes heal 1 HP',
    comboTier: 'transcendent',
    skillScaling: 'extreme',
    apexIntegration: {
      duringStrike: { damagePercent: 200, moveSpeedPercent: 100 },
      description: 'Apex is even more devastating',
    },
  },
];

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Get enhanced perk by ID
 */
export function getEnhancedPerk(id: AbilityId): EnhancedPerk | undefined {
  return ENHANCED_PERKS.find(p => p.id === id);
}

/**
 * Get perks that synergize with a given perk
 */
export function getSynergyPartners(id: AbilityId): AbilityId[] {
  const perk = getEnhancedPerk(id);
  return perk?.synergizesWith ?? [];
}

/**
 * Check if two perks have a synergy
 */
export function hasSynergy(id1: AbilityId, id2: AbilityId): boolean {
  const perk1 = getEnhancedPerk(id1);
  const perk2 = getEnhancedPerk(id2);
  if (!perk1 || !perk2) return false;

  return perk1.synergizesWith.includes(id2) || perk2.synergizesWith.includes(id1);
}

/**
 * Get all active synergies for a set of perks
 */
export function getActiveSynergies(ownedPerks: AbilityId[]): Array<{
  perk1: AbilityId;
  perk2: AbilityId;
  bonus: string;
}> {
  const synergies: Array<{ perk1: AbilityId; perk2: AbilityId; bonus: string }> = [];

  for (let i = 0; i < ownedPerks.length; i++) {
    for (let j = i + 1; j < ownedPerks.length; j++) {
      const perk1 = ownedPerks[i];
      const perk2 = ownedPerks[j];

      if (hasSynergy(perk1, perk2)) {
        const enhancedPerk = getEnhancedPerk(perk1);
        synergies.push({
          perk1,
          perk2,
          bonus: enhancedPerk?.synergyBonus ?? 'Unknown synergy',
        });
      }
    }
  }

  return synergies;
}

/**
 * Calculate total enhanced effects from owned perks
 */
export function calculateEnhancedEffects(
  ownedPerks: AbilityId[],
  conditions: {
    playerHpPercent: number;
    nearbyEnemies: number;
    grazeStreak: number;
    comboTier: ComboTier;
  }
): EnhancedPerkEffect {
  const totalEffect: EnhancedPerkEffect = {
    damagePercent: 0,
    flatDamage: 0,
    critChance: 0,
    critMultiplier: 0,
    executeThreshold: 0,
    poisonDps: 0,
    bleedDps: 0,
    moveSpeedPercent: 0,
    attackSpeedPercent: 0,
    maxHpBonus: 0,
    damageReduction: 0,
    hpRegenPerSecond: 0,
    lifestealPercent: 0,
    chainRange: 0,
    bounceStrength: 0,
    grazeWindow: 0,
    momentumGain: 0,
  };

  const comboTierNumber = {
    basic: 0,
    advanced: 1,
    legendary: 2,
    transcendent: 3,
  }[conditions.comboTier];

  for (const perkId of ownedPerks) {
    const perk = getEnhancedPerk(perkId);
    if (!perk) continue;

    // Add base effects
    for (const [key, value] of Object.entries(perk.effect)) {
      if (typeof value === 'number') {
        (totalEffect as Record<string, number>)[key] = ((totalEffect as Record<string, number>)[key] || 0) + value;
      }
    }

    // Check conditional effects
    if (perk.conditionalEffect) {
      const { condition, threshold, effect } = perk.conditionalEffect;
      let conditionMet = false;
      let multiplier = 1;

      switch (condition) {
        case 'low_hp':
          conditionMet = conditions.playerHpPercent <= (threshold || 50);
          break;
        case 'high_combo':
          conditionMet = comboTierNumber >= (threshold || 1);
          multiplier = comboTierNumber;
          break;
        case 'near_enemies':
          conditionMet = conditions.nearbyEnemies >= (threshold || 1);
          multiplier = Math.min(conditions.nearbyEnemies, 5);
          break;
        case 'graze_streak':
          conditionMet = conditions.grazeStreak >= (threshold || 1);
          multiplier = Math.min(conditions.grazeStreak, 10);
          break;
        case 'bouncing':
          // Would need bounce state passed in
          break;
      }

      if (conditionMet) {
        for (const [key, value] of Object.entries(effect)) {
          if (typeof value === 'number') {
            (totalEffect as Record<string, number>)[key] = ((totalEffect as Record<string, number>)[key] || 0) + (value * multiplier);
          }
        }
      }
    }
  }

  return totalEffect;
}

// =============================================================================
// Export
// =============================================================================

export default {
  ENHANCED_PERKS,
  getEnhancedPerk,
  getSynergyPartners,
  hasSynergy,
  getActiveSynergies,
  calculateEnhancedEffects,
};
