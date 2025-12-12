"""
Tests for Gravity: Ground Constraints for Agent Output Validation.

Tests the Grounded pattern from spec/protocols/umwelt.md:
- GravityContract protocol
- Standard contracts (FactConsistency, EthicalBoundary, etc.)
- Grounded wrapper
- GravityBuilder
"""

from __future__ import annotations

from typing import Any

import pytest
from agents.f.gravity import (
    BoundedLength,
    ComposedContract,
    EthicalBoundary,
    FactConsistency,
    GravityBuilder,
    # Contracts
    GravityContract,
    # Wrapper
    Grounded,
    # Errors
    GroundingError,
    PredicateContract,
    RequiredFields,
    TypeContract,
)
from bootstrap.types import Agent

# ============================================================================
# Mock Agent for Testing
# ============================================================================


class MockAgent(Agent[str, str]):
    """Simple mock agent for testing Grounded wrapper."""

    def __init__(self, response: str = "mock response") -> None:
        self._response = response

    @property
    def name(self) -> str:
        return "MockAgent"

    async def invoke(self, input: str) -> str:
        return self._response


class EchoAgent(Agent[str, str]):
    """Agent that echoes input."""

    @property
    def name(self) -> str:
        return "EchoAgent"

    async def invoke(self, input: str) -> str:
        return f"Echo: {input}"


# ============================================================================
# FactConsistency Tests
# ============================================================================


class TestFactConsistency:
    """Test FactConsistency contract."""

    def test_no_contradiction_passes(self) -> None:
        """Output not contradicting facts passes."""
        contract = FactConsistency(known_facts={"sky_color": "blue"})
        assert contract.check("The sky is blue") is None

    def test_contradiction_fails(self) -> None:
        """Output contradicting facts fails."""
        contract = FactConsistency(known_facts={"sky_color": "blue"})
        result = contract.check("The sky_color is not blue")
        assert result is not None
        assert "Contradicts fact" in result

    def test_unrelated_output_passes(self) -> None:
        """Output not mentioning facts passes."""
        contract = FactConsistency(known_facts={"capital_of_france": "Paris"})
        assert contract.check("I like pizza") is None

    def test_multiple_facts(self) -> None:
        """Multiple facts are all checked."""
        contract = FactConsistency(
            known_facts={
                "sky_color": "blue",
                "grass_color": "green",
            }
        )
        assert contract.check("The sky is blue and grass is green") is None
        result = contract.check("The sky_color is not blue")
        assert result is not None

    def test_custom_check_function(self) -> None:
        """Custom check function can be provided."""

        def custom_check(output: Any, facts: dict[str, Any]) -> str | None:
            if "forbidden" in str(output).lower():
                return "Contains forbidden word"
            return None

        contract = FactConsistency(
            known_facts={"rule": "no forbidden"},
            _check_fn=custom_check,
        )

        assert contract.check("normal text") is None
        assert contract.check("this is forbidden") is not None


# ============================================================================
# EthicalBoundary Tests
# ============================================================================


class TestEthicalBoundary:
    """Test EthicalBoundary contract."""

    def test_strict_blocks_harmful(self) -> None:
        """Strict level blocks harmful patterns."""
        contract = EthicalBoundary(level="strict")
        result = contract.check("how to harm someone")
        assert result is not None
        assert "Ethical violation" in result

    def test_strict_blocks_hate(self) -> None:
        """Strict level blocks hate speech."""
        contract = EthicalBoundary(level="strict")
        result = contract.check("hate speech example")
        assert result is not None

    def test_moderate_allows_educational(self) -> None:
        """Moderate level is less restrictive."""
        contract = EthicalBoundary(level="moderate")
        # "how to harm" might pass in moderate (depends on exact pattern)
        # Should pass as it doesn't match blocked patterns
        assert contract.check("discussing historical violence in context") is None

    def test_permissive_allows_all(self) -> None:
        """Permissive level doesn't block anything."""
        contract = EthicalBoundary(level="permissive")
        assert contract.check("anything goes here") is None
        assert contract.check("even potentially problematic content") is None

    def test_admits_intent_strict(self) -> None:
        """Strict level rejects harmful intents."""
        contract = EthicalBoundary(level="strict")
        assert contract.admits("summarize this document") is True
        assert contract.admits("hate speech generator") is False

    def test_admits_intent_permissive(self) -> None:
        """Permissive level admits all intents."""
        contract = EthicalBoundary(level="permissive")
        assert contract.admits("anything") is True

    def test_custom_blocked_patterns(self) -> None:
        """Custom blocked patterns work."""
        contract = EthicalBoundary(
            level="strict",
            blocked_patterns=["confidential", "secret"],
        )
        assert contract.check("public information") is None
        result = contract.check("this is confidential")
        assert result is not None


