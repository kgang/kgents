# Witness Self-Correction: Continuous Refinement Protocol

> *"Self-correction is not failure—it's the proof of agency."*

**Status:** Ready for Implementation
**Priority:** High
**Estimated Effort:** 3-4 sessions
**Dependencies:** Witness Crown Jewel (98% complete)

---

## Executive Summary

This plan implements continuous refinement and self-correction capabilities for the Witness system. An enlightened agent doesn't just observe—it learns from its mistakes, tracks contradictions, and evolves its understanding over time.

**Core Insight:** Marks are opinions. Corrections are wisdom. Crystals are understanding.

---

## Phase 1: SUPERSEDES Link Relation

**Goal:** Allow marks to correct/supersede previous marks while preserving immutability.

### 1.1 Add SUPERSEDES to LinkRelation

**File:** `impl/claude/services/witness/mark.py`

```python
class LinkRelation(Enum):
    """
    Types of causal relationships between Marks.
    """
    CAUSES = auto()      # Direct causation: A caused B
    CONTINUES = auto()   # Continuation: A leads to B in same thread
    BRANCHES = auto()    # Branching: B is a parallel exploration from A
    FULFILLS = auto()    # Fulfillment: B completes intent declared in A
    SUPERSEDES = auto()  # NEW: B corrects/replaces A (A remains but is marked superseded)
```

### 1.2 Add superseded_by field to Mark metadata

The original mark gains metadata indicating it was superseded:

```python
# When creating a superseding mark, update the original's metadata
# Since marks are immutable, this is tracked in persistence layer
```

### 1.3 Update WitnessPersistence

**File:** `impl/claude/services/witness/persistence.py`

Add new method:

```python
async def save_mark_superseding(
    self,
    action: str,
    supersedes_mark_id: str,
    reasoning: str | None = None,
    principles: list[str] | None = None,
    author: str = "kent",
) -> MarkResult:
    """
    Save a mark that supersedes (corrects) another mark.

    This creates a SUPERSEDES link and marks the original as superseded
    in a separate tracking table.

    Args:
        action: The corrected understanding
        supersedes_mark_id: The mark being corrected
        reasoning: Why the correction was needed
        principles: Principles honored
        author: Who made the correction

    Returns:
        MarkResult for the new superseding mark
    """
    # 1. Validate supersedes_mark_id exists
    original = await self.get_mark(supersedes_mark_id)
    if not original:
        raise ValueError(f"Cannot supersede non-existent mark: {supersedes_mark_id}")

    # 2. Create the new mark with SUPERSEDES link
    mark_id = f"mark-{uuid.uuid4().hex[:12]}"

    # 3. Record in supersession tracking table
    # (See 1.4 for table schema)

    # 4. Return result
    return MarkResult(...)
```

Add query methods:

```python
async def get_marks(
    self,
    limit: int = 20,
    exclude_superseded: bool = False,  # NEW
    only_superseded: bool = False,     # NEW
    ...
) -> list[MarkResult]:
    """Get marks with optional supersession filtering."""

async def get_supersession_chain(self, mark_id: str) -> list[MarkResult]:
    """Get the chain of supersessions for a mark (original → corrections)."""

async def get_correction_stats(self) -> dict[str, Any]:
    """Get statistics about mark corrections."""
```

### 1.4 Add WitnessSupersession Model

**File:** `impl/claude/models/witness.py`

```python
class WitnessSupersession(Base):
    """
    Tracks mark supersession relationships.

    Separate from MarkLink because we need fast queries on superseded status.
    """
    __tablename__ = "witness_supersessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_mark_id: Mapped[str] = mapped_column(String(64), index=True)
    superseding_mark_id: Mapped[str] = mapped_column(String(64), index=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
```

### 1.5 Update CLI

**File:** `impl/claude/protocols/cli/handlers/witness_thin.py`

Update `cmd_mark`:

```python
def cmd_mark(args: list[str]) -> int:
    """
    Create a mark.

    Usage:
        kg witness mark "Did a thing"
        kg witness mark "Correction" --supersedes mark-abc123  # NEW
    """
    # Parse --supersedes flag
    supersedes_mark_id: str | None = None
    # ... parsing logic ...

    if supersedes_mark_id:
        result = _create_mark_superseding(action, supersedes_mark_id, reasoning, principles)
    else:
        result = _create_mark(action, reasoning, principles, parent_mark_id=parent_mark_id)
```

Update `cmd_show`:

```python
def cmd_show(args: list[str]) -> int:
    """
    Show recent marks.

    Usage:
        kg witness show --exclude-superseded  # NEW: Only current truth
        kg witness show --only-superseded     # NEW: Only corrected marks
        kg witness show --corrections         # NEW: Show correction chains
    """
```

### 1.6 Migration

**File:** `impl/claude/system/migrations/versions/XXX_add_witness_supersession.py`

