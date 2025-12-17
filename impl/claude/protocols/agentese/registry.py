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
    TypeVar,
)

if TYPE_CHECKING:
    from .node import BaseLogosNode, LogosNode

logger = logging.getLogger(__name__)

T = TypeVar("T")


# === Node Metadata ===


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
    """

    path: str
    description: str = ""
    dependencies: tuple[str, ...] = ()
    singleton: bool = True  # Default: cache single instance
    lazy: bool = True  # Default: defer instantiation


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

    Returns:
        Decorated class with node metadata

    Example:
        @node("self.memory", dependencies=("brain_crystal",))
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
    """

    def decorator(cls: type[T]) -> type[T]:
        # Get description from docstring if not provided
        desc = description or (cls.__doc__ or "").split("\n")[0].strip()

        # Create metadata
        meta = NodeMetadata(
            path=path,
            description=desc,
            dependencies=dependencies,
            singleton=singleton,
            lazy=lazy,
        )

        # Attach metadata to class
        setattr(cls, NODE_MARKER, meta)

        # Auto-register with global registry
        _get_registry()._register_class(path, cls, meta)

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
                logger.error(
                    f"Cannot instantiate {cls.__name__} without container: {e}"
                )
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
            return {
                "registered_nodes": len(self._nodes),
                "cached_instances": len(self._instances),
                "paths": list(self._nodes.keys()),
                "contexts": list(
                    set(p.split(".")[0] for p in self._nodes.keys() if "." in p)
                ),
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
    """
    global _registry
    with _registry_lock:
        if _registry is not None:
            _registry.clear()
        _registry = None


# === Exports ===

__all__ = [
    # Decorator
    "node",
    "is_node",
    "get_node_metadata",
    # Metadata
    "NodeMetadata",
    "NODE_MARKER",
    # Registry
    "NodeRegistry",
    "get_registry",
    "reset_registry",
]
