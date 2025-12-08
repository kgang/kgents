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
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from bootstrap.types import Agent


@dataclass(frozen=True)
class ImprovementRecord:
    """
    A record of a past improvement attempt.

    Frozen for immutability - records should never be modified after creation.
    """
    module: str
    hypothesis_hash: str
    description: str
    outcome: str  # "accepted", "rejected", "held"
    timestamp: str
    rejection_reason: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "module": self.module,
            "hypothesis_hash": self.hypothesis_hash,
            "description": self.description,
            "outcome": self.outcome,
            "timestamp": self.timestamp,
            "rejection_reason": self.rejection_reason,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ImprovementRecord":
        """Create from dictionary."""
        return cls(
            module=data["module"],
            hypothesis_hash=data["hypothesis_hash"],
            description=data["description"],
            outcome=data["outcome"],
            timestamp=data["timestamp"],
            rejection_reason=data.get("rejection_reason"),
        )


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


@dataclass(frozen=True)
class RecordInput:
    """Input for recording a new improvement attempt."""
    module: str
    hypothesis: str
    description: str
    outcome: str  # "accepted", "rejected", "held"
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

    def __init__(self, history_path: Optional[Path] = None):
        self._history_path = history_path or (
            Path(__file__).parent.parent.parent / ".evolve_logs" / "improvement_history.json"
        )
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
        """Save history to disk."""
        self._history_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"records": [r.to_dict() for r in self._records]}
        with open(self._history_path, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def hash_hypothesis(hypothesis: str) -> str:
        """Create a normalized hash of a hypothesis."""
        # Normalize: lowercase, remove extra whitespace, hash
        normalized = " ".join(hypothesis.lower().split())
        return f"{hash(normalized) & 0xFFFFFFFF:08x}"

    def was_rejected(self, module: str, hypothesis: str) -> Optional[ImprovementRecord]:
        """Check if a similar hypothesis was previously rejected."""
        h = self.hash_hypothesis(hypothesis)
        for r in self._records:
            if r.module == module and r.hypothesis_hash == h and r.outcome == "rejected":
                return r
        return None

    def was_recently_accepted(
        self,
        module: str,
        hypothesis: str,
        days: int = 7
    ) -> bool:
        """Check if a similar improvement was recently accepted."""
        h = self.hash_hypothesis(hypothesis)
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        for r in self._records:
            if (r.module == module and
                r.hypothesis_hash == h and
                r.outcome == "accepted" and
                r.timestamp > cutoff):
                return True
        return False

    def record(
        self,
        module: str,
        hypothesis: str,
        description: str,
        outcome: str,
        rejection_reason: Optional[str] = None
    ) -> ImprovementRecord:
        """Record an improvement attempt."""
        record = ImprovementRecord(
            module=module,
            hypothesis_hash=self.hash_hypothesis(hypothesis),
            description=description,
            outcome=outcome,
            timestamp=datetime.now().isoformat(),
            rejection_reason=rejection_reason,
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

    def query(self, module: str, hypothesis: str, days_back: int = 7) -> MemoryQueryResult:
        """Query memory for a hypothesis."""
        rejection = self.was_rejected(module, hypothesis)
        recently_accepted = self.was_recently_accepted(module, hypothesis, days_back)

        return MemoryQueryResult(
            was_rejected=rejection is not None,
            rejection_record=rejection,
            was_recently_accepted=recently_accepted,
            should_skip=rejection is not None or recently_accepted,
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
            rejection_reason=input.rejection_reason,
        )


# Convenience factory
def memory_agent(history_path: Optional[Path] = None) -> MemoryAgent:
    """Create a memory agent with optional custom history path."""
    memory = ImprovementMemory(history_path)
    return MemoryAgent(memory)
