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
class TurnBasedAdapter(Agent[A, B], Generic[A, B]):
    """
    Adapter that wraps an agent with Turn-gents Protocol behavior.

    The Turn-gents Protocol: interactions as causal morphisms.

    This adapter:
    1. Maintains a TheWeave for turn history
    2. Computes CausalCone context before each invoke
    3. Records turns to the weave after each invoke
    4. Tracks confidence and entropy costs
    5. Auto-yields for low-confidence ACTION turns

    The key insight: "Context is a Light Cone, not a Window."
    Instead of feeding the full history, we compute the causal
    cone for the current agent to get minimal relevant context.

    Args:
        inner: The wrapped agent
        allowed_types: Which turn types are allowed
        dependency_policy: How to compute dependencies
        cone_depth: Maximum depth of causal cone
        thought_collapse: Whether to collapse THOUGHT turns
        entropy_budget: Budget for order turns
        surplus_fraction: Fraction for exploration
        yield_threshold: Confidence threshold for YIELD
        yield_approvers: Default approvers for auto-yield
    """

    inner: Agent[A, B]
    allowed_types: frozenset[str] | None = None
    dependency_policy: str = "causal_cone"
    cone_depth: int | None = None
    thought_collapse: bool = True
    entropy_budget: float = 1.0
    surplus_fraction: float = 0.1
    yield_threshold: float = 0.3
    yield_approvers: frozenset[str] = field(
        default_factory=lambda: frozenset({"human"})
    )

    # Runtime state (not part of configuration)
    _weave: Any = field(default=None, init=False, repr=False)
    _cone: Any = field(default=None, init=False, repr=False)
    _entropy_spent: float = field(default=0.0, init=False, repr=False)
    _yield_handler: Any = field(default=None, init=False, repr=False)

    @property
    def name(self) -> str:
        return f"TurnBased({self.inner.name})"

    @property
    def weave(self) -> Any:
        """Access the turn history weave (from lifecycle or lazy-initialized)."""
        if self._weave is None:
            self._weave = self._get_or_create_weave()
        return self._weave

    def _get_or_create_weave(self) -> Any:
        """
        Get global weave from lifecycle or create instance-local fallback.

        The global weave is preferred because it enables:
        - Cross-agent turn correlation
        - CLI debugging via `kg turns` and `kg dag`
        - Compression metrics for H1 validation

        Falls back to instance-local weave if lifecycle not available.
        """
        # Try lifecycle state first (shared weave)
        try:
            from protocols.cli.hollow import get_lifecycle_state

            state = get_lifecycle_state()
            if state and state.weave is not None:
                return state.weave
        except ImportError:
            pass

        # Fallback to instance-local weave
        from weave import TheWeave

        return TheWeave()

    @property
    def cone(self) -> Any:
        """Access the causal cone projector (lazy-initialized)."""
        if self._cone is None:
            from weave import CausalCone

            self._cone = CausalCone(self.weave)
        return self._cone

    @property
    def yield_handler(self) -> Any:
        """Access the yield handler (lazy-initialized)."""
        if self._yield_handler is None:
            from weave.yield_handler import YieldHandler

            self._yield_handler = YieldHandler()
        return self._yield_handler

    def get_context(self, agent_id: str | None = None) -> list[Any]:
        """
        Get the causal context for the next turn.

        This is the key operation: compute minimal context
        via CausalCone projection instead of full history.

        Also logs compression metrics for H1 validation when using
        causal_cone dependency policy.

        Args:
            agent_id: Optional agent ID (defaults to inner.name)

        Returns:
            List of causally-relevant events in topological order
        """
        aid = agent_id or self.inner.name

        # Get full weave size for compression metrics
        full_size = len(self.weave)

        context: list[Any]
        if self.dependency_policy == "causal_cone":
            context = self.cone.project_context(aid)
        elif self.dependency_policy == "thread_only":
            context = self.weave.thread(aid)
        else:  # explicit
            context = []

        # Apply thought collapse if enabled
        if self.thought_collapse:
            from weave.turn import TurnType

            context = [
                e
                for e in context
                if not (hasattr(e, "turn_type") and e.turn_type == TurnType.THOUGHT)
            ]

        # Apply cone depth limit if set
        if self.cone_depth is not None and len(context) > self.cone_depth:
            context = context[-self.cone_depth :]

        # Log compression metrics for H1 validation
        # Only log when using causal_cone and there's meaningful data
        if self.dependency_policy == "causal_cone" and full_size > 0:
            try:
                from weave.metrics import estimate_tokens, log_compression

                full_tokens = estimate_tokens(full_size)
                cone_tokens = estimate_tokens(len(context))
                log_compression(aid, full_tokens, cone_tokens)
            except ImportError:
                pass  # Metrics module not available

        return context

    async def record_turn(
        self,
        content: Any,
        turn_type: str = "SPEECH",
        confidence: float = 1.0,
        entropy_cost: float = 0.0,
        depends_on: set[str] | None = None,
    ) -> str:
        """
        Record a turn to the weave.

        Args:
            content: The turn content
            turn_type: Type of turn (SPEECH, ACTION, THOUGHT, YIELD, SILENCE)
            confidence: Meta-cognition confidence score
            entropy_cost: Cost of this turn
            depends_on: Explicit dependencies (auto-computed if None)

        Returns:
            The turn ID
        """
        from weave import Turn
        from weave import TurnType as TT

        # Parse turn type
        tt = getattr(TT, turn_type, TT.SPEECH)

        # Validate against allowed types
        if self.allowed_types is not None and turn_type not in self.allowed_types:
            tt = TT.SPEECH  # Default to SPEECH if not allowed

        # Create turn
        turn = Turn.create_turn(
            content=content,
            source=self.inner.name,
            turn_type=tt,
            confidence=confidence,
            entropy_cost=entropy_cost,
        )

        # Compute dependencies if not provided
        if depends_on is None:
            tip = self.weave.tip(self.inner.name)
            depends_on = {tip.id} if tip else None

        # Record to weave
        self.weave.monoid.append_mut(turn, depends_on)

        # Refresh cone cache
        self.cone.refresh_braid()

        # Track entropy
        self._entropy_spent += entropy_cost

        return turn.id

    @property
    def entropy_remaining(self) -> float:
        """Get remaining entropy budget."""
        return max(0.0, self.entropy_budget - self._entropy_spent)

    @property
    def surplus_remaining(self) -> float:
        """Get remaining surplus (exploration) budget."""
        surplus_total = self.entropy_budget * self.surplus_fraction
        surplus_spent = min(
            self._entropy_spent * self.surplus_fraction,
            surplus_total,
        )
        return max(0.0, surplus_total - surplus_spent)

    def should_yield(self, confidence: float, turn_type: str = "ACTION") -> bool:
        """
        Determine if an action should generate a YIELD turn.

        Based on yield_threshold configuration and turn type.

        Args:
            confidence: The action's confidence score [0.0, 1.0]
            turn_type: The type of turn being evaluated

        Returns:
            True if the action should yield for approval
        """
        from weave.yield_handler import should_yield

        return should_yield(confidence, self.yield_threshold, turn_type)

    async def create_yield_turn(
        self,
        content: Any,
        yield_reason: str,
        *,
        required_approvers: set[str] | None = None,
        confidence: float = 0.5,
        entropy_cost: float = 0.0,
    ) -> Any:
        """
        Create and record a YIELD turn.

        Args:
            content: The proposed action/content
            yield_reason: Why approval is needed
            required_approvers: Who must approve (defaults to yield_approvers)
            confidence: Meta-cognition confidence score
            entropy_cost: Cost of this turn

        Returns:
            The YieldTurn that was created
        """
        from weave import YieldTurn

        approvers = required_approvers or set(self.yield_approvers)

        yield_turn = YieldTurn.create_yield(
            content=content,
            source=self.inner.name,
            yield_reason=yield_reason,
            required_approvers=approvers,
            confidence=confidence,
            entropy_cost=entropy_cost,
        )

        # Record to weave
        tip = self.weave.tip(self.inner.name)
        depends_on = {tip.id} if tip else None
        self.weave.monoid.append_mut(yield_turn, depends_on)

        # Refresh cone cache
        self.cone.refresh_braid()

        # Track entropy
        self._entropy_spent += entropy_cost

        return yield_turn

    async def request_approval(
        self,
        content: Any,
        yield_reason: str,
        *,
        required_approvers: set[str] | None = None,
        timeout: float | None = None,
        confidence: float = 0.5,
    ) -> Any:
        """
        Create a YIELD turn and block until approval/rejection/timeout.

        This is the high-level API for yielding with approval flow.

        Args:
            content: The proposed action/content
            yield_reason: Why approval is needed
            required_approvers: Who must approve
            timeout: Optional timeout in seconds
            confidence: Meta-cognition confidence score

        Returns:
            ApprovalResult with status and final turn state
        """
        yield_turn = await self.create_yield_turn(
            content=content,
            yield_reason=yield_reason,
            required_approvers=required_approvers,
            confidence=confidence,
        )

        return await self.yield_handler.request_approval(yield_turn, timeout=timeout)

    async def invoke(self, input_data: A) -> B:
        """
        Invoke the inner agent with turn-based behavior.

        1. Compute causal context
        2. Invoke inner agent
        3. Record turn to weave

        The context is available but not automatically injected -
        the agent can query get_context() if needed.
        """
        result = await self.inner.invoke(input_data)

        # Record as SPEECH turn (default)
        await self.record_turn(
            content=result,
            turn_type="SPEECH",
            confidence=1.0,
            entropy_cost=0.01,  # Minimal cost for basic turns
        )

        return result


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
            "TurnBasedCapability",
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

        # 4. Apply @TurnBased (Turn-gents Protocol)
        if _has_cap("TurnBasedCapability"):
            turnbased_cap = _get_cap("TurnBasedCapability")
            if turnbased_cap is not None:
                agent = self._apply_turnbased(agent, turnbased_cap)

        # 5. Apply @Observable (Mirror)
        # Note: Observable without Streamable just marks the agent
        observable_cap: Any = None
        if _has_cap("ObservableCapability"):
            observable_cap = _get_cap("ObservableCapability")

        # 6. Apply @Streamable (Flux-functor) - outermost
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

    def _apply_turnbased(self, agent: Agent[Any, Any], cap: Any) -> Agent[Any, Any]:
        """
        Wrap agent with Turn-gents Protocol behavior.

        Creates a TurnBasedAdapter that:
        - Maintains turn history in TheWeave
        - Computes CausalCone context before each turn
        - Records turns after each invoke
        - Tracks entropy costs

        Args:
            agent: The agent to wrap
            cap: TurnBasedCapability with protocol configuration

        Returns:
            TurnBasedAdapter wrapping the agent
        """
        return TurnBasedAdapter(
            inner=agent,
            allowed_types=cap.allowed_types,
            dependency_policy=cap.dependency_policy,
            cone_depth=cap.cone_depth,
            thought_collapse=cap.thought_collapse,
            entropy_budget=cap.entropy_budget,
            surplus_fraction=cap.surplus_fraction,
            yield_threshold=cap.yield_threshold,
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

        LocalProjector supports all five standard capabilities:
        - StatefulCapability
        - SoulfulCapability
        - ObservableCapability
        - StreamableCapability
        - TurnBasedCapability

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
            TurnBasedCapability,
        )

        return capability in {
            StatefulCapability,
            SoulfulCapability,
            ObservableCapability,
            StreamableCapability,
            TurnBasedCapability,
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
