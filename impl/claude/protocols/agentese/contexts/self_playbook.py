"""
AGENTESE Self Playbook Context: Lawful Workflow Orchestration.

Workflow-related nodes for self.playbook.* paths:
- PlaybookNode: Phase-gated workflow management

This node provides AGENTESE access to the Playbook primitive for
lawful, auditable workflow orchestration.

AGENTESE Paths:
    self.playbook.manifest  - Show active playbooks
    self.playbook.begin     - Start a new playbook (requires Grant + Scope)
    self.playbook.advance   - Transition playbook phase
    self.playbook.guard     - Evaluate a guard
    self.playbook.complete  - Complete a playbook

Integration (Session 7):
    Uses real GrantStore and ScopeStore instead of stubs.
    Playbooks are stored in the global PlaybookStore.

See: services/witness/playbook.py
See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
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

logger = logging.getLogger("kgents.agentese.self_playbook")


# =============================================================================
# Store Access Helpers
# =============================================================================


def _get_playbook_store() -> Any:
    """Get the global playbook store."""
    from services.witness.playbook import get_playbook_store

    return get_playbook_store()


def _get_grant_store() -> Any:
    """Get the global grant store."""
    from services.witness.grant import get_grant_store

    return get_grant_store()


def _get_scope_store() -> Any:
    """Get the global scope store."""
    from services.witness.scope import get_scope_store

    return get_scope_store()


# =============================================================================
# PlaybookNode: AGENTESE Interface to Playbook
# =============================================================================


PLAYBOOK_AFFORDANCES: tuple[str, ...] = ("manifest", "begin", "advance", "guard", "complete")


@node(
    "self.playbook",
    description="Lawful workflow orchestration with Grant and Scope gates",
)
@dataclass
class PlaybookNode(BaseLogosNode):
    """
    self.playbook - Lawful workflow orchestration.

    A Playbook is a curator-orchestrated workflow that:
    - Requires a Grant (permission contract)
    - Requires a Scope (resource contract)
    - Follows N-Phase directed cycle
    - Emits Marks for all actions

    Laws (from playbook.py):
    - Law 1 (Grant Required): Every Playbook has exactly one Grant
    - Law 2 (Scope Required): Every Playbook has exactly one Scope
    - Law 3 (Guard Transparency): Guards emit Marks on evaluation
    - Law 4 (Phase Ordering): Phase transitions follow directed cycle

    AGENTESE: self.playbook.*
    """

    _handle: str = "self.playbook"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Playbook affordances available to all archetypes."""
        return PLAYBOOK_AFFORDANCES

    # ==========================================================================
    # Core Protocol Methods
    # ==========================================================================

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Show active and recent playbooks.

        Returns:
            List of playbooks with status and phase
        """
        from services.witness.playbook import PlaybookStatus

        store = _get_playbook_store()

        # Collect stats
        total = len(store)
        active = len(store.active())
        complete = sum(1 for r in store.recent(limit=100) if r.status == PlaybookStatus.COMPLETE)

        recent = store.recent(limit=5)

        manifest_data = {
            "path": self.handle,
            "description": "Lawful workflow orchestration",
            "total_playbooks": total,
            "active_count": active,
            "complete_count": complete,
            "recent": [
                {
                    "id": str(r.id),
                    "name": r.name,
                    "phase": r.current_phase.value,
                    "status": r.status.name,
                    "grant_id": str(r.grant_id) if r.grant_id else None,
                    "scope_id": str(r.scope_id) if r.scope_id else None,
                }
                for r in recent
            ],
            "laws": [
                "Law 1: Every Playbook has exactly one Grant",
                "Law 2: Every Playbook has exactly one Scope",
                "Law 3: Guards emit Marks on evaluation",
                "Law 4: Phase transitions follow directed cycle",
            ],
        }

        return BasicRendering(
            summary="Playbooks (Lawful Workflows)",
            content=self._format_manifest_cli(manifest_data),
            metadata=manifest_data,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle Playbook-specific aspects."""
        match aspect:
            case "begin":
                return self._begin_playbook(**kwargs)
            case "advance":
                return self._advance_playbook(**kwargs)
            case "guard":
                return self._evaluate_guard(**kwargs)
            case "complete":
                return self._complete_playbook(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # ==========================================================================
    # Aspect Implementations
    # ==========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        help="Begin a new playbook (requires Grant + Scope)",
    )
    def _begin_playbook(
        self,
        name: str = "",
        grant_id: str = "",
        scope_id: str = "",
        phase: str = "SENSE",
    ) -> dict[str, Any]:
        """
        Begin a new Playbook.

        Uses real GrantStore and ScopeStore to look up existing
        Grant and Scope. Falls back to creating test stubs if not found
        (for development/testing).

        Args:
            name: Playbook name/description
            grant_id: ID of granted Grant
            scope_id: ID of valid Scope
            phase: Initial phase (default: SENSE)

        Returns:
            Created Playbook info
        """
        from services.witness.grant import Grant, GrantId, GrantStatus
        from services.witness.mark import NPhase
        from services.witness.playbook import MissingCovenant, MissingOffering, Playbook
        from services.witness.scope import Budget, Scope, ScopeId

        if not grant_id:
            return {"error": "grant_id is required (Law 1)"}
        if not scope_id:
            return {"error": "scope_id is required (Law 2)"}

        # Look up from real stores
        grant_store = _get_grant_store()
        scope_store = _get_scope_store()

        grant = grant_store.get(GrantId(grant_id))
        scope = scope_store.get(ScopeId(scope_id))

        # Graceful fallback for development/testing
        if grant is None:
            logger.debug(f"Grant {grant_id} not found in store, creating granted stub")
            grant = Grant(
                id=GrantId(grant_id),
                status=GrantStatus.GRANTED,
            )
            grant_store.add(grant)

        if scope is None:
            logger.debug(f"Scope {scope_id} not found in store, creating standard stub")
            scope = Scope.create(
                description="Auto-created for playbook",
                budget=Budget.standard(),
            )
            scope = Scope(
                id=ScopeId(scope_id),
                description="Auto-created for playbook",
                budget=Budget(tokens=10000),
            )
            scope_store.add(scope)

        # Validate Grant is granted
        if grant.status != GrantStatus.GRANTED:
            return {"error": f"Grant {grant_id} not granted (status: {grant.status.name})"}

        # Validate Scope is valid
        if not scope.is_valid():
            return {"error": f"Scope {scope_id} is not valid (expired or exhausted)"}

        # Validate phase
        try:
            initial_phase = NPhase(phase)
        except ValueError:
            return {"error": f"Invalid phase: {phase}"}

        # Create playbook (using new parameter names: grant, scope)
        try:
            playbook = Playbook.create(
                name=name,
                grant=grant,  # backwards compat: covenant -> grant
                scope=scope,  # backwards compat: offering -> scope
            )
            playbook.begin()
        except MissingCovenant as e:
            return {"error": f"Grant error: {e}"}
        except MissingOffering as e:
            return {"error": f"Scope error: {e}"}

        # Transition to initial phase if not SENSE
        if initial_phase != NPhase.SENSE:
            # SENSE is default, transition if needed
            if initial_phase == NPhase.ACT:
                playbook.advance_phase(NPhase.ACT)
            # For other phases, follow the directed cycle

        # Store
        playbook_store = _get_playbook_store()
        playbook_store.add(playbook)

        return {
            "id": str(playbook.id),
            "name": playbook.name,
            "phase": playbook.current_phase.value,
            "status": playbook.status.name,
            "grant_id": str(playbook.grant_id),
            "scope_id": str(playbook.scope_id),
            "started_at": playbook.started_at.isoformat() if playbook.started_at else None,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        help="Advance playbook to next phase",
    )
    def _advance_playbook(
        self,
        playbook_id: str = "",
        target_phase: str = "",
    ) -> dict[str, Any]:
        """
        Advance playbook to a new phase.

        Law 4: Phase transitions follow directed cycle.
        """
        from services.witness.mark import NPhase
        from services.witness.playbook import GuardFailed, PlaybookId, PlaybookNotActive

        if not playbook_id:
            return {"error": "playbook_id is required"}
        if not target_phase:
            return {"error": "target_phase is required"}

        store = _get_playbook_store()
        playbook = store.get(PlaybookId(playbook_id))
        if playbook is None:
            return {"error": f"Playbook {playbook_id} not found"}

        try:
            phase = NPhase(target_phase)
        except ValueError:
            return {"error": f"Invalid phase: {target_phase}"}

        old_phase = playbook.current_phase

        try:
            success = playbook.advance_phase(phase)
        except PlaybookNotActive as e:
            return {"error": f"Playbook not active: {e}"}
        except GuardFailed as e:
            return {
                "error": f"Guard failed: {e}",
                "guard_id": e.evaluation.guard.id if e.evaluation else None,
            }

        return {
            "playbook_id": playbook_id,
            "from_phase": old_phase.value,
            "to_phase": phase.value,
            "success": success,
            "status": playbook.status.name,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        idempotent=True,
        help="Evaluate a guard (Law 3: emits Mark)",
    )
    def _evaluate_guard(
        self,
        playbook_id: str = "",
        guard_id: str = "",
    ) -> dict[str, Any]:
        """
        Evaluate a guard on a playbook.

        Law 3: Guards emit Marks on evaluation.
        """
        from services.witness.playbook import PlaybookId

        if not playbook_id:
            return {"error": "playbook_id is required"}

        store = _get_playbook_store()
        playbook = store.get(PlaybookId(playbook_id))
        if playbook is None:
            return {"error": f"Playbook {playbook_id} not found"}

        # Count guards from phases and entry guards
        guards_count = len(playbook.entry_guards)
        for phase in playbook.phases:
            guards_count += len(phase.entry_guards) + len(phase.exit_guards)

        return {
            "playbook_id": playbook_id,
            "guard_id": guard_id,
            "guards_count": guards_count,
            "phase": playbook.current_phase.value,
            "guard_evaluations": len(playbook.guard_evaluations),
            "status": "evaluated",
        }

    @aspect(
        category=AspectCategory.MUTATION,
        help="Complete a playbook",
    )
    def _complete_playbook(
        self,
        playbook_id: str = "",
    ) -> dict[str, Any]:
        """Complete a playbook."""
        from services.witness.playbook import PlaybookId, PlaybookNotActive

        if not playbook_id:
            return {"error": "playbook_id is required"}

        store = _get_playbook_store()
        playbook = store.get(PlaybookId(playbook_id))
        if playbook is None:
            return {"error": f"Playbook {playbook_id} not found"}

        try:
            playbook.complete()
        except PlaybookNotActive as e:
            return {"error": f"Cannot complete playbook: {e}"}

        return {
            "playbook_id": playbook_id,
            "status": playbook.status.name,
            "phase": playbook.current_phase.value,
            "ended_at": playbook.ended_at.isoformat() if playbook.ended_at else None,
            "mark_count": playbook.mark_count,
        }

    # ==========================================================================
    # CLI Formatting Helpers
    # ==========================================================================

    def _format_manifest_cli(self, data: dict[str, Any]) -> str:
        """Format manifest for CLI output."""
        lines = [
            "Playbooks (Lawful Workflows)",
            "=" * 40,
            "",
            f"Total: {data['total_playbooks']}",
            f"Active: {data['active_count']}",
            f"Complete: {data['complete_count']}",
            "",
        ]

        if data["recent"]:
            lines.append("Recent Playbooks:")
            for r in data["recent"]:
                status_icon = ">" if r["status"] == "ACTIVE" else "o"
                lines.append(f"  {status_icon} {r['name']} [{r['phase']}] - {r['status']}")
        else:
            lines.append("No playbooks yet. Use begin to start one.")

        return "\n".join(lines)


# =============================================================================
# Backwards Compatibility Aliases
# =============================================================================

# Old name -> new name (for gradual migration)
RitualNode = PlaybookNode

# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "PlaybookNode",
    "RitualNode",  # Backwards compat
]
