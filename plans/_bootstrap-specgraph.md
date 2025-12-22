# Bootstrap: kgents Self-Hosting via SpecGraph/ASHC/Portal/Interactive Text

> *"The spec is not description—it is generative. The text is not passive—it is interface."*

**Date**: 2025-12-22
**Status**: Brainstorming Document
**Vision**: kgents working on itself FROM INSIDE the system

---

## The Core Insight

We have four powerful frameworks that, when unified, enable **self-hosting**:

| Framework | What It Does | Spec |
|-----------|-------------|------|
| **SpecGraph** | Treats specs as a navigable hypergraph | `typed-hypergraph.md` |
| **ASHC (Derivation)** | Bayesian proof theory with evidence chains | `derivation-framework.md` |
| **Portal Tokens** | Inline expansion UX | `portal-token.md` |
| **Interactive Text** | Specs become live interfaces | `interactive-text.md` |

**The Recursive Vision**:
```
┌─────────────────────────────────────────────────────────────────────┐
│  CURRENT: Specs are read by Claude → Claude implements → Tests pass │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│  FUTURE: Specs ARE the interface → Claude navigates specs via       │
│          portals → Derivation tracks confidence → Marks witness     │
│          decisions → Specs update based on implementation wisdom    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Spec Inventory (What We're Porting)

### Tier 1: Foundation Specs (Bootstrap These First)

These are the categorical primitives that everything else depends on:

| Spec | Path | Lines | Dependencies | Priority |
|------|------|-------|--------------|----------|
| `spec/principles.md` | `concept.principles` | ~1700 | None | **P0** |
| `spec/agents/composition.md` | `concept.composition` | ~300 | principles | **P0** |
| `spec/agents/primitives.md` | `concept.primitives` | ~200 | composition | **P0** |
| `spec/agents/operads.md` | `concept.operads` | ~400 | primitives | **P0** |
| `spec/agents/functors.md` | `concept.functors` | ~300 | composition | **P0** |

**Why P0**: These define the mathematical foundation. Every other spec draws from them.

### Tier 2: Protocol Specs (The Living Infrastructure)

| Spec | Path | Lines | Key Insight |
|------|------|-------|-------------|
| `spec/protocols/agentese.md` | `concept.agentese` | ~600 | "Observation is interaction" |
| `spec/protocols/derivation-framework.md` | `concept.derivation` | ~2000 | Bayesian proof theory |
| `spec/protocols/exploration-harness.md` | `self.explore` | ~800 | Trail as evidence |
| `spec/protocols/portal-token.md` | `self.portal` | ~600 | Inline expansion |
| `spec/protocols/interactive-text.md` | `self.document` | ~700 | Specs are interfaces |
| `spec/protocols/typed-hypergraph.md` | `self.context` | ~500 | Context as graph |

**Why P1**: These are the protocols we're USING to bootstrap. They must be self-describing.

### Tier 3: Agent Genera (Domain Specs)

| Genus | Spec Count | Example Paths |
|-------|------------|---------------|
| K-gent (Soul) | 3 | `self.soul.*` |
| M-gent (Memory) | 5 | `self.memory.*` |
| D-gent (State) | 1 | `self.state.*` |
| W-gent (Wire) | 4 | `world.wire.*` |
| T-gent (Testing) | 2 | `concept.testing.*` |
| Psi-gent (Psychopomp) | 8 | `concept.psi.*` |
| ... | ... | ... |

**Total**: ~60 spec files across 20 genera.

---

## Phase 2: The SpecGraph Structure

### 2.1 Typed Hyperedges for Specs

Every spec becomes a node in the hypergraph. Relationships are hyperedges:

```python
@dataclass
class SpecNode(ContextNode):
    """A spec file as a navigable node."""

    path: str                    # "spec/agents/composition.md"
    agentese_path: str           # "concept.composition"
    title: str                   # "Composition Protocol"
    tier: DerivationTier         # FUNCTOR, POLYNOMIAL, JEWEL, APP

    # Derivation integration
    derives_from: list[str]      # Other specs this extends
    principle_draws: list[str]   # Which principles it instantiates
    confidence: float            # Current confidence from ASHC

    # Hyperedges
    edges: dict[str, list[str]]  # type → destinations

