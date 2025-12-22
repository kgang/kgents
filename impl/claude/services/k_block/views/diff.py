"""DiffView: Unified diff view for K-Block content.

Shows the difference between current content and base content
using unified diff format. This view is read-only.
"""

import difflib
from dataclasses import dataclass, field
from typing import Any, FrozenSet

from .base import ViewType
from .tokens import SemanticToken


@dataclass
class DiffView:
    """Unified diff view of K-Block content.

    Compares current content against base_content and shows
    additions (+) and deletions (-) in unified diff format.

    This view is read-only — it's a derived projection that
    cannot be edited directly.
    """

    _content: str = ""
    _base_content: str = ""
    _diff: str = ""

    @property
    def view_type(self) -> ViewType:
        """Return DIFF view type."""
        return ViewType.DIFF

    @property
    def diff(self) -> str:
        """Return the computed diff."""
        return self._diff

    @property
    def has_changes(self) -> bool:
        """Check if there are any changes."""
        return self._content != self._base_content

    def render(self, content: str, *args: Any, **kwargs: Any) -> str:
        """Compute diff between content and base_content.

        Args:
            content: Current content
            *args: First positional arg is base_content (optional)
            **kwargs: base_content can also be passed as kwarg

        Returns:
            Unified diff as string
        """
        self._content = content

        # Get base_content from args or kwargs
        if args:
            self._base_content = args[0] if args[0] is not None else ""
        else:
            self._base_content = kwargs.get("base_content", "")

        self._diff = self._compute_diff()
        return self._diff

    def tokens(self) -> FrozenSet[SemanticToken]:
        """DiffView doesn't extract tokens (read-only view)."""
        return frozenset()

    def to_canonical(self) -> str:
        """Return current content (not the diff)."""
        return self._content

    def _compute_diff(self) -> str:
        """Compute unified diff between base and current content."""
        if not self._base_content and not self._content:
            return "(empty)"

        if not self._base_content:
            # All additions
            lines = [f"+{line}" for line in self._content.split("\n")]
            return "\n".join(["@@ New content @@"] + lines)

        if not self._content:
            # All deletions
            lines = [f"-{line}" for line in self._base_content.split("\n")]
            return "\n".join(["@@ Deleted content @@"] + lines)

        if self._content == self._base_content:
            return "(no changes)"

        # Compute unified diff
        base_lines = self._base_content.split("\n")
        current_lines = self._content.split("\n")

        diff = difflib.unified_diff(
            base_lines,
            current_lines,
            fromfile="base",
            tofile="current",
            lineterm="",
        )

        return "\n".join(diff)

    @property
    def additions(self) -> int:
        """Count lines added."""
        return sum(
            1
            for line in self._diff.split("\n")
            if line.startswith("+") and not line.startswith("+++")
        )

    @property
    def deletions(self) -> int:
        """Count lines deleted."""
        return sum(
            1
            for line in self._diff.split("\n")
            if line.startswith("-") and not line.startswith("---")
        )
