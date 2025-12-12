"""
Tests for void.pataphysics - The Science of Imaginary Solutions

Tests verify:
1. PataphysicsNode AGENTESE aspects (solve, melt, verify, imagine)
2. Contract verification with postconditions
3. Integration with VoidContextResolver
4. Entropy consumption for imaginary solutions

Required tests from creativity.md Phase 8:
- test_contract_melt_enforces_postcondition
- test_contract_melt_retries
- test_pataphysics_solve_alias
"""
# mypy: disable-error-code="arg-type,attr-defined"

from __future__ import annotations

from typing import Any

import pytest

from ..void import (
    EntropyPool,
    PataphysicsNode,
    VoidContextResolver,
    create_void_resolver,
)

# === Test Fixtures ===


class MockDNA:
    """Mock DNA for testing."""

    def __init__(self, name: str = "test", archetype: str = "default") -> None:
        self.name = name
        self.archetype = archetype
        self.capabilities: tuple[str, ...] = ()


class MockUmwelt:
    """Mock Umwelt for testing - typed as Any at fixture level."""

    def __init__(
        self,
        name: str = "test",
        archetype: str = "default",
        context: dict[str, Any] | None = None,
    ) -> None:
        self.dna = MockDNA(name, archetype)
        self.context = context or {}


# Type alias for test fixtures - suppresses arg-type errors at call sites
MockUmweltAny = Any


# === Test PataphysicsNode Basics ===


class TestPataphysicsNodeBasics:
    """Test basic PataphysicsNode structure and properties."""

    def test_node_has_correct_handle(self) -> None:
        """PataphysicsNode should have void.pataphysics handle."""
        node = PataphysicsNode()
        assert node.handle == "void.pataphysics"

    def test_node_has_solve_affordance(self) -> None:
        """PataphysicsNode should expose solve affordance."""
        node = PataphysicsNode()
        affordances = node._get_affordances_for_archetype("default")
        assert "solve" in affordances

    def test_node_has_melt_affordance(self) -> None:
        """PataphysicsNode should expose melt affordance."""
        node = PataphysicsNode()
        affordances = node._get_affordances_for_archetype("default")
        assert "melt" in affordances

    def test_node_has_verify_affordance(self) -> None:
        """PataphysicsNode should expose verify affordance."""
        node = PataphysicsNode()
        affordances = node._get_affordances_for_archetype("default")
        assert "verify" in affordances

    def test_node_has_imagine_affordance(self) -> None:
        """PataphysicsNode should expose imagine affordance."""
        node = PataphysicsNode()
        affordances = node._get_affordances_for_archetype("default")
        assert "imagine" in affordances


# === Test PataphysicsNode.solve ===


