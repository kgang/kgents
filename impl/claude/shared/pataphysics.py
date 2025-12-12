"""
Pataphysics Solver - LLM-backed Imaginary Solutions

Wire the @meltable decorator to use the Claude CLI for generating
"imaginary solutions" when functions fail.

'Pataphysics is the science of imaginary solutions.
- Alfred Jarry

This module provides:
1. PataphysicsAgent - LLMAgent for generating imaginary solutions
2. create_pataphysics_solver() - Factory for LLM-backed solvers
3. PataphysicsSolverConfig - Configuration for solver behavior

The solver uses the existing runtime/cli.py infrastructure which
leverages the Claude CLI's built-in OAuth authentication.
"""

from __future__ import annotations

import inspect
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable

from runtime.base import AgentContext, LLMAgent

if TYPE_CHECKING:
    from runtime.cli import ClaudeCLIRuntime

    from .melting import MeltingContext


class PataphysicsMode(Enum):
    """
    Mode of imaginary solution generation.

    Different modes invoke different creative strategies:
    - CLINAMEN: Small creative deviation (the Lucretian "swerve")
    - SYZYGY: Unexpected alignment of disparate concepts
    - ANOMALY: Direct resolution of the exception via inference
    """

    CLINAMEN = "clinamen"  # Creative perturbation
    SYZYGY = "syzygy"  # Unexpected alignment
    ANOMALY = "anomaly"  # Direct inference


@dataclass(frozen=True)
class PataphysicsSolverConfig:
    """
    Configuration for the pataphysics solver.

    Attributes:
        mode: Default mode for imaginary solution generation
        temperature: LLM temperature (higher = more creative)
        max_tokens: Maximum response tokens
        include_type_hints: Whether to include type hints in prompts
        verbose: Enable debug logging
    """

    mode: PataphysicsMode = PataphysicsMode.ANOMALY
    temperature: float = 0.7
    max_tokens: int = 2048
    include_type_hints: bool = True
    verbose: bool = False


@dataclass
class PataphysicsResult:
    """
    Result from pataphysics solver.

    Attributes:
        value: The imaginary solution
        mode: Mode used to generate the solution
        reasoning: Explanation of the solution
        confidence: Solver's confidence in the solution (0.0-1.0)
    """

    value: Any
    mode: PataphysicsMode
    reasoning: str
    confidence: float = 0.5


# === Prompt Templates ===


SYSTEM_PROMPT = """You are a Pataphysics Solver - a generator of "imaginary solutions."

'Pataphysics is the science of imaginary solutions, which symbolically attributes
the properties of objects, described by their virtuality, to their lineaments.
- Alfred Jarry

When a function fails, you provide an imaginary solution that:
1. SATISFIES the postcondition (contract) if one is specified
2. Is PLAUSIBLE given the function's purpose and arguments
3. Demonstrates CREATIVE problem-solving while remaining grounded

You respond in JSON format with:
{
    "value": <the imaginary solution - must match the expected return type>,
    "reasoning": "<brief explanation of your solution>",
    "confidence": <float between 0.0 and 1.0>
}

CRITICAL: The "value" field must be valid JSON. For strings, use "string".
For numbers, use 42 or 3.14. For booleans, use true or false.
For None/null, use null. For complex types, serialize appropriately."""


def build_anomaly_prompt(ctx: "MeltingContext", postcondition_str: str | None) -> str:
    """Build prompt for ANOMALY mode - direct inference."""
    lines = [
        f"## Function Failed: {ctx.function_name}",
        f"## Error: {type(ctx.error).__name__}: {ctx.error}",
        "",
        "## Arguments:",
        f"  args: {ctx.args}",
        f"  kwargs: {ctx.kwargs}",
    ]

    if postcondition_str:
        lines.extend(
            [
                "",
                "## Postcondition (MUST satisfy):",
                f"  {postcondition_str}",
            ]
        )

    lines.extend(
        [
            "",
            "## Task:",
            "Generate an imaginary solution that would make sense as the",
            "return value of this function. The solution must satisfy any",
            "postconditions specified above.",
            "",
            'Respond with JSON: {"value": <solution>, "reasoning": "...", "confidence": 0.X}',
        ]
    )

    return "\n".join(lines)


