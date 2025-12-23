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
]
