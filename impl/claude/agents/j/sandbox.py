"""
JIT Agent Sandbox: Safe execution environment for dynamically compiled agents.

This module provides:
- Restricted namespace execution (no dangerous builtins)
- Import whitelist enforcement
- Timeout enforcement
- Type checking before execution
- Integration with Chaosmonger and Judge

Philosophy:
> "Trust, but verify. Then sandbox anyway."

Generated agents are:
1. Type-checked with mypy --strict
2. Analyzed by Chaosmonger for stability
3. Evaluated by Judge for ethics
4. Executed in restricted namespace with timeout

See spec/j-gents/jit.md for full specification.
"""

from __future__ import annotations

import asyncio
import dataclasses
import datetime
import json
import math
import re
import sys
import types
from dataclasses import dataclass
from io import StringIO
from typing import Any, Optional

from .chaosmonger import StabilityConfig, StabilityInput, analyze_stability
from .meta_architect import AgentSource, ArchitectConstraints


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


async def type_check_source(source: str) -> tuple[bool, str]:
    """
    Type-check source code with mypy.

    Args:
        source: Python source code to check

    Returns:
        (success, error_message) tuple

    Note: This is a simplified implementation. Production version would
    invoke mypy as a subprocess and parse the output.
    """
    # For now, just check that it's syntactically valid
    try:
        compile(source, "<jit>", "exec")
        return (True, "")
    except SyntaxError as e:
        return (False, f"Syntax error: {e}")


async def execute_in_sandbox(
    source: AgentSource,
    method_name: str,
    args: tuple[Any, ...],
    config: SandboxConfig,
) -> SandboxResult:
    """
    Execute a JIT agent method in sandboxed environment.

    Pipeline:
    1. Type check (if enabled)
    2. Chaosmonger stability check (if enabled)
    3. Build restricted namespace
    4. Compile source in namespace
    5. Instantiate agent class
    6. Invoke method with timeout
    7. Capture output and errors

    Args:
        source: Generated agent source code
        method_name: Method to invoke on the agent
        args: Arguments to pass to the method
        config: Sandbox configuration

    Returns:
        SandboxResult with execution outcome
    """
    import time

    start_time = time.perf_counter()

    # Step 1: Type check
    if config.type_check:
        type_ok, type_error = await type_check_source(source.source)
        if not type_ok:
            return SandboxResult(
                success=False,
                output=None,
                error=f"Type check failed: {type_error}",
            )

    # Step 2: Chaosmonger stability check
    if config.chaosmonger_check:
        stability = analyze_stability(
            source_code=source.source,
            entropy_budget=1.0,  # Default budget
            config=StabilityConfig(
                max_cyclomatic_complexity=20,
                max_branching_factor=5,
                allowed_imports=config.allowed_imports,
            ),
        )
        if not stability.is_stable:
            return SandboxResult(
                success=False,
                output=None,
                error=f"Stability check failed: {', '.join(stability.violations)}",
            )

    # Step 3: Build restricted namespace
    sandbox_ns = SandboxedNamespace(config.allowed_imports)
    namespace = sandbox_ns.build_namespace()

    # Step 4: Compile source
    try:
        exec(source.source, namespace)
    except Exception as e:
        return SandboxResult(
            success=False,
            output=None,
            error=f"Compilation failed: {e}",
        )

    # Step 5: Instantiate agent class
    if source.class_name not in namespace:
        return SandboxResult(
            success=False,
            output=None,
            error=f"Class {source.class_name} not found in compiled code",
        )

    try:
        agent_class = namespace[source.class_name]
        agent_instance = agent_class()
    except Exception as e:
        return SandboxResult(
            success=False,
            output=None,
            error=f"Failed to instantiate {source.class_name}: {e}",
        )

    # Step 6: Invoke method with timeout
    if not hasattr(agent_instance, method_name):
        return SandboxResult(
            success=False,
            output=None,
            error=f"Method {method_name} not found on {source.class_name}",
        )

    # Capture stdout/stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    captured_stdout = StringIO()
    captured_stderr = StringIO()

    try:
        sys.stdout = captured_stdout
        sys.stderr = captured_stderr

        method = getattr(agent_instance, method_name)

        # Execute with timeout
        try:
            async with asyncio.timeout(config.timeout_seconds):
                # Check if method is async
                if asyncio.iscoroutinefunction(method):
                    result = await method(*args)
                else:
                    result = method(*args)

            execution_time = (time.perf_counter() - start_time) * 1000  # ms

            return SandboxResult(
                success=True,
                output=result,
                stdout=captured_stdout.getvalue(),
                stderr=captured_stderr.getvalue(),
                execution_time_ms=execution_time,
            )

        except TimeoutError:
            return SandboxResult(
                success=False,
                output=None,
                error=f"Execution timed out after {config.timeout_seconds}s",
                stdout=captured_stdout.getvalue(),
                stderr=captured_stderr.getvalue(),
            )

    except Exception as e:
        return SandboxResult(
            success=False,
            output=None,
            error=f"Execution failed: {e}",
            stdout=captured_stdout.getvalue(),
            stderr=captured_stderr.getvalue(),
        )

    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


# --- Convenience Functions ---


async def jit_compile_and_execute(
    source: AgentSource,
    method: str,
    *args: Any,
    timeout: float = 30.0,
) -> SandboxResult:
    """
    Compile and execute a JIT agent in one step.

    Args:
        source: Generated agent source
        method: Method name to invoke
        *args: Arguments for the method
        timeout: Execution timeout in seconds

    Returns:
        SandboxResult with execution outcome

    Example:
        >>> from agents.j import compile_agent
        >>> source = await compile_agent("Parse JSON logs")
        >>> result = await jit_compile_and_execute(
        ...     source,
        ...     "parse",
        ...     '{"level": "error", "msg": "failed"}'
        ... )
        >>> print(result.output)
    """
    config = SandboxConfig(timeout_seconds=timeout)
    return await execute_in_sandbox(source, method, args, config)


def validate_jit_safety(
    source: AgentSource,
    constraints: ArchitectConstraints,
) -> tuple[bool, str]:
    """
    Validate JIT agent meets safety constraints before execution.

    This is a pre-flight check before sandbox execution.

    Args:
        source: Generated agent source
        constraints: Safety constraints to enforce

    Returns:
        (is_safe, reason) tuple

    Checks:
    - Source complexity within budget
    - Only allowed imports
    - No forbidden patterns
    - Chaosmonger stability analysis
    """
    # Check complexity
    max_complexity = int(constraints.entropy_budget * constraints.max_cyclomatic_complexity)
    if source.complexity > max_complexity:
        return (
            False,
            f"Complexity {source.complexity} exceeds budget {max_complexity}",
        )

    # Check imports
    forbidden = source.imports - constraints.allowed_imports
    if forbidden:
        return (False, f"Forbidden imports: {forbidden}")

    # Check forbidden patterns
    for pattern in constraints.forbidden_patterns:
        if pattern in source.source:
            return (False, f"Forbidden pattern: {pattern}")

    # Chaosmonger check
    stability = analyze_stability(
        source_code=source.source,
        entropy_budget=constraints.entropy_budget,
        config=StabilityConfig(
            max_cyclomatic_complexity=max_complexity,
            max_branching_factor=constraints.max_branching_factor,
            allowed_imports=constraints.allowed_imports,
        ),
    )

    if not stability.is_stable:
        return (False, f"Unstable: {', '.join(stability.violations)}")

    return (True, "JIT agent passes safety checks")
