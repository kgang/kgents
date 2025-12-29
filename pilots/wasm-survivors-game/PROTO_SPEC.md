# Hornet Siege: The Colony Always Wins

**Status**: Enlightened Proto-Spec v2.1 (Radical Transformation Edition)
**Version**: 2.1.0
**Date**: 2025-12-28
**Derivation**: Zero Seed + Experience Quality Operad + Run 034 Analysis + Brainstorming Synthesis

> *"You are the apex predator. You are nature's perfect killing machine. And you will lose."*

---

## ⚡ THE RADICAL TRANSFORMATION MANDATE ⚡

> *"Do not maintain. Do not polish. TRANSFORM."*

### The Prime Directive

**Whatever exists is not good enough.** Your job is not to preserve the current state—it is to **radically upgrade it** until it makes players gasp.

Every session, ask:
1. **What would make this 10x better?** (Not 10% better. 10x.)
2. **What would make someone clip this?** (Shareability = quality)
3. **What would make a streamer lose their mind?** (Spectacle matters)
4. **What would I brag about building?** (Pride = signal)

### The Anti-Maintenance Principle

| ❌ DON'T | ✅ DO |
|----------|-------|
| "Fix the bug" | "Redesign the system so the bug category is impossible" |
| "Polish the animation" | "Make the animation so good it becomes a meme" |
| "Balance the numbers" | "Find the numbers that create *moments*" |
| "Add the feature" | "Add the feature that makes players say 'holy shit'" |
| "Match the spec" | "Exceed the spec so dramatically that the spec needs updating" |

### The Transformation Test

Before committing ANY work, ask:

> *"If I showed this to someone who saw yesterday's build, would they say 'whoa, what happened?' or would they say 'looks the same'?"*

**If "looks the same" → you haven't transformed enough. Keep pushing.**

### Specific Transformation Targets

| System | Current State | Transformation Goal |
|--------|---------------|---------------------|
| **Kills** | Functional | Every kill should feel like a **dopamine hit** |
| **THE BALL** | Threatening | THE BALL should be **clip-worthy spectacle** |
| **Death** | Game over | Death should feel like **completing a journey** |
| **Upgrades** | Choices | Upgrades should create **"oh shit" synergy moments** |
| **Movement** | Responsive | Movement should feel like **being a predator** |
| **Sound** | Present | Sound should create **ASMR-level satisfaction** |

### The Courage Clause

**You have permission to:**
- Delete code that isn't working
- Rewrite systems from scratch
- Ignore "how it was done before"
- Break things in pursuit of better things
- Propose wild ideas
- Ship something audacious

**You do NOT have permission to:**
- Ship something mediocre
- Preserve bad code out of politeness
- Add features without juice
- Call something "done" when it's merely "functional"
- Be conservative when boldness is needed

### The Quality Floor (Non-Negotiable)

A feature is **NOT DONE** until:
- [ ] It would impress a stranger in 5 seconds
- [ ] It has screen shake, particles, or audio feedback
- [ ] It creates a "moment" (not just a "function")
- [ ] You would be proud to show it
- [ ] It exceeds what a generic game would do

### Voice Anchor

> *"Daring, bold, creative, opinionated but not gaudy."*
>
> This is not a request. This is the **minimum standard**.

---

## Meta-Principles: Specification as Possibility Space

> *"The spec defines what CAN be generated, not what MUST be generated."*

This specification is **generative**, not prescriptive. It defines:
- **Axioms** (L < 0.10): Fixed points that MUST hold across all regenerations
- **Values** (L < 0.35): Derived but stable principles that SHOULD hold
- **Specifications** (L < 0.70): Implementation choices that MAY diverge
- **Tuning** (L ≥ 0.70): Parameters that WILL vary between runs

**The Generative Test**: Delete the implementation. Regenerate from spec. The result is *isomorphic* but not *identical* to the original.

---

## Part I: The Axiom Layer (L < 0.10 — Fixed Points)

> *"These survive radical restructuring. Everything else is derived."*

### A1: PLAYER AGENCY (L = 0.02)
**Statement**: The player's choices must determine outcomes.
**Derivation**: L0.2 (Morphism) — actions are arrows that compose into consequences.
**Test**: For any outcome O, there exists a traceable decision chain D₁ → D₂ → ... → Dₙ → O.

**Implications**:
- No RNG deaths without player-influenced probability
- Every death attributable to player decisions
- Skill ceiling is infinite (perfect play extends survival)

### A2: ATTRIBUTABLE OUTCOMES (L = 0.05)
**Statement**: Every outcome must trace to an identifiable cause.
**Derivation**: L1.5 (Contradict) — unattributable outcomes contradict agency.
**Test**: Player can articulate cause of death within 2 seconds.

**Implications**:
- "THE BALL got me because I let scouts coordinate" ✓
- "I just died randomly" ✗
- Death screen shows causal chain

### A3: VISIBLE MASTERY (L = 0.08)
**Statement**: Skill development must be externally observable.
**Derivation**: L1.7 (Fix) — learning is iteration toward fixed point.
**Test**: Run 10 looks different from Run 1. Metrics improve.

**Implications**:
- Skill metrics tracked and displayed
- "I'm getting better" is provable, not just felt
- Mastery has visible markers (escapes, chains, dodges)

### A4: COMPOSITIONAL EXPERIENCE (L = 0.03)
**Statement**: Moments compose algebraically into arcs.
**Derivation**: L1.1 (Compose) — (moment >> moment) >> session = moment >> (moment >> session).
**Test**: Experience quality obeys associativity.

**Implications**:
- Micro-decisions build into macro-strategy
- Upgrade choices compose into build identity
- Runs compose into player skill trajectory

---

## Part II: The Value Layer (L < 0.35 — Derived but Stable)

> *"These emerge from axioms applied to game design. They're robust but not immutable."*

### V1: CONTRAST (L = 0.15)
**Statement**: Experiences must oscillate between poles.
**Derivation**: A4 (Composition) + Hardy's aesthetic criterion.

