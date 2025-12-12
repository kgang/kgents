"""
L-gent HTTP Server - Containerized wrapper for L-gent library.

Provides HTTP endpoints for L-gent's semantic registry operations.
Designed for Kubernetes deployment with health/readiness probes.

Endpoints:
- GET  /health     - Liveness probe
- GET  /ready      - Readiness probe (checks registry initialized)
- GET  /catalog    - List catalog entries
- POST /search     - Semantic/keyword search
- POST /register   - Register new artifact
- GET  /entry/{id} - Get entry by ID
- GET  /stats      - Catalog statistics

AGENTESE: world.library.server
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import sys
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any

# Add parent paths for imports when running in container
if "/app" not in sys.path:
    sys.path.insert(0, "/app")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("lgent.server")


@dataclass
class ServerConfig:
    """L-gent server configuration."""

    host: str = "0.0.0.0"
    port: int = 8080
    database_url: str | None = None
    lgent_mode: str = "standalone"

    @classmethod
    def from_env(cls) -> ServerConfig:
        """Create config from environment variables."""
        return cls(
            host=os.environ.get("LGENT_HOST", "0.0.0.0"),
            port=int(os.environ.get("LGENT_PORT", "8080")),
            database_url=os.environ.get("DATABASE_URL"),
            lgent_mode=os.environ.get("LGENT_MODE", "standalone"),
        )


@dataclass
class Response:
    """HTTP response wrapper."""

    status: int = 200
    body: dict[str, Any] = field(default_factory=dict)
    content_type: str = "application/json"

    def to_bytes(self) -> bytes:
        """Serialize response body to JSON bytes."""
        return json.dumps(self.body, indent=2, default=str).encode("utf-8")


class LgentServer:
    """
    HTTP server for L-gent semantic registry.

    Uses asyncio.Protocol for lightweight serving without external deps.
    """

    def __init__(self, config: ServerConfig) -> None:
        self.config = config
        self._registry: Any = None
        self._ready = False
        self._shutdown = False

    async def initialize(self) -> None:
        """Initialize L-gent registry."""
        try:
            # Import L-gent components
            from agents.l import SemanticRegistry, create_semantic_registry

            logger.info("Initializing L-gent registry...")
            self._registry = await create_semantic_registry()
            self._ready = True
            logger.info("L-gent registry initialized successfully")
        except ImportError as e:
            logger.warning(f"L-gent import failed (using stub): {e}")
            self._registry = StubRegistry()
            self._ready = True
        except Exception as e:
            logger.error(f"Failed to initialize registry: {e}")
            self._ready = False

    async def handle_request(
        self, method: str, path: str, body: bytes | None = None
    ) -> Response:
        """Route and handle HTTP request."""
        # Health endpoints
        if path == "/health":
            return Response(body={"status": "healthy"})

        if path == "/ready":
            if self._ready:
                return Response(body={"ready": True, "mode": self.config.lgent_mode})
            return Response(
                status=HTTPStatus.SERVICE_UNAVAILABLE,
                body={"ready": False, "error": "Registry not initialized"},
            )

        # Catalog endpoints
        if path == "/catalog" and method == "GET":
            return await self._handle_catalog()

        if path == "/search" and method == "POST":
            return await self._handle_search(body)

        if path == "/register" and method == "POST":
            return await self._handle_register(body)

        if path.startswith("/entry/") and method == "GET":
            entry_id = path[7:]  # Strip "/entry/"
            return await self._handle_get_entry(entry_id)

        if path == "/stats" and method == "GET":
            return await self._handle_stats()

        # Not found
        return Response(
            status=HTTPStatus.NOT_FOUND,
            body={"error": "Not found", "path": path},
        )

    async def _handle_catalog(self) -> Response:
        """List catalog entries."""
        try:
            results = await self._registry.find()
            entries = [
                {
                    "id": r.entry.id,
                    "name": r.entry.name,
                    "type": r.entry.entity_type.value
                    if hasattr(r.entry, "entity_type") and r.entry.entity_type
                    else "unknown",
                    "description": getattr(r.entry, "description", None),
                }
                for r in results
            ]
            return Response(body={"entries": entries, "count": len(entries)})
        except Exception as e:
            logger.error(f"Catalog error: {e}")
            return Response(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                body={"error": str(e)},
            )

    async def _handle_search(self, body: bytes | None) -> Response:
        """Handle semantic/keyword search."""
        if not body:
            return Response(
                status=HTTPStatus.BAD_REQUEST,
                body={"error": "Request body required"},
            )

        try:
            data = json.loads(body.decode("utf-8"))
            query = data.get("query", "")
            mode = data.get("mode", "hybrid")  # hybrid, semantic, keyword
            limit = data.get("limit", 10)

            if not query:
                return Response(
                    status=HTTPStatus.BAD_REQUEST,
                    body={"error": "Query required"},
                )

            if mode == "semantic" and hasattr(self._registry, "find_semantic"):
                results = await self._registry.find_semantic(query, limit=limit)
            elif mode == "keyword":
                results = await self._registry.find(query=query, limit=limit)
            else:
                # Hybrid search
                if hasattr(self._registry, "find_hybrid"):
                    results = await self._registry.find_hybrid(query, limit=limit)
                else:
                    results = await self._registry.find(query=query, limit=limit)

            entries = [
                {
                    "id": r.entry.id,
                    "name": r.entry.name,
                    "score": getattr(r, "score", getattr(r, "similarity", 0.0)),
                    "description": getattr(r.entry, "description", None),
                }
                for r in results
            ]

            return Response(
                body={
                    "query": query,
                    "mode": mode,
                    "results": entries,
                    "count": len(entries),
                }
            )

        except json.JSONDecodeError as e:
            return Response(
                status=HTTPStatus.BAD_REQUEST,
                body={"error": f"Invalid JSON: {e}"},
            )
        except Exception as e:
            logger.error(f"Search error: {e}")
            return Response(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                body={"error": str(e)},
            )

    async def _handle_register(self, body: bytes | None) -> Response:
        """Register new artifact."""
        if not body:
            return Response(
                status=HTTPStatus.BAD_REQUEST,
                body={"error": "Request body required"},
            )

        try:
            import uuid

            from agents.l import CatalogEntry, EntityType, Status

            data = json.loads(body.decode("utf-8"))
            name = data.get("name")
            entity_type_str = data.get("type", "agent")
            description = data.get("description", "")

            if not name:
                return Response(
                    status=HTTPStatus.BAD_REQUEST,
                    body={"error": "Name required"},
                )

            # Map string to EntityType
            type_map: dict[str, EntityType] = {
                "agent": EntityType.AGENT,
                "tongue": EntityType.TONGUE,
                "contract": EntityType.CONTRACT,
                "memory": EntityType.MEMORY,
                "spec": EntityType.SPEC,
                "test": EntityType.TEST,
                "template": EntityType.TEMPLATE,
                "pattern": EntityType.PATTERN,
                "hypothesis": EntityType.HYPOTHESIS,
            }
            entity_type = type_map.get(entity_type_str.lower(), EntityType.AGENT)

            entry = CatalogEntry(
                id=str(uuid.uuid4())[:8],
                name=name,
                entity_type=entity_type,
                version="0.1.0",
                status=Status.ACTIVE,
                description=description,
            )

            await self._registry.register(entry)

            return Response(
                status=HTTPStatus.CREATED,
                body={
                    "id": entry.id,
                    "name": entry.name,
                    "type": entity_type_str,
                },
            )

        except json.JSONDecodeError as e:
            return Response(
                status=HTTPStatus.BAD_REQUEST,
                body={"error": f"Invalid JSON: {e}"},
            )
        except Exception as e:
            logger.error(f"Register error: {e}")
            return Response(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                body={"error": str(e)},
            )

    async def _handle_get_entry(self, entry_id: str) -> Response:
        """Get entry by ID."""
        try:
            entry = await self._registry.get(entry_id)
            if entry is None:
                return Response(
                    status=HTTPStatus.NOT_FOUND,
                    body={"error": f"Entry not found: {entry_id}"},
                )

            return Response(
                body={
                    "id": entry.id,
                    "name": entry.name,
                    "type": entry.entity_type.value
                    if hasattr(entry, "entity_type") and entry.entity_type
                    else None,
                    "status": entry.status.value
                    if hasattr(entry, "status") and entry.status
                    else None,
                    "description": getattr(entry, "description", None),
                    "version": getattr(entry, "version", None),
                }
            )
        except Exception as e:
            logger.error(f"Get entry error: {e}")
            return Response(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                body={"error": str(e)},
            )

    async def _handle_stats(self) -> Response:
        """Get catalog statistics."""
        try:
            results = await self._registry.find()

            by_type: dict[str, int] = {}
            for r in results:
                t = (
                    r.entry.entity_type.value
                    if hasattr(r.entry, "entity_type") and r.entry.entity_type
                    else "unknown"
                )
                by_type[t] = by_type.get(t, 0) + 1

            return Response(
                body={
                    "total": len(results),
                    "by_type": by_type,
                    "mode": self.config.lgent_mode,
                }
            )
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return Response(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                body={"error": str(e)},
            )


class StubRegistry:
    """Stub registry for when L-gent imports fail."""

    async def find(
        self, query: str | None = None, limit: int = 10, **kwargs: Any
    ) -> list[Any]:
        """Return empty results."""
        return []

    async def get(self, entry_id: str) -> None:
        """Return None."""
        return None

    async def register(self, entry: Any) -> None:
        """No-op."""
        pass


class HTTPProtocol(asyncio.Protocol):
    """Simple HTTP/1.1 protocol handler."""

    def __init__(self, server: LgentServer) -> None:
        self.server = server
        self.transport: asyncio.Transport | None = None

    def connection_made(self, transport: asyncio.Transport) -> None:  # type: ignore[override]
        self.transport = transport

    def data_received(self, data: bytes) -> None:
        asyncio.create_task(self._handle_data(data))

    async def _handle_data(self, data: bytes) -> None:
        """Parse HTTP request and send response."""
        try:
            # Simple HTTP parsing
            request_line, *headers_body = data.split(b"\r\n")
            parts = request_line.decode("utf-8").split(" ")
            if len(parts) < 2:
                return

            method = parts[0]
            path = parts[1].split("?")[0]  # Strip query string

            # Extract body for POST
            body = None
            if b"\r\n\r\n" in data:
                body = data.split(b"\r\n\r\n", 1)[1] or None

            # Handle request
            response = await self.server.handle_request(method, path, body)

            # Build HTTP response
            status_text = HTTPStatus(response.status).phrase
            response_body = response.to_bytes()
            http_response = (
                f"HTTP/1.1 {response.status} {status_text}\r\n"
                f"Content-Type: {response.content_type}\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
            ).encode("utf-8") + response_body

            if self.transport:
                self.transport.write(http_response)
                self.transport.close()

        except Exception as e:
            logger.error(f"Request handling error: {e}")
            if self.transport:
                error_body = json.dumps({"error": str(e)}).encode("utf-8")
                error_response = (
                    f"HTTP/1.1 500 Internal Server Error\r\n"
                    f"Content-Type: application/json\r\n"
                    f"Content-Length: {len(error_body)}\r\n"
                    f"\r\n"
                ).encode("utf-8") + error_body
                self.transport.write(error_response)
                self.transport.close()


async def run_server(config: ServerConfig) -> None:
    """Run L-gent HTTP server."""
    server = LgentServer(config)
    await server.initialize()

    loop = asyncio.get_event_loop()

    # Create server
    tcp_server = await loop.create_server(
        lambda: HTTPProtocol(server),
        config.host,
        config.port,
    )

    logger.info(f"L-gent server starting on {config.host}:{config.port}")
    logger.info(f"Mode: {config.lgent_mode}")
    if config.database_url:
        logger.info(f"Database: {config.database_url.split('@')[-1]}")

    # Handle shutdown signals
    shutdown_event = asyncio.Event()

    def handle_signal() -> None:
        logger.info("Shutdown signal received")
        shutdown_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_signal)

    # Serve until shutdown
    async with tcp_server:
        await shutdown_event.wait()

    logger.info("L-gent server stopped")


def main() -> None:
    """Entry point."""
    config = ServerConfig.from_env()
    asyncio.run(run_server(config))


if __name__ == "__main__":
    main()