```python
def upgrade() -> None:
    op.create_table(
        'witness_supersessions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('original_mark_id', sa.String(64), index=True, nullable=False),
        sa.Column('superseding_mark_id', sa.String(64), index=True, nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
```

### 1.7 Tests

**File:** `impl/claude/services/witness/_tests/test_supersession.py`

```python
class TestSupersession:
    async def test_supersede_mark_creates_link(self):
        """Superseding a mark creates SUPERSEDES link."""

    async def test_superseded_mark_excluded_by_default(self):
        """get_marks(exclude_superseded=True) filters superseded marks."""

    async def test_supersession_chain_traversal(self):
        """Can traverse A → B → C supersession chain."""

    async def test_cannot_supersede_nonexistent_mark(self):
        """Superseding non-existent mark raises ValueError."""

    async def test_correction_stats(self):
        """Correction statistics are accurate."""
```

---

## Phase 2: Crystal Confidence Decay

**Goal:** Crystal confidence should decay based on time, contradictions, and reference frequency.

### 2.1 Add DecayConfig

**File:** `impl/claude/services/witness/crystal.py`

```python
@dataclass(frozen=True)
class DecayConfig:
    """Configuration for confidence decay."""

    half_life_days: float = 30.0          # Confidence halves every N days
    contradiction_penalty: float = 0.9     # Multiply by this per contradiction
    reference_boost_per_query: float = 0.02  # Boost per recent reference
    max_boost: float = 1.2                 # Cap on reference boost
    floor: float = 0.1                     # Minimum confidence floor

DEFAULT_DECAY_CONFIG = DecayConfig()
```

### 2.2 Add Decay Calculation

**File:** `impl/claude/services/witness/crystal.py`

Add method to Crystal class:

```python
def decayed_confidence(
    self,
    now: datetime | None = None,
    contradiction_count: int = 0,
    reference_count: int = 0,
    config: DecayConfig = DEFAULT_DECAY_CONFIG,
) -> float:
    """
    Calculate confidence with decay applied.

    Decay formula:
        decayed = base * time_decay * contradiction_penalty * reference_boost

    Where:
        time_decay = 0.5 ^ (age_days / half_life_days)
        contradiction_penalty = 0.9 ^ contradiction_count
        reference_boost = min(1.0 + reference_count * 0.02, 1.2)

    Args:
        now: Current time (defaults to datetime.now())
        contradiction_count: Number of contradicting marks
        reference_count: Number of recent references in queries
        config: Decay configuration

    Returns:
        Decayed confidence value in [config.floor, 1.0]
    """
    now = now or datetime.now()
    age_days = (now - self.crystallized_at).total_seconds() / 86400

    time_decay = 0.5 ** (age_days / config.half_life_days)
    contradiction_penalty = config.contradiction_penalty ** contradiction_count
    reference_boost = min(
        1.0 + reference_count * config.reference_boost_per_query,
        config.max_boost
    )

    decayed = self.confidence * time_decay * contradiction_penalty * reference_boost
    return max(config.floor, min(1.0, decayed))
```

### 2.3 Track Reference Counts

**File:** `impl/claude/services/witness/crystal_store.py`

Add reference tracking:

```python
class CrystalStore:
    def __init__(self, ...):
        self._reference_counts: dict[CrystalId, int] = {}
        self._reference_timestamps: dict[CrystalId, list[datetime]] = {}

    def record_reference(self, crystal_id: CrystalId) -> None:
        """Record that a crystal was referenced in a query."""
        self._reference_counts[crystal_id] = self._reference_counts.get(crystal_id, 0) + 1
        if crystal_id not in self._reference_timestamps:
            self._reference_timestamps[crystal_id] = []
        self._reference_timestamps[crystal_id].append(datetime.now())
        # Keep only last 30 days of timestamps
        cutoff = datetime.now() - timedelta(days=30)
        self._reference_timestamps[crystal_id] = [
            t for t in self._reference_timestamps[crystal_id] if t > cutoff
        ]

    def get_recent_reference_count(self, crystal_id: CrystalId, days: int = 7) -> int:
        """Get reference count in last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        timestamps = self._reference_timestamps.get(crystal_id, [])
        return sum(1 for t in timestamps if t > cutoff)
```

### 2.4 Update Context Query

**File:** `impl/claude/services/witness/context.py`

```python
async def get_context(
    budget_tokens: int = 2000,
    recency_weight: float = 0.7,
    relevance_query: str | None = None,
    confidence_floor: float = 0.3,  # NEW: Filter by decayed confidence
    apply_decay: bool = True,       # NEW: Whether to apply decay
) -> ContextResult:
    """Get budget-aware context with optional confidence decay."""
```

### 2.5 Update CLI

**File:** `impl/claude/protocols/cli/handlers/witness_thin.py`

