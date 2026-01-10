# Ability Rebalance Proposal

**Date**: 2025-12-30
**Status**: Draft for Review
**Author**: Creative Agent + Kent

---

## Upgrade Economy Context

Understanding the flow of power is critical to balance:

| Wave | Approx Level | Upgrades Received | Cumulative |
|------|--------------|-------------------|------------|
| 1-2 | 1-3 | ~4-5 | 4-5 |
| 3-4 | 4-6 | ~3-4 | 7-9 |
| 5-6 | 7-9 | ~2-3 | 9-12 |
| 7-8 | 10-12 | ~2 | 11-14 |
| 9-10 | 13-15 | ~1.5 | 12-16 |
| 10+ | 15+ | ~1.25/wave | 15-20+ |

**Key Insight**: By wave 5, players have 9-12 upgrades. By endgame, 15-20+.

**Implication**: Individual ability power must be calibrated so that:
- 5 defense abilities don't create immortality
- 5 damage abilities don't one-shot everything
- Mixed builds remain viable against focused builds

---

## Power Budget Framework

Each ability has a "power budget" of **100 points**. This ensures:
- All abilities are roughly equal in impact
- Stacking similar abilities has diminishing total value
- Synergies can exceed 100 (the 1+1=3 moment)

| Power Type | Budget Allocation | Notes |
|------------|-------------------|-------|
| Pure Stat | 100 pts in one stat | Boring but reliable |
| Conditional | 150 pts with condition | Rewards skill |
| Risk-Reward | 200 pts benefit, -100 pts cost | High skill ceiling |
| Utility | 80 pts + unique effect | Enables strategies |

---

## Current State Analysis: DEFENSE CATEGORY

### The Immortality Stack (Current Problem)

If a player takes all defense abilities (assuming 3 stacks where applicable):

| Ability | Stacks | Effect | Cumulative Impact |
|---------|--------|--------|-------------------|
| thick_carapace | 3 | +225 HP | 325 total HP |
| hardened_shell | 1 | -40% damage | Effective HP: 542 |
| regeneration | 3 | +15 HP/s | Full heal in 36s |
| lifesteal | 1 | 25% of damage | +sustain on offense |
| last_stand | 1 | +90% DR below 30% | Near-invincible when low |
| second_wind | 1 | Revive at 75% HP | Free death |

**Result**: Player has 542 effective HP, regens 15 HP/s, has a free death, and becomes nearly invincible when low.

**Problem**: This removes the need for skill. Player can ignore mechanics and still survive.

---

## Rebalance Philosophy

### Three Laws of Defense

1. **Sustain must be earned, not passive**
   - No "free" HP/s regeneration
   - Healing tied to actions (kills, movement, grazes)

2. **Defense must have opportunity cost**
   - Taking defense = giving up offense or utility
   - Or: defense has an active tradeoff (take more damage for healing)

3. **Low HP should be dangerous, not safe**
   - Current `last_stand` makes low HP the safest place
   - Proposed: Low HP = high risk, high reward speed

---

## FULL ABILITY REBALANCE SPREADSHEET

### Legend

| Symbol | Meaning |
|--------|---------|
| 🟢 | Keep as-is or minor tweak |
| 🟡 | Significant rebalance needed |
| 🔴 | Remove or completely redesign |
| ⭐ | New ability (replaces removed) |
| 🎯 | Skill-gated (requires execution) |
| ⚖️ | Risk-reward (benefit + cost) |

---

### DAMAGE CATEGORY (4 abilities)

| ID | Name | Current | Issue | Proposed | Change | Tags |
|----|------|---------|-------|----------|--------|------|
| `raw_power` | Raw Power | +50% damage, stackable ∞ | Boring but necessary anchor | +40% damage, max 5 stacks (200% cap) | 🟡 Cap stacks | `aggressive` |
| `venomous_strike` | Infectious Poison | 3% max HP/s per stack, spreads on kill | Good design, maybe too strong late | 2.5% max HP/s per stack, max 4 stacks | 🟡 Slight nerf | `control`, `dot` |
| `double_strike` | Double Strike | 40% chance to hit twice | Fun, good variance | 35% chance to hit twice | 🟢 Minor tune | `aggressive`, `rng` |
| `savage_blow` | Savage Blow | +150% damage to <50% HP enemies | Synergizes with execute | +100% damage to <40% HP enemies | 🟡 Tighter window | `execute`, `aggressive` |
| `giant_killer` | Giant Killer | +300% damage to >75% HP enemies | Anti-tank, good niche | Keep as-is | 🟢 Keep | `aggressive`, `opener` |

