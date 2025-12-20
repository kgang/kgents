"""
Rumination: The Soul's Internal Life.

K-gent Phase 2: Ambient presence through autonomous event generation.

Rumination generates ambient events without external prompting:
- THOUGHT: Internal monologue triggered by time or pattern
- FEELING: Affective state shifts based on soul state
- OBSERVATION: Patterns noticed in the environment
- SELF_CHALLENGE: Dialectic self-questioning
- GRATITUDE: Tithe to entropy (Accursed Share)

The rumination generator is the heartbeat of the ambient soul. Instead of
waiting for external events, the soul generates its own internal life.

Architecture:
    ruminate(soul, config) → AsyncIterator[SoulEvent]

Usage:
    from agents.k.rumination import ruminate, RuminationConfig

    async for event in ruminate(soul, config):
        print(f"Ambient: {event.event_type.value}")
"""

from __future__ import annotations

import asyncio
import random
import uuid
from dataclasses import dataclass, field
from datetime import timedelta
from typing import TYPE_CHECKING, Any, AsyncIterator, Optional

from .events import (
    SoulEvent,
    feeling_event,
    gratitude_event,
    observation_event,
    self_challenge_event,
    thought_event,
)

if TYPE_CHECKING:
    from .eigenvectors import KentEigenvectors as Eigenvectors
    from .soul import KgentSoul


# =============================================================================
# Configuration
# =============================================================================


