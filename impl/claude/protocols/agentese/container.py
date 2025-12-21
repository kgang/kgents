"""
AGENTESE Service Container.

Dependency injection container for AGENTESE service nodes.

The Metaphysical Fullstack Pattern (AD-009):
- Services declare dependencies via @node decorator
- Container resolves dependencies at instantiation time
- D-gent, TableAdapters, LLM clients are all injectable

Example:
    @node("self.memory", dependencies=("brain_crystal", "embedder"))
    class BrainNode(BaseLogosNode):
        def __init__(self, crystal: BrainCrystal, embedder: Embedder):
            self._crystal = crystal
            self._embedder = embedder

    # Register providers
    container = ServiceContainer()
    container.register("brain_crystal", get_brain_crystal)
    container.register("embedder", get_embedder)

    # Node gets dependencies injected
    node = await container.create_node(BrainNode, meta)

Teaching:
    gotcha: Dependencies are REQUIRED by default (no default in __init__).
            Missing required deps raise DependencyNotFoundError immediately.
            To make a dependency optional, add a default: `brain: Brain | None = None`
            (Evidence: test_container.py::TestNodeCreation::test_required_deps_fail_immediately)

    gotcha: Optional dependencies are skipped gracefully if not registered.
            The node's __init__ default is used. This is intentional for
            graceful degradation (e.g., SoulNode without LLM).
            (Evidence: test_container.py::TestNodeCreation::test_optional_deps_skipped_gracefully)

    gotcha: Singleton is the DEFAULT. Every register() call creates a cached singleton
            unless singleton=False is explicitly passed. This means provider functions
            are called ONCE and the result is reused forever.
            (Evidence: test_container.py::TestDependencyResolution::test_singleton_caching)

    gotcha: Dependency names are CASE-SENSITIVE and EXACT-MATCH. If your @node
            declares dependencies=("brain_Crystal",) but you register "brain_crystal",
            the dependency silently fails to resolve.
            (Evidence: test_container.py::TestProviderRegistration::test_has_unregistered)

AGENTESE: protocols.agentese.container
"""

from __future__ import annotations

import asyncio
import inspect
import logging
from collections.abc import Coroutine
from dataclasses import dataclass, field
from threading import Lock
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    TypeVar,
)

if TYPE_CHECKING:
    from .node import LogosNode
    from .registry import NodeMetadata

logger = logging.getLogger(__name__)

T = TypeVar("T")


# === Exceptions ===


class DependencyNotFoundError(Exception):
    """Raised when a required dependency is not registered in the container."""

    pass


# === Provider Types ===


Provider = Callable[[], Any] | Callable[[], Coroutine[Any, Any, Any]]
"""Provider is a callable that returns a dependency (sync or async)."""


@dataclass(frozen=True)
class ProviderEntry:
    """
    Entry in the provider registry.

    Attributes:
        name: Dependency name
        provider: Callable that provides the dependency
        singleton: Cache the provided value (default: True)
        lazy: Defer instantiation until first use (default: True)
    """

    name: str
    provider: Provider
    singleton: bool = True
    lazy: bool = True


# === Service Container ===


