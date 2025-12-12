# Context Sovereignty: A Category-Theoretic Framework for Agent Context Management

> *"The brain that watches itself grow heavy is already dying. Health must be felt, not thought."*

**Version**: 3.1
**Status**: Implementation Plan (Refined)
**Date**: 2025-12-11
**Refinements**: Store Comonad, ContextProjector (not Lens), Resource Accounting

---

## Critical Refinements (v3.1)

### Architectural Corrections Applied

| Original | Issue | Correction |
|----------|-------|------------|
| `CompressionLens` | Violates Get-Put law (lossy compression) | → `ContextProjector` (Galois Connection) |
| `Linearity` enum | Python cannot enforce linear types | → Runtime Resource Accounting via `Ledger` |
| Generic Comonad | Missing specific structure | → **Store Comonad** `(S -> A, S)` |

See `plans/lattice-refinement.md` for full rationale.

---

## Part I: Theoretical Foundation

### 1.1 The Context Comonad

Context management has deep roots in category theory. The **comonad** structure provides the mathematical foundation for context-dependent computation.

```
                    ┌─────────────────────────────────────────┐
                    │         THE CONTEXT COMONAD             │
                    │                                         │
                    │  W : Type → Type                        │
                    │                                         │
                    │  extract : W A → A                      │
                    │    "Get the current value"              │
                    │                                         │
                    │  extend : (W A → B) → W A → W B         │
                    │    "Compute in context, return context" │
                    │                                         │
                    │  duplicate : W A → W (W A)              │
                    │    "Nest contexts"                      │
                    │                                         │
                    └─────────────────────────────────────────┘
```

**Key Insight**: An agent's context window IS a comonad. The current state (`extract`) exists within surrounding history (`extend` over past), and branching (`duplicate`) creates nested contexts for exploration.

