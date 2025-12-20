"""
MusePolynomial: State Machine for Contextual Guidance.

The Muse polynomial models the passive suggestion lifecycle:
- SILENT: Observing, accumulating patterns (not dormant—actively watching)
- CONTEMPLATING: Detected potential suggestion, building confidence
- WHISPERING: Suggestion ready, waiting for right moment
- RESONATING: Suggestion accepted, elaborating if asked
- REFLECTING: User engaged with suggestion, tracking outcome
- DORMANT: Cooldown after suggestion cycle (prevents over-guidance)

Key Insight from meta.md:
    "SILENT ≠ DORMANT (actively observing vs cooldown)"

The Muse never demands attention. It waits for pauses in activity
to surface suggestions, and backs off immediately if dismissed.

See: plans/witness-muse-implementation.md
See: docs/skills/polynomial-agent.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, FrozenSet

from .arc import ArcPhase, StoryArc

if TYPE_CHECKING:
    from services.witness.crystal import ExperienceCrystal


# =============================================================================
# Muse State (Activity Phases)
# =============================================================================


class MuseState(Enum):
    """
    Activity phases for The Muse.

    The key insight: SILENT and DORMANT are different.
    - SILENT: Actively observing, accumulating pattern data
    - DORMANT: Intentional cooldown, reduced observation
    """

    SILENT = auto()  # Actively watching, no suggestion ready
    CONTEMPLATING = auto()  # Building a suggestion, gaining confidence
    WHISPERING = auto()  # Suggestion ready, waiting for good moment
    RESONATING = auto()  # User engaged, suggestion in conversation
    REFLECTING = auto()  # Tracking outcome of taken suggestion
    DORMANT = auto()  # Cooldown after suggestion cycle

    @property
    def is_active(self) -> bool:
        """Is the Muse actively processing?"""
        return self in (MuseState.SILENT, MuseState.CONTEMPLATING, MuseState.WHISPERING)

    @property
    def is_engaged(self) -> bool:
        """Is the Muse in conversation with user?"""
        return self in (MuseState.RESONATING, MuseState.REFLECTING)

    @property
    def allows_suggestion(self) -> bool:
        """Can a new suggestion be formed?"""
        return self in (MuseState.SILENT, MuseState.CONTEMPLATING)


# =============================================================================
# Input Types (Events and Commands)
# =============================================================================


@dataclass(frozen=True)
class CrystalObserved:
    """A new Experience Crystal was created."""

    crystal_id: str
    session_id: str
    mood_brightness: float
    topics: tuple[str, ...]
    complexity: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ArcShift:
    """Detected shift in story arc phase."""

    from_phase: ArcPhase
    to_phase: ArcPhase
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class TensionRising:
    """Tension level increased (struggle detected)."""

    previous: float
    current: float
    trigger: str  # What caused the tension
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ActivityPause:
    """User paused activity (good moment for whisper)."""

    pause_seconds: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class WhisperAccepted:
    """User engaged with a whisper."""

    whisper_id: str
    action: str  # "viewed", "clicked", "dismissed", "acted"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class WhisperDismissed:
    """User dismissed a whisper."""

    whisper_id: str
    method: str  # "explicit", "timeout", "new_activity"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class RequestEncouragement:
    """User requested encouragement."""

    context: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class RequestReframe:
    """User requested perspective shift."""

    context: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class SummonMuse:
    """Force the Muse to suggest (bypass timing)."""

    topic: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class DormancyComplete:
    """Cooldown period ended."""

    timestamp: datetime = field(default_factory=datetime.now)


MuseEvent = CrystalObserved | ArcShift | TensionRising | ActivityPause
MuseCommand = (
    WhisperAccepted
    | WhisperDismissed
    | RequestEncouragement
    | RequestReframe
    | SummonMuse
    | DormancyComplete
)
MuseInput = MuseEvent | MuseCommand


# =============================================================================
# Output Types
# =============================================================================


@dataclass(frozen=True)
class MuseWhisper:
    """A suggestion from the Muse."""

    whisper_id: str
    content: str
    category: str  # "encouragement", "reframe", "suggestion", "observation"
    urgency: float  # 0.0 (passive) to 1.0 (should surface soon)
    confidence: float  # How sure the Muse is this will help
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class MuseSilence:
    """The Muse has nothing to say (also a valid output)."""

    reason: str  # "observing", "cooldown", "no_pattern"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MuseOutput:
    """Output from Muse transitions."""

    state: MuseState
    success: bool
    message: str = ""
    whisper: MuseWhisper | None = None
    silence: MuseSilence | None = None
    arc: StoryArc | None = None
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# Muse State (Full Context)
# =============================================================================


@dataclass
class MuseContext:
    """
    Complete Muse state context.

    Tracks arc, tension, recent crystals, and suggestion history.
    """

    state: MuseState = MuseState.SILENT
    arc: StoryArc = field(default_factory=lambda: StoryArc())
    tension: float = 0.0  # Current tension level [0, 1]
    tension_trend: float = 0.0  # Rate of change

    # Recent observations
    crystals_observed: int = 0
    last_crystal_time: datetime | None = None

    # Suggestion history
    whispers_made: int = 0
    whispers_accepted: int = 0
    whispers_dismissed: int = 0
    last_whisper_time: datetime | None = None

    # Cooldown tracking
    dormancy_started: datetime | None = None
    dormancy_duration: timedelta = timedelta(minutes=15)

    # Current whisper (if any)
    pending_whisper: MuseWhisper | None = None

    MAX_TENSION = 1.0
    WHISPER_COOLDOWN = timedelta(minutes=5)

    def observe_crystal(self, event: CrystalObserved) -> None:
        """Record a crystal observation."""
        self.crystals_observed += 1
        self.last_crystal_time = event.timestamp

    def record_whisper(self, whisper: MuseWhisper) -> None:
        """Record a whisper made."""
        self.whispers_made += 1
        self.last_whisper_time = whisper.timestamp
        self.pending_whisper = whisper

    def record_acceptance(self) -> None:
        """Record whisper accepted."""
        self.whispers_accepted += 1
        self.pending_whisper = None

    def record_dismissal(self) -> None:
        """Record whisper dismissed."""
        self.whispers_dismissed += 1
        self.pending_whisper = None

    def enter_dormancy(self) -> None:
        """Enter dormancy cooldown."""
        self.dormancy_started = datetime.now()
        self.state = MuseState.DORMANT

    def check_dormancy_complete(self) -> bool:
        """Check if dormancy period is over."""
        if self.dormancy_started is None:
            return True
        elapsed = datetime.now() - self.dormancy_started
        return elapsed >= self.dormancy_duration

    @property
    def acceptance_rate(self) -> float:
        """Whisper acceptance rate."""
        total = self.whispers_accepted + self.whispers_dismissed
        if total == 0:
            return 0.5  # Default to neutral
        return self.whispers_accepted / total

    @property
    def can_whisper(self) -> bool:
        """Can a new whisper be made?"""
        if self.pending_whisper is not None:
            return False
        if self.last_whisper_time is None:
            return True
        elapsed = datetime.now() - self.last_whisper_time
        return elapsed >= self.WHISPER_COOLDOWN

    def update_tension(self, delta: float) -> None:
        """Update tension level."""
        old_tension = self.tension
        self.tension = max(0.0, min(self.MAX_TENSION, self.tension + delta))
        self.tension_trend = self.tension - old_tension


# =============================================================================
# Direction Function (Valid Inputs per State)
# =============================================================================


def muse_directions(context: MuseContext) -> FrozenSet[type]:
    """
    Valid inputs for each Muse state.

    Encodes what events/commands are accepted in each state.
    """
    # All states accept crystal observations and arc shifts
    base: set[type] = {CrystalObserved, ArcShift, TensionRising}

    if context.state == MuseState.SILENT:
        # Can start contemplating, accept pause signals
        base.update({ActivityPause, SummonMuse})

    elif context.state == MuseState.CONTEMPLATING:
        # Can transition to whispering on pause
        base.update({ActivityPause, SummonMuse})

    elif context.state == MuseState.WHISPERING:
        # Waiting for user reaction
        base.update({WhisperAccepted, WhisperDismissed, ActivityPause})

    elif context.state == MuseState.RESONATING:
        # User engaged, can request more
        base.update({RequestEncouragement, RequestReframe, WhisperDismissed})

    elif context.state == MuseState.REFLECTING:
        # Tracking outcome
        base.update({WhisperDismissed})

    elif context.state == MuseState.DORMANT:
        # Waiting for cooldown
        base.add(DormancyComplete)

    return frozenset(base)


# =============================================================================
# Transition Function
# =============================================================================


def muse_transition(context: MuseContext, input: MuseInput) -> tuple[MuseContext, MuseOutput]:
    """
    Muse state transition function.

    transition: Context × Input → (NewContext, Output)
    """
    # Handle events first
    if isinstance(input, CrystalObserved):
        return _handle_crystal(context, input)
    elif isinstance(input, ArcShift):
        return _handle_arc_shift(context, input)
    elif isinstance(input, TensionRising):
        return _handle_tension(context, input)
    elif isinstance(input, ActivityPause):
        return _handle_pause(context, input)

    # Handle commands
    if isinstance(input, WhisperAccepted):
        return _handle_accepted(context, input)
    elif isinstance(input, WhisperDismissed):
        return _handle_dismissed(context, input)
    elif isinstance(input, RequestEncouragement):
        return _handle_encouragement(context, input)
    elif isinstance(input, RequestReframe):
        return _handle_reframe(context, input)
    elif isinstance(input, SummonMuse):
        return _handle_summon(context, input)
    elif isinstance(input, DormancyComplete):
        return _handle_dormancy_complete(context, input)

    # Unknown input
    return context, MuseOutput(
        state=context.state,
        success=False,
        message=f"Unknown input: {type(input).__name__}",
    )


# =============================================================================
# Transition Handlers
# =============================================================================


def _handle_crystal(context: MuseContext, event: CrystalObserved) -> tuple[MuseContext, MuseOutput]:
    """Handle crystal observation."""
    context.observe_crystal(event)

    # Update arc based on mood and complexity
    if event.mood_brightness > 0.7:
        # Bright mood might indicate progress
        if context.arc.phase in (ArcPhase.RISING_ACTION, ArcPhase.EXPOSITION):
            context.arc = context.arc.advance()
    elif event.mood_brightness < 0.3:
        # Dark mood might indicate struggle
        context.update_tension(0.1)

    # If we have enough observations, consider contemplating
    if context.state == MuseState.SILENT and context.crystals_observed >= 3:
        if context.can_whisper and context.tension > 0.3:
            context.state = MuseState.CONTEMPLATING

    return context, MuseOutput(
        state=context.state,
        success=True,
        message=f"Observed crystal {event.crystal_id[:8]}",
        arc=context.arc,
    )


def _handle_arc_shift(context: MuseContext, event: ArcShift) -> tuple[MuseContext, MuseOutput]:
    """Handle detected arc shift."""
    context.arc = StoryArc(phase=event.to_phase, confidence=event.confidence)

    # Arc shifts are often good moments for encouragement
    if event.to_phase == ArcPhase.CLIMAX:
        context.update_tension(0.2)
    elif event.to_phase == ArcPhase.FALLING_ACTION:
        context.update_tension(-0.3)  # Release tension after climax

    return context, MuseOutput(
        state=context.state,
        success=True,
        message=f"Arc shifted: {event.from_phase.name} → {event.to_phase.name}",
        arc=context.arc,
    )


def _handle_tension(context: MuseContext, event: TensionRising) -> tuple[MuseContext, MuseOutput]:
    """Handle rising tension."""
    context.update_tension(event.current - event.previous)

    # High tension might trigger contemplation
    if context.state == MuseState.SILENT and context.tension > 0.5:
        context.state = MuseState.CONTEMPLATING

    return context, MuseOutput(
        state=context.state,
        success=True,
        message=f"Tension: {event.previous:.2f} → {event.current:.2f}",
    )


def _handle_pause(context: MuseContext, event: ActivityPause) -> tuple[MuseContext, MuseOutput]:
    """Handle activity pause—good moment for whisper."""
    import uuid

    # Only whisper on meaningful pauses
    if event.pause_seconds < 5:
        return context, MuseOutput(
            state=context.state,
            success=True,
            message="Pause too brief for whisper",
        )

    if context.state == MuseState.CONTEMPLATING and context.can_whisper:
        # Generate whisper
        whisper = MuseWhisper(
            whisper_id=f"whisper-{uuid.uuid4().hex[:8]}",
            content=_generate_whisper_content(context),
            category="observation",
            urgency=min(context.tension, 0.8),
            confidence=context.arc.confidence,
        )
        context.record_whisper(whisper)
        context.state = MuseState.WHISPERING

        return context, MuseOutput(
            state=context.state,
            success=True,
            message="Whisper ready",
            whisper=whisper,
        )

    return context, MuseOutput(
        state=context.state,
        success=True,
        message=f"Pause observed ({event.pause_seconds:.1f}s)",
    )


def _handle_accepted(
    context: MuseContext, event: WhisperAccepted
) -> tuple[MuseContext, MuseOutput]:
    """Handle whisper acceptance."""
    context.record_acceptance()

    if event.action == "acted":
        context.state = MuseState.REFLECTING
    else:
        context.state = MuseState.RESONATING

    return context, MuseOutput(
        state=context.state,
        success=True,
        message=f"Whisper {event.action}",
    )


def _handle_dismissed(
    context: MuseContext, event: WhisperDismissed
) -> tuple[MuseContext, MuseOutput]:
    """Handle whisper dismissal."""
    context.record_dismissal()
    context.enter_dormancy()

    return context, MuseOutput(
        state=MuseState.DORMANT,
        success=True,
        message=f"Whisper dismissed ({event.method})",
        silence=MuseSilence(reason="cooldown"),
    )


def _handle_encouragement(
    context: MuseContext, event: RequestEncouragement
) -> tuple[MuseContext, MuseOutput]:
    """Handle encouragement request."""
    import uuid

    # Generate encouragement whisper
    whisper = MuseWhisper(
        whisper_id=f"whisper-{uuid.uuid4().hex[:8]}",
        content=_generate_encouragement(context, event.context),
        category="encouragement",
        urgency=0.9,  # Requested, so high urgency
        confidence=0.8,
    )
    context.record_whisper(whisper)
    context.state = MuseState.WHISPERING

    return context, MuseOutput(
        state=context.state,
        success=True,
        message="Encouragement ready",
        whisper=whisper,
    )


def _handle_reframe(context: MuseContext, event: RequestReframe) -> tuple[MuseContext, MuseOutput]:
    """Handle reframe request."""
    import uuid

    whisper = MuseWhisper(
        whisper_id=f"whisper-{uuid.uuid4().hex[:8]}",
        content=_generate_reframe(context, event.context),
        category="reframe",
        urgency=0.9,
        confidence=0.7,
    )
    context.record_whisper(whisper)
    context.state = MuseState.WHISPERING

    return context, MuseOutput(
        state=context.state,
        success=True,
        message="Reframe ready",
        whisper=whisper,
    )


def _handle_summon(context: MuseContext, event: SummonMuse) -> tuple[MuseContext, MuseOutput]:
    """Handle forced summon (bypass timing)."""
    import uuid

    whisper = MuseWhisper(
        whisper_id=f"whisper-{uuid.uuid4().hex[:8]}",
        content=_generate_summoned_whisper(context, event.topic),
        category="suggestion",
        urgency=1.0,  # Summoned = immediate
        confidence=0.6,  # Lower confidence since forced
    )
    context.record_whisper(whisper)
    context.state = MuseState.WHISPERING

    return context, MuseOutput(
        state=context.state,
        success=True,
        message="Muse summoned",
        whisper=whisper,
    )


def _handle_dormancy_complete(
    context: MuseContext, event: DormancyComplete
) -> tuple[MuseContext, MuseOutput]:
    """Handle dormancy period ending."""
    context.state = MuseState.SILENT
    context.dormancy_started = None

    return context, MuseOutput(
        state=MuseState.SILENT,
        success=True,
        message="Dormancy complete, observing",
        silence=MuseSilence(reason="observing"),
    )


# =============================================================================
# Whisper Content Generation (Templates)
# =============================================================================


def _generate_whisper_content(context: MuseContext) -> str:
    """Generate whisper content based on context."""
    if context.tension > 0.7:
        return "I notice you've been working through something challenging. Take a breath—you're closer than you think."
    elif context.arc.phase == ArcPhase.RISING_ACTION:
        return "The complexity is building. Consider committing your current progress before the next push."
    elif context.arc.phase == ArcPhase.CLIMAX:
        return "This feels like a turning point. Trust your instincts here."
    else:
        return "You're making steady progress. The pattern is forming."


def _generate_encouragement(context: MuseContext, user_context: str) -> str:
    """Generate encouragement based on context."""
    if context.crystals_observed > 10:
        return f"You've been at this for a while—{context.crystals_observed} observations captured. That's real dedication."
    elif context.whispers_accepted > context.whispers_dismissed:
        return "You're doing great. Your instincts have been right more often than not."
    else:
        return "Every attempt teaches something. The pattern will emerge."


def _generate_reframe(context: MuseContext, user_context: str) -> str:
    """Generate perspective shift."""
    if context.tension > 0.5:
        return "What if this difficulty is actually protecting you from a larger mistake?"
    elif context.arc.phase == ArcPhase.EXPOSITION:
        return "Understanding is a form of progress. The code you're reading now will inform decisions later."
    else:
        return "Consider: what would future-you wish you had done right now?"


def _generate_summoned_whisper(context: MuseContext, topic: str) -> str:
    """Generate whisper when explicitly summoned."""
    if topic:
        return (
            f"About {topic}: sometimes the best path forward is the one you haven't considered yet."
        )
    else:
        return "You called? I see the patterns in your work. What would you like to explore?"


# =============================================================================
# Polynomial Construction
# =============================================================================


class MusePolynomial:
    """
    The Muse polynomial agent.

    Uses MuseContext as composite state, tracking arc, tension, and history.
    """

    def __init__(self) -> None:
        self.name = "MusePolynomial"

    @property
    def positions(self) -> FrozenSet[MuseState]:
        """Muse states are the primary positions."""
        return frozenset(MuseState)

    def directions(self, context: MuseContext) -> FrozenSet[type]:
        """Valid inputs at this state."""
        return muse_directions(context)

    def transition(self, context: MuseContext, input: MuseInput) -> tuple[MuseContext, MuseOutput]:
        """Execute state transition."""
        return muse_transition(context, input)

    def invoke(self, context: MuseContext, input: MuseInput) -> tuple[MuseContext, MuseOutput]:
        """Invoke the polynomial (alias for transition)."""
        return self.transition(context, input)


# Global polynomial instance
MUSE_POLYNOMIAL = MusePolynomial()


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # States
    "MuseState",
    "MuseContext",
    # Events
    "CrystalObserved",
    "ArcShift",
    "TensionRising",
    "ActivityPause",
    # Commands
    "WhisperAccepted",
    "WhisperDismissed",
    "RequestEncouragement",
    "RequestReframe",
    "SummonMuse",
    "DormancyComplete",
    # Outputs
    "MuseWhisper",
    "MuseSilence",
    "MuseOutput",
    # Polynomial
    "MusePolynomial",
    "MUSE_POLYNOMIAL",
    "muse_transition",
    "muse_directions",
]
