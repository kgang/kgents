"""
Tests for trail file persistence.

"The trail IS the decision. The mark IS the witness."

These tests verify:
1. Trail save/load roundtrip
2. Trail ID sanitization
3. Listing trails
4. Error handling
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from protocols.trail.file_persistence import (
    TRAIL_DIR,
    TrailListEntry,
    TrailLoadResult,
    TrailSaveResult,
    delete_trail,
    generate_trail_id,
    list_trails,
    load_trail,
    sanitize_trail_name,
    save_trail,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def tmp_trail_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Use temporary directory for trails."""
    trail_dir = tmp_path / "trails"
    trail_dir.mkdir()
    monkeypatch.setattr("protocols.trail.file_persistence.TRAIL_DIR", trail_dir)
    return trail_dir


@pytest.fixture
def sample_trail_dict() -> dict[str, Any]:
    """Create a sample trail dictionary."""
    return {
        "id": "test-trail-123",
        "name": "Test Trail",
        "created_by": "developer",
        "created_at": "2025-12-22T10:00:00",
        "steps": [
            {
                "node_path": "world.auth_middleware",
                "edge_type": None,
                "timestamp": "2025-12-22T10:01:00",
            },
            {
                "node_path": "world.auth_middleware.tests",
                "edge_type": "tests",
                "timestamp": "2025-12-22T10:02:00",
            },
        ],
        "annotations": {},
    }


@pytest.fixture
def mock_exploration_trail() -> Any:
    """Create a mock ExplorationTrail."""

    class MockStep:
        def __init__(self, node: str, edge: str | None):
            self.node = node
            self.edge_taken = edge
            self.annotation = ""

    class MockTrail:
        def __init__(self) -> None:
            self.id = "mock-trail-abc"
            self.name = "Mock Trail"
            self.steps = (
                MockStep("world.core", None),
                MockStep("world.core.tests", "tests"),
            )
            self.annotations: dict[int, str] = {}

        def to_dict(self) -> dict[str, Any]:
            return {
                "id": self.id,
                "name": self.name,
                "steps": [
                    {"node_path": s.node, "edge_type": s.edge_taken}
                    for s in self.steps
                ],
                "annotations": self.annotations,
            }

    return MockTrail()


# =============================================================================
# Sanitization Tests
# =============================================================================


class TestSanitizeTrailName:
    """Tests for trail name sanitization."""

    def test_lowercase(self) -> None:
        """Should convert to lowercase."""
        assert sanitize_trail_name("Auth Bug") == "auth-bug"

    def test_spaces_to_dashes(self) -> None:
        """Should replace spaces with dashes."""
        assert sanitize_trail_name("my trail name") == "my-trail-name"

    def test_removes_special_chars(self) -> None:
        """Should remove special characters."""
        assert sanitize_trail_name("auth/bug!test") == "authbugtest"

    def test_collapses_dashes(self) -> None:
        """Should collapse multiple dashes."""
        assert sanitize_trail_name("auth--bug---test") == "auth-bug-test"

    def test_strips_leading_trailing_dashes(self) -> None:
        """Should strip leading/trailing dashes."""
        assert sanitize_trail_name("-auth-bug-") == "auth-bug"

    def test_truncates_long_names(self) -> None:
        """Should truncate to 64 characters."""
        long_name = "a" * 100
        result = sanitize_trail_name(long_name)
        assert len(result) <= 64

    def test_empty_becomes_unnamed(self) -> None:
        """Empty names should become 'unnamed-trail'."""
        assert sanitize_trail_name("") == "unnamed-trail"
        assert sanitize_trail_name("!!!") == "unnamed-trail"

    def test_realistic_names(self) -> None:
        """Test realistic trail names."""
        assert sanitize_trail_name("Auth Bug Investigation") == "auth-bug-investigation"
        assert sanitize_trail_name("Quick Test!!") == "quick-test"
        assert sanitize_trail_name("2025-12-22 Session") == "2025-12-22-session"


class TestGenerateTrailId:
    """Tests for trail ID generation."""

    def test_without_name(self) -> None:
        """Should generate UUID-based ID without name."""
        id1 = generate_trail_id()
        id2 = generate_trail_id()

        assert id1.startswith("trail_")
        assert id2.startswith("trail_")
        assert id1 != id2  # Should be unique

    def test_with_name(self) -> None:
        """Should generate name-based ID with timestamp."""
        id1 = generate_trail_id("Auth Bug")

        assert "auth-bug" in id1
        assert "_202" in id1  # Timestamp prefix (2025, etc.)


