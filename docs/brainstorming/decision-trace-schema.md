# DecisionTrace Schema: The Anatomy of Justified Action

> *"Every decision leaves a trace. The trace is the proof."*

**Status:** Design Draft
**Date:** 2025-12-21
**Companion:** `decision-quality-proofs.md`
**Heritage:** D-gent (persistence), M-gent (memory), CSA (stigmergy)

---

## Design Principles

Before the schema, the principles that shape it:

### 1. Traces Are Immutable, Annotations Are Additive

A decision, once made, cannot be unmade. The trace records what happened. But our *understanding* of the decision evolves:

```
DecisionTrace (immutable)     Annotations (append-only)
─────────────────────────     ─────────────────────────
Created at T₀                 Outcome observed at T₁
                              Regret assessed at T₂
                              Rebuttal encountered at T₃
                              Proof defeated at T₄
                              Learning extracted at T₅
```

### 2. Granularity Is Fractal

Decisions nest. A session contains many decisions. A decision contains many micro-choices:

```
Session
 └── Decision: "Refactor DI container"
      ├── Choice: "Use signature semantics"
      ├── Choice: "Singleton by default"
      └── Choice: "Explicit registration over autodiscovery"
          └── Micro: "Name it 'get_foo' not 'create_foo'"
```

We capture at multiple granularities, with explicit parent-child relationships.

### 3. Resources Are Observable, Attention Is Felt

Some resources can be measured:
- **Time**: Clock duration
- **Compute**: Token count, API calls
- **Money**: Direct costs

But attention is phenomenological—it must be *reported*, not measured:

```python
class AttentionLevel(Enum):
    """Kent's subjective sense of how much focus this required."""
    AMBIENT = "ambient"       # Background, habitual
    FOCUSED = "focused"       # Deliberate attention
    DEEP = "deep"            # Flow state, significant investment
    PEAK = "peak"            # Maximum concentration, exhausting
```

### 4. Values Are Explicit AND Latent

Some values are stated (CLAUDE.md). Some emerge from patterns. The schema must accommodate both:

```python
@dataclass
class ValueReference:
    source: Literal["stated", "latent", "aesthetic"]
    name: str
    evidence: str | None = None  # For latent values: what pattern revealed this?
```

---

## The Core Schema

