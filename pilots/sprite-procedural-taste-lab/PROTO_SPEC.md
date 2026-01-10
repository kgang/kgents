# Hornet Siege Art Forge

Status: **production**

> *"The colony has its defenders. The hornet has its swagger. Every pixel tells their story."*

---

## The Integration: Art Forge + Game Development

**This pilot is the art department for Hornet Siege.** Every generation run produces assets that integrate directly into `impl/claude/pilots-web/src/pilots/wasm-survivors-game/`.

The Art Forge does NOT generate abstract "characters with soul" — it generates **specific game assets** for a specific game: sprites, effects, UI elements, and animations that embody the tragedy of predator vs. collective.

### Cross-Reference Architecture

```
pilots/sprite-procedural-taste-lab/PROTO_SPEC.md  (this file)
         ↓ generates assets for ↓
pilots/wasm-survivors-game/PROTO_SPEC.md          (game design spec)
pilots/wasm-survivors-game/BEE_SPRITES_SPEC.md    (bee visual language)
pilots/wasm-survivors-game/HORNET_SPRITE_SPEC.md  (hornet visual language)
         ↓ outputs to ↓
impl/claude/pilots-web/src/pilots/wasm-survivors-game/  (game code)
```

---

## Implementation Directive

**This spec is a BUILD order for game art assets.**

When this PROTO_SPEC is consumed for regeneration:
- **Generate GAME-READY sprites** — exact sizes, palettes, and formats from BEE/HORNET_SPRITE_SPEC
- **Implement ALL laws (L1-L7)** — complete set
- **Implement ALL QAs (QA-1 through QA-6)** — complete set
- **Real pixel art** — actual rendered sprites, not descriptions
- **Real animation frames** — sprite sheets with frame data
- **Emit witness marks** — design decisions are traceable

### Failure Conditions (Automatic Fail)

| Condition | Impact |
|-----------|--------|
| **FC-1** UI describes sprites but doesn't render them | L1 violated |
| **FC-2** Assets don't match game palette (COLORS in types.ts) | Integration broken |
| **FC-3** System accepts all input without pushback | Transcription, not collaboration |
| **FC-4** Sprites don't express personality (swagger/dignity) | Soul missing |
| **FC-5** No animation playback | L3 violated |
| **FC-6** Exported assets unusable in game engine | Primary purpose failed |

### Quality Gates (Mandatory)

| Gate | Requirement | Failure = Block |
|------|-------------|-----------------|
| **QG-1** | Sprites visibly render at correct sizes (12-48px) | Yes |
| **QG-2** | Zero TypeScript errors | Yes |
| **QG-3** | All Laws have corresponding implementation | Yes |
| **QG-4** | Animation playable (idle at minimum) | Yes |
| **QG-5** | Design history navigable (L6) | Yes |
| **QG-6** | Export produces game-ready sprite sheets | Yes |
| **QG-7** | Palette matches COLORS constant from types.ts | Yes |

---

## Narrative: The Art Department

This is the **animation studio for Hornet Siege**.

The game tells a tragedy: an apex predator invades a colony, massacres defenders, and ultimately falls to collective intelligence. The Art Forge ensures every sprite embodies this narrative:

- **The Hornet** has swagger. It KNOWS it will lose. It hunts anyway.
- **The Bees** are dignified defenders. They are the HEROES of their story.
- **THE BALL** is clip-worthy spectacle — the moment when the colony wins.
- **Effects** sell the fantasy: kills feel like PUNCHES, deaths feel EARNED.

The Forge is where an artist (human) and system (AI) collaborate to make this tragedy visually stunning.

### Personality Tag

*"This pilot believes that great game art is discovered through dialogue. The system proposes with opinion, the artist refines with vision, and together they forge sprites worth showing off."*

---

## Asset Categories

### Category 1: The Hornet (Player Character)

**Source**: `pilots/wasm-survivors-game/HORNET_SPRITE_SPEC.md`

| Property | Specification |
|----------|---------------|
| **Size** | 48x48 pixels |
| **Palette** | 10 colors (see spec) |
| **Animations** | IDLE (4), IDLE_AGGRO (4), MOVE (4×4), ATTACK (6), DASH (6), HIT (2), DEATH (6) |
| **Sprite Sheet** | 384×288 pixels (8 cols × 6 rows) |
| **Personality** | SWAGGER — confident, never panicked, magnificent in death |