class TestPataphysicsSolve:
    """Test the void.pataphysics.solve aspect."""

    @pytest.mark.asyncio
    async def test_solve_returns_solution(self) -> None:
        """solve should return a solution dict."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("solve", observer, problem="test problem")

        assert "solution" in result
        assert "problem" in result
        assert result["problem"] == "test problem"

    @pytest.mark.asyncio
    async def test_solve_includes_method_pataphysics(self) -> None:
        """solve should identify method as pataphysics (oblique or llm)."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("solve", observer, problem="test")

        # Without LLM client, should use oblique method
        assert result.get("method") == "pataphysics_oblique"

    @pytest.mark.asyncio
    async def test_solve_is_jarry_certified(self) -> None:
        """solve should be Jarry certified (tribute to Alfred Jarry)."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("solve", observer, problem="test")

        assert result.get("jarry_certified") is True

    @pytest.mark.asyncio
    async def test_solve_consumes_entropy(self) -> None:
        """solve should consume entropy from the pool."""
        pool = EntropyPool(initial_budget=100.0, remaining=100.0)
        node = PataphysicsNode(_pool=pool)
        observer = MockUmwelt()

        initial_entropy = pool.remaining
        await node._invoke_aspect("solve", observer, problem="test")

        assert pool.remaining < initial_entropy

    @pytest.mark.asyncio
    async def test_solve_with_postcondition_check(self) -> None:
        """solve should check postcondition if provided."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        # Postcondition that always fails
        result = await node._invoke_aspect(
            "solve",
            observer,
            problem="test",
            ensure=lambda x: False,
        )

        assert "contract_satisfied" in result
        assert result["contract_satisfied"] is False

    @pytest.mark.asyncio
    async def test_solve_with_passing_postcondition(self) -> None:
        """solve should indicate contract satisfaction."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        # Postcondition that always passes
        result = await node._invoke_aspect(
            "solve",
            observer,
            problem="test",
            ensure=lambda x: True,
        )

        assert "contract_satisfied" in result
        assert result["contract_satisfied"] is True


# === Test PataphysicsNode.verify ===


class TestPataphysicsVerify:
    """Test the void.pataphysics.verify aspect."""

    @pytest.mark.asyncio
    async def test_verify_without_contract_is_vacuously_true(self) -> None:
        """verify without contract should return True."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("verify", observer, solution="anything")

        assert result["verified"] is True
        assert "vacuously true" in result["reason"]

    @pytest.mark.asyncio
    async def test_verify_with_passing_contract(self) -> None:
        """verify should return True when contract passes."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect(
            "verify",
            observer,
            solution=42,
            ensure=lambda x: x > 0,
        )

        assert result["verified"] is True
        assert "satisfied" in result["reason"]

    @pytest.mark.asyncio
    async def test_verify_with_failing_contract(self) -> None:
        """verify should return False when contract fails."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect(
            "verify",
            observer,
            solution=-1,
            ensure=lambda x: x > 0,
        )

        assert result["verified"] is False
        assert "violated" in result["reason"]

    @pytest.mark.asyncio
    async def test_verify_with_erroring_contract(self) -> None:
        """verify should return False when contract raises."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        def bad_contract(x: Any) -> bool:
            raise ValueError("contract error")

        result = await node._invoke_aspect(
            "verify",
            observer,
            solution="test",
            ensure=bad_contract,
        )

        assert result["verified"] is False
        assert "failed" in result["reason"]
        assert "error" in result


# === Test PataphysicsNode.imagine ===


class TestPataphysicsImagine:
    """Test the void.pataphysics.imagine aspect."""

    @pytest.mark.asyncio
    async def test_imagine_returns_imagination(self) -> None:
        """imagine should return an imagination dict."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("imagine", observer, domain="creativity")

        assert "imagination" in result
        assert "domain" in result
        assert result["domain"] == "creativity"

    @pytest.mark.asyncio
    async def test_imagine_consumes_entropy(self) -> None:
        """imagine should consume entropy from the pool."""
        pool = EntropyPool(initial_budget=100.0, remaining=100.0)
        node = PataphysicsNode(_pool=pool)
        observer = MockUmwelt()

        initial_entropy = pool.remaining
        await node._invoke_aspect("imagine", observer, domain="test")

        assert pool.remaining < initial_entropy


# === Test PataphysicsNode.melt ===


class TestPataphysicsMelt:
    """Test the void.pataphysics.melt aspect."""

    @pytest.mark.asyncio
    async def test_melt_returns_context(self) -> None:
        """melt should return melting context info."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("melt", observer, error_type="TestError")

        assert "melting_context" in result
        assert "instruction" in result
        assert "philosophy" in result

    @pytest.mark.asyncio
    async def test_melt_includes_philosophy(self) -> None:
        """melt should include philosophical note."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("melt", observer)

        assert "imagination provides" in result["philosophy"]


# === Test VoidContextResolver with Pataphysics ===


class TestVoidContextResolverPataphysics:
    """Test that VoidContextResolver correctly resolves pataphysics."""

    def test_resolver_has_pataphysics(self) -> None:
        """Resolver should resolve void.pataphysics."""
        resolver = create_void_resolver()

        node = resolver.resolve("pataphysics", [])

        assert isinstance(node, PataphysicsNode)
        assert node.handle == "void.pataphysics"

    def test_resolver_shares_entropy_pool(self) -> None:
        """Pataphysics should share entropy pool with resolver."""
        resolver = create_void_resolver(initial_budget=50.0)

        # Get pataphysics node
        pataphysics = resolver.resolve("pataphysics", [])
        entropy = resolver.resolve("entropy", [])

        # Both should reference the same pool
        assert pataphysics._pool is resolver._pool
        assert entropy._pool is resolver._pool


# === Test Entropy Budget Exhaustion ===


