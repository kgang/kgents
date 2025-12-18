---
path: plans/autopoietic-architecture
status: active
progress: 35
last_touched: 2025-12-17
touched_by: claude-opus-4-5
blocking: []
enables: [all-crown-jewels, metaphysical-fullstack]
session_notes: |
  Consolidated from autopoietic-consolidation.md + autopoietic-consolidation-review.md.
  Key insight: Compiler-first, not deletion-first. Safe annihilation requires regenerability.
  2025-12-17 Session:
  - Phase 0 complete: SpecGraph schema defined, Compile/Reflect interfaces created
  - self.system.* node implemented (manifest, audit, compile, reflect, evolve, witness)
  - Comprehensive audits completed: Operad (3 rogue), AGENTESE nodes (10 registered), Spec structure (0% YAML)
  - Autopoiesis score estimated: ~0.3 (per PolyAgent audit)
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: partial
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.05
  returned: 0.0
---

# Autopoietic Architecture: The Metaphysical Agent Stack

> *"The system that can regenerate itself can safely annihilate itself."*
> *"Autopoiesis is not self-description—it is self-production."*

---

## Purpose

Design and implement the **Autopoietic Kernel**—the minimal, regenerable system from which all kgents agents can be derived. This is not a deletion plan with regeneration as afterthought; it is a **compiler-first** plan where deletion becomes safe and fast.

---

## The Metaphysical Agent Stack (AD-009 Realized)

Every agent in kgents is a vertical slice through these seven layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES                                                      │
│     CLI  │  TUI  │  Web UI  │  marimo  │  JSON API  │  VR  │  SSE           │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE UNIVERSAL PROTOCOL                                              │
│     logos.invoke(path, observer, **kwargs) — all transports collapse here    │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE (@node decorator)                                          │
│     Semantic interface: aspects, effects, affordances, observer-dependence   │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE (Crown Jewels)                                            │
│     services/<name>/ — Business logic + Adapters + D-gent integration        │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD GRAMMAR                                                           │
│     Composition laws, operation signatures, valid compositions               │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL AGENT (State Machine)                                         │
│     PolyAgent[S, A, B]: positions, directions, transitions                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. SHEAF COHERENCE (Emergence)                                              │
│     Local views → global consistency via gluing                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**The Insight**: Understanding ONE layer teaches you ALL layers. They instantiate the same categorical pattern.

---

## The Autopoietic Kernel (SACRED)

These are the files that constitute the regenerable core. They cannot be deleted—only refined.

### Tier 1: Mathematical Ground (NEVER DELETE)

| File | Purpose | Why Sacred |
|------|---------|------------|
| `spec/principles.md` | Design philosophy + Kent's voice | Identity |
| `spec/c-gents/*.md` | Category theory specs | Mathematical ground |
| `impl/claude/agents/poly/` | PolyAgent implementation | State machines |
| `impl/claude/agents/operad/core.py` | **Canonical** Operad implementation | Composition grammar |
| `impl/claude/agents/sheaf/` | Sheaf implementation | Emergence |

### Tier 2: Protocol Ground (NEVER DELETE)

| File | Purpose | Why Sacred |
|------|---------|------------|
| `spec/protocols/agentese.md` | AGENTESE specification | Verb-first ontology |
| `impl/claude/protocols/agentese/` | AGENTESE implementation (559 tests) | Universal protocol |
| `spec/k-gent/persona.md` | K-gent personality specification | Personality space |
| `impl/claude/agents/k/` | K-gent (Soul/Governance) | Governance functor |

### Tier 3: Autopoietic Substrate (NEVER DELETE)

| File | Purpose | Why Sacred |
|------|---------|------------|
| `plans/meta.md` | Distilled learnings | Organizational memory |
| `CLAUDE.md` | Session context (regenerated) | Self-description |
| `impl/claude/protocols/prompt/` | Evergreen prompt system | Self-cultivation |

**Adding to SACRED**: Requires explicit justification in session notes + unanimous agreement that it cannot be derived from Tier 1-2.

---

## The Compiler Contract

> *"The only safe path to aggressive annihilation is to make the system regenerable."*

### The Three Functors

```
SpecCat ──Compile──▶ ImplCat ──Project──▶ PathCat
    ▲                    │                    │
    │                    ▼                    │
    └────Reflect────◀ DriftCheck ◀───────────┘
```