```python
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal, NewType

# =============================================================================
# Identity Types
# =============================================================================

TraceId = NewType("TraceId", str)
SessionId = NewType("SessionId", str)
PrincipleId = NewType("PrincipleId", str)
PatternId = NewType("PatternId", str)


def new_trace_id() -> TraceId:
    """Generate a new trace ID with timestamp prefix for sortability."""
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    short_uuid = uuid.uuid4().hex[:8]
    return TraceId(f"trace-{ts}-{short_uuid}")


# =============================================================================
# Enums and Simple Types
# =============================================================================


class DecisionGranularity(Enum):
    """The scale of the decision."""
    SESSION = "session"           # An entire work session
    DECISION = "decision"         # A discrete, nameable choice
    CHOICE = "choice"             # A sub-decision within a decision
    MICRO = "micro"               # A tiny choice (naming, ordering, etc.)


class AttentionLevel(Enum):
    """Subjective attention cost."""
    AMBIENT = "ambient"           # 0.1 - Background, habitual
    FOCUSED = "focused"           # 0.4 - Deliberate attention
    DEEP = "deep"                 # 0.7 - Flow state, significant
    PEAK = "peak"                 # 1.0 - Maximum, exhausting

    @property
    def weight(self) -> float:
        return {"ambient": 0.1, "focused": 0.4, "deep": 0.7, "peak": 1.0}[self.value]


class DecisionSource(Enum):
    """Where the decision originated."""
    CONSCIOUS = "conscious"       # Deliberate, reflected-upon choice
    INTUITIVE = "intuitive"       # Felt right, not fully articulated
    HABITUAL = "habitual"         # Pattern-following, automatic
    DELEGATED = "delegated"       # Claude or another agent decided
    EMERGENT = "emergent"         # Arose from interaction, no single author


class ProofStatus(Enum):
    """Current status of the decision's justification."""
    PENDING = "pending"           # Outcome not yet observed
    PROVISIONAL = "provisional"   # Tentatively justified
    PROVEN = "proven"             # Justified with confidence
    CHALLENGED = "challenged"     # Rebuttal encountered
    DEFEATED = "defeated"         # Proof overturned
    ARCHIVED = "archived"         # Old, no longer actively assessed


# =============================================================================
# Resource Tracking
# =============================================================================


@dataclass(frozen=True)
class ResourceExpenditure:
    """
    What was spent on this decision.

    All fields are optional because not all decisions have all costs.
    """
    # Time
    duration_minutes: float | None = None
    wall_clock_start: datetime | None = None
    wall_clock_end: datetime | None = None

    # Compute
    tokens_input: int | None = None
    tokens_output: int | None = None
    api_calls: int | None = None
    model_used: str | None = None

    # Money
    direct_cost_usd: float | None = None
    estimated_cost_usd: float | None = None

    # Attention (phenomenological)
    attention_level: AttentionLevel = AttentionLevel.FOCUSED
    energy_before: float | None = None   # 0.0 - 1.0, self-reported
    energy_after: float | None = None

    # Opportunity cost (what else could have been done)
    alternatives_foregone: tuple[str, ...] = ()

    @property
    def total_tokens(self) -> int:
        return (self.tokens_input or 0) + (self.tokens_output or 0)

    @property
    def attention_weighted_minutes(self) -> float:
        """Time weighted by attention intensity."""
        if self.duration_minutes is None:
            return 0.0
        return self.duration_minutes * self.attention_level.weight


# =============================================================================
# Value Alignment
# =============================================================================


@dataclass(frozen=True)
class ValueReference:
    """A reference to a value or principle."""
    source: Literal["stated", "latent", "aesthetic"]
    name: str
    location: str | None = None   # e.g., "CLAUDE.md:42" or "git:abc123"
    evidence: str | None = None   # For latent: what revealed this?


@dataclass(frozen=True)
class PrincipleAlignment:
    """How this decision relates to a principle."""
    principle: ValueReference
    relationship: Literal["honors", "violates", "neutral", "extends"]
    explanation: str | None = None
    confidence: float = 1.0       # How sure are we of this alignment?


@dataclass(frozen=True)
class AestheticAssessment:
    """
    Hardy's three aesthetic qualities, plus the Mirror Test.

    From Hardy's "A Mathematician's Apology" (1940):
    - Inevitability: "It couldn't have been otherwise"
    - Unexpectedness: "Surprising yet fitting"
    - Economy: "No wasted motion"

    The Mirror Test is Kent's addition:
    - "Does this feel like me on my best day?"
    """
    inevitability: bool | None = None
    unexpectedness: bool | None = None
    economy: bool | None = None
    mirror_test: bool | None = None

    # Freeform aesthetic notes
    notes: str | None = None

    @property
    def hardy_score(self) -> float:
        """Score from 0-1 based on Hardy's criteria."""
        criteria = [self.inevitability, self.unexpectedness, self.economy]
        assessed = [c for c in criteria if c is not None]
        if not assessed:
            return 0.5  # Unknown
        return sum(1 for c in assessed if c) / len(assessed)

    @property
    def beautiful(self) -> bool | None:
        """Is this beautiful? Requires inevitability + (unexpectedness OR economy)."""
        if self.inevitability is None:
            return None
        if not self.inevitability:
            return False
        if self.unexpectedness or self.economy:
            return True
        return False


# =============================================================================
# Alternatives and Counterfactuals
# =============================================================================


@dataclass(frozen=True)
class Alternative:
    """A path not taken."""
    description: str
    rejected_because: str
    estimated_cost: ResourceExpenditure | None = None
    estimated_value: str | None = None
    regret_if_chosen: float | None = None  # Retrospective: would this have been better?


# =============================================================================
# Outcomes and Evidence
# =============================================================================


@dataclass
class Outcome:
    """
    An observed outcome of a decision.

    Outcomes are mutable because they're discovered over time.
    """
    observed_at: datetime
    description: str

    # Quantitative
    value_created: float | None = None    # In some unit (usage, dollars, etc.)
    cost_incurred: float | None = None

    # Qualitative
    category: Literal["success", "failure", "neutral", "mixed", "unknown"] = "unknown"
    downstream_effects: list[str] = field(default_factory=list)

    # Evidence
    evidence_type: Literal["metric", "feedback", "observation", "inference"] = "observation"
    evidence_source: str | None = None    # Where did we learn this?


@dataclass
class Rebuttal:
    """
    A challenge to the decision's justification.

    From Toulmin: conditions under which the claim would not hold.
    """
    encountered_at: datetime
    description: str
    source: Literal["outcome", "principle", "pattern", "external", "reflection"]

    # Resolution
    resolved: bool = False
    resolution: str | None = None
    defeats_proof: bool = False


# =============================================================================
# The Proof Itself
# =============================================================================


@dataclass
class Warrant:
    """
    The reasoning that connects evidence to claim.

    From Toulmin: "Since [warrant], given [data], therefore [claim]."
    """
    statement: str                        # The warrant itself
    backing: tuple[str, ...] = ()         # What supports the warrant
    qualifiers: tuple[str, ...] = ()      # Conditions/limitations


@dataclass
class Proof:
    """
    The justification for a decision.

    This is Toulmin structure + defeasibility machinery.
    """
    # Toulmin structure
    claim: str                            # "This decision was justified"
    data: tuple[str, ...] = ()            # Facts that support the claim
    warrant: Warrant | None = None        # Reasoning connecting data to claim

    # Assessment
    status: ProofStatus = ProofStatus.PENDING
    confidence: float = 0.5               # 0.0 - 1.0
    last_assessed: datetime | None = None

    # Defeasibility
    rebuttals: list[Rebuttal] = field(default_factory=list)
    undercutters: list[str] = field(default_factory=list)  # Attacks on the warrant

    # Generated narrative (for humans)
    narrative: str | None = None


# =============================================================================
# Learning from Defeat
# =============================================================================


@dataclass
class DifferentialDenial:
    """
    When a proof is defeated, we extract a learning.

    This is the mechanism for "prevent bad decisions from happening again."
    """
    created_at: datetime
    original_trace_id: TraceId
    defeating_evidence: str

    # The learning
    anti_pattern: str                     # "Don't do X when Y"
    conditions_to_watch: tuple[str, ...]  # Signals that this pattern is emerging
    heuristic_update: str                 # How to decide differently

    # Stigmergic encoding
    pheromone_strength: float = -1.0      # Negative = anti-pheromone
    decay_rate_per_day: float = 0.05      # How fast to forget

    # Scope
    applies_to: Literal["all", "similar", "exact"] = "similar"
    similarity_threshold: float = 0.7


# =============================================================================
# The Complete Trace
# =============================================================================


@dataclass
class DecisionTrace:
    """
    The complete record of a decision.

    This is the atom of the Decision Quality Proof System.
    """

    # =========================================================================
    # Identity
    # =========================================================================

    id: TraceId
    created_at: datetime
    session_id: SessionId | None = None

    # Hierarchy
    granularity: DecisionGranularity = DecisionGranularity.DECISION
    parent_id: TraceId | None = None      # For nested decisions
    children_ids: list[TraceId] = field(default_factory=list)

    # =========================================================================
    # The Decision Itself
    # =========================================================================

    what: str                             # What was decided
    why: str | None = None                # Why (if known at decision time)
    how: str | None = None                # How it was implemented

    source: DecisionSource = DecisionSource.CONSCIOUS

    # Context at decision time
    context: dict[str, Any] = field(default_factory=dict)

    # Alternatives considered
    alternatives: list[Alternative] = field(default_factory=list)

    # =========================================================================
    # Resources
    # =========================================================================

    resources: ResourceExpenditure = field(default_factory=ResourceExpenditure)

    # =========================================================================
    # Value Alignment
    # =========================================================================

    principle_alignments: list[PrincipleAlignment] = field(default_factory=list)
    aesthetic: AestheticAssessment = field(default_factory=AestheticAssessment)

    # =========================================================================
    # Outcomes (populated over time)
    # =========================================================================

    outcomes: list[Outcome] = field(default_factory=list)

    # Regret assessment (retrospective)
    regret: float | None = None           # 0.0 = no regret, 1.0 = total regret
    regret_assessed_at: datetime | None = None

    # =========================================================================
    # The Proof
    # =========================================================================

    proof: Proof = field(default_factory=Proof)

    # If defeated, the learning extracted
    denial: DifferentialDenial | None = None

    # =========================================================================
    # Stigmergic Encoding
    # =========================================================================

    # Pattern this decision exemplifies (for reinforcement)
    patterns: list[PatternId] = field(default_factory=list)

    # Pheromone contribution (positive or negative)
    pheromone_delta: float = 0.0

    # =========================================================================
    # Metadata
    # =========================================================================

    tags: list[str] = field(default_factory=list)

    # Authorship
    authors: list[str] = field(default_factory=list)  # ["kent", "claude-opus-4"]

    # Git correlation
    git_commits: list[str] = field(default_factory=list)
    git_branch: str | None = None

    # =========================================================================
    # Computed Properties
    # =========================================================================

    @property
    def is_proven(self) -> bool:
        return self.proof.status == ProofStatus.PROVEN

    @property
    def is_defeated(self) -> bool:
        return self.proof.status == ProofStatus.DEFEATED

    @property
    def net_value(self) -> float | None:
        """Value created minus costs, if measurable."""
        value = sum(o.value_created or 0 for o in self.outcomes)
        cost = sum(o.cost_incurred or 0 for o in self.outcomes)
        cost += self.resources.direct_cost_usd or 0
        if value == 0 and cost == 0:
            return None
        return value - cost

    @property
    def principles_honored(self) -> list[str]:
        return [
            pa.principle.name
            for pa in self.principle_alignments
            if pa.relationship == "honors"
        ]

    @property
    def principles_violated(self) -> list[str]:
        return [
            pa.principle.name
            for pa in self.principle_alignments
            if pa.relationship == "violates"
        ]


# =============================================================================
# Factories
# =============================================================================


def create_decision_trace(
    what: str,
    *,
    why: str | None = None,
    session_id: SessionId | None = None,
    granularity: DecisionGranularity = DecisionGranularity.DECISION,
    source: DecisionSource = DecisionSource.CONSCIOUS,
    attention: AttentionLevel = AttentionLevel.FOCUSED,
    authors: list[str] | None = None,
) -> DecisionTrace:
    """
    Factory for creating a new decision trace.

    Usage:
        trace = create_decision_trace(
            what="Refactored DI container",
            why="Enable Crown Jewel pattern",
            attention=AttentionLevel.DEEP,
            authors=["kent", "claude-opus-4"],
        )
    """
    return DecisionTrace(
        id=new_trace_id(),
        created_at=datetime.utcnow(),
        session_id=session_id,
        granularity=granularity,
        what=what,
        why=why,
        source=source,
        resources=ResourceExpenditure(
            wall_clock_start=datetime.utcnow(),
            attention_level=attention,
        ),
        authors=authors or [],
    )


def complete_decision_trace(
    trace: DecisionTrace,
    *,
    duration_minutes: float | None = None,
    tokens: int | None = None,
    cost_usd: float | None = None,
) -> DecisionTrace:
    """
    Mark a decision trace as complete, filling in resource data.

    Returns a new trace (traces are conceptually immutable after creation,
    though we mutate for convenience).
    """
    now = datetime.utcnow()

    # Calculate duration if not provided
    if duration_minutes is None and trace.resources.wall_clock_start:
        delta = now - trace.resources.wall_clock_start
        duration_minutes = delta.total_seconds() / 60

    # Update resources
    trace.resources = ResourceExpenditure(
        duration_minutes=duration_minutes,
        wall_clock_start=trace.resources.wall_clock_start,
        wall_clock_end=now,
        tokens_input=tokens,
        tokens_output=tokens,  # Approximate
        direct_cost_usd=cost_usd,
        attention_level=trace.resources.attention_level,
        energy_before=trace.resources.energy_before,
        energy_after=trace.resources.energy_after,
    )

    return trace
```