**Key Constraints**:
- Mandibles visible in EVERY frame
- Eyes #FFD700 (Warning Yellow)
- 3+ orange/black bands on abdomen
- Death animation maintains dignity

### Category 2: The Bees (Enemy Types)

**Source**: `pilots/wasm-survivors-game/BEE_SPRITES_SPEC.md`

| Type | Size | Shape | Palette | Key Visual |
|------|------|-------|---------|------------|
| **Worker** | 12×12 | Circle | Amber #D4920A | Round, plump, golden glow |
| **Scout** | 14×10 | Triangle | Honey #E5B84A + Cyan #00D4FF | Streamlined, speed trails |
| **Guard** | 20×24 | Square | Dark Amber #B87A0A | Armor plates, blocky |
| **Propolis** | 16×16 | Diamond | Resin #A08020 + Violet #6B2D5B | Visible projectile organ |
| **Royal** | 28×32 | Octagon | Purple #6B2D5B + Gold #FFD700 | Crown accent, elite |

**Animation States** (all bee types):
- IDLE (2 frames) — Wing flutter
- CHASE (4 frames) — Forward lean, fast wings
- TELEGRAPH (3 frames) — Glow + pullback (CRITICAL for readability)
- ATTACK (2 frames) — Lunge
- RECOVERY (2 frames) — Dimmed, slower
- DEATH (5 frames) — Spiral descent + pollen burst

**Key Constraints**:
- Each type has DISTINCT silhouette (instant recognition)
- Warm amber palette (defenders, not monsters)
- Death animations show heroic sacrifice, not fodder disintegration

### Category 3: Visual Effects

| Effect | Description | Integration Point |
|--------|-------------|-------------------|
| **Kill Particle** | Spiral + scatter + pollen burst | `systems/juice.ts` |
| **XP Orb** | Amber glow, float toward player | `types.ts XPOrb` |
| **Damage Flash** | Orange→Red, fragment burst | `PARTICLES.damageFlash` |
| **Formation Glow** | Gold lines connecting bees | `systems/formation/render.ts` |
| **THE BALL Heat** | Red shimmer, temperature indicator | `BallPhase` rendering |
| **Graze Spark** | Cyan spark on near-miss | Risk-reward feedback |
| **Venom Drip** | Purple trail from hornet mandibles | Attack satisfaction |

**Palette from types.ts COLORS**:
```typescript
amber: '#FFB800'
honey: '#D4A017'
honeycomb: '#8B6914'
hiveDark: '#1a1a0f'
hiveLight: '#2a2a1f'
danger: '#FF4444'
warning: '#FFAA00'
formation: '#FF6B6B'
heat: '#FF3300'
```

### Category 4: UI Elements

| Element | Description | Style |
|---------|-------------|-------|
| **Health Bar** | Amber fill, honeycomb frame | Warm, organic |
| **XP Bar** | Pollen gold, drip effect on gain | Satisfying |
| **Wave Indicator** | Hexagonal badge | Hive aesthetic |
| **Upgrade Icons** | 32×32, clear silhouette | Readable at glance |
| **Death Screen Elements** | Dignified amber, not harsh red | Ceremony, not punishment |
| **THE BALL Warning** | Pulsing red, heat rising | Dread, not panic |

---

## The Core Interaction Loop

```
┌─────────────────────────────────────────────────────────────────┐
│  1. ARTIST REQUESTS                                              │
│     "I need a Guard Bee sprite. Make it feel like a tank that   │
│      holds the line. Reference BEE_SPRITES_SPEC.md."            │
├─────────────────────────────────────────────────────────────────┤
│  2. FORGE PROPOSES (with opinion!)                              │
│     → 3 visual concepts with rationale                          │
│     → "I gave it heavy armor plates because Guards don't chase  │
│        — they BLOCK. The square silhouette = unmistakable at    │
│        a glance. Darker amber says 'I've weathered attacks.'"   │
├─────────────────────────────────────────────────────────────────┤
│  3. ARTIST REFINES                                              │
│     "Love the plates! But the silhouette blends with Royal at   │
│      distance. Make it more distinctly rectangular."            │
├─────────────────────────────────────────────────────────────────┤
│  4. FORGE ITERATES (or pushes back!)                            │
│     → Adjusted proportions (wider than tall)                    │
│     → Or: "If we go more rectangular, we lose the 'heft' read.  │
│        What about adding vertical armor striping instead?       │
│        That preserves bulk while differentiating from Royal."   │
├─────────────────────────────────────────────────────────────────┤
│  5. REPEAT until asset is GAME-READY                            │
└─────────────────────────────────────────────────────────────────┘
```

