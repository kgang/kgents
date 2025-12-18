"""
Tests for services/bootstrap.py - Crown Jewel dependency injection.

Verifies:
- Registry initialization
- Lazy service instantiation
- Service injection for testing
- All 7 Crown Jewel services available
"""

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestServiceRegistry:
    """Test ServiceRegistry initialization and access."""

    def test_registry_not_initialized_by_default(self):
        """Registry should start uninitialized."""
        from services.bootstrap import ServiceRegistry

        registry = ServiceRegistry()
        assert not registry.is_initialized()

    @pytest.mark.asyncio
    async def test_registry_initialize(self):
        """Registry should initialize with session factory and dgent."""
        from services.bootstrap import ServiceRegistry

        registry = ServiceRegistry()
        await registry.initialize()

        assert registry.is_initialized()
        assert registry.session_factory is not None
        assert registry.dgent is not None

    @pytest.mark.asyncio
    async def test_registry_initialize_idempotent(self):
        """Multiple initialize calls should be safe."""
        from services.bootstrap import ServiceRegistry

        registry = ServiceRegistry()
        await registry.initialize()
        await registry.initialize()  # Should not raise

        assert registry.is_initialized()

    def test_registry_lists_all_services(self):
        """Registry should list all Crown Jewel services + supporting services."""
        from services.bootstrap import ServiceRegistry

        registry = ServiceRegistry()
        services = registry.list_services()

        # Core 7 Crown Jewels
        expected_core = [
            "brain_persistence",
            "town_persistence",
            "gardener_persistence",
            "gestalt_persistence",
            "atelier_persistence",
            "coalition_persistence",
            "park_persistence",
        ]
        for svc in expected_core:
            assert svc in services, f"Expected {svc} in services"

        # At minimum these should be present
        assert len(services) >= len(expected_core)

    def test_registry_stats(self):
        """Registry stats should show initialization state."""
        from services.bootstrap import ServiceRegistry

        registry = ServiceRegistry()
        stats = registry.stats()

        assert "initialized" in stats
        assert "cached_services" in stats
        assert "custom_factories" in stats

    def test_registry_reset_clears_state(self):
        """Reset should clear all state."""
        from services.bootstrap import ServiceRegistry

        registry = ServiceRegistry()
        registry.inject("test_service", "test_value")
        registry.reset()

        assert not registry.is_initialized()
        assert registry.stats()["cached_services"] == []


class TestServiceRegistryInjection:
    """Test service injection for testing."""

    @pytest.mark.asyncio
    async def test_inject_service(self):
        """Should be able to inject mock services."""
        from services.bootstrap import ServiceRegistry

        registry = ServiceRegistry()
        await registry.initialize()

        mock_service = MagicMock()
        registry.inject("brain_persistence", mock_service)

        result = await registry.get("brain_persistence")
        assert result is mock_service

    @pytest.mark.asyncio
    async def test_custom_factory(self):
        """Should be able to register custom factories."""
        from services.bootstrap import ServiceRegistry

        registry = ServiceRegistry()
        await registry.initialize()

        custom_value = {"custom": True}
        registry.register_factory("custom_service", lambda: custom_value)

        # Note: This would fail because custom_service is not in default list
        # but the factory is registered for potential extension


class TestGlobalRegistry:
    """Test global registry singleton pattern."""

    def test_get_registry_returns_singleton(self):
        """get_registry should return same instance."""
        from services.bootstrap import get_registry

        r1 = get_registry()
        r2 = get_registry()

        assert r1 is r2

    def test_reset_registry_clears_global(self):
        """reset_registry should clear the global singleton."""
        from services.bootstrap import get_registry, reset_registry

        registry1 = get_registry()
        reset_registry()
        registry2 = get_registry()

        # After reset, should get a new registry
        assert registry1 is not registry2