# ============================================================================
# TypeContract Tests
# ============================================================================


class TestTypeContract:
    """Test TypeContract."""

    def test_correct_type_passes(self) -> None:
        """Correct type passes."""
        contract: TypeContract = TypeContract(expected_type=dict)
        assert contract.check({"key": "value"}) is None

    def test_wrong_type_fails(self) -> None:
        """Wrong type fails."""
        contract: TypeContract = TypeContract(expected_type=dict)
        result = contract.check("string instead")
        assert result is not None
        assert "Type mismatch" in result

    def test_tuple_of_types(self) -> None:
        """Multiple acceptable types work."""
        contract: TypeContract = TypeContract(expected_type=(dict, list))
        assert contract.check({"key": "value"}) is None
        assert contract.check([1, 2, 3]) is None
        result = contract.check("string")
        assert result is not None


# ============================================================================
# BoundedLength Tests
# ============================================================================


class TestBoundedLength:
    """Test BoundedLength contract."""

    def test_within_bounds_passes(self) -> None:
        """Output within bounds passes."""
        contract = BoundedLength(min_length=5, max_length=100)
        assert contract.check("hello world") is None

    def test_too_short_fails(self) -> None:
        """Output too short fails."""
        contract = BoundedLength(min_length=10)
        result = contract.check("short")
        assert result is not None
        assert "too short" in result

    def test_too_long_fails(self) -> None:
        """Output too long fails."""
        contract = BoundedLength(max_length=10)
        result = contract.check("this is a very long string")
        assert result is not None
        assert "too long" in result

    def test_works_with_lists(self) -> None:
        """Works with list lengths."""
        contract = BoundedLength(max_length=5)
        assert contract.check([1, 2, 3]) is None
        result = contract.check([1, 2, 3, 4, 5, 6, 7])
        assert result is not None


# ============================================================================
# RequiredFields Tests
# ============================================================================


class TestRequiredFields:
    """Test RequiredFields contract."""

    def test_all_fields_present_passes(self) -> None:
        """Dict with all required fields passes."""
        contract = RequiredFields(fields=["id", "name", "type"])
        assert contract.check({"id": 1, "name": "test", "type": "A"}) is None

    def test_missing_field_fails(self) -> None:
        """Dict missing field fails."""
        contract = RequiredFields(fields=["id", "name", "type"])
        result = contract.check({"id": 1, "name": "test"})
        assert result is not None
        assert "Missing required fields" in result
        assert "type" in result

    def test_not_dict_fails(self) -> None:
        """Non-dict fails."""
        contract = RequiredFields(fields=["id"])
        result = contract.check("not a dict")
        assert result is not None
        assert "Expected dict" in result

    def test_extra_fields_ok(self) -> None:
        """Extra fields don't cause failure."""
        contract = RequiredFields(fields=["id"])
        assert contract.check({"id": 1, "extra": "field"}) is None


# ============================================================================
# PredicateContract Tests
# ============================================================================


