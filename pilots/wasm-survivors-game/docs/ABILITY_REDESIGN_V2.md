# Ability Redesign v2: The "Useless → Godlike" Philosophy

**Date**: 2025-12-30
**Status**: Draft
**Philosophy**: Stack weird tricks until you break the game

---

## Core Design Principles

### 1. NO STAT STICKS
❌ "+50% damage" - Boring, doesn't change play
✅ "Kills explode" - Changes how you position

### 2. NO DEFENSE
The hornet is glass. You get hit, you feel it. Play better.
- No damage reduction
- No passive healing
- No shields
- Maybe 1-2 weird "not-quite-defense" things (like brief immunity AFTER a kill)

### 3. WEAK BASE → GODLIKE CEILING
- Base attack: Slow, short range, low damage
- With 5 upgrades: Starting to feel competent
- With 10 upgrades: Powerful
- With 15+ upgrades: Absurd death machine

### 4. EVERY ABILITY IS SPICY
Each ability should make you go "ooh, what does THAT do?"
Not "oh, bigger numbers."

### 5. ABILITIES COMPOSE
A alone = small effect
B alone = small effect
A + B together = emergent combo neither describes

---

## The New Ability Pool

### Category: ATTACK MODIFIERS (How your bite works)

| ID | Name | Effect | Juice | Stacks? |
|----|------|--------|-------|---------|
| `chain` | Chain Bite | Kills jump to nearest enemy (1 bounce) | Lightning arc visual | +1 bounce/stack |
| `explode` | Death Burst | Kills explode for 30% damage in small radius | Boom + particles | +radius/stack |
| `pierce` | Pierce | Attack continues through first target | Slash trail | +1 target/stack |
| `echo` | Echo Strike | 0.2s after attacking, attack repeats at 50% damage | Ghost mandible visual | +1 echo/stack |
| `mark` | Hunter's Mark | First hit marks enemy. Marked enemies take 2x from you. | Glowing target | Marks last longer |
| `bleed` | Hemorrhage | Hits cause bleed (2% HP/s for 3s) | Blood drip particles | +1% HP/s per stack |
| `shatter` | Shatter | Enemies below 20% HP explode on hit | Glass break effect | +5% threshold |

### Category: ATTACK SPEED/RHYTHM (When you can bite)

| ID | Name | Effect | Juice | Stacks? |
|----|------|--------|-------|---------|
| `frenzy` | Blood Frenzy | Each kill reduces next attack cooldown by 20% (resets after 2s no kill) | Red pulse on kill | +10% per stack |
| `quickdraw` | Quick Draw | First attack after moving is instant | Blur effect | N/A (binary) |
| `relentless` | Relentless | No attack cooldown for 1s after killing 3+ enemies quickly | Time slow visual | +0.5s duration |
| `heartbeat` | Heartbeat | Attack to a rhythm - hitting on beat = 2x damage, off beat = 0.5x | Pulse indicator | Beat window wider |

### Category: MOVEMENT (How moving helps you kill)

| ID | Name | Effect | Juice | Stacks? |
|----|------|--------|-------|---------|
| `afterimage` | Afterimage | Moving leaves damaging trail (5 DPS) | Ghost trail | +DPS per stack |
| `dive` | Dive Bomb | Double-tap direction = dash that damages on contact | Impact crater | +damage per stack |
| `orbit` | Orbital Strike | Circling an enemy charges up a bonus hit | Orbit ring visual | +damage per stack |
| `momentum` | Momentum | Damage scales with how fast you're moving (up to +50%) | Speed lines | +max% per stack |
| `blink` | Phase Shift | Dash through enemies damages them | Distortion effect | +damage per stack |

### Category: ON-KILL EFFECTS (Rewards for murder)

| ID | Name | Effect | Juice | Stacks? |
|----|------|--------|-------|---------|
| `nova` | Death Nova | Every 5th kill releases damaging pulse | Expanding ring | Every 4th, 3rd... |
| `feast` | Feast | Kills drop meat that heals 1 HP (must collect) | Meat chunk bounce | +HP per meat |
| `fear` | Terror | Kills cause nearby enemies to flee for 1s | Fear lines on enemies | +range, +duration |
| `magnet` | Soul Magnet | Kills pull nearby enemies toward death point | Vortex effect | +pull strength |
| `chain_react` | Chain Reaction | If a kill triggers another kill within 0.5s, +25% damage | Lightning chain | +% per stack |

### Category: WEIRD/UTILITY (Strange tricks)

