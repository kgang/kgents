"""
Adapters: Transform agent runtime data to widget states.

Live data adapters bridge the gap between:
- Agent runtime (Kgent, SoulState, etc.) → Widget state (AgentCardState, etc.)
- Agent invocations → YieldCardState
- Multiple agents → DashboardScreenState

Key insight: Adapters are pure functions. Same input → same output.
They don't fetch data; they transform data you give them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol, Sequence

from agents.i.reactive.primitives.agent_card import AgentCardState
from agents.i.reactive.primitives.yield_card import YieldCardState
from agents.i.reactive.screens.dashboard import DashboardScreenState
from agents.i.reactive.signal import Signal

if TYPE_CHECKING:
    from agents.i.reactive.primitives.glyph import Phase


# === Protocols for Input Types ===


class SoulLike(Protocol):
    """Protocol for objects that look like KgentSoul."""

    @property
    def active_mode(self) -> Any:
        """Get active dialogue mode."""
        ...

    def manifest(self) -> Any:
        """Get soul state."""
        ...

    def manifest_brief(self) -> dict[str, Any]:
        """Get brief state."""
        ...


class AgentRuntimeLike(Protocol):
    """Protocol for objects that look like agent runtime."""

    @property
    def id(self) -> str:
        """Agent ID."""
        ...

    @property
    def name(self) -> str:
        """Agent name."""
        ...

    @property
    def status(self) -> str:
        """Agent status."""
        ...


class InvocationLike(Protocol):
    """Protocol for objects that look like agent invocations/yields."""

    @property
    def id(self) -> str:
        """Invocation ID."""
        ...

    @property
    def content(self) -> str:
        """Invocation content."""
        ...


# === Helper Functions ===


def _status_to_phase(status: str) -> "Phase":
    """Map status strings to Phase type."""
    mapping: dict[str, "Phase"] = {
        "idle": "idle",
        "running": "active",
        "active": "active",
        "waiting": "waiting",
        "paused": "waiting",
        "error": "error",
        "failed": "error",
        "yielding": "yielding",
        "yielded": "yielding",
        "thinking": "thinking",
        "processing": "thinking",
        "complete": "complete",
        "completed": "complete",
        "done": "complete",
    }
    return mapping.get(status.lower(), "idle")


def _mode_to_phase(mode: str | Any) -> "Phase":
    """Map dialogue modes to Phase type."""
    mode_str = str(mode).lower() if hasattr(mode, "__str__") else "idle"

    if "challenge" in mode_str:
        return "active"
    elif "reflect" in mode_str:
        return "thinking"
    elif "advise" in mode_str:
        return "active"
    elif "explore" in mode_str:
        return "thinking"
    else:
        return "idle"


# === Soul Adapter ===


@dataclass
class SoulAdapter:
    """
    Adapter: SoulState → AgentCardState

    Transforms K-gent soul state into a visual representation.

    Example:
        adapter = SoulAdapter()
        soul = KgentSoul()

        card_state = adapter.adapt(
            soul.manifest(),
            t=clock.state.value.t,
            entropy=0.2,
        )

        widget = AgentCardWidget(card_state)
    """

    # Default ID and name if not provided
    default_id: str = "kgent"
    default_name: str = "Kent"

    # Activity history window
    activity_window: int = 20

    # Internal activity tracking
    _activity_history: list[float] = field(default_factory=list)

    def adapt(
        self,
        soul_state: Any,
        t: float = 0.0,
        entropy: float = 0.0,
        seed: int = 0,
    ) -> AgentCardState:
        """
        Adapt soul state to AgentCardState.

        Args:
            soul_state: SoulState or dict from soul.manifest()
            t: Current time in milliseconds
            entropy: Visual entropy (0.0-1.0)
            seed: Deterministic seed

        Returns:
            AgentCardState for rendering
        """
        # Handle different input types
        if hasattr(soul_state, "active_mode"):
            # It's a SoulState object
            mode = (
                str(soul_state.active_mode.value)
                if hasattr(soul_state.active_mode, "value")
                else str(soul_state.active_mode)
            )
            phase = _mode_to_phase(mode)
            interactions = getattr(soul_state, "interactions_count", 0)
            name = getattr(soul_state, "session_id", None) or self.default_name
        elif isinstance(soul_state, dict):
            # It's a dict from manifest_brief()
            mode = soul_state.get("mode", "idle")
            phase = _mode_to_phase(mode)
            interactions = soul_state.get("session_interactions", 0)
            name = self.default_name
        else:
            # Unknown type, use defaults
            phase = "idle"
            interactions = 0
            name = self.default_name

        # Calculate activity from interactions (normalized 0-1)
        activity = min(1.0, interactions / 10.0) if interactions else 0.0

        # Track activity history
        self._activity_history.append(activity)
        if len(self._activity_history) > self.activity_window:
            self._activity_history = self._activity_history[-self.activity_window :]

        # Capability = health/readiness
        capability = 1.0 if phase != "error" else 0.3

        return AgentCardState(
            agent_id=self.default_id,
            name=name,
            phase=phase,
            activity=tuple(self._activity_history),
            capability=capability,
            entropy=entropy,
            seed=seed,
            t=t,
            style="full",
            breathing=phase == "active",
        )

    def adapt_brief(
        self,
        brief: dict[str, Any],
        t: float = 0.0,
        entropy: float = 0.0,
        seed: int = 0,
    ) -> AgentCardState:
        """Adapt from manifest_brief() output."""
        return self.adapt(brief, t, entropy, seed)


# === Agent Runtime Adapter ===


@dataclass
class AgentRuntimeAdapter:
    """
    Adapter: Agent runtime data → AgentCardState

    Transforms generic agent runtime data into visual representation.

    Example:
        adapter = AgentRuntimeAdapter()

        # From dict
        card_state = adapter.adapt({
            "id": "agent-1",
            "name": "Helper",
            "status": "running",
        })

        # From runtime object
        card_state = adapter.adapt(agent_runtime)
    """

    # Activity history per agent
    _activity: dict[str, list[float]] = field(default_factory=dict)
    activity_window: int = 20

    def adapt(
        self,
        agent_data: dict[str, Any] | AgentRuntimeLike,
        t: float = 0.0,
        entropy: float = 0.0,
        seed: int = 0,
    ) -> AgentCardState:
        """
        Adapt agent data to AgentCardState.

        Args:
            agent_data: Dict or protocol-compatible object with agent info
            t: Current time in milliseconds
            entropy: Visual entropy
            seed: Deterministic seed

        Returns:
            AgentCardState for rendering
        """
        # Extract data
        if isinstance(agent_data, dict):
            agent_id = agent_data.get("id", agent_data.get("agent_id", "unknown"))
            name = agent_data.get("name", agent_id)
            status = agent_data.get("status", agent_data.get("phase", "idle"))
            activity_value = agent_data.get("activity", 0.5)
            capability = agent_data.get("capability", agent_data.get("health", 1.0))
        else:
            agent_id = getattr(agent_data, "id", "unknown")
            name = getattr(agent_data, "name", agent_id)
            status = getattr(agent_data, "status", "idle")
            activity_value = getattr(agent_data, "activity", 0.5)
            capability = getattr(agent_data, "capability", 1.0)

        # Normalize values
        agent_id = str(agent_id)
        name = str(name)
        phase = _status_to_phase(str(status))

        # Track activity history for this agent
        if agent_id not in self._activity:
            self._activity[agent_id] = []

        self._activity[agent_id].append(float(activity_value))
        if len(self._activity[agent_id]) > self.activity_window:
            self._activity[agent_id] = self._activity[agent_id][-self.activity_window :]

        # Handle capability that might be None
        cap_value = 1.0 if capability is None else float(capability)

        return AgentCardState(
            agent_id=agent_id,
            name=name,
            phase=phase,
            activity=tuple(self._activity[agent_id]),
            capability=max(0.0, min(1.0, cap_value)),
            entropy=max(0.0, min(1.0, entropy)),
            seed=seed + hash(agent_id) % 1000,
            t=t,
            style="full",
            breathing=phase == "active",
        )

    def adapt_many(
        self,
        agents: Sequence[dict[str, Any] | AgentRuntimeLike],
        t: float = 0.0,
        entropy: float = 0.0,
        seed: int = 0,
    ) -> tuple[AgentCardState, ...]:
        """Adapt multiple agents."""
        return tuple(self.adapt(agent, t, entropy, seed + i) for i, agent in enumerate(agents))


# === Yield Adapter ===


@dataclass
class YieldAdapter:
    """
    Adapter: Agent yields/invocations → YieldCardState

    Transforms agent output yields into visual yield cards.

    Example:
        adapter = YieldAdapter()

        yield_state = adapter.adapt({
            "id": "yield-1",
            "content": "Processing complete",
            "type": "artifact",
            "source": "agent-1",
        })
    """

    # Counter for auto-generated IDs
    _yield_counter: int = 0

    def adapt(
        self,
        yield_data: dict[str, Any] | InvocationLike,
        t: float = 0.0,
        entropy: float = 0.0,
        seed: int = 0,
    ) -> YieldCardState:
        """
        Adapt yield data to YieldCardState.

        Args:
            yield_data: Dict or protocol-compatible object with yield info
            t: Current time
            entropy: Visual entropy
            seed: Deterministic seed

        Returns:
            YieldCardState for rendering
        """
        self._yield_counter += 1

        # Extract data
        if isinstance(yield_data, dict):
            yield_id = yield_data.get(
                "id", yield_data.get("yield_id", f"yield-{self._yield_counter}")
            )
            content = yield_data.get("content", yield_data.get("message", ""))
            yield_type = yield_data.get("type", yield_data.get("yield_type", "observation"))
            source_agent = yield_data.get("source", yield_data.get("source_agent", ""))
            importance = yield_data.get("importance", 0.5)
            timestamp = yield_data.get("timestamp")
        else:
            yield_id = getattr(yield_data, "id", f"yield-{self._yield_counter}")
            content = getattr(yield_data, "content", "")
            yield_type = getattr(yield_data, "type", "observation")
            source_agent = getattr(yield_data, "source", "")
            importance = getattr(yield_data, "importance", 0.5)
            timestamp = getattr(yield_data, "timestamp", None)

        # Normalize types
        yield_type_str = str(yield_type).lower()
        type_mapping = {
            "artifact": "artifact",
            "observation": "observation",
            "action": "action",
            "thought": "thought",
            "question": "question",
            "error": "error",
            "warning": "warning",
            "info": "observation",
            "result": "artifact",
            "output": "artifact",
            "debug": "thought",
        }
        normalized_type = type_mapping.get(yield_type_str, "observation")

        # Handle timestamp (convert to float milliseconds)
        if timestamp is None:
            timestamp_float = t  # Use current animation time
        elif isinstance(timestamp, datetime):
            timestamp_float = timestamp.timestamp() * 1000  # Convert to ms
        elif isinstance(timestamp, (int, float)):
            timestamp_float = float(timestamp)
        else:
            # Try to parse as ISO string
            try:
                timestamp_float = datetime.fromisoformat(str(timestamp)).timestamp() * 1000
            except (ValueError, TypeError):
                timestamp_float = t

        return YieldCardState(
            yield_id=str(yield_id),
            source_agent=str(source_agent),
            yield_type=normalized_type,  # type: ignore[arg-type]
            content=str(content),
            importance=max(0.0, min(1.0, float(importance))),
            timestamp=timestamp_float,
            entropy=max(0.0, min(1.0, entropy)),
            seed=seed + self._yield_counter,
            t=t,
            max_content_length=200,
            use_emoji=True,
        )

    def adapt_many(
        self,
        yields: Sequence[dict[str, Any] | InvocationLike],
        t: float = 0.0,
        entropy: float = 0.0,
        seed: int = 0,
    ) -> tuple[YieldCardState, ...]:
        """Adapt multiple yields."""
        return tuple(self.adapt(y, t, entropy, seed + i) for i, y in enumerate(yields))


# === Dashboard State Builder ===


def create_dashboard_state(
    agents: list[dict[str, Any]] | None = None,
    yields: list[dict[str, Any]] | None = None,
    t: float = 0.0,
    entropy: float = 0.0,
    seed: int = 0,
    width: int = 80,
    height: int = 24,
    show_density_field: bool = True,
) -> DashboardScreenState:
    """
    Create a DashboardScreenState from raw data.

    Convenience function that combines all adapters.

    Args:
        agents: List of agent data dicts
        yields: List of yield data dicts
        t: Current time
        entropy: Visual entropy
        seed: Deterministic seed
        width: Dashboard width
        height: Dashboard height
        show_density_field: Show activity heat map

    Returns:
        DashboardScreenState ready for rendering

    Example:
        state = create_dashboard_state(
            agents=[
                {"id": "agent-1", "name": "Alpha", "status": "active"},
                {"id": "agent-2", "name": "Beta", "status": "idle"},
            ],
            yields=[
                {"content": "Task complete", "type": "artifact"},
            ],
            t=clock.state.value.t,
        )

        dashboard = DashboardScreen(state)
    """
    agent_adapter = AgentRuntimeAdapter()
    yield_adapter = YieldAdapter()

    agent_states = agent_adapter.adapt_many(agents or [], t, entropy, seed)
    yield_states = yield_adapter.adapt_many(yields or [], t, entropy, seed + 1000)

    return DashboardScreenState(
        agents=agent_states,
        yields=yield_states,
        width=width,
        height=height,
        cards_per_row=2,
        max_yields_shown=5,
        t=t,
        entropy=entropy,
        seed=seed,
        show_density_field=show_density_field,
        density_field_width=40,
        density_field_height=10,
    )


# === Reactive Dashboard Adapter ===


@dataclass
class ReactiveDashboardAdapter:
    """
    Reactive adapter that maintains state and emits updates.

    Combines all adapters with Signal-based reactivity.

    Example:
        from agents.i.reactive.signal import Signal
        from agents.i.reactive.wiring.clock import create_clock

        clock = create_clock()
        adapter = ReactiveDashboardAdapter()

        # Connect to clock
        adapter.connect_clock(clock)

        # Add agents
        adapter.add_agent({"id": "agent-1", "name": "Test", "status": "active"})

        # Subscribe to state changes
        adapter.state.subscribe(lambda s: render_dashboard(s))
    """

    state: "Signal[DashboardScreenState]" = field(
        default_factory=lambda: Signal.of(DashboardScreenState())
    )

    # Internal adapters
    _agent_adapter: AgentRuntimeAdapter = field(default_factory=AgentRuntimeAdapter)
    _yield_adapter: YieldAdapter = field(default_factory=YieldAdapter)

    # Tracked data
    _agents: dict[str, dict[str, Any]] = field(default_factory=dict)
    _yields: list[dict[str, Any]] = field(default_factory=list)

    # Configuration
    _max_yields: int = 100
    _entropy: float = 0.0
    _seed: int = 0

    # Clock subscription cleanup
    _clock_unsub: Any = None

    def connect_clock(self, clock: Any) -> None:
        """
        Connect to a Clock for time updates.

        Args:
            clock: Clock instance
        """
        from agents.i.reactive.wiring.clock import Clock

        if isinstance(clock, Clock):
            # Disconnect existing
            if self._clock_unsub:
                self._clock_unsub()

            def on_tick(clock_state: Any) -> None:
                self._rebuild(clock_state.t, clock_state.seed)

            self._clock_unsub = clock.subscribe(on_tick)

    def disconnect_clock(self) -> None:
        """Disconnect from clock."""
        if self._clock_unsub:
            self._clock_unsub()
            self._clock_unsub = None

    def add_agent(self, agent_data: dict[str, Any]) -> None:
        """Add or update an agent."""
        agent_id = agent_data.get("id", agent_data.get("agent_id", "unknown"))
        self._agents[str(agent_id)] = agent_data
        self._rebuild()

    def remove_agent(self, agent_id: str) -> None:
        """Remove an agent."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            self._rebuild()

    def push_yield(self, yield_data: dict[str, Any]) -> None:
        """Push a new yield."""
        self._yields.insert(0, yield_data)
        if len(self._yields) > self._max_yields:
            self._yields = self._yields[: self._max_yields]
        self._rebuild()

    def clear_yields(self) -> None:
        """Clear all yields."""
        self._yields.clear()
        self._rebuild()

    def set_entropy(self, entropy: float) -> None:
        """Set visual entropy."""
        self._entropy = max(0.0, min(1.0, entropy))
        self._rebuild()

    def _rebuild(self, t: float | None = None, seed: int | None = None) -> None:
        """Rebuild dashboard state."""
        current = self.state.value
        t = t if t is not None else current.t
        seed = seed if seed is not None else self._seed

        new_state = create_dashboard_state(
            agents=list(self._agents.values()),
            yields=self._yields,
            t=t,
            entropy=self._entropy,
            seed=seed,
            width=current.width,
            height=current.height,
            show_density_field=current.show_density_field,
        )

        self.state.set(new_state)

    def snapshot(self) -> DashboardScreenState:
        """Get immutable snapshot of current state."""
        return self.state.value
