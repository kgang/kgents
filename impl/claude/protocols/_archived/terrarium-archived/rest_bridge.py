"""
PrismRestBridge: Auto-generate REST endpoints from CLICapable agents.

The bridge uses Prism's introspection to generate FastAPI endpoints,
creating a thin REST surface over CLI-exposed agent commands.

This is Phase 2 of Terrarium: projecting agent capabilities to HTTP.

Usage:
    from protocols.terrarium import Terrarium, PrismRestBridge
    from protocols.cli.prism import CLICapable

    terrarium = Terrarium()
    bridge = PrismRestBridge()

    # Mount agent commands as REST endpoints
    bridge.mount(terrarium.app, grammar_agent)

    # Now accessible at POST /api/grammar/parse, /api/grammar/reify, etc.
"""

from __future__ import annotations

import inspect
import json
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, get_type_hints

if TYPE_CHECKING:
    from protocols.cli.prism import CLICapable

logger = logging.getLogger(__name__)


@dataclass
class EndpointSpec:
    """
    Specification for a generated REST endpoint.

    Captures the introspected information needed to create
    a FastAPI route from a CLI method.
    """

    name: str
    method: Callable[..., Any]
    parameters: dict[str, ParameterSpec]
    description: str | None = None
    is_async: bool = False


@dataclass
class ParameterSpec:
    """
    Specification for a method parameter.

    Used to generate JSON schema and validate request bodies.
    """

    name: str
    python_type: Any  # Can be type, UnionType, GenericAlias, etc.
    required: bool
    default: Any = None

    def to_json_schema(self) -> dict[str, Any]:
        """Convert to JSON schema property."""
        return _type_to_json_schema(self.python_type)


def _type_to_json_schema(python_type: Any) -> dict[str, Any]:
    """
    Map Python type to JSON schema.

    Handles basic types and common generics.
    Accepts Any because python_type can be UnionType, GenericAlias, etc.
    """
    import sys
    from typing import Union, get_args, get_origin

    # Python 3.10+ union syntax
    if sys.version_info >= (3, 10):
        from types import UnionType
    else:
        UnionType = type(None)

    # Handle None type
    if python_type is type(None):
        return {"type": "null"}

    # Handle Union types (Optional, X | None)
    origin = get_origin(python_type)
    args = get_args(python_type)

    if isinstance(python_type, UnionType) or origin is Union:
        non_none_args = [a for a in args if a is not type(None)]
        if len(non_none_args) == 1:
            # Optional[T] -> schema for T, nullable
            schema = _type_to_json_schema(non_none_args[0])
            schema["nullable"] = True
            return schema
        # Multiple types - anyOf
        return {"anyOf": [_type_to_json_schema(t) for t in non_none_args]}

    # Handle list types
    if origin is list:
        inner_type = args[0] if args else Any
        return {
            "type": "array",
            "items": _type_to_json_schema(inner_type),
        }

    # Handle dict types
    if origin is dict:
        return {"type": "object"}

    # Built-in types
    if python_type is str:
        return {"type": "string"}
    if python_type is int:
        return {"type": "integer"}
    if python_type is float:
        return {"type": "number"}
    if python_type is bool:
        return {"type": "boolean"}

    # Enum types
    from enum import Enum

    if isinstance(python_type, type) and issubclass(python_type, Enum):
        return {
            "type": "string",
            "enum": [e.value for e in python_type],
        }

    # Default: object
    return {"type": "object"}


