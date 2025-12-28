# Wasm Survivors: Witnessed Run Lab

Status: proto-spec (v2 — Enlightened Edition)

> *"After two waves, you realize: they're not individuals. They're a hive mind. And they're learning."*

## Narrative

A chaotic arcade roguelike where survival is the tutorial and mastery is the destination—but the enemies are learning too. The game teaches through play—each death clarifies, each upgrade reshapes how you move and fight, each run deposits skill that carries forward.

**The twist**: The enemies aren't obstacles. They're a collective intelligence racing to metamorphose before you kill them. Let them live too long, and they combine into **Colossals**—mega-enemies with movesets no individual could perform.

You don't just fight enemies. You fight a hive mind. And it's watching.

## Personality Tag

*This pilot believes the best games make you better at them AND adapt to you getting better. Upgrades feel like superpowers. Enemies feel like puzzles. Death feels like a lesson. The hive feels like a mirror.*

## Objectives

- Create a survivors-like where **player skill matters as much as build RNG**—dodging, positioning, and timing should always be viable.
- Design **upgrades that change how you play**, not just numbers that go up. Each upgrade is a verb, not a noun.
- Design **enemies as a collective intelligence**—individually learnable, collectively adaptive. Every enemy type is a skill check; the hive is the final exam.
- Ensure **every run makes the player better**—AND the game adapts to that improvement through hive learning.
- Create **metamorphosis pressure**—kill fast or watch basic enemies become boss-tier Colossals.

---

## Core Pillars

### 1. Movement is Life

> *"A skilled player with no upgrades should survive longer than a lucky player with great upgrades."*

Movement is the primary skill expression. The game must reward:
- **Kiting**: Leading enemies into favorable positions
- **Dodging**: Weaving through projectiles and melee swings
- **Positioning**: Choosing where to fight (corners vs. open space)
- **Tempo**: Knowing when to engage vs. disengage

**Movement Laws:**
- **M1 Responsive**: < 16ms input-to-movement. WASD must feel *tight*.
- **M2 No Stun-Lock**: Player can always move. Damage slows but never stops.
- **M3 Speed Matters**: Base speed is fast enough to outrun basic enemies. Upgrades can make you *fly*.
- **M4 Spatial Reads**: Enemy attacks are telegraphed. Skilled players dodge; unskilled players tank.

### 2. Upgrades Transform Play

> *"If an upgrade doesn't change how I play, it's not an upgrade—it's inflation."*

Every upgrade should feel like acquiring a new ability, not incrementing a stat.

**Upgrade Design Laws:**
- **U1 Verb, Not Noun**: Upgrades change *what you do*, not just *how much damage*. "Shots pierce" > "+10% damage".
- **U2 Build Identity**: By wave 5, the player should be able to name their build. "I'm playing pierce-orbit" or "I'm doing melee-dash".
- **U3 Synergy Moments**: 2+ upgrades combine for emergent power. 1+1 > 2 somewhere. The "aha!" of discovery.
- **U4 Meaningful Choice**: Every level-up presents a real decision. No obvious best pick. Different builds want different things.
- **U5 Visual Transformation**: Upgrades visibly change how you look/act. The screen should *look different* at wave 10 vs wave 1.

**Upgrade Archetypes** (each run should support multiple):

| Archetype | Fantasy | Example Upgrades |
|-----------|---------|------------------|
| **Glass Cannon** | High risk, high reward | +damage, -health, critical strikes |
| **Tank** | Slow and steady | +health, +regen, thorns damage |
| **Speed Demon** | Never stop moving | +move speed, +fire rate, dash cooldown |
| **Orbit Master** | Defensive zone control | Orbitals, shields, area denial |
| **Sniper** | Precision over volume | Pierce, +range, slow fire, high damage |
| **Summoner** | Army of minions | Drones, turrets, companion spawns |

### 3. Enemies Are a Hive Mind

> *"Every enemy is a question. The hive is the final exam."*

Enemies are not HP bags—they're skill checks with personalities. But they're also **nodes in a collective intelligence** that races to evolve before you can stop it.