| Functor | Input | Output | Purpose |
|---------|-------|--------|---------|
| **Compile** | `spec/*.md` | `impl/` modules | Generate implementation from spec |
| **Project** | `impl/` modules | AGENTESE paths | Make service available to all projections |
| **Reflect** | `impl/` modules | `spec/*.md` | Extract spec from implementation |

**Autopoiesis Fixed Point**: A system is autopoietic when `Reflect(Compile(S)) ≅ S`.

### The SpecGraph Schema

Every spec file must conform to this schema to be compilable:

```yaml
# spec/<domain>/<name>.md
---
domain: <context>
holon: <name>
polynomial: <optional block>
operad: <optional block>
sheaf: <optional block>
agentese: <optional block>
---
```

### Concrete Binding Example (Minimal)

```yaml
---
domain: world
holon: town
polynomial: {positions: [idle], transition: town_transition}
operad: {operations: {greet: {arity: 1}}}
agentese: {path: world.town, aspects: [manifest]}
---
```

**Binding Rule (Flexible)**: References may be names, doc anchors, or module paths. Resolve late during compile.
**Flex Note**: Any block may be partial while the architecture is being redesigned.

### Drift Detection (CI Gate)

```python
# CI: compare spec vs impl and return a status
check_drift() -> status
```

**Reflect Output Format** (required for drift checks):

```yaml
reflected:
  spec_hash: <hash?>
  impl_hash: <hash?>
  summary: <optional>
```

**Drift Severity**: Compare hashes when available and fall back to structured diffs when specs are incomplete.

**Enforcement (Solo Gate)**: DIVERGED blocks activation unless a redesign waiver is recorded in `plans/_status.md` and echoed by `self.system.witness`.

### Compile + Reflect Stubs (Concise)

```python
def compile_spec(spec_path: str):
    """Spec -> Impl (may be partial during redesign)."""
    ...


def reflect_impl(impl_paths: list[str]):
    """Impl -> Spec (best-effort during redesign)."""
    ...
```

---

## Categorical Culling Rules

> *"Replace LoC and coverage thresholds with categorical invariants."*

### Delete If (Categorical Failure)

| Criterion | Check | Action |
|-----------|-------|--------|
| **Functor law violation** | `FunctorRegistry.verify_all()` fails | Delete impl, fix spec |
| **Operad law violation** | Operad doesn't use `operad/core.py` | Replace local operad |
| **Sheaf gluing fails** | Local views don't compose | Delete, rebuild with sheaf |
| **No AGENTESE path** | Service not discoverable | Add node or delete |
| **Spec-Impl divergence** | `DriftCheck` returns DIVERGED | Reconcile or delete both |

**Flex Note**: During redesign, prefer archiving over deletion unless a replacement is ready.

### Preserve If (Categorical Success)

| Criterion | Evidence |
|-----------|----------|
| Uses PolyAgent for state | Imports from `agents/poly/` |
| Uses canonical Operad | Subclasses or composes with `operad/core.py` |
| Has Sheaf coherence | Implements gluing for local views |
| AGENTESE discoverable | `@node` decorator registered |
| Spec matches impl | DriftCheck returns ALIGNED |

### The Categorical Test

For any system asking "should this survive?":

```python
should_survive(module) -> passes >= threshold
```

**Flex Note**: During redesign, allow survival with 3/5 checks if replacement work is in-flight.

---

## Operad Unification (Phase 1)

> *"Multiple competing operad implementations mean composition laws fragment."*

### The Problem (Audit 2025-12-17)

**11 operad implementations found, 3 are rogue (parallel class hierarchies):**

| File | Type | Status |
|------|------|--------|
| `agents/operad/core.py` | **CANONICAL** | ✅ Source of truth (576 lines) |
| `agents/operad/domains/*.py` | extends-canonical | ✅ SOUL, MEMORY, NARRATIVE, etc. |
| `agents/town/operad.py` | extends-canonical | ✅ Properly extends core |
| `agents/domain/drills/operad.py` | extends-canonical | ✅ CRISIS_OPERAD |
| `protocols/nphase/operad.py` | extends-canonical | ✅ NPHASE_OPERAD |
| `agents/f/operad.py` | **LOCAL** | ⚠️ ROGUE - defines own Operation/OpLaw/Operad |
| `agents/atelier/workshop/operad.py` | **LOCAL** | ⚠️ ROGUE - defines own classes |
| `protocols/agentese/contexts/self_grow/operad.py` | **LOCAL** | ⚠️ ROGUE - GrowthOperad |

