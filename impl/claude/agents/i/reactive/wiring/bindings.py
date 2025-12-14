"""
AGENTESE Bindings: Connect reactive screens to live AGENTESE paths.

The binding system bridges AGENTESE paths to reactive widgets:
- self.soul.* → AgentCardState updates
- world.agents.* → DashboardScreen agent list
- Yields from agent execution → YieldCard stream

Key insight: Bindings are declarative. You specify WHAT to bind,
the system handles HOW to propagate updates.

"The screen is the story. Reality wiring makes the story live."
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from agents.i.reactive.signal import Signal
from agents.i.reactive.wiring.adapters import (
    AgentRuntimeAdapter,
    SoulAdapter,
    YieldAdapter,
)
from agents.i.reactive.wiring.subscriptions import Event, EventBus, EventType

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from protocols.agentese.logos import Logos

T = TypeVar("T")


class BindingMode(Enum):
    """How the binding synchronizes data."""

    POLL = auto()  # Poll path at intervals
    PUSH = auto()  # Receive push notifications
    HYBRID = auto()  # Push with poll fallback


@dataclass(frozen=True)
class BindingConfig:
    """Configuration for an AGENTESE binding."""

    # Path pattern (e.g., "self.soul", "world.agents.*")
    path_pattern: str

    # How often to poll (if POLL or HYBRID mode)
    poll_interval_ms: float = 1000.0

    # Mode
    mode: BindingMode = BindingMode.HYBRID

    # Transform function (path result → widget state)
    transform: str = "auto"  # "auto", "soul", "agent", "yield"

    # Whether binding is enabled
    enabled: bool = True


@dataclass
class PathBinding(Generic[T]):
    """
    A binding between an AGENTESE path and a Signal.

    When the AGENTESE path value changes, the Signal is updated.

    Example:
        logos = create_logos()
        observer = create_observer()

        # Bind self.soul.manifest to a signal
        binding = PathBinding.create(
            path="self.soul.manifest",
            logos=logos,
            observer=observer,
        )

        # Subscribe to updates
        binding.signal.subscribe(lambda state: print(f"Soul: {state}"))

        # Start polling
        await binding.start()
    """

    path: str
    logos: "Logos"
    observer: "Umwelt[Any, Any]"
    signal: Signal[T | None]
    config: BindingConfig

    # Internal state
    _running: bool = field(default=False)
    _task: asyncio.Task[None] | None = field(default=None)
    _last_value: T | None = field(default=None)
    _poll_count: int = field(default=0)

    @classmethod
    def create(
        cls,
        path: str,
        logos: "Logos",
        observer: "Umwelt[Any, Any]",
        config: BindingConfig | None = None,
    ) -> PathBinding[Any]:
        """
        Create a new path binding.

        Args:
            path: AGENTESE path to bind
            logos: Logos resolver instance
            observer: Observer Umwelt for invocations
            config: Optional binding configuration

        Returns:
            PathBinding ready to start
        """
        cfg = config or BindingConfig(path_pattern=path)

        return cls(
            path=path,
            logos=logos,
            observer=observer,
            signal=Signal.of(None),
            config=cfg,
        )

    async def poll_once(self) -> T | None:
        """
        Poll the path once and update signal.

        Returns:
            The result from the path invocation
        """
        try:
            result = await self.logos.invoke(self.path, self.observer)
            self._last_value = result
            self.signal.set(result)
            self._poll_count += 1
            return result  # type: ignore[no-any-return]  # Result type is dynamic
        except Exception:
            # Log error but don't crash
            self._last_value = None
            self.signal.set(None)
            return None

    async def start(self) -> None:
        """Start the binding (begin polling/listening)."""
        if self._running:
            return

        self._running = True

        if self.config.mode in (BindingMode.POLL, BindingMode.HYBRID):
            self._task = asyncio.create_task(self._poll_loop())

    async def stop(self) -> None:
        """Stop the binding."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _poll_loop(self) -> None:
        """Internal polling loop."""
        while self._running and self.config.enabled:
            await self.poll_once()
            await asyncio.sleep(self.config.poll_interval_ms / 1000.0)

    @property
    def is_running(self) -> bool:
        """Whether binding is actively running."""
        return self._running

    @property
    def poll_count(self) -> int:
        """Number of successful polls."""
        return self._poll_count


