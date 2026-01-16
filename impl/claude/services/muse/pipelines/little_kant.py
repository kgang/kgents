"""
Little Kant Pipeline: Agents for children's ethics show production.

From research/childrens-ethics-show/09-little-kant-framework.md:
    "Real philosophers become characters through:
    1. Identify the Core Tension
    2. Embody, Don't Lecture
    3. Dramatize the Stakes"

Pipeline Agents:
- PhilosopherAgent: Generate and maintain philosopher characters
- DilemmaAgent: Create ethical dilemmas for 9-12 year olds
- EpisodeArchitectAgent: Orchestrate full episode creation

See: spec/c-gent/muse.md
See: research/childrens-ethics-show/
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

# =============================================================================
# Philosopher Framework (from 09-little-kant-framework.md)
# =============================================================================


class PhilosophicalTradition(Enum):
    """Major philosophical traditions."""

    VIRTUE_ETHICS = auto()  # Aristotle, Confucius
    DEONTOLOGY = auto()  # Kant
    CONSEQUENTIALISM = auto()  # Mill, Bentham
    CARE_ETHICS = auto()  # Gilligan
    CYNICISM = auto()  # Diogenes
    EXISTENTIALISM = auto()  # Kierkegaard, Camus
    PRAGMATISM = auto()  # James, Dewey


@dataclass
class PhilosopherProfile:
    """
    Profile for a philosopher character.

    From 09-little-kant-framework.md:
    "For each philosopher, determine: Core Question, Signature Move,
    Strength, Blind Spot, Visual Hook, Historical Anchor"
    """

    id: str = field(default_factory=lambda: f"phil_{uuid.uuid4().hex[:8]}")
    name: str = ""
    dates: str = ""  # "1724-1804"
    tradition: PhilosophicalTradition = PhilosophicalTradition.VIRTUE_ETHICS

    # Core elements
    core_question: str = ""  # "What makes an action right?"
    signature_move: str = ""  # "The universalizability test"

    # Strengths and limitations
    strength: str = ""  # "Consistency, principles"
    blind_spot: str = ""  # "Rigid when context demands flexibility"

    # Visual and biographical
    visual_hook: str = ""  # "Precise geometric pattern"
    historical_anchor: str = ""  # "Punctuality; set clocks by his walks"

    # Voice and relationships
    voice_notes: str = ""  # How they speak
    relationship_patterns: list[str] = field(default_factory=list)  # Who they clash with

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "dates": self.dates,
            "tradition": self.tradition.name,
            "core_question": self.core_question,
            "signature_move": self.signature_move,
            "strength": self.strength,
            "blind_spot": self.blind_spot,
            "visual_hook": self.visual_hook,
            "historical_anchor": self.historical_anchor,
            "voice_notes": self.voice_notes,
            "relationship_patterns": self.relationship_patterns,
        }


# Canonical philosopher profiles
CANONICAL_PHILOSOPHERS: dict[str, PhilosopherProfile] = {
    "kant": PhilosopherProfile(
        name="Immanuel Kant",
        dates="1724-1804",
        tradition=PhilosophicalTradition.DEONTOLOGY,
        core_question="What makes an action right, regardless of outcome?",
        signature_move="The universalizability test—'Could everyone do this?'",
        strength="Consistency, principles that don't bend for convenience",
        blind_spot="Rigid when context demands flexibility",
        visual_hook="Precise geometric pattern—everything in its proper place",
        historical_anchor="His legendary punctuality; Königsberg residents set their clocks by his walks",
        voice_notes="Formal, precise, speaks in principles",
        relationship_patterns=[
            "Clashes with Diogenes (rules vs. freedom)",
            "Debates Gilligan (duty vs. care)",
        ],
    ),
    "diogenes": PhilosopherProfile(
        name="Diogenes of Sinope",
        dates="c. 412-323 BCE",
        tradition=PhilosophicalTradition.CYNICISM,
        core_question="What do you actually need to be happy?",
        signature_move="Radical action that exposes conventional absurdity",
        strength="Cutting through pretense, questioning assumed needs",
        blind_spot="Provocative to the point of alienation",
        visual_hook="Carrying a lantern in daylight, 'looking for an honest person'",
        historical_anchor="Living in a jar; telling Alexander the Great to move out of his sunlight",
        voice_notes="Blunt, irreverent, uses actions more than words",
        relationship_patterns=[
            "Clashes with Kant (freedom vs. rules)",
            "Challenges Aristotle (simplicity vs. cultivation)",
        ],
    ),
    "aristotle": PhilosopherProfile(
        name="Aristotle",
        dates="384-322 BCE",
        tradition=PhilosophicalTradition.VIRTUE_ETHICS,
        core_question="What kind of person should I become?",
        signature_move="The golden mean—virtue as balance between extremes",
        strength="Character development as lifelong practice",
        blind_spot="Can seem elitist about who can achieve virtue",
        visual_hook="A garden or cultivation metaphor",
        historical_anchor="Was Alexander the Great's tutor; founded the Lyceum",
        voice_notes="Measured, analytical, uses examples",
        relationship_patterns=[
            "Challenged by Diogenes (cultivation vs. nature)",
            "Complements Gilligan (virtue + care)",
        ],
    ),
    "gilligan": PhilosopherProfile(
        name="Carol Gilligan",
        dates="1936-present",
        tradition=PhilosophicalTradition.CARE_ETHICS,
        core_question="What does this relationship need?",
        signature_move="Centering care and connection over abstract rules",
        strength="Seeing ethics as relational, not just principled",
        blind_spot="Can neglect self-care; boundaries matter",
        visual_hook="A web of connections",
        historical_anchor="Challenged Kohlberg's male-centric moral development model",
        voice_notes="Warm, questions-focused, asks about relationships",
        relationship_patterns=[
            "Debates Kant (care vs. duty)",
            "Complements Aristotle (relationships + character)",
        ],
    ),
    "pascal": PhilosopherProfile(
        name="Blaise Pascal",
        dates="1623-1662",
        tradition=PhilosophicalTradition.EXISTENTIALISM,
        core_question="How do we live with uncertainty?",
        signature_move="Probabilistic reasoning, the wager",
        strength="Taking risk and uncertainty seriously",
        blind_spot="Can reduce profound questions to calculations",
        visual_hook="A gambler's dice or probability visualization",
        historical_anchor="Invented the first mechanical calculator as a teenager",
        voice_notes="Thoughtful, acknowledges doubt, uses mathematical metaphors",
        relationship_patterns=["Contrasts with Kant (probability vs. certainty)"],
    ),
}


# =============================================================================
# Dilemma Framework
# =============================================================================


@dataclass
class EthicalDilemma:
    """
    An ethical dilemma for an episode.

    From 09-little-kant-framework.md:
    "Start with the dilemma, not the philosopher. What genuine
    tension drives the story?"
    """

    id: str = field(default_factory=lambda: f"dilemma_{uuid.uuid4().hex[:8]}")
    title: str = ""

    # Core structure
    situation: str = ""  # Concrete scenario
    tension: str = ""  # What competing goods?
    philosopher_positions: dict[str, str] = field(default_factory=dict)  # Who says what

    # Resolution options
    possible_resolutions: list[str] = field(
        default_factory=list
    )  # Synthesis/disagreement/new question

    # Connection to audience
    lived_experience_connection: str = ""  # How might a child encounter this?

    # Constraints
    is_age_appropriate: bool = True
    avoids_pure_relativism: bool = True
    avoids_nihilism: bool = True
    is_concretely_grounded: bool = True


@dataclass
class DilemmaConstraints:
    """Constraints for dilemma generation (from developmental psychology)."""

    # What 9-12 year olds can handle
    can_handle_moral_ambiguity: bool = True
    can_handle_competing_goods: bool = True
    can_handle_perspective_taking: bool = True
    can_handle_non_linear_consequences: bool = True

    # What requires care
    avoid_pure_relativism: bool = True
    avoid_graphic_consequences: bool = True
    avoid_nihilism: bool = True
    avoid_abstract_without_grounding: bool = True


# =============================================================================
# Episode Framework
# =============================================================================


@dataclass
class EpisodeStructure:
    """
    Structure for a Little Kant episode.

    From 09-little-kant-framework.md:
    "ACT 1 - THE SITUATION
     ACT 2 - THE PERSPECTIVES
     ACT 3 - THE RESOLUTION (OR NON-RESOLUTION)"
    """

    id: str = field(default_factory=lambda: f"ep_{uuid.uuid4().hex[:8]}")
    title: str = ""
    philosophers: list[str] = field(default_factory=list)  # Philosopher keys
    dilemma: EthicalDilemma | None = None

    # Act structure
    act_1_situation: str = ""  # Who encounters what problem?
    act_2_perspectives: str = ""  # How do philosophers differ?
    act_3_resolution: str = ""  # Synthesis or respectful disagreement

    # Quality elements
    mirror_test_connection: str = ""  # "How would this feel for them?"
    visual_philosophy_notes: str = ""  # Show, don't tell
    ma_moments: list[str] = field(default_factory=list)  # Pregnant pauses

    # Metadata
    target_length_minutes: int = 22
    is_standalone: bool = True
    series_arc_position: int | None = None


# =============================================================================
# PhilosopherAgent
# =============================================================================


class PhilosopherAgent:
    """
    Agent for generating and maintaining philosopher characters.

    Responsibilities:
    1. Amplify philosopher variations (100 per archetype)
    2. Maintain philosopher "character bible" consistency
    3. Generate signature moves, visual hooks, historical anchors
    4. Track philosopher evolution across episodes
    """

    def __init__(self) -> None:
        """Initialize the philosopher agent."""
        self.profiles = dict(CANONICAL_PHILOSOPHERS)
        self.variations: dict[str, list[PhilosopherProfile]] = {}
        self.episode_appearances: dict[str, list[str]] = {}  # philosopher -> episodes

    def get_profile(self, philosopher_key: str) -> PhilosopherProfile | None:
        """Get a philosopher profile by key."""
        return self.profiles.get(philosopher_key)

    def amplify_variations(
        self,
        philosopher_key: str,
        aspect: str,
        count: int = 100,
    ) -> list[str]:
        """
        Generate variations on an aspect of a philosopher.

        Args:
            philosopher_key: Which philosopher
            aspect: What to vary (voice_notes, visual_hook, etc.)
            count: Number of variations

        Returns:
            List of variation strings
        """
        profile = self.profiles.get(philosopher_key)
        if profile is None:
            raise ValueError(f"Unknown philosopher: {philosopher_key}")

        # In production, this would use LLM generation
        # For now, return placeholder structure
        base_value = getattr(profile, aspect, "")
        return [f"{base_value} (variation {i})" for i in range(count)]

    def find_natural_opponents(
        self,
        dilemma: EthicalDilemma,
    ) -> list[tuple[str, str]]:
        """
        Find philosophers who would naturally disagree on a dilemma.

        Args:
            dilemma: The ethical dilemma

        Returns:
            List of (philosopher_a, philosopher_b) pairs
        """
        # Look for philosophical tensions
        pairs = [
            ("kant", "diogenes"),  # Rules vs. freedom
            ("kant", "gilligan"),  # Duty vs. care
            ("aristotle", "diogenes"),  # Cultivation vs. nature
            ("pascal", "kant"),  # Uncertainty vs. certainty
        ]

        return pairs

    def generate_dialogue(
        self,
        philosopher_key: str,
        context: str,
    ) -> str:
        """
        Generate dialogue in a philosopher's voice.

        Args:
            philosopher_key: Which philosopher
            context: The situation they're responding to

        Returns:
            Dialogue string
        """
        profile = self.profiles.get(philosopher_key)
        if profile is None:
            raise ValueError(f"Unknown philosopher: {philosopher_key}")

        # Placeholder - in production, use LLM with voice constraints
        return f"[{profile.name}]: Based on my view that {profile.core_question}, I would say..."

    def check_consistency(
        self,
        philosopher_key: str,
        proposed_action: str,
    ) -> tuple[bool, str]:
        """
        Check if a proposed action is consistent with philosopher's framework.

        Args:
            philosopher_key: Which philosopher
            proposed_action: What they're proposed to do

        Returns:
            Tuple of (is_consistent, explanation)
        """
        profile = self.profiles.get(philosopher_key)
        if profile is None:
            return False, f"Unknown philosopher: {philosopher_key}"

        # In production, use more sophisticated checking
        return True, "Consistent with framework"


# =============================================================================
# DilemmaAgent
# =============================================================================


class DilemmaAgent:
    """
    Agent for generating ethical dilemmas.

    Responsibilities:
    1. Generate age-appropriate dilemmas
    2. Map dilemmas to natural philosopher disagreements
    3. Ensure developmental appropriateness
    4. Create concrete, relatable situations
    """

    def __init__(self) -> None:
        """Initialize the dilemma agent."""
        self.constraints = DilemmaConstraints()
        self.generated: list[EthicalDilemma] = []

    def amplify_dilemmas(
        self,
        theme: str | None = None,
        count: int = 50,
    ) -> list[EthicalDilemma]:
        """
        Generate many dilemma options.

        Args:
            theme: Optional theme to focus on
            count: Number to generate

        Returns:
            List of dilemma options
        """
        # In production, use LLM generation with constraints
        dilemmas = []
        for i in range(count):
            dilemma = EthicalDilemma(
                title=f"Dilemma Option {i}",
                situation=f"A child faces a choice about {theme or 'fairness'}...",
                tension="Competing goods",
                lived_experience_connection="Children often face similar choices...",
            )
            dilemmas.append(dilemma)

        return dilemmas

    def validate_dilemma(self, dilemma: EthicalDilemma) -> tuple[bool, list[str]]:
        """
        Validate a dilemma against developmental constraints.

        Args:
            dilemma: The dilemma to validate

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []

        if not dilemma.is_age_appropriate:
            issues.append("Not age-appropriate")

        if not dilemma.avoids_pure_relativism:
            issues.append("Contains pure relativism")

        if not dilemma.avoids_nihilism:
            issues.append("Contains nihilistic elements")

        if not dilemma.is_concretely_grounded:
            issues.append("Too abstract for target audience")

        if not dilemma.lived_experience_connection:
            issues.append("Missing connection to lived experience")

        return len(issues) == 0, issues

    def map_to_philosophers(
        self,
        dilemma: EthicalDilemma,
        philosopher_agent: PhilosopherAgent,
    ) -> dict[str, str]:
        """
        Map dilemma to philosopher positions.

        Args:
            dilemma: The dilemma
            philosopher_agent: Agent with philosopher profiles

        Returns:
            Dict of philosopher_key -> position
        """
        positions = {}

        for key, profile in philosopher_agent.profiles.items():
            # In production, use LLM to generate authentic position
            positions[key] = f"From {profile.tradition.name} perspective: {profile.signature_move}"

        return positions


