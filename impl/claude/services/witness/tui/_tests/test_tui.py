"""
Tests for Witness TUI Components.

Tests the Crystal Navigator TUI with:
- Navigation (j/k)
- Level filtering (0-3, a)
- Crystal selection and detail display
- Human-friendly age formatting

See: plans/witness-dashboard-tui.md
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from services.witness.crystal import Crystal, CrystalLevel, MoodVector, generate_crystal_id
from services.witness.mark import MarkId
from services.witness.tui.crystal_list import LEVEL_COLORS, LEVEL_NAMES, CrystalListPane, format_age
from services.witness.tui.hint_bar import HintBar

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_crystals() -> list[Crystal]:
    """Create sample crystals for testing."""
    now = datetime.now()

    return [
        Crystal(
            id=generate_crystal_id(),
            level=CrystalLevel.SESSION,
            insight="Completed extinction audit, removed 52K lines",
            significance="Codebase is leaner, focus is sharper",
            principles=("tasteful", "curated"),
            source_marks=(MarkId("mark-1"), MarkId("mark-2")),
            crystallized_at=now - timedelta(minutes=3),
            confidence=0.95,
            token_estimate=150,
        ),
        Crystal(
            id=generate_crystal_id(),
            level=CrystalLevel.SESSION,
            insight="Hardened Brain persistence layer",
            significance="Data integrity improved",
            principles=("composable",),
            source_marks=(MarkId("mark-3"),),
            crystallized_at=now - timedelta(hours=1),
            confidence=0.88,
            token_estimate=120,
        ),
        Crystal(
            id=generate_crystal_id(),
            level=CrystalLevel.DAY,
            insight="Major codebase cleanup completed",
            significance="Foundation for Phase 5",
            principles=("curated", "generative"),
            source_crystals=(),
            source_marks=(),
            crystallized_at=now - timedelta(hours=5),
            confidence=0.92,
            token_estimate=180,
        ),
    ]


# =============================================================================
# Age Formatting Tests (Pattern 14)
# =============================================================================


class TestFormatAge:
    """Tests for human-friendly age formatting."""

    def test_format_age_now(self) -> None:
        """Less than 1 minute shows 'now'."""
        dt = datetime.now() - timedelta(seconds=30)
        assert format_age(dt) == "now"

    def test_format_age_minutes(self) -> None:
        """Minutes show as 'Nm'."""
        dt = datetime.now() - timedelta(minutes=5)
        assert format_age(dt) == "5m"

    def test_format_age_hours(self) -> None:
        """Hours show as 'Nh'."""
        dt = datetime.now() - timedelta(hours=3)
        assert format_age(dt) == "3h"

    def test_format_age_days(self) -> None:
        """Days show as 'Nd'."""
        dt = datetime.now() - timedelta(days=2)
        assert format_age(dt) == "2d"

    def test_format_age_weeks(self) -> None:
        """Weeks show as 'Nw'."""
        dt = datetime.now() - timedelta(days=14)
        assert format_age(dt) == "2w"


# =============================================================================
# Level Constants Tests
# =============================================================================


class TestLevelConstants:
    """Tests for level colors and names."""

    def test_level_colors_complete(self) -> None:
        """All levels have colors."""
        for level in CrystalLevel:
            assert level.value in LEVEL_COLORS

    def test_level_names_complete(self) -> None:
        """All levels have names."""
        for level in CrystalLevel:
            assert level.value in LEVEL_NAMES

    def test_level_names_match_enum(self) -> None:
        """Level names match enum names."""
        assert LEVEL_NAMES[0] == "SESSION"
        assert LEVEL_NAMES[1] == "DAY"
        assert LEVEL_NAMES[2] == "WEEK"
        assert LEVEL_NAMES[3] == "EPOCH"


# =============================================================================
# HintBar Tests (Pattern 12)
# =============================================================================


class TestHintBar:
    """Tests for context-aware hint bar."""

    def test_default_hints(self) -> None:
        """HintBar has default hints."""
        bar = HintBar()
        assert "j/k" in bar._hints
        assert "quit" in bar._hints

    def test_set_mode_normal(self) -> None:
        """Set mode to normal updates hints."""
        bar = HintBar()
        bar.set_mode("normal")
        assert "j/k" in bar._hints

    def test_set_mode_filter(self) -> None:
        """Set mode to filter updates hints."""
        bar = HintBar()
        bar.set_mode("filter")
        assert "SESSION" in bar._hints
        assert "DAY" in bar._hints


# =============================================================================
# CrystalListPane Tests (Pattern 18)
# =============================================================================


class TestCrystalListPane:
    """Tests for crystal list navigation and display."""

    def test_set_crystals(self, sample_crystals: list[Crystal]) -> None:
        """Setting crystals updates the list."""
        pane = CrystalListPane()
        pane.set_crystals(sample_crystals)
        assert len(pane._crystals) == 3
        assert pane.selected_index == 0

    def test_selected_crystal(self, sample_crystals: list[Crystal]) -> None:
        """Selected crystal returns correct crystal."""
        pane = CrystalListPane()
        pane.set_crystals(sample_crystals)
        assert pane.selected_crystal == sample_crystals[0]

    def test_select_next(self, sample_crystals: list[Crystal]) -> None:
        """Selecting next moves selection down."""
        pane = CrystalListPane()
        pane.set_crystals(sample_crystals)
        pane.select_next()
        assert pane.selected_index == 1
        assert pane.selected_crystal == sample_crystals[1]

    def test_select_previous(self, sample_crystals: list[Crystal]) -> None:
        """Selecting previous moves selection up."""
        pane = CrystalListPane()
        pane.set_crystals(sample_crystals)
        pane.selected_index = 2
        pane.select_previous()
        assert pane.selected_index == 1

    def test_select_next_at_end(self, sample_crystals: list[Crystal]) -> None:
        """Selecting next at end stays at end."""
        pane = CrystalListPane()
        pane.set_crystals(sample_crystals)
        pane.selected_index = 2
        pane.select_next()
        assert pane.selected_index == 2  # Doesn't go beyond end

    def test_select_previous_at_start(self, sample_crystals: list[Crystal]) -> None:
        """Selecting previous at start stays at start."""
        pane = CrystalListPane()
        pane.set_crystals(sample_crystals)
        pane.select_previous()
        assert pane.selected_index == 0  # Doesn't go negative

    def test_empty_list_selected_crystal(self) -> None:
        """Empty list returns None for selected crystal."""
        pane = CrystalListPane()
        pane.set_crystals([])
        assert pane.selected_crystal is None


# =============================================================================
# Integration Tests (Async Textual)
# =============================================================================


@pytest.mark.asyncio
async def test_app_launch_and_quit(sample_crystals: list[Crystal]) -> None:
    """Test that app can launch and quit cleanly."""
    from services.witness.tui.app import WitnessDashApp

    app = WitnessDashApp()

    async with app.run_test() as pilot:
        # App should be running
        assert app.is_running

        # Quit the app
        await pilot.press("q")


@pytest.mark.asyncio
async def test_vim_navigation(sample_crystals: list[Crystal]) -> None:
    """Test j/k navigation in crystal list."""
    from services.witness.crystal_store import CrystalStore, set_crystal_store
    from services.witness.tui.app import WitnessDashApp

    # Create a test store with crystals
    store = CrystalStore()
    for crystal in sample_crystals:
        store._crystals[crystal.id] = crystal
        store._by_level[crystal.level].append(crystal.id)
        store._timeline.append(crystal.id)

    set_crystal_store(store)

    try:
        app = WitnessDashApp()

        async with app.run_test() as pilot:
            # Wait for crystals to load
            await pilot.pause()

            # Get the list pane
            list_pane = app.query_one("#crystal-list", CrystalListPane)

            # Initial selection is at 0
            assert list_pane.selected_index == 0

            # Press j to move down
            await pilot.press("j")
            assert list_pane.selected_index == 1

            # Press k to move back up
            await pilot.press("k")
            assert list_pane.selected_index == 0

            await pilot.press("q")
    finally:
        from services.witness.crystal_store import reset_crystal_store

        reset_crystal_store()


@pytest.mark.asyncio
async def test_level_filtering() -> None:
    """Test level filter changes via keyboard."""
    from services.witness.tui.app import WitnessDashApp

    app = WitnessDashApp()

    async with app.run_test() as pilot:
        # Initial filter is None (all)
        assert app.level_filter is None

        # Press 0 for SESSION filter
        await pilot.press("0")
        assert app.level_filter == 0

        # Press 1 for DAY filter
        await pilot.press("1")
        assert app.level_filter == 1

        # Press a for all
        await pilot.press("a")
        assert app.level_filter is None

        await pilot.press("q")


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "TestFormatAge",
    "TestLevelConstants",
    "TestHintBar",
    "TestCrystalListPane",
]
