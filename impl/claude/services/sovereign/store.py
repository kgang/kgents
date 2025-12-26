"""
Sovereign Store: Manages sovereign copies of ingested entities.

> *"We don't reference. We possess."*

This store maintains the filesystem-based sovereign copy storage:

    ~/.kgents/sovereign/
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
    5. XDG-compliant storage under ~/.kgents/

Teaching:
    gotcha: Windows doesn't support symlinks without admin privileges.
            We use a fallback "current" file containing the version number.

    gotcha: Paths can be deep (spec/protocols/very/nested/thing.md).
            Entity directory mirrors the full path structure.

    gotcha: Now uses unified StorageProvider for XDG-compliant paths.
            Default is ~/.kgents/sovereign/ instead of .kgents/sovereign/.
            (Evidence: services/storage/provider.py)

See: spec/protocols/inbound-sovereignty.md, spec/protocols/storage-unified.md
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..storage import get_kgents_data_root
from .types import Annotation, Diff, DiffType, ExportBundle, ExportedEntity, SovereignEntity

if TYPE_CHECKING:
    from ..witness.persistence import WitnessPersistence

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Default: ~/.kgents/sovereign (XDG-compliant)
DEFAULT_SOVEREIGN_ROOT = get_kgents_data_root() / "sovereign"
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

    async def is_analyzed(self, path: str) -> bool:
        """
        Check if an entity has been analyzed.

        An entity is considered analyzed if it has analysis metadata in its overlay
        with status=ANALYZED.

        Returns:
            True if entity has been successfully analyzed
            False if not analyzed or entity doesn't exist
        """
        from .analysis import AnalysisStatus

        state = await self.get_analysis_state(path)
        return state is not None and state.status == AnalysisStatus.ANALYZED

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

    async def get_overlay(self, path: str, overlay_type: str | None = None) -> dict[str, Any]:
        """
        Get overlay data for an entity.

        Args:
            path: Entity path
            overlay_type: Specific overlay type to get (e.g., "analysis", "edges")
                         If None, returns all overlay data

        Returns:
            Dict with overlay data (all or specific type)
        """
        entity_dir = self._entity_dir(path)
        overlay_dir = entity_dir / OVERLAY_DIR

        if not overlay_dir.exists():
            return {}

        # If specific type requested, read just that file
        if overlay_type is not None:
            # Check both direct overlay and derived directories
            for search_dir in [overlay_dir, overlay_dir / DERIVED_DIR]:
                overlay_file = search_dir / f"{overlay_type}.json"
                if overlay_file.exists():
                    try:
                        data: dict[str, Any] = json.loads(overlay_file.read_text(encoding="utf-8"))
                        return data
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in {overlay_file}")
                        empty: dict[str, Any] = {}
                        return empty
            empty_result: dict[str, Any] = {}
            return empty_result

        # Otherwise, return all overlay data
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
    # Zero Seed Integration (Phase 1: K-Block/Document Unification)
    # =========================================================================

    async def store_zero_seed_block(
        self,
        layer: int,
        kind: str,
        content: bytes,
        title: str,
        lineage: list[str],
        proof: dict[str, Any] | None = None,
        **metadata: Any,
    ) -> str:
        """
        Store a Zero Seed node as a sovereign entity.

        Zero Seed nodes are K-Blocks representing derivation DAG nodes.
        They follow the same versioning/overlay pattern as files, but
        use a special zeroseed:// path scheme.

        Args:
            layer: Zero Seed layer (1-7)
                   1=axiom, 2=value, 3=goal, 4=spec, 5=action, 6=reflection, 7=representation
            kind: Human-readable kind ("axiom", "value", "goal", etc.)
            content: Node content (Markdown, JSON, etc.)
            title: Human-readable title for this node
            lineage: List of parent node IDs (derivation chain)
            proof: Optional Toulmin proof structure
            **metadata: Additional metadata to store

        Returns:
            The zeroseed:// path for this node

        Example:
            >>> path = await store.store_zero_seed_block(
            ...     layer=1,
            ...     kind="axiom",
            ...     content=b"# Core Axiom\\nTruth is relative to observer.",
            ...     title="Relativity Axiom",
            ...     lineage=[],
            ...     proof={"claim": "Truth is observer-dependent", ...},
            ... )
            >>> print(path)
            zeroseed://axiom/a1b2c3d4
        """
        import uuid

        # Generate unique ID for this Zero Seed node
        node_id = uuid.uuid4().hex[:8]

        # Generate path based on layer/kind
        path = f"zeroseed://{kind}/{node_id}"

        # Store version with Zero Seed metadata
        version = await self.store_version(
            path=path,
            content=content,
            ingest_mark=f"zero-seed-{node_id}",
            metadata={
                "zero_seed_layer": layer,
                "zero_seed_kind": kind,
                "title": title,
                "lineage": lineage,
                "has_proof": proof is not None,
                "toulmin_proof": proof,
                **metadata,
            },
        )

        logger.info(
            f"Stored Zero Seed {kind} at {path} (v{version}, "
            f"{len(lineage)} parents, proof={proof is not None})"
        )

        return path

    # =========================================================================
    # Analysis State Operations
    # =========================================================================

    async def get_analysis_state(self, path: str) -> Any:
        """
        Get analysis state from overlay.

        Returns:
            AnalysisState or None if not found
        """
        from .analysis import AnalysisState

        overlay_data: dict[str, Any] = await self.get_overlay(path, "analysis")
        if overlay_data:
            return AnalysisState.from_dict(overlay_data)
        return None

    async def set_analysis_state(self, path: str, state: Any) -> None:
        """
        Set analysis state in overlay.

        Args:
            path: Entity path
            state: AnalysisState to store
        """
        await self.store_overlay(path, "analysis", state.to_dict())

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

    async def delete(
        self,
        path: str,
        check_references: bool = True,
        force: bool = False,
        convert_references_to_placeholders: bool = False,
        witness: Any | None = None,
        author: str = "kent",
    ) -> Any:
        """
        Delete an entity with safety checks and witness mark (Theorem 11).

        This operation:
        1. Checks for incoming references (if check_references=True)
        2. If references exist and not force: raises ValueError with reference list
        3. Creates witness mark BEFORE deletion
        4. Optionally converts references to placeholders
        5. Deletes the entity and all its versions

        Args:
            path: Entity path
            check_references: Check for references before deleting
            force: Force delete even with references
            convert_references_to_placeholders: Convert refs to placeholders (requires witness)
            witness: Optional WitnessPersistence for creating mark
            author: Who is performing the delete

        Returns:
            DeleteResult with success, path, mark_id, and references_converted list

        Raises:
            ValueError: If references exist and not force
        """
        from .types import DeleteResult

        entity_dir = self._entity_dir(path)

        if not entity_dir.exists():
            return DeleteResult(success=False, path=path)

        # Check for references (Theorem 11)
        references = []
        if check_references:
            references = await self.get_references_to(path)
            if references and not force:
                ref_paths = [ref["from_path"] for ref in references]
                raise ValueError(
                    f"Cannot delete {path}: {len(references)} entities reference it: {ref_paths}"
                )

        # Create witness mark BEFORE deletion (Theorem 11)
        mark_id: str | None = None
        if witness is not None:
            mark_result = await witness.save_mark(
                action=f"sovereign.delete: {path}",
                reasoning=f"Entity deleted with {len(references)} references"
                + (" (converted to placeholders)" if convert_references_to_placeholders else ""),
                principles=["ethical"],
                tags=["sovereign", "delete", "destructive"],
                author=author,
            )
            mark_id = mark_result.mark_id

        # Convert references to placeholders if requested
        references_converted = []
        if convert_references_to_placeholders and witness is not None:
            for ref in references:
                ref_path = ref["from_path"]
                # Update the overlay to mark edge as placeholder
                overlay = await self.get_overlay(ref_path, "edges")
                edges_data = overlay if overlay else {"edges": []}
                edges = edges_data.get("edges", [])

                for edge in edges:
                    if edge.get("target") == path:
                        edge["is_placeholder"] = True
                        edge["placeholder_created_at"] = datetime.now(UTC).isoformat()
                        edge["placeholder_mark_id"] = mark_id

                await self.store_overlay(ref_path, "edges", edges_data)
                references_converted.append(ref_path)

        # Delete the entity
        shutil.rmtree(entity_dir)
        logger.info(
            f"Deleted {path}"
            + (f" (mark: {mark_id})" if mark_id else "")
            + (f", {len(references_converted)} refs → placeholders" if references_converted else "")
        )

        return DeleteResult(
            success=True,
            path=path,
            mark_id=mark_id,
            references_converted_to_placeholders=references_converted,
        )

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

    # =========================================================================
    # File Management
    # =========================================================================

    async def rename(
        self,
        old_path: str,
        new_path: str,
        update_references: bool = True,
        witness: Any | None = None,
        author: str = "kent",
    ) -> str | None:
        """
        Rename/move an entity to a new path with witness mark (Theorem 10).

        This operation:
        1. Creates entity at new_path with all versions
        2. Updates overlay data with new path references
        3. Creates witness mark linking old → new path
        4. Stores mark_id in metadata of new entity

        Args:
            old_path: Current entity path
            new_path: Target entity path
            update_references: Whether to update internal path references
            witness: Optional WitnessPersistence for creating mark
            author: Who is performing the rename

        Returns:
            The witness mark ID if witness provided, None otherwise

        Raises:
            ValueError: If old_path doesn't exist or new_path already exists
        """
        old_dir = self._entity_dir(old_path)
        new_dir = self._entity_dir(new_path)

        if not old_dir.exists():
            raise ValueError(f"Entity not found: {old_path}")

        if new_dir.exists():
            raise ValueError(f"Entity already exists at: {new_path}")

        # Create witness mark BEFORE rename (Theorem 10)
        mark_id: str | None = None
        if witness is not None:
            mark_result = await witness.save_mark(
                action=f"sovereign.rename: {old_path} → {new_path}",
                reasoning=f"Entity renamed from {old_path} to {new_path}",
                principles=["composable"],
                tags=["sovereign", "rename"],
                author=author,
            )
            mark_id = mark_result.mark_id

        # Ensure parent directories exist
        new_dir.parent.mkdir(parents=True, exist_ok=True)

        # Move the entire entity directory
        shutil.move(str(old_dir), str(new_dir))

        # Update metadata in all versions with new path and mark
        if update_references:
            for version_dir in new_dir.iterdir():
                if version_dir.is_dir() and version_dir.name.startswith("v"):
                    meta_file = version_dir / META_FILENAME
                    if meta_file.exists():
                        meta = json.loads(meta_file.read_text(encoding="utf-8"))
                        meta["path"] = new_path
                        meta["renamed_from"] = old_path
                        meta["renamed_at"] = datetime.now(UTC).isoformat()
                        if mark_id:
                            meta["rename_mark_id"] = mark_id
                        meta_file.write_text(
                            json.dumps(meta, indent=2, default=str),
                            encoding="utf-8",
                        )

        logger.info(f"Renamed {old_path} → {new_path}" + (f" (mark: {mark_id})" if mark_id else ""))
        return mark_id

    async def export_entity(
        self,
        path: str,
        include_overlay: bool = True,
        include_history: bool = False,
        witness: WitnessPersistence | None = None,
        export_mark_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Export an entity with its metadata for external use.

        Law 3: If witness is provided, export_mark_id must be provided too.
        The mark should have been created BEFORE calling this method.

        Returns a dictionary containing:
        - path: The entity path
        - content: Base64-encoded content (for binary safety)
        - content_hash: SHA256 hash
        - metadata: Ingest metadata
        - overlay: Annotations, edges, analysis (if include_overlay)
        - versions: List of version info (if include_history)
        - export_mark_id: Witness mark for this export (if witness provided)

        Args:
            path: Entity path to export
            include_overlay: Include overlay data
            include_history: Include version history
            witness: Optional WitnessPersistence for Law 3 compliance
            export_mark_id: Mark ID if witness is provided

        Returns:
            Export bundle dictionary
        """
        import base64

        # Law 3 enforcement: if witness provided, mark required
        if witness is not None and export_mark_id is None:
            raise ValueError("Law 3: witness provided but no export_mark_id. Create mark first!")

        entity = await self.get_current(path)
        if not entity:
            raise ValueError(f"Entity not found: {path}")

        export_data: dict[str, Any] = {
            "path": path,
            "content": base64.b64encode(entity.content).decode("ascii"),
            "content_hash": entity.content_hash,
            "metadata": entity.metadata,
            "version": entity.version,
            "exported_at": datetime.now(UTC).isoformat(),
        }

        # Law 3: Include mark ID if provided
        if export_mark_id:
            export_data["export_mark_id"] = export_mark_id

        if include_overlay:
            export_data["overlay"] = await self.get_overlay(path)

        if include_history:
            versions = await self.list_versions(path)
            version_info = []
            for v in versions:
                v_entity = await self.get_version(path, v)
                if v_entity:
                    version_info.append({
                        "version": v,
                        "content_hash": v_entity.content_hash,
                        "ingested_at": v_entity.metadata.get("ingested_at"),
                        "source": v_entity.metadata.get("source"),
                    })
            export_data["versions"] = version_info

        return export_data

    async def export_bundle(
        self,
        paths: list[str],
        format: str = "json",
        witness: WitnessPersistence | None = None,
        export_mark_id: str | None = None,
    ) -> bytes:
        """
        Export multiple entities as a bundle.

        Law 3: If witness is provided, export_mark_id must be provided too.
        The mark should have been created BEFORE calling this method.

        Args:
            paths: List of entity paths to export
            format: Export format ("json" or "zip")
            witness: Optional WitnessPersistence for Law 3 compliance
            export_mark_id: Mark ID if witness is provided

        Returns:
            Exported bundle as bytes
        """
        import io
        import zipfile

        # Law 3 enforcement: if witness provided, mark required
        if witness is not None and export_mark_id is None:
            raise ValueError("Law 3: witness provided but no export_mark_id. Create mark first!")

        if format == "json":
            bundle: dict[str, Any] = {
                "type": "sovereign_export",
                "exported_at": datetime.now(UTC).isoformat(),
                "entity_count": len(paths),
                "entities": [],
            }
            entities_list: list[dict[str, Any]] = bundle["entities"]

            # Law 3: Include mark ID if provided
            if export_mark_id:
                bundle["export_mark_id"] = export_mark_id

            for path in paths:
                try:
                    entity_data = await self.export_entity(
                        path,
                        include_overlay=True,
                        include_history=True,
                        witness=witness,
                        export_mark_id=export_mark_id,
                    )
                    entities_list.append(entity_data)
                except ValueError as e:
                    logger.warning(f"Skipping {path}: {e}")
                    entities_list.append({"path": path, "error": str(e)})

            return json.dumps(bundle, indent=2).encode("utf-8")

        elif format == "zip":
            buffer = io.BytesIO()

            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                manifest: dict[str, Any] = {
                    "type": "sovereign_export",
                    "exported_at": datetime.now(UTC).isoformat(),
                    "entity_count": len(paths),
                    "entities": [],
                }
                manifest_entities: list[dict[str, Any]] = manifest["entities"]

                # Law 3: Include mark ID if provided
                if export_mark_id:
                    manifest["export_mark_id"] = export_mark_id

                for path in paths:
                    try:
                        entity = await self.get_current(path)
                        if entity:
                            # Add content file
                            zf.writestr(path, entity.content)

                            # Add metadata
                            meta_path = f".meta/{path}.json"
                            entity_data = await self.export_entity(
                                path,
                                witness=witness,
                                export_mark_id=export_mark_id,
                            )
                            del entity_data["content"]  # Already in file
                            zf.writestr(meta_path, json.dumps(entity_data, indent=2))

                            manifest_entities.append({"path": path, "status": "ok"})
                    except ValueError as e:
                        manifest_entities.append({"path": path, "error": str(e)})

                # Add manifest
                zf.writestr("manifest.json", json.dumps(manifest, indent=2))

            buffer.seek(0)
            return buffer.read()

        else:
            raise ValueError(f"Unknown format: {format}")

    async def get_references_to(self, path: str) -> list[dict[str, Any]]:
        """
        Find all entities that reference the given path.

        Useful for checking before delete/rename operations.

        Args:
            path: Entity path to find references to

        Returns:
            List of {path, edge_type, line} for each reference
        """
        references = []

        for entity_path in await self.list_all():
            overlay = await self.get_overlay(entity_path)
            edges_data = overlay.get("edges", {})

            # Handle both old format (list) and new format (dict with "edges" key)
            if isinstance(edges_data, dict):
                edges = edges_data.get("edges", [])
            else:
                edges = edges_data if isinstance(edges_data, list) else []

            for edge in edges:
                if edge.get("target") == path:
                    references.append({
                        "from_path": entity_path,
                        "edge_type": edge.get("edge_type", "references"),
                        "line": edge.get("line_number"),
                        "context": edge.get("context"),
                    })

        return references

    # =========================================================================
    # Edge Management (Phase 4: K-Block/Document Unification)
    # =========================================================================

    async def add_edge(
        self,
        from_path: str,
        to_path: str,
        edge_type: str,
        mark_id: str | None = None,
        context: str | None = None,
    ) -> str:
        """
        Add an edge from one K-Block to another.

        Stores in both:
        - from_path's overlay/derived/edges.json (outgoing)
        - to_path's overlay/derived/edges.json (incoming)

        Args:
            from_path: Source entity path
            to_path: Target entity path
            edge_type: Type of edge (e.g., "derives_from", "references")
            mark_id: Optional witness mark ID linking this edge creation
            context: Optional context or reasoning for this edge

        Returns:
            The edge ID
        """
        from uuid import uuid4

        edge_id = f"edge-{uuid4().hex[:8]}"

        # Store outgoing edge
        outgoing = await self.get_overlay(from_path, "edges") or {"edges": []}
        outgoing_edges: list[dict[str, Any]] = outgoing.get("edges", [])
        outgoing_edges.append({
            "id": edge_id,
            "target": to_path,
            "type": edge_type,
            "mark_id": mark_id,
            "context": context,
            "created_at": datetime.now(UTC).isoformat(),
            "direction": "outgoing",
        })
        outgoing["edges"] = outgoing_edges
        await self.store_overlay(from_path, "edges", outgoing)

        # Store incoming edge
        incoming = await self.get_overlay(to_path, "edges") or {"edges": []}
        incoming_edges: list[dict[str, Any]] = incoming.get("edges", [])
        incoming_edges.append({
            "id": edge_id,
            "source": from_path,
            "type": edge_type,
            "mark_id": mark_id,
            "context": context,
            "created_at": datetime.now(UTC).isoformat(),
            "direction": "incoming",
        })
        incoming["edges"] = incoming_edges
        await self.store_overlay(to_path, "edges", incoming)

        logger.debug(f"Added edge {edge_id}: {from_path} --[{edge_type}]--> {to_path}")
        return edge_id

    async def get_edges(self, path: str, direction: str = "both") -> list[dict[str, Any]]:
        """
        Get edges for a K-Block.

        Args:
            path: Entity path
            direction: "outgoing", "incoming", or "both"

        Returns:
            List of edge dictionaries
        """
        overlay = await self.get_overlay(path, "edges") or {"edges": []}
        edges: list[dict[str, Any]] = overlay.get("edges", [])

        if direction == "both":
            return edges
        return [e for e in edges if e.get("direction") == direction]

    async def remove_edge(self, edge_id: str, from_path: str, to_path: str) -> bool:
        """
        Remove an edge between two K-Blocks.

        Args:
            edge_id: The edge ID to remove
            from_path: Source entity path
            to_path: Target entity path

        Returns:
            True if edge was removed, False if not found
        """
        # Remove from source
        outgoing = await self.get_overlay(from_path, "edges") or {"edges": []}
        outgoing_edges: list[dict[str, Any]] = outgoing.get("edges", [])
        outgoing["edges"] = [e for e in outgoing_edges if e.get("id") != edge_id]
        await self.store_overlay(from_path, "edges", outgoing)

        # Remove from target
        incoming = await self.get_overlay(to_path, "edges") or {"edges": []}
        incoming_edges: list[dict[str, Any]] = incoming.get("edges", [])
        incoming["edges"] = [e for e in incoming_edges if e.get("id") != edge_id]
        await self.store_overlay(to_path, "edges", incoming)

        logger.debug(f"Removed edge {edge_id}: {from_path} --> {to_path}")
        return True

    # =========================================================================
    # Law 3: Witnessed Export (Complete Pattern)
    # =========================================================================

    async def witnessed_export(
        self,
        paths: list[str],
        witness: WitnessPersistence,
        author: str = "kent",
        reasoning: str | None = None,
        format: str = "json",
    ) -> ExportBundle:
        """
        Export entities with full witness trail (Law 3 compliance).

        This method implements the complete Law 3 pattern from the spec:
        1. Create export mark BEFORE gathering content
        2. Gather entities with provenance
        3. Return ExportBundle with mark_id and entities

        Law 3 Guarantee: ∀ export operation o on entity e:
            ∃ mark m such that m.action = "sovereign.export" ∧ m.entity_path = e.path

        Args:
            paths: List of entity paths to export
            witness: WitnessPersistence for creating the mark
            author: Who is exporting (default: "kent")
            reasoning: Why this export is happening
            format: Export format ("json" or "zip")

        Returns:
            ExportBundle with export_mark_id and entities

        Example:
            >>> bundle = await store.witnessed_export(
            ...     paths=["spec/protocols/k-block.md"],
            ...     witness=witness_persistence,
            ...     author="kent",
            ...     reasoning="Archiving Crown Jewel specifications",
            ... )
            >>> print(f"Exported {bundle.entity_count} entities with mark {bundle.export_mark_id}")
        """
        # 1. Create export mark BEFORE export (Law 3)
        if reasoning is None:
            reasoning = f"Export requested by {author}"

        mark_result = await witness.save_mark(
            action=f"sovereign.export: {len(paths)} entities",
            reasoning=reasoning,
            principles=["ethical"],  # Data leaving our control
            tags=["export", format, "law3"],
            author=author,
        )

        export_mark_id = mark_result.mark_id
        logger.info(f"Created export mark {export_mark_id} for {len(paths)} entities")

        # 2. Gather entities with witness-enabled export
        entities: list[ExportedEntity] = []

        for path in paths:
            try:
                entity = await self.get_current(path)
                if not entity:
                    logger.warning(f"Skipping non-existent entity: {path}")
                    continue

                entities.append(
                    ExportedEntity(
                        path=path,
                        content=entity.content,
                        content_hash=entity.content_hash,
                        ingest_mark_id=entity.ingest_mark_id,
                        version=entity.version,
                        metadata=entity.metadata,
                        overlay=await self.get_overlay(path),
                    )
                )
            except Exception as e:
                logger.error(f"Error exporting {path}: {e}")
                # Continue with other entities

        # 3. Package and return
        bundle = ExportBundle(
            export_mark_id=export_mark_id,
            entities=entities,
            exported_at=datetime.now(UTC),
            export_format=format,
        )

        logger.info(
            f"Exported {bundle.entity_count} entities with witness mark {export_mark_id}"
        )
        return bundle


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "SovereignStore",
    "DEFAULT_SOVEREIGN_ROOT",
]
