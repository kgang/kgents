"""
Safety validation for JIT agents.

This module provides:
- validate_jit_safety: Pre-flight safety check before sandbox execution
"""

from __future__ import annotations

from ..chaosmonger import StabilityConfig, analyze_stability
from ..meta_architect import AgentSource, ArchitectConstraints


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
