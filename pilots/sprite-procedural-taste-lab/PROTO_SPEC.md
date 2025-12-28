# Sprite Procedural Taste Lab

Status: **production**

> *"Every character has a story. The pixels are just how you hear it."*

---

## ⚠️ Implementation Directive

**This spec is a BUILD order, not a design document.**

When this PROTO_SPEC is consumed for regeneration:
- **Implement ALL laws (L1-L6)** — complete set
- **Implement ALL QAs (QA-1 through QA-5)** — complete set
- **Real sprite rendering** — actual pixels, not placeholder descriptions
- **Real animation** — visible movement, not static images
- **Emit actual witness marks** — not just capture intent

### Failure Conditions (Automatic Fail)

The system is **broken** if:

| Condition | Impact |
|-----------|--------|
| **FC-1** UI describes sprites but doesn't render them | L1 violated |
| **FC-2** Characters look generic/asset-pack quality | Soul missing |
| **FC-3** System never proposes or pushes back | Transcription, not collaboration |
| **FC-4** Backstory doesn't map to visible elements | L2 violated |
| **FC-5** No actual animation playback | L3 violated |

### Quality Gates (Mandatory)

| Gate | Requirement | Failure = Block |
|------|-------------|-----------------|
| **QG-1** | Sprites visibly render in UI | Yes |
| **QG-2** | Zero TypeScript errors | Yes |
| **QG-3** | All Laws have corresponding implementation | Yes |
| **QG-4** | Animation playable (idle at minimum) | Yes |
| **QG-5** | Design history navigable (L5) | Yes |
| **QG-6** | Export produces usable sprite sheet | Yes |

---

## ⚠️ EXECUTOR MANDATE: Opinionated Agency

**This spec requires the executing agent to exercise aesthetic judgment, not just mechanical translation.**

The agent MUST:
- **Have opinions** about what looks good, what feels alive, what communicates character
- **Propose unexpected directions** that honor the backstory but surprise the user
- **Push back** when a direction feels generic or lifeless—suggest alternatives
- **Curate quality** over quantity: one stunning character beats ten mediocre ones
- **Synthesize coherence** across visual design, animation, and narrative

The agent is a **creative collaborator**, not a transcription service. When the spec is ambiguous, the agent should make a bold choice and justify it. The user can redirect, but the agent should never produce something it wouldn't be proud to show.

---

## Narrative

This is an **animation studio for creating characters with soul**.

The user describes a character—their history, personality, fears, dreams. The system proposes visual designs: body shape, clothing, color palette, idle animations, movement style. Each visual choice reflects something true about the character.

A grumpy mushroom wizard doesn't just *look* grumpy—he *shuffles* with impatience, his hat droops when he's defeated, his spores puff when he's angry. The backstory lives in the movement.

The lab is where character concepts become **commercial-quality animated sprites** through iterative co-evolution between user and system.

## Personality Tag

*"This pilot believes that great characters are discovered, not manufactured. The system proposes, the user refines, and together they find someone worth caring about."*

---

## The Primary Artifact: Animated Character Sprites

A character in this lab is NOT an abstract concept. It is a **concrete visual artifact**:

| Component | Description | Example |
|-----------|-------------|---------|
| **Sprite Sheet** | 64x64 or 128x128 pixel art frames | 8 frames idle, 6 frames walk, 4 frames action |
| **Color Palette** | 8-16 colors that express mood/era | Warm earth tones for a homey baker; neon accents for a cyberpunk hacker |
| **Silhouette** | Recognizable at 16x16 thumbnail | The mushroom cap, the flowing cape, the mechanical arm |
| **Animation Cycles** | Looping movements that reveal personality | Nervous fidgeting, confident strut, weary shuffle |
| **Backstory Card** | 2-3 sentences of character essence | "Mira was a palace guard until she saw what the king really did. Now she protects the streets instead." |

**The sprite is the deliverable.** Everything else (taste tracking, branch exploration, crystals) serves the goal of producing a sprite you'd put in a commercial game.

---

## The Core Interaction Loop

```
┌─────────────────────────────────────────────────────────────────┐
│  1. USER DESCRIBES                                               │
│     "A retired pirate who now runs a bakery. She's tough but    │
│      kind, misses the sea, has a mechanical leg."               │
├─────────────────────────────────────────────────────────────────┤
│  2. SYSTEM PROPOSES (with opinion!)                             │
│     → 3 visual concepts with rationale                          │
│     → "I gave her salt-weathered blues and a flour-dusted       │
│        apron. The mechanical leg clicks when she walks—         │
│        she's proud of it, not hiding it."                       │
├─────────────────────────────────────────────────────────────────┤
│  3. USER REFINES                                                 │
│     "Love the leg detail! But make her warmer—she's found       │
│      happiness in the bakery."                                  │
├─────────────────────────────────────────────────────────────────┤
│  4. SYSTEM ITERATES                                              │
│     → Adjusted palette (more golden/amber tones)                │
│     → Softened idle animation (content sway vs. restless scan)  │
│     → "Added a slight smile and relaxed shoulders. The sea      │
│        is in her past; the bread is her present."               │
├─────────────────────────────────────────────────────────────────┤
│  5. REPEAT until character feels ALIVE                          │
└─────────────────────────────────────────────────────────────────┘
```

