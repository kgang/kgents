"""
YouTube Pipeline: Agents for YouTube channel content production.

From research/youtube-channel/LAUNCH-RECOMMENDATIONS.md:
    "I learned to ______ with AI" — A developer uses coding agents
    to become things he's not: a musician, a children's show writer,
    a game designer.

Pipeline Agents:
- ConceptAgent: Promise-first video concept generation
- ScriptAgent: 30-50 iteration script development
- ThumbnailAgent: Volume-first visual generation

See: spec/c-gent/muse.md
See: research/youtube-channel/
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

from ..models import CreativeOption, TasteVector

# =============================================================================
# Video Concept Framework
# =============================================================================


class VideoDomain(Enum):
    """Creative domains for video content."""

    CHILDRENS_SHOW = auto()  # "I Learned to Write a Children's Show"
    GAME_MUSIC = auto()  # "I Learned to Compose Game Music"
    BOARD_GAME = auto()  # "I Learned to Design a Board Game"
    PODCAST = auto()  # "I Learned to Produce a Podcast"
    SHORT_FILM = auto()  # "I Learned to Make a Short Film"
    ALBUM = auto()  # "I Learned to Produce an Album"


@dataclass
class VideoPromise:
    """
    The promise that defines a video.

    From muse-part-vi.md:
    "The promise (thumbnail, title, cover, hook) is not packaging—
    it's a CREATIVE CONSTRAINT that focuses generation."
    """

    id: str = field(default_factory=lambda: f"promise_{uuid.uuid4().hex[:8]}")

    # Core promise
    title: str = ""  # "I Learned to Write a Children's Show"
    thumbnail_concept: str = ""  # Visual hook description
    curiosity_gap: str = ""  # What question does this create?

    # Fulfillment
    tangible_output: str = ""  # What will exist at the end?
    fulfillment_test: str = ""  # How do we know promise is kept?

    def to_constraint(self) -> dict[str, str]:
        """Convert promise to creative constraint."""
        return {
            "must_deliver": self.tangible_output,
            "must_answer": self.curiosity_gap,
            "must_feel_like": self.title,
        }


@dataclass
class VideoConcept:
    """
    A video concept following the "I Learned To" formula.

    From LAUNCH-RECOMMENDATIONS.md:
    "The Position: What happens when a developer with no creative
    training uses AI agents to become a musician, writer, game designer?"
    """

    id: str = field(default_factory=lambda: f"concept_{uuid.uuid4().hex[:8]}")
    domain: VideoDomain = VideoDomain.CHILDRENS_SHOW

    # Core concept
    title: str = ""  # "I Learned to _____ with AI"
    creative_domain: str = ""  # The skill being learned
    promise: VideoPromise | None = None

    # Tangible output
    tangible_output: str = ""  # What will exist
    output_description: str = ""  # How to describe it

    # Audience angle
    why_this_works: str = ""  # Emotional resonance
    unique_angle: str = ""  # What makes this different

    # Metadata
    estimated_length_minutes: int = 15
    target_audience: str = "creative-curious developers"


# =============================================================================
# Script Framework
# =============================================================================


@dataclass
class ScriptSection:
    """A section of video script."""

    name: str  # hook, context, thesis, etc.
    content: str = ""
    duration_seconds: int = 0
    iteration_count: int = 0
    is_locked: bool = False


@dataclass
class VideoScript:
    """
    A video script following the 30-50 iteration principle.

    From LAUNCH-RECOMMENDATIONS.md:
    Episode Structure (15-25 minutes):
    1. THE CHALLENGE (1-2 min)
    2. THE PLAN (2-3 min)
    3. THE STRUGGLE (5-8 min)
    4. THE BREAKTHROUGH (3-5 min)
    5. THE OUTPUT (3-5 min)
    6. THE REFLECTION (2-3 min)
    """

    id: str = field(default_factory=lambda: f"script_{uuid.uuid4().hex[:8]}")
    concept: VideoConcept | None = None

    # Script sections
    sections: dict[str, ScriptSection] = field(
        default_factory=lambda: {
            "hook": ScriptSection(name="hook", duration_seconds=30),
            "challenge": ScriptSection(name="challenge", duration_seconds=90),
            "plan": ScriptSection(name="plan", duration_seconds=150),
            "struggle": ScriptSection(name="struggle", duration_seconds=390),
            "breakthrough": ScriptSection(name="breakthrough", duration_seconds=240),
            "output": ScriptSection(name="output", duration_seconds=240),
            "reflection": ScriptSection(name="reflection", duration_seconds=150),
        }
    )

    # Iteration tracking
    total_iterations: int = 0
    current_section: str = "hook"

    @property
    def total_duration_seconds(self) -> int:
        return sum(s.duration_seconds for s in self.sections.values())

    @property
    def total_duration_minutes(self) -> float:
        return self.total_duration_seconds / 60


@dataclass
class ScriptDraft:
    """A draft version of script content."""

    section: str
    content: str
    iteration: int
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# Thumbnail Framework
# =============================================================================


@dataclass
class ThumbnailConcept:
    """
    A thumbnail concept.

    From LAUNCH-RECOMMENDATIONS.md:
    "Template formula:
    [Expressive face] + [Creative output preview] + [Bold text: I LEARNED TO ___]"
    """

    id: str = field(default_factory=lambda: f"thumb_{uuid.uuid4().hex[:8]}")

    # Visual elements
    face_expression: str = ""  # "surprised", "focused", "proud"
    creative_output_preview: str = ""  # What's shown from the output
    bold_text: str = ""  # The text overlay

    # Design elements
    primary_color: str = "#8B5CF6"  # Electric purple
    accent_color: str = "#F97316"  # Warm orange
    composition_notes: str = ""

    # Testing
    click_probability_estimate: float = 0.0
    clarity_score: float = 0.0


# =============================================================================
# ConceptAgent
# =============================================================================


class ConceptAgent:
    """
    Agent for generating video concepts.

    Responsibilities:
    1. Generate concepts using the "I Learned To" formula
    2. Apply promise-first model (promise before content)
    3. Test promise-fulfillment alignment
    4. Ensure tangible output is defined
    """

    def __init__(self) -> None:
        """Initialize the concept agent."""
        self.concepts: list[VideoConcept] = []
        self.domains = list(VideoDomain)

    def amplify_concepts(
        self,
        domain: VideoDomain | None = None,
        count: int = 50,
    ) -> list[VideoConcept]:
        """
        Generate many concept options.

        Args:
            domain: Optional specific domain to focus on
            count: Number of concepts to generate

        Returns:
            List of concept options
        """
        concepts = []
        domains_to_use = [domain] if domain else self.domains

        for i in range(count):
            d = domains_to_use[i % len(domains_to_use)]
            concept = VideoConcept(
                domain=d,
                title=f"I Learned to {d.name.replace('_', ' ').title()} with AI",
                creative_domain=d.name.lower().replace("_", " "),
            )
            concepts.append(concept)

        return concepts

    def create_promise(
        self,
        concept: VideoConcept,
    ) -> VideoPromise:
        """
        Create a promise for a concept.

        The promise is created BEFORE content exists.

        Args:
            concept: The video concept

        Returns:
            VideoPromise
        """
        return VideoPromise(
            title=concept.title,
            thumbnail_concept=f"Kent looking {self._suggest_expression(concept.domain)} + {concept.tangible_output or 'creative output'} preview",
            curiosity_gap=f"Can someone with no {concept.creative_domain} training actually do this?",
            tangible_output=concept.tangible_output,
            fulfillment_test=f"Does the video show a complete {concept.creative_domain} artifact?",
        )

    def validate_promise_fulfillment(
        self,
        promise: VideoPromise,
        script: VideoScript,
    ) -> tuple[bool, list[str]]:
        """
        Validate that script fulfills promise.

        Args:
            promise: The video promise
            script: The script

        Returns:
            Tuple of (is_fulfilled, issues)
        """
        issues = []

        # Check that output section describes the tangible output
        output_section = script.sections.get("output")
        if output_section and promise.tangible_output:
            if promise.tangible_output.lower() not in output_section.content.lower():
                issues.append(f"Output section doesn't clearly present: {promise.tangible_output}")

        # Check that curiosity gap is answered
        if not script.sections.get("reflection"):
            issues.append("Missing reflection section to close curiosity gap")

        return len(issues) == 0, issues

    def _suggest_expression(self, domain: VideoDomain) -> str:
        """Suggest facial expression for thumbnail."""
        expressions = {
            VideoDomain.CHILDRENS_SHOW: "surprised and delighted",
            VideoDomain.GAME_MUSIC: "focused with headphones",
            VideoDomain.BOARD_GAME: "strategic and excited",
            VideoDomain.PODCAST: "thoughtful and engaged",
            VideoDomain.SHORT_FILM: "cinematic and proud",
            VideoDomain.ALBUM: "creative and accomplished",
        }
        return expressions.get(domain, "curious and determined")


# =============================================================================
# ScriptAgent
# =============================================================================


class ScriptAgent:
    """
    Agent for developing video scripts.

    Responsibilities:
    1. Apply 30-50 iteration principle
    2. Track iteration milestones
    3. Maintain voice consistency
    4. Ensure structure completeness
    """

    def __init__(self) -> None:
        """Initialize the script agent."""
        self.scripts: list[VideoScript] = []
        self.drafts: list[ScriptDraft] = []

    def create_script(self, concept: VideoConcept) -> VideoScript:
        """
        Create a new script for a concept.

        Args:
            concept: The video concept

        Returns:
            New VideoScript
        """
        script = VideoScript(concept=concept)
        self.scripts.append(script)
        return script

    def generate_section_options(
        self,
        script: VideoScript,
        section: str,
        count: int = 50,
    ) -> list[str]:
        """
        Generate options for a script section.

        Args:
            script: The script
            section: Which section
            count: Number of options

        Returns:
            List of content options
        """
        # In production, use LLM generation
        if section == "hook":
            return [
                f"I've never {script.concept.creative_domain if script.concept else 'done this'} before. But with AI agents... (v{i})"
                for i in range(count)
            ]

        return [f"Section {section} content option {i}" for i in range(count)]

    def iterate_section(
        self,
        script: VideoScript,
        section: str,
        new_content: str,
    ) -> ScriptDraft:
        """
        Record an iteration on a section.

        Args:
            script: The script
            section: Which section
            new_content: New content

        Returns:
            ScriptDraft
        """
        if section in script.sections:
            script.sections[section].content = new_content
            script.sections[section].iteration_count += 1
            script.total_iterations += 1

        draft = ScriptDraft(
            section=section,
            content=new_content,
            iteration=script.total_iterations,
        )
        self.drafts.append(draft)

        return draft

    def check_voice_consistency(
        self,
        script: VideoScript,
    ) -> tuple[bool, list[str]]:
        """
        Check if script maintains consistent voice.

        Args:
            script: The script to check

        Returns:
            Tuple of (is_consistent, issues)
        """
        issues = []

        # Check for voice markers
        voice_markers = ["I", "my", "I've", "I'm"]  # First person voice
        for name, section in script.sections.items():
            if section.content:
                has_first_person = any(marker in section.content for marker in voice_markers)
                if not has_first_person:
                    issues.append(f"Section '{name}' may lack personal voice")

        return len(issues) == 0, issues

    def get_iteration_status(
        self,
        script: VideoScript,
    ) -> dict[str, Any]:
        """
        Get iteration status for script.

        Args:
            script: The script

        Returns:
            Status dict
        """
        return {
            "total_iterations": script.total_iterations,
            "minimum_met": script.total_iterations >= 30,
            "target_met": script.total_iterations >= 50,
            "section_iterations": {
                name: section.iteration_count for name, section in script.sections.items()
            },
        }


# =============================================================================
# ThumbnailAgent
# =============================================================================


class ThumbnailAgent:
    """
    Agent for generating thumbnail concepts.

    Responsibilities:
    1. Generate 30 thumbnail options
    2. Apply brand consistency
    3. Test click probability
    4. Ensure promise-thumbnail alignment
    """

    def __init__(self) -> None:
        """Initialize the thumbnail agent."""
        self.thumbnails: list[ThumbnailConcept] = []

        # Brand palette from LAUNCH-RECOMMENDATIONS.md
        self.brand_colors = {
            "primary": "#8B5CF6",  # Electric purple
            "accent": "#F97316",  # Warm orange
            "background": "#FAFAFA",  # Off-white
            "text": "#1F2937",  # Charcoal
        }

    def amplify_thumbnails(
        self,
        concept: VideoConcept,
        count: int = 30,
    ) -> list[ThumbnailConcept]:
        """
        Generate thumbnail options.

        Args:
            concept: The video concept
            count: Number to generate (default 30)

        Returns:
            List of thumbnail concepts
        """
        thumbnails = []

        expressions = [
            "surprised",
            "curious",
            "excited",
            "focused",
            "proud",
            "delighted",
            "determined",
            "amazed",
        ]

        for i in range(count):
            expression = expressions[i % len(expressions)]
            thumbnail = ThumbnailConcept(
                face_expression=expression,
                creative_output_preview=concept.tangible_output or "creative output",
                bold_text=concept.title.upper().replace("I LEARNED TO", "").strip(),
                primary_color=self.brand_colors["primary"],
                accent_color=self.brand_colors["accent"],
            )
            thumbnails.append(thumbnail)

        return thumbnails

    def score_thumbnail(
        self,
        thumbnail: ThumbnailConcept,
        promise: VideoPromise,
    ) -> float:
        """
        Score a thumbnail for effectiveness.

        Args:
            thumbnail: The thumbnail to score
            promise: The video promise for alignment check

        Returns:
            Score 0-1
        """
        score = 0.5  # Base score

        # Check alignment with promise
        if promise.thumbnail_concept:
            if thumbnail.face_expression in promise.thumbnail_concept.lower():
                score += 0.2

        # Check clarity
        if thumbnail.bold_text and len(thumbnail.bold_text) < 20:
            score += 0.15  # Clear, short text

        # Check composition
        if thumbnail.creative_output_preview:
            score += 0.15  # Has output preview

        return min(1.0, score)

    def select_top_thumbnails(
        self,
        thumbnails: list[ThumbnailConcept],
        promise: VideoPromise,
        count: int = 3,
    ) -> list[ThumbnailConcept]:
        """
        Select top thumbnails for testing.

        Args:
            thumbnails: All thumbnail options
            promise: Video promise
            count: How many to select

        Returns:
            Top N thumbnails
        """
        scored = [(self.score_thumbnail(t, promise), t) for t in thumbnails]
        scored.sort(key=lambda x: x[0], reverse=True)

        return [t for _, t in scored[:count]]


# =============================================================================
# Pipeline Factory
# =============================================================================


def create_youtube_pipeline() -> tuple[ConceptAgent, ScriptAgent, ThumbnailAgent]:
    """Create the full YouTube pipeline."""
    concept_agent = ConceptAgent()
    script_agent = ScriptAgent()
    thumbnail_agent = ThumbnailAgent()

    return concept_agent, script_agent, thumbnail_agent


# =============================================================================
# Module Exports
# =============================================================================


__all__ = [
    # Enums
    "VideoDomain",
    # Types
    "VideoPromise",
    "VideoConcept",
    "ScriptSection",
    "VideoScript",
    "ScriptDraft",
    "ThumbnailConcept",
    # Agents
    "ConceptAgent",
    "ScriptAgent",
    "ThumbnailAgent",
    # Factory
    "create_youtube_pipeline",
]
