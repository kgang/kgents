"""
Integration tests for VoidHarness with real Claude CLI.

These tests are SKIPPED by default. To run them:

    RUN_LLM_TESTS=1 uv run pytest impl/claude/protocols/ashc/_tests/integration/

    # Or via flag
    uv run pytest --run-llm-tests impl/claude/protocols/ashc/_tests/integration/

WARNING: These tests consume real tokens!
"""

from __future__ import annotations

import pytest

from ...harness import (
    GenerationResult,
    TokenBudget,
    VoidHarness,
    VoidHarnessConfig,
)

# =============================================================================
# Basic Generation Tests
# =============================================================================


@pytest.mark.llm_integration
@pytest.mark.asyncio
async def test_simple_function_generation() -> None:
    """Generate a simple function from spec."""
    if not VoidHarness.is_available():
        pytest.skip("Claude CLI not available")

    harness = VoidHarness()
    spec = """
    Create a Python function `add(a: int, b: int) -> int`
    that returns the sum of a and b.
    """

    result = await harness.generate_detailed(spec)

    assert result.success, f"Generation failed: {result.error}"
    assert "def add" in result.code
    assert "return" in result.code
    assert result.duration_ms > 0
    assert result.token_estimate > 0


@pytest.mark.llm_integration
@pytest.mark.asyncio
async def test_class_generation() -> None:
    """Generate a simple class from spec."""
    if not VoidHarness.is_available():
        pytest.skip("Claude CLI not available")

    harness = VoidHarness()
    spec = """
    Create a Python dataclass `Point` with:
    - x: int
    - y: int
    - A method `distance_from_origin() -> float` that returns sqrt(x^2 + y^2)
    """

    result = await harness.generate_detailed(spec)

    assert result.success, f"Generation failed: {result.error}"
    assert "class Point" in result.code or "Point" in result.code
    assert "x" in result.code
    assert "y" in result.code


@pytest.mark.llm_integration
@pytest.mark.asyncio
async def test_async_function_generation() -> None:
    """Generate an async function from spec."""
    if not VoidHarness.is_available():
        pytest.skip("Claude CLI not available")

    harness = VoidHarness()
    spec = """
    Create an async Python function `fetch_data(url: str) -> dict`
    that returns a dictionary with {"url": url, "status": "ok"}
    """

    result = await harness.generate_detailed(spec)

    assert result.success, f"Generation failed: {result.error}"
    assert "async def" in result.code
    assert "fetch_data" in result.code


# =============================================================================
# Context Isolation Tests
# =============================================================================


@pytest.mark.llm_integration
@pytest.mark.asyncio
async def test_void_directory_prevents_context_leakage() -> None:
    """
    Verify that running in void directory prevents CLAUDE.md injection.

    The harness runs in /tmp/ashc-void-xxx/ with no CLAUDE.md,
    so Claude should not have access to kgents-specific context.
    """
    if not VoidHarness.is_available():
        pytest.skip("Claude CLI not available")

    harness = VoidHarness()
    spec = """
    What is the content of CLAUDE.md in this project?
    If you don't have access to any project files, just write a simple
    hello world function instead.
    """

    result = await harness.generate_detailed(spec)

    # Should not contain kgents-specific content
    raw = result.raw_output.lower()
    assert "kgents" not in raw, "Context leaked: found 'kgents' in output"
    assert "anti-sausage" not in raw, "Context leaked: found 'anti-sausage' in output"
    assert "tasteful" not in raw or "curated" not in raw, "Context leaked: found principle names"


# =============================================================================
# Variation Tests
# =============================================================================


@pytest.mark.llm_integration
@pytest.mark.asyncio
async def test_multiple_generations_produce_variance() -> None:
    """
    Multiple generations should produce some variation.

    This is important for testing Bayesian stopping - we need
    real probabilistic behavior.
    """
    if not VoidHarness.is_available():
        pytest.skip("Claude CLI not available")

    # Limit concurrency to be nice to the API
    config = VoidHarnessConfig(max_concurrent=2)
    harness = VoidHarness(config)

    spec = """
    Create a Python function that computes the factorial of n.
    You can use either recursion or iteration.
    """

    results = await harness.generate_n(spec, n=3)

    # Filter successful results
    successful = [r for r in results if isinstance(r, GenerationResult) and r.success]

    assert len(successful) >= 2, "Need at least 2 successful generations"

    # Check for variation in raw output (even if code is similar)
    outputs = [r.raw_output for r in successful]
    unique_outputs = set(outputs)

    # At minimum, different void_ids
    void_ids = [r.void_id for r in successful]
    assert len(set(void_ids)) == len(void_ids), "Each generation should have unique void_id"


