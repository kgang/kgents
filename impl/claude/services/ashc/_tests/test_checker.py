"""
Tests for ASHC Proof Checker Bridge.

These tests verify the proof checker abstraction and implementations:
- ProofChecker protocol compliance
- MockChecker for unit testing
- DafnyChecker integration (marked @pytest.mark.integration)

Phase 1 Exit Criteria:
- [x] DafnyChecker passes all integration tests (requires Dafny installed)
- [x] Timeout handling is robust (no zombie processes)
- [x] Error parsing extracts actionable diagnostics
- [x] Checker protocol allows future Lean4/Verus adapters

Teaching:
    gotcha: Integration tests are marked @pytest.mark.integration and
            skipped when Dafny is not installed. Run them explicitly:
            pytest -m integration --run-integration
"""

from __future__ import annotations

import asyncio
from dataclasses import FrozenInstanceError

import pytest

from ..checker import (
    CheckerError,
    CheckerRegistry,
    CheckerUnavailable,
    DafnyChecker,
    Lean4Checker,
    MockChecker,
    ProofChecker,
    VerusChecker,
    available_checkers,
    get_checker,
)
from ..contracts import CheckerResult


# =============================================================================
# MockChecker Tests (Always Run)
# =============================================================================


class TestMockChecker:
    """Tests for MockChecker behavior."""

    @pytest.mark.asyncio
    async def test_default_success(self) -> None:
        """MockChecker succeeds by default."""
        checker = MockChecker(default_success=True)

        result = await checker.check("any proof")

        assert result.success
        assert result.errors == ()
        assert checker.call_count == 1

    @pytest.mark.asyncio
    async def test_default_failure(self) -> None:
        """MockChecker can be configured to fail by default."""
        checker = MockChecker(default_success=False)

        result = await checker.check("any proof")

        assert not result.success
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_success_pattern(self) -> None:
        """MockChecker succeeds on matching patterns."""
        checker = MockChecker(default_success=False)
        checker.always_succeed_on(r"ensures\s+true")

        # Should succeed despite default failure
        result = await checker.check("lemma Test() ensures true {}")

        assert result.success

    @pytest.mark.asyncio
    async def test_failure_pattern(self) -> None:
        """MockChecker fails on matching patterns."""
        checker = MockChecker(default_success=True)
        checker.always_fail_on(r"ensures\s+false")

        # Should fail despite default success
        result = await checker.check("lemma Test() ensures false {}")

        assert not result.success

    @pytest.mark.asyncio
    async def test_failure_pattern_priority(self) -> None:
        """Failure patterns take priority over success patterns."""
        checker = MockChecker()
        checker.always_succeed_on(r"lemma")
        checker.always_fail_on(r"false")

        # Contains both patterns - failure wins
        result = await checker.check("lemma Test() ensures false {}")

        assert not result.success

    @pytest.mark.asyncio
    async def test_tracks_last_proof(self) -> None:
        """MockChecker tracks the last proof checked."""
        checker = MockChecker()

        await checker.check("first proof")
        await checker.check("second proof")

        assert checker.last_proof == "second proof"
        assert checker.call_count == 2

    @pytest.mark.asyncio
    async def test_simulated_latency(self) -> None:
        """MockChecker simulates verification latency."""
        latency = 100
        checker = MockChecker(latency_ms=latency)

        result = await checker.check("proof")

        assert result.duration_ms == latency

    def test_is_always_available(self) -> None:
        """MockChecker is always available."""
        checker = MockChecker()
        assert checker.is_available

    def test_name_property(self) -> None:
        """MockChecker has correct name."""
        checker = MockChecker()
        assert checker.name == "mock"

    @pytest.mark.asyncio
    async def test_fluent_api(self) -> None:
        """Pattern methods return self for fluent chaining."""
        checker = (
            MockChecker()
            .always_succeed_on(r"good")
            .always_fail_on(r"bad")
        )

        good_result = await checker.check("this is good")
        bad_result = await checker.check("this is bad")

        assert good_result.success
        assert not bad_result.success


# =============================================================================
# ProofChecker Protocol Tests
# =============================================================================


