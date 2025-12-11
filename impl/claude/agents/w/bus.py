"""
W-gent Middleware Bus: Central nervous system for agent coordination.

The Bus intercepts all agent invocations, enabling:
- B-gent metering (token economics)
- J-gent safety (entropy/reality gating)
- O-gent telemetry (observation emission)
- K-gent persona (prior injection)

Architecture:
    Agent A --[BusMessage]--> MiddlewareBus --[dispatch]--> Agent B
                                   |
                            [Interceptors]
                            - before(): transform/block
                            - after(): transform result

Key insight: Agents never call each other directly. They emit messages
to the bus, which routes through registered interceptors.

See: docs/agent-cross-pollination-final-proposal.md (Phase 0)
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Generic, TypeVar, Protocol, runtime_checkable

A = TypeVar("A")
B = TypeVar("B")


class MessagePriority(Enum):
    """Message priority levels for dispatch ordering."""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class BusMessage(Generic[A, B]):
    """
    Every agent call becomes a message on the bus.

    The bus intercepts all communication, enabling middleware
    patterns (metering, safety, telemetry) without agent coupling.
    """

    # Required fields
    source: str  # Source agent ID
    target: str  # Target agent ID
    payload: A  # The input to the target agent

    # Unique message identifier
    message_id: str = field(
        default_factory=lambda: f"msg-{datetime.now(timezone.utc).timestamp()}"
    )

    # Routing metadata
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Interceptor state
    blocked: bool = False
    block_reason: str | None = None

    # Context for interceptors
    context: dict[str, Any] = field(default_factory=dict)

    # Optional functor for C-gent structural mapping
    functor_name: str | None = None

    def block(self, reason: str) -> None:
        """Mark this message as blocked by an interceptor."""
        self.blocked = True
        self.block_reason = reason

    def set_context(self, key: str, value: Any) -> None:
        """Add context for downstream interceptors."""
        self.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Retrieve context set by upstream interceptors."""
        return self.context.get(key, default)


@dataclass
class InterceptorResult(Generic[B]):
    """
    Result from an interceptor's after() hook.

    Allows interceptors to transform results, add metadata,
    or inject errors without modifying the target agent.
    """

    value: B
    modified: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Interceptor(Protocol):
    """
    Interceptor protocol for bus middleware.

    Interceptors can:
    - Transform or block messages (before)
    - Transform results (after)
    - Emit side effects (telemetry, logging)

    Example interceptors:
    - MeteringInterceptor (B-gent): Token accounting
    - SafetyInterceptor (J-gent): Entropy/reality check
    - TelemetryInterceptor (O-gent): Observation emission
    - PersonaInterceptor (K-gent): Prior injection
    """

    @property
    def name(self) -> str:
        """Unique interceptor name."""
        ...

    @property
    def order(self) -> int:
        """
        Execution order (lower = earlier).

        Recommended ranges:
        - 0-99: Security (J-gent)
        - 100-199: Economics (B-gent)
        - 200-299: Telemetry (O-gent)
        - 300-399: Persona (K-gent)
        - 400+: Custom
        """
        ...

    async def before(self, msg: BusMessage[Any, Any]) -> BusMessage[Any, Any]:
        """
        Transform message before dispatch.

        Can:
        - Modify payload
        - Block message (msg.block(reason))
        - Add context for other interceptors

        Returns the (possibly modified) message.
        """
        ...

    async def after(
        self, msg: BusMessage[Any, Any], result: Any
    ) -> InterceptorResult[Any]:
        """
        Transform result after dispatch.

        Can:
        - Modify result
        - Add metadata
        - Emit telemetry

        Returns InterceptorResult with (possibly modified) value.
        """
        ...


class BaseInterceptor(ABC):
    """
    Base class for interceptors with sensible defaults.

    Subclass and override before/after as needed.
    """

    def __init__(self, name: str, order: int = 500):
        self._name = name
        self._order = order

    @property
    def name(self) -> str:
        return self._name

    @property
    def order(self) -> int:
        return self._order

    async def before(self, msg: BusMessage[Any, Any]) -> BusMessage[Any, Any]:
        """Default: pass through unchanged."""
        return msg

    async def after(
        self, msg: BusMessage[Any, Any], result: Any
    ) -> InterceptorResult[Any]:
        """Default: wrap result unchanged."""
        return InterceptorResult(value=result)


