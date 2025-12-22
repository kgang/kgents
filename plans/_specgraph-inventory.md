# SpecGraph Inventory: Mapping Specs to the Framework

> *"Every spec is a node. Every reference is an edge. The graph IS the system."*

**Date**: 2025-12-22
**Purpose**: Detailed inventory of specs for SpecGraph bootstrap

---

## The Core 10: Bootstrap First

These specs define the framework we're building. They must be self-describing first.

### 1. `spec/principles.md` — The Constitution

```yaml
agentese_path: concept.principles
tier: BOOTSTRAP
confidence: 1.0  # Axiomatic
lines: ~1700

edges:
  extends: []  # Root node
  implements:
    - impl/claude/protocols/derivation/core.py  # PrincipleDraw type
    - The Constitution in CLAUDE.md
  tests:
    - All tests that verify principle adherence
  extended_by:
    - spec/agents/composition.md
    - spec/agents/primitives.md
    - Every other spec

principle_draws:
  - Tasteful: 1.0 (CATEGORICAL)  # Self-referential
  - Curated: 1.0 (CATEGORICAL)
  - Ethical: 1.0 (CATEGORICAL)
  - Joy-Inducing: 1.0 (CATEGORICAL)
  - Composable: 1.0 (CATEGORICAL)
  - Heterarchical: 1.0 (CATEGORICAL)
  - Generative: 1.0 (CATEGORICAL)

key_tokens:
  - "(AD-001)" → AD decision reference
  - "(AD-002)" → AD decision reference
  - "(Tasteful)" → principle reference
  - "`Agent[A, B]`" → type reference
```

### 2. `spec/protocols/derivation-framework.md` — Bayesian Proofs

```yaml
agentese_path: concept.derivation
tier: PROTOCOL
confidence: 0.95  # Heavily tested, 306 tests
lines: ~2000

edges:
  extends:
    - spec/principles.md  # Uses all 7 principles
    - spec/protocols/exploration-harness.md  # Trail evidence
    - spec/protocols/portal-token.md  # Trust integration
  implements:
    - impl/claude/protocols/derivation/core.py
    - impl/claude/protocols/derivation/ashc_bridge.py
    - impl/claude/protocols/derivation/witness_bridge.py
    - impl/claude/protocols/derivation/decay.py
  tests:
    - impl/claude/protocols/derivation/_tests/  # 306 tests
  extended_by:
    - Services that use derivation for trust

principle_draws:
  - Composable: 0.95 (CATEGORICAL)  # DAG composition
  - Generative: 0.90 (EMPIRICAL)  # Can regenerate
  - Ethical: 0.85 (EMPIRICAL)  # Disgust veto preserved

key_tokens:
  - "`DerivationTier`" → enum reference
  - "`PrincipleDraw`" → type reference
  - "Bootstrap agents" → bootstrap spec reference
```

### 3. `spec/protocols/exploration-harness.md` — Trail as Evidence

```yaml
agentese_path: self.explore
tier: PROTOCOL
confidence: 0.90  # 110 tests
lines: ~800

edges:
  extends:
    - spec/protocols/typed-hypergraph.md  # Navigation model
    - spec/protocols/portal-token.md  # UX layer
  implements:
    - impl/claude/protocols/exploration/harness.py
    - impl/claude/protocols/exploration/budget.py
    - impl/claude/protocols/exploration/loops.py
    - impl/claude/protocols/exploration/evidence.py
    - impl/claude/protocols/exploration/commitment.py
  tests:
    - impl/claude/protocols/exploration/_tests/  # 110 tests
  extended_by:
    - Portal Token (uses harness for safety)
    - Derivation (consumes trail evidence)

principle_draws:
  - Composable: 0.90 (EMPIRICAL)  # Harness composes
  - Ethical: 0.85 (EMPIRICAL)  # Evidence accumulation honest
  - Generative: 0.75 (EMPIRICAL)  # Trail generates evidence

key_tokens:
  - "`NavigationBudget`" → type reference
  - "`Trail`" → type reference
  - "`ASHCCommitment`" → type reference
```

### 4. `spec/protocols/portal-token.md` — Inline Expansion

