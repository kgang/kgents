"""
ValidationStore: Persistence for validation runs.

Design:
- Append-only ledger pattern (like CrystalStore)
- JSONL persistence for simplicity
- Secondary indices for common queries

See: docs/skills/crown-jewel-patterns.md (Pattern 7: Append-Only History)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .schema import (
    Direction,
    GateCondition,
    GateId,
    GateResult,
    Initiative,
    InitiativeId,
    MetricType,
    PhaseId,
    PropositionId,
    PropositionResult,
    ValidationRun,
)

logger = logging.getLogger("kgents.validation.store")

# =============================================================================
# Exceptions
# =============================================================================


class ValidationStoreError(Exception):
    """Base exception for validation store errors."""

    pass


class ValidationRunNotFoundError(ValidationStoreError):
    """Raised when a validation run is not found."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        super().__init__(f"Validation run {run_id} not found")


# =============================================================================
# Query Types
# =============================================================================


@dataclass(frozen=True)
class ValidationRunQuery:
    """
    Query parameters for validation run retrieval.

    All parameters are optional. Multiple parameters combine with AND logic.
    """

    # Initiative filter
    initiative_id: InitiativeId | None = None

    # Phase filter
    phase_id: PhaseId | None = None

    # Time range
    after: datetime | None = None
    before: datetime | None = None

    # Pass/fail filter
    passed: bool | None = None

    # Limit and offset for pagination
    limit: int | None = None
    offset: int = 0

    def matches(self, run: ValidationRun) -> bool:
        """Check if a validation run matches this query."""
        # Initiative filter
        if self.initiative_id is not None and run.initiative_id != self.initiative_id:
            return False

        # Phase filter
        if self.phase_id is not None and run.phase_id != self.phase_id:
            return False

        # Time range
        if self.after and run.timestamp <= self.after:
            return False
        if self.before and run.timestamp >= self.before:
            return False

        # Pass/fail filter
        if self.passed is not None and run.passed != self.passed:
            return False

        return True


# =============================================================================
# Serialization
# =============================================================================


def _serialize_datetime(dt: datetime) -> str:
    """Serialize datetime to ISO format."""
    return dt.isoformat()


def _deserialize_datetime(s: str) -> datetime:
    """Deserialize datetime from ISO format."""
    return datetime.fromisoformat(s)


def _serialize_proposition_result(result: PropositionResult) -> dict[str, Any]:
    """Serialize a PropositionResult to dict."""
    return {
        "proposition_id": str(result.proposition_id),
        "value": result.value,
        "passed": result.passed,
        "timestamp": _serialize_datetime(result.timestamp),
        "mark_id": str(result.mark_id) if result.mark_id else None,
    }


def _deserialize_proposition_result(data: dict[str, Any]) -> PropositionResult:
    """Deserialize a PropositionResult from dict."""
    from .schema import MarkId

    return PropositionResult(
        proposition_id=PropositionId(data["proposition_id"]),
        value=data.get("value"),
        passed=data["passed"],
        timestamp=_deserialize_datetime(data["timestamp"]),
        mark_id=MarkId(data["mark_id"]) if data.get("mark_id") else None,
    )


def _serialize_gate_result(result: GateResult) -> dict[str, Any]:
    """Serialize a GateResult to dict."""
    return {
        "gate_id": str(result.gate_id),
        "proposition_results": [
            _serialize_proposition_result(pr) for pr in result.proposition_results
        ],
        "passed": result.passed,
        "timestamp": _serialize_datetime(result.timestamp),
        "decision_id": result.decision_id,
    }


def _deserialize_gate_result(data: dict[str, Any]) -> GateResult:
    """Deserialize a GateResult from dict."""
    return GateResult(
        gate_id=GateId(data["gate_id"]),
        proposition_results=tuple(
            _deserialize_proposition_result(pr) for pr in data["proposition_results"]
        ),
        passed=data["passed"],
        timestamp=_deserialize_datetime(data["timestamp"]),
        decision_id=data.get("decision_id"),
    )


def _serialize_validation_run(run: ValidationRun) -> dict[str, Any]:
    """Serialize a ValidationRun to dict."""
    return {
        "initiative_id": str(run.initiative_id),
        "phase_id": str(run.phase_id) if run.phase_id else None,
        "gate_result": _serialize_gate_result(run.gate_result),
        "measurements": run.measurements,
        "timestamp": _serialize_datetime(run.timestamp),
    }


def _deserialize_validation_run(data: dict[str, Any]) -> ValidationRun:
    """Deserialize a ValidationRun from dict."""
    return ValidationRun(
        initiative_id=InitiativeId(data["initiative_id"]),
        phase_id=PhaseId(data["phase_id"]) if data.get("phase_id") else None,
        gate_result=_deserialize_gate_result(data["gate_result"]),
        measurements=data["measurements"],
        timestamp=_deserialize_datetime(data["timestamp"]),
    )


# =============================================================================
# ValidationStore
# =============================================================================


