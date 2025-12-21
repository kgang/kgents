"""
MetabolismPersistence: D-gent backed storage for metabolic state.

Checkpoint 2.2 of Metabolic Development Protocol.

User Journey:
    # Session 1
    kg session begin
        ↓
    Evidence accumulates in background
        ↓
    kg session end
        ↓
    Evidence persisted to D-gent

    # Session 2
    kg session begin
        ↓
    Evidence loaded from D-gent (cross-session continuity!)
        ↓
    Prior patterns inform current session

This is the persistence layer for:
- BackgroundEvidencing (evidence patterns, runs, causal insights)
- VoiceStigmergy (pheromone traces, decay rates)

The key insight: metabolism remembers across sessions. The garden
continues to grow even when the gardener sleeps.

Teaching:
    gotcha: D-gent fallback is graceful but lossy.
            If no database, falls back to JSON file.
            JSON file is local; D-gent is shared.
            (Evidence: test_persistence.py::test_fallback)

    gotcha: Trace evaporation is database-side for efficiency.
            Don't load all traces just to filter by intensity.
            (Evidence: test_persistence.py::test_evaporation_query)

AGENTESE: time.metabolism.persistence
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agents.d import DgentProtocol

logger = logging.getLogger(__name__)


# =============================================================================
# Contracts
# =============================================================================


@dataclass
class StoredEvidenceRecord:
    """
    Database record for evidence pattern.

    This is the persistence contract—what gets stored and retrieved.
    The full StoredEvidence object is reconstructed from this.
    """

    task_pattern: str
    run_count: int
    pass_rate: float
    diversity_score: float
    unique_signatures_count: int
    created_at: datetime
    last_run_at: datetime | None
    runs_json: str  # JSON-serialized list of recent runs

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_pattern": self.task_pattern,
            "run_count": self.run_count,
            "pass_rate": round(self.pass_rate, 4),
            "diversity_score": round(self.diversity_score, 4),
            "unique_signatures_count": self.unique_signatures_count,
            "created_at": self.created_at.isoformat(),
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "runs_json": self.runs_json,
        }


@dataclass
class CausalInsightRecord:
    """Database record for causal insight."""

    nudge_pattern: str
    outcome_delta: float
    observation_count: int
    confidence: float
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "nudge_pattern": self.nudge_pattern,
            "outcome_delta": round(self.outcome_delta, 4),
            "observation_count": self.observation_count,
            "confidence": round(self.confidence, 4),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class StigmergyTraceRecord:
    """Database record for stigmergy trace."""

    concept: str
    intensity: float
    deposited_at: datetime
    depositor: str
    metadata_json: str  # JSON-serialized metadata

    def to_dict(self) -> dict[str, Any]:
        return {
            "concept": self.concept,
            "intensity": round(self.intensity, 6),
            "deposited_at": self.deposited_at.isoformat(),
            "depositor": self.depositor,
            "metadata_json": self.metadata_json,
        }


# =============================================================================
# MetabolismPersistence
# =============================================================================


class MetabolismPersistence:
    """
    Unified persistence layer for metabolism services.

    Uses D-gent (DgentProtocol) for proper database backing.
    Falls back gracefully to JSON files if database unavailable.

    This follows the BrainPersistence pattern:
    - D-gent for semantic content storage
    - Graceful degradation when unavailable

    Usage:
        persistence = MetabolismPersistence(dgent=router)

        # Evidence
        await persistence.save_evidence("verification", evidence_record)
        record = await persistence.load_evidence("verification")

        # Insights
        await persistence.save_insight(insight_record)
        insights = await persistence.load_insights()

        # Stigmergy
        await persistence.save_stigmergy_trace(trace_record)
        traces = await persistence.load_stigmergy_traces("python")
    """

    def __init__(
        self,
        dgent: "DgentProtocol | None" = None,
        fallback_dir: Path | str | None = None,
    ) -> None:
        """
        Initialize MetabolismPersistence.

        Args:
            dgent: D-gent router for database storage
            fallback_dir: Directory for JSON fallback files
        """
        self._dgent = dgent
        self._fallback_dir = Path(fallback_dir) if fallback_dir else self._default_fallback_dir()
        self._use_fallback = dgent is None

        if self._use_fallback:
            logger.debug("MetabolismPersistence using JSON fallback (no D-gent)")
        else:
            logger.debug("MetabolismPersistence using D-gent storage")

    def _default_fallback_dir(self) -> Path:
        """Get default XDG-compliant fallback directory."""
        import os

        xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        return Path(xdg_data) / "kgents" / "metabolism"

    @property
    def has_dgent(self) -> bool:
        """Check if D-gent is available."""
        return self._dgent is not None

    # =========================================================================
    # Evidence Persistence
    # =========================================================================

    async def save_evidence(
        self,
        pattern: str,
        record: StoredEvidenceRecord,
    ) -> str:
        """
        Save evidence record for a task pattern.

        Args:
            pattern: The task pattern key
            record: Evidence record to save

        Returns:
            Storage ID (datum ID or file path)
        """
        if self._dgent:
            from agents.d import Datum

            datum = Datum(
                id=f"metabolism-evidence-{pattern}",
                content=json.dumps(record.to_dict()).encode("utf-8"),
                created_at=record.created_at.timestamp(),
                causal_parent=None,
                metadata={"type": "metabolism_evidence", "pattern": pattern},
            )
            return await self._dgent.put(datum)
        else:
            # JSON fallback
            return await self._save_evidence_json(pattern, record)

    async def load_evidence(self, pattern: str) -> StoredEvidenceRecord | None:
        """
        Load evidence record for a task pattern.

        Args:
            pattern: The task pattern key

        Returns:
            Evidence record or None if not found
        """
        if self._dgent:
            datum = await self._dgent.get(f"metabolism-evidence-{pattern}")
            if datum:
                data = json.loads(datum.content.decode("utf-8"))
                return self._record_from_dict(data)
            return None
        else:
            return await self._load_evidence_json(pattern)

    async def list_evidence_patterns(self) -> list[str]:
        """
        List all stored evidence patterns.

        Returns:
            List of pattern names
        """
        if self._dgent:
            datums = await self._dgent.list(prefix="metabolism-evidence-", limit=1000)
            patterns = []
            for datum in datums:
                # Extract pattern from ID: "metabolism-evidence-{pattern}"
                if datum.id.startswith("metabolism-evidence-"):
                    patterns.append(datum.id[20:])  # len("metabolism-evidence-") = 20
            return patterns
        else:
            return await self._list_evidence_patterns_json()

    async def delete_evidence(self, pattern: str) -> bool:
        """
        Delete evidence for a pattern.

        Args:
            pattern: The task pattern key

        Returns:
            True if deleted, False if not found
        """
        if self._dgent:
            return await self._dgent.delete(f"metabolism-evidence-{pattern}")
        else:
            return await self._delete_evidence_json(pattern)

    def _record_from_dict(self, data: dict[str, Any]) -> StoredEvidenceRecord:
        """Create StoredEvidenceRecord from dictionary."""
        return StoredEvidenceRecord(
            task_pattern=data["task_pattern"],
            run_count=data["run_count"],
            pass_rate=data["pass_rate"],
            diversity_score=data["diversity_score"],
            unique_signatures_count=data.get("unique_signatures_count", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_run_at=(
                datetime.fromisoformat(data["last_run_at"]) if data.get("last_run_at") else None
            ),
            runs_json=data.get("runs_json", "[]"),
        )

    # =========================================================================
    # Insight Persistence
    # =========================================================================

    async def save_insight(self, record: CausalInsightRecord) -> str:
        """
        Save causal insight record.

        Args:
            record: Insight record to save

        Returns:
            Storage ID
        """
        if self._dgent:
            from agents.d import Datum

            datum = Datum(
                id=f"metabolism-insight-{record.nudge_pattern}",
                content=json.dumps(record.to_dict()).encode("utf-8"),
                created_at=record.updated_at.timestamp(),
                causal_parent=None,
                metadata={"type": "metabolism_insight", "nudge": record.nudge_pattern},
            )
            return await self._dgent.put(datum)
        else:
            return await self._save_insight_json(record)

    async def load_insights(self, query: str | None = None) -> list[CausalInsightRecord]:
        """
        Load causal insights, optionally filtered.

        Args:
            query: Optional pattern to filter by

        Returns:
            List of insight records
        """
        if self._dgent:
            datums = await self._dgent.list(prefix="metabolism-insight-", limit=1000)
            insights = []
            for datum in datums:
                data = json.loads(datum.content.decode("utf-8"))
                record = CausalInsightRecord(
                    nudge_pattern=data["nudge_pattern"],
                    outcome_delta=data["outcome_delta"],
                    observation_count=data["observation_count"],
                    confidence=data["confidence"],
                    updated_at=datetime.fromisoformat(
                        data.get("updated_at", datetime.now().isoformat())
                    ),
                )
                # Filter if query provided
                if query is None or query.lower() in record.nudge_pattern.lower():
                    insights.append(record)
            return insights
        else:
            return await self._load_insights_json(query)

    # =========================================================================
    # Stigmergy Persistence
    # =========================================================================

    async def save_stigmergy_trace(self, record: StigmergyTraceRecord) -> str:
        """
        Save a stigmergy trace record.

        Args:
            record: Trace record to save

        Returns:
            Storage ID
        """
        if self._dgent:
            from agents.d import Datum

            # Use timestamp in ID for uniqueness
            trace_id = f"metabolism-stigmergy-{record.concept}-{int(record.deposited_at.timestamp() * 1000)}"
            datum = Datum(
                id=trace_id,
                content=json.dumps(record.to_dict()).encode("utf-8"),
                created_at=record.deposited_at.timestamp(),
                causal_parent=None,
                metadata={
                    "type": "metabolism_stigmergy",
                    "concept": record.concept,
                    "depositor": record.depositor,
                },
            )
            return await self._dgent.put(datum)
        else:
            return await self._save_stigmergy_json(record)

    async def load_stigmergy_traces(
        self,
        concept: str | None = None,
        min_intensity: float = 0.0,
    ) -> list[StigmergyTraceRecord]:
        """
        Load stigmergy traces, optionally filtered.

        Args:
            concept: Optional concept to filter by
            min_intensity: Minimum intensity threshold

        Returns:
            List of trace records
        """
        if self._dgent:
            # Build prefix based on concept filter
            prefix = "metabolism-stigmergy-"
            if concept:
                prefix = f"metabolism-stigmergy-{concept}-"

            datums = await self._dgent.list(prefix=prefix, limit=10000)
            traces = []
            for datum in datums:
                data = json.loads(datum.content.decode("utf-8"))
                record = StigmergyTraceRecord(
                    concept=data["concept"],
                    intensity=data["intensity"],
                    deposited_at=datetime.fromisoformat(data["deposited_at"]),
                    depositor=data.get("depositor", "anonymous"),
                    metadata_json=data.get("metadata_json", "{}"),
                )
                # Filter by intensity
                if record.intensity >= min_intensity:
                    traces.append(record)
            return traces
        else:
            return await self._load_stigmergy_json(concept, min_intensity)

    async def delete_evaporated_traces(self, threshold: float) -> int:
        """
        Delete traces below intensity threshold.

        Args:
            threshold: Minimum intensity to keep

        Returns:
            Number of traces deleted
        """
        if self._dgent:
            datums = await self._dgent.list(prefix="metabolism-stigmergy-", limit=10000)
            deleted = 0
            for datum in datums:
                data = json.loads(datum.content.decode("utf-8"))
                if data.get("intensity", 0) < threshold:
                    await self._dgent.delete(datum.id)
                    deleted += 1
            return deleted
        else:
            return await self._delete_evaporated_json(threshold)

    # =========================================================================
    # JSON Fallback Methods
    # =========================================================================

    def _ensure_fallback_dir(self) -> None:
        """Ensure fallback directory exists."""
        self._fallback_dir.mkdir(parents=True, exist_ok=True)

    # Evidence JSON fallback

    def _evidence_file(self) -> Path:
        return self._fallback_dir / "evidence.json"

    async def _save_evidence_json(self, pattern: str, record: StoredEvidenceRecord) -> str:
        """Save evidence to JSON file."""
        self._ensure_fallback_dir()
        path = self._evidence_file()

        data: dict[str, Any] = {}
        if path.exists():
            data = json.loads(path.read_text())

        data[pattern] = record.to_dict()
        path.write_text(json.dumps(data, indent=2))

        return f"file://{path}#{pattern}"

    async def _load_evidence_json(self, pattern: str) -> StoredEvidenceRecord | None:
        """Load evidence from JSON file."""
        path = self._evidence_file()
        if not path.exists():
            return None

        data = json.loads(path.read_text())
        if pattern not in data:
            return None

        return self._record_from_dict(data[pattern])

    async def _list_evidence_patterns_json(self) -> list[str]:
        """List patterns from JSON file."""
        path = self._evidence_file()
        if not path.exists():
            return []

        data = json.loads(path.read_text())
        return list(data.keys())

    async def _delete_evidence_json(self, pattern: str) -> bool:
        """Delete evidence from JSON file."""
        path = self._evidence_file()
        if not path.exists():
            return False

        data = json.loads(path.read_text())
        if pattern not in data:
            return False

        del data[pattern]
        path.write_text(json.dumps(data, indent=2))
        return True

    # Insight JSON fallback

    def _insights_file(self) -> Path:
        return self._fallback_dir / "insights.json"

    async def _save_insight_json(self, record: CausalInsightRecord) -> str:
        """Save insight to JSON file."""
        self._ensure_fallback_dir()
        path = self._insights_file()

        data: dict[str, Any] = {}
        if path.exists():
            data = json.loads(path.read_text())

        data[record.nudge_pattern] = record.to_dict()
        path.write_text(json.dumps(data, indent=2))

        return f"file://{path}#{record.nudge_pattern}"

    async def _load_insights_json(self, query: str | None) -> list[CausalInsightRecord]:
        """Load insights from JSON file."""
        path = self._insights_file()
        if not path.exists():
            return []

        data = json.loads(path.read_text())
        insights = []
        for nudge, insight_data in data.items():
            record = CausalInsightRecord(
                nudge_pattern=insight_data["nudge_pattern"],
                outcome_delta=insight_data["outcome_delta"],
                observation_count=insight_data["observation_count"],
                confidence=insight_data["confidence"],
                updated_at=datetime.fromisoformat(
                    insight_data.get("updated_at", datetime.now().isoformat())
                ),
            )
            if query is None or query.lower() in record.nudge_pattern.lower():
                insights.append(record)
        return insights

    # Stigmergy JSON fallback

    def _stigmergy_file(self) -> Path:
        return self._fallback_dir / "stigmergy.json"

    async def _save_stigmergy_json(self, record: StigmergyTraceRecord) -> str:
        """Save stigmergy trace to JSON file."""
        self._ensure_fallback_dir()
        path = self._stigmergy_file()

        data: dict[str, list[dict[str, Any]]] = {}
        if path.exists():
            data = json.loads(path.read_text())

        if record.concept not in data:
            data[record.concept] = []
        data[record.concept].append(record.to_dict())
        path.write_text(json.dumps(data, indent=2))

        return f"file://{path}#{record.concept}"

    async def _load_stigmergy_json(
        self, concept: str | None, min_intensity: float
    ) -> list[StigmergyTraceRecord]:
        """Load stigmergy traces from JSON file."""
        path = self._stigmergy_file()
        if not path.exists():
            return []

        data = json.loads(path.read_text())
        traces = []

        concepts_to_check = [concept] if concept else list(data.keys())
        for c in concepts_to_check:
            if c not in data:
                continue
            for trace_data in data[c]:
                record = StigmergyTraceRecord(
                    concept=trace_data["concept"],
                    intensity=trace_data["intensity"],
                    deposited_at=datetime.fromisoformat(trace_data["deposited_at"]),
                    depositor=trace_data.get("depositor", "anonymous"),
                    metadata_json=trace_data.get("metadata_json", "{}"),
                )
                if record.intensity >= min_intensity:
                    traces.append(record)

        return traces

    async def _delete_evaporated_json(self, threshold: float) -> int:
        """Delete evaporated traces from JSON file."""
        path = self._stigmergy_file()
        if not path.exists():
            return 0

        data = json.loads(path.read_text())
        deleted = 0

        for concept in list(data.keys()):
            surviving = []
            for trace_data in data[concept]:
                if trace_data.get("intensity", 0) >= threshold:
                    surviving.append(trace_data)
                else:
                    deleted += 1
            if surviving:
                data[concept] = surviving
            else:
                del data[concept]

        path.write_text(json.dumps(data, indent=2))
        return deleted

    # =========================================================================
    # Statistics
    # =========================================================================

    async def stats(self) -> dict[str, Any]:
        """Get persistence statistics."""
        patterns = await self.list_evidence_patterns()
        insights = await self.load_insights()
        traces = await self.load_stigmergy_traces()

        return {
            "storage_type": "dgent" if self._dgent else "json_fallback",
            "evidence_patterns": len(patterns),
            "insight_count": len(insights),
            "stigmergy_trace_count": len(traces),
            "fallback_dir": str(self._fallback_dir),
        }


# =============================================================================
# Factory
# =============================================================================


_persistence: MetabolismPersistence | None = None


def get_metabolism_persistence() -> MetabolismPersistence:
    """Get or create the global MetabolismPersistence service."""
    global _persistence
    if _persistence is None:
        # Start with fallback; wire to D-gent via providers.py
        _persistence = MetabolismPersistence()
    return _persistence


def set_metabolism_persistence(persistence: MetabolismPersistence) -> None:
    """Set the global MetabolismPersistence service (for testing/wiring)."""
    global _persistence
    _persistence = persistence


def reset_metabolism_persistence() -> None:
    """Reset the global MetabolismPersistence service."""
    global _persistence
    _persistence = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Contracts
    "StoredEvidenceRecord",
    "CausalInsightRecord",
    "StigmergyTraceRecord",
    # Service
    "MetabolismPersistence",
    "get_metabolism_persistence",
    "set_metabolism_persistence",
    "reset_metabolism_persistence",
]