class PassthroughInterceptor(BaseInterceptor):
    """No-op interceptor for testing."""

    def __init__(self, name: str = "passthrough"):
        super().__init__(name, order=999)


@runtime_checkable
class Invocable(Protocol[A, B]):
    """Protocol for anything that can be invoked."""

    async def invoke(self, input: A) -> B: ...


class AgentRegistry:
    """
    Registry of invocable agents.

    The bus looks up targets here. Agents register themselves
    at startup and can be dynamically added/removed.
    """

    def __init__(self) -> None:
        self._agents: dict[str, Invocable[Any, Any]] = {}

    def register(self, agent_id: str, agent: Invocable[Any, Any]) -> None:
        """Register an agent for bus dispatch."""
        self._agents[agent_id] = agent

    def unregister(self, agent_id: str) -> bool:
        """Remove an agent. Returns True if found."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False

    def get(self, agent_id: str) -> Invocable[Any, Any] | None:
        """Get agent by ID."""
        return self._agents.get(agent_id)

    def list_agents(self) -> list[str]:
        """List all registered agent IDs."""
        return list(self._agents.keys())

    async def invoke(self, agent_id: str, payload: Any) -> Any:
        """Invoke an agent by ID."""
        agent = self._agents.get(agent_id)
        if agent is None:
            raise KeyError(f"Agent not found: {agent_id}")
        return await agent.invoke(payload)


@dataclass
class DispatchResult(Generic[B]):
    """
    Complete result of a bus dispatch.

    Includes:
    - The final result value
    - Whether message was blocked
    - Interceptor metadata
    - Timing information
    """

    value: B | None
    blocked: bool = False
    block_reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    interceptors_run: list[str] = field(default_factory=list)


class MiddlewareBus:
    """
    W-gent as the nervous system.

    The bus intercepts all agent invocations, running them through
    registered interceptors. This enables:

    - Universal metering (B-gent)
    - Safety gating (J-gent)
    - Telemetry (O-gent)
    - Prior injection (K-gent)

    Without any agent knowing about these concerns.

    Example:
        bus = MiddlewareBus()
        bus.register_interceptor(MeteringInterceptor())
        bus.register_interceptor(SafetyInterceptor())

        bus.registry.register("psi", psi_agent)
        bus.registry.register("forge", forge_agent)

        result = await bus.dispatch(BusMessage(
            source="cli",
            target="psi",
            payload=problem,
        ))
    """

    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self._interceptors: list[Interceptor] = []
        self.registry = registry or AgentRegistry()
        self._fallbacks: dict[str, Callable[[BusMessage[Any, Any]], Any]] = {}

    def register_interceptor(self, interceptor: Interceptor) -> None:
        """
        Add an interceptor to the bus.

        Interceptors are sorted by order (ascending) after registration.
        """
        self._interceptors.append(interceptor)
        self._interceptors.sort(key=lambda i: i.order)

    def unregister_interceptor(self, name: str) -> bool:
        """Remove interceptor by name. Returns True if found."""
        for i, interceptor in enumerate(self._interceptors):
            if interceptor.name == name:
                self._interceptors.pop(i)
                return True
        return False

    def register_fallback(
        self, target: str, fallback: Callable[[BusMessage[Any, Any]], Any]
    ) -> None:
        """
        Register a fallback handler for when target is blocked.

        The fallback receives the blocked message and returns
        a default value.
        """
        self._fallbacks[target] = fallback

    def list_interceptors(self) -> list[str]:
        """List registered interceptor names in execution order."""
        return [i.name for i in self._interceptors]

    async def dispatch(self, msg: BusMessage[A, B]) -> DispatchResult[B]:
        """
        Dispatch a message through the bus.

        Flow:
        1. Run interceptors' before() hooks (in order)
        2. If blocked, return fallback or None
        3. Dispatch to target agent
        4. Run interceptors' after() hooks (in reverse order)
        5. Return final result
        """
        start_time = datetime.now(timezone.utc)
        interceptors_run: list[str] = []
        metadata: dict[str, Any] = {}

        # Phase 1: Run before() hooks
        current_msg = msg
        for interceptor in self._interceptors:
            current_msg = await interceptor.before(current_msg)
            interceptors_run.append(f"{interceptor.name}:before")

            if current_msg.blocked:
                # Message blocked - try fallback
                duration_ms = (
                    datetime.now(timezone.utc) - start_time
                ).total_seconds() * 1000

                fallback = self._fallbacks.get(msg.target)
                if fallback:
                    fallback_value = fallback(current_msg)
                    return DispatchResult(
                        value=fallback_value,
                        blocked=True,
                        block_reason=current_msg.block_reason,
                        metadata=metadata,
                        duration_ms=duration_ms,
                        interceptors_run=interceptors_run,
                    )

                return DispatchResult(
                    value=None,
                    blocked=True,
                    block_reason=current_msg.block_reason,
                    metadata=metadata,
                    duration_ms=duration_ms,
                    interceptors_run=interceptors_run,
                )

        # Phase 2: Dispatch to target
        try:
            result = await self.registry.invoke(current_msg.target, current_msg.payload)
        except KeyError as e:
            duration_ms = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds() * 1000
            return DispatchResult(
                value=None,
                blocked=True,
                block_reason=f"Target not found: {current_msg.target}",
                metadata={"error": str(e)},
                duration_ms=duration_ms,
                interceptors_run=interceptors_run,
            )
        except Exception as e:
            duration_ms = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds() * 1000
            return DispatchResult(
                value=None,
                blocked=True,
                block_reason=f"Invocation failed: {type(e).__name__}: {e}",
                metadata={"error": str(e), "error_type": type(e).__name__},
                duration_ms=duration_ms,
                interceptors_run=interceptors_run,
            )

        # Phase 3: Run after() hooks in reverse order
        current_result = result
        for interceptor in reversed(self._interceptors):
            interceptor_result = await interceptor.after(current_msg, current_result)
            interceptors_run.append(f"{interceptor.name}:after")
            current_result = interceptor_result.value
            metadata.update(interceptor_result.metadata)

        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        return DispatchResult(
            value=current_result,
            blocked=False,
            metadata=metadata,
            duration_ms=duration_ms,
            interceptors_run=interceptors_run,
        )

    async def send(
        self,
        source: str,
        target: str,
        payload: A,
        priority: MessagePriority = MessagePriority.NORMAL,
        context: dict[str, Any] | None = None,
    ) -> DispatchResult[B]:
        """
        Convenience method to create and dispatch a message.

        Example:
            result = await bus.send("cli", "psi", problem)
        """
        msg: BusMessage[A, B] = BusMessage(
            source=source,
            target=target,
            payload=payload,
            priority=priority,
            context=context or {},
        )
        return await self.dispatch(msg)


# --- Factory functions ---


def create_bus(*interceptors: Interceptor) -> MiddlewareBus:
    """
    Create a bus with the given interceptors.

    Example:
        bus = create_bus(
            MeteringInterceptor(),
            SafetyInterceptor(),
            TelemetryInterceptor(),
        )
    """
    bus = MiddlewareBus()
    for interceptor in interceptors:
        bus.register_interceptor(interceptor)
    return bus


# --- Example interceptors for testing ---


class LoggingInterceptor(BaseInterceptor):
    """
    Simple logging interceptor for debugging.

    Logs all messages passing through the bus.
    """

    def __init__(self) -> None:
        super().__init__("logging", order=999)
        self.log: list[dict[str, Any]] = []

    async def before(self, msg: BusMessage[Any, Any]) -> BusMessage[Any, Any]:
        self.log.append(
            {
                "phase": "before",
                "message_id": msg.message_id,
                "source": msg.source,
                "target": msg.target,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return msg

    async def after(
        self, msg: BusMessage[Any, Any], result: Any
    ) -> InterceptorResult[Any]:
        self.log.append(
            {
                "phase": "after",
                "message_id": msg.message_id,
                "source": msg.source,
                "target": msg.target,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return InterceptorResult(value=result)


class BlockingInterceptor(BaseInterceptor):
    """
    Interceptor that blocks messages matching a predicate.

    For testing and demonstrating the block mechanism.
    """

    def __init__(
        self,
        name: str,
        predicate: Callable[[BusMessage[Any, Any]], bool],
        reason: str = "Blocked by policy",
        order: int = 0,
    ) -> None:
        super().__init__(name, order)
        self._predicate = predicate
        self._reason = reason

    async def before(self, msg: BusMessage[Any, Any]) -> BusMessage[Any, Any]:
        if self._predicate(msg):
            msg.block(self._reason)
        return msg
