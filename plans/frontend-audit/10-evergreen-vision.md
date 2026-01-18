# The Evergreen Vision: Frontend as Anti-Sloppification Machine

> *"The fundamental thing to avoid is the suppression and atrophy of human creativity, authenticity, and expression."*
> *"There is no such thing as shipping. Only continuous iteration and evolution."*

**Status:** Canonical Vision
**Created:** 2026-01-17
**Supersedes:** 08-protocol-integration.md, 09-metaphysical-container.md
**Grounded In:** Constitution, Axiom Interview (2026-01-17)

---

## I. The Foundational Axioms

This vision is grounded in discovered axioms, not stipulated requirements.

### A0: The Ethical Floor (Pre-existing)

> Nothing should make people question their existence at a sanity or emotional level.

**Frontend Implication:** No dark patterns. No manipulation. No anxiety-inducing states. Errors guide, never blame.

### A1: Creativity Preservation (L1-001)

> The fundamental thing to avoid is the suppression and atrophy of human creativity, authenticity, and expression.

**Frontend Implication:** The UI must AMPLIFY Kent's creative capacity, not replace it. Every interaction should leave Kent more capable, not more dependent.

**Anti-patterns to eliminate:**
- Auto-complete that overwrites intent
- Suggestions that feel like pressure
- Workflows that impose structure before understanding
- "AI did this for you" that removes agency

### A2: The Sloppification Axiom (L1-002)

> LLMs touching something inherently sloppifies it.

**Frontend Implication:** The UI must make sloppification VISIBLE. Every AI-touched element must be distinguishable from human-authored elements. The UI is a **sloppification detector**, not a sloppification hider.

**Design principle:**
```
HUMAN_AUTHORED → Full intensity (#e0e0e8)
AI_ASSISTED    → Medium intensity (#8a8a94) + indicator
AI_GENERATED   → Low intensity (#5a5a64) + prominent indicator
NEEDS_REVIEW   → Amber glow (#c4a77d) until human confirms
```

### A3: Evolutionary Epistemology (L1-003)

> Everything can be questioned and proven false. Accepting impermanence allows truth through evolution and survival.

**Frontend Implication:** Nothing in the UI is permanent. Every component, every design decision, every workflow is provisional and falsifiable. The UI must support its own evolution.

**Design principle:**
- Version everything
- Show derivation (why does this exist?)
- Enable deletion without fear
- Git history is the only archive

### A4: The No-Shipping Axiom (L1-004)

> There is no such thing as shipping. Only continuous iteration and evolution.

**Frontend Implication:** No "launch" state. No "complete" features. The UI is a garden that grows, not a product that ships. Evergreen development means every session adds value.

**Design principle:**
- No "beta" labels (everything is beta forever)
- No "coming soon" (build when needed)
- No feature flags hiding incomplete work (incomplete = absent)
- The current state IS the product

### A5: Delusion/Creativity Boundary (L1-005)

> The boundary between AI enabling delusion and AI enabling creativity is unclear.

**Frontend Implication:** The UI must support reflection, anti-defensiveness, and humility. When Kent feels "productive," the UI should help distinguish real progress from motion.

**Design principle:**
- Show evidence, not claims
- Witness marks create accountability
- Dialectic traces show reasoning
- "Claude thinks X" ≠ "X is true"

### A6: The Authority Axiom (L1-006)

> Claude doesn't convince me of anything. I don't put myself in that position.

**Frontend Implication:** The UI never persuades. It presents options, shows evidence, and waits for decision. Claude is evaluated by results, not trusted by default.

**Design principle:**
- No "recommended" badges from AI
- No auto-actions without consent
- Evaluation dashboard: did Claude's suggestions improve outcomes?
- Authority gradient: Kent → Constitution → Evidence → Claude

### A7: Disgust Triggers (L2-001)

> Feeling lost. Things happening that I don't fully understand. The impulse to destroy everything and start over.

**Frontend Implication:** The UI must prevent these states. If Kent feels lost, the UI has failed. If things happen that Kent doesn't understand, the UI has failed.

**Design principle:**
- Always show "where am I?" (path, context, state)
- Always show "what just happened?" (witness trail)
- Always show "how did I get here?" (navigation history)
- "Destroy everything" is a valid action (radical deletion is supported, not prevented)

