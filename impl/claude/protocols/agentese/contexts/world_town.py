"""
AGENTESE Town Context: Agent Town Crown Jewel Integration.

The world.town context provides access to Agent Town simulation:
- world.town.manifest - Show town status and citizen activity
- world.town.citizen.<name>.* - Individual citizen interface (see town_citizen.py)
- world.town.step - Advance simulation
- world.town.witness - View activity history
- world.town.start - Start a new simulation
- world.town.observe - MESA view (town overview)

This module defines TownNode which handles town-level operations.
Citizen-level operations are delegated to TownCitizenNode.

AGENTESE: world.town.*

Principle Alignment:
- Ethical: Citizens can refuse interaction (Right to Rest)
- Joy-Inducing: Emergent narratives from citizen interactions
- Composable: Town is an operad composition of citizens
- Heterarchical: Citizens are in flux, not fixed hierarchy
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable

if TYPE_CHECKING:
    from agents.town.environment import TownEnvironment
    from agents.town.flux import TownFlux
    from bootstrap.umwelt import Umwelt

    from .town_citizen import TownCitizenNode, TownCitizenResolver


# Town affordances available at world.town.*
TOWN_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "observe",
    "witness",
    "start",
    "step",
    "metrics",
    "budget",
    "citizen",
    "demo",
    "chat",
)


# =============================================================================
# TownNode
# =============================================================================


@dataclass
class TownNode(BaseLogosNode):
    """
    world.town - Agent Town simulation interface.

    The Town Crown Jewel provides:
    - Town-level operations (start, step, observe)
    - Citizen resolution for world.town.citizen.<name>.*
    - Emergence metrics tracking
    - Chat with individual citizens (via citizen resolver)

    Storage:
    - In-memory simulation state (TownEnvironment, TownFlux)
    - services/town/persistence.py for database persistence
    """

    _handle: str = "world.town"

    # Simulation state (in-memory)
    _environment: "TownEnvironment | None" = None
    _flux: "TownFlux | None" = None

    # Citizen resolver for dynamic citizen paths
    _citizen_resolver: "TownCitizenResolver | None" = None

    @property
    def handle(self) -> str:
        return self._handle

    @property
    def environment(self) -> "TownEnvironment | None":
        return self._environment

    @property
    def flux(self) -> "TownFlux | None":
        return self._flux

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Town affordances - mostly available to all archetypes."""
        return TOWN_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("town_state")],
        help="Show town status and citizen activity",
        examples=["kg town", "kg town status"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show town status."""
        if self._environment is None:
            return BasicRendering(
                summary="Agent Town: Not Running",
                content=("No simulation running.\nUse 'kg town start' to begin a new simulation."),
                metadata={"status": "not_running"},
            )

        env = self._environment
        status = self._flux.get_status() if self._flux else {}

        return BasicRendering(
            summary=f"Agent Town: {env.name}",
            content=(
                f"Name: {env.name}\n"
                f"Day: {status.get('day', 1)} / Phase: {status.get('phase', 'IDLE')}\n"
                f"Citizens: {len(env.citizens)} ({', '.join(c.name for c in env.citizens.values())})\n"
                f"Regions: {len(env.regions)} ({', '.join(env.regions.keys())})\n"
                f"Tension: {env.tension_index():.3f}\n"
                f"Cooperation: {env.cooperation_level():.2f}"
            ),
            metadata={
                "status": "running",
                "name": env.name,
                "day": status.get("day", 1),
                "phase": status.get("phase", "IDLE"),
                "citizen_count": len(env.citizens),
                "citizens": [c.name for c in env.citizens.values()],
                "region_count": len(env.regions),
                "regions": list(env.regions.keys()),
                "tension": env.tension_index(),
                "cooperation": env.cooperation_level(),
                "tokens": status.get("total_tokens", 0),
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("town_state")],
        help="Show MESA view (town overview with citizens by region)",
        examples=["kg town observe"],
    )
    async def observe(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Show MESA view - citizens by region."""
        if self._environment is None:
            return await self.manifest(observer)

        env = self._environment
        lines = []

        # Header
        lines.append("=" * 60)
        lines.append(f"  AGENT TOWN: {env.name}")
        if self._flux:
            status = self._flux.get_status()
            lines.append(f"  Day {status['day']} / {status['phase']}")
        lines.append("=" * 60)

        # Regions with citizens
        for region_name, region in env.regions.items():
            citizens_here = env.get_citizens_in_region(region_name)
            density = env.density_at(region_name)

            lines.append(f"\n  [{region_name.upper()}] ({density:.0%} density)")
            lines.append(f"    {region.description}")

            if citizens_here:
                for c in citizens_here:
                    phase_icon = _phase_icon(c.phase.name)
                    lines.append(f"    {phase_icon} {c.name} ({c.archetype})")
            else:
                lines.append("    (empty)")

        # Metrics
        lines.append("\n" + "-" * 60)
        tension = env.tension_index()
        coop = env.cooperation_level()
        lines.append(
            f"  TENSION: {tension:.2f}  COOPERATION: {coop:.2f}  TOKENS: {env.total_token_spend}"
        )
        lines.append("=" * 60)

        return BasicRendering(
            summary=f"MESA View: {env.name}",
            content="\n".join(lines),
            metadata={
                "view": "mesa",
                "citizen_count": len(env.citizens),
                "region_count": len(env.regions),
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("town_state")],
        help="View activity history and recent events",
        examples=["kg town witness"],
    )
    async def witness(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View activity history."""
        if self._environment is None:
            return await self.manifest(observer)

        env = self._environment
        lines = ["[WITNESS] Town Activity Report", "=" * 50]

        # Simulation status
        if self._flux:
            status = self._flux.get_status()
            lines.append(f"  Day {status['day']} - {status['phase']}")
            lines.append(f"  Total events: {status['total_events']}")

        # Citizen activities
        lines.append("\n  Citizen Status:")
        for citizen in env.citizens.values():
            phase_icon = _phase_icon(citizen.phase.name)
            lines.append(
                f"    {phase_icon} {citizen.name} ({citizen.archetype}) @ {citizen.region}"
            )

            # Show relationships
            if citizen.relationships:
                top_rel = sorted(
                    citizen.relationships.items(), key=lambda x: abs(x[1]), reverse=True
                )[:2]
                for other_id, weight in top_rel:
                    other = env.get_citizen_by_id(other_id)
                    other_name = other.name if other else other_id[:6]
                    rel_type = "friendly with" if weight > 0.3 else "neutral toward"
                    if weight < -0.3:
                        rel_type = "tense with"
                    lines.append(f"       - {rel_type} {other_name}")

        # Emergence metrics
        lines.append("\n  Emergence Metrics:")
        lines.append(f"    Tension: {env.tension_index():.3f}")
        lines.append(f"    Cooperation: {env.cooperation_level():.2f}")
        lines.append(f"    Accursed Surplus: {env.total_accursed_surplus():.2f}")

        lines.append("=" * 50)

        return BasicRendering(
            summary="Town Activity Report",
            content="\n".join(lines),
            metadata={"view": "witness"},
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("town_state")],
        help="Start a new Agent Town simulation",
        examples=["kg town start", "kg town start --phase2"],
    )
    async def start(
        self,
        observer: "Umwelt[Any, Any]",
        phase2: bool = False,
        seed: int | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Start a new simulation."""
        # Lazy import to avoid circular dependencies
        from agents.town.environment import (
            create_mpp_environment,
            create_phase2_environment,
        )
        from agents.town.flux import TownFlux

        # Check if already running
        if self._environment is not None:
            return BasicRendering(
                summary="Town Already Running",
                content=(
                    f"Simulation '{self._environment.name}' already running.\n"
                    "Use 'kg town step' to advance."
                ),
                metadata={"status": "already_running"},
            )

        # Create environment
        if phase2:
            self._environment = create_phase2_environment()
        else:
            self._environment = create_mpp_environment()

        # Create flux
        self._flux = TownFlux(self._environment, seed=seed)

        # Initialize citizen resolver
        self._init_citizen_resolver()

        return BasicRendering(
            summary=f"Town Started: {self._environment.name}",
            content=(
                f"Agent Town '{self._environment.name}' initialized.\n"
                f"Citizens: {', '.join(c.name for c in self._environment.citizens.values())}\n"
                f"Regions: {', '.join(self._environment.regions.keys())}\n\n"
                "Use 'kg town step' to advance the simulation."
            ),
            metadata={
                "status": "started",
                "name": self._environment.name,
                "citizens": [c.name for c in self._environment.citizens.values()],
                "regions": list(self._environment.regions.keys()),
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("town_state")],
        help="Advance simulation by one phase",
        examples=["kg town step"],
    )
    async def step(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Advance simulation by one phase."""
        if self._flux is None:
            return BasicRendering(
                summary="No Simulation",
                content="No simulation running. Use 'kg town start' first.",
                metadata={"status": "not_running"},
            )

        # Run the step
        events = []
        async for event in self._flux.step():
            events.append(event)

        # Build output
        status = self._flux.get_status()
        lines = [
            f"\n[TOWN] Day {status['day']} - {status['phase']}",
            "=" * 50,
        ]

        for event in events:
            icon = "+" if event.success else "x"
            participants_str = ", ".join(event.participants)
            lines.append(f"  {icon} [{event.operation.upper()}] {event.message}")
            lines.append(f"    Participants: {participants_str}")
            lines.append(f"    Tokens: {event.tokens_used}, Drama: {event.drama_contribution:.2f}")

        lines.append("\n[METRICS]")
        lines.append(f"  Tension Index: {status['tension_index']:.4f}")
        lines.append(f"  Cooperation Level: {status['cooperation_level']:.2f}")
        lines.append(f"  Total Tokens: {status['total_tokens']}")

        return BasicRendering(
            summary=f"Day {status['day']} - {status['phase']}",
            content="\n".join(lines),
            metadata={
                "status": "stepped",
                "day": status["day"],
                "phase": status["phase"],
                "events": [e.to_dict() for e in events],
                "tension": status["tension_index"],
                "cooperation": status["cooperation_level"],
                "tokens": status["total_tokens"],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("town_state")],
        help="Show emergence metrics",
        examples=["kg town metrics"],
    )
    async def metrics(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Show emergence metrics."""
        if self._environment is None:
            return await self.manifest(observer)

        env = self._environment

        tension = env.tension_index()
        coop = env.cooperation_level()
        surplus = env.total_accursed_surplus()

        lines = [
            "[METRICS] Agent Town Emergence Metrics",
            "=" * 50,
            f"  Tension Index:     {tension:.4f}  {'(HIGH DRAMA!)' if tension > 0.7 else ''}",
            f"  Cooperation Level: {coop:.2f}",
            f"  Accursed Surplus:  {surplus:.2f}  {'(NEEDS EXPENDITURE!)' if surplus > 10 else ''}",
        ]

        if self._flux:
            status = self._flux.get_status()
            lines.append(f"\n  Total Events:      {status['total_events']}")
            lines.append(f"  Total Tokens:      {status['total_tokens']}")

        lines.append("=" * 50)

        return BasicRendering(
            summary="Emergence Metrics",
            content="\n".join(lines),
            metadata={
                "tension": tension,
                "cooperation": coop,
                "surplus": surplus,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("town_state")],
        help="Show token budget status",
        examples=["kg town budget"],
    )
    async def budget(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Show budget status."""
        if self._environment is None:
            return await self.manifest(observer)

        env = self._environment
        monthly_cap = 1_000_000  # MPP budget
        spent = env.total_token_spend
        pct = (spent / monthly_cap) * 100 if monthly_cap > 0 else 0

        lines = [
            "[BUDGET] Agent Town Token Budget",
            "=" * 50,
            f"  Monthly Cap:       {monthly_cap:,} tokens",
            f"  Spent This Session: {spent:,} tokens ({pct:.1f}%)",
        ]

        if self._flux:
            status = self._flux.get_status()
            daily_avg = spent / max(1, status["day"])
            projected = daily_avg * 30
            lines.append(f"  Daily Average:     {daily_avg:,.0f} tokens")
            lines.append(f"  Projected Monthly: {projected:,.0f} tokens")

            budget_status = "ON BUDGET" if projected < monthly_cap else "OVER BUDGET"
            lines.append(f"\n  Status: {budget_status}")

        lines.append("=" * 50)

        return BasicRendering(
            summary="Token Budget",
            content="\n".join(lines),
            metadata={
                "monthly_cap": monthly_cap,
                "spent": spent,
                "percent": pct,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle town-specific aspects."""
        match aspect:
            case "observe":
                return await self.observe(observer, **kwargs)
            case "witness":
                return await self.witness(observer, **kwargs)
            case "start":
                return await self.start(observer, **kwargs)
            case "step":
                return await self.step(observer, **kwargs)
            case "metrics":
                return await self.metrics(observer, **kwargs)
            case "budget":
                return await self.budget(observer, **kwargs)
            case "citizen":
                # Return citizen resolver for path chaining
                return self._get_citizen_resolver()
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    def _init_citizen_resolver(self) -> None:
        """Initialize citizen resolver from environment."""
        if self._environment is None:
            return

        from .town_citizen import TownCitizenResolver

        self._citizen_resolver = TownCitizenResolver(
            _citizen_lookup=self._environment.get_citizen_by_name
        )

        # Pre-populate with existing citizens
        for citizen in self._environment.citizens.values():
            self._citizen_resolver.resolve(citizen.name, citizen)

    def _get_citizen_resolver(self) -> "TownCitizenResolver | None":
        """Get or create citizen resolver."""
        if self._citizen_resolver is None:
            self._init_citizen_resolver()
        return self._citizen_resolver

    def resolve_citizen(self, name: str) -> "TownCitizenNode | None":
        """
        Resolve a citizen by name.

        Used by Logos for path resolution:
        world.town.citizen.elara.manifest -> TownCitizenNode.manifest
        """
        resolver = self._get_citizen_resolver()
        if resolver is None:
            return None

        citizen = None
        if self._environment:
            citizen = self._environment.get_citizen_by_name(name)

        return resolver.resolve(name, citizen)


# =============================================================================
# Helpers
# =============================================================================


def _phase_icon(phase: str) -> str:
    """Get an icon for a citizen phase."""
    icons = {
        "IDLE": ".",
        "SOCIALIZING": "*",
        "WORKING": "#",
        "REFLECTING": "~",
        "RESTING": "z",
    }
    return icons.get(phase, "?")


# =============================================================================
# Factory Functions
# =============================================================================

# Global singleton for TownNode
_town_node: TownNode | None = None


def get_town_node() -> TownNode:
    """Get the global TownNode singleton."""
    global _town_node
    if _town_node is None:
        _town_node = TownNode()
    return _town_node


def set_town_node(node: TownNode) -> None:
    """Set the global TownNode singleton (for testing)."""
    global _town_node
    _town_node = node


def create_town_node(
    environment: "TownEnvironment | None" = None,
    flux: "TownFlux | None" = None,
) -> TownNode:
    """
    Create a TownNode with optional environment/flux injection.

    Args:
        environment: Pre-created environment
        flux: Pre-created flux

    Returns:
        Configured TownNode
    """
    node = TownNode(
        _environment=environment,
        _flux=flux,
    )
    if environment:
        node._init_citizen_resolver()
    return node


__all__ = [
    # Constants
    "TOWN_AFFORDANCES",
    # Node
    "TownNode",
    # Factory
    "get_town_node",
    "set_town_node",
    "create_town_node",
]