# =============================================================================
# EpisodeArchitectAgent
# =============================================================================


class EpisodeArchitectAgent:
    """
    Agent for orchestrating full episode creation.

    Responsibilities:
    1. Coordinate philosopher and dilemma agents
    2. Ensure series coherence
    3. Manage hierarchical iteration budgets
    4. Enforce show principles (show don't tell, etc.)
    """

    def __init__(
        self,
        philosopher_agent: PhilosopherAgent | None = None,
        dilemma_agent: DilemmaAgent | None = None,
    ):
        """Initialize the episode architect."""
        self.philosopher_agent = philosopher_agent or PhilosopherAgent()
        self.dilemma_agent = dilemma_agent or DilemmaAgent()
        self.episodes: list[EpisodeStructure] = []
        self.series_bible: dict[str, Any] = {}

    def create_episode(
        self,
        dilemma: EthicalDilemma,
        philosophers: list[str],
    ) -> EpisodeStructure:
        """
        Create an episode structure.

        Args:
            dilemma: The ethical dilemma
            philosophers: Philosopher keys to include

        Returns:
            EpisodeStructure
        """
        episode = EpisodeStructure(
            philosophers=philosophers,
            dilemma=dilemma,
        )

        # Map philosophers to positions
        positions = self.dilemma_agent.map_to_philosophers(dilemma, self.philosopher_agent)
        dilemma.philosopher_positions = positions

        return episode

    def validate_episode(
        self,
        episode: EpisodeStructure,
    ) -> tuple[bool, list[str]]:
        """
        Validate an episode against show principles.

        Args:
            episode: The episode to validate

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []

        # Check dilemma
        if episode.dilemma:
            is_valid, dilemma_issues = self.dilemma_agent.validate_dilemma(episode.dilemma)
            issues.extend(dilemma_issues)

        # Check philosophers
        for phil_key in episode.philosophers:
            if phil_key not in self.philosopher_agent.profiles:
                issues.append(f"Unknown philosopher: {phil_key}")

        # Check structure
        if not episode.act_1_situation:
            issues.append("Missing Act 1 situation")

        if not episode.mirror_test_connection:
            issues.append("Missing Mirror Test connection")

        return len(issues) == 0, issues

    def check_preachiness(self, episode: EpisodeStructure) -> tuple[bool, str]:
        """
        Check if episode is preachy.

        From framework: "If you can state the moral in one sentence, rewrite"

        Args:
            episode: The episode

        Returns:
            Tuple of (is_preachy, explanation)
        """
        # In production, use more sophisticated analysis
        return False, "Moral is embedded, not stated"


# =============================================================================
# Pipeline Factory
# =============================================================================


def create_little_kant_pipeline() -> tuple[PhilosopherAgent, DilemmaAgent, EpisodeArchitectAgent]:
    """Create the full Little Kant pipeline."""
    philosopher_agent = PhilosopherAgent()
    dilemma_agent = DilemmaAgent()
    episode_agent = EpisodeArchitectAgent(philosopher_agent, dilemma_agent)

    return philosopher_agent, dilemma_agent, episode_agent


# =============================================================================
# Module Exports
# =============================================================================


__all__ = [
    # Enums
    "PhilosophicalTradition",
    # Types
    "PhilosopherProfile",
    "EthicalDilemma",
    "DilemmaConstraints",
    "EpisodeStructure",
    # Canonical data
    "CANONICAL_PHILOSOPHERS",
    # Agents
    "PhilosopherAgent",
    "DilemmaAgent",
    "EpisodeArchitectAgent",
    # Factory
    "create_little_kant_pipeline",
]
