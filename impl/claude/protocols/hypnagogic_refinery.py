"""
Hypnagogic Refinery: Automatic codebase optimization during "sleep".

Phase 4.2 of Cross-Pollination: The system improves itself over time
by analyzing cold memories and compressing/optimizing them.

Components:
- M-gent: Identifies cold memories (rarely accessed paths)
- E-gent: Retrieves actual code/data to optimize
- R-gent: Compresses/optimizes using DSPy techniques

Process:
1. IDENTIFY (M-gent): Find cold memories by temperature
2. RETRIEVE (E-gent): Get actual code/artifacts
3. REFINE (R-gent): Optimize with constraints (preserve semantics)
4. APPLY: Apply optimizations with rollback capability

The system becomes more efficient through "dreaming."

See: docs/agent-cross-pollination-final-proposal.md (Phase 4)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class MemoryTemperature(Enum):
    """
    Temperature classification for memories.

    Based on access frequency and recency.
    """

    HOT = "hot"  # Frequently accessed, recent
    WARM = "warm"  # Occasionally accessed
    COLD = "cold"  # Rarely accessed
    FROZEN = "frozen"  # Archival, never accessed


class OptimizationObjective(Enum):
    """Types of optimization objectives."""

    COMPRESSION = "compression"  # Make smaller
    SPEED = "speed"  # Make faster
    CLARITY = "clarity"  # Make clearer/simpler
    CONSOLIDATION = "consolidation"  # Merge related items


class OptimizationStatus(Enum):
    """Status of an optimization attempt."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    APPLIED = "applied"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class MemoryRecord:
    """
    A record in the memory system.

    Could be code, configuration, cached results, etc.
    """

    id: str
    kind: str  # "code", "config", "cache", "trace"
    content: str
    size_bytes: int

    # Access tracking
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)

    # Temperature metrics
    temperature: MemoryTemperature = MemoryTemperature.WARM

    # Reference to original location
    source_path: str | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def age_days(self) -> float:
        """Days since creation."""
        delta = datetime.now() - self.created_at
        return delta.total_seconds() / 86400

    @property
    def dormancy_days(self) -> float:
        """Days since last access."""
        delta = datetime.now() - self.last_accessed
        return delta.total_seconds() / 86400


@dataclass
class OptimizationCandidate:
    """
    A candidate for optimization.
    """

    memory: MemoryRecord
    objective: OptimizationObjective
    estimated_improvement: float  # 0.0 to 1.0
    priority: int = 0  # Lower = higher priority

    # Why this is a good candidate
    rationale: str = ""


@dataclass
class OptimizationResult:
    """
    Result of an optimization attempt.
    """

    candidate: OptimizationCandidate
    status: OptimizationStatus

    # Before/after
    original_content: str
    optimized_content: str | None = None

    # Metrics
    size_before: int = 0
    size_after: int = 0
    improvement: float = 0.0  # Achieved improvement (0.0 to 1.0)

    # Verification
    tests_passed: bool = False
    semantics_preserved: bool = False

    # Rollback
    rollback_available: bool = False

    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None

    # Notes
    notes: str = ""

    @property
    def duration_ms(self) -> float:
        """Duration of optimization in milliseconds."""
        if not self.completed_at:
            return 0.0
        delta = self.completed_at - self.started_at
        return delta.total_seconds() * 1000

    @property
    def size_reduction(self) -> int:
        """Bytes saved."""
        return self.size_before - self.size_after


@dataclass
class RefineryReport:
    """
    Report from a dream cycle.
    """

    cycle_id: str
    started_at: datetime
    completed_at: datetime | None = None

    # What was examined
    memories_examined: int = 0
    candidates_found: int = 0

    # What was optimized
    optimizations_attempted: int = 0
    optimizations_succeeded: int = 0
    optimizations_failed: int = 0

    # Overall impact
    total_bytes_saved: int = 0
    total_improvement: float = 0.0

    # Results
    results: list[OptimizationResult] = field(default_factory=list)

    @property
    def duration_ms(self) -> float:
        """Duration of cycle in milliseconds."""
        if not self.completed_at:
            return 0.0
        delta = self.completed_at - self.started_at
        return delta.total_seconds() * 1000

    @property
    def success_rate(self) -> float:
        """Success rate of optimizations."""
        if self.optimizations_attempted == 0:
            return 0.0
        return self.optimizations_succeeded / self.optimizations_attempted


# =============================================================================
# Memory Store (M-gent Interface)
# =============================================================================


