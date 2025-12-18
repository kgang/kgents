"""Integration tests for Phase 6 screen migration.

This test suite verifies that all major screens:
1. Inherit from KgentsScreen
2. Have ANCHOR attributes defined
3. Can be imported correctly
4. Maintain their existing functionality
"""

import pytest

from agents.i.screens import (
    CockpitScreen,
    FluxScreen,
    KgentsScreen,
    MRIScreen,
    ObservatoryScreen,
)


class TestScreenInheritance:
    """Test that all major screens inherit from KgentsScreen."""

    def test_cockpit_inherits_from_kgents_screen(self) -> None:
        """CockpitScreen should inherit from KgentsScreen."""
        assert issubclass(CockpitScreen, KgentsScreen)

    def test_observatory_inherits_from_kgents_screen(self) -> None:
        """ObservatoryScreen should inherit from KgentsScreen."""
        assert issubclass(ObservatoryScreen, KgentsScreen)

    def test_flux_inherits_from_kgents_screen(self) -> None:
        """FluxScreen should inherit from KgentsScreen."""
        assert issubclass(FluxScreen, KgentsScreen)

    def test_mri_inherits_from_kgents_screen(self) -> None:
        """MRIScreen should inherit from KgentsScreen."""
        assert issubclass(MRIScreen, KgentsScreen)


class TestAnchorAttributes:
    """Test that all screens have ANCHOR attributes defined."""

    def test_cockpit_has_anchor(self) -> None:
        """CockpitScreen should have ANCHOR attribute."""
        assert hasattr(CockpitScreen, "ANCHOR")
        assert isinstance(CockpitScreen.ANCHOR, str)
        assert len(CockpitScreen.ANCHOR) > 0

    def test_observatory_has_anchor(self) -> None:
        """ObservatoryScreen should have ANCHOR attribute."""
        assert hasattr(ObservatoryScreen, "ANCHOR")
        assert isinstance(ObservatoryScreen.ANCHOR, str)
        assert len(ObservatoryScreen.ANCHOR) > 0

    def test_flux_has_anchor(self) -> None:
        """FluxScreen should have ANCHOR attribute."""
        assert hasattr(FluxScreen, "ANCHOR")
        assert isinstance(FluxScreen.ANCHOR, str)
        assert len(FluxScreen.ANCHOR) > 0

    def test_mri_has_anchor(self) -> None:
        """MRIScreen should have ANCHOR attribute."""
        assert hasattr(MRIScreen, "ANCHOR")
        assert isinstance(MRIScreen.ANCHOR, str)
        assert len(MRIScreen.ANCHOR) > 0


class TestPassthroughKeys:
    """Test that screens inherit passthrough key behavior from KgentsScreen."""

    def test_cockpit_has_passthrough_keys(self) -> None:
        """CockpitScreen should have PASSTHROUGH_KEYS from base class."""
        assert hasattr(CockpitScreen, "PASSTHROUGH_KEYS")
        assert "q" in CockpitScreen.PASSTHROUGH_KEYS
        assert "tab" in CockpitScreen.PASSTHROUGH_KEYS

    def test_observatory_has_passthrough_keys(self) -> None:
        """ObservatoryScreen should have PASSTHROUGH_KEYS from base class."""
        assert hasattr(ObservatoryScreen, "PASSTHROUGH_KEYS")
        assert "q" in ObservatoryScreen.PASSTHROUGH_KEYS
        assert "tab" in ObservatoryScreen.PASSTHROUGH_KEYS

    def test_flux_has_passthrough_keys(self) -> None:
        """FluxScreen should have PASSTHROUGH_KEYS from base class."""
        assert hasattr(FluxScreen, "PASSTHROUGH_KEYS")
        assert "q" in FluxScreen.PASSTHROUGH_KEYS
        assert "tab" in FluxScreen.PASSTHROUGH_KEYS

    def test_mri_has_passthrough_keys(self) -> None:
        """MRIScreen should have PASSTHROUGH_KEYS from base class."""
        assert hasattr(MRIScreen, "PASSTHROUGH_KEYS")
        assert "q" in MRIScreen.PASSTHROUGH_KEYS
        assert "tab" in MRIScreen.PASSTHROUGH_KEYS


class TestImports:
    """Test that all necessary components can be imported from screens.__init__."""

    def test_import_base_classes(self) -> None:
        """Base classes should be importable from screens."""
        from agents.i.screens import KgentsModalScreen, KgentsScreen

        assert KgentsScreen is not None
        assert KgentsModalScreen is not None

    def test_import_transitions(self) -> None:
        """Transition system should be importable from screens."""
        from agents.i.screens import (
            GentleNavigator,
            ScreenTransition,
            TransitionStyle,
        )

        assert TransitionStyle is not None
        assert ScreenTransition is not None
        assert GentleNavigator is not None

    def test_import_mixins(self) -> None:
        """Mixins should be importable from screens."""
        from agents.i.screens import (
            DashboardHelpMixin,
            DashboardNavigationMixin,
            DashboardScreensMixin,
        )

        assert DashboardNavigationMixin is not None
        assert DashboardScreensMixin is not None
        assert DashboardHelpMixin is not None

    def test_import_screens(self) -> None:
        """All screens should be importable from screens."""
        from agents.i.screens import (
            CockpitScreen,
            FluxScreen,
            MRIScreen,
            ObservatoryScreen,
        )

        assert CockpitScreen is not None
        assert ObservatoryScreen is not None
        assert FluxScreen is not None
        assert MRIScreen is not None