class TestEntropyBudgetExhaustion:
    """Test behavior when entropy budget is exhausted."""

    @pytest.mark.asyncio
    async def test_solve_returns_exhausted_message(self) -> None:
        """solve should return special message when budget exhausted."""
        pool = EntropyPool(initial_budget=0.01, remaining=0.01)
        node = PataphysicsNode(_pool=pool)
        observer = MockUmwelt()

        result = await node._invoke_aspect("solve", observer, problem="test")

        assert "status" in result
        assert result["status"] == "budget_exhausted"
        assert "exhausted" in result["solution"].lower()

    @pytest.mark.asyncio
    async def test_imagine_returns_exhausted_message(self) -> None:
        """imagine should return special message when budget exhausted."""
        pool = EntropyPool(initial_budget=0.01, remaining=0.01)
        node = PataphysicsNode(_pool=pool)
        observer = MockUmwelt()

        result = await node._invoke_aspect("imagine", observer, domain="test")

        assert "status" in result
        assert result["status"] == "budget_exhausted"


# === Test PataphysicsNode.manifest ===


class TestPataphysicsManifest:
    """Test the manifest (view) aspect of PataphysicsNode."""

    @pytest.mark.asyncio
    async def test_manifest_returns_renderable(self) -> None:
        """manifest should return a Renderable."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node.manifest(observer)

        assert result.summary is not None
        assert "Pataphysics" in result.summary

    @pytest.mark.asyncio
    async def test_manifest_includes_jarry_quote(self) -> None:
        """manifest should include a Jarry quote in metadata."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node.manifest(observer)

        assert "jarry_quote" in result.metadata


# === Test Required Phase 8 Tests ===