@dataclass
class ValidationStore:
    """
    Append-only ledger for validation runs.

    Provides:
    - Persistence to JSONL file
    - Query by initiative, phase, time range
    - Latest run retrieval per initiative/phase

    Example:
        >>> store = ValidationStore()
        >>> store.save_run(run)
        >>> latest = store.get_latest("brain")
        >>> history = store.get_history("brain", limit=10)
    """

    # Primary storage: list of runs in chronological order
    _runs: list[ValidationRun] = field(default_factory=list)

    # Index by initiative: initiative_id → list of run indices
    _by_initiative: dict[InitiativeId, list[int]] = field(default_factory=dict)

    # Index by initiative+phase: (initiative_id, phase_id) → list of run indices
    _by_phase: dict[tuple[InitiativeId, PhaseId | None], list[int]] = field(default_factory=dict)

    # Persistence path (if any)
    _persistence_path: Path | None = None

    # =========================================================================
    # Core Operations
    # =========================================================================

    def save_run(self, run: ValidationRun) -> None:
        """
        Save a validation run to the store.

        Appends to the ledger and persists if path is set.
        """
        index = len(self._runs)
        self._runs.append(run)

        # Update initiative index
        if run.initiative_id not in self._by_initiative:
            self._by_initiative[run.initiative_id] = []
        self._by_initiative[run.initiative_id].append(index)

        # Update phase index
        key = (run.initiative_id, run.phase_id)
        if key not in self._by_phase:
            self._by_phase[key] = []
        self._by_phase[key].append(index)

        # Persist if path is set
        if self._persistence_path:
            self._append_to_file(run)

        logger.debug(
            f"Saved validation run: initiative={run.initiative_id}, "
            f"phase={run.phase_id}, passed={run.passed}"
        )

    def get_latest(
        self,
        initiative_id: InitiativeId,
        phase_id: PhaseId | None = None,
    ) -> ValidationRun | None:
        """
        Get the most recent validation run for an initiative/phase.

        Args:
            initiative_id: The initiative to query
            phase_id: Optional phase filter (for phased initiatives)

        Returns:
            The most recent run, or None if no runs exist
        """
        key = (initiative_id, phase_id)
        indices = self._by_phase.get(key, [])

        if not indices:
            return None

        return self._runs[indices[-1]]

    def get_history(
        self,
        initiative_id: InitiativeId,
        phase_id: PhaseId | None = None,
        limit: int = 10,
    ) -> list[ValidationRun]:
        """
        Get recent validation runs for an initiative/phase.

        Args:
            initiative_id: The initiative to query
            phase_id: Optional phase filter
            limit: Maximum number of runs to return

        Returns:
            List of runs in reverse chronological order (newest first)
        """
        key = (initiative_id, phase_id)
        indices = self._by_phase.get(key, [])

        if not indices:
            return []

        # Return newest first, limited
        return [self._runs[i] for i in reversed(indices[-limit:])]

    def query(self, query: ValidationRunQuery) -> Iterator[ValidationRun]:
        """
        Query validation runs matching the given criteria.

        Returns an iterator over matching runs in chronological order.
        """
        count = 0
        skipped = 0

        for run in self._runs:
            if not query.matches(run):
                continue

            # Handle offset
            if skipped < query.offset:
                skipped += 1
                continue

            # Handle limit
            if query.limit and count >= query.limit:
                return

            yield run
            count += 1

    def count(self, query: ValidationRunQuery | None = None) -> int:
        """Count runs matching the query (or all if no query)."""
        if query is None:
            return len(self._runs)
        return sum(1 for _ in self.query(query))

    def all(self) -> Iterator[ValidationRun]:
        """Iterate over all runs in chronological order."""
        yield from self._runs

    # =========================================================================
    # Persistence
    # =========================================================================

    def _append_to_file(self, run: ValidationRun) -> None:
        """Append a single run to the persistence file."""
        if not self._persistence_path:
            return

        self._persistence_path.parent.mkdir(parents=True, exist_ok=True)

        with self._persistence_path.open("a", encoding="utf-8") as f:
            json_line = json.dumps(_serialize_validation_run(run))
            f.write(json_line + "\n")

    def _load_from_file(self) -> None:
        """Load all runs from the persistence file."""
        if not self._persistence_path or not self._persistence_path.exists():
            return

        with self._persistence_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    run = _deserialize_validation_run(data)
                    # Use internal append to rebuild indices
                    index = len(self._runs)
                    self._runs.append(run)

                    if run.initiative_id not in self._by_initiative:
                        self._by_initiative[run.initiative_id] = []
                    self._by_initiative[run.initiative_id].append(index)

                    key = (run.initiative_id, run.phase_id)
                    if key not in self._by_phase:
                        self._by_phase[key] = []
                    self._by_phase[key].append(index)

                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON at line {line_num}: {e}")
                except Exception as e:
                    logger.warning(f"Failed to load run at line {line_num}: {e}")

        logger.info(f"Loaded {len(self._runs)} validation runs from {self._persistence_path}")

    @classmethod
    def from_path(cls, path: Path) -> ValidationStore:
        """Create a ValidationStore with persistence to the given path."""
        store = cls(_persistence_path=path)
        store._load_from_file()
        return store


# =============================================================================
# Global Store (Module Singleton Pattern)
# =============================================================================

_store: ValidationStore | None = None


def get_validation_store() -> ValidationStore:
    """
    Get the global ValidationStore instance.

    Uses default XDG path for persistence.
    """
    global _store
    if _store is None:
        # Use XDG data directory
        xdg_data = Path.home() / ".local" / "share" / "kgents" / "validation"
        persistence_path = xdg_data / "runs.jsonl"
        _store = ValidationStore.from_path(persistence_path)
    return _store


def set_validation_store(store: ValidationStore) -> None:
    """Set the global ValidationStore instance (for testing)."""
    global _store
    _store = store


def reset_validation_store() -> None:
    """Reset the global ValidationStore instance (for testing)."""
    global _store
    _store = None
