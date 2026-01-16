"""
Muse Checkpoint System: CGP Grey's 66-checkpoint discipline.

From muse-part-vi.md:
    "66 checkpoints is not bureaucracy. It's the difference between
    hoping for quality and guaranteeing it."

Each checkpoint:
1. Asks a specific question
2. Locks a specific element upon passing
3. Uses appropriate co-creative mode (amplify, contradict, mirror)
4. Requires explicit unlock with justification to modify

See: spec/c-gent/muse-part-vi.md
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable

from .models import AIRole, ResonanceLevel

# =============================================================================
# Co-Creative Modes for Checkpoints
# =============================================================================


class CoCreativeMode(Enum):
    """
    The co-creative mode to use at each checkpoint.

    From muse-part-vi.md:
    - AMPLIFY: Generate options for this checkpoint's element
    - CONTRADICT: Challenge the current state
    - MIRROR: Apply externalized Mirror Test
    - NONE: Human-only (no AI involvement)
    """

    AMPLIFY = auto()  # Generate 50 options
    CONTRADICT = auto()  # Challenge the selection
    MIRROR = auto()  # Apply taste/Mirror Test
    NONE = auto()  # Human-only


# =============================================================================
# Checkpoint Definition
# =============================================================================


def generate_checkpoint_id() -> str:
    """Generate unique checkpoint ID."""
    return f"ckpt_{uuid.uuid4().hex[:8]}"


@dataclass(frozen=True)
class Checkpoint:
    """
    A discrete moment where quality is verified and locked.

    From muse-part-vi.md:
    "Each checkpoint: specific question answered, specific quality verified."
    """

    number: int  # Position in sequence
    name: str  # Machine-readable name
    question: str  # What must be answered?
    lock: str  # What gets locked at this point?
    unlock_condition: str = ""  # What allows regression?

    # Quality gates
    must_pass: tuple[str, ...] = ()  # Tests that must pass
    co_creative_mode: CoCreativeMode = CoCreativeMode.AMPLIFY

    # Metadata
    phase: str = ""  # Which production phase

    def __hash__(self) -> int:
        return hash((self.number, self.name))


@dataclass
class CheckpointResult:
    """Result of checkpoint verification."""

    checkpoint: Checkpoint
    passed: bool
    failures: list[str] = field(default_factory=list)
    resonance: ResonanceLevel | None = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LockedElement:
    """
    An element locked after checkpoint passes.

    Once locked, changes require explicit unlock with justification.
    """

    checkpoint: Checkpoint
    content_hash: str  # Hash of locked content
    locked_at: datetime = field(default_factory=datetime.now)
    can_unlock_if: str = ""

    @property
    def is_locked(self) -> bool:
        return True


@dataclass
class UnlockedElement:
    """
    Record of an unlocked element.

    Unlocking triggers re-verification of dependent checkpoints.
    """

    original: LockedElement
    justification: str
    must_repass: list[Checkpoint] = field(default_factory=list)
    unlocked_at: datetime = field(default_factory=datetime.now)


# =============================================================================
# Checkpoint Templates by Domain
# =============================================================================


# YouTube Video Production (48 checkpoints)
YOUTUBE_CHECKPOINTS: tuple[Checkpoint, ...] = (
    # === PHASE 0: CONCEPT (Checkpoints 1-8) ===
    Checkpoint(
        number=1,
        name="spark_capture",
        question="What's the core idea?",
        lock="Topic and angle",
        phase="concept",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=2,
        name="viability_check",
        question="Is this worth making?",
        lock="Go/no-go decision",
        phase="concept",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=3,
        name="promise_draft",
        question="What's the thumbnail/title promise?",
        lock="Core promise (not final execution)",
        phase="concept",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=4,
        name="hook_concept",
        question="How does this open?",
        lock="Opening strategy",
        phase="concept",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=5,
        name="payoff_clarity",
        question="What's the satisfying ending?",
        lock="Payoff concept",
        phase="concept",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=6,
        name="structure_draft",
        question="What are the major beats?",
        lock="Story structure",
        phase="concept",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=7,
        name="surprise_check",
        question="Where's the surprise?",
        lock="Surprise element",
        phase="concept",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=8,
        name="concept_lock",
        question="Is this concept breakthrough-worthy?",
        lock="Full concept",
        phase="concept",
        co_creative_mode=CoCreativeMode.MIRROR,
        must_pass=("concept_clarity", "concept_novelty", "concept_taste"),
    ),
    # === PHASE 1: SCRIPT (Checkpoints 9-20) ===
    Checkpoint(
        number=9,
        name="script_v0",
        question="What's the zeroth draft?",
        lock="Nothing—this is exploratory",
        phase="script",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=10,
        name="hook_script",
        question="First 30 seconds locked?",
        lock="Opening script",
        phase="script",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=11,
        name="value_script",
        question="Core value delivery clear?",
        lock="Main content structure",
        phase="script",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=12,
        name="payoff_script",
        question="Ending earns its emotion?",
        lock="Closing script",
        phase="script",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=13,
        name="flow_check",
        question="Does it flow without friction?",
        lock="Transition points",
        phase="script",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=14,
        name="cut_pass",
        question="What can be cut without loss?",
        lock="Trimmed script",
        phase="script",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=15,
        name="voice_check",
        question="Does every line sound like Kent?",
        lock="Voice consistency",
        phase="script",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=16,
        name="read_aloud",
        question="Does it work spoken?",
        lock="Speakability",
        phase="script",
        co_creative_mode=CoCreativeMode.NONE,
    ),
    Checkpoint(
        number=17,
        name="pattern_interrupts",
        question="Where are the attention resets?",
        lock="Pattern interrupt points",
        phase="script",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=18,
        name="open_loops",
        question="What questions keep viewer watching?",
        lock="Curiosity gaps",
        phase="script",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=19,
        name="no_compromises_script",
        question="Does every line pass the taste test?",
        lock="Script quality",
        phase="script",
        co_creative_mode=CoCreativeMode.MIRROR,
        must_pass=("voice_consistency", "value_delivery", "taste_alignment"),
    ),
    Checkpoint(
        number=20,
        name="script_lock",
        question="Is this script breakthrough-worthy?",
        lock="Final script",
        phase="script",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    # === PHASE 2: PRODUCTION (Checkpoints 21-30) ===
    Checkpoint(
        number=21,
        name="shot_list",
        question="What needs to be captured?",
        lock="Shot requirements",
        phase="production",
        co_creative_mode=CoCreativeMode.NONE,
    ),
    Checkpoint(
        number=22,
        name="b_roll_plan",
        question="What supports the A-roll?",
        lock="B-roll list",
        phase="production",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=23,
        name="location_setup",
        question="Is the environment right?",
        lock="Location",
        phase="production",
        co_creative_mode=CoCreativeMode.NONE,
    ),
    Checkpoint(
        number=24,
        name="performance_prep",
        question="Is Kent ready to deliver?",
        lock="Performance state",
        phase="production",
        co_creative_mode=CoCreativeMode.NONE,
    ),
    Checkpoint(
        number=25,
        name="a_roll_capture",
        question="Is the core performance captured?",
        lock="A-roll footage",
        phase="production",
        co_creative_mode=CoCreativeMode.NONE,
    ),
    Checkpoint(
        number=26,
        name="performance_review",
        question="Does the performance work?",
        lock="Take selection",
        phase="production",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=27,
        name="b_roll_capture",
        question="Is supporting footage captured?",
        lock="B-roll footage",
        phase="production",
        co_creative_mode=CoCreativeMode.NONE,
    ),
    Checkpoint(
        number=28,
        name="audio_quality",
        question="Is audio clean and usable?",
        lock="Audio quality",
        phase="production",
        co_creative_mode=CoCreativeMode.NONE,
    ),
    Checkpoint(
        number=29,
        name="coverage_check",
        question="Do we have everything needed?",
        lock="Complete footage",
        phase="production",
        co_creative_mode=CoCreativeMode.NONE,
    ),
    Checkpoint(
        number=30,
        name="production_lock",
        question="Is production complete?",
        lock="All raw materials",
        phase="production",
        co_creative_mode=CoCreativeMode.NONE,
    ),
    # === PHASE 3: EDIT (Checkpoints 31-40) ===
    Checkpoint(
        number=31,
        name="rough_cut",
        question="Does the structure work?",
        lock="Basic structure",
        phase="edit",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=32,
        name="hook_edit",
        question="Do first 30 seconds command attention?",
        lock="Opening edit",
        phase="edit",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=33,
        name="pacing_pass",
        question="Does pacing maintain engagement?",
        lock="Cut rhythm",
        phase="edit",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=34,
        name="pattern_interrupt_edit",
        question="Are attention resets in place?",
        lock="Visual variety",
        phase="edit",
        co_creative_mode=CoCreativeMode.NONE,
    ),
    Checkpoint(
        number=35,
        name="audio_edit",
        question="Is audio polished?",
        lock="Audio mix",
        phase="edit",
        co_creative_mode=CoCreativeMode.NONE,
    ),
    Checkpoint(
        number=36,
        name="music_pass",
        question="Does music support without distracting?",
        lock="Music selection",
        phase="edit",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=37,
        name="color_pass",
        question="Does color grade support tone?",
        lock="Color grade",
        phase="edit",
        co_creative_mode=CoCreativeMode.NONE,
    ),
    Checkpoint(
        number=38,
        name="graphics_pass",
        question="Do graphics clarify without cluttering?",
        lock="Graphic elements",
        phase="edit",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=39,
        name="final_cut",
        question="Is this the best it can be?",
        lock="Edit",
        phase="edit",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=40,
        name="edit_lock",
        question="Is the edit breakthrough-worthy?",
        lock="Final edit",
        phase="edit",
        co_creative_mode=CoCreativeMode.MIRROR,
        must_pass=("pacing", "visual_quality", "audio_quality", "taste_alignment"),
    ),
    # === PHASE 4: PACKAGE (Checkpoints 41-45) ===
    Checkpoint(
        number=41,
        name="thumbnail_generation",
        question="What are the thumbnail options?",
        lock="Nothing—exploration",
        phase="package",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=42,
        name="thumbnail_selection",
        question="Which thumbnail is strongest?",
        lock="Top 3 thumbnails",
        phase="package",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=43,
        name="title_finalization",
        question="Does title + thumbnail = click?",
        lock="Title",
        phase="package",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=44,
        name="description_seo",
        question="Is description optimized?",
        lock="Description",
        phase="package",
        co_creative_mode=CoCreativeMode.NONE,
    ),
    Checkpoint(
        number=45,
        name="package_lock",
        question="Does package fulfill promise?",
        lock="Complete package",
        phase="package",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    # === PHASE 5: SHIP (Checkpoints 46-48) ===
    Checkpoint(
        number=46,
        name="final_watch",
        question="Does Kent want to watch this?",
        lock="Quality approval",
        phase="ship",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=47,
        name="upload_prep",
        question="Is everything ready for upload?",
        lock="Upload package",
        phase="ship",
        co_creative_mode=CoCreativeMode.NONE,
    ),
    Checkpoint(
        number=48,
        name="ship",
        question="Published?",
        lock="Publication",
        phase="ship",
        co_creative_mode=CoCreativeMode.NONE,
    ),
)


# Little Kant Episode Production (40 checkpoints)
LITTLE_KANT_CHECKPOINTS: tuple[Checkpoint, ...] = (
    # === PHASE 0: CONCEPT (Checkpoints 1-10) ===
    Checkpoint(
        number=1,
        name="dilemma_spark",
        question="What ethical tension drives this episode?",
        lock="Core dilemma",
        phase="concept",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=2,
        name="philosopher_selection",
        question="Which philosophers naturally disagree about this?",
        lock="Philosopher ensemble for episode",
        phase="concept",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=3,
        name="concrete_situation",
        question="What relatable scenario grounds this dilemma?",
        lock="Concrete situation",
        phase="concept",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=4,
        name="child_connection",
        question="How might a 9-12 year old have encountered this?",
        lock="Lived experience connection",
        phase="concept",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=5,
        name="resolution_options",
        question="What are the possible resolutions?",
        lock="Synthesis/disagreement/new question options",
        phase="concept",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=6,
        name="mirror_test_connection",
        question="How does this connect to 'How would this feel for them?'",
        lock="Mirror Test hook",
        phase="concept",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=7,
        name="preachiness_check",
        question="Can you state the moral in one sentence? (If yes, rewrite)",
        lock="Anti-preachiness",
        phase="concept",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=8,
        name="age_appropriateness",
        question="Does this honor 9-12 cognitive capabilities?",
        lock="Developmental appropriateness",
        phase="concept",
        co_creative_mode=CoCreativeMode.CONTRADICT,
        must_pass=("no_pure_relativism", "no_nihilism", "concrete_grounding"),
    ),
    Checkpoint(
        number=9,
        name="series_continuity",
        question="Does this fit the series arc?",
        lock="Series coherence",
        phase="concept",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=10,
        name="concept_lock",
        question="Is this concept breakthrough-worthy?",
        lock="Full episode concept",
        phase="concept",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    # === PHASE 1: SCRIPT (Checkpoints 11-25) ===
    Checkpoint(
        number=11,
        name="act_1_situation",
        question="Who encounters what problem? What are the stakes?",
        lock="Act 1 structure",
        phase="script",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=12,
        name="philosopher_voice_1",
        question="Does Philosopher A embody their framework through action?",
        lock="First philosopher's approach",
        phase="script",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=13,
        name="philosopher_voice_2",
        question="Does Philosopher B embody their framework through action?",
        lock="Second philosopher's approach",
        phase="script",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=14,
        name="conflict_dramatization",
        question="Is the philosophical conflict shown, not told?",
        lock="Framework conflict",
        phase="script",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=15,
        name="act_3_resolution",
        question="Does resolution honor multiple truths?",
        lock="Resolution structure",
        phase="script",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=16,
        name="dialogue_authenticity",
        question="Does each character speak distinctly?",
        lock="Character voices",
        phase="script",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=17,
        name="visual_philosophy",
        question="Are ideas shown through action and image?",
        lock="Visual storytelling",
        phase="script",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=18,
        name="ma_moments",
        question="Are there moments of pregnant pause?",
        lock="Pacing and silence",
        phase="script",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=19,
        name="child_protagonist_agency",
        question="Do children ask questions, not just receive answers?",
        lock="Child agency",
        phase="script",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=20,
        name="adult_competence",
        question="Are adults helpful without being authoritarian or useless?",
        lock="Adult portrayal",
        phase="script",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=21,
        name="no_explicit_moral",
        question="Is the lesson embedded, never stated?",
        lock="Implicit teaching",
        phase="script",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=22,
        name="historical_anchors",
        question="Are philosophers humanized through specific details?",
        lock="Biographical authenticity",
        phase="script",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=23,
        name="discussion_hooks",
        question="Does this generate questions, not closure?",
        lock="Post-viewing discussion potential",
        phase="script",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=24,
        name="script_quality",
        question="Does every scene pass the taste test?",
        lock="Script quality",
        phase="script",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=25,
        name="script_lock",
        question="Is this script breakthrough-worthy?",
        lock="Final script",
        phase="script",
        co_creative_mode=CoCreativeMode.MIRROR,
        must_pass=("philosophy_embodied", "age_appropriate", "anti_preachy", "taste_aligned"),
    ),
    # === PHASE 2: DESIGN (Checkpoints 26-32) ===
    Checkpoint(
        number=26,
        name="visual_hook_integration",
        question="Are philosopher visual hooks present?",
        lock="Visual philosophy motifs",
        phase="design",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=27,
        name="character_consistency",
        question="Do characters match series bible?",
        lock="Character design consistency",
        phase="design",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=28,
        name="threshold_world",
        question="Does the liminal space enable transformation?",
        lock="Setting design",
        phase="design",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=29,
        name="animation_philosophy",
        question="Does animation serve the philosophy?",
        lock="Animation approach",
        phase="design",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=30,
        name="diversity_check",
        question="Is diversity default, not episode?",
        lock="Representation",
        phase="design",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=31,
        name="storyboard",
        question="Does visual sequence serve the story?",
        lock="Storyboard",
        phase="design",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=32,
        name="design_lock",
        question="Is design breakthrough-worthy?",
        lock="Final design package",
        phase="design",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    # === PHASE 3: EDUCATIONAL REVIEW (Checkpoints 33-37) ===
    Checkpoint(
        number=33,
        name="p4c_methodology",
        question="Does structure mirror P4C (stimulus → questions → inquiry)?",
        lock="Educational methodology",
        phase="educational",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=34,
        name="philosopher_accuracy",
        question="Are philosophical positions accurately represented?",
        lock="Philosophical accuracy",
        phase="educational",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=35,
        name="developmental_review",
        question="Does this match 9-12 capabilities per research?",
        lock="Developmental alignment",
        phase="educational",
        co_creative_mode=CoCreativeMode.CONTRADICT,
    ),
    Checkpoint(
        number=36,
        name="companion_materials",
        question="Can discussion guides be generated?",
        lock="Educational extensions",
        phase="educational",
        co_creative_mode=CoCreativeMode.AMPLIFY,
    ),
    Checkpoint(
        number=37,
        name="educational_lock",
        question="Does this meet educational standards?",
        lock="Educational quality",
        phase="educational",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    # === PHASE 4: SHIP (Checkpoints 38-40) ===
    Checkpoint(
        number=38,
        name="final_review",
        question="Does Kent want to show this to a child?",
        lock="Quality approval",
        phase="ship",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=39,
        name="series_integration",
        question="Does this strengthen the series?",
        lock="Series contribution",
        phase="ship",
        co_creative_mode=CoCreativeMode.MIRROR,
    ),
    Checkpoint(
        number=40,
        name="ship",
        question="Ready for production?",
        lock="Episode complete",
        phase="ship",
        co_creative_mode=CoCreativeMode.NONE,
    ),
)


# =============================================================================
# Checkpoint Templates Registry
# =============================================================================


CHECKPOINT_TEMPLATES: dict[str, tuple[Checkpoint, ...]] = {
    "youtube": YOUTUBE_CHECKPOINTS,
    "little_kant": LITTLE_KANT_CHECKPOINTS,
}


def get_checkpoints(domain: str) -> tuple[Checkpoint, ...]:
    """Get checkpoint template for a domain."""
    if domain not in CHECKPOINT_TEMPLATES:
        raise ValueError(
            f"Unknown domain: {domain}. Available: {list(CHECKPOINT_TEMPLATES.keys())}"
        )
    return CHECKPOINT_TEMPLATES[domain]


def get_checkpoint_by_name(domain: str, name: str) -> Checkpoint | None:
    """Get a specific checkpoint by name."""
    checkpoints = get_checkpoints(domain)
    for ckpt in checkpoints:
        if ckpt.name == name:
            return ckpt
    return None


def get_checkpoints_by_phase(domain: str, phase: str) -> tuple[Checkpoint, ...]:
    """Get all checkpoints for a specific phase."""
    checkpoints = get_checkpoints(domain)
    return tuple(ckpt for ckpt in checkpoints if ckpt.phase == phase)


# =============================================================================
# Module Exports
# =============================================================================


__all__ = [
    # Enums
    "CoCreativeMode",
    # Types
    "Checkpoint",
    "CheckpointResult",
    "LockedElement",
    "UnlockedElement",
    # Templates
    "YOUTUBE_CHECKPOINTS",
    "LITTLE_KANT_CHECKPOINTS",
    "CHECKPOINT_TEMPLATES",
    # Functions
    "generate_checkpoint_id",
    "get_checkpoints",
    "get_checkpoint_by_name",
    "get_checkpoints_by_phase",
]
