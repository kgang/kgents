"""
Sovereign Store: Manages sovereign copies of ingested entities.

> *"We don't reference. We possess."*

This store maintains the filesystem-based sovereign copy storage:

    .kgents/sovereign/
    ├── spec/
    │   └── protocols/
    │       └── k-block.md/           # Directory per entity
    │           ├── v1/               # Version 1
    │           │   ├── content.md    # Exact copy at ingest
    │           │   └── meta.json     # Ingest mark, edges
    │           ├── v2/               # Version 2 (after sync)
    │           │   ├── content.md
    │           │   └── meta.json
    │           ├── current -> v2/    # Symlink to latest
    │           └── overlay/          # OUR modifications
    │               ├── annotations.json
    │               └── derived/
    │                   └── edges.json

Design Principles:
    1. File-based for visibility + git compatibility
    2. Symlinks for current version → easy to see what's active
    3. Versioned directories → full history
    4. Overlay separate from content → our mods don't touch original

Teaching:
    gotcha: Windows doesn't support symlinks without admin privileges.
            We use a fallback "current" file containing the version number.

    gotcha: Paths can be deep (spec/protocols/very/nested/thing.md).
            Entity directory mirrors the full path structure.

See: spec/protocols/inbound-sovereignty.md
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .types import Annotation, Diff, DiffType, SovereignEntity

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

DEFAULT_SOVEREIGN_ROOT = Path(".kgents/sovereign")
META_FILENAME = "meta.json"
CURRENT_LINK = "current"
OVERLAY_DIR = "overlay"
DERIVED_DIR = "derived"


# =============================================================================
# SovereignStore
# =============================================================================


class SovereignStore:
    """
    Manages sovereign copies of ingested entities.

    Storage Structure:
        .kgents/sovereign/{path}/
            ├── v{N}/content.{ext}    # Versioned copies
            ├── current -> v{N}/      # Symlink to latest
            └── overlay/              # Our modifications

    Example:
        >>> store = SovereignStore()
        >>> version = await store.store_version(
        ...     path="spec/protocols/k-block.md",
        ...     content=b"# K-Block\\n...",
        ...     ingest_mark="mark-abc123",
        ...     metadata={"source": "git"},
        ... )
        >>> entity = await store.get_current("spec/protocols/k-block.md")
    """

    def __init__(self, root: Path | str | None = None):
        """
        Initialize the sovereign store.

        Args:
            root: Root directory for sovereign storage.
                  Defaults to .kgents/sovereign/ in current directory.
        """
        if root is None:
            self.root = DEFAULT_SOVEREIGN_ROOT
        elif isinstance(root, str):
            self.root = Path(root)
        else:
            self.root = root

        # Ensure root exists
        self.root.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # Version Storage
    # =========================================================================

    async def store_version(
        self,
        path: str,
        content: bytes,
        ingest_mark: str,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """
        Store a new version of an entity.

        Creates a versioned directory with content and metadata.
        Updates the 'current' symlink to point to this version.

        Args:
            path: Entity path (e.g., "spec/protocols/k-block.md")
            content: The content bytes
            ingest_mark: The ingest mark ID
            metadata: Additional metadata to store

        Returns:
            The version number (1, 2, 3, ...)

        Raises:
            ValueError: If content is empty
        """
        if not content:
            raise ValueError("Cannot store empty content")

        entity_dir = self._entity_dir(path)
        entity_dir.mkdir(parents=True, exist_ok=True)

        # Find next version number
        version = self._next_version(entity_dir)

        # Create version directory
        version_dir = entity_dir / f"v{version}"
        version_dir.mkdir()

        # Store content with original extension
        ext = Path(path).suffix or ".bin"
        content_file = version_dir / f"content{ext}"
        content_file.write_bytes(content)

        # Compute content hash
        import hashlib

        content_hash = hashlib.sha256(content).hexdigest()

        # Store metadata
        meta = {
            "version": version,
            "ingest_mark": ingest_mark,
            "content_hash": content_hash,
            "ingested_at": datetime.now(UTC).isoformat(),
            "path": path,
            **(metadata or {}),
        }

        meta_file = version_dir / META_FILENAME
        meta_file.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        # Update current symlink/marker
        self._update_current(entity_dir, version)

        logger.debug(f"Stored {path} v{version} ({len(content)} bytes)")
        return version

    def _entity_dir(self, path: str) -> Path:
        """Get the entity directory for a path."""
        # Normalize path separators
        normalized = path.replace("\\", "/")
        return self.root / normalized

    def _next_version(self, entity_dir: Path) -> int:
        """Find the next version number for an entity."""
        existing = [d for d in entity_dir.iterdir() if d.is_dir() and d.name.startswith("v")]

        if not existing:
            return 1

        # Extract version numbers
        versions = []
        for d in existing:
            try:
                v = int(d.name[1:])
                versions.append(v)
            except ValueError:
                continue

        return max(versions, default=0) + 1

    def _update_current(self, entity_dir: Path, version: int) -> None:
        """Update the 'current' marker to point to a version."""
        current_path = entity_dir / CURRENT_LINK

        # Try symlink first (Unix)
        try:
            if current_path.exists() or current_path.is_symlink():
                current_path.unlink()
            current_path.symlink_to(f"v{version}")
        except OSError:
            # Fallback for Windows: use a text file with version number
            current_path.write_text(str(version), encoding="utf-8")

    def _get_current_version(self, entity_dir: Path) -> int | None:
        """Get the current version number for an entity."""
        current_path = entity_dir / CURRENT_LINK

        if not current_path.exists() and not current_path.is_symlink():
            return None

        try:
            if current_path.is_symlink():
                # Unix: read symlink target
                target = os.readlink(current_path)
                if target.startswith("v"):
                    return int(target[1:])
            else:
                # Windows fallback: read version number from file
                content = current_path.read_text(encoding="utf-8").strip()
                return int(content)
        except (ValueError, OSError):
            pass

        return None

    # =========================================================================
    # Entity Retrieval
    # =========================================================================

    async def get_current(self, path: str) -> SovereignEntity | None:
        """
        Get the current version of an entity.

        Args:
            path: Entity path

        Returns:
            SovereignEntity or None if not found
        """
        entity_dir = self._entity_dir(path)

        if not entity_dir.exists():
            return None

        version = self._get_current_version(entity_dir)
        if version is None:
            return None

        return await self.get_version(path, version)

    async def get_version(self, path: str, version: int) -> SovereignEntity | None:
        """
        Get a specific version of an entity.

        Args:
            path: Entity path
            version: Version number

        Returns:
            SovereignEntity or None if not found
        """
        entity_dir = self._entity_dir(path)
        version_dir = entity_dir / f"v{version}"

        if not version_dir.exists():
            return None

        # Find content file (any extension)
        content_files = list(version_dir.glob("content.*"))
        if not content_files:
            return None

        content_file = content_files[0]
        content = content_file.read_bytes()

        # Read metadata
        meta_file = version_dir / META_FILENAME
        if meta_file.exists():
            metadata = json.loads(meta_file.read_text(encoding="utf-8"))
        else:
            metadata = {}

        # Read overlay
        overlay = await self.get_overlay(path)

        return SovereignEntity(
            path=path,
            content=content,
            version=version,
            metadata=metadata,
            overlay=overlay,
        )

    async def exists(self, path: str) -> bool:
        """Check if an entity exists."""
        entity_dir = self._entity_dir(path)
        return entity_dir.exists() and self._get_current_version(entity_dir) is not None

    async def list_versions(self, path: str) -> list[int]:
        """List all versions of an entity."""
        entity_dir = self._entity_dir(path)

        if not entity_dir.exists():
            return []

        versions = []
        for d in entity_dir.iterdir():
            if d.is_dir() and d.name.startswith("v"):
                try:
                    versions.append(int(d.name[1:]))
                except ValueError:
                    continue

        return sorted(versions)

    # =========================================================================
    # Overlay Operations
    # =========================================================================

    async def store_overlay(
        self,
        path: str,
        overlay_type: str,
        data: dict[str, Any],
    ) -> None:
        """
        Store data in the overlay (our modifications).

        Args:
            path: Entity path
            overlay_type: Type of overlay ("annotations", "edges", etc.)
            data: The data to store

        The overlay structure:
            overlay/
                annotations.json
                corrections.json
                derived/
                    edges.json
                    tokens.json
        """
        entity_dir = self._entity_dir(path)

        if overlay_type in ("edges", "tokens"):
            overlay_dir = entity_dir / OVERLAY_DIR / DERIVED_DIR
        else:
            overlay_dir = entity_dir / OVERLAY_DIR

        overlay_dir.mkdir(parents=True, exist_ok=True)

        overlay_file = overlay_dir / f"{overlay_type}.json"
        overlay_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

        logger.debug(f"Stored overlay {overlay_type} for {path}")

    async def get_overlay(self, path: str) -> dict[str, Any]:
        """
        Get all overlay data for an entity.

        Returns:
            Dict with all overlay data (annotations, edges, etc.)
        """
        entity_dir = self._entity_dir(path)
        overlay_dir = entity_dir / OVERLAY_DIR

        if not overlay_dir.exists():
            return {}

        result: dict[str, Any] = {}

        # Read all JSON files in overlay (including derived/)
        for json_file in overlay_dir.rglob("*.json"):
            key = json_file.stem
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                result[key] = data
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in {json_file}")
                continue

        return result

    async def annotate(
        self,
        path: str,
        annotation: Annotation,
    ) -> None:
        """
        Add an annotation to an entity.

        Annotations are stored in overlay/annotations.json,
        appended to the existing list.

        Args:
            path: Entity path
            annotation: The annotation to add
        """
        overlay = await self.get_overlay(path)
        annotations = overlay.get("annotations", [])
        annotations.append(annotation.to_dict())

        await self.store_overlay(path, "annotations", annotations)

    # =========================================================================
    # Comparison
    # =========================================================================

    async def diff_with_source(
        self,
        path: str,
        source_content: bytes,
    ) -> Diff:
        """
        Compare our sovereign copy with external source.

        Used during sync to see what changed.

        Args:
            path: Entity path
            source_content: Content from external source

        Returns:
            Diff describing the difference
        """
        current = await self.get_current(path)

        if not current:
            return Diff.new(source_content)

        if current.content == source_content:
            return Diff.unchanged()

        return Diff.modified(current.content, source_content)

    # =========================================================================
    # Listing
    # =========================================================================

    async def list_all(self) -> list[str]:
        """
        List all sovereign entities.

        Returns:
            List of entity paths
        """
        paths: list[str] = []

        def is_version_dir(name: str) -> bool:
            """Check if a name is a version directory (v1, v2, v123, etc.)."""
            return name.startswith("v") and len(name) > 1 and name[1:].isdigit()

        def is_entity_dir(directory: Path) -> bool:
            """Check if this directory is an entity directory (has version subdirs)."""
            if not directory.exists():
                return False
            try:
                return any(d.is_dir() and is_version_dir(d.name) for d in directory.iterdir())
            except OSError:
                return False

        def find_entities(directory: Path, prefix: str = "") -> None:
            """Recursively find entity directories."""
            if not directory.exists():
                return

            try:
                items = list(directory.iterdir())
            except OSError:
                return

            for item in items:
                if item.is_dir():
                    item_path = f"{prefix}{item.name}" if prefix else item.name

                    if is_entity_dir(item):
                        # This is an entity directory - add it
                        paths.append(item_path)
                    else:
                        # This might be a namespace directory, recurse
                        # Skip special directories: overlay, current, derived, and version dirs (v1, v2, etc.)
                        if item.name not in (
                            "overlay",
                            "current",
                            "derived",
                        ) and not is_version_dir(item.name):
                            find_entities(item, f"{item_path}/")

        find_entities(self.root)
        return sorted(paths)

    async def count(self) -> int:
        """Count total sovereign entities."""
        entities = await self.list_all()
        return len(entities)

    async def total_versions(self) -> int:
        """Count total versions across all entities."""
        total = 0
        for path in await self.list_all():
            versions = await self.list_versions(path)
            total += len(versions)
        return total

    # =========================================================================
    # Cleanup
    # =========================================================================

    async def delete(self, path: str) -> bool:
        """
        Delete an entity and all its versions.

        Args:
            path: Entity path

        Returns:
            True if deleted, False if not found
        """
        entity_dir = self._entity_dir(path)

        if not entity_dir.exists():
            return False

        shutil.rmtree(entity_dir)
        logger.debug(f"Deleted {path}")
        return True

    async def delete_version(self, path: str, version: int) -> bool:
        """
        Delete a specific version.

        Cannot delete the current version.

        Args:
            path: Entity path
            version: Version to delete

        Returns:
            True if deleted, False if not found or is current

        Raises:
            ValueError: If trying to delete current version
        """
        entity_dir = self._entity_dir(path)
        current = self._get_current_version(entity_dir)

        if current == version:
            raise ValueError("Cannot delete current version")

        version_dir = entity_dir / f"v{version}"

        if not version_dir.exists():
            return False

        shutil.rmtree(version_dir)
        logger.debug(f"Deleted {path} v{version}")
        return True

    # =========================================================================
    # Compaction (Future)
    # =========================================================================

    async def compact(
        self,
        path: str,
        keep_versions: int = 5,
    ) -> int:
        """
        Compact old versions, keeping only the most recent.

        Args:
            path: Entity path
            keep_versions: Number of versions to keep

        Returns:
            Number of versions deleted
        """
        versions = await self.list_versions(path)

        if len(versions) <= keep_versions:
            return 0

        # Keep the most recent versions
        to_delete = versions[:-keep_versions]
        deleted = 0

        for v in to_delete:
            try:
                await self.delete_version(path, v)
                deleted += 1
            except ValueError:
                # Can't delete current version
                continue

        return deleted


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "SovereignStore",
    "DEFAULT_SOVEREIGN_ROOT",
]