```yaml
agentese_path: self.portal
tier: PROTOCOL
confidence: 0.85  # 125 tests (Phases 1-4)
lines: ~600

edges:
  extends:
    - spec/protocols/typed-hypergraph.md  # Conceptual model
    - spec/protocols/exploration-harness.md  # Safety layer
  implements:
    - impl/claude/protocols/file_operad/portal.py
    - impl/claude/protocols/file_operad/source_portals.py
    - impl/claude/web/src/components/portal/
  tests:
    - impl/claude/protocols/file_operad/_tests/test_portal.py
    - impl/claude/protocols/file_operad/_tests/test_source_portals.py
  extended_by:
    - Interactive Text (uses portals)
    - SpecGraph (spec navigation via portals)

principle_draws:
  - Joy-Inducing: 0.90 (AESTHETIC)  # Great UX
  - Composable: 0.85 (EMPIRICAL)  # Portals compose
  - Generative: 0.70 (EMPIRICAL)  # Portal tree from edges

key_tokens:
  - "`PortalExpansionToken`" → type reference
  - "`PortalTree`" → type reference
  - "▶ [tests] ──→" → portal rendering
```

### 5. `spec/protocols/interactive-text.md` — Specs as Interfaces

```yaml
agentese_path: self.document
tier: PROTOCOL
confidence: 0.60  # Planned, not yet implemented
lines: ~700

edges:
  extends:
    - spec/protocols/portal-token.md  # Portal tokens are subset
    - spec/protocols/projection.md  # Projection functor
    - spec/principles.md  # AD-009 Metaphysical Fullstack
  implements:
    - services/interactive-text/ (PLANNED)
  tests:
    - (PLANNED)
  extended_by:
    - SpecGraph (specs are interactive docs)

principle_draws:
  - Joy-Inducing: 0.95 (AESTHETIC)  # Vision is delightful
  - Generative: 0.90 (CONCEPTUAL)  # Spec IS interface
  - Composable: 0.85 (CONCEPTUAL)  # Tokens compose

key_tokens:
  - "`AGENTESEPath`" → token type
  - "`TaskCheckbox`" → token type
  - "`DocumentPolynomial`" → state machine
```

### 6. `spec/protocols/typed-hypergraph.md` — Context as Graph

```yaml
agentese_path: self.context
tier: PROTOCOL
confidence: 0.85  # Implemented via exploration harness
lines: ~500

edges:
  extends:
    - spec/agents/composition.md  # Category theory base
  implements:
    - impl/claude/protocols/exploration/types.py
    - impl/claude/protocols/context/
  tests:
    - impl/claude/protocols/context/_tests/
  extended_by:
    - Exploration Harness
    - Portal Tokens
    - SpecGraph

principle_draws:
  - Composable: 0.95 (CATEGORICAL)  # Graph composition
  - Generative: 0.80 (EMPIRICAL)  # Derives exploration
```

### 7. `spec/agents/composition.md` — The >> Operator

```yaml
agentese_path: concept.composition
tier: BOOTSTRAP
confidence: 1.0  # Axiomatic
lines: ~300

edges:
  extends:
    - spec/principles.md  # Composable principle
    - Category theory (external)
  implements:
    - impl/claude/agents/core/skeleton.py  # compose method
    - impl/claude/agents/bootstrap/compose.py
  tests:
    - impl/claude/agents/bootstrap/_tests/test_bootstrap.py
  extended_by:
    - spec/agents/operads.md
    - spec/agents/functors.md
    - Every composable agent

principle_draws:
  - Composable: 1.0 (CATEGORICAL)  # IS the principle
  - Generative: 0.90 (CATEGORICAL)  # Generates pipelines
```

### 8. `spec/agents/operads.md` — Composition Grammar

```yaml
agentese_path: concept.operads
tier: FUNCTOR
confidence: 0.92  # Laws verified
lines: ~400

edges:
  extends:
    - spec/agents/composition.md
    - spec/agents/primitives.md
  implements:
    - impl/claude/agents/operad/core.py
    - impl/claude/agents/operad/algebra.py
  tests:
    - impl/claude/agents/operad/_tests/
  extended_by:
    - spec/agents/flux.md
    - spec/services/town.md (TOWN_OPERAD)

principle_draws:
  - Composable: 0.95 (CATEGORICAL)
  - Generative: 0.90 (CATEGORICAL)  # AD-003
```

### 9. `spec/protocols/agentese.md` — The Universal Protocol

```yaml
agentese_path: concept.agentese
tier: PROTOCOL
confidence: 0.95  # 559 tests
lines: ~600

edges:
  extends:
    - spec/principles.md  # Five contexts from principles
    - spec/agents/composition.md  # Path composition
  implements:
    - impl/claude/protocols/agentese/
  tests:
    - impl/claude/protocols/agentese/_tests/  # 559 tests
  extended_by:
    - Every AGENTESE node registration
    - CLI handlers (route to paths)

principle_draws:
  - Composable: 0.95 (CATEGORICAL)  # Paths compose
  - Heterarchical: 0.90 (CATEGORICAL)  # No fixed hierarchy
  - Ethical: 0.85 (EMPIRICAL)  # Observer determines perception
```

