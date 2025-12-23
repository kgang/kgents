"""
Proxy Handle Store: Lifecycle management for computed data.

AD-015: Proxy Handles & Transparent Batch Processes

Core responsibilities:
    1. Store handles (in-memory with optional persistence)
    2. Track staleness via source hash and TTL
    3. Coordinate computation (prevent duplicate work)
    4. Emit events for transparency

The key insight: Computation is ALWAYS explicit. There is no auto-compute.

Laws enforced:
    1. Explicit Computation: compute() is the ONLY way to create handles
    2. Provenance Preservation: Every handle knows its origin
    3. Event Transparency: Every state transition emits events
    4. No Anonymous Debris: human_label is required
    5. Idempotent Computation: Concurrent compute() awaits same work

AGENTESE: services.proxy.store
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Generic, TypeVar

from .exceptions import ComputationError, NoProxyHandleError
from .types import HandleStatus, ProxyHandle, ProxyHandleEvent, SourceType

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Type alias for event callbacks
ProxyHandleEventCallback = Callable[[ProxyHandleEvent], None]
Unsubscribe = Callable[[], None]


# =============================================================================
# Store Statistics
# =============================================================================


@dataclass
class ProxyStoreStats:
    """Statistics about proxy handle store."""

    total_handles: int
    fresh_count: int
    stale_count: int
    computing_count: int
    error_count: int
    total_computations: int
    total_computation_time: float
    avg_computation_time: float


# =============================================================================
# Proxy Handle Store
# =============================================================================


@dataclass
class ProxyHandleStore:
    """
    Manages proxy handle lifecycle across the system.

    Thread-safe, supports concurrent access with proper locking.
    Uses asyncio.Lock for per-source_type computation coordination.

    Example:
        store = ProxyHandleStore()

        # Explicit computation (AD-015)
        handle = await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=analyze_corpus,
            human_label="Spec corpus analysis",
            ttl=timedelta(minutes=5),
        )

        # Get existing handle (raises if not computed)
        handle = await store.get_or_raise(SourceType.SPEC_CORPUS)

        # Subscribe to lifecycle events
        def on_event(event: ProxyHandleEvent) -> None:
            print(f"Event: {event.event_type} for {event.source_type}")

        unsubscribe = store.subscribe(on_event)
    """

    # Configuration
    persist_path: Path | None = None
    default_ttl: timedelta = field(default_factory=lambda: timedelta(minutes=5))

    # Internal state (initialized in __post_init__)
    _handles: dict[SourceType, ProxyHandle[Any]] = field(default_factory=dict, repr=False)
    _compute_locks: dict[SourceType, asyncio.Lock] = field(default_factory=dict, repr=False)
    _compute_futures: dict[SourceType, asyncio.Future[ProxyHandle[Any]]] = field(
        default_factory=dict, repr=False
    )
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)
    _callbacks: list[ProxyHandleEventCallback] = field(default_factory=list, repr=False)

    # Metrics
    _total_computations: int = field(default=0, repr=False)
    _total_computation_time: float = field(default=0.0, repr=False)

    def __post_init__(self) -> None:
        """Initialize store, optionally loading from persistence."""
        if self.persist_path:
            self._load_from_disk()

    # =========================================================================
    # Core Operations
    # =========================================================================

    async def get(self, source_type: SourceType) -> ProxyHandle[Any] | None:
        """
        Get existing handle, or None if doesn't exist.

        Does NOT trigger computation. For explicit computation, use compute().
        """
        with self._lock:
            handle = self._handles.get(source_type)
            if handle:
                handle.access()
                await self._emit(
                    ProxyHandleEvent(
                        event_type="handle_accessed",
                        source_type=source_type,
                        handle_id=handle.handle_id,
                        details={"is_fresh": handle.is_fresh()},
                    )
                )
            return handle

    async def get_or_raise(self, source_type: SourceType) -> ProxyHandle[Any]:
        """
        Get existing handle, or raise NoProxyHandleError.

        AD-015: This is the preferred method for code that requires data.
        It makes the absence of data explicit, enabling proper error handling.
        """
        handle = await self.get(source_type)
        if handle is None:
            raise NoProxyHandleError(source_type)
        return handle

    async def get_fresh_or_raise(self, source_type: SourceType) -> ProxyHandle[Any]:
        """
        Get existing FRESH handle, or raise NoProxyHandleError.

        Use when stale data is not acceptable.
        """
        handle = await self.get_or_raise(source_type)
        if not handle.is_fresh():
            raise NoProxyHandleError(
                source_type,
                f"Proxy handle for '{source_type.value}' exists but is stale. "
                f"Use compute(force=True) to refresh.",
            )
        return handle

    async def compute(
        self,
        source_type: SourceType,
        compute_fn: Callable[[], Awaitable[T]],
        *,
        force: bool = False,
        ttl: timedelta | None = None,
        human_label: str,
        computed_by: str = "system",
        source_hash: str | None = None,
    ) -> ProxyHandle[T]:
        """
        Explicit computation — the ONLY way to create/refresh handles.

        AD-015: Computation is always explicit. This method:
        1. Checks if fresh handle exists (returns it unless force=True)
        2. Acquires per-source_type lock (prevents duplicate work)
        3. Runs compute_fn and creates handle
        4. Emits events for transparency
        5. Persists if configured

        Idempotency: Concurrent calls for same source_type await the same
        computation. This prevents duplicate expensive work.

        Args:
            source_type: What this is a proxy for
            compute_fn: Async function that produces the data
            force: Force recomputation even if fresh handle exists
            ttl: Time to live (defaults to store default)
            human_label: REQUIRED - explains what this is
            computed_by: Who/what triggered this computation
            source_hash: Optional hash of source for staleness detection

        Returns:
            ProxyHandle with computed data

        Raises:
            ComputationError: If compute_fn raises
        """
        if not human_label:
            raise ValueError("human_label is required (no anonymous debris)")

        # Check for existing fresh handle (fast path)
        if not force:
            with self._lock:
                existing = self._handles.get(source_type)
                if existing and existing.is_fresh():
                    existing.access()
                    return existing

        # Get or create lock for this source type
        lock = self._get_or_create_lock(source_type)

        async with lock:
            # Double-check after acquiring lock
            if not force:
                with self._lock:
                    existing = self._handles.get(source_type)
                    if existing and existing.is_fresh():
                        existing.access()
                        return existing

            # Check for in-progress computation (idempotency)
            with self._lock:
                if source_type in self._compute_futures:
                    existing_future = self._compute_futures[source_type]
                    if not existing_future.done():
                        logger.debug(f"Awaiting existing computation for {source_type.value}")
                        return await existing_future

                # Create future for this computation
                loop = asyncio.get_event_loop()
                new_future: asyncio.Future[ProxyHandle[Any]] = loop.create_future()
                self._compute_futures[source_type] = new_future

            # Mark as computing
            await self._emit(
                ProxyHandleEvent(
                    event_type="computation_started",
                    source_type=source_type,
                    handle_id=None,
                    details={"force": force, "computed_by": computed_by},
                )
            )

            start_time = time.time()
            try:
                # Run computation
                data = await compute_fn()
                duration = time.time() - start_time

                # Get previous computation count
                with self._lock:
                    prev = self._handles.get(source_type)
                    prev_count = prev.computation_count if prev else 0

                # Create handle
                handle: ProxyHandle[T] = ProxyHandle(
                    source_type=source_type,
                    human_label=human_label,
                    status=HandleStatus.FRESH,
                    created_at=datetime.now(),
                    ttl=ttl or self.default_ttl,
                    source_hash=source_hash,
                    data=data,
                    computed_by=computed_by,
                    computation_duration=duration,
                    computation_count=prev_count + 1,
                )

                # Store handle
                with self._lock:
                    self._handles[source_type] = handle
                    self._total_computations += 1
                    self._total_computation_time += duration

                # Persist if configured
                await self._persist_if_enabled()

                # Emit success event
                await self._emit(
                    ProxyHandleEvent(
                        event_type="computation_completed",
                        source_type=source_type,
                        handle_id=handle.handle_id,
                        details={
                            "duration": duration,
                            "computation_count": handle.computation_count,
                        },
                    )
                )

                # Resolve future for waiters
                with self._lock:
                    if source_type in self._compute_futures:
                        self._compute_futures[source_type].set_result(handle)
                        del self._compute_futures[source_type]

                logger.info(f"Computed proxy handle for {source_type.value} in {duration:.2f}s")
                return handle

            except Exception as e:
                duration = time.time() - start_time

                # Create error handle
                error_handle: ProxyHandle[T] = ProxyHandle(
                    source_type=source_type,
                    human_label=human_label,
                    status=HandleStatus.ERROR,
                    error=str(e),
                    computed_by=computed_by,
                    computation_duration=duration,
                )

                with self._lock:
                    self._handles[source_type] = error_handle

                # Emit failure event
                await self._emit(
                    ProxyHandleEvent(
                        event_type="computation_failed",
                        source_type=source_type,
                        handle_id=error_handle.handle_id,
                        details={"error": str(e), "duration": duration},
                    )
                )

                # Reject future for waiters
                with self._lock:
                    if source_type in self._compute_futures:
                        self._compute_futures[source_type].set_exception(e)
                        del self._compute_futures[source_type]

                logger.error(f"Computation failed for {source_type.value}: {e}")
                raise ComputationError(source_type, e) from e

    async def invalidate(self, source_type: SourceType) -> bool:
        """
        Mark a handle as STALE (source changed).

        Use when you know the source has changed but don't want to
        recompute immediately. Agents can decide when to refresh.

        Returns:
            True if handle was invalidated, False if no handle exists
        """
        with self._lock:
            handle = self._handles.get(source_type)
            if handle is None:
                return False

            if handle.status == HandleStatus.COMPUTING:
                logger.warning(f"Cannot invalidate {source_type.value} - computation in progress")
                return False

            handle.status = HandleStatus.STALE

        await self._emit(
            ProxyHandleEvent(
                event_type="handle_invalidated",
                source_type=source_type,
                handle_id=handle.handle_id,
                details={},
            )
        )

        await self._persist_if_enabled()
        return True

    async def delete(self, source_type: SourceType) -> bool:
        """
        Remove a handle entirely.

        Returns:
            True if handle was deleted, False if no handle exists
        """
        with self._lock:
            handle = self._handles.get(source_type)
            if handle is None:
                return False

            del self._handles[source_type]

        await self._emit(
            ProxyHandleEvent(
                event_type="handle_deleted",
                source_type=source_type,
                handle_id=handle.handle_id,
                details={},
            )
        )

        await self._persist_if_enabled()
        return True

    # =========================================================================
    # Query Operations
    # =========================================================================

    def all(self) -> list[ProxyHandle[Any]]:
        """Get all handles."""
        with self._lock:
            return list(self._handles.values())

    def source_types(self) -> list[SourceType]:
        """Get all source types that have handles."""
        with self._lock:
            return list(self._handles.keys())

    def stats(self) -> ProxyStoreStats:
        """Get store statistics."""
        with self._lock:
            handles = list(self._handles.values())
            fresh = sum(1 for h in handles if h.is_fresh())
            stale = sum(1 for h in handles if h.is_stale())
            computing = sum(1 for h in handles if h.is_computing())
            error = sum(1 for h in handles if h.is_error())

            avg_time = (
                self._total_computation_time / self._total_computations
                if self._total_computations > 0
                else 0.0
            )

            return ProxyStoreStats(
                total_handles=len(handles),
                fresh_count=fresh,
                stale_count=stale,
                computing_count=computing,
                error_count=error,
                total_computations=self._total_computations,
                total_computation_time=self._total_computation_time,
                avg_computation_time=avg_time,
            )

    # =========================================================================
    # Event Subscription
    # =========================================================================

    def subscribe(self, callback: ProxyHandleEventCallback) -> Unsubscribe:
        """
        Subscribe to lifecycle events for transparency.

        Returns:
            Unsubscribe function to remove the callback
        """
        with self._lock:
            self._callbacks.append(callback)

        def unsubscribe() -> None:
            with self._lock:
                if callback in self._callbacks:
                    self._callbacks.remove(callback)

        return unsubscribe

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    def _get_or_create_lock(self, source_type: SourceType) -> asyncio.Lock:
        """Get or create an asyncio.Lock for a source type."""
        with self._lock:
            if source_type not in self._compute_locks:
                self._compute_locks[source_type] = asyncio.Lock()
            return self._compute_locks[source_type]

    async def _emit(self, event: ProxyHandleEvent) -> None:
        """
        Emit event to all subscribers.

        Non-blocking: failures don't affect store operations.
        """
        with self._lock:
            callbacks = list(self._callbacks)

        for callback in callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.warning(f"Event callback error: {e}")

        # Also emit to WitnessSynergyBus if available
        await self._emit_to_bus(event)

    async def _emit_to_bus(self, event: ProxyHandleEvent) -> None:
        """
        Non-blocking event emission to WitnessSynergyBus.

        Graceful degradation: if bus not available, skip silently.
        """
        try:
            from services.witness.bus import WitnessTopics, get_synergy_bus

            bus = get_synergy_bus()
            if bus is None:
                return

            topic_map = {
                "computation_started": WitnessTopics.PROXY_STARTED,
                "computation_completed": WitnessTopics.PROXY_COMPLETED,
                "computation_failed": WitnessTopics.PROXY_FAILED,
                "handle_stale": WitnessTopics.PROXY_STALE,
            }

            topic = topic_map.get(event.event_type)
            if topic:
                # Non-blocking publish
                asyncio.create_task(bus.publish(topic, event.to_dict()))

        except ImportError:
            # WitnessBus not available - graceful degradation
            pass
        except Exception as e:
            # Never let bus errors affect store operations
            logger.debug(f"Bus emission skipped: {e}")

    # =========================================================================
    # Persistence
    # =========================================================================

    async def _persist_if_enabled(self) -> None:
        """Persist handles to disk if configured."""
        if self.persist_path is None:
            return

        try:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)

            with self._lock:
                data = {st.value: handle.to_dict() for st, handle in self._handles.items()}

            content = json.dumps(data, indent=2)
            self.persist_path.write_text(content)

        except Exception as e:
            logger.warning(f"Failed to persist proxy handles: {e}")

    def _load_from_disk(self) -> None:
        """Load handles from disk if file exists."""
        if self.persist_path is None or not self.persist_path.exists():
            return

        try:
            content = self.persist_path.read_text()
            data = json.loads(content)

            for source_type_str, handle_data in data.items():
                try:
                    source_type = SourceType(source_type_str)
                    handle = ProxyHandle.from_dict(handle_data)
                    self._handles[source_type] = handle
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping invalid handle data: {e}")

            logger.info(f"Loaded {len(self._handles)} proxy handles from disk")

        except Exception as e:
            logger.warning(f"Failed to load proxy handles: {e}")


# =============================================================================
# Singleton Factory
# =============================================================================

_store: ProxyHandleStore | None = None
_store_lock = threading.Lock()


def get_proxy_handle_store(
    persist_path: Path | None = None,
    default_ttl: timedelta | None = None,
) -> ProxyHandleStore:
    """
    Get the singleton ProxyHandleStore instance.

    First call creates the instance with provided configuration.
    Subsequent calls return the same instance (ignoring arguments).

    For testing, use reset_proxy_handle_store() to clear the singleton.
    """
    global _store
    with _store_lock:
        if _store is None:
            _store = ProxyHandleStore(
                persist_path=persist_path,
                default_ttl=default_ttl or timedelta(minutes=5),
            )
        return _store


def reset_proxy_handle_store() -> None:
    """Reset the singleton store (for testing)."""
    global _store
    with _store_lock:
        _store = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core class
    "ProxyHandleStore",
    # Stats
    "ProxyStoreStats",
    # Type aliases
    "ProxyHandleEventCallback",
    "Unsubscribe",
    # Factory
    "get_proxy_handle_store",
    "reset_proxy_handle_store",
]
