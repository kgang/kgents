"""
H-gents Persistent Dialectic: DGent-backed dialectic history

Provides persistent tracking of dialectic synthesis across sessions.
This enables:
- Historical analysis of contradictions and resolutions
- Pattern recognition in recurring tensions
- Lineage tracking across multiple sessions
- Auditability of synthesis decisions

Architecture:
    HegelAgent (existing) + PersistentAgent[DialecticHistory]
    → PersistentDialecticAgent (D-gent backed)

Pattern: Wrapper that persists dialectic outputs after each synthesis.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from agents.d import PersistentAgent
from bootstrap.types import Agent

from .hegel import (
    DialecticInput,
    DialecticOutput,
    DialecticStep,
    HegelAgent,
)


@dataclass
class DialecticRecord:
    """
    A persisted dialectic synthesis record.

    Stores the full lineage and result of a dialectic operation.
    """

    thesis_repr: str  # String representation of thesis
    antithesis_repr: Optional[str]  # String representation of antithesis
    synthesis_repr: Optional[str]  # String representation of synthesis
    sublation_notes: str
    productive_tension: bool
    timestamp: str
    lineage: list[dict[str, Any]]  # Serialized DialecticSteps
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DialecticRecord:
        """Deserialize from dict."""
        return cls(
            thesis_repr=data["thesis_repr"],
            antithesis_repr=data.get("antithesis_repr"),
            synthesis_repr=data.get("synthesis_repr"),
            sublation_notes=data["sublation_notes"],
            productive_tension=data["productive_tension"],
            timestamp=data["timestamp"],
            lineage=data.get("lineage", []),
            metadata=data.get("metadata", {}),
        )


@dataclass
class DialecticHistory:
    """
    State schema for persistent dialectic history.

    Stores chronological record of all dialectic operations.
    """

    version: str = "1.0.0"
    records: list[dict[str, Any]] = field(
        default_factory=list
    )  # Serialized DialecticRecords

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for PersistentAgent."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DialecticHistory:
        """Deserialize from dict for PersistentAgent."""
        return cls(
            version=data.get("version", "1.0.0"), records=data.get("records", [])
        )


class PersistentDialecticAgent(Agent[DialecticInput, DialecticOutput]):
    """
    DGent-backed dialectic synthesis agent.

    Wraps HegelAgent with persistent state management via PersistentAgent.

    Benefits:
    - History of all dialectic operations across sessions
    - Pattern analysis: recurring tensions, synthesis types
    - Auditability: full lineage tracking
    - Temporal analysis: when tensions emerge/resolve
    """

    def __init__(
        self,
        history_path: Optional[Path] = None,
        hegel: Optional[HegelAgent] = None,
    ):
        # Resolve history path
        if history_path is None:
            history_path = Path.cwd() / ".dialectic_history.json"

        self._history_path = history_path
        self._hegel = hegel or HegelAgent()

        # Create PersistentAgent for state management
        self._dgent: PersistentAgent[DialecticHistory] = PersistentAgent(
            path=self._history_path,
            schema=DialecticHistory,
            max_history=100,  # Keep last 100 state snapshots
        )
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Initialize state if file doesn't exist (called lazily on first use)."""
        if self._initialized:
            return

        try:
            state = await self._dgent.load()
            if state is None:
                await self._dgent.save(DialecticHistory())
        except Exception:
            await self._dgent.save(DialecticHistory())

        self._initialized = True

    @property
    def name(self) -> str:
        return "PersistentDialecticAgent"

    async def invoke(self, input: DialecticInput) -> DialecticOutput:
        """
        Perform dialectic synthesis and persist the result.

        Delegates to HegelAgent for actual synthesis, then records
        the full operation in persistent history.
        """
        await self._ensure_initialized()

        # Perform synthesis
        output = await self._hegel.invoke(input)

        # Serialize the operation for persistence
        record = DialecticRecord(
            thesis_repr=repr(input.thesis),
            antithesis_repr=repr(input.antithesis) if input.antithesis else None,
            synthesis_repr=repr(output.synthesis) if output.synthesis else None,
            sublation_notes=output.sublation_notes,
            productive_tension=output.productive_tension,
            timestamp=datetime.now().isoformat(),
            lineage=[self._serialize_step(step) for step in output.lineage],
            metadata=output.metadata,
        )

        # Persist the record
        await self._record(record)

        return output

    def _serialize_step(self, step: DialecticStep) -> dict[str, Any]:
        """Serialize a DialecticStep for storage."""
        return {
            "stage": step.stage,
            "thesis": repr(step.thesis),
            "antithesis": repr(step.antithesis) if step.antithesis else None,
            "result": repr(step.result) if step.result else None,
            "notes": step.notes,
            "timestamp": step.timestamp,
        }

    async def _record(self, record: DialecticRecord) -> None:
        """Add record to history."""
        state = await self._dgent.load()
        if state is None:
            state = DialecticHistory()

        state.records.append(record.to_dict())
        await self._dgent.save(state)

    async def get_history(self) -> list[DialecticRecord]:
        """Get full dialectic history."""
        await self._ensure_initialized()
        state = await self._dgent.load()
        if state is None:
            return []

        return [DialecticRecord.from_dict(r) for r in state.records]

    async def get_recent_tensions(self, limit: int = 10) -> list[DialecticRecord]:
        """Get most recent dialectic operations."""
        history = await self.get_history()
        return history[-limit:] if len(history) > limit else history

    async def get_productive_tensions(self) -> list[DialecticRecord]:
        """Get all dialectic operations that resulted in held tension."""
        history = await self.get_history()
        return [r for r in history if r.productive_tension]

    async def get_synthesis_count(self) -> dict[str, int]:
        """Get count of synthesis vs held tension outcomes."""
        history = await self.get_history()
        return {
            "total": len(history),
            "synthesized": len([r for r in history if not r.productive_tension]),
            "held": len([r for r in history if r.productive_tension]),
        }

    async def get_state_history(self) -> list[DialecticHistory]:
        """Get state history from DGent."""
        return await self._dgent.history()


class DialecticMemoryAgent(Agent[str, list[DialecticRecord]]):
    """
    Query agent for dialectic history.

    Morphism: SearchQuery → list[DialecticRecord]

    Enables searching dialectic history by thesis/antithesis content.
    """

    def __init__(self, persistent_dialectic: PersistentDialecticAgent):
        self._dialectic = persistent_dialectic

    @property
    def name(self) -> str:
        return "DialecticMemoryAgent"

    async def invoke(self, query: str) -> list[DialecticRecord]:
        """
        Search dialectic history for matching records.

        Simple substring matching on thesis/antithesis representations.
        Future: could use vector embeddings for semantic search.
        """
        history = await self._dialectic.get_history()

        query_lower = query.lower()
        matches = []

        for record in history:
            # Search in thesis, antithesis, synthesis representations
            if (
                query_lower in record.thesis_repr.lower()
                or (
                    record.antithesis_repr
                    and query_lower in record.antithesis_repr.lower()
                )
                or (
                    record.synthesis_repr
                    and query_lower in record.synthesis_repr.lower()
                )
            ):
                matches.append(record)

        return matches


# Convenience factories


def persistent_dialectic_agent(
    history_path: Optional[Path] = None,
) -> PersistentDialecticAgent:
    """Create a DGent-backed dialectic agent."""
    return PersistentDialecticAgent(history_path)


def dialectic_memory_agent(
    persistent_dialectic: PersistentDialecticAgent,
) -> DialecticMemoryAgent:
    """Create a dialectic memory query agent."""
    return DialecticMemoryAgent(persistent_dialectic)
