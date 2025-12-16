"""
AGENTESE Handlers for The Gardener.

Wires AGENTESE paths to GardenerSession operations:
    concept.gardener.session.create  → GardenerSession.create()
    concept.gardener.session.manifest → session.manifest()
    concept.gardener.session.resume  → SessionStore.get_active() + from_state()
    concept.gardener.session.advance → session.advance()

See: plans/core-apps/the-gardener.md
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from opentelemetry import trace

from .persistence import SessionStore, create_session_store
from .session import (
    GardenerSession,
    SessionConfig,
    SessionIntent,
    SessionPhase,
    SessionState,
    create_gardener_session,
    project_session_to_ascii,
    project_session_to_dict,
)

if TYPE_CHECKING:
    from protocols.agentese.logos import Logos


# =============================================================================
# OTEL Telemetry
# =============================================================================

_tracer: trace.Tracer | None = None


def _get_handler_tracer() -> trace.Tracer:
    """Get the handler tracer, creating if needed."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("kgents.gardener.handlers", "0.1.0")
    return _tracer


# =============================================================================
# GardenerContext: Runtime state for handlers
# =============================================================================


@dataclass
class GardenerContext:
    """
    Runtime context for Gardener AGENTESE handlers.

    Maintains the active session and persistence store.
    Injected into Logos for path resolution.
    """

    store: SessionStore
    active_session: GardenerSession | None = None
    config: SessionConfig = field(default_factory=SessionConfig)
    _initialized: bool = field(default=False, init=False)

    async def init(self) -> None:
        """Initialize the context (idempotent)."""
        if self._initialized:
            return

        await self.store.init()

        # Try to resume active session from store
        stored = await self.store.get_active()
        if stored:
            state = SessionState.from_dict(stored.state)
            state.session_id = stored.id
            state.name = stored.name
            state.plan_path = stored.plan_path

            phase = SessionPhase[stored.phase]
            self.active_session = GardenerSession.from_state(
                state=state,
                phase=phase,
                config=self.config,
                store=self.store,
            )

        self._initialized = True


# =============================================================================
# AGENTESE Handlers
# =============================================================================


async def handle_session_create(
    ctx: GardenerContext,
    observer: dict[str, Any],
    **kwargs: Any,
) -> dict[str, Any]:
    """
    concept.gardener.session.create → Create a new development session.

    Args:
        ctx: GardenerContext
        observer: Observer umwelt (not used for creation)
        name: Session name (required)
        plan_path: Optional link to forest plan file
        intent: Optional initial intent description

    Returns:
        Session manifest dict with id, phase, etc.
    """
    tracer = _get_handler_tracer()
    with tracer.start_as_current_span("gardener.session.create") as span:
        name = kwargs.get("name", f"Session-{uuid.uuid4().hex[:8]}")
        plan_path = kwargs.get("plan_path")
        intent_str = kwargs.get("intent")

        span.set_attribute("session.name", name)
        if plan_path:
            span.set_attribute("session.plan_path", plan_path)

        # Create session
        session = create_gardener_session(
            name=name,
            plan_path=plan_path,
            config=ctx.config,
            store=ctx.store,
        )

        # Set intent if provided
        if intent_str:
            intent = (
                SessionIntent.from_dict(intent_str)
                if isinstance(intent_str, dict)
                else SessionIntent(description=str(intent_str))
            )
            await session.set_intent(intent)

        # Persist to store
        await ctx.store.create(
            session_id=session.session_id,
            name=name,
            plan_path=plan_path,
            initial_state=session.state.to_dict(),
            intent=intent.to_dict() if intent_str else None,
        )

        # Set as active
        ctx.active_session = session

        return {
            "status": "created",
            "session": project_session_to_dict(session),
        }


async def handle_session_manifest(
    ctx: GardenerContext,
    observer: dict[str, Any],
    **kwargs: Any,
) -> dict[str, Any]:
    """
    concept.gardener.session.manifest → View current session state.

    Args:
        ctx: GardenerContext
        observer: Observer umwelt (affects projection format)
        session_id: Optional specific session to manifest (default: active)
        format: "dict" or "ascii" (default: "dict")

    Returns:
        Session state projection.
    """
    tracer = _get_handler_tracer()
    with tracer.start_as_current_span("gardener.session.manifest") as span:
        session_id = kwargs.get("session_id")
        fmt = kwargs.get("format", "dict")

        # Get session
        if session_id:
            stored = await ctx.store.get(session_id)
            if not stored:
                return {
                    "status": "error",
                    "message": f"Session not found: {session_id}",
                }

            state = SessionState.from_dict(stored.state)
            state.session_id = stored.id
            state.name = stored.name
            state.plan_path = stored.plan_path

            session = GardenerSession.from_state(
                state=state,
                phase=SessionPhase[stored.phase],
                config=ctx.config,
                store=ctx.store,
            )
        elif ctx.active_session:
            session = ctx.active_session
        else:
            return {"status": "error", "message": "No active session"}

        span.set_attribute("session.id", session.session_id)
        span.set_attribute("format", fmt)

        if fmt == "ascii":
            return {
                "status": "manifest",
                "format": "ascii",
                "content": project_session_to_ascii(session),
            }

        return {
            "status": "manifest",
            "format": "dict",
            "session": project_session_to_dict(session),
        }


