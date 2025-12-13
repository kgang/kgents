---
path: architecture/turn-gents
status: active
progress: 100
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [architecture/polyfunctor, devex/trace-integration]
session_notes: |
  Initial synthesis from turn-gents3.md and turn-gents4.md
  Research validated against:
  - Lamport happened-before (1978) - still foundational
  - Mazurkiewicz traces (1977-1995) - exact match for TraceMonoid
  - Spivak Polynomial Functors (2023-2024) - active research
  - Game Semantics (Abramsky 1994-present) - dialogue as moves

  2025-12-13 (Phases 1-4 COMPLETE):
  - Phase 1: Turn schema implemented (TurnType, Turn, YieldTurn) - 46 tests
  - Phase 2: CausalCone + linearize_subset() - 21 tests
  - Phase 3: TurnBasedCapability Halo decorator - 8 tests
  - Phase 4: TurnBasedAdapter + LocalProjector integration - 12 tests
  - Total: 87 new tests, all passing, mypy clean
  - Files:
    - weave/turn.py (Turn, TurnType, YieldTurn)
    - weave/causal_cone.py (CausalCone, CausalConeStats)
    - weave/trace_monoid.py (linearize_subset)
    - agents/a/halo.py (TurnBasedCapability)
    - system/projector/local.py (TurnBasedAdapter)

  2025-12-13 (Phases 5-7 COMPLETE):
  - Phase 5: YieldHandler + approval strategies (All, Any, Majority) - 40 tests
  - Phase 6: TurnDAGRenderer for Terrarium TUI, fork/rewind - 25 tests
  - Phase 7: TurnBudgetTracker (order + surplus budgets) - 35 tests
  - Total for Phases 5-7: 100 new tests, all passing, mypy clean
  - New Files:
    - weave/yield_handler.py (YieldHandler, ApprovalStrategy, should_yield)
    - weave/economics.py (TurnBudgetTracker, BudgetPolicy)
    - agents/i/screens/turn_dag.py (TurnDAGRenderer, fork_from)
  - Updated:
    - system/projector/local.py (yield_handler, request_approval, should_yield)
    - weave/__init__.py (exports for all new modules)
  - TOTAL: 187 Turn-gents tests across all 7 phases
  - ALL PHASES COMPLETE
---

# Turn-gents: The Chronos-Kairos Protocol

> *"Context is not a window. Context is a Light Cone."*

