# Ability Redesign v3: Small Tricks, Big Stacks

**Date**: 2025-12-30
**Philosophy**: 15 small weird things = one god

---

## Design Axioms

### 1. NO ABILITY IS ESSENTIAL
If removing any single ability makes the game unplayable, it's too strong.
Each ability = ~5-10% toward godlike. You need MANY.

### 2. NO ABILITY IS GAME-WARPING
"Chain kills bounce" warps the game around it.
"Kills have 15% chance to spark nearby" does not.

### 3. EVERY ABILITY IS THEMATIC
Draw from real hornet/bee biology. The theme IS the mechanic.

### 4. STACKING IS THE GAME
- 3 abilities: "Hmm, that's kinda cool"
- 8 abilities: "Okay I see where this is going"
- 15 abilities: "I AM THE SWARM'S NIGHTMARE"

---

## The Ability Pool: 36 Small Tricks

### 🦷 MANDIBLE TECHNIQUES (How your bite works)

| # | Name | Effect | Juice | Theme Source |
|---|------|--------|-------|--------------|
| 1 | **Serration** | Bites leave tiny bleed (1% HP over 2s) | Red tick marks | Hornet mandible ridges |
| 2 | **Scissor Grip** | 10% chance bite holds enemy still for 0.3s | Grabbing animation | Decapitation grip |
| 3 | **Chitin Crack** | Bites reduce enemy armor by 5% (stacks) | Crack visual on enemy | Exoskeleton damage |
| 4 | **Resonant Strike** | Bites create tiny vibration (5px knockback) | Ripple effect | Wing vibration physics |
| 5 | **Sawtooth** | Every 5th bite deals +30% damage | Glint on 4th hit | Mandible serration |
| 6 | **Nectar Sense** | Bites on full-HP enemies mark them (visible through fog) | Faint glow outline | Hornet target marking |

### 💜 VENOM ARTS (Poison and debuffs)

| # | Name | Effect | Juice | Theme Source |
|---|------|--------|-------|--------------|
| 7 | **Trace Venom** | Attacks apply 0.5% slow (stacks to 15%) | Purple tint deepens | Neurotoxin effects |
| 8 | **Lingering Sting** | Damaged enemies stay damaged 1s longer before healing | Purple timer icon | Venom persistence |
| 9 | **Melittin Traces** | Poisoned enemies take +5% damage from all sources | Faint purple aura | Melittin compound |
| 10 | **Pheromone Tag** | Damaged enemies attract 10% of nearby damage to themselves | Scent lines visual | Alarm pheromone |
| 11 | **Paralytic Micro-dose** | 3% chance attacks cause 0.2s freeze | Brief purple flash | Paralytic venom |
| 12 | **Histamine Burst** | Enemies you damage move 5% faster (but take 8% more damage) | Jittery animation | Histamine reaction |

### 🪽 WING MASTERY (Movement creates effects)

| # | Name | Effect | Juice | Theme Source |
|---|------|--------|-------|--------------|
| 13 | **Draft** | Moving near enemies pulls them slightly toward your path | Air disturbance lines | Wing turbulence |
| 14 | **Buzz Field** | Standing still for 0.5s creates 20px damage aura (2 DPS) | Vibrating circle | Defensive buzzing |
| 15 | **Thermal Wake** | Moving leaves warmth trail. Enemies in trail move 5% slower | Heat shimmer | Hornet body heat |
| 16 | **Scatter Dust** | Dashing kicks up particles that briefly (0.3s) obscure enemy vision | Pollen puff | Wing-disturbed pollen |
| 17 | **Updraft** | Kills give you +3% move speed for 1s | Brief lift animation | Thermal riding |
| 18 | **Hover Pressure** | Being near enemies (50px) deals 1 DPS to them | Pressure wave visual | Wing pressure |

### 💀 PREDATOR INSTINCTS (Kill triggers)

| # | Name | Effect | Juice | Theme Source |
|---|------|--------|-------|--------------|
| 19 | **Feeding Efficiency** | Kills give +2% attack speed for 3s (stacks 5x) | Speed lines | Hunting metabolism |
| 20 | **Territorial Mark** | Where enemies die, you deal +10% damage for 2s | Ground stain | Scent marking |
| 21 | **Trophy Scent** | Each unique enemy type killed = +1% permanent damage | Trophy flash | Species tracking |
| 22 | **Pack Signal** | Kills cause nearby enemies to hesitate 0.1s | Fear ripple | Predator presence |
| 23 | **Corpse Heat** | Standing on recent kills grants +5% damage for 1s | Heat wisps | Body heat |
| 24 | **Clean Kill** | Enemies killed in one hit explode in tiny radius (10px, 5 dmg) | Mini pop | Efficient predation |

### 🧪 PHEROMONE WARFARE (Area denial)

