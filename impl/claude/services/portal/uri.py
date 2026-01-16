"""
Portal URI: Parser for portal resource URIs.

Parses URIs like:
- file:spec/protocols/witness.md
- chat:session-abc123
- chat:session-abc123#turn-5
- mark:session-abc123#turn-5

Implicit file: prefix for paths without a type.

See: spec/protocols/portal-resource-system.md §II
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Resource type catalog from spec §2.2
KNOWN_RESOURCE_TYPES = {
    "file",
    "chat",
    "turn",
    "mark",
    "crystal",
    "trace",
    "evidence",
    "constitutional",
    "witness",
    "node",
}


@dataclass(frozen=True)
class PortalURI:
    """
    Parsed portal resource URI.

    Examples:
        >>> uri = PortalURI.parse("file:spec/protocols/witness.md")
        >>> uri.resource_type
        'file'
        >>> uri.resource_path
        'spec/protocols/witness.md'
        >>> uri.fragment
        None

        >>> uri = PortalURI.parse("chat:session-abc123#turn-5")
        >>> uri.resource_type
        'chat'
        >>> uri.resource_path
        'session-abc123'
        >>> uri.fragment
        'turn-5'

        >>> uri = PortalURI.parse("spec/protocols/witness.md")  # Implicit file:
        >>> uri.resource_type
        'file'
    """

    raw: str  # Original URI string
    resource_type: str  # "file", "chat", "mark", etc.
    resource_path: str  # The path/identifier
    fragment: str | None  # Optional fragment (#turn-5)

    @classmethod
    def parse(cls, uri: str) -> PortalURI:
        """
        Parse URI string to PortalURI.

        Grammar (from spec §2.1):
            PortalURI     := ResourceType ":" ResourcePath Fragment?
            ResourceType  := "file" | "chat" | "turn" | "mark" | ...
            ResourcePath  := Identifier ("/" Identifier)*
            Fragment      := "#" FragmentSpec
            FragmentSpec  := "turn-" Number | "mark-" Identifier | Identifier

        Implicit file: prefix:
            If no resource type is detected, treat as file path.

        Args:
            uri: URI string to parse

        Returns:
            Parsed PortalURI

        Raises:
            ValueError: If URI is malformed
        """
        if not uri or not uri.strip():
            raise ValueError("URI cannot be empty")

        uri = uri.strip()

        # Split fragment first (everything after #)
        fragment: str | None = None
        if "#" in uri:
            uri_part, fragment = uri.split("#", 1)
            fragment = fragment.strip()
            if not fragment:
                fragment = None
        else:
            uri_part = uri

        # Parse resource type and path
        # Pattern: <type>:<path> or just <path> (implicit file:)
        if ":" in uri_part:
            # Explicit type
            resource_type, resource_path = uri_part.split(":", 1)
            resource_type = resource_type.strip().lower()
            resource_path = resource_path.strip()

            if not resource_type:
                raise ValueError(f"Resource type cannot be empty: {uri}")
            if not resource_path:
                raise ValueError(f"Resource path cannot be empty: {uri}")

            # Validate known types (warning only, not strict)
            if resource_type not in KNOWN_RESOURCE_TYPES:
                # Allow unknown types for extensibility
                pass
        else:
            # Implicit file: prefix
            resource_type = "file"
            resource_path = uri_part.strip()

            if not resource_path:
                raise ValueError(f"Resource path cannot be empty: {uri}")

        return cls(
            raw=uri,
            resource_type=resource_type,
            resource_path=resource_path,
            fragment=fragment,
        )

    def render(self) -> str:
        """
        Render back to URI string.

        Law (spec §8.1): render(parse(uri)) ≡ uri

        Returns:
            URI string
        """
        # Build base URI
        base = f"{self.resource_type}:{self.resource_path}"

        # Add fragment if present
        if self.fragment:
            return f"{base}#{self.fragment}"

        return base

    def __str__(self) -> str:
        return self.render()

    def __repr__(self) -> str:
        return f"PortalURI({self.resource_type}:{self.resource_path}{f'#{self.fragment}' if self.fragment else ''})"
