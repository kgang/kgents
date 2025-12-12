"""
D-gent Server: FastAPI application for cluster-native state management.

This server exposes D-gent capabilities as HTTP endpoints for Kubernetes deployment.
Designed to run as a sidecar container, providing state persistence to agent pods.

Features:
- Key-value state CRUD operations
- Versioned state for optimistic concurrency control
- Checkpoint creation for durability
- Namespace isolation (multiple agents share one D-gent sidecar)

Usage (local development):
    uvicorn agents.d.server:app --reload --port 8081

Usage (in-cluster):
    Deploy as sidecar in agent pod with shared volume

AGENTESE: self.dgent.server
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# --- Request/Response Models ---


class StateValue(BaseModel):
    """A versioned state value."""

    key: str = Field(..., description="State key")
    value: Any = Field(..., description="State value (JSON-serializable)")
    version: int = Field(default=1, description="Version for optimistic concurrency")
    namespace: str = Field(default="default", description="Namespace for isolation")
    created_at: str = Field(default="", description="Creation timestamp")
    updated_at: str = Field(default="", description="Last update timestamp")


class PutRequest(BaseModel):
    """Request to write state."""

    value: Any = Field(..., description="State value to store")
    expected_version: Optional[int] = Field(
        None, description="Expected version for CAS (Compare-And-Swap)"
    )


class CheckpointResponse(BaseModel):
    """Response from checkpoint creation."""

    checkpoint_id: str
    namespace: str
    keys: int
    timestamp: str
    path: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    storage_type: str
    keys_stored: int
    namespaces: list[str]
    timestamp: str


class StateNotFoundError(Exception):
    """Raised when requested state key doesn't exist."""

    pass


class VersionConflictError(Exception):
    """Raised on optimistic concurrency violation."""

    pass


# --- Storage Backend ---


