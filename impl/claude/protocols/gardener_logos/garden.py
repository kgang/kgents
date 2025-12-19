"""
Garden State: The unified state model for Gardener-Logos.

The garden is the union of:
1. SESSION state (SENSE/ACT/REFLECT cycle)
2. PROMPT state (prompt registry + evolution)
3. MEMORY context (crystals from Brain)
4. SEASON (relationship to change)
5. PLOTS (focused regions with their own state)

See: spec/protocols/gardener-logos.md Part I
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agents.gardener.session import GardenerSession, SessionPhase, SessionState

    from .plots import PlotState
    from .tending import TendingGesture


class GardenSeason(Enum):
    """
    The seasons of the garden.

    Unlike N-Phase (which is a development cycle), seasons describe
    the garden's *relationship to change*:

    - DORMANT: Garden is resting. Low entropy cost. Prompts are stable.
    - SPROUTING: New ideas emerging. Medium entropy. High plasticity.
    - BLOOMING: Ideas are crystallizing. Low plasticity. High visibility.
    - HARVEST: Time to gather and consolidate. Reflection-oriented.
    - COMPOSTING: Breaking down old patterns. High entropy tolerance.

    Seasons affect:
    - How aggressive TextGRAD improvements are
    - What kind of suggestions the Gardener offers
    - Visual representation (CLI/Web)
    - Entropy budget consumption rates
    """

    DORMANT = auto()
    SPROUTING = auto()
    BLOOMING = auto()
    HARVEST = auto()
    COMPOSTING = auto()

    @property
    def emoji(self) -> str:
        """Season emoji for display."""
        return {
            GardenSeason.DORMANT: "💤",
            GardenSeason.SPROUTING: "🌱",
            GardenSeason.BLOOMING: "🌸",
            GardenSeason.HARVEST: "🌾",
            GardenSeason.COMPOSTING: "🍂",
        }[self]

    @property
    def plasticity(self) -> float:
        """How much the garden accepts change (0-1)."""
        return {
            GardenSeason.DORMANT: 0.1,
            GardenSeason.SPROUTING: 0.9,
            GardenSeason.BLOOMING: 0.3,
            GardenSeason.HARVEST: 0.2,
            GardenSeason.COMPOSTING: 0.8,
        }[self]

    @property
    def entropy_multiplier(self) -> float:
        """How much entropy operations cost in this season."""
        return {
            GardenSeason.DORMANT: 0.5,  # Cheap to observe
            GardenSeason.SPROUTING: 1.5,  # Expensive to grow
            GardenSeason.BLOOMING: 1.0,  # Normal
            GardenSeason.HARVEST: 0.8,  # Efficient gathering
            GardenSeason.COMPOSTING: 2.0,  # Breaking down is hard
        }[self]


@dataclass
class GardenMetrics:
    """Observable metrics about the garden's health."""

    total_prompts: int = 0
    active_plots: int = 0
    recent_gestures: int = 0
    session_cycles: int = 0
    crystals_referenced: int = 0
    entropy_spent: float = 0.0
    entropy_budget: float = 1.0

    @property
    def health_score(self) -> float:
        """
        Overall garden health (0-1).

        Factors:
        - Plot activity (active plots / expected)
        - Gesture frequency (recent activity)
        - Entropy balance (budget remaining)
        - Session completion (cycles completed)
        """
        plot_factor = min(1.0, self.active_plots / 3) * 0.25
        gesture_factor = min(1.0, self.recent_gestures / 5) * 0.25
        entropy_factor = min(1.0, max(0, self.entropy_budget - self.entropy_spent)) * 0.25
        cycle_factor = min(1.0, self.session_cycles / 10) * 0.25

        return min(1.0, plot_factor + gesture_factor + entropy_factor + cycle_factor)


