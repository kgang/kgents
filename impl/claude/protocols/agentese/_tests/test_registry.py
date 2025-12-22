"""
Tests for AGENTESE Node Registry.

Verifies @node decorator and NodeRegistry functionality.
"""

from __future__ import annotations

from typing import Any

import pytest

from protocols.agentese.node import BaseLogosNode, BasicRendering, Observer, Renderable
from protocols.agentese.registry import (
    NODE_MARKER,
    NodeExample,
    NodeMetadata,
    NodeRegistry,
    get_node_metadata,
    get_registry,
    is_node,
    node,
    repopulate_registry,
    reset_registry,
)

# === Test Node Classes ===


class MockRenderable:
    """Mock renderable for testing."""

    def to_dict(self) -> dict[str, Any]:
        return {"type": "mock"}

    def to_text(self) -> str:
        return "mock"


class SimpleNode(BaseLogosNode):
    """A simple test node without dependencies."""

    @property
    def handle(self) -> str:
        return "test.simple"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("test",)

    async def manifest(self, observer: Any) -> Renderable:
        return BasicRendering(summary="Simple node")

    async def _invoke_aspect(self, aspect: str, observer: Any, **kwargs: Any) -> Any:
        return {"aspect": aspect, "kwargs": kwargs}


class DependentNode(BaseLogosNode):
    """A node with dependencies."""

    def __init__(self, service: Any, config: dict[str, Any] | None = None):
        self._service = service
        self._config = config or {}

    @property
    def handle(self) -> str:
        return "test.dependent"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("capture", "search")

    async def manifest(self, observer: Any) -> Renderable:
        return BasicRendering(summary="Dependent node")

    async def _invoke_aspect(self, aspect: str, observer: Any, **kwargs: Any) -> Any:
        return {"service": self._service, "aspect": aspect}


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


# === Test @node Decorator ===


class TestNodeDecorator:
    """Tests for @node decorator."""

    def test_basic_decoration(self):
        """@node attaches metadata to class."""

        @node("test.basic")
        class TestNode(SimpleNode):
            pass

        assert is_node(TestNode)
        meta = get_node_metadata(TestNode)
        assert meta is not None
        assert meta.path == "test.basic"

    def test_decorator_with_options(self):
        """@node accepts configuration options."""

        @node(
            "test.configured",
            description="A configured node",
            dependencies=("service_a", "service_b"),
            singleton=False,
            lazy=False,
        )
        class ConfiguredNode(SimpleNode):
            # IMPORTANT: __init__ params MUST match declared dependencies
            # (fail-fast validation at import time)
            def __init__(self, service_a: Any = None, service_b: Any = None):
                self._a = service_a
                self._b = service_b

        meta = get_node_metadata(ConfiguredNode)
        assert meta is not None
        assert meta.path == "test.configured"
        assert meta.description == "A configured node"
        assert meta.dependencies == ("service_a", "service_b")
        assert meta.singleton is False
        assert meta.lazy is False

    def test_description_from_docstring(self):
        """@node uses class docstring as default description."""

        @node("test.docstring")
        class DocstringNode(SimpleNode):
            """This is the docstring description."""

            pass

        meta = get_node_metadata(DocstringNode)
        assert meta is not None
        assert meta.description == "This is the docstring description."

    def test_auto_registration(self):
        """@node auto-registers with global registry."""

        @node("test.autoregistered")
        class AutoNode(SimpleNode):
            pass

        registry = get_registry()
        assert registry.has("test.autoregistered")
        assert registry.get("test.autoregistered") is AutoNode

    def test_multiple_nodes(self):
        """Multiple nodes can be registered."""

        @node("test.node1")
        class Node1(SimpleNode):
            @property
            def handle(self) -> str:
                return "test.node1"

        @node("test.node2")
        class Node2(SimpleNode):
            @property
            def handle(self) -> str:
                return "test.node2"

        registry = get_registry()
        assert registry.has("test.node1")
        assert registry.has("test.node2")
        assert registry.get("test.node1") is Node1
        assert registry.get("test.node2") is Node2

    def test_dependency_mismatch_fails_fast(self):
        """@node validates dependencies at import time (FAIL-FAST).

        This catches the common error where @node(dependencies=("foo",))
        is declared but the class __init__ has a different parameter name.

        Evidence: This test catches errors at decorator time, not at runtime
        invocation. Much better DX.
        """
        with pytest.raises(TypeError) as exc_info:

            @node(
                "test.mismatch",
                dependencies=("wrong_name",),
            )
            class MismatchedNode(SimpleNode):
                # __init__ has 'actual_name' but dependencies declares 'wrong_name'
                def __init__(self, actual_name: Any = None):
                    self._actual = actual_name

        error_msg = str(exc_info.value)
        assert "wrong_name" in error_msg
        assert "MismatchedNode" in error_msg
        assert "actual_name" in error_msg  # Shows available params


