"""
Garden State AGENTESE Contract Definitions.

self.garden.* handles garden STATE (plots, seasons, gestures, health).
Distinct from services/gardener/contracts.py which handles SESSION orchestration.

The relationship:
- concept.gardener.* = Session polynomial (SENSE → ACT → REFLECT)
- self.garden.* = Garden state (plots, seasons, gestures)

The Gardener2D visualization needs BOTH:
- GardenJSON from self.garden.manifest (plots, seasons)
- GardenerSessionState from concept.gardener.session.manifest (phase, intent)

Contract Protocol (Phase 7: Autopoietic Architecture):
- Response() for perception aspects (manifest, season, health, suggest)
- Contract() for mutation aspects (init, transition, accept, dismiss)

@see protocols/agentese/contexts/garden.py
@see impl/claude/web/src/reactive/types.ts - GardenJSON TypeScript equivalent
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# =============================================================================
# Season Type
# =============================================================================

GardenSeason = Literal["DORMANT", "SPROUTING", "BLOOMING", "HARVEST", "COMPOSTING"]

# =============================================================================
# Manifest Response (Full Garden State)
# =============================================================================


@dataclass(frozen=True)
class PlotContract:
    """Plot state for garden regions."""

    name: str
    path: str
    description: str
    plan_path: str | None
    crown_jewel: str | None
    prompts: list[str]
    season_override: GardenSeason | None
    rigidity: float
    progress: float
    created_at: str
    last_tended: str
    tags: list[str]
    metadata: dict[str, object] = field(default_factory=dict)
    is_active: bool = False


@dataclass(frozen=True)
class GestureContract:
    """Tending gesture record."""

    verb: str  # OBSERVE, PRUNE, GRAFT, WATER, ROTATE, WAIT
    target: str
    tone: float
    reasoning: str
    entropy_cost: float
    timestamp: str
    observer: str
    session_id: str | None
    result_summary: str


@dataclass(frozen=True)
class GardenMetricsContract:
    """Garden metrics."""

    health_score: float
    total_prompts: int
    active_plots: int
    entropy_spent: float
    entropy_budget: float


@dataclass(frozen=True)
class GardenComputedContract:
    """Computed garden fields."""

    health_score: float
    entropy_remaining: float
    entropy_percentage: float
    active_plot_count: int
    total_plot_count: int
    season_plasticity: float
    season_entropy_multiplier: float


@dataclass(frozen=True)
class SelfGardenManifestResponse:
    """
    Full garden state JSON (from project_garden_to_json).

    This is the rich structure used by Gardener2D visualization.
    Maps to GardenJSON TypeScript type in reactive/types.ts.
    """

    type: str  # Always "garden"
    garden_id: str
    name: str
    created_at: str
    season: GardenSeason
    season_since: str
    plots: dict[str, object]  # Record<string, PlotContract>
    active_plot: str | None
    session_id: str | None
    memory_crystals: list[str]
    prompt_count: int
    prompt_types: dict[str, int]  # Record<string, number>
    recent_gestures: list[dict[str, object]]  # GestureContract[]
    last_tended: str
    metrics: dict[str, object]  # GardenMetricsContract
    computed: dict[str, object]  # GardenComputedContract


# =============================================================================
# Season Response
# =============================================================================


@dataclass(frozen=True)
class SelfGardenSeasonResponse:
    """Current season information."""

    name: GardenSeason
    emoji: str
    plasticity: float
    entropy_multiplier: float
    since: str
    description: str


# =============================================================================
# Health Response
# =============================================================================


@dataclass(frozen=True)
class SelfGardenHealthResponse:
    """Garden health metrics."""

    health_score: float
    total_prompts: int
    active_plots: int
    recent_gestures: int
    session_cycles: int
    entropy_spent: float
    entropy_budget: float
    entropy_remaining: float
    health_bar: str  # ASCII progress bar


# =============================================================================
# Suggestion Response
# =============================================================================


@dataclass(frozen=True)
class SelfGardenSuggestResponse:
    """Auto-inducer season transition suggestion."""

    status: str  # "suggestion" | "no_suggestion"
    from_season: GardenSeason | None = None
    to_season: GardenSeason | None = None
    confidence: float = 0.0
    reason: str = ""
    signals: dict[str, object] = field(default_factory=dict)
    should_suggest: bool = False
    confidence_bar: str = ""
    message: str | None = None


# =============================================================================
# Mutation Contracts
# =============================================================================


@dataclass(frozen=True)
class SelfGardenInitResponse:
    """Response after initializing garden."""

    status: str  # "initialized" | "error"
    garden_id: str
    name: str
    season: GardenSeason
    plots: list[str]
    plot_count: int


@dataclass(frozen=True)
class SelfGardenTransitionRequest:
    """Request to transition to new season."""

    target: str  # Target season name
    reason: str = "Manual transition"


@dataclass(frozen=True)
class SelfGardenTransitionResponse:
    """Response after season transition."""

    status: str  # "transitioned" | "error"
    from_season: GardenSeason
    from_emoji: str
    to_season: GardenSeason
    to_emoji: str
    reason: str
    old_plasticity: float
    new_plasticity: float


@dataclass(frozen=True)
class SelfGardenAcceptResponse:
    """Response after accepting transition suggestion."""

    status: str  # "accepted" | "no_suggestion"
    from_season: GardenSeason | None = None
    to_season: GardenSeason | None = None
    reason: str = ""
    message: str | None = None


@dataclass(frozen=True)
class SelfGardenDismissResponse:
    """Response after dismissing transition suggestion."""

    status: str  # "dismissed" | "no_suggestion"
    from_season: GardenSeason | None = None
    to_season: GardenSeason | None = None
    cooldown_hours: int = 4
    message: str | None = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Season type
    "GardenSeason",
    # Sub-contracts
    "PlotContract",
    "GestureContract",
    "GardenMetricsContract",
    "GardenComputedContract",
    # Perception responses
    "SelfGardenManifestResponse",
    "SelfGardenSeasonResponse",
    "SelfGardenHealthResponse",
    "SelfGardenSuggestResponse",
    # Mutation contracts
    "SelfGardenInitResponse",
    "SelfGardenTransitionRequest",
    "SelfGardenTransitionResponse",
    "SelfGardenAcceptResponse",
    "SelfGardenDismissResponse",
]
