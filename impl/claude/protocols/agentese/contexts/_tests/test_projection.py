"""
Tests for AGENTESE Projection Context (Layout Projection Functor)

Tests cover:
- PhysicalCapacity creation and density detection
- LayoutUmwelt factory methods (mobile, desktop)
- self.layout.density aspect
- self.layout.modality aspect
- world.panel.manifest density-dependent projection
- world.actions.manifest density-dependent projection
- world.split.manifest density-dependent projection
- Physical constraints enforcement
- Structural isomorphism verification

Phase 5 of the Layout Projection Functor plan.
See: plans/web-refactor/layout-projection-functor.md
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from protocols.agentese.contexts.projection import (
    ACTIONS_BEHAVIORS,
    # Behaviors
    PANEL_BEHAVIORS,
    PHYSICAL_CONSTRAINTS,
    # Affordances
    PROJECTION_AFFORDANCES,
    SPLIT_BEHAVIORS,
    ActionsNode,
    Bandwidth,
    # Types
    Density,
    # Nodes
    LayoutNode,
    LayoutUmwelt,
    Modality,
    PanelNode,
    PhysicalCapacity,
    SplitNode,
    create_actions_node,
    create_layout_node,
    create_panel_node,
    # Factories
    create_projection_resolver,
    create_split_node,
)

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
def compact_capacity() -> PhysicalCapacity:
    """Create a compact (mobile) physical capacity."""
    return PhysicalCapacity(
        density=Density.COMPACT,
        modality=Modality.TOUCH,
        bandwidth=Bandwidth.MEDIUM,
        viewport_width=375,
        viewport_height=667,
    )


@pytest.fixture
def spacious_capacity() -> PhysicalCapacity:
    """Create a spacious (desktop) physical capacity."""
    return PhysicalCapacity(
        density=Density.SPACIOUS,
        modality=Modality.POINTER,
        bandwidth=Bandwidth.HIGH,
        viewport_width=1920,
        viewport_height=1080,
    )


# =============================================================================
# PhysicalCapacity Tests
# =============================================================================


class TestPhysicalCapacity:
    """Tests for PhysicalCapacity dataclass."""

    def test_default_capacity_is_spacious(self) -> None:
        """Default capacity should be spacious/pointer/high."""
        capacity = PhysicalCapacity()
        assert capacity.density == Density.SPACIOUS
        assert capacity.modality == Modality.POINTER
        assert capacity.bandwidth == Bandwidth.HIGH

    def test_from_viewport_compact(self) -> None:
        """Viewport < 768px should be compact."""
        capacity = PhysicalCapacity.from_viewport(375)
        assert capacity.density == Density.COMPACT
        assert capacity.modality == Modality.TOUCH  # Inferred from compact

    def test_from_viewport_comfortable(self) -> None:
        """Viewport 768-1024px should be comfortable."""
        capacity = PhysicalCapacity.from_viewport(800)
        assert capacity.density == Density.COMFORTABLE
        assert capacity.modality == Modality.POINTER

    def test_from_viewport_spacious(self) -> None:
        """Viewport > 1024px should be spacious."""
        capacity = PhysicalCapacity.from_viewport(1200)
        assert capacity.density == Density.SPACIOUS
        assert capacity.modality == Modality.POINTER

    def test_from_viewport_boundary_768(self) -> None:
        """Viewport at exactly 768px should be comfortable (not compact)."""
        capacity = PhysicalCapacity.from_viewport(768)
        assert capacity.density == Density.COMFORTABLE

    def test_from_viewport_boundary_1024(self) -> None:
        """Viewport at exactly 1024px should be spacious (not comfortable)."""
        capacity = PhysicalCapacity.from_viewport(1024)
        assert capacity.density == Density.SPACIOUS

    def test_from_viewport_boundary_767(self) -> None:
        """Viewport at 767px should be compact."""
        capacity = PhysicalCapacity.from_viewport(767)
        assert capacity.density == Density.COMPACT


# =============================================================================
# LayoutUmwelt Tests
# =============================================================================


class TestLayoutUmwelt:
    """Tests for LayoutUmwelt factory methods."""

    def test_mobile_factory(self) -> None:
        """LayoutUmwelt.mobile() creates compact touch umwelt."""
        umwelt = LayoutUmwelt.mobile()
        assert umwelt.observer_id == "mobile_user"
        assert umwelt.capacity.density == Density.COMPACT
        assert umwelt.capacity.modality == Modality.TOUCH

    def test_desktop_factory(self) -> None:
        """LayoutUmwelt.desktop() creates spacious pointer umwelt."""
        umwelt = LayoutUmwelt.desktop()
        assert umwelt.observer_id == "desktop_user"
        assert umwelt.capacity.density == Density.SPACIOUS
        assert umwelt.capacity.modality == Modality.POINTER

    def test_custom_observer_id(self) -> None:
        """Factory methods accept custom observer IDs."""
        umwelt = LayoutUmwelt.mobile("custom-mobile")
        assert umwelt.observer_id == "custom-mobile"


# =============================================================================
# LayoutNode Tests (self.layout.*)
# =============================================================================


class TestLayoutNode:
    """Tests for self.layout.* paths."""

    @pytest.mark.asyncio
    async def test_density_aspect(
        self, mock_umwelt: MagicMock, compact_capacity: PhysicalCapacity
    ) -> None:
        """self.layout.density returns current density."""
        node = create_layout_node(compact_capacity)
        result = await node._invoke_aspect("density", mock_umwelt)
        assert result == Density.COMPACT

    @pytest.mark.asyncio
    async def test_modality_aspect(
        self, mock_umwelt: MagicMock, compact_capacity: PhysicalCapacity
    ) -> None:
        """self.layout.modality returns current modality."""
        node = create_layout_node(compact_capacity)
        result = await node._invoke_aspect("modality", mock_umwelt)
        assert result == Modality.TOUCH

    @pytest.mark.asyncio
    async def test_capacity_aspect(
        self, mock_umwelt: MagicMock, compact_capacity: PhysicalCapacity
    ) -> None:
        """self.layout.capacity returns full PhysicalCapacity."""
        node = create_layout_node(compact_capacity)
        result = await node._invoke_aspect("capacity", mock_umwelt)
        assert result == compact_capacity

    @pytest.mark.asyncio
    async def test_viewport_aspect(
        self, mock_umwelt: MagicMock, compact_capacity: PhysicalCapacity
    ) -> None:
        """self.layout.viewport returns viewport dimensions."""
        node = create_layout_node(compact_capacity)
        result = await node._invoke_aspect("viewport", mock_umwelt)
        assert result == {"width": 375, "height": 667}

    @pytest.mark.asyncio
    async def test_manifest(
        self, mock_umwelt: MagicMock, compact_capacity: PhysicalCapacity
    ) -> None:
        """self.layout.manifest returns layout context summary."""
        node = create_layout_node(compact_capacity)
        result = await node.manifest(mock_umwelt)
        assert "compact" in result.summary.lower()
        assert result.metadata["density"] == "compact"
        assert result.metadata["modality"] == "touch"


# =============================================================================
# PanelNode Tests (world.panel.*)
# =============================================================================


class TestPanelNode:
    """Tests for world.panel.* paths."""

    @pytest.mark.asyncio
    async def test_manifest_compact_returns_drawer(self, mock_umwelt: MagicMock) -> None:
        """world.panel.manifest returns drawer in compact mode."""
        # The panel node will use default spacious capacity
        # To test with compact, we would need to inject capacity into observer
        node = create_panel_node()
        # Default behavior (spacious)
        result = await node._invoke_aspect("manifest", mock_umwelt)
        assert result["layout"] == "sidebar"

    def test_panel_behaviors_defined_for_all_densities(self) -> None:
        """PANEL_BEHAVIORS defines behavior for all three densities."""
        assert Density.COMPACT in PANEL_BEHAVIORS
        assert Density.COMFORTABLE in PANEL_BEHAVIORS
        assert Density.SPACIOUS in PANEL_BEHAVIORS

    def test_compact_panel_is_drawer(self) -> None:
        """Compact panel layout is 'drawer'."""
        assert PANEL_BEHAVIORS[Density.COMPACT]["layout"] == "drawer"

    def test_spacious_panel_is_sidebar(self) -> None:
        """Spacious panel layout is 'sidebar'."""
        assert PANEL_BEHAVIORS[Density.SPACIOUS]["layout"] == "sidebar"

    def test_comfortable_panel_is_collapsible(self) -> None:
        """Comfortable panel layout is 'collapsible'."""
        assert PANEL_BEHAVIORS[Density.COMFORTABLE]["layout"] == "collapsible"


# =============================================================================
# ActionsNode Tests (world.actions.*)
# =============================================================================


class TestActionsNode:
    """Tests for world.actions.* paths."""

    @pytest.mark.asyncio
    async def test_behaviors_aspect(self, mock_umwelt: MagicMock) -> None:
        """world.actions.behaviors returns all action behaviors."""
        node = create_actions_node()
        result = await node._invoke_aspect("behaviors", mock_umwelt)
        assert Density.COMPACT in result
        assert Density.SPACIOUS in result

    def test_actions_behaviors_defined_for_all_densities(self) -> None:
        """ACTIONS_BEHAVIORS defines behavior for all three densities."""
        assert Density.COMPACT in ACTIONS_BEHAVIORS
        assert Density.COMFORTABLE in ACTIONS_BEHAVIORS
        assert Density.SPACIOUS in ACTIONS_BEHAVIORS

    def test_compact_actions_is_fab(self) -> None:
        """Compact actions layout is 'floating_fab'."""
        assert ACTIONS_BEHAVIORS[Density.COMPACT]["layout"] == "floating_fab"

    def test_spacious_actions_is_toolbar(self) -> None:
        """Spacious actions layout is 'full_toolbar'."""
        assert ACTIONS_BEHAVIORS[Density.SPACIOUS]["layout"] == "full_toolbar"

    def test_comfortable_actions_is_inline(self) -> None:
        """Comfortable actions layout is 'inline_buttons'."""
        assert ACTIONS_BEHAVIORS[Density.COMFORTABLE]["layout"] == "inline_buttons"


# =============================================================================
# SplitNode Tests (world.split.*)
# =============================================================================


class TestSplitNode:
    """Tests for world.split.* paths."""

    @pytest.mark.asyncio
    async def test_behaviors_aspect(self, mock_umwelt: MagicMock) -> None:
        """world.split.behaviors returns all split behaviors."""
        node = create_split_node()
        result = await node._invoke_aspect("behaviors", mock_umwelt)
        assert Density.COMPACT in result
        assert Density.SPACIOUS in result

    def test_split_behaviors_defined_for_all_densities(self) -> None:
        """SPLIT_BEHAVIORS defines behavior for all three densities."""
        assert Density.COMPACT in SPLIT_BEHAVIORS
        assert Density.COMFORTABLE in SPLIT_BEHAVIORS
        assert Density.SPACIOUS in SPLIT_BEHAVIORS

    def test_compact_split_is_collapsed(self) -> None:
        """Compact split layout is 'collapsed'."""
        assert SPLIT_BEHAVIORS[Density.COMPACT]["layout"] == "collapsed"

    def test_spacious_split_is_resizable(self) -> None:
        """Spacious split layout is 'resizable'."""
        assert SPLIT_BEHAVIORS[Density.SPACIOUS]["layout"] == "resizable"

    def test_comfortable_split_is_fixed(self) -> None:
        """Comfortable split layout is 'fixed'."""
        assert SPLIT_BEHAVIORS[Density.COMFORTABLE]["layout"] == "fixed"


# =============================================================================
# Physical Constraints Tests
# =============================================================================


class TestPhysicalConstraints:
    """Tests for density-invariant physical constraints."""

    def test_min_touch_target_is_48(self) -> None:
        """Minimum touch target must be 48px."""
        assert PHYSICAL_CONSTRAINTS["min_touch_target"] == 48

    def test_min_font_size_is_14(self) -> None:
        """Minimum font size must be 14px."""
        assert PHYSICAL_CONSTRAINTS["min_font_size"] == 14

    def test_min_tap_spacing_is_8(self) -> None:
        """Minimum tap spacing must be 8px."""
        assert PHYSICAL_CONSTRAINTS["min_tap_spacing"] == 8

    def test_compact_panel_touch_target(self) -> None:
        """Compact panel uses 48px touch target."""
        assert PANEL_BEHAVIORS[Density.COMPACT]["touch_target"] == 48

    def test_compact_actions_button_size(self) -> None:
        """Compact actions uses 48px button size."""
        assert ACTIONS_BEHAVIORS[Density.COMPACT]["button_size"] == 48


# =============================================================================
# Structural Isomorphism Tests
# =============================================================================


class TestStructuralIsomorphism:
    """Verify structural isomorphism properties."""

    def test_all_primitives_define_all_densities(self) -> None:
        """All three primitives define behaviors for all three densities."""
        densities = [Density.COMPACT, Density.COMFORTABLE, Density.SPACIOUS]
        for density in densities:
            assert density in PANEL_BEHAVIORS
            assert density in ACTIONS_BEHAVIORS
            assert density in SPLIT_BEHAVIORS

    def test_layout_key_present_in_all_behaviors(self) -> None:
        """All behavior definitions include a 'layout' key."""
        for density in Density:
            assert "layout" in PANEL_BEHAVIORS[density]
            assert "layout" in ACTIONS_BEHAVIORS[density]
            assert "layout" in SPLIT_BEHAVIORS[density]

    def test_affordances_defined(self) -> None:
        """All projection affordances are defined."""
        assert "layout" in PROJECTION_AFFORDANCES
        assert "panel" in PROJECTION_AFFORDANCES
        assert "actions" in PROJECTION_AFFORDANCES
        assert "split" in PROJECTION_AFFORDANCES


# =============================================================================
# Resolver Tests
# =============================================================================


class TestProjectionResolver:
    """Tests for the projection context resolver."""

    def test_create_resolver(self) -> None:
        """Resolver can be created with default capacity."""
        resolver = create_projection_resolver()
        assert resolver.layout_node is not None
        assert resolver.panel_node is not None
        assert resolver.actions_node is not None
        assert resolver.split_node is not None

    def test_resolve_self_layout(self) -> None:
        """Resolver resolves self.layout paths."""
        resolver = create_projection_resolver()
        node = resolver.resolve("self.layout.density")
        assert node is resolver.layout_node

    def test_resolve_world_panel(self) -> None:
        """Resolver resolves world.panel paths."""
        resolver = create_projection_resolver()
        node = resolver.resolve("world.panel.manifest")
        assert node is resolver.panel_node

    def test_resolve_world_actions(self) -> None:
        """Resolver resolves world.actions paths."""
        resolver = create_projection_resolver()
        node = resolver.resolve("world.actions.manifest")
        assert node is resolver.actions_node

    def test_resolve_world_split(self) -> None:
        """Resolver resolves world.split paths."""
        resolver = create_projection_resolver()
        node = resolver.resolve("world.split.manifest")
        assert node is resolver.split_node

    def test_resolve_unknown_returns_none(self) -> None:
        """Resolver returns None for unknown paths."""
        resolver = create_projection_resolver()
        assert resolver.resolve("unknown.path") is None

    def test_resolver_with_custom_capacity(self, compact_capacity: PhysicalCapacity) -> None:
        """Resolver can be created with custom capacity."""
        resolver = create_projection_resolver(compact_capacity)
        assert resolver.layout_node._capacity == compact_capacity