**Enemy Design Laws:**
- **E1 Readable Tells**: Every attack is telegraphed. Wind-up animations, audio cues, ground markers.
- **E2 Learnable Patterns**: Enemy behavior is consistent. Same enemy, same patterns. Mastery is possible.
- **E3 Distinct Silhouettes**: Know the enemy type instantly from shape/color. No confusion in chaos.
- **E4 Escalating Threat**: Basic enemies teach fundamentals. Elites combine patterns. **Colossals demand mastery.**
- **E5 Fair Deaths**: Every death is attributable. "I died because I let them combine."

**Enemy Archetypes**:

| Type | Behavior | Teaches | Colossal Form |
|------|----------|---------|---------------|
| **Shambler** | Walks toward player | Basic kiting | THE TIDE (unstoppable wave) |
| **Rusher** | Charges in straight line | Sidestep timing | THE RAMPAGE (perpetual motion) |
| **Spitter** | Ranged projectiles | Projectile dodging | THE ARTILLERY (arena control) |
| **Tank** | Slow, high HP, big damage | Prioritization | THE FORTRESS (siege warfare) |
| **Swarm** | Many weak enemies | AoE value, crowd management | THE LEGION (coordinated multiplicity) |

---

### 4. The Metamorphosis System

> *"Kill them fast, or watch them become something you can't imagine."*

**Core Rule**: Enemies that survive long enough on screen combine into **Mutant Colossals**—mega-enemies with epic movesets that single enemies could never perform.

| Survival Time | What Happens |
|---------------|--------------|
| 0-10s | Normal behavior |
| 10-15s | **Pulsing begins**—seeking combination partners |
| 15-20s | Gravitates toward other pulsing enemies |
| 20s+ | **Metamorphosis** if 2+ pulsing enemies touch |

**Metamorphosis Laws:**
- **M1 Predictable Timer**: Players must be able to learn how long until metamorphosis
- **M2 Visual Warning**: Pulsing enemies are OBVIOUS—this is a skill test, not a trap
- **M3 Interruptible**: Killing ANY pulsing enemy resets nearby enemies' timers
- **M4 Escapable**: Colossals can be run from. Slow but powerful.
- **M5 Soloable**: Every Colossal can be killed with base stats. Skill ceiling is infinite.

**Mutant Variants**: Every spawned enemy has a chance to be a **Mutant** (glowing outline). Mutants that participate in metamorphosis make the resulting Colossal **faster**. Kill mutants first, or the Colossal will be a nightmare.

---

### 5. The Five Colossals

**THE TIDE (Shambler Colossal)**
*Theme*: Overwhelming inevitability. The thing that cannot be stopped.

| Move | Description | Counter |
|------|-------------|---------|
| Inexorable Advance | 0.5x speed but CANNOT be slowed | Kite perpendicular |
| Absorption | Absorbs nearby enemies, healing | Clear field first |
| Fission | At 25% HP, splits into 5 shamblers | Burst it down fast |
| Gravity Well | Nearby enemies accelerate toward you | Don't fight near mobs |

**THE RAMPAGE (Rusher Colossal)**
*Theme*: Unstoppable kinetic force. The thing that never stops moving.

| Move | Description | Counter |
|------|-------------|---------|
| Pinball | Bounces off walls, accelerating | Predict trajectory |
| Aftershock | Leaves damage trail during charges | Don't follow |
| Momentum Transfer | Hitting you launches you | Brace near walls |
| Redline | Below 50% HP, charge cooldown halves | Burst or run |

**THE ARTILLERY (Spitter Colossal)**
*Theme*: Ranged supremacy. The thing that controls the entire arena.

| Move | Description | Counter |
|------|-------------|---------|
| Barrage | 12 projectiles in spread | Weave through gaps |
| Mortar | Slow lob that explodes in AoE | Watch the shadow |
| Suppression | Continuous tracking fire | Break the pattern |
| Air Burst | Projectiles detonate mid-flight | Stay close (risky) |

**THE FORTRESS (Tank Colossal)**
*Theme*: Immovable defense. The thing that makes YOU come to IT.

| Move | Description | Counter |
|------|-------------|---------|
| Siege Mode | Stops moving, spawns turrets | Flank and burst |
| Quake | Ground pound damages arena | Stay far |
| Magnetize | Pulls XP orbs toward itself | Race for XP |
| Bunker | At 25% HP, invulnerable 5s + adds | DPS race |

