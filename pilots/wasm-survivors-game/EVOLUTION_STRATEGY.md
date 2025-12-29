# WASM Survivors: Evolution Strategy

> *"Whatever exists is not good enough. Your job is not to preserve—it is to RADICALLY UPGRADE."*

**Generated:** 2024-12-29 | **Status:** Living Document

---

## EXECUTIVE SUMMARY

This document provides a foundational strategy for continuously refining and evolving the wasm-survivors-game pilot. Based on comprehensive architectural analysis, the game has a **production-quality foundation** with clear extension points. The strategy focuses on three evolutionary axes:

1. **SCOPE** — Expanding gameplay breadth (new mechanics, systems, content)
2. **DEPTH** — Deepening existing systems (mastery curves, emergent complexity)
3. **QUALIA** — Elevating experiential quality (art, animations, juice, legibility)

---

## I. ARCHITECTURAL FOUNDATIONS (Current State)

### System Census (40+ Systems)

```
LAYER 0: FOUNDATION
├─ Physics System (508 lines) — movement, collision, arena bounds
├─ Events System (1837 lines) — typed event bus, replay, analytics
├─ Spawn System — wave progression, enemy introduction
└─ Types (core) — GameState, Player, Enemy, Particle, etc.

LAYER 1: GAMEPLAY
├─ Enemies (bee taxonomy: 5 types, FSM behaviors)
├─ Upgrades (12 verb-based, 20+ synergies, 6 archetypes)
├─ Abilities (61 composable, Run 036)
├─ Combos (27 recipes, discovery system)
├─ Formation (THE BALL: 13 sub-modules, 7 phases)
├─ Metamorphosis (pulsing → seeking → combining)
├─ Colossal (THE TIDE: absorption, fission, gravity well)
└─ Melee (Mandible Reaver: arc, stances, multishot)

LAYER 2: COMBAT
├─ Apex Strike (predator dash: lock→strike→chain, bloodlust)
├─ Combat (hit detection, damage, invincibility frames)
├─ Graze (near-miss mechanic, frenzy stacking)
└─ Thermal Momentum (movement-based heat)

LAYER 3: EXPERIENCE
├─ Juice (shake, particles, freeze frames, crescendo)
├─ Sound (3-layer ASMR kills, spatial audio, TRUE SILENCE)
├─ Contrast (7 emotional dimensions, pole oscillation)
├─ Witness (mark emission, ghosts, crystal compression)
└─ Witness-Adaptive Bridge (transparent adaptation)

LAYER 4: INTELLIGENCE
├─ Player Modeling (micro/macro skill tracking)
├─ Colony Intelligence (enemy learning, patterns)
├─ Colony Memory (pheromone persistence)
├─ Personality (enemy trait variation)
└─ Axiom Guards (4 True Axioms verification)

LAYER 5: RENDERING
├─ GameCanvas (2D Canvas, 8-layer pipeline)
├─ Components (DeathOverlay, UpgradeUI, CrystalView, etc.)
├─ Vignette (health-based tunnel vision)
└─ Crescendo (combo-based saturation/brightness)
```

### Performance Profile

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Frame Budget | ~13ms | <16ms | ✅ GOOD |
| Input Latency | <1ms | <1ms | ✅ GOOD |
| Particle Cap | 500 | 500 | ✅ GOOD |
| Re-render Rate | Selective | Selective | ✅ GOOD |

### Extension Points (Where to Add)

1. **Systems** → `systems/*.ts` (add new file, export from index.ts)
2. **Abilities** → `systems/abilities.ts` (ABILITY_POOL array)
3. **Combos** → `systems/combos.ts` (COMBO_RECIPES array)
4. **Enemy Types** → `systems/enemies.ts` (BEE_BEHAVIORS config)
5. **Events** → `systems/events.ts` (GameEvent union type)
6. **Particles** → `systems/juice.ts` (Particle type enum)
7. **Sounds** → `systems/audio.ts` (synthesis functions)
8. **Components** → `components/*.tsx` (React components)
9. **Hooks** → `hooks/*.ts` (game loop integration)

---

## II. SCOPE EXPANSION STRATEGY

### Near-Term (1-2 Weeks): Complete THE BALL

**Current Gap:** THE BALL is specified but needs polish refinement.

