"""
Sheaf-related errors for K-Block.

These errors indicate violations of the sheaf condition or
invalid propagation attempts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..views.base import ViewType


# -----------------------------------------------------------------------------
# Token Conflict
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class TokenConflict:
    """
    A specific token disagreement between views.

    This indicates a violation of the sheaf condition: two views
    have a token with the same ID but different kind or value.
    """

    token_id: str
    view1: "ViewType"
    view2: "ViewType"
    kind1: str
    kind2: str
    value1: str
    value2: str

    @property
    def is_kind_mismatch(self) -> bool:
        """Whether the conflict is a kind mismatch (vs value)."""
        return self.kind1 != self.kind2

    @property
    def is_value_mismatch(self) -> bool:
        """Whether the conflict is a value mismatch (vs kind)."""
        return self.value1 != self.value2

    def __str__(self) -> str:
        if self.is_kind_mismatch:
            return (
                f"Token '{self.token_id}' has kind '{self.kind1}' in {self.view1.value} "
                f"but '{self.kind2}' in {self.view2.value}"
            )
        return (
            f"Token '{self.token_id}' has value '{self.value1}' in {self.view1.value} "
            f"but '{self.value2}' in {self.view2.value}"
        )


# -----------------------------------------------------------------------------
# Sheaf Errors
# -----------------------------------------------------------------------------


class SheafError(Exception):
    """Base class for sheaf-related errors."""

    pass


class SheafConditionError(SheafError):
    """
    Views are not compatible — sheaf condition violated.

    The sheaf condition requires that all pairs of views agree on
    their overlapping tokens. When this is violated, gluing is
    impossible because there's no unique global content.
    """

    def __init__(self, message: str, conflicts: list[TokenConflict] | None = None):
        super().__init__(message)
        self.conflicts = conflicts or []

    def __str__(self) -> str:
        base = super().__str__()
        if self.conflicts:
            conflict_strs = [f"  - {c}" for c in self.conflicts[:5]]
            if len(self.conflicts) > 5:
                conflict_strs.append(f"  ... and {len(self.conflicts) - 5} more")
            return f"{base}\nConflicts:\n" + "\n".join(conflict_strs)
        return base


class PropagationError(SheafError):
    """
    Cannot propagate from this view type.

    In prose-canonical model, only PROSE can be the source of
    propagation. Attempting to propagate from a derived view
    (GRAPH, CODE, OUTLINE) raises this error.
    """

    def __init__(self, source: "ViewType", reason: str):
        self.source = source
        self.reason = reason
        super().__init__(f"Cannot propagate from {source.value}: {reason}")


class GluingError(SheafError):
    """
    Gluing operation failed.

    This can happen when:
    - No views are active
    - The canonical view (PROSE) is not active
    - Views are incompatible (use SheafConditionError for details)
    """

    pass