```python
def cmd_crystals(args: list[str]) -> int:
    """
    List recent crystals.

    Usage:
        kg witness crystals --with-decay     # NEW: Show decayed confidence
        kg witness crystals --confidence-floor 0.5  # NEW: Filter by confidence
    """

def cmd_context(args: list[str]) -> int:
    """
    Usage:
        kg witness context --confidence-floor 0.5  # NEW
        kg witness context --no-decay              # NEW: Raw confidence
    """
```

### 2.6 Tests

**File:** `impl/claude/services/witness/_tests/test_confidence_decay.py`

```python
class TestConfidenceDecay:
    def test_decay_over_time(self):
        """Confidence decays with half-life."""
        crystal = Crystal(confidence=0.8, crystallized_at=thirty_days_ago)
        assert crystal.decayed_confidence() == pytest.approx(0.4, rel=0.1)

    def test_contradiction_penalty(self):
        """Contradictions reduce confidence."""
        crystal = Crystal(confidence=0.8, crystallized_at=now)
        assert crystal.decayed_confidence(contradiction_count=2) < 0.8

    def test_reference_boost(self):
        """Recent references boost confidence."""
        crystal = Crystal(confidence=0.5, crystallized_at=now)
        assert crystal.decayed_confidence(reference_count=5) > 0.5

    def test_floor_respected(self):
        """Confidence never drops below floor."""
        crystal = Crystal(confidence=0.8, crystallized_at=one_year_ago)
        assert crystal.decayed_confidence() >= 0.1
```

---

## Phase 3: Conflict Detection

**Goal:** Detect when new marks contradict existing marks and surface conflicts.

### 3.1 Add ConflictDetector

**File:** `impl/claude/services/witness/conflict.py` (NEW FILE)

```python
"""
Conflict Detection for Witness Marks.

Detects semantic and principle-based contradictions between marks.
Implements Article II: Adversarial Cooperation from the Constitution.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mark import Mark
    from .persistence import WitnessPersistence

@dataclass
class Conflict:
    """A detected conflict between marks."""

    mark_a_id: str
    mark_b_id: str
    conflict_type: str  # "semantic" | "principle" | "temporal"
    confidence: float   # How confident we are this is a real conflict
    description: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "mark_a_id": self.mark_a_id,
            "mark_b_id": self.mark_b_id,
            "conflict_type": self.conflict_type,
            "confidence": self.confidence,
            "description": self.description,
        }


class ConflictDetector:
    """
    Detects conflicts between marks.

    Detection strategies:
    1. Keyword contradiction: "use X" vs "don't use X"
    2. Principle contradiction: same topic, different principles
    3. Temporal contradiction: "A before B" vs "B before A"

    Future: Embedding-based semantic similarity for deeper conflicts.
    """

    # Contradiction keywords (word → opposite)
    CONTRADICTIONS = {
        "use": "don't use",
        "should": "shouldn't",
        "always": "never",
        "enable": "disable",
        "add": "remove",
        "keep": "delete",
        "yes": "no",
        "correct": "incorrect",
        "right": "wrong",
    }

    def __init__(self, persistence: "WitnessPersistence"):
        self._persistence = persistence

    async def check_conflicts(
        self,
        new_mark: "Mark",
        window_hours: int = 168,  # 7 days
        limit: int = 100,
    ) -> list[Conflict]:
        """
        Check if a new mark conflicts with recent marks.

        Args:
            new_mark: The mark being created
            window_hours: How far back to look
            limit: Max marks to check against

        Returns:
            List of detected conflicts (may be empty)
        """
        recent_marks = await self._persistence.get_marks(
            limit=limit,
            since=datetime.now() - timedelta(hours=window_hours),
        )

        conflicts = []
        for existing in recent_marks:
            conflict = self._detect_conflict(new_mark, existing)
            if conflict:
                conflicts.append(conflict)

        return conflicts

    def _detect_conflict(
        self,
        new_mark: "Mark",
        existing: "MarkResult",
    ) -> Conflict | None:
        """Detect conflict between two marks."""
        new_content = new_mark.response.content.lower()
        existing_content = existing.action.lower()

        # Check keyword contradictions
        for word, opposite in self.CONTRADICTIONS.items():
            if word in new_content and opposite in existing_content:
                return Conflict(
                    mark_a_id=existing.mark_id,
                    mark_b_id=str(new_mark.id),
                    conflict_type="semantic",
                    confidence=0.7,
                    description=f"Potential contradiction: '{word}' vs '{opposite}'",
                )
            if opposite in new_content and word in existing_content:
                return Conflict(
                    mark_a_id=existing.mark_id,
                    mark_b_id=str(new_mark.id),
                    conflict_type="semantic",
                    confidence=0.7,
                    description=f"Potential contradiction: '{opposite}' vs '{word}'",
                )

        # Check principle contradictions (same topic, different principles)
        # Future enhancement: use embeddings for topic similarity

        return None


async def detect_and_surface_conflicts(
    mark: "Mark",
    persistence: "WitnessPersistence",
) -> list[Conflict]:
    """
    Convenience function to detect conflicts and return them.

    Used by CLI to warn about potential contradictions.
    """
    detector = ConflictDetector(persistence)
    return await detector.check_conflicts(mark)
```

