"""
Tests for Gardener-Logos AGENTESE Integration.

Tests cover:
- GardenerLogosNode manifest (garden overview)
- Tending gesture application (all 6 verbs)
- Season operations (manifest, transition)
- Plot operations (list, create, focus, manifest)
- Role-based affordances
- Error handling for invalid inputs

Per plans/gardener-logos-enactment.md Phase 1.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import MagicMock

import pytest

from ..agentese.context import (
    GARDENER_LOGOS_AFFORDANCES,
    GardenerLogosNode,
    GardenerLogosResolver,
    create_gardener_logos_node,
    create_gardener_logos_resolver,
)
from ..garden import GardenSeason, create_garden
from ..plots import create_plot
from ..tending import TendingVerb

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
def gardener_node() -> GardenerLogosNode:
    """Create a GardenerLogosNode instance."""
    return create_gardener_logos_node()


@pytest.fixture
def gardener_with_garden() -> GardenerLogosNode:
    """Create a GardenerLogosNode with pre-configured garden."""
    garden = create_garden("test-garden", GardenSeason.SPROUTING)

    # Create plots with progress set after creation
    test_plot = create_plot(
        name="test-plot",
        path="concept.test",
        description="A test plot",
    )
    test_plot.progress = 0.5

    atelier_plot = create_plot(
        name="atelier",
        path="world.atelier",
        crown_jewel="Atelier",
    )

    garden.plots = {
        "test-plot": test_plot,
        "atelier": atelier_plot,
    }
    garden.active_plot = "test-plot"
    node = create_gardener_logos_node(garden)
    return node


# =============================================================================
# Manifest Tests
# =============================================================================


class TestManifest:
    """Tests for concept.gardener.manifest."""

    @pytest.mark.asyncio
    async def test_manifest_returns_basic_rendering(
        self, gardener_node: GardenerLogosNode, mock_umwelt: Any
    ):
        """Manifest returns a BasicRendering."""
        result = await gardener_node.manifest(mock_umwelt)
        assert result is not None
        assert hasattr(result, "summary")
        assert hasattr(result, "content")
        assert hasattr(result, "metadata")

    @pytest.mark.asyncio
    async def test_manifest_contains_garden_info(
        self, gardener_node: GardenerLogosNode, mock_umwelt: Any
    ):
        """Manifest content contains garden information."""
        result = await gardener_node.manifest(mock_umwelt)
        assert "GARDEN" in result.content
        assert "Season:" in result.content or "DORMANT" in result.content

    @pytest.mark.asyncio
    async def test_manifest_metadata_has_garden_id(
        self, gardener_node: GardenerLogosNode, mock_umwelt: Any
    ):
        """Manifest metadata contains garden_id."""
        result = await gardener_node.manifest(mock_umwelt)
        assert "garden_id" in result.metadata

    @pytest.mark.asyncio
    async def test_manifest_shows_plots(
        self, gardener_with_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Manifest shows plots when present."""
        result = await gardener_with_garden.manifest(mock_umwelt)
        assert "PLOTS" in result.content or "test-plot" in result.content.lower()

    @pytest.mark.asyncio
    async def test_manifest_via_invoke_aspect(
        self, gardener_node: GardenerLogosNode, mock_umwelt: Any
    ):
        """Manifest can be invoked via _invoke_aspect."""
        result = await gardener_node._invoke_aspect("manifest", mock_umwelt)
        assert "GARDEN" in result.content


# =============================================================================
# Tend Tests (All 6 Verbs)
# =============================================================================