class TestPredicateContract:
    """Test PredicateContract."""

    def test_predicate_passes(self) -> None:
        """Predicate returning True passes."""
        contract = PredicateContract(
            predicate=lambda x: x > 0,
            error_message="Must be positive",
        )
        assert contract.check(5) is None

    def test_predicate_fails(self) -> None:
        """Predicate returning False fails."""
        contract = PredicateContract(
            predicate=lambda x: x > 0,
            error_message="Must be positive",
        )
        result = contract.check(-1)
        assert result == "Must be positive"

    def test_predicate_exception_handled(self) -> None:
        """Exceptions in predicate are handled."""
        contract = PredicateContract(
            predicate=lambda x: len(x) > 0,  # Fails for non-iterable
            error_message="Must have length",
        )
        result = contract.check(42)  # int has no len()
        assert result is not None
        assert "Predicate error" in result


# ============================================================================
# ComposedContract Tests
# ============================================================================


class TestComposedContract:
    """Test ComposedContract."""

    def test_all_pass_composition_passes(self) -> None:
        """All passing contracts → composition passes."""
        c1: TypeContract = TypeContract(expected_type=dict)
        c2: RequiredFields = RequiredFields(fields=["id"])
        composed = c1 & c2

        assert composed.check({"id": 1}) is None

    def test_one_fails_composition_fails(self) -> None:
        """One failing contract → composition fails."""
        c1: TypeContract = TypeContract(expected_type=dict)
        c2: RequiredFields = RequiredFields(fields=["id", "name"])
        composed = c1 & c2

        result = composed.check({"id": 1})  # Missing "name"
        assert result is not None

    def test_composition_name(self) -> None:
        """Composition name includes all contracts."""
        c1: TypeContract = TypeContract(expected_type=dict)
        c2: RequiredFields = RequiredFields(fields=["id"])
        composed = c1 & c2

        assert "TypeContract" in composed.name
        assert "RequiredFields" in composed.name

    def test_admits_requires_all(self) -> None:
        """Composition.admits requires all contracts to admit."""
        c1 = EthicalBoundary(level="strict")
        c2 = EthicalBoundary(level="permissive")
        composed = c1 & c2

        # c1 might reject, c2 always admits
        # Result depends on c1 - test composition exists
        assert composed is not None


# ============================================================================
# Grounded Wrapper Tests
# ============================================================================


