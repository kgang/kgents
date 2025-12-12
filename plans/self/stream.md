# Context Sovereignty: self.stream.* Implementation

> *"The brain that watches itself grow heavy is already dying. Health must be felt, not thought."*

**AGENTESE Context**: `self.stream.*`
**Status**: Theoretical Foundation Complete, Implementation Planned
**Principles**: Composable, Heterarchical, Accursed Share

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Store Comonad** | `ContextWindow` uses `(S -> A, S)` structure. `duplicate()` enables Modal Scope. |
| **ContextProjector (not Lens)** | Lossy compression violates Get-Put law. Use Galois Connection. |
| **Resource Accounting (not Linear Types)** | Python cannot enforce linearity at type level. Runtime ledger. |
| **Dual-lane pheromones** | Fast (logs) vs slow (CRDs). Avoid etcd hammer. |
| **JetBrains masking** | Mask observations before summarizing reasoning. 52% cost reduction. |
| **Adaptive thresholds** | ACON-style: thresholds respond to task progress, not fixed 70%. |

---

## Theoretical Foundation

### The Context Comonad

```
W : Type → Type

extract : W A → A           "Get the current value"
extend : (W A → B) → W A → W B  "Compute in context, return context"
duplicate : W A → W (W A)   "Nest contexts"
```

**Key insight**: An agent's context window IS a comonad. `duplicate()` creates nested contexts for branching (Modal Scope).

### Resource Classes

| Class | Semantics | Example |
|-------|-----------|---------|
| `DROPPABLE` | May be discarded | Observations |
| `REQUIRED` | Must flow to output | Reasoning traces |
| `PRESERVED` | Must survive verbatim | Focus fragments |

---

## Store Comonad Implementation (📋 PLANNED)

```python
@dataclass(frozen=True)
class ContextWindow(Generic[A]):
    """
    The Store Comonad for agent state.

    Structure: (S -> A, S) where:
        S = Position (current focus in context history)
        S -> A = Peek function (access value at any position)
    """

    position: int                    # Current focus position
    peek: Callable[[int], A]         # Access any position
    history: tuple[A, ...]           # Materialized history
    metadata: ContextMeta            # Resource accounting

    def extract(self) -> A:
        """Comonad law: extract gives the current focus."""
        return self.peek(self.position)

    def extend(self, f: Callable[["ContextWindow[A]"], B]) -> "ContextWindow[B]":
        """Comonad law: extend applies f at every position."""
        ...

    def duplicate(self) -> "ContextWindow[ContextWindow[A]]":
        """
        Comonad law: duplicate nests the context.

        This is the key operation for Modal Scope—creates a context
        containing all possible "views" of the current context.
        """
        ...

    def seek(self, new_pos: int) -> "ContextWindow[A]":
        """Store-specific: Move focus to new position."""
        ...

    def seeks(self, f: Callable[[int], int]) -> "ContextWindow[A]":
        """Store-specific: Move focus by function."""
        ...
```

**Location**: `agents/d/context_comonad.py`

---

## ContextProjector (📋 PLANNED)

**Not a Lens**—this is a Galois Connection:

```python
class ContextProjector:
    """
    A Galois Connection for context compression.

    NOT a Lens—compression is lossy. Information is discarded.
    The developer is warned: there is no inverse.

    Property: compress(expand(c_hat)) <= c_hat
    """

    async def compress(
        self,
        context: ContextWindow[Turn],
        target_pressure: float = 0.5,
    ) -> ContextWindow[Turn]:
        """
        Compress context while respecting resource classes.

        Strategy:
        1. Partition by resource class
        2. Drop DROPPABLE regions first (observation masking)
        3. Summarize REQUIRED regions (preserving decisions)
        4. Never touch PRESERVED regions (focus fragments)
        """
        ...
```

**Location**: `agents/d/projector.py`

---

## Adaptive Thresholds (📋 PLANNED)

```python
@dataclass
class AdaptiveThreshold:
    """
    ACON-style adaptive compression thresholds.

    Key insight: Fixed thresholds (70%, 95%) ignore task dynamics.
    Adaptive thresholds respond to task progress.
    """

    base_threshold: float = 0.7
    task_progress: float = 0.0
    error_rate: float = 0.0
    loop_detection: bool = False

    @property
    def effective_threshold(self) -> float:
        """
        Compute adaptive threshold:
        - Early in task: Higher (keep more context)
        - Near completion: Lower (compress aggressively)
        - After errors: Higher (preserve debug info)
        - Loop detected: Lower (break the pattern)
        """
        ...
```

---

## Dual-Lane Pheromones (📋 PLANNED)