| # | Name | Effect | Juice | Theme Source |
|---|------|--------|-------|--------------|
| 25 | **Threat Aura** | Enemies within 30px deal 5% less damage | Faint orange glow | Intimidation pheromones |
| 26 | **Confusion Cloud** | Getting hit releases cloud. Enemies in cloud have 10% miss chance | Swirling particles | Alarm interference |
| 27 | **Rally Scent** | Your trail (last 2s of movement) makes enemies 5% slower | Fading path line | Territorial marking |
| 28 | **Death Marker** | Corpses emit field (15px) that slows enemies 10% for 3s | Seeping effect | Death pheromones |
| 29 | **Aggro Pulse** | Every 10s, pulse that makes enemies target you for 1s | Expanding ring | Queen pheromone |
| 30 | **Bitter Taste** | Enemies that damage you deal 10% less for 2s | Grimace VFX on enemy | Chemical deterrent |

### 🛡️ CHITIN ADAPTATIONS (Body modifications - NOT defense!)

| # | Name | Effect | Juice | Theme Source |
|---|------|--------|-------|--------------|
| 31 | **Barbed Chitin** | Enemies that touch you take 3 damage | Tiny spike visual | Defensive spines |
| 32 | **Ablative Shell** | First hit each wave deals -20% damage | Shell fragment flies off | Exoskeleton layer |
| 33 | **Heat Retention** | You move 5% faster when below 50% HP | Red heat aura | Metabolic heat |
| 34 | **Compound Eyes** | See enemy attack telegraphs 0.1s earlier | Wider vision cone | Multi-faceted vision |
| 35 | **Antenna Sensitivity** | Enemies highlighted 0.5s before entering screen | Edge glow warning | Antenna detection |
| 36 | **Molting Burst** | At 10% HP, once per run: brief invuln + small damage burst | Shedding animation | Emergency molt |

---

## Removed Concepts (Too Essential/Game-Warping)

| Concept | Why Removed |
|---------|-------------|
| "Kills chain to nearest" | Game-warping - changes entire playstyle |
| "Kills explode in AoE" | Game-warping - trivializes crowds |
| "Attack repeats (echo)" | Essential - too much value in one pick |
| "Instant kill threshold" | Game-warping - execute builds dominate |
| "Full heal on condition" | Defense disguised as offense |
| "Invulnerability window" | Defense |
| "Damage reduction %" | Defense |
| "Passive HP regen" | Defense |
| "Revive mechanic" | Defense - removes stakes |
| "+50% damage" flat | Boring, too strong |
| "+50% attack speed" flat | Boring, too strong |
| "Multi-shot/pierce" | Game-warping - changes attack fundamentally |

---

## How Small Becomes Godlike

### Example: "The Bleeder" (12 abilities)

**Abilities:**
1. Serration (1% HP bleed)
2. Chitin Crack (5% armor reduction per hit)
3. Melittin Traces (+5% damage to poisoned)
4. Trace Venom (0.5% slow stacking)
5. Feeding Efficiency (+2% AS on kill)
6. Territorial Mark (+10% in kill zones)
7. Trophy Scent (+1% per type)
8. Thermal Wake (5% slow trail)
9. Death Marker (corpse slow field)
10. Histamine Burst (+8% damage taken)
11. Sawtooth (every 5th = +30%)
12. Corpse Heat (+5% on kill spots)

**Wave 3 (3 abilities):** "I have some bleed and a bit of slow. Okay."

**Wave 6 (7 abilities):** "Enemies are getting stacked with debuffs. They're slower, taking more damage, and I'm faster after kills."

**Wave 9 (12 abilities):** "The battlefield is a web of death zones. Every corpse slows. Every hit stacks. I'm 15% faster from kills, they're 15% slower from venom, and taking 13% extra damage from Melittin+Histamine. My 5th hits are devastating."

**The Math:**
- Base damage: 15
- Territorial (+10%) + Corpse Heat (+5%) + Trophy (assume +5%) + Histamine (+8%) + Melittin (+5%) = +33%
- Every 5th hit: +30% more
- Effective DPS increase from speed: +10%
- Enemy effective HP reduced by: armor debuff + slows meaning more hits land

**No single ability is broken. Together = apex predator.**

---

### Example: "The Pressure" (10 abilities)

**Abilities:**
1. Hover Pressure (1 DPS near enemies)
2. Buzz Field (2 DPS standing still)
3. Threat Aura (enemies deal -5%)
4. Draft (pull enemies toward path)
5. Thermal Wake (slow trail)
6. Rally Scent (slow in your trail)
7. Death Marker (corpse slows)
8. Resonant Strike (tiny knockback)
9. Pack Signal (hesitation on kill)
10. Compound Eyes (see telegraphs early)