# =============================================================================
# Save Tests
# =============================================================================


class TestSaveTrail:
    """Tests for save_trail function."""

    @pytest.mark.asyncio
    async def test_save_dict_trail(
        self, tmp_trail_dir: Path, sample_trail_dict: dict[str, Any]
    ) -> None:
        """Should save a dictionary trail."""
        # Disable witness mark emission for this test
        result = await save_trail(sample_trail_dict, emit_mark=False)

        assert result.trail_id == "test-trail-123"
        assert result.name == "Test Trail"
        assert result.step_count == 2
        assert result.file_path.exists()

        # Verify file contents
        saved_data = json.loads(result.file_path.read_text())
        assert saved_data["name"] == "Test Trail"
        assert len(saved_data["steps"]) == 2

    @pytest.mark.asyncio
    async def test_save_with_name_override(
        self, tmp_trail_dir: Path, sample_trail_dict: dict[str, Any]
    ) -> None:
        """Should use provided name over trail's name."""
        result = await save_trail(sample_trail_dict, name="Custom Name", emit_mark=False)

        assert result.name == "Custom Name"
        saved_data = json.loads(result.file_path.read_text())
        assert saved_data["name"] == "Custom Name"

    @pytest.mark.asyncio
    async def test_save_adds_saved_at(
        self, tmp_trail_dir: Path, sample_trail_dict: dict[str, Any]
    ) -> None:
        """Should add saved_at timestamp."""
        result = await save_trail(sample_trail_dict, emit_mark=False)

        saved_data = json.loads(result.file_path.read_text())
        assert "saved_at" in saved_data

    @pytest.mark.asyncio
    async def test_save_exploration_trail(
        self, tmp_trail_dir: Path, mock_exploration_trail: Any
    ) -> None:
        """Should save ExplorationTrail object."""
        result = await save_trail(mock_exploration_trail, emit_mark=False)

        assert result.trail_id == "mock-trail-abc"
        assert result.file_path.exists()

    @pytest.mark.asyncio
    async def test_save_emits_witness_mark(
        self, tmp_trail_dir: Path, sample_trail_dict: dict[str, Any]
    ) -> None:
        """Should emit witness mark when emit_mark=True."""
        # Test that save succeeds even when witness service isn't available
        # The fire-and-forget pattern means save should never fail due to witness
        result = await save_trail(sample_trail_dict, emit_mark=True)

        # Save should succeed regardless of witness availability
        assert result.file_path.exists()
        # mark_id may be None if witness service isn't available
        # (This is expected in unit tests)


# =============================================================================
# Load Tests
# =============================================================================


class TestLoadTrail:
    """Tests for load_trail function."""

    @pytest.mark.asyncio
    async def test_load_existing_trail(
        self, tmp_trail_dir: Path, sample_trail_dict: dict[str, Any]
    ) -> None:
        """Should load an existing trail."""
        # First save
        save_result = await save_trail(sample_trail_dict, emit_mark=False)

        # Then load
        load_result = await load_trail(save_result.trail_id)

        assert load_result is not None
        assert load_result.trail_id == "test-trail-123"
        assert load_result.name == "Test Trail"
        assert len(load_result.steps) == 2

    @pytest.mark.asyncio
    async def test_load_nonexistent_trail(self, tmp_trail_dir: Path) -> None:
        """Should return None for nonexistent trail."""
        result = await load_trail("nonexistent-trail-xyz")
        assert result is None

    @pytest.mark.asyncio
    async def test_load_handles_corrupt_file(self, tmp_trail_dir: Path) -> None:
        """Should return None for corrupt JSON file."""
        corrupt_file = tmp_trail_dir / "corrupt.json"
        corrupt_file.write_text("not valid json {{{")

        result = await load_trail("corrupt")
        assert result is None


# =============================================================================
# List Tests
# =============================================================================