**Status**: proposed
**AGENTESE Context**: `time.*` paths, TheWeave integration
**Principles**: Composable, Generative, Heterarchical, Tasteful
**Theory**: [Lamport Clocks](https://lamport.azurewebsites.net/pubs/time-clocks.pdf) × [Mazurkiewicz Traces](https://www.mimuw.edu.pl/~sl/teaching/22_23/TW/LITERATURA/book-of-traces-intro.pdf) × [Polynomial Functors](https://arxiv.org/abs/2312.00990) × [Game Semantics](https://www.irif.fr/~mellies/mpri/mpri-ens/articles/abramsky-mccusker-game-semantics.pdf)

---

## The Problem

Traditional agent systems treat context as a **window**—a sliding view over linear chat history. This creates:

1. **Context bloat**: Feed the whole log, hope the LLM finds relevance
2. **Causal blindness**: No distinction between dependent and concurrent events
3. **Debugging hell**: Log scraping for root cause analysis
4. **Governance gaps**: No principled intercept points

Turn-gents proposes: **Context is a Light Cone, not a Window.**

---

## Core Insight: Turns as Causal Events

### From Linear History to Partial Order

Classical LLMs: Feed entire chat log (noise).
The Weave: Feed only **causal ancestors** of the current Turn (signal).

The mathematical model:
- **Events** (Turns) form a partial order `(E, ⊑)`
- `a ⊑ b` means Turn `a` **happened-before** Turn `b` (Lamport)
- Concurrent turns (`a ⋢ b` and `b ⋢ a`) are invisible to each other

### Turn as Interaction Morphism

From Spivak's Polynomial Functors:

```
Turn: (S_pre × Input) → (S_post × Output)
```

A Turn is not a "log line" but a **morphism**—a state transformation with explicit dependencies.

```python
@dataclass
class Turn(Event[T]):
    """A Turn is an Event with causal structure."""
    dependencies: set[str]      # Incoming arrows (happened-before)
    turn_type: TurnType         # speech | action | thought | yield | silence
    state_hash_pre: str         # Hash of S_pre (for debugging)
    state_hash_post: str        # Hash of S_post (for debugging)
    confidence: float           # Meta-cognition
    entropy_cost: float         # Thermodynamic cost (Accursed Share)
```

### The Five Turn Types

| Type | Game Move | Governance | Description |
|------|-----------|------------|-------------|
| **Speech** | Output | Inspectable | Utterance to user/agent |
| **Action** | Effect | Interceptable | Tool call, side effect |
| **Thought** | Internal | Hidden by default | Chain-of-thought |
| **Yield** | Pause | Blocks until resolved | Request for human approval |
| **Silence** | Pass | Logged | Intentional non-action |

These form an interface contract (game-semantic "moves"), not a taxonomy explosion.

---

## The Perspective Functor: Auto-Context

The "killer feature" of Turn-gents: **automatic context projection**.

Instead of manually selecting context, implement a **Perspective Functor** that projects the Weave onto an agent's **Causal Cone**:

```python
class CausalCone:
    """
    Implements the Past Light Cone projection.
    Ref: Lamport 'Happened-Before' Relation.
    """
    def __init__(self, weave: TheWeave):
        self.weave = weave
        self.braid = weave.braid()  # DependencyGraph

    def project_context(self, agent_id: str) -> list[Turn]:
        """
        Return MINIMAL causal history for agent's next turn.

        If Agent A never read Agent B's message,
        Agent B's turn is NOT in A's cone.
        This mathematically eliminates context bloat.
        """
        # 1. Get agent's tip (last known state)
        tip = self.weave.tip(agent_id)
        if tip is None:
            return []

        # 2. Compute transitive closure of dependencies
        causal_history = self.braid.get_causal_past(tip.id)

        # 3. Linearize (topological sort) for LLM consumption
        return self.weave.monoid.linearize_subset(causal_history)
```

### Why This Matters

1. **Context efficiency**: Only causal ancestors, not entire log
2. **Concurrency safety**: Independent threads don't pollute each other
3. **Debuggability**: Causal history is explicit and replayable

---

## The Knot as Sheaf Gluing (Consensus)

Knots are synchronization points—where independent threads must agree before proceeding.

Using **Sheaf Theory** vocabulary:
- **Local Sections**: Individual agent threads (divergent thinking)
- **Global Section**: The Knot where they agree (convergent thinking)
- **Restriction**: Knot validates that all local perspectives are compatible

When K-gent (Soul), B-gent (Banker), and L-gent (Lattice) need to agree on a deployment:
1. They weave toward a Knot
2. If the Knot ties successfully → **Consensus Truth**
3. If the Knot fails (incompatible states) → TraceMonoid rejects the append

This maps exactly to existing `TheWeave.synchronize()` and `TraceMonoid.knot()`.

---

## The Six Laws of Turn-gents

### Law 1 — Turn as Interaction Morphism
A Turn is the morphism `(S_pre × Input) → (S_post × Output)`. This aligns with Spivak's polynomial functor semantics.

### Law 2 — Causal Soundness (Lamport)
Every turn has explicit `dependencies: set[str]`. The Weave's order `⊑` is the transitive closure of dependency edges.

### Law 3 — Concurrency / Commutation (Mazurkiewicz)
Concurrent turns (`a ⋢ b` and `b ⋢ a`) commute at the trace level. This is the formal basis of "braids not lists."

### Law 4 — Perspective as Functor
Context is computed via `CausalCone.project_context()`, not manually curated. This is the categorical move: `Weave → List[Turn]`.

### Law 5 — Knots as Synchronization
A Knot is a barrier event enforcing consensus (sheaf gluing). Operationally: "no further turns until knot ties."

### Law 6 — Compositional Integrity
Turn-processing agents must still be valid kgents agents. Identity and associativity laws hold and are testable.

---

## Integration: Turn-gents as Halo + Projector

Following kgents' **Nucleus / Halo / Projector** architecture:

### The Turn Halo (Capability Declaration)

```python
@TurnBased(
    turn_schema=TurnSchema(types={Speech, Action, Thought, Yield}),
    dependency_policy=DependencyPolicy.CAUSAL_CONE,
    context_policy=ContextPolicy(cone_depth=None, thought_collapse=True),
    economics_policy=EconomicsPolicy(entropy_budget=0.1, yield_threshold=0.8),
)
class MyAgent(Agent[Input, Output]):
    """Turn-based agent with declared policies."""
    ...
```

This keeps Turn semantics **opt-in** (tasteful) and **declarative** (generative).

### The Turn Projector (Compilation)

The Projector compiles the Halo declaration into:
1. `weave.record_event(turn)` on every Turn commit
2. `CausalCone.project_context(agent_id)` before inference
3. Observability emission (maps onto O-gent ordering)

This achieves the **generative** principle: spec → implementation with high autopoiesis.

---

## Economics: The Accursed Share Integration

Turn-gents operationalizes the Accursed Share through **two budgets**:

| Budget | Purpose | Policy |
|--------|---------|--------|
| **Order Budget** | Production-critical turns | Metered, bounded entropy |
| **Surplus Budget** | Exploration, oblique turns | 10% allocation, expenditure sacred |

```python
@dataclass
class TurnEconomics:
    entropy_spent: float      # This turn's cost
    order_budget_remaining: float
    surplus_budget_remaining: float
    is_oblique: bool          # Explicitly labeled exploration
```

This makes "joy-inducing" and "accursed share" non-performative—they become **schedulable resource classes**.

---

## Falsifiable Hypotheses

### H1 — Context Efficiency
Auto-context via causal cone reduces prompt tokens while preserving decision quality.
- **Metric**: `ContextCompression = 1 - tokens(cone) / tokens(full_log)`
- **Metric**: Task success rate (post-hoc)

### H2 — Debuggability
Turn DAG + rewind/fork yields faster root-cause isolation.
- **Metric**: Mean time-to-fix on seeded failures
- **Mechanism**: Rewind to known turn boundary, branch

### H3 — Governance Correctness
Soul intercept + Yield turns reduce high-risk actions without blocking throughput.
- **Metric**: Prevented-risk events / total attempts
- **Metric**: Human approvals requested vs. unnecessary interruptions

### H4 — Concurrency Safety
Trace commutation prevents cross-thread leakage.
- **Metric**: Rate of events incorrectly included in context
- **Mechanism**: Cone projection excludes unrelated concurrent events by construction

---

## Principle Alignment Check

| Principle | Turn-gents Compliance |
|-----------|----------------------|
| **Tasteful** | Opt-in via `@TurnBased` Halo; no forced adoption |
| **Curated** | Five turn types only; not a taxonomy explosion |
| **Ethical** | Yield turns preserve human agency for high-risk actions |
| **Joy-Inducing** | Surplus budget explicitly reserves exploration capacity |
| **Composable** | Turns are morphisms; compose via Weave's monoid operations |
| **Heterarchical** | No central "turn manager"; agents record turns to shared Weave |
| **Generative** | Spec (Halo) compiles to impl (Projector) |
| **Accursed Share** | Two-budget system; surplus is sacred |

---

## Existing Infrastructure Mapping

Turn-gents builds on, not replaces, existing code:

| Existing | Turn-gents Addition |
|----------|---------------------|
| `TheWeave` | Becomes partial order store for Turns |
| `TraceMonoid` | Already supports `dependencies`, `knot()`, `linearize()` |
| `DependencyGraph` | Provides `get_causal_past()` (to implement) |
| `Event[T]` | `Turn` extends with `turn_type`, hashes, economics |
| `PolyAgent` | Turn-based agents use polynomial transitions |
| `SOUL_SHEAF` | Knots map to sheaf gluing operations |

---

## Sources

The theoretical foundations are well-established:

1. **Lamport, L. (1978)**. [Time, Clocks, and the Ordering of Events in a Distributed System](https://lamport.azurewebsites.net/pubs/time-clocks.pdf). Communications of the ACM.
2. **Mazurkiewicz, A. (1977-1995)**. [Introduction to Trace Theory](https://www.mimuw.edu.pl/~sl/teaching/22_23/TW/LITERATURA/book-of-traces-intro.pdf). The Book of Traces.
3. **Niu, N. & Spivak, D. I. (2023-2024)**. [Polynomial Functors: A Mathematical Theory of Interaction](https://arxiv.org/abs/2312.00990). arXiv/Cambridge University Press.
4. **Abramsky, S. (1994-present)**. [Game Semantics](https://www.irif.fr/~mellies/mpri/mpri-ens/articles/abramsky-mccusker-game-semantics.pdf). Various venues.
5. **Bataille, G. (1949)**. The Accursed Share. (Basis for entropy/cost tracking)

---

## Implementation Strategy

### Phase 1: Turn Schema (Foundation)

**Goal**: Define Turn as Event subclass without changing existing behavior.

**What**:
1. Create `impl/claude/weave/turn.py` with:
   - `TurnType` enum: `SPEECH | ACTION | THOUGHT | YIELD | SILENCE`
   - `Turn(Event[T])` dataclass with `turn_type`, `state_hash_pre`, `state_hash_post`, `confidence`, `entropy_cost`
   - Backwards-compatible: `Turn` IS-A `Event`, so existing Weave operations work unchanged

2. Add `DependencyGraph.get_causal_past(event_id)` method:
   - Return `set[str]` of all transitive dependencies
   - Already have `get_all_dependencies()` which does exactly this

**Tests**:
- Turn creation and type hierarchy
- Serialization/deserialization
- Event compatibility (Turn works with TheWeave unchanged)

**Exit Criteria**: Turn exists, is an Event, Weave doesn't break.

---

### Phase 2: Causal Cone Projection

**Goal**: Implement the Perspective Functor for automatic context.

**What**:
1. Create `impl/claude/weave/causal_cone.py` with:
   - `CausalCone` class wrapping TheWeave
   - `project_context(agent_id) -> list[Turn]` method
   - Uses existing `DependencyGraph.get_all_dependencies()` + `topological_sort()`

2. Add `TraceMonoid.linearize_subset(event_ids: set[str]) -> list[Event]`:
   - Linearize only specified events (not full weave)
   - Respects dependency ordering

**Tests**:
- Single-agent cone is all their turns plus dependencies
- Multi-agent concurrent turns are excluded from each other's cones
- Cone linearization respects happened-before

**Exit Criteria**: `CausalCone.project_context()` returns minimal causal history.

---

### Phase 3: Turn Halo Declaration

**Goal**: Create opt-in `@TurnBased` decorator for agents.

**What**:
1. Create `impl/claude/agents/halo/turn_based.py` with:
   - `TurnSchema` dataclass (allowed turn types)
   - `DependencyPolicy` enum (CAUSAL_CONE | THREAD_ONLY | EXPLICIT)
   - `ContextPolicy` dataclass (cone_depth, thought_collapse, etc.)
   - `EconomicsPolicy` dataclass (entropy_budget, yield_threshold)
   - `@TurnBased(...)` decorator

2. Halo stores declaration metadata; no runtime behavior yet.

**Tests**:
- Decorator applies without changing agent behavior
- Schema validation (reject invalid turn types)
- Policy defaults are sensible

**Exit Criteria**: Agents can declare turn-based policies; no runtime change.

---

### Phase 4: Turn Projector (Compilation)

**Goal**: Compile Halo declarations into runtime behavior.

**What**:
1. Create `impl/claude/agents/projector/turn_projector.py` with:
   - `TurnProjector.compile(agent)` method
   - Wraps agent's invoke/take_turn with:
     a. Context injection via `CausalCone.project_context()`
     b. Turn recording via `TheWeave.record(Turn(...))`
     c. Entropy metering (if EconomicsPolicy defined)

2. Integrate with existing Projector pattern (if one exists) or establish it.

**Tests**:
- Compiled agent records Turns to Weave automatically
- Context is cone-projected before each turn
- Entropy costs are tracked

**Exit Criteria**: `@TurnBased` agent gets auto-context and auto-recording.

---

### Phase 5: Yield Governance

**Goal**: Implement YIELD turn type with human approval flow.

**What**:
1. Add `YieldTurn` variant with:
   - `yield_reason: str`
   - `required_approvals: set[str]` (agent IDs, e.g., `{"k-gent", "human"}`)
   - `status: PENDING | APPROVED | REJECTED`

2. Yield blocks execution until resolved (async await on Knot).

3. Soul intercept: K-gent's `intercept()` can inject Yield turns for high-risk actions.

**Tests**:
- Yield turn blocks until approval
- Soul intercept triggers Yield for threshold-exceeding actions
- Rejected Yield prevents action completion

**Exit Criteria**: High-risk actions require approval; flow is non-blocking for approved turns.

---

### Phase 6: Debugger Integration (Terrarium)

**Goal**: Visualize Turn DAG in TUI.

**What**:
1. Add `TurnRenderer` to Terrarium TUI:
   - DAG visualization (not list)
   - Collapsible THOUGHT turns
   - Knot visualization as merge points
   - Causal cone highlighting for selected agent

2. Add rewind/fork capability:
   - Select a Turn node
   - Fork from that point (new branch in Weave)

**Tests**:
- DAG renders correctly for concurrent agents
- Thought collapse hides/shows properly
- Fork creates new branch without destroying history

**Exit Criteria**: Terrarium shows causal structure; rewind/fork works.

---

### Phase 7: Economics Integration

**Goal**: Operationalize the Accursed Share through budget tracking.

**What**:
1. Add `TurnBudgetTracker`:
   - `order_budget: float` (production-critical)
   - `surplus_budget: float` (exploration, 10% default)
   - Auto-replenish on schedule or event

2. Turns consume from appropriate budget:
   - `is_oblique=True` → surplus budget
   - Otherwise → order budget

3. Budget exhaustion triggers Yield (ask for more budget or stop).

**Tests**:
- Entropy consumption tracked per Turn
- Surplus budget explicitly labeled and tracked
- Budget exhaustion flows to Yield

**Exit Criteria**: Two-budget system operational; exploration is first-class.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| **Complexity creep** | Each phase is self-contained; stop anytime after Phase 2 |
| **Performance** | Causal cone computation is O(n) in dependencies; cache aggressively |
| **Adoption friction** | `@TurnBased` is opt-in; existing agents unchanged |
| **Over-engineering** | Each phase delivers value independently; no big-bang requirement |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Context Compression** | >50% token reduction vs. full log | A/B test on sample tasks |
| **Debug Time Reduction** | >30% faster root cause isolation | Seeded failure experiments |
| **Yield Accuracy** | <10% unnecessary interruptions | Human approval rate analysis |
| **Adoption** | >3 agent genera using Turn-gents | Count of `@TurnBased` usages |

---

## Changelog

- 2025-12-13: Initial synthesis from turn-gents3.md and turn-gents4.md
