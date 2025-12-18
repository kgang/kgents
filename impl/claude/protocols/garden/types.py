"""
Garden Protocol Types: Core type definitions for next-generation planning.

This module implements the types from spec/protocols/garden-protocol.md:
- Season: Plan lifecycle stages (SPROUTING → BLOOMING → FRUITING → COMPOSTING → DORMANT)
- Mood: Emotional state vocabulary (excited, curious, focused, stuck, tired, dreaming...)
- Trajectory: Momentum direction (accelerating, cruising, decelerating, parked)
- GardenPlanHeader: The new YAML header format
- GardenPolynomial: PolyAgent for plan behavior

Key insight from spec:
> "Plans are conversations with future selves, not checklists."
> "The unit of planning is the session, not the plan file."
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, FrozenSet

import yaml
from agents.poly.protocol import PolyAgent

# =============================================================================
# Enums: Season, Trajectory, Mood, GardenInput, GestureType
# =============================================================================


class Season(Enum):
    """
    Plan lifecycle stages.

    Plans have natural rhythms like gardens:
    - SPROUTING: New, exploring, high plasticity
    - BLOOMING: Active development, productive
    - FRUITING: Harvesting results, documentation
    - COMPOSTING: Extracting learnings, winding down
    - DORMANT: Resting, may dream (void.* connections)
    """

    SPROUTING = "sprouting"
    BLOOMING = "blooming"
    FRUITING = "fruiting"
    COMPOSTING = "composting"
    DORMANT = "dormant"


class Trajectory(Enum):
    """
    Momentum direction - how the plan's energy is changing.

    Combined with momentum (0-1 float), this gives a full picture:
    - accelerating + momentum 0.7 = gaining speed
    - decelerating + momentum 0.3 = slowing down
    - parked + momentum 0.0 = intentionally stopped
    """

    ACCELERATING = "accelerating"
    CRUISING = "cruising"
    DECELERATING = "decelerating"
    PARKED = "parked"


class Mood(Enum):
    """
    Emotional state vocabulary for plans.

    From spec: "Choose from natural, unstrained words."
    Anti-pattern: Don't use forced vocabulary ("vibing", "stoked", "effervescent").
    """

    EXCITED = "excited"  # High energy, eager to work on this
    CURIOUS = "curious"  # Exploring, not sure where it leads
    FOCUSED = "focused"  # Deep work, don't interrupt
    SATISFIED = "satisfied"  # Good progress, happy with state
    STUCK = "stuck"  # Blocked but not by external dep
    WAITING = "waiting"  # Blocked by external dep
    TIRED = "tired"  # Needs rest, don't push
    DREAMING = "dreaming"  # Dormant but generating connections
    COMPLETE = "complete"  # Ready for archive


class GardenInput(Enum):
    """
    Valid inputs for GardenPolynomial based on season.

    Different seasons accept different inputs - this is the key polynomial insight.
    """

    # SPROUTING inputs
    EXPLORE = "explore"  # Divergent exploration
    DEFINE = "define"  # Define scope
    CONNECT = "connect"  # Find connections to other plans

    # BLOOMING inputs
    BUILD = "build"  # Active development
    TEST = "test"  # Testing and validation
    REFINE = "refine"  # Iterative improvement

    # FRUITING inputs
    DOCUMENT = "document"  # Documentation
    SHIP = "ship"  # Release/deploy
    CELEBRATE = "celebrate"  # Mark achievement

    # COMPOSTING inputs
    EXTRACT = "extract"  # Extract learnings
    ARCHIVE = "archive"  # Archive completed work
    TITHE = "tithe"  # Return learning to void

    # DORMANT inputs
    DREAM = "dream"  # Generate void connections
    WAKE = "wake"  # Transition out of dormant


class GestureType(Enum):
    """
    Atomic units of work within a session.

    Gestures are recorded in sessions and propagate to plan updates.
    """

    CODE = "code"  # Files changed
    INSIGHT = "insight"  # Learning captured
    DECISION = "decision"  # Choice made
    VOID_SIP = "void_sip"  # Entropy draw
    VOID_TITHE = "void_tithe"  # Learning returned
    CONNECT = "connect"  # Cross-plan link discovered
    PRUNE = "prune"  # Removed/archived something


# =============================================================================
# Dataclasses: EntropyBudget, GardenPlanHeader, Gesture, SessionHeader
# =============================================================================


@dataclass(frozen=True)
class EntropySip:
    """
    A single draw from the void entropy budget.

    Records when and why entropy was spent on exploration.
    """

    date: str
    description: str

    def __str__(self) -> str:
        return f"{self.date}: {self.description}"


@dataclass
class EntropyBudget:
    """
    Void budget tracking for serendipity.

    Each plan has an entropy budget that actually gets spent:
    - available: Starting budget (configurable per plan)
    - spent: Accumulated draws
    - sips: Record of what was drawn

    When spent >= available, no more `sip` operations allowed.
    This forces intentionality about exploration vs execution.
    """

    available: float = 0.10
    spent: float = 0.0
    sips: list[EntropySip] = field(default_factory=list)

    @property
    def remaining(self) -> float:
        """Remaining entropy budget."""
        return max(0.0, self.available - self.spent)

    @property
    def exhausted(self) -> bool:
        """True if no more entropy available."""
        return self.spent >= self.available

    def sip(self, description: str, amount: float = 0.02) -> bool:
        """
        Draw from entropy budget.

        Returns True if draw succeeded, False if budget exhausted.
        """
        if self.exhausted:
            return False

        self.spent += amount
        self.sips.append(
            EntropySip(
                date=date.today().isoformat(),
                description=description,
            )
        )
        return True

    def tithe(self, amount: float = 0.02) -> None:
        """Return learning to void, restoring available budget."""
        self.available += amount

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        result: dict[str, Any] = {
            "available": self.available,
            "spent": self.spent,
        }
        if self.sips:
            result["sips"] = [str(s) for s in self.sips]
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EntropyBudget":
        """Create from dictionary (YAML deserialization)."""
        sips = []
        for sip_str in data.get("sips", []):
            # Parse "YYYY-MM-DD: description" format
            if ": " in sip_str:
                date_part, desc = sip_str.split(": ", 1)
                sips.append(EntropySip(date=date_part, description=desc))
            else:
                sips.append(EntropySip(date="", description=sip_str))

        return cls(
            available=data.get("available", 0.10),
            spent=data.get("spent", 0.0),
            sips=sips,
        )


@dataclass
class GardenPlanHeader:
    """
    The new YAML header format for Garden Protocol.

    From spec:
    ```yaml
    path: self.forest.plan.coalition-forge
    mood: excited
    momentum: 0.7
    trajectory: accelerating
    season: BLOOMING
    last_gardened: 2025-12-18
    gardener: claude-opus-4-5
    letter: |
      We made real progress today...
    resonates_with:
      - atelier-experience
      - punchdrunk-park
    entropy:
      available: 0.10
      spent: 0.03
      sips: [...]
    ```

    Key changes from Forest Protocol:
    - path: Now AGENTESE path (self.forest.plan.{name})
    - mood: Replaces status (more expressive)
    - momentum + trajectory: Replaces progress percentage
    - season: Lifecycle stage
    - letter: Replaces session_notes (conversation, not log)
    - resonates_with: Replaces blocking/enables (semantic, not dependency)
    """

    # Identity
    path: str  # AGENTESE path: self.forest.plan.{name}

    # State
    mood: Mood
    momentum: float  # 0.0 to 1.0
    trajectory: Trajectory
    season: Season

    # Metadata
    last_gardened: date
    gardener: str

    # Content
    letter: str  # Conversation with future self
    resonates_with: list[str] = field(default_factory=list)  # Semantic connections

    # Entropy
    entropy: EntropyBudget = field(default_factory=EntropyBudget)

    @property
    def name(self) -> str:
        """Extract plan name from AGENTESE path."""
        # self.forest.plan.coalition-forge -> coalition-forge
        if self.path.startswith("self.forest.plan."):
            return self.path.split(".")[-1]
        # Legacy path: plans/coalition-forge -> coalition-forge
        return self.path.split("/")[-1]

    @property
    def progress_equivalent(self) -> int:
        """
        Convert momentum/trajectory to legacy progress percentage.

        For backwards compatibility with Forest Protocol tools.
        """
        base = int(self.momentum * 100)

        # Adjust based on season
        match self.season:
            case Season.SPROUTING:
                return min(base, 20)
            case Season.BLOOMING:
                return max(20, min(base, 80))
            case Season.FRUITING:
                return max(80, min(base, 95))
            case Season.COMPOSTING:
                return max(95, base)
            case Season.DORMANT:
                return base

        return base

    @property
    def status_equivalent(self) -> str:
        """
        Convert season/mood to legacy status.

        For backwards compatibility with Forest Protocol tools.
        """
        if self.mood == Mood.COMPLETE:
            return "complete"
        if self.season == Season.DORMANT:
            return "dormant"
        if self.mood == Mood.WAITING:
            return "blocked"
        return "active"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        return {
            "path": self.path,
            "mood": self.mood.value,
            "momentum": self.momentum,
            "trajectory": self.trajectory.value,
            "season": self.season.value.upper(),
            "last_gardened": self.last_gardened.isoformat(),
            "gardener": self.gardener,
            "letter": self.letter,
            "resonates_with": self.resonates_with,
            "entropy": self.entropy.to_dict(),
        }

    def to_yaml(self) -> str:
        """Convert to YAML string for writing to file."""
        return yaml.dump(
            self.to_dict(),
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GardenPlanHeader":
        """Create from dictionary (YAML deserialization)."""
        # Parse date
        last_gardened_raw = data.get("last_gardened", date.today())
        if isinstance(last_gardened_raw, str):
            try:
                last_gardened = datetime.strptime(last_gardened_raw, "%Y-%m-%d").date()
            except ValueError:
                last_gardened = date.today()
        elif isinstance(last_gardened_raw, date):
            last_gardened = last_gardened_raw
        else:
            last_gardened = date.today()

        # Parse season (handle both "BLOOMING" and "blooming")
        season_str = data.get("season", "SPROUTING")
        try:
            season = Season(season_str.lower())
        except ValueError:
            season = Season.SPROUTING

        # Parse mood
        mood_str = data.get("mood", "curious")
        try:
            mood = Mood(mood_str.lower())
        except ValueError:
            mood = Mood.CURIOUS

        # Parse trajectory
        trajectory_str = data.get("trajectory", "cruising")
        try:
            trajectory = Trajectory(trajectory_str.lower())
        except ValueError:
            trajectory = Trajectory.CRUISING

        # Parse entropy
        entropy_data = data.get("entropy", {})
        if isinstance(entropy_data, dict):
            entropy = EntropyBudget.from_dict(entropy_data)
        else:
            entropy = EntropyBudget()

        return cls(
            path=data.get("path", "self.forest.plan.unknown"),
            mood=mood,
            momentum=float(data.get("momentum", 0.5)),
            trajectory=trajectory,
            season=season,
            last_gardened=last_gardened,
            gardener=data.get("gardener", "unknown"),
            letter=data.get("letter", ""),
            resonates_with=data.get("resonates_with", []) or [],
            entropy=entropy,
        )


@dataclass
class Gesture:
    """
    An atomic unit of work within a session.

    Gestures are recorded as work happens and propagate to plan updates.
    """

    type: GestureType
    plan: str  # Plan name affected
    summary: str
    files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        result: dict[str, Any] = {
            "type": self.type.value,
            "plan": self.plan,
            "summary": self.summary,
        }
        if self.files:
            result["files"] = self.files
        return result


@dataclass
class SessionHeader:
    """
    YAML header for session files.

    Sessions are the primary unit of planning in Garden Protocol.
    Plans emerge from session traces like paths worn through a garden.

    Example:
    ```yaml
    date: 2025-12-18
    period: morning
    gardener: claude-opus-4-5
    plans_tended:
      - coalition-forge (BLOOMING → BLOOMING, momentum +0.1)
    gestures: [...]
    entropy_spent: 0.02
    ```
    """

    date: date
    period: str  # morning | afternoon | evening | night
    gardener: str
    plans_tended: list[str]  # "plan-name (SEASON → SEASON, momentum +/-X)"
    gestures: list[Gesture]
    entropy_spent: float
    letter: str = ""  # Letter to next session

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        return {
            "date": self.date.isoformat(),
            "period": self.period,
            "gardener": self.gardener,
            "plans_tended": self.plans_tended,
            "gestures": [g.to_dict() for g in self.gestures],
            "entropy_spent": self.entropy_spent,
        }


# =============================================================================
# GardenPolynomial: PolyAgent for plan behavior
# =============================================================================


def _garden_directions(season: Season) -> FrozenSet[GardenInput]:
    """
    Season-dependent valid inputs.

    From spec: Different seasons accept different inputs - this is the
    key polynomial insight that makes plans responsive to their lifecycle.
    """
    match season:
        case Season.SPROUTING:
            return frozenset(
                [GardenInput.EXPLORE, GardenInput.DEFINE, GardenInput.CONNECT]
            )
        case Season.BLOOMING:
            return frozenset([GardenInput.BUILD, GardenInput.TEST, GardenInput.REFINE])
        case Season.FRUITING:
            return frozenset(
                [GardenInput.DOCUMENT, GardenInput.SHIP, GardenInput.CELEBRATE]
            )
        case Season.COMPOSTING:
            return frozenset(
                [GardenInput.EXTRACT, GardenInput.ARCHIVE, GardenInput.TITHE]
            )
        case Season.DORMANT:
            return frozenset([GardenInput.DREAM, GardenInput.WAKE])


def _garden_transition(
    season: Season, input: GardenInput
) -> tuple[Season, GardenInput]:
    """
    State transition function for garden polynomial.

    Returns (new_season, output). Output is the input that was processed
    (for composition with downstream agents).
    """
    # Most inputs don't change season
    new_season = season

    # Special transitions
    match (season, input):
        # SPROUTING can bloom when defined
        case (Season.SPROUTING, GardenInput.DEFINE):
            # Optionally transition to BLOOMING
            pass

        # BLOOMING can fruit when shipped
        case (Season.BLOOMING, GardenInput.SHIP):
            new_season = Season.FRUITING

        # FRUITING can compost when celebrated
        case (Season.FRUITING, GardenInput.CELEBRATE):
            new_season = Season.COMPOSTING

        # COMPOSTING can go dormant when archived
        case (Season.COMPOSTING, GardenInput.ARCHIVE):
            new_season = Season.DORMANT

        # DORMANT wakes to SPROUTING
        case (Season.DORMANT, GardenInput.WAKE):
            new_season = Season.SPROUTING

    return new_season, input


# The Garden Polynomial as a PolyAgent
GardenPolynomial = PolyAgent[Season, GardenInput, GardenInput](
    name="GardenPolynomial",
    positions=frozenset(Season),
    _directions=_garden_directions,
    _transition=_garden_transition,
)
"""
Planning as polynomial functor.

