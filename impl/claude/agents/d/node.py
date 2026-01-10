"""
D-gent AGENTESE Node: @node("self.data")

Wraps Universe and DgentRouter as AGENTESE nodes for universal gateway access.

AGENTESE Paths:
- self.data.manifest       - Data layer health status
- self.data.store          - Store typed object
- self.data.query          - Query for data
- self.data.get            - Get data by ID
- self.data.delete         - Delete data by ID
- self.data.stats          - Universe statistics
- self.data.schema.register - Register schema
- self.data.datum.put      - Store raw Datum
- self.data.datum.get      - Get raw Datum
- self.data.datum.list     - List data
- self.data.datum.chain    - Get causal chain

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: docs/skills/metaphysical-fullstack.md
See: spec/agents/d-gent.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.affordances import AspectCategory, Effect, aspect
from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .datum import Datum
from .router import DgentRouter
from .universe.universe import Query, Universe, UniverseStats

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === D-gent Response Contracts ===


@dataclass(frozen=True)
class DataManifestResponse:
    """Response for self.data.manifest."""

    backend: str
    total_data: int
    schemas_registered: int
    namespace: str
    available_backends: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "total_data": self.total_data,
            "schemas_registered": self.schemas_registered,
            "namespace": self.namespace,
            "available_backends": self.available_backends,
        }


@dataclass(frozen=True)
class StoreRequest:
    """Request for self.data.store."""

    obj: Any  # The object to store
    schema_name: str | None = None


@dataclass(frozen=True)
class StoreResponse:
    """Response for self.data.store."""

    datum_id: str
    schema: str | None

    def to_dict(self) -> dict[str, Any]:
        return {"datum_id": self.datum_id, "schema": self.schema}


@dataclass(frozen=True)
class QueryRequest:
    """Request for self.data.query."""

    prefix: str | None = None
    after: float | None = None
    limit: int = 100
    schema: str | None = None


@dataclass(frozen=True)
class QueryResponse:
    """Response for self.data.query."""

    results: list[Any]
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {"results": self.results, "count": self.count}


@dataclass(frozen=True)
class GetRequest:
    """Request for self.data.get."""

    id: str


@dataclass(frozen=True)
class GetResponse:
    """Response for self.data.get."""

    data: Any | None

    def to_dict(self) -> dict[str, Any]:
        return {"data": self.data}


@dataclass(frozen=True)
class DeleteRequest:
    """Request for self.data.delete."""

    id: str


@dataclass(frozen=True)
class DeleteResponse:
    """Response for self.data.delete."""

    deleted: bool

    def to_dict(self) -> dict[str, Any]:
        return {"deleted": self.deleted}


@dataclass(frozen=True)
class StatsResponse:
    """Response for self.data.stats."""

    backend: str
    total_data: int
    schemas_registered: int
    namespace: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "total_data": self.total_data,
            "schemas_registered": self.schemas_registered,
            "namespace": self.namespace,
        }


@dataclass(frozen=True)
class RegisterSchemaRequest:
    """Request for self.data.schema.register."""

    name: str
    type_cls: type


@dataclass(frozen=True)
class RegisterSchemaResponse:
    """Response for self.data.schema.register."""

    registered: bool
    schema_name: str

    def to_dict(self) -> dict[str, Any]:
        return {"registered": self.registered, "schema_name": self.schema_name}


@dataclass(frozen=True)
class DatumPutRequest:
    """Request for self.data.datum.put."""

    datum: Datum


@dataclass(frozen=True)
class DatumPutResponse:
    """Response for self.data.datum.put."""

    datum_id: str

    def to_dict(self) -> dict[str, Any]:
        return {"datum_id": self.datum_id}


@dataclass(frozen=True)
class DatumGetRequest:
    """Request for self.data.datum.get."""

    id: str


@dataclass(frozen=True)
class DatumGetResponse:
    """Response for self.data.datum.get."""

    datum: Datum | None

    def to_dict(self) -> dict[str, Any]:
        return {"datum": self.datum.to_json() if self.datum else None}


@dataclass(frozen=True)
class DatumListRequest:
    """Request for self.data.datum.list."""

    prefix: str | None = None
    after: float | None = None
    limit: int = 100


@dataclass(frozen=True)
class DatumListResponse:
    """Response for self.data.datum.list."""

    data: list[Datum]
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "data": [d.to_json() for d in self.data],
            "count": self.count,
        }


@dataclass(frozen=True)
class CausalChainRequest:
    """Request for self.data.datum.chain."""

    id: str


@dataclass(frozen=True)
class CausalChainResponse:
    """Response for self.data.datum.chain."""

    chain: list[Datum]
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "chain": [d.to_json() for d in self.chain],
            "count": self.count,
        }


# === D-gent Rendering ===


@dataclass(frozen=True)
class DataManifestRendering:
    """Rendering for D-gent manifest."""

    stats: UniverseStats
    available_backends: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "data_manifest",
            "backend": self.stats.backend,
            "total_data": self.stats.total_data,
            "schemas_registered": self.stats.schemas_registered,
            "namespace": self.stats.namespace,
            "available_backends": self.available_backends,
        }

    def to_text(self) -> str:
        lines = [
            "D-gent Data Layer",
            "=================",
            f"Backend: {self.stats.backend}",
            f"Namespace: {self.stats.namespace}",
            f"Total Data: {self.stats.total_data}",
            f"Schemas: {self.stats.schemas_registered}",
            "",
            "Available Backends:",
        ]
        for backend_info in self.available_backends:
            status_icon = "✓" if backend_info["available"] else "✗"
            lines.append(
                f"  {status_icon} {backend_info['backend']:10} - {backend_info.get('reason', 'OK')}"
            )
        return "\n".join(lines)


# === Data Affordances ===

DATA_AFFORDANCES: tuple[str, ...] = (
    "store",  # Store typed object
    "query",  # Query for data
    "get",  # Get by ID
    "delete",  # Delete by ID
    "stats",  # Get statistics
)

# Developer/operator affordances (full access)
DATA_ADMIN_AFFORDANCES: tuple[str, ...] = DATA_AFFORDANCES + (
    "schema.register",  # Register schema
    "datum.put",  # Store raw Datum
    "datum.get",  # Get raw Datum
    "datum.list",  # List data
    "datum.chain",  # Get causal chain
)


# === DataNode ===


@node(
    "self.data",
    description="D-gent persistence layer - universal data storage",
    dependencies=("universe",),
    contracts={
        # Perception aspects (Response only - no request needed)
        "manifest": Response(DataManifestResponse),
        "stats": Response(StatsResponse),
        # Mutation aspects (Contract with request + response)
        "store": Contract(StoreRequest, StoreResponse),
        "query": Contract(QueryRequest, QueryResponse),
        "get": Contract(GetRequest, GetResponse),
        "delete": Contract(DeleteRequest, DeleteResponse),
        "schema.register": Contract(RegisterSchemaRequest, RegisterSchemaResponse),
        "datum.put": Contract(DatumPutRequest, DatumPutResponse),
        "datum.get": Contract(DatumGetRequest, DatumGetResponse),
        "datum.list": Contract(DatumListRequest, DatumListResponse),
        "datum.chain": Contract(CausalChainRequest, CausalChainResponse),
    },
    examples=[
        ("stats", {}, "Show D-gent statistics"),
        ("query", {"limit": 10}, "List recent data"),
    ],
)
class DataNode(BaseLogosNode):
    """
    AGENTESE node for D-gent persistence layer.

    Exposes Universe (typed data) and DgentRouter (raw Datum) through
    the universal protocol. All transports (HTTP, WebSocket, CLI) collapse
    to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/self/data/store
        {"obj": {...}, "schema_name": "crystal"}

        # Via Logos directly
        await logos.invoke("self.data.store", observer, obj=crystal)

        # Via CLI
        kgents data store crystal.json

    Teaching:
        gotcha: DataNode REQUIRES universe dependency. Without it,
                instantiation fails with TypeError—this is intentional!
                It enables Logos fallback when DI isn't configured.

        gotcha: Raw Datum operations (datum.*) require developer/operator
                archetype. Regular users only see typed store/query/get.
                (Evidence: affordances vary by archetype)

        gotcha: Every DataNode invocation emits a Mark (WARP Law 3). Don't add
                manual tracing—the gateway handles it at _invoke_path().
    """

    def __init__(self, universe: Universe) -> None:
        """
        Initialize DataNode.

        Universe is REQUIRED. When Logos tries to instantiate
        without dependencies, it will fail and fall back to a
        minimal context resolver.

        Args:
            universe: The Universe instance (injected by container)

        Raises:
            TypeError: If universe is not provided (intentional for fallback)
        """
        self._universe = universe

    @property
    def handle(self) -> str:
        return "self.data"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Observer gradation:
        - developer/operator: Full access including raw Datum operations
        - architect/researcher: Typed operations only
        - guest: Read-only (query, get, stats)
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators, admins
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return DATA_ADMIN_AFFORDANCES

        # Architects/researchers: typed operations only
        if archetype_lower in ("architect", "researcher", "technical"):
            return DATA_AFFORDANCES

        # Guest (default): read-only
        return ("query", "get", "stats")

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("universe")],
        help="Display D-gent data layer status",
        examples=["kg data", "kg data manifest"],
    )
    async def manifest(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Manifest D-gent status to observer.

        AGENTESE: self.data.manifest
        """
        if self._universe is None:
            return BasicRendering(
                summary="D-gent not initialized",
                content="No Universe configured",
                metadata={"error": "no_universe"},
            )

        # Get Universe stats
        stats = await self._universe.stats()

        # Get available backends from DgentRouter
        router = DgentRouter()
        backend_statuses = await router.status()
        available_backends = [
            {
                "backend": status.backend.name.lower(),
                "available": status.available,
                "reason": status.reason or "OK",
            }
            for status in backend_statuses
        ]

        return DataManifestRendering(stats=stats, available_backends=available_backends)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to Universe/DgentRouter methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if self._universe is None:
            return {"error": "Universe not configured"}

        # Route to appropriate method
        if aspect == "store":
            obj = kwargs.get("obj")
            schema_name = kwargs.get("schema_name")
            if obj is None:
                return {"error": "obj required"}

            datum_id = await self._universe.store(obj, schema_name)
            return {"datum_id": datum_id, "schema": schema_name}

        elif aspect == "query":
            prefix = kwargs.get("prefix")
            after = kwargs.get("after")
            limit = kwargs.get("limit", 100)
            schema = kwargs.get("schema")

            q = Query(prefix=prefix, after=after, limit=limit, schema=schema)
            results = await self._universe.query(q)
            return {"results": results, "count": len(results)}

        elif aspect == "get":
            datum_id_raw = kwargs.get("id")
            if not datum_id_raw:
                return {"error": "id required"}
            datum_id = str(datum_id_raw)

            data = await self._universe.get(datum_id)
            return {"data": data}

        elif aspect == "delete":
            datum_id_raw = kwargs.get("id")
            if not datum_id_raw:
                return {"error": "id required"}
            datum_id = str(datum_id_raw)

            deleted = await self._universe.delete(datum_id)
            return {"deleted": deleted}

        elif aspect == "stats":
            stats = await self._universe.stats()
            return {
                "backend": stats.backend,
                "total_data": stats.total_data,
                "schemas_registered": stats.schemas_registered,
                "namespace": stats.namespace,
            }

        elif aspect == "schema.register":
            name = kwargs.get("name")
            type_cls = kwargs.get("type_cls")
            if not name or not type_cls:
                return {"error": "name and type_cls required"}

            self._universe.register_type(name, type_cls)
            return {"registered": True, "schema_name": name}

        # Datum operations (raw DgentRouter)
        elif aspect == "datum.put":
            datum = kwargs.get("datum")
            if datum is None:
                return {"error": "datum required"}

            datum_id = await self._universe.store_datum(datum)
            return {"datum_id": datum_id}

        elif aspect == "datum.get":
            datum_id_raw = kwargs.get("id")
            if not datum_id_raw:
                return {"error": "id required"}
            datum_id = str(datum_id_raw)

            # Get raw datum (bypass schema deserialization)
            router = DgentRouter()
            datum = await router.get(datum_id)
            return {"datum": datum}

        elif aspect == "datum.list":
            prefix = kwargs.get("prefix")
            after = kwargs.get("after")
            limit = kwargs.get("limit", 100)

            router = DgentRouter()
            data = await router.list(prefix=prefix, after=after, limit=limit)
            return {"data": data, "count": len(data)}

        elif aspect == "datum.chain":
            datum_id_raw = kwargs.get("id")
            if not datum_id_raw:
                return {"error": "id required"}
            datum_id = str(datum_id_raw)

            router = DgentRouter()
            chain = await router.causal_chain(datum_id)
            return {"chain": chain, "count": len(chain)}

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# === Exports ===

__all__ = [
    "DataNode",
    "DataManifestRendering",
    "DataManifestResponse",
    "StoreRequest",
    "StoreResponse",
    "QueryRequest",
    "QueryResponse",
    "GetRequest",
    "GetResponse",
    "DeleteRequest",
    "DeleteResponse",
    "StatsResponse",
    "RegisterSchemaRequest",
    "RegisterSchemaResponse",
    "DatumPutRequest",
    "DatumPutResponse",
    "DatumGetRequest",
    "DatumGetResponse",
    "DatumListRequest",
    "DatumListResponse",
    "CausalChainRequest",
    "CausalChainResponse",
]