| ID | Name | Effect | Juice | Stacks? |
|----|------|--------|-------|---------|
| `poison_cloud` | Miasma | Standing still creates growing poison cloud | Green fog | +radius/DPS |
| `clone` | Decoy | Getting hit spawns decoy that enemies target for 2s | Flickering copy | +decoy duration |
| `gravity` | Gravity Well | Enemies near you move 20% slower | Distortion field | +slow% |
| `thorns` | Thorns | Enemies that hit you take 50% of the damage back | Spike burst | +reflect% |
| `last_gasp` | Last Gasp | At 1 HP: immune for 0.5s, next kill heals to 25% | Red flash, slow-mo | +heal% |
| `glass_soul` | Glass Soul | Max HP = 50. Damage = 3x. | Crystalline visual | N/A |

### Category: SCALING/SNOWBALL (Get stronger as you kill)

| ID | Name | Effect | Juice | Stacks? |
|----|------|--------|-------|---------|
| `rampage` | Rampage | +5% damage per kill this wave (resets each wave) | Stacking fire aura | +% per kill |
| `evolve` | Evolve | Every 50 kills, permanently +10% damage | Evolution flash | Lower threshold |
| `absorb` | Absorb | Killing elites grants their speed/damage briefly | Color drain effect | +duration |
| `trophy` | Trophy Hunter | Each enemy TYPE killed first = +5% permanent damage | Trophy notification | N/A |

---

## Removed / Banned Concepts

### ❌ REMOVED ENTIRELY

| Old Ability | Why Removed |
|-------------|-------------|
| `raw_power` (+50% damage) | Boring stat stick |
| `quick_strikes` (+50% AS) | Boring stat stick |
| `swift_wings` (+40% MS) | Boring stat stick |
| `thick_carapace` (+75 HP) | Defense, boring |
| `hardened_shell` (-40% DR) | Defense, boring |
| `regeneration` (+5 HP/s) | Defense, passive |
| `lifesteal` (25%) | Defense, too reliable |
| `last_stand` (+90% DR low) | Defense, makes low HP safe |
| `second_wind` (revive) | Defense, removes stakes |
| `critical_sting` (30% crit) | Boring RNG stat |
| `berserker_pace` | "+both stats" = boring |
| `bullet_time` | Defensive utility |

### ❌ BANNED DESIGN PATTERNS

| Pattern | Why Banned |
|---------|------------|
| "+X% [stat]" alone | Doesn't change play |
| "While moving, +X" | You're always moving, it's just +X |
| "Below X% HP, bonus" | Encourages staying low = defense |
| Passive damage reduction | Removes need for skill |
| Passive healing | Removes need for skill |
| "Chance to X" without player control | RNG isn't satisfying |

---

## How Stacking Creates God Mode

### Example Build: "The Blender"

**Abilities taken:**
1. `chain` (kills bounce)
2. `explode` (kills explode)
3. `frenzy` (kills speed up attacks)
4. `relentless` (multi-kills = no cooldown)
5. `chain_react` (chained kills = bonus damage)

**At 1 kill:** You kill one bee. It explodes. Deals small damage to nearby bee.

**At 3 kills:** You're attacking faster from frenzy. Explosions are chaining. chain_react is proccing.

**At 10 kills:** You haven't stopped attacking. Relentless is active. Everything is exploding into everything else. Screen is chaos.

**At 30 kills:** You are a localized apocalypse. Bees die from being near other bees dying.

### Example Build: "The Surgeon"

**Abilities taken:**
1. `mark` (first hit = 2x damage on target)
2. `shatter` (low HP enemies explode)
3. `quickdraw` (instant attack after moving)
4. `pierce` (attack goes through)
5. `echo` (attack repeats)

**Playstyle:** Mark a target, reposition, quickdraw through them with pierce+echo. They shatter. Repeat.

**At 1 kill:** Satisfying execution combo.

**At 10 kills:** You're surgically removing priority targets.

**At 30 kills:** The battlefield is controlled demolition.

### Example Build: "The Plague"

**Abilities taken:**
1. `bleed` (DoT)
2. `poison_cloud` (standing = AoE DoT)
3. `fear` (kills scatter enemies)
4. `magnet` (kills pull enemies)
5. `nova` (periodic damage pulse)

**Playstyle:** Infect, watch them run, watch them get pulled back, repeat.

**At 1 kill:** Single enemy bleeding out.

**At 10 kills:** Half the screen is poisoned.

**At 30 kills:** The hive is a plague zone. They can't escape.

---

## Base Stats: The Nerf

For abilities to feel transformative, base must be weak:

| Stat | Current | Proposed | Why |
|------|---------|----------|-----|
| Attack Damage | 25 | 15 | Needs abilities to kill efficiently |
| Attack Speed | 2/sec | 1.2/sec | Frenzy/relentless feel better |
| Attack Range | 50px | 40px | Dive/blink feel necessary |
| Move Speed | 200 | 180 | Momentum/afterimage matter more |
| Max HP | 100 | 75 | Glass cannon by default |
| HP Regen | 0 | 0 | N/A |
| Dash Cooldown | 2s | 3s | Abilities should enhance |
| Dash Distance | 120px | 100px | Blink upgrade feels good |

**With these nerfs:**
- Wave 1-2: You struggle. You need upgrades.
- Wave 3-4: First abilities come online. You're competent.
- Wave 5-6: Build identity emerges. You feel powerful.
- Wave 7+: Godlike. But still glass. One mistake = death.

---

## The One "Defense" Exception: Feast

`feast` is the only sustain, and it's skill-gated:

- Kills drop meat
- Meat heals 1-2 HP
- You must COLLECT it (position into danger)
- It despawns quickly
- With many stacks: 3-4 HP per meat

This creates gameplay: "Do I grab that meat or play safe?"

**NOT defense because:**
- Requires kills (offense)
- Requires positioning (skill)
- Doesn't prevent damage
- Creates risk decisions

---

## The "Almost Defense" Abilities

These look like defense but aren't:

| Ability | Why It's Not Defense |
|---------|---------------------|
| `clone` (decoy on hit) | You already got hit. Doesn't prevent damage. |
| `thorns` (reflect damage) | You already got hit. Punishes attacker. |
| `last_gasp` (1 HP save) | Happens once. Then you're at 25% HP in danger. |
| `glass_soul` (50 HP, 3x damage) | LESS HP. It's offense. |

---

## Combo Examples (Emergent)

These aren't coded - they emerge from ability interactions:

| Combo | Abilities | Emergent Effect |
|-------|-----------|-----------------|
| "Cascade" | chain + explode | Each chain bounce explodes, which can chain more |
| "Bloodbath" | bleed + fear + magnet | Bleeding enemies flee, get pulled back, flee again (CC loop) |
| "One Punch" | mark + echo + shatter | Mark → Echo hits → Both deal 2x → Target shatters |
| "The Floor is Lava" | afterimage + momentum + dive | High-speed movement = death zone behind you |
| "Reaper" | frenzy + relentless + rampage | Kill streaks = exponential attack speed + damage |
| "Patient Zero" | bleed + nova + chain_react | DoT spreads, novas trigger, chain reacts compound |

---

## Upgrade Presentation: Make It Spicy

### Current (Boring)
```
┌─────────────────────┐
│ Quick Strikes       │
│ +50% attack speed   │
│                     │
└─────────────────────┘
```

### Proposed (Spicy)
```
┌─────────────────────────────────────┐
│ ⚡ ECHO STRIKE                      │
│                                     │
│ "Your mandibles leave ghosts"       │
│                                     │
│ After biting, a phantom bite        │
│ follows 0.2s later at half damage.  │
│                                     │
│ [Preview: ghost mandible animation] │
└─────────────────────────────────────┘
```

Each upgrade card should:
1. Have a flavorful name
2. One evocative sentence
3. Clear mechanical description
4. Preview of the visual effect

---

## Implementation Priority

### Phase 1: Remove the Boring
- [ ] Delete all "+X% stat" abilities
- [ ] Delete all passive defense
- [ ] Delete all "while X" fake conditionals

### Phase 2: Add the Spicy
- [ ] Implement chain (bouncing kills)
- [ ] Implement explode (death bursts)
- [ ] Implement echo (phantom attacks)
- [ ] Implement afterimage (movement trails)
- [ ] Implement frenzy (kill-based attack speed)

### Phase 3: Nerf the Base
- [ ] Reduce base damage 25 → 15
- [ ] Reduce attack speed 2/s → 1.2/s
- [ ] Reduce range 50px → 40px
- [ ] Reduce HP 100 → 75
- [ ] Increase dash cooldown 2s → 3s

### Phase 4: Juice Everything
- [ ] Each ability gets unique visual effect
- [ ] Each ability gets sound effect
- [ ] Combo triggers get announcements
- [ ] Kill streaks get escalating feedback

---

## Summary

### Old Philosophy
"Stack stats until numbers are big"

### New Philosophy
"Stack weird tricks until physics breaks"

### The Feeling
- **Wave 1**: "I'm so weak, I need something"
- **Wave 3**: "Okay, echo strike is cool"
- **Wave 5**: "Wait, echo + chain means..."
- **Wave 7**: "EVERYTHING IS EXPLODING"
- **Wave 9**: "I AM BECOME DEATH"
- **Wave 10**: "...and I still died in one hit lmao"

---

*"The predator doesn't tank hits. The predator doesn't survive damage. The predator kills everything before it matters."*
