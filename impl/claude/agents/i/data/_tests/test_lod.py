"""
Tests for LOD (Level of Detail) projection system.

The LODProjector is the key abstraction for semantic zoom,
replacing discrete screens with continuous detail levels.
"""

from __future__ import annotations

import pytest

from ...widgets.density_field import Phase
from ..lod import LODLevel, LODProjector, can_zoom_in, can_zoom_out, get_default_lod
from ..state import AgentSnapshot


class TestLODLevel:
    """Test the LODLevel enum and its navigation methods."""

    def test_lod_levels_defined(self):
        """Test that all three LOD levels are defined."""
        assert LODLevel.ORBIT is not None
        assert LODLevel.SURFACE is not None
        assert LODLevel.INTERNAL is not None

    def test_lod_level_values(self):
        """Test LOD level numeric values."""
        assert LODLevel.ORBIT.value == 0
        assert LODLevel.SURFACE.value == 1
        assert LODLevel.INTERNAL.value == 2

    def test_zoom_in_from_orbit(self):
        """Test zooming in from ORBIT goes to SURFACE."""
        result = LODLevel.ORBIT.zoom_in()
        assert result == LODLevel.SURFACE

    def test_zoom_in_from_surface(self):
        """Test zooming in from SURFACE goes to INTERNAL."""
        result = LODLevel.SURFACE.zoom_in()
        assert result == LODLevel.INTERNAL

    def test_zoom_in_from_internal_returns_none(self):
        """Test zooming in from INTERNAL returns None (max zoom)."""
        result = LODLevel.INTERNAL.zoom_in()
        assert result is None

    def test_zoom_out_from_internal(self):
        """Test zooming out from INTERNAL goes to SURFACE."""
        result = LODLevel.INTERNAL.zoom_out()
        assert result == LODLevel.SURFACE

    def test_zoom_out_from_surface(self):
        """Test zooming out from SURFACE goes to ORBIT."""
        result = LODLevel.SURFACE.zoom_out()
        assert result == LODLevel.ORBIT

    def test_zoom_out_from_orbit_returns_none(self):
        """Test zooming out from ORBIT returns None (min zoom)."""
        result = LODLevel.ORBIT.zoom_out()
        assert result is None

    def test_zoom_chain(self):
        """Test full zoom chain: ORBIT → SURFACE → INTERNAL → SURFACE → ORBIT."""
        level: LODLevel = LODLevel.ORBIT

        # Zoom in twice
        next_level = level.zoom_in()
        assert next_level == LODLevel.SURFACE
        next_level = next_level.zoom_in()
        assert next_level == LODLevel.INTERNAL

        # Zoom out twice
        next_level = next_level.zoom_out()
        assert next_level == LODLevel.SURFACE
        next_level = next_level.zoom_out()
        assert next_level == LODLevel.ORBIT