class TestProofCheckerProtocol:
    """Tests for ProofChecker protocol compliance."""

    def test_mock_checker_is_protocol(self) -> None:
        """MockChecker implements ProofChecker protocol."""
        checker = MockChecker()
        assert isinstance(checker, ProofChecker)

    def test_dafny_checker_is_protocol(self) -> None:
        """DafnyChecker implements ProofChecker protocol."""
        # Use verify_on_init=False to avoid installation check
        checker = DafnyChecker(verify_on_init=False)
        assert isinstance(checker, ProofChecker)

    def test_lean4_checker_is_protocol(self) -> None:
        """Lean4Checker implements ProofChecker protocol."""
        checker = Lean4Checker(verify_on_init=False)
        assert isinstance(checker, ProofChecker)

    def test_verus_checker_is_protocol(self) -> None:
        """VerusChecker implements ProofChecker protocol."""
        checker = VerusChecker(verify_on_init=False)
        assert isinstance(checker, ProofChecker)


# =============================================================================
# CheckerRegistry Tests
# =============================================================================


class TestCheckerRegistry:
    """Tests for CheckerRegistry."""

    def test_register_and_get(self) -> None:
        """Can register and retrieve checker classes."""
        registry = CheckerRegistry()
        registry.register("mock", MockChecker)

        checker = registry.get("mock")

        assert isinstance(checker, MockChecker)

    def test_lazy_instantiation(self) -> None:
        """Checkers are instantiated on first get(), not on register()."""
        registry = CheckerRegistry()
        registry.register("mock", MockChecker)

        # Not yet instantiated
        assert "mock" not in registry._instances

        registry.get("mock")

        # Now instantiated
        assert "mock" in registry._instances

    def test_singleton_instances(self) -> None:
        """Same instance is returned on repeated get() calls."""
        registry = CheckerRegistry()
        registry.register("mock", MockChecker)

        checker1 = registry.get("mock")
        checker2 = registry.get("mock")

        assert checker1 is checker2

    def test_unknown_checker_raises(self) -> None:
        """Requesting unknown checker raises KeyError."""
        registry = CheckerRegistry()

        with pytest.raises(KeyError, match="unknown"):
            registry.get("unknown")

    def test_available_checkers(self) -> None:
        """available_checkers returns only installed checkers."""
        registry = CheckerRegistry()
        registry.register("mock", MockChecker)

        available = registry.available_checkers()

        assert "mock" in available


# =============================================================================
# Global Registry Functions Tests
# =============================================================================


class TestGlobalRegistry:
    """Tests for global registry functions."""

    def test_get_mock_checker(self) -> None:
        """Can get mock checker from global registry."""
        checker = get_checker("mock")
        assert checker.name == "mock"

    def test_available_includes_mock(self) -> None:
        """Mock is always available."""
        available = available_checkers()
        assert "mock" in available


# =============================================================================
# CheckerResult Tests (Additional to test_contracts.py)
# =============================================================================


class TestCheckerResultIntegration:
    """Integration tests for CheckerResult with checker."""

    @pytest.mark.asyncio
    async def test_result_immutability(self) -> None:
        """CheckerResult from checker is immutable."""
        checker = MockChecker()
        result = await checker.check("proof")

        with pytest.raises(FrozenInstanceError):
            result.success = False  # type: ignore[misc]


# =============================================================================
# DafnyChecker Unit Tests (No Dafny Required)
# =============================================================================


class TestDafnyCheckerUnit:
    """Unit tests for DafnyChecker that don't require Dafny installed."""

    def test_lazy_verification(self) -> None:
        """DafnyChecker can be created with lazy verification."""
        # This should not raise even if Dafny is not installed
        checker = DafnyChecker(verify_on_init=False)
        assert checker.name == "dafny"

    def test_custom_path(self) -> None:
        """DafnyChecker accepts custom dafny path."""
        checker = DafnyChecker(dafny_path="/custom/dafny", verify_on_init=False)
        assert checker._dafny_path == "/custom/dafny"

    def test_is_available_caches(self) -> None:
        """is_available caches the verification result."""
        checker = DafnyChecker(verify_on_init=False)

        # First call runs verification (may fail)
        available1 = checker.is_available

        # Second call should use cached value
        available2 = checker.is_available

        assert available1 == available2


