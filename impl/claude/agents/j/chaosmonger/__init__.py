"""
Chaosmonger - AST-based stability analyzer for JIT-compiled code.

The Chaosmonger is the pre-Judge filter that handles computable safety:
- Import whitelist/blacklist checking
- Cyclomatic complexity analysis
- Branching factor estimation
- Unbounded recursion detection

See spec/j-gents/stability.md for the full specification.

## Package Structure

- `types.py` - Core types, configuration, risk scores
- `imports.py` - Import extraction and safety checking
- `complexity.py` - Complexity metrics (cyclomatic, branching, nesting, runtime)
- `recursion.py` - Unbounded recursion detection
- `analyzer.py` - Main analysis orchestrator

## Public API

Types:
- `StabilityConfig` - Configuration with thresholds
- `StabilityMetrics` - Quantitative measurements
- `StabilityInput` - Agent input
- `StabilityResult` - Agent output

Agent:
- `Chaosmonger` - Main agent implementation

Functions:
- `analyze_stability(code, budget, config)` - Core analysis
- `check_stability(code, budget, config)` - Convenience wrapper
- `is_stable(code, budget)` - Quick boolean check

Constants:
- `IMPORT_RISK` - Module risk scores
- `DEFAULT_CONFIG` - Default configuration
"""

from __future__ import annotations

from agents.poly.types import Agent

from .analyzer import analyze_stability
from .types import (
    DEFAULT_CONFIG,
    IMPORT_RISK,
    StabilityConfig,
    StabilityInput,
    StabilityMetrics,
    StabilityResult,
)


class Chaosmonger(Agent[StabilityInput, StabilityResult]):
    """
    Agent that performs AST-based stability analysis.

    The Chaosmonger is the pre-Judge filter that handles computable safety:
    - Chaosmonger: handles what CAN be computed (complexity, imports, recursion)
    - Judge: handles what CANNOT be computed (taste, ethics, joy)

    Pipeline:
        GeneratedCode → Chaosmonger → [stable?] → Judge → [accept?] → Execute
                             ↓                      ↓
                       [unstable]              [reject]
                             ↓                      ↓
                          Ground                 Ground
    """

    def __init__(self, config: StabilityConfig = DEFAULT_CONFIG):
        """
        Initialize the Chaosmonger.

        Args:
            config: Stability configuration (thresholds, allowed imports, etc.)
        """
        self._config = config

    @property
    def name(self) -> str:
        return "Chaosmonger"

    async def invoke(self, input: StabilityInput) -> StabilityResult:
        """
        Analyze source code for stability.

        Args:
            input: StabilityInput with source_code, entropy_budget, and config

        Returns:
            StabilityResult with is_stable, metrics, and violations
        """
        return analyze_stability(
            source_code=input.source_code,
            entropy_budget=input.entropy_budget,
            config=input.config,
        )


# Convenience Functions


def check_stability(
    source_code: str,
    entropy_budget: float = 1.0,
    config: StabilityConfig | None = None,
) -> StabilityResult:
    """
    Convenience function to check stability synchronously.

    Args:
        source_code: Python source to analyze
        entropy_budget: Available budget (default 1.0)
        config: Optional custom configuration

    Returns:
        StabilityResult with is_stable, metrics, and violations
    """
    return analyze_stability(
        source_code=source_code,
        entropy_budget=entropy_budget,
        config=config or DEFAULT_CONFIG,
    )


def is_stable(
    source_code: str,
    entropy_budget: float = 1.0,
) -> bool:
    """
    Quick check if code is stable.

    Args:
        source_code: Python source to analyze
        entropy_budget: Available budget (default 1.0)

    Returns:
        True if code passes all stability checks
    """
    result = check_stability(source_code, entropy_budget)
    return result.is_stable


# Public API exports
__all__ = [
    # Types
    "StabilityConfig",
    "StabilityMetrics",
    "StabilityInput",
    "StabilityResult",
    # Agent
    "Chaosmonger",
    # Functions
    "analyze_stability",
    "check_stability",
    "is_stable",
    # Constants
    "IMPORT_RISK",
    "DEFAULT_CONFIG",
]
