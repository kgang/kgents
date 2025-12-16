"""
Datum: The atomic unit of persisted data.

Schema-free by design. Just bytes with an identity and optional causal link.

This is the NEW simplified D-gent architecture (data-architecture-rewrite).
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class Datum:
    """
    The atomic unit of persisted data.

    Schema-free by default. Just bytes with an identity.

    Attributes:
        id: UUID or content-addressed hash
        content: Raw data (schema-free bytes)
        created_at: Unix timestamp
        causal_parent: ID of datum that caused this one (for tracing)
        metadata: Optional tags (no schema enforcement)
    """

    id: str
    content: bytes
    created_at: float
    causal_parent: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        content: bytes,
        *,
        id: str | None = None,
        causal_parent: str | None = None,
        metadata: dict[str, str] | None = None,
        content_addressed: bool = False,
    ) -> Datum:
        """
        Factory for creating Datum with sensible defaults.

        Args:
            content: Raw bytes to store
            id: Optional custom ID (auto-generated if None)
            causal_parent: ID of parent datum for causal tracing
            metadata: Optional string key-value tags
            content_addressed: If True, ID is SHA-256 hash of content

        Returns:
            New Datum instance
        """
        if id is None:
            if content_addressed:
                id = hashlib.sha256(content).hexdigest()
            else:
                id = uuid4().hex

        return cls(
            id=id,
            content=content,
            created_at=time.time(),
            causal_parent=causal_parent,
            metadata=metadata or {},
        )

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Datum:
        """Deserialize from JSON-compatible dict."""
        content = data["content"]
        if isinstance(content, str):
            # Base64 or hex encoded
            import base64

            try:
                content = base64.b64decode(content)
            except Exception:
                content = bytes.fromhex(content)

        return cls(
            id=data["id"],
            content=content,
            created_at=data["created_at"],
            causal_parent=data.get("causal_parent"),
            metadata=data.get("metadata", {}),
        )

    def to_json(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        import base64

        return {
            "id": self.id,
            "content": base64.b64encode(self.content).decode("ascii"),
            "created_at": self.created_at,
            "causal_parent": self.causal_parent,
            "metadata": self.metadata,
        }

    def to_jsonl_line(self) -> str:
        """Serialize to a single JSONL line (no trailing newline)."""
        return json.dumps(self.to_json(), separators=(",", ":"))

    @classmethod
    def from_jsonl_line(cls, line: str) -> Datum:
        """Deserialize from a single JSONL line."""
        return cls.from_json(json.loads(line))

    def with_metadata(self, **kwargs: str) -> Datum:
        """Return new Datum with additional metadata."""
        return Datum(
            id=self.id,
            content=self.content,
            created_at=self.created_at,
            causal_parent=self.causal_parent,
            metadata={**self.metadata, **kwargs},
        )

    def derive(
        self,
        content: bytes,
        *,
        id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> Datum:
        """
        Create a new Datum that causally derives from this one.

        The new datum's causal_parent will point to this datum's ID.
        """
        return Datum.create(
            content=content,
            id=id,
            causal_parent=self.id,
            metadata=metadata,
        )

    @property
    def size(self) -> int:
        """Size of content in bytes."""
        return len(self.content)

    def __repr__(self) -> str:
        content_preview = (
            self.content[:20].decode("utf-8", errors="replace") + "..."
            if len(self.content) > 20
            else self.content.decode("utf-8", errors="replace")
        )
        return (
            f"Datum(id={self.id[:8]}..., "
            f"content={content_preview!r}, "
            f"size={self.size}B)"
        )
