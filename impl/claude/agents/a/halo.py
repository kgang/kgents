"""
Halo: Declarative Capability Protocol for the Alethic Architecture.

The Halo is the set of capabilities that wrap an agent's Nucleus (pure logic).
Capabilities are metadata decorators that declare what an agent *could become*
without coupling to implementation.

Key Insight:
- Decorators add **metadata only** — no runtime overhead
- No coupling to implementation (D-gent, K-gent not imported)
- Projectors (Local, K8s) read Halo metadata and compile accordingly

Example:
    >>> @Capability.Stateful(schema=MyMemory)
    ... @Capability.Soulful(persona="Kent")
    ... class MyAgent(Agent[str, str]):
    ...     async def invoke(self, input: str) -> str:
    ...         return f"Hello, {input}"
    ...
    >>> halo = get_halo(MyAgent)
    >>> assert len(halo) == 2
    >>> assert has_capability(MyAgent, StatefulCapability)

The Alethic Architecture:
- Nucleus: Pure logic (what the agent does)
- Halo: Declarative capabilities (what the agent could become)
- Projector: Target-specific compilation (how the agent manifests)

See: plans/architecture/alethic.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeVar, overload

if TYPE_CHECKING:
    pass

# Type variable for capability types
T = TypeVar("T", bound="CapabilityBase")

# The attribute name where we store capabilities
HALO_ATTR = "__halo__"


# --- Base Capability Class ---


@dataclass(frozen=True, eq=True)
class CapabilityBase:
    """
    Base class for all capabilities.

    Capabilities are frozen dataclasses that:
    1. Store configuration (schema, persona, etc.)
    2. Act as decorators (add self to __halo__)
    3. Have NO runtime effect (metadata only)

    The frozen=True ensures capabilities are hashable for set storage.
    """

    def __call__(self, cls: type) -> type:
        """
        Decorate an agent class with this capability.

        Adds this capability to the class's __halo__ attribute.
        Does NOT modify runtime behavior.

        Override Semantics:
        - If the class (or parent) already has a capability of the SAME TYPE,
          this decorator REPLACES it with the new configuration.
        - This enables archetype subclasses to override parent capabilities.

        Args:
            cls: The agent class to decorate

        Returns:
            The same class, with __halo__ updated
        """
        # Get existing halo or create new set
        existing_halo: set[CapabilityBase] = getattr(cls, HALO_ATTR, set())

        # Create new halo, replacing any capability of the same type
        # This implements proper override semantics for archetype inheritance
        new_halo: set[CapabilityBase] = set()
        my_type = type(self)

        for cap in existing_halo:
            if type(cap) is not my_type:
                # Keep capabilities of different types
                new_halo.add(cap)
            # else: drop the old capability of same type (will be replaced)

        # Add this capability (either new or replacing old)
        new_halo.add(self)

        # Set on class
        setattr(cls, HALO_ATTR, new_halo)

        return cls


# --- Standard Capabilities ---


@dataclass(frozen=True, eq=True)
class StatefulCapability(CapabilityBase):
    """
    Declare that this agent requires persistent state.

    The Projector will inject appropriate state management:
    - LocalProjector: SQLite Symbiont in ~/.kgents/
    - K8sProjector: StatefulSet + PVC

    Args:
        schema: The state schema type (dataclass or dict)
        backend: Storage backend hint ("auto", "sqlite", "redis", "postgres")
    """

    schema: type
    backend: str = "auto"


@dataclass(frozen=True, eq=True)
class SoulfulCapability(CapabilityBase):
    """
    Declare that this agent should embody K-gent personality.

    The Projector will inject K-gent persona handling:
    - LocalProjector: In-process KgentAgent wrapper
    - K8sProjector: K-gent sidecar container

    Args:
        persona: Name of the persona to embody (e.g., "Kent")
        mode: How strictly to apply persona ("advisory", "strict", "override")
    """

    persona: str
    mode: str = "advisory"


@dataclass(frozen=True, eq=True)
class ObservableCapability(CapabilityBase):
    """
    Declare that this agent should emit observability data.

    The Projector will inject observation infrastructure:
    - LocalProjector: WebSocket to Terrarium
    - K8sProjector: ServiceMonitor + Prometheus

    Args:
        mirror: Enable HolographicBuffer for Terrarium
        metrics: Enable Prometheus metrics
    """

    mirror: bool = True
    metrics: bool = True


@dataclass(frozen=True, eq=True)
class StreamableCapability(CapabilityBase):
    """
    Declare that this agent can be lifted to Flux domain.

    The Projector will configure streaming infrastructure:
    - LocalProjector: asyncio FluxAgent wrapper
    - K8sProjector: HPA + event-driven autoscaling

    Args:
        budget: Entropy budget for stream processing
        feedback: Ouroboric feedback fraction (0.0 - 1.0)
    """

    budget: float = 10.0
    feedback: float = 0.0


@dataclass(frozen=True, eq=True)
class TurnBasedCapability(CapabilityBase):
    """
    Declare that this agent handles turn-based interactions.

    The Turn-gents Protocol: interactions as causal morphisms.

    The Projector will inject turn-based infrastructure:
    - LocalProjector: CausalCone context projection, turn recording
    - K8sProjector: Turn history in PVC, distributed cone computation

    Turn Types:
    - SPEECH: Utterance to user/agent (inspectable)
    - ACTION: Tool call, side effect (interceptable)
    - THOUGHT: Chain-of-thought (hidden by default)
    - YIELD: Request for approval (blocks until resolved)
    - SILENCE: Intentional non-action (logged)

    Args:
        allowed_types: Allowed turn types (None = all allowed)
        dependency_policy: How to compute dependencies
            - "causal_cone": Use CausalCone projection (default)
            - "thread_only": Only agent's own events
            - "explicit": Manual dependency specification
        cone_depth: Maximum depth of causal cone (None = unlimited)
        thought_collapse: Collapse THOUGHT turns in context (default: True)
        entropy_budget: Entropy budget for order (production) turns
        surplus_fraction: Fraction reserved for exploration (Accursed Share)
        yield_threshold: Confidence threshold below which to YIELD
    """

    allowed_types: frozenset[str] | None = None  # None = all allowed
    dependency_policy: str = "causal_cone"
    cone_depth: int | None = None
    thought_collapse: bool = True
    entropy_budget: float = 1.0
    surplus_fraction: float = 0.1
    yield_threshold: float = 0.3


# --- Capability Factory ---


class Capability:
    """
    Factory for creating capability decorators.

    Usage:
        @Capability.Stateful(schema=MySchema)
        @Capability.Soulful(persona="Kent")
        class MyAgent(Agent[A, B]):
            ...

    Each method returns a capability instance that can be used as a decorator.
    """

    @staticmethod
    def Stateful(*, schema: type, backend: str = "auto") -> StatefulCapability:
        """
        Declare that this agent requires persistent state.

        Args:
            schema: The state schema type
            backend: Storage backend hint

        Returns:
            StatefulCapability decorator
        """
        return StatefulCapability(schema=schema, backend=backend)

    @staticmethod
    def Soulful(*, persona: str, mode: str = "advisory") -> SoulfulCapability:
        """
        Declare that this agent should embody K-gent personality.

        Args:
            persona: Name of the persona
            mode: Application mode

        Returns:
            SoulfulCapability decorator
        """
        return SoulfulCapability(persona=persona, mode=mode)

    @staticmethod
    def Observable(
        *, mirror: bool = True, metrics: bool = True
    ) -> ObservableCapability:
        """
        Declare that this agent should emit observability data.

        Args:
            mirror: Enable Terrarium mirror
            metrics: Enable Prometheus metrics

        Returns:
            ObservableCapability decorator
        """
        return ObservableCapability(mirror=mirror, metrics=metrics)

    @staticmethod
    def Streamable(
        *, budget: float = 10.0, feedback: float = 0.0
    ) -> StreamableCapability:
        """
        Declare that this agent can be lifted to Flux domain.

        Args:
            budget: Entropy budget
            feedback: Ouroboric feedback fraction

        Returns:
            StreamableCapability decorator
        """
        return StreamableCapability(budget=budget, feedback=feedback)

    @staticmethod
    def TurnBased(
        *,
        allowed_types: set[str] | None = None,
        dependency_policy: str = "causal_cone",
        cone_depth: int | None = None,
        thought_collapse: bool = True,
        entropy_budget: float = 1.0,
        surplus_fraction: float = 0.1,
        yield_threshold: float = 0.3,
    ) -> TurnBasedCapability:
        """
        Declare that this agent handles turn-based interactions.

        The Turn-gents Protocol: interactions as causal morphisms.
        Context is computed via CausalCone projection, not manually curated.

        Args:
            allowed_types: Set of allowed turn type names (e.g., {"SPEECH", "ACTION"}).
                           None means all types allowed.
            dependency_policy: How to compute dependencies:
                - "causal_cone": Use CausalCone projection (default)
                - "thread_only": Only agent's own events
                - "explicit": Manual dependency specification
            cone_depth: Maximum depth of causal cone (None = unlimited)
            thought_collapse: Collapse THOUGHT turns in context
            entropy_budget: Entropy budget for order (production) turns
            surplus_fraction: Fraction reserved for exploration (Accursed Share)
            yield_threshold: Confidence threshold below which to YIELD

        Returns:
            TurnBasedCapability decorator

        Example:
            @Capability.TurnBased(
                allowed_types={"SPEECH", "ACTION", "THOUGHT"},
                entropy_budget=10.0,
                yield_threshold=0.5,
            )
            class MyAgent(Agent[str, str]):
                ...
        """
        return TurnBasedCapability(
            allowed_types=frozenset(allowed_types) if allowed_types else None,
            dependency_policy=dependency_policy,
            cone_depth=cone_depth,
            thought_collapse=thought_collapse,
            entropy_budget=entropy_budget,
            surplus_fraction=surplus_fraction,
            yield_threshold=yield_threshold,
        )


# --- Halo Introspection Functions ---


def get_halo(agent_cls: type) -> set[CapabilityBase]:
    """
    Get the Halo (capability set) of an agent class.

    Args:
        agent_cls: The agent class to inspect

    Returns:
        Set of capabilities decorating this class

    Example:
        >>> halo = get_halo(MyAgent)
        >>> for cap in halo:
        ...     print(type(cap).__name__)
    """
    return getattr(agent_cls, HALO_ATTR, set()).copy()


def has_capability(agent_cls: type, cap_type: type[CapabilityBase]) -> bool:
    """
    Check if agent has a specific capability type.

    Args:
        agent_cls: The agent class to check
        cap_type: The capability type to look for

    Returns:
        True if agent has the capability

    Example:
        >>> if has_capability(MyAgent, StatefulCapability):
        ...     print("Agent is stateful")
    """
    return any(isinstance(c, cap_type) for c in get_halo(agent_cls))


@overload
def get_capability(agent_cls: type, cap_type: type[T]) -> T | None: ...


@overload
def get_capability(agent_cls: type, cap_type: type[T], default: T) -> T: ...


def get_capability(
    agent_cls: type, cap_type: type[T], default: T | None = None
) -> T | None:
    """
    Get a specific capability instance from the Halo.

    Args:
        agent_cls: The agent class to inspect
        cap_type: The capability type to get
        default: Default value if not found

    Returns:
        The capability instance, or default if not found

    Example:
        >>> cap = get_capability(MyAgent, StreamableCapability)
        >>> if cap:
        ...     print(f"Budget: {cap.budget}")
    """
    for c in get_halo(agent_cls):
        if isinstance(c, cap_type):
            return c
    return default


def merge_halos(*halos: set[CapabilityBase]) -> set[CapabilityBase]:
    """
    Merge multiple halos into one.

    Later halos override earlier ones (by capability type).

    Args:
        *halos: Halos to merge

    Returns:
        Merged halo set

    Example:
        >>> base_halo = {Stateful(...)}
        >>> child_halo = {Soulful(...)}
        >>> merged = merge_halos(base_halo, child_halo)
    """
    result: dict[type, CapabilityBase] = {}
    for halo in halos:
        for cap in halo:
            result[type(cap)] = cap
    return set(result.values())


def get_own_halo(agent_cls: type) -> set[CapabilityBase]:
    """
    Get only the capabilities declared directly on this class (not inherited).

    Args:
        agent_cls: The agent class to inspect

    Returns:
        Set of capabilities declared directly on this class

    Example:
        >>> @Capability.Stateful(schema=dict)
        ... class Parent(Agent): ...
        >>> @Capability.Soulful(persona="Kent")
        ... class Child(Parent): ...
        >>> get_own_halo(Child)  # Returns only Soulful, not Stateful
    """
    # Check if __halo__ is in the class's own __dict__ (not inherited)
    if HALO_ATTR in agent_cls.__dict__:
        own_halo: set[CapabilityBase] = agent_cls.__dict__[HALO_ATTR]
        # We need to find which capabilities were added by this class
        # by comparing with parent's halo
        parent_halo: set[CapabilityBase] = set()
        for base in agent_cls.__bases__:
            parent_halo |= getattr(base, HALO_ATTR, set())
        return own_halo - parent_halo
    return set()


def inherit_halo(parent_cls: type, child_cls: type) -> set[CapabilityBase]:
    """
    Compute inherited halo for a child class.

    Child capabilities override parent capabilities of the same type.

    Args:
        parent_cls: Parent agent class
        child_cls: Child agent class

    Returns:
        Combined halo
    """
    return merge_halos(get_halo(parent_cls), get_own_halo(child_cls))


# --- Exports ---

__all__ = [
    # Base
    "CapabilityBase",
    "HALO_ATTR",
    # Capability types
    "StatefulCapability",
    "SoulfulCapability",
    "ObservableCapability",
    "StreamableCapability",
    "TurnBasedCapability",
    # Factory
    "Capability",
    # Introspection
    "get_halo",
    "get_own_halo",
    "has_capability",
    "get_capability",
    "merge_halos",
    "inherit_halo",
]
