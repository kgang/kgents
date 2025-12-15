"""Tests for FlinchStore - D-gent backed test flinch storage."""

from __future__ import annotations

import asyncio
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock

import pytest
from protocols.cli.devex.flinch_store import (
    Flinch,
    FlinchStore,
    get_flinch_store,
)
from protocols.cli.instance_db.interfaces import TelemetryEvent
from protocols.cli.instance_db.providers.sqlite import InMemoryTelemetryStore

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_report() -> Any:
    """Create a mock pytest report object."""
    report = MagicMock()
    report.nodeid = "test_example.py::TestFoo::test_bar"
    report.when = "call"
    report.duration = 1.23
    report.outcome = "failed"
    report.longrepr = MagicMock()
    report.longrepr.reprcrash = MagicMock()
    report.longrepr.reprcrash.message = "AssertionError: expected True"
    report.longrepr.__str__ = lambda self: "AssertionError: expected True but got False"
    return report


@pytest.fixture
def telemetry_store() -> Any:
    """Create an in-memory telemetry store."""
    return InMemoryTelemetryStore()


@pytest.fixture
def flinch_store(telemetry_store: Any, temp_dir: Path) -> Any:
    """Create a FlinchStore with in-memory telemetry."""
    return FlinchStore(
        telemetry=telemetry_store,
        jsonl_fallback=temp_dir / "flinches.jsonl",
    )


# =============================================================================
# Flinch Dataclass Tests
# =============================================================================


class TestFlinch:
    """Tests for the Flinch dataclass."""

    def test_create_flinch_minimal(self) -> None:
        """Create flinch with minimal required fields."""
        flinch = Flinch(
            test_id="test_foo.py::test_bar",
            phase="call",
            duration=0.5,
            outcome="failed",
        )

        assert flinch.test_id == "test_foo.py::test_bar"
        assert flinch.phase == "call"
        assert flinch.duration == 0.5
        assert flinch.outcome == "failed"
        assert flinch.id.startswith("FLINCH-")
        assert flinch.timestamp  # Auto-generated

    def test_create_flinch_with_error_info(self) -> None:
        """Create flinch with error information."""
        flinch = Flinch(
            test_id="test_foo.py::test_bar",
            phase="call",
            duration=0.5,
            outcome="failed",
            error_type="AssertionError",
            error_message="expected 1, got 2",
        )

        assert flinch.error_type == "AssertionError"
        assert flinch.error_message == "expected 1, got 2"

    def test_from_report(self, mock_report: Any) -> None:
        """Create flinch from pytest report."""
        flinch = Flinch.from_report(mock_report)

        assert flinch.test_id == "test_example.py::TestFoo::test_bar"
        assert flinch.phase == "call"
        assert flinch.duration == 1.23
        assert flinch.outcome == "failed"
        assert flinch.file_path == "test_example.py"
        assert flinch.function_name == "test_bar"
        assert flinch.error_type == "AssertionError"

    def test_to_event(self) -> None:
        """Convert flinch to TelemetryEvent."""
        flinch = Flinch(
            test_id="test_foo.py::test_bar",
            phase="call",
            duration=0.5,
            outcome="failed",
            error_type="ValueError",
        )

        event = flinch.to_event()

        assert isinstance(event, TelemetryEvent)
        assert event.event_type == "test_flinch"
        assert event.data["test_id"] == "test_foo.py::test_bar"
        assert event.data["error_type"] == "ValueError"

    def test_to_jsonl_dict(self) -> None:
        """Convert flinch to JSONL-compatible dict (Phase 1 format)."""
        flinch = Flinch(
            test_id="test_foo.py::test_bar",
            phase="call",
            duration=0.5,
            outcome="failed",
        )

        jsonl = flinch.to_jsonl_dict()

        assert "ts" in jsonl  # Unix timestamp
        assert jsonl["test"] == "test_foo.py::test_bar"
        assert jsonl["phase"] == "call"
        assert jsonl["duration"] == 0.5
        assert jsonl["outcome"] == "failed"

    def test_embed_text(self) -> None:
        """Generate text for embedding."""
        flinch = Flinch(
            test_id="test_foo.py::test_bar",
            phase="call",
            duration=0.5,
            outcome="failed",
            error_type="AssertionError",
            error_message="expected 1, got 2",
        )

        text = flinch.embed_text()

        assert "test_foo.py::test_bar" in text
        assert "failed" in text
        assert "AssertionError" in text
        assert "expected 1, got 2" in text


