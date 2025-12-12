"""
The Glass Client: A resilient gRPC wrapper with Ghost fallback.

Principle: Graceful Degradation - never fail completely.
Principle: Transparent Infrastructure - tell users what's happening.

The Glass Terminal architecture transforms the CLI into a thin, transparent shell
that delegates all business logic to the Cortex daemon. When the daemon is unavailable,
the Glass Client falls back to Ghost Mode: reading last-known-good state from the
local cache at ~/.kgents/ghost/.

The Glass Client is the CLI's view of the world—resilient, never blind.
Always returns data: live if possible, ghost if not.

AGENTESE Mapping:
    Ghost write = self.memory.engram (persist state on successful invocation)
    Ghost read = self.memory.manifest (cached last-known-good state)
    Ghost miss = Transparent error message with recovery guidance

Usage:
    client = GlassClient()
    response = await client.invoke(
        method="GetStatus",
        request=StatusRequest(verbose=True),
        ghost_key="status"  # Enables Ghost fallback
    )

    if response.is_ghost:
        print(f"[GHOST] Data from {response.ghost_age.seconds}s ago")
    else:
        print(f"[LIVE] {response.data}")
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, TypeVar, cast

if TYPE_CHECKING:
    from infra.cortex import CortexServicer

# Type variables for generic responses
T = TypeVar("T")

# =============================================================================
# Configuration
# =============================================================================

# Ghost cache location (user's home directory)
GHOST_DIR = Path.home() / ".kgents" / "ghost"

# gRPC connection timeout (fail fast to Ghost)
# 500ms is enough for local daemon, but fast enough to not block user
GRPC_TIMEOUT = 0.5

# Default gRPC address for the Cortex daemon
DEFAULT_GRPC_ADDRESS = "localhost:50051"


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class GlassResponse:
    """
    Response that knows whether it came from live or ghost.

    The Glass Response is transparent about its provenance:
    - Live responses have is_ghost=False
    - Ghost responses have is_ghost=True and ghost_age indicates staleness

    This transparency allows the CLI to inform users clearly about data freshness.
    """

    data: Any
    is_ghost: bool = False
    ghost_age: timedelta | None = None
    ghost_timestamp: datetime | None = None

    def render(self, format: str = "text") -> str:
        """
        Render the response with optional Ghost prefix.

        Principle: Transparent Infrastructure - users should never wonder
        "what just happened?"
        """
        prefix = ""
        age_suffix = ""

        if self.is_ghost:
            prefix = "[GHOST] "
            if self.ghost_age:
                seconds = int(self.ghost_age.total_seconds())
                if seconds < 60:
                    age_suffix = f" (data from {seconds}s ago)"
                elif seconds < 3600:
                    age_suffix = f" (data from {seconds // 60}m ago)"
                else:
                    age_suffix = f" (data from {seconds // 3600}h ago)"

        if format == "json":
            return json.dumps(
                {
                    "data": self.data,
                    "is_ghost": self.is_ghost,
                    "ghost_age_seconds": (
                        self.ghost_age.total_seconds() if self.ghost_age else None
                    ),
                },
                indent=2,
                default=str,
            )

        # Text format
        if isinstance(self.data, dict):
            return f"{prefix}{json.dumps(self.data, indent=2, default=str)}{age_suffix}"
        return f"{prefix}{self.data}{age_suffix}"


@dataclass
class GhostCacheEntry:
    """
    A single entry in the Ghost cache.

    The Ghost cache stores last-known-good state for offline recovery.
    Each entry includes:
    - The data itself
    - When it was cached (for staleness calculation)
    - The AGENTESE path that produced it (for debugging)
    """

    data: Any
    timestamp: datetime
    agentese_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Ghost Cache Manager
# =============================================================================


class GhostCache:
    """
    Manages the Ghost cache at ~/.kgents/ghost/.

    The Ghost cache provides offline resilience:
    - On successful gRPC calls, data is written to the cache
    - On gRPC failures, data is read from the cache
    - Users always see something useful

    Directory structure:
        ~/.kgents/ghost/
        ├── status.json         # Last known cortex status
        ├── map.json            # Last known HoloMap
        ├── agents/             # Per-agent state snapshots
        │   ├── d-gent.json
        │   └── l-gent.json
        └── meta.json           # Timestamps, staleness info
    """

    def __init__(self, ghost_dir: Path = GHOST_DIR):
        self.ghost_dir = ghost_dir

    def ensure_directory(self) -> None:
        """Ensure the Ghost directory structure exists."""
        self.ghost_dir.mkdir(parents=True, exist_ok=True)
        (self.ghost_dir / "agents").mkdir(exist_ok=True)

    def write(
        self,
        key: str,
        data: Any,
        agentese_path: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Write data to the Ghost cache.

        Maps to AGENTESE: self.memory.engram
        """
        self.ensure_directory()

        entry = {
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "agentese_path": agentese_path,
            "metadata": metadata or {},
        }

        # Handle nested keys (e.g., "agents/d-gent")
        if "/" in key:
            subdir, filename = key.rsplit("/", 1)
            (self.ghost_dir / subdir).mkdir(parents=True, exist_ok=True)
            ghost_file = self.ghost_dir / subdir / f"{filename}.json"
        else:
            ghost_file = self.ghost_dir / f"{key}.json"

        ghost_file.write_text(json.dumps(entry, indent=2, default=str))

        # Update meta.json with last write time
        self._update_meta(key)

    def read(self, key: str) -> tuple[Any, timedelta | None, datetime | None]:
        """
        Read data from the Ghost cache.

        Maps to AGENTESE: self.memory.manifest

        Returns:
            (data, age, timestamp) or (None, None, None) if not found
        """
        # Handle nested keys
        if "/" in key:
            subdir, filename = key.rsplit("/", 1)
            ghost_file = self.ghost_dir / subdir / f"{filename}.json"
        else:
            ghost_file = self.ghost_dir / f"{key}.json"

        if not ghost_file.exists():
            return None, None, None

        try:
            cached = json.loads(ghost_file.read_text())
            timestamp = datetime.fromisoformat(cached["timestamp"])
            age = datetime.now() - timestamp
            return cached["data"], age, timestamp
        except (json.JSONDecodeError, KeyError, ValueError):
            return None, None, None

    def exists(self, key: str) -> bool:
        """Check if a Ghost cache entry exists."""
        if "/" in key:
            subdir, filename = key.rsplit("/", 1)
            ghost_file = self.ghost_dir / subdir / f"{filename}.json"
        else:
            ghost_file = self.ghost_dir / f"{key}.json"
        return ghost_file.exists()

    def _update_meta(self, key: str) -> None:
        """Update meta.json with latest write info."""
        meta_file = self.ghost_dir / "meta.json"

        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text())
            except (json.JSONDecodeError, ValueError):
                meta = {}
        else:
            meta = {}

        if "last_writes" not in meta:
            meta["last_writes"] = {}

        meta["last_writes"][key] = datetime.now().isoformat()
        meta["last_updated"] = datetime.now().isoformat()

        meta_file.write_text(json.dumps(meta, indent=2))

    def get_meta(self) -> dict[str, Any]:
        """Get cache metadata."""
        meta_file = self.ghost_dir / "meta.json"
        if not meta_file.exists():
            return {}
        try:
            return cast(dict[str, Any], json.loads(meta_file.read_text()))
        except (json.JSONDecodeError, ValueError):
            return {}


