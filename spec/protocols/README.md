# Protocols: Cross-Cutting Coordination Patterns

**Where agents meet to form higher-order behaviors.**

---

## What Are Protocols?

Protocols are **coordination patterns** that emerge when multiple agent genera work together toward a unified goal. Unlike individual agents (which are morphisms), protocols are **functors** that map entire categories of agents into coordinated systems.

```
Protocol : (Agent₁ × Agent₂ × ... × Agentₙ) → CoordinatedSystem
```

A protocol is not a single agent—it is the **grammar of interaction** between agents.

---

## The Protocol Catalog

| Protocol | Purpose | Key Agents | Status |
|----------|---------|------------|--------|
| [turn.md](turn.md) | Fixed-point event primitive, causal history | F, N, Ω | Spec v1.0 |
| [cli.md](cli.md) | Human-agent interface membrane | P, K, O | Spec v1.0 |
| [cross-pollination.md](cross-pollination.md) | Agent coordination without coupling | W, L, M, K | Spec v1.0 |
| [mirror.md](mirror.md) | Organizational introspection | P, W, H, O, J | Spec v1.0 |
| bootstrap.md | Irreducible kernel verification | T, O | Planned |
| composition.md | Multi-agent pipeline orchestration | C, O, T | Planned |

---

## Protocol Design Principles

### 1. Protocols Are Not Agents

An agent is a morphism: `Input → Output`
A protocol is a functor: `Category → Category`

Protocols don't *do* work—they coordinate work.

### 2. Protocols Respect Composition

Any protocol-coordinated system must still obey composition laws:
- Identity: The protocol with no agents is identity
- Associativity: `(P₁ ∘ P₂) ∘ P₃ ≡ P₁ ∘ (P₂ ∘ P₃)`

### 3. Protocols Have Surfaces

Every protocol defines an **interface surface**—the boundary between the protocol internals and the outside world. The CLI protocol defines the human-facing surface. The Mirror protocol defines the organizational-facing surface.

### 4. Protocols Are Heterarchical

Like agents, protocols can operate in both:
- **Functional mode**: Single invocation, defined outcome
- **Autonomous mode**: Continuous operation, event-driven

---

## Protocol Relationships

```
                    ┌─────────────────────────────────────┐
                    │           CLI Protocol              │
                    │     (Human-Agent Interface)         │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────┼───────────────────┐
                    │                 │                   │
                    ▼                 ▼                   ▼
           ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
           │ Mirror Protocol│ │  Composition   │ │   Bootstrap    │
           │ (Introspection)│ │   Protocol     │ │   Protocol     │
           └────────────────┘ └────────────────┘ └────────────────┘
                    │                 │                   │
                    ▼                 ▼                   ▼
           ┌─────────────────────────────────────────────────────┐
           │              Agent Genera (A-Z)                      │
           │   P-gents  W-gents  H-gents  J-gents  T-gents ...   │
           └─────────────────────────────────────────────────────┘
```

---

## Implementing a Protocol

A protocol implementation requires:

1. **Surface Definition**: What operations are exposed?
2. **Agent Coordination**: Which agents work together and how?
3. **State Threading**: How is context passed between agents?
4. **Mode Support**: Both functional and autonomous operation
5. **Observability**: O-gent integration for the three dimensions

### Example: Mirror Protocol Surface

```python
class MirrorProtocol:
    """
    The coordination pattern for organizational introspection.

    Agents involved:
    - P-gent: Extracts stated principles (Thesis)
    - W-gent: Observes actual patterns (Antithesis candidate)
    - H-gent: Detects tensions and proposes synthesis
    - O-gent: Reports on protocol health
    - J-gent: Executes interventions at kairos moments
    """

    def observe(self, target: Path) -> MirrorReport:
        """Functional mode: Single observation."""
        principles = P_gent.extract(target)
        patterns = W_gent.observe(target)
        tensions = H_gent.contradict(principles, patterns)
        return MirrorReport(tensions)

    async def watch(self, target: Path) -> AsyncIterator[Intervention]:
        """Autonomous mode: Continuous observation with kairos timing."""
        async for event in W_gent.stream(target):
            tensions = H_gent.check(event)
            for tension in tensions:
                kairos = await J_gent.await_kairos(tension)
                if kairos:
                    yield kairos.intervention
```

---

## The Protocol Stack

Protocols can compose into stacks:

```
┌─────────────────────────────────────┐
│ CLI Protocol (outermost)            │
│  ┌───────────────────────────────┐  │
│  │ Session Protocol              │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │ Mirror Protocol         │  │  │
│  │  │  ┌───────────────────┐  │  │  │
│  │  │  │ Composition Proto │  │  │  │
│  │  │  └───────────────────┘  │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

Each layer adds capabilities without breaking the inner layers.

---

## See Also

- [../principles.md](../principles.md) — Core design principles
- [../c-gents/README.md](../c-gents/README.md) — Composition theory
- [../bootstrap.md](../bootstrap.md) — Irreducible kernel
- [../../docs/mirror-protocol-implementation.md](../../docs/mirror-protocol-implementation.md) — Mirror Protocol phases

---

*"A protocol is a promise that agents make to each other about how they will collaborate."*