---

## Open Questions & Explorations

### 1. The Granularity Problem

**Question:** At what level do we capture decisions?

Every keystroke is technically a decision. But that's absurd. Conversely, only capturing "session-level" decisions loses the micro-choices that compound.

**Current Thinking:** Three practical levels:

| Level | Trigger | Example |
|-------|---------|---------|
| **Session** | Manual: start/end of work | "2-hour morning session on DI" |
| **Decision** | Significant choice point | "Use signature semantics for DI" |
| **Choice** | Sub-decision within decision | "Name it 'get_foo' not 'create_foo'" |

Micro-level is captured implicitly via git diffs, not explicit traces.

**Open:** Should there be automatic detection of decision points? LLM analysis of conversation to identify choice moments?

---

### 2. Implicit vs. Explicit Decisions

**Question:** What about decisions Kent didn't consciously make?

Many choices are habitual, intuitive, or emergent from dialogue. The `DecisionSource` enum attempts to capture this:

```python
class DecisionSource(Enum):
    CONSCIOUS = "conscious"       # "I decided to..."
    INTUITIVE = "intuitive"       # "It felt right to..."
    HABITUAL = "habitual"         # "I always do it this way"
    DELEGATED = "delegated"       # "Claude suggested and I accepted"
    EMERGENT = "emergent"         # "It emerged from our conversation"
```