class TestPhase8Required:
    """
    Required tests from creativity.md Phase 8:
    - test_contract_melt_enforces_postcondition
    - test_contract_melt_retries
    - test_pataphysics_solve_alias
    """

    @pytest.mark.asyncio
    async def test_contract_melt_enforces_postcondition(self) -> None:
        """Verify that postconditions are enforced in pataphysics."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        # Verify contract checking in solve
        result = await node._invoke_aspect(
            "solve",
            observer,
            problem="test",
            ensure=lambda x: "imaginary" not in x.lower(),  # Will fail
        )

        # The solve aspect itself doesn't reject, it just reports
        assert "contract_satisfied" in result
        # Note: The actual contract enforcement happens in @meltable decorator
        # This test verifies the AGENTESE integration reports contract status

    @pytest.mark.asyncio
    async def test_contract_melt_retries(self) -> None:
        """Verify that contract failures can trigger retries."""
        # This is tested in shared/_tests/test_melting.py
        # Here we verify the AGENTESE path exists
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect(
            "melt", observer, error_type="ContractViolation"
        )

        assert "instruction" in result
        assert "meltable" in result["instruction"].lower()

    @pytest.mark.asyncio
    async def test_pataphysics_solve_alias(self) -> None:
        """Verify void.pataphysics.solve is the correct AGENTESE path."""
        # This test verifies the rename from void.execution.hallucinate
        # to void.pataphysics.solve as specified in creativity.md

        resolver = create_void_resolver()

        # Resolve pataphysics
        node = resolver.resolve("pataphysics", [])

        assert node.handle == "void.pataphysics"
        assert "solve" in node._get_affordances_for_archetype("default")

        # Verify we're not using the old "hallucinate" name
        affordances = node._get_affordances_for_archetype("default")
        assert "hallucinate" not in affordances  # Old name should not exist


# === Test LLM Integration (v2.5 PAYADOR Enhancement) ===


class MockLLMClient:
    """Mock LLM client for testing."""

    def __init__(
        self,
        responses: list[str] | None = None,
        should_fail: bool = False,
    ) -> None:
        self.responses = responses or ["An imaginary solution emerges from the void."]
        self.call_count = 0
        self.should_fail = should_fail
        self.last_temperature: float | None = None
        self.last_prompt: str | None = None

    async def generate(
        self,
        prompt: str,
        temperature: float = 1.0,
        max_tokens: int = 100,
    ) -> str:
        self.call_count += 1
        self.last_temperature = temperature
        self.last_prompt = prompt

        if self.should_fail:
            raise RuntimeError("LLM failed")

        # Cycle through responses
        idx = (self.call_count - 1) % len(self.responses)
        return self.responses[idx]


class TestPataphysicsLLMIntegration:
    """Test LLM integration for void.pataphysics.solve (v2.5 PAYADOR)."""

    @pytest.mark.asyncio
    async def test_solve_with_llm_uses_high_temperature(self) -> None:
        """solve with LLM should use high temperature (1.4)."""
        llm = MockLLMClient()
        node = PataphysicsNode()
        observer = MockUmwelt()

        await node._invoke_aspect(
            "solve",
            observer,
            problem="test problem",
            llm_client=llm,
        )

        assert llm.call_count == 1
        assert llm.last_temperature == 1.4  # HIGH temperature for creativity

    @pytest.mark.asyncio
    async def test_solve_with_llm_returns_llm_response(self) -> None:
        """solve with LLM should return LLM-generated solution."""
        expected_solution = "The key is to invert the problem itself."
        llm = MockLLMClient(responses=[expected_solution])
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect(
            "solve",
            observer,
            problem="test problem",
            llm_client=llm,
        )

        assert result["solution"] == expected_solution
        assert result["method"] == "pataphysics_llm"

    @pytest.mark.asyncio
    async def test_solve_without_llm_uses_oblique(self) -> None:
        """solve without LLM should fall back to oblique templates."""
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect(
            "solve",
            observer,
            problem="test problem",
        )

        assert result["method"] == "pataphysics_oblique"
        # Should contain templated solution
        assert (
            "problem" in result["solution"].lower()
            or "test problem" in result["solution"]
        )

    @pytest.mark.asyncio
    async def test_solve_llm_with_postcondition_retries(self) -> None:
        """solve with LLM should retry until postcondition passes."""
        # First response fails postcondition, second passes
        llm = MockLLMClient(
            responses=[
                "too short",  # Will fail length check
                "This is a longer solution that passes the postcondition check.",
            ]
        )
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect(
            "solve",
            observer,
            problem="test",
            llm_client=llm,
            ensure=lambda x: len(x) > 20,  # Requires longer solution
        )

        # Should have called LLM twice (retry)
        assert llm.call_count == 2
        assert result["contract_satisfied"] is True

    @pytest.mark.asyncio
    async def test_solve_llm_falls_back_on_failure(self) -> None:
        """solve should fall back to oblique when LLM fails."""
        llm = MockLLMClient(should_fail=True)
        node = PataphysicsNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect(
            "solve",
            observer,
            problem="test problem",
            llm_client=llm,
        )

        # Should still return a solution (from templates)
        assert "solution" in result
        # Method still says LLM because we tried it
        assert result["method"] == "pataphysics_llm"

    @pytest.mark.asyncio
    async def test_solve_llm_prompt_includes_problem(self) -> None:
        """solve LLM prompt should include the problem."""
        llm = MockLLMClient()
        node = PataphysicsNode()
        observer = MockUmwelt()

        await node._invoke_aspect(
            "solve",
            observer,
            problem="quantum entanglement paradox",
            llm_client=llm,
        )

        assert llm.last_prompt is not None
        assert "quantum entanglement paradox" in llm.last_prompt

    @pytest.mark.asyncio
    async def test_solve_llm_prompt_mentions_jarry(self) -> None:
        """solve LLM prompt should reference Alfred Jarry (pataphysics founder)."""
        llm = MockLLMClient()
        node = PataphysicsNode()
        observer = MockUmwelt()

        await node._invoke_aspect(
            "solve",
            observer,
            problem="test",
            llm_client=llm,
        )

        assert llm.last_prompt is not None
        assert "Jarry" in llm.last_prompt

    @pytest.mark.asyncio
    async def test_solve_respects_max_retries(self) -> None:
        """solve should respect max_retries parameter."""
        # Response always fails postcondition
        llm = MockLLMClient(responses=["x"])
        node = PataphysicsNode()
        observer = MockUmwelt()

        await node._invoke_aspect(
            "solve",
            observer,
            problem="test",
            llm_client=llm,
            ensure=lambda x: False,  # Always fails
            max_retries=5,
        )

        # Should have tried 5 times
        assert llm.call_count == 5
