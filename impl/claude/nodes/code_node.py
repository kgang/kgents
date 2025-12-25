"""
Code Node: AGENTESE interface for code artifact operations.

AGENTESE Paths:
- world.code.manifest        - Show code layer status
- world.code.function.list   - List function crystals
- world.code.function.get    - Get function by ID
- world.code.function.store  - Store function crystal
- world.code.function.graph  - Get call graph for function
- world.code.kblock.list     - List K-blocks
- world.code.kblock.get      - Get K-block with contents
- world.code.kblock.suggest  - Suggest boundary changes
- world.code.ghost.list      - List ghost placeholders
- world.code.ghost.resolve   - Mark ghost as resolved
- world.code.upload          - Upload file (parse to functions)
- world.code.sync            - Sync directory
- world.code.derivation      - Get derivation chain for function
- world.code.drift           - Detect spec/impl drift

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: docs/skills/metaphysical-fullstack.md
See: spec/protocols/zero-seed.md
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

if TYPE_CHECKING:
    from agents.d.universe.universe import Universe
    from bootstrap.umwelt import Umwelt


# === Code Node Response Contracts ===


@dataclass(frozen=True)
class CodeManifestResponse:
    """Response for world.code.manifest."""

    backend: str
    total_functions: int
    total_kblocks: int
    total_ghosts: int
    unresolved_ghosts: int
    namespace: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "total_functions": self.total_functions,
            "total_kblocks": self.total_kblocks,
            "total_ghosts": self.total_ghosts,
            "unresolved_ghosts": self.unresolved_ghosts,
            "namespace": self.namespace,
        }


@dataclass(frozen=True)
class FunctionListRequest:
    """Request for world.code.function.list."""

    kblock_id: str | None = None
    layer: int | None = None
    is_ghost: bool = False
    limit: int = 100


@dataclass(frozen=True)
class FunctionListResponse:
    """Response for world.code.function.list."""

    functions: list[dict[str, Any]]
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {"functions": self.functions, "count": self.count}


@dataclass(frozen=True)
class FunctionGetRequest:
    """Request for world.code.function.get."""

    id: str


@dataclass(frozen=True)
class FunctionGetResponse:
    """Response for world.code.function.get."""

    function: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return {"function": self.function}


@dataclass(frozen=True)
class FunctionStoreRequest:
    """Request for world.code.function.store."""

    function: dict[str, Any]  # FunctionCrystal.to_dict()


@dataclass(frozen=True)
class FunctionStoreResponse:
    """Response for world.code.function.store."""

    function_id: str

    def to_dict(self) -> dict[str, Any]:
        return {"function_id": self.function_id}


@dataclass(frozen=True)
class FunctionGraphRequest:
    """Request for world.code.function.graph."""

    id: str
    depth: int = 1  # How many levels of calls to follow


@dataclass(frozen=True)
class FunctionGraphResponse:
    """Response for world.code.function.graph."""

    root: dict[str, Any]
    calls: list[dict[str, Any]]  # Functions this one calls
    called_by: list[dict[str, Any]]  # Functions that call this one
    depth: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": self.root,
            "calls": self.calls,
            "called_by": self.called_by,
            "depth": self.depth,
        }


@dataclass(frozen=True)
class KBlockListRequest:
    """Request for world.code.kblock.list."""

    parent_id: str | None = None
    boundary_type: str | None = None
    limit: int = 100


@dataclass(frozen=True)
class KBlockListResponse:
    """Response for world.code.kblock.list."""

    kblocks: list[dict[str, Any]]
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {"kblocks": self.kblocks, "count": self.count}


@dataclass(frozen=True)
class KBlockGetRequest:
    """Request for world.code.kblock.get."""

    id: str
    include_functions: bool = True


@dataclass(frozen=True)
class KBlockGetResponse:
    """Response for world.code.kblock.get."""

    kblock: dict[str, Any] | None
    functions: list[dict[str, Any]]  # Only if include_functions=True

    def to_dict(self) -> dict[str, Any]:
        return {"kblock": self.kblock, "functions": self.functions}


@dataclass(frozen=True)
class KBlockSuggestRequest:
    """Request for world.code.kblock.suggest."""

    id: str


@dataclass(frozen=True)
class KBlockSuggestResponse:
    """Response for world.code.kblock.suggest."""

    kblock_id: str
    current_boundary: str
    suggestions: list[dict[str, Any]]  # List of suggested changes

    def to_dict(self) -> dict[str, Any]:
        return {
            "kblock_id": self.kblock_id,
            "current_boundary": self.current_boundary,
            "suggestions": self.suggestions,
        }


@dataclass(frozen=True)
class GhostListRequest:
    """Request for world.code.ghost.list."""

    resolved: bool = False
    reason: str | None = None
    limit: int = 100


@dataclass(frozen=True)
class GhostListResponse:
    """Response for world.code.ghost.list."""

    ghosts: list[dict[str, Any]]
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {"ghosts": self.ghosts, "count": self.count}


@dataclass(frozen=True)
class GhostResolveRequest:
    """Request for world.code.ghost.resolve."""

    id: str
    resolved_to: str | None = None  # Function ID if implemented, None if dismissed


@dataclass(frozen=True)
class GhostResolveResponse:
    """Response for world.code.ghost.resolve."""

    ghost_id: str
    resolved: bool
    resolved_to: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ghost_id": self.ghost_id,
            "resolved": self.resolved,
            "resolved_to": self.resolved_to,
        }


@dataclass(frozen=True)
class CodeUploadRequest:
    """Request for world.code.upload."""

    file_path: str
    content: str
    parse: bool = True  # Parse into function crystals


@dataclass(frozen=True)
class CodeUploadResponse:
    """Response for world.code.upload."""

    file_path: str
    functions_created: int
    function_ids: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "functions_created": self.functions_created,
            "function_ids": self.function_ids,
        }


@dataclass(frozen=True)
class CodeSyncRequest:
    """Request for world.code.sync."""

    directory: str
    recursive: bool = True


@dataclass(frozen=True)
class CodeSyncResponse:
    """Response for world.code.sync."""

    directory: str
    files_scanned: int
    functions_created: int
    functions_updated: int
    kblocks_created: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "directory": self.directory,
            "files_scanned": self.files_scanned,
            "functions_created": self.functions_created,
            "functions_updated": self.functions_updated,
            "kblocks_created": self.kblocks_created,
        }


@dataclass(frozen=True)
class DerivationRequest:
    """Request for world.code.derivation."""

    id: str
    include_spec: bool = True


@dataclass(frozen=True)
class DerivationResponse:
    """Response for world.code.derivation."""

    function_id: str
    derivation_chain: list[dict[str, Any]]  # Parent functions
    spec_refs: list[dict[str, Any]]  # Spec references

    def to_dict(self) -> dict[str, Any]:
        return {
            "function_id": self.function_id,
            "derivation_chain": self.derivation_chain,
            "spec_refs": self.spec_refs,
        }


@dataclass(frozen=True)
class DriftRequest:
    """Request for world.code.drift."""

    spec_id: str
    threshold: float = 0.3  # Drift threshold


@dataclass(frozen=True)
class DriftResponse:
    """Response for world.code.drift."""

    spec_id: str
    drift_detected: bool
    drift_score: float
    affected_functions: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "spec_id": self.spec_id,
            "drift_detected": self.drift_detected,
            "drift_score": self.drift_score,
            "affected_functions": self.affected_functions,
        }


# === Code Rendering ===


@dataclass(frozen=True)
class CodeManifestRendering:
    """Rendering for Code manifest."""

    backend: str
    total_functions: int
    total_kblocks: int
    total_ghosts: int
    unresolved_ghosts: int
    namespace: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "code_manifest",
            "backend": self.backend,
            "total_functions": self.total_functions,
            "total_kblocks": self.total_kblocks,
            "total_ghosts": self.total_ghosts,
            "unresolved_ghosts": self.unresolved_ghosts,
            "namespace": self.namespace,
        }

    def to_text(self) -> str:
        lines = [
            "Code Artifact Layer (L5)",
            "========================",
            f"Backend: {self.backend}",
            f"Namespace: {self.namespace}",
            "",
            "Inventory:",
            f"  Functions: {self.total_functions}",
            f"  K-Blocks: {self.total_kblocks}",
            f"  Ghosts: {self.total_ghosts} ({self.unresolved_ghosts} unresolved)",
        ]
        return "\n".join(lines)


# === Code Affordances ===

CODE_AFFORDANCES: tuple[str, ...] = (
    "function.list",  # List function crystals
    "function.get",  # Get function by ID
    "kblock.list",  # List K-blocks
    "kblock.get",  # Get K-block with contents
    "ghost.list",  # List ghost placeholders
)

# Developer/operator affordances (full access)
CODE_ADMIN_AFFORDANCES: tuple[str, ...] = CODE_AFFORDANCES + (
    "function.store",  # Store function crystal
    "function.graph",  # Get call graph
    "kblock.suggest",  # Suggest boundary changes
    "ghost.resolve",  # Mark ghost as resolved
    "upload",  # Upload file (parse to functions)
    "sync",  # Sync directory
    "derivation",  # Get derivation chain
    "drift",  # Detect spec/impl drift
)


# === CodeNode ===


@node(
    "world.code",
    description="Code artifacts - functions, tests, K-blocks",
    dependencies=("universe",),
    contracts={
        # Perception aspects (Response only - no request needed)
        "manifest": Response(CodeManifestResponse),
        # Mutation aspects (Contract with request + response)
        "function.list": Contract(FunctionListRequest, FunctionListResponse),
        "function.get": Contract(FunctionGetRequest, FunctionGetResponse),
        "function.store": Contract(FunctionStoreRequest, FunctionStoreResponse),
        "function.graph": Contract(FunctionGraphRequest, FunctionGraphResponse),
        "kblock.list": Contract(KBlockListRequest, KBlockListResponse),
        "kblock.get": Contract(KBlockGetRequest, KBlockGetResponse),
        "kblock.suggest": Contract(KBlockSuggestRequest, KBlockSuggestResponse),
        "ghost.list": Contract(GhostListRequest, GhostListResponse),
        "ghost.resolve": Contract(GhostResolveRequest, GhostResolveResponse),
        "upload": Contract(CodeUploadRequest, CodeUploadResponse),
        "sync": Contract(CodeSyncRequest, CodeSyncResponse),
        "derivation": Contract(DerivationRequest, DerivationResponse),
        "drift": Contract(DriftRequest, DriftResponse),
    },
    examples=[
        ("function.list", {"limit": 10}, "List recent function crystals"),
        ("ghost.list", {"resolved": False}, "List unresolved ghost functions"),
    ],
)
class CodeNode(BaseLogosNode):
    """
    AGENTESE node for code artifact layer (L5).

    Exposes FunctionCrystal, KBlockCrystal, and GhostFunctionCrystal
    operations through the universal protocol. All transports (HTTP,
    WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/world/code/function/list
        {"limit": 10}

        # Via Logos directly
        await logos.invoke("world.code.function.list", observer, limit=10)

        # Via CLI
        kgents code function list --limit 10

    Teaching:
        gotcha: CodeNode REQUIRES universe dependency. Without it,
                instantiation fails with TypeError—this is intentional!
                It enables Logos fallback when DI isn't configured.

        gotcha: Function crystal operations (function.store, function.graph)
                require developer/operator archetype. Regular users only
                see function.list, function.get.
                (Evidence: affordances vary by archetype)

        gotcha: Every CodeNode invocation emits a Mark (WARP Law 3). Don't add
                manual tracing—the gateway handles it at _invoke_path().
    """

    def __init__(self, universe: Universe) -> None:
        """
        Initialize CodeNode.

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
        return "world.code"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Observer gradation:
        - developer/operator: Full access including mutations
        - architect/researcher: Read operations only
        - guest: Limited read-only (list, get)
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators, admins
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return CODE_ADMIN_AFFORDANCES

        # Architects/researchers: read operations only
        if archetype_lower in ("architect", "researcher", "technical"):
            return CODE_AFFORDANCES

        # Guest (default): limited read-only
        return ("function.list", "function.get", "kblock.list", "ghost.list")

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("universe")],
        help="Display code artifact layer status",
        examples=["kg code", "kg code manifest"],
    )
    async def manifest(
        self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any
    ) -> Renderable:
        """
        Manifest code layer status to observer.

        AGENTESE: world.code.manifest
        """
        if self._universe is None:
            return BasicRendering(
                summary="Code layer not initialized",
                content="No Universe configured",
                metadata={"error": "no_universe"},
            )

        # Get stats from Universe
        stats = await self._universe.stats()

        # Query for function count
        from agents.d.universe.universe import Query

        functions_query = Query(schema="code.function", limit=10000)
        functions = await self._universe.query(functions_query)
        total_functions = len(functions)

        # Query for K-block count
        kblocks_query = Query(schema="code.kblock", limit=10000)
        kblocks = await self._universe.query(kblocks_query)
        total_kblocks = len(kblocks)

        # Query for ghost count
        ghosts_query = Query(schema="code.ghost", limit=10000)
        ghosts = await self._universe.query(ghosts_query)
        total_ghosts = len(ghosts)

        # Count unresolved ghosts
        from agents.d.schemas.ghost import GhostFunctionCrystal

        unresolved_ghosts = sum(
            1 for g in ghosts if isinstance(g, GhostFunctionCrystal) and not g.resolved
        )

        return CodeManifestRendering(
            backend=stats.backend,
            total_functions=total_functions,
            total_kblocks=total_kblocks,
            total_ghosts=total_ghosts,
            unresolved_ghosts=unresolved_ghosts,
            namespace=stats.namespace,
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

        # === Function operations ===
        if aspect == "function.list":
            return await self._function_list(**kwargs)
        elif aspect == "function.get":
            return await self._function_get(**kwargs)
        elif aspect == "function.store":
            return await self._function_store(**kwargs)
        elif aspect == "function.graph":
            return await self._function_graph(**kwargs)

        # === K-block operations ===
        elif aspect == "kblock.list":
            return await self._kblock_list(**kwargs)
        elif aspect == "kblock.get":
            return await self._kblock_get(**kwargs)
        elif aspect == "kblock.suggest":
            return await self._kblock_suggest(**kwargs)

        # === Ghost operations ===
        elif aspect == "ghost.list":
            return await self._ghost_list(**kwargs)
        elif aspect == "ghost.resolve":
            return await self._ghost_resolve(**kwargs)

        # === File operations ===
        elif aspect == "upload":
            return await self._upload(**kwargs)
        elif aspect == "sync":
            return await self._sync(**kwargs)

        # === Analysis operations ===
        elif aspect == "derivation":
            return await self._derivation(**kwargs)
        elif aspect == "drift":
            return await self._drift(**kwargs)

        else:
            return {"error": f"Unknown aspect: {aspect}"}

    # === Function operations ===

    async def _function_list(
        self,
        kblock_id: str | None = None,
        layer: int | None = None,
        is_ghost: bool = False,
        limit: int = 100,
    ) -> dict[str, Any]:
        """List function crystals with optional filters."""
        from agents.d.universe.universe import Query

        # Query functions from Universe
        query = Query(schema="code.function", limit=limit)
        functions = await self._universe.query(query)

        # Apply filters
        if kblock_id:
            functions = [f for f in functions if getattr(f, "kblock_id", None) == kblock_id]
        if layer is not None:
            functions = [f for f in functions if getattr(f, "layer", None) == layer]
        if is_ghost:
            functions = [f for f in functions if getattr(f, "is_ghost", False)]

        # Serialize
        serialized = [f.to_dict() if hasattr(f, "to_dict") else f for f in functions]
        return {"functions": serialized, "count": len(serialized)}

    async def _function_get(self, id: str) -> dict[str, Any]:
        """Get function crystal by ID."""
        function = await self._universe.get(id)
        if function is None:
            return {"function": None}

        serialized = function.to_dict() if hasattr(function, "to_dict") else function
        return {"function": serialized}

    async def _function_store(self, function: dict[str, Any]) -> dict[str, Any]:
        """Store function crystal."""
        from agents.d.schemas.code import FunctionCrystal

        # Deserialize from dict
        func_crystal = FunctionCrystal.from_dict(function)

        # Store via Universe
        function_id = await self._universe.store(func_crystal, schema_name="code.function")

        return {"function_id": function_id}

    async def _function_graph(self, id: str, depth: int = 1) -> dict[str, Any]:
        """Get call graph for a function."""
        # Get root function
        root = await self._universe.get(id)
        if root is None:
            return {
                "root": None,
                "calls": [],
                "called_by": [],
                "depth": depth,
            }

        # Get functions this one calls
        calls_ids = getattr(root, "calls", frozenset())
        calls = []
        for call_id in calls_ids:
            # Try to resolve by qualified name
            from agents.d.universe.universe import Query

            query = Query(schema="code.function", limit=1000)
            all_functions = await self._universe.query(query)
            matching = [
                f
                for f in all_functions
                if getattr(f, "qualified_name", None) == call_id
            ]
            if matching:
                calls.append(
                    matching[0].to_dict()
                    if hasattr(matching[0], "to_dict")
                    else matching[0]
                )

        # Get functions that call this one
        called_by_ids = getattr(root, "called_by", frozenset())
        called_by = []
        for caller_id in called_by_ids:
            from agents.d.universe.universe import Query

            query = Query(schema="code.function", limit=1000)
            all_functions = await self._universe.query(query)
            matching = [
                f
                for f in all_functions
                if getattr(f, "qualified_name", None) == caller_id
            ]
            if matching:
                called_by.append(
                    matching[0].to_dict()
                    if hasattr(matching[0], "to_dict")
                    else matching[0]
                )

        root_dict = root.to_dict() if hasattr(root, "to_dict") else root
        return {
            "root": root_dict,
            "calls": calls,
            "called_by": called_by,
            "depth": depth,
        }

    # === K-block operations ===

    async def _kblock_list(
        self,
        parent_id: str | None = None,
        boundary_type: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """List K-blocks with optional filters."""
        from agents.d.universe.universe import Query

        # Query K-blocks from Universe
        query = Query(schema="code.kblock", limit=limit)
        kblocks = await self._universe.query(query)

        # Apply filters
        if parent_id:
            kblocks = [
                kb for kb in kblocks if getattr(kb, "parent_kblock_id", None) == parent_id
            ]
        if boundary_type:
            kblocks = [
                kb for kb in kblocks if getattr(kb, "boundary_type", None) == boundary_type
            ]

        # Serialize
        serialized = [kb.to_dict() if hasattr(kb, "to_dict") else kb for kb in kblocks]
        return {"kblocks": serialized, "count": len(serialized)}

    async def _kblock_get(
        self, id: str, include_functions: bool = True
    ) -> dict[str, Any]:
        """Get K-block by ID with optional function contents."""
        kblock = await self._universe.get(id)
        if kblock is None:
            return {"kblock": None, "functions": []}

        functions = []
        if include_functions:
            # Get function IDs from K-block
            function_ids = getattr(kblock, "function_ids", frozenset())
            for func_id in function_ids:
                func = await self._universe.get(func_id)
                if func:
                    functions.append(
                        func.to_dict() if hasattr(func, "to_dict") else func
                    )

        kblock_dict = kblock.to_dict() if hasattr(kblock, "to_dict") else kblock
        return {"kblock": kblock_dict, "functions": functions}

    async def _kblock_suggest(self, id: str) -> dict[str, Any]:
        """Suggest boundary changes for a K-block."""
        from agents.d.schemas.kblock import KBLOCK_SIZE_HEURISTICS

        kblock = await self._universe.get(id)
        if kblock is None:
            return {
                "kblock_id": id,
                "current_boundary": "unknown",
                "suggestions": [],
            }

        suggestions = []

        # Check if K-block is oversized
        estimated_tokens = getattr(kblock, "estimated_tokens", 0)
        if estimated_tokens > KBLOCK_SIZE_HEURISTICS["max_tokens"]:
            suggestions.append(
                {
                    "type": "SPLIT",
                    "reason": f"K-block exceeds max tokens ({estimated_tokens} > {KBLOCK_SIZE_HEURISTICS['max_tokens']})",
                    "priority": "high",
                }
            )

        # Check if K-block is undersized
        if estimated_tokens < KBLOCK_SIZE_HEURISTICS["min_tokens"]:
            suggestions.append(
                {
                    "type": "MERGE",
                    "reason": f"K-block below min tokens ({estimated_tokens} < {KBLOCK_SIZE_HEURISTICS['min_tokens']})",
                    "priority": "low",
                }
            )

        # Check coherence metrics
        internal_coherence = getattr(kblock, "internal_coherence", 1.0)
        if internal_coherence < 0.5:
            suggestions.append(
                {
                    "type": "REFACTOR",
                    "reason": f"Low internal coherence ({internal_coherence:.2f})",
                    "priority": "medium",
                }
            )

        # Check coupling
        external_coupling = getattr(kblock, "external_coupling", 0.0)
        if external_coupling > 0.7:
            suggestions.append(
                {
                    "type": "DECOUPLE",
                    "reason": f"High external coupling ({external_coupling:.2f})",
                    "priority": "medium",
                }
            )

        boundary_type = getattr(kblock, "boundary_type", "unknown")
        return {
            "kblock_id": id,
            "current_boundary": boundary_type,
            "suggestions": suggestions,
        }

    # === Ghost operations ===

    async def _ghost_list(
        self, resolved: bool = False, reason: str | None = None, limit: int = 100
    ) -> dict[str, Any]:
        """List ghost placeholders with optional filters."""
        from agents.d.universe.universe import Query

        # Query ghosts from Universe
        query = Query(schema="code.ghost", limit=limit)
        ghosts = await self._universe.query(query)

        # Apply filters
        ghosts = [
            g for g in ghosts if getattr(g, "resolved", True) == resolved
        ]
        if reason:
            ghosts = [
                g for g in ghosts if getattr(g, "ghost_reason", None) == reason
            ]

        # Serialize
        serialized = [g.to_dict() if hasattr(g, "to_dict") else g for g in ghosts]
        return {"ghosts": serialized, "count": len(serialized)}

    async def _ghost_resolve(
        self, id: str, resolved_to: str | None = None
    ) -> dict[str, Any]:
        """Mark ghost as resolved."""
        from datetime import UTC, datetime

        ghost = await self._universe.get(id)
        if ghost is None:
            return {
                "ghost_id": id,
                "resolved": False,
                "resolved_to": None,
            }

        # Create updated ghost (frozen dataclass)
        from agents.d.schemas.ghost import GhostFunctionCrystal

        updated_ghost = GhostFunctionCrystal(
            id=ghost.id,
            suggested_name=ghost.suggested_name,
            suggested_location=ghost.suggested_location,
            ghost_reason=ghost.ghost_reason,
            source_id=ghost.source_id,
            expected_signature=ghost.expected_signature,
            expected_behavior=ghost.expected_behavior,
            spec_id=ghost.spec_id,
            resolved=True,
            resolved_to=resolved_to,
            resolved_at=datetime.now(UTC),
            created_at=ghost.created_at,
        )

        # Store updated ghost
        await self._universe.store(updated_ghost, schema_name="code.ghost")

        return {
            "ghost_id": id,
            "resolved": True,
            "resolved_to": resolved_to,
        }

    # === File operations ===

    async def _upload(
        self, file_path: str, content: str, parse: bool = True
    ) -> dict[str, Any]:
        """Upload file and optionally parse into function crystals."""
        # TODO: Implement file parsing with AST
        # For now, return placeholder
        return {
            "file_path": file_path,
            "functions_created": 0,
            "function_ids": [],
        }

    async def _sync(self, directory: str, recursive: bool = True) -> dict[str, Any]:
        """Sync directory and parse into function crystals."""
        # TODO: Implement directory sync with AST parsing
        # For now, return placeholder
        return {
            "directory": directory,
            "files_scanned": 0,
            "functions_created": 0,
            "functions_updated": 0,
            "kblocks_created": 0,
        }

    # === Analysis operations ===

    async def _derivation(
        self, id: str, include_spec: bool = True
    ) -> dict[str, Any]:
        """Get derivation chain for a function."""
        function = await self._universe.get(id)
        if function is None:
            return {
                "function_id": id,
                "derivation_chain": [],
                "spec_refs": [],
            }

        # Get parent functions
        derived_from = getattr(function, "derived_from", ())
        derivation_chain = []
        for parent_name in derived_from:
            # Try to resolve by qualified name
            from agents.d.universe.universe import Query

            query = Query(schema="code.function", limit=1000)
            all_functions = await self._universe.query(query)
            matching = [
                f
                for f in all_functions
                if getattr(f, "qualified_name", None) == parent_name
            ]
            if matching:
                derivation_chain.append(
                    matching[0].to_dict()
                    if hasattr(matching[0], "to_dict")
                    else matching[0]
                )

        # Get spec references
        spec_refs = []
        if include_spec:
            spec_id = getattr(function, "spec_id", None)
            if spec_id:
                spec_refs.append({"spec_id": spec_id})

        return {
            "function_id": id,
            "derivation_chain": derivation_chain,
            "spec_refs": spec_refs,
        }

    async def _drift(self, spec_id: str, threshold: float = 0.3) -> dict[str, Any]:
        """Detect spec/impl drift."""
        # TODO: Implement drift detection with Galois loss
        # For now, return placeholder
        return {
            "spec_id": spec_id,
            "drift_detected": False,
            "drift_score": 0.0,
            "affected_functions": [],
        }


# === Exports ===

__all__ = [
    "CodeNode",
    "CodeManifestRendering",
    "CodeManifestResponse",
    "FunctionListRequest",
    "FunctionListResponse",
    "FunctionGetRequest",
    "FunctionGetResponse",
    "FunctionStoreRequest",
    "FunctionStoreResponse",
    "FunctionGraphRequest",
    "FunctionGraphResponse",
    "KBlockListRequest",
    "KBlockListResponse",
    "KBlockGetRequest",
    "KBlockGetResponse",
    "KBlockSuggestRequest",
    "KBlockSuggestResponse",
    "GhostListRequest",
    "GhostListResponse",
    "GhostResolveRequest",
    "GhostResolveResponse",
    "CodeUploadRequest",
    "CodeUploadResponse",
    "CodeSyncRequest",
    "CodeSyncResponse",
    "DerivationRequest",
    "DerivationResponse",
    "DriftRequest",
    "DriftResponse",
]