**Damage Category Health**: Generally good. Damage has natural diminishing returns (overkill is wasted).

---

### SPEED CATEGORY (6 abilities)

| ID | Name | Current | Issue | Proposed | Change | Tags |
|----|------|---------|-------|----------|--------|------|
| `quick_strikes` | Quick Strikes | +50% attack speed, 3 stacks | Stacks to +150% = absurd | +40% attack speed, 2 stacks max (80% cap) | 🟡 Cap stacks | `aggressive`, `tempo` |
| `frenzy` | Bloodrush | +25% attack speed (placeholder) | Not implemented as described | Kills grant +15% attack speed for 2s, stacks 5x | 🟡 Implement properly | `aggressive`, `momentum` 🎯 |
| `swift_wings` | Swift Wings | +40% move speed, 3 stacks | +120% = too fast | +30% move speed, 2 stacks max (60% cap) | 🟡 Cap stacks | `mobile`, `evasion` |
| `hunters_rush` | Hunter's Rush | +60% move speed | Overlaps swift_wings | +40% move speed toward enemies only | 🟡 Conditional | `aggressive`, `mobile` 🎯 |
| `berserker_pace` | Berserker Pace | +35% attack AND move | Efficient slot | +25% attack, +25% move, -10% max HP | 🟡 Add cost | `aggressive`, `mobile` ⚖️ |
| `bullet_time` | Bullet Time | Enemies 10% slower, 2 stacks | Good utility, maybe weak | Enemies 15% slower, 2 stacks (30% cap) | 🟡 Buff slightly | `control`, `evasion` |

**Speed Category Health**: Mostly fine. Needs stack caps to prevent absurdity.

---

### DEFENSE CATEGORY (6 abilities) - MAJOR OVERHAUL

| ID | Name | Current | Issue | Proposed | Change | Tags |
|----|------|---------|-------|----------|--------|------|
| `thick_carapace` | Thick Carapace | +75 HP, 3 stacks (+225) | Too much free HP | +50 HP, 2 stacks max (+100 cap) | 🟡 Reduce | `tank`, `passive` |
| `hardened_shell` | Hardened Shell | -40% damage taken | Passive DR is boring | -25% damage while moving, 0% while still | 🔴 Redesign | `tank`, `mobile` 🎯 |
| `regeneration` | Regeneration | +5 HP/s, 3 stacks | Passive regen = no skill | **REMOVE** → Replace with Predator's Hunger | 🔴 Remove | - |
| `lifesteal` | Lifesteal | Heal 25% of damage | Too strong, passive | Heal 8% of damage, cap at 5 HP per hit | 🟡 Heavy nerf | `sustain`, `aggressive` |
| `last_stand` | Last Stand | +90% DR below 30% HP | Makes low HP safest | Below 30% HP: +50% speed, +25% damage, 0% DR | 🔴 Redesign | `glass`, `mobile` 🎯 |
| `second_wind` | Second Wind | Revive once at 75% HP | Free death = no stakes | Revive at 25% HP only if combo ≥30 | 🔴 Redesign | `sustain`, `momentum` 🎯 |

#### New Defense Abilities (Replacements)

| ID | Name | Description | Design Intent | Tags |
|----|------|-------------|---------------|------|
| ⭐ `predators_hunger` | Predator's Hunger | Kills heal 3% max HP. Taking damage resets heal-per-kill to 0% for 2s. | Sustain requires not getting hit | `sustain`, `aggressive` 🎯 |
| ⭐ `blood_price` | Blood Price | Heal 15% of damage dealt. Take 20% more damage. | High sustain, high risk | `sustain`, `glass` ⚖️ |
| ⭐ `adrenaline_surge` | Adrenaline Surge | After taking damage: +60% speed for 1.5s, 0.15s immunity. 3s cooldown. | Reward for surviving hits | `mobile`, `reactive` 🎯 |
| ⭐ `hollow_carapace` | Hollow Carapace | Max HP = 1. +150% damage. +50% speed. | Ultimate glass cannon | `glass`, `aggressive` ⚖️ |

---

### SPECIAL CATEGORY (6 base + 5 skill-gated = 11 abilities)

