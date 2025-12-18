"""
JSON Schema Generation for AGENTESE Contracts.

Converts Python dataclasses to JSON Schema for FE type generation.

The Schema Generator (Phase 7: Autopoietic Architecture):
- dataclass_to_schema() converts a single dataclass to JSON Schema
- contract_to_schema() converts a Contract/Response/Request to schema dict
- node_contracts_to_schema() converts all contracts for a node

Example:
    from dataclasses import dataclass
    from protocols.agentese.schema_gen import dataclass_to_schema

    @dataclass
    class TownManifest:
        name: str
        citizen_count: int
        is_active: bool
        regions: list[str]

    schema = dataclass_to_schema(TownManifest)
    # Returns JSON Schema:
    # {
    #   "type": "object",
    #   "title": "TownManifest",
    #   "properties": {
    #     "name": {"type": "string"},
    #     "citizen_count": {"type": "integer"},
    #     "is_active": {"type": "boolean"},
    #     "regions": {"type": "array", "items": {"type": "string"}}
    #   },
    #   "required": ["name", "citizen_count", "is_active", "regions"]
    # }
"""

from __future__ import annotations

import logging
import types
from dataclasses import MISSING, fields, is_dataclass
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from .contract import Contract, ContractsDict, ContractType, Request, Response

logger = logging.getLogger(__name__)


# === Type Mapping ===


def python_type_to_json_schema(python_type: Type[Any]) -> dict[str, Any]:
    """
    Convert a Python type to JSON Schema type definition.

    Handles:
    - Primitive types (str, int, float, bool, None)
    - Collections (list, dict, set, tuple)
    - Optional and Union types
    - Nested dataclasses
    - Enums

    Args:
        python_type: Python type annotation

    Returns:
        JSON Schema type definition
    """
    # Handle None type
    if python_type is type(None):
        return {"type": "null"}

    # Handle basic types
    type_mapping = {
        str: {"type": "string"},
        int: {"type": "integer"},
        float: {"type": "number"},
        bool: {"type": "boolean"},
        bytes: {"type": "string", "format": "byte"},
    }

    if python_type in type_mapping:
        return type_mapping[python_type]

    # Handle Any
    if python_type is Any:
        return {}  # Empty schema means any type

    # Get origin for generic types
    origin = get_origin(python_type)
    args = get_args(python_type)

    # Handle Optional (Union[X, None]) and Python 3.10+ union syntax (X | None)
    if origin is Union or origin is types.UnionType:
        non_none_types = [t for t in args if t is not type(None)]
        if len(non_none_types) == 1 and type(None) in args:
            # It's Optional[X] or X | None
            inner_schema = python_type_to_json_schema(non_none_types[0])
            return {**inner_schema, "nullable": True}
        else:
            # It's a real union
            return {"oneOf": [python_type_to_json_schema(t) for t in args]}

    # Handle List/list
    if origin in (list, List):
        if args:
            items_schema = python_type_to_json_schema(args[0])
            return {"type": "array", "items": items_schema}
        return {"type": "array"}

    # Handle Dict/dict
    if origin in (dict, Dict):
        if len(args) >= 2:
            # JSON Schema doesn't support key types directly
            value_schema = python_type_to_json_schema(args[1])
            return {"type": "object", "additionalProperties": value_schema}
        return {"type": "object"}

    # Handle set
    if origin is set:
        if args:
            items_schema = python_type_to_json_schema(args[0])
            return {"type": "array", "items": items_schema, "uniqueItems": True}
        return {"type": "array", "uniqueItems": True}

    # Handle tuple
    if origin is tuple:
        if args:
            # Fixed-length tuple
            return {
                "type": "array",
                "items": [python_type_to_json_schema(t) for t in args],
                "minItems": len(args),
                "maxItems": len(args),
            }
        return {"type": "array"}

    # Handle frozenset
    if origin is frozenset:
        if args:
            items_schema = python_type_to_json_schema(args[0])
            return {"type": "array", "items": items_schema, "uniqueItems": True}
        return {"type": "array", "uniqueItems": True}

    # Handle Enum
    if isinstance(python_type, type) and issubclass(python_type, Enum):
        enum_values = [e.value for e in python_type]
        # Determine type from enum values
        if all(isinstance(v, str) for v in enum_values):
            return {"type": "string", "enum": enum_values}
        elif all(isinstance(v, int) for v in enum_values):
            return {"type": "integer", "enum": enum_values}
        else:
            return {"enum": enum_values}

    # Handle nested dataclass
    if is_dataclass(python_type) and isinstance(python_type, type):
        return dataclass_to_schema(python_type)

    # Fallback for unknown types
    logger.debug(f"Unknown type for JSON Schema: {python_type}, using empty schema")
    return {}


