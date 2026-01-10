"""
Flow: The core flow agent implementation.

Flow transforms discrete agents into continuous stream processors.
Static: Agent[A, B] - a point transformation (invoke once)
Dynamic: Flow(Agent): dA/dt -> dB/dt - continuous flow (stream processing)

See: spec/f-gents/README.md
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Callable,
    Generic,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from agents.f.config import FlowConfig
from agents.f.polynomial import get_polynomial
from agents.f.state import FlowState

if TYPE_CHECKING:
    from agents.f.polynomial import FlowPolynomial

# Type variables
A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type
A_co = TypeVar("A_co", covariant=True)
B_co = TypeVar("B_co", covariant=True)


@runtime_checkable
class AgentProtocol(Protocol[A_co, B_co]):
    """Protocol for agents that can be lifted to flows."""

    @property
    def name(self) -> str:
        """Agent name."""
        ...

    async def invoke(self, input: Any) -> Any:
        """Invoke the agent."""
        ...


@dataclass
class FlowEvent(Generic[B]):
    """An event in a flow stream."""

    value: B
    timestamp: datetime = field(default_factory=datetime.now)
    event_type: str = "output"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowAgent(Generic[A, B]):
    """
    A flow-lifted agent that processes streams.

    FlowAgent wraps a discrete Agent[A, B] and enables:
    - Continuous stream processing via start()
    - Perturbation injection during streaming
    - State management via polynomial
    - Entropy tracking
    """

    inner: AgentProtocol[A, B]
    config: FlowConfig
    polynomial: FlowPolynomial[FlowState, str, dict[str, Any]]

    # Runtime state
    _state: FlowState = field(default=FlowState.DORMANT)
    _entropy: float = field(default=1.0)
    _perturbation_queue: asyncio.Queue[tuple[A, asyncio.Future[B]]] = field(
        default_factory=asyncio.Queue
    )
    _events_processed: int = 0
    _started_at: datetime | None = None
    _stopped_at: datetime | None = None

    def __post_init__(self) -> None:
        """Initialize entropy from config."""
        self._entropy = self.config.entropy_budget

    @property
    def name(self) -> str:
        """Get agent name."""
        return f"Flow({self.inner.name})"

    @property
    def state(self) -> FlowState:
        """Get current flow state."""
        return self._state

    @property
    def entropy(self) -> float:
        """Get remaining entropy."""
        return self._entropy

    @property
    def is_active(self) -> bool:
        """Check if flow is active."""
        return self._state.is_active()

    async def invoke(self, input: A) -> B:
        """
        Invoke the agent.

        If flow is DORMANT, invoke directly.
        If flow is STREAMING, inject via perturbation queue.
        """
        if self._state == FlowState.DORMANT:
            # Direct invocation when not streaming
            result: B = await self.inner.invoke(input)
            return result
        elif self._state.can_perturb():
            # Perturbation: inject into stream
            return await self._perturb(input)
        else:
            msg = f"Cannot invoke in state {self._state}"
            raise RuntimeError(msg)

    async def _perturb(self, input: A) -> B:
        """
        Inject input via perturbation queue.

        This ensures state integrity - the input goes through
        the stream processor, not bypassing it.
        """
        future: asyncio.Future[B] = asyncio.Future()
        await self._perturbation_queue.put((input, future))
        return await future

    async def start(
        self,
        source: AsyncIterator[A],
    ) -> AsyncIterator[FlowEvent[B]]:
        """
        Start the flow with an input source.

        Args:
            source: Async iterator of inputs

        Yields:
            FlowEvent objects containing outputs
        """
        if self._state != FlowState.DORMANT:
            msg = f"Cannot start in state {self._state}"
            raise RuntimeError(msg)

        self._state = FlowState.STREAMING
        self._started_at = datetime.now()

        try:
            async for input in self._merged_source(source):
                # Check entropy
                if self._entropy <= 0:
                    self._state = FlowState.COLLAPSED
                    break

                # Check max events
                if (
                    self.config.max_events is not None
                    and self._events_processed >= self.config.max_events
                ):
                    self._state = FlowState.DRAINING
                    break

                # Process input
                try:
                    output = await self.inner.invoke(input)
                    self._events_processed += 1
                    self._entropy -= self.config.entropy_decay

                    yield FlowEvent(
                        value=output,
                        event_type="output",
                        metadata={
                            "events_processed": self._events_processed,
                            "entropy_remaining": self._entropy,
                        },
                    )

                    # Feedback loop (ouroboros)
                    if self.config.feedback_fraction > 0:
                        await self._maybe_feedback(output)

                except Exception as e:
                    yield FlowEvent(
                        value=None,  # type: ignore[arg-type]
                        event_type="error",
                        metadata={"error": str(e)},
                    )

        finally:
            self._state = FlowState.COLLAPSED
            self._stopped_at = datetime.now()

    async def _merged_source(
        self,
        primary: AsyncIterator[A],
    ) -> AsyncIterator[A]:
        """
        Merge primary source with perturbation queue.

        Perturbations have priority.
        """
        primary_exhausted = False
        primary_iter = primary.__aiter__()

        while True:
            # Check for perturbations first (priority)
            try:
                input, future = self._perturbation_queue.get_nowait()
                try:
                    result = await self.inner.invoke(input)
                    future.set_result(result)
                except Exception as e:
                    future.set_exception(e)
                continue
            except asyncio.QueueEmpty:
                pass

            # Then try primary source
            if not primary_exhausted:
                try:
                    input = await asyncio.wait_for(
                        primary_iter.__anext__(),
                        timeout=0.1,  # Short timeout to check perturbations
                    )
                    yield input
                except asyncio.TimeoutError:
                    continue
                except StopAsyncIteration:
                    primary_exhausted = True

            if primary_exhausted and self._perturbation_queue.empty():
                break

    async def _maybe_feedback(self, output: B) -> None:
        """Maybe feed output back as input."""
        import random

        if random.random() < self.config.feedback_fraction:
            if self.config.feedback_transform:
                feedback_input = self.config.feedback_transform(output)
            else:
                feedback_input = output  # Feedback B → A is intentional here
            # Queue as low-priority perturbation
            future: asyncio.Future[Any] = asyncio.Future()
            await self._perturbation_queue.put((feedback_input, future))

    async def stop(self) -> None:
        """Stop the flow."""
        if self._state == FlowState.STREAMING:
            self._state = FlowState.DRAINING
        elif self._state == FlowState.DRAINING:
            self._state = FlowState.COLLAPSED

    def reset(self) -> None:
        """Reset the flow to dormant state."""
        self._state = FlowState.DORMANT
        self._entropy = self.config.entropy_budget
        self._events_processed = 0
        self._started_at = None
        self._stopped_at = None
        self._perturbation_queue = asyncio.Queue()


class Flow:
    """
    Factory class for creating flow agents.

    The Flow class provides static methods for lifting agents to flows.
    """

    @staticmethod
    def lift(
        agent: AgentProtocol[A, B],
        config: FlowConfig | None = None,
    ) -> FlowAgent[A, B]:
        """
        Lift a discrete agent to a flow agent.

        Args:
            agent: The agent to lift
            config: Optional flow configuration

        Returns:
            A FlowAgent wrapping the input agent
        """
        if config is None:
            config = FlowConfig()

        polynomial = get_polynomial(config.modality)

        return FlowAgent(
            inner=agent,
            config=config,
            polynomial=polynomial,
        )

    @staticmethod
    def lift_multi(
        agents: dict[str, AgentProtocol[A, B]],
        config: FlowConfig | None = None,
    ) -> FlowAgent[A, B]:
        """
        Lift multiple agents for collaboration.

        Args:
            agents: Dictionary of agent_id -> agent
            config: Optional flow configuration (should have modality="collaboration")

        Returns:
            A FlowAgent configured for multi-agent collaboration
        """
        if config is None:
            config = FlowConfig(modality="collaboration")

        if config.modality != "collaboration":
            config = FlowConfig(**{**config.__dict__, "modality": "collaboration"})

        # Set agent IDs from the provided agents
        config.agents = list(agents.keys())

        # For now, use the first agent as the "primary"
        # Full collaboration logic is in the collaboration modality
        primary_agent = next(iter(agents.values()))

        polynomial = get_polynomial("collaboration")

        flow_agent = FlowAgent(
            inner=primary_agent,
            config=config,
            polynomial=polynomial,
        )

        # Attach the full agent pool for collaboration modality to use
        flow_agent._agent_pool = agents  # type: ignore[attr-defined]

        return flow_agent

    @staticmethod
    async def from_source(
        transform: Callable[[A], B],
        source: AsyncIterator[A],
        config: FlowConfig | None = None,
    ) -> AsyncIterator[FlowEvent[B]]:
        """
        Create a flow directly from a transform function and source.

        Args:
            transform: Function to apply to each input
            source: Input source
            config: Optional configuration

        Yields:
            FlowEvent objects
        """

        class FunctionAgent:
            name = "FunctionAgent"

            async def invoke(self, input: A) -> B:
                return transform(input)

        agent = FunctionAgent()
        flow_agent: FlowAgent[A, B] = Flow.lift(agent, config)

        async for event in flow_agent.start(source):
            yield event


__all__ = [
    "AgentProtocol",
    "FlowEvent",
    "FlowAgent",
    "Flow",
]
