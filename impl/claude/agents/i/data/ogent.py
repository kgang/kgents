"""
O-gent Polling - XYZ Health Monitoring for I-gent.

Polls O-gent for telemetry, semantic, and economic health metrics.

The Three Dimensions:
- X (Telemetry): "Is it running?" - Latency, errors, throughput
- Y (Semantic): "Does it mean what it says?" - Drift, coherence
- Z (Economic): "Is it worth the cost?" - RoC, value ledger

Polling Spec:
- Base interval: 2.2 seconds
- Jitter: ±0.3 seconds (to avoid thundering herd)
- Non-blocking: Uses asyncio

FD3 Integration:
- Can optionally consume health updates from FD3 channel
- When fd3_channel is set, reads "health" messages instead of polling
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Protocol

from .registry import AgentRegistry, RegisteredAgent

if TYPE_CHECKING:
    from protocols.cli.fd3 import FD3Channel, FD3Message


class HealthLevel(Enum):
    """Health level for each dimension."""

    CRITICAL = "CRITICAL"  # 0.0 - 0.2
    POOR = "POOR"  # 0.2 - 0.4
    FAIR = "FAIR"  # 0.4 - 0.6
    GOOD = "GOOD"  # 0.6 - 0.8
    EXCELLENT = "EXCELLENT"  # 0.8 - 1.0


def value_to_health_level(value: float) -> HealthLevel:
    """Convert a 0.0-1.0 value to a health level."""
    if value < 0.2:
        return HealthLevel.CRITICAL
    elif value < 0.4:
        return HealthLevel.POOR
    elif value < 0.6:
        return HealthLevel.FAIR
    elif value < 0.8:
        return HealthLevel.GOOD
    else:
        return HealthLevel.EXCELLENT


@dataclass
class XYZHealth:
    """
    Health metrics across all three dimensions.

    Each dimension is a float from 0.0 to 1.0.
    """

    # Dimension X: Telemetry
    x_telemetry: float = 1.0
    x_latency_ms: float = 0.0
    x_error_rate: float = 0.0
    x_throughput: float = 0.0

    # Dimension Y: Semantic
    y_semantic: float = 1.0
    y_drift: float = 0.0
    y_coherence: float = 1.0

    # Dimension Z: Economic
    z_economic: float = 1.0
    z_roc: float = 0.0  # Return on Cognition
    z_balance: float = 0.0

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def x_level(self) -> HealthLevel:
        """Get telemetry health level."""
        return value_to_health_level(self.x_telemetry)

    @property
    def y_level(self) -> HealthLevel:
        """Get semantic health level."""
        return value_to_health_level(self.y_semantic)

    @property
    def z_level(self) -> HealthLevel:
        """Get economic health level."""
        return value_to_health_level(self.z_economic)

    @property
    def overall(self) -> float:
        """Overall health (geometric mean of dimensions)."""
        result: float = (self.x_telemetry * self.y_semantic * self.z_economic) ** (
            1 / 3
        )
        return result

    @property
    def overall_level(self) -> HealthLevel:
        """Overall health level."""
        return value_to_health_level(self.overall)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "x_telemetry": self.x_telemetry,
            "x_latency_ms": self.x_latency_ms,
            "x_error_rate": self.x_error_rate,
            "x_throughput": self.x_throughput,
            "y_semantic": self.y_semantic,
            "y_drift": self.y_drift,
            "y_coherence": self.y_coherence,
            "z_economic": self.z_economic,
            "z_roc": self.z_roc,
            "z_balance": self.z_balance,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "XYZHealth":
        """Create from dict."""
        return cls(
            x_telemetry=data.get("x_telemetry", 1.0),
            x_latency_ms=data.get("x_latency_ms", 0.0),
            x_error_rate=data.get("x_error_rate", 0.0),
            x_throughput=data.get("x_throughput", 0.0),
            y_semantic=data.get("y_semantic", 1.0),
            y_drift=data.get("y_drift", 0.0),
            y_coherence=data.get("y_coherence", 1.0),
            z_economic=data.get("z_economic", 1.0),
            z_roc=data.get("z_roc", 0.0),
            z_balance=data.get("z_balance", 0.0),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if "timestamp" in data
            else datetime.now(),
        )


# Callback type for health updates
HealthCallback = Callable[[str, XYZHealth], None]


class OgentPoller:
    """
    Polls O-gent for XYZ health metrics.

    Uses a ~2.2 second interval with jitter to avoid thundering herd.
    """

    # Base polling interval in seconds
    BASE_INTERVAL = 2.2
    # Jitter range (±)
    JITTER = 0.3
    # Timeout for individual agent polling
    POLL_TIMEOUT = 5.0

    def __init__(
        self,
        registry: AgentRegistry | None = None,
        interval: float = BASE_INTERVAL,
        jitter: float = JITTER,
        timeout: float = POLL_TIMEOUT,
        fd3_channel: "FD3Channel | None" = None,
    ) -> None:
        self._registry = registry
        self._interval = interval
        self._jitter = jitter
        self._timeout = timeout
        self._fd3_channel = fd3_channel
        self._running = False
        self._task: asyncio.Task[None] | None = None
        self._fd3_task: asyncio.Task[None] | None = None
        self._callbacks: list[HealthCallback] = []
        self._health_cache: dict[str, XYZHealth] = {}
        self._timeout_count: dict[str, int] = {}  # Track timeouts per agent

    def subscribe(self, callback: HealthCallback) -> None:
        """Subscribe to health updates."""
        self._callbacks.append(callback)

    def unsubscribe(self, callback: HealthCallback) -> None:
        """Unsubscribe from health updates."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _emit(self, agent_id: str, health: XYZHealth) -> None:
        """Emit health update to all subscribers."""
        for callback in self._callbacks:
            try:
                callback(agent_id, health)
            except Exception:
                pass  # Don't let one callback break others

    def get_cached_health(self, agent_id: str) -> XYZHealth | None:
        """Get cached health for an agent."""
        return self._health_cache.get(agent_id)

    def _get_jittered_interval(self) -> float:
        """Get the polling interval with random jitter."""
        return self._interval + random.uniform(-self._jitter, self._jitter)

    async def poll_once(self) -> dict[str, XYZHealth]:
        """
        Poll all agents once for health metrics.

        Returns a dict mapping agent_id -> XYZHealth.
        Uses timeout to handle unresponsive agents gracefully.
        """
        results: dict[str, XYZHealth] = {}

        if not self._registry:
            return results

        agents = await self._registry.discover()

        for agent in agents:
            try:
                health = await asyncio.wait_for(
                    self._poll_agent(agent),
                    timeout=self._timeout,
                )
                # Reset timeout counter on success
                self._timeout_count[agent.id] = 0
            except asyncio.TimeoutError:
                # Track timeout and return degraded health
                self._timeout_count[agent.id] = self._timeout_count.get(agent.id, 0) + 1
                health = self._create_timeout_health(agent.id)
            except Exception:
                # Return degraded health on other errors
                health = XYZHealth(
                    x_telemetry=0.3,
                    y_semantic=0.5,
                    z_economic=0.5,
                )

            results[agent.id] = health
            self._health_cache[agent.id] = health
            self._emit(agent.id, health)

        return results

    def _create_timeout_health(self, agent_id: str) -> XYZHealth:
        """Create health object for timed-out agent."""
        timeout_count = self._timeout_count.get(agent_id, 1)
        # Degrade health more with repeated timeouts
        degradation = min(0.9, timeout_count * 0.2)
        return XYZHealth(
            x_telemetry=max(0.1, 1.0 - degradation),
            x_latency_ms=self._timeout * 1000,  # Show timeout as latency
            x_error_rate=degradation,
            y_semantic=max(0.3, 1.0 - degradation * 0.5),
            y_coherence=max(0.3, 1.0 - degradation * 0.5),
            z_economic=max(0.3, 1.0 - degradation * 0.3),
        )

    def get_timeout_count(self, agent_id: str) -> int:
        """Get the number of consecutive timeouts for an agent."""
        return self._timeout_count.get(agent_id, 0)

    async def _poll_agent(self, agent: RegisteredAgent) -> XYZHealth:
        """
        Poll a single agent for health metrics.

        This is where we'd integrate with real O-gent observers.
        For now, we derive health from cached values.
        """
        # If agent has an observable, use it
        if agent.observable:
            try:
                metrics = await agent.observable.metrics()
                activity = await agent.observable.activity_level()

                # Derive health from metrics
                return XYZHealth(
                    x_telemetry=min(
                        1.0, max(0.0, 1.0 - metrics.get("error_rate", 0.0))
                    ),
                    x_latency_ms=metrics.get("latency_ms", 0.0),
                    x_error_rate=metrics.get("error_rate", 0.0),
                    x_throughput=metrics.get("throughput", 0.0),
                    y_semantic=metrics.get("semantic_health", 1.0),
                    y_drift=metrics.get("drift", 0.0),
                    y_coherence=metrics.get("coherence", 1.0),
                    z_economic=metrics.get("economic_health", 1.0),
                    z_roc=metrics.get("roc", 0.0),
                    z_balance=metrics.get("balance", 0.0),
                )
            except Exception:
                # Return degraded health on error
                return XYZHealth(
                    x_telemetry=0.5,
                    y_semantic=0.5,
                    z_economic=0.5,
                )

        # Derive mock health from cached activity level
        # This provides smooth transitions for demo mode
        activity = agent.cached_activity
        phase_multiplier = {
            "ACTIVE": 1.0,
            "WAKING": 0.7,
            "WANING": 0.4,
            "DORMANT": 0.2,
            "VOID": 0.1,
        }.get(agent.cached_phase.value, 0.5)

        base_health = activity * phase_multiplier

        # Add some variation per dimension
        return XYZHealth(
            x_telemetry=min(1.0, base_health + random.uniform(0.0, 0.2)),
            x_latency_ms=max(0.0, (1.0 - base_health) * 100 + random.uniform(0, 50)),
            x_error_rate=max(0.0, (1.0 - base_health) * 0.1),
            x_throughput=base_health * 100,
            y_semantic=min(1.0, base_health + random.uniform(0.0, 0.3)),
            y_drift=max(0.0, (1.0 - base_health) * 0.2),
            y_coherence=min(1.0, base_health + random.uniform(0.1, 0.2)),
            z_economic=min(1.0, base_health + random.uniform(-0.1, 0.2)),
            z_roc=base_health * 2.0 - 1.0,  # -1.0 to 1.0 range
            z_balance=base_health * 1000,  # Arbitrary units
        )

    async def start(self) -> None:
        """Start the polling loop."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._poll_loop())

        # Also start FD3 watcher if channel is configured
        if self._fd3_channel and self._fd3_channel.is_enabled:
            self._fd3_task = asyncio.create_task(self._fd3_watch_loop())

    async def stop(self) -> None:
        """Stop the polling loop."""
        self._running = False

        # Stop FD3 watcher
        if self._fd3_task:
            self._fd3_task.cancel()
            try:
                await self._fd3_task
            except asyncio.CancelledError:
                pass
            self._fd3_task = None

        # Stop poll task
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _poll_loop(self) -> None:
        """The main polling loop."""
        while self._running:
            try:
                await self.poll_once()
            except Exception:
                pass  # Don't let polling errors stop the loop

            # Wait with jitter
            await asyncio.sleep(self._get_jittered_interval())

    async def _fd3_watch_loop(self) -> None:
        """Watch FD3 channel for health updates."""
        if not self._fd3_channel:
            return

        async for msg in self._fd3_channel.watch():
            if not self._running:
                break

            # Process health messages
            if msg.type == "health":
                self._handle_fd3_health(msg)

    def _handle_fd3_health(self, msg: "FD3Message") -> None:
        """Handle a health message from FD3."""
        payload = msg.payload
        agent_id = payload.get("agent_id", "")
        if not agent_id:
            return

        # Create health from FD3 payload
        health = XYZHealth(
            x_telemetry=payload.get("x_telemetry", 1.0),
            x_latency_ms=payload.get("x_latency_ms", 0.0),
            x_error_rate=payload.get("x_error_rate", 0.0),
            x_throughput=payload.get("x_throughput", 0.0),
            y_semantic=payload.get("y_semantic", 1.0),
            y_drift=payload.get("y_drift", 0.0),
            y_coherence=payload.get("y_coherence", 1.0),
            z_economic=payload.get("z_economic", 1.0),
            z_roc=payload.get("z_roc", 0.0),
            z_balance=payload.get("z_balance", 0.0),
        )

        # Cache and emit
        self._health_cache[agent_id] = health
        self._emit(agent_id, health)

    @property
    def is_running(self) -> bool:
        """Whether the poller is running."""
        return self._running

    @property
    def fd3_channel(self) -> "FD3Channel | None":
        """Get the FD3 channel."""
        return self._fd3_channel

    def set_fd3_channel(self, channel: "FD3Channel | None") -> None:
        """Set the FD3 channel."""
        self._fd3_channel = channel


def create_mock_health(
    agent_id: str,
    activity: float = 0.5,
    phase: str = "ACTIVE",
) -> XYZHealth:
    """
    Create mock health metrics for testing.

    Derives health from activity level and phase.
    """
    phase_multiplier = {
        "ACTIVE": 1.0,
        "WAKING": 0.7,
        "WANING": 0.4,
        "DORMANT": 0.2,
        "VOID": 0.1,
    }.get(phase, 0.5)

    base_health = activity * phase_multiplier

    return XYZHealth(
        x_telemetry=min(1.0, base_health + 0.1),
        x_latency_ms=(1.0 - base_health) * 100,
        x_error_rate=(1.0 - base_health) * 0.1,
        x_throughput=base_health * 100,
        y_semantic=min(1.0, base_health + 0.15),
        y_drift=(1.0 - base_health) * 0.2,
        y_coherence=min(1.0, base_health + 0.2),
        z_economic=min(1.0, base_health + 0.05),
        z_roc=base_health * 2.0 - 1.0,
        z_balance=base_health * 1000,
    )


def render_xyz_bar(health: XYZHealth, width: int = 10) -> str:
    """
    Render XYZ health as a compact bar.

    Returns a string like: X[████░░] Y[███░░░] Z[█████░]
    """

    def render_bar(value: float, w: int) -> str:
        filled = int(value * w)
        empty = w - filled
        return "█" * filled + "░" * empty

    x_bar = render_bar(health.x_telemetry, width)
    y_bar = render_bar(health.y_semantic, width)
    z_bar = render_bar(health.z_economic, width)

    return f"X[{x_bar}] Y[{y_bar}] Z[{z_bar}]"


def render_xyz_compact(health: XYZHealth) -> str:
    """
    Render XYZ health as a compact single-line string.

    Returns a string like: X:87% Y:92% Z:78%
    """
    return (
        f"X:{int(health.x_telemetry * 100):2d}% "
        f"Y:{int(health.y_semantic * 100):2d}% "
        f"Z:{int(health.z_economic * 100):2d}%"
    )