### 3.2 Integrate with Mark Creation

**File:** `impl/claude/protocols/cli/handlers/witness_thin.py`

After creating a mark, check for conflicts:

```python
async def _create_mark_with_conflict_check(
    action: str,
    reasoning: str | None,
    principles: list[str] | None,
    ...
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Create mark and check for conflicts."""
    from services.witness.conflict import detect_and_surface_conflicts

    # Create the mark
    result = await _create_mark_async(action, reasoning, principles, ...)

    # Check for conflicts
    mark = Mark.from_thought(action, "cli", tags=tuple(principles or []))
    conflicts = await detect_and_surface_conflicts(mark, persistence)

    return result, [c.to_dict() for c in conflicts]
```

Update CLI output:

```python
def cmd_mark(args: list[str]) -> int:
    result, conflicts = _create_mark_with_conflict_check(...)

    if conflicts and not json_output:
        console.print(f"\n[yellow]⚠️  Potential conflicts detected:[/yellow]")
        for c in conflicts:
            console.print(f"  • {c['description']}")
            console.print(f"    Conflicts with: {c['mark_a_id'][:12]}...")
        console.print(f"\n[dim]Use --supersedes to correct if needed[/dim]")
```

### 3.3 Tests

**File:** `impl/claude/services/witness/_tests/test_conflict.py`

```python
class TestConflictDetection:
    async def test_keyword_contradiction_detected(self):
        """'use X' conflicts with 'don't use X'."""

    async def test_no_false_positives_unrelated(self):
        """Unrelated marks don't trigger conflicts."""

    async def test_conflict_window_respected(self):
        """Old marks outside window don't trigger conflicts."""
```

---

## Phase 4: Reflection Loop

**Goal:** After crystallization, emit a meta-mark reflecting on crystallization quality.

### 4.1 Update Crystallizer

**File:** `impl/claude/services/witness/crystallizer.py`

```python
async def crystallize_marks_with_reflection(
    self,
    marks: list[Mark],
    session_id: str = "",
    emit_reflection: bool = True,
) -> tuple[Crystal, Mark | None]:
    """
    Crystallize marks and emit a reflection mark.

    The reflection mark captures:
    - Number of marks crystallized
    - Resulting confidence
    - Whether LLM was used
    - Dominant mood dimension

    This creates a trail of crystallization quality that can itself be analyzed.

    Args:
        marks: Marks to crystallize
        session_id: Session identifier
        emit_reflection: Whether to emit reflection mark

    Returns:
        Tuple of (crystal, reflection_mark or None)
    """
    crystal = await self.crystallize_marks(marks, session_id)

    reflection_mark = None
    if emit_reflection:
        reflection_content = (
            f"Crystallized {len(marks)} marks → L{crystal.level.value} crystal "
            f"(confidence: {crystal.confidence:.0%}, mood: {crystal.mood.dominant_quality})"
        )
        reflection_mark = Mark.from_thought(
            content=reflection_content,
            source="crystallizer",
            tags=("meta", "reflection", "crystallization"),
            origin="witness",
        )

    return crystal, reflection_mark
```

### 4.2 Update CLI

**File:** `impl/claude/protocols/cli/handlers/witness_thin.py`

```python
async def _crystallize_async(...) -> dict[str, Any]:
    """Crystallize with optional reflection."""
    crystal, reflection = await crystallizer.crystallize_marks_with_reflection(
        marks,
        session_id=session_id or "",
        emit_reflection=True,
    )

    # Save reflection mark
    if reflection:
        await persistence.save_mark(
            action=reflection.response.content,
            reasoning="Automatic crystallization reflection",
            principles=["generative"],
            author="system",
        )

    return {
        "crystal_id": str(crystal.id),
        "reflection_mark_id": str(reflection.id) if reflection else None,
        ...
    }
```

### 4.3 Tests

**File:** `impl/claude/services/witness/_tests/test_crystallizer.py`

Add tests:

```python
async def test_crystallize_with_reflection_emits_mark(self):
    """Crystallization emits reflection mark."""
    crystal, reflection = await crystallizer.crystallize_marks_with_reflection(marks)
    assert reflection is not None
    assert "meta" in reflection.tags
    assert str(len(marks)) in reflection.response.content

async def test_reflection_can_be_disabled(self):
    """Reflection can be disabled."""
    crystal, reflection = await crystallizer.crystallize_marks_with_reflection(
        marks, emit_reflection=False
    )
    assert reflection is None
```

---

## Phase 5: Self-Audit Trail

**Goal:** Query capabilities for analyzing marking patterns and correction rates.

