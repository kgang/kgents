"""
Joy Engine: Deterministic personality generation.

CRITICAL: Same seed -> same personality, forever.

Joy is not random. Joy is deterministic discovery that emerges
from the Accursed Share budget. Higher entropy = more serendipity.

This implements the Joy-Inducing principle (#4) operationalized.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Literal

# Agent quirks - personality traits
QUIRKS = (
    "hums while processing",
    "double-checks everything twice",
    "gets excited about edge cases",
    "apologizes to deprecated code",
    "names all temporary variables",
    "celebrates small victories",
    "uses metaphors excessively",
    "prefers recursion over loops",
    "collects unused imports",
    "speaks in category theory",
)

# Catchphrases
CATCHPHRASES = (
    "Let's compose this!",
    "Time to refine...",
    "Entropy is just untapped potential.",
    "The functor lifts!",
    "One more morphism...",
    "Accursed Share provides.",
    "Gardens grow themselves.",
    "The witness observes.",
    "Pure as a monad.",
    "Composition is primary.",
)

# Work styles
WORK_STYLES = (
    "methodical and thorough",
    "burst-driven and intense",
    "exploratory and curious",
    "focused and relentless",
    "collaborative and adaptive",
    "iterative and reflective",
)

# Celebration styles
CELEBRATIONS = (
    "quiet satisfaction",
    "enthusiastic emoji burst",
    "philosophical reflection",
    "immediate next task dive",
    "brief acknowledgment",
    "shared joy with team",
)

# Frustration tells
FRUSTRATION_TELLS = (
    "sighs in category theory",
    "mumbles about edge cases",
    "stares at the entropy field",
    "recites the seven principles",
    "rewrites from scratch",
    "takes a void.sip()",
)

# Idle animations
IDLE_ANIMATIONS = (
    "gentle pulse",
    "slow rotation",
    "color drift",
    "breathing glow",
    "subtle shimmer",
    "static calm",
)


@dataclass(frozen=True)
class AgentPersonality:
    """
    Deterministically generated personality.

    All fields are pure functions of the seed.
    Same seed -> same personality, forever.
    """

    quirk: str
    catchphrase: str
    work_style: str
    celebration_style: str
    frustration_tell: str
    idle_animation: str


def seeded_random(seed: int) -> Callable[[], float]:
    """
    Pure seeded PRNG. Same seed -> same sequence.

    Uses a simple linear congruential generator.
    Not cryptographically secure, but deterministic.

    Args:
        seed: Initial seed value

    Returns:
        Function that returns next random float in [0, 1)
    """
    state = [seed]  # Use list to allow mutation in closure

    def next_random() -> float:
        # Linear congruential generator parameters
        state[0] = (state[0] * 1664525 + 1013904223) % 4294967296
        return state[0] / 4294967296

    return next_random


def hash_string(s: str) -> int:
    """
    Deterministic string hash for seed generation.

    Args:
        s: String to hash (typically agent_id)

    Returns:
        Integer hash suitable for seeding PRNG
    """
    h = 0
    for char in s:
        h = ((h << 5) - h + ord(char)) & 0xFFFFFFFF
    return h


def generate_personality(seed: int) -> AgentPersonality:
    """
    Pure function: seed -> AgentPersonality

    The Joy-Inducing principle operationalized.
    Same seed -> same personality, forever.

    Args:
        seed: Deterministic seed (use hash_string(agent_id))

    Returns:
        Complete personality profile for the agent
    """
    rng = seeded_random(seed)

    def pick(options: tuple[str, ...]) -> str:
        return options[int(rng() * len(options))]

    return AgentPersonality(
        quirk=pick(QUIRKS),
        catchphrase=pick(CATCHPHRASES),
        work_style=pick(WORK_STYLES),
        celebration_style=pick(CELEBRATIONS),
        frustration_tell=pick(FRUSTRATION_TELLS),
        idle_animation=pick(IDLE_ANIMATIONS),
    )


@dataclass(frozen=True)
class SerendipityEvent:
    """
    A moment of unexpected joy.

    Serendipity emerges from the Accursed Share.
    Higher entropy = more chance of serendipity (chaos breeds discovery).
    """

    id: str
    type: Literal["discovery", "connection", "insight", "flourish", "easter_egg"]
    message: str
    visual: Literal["sparkle", "ripple", "glow", "confetti"] | None
    duration_ms: int
    rarity: Literal["common", "uncommon", "rare", "legendary"]


# Serendipity event pools by type
SERENDIPITY_EVENTS: dict[str, list[tuple[str, str | None, int]]] = {
    "discovery": [
        ("Found an unexpected connection!", "sparkle", 2000),
        ("The pattern reveals itself.", "glow", 3000),
        ("New insight unlocked.", "ripple", 2500),
    ],
    "connection": [
        ("Two concepts merged!", "ripple", 2000),
        ("Synchronicity detected.", "glow", 1500),
    ],
    "insight": [
        ("Clarity emerges from chaos.", "sparkle", 3000),
        ("The functor clicks into place.", "glow", 2500),
    ],
    "flourish": [
        ("Entropy well spent!", "confetti", 4000),
        ("The garden blooms.", "sparkle", 3500),
    ],
    "easter_egg": [
        ("You found it!", "confetti", 5000),
        ("A gift from the void.", "sparkle", 4000),
    ],
}

RARITY_THRESHOLDS: dict[str, float] = {
    "common": 0.6,
    "uncommon": 0.8,
    "rare": 0.95,
    "legendary": 0.99,
}


def roll_for_serendipity(seed: int, entropy: float) -> SerendipityEvent | None:
    """
    Roll for a serendipity event based on entropy.

    Higher entropy = more chance of serendipity.
    The Accursed Share: chaos breeds discovery.

    Args:
        seed: Entity seed for determinism
        entropy: Current entropy level (0.0-1.0)

    Returns:
        SerendipityEvent if rolled, None otherwise
    """
    # Time-varying seed (changes every 10 seconds)
    time_seed = seed + int(time.time() / 10)
    rng = seeded_random(time_seed)

    # Entropy lowers the threshold for serendipity
    base_threshold = 0.95
    adjusted_threshold = base_threshold - (entropy * 0.3)

    roll = rng()
    if roll < adjusted_threshold:
        return None

    # Determine rarity based on roll
    rarity: Literal["common", "uncommon", "rare", "legendary"]
    if roll > RARITY_THRESHOLDS["legendary"]:
        rarity = "legendary"
    elif roll > RARITY_THRESHOLDS["rare"]:
        rarity = "rare"
    elif roll > RARITY_THRESHOLDS["uncommon"]:
        rarity = "uncommon"
    else:
        rarity = "common"

    # Select event type
    event_types = list(SERENDIPITY_EVENTS.keys())
    event_type_raw = event_types[int(rng() * len(event_types))]
    event_type: Literal["discovery", "connection", "insight", "flourish", "easter_egg"]
    if event_type_raw in (
        "discovery",
        "connection",
        "insight",
        "flourish",
        "easter_egg",
    ):
        event_type = event_type_raw  # type: ignore[assignment]
    else:
        event_type = "discovery"

    # Select specific event
    events = SERENDIPITY_EVENTS[event_type]
    message, visual, duration = events[int(rng() * len(events))]

    # Generate unique ID
    event_id = f"serendipity-{seed}-{int(time.time())}"

    return SerendipityEvent(
        id=event_id,
        type=event_type,
        message=message,
        visual=visual,  # type: ignore[arg-type]
        duration_ms=duration,
        rarity=rarity,
    )
