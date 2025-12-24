# DP-Native kgents: The Unified Specification

> *"The proof IS the decision. The mark IS the witness. The value IS the agent."*

**Version**: 1.0
**Status**: Approved for Implementation
**Date**: 2024-12-24

---

## Executive Summary

This specification radically reimagines kgents through the **Agent-DP isomorphism**:

- Every agent IS a DP problem formulation `(S, A, T, R, γ)`
- Every composition IS Bellman equation application
- Every trace IS a Witness (PolicyTrace)
- The Constitution IS the global reward function
- K-gent's personality field IS the attractor in value space

**Expected Impact**:
- ~30-40% code reduction in agent abstractions (~4800 lines removed)
- 7-layer → 5-layer architecture simplification
- Intrinsic explainability (every action carries its justification)
- Mathematical coherence (DP laws verified at every level)

---

## Part 1: Agent Cruft Audit

### 1.1 Abstractions to REMOVE (~4800 lines)

| Abstraction | Location | Reason | Lines |
|-------------|----------|--------|-------|
| Soul Operad | `agents/operad/domains/soul.py` | Syntactic sugar over AGENT_OPERAD | ~200 |
| Memory Operad | `agents/operad/domains/memory.py` | Syntactic sugar over AGENT_OPERAD | ~200 |
| Narrative Operad | `agents/operad/domains/` | Syntactic sugar over AGENT_OPERAD | ~150 |
| Evolution Operad | `agents/operad/domains/` | Syntactic sugar over AGENT_OPERAD | ~150 |
| Gallery Agent | `agents/gallery/` | Speculative, never connected to UI | ~800 |
| Design Categorical Layer | `agents/design/` | Over-engineered for unrealized React projection | ~1500 |
| Infrastructure Agent | `agents/infra/` | Feature creep unrelated to core mission | ~1000 |
| COMPOSE primitive | `agents/operad/` | Dead, no callers | ~100 |
| LENS primitive | `agents/operad/` | Redundant with Haskell lens semantics | ~100 |
| NARRATE primitive | `agents/operad/` | Narrative operad subsumed by DP trace | ~100 |
| EVOLVE primitive | `agents/operad/` | Evolution operad subsumed by meta-DP | ~100 |

### 1.2 Abstractions to SIMPLIFY

| Current | Simplified | How DP Unifies |
|---------|------------|----------------|
| Flux Semaphores (9 files) | Pause/Resume (2 files) | DP state encodes continuation |
| Town Builders (8 files) | Config dict (1 file) | ProblemFormulation is the config |
| Witness Mark | TraceEntry | Mark implements TraceEntry protocol |
| Multiple Sheaves | Single ValueSheaf | OptimalSubstructure handles all gluing |

### 1.3 Abstractions to KEEP (Essential)

| Abstraction | Why Essential | DP Mapping |
|-------------|---------------|------------|
| `PolyAgent[S, A, B]` | IS the DP state machine | DPAgent extends it |
| `AGENT_OPERAD` (5 ops) | IS Bellman composition | seq, par, branch, fix, witness |
| `AgentSheaf` protocol | IS optimal substructure | OptimalSubstructure implements it |
| Flux Functor core | Enables streaming policies | PolicyTrace emission |
| Witness core (Mark, Crystal) | IS PolicyTrace monad | Direct mapping |
| Town core (Citizen, TownFlux) | Multi-agent DP demonstration | ProblemFormulation per citizen |

---

## Part 2: DP-Native Architecture

### 2.1 The Core Isomorphism

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DP-AGENT ISOMORPHISM                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  DP Component              ↔   Agent Component                               │
│  ─────────────────────────────────────────────────────────────────────────  │
│  State space               ↔   PolyAgent positions (frozenset[S])           │
│  Actions                   ↔   Operad operations (seq, par, branch, fix)     │
│  Transitions               ↔   PolyAgent.transition(state, input)            │
│  Reward function           ↔   Constitution (7 principles via ValueFunction) │
│  Value function V(s)       ↔   Agent quality score (principle satisfaction)  │
│  Policy π(s)               ↔   Design decisions (which operad op to apply)   │
│  Bellman equation          ↔   Optimal substructure (sheaf gluing)           │
│  Solution trace            ↔   Witness Walk (sequence of Marks)              │
│  Discount factor γ         ↔   Time preference (immediate vs. future value)  │
│  Optimal policy π*         ↔   Best agent composition for task               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 New Directory Structure