The same input produces different outputs depending on season:
- SPROUTING: divergent exploration welcome
- BLOOMING: focused work expected
- COMPOSTING: reflection and extraction
- DORMANT: may dream (void.* connections)

Usage:
    >>> season = Season.BLOOMING
    >>> valid_inputs = GardenPolynomial.directions(season)
    >>> new_season, output = GardenPolynomial.invoke(season, GardenInput.BUILD)
"""


# =============================================================================
# Parser: YAML header parsing and migration
# =============================================================================


def parse_garden_header(file_path: Path) -> GardenPlanHeader | None:
    """
    Parse Garden Protocol YAML header from a markdown file.

    Args:
        file_path: Path to markdown file with YAML frontmatter

    Returns:
        GardenPlanHeader if valid Garden Protocol format, None otherwise
    """
    try:
        content = file_path.read_text()
    except Exception:
        return None

    if not content.startswith("---"):
        return None

    # Find end of YAML block
    end_match = re.search(r"\n---\s*\n", content[3:])
    if not end_match:
        return None

    yaml_content = content[3 : end_match.start() + 3]

    try:
        parsed = yaml.safe_load(yaml_content)
        if not parsed:
            return None

        # Check if this is Garden Protocol format (has 'mood' or 'season')
        if "mood" not in parsed and "season" not in parsed:
            return None

        return GardenPlanHeader.from_dict(parsed)
    except yaml.YAMLError:
        return None


def migrate_forest_to_garden(forest_header: dict[str, Any]) -> GardenPlanHeader:
    """
    Migrate a Forest Protocol header to Garden Protocol format.

    From spec section 8.2:
    - status: active → mood: focused (inferred)
    - progress: 55 → momentum: 0.55, trajectory: cruising
    - session_notes → letter
    - blocking/enables → resonates_with

    Args:
        forest_header: Parsed Forest Protocol YAML header

    Returns:
        Equivalent GardenPlanHeader
    """
    # Convert path
    old_path = forest_header.get("path", "unknown")
    if old_path.startswith("plans/"):
        name = old_path.split("/")[-1]
    else:
        name = old_path.replace("/", "-")
    new_path = f"self.forest.plan.{name}"

    # Convert status to mood
    status = forest_header.get("status", "active")
    mood_map = {
        "active": Mood.FOCUSED,
        "dormant": Mood.DREAMING,
        "blocked": Mood.WAITING,
        "complete": Mood.COMPLETE,
        "draft": Mood.CURIOUS,
    }
    mood = mood_map.get(status, Mood.CURIOUS)

    # Convert progress to momentum + trajectory
    progress = forest_header.get("progress", 0)
    momentum = progress / 100.0

    if momentum < 0.2:
        trajectory = Trajectory.PARKED if momentum == 0 else Trajectory.ACCELERATING
    elif momentum > 0.8:
        trajectory = Trajectory.DECELERATING
    else:
        trajectory = Trajectory.CRUISING

    # Infer season from progress and status
    if status == "complete":
        season = Season.COMPOSTING
    elif status == "dormant":
        season = Season.DORMANT
    elif progress < 20:
        season = Season.SPROUTING
    elif progress < 80:
        season = Season.BLOOMING
    elif progress < 95:
        season = Season.FRUITING
    else:
        season = Season.COMPOSTING

    # Convert last_touched to last_gardened
    last_touched_raw = forest_header.get("last_touched", date.today())
    if isinstance(last_touched_raw, str):
        try:
            last_gardened = datetime.strptime(last_touched_raw, "%Y-%m-%d").date()
        except ValueError:
            last_gardened = date.today()
    elif isinstance(last_touched_raw, date):
        last_gardened = last_touched_raw
    else:
        last_gardened = date.today()

    # Convert session_notes to letter
    session_notes = forest_header.get("session_notes", "")

    # Convert blocking/enables to resonates_with
    blocking = forest_header.get("blocking", []) or []
    enables = forest_header.get("enables", []) or []
    resonates_with = list(set(blocking + enables))

    # Convert entropy (if present)
    old_entropy = forest_header.get("entropy", {})
    if old_entropy:
        entropy = EntropyBudget(
            available=old_entropy.get("planned", 0.05)
            + old_entropy.get("returned", 0.0),
            spent=old_entropy.get("spent", 0.0),
            sips=[],
        )
    else:
        entropy = EntropyBudget()

    return GardenPlanHeader(
        path=new_path,
        mood=mood,
        momentum=momentum,
        trajectory=trajectory,
        season=season,
        last_gardened=last_gardened,
        gardener=forest_header.get("touched_by", "unknown"),
        letter=session_notes,
        resonates_with=resonates_with,
        entropy=entropy,
    )


__all__ = [
    # Enums
    "Season",
    "Trajectory",
    "Mood",
    "GardenInput",
    "GestureType",
    # Dataclasses
    "EntropyBudget",
    "EntropySip",
    "GardenPlanHeader",
    "Gesture",
    "SessionHeader",
    # Polynomial
    "GardenPolynomial",
    # Parser
    "parse_garden_header",
    "migrate_forest_to_garden",
]
