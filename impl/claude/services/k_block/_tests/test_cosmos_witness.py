"""
Tests for Phase 2: Cosmos-Witness Integration.

Philosophy:
    "The proof IS the decision. The mark IS the witness."

These tests verify that:
1. CosmosEntry stores mark_id correctly
2. Cosmos.blame() returns traced history
3. WitnessedCosmos emits marks on commit
4. Harness.save() integrates with witness system
5. SaveResult includes mark_id when witnessed

See: spec/protocols/k-block.md §5
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.k_block.core import (
    BlameEntry,
    Cosmos,
    CosmosEntry,
    FileOperadHarness,
    IsolationState,
    KBlock,
    VersionId,
    generate_kblock_id,
)
from services.k_block.core.witnessed import (
    BlameEntryWithMark,
    CommitResult,
    WitnessedCosmos,
    WitnessTrace,
    create_witnessed_cosmos,
)

# -----------------------------------------------------------------------------
# Test Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def cosmos() -> Cosmos:
    """Fresh cosmos for each test."""
    return Cosmos()


@pytest.fixture
def mock_mark_store() -> MagicMock:
    """Mock mark store for testing."""
    store = MagicMock()
    # MarkStore.append is synchronous, MarkStore.get is synchronous
    store.append = MagicMock()
    store.get = MagicMock(return_value=None)
    return store


@pytest.fixture
def witnessed_cosmos(cosmos: Cosmos, mock_mark_store: MagicMock) -> WitnessedCosmos:
    """WitnessedCosmos with mock store."""
    return WitnessedCosmos(cosmos=cosmos, mark_store=mock_mark_store)


@pytest.fixture
def harness(cosmos: Cosmos) -> FileOperadHarness:
    """Harness without witness (for isolation testing)."""
    h = FileOperadHarness(cosmos=cosmos, witness_enabled=False)
    return h


@pytest.fixture
def witnessed_harness(cosmos: Cosmos, mock_mark_store: MagicMock) -> FileOperadHarness:
    """Harness with witness enabled."""
    witnessed = WitnessedCosmos(cosmos=cosmos, mark_store=mock_mark_store)
    h = FileOperadHarness(
        cosmos=cosmos,
        witness_enabled=True,
        _witnessed_cosmos=witnessed,
    )
    return h


# -----------------------------------------------------------------------------
# CosmosEntry Tests
# -----------------------------------------------------------------------------


class TestCosmosEntryWithMarkId:
    """Tests for CosmosEntry.mark_id field."""

    def test_cosmos_entry_has_mark_id_field(self) -> None:
        """CosmosEntry should have mark_id field."""
        entry = CosmosEntry.create(
            path="test.md",
            content="# Test",
            parent_version=None,
            actor="Kent",
            reasoning="Test commit",
            mark_id="mark-abc123",
        )
        assert entry.mark_id == "mark-abc123"

    def test_cosmos_entry_mark_id_defaults_to_none(self) -> None:
        """mark_id should default to None."""
        entry = CosmosEntry.create(
            path="test.md",
            content="# Test",
            parent_version=None,
        )
        assert entry.mark_id is None

    def test_cosmos_entry_serializes_mark_id(self) -> None:
        """mark_id should be included in to_dict()."""
        entry = CosmosEntry.create(
            path="test.md",
            content="# Test",
            parent_version=None,
            mark_id="mark-xyz789",
        )
        data = entry.to_dict()
        assert data["mark_id"] == "mark-xyz789"

    def test_cosmos_entry_deserializes_mark_id(self) -> None:
        """mark_id should be restored from from_dict()."""
        original = CosmosEntry.create(
            path="test.md",
            content="# Test",
            parent_version=None,
            mark_id="mark-restore123",
        )
        data = original.to_dict()
        restored = CosmosEntry.from_dict(data)
        assert restored.mark_id == "mark-restore123"


# -----------------------------------------------------------------------------
# BlameEntry Tests
# -----------------------------------------------------------------------------


class TestBlameEntry:
    """Tests for BlameEntry data structure."""

    def test_blame_entry_has_required_fields(self) -> None:
        """BlameEntry should have all required fields."""
        entry = BlameEntry(
            version_id=VersionId("v_test123"),
            actor="Kent",
            reasoning="Fixed typo",
            mark_id="mark-abc",
            timestamp=datetime.now(timezone.utc),
            summary="Changed: line 1",
        )
        assert entry.version_id == "v_test123"
        assert entry.actor == "Kent"
        assert entry.reasoning == "Fixed typo"
        assert entry.mark_id == "mark-abc"
        assert entry.summary == "Changed: line 1"

    def test_blame_entry_to_dict(self) -> None:
        """BlameEntry should serialize correctly."""
        ts = datetime.now(timezone.utc)
        entry = BlameEntry(
            version_id=VersionId("v_test123"),
            actor="Claude",
            reasoning=None,
            mark_id=None,
            timestamp=ts,
            summary="Initial: # Title",
        )
        data = entry.to_dict()
        assert data["version_id"] == "v_test123"
        assert data["actor"] == "Claude"
        assert data["reasoning"] is None
        assert data["mark_id"] is None
        assert data["timestamp"] == ts.isoformat()


# -----------------------------------------------------------------------------
# Cosmos.blame() Tests
# -----------------------------------------------------------------------------


class TestCosmosBlame:
    """Tests for Cosmos.blame() method."""

    @pytest.mark.asyncio
    async def test_blame_returns_empty_for_nonexistent_path(self, cosmos: Cosmos) -> None:
        """blame() should return empty list for unknown path."""
        result = await cosmos.blame("nonexistent.md")
        assert result == []

    @pytest.mark.asyncio
    async def test_blame_returns_single_entry_for_new_file(self, cosmos: Cosmos) -> None:
        """blame() should return one entry after initial commit."""
        await cosmos.commit(
            path="new.md",
            content="# New File",
            actor="Kent",
            reasoning="Created file",
            mark_id="mark-new123",
        )

        result = await cosmos.blame("new.md")
        assert len(result) == 1
        assert result[0].actor == "Kent"
        assert result[0].reasoning == "Created file"
        assert result[0].mark_id == "mark-new123"
        assert "Initial:" in result[0].summary

    @pytest.mark.asyncio
    async def test_blame_returns_history_newest_first(self, cosmos: Cosmos) -> None:
        """blame() should return entries newest first."""
        await cosmos.commit("doc.md", "Version 1", actor="Kent")
        await cosmos.commit("doc.md", "Version 2", actor="Claude")
        await cosmos.commit("doc.md", "Version 3", actor="Kent")

        result = await cosmos.blame("doc.md")
        assert len(result) == 3
        assert result[0].actor == "Kent"  # Most recent
        assert result[1].actor == "Claude"
        assert result[2].actor == "Kent"  # Oldest

    @pytest.mark.asyncio
    async def test_blame_respects_limit(self, cosmos: Cosmos) -> None:
        """blame() should respect limit parameter."""
        for i in range(10):
            await cosmos.commit("multi.md", f"Version {i}", actor="Kent")

        result = await cosmos.blame("multi.md", limit=5)
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_blame_computes_change_summary(self, cosmos: Cosmos) -> None:
        """blame() should compute meaningful summaries."""
        await cosmos.commit("doc.md", "Line 1\nLine 2")
        await cosmos.commit("doc.md", "Line 1 CHANGED\nLine 2")

        result = await cosmos.blame("doc.md")
        # Most recent entry should show the change
        assert "Changed:" in result[0].summary or "Line 1 CHANGED" in result[0].summary


# -----------------------------------------------------------------------------
# WitnessedCosmos Tests
# -----------------------------------------------------------------------------


class TestWitnessedCosmos:
    """Tests for WitnessedCosmos wrapper."""

    @pytest.mark.asyncio
    async def test_commit_creates_mark(
        self, witnessed_cosmos: WitnessedCosmos, mock_mark_store: MagicMock
    ) -> None:
        """commit() should create a Mark and store it."""
        trace = WitnessTrace.simple(actor="Kent", reasoning="Test commit")

        result = await witnessed_cosmos.commit(
            path="test.md",
            content="# Test",
            trace=trace,
        )

        # Mark store should have been called
        mock_mark_store.append.assert_called_once()

        # Result should have mark_id
        assert result.mark_id is not None
        assert result.is_witnessed

    @pytest.mark.asyncio
    async def test_commit_returns_version_id(self, witnessed_cosmos: WitnessedCosmos) -> None:
        """commit() should return valid version_id."""
        trace = WitnessTrace.simple(actor="Kent", reasoning="Test")

        result = await witnessed_cosmos.commit(
            path="test.md",
            content="# Content",
            trace=trace,
        )

        assert result.version_id.startswith("v_")
        assert result.path == "test.md"

    @pytest.mark.asyncio
    async def test_commit_without_mark_store(self, cosmos: Cosmos) -> None:
        """commit() should work without mark store (degraded mode)."""
        witnessed = WitnessedCosmos(cosmos=cosmos, mark_store=None)
        trace = WitnessTrace.simple(actor="Kent", reasoning="Test")

        result = await witnessed.commit(
            path="test.md",
            content="# Content",
            trace=trace,
        )

        # Should succeed but without mark
        assert result.version_id is not None
        assert result.mark_id is None
        assert not result.is_witnessed


# -----------------------------------------------------------------------------
# WitnessTrace Tests
# -----------------------------------------------------------------------------


class TestWitnessTrace:
    """Tests for WitnessTrace data structure."""

    def test_simple_trace(self) -> None:
        """WitnessTrace.simple() should create basic trace."""
        trace = WitnessTrace.simple(actor="Kent", reasoning="Quick fix")
        assert trace.actor == "Kent"
        assert trace.reasoning == "Quick fix"
        assert trace.kblock_id is None

    def test_kblock_trace(self) -> None:
        """WitnessTrace.from_kblock() should include kblock context."""
        trace = WitnessTrace.from_kblock(
            actor="Claude",
            kblock_id="kb_abc123",
            reasoning="Refactored",
            delta_summary="+5/-2 lines",
        )
        assert trace.actor == "Claude"
        assert trace.kblock_id == "kb_abc123"
        assert trace.delta_summary == "+5/-2 lines"
        assert "kblock" in trace.tags
        assert "save" in trace.tags


# -----------------------------------------------------------------------------
# Harness Integration Tests
# -----------------------------------------------------------------------------


class TestHarnessWitnessIntegration:
    """Tests for Harness + Witness integration."""

    @pytest.mark.asyncio
    async def test_save_without_witness(self, harness: FileOperadHarness) -> None:
        """save() should work without witness enabled."""
        block = await harness.create("test.md")
        block.set_content("# Updated")

        result = await harness.save(block, actor="Kent", reasoning="Updated")

        assert result.success
        assert result.version_id is not None
        assert result.mark_id is None  # No witness
        assert not result.is_witnessed

    @pytest.mark.asyncio
    async def test_save_with_witness(self, witnessed_harness: FileOperadHarness) -> None:
        """save() should create witness mark when enabled."""
        block = await witnessed_harness.create("test.md")
        block.set_content("# Updated")

        result = await witnessed_harness.save(block, actor="Kent", reasoning="Major update")

        assert result.success
        assert result.version_id is not None
        assert result.mark_id is not None
        assert result.is_witnessed

    @pytest.mark.asyncio
    async def test_save_result_tracks_witness(self, witnessed_harness: FileOperadHarness) -> None:
        """SaveResult.is_witnessed should reflect mark presence."""
        block = await witnessed_harness.create("test.md")
        block.set_content("# Content")

        result = await witnessed_harness.save(block, actor="Claude")

        assert result.is_witnessed is True
        assert result.mark_id is not None
        assert result.mark_id.startswith("mark-")


# -----------------------------------------------------------------------------
# get_mark_ids_for_path Tests
# -----------------------------------------------------------------------------


class TestGetMarkIdsForPath:
    """Tests for Cosmos.get_mark_ids_for_path()."""

    @pytest.mark.asyncio
    async def test_returns_empty_for_unwitnessed_history(self, cosmos: Cosmos) -> None:
        """Should return empty list when no marks."""
        await cosmos.commit("test.md", "Content", actor="Kent")

        mark_ids = await cosmos.get_mark_ids_for_path("test.md")
        assert mark_ids == []

    @pytest.mark.asyncio
    async def test_returns_mark_ids_newest_first(self, cosmos: Cosmos) -> None:
        """Should return mark IDs for witnessed commits."""
        await cosmos.commit("test.md", "v1", actor="Kent", mark_id="mark-1")
        await cosmos.commit("test.md", "v2", actor="Claude", mark_id="mark-2")
        await cosmos.commit("test.md", "v3", actor="Kent", mark_id="mark-3")

        mark_ids = await cosmos.get_mark_ids_for_path("test.md")
        assert mark_ids == ["mark-3", "mark-2", "mark-1"]  # Newest first

    @pytest.mark.asyncio
    async def test_excludes_unwitnessed_commits(self, cosmos: Cosmos) -> None:
        """Should skip commits without mark_id."""
        await cosmos.commit("test.md", "v1", mark_id="mark-1")
        await cosmos.commit("test.md", "v2")  # No mark
        await cosmos.commit("test.md", "v3", mark_id="mark-3")

        mark_ids = await cosmos.get_mark_ids_for_path("test.md")
        assert mark_ids == ["mark-3", "mark-1"]  # v2 excluded


# -----------------------------------------------------------------------------
# Law Verification
# -----------------------------------------------------------------------------


class TestWitnessLaws:
    """
    Verify Phase 2 laws from spec.

    Law: Every save CAN be witnessed (optional but available).
    Law: Witnessed saves include mark_id linking to full trace.
    Law: blame() returns traced history for auditing.
    """

    @pytest.mark.asyncio
    async def test_law_save_can_be_witnessed(self, witnessed_harness: FileOperadHarness) -> None:
        """Law: save() produces witness when enabled."""
        block = await witnessed_harness.create("law-test.md")
        block.set_content("# Law Test")

        result = await witnessed_harness.save(block, actor="Kent", reasoning="Testing witness law")

        # Witness was produced
        assert result.is_witnessed
        assert result.mark_id is not None

    @pytest.mark.asyncio
    async def test_law_mark_id_links_to_trace(
        self, witnessed_cosmos: WitnessedCosmos, mock_mark_store: MagicMock
    ) -> None:
        """Law: mark_id in cosmos links to stored mark."""
        trace = WitnessTrace.simple("Kent", "Law test")

        result = await witnessed_cosmos.commit(
            path="law.md",
            content="# Content",
            trace=trace,
        )

        # Mark was stored
        mock_mark_store.append.assert_called_once()
        stored_mark = mock_mark_store.append.call_args[0][0]
        assert str(stored_mark.id) == result.mark_id

    @pytest.mark.asyncio
    async def test_law_blame_returns_traced_history(self, cosmos: Cosmos) -> None:
        """Law: blame() returns history with mark context."""
        await cosmos.commit("audit.md", "v1", actor="Kent", mark_id="mark-audit-1")
        await cosmos.commit(
            "audit.md", "v2", actor="Claude", reasoning="Reviewed", mark_id="mark-audit-2"
        )

        blame = await cosmos.blame("audit.md")

        # History is traceable
        assert len(blame) == 2
        assert blame[0].mark_id == "mark-audit-2"
        assert blame[0].reasoning == "Reviewed"
        assert blame[1].mark_id == "mark-audit-1"