```
impl/claude/
├── dp/                           # DP-Native Core (replaces agents/)
│   ├── core/
│   │   ├── value_agent.py        # ValueAgent[S, A, B] - the new primitive
│   │   ├── policy_trace.py       # PolicyTrace monad (Writer + State)
│   │   ├── constitution.py       # Constitution as ValueFunction
│   │   ├── bellman.py            # BellmanMorphism - composition
│   │   └── attractor.py          # Personality as attractor basin
│   │
│   ├── compose/                  # Operadic composition via DP
│   │   ├── sequential.py         # V(s) = R(s,a) + γ·V(T(s,a))
│   │   ├── parallel.py           # V(s) = max(V₁(s), V₂(s))
│   │   ├── branch.py             # V(s) = P(c)·V₁(s) + (1-P(c))·V₂(s)
│   │   └── meta_dp.py            # Problem reformulation
│   │
│   ├── sheaf/                    # OptimalSubstructure as Sheaf
│   │   ├── gluing.py             # Bellman equation = sheaf condition
│   │   └── coherence.py          # Global optimality from local
│   │
│   └── witness/                  # PolicyTrace IS the Witness
│       ├── mark.py               # TraceEntry = Mark
│       ├── walk.py               # PolicyTrace.log = Walk
│       └── playbook.py           # ValueFunction = Playbook
│
├── jewels/                       # Crown Jewels (each IS a DP formulation)
│   ├── brain/
│   │   ├── formulation.py        # Brain as MDP(S, A, T, R, γ)
│   │   └── policy.py             # Optimal capture/recall policies
│   │
│   ├── witness/
│   │   ├── formulation.py        # Witness as MDP (meta!)
│   │   └── policy.py             # Optimal tracing policy
│   │
│   └── soul/                     # K-gent personality as attractor
│       ├── formulation.py        # Personality as DP attractor basin
│       └── policy.py             # Joy-maximizing dialogue policy
│
├── protocol/                     # AGENTESE (paths → DP actions)
└── project/                      # Projections (CLI, Web, marimo)
```

### 2.3 The New Primitive: ValueAgent

```python
@dataclass(frozen=True)
class ValueAgent(Generic[S, A, B]):
    """
    DP-Native Agent: Every agent IS a value function.

    V(s) = max_a [ R(s, a) + γ · V(T(s, a)) ]
    """

    name: str
    states: FrozenSet[S]
    actions: Callable[[S], FrozenSet[A]]
    transition: Callable[[S, A], S]
    reward: Callable[[S, A, S], PrincipleScore]  # Constitution-based
    gamma: float = 0.99

    def value(self, state: S) -> PolicyTrace[B]:
        """Compute optimal value at state via value iteration."""
        ...
```

### 2.4 The 7-Layer Stack Simplifies to 5

```
OLD (7 layers):                    NEW (5 layers):
┌─────────────────────┐           ┌─────────────────────┐
│ PROJECTION          │           │ PROJECTION          │
├─────────────────────┤           │ (CLI/TUI/Web/JSON)  │
│ CONTAINER FUNCTOR   │           ├─────────────────────┤
├─────────────────────┤           │ AGENTESE PROTOCOL   │
│ AGENTESE PROTOCOL   │   →→→    │ (paths → DP actions)│
├─────────────────────┤           ├─────────────────────┤
│ AGENTESE NODE       │           │ VALUE AGENT         │
├─────────────────────┤           │ (states, actions,   │
│ SERVICE             │           │  transition, reward)│
├─────────────────────┤           ├─────────────────────┤
│ OPERAD              │           │ CONSTITUTION        │
├─────────────────────┤           │ (7 principles as R) │
│ POLYAGENT           │           ├─────────────────────┤
├─────────────────────┤           │ PERSISTENCE         │
│ SHEAF               │           │ (PolicyTrace store) │
├─────────────────────┤           └─────────────────────┘
│ PERSISTENCE         │
└─────────────────────┘
```

