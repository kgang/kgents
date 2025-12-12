"""
Terrarium Gateway: FastAPI WebSocket server.

The main entry point for the Terrarium web gateway. Provides:
- /perturb/{agent_id}: The Beam (high entropy, auth required)
- /observe/{agent_id}: The Reflection (zero entropy, broadcast)
- /api/{agent_id}/snapshot: REST endpoint for current state

The Gateway manages:
- Agent registry (agent_id → FluxAgent + HolographicBuffer)
- WebSocket lifecycle
- The Mirror Protocol

Note: FastAPI is an optional dependency. Import this module only if
you have fastapi and starlette installed.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from .config import TerrariumConfig
from .mirror import HolographicBuffer

if TYPE_CHECKING:
    from agents.flux import FluxAgent

logger = logging.getLogger(__name__)

A = TypeVar("A")
B = TypeVar("B")


# Custom exceptions for gateway operations
class AgentNotFoundError(Exception):
    """Raised when requested agent is not registered."""

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id
        super().__init__(f"Agent not found: {agent_id}")


class AuthenticationError(Exception):
    """Raised when authentication fails for /perturb endpoint."""

    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message)


@dataclass
class AgentRegistration(Generic[A, B]):
    """
    Registration entry for an agent in the terrarium.

    Bundles the FluxAgent with its HolographicBuffer for the Mirror Protocol.
    """

    agent: "FluxAgent[A, B]"
    mirror: HolographicBuffer
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Terrarium:
    """
    The Agent Server Web Gateway.

    Manages agent registration and provides the Mirror Protocol endpoints.
    This is a thin gateway—it projects existing FluxAgent capabilities
    to the browser, not a UI framework.

    The Mirror Protocol:
    - /perturb/{agent_id}: Inject perturbations (The Beam)
    - /observe/{agent_id}: Subscribe to mirror broadcast (The Reflection)

    Usage:
        terrarium = Terrarium()

        # Register agents
        terrarium.register_agent("grammar", grammar_flux_agent)

        # Get the ASGI app
        app = terrarium.app

        # Run with uvicorn
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8080)
    """

    config: TerrariumConfig = field(default_factory=TerrariumConfig)

    # Agent registry: agent_id → AgentRegistration
    _registry: dict[str, AgentRegistration[Any, Any]] = field(
        default_factory=dict, init=False
    )

    # The FastAPI app (lazy-initialized)
    _app: Any = field(default=None, init=False)

    @property
    def app(self) -> Any:
        """
        Get the FastAPI application.

        Lazy-initializes the app on first access.

        Returns:
            FastAPI application instance

        Raises:
            ImportError: If fastapi is not installed
        """
        if self._app is None:
            self._app = self._create_app()
        return self._app

    def _create_app(self) -> Any:
        """Create the FastAPI application with all routes."""
        try:
            from fastapi import FastAPI, WebSocket, WebSocketDisconnect
            from fastapi.responses import JSONResponse
        except ImportError as e:
            raise ImportError(
                "FastAPI is required for Terrarium. "
                "Install with: pip install fastapi uvicorn"
            ) from e

        app = FastAPI(
            title=self.config.title,
            version=self.config.version,
            description=(
                "kgents Terrarium - Agent Server Web Gateway. "
                "The Mirror Protocol exposes FluxAgents as WebSocket streams."
            ),
        )

        @app.get("/health")  # type: ignore[untyped-decorator]
        async def health() -> dict[str, str]:
            """Health check endpoint."""
            return {"status": "healthy", "service": "terrarium"}

        @app.get("/api/agents")  # type: ignore[untyped-decorator]
        async def list_agents() -> dict[str, Any]:
            """List all registered agents."""
            return {
                "agents": [
                    {
                        "id": agent_id,
                        "state": str(reg.agent.state),
                        "observers": reg.mirror.observer_count,
                        "events": reg.mirror.events_reflected,
                        "metadata": reg.metadata,
                    }
                    for agent_id, reg in self._registry.items()
                ]
            }

        @app.get("/api/{agent_id}/snapshot")  # type: ignore[untyped-decorator]
        async def get_snapshot(agent_id: str) -> JSONResponse:
            """
            Get current state snapshot for an agent.

            This is the REST alternative to WebSocket /observe.
            Returns the current history buffer contents.
            """
            reg = self._registry.get(agent_id)
            if reg is None:
                return JSONResponse(
                    status_code=404,
                    content={"error": f"Agent not found: {agent_id}"},
                )

            return JSONResponse(
                content={
                    "agent_id": agent_id,
                    "state": str(reg.agent.state),
                    "history": reg.mirror.get_snapshot(),
                    "total_events": reg.mirror.events_reflected,
                }
            )

        @app.websocket("/perturb/{agent_id}")  # type: ignore[untyped-decorator]
        async def ws_perturb(websocket: WebSocket, agent_id: str) -> None:
            """
            The Beam: High entropy, auth required, injects Perturbation.

            This endpoint allows clients to inject events into a FluxAgent's
            processing stream. Each message is treated as a perturbation with
            high priority.

            Protocol:
            1. Client connects
            2. (Future: Auth handshake)
            3. Client sends JSON: {"data": <input_data>}
            4. Server responds with result or error
            5. Repeat 3-4 until disconnect
            """
            reg = self._registry.get(agent_id)
            if reg is None:
                await websocket.close(code=4004, reason="Agent not found")
                return

            await websocket.accept()
            logger.info(f"Perturb connection opened for {agent_id}")

            try:
                while True:
                    # Receive perturbation request
                    raw_data = await websocket.receive_text()

                    try:
                        request = json.loads(raw_data)
                        input_data = request.get("data")

                        if input_data is None:
                            await websocket.send_text(
                                json.dumps({"error": "Missing 'data' field"})
                            )
                            continue

                        # Invoke through the flux (becomes perturbation if flowing)
                        result = await asyncio.wait_for(
                            reg.agent.invoke(input_data),
                            timeout=self.config.agent_timeout,
                        )

                        await websocket.send_text(
                            json.dumps(
                                {
                                    "success": True,
                                    "result": result,
                                }
                            )
                        )

                    except json.JSONDecodeError:
                        await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
                    except asyncio.TimeoutError:
                        await websocket.send_text(
                            json.dumps({"error": "Agent timeout"})
                        )
                    except Exception as e:
                        await websocket.send_text(json.dumps({"error": str(e)}))

            except WebSocketDisconnect:
                logger.info(f"Perturb connection closed for {agent_id}")

        @app.websocket("/observe/{agent_id}")  # type: ignore[untyped-decorator]
        async def ws_observe(websocket: WebSocket, agent_id: str) -> None:
            """
            The Reflection: Zero entropy to agent, broadcast mirror.

            This endpoint allows clients to observe agent activity without
            disturbing it. All observers share one broadcast stream.

            Protocol:
            1. Client connects
            2. Server sends history (The Ghost)
            3. Server pushes events as they occur
            4. Client may send pings (ignored)
            5. Connection closed by either side
            """
            reg = self._registry.get(agent_id)
            if reg is None:
                await websocket.close(code=4004, reason="Agent not found")
                return

            logger.info(f"Observer attached to {agent_id}")

            try:
                # Attach to mirror (sends history automatically)
                await reg.mirror.attach_mirror(websocket)

                # Keep connection alive
                # The mirror will push events via broadcasts
                while True:
                    try:
                        # Listen for client messages (pings, disconnect)
                        await asyncio.wait_for(
                            websocket.receive_text(),
                            timeout=60.0,  # Heartbeat timeout
                        )
                        # Any message is treated as a keep-alive
                    except asyncio.TimeoutError:
                        # Send ping
                        await websocket.send_text('{"type":"ping"}')

            except WebSocketDisconnect:
                pass
            finally:
                reg.mirror.detach_mirror(websocket)
                logger.info(f"Observer detached from {agent_id}")

        return app

    def register_agent(
        self,
        agent_id: str,
        agent: "FluxAgent[A, B]",
        metadata: dict[str, Any] | None = None,
    ) -> HolographicBuffer:
        """
        Register a FluxAgent with the terrarium.

        Creates a HolographicBuffer for the agent and wires it up
        to receive agent events.

        Args:
            agent_id: Unique identifier for the agent
            agent: The FluxAgent to register
            metadata: Optional metadata (shown in agent list)

        Returns:
            The HolographicBuffer for the agent (for direct use)

        Raises:
            ValueError: If agent_id is already registered
        """
        if agent_id in self._registry:
            raise ValueError(f"Agent already registered: {agent_id}")

        mirror = HolographicBuffer(
            max_history=self.config.mirror_history_size,
            broadcast_timeout=self.config.mirror_broadcast_timeout,
        )

        self._registry[agent_id] = AgentRegistration(
            agent=agent,
            mirror=mirror,
            metadata=metadata or {},
        )

        logger.info(f"Registered agent: {agent_id}")
        return mirror

    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the terrarium.

        Args:
            agent_id: The agent to unregister

        Returns:
            True if agent was found and unregistered, False otherwise
        """
        if agent_id in self._registry:
            del self._registry[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
            return True
        return False

    def get_agent(self, agent_id: str) -> "FluxAgent[Any, Any] | None":
        """Get a registered agent by ID."""
        reg = self._registry.get(agent_id)
        return reg.agent if reg else None

    def get_mirror(self, agent_id: str) -> HolographicBuffer | None:
        """Get the HolographicBuffer for an agent."""
        reg = self._registry.get(agent_id)
        return reg.mirror if reg else None

    @property
    def registered_agents(self) -> list[str]:
        """List of registered agent IDs."""
        return list(self._registry.keys())
