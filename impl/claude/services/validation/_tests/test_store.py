"""
Tests for ValidationStore persistence.

Verifies:
- Run storage and retrieval
- Query functionality
- JSONL persistence
"""

from __future__ import annotations

import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from services.validation.schema import (
    GateId,
    GateResult,
    InitiativeId,
    PhaseId,
    PropositionId,
    PropositionResult,
    ValidationRun,
)
from services.validation.store import (
    ValidationRunQuery,
    ValidationStore,
    ValidationStoreError,
    reset_validation_store,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def store() -> ValidationStore:
    """Create a fresh in-memory store."""
    return ValidationStore()


@pytest.fixture
def sample_run() -> ValidationRun:
    """Create a sample validation run."""
    return ValidationRun(
        initiative_id=InitiativeId("brain"),
        phase_id=None,
        gate_result=GateResult(
            gate_id=GateId("brain_gate"),
            proposition_results=(
                PropositionResult(
                    proposition_id=PropositionId("tests_pass"),
                    value=1.0,
                    passed=True,
                ),
            ),
            passed=True,
        ),
        measurements={"tests_pass": 1.0},
    )


@pytest.fixture
def sample_phased_run() -> ValidationRun:
    """Create a sample phased validation run."""
    return ValidationRun(
        initiative_id=InitiativeId("categorical"),
        phase_id=PhaseId("foundations"),
        gate_result=GateResult(
            gate_id=GateId("foundations_gate"),
            proposition_results=(
                PropositionResult(
                    proposition_id=PropositionId("correlation"),
                    value=0.45,
                    passed=True,
                ),
            ),
            passed=True,
        ),
        measurements={"correlation": 0.45},
    )


# =============================================================================
# Basic Operations Tests
# =============================================================================


class TestBasicOperations:
    """Tests for basic store operations."""

    def test_save_and_retrieve(self, store: ValidationStore, sample_run: ValidationRun) -> None:
        """Save a run and retrieve it."""
        store.save_run(sample_run)

        latest = store.get_latest(InitiativeId("brain"))

        assert latest is not None
        assert latest.initiative_id == "brain"
        assert latest.passed is True

    def test_get_latest_no_runs(self, store: ValidationStore) -> None:
        """Get latest returns None when no runs exist."""
        latest = store.get_latest(InitiativeId("nonexistent"))

        assert latest is None

    def test_get_latest_with_phase(
        self, store: ValidationStore, sample_phased_run: ValidationRun
    ) -> None:
        """Get latest with phase filter."""
        store.save_run(sample_phased_run)

        latest = store.get_latest(
            InitiativeId("categorical"),
            PhaseId("foundations"),
        )

        assert latest is not None
        assert latest.phase_id == "foundations"

    def test_get_history(self, store: ValidationStore) -> None:
        """Get history returns runs in reverse chronological order."""
        # Create multiple runs with different timestamps
        for i in range(5):
            run = ValidationRun(
                initiative_id=InitiativeId("brain"),
                phase_id=None,
                gate_result=GateResult(
                    gate_id=GateId("gate"),
                    proposition_results=(),
                    passed=i % 2 == 0,  # Alternating
                ),
                measurements={"count": float(i)},
                timestamp=datetime.now(timezone.utc) + timedelta(seconds=i),
            )
            store.save_run(run)

        history = store.get_history(InitiativeId("brain"), limit=3)

        assert len(history) == 3
        # Newest first
        assert history[0].measurements["count"] == 4.0
        assert history[1].measurements["count"] == 3.0
        assert history[2].measurements["count"] == 2.0

    def test_count(self, store: ValidationStore, sample_run: ValidationRun) -> None:
        """Count runs."""
        assert store.count() == 0

        store.save_run(sample_run)

        assert store.count() == 1

    def test_all(self, store: ValidationStore) -> None:
        """Iterate over all runs."""
        for i in range(3):
            run = ValidationRun(
                initiative_id=InitiativeId(f"initiative_{i}"),
                phase_id=None,
                gate_result=GateResult(
                    gate_id=GateId("gate"),
                    proposition_results=(),
                    passed=True,
                ),
                measurements={},
            )
            store.save_run(run)

        all_runs = list(store.all())

        assert len(all_runs) == 3


# =============================================================================
# Query Tests
# =============================================================================


class TestQuery:
    """Tests for query functionality."""

    def test_query_by_initiative(self, store: ValidationStore) -> None:
        """Query by initiative ID."""
        # Add runs for different initiatives
        for initiative in ["brain", "witness", "brain"]:
            run = ValidationRun(
                initiative_id=InitiativeId(initiative),
                phase_id=None,
                gate_result=GateResult(
                    gate_id=GateId("gate"),
                    proposition_results=(),
                    passed=True,
                ),
                measurements={},
            )
            store.save_run(run)

        query = ValidationRunQuery(initiative_id=InitiativeId("brain"))
        results = list(store.query(query))

        assert len(results) == 2
        assert all(r.initiative_id == "brain" for r in results)

    def test_query_by_phase(self, store: ValidationStore) -> None:
        """Query by phase ID."""
        # Add runs for different phases
        for phase in ["foundations", "integration", "foundations"]:
            run = ValidationRun(
                initiative_id=InitiativeId("categorical"),
                phase_id=PhaseId(phase),
                gate_result=GateResult(
                    gate_id=GateId("gate"),
                    proposition_results=(),
                    passed=True,
                ),
                measurements={},
            )
            store.save_run(run)

        query = ValidationRunQuery(
            initiative_id=InitiativeId("categorical"),
            phase_id=PhaseId("foundations"),
        )
        results = list(store.query(query))

        assert len(results) == 2
        assert all(r.phase_id == "foundations" for r in results)

    def test_query_by_passed(self, store: ValidationStore) -> None:
        """Query by pass/fail status."""
        # Add passing and failing runs
        for passed in [True, False, True, False]:
            run = ValidationRun(
                initiative_id=InitiativeId("brain"),
                phase_id=None,
                gate_result=GateResult(
                    gate_id=GateId("gate"),
                    proposition_results=(),
                    passed=passed,
                ),
                measurements={},
            )
            store.save_run(run)

        query = ValidationRunQuery(passed=True)
        results = list(store.query(query))

        assert len(results) == 2
        assert all(r.passed for r in results)

    def test_query_by_time_range(self, store: ValidationStore) -> None:
        """Query by time range."""
        now = datetime.now(timezone.utc)

        # Add runs at different times
        for i in range(5):
            run = ValidationRun(
                initiative_id=InitiativeId("brain"),
                phase_id=None,
                gate_result=GateResult(
                    gate_id=GateId("gate"),
                    proposition_results=(),
                    passed=True,
                ),
                measurements={"index": float(i)},
                timestamp=now + timedelta(hours=i),
            )
            store.save_run(run)

        # Query for runs after 2 hours from now
        query = ValidationRunQuery(after=now + timedelta(hours=2))
        results = list(store.query(query))

        assert len(results) == 2  # index 3, 4

    def test_query_with_limit_and_offset(self, store: ValidationStore) -> None:
        """Query with pagination."""
        for i in range(10):
            run = ValidationRun(
                initiative_id=InitiativeId("brain"),
                phase_id=None,
                gate_result=GateResult(
                    gate_id=GateId("gate"),
                    proposition_results=(),
                    passed=True,
                ),
                measurements={"index": float(i)},
            )
            store.save_run(run)

        query = ValidationRunQuery(limit=3, offset=2)
        results = list(store.query(query))

        assert len(results) == 3
        assert results[0].measurements["index"] == 2.0

    def test_query_count(self, store: ValidationStore) -> None:
        """Count with query."""
        for passed in [True, True, False]:
            run = ValidationRun(
                initiative_id=InitiativeId("brain"),
                phase_id=None,
                gate_result=GateResult(
                    gate_id=GateId("gate"),
                    proposition_results=(),
                    passed=passed,
                ),
                measurements={},
            )
            store.save_run(run)

        query = ValidationRunQuery(passed=True)
        count = store.count(query)

        assert count == 2


# =============================================================================
# Persistence Tests
# =============================================================================


class TestPersistence:
    """Tests for JSONL persistence."""

    def test_persist_and_load(self, sample_run: ValidationRun) -> None:
        """Persist to file and load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runs.jsonl"

            # Create store and save run
            store1 = ValidationStore.from_path(path)
            store1.save_run(sample_run)

            # Create new store from same path
            store2 = ValidationStore.from_path(path)

            assert store2.count() == 1
            latest = store2.get_latest(InitiativeId("brain"))
            assert latest is not None
            assert latest.passed is True

    def test_append_multiple_runs(self) -> None:
        """Multiple runs are appended to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runs.jsonl"

            store = ValidationStore.from_path(path)

            for i in range(3):
                run = ValidationRun(
                    initiative_id=InitiativeId(f"initiative_{i}"),
                    phase_id=None,
                    gate_result=GateResult(
                        gate_id=GateId("gate"),
                        proposition_results=(),
                        passed=True,
                    ),
                    measurements={},
                )
                store.save_run(run)

            # Count lines in file
            lines = path.read_text().strip().split("\n")
            assert len(lines) == 3

    def test_handles_empty_file(self) -> None:
        """Gracefully handles empty persistence file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runs.jsonl"
            path.touch()  # Create empty file

            store = ValidationStore.from_path(path)

            assert store.count() == 0

    def test_handles_nonexistent_file(self) -> None:
        """Gracefully handles nonexistent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nonexistent" / "runs.jsonl"

            store = ValidationStore.from_path(path)

            assert store.count() == 0

    def test_creates_parent_directories(self, sample_run: ValidationRun) -> None:
        """Creates parent directories when saving."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "dir" / "runs.jsonl"

            store = ValidationStore.from_path(path)
            store.save_run(sample_run)

            assert path.exists()


# =============================================================================
# Module Singleton Tests
# =============================================================================


class TestModuleSingleton:
    """Tests for module singleton pattern."""

    def test_reset_clears_store(self) -> None:
        """Reset clears the global store."""
        reset_validation_store()
        # Just verify it doesn't raise