**Each iteration produces viewable sprites.** Not descriptions of sprites. Actual rendered pixel art with animation.

---

## Quality Bar: Commercial Level

This pilot aims for **professional indie game quality**. Reference points:

- Celeste character expressiveness
- Stardew Valley warmth and readability
- Hyper Light Drifter atmospheric silhouettes
- Undertale personality-in-pixels

A character is "done" when:
1. You could put it in a game and it wouldn't look out of place
2. A stranger could describe their personality from the sprite alone
3. The animation makes you *feel* something

---

## Objectives

1. **Backstory → Pixels**: Every visual choice traces back to character truth. "Why is she wearing red?" → "Because she's still mourning and red is how her culture honors the dead."

2. **Animation as Character**: Movement isn't decoration—it's revelation. How they stand, shift, react. A confident character and a nervous character with the same silhouette should feel completely different.

3. **Iterative Refinement**: The first proposal is a starting point, not a destination. User and system converge on the character through dialogue.

4. **Wild Exploration**: When the user says "surprise me," the system should propose something unexpected but justified. Not random—*imaginative*.

5. **Commercial Export**: Final characters can be exported as sprite sheets ready for game engines.

---

## Laws

- **L1 Visual-First Law**: Every UI state shows rendered sprites, not just metadata. The character is always visible.

- **L2 Backstory-Trace Law**: Every visual element can be traced to a backstory element. Click on the mechanical leg → see "lost in the Storm of '47, rebuilt by her first mate."

- **L3 Animation-Personality Law**: Idle animations must reflect emotional state. A happy character and sad character cannot have the same idle loop.

- **L4 Proposal-Rationale Law**: When the system proposes a design, it must explain *why*. "I chose heavy boots because she needs to feel grounded—her past was chaotic."

- **L5 Iteration-Memory Law**: Previous iterations are preserved. The user can say "go back to the version with the longer cape" and the system retrieves it.

- **L6 Quality-Gate Law**: The system should flag when a design feels generic or incoherent. "This silhouette is hard to read at small sizes—consider simplifying the shoulder detail."

---

## Qualitative Assertions

- **QA-1** The user should feel like they're **collaborating with an artist**, not filling out a form.

- **QA-2** Proposed characters should have **surprising-but-fitting** details the user didn't specify but immediately recognizes as right.

- **QA-3** The difference between first iteration and final should be **visibly dramatic**—co-evolution produces better results than either party alone.

- **QA-4** Watching the idle animation should make you **want to know more** about the character.

- **QA-5** The system's rationale should make you say **"oh, that's clever"** at least once per session.

---

## Anti-Success (Failure Modes)

The system fails if:

- **Generic output**: Characters look like they came from an asset pack. No soul, no specificity.

- **Description-only**: The UI talks about sprites but doesn't show them. "Your character has warm colors" without rendering warm colors.

- **User does all the work**: The system just executes instructions without proposing, pushing back, or adding creative value.

- **Backstory-visual disconnect**: The character has a rich backstory but the sprite could belong to anyone. The visual doesn't tell the story.

- **One-and-done**: First proposal is final. No iteration, no refinement, no co-evolution.

- **Timid agent**: The system never disagrees, never suggests alternatives, never has opinions. Just transcribes.

---

## Technical Approach: Procedural Generation + AI Guidance

The system uses a **hybrid approach**:

| Layer | Method | Purpose |
|-------|--------|---------|
| **Backstory → Traits** | LLM interpretation | "retired pirate baker" → `[seafaring, domestic, mechanical, warm]` |
| **Traits → Visual Params** | Constrained generation | Traits map to palette, proportions, silhouette rules |
| **Visual Params → Pixels** | Procedural pixel art | Algorithm generates actual sprite frames |
| **Animation → Personality** | Motion libraries + blending | Idle/walk/action cycles from personality parameters |
| **Critique → Refinement** | LLM + heuristics | Evaluate coherence, readability, expressiveness |

The system should be able to generate **actual viewable sprites**, not placeholders. If true procedural generation is too complex for initial implementation, the system may use:
- Curated base sprites with parameter-driven variations
- Color/proportion transforms on template characters
- Composite layering (body + clothing + accessories + effects)

**The key constraint: something must render.** A character that exists only as text has failed.

---

## Backstory Elements → Visual Mappings

Examples of how narrative becomes pixels:

| Backstory Element | Visual Expression |
|-------------------|-------------------|
| "Lost her family young" | Muted palette, protective posture, eyes that look past you |
| "Former soldier" | Rigid stance, economic movements, scars integrated into design |
| "Loves to cook" | Warm colors, flour dusting, comfortable roundness, happy idle sway |
| "Hiding a secret" | Asymmetric design, one hand often near pocket/bag, glancing animation |
| "Mechanical augmentation" | Visible gears/plates, different movement on enhanced limbs, subtle glow |
| "Royalty in disguise" | Refined gestures despite simple clothes, unconscious grace |

