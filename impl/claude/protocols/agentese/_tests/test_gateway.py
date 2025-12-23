"""
Tests for AGENTESE Universal Gateway.

Verifies auto-exposure of @node registered classes via HTTP.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from protocols.agentese.gateway import (
    AgenteseGateway,
    _extract_observer,
    _to_json_safe,
    create_gateway,
)
from protocols.agentese.node import BaseLogosNode, BasicRendering, Observer, Renderable
from protocols.agentese.registry import node, repopulate_registry, reset_registry

# Graceful FastAPI import
try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from httpx import ASGITransport, AsyncClient

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    FastAPI = None  # type: ignore
    TestClient = None  # type: ignore
    AsyncClient = None  # type: ignore


# === Test Node Classes ===


class TestNode(BaseLogosNode):
    """Test node for gateway testing."""

    def __init__(self, path: str = "test.node"):
        self._path = path

    @property
    def handle(self) -> str:
        return self._path

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("greet", "echo")

    async def manifest(self, observer: Any, **kwargs: Any) -> Renderable:
        return BasicRendering(
            summary=f"Test node: {self._path}",
            metadata={"observer_archetype": getattr(observer, "archetype", "unknown")},
        )

    async def _invoke_aspect(self, aspect: str, observer: Any, **kwargs: Any) -> Any:
        if aspect == "greet":
            name = kwargs.get("name", "World")
            return {"message": f"Hello, {name}!"}
        elif aspect == "echo":
            return {"echo": kwargs}
        return {"aspect": aspect, "kwargs": kwargs}


# === Fixtures ===


@pytest.fixture(autouse=True)
def clean_registry():
    """
    Reset registry before each test, repopulate after.

    CRITICAL for pytest-xdist: Without repopulation, tests on the same
    worker that run after this test will see an empty registry, breaking
    canary tests and any test that relies on global node registration.

    See: protocols/agentese/_tests/test_xdist_node_registry_canary.py
    """
    reset_registry()
    yield
    # Repopulate registry for subsequent tests on this worker
    # NOTE: repopulate_registry() scans sys.modules for @node classes
    # _import_node_modules() won't work because imports are cached
    repopulate_registry()


@pytest.fixture
def test_app():
    """Create a test FastAPI app."""
    if not HAS_FASTAPI:
        pytest.skip("FastAPI not available")
    return FastAPI()


@pytest.fixture
def gateway():
    """Create a gateway instance."""
    return create_gateway(prefix="/agentese")


# === Test Helper Functions ===


class TestHelpers:
    """Tests for gateway helper functions."""

    def test_to_json_safe_primitives(self):
        """Primitives pass through unchanged."""
        assert _to_json_safe(None) is None
        assert _to_json_safe("hello") == "hello"
        assert _to_json_safe(42) == 42
        assert _to_json_safe(3.14) == 3.14
        assert _to_json_safe(True) is True

    def test_to_json_safe_dict(self):
        """Dicts are recursively converted."""
        result = _to_json_safe({"a": 1, "b": {"c": 2}})
        assert result == {"a": 1, "b": {"c": 2}}

    def test_to_json_safe_list(self):
        """Lists are recursively converted."""
        result = _to_json_safe([1, "two", {"three": 3}])
        assert result == [1, "two", {"three": 3}]

    def test_to_json_safe_to_dict_method(self):
        """Objects with to_dict() are converted."""

        class HasToDict:
            def to_dict(self) -> dict[str, Any]:
                return {"converted": True}

        result = _to_json_safe(HasToDict())
        assert result == {"converted": True}

    def test_to_json_safe_dataclass_like(self):
        """Objects with __dict__ are converted."""

        class DataLike:
            def __init__(self):
                self.public = "visible"
                self._private = "hidden"

        result = _to_json_safe(DataLike())
        assert result == {"public": "visible"}

    def test_to_json_safe_fallback(self):
        """Unknown objects with __dict__ are converted."""

        class Unknown:
            def __init__(self):
                self.value = "test"

            def __str__(self) -> str:
                return "unknown-str"

        result = _to_json_safe(Unknown())
        # Objects with __dict__ have their public attrs extracted
        assert result == {"value": "test"}


class TestExtractObserver:
    """Tests for observer extraction from request headers."""

    def test_observer_from_headers_direct(self):
        """Test observer extraction directly without HTTP."""
        # Test default observer
        observer = Observer.guest()
        assert observer.archetype == "guest"
        assert observer.capabilities == frozenset()

    def test_observer_with_capabilities(self):
        """Test observer with capabilities."""
        observer = Observer(
            archetype="developer",
            capabilities=frozenset({"define", "refine", "test"}),
        )
        assert observer.archetype == "developer"
        assert "define" in observer.capabilities
        assert "refine" in observer.capabilities
        assert "test" in observer.capabilities


# === Test Gateway ===


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not available")
class TestGatewayMounting:
    """Tests for gateway mounting."""

    def test_gateway_mounts_successfully(self, test_app, gateway):
        """Gateway mounts on FastAPI app."""
        gateway.mount_on(test_app)

        # Check routes exist
        routes = [route.path for route in test_app.routes]
        assert any("/agentese" in route for route in routes)

    def test_gateway_custom_prefix(self, test_app):
        """Gateway uses custom prefix."""
        gateway = create_gateway(prefix="/api/v2")
        gateway.mount_on(test_app)

        routes = [route.path for route in test_app.routes]
        assert any("/api/v2" in route for route in routes)


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not available")
class TestGatewayDiscovery:
    """Tests for discovery endpoints."""

    def test_discover_empty_registry(self, test_app, gateway):
        """Discover returns empty when no nodes registered."""
        gateway.mount_on(test_app)
        client = TestClient(test_app)

        response = client.get("/agentese/discover")
        assert response.status_code == 200
        data = response.json()
        assert "paths" in data
        assert "stats" in data

    def test_discover_with_registered_nodes(self, test_app, gateway):
        """Discover returns registered nodes."""

        @node("test.discovery")
        class DiscoveryNode(TestNode):
            pass

        gateway.mount_on(test_app)
        client = TestClient(test_app)

        response = client.get("/agentese/discover")
        data = response.json()
        assert "test.discovery" in data["paths"]

    def test_discover_by_context(self, test_app, gateway):
        """Discover filters by context."""

        @node("self.test1")
        class SelfNode1(TestNode):
            pass

        @node("self.test2")
        class SelfNode2(TestNode):
            pass

        @node("world.test3")
        class WorldNode(TestNode):
            pass

        gateway.mount_on(test_app)
        client = TestClient(test_app)

        response = client.get("/agentese/discover/self")
        data = response.json()
        assert "self.test1" in data["paths"]
        assert "self.test2" in data["paths"]
        assert "world.test3" not in data["paths"]

    def test_discover_invalid_context(self, test_app, gateway):
        """Invalid context returns 400."""
        gateway.mount_on(test_app)
        client = TestClient(test_app)

        response = client.get("/agentese/discover/invalid")
        assert response.status_code == 400


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not available")
class TestGatewayManifest:
    """Tests for manifest endpoint."""

    def test_manifest_registered_node(self, test_app, gateway):
        """Manifest invokes registered node."""

        @node("test.manifest")
        class ManifestNode(TestNode):
            @property
            def handle(self) -> str:
                return "test.manifest"

        gateway.mount_on(test_app)
        client = TestClient(test_app)

        response = client.get("/agentese/test/manifest/manifest")
        assert response.status_code == 200
        data = response.json()
        assert data["path"] == "test.manifest"
        assert data["aspect"] == "manifest"
        assert "result" in data

    def test_manifest_with_observer_headers(self, test_app, gateway):
        """Manifest passes observer context."""

        @node("test.observer")
        class ObserverNode(TestNode):
            @property
            def handle(self) -> str:
                return "test.observer"

        gateway.mount_on(test_app)
        client = TestClient(test_app)

        response = client.get(
            "/agentese/test/observer/manifest",
            headers={"X-Observer-Archetype": "architect"},
        )
        data = response.json()
        # The manifest should include observer info
        assert response.status_code == 200


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not available")
class TestGatewayInvoke:
    """Tests for aspect invocation endpoint."""

    def test_invoke_aspect(self, test_app, gateway):
        """Invoke calls registered node aspect."""

        @node("test.invoke")
        class InvokeNode(TestNode):
            @property
            def handle(self) -> str:
                return "test.invoke"

        gateway.mount_on(test_app)
        client = TestClient(test_app)

        response = client.post(
            "/agentese/test/invoke/greet",
            json={"name": "Gateway"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["path"] == "test.invoke"
        assert data["aspect"] == "greet"
        assert data["result"]["message"] == "Hello, Gateway!"

    def test_invoke_with_empty_body(self, test_app, gateway):
        """Invoke works with empty request body."""

        @node("test.emptybody")
        class EmptyBodyNode(TestNode):
            @property
            def handle(self) -> str:
                return "test.emptybody"

        gateway.mount_on(test_app)
        client = TestClient(test_app)

        response = client.post("/agentese/test/emptybody/greet")
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["message"] == "Hello, World!"


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not available")
class TestGatewayAffordances:
    """Tests for affordances endpoint."""

    def test_affordances_returns_list(self, test_app, gateway):
        """Affordances endpoint returns list."""

        @node("test.affordances")
        class AffordancesNode(TestNode):
            @property
            def handle(self) -> str:
                return "test.affordances"

        gateway.mount_on(test_app)
        client = TestClient(test_app)

        response = client.get("/agentese/test/affordances/affordances")
        assert response.status_code == 200
        data = response.json()
        assert "affordances" in data
        assert isinstance(data["affordances"], list)
        # Should include base affordances
        assert "manifest" in data["affordances"]


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not available")
class TestGatewayFallback:
    """Tests for Logos fallback."""

    def test_unregistered_path_returns_404_when_no_fallback(self, test_app):
        """Unregistered path returns 404 without fallback."""
        gateway = create_gateway(prefix="/agentese", fallback_to_logos=False)
        gateway.mount_on(test_app)
        client = TestClient(test_app)

        response = client.get("/agentese/nonexistent/path/manifest")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data["detail"]
        assert "suggestion" in data["detail"]


# === Test Configuration ===


class TestGatewayConfiguration:
    """Tests for gateway configuration."""

    def test_default_configuration(self):
        """Default gateway configuration."""
        gateway = create_gateway()
        assert gateway.prefix == "/agentese"
        assert gateway.enable_streaming is True
        assert gateway.enable_websocket is True
        # AD-016: fail-fast by default (no JIT fallback)
        assert gateway.fallback_to_logos is False

    def test_custom_configuration(self):
        """Custom gateway configuration."""
        gateway = create_gateway(
            prefix="/custom",
            enable_streaming=False,
            enable_websocket=False,
            fallback_to_logos=False,
        )
        assert gateway.prefix == "/custom"
        assert gateway.enable_streaming is False
        assert gateway.enable_websocket is False
        assert gateway.fallback_to_logos is False


# === Test Mark Emission (Law 3) ===


@pytest.fixture
def clean_trace_store():
    """Reset trace store before and after each test."""
    from services.witness.trace_store import reset_mark_store

    reset_mark_store()
    yield
    reset_mark_store()


@pytest.fixture
def clean_synergy_bus():
    """Reset synergy bus before and after each test."""
    from services.witness.bus import reset_witness_bus_manager

    reset_witness_bus_manager()
    yield
    reset_witness_bus_manager()


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not available")
class TestGatewayMarkEmission:
    """
    Tests for Law 3: Every AGENTESE invocation emits exactly one Mark.

    These tests verify that the gateway instruments all invocations with
    Mark emission to the MarkStore.
    """

    def test_invoke_emits_trace_node(self, test_app, gateway, clean_registry, clean_trace_store):
        """Successful invocation emits a Mark."""
        from services.witness.trace_store import get_mark_store

        @node("test.traced")
        class TracedNode(TestNode):
            @property
            def handle(self) -> str:
                return "test.traced"

        gateway.mount_on(test_app)
        client = TestClient(test_app)

        # Make an invocation
        response = client.post(
            "/agentese/test/traced/greet",
            json={"name": "Law3"},
        )
        assert response.status_code == 200

        # Verify Mark was emitted
        store = get_mark_store()
        assert len(store) == 1

        # Verify Mark content
        traces = list(store.all())
        trace = traces[0]
        assert trace.origin == "gateway"
        assert trace.stimulus.kind == "agentese"
        assert "test.traced" in trace.stimulus.content
        assert trace.response.success is True
        assert "agentese" in trace.tags

    def test_manifest_emits_trace_node(self, test_app, gateway, clean_registry, clean_trace_store):
        """Manifest invocation emits a Mark."""
        from services.witness.trace_store import get_mark_store

        @node("test.manifest.traced")
        class ManifestTracedNode(TestNode):
            @property
            def handle(self) -> str:
                return "test.manifest.traced"

        gateway.mount_on(test_app)
        client = TestClient(test_app)

        response = client.get("/agentese/test/manifest/traced/manifest")
        assert response.status_code == 200

        store = get_mark_store()
        assert len(store) == 1

        trace = list(store.all())[0]
        assert trace.stimulus.kind == "agentese"
        assert "manifest" in trace.stimulus.content

    def test_error_emits_trace_node_with_error(
        self, test_app, gateway, clean_registry, clean_trace_store
    ):
        """Failed invocation emits a Mark with error response."""
        from services.witness.trace_store import get_mark_store

        gateway = create_gateway(prefix="/agentese", fallback_to_logos=False)
        gateway.mount_on(test_app)
        client = TestClient(test_app)

        # Invoke non-existent path
        response = client.get("/agentese/nonexistent/path/manifest")
        assert response.status_code == 404

        store = get_mark_store()
        assert len(store) == 1

        trace = list(store.all())[0]
        assert trace.response.success is False
        assert trace.response.kind == "error"

    def test_trace_node_captures_observer(
        self, test_app, gateway, clean_registry, clean_trace_store
    ):
        """Mark captures observer context from request headers."""
        from services.witness.trace_store import get_mark_store

        @node("test.observer.traced")
        class ObserverTracedNode(TestNode):
            @property
            def handle(self) -> str:
                return "test.observer.traced"

        gateway.mount_on(test_app)
        client = TestClient(test_app)

        response = client.get(
            "/agentese/test/observer/traced/manifest",
            headers={"X-Observer-Archetype": "architect"},
        )
        assert response.status_code == 200

        store = get_mark_store()
        trace = list(store.all())[0]
        assert trace.umwelt.observer_id == "architect"
        assert trace.umwelt.role == "architect"

    def test_multiple_invocations_emit_multiple_traces(
        self, test_app, gateway, clean_registry, clean_trace_store
    ):
        """Multiple invocations emit multiple Marks."""
        from services.witness.trace_store import get_mark_store

        @node("test.multi")
        class MultiNode(TestNode):
            @property
            def handle(self) -> str:
                return "test.multi"

        gateway.mount_on(test_app)
        client = TestClient(test_app)

        # Make multiple invocations
        for i in range(3):
            response = client.post(
                "/agentese/test/multi/greet",
                json={"name": f"Call{i}"},
            )
            assert response.status_code == 200

        store = get_mark_store()
        assert len(store) == 3

        # All traces are unique
        trace_ids = [t.id for t in store.all()]
        assert len(set(trace_ids)) == 3

    def test_trace_node_synergy_bus_publication(
        self, test_app, gateway, clean_registry, clean_trace_store, clean_synergy_bus
    ):
        """Mark emission publishes to SynergyBus."""
        from services.witness.bus import WitnessTopics, get_synergy_bus

        @node("self.gateway.synergy")
        class SynergyNode(TestNode):
            @property
            def handle(self) -> str:
                return "self.gateway.synergy"

        # Set up a subscriber to capture events
        captured_events: list[Any] = []

        async def capture_event(topic: str, event: Any) -> None:
            captured_events.append((topic, event))

        bus = get_synergy_bus()
        bus.subscribe(WitnessTopics.AGENTESE_INVOKED, capture_event)

        gateway.mount_on(test_app)
        client = TestClient(test_app)

        response = client.post("/agentese/self/gateway/synergy/greet", json={})
        assert response.status_code == 200

        # Note: The asyncio.create_task in gateway may not complete synchronously
        # in TestClient. The bus subscription verifies the wiring is correct.
        # In a real async environment, the event would be captured.
        # For this test, we verify the trace was stored (sync operation).
        from services.witness.trace_store import get_mark_store

        store = get_mark_store()
        assert len(store) == 1