**Open:** How do we capture decisions Kent didn't realize he was making? Post-hoc analysis of git history? Session review?

---

### 3. The Authorship Problem

**Question:** Who made the decision—Kent or Claude?

In collaborative sessions, decisions often emerge from dialogue. Neither party "decided" alone.

**Current Thinking:** `authors: list[str]` captures all contributors, but doesn't capture the *nature* of contribution:

```python
# Future refinement?
@dataclass
class Authorship:
    agent: str  # "kent", "claude-opus-4"
    role: Literal["initiator", "refiner", "executor", "approver"]
    contribution: str  # What specifically
```

**Open:** Does it matter? Maybe "we decided together" is the right framing.

---

### 4. Attention Measurement

**Question:** How do we measure attention cost?

Attention is phenomenological—it can only be *reported*, not measured. But Kent won't want to constantly rate his attention level.

**Possible Approaches:**

1. **Infer from engagement patterns** — Long pauses = deep thought? Fast responses = flow?
2. **Session-level default** — "This was a deep work session"
3. **Rare explicit marking** — Only mark when exceptional
4. **Energy proxy** — Track energy before/after session

**Open:** Is there a non-intrusive way to capture this? Or should we accept that it's approximate?

---

### 5. Value Drift

**Question:** What happens when principles change?