### A8: Understandability Priority (L2-002)

> Understandability first, but understandable code should immediately factor into compositional form.

**Frontend Implication:** Every UI element must be immediately understandable. But understanding enables composition—elements that can't be combined aren't truly understood.

**Design principle:**
- Simple elements that compose
- No "magic" components
- Composition visible in the UI (show how parts combine)
- If you can't explain it, delete it

---

## II. The Anti-Sloppification Architecture

The frontend is not a view layer. It is an **anti-sloppification machine** that makes AI assistance visible, bounded, and evaluable.

### The Three Containers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HUMAN CONTAINER (Kent)                               │
│  - Full authority                                                           │
│  - Full intensity rendering                                                 │
│  - No AI mediation                                                          │
│  - Direct manipulation only                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                     COLLABORATION CONTAINER (Kent + Claude)                 │
│  - Dialectic visible                                                        │
│  - Sloppification indicators                                                │
│  - Witness marks mandatory                                                  │
│  - Fusion decisions tracked                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                        AI CONTAINER (Claude alone)                          │
│  - Low intensity rendering                                                  │
│  - Prominent "AI generated" indicator                                       │
│  - Requires human review before elevation                                   │
│  - Automatically deprecated if not reviewed                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Sloppification Visibility Protocol

Every element shows its provenance:

```typescript
interface Provenance {
  author: 'kent' | 'claude' | 'fusion';
  confidence: number;        // 0-1, how confident is the authorship
  reviewed: boolean;         // Has human reviewed AI content?
  sloppification_risk: number; // 0-1, how likely is this sloppy?
  evidence: string[];        // Why do we believe this assessment?
}
```

**Visual encoding:**

| Provenance | Rendering | Indicator |
|------------|-----------|-----------|
| kent (human) | Full intensity | None |
| fusion (dialectic) | Full intensity | ⚡ fusion mark |
| claude (AI, reviewed) | Medium intensity | ◇ reviewed |
| claude (AI, unreviewed) | Low intensity + amber border | ◆ needs review |

### The Collapsing Functions

Formal verification and tests are "collapsing functions" that make AI capabilities graspable.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ COLLAPSING FUNCTION: TypeScript                                             │
│ AI output → Type check → Binary (passes/fails)                              │
│ Sloppification collapsed to: "Does it compile?"                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ COLLAPSING FUNCTION: Tests                                                  │
│ AI output → Test suite → Binary (passes/fails)                              │
│ Sloppification collapsed to: "Does it work?"                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ COLLAPSING FUNCTION: Constitutional Scoring                                 │
│ AI output → 7 principles → Score (0-7)                                      │
│ Sloppification collapsed to: "Does it align?"                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ COLLAPSING FUNCTION: Galois Loss                                            │
│ AI output → Compression test → L value (0-1)                                │
│ Sloppification collapsed to: "Is it grounded?"                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Frontend surfaces these collapsing functions:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ COLLAPSE PANEL: Current K-Block                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ TypeScript:    ████████████████████ PASS                                   │
│ Tests:         ████████████████░░░░ 16/20 PASS                             │
│ Constitution:  ██████████████░░░░░░ 5.8/7                                   │
│ Galois (L):    ████████████████████ 0.08 GROUNDED                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ SLOPPIFICATION ASSESSMENT: LOW                                              │
│ Evidence: Types pass, tests mostly pass, principles aligned, grounded.     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## III. The Evergreen Development Loop

No shipping. Only evolution. The frontend embodies this.

### The Garden Metaphor (Literal)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THE GARDEN                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   SEED          SPROUT         BLOOM          WITHER         COMPOST       │
│    ●    ───►    ╱│╲     ───►    ✿     ───►     ╱     ───►      ░           │
│   idea         draft          mature        deprecated      deleted        │
│                                                                             │
│ Every element in the UI has a lifecycle:                                    │
│ - Seeds are ideas (unimplemented)                                           │
│ - Sprouts are drafts (K-Blocks in progress)                                 │
│ - Blooms are mature (reviewed, tested, grounded)                            │
│ - Withered are deprecated (no longer needed)                                │
│ - Compost is deleted (gone, but fed the soil)                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Frontend shows lifecycle state:**

