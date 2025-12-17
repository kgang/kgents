"""
Genus Archetypes: Pre-packaged Halos for common agent patterns.

Archetypes provide "batteries included" ergonomics by defining standard
capability sets that subclasses inherit automatically.

The Alethic Architecture:
- Nucleus: Pure logic (what the agent does)
- Halo: Declarative capabilities (what the agent could become)
- Projector: Target-specific compilation (how the agent manifests)
- **Archetype**: Pre-packaged Halo for common patterns

Standard Archetypes:
| Archetype | Capabilities | Use When |
|-----------|--------------|----------|
| Kappa     | All four     | Full-stack service agents |
| Lambda    | Observable   | Stateless function agents |
| Delta     | Stateful + Observable | Data-focused agents |

Example:
    >>> class MyService(Kappa[Request, Response]):
    ...     @property
    ...     def name(self): return "my-service"
    ...     async def invoke(self, req): return process(req)
    ...
    >>> # MyService inherits Kappa's full Halo
    >>> assert has_capability(MyService, StatefulCapability)
    >>> assert has_capability(MyService, SoulfulCapability)

See: plans/architecture/alethic.md
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from agents.poly.types import Agent

from .halo import (
    HALO_ATTR,
    Capability,
    CapabilityBase,
    ObservableCapability,
    SoulfulCapability,
    StatefulCapability,
    StreamableCapability,
    get_halo,
    get_own_halo,
    has_capability,
    merge_halos,
)

# Type variables for agent input/output
A = TypeVar("A")
B = TypeVar("B")


class Archetype(Agent[A, B], Generic[A, B]):
    """
    Base class for pre-packaged capability sets.

    Archetypes provide "batteries included" ergonomics by defining
    standard Halos that subclasses inherit automatically.

    The `__init_subclass__` mechanism transfers the archetype's Halo
    to all subclasses. Subclasses can add or override capabilities.

    Override Rules:
    1. Archetype's Halo is automatically transferred to subclasses
    2. Subclass decorators ADD to the inherited Halo
    3. Same capability type from subclass OVERRIDES archetype's version
    4. Multiple archetype inheritance is NOT supported (use composition)

    Example:
        >>> class MyService(Kappa[Request, Response]):
        ...     @property
        ...     def name(self): return "my-service"
        ...     async def invoke(self, req: Request) -> Response:
        ...         return process(req)
        >>>
        >>> # MyService inherits Kappa's full Halo
        >>> halo = get_halo(MyService)
        >>> assert has_capability(MyService, StatefulCapability)

        >>> # Can override archetype capabilities
        >>> @Capability.Stateful(schema=list, backend="redis")
        ... class CustomService(Kappa[str, str]):
        ...     @property
        ...     def name(self): return "custom"
        ...     async def invoke(self, x): return x
        >>>
        >>> cap = get_capability(CustomService, StatefulCapability)
        >>> assert cap.backend == "redis"  # Overridden
    """

    @classmethod
    def archetype_halo(cls) -> set[CapabilityBase]:
        """
        Return the archetype's pre-defined Halo.

        Subclasses of specific archetypes (Kappa, Lambda, Delta) inherit
        this from their parent. The base Archetype class has an empty halo.

        Returns:
            Set of capabilities defined by this archetype.
        """
        # Base Archetype has no pre-defined capabilities
        # Concrete archetypes (Kappa, etc.) override this via __init_subclass__
        return getattr(cls, HALO_ATTR, set()).copy()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Transfer archetype Halo to subclass.

        When a class inherits from an Archetype:
        1. Find the archetype parent in MRO
        2. Get the archetype's Halo
        3. Merge with any capabilities declared on the subclass
        4. Set the merged Halo on the subclass

        The merge uses `merge_halos` which handles override semantics:
        - Later halos override earlier ones by capability TYPE
        - So subclass decorators override archetype capabilities
        """
        super().__init_subclass__(**kwargs)

        # Find archetype parent in MRO (skip the class itself and Archetype base)
        archetype_parent: type[Archetype[Any, Any]] | None = None
        for base in cls.__mro__[1:]:
            if base is Archetype:
                # We've reached the base, no archetype parent found
                break
            if (
                isinstance(base, type)
                and issubclass(base, Archetype)
                and base is not Archetype
            ):
                # Found an archetype parent (Kappa, Lambda, Delta, or custom)
                archetype_parent = base
                break

        if archetype_parent is None:
            # No archetype parent, nothing to inherit
            return

        # Get parent archetype's halo
        parent_halo = archetype_parent.archetype_halo()

        # Get only capabilities declared directly on cls (not inherited).
        # The decorator's __call__ copies parent halo and adds new cap,
        # so we need to extract only the NEW capabilities.
        own_halo = get_own_halo(cls)

        # Check if cls has its OWN halo (not inherited from parent)
        has_own_halo = HALO_ATTR in cls.__dict__

        if has_own_halo and own_halo:
            # Subclass has NEW decorators - merge parent with child (child overrides)
            merged = merge_halos(parent_halo, own_halo)
        else:
            # No new decorators on subclass - just inherit parent's halo
            merged = parent_halo.copy()

        # Set the merged halo on the class
        setattr(cls, HALO_ATTR, merged)


