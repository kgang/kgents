---
path: self/stream
status: complete
progress: 100
last_touched: 2025-12-12
touched_by: claude-opus-4.5
blocking: []
enables: [self/memory]
session_notes: |
  ALL PHASES COMPLETE:
  - Phase 2.1: ContextWindow, LinearityMap, Projector (181 tests)
  - Phase 2.2: ModalScope (44 tests)
  - Phase 2.3: Pulse, VitalityAnalyzer (35 tests)
  - Phase 2.4: StateCrystal, CrystallizationEngine (42 tests)
  self/memory is now UNBLOCKED
---

# Context Sovereignty: self.stream.* Implementation

> *"The brain that watches itself grow heavy is already dying. Health must be felt, not thought."*

**AGENTESE Context**: `self.stream.*`
**Status**: Phase 2.1 Complete (70%), Phase 2.2-2.4 Planned
**Principles**: Composable, Heterarchical, Accursed Share

---

## Executive Summary

Context management for AI agents is not merely "token bookkeeping"—it is a **thermodynamic system** where information pressure must be continuously managed. This plan provides a rigorous, category-theoretic foundation for context operations while remaining practically implementable.

**Core Insight**: The context window IS a [Store Comonad](https://ncatlab.org/nlab/show/store+comonad). This isn't a metaphor—it's a structural isomorphism that provides:
- `extract()`: Get the current focus (the "now" of conversation)
- `extend()`: Apply context-aware computation at every position
- `duplicate()`: Create nested contexts for **branching** (Modal Scope)

The [Galois Connection](https://math.libretexts.org/Bookshelves/Applied_Mathematics/Seven_Sketches_in_Compositionality:_An_Invitation_to_Applied_Category_Theory_(Fong_and_Spivak)/01:_Generative_Effects_-_Orders_and_Adjunctions/1.03:_Galois_Connections) structure for compression ensures we never claim lossless reduction—the developer is explicitly warned that `compress(expand(c)) ≤ c`.

---

## Part I: Theoretical Foundation

### 1.1 The Store Comonad

A comonad W on category C provides three operations satisfying specific laws:

```
W : Type → Type

extract   : W A → A                    -- "Get the current value"
extend    : (W A → B) → W A → W B      -- "Compute in context, return context"
duplicate : W A → W (W A)              -- "Nest contexts"
```

**Comonad Laws** (must hold for all implementations):
```
1. Left Identity:   extract . duplicate = id
2. Right Identity:  fmap extract . duplicate = id
3. Associativity:   duplicate . duplicate = fmap duplicate . duplicate
```

The **Store Comonad** specifically has the structure `(S → A, S)` where:
- `S` = Position type (index into history)
- `S → A` = Accessor function (peek at any position)
- Current `S` = The focus position

```python
@dataclass
class StoreComonad(Generic[S, A]):
    """
    Store s a ≅ (s → a, s)

    The position 's' is where we're currently focused.
    The function 's → a' lets us peek at any position.
    """
    position: S
    peek: Callable[[S], A]

    def extract(self) -> A:
        return self.peek(self.position)

    def extend(self, f: Callable[["StoreComonad[S, A]"], B]) -> "StoreComonad[S, B]":
        def new_peek(pos: S) -> B:
            return f(StoreComonad(pos, self.peek))
        return StoreComonad(self.position, new_peek)

    def duplicate(self) -> "StoreComonad[S, StoreComonad[S, A]]":
        def new_peek(pos: S) -> StoreComonad[S, A]:
            return StoreComonad(pos, self.peek)
        return StoreComonad(self.position, new_peek)
```

### 1.2 Why Comonads for Context?

Comonads excel at **context-dependent computation**. As [Bartosz Milewski notes](https://bartoszmilewski.com/2017/01/02/comonads/):

> "A comonad provides the means of extracting a single value from it. It does not give the means to insert values. So if you want to think of a comonad as a container, it always comes pre-filled with contents."

This perfectly models conversation context:
- Context is always "full"—you can't have an empty conversation
- You can extract the current turn (`extract`)
- You can transform context-aware computations across all positions (`extend`)
- You can create branching exploration paths (`duplicate`)

### 1.3 The Galois Connection for Compression

A **Galois Connection** between posets (L, ≤) and (R, ≤) consists of:
- Lower adjoint: `f : L → R`
- Upper adjoint: `g : R → L`

Such that: `f(l) ≤ r ⟺ l ≤ g(r)`

For context compression:
```
compress : FullContext → CompressedContext   (lower adjoint)
expand   : CompressedContext → FullContext   (upper adjoint)

Property: compress(expand(c)) ≤ c    -- "Round-trip loses information"
Property: s ≤ expand(compress(s))    -- "Expansion is always bigger"
```

**Critical**: This is NOT a lens. A lens requires `put(get(s), s) = s` (Get-Put law). Compression fundamentally violates this—we cannot recover discarded tokens. The Galois Connection structure makes this explicit.

### 1.4 Resource Linearity

Linear type systems ensure resources are used exactly once. Python cannot enforce this at the type level, so we use a **runtime ledger** (LinearityMap).

```
Resource Classes (partial order):
    DROPPABLE < REQUIRED < PRESERVED

Monotonicity: Once promoted, never demoted
    promote : (r, class) → (r, class') where class' ≥ class

Compression respects order:
    compress(window) drops only DROPPABLE resources first
```

---

## Part II: What's Already Implemented

### 2.1 ContextWindow (Store Comonad) ✅

**Location**: `agents/d/context_window.py` (41 tests)

```python
@dataclass
class ContextWindow:
    """Turn-level Store Comonad for agent context."""

    max_tokens: int = 100_000
    _turns: list[Turn]
    _position: int
    _linearity: LinearityMap
    _meta: ContextMeta

    def extract(self) -> Turn | None: ...
    def extend(self, f: Callable[[ContextWindow], B]) -> list[B]: ...
    def duplicate(self) -> list[ContextSnapshot[Turn | None]]: ...
    def seek(self, new_position: int) -> ContextWindow: ...
    def seeks(self, f: Callable[[int], int]) -> ContextWindow: ...
```

**Comonad Laws Verified**: Property-based tests confirm all three laws hold.

### 2.2 LinearityMap ✅

**Location**: `agents/d/linearity.py` (38 tests)

```python
class ResourceClass(IntEnum):
    DROPPABLE = 1  # May discard (observations)
    REQUIRED = 2   # Must flow to output (decisions)
    PRESERVED = 3  # Must survive verbatim (focus fragments)

@dataclass
class LinearityMap:
    """Runtime ledger for resource class tracking."""

    def tag(self, value: T, resource_class: ResourceClass, ...) -> str: ...
    def promote(self, resource_id: str, new_class: ResourceClass, ...) -> bool: ...
    def drop(self, resource_id: str) -> bool: ...  # Only DROPPABLE
```

**Monotonicity Enforced**: `promote()` rejects demotions.

### 2.3 ContextProjector (Galois Connection) ✅

**Location**: `agents/d/projector.py` (28 tests)

```python
@dataclass
class ContextProjector:
    """
    Galois Connection for context compression.

    NOT a Lens—compression is lossy. The developer is warned.
    Property: compress(expand(c_hat)) <= c_hat
    """

    async def compress(
        self,
        window: ContextWindow,
        target_pressure: float = 0.5,
    ) -> CompressionResult:
        """
        Strategy:
        1. Partition by resource class
        2. Drop DROPPABLE first
        3. Summarize REQUIRED (preserving decisions)
        4. NEVER touch PRESERVED
        """
```

### 2.4 AGENTESE Stream Context ✅

**Location**: `protocols/agentese/contexts/stream.py` (31 tests)

| Path | Operation | Implementation |
|------|-----------|----------------|
| `self.stream.focus` | Current turn | `extract()` |
| `self.stream.map` | Context transform | `extend()` |
| `self.stream.seek` | Navigate | `seek()` / `seeks()` |
| `self.stream.project` | Compress | `ContextProjector` |
| `self.stream.linearity` | Resource classes | `LinearityMap` |
| `self.stream.pressure` | Health check | `ContextMeta.pressure` |

### 2.5 MDL Compression Validation ✅

**Location**: `protocols/agentese/contexts/compression.py` (43 tests)

The "Ventura Fix" ensures spec quality:
```python
Quality = CompressionRatio × (1.0 - ReconstructionError)
```

An empty spec gets quality = 0, not infinity.

---

## Part III: What Remains (Phases 2.2-2.4)

### Phase 2.2: Modal Scope (Git-Backed Branching)

> *"What if we managed agent memory like a software engineer manages code?"*
> — [GCC: Git Context Controller](https://arxiv.org/html/2508.00031v1)

**The Insight**: The comonadic `duplicate()` operation naturally creates branching. When we duplicate a context, we get a context *of contexts*—each position becomes its own explorable branch.

```
                    ┌─────────────────────────────────┐
                    │         Main Context            │
                    │  [Turn1] [Turn2] [Turn3] ...    │
                    └─────────────┬───────────────────┘
                                  │ duplicate()
           ┌──────────────────────┼──────────────────────┐
           │                      │                      │
           ▼                      ▼                      ▼
    ┌──────────────┐     ┌──────────────┐      ┌──────────────┐
    │  Branch A    │     │  Branch B    │      │  Branch C    │
    │  (explore)   │     │  (safe)      │      │  (risky)     │
    └──────────────┘     └──────────────┘      └──────────────┘
           │                      │
           │ merge()              │ discard()
           │                      ▼
           │              [composted via void.entropy.pour]
           ▼
    ┌──────────────────────────────────────────────────────────┐
    │              Main Context (extended)                      │
    │  [Turn1] [Turn2] [Turn3] [BranchA-summary] ...           │
    └──────────────────────────────────────────────────────────┘
```

**Implementation**:

```python
@dataclass
class ModalScope:
    """
    Git-like branching for context exploration.

    AGENTESE: void.entropy.sip (branch) → void.entropy.pour (merge/discard)

    Category Theory: This is the comonadic duplicate() made persistent.
    """

    scope_id: str
    parent_scope: str | None
    branch_name: str
    created_at: datetime

    # The branched context window
    window: ContextWindow

    # Git-like metadata
    commit_message: str | None = None
    merge_strategy: MergeStrategy = MergeStrategy.SUMMARIZE

    # Entropy budget (how much exploration allowed)
    entropy_budget: float = 0.1  # 10% of main context tokens

    def branch(self, name: str, budget: float = 0.05) -> "ModalScope":
        """
        Create a child scope (duplicate + diverge).

        Budget limits how much the branch can grow before
        forced merge/discard.
        """
        child_window = ContextWindow.from_dict(self.window.to_dict())
        return ModalScope(
            scope_id=f"{self.scope_id}:{name}",
            parent_scope=self.scope_id,
            branch_name=name,
            window=child_window,
            entropy_budget=budget,
        )

    async def merge(self, child: "ModalScope") -> MergeResult:
        """
        Merge child branch back into this scope.

        Strategies:
        - SUMMARIZE: Compress child to summary turn
        - CHERRY_PICK: Select specific turns
        - SQUASH: Single turn with key decisions
        - REBASE: Replay child turns on current state
        """
        ...

    def discard(self, child: "ModalScope") -> None:
        """
        Compost the branch via void.entropy.pour.

        The branch's information is lost, but the entropy cost
        is returned to the main context's budget.
        """
        ...
```

**File Structure**:
```
agents/d/
├── modal_scope.py        # ModalScope, MergeStrategy, MergeResult
├── scope_tree.py         # ScopeTree (manages branch hierarchy)
└── _tests/
    ├── test_modal_scope.py
    └── test_scope_tree.py
```

**AGENTESE Integration**:
```python
# Branch for speculative exploration
await logos.invoke("void.entropy.sip", observer, branch_name="explore-api")

# In the branch, try risky operations...
# ...

# If successful, merge
await logos.invoke("void.entropy.pour", observer, action="merge")

# If failed, discard
await logos.invoke("void.entropy.pour", observer, action="discard")
```

**Exit Criteria**:
- `ModalScope.branch()` creates isolated context copy
- `ModalScope.merge()` with SUMMARIZE strategy compresses branch
- `ModalScope.discard()` cleanly removes branch
- Entropy budget limits branch growth
- 25+ tests covering branching, merging, discarding

---

### Phase 2.3: Dual-Lane Pheromones

> *"The brain that watches itself grow heavy is already dying."*

Health signals must be **zero-context cost**. We split into two channels:

| Channel | Medium | Use Case | Frequency |
|---------|--------|----------|-----------|
| **Fast** | Structured logs | Heartbeats, vitality | Every turn |
| **Slow** | K8s CRDs | State changes | Per-minute |

**Fast Lane (Pulse)**:

```python
@dataclass(frozen=True)
class Pulse:
    """
    Fast-lane vitality signal via structured logging.

    Zero LLM tokens required—pattern detection is heuristic.
    """
    agent: str
    timestamp: datetime
    pressure: float           # Context pressure (0-1)
    phase: str                # "thinking", "acting", "waiting"
    content_hash: str         # For loop detection
    turn_count: int

    def to_log(self) -> str:
        """PULSE|agent=l-gent|pressure=0.45|phase=thinking|..."""
        return f"PULSE|agent={self.agent}|pressure={self.pressure:.2f}|phase={self.phase}|hash={self.content_hash[:8]}|turns={self.turn_count}"

    @classmethod
    def from_log(cls, line: str) -> "Pulse | None":
        """Parse structured log line."""
        ...
```

**Pattern Detection** (no LLM calls):

```python
class VitalityAnalyzer:
    """
    Derive health from pulse patterns.

    - Regular intervals → Healthy
    - Erratic intervals → Degraded
    - Repeated hashes → Stuck (loop)
    - Rising pressure → Compress needed
    """

    def __init__(self, window_size: int = 20):
        self._pulses: deque[Pulse] = deque(maxlen=window_size)
        self._hash_counts: Counter[str] = Counter()

    def ingest(self, pulse: Pulse) -> VitalityStatus:
        """Analyze pulse and return status."""
        self._pulses.append(pulse)
        self._hash_counts[pulse.content_hash] += 1

        return VitalityStatus(
            is_healthy=self._check_regularity(),
            is_stuck=self._detect_loop(),
            needs_compression=self._check_pressure(),
            recommended_action=self._recommend(),
        )

    def _detect_loop(self, threshold: int = 3) -> bool:
        """Detect if same content hash appears too often."""
        most_common = self._hash_counts.most_common(1)
        return most_common[0][1] >= threshold if most_common else False
```

**Slow Lane (CRDs)**:

For persistent, infrequent signals that need K8s visibility:

```yaml
apiVersion: kgents.io/v1
kind: AgentVitality
metadata:
  name: l-gent-vitality
spec:
  agentRef: l-gent
  timestamp: "2025-12-12T10:30:00Z"
  status:
    phase: "active"
    pressure: 0.45
    lastCompression: "2025-12-12T09:15:00Z"
    scopeDepth: 2  # Modal Scope nesting
  signals:
    - type: COMPRESS_REQUEST
      reason: "Approaching 70% pressure"
    - type: BRANCH_ACTIVE
      branch: "explore-api"
```

**File Structure**:
```
agents/d/
├── pulse.py              # Pulse, VitalityAnalyzer
├── vitality_crd.py       # AgentVitality CRD helpers
└── _tests/
    ├── test_pulse.py
    └── test_vitality_analyzer.py
```

**Exit Criteria**:
- `Pulse.to_log()` / `Pulse.from_log()` roundtrip
- `VitalityAnalyzer` detects loops with >90% accuracy
- CRD schema defined in `infra/k8s/crds/`
- Zero LLM tokens for health checks
- 20+ tests

---

### Phase 2.4: State Crystallization

Crystals are checkpoints with comonadic lineage—they know their parent and can be restored or composted.

```python
@dataclass
class StateCrystal:
    """
    Checkpoint with linearity-aware compression.

    AGENTESE: self.memory.crystallize

    The crystal preserves the comonadic structure:
    - parent_crystal: The duplicate() chain
    - branch_depth: How nested is this scope?
    """

    crystal_id: str
    agent: str
    created_at: datetime

    # Core state (REQUIRED: preserved in compression)
    task_state: TaskState
    working_memory: dict[str, Any]

    # Compressed history (DROPPABLE masked)
    history_summary: str
    summary_token_count: int

    # Focus fragments (PRESERVED: verbatim)
    focus_fragments: list[FocusFragment]
    focus_token_count: int

    # Comonadic lineage
    parent_crystal: str | None
    branch_depth: int = 0
    scope_path: list[str] = field(default_factory=list)

    # Accursed Share lifecycle
    ttl: timedelta = timedelta(hours=24)
    pinned: bool = False
    access_count: int = 0
    last_accessed: datetime | None = None

    def cherish(self) -> None:
        """Pin crystal from reaping (self.memory.cherish)."""
        self.pinned = True

    def touch(self) -> None:
        """Record access, extending effective TTL."""
        self.access_count += 1
        self.last_accessed = datetime.now(UTC)

    @property
    def is_expired(self) -> bool:
        """Check if crystal should be composted."""
        if self.pinned:
            return False
        age = datetime.now(UTC) - self.created_at
        return age > self.ttl
```

**Crystallization Engine**:

```python
class CrystallizationEngine:
    """
    Creates and manages StateCrystals.

    Strategy:
    1. Extract PRESERVED fragments verbatim
    2. Summarize REQUIRED regions (preserving decisions)
    3. Discard DROPPABLE (observations, intermediate)
    4. Record comonadic lineage
    """

    def __init__(
        self,
        projector: ContextProjector,
        summarizer: Summarizer,
        storage: CrystalStorage,
    ):
        self._projector = projector
        self._summarizer = summarizer
        self._storage = storage

    async def crystallize(
        self,
        window: ContextWindow,
        scope: ModalScope | None = None,
        task_state: TaskState | None = None,
    ) -> StateCrystal:
        """
        Create a crystal from current context.

        AGENTESE: self.memory.crystallize
        """
        # Extract fragments by linearity class
        preserved = window.preserved_turns()
        required = window.required_turns()

        # Summarize required (decisions, reasoning)
        history_summary = await self._summarize_required(required)

        # Create crystal
        crystal = StateCrystal(
            crystal_id=self._generate_id(),
            agent=scope.scope_id if scope else "default",
            created_at=datetime.now(UTC),
            task_state=task_state or TaskState.IN_PROGRESS,
            working_memory={},
            history_summary=history_summary,
            summary_token_count=len(history_summary) // 4,
            focus_fragments=[
                FocusFragment(content=t.content, role=t.role.value)
                for t in preserved
            ],
            focus_token_count=sum(t.token_estimate for t in preserved),
            parent_crystal=self._get_parent_crystal_id(scope),
            branch_depth=scope.branch_depth if scope else 0,
            scope_path=scope.scope_path if scope else [],
        )

        await self._storage.store(crystal)
        return crystal

    async def resume(self, crystal_id: str) -> ContextWindow:
        """
        Restore context from crystal.

        AGENTESE: self.memory.resume
        """
        crystal = await self._storage.load(crystal_id)
        crystal.touch()

        window = create_context_window()

        # Restore preserved fragments first (verbatim)
        for fragment in crystal.focus_fragments:
            window.append(fragment.role, fragment.content)
            # Promote to PRESERVED
            if window._turns:
                window.promote_turn(
                    window._turns[-1],
                    ResourceClass.PRESERVED,
                    "restored from crystal",
                )

        # Add summary as REQUIRED
        if crystal.history_summary:
            window.append(
                TurnRole.SYSTEM,
                f"[Context Summary]\n{crystal.history_summary}",
            )

        return window
```

**Crystal Reaper** (Accursed Share composting):

```python
class CrystalReaper:
    """
    Composts expired crystals.

    AGENTESE: void.entropy.pour (for crystals)

    The Accursed Share: information that must be discharged
    to maintain system health.
    """

    async def reap(self, storage: CrystalStorage) -> ReapResult:
        """Remove expired, non-pinned crystals."""
        expired = await storage.find_expired()
        composted = 0
        retained = 0

        for crystal in expired:
            if crystal.pinned:
                retained += 1
                continue
            await storage.delete(crystal.crystal_id)
            composted += 1

        return ReapResult(composted=composted, retained=retained)
```

**Exit Criteria**:
- `CrystallizationEngine.crystallize()` creates valid crystals
- `CrystallizationEngine.resume()` restores context
- PRESERVED fragments survive verbatim (100%)
- `CrystalReaper` respects pinned crystals
- Comonadic lineage (parent_crystal) is tracked
- 30+ tests

---

## Part IV: Novel Architectural Insights

### 4.1 Context as Thermodynamic System

Context management can be modeled as a thermodynamic system:

| Thermodynamic Concept | Context Analog |
|----------------------|----------------|
| **Pressure** | Token count / Max tokens |
| **Temperature** | Activity rate (pulses/second) |
| **Entropy** | Information disorder (loop detection) |
| **Heat dissipation** | Compression (DROPPABLE removal) |
| **Phase transition** | Crystallization (liquid → solid) |
| **Free energy** | Available token budget for exploration |

**Insight**: The Accursed Share (from Georges Bataille) is the "excess heat" that must be dissipated. In context terms, this is the information that cannot be compressed further but also cannot be retained. It must be discharged via:
- **Potlatch**: Ritual discharge (generous summarization)
- **Branching**: Offloading to Modal Scope (spreading heat)
- **Crystallization**: Phase transition to persistent form

### 4.2 The GCC Connection

The [Git Context Controller](https://arxiv.org/html/2508.00031v1) research shows that versioned context management improves agent performance. Our `duplicate()` operation is the comonadic generalization:

```
GCC COMMIT ≈ crystallize()
GCC BRANCH ≈ duplicate() + ModalScope.branch()
GCC MERGE ≈ ModalScope.merge()
GCC CONTEXT ≈ extract() + seek()
```

The key innovation is grounding this in category theory—we get the compositional guarantees from comonad laws rather than ad-hoc implementation.

### 4.3 Adaptive Compression (ACON-Style)

Current implementation has static 70% threshold. Research on [adaptive activation functions](https://arxiv.org/html/2510.00615v1) suggests dynamic thresholds:

```python
@dataclass
class AdaptiveThreshold:
    base_threshold: float = 0.7
    task_progress: float = 0.0
    error_rate: float = 0.0
    loop_detected: bool = False

    @property
    def effective_threshold(self) -> float:
        t = self.base_threshold

        # Early task: preserve more context
        if self.task_progress < 0.2:
            t += 0.1

        # Near completion: compress aggressively
        if self.task_progress > 0.8:
            t -= 0.1

        # After errors: preserve debug info
        t += self.error_rate * 0.15

        # Loop detected: break pattern by compressing
        if self.loop_detected:
            t -= 0.15

        return max(0.5, min(0.95, t))
```

This is already implemented in `projector.py` but not yet wired to task progress detection.

### 4.4 KV-Cache Inspired Optimization

Research on [KV cache compression](https://github.com/HuangOwen/Awesome-LLM-Compression) shows that attention patterns reveal what's important. Future enhancement:

```python
class AttentionGuidedProjector:
    """
    Use attention scores to guide compression.

    High-attention tokens → PRESERVED
    Medium-attention tokens → REQUIRED
    Low-attention tokens → DROPPABLE

    Requires model introspection (future work).
    """
```

---

## Part V: Implementation Matrix

| Component | File | Status | Tests |
|-----------|------|--------|-------|
| ContextWindow | `agents/d/context_window.py` | ✅ Done | 41 |
| LinearityMap | `agents/d/linearity.py` | ✅ Done | 38 |
| ContextProjector | `agents/d/projector.py` | ✅ Done | 28 |
| StreamContextResolver | `protocols/agentese/contexts/stream.py` | ✅ Done | 31 |
| MDL Compression | `protocols/agentese/contexts/compression.py` | ✅ Done | 43 |
| ModalScope | `agents/d/modal_scope.py` | 📋 Phase 2.2 | - |
| ScopeTree | `agents/d/scope_tree.py` | 📋 Phase 2.2 | - |
| Pulse | `agents/d/pulse.py` | 📋 Phase 2.3 | - |
| VitalityAnalyzer | `agents/d/pulse.py` | 📋 Phase 2.3 | - |
| StateCrystal | `agents/d/crystal.py` | 📋 Phase 2.4 | - |
| CrystallizationEngine | `agents/d/crystal.py` | 📋 Phase 2.4 | - |
| CrystalReaper | `agents/d/crystal.py` | 📋 Phase 2.4 | - |

---

## Part VI: AGENTESE Path Registry

| Path | Operation | Component | Status |
|------|-----------|-----------|--------|
| `self.stream.focus` | Current turn | ContextWindow.extract() | ✅ |
| `self.stream.map` | Context transform | ContextWindow.extend() | ✅ |
| `self.stream.seek` | Navigate | ContextWindow.seek() | ✅ |
| `self.stream.project` | Compress | ContextProjector | ✅ |
| `self.stream.linearity` | Resource classes | LinearityMap | ✅ |
| `self.stream.pressure` | Health check | ContextMeta.pressure | ✅ |
| `self.memory.crystallize` | Checkpoint | CrystallizationEngine | 📋 |
| `self.memory.resume` | Restore | CrystallizationEngine | 📋 |
| `self.memory.cherish` | Pin crystal | StateCrystal.cherish() | 📋 |
| `self.vitality.sense` | Zero-cost health | FastChannel | 📋 |
| `void.entropy.sip` | Branch (duplicate) | ModalScope.branch() | 📋 |
| `void.entropy.pour` | Merge/discard | ModalScope.merge/discard | 📋 |
| `time.trace.pulse` | Heartbeat | Pulse.emit() | 📋 |

---

## Part VII: Success Criteria

| Metric | Current | Target |
|--------|---------|--------|
| Health check token cost | N/A | 0 tokens |
| Branch operation cost | N/A | <100 tokens |
| Crystal size | N/A | <10KB |
| etcd writes per agent/min | N/A | <0.1 |
| PRESERVED fragment survival | 100% | 100% |
| Comonad law compliance | 100% | 100% |
| Loop detection accuracy | N/A | >90% |
| Total tests | 181 | 250+ |

---

## Part VIII: Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Modal Scope complexity | Medium | High | Start with single-level branching |
| Merge conflicts | Medium | Medium | Default to SUMMARIZE strategy |
| Crystal storage growth | Low | Medium | Aggressive reaping, TTL defaults |
| Loop detection false positives | Medium | Low | Tunable threshold, human override |
| Performance overhead | Low | Medium | Lazy initialization, batch operations |

---

## Part IX: References

### Research Papers
- [Git Context Controller (GCC)](https://arxiv.org/html/2508.00031v1) - Git-style context management
- [Recurrent Context Compression (RCC)](https://arxiv.org/abs/2406.06110) - 32x compression with BLEU4 ~0.95
- [LLMLingua-2](https://arxiv.org/abs/2403.12968) - Task-agnostic prompt compression
- [Pretraining Context Compressor (PCC)](https://aclanthology.org/2025.acl-long.1394.pdf) - Embedding-based memory

### Category Theory
- [Store Comonad (nLab)](https://ncatlab.org/nlab/show/store+comonad)
- [Comonads - Bartosz Milewski](https://bartoszmilewski.com/2017/01/02/comonads/)
- [Galois Connections - Seven Sketches](https://math.libretexts.org/Bookshelves/Applied_Mathematics/Seven_Sketches_in_Compositionality:_An_Invitation_to_Applied_Category_Theory_(Fong_and_Spivak)/01:_Generative_Effects_-_Orders_and_Adjunctions/1.03:_Galois_Connections)
- [Lenses are coalgebras for the costate comonad](https://patternsinfp.wordpress.com/2011/01/31/lenses-are-the-coalgebras-for-the-costate-comonad/)

### Implementation Resources
- [Awesome LLM Compression](https://github.com/HuangOwen/Awesome-LLM-Compression)
- [Awesome LLM Long Context Modeling](https://github.com/Xnhyacinth/Awesome-LLM-Long-Context-Modeling)

---

*"Context is not a cage—it is a comonad. And comonads, unlike monads, always come pre-filled with contents."*