@dataclass
class GardenState:
    """
    The full state of the garden.

    The garden is the unified view of the development environment:
    - Session state from the GardenerSession polynomial
    - Prompt registry state from Prompt Logos
    - Memory context (relevant Brain crystals)
    - Current season
    - Named plots (focused regions)
    - Momentum (recent gestures)
    """

    # Identity
    garden_id: str = ""
    name: str = "Default Garden"
    created_at: datetime = field(default_factory=datetime.now)

    # Season (relationship to change)
    season: GardenSeason = GardenSeason.DORMANT
    season_since: datetime = field(default_factory=datetime.now)

    # Plots (named focus regions)
    plots: dict[str, "PlotState"] = field(default_factory=dict)
    active_plot: str | None = None

    # Embedded session (unified Phase 4)
    # The garden owns the session - session phases sync with garden seasons
    _session: "GardenerSession | None" = field(default=None, repr=False)

    # Session link ID (for persistence, separate from embedded session)
    session_id: str | None = None

    # Memory context (crystal IDs from Brain)
    memory_crystals: list[str] = field(default_factory=list)

    # Prompt registry state (simplified - full state in Prompt Logos)
    prompt_count: int = 0
    prompt_types: dict[str, int] = field(default_factory=dict)

    # Momentum (recent gestures for trajectory)
    recent_gestures: list["TendingGesture"] = field(default_factory=list)

    # Metrics
    metrics: GardenMetrics = field(default_factory=GardenMetrics)

    # Timing
    last_tended: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for persistence/API."""
        return {
            "garden_id": self.garden_id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "season": self.season.name,
            "season_since": self.season_since.isoformat(),
            "plots": {k: v.to_dict() for k, v in self.plots.items()},
            "active_plot": self.active_plot,
            "session_id": self.session_id,
            "memory_crystals": self.memory_crystals,
            "prompt_count": self.prompt_count,
            "prompt_types": self.prompt_types,
            "recent_gestures": [g.to_dict() for g in self.recent_gestures[-10:]],
            "last_tended": self.last_tended.isoformat(),
            "metrics": {
                "health_score": self.metrics.health_score,
                "total_prompts": self.metrics.total_prompts,
                "active_plots": self.metrics.active_plots,
                "entropy_spent": self.metrics.entropy_spent,
                "entropy_budget": self.metrics.entropy_budget,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GardenState":
        """Deserialize from persistence/API."""
        from .plots import PlotState
        from .tending import TendingGesture

        def parse_dt(val: str | None) -> datetime:
            if val:
                return datetime.fromisoformat(val)
            return datetime.now()

        plots = {k: PlotState.from_dict(v) for k, v in data.get("plots", {}).items()}
        gestures = [TendingGesture.from_dict(g) for g in data.get("recent_gestures", [])]

        metrics_data = data.get("metrics", {})
        metrics = GardenMetrics(
            total_prompts=metrics_data.get("total_prompts", 0),
            active_plots=metrics_data.get("active_plots", 0),
            entropy_spent=metrics_data.get("entropy_spent", 0.0),
            entropy_budget=metrics_data.get("entropy_budget", 1.0),
        )

        return cls(
            garden_id=data.get("garden_id", ""),
            name=data.get("name", "Default Garden"),
            created_at=parse_dt(data.get("created_at")),
            season=GardenSeason[data.get("season", "DORMANT")],
            season_since=parse_dt(data.get("season_since")),
            plots=plots,
            active_plot=data.get("active_plot"),
            session_id=data.get("session_id"),
            memory_crystals=data.get("memory_crystals", []),
            prompt_count=data.get("prompt_count", 0),
            prompt_types=data.get("prompt_types", {}),
            recent_gestures=gestures,
            metrics=metrics,
            last_tended=parse_dt(data.get("last_tended")),
        )

    def transition_season(
        self, new_season: GardenSeason, reason: str = "", emit_event: bool = True
    ) -> None:
        """
        Transition to a new season.

        Args:
            new_season: The season to transition to
            reason: Why the transition is happening
            emit_event: If True, emit a synergy event (async-safe via background task)
        """
        from .tending import TendingGesture, TendingVerb

        old_season = self.season
        self.season = new_season
        self.season_since = datetime.now()

        # Record as a gesture
        gesture = TendingGesture(
            verb=TendingVerb.ROTATE,
            target="concept.gardener.season",
            tone=0.8,
            reasoning=reason or f"Transitioned to {new_season.name}",
            entropy_cost=0.1,
        )
        self.add_gesture(gesture)

        # Emit synergy event if requested
        if emit_event:
            _emit_season_changed_event(
                garden_id=self.garden_id,
                garden_name=self.name,
                old_season=old_season.name,
                new_season=new_season.name,
                reason=reason or f"Transitioned to {new_season.name}",
            )

    def add_gesture(self, gesture: "TendingGesture") -> None:
        """Add a gesture to the momentum trace."""
        self.recent_gestures.append(gesture)
        self.last_tended = datetime.now()

        # Keep only last 50 gestures
        if len(self.recent_gestures) > 50:
            self.recent_gestures = self.recent_gestures[-50:]

        # Update metrics
        self.metrics.recent_gestures = len(
            [g for g in self.recent_gestures if g.is_recent(hours=24)]
        )
        self.metrics.entropy_spent += gesture.entropy_cost

    # =========================================================================
    # Session Integration (Phase 4 Unification)
    # =========================================================================

    @property
    def session(self) -> "GardenerSession | None":
        """Get the embedded session, if any."""
        return self._session

    @session.setter
    def session(self, value: "GardenerSession | None") -> None:
        """Set the embedded session."""
        self._session = value
        if value is not None:
            self.session_id = value.session_id

    def get_or_create_session(
        self,
        name: str | None = None,
        plan_path: str | None = None,
    ) -> "GardenerSession":
        """
        Get the active session or create a new one.

        If a session exists and is active, returns it.
        Otherwise, creates a new session linked to this garden.

        Args:
            name: Session name (defaults to garden name + timestamp)
            plan_path: Optional plan file path

        Returns:
            GardenerSession ready for use
        """
        from agents.gardener.session import create_gardener_session

        if self._session is not None:
            return self._session

        # Create session name
        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M")
            name = f"{self.name}-{timestamp}"

        # Create and link session
        session = create_gardener_session(
            name=name,
            plan_path=plan_path,
        )

        self._session = session
        self.session_id = session.session_id

        # If garden is DORMANT and we're creating a session, transition to SPROUTING
        if self.season == GardenSeason.DORMANT:
            self.transition_season(GardenSeason.SPROUTING, f"Session '{name}' started")

        return session

    async def on_session_phase_advance(
        self,
        old_phase: "SessionPhase",
        new_phase: "SessionPhase",
    ) -> GardenSeason | None:
        """
        React to session phase changes with potential garden season transitions.

        This implements the Phase → Season synergy described in the plan:
        - SENSE → ACT: Garden might transition DORMANT → SPROUTING
        - ACT → REFLECT: Garden might transition SPROUTING → BLOOMING
        - REFLECT → SENSE (cycle): Garden might stay or transition to HARVEST
        - Session complete: Garden transitions to HARVEST

        Args:
            old_phase: The phase before advancement
            new_phase: The phase after advancement

        Returns:
            The new season if a transition occurred, None otherwise
        """
        from agents.gardener.session import SessionPhase

        old_season = self.season
        new_season: GardenSeason | None = None

        # Phase transition logic
        if old_phase == SessionPhase.SENSE and new_phase == SessionPhase.ACT:
            # Ideas are forming - garden should be active
            if self.season == GardenSeason.DORMANT:
                new_season = GardenSeason.SPROUTING
                reason = "Session entered ACT phase - ideas forming"
            elif self.season == GardenSeason.COMPOSTING:
                # After composting, new work triggers sprouting
                new_season = GardenSeason.SPROUTING
                reason = "Fresh work after composting"

        elif old_phase == SessionPhase.ACT and new_phase == SessionPhase.REFLECT:
            # Work is crystallizing
            if self.season == GardenSeason.SPROUTING:
                new_season = GardenSeason.BLOOMING
                reason = "Session entered REFLECT phase - work crystallizing"

        elif old_phase == SessionPhase.REFLECT and new_phase == SessionPhase.SENSE:
            # Cycle complete - consider harvest if many cycles
            if self._session and self._session.state.reflect_count >= 3:
                if self.season == GardenSeason.BLOOMING:
                    new_season = GardenSeason.HARVEST
                    reason = f"Multiple cycles completed ({self._session.state.reflect_count})"

        # Apply transition if determined
        if new_season and new_season != old_season:
            self.transition_season(new_season, reason)
            return new_season

        return None

    async def on_session_complete(self) -> GardenSeason:
        """
        Handle session completion.

        Transitions garden to HARVEST season to gather learnings.

        Returns:
            The new season (HARVEST)
        """
        self.transition_season(GardenSeason.HARVEST, "Session completed - time to gather")

        # Clear the session reference (but keep session_id for history)
        self._session = None

        return GardenSeason.HARVEST

    def clear_session(self) -> None:
        """Clear the session reference without transitioning."""
        self._session = None


def create_garden(
    name: str = "Default Garden",
    season: GardenSeason = GardenSeason.DORMANT,
) -> GardenState:
    """
    Factory to create a new garden.

    Args:
        name: Human-readable garden name
        season: Initial season (default: DORMANT)

    Returns:
        Fresh GardenState ready for tending
    """
    import uuid

    return GardenState(
        garden_id=str(uuid.uuid4()),
        name=name,
        season=season,
        created_at=datetime.now(),
        season_since=datetime.now(),
    )


# =============================================================================
# Synergy Event Emission (Phase 6)
# =============================================================================


def _emit_season_changed_event(
    garden_id: str,
    garden_name: str,
    old_season: str,
    new_season: str,
    reason: str,
) -> None:
    """
    Emit a SEASON_CHANGED synergy event.

    This is called from the sync transition_season method, so we need
    to handle the async emission carefully. We use asyncio.create_task
    if there's a running event loop, otherwise we skip emission.
    """
    import asyncio

    try:
        from protocols.synergy import get_synergy_bus
        from protocols.synergy.events import create_season_changed_event

        event = create_season_changed_event(
            garden_id=garden_id,
            garden_name=garden_name,
            old_season=old_season,
            new_season=new_season,
            reason=reason,
        )

        # Try to emit if we have a running event loop
        try:
            loop = asyncio.get_running_loop()
            # Schedule emission in background (fire-and-forget)
            loop.create_task(get_synergy_bus().emit(event))
        except RuntimeError:
            # No running event loop - log and skip
            import logging

            logger = logging.getLogger("kgents.gardener.synergy")
            logger.debug(f"No event loop for season change emission: {old_season} → {new_season}")

    except ImportError:
        # Synergy module not available - skip silently
        pass


__all__ = [
    "GardenSeason",
    "GardenMetrics",
    "GardenState",
    "create_garden",
]