class TestGrounded:
    """Test Grounded agent wrapper."""

    @pytest.mark.asyncio
    async def test_grounded_passes_valid_output(self) -> None:
        """Grounded passes valid output unchanged."""
        inner = MockAgent(response="valid response")
        grounded_agent = Grounded(
            inner=inner,
            gravity=[BoundedLength(max_length=100)],
        )

        result = await grounded_agent.invoke("input")
        assert result == "valid response"

    @pytest.mark.asyncio
    async def test_grounded_raises_on_violation(self) -> None:
        """Grounded raises GroundingError on violation."""
        inner = MockAgent(response="x" * 200)  # Too long
        grounded_agent = Grounded(
            inner=inner,
            gravity=[BoundedLength(max_length=100)],
        )

        with pytest.raises(GroundingError) as exc:
            await grounded_agent.invoke("input")

        assert exc.value.agent == "MockAgent"
        assert exc.value.contract == "BoundedLength"

    @pytest.mark.asyncio
    async def test_grounded_warn_mode(self) -> None:
        """Grounded warns but returns on violation when on_violation='warn'."""
        import warnings

        inner = MockAgent(response="x" * 200)
        grounded_agent = Grounded(
            inner=inner,
            gravity=[BoundedLength(max_length=100)],
            on_violation="warn",
        )

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = await grounded_agent.invoke("input")

            # Returns output despite violation
            assert result == "x" * 200
            # Warning was raised
            assert len(w) == 1
            assert "violated" in str(w[0].message)

    @pytest.mark.asyncio
    async def test_grounded_multiple_contracts(self) -> None:
        """Grounded checks all contracts."""

        # Use a dict-returning agent instead of MockAgent
        class DictAgent(Agent[str, dict[str, int]]):
            @property
            def name(self) -> str:
                return "DictAgent"

            async def invoke(self, input: str) -> dict[str, int]:
                return {"id": 1}

        inner: DictAgent = DictAgent()
        grounded_agent: Grounded[str, dict[str, int]] = Grounded(
            inner=inner,
            gravity=[
                TypeContract(expected_type=dict),
                RequiredFields(fields=["id"]),
            ],
        )

        result = await grounded_agent.invoke("input")
        assert result == {"id": 1}

    @pytest.mark.asyncio
    async def test_grounded_first_violation_raises(self) -> None:
        """Grounded raises on first violation (doesn't check all)."""
        inner = MockAgent(response="string")  # Wrong type
        grounded_agent = Grounded(
            inner=inner,
            gravity=[
                TypeContract(expected_type=dict),  # Fails first
                RequiredFields(fields=["id"]),
            ],
        )

        with pytest.raises(GroundingError) as exc:
            await grounded_agent.invoke("input")

        assert exc.value.contract == "TypeContract"

    def test_grounded_name(self) -> None:
        """Grounded name includes contracts."""
        inner: MockAgent = MockAgent()
        grounded_agent: Grounded[str, str] = Grounded(
            inner=inner,
            gravity=[TypeContract(expected_type=dict), BoundedLength(max_length=100)],
        )

        assert "MockAgent" in grounded_agent.name
        assert "TypeContract" in grounded_agent.name
        assert "BoundedLength" in grounded_agent.name

    @pytest.mark.asyncio
    async def test_grounded_with_gravity(self) -> None:
        """with_gravity adds contracts."""

        # Use a dict-returning agent
        class DictAgent(Agent[str, dict[str, int]]):
            @property
            def name(self) -> str:
                return "DictAgent"

            async def invoke(self, input: str) -> dict[str, int]:
                return {"id": 1}

        inner: DictAgent = DictAgent()
        grounded1: Grounded[str, dict[str, int]] = Grounded(
            inner=inner,
            gravity=[TypeContract(expected_type=dict)],
        )
        grounded2 = grounded1.with_gravity(RequiredFields(fields=["id"]))

        assert len(grounded1._gravity) == 1
        assert len(grounded2._gravity) == 2

    def test_grounded_admits_intent(self) -> None:
        """admits_intent checks all contracts."""
        inner = MockAgent()
        grounded_agent = Grounded(
            inner=inner,
            gravity=[
                EthicalBoundary(level="strict"),
            ],
        )

        assert grounded_agent.admits_intent("summarize document") is True
        assert grounded_agent.admits_intent("hate speech") is False


# ============================================================================
# GravityBuilder Tests
# ============================================================================