**THE LEGION (Swarm Colossal)**
*Theme*: Coordinated multiplicity. The thing that's everywhere at once.

| Move | Description | Counter |
|------|-------------|---------|
| Scatter | Disperses into 20 micro-enemies | AoE or flee |
| Encircle | Forms constricting ring | Dash through |
| Drone Strike | 3 suicide bombers | Kite into each other |
| Hivemind | All nearby enemies gain +50% speed | Priority target |

---

### 6. Hive Intelligence

> *"They're not just combining. They're learning from each other."*

**Collective Learning**: The hive mind shares information across all active enemies.

| Behavior | Description |
|----------|-------------|
| **Pattern Propagation** | If one enemy learns your dodge pattern, ALL enemies adjust |
| **Sacrifice Awareness** | Enemies know when one is about to die—others accelerate |
| **Colossal Priority** | When a Colossal exists, lesser enemies become supports |
| **Death Knowledge** | The hive remembers which attacks killed YOU—uses them more |

**Hive Laws:**
- **H1 Fair Learning**: Hive learns from success, not failure. If you dodge it, they adapt.
- **H2 Reset Between Runs**: Hive intelligence resets each run. No cross-run punishment.
- **H3 Visible Intelligence**: HUD shows hive awareness level (subtle, not invasive)
- **H4 Counterplay Exists**: Every hive behavior has a counter. Adaptation is a puzzle.

**Visual Language of the Hive**:

| State | Visual |
|-------|--------|
| Individual | Normal behavior, isolated movement |
| Pulsing | Glowing outline, seeking combination |
| Linked | Visible energy threads between nearby enemies |
| Pre-Metamorphosis | Flash of light, bodies gravitating together |
| Colossal Active | All lesser enemies gain subtle hive glow |

### 7. Mastery Accumulates (Mutual Adaptation)

> *"Run 50 should feel different from run 1—not because of unlocks, but because of *you*. And the hive knows it."*

The player should get better at the game, not just better at builds. But now the hive is learning too.

**Mastery Laws:**
- **P1 Skill Transfer**: Skills learned in one run apply to all future runs. Dodge timing doesn't reset.
- **P2 Pattern Recognition**: Repeated play reveals enemy patterns. "I know this spawn wave."
- **P3 Build Intuition**: Experienced players know which upgrades synergize. Decision speed improves.
- **P4 Mechanical Ceiling**: High skill ceiling for movement. Speedrunners should look superhuman.
- **P5 Progress Feeling**: After 10 runs, player should *feel* more competent, even without meta-progression.
- **P6 Hive Adaptation**: The hive learns your patterns WITHIN a run. You must evolve faster than it does.

---

## Game Design Laws

### Emotional Arc (E)

- **E1 Journey Shape**: Runs traverse HOPE → FLOW → CRISIS → TRIUMPH/GRIEF. Flat emotional lines are failures.
- **E2 One More Run**: The post-death state must invite immediate retry. Friction here kills the game.
- **E3 Defeat Clarity**: Failure runs produce *clearer* feedback than victories. You must know *why* you died.
- **E4 The Revelation**: Wave 2-3 should deliver the "WHAT WAS THAT" moment—first metamorphosis, first realization that they're a hive mind.
- **E5 Mutual Stakes**: Late waves should feel like a chess match—the hive knows you, you know it, both adapting.

### Spectacle (S)

- **S1 Feedback Density**: Every player action has visual + audio response. Silent actions are lies.
- **S2 Escalation**: Juice scales with wave, combo, and stakes. Wave 10 must *look* harder than wave 1.
- **S3 Clutch Moment**: Near-death survival triggers spectacle: time-slow, zoom, bass. You *felt* that.
- **S4 Kill Satisfaction**: Enemy death is a micro-celebration. Particles, sound, XP burst—earned, not given.

### Contrast (C)

- **C1 Breath**: Crescendos require silences. After intensity peaks, spawn a recovery window.
- **C2 Scarcity Oscillation**: Feast and famine, never constant medium. Sometimes swimming in XP, sometimes starving.
- **C3 Tempo Inversion**: Fast combat → slow choices. Slow combat → fast choices. Match rhythm to inverse.
- **C4 Stakes Gradient**: Runs must visit both "invincible" and "one hit from death." Mid-range is death.
- **C5 Silence Before Storm**: Boss/elite spawn preceded by 2-4s of empty arena. Dread is a gift.

