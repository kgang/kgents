"""
Tests for C-gent Contract Validator (Cross-pollination T2.8).

Tests contract law validation for F-gent synthesized contracts.
"""

from dataclasses import dataclass, field

from agents.c.contract_validator import (
    ContractLawViolation,
    ContractValidationReport,
    ContractValidator,
    suggest_contract_improvements,
    validate_composition_compatibility,
    validate_contract_laws,
)

# --- Mock Contract (matches F-gent Contract structure) ---


@dataclass
class MockInvariant:
    """Mock invariant for testing."""

    description: str
    property: str
    category: str


@dataclass
class MockCompositionRule:
    """Mock composition rule for testing."""

    mode: str
    description: str
    type_constraint: str = ""


@dataclass
class MockContract:
    """Mock contract for testing."""

    agent_name: str
    input_type: str
    output_type: str
    invariants: list[MockInvariant] = field(default_factory=list)
    composition_rules: list[MockCompositionRule] = field(default_factory=list)
    semantic_intent: str = ""


# --- Test: Type Compatibility ---


def test_type_compatibility_valid() -> None:
    """Test validation of valid type morphism."""
    contract = MockContract(
        agent_name="TestAgent",
        input_type="str",
        output_type="int",
    )

    validator = ContractValidator()
    report = validator.validate_contract(contract)

    assert report.passed is True
    assert "Type Morphism Existence" in report.laws_checked


def test_type_compatibility_missing_types() -> None:
    """Test detection of missing type definitions."""
    contract = MockContract(
        agent_name="TestAgent",
        input_type="",
        output_type="int",
    )

    validator = ContractValidator()
    report = validator.validate_contract(contract)

    assert report.passed is False
    assert any("Type Morphism" in v.law_name for v in report.violations)


def test_type_compatibility_degenerate() -> None:
    """Test warning for degenerate morphism (None → None)."""
    contract = MockContract(
        agent_name="TestAgent",
        input_type="None",
        output_type="None",
    )

    validator = ContractValidator()
    report = validator.validate_contract(contract)

    # Should have warning, not error
    assert report.warning_count > 0
    assert any("degenerate" in w.description.lower() for w in report.warnings)


# --- Test: Composition Laws ---


def test_composition_sequential_no_side_effects() -> None:
    """Test sequential composition without side effects."""
    contract = MockContract(
        agent_name="PureAgent",
        input_type="int",
        output_type="int",
        composition_rules=[
            MockCompositionRule(
                mode="sequential",
                description="Pure sequential composition",
            )
        ],
    )

    validator = ContractValidator()
    report = validator.validate_contract(contract)

    assert "Composition Associativity" in report.laws_checked


def test_composition_sequential_with_side_effects() -> None:
    """Test warning for sequential composition with side effects."""
    contract = MockContract(
        agent_name="StatefulAgent",
        input_type="int",
        output_type="int",
        invariants=[
            MockInvariant(
                description="Maintains internal state across invocations",
                property="state_preserved",
                category="behavioral",
            )
        ],
        composition_rules=[
            MockCompositionRule(
                mode="sequential",
                description="Sequential with state",
            )
        ],
    )

    validator = ContractValidator()
    report = validator.validate_contract(contract)

    # Should warn about associativity with state
    assert any("associative" in w.description.lower() for w in report.warnings)


def test_composition_no_rules_warning() -> None:
    """Test warning when no composition rules specified."""
    contract = MockContract(
        agent_name="NoRules",
        input_type="str",
        output_type="str",
        composition_rules=[],  # Empty
    )

    validator = ContractValidator()
    report = validator.validate_contract(contract)

    assert report.warning_count > 0


# --- Test: Invariant Laws ---


def test_identity_invariant_valid() -> None:
    """Test validation of identity invariant with matching types."""
    contract = MockContract(
        agent_name="IdentityAgent",
        input_type="str",
        output_type="str",
        invariants=[
            MockInvariant(
                description="Identity function",
                property="id",
                category="categorical",
            )
        ],
    )

    validator = ContractValidator()
    report = validator.validate_contract(contract)

    assert report.passed is True


def test_identity_invariant_invalid() -> None:
    """Test detection of invalid identity claim (type mismatch)."""
    contract = MockContract(
        agent_name="FakeIdentity",
        input_type="str",
        output_type="int",
        invariants=[
            MockInvariant(
                description="Claims to be identity but types differ",
                property="id",
                category="categorical",
            )
        ],
    )

    validator = ContractValidator()
    report = validator.validate_contract(contract)

    assert report.passed is False
    assert any("Identity Law" in v.law_name for v in report.violations)


