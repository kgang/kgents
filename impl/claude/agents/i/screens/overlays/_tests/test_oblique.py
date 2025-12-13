"""
Tests for ObliqueStrategyOverlay.

Validates:
- Strategy selection
- Entropy threshold
- Overlay rendering
"""

from __future__ import annotations

import pytest

from ..oblique import (
    OBLIQUE_STRATEGIES,
    ObliqueStrategyOverlay,
    should_show_oblique_strategy,
)


class TestObliqueStrategies:
    """Test suite for oblique strategies data."""

    def test_strategies_exist(self) -> None:
        """Oblique strategies are defined."""
        assert len(OBLIQUE_STRATEGIES) > 0
        assert all(isinstance(s, str) for s in OBLIQUE_STRATEGIES)

    def test_strategies_are_meaningful(self) -> None:
        """All strategies have meaningful content."""
        for strategy in OBLIQUE_STRATEGIES:
            assert len(strategy) > 0
            # Should contain at least one letter
            assert any(c.isalpha() for c in strategy)

    def test_strategy_variety(self) -> None:
        """Strategies are diverse (not all the same)."""
        unique_strategies = set(OBLIQUE_STRATEGIES)
        # Should have at least 80% unique strategies
        assert len(unique_strategies) >= len(OBLIQUE_STRATEGIES) * 0.8

    def test_no_overly_long_strategies(self) -> None:
        """Strategies fit reasonably in UI."""
        for strategy in OBLIQUE_STRATEGIES:
            # Should fit in ~60 character width overlay
            assert len(strategy) < 100


class TestObliqueStrategyOverlay:
    """Test suite for ObliqueStrategyOverlay."""

    def test_overlay_creation_random(self) -> None:
        """Can create overlay with random strategy."""
        overlay = ObliqueStrategyOverlay()
        assert overlay.strategy_text in OBLIQUE_STRATEGIES

    def test_overlay_creation_specific(self) -> None:
        """Can create overlay with specific strategy."""
        strategy = "Trust in the you of now"
        overlay = ObliqueStrategyOverlay(strategy=strategy)
        assert overlay.strategy_text == strategy

    @pytest.mark.asyncio
    async def test_overlay_rendering(self) -> None:
        """Overlay renders without errors."""
        from textual.app import App

        class TestApp(App[None]):
            pass

        app = TestApp()
        async with app.run_test() as pilot:
            overlay = ObliqueStrategyOverlay(strategy="Test strategy")
            app.push_screen(overlay)

            await pilot.pause(0.05)

            # Should have rendered without crashing
            assert overlay.is_mounted

    @pytest.mark.asyncio
    async def test_new_strategy_action(self) -> None:
        """Can get a new random strategy."""
        from textual.app import App

        class TestApp(App[None]):
            pass

        app = TestApp()
        async with app.run_test() as pilot:
            overlay = ObliqueStrategyOverlay(strategy="Initial strategy")
            app.push_screen(overlay)
            await pilot.pause(0.05)

            initial = overlay.strategy_text

            # Simulate "space" key to get new strategy
            await overlay.action_new_strategy()

            # Strategy might be the same by chance, but method should work
            assert overlay.strategy_text in OBLIQUE_STRATEGIES


class TestShouldShowObliqueStrategy:
    """Test suite for should_show_oblique_strategy function."""

    def test_low_entropy_no_show(self) -> None:
        """Low entropy does not trigger oblique strategy."""
        assert not should_show_oblique_strategy(0.0)
        assert not should_show_oblique_strategy(0.5)
        assert not should_show_oblique_strategy(0.79)

    def test_high_entropy_shows(self) -> None:
        """High entropy triggers oblique strategy."""
        assert should_show_oblique_strategy(0.8)
        assert should_show_oblique_strategy(0.9)
        assert should_show_oblique_strategy(1.0)

    def test_custom_threshold(self) -> None:
        """Can use custom entropy threshold."""
        # Lower threshold (triggers more easily)
        assert should_show_oblique_strategy(0.5, threshold=0.5)
        assert should_show_oblique_strategy(0.6, threshold=0.5)

        # Higher threshold (triggers less easily)
        assert not should_show_oblique_strategy(0.8, threshold=0.9)
        assert should_show_oblique_strategy(0.95, threshold=0.9)

    def test_edge_cases(self) -> None:
        """Handles edge cases correctly."""
        # Exactly at threshold
        assert should_show_oblique_strategy(0.8, threshold=0.8)

        # Just below threshold
        assert not should_show_oblique_strategy(0.799, threshold=0.8)

        # Extreme values
        assert not should_show_oblique_strategy(-0.1, threshold=0.8)
        assert should_show_oblique_strategy(1.5, threshold=0.8)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
