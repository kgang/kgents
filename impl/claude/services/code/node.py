"""
AGENTESE nodes for code artifacts.

Paths:
- world.code.manifest      - Code layer status
- world.code.upload        - Upload single file
- world.code.sync          - Sync directory
- world.code.bootstrap     - Bootstrap spec+impl pair

- world.code.function.list   - List functions
- world.code.function.get    - Get function by ID
- world.code.function.graph  - Get call graph

- world.code.kblock.list     - List K-blocks
- world.code.kblock.get      - Get K-block with contents
- world.code.kblock.suggest  - Suggest boundary changes

- world.code.ghost.list      - List ghost placeholders
- world.code.ghost.resolve   - Mark ghost as resolved

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)
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
    from agents.d.universe import Universe
    from bootstrap.umwelt import Umwelt

    from .service import CodeService


# === Request/Response Contracts ===


@dataclass(frozen=True)
class CodeManifestResponse:
    """Response for world.code.manifest."""

    total_functions: int
    total_kblocks: int
    total_ghosts: int
    backend: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_functions": self.total_functions,
            "total_kblocks": self.total_kblocks,
            "total_ghosts": self.total_ghosts,
            "backend": self.backend,
        }


@dataclass(frozen=True)
class UploadRequest:
    """Request for world.code.upload."""

    file_path: str
    spec_id: str | None = None
    auto_extract: bool = True


@dataclass(frozen=True)
class UploadResponse:
    """Response for world.code.upload."""

    file_path: str
    functions_created: int
    ghosts_created: int
    kblock_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "functions_created": self.functions_created,
            "ghosts_created": self.ghosts_created,
            "kblock_id": self.kblock_id,
        }


@dataclass(frozen=True)
class SyncRequest:
    """Request for world.code.sync."""

    directory: str
    pattern: str = "**/*.py"
    incremental: bool = True


@dataclass(frozen=True)
class SyncResponse:
    """Response for world.code.sync."""

    files_processed: int
    functions_created: int
    functions_updated: int
    kblocks_created: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "files_processed": self.files_processed,
            "functions_created": self.functions_created,
            "functions_updated": self.functions_updated,
            "kblocks_created": self.kblocks_created,
        }


@dataclass(frozen=True)
class BootstrapRequest:
    """Request for world.code.bootstrap."""

    spec_content: str
    impl_content: str
    name: str


@dataclass(frozen=True)
class BootstrapResponse:
    """Response for world.code.bootstrap."""

    spec_id: str
    impl_functions: list[str]
    kblock_id: str
    derivation_edges: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "spec_id": self.spec_id,
            "impl_functions": self.impl_functions,
            "kblock_id": self.kblock_id,
            "derivation_edges": self.derivation_edges,
        }


@dataclass(frozen=True)
class FunctionListRequest:
    """Request for world.code.function.list."""

    prefix: str | None = None
    kblock_id: str | None = None
    limit: int = 100


@dataclass(frozen=True)
class FunctionListResponse:
    """Response for world.code.function.list."""

    functions: list[dict[str, Any]]
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "functions": self.functions,
            "count": self.count,
        }


@dataclass(frozen=True)
class FunctionGetRequest:
    """Request for world.code.function.get."""

    id: str


@dataclass(frozen=True)
class FunctionGetResponse:
    """Response for world.code.function.get."""

    function: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "function": self.function,
        }


@dataclass(frozen=True)
class GraphRequest:
    """Request for world.code.function.graph."""

    function_id: str
    depth: int = 1


@dataclass(frozen=True)
class GraphResponse:
    """Response for world.code.function.graph."""

    graph: dict[str, list[str]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph": self.graph,
        }


@dataclass(frozen=True)
class KBlockListRequest:
    """Request for world.code.kblock.list."""

    limit: int = 100


@dataclass(frozen=True)
class KBlockListResponse:
    """Response for world.code.kblock.list."""

    kblocks: list[dict[str, Any]]
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "kblocks": self.kblocks,
            "count": self.count,
        }


@dataclass(frozen=True)
class KBlockGetRequest:
    """Request for world.code.kblock.get."""

    id: str


@dataclass(frozen=True)
class KBlockGetResponse:
    """Response for world.code.kblock.get."""

    kblock: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "kblock": self.kblock,
        }


@dataclass(frozen=True)
class SuggestRequest:
    """Request for world.code.kblock.suggest."""

    file_path: str


@dataclass(frozen=True)
class SuggestResponse:
    """Response for world.code.kblock.suggest."""

    suggestions: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "suggestions": self.suggestions,
        }


@dataclass(frozen=True)
class GhostListRequest:
    """Request for world.code.ghost.list."""

    limit: int = 100


@dataclass(frozen=True)
class GhostListResponse:
    """Response for world.code.ghost.list."""

    ghosts: list[dict[str, Any]]
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "ghosts": self.ghosts,
            "count": self.count,
        }


@dataclass(frozen=True)
class GhostResolveRequest:
    """Request for world.code.ghost.resolve."""

    id: str


@dataclass(frozen=True)
class GhostResolveResponse:
    """Response for world.code.ghost.resolve."""

    resolved: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "resolved": self.resolved,
        }


# === Code Rendering ===


@dataclass(frozen=True)
class CodeManifestRendering:
    """Rendering for Code manifest."""

    total_functions: int
    total_kblocks: int
    total_ghosts: int
    backend: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "code_manifest",
            "total_functions": self.total_functions,
            "total_kblocks": self.total_kblocks,
            "total_ghosts": self.total_ghosts,
            "backend": self.backend,
        }

    def to_text(self) -> str:
        lines = [
            "Code Artifact Layer",
            "===================",
            f"Backend: {self.backend}",
            f"Total Functions: {self.total_functions}",
            f"Total K-Blocks: {self.total_kblocks}",
            f"Total Ghosts: {self.total_ghosts}",
        ]
        return "\n".join(lines)


# === Code Affordances ===

CODE_AFFORDANCES: tuple[str, ...] = (
    "upload",  # Upload single file
    "sync",  # Sync directory
    "bootstrap",  # Bootstrap spec+impl pair
    "function.list",  # List functions
    "function.get",  # Get function by ID
    "function.graph",  # Get call graph
    "kblock.list",  # List K-blocks
    "kblock.get",  # Get K-block
    "kblock.suggest",  # Suggest boundaries
    "ghost.list",  # List ghosts
    "ghost.resolve",  # Resolve ghost
)


# === CodeNode ===


@node(
    "world.code",
    description="Code artifact tracking - function-level crystals",
    dependencies=("universe", "code_service"),
    contracts={
        "manifest": Response(CodeManifestResponse),
        "upload": Contract(UploadRequest, UploadResponse),
        "sync": Contract(SyncRequest, SyncResponse),
        "bootstrap": Contract(BootstrapRequest, BootstrapResponse),
        "function.list": Contract(FunctionListRequest, FunctionListResponse),
        "function.get": Contract(FunctionGetRequest, FunctionGetResponse),
        "function.graph": Contract(GraphRequest, GraphResponse),
        "kblock.list": Contract(KBlockListRequest, KBlockListResponse),
        "kblock.get": Contract(KBlockGetRequest, KBlockGetResponse),
        "kblock.suggest": Contract(SuggestRequest, SuggestResponse),
        "ghost.list": Contract(GhostListRequest, GhostListResponse),
        "ghost.resolve": Contract(GhostResolveRequest, GhostResolveResponse),
    },
    examples=[
        ("function.list", {"limit": 10}, "List recent functions"),
        ("kblock.list", {}, "List all K-blocks"),
        ("ghost.list", {}, "List ghost placeholders"),
    ],
)
class CodeNode(BaseLogosNode):
    """
    AGENTESE node for Code Crown Jewel.

    Exposes function-level artifact tracking through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/world/code/upload
        {"file_path": "impl/claude/agents/d/node.py"}

        # Via Logos directly
        await logos.invoke("world.code.upload", observer, file_path="...")

        # Via CLI
        kg code upload impl/claude/agents/d/node.py

    Teaching:
        gotcha: CodeNode REQUIRES universe and code_service dependencies.
                Without them, instantiation fails with TypeError—this is intentional!
                It enables Logos fallback when DI isn't configured.

        gotcha: Every CodeNode invocation emits a Mark (WARP Law 3). Don't add
                manual tracing—the gateway handles it at _invoke_path().
    """

    def __init__(self, universe: Universe, code_service: CodeService) -> None:
        """
        Initialize CodeNode.

        Args:
            universe: The Universe instance (injected by container)
            code_service: The CodeService instance (injected by container)

        Raises:
            TypeError: If dependencies are not provided (intentional for fallback)
        """
        self._universe = universe
        self._code_service = code_service

    @property
    def handle(self) -> str:
        return "world.code"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Observer gradation:
        - developer/operator: Full access
        - architect/researcher: Read-only
        - guest: Manifest only
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return CODE_AFFORDANCES

        # Architects/researchers: read-only
        if archetype_lower in ("architect", "researcher", "technical"):
            return (
                "function.list",
                "function.get",
                "function.graph",
                "kblock.list",
                "kblock.get",
                "ghost.list",
            )

        # Guest (default): manifest only
        return ()

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("universe")],
        help="Display code artifact layer status",
        examples=["kg code", "kg code manifest"],
    )
    async def manifest(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Manifest Code layer status to observer.

        AGENTESE: world.code.manifest
        """
        if self._universe is None:
            return BasicRendering(
                summary="Code layer not initialized",
                content="No Universe configured",
                metadata={"error": "no_universe"},
            )

        # Get stats from Universe
        # For now, return placeholder stats
        # In full implementation, would query Universe for function/kblock/ghost counts

        return CodeManifestRendering(
            total_functions=0,
            total_kblocks=0,
            total_ghosts=0,
            backend="universe",
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to CodeService methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if self._code_service is None:
            return {"error": "CodeService not configured"}

        # Route to appropriate method
        if aspect == "upload":
            file_path = kwargs.get("file_path")
            spec_id = kwargs.get("spec_id")
            auto_extract = kwargs.get("auto_extract", True)

            if not file_path:
                return {"error": "file_path required"}

            result = await self._code_service.upload_file(
                file_path=file_path,
                spec_id=spec_id,
                auto_extract_functions=auto_extract,
            )

            return {
                "file_path": result.file_path,
                "functions_created": len(result.functions_created),
                "ghosts_created": len(result.ghosts_created),
                "kblock_id": result.kblock_id,
            }

        elif aspect == "sync":
            directory = kwargs.get("directory")
            pattern = kwargs.get("pattern", "**/*.py")
            incremental = kwargs.get("incremental", True)

            if not directory:
                return {"error": "directory required"}

            result = await self._code_service.sync_directory(
                directory=directory,
                pattern=pattern,
                incremental=incremental,
            )

            return {
                "files_processed": result.files_processed,
                "functions_created": result.functions_created,
                "functions_updated": result.functions_updated,
                "kblocks_created": result.kblocks_created,
            }

        elif aspect == "bootstrap":
            spec_content = kwargs.get("spec_content")
            impl_content = kwargs.get("impl_content")
            name = kwargs.get("name")

            if not all([spec_content, impl_content, name]):
                return {"error": "spec_content, impl_content, and name required"}

            result = await self._code_service.bootstrap_spec_impl_pair(
                spec_content=spec_content,
                impl_content=impl_content,
                name=name,
            )

            return {
                "spec_id": result.spec_id,
                "impl_functions": result.impl_functions,
                "kblock_id": result.kblock_id,
                "derivation_edges": result.derivation_edges,
            }

        elif aspect == "function.list":
            prefix = kwargs.get("prefix")
            kblock_id = kwargs.get("kblock_id")
            limit = kwargs.get("limit", 100)

            # Placeholder implementation
            return {"functions": [], "count": 0}

        elif aspect == "function.get":
            function_id = kwargs.get("id")
            if not function_id:
                return {"error": "id required"}

            # Placeholder implementation
            return {"function": None}

        elif aspect == "function.graph":
            function_id = kwargs.get("function_id")
            depth = kwargs.get("depth", 1)

            if not function_id:
                return {"error": "function_id required"}

            # Placeholder implementation
            return {"graph": {}}

        elif aspect == "kblock.list":
            limit = kwargs.get("limit", 100)

            # Placeholder implementation
            return {"kblocks": [], "count": 0}

        elif aspect == "kblock.get":
            kblock_id = kwargs.get("id")
            if not kblock_id:
                return {"error": "id required"}

            # Placeholder implementation
            return {"kblock": None}

        elif aspect == "kblock.suggest":
            file_path = kwargs.get("file_path")
            if not file_path:
                return {"error": "file_path required"}

            # Placeholder implementation
            return {"suggestions": []}

        elif aspect == "ghost.list":
            limit = kwargs.get("limit", 100)

            # Placeholder implementation
            return {"ghosts": [], "count": 0}

        elif aspect == "ghost.resolve":
            ghost_id = kwargs.get("id")
            if not ghost_id:
                return {"error": "id required"}

            # Placeholder implementation
            return {"resolved": True}

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# === Exports ===

__all__ = [
    "CodeNode",
    "CodeManifestRendering",
    "CodeManifestResponse",
    "UploadRequest",
    "UploadResponse",
    "SyncRequest",
    "SyncResponse",
    "BootstrapRequest",
    "BootstrapResponse",
    "FunctionListRequest",
    "FunctionListResponse",
    "FunctionGetRequest",
    "FunctionGetResponse",
    "GraphRequest",
    "GraphResponse",
    "KBlockListRequest",
    "KBlockListResponse",
    "KBlockGetRequest",
    "KBlockGetResponse",
    "SuggestRequest",
    "SuggestResponse",
    "GhostListRequest",
    "GhostListResponse",
    "GhostResolveRequest",
    "GhostResolveResponse",
]
