"""
Tests for G-gent core types.

Tests cover:
- Enum definitions (GrammarLevel, GrammarFormat)
- ParseResult and ExecutionResult
- ParserConfig and InterpreterConfig
- ConstraintProof
- DomainAnalysis
- Tongue dataclass (immutability, hashing, serialization)
"""

import json
import pytest
from agents.g.types import (
    GrammarLevel,
    GrammarFormat,
    ParseResult,
    ExecutionResult,
    ParserConfig,
    InterpreterConfig,
    ConstraintProof,
    CounterExample,
    DomainAnalysis,
    Example,
    Tongue,
)


# ============================================================================
# Enum Tests
# ============================================================================


def test_grammar_level_enum():
    """Test GrammarLevel enum values."""
    assert GrammarLevel.SCHEMA.value == "schema"
    assert GrammarLevel.COMMAND.value == "command"
    assert GrammarLevel.RECURSIVE.value == "recursive"


def test_grammar_format_enum():
    """Test GrammarFormat enum values."""
    assert GrammarFormat.PYDANTIC.value == "pydantic"
    assert GrammarFormat.BNF.value == "bnf"
    assert GrammarFormat.EBNF.value == "ebnf"
    assert GrammarFormat.LARK.value == "lark"


# ============================================================================
# Result Types Tests
# ============================================================================


def test_parse_result_success():
    """Test successful ParseResult."""
    result = ParseResult(success=True, ast={"type": "command"}, confidence=0.95)
    assert result.success
    assert result
    assert result.ast == {"type": "command"}
    assert result.confidence == 0.95
    assert result.error is None


def test_parse_result_failure():
    """Test failed ParseResult."""
    result = ParseResult(success=False, error="Syntax error at line 1")
    assert not result.success
    assert not result
    assert result.ast is None
    assert result.error == "Syntax error at line 1"


def test_execution_result_success():
    """Test successful ExecutionResult."""
    result = ExecutionResult(success=True, value=42, side_effects=["logged execution"])
    assert result.success
    assert result
    assert result.value == 42
    assert result.side_effects == ["logged execution"]


def test_execution_result_failure():
    """Test failed ExecutionResult."""
    result = ExecutionResult(success=False, error="Runtime error: division by zero")
    assert not result.success
    assert not result
    assert result.error == "Runtime error: division by zero"


# ============================================================================
# Config Tests
# ============================================================================


def test_parser_config_defaults():
    """Test ParserConfig with defaults."""
    config = ParserConfig(
        strategy="regex",
        grammar_format=GrammarFormat.BNF,
    )
    assert config.strategy == "regex"
    assert config.grammar_format == GrammarFormat.BNF
    assert config.confidence_threshold == 0.8
    assert config.repair_strategy == "fail"
    assert config.case_sensitive is True


def test_parser_config_validation():
    """Test ParserConfig validation."""
    with pytest.raises(ValueError, match="confidence_threshold must be in"):
        ParserConfig(
            strategy="lark",
            grammar_format=GrammarFormat.LARK,
            confidence_threshold=1.5,  # Invalid
        )


def test_interpreter_config_defaults():
    """Test InterpreterConfig with defaults."""
    config = InterpreterConfig(runtime="python")
    assert config.runtime == "python"
    assert config.semantics == {}
    assert config.pure_functions_only is False
    assert config.timeout_ms == 5000


def test_interpreter_config_validation():
    """Test InterpreterConfig validation."""
    with pytest.raises(ValueError, match="timeout_ms must be positive"):
        InterpreterConfig(
            runtime="sandboxed",
            timeout_ms=-100,  # Invalid
        )


# ============================================================================
# ConstraintProof Tests
# ============================================================================


def test_constraint_proof_structural():
    """Test structural constraint proof detection."""
    proof = ConstraintProof(
        constraint="No DELETE operations",
        mechanism="DELETE verb not in lexicon - grammatically impossible",
    )
    assert proof.is_structural()


def test_constraint_proof_non_structural():
    """Test non-structural constraint proof detection."""
    proof = ConstraintProof(
        constraint="No operations on Sundays",
        mechanism="Runtime check for day of week",
    )
    assert not proof.is_structural()


