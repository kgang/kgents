"""
Dawn Cockpit Snippet Types.

Three snippet patterns form the "button pad" — Kent's copy-paste toolkit:

1. StaticSnippet: Configured, rarely changing (voice anchors, quotes, patterns)
   - Rendered eagerly at startup
   - Source: CLAUDE.md, config files

2. QuerySnippet: Derived from AGENTESE queries
   - Rendered lazily on first access
   - Source: self.witness.recent, self.brain.now, etc.

3. CustomSnippet: User-added, ephemeral per session
   - Created during work session
   - Cleared on session end

All snippets are frozen dataclasses for immutability.

See: spec/protocols/dawn-cockpit.md
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal


def _deterministic_id(content: str) -> str:
    """Generate a deterministic 8-char ID from content hash."""
    return hashlib.sha256(content.encode()).hexdigest()[:8]


@dataclass(frozen=True)
class StaticSnippet:
    """
    Configured, rarely changing. Rendered eagerly.

    Static snippets are loaded at startup from configuration.
    They include voice anchors, quotes, and common patterns.

    Attributes:
        id: Unique identifier
        kind: Type of static snippet (voice_anchor, quote, pattern)
        label: Short display label
        content: The actual content to copy
        source: Where this snippet came from (file path or config key)
    """

    id: str
    kind: Literal["voice_anchor", "quote", "pattern"]
    label: str
    content: str
    source: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "kind": self.kind,
            "label": self.label,
            "content": self.content,
            "source": self.source,
            "type": "static",
        }


@dataclass(frozen=True)
class QuerySnippet:
    """
    Derived from AGENTESE query. Rendered lazily.

    Query snippets store an AGENTESE path to invoke. Content is loaded
    on first access and cached in _content. Use with_content() to
    create a loaded version.

    Attributes:
        id: Unique identifier
        kind: Type of query (mark, path, file, now)
        label: Short display label
        query: AGENTESE path to invoke (e.g., "self.witness.recent")
        _content: Cached content (None until loaded)
    """

    id: str
    kind: Literal["mark", "path", "file", "now"]
    label: str
    query: str
    _content: str | None = field(default=None, repr=False)

    @property
    def is_loaded(self) -> bool:
        """Check if content has been loaded."""
        return self._content is not None

    @property
    def content(self) -> str | None:
        """Get cached content (None if not loaded)."""
        return self._content

    def with_content(self, content: str) -> QuerySnippet:
        """
        Return new QuerySnippet with content populated.

        Since QuerySnippet is frozen, we return a new instance with
        the content field set.
        """
        return QuerySnippet(
            id=self.id,
            kind=self.kind,
            label=self.label,
            query=self.query,
            _content=content,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "kind": self.kind,
            "label": self.label,
            "query": self.query,
            "content": self._content,
            "is_loaded": self.is_loaded,
            "type": "query",
        }


@dataclass(frozen=True)
class CustomSnippet:
    """
    User-added, ephemeral per session.

    Custom snippets are created by the user during a work session.
    They are not persisted and are cleared at session end.

    Attributes:
        id: Unique identifier
        label: User-provided label
        content: The content to copy
        created_at: When the snippet was created
    """

    id: str
    label: str
    content: str
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "label": self.label,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "type": "custom",
        }


# Type alias for any snippet
Snippet = StaticSnippet | QuerySnippet | CustomSnippet


class SnippetLibrary:
    """
    Manages snippet collection across the three patterns.

    Provides separate storage for static, query, and custom snippets.
    Static and query snippets are configured at startup; custom snippets
    are added by the user during the session.

    Usage:
        lib = SnippetLibrary()
        lib.load_defaults()  # Load voice anchors

        # Add custom snippet during session
        snippet = lib.add_custom("My Note", "Remember this")

        # Copy operation would use lib.get(snippet.id)
    """

    def __init__(self) -> None:
        """Initialize empty snippet library."""
        self._static: dict[str, StaticSnippet] = {}
        self._query: dict[str, QuerySnippet] = {}
        self._custom: dict[str, CustomSnippet] = {}

    # === List operations ===

    def list_static(self) -> list[StaticSnippet]:
        """List all static snippets."""
        return list(self._static.values())

    def list_query(self) -> list[QuerySnippet]:
        """List all query snippets."""
        return list(self._query.values())

    def list_custom(self) -> list[CustomSnippet]:
        """List all custom snippets, newest first."""
        return sorted(
            self._custom.values(),
            key=lambda s: s.created_at,
            reverse=True,
        )

    def list_all(self) -> list[Snippet]:
        """List all snippets (static, then query, then custom)."""
        return self.list_static() + self.list_query() + self.list_custom()

    # === Get operation ===

    def get(self, snippet_id: str) -> Snippet | None:
        """Get any snippet by ID (searches all collections)."""
        return (
            self._static.get(snippet_id)
            or self._query.get(snippet_id)
            or self._custom.get(snippet_id)
        )

    # === Static snippets (configured at startup) ===

    def add_static(
        self,
        kind: Literal["voice_anchor", "quote", "pattern"],
        label: str,
        content: str,
        source: str,
        deterministic: bool = True,
    ) -> StaticSnippet:
        """
        Add a static snippet.

        Args:
            deterministic: If True, use content-based ID (stable across runs).
                          If False, use random UUID (ephemeral).
        """
        snippet_id = _deterministic_id(content) if deterministic else str(uuid.uuid4())[:8]
        snippet = StaticSnippet(
            id=snippet_id,
            kind=kind,
            label=label,
            content=content,
            source=source,
        )
        self._static[snippet.id] = snippet
        return snippet

    # === Query snippets (configured at startup) ===

    def add_query(
        self,
        kind: Literal["mark", "path", "file", "now"],
        label: str,
        query: str,
        deterministic: bool = True,
    ) -> QuerySnippet:
        """
        Add a query snippet (content loaded lazily).

        Args:
            deterministic: If True, use query-based ID (stable across runs).
                          If False, use random UUID (ephemeral).
        """
        snippet_id = _deterministic_id(query) if deterministic else str(uuid.uuid4())[:8]
        snippet = QuerySnippet(
            id=snippet_id,
            kind=kind,
            label=label,
            query=query,
        )
        self._query[snippet.id] = snippet
        return snippet

    def update_query_content(
        self,
        snippet_id: str,
        content: str,
    ) -> QuerySnippet | None:
        """
        Update a query snippet's content after loading.

        Returns the updated snippet, or None if not found.
        """
        snippet = self._query.get(snippet_id)
        if snippet is None:
            return None
        updated = snippet.with_content(content)
        self._query[snippet_id] = updated
        return updated

    # === Custom snippets (user-added per session) ===

    def add_custom(
        self,
        label: str,
        content: str,
    ) -> CustomSnippet:
        """Add a custom snippet (ephemeral per session)."""
        snippet = CustomSnippet(
            id=str(uuid.uuid4())[:8],
            label=label,
            content=content,
            created_at=datetime.now(),
        )
        self._custom[snippet.id] = snippet
        return snippet

    def remove_custom(self, snippet_id: str) -> bool:
        """
        Remove a custom snippet.

        Returns True if removed, False if not found.
        Only custom snippets can be removed.
        """
        if snippet_id in self._custom:
            del self._custom[snippet_id]
            return True
        return False

    def clear_custom(self) -> None:
        """Clear all custom snippets (session end)."""
        self._custom.clear()

    # === Bulk operations ===

    def clear(self) -> None:
        """Clear all snippets (for testing)."""
        self._static.clear()
        self._query.clear()
        self._custom.clear()

    def load_defaults(self) -> None:
        """
        Load default snippets (voice anchors, common patterns).

        Called at startup to populate the button pad with
        useful defaults from CLAUDE.md.
        """
        # Voice anchors from CLAUDE.md
        self.add_static(
            kind="voice_anchor",
            label="Depth > breadth",
            content="Depth over breadth",
            source="CLAUDE.md",
        )
        self.add_static(
            kind="voice_anchor",
            label="Mirror Test",
            content="Does K-gent feel like me on my best day?",
            source="CLAUDE.md",
        )
        self.add_static(
            kind="voice_anchor",
            label="Tasteful > complete",
            content="Tasteful > feature-complete; Joy-inducing > merely functional",
            source="CLAUDE.md",
        )
        self.add_static(
            kind="quote",
            label="Proof IS decision",
            content="The proof IS the decision. The mark IS the witness.",
            source="CLAUDE.md",
        )

        # Common query snippets
        self.add_query(
            kind="now",
            label="NOW.md Focus",
            query="self.brain.now",
        )
        self.add_query(
            kind="mark",
            label="Recent Witness",
            query="self.witness.recent",
        )

    def __len__(self) -> int:
        """Return total number of snippets."""
        return len(self._static) + len(self._query) + len(self._custom)


__all__ = [
    "StaticSnippet",
    "QuerySnippet",
    "CustomSnippet",
    "Snippet",
    "SnippetLibrary",
]
