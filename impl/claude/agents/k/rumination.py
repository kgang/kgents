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
from typing import TYPE_CHECKING, AsyncIterator, Optional

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
    rest_after_exhaustion: timedelta = field(
        default_factory=lambda: timedelta(minutes=5)
    )

    # Eigenvector tension threshold (triggers self-challenge)
    eigenvector_tension_threshold: float = 0.3


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
    """
    # Weight selection by eigenvector strength
    weights = eigenvectors.to_dict()

    # Pick eigenvector weighted by strength
    total = sum(weights.values())
    if total == 0:
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

    # Get templates for this eigenvector
    templates = THOUGHT_TEMPLATES.get(dominant, THOUGHT_TEMPLATES["pragmatic"])
    template = random.choice(templates)

    # Substitute pattern if present
    content = template.format(pattern=recent_pattern or "the system")

    # Depth based on probability
    depth = 3 if random.random() > 0.7 else 1

    triggered_by = f"eigenvector:{dominant}" if random.random() > 0.5 else None

    return content, depth, triggered_by


def generate_feeling(
    eigenvectors: "Eigenvectors",
    recent_events_count: int,
) -> tuple[str, float, Optional[str]]:
    """
    Generate a feeling based on soul state.

    Returns:
        (valence, intensity, cause)
    """
    # Feelings based on activity level and eigenvector balance
    if recent_events_count > 10:
        valences = ["engaged", "focused", "energized"]
        intensity = min(0.8, 0.4 + recent_events_count * 0.05)
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
    """
    cfg = config or RuminationConfig()
    state = RuminationState()

    while True:
        # Rest if exhausted
        if state.ruminations_count >= cfg.max_ruminations:
            state.is_resting = True
            await asyncio.sleep(cfg.rest_after_exhaustion.total_seconds())
            state.ruminations_count = 0
            state.is_resting = False
            continue

        # Wait for next check
        await asyncio.sleep(cfg.check_interval.total_seconds())

        # Get current soul state
        soul_state = soul.manifest()
        eigenvectors = soul_state.eigenvectors

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
                soul_state.interactions_count,
            )
            event = feeling_event(
                valence=valence,
                intensity=intensity,
                cause=cause,
                correlation_id=f"{state.session_id}-feeling-{state.ruminations_count}",
            )

        elif (
            r
            < cfg.thought_probability
            + cfg.feeling_probability
            + cfg.observation_probability
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
            thesis, antithesis, synthesis, eigenvector = generate_self_challenge(
                eigenvectors
            )
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
# Exports
# =============================================================================

__all__ = [
    "RuminationConfig",
    "RuminationState",
    "ruminate",
    "quick_rumination",
]
