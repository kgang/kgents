"""Semantic tokens for K-Block view coherence.

Tokens are the atomic units of meaning shared across views.
They enable the sheaf to verify that views agree on overlapping content.
"""

from dataclasses import dataclass
from enum import Enum


class TokenKind(Enum):
    """Types of semantic tokens extractable from content."""

    HEADING = "heading"  # Markdown headings (# Title)
    FIELD = "field"  # Field definitions (- name: type)
    TYPE = "type"  # Type declarations
    RELATION = "relation"  # References between concepts
    BLOCK = "block"  # Code blocks or quoted sections


@dataclass(frozen=True)
class SemanticToken:
    """Atomic unit of meaning shared across views.

    Tokens are immutable and hashable, enabling set operations
    for sheaf coherence checks.

    Attributes:
        id: Stable identifier (e.g., "h-0" for heading at line 0)
        kind: Token type from TokenKind enum
        value: The actual content (e.g., heading text, field name)
        position: Line number in source (optional, for debugging)
    """

    id: str
    kind: TokenKind
    value: str
    position: int | None = None

    def __repr__(self) -> str:
        pos = f"@{self.position}" if self.position is not None else ""
        return f"Token({self.kind.value}:{self.value}{pos})"
