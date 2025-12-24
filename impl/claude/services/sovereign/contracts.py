"""
Sovereign Service Contracts: BE/FE type sync via AGENTESE contracts.

These dataclasses define the request/response shapes for each aspect.
The AGENTESE contract system generates TypeScript types from these.

See: docs/skills/agentese-contract-protocol.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# =============================================================================
# Manifest (concept.sovereign.manifest)
# =============================================================================


@dataclass
class SovereignManifestResponse:
    """Response for manifest aspect - sovereign store health."""

    entity_count: int
    total_versions: int
    storage_root: str
    last_ingest: str | None = None


# =============================================================================
# Ingest (concept.sovereign.ingest)
# =============================================================================


@dataclass
class IngestRequest:
    """Request to ingest a document."""

    path: str  # The claimed path (e.g., "spec/protocols/k-block.md")
    content: str  # The content (UTF-8 text)
    source: str = "api"  # Where it came from


@dataclass
class IngestResponse:
    """Response from ingest - the birth certificate."""

    path: str
    version: int
    ingest_mark_id: str
    edge_count: int


# =============================================================================
# Query (concept.sovereign.query)
# =============================================================================


@dataclass
class QueryRequest:
    """Request to query a sovereign entity."""

    path: str  # Entity path
    version: int | None = None  # Specific version (None = current)
    include_overlay: bool = True  # Include annotations/edges


@dataclass
class QueryResponse:
    """Response with entity content and metadata."""

    path: str
    version: int
    content: str
    content_hash: str
    ingest_mark_id: str | None
    overlay: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Diff (concept.sovereign.diff)
# =============================================================================


@dataclass
class DiffRequest:
    """Request to diff sovereign copy with source."""

    path: str
    source_content: str


@dataclass
class DiffResponse:
    """Response with diff result."""

    path: str
    diff_type: str  # "new", "unchanged", "modified", "deleted"
    our_hash: str | None = None
    source_hash: str | None = None


# =============================================================================
# List (concept.sovereign.list)
# =============================================================================


@dataclass
class ListRequest:
    """Request to list sovereign entities."""

    prefix: str = ""  # Filter by path prefix
    limit: int = 100


@dataclass
class ListResponse:
    """Response with entity paths."""

    paths: list[str]
    total: int


# =============================================================================
# Bootstrap (concept.sovereign.bootstrap)
# =============================================================================


@dataclass
class BootstrapRequest:
    """Request to bootstrap from filesystem."""

    root: str  # Root directory to scan
    pattern: str = "**/*"  # Glob pattern
    dry_run: bool = False  # If True, just count files


@dataclass
class BootstrapResponse:
    """Response from bootstrap operation."""

    files_found: int
    files_ingested: int
    edges_discovered: int
    duration_seconds: float
    dry_run: bool


# =============================================================================
# Sync (concept.sovereign.sync)
# =============================================================================


@dataclass
class SyncRequest:
    """Request to sync a file from source."""

    path: str
    source: str = "file"  # "file", "git", "memory"


@dataclass
class SyncResponse:
    """Response from sync operation."""

    path: str
    status: str  # "accepted", "rejected", "unchanged", "conflict", "error"
    old_version: int | None = None
    new_version: int | None = None
    message: str = ""


# =============================================================================
# Rename (concept.sovereign.rename)
# =============================================================================


@dataclass
class RenameRequest:
    """Request to rename/move an entity."""

    old_path: str
    new_path: str


@dataclass
class RenameResponse:
    """Response from rename operation."""

    old_path: str
    new_path: str
    success: bool
    message: str = ""


# =============================================================================
# Delete (concept.sovereign.delete)
# =============================================================================


@dataclass
class DeleteRequest:
    """Request to delete an entity."""

    path: str
    force: bool = False  # Force delete even with references


@dataclass
class DeleteResponse:
    """Response from delete operation."""

    path: str
    deleted: bool
    references: list[str] = field(default_factory=list)  # Entities that reference this
    message: str = ""


# =============================================================================
# Export (concept.sovereign.export)
# =============================================================================


@dataclass
class ExportRequest:
    """Request to export entities with witness trail (Law 3).

    AGENTESE: concept.sovereign.export
    """

    paths: list[str]
    format: str = "json"  # "json" or "zip"
    witness: bool = True  # Create witness mark for export (Law 3)
    reasoning: str = "Export via AGENTESE"  # Reasoning for witness mark


@dataclass
class ExportResponse:
    """Response from export operation with witness trail (Law 3).

    When witness is available:
    - export_mark_id: The witness mark for this export (Law 3 guarantee)
    - entities: List of exported entity metadata

    When no witness:
    - witness_mark_id: None
    - entities: Still populated, but no provenance guarantee
    """

    entity_count: int
    format: str
    export_mark_id: str | None = None  # Mark witnessing the export (Law 3)
    exported_at: str | None = None  # ISO timestamp
    entities: list[dict[str, str | int | None]] | None = None  # Entity metadata
    bundle_size_bytes: int | None = None  # For ZIP format


# =============================================================================
# Collection (concept.sovereign.collection.*)
# =============================================================================


@dataclass
class CollectionCreateRequest:
    """Request to create a collection."""

    name: str
    description: str | None = None
    paths: list[str] | None = None
    parent_id: str | None = None


@dataclass
class CollectionResponse:
    """Response with collection data."""

    id: str
    name: str
    description: str | None
    paths: list[str]
    parent_id: str | None
    analysis_status: str
    analyzed_count: int
    entity_count: int | None = None  # Resolved path count


@dataclass
class CollectionListResponse:
    """Response with list of collections."""

    collections: list[dict[str, Any]]
    total: int


@dataclass
class CollectionUpdateRequest:
    """Request to update a collection."""

    collection_id: str
    name: str | None = None
    description: str | None = None
    add_paths: list[str] | None = None
    remove_paths: list[str] | None = None


# =============================================================================
# Verify (concept.sovereign.verify)
# =============================================================================


@dataclass
class VerifyRequest:
    """Request to verify entity integrity."""

    path: str | None = None  # Specific entity (None = verify all)


@dataclass
class VerifyResponse:
    """Response from integrity verification."""

    path: str | None  # None if verifying all
    verified: bool
    issues: list[dict[str, Any]] = field(default_factory=list)
    entities_checked: int = 0
    message: str = ""


# =============================================================================
# References (concept.sovereign.references)
# =============================================================================


@dataclass
class ReferencesRequest:
    """Request to find references to an entity."""

    path: str


@dataclass
class ReferencesResponse:
    """Response with entities that reference the given path."""

    path: str
    referenced_by: list[dict[str, Any]]  # [{from_path, edge_type, line, context}]
    count: int


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Manifest
    "SovereignManifestResponse",
    # Ingest
    "IngestRequest",
    "IngestResponse",
    # Query
    "QueryRequest",
    "QueryResponse",
    # Diff
    "DiffRequest",
    "DiffResponse",
    # List
    "ListRequest",
    "ListResponse",
    # Bootstrap
    "BootstrapRequest",
    "BootstrapResponse",
    # Sync
    "SyncRequest",
    "SyncResponse",
    # File Management
    "RenameRequest",
    "RenameResponse",
    "DeleteRequest",
    "DeleteResponse",
    "ExportRequest",
    "ExportResponse",
    "VerifyRequest",
    "VerifyResponse",
    "ReferencesRequest",
    "ReferencesResponse",
    # Collections
    "CollectionCreateRequest",
    "CollectionResponse",
    "CollectionListResponse",
    "CollectionUpdateRequest",
]
