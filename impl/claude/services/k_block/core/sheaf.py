"""
KBlockSheaf: Coherence verifier for K-Block views.

The sheaf ensures that multiple views of the same content remain
coherent. The gluing axiom: if views agree on overlapping semantic
content, there exists a unique global content they all derive from.

For prose-canonical model: that unique content IS the prose.

Philosophy:
    "Views within K-Block glue to form coherent content."
    — spec/protocols/k-block.md §2.4

See: spec/protocols/k-block.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..views.base import View, ViewType
from .errors import (
    GluingError,
    PropagationError,
    SheafConditionError,
    TokenConflict,
)
from .verification import SheafVerification

if TYPE_CHECKING:
    from .kblock import KBlock


# -----------------------------------------------------------------------------
# KBlockSheaf
# -----------------------------------------------------------------------------


@dataclass
class KBlockSheaf:
    """
    Sheaf over K-Block views.

    The gluing axiom: If views agree on overlapping semantic content,
    there exists a unique global content they all derive from.

    For prose-canonical model: that unique content IS the prose.
    Other views (GRAPH, CODE, OUTLINE) derive from prose and cannot
    be edited directly. DIFF is read-only with no tokens.

    Key Operations:
        - compatible(v1, v2): Check if two views agree on shared tokens
        - glue(): Combine views into unified content (returns prose)
        - propagate(source, delta): Propagate changes from source to others
        - verify_sheaf_condition(): Verify all views are pairwise compatible
        - refresh_all(): Re-render all views from canonical content

    Example:
        >>> sheaf = KBlockSheaf(kblock)
        >>> if sheaf.verify_sheaf_condition():
        ...     content = sheaf.glue()
        ...     print("Views are coherent!")

    Teaching (gotcha):
        In prose-canonical model, propagate() only accepts PROSE as source.
        Attempting to propagate from GRAPH/CODE/OUTLINE raises PropagationError.
        This is by design — derived views are projections, not sources.
    """

    kblock: "KBlock"

    # -------------------------------------------------------------------------
    # Compatibility
    # -------------------------------------------------------------------------

    def compatible(self, v1: View, v2: View) -> bool:
        """
        Views agree on overlapping semantic content.

        Two views are compatible when shared token IDs have the same
        (kind, value). This is the local compatibility condition for
        the sheaf.

        Args:
            v1: First view
            v2: Second view

        Returns:
            True if views are compatible (agree on overlaps)

        Teaching (gotcha):
            Empty intersection is COMPATIBLE (vacuously true).
            Two views with no shared tokens don't conflict.
        """
        tokens1 = {t.id: t for t in v1.tokens()}
        tokens2 = {t.id: t for t in v2.tokens()}

        # Find overlapping token IDs
        shared_ids = set(tokens1.keys()) & set(tokens2.keys())

        # Check each shared token
        for tid in shared_ids:
            t1, t2 = tokens1[tid], tokens2[tid]
            if t1.kind != t2.kind:
                return False  # Kind mismatch
            if t1.value != t2.value:
                return False  # Value mismatch

        return True

    def _find_conflicts(self, v1: View, v2: View) -> list[TokenConflict]:
        """
        Find all token conflicts between two views.

        Returns:
            List of TokenConflict instances (empty if compatible)
        """
        conflicts: list[TokenConflict] = []
        tokens1 = {t.id: t for t in v1.tokens()}
        tokens2 = {t.id: t for t in v2.tokens()}

        shared_ids = set(tokens1.keys()) & set(tokens2.keys())

        for tid in shared_ids:
            t1, t2 = tokens1[tid], tokens2[tid]
            if t1.kind != t2.kind or t1.value != t2.value:
                conflicts.append(
                    TokenConflict(
                        token_id=tid,
                        view1=v1.view_type,
                        view2=v2.view_type,
                        kind1=t1.kind.value,
                        kind2=t2.kind.value,
                        value1=t1.value,
                        value2=t2.value,
                    )
                )

        return conflicts

    # -------------------------------------------------------------------------
    # Verification
    # -------------------------------------------------------------------------

    def verify_sheaf_condition(self) -> SheafVerification:
        """
        Verify all active views are pairwise compatible.

        Checks that every pair of active views agrees on their
        overlapping tokens. This is the sheaf condition.

        Returns:
            SheafVerification with detailed results

        Teaching (gotcha):
            A single view is trivially coherent with itself.
            No active views → trivially coherent (empty sheaf).
        """
        views = list(self.kblock.views.values())

        if len(views) <= 1:
            # 0 or 1 views: trivially coherent
            total_tokens = sum(len(v.tokens()) for v in views)
            return SheafVerification(
                passed=True,
                checked_pairs=0,
                conflicts=[],
                shared_tokens=total_tokens,  # All tokens shared with self
                total_tokens=total_tokens,
            )

        all_conflicts: list[TokenConflict] = []
        checked_pairs = 0
        all_token_ids: set[str] = set()
        token_appearances: dict[str, int] = {}  # How many views have each token

        # Collect token appearances
        for view in views:
            view_tokens = {t.id for t in view.tokens()}
            all_token_ids.update(view_tokens)
            for tid in view_tokens:
                token_appearances[tid] = token_appearances.get(tid, 0) + 1

        # Check all pairs
        for i, v1 in enumerate(views):
            for v2 in views[i + 1 :]:
                checked_pairs += 1
                conflicts = self._find_conflicts(v1, v2)
                all_conflicts.extend(conflicts)

        # Shared tokens = tokens appearing in 2+ views
        shared_count = sum(1 for count in token_appearances.values() if count >= 2)

        return SheafVerification(
            passed=len(all_conflicts) == 0,
            checked_pairs=checked_pairs,
            conflicts=all_conflicts,
            shared_tokens=shared_count,
            total_tokens=len(all_token_ids),
        )

    # -------------------------------------------------------------------------
    # Gluing
    # -------------------------------------------------------------------------

    def glue(self) -> str:
        """
        Combine views into unified content.

        Returns the canonical content (prose) after verifying
        all active views are compatible. For prose-canonical model,
        this is simply the KBlock's content.

        Returns:
            The canonical (prose) content

        Raises:
            GluingError: If no views active or prose not active
            SheafConditionError: If views are not compatible

        Teaching (gotcha):
            Glue returns the EXISTING canonical content, it doesn't
            synthesize new content from derived views. That would
            require bidirectional transforms (Phase 2).
        """
        views = self.kblock.views

        if not views:
            raise GluingError("No views active — cannot glue empty sheaf")

        # Verify sheaf condition
        verification = self.verify_sheaf_condition()
        if not verification:
            raise SheafConditionError(
                "Views are not compatible — cannot glue",
                conflicts=verification.conflicts,
            )

        # Return canonical content (prose)
        return self.kblock.content

    # -------------------------------------------------------------------------
    # Propagation
    # -------------------------------------------------------------------------

    def propagate(self, source: ViewType, new_content: str) -> dict[ViewType, dict[str, Any]]:
        """
        Propagate change from source view to all others.

        For prose-canonical model:
            - source MUST be PROSE (raises if not)
            - Updates KBlock content
            - Refreshes all active derived views
            - Returns info about what changed

        Args:
            source: The view type that was edited
            new_content: The new content from that view

        Returns:
            Dict mapping view types to their change info

        Raises:
            PropagationError: If source is not PROSE

        Teaching (gotcha):
            In prose-canonical, derived views CAN'T be edited.
            This method is the ONLY way to update content, and it
            must come from PROSE. Phase 2 will enable bidirectional.
        """
        if source != ViewType.PROSE:
            raise PropagationError(
                source=source,
                reason="Prose-canonical model: only PROSE can be edited. "
                "Edit the prose content, and other views will update.",
            )

        # Capture before state for derived views
        before_tokens: dict[ViewType, set[str]] = {}
        for vtype, view in self.kblock.views.items():
            if vtype != ViewType.PROSE:
                before_tokens[vtype] = {t.id for t in view.tokens()}

        # Update content
        old_content = self.kblock.content
        self.kblock.set_content(new_content)

        # Refresh all views
        self.refresh_all()

        # Compute what changed in each view
        changes: dict[ViewType, dict[str, Any]] = {}
        for vtype, view in self.kblock.views.items():
            if vtype == ViewType.PROSE:
                # Prose change is the source
                changes[vtype] = {
                    "source": True,
                    "content_changed": old_content != new_content,
                }
            elif vtype == ViewType.DIFF:
                # Diff is read-only, just note it updated
                changes[vtype] = {
                    "source": False,
                    "has_changes": view.has_changes if hasattr(view, "has_changes") else False,
                }
            else:
                # Derived view: compute token delta
                after_tokens = {t.id for t in view.tokens()}
                prev = before_tokens.get(vtype, set())
                changes[vtype] = {
                    "source": False,
                    "tokens_added": list(after_tokens - prev),
                    "tokens_removed": list(prev - after_tokens),
                }

        return changes

    # -------------------------------------------------------------------------
    # Refresh
    # -------------------------------------------------------------------------

    def refresh_all(self) -> None:
        """
        Re-render all active views from canonical content.

        This is the prose-canonical gluing operation:
        1. Get prose content (canonical)
        2. Refresh all derived views with that content
        3. Verify sheaf condition holds

        Teaching (gotcha):
            This does NOT verify after refresh by default.
            Call verify_sheaf_condition() explicitly if you need
            assurance. Refresh is fast; verification has overhead.
        """
        self.kblock.refresh_views()

    # -------------------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------------------

    def active_view_types(self) -> set[ViewType]:
        """Return set of currently active view types."""
        return set(self.kblock.views.keys())

    def token_coverage(self) -> dict[ViewType, int]:
        """
        Get token count per active view.

        Useful for understanding which views contribute
        the most semantic content.
        """
        return {vtype: len(view.tokens()) for vtype, view in self.kblock.views.items()}

    def __repr__(self) -> str:
        views = [vt.value for vt in self.active_view_types()]
        return f"KBlockSheaf(views={views}, kblock_id={self.kblock.id!r})"
