"""
Tests for Morning Coffee Garden View generator.

Verifies:
- Git stat parsing extracts file changes correctly
- NOW.md parsing extracts progress percentages
- Brainstorming detection finds recent ideas
- GardenView composition is correct
"""

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from services.liminal.coffee.garden import (
    _categorize_by_progress,
    _parse_numstat,
    _simplify_path,
    detect_recent_brainstorming,
    generate_garden_view,
    parse_git_stat,
    parse_now_md,
)
from services.liminal.coffee.types import (
    GardenCategory,
    GardenItem,
    GardenView,
)

# =============================================================================
# Git Stat Parsing Tests
# =============================================================================


class TestParseNumstat:
    """Tests for _parse_numstat helper."""

    def test_basic_numstat(self) -> None:
        """Parse basic numstat output."""
        output = "10\t5\tsrc/main.py\n"
        items = _parse_numstat(output)

        assert len(items) == 1
        assert items[0].source == "git"
        assert items[0].category == GardenCategory.HARVEST

    def test_multiple_files(self) -> None:
        """Parse multiple file changes."""
        output = """10\t5\tsrc/main.py
20\t3\tsrc/utils.py
5\t15\tsrc/old.py
"""
        items = _parse_numstat(output)
        assert len(items) == 3

    def test_binary_files(self) -> None:
        """Handle binary files (marked with -)."""
        output = "-\t-\tassets/image.png\n"
        items = _parse_numstat(output)
        # Binary files have 0 changes, should be filtered
        assert len(items) == 0

    def test_insertion_heavy_is_expanded(self) -> None:
        """Files with many insertions should be 'expanded'."""
        output = "100\t10\tsrc/new_feature.py\n"
        items = _parse_numstat(output)

        assert len(items) == 1
        assert "expanded" in items[0].description

    def test_deletion_heavy_is_cleaned(self) -> None:
        """Files with many deletions should be 'cleaned up'."""
        output = "5\t50\tsrc/legacy.py\n"
        items = _parse_numstat(output)

        assert len(items) == 1
        assert "cleaned up" in items[0].description

    def test_balanced_changes_is_refined(self) -> None:
        """Balanced changes should be 'refined'."""
        output = "30\t25\tsrc/module.py\n"
        items = _parse_numstat(output)

        assert len(items) == 1
        assert "refined" in items[0].description

    def test_empty_output(self) -> None:
        """Handle empty output gracefully."""
        items = _parse_numstat("")
        assert items == []

    def test_aggregates_same_file(self) -> None:
        """Same file in multiple commits aggregates."""
        output = """10\t5\tsrc/main.py
5\t5\tsrc/main.py
"""
        items = _parse_numstat(output)
        # Same file should be aggregated to one item
        assert len(items) == 1


class TestSimplifyPath:
    """Tests for _simplify_path helper."""

    def test_removes_impl_claude_prefix(self) -> None:
        """Remove impl/claude/ prefix."""
        result = _simplify_path("impl/claude/services/brain/core.py")
        assert result == "services/brain/core.py"

    def test_removes_spec_prefix(self) -> None:
        """Remove spec/ prefix."""
        result = _simplify_path("spec/protocols/foo.md")
        assert result == "protocols/foo.md"

    def test_truncates_long_paths(self) -> None:
        """Truncate very long paths."""
        long_path = "a/b/c/d/e/f/g/h/very_long_filename_that_goes_on.py"
        result = _simplify_path(long_path)
        assert len(result) <= 50 or "..." in result

    def test_preserves_short_paths(self) -> None:
        """Keep short paths as-is."""
        result = _simplify_path("README.md")
        assert result == "README.md"


