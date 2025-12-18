"""
Tests for H-gent reactive cards.

Tests for ShadowCardWidget and DialecticCardWidget.
"""

from __future__ import annotations

import pytest

from agents.i.reactive.primitives.hgent_card import (
    DialecticCardState,
    DialecticCardWidget,
    ShadowCardState,
    ShadowCardWidget,
    ShadowItem,
)
from agents.i.reactive.widget import RenderTarget

# === ShadowCard Tests ===


class TestShadowCardWidget:
    """Tests for ShadowCardWidget."""

    def test_shadow_card_default_state(self) -> None:
        """Shadow card can be created with default state."""
        card = ShadowCardWidget()
        state = card.state.value

        assert state.title == "Shadow Analysis"
        assert state.balance == 0.5
        assert state.shadow_inventory == ()

    def test_shadow_card_with_inventory(self) -> None:
        """Shadow card with shadow inventory."""
        items = (
            ShadowItem("capacity for harm", "helpful identity", "high"),
            ShadowItem("tendency to guess", "accuracy identity", "medium"),
        )
        card = ShadowCardWidget(ShadowCardState(shadow_inventory=items, balance=0.3))

        state = card.state.value
        assert len(state.shadow_inventory) == 2
        assert state.balance == 0.3

    def test_shadow_card_cli_projection(self) -> None:
        """Shadow card projects to CLI."""
        items = (ShadowItem("test shadow", "test reason", "low"),)
        card = ShadowCardWidget(ShadowCardState(shadow_inventory=items))

        output = card.project(RenderTarget.CLI)

        assert isinstance(output, str)
        assert "Shadow Analysis" in output
        assert "test shadow" in output

    def test_shadow_card_json_projection(self) -> None:
        """Shadow card projects to JSON."""
        items = (ShadowItem("test shadow", "test reason", "medium"),)
        card = ShadowCardWidget(ShadowCardState(shadow_inventory=items, balance=0.7))

        output = card.project(RenderTarget.JSON)

        assert isinstance(output, dict)
        assert output["type"] == "shadow_card"
        assert output["balance"] == 0.7
        assert len(output["shadow_inventory"]) == 1
        assert output["shadow_inventory"][0]["content"] == "test shadow"

    def test_shadow_card_with_balance_immutable(self) -> None:
        """with_balance returns new card without modifying original."""
        card = ShadowCardWidget(ShadowCardState(balance=0.5))
        new_card = card.with_balance(0.8)

        assert card.state.value.balance == 0.5
        assert new_card.state.value.balance == 0.8

    def test_shadow_card_balance_clamped(self) -> None:
        """Balance is clamped to 0.0-1.0 range."""
        card = ShadowCardWidget()

        low_card = card.with_balance(-0.5)
        high_card = card.with_balance(1.5)

        assert low_card.state.value.balance == 0.0
        assert high_card.state.value.balance == 1.0

    def test_shadow_card_marimo_projection(self) -> None:
        """Shadow card projects to MARIMO (HTML)."""
        card = ShadowCardWidget(
            ShadowCardState(shadow_inventory=(ShadowItem("test", "reason", "high"),))
        )

        output = card.project(RenderTarget.MARIMO)

        assert isinstance(output, str)
        assert "kgents-shadow-card" in output
        assert "test" in output

    def test_shadow_card_difficulty_indicator(self) -> None:
        """Difficulty indicator shows correct symbols."""
        card = ShadowCardWidget()

        assert card._difficulty_indicator("low") == "●"
        assert card._difficulty_indicator("medium") == "◐"
        assert card._difficulty_indicator("high") == "○"


# === DialecticCard Tests ===


