"""
OpenAPI Projection Surface.

The OpenAPILens functor projects AGENTESE registry -> OpenAPI 3.1 spec.
This is lossy by design: observer-dependence maps to x-agentese extensions.

The Core Insight:
    OpenAPI (REST): ONE route + ONE method = ONE operation
    AGENTESE:       ONE path + MANY observers = MANY semantic operations

This is not a paradigm mismatch to fix. It's observer-dependent perception
made visible via x-agentese extensions.

Example:
    from protocols.agentese.openapi import generate_openapi_spec, OpenAPILens

    # Generate spec directly
    spec = generate_openapi_spec()

    # Or use the lens pattern
    lens = OpenAPILens(title="My API", version="1.0.0")
    spec = lens.project()

The generated spec includes:
    - Standard OpenAPI 3.1 paths and operations
    - x-agentese info extension (contexts, observer header)
    - x-agentese-path extensions per operation
    - JSON Schema from contracts (when available)

@see plans/openapi-projection-surface.md
"""

from __future__ import annotations

import logging
from typing import Any

from .contract import Contract, ContractType, Request, Response
from .registry import NodeMetadata, get_registry
from .schema_gen import dataclass_to_schema

logger = logging.getLogger(__name__)

# AGENTESE contexts
CONTEXTS = ("world", "self", "concept", "void", "time")


def generate_openapi_spec(
    title: str = "KGENTS AGENTESE API",
    version: str = "1.0.0",
    description: str | None = None,
    base_path: str = "/agentese",
) -> dict[str, Any]:
    """
    Generate OpenAPI 3.1 spec from AGENTESE registry.

    This is a PROJECTION--lossy by design:
    - Observer semantics -> x-agentese extensions
    - Streaming aspects -> text/event-stream media type
    - Examples -> OpenAPI examples object
    - Contracts -> JSON Schema components

    Args:
        title: API title for the spec
        version: API version string
        description: API description (defaults to AGENTESE explanation)
        base_path: Base path for all operations (default: /agentese)

    Returns:
        OpenAPI 3.1 spec as dictionary

    Example:
        spec = generate_openapi_spec()
        # Use with FastAPI: app.openapi_schema = spec
    """
    registry = get_registry()
    paths_list = registry.list_paths()

    # Default description explains AGENTESE
    if description is None:
        description = (
            "AGENTESE Universal Protocol - Observer-dependent API.\n\n"
            "Unlike REST where one route = one operation, AGENTESE paths "
            "return different results based on the observer. Use the "
            "`X-Observer-Archetype` header to specify your perspective."
        )

    spec: dict[str, Any] = {
        "openapi": "3.1.0",
        "info": {
            "title": title,
            "version": version,
            "description": description,
            "x-agentese": {
                "version": "3",
                "contexts": list(CONTEXTS),
                "observer_header": "X-Observer-Archetype",
                "capabilities_header": "X-Observer-Capabilities",
                "discovery_endpoint": f"{base_path}/discover",
            },
        },
        "servers": [{"url": base_path, "description": "AGENTESE Gateway"}],
        "paths": {},
        "components": {
            "securitySchemes": {
                "observerArchetype": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-Observer-Archetype",
                    "description": "Observer archetype (guest, developer, mayor, etc.)",
                },
                "observerCapabilities": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-Observer-Capabilities",
                    "description": "Comma-separated observer capabilities",
                },
            },
            "schemas": {},
        },
        "tags": [
            {"name": "world", "description": "External entities and environments"},
            {"name": "self", "description": "Internal memory and capability"},
            {"name": "concept", "description": "Abstract definitions and logic"},
            {"name": "void", "description": "Entropy and serendipity"},
            {"name": "time", "description": "Traces and schedules"},
            {"name": "discovery", "description": "Path discovery and metadata"},
        ],
    }

    # Add discovery endpoint
    _add_discovery_endpoint(spec, base_path)

    # Generate path operations from registry
    for agentese_path in sorted(paths_list):
        metadata = registry.get_metadata(agentese_path)
        contracts = registry.get_contracts(agentese_path) or {}
        _add_path_operations(spec, agentese_path, metadata, contracts, base_path)

    return spec


