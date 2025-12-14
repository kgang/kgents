---
path: plans/ideas-consolidation
status: active
progress: 10
last_touched: 2025-12-14
touched_by: opus-4.5
blocking: []
enables: [k-terrarium-llm-agents, reactive-substrate-unification, clarity]
session_notes: |
  Grand strategy for consolidating, refining, and CULLING plans/ideas.
  TRANSFORMATIVE: Apply spec/principles.md ruthlessly.
  AD-003 (Generative Over Enumerative) is the knife.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.12
  spent: 0.04
  returned: 0.0
---

# Ideas Consolidation: The Generative Cull

> *"Don't build agents. Build the machine that builds agents."* — meta-construction.md
>
> *"Don't enumerate the flowers. Describe the garden's grammar."* — spec/principles.md

**Mission**: Apply the seven principles to the ideas folder. What survives earns its place.

---

## The Brutal Truth

The `plans/ideas/` folder contains 600+ ideas enumerated across 15 sessions. This is **precisely the anti-pattern** that AD-003 (Generative Over Enumerative) warns against:

> "Instead of listing commands, define operads that generate them."

**quick-wins.md** lists 70+ CLI commands by name.
**crown-jewels.md** lists 45 "perfect 10" features.
**master-plan-current.md** tracks which commands are "DONE".

This is counting, not composition. This is documentation of dreams, not machinery that generates reality.

**The cull will be severe.**

---

## Principles as Knife

| Principle | Applied to Ideas | Verdict |
|-----------|------------------|---------|
| **Tasteful** | "Say no more than yes. Not every idea deserves an agent." | 600 ideas → ~10 survive |
| **Curated** | "No parking lot of half-baked ideas" | Session files are parking lot |
| **Generative** | "Define grammars that generate compositions, not instances" | Command lists are anti-pattern |
| **Composable** | "Agents compose via `>>`" | Single command ideas don't compose |
| **Heterarchical** | "No fixed hierarchy" | Tiered priority lists impose hierarchy |
| **Joy-Inducing** | "Delight in interaction" | Lists don't spark joy |

---

## Classification: Alive, Compost, Delete

### ALIVE (Keep & Enhance)

These align with principles and serve active work:

| Document | Why It Lives | Synergy |
|----------|--------------|---------|
| `impl/meta-construction.md` | IS the generative approach (AD-003) | Foundation for everything |
| `impl/categorical-critique.md` | Identifies the enumeration problem | Theoretical grounding |
| `master-plan-current.md` | Active tracking (but needs refocus) | k-terrarium-llm-agents |

### COMPOST (Archive with Honor)

Historical value, no longer actionable:

| Document | Why It's Compost | Archive Path |
|----------|------------------|--------------|
| All 15 `session-*.md` | Brainstorm archaeology | `_archive/ideas/sessions/` |
| `impl/quick-wins.md` | **Enumeration anti-pattern** | `_archive/ideas/anti-patterns/` |
| `impl/crown-jewels.md` | **Enumeration anti-pattern** | `_archive/ideas/anti-patterns/` |
| `impl/medium-complexity.md` | Project list, not operad | `_archive/ideas/` |
| `impl/cross-synergy.md` | Combination list, not composition grammar | `_archive/ideas/` |
| `impl/master-plan.md` | Superseded by master-plan-current | `_archive/ideas/` |
| `kentspicks.md` | Curated enumeration (still enumeration) | `_archive/ideas/` |
| `strategic-recommendations-*.md` | Historical snapshot | `_archive/ideas/` |
| `idea-audit-summary.md` | Meta-document about dead documents | `_archive/ideas/` |

### DELETE (Truly Dead)

Nothing survives this category after archiving.

---

## The Survivor Surgery

### 1. meta-construction.md → The New Core

This document IS the answer. It defines:
- Primitives (13 atomic agents as polynomial functors)
- Operads (composition grammar)
- Sheaves (local → global emergence)

**Enhancement needed**: Wire to active plans.

```markdown
# Additions to meta-construction.md

## Active Integration Points

### K-Terrarium LLM Agents (TOP PRIORITY)
The SOUL_OPERAD with operations {introspect, challenge, shadow, dialectic}
generates all K-gent CLI commands via CLIAlgebra functor.

### Reactive Substrate Unification
Widget definitions are polynomial functors:
- Positions = render targets (CLI, TUI, marimo, JSON)
- Directions = state updates (Signal.set, Signal.update)
- Transitions = project(target) → rendered output

### Process
Don't enumerate `kg soul vibe`, `kg soul drift`, `kg soul tense`.
Define:
```python
SOUL_OPERAD = Operad(
    operations={
        "vibe": Operation(arity=0),      # eigenvector summary
        "drift": Operation(arity=0),     # temporal delta
        "tense": Operation(arity=0),     # held tensions
        "shadow": Operation(arity=1),    # Jung analysis
        "dialectic": Operation(arity=2), # Hegel synthesis
    }
)
# CLI commands derived: operad.derive_cli() → handlers
```
```