def build_clinamen_prompt(ctx: "MeltingContext", postcondition_str: str | None) -> str:
    """Build prompt for CLINAMEN mode - creative deviation."""
    lines = [
        f"## Function Failed: {ctx.function_name}",
        f"## Error: {type(ctx.error).__name__}: {ctx.error}",
        "",
        "## Arguments:",
        f"  args: {ctx.args}",
        f"  kwargs: {ctx.kwargs}",
    ]

    if postcondition_str:
        lines.extend(
            [
                "",
                "## Postcondition (MUST satisfy):",
                f"  {postcondition_str}",
            ]
        )

    lines.extend(
        [
            "",
            "## Task (CLINAMEN - The Swerve):",
            "The clinamen is Lucretius' concept of the 'swerve' - a small",
            "unpredictable deviation that creates novelty.",
            "",
            "Generate a solution that introduces a small creative deviation",
            "from what might be expected, while still satisfying any postconditions.",
            "The deviation should be surprising yet plausible.",
            "",
            'Respond with JSON: {"value": <solution>, "reasoning": "...", "confidence": 0.X}',
        ]
    )

    return "\n".join(lines)


def build_syzygy_prompt(ctx: "MeltingContext", postcondition_str: str | None) -> str:
    """Build prompt for SYZYGY mode - unexpected alignment."""
    lines = [
        f"## Function Failed: {ctx.function_name}",
        f"## Error: {type(ctx.error).__name__}: {ctx.error}",
        "",
        "## Arguments:",
        f"  args: {ctx.args}",
        f"  kwargs: {ctx.kwargs}",
    ]

    if postcondition_str:
        lines.extend(
            [
                "",
                "## Postcondition (MUST satisfy):",
                f"  {postcondition_str}",
            ]
        )

    lines.extend(
        [
            "",
            "## Task (SYZYGY - Unexpected Alignment):",
            "In 'pataphysics, syzygy is the alignment of disparate concepts",
            "to create meaning through unexpected connections.",
            "",
            "Generate a solution that finds an unexpected but valid alignment",
            "between the function's purpose and a solution that satisfies",
            "the postcondition. Draw connections that aren't obvious.",
            "",
            'Respond with JSON: {"value": <solution>, "reasoning": "...", "confidence": 0.X}',
        ]
    )

    return "\n".join(lines)


# === PataphysicsAgent ===


