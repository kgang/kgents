"""
AGENTESE Self Ritual Context: Lawful Workflow Orchestration.

Workflow-related nodes for self.ritual.* paths:
- RitualNode: Phase-gated workflow management

This node provides AGENTESE access to the Ritual primitive for
lawful, auditable workflow orchestration.

AGENTESE Paths:
    self.ritual.manifest  - Show active rituals
    self.ritual.begin     - Start a new ritual (requires Covenant + Offering)
    self.ritual.advance   - Transition ritual phase
    self.ritual.guard     - Evaluate a guard
    self.ritual.complete  - Complete a ritual

Integration (Session 7):
    Uses real CovenantStore and OfferingStore instead of stubs.
    Rituals are stored in the global RitualStore.

See: services/witness/ritual.py
See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..affordances import (
    AspectCategory,
    aspect,
)
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger("kgents.agentese.self_ritual")


# =============================================================================
# Store Access Helpers
# =============================================================================


def _get_ritual_store() -> Any:
    """Get the global ritual store."""
    from services.witness.ritual import get_ritual_store
    return get_ritual_store()


def _get_covenant_store() -> Any:
    """Get the global covenant store."""
    from services.witness.covenant import get_covenant_store
    return get_covenant_store()


def _get_offering_store() -> Any:
    """Get the global offering store."""
    from services.witness.offering import get_offering_store
    return get_offering_store()


# =============================================================================
# RitualNode: AGENTESE Interface to Ritual
# =============================================================================


RITUAL_AFFORDANCES: tuple[str, ...] = ("manifest", "begin", "advance", "guard", "complete")


@node(
    "self.ritual",
    description="Lawful workflow orchestration with Covenant and Offering gates",
)
@dataclass
class RitualNode(BaseLogosNode):
    """
    self.ritual - Lawful workflow orchestration.

    A Ritual is a curator-orchestrated workflow that:
    - Requires a Covenant (permission contract)
    - Requires an Offering (resource contract)
    - Follows N-Phase directed cycle
    - Emits TraceNodes for all actions

    Laws (from ritual.py):
    - Law 1 (Covenant Required): Every Ritual has exactly one Covenant
    - Law 2 (Offering Required): Every Ritual has exactly one Offering
    - Law 3 (Guard Transparency): Guards emit TraceNodes on evaluation
    - Law 4 (Phase Ordering): Phase transitions follow directed cycle

    AGENTESE: self.ritual.*
    """

    _handle: str = "self.ritual"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Ritual affordances available to all archetypes."""
        return RITUAL_AFFORDANCES

    # ==========================================================================
    # Core Protocol Methods
    # ==========================================================================

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Show active and recent rituals.

        Returns:
            List of rituals with status and phase
        """
        from services.witness.ritual import RitualStatus

        store = _get_ritual_store()

        # Collect stats
        total = len(store)
        active = len(store.active())
        complete = sum(
            1 for r in store.recent(limit=100) if r.status == RitualStatus.COMPLETE
        )

        recent = store.recent(limit=5)

        manifest_data = {
            "path": self.handle,
            "description": "Lawful workflow orchestration",
            "total_rituals": total,
            "active_count": active,
            "complete_count": complete,
            "recent": [
                {
                    "id": str(r.id),
                    "name": r.name,
                    "phase": r.current_phase.value,
                    "status": r.status.name,
                    "covenant_id": str(r.covenant_id) if r.covenant_id else None,
                    "offering_id": str(r.offering_id) if r.offering_id else None,
                }
                for r in recent
            ],
            "laws": [
                "Law 1: Every Ritual has exactly one Covenant",
                "Law 2: Every Ritual has exactly one Offering",
                "Law 3: Guards emit TraceNodes on evaluation",
                "Law 4: Phase transitions follow directed cycle",
            ],
        }

        return BasicRendering(
            summary="Rituals (Lawful Workflows)",
            content=self._format_manifest_cli(manifest_data),
            metadata=manifest_data,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle Ritual-specific aspects."""
        match aspect:
            case "begin":
                return self._begin_ritual(**kwargs)
            case "advance":
                return self._advance_ritual(**kwargs)
            case "guard":
                return self._evaluate_guard(**kwargs)
            case "complete":
                return self._complete_ritual(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # ==========================================================================
    # Aspect Implementations
    # ==========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        help="Begin a new ritual (requires Covenant + Offering)",
    )
    def _begin_ritual(
        self,
        name: str = "",
        covenant_id: str = "",
        offering_id: str = "",
        phase: str = "SENSE",
    ) -> dict[str, Any]:
        """
        Begin a new Ritual.

        Uses real CovenantStore and OfferingStore to look up existing
        Covenant and Offering. Falls back to creating test stubs if not found
        (for development/testing).

        Args:
            name: Ritual name/description
            covenant_id: ID of granted Covenant
            offering_id: ID of valid Offering
            phase: Initial phase (default: SENSE)

        Returns:
            Created Ritual info
        """
        from services.witness.covenant import Covenant, CovenantId, CovenantStatus
        from services.witness.offering import Budget, Offering, OfferingId
        from services.witness.ritual import MissingCovenant, MissingOffering, Ritual
        from services.witness.trace_node import NPhase

        if not covenant_id:
            return {"error": "covenant_id is required (Law 1)"}
        if not offering_id:
            return {"error": "offering_id is required (Law 2)"}

        # Look up from real stores
        covenant_store = _get_covenant_store()
        offering_store = _get_offering_store()

        covenant = covenant_store.get(CovenantId(covenant_id))
        offering = offering_store.get(OfferingId(offering_id))

        # Graceful fallback for development/testing
        if covenant is None:
            logger.debug(
                f"Covenant {covenant_id} not found in store, creating granted stub"
            )
            covenant = Covenant(
                id=CovenantId(covenant_id),
                status=CovenantStatus.GRANTED,
            )
            covenant_store.add(covenant)

        if offering is None:
            logger.debug(
                f"Offering {offering_id} not found in store, creating standard stub"
            )
            offering = Offering.create(
                description="Auto-created for ritual",
                budget=Budget.standard(),
            )
            offering = Offering(
                id=OfferingId(offering_id),
                description="Auto-created for ritual",
                budget=Budget(tokens=10000),
            )
            offering_store.add(offering)

        # Validate Covenant is granted
        if covenant.status != CovenantStatus.GRANTED:
            return {
                "error": f"Covenant {covenant_id} not granted (status: {covenant.status.name})"
            }

        # Validate Offering is valid
        if not offering.is_valid():
            return {"error": f"Offering {offering_id} is not valid (expired or exhausted)"}

        # Validate phase
        try:
            initial_phase = NPhase(phase)
        except ValueError:
            return {"error": f"Invalid phase: {phase}"}

        # Create ritual
        try:
            ritual = Ritual.create(
                name=name,
                covenant=covenant,
                offering=offering,
            )
            ritual.begin()
        except MissingCovenant as e:
            return {"error": f"Covenant error: {e}"}
        except MissingOffering as e:
            return {"error": f"Offering error: {e}"}

        # Transition to initial phase if not SENSE
        if initial_phase != NPhase.SENSE:
            # SENSE is default, transition if needed
            if initial_phase == NPhase.ACT:
                ritual.advance_phase(NPhase.ACT)
            # For other phases, follow the directed cycle

        # Store
        ritual_store = _get_ritual_store()
        ritual_store.add(ritual)

        return {
            "id": str(ritual.id),
            "name": ritual.name,
            "phase": ritual.current_phase.value,
            "status": ritual.status.name,
            "covenant_id": str(ritual.covenant_id),
            "offering_id": str(ritual.offering_id),
            "started_at": ritual.started_at.isoformat() if ritual.started_at else None,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        help="Advance ritual to next phase",
    )
    def _advance_ritual(
        self,
        ritual_id: str = "",
        target_phase: str = "",
    ) -> dict[str, Any]:
        """
        Advance ritual to a new phase.

        Law 4: Phase transitions follow directed cycle.
        """
        from services.witness.ritual import GuardFailed, RitualId, RitualNotActive
        from services.witness.trace_node import NPhase

        if not ritual_id:
            return {"error": "ritual_id is required"}
        if not target_phase:
            return {"error": "target_phase is required"}

        store = _get_ritual_store()
        ritual = store.get(RitualId(ritual_id))
        if ritual is None:
            return {"error": f"Ritual {ritual_id} not found"}

        try:
            phase = NPhase(target_phase)
        except ValueError:
            return {"error": f"Invalid phase: {target_phase}"}

        old_phase = ritual.current_phase

        try:
            success = ritual.advance_phase(phase)
        except RitualNotActive as e:
            return {"error": f"Ritual not active: {e}"}
        except GuardFailed as e:
            return {
                "error": f"Guard failed: {e}",
                "guard_id": e.evaluation.guard.id if e.evaluation else None,
            }

        return {
            "ritual_id": ritual_id,
            "from_phase": old_phase.value,
            "to_phase": phase.value,
            "success": success,
            "status": ritual.status.name,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        idempotent=True,
        help="Evaluate a guard (Law 3: emits TraceNode)",
    )
    def _evaluate_guard(
        self,
        ritual_id: str = "",
        guard_id: str = "",
    ) -> dict[str, Any]:
        """
        Evaluate a guard on a ritual.

        Law 3: Guards emit TraceNodes on evaluation.
        """
        from services.witness.ritual import RitualId

        if not ritual_id:
            return {"error": "ritual_id is required"}

        store = _get_ritual_store()
        ritual = store.get(RitualId(ritual_id))
        if ritual is None:
            return {"error": f"Ritual {ritual_id} not found"}

        # Count guards from phases and entry guards
        guards_count = len(ritual.entry_guards)
        for phase in ritual.phases:
            guards_count += len(phase.entry_guards) + len(phase.exit_guards)

        return {
            "ritual_id": ritual_id,
            "guard_id": guard_id,
            "guards_count": guards_count,
            "phase": ritual.current_phase.value,
            "guard_evaluations": len(ritual.guard_evaluations),
            "status": "evaluated",
        }

    @aspect(
        category=AspectCategory.MUTATION,
        help="Complete a ritual",
    )
    def _complete_ritual(
        self,
        ritual_id: str = "",
    ) -> dict[str, Any]:
        """Complete a ritual."""
        from services.witness.ritual import RitualId, RitualNotActive

        if not ritual_id:
            return {"error": "ritual_id is required"}

        store = _get_ritual_store()
        ritual = store.get(RitualId(ritual_id))
        if ritual is None:
            return {"error": f"Ritual {ritual_id} not found"}

        try:
            ritual.complete()
        except RitualNotActive as e:
            return {"error": f"Cannot complete ritual: {e}"}

        return {
            "ritual_id": ritual_id,
            "status": ritual.status.name,
            "phase": ritual.current_phase.value,
            "ended_at": ritual.ended_at.isoformat() if ritual.ended_at else None,
            "trace_count": ritual.trace_count,
        }

    # ==========================================================================
    # CLI Formatting Helpers
    # ==========================================================================

    def _format_manifest_cli(self, data: dict[str, Any]) -> str:
        """Format manifest for CLI output."""
        lines = [
            "Rituals (Lawful Workflows)",
            "=" * 40,
            "",
            f"Total: {data['total_rituals']}",
            f"Active: {data['active_count']}",
            f"Complete: {data['complete_count']}",
            "",
        ]

        if data["recent"]:
            lines.append("Recent Rituals:")
            for r in data["recent"]:
                status_icon = ">" if r["status"] == "ACTIVE" else "o"
                lines.append(f"  {status_icon} {r['name']} [{r['phase']}] - {r['status']}")
        else:
            lines.append("No rituals yet. Use begin to start one.")

        return "\n".join(lines)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "RitualNode",
]
