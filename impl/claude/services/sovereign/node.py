"""
Sovereign AGENTESE Node: @node("concept.sovereign")

Exposes Inbound Sovereignty through the universal AGENTESE protocol.

AGENTESE Paths:
- concept.sovereign.manifest   - Store health, entity count, storage location
- concept.sovereign.ingest     - Ingest a document (create birth certificate)
- concept.sovereign.query      - Query sovereign copy with full provenance
- concept.sovereign.list       - List all sovereign entities
- concept.sovereign.diff       - Compare with external source
- concept.sovereign.bootstrap  - One-time migration from filesystem
- concept.sovereign.sync       - Sync a single file (re-ingest if changed)
- concept.sovereign.verify     - Verify integrity of entity/all
- concept.sovereign.export     - Export with witness mark
- concept.sovereign.rename     - Rename with witness
- concept.sovereign.delete     - Safe delete with witness
- concept.sovereign.references - Find what references a path

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

Philosophy:
    "We don't reference. We possess."
    "The file is a lie. There is only the witnessed entity."

See: spec/protocols/inbound-sovereignty.md
See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from protocols.agentese.affordances import AspectCategory, aspect
from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import (
    BootstrapRequest,
    BootstrapResponse,
    DeleteRequest,
    DeleteResponse,
    DiffRequest,
    DiffResponse,
    ExportRequest,
    ExportResponse,
    IngestRequest,
    IngestResponse,
    ListRequest,
    ListResponse,
    QueryRequest,
    QueryResponse,
    ReferencesRequest,
    ReferencesResponse,
    RenameRequest,
    RenameResponse,
    SovereignManifestResponse,
    SyncRequest,
    SyncResponse,
    VerifyRequest,
    VerifyResponse,
)
from .ingest import Ingestor
from .store import SovereignStore
from .types import IngestEvent

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from services.witness.persistence import WitnessPersistence


# =============================================================================
# Rendering Types
# =============================================================================


@dataclass(frozen=True)
class SovereignManifestRendering:
    """Rendering for sovereign store manifest."""

    entity_count: int
    total_versions: int
    storage_root: str
    last_ingest: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "sovereign_manifest",
            "entity_count": self.entity_count,
            "total_versions": self.total_versions,
            "storage_root": self.storage_root,
            "last_ingest": self.last_ingest,
        }

    def to_text(self) -> str:
        lines = [
            "Sovereign Store Status",
            "======================",
            f"Entities: {self.entity_count}",
            f"Total Versions: {self.total_versions}",
            f"Storage: {self.storage_root}",
        ]
        if self.last_ingest:
            lines.append(f"Last Ingest: {self.last_ingest}")
        return "\n".join(lines)


# =============================================================================
# SovereignNode
# =============================================================================


@node(
    "concept.sovereign",
    description="Inbound Sovereignty - Data enters, is witnessed, never leaves without consent",
    # Note: sovereign_store is OPTIONAL - we create one if not injected
    # This enables direct instantiation for CLI resolution
    contracts={
        # Perception aspects
        "manifest": Response(SovereignManifestResponse),
        "list": Contract(ListRequest, ListResponse),
        "query": Contract(QueryRequest, QueryResponse),
        "diff": Contract(DiffRequest, DiffResponse),
        "verify": Contract(VerifyRequest, VerifyResponse),
        "references": Contract(ReferencesRequest, ReferencesResponse),
        # Mutation aspects
        "ingest": Contract(IngestRequest, IngestResponse),
        "bootstrap": Contract(BootstrapRequest, BootstrapResponse),
        "sync": Contract(SyncRequest, SyncResponse),
        "export": Contract(ExportRequest, ExportResponse),
        "rename": Contract(RenameRequest, RenameResponse),
        "delete": Contract(DeleteRequest, DeleteResponse),
    },
    examples=[
        ("manifest", {}, "Show sovereign store status"),
        ("list", {"prefix": "spec/"}, "List entities under spec/"),
        ("query", {"path": "spec/protocols/k-block.md"}, "Query entity with overlay"),
        ("ingest", {"path": "spec/new.md", "content": "# New Spec"}, "Ingest document"),
        ("bootstrap", {"root": "spec/", "dry_run": True}, "Preview bootstrap"),
        ("sync", {"path": "spec/protocols/k-block.md"}, "Sync single file"),
        ("verify", {"path": "spec/protocols/k-block.md"}, "Verify entity integrity"),
        ("export", {"paths": ["spec/protocols/k-block.md"], "format": "json"}, "Export entity"),
        ("rename", {"old_path": "spec/old.md", "new_path": "spec/new.md"}, "Rename entity"),
        ("delete", {"path": "spec/deprecated.md"}, "Safe delete entity"),
        ("references", {"path": "spec/protocols/k-block.md"}, "Find references"),
    ],
)
class SovereignNode(BaseLogosNode):
    """
    AGENTESE node for Inbound Sovereignty.

    Exposes the sovereign store and ingestor through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/concept/sovereign/ingest
        {"path": "spec/my-spec.md", "content": "# My Spec"}

        # Via Logos directly
        await logos.invoke("concept.sovereign.query", observer, path="spec/...")

        # Via CLI
        kg sovereign ingest spec/my-spec.md
    """

    def __init__(
        self,
        sovereign_store: SovereignStore | None = None,
        witness_persistence: "WitnessPersistence | None" = None,
    ) -> None:
        """
        Initialize SovereignNode.

        Args:
            sovereign_store: The sovereign store (optional, creates default if not provided)
            witness_persistence: Optional witness for marks
        """
        # Create default store if not provided (enables direct instantiation)
        if sovereign_store is None:
            sovereign_store = SovereignStore()
        self._store = sovereign_store
        self._witness = witness_persistence
        self._ingestor = Ingestor(sovereign_store, witness_persistence)
        self._last_ingest: str | None = None

    @property
    def handle(self) -> str:
        return "concept.sovereign"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Trust-gated access:
        - developer/operator/cli: Full access including bootstrap
        - architect: Query, list, diff, verify, references (no mutations)
        - newcomer/guest: Manifest only
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators, CLI
        # CLI gets full access because it's a local operation with file access
        if archetype_lower in ("developer", "operator", "admin", "system", "cli"):
            return (
                "manifest",
                "list",
                "query",
                "diff",
                "verify",
                "references",
                "ingest",
                "bootstrap",
                "sync",
                "export",
                "rename",
                "delete",
            )

        # Read access: architects, researchers
        if archetype_lower in ("architect", "artist", "researcher", "technical"):
            return ("manifest", "list", "query", "diff", "verify", "references")

        # Minimal: newcomers, guests
        return ("manifest",)

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Sovereign store health and statistics",
    )
    async def manifest(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Manifest sovereign store status.

        AGENTESE: concept.sovereign.manifest
        """
        entity_count = await self._store.count()
        total_versions = await self._store.total_versions()

        return SovereignManifestRendering(
            entity_count=entity_count,
            total_versions=total_versions,
            storage_root=str(self._store.root),
            last_ingest=self._last_ingest,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to appropriate methods."""

        if aspect == "list":
            prefix = kwargs.get("prefix", "")
            limit = kwargs.get("limit", 100)

            all_paths = await self._store.list_all()

            # Filter by prefix
            if prefix:
                paths = [p for p in all_paths if p.startswith(prefix)]
            else:
                paths = all_paths

            # Apply limit
            paths = paths[:limit]

            return {
                "paths": paths,
                "total": len(all_paths),
            }

        elif aspect == "query":
            # Accept both "path" and "entity_path" (CLI uses entity_path to avoid conflict)
            entity_path = kwargs.get("entity_path") or kwargs.get("path", "")
            version = kwargs.get("version")
            include_overlay = kwargs.get("include_overlay", True)

            if not entity_path:
                return {"error": "path required"}

            if version:
                entity = await self._store.get_version(entity_path, version)
            else:
                entity = await self._store.get_current(entity_path)

            if not entity:
                return {"error": f"Entity not found: {entity_path}"}

            result: dict[str, Any] = {
                "path": entity.path,
                "version": entity.version,
                "content": entity.content_text,
                "content_hash": entity.content_hash,
                "ingest_mark_id": entity.ingest_mark_id,
            }

            if include_overlay:
                result["overlay"] = entity.overlay

            return result

        elif aspect == "diff":
            # Accept both "path" and "entity_path" (CLI uses entity_path to avoid conflict)
            entity_path = kwargs.get("entity_path") or kwargs.get("path", "")
            source_content = kwargs.get("source_content", "")

            if not entity_path:
                return {"error": "path required"}
            if not source_content:
                return {"error": "source_content required"}

            # Convert to bytes for diff
            source_bytes = source_content.encode("utf-8")
            diff = await self._store.diff_with_source(entity_path, source_bytes)

            return {
                "path": entity_path,
                "diff_type": diff.diff_type.name.lower(),
                "our_hash": diff.our_hash,
                "source_hash": diff.source_hash,
            }

        elif aspect == "ingest":
            # Accept both "path" and "claimed_path" (CLI uses claimed_path to avoid conflict)
            claimed_path = kwargs.get("claimed_path") or kwargs.get("path", "")
            content = kwargs.get("content", "")
            source = kwargs.get("source", "api")

            if not claimed_path:
                return {"error": "path required"}
            if not content:
                return {"error": "content required"}

            # Create ingest event
            event = IngestEvent.from_content(
                content=content,
                claimed_path=claimed_path,
                source=source,
            )

            # Ingest
            ingest_result = await self._ingestor.ingest(event)
            self._last_ingest = claimed_path

            return {
                "path": ingest_result.path,
                "version": ingest_result.version,
                "ingest_mark_id": ingest_result.ingest_mark_id,
                "edge_count": ingest_result.edge_count,
            }

        elif aspect == "bootstrap":
            root = kwargs.get("root", "")
            pattern = kwargs.get("pattern", "**/*")
            dry_run = kwargs.get("dry_run", False)

            if not root:
                return {"error": "root required"}

            root_path = Path(root)
            if not root_path.exists():
                return {"error": f"Root path does not exist: {root}"}

            start_time = time.time()
            files_found = 0
            files_ingested = 0
            total_edges = 0

            # Find all matching files
            for file_path in root_path.glob(pattern):
                if file_path.is_file():
                    files_found += 1

                    if not dry_run:
                        try:
                            event = IngestEvent.from_file(
                                file_path,
                                source=f"bootstrap:{root}",
                            )
                            # Adjust claimed_path to be relative to root
                            relative_path = str(file_path.relative_to(root_path))
                            event = IngestEvent(
                                source=event.source,
                                content_hash=event.content_hash,
                                content=event.content,
                                claimed_path=relative_path,
                                source_timestamp=event.source_timestamp,
                            )

                            file_result = await self._ingestor.ingest(event)
                            files_ingested += 1
                            total_edges += file_result.edge_count
                        except Exception:
                            # Skip files that fail to ingest
                            pass

            duration = time.time() - start_time

            return {
                "files_found": files_found,
                "files_ingested": files_ingested,
                "edges_discovered": total_edges,
                "duration_seconds": round(duration, 2),
                "dry_run": dry_run,
            }

        elif aspect == "sync":
            # Accept both "path" and "entity_path" (CLI uses entity_path to avoid conflict)
            entity_path = kwargs.get("entity_path") or kwargs.get("path", "")
            source = kwargs.get("source", "file")

            if not entity_path:
                return {"error": "path required"}

            # Get current entity
            current = await self._store.get_current(entity_path)

            # For file source, read from filesystem
            if source == "file":
                file_path = Path(entity_path)
                if not file_path.exists():
                    if current:
                        return {
                            "path": entity_path,
                            "status": "deleted",
                            "message": "Source file no longer exists",
                        }
                    return {
                        "path": entity_path,
                        "status": "error",
                        "message": "File not found and no sovereign copy exists",
                    }

                new_content = file_path.read_bytes()
            else:
                return {"error": f"Unsupported source: {source}"}

            # Check if changed
            diff = await self._store.diff_with_source(entity_path, new_content)

            if not diff.is_changed:
                return {
                    "path": entity_path,
                    "status": "unchanged",
                    "old_version": current.version if current else None,
                    "message": "No change detected",
                }

            # Re-ingest
            sync_result = await self._ingestor.reingest(
                path=entity_path,
                new_content=new_content,
                source=f"sync:{source}",
            )

            return {
                "path": entity_path,
                "status": "accepted",
                "old_version": current.version if current else None,
                "new_version": sync_result.version,
                "message": f"Synced to v{sync_result.version}",
            }

        elif aspect == "verify":
            # Accept both "path" and "entity_path"
            entity_path = kwargs.get("entity_path") or kwargs.get("path")

            issues = []
            entities_checked = 0

            if entity_path:
                # Verify single entity
                entity = await self._store.get_current(entity_path)
                if not entity:
                    return {
                        "path": entity_path,
                        "verified": False,
                        "entities_checked": 0,
                        "message": f"Entity not found: {entity_path}",
                    }

                # Basic integrity check: can we read content and hash matches
                import hashlib
                actual_hash = hashlib.sha256(entity.content).hexdigest()
                if actual_hash != entity.content_hash:
                    issues.append({
                        "path": entity_path,
                        "issue": "hash_mismatch",
                        "expected": entity.content_hash,
                        "actual": actual_hash,
                    })

                entities_checked = 1

                return {
                    "path": entity_path,
                    "verified": len(issues) == 0,
                    "issues": issues,
                    "entities_checked": entities_checked,
                    "message": "Integrity verified" if not issues else "Integrity issues found",
                }
            else:
                # Verify all entities
                all_paths = await self._store.list_all()

                for path in all_paths:
                    entity = await self._store.get_current(path)
                    if entity:
                        import hashlib
                        actual_hash = hashlib.sha256(entity.content).hexdigest()
                        if actual_hash != entity.content_hash:
                            issues.append({
                                "path": path,
                                "issue": "hash_mismatch",
                                "expected": entity.content_hash,
                                "actual": actual_hash,
                            })
                        entities_checked += 1

                return {
                    "path": None,
                    "verified": len(issues) == 0,
                    "issues": issues,
                    "entities_checked": entities_checked,
                    "message": f"Verified {entities_checked} entities" if not issues else f"Found {len(issues)} issues",
                }

        elif aspect == "export":
            paths = kwargs.get("paths", [])
            format_type = kwargs.get("format", "json")
            witness = kwargs.get("witness", True)
            reasoning = kwargs.get("reasoning", "Export via AGENTESE")

            if not paths:
                return {"error": "paths required"}

            # Use witnessed_export if witness is available and requested
            if witness and self._witness:
                bundle = await self._store.witnessed_export(
                    paths=paths,
                    witness=self._witness,
                    format=format_type,
                    reasoning=reasoning,
                )

                return {
                    "export_mark_id": bundle.export_mark_id,
                    "entity_count": bundle.entity_count,
                    "format": bundle.export_format,
                    "exported_at": bundle.exported_at.isoformat(),
                    "entities": [
                        {
                            "path": e.path,
                            "content_hash": e.content_hash,
                            "ingest_mark_id": e.ingest_mark_id,
                            "version": e.version,
                        }
                        for e in bundle.entities
                    ],
                }
            else:
                # Fallback: export without witness (legacy)
                bundle_data = await self._store.export_bundle(paths, format=format_type)

                import json
                if isinstance(bundle_data, bytes):
                    # ZIP format returns bytes
                    return {
                        "entity_count": len(paths),
                        "format": format_type,
                        "bundle_size_bytes": len(bundle_data),
                        "witness_mark_id": None,
                    }
                else:
                    # JSON format returns dict via loads
                    data = json.loads(bundle_data)
                    return {
                        "entity_count": len(data.get("entities", [])),
                        "format": format_type,
                        "entities": data.get("entities", []),
                        "witness_mark_id": None,
                    }

        elif aspect == "rename":
            old_path = kwargs.get("old_path", "")
            new_path = kwargs.get("new_path", "")

            if not old_path or not new_path:
                return {"error": "old_path and new_path required"}

            try:
                success = await self._store.rename(old_path, new_path)

                # Create witness mark
                if success and self._witness:
                    await self._witness.save_mark(
                        action="rename",
                        reasoning=f"Renamed {old_path} → {new_path}",
                        tags=["rename", "file_management"],
                    )

                return {
                    "old_path": old_path,
                    "new_path": new_path,
                    "success": success,
                    "message": f"Renamed {old_path} → {new_path}" if success else "Rename failed",
                }

            except ValueError as e:
                return {
                    "old_path": old_path,
                    "new_path": new_path,
                    "success": False,
                    "message": str(e),
                }

        elif aspect == "delete":
            entity_path = kwargs.get("entity_path") or kwargs.get("path", "")
            force = kwargs.get("force", False)

            if not entity_path:
                return {"error": "path required"}

            # Check for references unless force
            references: list[str] = []
            if not force:
                refs = await self._store.get_references_to(entity_path)
                if refs:
                    return {
                        "path": entity_path,
                        "deleted": False,
                        "references": [r["from_path"] for r in refs],
                        "message": f"Entity is referenced by {len(refs)} others. Use force=true to delete anyway.",
                    }

            # Delete
            deleted = await self._store.delete(entity_path)

            # Create witness mark
            if deleted and self._witness:
                await self._witness.save_mark(
                    action="delete",
                    reasoning=f"Deleted {entity_path}" + (" (forced)" if force else ""),
                    tags=["delete", "file_management"] + (["forced"] if force else []),
                )

            return {
                "path": entity_path,
                "deleted": deleted,
                "references": references,
                "message": "Deleted successfully" if deleted else "Entity not found",
            }

        elif aspect == "references":
            entity_path = kwargs.get("entity_path") or kwargs.get("path", "")

            if not entity_path:
                return {"error": "path required"}

            refs = await self._store.get_references_to(entity_path)

            return {
                "path": entity_path,
                "referenced_by": refs,
                "count": len(refs),
            }

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "SovereignNode",
    "SovereignManifestRendering",
]
