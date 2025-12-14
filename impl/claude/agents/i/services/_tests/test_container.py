"""
Tests for the DashboardServices container.

Verifies that the service container correctly:
- Creates and wires all services
- Preserves flags like demo_mode
- Provides access to the singleton EventBus
- Can be reset for testing
"""

from unittest.mock import Mock

import pytest
from agents.i.services.container import DashboardServices
from agents.i.services.events import EventBus, ScreenNavigationEvent


class TestDashboardServicesCreation:
    """Test the DashboardServices.create() factory method."""

    def test_create_returns_valid_container(self):
        """DashboardServices.create() should return a valid container with all services."""
        # Arrange
        mock_app = Mock()

        # Act
        services = DashboardServices.create(mock_app)

        # Assert
        assert services is not None
        assert services.state_manager is not None
        assert services.nav_controller is not None
        assert services.event_bus is not None

    def test_create_with_demo_mode(self):
        """DashboardServices.create(demo_mode=True) should preserve the flag."""
        # Arrange
        mock_app = Mock()

        # Act
        services = DashboardServices.create(mock_app, demo_mode=True)

        # Assert
        assert services.demo_mode is True

    def test_create_without_demo_mode(self):
        """DashboardServices.create() should default demo_mode to False."""
        # Arrange
        mock_app = Mock()

        # Act
        services = DashboardServices.create(mock_app)

        # Assert
        assert services.demo_mode is False


class TestDashboardServicesAccess:
    """Test that all services are accessible from the container."""

    def test_state_manager_is_accessible(self):
        """state_manager should be accessible and functional."""
        # Arrange
        mock_app = Mock()
        services = DashboardServices.create(mock_app)

        # Act
        services.state_manager.save_focus("test_screen", "test_focus")
        focus = services.state_manager.get_focus("test_screen")

        # Assert
        assert focus == "test_focus"

    def test_nav_controller_is_accessible(self):
        """nav_controller should be accessible and functional."""
        # Arrange
        mock_app = Mock()
        services = DashboardServices.create(mock_app)

        # Act
        current_lod = services.nav_controller.get_current_lod()

        # Assert - NavigationController starts at LOD 0 (Terrarium)
        assert current_lod == 0

    def test_event_bus_is_accessible(self):
        """event_bus should be accessible and functional."""
        # Arrange
        mock_app = Mock()
        services = DashboardServices.create(mock_app)
        events_received = []

        def handler(event: ScreenNavigationEvent) -> None:
            events_received.append(event)

        # Act
        services.event_bus.subscribe(ScreenNavigationEvent, handler)
        services.event_bus.emit(ScreenNavigationEvent(target_screen="cockpit"))

        # Assert
        assert len(events_received) == 1
        assert events_received[0].target_screen == "cockpit"


class TestEventBusSingleton:
    """Test that the EventBus is a singleton."""

    def test_event_bus_is_singleton(self):
        """Multiple containers should share the same EventBus instance."""
        # Arrange
        mock_app1 = Mock()
        mock_app2 = Mock()

        # Act
        services1 = DashboardServices.create(mock_app1)
        services2 = DashboardServices.create(mock_app2)

        # Assert - Both containers should have the same EventBus instance
        assert services1.event_bus is services2.event_bus
        assert services1.event_bus is EventBus.get()


class TestDashboardServicesReset:
    """Test the reset_state() method."""

    def test_reset_state_clears_state_manager(self):
        """reset_state() should clear the state manager."""
        # Arrange
        mock_app = Mock()
        services = DashboardServices.create(mock_app)
        services.state_manager.save_focus("screen", "focus")
        services.state_manager.push_history("screen", "focus")

        # Act
        services.reset_state()

        # Assert
        assert services.state_manager.get_focus("screen") is None
        assert services.state_manager.get_history() == []

    def test_reset_state_does_not_affect_event_bus(self):
        """reset_state() should NOT reset the EventBus (it's a singleton)."""
        # Arrange
        mock_app = Mock()
        services = DashboardServices.create(mock_app)
        events_received = []

        def handler(event: ScreenNavigationEvent) -> None:
            events_received.append(event)

        services.event_bus.subscribe(ScreenNavigationEvent, handler)

        # Act
        services.reset_state()
        services.event_bus.emit(ScreenNavigationEvent(target_screen="test"))

        # Assert - Handler should still be subscribed
        assert len(events_received) == 1
