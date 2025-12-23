"""
Proxy Handle Service: Epistemic hygiene for computed data.

AD-015: Proxy Handles & Transparent Batch Processes

Every expensive computation produces a proxy handle—an independent artifact
with its own identity, lifecycle, and provenance. This makes data staleness,
computation state, and refresh mechanics explicit and transparent.

Core Abstractions:
    ProxyHandle[T] — Generic handle with identity, lifecycle, provenance
    ProxyHandleStore — Lifecycle manager with get(), compute(), invalidate()
    ProxyHandleEvent — Events for transparency

State Machine:
    EMPTY → COMPUTING → FRESH → STALE → (cycle)
            ↓
          ERROR

Laws:
    1. Explicit Computation: compute() is the ONLY way to create handles
    2. Provenance Preservation: Every handle knows its origin
    3. Event Transparency: Every state transition emits events
    4. No Anonymous Debris: human_label is required
    5. Idempotent Computation: Concurrent compute() awaits same work

Example:
    from services.proxy import (
        ProxyHandleStore,
        SourceType,
        NoProxyHandleError,
    )

    store = ProxyHandleStore()

    # Explicit computation (AD-015)
    handle = await store.compute(
        source_type=SourceType.SPEC_CORPUS,
        compute_fn=analyze_corpus,
        human_label="Spec corpus analysis",
    )

    # Get existing or raise
    try:
        handle = await store.get_or_raise(SourceType.SPEC_CORPUS)
        use(handle.data)
    except NoProxyHandleError:
        # Surface to user: "Run computation to generate"
        pass

AGENTESE: services.proxy
"""

from .exceptions import (
    ComputationError,
    ComputationInProgressError,
    NoPreComputedDataError,
    NoProxyHandleError,
    ProxyHandleError,
    StaleHandleError,
)
from .store import (
    ProxyHandleEventCallback,
    ProxyHandleStore,
    ProxyStoreStats,
    Unsubscribe,
    get_proxy_handle_store,
    reset_proxy_handle_store,
)
from .types import (
    HandleStatus,
    ProxyHandle,
    ProxyHandleEvent,
    ProxyHandleEventType,
    SourceType,
)

__all__ = [
    # Core types
    "ProxyHandle",
    "HandleStatus",
    "SourceType",
    # Events
    "ProxyHandleEvent",
    "ProxyHandleEventType",
    # Store
    "ProxyHandleStore",
    "ProxyStoreStats",
    "ProxyHandleEventCallback",
    "Unsubscribe",
    # Factory
    "get_proxy_handle_store",
    "reset_proxy_handle_store",
    # Exceptions
    "ProxyHandleError",
    "NoProxyHandleError",
    "ComputationError",
    "ComputationInProgressError",
    "StaleHandleError",
    # Backward compatibility
    "NoPreComputedDataError",
]
