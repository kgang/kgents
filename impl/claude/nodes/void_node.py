"""
AGENTESE Node for void.* - Axioms and Values (L1-L2)

The void namespace represents the irreducible ground - axioms and values
that form the constitutional foundation. These are the bedrock upon which
all other derivations rest.

L1 (Axiom): Self-evident truths, no proof needed
L2 (Value): Principles derived from axioms, still foundational

AGENTESE Paths:
- void.axiom.list - List all axioms
- void.axiom.get - Get axiom by ID
- void.axiom.create - Create new axiom
- void.value.list - List all values
- void.value.get - Get value by ID
- void.value.create - Create value (links to axioms)
- void.manifest - Show void layer status

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: spec/protocols/zero-seed.md
See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from agents.d.schemas.axiom import AxiomCrystal, ValueCrystal
from agents.d.universe.universe import Query, Universe, UniverseStats
from protocols.agentese.affordances import AspectCategory, Effect, aspect
from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import BaseLogosNode, BasicRendering, Observer, Renderable
from protocols.agentese.registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Void Response Contracts ===


@dataclass(frozen=True)
class VoidManifestResponse:
    """Response for void.manifest."""

    total_axioms: int
    total_values: int
    domains: list[str]
    backend: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_axioms": self.total_axioms,
            "total_values": self.total_values,
            "domains": self.domains,
            "backend": self.backend,
        }


@dataclass(frozen=True)
class AxiomListRequest:
    """Request for void.axiom.list."""

    domain: str | None = None
    tags: list[str] | None = None
    limit: int = 100


@dataclass(frozen=True)
class AxiomListResponse:
    """Response for void.axiom.list."""

    axioms: list[AxiomCrystal]
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "axioms": [a.to_dict() for a in self.axioms],
            "count": self.count,
        }


@dataclass(frozen=True)
class AxiomGetRequest:
    """Request for void.axiom.get."""

    id: str


@dataclass(frozen=True)
class AxiomGetResponse:
    """Response for void.axiom.get."""

    axiom: AxiomCrystal | None

    def to_dict(self) -> dict[str, Any]:
        return {"axiom": self.axiom.to_dict() if self.axiom else None}


@dataclass(frozen=True)
class AxiomCreateRequest:
    """Request for void.axiom.create."""

    content: str
    domain: str
    tags: list[str] | None = None


@dataclass(frozen=True)
class AxiomCreateResponse:
    """Response for void.axiom.create."""

    axiom_id: str
    axiom: AxiomCrystal

    def to_dict(self) -> dict[str, Any]:
        return {
            "axiom_id": self.axiom_id,
            "axiom": self.axiom.to_dict(),
        }


@dataclass(frozen=True)
class ValueListRequest:
    """Request for void.value.list."""

    axiom_id: str | None = None
    tags: list[str] | None = None
    limit: int = 100


@dataclass(frozen=True)
class ValueListResponse:
    """Response for void.value.list."""

    values: list[ValueCrystal]
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "values": [v.to_dict() for v in self.values],
            "count": self.count,
        }


@dataclass(frozen=True)
class ValueGetRequest:
    """Request for void.value.get."""

    id: str


@dataclass(frozen=True)
class ValueGetResponse:
    """Response for void.value.get."""

    value: ValueCrystal | None

    def to_dict(self) -> dict[str, Any]:
        return {"value": self.value.to_dict() if self.value else None}


@dataclass(frozen=True)
class ValueCreateRequest:
    """Request for void.value.create."""

    principle: str
    axiom_ids: list[str]
    tags: list[str] | None = None


@dataclass(frozen=True)
class ValueCreateResponse:
    """Response for void.value.create."""

    value_id: str
    value: ValueCrystal

    def to_dict(self) -> dict[str, Any]:
        return {
            "value_id": self.value_id,
            "value": self.value.to_dict(),
        }


# === Void Rendering ===


@dataclass(frozen=True)
class VoidManifestRendering:
    """Rendering for void.manifest."""

    total_axioms: int
    total_values: int
    domains: list[str]
    backend: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "void_manifest",
            "total_axioms": self.total_axioms,
            "total_values": self.total_values,
            "domains": self.domains,
            "backend": self.backend,
        }

    def to_text(self) -> str:
        lines = [
            "Void Layer - Axiomatic Ground",
            "=============================",
            f"Backend: {self.backend}",
            f"Total Axioms: {self.total_axioms}",
            f"Total Values: {self.total_values}",
            "",
            "Domains:",
        ]
        for domain in self.domains:
            lines.append(f"  - {domain}")
        return "\n".join(lines)


# === Void Affordances ===

VOID_AFFORDANCES: tuple[str, ...] = (
    "axiom.list",  # List axioms
    "axiom.get",  # Get axiom by ID
    "value.list",  # List values
    "value.get",  # Get value by ID
)

# Developer/operator affordances (creation)
VOID_ADMIN_AFFORDANCES: tuple[str, ...] = VOID_AFFORDANCES + (
    "axiom.create",  # Create axiom
    "value.create",  # Create value
)


# === VoidNode ===


@node(
    "void",
    description="Axioms and values - the irreducible ground (L1-L2)",
    dependencies=("universe",),
    contracts={
        # Perception aspects
        "manifest": Response(VoidManifestResponse),
        "axiom.list": Contract(AxiomListRequest, AxiomListResponse),
        "axiom.get": Contract(AxiomGetRequest, AxiomGetResponse),
        "value.list": Contract(ValueListRequest, ValueListResponse),
        "value.get": Contract(ValueGetRequest, ValueGetResponse),
        # Mutation aspects
        "axiom.create": Contract(AxiomCreateRequest, AxiomCreateResponse),
        "value.create": Contract(ValueCreateRequest, ValueCreateResponse),
    },
    examples=[
        ("manifest", {}, "Show void layer status"),
        ("axiom.list", {"domain": "constitution", "limit": 10}, "List constitutional axioms"),
    ],
)
class VoidNode(BaseLogosNode):
    """
    AGENTESE node for axioms and values (L1-L2).

    The void namespace represents the foundational layer - axioms that
    require no proof (self-evident) and values derived directly from axioms.

    Observer gradation:
    - developer/operator: Full access including creation
    - philosopher/architect: Read-only access
    - guest: Read-only access to public axioms

    Example:
        # Via AGENTESE gateway
        POST /agentese/void/axiom/list
        {"domain": "constitution", "limit": 10}

        # Via Logos directly
        await logos.invoke("void.axiom.list", observer, domain="constitution")

        # Via CLI
        kgents void axiom list --domain constitution

    Teaching:
        gotcha: VoidNode REQUIRES universe dependency. Without it,
                instantiation fails with TypeError—this is intentional!
                It enables Logos fallback when DI isn't configured.

        gotcha: Axiom creation requires developer/operator archetype.
                Regular users only see read operations.
                (Evidence: affordances vary by archetype)

        gotcha: Every VoidNode invocation emits a Mark (WARP Law 3). Don't add
                manual tracing—the gateway handles it at _invoke_path().
    """

    def __init__(self, universe: Universe) -> None:
        """
        Initialize VoidNode.

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
        return "void"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Observer gradation:
        - developer/operator: Full access including creation
        - philosopher/architect: Read-only
        - guest: Read-only
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators, admins
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return VOID_ADMIN_AFFORDANCES

        # Philosophers/architects: read-only
        if archetype_lower in ("philosopher", "architect", "researcher", "technical"):
            return VOID_AFFORDANCES

        # Guest (default): read-only
        return VOID_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("universe")],
        help="Display void layer status (axioms and values)",
        examples=["kg void", "kg void manifest"],
    )
    async def manifest(
        self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any
    ) -> Renderable:
        """
        Manifest void layer status to observer.

        AGENTESE: void.manifest
        """
        if self._universe is None:
            return BasicRendering(
                summary="Void layer not initialized",
                content="No Universe configured",
                metadata={"error": "no_universe"},
            )

        # Query for axioms and values
        axiom_query = Query(schema="concept.axiom", limit=1000)
        value_query = Query(schema="concept.value", limit=1000)

        axioms = await self._universe.query(axiom_query)
        values = await self._universe.query(value_query)

        # Extract unique domains from axioms
        domains = sorted(set(a.domain for a in axioms if isinstance(a, AxiomCrystal)))

        stats = await self._universe.stats()

        return VoidManifestRendering(
            total_axioms=len(axioms),
            total_values=len(values),
            domains=domains,
            backend=stats.backend,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to Universe methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if self._universe is None:
            return {"error": "Universe not configured"}

        # Route to appropriate method
        if aspect == "axiom.list":
            domain = kwargs.get("domain")
            tags = kwargs.get("tags")
            limit = kwargs.get("limit", 100)

            # Build query
            q = Query(schema="concept.axiom", limit=limit)
            results = await self._universe.query(q)

            # Filter by domain and tags
            filtered = results
            if domain:
                filtered = [a for a in filtered if a.domain == domain]
            if tags:
                tag_set = set(tags)
                filtered = [a for a in filtered if tag_set & a.tags]

            return {"axioms": filtered, "count": len(filtered)}

        elif aspect == "axiom.get":
            axiom_id = kwargs.get("id")
            if not axiom_id:
                return {"error": "id required"}

            axiom = await self._universe.get(axiom_id)
            return {"axiom": axiom}

        elif aspect == "axiom.create":
            content = kwargs.get("content")
            domain = kwargs.get("domain")
            tags = kwargs.get("tags", [])

            if not content or not domain:
                return {"error": "content and domain required"}

            axiom = AxiomCrystal(
                content=content,
                domain=domain,
                tags=frozenset(tags),
            )

            axiom_id = await self._universe.store(axiom, "concept.axiom")
            return {"axiom_id": axiom_id, "axiom": axiom}

        elif aspect == "value.list":
            axiom_id = kwargs.get("axiom_id")
            tags = kwargs.get("tags")
            limit = kwargs.get("limit", 100)

            # Build query
            q = Query(schema="concept.value", limit=limit)
            results = await self._universe.query(q)

            # Filter by axiom_id and tags
            filtered = results
            if axiom_id:
                filtered = [v for v in filtered if axiom_id in v.axiom_ids]
            if tags:
                tag_set = set(tags)
                filtered = [v for v in filtered if tag_set & v.tags]

            return {"values": filtered, "count": len(filtered)}

        elif aspect == "value.get":
            value_id = kwargs.get("id")
            if not value_id:
                return {"error": "id required"}

            value = await self._universe.get(value_id)
            return {"value": value}

        elif aspect == "value.create":
            principle = kwargs.get("principle")
            axiom_ids = kwargs.get("axiom_ids", [])
            tags = kwargs.get("tags", [])

            if not principle or not axiom_ids:
                return {"error": "principle and axiom_ids required"}

            value = ValueCrystal(
                principle=principle,
                axiom_ids=tuple(axiom_ids),
                tags=frozenset(tags),
            )

            value_id = await self._universe.store(value, "concept.value")
            return {"value_id": value_id, "value": value}

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# === Exports ===

__all__ = [
    "VoidNode",
    "VoidManifestRendering",
    "VoidManifestResponse",
    "AxiomListRequest",
    "AxiomListResponse",
    "AxiomGetRequest",
    "AxiomGetResponse",
    "AxiomCreateRequest",
    "AxiomCreateResponse",
    "ValueListRequest",
    "ValueListResponse",
    "ValueGetRequest",
    "ValueGetResponse",
    "ValueCreateRequest",
    "ValueCreateResponse",
]