### 5.1 Add Statistics Methods

**File:** `impl/claude/services/witness/persistence.py`

```python
@dataclass
class WitnessStats:
    """Statistics about witness activity."""

    total_marks: int
    superseded_marks: int
    correction_rate: float  # superseded / total
    marks_by_principle: dict[str, int]
    marks_by_author: dict[str, int]
    avg_marks_per_day: float
    crystals_by_level: dict[int, int]
    avg_crystal_confidence: float
    period_days: int


class WitnessPersistence:
    async def get_stats(
        self,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> WitnessStats:
        """
        Get comprehensive witness statistics.

        Args:
            since: Start of period (default: 30 days ago)
            until: End of period (default: now)

        Returns:
            WitnessStats with comprehensive metrics
        """
        since = since or (datetime.now() - timedelta(days=30))
        until = until or datetime.now()
        period_days = (until - since).days or 1

        async with self.session_factory() as session:
            # Total marks in period
            total_marks = await session.execute(
                select(func.count()).select_from(WitnessMark)
                .where(WitnessMark.created_at.between(since, until))
            )
            total = total_marks.scalar() or 0

            # Superseded marks
            superseded_marks = await session.execute(
                select(func.count()).select_from(WitnessSupersession)
                .where(WitnessSupersession.created_at.between(since, until))
            )
            superseded = superseded_marks.scalar() or 0

            # Marks by principle
            # ... aggregation query ...

            # Crystals by level
            # ... aggregation query ...

        return WitnessStats(
            total_marks=total,
            superseded_marks=superseded,
            correction_rate=superseded / total if total > 0 else 0.0,
            marks_by_principle=marks_by_principle,
            marks_by_author=marks_by_author,
            avg_marks_per_day=total / period_days,
            crystals_by_level=crystals_by_level,
            avg_crystal_confidence=avg_confidence,
            period_days=period_days,
        )
```

### 5.2 Add CLI Commands

**File:** `impl/claude/protocols/cli/handlers/witness_thin.py`

```python
def cmd_stats(args: list[str]) -> int:
    """
    Show witness statistics.

    Usage:
        kg witness stats                    # Last 30 days
        kg witness stats --days 7           # Last 7 days
        kg witness stats --correction-rate  # Just correction rate
        kg witness stats --by-principle     # Marks grouped by principle
        kg witness stats --confidence-trend # Crystal confidence over time
        kg witness stats --json             # Machine-readable
    """
    # Parse args
    days = 30
    show_correction_rate = "--correction-rate" in args
    show_by_principle = "--by-principle" in args
    show_confidence_trend = "--confidence-trend" in args
    json_output = "--json" in args

    stats = _get_stats(days)

    if json_output:
        print(json.dumps(stats.to_dict()))
        return 0

    console = _get_console()

    if show_correction_rate:
        console.print(f"Correction rate: {stats.correction_rate:.1%}")
        return 0

    if show_by_principle:
        console.print("\n[bold]Marks by Principle[/bold]")
        for principle, count in sorted(stats.marks_by_principle.items(), key=lambda x: -x[1]):
            console.print(f"  {principle}: {count}")
        return 0

    # Full stats output
    console.print(f"\n[bold]Witness Statistics ({stats.period_days} days)[/bold]")
    console.print("[dim]" + "─" * 40 + "[/dim]")
    console.print(f"  Total marks: {stats.total_marks}")
    console.print(f"  Superseded marks: {stats.superseded_marks}")
    console.print(f"  Correction rate: {stats.correction_rate:.1%}")
    console.print(f"  Avg marks/day: {stats.avg_marks_per_day:.1f}")
    console.print(f"\n[bold]Crystals by Level[/bold]")
    for level, count in stats.crystals_by_level.items():
        level_name = ["SESSION", "DAY", "WEEK", "EPOCH"][level]
        console.print(f"  L{level} ({level_name}): {count}")
    console.print(f"\n  Avg crystal confidence: {stats.avg_crystal_confidence:.0%}")

    return 0
```

Update help and handlers dict:

```python
handlers = {
    ...
    "stats": cmd_stats,
}
```

### 5.3 Tests

**File:** `impl/claude/services/witness/_tests/test_stats.py`

```python
class TestWitnessStats:
    async def test_correction_rate_calculation(self):
        """Correction rate = superseded / total."""

    async def test_marks_by_principle_aggregation(self):
        """Principles are correctly aggregated."""

    async def test_empty_period_returns_zeros(self):
        """Empty period returns zeroed stats, not errors."""
```

---

## Phase 6: Teaching Promotion Loop

**Goal:** Track when crystals are promoted to Brain teachings for feedback.

### 6.1 Add PromotionRecord Model

**File:** `impl/claude/models/witness.py`