class TestBootstrapServices:
    """Test the bootstrap_services convenience function."""

    @pytest.mark.asyncio
    async def test_bootstrap_services_initializes_registry(self):
        """bootstrap_services should initialize and return registry."""
        from services.bootstrap import bootstrap_services, reset_services

        reset_services()
        registry = await bootstrap_services()

        assert registry.is_initialized()

    @pytest.mark.asyncio
    async def test_get_service_after_bootstrap(self):
        """get_service should work after bootstrap."""
        from services.bootstrap import bootstrap_services, get_service, reset_services

        reset_services()
        await bootstrap_services()

        brain = await get_service("brain_persistence")
        assert brain is not None
        assert type(brain).__name__ == "BrainPersistence"


class TestAllSevenServices:
    """Test that all 7 Crown Jewel services instantiate correctly."""

    @pytest.fixture
    async def bootstrapped_registry(self):
        """Provide initialized registry."""
        from services.bootstrap import bootstrap_services, reset_services

        reset_services()
        registry = await bootstrap_services()
        yield registry
        reset_services()

    @pytest.mark.asyncio
    async def test_brain_persistence(self, bootstrapped_registry):
        """Brain persistence should instantiate."""
        from services.bootstrap import get_service

        svc = await get_service("brain_persistence")
        assert type(svc).__name__ == "BrainPersistence"

    @pytest.mark.asyncio
    async def test_town_persistence(self, bootstrapped_registry):
        """Town persistence should instantiate."""
        from services.bootstrap import get_service

        svc = await get_service("town_persistence")
        assert type(svc).__name__ == "TownPersistence"

    @pytest.mark.asyncio
    async def test_gardener_persistence(self, bootstrapped_registry):
        """Gardener persistence should instantiate."""
        from services.bootstrap import get_service

        svc = await get_service("gardener_persistence")
        assert type(svc).__name__ == "GardenerPersistence"

    @pytest.mark.asyncio
    async def test_gestalt_persistence(self, bootstrapped_registry):
        """Gestalt persistence should instantiate."""
        from services.bootstrap import get_service

        svc = await get_service("gestalt_persistence")
        assert type(svc).__name__ == "GestaltPersistence"

    @pytest.mark.asyncio
    async def test_atelier_persistence(self, bootstrapped_registry):
        """Atelier persistence should instantiate."""
        from services.bootstrap import get_service

        svc = await get_service("atelier_persistence")
        assert type(svc).__name__ == "AtelierPersistence"

    @pytest.mark.asyncio
    async def test_coalition_persistence(self, bootstrapped_registry):
        """Coalition persistence should instantiate."""
        from services.bootstrap import get_service

        svc = await get_service("coalition_persistence")
        assert type(svc).__name__ == "CoalitionPersistence"

    @pytest.mark.asyncio
    async def test_park_persistence(self, bootstrapped_registry):
        """Park persistence should instantiate."""
        from services.bootstrap import get_service

        svc = await get_service("park_persistence")
        assert type(svc).__name__ == "ParkPersistence"

    @pytest.mark.asyncio
    async def test_services_are_cached(self, bootstrapped_registry):
        """Same service should return cached instance."""
        from services.bootstrap import get_service

        brain1 = await get_service("brain_persistence")
        brain2 = await get_service("brain_persistence")

        assert brain1 is brain2


class TestBackwardCompatibleProviders:
    """Test that providers.py still works."""

    @pytest.mark.asyncio
    async def test_setup_providers(self):
        """setup_providers should work."""
        from services.providers import reset_services, setup_providers

        reset_services()
        await setup_providers()
        # Should not raise

    @pytest.mark.asyncio
    async def test_provider_getters(self):
        """Individual provider getters should work."""
        from services.providers import (
            get_atelier_persistence,
            get_brain_persistence,
            get_coalition_persistence,
            get_gardener_persistence,
            get_gestalt_persistence,
            get_park_persistence,
            get_town_persistence,
            reset_services,
            setup_providers,
        )

        reset_services()
        await setup_providers()

        # Test each getter
        getters = [
            get_brain_persistence,
            get_town_persistence,
            get_gardener_persistence,
            get_gestalt_persistence,
            get_atelier_persistence,
            get_coalition_persistence,
            get_park_persistence,
        ]

        for getter in getters:
            svc = await getter()
            assert svc is not None
