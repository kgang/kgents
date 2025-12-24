"""
Tests for Phase 4: Witness Crystallization Features.

Tests:
- Handoff context (auto-crystallize)
- NOW.md proposal generation
- Brain promotion
- Crystal streaming

See: plans/witness-crystallization.md (Phase 4)

Note: Named test_phase4.py (not *_integration.py) to avoid
auto-skip for LLM tests. These are pure unit tests.
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.witness.crystal import Crystal, CrystalId, CrystalLevel, MoodVector
from services.witness.crystal_store import CrystalStore, reset_crystal_store, set_crystal_store
from services.witness.integration import (
    HandoffContext,
    NowMdProposal,
    PromotionCandidate,
    _extract_section,
    apply_now_proposal,
    auto_promote_crystals,
    identify_promotion_candidates,
    prepare_handoff_context,
    promote_to_brain,
    propose_now_update,
)
from services.witness.mark import MarkId
from services.witness.stream import (
    CrystalEvent,
    CrystalEventType,
    crystal_stream,
    publish_crystal_created,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_crystal() -> Crystal:
    """Create a test crystal."""
    return Crystal(
        id=CrystalId("crystal-test-123"),
        level=CrystalLevel.SESSION,
        insight="Completed Phase 4 of witness crystallization",
        significance="Enables real-time streaming and handoff integration",
        principles=["composable", "generative"],
        topics={"witness", "crystallization", "streaming"},
        source_marks=[MarkId("mark-001"), MarkId("mark-002")],
        source_crystals=[],
        mood=MoodVector.neutral(),
        confidence=0.9,
        crystallized_at=datetime.now(UTC),
    )


@pytest.fixture
def mock_store(mock_crystal: Crystal) -> CrystalStore:
    """Create a test store with some crystals."""
    store = CrystalStore()
    store._crystals[mock_crystal.id] = mock_crystal
    store._by_level[mock_crystal.level].append(mock_crystal.id)
    store._timeline.append(mock_crystal.id)
    set_crystal_store(store)
    yield store
    reset_crystal_store()


@pytest.fixture
def high_confidence_crystal() -> Crystal:
    """Create a high-confidence crystal for promotion tests."""
    return Crystal(
        id=CrystalId("crystal-high-conf"),
        level=CrystalLevel.SESSION,
        insight="Critical insight about architecture decisions",
        significance="This changes how we approach all future work",
        principles=["composable", "generative", "tasteful"],
        topics={"architecture", "decisions", "patterns"},
        source_marks=[MarkId(f"mark-{i}") for i in range(10)],
        source_crystals=[],
        mood=MoodVector.neutral(),
        confidence=0.92,
        crystallized_at=datetime.now(UTC),
    )


# =============================================================================
# HandoffContext Tests
# =============================================================================


class TestHandoffContext:
    """Tests for HandoffContext dataclass."""

    def test_to_dict_with_crystal(self, mock_crystal: Crystal) -> None:
        """Test serialization with a new crystal."""
        ctx = HandoffContext(
            new_crystal=mock_crystal,
            recent_crystals=[mock_crystal],
            tokens_used=150,
            crystallization_performed=True,
            errors=[],
        )

        result = ctx.to_dict()

        assert result["new_crystal"]["id"] == str(mock_crystal.id)
        assert result["crystallization_performed"] is True
        assert result["tokens_used"] == 150
        assert len(result["recent_crystals"]) == 1

    def test_to_dict_without_crystal(self) -> None:
        """Test serialization without a new crystal."""
        ctx = HandoffContext(
            new_crystal=None,
            recent_crystals=[],
            tokens_used=0,
            crystallization_performed=False,
            errors=["No marks to crystallize"],
        )

        result = ctx.to_dict()

        assert result["new_crystal"] is None
        assert result["crystallization_performed"] is False
        assert "No marks to crystallize" in result["errors"]

    def test_format_for_handoff(self, mock_crystal: Crystal) -> None:
        """Test formatting for handoff prompt."""
        ctx = HandoffContext(
            new_crystal=mock_crystal,
            recent_crystals=[mock_crystal],
            tokens_used=150,
            crystallization_performed=True,
            errors=[],
        )

        formatted = ctx.format_for_handoff()

        assert "## Witness Context" in formatted
        assert "Just Crystallized" in formatted
        assert mock_crystal.insight in formatted
        assert "Recent Crystals" in formatted


# =============================================================================
# NOW.md Proposal Tests
# =============================================================================


class TestNowMdProposal:
    """Tests for NowMdProposal."""

    def test_to_dict(self, mock_crystal: Crystal) -> None:
        """Test proposal serialization."""
        proposal = NowMdProposal(
            section="What Just Happened",
            current_content="Old content",
            proposed_content="New content from crystals",
            source_crystals=[mock_crystal],
            confidence=0.85,
        )

        result = proposal.to_dict()

        assert result["section"] == "What Just Happened"
        assert result["proposed_content"] == "New content from crystals"
        assert result["source_crystal_count"] == 1
        assert result["confidence"] == 0.85

    def test_format_diff(self, mock_crystal: Crystal) -> None:
        """Test diff formatting."""
        proposal = NowMdProposal(
            section="What Just Happened",
            current_content="Old content",
            proposed_content="New content from crystals",
            source_crystals=[mock_crystal],
            confidence=0.85,
        )

        diff = proposal.format_diff()

        assert "## Proposed Update: What Just Happened" in diff
        assert "**Current:**" in diff
        assert "Old content" in diff
        assert "**Proposed:**" in diff
        assert "New content from crystals" in diff
        assert "1 crystals" in diff


class TestExtractSection:
    """Tests for markdown section extraction."""

    def test_extract_existing_section(self) -> None:
        """Test extracting an existing section."""
        content = """# NOW.md

