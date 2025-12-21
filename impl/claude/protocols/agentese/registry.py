"""
AGENTESE Node Registry.

Provides `@node` decorator for registering service nodes with AGENTESE paths.

The Metaphysical Fullstack Pattern (AD-009):
- Services register their nodes via @node("path")
- Logos queries the registry before falling back to context resolvers
- The protocol IS the API - no explicit routes needed

Example:
    @node("self.memory")
    class BrainNode(BaseLogosNode):
        '''Brain service AGENTESE node.'''

        def __init__(self, crystal: BrainCrystal):
            self._crystal = crystal

        @property
        def handle(self) -> str:
            return "self.memory"

        async def capture(self, observer: Observer, content: str) -> CaptureResult:
            return await self._crystal.capture(content)

Usage:
    from protocols.agentese.registry import node, get_registry

    # Register nodes (happens at import time)
    @node("self.memory")
    class BrainNode(BaseLogosNode): ...

    # Query registry
    registry = get_registry()
    node_cls = registry.get("self.memory")  # Returns BrainNode class
    node = await registry.resolve("self.memory")  # Returns instantiated node
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from threading import Lock
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Mapping,
    TypeVar,
)

if TYPE_CHECKING:
    from .contract import ContractsDict
    from .node import BaseLogosNode, LogosNode

logger = logging.getLogger(__name__)

T = TypeVar("T")


# === Node Metadata ===


@dataclass(frozen=True)
class NodeExample:
    """
    A pre-seeded example invocation for a node.

    Examples show up as one-click buttons in the Habitat, enabling
    rapid exploration of node affordances without needing to know
    the exact arguments.

    Attributes:
        aspect: The aspect to invoke (e.g., "capture", "search")
        kwargs: Keyword arguments to pass to the aspect
        label: Display label for the button (defaults to "Try {aspect}")

    Teaching:
        gotcha: Examples are defined in @node decorator, not in node class.
                Pass examples=[(aspect, kwargs, label), ...] to @node().
                (Evidence: test_registry.py::test_node_examples)
    """

    aspect: str
    kwargs: Mapping[str, Any] = field(default_factory=dict)
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "aspect": self.aspect,
            "kwargs": dict(self.kwargs),
            "label": self.label or f"Try {self.aspect}",
        }


@dataclass(frozen=True)
class NodeMetadata:
    """
    Metadata attached to a node class by @node decorator.

    Attributes:
        path: AGENTESE path (e.g., "self.memory", "world.town")
        description: Human-readable description
        dependencies: Required dependencies for instantiation
        singleton: Whether to cache a single instance
        lazy: Whether to defer instantiation until first use
        contracts: Contract declarations for type-safe BE/FE sync (Phase 7)
        examples: Pre-seeded example invocations (Habitat 2.0)

    Teaching:
        gotcha: Dependencies are resolved by ServiceContainer at instantiation.
                If a dependency isn't registered, the node SILENTLY SKIPS!
                Always verify deps exist in providers.py.
                (Evidence: test_registry.py::test_missing_dependency)
    """

    path: str
    description: str = ""
    dependencies: tuple[str, ...] = ()
    singleton: bool = True  # Default: cache single instance
    lazy: bool = True  # Default: defer instantiation
    contracts: "ContractsDict | None" = None  # Phase 7: Contract declarations
    examples: tuple[NodeExample, ...] = ()  # Habitat 2.0: Example invocations


# Marker attribute name for registered nodes
NODE_MARKER = "__node_meta__"


# === @node Decorator ===


def node(
    path: str,
    *,
    description: str = "",
    dependencies: tuple[str, ...] = (),
    singleton: bool = True,
    lazy: bool = True,
    contracts: "ContractsDict | None" = None,
    examples: list[tuple[str, dict[str, Any]] | tuple[str, dict[str, Any], str] | NodeExample]
    | None = None,
) -> Callable[[type[T]], type[T]]:
    """
    Decorator to register a LogosNode class with the AGENTESE registry.

    The decorated class will be automatically discoverable via the
    NodeRegistry, enabling the universal gateway pattern.

    Args:
        path: AGENTESE path (e.g., "self.memory", "world.town")
        description: Human-readable description (default: from docstring)
        dependencies: Dependency names for DI container
        singleton: Cache single instance (default: True)
        lazy: Defer instantiation until first use (default: True)
        contracts: Contract declarations for type-safe BE/FE sync (Phase 7)
            Use Contract(), Response(), Request() from protocols.agentese.contract
        examples: Pre-seeded examples for Habitat (Habitat 2.0)
            Can be NodeExample objects or tuples:
            - (aspect, kwargs) - aspect name and arguments
            - (aspect, kwargs, label) - with custom label

    Returns:
        Decorated class with node metadata

    Example:
        from protocols.agentese.contract import Contract, Response

        @node(
            "self.memory",
            dependencies=("brain_crystal",),
            contracts={
                "manifest": Response(BrainManifestResponse),
                "capture": Contract(CaptureRequest, CaptureResponse),
            },
            examples=[
                ("search", {"query": "Python tips", "limit": 5}, "Search for Python"),
                ("recent", {"limit": 10}, "Show recent memories"),
            ]
        )
        class BrainNode(BaseLogosNode):
            '''Holographic Brain AGENTESE node.'''

            def __init__(self, crystal: BrainCrystal):
                self._crystal = crystal

            @property
            def handle(self) -> str:
                return "self.memory"

            @aspect(category=AspectCategory.MUTATION, effects=[Effect.WRITES("crystals")])
            async def capture(self, observer: Observer, content: str) -> CaptureResult:
                return await self._crystal.capture(content)

    Note:
        - The path should match the node's `handle` property
        - Dependencies are resolved by ServiceContainer at instantiation
        - Singleton nodes are cached after first instantiation
        - Contracts enable FE type generation via /discover?include_schemas=true
        - Examples appear as one-click buttons in Concept Home
    """

    def decorator(cls: type[T]) -> type[T]:
        """Apply @node metadata to class and register with global registry."""
        # Get description from docstring if not provided
        desc = description or (cls.__doc__ or "").split("\n")[0].strip()

        # Parse examples into NodeExample objects
        parsed_examples: tuple[NodeExample, ...] = ()
        if examples:
            example_list: list[NodeExample] = []
            for ex in examples:
                if isinstance(ex, NodeExample):
                    example_list.append(ex)
                elif isinstance(ex, tuple):
                    if len(ex) == 2:
                        aspect, kwargs = ex
                        example_list.append(NodeExample(aspect=aspect, kwargs=kwargs))
                    elif len(ex) == 3:
                        aspect, kwargs, label = ex
                        example_list.append(NodeExample(aspect=aspect, kwargs=kwargs, label=label))
                    else:
                        logger.warning(f"Invalid example format for {path}: {ex}")
            parsed_examples = tuple(example_list)

        # Create metadata
        meta = NodeMetadata(
            path=path,
            description=desc,
            dependencies=dependencies,
            singleton=singleton,
            lazy=lazy,
            contracts=contracts,
            examples=parsed_examples,
        )

        # Attach metadata to class
        setattr(cls, NODE_MARKER, meta)

        # Auto-register with global registry
        _get_registry()._register_class(path, cls, meta)

        # Register contracts if provided (Phase 7)
        if contracts is not None:
            try:
                from .contract import get_contract_registry

                get_contract_registry().register(path, contracts)
            except ImportError:
                logger.debug("Contract registry not available")

        logger.debug(f"Registered AGENTESE node: {path} -> {cls.__name__}")

        return cls

    return decorator


def is_node(cls: type[Any]) -> bool:
    """Check if a class is decorated with @node."""
    return hasattr(cls, NODE_MARKER)


def get_node_metadata(cls: type[Any]) -> NodeMetadata | None:
    """Get node metadata from a decorated class."""
    return getattr(cls, NODE_MARKER, None)


# === Node Registry ===


@dataclass
class NodeRegistry:
    """
    Central registry for AGENTESE nodes.

    The registry is the SINGLE SOURCE OF TRUTH for AGENTESE paths.
    If a path is not registered here via @node, it does not exist.

    The registry:
    1. Stores @node decorated classes mapped by path
    2. Provides path resolution for Logos
    3. Manages singleton instances
    4. Supports dependency injection via ServiceContainer

    Thread-safe for concurrent access.

    Example:
        registry = get_registry()

        # Check if path is registered
        if registry.has("self.memory"):
            node_cls = registry.get("self.memory")

        # Resolve with DI container
        node = await registry.resolve("self.memory", container)

        # List all registered paths
        paths = registry.list_paths()

    Teaching:
        gotcha: @node decorator runs at import time. If a module isn't imported,
                its node won't be registered. Call _import_node_modules() first
                (done automatically by gateway.mount_on()).
                (Evidence: test_registry.py::test_node_import_order)

        gotcha: After reset_registry() in tests, call repopulate_registry()
                to restore nodes for subsequent tests on the same xdist worker.
                (Evidence: test_registry.py::test_registry_reset)
    """

    # Path -> node class
    _nodes: dict[str, type[Any]] = field(default_factory=dict)

    # Path -> node metadata
    _metadata: dict[str, NodeMetadata] = field(default_factory=dict)

    # Path -> singleton instance (if applicable)
    _instances: dict[str, Any] = field(default_factory=dict)

    # Thread lock for concurrent access
    _lock: Lock = field(default_factory=Lock)

    def _register_class(
        self,
        path: str,
        cls: type[Any],
        meta: NodeMetadata,
    ) -> None:
        """
        Register a node class (internal, called by @node decorator).

        Args:
            path: AGENTESE path
            cls: Node class
            meta: Node metadata
        """
        with self._lock:
            if path in self._nodes:
                existing = self._nodes[path]
                logger.warning(
                    f"Overwriting AGENTESE node {path}: {existing.__name__} -> {cls.__name__}"
                )
            self._nodes[path] = cls
            self._metadata[path] = meta

    def has(self, path: str) -> bool:
        """Check if a path is registered."""
        with self._lock:
            return path in self._nodes

    def get(self, path: str) -> type[Any] | None:
        """
        Get the node class for a path.

        Args:
            path: AGENTESE path

        Returns:
            Node class or None if not registered
        """
        with self._lock:
            return self._nodes.get(path)

    def get_metadata(self, path: str) -> NodeMetadata | None:
        """Get metadata for a path."""
        with self._lock:
            return self._metadata.get(path)

    async def resolve(
        self,
        path: str,
        container: Any | None = None,
    ) -> "LogosNode | None":
        """
        Resolve a path to an instantiated node.

        If the node is a singleton and already instantiated, returns cached instance.
        Otherwise, creates a new instance using the DI container.

        Args:
            path: AGENTESE path
            container: Optional ServiceContainer for dependency injection

        Returns:
            Instantiated node or None if not registered
        """
        with self._lock:
            # Check for cached singleton
            if path in self._instances:
                cached: LogosNode | None = self._instances[path]
                return cached

            # Get class
            cls = self._nodes.get(path)
            if cls is None:
                return None

            meta = self._metadata.get(path)

        # Instantiate outside lock to avoid deadlock
        if container is not None:
            # Use container for DI
            instance = await container.create_node(cls, meta)
        else:
            # Try to instantiate without dependencies
            try:
                instance = cls()
            except TypeError as e:
                logger.error(f"Cannot instantiate {cls.__name__} without container: {e}")
                return None

        # Cache singleton
        if meta and meta.singleton:
            with self._lock:
                self._instances[path] = instance

        result: LogosNode = instance
        return result

    def list_paths(self) -> list[str]:
        """List all registered paths."""
        with self._lock:
            return list(self._nodes.keys())

    def list_by_context(self, context: str) -> list[str]:
        """
        List paths for a specific context.

        Args:
            context: AGENTESE context (world, self, concept, void, time)

        Returns:
            Paths starting with the context
        """
        with self._lock:
            prefix = f"{context}."
            return [p for p in self._nodes.keys() if p.startswith(prefix)]

    def clear(self) -> None:
        """Clear all registrations (for testing)."""
        with self._lock:
            self._nodes.clear()
            self._metadata.clear()
            self._instances.clear()

    def clear_instances(self) -> None:
        """Clear cached instances but keep registrations."""
        with self._lock:
            self._instances.clear()

    def stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        with self._lock:
            paths_with_contracts = sum(
                1 for meta in self._metadata.values() if meta.contracts is not None
            )
            return {
                "registered_nodes": len(self._nodes),
                "cached_instances": len(self._instances),
                "paths": list(self._nodes.keys()),
                "contexts": list(set(p.split(".")[0] for p in self._nodes.keys() if "." in p)),
                "paths_with_contracts": paths_with_contracts,
            }

    def get_contracts(self, path: str) -> "ContractsDict | None":
        """
        Get contracts for a path.

        Args:
            path: AGENTESE path

        Returns:
            Contracts dict or None if no contracts defined
        """
        meta = self.get_metadata(path)
        if meta is None:
            return None
        return meta.contracts

    def list_paths_with_contracts(self) -> list[str]:
        """List all paths that have contract declarations."""
        with self._lock:
            return [path for path, meta in self._metadata.items() if meta.contracts is not None]

    def get_all_contracts(self) -> dict[str, "ContractsDict"]:
        """
        Get all contracts for all paths.

        Returns:
            Dictionary of path -> contracts dict (only paths with contracts)
        """
        with self._lock:
            return {
                path: meta.contracts
                for path, meta in self._metadata.items()
                if meta.contracts is not None
            }


# === Global Registry Singleton ===

_registry: NodeRegistry | None = None
_registry_lock = Lock()


def _get_registry() -> NodeRegistry:
    """Get the global registry singleton (internal)."""
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = NodeRegistry()
    return _registry


def get_registry() -> NodeRegistry:
    """
    Get the global node registry.

    Returns:
        The singleton NodeRegistry instance

    Example:
        registry = get_registry()
        if registry.has("self.memory"):
            node = await registry.resolve("self.memory")
    """
    return _get_registry()


def reset_registry() -> None:
    """
    Reset the global registry (for testing).

    Clears all registrations and cached instances.

    WARNING: After calling this, the registry will be EMPTY!
    Call repopulate_registry() to re-register all @node decorated classes.

    In pytest-xdist, tests on the same worker share Python state.
    If you reset the registry and don't repopulate it, subsequent tests
    that rely on node registration will FAIL.

    Recommended pattern for autouse fixtures:
        @pytest.fixture(autouse=True)
        def clean_registry():
            reset_registry()
            yield
            repopulate_registry()  # CRITICAL for xdist!
    """
    global _registry
    with _registry_lock:
        if _registry is not None:
            _registry.clear()
        _registry = None


def repopulate_registry() -> None:
    """
    Re-register all @node decorated classes found in sys.modules.

    This scans all loaded Python modules for classes that have the
    NODE_MARKER attribute (set by @node decorator) and re-registers
    them with the global registry.

    Use this after reset_registry() in test fixtures to restore
    the registry state for subsequent tests on the same worker.

    Example:
        @pytest.fixture(autouse=True)
        def clean_registry():
            reset_registry()
            yield
            repopulate_registry()  # Re-register all nodes
    """
    import sys

    registry = _get_registry()
    registered_count = 0

    # Modules to skip during scan (to avoid deprecation warnings)
    # - typing.io deprecated in Python 3.12+, triggers warning on getattr
    # - starlette.status deprecated HTTP constants (HTTP_413_REQUEST_ENTITY_TOO_LARGE etc.)
    skip_prefixes = ("typing.", "starlette.")
    skip_exact = {"typing", "starlette.status"}

    # Scan all loaded modules
    for module in list(sys.modules.values()):
        if module is None:
            continue

        # Skip modules that trigger deprecation warnings
        module_name = getattr(module, "__name__", "")
        if module_name in skip_exact or any(module_name.startswith(p) for p in skip_prefixes):
            continue

        # Check all attributes in the module
        try:
            for name in dir(module):
                try:
                    obj = getattr(module, name)
                    # Check if it's a class with NODE_MARKER
                    if isinstance(obj, type) and hasattr(obj, NODE_MARKER):
                        meta = getattr(obj, NODE_MARKER)
                        if isinstance(meta, NodeMetadata):
                            registry._register_class(meta.path, obj, meta)
                            registered_count += 1
                except Exception:
                    # Some attributes may not be accessible
                    continue
        except Exception:
            # Some modules may not support dir()
            continue

    logger.debug(f"Repopulated NodeRegistry with {registered_count} nodes")


# === Exports ===

__all__ = [
    # Decorator
    "node",
    "is_node",
    "get_node_metadata",
    # Metadata
    "NodeMetadata",
    "NodeExample",
    "NODE_MARKER",
    # Registry
    "NodeRegistry",
    "get_registry",
    "reset_registry",
    "repopulate_registry",
]
