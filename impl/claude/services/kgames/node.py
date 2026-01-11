"""
KGames AGENTESE Node: @node("self.tangibility.kgames")

Exposes the KGames kernel and operad via AGENTESE for game generation
and verification from axioms.

AGENTESE Paths:
- self.tangibility.kgames.manifest     - Overview of kgames service
- self.tangibility.kgames.kernel       - View the four axioms
- self.tangibility.kgames.operad       - View composition grammar
- self.tangibility.kgames.generate     - Generate game spec from axioms + theme
- self.tangibility.kgames.verify       - Verify implementation against axioms

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

Philosophy:
    "Games are theorems in the KGAMES kernel.
     Generation is proof search. Verification is proof checking."

See: docs/skills/metaphysical-fullstack.md
See: spec/agents/kgames-kernel.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.affordances import AspectCategory, aspect
from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .kernel import (
    AgencyAxiom,
    AttributionAxiom,
    CompositionAxiom,
    GameImplementation,
    GameKernel,
    MasteryAxiom,
    ValidationResult,
    create_kernel,
)
from .operad import (
    GAME_OPERAD,
    Mechanic,
    get_mechanic,
    list_mechanics,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)


# =============================================================================
# Renderings
# =============================================================================


@dataclass(frozen=True)
class KernelRendering:
    """Rendering for the GameKernel."""

    kernel: GameKernel

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "kgames_kernel",
            **self.kernel.to_dict(),
        }

    def to_text(self) -> str:
        return self.kernel.to_text()


@dataclass(frozen=True)
class OperadRendering:
    """Rendering for the GameOperad."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "kgames_operad",
            "name": GAME_OPERAD.name,
            "description": GAME_OPERAD.description,
            "operations": {
                name: {
                    "name": op.name,
                    "arity": op.arity,
                    "signature": op.signature,
                    "description": op.description,
                }
                for name, op in GAME_OPERAD.operations.items()
            },
            "laws": [
                {
                    "name": law.name,
                    "equation": law.equation,
                    "description": law.description,
                }
                for law in GAME_OPERAD.laws
            ],
            "mechanics": [m.to_dict() for m in list_mechanics()],
        }

    def to_text(self) -> str:
        lines = [
            f"=== {GAME_OPERAD.name} ===",
            GAME_OPERAD.description or "",
            "",
            "Operations:",
        ]
        for name, op in GAME_OPERAD.operations.items():
            lines.append(f"  {name}: {op.signature}")
            lines.append(f"    {op.description}")
        lines.append("")
        lines.append("Laws:")
        for law in GAME_OPERAD.laws:
            lines.append(f"  {law.name}: {law.equation}")
        lines.append("")
        lines.append("Predefined Mechanics:")
        for m in list_mechanics():
            lines.append(f"  {m.name} ({m.category}): {m.description}")
        return "\n".join(lines)


@dataclass(frozen=True)
class ValidationRendering:
    """Rendering for a validation result."""

    result: ValidationResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "kgames_validation",
            **self.result.to_dict(),
        }

    def to_text(self) -> str:
        return self.result.to_text()


@dataclass(frozen=True)
class GameSpecRendering:
    """Rendering for a generated game spec."""

    spec: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "kgames_spec",
            **self.spec,
        }

    def to_text(self) -> str:
        lines = [
            "=== GENERATED GAME SPEC ===",
            f"Title: {self.spec.get('title', 'Untitled')}",
            f"Theme: {self.spec.get('theme', 'Unknown')}",
            "",
            "Axiom Integration:",
        ]
        for axiom_id, impl in self.spec.get("axiom_integration", {}).items():
            lines.append(f"  {axiom_id}: {impl}")
        lines.append("")
        lines.append("Core Mechanics:")
        for m in self.spec.get("mechanics", []):
            lines.append(f"  - {m}")
        lines.append("")
        lines.append("Witness Integration:")
        for k, v in self.spec.get("witness_integration", {}).items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)


# =============================================================================
# Mock Implementation for Testing
# =============================================================================


class MockGameImplementation:
    """
    Mock implementation for testing axiom validation.

    Provides configurable death contexts, skill metrics, and arc history.
    """

    def __init__(
        self,
        death_contexts: list[dict[str, Any]] | None = None,
        skill_metrics: list[dict[str, Any]] | None = None,
        arc_history: dict[str, Any] | None = None,
    ):
        self._death_contexts = death_contexts or []
        self._skill_metrics = skill_metrics or []
        self._arc_history = arc_history or {
            "phases": ["POWER", "FLOW", "CRISIS"],
            "hasDefiniteClosure": True,
            "closureType": "dignity",
        }

    def get_death_contexts(self) -> list[dict[str, Any]]:
        return self._death_contexts

    def get_skill_metrics(self) -> list[dict[str, Any]]:
        return self._skill_metrics

    def get_arc_history(self) -> dict[str, Any]:
        return self._arc_history