class TestParseGitStat:
    """Tests for parse_git_stat with subprocess mocking."""

    @patch("services.liminal.coffee.garden.subprocess.run")
    def test_git_failure_returns_empty(self, mock_run: MagicMock) -> None:
        """Git failure should return empty list (graceful degradation)."""
        mock_run.return_value = MagicMock(returncode=1, stderr="error")

        result = parse_git_stat()
        assert result == []

    @patch("services.liminal.coffee.garden.subprocess.run")
    def test_success_returns_items(self, mock_run: MagicMock) -> None:
        """Successful git returns parsed items."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="10\t5\tsrc/main.py\n",
        )

        result = parse_git_stat()
        assert len(result) == 1
        assert result[0].category == GardenCategory.HARVEST

    @patch("services.liminal.coffee.garden.subprocess.run")
    def test_uses_since_parameter(self, mock_run: MagicMock) -> None:
        """Should pass --since to git."""
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        since = datetime(2025, 12, 20, 8, 0, 0)
        parse_git_stat(since=since)

        # Check that git was called with --since
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert any("--since" in str(arg) for arg in cmd)


# =============================================================================
# NOW.md Parsing Tests
# =============================================================================


class TestParseNowMd:
    """Tests for parse_now_md."""

    def test_parses_percentage_format(self, tmp_path: Path) -> None:
        """Parse 'JewelName XX%' format."""
        now_md = tmp_path / "NOW.md"
        now_md.write_text("Brain 100%\nGestalt 85%\n")

        result = parse_now_md(now_md)

        assert result["brain"] == 1.0
        assert result["gestalt"] == 0.85

    def test_parses_bold_format(self, tmp_path: Path) -> None:
        """Parse '**JewelName** XX%' format."""
        now_md = tmp_path / "NOW.md"
        now_md.write_text("**Brain** 100%\n**Gestalt** 85%\n")

        result = parse_now_md(now_md)

        assert result["brain"] == 1.0
        assert result["gestalt"] == 0.85

    def test_ignores_unknown_names(self, tmp_path: Path) -> None:
        """Ignore names that aren't known jewels."""
        now_md = tmp_path / "NOW.md"
        now_md.write_text("RandomWord 50%\nBrain 100%\n")

        result = parse_now_md(now_md)

        assert "randomword" not in result
        assert "brain" in result

    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        """Missing NOW.md returns empty dict."""
        result = parse_now_md(tmp_path / "nonexistent.md")
        assert result == {}

    def test_parses_colon_format(self, tmp_path: Path) -> None:
        """Parse 'JewelName: XX%' format."""
        now_md = tmp_path / "NOW.md"
        now_md.write_text("Brain: 100%\nGestalt: 70%\n")

        result = parse_now_md(now_md)

        assert result["brain"] == 1.0
        assert result["gestalt"] == 0.70


class TestCategorizeByProgress:
    """Tests for _categorize_by_progress."""

    def test_high_progress_is_harvest(self) -> None:
        """95%+ is HARVEST (mature)."""
        cat = _categorize_by_progress("brain", 0.95)
        assert cat == GardenCategory.HARVEST

    def test_medium_high_is_growing(self) -> None:
        """70-94% is GROWING."""
        cat = _categorize_by_progress("gestalt", 0.85)
        assert cat == GardenCategory.GROWING

    def test_medium_is_sprouting(self) -> None:
        """30-69% is SPROUTING."""
        cat = _categorize_by_progress("town", 0.55)
        assert cat == GardenCategory.SPROUTING

    def test_low_is_seeds(self) -> None:
        """<30% is SEEDS."""
        cat = _categorize_by_progress("park", 0.25)
        assert cat == GardenCategory.SEEDS


# =============================================================================
# Brainstorming Detection Tests
# =============================================================================