class TestTend:
    """Tests for concept.gardener.tend."""

    @pytest.mark.asyncio
    async def test_tend_observe(self, gardener_node: GardenerLogosNode, mock_umwelt: Any):
        """OBSERVE gesture works."""
        result = await gardener_node._invoke_aspect(
            "tend",
            mock_umwelt,
            verb="observe",
            target="concept.gardener",
            reasoning="Testing observe",
        )
        assert result.metadata["verb"] == "OBSERVE"
        assert result.metadata["accepted"] is True

    @pytest.mark.asyncio
    async def test_tend_prune(self, gardener_node: GardenerLogosNode, mock_umwelt: Any):
        """PRUNE gesture works."""
        result = await gardener_node._invoke_aspect(
            "tend",
            mock_umwelt,
            verb="prune",
            target="concept.old.feature",
            reasoning="Removing old feature",
            tone=0.7,
        )
        assert result.metadata["verb"] == "PRUNE"
        assert result.metadata["accepted"] is True
        assert result.metadata["state_changed"] is True

    @pytest.mark.asyncio
    async def test_tend_graft(self, gardener_node: GardenerLogosNode, mock_umwelt: Any):
        """GRAFT gesture works."""
        result = await gardener_node._invoke_aspect(
            "tend",
            mock_umwelt,
            verb="graft",
            target="concept.new.feature",
            reasoning="Adding new feature",
            tone=0.8,
        )
        assert result.metadata["verb"] == "GRAFT"
        assert result.metadata["accepted"] is True

    @pytest.mark.asyncio
    async def test_tend_water(self, gardener_node: GardenerLogosNode, mock_umwelt: Any):
        """WATER gesture works."""
        result = await gardener_node._invoke_aspect(
            "tend",
            mock_umwelt,
            verb="water",
            target="concept.prompt.task",
            reasoning="Improve with feedback",
            tone=0.5,
        )
        assert result.metadata["verb"] == "WATER"
        assert result.metadata["accepted"] is True

    @pytest.mark.asyncio
    async def test_tend_rotate(self, gardener_node: GardenerLogosNode, mock_umwelt: Any):
        """ROTATE gesture works."""
        result = await gardener_node._invoke_aspect(
            "tend",
            mock_umwelt,
            verb="rotate",
            target="concept.architecture",
            reasoning="Change perspective",
        )
        assert result.metadata["verb"] == "ROTATE"
        assert result.metadata["accepted"] is True

    @pytest.mark.asyncio
    async def test_tend_wait(self, gardener_node: GardenerLogosNode, mock_umwelt: Any):
        """WAIT gesture works."""
        result = await gardener_node._invoke_aspect(
            "tend",
            mock_umwelt,
            verb="wait",
            reasoning="Allowing time to pass",
        )
        assert result.metadata["verb"] == "WAIT"
        assert result.metadata["accepted"] is True
        assert result.metadata["state_changed"] is False

    @pytest.mark.asyncio
    async def test_tend_invalid_verb(self, gardener_node: GardenerLogosNode, mock_umwelt: Any):
        """Invalid verb returns error."""
        result = await gardener_node._invoke_aspect(
            "tend",
            mock_umwelt,
            verb="invalid",
            target="concept.test",
        )
        assert "error" in result.metadata
        assert result.metadata["error"] == "invalid_verb"

    @pytest.mark.asyncio
    async def test_tend_updates_garden(self, gardener_node: GardenerLogosNode, mock_umwelt: Any):
        """Tending updates the garden state."""
        # Get initial entropy
        garden = gardener_node._get_garden()
        initial_entropy = garden.metrics.entropy_spent

        # Apply a gesture that costs entropy
        await gardener_node._invoke_aspect(
            "tend",
            mock_umwelt,
            verb="prune",
            target="concept.test",
            reasoning="Test pruning",
        )

        # Verify entropy increased
        assert garden.metrics.entropy_spent > initial_entropy


# =============================================================================
# Season Tests
# =============================================================================


