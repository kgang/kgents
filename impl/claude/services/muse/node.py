"""
Muse AGENTESE Node: @node("self.muse")

The Muse - pattern detection and contextual guidance.

AGENTESE Paths:
- self.muse.manifest   - Muse state, arc phase, tension
- self.muse.arc        - Current story arc analysis
- self.muse.tension    - Tension level and trend
- self.muse.whisper    - Current suggestion (if any)
- self.muse.encourage  - Request earned encouragement
- self.muse.reframe    - Request perspective shift
- self.muse.summon     - Force suggestions (bypass timing)
- self.muse.dismiss    - Dismiss current whisper
- self.muse.accept     - Accept/acknowledge a whisper
- self.muse.history    - Whisper history

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- Muse whispers, never shouts
- Passive observation with earned encouragement

Philosophy:
    "I see the arc of your work. I know when you're rising, when you're
     stuck, when you're about to break through. I whisper—never shout."

See: docs/skills/metaphysical-fullstack.md
See: plans/witness-muse-implementation.md
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, AsyncGenerator
from uuid import uuid4

from protocols.agentese.affordances import AspectCategory, aspect
from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .arc import ArcPhase, StoryArc, StoryArcDetector
from .contracts import (
    AcceptRequest,
    AcceptResponse,
    ArcRequest,
    ArcResponse,
    DismissRequest,
    DismissResponse,
    EncourageRequest,
    EncourageResponse,
    HistoryRequest,
    HistoryResponse,
    MuseManifestResponse,
    ReframeRequest,
    ReframeResponse,
    SummonRequest,
    SummonResponse,
    TensionRequest,
    TensionResponse,
    WhisperHistoryItem,
    WhisperRequest,
    WhisperResponse,
)
from .polynomial import (
    ActivityPause,
    DormancyComplete,
    MuseContext,
    MusePolynomial,
    MuseState,
    MuseWhisper,
    RequestEncouragement,
    RequestReframe,
    SummonMuse,
    WhisperAccepted,
    WhisperDismissed,
    muse_transition,
)
from .whisper import WhisperEngine

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === MuseNode Rendering ===


@dataclass(frozen=True)
class MuseManifestRendering:
    """Rendering for muse manifest."""

    manifest: MuseManifestResponse

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "muse_manifest",
            "state": self.manifest.state,
            "arc_phase": self.manifest.arc_phase,
            "arc_confidence": self.manifest.arc_confidence,
            "tension": self.manifest.tension,
            "tension_trend": self.manifest.tension_trend,
            "crystals_observed": self.manifest.crystals_observed,
            "whispers_made": self.manifest.whispers_made,
            "whispers_accepted": self.manifest.whispers_accepted,
            "whispers_dismissed": self.manifest.whispers_dismissed,
            "acceptance_rate": self.manifest.acceptance_rate,
            "can_whisper": self.manifest.can_whisper,
            "pending_whisper_id": self.manifest.pending_whisper_id,
            "status": self.manifest.status,
        }

    def to_text(self) -> str:
        arc_emoji = {
            "EXPOSITION": "📖",
            "RISING_ACTION": "🔺",
            "CLIMAX": "⚡",
            "FALLING_ACTION": "🔻",
            "DENOUEMENT": "🌅",
        }.get(self.manifest.arc_phase, "?")

        lines = [
            "The Muse",
            "========",
            f"State: {self.manifest.state}",
            f"Arc: {arc_emoji} {self.manifest.arc_phase} (confidence: {self.manifest.arc_confidence:.0%})",
            f"Tension: {self.manifest.tension:.0%} (trend: {self.manifest.tension_trend:+.0%})",
            "",
            f"Crystals Observed: {self.manifest.crystals_observed}",
            f"Whispers Made: {self.manifest.whispers_made}",
            f"Accepted: {self.manifest.whispers_accepted} | Dismissed: {self.manifest.whispers_dismissed}",
            f"Acceptance Rate: {self.manifest.acceptance_rate:.0%}",
        ]

        if self.manifest.pending_whisper_id:
            lines.append(f"\nPending Whisper: {self.manifest.pending_whisper_id}")

        return "\n".join(lines)


# === MuseNode ===


@node(
    "self.muse",
    description="The Muse - Pattern detection and contextual whispers",
    dependencies=(),
    contracts={
        # Perception aspects
        "manifest": Response(MuseManifestResponse),
        # Query aspects
        "arc": Contract(ArcRequest, ArcResponse),
        "tension": Contract(TensionRequest, TensionResponse),
        "whisper": Contract(WhisperRequest, WhisperResponse),
        # Mutation aspects
        "encourage": Contract(EncourageRequest, EncourageResponse),
        "reframe": Contract(ReframeRequest, ReframeResponse),
        "summon": Contract(SummonRequest, SummonResponse),
        "dismiss": Contract(DismissRequest, DismissResponse),
        "accept": Contract(AcceptRequest, AcceptResponse),
        "history": Contract(HistoryRequest, HistoryResponse),
    },
    examples=[
        ("manifest", {}, "Get Muse state and arc"),
        ("arc", {}, "Get current story arc"),
        ("tension", {}, "Get tension level"),
        ("whisper", {}, "Get current whisper if any"),
        ("encourage", {"context": "stuck on tests"}, "Request encouragement"),
        ("reframe", {"context": "feels like wasted effort"}, "Request perspective shift"),
        ("summon", {"topic": "code quality"}, "Force a suggestion"),
        ("dismiss", {"whisper_id": "w-123", "reason": "not helpful"}, "Dismiss whisper"),
        ("accept", {"whisper_id": "w-123", "action": "acted"}, "Accept whisper"),
    ],
)
class MuseNode(BaseLogosNode):
    """
    AGENTESE node for The Muse Crown Jewel.

    The Muse observes Experience Crystals from The Witness and detects
    narrative structure in work sessions. It whispers contextual suggestions
    at appropriate moments, never demanding attention.

    Key Principles:
    1. PASSIVE BY DEFAULT: Observes, doesn't demand attention
    2. WHISPERS NOT SHOUTS: One suggestion at a time, easily dismissed
    3. EARNED ENCOURAGEMENT: Praise only after genuine progress
    4. AESTHETIC SENSITIVITY: Adapts tone to user's apparent mood

    Example:
        # Get current arc
        GET /agentese/self/muse/arc

        # Request encouragement
        POST /agentese/self/muse/encourage
        {"context": "stuck on this bug for hours"}

        # Force a suggestion
        POST /agentese/self/muse/summon
        {"topic": "testing strategy"}
    """

    def __init__(self) -> None:
        """Initialize MuseNode with fresh context."""
        self._context = MuseContext()
        self._polynomial = MusePolynomial()
        self._arc_detector = StoryArcDetector()
        self._whisper_engine = WhisperEngine()

        # Whisper history for history aspect
        self._whisper_history: list[dict[str, Any]] = []

    @property
    def handle(self) -> str:
        return "self.muse"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Muse is primarily for the developer/user:
        - developer/operator: Full access
        - architect/researcher: Full access (observation + guidance)
        - newcomer: Can view but not summon/encourage
        - guest: Manifest only
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access
        if archetype_lower in (
            "developer",
            "operator",
            "admin",
            "system",
            "architect",
            "researcher",
        ):
            return (
                "manifest",
                "arc",
                "tension",
                "whisper",
                "stream",  # SSE streaming
                "encourage",
                "reframe",
                "summon",
                "dismiss",
                "accept",
                "history",
            )

        # Newcomers: read-only + dismiss
        if archetype_lower in ("newcomer", "casual", "reviewer"):
            return (
                "manifest",
                "arc",
                "tension",
                "whisper",
                "stream",  # SSE streaming
                "dismiss",
                "history",
            )

        # Guest: minimal
        return ("manifest",)

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest Muse status to observer.

        AGENTESE: self.muse.manifest
        """
        ctx = self._context

        manifest = MuseManifestResponse(
            state=ctx.state.name,
            arc_phase=ctx.arc.phase.name,
            arc_confidence=ctx.arc.confidence,
            tension=ctx.tension,
            tension_trend=ctx.tension_trend,
            crystals_observed=ctx.crystals_observed,
            whispers_made=ctx.whispers_made,
            whispers_accepted=ctx.whispers_accepted,
            whispers_dismissed=ctx.whispers_dismissed,
            acceptance_rate=ctx.acceptance_rate,
            can_whisper=ctx.can_whisper,
            pending_whisper_id=ctx.pending_whisper.whisper_id if ctx.pending_whisper else None,
            status=ctx.state.name.lower(),
        )

        return MuseManifestRendering(manifest=manifest)

    @aspect(
        category=AspectCategory.PERCEPTION,
        streaming=True,
        help="Stream whispers in real-time via SSE",
        examples=["self.muse.stream", "self.muse.stream[poll_interval=60]"],
    )
    async def stream(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Stream whispers in real-time via Server-Sent Events.

        AGENTESE: self.muse.stream

        Yields whispers as they become appropriate to surface based on
        arc phase and tension. Respects min_interval between whispers.

        Args:
            poll_interval: Seconds between whisper checks (default 30.0)

        Yields:
            Whisper dicts as they become available
        """
        poll_interval = kwargs.get("poll_interval", 30.0)

        try:
            async for whisper in self._whisper_engine.whisper_stream(
                poll_interval=poll_interval,
            ):
                yield {
                    "type": "whisper",
                    "whisper_id": whisper.whisper_id,
                    "content": whisper.content,
                    "category": whisper.category.name,
                    "confidence": whisper.confidence,
                    "urgency": whisper.urgency,
                    "arc_phase": whisper.arc_phase.name,
                    "tension": whisper.tension,
                    "timestamp": whisper.delivered_at.isoformat(),
                }

                # Record in history
                from .polynomial import MuseWhisper

                muse_whisper = MuseWhisper(
                    whisper_id=whisper.whisper_id,
                    content=whisper.content,
                    category=whisper.category.name.lower(),
                    urgency=whisper.urgency,
                    confidence=whisper.confidence,
                )
                self._record_whisper_history(muse_whisper)

        except asyncio.CancelledError:
            # Clean shutdown on disconnect
            pass

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        if aspect == "arc":
            return await self._handle_arc(kwargs)
        elif aspect == "tension":
            return await self._handle_tension(kwargs)
        elif aspect == "whisper":
            return await self._handle_whisper(kwargs)
        elif aspect == "encourage":
            return await self._handle_encourage(kwargs)
        elif aspect == "reframe":
            return await self._handle_reframe(kwargs)
        elif aspect == "summon":
            return await self._handle_summon(kwargs)
        elif aspect == "dismiss":
            return await self._handle_dismiss(kwargs)
        elif aspect == "accept":
            return await self._handle_accept(kwargs)
        elif aspect == "history":
            return await self._handle_history(kwargs)
        elif aspect == "stream":
            # Return the async generator directly - gateway will handle SSE conversion
            return self.stream(observer, **kwargs)
        else:
            return {"error": f"Unknown aspect: {aspect}"}

    async def _handle_arc(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle arc aspect - get current story arc."""
        arc = self._context.arc

        return {
            "phase": arc.phase.name,
            "phase_emoji": arc.phase.emoji,
            "confidence": arc.confidence,
            "tension": arc.tension,
            "momentum": arc.momentum,
            "phase_duration_seconds": arc.phase_duration_seconds,
            "is_rising": arc.phase.is_rising,
            "is_falling": arc.phase.is_falling,
            "is_peak": arc.phase.is_peak,
        }

    async def _handle_tension(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle tension aspect - get tension level."""
        ctx = self._context
        include_trend = kwargs.get("include_trend", True)

        # Categorize tension
        if ctx.tension < 0.25:
            category = "low"
        elif ctx.tension < 0.5:
            category = "medium"
        elif ctx.tension < 0.75:
            category = "high"
        else:
            category = "critical"

        result: dict[str, Any] = {
            "level": ctx.tension,
            "category": category,
            "trigger": None,  # Would be set by tension events
        }

        if include_trend:
            result["trend"] = ctx.tension_trend

        return result

    async def _handle_whisper(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle whisper aspect - get current whisper if any."""
        whisper = self._context.pending_whisper

        if not whisper:
            return {
                "has_whisper": False,
                "whisper_id": None,
                "content": None,
                "category": None,
                "urgency": None,
                "confidence": None,
                "timestamp": None,
            }

        return {
            "has_whisper": True,
            "whisper_id": whisper.whisper_id,
            "content": whisper.content,
            "category": whisper.category,
            "urgency": whisper.urgency,
            "confidence": whisper.confidence,
            "timestamp": whisper.timestamp.isoformat(),
        }

    async def _handle_encourage(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle encourage aspect - request earned encouragement."""
        context = kwargs.get("context", "")

        # Transition via polynomial
        event = RequestEncouragement(context=context)
        self._context, output = muse_transition(self._context, event)

        whisper = output.whisper
        if not whisper:
            # Generate fallback encouragement
            whisper = MuseWhisper(
                whisper_id=f"whisper-{uuid4().hex[:8]}",
                content="You're doing important work. Keep going.",
                category="encouragement",
                urgency=0.8,
                confidence=0.7,
            )
            self._context.record_whisper(whisper)

        # Record in history
        self._record_whisper_history(whisper, accepted=False, dismissed=False)

        return {
            "whisper_id": whisper.whisper_id,
            "content": whisper.content,
            "earned": self._context.crystals_observed > 5,  # Earned if observed enough
            "arc_phase": self._context.arc.phase.name,
            "tension": self._context.tension,
            "timestamp": whisper.timestamp.isoformat(),
        }

    async def _handle_reframe(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle reframe aspect - request perspective shift."""
        context = kwargs.get("context", "")
        current_perspective = kwargs.get("current_perspective", context)

        # Transition via polynomial
        event = RequestReframe(context=context)
        self._context, output = muse_transition(self._context, event)

        whisper = output.whisper
        if not whisper:
            # Generate fallback reframe
            whisper = MuseWhisper(
                whisper_id=f"whisper-{uuid4().hex[:8]}",
                content="What if this obstacle is actually teaching you something valuable?",
                category="reframe",
                urgency=0.8,
                confidence=0.6,
            )
            self._context.record_whisper(whisper)

        # Record in history
        self._record_whisper_history(whisper, accepted=False, dismissed=False)

        return {
            "whisper_id": whisper.whisper_id,
            "content": whisper.content,
            "original_perspective": current_perspective,
            "new_perspective": whisper.content,
            "arc_phase": self._context.arc.phase.name,
            "timestamp": whisper.timestamp.isoformat(),
        }

    async def _handle_summon(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle summon aspect - force suggestion (bypass timing)."""
        topic = kwargs.get("topic", "")

        # Transition via polynomial
        event = SummonMuse(topic=topic)
        self._context, output = muse_transition(self._context, event)

        whisper = output.whisper
        if not whisper:
            # Generate fallback
            whisper = MuseWhisper(
                whisper_id=f"whisper-{uuid4().hex[:8]}",
                content=f"You summoned me about {topic if topic else 'your work'}. What specifically needs attention?",
                category="suggestion",
                urgency=1.0,
                confidence=0.5,
            )
            self._context.record_whisper(whisper)

        # Record in history
        self._record_whisper_history(whisper, accepted=False, dismissed=False)

        return {
            "whisper_id": whisper.whisper_id,
            "content": whisper.content,
            "category": whisper.category,
            "confidence": whisper.confidence,
            "summoned": True,
            "timestamp": whisper.timestamp.isoformat(),
        }

    async def _handle_dismiss(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle dismiss aspect - dismiss current whisper."""
        whisper_id = kwargs.get("whisper_id", "")
        reason = kwargs.get("reason", "")

        if not whisper_id:
            # Dismiss pending if no ID specified
            if self._context.pending_whisper:
                whisper_id = self._context.pending_whisper.whisper_id
            else:
                return {"error": "No whisper to dismiss"}

        # Transition via polynomial
        event = WhisperDismissed(whisper_id=whisper_id, method="explicit")
        self._context, output = muse_transition(self._context, event)

        # Update history
        self._update_whisper_history(whisper_id, dismissed=True)

        # Record dismissal in engine
        if self._context.pending_whisper:
            from .whisper import SuggestionCategory, Whisper

            whisper_obj = Whisper(
                whisper_id=whisper_id,
                content=self._context.pending_whisper.content,
                category=SuggestionCategory.OBSERVATION,
                confidence=self._context.pending_whisper.confidence,
                urgency=self._context.pending_whisper.urgency,
            )
            self._whisper_engine.record_dismissal(whisper_obj)

        return {
            "dismissed": True,
            "whisper_id": whisper_id,
            "cooldown_minutes": 15,  # Dormancy period
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def _handle_accept(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle accept aspect - accept/acknowledge a whisper."""
        whisper_id = kwargs.get("whisper_id", "")
        action = kwargs.get("action", "acknowledged")

        if not whisper_id:
            if self._context.pending_whisper:
                whisper_id = self._context.pending_whisper.whisper_id
            else:
                return {"error": "No whisper to accept"}

        # Transition via polynomial
        event = WhisperAccepted(whisper_id=whisper_id, action=action)
        self._context, output = muse_transition(self._context, event)

        # Update history
        self._update_whisper_history(whisper_id, accepted=True)

        return {
            "accepted": True,
            "whisper_id": whisper_id,
            "action": action,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def _handle_history(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle history aspect - get whisper history."""
        limit = kwargs.get("limit", 20)
        category = kwargs.get("category")
        accepted_only = kwargs.get("accepted_only", False)

        # Filter history
        history = self._whisper_history

        if category:
            history = [h for h in history if h.get("category") == category]

        if accepted_only:
            history = [h for h in history if h.get("accepted")]

        # Sort by timestamp (newest first) and limit
        history = sorted(history, key=lambda h: h.get("timestamp", ""), reverse=True)[:limit]

        items = [
            {
                "whisper_id": h.get("whisper_id", ""),
                "content": h.get("content", ""),
                "category": h.get("category", ""),
                "urgency": h.get("urgency", 0),
                "confidence": h.get("confidence", 0),
                "arc_phase": h.get("arc_phase", ""),
                "tension": h.get("tension", 0),
                "accepted": h.get("accepted", False),
                "dismissed": h.get("dismissed", False),
                "timestamp": h.get("timestamp", ""),
            }
            for h in history
        ]

        return {
            "count": len(items),
            "whispers": items,
        }

    def _record_whisper_history(
        self,
        whisper: MuseWhisper,
        accepted: bool = False,
        dismissed: bool = False,
    ) -> None:
        """Record a whisper in history."""
        self._whisper_history.append(
            {
                "whisper_id": whisper.whisper_id,
                "content": whisper.content,
                "category": whisper.category,
                "urgency": whisper.urgency,
                "confidence": whisper.confidence,
                "arc_phase": self._context.arc.phase.name,
                "tension": self._context.tension,
                "accepted": accepted,
                "dismissed": dismissed,
                "timestamp": whisper.timestamp.isoformat(),
            }
        )

        # Limit history size
        if len(self._whisper_history) > 100:
            self._whisper_history = self._whisper_history[-100:]

    def _update_whisper_history(
        self,
        whisper_id: str,
        accepted: bool | None = None,
        dismissed: bool | None = None,
    ) -> None:
        """Update an existing whisper in history."""
        for item in self._whisper_history:
            if item.get("whisper_id") == whisper_id:
                if accepted is not None:
                    item["accepted"] = accepted
                if dismissed is not None:
                    item["dismissed"] = dismissed
                break

    # === External API for Integration ===

    def observe_activity_pause(self, pause_seconds: float) -> None:
        """
        Observe an activity pause (good moment for whisper).

        Called by external integration when user pauses.
        """
        event = ActivityPause(pause_seconds=pause_seconds)
        self._context, output = muse_transition(self._context, event)

        if output.whisper:
            self._record_whisper_history(output.whisper)

    def check_dormancy(self) -> bool:
        """
        Check if dormancy period is complete.

        Returns True if transitioned back to SILENT.
        """
        if self._context.state == MuseState.DORMANT and self._context.check_dormancy_complete():
            event = DormancyComplete()
            self._context, output = muse_transition(self._context, event)
            return True
        return False


# === Exports ===

__all__ = [
    "MuseNode",
    "MuseManifestRendering",
]