class MemoryStore:
    """
    Interface to M-gent's memory system.

    Provides temperature-based access to memories.
    """

    def __init__(self) -> None:
        self._memories: dict[str, MemoryRecord] = {}

    def add(self, memory: MemoryRecord) -> str:
        """Add a memory record."""
        self._memories[memory.id] = memory
        return memory.id

    def get(self, memory_id: str) -> MemoryRecord | None:
        """Get a memory by ID (updates access count)."""
        memory = self._memories.get(memory_id)
        if memory:
            memory.access_count += 1
            memory.last_accessed = datetime.now()
            self._update_temperature(memory)
        return memory

    def query_by_temperature(
        self,
        max_temp: MemoryTemperature,
        limit: int = 100,
    ) -> list[MemoryRecord]:
        """
        Query memories by temperature.

        Returns memories at or below the given temperature.
        """
        temp_order = {
            MemoryTemperature.FROZEN: 0,
            MemoryTemperature.COLD: 1,
            MemoryTemperature.WARM: 2,
            MemoryTemperature.HOT: 3,
        }

        max_temp_value = temp_order[max_temp]

        results = [
            m
            for m in self._memories.values()
            if temp_order[m.temperature] <= max_temp_value
        ]

        # Sort by coldest first
        results.sort(key=lambda m: (temp_order[m.temperature], -m.dormancy_days))

        return results[:limit]

    def update(self, memory: MemoryRecord) -> None:
        """Update a memory record."""
        self._memories[memory.id] = memory

    def _update_temperature(self, memory: MemoryRecord) -> None:
        """Update temperature based on access patterns."""
        if memory.dormancy_days < 1:
            memory.temperature = MemoryTemperature.HOT
        elif memory.dormancy_days < 7:
            memory.temperature = MemoryTemperature.WARM
        elif memory.dormancy_days < 30:
            memory.temperature = MemoryTemperature.COLD
        else:
            memory.temperature = MemoryTemperature.FROZEN

    def recompute_temperatures(self) -> int:
        """Recompute all temperatures. Returns count updated."""
        count = 0
        for memory in self._memories.values():
            old_temp = memory.temperature
            self._update_temperature(memory)
            if memory.temperature != old_temp:
                count += 1
        return count

    @property
    def memory_count(self) -> int:
        """Total number of memories."""
        return len(self._memories)


# =============================================================================
# Optimization Engine (R-gent Interface)
# =============================================================================


class OptimizationEngine:
    """
    Interface to R-gent's optimization capabilities.

    Provides compression and optimization for different content types.
    """

    def __init__(
        self,
        min_improvement_threshold: float = 0.1,
    ) -> None:
        self._min_improvement = min_improvement_threshold

    async def optimize(
        self,
        content: str,
        objective: OptimizationObjective,
        kind: str,
        constraints: list[str] | None = None,
    ) -> tuple[str | None, float, str]:
        """
        Optimize content according to objective.

        Returns: (optimized_content, improvement, notes)

        If optimization fails or isn't worthwhile, returns (None, 0.0, reason).
        """
        constraints = constraints or []

        if objective == OptimizationObjective.COMPRESSION:
            return await self._compress(content, kind)
        elif objective == OptimizationObjective.CLARITY:
            return await self._clarify(content, kind)
        elif objective == OptimizationObjective.CONSOLIDATION:
            return (None, 0.0, "Consolidation requires multiple items")
        else:
            return (None, 0.0, f"Unknown objective: {objective}")

    async def _compress(self, content: str, kind: str) -> tuple[str | None, float, str]:
        """Compress content to reduce size."""
        if kind == "code":
            # Remove comments and extra whitespace
            lines = content.split("\n")
            compressed_lines: list[str] = []
            for line in lines:
                # Skip comment-only lines
                stripped = line.strip()
                if stripped.startswith("#") and len(stripped) < 50:
                    continue
                # Skip empty lines in sequence
                if (
                    not stripped
                    and compressed_lines
                    and not compressed_lines[-1].strip()
                ):
                    continue
                compressed_lines.append(line.rstrip())

            compressed = "\n".join(compressed_lines)
            improvement = 1.0 - (len(compressed) / max(len(content), 1))

            if improvement >= self._min_improvement:
                return (
                    compressed,
                    improvement,
                    f"Removed {int(improvement * 100)}% via comment/whitespace removal",
                )
            return (None, 0.0, f"Improvement {improvement:.1%} below threshold")

        elif kind == "config":
            # Remove redundant settings (placeholder)
            return (None, 0.0, "Config compression not implemented")

        elif kind == "cache":
            # Cache entries can often be discarded
            return ("", 1.0, "Cache entry can be regenerated")

        return (None, 0.0, f"Unknown kind: {kind}")

    async def _clarify(self, content: str, kind: str) -> tuple[str | None, float, str]:
        """Clarify content for better readability."""
        # Placeholder - would use LLM for actual clarification
        return (None, 0.0, "Clarification requires LLM (not implemented)")

    async def verify_semantics(
        self,
        original: str,
        optimized: str,
        kind: str,
    ) -> tuple[bool, str]:
        """
        Verify that optimized content preserves semantics.

        Returns: (preserved, notes)
        """
        if kind == "code":
            # Check that no function definitions were removed
            original_defs = set(
                line.strip()
                for line in original.split("\n")
                if line.strip().startswith("def ") or line.strip().startswith("class ")
            )
            optimized_defs = set(
                line.strip()
                for line in optimized.split("\n")
                if line.strip().startswith("def ") or line.strip().startswith("class ")
            )

            if original_defs != optimized_defs:
                missing = original_defs - optimized_defs
                return (False, f"Missing definitions: {missing}")

            return (True, "All definitions preserved")

        elif kind == "cache":
            # Caches can always be regenerated
            return (True, "Cache is regenerable")

        return (True, "No verification for this kind")


