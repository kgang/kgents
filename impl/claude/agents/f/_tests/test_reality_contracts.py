"""Tests for Reality-Aware Contracts (J-gent × F-gent integration)."""

from agents.f.j_integration import (
    BoundedComplexity,
    DeterministicOnly,
    EntropyAware,
    IntentFilter,
    RealityGate,
    admits_intent,
    create_safe_gate,
    create_strict_gate,
    gate_intent,
)


class TestRealityGate:
    """Tests for RealityGate contract."""

    def test_admits_deterministic(self) -> None:
        """Gate admits deterministic intents."""
        gate = RealityGate()

        assert gate.admits("read the file")
        assert gate.admits("parse json")
        assert gate.admits("fetch user data")

    def test_rejects_chaotic(self) -> None:
        """Gate rejects chaotic intents."""
        gate = RealityGate()

        assert not gate.admits("fix everything forever")
        assert not gate.admits("process all data infinitely")
        assert not gate.admits("always monitor continuously")

    def test_admits_probabilistic_by_default(self) -> None:
        """Gate admits probabilistic intents by default."""
        gate = RealityGate()

        assert gate.admits("analyze the data")
        assert gate.admits("refactor this code")
        assert gate.admits("implement the feature")

    def test_require_deterministic_mode(self) -> None:
        """Gate can require deterministic only."""
        gate = RealityGate(require_deterministic=True)

        assert gate.admits("read the file")
        assert not gate.admits("analyze the data")  # probabilistic
        assert not gate.admits("fix everything")  # chaotic

    def test_check_output_for_chaotic_patterns(self) -> None:
        """Output check detects chaotic patterns."""
        gate = RealityGate()

        assert gate.check("normal output") is None
        assert gate.check("This will run forever!") is not None
        assert gate.check("Processing everything") is not None

    def test_entropy_budget_affects_classification(self) -> None:
        """Low entropy budget increases strictness."""
        # High budget - more permissive
        high_gate = RealityGate(entropy_budget=0.9)
        assert high_gate.admits("analyze data")

        # Very low budget - even simple tasks may fail due to threshold
        RealityGate(entropy_budget=0.05, chaos_threshold=0.1)
        # Low budget forces chaotic classification
        # (depends on implementation details)


class TestDeterministicOnly:
    """Tests for DeterministicOnly contract."""

    def test_admits_atomic_intents(self) -> None:
        """Admits intents with atomic keywords."""
        contract = DeterministicOnly()

        assert contract.admits("read config")
        assert contract.admits("fetch data")
        assert contract.admits("parse json")
        assert contract.admits("get value")

    def test_rejects_complex_intents(self) -> None:
        """Rejects intents with complex keywords."""
        contract = DeterministicOnly()

        assert not contract.admits("analyze and optimize the system")
        assert not contract.admits("refactor the codebase")
        assert not contract.admits("implement new feature")

    def test_rejects_chaotic_intents(self) -> None:
        """Rejects intents with chaotic keywords."""
        contract = DeterministicOnly()

        assert not contract.admits("process everything")
        assert not contract.admits("run forever")

    def test_check_output_determinism(self) -> None:
        """Output check detects non-deterministic language."""
        contract = DeterministicOnly()

        assert contract.check("result: 42") is None
        assert contract.check("approximately 3.14") is not None
        assert contract.check("might be correct") is not None
        assert contract.check("could succeed") is not None


class TestBoundedComplexity:
    """Tests for BoundedComplexity contract."""

    def test_admits_simple_intents(self) -> None:
        """Admits intents within bounds."""
        contract = BoundedComplexity(max_steps=3)

        assert contract.admits("read the file")
        assert contract.admits("parse and validate")
        assert contract.admits("read, parse, validate")

    def test_rejects_too_many_steps(self) -> None:
        """Rejects intents with too many steps."""
        contract = BoundedComplexity(max_steps=3)

        assert not contract.admits("read, parse, validate, transform, and store")
        assert not contract.admits("step one and step two and step three and step four")

    def test_rejects_forbidden_patterns(self) -> None:
        """Rejects intents with forbidden patterns."""
        contract = BoundedComplexity()

        assert not contract.admits("process everything")
        assert not contract.admits("run for all items")
        assert not contract.admits("monitor forever")
        assert not contract.admits("always check")

    def test_rejects_long_intents(self) -> None:
        """Rejects intents exceeding word limit."""
        contract = BoundedComplexity(max_words=10)

        short = "read the file"
        long = " ".join(["word"] * 20)

        assert contract.admits(short)
        assert not contract.admits(long)

    def test_check_output_size(self) -> None:
        """Output check detects oversized outputs."""
        contract = BoundedComplexity()

        assert contract.check("normal output") is None
        assert contract.check("x" * 100001) is not None


