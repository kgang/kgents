"""
SpecSheaf: Multi-view coherence for spec editing.

The SpecSheaf ensures that multiple views of the same spec remain
coherent. When you edit in the Prose view, the Graph and Code views
update to reflect the change (and vice versa).

Sheaf Structure:
    Opens: {prose, graph, code, diff, outline, references}
    Sections: View content at each open
    Gluing: Changes propagate between views

The Gluing Axiom:
    If views agree on overlapping semantic content, there exists
    a unique global content they all derive from.

Philosophy:
    "Multiple views of the same document must remain coherent."
    "The prose is canonical. Other views are projections."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .monad import SpecMonad


# -----------------------------------------------------------------------------
# View Types
# -----------------------------------------------------------------------------


class ViewType(Enum):
    """Types of views available in the sheaf."""

    PROSE = auto()  # Markdown rendering (canonical)
    GRAPH = auto()  # Concept DAG visualization
    CODE = auto()  # Type definitions / implementation
    DIFF = auto()  # Delta from base content
    OUTLINE = auto()  # Hierarchical structure (headings)
    REFERENCES = auto()  # Implements/tests/extends edges


# -----------------------------------------------------------------------------
# View Protocol
# -----------------------------------------------------------------------------


@dataclass
class View:
    """
    A view onto spec content.

    Views are projections of the canonical prose content.
    Each view type interprets the content differently.
    """

    view_type: ViewType
    content: str = ""
    _rendered: dict[str, Any] = field(default_factory=dict)

    def render(self, prose_content: str, **kwargs: Any) -> dict[str, Any]:
        """
        Render this view from prose content.

        Args:
            prose_content: Canonical prose (markdown)
            **kwargs: View-specific options

        Returns:
            Rendered view data
        """
        self.content = prose_content

        match self.view_type:
            case ViewType.PROSE:
                self._rendered = self._render_prose(prose_content)
            case ViewType.OUTLINE:
                self._rendered = self._render_outline(prose_content)
            case ViewType.DIFF:
                base = kwargs.get("base_content", "")
                self._rendered = self._render_diff(prose_content, base)
            case ViewType.REFERENCES:
                spec_path = kwargs.get("spec_path", "")
                self._rendered = self._render_references(prose_content, spec_path)
            case _:
                self._rendered = {"content": prose_content}

        return self._rendered

    def _render_prose(self, content: str) -> dict[str, Any]:
        """Render prose view (passthrough with metadata)."""
        lines = content.split("\n")
        return {
            "content": content,
            "line_count": len(lines),
            "char_count": len(content),
        }

    def _render_outline(self, content: str) -> dict[str, Any]:
        """Extract heading structure for outline view."""
        import re

        headings: list[dict[str, Any]] = []
        for i, line in enumerate(content.split("\n")):
            match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if match:
                headings.append(
                    {
                        "level": len(match.group(1)),
                        "text": match.group(2),
                        "line": i + 1,
                    }
                )

        return {
            "headings": headings,
            "depth": max((h["level"] for h in headings), default=0),
        }

    def _render_diff(self, content: str, base: str) -> dict[str, Any]:
        """Render diff between content and base."""
        import difflib

        if not base:
            return {"diff": "", "additions": 0, "deletions": 0}

        diff_lines = list(
            difflib.unified_diff(
                base.splitlines(keepends=True),
                content.splitlines(keepends=True),
                fromfile="base",
                tofile="edited",
            )
        )

        additions = sum(1 for l in diff_lines if l.startswith("+") and not l.startswith("+++"))
        deletions = sum(1 for l in diff_lines if l.startswith("-") and not l.startswith("---"))

        return {
            "diff": "".join(diff_lines),
            "additions": additions,
            "deletions": deletions,
            "has_changes": additions > 0 or deletions > 0,
        }

    def _render_references(self, content: str, spec_path: str) -> dict[str, Any]:
        """Extract reference edges (implements, tests, extends)."""
        import re

        references: dict[str, list[str]] = {
            "implements": [],
            "tests": [],
            "extends": [],
            "related": [],
        }

        # Look for Prerequisites/Derives From sections
        for match in re.finditer(r"\*\*Prerequisites:\*\*\s*([^\n]+)", content):
            refs = [r.strip().strip("`") for r in match.group(1).split(",")]
            references["extends"].extend(refs)

        # Look for Implementation references
        for match in re.finditer(r"\*\*Implementation:\*\*\s*([^\n]+)", content):
            refs = [r.strip().strip("`") for r in match.group(1).split(",")]
            references["implements"].extend(refs)

        # Look for See: references
        for match in re.finditer(r"See:\s*([^\n]+)", content):
            refs = [r.strip().strip("`") for r in match.group(1).split(",")]
            references["related"].extend(refs)

        return {
            "references": references,
            "total": sum(len(v) for v in references.values()),
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize view state."""
        return {
            "view_type": self.view_type.name,
            "content": self.content,
            "rendered": self._rendered,
        }