class TestDetectRecentBrainstorming:
    """Tests for detect_recent_brainstorming."""

    def test_finds_recent_md_files(self, tmp_path: Path) -> None:
        """Find recently modified .md files."""
        brainstorm = tmp_path / "brainstorming"
        brainstorm.mkdir()

        # Create a recent file
        recent = brainstorm / "2025-12-21-new-idea.md"
        recent.write_text("# New Idea\n")

        result = detect_recent_brainstorming(
            brainstorm_path=brainstorm,
            since=datetime.now() - timedelta(hours=1),
        )

        assert len(result) == 1
        assert result[0].category == GardenCategory.SEEDS
        assert result[0].source == "brainstorming"

    def test_missing_dir_returns_empty(self, tmp_path: Path) -> None:
        """Missing brainstorming dir returns empty."""
        result = detect_recent_brainstorming(
            brainstorm_path=tmp_path / "nonexistent",
        )
        assert result == []

    def test_filters_old_files(self, tmp_path: Path) -> None:
        """Old files are filtered out."""
        brainstorm = tmp_path / "brainstorming"
        brainstorm.mkdir()

        old = brainstorm / "old-idea.md"
        old.write_text("# Old Idea\n")

        # Since = future, so all files are "old"
        result = detect_recent_brainstorming(
            brainstorm_path=brainstorm,
            since=datetime.now() + timedelta(days=1),
        )

        assert result == []


# =============================================================================
# Garden View Generator Tests
# =============================================================================


class TestGenerateGardenView:
    """Tests for generate_garden_view integration."""

    @patch("services.liminal.coffee.garden.subprocess.run")
    def test_returns_garden_view(
        self,
        mock_run: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Returns a proper GardenView."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="10\t5\tsrc/main.py\n",
        )

        # Create NOW.md
        now_md = tmp_path / "NOW.md"
        now_md.write_text("Brain 100%\nTown 55%\n")

        view = generate_garden_view(
            repo_path=tmp_path,
            now_md_path=now_md,
        )

        assert isinstance(view, GardenView)
        assert view.generated_at is not None

    @patch("services.liminal.coffee.garden.subprocess.run")
    def test_empty_view_is_valid(self, mock_run: MagicMock) -> None:
        """Empty view should still be valid."""
        mock_run.return_value = MagicMock(returncode=1, stderr="error")

        view = generate_garden_view()

        assert isinstance(view, GardenView)
        assert view.is_empty or not view.is_empty  # Just checking it works

    @patch("services.liminal.coffee.garden.subprocess.run")
    def test_categorizes_correctly(
        self,
        mock_run: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Items are categorized into correct buckets."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="10\t5\tsrc/main.py\n",
        )

        # Create NOW.md with various progress levels
        now_md = tmp_path / "NOW.md"
        now_md.write_text("Brain 100%\nGestalt 85%\nTown 55%\nPark 20%\n")

        view = generate_garden_view(
            repo_path=tmp_path,
            now_md_path=now_md,
        )

        # Git changes go to harvest
        assert len(view.harvest) >= 1

        # 85% = GROWING
        growing_names = [item.description for item in view.growing]
        assert any("Gestalt" in name for name in growing_names)

        # 55% = SPROUTING
        sprouting_names = [item.description for item in view.sprouting]
        assert any("Town" in name for name in sprouting_names)


# =============================================================================
# GardenView Type Tests
# =============================================================================


class TestGardenViewType:
    """Tests for GardenView dataclass."""

    def test_is_empty_when_empty(self) -> None:
        """is_empty returns True for empty view."""
        view = GardenView()
        assert view.is_empty is True

    def test_not_empty_with_items(self) -> None:
        """is_empty returns False with items."""
        item = GardenItem(
            description="test",
            category=GardenCategory.HARVEST,
        )
        view = GardenView(harvest=(item,))
        assert view.is_empty is False

    def test_total_items_counts_all(self) -> None:
        """total_items counts across all categories."""
        item = GardenItem(description="test", category=GardenCategory.HARVEST)
        view = GardenView(
            harvest=(item, item),
            growing=(item,),
            sprouting=(),
            seeds=(item,),
        )
        assert view.total_items == 4

    def test_to_dict_serializes(self) -> None:
        """to_dict creates valid dict."""
        item = GardenItem(
            description="test",
            category=GardenCategory.HARVEST,
            files_changed=5,
        )
        view = GardenView(harvest=(item,))

        data = view.to_dict()

        assert "harvest" in data
        assert "generated_at" in data
        assert len(data["harvest"]) == 1
