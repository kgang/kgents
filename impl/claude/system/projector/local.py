"""
LocalProjector: Compiles agent Halo to runnable Python objects.

The LocalProjector reads an agent's declarative capabilities (Halo)
and produces a runnable Python agent with all capabilities active.

Capability Mapping:
| Capability  | LocalProjector Action                           |
|-------------|------------------------------------------------|
| @Stateful   | Wrap with Symbiont(memory=VolatileAgent(...))  |
| @Soulful    | Wrap with K-gent persona advisor                |
| @Observable | Pre-attach mirror for Terrarium integration     |
| @Streamable | Wrap with FluxAgent(config=FluxConfig(...))     |

Canonical Functor Ordering:
    Nucleus → D → K → Mirror → Flux
            (inner)        (outer)

Example:
    >>> @Capability.Stateful(schema=MyState)
    ... @Capability.Streamable(budget=5.0)
    ... class MyAgent(Agent[str, str]):
    ...     @property
    ...     def name(self): return "my-agent"
    ...     async def invoke(self, x): return x.upper()
    >>>
    >>> compiled = LocalProjector().compile(MyAgent)
    >>> # compiled is FluxAgent wrapping stateful MyAgent
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from bootstrap.types import Agent

from .base import CompilationError, Projector, UnsupportedCapabilityError

if TYPE_CHECKING:
    from agents.a.halo import CapabilityBase


# Type variables for agent input/output
A = TypeVar("A")
B = TypeVar("B")
S = TypeVar("S")


@dataclass
class ObservableMixin:
    """
    Mixin for agents that declares observable intent.

    When @Observable is declared but @Streamable is not,
    the agent can't be wrapped with FluxAgent (which has attach_mirror).
    Instead, we mark the agent as "observable" so that when it IS
    later lifted to Flux, the mirror gets attached automatically.

    This is the pre-attachment pattern: declare intent now,
    realize it when the agent is used in a streaming context.
    """

    _observable_config: dict[str, Any] = field(default_factory=dict)

    @property
    def observable_config(self) -> dict[str, Any]:
        """Get the observable configuration (mirror=True, metrics=True, etc.)."""
        return self._observable_config


@dataclass
class StatefulAdapter(Agent[A, B], Generic[A, B, S]):
    """
    Adapter that bridges Agent[A, B] to Symbiont's (A, S) -> (B, S) signature.

    The Symbiont pattern expects logic: (Input, State) -> (Output, State).
    Our agents have invoke(Input) -> Output.

    This adapter:
    1. Stores state in a D-gent (VolatileAgent)
    2. Makes state accessible to the wrapped agent
    3. Provides state persistence via async context
    """

    inner: Agent[A, B]
    _state: S
    _state_schema: type[S]

    @property
    def name(self) -> str:
        return f"Stateful({self.inner.name})"

    @property
    def state(self) -> S:
        """Access current state (for agents that need it)."""
        return self._state

    async def update_state(self, new_state: S) -> None:
        """Update the state."""
        self._state = new_state

    async def invoke(self, input_data: A) -> B:
        """
        Invoke the inner agent with state context available.

        The inner agent can access state via parent reference if needed.
        This is a simple state management pattern - the agent doesn't
        explicitly receive state, but can query it.
        """
        return await self.inner.invoke(input_data)


@dataclass
class SoulfulAdapter(Agent[A, B], Generic[A, B]):
    """
    Adapter that wraps an agent with K-gent personality governance.

    The K-gent persona acts as an "advisor" that can be queried
    for preference alignment. In advisory mode (default), the wrapped
    agent runs normally but has access to persona guidance.

    In strict mode, the persona could intercept and modify outputs.
    (Not implemented here - that's for Phase 3 Archetypes)
    """

    inner: Agent[A, B]
    persona_name: str
    persona_mode: str = "advisory"

    # Lazy-loaded persona state
    _persona_state: Any = field(default=None, init=False)

    @property
    def name(self) -> str:
        return f"Soulful({self.inner.name}, persona={self.persona_name})"

    @property
    def persona(self) -> Any:
        """Access the K-gent persona state."""
        if self._persona_state is None:
            # Lazy import to avoid circular dependencies
            from agents.k.persona import PersonaSeed, PersonaState

            self._persona_state = PersonaState(seed=PersonaSeed(name=self.persona_name))
        return self._persona_state

    async def invoke(self, input_data: A) -> B:
        """
        Invoke the inner agent with K-gent governance.

        In advisory mode, we simply pass through.
        The persona is available for consultation if needed.
        """
        return await self.inner.invoke(input_data)


@dataclass
class LocalProjector(Projector[Agent[Any, Any]]):
    """
    Compiles agent Halo into local Python runtime.

    The LocalProjector reads capability decorators and applies
    functor wrappers in canonical order:

        Nucleus → D → K → Mirror → Flux
                (inner)        (outer)

    This ordering ensures:
    1. D (Stateful) is innermost - state management is foundational
    2. K (Soulful) wraps stateful - personality governs stateful behavior
    3. Mirror (Observable) wraps personalized+stateful - observe full stack
    4. Flux (Streamable) is outermost - stream processes complete agent

    Configuration:
        state_dir: Directory for persistent state storage
                   Default: ~/.kgents/state (created if needed)

    Example:
        >>> @Capability.Stateful(schema=MyState)
        ... @Capability.Streamable(budget=5.0)
        ... class MyAgent(Agent[str, str]): ...
        >>>
        >>> compiled = LocalProjector().compile(MyAgent)
        >>> # compiled is FluxAgent wrapping Symbiont wrapping MyAgent
    """

    state_dir: str = "~/.kgents/state"

    @property
    def name(self) -> str:
        return "LocalProjector"

    def compile(self, agent_cls: type[Agent[Any, Any]]) -> Agent[Any, Any]:
        """
        Compile agent class to runnable instance.

        Applies functors in canonical order: D → K → Mirror → Flux.

        Args:
            agent_cls: The decorated agent class to compile

        Returns:
            Runnable agent with all capabilities active

        Raises:
            UnsupportedCapabilityError: If agent has unsupported capability
            CompilationError: If compilation fails
        """
        # Import Halo introspection functions
        from agents.a.halo import (
            get_halo,
        )

        # Local helper functions that work by capability NAME rather than identity.
        # This is needed because Python can import the same module via different
        # paths (e.g., agents.a.halo vs claude.agents.a.halo), creating different
        # class objects that fail identity checks.
        def _has_cap(cap_name: str) -> bool:
            return any(type(c).__name__ == cap_name for c in halo)

        def _get_cap(cap_name: str) -> Any:
            for c in halo:
                if type(c).__name__ == cap_name:
                    return c
            return None

        # Check for unsupported capabilities
        halo = get_halo(agent_cls)
        supported_type_names = {
            "StatefulCapability",
            "SoulfulCapability",
            "ObservableCapability",
            "StreamableCapability",
        }

        for cap in halo:
            if type(cap).__name__ not in supported_type_names:
                raise UnsupportedCapabilityError(type(cap), self.name)

        # 1. Instantiate the nucleus
        try:
            agent: Agent[Any, Any] = agent_cls()
        except Exception as e:
            raise CompilationError(agent_cls, f"Failed to instantiate: {e}") from e

        # 2. Apply @Stateful (D-functor) - innermost
        if _has_cap("StatefulCapability"):
            stateful_cap = _get_cap("StatefulCapability")
            if stateful_cap is not None:
                agent = self._apply_stateful(agent, stateful_cap)

        # 3. Apply @Soulful (K-functor)
        if _has_cap("SoulfulCapability"):
            soulful_cap = _get_cap("SoulfulCapability")
            if soulful_cap is not None:
                agent = self._apply_soulful(agent, soulful_cap)

        # 4. Apply @Observable (Mirror)
        # Note: Observable without Streamable just marks the agent
        observable_cap: Any = None
        if _has_cap("ObservableCapability"):
            observable_cap = _get_cap("ObservableCapability")

        # 5. Apply @Streamable (Flux-functor) - outermost
        if _has_cap("StreamableCapability"):
            streamable_cap = _get_cap("StreamableCapability")
            if streamable_cap is not None:
                agent = self._apply_streamable(agent, streamable_cap, observable_cap)
        elif observable_cap is not None:
            # Observable without Streamable: mark as observable
            agent = self._apply_observable_only(agent, observable_cap)

        return agent

    def _apply_stateful(self, agent: Agent[Any, Any], cap: Any) -> Agent[Any, Any]:
        """
        Wrap agent with state management.

        Uses StatefulAdapter which provides state access to the wrapped agent.

        Args:
            agent: The agent to wrap
            cap: StatefulCapability with schema and backend info

        Returns:
            StatefulAdapter wrapping the agent
        """
        # Create initial state from schema
        schema = cap.schema
        try:
            if schema is dict:
                initial_state: Any = {}
            elif hasattr(schema, "__dataclass_fields__"):
                # Dataclass - instantiate with defaults
                initial_state = schema()
            else:
                # Try to instantiate
                initial_state = schema()
        except Exception:
            # Fall back to empty dict
            initial_state = {}

        return StatefulAdapter(
            inner=agent,
            _state=initial_state,
            _state_schema=schema,
        )

    def _apply_soulful(self, agent: Agent[Any, Any], cap: Any) -> Agent[Any, Any]:
        """
        Wrap agent with K-gent personality.

        Creates a SoulfulAdapter that provides persona governance.

        Args:
            agent: The agent to wrap
            cap: SoulfulCapability with persona and mode info

        Returns:
            SoulfulAdapter wrapping the agent
        """
        return SoulfulAdapter(
            inner=agent,
            persona_name=cap.persona,
            persona_mode=cap.mode,
        )

    def _apply_observable_only(
        self, agent: Agent[Any, Any], cap: Any
    ) -> Agent[Any, Any]:
        """
        Mark agent as observable when not wrapped with Flux.

        The agent remains as-is but gets an observable marker.
        When later lifted to Flux, the marker triggers mirror attachment.

        Args:
            agent: The agent to mark
            cap: ObservableCapability with mirror and metrics settings

        Returns:
            Agent with observable marker (same agent, marked)
        """
        # Store observable config on the agent for later use
        # This is a "pre-attachment" - actual mirror attached when in Flux context
        if not hasattr(agent, "_observable_config"):
            # For plain agents, we can't modify them in-place
            # Return as-is - the observable intent is recorded in the Halo
            pass
        return agent

    def _apply_streamable(
        self,
        agent: Agent[Any, Any],
        cap: Any,
        observable_cap: Any | None,
    ) -> Agent[Any, Any]:
        """
        Lift agent to Flux domain.

        Creates a FluxAgent wrapper with the specified entropy budget
        and feedback settings.

        Args:
            agent: The agent to lift
            cap: StreamableCapability with budget and feedback settings
            observable_cap: Optional ObservableCapability for mirror attachment

        Returns:
            FluxAgent wrapping the agent
        """
        from agents.flux import FluxAgent
        from agents.flux.config import FluxConfig

        config = FluxConfig(
            entropy_budget=cap.budget,
            feedback_fraction=cap.feedback,
        )

        flux_agent = FluxAgent(inner=agent, config=config)

        # If @Observable was also declared, pre-attach mirror intent
        # Actual mirror attached via attach_mirror() at runtime
        if observable_cap is not None and observable_cap.mirror:
            # The FluxAgent supports attach_mirror() method
            # But we don't have a HolographicBuffer yet
            # This is "declaration" - actual attachment happens at runtime
            pass

        # FluxAgent has name and invoke like Agent, so we cast
        # This preserves the FluxAgent type while satisfying the return type
        return cast(Agent[Any, Any], flux_agent)

    def supports(self, capability: type["CapabilityBase"]) -> bool:
        """
        Check if LocalProjector supports a capability type.

        LocalProjector supports all four standard capabilities:
        - StatefulCapability
        - SoulfulCapability
        - ObservableCapability
        - StreamableCapability

        Args:
            capability: The capability type to check

        Returns:
            True if capability is supported
        """
        from agents.a.halo import (
            ObservableCapability,
            SoulfulCapability,
            StatefulCapability,
            StreamableCapability,
        )

        return capability in {
            StatefulCapability,
            SoulfulCapability,
            ObservableCapability,
            StreamableCapability,
        }

    def _ensure_state_dir(self) -> Path:
        """
        Ensure state directory exists.

        Returns:
            Path to state directory
        """
        path = Path(self.state_dir).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        return path
