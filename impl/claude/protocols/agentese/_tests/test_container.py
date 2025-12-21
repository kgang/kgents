"""
Tests for AGENTESE Service Container.

Verifies dependency injection and provider resolution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from protocols.agentese.container import (
    DependencyNotFoundError,
    ProviderEntry,
    ServiceContainer,
    create_container,
    get_container,
    reset_container,
)
from protocols.agentese.node import BaseLogosNode, BasicRendering, Renderable
from protocols.agentese.registry import NodeMetadata

# === Test Dependencies ===


@dataclass
class MockService:
    """Mock service for testing."""

    name: str = "mock_service"
    call_count: int = 0


@dataclass
class MockConfig:
    """Mock configuration for testing."""

    debug: bool = False
    timeout: int = 30


class NodeWithDeps(BaseLogosNode):
    """Node that requires dependencies."""

    def __init__(self, service: MockService, config: MockConfig):
        self._service = service
        self._config = config

    @property
    def handle(self) -> str:
        return "test.withdeps"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ()

    async def manifest(self, observer: Any) -> Renderable:
        return BasicRendering(summary="Node with deps")

    async def _invoke_aspect(self, aspect: str, observer: Any, **kwargs: Any) -> Any:
        return {"service": self._service.name, "debug": self._config.debug}


class NodeWithDefaults(BaseLogosNode):
    """Node with optional dependencies."""

    def __init__(self, service: MockService | None = None):
        self._service = service

    @property
    def handle(self) -> str:
        return "test.defaults"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ()

    async def manifest(self, observer: Any) -> Renderable:
        return BasicRendering(summary="Node with defaults")

    async def _invoke_aspect(self, aspect: str, observer: Any, **kwargs: Any) -> Any:
        return {"has_service": self._service is not None}


class NodeNoDeps(BaseLogosNode):
    """Node without dependencies."""

    @property
    def handle(self) -> str:
        return "test.nodeps"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ()

    async def manifest(self, observer: Any) -> Renderable:
        return BasicRendering(summary="Node without deps")

    async def _invoke_aspect(self, aspect: str, observer: Any, **kwargs: Any) -> Any:
        return {"no_deps": True}


# === Fixtures ===


@pytest.fixture(autouse=True)
def clean_container():
    """Reset container before each test."""
    reset_container()
    yield
    reset_container()


@pytest.fixture
def container():
    """Create a fresh container."""
    return create_container()


# === Test Provider Registration ===


class TestProviderRegistration:
    """Tests for provider registration."""

    def test_register_sync_provider(self, container):
        """Register a sync provider."""

        def get_service() -> MockService:
            return MockService(name="sync")

        container.register("service", get_service)
        assert container.has("service")

    def test_register_async_provider(self, container):
        """Register an async provider."""

        async def get_service() -> MockService:
            return MockService(name="async")

        container.register("service", get_service)
        assert container.has("service")

    def test_register_lambda_provider(self, container):
        """Register a lambda provider."""
        container.register("service", lambda: MockService(name="lambda"))
        assert container.has("service")

    def test_register_value(self, container):
        """Register a pre-instantiated value."""
        service = MockService(name="value")
        container.register_value("service", service)
        assert container.has("service")

    def test_has_unregistered(self, container):
        """has() returns False for unregistered."""
        assert not container.has("nonexistent")

    def test_list_providers(self, container):
        """list_providers() returns registered names."""
        container.register("service1", lambda: MockService())
        container.register("service2", lambda: MockService())

        providers = container.list_providers()
        assert "service1" in providers
        assert "service2" in providers


# === Test Dependency Resolution ===


class TestDependencyResolution:
    """Tests for dependency resolution."""

    @pytest.mark.asyncio
    async def test_resolve_sync_provider(self, container):
        """Resolve a sync provider."""

        def get_service() -> MockService:
            return MockService(name="resolved")

        container.register("service", get_service)
        service = await container.resolve("service")

        assert isinstance(service, MockService)
        assert service.name == "resolved"

    @pytest.mark.asyncio
    async def test_resolve_async_provider(self, container):
        """Resolve an async provider."""

        async def get_service() -> MockService:
            return MockService(name="async_resolved")

        container.register("service", get_service)
        service = await container.resolve("service")

        assert isinstance(service, MockService)
        assert service.name == "async_resolved"

    @pytest.mark.asyncio
    async def test_resolve_value(self, container):
        """Resolve a registered value."""
        original = MockService(name="original")
        container.register_value("service", original)

        resolved = await container.resolve("service")
        assert resolved is original

    @pytest.mark.asyncio
    async def test_resolve_unregistered_raises(self, container):
        """Resolve unregistered raises KeyError."""
        with pytest.raises(KeyError):
            await container.resolve("nonexistent")

    @pytest.mark.asyncio
    async def test_singleton_caching(self, container):
        """Singleton providers are cached."""
        call_count = 0

        def get_service() -> MockService:
            nonlocal call_count
            call_count += 1
            return MockService(name=f"call_{call_count}")

        container.register("service", get_service, singleton=True)

        service1 = await container.resolve("service")
        service2 = await container.resolve("service")

        assert service1 is service2
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_non_singleton_not_cached(self, container):
        """Non-singleton providers are not cached."""
        call_count = 0

        def get_service() -> MockService:
            nonlocal call_count
            call_count += 1
            return MockService(name=f"call_{call_count}")

        container.register("service", get_service, singleton=False)

        service1 = await container.resolve("service")
        service2 = await container.resolve("service")

        assert service1 is not service2
        assert call_count == 2


# === Test Node Creation ===


class TestNodeCreation:
    """Tests for node creation with dependency injection."""

    @pytest.mark.asyncio
    async def test_create_node_no_deps(self, container):
        """Create node without dependencies."""
        node = await container.create_node(NodeNoDeps)
        assert node is not None
        assert node.handle == "test.nodeps"

    @pytest.mark.asyncio
    async def test_create_node_with_deps(self, container):
        """Create node with injected dependencies."""
        container.register("service", lambda: MockService(name="injected"))
        container.register("config", lambda: MockConfig(debug=True))

        node = await container.create_node(NodeWithDeps)
        assert node is not None
        assert node._service.name == "injected"
        assert node._config.debug is True

    @pytest.mark.asyncio
    async def test_create_node_with_metadata_deps(self, container):
        """Create node using metadata dependencies."""
        container.register("service", lambda: MockService(name="from_meta"))
        container.register("config", lambda: MockConfig(timeout=60))

        meta = NodeMetadata(
            path="test.withdeps",
            dependencies=("service", "config"),
        )

        node = await container.create_node(NodeWithDeps, meta)
        assert node._service.name == "from_meta"

    @pytest.mark.asyncio
    async def test_create_node_with_defaults(self, container):
        """Create node with optional deps, some missing."""
        # Don't register 'service' - should use default None
        node = await container.create_node(NodeWithDefaults)
        assert node is not None
        assert node._service is None

    @pytest.mark.asyncio
    async def test_create_node_with_some_deps_registered(self, container):
        """Create node with only some deps registered fails immediately."""
        container.register("service", lambda: MockService(name="partial"))
        # config not registered

        # This should fail immediately with DependencyNotFoundError
        # (Enlightened Resolution: required deps fail fast)
        with pytest.raises(DependencyNotFoundError) as exc_info:
            await container.create_node(NodeWithDeps)

        # Error message should be helpful
        assert "config" in str(exc_info.value)
        assert "NodeWithDeps" in str(exc_info.value)
        assert "providers.py" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_required_deps_fail_immediately(self, container):
        """Required dependencies (no default) fail immediately if missing."""
        # NodeWithDeps requires both 'service' and 'config'
        # Register neither

        with pytest.raises(DependencyNotFoundError) as exc_info:
            await container.create_node(NodeWithDeps)

        # Should mention the first missing required dep
        assert "service" in str(exc_info.value) or "config" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_optional_deps_skipped_gracefully(self, container):
        """Optional dependencies (with default) are skipped if missing."""
        # NodeWithDefaults has: service: MockService | None = None
        # Don't register anything - should use the default

        node = await container.create_node(NodeWithDefaults)
        assert node is not None
        assert node._service is None  # Used default

    @pytest.mark.asyncio
    async def test_optional_deps_resolved_when_available(self, container):
        """Optional dependencies are resolved when registered."""
        container.register("service", lambda: MockService(name="optional_but_present"))

        node = await container.create_node(NodeWithDefaults)
        assert node is not None
        assert node._service is not None
        assert node._service.name == "optional_but_present"

    @pytest.mark.asyncio
    async def test_create_node_invocation(self, container):
        """Created node can be invoked."""
        container.register("service", lambda: MockService(name="invokable"))
        container.register("config", lambda: MockConfig(debug=True))

        node = await container.create_node(NodeWithDeps)
        from protocols.agentese.node import Observer

        result = await node.invoke("custom", Observer.test())
        assert result["service"] == "invokable"
        assert result["debug"] is True


# === Test Container Management ===


class TestContainerManagement:
    """Tests for container lifecycle management."""

    def test_clear_removes_all(self, container):
        """clear() removes providers and cache."""
        container.register("service", lambda: MockService())
        container.clear()

        assert not container.has("service")

    @pytest.mark.asyncio
    async def test_clear_cache_keeps_providers(self, container):
        """clear_cache() keeps providers but clears cached values."""
        call_count = 0

        def get_service() -> MockService:
            nonlocal call_count
            call_count += 1
            return MockService()

        container.register("service", get_service, singleton=True)

        # First resolution
        await container.resolve("service")
        assert call_count == 1

        # Clear cache
        container.clear_cache()

        # Second resolution calls provider again
        await container.resolve("service")
        assert call_count == 2

    def test_stats(self, container):
        """stats() returns container info."""
        container.register("service1", lambda: MockService())
        container.register_value("service2", MockService())

        stats = container.stats()
        assert stats["providers"] == 2
        assert "service1" in stats["provider_names"]
        assert "service2" in stats["provider_names"]


# === Test Global Container ===


class TestGlobalContainer:
    """Tests for global container singleton."""

    def test_get_container_returns_singleton(self):
        """get_container() returns same instance."""
        c1 = get_container()
        c2 = get_container()
        assert c1 is c2

    def test_reset_container_creates_new(self):
        """reset_container() allows new instance."""
        c1 = get_container()
        reset_container()
        c2 = get_container()
        assert c1 is not c2


# === Test ProviderEntry ===


class TestProviderEntry:
    """Tests for ProviderEntry."""

    def test_defaults(self):
        """ProviderEntry has sensible defaults."""
        entry = ProviderEntry(name="test", provider=lambda: None)
        assert entry.singleton is True
        assert entry.lazy is True

    def test_custom_options(self):
        """ProviderEntry accepts custom options."""
        entry = ProviderEntry(
            name="test",
            provider=lambda: None,
            singleton=False,
            lazy=False,
        )
        assert entry.singleton is False
        assert entry.lazy is False

    def test_frozen(self):
        """ProviderEntry is immutable."""
        entry = ProviderEntry(name="test", provider=lambda: None)
        with pytest.raises(Exception):  # FrozenInstanceError
            entry.name = "changed"  # type: ignore