# --- Define the archetype classes with their Halos ---
# We apply decorators to the class BEFORE __init_subclass__ runs for children


@Capability.Stateful(schema=dict, backend="auto")
@Capability.Soulful(persona="default", mode="advisory")
@Capability.Observable(mirror=True, metrics=True)
@Capability.Streamable(budget=10.0, feedback=0.0)
class Kappa(Archetype[A, B], Generic[A, B]):
    """
    KAPPA: Full-stack service agent.

    Includes all four capabilities:
    - Stateful: Persistent state management (dict schema, auto backend)
    - Soulful: K-gent personality governance (default persona, advisory mode)
    - Observable: Terrarium integration (mirror + metrics enabled)
    - Streamable: Flux stream processing (10.0 entropy budget)

    Use when: Building complete, production-ready agents that need
    state persistence, personality governance, observability, and
    stream processing capabilities.

    The "batteries included" choice for most agents.

    Example:
        >>> class MyAPI(Kappa[Request, Response]):
        ...     @property
        ...     def name(self): return "my-api"
        ...     async def invoke(self, req: Request) -> Response:
        ...         return Response(data=process(req))
        >>>
        >>> # Full Halo automatically available
        >>> compiled = LocalProjector().compile(MyAPI)
    """


@Capability.Observable(mirror=False, metrics=True)
class Lambda(Archetype[A, B], Generic[A, B]):
    """
    LAMBDA: Stateless function agent.

    Minimal capabilities for pure transformations:
    - Observable: Metrics only (mirror disabled for minimal overhead)

    Use when: Building stateless transformers, mappers, validators,
    or any pure function that doesn't need state, personality, or streaming.

    The lightweight choice for simple transformations.

    Example:
        >>> class Sanitizer(Lambda[str, str]):
        ...     @property
        ...     def name(self): return "sanitizer"
        ...     async def invoke(self, text: str) -> str:
        ...         return sanitize(text)
        >>>
        >>> # Only Observable capability
        >>> assert has_capability(Sanitizer, ObservableCapability)
        >>> assert not has_capability(Sanitizer, StatefulCapability)
    """


@Capability.Stateful(schema=dict, backend="auto")
@Capability.Observable(mirror=True, metrics=True)
class Delta(Archetype[A, B], Generic[A, B]):
    """
    DELTA: Data-focused agent.

    Capabilities for data processing:
    - Stateful: Persistent state for accumulation/aggregation
    - Observable: Full observability (mirror + metrics)

    Use when: Building data pipelines, aggregators, ETL agents,
    or any agent that needs to maintain state across invocations
    without personality governance or streaming.

    The choice for data-centric operations.

    Example:
        >>> class Aggregator(Delta[Event, Summary]):
        ...     @property
        ...     def name(self): return "aggregator"
        ...     async def invoke(self, event: Event) -> Summary:
        ...         return accumulate(event)
        >>>
        >>> # Stateful + Observable
        >>> assert has_capability(Aggregator, StatefulCapability)
        >>> assert has_capability(Aggregator, ObservableCapability)
        >>> assert not has_capability(Aggregator, StreamableCapability)
    """


# --- Utility Functions ---


def get_archetype(cls: type) -> type[Archetype[Any, Any]] | None:
    """
    Find the archetype parent of a class.

    Args:
        cls: The class to inspect

    Returns:
        The archetype class (Kappa, Lambda, Delta, etc.) or None

    Example:
        >>> class MyService(Kappa[str, str]): ...
        >>> get_archetype(MyService)
        <class 'Kappa'>
    """
    for base in cls.__mro__:
        if isinstance(base, type) and issubclass(base, Archetype):
            if base is not Archetype and base is not cls:
                return base
    return None


def is_archetype_instance(obj: Any) -> bool:
    """
    Check if an object is an instance of an Archetype subclass.

    Args:
        obj: The object to check

    Returns:
        True if obj is an instance of Kappa, Lambda, Delta, etc.
    """
    return isinstance(obj, Archetype)


# --- Exports ---

__all__ = [
    # Base
    "Archetype",
    # Standard Archetypes
    "Kappa",
    "Lambda",
    "Delta",
    # Utilities
    "get_archetype",
    "is_archetype_instance",
]
