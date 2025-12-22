"""ProseView: Markdown prose view for K-Block content.

The ProseView is the canonical view — all other views derive from it.
It extracts semantic tokens (headings, fields, types) from markdown
for sheaf coherence verification.
"""

from dataclasses import dataclass, field
from typing import Any, FrozenSet

from .base import ViewType
from .tokens import SemanticToken, TokenKind


@dataclass
class ProseView:
    """Markdown prose view of K-Block content.

    This is the primary/canonical view. Edits happen here,
    and other views (Graph, Code, Outline) derive from prose.

    Token extraction patterns:
    - Headings: Lines starting with #
    - Fields: Lines matching "- name: type" pattern
    - Types: Lines matching "type Name" or "@dataclass class Name"
    """

    _content: str = ""
    _tokens: FrozenSet[SemanticToken] = field(default_factory=frozenset)
    _rendered: str = ""

    @property
    def view_type(self) -> ViewType:
        """Return PROSE view type."""
        return ViewType.PROSE

    def render(self, content: str, *args: Any, **kwargs: Any) -> str:
        """Parse markdown, extract tokens, return formatted.

        For prose, the "rendered" output is the same as input
        (markdown is already human-readable).

        Args:
            content: Markdown content to render

        Returns:
            The same content (prose is already rendered)
        """
        self._content = content
        self._tokens = self._extract_tokens(content)
        self._rendered = content
        return self._rendered

    def tokens(self) -> FrozenSet[SemanticToken]:
        """Return extracted semantic tokens."""
        return self._tokens

    def to_canonical(self) -> str:
        """Return canonical content (same as stored content for prose)."""
        return self._content

    def _extract_tokens(self, content: str) -> FrozenSet[SemanticToken]:
        """Extract semantic tokens from markdown content.

        Patterns recognized:
        - # Heading → HEADING token
        - - field: type → FIELD token
        - type Name or class Name → TYPE token
        - [[reference]] or [text](link) → RELATION token

        Args:
            content: Markdown content to parse

        Returns:
            Frozen set of extracted tokens
        """
        tokens: set[SemanticToken] = set()

        for line_num, line in enumerate(content.split("\n")):
            stripped = line.strip()

            # Extract headings
            if stripped.startswith("#"):
                level = len(stripped) - len(stripped.lstrip("#"))
                heading_text = stripped.lstrip("#").strip()
                if heading_text:
                    tokens.add(
                        SemanticToken(
                            id=f"h-{line_num}",
                            kind=TokenKind.HEADING,
                            value=heading_text,
                            position=line_num,
                        )
                    )

            # Extract field definitions: "- name: type" or "* name: type"
            elif stripped.startswith(("-", "*")) and ":" in stripped:
                # Remove bullet and split on first colon
                field_part = stripped.lstrip("-*").strip()
                if ":" in field_part:
                    field_name = field_part.split(":", 1)[0].strip()
                    if field_name and not field_name.startswith("http"):
                        tokens.add(
                            SemanticToken(
                                id=f"f-{field_name}",
                                kind=TokenKind.FIELD,
                                value=field_name,
                                position=line_num,
                            )
                        )

            # Extract type declarations: "type Name" or "class Name"
            elif stripped.startswith(("type ", "class ", "@dataclass")):
                parts = stripped.split()
                if len(parts) >= 2:
                    # Handle @dataclass class Name
                    if parts[0] == "@dataclass" and len(parts) >= 3:
                        type_name = parts[2].rstrip(":")
                    else:
                        type_name = parts[1].rstrip(":(")
                    if type_name:
                        tokens.add(
                            SemanticToken(
                                id=f"t-{type_name}",
                                kind=TokenKind.TYPE,
                                value=type_name,
                                position=line_num,
                            )
                        )

            # Extract wiki-style references: [[target]]
            if "[[" in stripped and "]]" in stripped:
                import re

                for match in re.finditer(r"\[\[([^\]]+)\]\]", stripped):
                    ref = match.group(1)
                    tokens.add(
                        SemanticToken(
                            id=f"r-{ref}",
                            kind=TokenKind.RELATION,
                            value=ref,
                            position=line_num,
                        )
                    )

        return frozenset(tokens)
