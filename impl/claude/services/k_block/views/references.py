"""
ReferencesView: Loose coupling to implementations and tests.

Phase 3 Extension: Enable K-Block to "loosely refer" to existing code.

Philosophy:
    "Every spec knows what implements it. Every impl knows what tests it."
    "The graph IS the system."

This view discovers:
    - impl/ files that implement this spec
    - _tests/ files that test this spec
    - Other specs that extend/reference this

The coupling is LOOSE:
    - Discovered via SpecGraph edges (not hard-coded)
    - Stale references are marked, not errors
    - Missing implementations are opportunities, not failures

See: protocols/specgraph/types.py for EdgeType
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, FrozenSet

from .tokens import SemanticToken, TokenKind

if TYPE_CHECKING:
    from .base import ViewType


# -----------------------------------------------------------------------------
# Reference Types
# -----------------------------------------------------------------------------


class ReferenceKind:
    """Types of loose references."""

    IMPLEMENTS = "implements"  # Code that implements this spec
    TESTS = "tests"  # Tests that verify this spec
    EXTENDS = "extends"  # Specs this builds on
    EXTENDED_BY = "extended_by"  # Specs that build on this
    REFERENCES = "references"  # Loose mentions
    HERITAGE = "heritage"  # External sources (papers, etc.)


@dataclass(frozen=True)
class Reference:
    """
    A loose reference to another file.

    References are DISCOVERED, not declared. They can become stale
    when the target is modified or deleted.
    """

    kind: str  # From ReferenceKind
    target: str  # Path to target (e.g., "impl/claude/services/k_block/core/sheaf.py")
    context: str = ""  # Where in the source this was found
    line_number: int | None = None
    confidence: float = 1.0  # How confident in this reference (0-1)
    stale: bool = False  # Whether target has changed since reference

    @property
    def exists(self) -> bool:
        """Check if target file exists."""
        return Path(self.target).exists()

    @property
    def target_name(self) -> str:
        """Short name of target."""
        return Path(self.target).name

    def to_token(self) -> SemanticToken:
        """Convert to semantic token for sheaf coherence."""
        return SemanticToken(
            id=f"ref-{self.kind}-{self.target_name}",
            kind=TokenKind.RELATION,
            value=self.target,
            position=self.line_number,
        )


# -----------------------------------------------------------------------------
# ReferencesView
# -----------------------------------------------------------------------------


@dataclass
class ReferencesView:
    """
    View of loose references from a K-Block to impl/tests/specs.

    This view is READ-ONLY (like Diff). It discovers references
    but doesn't allow editing them directly.

    Discovery sources:
    1. SpecGraph edges (if available)
    2. Inline references: `impl/...` paths in content
    3. Wiki-style: [[spec-name]] links
    4. Conventional: spec/X.md → impl/claude/services/X/

    Usage:
        >>> view = ReferencesView()
        >>> view.render(content, spec_path="spec/protocols/k-block.md")
        >>> print(view.implements)  # List of impl files
        >>> print(view.tests)  # List of test files
    """

    _content: str = ""
    _spec_path: str = ""
    _tokens: FrozenSet[SemanticToken] = field(default_factory=frozenset)
    _references: list[Reference] = field(default_factory=list)

    @property
    def view_type(self) -> "ViewType":
        """Return REFERENCES view type."""
        from .base import ViewType

        return ViewType.REFERENCES

    @property
    def references(self) -> list[Reference]:
        """All discovered references."""
        return self._references

    @property
    def implements(self) -> list[Reference]:
        """References to implementation files."""
        return [r for r in self._references if r.kind == ReferenceKind.IMPLEMENTS]

    @property
    def tests(self) -> list[Reference]:
        """References to test files."""
        return [r for r in self._references if r.kind == ReferenceKind.TESTS]

    @property
    def extends(self) -> list[Reference]:
        """Specs this extends."""
        return [r for r in self._references if r.kind == ReferenceKind.EXTENDS]

    @property
    def extended_by(self) -> list[Reference]:
        """Specs that extend this."""
        return [r for r in self._references if r.kind == ReferenceKind.EXTENDED_BY]

    def render(
        self,
        content: str,
        spec_path: str = "",
        specgraph: Any | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Discover references and render summary.

        Args:
            content: The spec markdown content
            spec_path: Path to the spec file (for conventional discovery)
            specgraph: Optional SpecGraph for edge-based discovery

        Returns:
            Text summary of discovered references
        """
        self._content = content
        self._spec_path = spec_path
        self._references = []

        # 1. Discover from SpecGraph if available
        if specgraph is not None:
            self._discover_from_specgraph(specgraph)

        # 2. Discover from inline paths in content
        self._discover_inline_paths(content)

        # 3. Discover from conventional structure
        if spec_path:
            self._discover_conventional(spec_path)

        # 4. Extract tokens
        self._tokens = frozenset(r.to_token() for r in self._references)

        return self._render_summary()

    def tokens(self) -> FrozenSet[SemanticToken]:
        """Return reference tokens."""
        return self._tokens

    def to_canonical(self) -> str:
        """References view is read-only; return source content."""
        return self._content

    # -------------------------------------------------------------------------
    # Discovery Methods
    # -------------------------------------------------------------------------

    def _discover_from_specgraph(self, specgraph: Any) -> None:
        """Discover references from SpecGraph edges."""
        if not self._spec_path:
            return

        # Try to import EdgeType
        try:
            from protocols.specgraph.types import EdgeType
        except ImportError:
            return

        # Get edges from this spec
        for edge in specgraph.edges_from(self._spec_path):
            kind = edge.edge_type.value  # "implements", "tests", etc.
            self._references.append(
                Reference(
                    kind=kind,
                    target=edge.target,
                    context=edge.context,
                    line_number=edge.line_number,
                )
            )

        # Get edges TO this spec (for extended_by)
        for edge in specgraph.edges_to(self._spec_path):
            if edge.edge_type == EdgeType.EXTENDS:
                self._references.append(
                    Reference(
                        kind=ReferenceKind.EXTENDED_BY,
                        target=edge.source,
                        context=edge.context,
                        line_number=edge.line_number,
                    )
                )

    def _discover_inline_paths(self, content: str) -> None:
        """Discover impl/test paths mentioned inline."""
        import re

        # Pattern: `impl/claude/...` or impl/claude/...
        impl_pattern = r'[`"]?(impl/claude/[^\s`"<>]+)[`"]?'
        for match in re.finditer(impl_pattern, content):
            path = match.group(1).rstrip(".,;:)")
            if "_tests/" in path or path.endswith("_test.py"):
                kind = ReferenceKind.TESTS
            else:
                kind = ReferenceKind.IMPLEMENTS

            # Find line number
            line_num = content[: match.start()].count("\n") + 1

            self._references.append(
                Reference(
                    kind=kind,
                    target=path,
                    context=content[max(0, match.start() - 20) : match.end() + 20],
                    line_number=line_num,
                )
            )

        # Pattern: spec/... references
        spec_pattern = r'[`"]?(spec/[^\s`"<>]+\.md)[`"]?'
        for match in re.finditer(spec_pattern, content):
            path = match.group(1)
            if path == self._spec_path:
                continue  # Skip self-reference

            line_num = content[: match.start()].count("\n") + 1

            self._references.append(
                Reference(
                    kind=ReferenceKind.REFERENCES,
                    target=path,
                    context=content[max(0, match.start() - 20) : match.end() + 20],
                    line_number=line_num,
                )
            )

    def _discover_conventional(self, spec_path: str) -> None:
        """Discover by conventional naming (spec/X.md → impl/.../X/)."""
        path = Path(spec_path)

        # Extract name from spec path
        # spec/protocols/k-block.md → k_block (underscore for Python)
        name = path.stem.replace("-", "_")

        # Check conventional impl locations
        impl_candidates = [
            f"impl/claude/services/{name}/",
            f"impl/claude/protocols/{name}/",
            f"impl/claude/agents/{name}/",
        ]

        for candidate in impl_candidates:
            candidate_path = Path(candidate)
            if candidate_path.exists() and candidate_path.is_dir():
                # Add as implementation reference
                self._references.append(
                    Reference(
                        kind=ReferenceKind.IMPLEMENTS,
                        target=candidate,
                        context=f"Conventional: {spec_path} → {candidate}",
                        confidence=0.8,  # Lower confidence for conventional
                    )
                )

                # Look for tests
                test_dir = candidate_path / "_tests"
                if test_dir.exists():
                    self._references.append(
                        Reference(
                            kind=ReferenceKind.TESTS,
                            target=str(test_dir),
                            context=f"Conventional tests for {candidate}",
                            confidence=0.8,
                        )
                    )

    def _render_summary(self) -> str:
        """Render human-readable summary of references."""
        lines = ["# References", ""]

        if self.implements:
            lines.append("## Implements")
            for ref in self.implements:
                status = "✓" if ref.exists else "?"
                conf = f" ({ref.confidence:.0%})" if ref.confidence < 1.0 else ""
                lines.append(f"  {status} {ref.target}{conf}")
            lines.append("")

        if self.tests:
            lines.append("## Tests")
            for ref in self.tests:
                status = "✓" if ref.exists else "?"
                lines.append(f"  {status} {ref.target}")
            lines.append("")

        if self.extends:
            lines.append("## Extends")
            for ref in self.extends:
                lines.append(f"  → {ref.target}")
            lines.append("")

        if self.extended_by:
            lines.append("## Extended By")
            for ref in self.extended_by:
                lines.append(f"  ← {ref.target}")
            lines.append("")

        other = [r for r in self._references if r.kind == ReferenceKind.REFERENCES]
        if other:
            lines.append("## References")
            for ref in other:
                lines.append(f"  - {ref.target}")
            lines.append("")

        if not self._references:
            lines.append("No references discovered.")

        return "\n".join(lines)


# -----------------------------------------------------------------------------
# Integration Helper
# -----------------------------------------------------------------------------


def discover_references(
    content: str,
    spec_path: str,
    specgraph: Any | None = None,
) -> list[Reference]:
    """
    Discover loose references from spec content.

    Convenience function for quick reference discovery without
    creating a full ReferencesView.

    Args:
        content: Spec markdown content
        spec_path: Path to spec file
        specgraph: Optional SpecGraph for edge discovery

    Returns:
        List of discovered Reference objects
    """
    view = ReferencesView()
    view.render(content, spec_path=spec_path, specgraph=specgraph)
    return view.references


# -----------------------------------------------------------------------------
# Module Exports
# -----------------------------------------------------------------------------

__all__ = [
    "ReferenceKind",
    "Reference",
    "ReferencesView",
    "discover_references",
]
