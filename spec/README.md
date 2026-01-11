# The kgents Specification

This directory contains the conceptual specification for kgents—implementation-agnostic definitions of what agents should be.

---

## The Core Insight

> *"77 lines. Everything else derives from this."*

The entire kgents system derives from a minimal kernel of 3 axioms and 8 primitives. See [kernel.md](kernel.md) for the irreducible foundation.

```
LAYER 0: IRREDUCIBLES (cannot be derived)
  L0.1 ENTITY:   There exist things.
  L0.2 MORPHISM: Things relate.
  L0.3 MIRROR:   We judge by reflection.

LAYER 1: PRIMITIVES → LAYER 2: DERIVED → Implementation
```

---

## Reading Order

**Start here** — each builds on the previous:

1. **[kernel.md](kernel.md)** — The 77-line irreducible core (THE foundation)
2. **[principles/CONSTITUTION.md](principles/CONSTITUTION.md)** — Seven principles + seven articles
3. **[principles.md](principles.md)** — Expanded principles with heritage citations
4. **[anatomy.md](anatomy.md)** — What constitutes an agent
5. **[bootstrap.md](bootstrap.md)** — The seven bootstrap agents
6. **[agents/composition.md](agents/composition.md)** — The `>>` operator as primary abstraction
7. **[meta.md](meta.md)** — Navigating the derivation DAG

**Deep Dives** (read as needed):

| Topic | Location | Purpose |
|-------|----------|---------|
| AGENTESE Protocol | [protocols/agentese.md](protocols/agentese.md) | The verb-first ontology |
| Categorical Foundations | [agents/](agents/) | Functors, monads, operads, sheaves |
| K-Block | [k-block/](k-block/) | Derivation contexts and witnessing |
| Protocols | [protocols/](protocols/) | 59 protocol specifications |
| Theory | [theory/](theory/) | Galois modularization, operads, DP |

---

## Directory Structure

### Foundation Layer

| Directory | Contents | Purpose |
|-----------|----------|---------|
| `kernel.md` | 77 lines | The irreducible axioms |
| `principles/` | CONSTITUTION, meta, operational, decisions | The seven principles + governance |
| `anatomy.md` | Agent definition | What makes an agent an agent |
| `bootstrap.md` | Seven bootstrap agents | The minimal self-regenerating kernel |
| `heritage.md` | Academic lineage | DSPy, SPEAR, TextGRAD, Meta-Prompting citations |

### Agent Genera

| Genus | Directory | Focus |
|-------|-----------|-------|
| **A-gents** | [a-gents/](a-gents/) | Abstract, Art, Alethic (truth-preserving) |
| **B-gents** | [b-gents/](b-gents/) | Bio (resource-constrained), Banker (economics) |
| **Categorical** | [agents/](agents/) | Core: composition, functors, monads, operads, primitives |
| **F-gents** | [f-gents/](f-gents/) | Flux (streaming), Function (continuous agents) |
| **G-gents** | [g-gents/](g-gents/) | Grammar (linguistic structure, tongue) |
| **I-gents** | [i-gents/](i-gents/) | Interface (visualization, scales, view functors) |
| **J-gents** | [j-gents/](j-gents/) | JIT (lazy evaluation, stability, reality mapping) |
| **K-gent** | [k-gent/](k-gent/) | Kent's personalization functor (the system's soul) |
| **L-gents** | [l-gents/](l-gents/) | Library (curation, lattice, lineage) |
| **M-gents** | [m-gents/](m-gents/) | Memory (holographic, architecture, primitives) |
| **N-gents** | [n-gents/](n-gents/) | Narrator (story-telling, time-travel debugging) |
| **O-gents** | [o-gents/](o-gents/) | Observability (telemetry, bootstrap witness) |
| **P-gents** | [p-gents/](p-gents/) | Parser (multi-strategy, structured output) |
| **S-gents** | [s-gents/](s-gents/) | Studio (creative workspace) |
| **T-gents** | [t-gents/](t-gents/) | Testing (algebraic reliability, taxonomy) |
| **U-gents** | [u-gents/](u-gents/) | Utility (tool use, MCP integration) |
| **V-gents** | [v-gents/](v-gents/) | Vector (semantic geometry, embeddings) |
| **W-gents** | [w-gents/](w-gents/) | Wire (stigmergy, fidelity, interceptors) |

### Protocol & Architecture

| Directory | Files | Purpose |
|-----------|-------|---------|
| [protocols/](protocols/) | 59 specs | AGENTESE, witness, storage, projection, etc. |
| [theory/](theory/) | 8 specs | Galois modularization, operads, DP-native agents |
| [services/](services/) | 6 specs | Foundry, muse, verification, witness |
| [k-block/](k-block/) | 2 specs | Derivation contexts, ASHC integration |
| [ui/](ui/) | 6 specs | Constitutional graph, layout sheaf, procedural vitality |
| [surfaces/](surfaces/) | 2 specs | Hypergraph editor, membrane |
| [validation/](validation/) | 1 spec | Schema definitions |

### Supporting

| Directory | Purpose |
|-----------|---------|
| [patterns/](patterns/) | Infrastructure vs composition, monad transformers |
| [architecture/](architecture/) | Polyfunctor specifications |
| [synthesis/](synthesis/) | Implementation roadmap, radical transformation |
| [gallery/](gallery/) | Gallery v2 specification |
| [saas/](saas/) | SaaS proposal for kgents |