**Actions:**
1. **Audio Perfection** — TRUE SILENCE phase must be *actually* silent (verify no sound leaks)
2. **Escape Gap Tuning** — Gap rotation speed/size for skill expression
3. **Formation Density** — Visual bee arrangement during sphere phase
4. **Temperature Visualization** — Screen-space heat shimmer effect
5. **Death Dignity** — Cooking phase ends with respectful animation

**Success Metric:** 80% of playtesters identify THE BALL as "the memorable moment."

### Mid-Term (2-4 Weeks): Content Depth

**New Systems to Add:**

| System | Purpose | Scope |
|--------|---------|-------|
| **Pheromone Trails** | Visual communication paths between bees | Medium |
| **Environmental Hazards** | Honeycomb zones with special effects | Medium |
| **Boss Encounters** | Scripted Royal Guard patterns | Large |
| **Run Modifiers** | Challenge variants (fast enemies, no upgrades) | Small |
| **Achievement Marks** | Witnessed accomplishments (first BALL escape) | Small |

**New Abilities to Add:**

```typescript
// Suggested ability concepts (verb-based)
'counter'     // Parry enemy attacks for burst damage
'devour'      // Execute low-health enemies for healing
'phase'       // Brief invincibility during dash
'siphon'      // Steal enemy speed on hit
'detonate'    // Sacrifice health for AoE
'manifest'    // Create decoy that draws aggro
```

### Long-Term (1-3 Months): Scope Multiplication

**Major Features:**
1. **The Queen** — Final boss encounter after wave 12-15
2. **Hive Modes** — Different arenas with unique mechanics
3. **Hornet Variants** — Character selection with different base abilities
4. **Daily Seeds** — Seeded runs for competition
5. **Replay System** — Watch crystallized runs with ghost overlay

---

## III. DEPTH STRATEGY (Mastery Curves)

### Skill Expression Ladders

Each mechanic should have a **floor** (anyone can use) and **ceiling** (experts can optimize):

| Mechanic | Floor | Ceiling |
|----------|-------|---------|
| **Movement** | WASD to move | Precise kiting patterns, graze farming |
| **Melee** | Click to attack | Direction-based stance combos, cancel timing |
| **Apex Strike** | Space to dash | Chain strikes, bloodlust stacking, lock-aim separation |
| **Upgrades** | Pick any three | Synergy hunting, archetype optimization |
| **THE BALL** | Find the gap | Gap timing prediction, escape direction optimization |

### Emergent Complexity Opportunities

1. **Combo Discovery Depth**
   - Current: Combos unlock on ability selection
   - Opportunity: Order-dependent combos (A→B→C ≠ C→B→A)

2. **Enemy Ecology**
   - Current: Each bee type has fixed behavior
   - Opportunity: Bee type interactions (scouts alert guards, workers protect queens)

3. **Build Divergence**
   - Current: 6 archetypes with overlap
   - Opportunity: Archetype locks (commit to path, unlock exclusive abilities)

4. **Metamorphosis Complexity**
   - Current: 2+ pulsing enemies = colossal
   - Opportunity: Fusion type depends on input bees (worker+guard ≠ scout+scout)

### Mastery Metrics (Track & Display)

```typescript
interface MasteryProfile {
  // Displayed post-run
  graceEfficiency: number;     // % of near-misses that built frenzy
  chainMastery: number;        // Average apex strike chain length
  buildFocus: number;          // Synergy completion rate
  ballEscapes: number;         // Times escaped THE BALL
  waveReached: number;         // Peak progression

  // Hidden (affects adaptation)
  dodgeRate: number;           // Attacks avoided / attacks faced
  damageEfficiency: number;    // Damage dealt / damage taken
  upgradeCoherence: number;    // How focused were selections?
}
```

---

## IV. QUALIA STRATEGY (Experiential Quality)

### Art Evolution Path

**Phase 1: Procedural Polish (Current)**
- Canvas 2D rendering with shape-based entities
- Color-coded by bee type/state
- Particle system for feedback

**Phase 2: Sprite Integration (Next)**
- Load sprite sheets per VFX_SPEC.md specifications
- Implement animation state machines
- Maintain shape silhouettes for readability
- Add idle/attack/recovery frame variations

**Phase 3: Atmospheric Depth**
- Background honeycomb layers (parallax)
- Lighting system (glow sources, shadows)
- Weather effects (pollen drift, heat waves)

### Animation Priority Queue