# Edge types for specs:
SPEC_EDGE_TYPES = {
    "extends": "Conceptual extension",      # spec/agents/flux.md extends composition
    "implements": "Implementation link",    # impl/claude/agents/poly/ implements composition
    "tests": "Test coverage",               # tests verify spec claims
    "examples": "Code examples",            # inline examples in spec
    "depends_on": "Hard dependency",        # Can't understand this without that
    "cross_pollinates": "Soft connection",  # Related but independent
    "contradicts": "Tension point",         # Dialectic opportunity
}
```

### 2.2 Auto-Discovery from Spec Content

Parse spec markdown to discover relationships:

```python
async def discover_spec_edges(spec_path: Path) -> dict[str, list[str]]:
    """Parse spec markdown to find hyperedges."""

    content = spec_path.read_text()
    edges = defaultdict(list)

    # Pattern 1: Explicit "See also" / "Related" sections
    see_also = re.findall(r'\*\*See\*\*:?\s*`([^`]+)`', content)
    edges["cross_pollinates"].extend(see_also)

    # Pattern 2: Heritage citations
    heritage = re.findall(r'\*\*Heritage Citation[^:]*\*\*:\s*([^\n]+)', content)
    edges["extends"].extend(heritage)

    # Pattern 3: AGENTESE path references
    agentese_refs = re.findall(r'`((?:world|self|concept|void|time)\.[a-z_.]+)`', content)
    edges["references"].extend(agentese_refs)

    # Pattern 4: Implementation file references
    impl_refs = re.findall(r'`impl/claude/([^`]+)`', content)
    edges["implements"].extend(impl_refs)

    # Pattern 5: Test file references
    test_refs = re.findall(r'`(tests?/[^`]+|_tests/[^`]+)`', content)
    edges["tests"].extend(test_refs)

    return edges
```

---

## Phase 3: Derivation Integration

### 3.1 Specs as Derivation Nodes

Every spec has a derivation that traces back to bootstrap:

```python
# Bootstrap specs (confidence = 1.0)
BOOTSTRAP_SPECS = {
    "principles.md": Derivation(
        agent_name="Principles",
        tier=DerivationTier.BOOTSTRAP,
        derives_from=(),
        inherited_confidence=1.0,
    ),
    "composition.md": Derivation(
        agent_name="Composition",
        tier=DerivationTier.BOOTSTRAP,
        derives_from=("Principles",),
        inherited_confidence=1.0,
    ),
}

# Derived specs inherit confidence
DERIVED_SPECS = {
    "flux.md": Derivation(
        agent_name="Flux",
        tier=DerivationTier.FUNCTOR,
        derives_from=("Composition", "Fix"),
        inherited_confidence=0.95,  # Product of parents
        principle_draws=(
            PrincipleDraw("Composable", 0.95, CATEGORICAL),
            PrincipleDraw("Heterarchical", 0.85, EMPIRICAL),
        ),
    ),
}
```

### 3.2 Spec Confidence from Implementation

Implementation success updates spec confidence:

```python
async def update_spec_confidence_from_impl(spec: SpecNode) -> float:
    """
    Implementation evidence → spec confidence.

    - Tests passing → empirical evidence
    - Usage patterns → stigmergic evidence
    - Code quality → aesthetic evidence
    """

    # Find implementation files
    impl_paths = await resolve_hyperedge(spec.path, "implements")

    evidence = EvidenceCollector()

    for impl in impl_paths:
        # Test coverage
        tests = await find_tests_for(impl)
        test_results = await run_tests(tests)
        if test_results.all_passed:
            evidence.add(Evidence(
                claim=f"{spec.title} implementation passes tests",
                source="test_results",
                strength=EvidenceStrength.STRONG,
            ))

        # Type check
        if await mypy_passes(impl):
            evidence.add(Evidence(
                claim=f"{spec.title} implementation is type-correct",
                source="mypy",
                strength=EvidenceStrength.MODERATE,
            ))

    return evidence.compute_confidence()
```

---

## Phase 4: Portal Tokens for Spec Navigation

### 4.1 Spec Portals

When reading a spec, references become expandable portals:

```markdown
# Composition Protocol

This extends the categorical foundations from `spec/agents/primitives.md`.

▶ [extends] ──→ spec/agents/primitives.md

The composition laws derive from:

▼ [heritage] ──→ Category Theory
┌────────────────────────────────────────────────────────────────────
│ **Heritage Citation (SPEAR):** The SPEAR paper (arXiv:2508.05012)
│ formalizes prompt algebra with composition, union, tensor...
│
│ ▶ [source] ──→ arXiv:2508.05012
└────────────────────────────────────────────────────────────────────
```

### 4.2 Bidirectional Navigation

Portals work both directions:

```
┌─────────────────────────────────────────────────────────────────────┐
│  spec/agents/composition.md                                          │
│                                                                      │
│  ▼ [implements] ──→ impl/claude/agents/poly/                         │
│  ┌──────────────────────────────────────────────────────────────────┐│
│  │  ▶ [tests] ──→ impl/claude/agents/poly/_tests/                   ││
│  │  ▶ [depends_on] ──→ spec/agents/primitives.md                    ││
│  │  ▶ [extended_by] ──→ spec/agents/flux.md                         ││
│  └──────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 5: Interactive Text for Specs

### 5.1 Six Token Types Applied to Specs

| Token Type | Spec Example | Affordance |
|------------|--------------|------------|
| **AGENTESEPath** | `` `self.memory.crystallize` `` | Click → invoke in REPL |
| **TaskCheckbox** | `- [x] Implement composition laws` | Toggle → witness mark |
| **Image** | `![diagram](poly-diagram.png)` | Hover → AI description |
| **CodeBlock** | ` ```python ... ``` ` | Run → execute in sandbox |
| **PrincipleRef** | `(AD-002)` | Hover → show full principle |
| **RequirementRef** | `_Requirements: 7.1, 7.4_` | Click → show trace |

### 5.2 Spec as Working Document

The spec becomes a REPL for developing its own implementation:

```markdown
# D-gent Specification

## State Machine

The D-gent has five positions:

```python
positions = frozenset(["IDLE", "LOADING", "STORING", "QUERYING", "FORGETTING"])
```

[▶ Run] [📋 Copy]

## Verification

Test the identity law:

```python
# This code block is executable!
from protocols.exploration import create_harness

harness = create_harness(start_node=ContextNode("spec/agents/d-gent.md"))
result = await harness.navigate("implements")
print(f"Found {len(result.graph.focus)} implementation files")
```

[▶ Run] → Output appears inline
```

---

## Phase 6: The Self-Hosting Loop

### 6.1 Claude Working FROM INSIDE kgents

Instead of:
```
Human: "Implement the D-gent spec"
Claude: *reads spec* → *writes code* → *runs tests*
```

We get:
```
Claude (inside kgents):
  1. Navigate to spec/agents/d-gent.md via portal
  2. Expand [implements] portal to see current state
  3. Expand [tests] portal to see coverage
  4. Use kg explore to navigate context
  5. Make decisions → kg decide witnesses them
  6. Update spec via interactive edit
  7. Derivation confidence updates automatically
```

### 6.2 The Bootstrap Commands

```bash
# Initialize spec graph
kg specgraph init
# → Parses all specs in spec/
# → Builds hyperedge relationships
# → Registers as concept.specgraph.* nodes

# Navigate specs via AGENTESE
kg invoke concept.specgraph.manifest spec/agents/composition.md
# → Shows: derivation, edges, confidence, implementation status

# Explore spec dependencies
kg explore start spec/agents/flux.md
kg explore navigate extends
kg explore navigate implements
kg explore trail  # Shows navigation history

# Portal expansion from CLI
kg portal spec/agents/flux.md implements
# → Shows implementation files with test status

# Interactive spec editing
kg document edit spec/agents/d-gent.md
# → Opens in interactive mode with portal tokens
```

### 6.3 Self-Improvement Loop