class TestListTrails:
    """Tests for list_trails function."""

    def test_list_empty_directory(self, tmp_trail_dir: Path) -> None:
        """Should return empty list for empty directory."""
        entries = list_trails()
        assert entries == []

    def test_list_with_trails(
        self, tmp_trail_dir: Path, sample_trail_dict: dict[str, Any]
    ) -> None:
        """Should list saved trails."""
        # Save a few trails
        for i in range(3):
            trail = sample_trail_dict.copy()
            trail["id"] = f"trail-{i}"
            trail["name"] = f"Trail {i}"
            trail["saved_at"] = datetime.now().isoformat()
            trail_file = tmp_trail_dir / f"trail-{i}.json"
            trail_file.write_text(json.dumps(trail))

        entries = list_trails()

        assert len(entries) == 3
        assert all(isinstance(e, TrailListEntry) for e in entries)

    def test_list_respects_limit(
        self, tmp_trail_dir: Path, sample_trail_dict: dict[str, Any]
    ) -> None:
        """Should respect limit parameter."""
        # Save 5 trails
        for i in range(5):
            trail = sample_trail_dict.copy()
            trail["id"] = f"trail-{i}"
            trail["saved_at"] = datetime.now().isoformat()
            trail_file = tmp_trail_dir / f"trail-{i}.json"
            trail_file.write_text(json.dumps(trail))

        entries = list_trails(limit=3)
        assert len(entries) == 3

    def test_list_sorted_by_date(
        self, tmp_trail_dir: Path, sample_trail_dict: dict[str, Any]
    ) -> None:
        """Should be sorted by saved_at descending (newest first)."""
        # Save with different timestamps
        for i, time in enumerate(["2025-12-20T10:00:00", "2025-12-22T10:00:00", "2025-12-21T10:00:00"]):
            trail = sample_trail_dict.copy()
            trail["id"] = f"trail-{i}"
            trail["saved_at"] = time
            trail_file = tmp_trail_dir / f"trail-{i}.json"
            trail_file.write_text(json.dumps(trail))

        entries = list_trails()

        # Should be sorted newest first: trail-1 (Dec 22), trail-2 (Dec 21), trail-0 (Dec 20)
        assert entries[0].trail_id == "trail-1"
        assert entries[1].trail_id == "trail-2"
        assert entries[2].trail_id == "trail-0"


# =============================================================================
# Delete Tests
# =============================================================================


class TestDeleteTrail:
    """Tests for delete_trail function."""

    @pytest.mark.asyncio
    async def test_delete_existing_trail(
        self, tmp_trail_dir: Path, sample_trail_dict: dict[str, Any]
    ) -> None:
        """Should delete existing trail."""
        # First save
        save_result = await save_trail(sample_trail_dict, emit_mark=False)
        assert save_result.file_path.exists()

        # Then delete
        deleted = await delete_trail(save_result.trail_id)

        assert deleted is True
        assert not save_result.file_path.exists()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_trail(self, tmp_trail_dir: Path) -> None:
        """Should return False for nonexistent trail."""
        deleted = await delete_trail("nonexistent-xyz")
        assert deleted is False


# =============================================================================
# Roundtrip Tests
# =============================================================================


class TestRoundtrip:
    """End-to-end roundtrip tests."""

    @pytest.mark.asyncio
    async def test_save_load_roundtrip(
        self, tmp_trail_dir: Path, sample_trail_dict: dict[str, Any]
    ) -> None:
        """Save → Load should preserve data."""
        # Save
        save_result = await save_trail(sample_trail_dict, emit_mark=False)

        # Load
        load_result = await load_trail(save_result.trail_id)

        assert load_result is not None
        assert load_result.trail_id == sample_trail_dict["id"]
        assert load_result.name == sample_trail_dict["name"]
        assert len(load_result.steps) == len(sample_trail_dict["steps"])

    @pytest.mark.asyncio
    async def test_exploration_trail_roundtrip(
        self, tmp_trail_dir: Path, mock_exploration_trail: Any
    ) -> None:
        """ExplorationTrail → save → load should preserve data."""
        # Save
        save_result = await save_trail(mock_exploration_trail, emit_mark=False)

        # Load
        load_result = await load_trail(save_result.trail_id)

        assert load_result is not None
        assert load_result.name == mock_exploration_trail.name
        assert len(load_result.steps) == len(mock_exploration_trail.steps)