| Animation | Current | Target | Impact |
|-----------|---------|--------|--------|
| **Player Idle** | Static circle | 4-frame breathing + mandible clicks | HIGH |
| **Player Attack** | Arc flash | 6-frame windup → strike → hold | HIGH |
| **Bee Death** | Particle burst | Spiral descent + honey drip | MEDIUM |
| **THE BALL Forming** | Glow ring | Swirling bee particles → solidify | HIGH |
| **Apex Strike** | Dash line | Motion blur + impact freeze | HIGH |
| **Upgrade Select** | Card appear | Card flip + glow burst | LOW |

### Juice Calibration

**Screen Shake Audit:**
```
Current:               Target (more impactful):
workerKill: 2px        workerKill: 2px (keep)
guardKill: 5px         guardKill: 6px (slightly more)
bossKill: 14px         bossKill: 18px (dramatic)
multiKill: 6px         multiKill: 8px (reward chains)
massacre: 15px         massacre: 20px + chromatic aberration
```

**Freeze Frame Audit:**
```
Current:               Target (more punch):
significantKill: 2f    significantKill: 3f
multiKill: 4f          multiKill: 5f
massacre: 6f           massacre: 8f + 0.3x slowmo
bossKill: N/A          bossKill: 12f + bass drop
```

### Legibility Improvements

1. **Telegraph Clarity**
   - Add arc preview for melee attacks
   - Increase telegraph duration (already done in Run 036)
   - Add audio cues per attack type

2. **Enemy State Visibility**
   - Glow intensity indicates behavior phase
   - Recovery state = distinct desaturated appearance
   - Attacking = white outline

3. **Health Communication**
   - Player health bar always visible (not just low HP)
   - Enemy health bars on damaged enemies (optional toggle)
   - Vignette more gradual (current is jarring)

4. **HUD Simplification**
   - Wave/Score always visible
   - Combo counter more prominent
   - XP bar more satisfying (shimmer on near-level)

---

## V. DEVELOPMENT WORKFLOW

### Session Protocol

```
1. HYDRATE (5 min)
   - Read this document
   - Check PROTO_SPEC.md for axiom reminders
   - Run `npm run typecheck` to ensure clean state

2. FOCUS (Choose ONE)
   - Pick scope expansion OR depth OR qualia
   - Never mix categories in single session
   - Document which focus in commit message

3. IMPLEMENT
   - Start with test if adding system
   - Follow extension point patterns
   - Keep changes under 500 lines

4. VERIFY
   - Run tests: `npm test`
   - Visual check: play 3 runs
   - Performance check: watch FPS counter

5. CRYSTALLIZE
   - Update this document if pattern discovered
   - Update PROTO_SPEC.md if axiom clarified
   - Commit with focus label: [scope], [depth], [qualia]
```

### Quality Gates

Before any merge:
- [ ] Does not violate any of the 4 True Axioms
- [ ] Passes Mirror Test ("Daring, bold, creative, opinionated but not gaudy")
- [ ] Would impress a stranger in 5 seconds
- [ ] Creates a "moment" not just a "function"
- [ ] FPS stays above 55 on mid-tier device

### Anti-Sausage Check

At end of each session:
- [ ] Did I smooth anything that should stay rough?
- [ ] Did I add words Kent wouldn't use?
- [ ] Did I lose any opinionated stances?
- [ ] Is this still daring, bold, creative—or did I make it safe?

---

## VI. PRIORITIZED ROADMAP

### Sprint 1: THE BALL Perfection (Week 1)

- [ ] TRUE SILENCE audio isolation
- [ ] Gap escape feel tuning
- [ ] Temperature visualization (heat shimmer)
- [ ] Cooking death animation dignity
- [ ] Playtester validation (80% memorable)

### Sprint 2: Animation Foundation (Week 2)

- [ ] Sprite sheet loading infrastructure
- [ ] Player idle animation (4-frame)
- [ ] Player attack animation (6-frame)
- [ ] Bee death spiral refinement
- [ ] Animation state machine pattern

### Sprint 3: Depth Mechanics (Week 3-4)

- [ ] Order-dependent combos
- [ ] Archetype commitment system
- [ ] Metamorphosis type variation
- [ ] Mastery metrics display
- [ ] Run modifier system

### Sprint 4: Content Expansion (Week 5-6)

- [ ] 6 new abilities (counter, devour, phase, siphon, detonate, manifest)
- [ ] Environmental hazard zones
- [ ] Pheromone trail visualization
- [ ] Boss encounter (Royal Guard)

### Sprint 5: Polish & Streamability (Week 7-8)