| Channel | Medium | Use Case | Rate |
|---------|--------|----------|------|
| **Fast** | Structured logs | Heartbeats, vitality | High frequency |
| **Slow** | K8s CRDs | State changes, requests | Low frequency |

### Fast Lane (Pulse)

```python
@dataclass
class Pulse:
    """Fast-lane vitality signal via structured logging."""
    agent: str
    pressure: float
    phase: str
    content_hash: str  # For loop detection

    def to_log(self) -> str:
        """Serialize to log: PULSE|agent=...|pressure=...|..."""
        ...
```

**Pattern detection** (no LLM calls):
- Regular intervals → Healthy
- Erratic intervals → Degraded
- Repeated hashes → Stuck
- Rising pressure → Compress needed

### Slow Lane (CRDs)

For infrequent, persistent signals:
- `BRANCH_REQUEST`
- `CRYSTALLIZE_REQUEST`
- `COMPRESS_REQUEST`
- `STATE_CHANGE`

---

## State Crystallization (📋 PLANNED)

```python
@dataclass
class StateCrystal:
    """
    Checkpoint with linearity-aware compression.

    AGENTESE: self.memory.crystallize
    """

    crystal_id: str
    agent: str
    timestamp: datetime

    # Core state (REQUIRED: must be preserved)
    task_state: TaskState
    working_memory: dict[str, Any]

    # Compressed history (DROPPABLE masked)
    history_summary: str
    summary_tokens: int

    # Focus fragments (PRESERVED: verbatim)
    focus_fragments: list[FocusFragment]
    focus_tokens: int

    # Comonadic structure
    parent_crystal: str | None    # For duplicate() chain
    branch_depth: int = 0

    # Accursed Share lifecycle
    ttl: timedelta = timedelta(hours=24)
    pinned: bool = False
```

---

## AGENTESE Path Registry

| Path | Operation | Component |
|------|-----------|-----------|
| `self.stream.focus` | Get current context | ContextWindow.extract() |
| `self.stream.map` | Context-aware transform | ContextWindow.extend() |
| `self.stream.project` | Compress context | ContextProjector |
| `self.stream.seek` | Navigate Store | ContextWindow.seek() |
| `self.memory.crystallize` | Create checkpoint | CrystallizationEngine |
| `self.memory.resume` | Restore checkpoint | Crystal → Context |
| `self.memory.cherish` | Pin from reaping | Set pinned=True |
| `self.vitality.sense` | Zero-context health | FastChannel |
| `void.entropy.sip` | Branch (duplicate) | ContextWindow.duplicate() |
| `void.entropy.pour` | Compost crystals | CrystalReaper |
| `time.trace.pulse` | Fast-lane heartbeat | Pulse.emit() |

---

## Implementation Phases

### Phase 2.1: Comonadic Foundation (📋 NEXT)
- [ ] `ContextWindow` Store Comonad
- [ ] Comonad law tests (property-based)
- [ ] `LinearityMap` for resource classes
- [ ] Bootstrap integration (Umwelt carries ContextWindow)

### Phase 2.2: Compression (📋 PLANNED)
- [ ] `ContextProjector` (Galois Connection)
- [ ] Observation masking (JetBrains pattern)
- [ ] Incremental summarization
- [ ] Adaptive thresholds

### Phase 2.3: Pheromones (📋 PLANNED)
- [ ] `Pulse` dataclass
- [ ] `FastChannel` (log-based)
- [ ] `SlowChannel` (CRD-based)
- [ ] Pattern analysis (vitality derivation)

### Phase 2.4: Crystallization (📋 PLANNED)
- [ ] `StateCrystal` format
- [ ] `CrystallizationEngine` (focus-aware)
- [ ] `CrystalReaper` (TTL-based composting)
- [ ] Entropy budget for branching

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Health check token cost | 0 tokens |
| Branch operation cost | <100 tokens |
| Crystal size | <10KB |
| etcd writes per agent/min | <0.1 |
| PRESERVED fragment survival | 100% |
| Comonad law compliance | 100% |

---

## Cross-References

- **Plans**: `self/memory.md` (Ghost = D-gent), `void/entropy.md` (Metabolism)
- **Impl**: `agents/d/` (D-gent), `infra/cortex/` (Channels)
- **Spec**: `spec/protocols/agentese.md` (AGENTESE paths)
- **References**:
  - [Contextads as Wreaths](https://www.emergentmind.com/papers/2410.21889) (Comonads)
  - [JetBrains Observation Masking](https://blog.jetbrains.com/research/2025/12/efficient-context-management/)
  - [ACON Adaptive Compression](https://arxiv.org/html/2510.00615v1)

---

*"Context is not a cage—it is a comonad."*