### 10. `spec/k-gent/persona.md` — The Soul Spec

```yaml
agentese_path: self.soul
tier: POLYNOMIAL
confidence: 0.88  # K-gent derivation
lines: ~400

edges:
  extends:
    - spec/principles.md  # All 7 principles
    - spec/agents/primitives.md  # PolyAgent base
  implements:
    - impl/claude/services/soul/
    - CLAUDE.md persona integration
  tests:
    - impl/claude/services/soul/_tests/
  extended_by:
    - The Mirror Test (meta)

principle_draws:
  - Tasteful: 0.85 (SOMATIC)  # Kent's judgment
  - Joy-Inducing: 0.88 (AESTHETIC)
  - Ethical: 0.92 (EMPIRICAL)
```

---

## Dependency Graph (ASCII)

```
                              PRINCIPLES (P0)
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
         COMPOSITION          PRIMITIVES            AGENTESE
              │                    │                    │
              ▼                    ▼                    │
           OPERADS             FUNCTORS                 │
              │                    │                    │
              ├────────────────────┘                    │
              ▼                                         ▼
            FLUX ◄─────────────────────────── TYPED-HYPERGRAPH
              │                                         │
              │        ┌────────────────────────────────┤
              │        ▼                                ▼
              │   EXPLORATION-HARNESS            PORTAL-TOKEN
              │        │                                │
              │        ▼                                │
              │   DERIVATION ◄──────────────────────────┤
              │        │                                │
              │        ▼                                ▼
              └───► WITNESS ◄────────────────── INTERACTIVE-TEXT
                       │
                       ▼
                   SPECGRAPH (this is what we're building!)
```

---

## Edge Type Catalog

| Edge Type | Meaning | Example |
|-----------|---------|---------|
| `extends` | Conceptual extension | flux.md extends composition.md |
| `implements` | Code realization | core.py implements composition.md |
| `tests` | Test coverage | test_bootstrap.py tests composition.md |
| `extended_by` | What builds on this | operads.md extended by flux.md |
| `references` | Mentions but doesn't extend | "See also" |
| `cross_pollinates` | Related genus | K-gent + M-gent synergy |
| `contradicts` | Dialectic tension | (rare, but valuable) |
| `heritage` | External source | arXiv paper, book, etc. |

---

## Token Patterns Across Specs

| Pattern | Regex | Count | Purpose |
|---------|-------|-------|---------|
| AGENTESE paths | `` `(world\|self\|concept\|void\|time)\.[a-z_.]+` `` | ~200 | Navigation |
| AD references | `\(AD-\d+\)` | ~50 | Decision links |
| Principle refs | `\(Tasteful\|Curated\|...\)` | ~100 | Principle draws |
| Impl refs | `` `impl/claude/[^`]+` `` | ~150 | Implementation links |
| Test refs | `` `_tests/[^`]+` `` | ~80 | Test links |
| Type refs | `` `[A-Z][a-zA-Z]+` `` | ~300 | Type definitions |

---

## Bootstrap Order

```
Phase 1: Parse and register these specs
  1. principles.md (root)
  2. composition.md (depends on: principles)
  3. primitives.md (depends on: composition)
  4. operads.md (depends on: primitives)
  5. agentese.md (depends on: composition)

Phase 2: Protocol layer
  6. typed-hypergraph.md (depends on: composition)
  7. exploration-harness.md (depends on: typed-hypergraph)
  8. portal-token.md (depends on: exploration-harness)
  9. derivation-framework.md (depends on: exploration, portal)
  10. interactive-text.md (depends on: portal)

Phase 3: Self-hosting
  11. specgraph itself (depends on: all above)
```

---

## Verification Plan

For each spec in the graph:

```bash
# Parse and register
kg specgraph register spec/agents/composition.md

# Verify edges discovered
kg specgraph edges spec/agents/composition.md
# → extends: [principles.md]
# → implements: [skeleton.py, compose.py]
# → tests: [test_bootstrap.py]
# → extended_by: [operads.md, functors.md, flux.md, ...]

# Verify derivation
kg derivation show composition.md
# → tier: BOOTSTRAP
# → confidence: 1.0
# → principle_draws: [Composable: 1.0]

# Portal navigation
kg portal spec/agents/composition.md implements
# → ▶ [impl/claude/agents/core/skeleton.py]
# → ▶ [impl/claude/agents/bootstrap/compose.py]
```

---

*"The map IS the territory when the territory is made of maps."*
