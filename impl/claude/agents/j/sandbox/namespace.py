"""
Sandboxed namespace for JIT agent execution.

This module provides:
- SandboxConfig: Configuration for sandboxed execution
- SandboxResult: Result of sandboxed execution
- SandboxedNamespace: Restricted namespace with safe builtins
"""

from __future__ import annotations

import asyncio
import dataclasses
import datetime
import json
import math
import re
import types
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class SandboxConfig:
    """Configuration for sandboxed execution."""

    timeout_seconds: float = 30.0  # Hard timeout
    allowed_imports: frozenset[str] = dataclasses.field(
        default_factory=lambda: frozenset(
            {
                "re",
                "json",
                "dataclasses",
                "typing",
                "datetime",
                "math",
            }
        )
    )
    type_check: bool = True  # Run mypy before execution
    chaosmonger_check: bool = True  # Run stability analysis
    max_output_size: int = 1_000_000  # 1MB max output


@dataclass(frozen=True)
class SandboxResult:
    """Result of sandboxed execution."""

    success: bool
    output: Any
    error: Optional[str] = None
    stdout: str = ""
    stderr: str = ""
    execution_time_ms: float = 0.0


class SandboxedNamespace:
    """
    Restricted namespace for JIT agent execution.

    Provides:
    - Safe builtins (no eval, exec, __import__, etc.)
    - Whitelisted modules only
    - No file I/O by default
    - No network access
    """

    def __init__(self, allowed_imports: frozenset[str]):
        """Initialize with allowed imports."""
        self.allowed_imports = allowed_imports
        self._namespace: dict[str, Any] = {}

    def build_namespace(self) -> dict[str, Any]:
        """
        Build the restricted namespace for exec().

        Returns a dict with:
        - Restricted __builtins__
        - Whitelisted modules
        - No dangerous operations
        """
        # Start with safe builtins
        safe_builtins = {
            # Type constructors
            "int": int,
            "str": str,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "frozenset": frozenset,
            # Utility functions
            "len": len,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "sorted": sorted,
            "reversed": reversed,
            "sum": sum,
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "any": any,
            "all": all,
            "print": print,  # Allow print for debugging
            # Type checking
            "isinstance": isinstance,
            "issubclass": issubclass,
            "type": type,
            "hasattr": hasattr,
            "getattr": getattr,
            "setattr": setattr,
            # Class/function construction (needed for class definitions)
            "__build_class__": __build_class__,
            "__name__": "__jit_sandbox__",
            # Exceptions
            "Exception": Exception,
            "ValueError": ValueError,
            "TypeError": TypeError,
            "KeyError": KeyError,
            "IndexError": IndexError,
            "AttributeError": AttributeError,
            "RuntimeError": RuntimeError,
            "NotImplementedError": NotImplementedError,
            # Special
            "None": None,
            "True": True,
            "False": False,
            # EXPLICITLY FORBIDDEN (document what we're blocking)
            # "eval": BLOCKED - arbitrary code execution
            # "exec": BLOCKED - arbitrary code execution
            # "compile": BLOCKED - code compilation
            # "__import__": BLOCKED - dynamic imports
            # "open": BLOCKED - file I/O
            # "input": BLOCKED - user input
            # "globals": BLOCKED - namespace inspection
            # "locals": BLOCKED - namespace inspection
            # "vars": BLOCKED - namespace inspection
        }

        namespace: dict[str, Any] = {
            "__builtins__": safe_builtins,
            "__name__": "__jit_sandbox__",
            "__doc__": "JIT agent sandbox namespace",
        }

        # Add whitelisted modules
        available_modules = {
            "re": re,
            "json": json,
            "dataclasses": dataclasses,
            "typing": types.ModuleType("typing"),  # Stub for type hints
            "datetime": datetime,
            "math": math,
            "asyncio": asyncio,
        }

        for module_name in self.allowed_imports:
            if module_name in available_modules:
                namespace[module_name] = available_modules[module_name]

        # typing module needs special handling (it's complex)
        if "typing" in self.allowed_imports:
            import typing

            namespace["typing"] = typing
            # Also add common typing constructs to namespace
            namespace["Optional"] = typing.Optional
            namespace["Any"] = typing.Any
            namespace["Callable"] = typing.Callable
            namespace["Union"] = typing.Union

        return namespace
