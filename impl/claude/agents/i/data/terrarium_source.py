"""
WebSocket data source for consuming Terrarium metrics.

Connects to the Terrarium /observe/{agent_id} WebSocket endpoint and
provides live metrics to I-gent widgets (DensityField, etc.).

The Key Insight:
    Terrarium emits TerriumEvent with pressure/flow/temperature.
    This module transforms that into I-gent widget data.

Usage:
    >>> from agents.i.data.terrarium_source import TerrariumWebSocketSource
    >>>
    >>> source = TerrariumWebSocketSource("ws://localhost:8080")
    >>> async for metrics in source.observe("agent-1"):
    ...     widget.activity = metrics.temperature
    ...     widget.refresh()
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable

# websockets is optional - only needed when actually connecting
# Type annotation uses Any to avoid mypy errors when not installed

logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    """
    Metrics for a single agent, derived from TerriumEvent.

    Maps Terrarium metabolism metrics to I-gent widget data.
    """

    agent_id: str
    state: str = "unknown"
    pressure: float = 0.0  # 0-100 scale (queue backlog)
    flow: float = 0.0  # events/second (throughput)
    temperature: float = 0.0  # 0-1 scale (metabolic heat)

    # Derived for I-gent widgets
    @property
    def activity(self) -> float:
        """
        Activity level for DensityField widget.

        Maps temperature (0-1) directly to activity.
        """
        return self.temperature

    @property
    def health(self) -> str:
        """
        Health indicator based on pressure.

        - healthy: pressure < 50
        - degraded: pressure 50-80
        - critical: pressure > 80
        """
        if self.pressure > 80:
            return "critical"
        if self.pressure >= 50:
            return "degraded"
        return "healthy"


@dataclass
class TerrariumWebSocketSource:
    """
    WebSocket data source for Terrarium metrics.

    Connects to the Terrarium gateway's /observe endpoint and
    yields AgentMetrics as they arrive.

    This is the bridge from Terrarium (WebSocket) to I-gent (TUI).
    """

    base_url: str = "ws://localhost:8080"
    """Base URL for Terrarium gateway."""

    reconnect_delay: float = 2.0
    """Delay before reconnection attempts."""

    max_reconnect_attempts: int = 5
    """Maximum reconnection attempts (0 = infinite)."""

    # Callbacks for event handling
    on_connected: Callable[[str], None] | None = None
    on_disconnected: Callable[[str], None] | None = None
    on_error: Callable[[str, Exception], None] | None = None

    # Internal state (Any type to avoid mypy errors when websockets not installed)
    _connections: dict[str, Any] = field(default_factory=dict, init=False)
    _last_metrics: dict[str, AgentMetrics] = field(default_factory=dict, init=False)

    async def observe(
        self,
        agent_id: str,
        auto_reconnect: bool = True,
    ) -> AsyncIterator[AgentMetrics]:
        """
        Subscribe to metrics for an agent.

        Connects to /observe/{agent_id} and yields AgentMetrics
        as TerriumEvent messages arrive.

        Args:
            agent_id: The agent to observe
            auto_reconnect: Automatically reconnect on disconnect

        Yields:
            AgentMetrics for each metabolism event
        """
        url = f"{self.base_url}/observe/{agent_id}"
        reconnect_count = 0

        while True:
            try:
                async for metrics in self._connect_and_observe(agent_id, url):
                    yield metrics
                    reconnect_count = 0  # Reset on successful message

                # Connection closed normally
                if not auto_reconnect:
                    break

            except Exception as e:
                if self.on_error:
                    self.on_error(agent_id, e)

                logger.warning(f"WebSocket error for {agent_id}: {e}")

                if not auto_reconnect:
                    raise

                reconnect_count += 1
                if (
                    self.max_reconnect_attempts > 0
                    and reconnect_count >= self.max_reconnect_attempts
                ):
                    logger.error(f"Max reconnect attempts reached for {agent_id}")
                    break

                await asyncio.sleep(self.reconnect_delay)

    async def _connect_and_observe(
        self,
        agent_id: str,
        url: str,
    ) -> AsyncIterator[AgentMetrics]:
        """
        Connect to WebSocket and yield metrics.

        Internal helper that handles a single connection session.
        """
        try:
            import websockets  # type: ignore[import-not-found]
        except ImportError as e:
            raise ImportError(
                "websockets is required for TerrariumWebSocketSource. "
                "Install with: pip install websockets"
            ) from e

        async with websockets.connect(url) as ws:
            self._connections[agent_id] = ws

            if self.on_connected:
                self.on_connected(agent_id)

            logger.info(f"Connected to {url}")

            try:
                async for message in ws:
                    try:
                        event = json.loads(message)
                        metrics = self._parse_event(agent_id, event)

                        if metrics:
                            self._last_metrics[agent_id] = metrics
                            yield metrics

                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON from {agent_id}: {message[:50]}")

            finally:
                self._connections.pop(agent_id, None)

                if self.on_disconnected:
                    self.on_disconnected(agent_id)

    def _parse_event(self, agent_id: str, event: dict[str, Any]) -> AgentMetrics | None:
        """
        Parse a TerriumEvent into AgentMetrics.

        Only metabolism events update metrics. Other events (lifecycle, etc.)
        are logged but don't yield new metrics.
        """
        event_type = event.get("type", "")

        if event_type == "metabolism":
            return AgentMetrics(
                agent_id=event.get("agent_id", agent_id),
                state=event.get("state", "unknown"),
                pressure=float(event.get("pressure", 0)),
                flow=float(event.get("flow", 0)),
                temperature=float(event.get("temperature", 0)),
            )

        if event_type == "agent_stopped":
            return AgentMetrics(
                agent_id=event.get("agent_id", agent_id),
                state="stopped",
                pressure=0.0,
                flow=0.0,
                temperature=0.0,
            )

        if event_type == "fever":
            # Fever events indicate high temperature
            last = self._last_metrics.get(agent_id)
            if last:
                return AgentMetrics(
                    agent_id=agent_id,
                    state=last.state,
                    pressure=last.pressure,
                    flow=last.flow,
                    temperature=float(event.get("temperature", 1.0)),
                )

        # Other events don't produce metrics
        logger.debug(f"Ignored event type: {event_type}")
        return None

    async def disconnect(self, agent_id: str) -> bool:
        """
        Disconnect from an agent's WebSocket.

        Args:
            agent_id: The agent to disconnect from

        Returns:
            True if disconnected, False if not connected
        """
        ws = self._connections.pop(agent_id, None)
        if ws:
            await ws.close()
            return True
        return False

    async def disconnect_all(self) -> int:
        """
        Disconnect from all agents.

        Returns:
            Number of connections closed
        """
        count = len(self._connections)

        for ws in list(self._connections.values()):
            await ws.close()

        self._connections.clear()
        return count

    def get_last_metrics(self, agent_id: str) -> AgentMetrics | None:
        """
        Get the last received metrics for an agent.

        Useful for checking state without waiting for next event.
        """
        return self._last_metrics.get(agent_id)

    def is_connected(self, agent_id: str) -> bool:
        """Check if connected to an agent."""
        return agent_id in self._connections

    @property
    def connected_agents(self) -> list[str]:
        """List of currently connected agent IDs."""
        return list(self._connections.keys())


async def observe_multiple(
    source: TerrariumWebSocketSource,
    agent_ids: list[str],
) -> AsyncIterator[AgentMetrics]:
    """
    Observe multiple agents concurrently.

    Merges metrics from all agents into a single stream.

    Args:
        source: The WebSocket source
        agent_ids: List of agent IDs to observe

    Yields:
        AgentMetrics from any observed agent
    """
    if not agent_ids:
        return

    # Shared queue for all agents
    merged_queue: asyncio.Queue[AgentMetrics] = asyncio.Queue()

    async def observe_one(agent_id: str) -> None:
        """Observe a single agent and put metrics in shared queue."""
        try:
            async for metrics in source.observe(agent_id):
                await merged_queue.put(metrics)
        except asyncio.CancelledError:
            pass

    # Start observation tasks
    tasks: list[asyncio.Task[None]] = [
        asyncio.create_task(observe_one(aid), name=f"observe-{aid}")
        for aid in agent_ids
    ]

    try:
        # Yield from merged queue
        while True:
            # Check if all tasks are done
            if all(task.done() for task in tasks) and merged_queue.empty():
                break

            try:
                metrics = await asyncio.wait_for(merged_queue.get(), timeout=0.1)
                yield metrics
            except asyncio.TimeoutError:
                continue

    except asyncio.CancelledError:
        pass
    finally:
        # Cancel all observation tasks
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