### 2. categorical-critique.md → The Why

Rename: `impl/why-generative.md`

This document explains WHY enumeration is wrong. It grounds the cull in theory.

### 3. master-plan-current.md → Refocus

The current master-plan tracks "which commands are DONE". This is backwards.

**Refocus**:
- Track operad implementation progress
- Track generative machinery completeness
- Measure: "How many valid compositions can we generate?" not "How many commands shipped?"

---

## Synergy with In-Flight Work

### K-Terrarium LLM Agents (Kent's TOP PRIORITY)

From `_focus.md`:
> "TOP PRIORITY: Functioning, sophisticated LLM-backed agents, live in k-terrarium. Kent says 'this is amazing' (HARD REQUIREMENT)."

The ideas folder should **directly serve this**. What survives:
- SOUL_OPERAD definition (generates soul commands)
- Streaming pipeline operators (composable, not enumerated)
- Ambient context injection (a single morphism, not a feature list)

What dies:
- Lists of "fun CLI commands"
- Tiered priority rankings
- Sprint assignments

### Reactive Substrate Unification

From `plans/reactive-substrate-unification.md`:
> "The widget IS the state machine. The UI is merely a projection."

This IS polynomial functor thinking. The ideas folder should amplify this:
- Widget definitions as PolyAgent[RenderTarget, StateUpdate, RenderedOutput]
- Projectors as morphisms between categories
- Signal/Computed/Effect as the reactive grammar

### AD-003 Enforcement

The consolidation enforces AD-003:

| Before | After |
|--------|-------|
| `quick-wins.md`: 70 commands | `SOUL_OPERAD.operations`: 5 primitives → infinite compositions |
| `crown-jewels.md`: 45 features | Operad derivation rules |
| Tiered priority lists | Operad composition laws |

---

## Execution Plan

### Phase 1: Archive the Compost

```bash
# Create archive structure
mkdir -p plans/_archive/ideas/sessions
mkdir -p plans/_archive/ideas/anti-patterns

# Archive sessions (historical brainstorming)
mv plans/ideas/session-*.md plans/_archive/ideas/sessions/

# Archive enumeration anti-patterns (with explicit labeling)
mv plans/ideas/impl/quick-wins.md plans/_archive/ideas/anti-patterns/
mv plans/ideas/impl/crown-jewels.md plans/_archive/ideas/anti-patterns/
mv plans/ideas/impl/medium-complexity.md plans/_archive/ideas/
mv plans/ideas/impl/cross-synergy.md plans/_archive/ideas/
mv plans/ideas/impl/master-plan.md plans/_archive/ideas/

# Archive meta-documents
mv plans/ideas/kentspicks.md plans/_archive/ideas/
mv plans/ideas/strategic-recommendations-*.md plans/_archive/ideas/
mv plans/ideas/idea-audit-summary.md plans/_archive/ideas/
```

### Phase 2: Elevate the Survivors

```bash
# Rename for clarity
mv plans/ideas/impl/categorical-critique.md plans/ideas/impl/why-generative.md

# meta-construction.md stays, gets enhanced
# master-plan-current.md stays, gets refocused
```

### Phase 3: Enhance the Core

Add to `meta-construction.md`:
1. Active integration points (k-terrarium, reactive-substrate)
2. Concrete operad definitions (SOUL_OPERAD, WIDGET_OPERAD)
3. Derivation examples showing how operads generate CLI

Refocus `master-plan-current.md`:
1. Replace command tracking with operad progress
2. Replace "DONE" checkboxes with composition coverage
3. Add metric: "generative coverage ratio"

### Phase 4: Create Living Index

New `plans/ideas/README.md`:

```markdown
# Ideas: Generative Machinery

> *"Don't enumerate the flowers. Describe the garden's grammar."*

## The Core

| Document | Purpose |
|----------|---------|
| `impl/meta-construction.md` | Primitives + Operads + Sheaves = Emergence |
| `impl/why-generative.md` | Why enumeration is the anti-pattern |
| `master-plan-current.md` | Active tracking of generative machinery |

## The Operads (Generate Everything)

| Operad | Generates | Coverage |
|--------|-----------|----------|
| SOUL_OPERAD | K-gent CLI commands | ~ |
| WIDGET_OPERAD | I-gent visualizations | ~ |
| INTROSPECTION_OPERAD | H-gent analyses | ~ |

## Integration Points

- **k-terrarium-llm-agents**: SOUL_OPERAD powers streaming dialogue
- **reactive-substrate-unification**: WIDGET_OPERAD powers multi-target rendering

## Archive

Historical brainstorming in `plans/_archive/ideas/`.
Enumeration anti-patterns explicitly labeled in `plans/_archive/ideas/anti-patterns/`.
```

