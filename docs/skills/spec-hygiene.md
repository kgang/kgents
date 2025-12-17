# Skill: Spec Hygiene

> *"Spec is compression. If you can't compress it, you don't understand it."*

## Overview

This document codifies learnings from the 8-phase spec distillation exercise (December 2025), which reduced the spec corpus from ~91,000 to ~78,000 lines while increasing clarity and generativity.

**Related**: `docs/skills/spec-template.md` (structure), `spec/principles.md` (philosophy)

---

## The Seven Bloat Patterns

These patterns were identified and removed during distillation. Watch for them in new specs.

### 1. Implementation Creep (Most Common)

**Symptom**: Full function bodies in spec files (>10 lines of code)

**Example (Bad)**:
```python
# This was in spec/protocols/self-grow.md
async def recognize_gaps(self, context: GrowthContext) -> list[GapSignal]:
    existing = await self._load_current_holons()
    requested = self._extract_requested_from_context(context)
    gaps = []
    for req in requested:
        if not self._find_matching_holon(req, existing):
            signal = GapSignal(
                pattern=req.pattern,
                frequency=req.mention_count,
                source_contexts=[context.id],
                confidence=self._estimate_confidence(req)
            )
            gaps.append(signal)
    return sorted(gaps, key=lambda g: g.confidence, reverse=True)
```

**Fixed (Good)**:
```python
async def recognize_gaps(context: GrowthContext) -> list[GapSignal]:
    """Identify ontological gaps from usage patterns."""
    ...  # See impl/claude/protocols/agentese/contexts/self_grow/
```

**Metric**: self-grow.md was 80% implementation code (2,037 → 442 lines)

---

### 2. Roadmap Drift

**Symptom**: Week-by-week plans, implementation timelines, checkbox lists

**Example (Bad)**:
```markdown
## Implementation Roadmap

### Week 1-2: Core Types
- [ ] Define Parser protocol
- [ ] Implement StackBalancingParser
- [ ] Add tests

### Week 3-4: Advanced Strategies
- [ ] ProbabilisticASTParser
- [ ] EvolvingParser
...
```

**Fixed**: Move to `plans/` directory. Specs are timeless; plans are temporal.

**Metric**: p-gents/README.md had 200+ lines of roadmap

---

### 3. Framework Comparison Tables

**Symptom**: Decision matrices comparing kgents to other frameworks

**Example (Bad)**:
```markdown
| Feature | kgents | LangChain | AutoGPT |
|---------|--------|-----------|---------|
| Tool composition | Functorial | Imperative | ... |
| Memory model | Sheaf | Vector DB | ... |
...
```

**Fixed**: Move to `docs/` if valuable, otherwise delete. Spec defines WHAT, not WHY NOT OTHERS.

---

### 4. Gap Analyses

**Symptom**: "Current State vs Desired State" sections

**Example (Bad)**:
```markdown
## Gap Analysis

### Current Implementation
- Only supports 3 of 14 functors
- No streaming support
- Memory limited to 10MB

### Desired State
- All 14 functors implemented
- Full streaming support
...
```

**Fixed**: Delete. These are temporal snapshots, not specifications. The spec defines the target; implementation tracks progress.

---

### 5. AI Session Artifacts

**Symptom**: Continuation prompts, agent instructions, session notes in specs

**Example (Bad)**:
```markdown
## Continuation Prompt

When resuming this session:
1. Read the context above
2. Check git status
3. Continue from Phase 3
...
```

**Fixed**: Move to `plans/_continuations/`. Specs are not session logs.

---

### 6. File Listings

**Symptom**: "Files to Create" sections with directory trees

**Example (Bad)**:
```markdown
## Files to Create

impl/claude/agents/p/
├── types.py              # All type definitions
├── stack_balancing.py    # StackBalancingParser implementation
├── anchor_based.py       # AnchorBasedParser implementation
├── probabilistic_ast.py  # ProbabilisticASTParser implementation
├── evolving.py           # EvolvingParser implementation
├── composition.py        # FallbackParser, FusionParser
└── graduated.py          # GraduatedPromptParser
```

**Fixed**: A single line suffices:
```markdown
**Implementation**: `impl/claude/agents/p/` (12 tests)
```

---

### 7. Test Code as Laws

**Symptom**: Full pytest functions in "Laws" section

**Example (Bad)**:
```python
## Laws

def test_functor_identity_law():
    agent = create_agent()
    assert agent.map(lambda x: x) == agent

def test_functor_composition_law():
    agent = create_agent()
    f = lambda x: x + 1
    g = lambda x: x * 2
    assert agent.map(f).map(g) == agent.map(lambda x: g(f(x)))
```

**Fixed**: Laws as equations:
```markdown
## Laws

1. **Identity**: `F.map(id) = id`
2. **Composition**: `F.map(g . f) = F.map(g) . F.map(f)`
```

---

## The Five Compression Patterns

These patterns emerged as effective ways to compress specs while maintaining generativity.

### 1. Type Signatures with Ellipsis

Show the shape, hide the body:

```python
@dataclass
class MemoryCrystal(Generic[T]):
    """Immutable, content-addressed memory artifact."""
    content: T
    hash: str
    created_at: datetime
    lineage: list[str]

    async def recall(self, query: Query) -> Stream[T]:
        ...  # Holographic retrieval

    async def consolidate(self, other: "MemoryCrystal[T]") -> "MemoryCrystal[T]":
        ...  # Merge with lineage tracking
```