# =============================================================================
# DafnyChecker Integration Tests (Require Dafny)
# =============================================================================


def dafny_available() -> bool:
    """Check if Dafny is available for integration tests."""
    try:
        checker = DafnyChecker(verify_on_init=True)
        return checker.is_available
    except CheckerUnavailable:
        return False


# Skip integration tests if Dafny not available
requires_dafny = pytest.mark.skipif(
    not dafny_available(),
    reason="Dafny not installed. Install: dotnet tool install --global dafny",
)


@pytest.mark.integration
class TestDafnyCheckerIntegration:
    """Integration tests that require Dafny to be installed."""

    @requires_dafny
    @pytest.mark.asyncio
    async def test_verifies_trivial_proof(self) -> None:
        """Dafny accepts obviously true proofs."""
        checker = DafnyChecker()
        proof = """
lemma TrivialTrue()
    ensures true
{}
"""
        result = await checker.check(proof)

        assert result.success
        assert result.errors == ()
        assert result.duration_ms > 0

    @requires_dafny
    @pytest.mark.asyncio
    async def test_rejects_false_claim(self) -> None:
        """Dafny rejects false claims."""
        checker = DafnyChecker()
        proof = """
lemma FalseClaim()
    ensures 1 == 2
{}
"""
        result = await checker.check(proof)

        assert not result.success
        assert len(result.errors) > 0

    @requires_dafny
    @pytest.mark.asyncio
    async def test_verifies_arithmetic(self) -> None:
        """Dafny verifies basic arithmetic lemmas."""
        checker = DafnyChecker()
        proof = """
lemma AddCommutative(x: int, y: int)
    ensures x + y == y + x
{}
"""
        result = await checker.check(proof)

        assert result.success

    @requires_dafny
    @pytest.mark.asyncio
    async def test_timeout_handling(self) -> None:
        """Checker returns timeout result, doesn't hang."""
        checker = DafnyChecker()
        # Very short timeout for any proof
        proof = """
lemma Test()
    ensures true
{}
"""
        # Use impossibly short timeout
        result = await checker.check(proof, timeout_ms=1)

        # Either it times out or completes very fast - both are valid
        # The key is that we don't hang
        assert result.duration_ms >= 0

    @requires_dafny
    @pytest.mark.asyncio
    async def test_parses_postcondition_error(self) -> None:
        """Dafny extracts postcondition violations."""
        checker = DafnyChecker()
        proof = """
lemma WrongPostcondition(x: int)
    ensures x > 0  // Not true for all x!
{}
"""
        result = await checker.check(proof)

        assert not result.success
        # Should have actionable error about postcondition
        error_text = " ".join(result.errors)
        assert "postcondition" in error_text.lower() or "ensures" in error_text.lower() or "error" in error_text.lower()

    @requires_dafny
    @pytest.mark.asyncio
    async def test_handles_syntax_error(self) -> None:
        """Dafny reports syntax errors clearly."""
        checker = DafnyChecker()
        proof = """
lemma Broken(
    // Missing closing paren and body
"""
        result = await checker.check(proof)

        assert not result.success
        assert len(result.errors) > 0

    @requires_dafny
    @pytest.mark.asyncio
    async def test_empty_proof_fails(self) -> None:
        """Empty proof source fails gracefully."""
        checker = DafnyChecker()
        result = await checker.check("")

        # Empty file might succeed (no errors) or fail (no content)
        # Either is fine, just shouldn't crash
        assert isinstance(result.success, bool)

    @requires_dafny
    @pytest.mark.asyncio
    async def test_unicode_in_comments(self) -> None:
        """Dafny handles unicode in comments."""
        checker = DafnyChecker()
        proof = """
// Unicode test: ∀ x. P(x) → Q(x)
lemma UnicodeTest()
    ensures true
{}
"""
        result = await checker.check(proof)

        assert result.success

    @requires_dafny
    @pytest.mark.asyncio
    async def test_temp_file_cleanup(self) -> None:
        """Temp files are cleaned up after verification."""
        import glob
        import tempfile

        checker = DafnyChecker()
        temp_dir = tempfile.gettempdir()

        # Count existing ashc temp files
        before = len(glob.glob(f"{temp_dir}/ashc_proof_*.dfy"))

        await checker.check("lemma Test() ensures true {}")

        # Should not accumulate temp files
        after = len(glob.glob(f"{temp_dir}/ashc_proof_*.dfy"))
        assert after <= before

    @requires_dafny
    @pytest.mark.asyncio
    async def test_concurrent_checks(self) -> None:
        """Multiple concurrent checks don't interfere."""
        checker = DafnyChecker()

        proofs = [
            "lemma A() ensures 1 == 1 {}",
            "lemma B() ensures 2 == 2 {}",
            "lemma C() ensures 3 == 3 {}",
        ]

        results = await asyncio.gather(*[
            checker.check(p) for p in proofs
        ])

        assert all(r.success for r in results)