# === Test NodeRegistry ===


class TestNodeRegistry:
    """Tests for NodeRegistry."""

    def test_has_unregistered_path(self):
        """has() returns False for unregistered paths."""
        registry = get_registry()
        assert registry.has("nonexistent.path") is False

    def test_get_unregistered_path(self):
        """get() returns None for unregistered paths."""
        registry = get_registry()
        assert registry.get("nonexistent.path") is None

    def test_list_paths(self):
        """list_paths() returns all registered paths."""

        @node("test.path1")
        class Node1(SimpleNode):
            pass

        @node("test.path2")
        class Node2(SimpleNode):
            pass

        registry = get_registry()
        paths = registry.list_paths()
        assert "test.path1" in paths
        assert "test.path2" in paths

    def test_list_by_context(self):
        """list_by_context() filters by context prefix."""

        @node("self.memory")
        class MemoryNode(SimpleNode):
            pass

        @node("self.soul")
        class SoulNode(SimpleNode):
            pass

        @node("world.town")
        class TownNode(SimpleNode):
            pass

        registry = get_registry()

        self_paths = registry.list_by_context("self")
        assert "self.memory" in self_paths
        assert "self.soul" in self_paths
        assert "world.town" not in self_paths

        world_paths = registry.list_by_context("world")
        assert "world.town" in world_paths
        assert "self.memory" not in world_paths

    def test_stats(self):
        """stats() returns registry statistics."""

        @node("test.stats")
        class StatsNode(SimpleNode):
            pass

        registry = get_registry()
        stats = registry.stats()

        assert stats["registered_nodes"] >= 1
        assert "test.stats" in stats["paths"]
        assert "test" in stats["contexts"]

    def test_clear(self):
        """clear() removes all registrations."""

        @node("test.toclear")
        class ToClearNode(SimpleNode):
            pass

        registry = get_registry()
        assert registry.has("test.toclear")

        registry.clear()
        assert not registry.has("test.toclear")

    @pytest.mark.asyncio
    async def test_resolve_simple_node(self):
        """resolve() instantiates a simple node."""

        @node("test.resolve")
        class ResolveNode(SimpleNode):
            @property
            def handle(self) -> str:
                return "test.resolve"

        registry = get_registry()
        instance = await registry.resolve("test.resolve")

        assert instance is not None
        assert instance.handle == "test.resolve"

    @pytest.mark.asyncio
    async def test_resolve_singleton_caching(self):
        """Singleton nodes are cached after first resolve."""

        @node("test.singleton", singleton=True)
        class SingletonNode(SimpleNode):
            pass

        registry = get_registry()
        instance1 = await registry.resolve("test.singleton")
        instance2 = await registry.resolve("test.singleton")

        assert instance1 is instance2

    @pytest.mark.asyncio
    async def test_resolve_non_singleton(self):
        """Non-singleton nodes create new instances."""

        @node("test.nonsingleton", singleton=False)
        class NonSingletonNode(SimpleNode):
            pass

        registry = get_registry()
        instance1 = await registry.resolve("test.nonsingleton")
        instance2 = await registry.resolve("test.nonsingleton")

        assert instance1 is not instance2

    @pytest.mark.asyncio
    async def test_resolve_unregistered(self):
        """resolve() returns None for unregistered paths."""
        registry = get_registry()
        result = await registry.resolve("nonexistent.path")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_dependent_node_fails_without_container(self):
        """Dependent nodes fail without container."""

        @node("test.needscontainer", dependencies=("service",))
        class NeedsContainerNode(DependentNode):
            pass

        registry = get_registry()
        # Should fail because DependentNode requires service argument
        result = await registry.resolve("test.needscontainer")
        assert result is None  # Cannot instantiate without container


# === Test Metadata ===


class TestNodeMetadata:
    """Tests for NodeMetadata."""

    def test_metadata_defaults(self):
        """NodeMetadata has sensible defaults."""
        meta = NodeMetadata(path="test.defaults")

        assert meta.path == "test.defaults"
        assert meta.description == ""
        assert meta.dependencies == ()
        assert meta.singleton is True
        assert meta.lazy is True

    def test_metadata_frozen(self):
        """NodeMetadata is immutable."""
        meta = NodeMetadata(path="test.frozen")

        with pytest.raises(Exception):  # FrozenInstanceError
            meta.path = "changed"  # type: ignore


# === Integration Tests ===