@dataclass
class ServiceContainer:
    """
    Dependency injection container for AGENTESE service nodes.

    The container:
    1. Stores provider registrations for dependencies
    2. Resolves dependencies by name
    3. Creates node instances with injected dependencies
    4. Caches singleton dependencies

    Thread-safe for concurrent access.

    Example:
        container = ServiceContainer()

        # Register providers
        container.register("brain_crystal", get_brain_crystal)
        container.register("embedder", get_embedder, singleton=True)

        # Create node with dependencies
        node = await container.create_node(BrainNode, meta)
    """

    # Name -> provider entry
    _providers: dict[str, ProviderEntry] = field(default_factory=dict)

    # Name -> cached singleton value
    _cache: dict[str, Any] = field(default_factory=dict)

    # Thread lock for concurrent access
    _lock: Lock = field(default_factory=Lock)

    def register(
        self,
        name: str,
        provider: Provider,
        *,
        singleton: bool = True,
        lazy: bool = True,
    ) -> None:
        """
        Register a dependency provider.

        Args:
            name: Dependency name (matches node dependency declarations)
            provider: Callable that returns the dependency
            singleton: Cache the provided value (default: True)
            lazy: Defer instantiation until first use (default: True)

        Example:
            container.register("brain_crystal", get_brain_crystal)
            container.register("embedder", lambda: create_embedder("all-MiniLM-L6-v2"))
        """
        with self._lock:
            entry = ProviderEntry(
                name=name,
                provider=provider,
                singleton=singleton,
                lazy=lazy,
            )
            self._providers[name] = entry
            logger.debug(f"Registered provider: {name}")

    def register_value(self, name: str, value: Any) -> None:
        """
        Register a pre-instantiated value as a singleton.

        Convenience method for registering existing instances.

        Args:
            name: Dependency name
            value: Pre-instantiated value

        Example:
            container.register_value("config", {"debug": True})
        """
        with self._lock:
            # Store directly in cache
            self._cache[name] = value
            # Register a provider that returns from cache
            entry = ProviderEntry(
                name=name,
                provider=lambda: value,
                singleton=True,
                lazy=False,  # Already instantiated
            )
            self._providers[name] = entry
            logger.debug(f"Registered value: {name}")

    def has(self, name: str) -> bool:
        """Check if a provider is registered."""
        with self._lock:
            return name in self._providers

    async def resolve(self, name: str) -> Any:
        """
        Resolve a dependency by name.

        Args:
            name: Dependency name

        Returns:
            Resolved dependency value

        Raises:
            KeyError: If no provider registered for name
        """
        with self._lock:
            # Check cache first
            if name in self._cache:
                return self._cache[name]

            # Get provider
            if name not in self._providers:
                raise KeyError(f"No provider registered for: {name}")
            entry = self._providers[name]

        # Resolve outside lock to avoid deadlock
        value = await self._call_provider(entry.provider)

        # Cache singleton
        if entry.singleton:
            with self._lock:
                self._cache[name] = value

        return value

    async def _call_provider(self, provider: Provider) -> Any:
        """Call a provider, handling sync and async."""
        result = provider()

        # If result is a coroutine, await it
        if asyncio.iscoroutine(result):
            return await result

        return result

    async def create_node(
        self,
        cls: type[T],
        meta: "NodeMetadata | None" = None,
    ) -> T:
        """
        Create a node instance with injected dependencies.

        Enlightened Resolution (2025-12-21):
        - Required deps (no default in __init__) → fail immediately if missing
        - Optional deps (has default in __init__) → skip gracefully if missing
        - Declared deps via @node(dependencies=(...)) → ALL treated as required

        Resolution order:
        1. Check meta.dependencies for declared dependencies (all required)
        2. If no declared deps, inspect __init__ signature for required/optional
        3. Resolve each dependency via registered providers
        4. Instantiate node with resolved dependencies

        Args:
            cls: Node class to instantiate
            meta: Optional node metadata with dependency declarations

        Returns:
            Instantiated node with dependencies

        Raises:
            DependencyNotFoundError: If a required dependency is not registered

        Example:
            node = await container.create_node(BrainNode, meta)
        """
        # Determine dependencies
        required_deps: tuple[str, ...]
        optional_deps: tuple[str, ...]

        if meta and meta.dependencies:
            # Declared deps are ALL required (per decision in plan)
            required_deps = meta.dependencies
            optional_deps = ()
        else:
            # Inspect __init__ signature for required vs optional
            required_deps, optional_deps = self._inspect_dependencies(cls)

        # Resolve dependencies
        kwargs: dict[str, Any] = {}

        # Required: fail immediately if missing
        for name in required_deps:
            if not self.has(name):
                raise DependencyNotFoundError(
                    f"Missing required dependency '{name}' for {cls.__name__}.\n\n"
                    f"This usually means the provider wasn't registered during startup.\n\n"
                    f"Fix: In services/providers.py, add:\n"
                    f"    container.register(\"{name}\", get_{name}, singleton=True)\n\n"
                    f"If this dependency should be optional, update the node's __init__:\n"
                    f"    def __init__(self, {name}: ... | None = None): ..."
                )
            try:
                kwargs[name] = await self.resolve(name)
            except Exception as e:
                raise DependencyNotFoundError(
                    f"Failed to resolve required dependency '{name}' for {cls.__name__}: {e}"
                ) from e

        # Optional: skip gracefully if missing (DEBUG level, not WARNING)
        for name in optional_deps:
            if self.has(name):
                try:
                    kwargs[name] = await self.resolve(name)
                except Exception as e:
                    logger.debug(
                        f"Failed to resolve optional dependency {name}: {e}"
                    )
            else:
                logger.debug(
                    f"Optional dependency '{name}' not registered for {cls.__name__}, "
                    f"using default"
                )

        # Instantiate with resolved dependencies
        return cls(**kwargs)

    def _inspect_dependencies(
        self, cls: type[T]
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """
        Inspect __init__ to find dependency parameter names.

        Separates required (no default) from optional (has default).
        Skips *args, **kwargs, and 'self'.

        Args:
            cls: Class to inspect

        Returns:
            Tuple of (required_deps, optional_deps) based on whether
            parameters have defaults in the signature.
        """
        try:
            sig = inspect.signature(cls.__init__)
        except (ValueError, TypeError):
            return ((), ())

        required: list[str] = []
        optional: list[str] = []

        for name, param in sig.parameters.items():
            # Skip 'self' and *args/**kwargs style parameters
            if name == "self":
                continue
            if param.kind in (
                inspect.Parameter.VAR_POSITIONAL,  # *args
                inspect.Parameter.VAR_KEYWORD,  # **kwargs
            ):
                continue

            if param.default is inspect.Parameter.empty:
                required.append(name)
            else:
                optional.append(name)

        return (tuple(required), tuple(optional))

    def list_providers(self) -> list[str]:
        """List all registered provider names."""
        with self._lock:
            return list(self._providers.keys())

    def clear(self) -> None:
        """Clear all providers and cache (for testing)."""
        with self._lock:
            self._providers.clear()
            self._cache.clear()

    def clear_cache(self) -> None:
        """Clear cached singletons but keep providers."""
        with self._lock:
            self._cache.clear()

    def stats(self) -> dict[str, Any]:
        """Get container statistics."""
        with self._lock:
            return {
                "providers": len(self._providers),
                "cached": len(self._cache),
                "provider_names": list(self._providers.keys()),
            }


# === Global Container Singleton ===

_container: ServiceContainer | None = None
_container_lock = Lock()


def get_container() -> ServiceContainer:
    """
    Get the global service container.

    Returns:
        The singleton ServiceContainer instance

    Example:
        container = get_container()
        container.register("brain_crystal", get_brain_crystal)
    """
    global _container
    if _container is None:
        with _container_lock:
            if _container is None:
                _container = ServiceContainer()
    return _container


def reset_container() -> None:
    """
    Reset the global container (for testing).

    Clears all providers and cached values.
    """
    global _container
    with _container_lock:
        if _container is not None:
            _container.clear()
        _container = None


# === Factory Functions ===


def create_container() -> ServiceContainer:
    """
    Create a new service container.

    Use this for isolated containers (e.g., in tests).
    For the global container, use get_container().

    Returns:
        New ServiceContainer instance
    """
    return ServiceContainer()


# === Exports ===

__all__ = [
    # Exceptions
    "DependencyNotFoundError",
    # Types
    "Provider",
    "ProviderEntry",
    # Container
    "ServiceContainer",
    "get_container",
    "reset_container",
    "create_container",
]
