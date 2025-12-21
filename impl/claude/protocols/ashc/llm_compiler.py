"""
ASHC LLM Compiler: Wire VoidHarness to Evidence/Adaptive Compilers

Convenience functions for compiling specs with real LLM generation.
This enables testing the Bayesian stopping infrastructure with
genuinely probabilistic behavior.

Usage:
    # Fixed-N compilation
    output = await compile_with_llm(spec, n_variations=10, test_code=tests)

    # Adaptive Bayesian compilation
    evidence = await adaptive_compile_with_llm(spec, test_code=tests)

> "The Bayesian and predictive infrastructure must be tested with
>  truly probabilistic functors."
"""

from __future__ import annotations

from .adaptive import (
    AdaptiveCompiler,
    AdaptiveEvidence,
    ConfidenceTier,
)
from .causal_graph import CausalLearner
from .evidence import (
    ASHCOutput,
    EvidenceCompiler,
    Nudge,
)
from .harness import (
    TokenBudget,
    VoidHarness,
    VoidHarnessConfig,
)

# =============================================================================
# Fixed-N Compilation with LLM
# =============================================================================


async def compile_with_llm(
    spec: str,
    n_variations: int = 10,
    test_code: str | None = None,
    harness_config: VoidHarnessConfig | None = None,
    budget: TokenBudget | None = None,
    run_tests: bool = True,
    run_types: bool = True,
    run_lint: bool = True,
    timeout: float = 60.0,
) -> ASHCOutput:
    """
    Compile spec using real LLM generation.

    Generates n_variations implementations, verifies each with pytest/mypy/ruff,
    and accumulates into Evidence.

    Args:
        spec: The specification to compile
        n_variations: Number of implementations to generate
        test_code: Optional test code for pytest
        harness_config: Configuration for VoidHarness
        budget: Token budget for tracking/limiting usage
        run_tests: Whether to run pytest verification
        run_types: Whether to run mypy verification
        run_lint: Whether to run ruff verification
        timeout: Timeout per verification run

    Returns:
        ASHCOutput with best executable and accumulated evidence

    Example:
        >>> output = await compile_with_llm(
        ...     spec="def add(a: int, b: int) -> int: ...",
        ...     n_variations=10,
        ...     test_code="def test_add(): assert add(1, 2) == 3",
        ... )
        >>> print(f"Pass rate: {output.evidence.pass_rate:.0%}")
    """
    harness = VoidHarness(harness_config, budget)

    if not harness.is_available():
        raise RuntimeError(
            "Claude CLI not available. Install with: npm install -g @anthropic/claude"
        )

    compiler = EvidenceCompiler(generate_fn=harness.generate)

    return await compiler.compile(
        spec=spec,
        n_variations=n_variations,
        test_code=test_code,
        run_tests=run_tests,
        run_types=run_types,
        run_lint=run_lint,
        timeout=timeout,
    )


# =============================================================================
# Adaptive Bayesian Compilation with LLM
# =============================================================================


async def adaptive_compile_with_llm(
    spec: str,
    test_code: str | None = None,
    tier: ConfidenceTier = ConfidenceTier.UNCERTAIN,
    harness_config: VoidHarnessConfig | None = None,
    budget: TokenBudget | None = None,
) -> AdaptiveEvidence:
    """
    Compile spec with adaptive Bayesian stopping using real LLM.

    Uses the n_diff stopping technique to minimize samples while
    maintaining statistical confidence. This is the key test of
    whether Bayesian stopping actually saves tokens with genuine
    probabilistic behavior.

    Args:
        spec: The specification to compile
        test_code: Optional test code for pytest
        tier: Confidence tier (affects prior and stopping config)
        harness_config: Configuration for VoidHarness
        budget: Token budget for tracking/limiting usage

    Returns:
        AdaptiveEvidence with runs, posterior belief, and stopping decision

    Example:
        >>> evidence = await adaptive_compile_with_llm(
        ...     spec="def double(x): return x * 2",
        ...     tier=ConfidenceTier.TRIVIALLY_EASY,
        ... )
        >>> print(f"Stopped after {evidence.sample_count} samples")
        >>> print(f"Saved {evidence.savings_vs_fixed:.0%} vs fixed-N")
    """
    harness = VoidHarness(harness_config, budget)

    if not harness.is_available():
        raise RuntimeError(
            "Claude CLI not available. Install with: npm install -g @anthropic/claude"
        )

    compiler = AdaptiveCompiler(generate_fn=harness.generate)

    return await compiler.compile(
        spec=spec,
        test_code=test_code,
        tier=tier,
    )


