"""
Main stability analysis orchestrator.

Coordinates all sub-analyzers to produce a comprehensive stability result.
"""

from __future__ import annotations

import ast

from .complexity import (
    calculate_cyclomatic_complexity,
    calculate_max_nesting,
    count_functions,
    estimate_branching_factor,
    estimate_runtime,
)
from .imports import check_imports, extract_imports
from .recursion import has_unbounded_recursion
from .types import (
    DEFAULT_CONFIG,
    StabilityConfig,
    StabilityMetrics,
    StabilityResult,
)


def analyze_stability(
    source_code: str,
    entropy_budget: float,
    config: StabilityConfig = DEFAULT_CONFIG,
) -> StabilityResult:
    """
    Analyze Python source code for stability.

    Applies checks in order:
    1. Import whitelist/blacklist
    2. Cyclomatic complexity
    3. Branching factor
    4. Unbounded recursion

    Args:
        source_code: Python source to analyze
        entropy_budget: Available budget (0.0-1.0)
        config: Stability configuration

    Returns:
        StabilityResult with is_stable, metrics, and violations
    """
    violations: list[str] = []

    # Try to parse the source
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return StabilityResult(
            is_stable=False,
            metrics=StabilityMetrics(
                cyclomatic_complexity=0,
                branching_factor=0,
                import_risk=0.0,
                has_unbounded_recursion=False,
                estimated_runtime="unknown",
                import_count=0,
                function_count=0,
                max_nesting_depth=0,
            ),
            violations=(f"Syntax error: {e}",),
        )

    # Extract imports
    imports = extract_imports(tree)

    # Check 1: Import safety
    import_safe, import_risk, import_violations = check_imports(imports, config, entropy_budget)
    violations.extend(import_violations)

    # Check 2: Cyclomatic complexity
    complexity = calculate_cyclomatic_complexity(tree)
    complexity_threshold = int(entropy_budget * config.max_cyclomatic_complexity)
    if complexity > complexity_threshold:
        violations.append(
            f"Cyclomatic complexity ({complexity}) exceeds threshold ({complexity_threshold})"
        )

    # Check 3: Branching factor
    branching = estimate_branching_factor(tree)
    branching_threshold = int(entropy_budget * config.max_branching_factor)
    if branching > branching_threshold and branching > 1:
        violations.append(
            f"Branching factor ({branching}) exceeds threshold ({branching_threshold})"
        )

    # Check 4: Unbounded recursion
    has_unbounded = has_unbounded_recursion(tree)
    if has_unbounded:
        violations.append("Unbounded recursion detected")

    # Calculate additional metrics
    runtime = estimate_runtime(tree)
    function_count = count_functions(tree)
    max_nesting = calculate_max_nesting(tree)

    metrics = StabilityMetrics(
        cyclomatic_complexity=complexity,
        branching_factor=branching,
        import_risk=import_risk,
        has_unbounded_recursion=has_unbounded,
        estimated_runtime=runtime,
        import_count=len(imports),
        function_count=function_count,
        max_nesting_depth=max_nesting,
    )

    return StabilityResult(
        is_stable=len(violations) == 0,
        metrics=metrics,
        violations=tuple(violations),
    )