# === Dataclass to Schema ===


def dataclass_to_schema(
    cls: Type[Any],
    include_descriptions: bool = True,
) -> dict[str, Any]:
    """
    Convert a dataclass to JSON Schema.

    Args:
        cls: Dataclass type to convert
        include_descriptions: Include field docstrings if available

    Returns:
        JSON Schema dictionary

    Example:
        @dataclass
        class Citizen:
            name: str
            age: int
            is_active: bool = True

        schema = dataclass_to_schema(Citizen)
    """
    if not is_dataclass(cls):
        raise TypeError(f"{cls.__name__} is not a dataclass")

    # Get type hints for the class
    try:
        type_hints = get_type_hints(cls)
    except Exception as e:
        logger.warning(f"Could not get type hints for {cls.__name__}: {e}")
        type_hints = {}

    # Build properties and required list
    properties: dict[str, Any] = {}
    required: list[str] = []

    for fld in fields(cls):
        # Get the type from hints or field
        field_type = type_hints.get(fld.name, fld.type)

        # Convert type to JSON Schema
        prop_schema = python_type_to_json_schema(field_type)

        # Add description from field metadata if available
        if include_descriptions:
            if fld.metadata and "description" in fld.metadata:
                prop_schema["description"] = fld.metadata["description"]

        # Add default value if present
        if fld.default is not MISSING:
            prop_schema["default"] = fld.default
        elif fld.default_factory is not MISSING:
            # Can't serialize default_factory, note it exists
            prop_schema["hasDefaultFactory"] = True

        properties[fld.name] = prop_schema

        # Add to required if no default
        if fld.default is MISSING and fld.default_factory is MISSING:
            required.append(fld.name)

    schema: dict[str, Any] = {
        "type": "object",
        "title": cls.__name__,
        "properties": properties,
    }

    if required:
        schema["required"] = required

    # Add class docstring as description
    if include_descriptions and cls.__doc__:
        schema["description"] = cls.__doc__.strip()

    return schema


# === Contract to Schema ===


def contract_to_schema(contract: ContractType) -> dict[str, Any]:
    """
    Convert a Contract/Response/Request to JSON Schema dict.

    Args:
        contract: Contract type instance

    Returns:
        Dictionary with 'request' and/or 'response' schemas
    """
    result: dict[str, Any] = {}

    if isinstance(contract, Response):
        result["response"] = dataclass_to_schema(contract.response_type)

    elif isinstance(contract, Request):
        result["request"] = dataclass_to_schema(contract.request_type)

    elif isinstance(contract, Contract):
        result["request"] = dataclass_to_schema(contract.request)
        result["response"] = dataclass_to_schema(contract.response)

    return result


def node_contracts_to_schema(contracts: ContractsDict) -> dict[str, dict[str, Any]]:
    """
    Convert all contracts for a node to JSON Schema dict.

    Args:
        contracts: Dictionary of aspect -> contract

    Returns:
        Dictionary of aspect -> schema dict
    """
    return {
        aspect: contract_to_schema(contract) for aspect, contract in contracts.items()
    }


# === Full Discovery Schema ===


def discovery_schema(
    paths: dict[str, ContractsDict],
) -> dict[str, dict[str, dict[str, Any]]]:
    """
    Generate complete discovery schema for all paths.

    Used by /discover?include_schemas=true endpoint.

    Args:
        paths: Dictionary of path -> contracts dict

    Returns:
        Dictionary of path -> aspect -> schema
    """
    return {
        path: node_contracts_to_schema(contracts) for path, contracts in paths.items()
    }


# === Exports ===

__all__ = [
    "python_type_to_json_schema",
    "dataclass_to_schema",
    "contract_to_schema",
    "node_contracts_to_schema",
    "discovery_schema",
]