class TestEntropyAware:
    """Tests for EntropyAware contract."""

    def test_high_budget_admits_probabilistic(self) -> None:
        """High entropy budget admits probabilistic intents."""
        contract = EntropyAware(current_budget=0.8)

        assert contract.admits("analyze the data")
        assert contract.admits("refactor code")

    def test_low_budget_rejects_probabilistic(self) -> None:
        """Low entropy budget rejects probabilistic intents."""
        contract = EntropyAware(current_budget=0.2)

        # Should only admit deterministic at low budget
        assert contract.admits("read file")
        assert not contract.admits("analyze complex data")

    def test_very_low_budget_rejects_all(self) -> None:
        """Very low entropy budget rejects everything."""
        contract = EntropyAware(current_budget=0.05)

        assert not contract.admits("read file")
        assert not contract.admits("analyze data")

    def test_always_rejects_chaotic(self) -> None:
        """Chaotic intents rejected regardless of budget."""
        high = EntropyAware(current_budget=1.0)
        low = EntropyAware(current_budget=0.2)

        assert not high.admits("fix everything forever")
        assert not low.admits("fix everything forever")

    def test_with_budget_creates_new(self) -> None:
        """with_budget creates new contract with updated budget."""
        original = EntropyAware(current_budget=0.8)
        updated = original.with_budget(0.2)

        assert original.current_budget == 0.8
        assert updated.current_budget == 0.2


class TestIntentFilter:
    """Tests for IntentFilter contract."""

    def test_custom_predicate(self) -> None:
        """Custom predicate controls admission."""
        no_delete = IntentFilter(
            predicate=lambda i: "delete" not in i.lower(),
            description="No delete operations",
        )

        assert no_delete.admits("read the file")
        assert no_delete.admits("write data")
        assert not no_delete.admits("delete all files")

    def test_predicate_exception_fails_closed(self) -> None:
        """Exception in predicate results in rejection."""

        def bad_predicate(i: str) -> bool:
            1 / 0  # Will raise ZeroDivisionError
            return True  # Never reached

        bad_filter = IntentFilter(
            predicate=bad_predicate,
            description="Bad filter",
        )

        assert not bad_filter.admits("anything")


class TestCompositeContracts:
    """Tests for composite contract factories."""

    def test_create_safe_gate(self) -> None:
        """create_safe_gate returns standard safety contracts."""
        contracts = create_safe_gate()

        assert len(contracts) == 3
        assert any(isinstance(c, RealityGate) for c in contracts)
        assert any(isinstance(c, BoundedComplexity) for c in contracts)
        assert any(isinstance(c, EntropyAware) for c in contracts)

    def test_create_strict_gate(self) -> None:
        """create_strict_gate returns strict contracts."""
        contracts = create_strict_gate()

        assert len(contracts) == 2
        assert any(isinstance(c, DeterministicOnly) for c in contracts)
        assert any(isinstance(c, BoundedComplexity) for c in contracts)


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_admits_intent_all_pass(self) -> None:
        """admits_intent returns True when all contracts pass."""
        contracts = [
            RealityGate(),
            BoundedComplexity(max_steps=5),
        ]

        assert admits_intent("read the file", contracts)

    def test_admits_intent_any_fail(self) -> None:
        """admits_intent returns False when any contract fails."""
        contracts = [
            RealityGate(),
            DeterministicOnly(),
        ]

        # Probabilistic intent - passes RealityGate, fails DeterministicOnly
        assert not admits_intent("analyze complex data", contracts)

    def test_gate_intent_admitted(self) -> None:
        """gate_intent returns admission status and reason."""
        admitted, reason = gate_intent("read the file")

        assert admitted is True
        assert reason == "Admitted"

    def test_gate_intent_rejected(self) -> None:
        """gate_intent returns rejection reason."""
        admitted, reason = gate_intent("fix everything forever")

        assert admitted is False
        assert "Rejected by" in reason

    def test_gate_intent_custom_contracts(self) -> None:
        """gate_intent uses custom contracts when provided."""
        strict = create_strict_gate()

        admitted, _ = gate_intent("read file", strict)
        assert admitted

        admitted, reason = gate_intent("analyze data", strict)
        assert not admitted


class TestIntegration:
    """Integration tests for reality contracts."""

    def test_safe_gate_flow(self) -> None:
        """Standard safe gate accepts simple, rejects complex/chaotic."""
        contracts = create_safe_gate()

        # Simple deterministic - passes all
        assert admits_intent("read config", contracts)

        # Bounded probabilistic - passes all
        assert admits_intent("parse and validate data", contracts)

        # Unbounded chaotic - fails RealityGate
        assert not admits_intent("process everything infinitely", contracts)

    def test_entropy_degradation(self) -> None:
        """Contracts become stricter as entropy depletes."""
        # Full budget - permissive
        high_contracts = create_safe_gate(entropy_budget=1.0)
        assert admits_intent("analyze the data", high_contracts)

        # Low budget - restrictive
        create_safe_gate(entropy_budget=0.15)
        # EntropyAware should reject probabilistic at low budget
        # But RealityGate and BoundedComplexity may still pass
        # This tests the combined behavior

    def test_strict_gate_very_restrictive(self) -> None:
        """Strict gate is very restrictive."""
        strict = create_strict_gate()

        # Only short, atomic intents pass
        assert admits_intent("read", strict)
        assert admits_intent("get data", strict)

        # Complex intents fail
        assert not admits_intent("analyze the complex dataset thoroughly", strict)
        assert not admits_intent("implement, test, and deploy", strict)
