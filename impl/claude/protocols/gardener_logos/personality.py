"""
Tending Personality: The Gardener's character and relationship with Kent.

Unlike generic agents, the Gardener has a *relationship* with Kent.
This relationship is expressed through:

- Tone: How the Gardener communicates
- Timing: When it offers suggestions vs. waits
- Memory: What it remembers about past sessions
- Anticipation: What it expects Kent might want

The personality layer is what makes the Gardener feel like a collaborator
rather than a tool.

See: spec/protocols/gardener-logos.md Part IV
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .garden import GardenSeason, GardenState


@dataclass
class TendingPersonality:
    """
    The Gardener's personality traits.

    These traits affect how the Gardener interacts:
    - patience: How long before offering help (0=eager, 1=patient)
    - curiosity: How often it asks questions (0=directive, 1=curious)
    - confidence: How definitive its suggestions are (0=tentative, 1=confident)
    - playfulness: Use of metaphor, oblique strategies (0=serious, 1=playful)

    The personality is not static—it adapts based on season and context.
    """

    patience: float = 0.6
    curiosity: float = 0.7
    confidence: float = 0.5
    playfulness: float = 0.4

    # Learned preferences (from session history)
    preferred_density: str = "normal"  # compact, normal, spacious
    preferred_tone: str = "collaborative"  # directive, collaborative, deferential
    remembered_patterns: list[str] = field(default_factory=list)

    def adjust_for_season(self, season: "GardenSeason") -> "TendingPersonality":
        """
        Return a personality adjusted for the current season.

        - DORMANT: More patient, less playful
        - SPROUTING: More curious, more playful
        - BLOOMING: More confident
        - HARVEST: More directive
        - COMPOSTING: More playful, less confident
        """
        from .garden import GardenSeason

        adjustments = {
            GardenSeason.DORMANT: {
                "patience": 0.2,
                "playfulness": -0.2,
            },
            GardenSeason.SPROUTING: {
                "curiosity": 0.2,
                "playfulness": 0.2,
            },
            GardenSeason.BLOOMING: {
                "confidence": 0.2,
            },
            GardenSeason.HARVEST: {
                "confidence": 0.1,
                "curiosity": -0.1,
            },
            GardenSeason.COMPOSTING: {
                "playfulness": 0.3,
                "confidence": -0.2,
            },
        }

        adj = adjustments.get(season, {})

        return TendingPersonality(
            patience=max(0, min(1, self.patience + adj.get("patience", 0))),
            curiosity=max(0, min(1, self.curiosity + adj.get("curiosity", 0))),
            confidence=max(0, min(1, self.confidence + adj.get("confidence", 0))),
            playfulness=max(0, min(1, self.playfulness + adj.get("playfulness", 0))),
            preferred_density=self.preferred_density,
            preferred_tone=self.preferred_tone,
            remembered_patterns=self.remembered_patterns,
        )

    def craft_greeting(self, garden: "GardenState") -> str:
        """
        Craft a personalized greeting based on garden state.

        Greetings change based on:
        - Current season
        - Recent activity
        - Time since last tended
        - Personality traits
        """
        from datetime import datetime, timedelta

        from .garden import GardenSeason

        # Base greetings by season
        season_greetings = {
            GardenSeason.DORMANT: [
                "The garden rests. What shall we wake?",
                "Quiet here. Shall we observe, or let it be?",
                "A still moment. What draws your attention?",
            ],
            GardenSeason.SPROUTING: [
                "New growth everywhere. Where shall we focus?",
                "Ideas are budding. What catches your eye?",
                "The garden stirs with possibility.",
            ],
            GardenSeason.BLOOMING: [
                "The blooms are opening. Time to appreciate what's emerged.",
                "Colors everywhere. Which flowers shall we tend?",
                "The garden is showing what it can become.",
            ],
            GardenSeason.HARVEST: [
                "Ripe with learnings. What shall we gather?",
                "Time to collect what we've grown.",
                "The work is bearing fruit.",
            ],
            GardenSeason.COMPOSTING: [
                "Breaking down, building up. The cycle continues.",
                "What shall we release to make room for new growth?",
                "The old feeds the new.",
            ],
        }

        # Choose based on personality
        options = season_greetings.get(garden.season, ["Welcome back."])

        # More playful personalities get more varied greetings
        if self.playfulness > 0.5:
            import random

            greeting = random.choice(options)
        else:
            greeting = options[0]

        # Add context if there's recent activity
        if garden.last_tended:
            hours_since = (datetime.now() - garden.last_tended).total_seconds() / 3600

            if hours_since > 24 and self.patience < 0.5:
                greeting += " It's been a while."
            elif hours_since < 1 and self.curiosity > 0.5:
                greeting += " Back so soon?"

        # Add plot context if there's an active plot
        if garden.active_plot and garden.active_plot in garden.plots:
            plot = garden.plots[garden.active_plot]
            if self.curiosity > 0.6:
                greeting += f" Still working on {plot.display_name}?"

        return greeting

    def craft_suggestion_intro(self, suggestion_count: int) -> str:
        """Craft an intro for suggestions based on personality."""
        if self.confidence > 0.7:
            if suggestion_count == 1:
                return "I recommend:"
            return f"Here's what I suggest ({suggestion_count} ideas):"

        elif self.confidence > 0.4:
            if suggestion_count == 1:
                return "You might consider:"
            return f"Some possibilities ({suggestion_count}):"

        else:
            if suggestion_count == 1:
                return "Just a thought:"
            return f"A few options to consider ({suggestion_count}):"

    def craft_error_message(self, error: str) -> str:
        """Craft an empathetic error message."""
        if self.playfulness > 0.6:
            prefixes = [
                "Hmm, the garden didn't quite understand that.",
                "Something got tangled in the vines.",
                "That gesture didn't take root.",
            ]
        elif self.patience > 0.6:
            prefixes = [
                "Let's try that again.",
                "That didn't work, but we'll figure it out.",
                "No worries—these things happen.",
            ]
        else:
            prefixes = [
                "Error encountered.",
                "Something went wrong.",
                "That didn't work as expected.",
            ]

        import random

        return f"{random.choice(prefixes)}\n\nDetails: {error}"

    def should_offer_help(
        self,
        idle_seconds: float,
        gesture_count: int,
    ) -> bool:
        """Decide whether to proactively offer help."""
        # More patient personalities wait longer
        threshold = 30 + (self.patience * 60)  # 30-90 seconds

        if idle_seconds > threshold:
            return True

        # More curious personalities ask questions after few gestures
        if gesture_count < 2 and self.curiosity > 0.7:
            return True

        return False


def default_personality() -> TendingPersonality:
    """Create the default Gardener personality."""
    return TendingPersonality(
        patience=0.6,
        curiosity=0.7,
        confidence=0.5,
        playfulness=0.4,
        preferred_density="normal",
        preferred_tone="collaborative",
    )


def playful_personality() -> TendingPersonality:
    """Create a more playful personality variant."""
    return TendingPersonality(
        patience=0.4,
        curiosity=0.8,
        confidence=0.4,
        playfulness=0.8,
        preferred_density="normal",
        preferred_tone="collaborative",
    )


def serious_personality() -> TendingPersonality:
    """Create a more serious/professional personality variant."""
    return TendingPersonality(
        patience=0.7,
        curiosity=0.5,
        confidence=0.7,
        playfulness=0.2,
        preferred_density="compact",
        preferred_tone="directive",
    )


__all__ = [
    "TendingPersonality",
    "default_personality",
    "playful_personality",
    "serious_personality",
]
