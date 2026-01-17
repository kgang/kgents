"""
Stigmergic Memory: Learning from Skill Usage Traces

Stigmergy is indirect coordination through environmental modification.
Skills leave traces when used. Good outcomes strengthen paths.
Bad outcomes weaken them. The system learns what works.

Philosophy:
    "Learn from what worked, forget what didn't."
    "Traces inform future activation."
    "The environment remembers."

AGENTESE: self.skill.memory
"""

from __future__ import annotations

import hashlib
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from .types import (
    SkillComposition,
    SkillUsageTrace,
    UsageOutcome,
)

logger = logging.getLogger(__name__)


@dataclass
class UsageStats:
    """Statistics for a skill's usage history."""

    total_uses: int = 0
    successes: int = 0
    partials: int = 0
    failures: int = 0
    skipped: int = 0
    total_duration_seconds: float = 0.0
    last_used: datetime | None = None
    contexts_used: set[str] = field(default_factory=set)

    @property
    def success_rate(self) -> float | None:
        """Compute success rate (successes / total_uses)."""
        if self.total_uses == 0:
            return None
        return (self.successes + 0.5 * self.partials) / self.total_uses

    @property
    def average_duration(self) -> float:
        """Average duration in seconds."""
        if self.total_uses == 0:
            return 0.0
        return self.total_duration_seconds / self.total_uses


@dataclass
class CompositionStats:
    """Statistics for skill composition usage."""

    composition_key: str  # Sorted tuple of skill IDs as string
    skill_ids: tuple[str, ...]
    usage_count: int = 0
    success_count: int = 0
    contexts: set[str] = field(default_factory=set)