class TestSeason:
    """Tests for concept.gardener.season.* paths."""

    @pytest.mark.asyncio
    async def test_season_manifest(self, gardener_node: GardenerLogosNode, mock_umwelt: Any):
        """Season manifest shows current season."""
        result = await gardener_node._invoke_aspect("season.manifest", mock_umwelt)
        assert "SEASON" in result.content
        assert "plasticity" in result.metadata

    @pytest.mark.asyncio
    async def test_season_transition_sprouting(
        self, gardener_node: GardenerLogosNode, mock_umwelt: Any
    ):
        """Season transition to SPROUTING works."""
        result = await gardener_node._invoke_aspect(
            "season.transition",
            mock_umwelt,
            to="SPROUTING",
            reason="Starting new growth",
        )
        assert result.metadata["new_season"] == "SPROUTING"
        garden = gardener_node._get_garden()
        assert garden.season == GardenSeason.SPROUTING

    @pytest.mark.asyncio
    async def test_season_transition_all_seasons(
        self, gardener_node: GardenerLogosNode, mock_umwelt: Any
    ):
        """All season transitions work."""
        for season in GardenSeason:
            result = await gardener_node._invoke_aspect(
                "season.transition",
                mock_umwelt,
                to=season.name,
                reason=f"Testing {season.name}",
            )
            assert result.metadata["new_season"] == season.name

    @pytest.mark.asyncio
    async def test_season_transition_invalid(
        self, gardener_node: GardenerLogosNode, mock_umwelt: Any
    ):
        """Invalid season returns error."""
        result = await gardener_node._invoke_aspect(
            "season.transition",
            mock_umwelt,
            to="INVALID_SEASON",
        )
        assert "error" in result.metadata
        assert result.metadata["error"] == "invalid_season"

    @pytest.mark.asyncio
    async def test_season_transition_no_season(
        self, gardener_node: GardenerLogosNode, mock_umwelt: Any
    ):
        """Missing season returns error."""
        result = await gardener_node._invoke_aspect(
            "season.transition",
            mock_umwelt,
        )
        assert "error" in result.metadata
        assert result.metadata["error"] == "no_season"


# =============================================================================
# Plot Tests
# =============================================================================


