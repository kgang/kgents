"""
E-gents Persistent Memory: DGent-backed ImprovementMemory

Migrates ImprovementMemory to use D-gent infrastructure for state management.
This provides:
- Consistent state serialization with other genera
- History tracking via D-gent protocol
- Potential for future enhancements (caching, vector search)

Architecture:
    ImprovementMemory (existing) + PersistentAgent[MemoryState]
    → PersistentMemoryAgent (D-gent backed)

Pattern: Wrapper over existing ImprovementMemory, using PersistentAgent
for state storage instead of manual JSON handling.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from agents.d import PersistentAgent

from .memory import (
    ImprovementRecord,
    MemoryQueryResult,
    similarity_ratio,
)


@dataclass
class MemoryState:
    """
    State schema for persistent improvement memory.

    This replaces manual JSON format in ImprovementMemory with
    a structured dataclass that PersistentAgent can serialize.
    """

    version: str = "1.0.0"
    records: list[dict[str, Any]] = field(
        default_factory=list
    )  # Serialized ImprovementRecords

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for PersistentAgent."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryState:
        """Deserialize from dict for PersistentAgent."""
        return cls(
            version=data.get("version", "1.0.0"), records=data.get("records", [])
        )


class PersistentMemoryAgent:
    """
    DGent-backed improvement memory.

    Provides same interface as ImprovementMemory but uses
    PersistentAgent[MemoryState] for state management.

    Benefits over manual JSON:
    - Consistent state management with other genera
    - Automatic history tracking
    - Crash-safe atomic writes
    - Future: can swap to CachedAgent, VectorAgent, etc.
    """

    def __init__(
        self,
        history_path: Optional[Path] = None,
        similarity_threshold: float = 0.8,
    ):
        # Resolve history path with same logic as ImprovementMemory
        if history_path is None:
            spec_path = Path.cwd() / ".evolve_memory.json"
            legacy_path = (
                Path(__file__).parent.parent.parent
                / ".evolve_logs"
                / "improvement_history.json"
            )

            if spec_path.exists():
                history_path = spec_path
            elif legacy_path.exists():
                history_path = legacy_path
            else:
                history_path = spec_path

        self._history_path = history_path
        self._similarity_threshold = similarity_threshold

        # Create PersistentAgent for state management
        self._dgent: PersistentAgent[MemoryState] = PersistentAgent(
            path=self._history_path,
            schema=MemoryState,
            max_history=50,  # Keep last 50 state snapshots
        )
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Initialize state if file doesn't exist (called lazily on first use)."""
        if self._initialized:
            return

        try:
            # Try to load - if it fails, initialize
            state = await self._dgent.load()
            if state is None:
                await self._dgent.save(MemoryState())
        except Exception:
            # File doesn't exist or corrupt - initialize
            await self._dgent.save(MemoryState())

        self._initialized = True

    async def _get_state(self) -> MemoryState:
        """Get current state from DGent."""
        await self._ensure_initialized()
        state = await self._dgent.load()
        return state if state else MemoryState()

    async def _set_state(self, state: MemoryState) -> None:
        """Save state via DGent."""
        await self._dgent.save(state)

    def _parse_records(self, state: MemoryState) -> list[ImprovementRecord]:
        """Parse records from state."""
        return [ImprovementRecord.from_dict(r) for r in state.records]

    async def was_rejected(
        self, module: str, hypothesis: str, return_similarity: bool = False
    ) -> Optional[ImprovementRecord] | tuple[Optional[ImprovementRecord], float]:
        """
        Check if similar hypothesis was previously rejected.

        Uses fuzzy matching with Levenshtein distance.
        """
        state = await self._get_state()
        records = self._parse_records(state)

        best_match: Optional[ImprovementRecord] = None
        max_similarity = 0.0

        for r in records:
            if r.module == module and r.outcome == "rejected":
                similarity = similarity_ratio(hypothesis, r.hypothesis)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = r

        # Only return match if exceeds threshold
        if max_similarity >= self._similarity_threshold:
            if return_similarity:
                return (best_match, max_similarity)
            return best_match

        if return_similarity:
            return (None, max_similarity)
        return None

    async def was_recently_accepted(
        self, module: str, hypothesis: str, days: int = 7
    ) -> bool:
        """Check if similar improvement was recently accepted."""
        from datetime import timedelta

        state = await self._get_state()
        records = self._parse_records(state)

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        for r in records:
            if r.module == module and r.outcome == "accepted" and r.timestamp > cutoff:
                similarity = similarity_ratio(hypothesis, r.hypothesis)
                if similarity >= self._similarity_threshold:
                    return True
        return False

    async def record(
        self,
        module: str,
        hypothesis: str,
        description: str,
        outcome: str,
        rationale: Optional[str] = None,
        rejection_reason: Optional[str] = None,
    ) -> ImprovementRecord:
        """Record an improvement attempt."""
        from .memory import hash_hypothesis

        record = ImprovementRecord(
            module=module,
            hypothesis=hypothesis,
            description=description,
            outcome=outcome,
            timestamp=datetime.now().isoformat(),
            rationale=rationale,
            rejection_reason=rejection_reason,
            hypothesis_hash=hash_hypothesis(hypothesis),
        )

        # Update state
        state = await self._get_state()
        state.records.append(record.to_dict())
        await self._set_state(state)

        return record

    async def get_success_patterns(self, module: str) -> dict[str, int]:
        """Get counts of successful improvement types for a module."""
        state = await self._get_state()
        records = self._parse_records(state)

        patterns: dict[str, int] = {}
        for r in records:
            if r.module == module and r.outcome == "accepted":
                patterns[r.description[:50]] = patterns.get(r.description[:50], 0) + 1
        return patterns

    async def get_failure_patterns(
        self, module: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Get failure patterns for module or all modules."""
        from collections import defaultdict
        from .memory import ImprovementMemory

        state = await self._get_state()
        records = self._parse_records(state)

        # Group by rejection reason pattern
        pattern_groups: dict[str, list[str]] = defaultdict(list)

        # Use categorization from ImprovementMemory
        temp_memory = ImprovementMemory()  # Just for categorization method

        for r in records:
            if r.outcome != "rejected":
                continue

            if module is not None and r.module != module:
                continue

            if r.rejection_reason:
                pattern_type = temp_memory._categorize_failure(r.rejection_reason)
                pattern_groups[pattern_type].append(r.rejection_reason)

        # Convert to list format
        patterns = []
        for pattern_type, examples in pattern_groups.items():
            patterns.append(
                {
                    "pattern": pattern_type,
                    "count": len(examples),
                    "examples": examples[:5],
                }
            )

        patterns.sort(key=lambda p: p["count"], reverse=True)
        return patterns

    async def get_stats(self) -> dict[str, Any]:
        """Get comprehensive statistics about memory."""
        from collections import Counter, defaultdict
        from .memory import ImprovementMemory

        state = await self._get_state()
        records = self._parse_records(state)

        total = len(records)
        by_outcome = Counter(r.outcome for r in records)

        # Per-module stats
        modules: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for r in records:
            modules[r.module][r.outcome] += 1

        # Rejection reason categorization
        temp_memory = ImprovementMemory()
        rejection_reasons: dict[str, int] = Counter()
        for r in records:
            if r.outcome == "rejected" and r.rejection_reason:
                category = temp_memory._categorize_failure(r.rejection_reason)
                rejection_reasons[category] += 1

        return {
            "total_records": total,
            "accepted": by_outcome.get("accepted", 0),
            "rejected": by_outcome.get("rejected", 0),
            "held": by_outcome.get("held", 0),
            "modules": dict(modules),
            "rejection_reasons": dict(rejection_reasons),
        }

    async def query(
        self, module: str, hypothesis: str, days_back: int = 7
    ) -> MemoryQueryResult:
        """Query memory for a hypothesis."""
        rejection, rejection_similarity = await self.was_rejected(
            module, hypothesis, return_similarity=True
        )
        recently_accepted = await self.was_recently_accepted(
            module, hypothesis, days_back
        )

        max_similarity = rejection_similarity if rejection else 0.0

        return MemoryQueryResult(
            was_rejected=rejection is not None,
            rejection_record=rejection,
            was_recently_accepted=recently_accepted,
            should_skip=rejection is not None or recently_accepted,
            similarity=max_similarity,
        )

    async def get_history(self) -> list[MemoryState]:
        """Get state history from DGent."""
        return await self._dgent.history()


# Convenience factory
def persistent_memory_agent(
    history_path: Optional[Path] = None,
) -> PersistentMemoryAgent:
    """Create a DGent-backed memory agent."""
    return PersistentMemoryAgent(history_path)