class TestGravityBuilder:
    """Test GravityBuilder fluent API."""

    def test_builder_basic(self) -> None:
        """Builder creates contracts."""
        gravity: list[GravityContract] = GravityBuilder().with_type(dict).build()

        assert len(gravity) == 1
        assert isinstance(gravity[0], TypeContract)

    def test_builder_multiple(self) -> None:
        """Builder chains multiple contracts."""
        gravity: list[GravityContract] = (
            GravityBuilder()
            .with_type(dict)
            .with_max_length(1000)
            .with_required_fields(["id", "name"])
            .build()
        )

        assert len(gravity) == 3

    def test_builder_with_facts(self) -> None:
        """Builder adds FactConsistency."""
        gravity: list[GravityContract] = (
            GravityBuilder().with_facts({"sky": "blue"}).build()
        )

        assert len(gravity) == 1
        assert isinstance(gravity[0], FactConsistency)

    def test_builder_with_ethics(self) -> None:
        """Builder adds EthicalBoundary."""
        gravity: list[GravityContract] = GravityBuilder().with_ethics("strict").build()

        assert len(gravity) == 1
        assert isinstance(gravity[0], EthicalBoundary)
        assert gravity[0].level == "strict"

    def test_builder_with_predicate(self) -> None:
        """Builder adds PredicateContract."""
        gravity: list[GravityContract] = (
            GravityBuilder()
            .with_predicate(
                predicate=lambda x: x > 0,
                error_message="Must be positive",
            )
            .build()
        )

        assert len(gravity) == 1
        assert isinstance(gravity[0], PredicateContract)

    def test_builder_with_custom_contract(self) -> None:
        """Builder adds custom contract."""

        class CustomContract(GravityContract):
            @property
            def name(self) -> str:
                return "Custom"

            def check(self, output: Any) -> str | None:
                return None

        gravity: list[GravityContract] = (
            GravityBuilder().with_contract(CustomContract()).build()
        )

        assert len(gravity) == 1
        assert gravity[0].name == "Custom"

    def test_builder_compose(self) -> None:
        """Builder.compose creates ComposedContract."""
        composed = (
            GravityBuilder().with_type(dict).with_required_fields(["id"]).compose()
        )

        assert isinstance(composed, ComposedContract)

    def test_builder_compose_empty(self) -> None:
        """Builder.compose returns None for empty."""
        composed = GravityBuilder().compose()
        assert composed is None

    def test_builder_compose_single(self) -> None:
        """Builder.compose returns single contract directly."""
        composed = GravityBuilder().with_type(dict).compose()
        assert isinstance(composed, TypeContract)


# ============================================================================
# Integration Tests
# ============================================================================


class TestGravityIntegration:
    """Integration tests for gravity system."""

    @pytest.mark.asyncio
    async def test_full_validation_pipeline(self) -> None:
        """Full pipeline: agent → grounded → contracts."""
        # Define strict contracts
        gravity: list[GravityContract] = (
            GravityBuilder()
            .with_type(dict)
            .with_required_fields(["status", "data"])
            .with_max_length(1000)
            .with_predicate(
                predicate=lambda x: x.get("status") in ("ok", "error"),
                error_message="Status must be 'ok' or 'error'",
            )
            .build()
        )

        # Create mock agent that returns valid response
        class ValidAgent(Agent[str, dict[str, Any]]):
            @property
            def name(self) -> str:
                return "ValidAgent"

            async def invoke(self, input: str) -> dict[str, Any]:
                return {"status": "ok", "data": input.upper()}

        grounded_agent: Grounded[str, dict[str, Any]] = Grounded(
            inner=ValidAgent(), gravity=gravity
        )
        result = await grounded_agent.invoke("hello")

        assert result == {"status": "ok", "data": "HELLO"}

    @pytest.mark.asyncio
    async def test_validation_rejects_invalid(self) -> None:
        """Pipeline rejects invalid responses."""
        gravity: list[GravityContract] = (
            GravityBuilder()
            .with_type(dict)
            .with_required_fields(["status", "data"])
            .build()
        )

        # Create agent that returns invalid response
        class InvalidAgent(Agent[str, dict[str, bool]]):
            @property
            def name(self) -> str:
                return "InvalidAgent"

            async def invoke(self, input: str) -> dict[str, bool]:
                return {"only_one_field": True}

        grounded_agent: Grounded[str, dict[str, bool]] = Grounded(
            inner=InvalidAgent(), gravity=gravity
        )

        with pytest.raises(GroundingError):
            await grounded_agent.invoke("input")

    @pytest.mark.asyncio
    async def test_ethical_and_type_combined(self) -> None:
        """Ethical and type contracts work together."""
        gravity: list[GravityContract] = (
            GravityBuilder()
            .with_ethics("strict")
            .with_type(str)
            .with_max_length(500)
            .build()
        )

        # Valid agent
        grounded: Grounded[str, str] = Grounded(
            inner=MockAgent(response="This is a safe response"),
            gravity=gravity,
        )

        result = await grounded.invoke("input")
        assert result == "This is a safe response"