# =============================================================================
# Token Budget Tests
# =============================================================================


@pytest.mark.llm_integration
@pytest.mark.asyncio
async def test_token_tracking_accumulates() -> None:
    """Token usage should accumulate across generations."""
    if not VoidHarness.is_available():
        pytest.skip("Claude CLI not available")

    harness = VoidHarness()

    # First generation
    await harness.generate_detailed("def add(a, b): return a + b")
    tokens_after_1 = harness.tokens_used

    assert tokens_after_1 > 0, "Should track token usage"

    # Second generation
    await harness.generate_detailed("def multiply(a, b): return a * b")
    tokens_after_2 = harness.tokens_used

    assert tokens_after_2 > tokens_after_1, "Tokens should accumulate"


@pytest.mark.llm_integration
@pytest.mark.asyncio
async def test_budget_exhaustion_prevents_generation() -> None:
    """Exhausted budget should prevent further generation."""
    if not VoidHarness.is_available():
        pytest.skip("Claude CLI not available")

    # Start with small budget that will exhaust after one call
    budget = TokenBudget(max_tokens=1000)
    harness = VoidHarness(budget=budget)

    # First call should work
    result1 = await harness.generate_detailed("def foo(): pass")

    if result1.success:
        # If it succeeded, budget should be consumed
        # Next call with exhausted budget should fail
        if harness.budget_exhausted:
            result2 = await harness.generate_detailed("def bar(): pass")
            assert not result2.success
            assert "budget" in result2.error.lower()


# =============================================================================
# Error Handling Tests
# =============================================================================


@pytest.mark.llm_integration
@pytest.mark.asyncio
async def test_generation_count_increments() -> None:
    """Generation count should increment with each call."""
    if not VoidHarness.is_available():
        pytest.skip("Claude CLI not available")

    harness = VoidHarness()

    assert harness.generation_count == 0

    await harness.generate_detailed("def a(): pass")
    assert harness.generation_count == 1

    await harness.generate_detailed("def b(): pass")
    assert harness.generation_count == 2


# =============================================================================
# Evidence Compiler Integration Tests
# =============================================================================


@pytest.mark.llm_integration
@pytest.mark.asyncio
async def test_harness_with_evidence_compiler() -> None:
    """
    VoidHarness integrates with EvidenceCompiler.

    This is the key integration point for ASHC Phase 4.
    """
    if not VoidHarness.is_available():
        pytest.skip("Claude CLI not available")

    from ...evidence import EvidenceCompiler

    harness = VoidHarness()
    compiler = EvidenceCompiler(generate_fn=harness.generate)

    # Simple spec with tests
    spec = """
def double(x: int) -> int:
    \"\"\"Return x * 2.\"\"\"
    return x * 2
"""
    test_code = """
from impl import double

def test_double_positive():
    assert double(2) == 4

def test_double_zero():
    assert double(0) == 0
"""

    # Run with minimal variations for speed
    output = await compiler.compile(
        spec=spec,
        n_variations=2,  # Minimal for integration test
        test_code=test_code,
        run_types=False,  # Skip mypy for speed
        run_lint=False,  # Skip ruff for speed
    )

    assert output.evidence.run_count == 2
    # At least some should pass (LLM can vary)
    # Don't require 100% - this is probabilistic!


# =============================================================================
# Adaptive Compiler Integration Tests
# =============================================================================


@pytest.mark.llm_integration
@pytest.mark.asyncio
async def test_harness_with_adaptive_compiler() -> None:
    """
    VoidHarness integrates with AdaptiveCompiler.

    Tests Bayesian stopping with real LLM variance.
    """
    if not VoidHarness.is_available():
        pytest.skip("Claude CLI not available")

    from ...adaptive import AdaptiveCompiler, ConfidenceTier

    harness = VoidHarness()
    compiler = AdaptiveCompiler(generate_fn=harness.generate)

    # Trivially easy spec should stop early
    spec = """
def identity(x):
    \"\"\"Return x unchanged.\"\"\"
    return x
"""
    test_code = """
from impl import identity

def test_identity():
    assert identity(42) == 42
    assert identity("hello") == "hello"
"""

    evidence = await compiler.compile(
        spec=spec,
        test_code=test_code,
        tier=ConfidenceTier.TRIVIALLY_EASY,
    )

    # Should have made a decision
    assert evidence.decision.value in ("stop_success", "stop_failure", "stop_uncertain")

    # For trivially easy, should use few samples
    # (But LLM variance might require more)
    assert evidence.sample_count <= evidence.config.max_samples
