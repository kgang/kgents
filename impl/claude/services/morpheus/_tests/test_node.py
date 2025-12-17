"""
Tests for MorpheusNode AGENTESE node.

Tests:
- manifest returns gateway status
- complete processes requests
- providers filters based on observer archetype
- metrics requires privileged access
"""

from __future__ import annotations

import pytest

from services.morpheus import (
    MorpheusGateway,
    MorpheusNode,
    MorpheusPersistence,
)
from services.morpheus.adapters import MockAdapter


class MockObserver:
    """Mock observer for testing."""

    def __init__(self, archetype: str = "guest") -> None:
        self.archetype = archetype


@pytest.fixture
def gateway() -> MorpheusGateway:
    """Create gateway with mock adapter."""
    gw = MorpheusGateway()
    gw.register_provider(
        name="mock",
        adapter=MockAdapter(default_response="Test response"),
        prefix="test-",
    )
    return gw


@pytest.fixture
def persistence(gateway: MorpheusGateway) -> MorpheusPersistence:
    """Create persistence layer."""
    return MorpheusPersistence(gateway=gateway)


@pytest.fixture
def node(persistence: MorpheusPersistence) -> MorpheusNode:
    """Create MorpheusNode."""
    return MorpheusNode(morpheus_persistence=persistence)


class TestMorpheusNodeHandle:
    """Test node handle property."""

    def test_handle(self, node: MorpheusNode) -> None:
        """Test handle returns correct path."""
        assert node.handle == "world.morpheus"


class TestMorpheusNodeAffordances:
    """Test observer-dependent affordances."""

    def test_admin_affordances(self, node: MorpheusNode) -> None:
        """Test admin gets full affordances."""
        affordances = node._get_affordances_for_archetype("admin")
        assert "complete" in affordances
        assert "stream" in affordances
        assert "health" in affordances
        assert "providers" in affordances
        assert "metrics" in affordances
        assert "configure" in affordances

    def test_developer_affordances(self, node: MorpheusNode) -> None:
        """Test developer gets standard affordances."""
        affordances = node._get_affordances_for_archetype("developer")
        assert "complete" in affordances
        assert "providers" in affordances
        assert "metrics" in affordances
        assert "configure" not in affordances

    def test_guest_affordances(self, node: MorpheusNode) -> None:
        """Test guest gets limited affordances."""
        affordances = node._get_affordances_for_archetype("guest")
        assert "complete" in affordances
        assert "stream" in affordances
        assert "health" in affordances
        assert "providers" not in affordances
        assert "metrics" not in affordances


class TestMorpheusNodeManifest:
    """Test manifest aspect."""

    @pytest.mark.asyncio
    async def test_manifest_returns_status(self, node: MorpheusNode) -> None:
        """Test manifest returns gateway status."""
        observer = MockObserver("guest")
        result = await node.manifest(observer)

        # Should return rendering with status
        assert hasattr(result, "to_dict")
        data = result.to_dict()
        assert data["type"] == "morpheus_manifest"
        assert "providers_total" in data


class TestMorpheusNodeComplete:
    """Test complete aspect."""

    @pytest.mark.asyncio
    async def test_complete_success(self, node: MorpheusNode) -> None:
        """Test successful completion."""
        observer = MockObserver("guest")
        result = await node._invoke_aspect(
            "complete",
            observer,
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
        )

        assert result["type"] == "completion_result"
        assert result["response"] == "Test response"
        assert result["model"] == "test-model"
        assert result["provider"] == "mock"
        assert "latency_ms" in result

    @pytest.mark.asyncio
    async def test_complete_missing_model(self, node: MorpheusNode) -> None:
        """Test error when model missing."""
        observer = MockObserver("guest")
        result = await node._invoke_aspect(
            "complete",
            observer,
            messages=[{"role": "user", "content": "Hello"}],
        )

        assert "error" in result
        assert "model" in result["error"]

    @pytest.mark.asyncio
    async def test_complete_missing_messages(self, node: MorpheusNode) -> None:
        """Test error when messages missing."""
        observer = MockObserver("guest")
        result = await node._invoke_aspect(
            "complete",
            observer,
            model="test-model",
        )

        assert "error" in result
        assert "messages" in result["error"]