class StigmergicMemory:
    """
    Memory system for skill usage traces.

    Tracks which skills were used in what contexts with what outcomes.
    Provides signals for the activation engine to boost or penalize skills.

    Teaching:
        gotcha: Memory decays over time. Recent successes matter more.
                Use `prune_old_traces` to remove stale data.
                (Evidence: test_stigmergic_memory.py::test_decay)

        gotcha: Context hash is computed from task description + active files.
                Similar contexts should produce similar hashes.
                (Evidence: test_stigmergic_memory.py::test_context_hash)

        gotcha: Call `record_usage` AFTER the skill is actually used.
                Don't record at activation time - record at completion.
                (Evidence: test_stigmergic_memory.py::test_record_timing)
    """

    def __init__(self, max_traces_per_skill: int = 100, decay_days: int = 30) -> None:
        """
        Initialize stigmergic memory.

        Args:
            max_traces_per_skill: Maximum traces to keep per skill
            decay_days: Days after which traces are pruned
        """
        self._traces: dict[str, list[SkillUsageTrace]] = defaultdict(list)
        self._stats: dict[str, UsageStats] = {}
        self._composition_stats: dict[str, CompositionStats] = {}
        self._max_traces = max_traces_per_skill
        self._decay_days = decay_days

    def record_usage(self, trace: SkillUsageTrace) -> None:
        """
        Record a skill usage trace.

        Args:
            trace: The usage trace to record
        """
        skill_id = trace.skill_id

        # Add to traces
        self._traces[skill_id].append(trace)

        # Prune if over limit
        if len(self._traces[skill_id]) > self._max_traces:
            self._traces[skill_id] = self._traces[skill_id][-self._max_traces :]

        # Update stats
        if skill_id not in self._stats:
            self._stats[skill_id] = UsageStats()

        stats = self._stats[skill_id]
        stats.total_uses += 1
        stats.total_duration_seconds += trace.duration_seconds
        stats.last_used = trace.timestamp
        stats.contexts_used.add(trace.context_hash)

        if trace.outcome == UsageOutcome.SUCCESS:
            stats.successes += 1
        elif trace.outcome == UsageOutcome.PARTIAL:
            stats.partials += 1
        elif trace.outcome == UsageOutcome.FAILURE:
            stats.failures += 1
        elif trace.outcome == UsageOutcome.SKIPPED:
            stats.skipped += 1

        logger.debug(f"Recorded usage: {skill_id} -> {trace.outcome.value}")

    def record_composition_usage(
        self,
        skill_ids: tuple[str, ...],
        context_hash: str,
        success: bool,
    ) -> None:
        """
        Record usage of a skill composition.

        Compositions that are frequently used together can be
        suggested as pre-defined compositions.

        Args:
            skill_ids: The skills used together
            context_hash: Hash of the context
            success: Whether the composition was successful
        """
        # Create stable key from sorted skill IDs
        key = ",".join(sorted(skill_ids))

        if key not in self._composition_stats:
            self._composition_stats[key] = CompositionStats(
                composition_key=key,
                skill_ids=tuple(sorted(skill_ids)),
            )

        stats = self._composition_stats[key]
        stats.usage_count += 1
        if success:
            stats.success_count += 1
        stats.contexts.add(context_hash)

        logger.debug(f"Recorded composition usage: {key}")

    def get_success_rate(self, skill_id: str) -> float | None:
        """
        Get the success rate for a skill.

        Args:
            skill_id: The skill ID

        Returns:
            Success rate (0.0-1.0) or None if no data
        """
        if skill_id not in self._stats:
            return None
        return self._stats[skill_id].success_rate

    def get_usage_stats(self, skill_id: str) -> UsageStats | None:
        """
        Get usage statistics for a skill.

        Args:
            skill_id: The skill ID

        Returns:
            Usage stats or None if no data
        """
        return self._stats.get(skill_id)

    def get_traces(
        self,
        skill_id: str,
        limit: int = 10,
        outcome: UsageOutcome | None = None,
    ) -> list[SkillUsageTrace]:
        """
        Get recent traces for a skill.

        Args:
            skill_id: The skill ID
            limit: Maximum traces to return
            outcome: Filter by outcome (optional)

        Returns:
            List of traces (most recent first)
        """
        traces = self._traces.get(skill_id, [])

        if outcome is not None:
            traces = [t for t in traces if t.outcome == outcome]

        return traces[-limit:][::-1]  # Most recent first

    def suggest_compositions(self, min_usage: int = 3) -> list[SkillComposition]:
        """
        Suggest skill compositions based on usage patterns.

        Looks for skills that are frequently used together.

        Args:
            min_usage: Minimum usage count to suggest

        Returns:
            List of suggested compositions
        """
        suggestions = []

        for key, stats in self._composition_stats.items():
            if stats.usage_count >= min_usage and len(stats.skill_ids) >= 2:
                # Only suggest if success rate is decent
                success_rate = stats.success_count / stats.usage_count
                if success_rate >= 0.5:
                    suggestions.append(
                        SkillComposition(
                            id=f"suggested-{key}",
                            name=f"Suggested: {', '.join(stats.skill_ids[:3])}...",
                            skill_ids=stats.skill_ids,
                            description=f"Used together {stats.usage_count} times",
                            usage_count=stats.usage_count,
                        )
                    )

        # Sort by usage count descending
        suggestions.sort(key=lambda c: c.usage_count, reverse=True)
        return suggestions

    def get_similar_contexts(self, context_hash: str, skill_id: str) -> list[SkillUsageTrace]:
        """
        Find traces with similar contexts.

        Args:
            context_hash: The context hash to match
            skill_id: The skill ID

        Returns:
            Traces with matching context hash
        """
        return [t for t in self._traces.get(skill_id, []) if t.context_hash == context_hash]

    def prune_old_traces(self, before: datetime | None = None) -> int:
        """
        Remove traces older than the decay period.

        Args:
            before: Prune traces before this time (default: now - decay_days)

        Returns:
            Number of traces pruned
        """
        if before is None:
            before = datetime.now(UTC) - timedelta(days=self._decay_days)

        pruned = 0
        for skill_id in list(self._traces.keys()):
            original_count = len(self._traces[skill_id])
            self._traces[skill_id] = [t for t in self._traces[skill_id] if t.timestamp >= before]
            pruned += original_count - len(self._traces[skill_id])

            # Remove empty entries
            if not self._traces[skill_id]:
                del self._traces[skill_id]

        logger.debug(f"Pruned {pruned} old traces")
        return pruned

    def stats_summary(self) -> dict[str, Any]:
        """
        Get a summary of memory statistics.

        Returns:
            Dictionary with memory stats
        """
        total_traces = sum(len(t) for t in self._traces.values())
        skills_with_data = len(self._stats)

        # Find most used skills
        top_skills = sorted(
            self._stats.items(),
            key=lambda x: x[1].total_uses,
            reverse=True,
        )[:5]

        return {
            "total_traces": total_traces,
            "skills_with_data": skills_with_data,
            "compositions_tracked": len(self._composition_stats),
            "top_skills": [
                {
                    "skill_id": sid,
                    "total_uses": stats.total_uses,
                    "success_rate": stats.success_rate,
                }
                for sid, stats in top_skills
            ],
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize memory to dictionary (for persistence).

        Returns:
            Dictionary representation
        """
        return {
            "traces": {
                skill_id: [t.to_dict() for t in traces] for skill_id, traces in self._traces.items()
            },
            "stats": {
                skill_id: {
                    "total_uses": s.total_uses,
                    "successes": s.successes,
                    "partials": s.partials,
                    "failures": s.failures,
                    "skipped": s.skipped,
                    "total_duration_seconds": s.total_duration_seconds,
                    "last_used": s.last_used.isoformat() if s.last_used else None,
                    "contexts_used": list(s.contexts_used),
                }
                for skill_id, s in self._stats.items()
            },
            "composition_stats": {
                key: {
                    "skill_ids": list(cs.skill_ids),
                    "usage_count": cs.usage_count,
                    "success_count": cs.success_count,
                    "contexts": list(cs.contexts),
                }
                for key, cs in self._composition_stats.items()
            },
        }


def compute_context_hash(task: str, files: tuple[str, ...] = ()) -> str:
    """
    Compute a hash for a context.

    Similar contexts should produce similar hashes.

    Args:
        task: The task description
        files: Active files

    Returns:
        Context hash
    """
    # Normalize task: lowercase, remove extra whitespace
    normalized_task = " ".join(task.lower().split())

    # Sort files for consistency
    sorted_files = sorted(files)

    # Create hash content
    content = f"{normalized_task}|{','.join(sorted_files)}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


# Global memory instance
_memory: StigmergicMemory | None = None


def get_stigmergic_memory() -> StigmergicMemory:
    """Get the global stigmergic memory instance."""
    global _memory
    if _memory is None:
        _memory = StigmergicMemory()
    return _memory


def set_stigmergic_memory(memory: StigmergicMemory) -> None:
    """Set the global stigmergic memory instance (for testing)."""
    global _memory
    _memory = memory


def reset_stigmergic_memory() -> None:
    """Reset the global stigmergic memory (for testing)."""
    global _memory
    _memory = None


__all__ = [
    "CompositionStats",
    "StigmergicMemory",
    "UsageStats",
    "compute_context_hash",
    "get_stigmergic_memory",
    "reset_stigmergic_memory",
    "set_stigmergic_memory",
]