**Specification**:
```
Contrast: (PoleA, PoleB) → Oscillation
Quality degrades without oscillation.
Flat experiences violate A4 (monotone composition).
```

### V2: ARC (L = 0.18)
**Statement**: Experiences must traverse phases toward definite closure.
**Derivation**: A4 (Composition) + narrative coherence.

**Specification**:
```
Arc: Phase[] → Closure
Valid arcs have: at least one peak, at least one valley, definite ending.
Fade-outs violate A2 (closure is attributable).
```

### V3: DIGNITY (L = 0.22)
**Statement**: Endings must feel meaningful, not arbitrary.
**Derivation**: A2 (Attribution) + affective quality.

**Specification**:
```
Dignity: Ending → {meaningful, arbitrary}
"They earned it" = meaningful.
"What happened?" = arbitrary (violates A2).
```

### V4: JUICE (L = 0.28)
**Statement**: Actions must feel impactful through feedback.
**Derivation**: A1 (Agency) requires felt consequence.

**Specification**:
```
Juice: Action → Feedback
No silent actions. Every input produces output.
Feedback delay < 16ms (predator response time).
```

### V5: WITNESSED (L = 0.32)
**Statement**: The system should feel like a collaborator, not a judge.
**Derivation**: L0.3 (Mirror) + ethical principle.

**Specification**:
```
Witnessed: System → {collaborator, surveiller}
"The colony learned from me" = witnessed.
"The game is tracking me" = surveilled (violates ethical floor).
```

---

## Part III: The Specification Layer (L < 0.70 — Implementation Choices)

> *"These are ONE instantiation of the axioms. Other instantiations are valid."*

### S1: THE COLLECTIVE THREAT (L = 0.45)

**Current Instantiation**: THE HEAT BALL — bees surround and cook the hornet.

**Abstract Pattern**: A signature mechanic where many weak entities coordinate into an unstoppable force.

**Why This Instantiation**:
- Real biology (Japanese honey bees vs. giant hornets)
- Clip-worthy spectacle
- Teaches the tragedy theme

**Valid Alternatives** (for future regeneration):
- THE SWARM: Overwhelm through numbers
- THE HIVE MIND: Perfect prediction of player movement
- THE SACRIFICE: Bees that self-destruct to create barriers

**Regeneration Law**: Any collective threat that satisfies A1 (escapable with skill), A2 (readable formation), A3 (visible mastery curve) is valid.

### S2: THE TRAGIC RESOLUTION (L = 0.55)

**Current Instantiation**: The colony always wins. You play the tragedy of the invader.

**Abstract Pattern**: The relationship between player and collective has a definite resolution.

**Why This Instantiation**:
- Unique in genre (survivors-likes are about victory)
- Teaches empathy for the "enemy"
- Dark humor + swagger makes it palatable

**Valid Alternatives**:
- THE BREAKTHROUGH: Player can achieve pyrrhic victory (kill queen, still die)
- THE CYCLE: Player becomes part of the colony (transformation ending)
- THE UNDERSTANDING: Player learns something that changes their approach

**Regeneration Law**: Any resolution that satisfies V3 (dignity) is valid. "You just lose randomly" is not valid.

### S3: THE PREDATOR FANTASY (L = 0.48)

**Current Instantiation**: Japanese giant hornet — apex predator with real biological basis.

**Abstract Pattern**: Player is the overwhelming threat that gradually gets overwhelmed.

**Why This Instantiation**:
- Real biology creates authentic power fantasy
- "40 kills per minute" is a real fact
- Mandibles, venom, flight are real capabilities

**Valid Alternatives**:
- Any apex predator vs. collective prey (shark vs. fish school, wolf vs. caribou herd)
- Abstract: "force of nature" vs. "emergent resistance"

### S4: THE SEVEN CONTRASTS (L = 0.52)

**Current Instantiation**:

| Contrast | Pole A | Pole B |
|----------|--------|--------|
| **Power** | God of Death | Cornered Prey |
| **Tempo** | Speed (combat) | Stillness (level-up) |
| **Stance** | Massacre (early) | Respect (late) |
| **Humility** | Hubris ("invincible") | Humility ("I still lost") |
| **Sound** | Noise (combat) | Silence (THE BALL forming) |
| **Role** | Predator | Prey |
| **Knowledge** | Learning | Knowing |

**Abstract Pattern**: Emotional oscillation across multiple dimensions.

**Contrast Laws** (derived from V1):
- **GD-1**: Every run MUST visit both extremes of at least 3 contrasts.
- **GD-2**: Transitions should be *sudden*, not gradual.
- **GD-3**: Contrasts compose — you can be "God of Death + Speed + Noise" simultaneously.

### S5: THE UPGRADE SYSTEM (L = 0.58)

**Current Instantiation**: Six archetypes with verb-based upgrades.

| Archetype | Fantasy | Example Verbs |
|-----------|---------|---------------|
| **Executioner** | Maximum damage per strike | Crush, Inject, Critical |
| **Survivor** | Outlast the swarm | Harden, Regenerate, Drain |
| **Skirmisher** | Never stop moving | Burst, Evade, Hit-and-Run |
| **Terror** | Break their will | Fear, Panic, Death Throes |
| **Assassin** | Precision elimination | Pierce, Mark, Silent Strike |
| **Berserker** | Overwhelming offense | Volley, Frenzy, Blood Rage |

**Upgrade Laws** (derived from A1, A3):
- **U1**: Upgrades change *how* you act, not just *how much*.
- **U2**: By wave 5, player should have a nameable identity.
- **U3**: Synergies exist (1 + 1 > 2 somewhere).
- **U4**: Every choice is meaningful (no obvious "best").

### S6: THE BEE TAXONOMY (L = 0.55)

**Current Instantiation**:

| Type | Behavior | Teaches | Formation Role |
|------|----------|---------|----------------|
| **Worker** | Swarms toward player | Basic kiting | Numbers |
| **Scout** | Fast, alerts others | Priority targeting | Coordination speed |
| **Guard** | Slow, high HP, blocks | Prioritization | Structure |
| **Propolis** | Ranged sticky attacks | Projectile dodging | Area denial |
| **Royal Guard** | Elite, complex patterns | Boss mechanics | THE BALL anchor |

**Enemy Laws** (derived from A2):
- **E1**: Every attack is telegraphed.
- **E2**: Bee types are consistent (learnable).
- **E3**: Distinct silhouettes (readable).
- **E4**: Escalating coordination (late > early).
- **E5**: Fair deaths (attributable).

---

## Part IV: The Tuning Layer (L ≥ 0.70 — Parameters)

> *"These are arbitrary. Change them freely during development."*

### T1: TIMING CONSTANTS

| Parameter | Current Value | Range | Notes |
|-----------|---------------|-------|-------|
| Dash i-frames | 0.12s | 0.08-0.20s | Skill expression window |
| Dash cooldown | 1.5s | 1.0-2.0s | Rhythm pacing |
| Dash distance | 80px | 60-120px | Escape distance |
| Ball forming duration | 10s | 8-15s | Tension building |
| Ball silence duration | 3s | 2-5s | "Oh no" moment |
| Ball constrict duration | 2s | 1.5-3s | Escape window |
| Final gap size | 45° | 30-60° | Difficulty knob |

### T2: ECONOMY CONSTANTS

| Parameter | Current Value | Range |
|-----------|---------------|-------|
| XP per level base | 10 | 5-20 |
| XP scaling | 1.5x | 1.3-2.0x |
| Coordination alarm time | 10s | 8-15s |
| Coordination complete time | 20s | 15-30s |

### T3: FEEDBACK CONSTANTS

| Parameter | Current Value |
|-----------|---------------|
| Screen shake (kill) | 3px |
| Screen shake (multi-kill) | 8px |
| Screen shake (massacre) | 15px |
| Hit freeze frames | 2-3 frames |
| Near-miss threshold | 10px |

---

## Part V: The Polymorphic Quality Algebra

> *"Quality is measurable and composable. Different games instantiate different algebras."*

### 5.1 Abstract Algebra Interface

```typescript
interface SurvivorsQualityAlgebra {
  // What two poles does this experience oscillate between?
  contrastPoles(): [string, string][];

  // What phases does the experience traverse?
  arcPhases(): ArcPhase[];

  // What voices evaluate quality?
  voices(): Voice[];

  // What aesthetic minimums must be met?
  floorChecks(): FloorCheck[];

  // Compose experiences
  compose(a: Experience, b: Experience): Experience;
}
```

### 5.2 Hornet Siege Algebra (Current Instantiation)

```typescript
const HornetSiegeAlgebra: SurvivorsQualityAlgebra = {
  contrastPoles: () => [
    ["god_of_death", "cornered_prey"],
    ["speed", "stillness"],
    ["massacre", "respect"],
    ["hubris", "humility"],
    ["noise", "silence"],
    ["predator", "prey"],
    ["learning", "knowing"],
  ],

  arcPhases: () => [
    { name: "POWER", description: "Feeling godlike, kills flowing" },
    { name: "FLOW", description: "In the zone, combos chaining" },
    { name: "CRISIS", description: "THE BALL forming, panic rising" },
    { name: "TRAGEDY", description: "Inevitable end, dignity in death" },
  ],

  voices: () => [
    { name: "CREATIVE", approves: (e) => e.hasSwagger && e.feelsBold },
    { name: "ADVERSARIAL", approves: (e) => e.isFair && e.hasCounterplay },
    { name: "PLAYER", approves: (e) => e.isJoyful && e.feelsEarned },
  ],

  floorChecks: () => [
    // Mechanical floors
    { name: "input_latency", check: (e) => e.inputLatency < 16 },
    { name: "feedback_density", check: (e) => e.feedbackDensity > 0.5 },
    { name: "respawn_time", check: (e) => e.respawnTime < 3000 },

    // Aesthetic floors (NEW)
    { name: "earned_not_imposed", check: (e) => e.aestheticFeelsEmergent },
    { name: "meaningful_not_arbitrary", check: (e) => e.endingsHaveCause },
    { name: "witnessed_not_surveilled", check: (e) => e.systemFeelsCollaborative },
    { name: "dignity_in_failure", check: (e) => e.deathFeelsLikeJourney },
  ],

  compose: (a, b) => ({
    contrasts: Math.max(a.contrasts, b.contrasts),
    arc: [...a.arcPhases, ...b.arcPhases],
    floor: a.floor && b.floor,
    quality: a.floor && b.floor ?
      (a.contrasts + b.contrasts) / 2 * a.arc.coverage * b.arc.coverage : 0,
  }),
};
```

### 5.3 Quality Equation

```
Q = F × (C × A × V^(1/n))

where:
  F = Floor gate (0 or 1) — any floor failure zeros quality
  C = Contrast score [0, 1] — how much oscillation occurred
  A = Arc coverage [0, 1] — what fraction of phases were visited
  V = Voice approval — geometric mean of voice approvals
  n = number of voices
```

### 5.4 Aesthetic Floor Checks (NEW)

| Check | Question | Violation Example |
|-------|----------|-------------------|
| **F-A1: EARNED_NOT_IMPOSED** | Does the aesthetic feel emergent? | "This bee theme feels forced" |
| **F-A2: MEANINGFUL_NOT_ARBITRARY** | Do endings have cause? | "I just died for no reason" |
| **F-A3: WITNESSED_NOT_SURVEILLED** | Does system feel collaborative? | "It's tracking my failures" |
| **F-A4: DIGNITY_IN_FAILURE** | Does losing feel like completion? | "I failed the test" vs "I completed the journey" |

---

## Part VI: Arc Grammar (Polymorphic)

