# Turn Protocol: The Fixed-Point Event Primitive

> *"A Turn is the Y combinator applied to agent state: (S, A) -> (S', B) where stability = (S = S')."*

**Status:** Spec v1.0
**Symbol:** Turn (the atomic causal event)
**Replaces:** Y-gent cognitive topology (archived)

---

## Purpose

The Turn Protocol defines the **atomic causal event** in agent interaction. It is the operational form of the Y combinator: a morphism from (state, input) to (state', output) with governance metadata, causal structure, and fixed-point semantics.

**Why this needs to exist** (Tasteful principle):

Without Turns, agents have no causal structure. Events are unordered, governance is ad-hoc, and fixed-point iteration is impossible. The Turn Protocol provides:

1. **Causal ordering** via happened-before relationships (Lamport clocks)
2. **Governance intercept** via YIELD turns that block for approval
3. **Fixed-point detection** via state hash comparison
4. **Thermodynamic accounting** via entropy cost tracking

---

## The Core Insight

Traditional event systems are flat: events happen, they're timestamped, done. Turn extends Event with **state morphism semantics**:

```
Traditional:  Event = (content, timestamp, source)
Turn:         Turn = (content, timestamp, source) + (S_pre -> S_post) + governance
```

The Turn captures the **transition** between states, not just what happened. This enables:

- **Stability detection**: `state_hash_pre == state_hash_post` means fixed point reached
- **Replay debugging**: State transitions are reproducible from turn history
- **Governance intercept**: High-risk transitions can YIELD for approval

---

## Formal Definition

### Turn as Morphism

```
Turn : (S_pre x Input) -> (S_post x Output)

Where:
- S_pre: Agent state before turn (hashed for storage)
- Input: The stimulus that triggered the turn
- S_post: Agent state after turn
- Output: The response produced
```

### Turn Types

Turns form an interface contract (game-semantic "moves"), not a taxonomy:

| Type | Game Move | Governance | Description |
|------|-----------|------------|-------------|
| `SPEECH` | Output | Inspectable | Utterance to user/agent |
| `ACTION` | Effect | Interceptable | Tool call, side effect |
| `THOUGHT` | Internal | Hidden default | Chain-of-thought |
| `YIELD` | Pause | Blocks | Request for human approval |
| `SILENCE` | Pass | Logged | Intentional non-action |

### The Five Turn Laws

1. **Immutability**: Turns are frozen; history cannot be rewritten
2. **Causality**: Turn B depends on Turn A iff B read A's output
3. **Observability**: THOUGHT turns hidden by default; others visible
4. **Governance**: ACTION and YIELD turns require governance review
5. **Stability**: Fixed point when `state_hash_pre == state_hash_post`

---

## The Weave: Concurrent Turn History

Turns compose into a **Weave**—a trace monoid that captures concurrent history.

### Mathematical Foundation

```
TraceMonoid M = (Events, Independence)

Where:
- Events: Partially ordered set of Turns
- Independence: Symmetric relation marking concurrent turns

Key property: Independent turns commute (ab = ba)
             Dependent turns don't (ab != ba)
```

This is the **Mazurkiewicz trace**—the same mathematical structure Y-gent's ThoughtGraph claimed to provide, but with proper categorical foundations.

### Operations

| Operation | Description |
|-----------|-------------|
| `record(turn)` | Add turn to weave with dependencies |
| `braid()` | Get dependency graph (DAG structure) |
| `thread(agent)` | Project to single agent's perspective |
| `knot(agents)` | Create synchronization point |
| `tip(agent?)` | Get latest turn (global or per-agent) |
| `linearize()` | Produce valid topological ordering |

---

## Fixed-Point Iteration

The Turn Protocol provides the machinery Y-gent's `Y.fix()` claimed:

### Stability Detection

```python
def is_stable(turn: Turn) -> bool:
    """A turn is stable if state didn't change."""
    return turn.state_hash_pre == turn.state_hash_post


def iterate_until_stable(
    agent: Agent[A, B],
    initial: A,
    max_iterations: int = 10,
) -> B:
    """
    Y-combinator style fixed-point iteration.

    Runs agent until output stabilizes (state stops changing).
    This replaces Y-gent's Y.fix() operator.
    """
    current = initial
    history: list[Turn] = []

    for i in range(max_iterations):
        turn = await agent.invoke_with_turn(current)
        history.append(turn)

        if is_stable(turn):
            return turn.content  # Fixed point reached

        if detect_cycle(history):
            return collapse_to_ground(history)  # Limit cycle

        current = turn.content

    return history[-1].content  # Best effort
```

### Cycle Detection

```python
def detect_cycle(history: list[Turn], window: int = 3) -> bool:
    """
    Detect limit cycles in turn history.

    A limit cycle occurs when state_hash repeats within window.
    """
    if len(history) < window:
        return False

    recent_hashes = [t.state_hash_post for t in history[-window:]]
    return len(recent_hashes) != len(set(recent_hashes))
```

---

## Causal Cone Projection

The **killer feature** of the Turn Protocol: automatic context projection.

### The Problem

Classical LLMs receive entire chat logs—noise. Most messages are irrelevant to the current turn.

### The Solution

Project the Weave onto an agent's **Causal Cone** (Light Cone / Past Cone):

```python
class CausalCone:
    """
    The Perspective Functor for Turn history.

    Instead of manually selecting context, CausalCone projects
    the Weave onto an agent's causal past.
    """

    def project_context(self, agent_id: str) -> list[Turn]:
        """
        Return MINIMAL causal history for agent's next turn.

        If Agent A never read Agent B's message,
        B's turn is NOT in A's cone.
        """
        tip = self.weave.tip(agent_id)
        if tip is None:
            return []

        # Compute transitive closure of dependencies
        causal_ids = self.braid.get_all_dependencies(tip.id)
        causal_ids.add(tip.id)

        # Linearize for LLM consumption
        return self.weave.linearize_subset(causal_ids)
```

### Compression Metrics

| Metric | Description |
|--------|-------------|
| `cone_size` | Number of turns in causal cone |
| `compression_ratio` | `1 - (cone_size / total_weave_size)` |

Higher compression = more irrelevant context eliminated.

---

## YIELD Governance

YIELD turns operationalize the **Ethical principle**: preserve human agency for high-risk actions.

### YieldTurn

```python
@dataclass(frozen=True)
class YieldTurn(Turn[T]):
    """
    A Turn that blocks until approval is granted.

    This is the governance intercept point in the Turn Protocol.
    """
    yield_reason: str
    required_approvers: frozenset[str]
    approved_by: frozenset[str]

    def is_approved(self) -> bool:
        """All required approvals granted."""
        return self.required_approvers <= self.approved_by

    def approve(self, approver: str) -> YieldTurn[T]:
        """Record approval (returns new YieldTurn—immutable)."""
        return YieldTurn(
            ...,
            approved_by=self.approved_by | {approver},
        )
```

### Approval Strategies

| Strategy | Behavior |
|----------|----------|
| `ALL` | All required approvers must approve |
| `ANY` | First approval wins |
| `MAJORITY` | >50% of required approvers |

### Risk-Based Yielding

```python
def should_yield(
    confidence: float,
    yield_threshold: float,
    is_destructive: bool = False,
) -> bool:
    """
    Determine if an action should generate a YIELD turn.

    Low-confidence + high-risk actions yield for approval.
    """
    if is_destructive:
        return confidence < yield_threshold * 1.5
    return confidence < yield_threshold
```

---

## Integration

### AGENTESE Paths

Turn Protocol introduces paths under `self.weave.*` and `time.*`:

```
self.weave.braid     - Dependency structure
self.weave.thread    - Agent's own turn history
self.weave.tip       - Latest turn
self.weave.cone      - Causal cone projection

time.turns           - All turns in linearized order
time.turn            - Current turn being processed
time.witness         - N-gent trace of turn history
```

### Composition with Existing Agents

| Pattern | Composition | Result |
|---------|-------------|--------|
| Turn-aware agent | `Turn >> Agent` | Agent receives causal context |
| Governed action | `Agent >> YieldHandler` | Actions require approval |
| Persistent turns | `Symbiont(Turn)` | D-gent stores turn history |
| Research flow | `Flow >> Turn` | F-gent research with stability detection |

---

## Relationship to Other Specs

### Subsumes Y-gent

The Turn Protocol **replaces** Y-gent's cognitive topology:

| Y-gent Concept | Turn Protocol Equivalent |
|----------------|--------------------------|
| `ThoughtNode` | `Turn` (richer: state hashes, governance) |
| `ThoughtGraph` | `TraceMonoid` / `Weave` |
| `Y.fix(criterion)` | `iterate_until_stable()` |
| `Y.branch(n)` | F-gent `FLOW_OPERAD.branch` |
| `Y.merge(strategy)` | F-gent `FLOW_OPERAD.merge` |
| V-gent termination | `is_stable()` + YIELD governance |
| B-gent budget | `TurnBudgetTracker` |

### Enables F-gent

F-gent's research modality uses Turn Protocol for:
- Tree-of-thought as turn DAG
- Hypothesis stability as fixed-point
- Branch/merge as weave operations

### Enables N-gent

N-gent (Narrator) witnesses turn history:
- `time.witness` path provides turn traces
- Causal cone enables "time travel" debugging
- Turn linearization enables story generation

---

## Implementation

```
impl/claude/weave/
├── __init__.py           # Public API
├── event.py              # Base Event class
├── turn.py               # Turn, TurnType, YieldTurn
├── trace_monoid.py       # TraceMonoid (concurrent history)
├── dependency.py         # DependencyGraph (braid)
├── weave.py              # TheWeave (high-level API)
├── causal_cone.py        # CausalCone (perspective functor)
├── yield_handler.py      # YieldHandler (governance)
├── economics.py          # TurnBudgetTracker
├── fixed_point.py        # iterate_until_stable, detect_cycle
└── _tests/
    ├── test_turn.py
    ├── test_trace_monoid.py
    ├── test_causal_cone.py
    ├── test_yield_handler.py
    └── test_fixed_point.py
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Mitigation |
|--------------|---------|------------|
| **Flat History** | Ignoring causal structure | Use CausalCone projection |
| **Governance Bypass** | Skipping YIELD for speed | Governance is mandatory for ACTION |
| **Infinite Loop** | No fixed-point detection | `max_iterations` + cycle detection |
| **State Amnesia** | Not hashing state | State hashes enable stability detection |
| **Context Bloat** | Feeding full history | Causal cone eliminates irrelevant turns |

---

## Principles Alignment

| Principle | How Turn Protocol Aligns |
|-----------|--------------------------|
| **Tasteful** | Single purpose: causal event with governance |
| **Curated** | Five turn types only—no taxonomy explosion |
| **Ethical** | YIELD preserves human agency for high-risk actions |
| **Joy-Inducing** | Causal cone makes context feel "right" |
| **Composable** | Turns compose via TraceMonoid laws |
| **Heterarchical** | No fixed turn ordering; causality determines order |
| **Generative** | Turn history generates replay, debugging, stories |

---

## References

- Lamport, "Time, Clocks, and the Ordering of Events" (1978)
- Mazurkiewicz, "Trace Theory" (1977)
- Spivak, "Polynomial Functors" (2023-2024)
- Abramsky, "Game Semantics" (1994-present)

---

## See Also

- `spec/f-gents/research.md` - Research flow uses Turn stability
- `spec/n-gents/README.md` - Narrator witnesses turn history
- `spec/protocols/agentese.md` - AGENTESE path integration
- `impl/claude/weave/` - Reference implementation

---

*"The noun is a lie. There is only the rate of change. A Turn captures that change."*