```typescript
interface LifecycleState {
  stage: 'seed' | 'sprout' | 'bloom' | 'wither' | 'compost';
  planted: Date;
  lastTended: Date;
  health: number; // 0-1, based on recent activity
  dependents: string[]; // What relies on this?
}
```

### Session as Tending

Every session is "tending the garden":

```
SESSION START
├─ Review what's withering (unused for 30+ days)
├─ Tend what's sprouting (K-Blocks in progress)
├─ Celebrate what's blooming (recent completions)
└─ Plant new seeds (ideas captured)

SESSION END
├─ Witness marks for decisions made
├─ K-Block saves for work in progress
├─ Compost decisions for deletions
└─ Garden state snapshot
```

**Frontend supports this ritual:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ GARDEN STATUS: 2026-01-17                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Seeds (ideas):     12 │ Sprouts (drafts):  8 │ Blooms (mature): 47         │
│ Withering:          3 │ Composted today:   1 │ Health: 0.82                │
├─────────────────────────────────────────────────────────────────────────────┤
│ ATTENTION NEEDED:                                                           │
│ ├─ [wither] spec/old-protocol.md — unused 45 days, 0 dependents            │
│ ├─ [sprout] K-Block: new-feature — started 3 days ago, 60% complete        │
│ └─ [seed] idea: streaming-optimization — captured, not started             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## IV. The SEVERE STARK Aesthetic (Evolved)

SEVERE STARK remains, but grounded in axioms.

### Why SEVERE STARK? (Axiomatic Grounding)

| Axiom | SEVERE STARK Response |
|-------|----------------------|
| A1 (Creativity) | Dense UI = more information = more creative raw material |
| A2 (Sloppification) | Monochrome = clear provenance indicators stand out |
| A3 (Evolution) | Minimal decoration = less to evolve, faster iteration |
| A4 (No-Shipping) | No polish debt = always presentable, never "almost done" |
| A5 (Delusion) | No celebration = no false sense of completion |
| A6 (Authority) | No persuasive design = UI presents, doesn't recommend |
| A7 (Disgust) | Always visible state = never lost |
| A8 (Understandability) | Simple elements = immediate comprehension |

### Evolved Color System

```css
/* Human Container */
--human-fg: #e0e0e8;           /* Full intensity */
--human-bg: #0a0a0c;           /* Steel-obsidian */

/* Collaboration Container */
--fusion-fg: #e0e0e8;          /* Full intensity */
--fusion-indicator: #8b6bc4;   /* Purple fusion mark */

/* AI Container */
--ai-fg: #5a5a64;              /* Low intensity */
--ai-border: #c4a77d;          /* Amber "needs review" */
--ai-reviewed: #4a6b4a;        /* Muted green "reviewed" */

/* Lifecycle */
--seed: #3a5a7a;               /* Blue-gray (potential) */
--sprout: #5a7a5a;             /* Green-gray (growing) */
--bloom: #e0e0e8;              /* Full intensity (mature) */
--wither: #5a5a64;             /* Fading (deprecated) */
--compost: #3a3a44;            /* Nearly gone (deleting) */

/* Collapsing Functions */
--collapse-pass: #4a6b4a;      /* Muted green */
--collapse-fail: #8b4a4a;      /* Muted red */
--collapse-partial: #8b6b4a;   /* Muted orange */
```

---

## V. The Unified Workspace (Final Form)