class TestLODProjector:
    """Test the LODProjector functor."""

    @pytest.fixture
    def sample_snapshot(self) -> AgentSnapshot:
        """Create a sample agent snapshot for testing."""
        return AgentSnapshot(
            id="test-agent",
            name="TestAgent",
            phase=Phase.ACTIVE,
            activity=0.7,
            summary="Test agent for LOD projection",
            grid_x=1,
            grid_y=1,
            children=["child1", "child2"],
            connections={"agent2": 0.8, "agent3": 0.5},
        )

    @pytest.fixture
    def projector(self) -> LODProjector:
        """Create a LODProjector instance."""
        return LODProjector()

    def test_projector_creation(self, projector):
        """Test that LODProjector can be created."""
        assert projector is not None

    def test_project_orbit_returns_widget(self, projector, sample_snapshot):
        """Test that projecting to ORBIT returns a widget."""
        widget = projector.project(sample_snapshot, LODLevel.ORBIT)
        assert widget is not None
        # Should return an AgentCard or Static (depending on implementation)
        from textual.widgets import Static

        from ...screens.flux import AgentCard

        assert isinstance(widget, (AgentCard, Static))

    def test_project_surface_returns_widget(self, projector, sample_snapshot):
        """Test that projecting to SURFACE returns a widget."""
        widget = projector.project(sample_snapshot, LODLevel.SURFACE)
        assert widget is not None
        # Should return a widget
        from textual.widgets import Static

        assert isinstance(widget, Static)

    def test_project_internal_returns_widget(self, projector, sample_snapshot):
        """Test that projecting to INTERNAL returns a widget."""
        widget = projector.project(sample_snapshot, LODLevel.INTERNAL)
        assert widget is not None
        # Should return a widget
        from textual.widgets import Static

        assert isinstance(widget, Static)

    def test_project_different_levels_return_different_widgets(self, projector, sample_snapshot):
        """Test that different LOD levels return different widget types."""
        orbit_widget = projector.project(sample_snapshot, LODLevel.ORBIT)
        surface_widget = projector.project(sample_snapshot, LODLevel.SURFACE)
        internal_widget = projector.project(sample_snapshot, LODLevel.INTERNAL)

        # All should be widgets (Widget is the base class, not Static)
        from textual.widget import Widget

        assert isinstance(orbit_widget, Widget)
        assert isinstance(surface_widget, Widget)
        assert isinstance(internal_widget, Widget)

        # They should be distinct instances
        assert orbit_widget is not surface_widget
        assert surface_widget is not internal_widget

    def test_interpolate_returns_parameters(self, projector):
        """Test that interpolate returns a dict of parameters."""
        params = projector.interpolate(LODLevel.ORBIT, LODLevel.SURFACE, 0.5)
        assert isinstance(params, dict)
        assert "opacity" in params
        assert "scale" in params
        assert "detail_level" in params

    def test_interpolate_progress_zero(self, projector):
        """Test interpolation at progress=0 (start of transition)."""
        params = projector.interpolate(LODLevel.ORBIT, LODLevel.SURFACE, 0.0)
        # At progress 0, we're still at the from_level
        assert params["detail_level"] == LODLevel.ORBIT.value

    def test_interpolate_progress_one(self, projector):
        """Test interpolation at progress=1 (end of transition)."""
        params = projector.interpolate(LODLevel.ORBIT, LODLevel.SURFACE, 1.0)
        # At progress 1, we're at the to_level
        assert params["detail_level"] == LODLevel.SURFACE.value

    def test_interpolate_progress_half(self, projector):
        """Test interpolation at progress=0.5 (midpoint)."""
        params = projector.interpolate(LODLevel.ORBIT, LODLevel.SURFACE, 0.5)
        # At progress 0.5, we're halfway between levels
        expected_detail = (LODLevel.ORBIT.value + LODLevel.SURFACE.value) / 2
        assert params["detail_level"] == expected_detail


class TestLODHelpers:
    """Test helper functions for LOD management."""

    def test_get_default_lod(self):
        """Test that default LOD is ORBIT."""
        default = get_default_lod()
        assert default == LODLevel.ORBIT

    def test_can_zoom_in_from_orbit(self):
        """Test can_zoom_in returns True from ORBIT."""
        assert can_zoom_in(LODLevel.ORBIT) is True

    def test_can_zoom_in_from_surface(self):
        """Test can_zoom_in returns True from SURFACE."""
        assert can_zoom_in(LODLevel.SURFACE) is True

    def test_can_zoom_in_from_internal(self):
        """Test can_zoom_in returns False from INTERNAL."""
        assert can_zoom_in(LODLevel.INTERNAL) is False

    def test_can_zoom_out_from_orbit(self):
        """Test can_zoom_out returns False from ORBIT."""
        assert can_zoom_out(LODLevel.ORBIT) is False

    def test_can_zoom_out_from_surface(self):
        """Test can_zoom_out returns True from SURFACE."""
        assert can_zoom_out(LODLevel.SURFACE) is True

    def test_can_zoom_out_from_internal(self):
        """Test can_zoom_out returns True from INTERNAL."""
        assert can_zoom_out(LODLevel.INTERNAL) is True


class TestLODProjectorEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def projector(self) -> LODProjector:
        """Create a LODProjector instance."""
        return LODProjector()

    def test_project_with_minimal_snapshot(self, projector):
        """Test projection with minimal agent data."""
        minimal_snapshot = AgentSnapshot(
            id="minimal",
            name="Minimal",
        )
        # Should not raise error
        widget = projector.project(minimal_snapshot, LODLevel.ORBIT)
        assert widget is not None

    def test_project_with_void_phase(self, projector):
        """Test projection of agent in VOID phase."""
        void_snapshot = AgentSnapshot(
            id="void-agent",
            name="VoidAgent",
            phase=Phase.VOID,
            activity=0.0,
        )
        widget = projector.project(void_snapshot, LODLevel.ORBIT)
        assert widget is not None

    def test_project_with_high_activity(self, projector):
        """Test projection of agent with maximum activity."""
        active_snapshot = AgentSnapshot(
            id="active-agent",
            name="ActiveAgent",
            phase=Phase.ACTIVE,
            activity=1.0,
        )
        widget = projector.project(active_snapshot, LODLevel.ORBIT)
        assert widget is not None