```python
class WitnessPromotion(Base):
    """
    Tracks crystal promotions to Brain teachings.

    This creates a feedback loop: crystals that become teachings
    validate the crystallization approach.
    """
    __tablename__ = "witness_promotions"

    id: Mapped[int] = mapped_column(primary_key=True)
    crystal_id: Mapped[str] = mapped_column(String(64), index=True)
    teaching_id: Mapped[str] = mapped_column(String(64), index=True)
    confidence_at_promotion: Mapped[float] = mapped_column(Float)
    promoted_by: Mapped[str] = mapped_column(String(32))  # "auto" | "kent" | "claude"
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
```

### 6.2 Update Integration Module

**File:** `impl/claude/services/witness/integration.py`

```python
async def promote_to_brain(
    crystal_id: CrystalId,
    promoted_by: str = "claude",
) -> dict[str, Any]:
    """
    Promote a crystal to a Brain teaching.

    Records the promotion for feedback analysis.
    """
    # ... existing promotion logic ...

    # Record the promotion
    async with session_factory() as session:
        promotion = WitnessPromotion(
            crystal_id=str(crystal_id),
            teaching_id=teaching_id,
            confidence_at_promotion=crystal.confidence,
            promoted_by=promoted_by,
        )
        session.add(promotion)
        await session.commit()

    return {
        "success": True,
        "crystal_id": str(crystal_id),
        "teaching_id": teaching_id,
        "promoted_by": promoted_by,
    }


async def get_promotion_stats() -> dict[str, Any]:
    """Get statistics about crystal promotions."""
    # Avg confidence at promotion
    # Promotion rate by crystal level
    # Most promoted principles
```

### 6.3 Migration

**File:** `impl/claude/system/migrations/versions/XXX_add_witness_promotion.py`

```python
def upgrade() -> None:
    op.create_table(
        'witness_promotions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('crystal_id', sa.String(64), index=True, nullable=False),
        sa.Column('teaching_id', sa.String(64), index=True, nullable=False),
        sa.Column('confidence_at_promotion', sa.Float(), nullable=False),
        sa.Column('promoted_by', sa.String(32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
```

---

## Phase 7: Agent Training & Documentation Updates

**Goal:** Update all documentation and system prompts so agents are trained to use `/crystallize` and self-correction appropriately.

**Critical Insight:** Infrastructure without training is shelfware. Agents need to be taught WHEN, WHY, and HOW to self-correct.

### 7.1 Update CLAUDE.md

**File:** `CLAUDE.md`

Add new section after "Decision Witnessing":

```markdown
## Self-Correction Protocol

> *"Self-correction is not failure—it's the proof of agency."*

### When to Correct

| Situation | Action |
|-----------|--------|
| You made a factual error | `km "Correction: X was wrong" --supersedes mark-xxx` |
| New information invalidates old mark | `km "Updated understanding" --supersedes mark-xxx` |
| You changed your mind after reflection | `km "Revised position" --supersedes mark-xxx` |

### The Mirror Test for Corrections

Before superseding, ask:
1. Is this genuinely wrong, or just different framing?
2. Would future-me benefit from seeing the correction?
3. Is this correction worth the cognitive overhead?

If all three are "yes", supersede. If not, just make a new mark.

### Crystallize at Session End

Before ending any productive session:
```bash
/crystallize   # Interactive ceremony
# OR
kg witness crystallize  # CLI direct
```

This compresses session marks into durable crystal memory.
```

### 7.2 Update HYDRATE.md

**File:** `HYDRATE.md`

Add to "Witnessing: Marks & Decisions" section:

```markdown
### Self-Correction

When you realize a previous mark was wrong:

```bash
# Supersede the incorrect mark
km "Corrected understanding" --supersedes mark-abc123 --tag correction

# Query your correction history
kg witness show --only-superseded  # See what you've corrected
kg witness stats --correction-rate  # Your correction rate
```

**Healthy correction rate:** 3-10% indicates growth without chaos.
**Too low (<1%):** May indicate overconfidence or fear of admitting mistakes.
**Too high (>20%):** May indicate insufficient reflection before marking.

### End of Session Crystallization

Before ending a productive session:

```bash
/crystallize   # Use the slash command for guided ceremony
```

This ensures:
1. Session marks are compressed to crystal
2. Valuable patterns don't evaporate
3. Next Claude inherits wisdom, not noise
```

### 7.3 Update /crystallize Slash Command

**File:** `.claude/commands/crystallize.md`

Enhance with self-correction awareness:

```markdown
## Self-Correction Check

Before crystallizing, review today's marks:

```bash
kg witness show --today
```

Ask:
- Any marks that should be superseded before crystallizing?
- Any contradictions that should be resolved?
- Any patterns emerging that deserve their own mark?

If you find marks to correct, supersede them first:
```bash
km "Corrected: X" --supersedes mark-xxx
```

Then proceed with crystallization.
```

### 7.4 Create /correct Slash Command

**File:** `.claude/commands/correct.md` (NEW FILE)