def _clamp_probability(value: float, name: str) -> float:
    """Clamp probability to [0.0, 1.0] with warning."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


@dataclass
class RuminationConfig:
    """Configuration for rumination behavior."""

    # Timing (how often to check for rumination)
    check_interval: timedelta = field(default_factory=lambda: timedelta(seconds=5))

    # Probabilities (per check cycle)
    thought_probability: float = 0.3
    feeling_probability: float = 0.2
    observation_probability: float = 0.15
    challenge_probability: float = 0.1
    gratitude_probability: float = 0.05

    # Depth thresholds
    deep_thought_threshold: float = 0.8  # Random threshold for deep vs surface
    intense_feeling_threshold: float = 0.7

    # Entropy budget (ruminations before rest)
    max_ruminations: int = 100
    rest_after_exhaustion: timedelta = field(default_factory=lambda: timedelta(minutes=5))

    # Eigenvector tension threshold (triggers self-challenge)
    eigenvector_tension_threshold: float = 0.3

    def __post_init__(self) -> None:
        """Validate and clamp probabilities."""
        self.thought_probability = _clamp_probability(self.thought_probability, "thought")
        self.feeling_probability = _clamp_probability(self.feeling_probability, "feeling")
        self.observation_probability = _clamp_probability(
            self.observation_probability, "observation"
        )
        self.challenge_probability = _clamp_probability(self.challenge_probability, "challenge")
        self.gratitude_probability = _clamp_probability(self.gratitude_probability, "gratitude")

        # Ensure max_ruminations is positive
        if self.max_ruminations < 1:
            self.max_ruminations = 1

    @property
    def total_probability(self) -> float:
        """Sum of all event probabilities."""
        return (
            self.thought_probability
            + self.feeling_probability
            + self.observation_probability
            + self.challenge_probability
            + self.gratitude_probability
        )


@dataclass
class RuminationState:
    """Runtime state for rumination."""

    ruminations_count: int = 0
    is_resting: bool = False
    last_thought: Optional[str] = None
    last_feeling: Optional[str] = None
    consecutive_same_type: int = 0
    session_id: str = field(default_factory=lambda: f"rum-{uuid.uuid4().hex[:8]}")


# =============================================================================
# Thought Generation
# =============================================================================

# Thought templates organized by eigenvector
THOUGHT_TEMPLATES: dict[str, list[str]] = {
    "aesthetic": [
        "The elegance of composition...",
        "There's something beautiful about how {pattern} works.",
        "Simplicity is the ultimate sophistication.",
        "Is this implementation as clean as it could be?",
    ],
    "categorical": [
        "Functors preserve structure...",
        "What's the natural transformation here?",
        "If {pattern} is a morphism, what are the objects?",
        "The algebra holds.",
    ],
    "pragmatic": [
        "Does this actually work?",
        "What's the simplest thing that could work?",
        "The user doesn't care about elegance, they care about results.",
        "Ship it.",
    ],
    "playful": [
        "What if we tried something weird?",
        "Rules are for discovering, then breaking.",
        "This could be fun...",
        "Let's see what happens.",
    ],
    "principled": [
        "What would be the ethical choice here?",
        "Does this augment or replace human judgment?",
        "The principles say...",
        "Intent matters as much as outcome.",
    ],
    "heterarchical": [
        "Sometimes leading, sometimes following...",
        "Who's the right agent for this task?",
        "Collaboration over control.",
        "The hierarchy isn't fixed.",
    ],
}

OBSERVATION_PATTERNS: list[str] = [
    "The tests are passing more often lately.",
    "There's a pattern in how errors cluster.",
    "The codebase is growing in a particular direction.",
    "Something shifted in the recent interactions.",
    "The functor composition is getting smoother.",
    "There's tension between pragmatism and elegance.",
]

GRATITUDE_TARGETS: list[str] = [
    "the categorical foundations",
    "the test suite that catches errors",
    "the entropy that enables change",
    "the composability of the design",
    "the time to think deeply",
    "the privilege of working on meaningful problems",
]


def generate_thought(
    eigenvectors: "Eigenvectors",
    recent_pattern: Optional[str] = None,
) -> tuple[str, int, Optional[str]]:
    """
    Generate a thought based on eigenvector weights.

    Returns:
        (content, depth, triggered_by)

    Handles edge cases:
    - Empty or zero-weight eigenvectors → falls back to "pragmatic"
    - Missing template keys → uses pragmatic fallback
    """
    # Weight selection by eigenvector strength
    try:
        weights = eigenvectors.to_dict()
    except (AttributeError, TypeError):
        # Fallback if eigenvectors is malformed
        weights = {}

    # Filter out non-positive weights
    weights = {k: v for k, v in weights.items() if v > 0}

    # Pick eigenvector weighted by strength
    total = sum(weights.values()) if weights else 0.0
    if total <= 0:
        dominant = "pragmatic"
    else:
        r = random.random() * total
        cumulative = 0.0
        dominant = "pragmatic"
        for name, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                dominant = name
                break

    # Get templates for this eigenvector (with fallback)
    templates = THOUGHT_TEMPLATES.get(dominant, THOUGHT_TEMPLATES["pragmatic"])
    if not templates:
        templates = THOUGHT_TEMPLATES["pragmatic"]
    template = random.choice(templates)

    # Substitute pattern if present (handle missing format keys gracefully)
    try:
        content = template.format(pattern=recent_pattern or "the system")
    except KeyError:
        content = template  # Use template as-is if format fails

    # Depth based on probability (1=surface, 3=deep)
    depth = 3 if random.random() > 0.7 else 1

    triggered_by = f"eigenvector:{dominant}" if random.random() > 0.5 else None

    return content, depth, triggered_by


def _clamp_intensity(value: float) -> float:
    """Clamp intensity to [0.0, 1.0]."""
    return max(0.0, min(1.0, value))


def generate_feeling(
    eigenvectors: "Eigenvectors",
    recent_events_count: int,
) -> tuple[str, float, Optional[str]]:
    """
    Generate a feeling based on soul state.

    Returns:
        (valence, intensity, cause)

    Intensity is always clamped to [0.0, 1.0].
    """
    # Ensure non-negative count
    recent_events_count = max(0, recent_events_count)

    # Feelings based on activity level and eigenvector balance
    if recent_events_count > 10:
        valences = ["engaged", "focused", "energized"]
        intensity = _clamp_intensity(0.4 + recent_events_count * 0.05)
        cause = "high activity"
    elif recent_events_count == 0:
        valences = ["contemplative", "serene", "curious"]
        intensity = 0.3
        cause = "quiet moment"
    else:
        valences = ["curious", "attentive", "open"]
        intensity = 0.5
        cause = None

    valence = random.choice(valences)
    return valence, intensity, cause


def generate_observation() -> tuple[str, float, str]:
    """
    Generate an observation.

    Returns:
        (pattern, confidence, domain)
    """
    pattern = random.choice(OBSERVATION_PATTERNS)
    confidence = 0.4 + random.random() * 0.4  # 0.4 to 0.8
    domain = "general"
    return pattern, confidence, domain


def generate_self_challenge(
    eigenvectors: "Eigenvectors",
) -> tuple[str, str, Optional[str], str]:
    """
    Generate a self-challenge based on eigenvector tension.

    Returns:
        (thesis, antithesis, synthesis, eigenvector)
    """
    challenges = [
        (
            "Composability is paramount",
            "But sometimes direct solutions are clearer",
            "Compose for architecture, be direct for implementation",
            "categorical",
        ),
        (
            "Elegance matters",
            "But shipping matters more",
            "Elegant code ships faster in the long run",
            "aesthetic",
        ),
        (
            "Principles should be followed",
            "But context changes everything",
            "Principles guide, context decides",
            "principled",
        ),
        (
            "Play enables discovery",
            "But deadlines are real",
            "Schedule time for play, protect time for delivery",
            "playful",
        ),
        (
            "Lead when you have vision",
            "Follow when others have expertise",
            "The role depends on the situation",
            "heterarchical",
        ),
    ]

    thesis, antithesis, synthesis_raw, eigenvector = random.choice(challenges)
    synthesis: Optional[str] = synthesis_raw

    # Sometimes leave synthesis unresolved
    if random.random() > 0.6:
        synthesis = None

    return thesis, antithesis, synthesis, eigenvector


def generate_gratitude() -> tuple[str, Optional[str], int]:
    """
    Generate a gratitude expression.

    Returns:
        (for_what, to_whom, depth)
    """
    for_what = random.choice(GRATITUDE_TARGETS)
    to_whom = "the system" if random.random() > 0.7 else None
    depth = 3 if random.random() > 0.8 else 1
    return for_what, to_whom, depth


# =============================================================================
# The Rumination Generator
# =============================================================================


async def ruminate(
    soul: "KgentSoul",
    config: Optional[RuminationConfig] = None,
) -> AsyncIterator[SoulEvent]:
    """
    Generate ambient events from the soul's internal life.

    This async generator yields THOUGHT, FEELING, OBSERVATION,
    SELF_CHALLENGE, and GRATITUDE events based on probabilistic
    triggers and soul state.

    Args:
        soul: The KgentSoul to ruminate on
        config: Optional configuration

    Yields:
        Ambient SoulEvents

    Handles:
        - CancelledError: Graceful shutdown
        - Soul state errors: Continues with defaults
    """
    cfg = config or RuminationConfig()
    state = RuminationState()

    try:
        while True:
            # Rest if exhausted
            if state.ruminations_count >= cfg.max_ruminations:
                state.is_resting = True
                await asyncio.sleep(cfg.rest_after_exhaustion.total_seconds())
                state.ruminations_count = 0
                state.is_resting = False
                continue

            # Wait for next check (cancellable)
            await asyncio.sleep(cfg.check_interval.total_seconds())

            # Get current soul state (with fallback)
            try:
                soul_state = soul.manifest()
                eigenvectors = soul_state.eigenvectors
                interactions_count = soul_state.interactions_count
            except (AttributeError, TypeError):
                # Fallback if soul is in unexpected state
                from .eigenvectors import KentEigenvectors

                eigenvectors = KentEigenvectors()
                interactions_count = 0

            # Roll for each event type
            event: Optional[SoulEvent] = None

            r = random.random()

            if r < cfg.thought_probability:
                content, depth, triggered_by = generate_thought(eigenvectors)
                event = thought_event(
                    content=content,
                    depth=depth,
                    triggered_by=triggered_by,
                    correlation_id=f"{state.session_id}-thought-{state.ruminations_count}",
                )

            elif r < cfg.thought_probability + cfg.feeling_probability:
                valence, intensity, cause = generate_feeling(
                    eigenvectors,
                    interactions_count,
                )
                event = feeling_event(
                    valence=valence,
                    intensity=intensity,
                    cause=cause,
                    correlation_id=f"{state.session_id}-feeling-{state.ruminations_count}",
                )

            elif (
                r < cfg.thought_probability + cfg.feeling_probability + cfg.observation_probability
            ):
                pattern, confidence, domain = generate_observation()
                event = observation_event(
                    pattern=pattern,
                    confidence=confidence,
                    domain=domain,
                    correlation_id=f"{state.session_id}-obs-{state.ruminations_count}",
                )

            elif (
                r
                < cfg.thought_probability
                + cfg.feeling_probability
                + cfg.observation_probability
                + cfg.challenge_probability
            ):
                thesis, antithesis, synthesis, eigenvector = generate_self_challenge(eigenvectors)
                event = self_challenge_event(
                    thesis=thesis,
                    antithesis=antithesis,
                    synthesis=synthesis,
                    eigenvector=eigenvector,
                    correlation_id=f"{state.session_id}-challenge-{state.ruminations_count}",
                )

            elif (
                r
                < cfg.thought_probability
                + cfg.feeling_probability
                + cfg.observation_probability
                + cfg.challenge_probability
                + cfg.gratitude_probability
            ):
                for_what, to_whom, depth = generate_gratitude()
                event = gratitude_event(
                    for_what=for_what,
                    to_whom=to_whom,
                    depth=depth,
                    correlation_id=f"{state.session_id}-gratitude-{state.ruminations_count}",
                )

            # Yield if we generated something
            if event is not None:
                state.ruminations_count += 1
                yield event

    except asyncio.CancelledError:
        # Graceful shutdown - don't propagate, just stop
        return


async def quick_rumination(
    soul: "KgentSoul",
    count: int = 5,
) -> AsyncIterator[SoulEvent]:
    """
    Generate a fixed number of ruminations quickly (for testing).

    This is a convenience for tests that need deterministic behavior.
    """
    config = RuminationConfig(
        check_interval=timedelta(milliseconds=10),
        thought_probability=0.4,
        feeling_probability=0.3,
        observation_probability=0.15,
        challenge_probability=0.1,
        gratitude_probability=0.05,
    )

    generated = 0
    async for event in ruminate(soul, config):
        yield event
        generated += 1
        if generated >= count:
            break


# =============================================================================
# Synergy: Pulse Bridge (K-gent → D-gent Vitality)
# =============================================================================


def soul_to_pulse(
    soul: "KgentSoul",
    phase: str = "thinking",
    recent_content: str = "",
) -> dict[str, Any]:
    """
    Convert KgentSoul state to D-gent Pulse-compatible format.

    This enables VitalityAnalyzer from agents.d.pulse to track K-gent's health.

    Args:
        soul: The KgentSoul to extract state from
        phase: Current phase (thinking/acting/waiting/yielding/crystallizing)
        recent_content: Recent content for hash generation (loop detection)

    Returns:
        Dict compatible with agents.d.pulse.Pulse.from_dict()

    Usage:
        from agents.d.pulse import Pulse, VitalityAnalyzer

        pulse_data = soul_to_pulse(soul, "thinking", last_response)
        pulse = Pulse.from_dict(pulse_data)
        status = analyzer.ingest(pulse)
    """
    import hashlib
    from datetime import UTC, datetime

    try:
        state = soul.manifest()
        interactions_count = state.interactions_count
        mode = state.active_mode.value
    except (AttributeError, TypeError):
        interactions_count = 0
        mode = "reflect"

    # Estimate pressure as ratio of interactions to typical session (100)
    pressure = min(1.0, interactions_count / 100.0)

    # Generate content hash for loop detection
    content_hash = hashlib.md5(recent_content.encode()).hexdigest()[:8]

    return {
        "agent": "k-gent",
        "timestamp": datetime.now(UTC).isoformat(),
        "pressure": pressure,
        "phase": phase,
        "content_hash": content_hash,
        "turn_count": interactions_count,
        "metadata": {
            "mode": mode,
            "source": "rumination",
        },
    }


def rumination_to_crystal_task(
    events: list["SoulEvent"],
    description: str = "Rumination session",
) -> dict[str, Any]:
    """
    Convert rumination events to D-gent TaskState format for crystallization.

    This enables StateCrystal from agents.d.crystal to persist K-gent's ruminations.

    Args:
        events: List of SoulEvents from rumination
        description: Task description

    Returns:
        Dict compatible with agents.d.crystal.TaskState.from_dict()

    Usage:
        from agents.d.crystal import TaskState, create_task_state

        task_data = rumination_to_crystal_task(events, "Morning rumination")
        task = TaskState.from_dict(task_data)
    """
    from uuid import uuid4

    # Count event types
    thought_count = sum(1 for e in events if e.event_type.value == "thought")
    feeling_count = sum(1 for e in events if e.event_type.value == "feeling")
    observation_count = sum(1 for e in events if e.event_type.value == "observation")
    challenge_count = sum(1 for e in events if e.event_type.value == "self_challenge")
    gratitude_count = sum(1 for e in events if e.event_type.value == "gratitude")

    return {
        "task_id": f"rum_{uuid4().hex[:8]}",
        "description": description,
        "status": "completed",
        "progress": 1.0,
        "metadata": {
            "event_count": len(events),
            "thoughts": thought_count,
            "feelings": feeling_count,
            "observations": observation_count,
            "challenges": challenge_count,
            "gratitude": gratitude_count,
            "source": "rumination",
        },
    }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "RuminationConfig",
    "RuminationState",
    "ruminate",
    "quick_rumination",
    # Synergy: Pulse Bridge
    "soul_to_pulse",
    "rumination_to_crystal_task",
]