```
┌─────────────────────────────────────────────────────────────────────┐
│                     KGENTS SELF-HOSTING LOOP                         │
│                                                                      │
│  1. SPEC                    2. IMPLEMENT                             │
│     concept.specgraph          impl/claude/...                       │
│     (defines what)             (builds how)                          │
│           │                          │                               │
│           ▼                          ▼                               │
│  ┌─────────────────┐        ┌─────────────────┐                     │
│  │   Derivation    │◄──────►│   Tests/ASHC    │                     │
│  │   Framework     │        │   Evidence      │                     │
│  └────────┬────────┘        └────────┬────────┘                     │
│           │                          │                               │
│           ▼                          ▼                               │
│  3. CONFIDENCE              4. WITNESS                               │
│     spec confidence             decisions marked                     │
│     updates                     wisdom captured                      │
│           │                          │                               │
│           ▼                          ▼                               │
│  5. SPEC EVOLUTION                                                   │
│     specs update from impl wisdom                                    │
│     the loop repeats                                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 7: Implementation Roadmap

### Session 1: SpecGraph Core (~4 hrs)

**Deliverables:**
- `protocols/specgraph/types.py` — SpecNode, SpecEdge types
- `protocols/specgraph/parser.py` — Parse specs, discover edges
- `protocols/specgraph/registry.py` — Registry of all specs
- AGENTESE paths: `concept.specgraph.*`

**Verification:**
```bash
kg invoke concept.specgraph.manifest spec/agents/composition.md
# → Shows parsed spec with edges
```

### Session 2: Derivation Bridge (~3 hrs)

**Deliverables:**
- `protocols/derivation/spec_bridge.py` — Specs as derivation nodes
- Confidence computation from implementation status
- Wire to existing derivation registry

**Verification:**
```bash
kg derivation show spec/agents/flux.md
# → Shows: tier, confidence, principle draws, ancestors
```

### Session 3: Portal Integration (~3 hrs)

**Deliverables:**
- Extend portal tokens to work with spec files
- CLI: `kg portal spec/agents/flux.md implements`
- Bidirectional edge resolution

**Verification:**
```bash
kg portal spec/agents/flux.md
# → Shows: ▶ [extends], ▶ [implements], ▶ [tests]
```

### Session 4: Interactive Spec Editing (~4 hrs)

**Deliverables:**
- `services/interactive-text/` Crown Jewel
- Token parser for six types
- CLI rendering with Rich
- Basic edit loop

**Verification:**
```bash
kg document edit spec/agents/d-gent.md
# → Opens interactive mode
# → Can expand portals, run code blocks
```

### Session 5: Self-Hosting Loop (~4 hrs)

**Deliverables:**
- Wire Claude Code to use kgents for kgents development
- Claude.md skill for "work on specs from inside"
- End-to-end flow: navigate → decide → mark → update

**Verification:**
```
Claude: I'm now working on kgents using kgents.
        *uses kg explore, kg portal, kg decide*
        *updates spec based on implementation*
```

---

## The Recursive Bootstrap Problem

### The Chicken-Egg

We want to use the framework to build the framework. But the framework doesn't exist yet.

### The Solution: Gradual Bootstrap

1. **Phase A**: Implement minimal SpecGraph using current tools (pytest, Claude direct)
2. **Phase B**: Once SpecGraph exists, port itself into SpecGraph
3. **Phase C**: Use SpecGraph to build Portal integration
4. **Phase D**: Port Portal integration into SpecGraph+Portal
5. **Phase E**: Each new feature self-hosts on completion

**The Key Insight**: Each component becomes self-hosting the moment it's complete:

```
Day 1: Build SpecGraph manually
Day 2: SpecGraph now exists; use it to understand its own structure
Day 3: Build Portal on SpecGraph; understand SpecGraph via Portal
Day 4: Build Interactive Text on Portal; edit SpecGraph interactively
Day 5: The system now develops itself
```

---

## Anti-Patterns to Avoid

### ❌ Over-Engineering the Bootstrap

We don't need full SpecGraph to start. Start with:
- Parse one spec
- Find its edges
- Display as portal tokens

### ❌ Waiting for Perfection

The first version will be rough. That's fine. The point is to have SOMETHING that enables self-hosting, then improve it.

### ❌ Ignoring the Derivation

Every decision should create a mark. Even in the bootstrap phase, we should be witnessing our decisions.

### ❌ Making It Too Abstract

The goal is practical: Claude working on kgents from inside kgents. Every feature should serve that goal.

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Self-Hosting Ratio** | >50% of dev done via kgents | Witness marks in Claude sessions |
| **Spec Coverage** | All 60 specs in SpecGraph | `kg specgraph status` |
| **Portal Navigation** | <2 clicks to any related file | User testing |
| **Derivation Tracing** | Every spec has confidence | `kg derivation list --tier all` |
| **Interactive Edit** | Can edit spec without leaving kgents | End-to-end demo |

---

## Philosophical Reflection

> *"The proof IS the decision. The mark IS the witness."*

This bootstrap is not just a technical project. It's a demonstration that:

1. **Specs can be generative** — Implementation follows from spec navigation
2. **Evidence accumulates** — Every implementation strengthens spec confidence
3. **The system evolves** — Wisdom flows back into specs
4. **Self-hosting is possible** — We can work ON the system FROM INSIDE the system

The ultimate test: Can a Claude session that starts with `kg` commands produce a feature that improves `kg`?

If yes, we've achieved true self-hosting.

---

*"The spec is not description—it is generative. The text is not passive—it is interface."*

*And now we prove it by building the proof inside itself.*

---

**Next Action**: Start Session 1 — SpecGraph Core