def test_constraint_proof_with_counter_examples():
    """Test constraint proof with counter examples."""
    proof = ConstraintProof(
        constraint="No DELETE operations",
        mechanism="DELETE verb not in lexicon",
        counter_examples=[
            CounterExample(
                text="DELETE meeting",
                expected_error="Verb 'DELETE' not found in lexicon",
                description="Attempt to delete should fail parsing",
            )
        ],
    )
    assert len(proof.counter_examples) == 1
    assert proof.counter_examples[0].text == "DELETE meeting"


# ============================================================================
# DomainAnalysis Tests
# ============================================================================


def test_domain_analysis_empty():
    """Test empty DomainAnalysis."""
    analysis = DomainAnalysis()
    assert analysis.entities == set()
    assert analysis.operations == set()
    assert analysis.constraints == []
    assert analysis.relationships == {}
    assert analysis.lexicon == set()


def test_domain_analysis_populated():
    """Test populated DomainAnalysis."""
    analysis = DomainAnalysis(
        entities={"Meeting", "Calendar"},
        operations={"CHECK", "ADD"},
        constraints=["No DELETE"],
        relationships={"Meeting": ["belongs_to", "Calendar"]},
        lexicon={"CHECK", "ADD", "Meeting", "Calendar"},
    )
    assert "Meeting" in analysis.entities
    assert "CHECK" in analysis.operations
    assert "No DELETE" in analysis.constraints
    assert analysis.relationships["Meeting"] == ["belongs_to", "Calendar"]


# ============================================================================
# Tongue Tests
# ============================================================================


@pytest.fixture
def sample_tongue():
    """Create a sample Tongue for testing."""
    grammar = 'CMD ::= "CHECK" Date | "ADD" Event'
    return Tongue(
        name="CalendarTongue",
        version="1.0.0",
        lexicon=frozenset(["CHECK", "ADD", "Date", "Event"]),
        grammar=grammar,
        mime_type="application/vnd.kgents.calendar",
        level=GrammarLevel.COMMAND,
        format=GrammarFormat.BNF,
        parser_config=ParserConfig(
            strategy="regex",
            grammar_format=GrammarFormat.BNF,
            grammar_spec=grammar,
        ),
        interpreter_config=InterpreterConfig(
            runtime="python",
            semantics="command",
        ),
        domain="Calendar Management",
        constraints=("No DELETE operations", "No overwrites"),
        examples=(
            Example("CHECK 2024-12-15"),
            Example("ADD 14:00 1h Meeting"),
        ),
        constraint_proofs=(
            ConstraintProof(
                constraint="No DELETE operations",
                mechanism="DELETE verb not in grammar",
            ),
        ),
        validated=True,
    )


def test_tongue_immutability(sample_tongue):
    """Test that Tongue is immutable (frozen)."""
    with pytest.raises(Exception):  # FrozenInstanceError
        sample_tongue.name = "NewName"


def test_tongue_hashable(sample_tongue):
    """Test that Tongue is hashable."""
    hash_value = hash(sample_tongue)
    assert isinstance(hash_value, int)

    # Same content should produce same hash
    tongue2 = Tongue(
        name="CalendarTongue",
        version="1.0.0",
        lexicon=frozenset(["CHECK", "ADD"]),
        grammar='CMD ::= "CHECK" Date | "ADD" Event',
        mime_type="application/vnd.kgents.calendar",
        level=GrammarLevel.COMMAND,
        format=GrammarFormat.BNF,
        parser_config=ParserConfig(
            strategy="regex",
            grammar_format=GrammarFormat.BNF,
        ),
        interpreter_config=InterpreterConfig(runtime="python"),
        domain="Calendar",
        constraints=(),
    )
    assert hash(sample_tongue) == hash(tongue2)


def test_tongue_parse_implemented(sample_tongue):
    """Test that parse() works with BNF grammar (Phase 3 implemented)."""
    result = sample_tongue.parse("CHECK 2024-12-15")
    assert result.success
    assert result.ast["verb"] == "CHECK"
    assert result.ast["noun"] == "2024-12-15"