# =============================================================================
# Compilation with Nudges (for Causal Learning)
# =============================================================================


async def compile_with_nudges(
    spec: str,
    nudges: list[Nudge],
    n_variations: int = 10,
    test_code: str | None = None,
    harness_config: VoidHarnessConfig | None = None,
    budget: TokenBudget | None = None,
) -> ASHCOutput:
    """
    Compile spec with tracked nudges for causal analysis.

    Each nudge modifies the spec. The resulting runs include
    the nudges for later causal graph learning.

    Args:
        spec: The specification to compile
        nudges: List of nudges to apply to the spec
        n_variations: Number of implementations to generate
        test_code: Optional test code for pytest
        harness_config: Configuration for VoidHarness
        budget: Token budget for tracking/limiting usage

    Returns:
        ASHCOutput with nudge-tagged runs

    Example:
        >>> nudge = Nudge(
        ...     location="docstring",
        ...     before="Returns the sum",
        ...     after="Returns the sum (must handle negative numbers)",
        ...     reason="Clarify edge case handling",
        ... )
        >>> output = await compile_with_nudges(spec, [nudge])
    """
    harness = VoidHarness(harness_config, budget)

    if not harness.is_available():
        raise RuntimeError(
            "Claude CLI not available. Install with: npm install -g @anthropic/claude"
        )

    compiler = EvidenceCompiler(generate_fn=harness.generate)

    return await compiler.compile_with_nudges(
        spec=spec,
        nudges=nudges,
        n_variations=n_variations,
        test_code=test_code,
    )


# =============================================================================
# Causal Learning from LLM Evidence
# =============================================================================


async def learn_causal_graph(
    specs_with_nudges: list[tuple[str, list[Nudge]]],
    test_code: str | None = None,
    n_per_spec: int = 5,
    harness_config: VoidHarnessConfig | None = None,
    budget: TokenBudget | None = None,
) -> CausalLearner:
    """
    Learn causal graph from real LLM evidence.

    Runs multiple specs with various nudges, accumulates evidence,
    and builds a causal graph of nudge -> outcome relationships.

    Args:
        specs_with_nudges: List of (spec, nudges) pairs to test
        test_code: Optional test code for pytest
        n_per_spec: Number of variations per spec
        harness_config: Configuration for VoidHarness
        budget: Token budget for tracking/limiting usage

    Returns:
        CausalLearner with populated causal graph

    Example:
        >>> learner = await learn_causal_graph([
        ...     (base_spec, []),  # Baseline
        ...     (base_spec, [clarity_nudge]),
        ...     (base_spec, [type_nudge]),
        ... ])
        >>> print(f"Learned {learner.graph.edge_count} causal edges")
    """
    learner = CausalLearner()

    for spec, nudges in specs_with_nudges:
        if nudges:
            output = await compile_with_nudges(
                spec=spec,
                nudges=nudges,
                n_variations=n_per_spec,
                test_code=test_code,
                harness_config=harness_config,
                budget=budget,
            )
        else:
            output = await compile_with_llm(
                spec=spec,
                n_variations=n_per_spec,
                test_code=test_code,
                harness_config=harness_config,
                budget=budget,
            )

        learner.observe_evidence(output.evidence)

    return learner


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Fixed-N compilation
    "compile_with_llm",
    # Adaptive Bayesian compilation
    "adaptive_compile_with_llm",
    # Nudge-based compilation
    "compile_with_nudges",
    # Causal learning
    "learn_causal_graph",
]