@dataclass
class AGENTESEBinding:
    """
    High-level AGENTESE binding manager.

    Manages multiple path bindings and coordinates updates
    to the reactive substrate.

    Example:
        logos = create_logos()
        observer = create_observer()
        clock = create_clock()
        event_bus = create_event_bus()

        binding = create_binding(logos, observer, event_bus)

        # Bind soul state
        binding.bind_soul("self.soul")

        # Bind agent list
        binding.bind_agents("world.agents")

        # Start all bindings
        await binding.start_all()

        # Get dashboard state
        dashboard_state = binding.to_dashboard_state(clock.state.value.t)
    """

    logos: "Logos"
    observer: "Umwelt[Any, Any]"
    event_bus: EventBus

    # Path bindings
    _bindings: dict[str, PathBinding[Any]] = field(default_factory=dict)

    # Specialized adapters
    _soul_adapter: SoulAdapter = field(default_factory=SoulAdapter)
    _agent_adapter: AgentRuntimeAdapter = field(default_factory=AgentRuntimeAdapter)
    _yield_adapter: YieldAdapter = field(default_factory=YieldAdapter)

    # Cached state
    _soul_path: str | None = field(default=None)
    _agents_path: str | None = field(default=None)
    _yields: list[dict[str, Any]] = field(default_factory=list)
    _max_yields: int = 100

    # Entropy configuration
    _entropy: float = 0.0
    _seed: int = 0

    def bind(
        self,
        path: str,
        config: BindingConfig | None = None,
    ) -> PathBinding[Any]:
        """
        Create a generic path binding.

        Args:
            path: AGENTESE path to bind
            config: Optional configuration

        Returns:
            The created PathBinding
        """
        cfg = config or BindingConfig(path_pattern=path)
        binding: PathBinding[Any] = PathBinding.create(
            path, self.logos, self.observer, cfg
        )
        self._bindings[path] = binding
        return binding

    def bind_soul(
        self,
        base_path: str = "self.soul",
        poll_interval_ms: float = 500.0,
    ) -> PathBinding[Any]:
        """
        Bind soul state for AgentCard display.

        Args:
            base_path: Base AGENTESE path for soul
            poll_interval_ms: How often to poll

        Returns:
            PathBinding for soul state
        """
        self._soul_path = f"{base_path}.manifest"

        config = BindingConfig(
            path_pattern=self._soul_path,
            poll_interval_ms=poll_interval_ms,
            mode=BindingMode.POLL,
            transform="soul",
        )

        binding = self.bind(self._soul_path, config)

        # Wire to event bus
        binding.signal.subscribe(lambda state: self._on_soul_update(state))

        return binding

    def bind_agents(
        self,
        base_path: str = "world.agents",
        poll_interval_ms: float = 1000.0,
    ) -> PathBinding[Any]:
        """
        Bind agent list for Dashboard display.

        Args:
            base_path: Base AGENTESE path for agents
            poll_interval_ms: How often to poll

        Returns:
            PathBinding for agent list
        """
        self._agents_path = f"{base_path}.manifest"

        config = BindingConfig(
            path_pattern=self._agents_path,
            poll_interval_ms=poll_interval_ms,
            mode=BindingMode.POLL,
            transform="agent",
        )

        binding = self.bind(self._agents_path, config)

        # Wire to event bus
        binding.signal.subscribe(lambda state: self._on_agents_update(state))

        return binding

    def push_yield(self, yield_data: dict[str, Any]) -> None:
        """
        Push a yield from agent execution.

        Args:
            yield_data: Yield data dict
        """
        self._yields.insert(0, yield_data)
        if len(self._yields) > self._max_yields:
            self._yields = self._yields[: self._max_yields]

        # Emit event
        self.event_bus.publish(
            Event(
                type=EventType.YIELD_CREATED,
                payload=yield_data,
                source_id="agentese_binding",
            )
        )

    def clear_yields(self) -> None:
        """Clear all yields."""
        self._yields.clear()

    async def start_all(self) -> None:
        """Start all bindings."""
        for binding in self._bindings.values():
            await binding.start()

    async def stop_all(self) -> None:
        """Stop all bindings."""
        for binding in self._bindings.values():
            await binding.stop()

    async def poll_all(self) -> dict[str, Any]:
        """
        Poll all bindings once.

        Returns:
            Dict of path → result
        """
        results: dict[str, Any] = {}
        for path, binding in self._bindings.items():
            results[path] = await binding.poll_once()
        return results

    def _on_soul_update(self, state: Any) -> None:
        """Handle soul state update."""
        if state is not None:
            self.event_bus.publish(
                Event(
                    type=EventType.AGENT_STATE_CHANGED,
                    payload={"source": "soul", "state": state},
                    source_id="agentese_binding",
                )
            )

    def _on_agents_update(self, state: Any) -> None:
        """Handle agents list update."""
        if state is not None:
            self.event_bus.publish(
                Event(
                    type=EventType.DASHBOARD_REFRESH,
                    payload={"source": "agents", "state": state},
                    source_id="agentese_binding",
                )
            )

    def get_soul_state(self) -> Any | None:
        """Get current soul state (if bound)."""
        if self._soul_path and self._soul_path in self._bindings:
            return self._bindings[self._soul_path].signal.value
        return None

    def get_agents_state(self) -> Any | None:
        """Get current agents state (if bound)."""
        if self._agents_path and self._agents_path in self._bindings:
            return self._bindings[self._agents_path].signal.value
        return None

    def set_entropy(self, entropy: float) -> None:
        """Set visual entropy for all adapters."""
        self._entropy = max(0.0, min(1.0, entropy))

    def set_seed(self, seed: int) -> None:
        """Set deterministic seed."""
        self._seed = seed

    def to_dashboard_state(
        self,
        t: float = 0.0,
        width: int = 80,
        height: int = 24,
        show_density_field: bool = True,
    ) -> Any:
        """
        Convert current binding state to DashboardScreenState.

        Args:
            t: Current time in milliseconds
            width: Dashboard width
            height: Dashboard height
            show_density_field: Show activity heat map

        Returns:
            DashboardScreenState ready for rendering
        """
        from agents.i.reactive.wiring.adapters import create_dashboard_state

        # Build agent list from bindings
        agents: list[dict[str, Any]] = []

        # Add soul as agent if bound
        soul_state = self.get_soul_state()
        if soul_state is not None:
            # Transform soul state to agent-like dict
            if hasattr(soul_state, "to_dict"):
                soul_dict = soul_state.to_dict()
            elif isinstance(soul_state, dict):
                soul_dict = soul_state
            else:
                soul_dict = {"id": "kgent", "name": "Kent", "status": "active"}

            agents.append(
                {
                    "id": soul_dict.get("agent_id", "kgent"),
                    "name": soul_dict.get("name", "Kent"),
                    "status": _extract_status(soul_dict),
                }
            )

        # Add agents from agents binding
        agents_state = self.get_agents_state()
        if agents_state is not None:
            if isinstance(agents_state, (list, tuple)):
                for agent in agents_state:
                    if isinstance(agent, dict):
                        agents.append(agent)
            elif isinstance(agents_state, dict):
                # Could be a dict of agents
                if "agents" in agents_state:
                    for agent in agents_state["agents"]:
                        if isinstance(agent, dict):
                            agents.append(agent)

        return create_dashboard_state(
            agents=agents,
            yields=self._yields,
            t=t,
            entropy=self._entropy,
            seed=self._seed,
            width=width,
            height=height,
            show_density_field=show_density_field,
        )

    @property
    def binding_count(self) -> int:
        """Number of active bindings."""
        return len(self._bindings)

    @property
    def running_count(self) -> int:
        """Number of running bindings."""
        return sum(1 for b in self._bindings.values() if b.is_running)