@dataclass
class InMemoryStore:
    """
    In-memory state storage with namespacing.

    Provides fast ephemeral storage suitable for sidecar use.
    State is lost on container restart unless checkpointed.
    """

    _data: dict[str, dict[str, StateValue]] = field(default_factory=dict)
    _checkpoint_dir: Optional[Path] = None

    def __post_init__(self) -> None:
        """Initialize checkpoint directory if specified via env var."""
        # Only use checkpoint directory if explicitly configured
        checkpoint_path = os.environ.get("DGENT_CHECKPOINT_DIR")
        if checkpoint_path:
            self._checkpoint_dir = Path(checkpoint_path)
            if self._checkpoint_dir.exists():
                self._restore_from_checkpoint()

    def _ensure_namespace(self, namespace: str) -> None:
        """Ensure namespace exists."""
        if namespace not in self._data:
            self._data[namespace] = {}

    def get(self, key: str, namespace: str = "default") -> Optional[StateValue]:
        """Get state by key."""
        self._ensure_namespace(namespace)
        return self._data[namespace].get(key)

    def put(
        self,
        key: str,
        value: Any,
        namespace: str = "default",
        expected_version: Optional[int] = None,
    ) -> StateValue:
        """
        Put state with optional optimistic concurrency.

        Args:
            key: State key
            value: State value
            namespace: Namespace for isolation
            expected_version: If provided, CAS check

        Returns:
            Updated StateValue with new version

        Raises:
            VersionConflictError: If expected_version doesn't match
        """
        self._ensure_namespace(namespace)
        now = datetime.now().isoformat()

        existing = self._data[namespace].get(key)

        if existing is not None:
            # Update existing
            if expected_version is not None and existing.version != expected_version:
                raise VersionConflictError(
                    f"Version conflict for {namespace}/{key}: "
                    f"expected {expected_version}, found {existing.version}"
                )
            new_version = existing.version + 1
            created_at = existing.created_at
        else:
            # Create new
            if expected_version is not None and expected_version != 0:
                raise VersionConflictError(
                    f"Key {namespace}/{key} doesn't exist but expected_version={expected_version}"
                )
            new_version = 1
            created_at = now

        state = StateValue(
            key=key,
            value=value,
            version=new_version,
            namespace=namespace,
            created_at=created_at,
            updated_at=now,
        )
        self._data[namespace][key] = state
        return state

    def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete state by key. Returns True if key existed."""
        self._ensure_namespace(namespace)
        if key in self._data[namespace]:
            del self._data[namespace][key]
            return True
        return False

    def list_keys(self, namespace: str = "default") -> list[str]:
        """List all keys in namespace."""
        self._ensure_namespace(namespace)
        return list(self._data[namespace].keys())

    def list_namespaces(self) -> list[str]:
        """List all namespaces."""
        return list(self._data.keys())

    def count(self, namespace: Optional[str] = None) -> int:
        """Count keys in namespace or total."""
        if namespace:
            self._ensure_namespace(namespace)
            return len(self._data[namespace])
        return sum(len(ns_data) for ns_data in self._data.values())

    def checkpoint(self, namespace: str = "default") -> CheckpointResponse:
        """
        Create a checkpoint of namespace state.

        Writes state to checkpoint directory if configured.
        """
        self._ensure_namespace(namespace)
        now = datetime.now()
        checkpoint_id = hashlib.sha256(
            f"{namespace}:{now.isoformat()}".encode()
        ).hexdigest()[:16]

        keys = list(self._data[namespace].keys())
        checkpoint_path = None

        if self._checkpoint_dir:
            self._checkpoint_dir.mkdir(parents=True, exist_ok=True)
            checkpoint_file = self._checkpoint_dir / f"{namespace}_{checkpoint_id}.json"

            # Serialize state
            checkpoint_data = {
                "namespace": namespace,
                "checkpoint_id": checkpoint_id,
                "timestamp": now.isoformat(),
                "state": {k: v.model_dump() for k, v in self._data[namespace].items()},
            }
            checkpoint_file.write_text(json.dumps(checkpoint_data, indent=2))
            checkpoint_path = str(checkpoint_file)
            logger.info(f"Checkpoint created: {checkpoint_path}")

        return CheckpointResponse(
            checkpoint_id=checkpoint_id,
            namespace=namespace,
            keys=len(keys),
            timestamp=now.isoformat(),
            path=checkpoint_path,
        )

    def _restore_from_checkpoint(self) -> None:
        """Restore state from latest checkpoint files."""
        if not self._checkpoint_dir or not self._checkpoint_dir.exists():
            return

        # Find latest checkpoint per namespace
        checkpoints: dict[str, Path] = {}
        for f in self._checkpoint_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                namespace = data.get("namespace", "default")
                timestamp = data.get("timestamp", "")

                if namespace not in checkpoints:
                    checkpoints[namespace] = f
                else:
                    # Compare timestamps, keep latest
                    existing_data = json.loads(checkpoints[namespace].read_text())
                    if timestamp > existing_data.get("timestamp", ""):
                        checkpoints[namespace] = f
            except Exception as e:
                logger.warning(f"Failed to parse checkpoint {f}: {e}")

        # Restore from latest checkpoints
        for namespace, checkpoint_file in checkpoints.items():
            try:
                data = json.loads(checkpoint_file.read_text())
                self._ensure_namespace(namespace)
                for key, state_data in data.get("state", {}).items():
                    self._data[namespace][key] = StateValue(**state_data)
                logger.info(
                    f"Restored {len(data.get('state', {}))} keys "
                    f"for namespace '{namespace}' from {checkpoint_file}"
                )
            except Exception as e:
                logger.warning(f"Failed to restore from {checkpoint_file}: {e}")


# --- Server State ---


@dataclass
class ServerState:
    """Server state for dependency injection."""

    store: InMemoryStore = field(default_factory=InMemoryStore)
    startup_time: datetime = field(default_factory=datetime.now)


# Global state (initialized on startup)
_state: Optional[ServerState] = None


def get_state() -> ServerState:
    """Get server state, initializing if needed."""
    global _state
    if _state is None:
        _state = ServerState()
    return _state


# --- FastAPI Application ---


def create_app() -> Any:
    """
    Create FastAPI application for D-gent server.

    The server provides:
    - GET /state/{key} - Read state
    - PUT /state/{key} - Write state (with optional CAS)
    - DELETE /state/{key} - Delete state
    - GET /keys - List keys in namespace
    - POST /checkpoint - Create checkpoint
    - GET /health - Health check

    Returns:
        FastAPI application
    """
    try:
        from fastapi import FastAPI, HTTPException, Query
        from fastapi.responses import JSONResponse
    except ImportError:
        raise ImportError(
            "FastAPI not installed. Install with: pip install fastapi uvicorn"
        )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        """Lifespan context manager for startup/shutdown."""
        # Startup
        state = get_state()
        logger.info(
            f"D-gent Server starting (checkpoint_dir={state.store._checkpoint_dir})"
        )

        yield

        # Shutdown - checkpoint all namespaces
        logger.info("D-gent Server shutting down, creating final checkpoints...")
        for namespace in state.store.list_namespaces():
            try:
                state.store.checkpoint(namespace)
            except Exception as e:
                logger.error(f"Failed to checkpoint namespace '{namespace}': {e}")

    app = FastAPI(
        title="D-gent Server",
        description="Cluster-native state management sidecar",
        version="1.0.0",
        lifespan=lifespan,
    )

    @app.get("/state/{key}", response_model=StateValue)
    async def get_state_value(
        key: str, namespace: str = Query("default", description="State namespace")
    ) -> StateValue:
        """Read state by key."""
        state = get_state()
        value = state.store.get(key, namespace)

        if value is None:
            raise HTTPException(
                status_code=404,
                detail=f"Key '{key}' not found in namespace '{namespace}'",
            )

        return value

    @app.put("/state/{key}", response_model=StateValue)
    async def put_state_value(
        key: str,
        request: PutRequest,
        namespace: str = Query("default", description="State namespace"),
    ) -> StateValue:
        """Write state with optional optimistic concurrency control."""
        state = get_state()

        try:
            return state.store.put(
                key=key,
                value=request.value,
                namespace=namespace,
                expected_version=request.expected_version,
            )
        except VersionConflictError as e:
            raise HTTPException(status_code=409, detail=str(e))

    @app.delete("/state/{key}")
    async def delete_state_value(
        key: str, namespace: str = Query("default", description="State namespace")
    ) -> dict[str, Any]:
        """Delete state by key."""
        state = get_state()
        deleted = state.store.delete(key, namespace)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Key '{key}' not found in namespace '{namespace}'",
            )

        return {"deleted": True, "key": key, "namespace": namespace}

    @app.get("/keys")
    async def list_keys(
        namespace: str = Query("default", description="State namespace"),
    ) -> dict[str, Any]:
        """List all keys in namespace."""
        state = get_state()
        keys = state.store.list_keys(namespace)
        return {"namespace": namespace, "keys": keys, "count": len(keys)}

    @app.post("/checkpoint", response_model=CheckpointResponse)
    async def create_checkpoint(
        namespace: str = Query("default", description="State namespace"),
    ) -> CheckpointResponse:
        """Create a checkpoint of namespace state."""
        state = get_state()
        return state.store.checkpoint(namespace)

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        """Health check endpoint."""
        state = get_state()
        return HealthResponse(
            status="healthy",
            storage_type="in-memory"
            if not state.store._checkpoint_dir
            else "checkpointed",
            keys_stored=state.store.count(),
            namespaces=state.store.list_namespaces() or ["default"],
            timestamp=datetime.now().isoformat(),
        )

    @app.get("/")
    async def root() -> dict[str, Any]:
        """Root endpoint with API info."""
        state = get_state()
        return {
            "name": "D-gent Server",
            "version": "1.0.0",
            "description": "Cluster-native state management sidecar",
            "storage_type": "in-memory"
            if not state.store._checkpoint_dir
            else "checkpointed",
            "keys_stored": state.store.count(),
            "endpoints": {
                "get_state": "GET /state/{key}?namespace=default",
                "put_state": "PUT /state/{key}?namespace=default",
                "delete_state": "DELETE /state/{key}?namespace=default",
                "list_keys": "GET /keys?namespace=default",
                "checkpoint": "POST /checkpoint?namespace=default",
                "health": "GET /health",
            },
        }

    return app


# Create app instance for uvicorn
app = create_app()


def main() -> None:
    """Run D-gent server."""
    try:
        import uvicorn
    except ImportError:
        raise ImportError("uvicorn not installed. Install with: pip install uvicorn")

    port = int(os.environ.get("DGENT_PORT", "8081"))
    host = os.environ.get("DGENT_HOST", "0.0.0.0")

    logging.basicConfig(level=logging.INFO)
    logger.info(f"Starting D-gent Server on {host}:{port}")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