---

## What Gets Better

### Before (Enumeration Hell)

```
plans/ideas/
├── 15 session files (600+ ideas)
├── impl/
│   ├── quick-wins.md (70 commands)
│   ├── crown-jewels.md (45 features)
│   ├── medium-complexity.md (projects)
│   └── ...
└── meta-documents (4)

Total: 30 files, ~565KB, enumerated instances
```

### After (Generative Core)

```
plans/ideas/
├── README.md (living index)
├── master-plan-current.md (refocused tracking)
└── impl/
    ├── meta-construction.md (THE answer)
    ├── why-generative.md (THE reasoning)
    ├── developer-education.md (learning paths)
    ├── metrics-reflection.md (measurement)
    └── qa-strategy.md (quality)

Total: 7 files, ~100KB, generative machinery

Archived: 23 files in _archive/ideas/ (honored, not forgotten)
```

### Quality Improvement

| Metric | Before | After |
|--------|--------|-------|
| Files | 30 | 7 |
| LOC | ~15,000 | ~3,000 |
| Ideas enumerated | 600+ | 0 |
| Operads defined | 0 | 3+ |
| Compositions derivable | 0 | Infinite |
| Aligned with principles | Partially | Fully |
| Serves TOP PRIORITY | Weakly | Directly |

---

## New Ideas Worth Adding

The cull makes room for higher-quality ideas:

### 1. SOUL_OPERAD Definition

```python
# The actual operad that replaces 70+ enumerated commands
SOUL_OPERAD = Operad(
    name="soul",
    primitives=["ground", "introspect", "shadow", "dialectic", "challenge"],
    laws=[
        Law("introspect >> shadow == shadow >> introspect"),  # Commutativity
        Law("ground >> X == X"),  # Identity
    ],
    derive_cli=lambda op: f"kg soul {op.name}"
)
```

### 2. Widget Polynomial Protocol

```python
# From reactive-substrate-unification, formalized
class WidgetPolynomial(PolyAgent[RenderTarget, StateUpdate, RenderedOutput]):
    """Widget as polynomial functor per AD-002."""

    positions = frozenset({RenderTarget.CLI, RenderTarget.TUI, RenderTarget.MARIMO, RenderTarget.JSON})

    def directions(self, target: RenderTarget) -> FrozenSet[StateUpdate]:
        return frozenset({Signal.set, Signal.update, Effect.run})

    def transition(self, target: RenderTarget, update: StateUpdate) -> tuple[RenderTarget, RenderedOutput]:
        return (target, self.project(target))
```

### 3. The "Amazing" Test

From k-terrarium-llm-agents:

> "Kent says 'this is amazing' to the agent (HARD REQUIREMENT)"

This is a wow-test, not a feature list. Add to meta-construction:

```python
@wow_test
def test_kent_says_amazing():
    """
    Success criterion: Genuine 'amazing' reaction.

    Evidence:
    - < 200ms first token (responsive)
    - Uses eigenvectors (personalized)
    - Pipelines compose (compositional)
    - Live metrics visible (observable)
    """
    ...
```

---

## Courage Check

Per N-Phase Cycle:

> "The agent does not describe work. The agent DOES work."

| Wrong | Right |
|-------|-------|
| "Consider archiving these files..." | Archive complete. 23 files moved. |
| "You might want to refocus..." | master-plan-current.md refocused. |
| "Next steps would be..." | Phase 1 DONE. Phase 2 executing. |

---

## Ledger

```yaml
phase_ledger:
  PLAN: touched
  RESEARCH: complete  # Read all files, understood terrain
  DEVELOP: complete   # Classification criteria established
  STRATEGIZE: complete  # Execution plan defined
  CROSS-SYNERGIZE: complete  # k-terrarium, reactive-substrate connected
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  sipped: 0.04
  budget_remaining: 0.08
branches:
  - blocking: []
  - parallel: []
  - deferred: []
```

---

## Continuation

⟿[IMPLEMENT]
/hydrate
handles: scope=ideas-consolidation; phase=IMPLEMENT; ledger={PLAN:done,RESEARCH:done,STRATEGIZE:done}; entropy=0.06
mission: Execute the cull. Archive compost. Enhance survivors. Create living index.
actions:
  - Create archive directories
  - Move 23 files to archive (sessions + anti-patterns)
  - Enhance meta-construction.md with integration points
  - Refocus master-plan-current.md
  - Create plans/ideas/README.md
exit: 7 files remain. Generative machinery elevated. k-terrarium integration clear.

---

*"The garden's grammar produces infinite flowers. The list of flowers produces nothing."*