Kent's values evolve. A decision that honored principles in December might violate principles in March.

**Options:**

1. **Freeze at decision time** — The decision honored *then-current* principles
2. **Re-evaluate continuously** — Proofs can be defeated by value changes
3. **Version principles** — `principles_v3.md` enables temporal comparison

**Current Thinking:** Option 2 is most honest. Values drift, and old decisions can become misaligned. But this risks constant churn.

**Proposed Mechanism:** Value changes trigger *review* of affected proofs, not automatic defeat.

```python
@dataclass
class ValueChange:
    """Record when a principle changes."""
    timestamp: datetime
    principle: str
    old_value: str
    new_value: str
    affected_traces: list[TraceId]  # Traces that should be reviewed
```

---

### 6. Proof Composition

**Question:** If decisions A and B are proven, is the composition A∘B proven?

Intuition says yes: if refactoring DI was good, and using DI for Brain was good, then the sequence was good.

But there are failure modes:
- **Sunk cost fallacy** — B only looks good because A was already done
- **Path dependency** — B wouldn't have been chosen without A; was A really justified?
- **Interference** — A and B are individually fine but create emergent problems

**Proposed:** Composition is *not* automatic. Sequences of decisions form a new decision ("the DI journey") that needs its own proof.

---

### 7. Integration with Existing Systems

