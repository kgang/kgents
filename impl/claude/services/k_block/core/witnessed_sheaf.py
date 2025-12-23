"""
WitnessedSheaf: Sheaf operations with witness traces.

Phase 3: Every view edit leaves a mark, not just saves.

Philosophy:
    "The proof IS the decision. The mark IS the witness."
    "Edit anywhere, witness everywhere."

This extends KBlockSheaf to emit Witness marks on every propagation,
creating a complete audit trail of all view edits within a K-Block.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from ..views.base import ViewType
from ..views.sync import SemanticDelta
from .sheaf import KBlockSheaf

if TYPE_CHECKING:
    from .kblock import KBlock


# -----------------------------------------------------------------------------
# View Edit Trace
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class ViewEditTrace:
    """
    A trace of a view edit operation.

    Captures everything needed to replay and audit view edits.

    Attributes:
        source_view: Which view was edited
        semantic_deltas: The semantic changes (for non-PROSE edits)
        old_content: Prose content before edit
        new_content: Prose content after edit
        actor: Who made the edit ("Kent", "Claude", "system")
        reasoning: Why this edit was made (optional)
        timestamp: When the edit occurred
    """

    source_view: ViewType
    semantic_deltas: list[SemanticDelta]
    old_content: str
    new_content: str
    actor: str = "system"
    reasoning: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize for witness marks."""
        return {
            "source_view": self.source_view.value,
            "semantic_deltas": [d.to_dict() for d in self.semantic_deltas],
            "old_content_hash": hash(self.old_content) & 0xFFFFFFFF,  # 32-bit hash
            "new_content_hash": hash(self.new_content) & 0xFFFFFFFF,
            "content_changed": self.old_content != self.new_content,
            "actor": self.actor,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat(),
        }


# -----------------------------------------------------------------------------
# Witnessed Sheaf
# -----------------------------------------------------------------------------