**Current canonical usage**: 73% (8 of 11 operads properly extend core)

### The Solution

1. **Canonical operad**: All operads extend `impl/claude/agents/operad/core.py`
2. **OperadRegistry**: Enforce as single source of truth (already exists)
3. **Law verification**: `OperadRegistry.verify_all()` runs in CI

```python
# Use canonical Operad + register it
OperadRegistry.register(Operad(...))
```

### Migration Required

1. `agents/f/operad.py` → Reimplement FLOW_OPERAD extending core
2. `agents/atelier/workshop/operad.py` → Reimplement ATELIER_OPERAD extending core
3. `contexts/self_grow/operad.py` → Reimplement GROWTH_OPERAD extending core

---

## AGENTESE Path Authority (Phase 2)

> *"All AGENTESE nodes must be generated from SpecGraph, not hand-decorated."*

### The Problem (Audit 2025-12-17)

```
crown_jewels.py (PATHS dicts) ────→ Documentation only (NOT discoverable)
@node decorator ──→ NodeRegistry ──→ /discover ──→ NavigationTree
```

**Current registered paths (10 total):**
```
self.chat         # Chat service
self.memory       # Brain Crown Jewel
self.system       # Autopoietic kernel (NEW)
world.emergence   # Cymatics Design Sampler
world.gestalt.live # Real-time 3D topology
world.park.force  # Park force mechanics
world.park.mask   # Park masks
world.park.scenario # Park scenarios
world.town        # Agent Town
world.town.inhabit # Town INHABIT mode
```

**Gaps identified:**
- `world.morpheus`, `self.chat` NOT in crown_jewels.py PATHS (orphaned)
- `world.coalition`, `world.simulation` in PATHS but NOT implemented
- Gardener paths (`concept.gardener.*`, `self.forest.*`) missing from gateway

### The Solution

1. **SpecGraph is authority**: Paths defined in spec, not code
2. **JIT from spec**: `@node` decorators generated from spec parsing
3. **Self-system paths**: ✅ Implement `self.system.*` for autopoiesis

```
self.system.manifest      # ✅ What is kgents? (projection)
self.system.audit         # ✅ What needs fixing? (drift detection)
self.system.evolve        # ✅ Apply consolidation (mutation)
self.system.witness       # ✅ History of changes (N-gent trace)
self.system.compile       # ✅ Spec → Impl (generation)
self.system.reflect       # ✅ Impl → Spec (extraction)
```

**Migration Rule (Flexible)**:
- Hand-authored `@node` registrations may remain until compile stabilizes.
- Paths missing from SpecGraph are flagged, not deleted, during redesign.

---

## Session Plan (Revised: Compiler-First)

### Phase 0: Define Compiler Contract ✅ COMPLETE
- [x] Consolidate plans
- [x] Define SpecGraph schema (see above)
- [x] Define Compile/Reflect interfaces (`self_system.py`)
- [x] Implement `self.system.*` node (manifest, audit, compile, reflect, evolve, witness)
- [x] Add to SACRED list

### Phase 1: Operad Unification (Session 2)
- Replace all local operads with canonical
- Enforce OperadRegistry
- Add CI gate for operad law verification

### Phase 2: AGENTESE Path Authority (Session 3)
- Audit all @node registrations
- Cross-reference with specs
- Add missing nodes or delete orphan impls
- Implement `self.system.*` paths

### Phase 3: Reference Agent Proof (Session 4)
- Pick highest-scoring jewel (Brain or Town)
- Prove: chat + web + SaaS all work
- Document the vertical slice pattern

### Phase 4: Cascading Compile (Session 5)
- Apply pattern to next 2 jewels
- Use Compile functor to generate from spec
- Verify with DriftCheck

### Phase 5: Autopoietic Loop (Session 6)
- `self.system.audit` generates Reflect report
- Feed to `self.system.evolve` to regenerate
- Prove: system can describe and improve itself

### Phase 6: Annihilation (Session 7)
- Now safe to delete aggressively
- Apply categorical culling rules
- Archive everything that fails survival test
- Target: ≥50% impl reduction, 90% autopoiesis score

---

## Minimal Skills for Full-Resolution Agent

> *"What skills does an agent need to build any kgents component?"*

These 12 skills are necessary and sufficient for full-resolution development:

### Foundation Skills (Categorical Ground)