# =============================================================================
# Hypnagogic Refinery
# =============================================================================


class HypnagogicRefinery:
    """
    Optimization through dreaming: Compress cold memories.

    The refinery runs during system idle time, finding and optimizing
    rarely-accessed code and data to improve system efficiency.

    This implements the "Night Watch" pattern - the system improves
    itself while not actively processing user requests.
    """

    def __init__(
        self,
        memory_store: MemoryStore | None = None,
        engine: OptimizationEngine | None = None,
        max_candidates_per_cycle: int = 10,
        min_improvement_threshold: float = 0.1,
    ) -> None:
        self._memory = memory_store or MemoryStore()
        self._engine = engine or OptimizationEngine(min_improvement_threshold)
        self._max_candidates = max_candidates_per_cycle
        self._min_improvement = min_improvement_threshold

        self._cycles: list[RefineryReport] = []

    async def dream_cycle(self) -> RefineryReport:
        """
        Run a single optimization cycle (a "dream").

        1. Identify cold memories
        2. Select optimization candidates
        3. Optimize with verification
        4. Apply successful optimizations
        """
        cycle_id = f"dream-{uuid4().hex[:8]}"
        report = RefineryReport(
            cycle_id=cycle_id,
            started_at=datetime.now(),
        )

        # 1. Identify cold memories
        cold_memories = self._memory.query_by_temperature(
            max_temp=MemoryTemperature.COLD,
            limit=self._max_candidates * 2,
        )
        report.memories_examined = len(cold_memories)

        # 2. Select candidates
        candidates = self._select_candidates(cold_memories)
        report.candidates_found = len(candidates)

        # 3. Optimize each candidate
        for candidate in candidates:
            result = await self._optimize_candidate(candidate)
            report.results.append(result)

            if result.status == OptimizationStatus.APPLIED:
                report.optimizations_succeeded += 1
                report.total_bytes_saved += result.size_reduction
                report.total_improvement += result.improvement
            elif result.status == OptimizationStatus.FAILED:
                report.optimizations_failed += 1
            elif result.status == OptimizationStatus.SKIPPED:
                pass  # Not counted as attempt
            else:
                report.optimizations_attempted += 1

        report.optimizations_attempted = len(candidates)
        report.completed_at = datetime.now()

        self._cycles.append(report)

        return report

    def _select_candidates(
        self,
        memories: list[MemoryRecord],
    ) -> list[OptimizationCandidate]:
        """Select optimization candidates from cold memories."""
        candidates: list[OptimizationCandidate] = []

        for memory in memories:
            if len(candidates) >= self._max_candidates:
                break

            # Determine best objective for this memory
            objective, estimated, rationale = self._estimate_optimization(memory)

            if estimated >= self._min_improvement:
                candidates.append(
                    OptimizationCandidate(
                        memory=memory,
                        objective=objective,
                        estimated_improvement=estimated,
                        priority=self._compute_priority(memory, estimated),
                        rationale=rationale,
                    )
                )

        # Sort by priority
        candidates.sort(key=lambda c: c.priority)

        return candidates

    def _estimate_optimization(
        self,
        memory: MemoryRecord,
    ) -> tuple[OptimizationObjective, float, str]:
        """Estimate potential optimization for a memory."""
        if memory.kind == "code":
            # Estimate based on size and comment density
            lines = memory.content.split("\n")
            comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
            empty_lines = sum(1 for line in lines if not line.strip())
            total_lines = len(lines)

            if total_lines > 0:
                waste_ratio = (comment_lines + empty_lines) / total_lines
                if waste_ratio > 0.2:
                    return (
                        OptimizationObjective.COMPRESSION,
                        min(0.5, waste_ratio),
                        f"~{int(waste_ratio * 100)}% comments/whitespace",
                    )

            return (
                OptimizationObjective.COMPRESSION,
                0.0,
                "Minimal optimization potential",
            )

        elif memory.kind == "cache":
            # Caches can always be cleared
            return (
                OptimizationObjective.COMPRESSION,
                1.0,
                "Cache can be regenerated on demand",
            )

        elif memory.kind == "config":
            return (
                OptimizationObjective.CONSOLIDATION,
                0.1,
                "May have redundant settings",
            )

        return (OptimizationObjective.COMPRESSION, 0.0, "Unknown kind")

    def _compute_priority(self, memory: MemoryRecord, estimated: float) -> int:
        """Compute optimization priority (lower = higher priority)."""
        # Prioritize: high improvement, large size, old age
        improvement_factor = int((1 - estimated) * 100)
        size_factor = int(100 - min(100, memory.size_bytes / 1000))
        age_factor = int(100 - min(100, memory.dormancy_days))

        return improvement_factor + size_factor + age_factor

    async def _optimize_candidate(
        self,
        candidate: OptimizationCandidate,
    ) -> OptimizationResult:
        """Optimize a single candidate."""
        memory = candidate.memory

        result = OptimizationResult(
            candidate=candidate,
            status=OptimizationStatus.IN_PROGRESS,
            original_content=memory.content,
            size_before=memory.size_bytes,
        )

        # Attempt optimization
        optimized, improvement, notes = await self._engine.optimize(
            content=memory.content,
            objective=candidate.objective,
            kind=memory.kind,
        )

        if optimized is None:
            result.status = OptimizationStatus.SKIPPED
            result.notes = notes
            result.completed_at = datetime.now()
            return result

        result.optimized_content = optimized
        result.size_after = len(optimized.encode("utf-8"))
        result.improvement = improvement

        # Verify semantics preserved
        preserved, verify_notes = await self._engine.verify_semantics(
            original=memory.content,
            optimized=optimized,
            kind=memory.kind,
        )

        result.semantics_preserved = preserved
        result.notes = f"{notes}; Verification: {verify_notes}"

        if not preserved:
            result.status = OptimizationStatus.FAILED
            result.completed_at = datetime.now()
            return result

        # Apply optimization
        result.status = OptimizationStatus.VERIFIED

        # Update memory
        memory.content = optimized
        memory.size_bytes = result.size_after
        self._memory.update(memory)

        result.status = OptimizationStatus.APPLIED
        result.rollback_available = True
        result.completed_at = datetime.now()

        return result

    def rollback(self, result: OptimizationResult) -> bool:
        """Rollback an optimization."""
        if not result.rollback_available:
            return False

        memory = result.candidate.memory
        memory.content = result.original_content
        memory.size_bytes = result.size_before
        self._memory.update(memory)

        result.status = OptimizationStatus.ROLLED_BACK
        result.rollback_available = False

        return True

    @property
    def memory_store(self) -> MemoryStore:
        """Access the memory store."""
        return self._memory

    @property
    def cycles(self) -> list[RefineryReport]:
        """Get all dream cycle reports."""
        return list(self._cycles)

    @property
    def total_bytes_saved(self) -> int:
        """Total bytes saved across all cycles."""
        return sum(c.total_bytes_saved for c in self._cycles)


# =============================================================================
# Factory Functions
# =============================================================================


def create_memory_store() -> MemoryStore:
    """Create a memory store."""
    return MemoryStore()


def create_optimization_engine(
    min_improvement: float = 0.1,
) -> OptimizationEngine:
    """Create an optimization engine."""
    return OptimizationEngine(min_improvement)


def create_refinery(
    memory_store: MemoryStore | None = None,
    engine: OptimizationEngine | None = None,
    max_candidates: int = 10,
    min_improvement: float = 0.1,
) -> HypnagogicRefinery:
    """Create a hypnagogic refinery."""
    return HypnagogicRefinery(
        memory_store=memory_store,
        engine=engine,
        max_candidates_per_cycle=max_candidates,
        min_improvement_threshold=min_improvement,
    )


def create_memory(
    content: str,
    kind: str = "code",
    **kwargs: Any,
) -> MemoryRecord:
    """Create a memory record."""
    return MemoryRecord(
        id=kwargs.get("id", f"mem-{uuid4().hex[:8]}"),
        kind=kind,
        content=content,
        size_bytes=len(content.encode("utf-8")),
        **{k: v for k, v in kwargs.items() if k != "id"},
    )
