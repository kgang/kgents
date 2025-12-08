"""
Improvement Memory Agent: Persistent memory of past improvement attempts.

Tracks accepted/rejected improvements to:
1. Avoid re-proposing similar rejected ideas
2. Track patterns of successful improvements
3. Enable learning from history

This agent provides the memory layer for the evolution pipeline,
ensuring we don't waste cycles re-trying ideas that already failed.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Union

from bootstrap.types import Agent


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings.

    Returns the minimum number of single-character edits (insertions,
    deletions, or substitutions) required to change one string into another.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def similarity_ratio(s1: str, s2: str) -> float:
    """
    Calculate similarity ratio between two strings using Levenshtein distance.

    Returns a float between 0.0 and 1.0, where 1.0 is identical.
    Normalizes both strings before comparison (lowercase, whitespace).
    """
    # Normalize strings
    s1_norm = " ".join(s1.lower().split())
    s2_norm = " ".join(s2.lower().split())

    if s1_norm == s2_norm:
        return 1.0

    distance = levenshtein_distance(s1_norm, s2_norm)
    max_len = max(len(s1_norm), len(s2_norm))

    if max_len == 0:
        return 1.0

    return 1.0 - (distance / max_len)


@dataclass(frozen=True)
class ImprovementRecord:
    """
    A record of a past improvement attempt.

    Frozen for immutability - records should never be modified after creation.
    """
    module: str
    hypothesis: str  # Full hypothesis text (spec requirement)
    description: str
    outcome: str  # "accepted", "rejected", "held"
    timestamp: str
    rationale: Optional[str] = None  # Why it was accepted/rejected/held (spec requirement)
    rejection_reason: Optional[str] = None  # Specific error/reason for rejection
    hypothesis_hash: Optional[str] = None  # For backward compatibility

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "module": self.module,
            "hypothesis": self.hypothesis,
            "description": self.description,
            "outcome": self.outcome,
            "timestamp": self.timestamp,
            "rationale": self.rationale,
            "rejection_reason": self.rejection_reason,
            # Include hash for backward compatibility
            "hypothesis_hash": self.hypothesis_hash or hash_hypothesis(self.hypothesis),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ImprovementRecord":
        """Create from dictionary, supporting both old and new formats."""
        # Support old format (hypothesis_hash only) for backward compatibility
        if "hypothesis" not in data and "hypothesis_hash" in data:
            # Old format - use hash as placeholder
            hypothesis = f"[legacy record {data['hypothesis_hash']}]"
        else:
            hypothesis = data.get("hypothesis", "")

        return cls(
            module=data["module"],
            hypothesis=hypothesis,
            description=data["description"],
            outcome=data["outcome"],
            timestamp=data["timestamp"],
            rationale=data.get("rationale"),
            rejection_reason=data.get("rejection_reason"),
            hypothesis_hash=data.get("hypothesis_hash"),
        )


def hash_hypothesis(hypothesis: str) -> str:
    """Create a normalized hash of a hypothesis."""
    # Normalize: lowercase, remove extra whitespace, hash
    normalized = " ".join(hypothesis.lower().split())
    return f"{hash(normalized) & 0xFFFFFFFF:08x}"


@dataclass(frozen=True)
class MemoryQuery:
    """Query input for memory lookups."""
    module: str
    hypothesis: str
    check_rejected: bool = True
    check_accepted: bool = True
    days_back: int = 7


@dataclass(frozen=True)
class MemoryQueryResult:
    """Result of a memory query."""
    was_rejected: bool
    rejection_record: Optional[ImprovementRecord] = None
    was_recently_accepted: bool = False
    should_skip: bool = False
    similarity: float = 0.0  # Similarity score 0.0 to 1.0 (spec requirement)


@dataclass(frozen=True)
class RecordInput:
    """Input for recording a new improvement attempt."""
    module: str
    hypothesis: str
    description: str
    outcome: str  # "accepted", "rejected", "held"
    rationale: Optional[str] = None  # Why it was accepted/rejected/held (spec requirement)
    rejection_reason: Optional[str] = None


class ImprovementMemory:
    """
    Persistent memory of past improvements.

    Stores accepted/rejected improvements to:
    1. Avoid re-proposing similar rejected ideas
    2. Track patterns of successful improvements
    3. Enable learning from history

    Note: This is a stateful class, not a pure Agent. It manages
    persistent storage and provides query methods.
    """

    def __init__(
        self,
        history_path: Optional[Path] = None,
        similarity_threshold: float = 0.8  # Spec requirement: 80% similarity threshold
    ):
        # Default to spec-compliant path, but allow override for backward compatibility
        if history_path is None:
            # Try spec path first (.evolve_memory.json in working directory)
            spec_path = Path.cwd() / ".evolve_memory.json"

            # Also check legacy path (relative to this file)
            legacy_path = Path(__file__).parent.parent.parent / ".evolve_logs" / "improvement_history.json"

            # Priority:
            # 1. If spec path exists, use it
            # 2. Else if legacy path exists, use it (backward compatibility)
            # 3. Else use spec path (new installation)
            if spec_path.exists():
                self._history_path = spec_path
            elif legacy_path.exists():
                self._history_path = legacy_path
            else:
                self._history_path = spec_path
        else:
            self._history_path = history_path

        self._similarity_threshold = similarity_threshold
        self._records: list[ImprovementRecord] = []
        self._load()

    def _load(self) -> None:
        """Load history from disk."""
        if self._history_path.exists():
            try:
                with open(self._history_path) as f:
                    data = json.load(f)
                self._records = [
                    ImprovementRecord.from_dict(r) for r in data.get("records", [])
                ]
            except (json.JSONDecodeError, KeyError):
                self._records = []

    def _save(self) -> None:
        """Save history to disk in spec-compliant format."""
        self._history_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0.0",  # Spec requirement
            "records": [r.to_dict() for r in self._records]
        }
        with open(self._history_path, "w") as f:
            json.dump(data, f, indent=2)

    def was_rejected(
        self,
        module: str,
        hypothesis: str,
        return_similarity: bool = False
    ) -> Union[Optional[ImprovementRecord], tuple[Optional[ImprovementRecord], float]]:
        """
        Check if a similar hypothesis was previously rejected.

        Uses fuzzy matching with Levenshtein distance (spec requirement).

        Args:
            module: Module name to check
            hypothesis: Hypothesis text to check
            return_similarity: If True, return (record, similarity) tuple

        Returns:
            The rejection record if found (and similarity >= threshold), or None.
            If return_similarity=True, returns (record, max_similarity) tuple.
        """
        best_match: Optional[ImprovementRecord] = None
        max_similarity = 0.0

        for r in self._records:
            if r.module == module and r.outcome == "rejected":
                similarity = similarity_ratio(hypothesis, r.hypothesis)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = r

        # Only return match if it exceeds threshold
        if max_similarity >= self._similarity_threshold:
            if return_similarity:
                return (best_match, max_similarity)
            return best_match

        if return_similarity:
            return (None, max_similarity)
        return None

    def was_recently_accepted(
        self,
        module: str,
        hypothesis: str,
        days: int = 7
    ) -> bool:
        """
        Check if a similar improvement was recently accepted.

        Uses fuzzy matching with Levenshtein distance (spec requirement).
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        for r in self._records:
            if (r.module == module and
                r.outcome == "accepted" and
                r.timestamp > cutoff):
                # Use fuzzy matching
                similarity = similarity_ratio(hypothesis, r.hypothesis)
                if similarity >= self._similarity_threshold:
                    return True
        return False

    def record(
        self,
        module: str,
        hypothesis: str,
        description: str,
        outcome: str,
        rationale: Optional[str] = None,
        rejection_reason: Optional[str] = None
    ) -> ImprovementRecord:
        """
        Record an improvement attempt.

        Args:
            module: Module name
            hypothesis: Full hypothesis text (spec requirement)
            description: Description of the improvement
            outcome: "accepted", "rejected", or "held"
            rationale: Why it was accepted/rejected/held (spec requirement)
            rejection_reason: Specific error/reason for rejection

        Returns:
            The created ImprovementRecord
        """
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
        self._records.append(record)
        self._save()
        return record

    def get_success_patterns(self, module: str) -> dict[str, int]:
        """Get counts of successful improvement types for a module."""
        patterns: dict[str, int] = {}
        for r in self._records:
            if r.module == module and r.outcome == "accepted":
                # Extract type from description if possible
                patterns[r.description[:50]] = patterns.get(r.description[:50], 0) + 1
        return patterns

    def get_failure_patterns(
        self,
        module: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Get failure patterns for a module or all modules (spec requirement).

        Args:
            module: Module name to filter by, or None for all modules

        Returns:
            List of pattern dicts with:
            - pattern: failure type/category
            - count: number of occurrences
            - examples: list of example rejection reasons
        """
        # Group by rejection reason pattern
        pattern_groups: dict[str, list[str]] = defaultdict(list)

        for r in self._records:
            if r.outcome != "rejected":
                continue

            if module is not None and r.module != module:
                continue

            if r.rejection_reason:
                # Extract pattern type from rejection reason
                pattern_type = self._categorize_failure(r.rejection_reason)
                pattern_groups[pattern_type].append(r.rejection_reason)

        # Convert to list format as per spec (lines 233-254)
        patterns = []
        for pattern_type, examples in pattern_groups.items():
            patterns.append({
                "pattern": pattern_type,
                "count": len(examples),
                "examples": examples[:5]  # Limit to 5 examples as per spec
            })

        # Sort by count (most common first)
        patterns.sort(key=lambda p: p["count"], reverse=True)
        return patterns

    def get_stats(self) -> dict[str, Any]:
        """
        Get comprehensive statistics about memory (spec requirement).

        Returns stats as per spec lines 531-558:
        - total_records: Total number of records
        - accepted/rejected/held: Counts by outcome
        - modules: Per-module breakdown
        - rejection_reasons: Breakdown of rejection reasons
        """
        total = len(self._records)
        by_outcome = Counter(r.outcome for r in self._records)

        # Per-module stats
        modules: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for r in self._records:
            modules[r.module][r.outcome] += 1

        # Rejection reason categorization
        rejection_reasons: dict[str, int] = Counter()
        for r in self._records:
            if r.outcome == "rejected" and r.rejection_reason:
                category = self._categorize_failure(r.rejection_reason)
                rejection_reasons[category] += 1

        return {
            "total_records": total,
            "accepted": by_outcome.get("accepted", 0),
            "rejected": by_outcome.get("rejected", 0),
            "held": by_outcome.get("held", 0),
            "modules": dict(modules),
            "rejection_reasons": dict(rejection_reasons),
        }

    def _categorize_failure(self, rejection_reason: str) -> str:
        """
        Categorize a rejection reason into a pattern type.

        Categories:
        - Test failure
        - Type error
        - Syntax error
        - Import error
        - Principle violation
        - Other
        """
        reason_lower = rejection_reason.lower()

        # Check for principle violations first (includes CodeJudge verdicts)
        if any(word in reason_lower for word in [
            "principle", "composability", "violates", "codejudge", "global state",
            "side effect", "purity", "immutability"
        ]):
            return "Principle violation"

        if any(word in reason_lower for word in ["test", "pytest", "assertion"]):
            return "Test failure"
        if any(word in reason_lower for word in ["type", "mypy", "annotation"]):
            return "Type error"
        if any(word in reason_lower for word in ["syntax", "indent", "invalid syntax"]):
            return "Syntax error"
        if any(word in reason_lower for word in ["import", "module not found", "cannot import"]):
            return "Import error"

        return "Other"

    def query(self, module: str, hypothesis: str, days_back: int = 7) -> MemoryQueryResult:
        """
        Query memory for a hypothesis.

        Returns result with similarity score (spec requirement).
        """
        rejection, rejection_similarity = self.was_rejected(module, hypothesis, return_similarity=True)
        recently_accepted = self.was_recently_accepted(module, hypothesis, days_back)

        # Calculate max similarity across all records
        max_similarity = rejection_similarity if rejection else 0.0

        return MemoryQueryResult(
            was_rejected=rejection is not None,
            rejection_record=rejection,
            was_recently_accepted=recently_accepted,
            should_skip=rejection is not None or recently_accepted,
            similarity=max_similarity,
        )


class MemoryAgent(Agent[MemoryQuery, MemoryQueryResult]):
    """
    Agent wrapper around ImprovementMemory for composition.

    Morphism: MemoryQuery → MemoryQueryResult

    Usage:
        memory_agent = MemoryAgent()
        result = await memory_agent.invoke(MemoryQuery(
            module="types",
            hypothesis="Add __hash__ to Agent base class"
        ))
        if result.should_skip:
            print("Skipping - previously processed")
    """

    def __init__(self, memory: Optional[ImprovementMemory] = None):
        self._memory = memory or ImprovementMemory()

    @property
    def name(self) -> str:
        return "MemoryAgent"

    @property
    def memory(self) -> ImprovementMemory:
        """Access underlying memory for recording."""
        return self._memory

    async def invoke(self, input: MemoryQuery) -> MemoryQueryResult:
        """Query the improvement memory."""
        return self._memory.query(
            module=input.module,
            hypothesis=input.hypothesis,
            days_back=input.days_back,
        )


class RecordAgent(Agent[RecordInput, ImprovementRecord]):
    """
    Agent for recording improvement outcomes.

    Morphism: RecordInput → ImprovementRecord

    Usage:
        recorder = RecordAgent(memory)
        record = await recorder.invoke(RecordInput(
            module="types",
            hypothesis="Add __hash__",
            description="Added __hash__ to Agent",
            outcome="accepted"
        ))
    """

    def __init__(self, memory: ImprovementMemory):
        self._memory = memory

    @property
    def name(self) -> str:
        return "RecordAgent"

    async def invoke(self, input: RecordInput) -> ImprovementRecord:
        """Record an improvement outcome."""
        return self._memory.record(
            module=input.module,
            hypothesis=input.hypothesis,
            description=input.description,
            outcome=input.outcome,
            rationale=input.rationale,
            rejection_reason=input.rejection_reason,
        )


# Convenience factory
def memory_agent(history_path: Optional[Path] = None) -> MemoryAgent:
    """Create a memory agent with optional custom history path."""
    memory = ImprovementMemory(history_path)
    return MemoryAgent(memory)