| ID | Name | Current | Issue | Proposed | Change | Tags |
|----|------|---------|-------|----------|--------|------|
| `critical_sting` | Critical Sting | 30% crit, 3 stacks | 90% crit = near-guaranteed | 25% crit, 2 stacks max (50% cap) | 🟡 Cap | `aggressive`, `rng` |
| `execution` | Execution | Instant kill <20% HP | Good execute fantasy | Instant kill <15% HP | 🟡 Tighter | `execute`, `aggressive` |
| `sweeping_arc` | Sweeping Arc | 360° attacks | Strong utility | Keep as-is | 🟢 Keep | `aoe`, `control` |
| `chain_lightning` | Chain Lightning | Kills chain +1 bounce/stack | Good scaling | Keep as-is | 🟢 Keep | `aoe`, `aggressive` |
| `momentum` | Momentum | +15% damage per kill, max 75% | Snowball mechanic | +10% per kill, max 50%, decays 5%/s without kills | 🟡 Add decay | `momentum`, `aggressive` 🎯 |
| `glass_cannon` | Glass Cannon | +150% damage, -40% HP | Good risk-reward | +100% damage, -50% HP | 🟡 More extreme | `glass`, `aggressive` ⚖️ |

#### Skill-Gated Special (Keep but verify implementation)

| ID | Name | Current | Status | Tags |
|----|------|---------|--------|------|
| `graze_frenzy` | Graze Frenzy | Near-miss stacks bonuses, hit resets | 🟢 Perfect design | `glass`, `evasion` 🎯 |
| `thermal_momentum` | Thermal Momentum | Movement builds heat, stop = pulse | 🟢 Good skill gate | `mobile`, `aoe` 🎯 |
| `execution_chain` | Execution Chain | Kill low-HP chains to wounded | 🟢 Good combo potential | `execute`, `aoe` 🎯 |
| `glass_cannon_mastery` | Glass Cannon Mastery | 1 HP, 500% damage, 50% speed | 🟢 Ultimate skill test | `glass`, `aggressive` ⚖️ |
| `venom_architect` | Venom Architect | Infinite venom stacks, explode on kill | 🟢 Good ramp mechanic | `dot`, `aoe` 🎯 |

---

## CUMULATIVE STACK ANALYSIS

### Before Rebalance: Max Stacking

| Stat | Max Current | With 15 upgrades | Problem? |
|------|-------------|------------------|----------|
| Damage | 3.0x cap | 3.0x (capped) | ✅ Capped |
| Attack Speed | +150% | +150% | ⚠️ Too high |
| Move Speed | +120% | +120% | ⚠️ Too high |
| Max HP | +225 | +225 | ⚠️ Too high |
| Damage Reduction | ~60% effective | ~60% | ⚠️ With last_stand = near immune |
| HP Regen | 15 HP/s | 15 HP/s | ❌ Way too high |
| Lifesteal | 25% | 25% | ⚠️ High |
| Crit Chance | 90% | 90% | ⚠️ Near guaranteed |

### After Rebalance: Max Stacking

| Stat | Max Proposed | With 15 upgrades | Status |
|------|--------------|------------------|--------|
| Damage | 3.0x cap | 3.0x (capped) | ✅ Kept |
| Attack Speed | +80% | +80% | ✅ Reasonable |
| Move Speed | +60% (base) +40% (conditional) | +100% situational | ✅ Skill-gated |
| Max HP | +100 | +100 | ✅ Reasonable |
| Damage Reduction | 25% (conditional) | 25% while moving | ✅ Skill-gated |
| HP Regen | 0 passive | 0 | ✅ Must earn healing |
| Lifesteal | 8%, cap 5/hit | 8% | ✅ Capped per-hit |
| Crit Chance | 50% | 50% | ✅ Reasonable |

---

## COMBO SYSTEM DESIGN

### Combo Tags Reference

| Tag | Meaning | Example Abilities |
|-----|---------|-------------------|
| `aggressive` | Offense focused | raw_power, double_strike, savage_blow |
| `mobile` | Movement focused | swift_wings, hunters_rush, adrenaline_surge |
| `control` | Crowd control | bullet_time, venomous_strike, sweeping_arc |
| `glass` | High risk high reward | glass_cannon, hollow_carapace, graze_frenzy |
| `sustain` | Survivability | predators_hunger, blood_price, lifesteal |
| `execute` | Finisher style | savage_blow, execution, execution_chain |
| `momentum` | Snowball/streak | frenzy, momentum, predators_hunger |
| `dot` | Damage over time | venomous_strike, venom_architect |
| `aoe` | Area damage | sweeping_arc, chain_lightning, thermal_momentum |

### Proposed Combos (Unlocked by having 2+ matching tags)