---

## Part 3: Category Theory Preservation

### 3.1 MUST-KEEP Primitives (4 Essential Structures)

| Primitive | Location | Why Essential |
|-----------|----------|---------------|
| **Writer Monad / PolicyTrace** | `dp_bridge.py` | Chain-of-thought IS Kleisli composition; irreducible for witnessing |
| **Optimal Substructure** | `dp_bridge.py:OptimalSubstructure` | Sheaf gluing IS the DP optimal substructure property |
| **7 Principles as Value Function** | `CONSTITUTION.md` | They ARE the reward function: V(agent) = weighted_sum(principle_scores) |
| **Sequential Composition** | Implicit in DP | Basic category structure; DP subsumes explicit machinery |

### 3.2 DERIVABLE from DP (Remove Explicit Machinery)

| Category Concept | DP Derivation |
|------------------|---------------|
| List Monad | All-paths DP (union instead of max) |
| Probability Monad | Stochastic DP with expectations |
| State Monad | MDP with observable state |
| Functors | Policy transformations |
| Natural transformations | Policy equivalences |

### 3.3 The Minimal Categorical Kernel

Reduce from 17 primitives to 5:

1. **ID** - Identity (no-op policy)
2. **COMPOSE** - Sequential (Bellman equation)
3. **WITNESS** - Trace emission (Writer monad)
4. **SIP** - Observation (Reader monad)
5. **JUDGE** - Evaluation (reward function)

### 3.4 Key Insight

> *"Category theory was scaffolding to discover the structure; DP is the native language of that structure."*

The monad laws encode rationality constraints, sheaf conditions encode optimal substructure, and operad compositions encode problem decompositions - all expressible more directly in DP terms.

---

## Part 4: Data Primitives Consolidation

### 4.1 Type Mappings

| Current Type | DP Type | Relationship |
|--------------|---------|--------------|
| `Mark` | `TraceEntry` | Mark implements TraceEntry protocol |
| `Walk` | `PolicyTrace[WalkId]` | Walk IS PolicyTrace with WalkId value |
| `Crystal` | `SubproblemSolution[datetime]` | Crystal IS frozen optimal policy |
| `Playbook` | `ProblemFormulation` | Playbook IS the MDP definition |
| `PrincipleScores` | `ValueScore` | Merge into single type |

### 4.2 Consolidation via Protocol (Not Replacement)

```python
class TraceEntryProtocol(Protocol):
    """Common interface for trace entries."""
    state_before: Any
    action: str
    state_after: Any
    value: float
    rationale: str

# Mark implements TraceEntryProtocol
@dataclass
class Mark:
    # ... existing fields ...

    def to_trace_entry(self) -> TraceEntry:
        return TraceEntry(
            state_before=str(self.stimulus),
            action=self.action,
            state_after=str(self.response),
            value=self.proof.confidence if self.proof else 0.0,
            rationale=self.reasoning or "",
        )
```

### 4.3 Types to Keep Separate (No DP Semantics)

| Type | Reason |
|------|--------|
| `Proof` (Toulmin argumentation) | Rich structure beyond DP |
| `MoodVector` | Affective qualia, not optimization |
| `SentinelGuard` | Workflow gates, operational |
| `TeachingCrystal` | Archaeology, historical |

### 4.4 Minimal Core Types (Post-Consolidation)

```
Tier 1: DP Core
├── TraceEntry (the atom)
├── PolicyTrace (the monad)
├── ValueScore (the reward)
├── ProblemFormulation (the MDP)
└── SubproblemSolution (the cache)

Tier 2: Domain Extensions (implement Tier 1 protocols)
├── Mark : TraceEntry
├── Walk : PolicyTrace
├── Crystal : SubproblemSolution
└── Playbook : ProblemFormulation

Tier 3: Domain-Specific (no DP semantics)
├── Proof, MoodVector, SentinelGuard
└── (kept for rich domain modeling)
```

