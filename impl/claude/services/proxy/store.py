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

    Composite Keys (AD-015 extension):
        For multi-instance caching (e.g., multiple validation initiatives),
        pass a `key` parameter to create composite keys:

        # Without key: one handle per source_type
        await store.compute(source_type=SourceType.SPEC_CORPUS, ...)

        # With key: multiple handles per source_type
        await store.compute(source_type=SourceType.VALIDATION_RUN, key="brain:phase1", ...)
        await store.compute(source_type=SourceType.VALIDATION_RUN, key="brain:phase2", ...)

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
    # Keys are composite: "{source_type.value}" or "{source_type.value}:{key}"
    _handles: dict[str, ProxyHandle[Any]] = field(default_factory=dict, repr=False)
    _compute_locks: dict[str, asyncio.Lock] = field(default_factory=dict, repr=False)
    _compute_futures: dict[str, asyncio.Future[ProxyHandle[Any]]] = field(
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
    # Key Management
    # =========================================================================

    @staticmethod
    def _make_key(source_type: SourceType, key: str | None = None) -> str:
        """
        Create composite key for handle storage.

        Args:
            source_type: The source type (semantic category)
            key: Optional disambiguation key for multi-instance caching

        Returns:
            Composite key string: "{source_type}" or "{source_type}:{key}"
        """
        if key:
            return f"{source_type.value}:{key}"
        return source_type.value

    # =========================================================================
    # Core Operations
    # =========================================================================

    async def get(self, source_type: SourceType, key: str | None = None) -> ProxyHandle[Any] | None:
        """
        Get existing handle, or None if doesn't exist.

        Does NOT trigger computation. For explicit computation, use compute().

        Args:
            source_type: The source type to look up
            key: Optional disambiguation key for multi-instance caching
        """
        composite_key = self._make_key(source_type, key)
        with self._lock:
            handle = self._handles.get(composite_key)
            if handle:
                handle.access()
                await self._emit(
                    ProxyHandleEvent(
                        event_type="handle_accessed",
                        source_type=source_type,
                        handle_id=handle.handle_id,
                        details={"is_fresh": handle.is_fresh(), "key": key},
                    )
                )
            return handle

    async def get_or_raise(
        self, source_type: SourceType, key: str | None = None
    ) -> ProxyHandle[Any]:
        """
        Get existing handle, or raise NoProxyHandleError.

        AD-015: This is the preferred method for code that requires data.
        It makes the absence of data explicit, enabling proper error handling.

        Args:
            source_type: The source type to look up
            key: Optional disambiguation key for multi-instance caching
        """
        handle = await self.get(source_type, key)
        if handle is None:
            composite_key = self._make_key(source_type, key)
            raise NoProxyHandleError(source_type, f"No handle for '{composite_key}'")
        return handle

    async def get_fresh_or_raise(
        self, source_type: SourceType, key: str | None = None
    ) -> ProxyHandle[Any]:
        """
        Get existing FRESH handle, or raise NoProxyHandleError.

        Use when stale data is not acceptable.

        Args:
            source_type: The source type to look up
            key: Optional disambiguation key for multi-instance caching
        """
        handle = await self.get_or_raise(source_type, key)
        if not handle.is_fresh():
            composite_key = self._make_key(source_type, key)
            raise NoProxyHandleError(
                source_type,
                f"Proxy handle for '{composite_key}' exists but is stale. "
                f"Use compute(force=True) to refresh.",
            )
        return handle

    async def compute(
        self,
        source_type: SourceType,
        compute_fn: Callable[[], Awaitable[T]],
        *,
        key: str | None = None,
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
        2. Acquires per-key lock (prevents duplicate work)
        3. Runs compute_fn and creates handle
        4. Emits events for transparency
        5. Persists if configured

        Idempotency: Concurrent calls for same key await the same
        computation. This prevents duplicate expensive work.

        Args:
            source_type: What this is a proxy for
            compute_fn: Async function that produces the data
            key: Optional disambiguation key for multi-instance caching
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

        composite_key = self._make_key(source_type, key)

        # Check for existing fresh handle (fast path)
        if not force:
            with self._lock:
                existing = self._handles.get(composite_key)
                if existing and existing.is_fresh():
                    existing.access()
                    return existing

        # Get or create lock for this composite key
        lock = self._get_or_create_lock(composite_key)

        async with lock:
            # Double-check after acquiring lock
            if not force:
                with self._lock:
                    existing = self._handles.get(composite_key)
                    if existing and existing.is_fresh():
                        existing.access()
                        return existing

            # Check for in-progress computation (idempotency)
            with self._lock:
                if composite_key in self._compute_futures:
                    existing_future = self._compute_futures[composite_key]
                    if not existing_future.done():
                        logger.debug(f"Awaiting existing computation for {composite_key}")
                        return await existing_future

                # Create future for this computation
                loop = asyncio.get_event_loop()
                new_future: asyncio.Future[ProxyHandle[Any]] = loop.create_future()
                self._compute_futures[composite_key] = new_future

            # Mark as computing
            await self._emit(
                ProxyHandleEvent(
                    event_type="computation_started",
                    source_type=source_type,
                    handle_id=None,
                    details={"force": force, "computed_by": computed_by, "key": key},
                )
            )

            start_time = time.time()
            try:
                # Run computation
                data = await compute_fn()
                duration = time.time() - start_time

                # Get previous computation count
                with self._lock:
                    prev = self._handles.get(composite_key)
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

                # Store handle with composite key
                with self._lock:
                    self._handles[composite_key] = handle
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
                            "key": key,
                        },
                    )
                )

                # Resolve future for waiters
                with self._lock:
                    if composite_key in self._compute_futures:
                        self._compute_futures[composite_key].set_result(handle)
                        del self._compute_futures[composite_key]

                logger.info(f"Computed proxy handle for {composite_key} in {duration:.2f}s")
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
                    self._handles[composite_key] = error_handle

                # Emit failure event
                await self._emit(
                    ProxyHandleEvent(
                        event_type="computation_failed",
                        source_type=source_type,
                        handle_id=error_handle.handle_id,
                        details={"error": str(e), "duration": duration, "key": key},
                    )
                )

                # Reject future for waiters
                with self._lock:
                    if composite_key in self._compute_futures:
                        self._compute_futures[composite_key].set_exception(e)
                        del self._compute_futures[composite_key]

                logger.error(f"Computation failed for {composite_key}: {e}")
                raise ComputationError(source_type, e) from e

    async def invalidate(self, source_type: SourceType, key: str | None = None) -> bool:
        """
        Mark a handle as STALE (source changed).

        Use when you know the source has changed but don't want to
        recompute immediately. Agents can decide when to refresh.

        Args:
            source_type: The source type to invalidate
            key: Optional disambiguation key for multi-instance caching

        Returns:
            True if handle was invalidated, False if no handle exists
        """
        composite_key = self._make_key(source_type, key)
        with self._lock:
            handle = self._handles.get(composite_key)
            if handle is None:
                return False

            if handle.status == HandleStatus.COMPUTING:
                logger.warning(f"Cannot invalidate {composite_key} - computation in progress")
                return False

            handle.status = HandleStatus.STALE

        await self._emit(
            ProxyHandleEvent(
                event_type="handle_invalidated",
                source_type=source_type,
                handle_id=handle.handle_id,
                details={"key": key},
            )
        )

        await self._persist_if_enabled()
        return True

    async def delete(self, source_type: SourceType, key: str | None = None) -> bool:
        """
        Remove a handle entirely.

        Args:
            source_type: The source type to delete
            key: Optional disambiguation key for multi-instance caching

        Returns:
            True if handle was deleted, False if no handle exists
        """
        composite_key = self._make_key(source_type, key)
        with self._lock:
            handle = self._handles.get(composite_key)
            if handle is None:
                return False

            del self._handles[composite_key]

        await self._emit(
            ProxyHandleEvent(
                event_type="handle_deleted",
                source_type=source_type,
                handle_id=handle.handle_id,
                details={"key": key},
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

    def keys(self) -> list[str]:
        """Get all composite keys that have handles."""
        with self._lock:
            return list(self._handles.keys())

    def source_types(self) -> list[SourceType]:
        """
        Get unique source types that have handles.

        Note: With composite keys, multiple handles may share the same source_type.
        This returns the deduplicated set of source types.
        """
        with self._lock:
            seen: set[SourceType] = set()
            for handle in self._handles.values():
                seen.add(handle.source_type)
            return list(seen)

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

    def _get_or_create_lock(self, composite_key: str) -> asyncio.Lock:
        """Get or create an asyncio.Lock for a composite key."""
        with self._lock:
            if composite_key not in self._compute_locks:
                self._compute_locks[composite_key] = asyncio.Lock()
            return self._compute_locks[composite_key]

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
                # Keys are now composite strings (e.g., "validation_run:brain:phase1")
                data = {key: handle.to_dict() for key, handle in self._handles.items()}

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

            for composite_key, handle_data in data.items():
                try:
                    handle = ProxyHandle.from_dict(handle_data)
                    # Use composite key directly (supports both old and new format)
                    self._handles[composite_key] = handle
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping invalid handle data for {composite_key}: {e}")

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