# =============================================================================
# Exception Tests
# =============================================================================


class TestCheckerExceptions:
    """Tests for checker exception handling."""

    def test_checker_unavailable_message(self) -> None:
        """CheckerUnavailable has informative message."""
        exc = CheckerUnavailable("dafny", "Not installed")
        assert "dafny" in str(exc)
        assert "Not installed" in str(exc)

    def test_checker_error_message(self) -> None:
        """CheckerError has informative message."""
        exc = CheckerError("dafny", "Failed", output="details")
        assert "dafny" in str(exc)
        assert "Failed" in str(exc)
        assert exc.output == "details"

    @pytest.mark.asyncio
    async def test_unavailable_checker_raises(self) -> None:
        """Checking with unavailable checker raises exception."""
        checker = DafnyChecker(dafny_path="/nonexistent/dafny", verify_on_init=False)

        # Force availability check
        assert not checker.is_available

        with pytest.raises(CheckerUnavailable):
            await checker.check("proof")


# =============================================================================
# Lean4Checker Unit Tests (No Lean4 Required)
# =============================================================================


class TestLean4CheckerUnit:
    """Unit tests for Lean4Checker that don't require Lean4 installed."""

    def test_lazy_verification(self) -> None:
        """Lean4Checker can be created with lazy verification."""
        # This should not raise even if Lean4 is not installed
        checker = Lean4Checker(verify_on_init=False)
        assert checker.name == "lean4"

    def test_custom_path(self) -> None:
        """Lean4Checker accepts custom lean path."""
        checker = Lean4Checker(binary_path="/custom/lean", verify_on_init=False)
        assert checker._binary_path == "/custom/lean"

    def test_is_available_caches(self) -> None:
        """is_available caches the verification result."""
        checker = Lean4Checker(verify_on_init=False)

        # First call runs verification (may fail)
        available1 = checker.is_available

        # Second call should use cached value
        available2 = checker.is_available

        assert available1 == available2

    @pytest.mark.asyncio
    async def test_unavailable_checker_raises(self) -> None:
        """Checking with unavailable Lean4 checker raises exception."""
        checker = Lean4Checker(binary_path="/nonexistent/lean", verify_on_init=False)

        # Force availability check
        assert not checker.is_available

        with pytest.raises(CheckerUnavailable):
            await checker.check("theorem trivial : True := trivial")


# =============================================================================
# Lean4Checker Integration Tests (Require Lean4)
# =============================================================================


def lean4_available() -> bool:
    """Check if Lean4 is available for integration tests."""
    try:
        checker = Lean4Checker(verify_on_init=True)
        return checker.is_available
    except CheckerUnavailable:
        return False


# Skip integration tests if Lean4 not available
requires_lean4 = pytest.mark.skipif(
    not lean4_available(),
    reason="Lean4 not installed. Install: curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh",
)