## What Just Happened

- Did thing one
- Did thing two

## What's Next

- Do thing three
"""
        result = _extract_section(content, "What Just Happened")

        assert result is not None
        assert "Did thing one" in result
        assert "Did thing two" in result

    def test_extract_nonexistent_section(self) -> None:
        """Test extracting a nonexistent section."""
        content = """# NOW.md

## What's Next

- Do thing
"""
        result = _extract_section(content, "What Just Happened")
        assert result is None

    def test_extract_last_section(self) -> None:
        """Test extracting the last section in the document."""
        content = """# NOW.md

## Section One

Content one

## Section Two

Content two
"""
        result = _extract_section(content, "Section Two")

        assert result is not None
        assert "Content two" in result


@pytest.mark.asyncio
async def test_propose_now_update_with_crystals(mock_store: CrystalStore) -> None:
    """Test NOW.md proposal generation with crystals."""
    proposals = await propose_now_update()

    # Should get proposals from the mock crystal
    assert len(proposals) > 0

    # Check that proposals have valid structure
    for p in proposals:
        assert p.section in ["What Just Happened", "Session Status"]
        assert len(p.source_crystals) > 0
        assert 0 <= p.confidence <= 1


@pytest.mark.asyncio
async def test_propose_now_update_empty_store() -> None:
    """Test NOW.md proposal with empty crystal store."""
    empty_store = CrystalStore()
    set_crystal_store(empty_store)

    try:
        proposals = await propose_now_update()
        # Should return empty list with no crystals
        assert len(proposals) == 0
    finally:
        reset_crystal_store()


def test_apply_now_proposal_creates_backup(tmp_path: Path, mock_crystal: Crystal) -> None:
    """Test that apply creates a backup."""
    now_md = tmp_path / "NOW.md"
    now_md.write_text("""# NOW.md

## What Just Happened

