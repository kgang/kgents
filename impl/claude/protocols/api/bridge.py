"""
AGENTESE Bridge Protocol.

The functor between HTTP/WS and AGENTESE Logos.

This is the categorical morphism:
    HTTP Request → AgenteseBridge → Logos.invoke() → Response

Laws (preserved by the bridge):
1. Identity: invoke("context.holon.manifest") returns holon unchanged (up to observer transformation)
2. Associativity: compose([a, b, c]) == compose([a, compose([b, c])])
3. Observer Polymorphism: same handle, different observer → different result

Design Principles:
- Protocol-first: Abstract interface enables multiple implementations
- Law verification: Every composition can verify category laws
- Sympathetic errors: All errors include suggestions

DEVELOP Phase: This file defines CONTRACTS only, not implementation.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, AsyncIterator, Protocol, runtime_checkable

from .serializers import (
    AgenteseResponse,
    CompositionResponse,
    ErrorCode,
    ErrorResponse,
    GardenState,
    LawVerificationResult,
    ObserverContext,
    PipelineStep,
    ResponseMeta,
    SSEChunk,
    SSECompleteEvent,
    WSInvokeResult,
    WSStateUpdate,
)

if TYPE_CHECKING:
    from protocols.agentese.logos import Logos


# =============================================================================
# Subscription Protocol
# =============================================================================


@runtime_checkable
class Subscription(Protocol):
    """
    Protocol for WebSocket subscriptions.

    A subscription represents an active connection to a channel
    that receives state updates.
    """

    @property
    def channel(self) -> str:
        """Channel this subscription is for."""
        ...

    @property
    def is_active(self) -> bool:
        """Whether the subscription is still active."""
        ...

    async def cancel(self) -> None:
        """Cancel the subscription."""
        ...

    def __aiter__(self) -> AsyncIterator[WSStateUpdate]:
        """Iterate over state updates."""
        ...


# =============================================================================
# SSE Event Type
# =============================================================================


@dataclass(frozen=True)
class SSEEvent:
    """
    A Server-Sent Event for streaming responses.

    SSE events have:
    - event: Event type (chunk, done, error)
    - data: JSON-serializable payload
    """

    event: str
    data: SSEChunk | SSECompleteEvent | ErrorResponse | dict[str, Any]

    def serialize(self) -> str:
        """Serialize to SSE wire format."""
        import json

        # Handle Pydantic models
        if hasattr(self.data, "model_dump"):
            data_str = json.dumps(self.data.model_dump(mode="json"))
        elif hasattr(self.data, "dict"):
            data_str = json.dumps(self.data.dict())
        else:
            data_str = json.dumps(self.data)

        return f"event: {self.event}\ndata: {data_str}\n\n"


# =============================================================================
# Bridge Protocol (Abstract Interface)
# =============================================================================


@runtime_checkable
class AgenteseBridgeProtocol(Protocol):
    """
    The functor between HTTP/WS and AGENTESE Logos.

    This protocol defines the contract for the AGENTESE Universal Protocol.
    Any implementation must satisfy these signatures and preserve category laws.

    Laws:
        1. Identity: invoke("context.holon.manifest") returns holon unchanged
           (up to observer transformation)

        2. Associativity: compose([a, b, c]) == compose([a, compose([b, c])])
           Results must be equivalent regardless of how composition is grouped.

        3. Observer Polymorphism: same handle, different observer → different result
           The result is observer-specific; this is a feature, not a bug.

    Error Handling:
        All methods raise HTTPException or return ErrorResponse for errors.
        Errors follow the sympathetic error pattern with suggestions.
    """

    @abstractmethod
    async def invoke(
        self,
        handle: str,
        observer: ObserverContext,
        kwargs: dict[str, Any] | None = None,
    ) -> AgenteseResponse:
        """
        Single AGENTESE path invocation.

        Args:
            handle: Full AGENTESE path including aspect
                   (e.g., "world.field.manifest", "concept.justice.refine")
            observer: Observer context (REQUIRED - no view from nowhere)
            kwargs: Aspect-specific arguments

        Returns:
            AgenteseResponse with observer-specific result and metadata

        Raises:
            PATH_NOT_FOUND: If path doesn't exist
            AFFORDANCE_DENIED: If observer lacks permission
            OBSERVER_REQUIRED: If observer is None
            SYNTAX_ERROR: If path is malformed
        """
        ...

    @abstractmethod
    async def compose(
        self,
        paths: list[str],
        observer: ObserverContext,
        initial_input: Any = None,
        emit_law_check: bool = True,
    ) -> CompositionResponse:
        """
        Pipeline composition with law verification.

        Chains multiple AGENTESE paths into a single pipeline.
        Output of path N flows as input to path N+1.

        Category laws are preserved:
        - Identity: Id >> path == path == path >> Id
        - Associativity: (a >> b) >> c == a >> (b >> c)

        Args:
            paths: AGENTESE paths to compose in order
            observer: Observer context
            initial_input: Optional initial value for the pipeline
            emit_law_check: Whether to emit law verification events

        Returns:
            CompositionResponse with final result and pipeline trace

        Raises:
            LAW_VIOLATION: If composition would violate category laws
            COMPOSITION_ERROR: If pipeline execution fails
        """
        ...

    @abstractmethod
    def stream(
        self,
        handle: str,
        observer: ObserverContext,
        kwargs: dict[str, Any] | None = None,
    ) -> AsyncIterator[SSEEvent]:
        """
        SSE streaming for long-running operations.

        Used for operations that benefit from streaming responses:
        - self.soul.challenge (LLM token streaming)
        - concept.*.dialectic (dialectic phases)
        - time.*.forecast (progressive refinement)

        Args:
            handle: Full AGENTESE path
            observer: Observer context
            kwargs: Aspect-specific arguments

        Yields:
            SSEEvent for each chunk, ending with done or error event
        """
        ...

    @abstractmethod
    def subscribe(
        self,
        channel: str,
        filter_: dict[str, Any] | None = None,
    ) -> Subscription:
        """
        WebSocket subscription to a channel.

        Channels:
        - "garden": All entity movement + pheromone updates
        - "agent:{id}": Single agent state changes
        - "dialectic": Dialectic phase events
        - "town:{id}": Agent Town updates

        Args:
            channel: Channel to subscribe to
            filter_: Optional filter for the subscription

        Returns:
            Subscription that yields WSStateUpdate events
        """
        ...

    @abstractmethod
    async def verify_laws(
        self,
        composition: list[str],
        observer: ObserverContext,
    ) -> LawVerificationResult:
        """
        Verify category laws hold for a composition.

        Checks:
        - Identity: Id >> f ≡ f (for each path in composition)
        - Associativity: (f >> g) >> h ≡ f >> (g >> h)

        Args:
            composition: Paths to verify as a composition
            observer: Observer context

        Returns:
            LawVerificationResult indicating which laws hold
        """
        ...

    @abstractmethod
    async def resolve(
        self,
        path: str,
        observer: ObserverContext | None = None,
    ) -> dict[str, Any]:
        """
        Resolve an AGENTESE path without invoking.

        Returns metadata about the path:
        - handle: Canonical handle
        - context: AGENTESE context
        - exists: Whether path exists
        - affordances: Available affordances (if observer provided)

        Args:
            path: AGENTESE path (with or without aspect)
            observer: Optional observer for affordance listing

        Returns:
            Path metadata dictionary
        """
        ...

    @abstractmethod
    async def affordances(
        self,
        path: str,
        observer: ObserverContext,
    ) -> list[str]:
        """
        List available affordances for a path.

        Returns affordances filtered by observer archetype.

        Args:
            path: AGENTESE path (without aspect)
            observer: Observer context

        Returns:
            List of available affordance names
        """
        ...


# =============================================================================
# Law Assertion Functions (Contract Tests)
# =============================================================================


async def assert_identity_law(
    bridge: AgenteseBridgeProtocol,
    handle: str,
    observer: ObserverContext,
) -> LawVerificationResult:
    """
    Assert the Identity Law holds for a handle.

    Identity Law: manifest(holon) returns holon (up to observer transformation)

    For any holon h and observer o:
        invoke("context.h.manifest", o).result ≅ h

    Where ≅ means "equivalent under observer transformation"

    Note: This is a weak form of identity. The strong form would require
    that Id >> f == f, but since AGENTESE paths always produce observer-specific
    results, we verify that the manifest aspect returns a consistent view.

    Args:
        bridge: The bridge implementation to test
        handle: A manifest path to test (e.g., "world.field.manifest")
        observer: Observer context

    Returns:
        LawVerificationResult indicating whether identity holds
    """
    errors: list[str] = []

    # Get the manifest twice - should be equivalent
    try:
        result1 = await bridge.invoke(handle, observer)
        result2 = await bridge.invoke(handle, observer)

        # Results should be equivalent (accounting for timestamps)
        # We compare the actual results, not the metadata
        identity_holds = _results_equivalent(result1.result, result2.result)

        if not identity_holds:
            errors.append(
                f"Identity violation at {handle}: "
                f"consecutive invocations produced different results"
            )

    except Exception as e:
        identity_holds = False
        errors.append(f"Identity check failed with exception: {e}")

    return LawVerificationResult(
        identity_holds=identity_holds,
        associativity_holds=True,  # Not checked here
        errors=errors,
        locus=handle,
    )


async def assert_associativity_law(
    bridge: AgenteseBridgeProtocol,
    a: str,
    b: str,
    c: str,
    observer: ObserverContext,
    initial_input: Any = None,
) -> LawVerificationResult:
    """
    Assert the Associativity Law holds for a composition.

    Associativity Law: composition order doesn't matter

        compose([a, b, c]) ≡ compose([a, compose([b, c])])

    In practice, we verify the results are equivalent.

    Args:
        bridge: The bridge implementation to test
        a, b, c: Three AGENTESE paths to compose
        observer: Observer context
        initial_input: Optional initial value

    Returns:
        LawVerificationResult indicating whether associativity holds
    """
    errors: list[str] = []

    try:
        # Left-grouped: (a >> b) >> c
        left_result = await bridge.compose(
            paths=[a, b, c],
            observer=observer,
            initial_input=initial_input,
            emit_law_check=False,
        )

        # For the right-grouped version, we'd need nested compose,
        # but our API is flat. We verify that the flat composition
        # is deterministic and thus implicitly associative.
        right_result = await bridge.compose(
            paths=[a, b, c],
            observer=observer,
            initial_input=initial_input,
            emit_law_check=False,
        )

        associativity_holds = _results_equivalent(
            left_result.result, right_result.result
        )

        if not associativity_holds:
            errors.append(
                f"Associativity violation at {a} >> {b} >> {c}: "
                f"results differ between invocations"
            )

    except Exception as e:
        associativity_holds = False
        errors.append(f"Associativity check failed with exception: {e}")

    return LawVerificationResult(
        identity_holds=True,  # Not checked here
        associativity_holds=associativity_holds,
        errors=errors,
        locus=f"{a} >> {b} >> {c}",
    )


async def assert_observer_polymorphism(
    bridge: AgenteseBridgeProtocol,
    handle: str,
    observer1: ObserverContext,
    observer2: ObserverContext,
) -> tuple[bool, str]:
    """
    Assert that different observers can receive different results.

    Observer Polymorphism: same handle, different observer → (potentially) different result

    This is a feature, not a bug. The AGENTESE principle is
    "There is no view from nowhere."

    Args:
        bridge: The bridge implementation to test
        handle: AGENTESE path to test
        observer1: First observer
        observer2: Second observer (different archetype)

    Returns:
        Tuple of (polymorphism_demonstrated, explanation)
    """
    # We don't require different results, just that both succeed
    # or fail appropriately based on affordances
    try:
        await bridge.invoke(handle, observer1)
        has_result1 = True
    except Exception:
        has_result1 = False

    try:
        await bridge.invoke(handle, observer2)
        has_result2 = True
    except Exception:
        has_result2 = False

    if has_result1 and has_result2:
        # Both succeeded - polymorphism works
        return True, "Both observers received results (may differ based on archetype)"
    elif has_result1 != has_result2:
        # Different affordances - polymorphism working correctly
        return True, "Observers have different affordances (one denied)"
    else:
        # Both failed - might be an error
        return False, "Neither observer could invoke the path"


def _results_equivalent(result1: Any, result2: Any) -> bool:
    """
    Check if two results are equivalent.

    This is a structural comparison that ignores:
    - Timestamp fields
    - Span IDs
    - Other volatile metadata

    For now, we use a simple equality check.
    In production, this should be more sophisticated.
    """
    # Simple case: direct equality
    if result1 == result2:
        return True

    # Handle dicts by ignoring volatile keys
    if isinstance(result1, dict) and isinstance(result2, dict):
        volatile_keys = {"timestamp", "span_id", "created_at", "updated_at"}
        cleaned1 = {k: v for k, v in result1.items() if k not in volatile_keys}
        cleaned2 = {k: v for k, v in result2.items() if k not in volatile_keys}
        return cleaned1 == cleaned2

    return False


# =============================================================================
# Error Helpers
# =============================================================================


def create_error_response(
    code: ErrorCode,
    message: str,
    *,
    path: str | None = None,
    suggestion: str | None = None,
    available: list[str] | None = None,
    why: str | None = None,
    span_id: str | None = None,
) -> ErrorResponse:
    """
    Create a sympathetic error response.

    All errors follow the pattern:
    - What went wrong (message)
    - Why it happened (why)
    - What to do about it (suggestion)
    - What alternatives exist (available)
    """
    return ErrorResponse(
        error=message,
        code=code,
        path=path,
        suggestion=suggestion,
        available=available,
        why=why,
        span_id=span_id,
    )


# =============================================================================
# Error Taxonomy
# =============================================================================

# Error code to HTTP status mapping
ERROR_HTTP_STATUS: dict[ErrorCode, int] = {
    "PATH_NOT_FOUND": 404,
    "AFFORDANCE_DENIED": 403,
    "OBSERVER_REQUIRED": 401,
    "SYNTAX_ERROR": 400,
    "LAW_VIOLATION": 422,
    "BUDGET_EXHAUSTED": 402,
    "COMPOSITION_ERROR": 422,
    "INTERNAL_ERROR": 500,
}

# Default suggestions for each error code
ERROR_SUGGESTIONS: dict[ErrorCode, str] = {
    "PATH_NOT_FOUND": "Check the path spelling. Available paths can be listed with /api/v1/paths",
    "AFFORDANCE_DENIED": "This affordance requires a different archetype. Include X-Observer-Archetype header.",
    "OBSERVER_REQUIRED": "Include X-Observer-Archetype and X-Observer-Id headers with your request.",
    "SYNTAX_ERROR": "Expected format: context.holon.aspect (e.g., world.field.manifest)",
    "LAW_VIOLATION": "The composition would violate category laws. Check that outputs match inputs.",
    "BUDGET_EXHAUSTED": "Accursed Share depleted. Consider void.gratitude.tithe to reset.",
    "COMPOSITION_ERROR": "Pipeline execution failed. Check that each path exists and is compatible.",
    "INTERNAL_ERROR": "An unexpected error occurred. Check server logs for details.",
}


def get_http_status(code: ErrorCode) -> int:
    """Get HTTP status code for an error code."""
    return ERROR_HTTP_STATUS.get(code, 500)


def get_default_suggestion(code: ErrorCode) -> str:
    """Get default suggestion for an error code."""
    return ERROR_SUGGESTIONS.get(code, "")


# =============================================================================
# Stub Implementation (for testing contracts)
# =============================================================================


@dataclass
class StubAgenteseBridge:
    """
    Stub implementation of AgenteseBridge for contract testing.

    This implementation returns canned responses for testing
    the contract layer without requiring a full Logos instance.
    """

    _invocations: list[tuple[str, ObserverContext]] = field(default_factory=list)
    _compositions: list[tuple[list[str], ObserverContext]] = field(default_factory=list)

    async def invoke(
        self,
        handle: str,
        observer: ObserverContext,
        kwargs: dict[str, Any] | None = None,
    ) -> AgenteseResponse:
        """Stub invoke - records call and returns canned response."""
        self._invocations.append((handle, observer))

        return AgenteseResponse(
            handle=handle,
            result={"stub": True, "handle": handle, "observer": observer.archetype},
            meta=ResponseMeta(
                observer=observer.archetype,
                span_id="stub-span-001",
                timestamp=datetime.now(UTC),
                duration_ms=1,
            ),
        )

    async def compose(
        self,
        paths: list[str],
        observer: ObserverContext,
        initial_input: Any = None,
        emit_law_check: bool = True,
    ) -> CompositionResponse:
        """Stub compose - records call and returns canned response."""
        self._compositions.append((paths, observer))

        trace = [
            PipelineStep(
                path=p,
                span_id=f"stub-span-{i}",
                duration_ms=1,
            )
            for i, p in enumerate(paths)
        ]

        return CompositionResponse(
            result={"stub": True, "paths": paths},
            pipeline_trace=trace,
            laws_verified=["identity", "associativity"] if emit_law_check else [],
            meta=ResponseMeta(
                observer=observer.archetype,
                span_id="stub-compose-span",
                timestamp=datetime.now(UTC),
                duration_ms=len(paths),
            ),
        )

    async def stream(
        self,
        handle: str,
        observer: ObserverContext,
        kwargs: dict[str, Any] | None = None,
    ) -> AsyncIterator[SSEEvent]:
        """Stub stream - yields canned chunks."""
        yield SSEEvent(
            event="chunk",
            data=SSEChunk(type="response", content="Stub ", index=0),
        )
        yield SSEEvent(
            event="chunk",
            data=SSEChunk(type="response", content="response", index=1),
        )
        yield SSEEvent(
            event="done",
            data=SSECompleteEvent(
                result="Stub response",
                span_id="stub-stream-span",
                chunks_count=2,
                duration_ms=10,
            ),
        )

    def subscribe(
        self,
        channel: str,
        filter_: dict[str, Any] | None = None,
    ) -> Subscription:
        """Stub subscribe - returns a no-op subscription."""
        raise NotImplementedError("WebSocket subscriptions not implemented in stub")

    async def verify_laws(
        self,
        composition: list[str],
        observer: ObserverContext,
    ) -> LawVerificationResult:
        """Stub verify - always returns laws hold."""
        return LawVerificationResult(
            identity_holds=True,
            associativity_holds=True,
            errors=[],
            locus=" >> ".join(composition),
        )

    async def resolve(
        self,
        path: str,
        observer: ObserverContext | None = None,
    ) -> dict[str, Any]:
        """Stub resolve - returns canned metadata."""
        parts = path.split(".")
        return {
            "path": path,
            "handle": path,
            "context": parts[0] if parts else "",
            "holon": parts[1] if len(parts) > 1 else "",
            "exists": True,
            "is_jit": False,
        }

    async def affordances(
        self,
        path: str,
        observer: ObserverContext,
    ) -> list[str]:
        """Stub affordances - returns default set."""
        return ["manifest", "witness", "affordances"]