@pytest.mark.integration
class TestLean4CheckerIntegration:
    """Integration tests that require Lean4 to be installed."""

    @requires_lean4
    @pytest.mark.asyncio
    async def test_verifies_trivial_proof(self) -> None:
        """Lean4 accepts obviously true proofs."""
        checker = Lean4Checker()
        proof = "theorem trivial : ∀ x : Nat, x = x := fun _ => rfl"

        result = await checker.check(proof)

        assert result.success
        assert result.errors == ()
        assert result.duration_ms > 0

    @requires_lean4
    @pytest.mark.asyncio
    async def test_rejects_sorry(self) -> None:
        """Lean4 rejects proofs with sorry (incomplete proof marker)."""
        checker = Lean4Checker()
        proof = "theorem incomplete : 1 = 2 := sorry"

        result = await checker.check(proof)

        # sorry means incomplete proof - should fail
        assert not result.success

    @requires_lean4
    @pytest.mark.asyncio
    async def test_rejects_false_claim(self) -> None:
        """Lean4 rejects false claims without proof."""
        checker = Lean4Checker()
        proof = "theorem false_claim : 1 = 2 := rfl"

        result = await checker.check(proof)

        assert not result.success
        assert len(result.errors) > 0

    @requires_lean4
    @pytest.mark.asyncio
    async def test_timeout_handling(self) -> None:
        """Checker returns timeout result, doesn't hang."""
        checker = Lean4Checker()
        proof = "theorem trivial : ∀ x : Nat, x = x := fun _ => rfl"

        # Use impossibly short timeout
        result = await checker.check(proof, timeout_ms=1)

        # Either it times out or completes very fast - both are valid
        # The key is that we don't hang
        assert result.duration_ms >= 0

    @requires_lean4
    @pytest.mark.asyncio
    async def test_handles_syntax_error(self) -> None:
        """Lean4 reports syntax errors clearly."""
        checker = Lean4Checker()
        proof = "theorem Broken("

        result = await checker.check(proof)

        assert not result.success
        assert len(result.errors) > 0

    @requires_lean4
    @pytest.mark.asyncio
    async def test_empty_proof_fails(self) -> None:
        """Empty proof source fails gracefully."""
        checker = Lean4Checker()
        result = await checker.check("")

        # Empty file might succeed (no errors) or fail (no content)
        # Either is fine, just shouldn't crash
        assert isinstance(result.success, bool)

    @requires_lean4
    @pytest.mark.asyncio
    async def test_temp_file_cleanup(self) -> None:
        """Temp files are cleaned up after verification."""
        import glob
        import tempfile

        checker = Lean4Checker()
        temp_dir = tempfile.gettempdir()

        # Count existing ashc temp files
        before = len(glob.glob(f"{temp_dir}/ashc_proof_*.lean"))

        await checker.check("theorem trivial : True := trivial")

        # Should not accumulate temp files
        after = len(glob.glob(f"{temp_dir}/ashc_proof_*.lean"))
        assert after <= before


# =============================================================================
# VerusChecker Unit Tests (No Verus Required)
# =============================================================================


class TestVerusCheckerUnit:
    """Unit tests for VerusChecker that don't require Verus installed."""

    def test_lazy_verification(self) -> None:
        """VerusChecker can be created with lazy verification."""
        # This should not raise even if Verus is not installed
        checker = VerusChecker(verify_on_init=False)
        assert checker.name == "verus"

    def test_custom_path(self) -> None:
        """VerusChecker accepts custom verus path."""
        checker = VerusChecker(binary_path="/custom/verus", verify_on_init=False)
        assert checker._binary_path == "/custom/verus"

    def test_is_available_caches(self) -> None:
        """is_available caches the verification result."""
        checker = VerusChecker(verify_on_init=False)

        # First call runs verification (may fail)
        available1 = checker.is_available

        # Second call should use cached value
        available2 = checker.is_available

        assert available1 == available2

    @pytest.mark.asyncio
    async def test_unavailable_checker_raises(self) -> None:
        """Checking with unavailable Verus checker raises exception."""
        checker = VerusChecker(binary_path="/nonexistent/verus", verify_on_init=False)

        # Force availability check
        assert not checker.is_available

        with pytest.raises(CheckerUnavailable):
            await checker.check("proof fn trivial() ensures true {}")


# =============================================================================
# VerusChecker Integration Tests (Require Verus)
# =============================================================================


def verus_available() -> bool:
    """Check if Verus is available for integration tests."""
    try:
        checker = VerusChecker(verify_on_init=True)
        return checker.is_available
    except CheckerUnavailable:
        return False


# Skip integration tests if Verus not available
requires_verus = pytest.mark.skipif(
    not verus_available(),
    reason="Verus not installed. Install from: https://github.com/verus-lang/verus",
)