def test_tongue_execute_implemented(sample_tongue):
    """Test that execute() works with parsed AST (Phase 3 implemented)."""
    result = sample_tongue.execute({"verb": "CHECK", "noun": "2024-12-15"})
    assert result.success
    # Command execution without handlers returns intent-only
    assert result.value["executed"] is False


def test_tongue_validate(sample_tongue):
    """Test that validate() returns validated status."""
    assert sample_tongue.validate() is True


def test_tongue_render_implemented(sample_tongue):
    """Test that render() works with AST (Phase 3 implemented)."""
    rendered = sample_tongue.render({"verb": "CHECK", "noun": "2024-12-15"})
    assert rendered == "CHECK 2024-12-15"


# ============================================================================
# Serialization Tests
# ============================================================================


def test_tongue_to_dict(sample_tongue):
    """Test Tongue serialization to dict."""
    data = sample_tongue.to_dict()
    assert data["name"] == "CalendarTongue"
    assert data["version"] == "1.0.0"
    assert data["domain"] == "Calendar Management"
    assert data["level"] == "command"
    assert data["format"] == "bnf"
    assert "CHECK" in data["lexicon"]
    assert len(data["examples"]) == 2
    assert len(data["constraint_proofs"]) == 1


def test_tongue_to_json(sample_tongue):
    """Test Tongue serialization to JSON."""
    json_str = sample_tongue.to_json()
    data = json.loads(json_str)
    assert data["name"] == "CalendarTongue"
    assert data["domain"] == "Calendar Management"


def test_tongue_from_dict(sample_tongue):
    """Test Tongue deserialization from dict."""
    data = sample_tongue.to_dict()
    tongue = Tongue.from_dict(data)

    assert tongue.name == sample_tongue.name
    assert tongue.version == sample_tongue.version
    assert tongue.domain == sample_tongue.domain
    assert tongue.level == sample_tongue.level
    assert tongue.format == sample_tongue.format
    assert tongue.lexicon == sample_tongue.lexicon
    assert len(tongue.examples) == len(sample_tongue.examples)


def test_tongue_from_json(sample_tongue):
    """Test Tongue deserialization from JSON."""
    json_str = sample_tongue.to_json()
    tongue = Tongue.from_json(json_str)

    assert tongue.name == sample_tongue.name
    assert tongue.version == sample_tongue.version


def test_tongue_serialization_round_trip(sample_tongue):
    """Test that serialization is a round-trip."""
    # JSON round-trip
    json_str = sample_tongue.to_json()
    tongue_from_json = Tongue.from_json(json_str)

    assert tongue_from_json.name == sample_tongue.name
    assert tongue_from_json.version == sample_tongue.version
    assert tongue_from_json.grammar == sample_tongue.grammar
    assert tongue_from_json.lexicon == sample_tongue.lexicon
    assert tongue_from_json.domain == sample_tongue.domain
    assert tongue_from_json.level == sample_tongue.level
    assert tongue_from_json.format == sample_tongue.format

    # Hash should be the same (same name, version, grammar)
    assert hash(tongue_from_json) == hash(sample_tongue)


# ============================================================================
# Example and CounterExample Tests
# ============================================================================


def test_example_creation():
    """Test Example creation."""
    ex = Example(
        text="CHECK 2024-12-15",
        expected_ast={"type": "check", "date": "2024-12-15"},
        description="Check calendar on specific date",
    )
    assert ex.text == "CHECK 2024-12-15"
    assert ex.expected_ast["type"] == "check"
    assert ex.description == "Check calendar on specific date"


def test_counter_example_creation():
    """Test CounterExample creation."""
    ce = CounterExample(
        text="DELETE meeting",
        expected_error="Verb 'DELETE' not found",
        description="DELETE should be forbidden",
    )
    assert ce.text == "DELETE meeting"
    assert ce.expected_error == "Verb 'DELETE' not found"
    assert ce.description == "DELETE should be forbidden"
