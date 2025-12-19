"""
L-gent Catalog: Registry & Core Types

The three-layer catalog architecture:
1. Registry: What exists? (flat index)
2. Lineage: Where from? (DAG ancestry) - see lineage.py
3. Lattice: How fits? (type partial order) - see lattice.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agents.d.persistent import PersistentAgent

# Re-export from types.py to avoid duplicate enum definitions
from agents.l.types import EntityType, Status

# Explicitly export re-imported types for mypy
__all__ = [
    "EntityType",
    "Status",
    "CatalogEntry",
    "Registry",
]


@dataclass
class CatalogEntry:
    """A single entry in the L-gent registry.

    Each entry represents one artifact in the kgents ecosystem,
    with metadata for discovery, provenance, and composition.
    """

    # Identity
    id: str  # Unique, immutable identifier
    entity_type: EntityType  # What kind of artifact
    name: str  # Human-readable name
    version: str  # Semantic version (e.g., "1.2.3")

    # Description (for semantic search)
    description: str  # Natural language purpose
    keywords: list[str]  # Manual tags for discovery
    embedding: list[float] | None = None  # Auto-generated semantic vector

    # Provenance
    author: str = "unknown"  # Creator identifier
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    forged_by: str | None = None  # F-gent instance that created it
    forged_from: str | None = None  # Intent/prompt that spawned it

    # Type information (for lattice)
    input_type: str | None = None  # For agents: input type signature
    output_type: str | None = None  # For agents: output type signature
    contracts_implemented: list[str] = field(default_factory=list)  # Contracts this satisfies
    contracts_required: list[str] = field(default_factory=list)  # Contracts this needs

    # Graph relationships (for lineage)
    relationships: dict[str, list[str]] = field(default_factory=dict)
    # Relationship types:
    # - "successor_to": Previous versions
    # - "forked_from": Parent artifact (branching)
    # - "depends_on": Runtime dependencies
    # - "tested_by": Associated test artifacts
    # - "documented_by": Associated spec documents
    # - "composes_with": Known good composition partners

    # Health metrics
    status: Status = Status.ACTIVE
    usage_count: int = 0
    success_rate: float = 1.0  # 0.0 to 1.0
    last_used: datetime | None = None
    last_error: str | None = None

    # Deprecation info
    deprecation_reason: str | None = None
    deprecated_in_favor_of: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "id": self.id,
            "entity_type": self.entity_type.value,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "keywords": self.keywords,
            "embedding": self.embedding,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "forged_by": self.forged_by,
            "forged_from": self.forged_from,
            "input_type": self.input_type,
            "output_type": self.output_type,
            "contracts_implemented": self.contracts_implemented,
            "contracts_required": self.contracts_required,
            "relationships": self.relationships,
            "status": self.status.value,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "last_error": self.last_error,
            "deprecation_reason": self.deprecation_reason,
            "deprecated_in_favor_of": self.deprecated_in_favor_of,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "CatalogEntry":
        """Reconstruct from dictionary."""
        return CatalogEntry(
            id=data["id"],
            entity_type=EntityType(data["entity_type"]),
            name=data["name"],
            version=data["version"],
            description=data["description"],
            keywords=data["keywords"],
            embedding=data.get("embedding"),
            author=data.get("author", "unknown"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            forged_by=data.get("forged_by"),
            forged_from=data.get("forged_from"),
            input_type=data.get("input_type"),
            output_type=data.get("output_type"),
            contracts_implemented=data.get("contracts_implemented", []),
            contracts_required=data.get("contracts_required", []),
            relationships=data.get("relationships", {}),
            status=Status(data.get("status", "active")),
            usage_count=data.get("usage_count", 0),
            success_rate=data.get("success_rate", 1.0),
            last_used=datetime.fromisoformat(data["last_used"]) if data.get("last_used") else None,
            last_error=data.get("last_error"),
            deprecation_reason=data.get("deprecation_reason"),
            deprecated_in_favor_of=data.get("deprecated_in_favor_of"),
        )


class Registry:
    """Layer 1: What exists in the ecosystem.

    The Registry is a persistent, indexed collection of CatalogEntries.
    It uses D-gent's PersistentAgent for storage.

    Indexing strategies:
    1. Primary: id → entry
    2. Type: entity_type → [entries]
    3. Author: author → [entries]
    4. Keyword: keyword → [entries]
    5. Contract: contract_name → [entries]
    6. Version: (name, version) → entry
    """

    def __init__(self, storage_path: str = ".kgents/catalog.json"):
        """Initialize registry with persistent storage."""
        self.storage = PersistentAgent(path=storage_path, schema=dict)
        self._entries: dict[str, CatalogEntry] = {}
        self._loaded = False

    async def _ensure_loaded(self) -> None:
        """Lazy load entries from storage."""
        if not self._loaded:
            try:
                data = await self.storage.load()
            except Exception:
                # If file doesn't exist or is corrupted, start with empty catalog
                data = {}

            self._entries = {
                entry_id: CatalogEntry.from_dict(entry_data)
                for entry_id, entry_data in data.items()
            }
            self._loaded = True

    async def register(self, entry: CatalogEntry) -> None:
        """Add or update an entry in the registry.

        If an entry with the same ID exists, it's updated.
        Otherwise, a new entry is created.
        """
        await self._ensure_loaded()

        # Update timestamp
        entry.updated_at = datetime.now()

        # Store in memory
        self._entries[entry.id] = entry

        # Persist to storage
        data = {entry_id: entry.to_dict() for entry_id, entry in self._entries.items()}
        await self.storage.save(data)

    async def get(self, entry_id: str) -> CatalogEntry | None:
        """Retrieve entry by ID."""
        await self._ensure_loaded()
        return self._entries.get(entry_id)

    async def list_all(self) -> list[CatalogEntry]:
        """Get all entries."""
        await self._ensure_loaded()
        return list(self._entries.values())

    async def list_entries(
        self,
        entity_type: EntityType | None = None,
        status: Status | None = None,
        author: str | None = None,
        limit: int | None = None,
    ) -> list[CatalogEntry]:
        """List entries with optional filters.

        Alias compatible with registry.Registry.list_entries().

        Args:
            entity_type: Filter by entity type
            status: Filter by status
            author: Filter by author
            limit: Maximum number of results

        Returns:
            List of matching entries, sorted by updated_at descending
        """
        await self._ensure_loaded()
        entries = list(self._entries.values())

        # Apply filters
        if entity_type is not None:
            entries = [e for e in entries if e.entity_type == entity_type]
        if status is not None:
            entries = [e for e in entries if e.status == status]
        if author is not None:
            entries = [e for e in entries if e.author == author]

        # Sort by updated_at descending (most recent first)
        entries.sort(key=lambda e: e.updated_at, reverse=True)

        # Apply limit
        if limit is not None:
            entries = entries[:limit]

        return entries

    async def list_by_type(self, entity_type: EntityType) -> list[CatalogEntry]:
        """Get all entries of a specific type."""
        await self._ensure_loaded()
        return [entry for entry in self._entries.values() if entry.entity_type == entity_type]

    async def list_by_author(self, author: str) -> list[CatalogEntry]:
        """Get all entries by a specific author."""
        await self._ensure_loaded()
        return [entry for entry in self._entries.values() if entry.author == author]

    async def list_by_status(self, status: Status) -> list[CatalogEntry]:
        """Get all entries with a specific status."""
        await self._ensure_loaded()
        return [entry for entry in self._entries.values() if entry.status == status]

    async def find_by_keyword(self, keyword: str) -> list[CatalogEntry]:
        """Find entries containing a specific keyword."""
        await self._ensure_loaded()
        keyword_lower = keyword.lower()
        return [
            entry
            for entry in self._entries.values()
            if keyword_lower in [kw.lower() for kw in entry.keywords]
        ]

    async def find_by_name_version(self, name: str, version: str) -> CatalogEntry | None:
        """Find entry by name and version."""
        await self._ensure_loaded()
        for entry in self._entries.values():
            if entry.name == name and entry.version == version:
                return entry
        return None

    async def deprecate(
        self, entry_id: str, reason: str, replacement_id: str | None = None
    ) -> None:
        """Mark an entry as deprecated.

        Args:
            entry_id: ID of entry to deprecate
            reason: Why it's being deprecated
            replacement_id: ID of recommended replacement (if any)
        """
        await self._ensure_loaded()

        entry = self._entries.get(entry_id)
        if not entry:
            raise ValueError(f"Entry {entry_id} not found")

        entry.status = Status.DEPRECATED
        entry.deprecation_reason = reason
        entry.deprecated_in_favor_of = replacement_id
        entry.updated_at = datetime.now()

        await self.register(entry)

    async def retire(self, entry_id: str) -> None:
        """Mark an entry as retired (no longer functional)."""
        await self._ensure_loaded()

        entry = self._entries.get(entry_id)
        if not entry:
            raise ValueError(f"Entry {entry_id} not found")

        entry.status = Status.RETIRED
        entry.updated_at = datetime.now()

        await self.register(entry)

    async def record_usage(
        self, entry_id: str, success: bool = True, error: str | None = None
    ) -> None:
        """Record usage of an entry.

        Updates usage count, success rate, last used timestamp.
        """
        await self._ensure_loaded()

        entry = self._entries.get(entry_id)
        if not entry:
            raise ValueError(f"Entry {entry_id} not found")

        # Update usage metrics
        entry.usage_count += 1
        entry.last_used = datetime.now()

        # Update success rate (exponential moving average)
        alpha = 0.1  # Weight for new observation
        if success:
            entry.success_rate = alpha * 1.0 + (1 - alpha) * entry.success_rate
            entry.last_error = None
        else:
            entry.success_rate = alpha * 0.0 + (1 - alpha) * entry.success_rate
            entry.last_error = error

        await self.register(entry)
