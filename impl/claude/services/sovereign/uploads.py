"""
Sovereign Uploads: Upload staging and file explorer backend.

> *"Uploads are portals. Every file is a witness in waiting."*

This module implements the upload staging area for the Zero Seed Genesis Grand Strategy.
Files in uploads/ are unmapped, sovereign territory—they exist but are not yet integrated
into the kgents cosmos.

Philosophy:
    "The uploads/ folder is liminal space. Content exists but is not yet witnessed.
     Integration is the act of crossing from potential to actual."

Directory Structure:
    ~/.kgents/uploads/     # SOVEREIGN STAGING (unmapped, XDG-compliant)
    /spec/                 # SPECIFICATIONS (L3-L4)
    /impl/                 # IMPLEMENTATION (L5)
    /docs/                 # DOCUMENTATION (L6-L7)
    /.kgents/              # SYSTEM (hidden, project-local)

Laws:
    Law 1: Files in uploads/ are sovereign but un-witnessed
    Law 2: Moving from uploads/ triggers full integration protocol
    Law 3: Uploads never block, never force—suggest, don't dictate
    Law 4: XDG-compliant storage under ~/.kgents/

Teaching:
    gotcha: Now uses unified StorageProvider for XDG-compliant paths.
            Default is ~/.kgents/uploads/ instead of ./uploads/.
            (Evidence: services/storage/provider.py)

See: plans/zero-seed-genesis-grand-strategy.md (Phase 2)
See: spec/protocols/storage-unified.md
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ..storage import get_uploads_dir

logger = logging.getLogger(__name__)


# =============================================================================
# Upload Types
# =============================================================================


class UploadStatus(Enum):
    """Status of an uploaded file."""

    STAGED = "staged"  # In uploads/, awaiting integration
    INTEGRATING = "integrating"  # Integration in progress
    INTEGRATED = "integrated"  # Successfully moved to destination
    FAILED = "failed"  # Integration failed


@dataclass
class UploadedFile:
    """
    A file in the uploads/ staging area.

    Attributes:
        path: Relative path from uploads/ root
        content_hash: SHA256 hash for deduplication
        size_bytes: File size in bytes
        uploaded_at: When the file appeared in uploads/
        status: Current status in the lifecycle
        metadata: Optional metadata (MIME type, etc.)
    """

    path: str
    content_hash: str
    size_bytes: int
    uploaded_at: datetime
    status: UploadStatus = UploadStatus.STAGED
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": self.path,
            "content_hash": self.content_hash,
            "size_bytes": self.size_bytes,
            "uploaded_at": self.uploaded_at.isoformat(),
            "status": self.status.value,
            "metadata": self.metadata,
        }


@dataclass
class FileExplorerEntry:
    """
    A file or directory in the file explorer.

    Attributes:
        path: Full path relative to kgents root
        name: Display name (filename or dirname)
        is_directory: True if directory, False if file
        size_bytes: Size in bytes (0 for directories)
        modified_at: Last modified timestamp
        children: Child entries (for directories)
        metadata: Additional metadata (layer, kblock_id, etc.)
    """

    path: str
    name: str
    is_directory: bool
    size_bytes: int = 0
    modified_at: datetime | None = None
    children: list[FileExplorerEntry] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": self.path,
            "name": self.name,
            "is_directory": self.is_directory,
            "size_bytes": self.size_bytes,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "children": [child.to_dict() for child in self.children],
            "metadata": self.metadata,
        }


# =============================================================================
# Upload Service
# =============================================================================


class UploadService:
    """
    Service for managing the uploads/ staging area.

    Provides:
    - Scanning uploads/ directory
    - Computing content hashes
    - Tracking upload status
    - Preparing files for integration
    """

    def __init__(self, uploads_root: Path):
        """
        Initialize upload service.

        Args:
            uploads_root: Path to uploads/ directory
        """
        self.uploads_root = uploads_root
        self.uploads_root.mkdir(parents=True, exist_ok=True)

    async def scan_uploads(self) -> list[UploadedFile]:
        """
        Scan uploads/ directory and return all staged files.

        Returns:
            List of UploadedFile entries
        """
        uploads: list[UploadedFile] = []

        for path in self.uploads_root.rglob("*"):
            if not path.is_file():
                continue

            # Skip hidden files
            if path.name.startswith("."):
                continue

            try:
                content = path.read_bytes()
                content_hash = hashlib.sha256(content).hexdigest()
                size_bytes = len(content)
                uploaded_at = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)

                relative_path = str(path.relative_to(self.uploads_root))

                uploads.append(
                    UploadedFile(
                        path=relative_path,
                        content_hash=content_hash,
                        size_bytes=size_bytes,
                        uploaded_at=uploaded_at,
                        status=UploadStatus.STAGED,
                        metadata=self._extract_metadata(path, content),
                    )
                )

            except Exception as e:
                logger.warning(f"Failed to process upload {path}: {e}")
                continue

        return uploads

    async def get_upload(self, relative_path: str) -> UploadedFile | None:
        """
        Get a specific uploaded file by relative path.

        Args:
            relative_path: Path relative to uploads/ root

        Returns:
            UploadedFile if found, None otherwise
        """
        path = self.uploads_root / relative_path

        if not path.exists() or not path.is_file():
            return None

        try:
            content = path.read_bytes()
            content_hash = hashlib.sha256(content).hexdigest()
            size_bytes = len(content)
            uploaded_at = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)

            return UploadedFile(
                path=relative_path,
                content_hash=content_hash,
                size_bytes=size_bytes,
                uploaded_at=uploaded_at,
                status=UploadStatus.STAGED,
                metadata=self._extract_metadata(path, content),
            )

        except Exception as e:
            logger.error(f"Failed to get upload {relative_path}: {e}")
            return None

    async def read_upload_content(self, relative_path: str) -> bytes | None:
        """
        Read the content of an uploaded file.

        Args:
            relative_path: Path relative to uploads/ root

        Returns:
            File content as bytes, or None if not found
        """
        path = self.uploads_root / relative_path

        if not path.exists() or not path.is_file():
            return None

        try:
            return path.read_bytes()
        except Exception as e:
            logger.error(f"Failed to read upload content {relative_path}: {e}")
            return None

    def _extract_metadata(self, path: Path, content: bytes) -> dict[str, Any]:
        """
        Extract metadata from uploaded file.

        Args:
            path: Path to file
            content: File content

        Returns:
            Metadata dictionary
        """
        metadata: dict[str, Any] = {}

        # MIME type detection (simple heuristic)
        suffix = path.suffix.lower()
        mime_types = {
            ".md": "text/markdown",
            ".txt": "text/plain",
            ".py": "text/x-python",
            ".ts": "text/typescript",
            ".tsx": "text/typescript-jsx",
            ".json": "application/json",
            ".yaml": "application/yaml",
            ".yml": "application/yaml",
        }
        metadata["mime_type"] = mime_types.get(suffix, "application/octet-stream")

        # Is text file?
        try:
            content.decode("utf-8")
            metadata["is_text"] = True
        except UnicodeDecodeError:
            metadata["is_text"] = False

        return metadata


# =============================================================================
# File Explorer Service
# =============================================================================


class FileExplorerService:
    """
    Service for exploring the kgents file tree.

    Provides:
    - Directory tree traversal
    - File metadata enrichment (layer, kblock_id)
    - Real file system representation
    """

    def __init__(self, root: Path):
        """
        Initialize file explorer service.

        Args:
            root: Root directory to explore
        """
        self.root = root

    async def get_tree(self, max_depth: int = 3) -> FileExplorerEntry:
        """
        Get the complete directory tree up to max_depth.

        Args:
            max_depth: Maximum depth to traverse

        Returns:
            Root FileExplorerEntry with children
        """
        return await self._build_tree(self.root, max_depth=max_depth, current_depth=0)

    async def get_directory(self, relative_path: str) -> FileExplorerEntry | None:
        """
        Get a specific directory entry.

        Args:
            relative_path: Path relative to root

        Returns:
            FileExplorerEntry if found and is directory, None otherwise
        """
        path = self.root / relative_path

        if not path.exists() or not path.is_dir():
            return None

        return await self._build_tree(path, max_depth=1, current_depth=0)

    async def _build_tree(
        self, path: Path, max_depth: int, current_depth: int
    ) -> FileExplorerEntry:
        """
        Recursively build directory tree.

        Args:
            path: Current path
            max_depth: Maximum depth to traverse
            current_depth: Current depth level

        Returns:
            FileExplorerEntry for this path
        """
        is_directory = path.is_dir()
        relative_path = str(path.relative_to(self.root)) if path != self.root else "."

        # Build entry
        entry = FileExplorerEntry(
            path=relative_path,
            name=path.name if path != self.root else "kgents",
            is_directory=is_directory,
            size_bytes=0 if is_directory else path.stat().st_size,
            modified_at=datetime.fromtimestamp(path.stat().st_mtime, tz=UTC),
            metadata=await self._extract_file_metadata(path),
        )

        # If directory and not at max depth, recurse
        if is_directory and current_depth < max_depth:
            children: list[FileExplorerEntry] = []

            try:
                for child_path in sorted(path.iterdir()):
                    # Skip hidden files/directories
                    if child_path.name.startswith("."):
                        continue

                    child_entry = await self._build_tree(child_path, max_depth, current_depth + 1)
                    children.append(child_entry)

            except PermissionError:
                logger.warning(f"Permission denied for {path}")

            entry.children = children

        return entry

    async def _extract_file_metadata(self, path: Path) -> dict[str, Any]:
        """
        Extract metadata for a file (layer assignment, kblock_id if applicable).

        Args:
            path: Path to file

        Returns:
            Metadata dictionary
        """
        metadata: dict[str, Any] = {}

        # Layer assignment based on path
        relative_path = str(path.relative_to(self.root))

        if relative_path.startswith("spec/"):
            metadata["layer"] = 3  # L3-L4: Specifications
        elif relative_path.startswith("impl/"):
            metadata["layer"] = 5  # L5: Implementation
        elif relative_path.startswith("docs/"):
            metadata["layer"] = 6  # L6-L7: Documentation
        elif relative_path.startswith("uploads/"):
            metadata["layer"] = None  # Unmapped

        # Check if this file is a K-Block (would query KBlock service)
        # For now, just mark files that COULD be K-Blocks
        if path.suffix.lower() in (".md", ".markdown"):
            metadata["potential_kblock"] = True

        return metadata


# =============================================================================
# Service Factories
# =============================================================================


_upload_service: UploadService | None = None
_file_explorer_service: FileExplorerService | None = None


def get_upload_service(uploads_root: Path | None = None) -> UploadService:
    """
    Get or create the global UploadService.

    Args:
        uploads_root: Path to uploads/ directory (defaults to ~/.kgents/uploads)

    Returns:
        UploadService singleton
    """
    global _upload_service

    if _upload_service is None:
        if uploads_root is None:
            uploads_root = get_uploads_dir()
        _upload_service = UploadService(uploads_root)

    return _upload_service


def get_file_explorer_service(root: Path | None = None) -> FileExplorerService:
    """
    Get or create the global FileExplorerService.

    Args:
        root: Root directory to explore (defaults to cwd)

    Returns:
        FileExplorerService singleton
    """
    global _file_explorer_service

    if _file_explorer_service is None:
        if root is None:
            root = Path.cwd()
        _file_explorer_service = FileExplorerService(root)

    return _file_explorer_service


def reset_upload_service() -> None:
    """Reset the global UploadService (for testing)."""
    global _upload_service
    _upload_service = None


def reset_file_explorer_service() -> None:
    """Reset the global FileExplorerService (for testing)."""
    global _file_explorer_service
    _file_explorer_service = None