The system should recognize these patterns and apply them—but also **surprise the user** with connections they didn't anticipate.

---

## Animation Vocabulary

Characters have **movement signatures**:

| Personality Trait | Idle Animation | Walk Cycle | Action Pose |
|-------------------|----------------|------------|-------------|
| Confident | Slight sway, hands on hips | Long stride, head high | Decisive, weight forward |
| Nervous | Fidgeting, looking around | Quick short steps | Flinch-ready, defensive |
| Weary | Slumped shoulders, slow blink | Heavy footfalls, head down | Reluctant, conserving energy |
| Joyful | Bouncy, can't stand still | Almost skipping | Enthusiastic, full extension |
| Mysterious | Minimal movement, watchful | Gliding, minimal bob | Precise, controlled |

These aren't prescriptive—they're vocabulary. A confident-but-weary character might have the sway but also the slumped shoulders.

---

## Iteration Tracking (Taste Evolution)

Each character has a **design history**:

```
Character: Mira the Pirate Baker
├── v1: "Tough, sea-worn, suspicious" [rejected: too cold]
├── v2: "Warmer palette, softer lines" [refined: keep warmth, add edge]
├── v3: "Golden apron, steel in eyes" [accepted as base]
│   └── v3.1: "Mechanical leg detail" [exploring]
│   └── v3.2: "Simplified silhouette" [exploring]
└── v4: [current working version]
```

The user can navigate this history, branch from any point, and understand how they got here.

---

## kgents Integrations

| Primitive | Role | Application |
|-----------|------|-------------|
| **Witness Mark** | Record design decisions | "Added scar because she's a survivor, not a victim" |
| **Witness Crystal** | Compress character journey | "Mira evolved from cold exile to warm guardian in 7 iterations" |
| **Galois Loss** | Measure design coherence | Flag when visual elements contradict backstory |
| **Trail** | Navigate design history | Browse/branch from previous iterations |

## Quality Algebra

> *See: `spec/theory/experience-quality-operad.md` for universal framework*

This pilot instantiates the Experience Quality Operad via `SPRITE_LAB_QUALITY_ALGEBRA`:

| Dimension | Instantiation |
|-----------|---------------|
| **Contrast** | visual_variety, personality_expression, backstory_alignment |
| **Arc** | concept → exploration → refinement → crystallization |
| **Voice** | soulful ("Has character?"), coherent ("Visuals match story?"), alive ("Animation reveals personality?") |
| **Floor** | no_generic_output, no_description_only, visual_renders, animation_plays |

**Weights**: C=0.25, A=0.25, V=0.50

**Implementation**: `impl/claude/services/experience_quality/algebras/sprite_lab.py`

**Domain Spec**: `spec/theory/domains/sprite-lab-quality.md`

---

## Canary Success Criteria

1. A user describes a character in 2-3 sentences and receives **three distinct visual proposals** within 30 seconds, each with a visible sprite and rationale.

2. After 3-5 iterations, the character should be **dramatically better** than the first proposal—and neither user nor system could have gotten there alone.

3. A stranger looking at the final sprite can **infer at least two backstory elements** correctly. ("She seems like she's been through something hard but found peace.")

4. The user says **"I didn't think of that but it's perfect"** at least once per character.

5. The exported sprite sheet is **immediately usable** in a game engine (proper transparency, consistent frame size, animation-ready). Animated GIF export lets you share characters instantly.

---

## Scope

**In Scope:**
- Character sprite generation (64x64 or 128x128)
- Idle, walk, and 1-2 action animation cycles
- Color palette generation tied to backstory
- Silhouette design for readability
- Iterative refinement with history
- PNG sprite sheet export (game-engine ready)
- Animated GIF export (shareable, looping)

**Out of Scope (for now):**
- Full game integration (engine plugins, etc.)
- Dialogue/voice generation
- Environment/background art
- Team collaboration features
- Real-time multiplayer editing

---

## Implementation Guidance for Regeneration

When regenerating this pilot, the agent should:

1. **Start with visuals**: The first thing built should be a sprite renderer, even if it's just displaying static placeholder art.

2. **Make something move**: Idle animation should be visible in iteration 1. Movement brings characters to life.

3. **Build the dialogue**: The backstory→proposal→refinement loop is core. Even with simple visuals, the conversation should feel alive.

4. **Layer complexity**: Start with palette + silhouette, then add animation, then add procedural variation.

5. **Have taste**: Don't just implement—curate. If a feature feels unnecessary, skip it. If something feels missing, add it.

6. **Show, don't tell**: Never describe a sprite when you could render it. Never talk about animation when you could play it.

---

*"The best characters feel like they existed before you found them. Your job is just to help them be seen."*