**Reference**: [Contextads as Wreaths in Category Theory](https://www.emergentmind.com/papers/2410.21889) (2024) unifies comonads, actegories, and contextful computation into a single framework.

### 1.2 Runtime Resource Accounting (Not Linear Types)

> **REFINEMENT (v3.1)**: Python's memory model (reference counting + GC) makes true linear types impossible. Calling this "Linear Types" would promise safety the runtime cannot guarantee. Instead, we implement **Runtime Resource Accounting**.

Context is a **tracked resource**—consumption is accounted for at runtime, not enforced at compile time.

```
                    ┌─────────────────────────────────────────┐
                    │      CONTEXT AS TRACKED RESOURCE        │
                    │                                         │
                    │  Token Ledger: Runtime accounting       │
                    │    → Issue tokens for resources         │
                    │    → Debit when consumed                │
                    │    → Violations detected at runtime     │
                    │                                         │
                    │  Resource Classes:                      │
                    │    → DROPPABLE: Can be discarded        │
                    │    → REQUIRED: Must flow to output      │
                    │    → PRESERVED: Must survive verbatim   │
                    │                                         │
                    └─────────────────────────────────────────┘
```

**Implementation**: Token Ledger (not type-level enforcement):
- **Observations**: Droppable tokens (can be masked)
- **Reasoning traces**: Required tokens (must reach output or summary)
- **Focus fragments**: Preserved tokens (must survive compression)

**Reference**: This is runtime accounting inspired by linear logic, not a claim of type-level safety. See `shared/accounting.py`.

### 1.3 Self-Adjusting Computation

Agent context updates should follow **incremental computation** principles—only recompute what changes.

```
                    ┌─────────────────────────────────────────┐
                    │    SELF-ADJUSTING COMPUTATION           │
                    │                                         │
                    │  Input Change → Propagate → Output      │
                    │       ↓             ↓           ↓       │
                    │  New observation  Identify    Updated   │
                    │                   affected    summary   │
                    │                   regions               │
                    │                                         │
                    │  Key Property: Δ-output ∝ Δ-input       │
                    │  (Small changes → small updates)        │
                    │                                         │
                    └─────────────────────────────────────────┘
```

**Application**: Compression should be **differential**—when context changes slightly, the compressed form changes proportionally, not via full re-summarization.

**Reference**: [Incremental Computing by Differential Execution](https://drops.dagstuhl.de/storage/00lipics/lipics-vol333-ecoop2025/LIPIcs.ECOOP.2025.20/LIPIcs.ECOOP.2025.20.pdf) (ECOOP 2025) provides formal semantics for change propagation.

### 1.4 Principle Alignment Analysis

The original v2.0 plan correctly identified principle alignment. This analysis adds **categorical justification**:

| Principle | v2.0 Manifestation | Categorical Basis |
|-----------|-------------------|-------------------|
| **Tasteful** | Dual-lane pheromone split | Functor decomposition (fast ⊥ slow) |
| **Curated** | Crystals compost unless cherished | Linearity (use or lose) |
| **Ethical** | Focus injection preserves intent | Relevance constraint |
| **Composable** | AGENTESE paths | Natural transformations |
| **Heterarchical** | Controller↔Agent via medium | Comonadic computation (local context) |
| **Generative** | Derived from Five Contexts | Free construction |
| **Accursed Share** | Entropy budget, TTL | Affine typing (may discard) |
| **AGENTESE** | All paths grounded | Yoneda embedding |

### 1.5 Critical Analysis of v2.0

**Strengths retained**:
1. Dual-lane pheromone architecture avoids etcd hammer
2. Focus injection addresses compression blind spot
3. Compost protocol handles garbage collection
4. AGENTESE grounding provides semantic coherence

**Gaps identified and addressed**:

| Gap | Issue | Resolution in v3.0 |
|-----|-------|-------------------|
| **No differential compression** | Full re-summarization wasteful | Incremental summary updates |
| **Missing linearity constraints** | No formal resource tracking | Type-level linearity markers |
| **Comonad structure implicit** | Branching ad-hoc | Explicit `duplicate`/`extend` |
| **No formal verification** | Properties claimed, not proven | Algebraic laws with tests |
| **Compression strategy static** | Single threshold (70%) | Adaptive thresholds (ACON-style) |

---

## Part II: Architecture

### 2.1 The Context Comonad Implementation

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable
from abc import ABC, abstractmethod

A = TypeVar('A')
B = TypeVar('B')


@dataclass(frozen=True)
class ContextWindow(Generic[A]):
    """
    The Store Comonad for agent state.

    REFINEMENT (v3.1): Explicitly implements Store Comonad structure:
        Store s a = (s -> a, s)

    Where:
        s = Position (current focus in context history)
        s -> a = Peek function (access value at any position)

    This gives us `duplicate` for free, which is exactly what
    we need for Git-backed counterfactuals (Modal Scope).

    Store Comonad operations:
    - extract: Get value at current position
    - extend: Compute f at every position
    - duplicate: Create context of all possible contexts
    - seek: Move focus to new position (Store-specific)
    - seeks: Move focus by function (Store-specific)
    """

    # Store Comonad components: (S -> A, S)
    position: int                    # S: Current focus position
    peek: Callable[[int], A]         # S -> A: Access any position
    history: tuple[A, ...]           # Materialized for efficiency
    metadata: ContextMeta            # Resource accounting, pressure, etc.

    def extract(self) -> A:
        """
        Comonad law: extract gives the current focus.

        Store-specific: peek at current position.

        AGENTESE: self.stream.focus
        """
        return self.peek(self.position)

    def extend(self, f: Callable[["ContextWindow[A]"], B]) -> "ContextWindow[B]":
        """
        Comonad law: extend applies f at every position.

        Store-specific: creates new store where each position
        contains f applied to the store focused at that position.

        AGENTESE: self.stream.map
        """
        def new_peek(pos: int) -> B:
            shifted = self._focus_at(pos)
            return f(shifted)

        return ContextWindow(
            position=self.position,
            peek=new_peek,
            history=tuple(new_peek(i) for i in range(len(self.history))),
            metadata=self.metadata.evolved(),
        )

    def duplicate(self) -> "ContextWindow[ContextWindow[A]]":
        """
        Comonad law: duplicate nests the context.

        Store-specific: each position contains the store focused there.
        This is the key operation for Modal Scope—creates a context
        containing all possible "views" of the current context.

        AGENTESE: void.entropy.sip (when materialized)
        """
        def new_peek(pos: int) -> ContextWindow[A]:
            return self._focus_at(pos)

        return ContextWindow(
            position=self.position,
            peek=new_peek,
            history=tuple(self._focus_at(i) for i in range(len(self.history))),
            metadata=self.metadata.branched(),
        )

    def _focus_at(self, new_pos: int) -> "ContextWindow[A]":
        """Shift focus to a different position (internal)."""
        return ContextWindow(
            position=new_pos,
            peek=self.peek,
            history=self.history,
            metadata=self.metadata,
        )

    # === Store-specific operations (beyond standard Comonad) ===

    def seek(self, new_pos: int) -> "ContextWindow[A]":
        """
        Move focus to new position.

        Store Comonad navigation. Does not change content.
        """
        return self._focus_at(new_pos)

    def seeks(self, f: Callable[[int], int]) -> "ContextWindow[A]":
        """
        Move focus by function (relative navigation).

        Example: seeks(lambda p: p - 1) moves focus back one step.
        """
        return self._focus_at(f(self.position))

    # === Comonad Laws (verified at runtime) ===

    @classmethod
    def verify_left_identity(cls, w: ContextWindow[A]) -> bool:
        """Law: extend(extract) == id"""
        extended = w.extend(lambda ctx: ctx.extract())
        return extended.focus == w.focus

    @classmethod
    def verify_right_identity(cls, w: ContextWindow[A], f: Callable) -> bool:
        """Law: extract(extend(f)(w)) == f(w)"""
        return w.extend(f).extract() == f(w)

    @classmethod
    def verify_associativity(cls, w: ContextWindow[A],
                             f: Callable, g: Callable) -> bool:
        """Law: extend(f)(extend(g)(w)) == extend(λx.f(extend(g)(x)))(w)"""
        lhs = w.extend(g).extend(f)
        rhs = w.extend(lambda x: f(x.extend(g)))
        return lhs.focus == rhs.focus


@dataclass
class ContextMeta:
    """
    Metadata for context resource tracking.

    REFINEMENT (v3.1): Renamed from "linearity" to "resource tracking".
    This is runtime accounting, not type-level enforcement.

    Resource classes (not linear types):
    - DROPPABLE: May be discarded (observations)
    - REQUIRED: Must flow to output (reasoning)
    - PRESERVED: Must survive compression verbatim (focus)
    """

    pressure: float                   # 0.0–1.0 context utilization
    resource_map: ResourceMap         # Token ranges → resource class
    branch_depth: int                 # Nesting level from duplicate()
    entropy_consumed: float           # Accursed share spent
    parent_crystal: str | None = None # For duplicate() chain
    agent_name: str = ""              # Owner agent

    def evolved(self) -> ContextMeta:
        """Create metadata for extended context."""
        return ContextMeta(
            pressure=self.pressure,
            linearity=self.linearity,
            branch_depth=self.branch_depth,
            entropy_consumed=self.entropy_consumed,
        )

    def branched(self) -> ContextMeta:
        """Create metadata for duplicated (branched) context."""
        return ContextMeta(
            pressure=self.pressure,
            linearity=self.linearity,
            branch_depth=self.branch_depth + 1,
            entropy_consumed=self.entropy_consumed + 0.1,
        )
```

### 2.2 Linearity-Aware Compression

```python
from enum import Enum
from dataclasses import dataclass


class Linearity(Enum):
    """
    Substructural linearity classes for context regions.

    Based on linear logic / substructural type systems.
    """
    AFFINE = "affine"       # May be dropped (observations)
    LINEAR = "linear"       # Must flow to output (reasoning)
    RELEVANT = "relevant"   # Must survive compression (focus)


@dataclass
class LinearityMap:
    """
    Maps token ranges to linearity constraints.

    This enables linearity-aware compression that:
    - Drops AFFINE regions aggressively
    - Summarizes LINEAR regions carefully
    - Preserves RELEVANT regions verbatim
    """

    regions: list[tuple[range, Linearity]]

    def classify(self, position: int) -> Linearity:
        """Get linearity class for a token position."""
        for token_range, linearity in self.regions:
            if position in token_range:
                return linearity
        return Linearity.AFFINE  # Default: can be dropped


class ContextProjector:
    """
    REFINEMENT (v3.1): Renamed from LinearityAwareCompressor.

    This is a Galois Connection, NOT a Lens.
    The compression is lossy—information is discarded.
    This warns the developer: there is no inverse.

    AGENTESE: self.stream.project (not compress)

    Key insight: Different parts of context have different
    resource tracking requirements. This is runtime accounting,
    not type-level enforcement.
    """

    async def compress(
        self,
        context: ContextWindow[Turn],
        target_pressure: float = 0.5,
    ) -> ContextWindow[Turn]:
        """
        Compress context while respecting linearity.

        Strategy:
        1. Partition by linearity class
        2. Drop AFFINE regions first (observation masking)
        3. Summarize LINEAR regions (preserving decisions)
        4. Never touch RELEVANT regions (focus fragments)
        """
        linearity_map = context.metadata.linearity

        # Partition turns by linearity
        affine_turns = []
        linear_turns = []
        relevant_turns = []

        for i, turn in enumerate(context.history):
            match linearity_map.classify(i):
                case Linearity.AFFINE:
                    affine_turns.append((i, turn))
                case Linearity.LINEAR:
                    linear_turns.append((i, turn))
                case Linearity.RELEVANT:
                    relevant_turns.append((i, turn))

        # Phase 1: Mask affine observations
        compressed_affine = [
            (i, self._mask_observation(turn))
            for i, turn in affine_turns
        ]

        current_pressure = self._compute_pressure(
            compressed_affine + linear_turns + relevant_turns
        )

        if current_pressure <= target_pressure:
            return self._rebuild_context(
                context, compressed_affine, linear_turns, relevant_turns
            )

        # Phase 2: Summarize linear regions incrementally
        summarized_linear = await self._incremental_summarize(
            linear_turns,
            target_tokens=self._tokens_for_pressure(
                target_pressure,
                len(relevant_turns),  # Reserved for focus
            ),
        )

        return self._rebuild_context(
            context, compressed_affine, summarized_linear, relevant_turns
        )

    def _mask_observation(self, turn: Turn) -> Turn:
        """
        JetBrains pattern: mask observation, keep reasoning.

        52% cost reduction with 2.6% higher solve rate.
        """
        return Turn(
            reasoning=turn.reasoning,
            action=turn.action,
            observation="[OBSERVATION MASKED]",
        )

    async def _incremental_summarize(
        self,
        turns: list[tuple[int, Turn]],
        target_tokens: int,
    ) -> list[tuple[int, Turn]]:
        """
        Differential summarization using self-adjusting computation.

        Key: Only re-summarize changed regions.
        """
        if not hasattr(self, '_summary_cache'):
            self._summary_cache = {}

        # Compute content hashes
        hashes = [self._hash_turn(t) for _, t in turns]

        # Find unchanged prefix
        unchanged_prefix = 0
        for i, h in enumerate(hashes):
            if self._summary_cache.get(i) == h:
                unchanged_prefix = i + 1
            else:
                break

        # Only summarize changed suffix
        changed_turns = turns[unchanged_prefix:]
        if not changed_turns:
            return self._cached_summary

        # Summarize changed region
        new_summary = await self.r_gent.compress(
            [t for _, t in changed_turns],
            strategy="anchored",
            max_tokens=target_tokens - self._cached_tokens(unchanged_prefix),
        )

        # Update cache
        for i, h in enumerate(hashes):
            self._summary_cache[i] = h

        return self._merge_summaries(
            self._cached_summary[:unchanged_prefix],
            new_summary,
        )
```

### 2.3 Adaptive Compression Thresholds

```python
@dataclass
class AdaptiveThreshold:
    """
    ACON-style adaptive compression thresholds.

    Key insight: Fixed thresholds (70%, 95%) ignore task dynamics.
    Adaptive thresholds respond to task progress.

    Reference: ACON (arXiv 2510.00615)
    """

    base_threshold: float = 0.7
    task_progress: float = 0.0      # 0.0–1.0
    error_rate: float = 0.0         # Recent error rate
    loop_detection: bool = False

    @property
    def effective_threshold(self) -> float:
        """
        Compute adaptive threshold based on task state.

        - Early in task: Higher threshold (keep more context)
        - Near completion: Lower threshold (compress aggressively)
        - After errors: Higher threshold (preserve debug info)
        - Loop detected: Lower threshold (break the pattern)
        """
        base = self.base_threshold

        # Progress adjustment: compress more as task progresses
        progress_adj = -0.1 * self.task_progress

        # Error adjustment: preserve more after errors
        error_adj = 0.15 * min(self.error_rate, 1.0)

        # Loop adjustment: compress aggressively to break loops
        loop_adj = -0.2 if self.loop_detection else 0.0

        return max(0.3, min(0.9, base + progress_adj + error_adj + loop_adj))

    def update(
        self,
        task_progress: float | None = None,
        error_occurred: bool = False,
        loop_detected: bool = False,
    ) -> AdaptiveThreshold:
        """Update threshold parameters."""
        new_error_rate = (
            self.error_rate * 0.9 + (0.1 if error_occurred else 0.0)
        )
        return AdaptiveThreshold(
            base_threshold=self.base_threshold,
            task_progress=task_progress or self.task_progress,
            error_rate=new_error_rate,
            loop_detection=loop_detected,
        )
```

### 2.4 Dual-Lane Pheromone Architecture (Refined)

```python
from abc import ABC, abstractmethod
from enum import Enum


class PheromoneChannel(Enum):
    """
    Dual-lane architecture for pheromone communication.

    Key insight: Different signals have different persistence requirements.
    This is a FUNCTOR DECOMPOSITION:

        Pheromone = FastPheromone × SlowPheromone

    Where × is categorical product (independent channels).
    """
    FAST = "fast"  # Logs, high frequency, ephemeral
    SLOW = "slow"  # CRDs, low frequency, persistent


@dataclass
class Pulse:
    """
    Fast-lane vitality signal.

    Emitted via structured logging (NOT K8s resources).
    Zero etcd overhead.

    AGENTESE: time.trace.pulse
    """
    agent: str
    pressure: float
    phase: str
    checkpoint: str | None
    timestamp: datetime
    content_hash: str  # For loop detection

    def to_log(self) -> str:
        """Serialize to structured log format."""
        return (
            f"PULSE|agent={self.agent}"
            f"|pressure={self.pressure:.2f}"
            f"|phase={self.phase}"
            f"|checkpoint={self.checkpoint or 'none'}"
            f"|hash={self.content_hash[:8]}"
            f"|t={self.timestamp.isoformat()}"
        )

    @classmethod
    def from_log(cls, line: str) -> Pulse | None:
        """Parse from structured log line."""
        if not line.startswith("PULSE|"):
            return None
        parts = dict(p.split("=", 1) for p in line[6:].split("|"))
        return cls(
            agent=parts["agent"],
            pressure=float(parts["pressure"]),
            phase=parts["phase"],
            checkpoint=parts["checkpoint"] if parts["checkpoint"] != "none" else None,
            timestamp=datetime.fromisoformat(parts["t"]),
            content_hash=parts["hash"],
        )


class FastChannel:
    """
    Fast-lane pheromone channel via structured logging.

    Pattern detection without K8s overhead:
    - Regular intervals → Healthy
    - Erratic intervals → Degraded
    - Repeated hashes → Stuck
    - Rising pressure → Compress needed
    """

    def __init__(self, log_query: LogQueryService):
        self.log_query = log_query

    async def sense_vitality(self, agent: str) -> VitalityStatus:
        """
        Zero-context vitality sensing.

        AGENTESE: self.vitality.sense
        """
        pulses = await self.log_query.query(
            f'{{agent="{agent}"}} |= "PULSE|"',
            since=timedelta(minutes=5),
        )

        if not pulses:
            return VitalityStatus(health=Health.SILENT)

        parsed = [Pulse.from_log(p) for p in pulses]
        parsed = [p for p in parsed if p is not None]

        return self._analyze_pattern(parsed)

    def _analyze_pattern(self, pulses: list[Pulse]) -> VitalityStatus:
        """Derive health from pulse patterns."""
        intervals = self._compute_intervals(pulses)
        hashes = [p.content_hash for p in pulses]
        pressures = [p.pressure for p in pulses]

        # Check for stuck (repeated hashes)
        if len(set(hashes[-5:])) == 1 and len(hashes) >= 5:
            return VitalityStatus(
                health=Health.STUCK,
                pattern="Repeated content hash",
                recommendation="Branch to break loop",
            )

        # Check for erratic intervals
        if len(intervals) >= 3:
            std = statistics.stdev(intervals)
            mean = statistics.mean(intervals)
            cv = std / mean if mean > 0 else float('inf')
            if cv > 0.5:
                return VitalityStatus(
                    health=Health.ERRATIC,
                    pattern=f"Interval CV={cv:.2f}",
                    recommendation="Monitor closely",
                )

        # Check for pressure trend
        if len(pressures) >= 3:
            trend = self._linear_trend(pressures)
            if trend > 0.05:  # Rising
                return VitalityStatus(
                    health=Health.PRESSURE_RISING,
                    pressure=pressures[-1],
                    pattern=f"Pressure trend={trend:.3f}",
                    recommendation="Proactive compression",
                )

        return VitalityStatus(
            health=Health.HEALTHY,
            pressure=pressures[-1] if pressures else 0.0,
        )


class SlowChannel:
    """
    Slow-lane pheromone channel via K8s CRDs.

    For infrequent, persistent signals:
    - BRANCH_REQUEST
    - CRYSTALLIZE_REQUEST
    - COMPRESS_REQUEST
    - STATE_CHANGE
    """

    def __init__(self, k8s_client: KubernetesClient):
        self.k8s = k8s_client

    async def emit(self, pheromone: SlowPheromone) -> None:
        """
        Emit slow-lane pheromone.

        Rate limited by nature (K8s operations are expensive).
        """
        await self.k8s.create_namespaced_custom_object(
            group="kgents.io",
            version="v1",
            namespace=pheromone.namespace,
            plural="pheromones",
            body=pheromone.to_manifest(),
        )

    async def sense(self, agent: str) -> list[SlowPheromone]:
        """
        Sense pending slow-lane pheromones for an agent.

        AGENTESE: world.pheromone.sense
        """
        result = await self.k8s.list_namespaced_custom_object(
            group="kgents.io",
            version="v1",
            namespace=agent,
            plural="pheromones",
            label_selector=f"target={agent},acknowledged!=true",
        )
        return [SlowPheromone.from_manifest(item) for item in result['items']]
```

### 2.5 State Crystallization (Enhanced)

```python
@dataclass
class StateCrystal:
    """
    Checkpoint with linearity-aware compression.

    AGENTESE: self.memory.crystallize

    Key improvements over v2.0:
    - Explicit linearity markers for focus fragments
    - Differential compression via incremental summary
    - Comonadic structure (parent_crystal enables duplicate())
    """

    crystal_id: str
    agent: str
    timestamp: datetime

    # Core state (LINEAR: must be preserved)
    task_state: TaskState
    working_memory: dict[str, Any]

    # Compressed history (AFFINE observations masked)
    history_summary: str
    summary_tokens: int

    # Focus fragments (RELEVANT: verbatim preservation)
    focus_fragments: list[FocusFragment]
    focus_tokens: int

    # Linearity map for reconstruction
    linearity_map: LinearityMap

    # Comonadic structure
    parent_crystal: str | None    # For duplicate() chain
    branch_reason: str | None
    branch_depth: int = 0

    # Accursed Share lifecycle
    ttl: timedelta = timedelta(hours=24)
    pinned: bool = False

    def is_expired(self) -> bool:
        """Check if crystal should be composted."""
        if self.pinned:
            return False
        return datetime.now() - self.timestamp > self.ttl

    def total_tokens(self) -> int:
        """Total token cost of crystal."""
        return self.summary_tokens + self.focus_tokens

    def to_context(self) -> ContextWindow:
        """
        Reconstruct ContextWindow from crystal.

        AGENTESE: self.memory.resume
        """
        # Reconstruct history from summary + focus
        history = self._reconstruct_history()

        return ContextWindow(
            history=tuple(history),
            focus=history[-1] if history else Turn.empty(),
            metadata=ContextMeta(
                pressure=len(history) / MAX_HISTORY,
                linearity=self.linearity_map,
                branch_depth=self.branch_depth,
                entropy_consumed=self.branch_depth * 0.1,
            ),
        )


@dataclass
class FocusFragment:
    """
    A preserved fragment with RELEVANT linearity.

    Focus fragments survive compression verbatim.
    """

    hint: str                   # What triggered preservation
    content: str                # Verbatim content
    position: int               # Original position in history
    linearity: Linearity = Linearity.RELEVANT


class CrystallizationEngine:
    """
    Creates State Crystals with linearity-aware compression.

    AGENTESE: self.memory.crystallize
    """

    async def crystallize(
        self,
        context: ContextWindow,
        focus_hints: list[str] | None = None,
        ttl: timedelta = timedelta(hours=24),
    ) -> StateCrystal:
        """
        Create a crystal from current context.

        Process:
        1. Mark linearity classes based on focus hints
        2. Extract RELEVANT fragments verbatim
        3. Compress AFFINE+LINEAR via observation masking + summary
        4. Store with comonadic metadata
        """
        # Build linearity map
        linearity_map = self._build_linearity_map(context, focus_hints or [])

        # Extract focus fragments (RELEVANT)
        focus_fragments = self._extract_focus(context, linearity_map)

        # Compress remaining (AFFINE + LINEAR)
        history_summary = await self._compress_with_linearity(
            context, linearity_map, focus_fragments
        )

        crystal = StateCrystal(
            crystal_id=f"crystal-{uuid4().hex[:8]}",
            agent=context.metadata.agent_name,
            timestamp=datetime.now(),
            task_state=self._extract_task_state(context),
            working_memory=self._extract_working_memory(context),
            history_summary=history_summary,
            summary_tokens=self._count_tokens(history_summary),
            focus_fragments=focus_fragments,
            focus_tokens=sum(self._count_tokens(f.content) for f in focus_fragments),
            linearity_map=linearity_map,
            parent_crystal=context.metadata.parent_crystal,
            branch_depth=context.metadata.branch_depth,
            ttl=ttl,
        )

        # Persist via D-gent
        await self.d_gent.save_crystal(crystal)

        # Emit slow pheromone for observability
        await self.slow_channel.emit(SlowPheromone(
            type=PheromoneType.CRYSTAL_CREATED,
            source=crystal.agent,
            payload={
                "crystal_id": crystal.crystal_id,
                "tokens": crystal.total_tokens(),
                "focus_count": len(crystal.focus_fragments),
            },
        ))

        return crystal

    def _build_linearity_map(
        self,
        context: ContextWindow,
        focus_hints: list[str],
    ) -> LinearityMap:
        """
        Build linearity map based on content analysis.

        Default:
        - Observations: AFFINE
        - Reasoning: LINEAR
        - Matching focus hints: RELEVANT
        """
        regions = []

        for i, turn in enumerate(context.history):
            # Check for focus hint matches
            is_focus = any(
                hint.lower() in turn.content.lower() or
                f"[FOCUS:{hint}]" in turn.content
                for hint in focus_hints
            )

            if is_focus:
                regions.append((range(i, i+1), Linearity.RELEVANT))
            elif turn.is_observation:
                regions.append((range(i, i+1), Linearity.AFFINE))
            else:
                regions.append((range(i, i+1), Linearity.LINEAR))

        return LinearityMap(regions=regions)
```

---

## Part III: Implementation Roadmap

### Phase 0: Comonadic Foundation

| # | Task | Files | Deliverable |
|---|------|-------|-------------|
| 0.1 | `ContextWindow` comonad | `agents/d/context_comonad.py` | extract/extend/duplicate |
| 0.2 | Comonad law tests | `agents/d/_tests/test_comonad_laws.py` | Property-based verification |
| 0.3 | `LinearityMap` | `agents/d/linearity.py` | Affine/Linear/Relevant markers |
| 0.4 | Bootstrap integration | `bootstrap/umwelt.py` | Umwelt carries ContextWindow |

**Success Criterion**: `verify_left_identity`, `verify_right_identity`, `verify_associativity` pass.

### Phase 1: Linearity-Aware Compression

| # | Task | Files | Deliverable |
|---|------|-------|-------------|
| 1.1 | `LinearityAwareCompressor` | `agents/d/compression.py` | Linearity-respecting compression |
| 1.2 | Observation masking | `agents/d/compression.py` | JetBrains pattern |
| 1.3 | Incremental summarization | `agents/r/incremental.py` | Differential summary updates |
| 1.4 | Adaptive thresholds | `agents/d/adaptive.py` | ACON-style dynamics |

**Success Criterion**: RELEVANT fragments survive compression verbatim; AFFINE dropped first.

### Phase 2: Dual-Lane Pheromones

| # | Task | Files | Deliverable |
|---|------|-------|-------------|
| 2.1 | `Pulse` dataclass | `agents/o/pulse.py` | Structured log format |
| 2.2 | `FastChannel` | `infra/cortex/fast_channel.py` | Log-based vitality sensing |
| 2.3 | `SlowChannel` | `infra/cortex/slow_channel.py` | CRD-based signals |
| 2.4 | Pattern analysis | `infra/cortex/vitality.py` | Health derivation from pulses |

**Success Criterion**: `self.vitality.sense` returns health with 0 LLM calls and 0 etcd writes.

### Phase 3: Crystallization & Compost

| # | Task | Files | Deliverable |
|---|------|-------|-------------|
| 3.1 | `StateCrystal` | `agents/d/crystal.py` | Enhanced crystal format |
| 3.2 | `CrystallizationEngine` | `agents/d/crystallize.py` | Focus-aware crystallization |
| 3.3 | `CrystalReaper` | `agents/d/reaper.py` | TTL-based composting |
| 3.4 | `EntropyBudget` | `agents/d/entropy.py` | Branching budget from slop |

**Success Criterion**: Crystals <10KB; unpinned crystals compost after TTL.

### Phase 4: Controller Integration

| # | Task | Files | Deliverable |
|---|------|-------|-------------|
| 4.1 | `LatentActionController` | `infra/cortex/latent.py` | Request emission |
| 4.2 | Agent loop integration | `agents/*/loop.py` | Pheromone sensing in loop |
| 4.3 | `KTerrariumController` | `infra/cortex/controller.py` | Full monitoring loop |
| 4.4 | Y-gent branching | `agents/y/topology.py` | Crystal-based duplicate() |

**Success Criterion**: End-to-end context sovereignty operational.

### Phase 5: Verification & Observability

| # | Task | Files | Deliverable |
|---|------|-------|-------------|
| 5.1 | Comonad law property tests | `agents/d/_tests/` | Hypothesis-based testing |
| 5.2 | Linearity constraint tests | `agents/d/_tests/` | Verify RELEVANT preservation |
| 5.3 | Terrarium TUI | `agents/i/terrarium_tui.py` | Vitality + crystal viz |
| 5.4 | CLI commands | `protocols/cli/handlers/` | `kgents crystal *` |

**Success Criterion**: All algebraic laws verified; TUI shows context health.

---

## Part IV: AGENTESE Path Registry

| AGENTESE Path | Operation | Category | Location |
|---------------|-----------|----------|----------|
| `self.stream.focus` | Get current context | Comonad extract | Agent |
| `self.stream.map` | Context-aware transform | Comonad extend | Agent |
| `self.stream.compress` | Linearity-aware compression | Linear → Affine | Agent |
| `self.memory.crystallize` | Create checkpoint | Comonad + Linear | Agent |
| `self.memory.resume` | Restore from checkpoint | Crystal → Context | Agent |
| `self.memory.cherish` | Pin from reaping | Affine → Linear | Agent |
| `self.vitality.sense` | Zero-context health | Derived path | Controller |
| `void.entropy.sip` | Branch (duplicate) | Comonad duplicate | Agent |
| `void.entropy.pour` | Compost crystals | Affine consumption | Reaper |
| `time.trace.pulse` | Fast-lane heartbeat | Log emission | Agent |
| `world.pheromone.sense` | Slow-lane sensing | CRD query | Agent |

---

## Part V: Success Criteria

### Quantitative

| Metric | Current | Target |
|--------|---------|--------|
| Health check token cost | ~100 tokens | 0 tokens |
| Branch operation cost | Full context | <100 tokens (summary + focus) |
| Crystal size | N/A | <10KB |
| etcd writes per agent per minute | N/A | <0.1 (slow lane only) |
| Compression threshold | 95% (reactive) | Adaptive (30-90%) |
| RELEVANT fragment preservation | N/A | 100% |
| Comonad law compliance | N/A | 100% |

### Qualitative

- [ ] Controller never invokes LLM directly
- [ ] Fast-lane uses logging, not K8s
- [ ] Slow-lane rate-limited by nature
- [ ] Focus fragments (RELEVANT) preserved verbatim
- [ ] Observations (AFFINE) masked before LINEAR summarized
- [ ] Crystals auto-compost unless cherished
- [ ] Branching respects entropy budget
- [ ] Comonad laws verified at runtime

---

## Part VI: Theoretical References

### Category Theory

- [Contextads as Wreaths in Category Theory](https://www.emergentmind.com/papers/2410.21889) (2024) - Unifies comonads and contextful computation
- [Categories for the lazy functional programmer](https://people.cs.nott.ac.uk/psztxa/mgs.2025/) - MGS 2025 course on comonads
- [Comonad: Context-Sensitive Computation](https://softwarepatternslexicon.com/functional/advanced-patterns/functional-abstractions/comonad/) - Practical comonad patterns

### Linear Types & Resource Management

- [From Linearity to Borrowing](https://dl.acm.org/doi/abs/10.1145/3764117) (2025) - Rust-style borrowing from linear types
- [Substructural Type Systems](https://en.wikipedia.org/wiki/Substructural_type_system) - Affine/Linear/Relevant overview
- [Mastering Linear Types](https://www.numberanalytics.com/blog/mastering-linear-types-type-theory) - Practical applications

### Incremental Computation

- [Incremental Computing by Differential Execution](https://drops.dagstuhl.de/storage/00lipics/lipics-vol333-ecoop2025/LIPIcs.ECOOP.2025.20/LIPIcs.ECOOP.2025.20.pdf) (ECOOP 2025) - Formal differential semantics
- [Self-Adjusting Computation](https://www.umut-acar.org/self-adjusting-computation) - Umut Acar's foundational work
- [Jane Street Incremental](https://github.com/janestreet/incremental) - Production incremental library

### LLM Context Management

- [JetBrains Research: Efficient Context Management](https://blog.jetbrains.com/research/2025/12/efficient-context-management/) - Observation masking study
- [ACON: Adaptive Context Compression](https://arxiv.org/html/2510.00615v1) - Adaptive thresholds
- [Task Memory Engine](https://arxiv.org/html/2504.08525v1) - Branching snapshots
- [Context Engineering for Agents](https://rlancemartin.github.io/2025/06/23/context_engineering/) - LangChain patterns
- [Memory Blocks](https://www.letta.com/blog/memory-blocks) - Letta's memory architecture

---

## Part VII: Principle Alignment (Final)

| Principle | Manifestation | Categorical Basis |
|-----------|---------------|-------------------|
| **Tasteful** | Dual-lane split | Functor decomposition |
| **Curated** | Composting, linearity | Affine type consumption |
| **Ethical** | Focus preservation | Relevant constraint |
| **Joy-Inducing** | Gratitude pheromones | Void context |
| **Composable** | Comonadic structure | extend/duplicate |
| **Heterarchical** | Shared medium | Local comonadic computation |
| **Generative** | Derived from Five Contexts | Free construction |
| **Accursed Share** | Entropy budget, TTL | Affine typing |
| **AGENTESE** | Path registry | Yoneda embedding |
| **Graceful Degradation** | Crystals enable recovery | Checkpoint = morphism |
| **Transparent Infrastructure** | Pulse logs, crystal lifecycle | Observable functors |

---

*"The sovereign agent knows its own limits. Context is not a cage—it is a comonad."*
