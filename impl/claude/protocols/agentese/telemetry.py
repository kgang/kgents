"""
AGENTESE Telemetry: OpenTelemetry Integration for Observability.

Provides automatic span creation for all AGENTESE invocations,
enabling distributed tracing through Jaeger, Tempo, or any OTLP-compatible backend.

Design Principles:
1. Observation doesn't mutate - outputs unchanged
2. Observation doesn't block - async, non-blocking
3. Observation doesn't leak - data stays within boundaries
4. Observation enables - self-knowledge enables improvement

Usage:
    from protocols.agentese.telemetry import TelemetryMiddleware, configure_telemetry

    # Configure once at startup
    configure_telemetry(TelemetryConfig(otlp_endpoint="localhost:4317"))

    # Middleware automatically wraps Logos invocations
    logos = create_logos_with_telemetry()
    result = await logos.invoke("self.soul.challenge", umwelt, "idea")
    # → Span created: agentese.invoke with path, context, tokens attributes
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, AsyncIterator, Awaitable, Callable

from opentelemetry import trace
from opentelemetry.trace import Span, Status, StatusCode, Tracer

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Tracer Singleton ===

_tracer: Tracer | None = None


def get_tracer() -> Tracer:
    """Get the AGENTESE tracer, creating if needed."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("kgents.agentese", "0.1.0")
    return _tracer


# === Span Attributes ===

ATTR_PATH = "agentese.path"
ATTR_CONTEXT = "agentese.context"
ATTR_HOLON = "agentese.holon"
ATTR_ASPECT = "agentese.aspect"
ATTR_OBSERVER_ID = "agentese.observer.id"
ATTR_OBSERVER_ARCHETYPE = "agentese.observer.archetype"
ATTR_TOKENS_IN = "agentese.tokens.in"
ATTR_TOKENS_OUT = "agentese.tokens.out"
ATTR_RESULT_TYPE = "agentese.result.type"
ATTR_DURATION_MS = "agentese.duration_ms"


# === Telemetry Middleware ===


@dataclass
class TelemetryMiddleware:
    """
    Middleware that adds OpenTelemetry spans to AGENTESE invocations.

    Wraps invoke() calls with distributed tracing spans, capturing:
    - Path components (context, holon, aspect)
    - Observer information
    - Token usage (if LLM-backed)
    - Timing and result type

    Example:
        middleware = TelemetryMiddleware()
        result = await middleware(
            path="self.soul.challenge",
            umwelt=observer,
            args=("idea",),
            kwargs={},
            next_handler=logos.invoke,
        )
    """

    # Whether to record token counts (requires LLM result inspection)
    record_tokens: bool = True

    # Whether to record result type
    record_result_type: bool = True

    # Span name prefix
    span_prefix: str = "agentese"

    async def __call__(
        self,
        path: str,
        umwelt: Any,  # Duck-typed: requires .id and optionally .dna
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        next_handler: Callable[..., Awaitable[Any]],
    ) -> Any:
        """
        Wrap an AGENTESE invocation with tracing.

        Args:
            path: Full AGENTESE path (e.g., "self.soul.challenge")
            umwelt: Observer's Umwelt
            args: Positional arguments for the invocation
            kwargs: Keyword arguments for the invocation
            next_handler: The actual invoke function to call

        Returns:
            Result from next_handler, unchanged
        """
        tracer = get_tracer()

        # Parse path components
        parts = path.split(".")
        context = parts[0] if len(parts) > 0 else "unknown"
        holon = parts[1] if len(parts) > 1 else "unknown"
        aspect = parts[2] if len(parts) > 2 else "unknown"

        # Extract observer info
        observer_id = getattr(umwelt, "id", "unknown")
        dna = getattr(umwelt, "dna", None)
        observer_archetype = getattr(dna, "archetype", "unknown") if dna else "unknown"

        # Create span
        with tracer.start_as_current_span(
            f"{self.span_prefix}.invoke",
            attributes={
                ATTR_PATH: path,
                ATTR_CONTEXT: context,
                ATTR_HOLON: holon,
                ATTR_ASPECT: aspect,
                ATTR_OBSERVER_ID: str(observer_id),
                ATTR_OBSERVER_ARCHETYPE: observer_archetype,
            },
        ) as span:
            start_time = time.perf_counter()

            try:
                # Call the actual handler
                result = await next_handler(path, umwelt, *args, **kwargs)

                # Record success
                span.set_status(Status(StatusCode.OK))

                # Record result type
                if self.record_result_type:
                    span.set_attribute(ATTR_RESULT_TYPE, type(result).__name__)

                # Record token usage if available
                if self.record_tokens:
                    self._record_tokens(span, result)

                return result

            except Exception as e:
                # Record error
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

            finally:
                # Record duration
                duration_ms = (time.perf_counter() - start_time) * 1000
                span.set_attribute(ATTR_DURATION_MS, duration_ms)

    def _record_tokens(self, span: Span, result: Any) -> None:
        """Record token counts if result contains usage info."""
        # Check for anthropic-style usage
        if hasattr(result, "usage"):
            usage = result.usage
            if hasattr(usage, "input_tokens"):
                span.set_attribute(ATTR_TOKENS_IN, usage.input_tokens)
            if hasattr(usage, "output_tokens"):
                span.set_attribute(ATTR_TOKENS_OUT, usage.output_tokens)

        # Check for dict-style usage
        elif isinstance(result, dict):
            if "tokens_in" in result:
                span.set_attribute(ATTR_TOKENS_IN, result["tokens_in"])
            if "tokens_out" in result:
                span.set_attribute(ATTR_TOKENS_OUT, result["tokens_out"])
            if "usage" in result and isinstance(result["usage"], dict):
                usage = result["usage"]
                if "input_tokens" in usage:
                    span.set_attribute(ATTR_TOKENS_IN, usage["input_tokens"])
                if "output_tokens" in usage:
                    span.set_attribute(ATTR_TOKENS_OUT, usage["output_tokens"])


