"""OutlineView: Heading hierarchy view for K-Block content.

Extracts markdown headings into a tree structure representing
the document outline.
"""

from dataclasses import dataclass, field
from typing import Any, FrozenSet

from .base import ViewType
from .tokens import SemanticToken, TokenKind


@dataclass
class OutlineNode:
    """A node in the outline tree."""

    id: str
    title: str
    level: int
    children: list["OutlineNode"] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "level": self.level,
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class OutlineView:
    """Heading hierarchy view of K-Block content.

    Extracts markdown headings (# to ######) and builds
    a tree structure based on heading levels.
    """

    _content: str = ""
    _tokens: FrozenSet[SemanticToken] = field(default_factory=frozenset)
    _root: OutlineNode = field(
        default_factory=lambda: OutlineNode(id="root", title="Document", level=0)
    )

    @property
    def view_type(self) -> ViewType:
        """Return OUTLINE view type."""
        return ViewType.OUTLINE

    @property
    def root(self) -> OutlineNode:
        """Return the root of the outline tree."""
        return self._root

    def render(self, content: str, *args: Any, **kwargs: Any) -> str:
        """Parse content and build outline tree.

        Args:
            content: Markdown content to parse

        Returns:
            Text representation of the outline
        """
        self._content = content
        self._build_tree(content)
        self._tokens = self._extract_tokens()
        return self._to_text()

    def tokens(self) -> FrozenSet[SemanticToken]:
        """Return semantic tokens (headings as tokens)."""
        return self._tokens

    def to_canonical(self) -> str:
        """Return original content (outline cannot be converted back)."""
        return self._content

    def _build_tree(self, content: str) -> None:
        """Build outline tree from markdown headings."""
        self._root = OutlineNode(id="root", title="Document", level=0)

        # Stack of (level, node) for building tree
        stack: list[tuple[int, OutlineNode]] = [(0, self._root)]

        for line_num, line in enumerate(content.split("\n")):
            stripped = line.strip()

            if stripped.startswith("#"):
                level = len(stripped) - len(stripped.lstrip("#"))
                title = stripped.lstrip("#").strip()

                if not title:
                    continue

                node = OutlineNode(id=f"h-{line_num}", title=title, level=level)

                # Pop stack until we find a parent with lower level
                while stack and stack[-1][0] >= level:
                    stack.pop()

                # Add as child of current top
                if stack:
                    stack[-1][1].children.append(node)
                else:
                    # Edge case: no parent, add to root
                    self._root.children.append(node)

                stack.append((level, node))

    def _extract_tokens(self) -> FrozenSet[SemanticToken]:
        """Convert outline nodes to semantic tokens."""
        tokens: set[SemanticToken] = set()
        self._collect_tokens(self._root, tokens)
        return frozenset(tokens)

    def _collect_tokens(self, node: OutlineNode, tokens: set[SemanticToken]) -> None:
        """Recursively collect tokens from outline tree."""
        if node.id != "root":
            tokens.add(
                SemanticToken(
                    id=node.id,
                    kind=TokenKind.HEADING,
                    value=node.title,
                    position=None,
                )
            )
        for child in node.children:
            self._collect_tokens(child, tokens)

    def _to_text(self, node: OutlineNode | None = None, indent: int = 0) -> str:
        """Render outline as indented text."""
        if node is None:
            node = self._root

        lines: list[str] = []

        if node.id != "root":
            prefix = "  " * (indent - 1) + "├─ " if indent > 0 else ""
            lines.append(f"{prefix}{node.title}")

        for child in node.children:
            lines.append(self._to_text(child, indent + 1))

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return outline as nested dictionary."""
        return self._root.to_dict()
