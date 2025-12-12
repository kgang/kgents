"""
Meltable: Contract-Bounded Hallucination (Pataphysics)

The @meltable decorator implements "imaginary solutions" - when rigid code fails,
pataphysics provides alternatives bounded by postconditions.

"Pataphysics is the science of imaginary solutions."
- Alfred Jarry

The Veale Protocol:
1. Try the original function
2. If it fails, invoke the pataphysics solver
3. Validate the result against the postcondition (ensure)
4. Retry up to max_retries times
5. Raise ContractViolationError if postcondition cannot be satisfied

Usage:
    @meltable(ensure=lambda x: 0.0 <= x <= 1.0)
    async def calculate_probability(...) -> float:
        '''Hallucinated result MUST satisfy postcondition.'''

The rename from "hallucinate" to "pataphysics.solve" is intentional:
- "Hallucinate" implies error, accident, unreliability
- "Solve" implies deliberate method, even when the method is imaginary

See: plans/concept/creativity.md Phase 8
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from collections.abc import Awaitable


# === Exceptions ===


@dataclass(frozen=True)
class ContractViolationError(Exception):
    """
    Raised when a meltable function cannot satisfy its postcondition.

    The imaginary solution failed to meet the contract requirements
    after exhausting all retries.
    """

    message: str
    attempts: int = 0
    last_result: Any = None
    original_error: Exception | None = None

    def __str__(self) -> str:
        base = self.message
        if self.attempts > 0:
            base += f" (after {self.attempts} attempts)"
        if self.original_error:
            base += f" [original: {type(self.original_error).__name__}]"
        return base


@dataclass(frozen=True)
class MeltingContext:
    """
    Context passed to pataphysics solver functions.

    Contains information about the failure that triggered melting.
    """

    function_name: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    error: Exception
    attempt: int = 0


# === Type Variables ===


T = TypeVar("T")


# === Default Solver ===


async def default_pataphysics_solver(
    ctx: MeltingContext,
) -> Any:
    """
    Default pataphysics solver.

    Returns None as the "imaginary solution" when no custom solver is provided.
    Real implementations would invoke an LLM or other generative system.

    In production, this would be connected to:
    - Logos.invoke("void.pataphysics.solve", ...)
    - An LLM prompt asking for an imaginary solution
    - A fallback value generator based on type hints
    """
    return None


# === The Meltable Decorator ===


def meltable(
    ensure: Callable[[Any], bool] | None = None,
    max_retries: int = 3,
    solver: Callable[[MeltingContext], "Awaitable[Any]"] | None = None,
) -> Callable[[Callable[..., "Awaitable[Any]"]], Callable[..., "Awaitable[Any]"]]:
    """
    Veale Protocol decorator with Contract Enforcement.

    When the decorated function fails:
    1. Invoke the pataphysics solver to generate an imaginary solution
    2. Validate the result against the postcondition (ensure)
    3. Retry up to max_retries times
    4. Raise ContractViolationError if postcondition cannot be satisfied

    Args:
        ensure: Postcondition predicate. Imaginary solution rejected if False.
        max_retries: Attempts before raising ContractViolationError.
        solver: Custom pataphysics solver (defaults to default_pataphysics_solver).

    Returns:
        Decorated async function with contract-bounded fallback.

    Example:
        @meltable(ensure=lambda x: 0.0 <= x <= 1.0, max_retries=3)
        async def calculate_probability(query: str) -> float:
            '''May fail, but pataphysics will provide a valid probability.'''
            return await some_unreliable_api(query)
    """
    pataphysics_solver = solver or default_pataphysics_solver

    def decorator(
        f: Callable[..., "Awaitable[Any]"],
    ) -> Callable[..., "Awaitable[Any]"]:
        @wraps(f)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # First, try the original function
            try:
                result = await f(*args, **kwargs)
                # If ensure is provided, validate the result
                if ensure is not None and not ensure(result):
                    raise ContractViolationError(
                        f"Postcondition failed for {f.__name__}",
                        attempts=0,
                        last_result=result,
                    )
                return result
            except ContractViolationError:
                # Re-raise contract violations (don't melt on contract failure from result)
                raise
            except Exception as original_error:
                # Melt: invoke pataphysics solver with contract enforcement
                last_result: Any = None
                for attempt in range(max_retries):
                    ctx = MeltingContext(
                        function_name=f.__name__,
                        args=args,
                        kwargs=kwargs,
                        error=original_error,
                        attempt=attempt,
                    )
                    imaginary_solution = await pataphysics_solver(ctx)
                    last_result = imaginary_solution

                    # Validate against postcondition
                    if ensure is None or ensure(imaginary_solution):
                        return imaginary_solution

                # Exhausted retries
                raise ContractViolationError(
                    f"Could not satisfy postcondition for {f.__name__}",
                    attempts=max_retries,
                    last_result=last_result,
                    original_error=original_error,
                ) from original_error

        # Attach metadata for introspection
        wrapper._meltable = True  # type: ignore[attr-defined]
        wrapper._ensure = ensure  # type: ignore[attr-defined]
        wrapper._max_retries = max_retries  # type: ignore[attr-defined]

        return wrapper

    return decorator


def meltable_sync(
    ensure: Callable[[Any], bool] | None = None,
    max_retries: int = 3,
    default: Any = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Synchronous version of @meltable for non-async functions.

    Instead of a solver, uses a default value when melting occurs.

    Args:
        ensure: Postcondition predicate. Default rejected if False.
        max_retries: Not used in sync version (for API consistency).
        default: Default value to return when function fails.

    Returns:
        Decorated sync function with contract-bounded fallback.

    Example:
        @meltable_sync(ensure=lambda x: x > 0, default=1)
        def get_positive_count(items: list) -> int:
            '''Returns positive count, falls back to 1 on error.'''
            return len(items)
    """

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = f(*args, **kwargs)
                if ensure is not None and not ensure(result):
                    raise ContractViolationError(
                        f"Postcondition failed for {f.__name__}",
                        attempts=0,
                        last_result=result,
                    )
                return result
            except ContractViolationError:
                raise
            except Exception as original_error:
                if default is not None:
                    if ensure is None or ensure(default):
                        return default
                raise ContractViolationError(
                    f"Could not satisfy postcondition for {f.__name__}",
                    attempts=1,
                    last_result=default,
                    original_error=original_error,
                ) from original_error

        wrapper._meltable = True  # type: ignore[attr-defined]
        wrapper._ensure = ensure  # type: ignore[attr-defined]
        wrapper._default = default  # type: ignore[attr-defined]

        return wrapper

    return decorator


