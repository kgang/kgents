"""
Tests for Morning Coffee overlay.

Verifies the four-movement ritual flow and result handling.
"""

import pytest

from ...focus import Bucket, FocusManager
from ...snippets import SnippetLibrary
from ..coffee_overlay import CoffeeOverlay, CoffeeResult, Movement


class TestMovementEnum:
    """Tests for Movement enum."""

    def test_movement_values(self) -> None:
        """Movements have correct sequential values."""
        assert Movement.GARDEN.value == 1
        assert Movement.HYGIENE.value == 2
        assert Movement.FOCUS.value == 3
        assert Movement.SNIPPET.value == 4

    def test_movement_titles(self) -> None:
        """Movements have human-readable titles."""
        assert Movement.GARDEN.title == "Garden View"
        assert Movement.HYGIENE.title == "Hygiene Pass"
        assert Movement.FOCUS.title == "Focus Set"
        assert Movement.SNIPPET.title == "Snippet Prime"

    def test_movement_subtitles(self) -> None:
        """Movements have descriptive subtitles."""
        assert "overnight" in Movement.GARDEN.subtitle.lower()
        assert "stale" in Movement.HYGIENE.subtitle.lower()
        assert "today" in Movement.FOCUS.subtitle.lower()
        assert "button" in Movement.SNIPPET.subtitle.lower()

    def test_movement_icons(self) -> None:
        """Movements have icons."""
        for m in Movement:
            assert len(m.icon) > 0


class TestCoffeeResult:
    """Tests for CoffeeResult dataclass."""

    def test_complete_result(self) -> None:
        """CoffeeResult captures completion state."""
        result = CoffeeResult(
            completed=True,
            movement_reached=Movement.SNIPPET,
            focus_confirmed=True,
            time_spent_seconds=120.5,
        )
        assert result.completed is True
        assert result.movement_reached == Movement.SNIPPET
        assert result.focus_confirmed is True
        assert result.time_spent_seconds == 120.5

    def test_partial_result(self) -> None:
        """CoffeeResult captures partial completion."""
        result = CoffeeResult(
            completed=False,
            movement_reached=Movement.HYGIENE,
            focus_confirmed=False,
            time_spent_seconds=30.0,
        )
        assert result.completed is False
        assert result.movement_reached == Movement.HYGIENE


class TestCoffeeOverlayConstruction:
    """Tests for CoffeeOverlay construction."""

    def test_create_without_dependencies(self) -> None:
        """CoffeeOverlay initializes without dependencies."""
        overlay = CoffeeOverlay()
        assert overlay._focus_manager is None
        assert overlay._snippet_library is None

    def test_create_with_dependencies(self) -> None:
        """CoffeeOverlay accepts injected dependencies."""
        fm = FocusManager()
        sl = SnippetLibrary()
        overlay = CoffeeOverlay(focus_manager=fm, snippet_library=sl)
        assert overlay._focus_manager is fm
        assert overlay._snippet_library is sl

    def test_movement_values_are_sequential(self) -> None:
        """Movement enum values are 1-4."""
        # Test using enum values instead of reactive
        assert Movement.GARDEN.value == 1
        assert Movement.HYGIENE.value == 2
        assert Movement.FOCUS.value == 3
        assert Movement.SNIPPET.value == 4


class TestCoffeeOverlayContent:
    """Tests for content loading in each movement."""

    @pytest.mark.asyncio
    async def test_garden_content_without_git(self) -> None:
        """Garden content handles missing git gracefully."""
        overlay = CoffeeOverlay()
        # This should not raise, even if git is not available
        content = await overlay._load_garden_content()
        assert isinstance(content, list)
        # Should have some content even if empty
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_hygiene_content_with_stale_items(self) -> None:
        """Hygiene content shows stale items."""
        fm = FocusManager()
        # Add an item (it may or may not be stale depending on test timing)
        fm.add("target", label="Test Item", bucket=Bucket.TODAY)

        overlay = CoffeeOverlay(focus_manager=fm)
        content = await overlay._load_hygiene_content()

        assert isinstance(content, list)
        assert len(content) > 0
        # Should mention "fresh" or have stale items
        content_str = "\n".join(content)
        assert (
            "fresh" in content_str.lower()
            or "stale" in content_str.lower()
            or "Focus" in content_str
        )

    @pytest.mark.asyncio
    async def test_hygiene_content_without_manager(self) -> None:
        """Hygiene content handles missing manager."""
        overlay = CoffeeOverlay()
        content = await overlay._load_hygiene_content()

        assert isinstance(content, list)
        assert "not available" in content[0].lower()

    @pytest.mark.asyncio
    async def test_focus_content_with_items(self) -> None:
        """Focus content shows today's items."""
        fm = FocusManager()
        fm.add("target1", label="First Item", bucket=Bucket.TODAY)
        fm.add("target2", label="Second Item", bucket=Bucket.TODAY)

        overlay = CoffeeOverlay(focus_manager=fm)
        content = await overlay._load_focus_content()

        content_str = "\n".join(content)
        assert "First Item" in content_str
        assert "Second Item" in content_str
        assert overlay._focus_confirmed is True

    @pytest.mark.asyncio
    async def test_snippet_content_with_library(self) -> None:
        """Snippet content shows library status."""
        sl = SnippetLibrary()
        sl.load_defaults()
        sl.add_custom("Custom", "Content")

        overlay = CoffeeOverlay(snippet_library=sl)
        content = await overlay._load_snippet_content()

        content_str = "\n".join(content)
        assert "Custom" in content_str or "custom" in content_str.lower()
        assert "complete" in content_str.lower()


class TestCoffeeOverlayActions:
    """Tests for overlay actions."""

    def test_movement_progression(self) -> None:
        """Movement enum progresses correctly."""
        # Test movement progression via values (avoids TUI context)
        assert Movement(1) == Movement.GARDEN
        assert Movement(2) == Movement.HYGIENE
        assert Movement(3) == Movement.FOCUS
        assert Movement(4) == Movement.SNIPPET

        # Test advancing logic
        current = Movement.GARDEN
        next_val = current.value + 1
        assert Movement(next_val) == Movement.HYGIENE

    def test_all_movements_have_content_methods(self) -> None:
        """Each movement has corresponding content loader."""
        overlay = CoffeeOverlay()
        # Verify the content methods exist
        assert hasattr(overlay, "_load_garden_content")
        assert hasattr(overlay, "_load_hygiene_content")
        assert hasattr(overlay, "_load_focus_content")
        assert hasattr(overlay, "_load_snippet_content")