def test_idempotence_invariant() -> None:
    """Test recognition of idempotence invariant."""
    contract = MockContract(
        agent_name="IdempotentAgent",
        input_type="str",
        output_type="str",
        invariants=[
            MockInvariant(
                description="Idempotent operation",
                property="f(f(x)) = f(x)",
                category="categorical",
            )
        ],
    )

    validator = ContractValidator()
    report = validator.validate_contract(contract)

    # Should pass without violations (idempotence is valid)
    assert "Invariant Consistency" in report.laws_checked


# --- Test: Functor Pattern ---


def test_functor_pattern_complete() -> None:
    """Test functor pattern with all required laws."""
    contract = MockContract(
        agent_name="MapAgent",
        input_type="List[A]",
        output_type="List[B]",
        composition_rules=[
            MockCompositionRule(
                mode="sequential",
                description="Map operation over lists",
            )
        ],
        invariants=[
            MockInvariant(
                description="Preserves identity",
                property="F(id) = id",
                category="categorical",
            ),
            MockInvariant(
                description="Preserves composition",
                property="F(g . f) = F(g) . F(f)",
                category="categorical",
            ),
        ],
    )

    validator = ContractValidator()
    report = validator.validate_contract(contract)

    assert report.passed is True
    assert "Functor Pattern" in report.laws_checked


def test_functor_pattern_missing_laws() -> None:
    """Test warning for functor pattern without required laws."""
    contract = MockContract(
        agent_name="IncompleteMap",
        input_type="List[A]",
        output_type="List[B]",
        composition_rules=[
            MockCompositionRule(
                mode="sequential",
                description="Map operation",
            )
        ],
        invariants=[],  # No functor law invariants
    )

    validator = ContractValidator()
    report = validator.validate_contract(contract)

    # Should have warnings about missing functor laws
    assert report.warning_count > 0
    assert any("Functor" in w.law_name for w in report.warnings)


# --- Test: Monad Pattern ---


def test_monad_pattern_complete() -> None:
    """Test monad pattern with all required laws."""
    contract = MockContract(
        agent_name="BindAgent",
        input_type="M[A]",
        output_type="M[B]",
        composition_rules=[
            MockCompositionRule(
                mode="sequential",
                description="Bind operation for monadic composition",
            )
        ],
        invariants=[
            MockInvariant(
                description="Left identity holds",
                property="unit(a).bind(f) = f(a)",
                category="categorical",
            ),
            MockInvariant(
                description="Right identity holds",
                property="m.bind(unit) = m",
                category="categorical",
            ),
            MockInvariant(
                description="Associativity holds",
                property="m.bind(f).bind(g) = m.bind(λa. f(a).bind(g))",
                category="categorical",
            ),
        ],
    )

    validator = ContractValidator()
    report = validator.validate_contract(contract)

    assert report.passed is True
    assert "Monad Pattern" in report.laws_checked


def test_monad_pattern_missing_laws() -> None:
    """Test warning for monad pattern without all laws."""
    contract = MockContract(
        agent_name="IncompleteBind",
        input_type="M[A]",
        output_type="M[B]",
        composition_rules=[
            MockCompositionRule(
                mode="sequential",
                description="Bind operation",
            )
        ],
        invariants=[
            MockInvariant(
                description="Left identity",
                property="unit(a).bind(f) = f(a)",
                category="categorical",
            )
            # Missing right identity and associativity
        ],
    )

    validator = ContractValidator()
    report = validator.validate_contract(contract)

    # Should warn about missing monad laws
    assert report.warning_count > 0
    monad_warnings = [w for w in report.warnings if "Monad" in w.law_name]
    assert len(monad_warnings) > 0


# --- Test: validate_contract_laws (convenience function) ---


def test_validate_contract_laws() -> None:
    """Test the convenience function for contract validation."""
    contract = MockContract(
        agent_name="SimpleAgent",
        input_type="str",
        output_type="int",
    )

    report = validate_contract_laws(contract)

    assert isinstance(report, ContractValidationReport)
    assert report.contract_name == "SimpleAgent"


# --- Test: validate_composition_compatibility ---