def _add_discovery_endpoint(spec: dict[str, Any], base_path: str) -> None:
    """Add the /discover endpoint to the spec."""
    spec["paths"]["/discover"] = {
        "get": {
            "operationId": "discover_paths",
            "summary": "Discover all registered AGENTESE paths",
            "description": (
                "Returns all registered paths with optional metadata and schemas.\n\n"
                "Query parameters:\n"
                "- `include_metadata`: Include aspects, effects, examples per path\n"
                "- `include_schemas`: Include JSON Schema for contracts"
            ),
            "tags": ["discovery"],
            "parameters": [
                {
                    "name": "include_metadata",
                    "in": "query",
                    "schema": {"type": "boolean", "default": False},
                    "description": "Include metadata (aspects, effects, examples) per path",
                },
                {
                    "name": "include_schemas",
                    "in": "query",
                    "schema": {"type": "boolean", "default": False},
                    "description": "Include JSON Schema for contracts",
                },
            ],
            "responses": {
                "200": {
                    "description": "Discovery response",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "paths": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of registered AGENTESE paths",
                                    },
                                    "stats": {
                                        "type": "object",
                                        "description": "Registry statistics",
                                    },
                                    "metadata": {
                                        "type": "object",
                                        "description": "Per-path metadata (if include_metadata=true)",
                                    },
                                    "schemas": {
                                        "type": "object",
                                        "description": "JSON Schema per path (if include_schemas=true)",
                                    },
                                },
                                "required": ["paths", "stats"],
                            }
                        }
                    },
                }
            },
        }
    }


def _add_path_operations(
    spec: dict[str, Any],
    agentese_path: str,
    metadata: NodeMetadata | None,
    contracts: dict[str, ContractType],
    base_path: str,
) -> None:
    """
    Add OpenAPI operations for an AGENTESE path.

    Creates:
    - GET /{path}/manifest - Default manifest operation
    - GET /{path}/affordances - List available aspects
    - POST /{path}/{aspect} - For each aspect in contracts
    - GET /{path}/{aspect}/stream - SSE streaming variant
    """
    # Convert dots to slashes for OpenAPI path
    url_path = f"/{agentese_path.replace('.', '/')}"
    context = agentese_path.split(".")[0] if "." in agentese_path else "world"
    # Use full URL path for operation ID to ensure uniqueness
    operation_id_base = url_path.replace("/", "_").lstrip("_")

    description = metadata.description if metadata else None

    # x-agentese extension for all operations on this path
    x_agentese_path: dict[str, Any] = {
        "x-agentese-path": agentese_path,
    }

    # Add examples if available
    examples_list: list[dict[str, Any]] = []
    if metadata and metadata.examples:
        for ex in metadata.examples:
            examples_list.append(ex.to_dict())

    if examples_list:
        x_agentese_path["x-agentese-examples"] = examples_list

    # === Manifest endpoint (GET) ===
    spec["paths"][f"{url_path}/manifest"] = {
        "get": {
            "operationId": f"{operation_id_base}_manifest",
            "summary": f"Manifest {agentese_path}",
            "description": description or f"Get manifest view of {agentese_path}",
            "tags": [context],
            **x_agentese_path,
            "responses": {
                "200": _build_response_schema(contracts.get("manifest"), "Manifest response"),
                "404": {"description": "Path not found"},
            },
        }
    }

    # === Affordances endpoint (GET) ===
    spec["paths"][f"{url_path}/affordances"] = {
        "get": {
            "operationId": f"{operation_id_base}_affordances",
            "summary": f"List affordances for {agentese_path}",
            "description": "Returns available aspects (actions) that can be invoked on this path",
            "tags": [context],
            **x_agentese_path,
            "responses": {
                "200": {
                    "description": "Affordances list",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "path": {"type": "string"},
                                    "affordances": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                            }
                        }
                    },
                },
                "404": {"description": "Path not found"},
            },
        }
    }

    # === Aspect endpoints (POST for mutations, GET for queries) ===
    for aspect, contract in contracts.items():
        if aspect == "manifest":
            continue  # Already added above

        # Normalize aspect: replace dots with slashes for URL, underscores for ID
        aspect_url_segment = aspect.replace(".", "/")
        aspect_url = f"{url_path}/{aspect_url_segment}"

        # Skip if URL already exists (handles overlap like world.town.citizen.list vs world.town with citizen.list aspect)
        if aspect_url in spec["paths"]:
            logger.debug(f"Skipping duplicate path {aspect_url} from {agentese_path}.{aspect}")
            continue

        aspect_operation_id = f"{operation_id_base}_{aspect.replace('.', '_')}"

        # Determine HTTP method based on contract type
        # Response-only contracts can use GET; Request+Response use POST
        is_mutation = isinstance(contract, (Contract, Request))

        operation = {
            "operationId": aspect_operation_id,
            "summary": f"Invoke {aspect} on {agentese_path}",
            "tags": [context],
            **x_agentese_path,
            "x-agentese-aspect": aspect,
            "responses": {
                "200": _build_response_schema(contract, "Successful invocation"),
                "404": {"description": "Path not found"},
                "500": {"description": "Internal error"},
            },
        }

        if is_mutation:
            # Add request body for mutations
            operation["requestBody"] = _build_request_body(contract)
            spec["paths"][aspect_url] = {"post": operation}
        else:
            spec["paths"][aspect_url] = {"get": operation}

        # === SSE streaming variant ===
        stream_url = f"{aspect_url}/stream"

        # Skip if stream URL already exists
        if stream_url in spec["paths"]:
            continue

        spec["paths"][stream_url] = {
            "get": {
                "operationId": f"{aspect_operation_id}_stream",
                "summary": f"Stream {aspect} on {agentese_path}",
                "description": "Server-Sent Events streaming variant",
                "tags": [context],
                **x_agentese_path,
                "x-agentese-aspect": aspect,
                "x-agentese-streaming": True,
                "responses": {
                    "200": {
                        "description": "SSE event stream",
                        "content": {
                            "text/event-stream": {
                                "schema": {"type": "string"},
                            }
                        },
                    },
                    "404": {"description": "Path not found"},
                },
            }
        }