### Difficulty (D)

- **D1 Skill Expression**: Ceiling is high. Mastery should feel like flying. Floor catches but doesn't trap.
- **D2 Fair Challenge**: Difficulty comes from enemy patterns, not RNG. Skilled players can no-hit.
- **D3 Gradual Escalation**: Wave 10 is harder than wave 1, but the ramp is smooth. No cliffs.
- **D4 Recovery Possible**: Bad early game can be recovered with skill. Never truly hopeless.

---

## Fun Floor

> *"Below this line, the game isn't worth playing. Above it, we iterate."*

### Must-Haves (non-negotiable)

| Category | Requirement |
|----------|-------------|
| **Input** | < 16ms response. WASD feels *tight*. |
| **Movement** | Player can always move. No stun-lock. |
| **Kill** | Death = particles + sound + XP burst. No silent kills. |
| **Level-up** | Pause + choice + fanfare. A *moment*, not a stat bump. |
| **Death** | Readable cause. "I died because X" in < 2 seconds. |
| **Restart** | < 3 seconds from death to new run. No menus. |
| **Build identity** | By wave 5, player can name their build. |
| **Synergy** | 2+ upgrades combine for emergent power. 1+1 > 2 somewhere. |
| **Escalation** | Wave 10 is obviously harder than wave 1. Visually, sonically. |
| **Enemy variety** | At least 4 distinct enemy types with different behaviors. |
| **Upgrade variety** | At least 8 upgrades that change playstyle. |
| **Pulsing visible** | Metamorphosis timer is ALWAYS readable (visual, not numeric). |
| **Colossal telegraphs** | Every Colossal attack has long, readable wind-up. |
| **Hive awareness** | HUD shows hive intelligence level (subtle indicator). |

### Player Advocate Tests

- **5-Minute Test**: New player understands controls (30s), gets first kill (10s), feels powerful (wave 2), retries after death.
- **Mastery Test**: Player on run 10 demonstrably plays better than run 1—dodges more, positions better, chooses faster.
- **Build Test**: Two players describe their runs differently based on upgrade choices. "I went orbital" vs "I went pierce".
- **Death Test**: Player can explain every death. "I got cornered" not "I don't know what happened."
- **Streamer Test**: Someone could entertainingly narrate this. Clear tension, readable choices, shareable moments.
- **Revelation Test**: First-time player has an audible "wait, WHAT?" moment when first metamorphosis happens.
- **Priority Test**: Experienced player can explain mutant priority. "Kill the glowing ones first."
- **Colossal Test**: Player can name and counter at least one Colossal type. "The Tide? Kite sideways, don't fight near mobs."

---

## Qualitative Assertions

- **QA-1** Movement should feel *crisp*. The character does exactly what you tell it, instantly.
- **QA-2** Upgrades should feel like *superpowers*. Each one changes what's possible.
- **QA-3** Enemies should feel like *puzzles*, not damage checks. Learn their patterns, own them.
- **QA-4** Death should feel like *lessons*, not punishment. "Ah, I see what I did wrong."
- **QA-5** Runs should feel like *practice*. Each one makes you better, not just luckier.
- **QA-6** Metamorphosis should feel like *dread*. The pulsing is a clock ticking toward catastrophe.
- **QA-7** Colossals should feel like *boss fights*. Not just bigger enemies—different games.
- **QA-8** The hive should feel like a *mirror*. "They're learning my patterns" = personal.

---

## Anti-Success (Failure Modes)

This pilot fails if:

**Core Gameplay Failures:**
- **Stat-stick upgrades**: Choices don't change *how* you play, only *numbers*. No emergent builds.
- **HP sponge enemies**: Enemies are just health bars, not patterns to learn. No skill expression.
- **Random death**: Player can't explain why they died. "It just happened" = design failure.
- **Movement tax**: Input lag, sluggish response, or stun-lock. The arcade loop is sacred.
- **Build sameness**: Every run plays the same regardless of upgrades. No identity.