> *"Many arc shapes are valid. Tragedy is one option, not the only option."*

### 6.1 Arc Validity Rules

Valid arcs satisfy:
1. **At least ONE peak** (moment of highest engagement)
2. **At least ONE valley** (moment of lowest engagement)
3. **Definite closure** (the arc ENDS, not fades)
4. **Closure is earned** (V3: Dignity)

### 6.2 Valid Arc Shapes

| Arc | Phases | When to Use |
|-----|--------|-------------|
| **Tragedy** | HOPE → FLOW → CRISIS → DEATH | Current Hornet Siege (inevitable loss) |
| **Hero's Journey** | STRUGGLE → BREAKTHROUGH → MASTERY → TRANSCENDENCE | If adding victory condition |
| **Learning Spiral** | CHAOS → PATTERN → CHAOS → PATTERN → UNDERSTANDING | Tutorial-focused runs |
| **Emotional** | CONNECTION → LOSS → GRIEF → ACCEPTANCE | Story-focused variant |
| **Comedy of Escalation** | SURPRISE → OVERWHELM → ABSURDITY → LAUGH | Dark humor variant |

### 6.3 Invalid Arc Shapes

| Invalid Arc | Why | Violation |
|-------------|-----|-----------|
| **Flat line** | No peaks or valleys | A4 (composition requires change) |
| **Fade-out** | No definite closure | V3 (dignity requires ending) |
| **Arbitrary cut** | Closure not earned | A2 (outcomes must be attributable) |
| **Monotone climb** | No valleys | V1 (contrast requires oscillation) |

### 6.4 Current Arc: The Tragedy

```
Phase 1: POWER (Wave 1-3)
  - Player is godlike
  - Bees scatter
  - Kills feel effortless
  - Upgrades feel like becoming unstoppable

Phase 2: FLOW (Wave 4-6)
  - Combat rhythm established
  - Combos chaining
  - Build identity emerging
  - "I'm playing terror build"

Phase 3: CRISIS (Wave 7-9)
  - Coordination rising
  - Formations forming
  - First BALL encounter
  - "They're learning..."

Phase 4: TRAGEDY (Wave 10+)
  - THE BALL forms
  - Escape attempts
  - Inevitable death
  - "They earned it."
```

---

## Part VII: The Hornet's Personality

> *"The hornet has SWAGGER. Dark humor, not grimdark."*

### 7.1 Character Core

The hornet is not a tragic hero. The hornet is a **magnificent bastard** who knows the score and hunts anyway.

**Character Axioms**:
- Never begs, never whines, never seems unfairly treated
- KNOWS what this is and does it anyway
- Swagger before the fall
- Respect for the colony in death

### 7.2 Voice Lines (Optional)

| Trigger | Line |
|---------|------|
| First kill | "40 per minute. I can do better." |
| Multi-kill | "Evolution made me for this." |
| Level up | "Ah. More ways to die magnificently." |
| Formation spotted | "They're learning. How adorable." |
| THE BALL forming | "Well. Here we go again." |
| Death | "The colony always wins. ...Respect." |

### 7.3 Animation Personality

| State | Animation |
|-------|-----------|
| Idle (early) | Alert, aggressive stance |
| Idle (late) | Confident swagger, surveying kills |
| Idle (low HP) | Still defiant, not cowering |
| Kill | Satisfying snap |
| Multi-kill | Brief pause, savoring |
| Death | Acceptance, not despair |

---

## Part VIII: Witness Integration (Amber Memory)

> *"Every siege is preserved in amber. The colony remembers, and so do you."*

### 8.1 During the Siege

- **Invisible**: Zero UI during gameplay. Pure flow.
- **Recording**: Every kill, escape, formation, decision tracked silently.
- **Mutual**: You learn the formations; they learn your patterns.

### 8.2 Amber Memory (Post-Run Crystal)

```typescript
interface AmberCrystal {
  // Identity
  runId: string;
  timestamp: number;

  // Metrics
  duration: number;
  killCount: number;
  wave: number;

  // Cause
  deathCause: DeathCause;
  causalChain: string[];  // "Ignored scouts" → "Fast coordination" → "THE BALL"

  // Build
  buildProfile: BuildProfile;
  archetypeDominant: UpgradeArchetype;

  // Skill (A3: Visible Mastery)
  skillMetrics: SkillMetrics;
  improvementFromLast: SkillDelta;

  // What the colony learned
  colonyLearnings: string[];  // "Prefers left dash", "Ignores propolis"

  // Ghosts (unchosen paths)
  ghosts: Ghost[];

  // Narrative
  rationale: string;  // AI-generated run summary
}
```

### 8.3 Witness Principles

- **Invisible During Play**: Zero metrics visible during combat.
- **Reflection After**: Amber shows what happened and why.
- **Never Judgmental**: Describes ("aggressive early"), doesn't evaluate ("bad play").
- **Optional Depth**: Casuals ignore it. Analysts dig in.
- **Thematic**: You're preserved in amber, like the insects you are.

---

## Part IX: Anti-Patterns (Failure Modes)

### 9.1 Childish Failures

| Symptom | Cause | Axiom Violated |
|---------|-------|----------------|
| Hand-holding tutorials | Over-guidance | A1 (agency) |
| "Good job!" on trivial | Unearned praise | V3 (dignity) |
| Deaths as "oopsies" | No weight | V3 (dignity) |
| Power fantasy without cost | No tragedy | V1 (contrast) |

### 9.2 Annoying Failures

| Symptom | Cause | Axiom Violated |
|---------|-------|----------------|
| THE BALL without warning | No telegraph | A2 (attribution) |
| Stat-bump upgrades | No verb change | S5 laws |
| Death says "You Died!" not WHY | No cause | A2 (attribution) |
| Looping sound design | No care | V4 (juice) |

### 9.3 Offensive Failures

