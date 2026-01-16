"""
Muse Core Models: Foundation types for the Co-Creative Engine.

The Creative Muse Protocol (C-gent) operationalizes breakthrough creativity through:
- The 30-50 Iteration Principle: No creative work ships before 30 iterations
- The Volume Principle: Generate 50 options before selecting one
- The Dialectical Engine: Amplify → Select → Contradict → Defend/Pivot → Repeat
- The Externalized Mirror Test: Kent's taste as computable function

From muse.md:
    "The goal is not AI-assisted creativity. The goal is Kent-at-10x—daring, bold,
    opinionated—with AI as the amplifier, contradictor, and relentless taste-enforcer."

See: spec/c-gent/muse.md
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum, auto
from typing import Any, FrozenSet, Generic, TypeVar

# =============================================================================
# Type Variables
# =============================================================================

T = TypeVar("T")  # Generic work type
S = TypeVar("S")  # State type


# =============================================================================
# AI Roles (The Five Co-Creative Roles)
# =============================================================================


class AIRole(Enum):
    """
    The five AI roles in co-creation.

    From muse.md:
    - AMPLIFIER: Generates volume (50 options per cycle)
    - CONTRADICTOR: Challenges choices to crystallize conviction
    - MEMORY: Maintains context and patterns across sessions
    - CRITIC: Applies externalized taste (Mirror Test)
    - GENERATOR: Produces raw creative material
    """

    AMPLIFIER = auto()  # Generates 50 options
    CONTRADICTOR = auto()  # Challenges selections
    MEMORY = auto()  # Tracks patterns and ghosts
    CRITIC = auto()  # Applies taste vector
    GENERATOR = auto()  # Produces creative output


# =============================================================================
# Resonance Levels (Mirror Test Outcomes)
# =============================================================================


class ResonanceLevel(IntEnum):
    """
    Levels of resonance with Kent's taste.

    From muse.md:
    - DISSONANT: "This isn't me at all"
    - FOREIGN: "I can see merit but wouldn't make this choice"
    - RESONANT: "Yes, this feels right"
    - PROFOUND: "This is me on my best day"

    Escape velocity is achieved at PROFOUND.
    """

    DISSONANT = 0  # "This isn't me at all"
    FOREIGN = 1  # "I can see merit but wouldn't make this choice"
    RESONANT = 2  # "Yes, this feels right"
    PROFOUND = 3  # "This is me on my best day" - escape velocity

    @property
    def emoji(self) -> str:
        """Visual indicator."""
        return {
            ResonanceLevel.DISSONANT: "💔",
            ResonanceLevel.FOREIGN: "🤔",
            ResonanceLevel.RESONANT: "✨",
            ResonanceLevel.PROFOUND: "🚀",
        }[self]

    @property
    def description(self) -> str:
        """Human-readable description."""
        return {
            ResonanceLevel.DISSONANT: "This isn't me at all",
            ResonanceLevel.FOREIGN: "I can see merit but wouldn't make this choice",
            ResonanceLevel.RESONANT: "Yes, this feels right",
            ResonanceLevel.PROFOUND: "This is me on my best day",
        }[self]


# =============================================================================
# Taste Vector (Externalized Aesthetic Preferences)
# =============================================================================


@dataclass
class TasteVector:
    """
    Kent's externalized taste as a computable structure.

    From muse.md:
    "Kent's taste is not ineffable. It can be captured, refined,
    and applied algorithmically."

    Dimensions (0.0-1.0):
    - darkness: Preference for shadow vs. light
    - complexity: Preference for layered vs. simple
    - warmth: Preference for intimate vs. distant
    - energy: Preference for kinetic vs. still
    - novelty: Preference for surprising vs. familiar
    - restraint: Preference for restrained vs. maximal
    """

    darkness: float = 0.6  # Preference for shadow (0=light, 1=dark)
    complexity: float = 0.7  # Layered depth (0=simple, 1=complex)
    warmth: float = 0.5  # Emotional temperature (0=cold, 1=warm)
    energy: float = 0.4  # Kinetic quality (0=still, 1=kinetic)
    novelty: float = 0.7  # Surprise factor (0=familiar, 1=novel)
    restraint: float = 0.6  # Elegance (0=maximal, 1=restrained)

    # Explicit never/always preferences
    never: tuple[str, ...] = ()  # Hard rejections
    always: tuple[str, ...] = ()  # Required elements

    def distance(self, other: TasteVector) -> float:
        """Euclidean distance between taste vectors."""
        return (
            (self.darkness - other.darkness) ** 2
            + (self.complexity - other.complexity) ** 2
            + (self.warmth - other.warmth) ** 2
            + (self.energy - other.energy) ** 2
            + (self.novelty - other.novelty) ** 2
            + (self.restraint - other.restraint) ** 2
        ) ** 0.5

    def drift_from(self, baseline: TasteVector) -> float:
        """Measure drift from historical baseline."""
        return self.distance(baseline)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage."""
        return {
            "darkness": self.darkness,
            "complexity": self.complexity,
            "warmth": self.warmth,
            "energy": self.energy,
            "novelty": self.novelty,
            "restraint": self.restraint,
            "never": self.never,
            "always": self.always,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TasteVector:
        """Deserialize from storage."""
        return cls(
            darkness=data.get("darkness", 0.5),
            complexity=data.get("complexity", 0.5),
            warmth=data.get("warmth", 0.5),
            energy=data.get("energy", 0.5),
            novelty=data.get("novelty", 0.5),
            restraint=data.get("restraint", 0.5),
            never=tuple(data.get("never", [])),
            always=tuple(data.get("always", [])),
        )


# Kent's default taste (from voice anchors)
KENT_TASTE_DEFAULT = TasteVector(
    darkness=0.6,
    complexity=0.7,
    warmth=0.5,
    energy=0.4,
    novelty=0.7,
    restraint=0.6,
    never=(
        "gaudy",
        "cliche",
        "pandering",
        "safe",
        "committee-designed",
    ),
    always=(
        "daring",
        "bold",
        "opinionated",
        "tasteful",
    ),
)


# =============================================================================
# Creative Options and Ghosts
# =============================================================================


def generate_option_id() -> str:
    """Generate unique option ID."""
    return f"opt_{uuid.uuid4().hex[:12]}"


def generate_ghost_id() -> str:
    """Generate unique ghost ID."""
    return f"ghost_{uuid.uuid4().hex[:12]}"


@dataclass
class CreativeOption(Generic[T]):
    """
    A generated creative option.

    Options are produced by amplification (50 per cycle).
    Only one is selected; the rest become ghosts.
    """

    id: str = field(default_factory=generate_option_id)
    content: T | None = None  # The actual creative content
    description: str = ""  # Human-readable summary
    ai_reasoning: str = ""  # Why AI generated this
    estimated_taste: TasteVector | None = None  # Predicted taste alignment
    novelty_score: float = 0.5  # How surprising (0-1)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage."""
        return {
            "id": self.id,
            "description": self.description,
            "ai_reasoning": self.ai_reasoning,
            "estimated_taste": self.estimated_taste.to_dict() if self.estimated_taste else None,
            "novelty_score": self.novelty_score,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Ghost(Generic[T]):
    """
    A rejected creative option (the path not taken).

    From muse-part-iii.md:
    "With 50 options generated per cycle and only 1 selected, we produce
    49 ghosts per iteration. Over 30-50 iterations, that's 1,500-2,500
    ghosts per session."

    Ghosts are the negative space that defines the work.
    """

    id: str = field(default_factory=generate_ghost_id)
    original_option: CreativeOption[T] | None = None
    rejection_reason: str = ""  # Why Kent rejected
    rejection_strength: float = 0.5  # How strongly (0=mild, 1=visceral)
    ai_championed: bool = False  # Did AI advocate for this?
    surprise_at_rejection: float = 0.5  # AI's surprise at rejection (0-1)
    iteration: int = 0  # When this was rejected
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def worth_resurrecting(self) -> bool:
        """Should this ghost be reconsidered?"""
        # High AI surprise + mild rejection = worth another look
        return self.surprise_at_rejection > 0.7 and self.rejection_strength < 0.3

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage."""
        return {
            "id": self.id,
            "original_option_id": self.original_option.id if self.original_option else None,
            "rejection_reason": self.rejection_reason,
            "rejection_strength": self.rejection_strength,
            "ai_championed": self.ai_championed,
            "surprise_at_rejection": self.surprise_at_rejection,
            "iteration": self.iteration,
            "timestamp": self.timestamp.isoformat(),
        }


# =============================================================================
# Contradiction (The Dialectical Challenge)
# =============================================================================


class ContradictionMove(Enum):
    """
    Types of productive contradiction.

    From muse.md, AI uses these moves:
    - OPPOSITE: "You want dark. What if light?"
    - ABSENCE: "You want a hook. What if no hook?"
    - PRIOR_KENT: "Last time you rejected this. What changed?"
    - AUDIENCE: "Your audience expects X. You're giving Y."
    - SPECIFICITY: "You said 'melancholy.' What KIND?"
    """

    OPPOSITE = auto()  # Direct inversion
    ABSENCE = auto()  # Remove the element entirely
    PRIOR_KENT = auto()  # Cite historical contradiction
    AUDIENCE = auto()  # Challenge audience expectations
    SPECIFICITY = auto()  # Demand greater precision


@dataclass
class Contradiction:
    """
    A challenge to a creative choice.

    The dialectical engine:
    1. Kent selects from options
    2. AI contradicts the selection
    3. Kent defends (conviction crystallizes) or pivots (discovers better)
    """

    id: str = field(default_factory=lambda: f"contra_{uuid.uuid4().hex[:8]}")
    move: ContradictionMove = ContradictionMove.OPPOSITE
    challenge: str = ""  # The challenge text
    target: str = ""  # What's being challenged
    evidence: str = ""  # Supporting evidence for challenge
    strength: float = 0.5  # How forceful (0=gentle, 1=aggressive)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DefenseResponse:
    """
    Kent's response to a contradiction.

    Either DEFEND (conviction crystallizes) or PIVOT (discover better).
    """

    defended: bool = True  # True=defend, False=pivot
    reasoning: str = ""  # Why defend or pivot
    conviction_strength: float = 0.5  # How strongly held (0-1)
    new_direction: str | None = None  # If pivoted, what's the new direction
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# Iteration Milestones
# =============================================================================


ITERATION_MILESTONES: dict[int, str] = {
    1: "Zeroth draft: capture the spark",
    10: "Foundation review: is this worth 40 more iterations?",
    20: "Clarity review: can a stranger understand this?",
    30: "Minimum viable: could ship (but shouldn't)",
    40: "Excellence review: this is GOOD. Is it GREAT?",
    50: "Escape velocity: undeniably itself. Ship it.",
}


# =============================================================================
# Session State
# =============================================================================


class SessionPhase(Enum):
    """
    Phases of a co-creative session.

    From muse.md:
    1. GROUND: What are we making? What's the constraint?
    2. SPARK: Kent provides initial direction
    3. SPIRAL: Diverge-converge cycles until escape velocity
    4. CRYSTALLIZE: Lock in the breakthrough
    5. WITNESS: Record what worked
    """

    GROUND = auto()  # Establishing constraints
    SPARK = auto()  # Initial direction
    SPIRAL = auto()  # Iterative diverge-converge
    CRYSTALLIZE = auto()  # Locking in the work
    WITNESS = auto()  # Recording the session


@dataclass
class SessionState(Generic[T]):
    """
    State of a co-creative session.

    Tracks iterations, ghosts, taste evolution, and escape velocity.
    """

    id: str = field(default_factory=lambda: f"session_{uuid.uuid4().hex[:8]}")
    phase: SessionPhase = SessionPhase.GROUND

    # The work being created
    current: T | None = None
    spark: str = ""  # Initial creative direction

    # Iteration tracking
    iteration: int = 0
    target_iterations: int = 50

    # Ghost collection
    ghosts: list[Ghost[T]] = field(default_factory=list)

    # Taste tracking
    taste: TasteVector = field(default_factory=lambda: KENT_TASTE_DEFAULT)
    selections: list[tuple[int, str]] = field(default_factory=list)  # (iteration, selection_id)

    # Contradiction tracking
    contradictions: list[Contradiction] = field(default_factory=list)
    defenses: list[DefenseResponse] = field(default_factory=list)

    # Resonance history
    resonance_history: list[tuple[int, ResonanceLevel]] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def escape_velocity_reached(self) -> bool:
        """Has the work achieved escape velocity?"""
        if not self.resonance_history:
            return False
        # Need PROFOUND resonance at recent iteration
        recent = [r for i, r in self.resonance_history if i >= self.iteration - 5]
        return any(r >= ResonanceLevel.PROFOUND for r in recent)

    @property
    def minimum_iterations_met(self) -> bool:
        """Have we reached the minimum iteration threshold?"""
        return self.iteration >= 30

    @property
    def can_ship(self) -> bool:
        """Can this work be shipped?"""
        return self.minimum_iterations_met and self.escape_velocity_reached

    def add_ghost(self, ghost: Ghost[T]) -> None:
        """Add a ghost to the collection."""
        ghost.iteration = self.iteration
        self.ghosts.append(ghost)

    def add_resonance(self, level: ResonanceLevel) -> None:
        """Record a resonance measurement."""
        self.resonance_history.append((self.iteration, level))
        self.updated_at = datetime.now()

    def advance_iteration(self) -> str:
        """Advance to next iteration, return milestone if any."""
        self.iteration += 1
        self.updated_at = datetime.now()
        return ITERATION_MILESTONES.get(self.iteration, "")


# =============================================================================
# Volume Targets (Domain-Specific)
# =============================================================================


VOLUME_TARGETS: dict[str, int] = {
    # Core creative (30-50 options)
    "song_hook": 100,  # Hooks need massive exploration
    "verse_lyrics": 50,
    "melody_phrase": 50,
    "album_title": 30,
    # Visual (20-30 options)
    "youtube_thumbnail": 30,
    "character_design": 30,
    "color_palette": 20,
    # Narrative (40-60 options)
    "episode_concept": 50,
    "dialogue_line": 40,
    "scene_structure": 30,
    "philosopher_trait": 100,  # Deep character exploration
    # Technical (10-20 options)
    "api_endpoint": 10,
    "test_case": 20,
}


# =============================================================================
# Module Exports
# =============================================================================


__all__ = [
    # Enums
    "AIRole",
    "ResonanceLevel",
    "ContradictionMove",
    "SessionPhase",
    # Core types
    "TasteVector",
    "KENT_TASTE_DEFAULT",
    "CreativeOption",
    "Ghost",
    "Contradiction",
    "DefenseResponse",
    "SessionState",
    # ID generators
    "generate_option_id",
    "generate_ghost_id",
    # Constants
    "ITERATION_MILESTONES",
    "VOLUME_TARGETS",
]