| Combo Name | Requires | Bonus | Discovery Text |
|------------|----------|-------|----------------|
| **Berserker's Fury** | 3x `aggressive` | +15% damage, attacks have 10% lifesteal | "PAIN IS FUEL" |
| **Glass Cannon Mastery** | 2x `glass` + 1x `aggressive` | +25% damage, -25% max HP | "FRAGILE BUT DEADLY" |
| **Predator's Dance** | 2x `mobile` + 1x `aggressive` | +20% damage while moving | "DEATH IN MOTION" |
| **Crowd Control** | 2x `control` + 1x `aoe` | Control effects last 50% longer | "THEY CAN'T ESCAPE" |
| **Execution Protocol** | 2x `execute` | Execute threshold +5% (e.g., 15% → 20%) | "NO MERCY" |
| **Momentum Demon** | 3x `momentum` | Kill streak bonuses decay 50% slower | "UNSTOPPABLE" |
| **Poison Master** | 2x `dot` | DoT effects deal 25% more damage | "SLOW DEATH" |
| **Area Denial** | 2x `aoe` | AoE radius +20% | "NOWHERE TO HIDE" |
| **Hybrid Vigor** | No 2+ of same tag | All stats +5% | "JACK OF ALL TRADES" |

### Combo UI Hints

When selecting an ability, show:

```
┌─────────────────────────────────────────────┐
│ 🟢 WOULD UNLOCK: "Berserker's Fury"         │
│    You have: raw_power, double_strike       │
│    This adds: savage_blow (aggressive)      │
│    Bonus: +15% damage, 10% lifesteal        │
└─────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────┐
│ 🟡 1 MORE FOR: "Predator's Dance"           │
│    You have: swift_wings (mobile)           │
│    This adds: hunters_rush (mobile)         │
│    Need: 1 more aggressive ability          │
└─────────────────────────────────────────────┘
```

---

## ARCHETYPE ALIGNMENT

Each archetype should have a natural combo path:

| Archetype | Core Tags | Natural Combo |
|-----------|-----------|---------------|
| **Executioner** | `execute`, `aggressive` | Execution Protocol + Berserker's Fury |
| **Survivor** | `sustain`, `control` | Crowd Control (sustain via space) |
| **Skirmisher** | `mobile`, `aggressive` | Predator's Dance |
| **Terror** | `control`, `dot`, `aoe` | Crowd Control + Area Denial |
| **Assassin** | `execute`, `glass` | Glass Cannon Mastery + Execution Protocol |
| **Berserker** | `aggressive`, `aoe`, `momentum` | Berserker's Fury + Momentum Demon |

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Immediate Caps (Low Risk)
- [ ] Cap `quick_strikes` at 2 stacks (80% max)
- [ ] Cap `swift_wings` at 2 stacks (60% max)
- [ ] Cap `thick_carapace` at 2 stacks (100 HP max)
- [ ] Cap `critical_sting` at 2 stacks (50% max)
- [ ] Cap `raw_power` at 5 stacks (200% max)
- [ ] Add decay to `momentum` (5%/s without kills)

### Phase 2: Defense Rework (Medium Risk)
- [ ] Remove `regeneration` entirely
- [ ] Add `predators_hunger` (kill healing, resets on damage)
- [ ] Rework `hardened_shell` → movement-conditional DR
- [ ] Rework `last_stand` → speed/damage instead of DR
- [ ] Rework `second_wind` → combo-gated revive
- [ ] Nerf `lifesteal` to 8% with 5 HP/hit cap

### Phase 3: Combo System (Medium Risk)
- [ ] Add combo tags to all abilities
- [ ] Implement combo detection logic
- [ ] Add combo unlock announcements
- [ ] Add combo hints to upgrade selection UI

### Phase 4: New Abilities (Higher Risk)
- [ ] Implement `blood_price` (sustain + increased damage taken)
- [ ] Implement `adrenaline_surge` (post-damage speed burst)
- [ ] Implement `hollow_carapace` (1 HP glass cannon)

---

## TESTING SCENARIOS

### Scenario 1: Tank Build (Should Feel Weaker)
Player takes: thick_carapace x2, hardened_shell, lifesteal, adrenaline_surge

**Before**: 325 HP, 40% DR, 25% lifesteal = near immortal
**After**: 200 HP, 25% DR while moving, 8% lifesteal capped = must play well

### Scenario 2: Glass Cannon (Should Feel Riskier but More Rewarding)
Player takes: glass_cannon, hollow_carapace, raw_power x3

**Before**: 60 HP, 2.5x damage = risky but manageable
**After**: 1 HP, 5.5x damage = one mistake = death, but incredible power

### Scenario 3: Balanced Build (Should Remain Viable)
Player takes: raw_power x2, swift_wings, predators_hunger, sweeping_arc

