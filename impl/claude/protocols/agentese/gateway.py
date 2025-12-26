"""
AGENTESE Universal Gateway.

Auto-exposes all registered @node decorated classes via HTTP/WebSocket.

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

This gateway:
1. Mounts a single dynamic route that handles ALL AGENTESE paths
2. Routes requests to registered nodes via NodeRegistry
3. Fails fast on unregistered paths (AD-016: no JIT fallback)
4. Supports SSE streaming for async generators
5. Supports WebSocket for bidirectional streams

Example:
    from protocols.agentese.gateway import AgenteseGateway

    # Mount on FastAPI app
    gateway = AgenteseGateway()
    gateway.mount_on(app)

    # Now all registered nodes are auto-exposed:
    # GET  /agentese/self/memory/manifest
    # POST /agentese/self/memory/capture
    # GET  /agentese/world/town/manifest
    # etc.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
)

if TYPE_CHECKING:
    from fastapi import FastAPI, Request, WebSocket

from .affordances import get_aspect_metadata
from .node import Observer
from .registry import get_registry

# === Auto-import node modules to register @node decorators ===
# This ensures all nodes are in the registry before discovery


def _import_node_modules() -> None:
    """
    Import all AGENTESE node modules to trigger @node registration.

    This is called lazily when the gateway is mounted, ensuring
    all nodes are discoverable via /agentese/discover.

    Node Discovery Architecture (Phase 2: AGENTESE Path Authority):
    - Service-level nodes (services/*/node.py) are authoritative
    - Context-level nodes (contexts/world_*.py) provide fallback/legacy paths
    - All @node decorated classes auto-register to NodeRegistry
    """
    try:
        # Import contexts to register world.*, self.*, etc. nodes
        from . import contexts  # noqa: F401

        # Import specific context node modules (legacy/fallback)
        # Note: removed 2025-12-21 (Crown Jewel Cleanup):
        #   time_trace_warp, self_archaeology, self_conductor
        from .contexts import (
            concept_derivation,  # noqa: F401 - Derivation Framework (concept.derivation.*)
            concept_intent,  # noqa: F401 - WARP Phase 1: Task decomposition (concept.intent.*)
            concept_scope,  # noqa: F401 - WARP Phase 1: Context contracts (concept.scope.*)
            design,  # noqa: F401 - Design Language System (concept.design.*)
            self_archaeology,  # noqa: F401 - Git Archaeology (self.memory.archaeology.*)
            self_collaboration,  # noqa: F401 - Phase 5C: Human-Agent Turn-Taking (self.collaboration.*)
            self_context,  # noqa: F401 - Typed-Hypergraph Navigation (self.context.*)
            self_differance,  # noqa: F401 - Différance navigation (self.differance.*)
            self_grant,  # noqa: F401 - WARP Phase 1: Permission contracts (self.grant.*)
            self_kgent,  # noqa: F401 - K-gent Sessions (self.kgent.*)
            self_lesson,  # noqa: F401 - WARP Phase 2: Knowledge layer (self.lesson.*)
            self_nphase,  # noqa: F401 - N-Phase Sessions (self.session.*)
            self_playbook,  # noqa: F401 - WARP Phase 1: Lawful workflows (self.playbook.*)
            self_portal,  # noqa: F401 - Portal Token Navigation (self.portal.*)
            self_presence,  # noqa: F401 - CLI v7 Phase 4: Collaborative Canvas (self.presence.*)
            self_repl,  # noqa: F401 - CLI v7 Phase 4: REPL state (self.repl.*)
            self_soul,  # noqa: F401 - K-gent Soul (self.soul.*)
            self_system,  # noqa: F401 - Autopoietic kernel (self.system.*)
            self_trail,  # noqa: F401 - Visual Trail Graph (self.trail.*)
            self_voice,  # noqa: F401 - WARP Phase 2: Anti-Sausage gate (self.voice.gate.*)
            time_differance,  # noqa: F401 - Ghost Heritage DAG (time.differance.*, time.branch.*)
            # Note: world_emergence removed 2025-12-21
            world_file,  # noqa: F401 - CLI v7 Phase 1: File I/O (world.file.*)
            world_gallery,  # noqa: F401 - Gallery V2 (world.emergence.gallery.*)
            world_gallery_api,  # noqa: F401 - Gallery REST API (world.gallery.*)
            world_scenery,  # noqa: F401 - WARP Phase 2: SceneGraph projection (world.scenery.*)
            world_workshop,  # noqa: F401 - Builder's Workshop (world.workshop.*)
        )

        # === Service-level nodes (AD-009 Metaphysical Fullstack) ===
        # These are the authoritative implementations with persistence layers
        # Note: town, chat, forge, gestalt, park removed 2025-12-21 (Crown Jewel Cleanup)

        try:
            from services.brain import node as brain_node  # noqa: F401  # self.memory.*
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (brain): {e}")

        try:
            from services.morpheus import (
                node as morpheus_node,  # noqa: F401  # world.morpheus.*
            )
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (morpheus): {e}")

        # === Witness Crown Jewel nodes ===
        # Note: world_witness context removed 2025-12-21 (Crown Jewel Cleanup)
        try:
            from services.witness import (
                node as witness_node,  # noqa: F401  # self.witness.*
            )
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (witness): {e}")

        try:
            from services.witness import (
                daily_lab as daily_lab_module,  # noqa: F401  # witness.daily_lab.*
            )
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (daily_lab): {e}")

        # === Concept context nodes ===
        try:
            from .contexts import (
                concept_principles,  # noqa: F401  # concept.principles.*
                concept_priors,  # noqa: F401  # concept.compiler.priors.* (ASHC integration)
                concept_specgraph,  # noqa: F401  # concept.specgraph.* (SpecGraph navigation)
            )
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (concept.*): {e}")

        # === Zero Seed Protocol nodes (void.axiom.*, void.value.*, concept.goal.*, etc.) ===
        try:
            from .contexts import zero_seed  # noqa: F401  # Zero Seed Galois Integration
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (zero_seed): {e}")

        # === Living Docs (concept.docs.*, self.docs.*) ===
        try:
            from services.living_docs import node as living_docs_node  # noqa: F401
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (living_docs): {e}")

        # === Liminal Protocols (time.coffee.*, etc.) ===
        try:
            from services.liminal.coffee import node as coffee_node  # noqa: F401
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (coffee): {e}")

        # === Interactive Text Crown Jewel (self.document.*) ===
        try:
            from services.interactive_text import node as interactive_text_node  # noqa: F401
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (interactive_text): {e}")

        # === Dawn Cockpit (time.dawn.*) ===
        try:
            from protocols.dawn import node as dawn_node  # noqa: F401  # time.dawn.*
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (dawn): {e}")

        # === K-Block Crown Jewel (self.kblock.*) ===
        try:
            from services.k_block import node as kblock_node  # noqa: F401  # self.kblock.*
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (k_block): {e}")

        # === Standalone AGENTESE nodes (nodes/*) ===
        try:
            import nodes  # noqa: F401  # world.code.*, void.*, concept.*

            # Register Zero Seed schemas with Universe
            nodes.register_crystal_schemas()
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (nodes): {e}")

        # === WitnessedGraph Crown Jewel (concept.graph.*) ===
        try:
            from services.witnessed_graph import node as graph_node  # noqa: F401  # concept.graph.*
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (witnessed_graph): {e}")

        # === Proxy Handle Crown Jewel (self.proxy.*) ===
        try:
            from services.proxy import node as proxy_node  # noqa: F401  # self.proxy.*
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (proxy): {e}")

        # === Analysis Operad Crown Jewel (concept.analysis.*) ===
        try:
            from services.analysis import node as analysis_node  # noqa: F401  # concept.analysis.*
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (analysis): {e}")

        # === Feed Crown Jewel (self.feed.*) ===
        try:
            from services.feed import node as feed_node  # noqa: F401  # self.feed.*
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (feed): {e}")

        # === Document Director Crown Jewel (concept.document.*) ===
        try:
            from services.director import node as director_node  # noqa: F401  # concept.document.*
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (director): {e}")

        # === Void and Concept Nodes (Zero Seed L1-L4) ===
        try:
            from nodes import (
                concept_node,  # noqa: F401  # concept.*
                void_node,  # noqa: F401  # void.*
            )
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (void/concept): {e}")

        # === Code Crown Jewel (world.code.*) ===
        try:
            from services.code import node as code_node  # noqa: F401  # world.code.*
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (code): {e}")

        # === Sovereign Store Crown Jewel (concept.sovereign.*) ===
        try:
            from services.sovereign import (
                node as sovereign_node,  # noqa: F401  # concept.sovereign.*
            )
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (sovereign): {e}")

        # === D-gent Universe (Layer 0 persistence) ===
        try:
            from agents.d import node as data_node  # noqa: F401  # self.data.*
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (d-gent): {e}")

        # === Fusion Crown Jewel (concept.fusion.*) ===
        try:
            from services.fusion import node as fusion_node  # noqa: F401
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (fusion): {e}")

        # === Foundry Crown Jewel (world.foundry.*) ===
        try:
            from services.foundry import node as foundry_node  # noqa: F401
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (foundry): {e}")

        # === Hypergraph Editor Crown Jewel (self.hypergraph.*) ===
        try:
            from services.hypergraph_editor import node as hypergraph_editor_node  # noqa: F401
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (hypergraph_editor): {e}")

        # === Living Spec Crown Jewel (self.spec.* - not yet implemented) ===
        # Note: living_spec/node.py exists but has no @node decorator yet
        try:
            from services.living_spec import node as living_spec_node  # noqa: F401
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (living_spec): {e}")

        # === Explorer Crown Jewel (world.explorer.*) ===
        try:
            from services.explorer import node as explorer_node  # noqa: F401
        except ImportError as e:
            logger.warning(f"AGENTESE node import failed (explorer): {e}")

        logger.debug("AGENTESE node modules imported for registration")
    except ImportError as e:
        logger.warning(f"Could not import some node modules: {e}")


# Graceful FastAPI import
try:
    from fastapi import APIRouter, HTTPException, Request, WebSocket
    from fastapi.responses import JSONResponse, StreamingResponse

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[assignment, misc]
    Request = None  # type: ignore[assignment, misc]
    WebSocket = None  # type: ignore[assignment, misc]
    StreamingResponse = None  # type: ignore[assignment, misc]
    JSONResponse = None  # type: ignore[assignment, misc]

    class HTTPException(Exception):  # type: ignore[no-redef]
        """
        Stub HTTPException for when FastAPI is not installed.

        Provides the minimal interface needed by gateway code without
        requiring FastAPI as a hard dependency.

        Teaching:
            gotcha: This stub exists for graceful degradation—gateway.py can
                    be imported even without FastAPI for type checking.
                    (Evidence: test_gateway.py::TestGatewayMounting::test_gateway_mounts_successfully)
        """

        def __init__(self, status_code: int, detail: str | dict[str, Any]) -> None:
            self.status_code = status_code
            self.detail = detail
            super().__init__(str(detail))


logger = logging.getLogger(__name__)

# Valid AGENTESE contexts
VALID_CONTEXTS = frozenset({"world", "self", "concept", "void", "time"})


# === Response Helpers ===


def _extract_aspect_metadata_from_class(cls: type[Any]) -> dict[str, dict[str, Any]]:
    """
    Extract @aspect metadata from a node class's methods.

    Inspects all methods of the class looking for __aspect_meta__ attribute
    attached by the @aspect decorator.

    Returns:
        Dict mapping aspect name -> aspect metadata dict with:
        - category: str (e.g., "PERCEPTION", "MUTATION")
        - requiredCapability: str | None (e.g., "write", "admin")
        - effects: list[str] (e.g., ["reads:memory", "writes:crystals"])
        - description: str
        - streaming: bool
    """
    aspect_data: dict[str, dict[str, Any]] = {}

    # Inspect all methods on the class
    for name in dir(cls):
        if name.startswith("_"):
            continue
        try:
            method = getattr(cls, name)
            meta = get_aspect_metadata(method)
            if meta is not None:
                # Convert effects to string list
                effects_str = [str(e) for e in meta.effects] if meta.effects else []

                aspect_data[name] = {
                    "category": meta.category.name
                    if hasattr(meta.category, "name")
                    else str(meta.category),
                    "requiredCapability": meta.required_capability,
                    "effects": effects_str,
                    "description": meta.description or "",
                    "streaming": meta.streaming,
                    "idempotent": meta.idempotent,
                }
        except Exception:
            # Some attributes may not be accessible
            continue

    return aspect_data


def _to_json_safe(obj: Any) -> Any:
    """Convert object to JSON-safe representation."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {k: _to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_json_safe(v) for v in obj]
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dict__"):
        return {k: _to_json_safe(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
    return str(obj)


def _extract_observer(request: "Request") -> Observer:
    """
    Extract Observer from HTTP headers.

    Headers:
    - X-Observer-Archetype: Observer archetype (default: "guest")
    - X-Observer-Capabilities: Comma-separated capabilities (default: "")
    """
    archetype = request.headers.get("X-Observer-Archetype", "guest")
    capabilities_str = request.headers.get("X-Observer-Capabilities", "")
    capabilities = frozenset(c.strip() for c in capabilities_str.split(",") if c.strip())

    return Observer(archetype=archetype, capabilities=capabilities)


async def _generate_sse(gen: AsyncGenerator[Any, None]) -> AsyncGenerator[str, None]:
    """Convert async generator to SSE format.

    Takes raw objects from async generator and wraps them in SSE format:
    `data: {json}\n\n`

    Teaching:
        gotcha: Stream aspects must yield raw dicts/objects, NOT pre-formatted SSE.
                This function wraps output with `data: {json}\n\n`. If the aspect
                already formats SSE, you get double-wrapping: `data: "data: {...}"`.
                (Evidence: test_gateway.py::test_sse_format)

        gotcha: Async generator aspects must NOT be awaited in _invoke_aspect.
                Calling an async generator function returns the generator; awaiting
                fails with "object async_generator can't be used in 'await' expression".
                Use: `return method()` not `await method()`.
                (Evidence: test_self_collaboration.py::test_stream_aspect_returns_generator)
    """
    try:
        async for chunk in gen:
            data = _to_json_safe(chunk)
            yield f"data: {json.dumps(data)}\n\n"
    except Exception as e:
        logger.error(f"SSE stream error: {e}")
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"


# === Gateway ===


@dataclass
class AgenteseGateway:
    """
    Universal gateway for AGENTESE protocol.

    Auto-exposes all @node registered classes via HTTP.
    The protocol IS the API - no explicit routes needed.

    Attributes:
        prefix: URL prefix for gateway routes (default: "/agentese")
        container: Optional ServiceContainer for dependency injection
        enable_streaming: Enable SSE streaming endpoints (default: True)
        enable_websocket: Enable WebSocket endpoints (default: True)
        fallback_to_logos: Fall back to Logos for unregistered paths (default: True)

    Example:
        gateway = AgenteseGateway(prefix="/api/v1")
        gateway.mount_on(app)

    Teaching:
        gotcha: Discovery endpoints MUST be defined BEFORE catch-all routes.
                FastAPI matches routes in definition order, so /discover
                must come before /{path:path}/* or it gets swallowed.
                (Evidence: test_gateway.py::TestGatewayDiscovery)

        gotcha: Law 3 (Completeness)—every AGENTESE invocation emits exactly
                one Mark via _emit_trace(). This happens in _invoke_path(),
                not at the endpoint level, ensuring consistent tracing.
                (Evidence: test_gateway.py::TestGatewayMarkEmission)
    """

    prefix: str = "/agentese"
    container: Any | None = None
    enable_streaming: bool = True
    enable_websocket: bool = True
    # AD-016: Fail-fast on unregistered paths (no JIT fallback by default)
    fallback_to_logos: bool = False
    _router: Any = field(default=None, repr=False)
    _logos: Any = field(default=None, repr=False)

    def _get_logos(self) -> Any:
        """Get or create Logos instance for fallback resolution."""
        if self._logos is None:
            try:
                from .logos import Logos

                self._logos = Logos()
            except ImportError:
                logger.warning("Logos not available for fallback")
        return self._logos

    def mount_on(self, app: "FastAPI") -> None:
        """
        Mount gateway routes on FastAPI app.

        This adds:
        - GET  {prefix}/{path:path}/manifest - Manifest node
        - POST {prefix}/{path:path}/{aspect} - Invoke aspect
        - GET  {prefix}/{path:path}/affordances - List affordances
        - GET  {prefix}/{path:path}/{aspect}/stream - SSE streaming
        - WS   {prefix}/ws/{path:path} - WebSocket (if enabled)

        Args:
            app: FastAPI application instance
        """
        if not HAS_FASTAPI:
            logger.error("Cannot mount gateway: FastAPI not available")
            return

        # Import node modules to populate registry
        _import_node_modules()

        router = APIRouter(prefix=self.prefix, tags=["agentese-gateway"])
        self._router = router

        # === Discovery Endpoints ===
        # IMPORTANT: Must be defined BEFORE catch-all /{path:path}/* routes
        # to prevent /discover/self being matched as path=discover/self
        @router.get("/discover")
        async def discover(
            include_schemas: bool = False,
            include_metadata: bool = False,
        ) -> JSONResponse:
            """
            List all registered AGENTESE paths.

            Query params:
                include_schemas: If true, include JSON Schema for contracts (Phase 7)
                include_metadata: If true, include node metadata for Concept Home (AD-010)

            Returns:
                paths: List of registered paths
                stats: Registry statistics
                metadata: (if include_metadata=true) Node metadata per path
                schemas: (if include_schemas=true) JSON Schema for each path's contracts
            """
            registry = get_registry()
            content: dict[str, Any] = {
                "paths": registry.list_paths(),
                "stats": registry.stats(),
            }

            # Include metadata for Concept Home Protocol (AD-010)
            # Extended for Umwelt v2 (2025-12-19): per-aspect metadata with requiredCapability
            if include_metadata:
                metadata: dict[str, Any] = {}
                for path in registry.list_paths():
                    node_meta = registry.get_metadata(path)
                    node_cls = registry.get(path)

                    # Extract @aspect metadata from class methods
                    aspect_metadata: dict[str, dict[str, Any]] = {}
                    if node_cls is not None:
                        aspect_metadata = _extract_aspect_metadata_from_class(node_cls)

                    if node_meta:
                        # Extract aspects from contracts if available, or from class inspection
                        aspects: list[str] = ["manifest"]  # Default
                        effects: list[str] = []

                        if node_meta.contracts:
                            # Get aspect names from contracts dict keys
                            aspects = list(node_meta.contracts.keys())
                        elif aspect_metadata:
                            # Fall back to introspected @aspect methods
                            aspects = list(aspect_metadata.keys()) or ["manifest"]

                        # Include examples (Habitat 2.0)
                        examples_data = [ex.to_dict() for ex in node_meta.examples]

                        metadata[path] = {
                            "path": path,
                            "description": node_meta.description or None,
                            "aspects": aspects,
                            "effects": effects,
                            "examples": examples_data,
                            # Umwelt v2: Per-aspect metadata with requiredCapability
                            "aspectMetadata": aspect_metadata,
                        }
                    else:
                        metadata[path] = {
                            "path": path,
                            "description": None,
                            "aspects": list(aspect_metadata.keys()) or ["manifest"],
                            "effects": [],
                            "examples": [],
                            "aspectMetadata": aspect_metadata,
                        }

                content["metadata"] = metadata

            if include_schemas:
                from .schema_gen import node_contracts_to_schema

                schemas: dict[str, Any] = {}
                all_contracts = registry.get_all_contracts()

                for path, contracts in all_contracts.items():
                    try:
                        schemas[path] = node_contracts_to_schema(contracts)
                    except Exception as e:
                        logger.warning(f"Failed to generate schema for {path}: {e}")
                        schemas[path] = {"error": str(e)}

                content["schemas"] = schemas
                content["contract_coverage"] = {
                    "paths_with_contracts": len(all_contracts),
                    "total_paths": len(registry.list_paths()),
                    "coverage_pct": (
                        round(len(all_contracts) / len(registry.list_paths()) * 100, 1)
                        if registry.list_paths()
                        else 0
                    ),
                }

            return JSONResponse(content=content)

        @router.get("/openapi.json")
        async def openapi_spec() -> JSONResponse:
            """
            OpenAPI 3.1 spec projected from AGENTESE registry.

            This is a PROJECTION of the AGENTESE registry.
            For the authoritative source, use /agentese/discover.

            The generated spec includes:
            - Standard OpenAPI 3.1 paths and operations
            - x-agentese extensions preserving observer semantics
            - JSON Schema from contracts (when available)
            """
            from .openapi import generate_openapi_spec

            return JSONResponse(content=generate_openapi_spec())

        @router.get("/discover/{context}")
        async def discover_context(context: str) -> JSONResponse:
            """List paths for a specific context."""
            if context not in VALID_CONTEXTS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid context: {context}. Valid: {', '.join(VALID_CONTEXTS)}",
                )
            registry = get_registry()
            return JSONResponse(
                content={
                    "context": context,
                    "paths": registry.list_by_context(context),
                }
            )

        # === Manifest Endpoint ===
        @router.get("/{path:path}/manifest")
        async def manifest(path: str, request: Request) -> JSONResponse:
            """Manifest a node to observer's view."""
            from fastapi import HTTPException as FastAPIHTTPException

            observer = _extract_observer(request)
            agentese_path = path.replace("/", ".")

            try:
                result = await self._invoke_path(agentese_path, "manifest", observer)
                return JSONResponse(
                    content={
                        "path": agentese_path,
                        "aspect": "manifest",
                        "result": _to_json_safe(result),
                    }
                )
            except FastAPIHTTPException:
                raise  # Re-raise HTTP exceptions unchanged
            except Exception as e:
                # AD-011: Log with traceback for debugging 500s
                logger.error(f"Manifest error for {agentese_path}: {e}", exc_info=True)
                raise FastAPIHTTPException(status_code=500, detail=str(e))

        # === Affordances Endpoint ===
        @router.get("/{path:path}/affordances")
        async def affordances(path: str, request: Request) -> JSONResponse:
            """List affordances for a node."""
            from fastapi import HTTPException as FastAPIHTTPException

            observer = _extract_observer(request)
            agentese_path = path.replace("/", ".")

            try:
                result = await self._invoke_path(agentese_path, "affordances", observer)
                return JSONResponse(
                    content={
                        "path": agentese_path,
                        "affordances": result if isinstance(result, list) else [],
                    }
                )
            except FastAPIHTTPException:
                raise  # Re-raise HTTP exceptions (404, etc.) unchanged
            except Exception as e:
                # AD-011: Log with traceback for debugging 500s
                logger.error(f"Affordances error for {agentese_path}: {e}", exc_info=True)
                raise FastAPIHTTPException(status_code=500, detail=str(e))

        # === Aspect Invocation Endpoint (POST) ===
        @router.post("/{path:path}/{aspect}")
        async def invoke_aspect_post(
            path: str,
            aspect: str,
            request: Request,
        ) -> JSONResponse:
            """Invoke an aspect on a node (POST with body kwargs)."""
            from fastapi import HTTPException as FastAPIHTTPException

            observer = _extract_observer(request)
            agentese_path = path.replace("/", ".")

            # Parse request body for kwargs
            try:
                body = await request.json()
                kwargs = body if isinstance(body, dict) else {}
            except Exception:
                kwargs = {}

            try:
                result = await self._invoke_path(agentese_path, aspect, observer, **kwargs)
                return JSONResponse(
                    content={
                        "path": agentese_path,
                        "aspect": aspect,
                        "result": _to_json_safe(result),
                    }
                )
            except FastAPIHTTPException:
                raise  # Re-raise HTTP exceptions (404, etc.) unchanged
            except Exception as e:
                # AD-011: Log with traceback for debugging 500s
                logger.error(f"Invoke error for {agentese_path}.{aspect}: {e}", exc_info=True)
                raise FastAPIHTTPException(status_code=500, detail=str(e))

        # === Aspect Invocation Endpoint (GET) ===
        # This catches GET requests for aspects like /world/emergence/qualia
        # Must be defined AFTER specific routes (/manifest, /affordances) to avoid conflicts
        @router.get("/{path:path}/{aspect}", response_model=None)
        async def invoke_aspect_get(
            path: str,
            aspect: str,
            request: Request,
        ) -> JSONResponse | StreamingResponse:
            """Invoke an aspect on a node (GET with query params)."""
            from fastapi import HTTPException as FastAPIHTTPException

            observer = _extract_observer(request)
            agentese_path = path.replace("/", ".")

            # Parse query params as kwargs
            kwargs = dict(request.query_params)

            try:
                result = await self._invoke_path(agentese_path, aspect, observer, **kwargs)

                # Phase 5: If result is async generator, stream it as SSE
                # This allows aspects like self.witness.stream to work directly
                if hasattr(result, "__aiter__"):
                    return StreamingResponse(
                        _generate_sse(result),
                        media_type="text/event-stream",
                        headers={
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive",
                            "X-Accel-Buffering": "no",
                        },
                    )

                return JSONResponse(
                    content={
                        "path": agentese_path,
                        "aspect": aspect,
                        "result": _to_json_safe(result),
                    }
                )
            except FastAPIHTTPException:
                raise  # Re-raise HTTP exceptions (404, etc.) unchanged
            except Exception as e:
                # AD-011: Log with traceback for debugging 500s
                logger.error(f"Invoke error for {agentese_path}.{aspect}: {e}", exc_info=True)
                raise FastAPIHTTPException(status_code=500, detail=str(e))

        # === SSE Streaming Endpoint ===
        if self.enable_streaming:

            @router.get("/{path:path}/{aspect}/stream")
            async def stream_aspect(
                path: str,
                aspect: str,
                request: Request,
            ) -> StreamingResponse:
                """Stream aspect results via SSE."""
                from fastapi import HTTPException as FastAPIHTTPException

                observer = _extract_observer(request)
                agentese_path = path.replace("/", ".")

                try:
                    result = await self._invoke_path(agentese_path, aspect, observer, _stream=True)

                    # If result is an async generator, stream it
                    if hasattr(result, "__aiter__"):
                        return StreamingResponse(
                            _generate_sse(result),
                            media_type="text/event-stream",
                            headers={
                                "Cache-Control": "no-cache",
                                "Connection": "keep-alive",
                                "X-Accel-Buffering": "no",
                            },
                        )
                    else:
                        # Single result, wrap in SSE format
                        async def single_event() -> AsyncGenerator[str, None]:
                            """Wrap single result as SSE event."""
                            yield f"data: {json.dumps(_to_json_safe(result))}\n\n"

                        return StreamingResponse(
                            single_event(),
                            media_type="text/event-stream",
                        )
                except FastAPIHTTPException:
                    raise  # Re-raise HTTP exceptions (404, etc.) unchanged
                except Exception as e:
                    # AD-011: Log with traceback for debugging 500s
                    logger.error(f"Stream error for {agentese_path}.{aspect}: {e}", exc_info=True)
                    raise FastAPIHTTPException(status_code=500, detail=str(e))

        # === WebSocket Endpoint ===
        if self.enable_websocket:

            @router.websocket("/ws/{path:path}")
            async def websocket_handler(
                websocket: WebSocket,
                path: str,
            ) -> None:
                """WebSocket handler for bidirectional streaming."""
                await websocket.accept()
                agentese_path = path.replace("/", ".")

                # Extract observer from query params or first message
                observer = Observer.guest()

                try:
                    while True:
                        # Receive message
                        data = await websocket.receive_json()
                        aspect = data.get("aspect", "manifest")
                        kwargs = data.get("kwargs", {})

                        # Update observer if provided
                        if "observer" in data:
                            obs_data = data["observer"]
                            observer = Observer(
                                archetype=obs_data.get("archetype", "guest"),
                                capabilities=frozenset(obs_data.get("capabilities", [])),
                            )

                        # Invoke and send result
                        try:
                            result = await self._invoke_path(
                                agentese_path, aspect, observer, **kwargs
                            )

                            # If streaming result, stream each chunk
                            if hasattr(result, "__aiter__"):
                                async for chunk in result:
                                    await websocket.send_json(
                                        {
                                            "type": "chunk",
                                            "data": _to_json_safe(chunk),
                                        }
                                    )
                                await websocket.send_json({"type": "done"})
                            else:
                                await websocket.send_json(
                                    {
                                        "type": "result",
                                        "data": _to_json_safe(result),
                                    }
                                )
                        except Exception as e:
                            await websocket.send_json(
                                {
                                    "type": "error",
                                    "error": str(e),
                                }
                            )

                except Exception as e:
                    logger.debug(f"WebSocket closed for {agentese_path}: {e}")
                finally:
                    try:
                        await websocket.close()
                    except Exception:
                        pass

        # Mount router on app
        app.include_router(router)
        logger.info(f"AGENTESE Gateway mounted at {self.prefix}")

    async def _invoke_path(
        self,
        agentese_path: str,
        aspect: str,
        observer: Observer,
        **kwargs: Any,
    ) -> Any:
        """
        Invoke an aspect on a path.

        Resolution order:
        1. Check NodeRegistry for @node registered class
        2. Fall back to Logos for context resolver paths

        Law 3 (Completeness): Every AGENTESE invocation emits exactly one Mark.
        This method instruments all invocations with Mark emission.

        Note: Parameter renamed from 'path' to 'agentese_path' to avoid collision
        with kwargs that may contain 'path' (e.g., world.file.read path parameter).

        Args:
            agentese_path: AGENTESE path (e.g., "self.memory")
            aspect: Aspect to invoke (e.g., "capture")
            observer: Observer context
            **kwargs: Aspect-specific arguments

        Returns:
            Aspect invocation result

        Raises:
            HTTPException: If path cannot be resolved
        """
        registry = get_registry()
        result: Any = None
        error: Exception | None = None
        is_streaming = False

        try:
            # Try registry first
            if registry.has(agentese_path):
                node = await registry.resolve(agentese_path, self.container)
                if node is not None:
                    # Observer is compatible with Umwelt for node.invoke
                    result = await node.invoke(aspect, observer, **kwargs)  # type: ignore[arg-type]
                    # Check if result is async generator (streaming)
                    is_streaming = hasattr(result, "__aiter__")
                    # Emit Mark for successful invocation
                    self._emit_trace(
                        agentese_path, aspect, observer, result, is_streaming=is_streaming
                    )
                    return result

            # AD-016: Fail-fast on unregistered paths (no JIT fallback)
            # Silent JIT fallback masks registration bugs - fail immediately with helpful error
            from fastapi import HTTPException as FastAPIHTTPException

            # Find similar paths for typo correction
            all_paths = registry.list_paths()
            context_prefix = agentese_path.split(".")[0] if "." in agentese_path else ""
            similar = [p for p in all_paths if context_prefix and p.startswith(context_prefix)][:5]
            if not similar:
                similar = all_paths[:5]

            error = FastAPIHTTPException(
                status_code=404,
                detail={
                    "error": f"Node '{agentese_path}' not registered",
                    "why": "No @node decorator registered this path (AD-016: fail-fast resolution)",
                    "similar_paths": similar,
                    "suggestion": (
                        "To fix: "
                        "1) Ensure @node decorator is applied to your node class, "
                        "2) Import the node module in services/providers.py:setup_providers()"
                    ),
                    "discover_endpoint": f"{self.prefix}/discover",
                },
            )
            raise error

        except Exception as e:
            # Emit Mark for error
            self._emit_trace(agentese_path, aspect, observer, None, error=e)
            raise

    def _emit_trace(
        self,
        path: str,
        aspect: str,
        observer: Observer,
        result: Any,
        *,
        is_streaming: bool = False,
        error: Exception | None = None,
    ) -> None:
        """
        Emit a Mark for an AGENTESE invocation.

        Law 3: Every AGENTESE invocation emits exactly one Mark.

        This method:
        1. Creates a Mark with stimulus and response
        2. Appends to the global MarkStore
        3. Publishes to WitnessSynergyBus for cross-jewel awareness
        """
        try:
            from services.witness.mark import (
                Mark,
                Response,
                Stimulus,
                UmweltSnapshot,
            )
            from services.witness.trace_store import get_mark_store

            # Create stimulus from AGENTESE invocation
            stimulus = Stimulus.from_agentese(path, aspect)

            # Create response based on outcome
            if error is not None:
                response = Response.error(str(error))
            elif is_streaming:
                response = Response(
                    kind="stream",
                    content=f"Streaming {path}.{aspect}",
                    success=True,
                    metadata={"streaming": True},
                )
            else:
                # Summarize result for response
                result_summary = self._summarize_result(result)
                response = Response(
                    kind="projection",
                    content=result_summary,
                    success=True,
                )

            # Create umwelt from observer
            umwelt = UmweltSnapshot(
                observer_id=observer.archetype,
                role=observer.archetype,
                capabilities=observer.capabilities,
                trust_level=0,  # Default trust level
            )

            # Create the Mark
            trace_node = Mark(
                origin="gateway",
                stimulus=stimulus,
                response=response,
                umwelt=umwelt,
                tags=("agentese", path.split(".")[0]),  # e.g., ("agentese", "self")
            )

            # Append to store (Law 3 enforcement)
            store = get_mark_store()
            store.append(trace_node)

            # Publish to SynergyBus for cross-jewel awareness
            self._publish_trace_event(trace_node, error)

            logger.debug(f"Mark emitted for {path}.{aspect}: {trace_node.id}")

        except Exception as e:
            # Don't let trace emission failure break the gateway
            logger.warning(f"Mark emission failed for {path}.{aspect}: {e}")

    def _summarize_result(self, result: Any) -> str:
        """Summarize a result for Mark response content."""
        if result is None:
            return "null"
        if isinstance(result, str):
            return result[:100] + "..." if len(result) > 100 else result
        if isinstance(result, (dict, list)):
            return f"{type(result).__name__}[{len(result)} items]"
        if hasattr(result, "to_dict"):
            return f"{type(result).__name__}"
        return str(result)[:100]

    def _publish_trace_event(self, trace_node: Any, error: Exception | None) -> None:
        """Publish trace event to WitnessSynergyBus."""
        try:
            from services.witness.bus import WitnessTopics, get_synergy_bus

            bus = get_synergy_bus()
            if bus is not None:
                import asyncio

                topic = WitnessTopics.AGENTESE_ERROR if error else WitnessTopics.AGENTESE_INVOKED
                # Non-blocking publish (fire and forget)
                asyncio.create_task(bus.publish(topic, trace_node.to_dict()))

        except Exception as e:
            # Don't let bus failure break the gateway
            logger.debug(f"SynergyBus publish failed: {e}")


# === Factory Functions ===


def create_gateway(
    prefix: str = "/agentese",
    container: Any | None = None,
    enable_streaming: bool = True,
    enable_websocket: bool = True,
    fallback_to_logos: bool = False,
) -> AgenteseGateway:
    """
    Create an AGENTESE gateway instance.

    Args:
        prefix: URL prefix for gateway routes
        container: Optional ServiceContainer for dependency injection
        enable_streaming: Enable SSE streaming endpoints
        enable_websocket: Enable WebSocket endpoints
        fallback_to_logos: Fall back to Logos for unregistered paths (default False, AD-016)

    Returns:
        Configured AgenteseGateway instance
    """
    return AgenteseGateway(
        prefix=prefix,
        container=container,
        enable_streaming=enable_streaming,
        enable_websocket=enable_websocket,
        fallback_to_logos=fallback_to_logos,
    )


def mount_gateway(
    app: "FastAPI",
    prefix: str = "/agentese",
    **kwargs: Any,
) -> AgenteseGateway:
    """
    Create and mount a gateway on a FastAPI app.

    Convenience function combining create_gateway and mount_on.

    Args:
        app: FastAPI application instance
        prefix: URL prefix for gateway routes
        **kwargs: Additional gateway configuration

    Returns:
        Mounted AgenteseGateway instance
    """
    gateway = create_gateway(prefix=prefix, **kwargs)
    gateway.mount_on(app)
    return gateway


# === Exports ===

__all__ = [
    "AgenteseGateway",
    "create_gateway",
    "mount_gateway",
]