# =============================================================================
# FlinchStore Tests
# =============================================================================


class TestFlinchStoreAsync:
    """Tests for async FlinchStore operations."""

    @pytest.mark.asyncio
    async def test_emit_to_telemetry(
        self, flinch_store: Any, telemetry_store: Any
    ) -> None:
        """Emit flinch writes to telemetry store."""
        flinch = Flinch(
            test_id="test_foo.py::test_bar",
            phase="call",
            duration=0.5,
            outcome="failed",
        )

        await flinch_store.emit(flinch)

        # Verify in telemetry store
        count = await telemetry_store.count("test_flinch")
        assert count == 1

        events = await telemetry_store.query(event_type="test_flinch")
        assert len(events) == 1
        assert events[0].data["test_id"] == "test_foo.py::test_bar"

    @pytest.mark.asyncio
    async def test_emit_writes_jsonl(self, flinch_store: Any, temp_dir: Path) -> None:
        """Emit flinch writes to JSONL fallback."""
        flinch = Flinch(
            test_id="test_foo.py::test_bar",
            phase="call",
            duration=0.5,
            outcome="failed",
        )

        await flinch_store.emit(flinch)

        jsonl_path = temp_dir / "flinches.jsonl"
        assert jsonl_path.exists()
        content = jsonl_path.read_text()
        assert "test_foo.py::test_bar" in content

    @pytest.mark.asyncio
    async def test_query_by_type(self, flinch_store: Any, telemetry_store: Any) -> None:
        """Query flinches by error type."""
        # Emit flinches with different error types
        await flinch_store.emit(
            Flinch(
                test_id="test_a.py::test_1",
                phase="call",
                duration=0.1,
                outcome="failed",
                error_type="AssertionError",
            )
        )
        await flinch_store.emit(
            Flinch(
                test_id="test_b.py::test_2",
                phase="call",
                duration=0.2,
                outcome="failed",
                error_type="TypeError",
            )
        )
        await flinch_store.emit(
            Flinch(
                test_id="test_c.py::test_3",
                phase="call",
                duration=0.3,
                outcome="failed",
                error_type="AssertionError",
            )
        )

        # Query by type
        results = await flinch_store.query_by_type(error_type="AssertionError")

        assert len(results) == 2
        assert all(f.error_type == "AssertionError" for f in results)

    @pytest.mark.asyncio
    async def test_query_frequent_failures(self, flinch_store: Any) -> None:
        """Find frequently failing tests."""
        # Emit multiple failures for the same test
        for i in range(5):
            await flinch_store.emit(
                Flinch(
                    test_id="test_flaky.py::test_unstable",
                    phase="call",
                    duration=0.1,
                    outcome="failed",
                )
            )

        # Emit single failure for another test
        await flinch_store.emit(
            Flinch(
                test_id="test_stable.py::test_one_off",
                phase="call",
                duration=0.1,
                outcome="failed",
            )
        )

        # Query frequent failures
        frequent = await flinch_store.query_frequent_failures(min_count=3)

        assert "test_flaky.py::test_unstable" in frequent
        assert frequent["test_flaky.py::test_unstable"] == 5
        assert "test_stable.py::test_one_off" not in frequent

    @pytest.mark.asyncio
    async def test_count(self, flinch_store: Any) -> None:
        """Count total flinches."""
        for i in range(3):
            await flinch_store.emit(
                Flinch(
                    test_id=f"test_{i}.py::test_{i}",
                    phase="call",
                    duration=0.1,
                    outcome="failed",
                )
            )

        count = await flinch_store.count()
        assert count == 3


