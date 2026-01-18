# UX Flow: Dogfooding (kgents in kgents)

> *"The garden knows itself. The system teaches itself. The user discovers alongside."*

**Status**: Active Plan
**Date**: 2026-01-17
**Meta-Goal**: Represent kgents' decision hierarchy, specs, and implementation fully within kgents
**Principles**: Generative, Composable, Heterarchical

---

## The Meta-Goal

**kgents must eat its own dogfood.**

Every decision, spec, and implementation in kgents should be:
1. **Visible** as K-Blocks in the Constitutional Graph
2. **Traceable** to its axiomatic foundation
3. **Annotated** with gotchas, derivations, and implementations
4. **Witnessed** with decision marks and crystals

This is not documentation. This is **self-description as first-class content**.

---

## The Radical Insight

When you open kgents for the first time, you're not just seeing "an app."

You're seeing **kgents explaining itself**:
- The 22 Genesis K-Blocks ARE the kgents Constitution
- The derivation edges ARE the kgents decision hierarchy
- The specs in `spec/` ARE ingested K-Blocks
- The implementation in `impl/` IS linked via implementation edges

**The product IS the documentation IS the system.**

---

## What Gets Dogfooded

### 1. The Constitution (Already Done)

The 22 Genesis K-Blocks are kgents explaining its foundation:

| Layer | Content | Source |
|-------|---------|--------|
| L0 | 4 axioms | CONSTITUTION.md |
| L1 | 7 primitives | Minimal Kernel |
| L2 | 7 principles | CONSTITUTION.md |
| L3 | 4 architecture patterns | AD-009, k-block.md, etc. |

**User Experience**: First-run Genesis flow shows the Constitution. User can trace any principle to its axiom.

### 2. The Specs (Ingest Required)

Every spec file in `spec/` should be ingested:

```
spec/
├── protocols/
│   ├── witness.md      → 14 K-Blocks
│   ├── k-block.md      → 18 K-Blocks
│   ├── genesis-clean-slate.md → 12 K-Blocks
│   └── ...
├── agents/
│   ├── d-gent.md       → 8 K-Blocks
│   └── ...
└── ui/
    ├── severe-stark.md → 5 K-Blocks
    └── ...
```

Each spec:
1. Gets ingested via the Ingest flow
2. K-Blocks are proposed (axioms, principles, gotchas)
3. Derivation edges link back to Constitution
4. Implementation edges link to `impl/`

### 3. The Decisions (Witness Required)

Every significant decision in kgents should be a witnessed mark:

```bash
# Example: The decision to use SEVERE STARK
kg decide --kent "Playful, animated UI" \
          --kent-reasoning "Joy-inducing, delightful" \
          --claude "Dense, stark UI" \
          --claude-reasoning "Yahoo Japan density, information-first" \
          --synthesis "SEVERE STARK: Dense but with personality in microinteractions" \
          --why "Both joy AND density achievable through restraint"
```

These decisions become K-Blocks in the graph, linked to:
- The principles they embody (JOY_INDUCING, TASTEFUL)
- The specs they inform (severe-stark.md)
- The implementations they constrain (CSS constraints)

### 4. The Implementation (Annotation Required)

Every implementation file should have annotation links:

```python
# services/witness/core/mark.py

@dataclass(frozen=True)
class Mark:
    """
    📦 Links to: spec/protocols/witness.md#Mark
    ⚡ Implements: witness:axiom:mark
    ◉ Embodies: COMPOSABLE, GENERATIVE
    """
    id: MarkId
    action: str
    reasoning: str | None
    timestamp: datetime
    tags: frozenset[str]
```

These annotations:
1. Create implementation edges in the graph
2. Allow navigation: K-Block → implementation
3. Allow reverse navigation: implementation → K-Block

---