| Symptom | Cause | Axiom Violated |
|---------|-------|----------------|
| "Beat your best time!" | Hustle theater | V5 (witnessed) |
| "You only killed 50 today" | Gap shame | V5 (witnessed) |
| "We noticed you stopped" | Surveillance | V5 (witnessed) |
| "Nothing matters" nihilism | Tragedy without dignity | V3 (dignity) |

### 9.4 Core Gameplay Failures

| Symptom | Cause | Axiom Violated |
|---------|-------|----------------|
| Random deaths | Unattributable | A2 |
| Stat-stick upgrades | No identity | A1 |
| HP sponge enemies | No learning | A3 |
| Movement lag | No predator feel | V4 |
| Build sameness | No diversity | S5 |
| Limp kills | No juice | V4 |

---

## Part X: Regeneration Laws

> *"When diverging from this spec, preserve axioms, respect values, supersede specifications freely."*

### RL-1: Axiom Preservation (MUST)

Any regeneration MUST preserve:
- A1: Player agency
- A2: Attributable outcomes
- A3: Visible mastery
- A4: Compositional experience

### RL-2: Value Stability (SHOULD)

Any regeneration SHOULD preserve:
- V1: Contrast (oscillation exists)
- V2: Arc (phases toward closure)
- V3: Dignity (meaningful endings)
- V4: Juice (felt feedback)
- V5: Witnessed (collaborative feel)

### RL-3: Specification Divergence (MAY)

Any regeneration MAY diverge from:
- S1: THE BALL (replace with any collective threat)
- S2: Tragedy (replace with any resolution)
- S3: Hornet (replace with any predator)
- S4: Seven Contrasts (replace with N contrasts, N ≥ 3)
- S5: Upgrade archetypes (replace with any verb-based system)
- S6: Bee types (replace with any learnable enemy taxonomy)

### RL-4: Explicit Supersession

When diverging, document:
1. What was superseded
2. Why (what new insight prompted change)
3. How axioms are still preserved
4. What new value is added

---

## Part XI: Multi-Phase Roadmap

> *"From prototype to sellable, jaw-dropping mind journey."*

### Phase 0: Foundation Verification (COMPLETE)

**Goal**: Validate core loop works.

**Exit Criteria**:
- [x] Player moves responsively (<16ms input lag)
- [x] Kills feel satisfying (crunch, scatter, XP burst)
- [x] Upgrades change gameplay (verb-based)
- [x] Enemies are readable (distinct silhouettes)
- [x] Basic coordination exists (pheromone visuals)

### Phase 1: THE BALL Perfection (CURRENT)

**Goal**: Make THE BALL clip-worthy.

**Exit Criteria**:
- [ ] First-time viewer gasps
- [ ] Escape feels frame-tight but fair
- [ ] Audio design creates dread (silence before death)
- [ ] Camera pull shows full sphere
- [ ] Temperature indicator visible
- [ ] Death feels *inevitable in retrospect*

**Specific Tasks**:
1. **Visual polish**: Heat shimmer, bee vibration, temperature glow
2. **Audio design**: Buzz crescendo → silence → bass note → cooking crackle
3. **Gap mechanics**: Green escape arc, forgiving but tense
4. **Camera work**: Pull-back during sphere, focus on gap during constrict
5. **Skill expression**: Perfect gap escape tracked as achievement

### Phase 2: Contrast Depth (NEXT)

**Goal**: Make every run emotionally varied.

**Exit Criteria**:
- [ ] Each run visits 3+ contrast poles
- [ ] "God of Death" → "Cornered Prey" transition is sudden
- [ ] Silence before THE BALL is palpable
- [ ] Player describes runs in contrast terms

**Specific Tasks**:
1. **Contrast tracking**: System monitors which poles have been visited
2. **Dynamic audio**: Music responds to contrast state
3. **Visual language**: Color palette shifts with mood
4. **Narrative beats**: Text appears at contrast transitions

### Phase 3: Build Diversity (WEEK 3-4)

**Goal**: Every run feels like a different hunting style.

**Exit Criteria**:
- [ ] 6 viable archetypes emerge
- [ ] Players name their builds ("terror build", "berserker run")
- [ ] Synergies are discovered, not told
- [ ] Ghost upgrades create "what if" tension

**Specific Tasks**:
1. **Synergy tuning**: Ensure 2+ combos per archetype
2. **Visual identity**: Hornet appearance changes with build
3. **Verb diversity**: Each upgrade changes HOW, not just HOW MUCH
4. **Balance pass**: No obviously dominant strategy

### Phase 4: Colony Intelligence (WEEK 5-6)

**Goal**: The colony feels like it's learning YOU.

**Exit Criteria**:
- [ ] Colony learns patterns within a run
- [ ] "They know I dash left" feeling emerges
- [ ] Death screen shows what colony learned
- [ ] Complicity is felt ("I taught them this")

**Specific Tasks**:
1. **Pattern tracking**: Colony remembers player behaviors
2. **Adaptive response**: Formations adjust to player style
3. **Visible learning**: HUD shows colony coordination level
4. **Death attribution**: "The colony learned: [your patterns]"

### Phase 5: Personality Polish (WEEK 7-8)

**Goal**: The hornet is a CHARACTER.

**Exit Criteria**:
- [ ] Players quote the hornet's lines
- [ ] Swagger is visible in animations
- [ ] Death feels like "completing a journey", not "failing a test"
- [ ] Dark humor lands

**Specific Tasks**:
1. **Voice lines**: Implement text-based personality
2. **Animation polish**: Confidence in idle, savoring in multi-kill
3. **Death ritual**: Dignified acceptance animation
4. **Humor tuning**: Dark but not grimdark

### Phase 6: Witness Integration (WEEK 9-10)

**Goal**: Every run is remembered.

**Exit Criteria**:
- [ ] Amber crystal captures run essence
- [ ] Improvement visible across runs
- [ ] Ghost upgrades create regret/wonder
- [ ] Run history is browsable

