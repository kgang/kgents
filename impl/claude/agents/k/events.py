"""
SoulEvent: Event types for K-gent streaming.

K-gent Phase 2: The SoulEvent hierarchy defines the vocabulary of events
that flow through KgentFlux. These events enable:

1. Dialogue streaming (turn-by-turn conversation)
2. Semaphore mediation (intercept requests and results)
3. Mode changes (REFLECT, ADVISE, CHALLENGE, EXPLORE)
4. Pulse emission (vitality signals)

The event types mirror the core KgentSoul operations:
- dialogue() -> DIALOGUE_* events
- intercept() -> INTERCEPT_* events
- enter_mode() -> MODE_CHANGE event
- manifest() -> STATE_SNAPSHOT event

Event Flow:
    External → SoulEvent → KgentFlux → KgentSoul → SoulEvent → External

This is the nervous system that connects K-gent to Terrarium.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .persona import DialogueMode
    from .soul import InterceptResult, SoulDialogueOutput, SoulState


class SoulEventType(str, Enum):
    """Types of events in the K-gent stream."""

    # Dialogue events
    DIALOGUE_START = "dialogue_start"
    DIALOGUE_TURN = "dialogue_turn"
    DIALOGUE_END = "dialogue_end"

    # Mode events
    MODE_CHANGE = "mode_change"

    # Semaphore mediation events
    INTERCEPT_REQUEST = "intercept_request"
    INTERCEPT_RESULT = "intercept_result"

    # Eigenvector probing (introspection)
    EIGENVECTOR_PROBE = "eigenvector_probe"

    # Vitality signals
    PULSE = "pulse"

    # State inspection
    STATE_SNAPSHOT = "state_snapshot"

    # Error events
    ERROR = "error"

    # System events
    PING = "ping"

    # ─────────────────────────────────────────────────────────────────────────
    # Ambient Events: The soul present, not invoked
    # ─────────────────────────────────────────────────────────────────────────

    # Internal monologue / rumination
    THOUGHT = "thought"

    # Emotional state shift
    FEELING = "feeling"

    # Pattern noticed in environment
    OBSERVATION = "observation"

    # Self-initiated dialectic
    SELF_CHALLENGE = "self_challenge"

    # Environmental perturbation from external source
    PERTURBATION = "perturbation"

    # Gratitude expression (tithe to entropy)
    GRATITUDE = "gratitude"

    # ─────────────────────────────────────────────────────────────────────────
    # Dream Events: Hypnagogia (Phase 4)
    # ─────────────────────────────────────────────────────────────────────────

    # Start of a dream cycle
    DREAM_START = "dream_start"

    # Pattern discovered during dream
    DREAM_PATTERN = "dream_pattern"

    # Eigenvector adjustment during dream
    DREAM_INSIGHT = "dream_insight"

    # End of a dream cycle
    DREAM_END = "dream_end"


@dataclass(frozen=True)
class SoulEvent:
    """
    A single event in the K-gent stream.

    SoulEvents are immutable records of K-gent activity. They carry:
    - event_type: What kind of event this is
    - timestamp: When the event occurred (UTC)
    - payload: Event-specific data
    - soul_state: Optional snapshot of soul state at event time

    The frozen dataclass ensures events are hashable and immutable,
    suitable for streaming and logging.
    """

    event_type: SoulEventType
    timestamp: datetime
    payload: dict[str, Any]
    soul_state: Optional[dict[str, Any]] = None
    correlation_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        result: dict[str, Any] = {
            "type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
        }

        if self.soul_state is not None:
            result["soul_state"] = self.soul_state

        if self.correlation_id is not None:
            result["correlation_id"] = self.correlation_id

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SoulEvent":
        """
        Create a SoulEvent from a dict.

        Raises:
            KeyError: If required fields 'type' or 'timestamp' are missing
            ValueError: If 'type' is not a valid SoulEventType
        """
        if "type" not in data:
            raise KeyError("SoulEvent.from_dict requires 'type' field")
        if "timestamp" not in data:
            raise KeyError("SoulEvent.from_dict requires 'timestamp' field")

        try:
            event_type = SoulEventType(data["type"])
        except ValueError as e:
            raise ValueError(f"Invalid event type: {data['type']}") from e

        try:
            timestamp = datetime.fromisoformat(data["timestamp"])
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid timestamp: {data['timestamp']}") from e

        return cls(
            event_type=event_type,
            timestamp=timestamp,
            payload=data.get("payload", {}),
            soul_state=data.get("soul_state"),
            correlation_id=data.get("correlation_id"),
        )


# =============================================================================
# Factory Functions
# =============================================================================


def _utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


def dialogue_start_event(
    mode: str,
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """Create a DIALOGUE_START event."""
    return SoulEvent(
        event_type=SoulEventType.DIALOGUE_START,
        timestamp=_utc_now(),
        payload={"mode": mode},
        correlation_id=correlation_id,
    )


def dialogue_turn_event(
    message: str,
    response: Optional[str] = None,
    mode: Optional[str] = None,
    is_request: bool = True,
    correlation_id: Optional[str] = None,
    soul_state: Optional[dict[str, Any]] = None,
) -> SoulEvent:
    """
    Create a DIALOGUE_TURN event.

    Args:
        message: The user's message (request) or K-gent's response
        response: K-gent's response (if this is a response event)
        mode: Current dialogue mode
        is_request: True if this is a user request, False if K-gent response
        correlation_id: ID to correlate request/response pairs
        soul_state: Optional snapshot of soul state
    """
    payload: dict[str, Any] = {
        "message": message,
        "is_request": is_request,
    }

    if response is not None:
        payload["response"] = response

    if mode is not None:
        payload["mode"] = mode

    return SoulEvent(
        event_type=SoulEventType.DIALOGUE_TURN,
        timestamp=_utc_now(),
        payload=payload,
        soul_state=soul_state,
        correlation_id=correlation_id,
    )


def dialogue_end_event(
    reason: str = "completed",
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """Create a DIALOGUE_END event."""
    return SoulEvent(
        event_type=SoulEventType.DIALOGUE_END,
        timestamp=_utc_now(),
        payload={"reason": reason},
        correlation_id=correlation_id,
    )


def mode_change_event(
    from_mode: str,
    to_mode: str,
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """Create a MODE_CHANGE event."""
    return SoulEvent(
        event_type=SoulEventType.MODE_CHANGE,
        timestamp=_utc_now(),
        payload={"from_mode": from_mode, "to_mode": to_mode},
        correlation_id=correlation_id,
    )


def intercept_request_event(
    token_id: str,
    prompt: str,
    severity: str = "info",
    options: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """Create an INTERCEPT_REQUEST event."""
    return SoulEvent(
        event_type=SoulEventType.INTERCEPT_REQUEST,
        timestamp=_utc_now(),
        payload={
            "token_id": token_id,
            "prompt": prompt,
            "severity": severity,
            "options": options or [],
        },
        correlation_id=correlation_id or token_id,
    )


def intercept_result_event(
    token_id: str,
    handled: bool,
    recommendation: Optional[str] = None,
    confidence: float = 0.0,
    reasoning: str = "",
    correlation_id: Optional[str] = None,
    soul_state: Optional[dict[str, Any]] = None,
) -> SoulEvent:
    """Create an INTERCEPT_RESULT event."""
    return SoulEvent(
        event_type=SoulEventType.INTERCEPT_RESULT,
        timestamp=_utc_now(),
        payload={
            "token_id": token_id,
            "handled": handled,
            "recommendation": recommendation,
            "confidence": confidence,
            "reasoning": reasoning,
        },
        soul_state=soul_state,
        correlation_id=correlation_id or token_id,
    )


def eigenvector_probe_event(
    eigenvectors: dict[str, Any],
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """Create an EIGENVECTOR_PROBE event (introspection)."""
    return SoulEvent(
        event_type=SoulEventType.EIGENVECTOR_PROBE,
        timestamp=_utc_now(),
        payload={"eigenvectors": eigenvectors},
        correlation_id=correlation_id,
    )


def pulse_event(
    interactions_count: int = 0,
    tokens_used_session: int = 0,
    active_mode: str = "reflect",
    is_healthy: bool = True,
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """
    Create a PULSE event (vitality signal).

    Pulses are heartbeat events emitted periodically when KgentFlux is FLOWING.
    They indicate the soul is alive and provide lightweight status.
    """
    return SoulEvent(
        event_type=SoulEventType.PULSE,
        timestamp=_utc_now(),
        payload={
            "interactions_count": interactions_count,
            "tokens_used_session": tokens_used_session,
            "active_mode": active_mode,
            "is_healthy": is_healthy,
        },
        correlation_id=correlation_id,
    )


def state_snapshot_event(
    state: dict[str, Any],
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """Create a STATE_SNAPSHOT event."""
    return SoulEvent(
        event_type=SoulEventType.STATE_SNAPSHOT,
        timestamp=_utc_now(),
        payload={},
        soul_state=state,
        correlation_id=correlation_id,
    )


def error_event(
    error: str,
    error_type: Optional[str] = None,
    original_event_type: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """Create an ERROR event."""
    payload: dict[str, Any] = {"error": error}

    if error_type is not None:
        payload["error_type"] = error_type

    if original_event_type is not None:
        payload["original_event_type"] = original_event_type

    return SoulEvent(
        event_type=SoulEventType.ERROR,
        timestamp=_utc_now(),
        payload=payload,
        correlation_id=correlation_id,
    )


def ping_event() -> SoulEvent:
    """Create a PING event (keep-alive)."""
    return SoulEvent(
        event_type=SoulEventType.PING,
        timestamp=_utc_now(),
        payload={},
    )


# =============================================================================
# Ambient Event Factories: The Soul Present, Not Invoked
# =============================================================================


def _clamp_intensity(value: float) -> float:
    """Clamp intensity to [0.0, 1.0]."""
    return max(0.0, min(1.0, value))


def _clamp_depth(value: int) -> int:
    """Clamp depth to valid range [1, 3]."""
    return max(1, min(3, value))


def thought_event(
    content: str,
    depth: int = 1,
    triggered_by: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """
    Create a THOUGHT event (internal monologue / rumination).

    Thoughts are autonomous internal processes—the soul thinking
    without being prompted. They may be triggered by:
    - Time passing (idle rumination)
    - Pattern matching in recent events
    - Eigenvector tension (conflicting values)

    Args:
        content: The thought content
        depth: Rumination depth (1=surface, 3=deep), clamped to [1, 3]
        triggered_by: What triggered this thought (optional)
        correlation_id: Correlation ID for tracing
    """
    return SoulEvent(
        event_type=SoulEventType.THOUGHT,
        timestamp=_utc_now(),
        payload={
            "content": content,
            "depth": _clamp_depth(depth),
            "triggered_by": triggered_by,
        },
        correlation_id=correlation_id,
    )


def feeling_event(
    valence: str,
    intensity: float = 0.5,
    cause: Optional[str] = None,
    eigenvector_shift: Optional[dict[str, float]] = None,
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """
    Create a FEELING event (emotional state shift).

    Feelings represent shifts in the soul's affective state.
    Unlike thoughts, they're non-propositional—more like
    color changes than sentences.

    Args:
        valence: The emotional quality (e.g., "curious", "frustrated", "delighted")
        intensity: 0.0 to 1.0 (calm → intense), clamped to valid range
        cause: What caused this feeling (optional)
        eigenvector_shift: How this affects eigenvector weights
        correlation_id: Correlation ID for tracing
    """
    payload: dict[str, Any] = {
        "valence": valence,
        "intensity": _clamp_intensity(intensity),
    }
    if cause is not None:
        payload["cause"] = cause
    if eigenvector_shift is not None:
        payload["eigenvector_shift"] = eigenvector_shift

    return SoulEvent(
        event_type=SoulEventType.FEELING,
        timestamp=_utc_now(),
        payload=payload,
        correlation_id=correlation_id,
    )


def observation_event(
    pattern: str,
    confidence: float = 0.5,
    domain: str = "general",
    evidence: Optional[list[str]] = None,
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """
    Create an OBSERVATION event (pattern noticed in environment).

    Observations are the soul noticing patterns in its environment—
    the kgents ecosystem, conversation history, or external data.

    Args:
        pattern: The pattern observed
        confidence: 0.0 to 1.0 (uncertain → certain), clamped to valid range
        domain: What domain this observation is in
        evidence: Supporting evidence for the pattern
        correlation_id: Correlation ID for tracing
    """
    return SoulEvent(
        event_type=SoulEventType.OBSERVATION,
        timestamp=_utc_now(),
        payload={
            "pattern": pattern,
            "confidence": _clamp_intensity(confidence),  # Reuse intensity clamping
            "domain": domain,
            "evidence": evidence or [],
        },
        correlation_id=correlation_id,
    )


def self_challenge_event(
    thesis: str,
    antithesis: str,
    synthesis: Optional[str] = None,
    eigenvector: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """
    Create a SELF_CHALLENGE event (self-initiated dialectic).

    Self-challenges are the soul questioning its own beliefs—
    the internal voice that says "but what if you're wrong?"

    This follows the THESIS → ANTITHESIS → SYNTHESIS pattern
    from the dialectic tradition.

    Args:
        thesis: The belief being challenged
        antithesis: The counter-argument
        synthesis: Resolution (if reached)
        eigenvector: Which eigenvector is being examined
        correlation_id: Correlation ID for tracing
    """
    payload: dict[str, Any] = {
        "thesis": thesis,
        "antithesis": antithesis,
    }
    if synthesis is not None:
        payload["synthesis"] = synthesis
    if eigenvector is not None:
        payload["eigenvector"] = eigenvector

    return SoulEvent(
        event_type=SoulEventType.SELF_CHALLENGE,
        timestamp=_utc_now(),
        payload=payload,
        correlation_id=correlation_id,
    )


def perturbation_event(
    source: str,
    intensity: float = 0.5,
    data: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """
    Create a PERTURBATION event (environmental stimulus).

    Perturbations are external stimuli that the soul must process—
    events from Purgatory, Semaphore tokens, or Terrarium webhooks.

    Args:
        source: Where the perturbation came from
        intensity: 0.0 to 1.0 (gentle → intense), clamped to valid range
        data: Additional data from the source
        correlation_id: Correlation ID for tracing
    """
    return SoulEvent(
        event_type=SoulEventType.PERTURBATION,
        timestamp=_utc_now(),
        payload={
            "source": source,
            "intensity": _clamp_intensity(intensity),
            "data": data or {},
        },
        correlation_id=correlation_id,
    )


def gratitude_event(
    for_what: str,
    to_whom: Optional[str] = None,
    depth: int = 1,
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """
    Create a GRATITUDE event (tithe to entropy).

    Gratitude is the soul's acknowledgment of what it has received—
    a tithe to the Accursed Share. Per AGENTESE, every operation
    should occasionally express gratitude for the resources consumed.

    Args:
        for_what: What the soul is grateful for
        to_whom: The recipient of gratitude (optional)
        depth: How deep the gratitude goes (1=surface, 3=profound), clamped to [1, 3]
        correlation_id: Correlation ID for tracing
    """
    payload: dict[str, Any] = {
        "for_what": for_what,
        "depth": _clamp_depth(depth),
    }
    if to_whom is not None:
        payload["to_whom"] = to_whom

    return SoulEvent(
        event_type=SoulEventType.GRATITUDE,
        timestamp=_utc_now(),
        payload=payload,
        correlation_id=correlation_id,
    )


# =============================================================================
# Higher-Level Event Creation (from Soul Types)
# =============================================================================


def from_dialogue_output(
    output: "SoulDialogueOutput",
    original_message: str,
    soul_state: Optional["SoulState"] = None,
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """Create a DIALOGUE_TURN event from SoulDialogueOutput."""
    state_dict: Optional[dict[str, Any]] = None
    if soul_state is not None:
        state_dict = {
            "mode": soul_state.active_mode.value,
            "interactions_count": soul_state.interactions_count,
            "tokens_used_session": soul_state.tokens_used_session,
        }

    return SoulEvent(
        event_type=SoulEventType.DIALOGUE_TURN,
        timestamp=_utc_now(),
        payload={
            "message": original_message,
            "response": output.response,
            "mode": output.mode.value,
            "is_request": False,
            "budget_tier": output.budget_tier.value,
            "tokens_used": output.tokens_used,
            "was_template": output.was_template,
        },
        soul_state=state_dict,
        correlation_id=correlation_id,
    )


def from_intercept_result(
    result: "InterceptResult",
    token_id: str,
    soul_state: Optional["SoulState"] = None,
    correlation_id: Optional[str] = None,
) -> SoulEvent:
    """Create an INTERCEPT_RESULT event from InterceptResult."""
    state_dict: Optional[dict[str, Any]] = None
    if soul_state is not None:
        state_dict = {
            "mode": soul_state.active_mode.value,
            "interactions_count": soul_state.interactions_count,
        }

    return SoulEvent(
        event_type=SoulEventType.INTERCEPT_RESULT,
        timestamp=_utc_now(),
        payload={
            "token_id": token_id,
            "handled": result.handled,
            "recommendation": result.recommendation,
            "confidence": result.confidence,
            "reasoning": result.reasoning,
            "was_deep": result.was_deep,
            "matching_principles": result.matching_principles,
        },
        soul_state=state_dict,
        correlation_id=correlation_id or token_id,
    )


# =============================================================================
# Event Predicates
# =============================================================================


def is_dialogue_event(event: SoulEvent) -> bool:
    """Check if event is a dialogue event."""
    return event.event_type in (
        SoulEventType.DIALOGUE_START,
        SoulEventType.DIALOGUE_TURN,
        SoulEventType.DIALOGUE_END,
    )


def is_intercept_event(event: SoulEvent) -> bool:
    """Check if event is an intercept event."""
    return event.event_type in (
        SoulEventType.INTERCEPT_REQUEST,
        SoulEventType.INTERCEPT_RESULT,
    )


def is_system_event(event: SoulEvent) -> bool:
    """Check if event is a system event (pulse, ping, snapshot)."""
    return event.event_type in (
        SoulEventType.PULSE,
        SoulEventType.PING,
        SoulEventType.STATE_SNAPSHOT,
    )


def is_request_event(event: SoulEvent) -> bool:
    """Check if event requires processing (vs. response/status)."""
    return event.event_type in (
        SoulEventType.DIALOGUE_TURN,
        SoulEventType.INTERCEPT_REQUEST,
        SoulEventType.MODE_CHANGE,
        SoulEventType.EIGENVECTOR_PROBE,
    ) and event.payload.get("is_request", True)


def is_ambient_event(event: SoulEvent) -> bool:
    """
    Check if event is an ambient event (soul present, not invoked).

    Ambient events are autonomous—generated by the soul without
    external prompting. They represent the soul's ongoing internal
    life rather than responses to requests.
    """
    return event.event_type in (
        SoulEventType.THOUGHT,
        SoulEventType.FEELING,
        SoulEventType.OBSERVATION,
        SoulEventType.SELF_CHALLENGE,
        SoulEventType.GRATITUDE,
    )


def is_external_event(event: SoulEvent) -> bool:
    """
    Check if event originated from external source.

    External events come from outside the soul—user dialogue,
    system perturbations, or API requests.
    """
    return event.event_type in (
        SoulEventType.DIALOGUE_TURN,
        SoulEventType.INTERCEPT_REQUEST,
        SoulEventType.MODE_CHANGE,
        SoulEventType.PERTURBATION,
        SoulEventType.PING,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core types
    "SoulEventType",
    "SoulEvent",
    # Factory functions - Transactional
    "dialogue_start_event",
    "dialogue_turn_event",
    "dialogue_end_event",
    "mode_change_event",
    "intercept_request_event",
    "intercept_result_event",
    "eigenvector_probe_event",
    "pulse_event",
    "state_snapshot_event",
    "error_event",
    "ping_event",
    # Factory functions - Ambient (soul present, not invoked)
    "thought_event",
    "feeling_event",
    "observation_event",
    "self_challenge_event",
    "perturbation_event",
    "gratitude_event",
    # Higher-level factories
    "from_dialogue_output",
    "from_intercept_result",
    # Predicates
    "is_dialogue_event",
    "is_intercept_event",
    "is_system_event",
    "is_request_event",
    "is_ambient_event",
    "is_external_event",
]