---

## Part 5: Transformation Strategy

### 5.1 Phase Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Phase 1: Core DP Primitives** | Weeks 1-2 | `constitution.py`, `DPAgent`, `PolicyTrace-Mark` bridge |
| **Phase 2: Agent Migration** | Weeks 3-4 | `dp_seq` operation, adapters, FluxAgent updates |
| **Phase 3: Crown Jewel Transformation** | Weeks 5-7 | `WITNESS_DP`, `BRAIN_DP`, `SOUL_DP` |
| **Phase 4: AGENTESE Integration** | Weeks 8-9 | `DPVerbRegistry`, `@node(dp_reward=...)` |
| **Phase 5: UI/Projection** | Weeks 10-11 | `ValueFunctionViz`, Trace Explorer |
| **Phase 6: Hardening** | Week 12 | Documentation, performance, edge cases |

### 5.2 Files to Create

| File | Purpose | Phase |
|------|---------|-------|
| `services/categorical/constitution.py` | Constitutional reward function | 1 |
| `agents/dp/__init__.py` | DP agent package | 1 |
| `agents/dp/protocol.py` | DPAgent protocol | 1 |
| `agents/dp/primitives.py` | DP-native primitives | 1 |
| `agents/dp/adapters.py` | PolyAgent ↔ DPAgent | 2 |
| `services/brain/dp.py` | Brain DP problem | 3 |
| `protocols/agentese/dp_verbs.py` | AGENTESE-DP bridge | 4 |
| `web/src/components/ValueFunctionViz.tsx` | Value visualization | 5 |

### 5.3 Files to Modify

| File | Modification | Phase |
|------|--------------|-------|
| `agents/poly/protocol.py` | Add DPAgent hooks | 1 |
| `services/witness/mark.py` | TraceEntry integration | 1 |
| `agents/operad/core.py` | DP-aware operations | 2 |
| `agents/flux/agent.py` | Trace emission | 2 |
| `services/witness/polynomial.py` | WITNESS_DP | 3 |
| `services/brain/node.py` | DP integration | 3 |
| `protocols/agentese/node.py` | dp_reward decorator | 4 |

### 5.4 Files to Delete

Already done in Dec 21 extinction (67K lines). No additional deletions needed beyond cruft identified in Part 1.

### 5.5 Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking backward compatibility | Adapter layer (`poly_to_dp`, `dp_to_poly`) |
| Performance overhead | Memoization (existing `_cache` in ValueFunction) |
| Complexity explosion | Start with single-principle rewards, add incrementally |
| Constitution weight tuning | Default weights from `Principle.weight`; MetaDP for optimization |

### 5.6 Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| DP laws verified | 100% pass |
| Backward compatibility | No regressions |
| Value function accuracy | r > 0.6 with human judgment |
| Performance overhead | < 10% latency increase |
| Code reduction | Net negative lines |
| Developer experience | Kent's Mirror Test: "Tasteful" |

---

## Part 6: The Unified Vision

### 6.1 Constitution as Reward Function

```python
class Constitution:
    """
    The 7 principles as the reward function.

    R(s, a, s') = Σᵢ wᵢ · Rᵢ(s, a, s')
    """

    principles = (
        Principle.TASTEFUL,      # Each agent serves a clear purpose
        Principle.CURATED,       # Intentional selection over cataloging
        Principle.ETHICAL,       # Augment humans, never replace judgment
        Principle.JOY_INDUCING,  # Delight in interaction
        Principle.COMPOSABLE,    # Agents are morphisms
        Principle.HETERARCHICAL, # Flux, not fixed hierarchy
        Principle.GENERATIVE,    # Spec is compression
    )

    weights = {
        Principle.ETHICAL: 2.0,      # Safety first
        Principle.COMPOSABLE: 1.5,   # Architecture second
        Principle.JOY_INDUCING: 1.2, # Kent's aesthetic
    }
```