# -----------------------------------------------------------------------------
# SpecSheaf
# -----------------------------------------------------------------------------


@dataclass
class SpecSheaf:
    """
    Sheaf over SpecMonad views.

    The sheaf manages multiple views of the same spec content,
    ensuring they remain coherent as edits are made.

    Key operations:
    - activate_view: Create/activate a view type
    - propagate: Propagate changes from one view to all others
    - verify_coherence: Check that all views derive from same content
    - glue: Combine views into canonical content
    """

    monad: "SpecMonad"
    _views: dict[ViewType, View] = field(default_factory=dict)

    # -------------------------------------------------------------------------
    # View Management
    # -------------------------------------------------------------------------

    def activate_view(self, view_type: ViewType) -> View:
        """
        Activate a view type.

        Creates the view if it doesn't exist, then renders it
        from the monad's working content.

        Args:
            view_type: Type of view to activate

        Returns:
            The activated View instance
        """
        if view_type not in self._views:
            self._views[view_type] = View(view_type=view_type)

        view = self._views[view_type]

        # Render with appropriate options
        if view_type == ViewType.DIFF:
            view.render(self.monad.working_content, base_content=self.monad.base_content)
        elif view_type == ViewType.REFERENCES:
            view.render(self.monad.working_content, spec_path=self.monad.spec.path)
        else:
            view.render(self.monad.working_content)

        return view

    def get_view(self, view_type: ViewType) -> View | None:
        """Get an active view by type."""
        return self._views.get(view_type)

    @property
    def active_views(self) -> set[ViewType]:
        """Set of currently active view types."""
        return set(self._views.keys())

    # -------------------------------------------------------------------------
    # Propagation
    # -------------------------------------------------------------------------

    def propagate(self, source_view: ViewType, new_content: str) -> dict[ViewType, dict[str, Any]]:
        """
        Propagate changes from one view to all others.

        When content changes in one view, this updates all other
        active views to maintain coherence.

        Args:
            source_view: View where change originated
            new_content: New content string

        Returns:
            Dict mapping view types to their updated rendered data
        """
        # Update monad content
        self.monad.set_content(new_content)

        # Re-render all active views
        updates: dict[ViewType, dict[str, Any]] = {}
        for view_type in self._views:
            view = self.activate_view(view_type)
            updates[view_type] = view.to_dict()

        return updates

    def refresh_views(self) -> None:
        """Re-render all active views with current content."""
        for view_type in list(self._views.keys()):
            self.activate_view(view_type)

    # -------------------------------------------------------------------------
    # Coherence
    # -------------------------------------------------------------------------

    def verify_coherence(self) -> "SheafVerification":
        """
        Verify all active views are coherent.

        Coherence means all views derive from the same canonical
        prose content.

        Returns:
            SheafVerification with detailed results
        """
        conflicts: list[str] = []
        canonical = self.monad.working_content

        for view_type, view in self._views.items():
            if view.content != canonical:
                conflicts.append(
                    f"{view_type.name}: content mismatch "
                    f"(expected {len(canonical)} chars, got {len(view.content)})"
                )

        return SheafVerification(
            passed=len(conflicts) == 0,
            canonical_hash=self.monad.content_hash,
            active_views=list(self.active_views),
            conflicts=conflicts,
        )

    def glue(self) -> str:
        """
        Combine views into canonical content.

        The prose view is canonical, so this returns the monad's
        working content.

        Returns:
            Canonical prose content
        """
        return self.monad.working_content

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize sheaf state."""
        return {
            "monad_id": self.monad.id,
            "active_views": [v.name for v in self.active_views],
            "views": {vt.name: v.to_dict() for vt, v in self._views.items()},
            "coherent": self.verify_coherence().passed,
        }


# -----------------------------------------------------------------------------
# Verification Result
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class SheafVerification:
    """Result of sheaf coherence verification."""

    passed: bool
    canonical_hash: str
    active_views: list[ViewType]
    conflicts: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Serialize for reporting."""
        return {
            "passed": self.passed,
            "canonical_hash": self.canonical_hash,
            "active_views": [
                v.name if isinstance(v, ViewType) else str(v) for v in self.active_views
            ],
            "conflicts": self.conflicts,
        }