async def handle_session_resume(
    ctx: GardenerContext,
    observer: dict[str, Any],
    **kwargs: Any,
) -> dict[str, Any]:
    """
    concept.gardener.session.resume → Resume an existing session.

    Implements `kg /continue` functionality.

    Args:
        ctx: GardenerContext
        observer: Observer umwelt
        session_id: Optional specific session to resume (default: last active)

    Returns:
        Resumed session manifest.
    """
    tracer = _get_handler_tracer()
    with tracer.start_as_current_span("gardener.session.resume") as span:
        session_id = kwargs.get("session_id")

        # Find session to resume
        if session_id:
            stored = await ctx.store.get(session_id)
        else:
            stored = await ctx.store.get_active()

        if not stored:
            # List recent sessions for user
            recent = await ctx.store.list_recent(limit=5)
            return {
                "status": "no_session",
                "message": "No active session to resume",
                "recent_sessions": [
                    {"id": s.id, "name": s.name, "phase": s.phase} for s in recent
                ],
            }

        span.set_attribute("session.id", stored.id)
        span.set_attribute("session.name", stored.name)

        # Reconstruct session
        state = SessionState.from_dict(stored.state)
        state.session_id = stored.id
        state.name = stored.name
        state.plan_path = stored.plan_path

        session = GardenerSession.from_state(
            state=state,
            phase=SessionPhase[stored.phase],
            config=ctx.config,
            store=ctx.store,
        )

        # Mark as resumed in store
        await ctx.store.mark_resumed(stored.id)

        # Set as active
        ctx.active_session = session

        return {
            "status": "resumed",
            "session": project_session_to_dict(session),
        }


async def handle_session_advance(
    ctx: GardenerContext,
    observer: dict[str, Any],
    **kwargs: Any,
) -> dict[str, Any]:
    """
    concept.gardener.session.advance → Advance to next phase.

    Args:
        ctx: GardenerContext
        observer: Observer umwelt

    Returns:
        Phase transition result.
    """
    tracer = _get_handler_tracer()
    with tracer.start_as_current_span("gardener.session.advance") as span:
        if not ctx.active_session:
            return {"status": "error", "message": "No active session"}

        span.set_attribute("session.id", ctx.active_session.session_id)
        span.set_attribute("phase.from", ctx.active_session.phase.name)

        result = await ctx.active_session.advance()

        span.set_attribute("phase.to", ctx.active_session.phase.name)

        return result


# =============================================================================
# Handler Registry
# =============================================================================


GARDENER_HANDLERS: dict[str, Any] = {
    "concept.gardener.session.create": handle_session_create,
    "concept.gardener.session.manifest": handle_session_manifest,
    "concept.gardener.session.resume": handle_session_resume,
    "concept.gardener.session.advance": handle_session_advance,
}


async def register_gardener_handlers(
    logos: "Logos",
    ctx: GardenerContext | None = None,
) -> GardenerContext:
    """
    Register Gardener AGENTESE handlers with a Logos instance.

    Args:
        logos: The Logos instance to register with
        ctx: Optional pre-configured GardenerContext

    Returns:
        The initialized GardenerContext
    """
    if ctx is None:
        ctx = GardenerContext(store=create_session_store())

    await ctx.init()

    # Register handlers with context closure
    for path, handler in GARDENER_HANDLERS.items():

        async def make_handler(h: Any, c: GardenerContext) -> Any:
            async def wrapped(observer: dict[str, Any], **kwargs: Any) -> Any:
                return await h(c, observer, **kwargs)

            return wrapped

        # Store handler reference for logos
        if not hasattr(logos, "_gardener_handlers"):
            logos._gardener_handlers = {}  # type: ignore[attr-defined]
        logos._gardener_handlers[path] = (handler, ctx)  # type: ignore[attr-defined]

    return ctx


__all__ = [
    "GardenerContext",
    "handle_session_create",
    "handle_session_manifest",
    "handle_session_resume",
    "handle_session_advance",
    "GARDENER_HANDLERS",
    "register_gardener_handlers",
]