## The Dogfood Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                           CONSTITUTIONAL GRAPH                                   │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                           │  │
│  │    L0: ZERO SEED (4 axioms)                                               │  │
│  │         │                                                                 │  │
│  │         ▼                                                                 │  │
│  │    L1: MINIMAL KERNEL (7 primitives)                                      │  │
│  │         │                                                                 │  │
│  │         ▼                                                                 │  │
│  │    L2: PRINCIPLES (7 principles)                                          │  │
│  │         │                                                                 │  │
│  │         ▼                                                                 │  │
│  │    L3: ARCHITECTURE (4 patterns)                                          │  │
│  │                                                                           │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                            │                                                    │
│                            │ derives_from                                       │
│                            ▼                                                    │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                           │  │
│  │    SPEC K-BLOCKS (ingested from spec/)                                    │  │
│  │    ├── witness.md (14 K-Blocks)                                           │  │
│  │    ├── k-block.md (18 K-Blocks)                                           │  │
│  │    ├── genesis-clean-slate.md (12 K-Blocks)                               │  │
│  │    └── ...                                                                │  │
│  │                                                                           │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                            │                                                    │
│                            │ implements                                         │
│                            ▼                                                    │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                           │  │
│  │    IMPLEMENTATION K-BLOCKS (linked from impl/)                            │  │
│  │    ├── services/witness/ → witness.md K-Blocks                            │  │
│  │    ├── services/k_block/ → k-block.md K-Blocks                            │  │
│  │    └── web/src/ → UI spec K-Blocks                                        │  │
│  │                                                                           │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                           │  │
│  │    DECISION K-BLOCKS (from kg decide)                                     │  │
│  │    ├── decision:severe-stark → JOY_INDUCING, TASTEFUL                     │  │
│  │    ├── decision:monadic-isolation → COMPOSABLE                            │  │
│  │    └── ...                                                                │  │
│  │                                                                           │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## The Dogfood Flow

### Step 1: Ingest All Specs

```bash
# Bulk ingest all specs
kg ingest spec/ --recursive

# Review and confirm K-Block proposals
# (Interactive review per file)
```

Result: All specs become K-Block graphs, linked to Constitution.

### Step 2: Link Implementations

```bash
# Scan implementations for annotations
kg annotate scan impl/claude/services/

# Or add manually
kg annotate impl/claude/services/witness/core/mark.py \
  --links spec/protocols/witness.md#Mark \
  --implements witness:axiom:mark
```

Result: Implementation files linked to spec K-Blocks.

### Step 3: Import Decision History

```bash
# Import existing decisions from witness history
kg dogfood import-decisions

# Creates K-Blocks for each significant decision
```

Result: Decision history becomes navigable K-Blocks.

### Step 4: Continuous Dogfooding

From now on:
- Every new spec → Ingest → K-Blocks
- Every new decision → `kg decide` → K-Block
- Every new implementation → Annotation → Links

---

## UX for Dogfood Navigation

### "How does witness.md implement COMPOSABLE?"

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ TRACE: COMPOSABLE → witness.md                                                  │
│ ─────────────────────────────────────────────────────────────────────────────── │
│                                                                                 │
│ genesis:L2:composable                                                           │
│ "Agents are morphisms in a category"                                            │
│         │                                                                       │
│         │ embodies                                                              │
│         ▼                                                                       │
│ witness:axiom:mark                                                              │
│ "Every action leaves a mark"                                                    │
│         │                                                                       │
│         │ implements                                                            │
│         ▼                                                                       │
│ witness:impl:mark_store                                                         │
│ services/witness/core/mark_store.py:MarkStore                                   │
│         │                                                                       │
│         │ uses                                                                  │
│         ▼                                                                       │
│ witness:impl:mark_dataclass                                                     │
│ services/witness/core/mark.py:Mark                                              │
│                                                                                 │
│ ─────────────────────────────────────────────────────────────────────────────── │
│ Path length: 4 edges                                                            │
│ Constitution → Spec → Impl → Code                                               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### "What decisions led to SEVERE STARK?"

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ DECISION TRAIL: SEVERE STARK                                                    │
│ ─────────────────────────────────────────────────────────────────────────────── │
│                                                                                 │
│ decision:2025-12-18:ui-density                                                  │
│ "How dense should the UI be?"                                                   │
│ Kent: "Playful, animated" / Claude: "Yahoo Japan dense"                         │
│ Synthesis: "Dense but with personality in microinteractions"                    │
│         │                                                                       │
│         │ led_to                                                                │
│         ▼                                                                       │
│ decision:2025-12-20:severe-stark                                                │
│ "What is the design philosophy?"                                                │
│ Kent: "I want it to feel intense" / Claude: "SEVERE STARK"                      │
│ Synthesis: "SEVERE STARK: No joy in layout, joy in microinteraction"            │
│         │                                                                       │
│         │ informs                                                               │
│         ▼                                                                       │
│ spec/ui/severe-stark.md                                                         │
│ "Dense, intense, no joy in spacing"                                             │
│         │                                                                       │
│         │ implements                                                            │
│         ▼                                                                       │
│ impl/claude/web/src/styles/layout-constraints.css                               │
│ "--spacing-xs: 2px; --spacing-sm: 4px; ..."                                     │
│                                                                                 │
│ ─────────────────────────────────────────────────────────────────────────────── │
│ Principles embodied: TASTEFUL, JOY_INDUCING, CURATED                            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### "What gotchas apply to K-Block editing?"

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ GOTCHAS: K-Block                                                                │
│ ─────────────────────────────────────────────────────────────────────────────── │
│                                                                                 │
│ ⚠ kblock:gotcha:no-nested-kblocks                                               │
│   "K-Blocks are flat, never nested"                                             │
│   Source: k-block.md, line 912                                                  │
│   Related: harness.fork(), harness.entangle()                                   │
│                                                                                 │
│ ⚠ kblock:gotcha:no-auto-save                                                    │
│   "Auto-save defeats monadic isolation"                                         │
│   Source: k-block.md, line 924                                                  │
│   Related: harness.save()                                                       │
│                                                                                 │
│ ⚠ kblock:gotcha:view-state-in-sheaf                                             │
│   "All view state derives from canonical content"                               │
│   Source: k-block.md, line 936                                                  │
│   Related: KBlockSheaf, view coherence                                          │
│                                                                                 │
│ ─────────────────────────────────────────────────────────────────────────────── │
│ Total gotchas: 3                                                                │
│ [Navigate to source] [Show in graph]                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Notes

