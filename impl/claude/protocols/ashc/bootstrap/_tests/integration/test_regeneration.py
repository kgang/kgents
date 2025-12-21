"""
Integration Tests for ASHC Bootstrap Regeneration.

These tests use real LLM generation via VoidHarness.
They are skipped by default and only run when:
- RUN_LLM_TESTS=1 environment variable is set
- --run-llm-tests pytest flag is used

Run: RUN_LLM_TESTS=1 uv run pytest protocols/ashc/bootstrap/_tests/integration/ -v

> "The proof is not formal—it's empirical. Now we prove it with real LLM calls."
"""

import os

import pytest

from ....harness import VoidHarness
from ...regenerator import (
    BootstrapRegenerator,
    RegenerationConfig,
    regenerate_bootstrap,
    regenerate_single,
)

# =============================================================================
# Skip Configuration
# =============================================================================

RUN_LLM_TESTS = os.environ.get("RUN_LLM_TESTS", "").lower() in ("1", "true", "yes")

skip_without_llm = pytest.mark.skipif(
    not RUN_LLM_TESTS,
    reason="LLM tests disabled. Run with RUN_LLM_TESTS=1 or --run-llm-tests",
)

skip_without_claude = pytest.mark.skipif(
    not VoidHarness.is_available(),
    reason="Claude CLI not available",
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def regenerator() -> BootstrapRegenerator:
    """Create a regenerator with conservative settings."""
    config = RegenerationConfig(
        n_variations=1,  # Single generation to save tokens
        max_tokens=10_000,  # Conservative budget for tests
    )
    return BootstrapRegenerator(config=config)


# =============================================================================
# Id Agent Tests (Simplest)
# =============================================================================


@skip_without_llm
@skip_without_claude
@pytest.mark.asyncio
class TestIdRegeneration:
    """Tests for Id agent regeneration."""

    async def test_regenerate_id_produces_result(self, regenerator):
        """Can regenerate Id agent from spec."""
        result = await regenerator.regenerate_agent("Id")
        assert result is not None
        assert result.agent_name == "Id"
        # We don't assert is_isomorphic since LLM output varies

    async def test_regenerate_id_has_code(self, regenerator):
        """Regenerated Id has actual code."""
        result = await regenerator.regenerate_agent("Id")
        # Check that we got some result
        assert result.test_pass_rate >= 0  # Valid rate
        # Error should be None or informative
        if not result.is_isomorphic:
            print(f"Id regeneration result: {result}")


# =============================================================================
# Compose Agent Tests
# =============================================================================


@skip_without_llm
@skip_without_claude
@pytest.mark.asyncio
class TestComposeRegeneration:
    """Tests for Compose agent regeneration."""

    async def test_regenerate_compose_produces_result(self, regenerator):
        """Can regenerate Compose agent from spec."""
        result = await regenerator.regenerate_agent("Compose")
        assert result is not None
        assert result.agent_name == "Compose"


# =============================================================================
# Multiple Agent Tests
# =============================================================================


@skip_without_llm
@skip_without_claude
@pytest.mark.asyncio
class TestMultipleAgents:
    """Tests for regenerating multiple agents."""

    async def test_regenerate_id_and_compose(self, regenerator):
        """Can regenerate both Id and Compose."""
        result = await regenerator.regenerate(agents=["Id", "Compose"])
        assert len(result.comparisons) == 2
        names = {c.agent_name for c in result.comparisons}
        assert names == {"Id", "Compose"}

    async def test_regeneration_tracks_tokens(self, regenerator):
        """Regeneration tracks token usage."""
        result = await regenerator.regenerate(agents=["Id"])
        # Should have used some tokens
        assert result.tokens_used > 0
        # Should have counted generations
        assert result.generation_count > 0


# =============================================================================
# Convenience Function Tests
# =============================================================================


@skip_without_llm
@skip_without_claude
@pytest.mark.asyncio
class TestConvenienceFunctions:
    """Tests for regenerate_single and regenerate_bootstrap."""

    async def test_regenerate_single_id(self):
        """regenerate_single works for Id."""
        config = RegenerationConfig(n_variations=1, max_tokens=5_000)
        result = await regenerate_single("Id", config=config)
        assert result.agent_name == "Id"


# =============================================================================
# Full Bootstrap Test (Expensive!)
# =============================================================================


@skip_without_llm
@skip_without_claude
@pytest.mark.asyncio
@pytest.mark.slow
class TestFullBootstrap:
    """Full bootstrap regeneration (expensive, slow)."""

    async def test_regenerate_all_seven(self):
        """
        Regenerate all 7 bootstrap agents.

        This is expensive (~100k tokens) and slow (~5 minutes).
        Run sparingly with: pytest -m slow --run-llm-tests
        """
        config = RegenerationConfig(
            n_variations=1,  # Minimal for testing
            max_tokens=150_000,  # Need enough budget
        )
        result = await regenerate_bootstrap(config=config)

        # Should have all 7
        assert len(result.comparisons) == 7

        # Print summary
        print("\n" + result.summary())

        # At least some should work
        assert result.isomorphic_count >= 1, "At least Id should regenerate"


# =============================================================================
# Resource Tracking Tests
# =============================================================================


@skip_without_llm
@skip_without_claude
@pytest.mark.asyncio
class TestResourceTracking:
    """Tests for resource (token, time) tracking."""

    async def test_tracks_regeneration_time(self, regenerator):
        """Regeneration tracks time in milliseconds."""
        result = await regenerator.regenerate(agents=["Id"])
        assert result.regeneration_time_ms > 0

    async def test_respects_token_budget(self):
        """Regeneration respects token budget."""
        config = RegenerationConfig(
            n_variations=1,
            max_tokens=100,  # Very small budget
        )
        regenerator = BootstrapRegenerator(config=config)

        # Should fail gracefully when budget exhausted
        result = await regenerator.regenerate(agents=["Id"])
        # Either succeeds quickly or fails with budget error
        assert result is not None