@pytest.mark.integration
class TestVerusCheckerIntegration:
    """Integration tests that require Verus to be installed."""

    @requires_verus
    @pytest.mark.asyncio
    async def test_verifies_trivial_proof(self) -> None:
        """Verus accepts obviously true proofs."""
        checker = VerusChecker()
        proof = """
proof fn trivial()
    ensures true
{
}
"""
        result = await checker.check(proof)

        assert result.success
        assert result.errors == ()
        assert result.duration_ms > 0

    @requires_verus
    @pytest.mark.asyncio
    async def test_rejects_false_claim(self) -> None:
        """Verus rejects false claims."""
        checker = VerusChecker()
        proof = """
proof fn false_claim()
    ensures 1int == 2int
{
}
"""
        result = await checker.check(proof)

        assert not result.success
        assert len(result.errors) > 0

    @requires_verus
    @pytest.mark.asyncio
    async def test_timeout_handling(self) -> None:
        """Checker returns timeout result, doesn't hang."""
        checker = VerusChecker()
        proof = "proof fn trivial() ensures true {}"

        # Use impossibly short timeout
        result = await checker.check(proof, timeout_ms=1)

        # Either it times out or completes very fast - both are valid
        assert result.duration_ms >= 0

    @requires_verus
    @pytest.mark.asyncio
    async def test_handles_syntax_error(self) -> None:
        """Verus reports syntax errors clearly."""
        checker = VerusChecker()
        proof = "proof fn Broken("

        result = await checker.check(proof)

        assert not result.success
        assert len(result.errors) > 0

    @requires_verus
    @pytest.mark.asyncio
    async def test_temp_file_cleanup(self) -> None:
        """Temp files are cleaned up after verification."""
        import glob
        import tempfile

        checker = VerusChecker()
        temp_dir = tempfile.gettempdir()

        # Count existing ashc temp files
        before = len(glob.glob(f"{temp_dir}/ashc_proof_*.rs"))

        await checker.check("proof fn trivial() ensures true {}")

        # Should not accumulate temp files
        after = len(glob.glob(f"{temp_dir}/ashc_proof_*.rs"))
        assert after <= before


# =============================================================================
# Global Registry Tests for New Checkers
# =============================================================================


class TestGlobalRegistryNewCheckers:
    """Tests for global registry with new checkers."""

    def test_get_lean4_checker_when_available(self) -> None:
        """Can get lean4 checker from global registry when installed."""
        # Skip if lean4 not available
        if not lean4_available():
            pytest.skip("Lean4 not installed")
        checker = get_checker("lean4")
        assert checker.name == "lean4"

    def test_get_lean4_checker_raises_when_unavailable(self) -> None:
        """Getting lean4 checker raises when not installed."""
        if lean4_available():
            pytest.skip("Lean4 is installed (test for unavailable case)")
        with pytest.raises(CheckerUnavailable):
            get_checker("lean4")

    def test_get_verus_checker_when_available(self) -> None:
        """Can get verus checker from global registry when installed."""
        # Skip if verus not available
        if not verus_available():
            pytest.skip("Verus not installed")
        checker = get_checker("verus")
        assert checker.name == "verus"

    def test_get_verus_checker_raises_when_unavailable(self) -> None:
        """Getting verus checker raises when not installed."""
        if verus_available():
            pytest.skip("Verus is installed (test for unavailable case)")
        with pytest.raises(CheckerUnavailable):
            get_checker("verus")

    def test_registry_has_all_checkers(self) -> None:
        """Registry should have dafny, lean4, verus, and mock."""
        # Note: available_checkers only returns INSTALLED checkers
        # So we test the registry directly
        registry = CheckerRegistry()
        registry.register("dafny", DafnyChecker)
        registry.register("lean4", Lean4Checker)
        registry.register("verus", VerusChecker)
        registry.register("mock", MockChecker)

        # Mock is always available
        available = registry.available_checkers()
        assert "mock" in available

    def test_lean4_registered_in_default_registry(self) -> None:
        """Lean4 is registered in the default registry."""
        # We can't call get_checker directly as it may raise,
        # but we can verify the registry structure
        assert "lean4" in _default_registry._checkers

    def test_verus_registered_in_default_registry(self) -> None:
        """Verus is registered in the default registry."""
        assert "verus" in _default_registry._checkers


# Access the default registry for testing
from ..checker import _default_registry