def _build_response_schema(
    contract: ContractType | None,
    description: str,
) -> dict[str, Any]:
    """
    Build OpenAPI response schema from contract.

    When schema generation fails, the response includes x-agentese-schema-error
    extension documenting why, rather than failing silently.
    """
    if contract is None:
        return {
            "description": description,
            "content": {"application/json": {}},
        }

    # Extract response type
    response_type = None
    if isinstance(contract, Response):
        response_type = contract.response_type
    elif isinstance(contract, Contract):
        response_type = contract.response

    if response_type is None:
        return {
            "description": description,
            "content": {"application/json": {}},
        }

    # Generate JSON Schema from dataclass
    try:
        schema = dataclass_to_schema(response_type)
        return {
            "description": description,
            "content": {
                "application/json": {
                    "schema": schema,
                }
            },
        }
    except Exception as e:
        # Document the failure in x-agentese-schema-error rather than failing silently
        logger.warning(f"Schema generation failed for {response_type}: {e}")
        return {
            "description": description,
            "content": {"application/json": {}},
            "x-agentese-schema-error": {
                "type": response_type.__name__
                if hasattr(response_type, "__name__")
                else str(response_type),
                "reason": str(e),
                "suggestion": "Ensure the response type is a dataclass with valid type hints",
            },
        }


def _build_request_body(contract: ContractType | None) -> dict[str, Any]:
    """
    Build OpenAPI request body from contract.

    When schema generation fails, the request body includes x-agentese-schema-error
    extension documenting why, rather than failing silently.
    """
    if contract is None:
        return {"content": {"application/json": {}}}

    # Extract request type
    request_type = None
    if isinstance(contract, Request):
        request_type = contract.request_type
    elif isinstance(contract, Contract):
        request_type = contract.request

    if request_type is None:
        return {"content": {"application/json": {}}}

    # Generate JSON Schema from dataclass
    try:
        schema = dataclass_to_schema(request_type)
        return {
            "required": True,
            "content": {
                "application/json": {
                    "schema": schema,
                }
            },
        }
    except Exception as e:
        # Document the failure in x-agentese-schema-error rather than failing silently
        logger.warning(f"Schema generation failed for request {request_type}: {e}")
        return {
            "content": {"application/json": {}},
            "x-agentese-schema-error": {
                "type": request_type.__name__
                if hasattr(request_type, "__name__")
                else str(request_type),
                "reason": str(e),
                "suggestion": "Ensure the request type is a dataclass with valid type hints",
            },
        }


class OpenAPILens:
    """
    Functor: AGENTESE Registry -> OpenAPI 3.1 Spec.

    The lens is the projection function. Calling project() invokes
    the functor, collapsing AGENTESE semantics into REST semantics.

    This is explicitly lossy--observer-dependent behavior cannot be
    fully captured in OpenAPI's one-route-one-operation model. The
    x-agentese extensions preserve what REST cannot express.

    Example:
        lens = OpenAPILens(title="My API")
        spec = lens.project()

        # Serve via FastAPI
        @app.get("/openapi.json")
        def openapi():
            return lens.project()

    Attributes:
        title: API title
        version: API version
        description: API description
        base_path: Base path for operations
    """

    def __init__(
        self,
        title: str = "KGENTS AGENTESE API",
        version: str = "1.0.0",
        description: str | None = None,
        base_path: str = "/agentese",
    ):
        self.title = title
        self.version = version
        self.description = description
        self.base_path = base_path

    def project(self) -> dict[str, Any]:
        """
        Project AGENTESE registry to OpenAPI spec.

        Returns:
            OpenAPI 3.1 spec dictionary
        """
        return generate_openapi_spec(
            title=self.title,
            version=self.version,
            description=self.description,
            base_path=self.base_path,
        )


# === Exports ===

__all__ = [
    "generate_openapi_spec",
    "OpenAPILens",
]