@dataclass
class WitnessedSheaf:
    """
    KBlockSheaf wrapper that emits witness traces on every operation.

    Phase 3 upgrade: Every view edit leaves a mark.

    The witness traces capture:
        - Which view was edited
        - What semantic changes were made
        - Who made the edit
        - Why (optional reasoning)

    Usage:
        >>> sheaf = WitnessedSheaf(kblock, actor="Kent")
        >>> result = await sheaf.propagate(
        ...     ViewType.GRAPH,
        ...     new_graph_state,
        ...     reasoning="Added new concept node",
        ... )
        >>> print(f"Mark ID: {result.mark_id}")

    Without Witness Service:
        If no witness service is available, traces are still created
        locally in edit_history but not persisted externally.
    """

    kblock: "KBlock"
    actor: str = "system"
    _inner: KBlockSheaf = field(init=False)
    edit_history: list[ViewEditTrace] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._inner = KBlockSheaf(self.kblock)

    # -------------------------------------------------------------------------
    # Delegated Read Operations
    # -------------------------------------------------------------------------

    def compatible(self, v1: Any, v2: Any) -> bool:
        """Delegate to inner sheaf."""
        return self._inner.compatible(v1, v2)

    def verify_sheaf_condition(self) -> Any:
        """Delegate to inner sheaf."""
        return self._inner.verify_sheaf_condition()

    def glue(self) -> str:
        """Delegate to inner sheaf."""
        return self._inner.glue()

    def refresh_all(self) -> None:
        """Delegate to inner sheaf."""
        self._inner.refresh_all()

    def active_view_types(self) -> set[ViewType]:
        """Delegate to inner sheaf."""
        return self._inner.active_view_types()

    def token_coverage(self) -> dict[ViewType, int]:
        """Delegate to inner sheaf."""
        return self._inner.token_coverage()

    def can_edit_view(self, view_type: ViewType) -> bool:
        """Delegate to inner sheaf."""
        return self._inner.can_edit_view(view_type)

    # -------------------------------------------------------------------------
    # Witnessed Propagation
    # -------------------------------------------------------------------------

    def propagate(
        self,
        source: ViewType,
        new_content: str | Any,
        old_state: Any | None = None,
        reasoning: str | None = None,
    ) -> dict[ViewType, dict[str, Any]]:
        """
        Propagate changes and emit witness trace.

        This is the witnessed version of KBlockSheaf.propagate().
        It creates a ViewEditTrace and stores it in edit_history.

        Args:
            source: The view type that was edited
            new_content: New content/state
            old_state: Previous view state (for non-PROSE)
            reasoning: Why this edit was made (for audit trail)

        Returns:
            Dict mapping view types to change info, with added 'trace' key
        """
        # Capture before state
        old_prose = self.kblock.content

        # Perform propagation
        changes = self._inner.propagate(source, new_content, old_state)

        # Extract semantic deltas from changes
        semantic_deltas: list[SemanticDelta] = []
        if source in changes and "semantic_deltas" in changes[source]:
            # Reconstruct SemanticDelta objects from dicts
            from ..views.tokens import SemanticToken, TokenKind

            for d in changes[source]["semantic_deltas"]:
                token = SemanticToken(
                    id=d["token_id"],
                    kind=TokenKind(d["token_kind"]),
                    value=d["token_value"],
                )
                delta = SemanticDelta(
                    kind=d["kind"],
                    token=token,
                    old_value=d.get("old_value"),
                    new_value=d.get("new_value"),
                    parent_id=d.get("parent_id"),
                    position_hint=d.get("position_hint"),
                )
                semantic_deltas.append(delta)

        # Create trace
        trace = ViewEditTrace(
            source_view=source,
            semantic_deltas=semantic_deltas,
            old_content=old_prose,
            new_content=self.kblock.content,
            actor=self.actor,
            reasoning=reasoning,
        )

        # Store in local history
        self.edit_history.append(trace)

        # Fire-and-forget to WitnessSynergyBus (editing IS witnessing)
        self._schedule_bus_emit(trace)

        # Add trace to changes for caller
        if source in changes:
            changes[source]["trace"] = trace.to_dict()

        return changes

    def _schedule_bus_emit(self, trace: ViewEditTrace) -> None:
        """
        Fire-and-forget emit to WitnessSynergyBus.

        This enables the unified editing/witnessing path:
        - Kent edits in Membrane → K-Block → Bus → WitnessStream
        - Claude edits via AGENTESE → K-Block → Bus → WitnessStream

        "The proof IS the decision. The mark IS the witness."
        """
        import asyncio

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._emit_to_bus(trace))
        except RuntimeError:
            # No running loop (sync context) — skip bus emit
            # This is expected in tests or CLI without async context
            pass

    async def _emit_to_bus(self, trace: ViewEditTrace) -> None:
        """Emit K-Block edit event to synergy bus."""
        try:
            from services.witness.bus import WitnessTopics, get_synergy_bus

            bus = get_synergy_bus()
            await bus.publish(
                WitnessTopics.KBLOCK_EDITED,
                {
                    "id": f"kblock-{trace.timestamp.timestamp():.0f}",
                    "type": "kblock",
                    "action": f"kblock.view_edit.{trace.source_view.value}",
                    "block_id": self.kblock.id,
                    "path": self.kblock.path,
                    "actor": trace.actor,
                    "reasoning": trace.reasoning,
                    "semantic_deltas": [d.to_dict() for d in trace.semantic_deltas],
                    "content_changed": trace.old_content != trace.new_content,
                    "timestamp": trace.timestamp.isoformat(),
                },
            )
        except Exception:
            # Swallow errors — bus emit is best-effort, shouldn't block editing
            pass

    def propagate_prose(
        self,
        new_content: str,
        reasoning: str | None = None,
    ) -> dict[ViewType, dict[str, Any]]:
        """
        Convenience for prose-only propagation with witness.

        Args:
            new_content: New prose content
            reasoning: Why this edit was made

        Returns:
            Dict mapping view types to change info
        """
        return self.propagate(ViewType.PROSE, new_content, reasoning=reasoning)

    # -------------------------------------------------------------------------
    # History Queries
    # -------------------------------------------------------------------------

    def get_edit_history(self) -> list[ViewEditTrace]:
        """Return all edit traces for this session."""
        return list(self.edit_history)

    def get_edits_by_view(self, view_type: ViewType) -> list[ViewEditTrace]:
        """Return traces for edits from a specific view."""
        return [t for t in self.edit_history if t.source_view == view_type]

    def get_edits_by_actor(self, actor: str) -> list[ViewEditTrace]:
        """Return traces for edits by a specific actor."""
        return [t for t in self.edit_history if t.actor == actor]

    def clear_history(self) -> None:
        """Clear local edit history (does not affect persisted marks)."""
        self.edit_history.clear()

    # -------------------------------------------------------------------------
    # Async Witness Integration
    # -------------------------------------------------------------------------

    async def propagate_async(
        self,
        source: ViewType,
        new_content: str | Any,
        old_state: Any | None = None,
        reasoning: str | None = None,
        witness_service: Any | None = None,
    ) -> tuple[dict[ViewType, dict[str, Any]], str | None]:
        """
        Propagate with async witness mark emission.

        When a witness service is provided, emits a persistent mark.

        Args:
            source: The view type that was edited
            new_content: New content/state
            old_state: Previous view state
            reasoning: Why this edit was made
            witness_service: Optional witness service for mark emission

        Returns:
            Tuple of (changes dict, mark_id or None)
        """
        # Perform witnessed propagation
        changes = self.propagate(source, new_content, old_state, reasoning)

        mark_id: str | None = None

        # Emit to witness service if available
        if witness_service is not None and hasattr(witness_service, "mark"):
            try:
                trace = self.edit_history[-1] if self.edit_history else None
                if trace:
                    mark = await witness_service.mark(
                        action=f"kblock.view_edit.{source.value}",
                        block_id=self.kblock.id,
                        path=self.kblock.path,
                        trace=trace.to_dict(),
                        reasoning=reasoning,
                    )
                    mark_id = mark.id if hasattr(mark, "id") else str(mark)
            except Exception:
                # Witness service unavailable; continue without mark
                pass

        return changes, mark_id

    # -------------------------------------------------------------------------
    # Representation
    # -------------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"WitnessedSheaf(kblock_id={self.kblock.id!r}, "
            f"actor={self.actor!r}, edits={len(self.edit_history)})"
        )


# -----------------------------------------------------------------------------
# Module Exports
# -----------------------------------------------------------------------------

__all__ = [
    "ViewEditTrace",
    "WitnessedSheaf",
]