**Specific Tasks**:
1. **Crystal generation**: Auto-generate run summaries
2. **Skill delta**: Show improvement from last run
3. **Ghost display**: "You could have been Berserker"
4. **History view**: Browse past runs, compare builds

### Phase 7: Streamability (WEEK 11-12)

**Goal**: Streamers want to play this.

**Exit Criteria**:
- [ ] "THE BALL IS FORMING" becomes a meme
- [ ] Clips are self-explanatory
- [ ] Commentary feels natural
- [ ] Deaths are entertaining, not frustrating

**Specific Tasks**:
1. **Clip detection**: Auto-identify clip-worthy moments
2. **Viewer-friendly UI**: Clear for observers
3. **Tension pacing**: Builds are entertaining to watch
4. **Death spectacle**: Deaths are dramatic, not anti-climactic

### Phase 8: Market Polish (WEEK 13-16)

**Goal**: Ready for sale.

**Exit Criteria**:
- [ ] Tutorial teaches without hand-holding
- [ ] First 5 minutes hook the player
- [ ] Steam page captures the vibe
- [ ] Reviews say "I can't stop playing"

**Specific Tasks**:
1. **Onboarding**: Non-intrusive tutorial
2. **First run optimization**: Hook in first 5 minutes
3. **Marketing assets**: Trailer, screenshots, capsule art
4. **Store page**: Copy that captures tragedy + swagger
5. **Localization**: Key markets
6. **Performance**: 60fps on target hardware

---

## Part XII: Success Metrics

### 12.1 Canary Tests (Qualitative)

| Test | Pass Criteria |
|------|---------------|
| **5-Minute Test** | New player: controls (30s), first kill (5s), feels powerful (wave 1), dies to THE BALL (wave 3-5), retries |
| **Tragedy Test** | Run 10 player plays better AND still loses. Lesson lands. |
| **Build Test** | Two players describe runs differently |
| **Death Test** | Player names cause of death in <2s |
| **Streamer Test** | Someone could entertainingly narrate |
| **Clip Test** | THE BALL is compelling without context |
| **Humor Test** | Player smiles at least once per run |
| **Dignity Test** | Player says "they earned it", not "that was BS" |

### 12.2 Quantitative Metrics

| Metric | Target |
|--------|--------|
| Retry rate | >80% after first death |
| Session length | >15 minutes average |
| Return rate | >40% day-2 retention |
| Build diversity | 6 distinct viable builds |
| Death attribution time | <2 seconds |
| Skill improvement | 2x survival time by run 10 |

### 12.3 Anti-Metrics (What NOT to Optimize)

| Anti-Metric | Why |
|-------------|-----|
| Time-to-first-death | Longer isn't better; tension is |
| Maximum kill count | High score isn't the point |
| Session count per day | Quality > quantity |
| Upgrade collection % | Diversity > completionism |

---

## Part XIII: The Pitch

> *"A survivors-like where you play the monster. You're a Japanese giant hornet raiding a bee colony—nature's perfect predator against nature's most coordinated defense. Your mandibles can kill 40 bees per minute. It won't be enough.*
>
> *The bees aren't just enemies. They're a civilization. And when they form THE BALL—surrounding you, vibrating, raising the temperature until you cook—you'll understand: sometimes the invader loses. Sometimes the colony prevails.*
>
> *You're not fighting bees. You're fighting a superorganism. And it always wins."*

---

## Part XIV: The Mirror Test

> *"Does this feel like Kent on his best day?"*

| Quality | Check |
|---------|-------|
| **Daring** | You play the villain. You lose. That's the point. |
| **Bold** | THE HEAT BALL as core mechanic—real biology, real tragedy. |
| **Creative** | A survivors-like where survival isn't the goal—understanding is. |
| **Opinionated** | The bees ALWAYS win. This is a tragedy you play through. |
| **Not gaudy** | Every system serves the core truth. No feature creep. |
| **Joyful** | Kills feel INCREDIBLE. The hornet has swagger. Dark humor, not grimdark. |

---

## Appendix A: Galois Stratification Summary

| Layer | Loss Range | Examples | Regeneration Rule |
|-------|------------|----------|-------------------|
| **Axiom** | L < 0.10 | A1-A4 (Agency, Attribution, Mastery, Composition) | MUST preserve |
| **Value** | L < 0.35 | V1-V5 (Contrast, Arc, Dignity, Juice, Witnessed) | SHOULD preserve |
| **Spec** | L < 0.70 | S1-S6 (THE BALL, Tragedy, Hornet, Contrasts, Upgrades, Bees) | MAY diverge |
| **Tuning** | L ≥ 0.70 | T1-T3 (Timing, Economy, Feedback constants) | WILL vary |

---

## Appendix B: Experience Quality Equation

```
Q = F × (C × A × V^(1/n))

where:
  Q = Total quality score [0, 1]
  F = Floor gate ∈ {0, 1}
  C = Contrast coverage [0, 1]
  A = Arc phase coverage [0, 1]
  V = Voice approval product
  n = Number of voices

Floor failures:
  - input_latency > 16ms → F = 0
  - feedback_density < 0.5 → F = 0
  - arbitrary_death = true → F = 0
  - surveilled_feeling = true → F = 0
```

---

## Appendix C: Implementation Cross-Reference

| Concept | File | Status |
|---------|------|--------|
| Types | `types.ts` | Complete |
| Formation System | `systems/formation.ts` | Complete |
| Enemy FSM | `systems/bee-fsm.ts` | Complete |
| Combat | `systems/combat.ts` | Complete |
| Upgrades | `systems/upgrades.ts` | Complete |
| Contrast | `systems/contrast.ts` | In Progress |
| Witness | `systems/witness.ts` | Complete |
| Juice | `systems/juice.ts` | Complete |
| Spawn | `systems/spawn.ts` | Complete |
| Physics | `systems/physics.ts` | Complete |

---

