"""
Terrarium Server: Production entry point for K8s deployment.

This is the main entry point that:
1. Reads configuration from environment variables
2. Initializes the Terrarium gateway with Purgatory and Mirror
3. Runs the FastAPI server via uvicorn

Usage:
    # Direct execution
    python -m protocols.terrarium.server

    # Docker
    CMD ["python", "-m", "protocols.terrarium.server"]

    # K8s (via AgentServer CRD)
    The operator sets environment variables from the CRD spec.

Environment Variables:
    TERRARIUM_HOST: Bind address (default: 0.0.0.0)
    TERRARIUM_PORT: Server port (default: 8080)
    TERRARIUM_METRICS_PORT: Metrics port (default: 9090)
    TERRARIUM_MIRROR_HISTORY: Events in history (default: 100)
    TERRARIUM_BROADCAST_TIMEOUT: Broadcast timeout in seconds (default: 0.1)
    TERRARIUM_AUTO_DISCOVER: Auto-discover agents (default: true)
    TERRARIUM_SEMAPHORES_ENABLED: Enable semaphore handling (default: true)
    TERRARIUM_PURGATORY_ENDPOINT: Expose /api/purgatory endpoints (default: true)
    TERRARIUM_OBSERVE_AUTH: Require auth for /observe (default: false)
    TERRARIUM_PERTURB_AUTH: Require auth for /perturb (default: true)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agents.flux.semaphore import Purgatory

logger = logging.getLogger(__name__)


def _parse_bool(value: str | None, default: bool = False) -> bool:
    """Parse boolean from environment variable."""
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")


@dataclass
class TerrariumServerConfig:
    """
    Server configuration loaded from environment.

    Designed to match the AgentServer CRD spec for seamless K8s integration.
    """

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    metrics_port: int = 9090

    # Mirror settings
    mirror_history_size: int = 100
    mirror_broadcast_timeout: float = 0.1

    # Agent discovery
    auto_discover: bool = True
    genus_filter: list[str] = field(default_factory=list)

    # Feature flags
    semaphores_enabled: bool = True
    purgatory_endpoint: bool = True

    # Auth settings
    observe_requires_auth: bool = False
    perturb_requires_auth: bool = True

    @classmethod
    def from_env(cls) -> "TerrariumServerConfig":
        """Load configuration from environment variables."""
        genus_filter_raw = os.environ.get("TERRARIUM_GENUS_FILTER", "")
        genus_filter = [g.strip() for g in genus_filter_raw.split(",") if g.strip()]

        return cls(
            host=os.environ.get("TERRARIUM_HOST", "0.0.0.0"),
            port=int(os.environ.get("TERRARIUM_PORT", "8080")),
            metrics_port=int(os.environ.get("TERRARIUM_METRICS_PORT", "9090")),
            mirror_history_size=int(os.environ.get("TERRARIUM_MIRROR_HISTORY", "100")),
            mirror_broadcast_timeout=float(
                os.environ.get("TERRARIUM_BROADCAST_TIMEOUT", "0.1")
            ),
            auto_discover=_parse_bool(
                os.environ.get("TERRARIUM_AUTO_DISCOVER"), default=True
            ),
            genus_filter=genus_filter,
            semaphores_enabled=_parse_bool(
                os.environ.get("TERRARIUM_SEMAPHORES_ENABLED"), default=True
            ),
            purgatory_endpoint=_parse_bool(
                os.environ.get("TERRARIUM_PURGATORY_ENDPOINT"), default=True
            ),
            observe_requires_auth=_parse_bool(
                os.environ.get("TERRARIUM_OBSERVE_AUTH"), default=False
            ),
            perturb_requires_auth=_parse_bool(
                os.environ.get("TERRARIUM_PERTURB_AUTH"), default=True
            ),
        )


class TerrariumServer:
    """
    The Terrarium server for K8s deployment.

    Manages:
    - Terrarium gateway lifecycle
    - Purgatory for semaphore handling
    - HolographicBuffer for observation
    - uvicorn server
    """

    def __init__(self, config: TerrariumServerConfig | None = None) -> None:
        self.config = config or TerrariumServerConfig.from_env()
        self._terrarium: Any = None
        self._purgatory: "Purgatory | None" = None
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """Start the terrarium server."""
        try:
            import uvicorn

            from .config import TerrariumConfig
            from .gateway import Terrarium
        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            logger.error("Install with: pip install fastapi uvicorn")
            return

        logger.info("[terrarium] Starting server...")
        logger.info(f"[terrarium] Host: {self.config.host}:{self.config.port}")
        logger.info(f"[terrarium] Metrics port: {self.config.metrics_port}")

        # Create Terrarium with config
        terrarium_config = TerrariumConfig(
            host=self.config.host,
            port=self.config.port,
            mirror_history_size=self.config.mirror_history_size,
            mirror_broadcast_timeout=self.config.mirror_broadcast_timeout,
            perturb_auth_required=self.config.perturb_requires_auth,
        )
        self._terrarium = Terrarium(config=terrarium_config)

        # Initialize Purgatory if semaphores enabled
        if self.config.semaphores_enabled:
            await self._init_purgatory()

        # Add purgatory endpoints if enabled
        if self.config.purgatory_endpoint and self._purgatory:
            self._add_purgatory_endpoints()

        # Add ready endpoint (more sophisticated than health)
        self._add_ready_endpoint()

        # Add soul stream WebSocket endpoint (C18)
        self._add_soul_stream_endpoint()

        # Create uvicorn config
        uvicorn_config = uvicorn.Config(
            self._terrarium.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info",
        )
        server = uvicorn.Server(uvicorn_config)

        # Run server with graceful shutdown
        logger.info("[terrarium] Server starting...")

        try:
            await server.serve()
        except Exception as e:
            logger.error(f"[terrarium] Server error: {e}")
            raise

    async def _init_purgatory(self) -> None:
        """Initialize Purgatory with buffer emission."""
        try:
            from agents.flux.semaphore import Purgatory
        except ImportError:
            logger.warning("[terrarium] Purgatory not available, skipping")
            return

        self._purgatory = Purgatory()

        # Wire pheromone emission to mirror buffer
        async def emit_to_buffer(signal: str, data: dict[str, Any]) -> None:
            if self._terrarium is None:
                return
            # Emit to all registered agent buffers
            # In production, we'd have a global buffer for purgatory events
            event = {
                "type": signal.replace(".", "_"),
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "source": "purgatory",
            }
            # For now, log it - full wiring happens with agent registration
            logger.debug(f"[purgatory] {signal}: {event}")

        self._purgatory._emit_pheromone = emit_to_buffer
        logger.info("[terrarium] Purgatory initialized")

    def _add_purgatory_endpoints(self) -> None:
        """Add REST endpoints for purgatory management.

        Note: FastAPI route decorators require `# type: ignore[untyped-decorator]`
        because FastAPI's type stubs don't fully annotate the decorator return types.
        This is a known upstream limitation; the runtime behavior is correct.
        """
        if self._terrarium is None or self._purgatory is None:
            return

        app = self._terrarium.app

        @app.get("/api/purgatory/list")  # type: ignore[untyped-decorator]
        async def list_pending() -> dict[str, Any]:
            """List pending semaphores."""
            tokens = self._purgatory.list_pending() if self._purgatory else []
            return {
                "pending": [
                    {
                        "id": t.id,
                        "reason": t.reason.value,
                        "prompt": t.prompt,
                        "options": t.options,
                        "severity": t.severity,
                        "created_at": t.created_at.isoformat(),
                        "deadline": t.deadline.isoformat() if t.deadline else None,
                    }
                    for t in tokens
                ],
                "count": len(tokens),
            }

        @app.post("/api/purgatory/resolve/{token_id}")  # type: ignore[untyped-decorator]
        async def resolve_token(token_id: str, human_input: str) -> dict[str, Any]:
            """Resolve a pending semaphore."""
            if self._purgatory is None:
                return {"error": "Purgatory not initialized"}

            reentry = await self._purgatory.resolve(token_id, human_input)
            if reentry is None:
                return {"error": f"Token not found or already resolved: {token_id}"}

            return {
                "success": True,
                "token_id": token_id,
                "reentry_ready": True,
            }

        @app.post("/api/purgatory/cancel/{token_id}")  # type: ignore[untyped-decorator]
        async def cancel_token(token_id: str) -> dict[str, Any]:
            """Cancel a pending semaphore."""
            if self._purgatory is None:
                return {"error": "Purgatory not initialized"}

            cancelled = await self._purgatory.cancel(token_id)
            return {
                "success": cancelled,
                "token_id": token_id,
            }

        @app.get("/api/purgatory/{token_id}")  # type: ignore[untyped-decorator]
        async def get_token(token_id: str) -> dict[str, Any]:
            """Get details of a specific token."""
            if self._purgatory is None:
                return {"error": "Purgatory not initialized"}

            token = self._purgatory.get(token_id)
            if token is None:
                return {"error": f"Token not found: {token_id}"}

            return {
                "id": token.id,
                "reason": token.reason.value,
                "prompt": token.prompt,
                "options": token.options,
                "severity": token.severity,
                "created_at": token.created_at.isoformat(),
                "deadline": token.deadline.isoformat() if token.deadline else None,
                "resolved_at": (
                    token.resolved_at.isoformat() if token.resolved_at else None
                ),
                "cancelled_at": (
                    token.cancelled_at.isoformat() if token.cancelled_at else None
                ),
                "voided_at": token.voided_at.isoformat() if token.voided_at else None,
                "is_pending": token.is_pending,
            }

        logger.info("[terrarium] Purgatory endpoints added")

    def _add_ready_endpoint(self) -> None:
        """Add readiness endpoint for K8s.

        Note: FastAPI route decorator requires `# type: ignore[untyped-decorator]`
        due to incomplete type stubs upstream.
        """
        if self._terrarium is None:
            return

        app = self._terrarium.app

        @app.get("/ready")  # type: ignore[untyped-decorator]
        async def ready() -> dict[str, Any]:
            """
            Readiness check for K8s.

            Returns ready when:
            - Server is running
            - (Future: Purgatory recovered, agents registered)
            """
            return {
                "ready": True,
                "service": "terrarium",
                "semaphores_enabled": self.config.semaphores_enabled,
                "purgatory_initialized": self._purgatory is not None,
                "agents_registered": (
                    len(self._terrarium.registered_agents) if self._terrarium else 0
                ),
            }

    def _add_soul_stream_endpoint(self) -> None:
        """Add WebSocket endpoint for K-gent Soul streaming.

        Endpoint: /ws/soul/stream

        Protocol:
        1. Client connects via WebSocket
        2. Client sends JSON: {"message": "...", "mode": "reflect|challenge|advise|explore"}
        3. Server streams response chunks: {"type": "chunk", "data": "..."}
        4. Server sends completion: {"type": "done", "tokens": N}
        5. Connection closes or client sends another message

        Rate limiting: Max 10 concurrent streams per IP (configurable via KGENT_WS_MAX_STREAMS)
        """
        if self._terrarium is None:
            return

        try:
            from fastapi import WebSocket, WebSocketDisconnect
        except ImportError:
            logger.warning("[terrarium] FastAPI not available for soul stream endpoint")
            return

        app = self._terrarium.app

        # Rate limiting: track active connections per IP
        active_streams: dict[str, int] = {}
        max_streams = int(os.environ.get("KGENT_WS_MAX_STREAMS", "10"))

        @app.websocket("/ws/soul/stream")  # type: ignore[untyped-decorator]
        async def ws_soul_stream(websocket: WebSocket) -> None:
            """
            WebSocket endpoint for K-gent Soul streaming dialogue.

            C18: Terrarium Server WebSocket Endpoint
            """
            # Get client IP for rate limiting
            client_ip = "unknown"
            if websocket.client:
                client_ip = websocket.client.host

            # Check rate limit
            current_streams = active_streams.get(client_ip, 0)
            if current_streams >= max_streams:
                await websocket.close(
                    code=4029,
                    reason=f"Rate limit exceeded: max {max_streams} streams per IP",
                )
                return

            await websocket.accept()
            active_streams[client_ip] = current_streams + 1
            logger.info(f"[soul-stream] Connection opened from {client_ip}")

            try:
                while True:
                    # Receive message
                    try:
                        raw_data = await websocket.receive_text()
                    except WebSocketDisconnect:
                        break

                    # Parse JSON
                    try:
                        data = json.loads(raw_data)
                    except json.JSONDecodeError as e:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "error": f"Invalid JSON: {e}",
                            }
                        )
                        continue

                    # Extract message and mode
                    message = data.get("message", "")
                    mode_str = data.get("mode", "reflect").lower()

                    if not message or not message.strip():
                        await websocket.send_json(
                            {
                                "type": "error",
                                "error": "Message is required",
                            }
                        )
                        continue

                    # Map mode string to DialogueMode
                    try:
                        from agents.k.persona import DialogueMode

                        mode_map = {
                            "reflect": DialogueMode.REFLECT,
                            "advise": DialogueMode.ADVISE,
                            "challenge": DialogueMode.CHALLENGE,
                            "explore": DialogueMode.EXPLORE,
                        }
                        mode = mode_map.get(mode_str, DialogueMode.REFLECT)
                    except ImportError:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "error": "K-gent module not available",
                            }
                        )
                        continue

                    # Create soul and stream response
                    try:
                        from agents.k.soul import KgentSoul

                        soul = KgentSoul()
                        total_tokens = 0

                        # Stream dialogue using dialogue_flux()
                        async for event in soul.dialogue_flux(message, mode=mode):
                            if event.is_data:
                                await websocket.send_json(
                                    {
                                        "type": "chunk",
                                        "data": event.value,
                                    }
                                )
                            elif event.is_metadata:
                                total_tokens = event.value.tokens_used

                        # Send completion message
                        await websocket.send_json(
                            {
                                "type": "done",
                                "tokens": total_tokens,
                            }
                        )

                    except Exception as e:
                        logger.error(f"[soul-stream] Error: {e}")
                        await websocket.send_json(
                            {
                                "type": "error",
                                "error": str(e),
                            }
                        )

            except WebSocketDisconnect:
                pass
            except Exception as e:
                logger.error(f"[soul-stream] Unexpected error: {e}")
            finally:
                # Decrement active stream count
                current = active_streams.get(client_ip, 1)
                if current <= 1:
                    active_streams.pop(client_ip, None)
                else:
                    active_streams[client_ip] = current - 1
                logger.info(f"[soul-stream] Connection closed from {client_ip}")

        logger.info("[terrarium] Soul stream endpoint added: /ws/soul/stream")

    @property
    def purgatory(self) -> "Purgatory | None":
        """Get the Purgatory instance for external wiring."""
        return self._purgatory

    @property
    def terrarium(self) -> Any:
        """Get the Terrarium instance."""
        return self._terrarium


async def run_server(config: TerrariumServerConfig | None = None) -> None:
    """
    Run the Terrarium server.

    This is the main entry point for running the server.
    """
    server = TerrariumServer(config=config)

    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()

    def handle_signal() -> None:
        logger.info("\n[terrarium] Received shutdown signal")
        server._shutdown_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, handle_signal)

    # Run the server
    await server.start()


def main() -> None:
    """Main entry point for the Terrarium server."""
    import argparse

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="Terrarium Server")
    parser.add_argument(
        "--host",
        "-H",
        type=str,
        default=None,
        help="Host to bind to (default: from env or 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=None,
        help="Port to listen on (default: from env or 8080)",
    )

    args = parser.parse_args()

    # Load config from env, override with CLI args
    config = TerrariumServerConfig.from_env()
    if args.host:
        config.host = args.host
    if args.port:
        config.port = args.port

    # Print startup banner
    print(
        """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   ▀█▀ █▀▀ █▀█ █▀█ ▄▀█ █▀█ █ █ █ █▀▄▀█                   ║
    ║    █  ██▄ █▀▄ █▀▄ █▀█ █▀▄ █ █▄█ █ ▀ █                   ║
    ║                                                          ║
    ║   The Mirror Protocol - Observe Without Disturbing       ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    )

    # Run the server
    try:
        asyncio.run(run_server(config))
    except KeyboardInterrupt:
        print("\n[terrarium] Interrupted")


if __name__ == "__main__":
    main()