class TestMorpheusNodeProviders:
    """Test providers aspect with observer filtering."""

    @pytest.mark.asyncio
    async def test_admin_sees_all_providers(
        self, node: MorpheusNode, gateway: MorpheusGateway
    ) -> None:
        """Test admin sees all providers."""
        # Add a disabled provider
        gateway.register_provider(
            name="disabled",
            adapter=MockAdapter(),
            prefix="disabled-",
            enabled=False,
        )

        observer = MockObserver("admin")
        result = await node._invoke_aspect("providers", observer)

        assert result["type"] == "providers_list"
        assert result["filter"] == "all"
        # Admin sees both enabled and disabled
        assert len(result["providers"]) == 2

    @pytest.mark.asyncio
    async def test_developer_sees_enabled_only(
        self, node: MorpheusNode, gateway: MorpheusGateway
    ) -> None:
        """Test developer sees enabled providers only."""
        # Add a disabled provider
        gateway.register_provider(
            name="disabled",
            adapter=MockAdapter(),
            prefix="disabled-",
            enabled=False,
        )

        observer = MockObserver("developer")
        result = await node._invoke_aspect("providers", observer)

        assert result["filter"] == "enabled"
        # Developer only sees enabled provider
        assert len(result["providers"]) == 1

    @pytest.mark.asyncio
    async def test_guest_sees_public_only(
        self, node: MorpheusNode, gateway: MorpheusGateway
    ) -> None:
        """Test guest sees public providers only."""
        # Add a private provider
        gateway.register_provider(
            name="private",
            adapter=MockAdapter(),
            prefix="private-",
            public=False,
        )

        observer = MockObserver("guest")
        result = await node._invoke_aspect("providers", observer)

        assert result["filter"] == "public"
        # Guest only sees public provider
        assert len(result["providers"]) == 1


class TestMorpheusNodeMetrics:
    """Test metrics aspect with access control."""

    @pytest.mark.asyncio
    async def test_admin_can_access_metrics(self, node: MorpheusNode) -> None:
        """Test admin can access metrics."""
        observer = MockObserver("admin")
        result = await node._invoke_aspect("metrics", observer)

        assert result["type"] == "morpheus_metrics"
        assert "total_requests" in result
        assert "total_errors" in result

    @pytest.mark.asyncio
    async def test_developer_can_access_metrics(self, node: MorpheusNode) -> None:
        """Test developer can access metrics."""
        observer = MockObserver("developer")
        result = await node._invoke_aspect("metrics", observer)

        assert result["type"] == "morpheus_metrics"

    @pytest.mark.asyncio
    async def test_guest_cannot_access_metrics(self, node: MorpheusNode) -> None:
        """Test guest cannot access metrics."""
        observer = MockObserver("guest")
        result = await node._invoke_aspect("metrics", observer)

        assert "error" in result
        assert "Forbidden" in result["error"]


class TestMorpheusNodeHealth:
    """Test health aspect."""

    @pytest.mark.asyncio
    async def test_health_returns_status(self, node: MorpheusNode) -> None:
        """Test health returns gateway health."""
        observer = MockObserver("guest")
        result = await node._invoke_aspect("health", observer)

        assert "status" in result
        assert "providers" in result


class TestMorpheusNodeRoute:
    """Test route aspect."""

    @pytest.mark.asyncio
    async def test_route_for_known_model(self, node: MorpheusNode) -> None:
        """Test route info for known model prefix."""
        observer = MockObserver("developer")
        result = await node._invoke_aspect("route", observer, model="test-model")

        assert result["model"] == "test-model"
        assert result["routed"] is True
        assert result["provider"] == "mock"

    @pytest.mark.asyncio
    async def test_route_for_unknown_model(self, node: MorpheusNode) -> None:
        """Test route info for unknown model."""
        observer = MockObserver("developer")
        result = await node._invoke_aspect("route", observer, model="unknown-model")

        assert result["routed"] is False
        assert "available_prefixes" in result

    @pytest.mark.asyncio
    async def test_route_missing_model(self, node: MorpheusNode) -> None:
        """Test error when model missing."""
        observer = MockObserver("developer")
        result = await node._invoke_aspect("route", observer)

        assert "error" in result
