"""
Morning Coffee Types: Core data structures for the liminal transition ritual.

This module defines the categorical foundation for Morning Coffee:
- CoffeeState: Polynomial positions (DORMANT → GARDEN → WEATHER → MENU → CAPTURE → TRANSITION)
- ChallengeLevel: Menu challenge gradients with properties (Pattern 2: Enum Property)
- Movement: Ritual phase metadata
- GardenView: Yesterday's changes and growth
- ConceptualWeather: What's shifting in the codebase
- ChallengeMenu: Invitations grouped by valence
- MorningVoice: Fresh capture of authentic morning state

All types are frozen dataclasses for immutability.

See: spec/services/morning-coffee.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum, auto
from typing import Any

# =============================================================================
# State Machine (Polynomial Positions)
# =============================================================================


class CoffeeState(Enum):
    """
    Positions in the Morning Coffee polynomial.

    The ritual flows: DORMANT → GARDEN → WEATHER → MENU → CAPTURE → TRANSITION

    Key insight: Every movement is skippable. If inspiration strikes during
    Garden View, honor it. The ritual serves the human, not vice versa.
    """

    DORMANT = auto()  # Not in ritual
    GARDEN = auto()  # Movement 1: Observing what grew
    WEATHER = auto()  # Movement 2: Understanding shifts
    MENU = auto()  # Movement 3: Choosing challenge
    CAPTURE = auto()  # Movement 4: Recording voice
    TRANSITION = auto()  # Bridging to work


# =============================================================================
# Challenge Gradients (Pattern 2: Enum Property)
# =============================================================================


class ChallengeLevel(Enum):
    """
    Challenge gradients for the Menu.

    The Menu presents invitations, not assignments. Kent chooses based
    on how he feels *right now*.

    Pattern 2 (Enum Property): Metadata co-located with enum values.
    """

    GENTLE = "gentle"  # Warmup, low stakes
    FOCUSED = "focused"  # Clear objective, moderate depth
    INTENSE = "intense"  # Deep work, high cognitive load
    SERENDIPITOUS = "serendipitous"  # Follow curiosity

    @property
    def emoji(self) -> str:
        """Visual indicator for the challenge level."""
        return {
            ChallengeLevel.GENTLE: "🧘",
            ChallengeLevel.FOCUSED: "🎯",
            ChallengeLevel.INTENSE: "🔥",
            ChallengeLevel.SERENDIPITOUS: "🎲",
        }[self]

    @property
    def description(self) -> str:
        """Human-readable description."""
        return {
            ChallengeLevel.GENTLE: "Warmup, low stakes",
            ChallengeLevel.FOCUSED: "Clear objective, moderate depth",
            ChallengeLevel.INTENSE: "Deep work, high cognitive load",
            ChallengeLevel.SERENDIPITOUS: "Follow curiosity",
        }[self]

    @property
    def cognitive_load(self) -> float:
        """Estimated cognitive load (0.0-1.0)."""
        return {
            ChallengeLevel.GENTLE: 0.2,
            ChallengeLevel.FOCUSED: 0.5,
            ChallengeLevel.INTENSE: 0.9,
            ChallengeLevel.SERENDIPITOUS: 0.4,  # Variable but typically moderate
        }[self]


# =============================================================================
# Movement Structure
# =============================================================================


@dataclass(frozen=True)
class Movement:
    """
    A phase of the Morning Coffee ritual.

    Each movement has a distinct character:
    - Garden and Weather are non-demanding (observation only)
    - Menu and Capture require input
    - All movements are skippable
    """

    name: str
    prompt: str  # What is asked
    duration_hint: str  # "~2 min", "~5 min"
    requires_input: bool  # False = observation, True = interaction
    skippable: bool = True  # Always true, but explicit

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "prompt": self.prompt,
            "duration_hint": self.duration_hint,
            "requires_input": self.requires_input,
            "skippable": self.skippable,
        }


# The four movements
MOVEMENTS: dict[str, Movement] = {
    "garden": Movement(
        name="Garden View",
        prompt="What grew while I slept?",
        duration_hint="~2 min",
        requires_input=False,
    ),
    "weather": Movement(
        name="Conceptual Weather",
        prompt="What's shifting in the atmosphere?",
        duration_hint="~2 min",
        requires_input=False,
    ),
    "menu": Movement(
        name="Menu",
        prompt="What suits my taste this morning?",
        duration_hint="~3 min",
        requires_input=True,
    ),
    "capture": Movement(
        name="Fresh Capture",
        prompt="What's on your mind before code takes over?",
        duration_hint="~3 min",
        requires_input=True,
    ),
}


# =============================================================================
# Garden Types (Movement 1)
# =============================================================================


class GardenCategory(Enum):
    """Categories of garden items."""

    HARVEST = "harvest"  # Yesterday's completed work
    GROWING = "growing"  # Active work in progress (high %)
    SPROUTING = "sprouting"  # Recently started (medium %)
    SEEDS = "seeds"  # Just planted (low %)


@dataclass(frozen=True)
class GardenItem:
    """
    A single item in the garden view.

    Represents a file change, commit, or progress indicator.
    """

    description: str
    category: GardenCategory
    files_changed: int = 0
    source: str = ""  # "git", "now_md", "brainstorming"
    percentage: float | None = None  # For progress items

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "description": self.description,
            "category": self.category.value,
            "files_changed": self.files_changed,
            "source": self.source,
            "percentage": self.percentage,
        }


@dataclass(frozen=True)
class GardenView:
    """
    The Garden View — Movement 1.

    A non-demanding overview that lets Kent's eye wander:
    - What changed yesterday (harvest)
    - What's actively growing (high progress)
    - What's just sprouting (medium progress)
    - What seeds were planted (new ideas)
    """

    harvest: tuple[GardenItem, ...] = ()
    growing: tuple[GardenItem, ...] = ()
    sprouting: tuple[GardenItem, ...] = ()
    seeds: tuple[GardenItem, ...] = ()
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "harvest": [item.to_dict() for item in self.harvest],
            "growing": [item.to_dict() for item in self.growing],
            "sprouting": [item.to_dict() for item in self.sprouting],
            "seeds": [item.to_dict() for item in self.seeds],
            "generated_at": self.generated_at.isoformat(),
        }

    @property
    def is_empty(self) -> bool:
        """Check if the garden view has any items."""
        return not (self.harvest or self.growing or self.sprouting or self.seeds)

    @property
    def total_items(self) -> int:
        """Total number of items across all categories."""
        return len(self.harvest) + len(self.growing) + len(self.sprouting) + len(self.seeds)


# =============================================================================
# Weather Types (Movement 2)
# =============================================================================


class WeatherType(Enum):
    """Types of conceptual weather patterns."""

    REFACTORING = "refactoring"  # Things being consolidated/renamed
    EMERGING = "emerging"  # New patterns/principles appearing
    SCAFFOLDING = "scaffolding"  # Architecture being built
    TENSION = "tension"  # Competing concerns/decisions

    @property
    def emoji(self) -> str:
        """Visual indicator."""
        return {
            WeatherType.REFACTORING: "🔄",
            WeatherType.EMERGING: "🌊",
            WeatherType.SCAFFOLDING: "🏗️",
            WeatherType.TENSION: "⚡",
        }[self]


@dataclass(frozen=True)
class WeatherPattern:
    """
    A single conceptual weather pattern.

    Not code changes — conceptual movements.
    """

    type: WeatherType
    label: str  # Short label
    description: str  # Explanation
    source: str = ""  # "plan", "commit", "witness"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "emoji": self.type.emoji,
            "label": self.label,
            "description": self.description,
            "source": self.source,
        }


@dataclass(frozen=True)
class ConceptualWeather:
    """
    The Conceptual Weather — Movement 2.

    What's shifting in the atmosphere of the codebase:
    - Refactoring: consolidations, renames, migrations
    - Emerging: new patterns, principles, insights
    - Scaffolding: architecture being built
    - Tension: competing concerns, unresolved decisions
    """

    refactoring: tuple[WeatherPattern, ...] = ()
    emerging: tuple[WeatherPattern, ...] = ()
    scaffolding: tuple[WeatherPattern, ...] = ()
    tension: tuple[WeatherPattern, ...] = ()
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "refactoring": [p.to_dict() for p in self.refactoring],
            "emerging": [p.to_dict() for p in self.emerging],
            "scaffolding": [p.to_dict() for p in self.scaffolding],
            "tension": [p.to_dict() for p in self.tension],
            "generated_at": self.generated_at.isoformat(),
        }

    @property
    def is_empty(self) -> bool:
        """Check if there are any weather patterns."""
        return not (self.refactoring or self.emerging or self.scaffolding or self.tension)

    @property
    def all_patterns(self) -> list[WeatherPattern]:
        """Get all patterns as a flat list."""
        return (
            list(self.refactoring)
            + list(self.emerging)
            + list(self.scaffolding)
            + list(self.tension)
        )


# =============================================================================
# Menu Types (Movement 3)
# =============================================================================


@dataclass(frozen=True)
class MenuItem:
    """
    A potential work item on the menu.

    Key: These are invitations, not assignments. Kent picks based on
    how he feels *right now*.
    """

    label: str
    description: str
    level: ChallengeLevel
    agentese_path: str | None = None  # Path to invoke if selected
    source: str = ""  # "todo", "plan", "witness"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "label": self.label,
            "description": self.description,
            "level": self.level.value,
            "level_emoji": self.level.emoji,
            "agentese_path": self.agentese_path,
            "source": self.source,
        }


@dataclass(frozen=True)
class ChallengeMenu:
    """
    The Menu — Movement 3.

    Presents challenge gradients — Kent chooses valence and magnitude.
    The serendipitous option is always available: "What caught your eye?"
    """

    gentle: tuple[MenuItem, ...] = ()
    focused: tuple[MenuItem, ...] = ()
    intense: tuple[MenuItem, ...] = ()
    serendipitous_prompt: str = "What caught your eye in the garden view?"
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "gentle": [item.to_dict() for item in self.gentle],
            "focused": [item.to_dict() for item in self.focused],
            "intense": [item.to_dict() for item in self.intense],
            "serendipitous_prompt": self.serendipitous_prompt,
            "generated_at": self.generated_at.isoformat(),
        }

    @property
    def is_empty(self) -> bool:
        """Check if menu has any items (serendipity always available)."""
        return not (self.gentle or self.focused or self.intense)

    def get_items_by_level(self, level: ChallengeLevel) -> tuple[MenuItem, ...]:
        """Get items for a specific challenge level."""
        return {
            ChallengeLevel.GENTLE: self.gentle,
            ChallengeLevel.FOCUSED: self.focused,
            ChallengeLevel.INTENSE: self.intense,
            ChallengeLevel.SERENDIPITOUS: (),  # No predefined items
        }[level]


# =============================================================================
# Voice Types (Movement 4)
# =============================================================================


@dataclass(frozen=True)
class MorningVoice:
    """
    Fresh capture of Kent's authentic morning state.

    The anti-sausage goldmine — Kent at 8am after rest ≠ Kent at 11pm
    after 6 hours of debugging. Morning Kent is closer to the "vision holder."

    These captures become voice anchors for future anti-sausage checks.
    """

    captured_date: date
    non_code_thought: str | None = None  # "What's on your mind (not code)?"
    eye_catch: str | None = None  # "What catches your eye in garden?"
    success_criteria: str | None = None  # "What would make today feel good?"
    raw_feeling: str | None = None  # Optional general feeling
    chosen_challenge: ChallengeLevel | None = None  # What was selected from menu

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "captured_date": self.captured_date.isoformat(),
            "non_code_thought": self.non_code_thought,
            "eye_catch": self.eye_catch,
            "success_criteria": self.success_criteria,
            "raw_feeling": self.raw_feeling,
            "chosen_challenge": self.chosen_challenge.value if self.chosen_challenge else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MorningVoice":
        """Create from dictionary."""
        captured_date = data.get("captured_date")
        if isinstance(captured_date, str):
            captured_date = date.fromisoformat(captured_date)
        elif captured_date is None:
            captured_date = date.today()

        chosen = data.get("chosen_challenge")
        chosen_challenge = ChallengeLevel(chosen) if chosen else None

        return cls(
            captured_date=captured_date,
            non_code_thought=data.get("non_code_thought"),
            eye_catch=data.get("eye_catch"),
            success_criteria=data.get("success_criteria"),
            raw_feeling=data.get("raw_feeling"),
            chosen_challenge=chosen_challenge,
        )

    @property
    def is_substantive(self) -> bool:
        """Check if the capture has meaningful content."""
        return bool(
            self.non_code_thought or self.eye_catch or self.success_criteria or self.raw_feeling
        )

    def as_voice_anchor(self) -> dict[str, Any] | None:
        """
        Convert to a voice anchor if substantive.

        Voice anchors are used by the anti-sausage protocol to check
        if today's work is consistent with morning Kent's voice.
        """
        if not self.success_criteria:
            return None

        return {
            "text": self.success_criteria,
            "source": "morning_coffee",
            "captured_at": datetime.now().isoformat(),
            "captured_date": self.captured_date.isoformat(),
        }


# =============================================================================
# Ritual Events and Outputs
# =============================================================================


@dataclass(frozen=True)
class RitualEvent:
    """
    Input event to the Coffee polynomial.

    Events drive state transitions in the ritual.
    """

    command: str  # "wake", "continue", "skip", "select", "record", "exit"
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "command": self.command,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class CoffeeOutput:
    """
    Output from the Coffee polynomial.

    Wraps the result of a state transition.
    """

    status: str  # "ok", "skipped", "exited", "error"
    state: CoffeeState
    movement: Movement | None = None
    garden: GardenView | None = None
    weather: ConceptualWeather | None = None
    menu: ChallengeMenu | None = None
    voice: MorningVoice | None = None
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "status": self.status,
            "state": self.state.name,
            "message": self.message,
        }
        if self.movement:
            result["movement"] = self.movement.to_dict()
        if self.garden:
            result["garden"] = self.garden.to_dict()
        if self.weather:
            result["weather"] = self.weather.to_dict()
        if self.menu:
            result["menu"] = self.menu.to_dict()
        if self.voice:
            result["voice"] = self.voice.to_dict()
        if self.data:
            result["data"] = self.data
        return result


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # State machine
    "CoffeeState",
    # Challenge levels
    "ChallengeLevel",
    # Movements
    "Movement",
    "MOVEMENTS",
    # Garden types
    "GardenCategory",
    "GardenItem",
    "GardenView",
    # Weather types
    "WeatherType",
    "WeatherPattern",
    "ConceptualWeather",
    # Menu types
    "MenuItem",
    "ChallengeMenu",
    # Voice types
    "MorningVoice",
    # Events and outputs
    "RitualEvent",
    "CoffeeOutput",
]
