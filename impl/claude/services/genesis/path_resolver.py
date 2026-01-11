"""
Genesis Path Resolver — Bidirectional path conversion utilities.

Philosophy: "Files are sovereign territory. K-Blocks are rich indexes.
Both addressing schemes must work seamlessly."

This module provides utilities for converting between:
- File paths: spec/genesis/L0/entity.md
- K-Block IDs: genesis:L0:entity
- K-Block URIs: kblock://genesis:L0:entity

See: spec/protocols/genesis-clean-slate.md
"""

from __future__ import annotations

import re
from pathlib import Path


class GenesisPathResolver:
    """
    Resolves between file paths, K-Block IDs, and URIs.

    Supports bidirectional conversion between three path formats:
    1. File path: spec/genesis/L0/entity.md
    2. K-Block ID: genesis:L0:entity
    3. K-Block URI: kblock://genesis:L0:entity

    Examples:
        >>> GenesisPathResolver.file_to_kblock_id("spec/genesis/L0/entity.md")
        'genesis:L0:entity'

        >>> GenesisPathResolver.kblock_id_to_file("genesis:L0:entity")
        'spec/genesis/L0/entity.md'

        >>> GenesisPathResolver.is_genesis_path("spec/genesis/L0/entity.md")
        True
    """

    # Pattern to match genesis file paths
    FILE_PATH_PATTERN = re.compile(r"^spec/genesis/L(\d)/(\w+)\.md$")

    # Pattern to match genesis K-Block IDs
    KBLOCK_ID_PATTERN = re.compile(r"^genesis:L(\d):(\w+)$")

    # Pattern to match kblock:// URIs
    KBLOCK_URI_PATTERN = re.compile(r"^kblock://genesis:L(\d):(\w+)$")

    @staticmethod
    def file_to_kblock_id(file_path: str) -> str | None:
        """
        Convert a file path to a K-Block ID.

        Args:
            file_path: File path like "spec/genesis/L0/entity.md"

        Returns:
            K-Block ID like "genesis:L0:entity", or None if not a genesis path
        """
        # Normalize path separators
        normalized = file_path.replace("\\", "/")

        match = GenesisPathResolver.FILE_PATH_PATTERN.match(normalized)
        if match:
            layer, name = match.groups()
            return f"genesis:L{layer}:{name}"
        return None

    @staticmethod
    def kblock_id_to_file(kblock_id: str) -> str | None:
        """
        Convert a K-Block ID to a file path.

        Args:
            kblock_id: K-Block ID like "genesis:L0:entity"

        Returns:
            File path like "spec/genesis/L0/entity.md", or None if not genesis
        """
        match = GenesisPathResolver.KBLOCK_ID_PATTERN.match(kblock_id)
        if match:
            layer, name = match.groups()
            return f"spec/genesis/L{layer}/{name}.md"
        return None

    @staticmethod
    def uri_to_file(uri: str) -> str | None:
        """
        Convert a kblock:// URI to a file path.

        Args:
            uri: URI like "kblock://genesis:L0:entity"

        Returns:
            File path like "spec/genesis/L0/entity.md", or None if not genesis
        """
        match = GenesisPathResolver.KBLOCK_URI_PATTERN.match(uri)
        if match:
            layer, name = match.groups()
            return f"spec/genesis/L{layer}/{name}.md"
        return None

    @staticmethod
    def uri_to_kblock_id(uri: str) -> str | None:
        """
        Extract K-Block ID from a kblock:// URI.

        Args:
            uri: URI like "kblock://genesis:L0:entity"

        Returns:
            K-Block ID like "genesis:L0:entity", or None if not valid
        """
        if uri.startswith("kblock://"):
            return uri[9:]  # Strip "kblock://"
        return None

    @staticmethod
    def kblock_id_to_uri(kblock_id: str) -> str:
        """
        Convert a K-Block ID to a kblock:// URI.

        Args:
            kblock_id: K-Block ID like "genesis:L0:entity"

        Returns:
            URI like "kblock://genesis:L0:entity"
        """
        return f"kblock://{kblock_id}"

    @staticmethod
    def is_genesis_path(path: str) -> bool:
        """
        Check if a path is a genesis file or K-Block.

        Args:
            path: Any path format (file, ID, or URI)

        Returns:
            True if this is a genesis path in any format
        """
        # Check file path
        if path.startswith("spec/genesis/"):
            return True

        # Check K-Block ID
        if path.startswith("genesis:"):
            return True

        # Check kblock:// URI
        if path.startswith("kblock://genesis:"):
            return True

        return False

    @staticmethod
    def is_genesis_file(path: str) -> bool:
        """Check if path is specifically a genesis file path."""
        return GenesisPathResolver.FILE_PATH_PATTERN.match(path) is not None

    @staticmethod
    def is_genesis_kblock_id(kblock_id: str) -> bool:
        """Check if ID is specifically a genesis K-Block ID."""
        return GenesisPathResolver.KBLOCK_ID_PATTERN.match(kblock_id) is not None

    @staticmethod
    def normalize_to_file_path(path: str) -> str | None:
        """
        Normalize any genesis path format to a file path.

        Args:
            path: File path, K-Block ID, or kblock:// URI

        Returns:
            File path like "spec/genesis/L0/entity.md", or None if not genesis
        """
        # Already a file path
        if path.startswith("spec/genesis/"):
            return path

        # K-Block ID
        if path.startswith("genesis:"):
            return GenesisPathResolver.kblock_id_to_file(path)

        # kblock:// URI
        if path.startswith("kblock://genesis:"):
            return GenesisPathResolver.uri_to_file(path)

        return None

    @staticmethod
    def normalize_to_kblock_id(path: str) -> str | None:
        """
        Normalize any genesis path format to a K-Block ID.

        Args:
            path: File path, K-Block ID, or kblock:// URI

        Returns:
            K-Block ID like "genesis:L0:entity", or None if not genesis
        """
        # File path
        if path.startswith("spec/genesis/"):
            return GenesisPathResolver.file_to_kblock_id(path)

        # Already a K-Block ID
        if path.startswith("genesis:"):
            return path

        # kblock:// URI
        if path.startswith("kblock://genesis:"):
            return GenesisPathResolver.uri_to_kblock_id(path)

        return None

    @staticmethod
    def extract_layer(path: str) -> int | None:
        """
        Extract layer number from any genesis path format.

        Args:
            path: Any genesis path format

        Returns:
            Layer number (0-3), or None if not genesis
        """
        # Try each pattern
        for pattern in [
            GenesisPathResolver.FILE_PATH_PATTERN,
            GenesisPathResolver.KBLOCK_ID_PATTERN,
            GenesisPathResolver.KBLOCK_URI_PATTERN,
        ]:
            match = pattern.match(path)
            if match:
                return int(match.group(1))
        return None

    @staticmethod
    def extract_name(path: str) -> str | None:
        """
        Extract short name from any genesis path format.

        Args:
            path: Any genesis path format

        Returns:
            Short name like "entity", or None if not genesis
        """
        # Try each pattern
        for pattern in [
            GenesisPathResolver.FILE_PATH_PATTERN,
            GenesisPathResolver.KBLOCK_ID_PATTERN,
            GenesisPathResolver.KBLOCK_URI_PATTERN,
        ]:
            match = pattern.match(path)
            if match:
                return match.group(2)
        return None

    @staticmethod
    def get_absolute_file_path(path: str, project_root: Path) -> Path | None:
        """
        Get absolute file path for a genesis path.

        Args:
            path: Any genesis path format
            project_root: Project root directory

        Returns:
            Absolute Path object, or None if not genesis
        """
        file_path = GenesisPathResolver.normalize_to_file_path(path)
        if file_path:
            return project_root / file_path
        return None


__all__ = ["GenesisPathResolver"]
