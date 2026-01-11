"""
AGENTESE Nodes for Pilots and Endeavor Tangibility.

Exposes pilot registry and endeavor actualization via AGENTESE protocol.

AGENTESE Paths:
- self.tangibility.pilots        - Pilot discovery and introspection
- self.tangibility.endeavor      - Axiom discovery and pilot bootstrap

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

Example (HTTP):
    GET /agentese/self.tangibility.pilots:list
    POST /agentese/self.tangibility.endeavor:discover
    {"endeavor": "I want to build a daily journaling habit"}

Example (Python):
    >>> from protocols.agentese.logos import create_logos
    >>> logos = create_logos()
    >>> result = await logos.invoke("self.tangibility.pilots", umwelt, aspect="list")

Teaching:
    gotcha: The @node decorator with dependencies requires the provider
            to be registered in providers.py BEFORE import.

    gotcha: Endeavor discovery is stateful - sessions persist across turns.
            Use session_id to continue a discovery dialogue.

    gotcha: Fast discover bypasses the dialogue for programmatic use.
            Use for AI agents that already know the axioms.

See: docs/skills/metaphysical-fullstack.md, docs/skills/agentese-node-registration.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node
from services.pilots import (
    PilotMetadata,
    PilotRegistry,
    get_pilot_registry,
)

from .bootstrap import (
    CustomPilot,
    PilotBootstrapService,
    PilotMatch,
    WitnessConfig,
    get_pilot_bootstrap_service,
)
from .discovery import (
    AxiomDiscoveryService,
    DiscoverySession,
    DiscoveryTurn,
    EndeavorAxioms,
    get_axiom_discovery_service,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)


# =============================================================================
# Contracts
# =============================================================================


@dataclass(frozen=True)
class PilotsManifestResponse:
    """Response for pilots manifest."""

    total: int
    by_tier: dict[str, int]
    by_status: dict[str, int]
    pilots_root: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "pilots_manifest",
            "total": self.total,
            "by_tier": self.by_tier,
            "by_status": self.by_status,
            "pilots_root": self.pilots_root,
        }

    def to_text(self) -> str:
        lines = [
            "Pilots Registry",
            "=" * 40,
            f"Total pilots: {self.total}",
            "",
            "By tier:",
        ]
        for tier, count in self.by_tier.items():
            lines.append(f"  {tier}: {count}")
        lines.append("")
        lines.append("By status:")
        for status, count in self.by_status.items():
            lines.append(f"  {status}: {count}")
        return "\n".join(lines)


@dataclass(frozen=True)
class PilotListResponse:
    """Response for pilot list."""

    pilots: list[dict[str, Any]]
    total: int
    tier_filter: str | None
    status_filter: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "pilot_list",
            "pilots": self.pilots,
            "total": self.total,
            "tier_filter": self.tier_filter,
            "status_filter": self.status_filter,
        }


@dataclass(frozen=True)
class PilotDetailResponse:
    """Response for pilot detail."""

    pilot: dict[str, Any] | None
    found: bool
    spec_preview: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "pilot_detail",
            "pilot": self.pilot,
            "found": self.found,
            "spec_preview": self.spec_preview,
        }


@dataclass(frozen=True)
class DiscoveryStartResponse:
    """Response for discovery start."""

    session_id: str
    current_phase: str
    prompt: str
    raw_endeavor: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "discovery_start",
            "session_id": self.session_id,
            "current_phase": self.current_phase,
            "prompt": self.prompt,
            "raw_endeavor": self.raw_endeavor,
        }


@dataclass(frozen=True)
class DiscoveryTurnResponse:
    """Response for discovery turn."""

    turn_number: int
    phase: str
    prompt: str
    is_complete: bool
    axioms_so_far: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "discovery_turn",
            "turn_number": self.turn_number,
            "phase": self.phase,
            "prompt": self.prompt,
            "is_complete": self.is_complete,
            "axioms_so_far": self.axioms_so_far,
        }


@dataclass(frozen=True)
class AxiomsResponse:
    """Response for completed axioms."""

    axioms: dict[str, Any]
    is_complete: bool
    completeness: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "axioms",
            "axioms": self.axioms,
            "is_complete": self.is_complete,
            "completeness": self.completeness,
        }


@dataclass(frozen=True)
class MatchResponse:
    """Response for pilot match."""

    match: dict[str, Any] | None
    found: bool
    score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "match",
            "match": self.match,
            "found": self.found,
            "score": self.score,
        }


@dataclass(frozen=True)
class BootstrapResponse:
    """Response for pilot bootstrap."""

    pilot: dict[str, Any]
    witness_config: dict[str, Any]
    success: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "bootstrap",
            "pilot": self.pilot,
            "witness_config": self.witness_config,
            "success": self.success,
        }


# =============================================================================
# Renderings
# =============================================================================


@dataclass(frozen=True)
class PilotsManifestRendering:
    """Rendering for pilots manifest."""

    response: PilotsManifestResponse

    def to_dict(self) -> dict[str, Any]:
        return self.response.to_dict()

    def to_text(self) -> str:
        return self.response.to_text()


# =============================================================================
# PilotsNode
# =============================================================================


@node(
    "self.tangibility.pilots",
    description="Pilots Registry - Discover and introspect tangible endeavor pilots",
    dependencies=("pilot_registry",),
    contracts={
        "manifest": Response(PilotsManifestResponse),
        "list": Response(PilotListResponse),
        "get": Response(PilotDetailResponse),
        "spec": Response(dict),
    },
    examples=[
        ("list", {}, "List all pilots"),
        ("list", {"tier": "core"}, "List core pilots only"),
        ("get", {"name": "trail-to-crystal-daily-lab"}, "Get pilot details"),
        ("spec", {"name": "wasm-survivors-game"}, "Get PROTO_SPEC content"),
    ],
)
class PilotsNode(BaseLogosNode):
    """
    AGENTESE node for Pilots Registry.

    Provides universal access to pilot discovery:
    - CLI: kg tangibility pilots list
    - HTTP: GET /agentese/self.tangibility.pilots:list
    - WebSocket: {"path": "self.tangibility.pilots", "aspect": "list"}

    AI Agent Usage:
        # List all pilots
        result = await logos.invoke(
            "self.tangibility.pilots",
            observer,
            aspect="list"
        )

        # Get specific pilot
        result = await logos.invoke(
            "self.tangibility.pilots",
            observer,
            aspect="get",
            name="trail-to-crystal-daily-lab"
        )
    """

    def __init__(self, pilot_registry: PilotRegistry | None = None) -> None:
        """
        Initialize with injected dependency.

        Args:
            pilot_registry: PilotRegistry instance (injected by container)
        """
        self._registry = pilot_registry or get_pilot_registry()

    @property
    def handle(self) -> str:
        """The AGENTESE path to this node."""
        return "self.tangibility.pilots"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        # All archetypes can read pilots
        return ("list", "get", "spec")

    async def manifest(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        Show pilots registry status.

        AGENTESE: self.tangibility.pilots.manifest
        """
        stats = self._registry.stats()
        response = PilotsManifestResponse(
            total=stats["total"],
            by_tier=stats["by_tier"],
            by_status=stats["by_status"],
            pilots_root=stats["pilots_root"],
        )
        return PilotsManifestRendering(response=response)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to registry methods."""
        match aspect:
            case "list":
                tier = kwargs.get("tier")
                status = kwargs.get("status")
                pilots = await self._registry.list_pilots(tier=tier, status=status)
                return PilotListResponse(
                    pilots=[p.to_dict() for p in pilots],
                    total=len(pilots),
                    tier_filter=tier,
                    status_filter=status,
                ).to_dict()

            case "get":
                name = kwargs.get("name", "")
                pilot = await self._registry.get_pilot(name)
                spec_preview = None
                if pilot:
                    spec = await self._registry.get_pilot_spec(name)
                    if spec:
                        spec_preview = spec[:500] + "..." if len(spec) > 500 else spec
                return PilotDetailResponse(
                    pilot=pilot.to_dict() if pilot else None,
                    found=pilot is not None,
                    spec_preview=spec_preview,
                ).to_dict()

            case "spec":
                name = kwargs.get("name", "")
                spec = await self._registry.get_pilot_spec(name)
                return {
                    "name": name,
                    "spec": spec,
                    "found": spec is not None,
                }

            case _:
                return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# EndeavorNode
# =============================================================================


@node(
    "self.tangibility.endeavor",
    description="Endeavor Actualization - Axiom discovery and pilot bootstrap",
    dependencies=("axiom_discovery_service", "pilot_bootstrap_service"),
    contracts={
        "discover": Contract(dict, DiscoveryStartResponse),
        "turn": Contract(dict, DiscoveryTurnResponse),
        "complete": Response(AxiomsResponse),
        "fast_discover": Contract(dict, AxiomsResponse),
        "match": Contract(dict, MatchResponse),
        "bootstrap": Contract(dict, BootstrapResponse),
    },
    examples=[
        ("discover", {"endeavor": "I want to build a daily journaling habit"}, "Start discovery"),
        ("turn", {"session_id": "...", "response": "I want to feel present"}, "Continue dialogue"),
        ("match", {"axioms": {}}, "Match axioms to existing pilot"),
        ("bootstrap", {"axioms": {}, "name": "My Daily Lab"}, "Create custom pilot"),
    ],
)
class EndeavorNode(BaseLogosNode):
    """
    AGENTESE node for Endeavor Actualization.

    Provides:
    - Axiom discovery dialogue (discover, turn, complete)
    - Fast axiom creation for programmatic use
    - Pilot matching from axioms
    - Custom pilot bootstrap

    AI Agent Usage:
        # Start discovery
        result = await logos.invoke(
            "self.tangibility.endeavor",
            observer,
            aspect="discover",
            endeavor="I want to build better habits"
        )

        # Process turn
        result = await logos.invoke(
            "self.tangibility.endeavor",
            observer,
            aspect="turn",
            session_id=result["session_id"],
            response="I want to feel accomplished"
        )

        # Fast discover (skip dialogue)
        result = await logos.invoke(
            "self.tangibility.endeavor",
            observer,
            aspect="fast_discover",
            endeavor="Daily journaling",
            success="Write one entry per day",
            feeling="Present and reflective",
            constraints=["Under 10 minutes"],
            verification="Week of entries visible"
        )

        # Match to existing pilot
        result = await logos.invoke(
            "self.tangibility.endeavor",
            observer,
            aspect="match",
            axioms=axioms_dict
        )

        # Bootstrap custom pilot
        result = await logos.invoke(
            "self.tangibility.endeavor",
            observer,
            aspect="bootstrap",
            axioms=axioms_dict,
            name="My Daily Lab"
        )
    """

    def __init__(
        self,
        axiom_discovery_service: AxiomDiscoveryService | None = None,
        pilot_bootstrap_service: PilotBootstrapService | None = None,
    ) -> None:
        """
        Initialize with injected dependencies.

        Args:
            axiom_discovery_service: AxiomDiscoveryService instance
            pilot_bootstrap_service: PilotBootstrapService instance
        """
        self._discovery = axiom_discovery_service or get_axiom_discovery_service()
        self._bootstrap = pilot_bootstrap_service or get_pilot_bootstrap_service()

    @property
    def handle(self) -> str:
        """The AGENTESE path to this node."""
        return "self.tangibility.endeavor"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        archetype_lower = archetype.lower() if archetype else "guest"

        # All authenticated users can discover and match
        base = ("discover", "turn", "complete", "fast_discover", "match")

        # Only developers can bootstrap (creates resources)
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return base + ("bootstrap",)

        return base

    async def manifest(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        Show endeavor service status.

        AGENTESE: self.tangibility.endeavor.manifest
        """
        from protocols.agentese.node import BasicRendering

        discovery_stats = self._discovery.stats()
        bootstrap_stats = self._bootstrap.stats()

        return BasicRendering(
            summary="Endeavor Actualization Service",
            content=(
                f"Discovery sessions: {discovery_stats['total_sessions']} "
                f"(active: {discovery_stats['active_sessions']})\n"
                f"Custom pilots: {bootstrap_stats['custom_pilots']}"
            ),
            metadata={
                "discovery": discovery_stats,
                "bootstrap": bootstrap_stats,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to service methods."""
        match aspect:
            case "discover":
                endeavor = kwargs.get("endeavor", "")
                session = await self._discovery.start_discovery(endeavor)
                first_turn = session.turns[0]
                return DiscoveryStartResponse(
                    session_id=session.session_id,
                    current_phase=session.current_phase.value,
                    prompt=first_turn.prompt,
                    raw_endeavor=session.raw_endeavor,
                ).to_dict()

            case "turn":
                session_id = kwargs.get("session_id", "")
                response = kwargs.get("response", "")
                try:
                    turn = await self._discovery.process_turn(session_id, response)
                    session_state = await self._discovery.get_session(session_id)
                    return DiscoveryTurnResponse(
                        turn_number=turn.turn_number,
                        phase=turn.phase.value,
                        prompt=turn.prompt,
                        is_complete=turn.phase.value == "complete",
                        axioms_so_far=session_state.axioms if session_state else {},
                    ).to_dict()
                except ValueError as e:
                    return {"error": str(e)}

            case "complete":
                session_id = kwargs.get("session_id", "")
                try:
                    axioms = await self._discovery.complete_discovery(session_id)
                    return AxiomsResponse(
                        axioms=axioms.to_dict(),
                        is_complete=axioms.is_complete(),
                        completeness=axioms.completeness_score(),
                    ).to_dict()
                except ValueError as e:
                    return {"error": str(e)}

            case "fast_discover":
                axioms = await self._discovery.fast_discover(
                    endeavor=kwargs.get("endeavor", ""),
                    success=kwargs.get("success", ""),
                    feeling=kwargs.get("feeling", ""),
                    constraints=kwargs.get("constraints", []),
                    verification=kwargs.get("verification", ""),
                )
                return AxiomsResponse(
                    axioms=axioms.to_dict(),
                    is_complete=axioms.is_complete(),
                    completeness=axioms.completeness_score(),
                ).to_dict()

            case "match":
                axioms_dict = kwargs.get("axioms", {})
                axioms = EndeavorAxioms.from_dict(axioms_dict)
                match = await self._bootstrap.match_pilot(axioms)
                return MatchResponse(
                    match=match.to_dict() if match else None,
                    found=match is not None,
                    score=match.score if match else 0.0,
                ).to_dict()

            case "bootstrap":
                axioms_dict = kwargs.get("axioms", {})
                name = kwargs.get("name", "custom-pilot")
                based_on = kwargs.get("based_on")

                axioms = EndeavorAxioms.from_dict(axioms_dict)
                pilot = await self._bootstrap.bootstrap_pilot(
                    axioms=axioms,
                    name=name,
                    based_on=based_on,
                )
                config = await self._bootstrap.setup_witness_infrastructure(pilot)

                return BootstrapResponse(
                    pilot=pilot.to_dict(),
                    witness_config=config.to_dict(),
                    success=True,
                ).to_dict()

            case _:
                return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "PilotsNode",
    "EndeavorNode",
    "PilotsManifestResponse",
    "PilotListResponse",
    "PilotDetailResponse",
    "DiscoveryStartResponse",
    "DiscoveryTurnResponse",
    "AxiomsResponse",
    "MatchResponse",
    "BootstrapResponse",
]