def _extract_status(data: dict[str, Any]) -> str:
    """Extract status from various dict formats."""
    if "status" in data:
        return str(data["status"])
    if "phase" in data:
        return str(data["phase"])
    if "mode" in data:
        mode = str(data["mode"]).lower()
        if "challenge" in mode or "active" in mode:
            return "active"
        if "reflect" in mode or "thinking" in mode:
            return "thinking"
        return "idle"
    return "idle"


def create_binding(
    logos: "Logos",
    observer: "Umwelt[Any, Any]",
    event_bus: EventBus | None = None,
) -> AGENTESEBinding:
    """
    Create an AGENTESE binding manager.

    Args:
        logos: Logos resolver instance
        observer: Observer Umwelt
        event_bus: Optional event bus (creates new if None)

    Returns:
        Configured AGENTESEBinding
    """
    from agents.i.reactive.wiring.subscriptions import create_event_bus

    bus = event_bus or create_event_bus()

    return AGENTESEBinding(
        logos=logos,
        observer=observer,
        event_bus=bus,
    )


# === Declarative Binding DSL ===


@dataclass
class BindingSpec:
    """
    Declarative specification for bindings.

    Allows defining bindings in a config-like way.
    """

    soul_path: str | None = None
    agents_path: str | None = None
    yield_patterns: list[str] = field(default_factory=list)
    poll_interval_ms: float = 500.0
    entropy: float = 0.0
    seed: int = 42


async def apply_binding_spec(
    spec: BindingSpec,
    logos: "Logos",
    observer: "Umwelt[Any, Any]",
    event_bus: EventBus | None = None,
) -> AGENTESEBinding:
    """
    Apply a binding specification.

    Args:
        spec: Binding specification
        logos: Logos resolver
        observer: Observer Umwelt
        event_bus: Optional event bus

    Returns:
        Configured and started AGENTESEBinding
    """
    binding = create_binding(logos, observer, event_bus)

    binding.set_entropy(spec.entropy)
    binding.set_seed(spec.seed)

    if spec.soul_path:
        binding.bind_soul(spec.soul_path, spec.poll_interval_ms)

    if spec.agents_path:
        binding.bind_agents(spec.agents_path, spec.poll_interval_ms)

    await binding.start_all()

    return binding