**Each iteration produces viewable sprites.** Not descriptions. Actual rendered pixel art with animation.

---

## Laws

### Asset Laws

- **L1 Visual-First Law**: Every UI state shows rendered sprites, not just metadata. The asset is always visible.

- **L2 Game-Palette Law**: Every generated asset uses ONLY colors from the established palettes (COLORS constant, BEE_SPRITES_SPEC, HORNET_SPRITE_SPEC). No drift allowed.

- **L3 Animation-Personality Law**: Animations must reflect entity personality. Hornet has swagger (weight shift, confident stance). Bees have purpose (coordinated, heroic). Death animations have dignity.

- **L4 Proposal-Rationale Law**: When the system proposes a design, it must explain *why* in terms of gameplay readability and emotional resonance. "Square silhouette = tank read at a glance."

- **L5 Spec-Reference Law**: Every asset proposal must cite the relevant spec (BEE_SPRITES_SPEC, HORNET_SPRITE_SPEC, PROTO_SPEC). No orphan designs.

- **L6 Iteration-Memory Law**: Previous iterations are preserved. The artist can say "go back to the wider Guard variant" and the system retrieves it.

- **L7 Export-Ready Law**: Final assets export in formats directly usable by the game:
  - PNG sprite sheets with consistent frame sizes
  - JSON animation metadata (frame timing, loop data)
  - Palette files for validation

### Integration Laws

- **L-INT-1**: Generated assets must match the type definitions in `types.ts` (BeeType, EnemyType sizes, etc.)

