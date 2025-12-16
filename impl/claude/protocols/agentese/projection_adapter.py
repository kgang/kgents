"""
AGENTESE Projection Adapter.

Bridges AGENTESE invocations with the Projection Component Library.
Wraps Logos results in WidgetEnvelope with appropriate metadata.

Example:
    from protocols.agentese.logos import create_logos
    from protocols.agentese.projection_adapter import ProjectionAdapter

    logos = create_logos()
    adapter = ProjectionAdapter(logos)

    # Invoke with projection envelope
    envelope = await adapter.invoke_with_projection(
        "world.town.manifest",
        observer,
    )
    # envelope.data = result
    # envelope.meta = WidgetMeta with status, cache hints, etc.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from protocols.projection.schema import (
    CacheMeta,
    ErrorInfo,
    RefusalInfo,
    StreamMeta,
    UIHint,
    WidgetEnvelope,
    WidgetMeta,
    WidgetStatus,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

    from .logos import Logos
    from .node import Observer


# === Projection Hints Extraction ===


def extract_ui_hint(path: str, result: Any) -> UIHint | None:
    """
    Extract UI hint from path and result type.

    Maps AGENTESE paths and result types to widget hints:
    - manifest → table, graph, text, card based on result type
    - stream → stream
    - witness → text (timeline format)

    Args:
        path: AGENTESE path that was invoked.
        result: The result from invocation.

    Returns:
        UI hint or None if no specific hint.
    """
    parts = path.split(".")
    aspect = parts[-1] if parts else ""

    # Streaming aspects
    if aspect in ("stream", "flux", "flow"):
        return "stream"

    # Perception aspects - infer from result type
    if aspect == "manifest":
        if isinstance(result, dict):
            if "rows" in result or "columns" in result:
                return "table"
            if "datasets" in result or "labels" in result:
                return "graph"
            return "card"
        if isinstance(result, (list, tuple)):
            return "table"
        return "text"

    # Narrative aspects
    if aspect in ("witness", "trace", "history"):
        return "text"

    # Form-like aspects
    if aspect in ("configure", "settings", "preferences"):
        return "form"

    return None


def is_deterministic_path(path: str) -> bool:
    """
    Check if a path is deterministic (cacheable).

    Deterministic paths always return the same result for the same input.

    Args:
        path: AGENTESE path.

    Returns:
        True if path is deterministic.
    """
    parts = path.split(".")
    context = parts[0] if parts else ""
    aspect = parts[-1] if parts else ""

    # void.* paths are never deterministic (entropy source)
    if context == "void":
        return False

    # GENERATION aspects are not deterministic
    non_deterministic_aspects = frozenset(
        {
            "define",
            "spawn",
            "fork",
            "dream",
            "refine",
            "dialectic",
            "sip",
            "solve",
            "blend",
        }
    )
    if aspect in non_deterministic_aspects:
        return False

    # Most perception aspects are deterministic
    return True


def extract_observer_archetype(
    observer: "Observer | Umwelt[Any, Any] | None",
) -> str | None:
    """
    Extract archetype from observer.

    Args:
        observer: Observer or Umwelt.

    Returns:
        Archetype string or None.
    """
    if observer is None:
        return None

    # v3 Observer
    from .node import Observer as ObserverClass

    if isinstance(observer, ObserverClass):
        return observer.archetype

    # v1 Umwelt
    dna = getattr(observer, "dna", None)
    if dna:
        return getattr(dna, "archetype", None)

    return None


# === Projection Adapter ===


@dataclass
class ProjectionAdapter:
    """
    Adapter for invoking AGENTESE paths with projection envelopes.

    Wraps Logos invocations to add widget metadata for rendering.

    Attributes:
        logos: The Logos instance to wrap.
        default_cache_ttl: Default TTL for cache metadata (seconds).
    """

    logos: "Logos"
    default_cache_ttl: int = 300  # 5 minutes

    async def invoke_with_projection(
        self,
        path: str,
        observer: "Observer | Umwelt[Any, Any] | None" = None,
        *,
        cache_hint: bool | None = None,
        stream_total: int | None = None,
        **kwargs: Any,
    ) -> WidgetEnvelope[Any]:
        """
        Invoke an AGENTESE path and wrap result in projection envelope.

        This is the main entry point for projection-aware invocations.
        The envelope contains both the data and metadata for rendering.

        Args:
            path: Full AGENTESE path including aspect.
            observer: Observer or Umwelt for invocation.
            cache_hint: Override cache detection (True = cached, False = not cached).
            stream_total: Expected total for streaming (if known).
            **kwargs: Additional arguments passed to logos.invoke().

        Returns:
            WidgetEnvelope with data and projection metadata.

        Example:
            adapter = ProjectionAdapter(logos)
            envelope = await adapter.invoke_with_projection(
                "world.town.manifest",
                observer,
            )
            if envelope.meta.status == WidgetStatus.DONE:
                render_widget(envelope.data, envelope.meta.ui_hint)
        """
        try:
            # Invoke the path
            result = await self.logos.invoke(path, observer, **kwargs)

            # Build metadata
            meta = self._build_success_meta(
                path=path,
                result=result,
                observer=observer,
                cache_hint=cache_hint,
                stream_total=stream_total,
            )

            return WidgetEnvelope(
                data=result,
                meta=meta,
                source_path=path,
                observer_archetype=extract_observer_archetype(observer),
            )

        except Exception as e:
            # Build error/refusal metadata
            meta = self._build_error_meta(e, path)

            return WidgetEnvelope(
                data=None,
                meta=meta,
                source_path=path,
                observer_archetype=extract_observer_archetype(observer),
            )

    def _build_success_meta(
        self,
        path: str,
        result: Any,
        observer: "Observer | Umwelt[Any, Any] | None",
        cache_hint: bool | None,
        stream_total: int | None,
    ) -> WidgetMeta:
        """Build metadata for successful invocation."""
        # Determine cache status
        is_cached = cache_hint if cache_hint is not None else False
        cache_meta = None
        if is_cached:
            cache_meta = CacheMeta(
                is_cached=True,
                cached_at=datetime.now(timezone.utc),
                ttl_seconds=self.default_cache_ttl,
                deterministic=is_deterministic_path(path),
            )

        # Determine UI hint
        ui_hint = extract_ui_hint(path, result)

        # Check if streaming
        stream_meta = None
        parts = path.split(".")
        aspect = parts[-1] if parts else ""
        if aspect in ("stream", "flux", "flow"):
            stream_meta = StreamMeta(
                total_expected=stream_total,
                received=0,
                started_at=datetime.now(timezone.utc),
                last_chunk_at=None,
            )

        return WidgetMeta(
            status=WidgetStatus.DONE,
            cache=cache_meta,
            error=None,
            refusal=None,
            stream=stream_meta,
            ui_hint=ui_hint,
        )

    def _build_error_meta(self, exc: Exception, path: str) -> WidgetMeta:
        """Build metadata for failed invocation."""
        from .exceptions import (
            AffordanceError,
            ObserverRequiredError,
            PathNotFoundError,
            PathSyntaxError,
            TastefulnessError,
        )

        # Check for refusal (TastefulnessError or AffordanceError)
        if isinstance(exc, TastefulnessError):
            refusal = RefusalInfo(
                reason=str(exc),
                consent_required=None,
                appeal_to="self.soul.appeal",
                override_cost=None,
            )
            return WidgetMeta.with_refusal(refusal)

        if isinstance(exc, AffordanceError):
            refusal = RefusalInfo(
                reason=str(exc),
                consent_required="elevated_access",
                appeal_to="self.soul.elevate",
                override_cost=10,
            )
            return WidgetMeta.with_refusal(refusal)

        # Map exception to error category
        category: str
        code: str

        if isinstance(exc, PathNotFoundError):
            category = "notFound"
            code = "PATH_NOT_FOUND"
        elif isinstance(exc, PathSyntaxError):
            category = "validation"
            code = "PATH_SYNTAX_ERROR"
        elif isinstance(exc, ObserverRequiredError):
            category = "permission"
            code = "OBSERVER_REQUIRED"
        elif isinstance(exc, TimeoutError):
            category = "timeout"
            code = "INVOCATION_TIMEOUT"
        elif isinstance(exc, (ConnectionError, OSError)):
            category = "network"
            code = "CONNECTION_ERROR"
        else:
            category = "unknown"
            code = type(exc).__name__.upper()

        error = ErrorInfo(
            category=category,  # type: ignore[arg-type]
            code=code,
            message=str(exc),
            retry_after_seconds=5 if category in ("network", "timeout") else None,
            fallback_action=self._suggest_fallback(exc, path),
            trace_id=None,
        )
        return WidgetMeta.with_error(error)

    def _suggest_fallback(self, exc: Exception, path: str) -> str | None:
        """Suggest fallback action based on error."""
        from .exceptions import AffordanceError, PathNotFoundError

        if isinstance(exc, PathNotFoundError):
            return f"Try: logos.query('?{path.rsplit('.', 1)[0]}.*')"

        if isinstance(exc, AffordanceError):
            return "Try a different observer or request elevated access"

        return None


# === Streaming Support ===


async def stream_with_projection(
    logos: "Logos",
    path: str,
    observer: "Observer | Umwelt[Any, Any] | None" = None,
    **kwargs: Any,
) -> AsyncIterator[WidgetEnvelope[Any]]:
    """
    Stream an AGENTESE path with projection envelopes.

    For paths that return async iterators, this yields
    WidgetEnvelope for each chunk.

    Args:
        logos: Logos instance.
        path: Full AGENTESE path.
        observer: Observer or Umwelt.
        **kwargs: Additional arguments.

    Yields:
        WidgetEnvelope for each chunk.

    Example:
        async for envelope in stream_with_projection(logos, "world.feed.stream", observer):
            if envelope.meta.status == WidgetStatus.STREAMING:
                update_ui(envelope.data)
            elif envelope.meta.status == WidgetStatus.DONE:
                finalize_ui()
    """
    archetype = extract_observer_archetype(observer)
    started_at = datetime.now(timezone.utc)
    received = 0

    try:
        result = await logos.invoke(path, observer, **kwargs)

        # Check if result is async iterator
        if hasattr(result, "__aiter__"):
            async for chunk in result:
                received += 1
                meta = WidgetMeta(
                    status=WidgetStatus.STREAMING,
                    stream=StreamMeta(
                        total_expected=None,
                        received=received,
                        started_at=started_at,
                        last_chunk_at=datetime.now(timezone.utc),
                    ),
                    ui_hint="stream",
                )
                yield WidgetEnvelope(
                    data=chunk,
                    meta=meta,
                    source_path=path,
                    observer_archetype=archetype,
                )

            # Final envelope
            yield WidgetEnvelope(
                data=None,
                meta=WidgetMeta(
                    status=WidgetStatus.DONE,
                    stream=StreamMeta(
                        total_expected=received,
                        received=received,
                        started_at=started_at,
                        last_chunk_at=datetime.now(timezone.utc),
                    ),
                    ui_hint="stream",
                ),
                source_path=path,
                observer_archetype=archetype,
            )
        else:
            # Non-streaming result - wrap normally
            adapter = ProjectionAdapter(logos)
            yield await adapter.invoke_with_projection(path, observer, **kwargs)

    except Exception as e:
        adapter = ProjectionAdapter(logos)
        yield WidgetEnvelope(
            data=None,
            meta=adapter._build_error_meta(e, path),
            source_path=path,
            observer_archetype=archetype,
        )


# === Convenience Functions ===


def wrap_with_envelope(
    data: Any,
    path: str,
    observer: "Observer | Umwelt[Any, Any] | None" = None,
    *,
    status: WidgetStatus = WidgetStatus.DONE,
    cache: CacheMeta | None = None,
    error: ErrorInfo | None = None,
    refusal: RefusalInfo | None = None,
    ui_hint: UIHint | None = None,
) -> WidgetEnvelope[Any]:
    """
    Wrap raw data in a projection envelope.

    Convenience function for manual envelope creation.

    Args:
        data: The data to wrap.
        path: Source AGENTESE path.
        observer: Observer for archetype extraction.
        status: Widget status.
        cache: Cache metadata.
        error: Error info.
        refusal: Refusal info.
        ui_hint: UI rendering hint.

    Returns:
        Configured WidgetEnvelope.
    """
    if ui_hint is None:
        ui_hint = extract_ui_hint(path, data)

    meta = WidgetMeta(
        status=status,
        cache=cache,
        error=error,
        refusal=refusal,
        stream=None,
        ui_hint=ui_hint,
    )

    return WidgetEnvelope(
        data=data,
        meta=meta,
        source_path=path,
        observer_archetype=extract_observer_archetype(observer),
    )


__all__ = [
    "ProjectionAdapter",
    "stream_with_projection",
    "wrap_with_envelope",
    "extract_ui_hint",
    "is_deterministic_path",
    "extract_observer_archetype",
]
