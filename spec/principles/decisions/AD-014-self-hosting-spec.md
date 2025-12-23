# AD-014: Self-Hosting Spec Architecture

**Date**: 2025-12-22

> Specs are not documentation—they are the navigable, editable, witnessed source of truth. The system works on itself from inside.

---

## Context

kgents accumulated 193+ specs across 20 agent genera. But specs were static markdown files read by humans and Claude. The goal was always: specs that the system itself can navigate, edit, and verify. This AD formalizes the layered architecture that makes self-hosting possible.

## Decision

Specs form a derivation DAG with confidence propagation:

```
                              PRINCIPLES (Bootstrap, confidence = 1.0)
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
         COMPOSITION            PRIMITIVES             AGENTESE
              │                      │                      │
              ▼                      ▼                      │
           OPERADS              FUNCTORS                    │
              │                      │                      │
              ├──────────────────────┘                      │
              ▼                                             ▼
            FLUX ◄──────────────────────────────── TYPED-HYPERGRAPH
              │                                             │
              └───► WITNESS ◄───────────────────── SPECGRAPH (self-hosting surface)
```

## The Six Systems

| System | Purpose | Spec |
|--------|---------|------|
| **SpecGraph** | Specs as navigable hypergraph (193 nodes, 734 edges) | `typed-hypergraph.md` |
| **ASHC** | Empirical evidence: spec ↔ implementation equivalence | `ASHC-agentic-self-hosting.md` |
| **K-Block** | Monadic isolation for spec editing with hyperdimensional views | `k-block.md` |
| **Interactive Text** | Six token types make specs live interfaces | `interactive-text.md` |
| **Portal Tokens** | Inline expansion: navigation IS expansion | `portal-token.md` |
| **Membrane** | Co-thinking surface where Kent and K-gent work together | `membrane.md` |

## The Self-Hosting Loop

```
1. NAVIGATE        Claude opens spec in SpecView via SpecGraph
       │
       ▼
2. EXPAND          Portal tokens reveal [implements], [tests], [extends]
       │
       ▼
3. EDIT            K-Block provides isolated editing universe
       │
       ▼
4. WITNESS         Save → witness mark → decision recorded
       │
       ▼
5. EVIDENCE        ASHC runs verification, updates derivation confidence
       │
       ▼
6. PROPAGATE       Cosmos updates, dependents marked stale, loop repeats
```

## Key Insights

1. **Specs have derivation confidence**: Bootstrap specs (principles, composition, primitives) have confidence 1.0. Derived specs inherit confidence from ancestors × evidence.

2. **Typing from Typed-Hypergraph**: Specs are ContextNodes. Edges (extends, implements, tests) are typed hyperedges. Navigation is AGENTESE invocation.

3. **Editing is monadic**: K-Block wraps FILE_OPERAD operations. Changes don't escape to cosmos until explicit commit. Multiple views (prose, graph, code) sync bidirectionally within the monad.

4. **Interactive tokens are projections**: The six token types (AGENTESE path, task checkbox, image, code block, principle ref, requirement ref) project differently on CLI vs web but share semantic meaning.

5. **Witness is the memory**: Every significant operation emits a Mark. Decisions use `kg decide`. The trail IS the evidence for derivation confidence.

## Consequences

1. **Self-hosting is possible**: Claude can edit specs from inside the webapp
2. **Confidence propagates**: Implementation success → test pass → derivation update → spec confidence increase
3. **Specs are active**: Clicking AGENTESE paths in specs invokes them; checkboxes toggle state
4. **Time travel works**: K-Block cosmos is append-only; any version of any spec is recoverable
5. **The graph is navigable**: `kg context focus spec/principles.md` works like any other AGENTESE path

## Connection to Principles

| Principle | How AD-014 Embodies It |
|-----------|------------------------|
| **Composable** | All six systems compose: SpecGraph >> Portal >> K-Block >> Witness |
| **Generative** | This spec COULD regenerate its implementation (that's the test) |
| **Heterarchical** | No system "owns" specs; they flow through the graph |
| **Joy-Inducing** | Working on specs from inside the system is delightful |
| **Ethical** | All changes witnessed; confidence is transparent |

## Anti-patterns

- Specs as static files that only humans read (pre-AD-014 state)
- Implementation without derivation chain (no confidence trail)
- Editing specs outside the K-Block monad (changes escape without witness)
- Frontend that can't display the spec it implements (documentation shell)
- Evidence accumulation without confidence update (wasted work)

## Implementation

See `plans/SPECGRAPH-ASHC-SELF-HOSTING.md`

*Zen Principle: The spec that can't be edited by the system it specifies is mere aspiration.*
