# spec/meta.md — Navigating the Derivation DAG

> *"The spec that can't be navigated from inside itself is mere documentation."*

**What you're holding**: The navigation hub for the kgents specification—a self-hosting, derivation-based architecture where specs generate implementations, not the other way around.

---

## What Is This Spec?

The kgents specification is a **derivation DAG**, not a documentation hierarchy. Nodes are specs. Edges are derivation relationships. Confidence propagates from bootstrap principles (immutable, confidence = 1.0) through compositional layers to implementation.

```
CONSTITUTION (1.0)
     │
     ├─→ COMPOSITION ──→ OPERADS ──→ FLUX
     ├─→ PRIMITIVES  ──→ FUNCTORS ──┘
     └─→ AGENTESE ────→ TYPED-HYPERGRAPH ──→ SELF-HOSTING
```

**The Generative Test**: Could you delete `impl/` and regenerate it from `spec/`? If the regenerated code is isomorphic to the original, the spec is generative. If not, it's just documentation.

---

## The Architecture: Bootstrap → Derive → Verify

### Layer 0: The Immutable Foundation

**Location**: `spec/principles/CONSTITUTION.md`

The seven principles that define what agents ARE:

1. **Tasteful** — Each agent serves a clear, justified purpose
2. **Curated** — Intentional selection over exhaustive cataloging
3. **Ethical** — Agents augment human capability, never replace judgment
4. **Joy-Inducing** — Delight in interaction; personality matters
5. **Composable** — Agents are morphisms in a category
6. **Heterarchical** — Agents exist in flux, not fixed hierarchy
7. **Generative** — Spec is compression; design generates implementation

**Plus**: Seven constitutional articles governing how agents relate (Symmetric Agency, Adversarial Cooperation, Supersession Rights, The Disgust Veto, Trust Accumulation, Fusion as Goal, Amendment).

### Layer 1: Meta-Principles (Operate ON the Seven)

**Location**: `spec/principles/meta.md`

- **The Accursed Share** — Everything is slop or comes from slop. Gratitude for the compost heap.
- **AGENTESE: No View From Nowhere** — Observation is interaction. The protocol IS the API.
- **Personality Space** — LLMs swim in personality-emotion manifolds. K-gent navigates, doesn't inject.

### Layer 2: Operational Principles

**Location**: `spec/principles/operational.md`

- **Transparent Infrastructure** — Infrastructure communicates what it's doing
- **Graceful Degradation** — When dependencies fail, degrade; never break entirely
- **Spec-Driven Infrastructure** — YAML is generated, not written
- **Event-Driven Streaming** — Flux > Loop; streams react to events, not timers

### Layer 3: Architectural Decisions (The Binding Rulings)

**Location**: `spec/principles/decisions/INDEX.md`

16 architectural decisions (AD-001 through AD-016) that shape implementation. Key examples:

| AD | Title | Core Insight |
|----|-------|--------------|
| AD-002 | Polynomial Generalization | PolyAgent[S,A,B] for state-dependent behavior |
| AD-003 | Generative Over Enumerative | Define grammars, not instances |
| AD-006 | Unified Categorical Foundation | PolyAgent + Operad + Sheaf everywhere |
| AD-009 | Metaphysical Fullstack Agent | Vertical slices from persistence to projection |
| AD-012 | Aspect Projection Protocol | Paths are PLACES, aspects are ACTIONS |

---

## Navigation: Where to Find What

### "I want to understand the core philosophy"

→ `spec/principles/CONSTITUTION.md` (the seven + seven)
→ `spec/principles/meta.md` (meta-principles)
→ `spec/principles.md` (detailed principle definitions with heritage citations)

### "I need to know the operational rules"

→ `spec/principles/operational.md` (infrastructure, degradation, streaming)

### "I'm making an architectural decision"

→ `spec/principles/decisions/INDEX.md` (see what's already decided)

### "I want to see what we've learned"

→ `plans/meta.md` (distilled learnings, anti-patterns, gotchas)

### "I need to know what's happening NOW"

→ `NOW.md` (the one living document)

### "I want to build something"

→ `docs/skills/` (30+ skills that are necessary and sufficient)
→ `docs/skills/metaphysical-fullstack.md` (start here)

### "I need to understand a specific agent genus"

→ `spec/agents/<letter>-gent.md` (e.g., `k-gent.md`, `d-gent.md`)

### "I want to understand AGENTESE"

→ `spec/protocols/agentese.md` (the verb-first ontology)
→ `docs/skills/agentese-path.md` (how paths work)
→ `docs/skills/agentese-node-registration.md` (how to expose agents)

---

## The Category-Theoretic Framing

The spec/ directory is a **sheaf**:

```
SpecSheaf: Cover × LocalView → GlobalSpec

where:
  Cover = {principles/, agents/, protocols/, heritage/}
  LocalView = individual .md files
  Gluing = derivation edges (extends, implements, tests)
  GlobalSpec = the coherent whole
```

**Sheaf Laws**:
1. **Identity**: A spec extended by nothing is itself
2. **Associativity**: (A extends B) extends C ≡ A extends (B extends C)
3. **Compatibility**: Overlapping specs must agree on shared concepts
4. **Gluing**: Compatible local specs uniquely determine the global spec

---

## Confidence Propagation

Every spec node has **derivation confidence**:

```
confidence(spec) = min(ancestors) × evidence_factor

where:
  evidence_factor = (passing_tests / total_tests) × diversity_score
```

**Bootstrap specs** (CONSTITUTION, meta-principles) have confidence = 1.0 by definition.
**Derived specs** inherit confidence modulated by empirical evidence.
**Stale specs** decay over time if not refreshed.

---

## The Self-Referential Test

**Does this meta-spec pass the Generative Principle?**

1. ✅ **Compression**: ~150 lines compress navigation for 193 spec files
2. ✅ **Regenerability**: Could reconstruct spec/ structure from this file
3. ✅ **Derivation clarity**: The DAG structure is explicit

**Verdict**: This meta-spec is **axiomatic** (Layer 0), not derived. It ENABLES regeneration of other specs but is itself part of the immutable foundation.

---

## Voice Preservation: The Anti-Sausage Check

Before modifying specs, ask:

- ❓ *Did I smooth anything that should stay rough?*
- ❓ *Did I add words Kent wouldn't use?*
- ❓ *Did I lose any opinionated stances?*
- ❓ *Is this still daring, bold, creative—or did I make it safe?*

**Voice Anchors** (quote directly, don't paraphrase):

| Anchor | Use When |
|--------|----------|
| *"Daring, bold, creative, opinionated but not gaudy"* | Making aesthetic decisions |
| *"The Mirror Test"* | Evaluating if something feels right |
| *"Tasteful > feature-complete"* | Scoping work |
| *"The persona is a garden, not a museum"* | Discussing evolution vs. preservation |

---

## The Zen Koan

> *"The spec that documents what exists is a mirror.*
> *The spec that generates what could be is a seed.*
> *The spec that verifies itself is a garden."*

This is the garden.

---

**Filed**: 2025-12-23 | **Status**: Bootstrap
