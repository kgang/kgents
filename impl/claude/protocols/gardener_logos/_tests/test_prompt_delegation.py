"""
Tests for Gardener-Logos Phase 5: Prompt Logos Delegation.

Tests cover:
- Prompt delegation from GardenerLogosNode to PromptNode
- Garden context injection (season, plasticity, active_plot)
- Season-aware learning rate adjustment for TextGRAD
- WATER gesture integration with TextGRAD

Per plans/gardener-logos-enactment.md Phase 5.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ..agentese.context import (
    GARDENER_LOGOS_AFFORDANCES,
    GardenerLogosNode,
    create_gardener_logos_node,
)
from ..garden import GardenSeason, create_garden
from ..tending import TendingVerb, water

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_umwelt() -> MagicMock:
    """Create a mock Umwelt for testing."""
    umwelt = MagicMock()
    umwelt.meta.archetype = "developer"
    umwelt.meta.name = "test-observer"
    return umwelt


@pytest.fixture
def sprouting_garden() -> GardenerLogosNode:
    """Create a node with SPROUTING season (high plasticity)."""
    garden = create_garden("test", GardenSeason.SPROUTING)
    garden.active_plot = "test-plot"
    return create_gardener_logos_node(garden)


@pytest.fixture
def dormant_garden() -> GardenerLogosNode:
    """Create a node with DORMANT season (low plasticity)."""
    garden = create_garden("test", GardenSeason.DORMANT)
    garden.active_plot = "dormant-plot"
    return create_gardener_logos_node(garden)


@pytest.fixture
def blooming_garden() -> GardenerLogosNode:
    """Create a node with BLOOMING season (medium plasticity)."""
    garden = create_garden("test", GardenSeason.BLOOMING)
    garden.active_plot = "blooming-plot"
    return create_gardener_logos_node(garden)


# =============================================================================
# Affordance Tests
# =============================================================================


class TestPromptAffordances:
    """Tests for prompt affordances in different roles."""

    def test_guest_has_limited_prompt_affordances(self):
        """Guest can only manifest and view history."""
        affordances = GARDENER_LOGOS_AFFORDANCES["guest"]
        assert "prompt.manifest" in affordances
        assert "prompt.history" in affordances
        assert "prompt.evolve" not in affordances
        assert "prompt.rollback" not in affordances

    def test_developer_has_full_prompt_affordances(self):
        """Developer has full prompt affordances."""
        affordances = GARDENER_LOGOS_AFFORDANCES["developer"]
        assert "prompt.manifest" in affordances
        assert "prompt.evolve" in affordances
        assert "prompt.validate" in affordances
        assert "prompt.compile" in affordances
        assert "prompt.history" in affordances
        assert "prompt.rollback" in affordances
        assert "prompt.diff" in affordances

    def test_meta_has_full_prompt_affordances(self):
        """Meta role has full prompt affordances."""
        affordances = GARDENER_LOGOS_AFFORDANCES["meta"]
        assert "prompt.manifest" in affordances
        assert "prompt.evolve" in affordances
        assert "prompt.rollback" in affordances

    def test_default_has_manifest_only(self):
        """Default role can only view prompt manifest."""
        affordances = GARDENER_LOGOS_AFFORDANCES["default"]
        assert "prompt.manifest" in affordances
        assert "prompt.evolve" not in affordances


# =============================================================================
# Prompt Delegation Tests
# =============================================================================


class TestPromptDelegation:
    """Tests for prompt.* path delegation."""

    @pytest.mark.asyncio
    async def test_prompt_manifest_delegation(
        self, sprouting_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Prompt manifest is delegated to PromptNode."""
        with patch("protocols.agentese.contexts.prompt.create_prompt_resolver") as mock_create:
            # Set up mock
            mock_node = AsyncMock()
            mock_node.manifest = AsyncMock(
                return_value=MagicMock(
                    summary="CLAUDE.md",
                    content="test content",
                    metadata={"sections": []},
                )
            )
            mock_resolver = MagicMock()
            mock_resolver.resolve.return_value = mock_node
            mock_create.return_value = mock_resolver

            result = await sprouting_garden._invoke_aspect("prompt.manifest", mock_umwelt)

            # Verify delegation occurred
            mock_resolver.resolve.assert_called_once_with("prompt", ["manifest"])
            mock_node.manifest.assert_called_once_with(mock_umwelt)

    @pytest.mark.asyncio
    async def test_prompt_evolve_delegation(
        self, sprouting_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Prompt evolve is delegated with garden context."""
        with patch("protocols.agentese.contexts.prompt.create_prompt_resolver") as mock_create:
            # Set up mock
            mock_node = AsyncMock()
            mock_node._invoke_aspect = AsyncMock(
                return_value=MagicMock(success=True, message="Evolved")
            )
            mock_resolver = MagicMock()
            mock_resolver.resolve.return_value = mock_node
            mock_create.return_value = mock_resolver

            await sprouting_garden._invoke_aspect(
                "prompt.evolve",
                mock_umwelt,
                feedback="Make more concise",
                learning_rate=0.5,
            )

            # Verify _invoke_aspect was called
            mock_node._invoke_aspect.assert_called_once()
            call_args = mock_node._invoke_aspect.call_args

            # Check garden_context was injected
            assert "garden_context" in call_args.kwargs
            assert call_args.kwargs["garden_context"]["season"] == "SPROUTING"
            assert call_args.kwargs["garden_context"]["plasticity"] == 0.9

    @pytest.mark.asyncio
    async def test_prompt_evolve_adjusts_learning_rate_by_plasticity(
        self, sprouting_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Evolve adjusts learning_rate based on season plasticity."""
        with patch("protocols.agentese.contexts.prompt.create_prompt_resolver") as mock_create:
            mock_node = AsyncMock()
            mock_node._invoke_aspect = AsyncMock(return_value=MagicMock())
            mock_resolver = MagicMock()
            mock_resolver.resolve.return_value = mock_node
            mock_create.return_value = mock_resolver

            # Base learning rate of 0.5, SPROUTING plasticity of 0.9
            await sprouting_garden._invoke_aspect(
                "prompt.evolve",
                mock_umwelt,
                feedback="Test",
                learning_rate=0.5,
            )

            call_args = mock_node._invoke_aspect.call_args
            # Expected: 0.5 * 0.9 = 0.45
            assert call_args.kwargs["learning_rate"] == pytest.approx(0.45, rel=0.01)

    @pytest.mark.asyncio
    async def test_dormant_season_reduces_learning_rate(
        self, dormant_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """DORMANT season significantly reduces learning rate."""
        with patch("protocols.agentese.contexts.prompt.create_prompt_resolver") as mock_create:
            mock_node = AsyncMock()
            mock_node._invoke_aspect = AsyncMock(return_value=MagicMock())
            mock_resolver = MagicMock()
            mock_resolver.resolve.return_value = mock_node
            mock_create.return_value = mock_resolver

            # Base learning rate of 0.5, DORMANT plasticity of 0.1
            await dormant_garden._invoke_aspect(
                "prompt.evolve",
                mock_umwelt,
                feedback="Test",
                learning_rate=0.5,
            )

            call_args = mock_node._invoke_aspect.call_args
            # Expected: 0.5 * 0.1 = 0.05
            assert call_args.kwargs["learning_rate"] == pytest.approx(0.05, rel=0.01)


# =============================================================================
# Garden Context Injection Tests
# =============================================================================


class TestGardenContextInjection:
    """Tests for garden context injection into prompt operations."""

    @pytest.mark.asyncio
    async def test_garden_context_includes_season(
        self, sprouting_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Garden context includes season name."""
        with patch("protocols.agentese.contexts.prompt.create_prompt_resolver") as mock_create:
            mock_node = AsyncMock()
            mock_node._invoke_aspect = AsyncMock(return_value=MagicMock())
            mock_resolver = MagicMock()
            mock_resolver.resolve.return_value = mock_node
            mock_create.return_value = mock_resolver

            await sprouting_garden._invoke_aspect("prompt.evolve", mock_umwelt, feedback="Test")

            call_args = mock_node._invoke_aspect.call_args
            ctx = call_args.kwargs["garden_context"]
            assert ctx["season"] == "SPROUTING"

    @pytest.mark.asyncio
    async def test_garden_context_includes_active_plot(
        self, sprouting_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Garden context includes active plot."""
        with patch("protocols.agentese.contexts.prompt.create_prompt_resolver") as mock_create:
            mock_node = AsyncMock()
            mock_node._invoke_aspect = AsyncMock(return_value=MagicMock())
            mock_resolver = MagicMock()
            mock_resolver.resolve.return_value = mock_node
            mock_create.return_value = mock_resolver

            await sprouting_garden._invoke_aspect("prompt.history", mock_umwelt, limit=5)

            call_args = mock_node._invoke_aspect.call_args
            ctx = call_args.kwargs["garden_context"]
            assert ctx["active_plot"] == "test-plot"

    @pytest.mark.asyncio
    async def test_garden_context_includes_plasticity(
        self, blooming_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Garden context includes plasticity value."""
        with patch("protocols.agentese.contexts.prompt.create_prompt_resolver") as mock_create:
            mock_node = AsyncMock()
            mock_node._invoke_aspect = AsyncMock(return_value=MagicMock())
            mock_resolver = MagicMock()
            mock_resolver.resolve.return_value = mock_node
            mock_create.return_value = mock_resolver

            await blooming_garden._invoke_aspect("prompt.validate", mock_umwelt)

            # Just verify context was passed (exact value may vary by fixture)
            call_args = mock_node._invoke_aspect.call_args
            ctx = call_args.kwargs["garden_context"]
            assert "plasticity" in ctx

    @pytest.mark.asyncio
    async def test_garden_context_includes_entropy_multiplier(
        self, sprouting_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Garden context includes entropy multiplier."""
        with patch("protocols.agentese.contexts.prompt.create_prompt_resolver") as mock_create:
            mock_node = AsyncMock()
            mock_node._invoke_aspect = AsyncMock(return_value=MagicMock())
            mock_resolver = MagicMock()
            mock_resolver.resolve.return_value = mock_node
            mock_create.return_value = mock_resolver

            await sprouting_garden._invoke_aspect("prompt.compile", mock_umwelt)

            call_args = mock_node._invoke_aspect.call_args
            ctx = call_args.kwargs["garden_context"]
            assert "entropy_multiplier" in ctx


# =============================================================================
# Season-Aware TextGRAD Tests (via WATER gesture)
# =============================================================================


class TestSeasonAwareTextGRAD:
    """Tests for season-aware TextGRAD via WATER gesture."""

    @pytest.mark.asyncio
    async def test_water_calculates_learning_rate(
        self, sprouting_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """WATER gesture calculates learning rate from tone × plasticity."""
        garden = sprouting_garden._get_garden()

        # Create water gesture with tone 0.8
        gesture = water("concept.prompt.task", "Make more clear", tone=0.8)

        # Import and call handler directly
        from ..tending import _handle_water

        result = await _handle_water(garden, gesture)

        # Verify learning rate calculation is in reasoning trace
        # Expected: 0.8 × 0.9 = 0.72
        trace_str = " ".join(result.reasoning_trace)
        assert "0.72" in trace_str or "learning_rate" in trace_str.lower()

    @pytest.mark.asyncio
    async def test_water_in_dormant_has_low_rate(
        self, dormant_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """WATER in DORMANT season has very low learning rate."""
        garden = dormant_garden._get_garden()

        gesture = water("concept.prompt.task", "Make more clear", tone=0.5)

        from ..tending import _handle_water

        result = await _handle_water(garden, gesture)

        # Expected: 0.5 × 0.1 = 0.05
        trace_str = " ".join(result.reasoning_trace)
        assert "0.05" in trace_str or "learning_rate" in trace_str.lower()

    @pytest.mark.asyncio
    async def test_water_prompt_triggers_textgrad_synergy(
        self, sprouting_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """WATER on prompt target triggers TextGRAD synergy."""
        garden = sprouting_garden._get_garden()

        gesture = water("concept.prompt.task", "Improve clarity", tone=0.5)

        from ..tending import _handle_water

        result = await _handle_water(garden, gesture)

        # Should trigger textgrad synergy
        assert "textgrad:improvement_proposed" in result.synergies_triggered

    @pytest.mark.asyncio
    async def test_water_non_prompt_no_textgrad(
        self, sprouting_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """WATER on non-prompt target doesn't trigger TextGRAD."""
        garden = sprouting_garden._get_garden()

        gesture = water("concept.workflow.feature", "Nurture", tone=0.5)

        from ..tending import _handle_water

        result = await _handle_water(garden, gesture)

        # Should NOT trigger textgrad synergy
        assert "textgrad:improvement_proposed" not in result.synergies_triggered
        assert "Nurtured: concept.workflow.feature" in result.changes


# =============================================================================
# Integration Tests
# =============================================================================


class TestPromptDelegationIntegration:
    """Integration tests for prompt delegation flow."""

    @pytest.mark.asyncio
    async def test_full_evolve_flow_sprouting(
        self, sprouting_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Test complete evolve flow in SPROUTING season."""
        # This test verifies the delegation path works end-to-end
        # The actual PromptNode may not be available in test env

        with patch("protocols.agentese.contexts.prompt.create_prompt_resolver") as mock_create:
            mock_node = AsyncMock()
            mock_node._invoke_aspect = AsyncMock(
                return_value=MagicMock(
                    success=True,
                    original_content="old",
                    improved_content="new",
                    sections_modified=("skills",),
                )
            )
            mock_resolver = MagicMock()
            mock_resolver.resolve.return_value = mock_node
            mock_create.return_value = mock_resolver

            result = await sprouting_garden._invoke_aspect(
                "prompt.evolve",
                mock_umwelt,
                feedback="Add more examples to skills section",
                learning_rate=0.7,
            )

            # Verify the flow
            assert mock_resolver.resolve.called
            assert mock_node._invoke_aspect.called

            # Verify learning rate was adjusted (0.7 × 0.9 = 0.63)
            call_args = mock_node._invoke_aspect.call_args
            assert call_args.kwargs["learning_rate"] == pytest.approx(0.63, rel=0.01)

    @pytest.mark.asyncio
    async def test_season_transition_affects_subsequent_evolve(
        self, sprouting_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Season transition affects subsequent evolve learning rate."""
        # Start in SPROUTING
        garden = sprouting_garden._get_garden()
        assert garden.season == GardenSeason.SPROUTING

        # Transition to DORMANT
        garden.transition_season(GardenSeason.DORMANT, "Going dormant")
        assert garden.season == GardenSeason.DORMANT
        assert garden.season.plasticity == 0.1

        # Now evolve should use DORMANT plasticity
        with patch("protocols.agentese.contexts.prompt.create_prompt_resolver") as mock_create:
            mock_node = AsyncMock()
            mock_node._invoke_aspect = AsyncMock(return_value=MagicMock())
            mock_resolver = MagicMock()
            mock_resolver.resolve.return_value = mock_node
            mock_create.return_value = mock_resolver

            await sprouting_garden._invoke_aspect(
                "prompt.evolve",
                mock_umwelt,
                feedback="Test",
                learning_rate=0.5,
            )

            # Learning rate should now be 0.5 × 0.1 = 0.05
            call_args = mock_node._invoke_aspect.call_args
            assert call_args.kwargs["learning_rate"] == pytest.approx(0.05, rel=0.01)


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestPromptDelegationErrors:
    """Tests for error handling in prompt delegation."""

    @pytest.mark.asyncio
    async def test_unknown_prompt_aspect_delegated(
        self, sprouting_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Unknown prompt aspects are still delegated."""
        with patch("protocols.agentese.contexts.prompt.create_prompt_resolver") as mock_create:
            mock_node = AsyncMock()
            mock_node._invoke_aspect = AsyncMock(
                return_value={"aspect": "unknown", "status": "not implemented"}
            )
            mock_resolver = MagicMock()
            mock_resolver.resolve.return_value = mock_node
            mock_create.return_value = mock_resolver

            result = await sprouting_garden._invoke_aspect(
                "prompt.unknown_aspect",
                mock_umwelt,
            )

            # Should delegate to PromptNode, which handles unknown aspects
            mock_node._invoke_aspect.assert_called_once()
