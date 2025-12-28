# Wasm Survivors: Witnessed Run Lab

Status: proto-spec

> *"Every death teaches. Every upgrade transforms. Every run, you're better than before."*

## Narrative

A chaotic arcade roguelike where survival is the tutorial and mastery is the destination. The game teaches through play—each death clarifies, each upgrade reshapes how you move and fight, each run deposits skill that carries forward. You don't just get stronger builds; you become a better player.

## Personality Tag

*This pilot believes the best games make you better at them. Upgrades should feel like superpowers, enemies should feel like puzzles, and death should feel like a lesson.*

## Objectives

- Create a survivors-like where **player skill matters as much as build RNG**—dodging, positioning, and timing should always be viable.
- Design **upgrades that change how you play**, not just numbers that go up. Each upgrade is a verb, not a noun.
- Design **enemies that teach through patterns**—learnable, readable, punishable. Every enemy type is a skill check.
- Ensure **every run makes the player better**—whether through build discovery, pattern recognition, or mechanical improvement.

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

### 3. Enemies Teach Through Play

> *"Every enemy is a question. Skilled players know the answers."*

Enemies are not HP bags—they're skill checks with personalities.

**Enemy Design Laws:**
- **E1 Readable Tells**: Every attack is telegraphed. Wind-up animations, audio cues, ground markers.
- **E2 Learnable Patterns**: Enemy behavior is consistent. Same enemy, same patterns. Mastery is possible.
- **E3 Distinct Silhouettes**: Know the enemy type instantly from shape/color. No confusion in chaos.
- **E4 Escalating Threat**: Basic enemies teach fundamentals. Elites combine patterns. Bosses demand mastery.
- **E5 Fair Deaths**: Every death is attributable. "I died because I didn't dodge the red one's charge."

**Enemy Archetypes**:

| Type | Behavior | Teaches |
|------|----------|---------|
| **Shambler** | Walks toward player | Basic kiting |
| **Rusher** | Charges in straight line | Sidestep timing |
| **Spitter** | Ranged projectiles | Projectile dodging |
| **Splitter** | Splits on death | Positioning, not just killing |
| **Tank** | Slow, high HP, big damage | Prioritization |
| **Swarm** | Many weak enemies | AoE value, crowd management |
| **Elite/Boss** | Combines patterns | Everything at once |

### 4. Mastery Accumulates

> *"Run 50 should feel different from run 1—not because of unlocks, but because of *you*."*

The player should get better at the game, not just better at builds.

**Mastery Laws:**
- **P1 Skill Transfer**: Skills learned in one run apply to all future runs. Dodge timing doesn't reset.
- **P2 Pattern Recognition**: Repeated play reveals enemy patterns. "I know this spawn wave."
- **P3 Build Intuition**: Experienced players know which upgrades synergize. Decision speed improves.
- **P4 Mechanical Ceiling**: High skill ceiling for movement. Speedrunners should look superhuman.
- **P5 Progress Feeling**: After 10 runs, player should *feel* more competent, even without meta-progression.

---

## Game Design Laws

### Emotional Arc (E)

- **E1 Journey Shape**: Runs traverse HOPE → FLOW → CRISIS → TRIUMPH/GRIEF. Flat emotional lines are failures.
- **E2 One More Run**: The post-death state must invite immediate retry. Friction here kills the game.
- **E3 Defeat Clarity**: Failure runs produce *clearer* feedback than victories. You must know *why* you died.

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

### Player Advocate Tests

- **5-Minute Test**: New player understands controls (30s), gets first kill (10s), feels powerful (wave 2), retries after death.
- **Mastery Test**: Player on run 10 demonstrably plays better than run 1—dodges more, positions better, chooses faster.
- **Build Test**: Two players describe their runs differently based on upgrade choices. "I went orbital" vs "I went pierce".
- **Death Test**: Player can explain every death. "I got cornered" not "I don't know what happened."
- **Streamer Test**: Someone could entertainingly narrate this. Clear tension, readable choices, shareable moments.

---

## Qualitative Assertions

- **QA-1** Movement should feel *crisp*. The character does exactly what you tell it, instantly.
- **QA-2** Upgrades should feel like *superpowers*. Each one changes what's possible.
- **QA-3** Enemies should feel like *puzzles*, not damage checks. Learn their patterns, own them.
- **QA-4** Death should feel like *lessons*, not punishment. "Ah, I see what I did wrong."
- **QA-5** Runs should feel like *practice*. Each one makes you better, not just luckier.

---

## Anti-Success (Failure Modes)

This pilot fails if:

**Core Gameplay Failures:**
- **Stat-stick upgrades**: Choices don't change *how* you play, only *numbers*. No emergent builds.
- **HP sponge enemies**: Enemies are just health bars, not patterns to learn. No skill expression.
- **Random death**: Player can't explain why they died. "It just happened" = design failure.
- **Movement tax**: Input lag, sluggish response, or stun-lock. The arcade loop is sacred.
- **Build sameness**: Every run plays the same regardless of upgrades. No identity.

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

## Witness Integration (Background)

> *The witness layer records runs without interfering with play. It's a diary, not a coach.*

The game quietly records each run for post-game reflection:
- **Run Summary**: What upgrades were chosen, how long survived, what killed you
- **Build Profile**: What playstyle emerged from upgrade choices
- **Unchosen Paths**: What upgrades were offered but not taken (ghost alternatives)

**Witness Principles:**
- **Invisible During Play**: Zero UI during gameplay. No live metrics, no Galois loss, no marks visible.
- **Reflection After**: Post-run crystal shows what happened and why, if player wants to look.
- **Never Judgmental**: Crystals describe ("aggressive early game") not evaluate ("bad choices").
- **Optional Depth**: Casual players ignore it. Analysts dig in. Both valid.

---

## Canary Success Criteria

**Core Gameplay Canaries:**
- **Retry rate > 80%**: After first death, player starts new run immediately.
- **"One more run" heard**: Playtester says it unprompted.
- **Build diversity**: 5 distinct viable builds emerge from playtest pool.
- **Death attribution**: Player names cause of death within 2 seconds, every time.
- **Mastery visible**: Experienced players survive 2x longer than beginners with same RNG.

**Design Canaries:**
- **Upgrade excitement**: Players audibly react to upgrade choices. "Ooh, I could go pierce!"
- **Enemy recognition**: Players name enemy types. "Watch out for the red chargers."
- **Skill progression**: Same player improves measurably over 10 runs.
- **Movement praise**: Players comment on how good movement feels. "This is so responsive."

---

## Out of Scope

- Complex witness UI during gameplay (crystals are post-run only)
- Galois loss metrics or live build coherence tracking
- Multiplayer balance, long-term meta economy, or matchmaking
- Leaderboards or competitive ranking systems
- Meta-progression unlocks (skill is the progression)