**Question:** How does this connect to kgents infrastructure?

| System | Integration |
|--------|-------------|
| **D-gent** | DecisionTrace is a D-gent domain; persistence via StorageProvider |
| **M-gent** | Traces contribute to memory; stigmergic patterns feed M-gent |
| **Coffee** | Stigmergy patterns share mechanism with Coffee stigmergy |
| **AGENTESE** | Expose via `self.witness.*` paths |
| **Session** | Traces are scoped to sessions; session is parent trace |

**Proposed AGENTESE paths:**
```
self.witness.trace.create    → Create new decision trace
self.witness.trace.complete  → Complete a trace with outcomes
self.witness.proof.assess    → Assess/generate proof for a trace
self.witness.proof.challenge → Register a rebuttal
self.witness.pattern.reinforce → Strengthen a pattern
self.witness.pattern.warn    → Check pending decision against anti-patterns
```

---

### 8. The Aesthetics of Proofs Themselves

**Question:** Should proofs themselves be beautiful?

Hardy says mathematical proofs have aesthetic qualities. Why not decision proofs?

A beautiful proof might be:
- **Inevitable** — Given the values, this decision *had* to be made
- **Unexpected** — The justification reveals something non-obvious
- **Economical** — The reasoning is minimal, no bloat

**Open:** How do we cultivate beautiful justifications, not just correct ones?

---

### 9. Collective vs. Individual

**Question:** Are these Kent's decisions or kgents' decisions?

kgents is bigger than Kent. It has collaborators (Claude instances across sessions), a community (future contributors), and its own emergent identity.

**Levels of Attribution:**

1. **Kent's decisions** — Align with Kent's personal values
2. **Session decisions** — Kent + Claude in this session
3. **kgents decisions** — What the project "decided" across time

**Open:** Should there be a "kgents soul" that accumulates values across all sessions, distinct from Kent's individual soul?

---

## Speculative Ideas

### The Proof Garden

A visualization metaphor:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THE PROOF GARDEN                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    Healthy (proven)         Challenged         Defeated                    │
│    🌳 DI Refactor          🌿 Chat removal    💀 Forge service             │
│    🌳 Crown Jewel pattern  🌿 Deletion spree                               │
│    🌳 AGENTESE protocol                                                    │
│    🌲 Flux streaming                                                       │
│                                                                             │
│    Seeds (pending)                                                         │
│    🌱 Decision Quality Proofs (this document)                              │
│    🌱 Witness service                                                      │
│                                                                             │
│    Anti-patterns (differential denials)                                    │
│    🚫 "Don't add services without AGENTESE path"                          │
│    🚫 "Don't refactor during feature push"                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Regret Surfaces

Map decision space to regret:

```
                    High
                     │
            Regret   │     ╱╲
                     │    ╱  ╲   Over-engineering
                     │   ╱    ╲  zone
                     │  ╱      ╲
                     │ ╱        ╲
                     │╱──────────╲───────
                    ─┼────────────╲──────── Resource investment
                     │             ╲
                     │              ╲  Under-investment
                     │               ╲ zone
                    Low

                     │←─ Sweet spot ─→│
```

The goal: find decisions in the sweet spot where investment matches value.

---

### Value Crystals

As latent principles emerge and solidify:

```python
@dataclass
class ValueCrystal:
    """A latent principle that has crystallized from patterns."""

    name: str
    first_observed: datetime
    crystallized_at: datetime | None = None  # When it became explicit

    # Evidence
    supporting_traces: list[TraceId] = field(default_factory=list)
    pattern_description: str = ""

    # Status
    confidence: float = 0.0  # 0.0 = nascent, 1.0 = crystallized

    def is_crystallized(self) -> bool:
        return self.confidence >= 0.8 and self.crystallized_at is not None
```

Value crystals emerge from stigmergic traces. When a pattern has enough support, it becomes a stated principle.

---

### Decision Genealogies

Every decision has ancestors:

```
                    ┌──────────────────┐
                    │ "Taste matters"  │ (founding value)
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
     │ "Curated > all"│ │ "Joy-inducing" │ │ "Composable"   │
     └───────┬────────┘ └───────┬────────┘ └───────┬────────┘
             │                  │                  │
             ▼                  ▼                  ▼
     ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
     │ Delete Forge   │ │ Crown Jewel UI │ │ AGENTESE verbs │
     │ and Chat       │ │ breathing anim │ │ >> composition │
     └────────────────┘ └────────────────┘ └────────────────┘
```

**Open:** Should traces explicitly link to their value ancestors?

---

### Proof Debt

Like technical debt, but for justification:

```python
@dataclass
class ProofDebt:
    """A decision we haven't yet justified."""

    trace_id: TraceId
    incurred_at: datetime

    # Why we haven't proven it yet
    reason: Literal["no_outcome_yet", "low_priority", "unclear_values", "contested"]

    # Interest: the longer we wait, the harder to prove
    debt_multiplier: float = 1.0

    def accrue_interest(self, days: float) -> None:
        """Proof debt compounds."""
        self.debt_multiplier *= (1 + 0.01 * days)  # 1% per day
```

---

### Circadian Alignment

Decisions made at different times have different qualities:

```python
@dataclass
class CircadianContext:
    """When in Kent's cycle was this decision made?"""

    time_of_day: datetime

    # Kent's self-reported state
    energy_phase: Literal["rising", "peak", "falling", "trough"]

    # Inferred quality
    @property
    def decision_quality_multiplier(self) -> float:
        """Peak decisions are more likely to be good."""
        return {
            "rising": 0.9,
            "peak": 1.2,
            "falling": 0.8,
            "trough": 0.6,
        }[self.energy_phase]
```

**Open:** Should we weight proof confidence by circadian phase?

---

## Storage Model

DecisionTraces are D-gent domains:

```python
# In services/witness/persistence.py

from agents.d import TableAdapter
from sqlalchemy import Column, String, Float, DateTime, JSON, Enum as SAEnum

class DecisionTraceAdapter(TableAdapter[DecisionTrace]):
    """D-gent persistence for decision traces."""

    __tablename__ = "decision_traces"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, nullable=False, index=True)
    session_id = Column(String, index=True)
    parent_id = Column(String, index=True)

    what = Column(String, nullable=False)
    why = Column(String)

    granularity = Column(SAEnum(DecisionGranularity))
    source = Column(SAEnum(DecisionSource))

    # JSON columns for complex structures
    resources = Column(JSON)
    principle_alignments = Column(JSON)
    aesthetic = Column(JSON)
    outcomes = Column(JSON)
    proof = Column(JSON)

    # Denormalized for querying
    proof_status = Column(SAEnum(ProofStatus), index=True)
    confidence = Column(Float)
    regret = Column(Float)
```

---

## Next Steps

1. **Implement `DecisionTrace` dataclass** — The schema above as Python code
2. **Create `self.witness.*` AGENTESE paths** — Expose trace creation/assessment
3. **Wire to D-gent** — Persistence layer
4. **Build trivial prover** — Phase 0: everything passes
5. **Add to session workflow** — Prompt Kent to create traces at decision points

---

*"The trace is the proof. The proof is the trace."*

---

**Filed:** 2025-12-21
**Companion:** `decision-quality-proofs.md`
**Status:** Ready for implementation feedback
