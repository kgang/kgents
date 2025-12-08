"""
Sandbox execution functions for JIT agents.

This module provides:
- type_check_source: Type-check source code with mypy
- execute_in_sandbox: Full sandboxed execution pipeline
- jit_compile_and_execute: Convenience function for one-step execution
"""

from __future__ import annotations

import asyncio
import sys
import time
from io import StringIO
from typing import Any

from ..chaosmonger import StabilityConfig, analyze_stability
from ..meta_architect import AgentSource
from .namespace import SandboxConfig, SandboxResult, SandboxedNamespace


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