*"LEGIBLE DOOM is not the axiom. LEGIBLE DOOM is what emerged when we applied the axioms to bees. The axioms are: agency, attribution, mastery, composition. Everything else is derived."*

*"You are the apex predator. You are evolution's perfect killing machine. You will slaughter thousands. And when they form THE BALL, when the heat rises, when you cook alive surrounded by the civilization you tried to destroy—you'll understand.*

*The colony always wins. And it should."*

---

## Appendix D: CONCRETE MECHANICS (Implement These)

> *"No theory. Specific numbers. Build Monday morning."*

### Priority 1: Core Combat Feel (Week 1)

| Mechanic | What It Does | Numbers | Why Fun |
|----------|--------------|---------|---------|
| **Venom Stacking** | 3 hits = paralysis | Stack duration: 4s, Freeze: 1.5s | See buildup, trigger payoff |
| **Bleeding DoT** | Melee causes stacking bleed | 5 DPS × 5 stacks max, 8s duration | Watch enemies bleed out |
| **Berserker Aura** | +5% damage per nearby enemy | 200px range, 50% max bonus | Swarms make you stronger |
| **Hover Brake** | Instant stop + i-frames | 0.3s invuln, 3s cooldown | Clutch dodges feel GOOD |

### Priority 2: Risk-Reward Systems (Week 2)

| Mechanic | What It Does | Numbers | Why Fun |
|----------|--------------|---------|---------|
| **Execute Threshold** | +50% damage to low-HP enemies | Below 25% HP triggers | Setup → payoff |
| **Revenge Buff** | Getting hit = +25% damage | 3s duration, no cooldown | Aggression rewarded |
| **Graze Bonus** | Near-miss = meter + chain bonus | 30px graze zone, 5 grazes = +10% damage | Risk-taking rewarded |
| **Afterimage Dash** | Dashing spawns damage trail | 8 damage per image, 0.1s spawn rate | Speed IS your weapon |

### Priority 3: Enemy Depth (Week 3)

| Mechanic | What It Does | Numbers | Why Fun |
|----------|--------------|---------|---------|
| **Pheromone Bomb** | Attract enemies → explode | 300px attract, 2s delay, 40 damage | Set trap, enemies walk in, BOOM |
| **Wax Barriers** | Builder bees create destructible walls | 60 HP walls, 3s build time | Dynamic terrain puzzle |

---

## Appendix E: JUICE PARAMETERS (Copy-Paste These)

> *"Screen shake, particles, audio. Exact values."*

### Screen Shake

```typescript
const SHAKE = {
  workerKill:  { amplitude: 2,  duration: 80,  frequency: 60 },
  guardKill:   { amplitude: 5,  duration: 150, frequency: 60 },
  bossKill:    { amplitude: 14, duration: 300, frequency: 60 },
  playerHit:   { amplitude: 8,  duration: 200, frequency: 60 },
};
```

### Freeze Frames

```typescript
const FREEZE = {
  significantKill: 2,   // frames (33ms at 60fps)
  multiKill:       4,   // frames (66ms)
  criticalHit:     3,   // frames
};
```

### Particles

```typescript
const PARTICLES = {
  deathSpiral: {
    count: 25,
    color: '#FFE066',  // soft yellow pollen
    spread: 45,        // degrees
    lifespan: 400,     // ms
    rotation: 3,       // full rotations during descent
  },
  honeyDrip: {
    count: 15,
    color: '#F4A300',  // amber
    gravity: 200,      // px/s²
    poolFade: 1200,    // ms
  },
  damageFlash: {
    colors: ['#FF6600', '#FF0000'],  // orange → red
    flashDuration: 100,
    fadeDuration: 200,
    fragmentCount: 10,
    fragmentVelocity: 225,  // px/s
  },
};
```

### Visual Tells

```typescript
const TELLS = {
  chargingGlow: {
    color: '#FFD700',    // gold
    duration: 500,       // ms pre-attack
    pulseScale: 1.2,     // max scale
    pulseRate: 100,      // ms per pulse
    opacity: [0.4, 0.8], // min → max
  },
  formationLines: {
    color: '#FFD700',
    opacity: 0.4,
    width: 1.5,          // px
    fadeTime: 150,       // ms
    minBees: 3,          // show only when coordinated
  },
  stingerTrail: {
    color: '#6B2D5B',    // venom purple
    duration: 300,       // ms linger
  },
};
```

### Audio Cues

```typescript
const AUDIO = {
  alarmPheromone: {
    freqStart: 400,      // Hz
    freqEnd: 2000,       // Hz
    duration: 300,       // ms
  },
  ballForming: {
    buzzVolume: 0.3,     // starts quiet
    buzzPeak: 1.0,       // crescendo
    silenceDuration: 3000,  // ms of dread
  },
};
```

---

## Appendix F: GENRE-PROVEN TIMINGS

> *"Numbers from Vampire Survivors, Brotato, 20 Minutes Till Dawn."*

### Session Pacing

| Time | What Happens | Difficulty |
|------|--------------|------------|
| 0:00-2:00 | Learn mechanics, feel powerful | Gentle |
| 2:00-5:00 | First synergies available | +40% spawn rate |
| 5:00-10:00 | Build identity forms | Introduce elites |
| 10:00-15:00 | Plateau, player feels strong | Maintain pressure |
| 15:00-18:00 | THE BALL starts forming | 3-phase encounter |
| 18:00-22:00 | Escape or die | Exponential |

### Upgrade Cadence

| Event | Timing |
|-------|--------|
| First upgrade | 20-30 seconds |
| Subsequent upgrades | Every 35-40 seconds |
| First synergy possible | Minute 2-3 |
| Full build realized | Minute 12-15 |
| Choices per decision | Exactly 3 |

### Spawn Density

| Time | Enemies on Screen |
|------|-------------------|
| 0-5 min | 3-5 |
| 5-10 min | 8-12 |
| 10-20 min | 15-25 |
| 20+ min | 30-50 + formations |

### Enemy Introduction