class TestPlotList:
    """Tests for concept.gardener.plot.list."""

    @pytest.mark.asyncio
    async def test_plot_list_with_plots(
        self, gardener_with_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Plot list shows plots."""
        result = await gardener_with_garden._invoke_aspect("plot.list", mock_umwelt)
        assert "plots" in result.metadata
        assert len(result.metadata["plots"]) == 2

    @pytest.mark.asyncio
    async def test_plot_list_empty(self, mock_umwelt: Any):
        """Plot list with no plots shows message."""
        garden = create_garden("empty")
        garden.plots = {}
        node = create_gardener_logos_node(garden)
        result = await node._invoke_aspect("plot.list", mock_umwelt)
        assert "No plots" in result.content or result.metadata["plots"] == []

    @pytest.mark.asyncio
    async def test_plot_list_shows_active(
        self, gardener_with_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Plot list marks active plot."""
        result = await gardener_with_garden._invoke_aspect("plot.list", mock_umwelt)
        assert result.metadata["active_plot"] == "test-plot"


class TestPlotCreate:
    """Tests for concept.gardener.plot.create."""

    @pytest.mark.asyncio
    async def test_plot_create(self, gardener_node: GardenerLogosNode, mock_umwelt: Any):
        """Plot creation works."""
        result = await gardener_node._invoke_aspect(
            "plot.create",
            mock_umwelt,
            name="new-plot",
            path="concept.new",
            description="A new plot",
        )
        assert result.metadata["name"] == "new-plot"
        assert result.metadata["path"] == "concept.new"

    @pytest.mark.asyncio
    async def test_plot_create_with_plan(self, gardener_node: GardenerLogosNode, mock_umwelt: Any):
        """Plot creation with plan link works."""
        result = await gardener_node._invoke_aspect(
            "plot.create",
            mock_umwelt,
            name="planned-plot",
            path="world.planned",
            plan="plans/test.md",
        )
        assert result.metadata["plan_path"] == "plans/test.md"

    @pytest.mark.asyncio
    async def test_plot_create_no_name(self, gardener_node: GardenerLogosNode, mock_umwelt: Any):
        """Plot creation without name returns error."""
        result = await gardener_node._invoke_aspect(
            "plot.create",
            mock_umwelt,
            path="concept.test",
        )
        assert "error" in result.metadata
        assert result.metadata["error"] == "no_name"

    @pytest.mark.asyncio
    async def test_plot_create_duplicate(
        self, gardener_with_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Duplicate plot name returns error."""
        result = await gardener_with_garden._invoke_aspect(
            "plot.create",
            mock_umwelt,
            name="test-plot",  # Already exists
            path="concept.duplicate",
        )
        assert "error" in result.metadata
        assert result.metadata["error"] == "plot_exists"


class TestPlotFocus:
    """Tests for concept.gardener.plot.focus."""

    @pytest.mark.asyncio
    async def test_plot_focus_change(
        self, gardener_with_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Focus can be changed."""
        result = await gardener_with_garden._invoke_aspect(
            "plot.focus",
            mock_umwelt,
            name="atelier",
        )
        assert result.metadata["active_plot"] == "atelier"
        assert result.metadata["old_focus"] == "test-plot"

    @pytest.mark.asyncio
    async def test_plot_focus_show_current(
        self, gardener_with_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Focus without name shows current focus."""
        result = await gardener_with_garden._invoke_aspect("plot.focus", mock_umwelt)
        assert result.metadata["active_plot"] == "test-plot"

    @pytest.mark.asyncio
    async def test_plot_focus_not_found(
        self, gardener_with_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Focus on non-existent plot returns error."""
        result = await gardener_with_garden._invoke_aspect(
            "plot.focus",
            mock_umwelt,
            name="nonexistent",
        )
        assert "error" in result.metadata
        assert result.metadata["error"] == "plot_not_found"


class TestPlotManifest:
    """Tests for concept.gardener.plot.manifest."""

    @pytest.mark.asyncio
    async def test_plot_manifest_by_name(
        self, gardener_with_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Plot manifest by name works."""
        result = await gardener_with_garden._invoke_aspect(
            "plot.manifest",
            mock_umwelt,
            name="test-plot",
        )
        assert result.metadata["name"] == "test-plot"

    @pytest.mark.asyncio
    async def test_plot_manifest_active(
        self, gardener_with_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Plot manifest without name uses active plot."""
        result = await gardener_with_garden._invoke_aspect(
            "plot.manifest",
            mock_umwelt,
        )
        assert result.metadata["name"] == "test-plot"

    @pytest.mark.asyncio
    async def test_plot_manifest_not_found(
        self, gardener_with_garden: GardenerLogosNode, mock_umwelt: Any
    ):
        """Plot manifest for non-existent returns error."""
        result = await gardener_with_garden._invoke_aspect(
            "plot.manifest",
            mock_umwelt,
            name="nonexistent",
        )
        assert "error" in result.metadata


# =============================================================================
# Role Affordances Tests
# =============================================================================


class TestRoleAffordances:
    """Tests for role-based affordances."""

    def test_guest_has_limited_affordances(self):
        """Guest role has limited affordances."""
        affordances = GARDENER_LOGOS_AFFORDANCES["guest"]
        assert "manifest" in affordances
        assert "tend" not in affordances
        assert "plot.create" not in affordances

    def test_developer_can_tend(self):
        """Developer role can tend."""
        affordances = GARDENER_LOGOS_AFFORDANCES["developer"]
        assert "tend" in affordances
        assert "season.transition" in affordances
        assert "plot.create" in affordances

    def test_meta_has_full_access(self):
        """Meta role has full access."""
        affordances = GARDENER_LOGOS_AFFORDANCES["meta"]
        assert "plot.delete" in affordances
        assert len(affordances) > len(GARDENER_LOGOS_AFFORDANCES["developer"])


# =============================================================================
# Resolver Tests
# =============================================================================


class TestResolver:
    """Tests for GardenerLogosResolver."""

    def test_resolver_creates_node(self):
        """Resolver creates a node."""
        resolver = create_gardener_logos_resolver()
        node = resolver.resolve("gardener", ["manifest"])
        assert isinstance(node, GardenerLogosNode)

    def test_resolver_returns_singleton(self):
        """Resolver returns same node instance."""
        resolver = create_gardener_logos_resolver()
        node1 = resolver.resolve("gardener", ["manifest"])
        node2 = resolver.resolve("gardener", ["tend"])
        assert node1 is node2

    def test_resolver_accepts_garden(self):
        """Resolver accepts pre-configured garden."""
        garden = create_garden("custom")
        resolver = create_gardener_logos_resolver(garden)
        node = resolver.resolve("gardener", [])
        assert node._garden is garden


# =============================================================================
# Unknown Aspect Tests
# =============================================================================


class TestUnknownAspect:
    """Tests for unknown aspect handling."""

    @pytest.mark.asyncio
    async def test_unknown_aspect_returns_error(
        self, gardener_node: GardenerLogosNode, mock_umwelt: Any
    ):
        """Unknown aspect returns error rendering."""
        result = await gardener_node._invoke_aspect(
            "unknown.aspect",
            mock_umwelt,
        )
        assert "error" in result.metadata or "unknown_aspect" in result.metadata.get("error", "")


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration-style tests for complete workflows."""

    @pytest.mark.asyncio
    async def test_full_garden_workflow(self, gardener_node: GardenerLogosNode, mock_umwelt: Any):
        """Test complete garden workflow: transition → create plot → tend."""
        # 1. Transition to SPROUTING
        result = await gardener_node._invoke_aspect(
            "season.transition",
            mock_umwelt,
            to="SPROUTING",
            reason="Starting work",
        )
        assert result.metadata["new_season"] == "SPROUTING"

        # 2. Create a new plot
        result = await gardener_node._invoke_aspect(
            "plot.create",
            mock_umwelt,
            name="workflow-test",
            path="concept.workflow",
        )
        assert result.metadata["name"] == "workflow-test"

        # 3. Focus on it
        result = await gardener_node._invoke_aspect(
            "plot.focus",
            mock_umwelt,
            name="workflow-test",
        )
        assert result.metadata["active_plot"] == "workflow-test"

        # 4. Tend it (graft)
        result = await gardener_node._invoke_aspect(
            "tend",
            mock_umwelt,
            verb="graft",
            target="concept.workflow.feature",
            reasoning="Adding new feature",
        )
        assert result.metadata["accepted"] is True

        # 5. Observe result
        result = await gardener_node._invoke_aspect(
            "tend",
            mock_umwelt,
            verb="observe",
            target="concept.workflow",
            reasoning="Checking progress",
        )
        assert result.metadata["accepted"] is True

        # 6. Verify garden state via manifest
        result = await gardener_node.manifest(mock_umwelt)
        garden = gardener_node._get_garden()
        assert garden.season == GardenSeason.SPROUTING
        assert "workflow-test" in garden.plots
        assert len(garden.recent_gestures) >= 2

    @pytest.mark.asyncio
    async def test_season_affects_tending(self, gardener_node: GardenerLogosNode, mock_umwelt: Any):
        """Test that season affects tending results."""
        # In SPROUTING (high plasticity), grafting should work well
        await gardener_node._invoke_aspect(
            "season.transition",
            mock_umwelt,
            to="SPROUTING",
        )

        garden = gardener_node._get_garden()
        assert garden.season.plasticity == 0.9

        # In DORMANT (low plasticity), garden is more resistant
        await gardener_node._invoke_aspect(
            "season.transition",
            mock_umwelt,
            to="DORMANT",
        )

        assert garden.season.plasticity == 0.1
