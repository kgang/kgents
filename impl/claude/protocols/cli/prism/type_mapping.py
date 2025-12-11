"""
TypeRegistry - Extensible type hint to argparse mapping.

Maps Python type hints to argparse argument configurations.
Supports built-in types and allows registration of custom mappers.

See: spec/protocols/prism.md
"""

from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Union, cast, get_args, get_origin

# Python 3.10+ has types.UnionType for X | Y syntax
if sys.version_info >= (3, 10):
    from types import UnionType
else:
    UnionType = type(None)  # Dummy type for Python < 3.10


class TypeRegistry:
    """
    Extensible registry for type → argparse mapping.

    Built-in mappings:
        str     → {"type": str}
        int     → {"type": int}
        float   → {"type": float}
        bool    → {"action": "store_true"}
        Path    → {"type": Path}
        list[T] → {"nargs": "*", "type": T}
        T | None → marks as not required
        Enum    → {"choices": [...], "type": str}

    Custom types can be registered:
        TypeRegistry.register(MyType, lambda t: {"type": my_parser})
    """

    _custom_mappings: dict[type, Callable[[type], dict[str, Any]]] = {}

    @classmethod
    def register(
        cls, python_type: type, mapper: Callable[[type], dict[str, Any]]
    ) -> None:
        """
        Register a custom type mapping.

        Args:
            python_type: The Python type to map.
            mapper: Function taking the type and returning argparse kwargs.

        Example:
            TypeRegistry.register(
                GrammarLevel,
                lambda t: {"choices": [e.value for e in t], "type": str}
            )
        """
        cls._custom_mappings[python_type] = mapper

    @classmethod
    def unregister(cls, python_type: type) -> None:
        """Remove a custom type mapping."""
        cls._custom_mappings.pop(python_type, None)

    @classmethod
    def map(cls, python_type: type, has_default: bool = False) -> dict[str, Any]:
        """
        Get argparse kwargs for a Python type.

        Args:
            python_type: The type hint to map.
            has_default: Whether the parameter has a default value.

        Returns:
            Dictionary of argparse.add_argument() kwargs.
        """
        # Check for custom mapping first (exact match)
        if python_type in cls._custom_mappings:
            return cls._custom_mappings[python_type](python_type)

        # Handle None type (shouldn't happen but be safe)
        if python_type is type(None):
            return {"type": str, "default": None}

        # Handle Union types (T | None, Optional[T])
        origin = get_origin(python_type)
        args = get_args(python_type)

        # Check for Python 3.10+ union type syntax (str | None)
        if isinstance(python_type, UnionType):
            args = get_args(python_type)
            non_none_args = [a for a in args if a is not type(None)]
            if len(non_none_args) == 1:
                inner_kwargs = cls.map(non_none_args[0], has_default=True)
                inner_kwargs["required"] = False
                return inner_kwargs
            return {"type": str}

        if origin is Union:
            # Filter out NoneType to get the actual type
            non_none_args = [a for a in args if a is not type(None)]
            if len(non_none_args) == 1:
                # This is Optional[T], map the inner type
                inner_kwargs = cls.map(non_none_args[0], has_default=True)
                inner_kwargs["required"] = False
                return inner_kwargs
            # Union of multiple types - fall back to str
            return {"type": str}

        # Handle list types
        if origin is list:
            inner_type = args[0] if args else str
            inner_kwargs = cls.map(inner_type, has_default=True)
            # Extract just the type for nargs
            item_type = inner_kwargs.get("type", str)
            return {"nargs": "*", "type": item_type, "default": []}

        # Handle Enum types
        if isinstance(python_type, type) and issubclass(python_type, Enum):
            return {
                "choices": [e.value for e in python_type],
                "type": str,
            }

        # Check for custom mapping by origin (for generic types)
        if origin in cls._custom_mappings:
            return cls._custom_mappings[origin](python_type)

        # Built-in type mappings
        if python_type is str:
            return {"type": str}

        if python_type is int:
            return {"type": int}

        if python_type is float:
            return {"type": float}

        if python_type is bool:
            # Boolean flags use store_true action
            return {"action": "store_true", "default": False}

        if python_type is Path:
            return {"type": Path}

        # Check if it's a subclass of known types
        if isinstance(python_type, type):
            if issubclass(python_type, Path):
                return {"type": python_type}
            if issubclass(python_type, Enum):
                return {
                    "choices": [e.value for e in python_type],
                    "type": str,
                }

        # Default: treat as string
        return {"type": str}

    @classmethod
    def is_flag_type(cls, python_type: type) -> bool:
        """Check if a type should be treated as a boolean flag."""
        return python_type is bool

    @classmethod
    def is_optional(cls, python_type: type) -> bool:
        """Check if a type is Optional (T | None)."""
        # Check Python 3.10+ union type syntax
        if isinstance(python_type, UnionType):
            args = get_args(python_type)
            return type(None) in args

        origin = get_origin(python_type)
        if origin is Union:
            args = get_args(python_type)
            return type(None) in args
        return False

    @classmethod
    def get_inner_type(cls, python_type: type) -> type:
        """Extract the inner type from Optional[T] or list[T]."""
        # Check Python 3.10+ union type syntax
        if isinstance(python_type, UnionType):
            args = get_args(python_type)
            non_none_args = [a for a in args if a is not type(None)]
            if non_none_args:
                return non_none_args[0]

        origin = get_origin(python_type)
        args = get_args(python_type)

        if origin is Union:
            non_none_args = [a for a in args if a is not type(None)]
            if non_none_args:
                return cast(type, non_none_args[0])

        if origin is list and args:
            return cast(type, args[0])

        return python_type
