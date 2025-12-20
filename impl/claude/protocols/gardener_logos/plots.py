"""
Plots: Named regions of the garden with their own state.

A plot is a focused area of the garden that can have:
- Its own prompts (task templates, agent configurations)
- Its own season (may differ from garden-wide)
- Its own momentum (gesture trace)
- Rigidity (resistance to change)

Plots correspond to:
- Plan files (e.g., plans/coalition-forge.md)
- Crown jewels (e.g., Atelier, Brain)
- Custom focus areas (e.g., "refactoring auth")

See: spec/protocols/gardener-logos.md Part I.3
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .garden import GardenSeason
    from .tending import TendingGesture


@dataclass
class PlotState:
    """
    A plot in the garden.

    Plots are named focus regions, each with their own:
    - Prompts active in the plot
    - Season (can differ from garden-wide)
    - Momentum (recent gestures)
    - Rigidity (resistance to change)

    Plots naturally map to Forest Protocol plans:
    - name: "coalition-forge"
    - path: "world.forge" (AGENTESE)
    - plan_path: "plans/core-apps/coalition-forge.md"

    Or to Crown Jewels:
    - name: "holographic-brain"
    - path: "self.memory"
    - crown_jewel: "Brain"
    """

    # Identity
    name: str
    path: str  # AGENTESE path (world.forge, self.memory, etc.)
    description: str = ""

    # Optional linkages
    plan_path: str | None = None  # Forest Protocol plan file
    crown_jewel: str | None = None  # Which jewel this corresponds to

    # Prompts active in this plot
    prompts: list[str] = field(default_factory=list)  # Prompt IDs

    # Season (if None, inherits from garden)
    season_override: "GardenSeason | None" = None

    # Momentum (recent gestures in this plot)
    momentum: list["TendingGesture"] = field(default_factory=list)

    # Rigidity (0.0 = fully plastic, 1.0 = fixed)
    rigidity: float = 0.5

    # Progress (for plan-linked plots)
    progress: float = 0.0

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    last_tended: datetime = field(default_factory=datetime.now)

    # Metadata
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for persistence."""
        return {
            "name": self.name,
            "path": self.path,
            "description": self.description,
            "plan_path": self.plan_path,
            "crown_jewel": self.crown_jewel,
            "prompts": self.prompts,
            "season_override": self.season_override.name if self.season_override else None,
            "momentum": [g.to_dict() for g in self.momentum[-10:]],
            "rigidity": self.rigidity,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
            "last_tended": self.last_tended.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlotState":
        """Deserialize from persistence."""
        from .garden import GardenSeason
        from .tending import TendingGesture

        def parse_dt(val: str | None) -> datetime:
            if val:
                return datetime.fromisoformat(val)
            return datetime.now()

        season_name = data.get("season_override")
        season = GardenSeason[season_name] if season_name else None

        momentum = [TendingGesture.from_dict(g) for g in data.get("momentum", [])]

        return cls(
            name=data.get("name", ""),
            path=data.get("path", ""),
            description=data.get("description", ""),
            plan_path=data.get("plan_path"),
            crown_jewel=data.get("crown_jewel"),
            prompts=data.get("prompts", []),
            season_override=season,
            momentum=momentum,
            rigidity=data.get("rigidity", 0.5),
            progress=data.get("progress", 0.0),
            created_at=parse_dt(data.get("created_at")),
            last_tended=parse_dt(data.get("last_tended")),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )

    def get_effective_season(self, garden_season: "GardenSeason") -> "GardenSeason":
        """Get the season for this plot (override or garden default)."""
        return self.season_override or garden_season

    def add_gesture(self, gesture: "TendingGesture") -> None:
        """Add a gesture to the plot's momentum."""
        self.momentum.append(gesture)
        self.last_tended = datetime.now()

        # Keep only last 20 gestures per plot
        if len(self.momentum) > 20:
            self.momentum = self.momentum[-20:]

    @property
    def is_active(self) -> bool:
        """Whether the plot has been tended recently."""
        from datetime import timedelta

        return datetime.now() - self.last_tended < timedelta(hours=24)

    @property
    def display_name(self) -> str:
        """Display-friendly name."""
        return self.name.replace("-", " ").title()


def create_plot(
    name: str,
    path: str,
    description: str = "",
    plan_path: str | None = None,
    crown_jewel: str | None = None,
    rigidity: float = 0.5,
) -> PlotState:
    """
    Factory to create a new plot.

    Args:
        name: Human-readable name (e.g., "coalition-forge")
        path: AGENTESE path (e.g., "world.forge")
        description: Optional description
        plan_path: Link to Forest Protocol plan file
        crown_jewel: Which crown jewel this corresponds to
        rigidity: How much the plot resists change (0-1)

    Returns:
        Fresh PlotState
    """
    return PlotState(
        name=name,
        path=path,
        description=description,
        plan_path=plan_path,
        crown_jewel=crown_jewel,
        rigidity=rigidity,
    )


# =============================================================================
# Standard Plots (Pre-defined for Crown Jewels)
# =============================================================================


def create_crown_jewel_plots() -> dict[str, PlotState]:
    """
    Create standard plots for the seven Crown Jewels.

    These are the default plots that exist in every garden,
    corresponding to the Crown Jewel architecture.
    """
    return {
        "atelier": PlotState(
            name="atelier",
            path="world.atelier",
            description="Creative workshop for artifact creation",
            crown_jewel="Atelier",
            rigidity=0.4,  # Creative = more plastic
            tags=["creation", "artifacts", "bidding"],
        ),
        "coalition-forge": PlotState(
            name="coalition-forge",
            path="world.forge",
            description="Multi-agent coalition formation",
            crown_jewel="Coalition",
            rigidity=0.5,
            tags=["agents", "teams", "tasks"],
        ),
        "holographic-brain": PlotState(
            name="holographic-brain",
            path="self.memory",
            description="Semantic memory and knowledge cartography",
            crown_jewel="Brain",
            rigidity=0.6,  # Memory should be stable
            tags=["memory", "crystals", "knowledge"],
        ),
        "punchdrunk-park": PlotState(
            name="punchdrunk-park",
            path="world.town",
            description="Agent Town immersive simulation",
            crown_jewel="Park",
            rigidity=0.3,  # Playful = very plastic
            tags=["simulation", "inhabit", "scenarios"],
        ),
        "domain-sim": PlotState(
            name="domain-sim",
            path="world.simulation",
            description="Domain-specific crisis and compliance drills",
            crown_jewel="Domain",
            rigidity=0.7,  # Drills should be stable
            tags=["drills", "compliance", "crisis"],
        ),
        "gestalt-viz": PlotState(
            name="gestalt-viz",
            path="world.codebase",
            description="Codebase architecture visualization",
            crown_jewel="Gestalt",
            rigidity=0.5,
            tags=["architecture", "modules", "drift"],
        ),
        "gardener": PlotState(
            name="gardener",
            path="concept.gardener",
            description="The meta-tending interface itself",
            crown_jewel="Gardener",
            rigidity=0.8,  # Core infrastructure = stable
            tags=["meta", "sessions", "prompts"],
        ),
    }


# =============================================================================
# Plot Discovery (from Forest Protocol)
# =============================================================================


async def discover_plots_from_forest(
    forest_path: str = "plans",
) -> list[PlotState]:
    """
    Discover plots from Forest Protocol plan files.

    Phase 5: Batteries Included - Now extracts real progress from:
    1. _forest.md table (source of truth for progress percentages)
    2. Individual plan file headers for status

    Scans the plans/ directory for active plan files and
    creates corresponding plots with real progress data.

    Args:
        forest_path: Path to plans directory

    Returns:
        List of discovered plots with real progress
    """
    from pathlib import Path

    from services.gardener.plan_parser import (
        infer_agentese_path,
        infer_crown_jewel,
        parse_forest_table,
        parse_plan_progress,
    )

    plots: list[PlotState] = []
    plans_dir = Path(forest_path)

    if not plans_dir.exists():
        return plots

    # 1. Parse _forest.md for authoritative progress data
    forest_file = plans_dir / "_forest.md"
    forest_progress = parse_forest_table(forest_file)

    # 2. Scan for plan files
    for plan_file in plans_dir.glob("**/*.md"):
        # Skip underscore-prefixed (meta files like _forest.md, _focus.md)
        if plan_file.name.startswith("_"):
            continue

        # Parse plan name from file
        name = plan_file.stem

        # 3. Get progress: forest table is authoritative, fallback to file parse
        if name in forest_progress:
            metadata = forest_progress[name]
            progress = metadata.progress
            status = metadata.status
            notes = metadata.notes
        else:
            # Parse individual file
            metadata = await parse_plan_progress(plan_file)
            progress = metadata.progress
            status = metadata.status
            notes = metadata.notes

        # 4. Infer AGENTESE path
        path = infer_agentese_path(plan_file)

        # 5. Check if this links to a Crown Jewel
        crown_jewel = infer_crown_jewel(name)

        # 6. Infer rigidity from status
        rigidity = _status_to_rigidity(status)

        # 7. Build tags from status and crown jewel
        tags = ["plan", "forest"]
        if status:
            tags.append(status)
        if crown_jewel:
            tags.append("crown-jewel")

        plot = PlotState(
            name=name,
            path=path,
            description=notes or f"Plan: {plan_file.name}",
            plan_path=str(plan_file),
            crown_jewel=crown_jewel,
            rigidity=rigidity,
            progress=progress,
            tags=tags,
        )
        plots.append(plot)

    return plots


def _status_to_rigidity(status: str) -> float:
    """
    Map plan status to rigidity value.

    Active plans are more plastic, complete plans are rigid.
    """
    status = status.lower() if status else "active"

    rigidity_map = {
        "planning": 0.3,  # Very plastic - still exploring
        "seedling": 0.35,
        "active": 0.4,  # Moderate plasticity
        "executing": 0.45,
        "priority": 0.5,
        "complete": 0.8,  # Rigid - done
        "dormant": 0.6,  # Somewhat rigid - inactive
        "superseded": 0.7,  # Rigid - replaced
    }

    return rigidity_map.get(status, 0.5)


__all__ = [
    "PlotState",
    "create_plot",
    "create_crown_jewel_plots",
    "discover_plots_from_forest",
]