**Before**: Generalist, okay at everything
**After**: Unlocks "Hybrid Vigor" (+5% all stats), still generalist but with identity

---

## APPENDIX: FULL ABILITY LIST (POST-REBALANCE)

### DAMAGE (5)
| ID | Name | Effect | Stacks | Tags |
|----|------|--------|--------|------|
| raw_power | Raw Power | +40% damage | 5 (200%) | aggressive |
| venomous_strike | Infectious Poison | 2.5% max HP/s per stack, spreads | 1 | control, dot |
| double_strike | Double Strike | 35% double hit | 1 | aggressive, rng |
| savage_blow | Savage Blow | +100% to <40% HP | 1 | execute, aggressive |
| giant_killer | Giant Killer | +300% to >75% HP | 1 | aggressive, opener |

### SPEED (6)
| ID | Name | Effect | Stacks | Tags |
|----|------|--------|--------|------|
| quick_strikes | Quick Strikes | +40% attack speed | 2 (80%) | aggressive, tempo |
| frenzy | Bloodrush | Kills: +15% AS for 2s, 5 stacks | 1 | aggressive, momentum 🎯 |
| swift_wings | Swift Wings | +30% move speed | 2 (60%) | mobile, evasion |
| hunters_rush | Hunter's Rush | +40% speed toward enemies | 1 | aggressive, mobile 🎯 |
| berserker_pace | Berserker Pace | +25% AS, +25% MS, -10% HP | 1 | aggressive, mobile ⚖️ |
| bullet_time | Bullet Time | Enemies 15% slower | 2 (30%) | control, evasion |

### DEFENSE (6) - REWORKED
| ID | Name | Effect | Stacks | Tags |
|----|------|--------|--------|------|
| thick_carapace | Thick Carapace | +50 max HP | 2 (100) | tank, passive |
| hardened_shell | Momentum Shield | -25% damage while moving | 1 | tank, mobile 🎯 |
| predators_hunger | Predator's Hunger | Kills heal 3%, resets on damage | 1 | sustain, aggressive 🎯 |
| blood_price | Blood Price | Heal 15% dealt, take 20% more | 1 | sustain, glass ⚖️ |
| adrenaline_surge | Adrenaline Surge | Post-damage: +60% speed 1.5s | 1 | mobile, reactive 🎯 |
| lifesteal | Lifesteal | Heal 8% dealt, cap 5/hit | 1 | sustain, aggressive |

### SPECIAL (11)
| ID | Name | Effect | Stacks | Tags |
|----|------|--------|--------|------|
| critical_sting | Critical Sting | 25% crit chance | 2 (50%) | aggressive, rng |
| execution | Execution | Instant kill <15% HP | 1 | execute, aggressive |
| sweeping_arc | Sweeping Arc | 360° attacks | 1 | aoe, control |
| chain_lightning | Chain Lightning | +1 chain bounce | 5 | aoe, aggressive |
| momentum | Momentum | +10%/kill, max 50%, decays | 1 | momentum, aggressive 🎯 |
| glass_cannon | Glass Cannon | +100% damage, -50% HP | 1 | glass, aggressive ⚖️ |
| graze_frenzy | Graze Frenzy | Near-miss stacks, hit resets | 1 | glass, evasion 🎯 |
| thermal_momentum | Thermal Momentum | Move=heat, stop=pulse | 1 | mobile, aoe 🎯 |
| execution_chain | Execution Chain | Low-HP kill chains | 1 | execute, aoe 🎯 |
| glass_cannon_mastery | GC Mastery | 1 HP, 500% dmg, 50% speed | 1 | glass, aggressive ⚖️ |
| venom_architect | Venom Architect | ∞ venom, explode on kill | 1 | dot, aoe 🎯 |

---

## SUMMARY

### Key Changes
1. **Passive sustain removed** - No more free HP regen
2. **Defense is skill-gated** - DR requires movement, healing requires not getting hit
3. **Stacks are capped** - No more 150% attack speed or 120% move speed
4. **Risk-reward options added** - blood_price, hollow_carapace for high-skill players
5. **Combo system introduced** - Tags enable emergent build identity
6. **Archetypes have clear paths** - Each archetype has natural combo synergies

### Expected Outcomes
- Tank builds require skill (movement, kill streaks)
- Glass cannon builds are viable but punishing
- Mixed builds get "Hybrid Vigor" identity
- Players discover combos organically
- Skill ceiling raised significantly
- "I can't die" builds eliminated

---

*"The predator earns every moment of survival."*