class TestRegistryIntegration:
    """Integration tests for registry with AGENTESE patterns."""

    @pytest.mark.asyncio
    async def test_node_invocation_through_registry(self):
        """Nodes resolved through registry can be invoked."""

        @node("test.invokable")
        class InvokableNode(SimpleNode):
            @property
            def handle(self) -> str:
                return "test.invokable"

            async def _invoke_aspect(self, aspect: str, observer: Any, **kwargs: Any) -> Any:
                if aspect == "greet":
                    return f"Hello, {kwargs.get('name', 'World')}!"
                return await super()._invoke_aspect(aspect, observer, **kwargs)

        registry = get_registry()
        instance = await registry.resolve("test.invokable")
        assert instance is not None

        observer = Observer.test()
        result = await instance.invoke("greet", observer, name="Test")
        assert result == "Hello, Test!"

    def test_path_hierarchy(self):
        """Registry supports hierarchical paths."""

        @node("self.memory")
        class MemoryRoot(SimpleNode):
            pass

        @node("self.memory.crystals")
        class MemoryCrystals(SimpleNode):
            pass

        @node("self.memory.crystals.recent")
        class RecentCrystals(SimpleNode):
            pass

        registry = get_registry()

        # All paths should be registered
        assert registry.has("self.memory")
        assert registry.has("self.memory.crystals")
        assert registry.has("self.memory.crystals.recent")

        # list_by_context should find all self.* paths
        self_paths = registry.list_by_context("self")
        assert len(self_paths) >= 3


# === Test Examples (Habitat 2.0) ===


class TestNodeExamples:
    """Tests for pre-seeded examples feature."""

    def test_node_example_creation(self):
        """NodeExample can be created and serialized."""
        example = NodeExample(
            aspect="search", kwargs={"query": "Python", "limit": 5}, label="Search Python"
        )

        assert example.aspect == "search"
        assert example.kwargs == {"query": "Python", "limit": 5}
        assert example.label == "Search Python"

        # Test to_dict serialization
        data = example.to_dict()
        assert data["aspect"] == "search"
        assert data["kwargs"] == {"query": "Python", "limit": 5}
        assert data["label"] == "Search Python"

    def test_node_example_default_label(self):
        """NodeExample generates default label if not provided."""
        example = NodeExample(aspect="capture", kwargs={"content": "test"})

        assert example.label == ""
        # Default label should be generated in to_dict
        data = example.to_dict()
        assert data["label"] == "Try capture"

    def test_node_with_tuple_examples(self):
        """@node accepts examples as tuples."""

        @node(
            "test.examples",
            examples=[
                ("search", {"query": "test"}),
                ("recent", {"limit": 10}, "Show recent"),
            ],
        )
        class ExamplesNode(SimpleNode):
            pass

        meta = get_node_metadata(ExamplesNode)
        assert meta is not None
        assert len(meta.examples) == 2

        # First example (2-tuple)
        ex1 = meta.examples[0]
        assert ex1.aspect == "search"
        assert ex1.kwargs == {"query": "test"}
        assert ex1.label == ""  # No label provided

        # Second example (3-tuple with label)
        ex2 = meta.examples[1]
        assert ex2.aspect == "recent"
        assert ex2.kwargs == {"limit": 10}
        assert ex2.label == "Show recent"

    def test_node_with_nodeexample_objects(self):
        """@node accepts NodeExample objects."""
        example1 = NodeExample(aspect="capture", kwargs={"content": "test"}, label="Capture")
        example2 = NodeExample(aspect="search", kwargs={"query": "Python"})

        @node("test.example_objects", examples=[example1, example2])
        class ExampleObjectsNode(SimpleNode):
            pass

        meta = get_node_metadata(ExampleObjectsNode)
        assert meta is not None
        assert len(meta.examples) == 2
        assert meta.examples[0].aspect == "capture"
        assert meta.examples[1].aspect == "search"

    def test_node_examples_empty_by_default(self):
        """Nodes without examples have empty tuple."""

        @node("test.noexamples")
        class NoExamplesNode(SimpleNode):
            pass

        meta = get_node_metadata(NoExamplesNode)
        assert meta is not None
        assert meta.examples == ()

    def test_node_examples_serialization(self):
        """Examples can be serialized for discovery endpoint."""

        @node(
            "test.serialization",
            examples=[
                ("search", {"query": "Python tips", "limit": 5}, "Search for Python"),
                ("recent", {"limit": 10}, "Show recent memories"),
            ],
        )
        class SerializationNode(SimpleNode):
            pass

        meta = get_node_metadata(SerializationNode)
        assert meta is not None

        # Serialize all examples
        serialized = [ex.to_dict() for ex in meta.examples]

        assert len(serialized) == 2
        assert serialized[0] == {
            "aspect": "search",
            "kwargs": {"query": "Python tips", "limit": 5},
            "label": "Search for Python",
        }
        assert serialized[1] == {
            "aspect": "recent",
            "kwargs": {"limit": 10},
            "label": "Show recent memories",
        }