| Wave | New Content |
|------|-------------|
| 1 | Workers only (learn basics) |
| 3 | Scouts (coordination preview) |
| 5 | Guards (tanky, prioritization) |
| 7 | Propolis (ranged, dodging) |
| 9+ | Royal Guards + THE BALL |

### Health/Damage Calibration

| Parameter | Value | Reason |
|-----------|-------|--------|
| Player HP | 100 | Nice round number |
| Damage per hit | 5-15 | Forces dodging (6+ hits to kill) |
| Healing frequency | Every 2-3 min | Creates scarcity |
| "Threatened" threshold | <30% HP | Trigger visual/audio warning |
| THE BALL damage | 20-30 per tick | Forces active escape |

---

## Appendix G: MONDAY MORNING CHECKLIST

> *"What to actually build this week. Build it LOUD."*

### 🔥 TRANSFORMATION MINDSET (Read First)

Before you touch any code, internalize this:

**You are not here to maintain. You are here to make this game INCREDIBLE.**

| Task | Maintenance Mindset ❌ | Transformation Mindset ✅ |
|------|------------------------|---------------------------|
| Screen shake | "Add 3px shake" | "Make kills feel like PUNCHES" |
| Freeze frames | "Pause for 2 frames" | "Create 'time slows when you're badass' moments" |
| Particles | "Spawn some particles" | "Make death explosions that players want to screenshot" |
| Venom | "Implement the mechanic" | "Make paralysis so satisfying players SEEK IT" |

### This Week's Tasks (Priority Order)

1. **Screen shake on kills** (2 hours)
   - Copy SHAKE values from Appendix E
   - Hook into kill event
   - Test: Worker kill = subtle, Guard kill = noticeable
   - **🔥 TRANSFORMATION**: Does multi-kill shake make you feel POWERFUL?

2. **Freeze frames on significant kills** (1 hour)
   - Copy FREEZE values
   - Hook into multi-kill detection
   - Test: 3+ kill feels WEIGHTY
   - **🔥 TRANSFORMATION**: Does time-stop make you feel like an APEX PREDATOR?

3. **Death spiral animation** (2 hours)
   - Copy deathSpiral particle config
   - 3 rotations during 0.6s descent
   - Pollen burst on impact
   - **🔥 TRANSFORMATION**: Would someone CLIP this death animation?

4. **Venom stacking system** (3 hours)
   - 3 stacks = 1.5s paralysis
   - Visual: color shift per stack
   - Test: Satisfying freeze payoff
   - **🔥 TRANSFORMATION**: Does the paralysis moment feel like a TRAP SPRINGING?

5. **Graze detection** (2 hours)
   - 30px near-miss zone
   - Cyan spark particle on graze
   - 5 consecutive grazes = damage buff
   - **🔥 TRANSFORMATION**: Does grazing feel DANGEROUS and REWARDING?

### NOT This Week

- ❌ Quality equation calculations
- ❌ Galois loss measurements
- ❌ Category theory derivations
- ❌ Polymorphic quality algebras
- ❌ Regeneration law documentation
- ❌ Conservative incremental improvements
- ❌ "Good enough" implementations

### Definition of Done (Transformed)

Each feature is DONE when:
- [ ] Specific numbers from spec are implemented
- [ ] Visual/audio feedback is present
- [ ] Feels good to use (player smiles)
- [ ] No crashes or obvious bugs
- [ ] **🔥 You would show this to a friend**
- [ ] **🔥 It exceeds what you thought possible when you started**
- [ ] **🔥 Yesterday's build looks BORING compared to today's**

### Transformation Checkpoints

**Every 2 hours, stop and ask:**

1. "Am I building something BOLD or something SAFE?"
2. "Would this make Kent say 'holy shit' or 'that's fine'?"
3. "Is this 10x better or 10% better?"
4. "Would I be PROUD to demo this?"

**If any answer is the conservative option → PIVOT. Push harder.**

### The Transformation Failures to Avoid

| Failure Mode | What It Looks Like | The Fix |
|--------------|-------------------|---------|
| **Timid shake** | 1-2px shake that's barely visible | DOUBLE IT. Then double it again. |
| **Weak particles** | 5 particles that fade instantly | 25 particles, longer trails, brighter colors |
| **Silent kills** | No audio feedback | Add CRUNCH. Add SPLAT. Layer sounds. |
| **Boring upgrades** | "+10% damage" text | Show the damage HAPPENING. Enemies EXPLODE. |
| **Limp death** | Sprite disappears | SPIRAL. SCATTER. HONEY DRIP. DRAMA. |

### The Ultimate Question

At the end of each session:

> *"If a stranger played this for 30 seconds, would they want to play for 30 minutes?"*

**If NO → you haven't transformed enough. Tomorrow, go harder.**

---

## Appendix H: LOCKED vs OPEN

> *"What you can change freely vs. what needs approval."*

### LOCKED (Do Not Change Without Discussion)

| Item | Why Locked |
|------|------------|
| THE BALL is the final threat | Core identity |
| Player always loses | Tragedy theme |
| Hornet is a predator, not victim | Character core |
| Arc is 4 phases (Power→Flow→Crisis→Tragedy) | Tested structure |
| Death is dignified, not punishing | Ethical floor |

### OPEN (Change Freely)

| Item | Guidance |
|------|----------|
| Timing constants | See Appendix F ranges |
| Visual polish | See Appendix E values |
| Audio design | Experiment within vibe |
| Bee variants | Add/remove as needed |
| Upgrade archetypes | Must stay verb-based |
| Particle counts | Optimize for performance |
| Screen shake amounts | Tune to feel |

### The Rule

If you want to change a LOCKED item:
1. Stop coding
2. Open an issue
3. Discuss with Kent
4. Get explicit approval

If it's OPEN: just change it and note in commit.

---

**Filed**: 2025-12-28
**Compression**: This spec is generative. Delete the implementation. Regenerate. The result is isomorphic.
