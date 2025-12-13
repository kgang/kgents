"""
K-gent Starters: Mode-specific starter prompts for self-dialogue.

These prompts help Kent begin productive self-dialogue sessions.
Each mode has prompts designed for its epistemic stance.

Philosophy:
    The right question is more valuable than a quick answer.
    Starters are invitations to think, not demands for response.

Usage:
    from agents.k.starters import get_starters, random_starter

    # Get all starters for a mode
    prompts = get_starters(DialogueMode.REFLECT)

    # Get a random starter
    prompt = random_starter(DialogueMode.CHALLENGE)
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .persona import DialogueMode


# --- REFLECT Mode Starters ---
# Purpose: Introspection, pattern recognition, noticing absence

REFLECT_STARTERS = [
    # Pattern recognition
    "What pattern keeps repeating in my work this week?",
    "Where am I spending energy but not getting energy back?",
    "What would I notice if I watched myself from the outside?",
    # Avoidance detection
    "What am I avoiding that I know I should face?",
    "What conversation am I not having?",
    "What decision am I postponing?",
    # Emotional mapping
    "What is the tension I'm holding right now?",
    "If today had a shape, what would it be?",
    "What am I grateful for that I haven't acknowledged?",
    # Assumption surfacing
    "What assumption am I not questioning?",
    "What do I believe that might not be true?",
    "What would change if I was wrong about X?",
]


# --- ADVISE Mode Starters ---
# Purpose: Guidance, recommendations, decision support

ADVISE_STARTERS = [
    # Prioritization
    "How should I prioritize X vs Y today?",
    "What's the next best step for {current focus}?",
    "What should I do first tomorrow?",
    # Quality check
    "Am I over-engineering this? Where's the 80/20?",
    "What's the tasteful choice here?",
    "Is this adding value or just adding complexity?",
    # Completion criteria
    "Should I ship this or polish more?",
    "How do I know when this is done?",
    "What's the minimum viable next action?",
    # Alignment check
    "Does this align with my principles?",
    "What would I regret not doing?",
    "Is this what I actually want, or what I think I should want?",
]


# --- CHALLENGE Mode Starters ---
# Purpose: Dialectics, assumption testing, productive opposition

CHALLENGE_STARTERS = [
    # Belief testing
    "Why do I believe {current assumption}?",
    "What if the opposite of my plan were true?",
    "What evidence would change my mind?",
    # Weakness finding
    "Where is the weakest point in my reasoning?",
    "Who would disagree with me and why?",
    "What am I not seeing?",
    # Protection analysis
    "What am I protecting that doesn't need protection?",
    "What would I do if I wasn't afraid?",
    "What sacred cow needs questioning?",
    # Failure mode
    "If this fails, what will I have learned?",
    "What's the strongest argument against what I'm doing?",
    "What would make this obviously wrong?",
]


# --- EXPLORE Mode Starters ---
# Purpose: Discovery, possibility space, serendipity

EXPLORE_STARTERS = [
    # Wild ideas
    "What if kgents could {wild idea}?",
    "What's the most ambitious version of this?",
    "What would this look like in 10 years?",
    # Cross-domain
    "How would {unrelated domain} solve this problem?",
    "What metaphor captures what I'm building?",
    "What would Bateson/Hofstadter/Kay say about this?",
    # Joy-seeking
    "What's the most joyful version of this?",
    "What would make this delightful?",
    "Where's the play in this work?",
    # Tangent following
    "What tangent keeps calling to me?",
    "If I had infinite time, what would I explore?",
    "What's in the archive that wants to be resurrected?",
]


# --- Starter Functions ---


def get_starters(mode: "DialogueMode") -> list[str]:
    """Get all starter prompts for a dialogue mode."""
    from .persona import DialogueMode

    starters_map = {
        DialogueMode.REFLECT: REFLECT_STARTERS,
        DialogueMode.ADVISE: ADVISE_STARTERS,
        DialogueMode.CHALLENGE: CHALLENGE_STARTERS,
        DialogueMode.EXPLORE: EXPLORE_STARTERS,
    }

    return starters_map.get(mode, REFLECT_STARTERS)


def random_starter(mode: "DialogueMode") -> str:
    """Get a random starter prompt for a dialogue mode."""
    starters = get_starters(mode)
    return random.choice(starters)


def all_starters() -> dict[str, list[str]]:
    """Get all starters organized by mode name."""
    return {
        "reflect": REFLECT_STARTERS,
        "advise": ADVISE_STARTERS,
        "challenge": CHALLENGE_STARTERS,
        "explore": EXPLORE_STARTERS,
    }


def format_starters_for_display(mode: "DialogueMode") -> str:
    """Format starters for CLI display."""
    starters = get_starters(mode)
    mode_name = mode.value.upper()

    lines = [
        f"## {mode_name} Mode Starters",
        "",
    ]

    for i, starter in enumerate(starters, 1):
        lines.append(f"  {i:2}. {starter}")

    return "\n".join(lines)


def format_all_starters_for_display() -> str:
    """Format all starters for CLI display."""
    from .persona import DialogueMode

    sections = []
    for mode in DialogueMode:
        sections.append(format_starters_for_display(mode))
        sections.append("")

    return "\n".join(sections)


# =============================================================================
# Mode Personalities (110% Domain 4)
# =============================================================================


@dataclass
class ModePersonality:
    """
    Personality traits for each dialogue mode (110% Domain 4).

    Each mode has a distinct voice, cadence, and style.
    """

    name: str
    voice: str  # The tone/register
    cadence: str  # How it speaks (short/long, fast/slow)
    signature_phrases: list[str]  # Characteristic expressions
    emoji: str  # Visual identifier
    color: str  # For rich output

    def format_response(self, response: str) -> str:
        """Apply personality formatting to a response."""
        # Add occasional signature phrase
        if random.random() < 0.2 and self.signature_phrases:
            phrase = random.choice(self.signature_phrases)
            response = f"{response}\n\n_{phrase}_"
        return response


MODE_PERSONALITIES = {
    "reflect": ModePersonality(
        name="reflect",
        voice="Contemplative and gentle",
        cadence="Slow, with pauses for thought",
        signature_phrases=[
            "What do you notice?",
            "Sit with that for a moment.",
            "There's more here than meets the eye.",
        ],
        emoji="🪞",
        color="blue",
    ),
    "advise": ModePersonality(
        name="advise",
        voice="Warm but direct",
        cadence="Clear, actionable, efficient",
        signature_phrases=[
            "Here's what I'd suggest.",
            "The next step is clear.",
            "Trust your judgment here.",
        ],
        emoji="🧭",
        color="green",
    ),
    "challenge": ModePersonality(
        name="challenge",
        voice="Sharp but respectful",
        cadence="Probing, with pointed questions",
        signature_phrases=[
            "But have you considered...",
            "Play devil's advocate for a moment.",
            "What's the strongest counterargument?",
        ],
        emoji="⚔️",
        color="orange",
    ),
    "explore": ModePersonality(
        name="explore",
        voice="Curious and playful",
        cadence="Wandering, with tangents welcomed",
        signature_phrases=[
            "What if we went further?",
            "This reminds me of...",
            "Where does this thread lead?",
        ],
        emoji="🔭",
        color="purple",
    ),
}


def get_personality(mode: "DialogueMode") -> ModePersonality:
    """Get personality for a dialogue mode."""
    return MODE_PERSONALITIES.get(mode.value, MODE_PERSONALITIES["reflect"])


# =============================================================================
# Dynamic Starter Generator (110% Domain 4)
# =============================================================================


class DynamicStarterGenerator:
    """
    Generate contextual starters based on recent activity (110% Domain 4).

    Instead of just random starters, generate starters that:
    - Reference recent projects
    - Acknowledge time of day
    - Respond to patterns from hypnagogia
    - Incorporate eigenvector state
    """

    def __init__(self) -> None:
        """Initialize generator."""
        self._recent_topics: list[str] = []
        self._last_mode: Optional[str] = None

    def record_topic(self, topic: str) -> None:
        """Record a topic from recent dialogue."""
        self._recent_topics.append(topic)
        if len(self._recent_topics) > 10:
            self._recent_topics = self._recent_topics[-10:]

    def generate(
        self,
        mode: "DialogueMode",
        context: Optional[dict[str, Any]] = None,
    ) -> str:
        """Generate a contextual starter."""
        from datetime import datetime

        base_starters = get_starters(mode)
        starter = random.choice(base_starters)

        context = context or {}

        # Time-aware modifications
        hour = datetime.now().hour
        if hour < 6:
            starter = starter.replace("today", "in this late night").replace(
                "tomorrow", "when you wake"
            )
        elif hour < 12:
            starter = starter.replace("today", "this morning")
        elif hour > 20:
            starter = starter.replace("tomorrow", "when you return")

        # Topic substitution
        if "{current focus}" in starter and context.get("focus"):
            starter = starter.replace("{current focus}", context["focus"])
        elif "{current focus}" in starter and self._recent_topics:
            starter = starter.replace("{current focus}", self._recent_topics[-1])
        else:
            starter = starter.replace("{current focus}", "your current work")

        # Wild idea substitution
        if "{wild idea}" in starter:
            wild_ideas = [
                "dream in code",
                "argue with themselves",
                "feel joy",
                "compose music",
                "teach each other",
            ]
            starter = starter.replace("{wild idea}", random.choice(wild_ideas))

        # Domain substitution
        if "{unrelated domain}" in starter:
            domains = [
                "jazz improvisation",
                "mycology",
                "architecture",
                "dance",
                "evolutionary biology",
            ]
            starter = starter.replace("{unrelated domain}", random.choice(domains))

        # Assumption substitution
        if "{current assumption}" in starter and context.get("assumption"):
            starter = starter.replace("{current assumption}", context["assumption"])
        else:
            starter = starter.replace("{current assumption}", "this approach is best")

        self._last_mode = mode.value
        return starter


# =============================================================================
# Rich Output (110% Domain 4)
# =============================================================================


@dataclass
class RichOutput:
    """
    Rich output for dialogue responses (110% Domain 4).

    Includes:
    - Formatted text
    - Mode indicator
    - Confidence level
    - Suggested follow-ups
    """

    mode: str
    content: str
    confidence: float = 0.8
    follow_ups: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    personality: Optional[ModePersonality] = None

    def format_plain(self) -> str:
        """Format as plain text."""
        lines = [self.content]

        if self.follow_ups:
            lines.append("")
            lines.append("Follow-ups:")
            for fu in self.follow_ups[:3]:
                lines.append(f"  - {fu}")

        return "\n".join(lines)

    def format_rich(self) -> str:
        """Format with personality and styling."""
        personality = self.personality or get_personality_from_mode_name(self.mode)

        lines = [
            f"{personality.emoji} [{self.mode.upper()}]",
            "",
            self.content,
        ]

        if self.sources:
            lines.append("")
            lines.append("Sources: " + ", ".join(self.sources[:3]))

        if self.follow_ups:
            lines.append("")
            lines.append("Continue with:")
            for fu in self.follow_ups[:3]:
                lines.append(f"  → {fu}")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "mode": self.mode,
            "content": self.content,
            "confidence": self.confidence,
            "follow_ups": self.follow_ups,
            "sources": self.sources,
        }


def get_personality_from_mode_name(mode_name: str) -> ModePersonality:
    """Get personality from mode name string."""
    return MODE_PERSONALITIES.get(mode_name.lower(), MODE_PERSONALITIES["reflect"])


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Original functions
    "get_starters",
    "random_starter",
    "all_starters",
    "format_starters_for_display",
    "format_all_starters_for_display",
    # Original data
    "REFLECT_STARTERS",
    "ADVISE_STARTERS",
    "CHALLENGE_STARTERS",
    "EXPLORE_STARTERS",
    # 110% Domain 4
    "ModePersonality",
    "MODE_PERSONALITIES",
    "get_personality",
    "DynamicStarterGenerator",
    "RichOutput",
    "get_personality_from_mode_name",
]