class TestDialecticCardWidget:
    """Tests for DialecticCardWidget."""

    def test_dialectic_card_default_state(self) -> None:
        """Dialectic card can be created with default state."""
        card = DialecticCardWidget()
        state = card.state.value

        assert state.thesis == ""
        assert state.antithesis is None
        assert state.synthesis is None
        assert state.productive_tension is False

    def test_dialectic_card_with_synthesis(self) -> None:
        """Dialectic card with thesis/antithesis/synthesis."""
        card = DialecticCardWidget(
            DialecticCardState(
                thesis="speed",
                antithesis="quality",
                synthesis="iterative refinement",
                sublation_notes="Balance through iteration",
            )
        )

        state = card.state.value
        assert state.thesis == "speed"
        assert state.antithesis == "quality"
        assert state.synthesis == "iterative refinement"

    def test_dialectic_card_with_tension(self) -> None:
        """Dialectic card with productive tension."""
        card = DialecticCardWidget(
            DialecticCardState(
                thesis="freedom",
                antithesis="security",
                productive_tension=True,
                sublation_notes="Cannot be fully synthesized",
            )
        )

        state = card.state.value
        assert state.productive_tension is True
        assert state.synthesis is None

    def test_dialectic_card_cli_projection(self) -> None:
        """Dialectic card projects to CLI."""
        card = DialecticCardWidget(
            DialecticCardState(
                thesis="A",
                antithesis="B",
                synthesis="C",
            )
        )

        output = card.project(RenderTarget.CLI)

        assert isinstance(output, str)
        assert "Synthesis" in output
        assert "Thesis: A" in output
        assert "Antithesis: B" in output

    def test_dialectic_card_cli_tension(self) -> None:
        """CLI projection shows tension when held."""
        card = DialecticCardWidget(
            DialecticCardState(
                thesis="X",
                antithesis="Y",
                productive_tension=True,
            )
        )

        output = card.project(RenderTarget.CLI)

        assert "Tension" in output
        assert "no synthesis forced" in output

    def test_dialectic_card_json_projection(self) -> None:
        """Dialectic card projects to JSON."""
        card = DialecticCardWidget(
            DialecticCardState(
                thesis="A",
                antithesis="B",
                synthesis="C",
            )
        )

        output = card.project(RenderTarget.JSON)

        assert isinstance(output, dict)
        assert output["type"] == "dialectic_card"
        assert output["thesis"] == "A"
        assert output["antithesis"] == "B"
        assert output["synthesis"] == "C"
        assert output["productive_tension"] is False

    def test_dialectic_card_with_time_immutable(self) -> None:
        """with_time returns new card without modifying original."""
        card = DialecticCardWidget(DialecticCardState(t=0.0))
        new_card = card.with_time(100.0)

        assert card.state.value.t == 0.0
        assert new_card.state.value.t == 100.0

    def test_dialectic_card_marimo_projection(self) -> None:
        """Dialectic card projects to MARIMO (HTML)."""
        card = DialecticCardWidget(
            DialecticCardState(
                thesis="test",
                antithesis="opposition",
                synthesis="resolution",
            )
        )

        output = card.project(RenderTarget.MARIMO)

        assert isinstance(output, str)
        assert "kgents-dialectic-card" in output
        assert "test" in output


# === Integration Tests ===


class TestHgentCardsIntegration:
    """Integration tests for H-gent cards."""

    def test_shadow_card_tui_fallback(self) -> None:
        """Shadow card TUI falls back to CLI if Rich not available."""
        card = ShadowCardWidget()
        # TUI should return something (either Rich Panel or CLI string)
        output = card.project(RenderTarget.TUI)
        assert output is not None

    def test_dialectic_card_tui_fallback(self) -> None:
        """Dialectic card TUI falls back to CLI if Rich not available."""
        card = DialecticCardWidget()
        # TUI should return something
        output = card.project(RenderTarget.TUI)
        assert output is not None

    def test_cards_import_from_primitives(self) -> None:
        """Cards can be imported from primitives module."""
        from agents.i.reactive.primitives import (
            DialecticCardState,
            DialecticCardWidget,
            ShadowCardState,
            ShadowCardWidget,
            ShadowItem,
        )

        # Should be importable
        assert ShadowCardWidget is not None
        assert DialecticCardWidget is not None
        assert ShadowItem is not None