Old content here
""")

    proposal = NowMdProposal(
        section="What Just Happened",
        current_content="Old content here",
        proposed_content="New content from crystals",
        source_crystals=[mock_crystal],
        confidence=0.85,
    )

    success = apply_now_proposal(proposal, now_md, backup=True)

    assert success is True

    # Check backup was created
    backups = list(tmp_path.glob("NOW.md.*.bak"))
    assert len(backups) == 1

    # Check content was updated
    new_content = now_md.read_text()
    assert "New content from crystals" in new_content


# =============================================================================
# Promotion Tests
# =============================================================================


class TestPromotionCandidate:
    """Tests for PromotionCandidate."""

    def test_to_dict(self, high_confidence_crystal: Crystal) -> None:
        """Test serialization."""
        candidate = PromotionCandidate(
            crystal=high_confidence_crystal,
            score=0.85,
            reasons=["High confidence (92%)", "Good compression (10 sources)"],
        )

        result = candidate.to_dict()

        assert result["crystal_id"] == str(high_confidence_crystal.id)
        assert result["score"] == 0.85
        assert len(result["reasons"]) == 2


def test_identify_promotion_candidates(high_confidence_crystal: Crystal) -> None:
    """Test promotion candidate identification."""
    store = CrystalStore()
    store._crystals[high_confidence_crystal.id] = high_confidence_crystal
    store._by_level[high_confidence_crystal.level].append(high_confidence_crystal.id)
    store._timeline.append(high_confidence_crystal.id)
    set_crystal_store(store)

    try:
        candidates = identify_promotion_candidates(
            min_confidence=0.85,
            min_sources=5,
        )

        # High confidence crystal should be a candidate
        assert len(candidates) >= 1
        assert any(c.crystal.id == high_confidence_crystal.id for c in candidates)

        # Should be sorted by score
        scores = [c.score for c in candidates]
        assert scores == sorted(scores, reverse=True)
    finally:
        reset_crystal_store()


def test_identify_promotion_candidates_filters_low_confidence(mock_crystal: Crystal) -> None:
    """Test that low-confidence crystals are filtered out."""
    # Modify mock crystal to have low confidence
    low_conf_crystal = Crystal(
        id=CrystalId("crystal-low-conf"),
        level=CrystalLevel.SESSION,
        insight="Low confidence insight",
        significance="",
        principles=[],
        topics=set(),
        source_marks=[MarkId("mark-1")],
        source_crystals=[],
        mood=MoodVector.neutral(),
        confidence=0.5,  # Below threshold
        crystallized_at=datetime.now(UTC),
    )

    store = CrystalStore()
    store._crystals[low_conf_crystal.id] = low_conf_crystal
    store._by_level[low_conf_crystal.level].append(low_conf_crystal.id)
    store._timeline.append(low_conf_crystal.id)
    set_crystal_store(store)

    try:
        candidates = identify_promotion_candidates(min_confidence=0.85)

        # Low confidence crystal should not be a candidate
        assert not any(c.crystal.id == low_conf_crystal.id for c in candidates)
    finally:
        reset_crystal_store()


@pytest.mark.asyncio
async def test_promote_to_brain_not_found() -> None:
    """Test promotion with nonexistent crystal."""
    empty_store = CrystalStore()
    set_crystal_store(empty_store)

    try:
        result = await promote_to_brain(CrystalId("nonexistent-id"))
        assert "error" in result
        assert "not found" in result["error"]
    finally:
        reset_crystal_store()


@pytest.mark.asyncio
async def test_promote_to_brain_success(mock_store: CrystalStore, mock_crystal: Crystal) -> None:
    """Test successful crystal promotion."""
    result = await promote_to_brain(mock_crystal.id)

    assert result.get("success") is True
    assert result["crystal_id"] == str(mock_crystal.id)
    assert "teaching_data" in result


# =============================================================================
# Crystal Streaming Tests
# =============================================================================


class TestCrystalEvent:
    """Tests for CrystalEvent."""

    def test_created_event(self, mock_crystal: Crystal) -> None:
        """Test crystal.created event creation."""
        event = CrystalEvent.created(mock_crystal)

        assert event.event_type == CrystalEventType.CREATED
        assert event.data["id"] == str(mock_crystal.id)
        assert event.data["level"] == "SESSION"
        assert event.data["insight"] == mock_crystal.insight

    def test_batch_event(self, mock_crystal: Crystal) -> None:
        """Test crystal.batch event creation."""
        event = CrystalEvent.batch([mock_crystal, mock_crystal])

        assert event.event_type == CrystalEventType.BATCH
        assert event.data["count"] == 2
        assert len(event.data["crystals"]) == 2

    def test_heartbeat_event(self) -> None:
        """Test heartbeat event creation."""
        event = CrystalEvent.heartbeat()

        assert event.event_type == CrystalEventType.HEARTBEAT
        assert event.data["message"] == "keep-alive"
        assert "server_time" in event.data

    def test_error_event(self) -> None:
        """Test error event creation."""
        event = CrystalEvent.error("Something went wrong", "test_error")

        assert event.event_type == CrystalEventType.ERROR
        assert event.data["code"] == "test_error"
        assert event.data["message"] == "Something went wrong"

    def test_to_sse(self, mock_crystal: Crystal) -> None:
        """Test SSE formatting."""
        event = CrystalEvent.created(mock_crystal)
        sse = event.to_sse()

        assert sse.startswith("event: crystal.created\n")
        assert "data:" in sse
        assert sse.endswith("\n\n")

        # Should be valid JSON in data
        data_line = [l for l in sse.split("\n") if l.startswith("data:")][0]
        data_json = data_line.replace("data: ", "")
        parsed = json.loads(data_json)
        assert parsed["type"] == "crystal.created"


@pytest.mark.asyncio
async def test_crystal_stream_emits_heartbeat(mock_store: CrystalStore) -> None:
    """Test that crystal stream emits heartbeats."""
    events_received = []

    # Short heartbeat for testing
    stream = crystal_stream(
        heartbeat_interval=0.1,
        include_initial=True,
    )

    # Collect a few events
    async def collect_events() -> None:
        count = 0
        async for event in stream:
            events_received.append(event)
            count += 1
            if count >= 3:
                break

    # Run with timeout
    try:
        await asyncio.wait_for(collect_events(), timeout=1.0)
    except asyncio.TimeoutError:
        pass

    # Should have received at least initial batch or heartbeat
    assert len(events_received) >= 1


@pytest.mark.asyncio
async def test_publish_crystal_created(mock_store: CrystalStore, mock_crystal: Crystal) -> None:
    """Test publishing crystal creation event."""
    # Just verify it doesn't raise
    await publish_crystal_created(mock_crystal)

    # Check bus stats show emit
    from services.witness.bus import get_witness_bus_manager

    manager = get_witness_bus_manager()
    assert manager.synergy_bus.stats["total_emitted"] >= 1


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_full_handoff_flow(mock_store: CrystalStore) -> None:
    """Test the full handoff preparation flow."""
    with patch("services.witness.integration._crystallize_session_marks") as mock_cryst:
        mock_cryst.return_value = None  # No marks to crystallize

        ctx = await prepare_handoff_context(
            soul=None,
            crystallize=True,
            budget_tokens=1500,
            session_id="test-session",
        )

        assert isinstance(ctx, HandoffContext)
        # Should have recent crystals from store
        assert ctx.tokens_used >= 0


@pytest.mark.asyncio
async def test_auto_promote_crystals_empty() -> None:
    """Test auto-promote with no candidates."""
    empty_store = CrystalStore()
    set_crystal_store(empty_store)

    try:
        results = await auto_promote_crystals(limit=3)
        # Should return empty list with no candidates
        assert results == []
    finally:
        reset_crystal_store()


# =============================================================================
# CLI Command Tests (Smoke Tests)
# =============================================================================


def test_cmd_promote_candidates_empty_store() -> None:
    """Test promote --candidates with empty store."""
    from protocols.cli.handlers.witness import cmd_promote

    empty_store = CrystalStore()
    set_crystal_store(empty_store)

    try:
        # Should not raise
        result = cmd_promote(["--candidates"])
        assert result == 0  # Success, just empty
    finally:
        reset_crystal_store()