@dataclass
class PrismRestBridge:
    """
    Generate REST endpoints from CLICapable agents.

    The bridge introspects agent methods to create FastAPI routes.
    Each exposed command becomes a POST endpoint under /api/{genus_name}/.

    Design Principles:
    - Thin bridge, not a framework
    - Uses Prism's type introspection
    - Composable with existing Terrarium

    Example:
        bridge = PrismRestBridge()
        bridge.mount(terrarium.app, grammar_cli)

        # GrammarCLI.parse(text: str) becomes:
        # POST /api/grammar/parse {"text": "Create calendar"}
    """

    # Prefix for all agent API routes
    api_prefix: str = "/api"

    # Mounted agents (genus_name → CLICapable)
    _mounted: dict[str, "CLICapable"] = field(default_factory=dict, init=False)

    def mount(self, app: Any, agent: "CLICapable") -> None:
        """
        Mount a CLICapable agent's commands as REST endpoints.

        Creates a router with endpoints for each exposed command.
        All endpoints accept POST with JSON body.

        Args:
            app: FastAPI application instance
            agent: Agent implementing CLICapable protocol

        Raises:
            ImportError: If FastAPI is not installed
            ValueError: If agent is already mounted
        """
        try:
            from fastapi import APIRouter
            from fastapi.responses import JSONResponse
        except ImportError as e:
            raise ImportError(
                "FastAPI is required for PrismRestBridge. "
                "Install with: pip install fastapi"
            ) from e

        genus = agent.genus_name

        if genus in self._mounted:
            raise ValueError(f"Agent already mounted: {genus}")

        # Create router for this agent
        router = APIRouter(
            prefix=f"{self.api_prefix}/{genus}",
            tags=[genus],
        )

        # Get exposed commands
        commands = agent.get_exposed_commands()

        for name, method in commands.items():
            spec = self._introspect_method(name, method)
            endpoint = self._create_endpoint(spec)

            # Add route
            router.add_api_route(
                f"/{name}",
                endpoint,
                methods=["POST"],
                summary=spec.description or f"Execute {name}",
                response_class=JSONResponse,
            )

            logger.debug(f"Mounted endpoint: POST {self.api_prefix}/{genus}/{name}")

        # Include router in app
        app.include_router(router)
        self._mounted[genus] = agent

        logger.info(f"Mounted {len(commands)} endpoints for {genus}")

    def _introspect_method(self, name: str, method: Callable[..., Any]) -> EndpointSpec:
        """
        Introspect a method to create an EndpointSpec.

        Extracts type hints and parameter information.
        """
        try:
            hints = get_type_hints(method)
        except Exception:
            hints = {}

        sig = inspect.signature(method)
        parameters: dict[str, ParameterSpec] = {}

        for param_name, param in sig.parameters.items():
            # Skip self, cls
            if param_name in ("self", "cls"):
                continue

            # Skip *args, **kwargs
            if param.kind in (
                inspect.Parameter.VAR_KEYWORD,
                inspect.Parameter.VAR_POSITIONAL,
            ):
                continue

            python_type = hints.get(param_name, str)
            has_default = param.default is not inspect.Parameter.empty
            default_value = param.default if has_default else None

            parameters[param_name] = ParameterSpec(
                name=param_name,
                python_type=python_type,
                required=not has_default,
                default=default_value,
            )

        # Get description from @expose metadata or docstring
        description = method.__doc__
        try:
            from protocols.cli.prism import get_expose_meta

            meta = get_expose_meta(method)
            if meta:
                description = meta.help
        except ImportError:
            pass

        return EndpointSpec(
            name=name,
            method=method,
            parameters=parameters,
            description=description,
            is_async=inspect.iscoroutinefunction(method),
        )

    def _create_endpoint(self, spec: EndpointSpec) -> Callable[..., Any]:
        """
        Create a FastAPI endpoint function from an EndpointSpec.

        The endpoint accepts a JSON body and calls the underlying method.
        """
        from fastapi.responses import JSONResponse

        method = spec.method
        is_async = spec.is_async
        param_specs = spec.parameters

        async def endpoint(body: dict[str, Any] = {}) -> JSONResponse:  # noqa: B006
            """Generated endpoint that delegates to agent method."""
            try:
                # Extract and validate parameters
                kwargs = {}
                missing = []

                for name, param_spec in param_specs.items():
                    if name in body:
                        kwargs[name] = body[name]
                    elif param_spec.required:
                        missing.append(name)
                    elif param_spec.default is not None:
                        kwargs[name] = param_spec.default

                if missing:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "Missing required parameters",
                            "missing": missing,
                        },
                    )

                # Call the method
                if is_async:
                    result = await method(**kwargs)
                else:
                    result = method(**kwargs)

                # Return result
                return JSONResponse(content={"success": True, "result": result})

            except Exception as e:
                logger.exception(f"Error in endpoint {spec.name}")
                return JSONResponse(
                    status_code=500,
                    content={"error": str(e), "type": type(e).__name__},
                )

        # Set function name for OpenAPI docs
        endpoint.__name__ = spec.name
        endpoint.__doc__ = spec.description

        return endpoint

    def get_openapi_schema(self, agent: "CLICapable") -> dict[str, Any]:
        """
        Generate OpenAPI schema for an agent's endpoints.

        Useful for documentation and client generation.

        Args:
            agent: The CLICapable agent

        Returns:
            OpenAPI-compatible paths schema
        """
        genus = agent.genus_name
        commands = agent.get_exposed_commands()
        paths: dict[str, Any] = {}

        for name, method in commands.items():
            spec = self._introspect_method(name, method)
            path = f"{self.api_prefix}/{genus}/{name}"

            # Build request body schema
            properties = {}
            required = []

            for param_name, param_spec in spec.parameters.items():
                properties[param_name] = param_spec.to_json_schema()
                if param_spec.required:
                    required.append(param_name)

            paths[path] = {
                "post": {
                    "summary": spec.description or f"Execute {name}",
                    "operationId": f"{genus}_{name}",
                    "tags": [genus],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": properties,
                                    "required": required,
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "result": {"type": "object"},
                                        },
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Bad request",
                        },
                        "500": {
                            "description": "Internal server error",
                        },
                    },
                }
            }

        return paths

    def unmount(self, app: Any, genus_name: str) -> bool:
        """
        Remove a mounted agent.

        Note: FastAPI doesn't support dynamic route removal cleanly.
        This primarily clears our internal tracking.

        Args:
            app: FastAPI application
            genus_name: The genus name to unmount

        Returns:
            True if agent was tracked and removed
        """
        if genus_name in self._mounted:
            del self._mounted[genus_name]
            logger.info(f"Unmounted {genus_name} (routes remain in app)")
            return True
        return False

    @property
    def mounted_agents(self) -> list[str]:
        """List of mounted agent genus names."""
        return list(self._mounted.keys())
