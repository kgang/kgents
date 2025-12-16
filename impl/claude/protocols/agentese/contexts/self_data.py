"""
AGENTESE Self Data Context

Data persistence nodes for self.data.* paths:
- DataNode: The agent's data persistence layer (D-gent)

Part of the Data Architecture Rewrite (plans/data-architecture-rewrite.md).
Provides AGENTESE access to the new simplified D-gent API.

Five core operations: put, get, delete, list, causal_chain
Plus: exists, count, backend (diagnostics)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Data Affordances ===

DATA_AFFORDANCES: tuple[str, ...] = (
    # Core 5 methods (DgentProtocol)
    "put",           # Store datum
    "get",           # Retrieve datum by ID
    "delete",        # Remove datum
    "list",          # List data with filters
    "causal_chain",  # Get causal ancestors
    # Additional methods
    "exists",        # Check if datum exists
    "count",         # Count total data
    # Diagnostics
    "backend",       # Show current backend info
    "stats",         # Storage statistics
)


# === Data Node ===


@dataclass
class DataNode(BaseLogosNode):
    """
    self.data - The agent's data persistence layer.

    Provides access to D-gent operations via AGENTESE:
    - put: Store datum, return ID
    - get: Retrieve datum by ID
    - delete: Remove datum
    - list: List data with optional filters
    - causal_chain: Get causal ancestors

    AGENTESE: self.data.*

    Architecture (Projection Lattice):
        Memory (Tier 0) → JSONL (Tier 1) → SQLite (Tier 2) → Postgres (Tier 3)

    Selection: DgentRouter automatically selects the best available backend.
    """

    _handle: str = "self.data"

    # D-gent backend (injected via create_data_resolver)
    _dgent: Any = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Data affordances available to all archetypes."""
        return DATA_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View current data storage state."""
        if self._dgent is None:
            return BasicRendering(
                summary="Data Storage (Not Configured)",
                content="D-gent not configured. Wire via create_data_resolver().",
                metadata={"configured": False},
            )

        # Get stats from backend
        count = await self._dgent.count()
        backend_name = type(self._dgent).__name__

        return BasicRendering(
            summary="Data Storage State",
            content=f"Backend: {backend_name}\nData count: {count}",
            metadata={
                "configured": True,
                "backend": backend_name,
                "count": count,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle data-specific aspects."""
        match aspect:
            case "put":
                return await self._put(observer, **kwargs)
            case "get":
                return await self._get(observer, **kwargs)
            case "delete":
                return await self._delete(observer, **kwargs)
            case "list":
                return await self._list(observer, **kwargs)
            case "causal_chain":
                return await self._causal_chain(observer, **kwargs)
            case "exists":
                return await self._exists(observer, **kwargs)
            case "count":
                return await self._count(observer, **kwargs)
            case "backend":
                return await self._backend(observer, **kwargs)
            case "stats":
                return await self._stats(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # === Core Operations ===

    async def _put(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Store datum and return ID.

        AGENTESE: self.data.put[content="...", metadata={...}]

        Args:
            content: The content to store (required)
            metadata: Optional metadata dict
            causal_parent: Optional causal parent ID

        Returns:
            Dict with datum ID and storage confirmation
        """
        if self._dgent is None:
            return {"error": "D-gent not configured"}

        content = kwargs.get("content")
        if content is None:
            return {
                "error": "content is required",
                "usage": "self.data.put[content='your data here']",
            }

        # Import Datum from the new architecture
        from agents.d.datum import Datum

        datum = Datum.create(
            content=content,
            causal_parent=kwargs.get("causal_parent"),
            metadata=kwargs.get("metadata", {}),
        )

        datum_id = await self._dgent.put(datum)

        return {
            "status": "stored",
            "id": datum_id,
            "content_preview": str(content)[:100],
        }

    async def _get(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Retrieve datum by ID.

        AGENTESE: self.data.get[id="..."]

        Args:
            id: The datum ID to retrieve (required)

        Returns:
            Dict with datum content or not found error
        """
        if self._dgent is None:
            return {"error": "D-gent not configured"}

        datum_id = kwargs.get("id")
        if datum_id is None:
            return {
                "error": "id is required",
                "usage": "self.data.get[id='datum_id_here']",
            }

        datum = await self._dgent.get(datum_id)

        if datum is None:
            return {"status": "not_found", "id": datum_id}

        return {
            "status": "found",
            "id": datum.id,
            "content": datum.content,
            "created_at": datum.created_at,
            "causal_parent": datum.causal_parent,
            "metadata": datum.metadata,
        }

    async def _delete(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Remove datum by ID.

        AGENTESE: self.data.delete[id="..."]

        Args:
            id: The datum ID to delete (required)

        Returns:
            Dict with deletion confirmation
        """
        if self._dgent is None:
            return {"error": "D-gent not configured"}

        datum_id = kwargs.get("id")
        if datum_id is None:
            return {
                "error": "id is required",
                "usage": "self.data.delete[id='datum_id_here']",
            }

        success = await self._dgent.delete(datum_id)

        return {
            "status": "deleted" if success else "not_found",
            "id": datum_id,
        }

    async def _list(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        List data with optional filters.

        AGENTESE: self.data.list
                  self.data.list[prefix="...", limit=10]

        Args:
            prefix: Filter to IDs starting with this prefix
            after: Filter to data created after this Unix timestamp
            limit: Maximum results (default 100)

        Returns:
            Dict with list of matching data
        """
        if self._dgent is None:
            return {"error": "D-gent not configured"}

        prefix = kwargs.get("prefix")
        after = kwargs.get("after")
        limit = kwargs.get("limit", 100)

        data = await self._dgent.list(prefix=prefix, after=after, limit=limit)

        return {
            "status": "ok",
            "count": len(data),
            "data": [
                {
                    "id": d.id,
                    "content_preview": str(d.content)[:50],
                    "created_at": d.created_at,
                }
                for d in data
            ],
            "filters": {
                "prefix": prefix,
                "after": after,
                "limit": limit,
            },
        }

    async def _causal_chain(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get causal ancestors of a datum.

        AGENTESE: self.data.causal_chain[id="..."]

        Follows causal_parent links to build the full lineage.
        If A → B → C, returns [A, B, C] (oldest to newest).

        Args:
            id: The datum ID to trace ancestry for (required)

        Returns:
            Dict with causal chain from oldest to newest
        """
        if self._dgent is None:
            return {"error": "D-gent not configured"}

        datum_id = kwargs.get("id")
        if datum_id is None:
            return {
                "error": "id is required",
                "usage": "self.data.causal_chain[id='datum_id_here']",
            }

        chain = await self._dgent.causal_chain(datum_id)

        return {
            "status": "ok",
            "id": datum_id,
            "chain_length": len(chain),
            "chain": [
                {
                    "id": d.id,
                    "content_preview": str(d.content)[:50],
                    "created_at": d.created_at,
                }
                for d in chain
            ],
        }

    # === Additional Operations ===

    async def _exists(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Check if datum exists.

        AGENTESE: self.data.exists[id="..."]

        Args:
            id: The datum ID to check (required)

        Returns:
            Dict with existence status
        """
        if self._dgent is None:
            return {"error": "D-gent not configured"}

        datum_id = kwargs.get("id")
        if datum_id is None:
            return {
                "error": "id is required",
                "usage": "self.data.exists[id='datum_id_here']",
            }

        exists = await self._dgent.exists(datum_id)

        return {"id": datum_id, "exists": exists}

    async def _count(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Count total number of data stored.

        AGENTESE: self.data.count

        Returns:
            Dict with total count
        """
        if self._dgent is None:
            return {"error": "D-gent not configured"}

        count = await self._dgent.count()

        return {"count": count}

    # === Diagnostics ===

    async def _backend(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Show current backend information.

        AGENTESE: self.data.backend

        Returns:
            Dict with backend type and configuration
        """
        if self._dgent is None:
            return {"error": "D-gent not configured"}

        backend_name = type(self._dgent).__name__

        # Check if it's a router (multi-backend)
        if hasattr(self._dgent, "backends"):
            return {
                "type": "router",
                "backends": [type(b).__name__ for b in self._dgent.backends],
                "active": backend_name,
            }

        return {
            "type": "single",
            "backend": backend_name,
        }

    async def _stats(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get storage statistics.

        AGENTESE: self.data.stats

        Returns:
            Dict with storage statistics
        """
        if self._dgent is None:
            return {"error": "D-gent not configured"}

        count = await self._dgent.count()
        backend_name = type(self._dgent).__name__

        stats = {
            "backend": backend_name,
            "count": count,
        }

        # Add bus stats if bus-enabled
        if hasattr(self._dgent, "bus"):
            stats["bus"] = self._dgent.bus.stats

        return stats


# === Factory Function ===


def create_data_resolver(dgent: Any = None) -> DataNode:
    """
    Create a DataNode with optional D-gent backend.

    Args:
        dgent: D-gent backend (DgentProtocol implementation)
               If None, creates unconfigured node.

    Returns:
        Configured DataNode

    Example:
        from agents.d.backends.memory import MemoryBackend
        dgent = MemoryBackend()
        data_node = create_data_resolver(dgent)
    """
    node = DataNode()
    node._dgent = dgent
    return node