**Playstyle:** You're a mobile hazard zone. Not high burst, but constant pressure. Enemies are always slightly slowed, slightly pulled, slightly damaged just by being near you. You see attacks coming, you push them around, and they can't escape your influence.

**No ability here is strong alone. A 1 DPS aura is nothing. 2 DPS for standing still is worse than attacking. But layered...**

---

## Stack Scaling Philosophy

### Individual Ability Power

| Stacks | Effect Size | Feeling |
|--------|-------------|---------|
| 1-3 | +5-15% each | "Neat" |
| 4-7 | Combinations emerge | "I see the synergy" |
| 8-12 | System is humming | "This is my build" |
| 13-18 | Overwhelming | "I am death" |
| 18+ | Absurd | "Physics is optional" |

### Why This Works

**Old system:** Each ability = significant. 5 abilities = broken.

**New system:** Each ability = marginal. 5 abilities = baseline competence. 15 abilities = broken (as intended).

The FUN is in the accumulation. Each upgrade is a small "ooh" that builds toward "HOLY SHIT."

---

## Visual Juice Per Ability

Every ability needs clear feedback:

| Ability | Visual | Audio |
|---------|--------|-------|
| Serration | Red scratch marks | Tiny "shik" |
| Scissor Grip | Enemy jolts, held | Crunch |
| Trace Venom | Purple tint accumulates | Wet sizzle |
| Draft | Air distortion lines | Whoosh |
| Buzz Field | Vibrating circle | Low hum |
| Thermal Wake | Heat shimmer trail | Hiss |
| Feeding Efficiency | Speed lines on kill | Tempo increase |
| Territorial Mark | Ground stain | Splat |
| Death Marker | Seeping purple | Ooze sound |
| Barbed Chitin | Tiny spike flash | Plink |

**Rule: If you can't see/hear it working, it's not juicy enough.**

---

## Implementation Approach

### Phase 1: Gut the Old System
- Remove ALL flat stat bonuses (+X% damage, +X% speed)
- Remove ALL defense abilities
- Remove ALL "game-warping" abilities (chain, explode, pierce, execute)

### Phase 2: Implement Core 12
Start with one ability from each category, plus extras:
1. Serration (Mandible)
2. Trace Venom (Venom)
3. Thermal Wake (Wing)
4. Feeding Efficiency (Predator)
5. Death Marker (Pheromone)
6. Barbed Chitin (Chitin)
7. Chitin Crack (Mandible)
8. Melittin Traces (Venom)
9. Draft (Wing)
10. Territorial Mark (Predator)
11. Threat Aura (Pheromone)
12. Compound Eyes (Chitin)

### Phase 3: Add Remaining 24
Fill out pool to full 36, ensuring:
- No ability overlaps another's function
- Each has unique visual/audio
- Stacking math is validated

### Phase 4: Tune Base Stats
Weaken base so upgrades matter:
- Base damage: 15 → 12
- Base attack speed: 1.2/s → 1.0/s
- Base move speed: 180 → 160

---

## Quick Reference: The 36 Abilities

### Mandible (6)
Serration, Scissor Grip, Chitin Crack, Resonant Strike, Sawtooth, Nectar Sense

### Venom (6)
Trace Venom, Lingering Sting, Melittin Traces, Pheromone Tag, Paralytic Micro-dose, Histamine Burst

### Wing (6)
Draft, Buzz Field, Thermal Wake, Scatter Dust, Updraft, Hover Pressure

### Predator (6)
Feeding Efficiency, Territorial Mark, Trophy Scent, Pack Signal, Corpse Heat, Clean Kill

### Pheromone (6)
Threat Aura, Confusion Cloud, Rally Scent, Death Marker, Aggro Pulse, Bitter Taste

### Chitin (6)
Barbed Chitin, Ablative Shell, Heat Retention, Compound Eyes, Antenna Sensitivity, Molting Burst

---

## The Feeling

**Wave 1:** "I have Serration. Enemies bleed a tiny bit. Cool I guess."

**Wave 3:** "Added Trace Venom and Feeding Efficiency. Now they're slow AND I'm fast after kills."

**Wave 5:** "Chitin Crack, Melittin Traces, Territorial Mark. Enemies are debuffed, taking extra damage, and my kill zones are dangerous."

**Wave 7:** "Draft, Thermal Wake, Death Marker. The entire arena is my domain. They can't escape my influence."

**Wave 9:** "12 abilities deep. Every system is stacked. Bleeds, slows, damage amps, speed buffs, pressure auras. I'm not fighting them. They're drowning in my presence."

**Wave 10+:** "I don't attack enemies. I exist near them and they dissolve."

---

*"The hornet doesn't need one big weapon. The hornet IS the weapon, refined through a thousand small adaptations."*