# =============================================================================
# KGamesNode
# =============================================================================


@node(
    "self.tangibility.kgames",
    description="KGames - Game generation and verification from axioms",
    dependencies=(),
    contracts={
        # Perception aspects
        "manifest": Response(dict),
        "kernel": Response(dict),
        "operad": Response(dict),
        # Generation aspects
        "generate": Response(dict),
        # Verification aspects
        "verify": Response(dict),
    },
    examples=[
        ("kernel", {}, "View the four game axioms (A1-A4)"),
        ("operad", {}, "View the game mechanic composition grammar"),
        ("generate", {"theme": "hornet_siege"}, "Generate game spec from theme"),
        ("verify", {"death_count": 1, "has_causal_chain": True}, "Verify implementation"),
    ],
)
class KGamesNode(BaseLogosNode):
    """
    AGENTESE node for KGames service.

    Exposes the GameKernel and GameOperad through the universal protocol.
    Enables AI agents to generate and verify game specifications.

    The Four Axioms (from wasm-survivors):
    - A1: AGENCY (L=0.02) - Player choices determine outcomes
    - A2: ATTRIBUTION (L=0.05) - Outcomes trace to identifiable causes
    - A3: MASTERY (L=0.08) - Skill development is externally observable
    - A4: COMPOSITION (L=0.03) - Moments compose algebraically into arcs

    Example:
        # Via AGENTESE gateway
        GET /agentese/self/tangibility/kgames/kernel

        # Via Logos directly
        await logos.invoke("self.tangibility.kgames.kernel", observer)

        # Via CLI
        kg kgames kernel
    """

    def __init__(self) -> None:
        """Initialize KGamesNode with the GameKernel."""
        self._kernel = create_kernel()

    @property
    def handle(self) -> str:
        return "self.tangibility.kgames"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        All archetypes can view kernel and operad.
        Generation and verification require higher trust.
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Base affordances for all
        base = ("kernel", "operad")

        # Developers get full access
        if archetype_lower in ("developer", "operator", "admin", "system", "architect"):
            return base + ("generate", "verify")

        # Guests can only view
        return base

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="View KGames service overview",
        examples=["self.tangibility.kgames.manifest"],
    )
    async def manifest(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        Manifest KGames service overview.

        AGENTESE: self.tangibility.kgames.manifest
        """
        return BasicRendering(
            summary="KGames: Game Generation from Axioms",
            content=(
                "The KGames service enables game generation and verification "
                "using the four constitutional axioms discovered through wasm-survivors.\n\n"
                "Axioms:\n"
                "- A1: AGENCY (L=0.02) - Player choices determine outcomes\n"
                "- A2: ATTRIBUTION (L=0.05) - Outcomes trace to causes\n"
                "- A3: MASTERY (L=0.08) - Skill development is observable\n"
                "- A4: COMPOSITION (L=0.03) - Moments compose into arcs\n\n"
                "Use 'kernel' to view axioms, 'operad' to view composition grammar, "
                "'generate' to create a game spec, 'verify' to validate an implementation."
            ),
            metadata={
                "axiom_count": 4,
                "operation_count": len(GAME_OPERAD.operations),
                "mechanic_count": len(list_mechanics()),
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="View the four game axioms",
        examples=["self.tangibility.kgames.kernel"],
    )
    async def kernel(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        axiom: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        View the GameKernel with its four axioms.

        Args:
            axiom: Optional specific axiom ID (A1, A2, A3, A4)

        Returns:
            Kernel or specific axiom information
        """
        if axiom:
            ax = self._kernel.get_axiom(axiom)
            if ax:
                return ax.to_dict()
            return {"error": f"Unknown axiom: {axiom}. Valid: A1, A2, A3, A4"}

        return KernelRendering(kernel=self._kernel).to_dict()

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="View the game mechanic composition grammar",
        examples=["self.tangibility.kgames.operad"],
    )
    async def operad(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        mechanic: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        View the GameOperad composition grammar.

        Args:
            mechanic: Optional specific mechanic name to view

        Returns:
            Operad or specific mechanic information
        """
        if mechanic:
            m = get_mechanic(mechanic)
            if m:
                return m.to_dict()
            return {
                "error": f"Unknown mechanic: {mechanic}",
                "available": [m.name for m in list_mechanics()],
            }

        return OperadRendering().to_dict()

    @aspect(
        category=AspectCategory.MUTATION,
        help="Generate a game spec from axioms and theme",
        examples=[
            "self.tangibility.kgames.generate[theme=hornet_siege]",
            "self.tangibility.kgames.generate[theme=tower_defense]",
        ],
    )
    async def generate(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        theme: str = "default",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate a game specification from axioms and theme.

        This creates a blueprint for a game that satisfies all four axioms.
        The spec includes axiom integration points and core mechanics.

        Args:
            theme: The game theme (e.g., "hornet_siege", "tower_defense")

        Returns:
            Generated game specification
        """
        # Generate a spec that explicitly addresses each axiom
        spec = {
            "title": f"{theme.replace('_', ' ').title()} Game",
            "theme": theme,
            "axiom_integration": {
                "A1": "Every death traces to player decisions via causal chain",
                "A2": "Death screen shows specific cause (<50 chars)",
                "A3": "Track attacksEncountered, attacksEvaded, dodgeRate",
                "A4": "Arc phases: POWER -> FLOW -> CRISIS with dignified closure",
            },
            "mechanics": [
                "attack: Deal damage to enemies",
                "dodge: Evade incoming attacks (tracked for A3)",
                "upgrade: Select from 3 choices (tracked for A1)",
                "spawn_wave: Increase difficulty (creates A4 phases)",
            ],
            "witness_integration": {
                "marks": "Capture decision points (A1) and outcomes (A2)",
                "traces": "Accumulate skill metrics (A3)",
                "crystals": "Compose narrative arcs (A4)",
            },
            "galois_loss_budget": sum(a["galois_loss"] for a in self._kernel.list_axioms()),
            "validation_required": True,
        }

        return GameSpecRendering(spec=spec).to_dict()

    @aspect(
        category=AspectCategory.MUTATION,
        help="Verify an implementation against the four axioms",
        examples=[
            "self.tangibility.kgames.verify",
            "self.tangibility.kgames.verify[death_count=1,has_causal_chain=true]",
        ],
    )
    async def verify(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        # Death context parameters
        death_count: int = 1,
        has_causal_chain: bool = True,
        has_player_decisions: bool = True,
        specific_cause: str = "Killed by Soldier Ant",
        killer_type: str = "soldier_ant",
        # Skill metrics parameters
        attacks_encountered: int = 100,
        attacks_evaded: int = 70,
        # Arc history parameters
        phases: str = "POWER,FLOW,CRISIS",
        has_closure: bool = True,
        closure_type: str = "dignity",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Verify an implementation against the four axioms.

        Creates a mock implementation from the parameters and validates it.

        Args:
            death_count: Number of deaths to simulate
            has_causal_chain: Whether deaths have causal chains
            has_player_decisions: Whether causal chains have player decisions
            specific_cause: The death cause message
            killer_type: What killed the player
            attacks_encountered: Total attacks directed at player
            attacks_evaded: Attacks player dodged
            phases: Comma-separated arc phases
            has_closure: Whether arc has definite closure
            closure_type: 'dignity' or 'arbitrary'

        Returns:
            Validation result with per-axiom results and overall quality
        """
        # Build death contexts
        death_contexts = []
        for _ in range(death_count):
            causal_chain = []
            if has_causal_chain:
                if has_player_decisions:
                    causal_chain.append(
                        {
                            "actor": "player",
                            "action": "moved into danger zone",
                            "consequence": "exposed to enemy fire",
                            "gameTime": 1000,
                        }
                    )
                causal_chain.append(
                    {
                        "actor": "enemy",
                        "action": "attacked",
                        "consequence": "dealt fatal damage",
                        "gameTime": 2000,
                    }
                )

            death_contexts.append(
                {
                    "causalChain": causal_chain,
                    "gameTime": 3000,
                    "specificCause": specific_cause,
                    "cause": "combat",
                    "killerType": killer_type,
                }
            )

        # Build skill metrics
        dodge_rate = attacks_evaded / attacks_encountered if attacks_encountered > 0 else 0
        skill_metrics = [
            {
                "attacksEncountered": attacks_encountered,
                "attacksEvaded": attacks_evaded,
                "dodgeRate": dodge_rate,
                "survivalTime": 60000,
            }
        ]

        # Build arc history
        phase_list = [p.strip().upper() for p in phases.split(",")]
        arc_history = {
            "phases": phase_list,
            "hasDefiniteClosure": has_closure,
            "closureType": closure_type,
        }

        # Create mock implementation and validate
        impl = MockGameImplementation(
            death_contexts=death_contexts,
            skill_metrics=skill_metrics,
            arc_history=arc_history,
        )

        result = self._kernel.validate_implementation(impl)
        return ValidationRendering(result=result).to_dict()

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to appropriate methods.
        """
        if aspect == "kernel":
            return await self.kernel(observer, **kwargs)
        elif aspect == "operad":
            return await self.operad(observer, **kwargs)
        elif aspect == "generate":
            return await self.generate(observer, **kwargs)
        elif aspect == "verify":
            return await self.verify(observer, **kwargs)
        else:
            return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "KGamesNode",
    "KernelRendering",
    "OperadRendering",
    "ValidationRendering",
    "GameSpecRendering",
    "MockGameImplementation",
]