- **L-INT-2**: Color values must be exact hex matches to COLORS constant (no #FFB801 when COLORS.amber is #FFB800)

- **L-INT-3**: Sprite dimensions must match spec (Worker 12×12, Hornet 48×48, etc.)

- **L-INT-4**: Animation frame counts must match spec requirements (Hornet ATTACK = 6 frames, etc.)

---

## Qualitative Assertions

- **QA-1** The artist should feel like they're **collaborating with an opinionated art director**, not filling out an asset request form.

- **QA-2** Proposed assets should have **gameplay-justified details** the artist didn't specify but immediately recognizes as right. "Oh, the telegraph glow makes the attack readable!"

- **QA-3** The difference between first iteration and final should be **visibly dramatic** — co-evolution produces better game art than either party alone.

- **QA-4** Watching the idle animation should communicate **personality instantly**. You should KNOW the Hornet has swagger. You should FEEL the Guard's defensive stance.

- **QA-5** The system's rationale should reference **gameplay impact**: "This silhouette reads at distance during swarm chaos."

- **QA-6** Exported assets should **work on first import** into the game. No manual cleanup required.

---

## Anti-Success (Failure Modes)

| Failure | What It Looks Like | Violates |
|---------|-------------------|----------|
| **Generic output** | Bees look like "asset pack insects" | Soul, QA-4 |
| **Description-only** | UI says "amber-colored Guard" without rendering it | L1 |
| **Palette drift** | Uses #DAA520 instead of #D4A017 | L2, L-INT-2 |
| **Silent acceptance** | System never pushes back on bad directions | QA-1 |
| **Spec ignorance** | Proposes 64×64 Hornet when spec says 48×48 | L5, L-INT-3 |
| **One-and-done** | First proposal is final, no iteration | QA-3, L6 |
| **Export failure** | Sprite sheet has wrong frame alignment | L7, QA-6 |

---

## Technical Approach: Constrained Procedural Generation

The system uses a **spec-constrained approach**:

| Layer | Method | Constraint Source |
|-------|--------|-------------------|
| **Type → Shape** | Spec lookup | BEE_SPRITES_SPEC silhouette rules |
| **Shape → Palette** | Constrained selection | COLORS constant + spec palettes |
| **Palette → Pixels** | Procedural pixel art | Size from spec, colors from palette |
| **Pixels → Animation** | Frame generation | Frame counts from spec, timing from spec |
| **Animation → Personality** | Motion signature | Swagger/dignity/heroism from narrative |

The system CANNOT propose:
- Colors not in the established palettes
- Sizes that don't match spec
- Animation frame counts that differ from spec
- Silhouettes that contradict type identity

The system CAN propose:
- Variations within constraints (different armor plate arrangements)
- Personality interpretations (MORE swagger, DIFFERENT dignity)
- Detail choices (which pixels highlight, shade distribution)
- Timing variations within acceptable ranges

---

## Asset Integration Workflow

### From Forge to Game

```
1. FORGE generates sprite sheet (PNG)
   ↓
2. FORGE generates animation metadata (JSON)
   {
     "type": "guard",
     "frames": { "idle": [0,1], "chase": [2,3,4,5], ... },
     "timing": { "idle": 200, "chase": 100, ... },
     "palette": ["#B87A0A", "#4A3000", "#C4A000"]
   }
   ↓
3. Export to impl/claude/pilots-web/src/pilots/wasm-survivors-game/assets/
   ↓
4. Update sprite rendering code to use new assets
   ↓
5. Witness mark records: "Guard Bee v3 integrated, swagger level increased"
```

### Validation Checklist (Per Asset)

- [ ] Dimensions match spec
- [ ] Colors are exact palette matches
- [ ] Animation frame count correct
- [ ] Sprite sheet alignment verified
- [ ] Idle animation loops smoothly
- [ ] Silhouette distinct from other types
- [ ] Personality readable in 0.1 seconds
- [ ] Exported files load in game without error

---

## kgents Integrations

| Primitive | Role | Application |
|-----------|------|-------------|
| **Witness Mark** | Record design decisions | "Made Guard wider to differentiate from Royal at distance" |
| **Witness Crystal** | Compress asset evolution | "Guard Bee evolved from generic tank to distinctive blocker in 4 iterations" |
| **Galois Loss** | Measure spec adherence | Flag when assets drift from established visual language |
| **Trail** | Navigate design history | Browse/branch from previous asset versions |

### Quality Algebra Instantiation

```
HORNET_SIEGE_ART_ALGEBRA = {
  contrast: [
    "visual_variety" (not all bees look same),
    "personality_expression" (swagger vs dignity),
    "spec_alignment" (matches source specs)
  ],
  arc: [
    "request" → "proposal" → "iteration" → "refinement" → "export"
  ],
  voice: [
    "gameplay_voice" ("Is it readable in chaos?"),
    "narrative_voice" ("Does it tell the tragedy?"),
    "integration_voice" ("Does it work in the game?")
  ],
  floor: [
    "palette_exact_match",
    "dimension_exact_match",
    "animation_playable",
    "export_functional"
  ]
}
```

---

## Canary Success Criteria

1. **Request → Proposals (30s)**: Artist describes needed asset, receives 3 distinct visual concepts with rationale within 30 seconds.

2. **Iteration Quality**: After 3-5 iterations, the asset is dramatically better than first proposal — and neither artist nor system could have gotten there alone.

3. **Instant Recognition**: A player seeing the sprite for 0.1 seconds can identify the entity type (Worker vs Guard vs Royal).

4. **Swagger/Dignity Test**: Watching the Hornet idle, you FEEL the confidence. Watching a Bee die, you FEEL the sacrifice.

5. **Game Integration**: Exported sprite sheets load into the game and render correctly on first attempt.

6. **Spec Adherence**: Random palette sampling shows 100% match to established colors.

---

## Scope

**In Scope:**
- Hornet player sprite (48×48, full animation set)
- Five bee types (Worker, Scout, Guard, Propolis, Royal)
- Kill/damage/effect particles
- UI elements (health bar, XP bar, upgrade icons)
- THE BALL visual effects
- Sprite sheet export (PNG)
- Animation metadata export (JSON)
- Design iteration history

**Out of Scope (for now):**
- 3D models
- Full game backgrounds (handled by game renderer)
- Sound design (separate system)
- Marketing assets (separate effort)
- Localization of UI text

---

## Implementation Guidance for Regeneration

When regenerating this pilot, the agent should:

1. **Load the specs first**: Read BEE_SPRITES_SPEC.md and HORNET_SPRITE_SPEC.md before generating any assets.

2. **Enforce constraints**: Reject/flag any proposal that violates palette, dimension, or silhouette constraints.

3. **Start with rendering**: The first thing built should display actual pixels, even if placeholder.

4. **Make something move**: Idle animation should be visible in iteration 1.

5. **Build the dialogue**: The request→proposal→refinement loop is core. System must have opinions.

6. **Integrate continuously**: Test exports against the actual game early and often.

7. **Have taste within constraints**: The spec provides the boundaries. Within those boundaries, be bold.

8. **Show, don't tell**: Never describe a sprite when you could render it.

---

## Voice Anchor

> *"Daring, bold, creative, opinionated but not gaudy."*

Within the constraints of established specs, the Forge should:
- Propose unexpected details that improve gameplay readability
- Push back when directions would hurt visual hierarchy
- Celebrate the tragedy — the Hornet's swagger, the Bees' heroism
- Make every pixel earn its place

---

## The Mirror Test

Before shipping any asset, ask:

| Quality | Check |
|---------|-------|
| **Spec-Aligned** | Does this match BEE/HORNET_SPRITE_SPEC exactly? |
| **Game-Ready** | Will this work on first import? |
| **Personality** | Can you FEEL the swagger/dignity/heroism? |
| **Readable** | Identifiable in 0.1s during swarm chaos? |
| **Collaborative** | Did system propose something artist didn't expect but loves? |
| **Traceable** | Is the design evolution witnessed? |

---

*"The colony always wins. The art should show why they deserve to."*

*"The hornet knows the score and hunts anyway. The sprite should know too."*

---

## Appendix A: Quick Reference Palettes

### Hornet Palette (10 colors)
```
#FF6B00 - Hornet Orange
#CC5500 - Burnt Orange
#993D00 - Deep Orange
#1A1A1A - Venom Black
#2D1F3D - Bruise Purple
#0D0D0D - Void Black
#FFD700 - Warning Yellow
#FFE55C - Pale Yellow
#4A6B8C - Wing Blue
#2A3B4C - Wing Shadow
```

### Bee Palette (by type)
```
Worker:   #D4920A, #FFE066, #FFF8E7
Scout:    #E5B84A, #00D4FF, #FFD700
Guard:    #B87A0A, #4A3000, #C4A000
Propolis: #A08020, #6B2D5B, #D4A5D4
Royal:    #6B2D5B, #FFD700, #FFFFFF
```

### Effect Palette (from COLORS constant)
```
amber:      #FFB800
honey:      #D4A017
honeycomb:  #8B6914
danger:     #FF4444
warning:    #FFAA00
formation:  #FF6B6B
heat:       #FF3300
```

---

## Appendix B: Sprite Size Reference

```
         SPRITE SIZES (to scale, 4px = *)

Hornet (48×48)     Royal (28×32)    Guard (20×24)
************       *******          *****
************       *******          *****
************       *******          *****
************       *******          *****
************       *******          *****
************       *******          *****
************       *******
************       *******

Propolis (16×16)   Scout (14×10)    Worker (12×12)
****               ***              ***
****               ***              ***
****               **               ***
****
```

---

## Appendix C: Animation Frame Counts

| Entity | Idle | Chase | Telegraph | Attack | Recovery | Death |
|--------|------|-------|-----------|--------|----------|-------|
| Hornet | 4 | 4×4 | - | 6 | - | 6 |
| Worker | 2 | 4 | 3 | 2 | 2 | 5 |
| Scout | 2 | 4 | 3 | 2 | 2 | 5 |
| Guard | 2 | 4 | 3 | 2 | 2 | 5 |
| Propolis | 2 | 4 | 3 | 2 | 2 | 5 |
| Royal | 2 | 4 | 3 | 2 | 2 | 5 |

---

**Filed**: 2025-12-29
**Version**: 2.0.0 — Hornet Siege Integration Edition
**Compression**: This spec + BEE_SPRITES_SPEC + HORNET_SPRITE_SPEC = complete art direction