- [ ] Replay system infrastructure
- [ ] Screenshot/clip moments
- [ ] Achievement marks
- [ ] Daily seed system
- [ ] Performance optimization pass

---

## VII. METRICS TO TRACK

### Engagement Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Average Wave Reached | ? | 8+ | Post-run witness |
| Session Length | ? | 15+ min | Timer |
| Runs Per Session | ? | 3+ | Counter |
| THE BALL Encounters | ? | 80%+ of runs | Event tracking |
| Ability Diversity | ? | All 12 used | Upgrade analytics |

### Quality Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Death Attribution | ? | 100% identifiable | Playtest survey |
| Upgrade Satisfaction | ? | 90%+ meaningful | Post-run survey |
| Frame Rate (P95) | ~60 | 55+ | Performance monitor |
| Memory Leaks | ? | 0 | DevTools profiling |

### Voice Metrics (Kent's Assessment)

| Aspect | Question | Target |
|--------|----------|--------|
| **Daring** | Does this take risks? | Yes |
| **Bold** | Is this confident? | Yes |
| **Creative** | Is this novel? | Yes |
| **Opinionated** | Does this commit to a stance? | Yes |
| **Not Gaudy** | Is this restrained elegance? | Yes |

---

## VIII. DECISION LOG

### Architectural Decisions Made

| ID | Decision | Reasoning | Date |
|----|----------|-----------|------|
| AD-1 | Canvas 2D over WebGL | Simplicity, sufficient for 2D bullet-hell, easier debugging | Pre-Run 036 |
| AD-2 | Ref-based state over React state | 60 FPS requires no re-render storms | Pre-Run 036 |
| AD-3 | Event bus for cross-system communication | Loose coupling, replay capability, witness integration | Pre-Run 036 |
| AD-4 | Verb-based upgrades | "Change HOW you play, not HOW MUCH" | Pre-Run 036 |
| AD-5 | 4-phase arc structure | POWER→FLOW→CRISIS→TRAGEDY creates narrative | Pre-Run 036 |
| AD-6 | THE BALL as climax | Real biology, high drama, shareability | Pre-Run 036 |

### Decisions Pending

| ID | Question | Options | Owner |
|----|----------|---------|-------|
| PD-1 | Sprite vs procedural long-term? | Full sprites / Hybrid / Stay procedural | Kent |
| PD-2 | WebGL migration? | Yes (effects) / No (simplicity) | Kent |
| PD-3 | Queen boss design? | Scripted pattern / Adaptive / Hybrid | Kent |
| PD-4 | Multiplayer scope? | Co-op / Versus / Neither | Kent |

---

## IX. APPENDIX: KEY FILE LOCATIONS

```
SPECIFICATIONS
pilots/wasm-survivors-game/PROTO_SPEC.md         — Master specification
pilots/wasm-survivors-game/VFX_SPEC.md           — Visual/audio spec
pilots/wasm-survivors-game/HORNET_SPRITE_SPEC.md — Player sprite design
pilots/wasm-survivors-game/BEE_SPRITES_SPEC.md   — Enemy sprite design
pilots/wasm-survivors-game/ART_STYLE_GUIDE.md    — Visual language

IMPLEMENTATION
impl/claude/pilots-web/src/pilots/wasm-survivors-game/
├─ index.tsx                    — Main component
├─ types.ts                     — Core types
├─ hooks/
│  ├─ useGameLoop.ts           — 60 FPS engine
│  ├─ useInput.ts              — WASD + Space
│  └─ useSoundEngine.ts        — Audio
├─ components/
│  ├─ GameCanvas.tsx           — Rendering pipeline
│  ├─ DeathOverlay.tsx         — Death sequence
│  └─ UpgradeUI.tsx            — Level-up screen
└─ systems/
   ├─ physics.ts               — Movement/collision
   ├─ spawn.ts                 — Wave management
   ├─ enemies.ts               — Bee FSM
   ├─ upgrades.ts              — Ability system
   ├─ abilities.ts             — 61 abilities
   ├─ combos.ts                — 27 combos
   ├─ juice.ts                 — Game feel
   ├─ witness.ts               — Run crystallization
   ├─ contrast.ts              — Emotional tracking
   ├─ formation/               — THE BALL (13 files)
   ├─ apex-strike.ts           — Predator dash
   └─ __tests__/               — System tests
```

---

*"The proof IS the decision. The mark IS the witness."*

**Filed:** 2024-12-29
**Status:** Living Document — Update after each significant session