---

## The Derivation DAG

Specs form a **derivation DAG**, not a documentation hierarchy:

```
kernel.md (L0-L1)
     │
     ├─→ CONSTITUTION (L2: principles + articles)
     │        │
     │        ├─→ anatomy.md → bootstrap.md
     │        │
     │        ├─→ agents/composition.md → agents/operads.md → agents/flux.md
     │        │
     │        └─→ protocols/agentese.md → protocols/typed-hypergraph.md
     │
     └─→ theory/galois-modularization.md → theory/analysis-operad.md
```

**Confidence propagates** from bootstrap (immutable, confidence = 1.0) through derivations to implementation.

---

## Cross-Pollination Graph

Agents compose. Key integration points:

| Integration | Description |
|-------------|-------------|
| **Categorical Core** | |
| J+F | F-gent artifacts can be JIT-instantiated via J-gent |
| T+* | T-gents can test any agent via Spy/Mock patterns |
| K+* | K-gent functor lifts any agent into personalized space |
| O+* | O-gents observe all agents including bootstrap |
| **Data & Memory** | |
| M+D | M-gent holographic memory composes with D-gent persistence |
| V+M | M-gent uses V-gent for associative recall similarity |
| V+L | L-gent catalog delegates vector operations to V-gent |
| **Interface & Visualization** | |
| W+I | W-gent observation feeds I-gent visualization |
| I+G | I-gent scales use G-gent grammar for linguistic display |
| N+O | N-gent stories feed O-gent metrics |
| **Tools & Infrastructure** | |
| U+P | U-gent Tool parsing uses P-gent strategies |
| U+D | U-gent tools use D-gent caching |
| U+W | W-gent traces U-gent tool execution |
| **Economics** | |
| B+B | B-Banker controls B-Bio's resource allocation |
| B+O | O-gent ValueLedgerObserver monitors B-Banker economic health |

---

## Implementation Validation

The spec/impl relationship is bidirectional:

- **Spec → Impl**: Specifications prescribe behavior
- **Impl → Spec**: Successful patterns inform specification refinement

See `impl/claude/` for the reference implementation. Key validations:

- All 7 bootstrap agents implemented and law-verified
- 18+ agent genera with cross-pollination
- Passing tests validating spec compliance

**The Generative Test**: Could you delete `impl/` and regenerate it from `spec/`? If yes, the spec is generative.

---

## Spec Hygiene

> *"Spec is compression. If you can't compress it, you don't understand it."*

### The Generative Principle

A well-formed spec is **smaller than its implementation** but contains enough information to regenerate it. The spec is the compression; the impl is the decompression.

### Seven Bloat Patterns (Avoid)

| Pattern | Signal | Fix |
|---------|--------|-----|
| **Implementation Creep** | Functions >10 lines | Extract to `impl/` |
| **Roadmap Drift** | Week-by-week plans | Move to `plans/` |
| **Framework Comparisons** | Decision matrices | Move to `docs/` |
| **Gap Analyses** | Current vs Desired | Delete |
| **Session Artifacts** | Continuation prompts | Move to `plans/` |
| **File Listings** | Directory trees | One-line reference |
| **Test Code as Laws** | pytest functions | Algebraic equations |

### Five Compression Patterns (Use)

1. **Type signatures with `...`** — Show shape, hide body
2. **Laws as equations** — `F.map(g . f) = F.map(g) . F.map(f)`
3. **AGENTESE path chains** — `self.memory.crystallize → concept.association.emerge`
4. **ASCII diagrams** — Worth 100 lines of prose
5. **Summary tables** — Compress enumeration

### Line Limits

| Spec Type | Target | Hard Limit |
|-----------|--------|------------|
| Simple agent | 100-200 | 300 |
| Complex agent | 200-300 | 400 |
| Protocol | 300-400 | 500 |
| Core system | 400-500 | 600 |

**Full guide**: `docs/skills/spec-hygiene.md` | **Template**: `docs/skills/spec-template.md`

---

## Contributing New Agents

Before proposing, ask:

| Principle | Question |
|-----------|----------|
| Tasteful | Does this agent have a clear, justified purpose? |
| Curated | Does this add unique value, or duplicate something existing? |
| Ethical | Does this respect human agency and privacy? |
| Joy-Inducing | Would I enjoy interacting with this? |
| Composable | Can this work with other agents? Single outputs? |
| Heterarchical | Can this agent both lead and follow? |
| Generative | Could this be regenerated from spec? |

A "no" on any principle is a signal to reconsider.

---

## Notation Conventions

- **MUST** / **SHALL**: Absolute requirement
- **SHOULD**: Recommended but not required
- **MAY**: Optional
- `code blocks`: Refer to implementation artifacts
- *italics*: Defined terms

---

## Quick Reference

| Need | Go To |
|------|-------|
| "What are the core principles?" | [principles/CONSTITUTION.md](principles/CONSTITUTION.md) |
| "How do agents compose?" | [agents/composition.md](agents/composition.md) |
| "What is AGENTESE?" | [protocols/agentese.md](protocols/agentese.md) |
| "What's the kernel?" | [kernel.md](kernel.md) |
| "How do I navigate this?" | [meta.md](meta.md) |
| "What decisions are binding?" | [principles/decisions/INDEX.md](principles/decisions/INDEX.md) |

---

*"The noun is a lie. There is only the rate of change."*