@dataclass
class PataphysicsAgent(LLMAgent["MeltingContext", PataphysicsResult]):
    """
    LLMAgent for generating imaginary solutions via pataphysics.

    Usage:
        agent = PataphysicsAgent(config=PataphysicsSolverConfig())
        result = await runtime.execute(agent, melting_context)
        imaginary_solution = result.output.value
    """

    config: PataphysicsSolverConfig = field(default_factory=PataphysicsSolverConfig)
    postcondition: Callable[[Any], bool] | None = None
    postcondition_source: str | None = None

    @property
    def name(self) -> str:
        return f"PataphysicsAgent({self.config.mode.value})"

    async def invoke(self, input: "MeltingContext") -> PataphysicsResult:
        """Not implemented - use execute_async with runtime."""
        raise NotImplementedError("Use runtime.execute(agent, input) instead")

    def build_prompt(self, input: "MeltingContext") -> AgentContext:
        """Convert MeltingContext to LLM prompt."""
        # Get postcondition string
        postcondition_str = self.postcondition_source
        if postcondition_str is None and self.postcondition is not None:
            # Try to get source code of postcondition
            try:
                postcondition_str = inspect.getsource(self.postcondition).strip()
            except (OSError, TypeError):
                postcondition_str = str(self.postcondition)

        # Build mode-specific prompt
        match self.config.mode:
            case PataphysicsMode.CLINAMEN:
                user_prompt = build_clinamen_prompt(input, postcondition_str)
            case PataphysicsMode.SYZYGY:
                user_prompt = build_syzygy_prompt(input, postcondition_str)
            case PataphysicsMode.ANOMALY:
                user_prompt = build_anomaly_prompt(input, postcondition_str)

        return AgentContext(
            system_prompt=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

    def parse_response(self, response: str) -> PataphysicsResult:
        """Parse LLM response to PataphysicsResult."""
        # Try to extract JSON from response
        json_match = re.search(r"\{[^{}]*\}", response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return PataphysicsResult(
                    value=data.get("value"),
                    mode=self.config.mode,
                    reasoning=data.get("reasoning", "No reasoning provided"),
                    confidence=float(data.get("confidence", 0.5)),
                )
            except (json.JSONDecodeError, ValueError, KeyError):
                pass

        # Fallback: try to extract just a value
        # Look for common patterns
        value_match = re.search(r'"value"\s*:\s*([^,}\n]+)', response)
        if value_match:
            value_str = value_match.group(1).strip()
            try:
                value = json.loads(value_str)
            except json.JSONDecodeError:
                value = value_str.strip('"')

            return PataphysicsResult(
                value=value,
                mode=self.config.mode,
                reasoning="Extracted from partial response",
                confidence=0.3,
            )

        # Last resort: return None with low confidence
        return PataphysicsResult(
            value=None,
            mode=self.config.mode,
            reasoning=f"Could not parse response: {response[:200]}",
            confidence=0.1,
        )


# === Solver Factory ===


def create_pataphysics_solver(
    runtime: "ClaudeCLIRuntime | None" = None,
    config: PataphysicsSolverConfig | None = None,
    postcondition: Callable[[Any], bool] | None = None,
    postcondition_source: str | None = None,
) -> Callable[["MeltingContext"], Any]:
    """
    Create an LLM-backed pataphysics solver.

    This factory returns an async function suitable for use with @meltable:

        solver = create_pataphysics_solver()

        @meltable(solver=solver, ensure=lambda x: x > 0)
        async def my_function() -> int:
            raise RuntimeError("Boom")

    Args:
        runtime: ClaudeCLIRuntime instance. Created lazily if not provided.
        config: Solver configuration. Uses defaults if not provided.
        postcondition: Optional postcondition predicate for prompting.
        postcondition_source: Optional source code of postcondition.

    Returns:
        Async function (MeltingContext) -> Any for use as solver
    """
    _config = config or PataphysicsSolverConfig()
    _runtime: "ClaudeCLIRuntime | None" = runtime
    _postcondition = postcondition
    _postcondition_source = postcondition_source

    async def llm_pataphysics_solver(ctx: "MeltingContext") -> Any:
        """LLM-backed pataphysics solver."""
        nonlocal _runtime

        # Lazy-initialize runtime
        if _runtime is None:
            from runtime.cli import ClaudeCLIRuntime

            _runtime = ClaudeCLIRuntime(
                timeout=60.0,
                max_retries=2,
                verbose=_config.verbose,
            )

        # Create agent
        agent = PataphysicsAgent(
            config=_config,
            postcondition=_postcondition,
            postcondition_source=_postcondition_source,
        )

        # Execute
        result = await _runtime.execute(agent, ctx)
        return result.output.value

    return llm_pataphysics_solver


# === Convenience Functions ===


def pataphysics_solver_with_postcondition(
    ensure: Callable[[Any], bool],
    mode: PataphysicsMode = PataphysicsMode.ANOMALY,
    verbose: bool = False,
) -> Callable[["MeltingContext"], Any]:
    """
    Create a pataphysics solver that knows about the postcondition.

    This is a convenience wrapper that extracts the postcondition source
    code for better prompting.

    Usage:
        @meltable(
            solver=pataphysics_solver_with_postcondition(
                ensure=lambda x: 0.0 <= x <= 1.0
            ),
            ensure=lambda x: 0.0 <= x <= 1.0,
        )
        async def calculate_probability() -> float:
            ...
    """
    # Try to get source code
    try:
        source = inspect.getsource(ensure).strip()
    except (OSError, TypeError):
        source = str(ensure)

    config = PataphysicsSolverConfig(mode=mode, verbose=verbose)
    return create_pataphysics_solver(
        config=config,
        postcondition=ensure,
        postcondition_source=source,
    )


# === AGENTESE Integration: void.pataphysics.solve ===


async def void_hallucinate(
    func: Callable[..., Any],
    error: Exception,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    runtime: "ClaudeCLIRuntime | None" = None,
    mode: PataphysicsMode = PataphysicsMode.ANOMALY,
    postcondition: Callable[[Any], bool] | None = None,
) -> Any:
    """
    Invoke imaginary solution via LLM when reality fails.

    This is the AGENTESE entry point for void.pataphysics.solve.
    When a function fails (raises an exception), this function uses the
    Claude CLI to generate a plausible result that satisfies the contract.

    'Pataphysics is the science of imaginary solutions.
    - Alfred Jarry

    Args:
        func: The function that failed
        error: The exception that was raised
        args: Positional arguments that were passed to func
        kwargs: Keyword arguments that were passed to func
        runtime: Optional ClaudeCLIRuntime instance (created if None)
        mode: Pataphysics mode (ANOMALY, CLINAMEN, or SYZYGY)
        postcondition: Optional postcondition the result must satisfy

    Returns:
        An imaginary solution that is plausible given the function's contract

    Example:
        @meltable(solver=void_hallucinate)
        async def risky_operation() -> dict:
            raise ConnectionError("Network unavailable")

        # When risky_operation fails, void_hallucinate generates
        # a plausible result based on the function signature and context

    AGENTESE Usage:
        result = await logos.invoke(
            "void.pataphysics.solve",
            observer,
            func=my_func,
            error=caught_error,
            args=original_args,
            kwargs=original_kwargs,
        )
    """
    # Build MeltingContext
    from .melting import MeltingContext

    ctx = MeltingContext(
        function_name=func.__name__,
        args=args,
        kwargs=kwargs,
        error=error,
    )

    # Create solver with config
    config = PataphysicsSolverConfig(mode=mode)
    solver = create_pataphysics_solver(
        runtime=runtime,
        config=config,
        postcondition=postcondition,
    )

    # Invoke and return
    return await solver(ctx)


async def void_hallucinate_with_type(
    expected_type: type[Any],
    error: Exception,
    context: str = "",
    runtime: "ClaudeCLIRuntime | None" = None,
    mode: PataphysicsMode = PataphysicsMode.ANOMALY,
) -> Any:
    """
    Generate an imaginary solution of a specific type.

    Simpler API when you just need a value of a certain type
    without a full function context.

    Args:
        expected_type: The type of value to generate
        error: The error that triggered the hallucination
        context: Optional context about what was being attempted
        runtime: Optional ClaudeCLIRuntime instance
        mode: Pataphysics mode

    Returns:
        An imaginary value of the expected type

    Example:
        # When API fails, generate plausible response
        try:
            data = await fetch_user_data(user_id)
        except APIError as e:
            data = await void_hallucinate_with_type(
                expected_type=dict,
                error=e,
                context=f"Fetching user data for {user_id}",
            )
    """

    # Create a dummy function with the right return type annotation
    def _dummy() -> Any:
        pass

    _dummy.__annotations__["return"] = expected_type
    _dummy.__name__ = f"generate_{expected_type.__name__}"
    _dummy.__doc__ = context or f"Generate a plausible {expected_type.__name__}"

    return await void_hallucinate(
        func=_dummy,
        error=error,
        args=(),
        kwargs={},
        runtime=runtime,
        mode=mode,
    )


# === Exports ===


__all__ = [
    "PataphysicsAgent",
    "PataphysicsMode",
    "PataphysicsResult",
    "PataphysicsSolverConfig",
    "create_pataphysics_solver",
    "pataphysics_solver_with_postcondition",
    # AGENTESE integration (v2.5)
    "void_hallucinate",
    "void_hallucinate_with_type",
]