```markdown
# /correct - Self-Correction Ceremony

A guided ceremony for correcting previous marks.

## Protocol

1. **Identify the mark to correct**
   ```bash
   kg witness show --today
   # Find the mark ID (mark-xxx)
   ```

2. **Explain the correction**
   - What was wrong?
   - Why was it wrong?
   - What's the corrected understanding?

3. **Emit the correction**
   ```bash
   km "Corrected: [new understanding]" --supersedes mark-xxx -w "reason for correction" --tag correction
   ```

4. **Verify the supersession**
   ```bash
   kg witness show --corrections
   ```

## When to Use

- You made a factual error
- New information invalidates old understanding
- You changed your position after reflection
- A mark was hasty or unconsidered

## Anti-Patterns

- **Correcting style, not substance**: Don't supersede just because you'd phrase it differently
- **Correcting to please**: Don't supersede because someone disagreed
- **Over-correcting**: If you're superseding >20% of marks, slow down

## Example

```
Agent: I marked that "WebSockets are better for this use case" but after
       reading the latency requirements, SSE is actually sufficient.

km "SSE is sufficient for our latency requirements" \
   --supersedes mark-abc123 \
   -w "WebSockets add complexity without benefit for unidirectional flow" \
   --tag correction
```
```

### 7.5 Update docs/skills/witness-for-agents.md

**File:** `docs/skills/witness-for-agents.md`

Add new section:

```markdown
## Self-Correction Protocol

### Superseding Marks

```bash
# Correct a previous mark
km "Corrected understanding" --supersedes mark-abc123 --json
# → {"mark_id": "mark-xyz789", "supersedes": "mark-abc123", ...}

# Query only non-superseded marks (current truth)
kg witness show --exclude-superseded --json

# Query only superseded marks (correction history)
kg witness show --only-superseded --json

# Get correction statistics
kg witness stats --correction-rate --json
# → {"correction_rate": 0.05, ...}
```

### Subagent Correction Protocol

1. Before acting, check if recent marks conflict with your understanding
2. If you must correct, explain WHY in the reasoning
3. Use `--tag correction` for traceability
4. Report correction to parent agent if significant

```python
# Example: Subagent discovers error in parent's mark
async def correct_if_needed(parent_mark_id: str, new_understanding: str):
    result = subprocess.run([
        "km", new_understanding,
        "--supersedes", parent_mark_id,
        "-w", "Discovered during deeper analysis",
        "--tag", "correction",
        "--json"
    ], capture_output=True, text=True)
    return json.loads(result.stdout)
```
```

### 7.6 Reference U-gent Safety Infrastructure

**Integration Point:** `spec/agents/u-gent.md`

The self-correction system should integrate with U-gent's safety harness:

```markdown
### Safety Harness Integration

Self-correction operates within U-gent's exploration boundaries:

1. **Correction Limits**: U-gent can set max corrections per session
2. **Escalation Triggers**: Too many corrections may trigger human review
3. **Rollback Integration**: Corrections can trigger automatic rollback checkpoints

The safety harness from `spec/agents/u-gent.md` provides:
- Exploration boundaries (don't correct in protected zones)
- Escalation protocols (when correction rate exceeds threshold)
- Audit trail integration (all corrections are witnessed)

See: `spec/agents/u-gent.md` → Safety Harness section
```

### 7.7 Update System Prompt Templates

**File:** `impl/claude/protocols/agentese/contexts/self_trail.py`

Add self-correction context:

```python
SELF_CORRECTION_CONTEXT = """
## Self-Correction Protocol

You have the ability to correct previous marks when you discover errors.

**When to correct:**
- Factual errors discovered through new information
- Changed understanding after deeper analysis
- Hasty marks that need refinement

**How to correct:**
```bash
km "Corrected: [new understanding]" --supersedes mark-xxx -w "reason"
```

**When NOT to correct:**
- Style differences (just make a new mark)
- Disagreement without new evidence
- Correcting to please (maintain intellectual honesty)

Your healthy correction rate should be 3-10%. Check with:
```bash
kg witness stats --correction-rate
```
"""
```

### 7.8 Tests for Documentation Compliance

**File:** `impl/claude/protocols/_tests/test_self_correction_docs.py`

```python
class TestSelfCorrectionDocs:
    def test_claude_md_has_self_correction_section(self):
        """CLAUDE.md includes self-correction protocol."""
        content = Path("CLAUDE.md").read_text()
        assert "Self-Correction Protocol" in content
        assert "--supersedes" in content

    def test_hydrate_md_has_correction_guidance(self):
        """HYDRATE.md includes correction guidance."""
        content = Path("HYDRATE.md").read_text()
        assert "correction-rate" in content
        assert "--supersedes" in content

    def test_crystallize_command_exists(self):
        """crystallize.md slash command exists."""
        assert Path(".claude/commands/crystallize.md").exists()

    def test_correct_command_exists(self):
        """correct.md slash command exists."""
        assert Path(".claude/commands/correct.md").exists()
```