# =============================================================================
# The Glass Client
# =============================================================================


class GlassClient:
    """
    The CLI's view of the world—resilient, never blind.

    Always returns data: live if possible, ghost if not.
    The user is never left wondering "what happened?"

    The Glass Client implements the three-layer fallback strategy:
    1. Try gRPC call to Cortex daemon (live data)
    2. On failure, read from Ghost cache (last-known-good)
    3. On cache miss, provide clear error with recovery guidance

    Usage:
        client = GlassClient()

        # Simple invocation with Ghost fallback
        response = await client.invoke(
            method="GetStatus",
            request=StatusRequest(verbose=True),
            ghost_key="status"
        )

        # Stream invocation (no Ghost fallback for streams)
        async with client.stream("StreamDreams") as stream:
            async for chunk in stream:
                print(chunk.text)
    """

    def __init__(
        self,
        address: str = DEFAULT_GRPC_ADDRESS,
        ghost_cache: GhostCache | None = None,
        timeout: float = GRPC_TIMEOUT,
        use_local_servicer: bool = True,
    ):
        """
        Initialize the Glass Client.

        The Glass Client implements a three-layer fallback strategy:
        1. Try gRPC call to Cortex daemon (live data)
        2. On gRPC failure, try local servicer (in-process)
        3. On local failure, read from Ghost cache (last-known-good)
        4. On cache miss, provide clear error with recovery guidance

        Args:
            address: gRPC address for Cortex daemon (default: localhost:50051)
            ghost_cache: Custom Ghost cache instance (default: ~/.kgents/ghost/)
            timeout: gRPC timeout in seconds (default: 0.5)
            use_local_servicer: Try local CortexServicer before Ghost (default: True)
        """
        self.address = address
        self.ghost_cache = ghost_cache or GhostCache()
        self.timeout = timeout
        self.use_local_servicer = use_local_servicer
        self._stub = None  # Lazy-initialized
        self._local_servicer: CortexServicer | None = None  # Lazy-initialized

    async def invoke(
        self,
        method: str,
        request: Any = None,
        ghost_key: str | None = None,
        agentese_path: str | None = None,
        transform: Callable[[Any], Any] | None = None,
    ) -> GlassResponse:
        """
        Invoke a gRPC method with Ghost fallback.

        This is the heart of the Glass Terminal pattern:
        1. Attempt gRPC call with fast timeout
        2. On success, update Ghost cache
        3. On failure, read from Ghost cache
        4. On cache miss, raise informative error

        Args:
            method: The gRPC method name (e.g., "GetStatus")
            request: The protobuf request object
            ghost_key: Key for ghost cache (e.g., "status")
            agentese_path: AGENTESE path for tracing (e.g., "self.cortex.manifest")
            transform: Optional function to transform response data

        Returns:
            GlassResponse with data and ghost status

        Raises:
            ConnectionError: When gRPC fails and no Ghost cache available
        """
        try:
            # Attempt live gRPC connection
            response = await self._grpc_invoke(method, request)

            # Transform if needed
            data = transform(response) if transform else response

            # Success! Update Ghost cache
            if ghost_key:
                self.ghost_cache.write(
                    key=ghost_key,
                    data=self._serialize_for_cache(data),
                    agentese_path=agentese_path,
                )

            return GlassResponse(data=data, is_ghost=False)

        except (asyncio.TimeoutError, ConnectionError, OSError) as e:
            # Ghost mode: read from cache
            if ghost_key:
                ghost_data, age, timestamp = self.ghost_cache.read(ghost_key)
                if ghost_data is not None:
                    return GlassResponse(
                        data=ghost_data,
                        is_ghost=True,
                        ghost_age=age,
                        ghost_timestamp=timestamp,
                    )

            # No Ghost available - transparent failure with recovery guidance
            raise ConnectionError(
                f"Cortex daemon unavailable at {self.address}. "
                + (f"No cached data for '{ghost_key}'. " if ghost_key else "")
                + "Run 'kgents infra init' to start the daemon, "
                + "or 'kgents infra status' to check infrastructure."
            ) from e

    async def _grpc_invoke(self, method: str, request: Any) -> Any:
        """
        Execute a gRPC call with timeout, with local servicer fallback.

        The three-layer fallback strategy:
        1. Try gRPC to Cortex daemon
        2. On failure, try local CortexServicer (in-process)
        3. On local failure, raise ConnectionError (Ghost handled by caller)
        """
        # Try gRPC first (when stubs are available)
        try:
            return await self._try_grpc(method, request)
        except ConnectionError:
            pass  # Fall through to local servicer

        # Try local servicer as fallback
        if self.use_local_servicer:
            try:
                return await self._try_local_servicer(method, request)
            except Exception:
                pass  # Fall through to raise error

        # Both failed - let caller handle Ghost fallback
        raise ConnectionError(
            f"Cortex daemon unavailable at {self.address}. "
            "Local servicer also unavailable."
        )

    async def _try_grpc(self, method: str, request: Any) -> Any:
        """
        Try gRPC call to Cortex daemon.

        Raises ConnectionError if gRPC is not available or fails.
        """
        try:
            import grpc
            from protocols.proto.generated import LogosStub
        except ImportError as e:
            raise ConnectionError(f"gRPC not available: {e}")

        try:
            # Create async channel with fast timeout for connection
            channel = grpc.aio.insecure_channel(
                self.address,
                options=[
                    ("grpc.connect_timeout_ms", int(self.timeout * 1000)),
                ],
            )

            # Create stub and invoke method
            stub = LogosStub(channel)  # type: ignore[no-untyped-call]
            grpc_method = getattr(stub, method, None)
            if grpc_method is None:
                raise ConnectionError(f"Unknown gRPC method: {method}")

            # Call with timeout
            response = await asyncio.wait_for(
                grpc_method(request),
                timeout=self.timeout,
            )

            await channel.close()
            return response

        except asyncio.TimeoutError:
            raise ConnectionError(f"gRPC timeout connecting to {self.address}")
        except grpc.RpcError as e:
            raise ConnectionError(f"gRPC error: {e.code()} - {e.details()}")

    async def _try_local_servicer(self, method: str, request: Any) -> Any:
        """
        Try local CortexServicer (in-process fallback).

        This provides functionality when gRPC daemon is not running,
        but with reduced capabilities (no K8s integration, etc.).
        """
        if self._local_servicer is None:
            try:
                from infra.cortex import create_cortex_servicer
                from protocols.cli.hollow import get_lifecycle_state

                # Create servicer with lifecycle state if available
                lifecycle_state = get_lifecycle_state()
                self._local_servicer = create_cortex_servicer(
                    lifecycle_state=lifecycle_state
                )
            except ImportError as e:
                raise ConnectionError(f"Local servicer not available: {e}")

        # Map method to servicer method
        servicer_method = getattr(self._local_servicer, method, None)
        if servicer_method is None:
            raise ConnectionError(f"Method {method} not implemented in local servicer")

        # Call the servicer method
        result = await servicer_method(request)
        return result

    def _serialize_for_cache(self, data: Any) -> Any:
        """
        Serialize data for Ghost cache storage.

        Handles protobuf messages, dataclasses, and plain dicts.
        """
        # Check for protobuf Message type (from google.protobuf)
        try:
            from google.protobuf.json_format import MessageToDict

            if hasattr(data, "DESCRIPTOR"):
                # It's a protobuf message
                return MessageToDict(data, preserving_proto_field_name=True)
        except ImportError:
            pass

        # If it has a to_dict method (protobuf style), use it
        if hasattr(data, "to_dict"):
            return data.to_dict()

        # If it's a dataclass, convert to dict
        if hasattr(data, "__dataclass_fields__"):
            from dataclasses import asdict

            return asdict(data)

        # If it's already JSON-serializable, use as-is
        return data

    def write_ghost(
        self,
        key: str,
        data: Any,
        agentese_path: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Manually write to Ghost cache (for thick handlers like infra).

        Some commands (like `kgents infra`) need to write to Ghost cache
        even though they don't use gRPC. This method provides direct access.

        Args:
            key: Cache key (e.g., "status", "agents/l-gent")
            data: Data to cache
            agentese_path: AGENTESE path for tracing
            metadata: Additional metadata
        """
        self.ghost_cache.write(
            key=key,
            data=data,
            agentese_path=agentese_path,
            metadata=metadata,
        )

    def read_ghost(self, key: str) -> GlassResponse | None:
        """
        Manually read from Ghost cache.

        Returns None if no cached data exists.
        """
        data, age, timestamp = self.ghost_cache.read(key)
        if data is None:
            return None

        return GlassResponse(
            data=data,
            is_ghost=True,
            ghost_age=age,
            ghost_timestamp=timestamp,
        )


# =============================================================================
# Convenience Functions
# =============================================================================


def get_glass_client() -> GlassClient:
    """
    Get a GlassClient instance with default configuration.

    This is the recommended way to get a client for CLI handlers.
    """
    return GlassClient()


def seed_ghost_cache(initial_data: dict[str, Any]) -> None:
    """
    Seed the Ghost cache with initial data.

    Used by `kgents infra init` after successful infrastructure setup
    to ensure Ghost cache has baseline data.

    Args:
        initial_data: Dict mapping cache keys to data
                      e.g., {"status": {...}, "meta": {...}}
    """
    cache = GhostCache()
    for key, data in initial_data.items():
        cache.write(key=key, data=data, agentese_path=f"self.{key}.manifest")


def clear_ghost_cache() -> None:
    """
    Clear the entire Ghost cache.

    Used by `kgents wipe` or for testing.
    """
    import shutil

    if GHOST_DIR.exists():
        shutil.rmtree(GHOST_DIR)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "GlassClient",
    "GlassResponse",
    "GhostCache",
    "GhostCacheEntry",
    "get_glass_client",
    "seed_ghost_cache",
    "clear_ghost_cache",
    "GHOST_DIR",
    "GRPC_TIMEOUT",
    "DEFAULT_GRPC_ADDRESS",
]
