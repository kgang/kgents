"""
File Resolver: Resolves file: URIs and implicit file paths.

Resolves portal URIs pointing to files in the codebase.

Examples:
    file:spec/protocols/witness.md
    spec/protocols/witness.md  (implicit file: prefix)

See: spec/protocols/portal-resource-system.md §5.1 (by analogy)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ..resolver import PermissionDenied, PortalResolver, ResolvedResource, ResourceNotFound
from ..uri import PortalURI


class FileResolver:
    """
    Resolver for file: resources.

    Resolves file paths to file contents with metadata.
    """

    def __init__(self, base_path: Path | None = None):
        """
        Initialize file resolver.

        Args:
            base_path: Base path for resolving relative file paths.
                      Defaults to current working directory.
        """
        self._base_path = base_path or Path.cwd()

    @property
    def resource_type(self) -> str:
        """The resource type this resolver handles."""
        return "file"

    def can_resolve(self, uri: PortalURI) -> bool:
        """
        Check if this resolver can handle the given URI.

        Args:
            uri: Parsed portal URI

        Returns:
            True if this is a file: URI
        """
        return uri.resource_type == "file"

    async def resolve(self, uri: PortalURI, observer: Any) -> ResolvedResource:
        """
        Resolve file URI to file contents.

        Args:
            uri: Parsed portal URI (must be file: type)
            observer: Observer context (currently unused for file access)

        Returns:
            Resolved resource with file contents

        Raises:
            ResourceNotFound: If file doesn't exist
            PermissionDenied: If file isn't readable
        """
        # Build file path
        file_path = self._resolve_path(uri.resource_path)

        # Check existence
        if not file_path.exists():
            raise ResourceNotFound(f"File not found: {file_path}")

        # Check if it's a file (not a directory)
        if not file_path.is_file():
            raise ResourceNotFound(f"Path is not a file: {file_path}")

        # Check readability
        if not os.access(file_path, os.R_OK):
            raise PermissionDenied(f"File not readable: {file_path}")

        # Read file
        content: str | bytes
        try:
            content = file_path.read_text(encoding="utf-8")
            is_binary = False
        except UnicodeDecodeError:
            # Binary file - read as bytes and note it
            content = file_path.read_bytes()
            is_binary = True

        # Get file info
        stat = file_path.stat()
        file_size = stat.st_size
        modified_time = stat.st_mtime

        # Generate preview (first 200 chars for text, note for binary)
        preview: str
        if is_binary:
            preview = f"[Binary file, {file_size} bytes]"
        else:
            # content is str here (we're in the else branch)
            assert isinstance(content, str)
            preview = content[:200]
            if len(content) > 200:
                preview += "..."

        # Determine actions based on file type
        actions = ["expand", "view"]
        if not is_binary and file_size < 1_000_000:  # 1MB limit for editing
            actions.append("edit")

        return ResolvedResource(
            uri=uri.render(),
            resource_type="file",
            exists=True,
            title=file_path.name,
            preview=preview,
            content=content,
            actions=actions,
            metadata={
                "path": str(file_path),
                "size": file_size,
                "modified_time": modified_time,
                "is_binary": is_binary,
                "extension": file_path.suffix,
            },
        )

    def _resolve_path(self, resource_path: str) -> Path:
        """
        Resolve resource path to absolute file path.

        Args:
            resource_path: Path from URI

        Returns:
            Absolute path to file
        """
        path = Path(resource_path)

        # If already absolute, use it
        if path.is_absolute():
            return path

        # Otherwise resolve relative to base path
        return (self._base_path / path).resolve()