| Skill | File | Purpose |
|-------|------|---------|
| **polynomial-agent** | `docs/skills/polynomial-agent.md` | State machines with mode-dependent inputs |
| **building-agent** | `docs/skills/building-agent.md` | Agent[A,B] with functors |

### Protocol Skills (AGENTESE)

| Skill | File | Purpose |
|-------|------|---------|
| **agentese-path** | `docs/skills/agentese-path.md` | Adding AGENTESE paths |
| **agentese-node-registration** | `docs/skills/agentese-node-registration.md` | @node decorator, discovery |

### Architecture Skills (Vertical Slice)

| Skill | File | Purpose |
|-------|------|---------|
| **crown-jewel-patterns** | `docs/skills/crown-jewel-patterns.md` | Service module structure |
| **metaphysical-fullstack** | `docs/skills/metaphysical-fullstack.md` | AD-009 stack |
| **data-bus-integration** | `docs/skills/data-bus-integration.md` | Event-driven communication |

### Process Skills (N-Phase)

| Skill | File | Purpose |
|-------|------|---------|
| **plan-file** | `docs/skills/plan-file.md` | Forest Protocol plans |
| **spec-template** | `docs/skills/spec-template.md` | Writing specs (200-400 lines) |
| **spec-hygiene** | `docs/skills/spec-hygiene.md` | Bloat patterns, distillation |

### Projection Skills (Multi-Target)

| Skill | File | Purpose |
|-------|------|---------|
| **projection-target** | `docs/skills/projection-target.md` | CLI/TUI/JSON/marimo |
| **test-patterns** | `docs/skills/test-patterns.md` | Testing conventions |

### The Skill Composition Theorem

> Any kgents component can be built by composing these 12 skills.

```
Component = Foundation ∘ Protocol ∘ Architecture ∘ Process ∘ Projection
```

**Proof by construction**: Every Crown Jewel uses this exact composition.

---

## Sheaf Placement Clarification

Sheaf coherence is listed as Layer 1 because it is foundational, but operationally it composes *over* local agents (polynomial + operad). Treat the stack as conceptual order, not runtime call order.

---

## Success Criteria

### Quantitative (Measured 2025-12-17)

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Autopoiesis Score | ~0.3 | ≥0.9 | 🔴 |
| Operad implementations | 11 (3 rogue) | 1 canonical | 🟡 73% compliant |
| AGENTESE path coverage | 10 registered | 100% of survivors | 🟡 |
| Spec-Impl drift | 0% YAML frontmatter | ALIGNED for all | 🔴 |
| impl/ LoC | ~50K | -50% | 🔴 |
| Skills in CLAUDE.md | 12 minimal | 12 (minimal) | ✅ |

### Qualitative

- [x] `kg self.system.manifest` returns valid projection ✅ IMPLEMENTED
- [ ] New contributor finds correct system in <2 minutes
- [ ] All Crown Jewels follow AD-009 stack
- [x] System can explain itself via AGENTESE paths ✅ self.system.*
- [ ] **"I could explain the whole system in 10 minutes"**

### The Phoenix Metric

```
Autopoiesis Score = (Systems using categorical foundation) / (Total systems)

Current: ~0.3 (most systems don't use PolyAgent/Operad/Sheaf)
Target:  ≥0.9 (90% categorical foundation usage)
```

---

## Open Questions (Require Kent's Call)

1. **K-gent persona**: Part of autopoietic kernel, or generated layer?
   - *Current decision*: SACRED (Tier 2) — personality is meta-principle

2. **AGENTESE path authority**: Spec or code decorators?
   - *Current decision*: Spec is authority, decorators are generated

3. **Compiler preservation**: Can compiler discard hand-tuned implementations?
   - *Current decision*: Yes, if spec can regenerate equivalent

---

## The Autopoietic Creed

> *"The sculptor does not add clay; the sculptor removes what is not the statue."*
>
> *"The foundation remains. Everything else is kindling for the phoenix."*
>
> *"If you can regenerate it from spec, delete it now."*
>
> *"The form that generates forms is itself a form."*

**Autopoiesis = Compile(spec) ≅ impl ≅ Reflect(impl)**

**What survives compilation IS the system.**

---

*Consolidated: 2025-12-17 | From: autopoietic-consolidation.md + autopoietic-consolidation-review.md*
*Updated: 2025-12-17 | Phase 0 complete, audits integrated, self.system.* implemented*
