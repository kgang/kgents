"""
L0 Kernel Runtime

Fail-fast execution of L0 programs.
Per design decision: any error halts immediately, no partial results.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .ast import (
    L0Call,
    L0Compose,
    L0Define,
    L0Emit,
    L0Expr,
    L0Handle,
    L0Literal,
    L0MatchExpr,
    L0ProgramAST,
    L0Stmt,
    L0Witness,
)
from .primitives import Artifact, L0Primitives, TraceWitnessResult

# =============================================================================
# Error Types
# =============================================================================


class L0Error(Exception):
    """
    Fail-fast error. Execution halts immediately.

    Per design decision: no partial results, no recovery.
    """

    def __init__(self, message: str, location: str | None = None):
        self.message = message
        self.location = location
        if location:
            super().__init__(f"L0 Error at {location}: {message}")
        else:
            super().__init__(f"L0 Error: {message}")


# =============================================================================
# Result Types
# =============================================================================


@dataclass(frozen=True)
class L0Result:
    """
    Successful execution result.

    Contains all bindings, artifacts, and witnesses from execution.
    """

    program_name: str
    bindings: dict[str, Any]
    artifacts: tuple[Artifact, ...]
    witnesses: tuple[TraceWitnessResult, ...]
    execution_time_ms: float


# =============================================================================
# Expression Resolution
# =============================================================================


async def resolve_expr(
    expr: L0Expr,
    bindings: dict[str, Any],
    primitives: L0Primitives,
) -> Any:
    """
    Resolve an expression to its value.

    Handles all expression types: Handle, Literal, Call, Compose, Match.
    """
    if isinstance(expr, L0Handle):
        if expr.name not in bindings:
            raise L0Error(f"Undefined handle: {expr.name}")
        return bindings[expr.name]

    elif isinstance(expr, L0Literal):
        return expr.value

    elif isinstance(expr, L0Call):
        # Resolve arguments
        resolved_args: dict[str, Any] = {}
        for arg_name, arg_expr in expr.args:
            resolved_args[arg_name] = await resolve_expr(arg_expr, bindings, primitives)

        # Call the callable
        try:
            result = expr.callable(**resolved_args)
            # Handle async callables
            if inspect.isawaitable(result):
                result = await result
            return result
        except Exception as e:
            raise L0Error(f"Call failed: {e}")

    elif isinstance(expr, L0Compose):
        # Resolve both parts
        first_val = await resolve_expr(expr.first, bindings, primitives)
        second_val = await resolve_expr(expr.second, bindings, primitives)

        # If both are callables, compose them
        if callable(first_val) and callable(second_val):
            return primitives.compose(first_val, second_val)

        # If first is a value and second is a callable, apply
        if callable(second_val):
            result = second_val(first_val)
            if inspect.isawaitable(result):
                result = await result
            return result

        # Otherwise, just return second (pipe-through semantics)
        return second_val

    elif isinstance(expr, L0MatchExpr):
        # Resolve the value to match
        value = await resolve_expr(expr.value, bindings, primitives)
        # Perform the match
        return primitives.match(expr.pattern, value)

    else:
        raise L0Error(f"Unknown expression type: {type(expr).__name__}")


# =============================================================================
# Statement Execution
# =============================================================================


async def execute_stmt(
    stmt: L0Stmt,
    bindings: dict[str, Any],
    primitives: L0Primitives,
    artifacts: list[Artifact],
    witnesses: list[TraceWitnessResult],
) -> dict[str, Any]:
    """
    Execute a single statement.

    Updates bindings for Define, collects artifacts/witnesses for Emit/Witness.
    Returns updated bindings.
    """
    if isinstance(stmt, L0Define):
        try:
            value = await resolve_expr(stmt.expr, bindings, primitives)
            bindings[stmt.name] = value
        except L0Error as e:
            # Add location if not already present
            if e.location is None:
                raise L0Error(e.message, location=f"define {stmt.name}")
            raise
        except Exception as e:
            raise L0Error(str(e), location=f"define {stmt.name}")

    elif isinstance(stmt, L0Emit):
        try:
            content = await resolve_expr(stmt.content, bindings, primitives)
            artifact = primitives.emit(stmt.artifact_type, content)
            artifacts.append(artifact)
        except L0Error as e:
            if e.location is None:
                raise L0Error(e.message, location=f"emit {stmt.artifact_type}")
            raise
        except Exception as e:
            raise L0Error(str(e), location=f"emit {stmt.artifact_type}")

    elif isinstance(stmt, L0Witness):
        try:
            input_val = await resolve_expr(stmt.input_expr, bindings, primitives)
            output_val = await resolve_expr(stmt.output_expr, bindings, primitives)
            witness = primitives.witness(stmt.pass_name, input_val, output_val)
            witnesses.append(witness)
        except L0Error as e:
            if e.location is None:
                raise L0Error(e.message, location=f"witness {stmt.pass_name}")
            raise
        except Exception as e:
            raise L0Error(str(e), location=f"witness {stmt.pass_name}")

    else:
        raise L0Error(f"Unknown statement type: {type(stmt).__name__}")

    return bindings


# =============================================================================
# Program Execution
# =============================================================================


async def run_program(
    program: L0ProgramAST,
    primitives: L0Primitives | None = None,
) -> L0Result:
    """
    Execute L0 program with fail-fast semantics.

    Raises L0Error on ANY failure. No partial results.

    Args:
        program: The L0 program AST to execute
        primitives: Optional primitives instance (uses default if not provided)

    Returns:
        L0Result with bindings, artifacts, and witnesses

    Raises:
        L0Error: On any execution failure
    """
    if primitives is None:
        primitives = L0Primitives()

    start = datetime.now()
    bindings: dict[str, Any] = {}
    artifacts: list[Artifact] = []
    witnesses: list[TraceWitnessResult] = []

    # Execute all statements in order
    for stmt in program.statements:
        bindings = await execute_stmt(stmt, bindings, primitives, artifacts, witnesses)

    elapsed_ms = (datetime.now() - start).total_seconds() * 1000

    return L0Result(
        program_name=program.name,
        bindings=bindings,
        artifacts=tuple(artifacts),
        witnesses=tuple(witnesses),
        execution_time_ms=elapsed_ms,
    )