### Dogfood Command Group

```bash
# New commands for dogfooding
kg dogfood ingest-all      # Ingest all specs
kg dogfood link-impl       # Scan and link implementations
kg dogfood import-decisions # Import decision history
kg dogfood validate        # Check dogfood completeness
kg dogfood report          # Generate dogfood coverage report
```

### Dogfood Metrics

```python
@dataclass
class DogfoodReport:
    """Report on dogfood completeness."""

    specs_ingested: int
    specs_total: int
    impl_linked: int
    impl_total: int
    decisions_captured: int
    gotchas_indexed: int

    constitutional_coverage: float  # % of Constitution linked to specs
    spec_coverage: float           # % of specs with K-Blocks
    impl_coverage: float           # % of impl files linked

    orphan_kblocks: list[str]      # K-Blocks with no derivation
    orphan_impl: list[str]         # Impl files with no links
```

### Validation

```python
async def validate_dogfood() -> DogfoodValidation:
    """Validate dogfood completeness."""

    # 1. Every L2 principle should be embodied by at least one spec K-Block
    for principle in PRINCIPLES:
        embodiments = await graph.find_embodiments(principle.id)
        if not embodiments:
            yield Warning(f"{principle.title} has no embodiments in specs")

    # 2. Every spec K-Block should derive from Constitution
    for kblock in await graph.get_spec_kblocks():
        if not kblock.derivations_from:
            yield Error(f"{kblock.id} has no constitutional derivation")

    # 3. Every axiom in specs should have implementation links
    for kblock in await graph.get_axiom_kblocks():
        impl_links = await graph.get_impl_links(kblock.id)
        if not impl_links:
            yield Warning(f"{kblock.id} has no implementation links")

    # 4. Every decision should link to principles
    for decision in await graph.get_decision_kblocks():
        if not decision.principles:
            yield Warning(f"Decision {decision.id} has no principle links")
```

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Spec coverage | 100% of `spec/` ingested |
| Constitutional linkage | 100% of spec K-Blocks derive from Constitution |
| Implementation linkage | > 80% of impl files linked |
| Decision capture | All significant decisions in graph |
| Orphan K-Blocks | 0 (every K-Block has derivation) |

---

## The End State

When dogfooding is complete:

1. **New user opens kgents** → sees Constitutional Graph
2. **Clicks TASTEFUL** → sees all specs that embody TASTEFUL
3. **Clicks witness.md** → sees its K-Block decomposition
4. **Clicks Mark axiom** → sees implementation link
5. **Clicks implementation** → opens code in editor
6. **Sees gotcha** → understands constraint
7. **Creates their own K-Block** → links to Constitution

**The system teaches itself to the user by being fully navigable.**

---

*"The product IS the documentation IS the system."*