# === Utility Functions ===


def is_meltable(f: Callable[..., Any]) -> bool:
    """Check if a function is decorated with @meltable."""
    return getattr(f, "_meltable", False)


def get_postcondition(f: Callable[..., Any]) -> Callable[[Any], bool] | None:
    """Get the postcondition (ensure) predicate from a meltable function."""
    return getattr(f, "_ensure", None)


# === LLM-backed Solver (Task 3: Wire Pataphysics to LLM) ===


def create_llm_solver(
    ensure: "Callable[[Any], bool] | None" = None,
    verbose: bool = False,
) -> "Callable[[MeltingContext], Awaitable[Any]]":
    """
    Create an LLM-backed pataphysics solver using Claude CLI.

    This factory creates a solver that uses the Claude Code CLI for
    generating imaginary solutions. The CLI handles authentication
    automatically via OAuth.

    Args:
        ensure: Optional postcondition for better prompting
        verbose: Enable debug logging

    Returns:
        Async solver function for use with @meltable(solver=...)

    Example:
        @meltable(
            solver=create_llm_solver(ensure=lambda x: x > 0),
            ensure=lambda x: x > 0,
        )
        async def calculate_value() -> int:
            raise RuntimeError("Boom")

    Note:
        Requires Claude CLI to be installed and authenticated.
        The solver is lazy-initialized on first use.
    """
    from .pataphysics import pataphysics_solver_with_postcondition

    if ensure is not None:
        return pataphysics_solver_with_postcondition(ensure=ensure, verbose=verbose)

    # No postcondition, return a basic solver
    from .pataphysics import create_pataphysics_solver

    return create_pataphysics_solver()


# === Re-exports ===


__all__ = [
    "ContractViolationError",
    "MeltingContext",
    "create_llm_solver",
    "default_pataphysics_solver",
    "get_postcondition",
    "is_meltable",
    "meltable",
    "meltable_sync",
]