**Hive Failures:**
- **Invisible metamorphosis**: Player can't tell when enemies are about to combine. Unfair.
- **Unfair Colossals**: Attacks aren't telegraphed, counters don't exist. Frustration, not challenge.
- **Hive feels random**: Adaptation doesn't feel personal. "They're not learning ME."
- **No revelation moment**: First metamorphosis passes without the "WHAT WAS THAT" reaction.
- **Colossal spam**: Too many Colossals too fast. Chaos without clarity.

**Experience Failures:**
- **Monotony**: Runs feel the same. No contrast, no peaks, no valleys.
- **Flat arc**: No CRISIS moment. No TRIUMPH/GRIEF. Just... middle. Emotional flatline.
- **Silent feedback**: Kills, hits, or level-ups without juice. Every action needs response.
- **Restart friction**: > 3 seconds from death to new run. Menus between runs. Momentum killed.
- **No mastery curve**: Run 50 feels the same as run 1. Player never gets better.

---

## Generative Refactor Mandate

> *"Every orchestrator plants something new. The garden never stagnates."*

**The Rule**: Each generation, the orchestrator MUST pick **ONE feature or game system** to refactor, rework, or reinvent with the intent of creating something unique to that generation.

**Target Selection**: The refactor target should be chosen from **the worst aspects of existing or common builds**—the systems that feel stale, underpowered, unexpressive, or derivative. Don't reinvent what's working. Attack what's weak.

**What's Allowed**:
- **Backwards incompatible**: Break old assumptions. Delete whole systems.
- **Destructive**: Tear down to rebuild. The phoenix path is valid.
- **Bizarre**: Plants theme? Pets that fight? Gravity inversion? *Yes.*

**The Only Constraint**: The pilot must remain **completable and playable** with the satisfaction criteria of this spec. The Fun Floor holds. Everything above it is fair game.

**Why This Exists**: Prevents convergence to local optima. Forces creativity over iteration. Each generation is a *statement*, not an increment.

**Example Refactors** (each is a valid choice):

| System | Possible Rework | What Changes |
|--------|-----------------|--------------|
| **Powers** | Powers have cooldowns + combos instead of passive fire | Active ability game, not auto-battler |
| **Movement** | Replace WASD with momentum physics or dash-only | Entirely different skill expression |
| **Enemies** | All enemies are environmental hazards, not mobs | Puzzle-survival hybrid |
| **Visuals** | Full aesthetic retheme (plants, cyberpunk, paper) | Same mechanics, new soul |
| **Companions** | Add pets that fight/buff/tank | Build identity includes creature choice |
| **Progression** | Upgrades morph your character's form | Visual and mechanical transformation |
| **Weapons** | Single weapon that evolves vs. weapon switching | Deep mastery vs. broad variety |
| **Arena** | Dynamic terrain (walls spawn, pits open) | Positioning becomes survival |

**Orchestrator Protocol**:
1. At generation start, **declare the refactor target** in witness mark
2. Implement the refactor fully—no half-measures
3. Validate against Fun Floor (the spec still holds)
4. Document what was learned in crystal

---

## Witness Integration (The Hive IS the Witness)

> *"The witness layer and the hive mind are the same thing. The game is the hive. The hive is watching."*

The game quietly records each run for post-game reflection—but narratively, it's the hive learning:

**During the Run:**
- **Pattern Tracking**: Every dodge, every kite, every kill—the hive watches
- **Adaptation Visible**: The hive intelligence indicator shows it's learning YOU
- **Mutual Recording**: You learn the Colossals; they learn your patterns

**Run Summary** (stored in crystal):
- What upgrades were chosen, how long survived, what killed you
- **Metamorphosis count**: How many Colossals spawned before you died
- **Hive intelligence level**: How smart the hive got during your run
- **Closest call**: The Colossal you almost let form
- Build profile: What playstyle emerged from upgrade choices
- Unchosen paths: What upgrades were offered but not taken (ghost alternatives)

**Crystal Inheritance**:
When killed by a Colossal, the crystallization shows:
- The Colossal that killed you (rotating 3D view)
- The enemies that formed it (decomposition view)
- How long they survived before combining (your failure window)
- What you could have done ("Kill the mutant first next time")