class TestFlinchStoreSync:
    """Tests for sync FlinchStore operations (for pytest hooks)."""

    def test_emit_sync_writes_jsonl_immediately(self, temp_dir: Path) -> None:
        """emit_sync writes to JSONL immediately."""
        store = FlinchStore(jsonl_fallback=temp_dir / "flinches.jsonl")
        flinch = Flinch(
            test_id="test_foo.py::test_bar",
            phase="call",
            duration=0.5,
            outcome="failed",
        )

        store.emit_sync(flinch)

        # JSONL should be written immediately (no async)
        jsonl_path = temp_dir / "flinches.jsonl"
        assert jsonl_path.exists()
        content = jsonl_path.read_text()
        assert "test_foo.py::test_bar" in content

    @pytest.mark.slow
    def test_emit_sync_queues_for_telemetry(
        self, telemetry_store: Any, temp_dir: Path
    ) -> None:
        """emit_sync queues flinch for async telemetry processing."""
        store = FlinchStore(
            telemetry=telemetry_store,
            jsonl_fallback=temp_dir / "flinches.jsonl",
        )
        flinch = Flinch(
            test_id="test_foo.py::test_bar",
            phase="call",
            duration=0.5,
            outcome="failed",
        )

        store.emit_sync(flinch)

        # Give worker time to process (this is timing-sensitive)
        time.sleep(1.0)

        # Verify in telemetry store
        count = asyncio.run(telemetry_store.count("test_flinch"))
        assert count == 1

    def test_emit_sync_multiple_flinches(self, temp_dir: Path) -> None:
        """emit_sync handles multiple flinches."""
        store = FlinchStore(jsonl_fallback=temp_dir / "flinches.jsonl")

        for i in range(5):
            store.emit_sync(
                Flinch(
                    test_id=f"test_{i}.py::test_{i}",
                    phase="call",
                    duration=0.1 * i,
                    outcome="failed",
                )
            )

        jsonl_path = temp_dir / "flinches.jsonl"
        lines = jsonl_path.read_text().strip().split("\n")
        assert len(lines) == 5


class TestFlinchStoreJSONLFallback:
    """Tests for JSONL-only mode (D-gent unavailable)."""

    def test_jsonl_only_mode(self, temp_dir: Path) -> None:
        """FlinchStore works with only JSONL fallback."""
        store = FlinchStore(jsonl_fallback=temp_dir / "flinches.jsonl")

        store.emit_sync(
            Flinch(
                test_id="test_foo.py::test_bar",
                phase="call",
                duration=0.5,
                outcome="failed",
            )
        )

        jsonl_path = temp_dir / "flinches.jsonl"
        assert jsonl_path.exists()

    @pytest.mark.asyncio
    async def test_no_telemetry_graceful(self, temp_dir: Path) -> None:
        """Store works gracefully without telemetry."""
        store = FlinchStore(jsonl_fallback=temp_dir / "flinches.jsonl")

        # Should not raise
        await store.emit(
            Flinch(
                test_id="test_foo.py::test_bar",
                phase="call",
                duration=0.5,
                outcome="failed",
            )
        )

        # Query returns empty (no telemetry)
        results = await store.query_by_type()
        assert results == []


# =============================================================================
# Singleton Tests
# =============================================================================


class TestGetFlinchStore:
    """Tests for the singleton factory."""

    def test_get_flinch_store_creates_singleton(self, temp_dir: Path) -> None:
        """get_flinch_store returns same instance."""
        store1 = get_flinch_store(
            jsonl_fallback=temp_dir / "flinches.jsonl", reinit=True
        )
        store2 = get_flinch_store()

        assert store1 is store2

    def test_get_flinch_store_reinit(self, temp_dir: Path) -> None:
        """reinit=True creates new instance."""
        store1 = get_flinch_store(
            jsonl_fallback=temp_dir / "flinches1.jsonl", reinit=True
        )
        store2 = get_flinch_store(
            jsonl_fallback=temp_dir / "flinches2.jsonl", reinit=True
        )

        assert store1 is not store2