def test_composition_compatibility_valid() -> None:
    """Test composition compatibility for matching types."""
    contract1 = MockContract(
        agent_name="Agent1",
        input_type="str",
        output_type="int",
        composition_rules=[
            MockCompositionRule(mode="sequential", description="Sequential")
        ],
    )

    contract2 = MockContract(
        agent_name="Agent2",
        input_type="int",
        output_type="bool",
    )

    compatible, reason = validate_composition_compatibility(contract1, contract2)

    assert compatible is True
    assert "Compatible" in reason


def test_composition_compatibility_type_mismatch() -> None:
    """Test detection of type incompatibility."""
    contract1 = MockContract(
        agent_name="Agent1",
        input_type="str",
        output_type="int",
    )

    contract2 = MockContract(
        agent_name="Agent2",
        input_type="bool",  # Mismatch with contract1.output_type
        output_type="str",
    )

    compatible, reason = validate_composition_compatibility(contract1, contract2)

    assert compatible is False
    assert "Type mismatch" in reason


def test_composition_compatibility_fuzzy_match() -> None:
    """Test fuzzy type matching (str vs string)."""
    contract1 = MockContract(
        agent_name="Agent1",
        input_type="int",
        output_type="str",
    )

    contract2 = MockContract(
        agent_name="Agent2",
        input_type="string",  # Fuzzy match with "str"
        output_type="bool",
    )

    compatible, reason = validate_composition_compatibility(contract1, contract2)

    assert compatible is True


def test_composition_compatibility_no_sequential_rule() -> None:
    """Test detection when contract doesn't support sequential composition."""
    contract1 = MockContract(
        agent_name="Agent1",
        input_type="str",
        output_type="int",
        composition_rules=[
            MockCompositionRule(mode="parallel", description="Parallel only")
        ],
    )

    contract2 = MockContract(
        agent_name="Agent2",
        input_type="int",
        output_type="bool",
    )

    compatible, reason = validate_composition_compatibility(contract1, contract2)

    assert compatible is False
    assert "does not support sequential" in reason


# --- Test: suggest_contract_improvements ---


def test_suggest_improvements_functor() -> None:
    """Test improvement suggestions for functor pattern."""
    report = ContractValidationReport(
        contract_name="TestAgent",
        laws_checked=["Functor Pattern"],
        violations=[],
        warnings=[
            ContractLawViolation(
                law_name="Functor Identity Law",
                contract_name="TestAgent",
                description="Missing functor law",
                evidence="Test",
                severity="warning",
            )
        ],
        passed=True,
    )

    suggestions = suggest_contract_improvements(report)

    assert len(suggestions) > 0
    assert any("functor" in s.lower() for s in suggestions)
    assert any("F(id) = id" in s for s in suggestions)


def test_suggest_improvements_monad() -> None:
    """Test improvement suggestions for monad pattern."""
    report = ContractValidationReport(
        contract_name="TestAgent",
        laws_checked=["Monad Pattern"],
        violations=[],
        warnings=[
            ContractLawViolation(
                law_name="Monad Laws",
                contract_name="TestAgent",
                description="Missing monad laws",
                evidence="Test",
                severity="warning",
            )
        ],
        passed=True,
    )

    suggestions = suggest_contract_improvements(report)

    assert len(suggestions) > 0
    assert any("monad" in s.lower() for s in suggestions)


def test_suggest_improvements_type_error() -> None:
    """Test improvement suggestions for type errors."""
    report = ContractValidationReport(
        contract_name="TestAgent",
        laws_checked=["Type Morphism"],
        violations=[
            ContractLawViolation(
                law_name="Type Morphism Existence",
                contract_name="TestAgent",
                description="Missing types",
                evidence="Test",
            )
        ],
        warnings=[],
        passed=False,
    )

    suggestions = suggest_contract_improvements(report)

    assert len(suggestions) > 0
    assert any("type" in s.lower() for s in suggestions)


# --- Test: Report string representation ---


def test_contract_violation_str() -> None:
    """Test ContractLawViolation string representation."""
    violation = ContractLawViolation(
        law_name="Functor Identity",
        contract_name="MapAgent",
        description="F(id) not specified",
        evidence="No identity law invariant",
        severity="error",
    )

    str_rep = str(violation)
    assert "Functor Identity" in str_rep
    assert "MapAgent" in str_rep


def test_contract_report_str() -> None:
    """Test ContractValidationReport string representation."""
    report = ContractValidationReport(
        contract_name="TestAgent",
        laws_checked=["Type", "Composition"],
        violations=[],
        warnings=[],
        passed=True,
    )

    str_rep = str(report)
    assert "PASSED" in str_rep
    assert "TestAgent" in str_rep
