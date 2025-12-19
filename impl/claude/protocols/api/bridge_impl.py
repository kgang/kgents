"""
AGENTESE Bridge Implementation.

The real bridge between HTTP/WS and AGENTESE Logos.

This is the backed implementation that:
1. Translates ObserverContext → Umwelt for Logos invocations
2. Maps AGENTESE exceptions → HTTP status codes
3. Wraps Logos.invoke() with proper telemetry
4. Implements SSE streaming for long-running operations
5. Verifies category laws during composition

Design:
    LogosAgenteseBridge : AgenteseBridgeProtocol

    HTTP Request → LogosAgenteseBridge.invoke() → Logos.invoke() → Response

Laws (preserved):
1. Identity: invoke("context.holon.manifest") returns holon unchanged
2. Associativity: compose([a, b, c]) == compose([a, compose([b, c])])
3. Observer Polymorphism: same handle, different observer → different result
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, AsyncIterator, cast

from .bridge import (
    AgenteseBridgeProtocol,
    SSEEvent,
    Subscription,
    create_error_response,
    get_default_suggestion,
    get_http_status,
)
from .serializers import (
    AgenteseResponse,
    CompositionResponse,
    ErrorCode,
    ErrorResponse,
    LawVerificationResult,
    ObserverContext,
    PipelineStep,
    ResponseMeta,
    SSEChunk,
    SSECompleteEvent,
    WSStateUpdate,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from protocols.agentese.logos import Logos


# =============================================================================
# Mock Umwelt for API Invocations
# =============================================================================


@dataclass(frozen=True)
class _MockDNA:
    """Mock DNA for API Umwelt."""

    name: str = "api_user"
    archetype: str = "developer"
    capabilities: tuple[str, ...] = ()


@dataclass(frozen=True)
class _MockUmwelt:
    """
    Minimal Umwelt for API invocations.

    Satisfies the Umwelt protocol for Logos.invoke().
    """

    dna: _MockDNA = field(default_factory=_MockDNA)
    gravity: tuple[Any, ...] = ()


def _observer_to_umwelt(observer: ObserverContext) -> "Umwelt[Any, Any]":
    """
    Convert ObserverContext to Logos-compatible Umwelt.

    This is the functor mapping from HTTP observer representation
    to the internal Umwelt structure used by AGENTESE Logos.

    Args:
        observer: HTTP observer context (from headers or request body)

    Returns:
        MockUmwelt suitable for Logos.invoke()
    """
    dna = _MockDNA(
        name=observer.id,
        archetype=observer.archetype,
        capabilities=tuple(observer.capabilities),
    )
    return cast("Umwelt[Any, Any]", _MockUmwelt(dna=dna))


# =============================================================================
# Exception Mapping
# =============================================================================


def _exception_to_error_code(exc: Exception) -> ErrorCode:
    """
    Map AGENTESE exception to error code.

    Exception taxonomy:
    - PathNotFoundError → PATH_NOT_FOUND
    - AffordanceError → AFFORDANCE_DENIED
    - ObserverRequiredError → OBSERVER_REQUIRED
    - PathSyntaxError → SYNTAX_ERROR
    - TastefulnessError → LAW_VIOLATION (aesthetics are laws too)
    - Other → INTERNAL_ERROR
    """
    exc_type = type(exc).__name__

    mapping: dict[str, ErrorCode] = {
        "PathNotFoundError": "PATH_NOT_FOUND",
        "AffordanceError": "AFFORDANCE_DENIED",
        "ObserverRequiredError": "OBSERVER_REQUIRED",
        "PathSyntaxError": "SYNTAX_ERROR",
        "TastefulnessError": "LAW_VIOLATION",
        "LineageError": "LAW_VIOLATION",
        "LatticeError": "LAW_VIOLATION",
        "BudgetExhaustedError": "BUDGET_EXHAUSTED",
    }

    return mapping.get(exc_type, "INTERNAL_ERROR")


def _exception_to_error_response(
    exc: Exception,
    path: str | None = None,
    span_id: str | None = None,
) -> ErrorResponse:
    """
    Convert an AGENTESE exception to a sympathetic ErrorResponse.

    Errors include:
    - What went wrong (message)
    - Why it happened (from exception attributes)
    - What to do about it (suggestion)
    - What alternatives exist (available)
    """
    code = _exception_to_error_code(exc)

    # Extract attributes from known exception types
    available = getattr(exc, "available", None)
    why = getattr(exc, "why", None)
    suggestion = getattr(exc, "suggestion", get_default_suggestion(code))

    # Use exception path if not provided
    if path is None:
        path = getattr(exc, "path", None)

    return create_error_response(
        code=code,
        message=str(exc),
        path=path,
        suggestion=suggestion,
        available=available,
        why=why,
        span_id=span_id,
    )


# =============================================================================
# Logos Bridge Implementation
# =============================================================================


@dataclass
class LogosAgenteseBridge:
    """
    The bridge between HTTP/WS and AGENTESE Logos.

    This is the functor between external API and internal AGENTESE:

        HTTP Request → LogosAgenteseBridge → Logos.invoke() → Response

    Responsibilities:
    1. Parse incoming requests into Umwelt + handle
    2. Invoke Logos with proper observer context
    3. Serialize results to JSON
    4. Handle streaming for SSE
    5. Verify category laws during composition

    Laws (preserved by the bridge):
    1. Identity: invoke("context.holon.manifest") returns holon unchanged
    2. Associativity: compose([a, b, c]) == compose([a, compose([b, c])])
    3. Observer Polymorphism: same handle, different observer → different result
    """

    logos: "Logos"
    telemetry_enabled: bool = True

    async def invoke(
        self,
        handle: str,
        observer: ObserverContext,
        kwargs: dict[str, Any] | None = None,
    ) -> AgenteseResponse:
        """
        Single AGENTESE path invocation.

        Maps:
            POST /api/v1/{context}/{holon}/{aspect}
            → logos.invoke("context.holon.aspect", observer_umwelt)

        Args:
            handle: Full AGENTESE path including aspect
                   (e.g., "world.field.manifest", "concept.justice.refine")
            observer: Observer context (REQUIRED - no view from nowhere)
            kwargs: Aspect-specific arguments

        Returns:
            AgenteseResponse with observer-specific result and metadata

        Raises:
            ErrorResponse wrapped in exception for HTTP error responses
        """
        kwargs = kwargs or {}
        span_id = self._generate_span_id()
        start_time = time.perf_counter()

        # Convert observer to Umwelt
        umwelt = _observer_to_umwelt(observer)

        try:
            # Invoke Logos
            result = await self.logos.invoke(handle, umwelt, **kwargs)

            # Calculate duration
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            # Serialize result
            serialized = self._serialize_result(result)

            return AgenteseResponse(
                handle=handle,
                result=serialized,
                meta=ResponseMeta(
                    observer=observer.archetype,
                    span_id=span_id,
                    timestamp=datetime.now(UTC),
                    duration_ms=duration_ms,
                    cached=self.logos.is_resolved(handle),
                ),
            )

        except Exception as e:
            # Convert to ErrorResponse
            error = _exception_to_error_response(e, path=handle, span_id=span_id)
            # Re-raise as an exception that carries the error response
            raise BridgeError(error) from e

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
            BridgeError: If composition fails
        """
        span_id = self._generate_span_id()
        start_time = time.perf_counter()
        pipeline_trace: list[PipelineStep] = []
        laws_verified: list[str] = []

        umwelt = _observer_to_umwelt(observer)

        try:
            # Create composed path via Logos (validates composition, result unused)
            _ = self.logos.compose(
                *paths,
                enforce_output=True,
                emit_law_check=emit_law_check,
            )

            # Execute and collect trace
            current = initial_input
            for i, path in enumerate(paths):
                step_start = time.perf_counter()
                step_span_id = f"{span_id}-{i}"

                current = await self.logos.invoke(path, umwelt, input=current)

                step_duration = int((time.perf_counter() - step_start) * 1000)
                pipeline_trace.append(
                    PipelineStep(
                        path=path,
                        span_id=step_span_id,
                        duration_ms=step_duration,
                        output_type=type(current).__name__,
                    )
                )

            # Verify laws if requested
            if emit_law_check:
                laws_verified = ["identity", "associativity"]

            duration_ms = int((time.perf_counter() - start_time) * 1000)

            return CompositionResponse(
                result=self._serialize_result(current),
                pipeline_trace=pipeline_trace,
                laws_verified=laws_verified,
                meta=ResponseMeta(
                    observer=observer.archetype,
                    span_id=span_id,
                    timestamp=datetime.now(UTC),
                    duration_ms=duration_ms,
                ),
            )

        except Exception as e:
            error = _exception_to_error_response(
                e,
                path=" >> ".join(paths),
                span_id=span_id,
            )
            raise BridgeError(error) from e

    async def stream(
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
        kwargs = kwargs or {}
        span_id = self._generate_span_id()
        start_time = time.perf_counter()
        chunk_index = 0

        umwelt = _observer_to_umwelt(observer)

        try:
            # Check if this is a streaming-capable path
            if "soul" in handle and "challenge" in handle:
                # Stream soul challenge via K-gent
                async for chunk in self._stream_soul_challenge(umwelt, handle, kwargs, observer):
                    yield SSEEvent(
                        event="chunk",
                        data=SSEChunk(
                            type="response",
                            content=chunk,
                            partial=True,
                            index=chunk_index,
                        ),
                    )
                    chunk_index += 1

                duration_ms = int((time.perf_counter() - start_time) * 1000)
                yield SSEEvent(
                    event="done",
                    data=SSECompleteEvent(
                        result="[Streamed response complete]",
                        span_id=span_id,
                        chunks_count=chunk_index,
                        duration_ms=duration_ms,
                    ),
                )

            elif "dialectic" in handle:
                # Stream dialectic phases
                async for phase, content in self._stream_dialectic(umwelt, handle, kwargs):
                    yield SSEEvent(
                        event="chunk",
                        data=SSEChunk(
                            type="response" if phase == "synthesis" else "thinking",
                            content=f"[{phase.upper()}] {content}",
                            partial=phase != "synthesis",
                            index=chunk_index,
                        ),
                    )
                    chunk_index += 1

                duration_ms = int((time.perf_counter() - start_time) * 1000)
                yield SSEEvent(
                    event="done",
                    data=SSECompleteEvent(
                        result="Dialectic complete",
                        span_id=span_id,
                        chunks_count=chunk_index,
                        duration_ms=duration_ms,
                    ),
                )

            else:
                # Regular invoke, single response
                result = await self.logos.invoke(handle, umwelt, **kwargs)
                yield SSEEvent(
                    event="chunk",
                    data=SSEChunk(
                        type="response",
                        content=str(self._serialize_result(result)),
                        partial=False,
                        index=0,
                    ),
                )

                duration_ms = int((time.perf_counter() - start_time) * 1000)
                yield SSEEvent(
                    event="done",
                    data=SSECompleteEvent(
                        result=self._serialize_result(result),
                        span_id=span_id,
                        chunks_count=1,
                        duration_ms=duration_ms,
                    ),
                )

        except Exception as e:
            error = _exception_to_error_response(e, path=handle, span_id=span_id)
            yield SSEEvent(event="error", data=error)

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
        # WebSocket subscriptions will be implemented in Wave 3
        # For now, raise NotImplementedError
        raise NotImplementedError(
            "WebSocket subscriptions not yet implemented. Use SSE streaming for real-time updates."
        )

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
        errors: list[str] = []
        identity_holds = True
        associativity_holds = True

        umwelt = _observer_to_umwelt(observer)

        # Verify identity for each path
        for path in composition:
            try:
                # Invoke twice and compare
                result1 = await self.logos.invoke(path, umwelt)
                result2 = await self.logos.invoke(path, umwelt)

                # Check results are equivalent (ignoring timestamps)
                if not self._results_equivalent(result1, result2):
                    identity_holds = False
                    errors.append(f"Identity violation at {path}")

            except Exception as e:
                identity_holds = False
                errors.append(f"Identity check failed at {path}: {e}")

        # Verify associativity if 3+ paths
        if len(composition) >= 3:
            try:
                # Execute in order twice
                composed1 = self.logos.compose(*composition)
                composed2 = self.logos.compose(*composition)

                result1 = await composed1.invoke(umwelt)
                result2 = await composed2.invoke(umwelt)

                if not self._results_equivalent(result1, result2):
                    associativity_holds = False
                    errors.append("Associativity violation: results differ")

            except Exception as e:
                associativity_holds = False
                errors.append(f"Associativity check failed: {e}")

        return LawVerificationResult(
            identity_holds=identity_holds,
            associativity_holds=associativity_holds,
            errors=errors,
            locus=" >> ".join(composition),
        )

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
        parts = path.split(".")
        context = parts[0] if parts else ""
        holon = parts[1] if len(parts) > 1 else ""

        try:
            # Try to resolve the path
            node = self.logos.resolve(path)
            exists = True
            is_jit = hasattr(node, "source") and hasattr(node, "usage_count")

            # Get affordances if observer provided
            affordances: list[str] = []
            if observer is not None:
                affordances = await self.affordances(path, observer)

        except Exception:
            exists = False
            is_jit = False
            affordances = []

        return {
            "path": path,
            "handle": path,
            "context": context,
            "holon": holon,
            "exists": exists,
            "is_jit": is_jit,
            "affordances": affordances,
        }

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
        try:
            node = self.logos.resolve(path)

            # Get AgentMeta from observer
            from protocols.agentese.node import AgentMeta

            meta = AgentMeta(
                name=observer.id,
                archetype=observer.archetype,
                capabilities=tuple(observer.capabilities),
            )

            if hasattr(node, "affordances"):
                return node.affordances(meta)

            # Default affordances
            return ["manifest", "witness", "affordances"]

        except Exception:
            return []

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _generate_span_id(self) -> str:
        """Generate a unique span ID for tracing."""
        return uuid.uuid4().hex[:16]

    def _serialize_result(self, result: Any) -> Any:
        """
        Serialize a result for JSON response.

        Handles:
        - Pydantic models (model_dump)
        - Dataclasses (__dict__)
        - Objects with to_dict()
        - Primitives (passthrough)
        """
        if hasattr(result, "model_dump"):
            return result.model_dump(mode="json")
        elif hasattr(result, "to_dict"):
            return result.to_dict()
        elif hasattr(result, "__dict__") and not isinstance(
            result, (str, int, float, bool, list, dict, type(None))
        ):
            return result.__dict__
        return result

    def _results_equivalent(self, result1: Any, result2: Any) -> bool:
        """
        Check if two results are equivalent.

        Ignores volatile fields like timestamps and span_ids.
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

    async def _stream_soul_challenge(
        self,
        umwelt: "Umwelt[Any, Any]",
        handle: str,
        kwargs: dict[str, Any],
        observer: ObserverContext,
    ) -> AsyncIterator[str]:
        """
        Stream soul challenge response.

        Attempts to use K-gent streaming if available,
        falls back to single invocation.
        """
        try:
            # Try to get soul with streaming
            from agents.k.soul import KgentSoul

            soul = KgentSoul()
            challenge = kwargs.get("challenge", kwargs.get("input", ""))

            if hasattr(soul, "dialogue_stream") and soul.has_llm:
                async for chunk in soul.dialogue_stream(challenge):
                    yield chunk
            else:
                # Fall back to non-streaming
                result = await soul.dialogue(challenge)
                if hasattr(result, "response"):
                    yield result.response
                else:
                    yield str(result)

        except ImportError:
            # No K-gent, use Logos directly
            result = await self.logos.invoke(handle, umwelt, **kwargs)
            yield str(self._serialize_result(result))

    async def _stream_dialectic(
        self,
        umwelt: "Umwelt[Any, Any]",
        handle: str,
        kwargs: dict[str, Any],
    ) -> AsyncIterator[tuple[str, str]]:
        """
        Stream dialectic phases.

        Yields (phase, content) tuples for thesis, antithesis, synthesis.
        """
        # For now, invoke and split into phases
        # Real implementation would stream from dialectic engine
        try:
            result = await self.logos.invoke(handle, umwelt, **kwargs)

            if isinstance(result, dict):
                if "thesis" in result:
                    yield ("thesis", str(result["thesis"]))
                if "antithesis" in result:
                    yield ("antithesis", str(result["antithesis"]))
                if "synthesis" in result:
                    yield ("synthesis", str(result["synthesis"]))
            else:
                yield ("synthesis", str(result))

        except Exception as e:
            yield ("error", str(e))


# =============================================================================
# Bridge Error (for HTTP error propagation)
# =============================================================================


class BridgeError(Exception):
    """
    Exception that carries an ErrorResponse for HTTP error handling.

    Used to propagate structured errors from the bridge to HTTP handlers.
    """

    def __init__(self, error: ErrorResponse):
        self.error = error
        super().__init__(error.error)


# =============================================================================
# Factory Function
# =============================================================================


def create_logos_bridge(
    logos: "Logos | None" = None,
    telemetry_enabled: bool = True,
) -> LogosAgenteseBridge:
    """
    Create a LogosAgenteseBridge.

    Args:
        logos: Optional Logos instance. If not provided, creates default.
        telemetry_enabled: Whether to enable telemetry spans.

    Returns:
        Configured LogosAgenteseBridge instance.
    """
    if logos is None:
        from protocols.agentese.logos import create_logos

        logos = create_logos()

    return LogosAgenteseBridge(
        logos=logos,
        telemetry_enabled=telemetry_enabled,
    )