**Witness Principles:**
- **Invisible During Play**: Zero UI during gameplay. No live metrics, no Galois loss, no marks visible.
- **Reflection After**: Post-run crystal shows what happened and why, if player wants to look.
- **Never Judgmental**: Crystals describe ("aggressive early game") not evaluate ("bad choices").
- **Optional Depth**: Casual players ignore it. Analysts dig in. Both valid.
- **Hive Synergy**: The witness layer IS the hive's memory. Same data, different framing.

---

## Canary Success Criteria

**Core Gameplay Canaries:**
- **Retry rate > 80%**: After first death, player starts new run immediately.
- **"One more run" heard**: Playtester says it unprompted.
- **Build diversity**: 5 distinct viable builds emerge from playtest pool.
- **Death attribution**: Player names cause of death within 2 seconds, every time.
- **Mastery visible**: Experienced players survive 2x longer than beginners with same RNG.

**Hive/Metamorphosis Canaries:**
- **Revelation moment**: Every new player has a visible reaction to first metamorphosis.
- **Priority learning**: By run 3, players kill pulsing enemies first.
- **Colossal respect**: Players audibly react to Colossal spawn. "Oh no, not THE TIDE."
- **Mutant awareness**: Experienced players mention mutants unprompted. "Kill the glowing one!"
- **Hive personalization**: Players feel the hive adapting to THEM specifically. "It knows I dodge left."

**Design Canaries:**
- **Upgrade excitement**: Players audibly react to upgrade choices. "Ooh, I could go pierce!"
- **Enemy recognition**: Players name enemy types. "Watch out for the red chargers."
- **Colossal recognition**: Players name Colossals. "That's THE RAMPAGE—stay near walls."
- **Skill progression**: Same player improves measurably over 10 runs.
- **Movement praise**: Players comment on how good movement feels. "This is so responsive."

---

## Implementation Phases

### Phase 1: Core Survivors Loop (Current)
The base game without hive mechanics. Must satisfy Fun Floor before proceeding.

### Phase 2: Metamorphosis (Run 030)
1. Implement survival timer on enemies
2. Add pulsing visual state
3. Create one Colossal type (Shambler → THE TIDE)
4. Add metamorphosis trigger and animation

### Phase 3: Full Colossal Roster (Run 031)
1. Implement all 5 base Colossals
2. Add mutant variant system
3. Create themed movesets
4. Balance survival timers

### Phase 4: Hybrid Colossals (Run 032)
1. Implement hybrid detection (multiple enemy types combining)
2. Create 5 hybrid Colossals (AVALANCHE, STRAFING RUN, BUNKER, HIVE QUEEN, MIGRATION)
3. Add discovery system (no tooltips—experience only)

### Phase 5: Hive Intelligence (Run 033)
1. Implement collective learning (pattern propagation)
2. Add hive awareness HUD element
3. Create cross-enemy pattern propagation
4. Balance learning rate (fair, not punishing)

### Phase 6: Integration with Witness Systems (Run 034)
1. Merge hive data into crystal system
2. Add Colossal death rituals
3. Implement "hive knows you" personalization

---

## Out of Scope

- Complex witness UI during gameplay (crystals are post-run only)
- Galois loss metrics or live build coherence tracking
- Multiplayer balance, long-term meta economy, or matchmaking
- Leaderboards or competitive ranking systems
- Meta-progression unlocks (skill is the progression)
- Cross-run hive memory (hive resets each run per H2)

---

## The Pitch

> *"A survivors-like where the enemies are a hive mind racing to evolve before you can kill them. Let them live too long and they combine into Colossals with movesets no individual enemy could perform. The hive learns your patterns. The hive adapts. And every run, the hive remembers what killed you—and uses it.*
>
> *You're not fighting enemies. You're fighting an intelligence. And it's watching."*

---

## The Mirror Test

> *"Does this feel like Kent on his best day?"*

**Daring**: Hive mind enemies that actually learn and adapt.
**Bold**: Metamorphosis as core mechanic, not gimmick.
**Creative**: Colossals as emergent boss fights, not scripted encounters.
**Opinionated**: The hive and the witness are the same. The game is the enemy.
**Not gaudy**: Every system serves the core tension: kill fast or face metamorphosis.

---

*"They're not just enemies. They're a mirror. And they're learning faster than you."*
