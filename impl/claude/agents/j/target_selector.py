"""
Target Selection — Map (Reality, Context, Stability) → Projection Target.

The TargetSelector determines the appropriate projection target for an agent
based on:
1. Reality classification (DETERMINISTIC, PROBABILISTIC, CHAOTIC)
2. Context flags (interactive, production, etc.)
3. Stability analysis (Chaosmonger result)

KEY INSIGHT: CHAOTIC reality or unstable code FORCES WASM sandbox.
This is the zero-trust safety net.

See spec/services/foundry.md for the full specification.

## Default Mappings

| Reality         | Context           | Target  | Rationale                     |
|-----------------|-------------------|---------|-------------------------------|
| DETERMINISTIC   | any               | LOCAL   | Atomic, single-step → fast    |
| PROBABILISTIC   | interactive=True  | MARIMO  | Exploration → notebook        |
| PROBABILISTIC   | production=True   | K8S     | Scale → Kubernetes            |
| PROBABILISTIC   | else              | CLI     | Quick test → shell script     |
| CHAOTIC         | any               | WASM    | Untrusted → sandboxed browser |
| UNSTABLE        | any               | WASM    | Failed stability → sandboxed  |

Example:
    >>> from agents.j.reality import Reality, classify_sync
    >>> from agents.j.target_selector import select_target, Target
    >>>
    >>> reality = classify_sync("parse this JSON")
    >>> target = select_target(reality, {})
    >>> target
    Target.LOCAL
    >>>
    >>> # Chaotic reality forces WASM
    >>> reality = classify_sync("do everything forever")
    >>> target = select_target(reality, {})
    >>> target
    Target.WASM
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .chaosmonger import StabilityResult
from .reality import Reality


class Target(Enum):
    """Projection targets for agent compilation."""

    LOCAL = "local"  # In-process Python execution
    CLI = "cli"  # Executable shell script
    DOCKER = "docker"  # Container image
    K8S = "k8s"  # Kubernetes manifests
    WASM = "wasm"  # Browser WASM sandbox (Pyodide)
    MARIMO = "marimo"  # Interactive notebook cell


@dataclass(frozen=True)
class TargetSelectionInput:
    """Input to the TargetSelector."""

    reality: Reality
    context: dict[str, Any]
    stability: StabilityResult | None = None  # Optional Chaosmonger result


@dataclass(frozen=True)
class TargetSelectionOutput:
    """Output from the TargetSelector."""

    target: Target
    forced: bool  # True if safety constraint forced this target
    reason: str


def select_target(
    reality: Reality,
    context: dict[str, Any],
    stability: StabilityResult | None = None,
) -> Target:
    """
    Select the appropriate projection target.

    Args:
        reality: Reality classification (DETERMINISTIC, PROBABILISTIC, CHAOTIC)
        context: Context flags (interactive, production, etc.)
        stability: Optional Chaosmonger stability result

    Returns:
        The Target enum value

    Example:
        >>> select_target(Reality.DETERMINISTIC, {})
        Target.LOCAL
        >>> select_target(Reality.CHAOTIC, {})
        Target.WASM
    """
    result = select_target_with_reason(reality, context, stability)
    return result.target


def select_target_with_reason(
    reality: Reality,
    context: dict[str, Any],
    stability: StabilityResult | None = None,
) -> TargetSelectionOutput:
    """
    Select target with full reasoning.

    This is the core target selection logic. It implements the safety-first
    principle: CHAOTIC reality or unstable code ALWAYS goes to WASM sandbox.

    Args:
        reality: Reality classification
        context: Context flags
        stability: Optional Chaosmonger result

    Returns:
        TargetSelectionOutput with target, forced flag, and reason
    """
    # SAFETY FIRST: Check for forced WASM conditions

    # 1. Chaotic reality → WASM (unconditional)
    if reality == Reality.CHAOTIC:
        return TargetSelectionOutput(
            target=Target.WASM,
            forced=True,
            reason="CHAOTIC reality forces WASM sandbox for zero-trust execution",
        )

    # 2. Unstable code → WASM (Chaosmonger failed)
    if stability is not None and not stability.is_stable:
        violations = ", ".join(stability.violations[:3])  # First 3 violations
        return TargetSelectionOutput(
            target=Target.WASM,
            forced=True,
            reason=f"Unstable code forces WASM sandbox: {violations}",
        )

    # 3. Explicit target override (if provided and not violating safety)
    explicit_target = context.get("target")
    if explicit_target is not None:
        try:
            target = Target(explicit_target)
            # Allow override only if not trying to bypass sandbox for chaotic/unstable
            return TargetSelectionOutput(
                target=target,
                forced=False,
                reason=f"Explicit target override: {explicit_target}",
            )
        except ValueError:
            pass  # Invalid target string, fall through to defaults

    # 4. Reality-based selection for safe code

    if reality == Reality.DETERMINISTIC:
        # Atomic, bounded → fast in-process execution
        return TargetSelectionOutput(
            target=Target.LOCAL,
            forced=False,
            reason="DETERMINISTIC reality → LOCAL for fast in-process execution",
        )

    # Reality.PROBABILISTIC → context-dependent
    if context.get("interactive"):
        return TargetSelectionOutput(
            target=Target.MARIMO,
            forced=False,
            reason="PROBABILISTIC + interactive → MARIMO for exploration",
        )

    if context.get("production"):
        return TargetSelectionOutput(
            target=Target.K8S,
            forced=False,
            reason="PROBABILISTIC + production → K8S for scale",
        )

    if context.get("container"):
        return TargetSelectionOutput(
            target=Target.DOCKER,
            forced=False,
            reason="PROBABILISTIC + container → DOCKER for isolation",
        )

    # Default for PROBABILISTIC: CLI for quick testing
    return TargetSelectionOutput(
        target=Target.CLI,
        forced=False,
        reason="PROBABILISTIC → CLI for quick testing (default)",
    )


def is_sandbox_required(
    reality: Reality,
    stability: StabilityResult | None = None,
) -> bool:
    """
    Quick check if WASM sandbox is required.

    Args:
        reality: Reality classification
        stability: Optional Chaosmonger result

    Returns:
        True if WASM sandbox is forced

    Example:
        >>> is_sandbox_required(Reality.CHAOTIC)
        True
        >>> is_sandbox_required(Reality.DETERMINISTIC)
        False
    """
    if reality == Reality.CHAOTIC:
        return True
    if stability is not None and not stability.is_stable:
        return True
    return False


def recommend_target_for_code(
    source_code: str,
    intent: str,
    context: dict[str, Any] | None = None,
    entropy_budget: float = 1.0,
) -> TargetSelectionOutput:
    """
    Complete pipeline: analyze code and intent, recommend target.

    This is the convenience function that runs both RealityClassifier
    and Chaosmonger, then selects the appropriate target.

    Args:
        source_code: Python source to analyze
        intent: What the agent is supposed to do
        context: Optional context flags
        entropy_budget: Computation budget (0.0-1.0)

    Returns:
        TargetSelectionOutput with recommended target

    Example:
        >>> result = recommend_target_for_code(
        ...     source_code="def greet(name): return f'Hello {name}'",
        ...     intent="greet the user",
        ... )
        >>> result.target
        Target.LOCAL
    """
    from .chaosmonger import check_stability
    from .reality import classify_intent

    context = context or {}

    # Step 1: Classify reality
    classification = classify_intent(
        intent=intent,
        context=context,
        entropy_budget=entropy_budget,
    )

    # Step 2: Analyze stability (if code provided)
    stability = None
    if source_code.strip():
        stability = check_stability(source_code, entropy_budget)

    # Step 3: Select target
    return select_target_with_reason(
        reality=classification.reality,
        context=context,
        stability=stability,
    )


# Public API
__all__ = [
    "Target",
    "TargetSelectionInput",
    "TargetSelectionOutput",
    "select_target",
    "select_target_with_reason",
    "is_sandbox_required",
    "recommend_target_for_code",
]
