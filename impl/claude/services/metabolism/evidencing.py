"""
Background Evidence Accumulator: ASHC Continuous Mode.

Checkpoint 2.1 of Metabolic Development Protocol.

User Journey:
    # Developer saves file
    services/verification/core.py saved
        ↓
    [Background] ASHC adaptive verification triggered
        ↓
    Evidence corpus grows (+1 run, diversity score updated)
        ↓
    Causal graph learns: "type hints" → +8% pass rate
        ↓
    [Only on critical failure] Developer notified

The key insight: 100 identical runs ≠ 100× confidence.
Diversity scoring prevents confidence inflation from repeated inputs.

Teaching:
    gotcha: Diversity score matters more than run count.
            10 diverse runs > 100 identical runs.
            (Evidence: test_evidencing.py::test_diversity_beats_count)

    gotcha: Background accumulation is fire-and-forget.
            Only critical failures surface to the developer.
            (Evidence: test_evidencing.py::test_silent_accumulation)

AGENTESE: time.metabolism.evidence
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .persistence import MetabolismPersistence

logger = logging.getLogger(__name__)


# =============================================================================
# Diversity Scoring
# =============================================================================


@dataclass(frozen=True)
class InputSignature:
    """
    A unique signature for a test input.

    Used to detect duplicate/similar inputs for diversity scoring.
    """

    file_hash: str  # Hash of file contents
    test_focus: str  # Which tests were run
    context_hash: str  # Hash of context (env, config, etc.)

    @classmethod
    def from_run(
        cls,
        file_content: str,
        test_files: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> InputSignature:
        """Create signature from run parameters."""
        file_hash = hashlib.sha256(file_content.encode()).hexdigest()[:16]
        test_focus = ",".join(sorted(test_files or []))
        context_str = json.dumps(context or {}, sort_keys=True)
        context_hash = hashlib.sha256(context_str.encode()).hexdigest()[:8]

        return cls(
            file_hash=file_hash,
            test_focus=test_focus,
            context_hash=context_hash,
        )


@dataclass
class DiversityScore:
    """
    Measures input diversity across evidence runs.

    The core principle: unique_inputs / total_runs
    - Score of 1.0 = every run had unique input
    - Score of 0.1 = 10% unique, 90% duplicates
    """

    unique_signatures: set[str] = field(default_factory=set)
    total_runs: int = 0

    @property
    def score(self) -> float:
        """Diversity score between 0.0 and 1.0."""
        if self.total_runs == 0:
            return 0.0
        return len(self.unique_signatures) / self.total_runs

    def add_run(self, signature: InputSignature) -> bool:
        """
        Record a new run.

        Returns True if this was a unique input, False if duplicate.
        """
        self.total_runs += 1
        sig_str = f"{signature.file_hash}:{signature.test_focus}:{signature.context_hash}"

        if sig_str in self.unique_signatures:
            return False

        self.unique_signatures.add(sig_str)
        return True

    @property
    def unique_count(self) -> int:
        """Number of unique inputs seen."""
        return len(self.unique_signatures)

    def to_dict(self) -> dict[str, Any]:
        return {
            "unique_count": self.unique_count,
            "total_runs": self.total_runs,
            "score": round(self.score, 4),
        }


# =============================================================================
# Evidence Run (single verification result)
# =============================================================================


@dataclass(frozen=True)
class EvidenceRun:
    """
    A single background verification run.

    Captured silently in the background during development.
    """

    run_id: str
    task_pattern: str
    passed: bool
    test_count: int
    failed_tests: tuple[str, ...]
    duration_ms: float
    signature: InputSignature
    timestamp: datetime = field(default_factory=datetime.now)
    nudges: tuple[str, ...] = ()  # Any spec modifications

    @property
    def is_critical_failure(self) -> bool:
        """
        Determine if this is a critical failure that should surface.

        Critical = passed previously, now failing (regression).
        """
        # For now, any failure with >50% test failures is critical
        if not self.passed and self.test_count > 0:
            fail_rate = len(self.failed_tests) / self.test_count
            return fail_rate > 0.5
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "task_pattern": self.task_pattern,
            "passed": self.passed,
            "test_count": self.test_count,
            "failed_tests": list(self.failed_tests),
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat(),
            "nudges": list(self.nudges),
        }


# =============================================================================
# Stored Evidence (accumulated runs for a task pattern)
# =============================================================================


@dataclass
class StoredEvidence:
    """
    Accumulated evidence for a specific task pattern.

    This is what gets surfaced in brain_adapter.find_prior_evidence().
    """

    task_pattern: str
    runs: list[EvidenceRun] = field(default_factory=list)
    diversity: DiversityScore = field(default_factory=DiversityScore)
    created_at: datetime = field(default_factory=datetime.now)
    last_run_at: datetime | None = None

    @property
    def run_count(self) -> int:
        return len(self.runs)

    @property
    def pass_rate(self) -> float:
        if not self.runs:
            return 0.0
        passed = sum(1 for r in self.runs if r.passed)
        return passed / len(self.runs)

    @property
    def diversity_score(self) -> float:
        return self.diversity.score

    def add_run(self, run: EvidenceRun) -> None:
        """Add a new run to the evidence."""
        self.runs.append(run)
        self.diversity.add_run(run.signature)
        self.last_run_at = run.timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_pattern": self.task_pattern,
            "run_count": self.run_count,
            "pass_rate": round(self.pass_rate, 4),
            "diversity_score": round(self.diversity_score, 4),
            "created_at": self.created_at.isoformat(),
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
        }


# =============================================================================
# Causal Insight Tracking
# =============================================================================


@dataclass
class CausalInsight:
    """
    A learned relationship: nudge → outcome.

    Over time, we learn which changes lead to better outcomes.
    E.g., "adding type hints" → +8% pass rate
    """

    nudge_pattern: str  # What was changed
    outcome_delta: float  # Change in pass rate
    observation_count: int  # How many times observed
    confidence: float  # Bayesian confidence in the relationship

    def to_dict(self) -> dict[str, Any]:
        return {
            "nudge_pattern": self.nudge_pattern,
            "outcome_delta": round(self.outcome_delta, 4),
            "observation_count": self.observation_count,
            "confidence": round(self.confidence, 4),
        }


# =============================================================================
# Background Evidence Accumulator
# =============================================================================


class BackgroundEvidencing:
    """
    Fire-and-forget evidence accumulation service.

    Runs verification in the background, accumulates evidence,
    and only surfaces critical failures.

    Usage:
        evidencing = BackgroundEvidencing()

        # Fire-and-forget: schedule verification
        await evidencing.schedule_verification(
            task_pattern="verification integration",
            file_content=code,
            test_files=["test_core.py"],
        )

        # Query accumulated evidence
        evidence = evidencing.get_evidence("verification")

        # Get causal insights
        insights = evidencing.get_insights("type hints")

    With persistence (D-gent backed):
        persistence = MetabolismPersistence(dgent=router)
        evidencing = BackgroundEvidencing(persistence=persistence)

        # Evidence now persists across sessions
        await evidencing.load()  # Load prior evidence
        # ... work happens ...
        await evidencing.save()  # Persist for next session
    """

    def __init__(
        self,
        store_path: Path | str | None = None,
        max_runs_per_pattern: int = 100,
        persistence: "MetabolismPersistence | None" = None,
    ):
        """
        Initialize the accumulator.

        Args:
            store_path: Path for evidence persistence (XDG-compliant, fallback if no D-gent)
            max_runs_per_pattern: Maximum runs to keep per pattern (oldest evicted)
            persistence: Optional D-gent backed persistence layer
        """
        self._store_path = Path(store_path) if store_path else self._default_store_path()
        self._max_runs = max_runs_per_pattern
        self._persistence = persistence
        self._evidence: dict[str, StoredEvidence] = {}
        self._insights: dict[str, CausalInsight] = {}
        self._pending_tasks: set[str] = set()
        self._critical_failures: list[EvidenceRun] = []

    def _default_store_path(self) -> Path:
        """Get default XDG-compliant store path."""
        import os

        xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        return Path(xdg_data) / "kgents" / "metabolism" / "evidence.json"

    # =========================================================================
    # Scheduling (Fire-and-Forget)
    # =========================================================================

    async def schedule_verification(
        self,
        task_pattern: str,
        file_content: str,
        test_files: list[str] | None = None,
        context: dict[str, Any] | None = None,
        nudges: list[str] | None = None,
    ) -> str:
        """
        Schedule a background verification run.

        This is fire-and-forget: returns immediately with a run_id,
        verification happens in the background.

        Args:
            task_pattern: Pattern describing the work (e.g., "verification integration")
            file_content: The code being verified
            test_files: Optional list of test files to run
            context: Optional context (env, config)
            nudges: Optional list of spec modifications applied

        Returns:
            Run ID for tracking
        """
        import uuid

        run_id = str(uuid.uuid4())[:8]

        # Create signature
        signature = InputSignature.from_run(
            file_content=file_content,
            test_files=test_files,
            context=context,
        )

        # Schedule background task
        self._pending_tasks.add(run_id)
        asyncio.create_task(
            self._run_verification(
                run_id=run_id,
                task_pattern=task_pattern,
                file_content=file_content,
                test_files=test_files,
                signature=signature,
                nudges=tuple(nudges or []),
            )
        )

        logger.debug(f"Scheduled verification {run_id} for pattern: {task_pattern}")
        return run_id

    async def _run_verification(
        self,
        run_id: str,
        task_pattern: str,
        file_content: str,
        test_files: list[str] | None,
        signature: InputSignature,
        nudges: tuple[str, ...],
    ) -> None:
        """
        Run verification in background and accumulate result.

        This is the internal worker that runs after scheduling.
        """
        import time

        start = time.monotonic()

        try:
            # Import here to avoid circular deps
            from protocols.ashc.verify import verify_code

            # Run verification
            result = await verify_code(
                code=file_content,
                run_tests=bool(test_files),
                run_types=True,
                run_lint=True,
            )

            duration_ms = (time.monotonic() - start) * 1000

            # Extract failed tests
            failed_tests: list[str] = []
            if not result.test_report.success:
                # Parse failures from output if available
                failed_tests = self._extract_failed_tests(result.test_report.raw_output)

            # Create run record
            run = EvidenceRun(
                run_id=run_id,
                task_pattern=task_pattern,
                passed=result.passed,
                test_count=result.test_report.total,
                failed_tests=tuple(failed_tests),
                duration_ms=duration_ms,
                signature=signature,
                nudges=nudges,
            )

            # Accumulate evidence
            self._accumulate(run)

            # Check for critical failure
            if run.is_critical_failure:
                self._critical_failures.append(run)
                logger.warning(f"Critical failure in verification {run_id}: {failed_tests}")

        except Exception as e:
            logger.error(f"Background verification {run_id} failed: {e}")

        finally:
            self._pending_tasks.discard(run_id)

    def _extract_failed_tests(self, output: str) -> list[str]:
        """Extract failed test names from pytest output."""
        import re

        # Look for FAILED lines
        pattern = r"FAILED\s+(\S+)"
        matches = re.findall(pattern, output)
        return matches

    def _accumulate(self, run: EvidenceRun) -> None:
        """Accumulate a run into the evidence store."""
        pattern = run.task_pattern

        if pattern not in self._evidence:
            self._evidence[pattern] = StoredEvidence(task_pattern=pattern)

        evidence = self._evidence[pattern]
        evidence.add_run(run)

        # Evict oldest if over limit
        if len(evidence.runs) > self._max_runs:
            evidence.runs = evidence.runs[-self._max_runs :]

        logger.debug(
            f"Accumulated run for '{pattern}': "
            f"count={evidence.run_count}, "
            f"pass_rate={evidence.pass_rate:.2%}, "
            f"diversity={evidence.diversity_score:.2f}"
        )

    # =========================================================================
    # Evidence Querying
    # =========================================================================

    def get_evidence(self, task_pattern: str) -> StoredEvidence | None:
        """Get accumulated evidence for a task pattern."""
        return self._evidence.get(task_pattern)

    def find_matching_evidence(
        self,
        query: str,
        limit: int = 5,
    ) -> list[StoredEvidence]:
        """
        Find evidence for patterns matching a query.

        Uses simple substring matching for now.
        Future: Use semantic similarity via Brain vectors.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            Matching evidence sorted by run count
        """
        query_lower = query.lower()
        matches: list[StoredEvidence] = []

        for pattern, evidence in self._evidence.items():
            # Simple substring matching
            if query_lower in pattern.lower():
                matches.append(evidence)
            elif any(word in pattern.lower() for word in query_lower.split()):
                matches.append(evidence)

        # Sort by run count (most evidence first)
        matches.sort(key=lambda e: e.run_count, reverse=True)
        return matches[:limit]

    def get_critical_failures(self) -> list[EvidenceRun]:
        """Get unacknowledged critical failures."""
        return list(self._critical_failures)

    def acknowledge_failure(self, run_id: str) -> bool:
        """Acknowledge a critical failure (remove from queue)."""
        for i, run in enumerate(self._critical_failures):
            if run.run_id == run_id:
                self._critical_failures.pop(i)
                return True
        return False

    # =========================================================================
    # Causal Insights
    # =========================================================================

    def record_nudge_outcome(
        self,
        nudge_pattern: str,
        before_pass_rate: float,
        after_pass_rate: float,
    ) -> None:
        """
        Record a nudge → outcome relationship.

        Over time, this builds causal insights about what changes help.
        """
        delta = after_pass_rate - before_pass_rate

        if nudge_pattern not in self._insights:
            self._insights[nudge_pattern] = CausalInsight(
                nudge_pattern=nudge_pattern,
                outcome_delta=delta,
                observation_count=1,
                confidence=0.5,  # Start with neutral confidence
            )
        else:
            insight = self._insights[nudge_pattern]
            # Bayesian update: weighted average with new observation
            n = insight.observation_count
            new_delta = (insight.outcome_delta * n + delta) / (n + 1)
            # Confidence increases with observations
            new_confidence = min(0.95, 0.5 + (n + 1) * 0.05)

            self._insights[nudge_pattern] = CausalInsight(
                nudge_pattern=nudge_pattern,
                outcome_delta=new_delta,
                observation_count=n + 1,
                confidence=new_confidence,
            )

    def get_insights(self, query: str | None = None) -> list[CausalInsight]:
        """
        Get causal insights, optionally filtered by query.

        Args:
            query: Optional filter for nudge patterns

        Returns:
            Insights sorted by confidence
        """
        insights = list(self._insights.values())

        if query:
            query_lower = query.lower()
            insights = [i for i in insights if query_lower in i.nudge_pattern.lower()]

        insights.sort(key=lambda i: i.confidence, reverse=True)
        return insights

    # =========================================================================
    # Persistence
    # =========================================================================

    async def save(self) -> Path:
        """
        Persist evidence to storage.

        If MetabolismPersistence is configured, uses D-gent.
        Otherwise falls back to JSON file.
        """
        if self._persistence:
            # Use D-gent backed persistence
            from .persistence import CausalInsightRecord, StoredEvidenceRecord

            for pattern, evidence in self._evidence.items():
                record = StoredEvidenceRecord(
                    task_pattern=pattern,
                    run_count=evidence.run_count,
                    pass_rate=evidence.pass_rate,
                    diversity_score=evidence.diversity_score,
                    unique_signatures_count=evidence.diversity.unique_count,
                    created_at=evidence.created_at,
                    last_run_at=evidence.last_run_at,
                    runs_json=json.dumps([r.to_dict() for r in evidence.runs[-50:]]),
                )
                await self._persistence.save_evidence(pattern, record)

            for nudge, insight in self._insights.items():
                insight_record = CausalInsightRecord(
                    nudge_pattern=insight.nudge_pattern,
                    outcome_delta=insight.outcome_delta,
                    observation_count=insight.observation_count,
                    confidence=insight.confidence,
                )
                await self._persistence.save_insight(insight_record)

            logger.debug("Saved evidence to D-gent persistence")
            return self._store_path  # Return path for API compatibility
        else:
            # JSON fallback
            return await self._save_json()

    async def _save_json(self) -> Path:
        """Save evidence to JSON file (fallback)."""
        self._store_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "evidence": {
                pattern: {
                    **evidence.to_dict(),
                    "runs": [r.to_dict() for r in evidence.runs[-50:]],
                }
                for pattern, evidence in self._evidence.items()
            },
            "insights": {k: v.to_dict() for k, v in self._insights.items()},
            "saved_at": datetime.now().isoformat(),
        }

        with open(self._store_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.debug(f"Saved evidence to {self._store_path}")
        return self._store_path

    async def load(self) -> bool:
        """
        Load evidence from storage.

        If MetabolismPersistence is configured, loads from D-gent.
        Otherwise falls back to JSON file.
        """
        if self._persistence:
            # Load from D-gent backed persistence
            patterns = await self._persistence.list_evidence_patterns()
            for pattern in patterns:
                record = await self._persistence.load_evidence(pattern)
                if record:
                    evidence = StoredEvidence(
                        task_pattern=pattern,
                        created_at=record.created_at,
                        last_run_at=record.last_run_at,
                    )
                    # Restore diversity metadata
                    evidence.diversity.total_runs = record.run_count
                    # Note: We can't fully restore unique signatures from record
                    # This is a known limitation - diversity score may be approximate
                    self._evidence[pattern] = evidence

            # Load insights
            insights = await self._persistence.load_insights()
            for insight_record in insights:
                self._insights[insight_record.nudge_pattern] = CausalInsight(
                    nudge_pattern=insight_record.nudge_pattern,
                    outcome_delta=insight_record.outcome_delta,
                    observation_count=insight_record.observation_count,
                    confidence=insight_record.confidence,
                )

            logger.debug(f"Loaded {len(patterns)} evidence patterns from D-gent")
            return bool(patterns)
        else:
            return await self._load_json()

    async def _load_json(self) -> bool:
        """Load evidence from JSON file (fallback)."""
        if not self._store_path.exists():
            logger.debug("No persisted evidence found")
            return False

        try:
            with open(self._store_path) as f:
                data = json.load(f)

            # Restore evidence (metadata only, not full runs for now)
            for pattern, ev_data in data.get("evidence", {}).items():
                self._evidence[pattern] = StoredEvidence(
                    task_pattern=pattern,
                    created_at=datetime.fromisoformat(
                        ev_data.get("created_at", datetime.now().isoformat())
                    ),
                )

            # Restore insights
            for nudge, insight_data in data.get("insights", {}).items():
                self._insights[nudge] = CausalInsight(
                    nudge_pattern=insight_data["nudge_pattern"],
                    outcome_delta=insight_data["outcome_delta"],
                    observation_count=insight_data["observation_count"],
                    confidence=insight_data["confidence"],
                )

            logger.debug(f"Loaded evidence from {self._store_path}")
            return True

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to load evidence: {e}")
            return False

    # =========================================================================
    # Statistics
    # =========================================================================

    def stats(self) -> dict[str, Any]:
        """Get accumulator statistics."""
        return {
            "pattern_count": len(self._evidence),
            "total_runs": sum(e.run_count for e in self._evidence.values()),
            "pending_tasks": len(self._pending_tasks),
            "critical_failures": len(self._critical_failures),
            "insight_count": len(self._insights),
            "store_path": str(self._store_path),
        }


# =============================================================================
# Factory
# =============================================================================


_accumulator: BackgroundEvidencing | None = None


def get_background_evidencing() -> BackgroundEvidencing:
    """Get or create the global BackgroundEvidencing service."""
    global _accumulator
    if _accumulator is None:
        _accumulator = BackgroundEvidencing()
    return _accumulator


def set_background_evidencing(accumulator: BackgroundEvidencing) -> None:
    """Set the global BackgroundEvidencing service (for testing)."""
    global _accumulator
    _accumulator = accumulator


def reset_background_evidencing() -> None:
    """Reset the global BackgroundEvidencing service."""
    global _accumulator
    _accumulator = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core types
    "InputSignature",
    "DiversityScore",
    "EvidenceRun",
    "StoredEvidence",
    "CausalInsight",
    # Service
    "BackgroundEvidencing",
    "get_background_evidencing",
    "set_background_evidencing",
    "reset_background_evidencing",
]