### Layout

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ [world] [self] [concept] [void] [time]               KENT │ density:max │ garden:healthy   │
├────────────┬───────────────────────────────────────────────────────────────┬────────────────┤
│            │                                                               │                │
│  NAVIGATE  │                        K-BLOCK                                │   COLLAPSE     │
│  (15%)     │                        (60%)                                  │   (25%)        │
│            │                                                               │                │
│ GARDEN:    │ ┌─────────────────────────────────────────────────────────┐   │ TypeScript: ██ │
│ ├─ 12 seed │ │ spec/principles.md                    [bloom] [fusion]  │   │ Tests: ████░░ │
│ ├─ 8 sprout│ ├─────────────────────────────────────────────────────────┤   │ Constitution: │
│ ├─47 bloom │ │                                                         │   │   ██████░░░░  │
│ └─ 3 wither│ │ # Design Principles                                     │   │ Galois: 0.08  │
│            │ │                                                         │   │               │
│ PATH:      │ │ These seven principles guide all kgents decisions.     │   │ SLOP: LOW     │
│ world.     │ │                                                         │   │               │
│ document.  │ │ ## 1. Tasteful                                          │   │ ───────────── │
│ spec/      │ │                                                         │   │ PROVENANCE:   │
│ principles │ │ > Each agent serves a clear, justified purpose.        │   │ fusion (94%)  │
│            │ │                                                         │   │ reviewed: yes │
│ ASPECTS:   │ │ - **Say "no" more than "yes"**  ◇                      │   │               │
│ [m]anifest │ │ - **Avoid feature creep**       ◇                      │   │ WITNESS:      │
│ [w]itness  │ │ - **Aesthetic matters**         ◆ needs review         │   │ 3 marks today │
│ [t]ransform│ │                                                         │   │ last: 4m ago  │
│            │ └─────────────────────────────────────────────────────────┘   │               │
├────────────┴───────────────────────────────────────────────────────────────┴────────────────┤
│ MODE: NORMAL │ world.document.spec/principles │ ln:42 │ slop:low │ garden:bloom │ EVERGREEN │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Component Architecture

```typescript
// The three containers, implemented
interface WorkspaceProps {
  observer: Observer;           // Kent or guest
  path: AgentesePath;          // Current location
  gardenState: GardenState;    // Lifecycle summary
}

// Navigation shows garden state, not just files
interface NavigationProps {
  garden: GardenState;
  path: AgentesePath;
  aspects: Aspect[];
}

// K-Block shows provenance inline
interface KBlockProps {
  content: string;
  provenance: Map<Range, Provenance>;  // Per-line provenance
  lifecycle: LifecycleState;
}

// Collapse panel shows sloppification assessment
interface CollapsePanelProps {
  typescript: CollapseResult;
  tests: CollapseResult;
  constitution: ConstitutionalScore;
  galois: number;
  overallSlop: 'low' | 'medium' | 'high';
  provenance: Provenance;
  witness: WitnessSummary;
}
```

---

## VI. Implementation Principles

### Principle 1: Build Only What's Understood

From A8: If you can't explain it in one sentence, don't build it.

```
Before implementing anything:
1. Write the one-sentence explanation
2. Write the test that verifies it
3. Write the collapsing function that evaluates it
4. THEN implement
```

### Principle 2: Make Sloppification Visible

From A2: Every AI touch must be visible.

```
Before any AI-assisted feature:
1. Define the provenance indicator
2. Define the "needs review" state
3. Define how human confirmation clears sloppification
4. THEN implement
```

### Principle 3: Support Radical Deletion

From A3 + A7: Everything is falsifiable. Deletion prevents disgust.

```
Before any feature is "done":
1. Verify it can be deleted without breaking dependents
2. Verify git history preserves it
3. Verify no orphan references remain
4. THEN call it complete
```

### Principle 4: No Persuasion

From A6: UI presents, doesn't recommend.

```
Before any suggestion/recommendation:
1. Remove "recommended" language
2. Show evidence, not conclusions
3. Show alternatives with equal weight
4. THEN present the options
```

### Principle 5: Garden First

From A4: No shipping, only tending.

```
Every session:
1. Review garden state
2. Tend what needs attention
3. Plant new seeds
4. Compost what's dead
5. Snapshot the garden
```

---

## VII. The Evergreen Promise

This frontend makes a promise:

1. **It will never suppress Kent's creativity** — It amplifies, never replaces
2. **It will never hide sloppification** — AI assistance is always visible
3. **It will never pretend to be complete** — The garden grows forever
4. **It will never persuade** — It presents evidence and waits
5. **It will never leave Kent lost** — State is always visible
6. **It will always support deletion** — Nothing is precious except the axioms

This is not a product. It is a practice.

This is not a launch. It is a planting.

This is not software. It is a garden.

---

*"The persona is a garden, not a museum."*
*"There is no shipping. Only evolution."*
*"The fundamental thing to avoid is the suppression and atrophy of human creativity."*
