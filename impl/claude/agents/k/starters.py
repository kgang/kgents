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
from typing import TYPE_CHECKING

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
