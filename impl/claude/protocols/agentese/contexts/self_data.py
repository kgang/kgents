"""
AGENTESE Self Data Context

Data persistence nodes for self.data.* paths:
- DataNode: The agent's data persistence layer (D-gent)
- UpgraderNode: Tier promotion visibility (Phase 5)

Part of the Data Architecture Rewrite (plans/data-architecture-rewrite.md).
Provides AGENTESE access to the new simplified D-gent API.

Five core operations: put, get, delete, list, causal_chain
Plus: exists, count, backend (diagnostics)
Plus: upgrader (tier promotion observability)
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
    "put",  # Store datum
    "get",  # Retrieve datum by ID
    "delete",  # Remove datum
    "list",  # List data with filters
    "causal_chain",  # Get causal ancestors
    # Additional methods
    "exists",  # Check if datum exists
    "count",  # Count total data
    # Diagnostics
    "backend",  # Show current backend info
    "stats",  # Storage statistics
    # Sub-nodes
    "upgrader",  # Tier promotion observability
    "table",  # Alembic table access (Dual-Track Architecture)
)

# Table-specific affordances (Dual-Track Architecture)
TABLE_AFFORDANCES: tuple[str, ...] = (
    "get",  # Get by ID from table
    "put",  # Upsert to table
    "delete",  # Delete from table
    "list",  # List with filters
    "count",  # Count records
    "query",  # Direct SQL (advanced)
    "models",  # List available models
)

# Upgrader-specific affordances
UPGRADER_AFFORDANCES: tuple[str, ...] = (
    "status",  # Quick health check
    "history",  # Recent tier transitions
    "pending",  # Data approaching promotion threshold
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
    - upgrader: Tier promotion observability (sub-node)

    AGENTESE: self.data.*

    Architecture (Projection Lattice):
        Memory (Tier 0) → JSONL (Tier 1) → SQLite (Tier 2) → Postgres (Tier 3)

    Selection: DgentRouter automatically selects the best available backend.
    """

    _handle: str = "self.data"

    # D-gent backend (injected via create_data_resolver)
    _dgent: Any = None

    # AutoUpgrader for tier promotion (injected via create_data_resolver)
    _upgrader: Any = None

    # Upgrader sub-node (created lazily)
    _upgrader_node: "UpgraderNode | None" = None

    # Table sub-node for Dual-Track Architecture (created lazily)
    _table_node: "TableNode | None" = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Data affordances available to all archetypes."""
        return DATA_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
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
            case "upgrader":
                # Return the upgrader sub-node
                return self._upgrader_node
            case "table":
                # Return the table sub-node (Dual-Track Architecture)
                return self._table_node
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


# === Upgrader Node ===


@dataclass
class UpgraderNode(BaseLogosNode):
    """
    self.data.upgrader - Tier promotion observability.

    Makes data tier transitions visible:
    - status: Current upgrader health
    - history: Recent tier promotions
    - pending: Data approaching promotion threshold

    AGENTESE: self.data.upgrader.*

    Phase 5 of D-gent Integration: Upgrader Observability.
    """

    _handle: str = "self.data.upgrader"

    # AutoUpgrader instance (injected)
    _upgrader: Any = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Upgrader affordances available to all archetypes."""
        return UPGRADER_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View current upgrader state."""
        if self._upgrader is None:
            return BasicRendering(
                summary="Data Upgrader (Not Configured)",
                content="AutoUpgrader not configured. Wire via create_data_resolver().",
                metadata={"configured": False},
            )

        stats = self._upgrader.stats

        return BasicRendering(
            summary="Data Tier Upgrader",
            content=(
                f"Running: {self._upgrader._running}\n"
                f"Memory → JSONL: {stats.upgrades_memory_to_jsonl}\n"
                f"JSONL → SQLite: {stats.upgrades_jsonl_to_sqlite}\n"
                f"SQLite → Postgres: {stats.upgrades_sqlite_to_postgres}\n"
                f"Failures: {stats.upgrade_failures}"
            ),
            metadata={
                "configured": True,
                "running": self._upgrader._running,
                "memory_to_jsonl": stats.upgrades_memory_to_jsonl,
                "jsonl_to_sqlite": stats.upgrades_jsonl_to_sqlite,
                "sqlite_to_postgres": stats.upgrades_sqlite_to_postgres,
                "failures": stats.upgrade_failures,
                "last_upgrade": stats.last_upgrade_time,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle upgrader-specific aspects."""
        match aspect:
            case "status":
                return await self._status(observer, **kwargs)
            case "history":
                return await self._history(observer, **kwargs)
            case "pending":
                return await self._pending(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _status(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Quick health check of upgrader.

        AGENTESE: self.data.upgrader.status

        Returns:
            Dict with running status and recent activity
        """
        if self._upgrader is None:
            return {"error": "AutoUpgrader not configured"}

        stats = self._upgrader.stats

        return {
            "status": "running" if self._upgrader._running else "stopped",
            "total_upgrades": (
                stats.upgrades_memory_to_jsonl
                + stats.upgrades_jsonl_to_sqlite
                + stats.upgrades_sqlite_to_postgres
            ),
            "failures": stats.upgrade_failures,
            "tracked_data": len(self._upgrader._datum_stats),
            "last_upgrade": stats.last_upgrade_time,
        }

    async def _history(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get recent tier transitions.

        AGENTESE: self.data.upgrader.history

        Returns:
            Dict with upgrade statistics by tier transition
        """
        if self._upgrader is None:
            return {"error": "AutoUpgrader not configured"}

        stats = self._upgrader.stats

        return {
            "transitions": {
                "MEMORY_to_JSONL": stats.upgrades_memory_to_jsonl,
                "JSONL_to_SQLITE": stats.upgrades_jsonl_to_sqlite,
                "SQLITE_to_POSTGRES": stats.upgrades_sqlite_to_postgres,
            },
            "total": (
                stats.upgrades_memory_to_jsonl
                + stats.upgrades_jsonl_to_sqlite
                + stats.upgrades_sqlite_to_postgres
            ),
            "failures": stats.upgrade_failures,
            "last_upgrade_time": stats.last_upgrade_time,
        }

    async def _pending(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get data approaching promotion threshold.

        AGENTESE: self.data.upgrader.pending

        Args:
            limit: Max items to return (default 10)

        Returns:
            Dict with data items close to promotion
        """
        if self._upgrader is None:
            return {"error": "AutoUpgrader not configured"}

        limit = kwargs.get("limit", 10)
        policy = self._upgrader.policy

        # Find data approaching thresholds
        pending = []
        for datum_id, stats in list(self._upgrader._datum_stats.items())[:limit]:
            # Calculate progress toward next tier
            progress = 0.0
            next_tier = None

            if stats.tier.name == "MEMORY":
                progress = stats.access_count / policy.memory_to_jsonl_accesses
                next_tier = "JSONL"
            elif stats.tier.name == "JSONL":
                progress = stats.access_count / policy.jsonl_to_sqlite_accesses
                next_tier = "SQLITE"

            if progress > 0.5:  # Only show items > 50% toward threshold
                pending.append(
                    {
                        "id": datum_id[:16] + "...",
                        "current_tier": stats.tier.name,
                        "next_tier": next_tier,
                        "progress": round(progress, 2),
                        "access_count": stats.access_count,
                    }
                )

        # Sort by progress (closest to promotion first)
        pending.sort(key=lambda x: x["progress"], reverse=True)

        return {
            "pending": pending[:limit],
            "total_tracked": len(self._upgrader._datum_stats),
        }


# === Table Node (Dual-Track Architecture) ===


@dataclass
class TableNode(BaseLogosNode):
    """
    self.data.table - Alembic table access for application state.

    Part of the Dual-Track Architecture:
    - D-gent Track: Agent memory (schema-free)
    - Alembic Track: Application state (typed, migrated)
    - TableAdapter: Bridge via DgentProtocol

    Enables agent access to typed, migrated tables through AGENTESE:
    - get: Retrieve by ID
    - put: Upsert record
    - delete: Remove record
    - list: Query with filters
    - count: Count records
    - models: List available models

    AGENTESE: self.data.table.*
              self.data.table.crystal.get[id="..."]
              self.data.table.citizen.list[limit=10]
    """

    _handle: str = "self.data.table"

    # Registry of TableAdapter instances by model name
    _adapters: dict[str, Any] = field(default_factory=dict)

    # Session factory for creating adapters on-demand
    _session_factory: Any = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Table affordances available to all archetypes."""
        return TABLE_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View available tables and their status."""
        if not self._adapters and self._session_factory is None:
            return BasicRendering(
                summary="Table Storage (Not Configured)",
                content="No tables configured. Wire via create_data_resolver().",
                metadata={"configured": False},
            )

        tables = list(self._adapters.keys())

        return BasicRendering(
            summary="Alembic Table Storage",
            content=f"Available tables: {', '.join(tables) if tables else 'None loaded'}",
            metadata={
                "configured": True,
                "tables": tables,
                "count": len(tables),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle table-specific aspects."""
        match aspect:
            case "models":
                return await self._models(observer, **kwargs)
            case "get":
                return await self._get(observer, **kwargs)
            case "put":
                return await self._put(observer, **kwargs)
            case "delete":
                return await self._delete(observer, **kwargs)
            case "list":
                return await self._list(observer, **kwargs)
            case "count":
                return await self._count(observer, **kwargs)
            case _:
                # Check if it's a model name (e.g., self.data.table.crystal)
                if aspect in self._adapters:
                    return TableModelNode(
                        _handle=f"self.data.table.{aspect}",
                        _adapter=self._adapters[aspect],
                    )
                return {
                    "aspect": aspect,
                    "status": "not implemented or model not found",
                }

    async def _models(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        List available table models.

        AGENTESE: self.data.table.models

        Returns:
            Dict with available model names and their table info
        """
        models = []
        for name, adapter in self._adapters.items():
            models.append(
                {
                    "name": name,
                    "table": adapter.table_name,
                    "id_field": adapter.id_field,
                }
            )

        return {
            "status": "ok",
            "models": models,
            "count": len(models),
        }

    async def _get(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get record by ID from specified table.

        AGENTESE: self.data.table.get[model="crystal", id="..."]

        Args:
            model: Model name (required)
            id: Record ID (required)
        """
        model = kwargs.get("model")
        record_id = kwargs.get("id")

        if not model or not record_id:
            return {
                "error": "model and id are required",
                "usage": "self.data.table.get[model='crystal', id='xxx']",
            }

        if model not in self._adapters:
            return {
                "error": f"Unknown model: {model}",
                "available": list(self._adapters.keys()),
            }

        adapter = self._adapters[model]
        datum = await adapter.get(record_id)

        if datum is None:
            return {"status": "not_found", "model": model, "id": record_id}

        import json

        return {
            "status": "found",
            "model": model,
            "id": datum.id,
            "content": json.loads(datum.content.decode("utf-8")),
            "created_at": datum.created_at,
        }

    async def _put(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Upsert record to specified table.

        AGENTESE: self.data.table.put[model="crystal", id="...", data={...}]
        """
        model = kwargs.get("model")
        record_id = kwargs.get("id")
        data = kwargs.get("data", {})

        if not model or not record_id:
            return {
                "error": "model and id are required",
                "usage": "self.data.table.put[model='crystal', id='xxx', data={...}]",
            }

        if model not in self._adapters:
            return {
                "error": f"Unknown model: {model}",
                "available": list(self._adapters.keys()),
            }

        import json

        from agents.d.datum import Datum

        datum = Datum.create(
            content=json.dumps(data).encode("utf-8"),
            id=record_id,
        )

        adapter = self._adapters[model]
        result_id = await adapter.put(datum)

        return {
            "status": "stored",
            "model": model,
            "id": result_id,
        }

    async def _delete(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Delete record from specified table.

        AGENTESE: self.data.table.delete[model="crystal", id="..."]
        """
        model = kwargs.get("model")
        record_id = kwargs.get("id")

        if not model or not record_id:
            return {
                "error": "model and id are required",
                "usage": "self.data.table.delete[model='crystal', id='xxx']",
            }

        if model not in self._adapters:
            return {
                "error": f"Unknown model: {model}",
                "available": list(self._adapters.keys()),
            }

        adapter = self._adapters[model]
        success = await adapter.delete(record_id)

        return {
            "status": "deleted" if success else "not_found",
            "model": model,
            "id": record_id,
        }

    async def _list(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        List records from specified table.

        AGENTESE: self.data.table.list[model="crystal", limit=10]
        """
        model = kwargs.get("model")

        if not model:
            return {
                "error": "model is required",
                "usage": "self.data.table.list[model='crystal', limit=10]",
            }

        if model not in self._adapters:
            return {
                "error": f"Unknown model: {model}",
                "available": list(self._adapters.keys()),
            }

        adapter = self._adapters[model]
        prefix = kwargs.get("prefix")
        limit = kwargs.get("limit", 100)

        data = await adapter.list(prefix=prefix, limit=limit)

        import json

        return {
            "status": "ok",
            "model": model,
            "count": len(data),
            "records": [
                {
                    "id": d.id,
                    "preview": json.loads(d.content.decode("utf-8")),
                }
                for d in data[:10]  # Preview first 10
            ],
        }

    async def _count(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Count records in specified table.

        AGENTESE: self.data.table.count[model="crystal"]
        """
        model = kwargs.get("model")

        if not model:
            return {
                "error": "model is required",
                "usage": "self.data.table.count[model='crystal']",
            }

        if model not in self._adapters:
            return {
                "error": f"Unknown model: {model}",
                "available": list(self._adapters.keys()),
            }

        adapter = self._adapters[model]
        count = await adapter.count()

        return {
            "status": "ok",
            "model": model,
            "count": count,
        }


@dataclass
class TableModelNode(BaseLogosNode):
    """
    self.data.table.<model> - Direct access to a specific table model.

    Enables ergonomic access like:
        self.data.table.crystal.get[id="xxx"]
        self.data.table.citizen.list[limit=10]

    Instead of:
        self.data.table.get[model="crystal", id="xxx"]
    """

    _handle: str = "self.data.table.model"
    _adapter: Any = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("get", "put", "delete", "list", "count", "causal_chain")

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View model table info."""
        if self._adapter is None:
            return BasicRendering(
                summary="Table Model (Not Configured)",
                content="Adapter not configured.",
                metadata={"configured": False},
            )

        count = await self._adapter.count()

        return BasicRendering(
            summary=f"Table: {self._adapter.table_name}",
            content=f"Records: {count}",
            metadata={
                "table": self._adapter.table_name,
                "count": count,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle model-specific aspects."""
        if self._adapter is None:
            return {"error": "Adapter not configured"}

        match aspect:
            case "get":
                record_id = kwargs.get("id")
                if not record_id:
                    return {"error": "id is required"}
                datum = await self._adapter.get(record_id)
                if datum is None:
                    return {"status": "not_found", "id": record_id}
                import json

                return {
                    "status": "found",
                    "id": datum.id,
                    "content": json.loads(datum.content.decode("utf-8")),
                }
            case "list":
                limit = kwargs.get("limit", 100)
                prefix = kwargs.get("prefix")
                data = await self._adapter.list(prefix=prefix, limit=limit)
                import json

                return {
                    "count": len(data),
                    "records": [
                        {"id": d.id, "preview": json.loads(d.content.decode("utf-8"))}
                        for d in data[:10]
                    ],
                }
            case "count":
                count = await self._adapter.count()
                return {"count": count}
            case "delete":
                record_id = kwargs.get("id")
                if not record_id:
                    return {"error": "id is required"}
                success = await self._adapter.delete(record_id)
                return {
                    "status": "deleted" if success else "not_found",
                    "id": record_id,
                }
            case "causal_chain":
                record_id = kwargs.get("id")
                if not record_id:
                    return {"error": "id is required"}
                chain = await self._adapter.causal_chain(record_id)
                import json

                return {
                    "chain_length": len(chain),
                    "chain": [
                        {"id": d.id, "preview": json.loads(d.content.decode("utf-8"))}
                        for d in chain
                    ],
                }
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# === Factory Function ===


def create_data_resolver(
    dgent: Any = None,
    upgrader: Any = None,
    table_adapters: dict[str, Any] | None = None,
) -> DataNode:
    """
    Create a DataNode with optional D-gent backend, upgrader, and table adapters.

    Args:
        dgent: D-gent backend (DgentProtocol implementation)
               If None, creates unconfigured node.
        upgrader: AutoUpgrader for tier promotion observability
                  If None, upgrader sub-node returns unconfigured state.
        table_adapters: Dict mapping model name to TableAdapter instance
                        Enables self.data.table.* paths for Dual-Track Architecture.

    Returns:
        Configured DataNode with optional upgrader and table sub-nodes

    Example:
        from agents.d.backends.memory import MemoryBackend
        from agents.d.upgrader import AutoUpgrader
        from agents.d.adapters import TableAdapter
        from models import Crystal, Citizen
        from models.base import get_session_factory

        dgent = MemoryBackend()
        upgrader = AutoUpgrader(source=dgent, ...)

        # Create table adapters for Crown Jewels
        session_factory = get_session_factory()
        table_adapters = {
            "crystal": TableAdapter(Crystal, session_factory),
            "citizen": TableAdapter(Citizen, session_factory),
        }

        data_node = create_data_resolver(dgent, upgrader, table_adapters)

        # Now use AGENTESE:
        # self.data.table.crystal.get[id="xxx"]
        # self.data.table.citizen.list[limit=10]
    """
    node = DataNode()
    node._dgent = dgent
    node._upgrader = upgrader

    # Create upgrader sub-node
    upgrader_node = UpgraderNode()
    upgrader_node._upgrader = upgrader
    node._upgrader_node = upgrader_node

    # Create table sub-node (Dual-Track Architecture)
    table_node = TableNode()
    if table_adapters:
        table_node._adapters = table_adapters
    node._table_node = table_node

    return node