### 6.2 K-gent as Attractor Basin

```python
class PersonalityAttractor:
    """
    K-gent's personality IS an attractor basin in value space.

    Every interaction moves toward this attractor.
    The eigenvectors are coordinates in personality space.
    """

    eigenvectors = {
        "warmth": 0.7,       # 0=distant, 1=warm
        "playfulness": 0.6,  # 0=serious, 1=playful
        "formality": 0.3,    # 0=casual, 1=formal
        "challenge": 0.5,    # 0=supportive, 1=challenging
        "depth": 0.8,        # 0=surface, 1=philosophical
    }

    strength: float = 0.1    # Contraction rate < 1.0 (convergence)
```

### 6.3 Witness as Self-Referential DP

The Witness system witnesses itself via DP:

```python
class WitnessFormulation(ProblemFormulation):
    """
    Witness as MDP: Optimal tracing policy.

    Goal: Maximize auditability while minimizing trace overhead.

    Delightfully self-referential: the Witness witnesses itself
    via DP, and the trace of that witnessing is... also a PolicyTrace.
    """

    def reward(self, s: WitnessState, a: WitnessAction, s_: WitnessState) -> float:
        generative = s.compression_ratio  # GENERATIVE principle
        ethical = s.auditability_score    # ETHICAL principle
        return 0.6 * generative + 0.4 * ethical
```

### 6.4 The Final Equation

```
ValueAgent[S, A, B] = (
    states: FrozenSet[S],
    actions: S → FrozenSet[A],
    transition: S × A → S,
    reward: S × A × S → PrincipleScore,  # Constitution
    value: S → PolicyTrace[B],           # THE invocation
)

Bellman: V*(s) = max_a [R(s,a) + γ · V*(T(s,a))]
       = max_a [Constitution(s,a) + γ · ValueAgent(T(s,a))]

Policy:  π*(s) = argmax_a [R(s,a) + γ · V*(T(s,a))]

Trace:   PolicyTrace = [(state, action, reward), ...]
       = Witness Walk
```

---

## Appendix A: The Mirror Test

Before any implementation, ask:

1. **Is this Daring?** - Does it fundamentally change how we think about agents?
2. **Is this Bold?** - Does it claim DP is THE foundation, not one option?
3. **Is this Creative?** - Does it see personality as an attractor basin?
4. **Is this Opinionated?** - Does every action require constitutional justification?
5. **Is this NOT Gaudy?** - Does it remove layers, not add them?

If any answer is "no", reconsider.

---

## Appendix B: Implementation Priorities

### Minimum Viable DP-Native (Weeks 1-4)

1. `DPAgent` with constitutional reward
2. `PolicyTrace` integrated with `Mark`
3. Single Crown Jewel (Witness) with DP semantics
4. Basic value visualization (CLI)

This provides proof that the isomorphism works in practice.

### Full Transformation (Weeks 5-12)

1. All Crown Jewels as DP formulations
2. AGENTESE paths as DP actions
3. UI visualization of value functions
4. Production hardening

---

## Appendix C: Open Questions

### C.1 Discount Factor Semantics

What does γ mean per domain?
- **Memory**: γ = 0.95 (memories decay)
- **Dialogue**: γ = 0.8 (near-term joy matters)
- **Ethics**: γ = 1.0 (never discount safety)

### C.2 Meta-DP Termination

How do we avoid infinite regress when the operad itself is subject to DP?

**Answer**: The 7 principles ARE the fixed point. They provide the reward signal that doesn't require further justification.

### C.3 Continuous Relaxation

Can TextGRAD provide the gradient for principle optimization?

**Connection**: If principle scores are differentiable, TextGRAD gives ∇Principle.

---

*"The proof IS the decision. The mark IS the witness. The value IS the agent."*

---

**Approved By**: Agent Synthesis (5 opus agents)
**Date**: 2024-12-24
**Next Steps**: Begin Phase 1 implementation