# === Context Manager for Manual Spans ===


@asynccontextmanager
async def trace_invocation(
    path: str,
    umwelt: Any,  # Duck-typed: requires .id and optionally .dna
    **extra_attributes: Any,
) -> AsyncIterator[Span]:
    """
    Context manager for manually tracing an AGENTESE operation.

    Use this when you need fine-grained control over span creation,
    or when tracing operations that don't go through invoke().

    Example:
        async with trace_invocation("self.memory.consolidate", umwelt) as span:
            span.set_attribute("memory.count", 42)
            result = await do_consolidation()
            span.set_attribute("consolidated", len(result))

    Args:
        path: AGENTESE path being traced
        umwelt: Observer's Umwelt
        **extra_attributes: Additional span attributes

    Yields:
        The active span for attribute setting
    """
    tracer = get_tracer()

    # Parse path
    parts = path.split(".")
    context = parts[0] if len(parts) > 0 else "unknown"
    holon = parts[1] if len(parts) > 1 else "unknown"
    aspect = parts[2] if len(parts) > 2 else "unknown"

    # Extract observer info
    observer_id = getattr(umwelt, "id", "unknown")
    dna = getattr(umwelt, "dna", None)
    observer_archetype = getattr(dna, "archetype", "unknown") if dna else "unknown"

    attributes = {
        ATTR_PATH: path,
        ATTR_CONTEXT: context,
        ATTR_HOLON: holon,
        ATTR_ASPECT: aspect,
        ATTR_OBSERVER_ID: str(observer_id),
        ATTR_OBSERVER_ARCHETYPE: observer_archetype,
        **extra_attributes,
    }

    with tracer.start_as_current_span("agentese.invoke", attributes=attributes) as span:
        start_time = time.perf_counter()
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            span.set_attribute(ATTR_DURATION_MS, duration_ms)


# === Utility Functions ===


def create_child_span(name: str, **attributes: Any) -> Span:
    """
    Create a child span under the current trace context.

    Use this for tracing sub-operations within an AGENTESE invocation.

    Args:
        name: Span name (will be prefixed with "agentese.")
        **attributes: Span attributes

    Returns:
        Started span (use as context manager)
    """
    tracer = get_tracer()
    return tracer.start_as_current_span(f"agentese.{name}", attributes=attributes)  # type: ignore[return-value]


def add_event(name: str, attributes: dict[str, Any] | None = None) -> None:
    """
    Add an event to the current span.

    Events are timestamped annotations within a span, useful for
    marking significant points in processing.

    Args:
        name: Event name
        attributes: Optional event attributes
    """
    span = trace.get_current_span()
    if span and span.is_recording():
        span.add_event(name, attributes=attributes or {})


def set_attribute(key: str, value: Any) -> None:
    """
    Set an attribute on the current span.

    Args:
        key: Attribute key
        value: Attribute value
    """
    span = trace.get_current_span()
    if span and span.is_recording():
        span.set_attribute(key, value)