### 2. Laws as Algebraic Equations

Declarative, not procedural:

```markdown
## Laws

| Law | Statement |
|-----|-----------|
| Associativity | `(f >> g) >> h = f >> (g >> h)` |
| Identity | `id >> f = f = f >> id` |
| Naturality | `P(f . g) = P(f) . P(g)` for functor P |
| Rashomon | `witness(e, O1) ≠ witness(e, O2)` for distinct observers |
```

### 3. AGENTESE Path Chains

Composition in one line:

```markdown
## Integration

- **Recall**: `self.memory.crystallize` → `concept.association.emerge`
- **Store**: `world.event.manifest` → `self.memory.absorb` → `void.gratitude.tithe`
- **Narrate**: `self.memory.witness` → `concept.narrative.collapse` → `world.story.tell`
```

### 4. ASCII Architecture Diagrams

Worth 100 lines of prose:

```
┌─────────────────────────────────────────────────────┐
│                    PROJECTION                        │
│  State ──→ Widget ──→ Layout ──→ Target             │
│    │         │          │          │                 │
│  [data]   [atomic]   [spatial]  [render]            │
│            Signal     VBox       CLI/JSON/VR         │
└─────────────────────────────────────────────────────┘
```

### 5. Summary Tables

Compress enumeration into scannable form:

```markdown
## Functor Summary

| Functor | Polynomial | Core Insight |
|---------|------------|--------------|
| Promise | `y^A` | Deferred computation |
| Metered | `1 + y` | Resource-gated execution |
| Spy | `y × Log` | Observation without interference |
| Lens | `y^(S×A)` | Bidirectional state access |
```

---

## Distillation Checklist

When reviewing or distilling a spec:

```markdown
- [ ] **No function bodies >10 lines** (extract to impl/)
- [ ] **No roadmaps or timelines** (move to plans/)
- [ ] **No framework comparisons** (move to docs/ or delete)
- [ ] **No gap analyses** (delete - temporal, not conceptual)
- [ ] **No session artifacts** (move to plans/_continuations/)
- [ ] **No file listings** (one-line impl reference)
- [ ] **Laws are equations, not test code**
- [ ] **Type signatures use `...` for bodies**
- [ ] **AGENTESE paths are chains, not paragraphs**
- [ ] **Diagrams replace prose where possible**
- [ ] **Spec < Impl** (compression achieved)
- [ ] **Spec is generative** (can regenerate impl from spec)
```

---

## Metrics from Distillation Exercise

### Phase Results

| Phase | Target | Before | After | Reduction |
|-------|--------|--------|-------|-----------|
| 1 | Deprecated files | ~5,700 | 0 | 100% |
| 2 | self-grow.md | 2,037 | 442 | 78% |
| 3 | p-gents/README.md | 1,568 | 427 | 73% |
| 4 | u-gents/tool-use.md | 1,381 | 518 | 62% |
| 5 | b-gents/banker.md | 1,394 | 275 | 80% |
| 6 | AGENTESE consolidation | 2,253 | 1,051 | 53% |
| 7 | Template creation | - | 133 | (new) |
| 8 | 6 HIGH/MEDIUM specs | 5,952 | 2,917 | 51% |

### Overall

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total spec lines | ~91,000 | ~78,000 | -14% |
| Specs >1,000 lines | 15+ | 4 | -73% |
| Impl code in specs | ~25,000 | ~5,000 | -80% |

---

## The Generative Test

A spec passes the generative test if:

1. **Compression**: `lines(spec) < lines(impl)`
2. **Regeneration**: An implementer can build the system from the spec alone
3. **Laws Hold**: All stated invariants are mechanically verifiable
4. **No Orphans**: Every type in spec has corresponding impl/

```python
def is_generative(spec: Path, impl: Path) -> bool:
    """The ultimate spec quality check."""
    spec_lines = count_lines(spec)
    impl_lines = count_lines(impl)

    # Compression achieved
    if spec_lines >= impl_lines:
        return False

    # All types have implementations
    spec_types = extract_types(spec)
    impl_types = extract_types(impl)
    if not spec_types.issubset(impl_types):
        return False

    # Laws are testable
    laws = extract_laws(spec)
    for law in laws:
        if not is_verifiable(law):
            return False

    return True
```

---

## Anti-Patterns Summary

| Anti-Pattern | Signal | Fix |
|--------------|--------|-----|
| Implementation Creep | Functions >10 lines | Extract to impl/ |
| Roadmap Drift | Week-by-week plans | Move to plans/ |
| Framework Comparison | Decision matrices | Move to docs/ |
| Gap Analysis | Current vs Desired | Delete |
| Session Artifacts | Continuation prompts | Move to plans/_continuations/ |
| File Listings | Directory trees | One-line reference |
| Test Code as Laws | pytest functions | Algebraic equations |

---

## Cross-References

- `docs/skills/spec-template.md` - Structure for new specs
- `spec/principles.md` - §7 Generative Principle
- `plans/meta/spec-distillation.md` - Full distillation history
- `docs/impl-guide.md` - Where implementations go

---

*"The event is the stone. The story is the shadow. The spec is the light that casts them both."*
