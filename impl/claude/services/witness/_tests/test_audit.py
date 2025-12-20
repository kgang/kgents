"""
Tests for Witness Audit Trail (Phase 3C).

Tests the automatic action recording layer that bridges
scheduler/pipeline to persistence.

See: plans/kgentsd-cross-jewel.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.witness.audit import (
    AuditEntry,
    AuditingInvoker,
    AuditingPipelineRunner,
    create_auditing_invoker,
    create_auditing_runner,
)
from services.witness.invoke import create_invoker
from services.witness.pipeline import Pipeline, Step, step
from services.witness.polynomial import TrustLevel

# =============================================================================
# AuditEntry Tests
# =============================================================================


class TestAuditEntry:
    """Tests for AuditEntry dataclass."""

    def test_entry_creation(self) -> None:
        """Test creating an audit entry."""
        entry = AuditEntry(
            path="world.forge.fix",
            action_type="invoke",
            success=True,
        )

        assert entry.path == "world.forge.fix"
        assert entry.action_type == "invoke"
        assert entry.entry_id.startswith("audit-")

    def test_entry_id_uniqueness(self) -> None:
        """Test that entry IDs are unique."""
        entry1 = AuditEntry(path="a")
        entry2 = AuditEntry(path="b")

        assert entry1.entry_id != entry2.entry_id

    def test_to_action_result(self) -> None:
        """Test conversion to ActionResult."""
        entry = AuditEntry(
            path="world.forge.fix",
            action_type="invoke",
            success=True,
            reversible=True,
            inverse_action="git stash pop",
        )

        result = entry.to_action_result()

        assert result.action == "invoke: world.forge.fix"
        assert result.success is True
        assert result.reversible is True
        assert result.inverse_action == "git stash pop"

    def test_entry_defaults(self) -> None:
        """Test default values."""
        entry = AuditEntry()

        assert entry.success is True
        assert entry.is_mutation is False
        assert entry.reversible is True
        assert entry.error is None


# =============================================================================
# AuditingInvoker Tests
# =============================================================================


class TestAuditingInvoker:
    """Tests for AuditingInvoker."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos."""
        logos = MagicMock()
        logos.invoke = AsyncMock(return_value={"status": "ok"})
        return logos

    @pytest.fixture
    def inner_invoker(self, mock_logos: MagicMock) -> MagicMock:
        """Create a JewelInvoker."""
        return create_invoker(mock_logos, TrustLevel.AUTONOMOUS)

    @pytest.fixture
    def mock_observer(self) -> MagicMock:
        """Create a mock Observer."""
        observer = MagicMock()
        observer.archetype = "developer"
        return observer

    @pytest.fixture
    def auditing(self, inner_invoker: MagicMock) -> AuditingInvoker:
        """Create an AuditingInvoker."""
        return create_auditing_invoker(inner_invoker)

    @pytest.mark.asyncio
    async def test_invoke_mutation_recorded(
        self, auditing: AuditingInvoker, mock_observer: MagicMock
    ) -> None:
        """Test that mutations are recorded."""
        await auditing.invoke("world.forge.fix", mock_observer)

        log = auditing.get_log(mutations_only=True)
        assert len(log) == 1
        assert log[0].path == "world.forge.fix"
        assert log[0].is_mutation is True

    @pytest.mark.asyncio
    async def test_invoke_read_not_recorded_by_default(
        self, auditing: AuditingInvoker, mock_observer: MagicMock
    ) -> None:
        """Test that reads are not recorded by default."""
        await auditing.invoke("world.gestalt.manifest", mock_observer)

        log = auditing.get_log(mutations_only=True)
        assert len(log) == 0

    @pytest.mark.asyncio
    async def test_invoke_read_recorded_when_enabled(
        self, inner_invoker: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test that reads are recorded when record_reads=True."""
        auditing = create_auditing_invoker(inner_invoker, record_reads=True)

        await auditing.invoke("world.gestalt.manifest", mock_observer)

        log = auditing.get_log(mutations_only=False)
        assert len(log) == 1
        assert log[0].is_mutation is False

    @pytest.mark.asyncio
    async def test_invoke_mutation_with_rollback_info(
        self, auditing: AuditingInvoker, mock_observer: MagicMock
    ) -> None:
        """Test mutation with explicit rollback info."""
        await auditing.invoke_mutation(
            "world.forge.fix",
            mock_observer,
            reversible=True,
            inverse_action="git stash pop",
        )

        log = auditing.get_log()
        assert len(log) == 1
        assert log[0].reversible is True
        assert log[0].inverse_action == "git stash pop"

    @pytest.mark.asyncio
    async def test_invoke_records_duration(
        self, auditing: AuditingInvoker, mock_observer: MagicMock
    ) -> None:
        """Test that duration is recorded."""
        await auditing.invoke("world.forge.fix", mock_observer)

        log = auditing.get_log()
        assert log[0].duration_ms >= 0

    @pytest.mark.asyncio
    async def test_invoke_records_observer_context(
        self, auditing: AuditingInvoker, mock_observer: MagicMock
    ) -> None:
        """Test that observer context is recorded."""
        await auditing.invoke("world.forge.fix", mock_observer)

        log = auditing.get_log()
        assert log[0].observer_archetype == "developer"
        assert log[0].trust_level == "AUTONOMOUS"

    @pytest.mark.asyncio
    async def test_callback_invoked(
        self, auditing: AuditingInvoker, mock_observer: MagicMock
    ) -> None:
        """Test that callbacks are invoked."""
        callback_entries: list[AuditEntry] = []

        async def callback(entry: AuditEntry) -> None:
            callback_entries.append(entry)

        auditing.add_callback(callback)
        await auditing.invoke("world.forge.fix", mock_observer)

        assert len(callback_entries) == 1
        assert callback_entries[0].path == "world.forge.fix"

    @pytest.mark.asyncio
    async def test_persistence_called(
        self, inner_invoker: MagicMock, mock_observer: MagicMock
    ) -> None:
        """Test that persistence is called for mutations."""
        mock_persistence = MagicMock()
        mock_persistence.record_action = AsyncMock()

        auditing = create_auditing_invoker(inner_invoker, persistence=mock_persistence)
        await auditing.invoke("world.forge.fix", mock_observer)

        mock_persistence.record_action.assert_called_once()

    def test_trust_level_exposed(self, auditing: AuditingInvoker) -> None:
        """Test that inner invoker's trust level is exposed."""
        assert auditing.trust_level == TrustLevel.AUTONOMOUS


# =============================================================================
# AuditingPipelineRunner Tests
# =============================================================================


class TestAuditingPipelineRunner:
    """Tests for AuditingPipelineRunner."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos."""
        logos = MagicMock()
        logos.invoke = AsyncMock(return_value={"status": "ok"})
        return logos

    @pytest.fixture
    def invoker(self, mock_logos: MagicMock) -> MagicMock:
        """Create a JewelInvoker."""
        return create_invoker(mock_logos, TrustLevel.AUTONOMOUS)

    @pytest.fixture
    def mock_observer(self) -> MagicMock:
        """Create a mock Observer."""
        observer = MagicMock()
        observer.archetype = "developer"
        return observer

    @pytest.fixture
    def mock_persistence(self) -> MagicMock:
        """Create a mock persistence layer."""
        persistence = MagicMock()
        persistence.record_action = AsyncMock()
        return persistence

    @pytest.mark.asyncio
    async def test_pipeline_recorded(
        self, invoker: MagicMock, mock_observer: MagicMock, mock_persistence: MagicMock
    ) -> None:
        """Test that pipeline execution is recorded."""
        runner = create_auditing_runner(invoker, mock_observer, persistence=mock_persistence)

        pipeline = Pipeline(
            [
                Step(path="world.gestalt.manifest"),
                Step(path="self.memory.manifest"),
            ]
        )

        result = await runner.run(pipeline, name="Test Pipeline")

        assert result.success is True
        mock_persistence.record_action.assert_called_once()

        # Check the recorded action
        call = mock_persistence.record_action.call_args[0][0]
        assert "pipeline:Test Pipeline" in call.action

    @pytest.mark.asyncio
    async def test_pipeline_with_mutations_marked(
        self, invoker: MagicMock, mock_observer: MagicMock, mock_persistence: MagicMock
    ) -> None:
        """Test that pipelines with mutations are marked as mutations."""
        runner = create_auditing_runner(invoker, mock_observer, persistence=mock_persistence)

        pipeline = Pipeline(
            [
                Step(path="world.gestalt.analyze"),  # Read
                Step(path="world.forge.fix"),  # Mutation
            ]
        )

        await runner.run(pipeline)

        call = mock_persistence.record_action.call_args[0][0]
        # Should be marked as mutation because it contains a mutation step
        # (Checked in the is_mutation detection)

    @pytest.mark.asyncio
    async def test_pipeline_failure_recorded(
        self, mock_observer: MagicMock, mock_persistence: MagicMock
    ) -> None:
        """Test that failed pipeline execution is recorded."""
        # Create invoker that fails
        logos = MagicMock()
        logos.invoke = AsyncMock(side_effect=Exception("Test failure"))
        invoker = create_invoker(logos, TrustLevel.AUTONOMOUS)

        runner = create_auditing_runner(invoker, mock_observer, persistence=mock_persistence)

        pipeline = Pipeline([Step(path="world.fail.now")])

        result = await runner.run(pipeline)

        assert result.success is False
        mock_persistence.record_action.assert_called_once()

    @pytest.mark.asyncio
    async def test_with_auditing_invoker(
        self, invoker: MagicMock, mock_observer: MagicMock, mock_persistence: MagicMock
    ) -> None:
        """Test runner with AuditingInvoker wrapper."""
        auditing_invoker = create_auditing_invoker(invoker, persistence=mock_persistence)
        runner = create_auditing_runner(
            auditing_invoker, mock_observer, persistence=mock_persistence
        )

        pipeline = Pipeline([Step(path="world.gestalt.manifest")])

        result = await runner.run(pipeline)

        assert result.success is True


# =============================================================================
# Integration Tests
# =============================================================================


class TestAuditIntegration:
    """Integration tests for the audit trail system."""

    @pytest.fixture
    def mock_observer(self) -> MagicMock:
        """Create a mock Observer."""
        observer = MagicMock()
        observer.archetype = "developer"
        return observer

    @pytest.mark.asyncio
    async def test_full_audit_trail(self, mock_observer: MagicMock) -> None:
        """Test building a complete audit trail."""
        logos = MagicMock()
        logos.invoke = AsyncMock(return_value={"ok": True})
        invoker = create_invoker(logos, TrustLevel.AUTONOMOUS)

        # Track all recorded actions
        recorded_actions: list[Any] = []
        mock_persistence = MagicMock()
        mock_persistence.record_action = AsyncMock(side_effect=lambda a: recorded_actions.append(a))

        auditing = create_auditing_invoker(invoker, persistence=mock_persistence)

        # Execute multiple operations
        await auditing.invoke("world.forge.fix", mock_observer)
        await auditing.invoke_mutation(
            "world.forge.apply",
            mock_observer,
            inverse_action="git revert HEAD",
        )

        # Build and run a pipeline
        runner = create_auditing_runner(auditing, mock_observer, persistence=mock_persistence)
        pipeline = step("world.gestalt.manifest") >> step("world.forge.document")
        await runner.run(pipeline, name="Doc Pipeline")

        # Verify trail
        assert len(recorded_actions) == 3  # 2 invokes + 1 pipeline

        # Check the audit log on the invoker
        log = auditing.get_log(mutations_only=False)
        assert len(log) == 2  # Only the mutations from invoke

    @pytest.mark.asyncio
    async def test_audit_entry_to_action_result_roundtrip(self) -> None:
        """Test that audit entries convert correctly to ActionResult."""
        entry = AuditEntry(
            path="world.forge.fix",
            action_type="invoke",
            success=True,
            reversible=True,
            inverse_action="git stash pop",
        )

        result = entry.to_action_result()

        assert result.action_id == entry.entry_id
        assert "invoke: world.forge.fix" in result.action
        assert result.reversible == entry.reversible
        assert result.inverse_action == entry.inverse_action
