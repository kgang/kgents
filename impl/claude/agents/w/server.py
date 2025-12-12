"""
W-gent Server: FastAPI-based observation server with SSE.

Implementation principles:
1. Zero-build frontend: No npm, Webpack, or React
2. Localhost-only by default: Binds to 127.0.0.1
3. Process isolation: Runs as separate process
4. Graceful degradation: Never breaks observed agent

Stack:
- Backend: FastAPI for HTTP, Jinja2 for templating
- Frontend: Pure HTML + CSS
- Interactivity: HTMX (HTML-over-the-wire, no JavaScript build)
- Real-time: Server-Sent Events (SSE)
"""

from __future__ import annotations

import asyncio
import json
import logging
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Optional

try:
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse, PlainTextResponse, StreamingResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from .fidelity import Fidelity, detect_fidelity, get_adapter
from .protocol import WireReader

logger = logging.getLogger(__name__)


class WireServer:
    """
    FastAPI-based wire observation server.

    Serves agent state visualization at localhost:{port}.

    Usage:
        server = WireServer("robin", port=8000)
        await server.start()
        # Browser opens to localhost:8000
        await server.stop()

    CLI equivalent:
        kgents wire attach robin --port 8000
    """

    def __init__(
        self,
        agent_name: str,
        port: int = 8000,
        host: str = "127.0.0.1",  # Localhost-only by default
        fidelity: Optional[Fidelity] = None,
        auto_open: bool = True,
        wire_base: Optional[Path] = None,
    ) -> None:
        """
        Initialize wire server.

        Args:
            agent_name: Name of the agent to observe
            port: Port to serve on (default 8000)
            host: Host to bind to (default 127.0.0.1 - localhost only)
            fidelity: Explicit fidelity level (auto-detect if None)
            auto_open: Whether to auto-open browser
            wire_base: Base directory for .wire files
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError(
                "FastAPI and uvicorn are required for WireServer. "
                "Install with: pip install fastapi uvicorn"
            )

        self.agent_name = agent_name
        self.port = port
        self.host = host
        self.fidelity = fidelity
        self.auto_open = auto_open

        self.reader = WireReader(agent_name, wire_base)
        self.app = self._create_app()
        self._server: Optional[uvicorn.Server] = None
        self._task: Optional[asyncio.Task[Any]] = None

    def _create_app(self) -> FastAPI:
        """Create the FastAPI application."""
        app = FastAPI(
            title=f"W-gent :: {self.agent_name}",
            docs_url=None,  # Disable swagger UI
            redoc_url=None,  # Disable redoc
        )

        @app.get("/", response_class=HTMLResponse)  # type: ignore[misc]
        async def index() -> HTMLResponse:
            """Main view - rendered by fidelity adapter."""
            adapter = get_adapter(self.reader, self.fidelity)
            result = adapter.render()
            return HTMLResponse(content=result.html)

        @app.get("/state")  # type: ignore[misc]
        async def state() -> dict[str, Any]:
            """Raw state JSON endpoint."""
            wire_state = self.reader.read_state()
            if wire_state:
                return wire_state.to_dict()
            return {"error": "No state available", "agent_id": self.agent_name}

        @app.get("/stream")  # type: ignore[misc]
        async def stream() -> list[dict[str, Any]]:
            """Raw stream events as JSON."""
            events = self.reader.read_stream(tail=100)
            return [e.to_dict() for e in events]

        @app.get("/metrics")  # type: ignore[misc]
        async def metrics() -> dict[str, Any]:
            """Raw metrics JSON endpoint."""
            wire_metrics = self.reader.read_metrics()
            if wire_metrics:
                return wire_metrics.to_dict()
            return {"error": "No metrics available"}

        @app.get("/events")  # type: ignore[misc]
        async def events_sse() -> StreamingResponse:
            """Server-Sent Events stream for real-time updates."""

            async def event_generator() -> AsyncIterator[str]:
                last_count = 0
                while True:
                    events = self.reader.read_stream()
                    if len(events) > last_count:
                        for event in events[last_count:]:
                            data = json.dumps(event.to_dict())
                            yield f"data: {data}\n\n"
                        last_count = len(events)
                    await asyncio.sleep(0.5)

            return StreamingResponse(event_generator(), media_type="text/event-stream")

        @app.get("/download")  # type: ignore[misc]
        async def download() -> PlainTextResponse:
            """Download stream log as text file."""
            events = self.reader.read_stream()
            content = "\n".join(e.to_log_line() for e in events)
            return PlainTextResponse(
                content=content,
                media_type="text/plain",
                headers={
                    "Content-Disposition": f"attachment; filename={self.agent_name}-stream.log"
                },
            )

        @app.get("/export")  # type: ignore[misc]
        async def export_to_igent() -> PlainTextResponse:
            """Export current state as I-gent margin note format."""
            state = self.reader.read_state()
            metrics = self.reader.read_metrics()

            notes = []
            ts = datetime.now().strftime("%H:%M:%S")

            if state:
                task = state.current_task or "running"
                progress = (
                    f"{int((state.progress or 0) * 100)}%" if state.progress else ""
                )
                notes.append(
                    f"{ts} — [w-gent] {self.agent_name} {task} {progress}".strip()
                )

            if metrics:
                parts = []
                if metrics.api_calls:
                    parts.append(f"{metrics.api_calls} API calls")
                if metrics.tokens_processed:
                    parts.append(f"{metrics.tokens_processed:,} tokens")
                if parts:
                    notes.append(f"{ts} — [w-gent] Metrics: {', '.join(parts)}")

            return PlainTextResponse(content="\n".join(notes), media_type="text/plain")

        @app.get("/health")  # type: ignore[misc]
        async def health() -> dict[str, Any]:
            """Health check endpoint."""
            return {
                "status": "ok",
                "agent": self.agent_name,
                "fidelity": (self.fidelity or detect_fidelity(self.reader)).value,
                "wire_exists": self.reader.exists(),
            }

        return app

    async def start(self) -> None:
        """Start the server."""
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="warning",
        )
        self._server = uvicorn.Server(config)

        # Start server in background
        self._task = asyncio.create_task(self._server.serve())

        # Wait a moment for server to start
        await asyncio.sleep(0.5)

        logger.info(f"W-gent serving at http://{self.host}:{self.port}")
        print("W-gent starting...")
        print(f"Attaching to: {self.agent_name}")
        print(f"Fidelity: {(self.fidelity or detect_fidelity(self.reader)).value}")
        print(f"Serving at: http://{self.host}:{self.port}")

        if self.auto_open:
            webbrowser.open(f"http://{self.host}:{self.port}")
            print("Browser opening...")

    async def stop(self) -> None:
        """Stop the server."""
        if self._server:
            self._server.should_exit = True
            if self._task:
                await self._task
            logger.info("W-gent stopped")

    async def run_forever(self) -> None:
        """Run the server until interrupted."""
        await self.start()
        try:
            if self._task:
                await self._task
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()


async def serve_agent(
    agent_name: str,
    port: int = 8000,
    fidelity: Optional[Fidelity] = None,
    auto_open: bool = True,
) -> None:
    """
    Convenience function to serve an agent.

    Args:
        agent_name: Name of the agent to observe
        port: Port to serve on
        fidelity: Explicit fidelity level (auto-detect if None)
        auto_open: Whether to auto-open browser
    """
    server = WireServer(
        agent_name,
        port=port,
        fidelity=fidelity,
        auto_open=auto_open,
    )
    await server.run_forever()


def cli_main() -> None:
    """CLI entry point for wire server."""
    import argparse

    parser = argparse.ArgumentParser(description="W-gent: Wire observation server")
    parser.add_argument("agent", help="Name of agent to observe")
    parser.add_argument("--port", type=int, default=8000, help="Port to serve on")
    parser.add_argument(
        "--mode",
        choices=["teletype", "documentarian", "livewire", "auto"],
        default="auto",
        help="Fidelity mode",
    )
    parser.add_argument(
        "--no-open", action="store_true", help="Don't auto-open browser"
    )

    args = parser.parse_args()

    fidelity = None
    if args.mode != "auto":
        fidelity = Fidelity(args.mode)

    asyncio.run(
        serve_agent(
            args.agent,
            port=args.port,
            fidelity=fidelity,
            auto_open=not args.no_open,
        )
    )


if __name__ == "__main__":
    cli_main()