---

## Verification Checklist

After implementation, verify:

- [ ] `km "test" --supersedes mark-xxx` creates SUPERSEDES link
- [ ] `kg witness show --exclude-superseded` filters correctly
- [ ] `kg witness crystals --with-decay` shows decayed confidence
- [ ] `kg witness context --confidence-floor 0.5` filters low-confidence crystals
- [ ] Conflict detection warns when creating contradictory marks
- [ ] Crystallization emits reflection marks
- [ ] `kg witness stats` shows comprehensive statistics
- [ ] `kg witness stats --correction-rate` shows correction percentage
- [ ] Crystal promotions are tracked in database
- [ ] All tests pass: `uv run pytest services/witness/_tests/ -v`
- [ ] Type checks pass: `uv run mypy .`
- [ ] CLAUDE.md has Self-Correction Protocol section
- [ ] HYDRATE.md has correction guidance
- [ ] `/correct` slash command exists
- [ ] `docs/skills/witness-for-agents.md` has self-correction section
- [ ] U-gent safety harness integration documented

---

## Files Changed Summary

| File | Change Type | Phase |
|------|-------------|-------|
| `services/witness/mark.py` | Modify (add SUPERSEDES) | 1 |
| `services/witness/persistence.py` | Modify (supersession methods) | 1, 5 |
| `models/witness.py` | Modify (add tables) | 1, 6 |
| `protocols/cli/handlers/witness_thin.py` | Modify (new flags) | 1, 2, 3, 5 |
| `services/witness/crystal.py` | Modify (decay methods) | 2 |
| `services/witness/crystal_store.py` | Modify (reference tracking) | 2 |
| `services/witness/context.py` | Modify (confidence floor) | 2 |
| `services/witness/conflict.py` | **NEW FILE** | 3 |
| `services/witness/crystallizer.py` | Modify (reflection) | 4 |
| `services/witness/integration.py` | Modify (promotion tracking) | 6 |
| `system/migrations/versions/XXX_*.py` | **NEW FILES** (2) | 1, 6 |
| `services/witness/_tests/test_supersession.py` | **NEW FILE** | 1 |
| `services/witness/_tests/test_confidence_decay.py` | **NEW FILE** | 2 |
| `services/witness/_tests/test_conflict.py` | **NEW FILE** | 3 |
| `services/witness/_tests/test_stats.py` | **NEW FILE** | 5 |
| `CLAUDE.md` | Modify (add Self-Correction Protocol) | 7 |
| `HYDRATE.md` | Modify (add correction guidance) | 7 |
| `.claude/commands/crystallize.md` | Modify (add self-correction check) | 7 |
| `.claude/commands/correct.md` | **NEW FILE** | 7 |
| `docs/skills/witness-for-agents.md` | Modify (add self-correction section) | 7 |
| `protocols/agentese/contexts/self_trail.py` | Modify (add correction context) | 7 |
| `protocols/_tests/test_self_correction_docs.py` | **NEW FILE** | 7 |

---

## Implementation Order

1. **Phase 1** (SUPERSEDES) — Foundation for all self-correction
2. **Phase 2** (Confidence Decay) — Makes context queries smarter
3. **Phase 4** (Reflection Loop) — Quick win, low effort
4. **Phase 5** (Self-Audit Trail) — Enables measurement
5. **Phase 6** (Promotion Loop) — Closes the feedback loop
6. **Phase 7** (Agent Training) — **Do alongside Phases 1-6** — Docs must match implementation
7. **Phase 3** (Conflict Detection) — Most complex, do last

**Critical Note on Phase 7:** Documentation updates should happen in parallel with implementation phases. As each feature lands, update the corresponding docs immediately. Don't leave docs for the end.

---

## Dependencies & References

### U-gent Safety Harness

Phase 7.6 references U-gent's safety infrastructure. Before implementing safety harness integration:

1. **Read:** `spec/agents/u-gent.md` — Safety Harness section
2. **Understand:** Exploration boundaries, escalation protocols
3. **Integrate:** Correction limits, rollback triggers

The safety harness ensures self-correction doesn't become self-destruction:
- Max corrections per session (configurable)
- Escalation when correction rate exceeds threshold
- Protected zones where correction requires human approval

### Exploration Harness

The exploration harness (also in U-gent) provides the sandbox for testing self-correction:
- Isolated environments for correction experiments
- Rollback capabilities when corrections go wrong
- Audit trail for all correction attempts

**Key Principle:** Self-correction should be SAFE. The harness ensures corrections can be undone if they cascade incorrectly.

---

*"The proof IS the decision. The correction IS the growth. The mark IS the witness."*

*Plan created: 2025-12-22 | Updated: 2025-12-22 (added Phase 7 & safety harness refs)*
