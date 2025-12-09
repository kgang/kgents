"""
Tests for Tongue artifact utilities.

Tests cover:
- TongueBuilder pattern
- Validation utilities
- Serialization utilities (JSON, YAML)
- Tongue templates (schema, command, recursive)
- Tongue evolution/versioning
"""

import tempfile
import pytest
from pathlib import Path

import importlib.util

HAS_YAML = importlib.util.find_spec("yaml") is not None

from agents.g.types import (
    GrammarLevel,
    GrammarFormat,
    ParserConfig,
    InterpreterConfig,
    ConstraintProof,
)
from agents.g.tongue import (
    TongueBuilder,
    validate_tongue,
    save_tongue_json,
    load_tongue_json,
    save_tongue_yaml,
    load_tongue_yaml,
    create_schema_tongue,
    create_command_tongue,
    create_recursive_tongue,
    evolve_tongue,
)


# ============================================================================
# TongueBuilder Tests
# ============================================================================


def test_tongue_builder_minimal():
    """Test TongueBuilder with minimal required fields."""
    tongue = (
        TongueBuilder("TestTongue", "1.0.0")
        .with_domain("Testing")
        .with_grammar('TEST ::= "test"')
        .build()
    )

    assert tongue.name == "TestTongue"
    assert tongue.version == "1.0.0"
    assert tongue.domain == "Testing"
    assert tongue.grammar == 'TEST ::= "test"'
    assert tongue.level == GrammarLevel.COMMAND  # default


def test_tongue_builder_missing_grammar():
    """Test TongueBuilder raises error without grammar."""
    builder = TongueBuilder("TestTongue", "1.0.0").with_domain("Testing")
    with pytest.raises(ValueError, match="Grammar is required"):
        builder.build()


def test_tongue_builder_missing_domain():
    """Test TongueBuilder raises error without domain."""
    builder = TongueBuilder("TestTongue", "1.0.0").with_grammar("TEST")
    with pytest.raises(ValueError, match="Domain is required"):
        builder.build()


def test_tongue_builder_full():
    """Test TongueBuilder with all fields."""
    tongue = (
        TongueBuilder("CalendarTongue", "1.0.0")
        .with_domain("Calendar Management")
        .with_level(GrammarLevel.COMMAND)
        .with_format(GrammarFormat.BNF)
        .with_grammar('CMD ::= "CHECK" | "ADD"')
        .with_lexicon("CHECK", "ADD", "Date", "Event")
        .with_mime_type("application/vnd.kgents.calendar")
        .with_constraint("No DELETE operations")
        .with_example("CHECK 2024-12-15")
        .with_parser_config(
            ParserConfig(
                strategy="regex",
                grammar_format=GrammarFormat.BNF,
            )
        )
        .with_interpreter_config(InterpreterConfig(runtime="python"))
        .with_proof(
            ConstraintProof(
                constraint="No DELETE",
                mechanism="DELETE not in lexicon",
            )
        )
        .validated(True)
        .build()
    )

    assert tongue.name == "CalendarTongue"
    assert tongue.version == "1.0.0"
    assert tongue.domain == "Calendar Management"
    assert tongue.level == GrammarLevel.COMMAND
    assert tongue.format == GrammarFormat.BNF
    assert "CHECK" in tongue.lexicon
    assert len(tongue.constraints) == 1
    assert len(tongue.examples) == 1
    assert len(tongue.constraint_proofs) == 1
    assert tongue.validated is True


def test_tongue_builder_fluent_interface():
    """Test that TongueBuilder supports method chaining."""
    builder = TongueBuilder("Test", "1.0.0")
    assert builder.with_domain("Test") is builder
    assert builder.with_grammar("TEST") is builder
    assert builder.with_level(GrammarLevel.SCHEMA) is builder


def test_tongue_builder_infer_parser_strategy():
    """Test that parser strategy is inferred correctly."""
    # PYDANTIC format -> pydantic strategy
    tongue1 = (
        TongueBuilder("Test1", "1.0.0")
        .with_domain("Test")
        .with_format(GrammarFormat.PYDANTIC)
        .with_grammar("class Test(BaseModel): pass")
        .build()
    )
    assert tongue1.parser_config.strategy == "pydantic"

    # LARK format -> lark strategy
    tongue2 = (
        TongueBuilder("Test2", "1.0.0")
        .with_domain("Test")
        .with_format(GrammarFormat.LARK)
        .with_grammar("test: TEST")
        .build()
    )
    assert tongue2.parser_config.strategy == "lark"

    # COMMAND level -> regex strategy
    tongue3 = (
        TongueBuilder("Test3", "1.0.0")
        .with_domain("Test")
        .with_level(GrammarLevel.COMMAND)
        .with_grammar("CMD ::= TEST")
        .build()
    )
    assert tongue3.parser_config.strategy == "regex"


# ============================================================================
# Validation Tests
# ============================================================================


def test_validate_tongue_success():
    """Test validation of a valid Tongue."""
    tongue = (
        TongueBuilder("ValidTongue", "1.0.0")
        .with_domain("Valid Domain")
        .with_grammar('VALID ::= "test"')
        .with_constraint("No DELETE")
        .with_proof(
            ConstraintProof(
                constraint="No DELETE",
                mechanism="DELETE not in grammar - grammatically impossible",
            )
        )
        .build()
    )

    is_valid, errors = validate_tongue(tongue)
    assert is_valid
    assert len(errors) == 0


def test_validate_tongue_empty_grammar():
    """Test validation fails for empty grammar."""
    # Builder will catch this, but let's test validate_tongue directly
    # by bypassing the builder
    tongue = (
        TongueBuilder("InvalidTongue", "1.0.0")
        .with_domain("Test")
        .with_grammar("   ")  # Whitespace only - passes builder but fails validation
        .build()
    )

    is_valid, errors = validate_tongue(tongue)
    assert not is_valid
    assert any("Grammar cannot be empty" in error for error in errors)


def test_validate_tongue_empty_domain():
    """Test validation fails for empty domain."""
    # Builder will catch this, but let's test validate_tongue directly
    # by bypassing the builder
    tongue = (
        TongueBuilder("InvalidTongue", "1.0.0")
        .with_domain("   ")  # Whitespace only - passes builder but fails validation
        .with_grammar("TEST")
        .build()
    )

    is_valid, errors = validate_tongue(tongue)
    assert not is_valid
    assert any("Domain cannot be empty" in error for error in errors)


def test_validate_tongue_constraints_without_proofs():
    """Test validation fails for constraints without proofs."""
    tongue = (
        TongueBuilder("InvalidTongue", "1.0.0")
        .with_domain("Test")
        .with_grammar("TEST")
        .with_constraint("No DELETE")
        # No proofs added
        .build()
    )

    is_valid, errors = validate_tongue(tongue)
    assert not is_valid
    assert any("no proofs provided" in error for error in errors)


def test_validate_tongue_non_structural_constraint():
    """Test validation fails for non-structural constraints."""
    tongue = (
        TongueBuilder("InvalidTongue", "1.0.0")
        .with_domain("Test")
        .with_grammar("TEST")
        .with_constraint("No operations on Sundays")
        .with_proof(
            ConstraintProof(
                constraint="No operations on Sundays",
                mechanism="Runtime check for day of week",  # Not structural!
            )
        )
        .build()
    )

    is_valid, errors = validate_tongue(tongue)
    assert not is_valid
    assert any("not structurally enforced" in error for error in errors)


def test_validate_tongue_format_strategy_mismatch():
    """Test validation fails for PYDANTIC format with wrong strategy."""
    tongue = (
        TongueBuilder("InvalidTongue", "1.0.0")
        .with_domain("Test")
        .with_format(GrammarFormat.PYDANTIC)
        .with_grammar("class Test(BaseModel): pass")
        .with_parser_config(
            ParserConfig(
                strategy="regex",  # Wrong strategy!
                grammar_format=GrammarFormat.PYDANTIC,
            )
        )
        .build()
    )

    is_valid, errors = validate_tongue(tongue)
    assert not is_valid
    assert any(
        "PYDANTIC format requires 'pydantic' parser strategy" in error
        for error in errors
    )


# ============================================================================
# Serialization Tests
# ============================================================================


def test_save_load_json():
    """Test saving and loading Tongue from JSON."""
    tongue = (
        TongueBuilder("TestTongue", "1.0.0")
        .with_domain("Test")
        .with_grammar("TEST")
        .build()
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        filepath = f.name

    try:
        save_tongue_json(tongue, filepath)
        loaded = load_tongue_json(filepath)

        assert loaded.name == tongue.name
        assert loaded.version == tongue.version
        assert loaded.grammar == tongue.grammar
        assert loaded.domain == tongue.domain
    finally:
        Path(filepath).unlink()


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
def test_save_load_yaml():
    """Test saving and loading Tongue from YAML."""
    tongue = (
        TongueBuilder("TestTongue", "1.0.0")
        .with_domain("Test")
        .with_grammar("TEST")
        .with_example("test example")
        .build()
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        filepath = f.name

    try:
        save_tongue_yaml(tongue, filepath)
        loaded = load_tongue_yaml(filepath)

        assert loaded.name == tongue.name
        assert loaded.version == tongue.version
        assert loaded.grammar == tongue.grammar
        assert len(loaded.examples) == 1
    finally:
        Path(filepath).unlink()


# ============================================================================
# Template Tests
# ============================================================================


def test_create_schema_tongue():
    """Test creating a SCHEMA-level tongue."""
    pydantic_model = """
    from pydantic import BaseModel
    class User(BaseModel):
        name: str
        age: int
    """

    tongue = create_schema_tongue(
        name="UserSchema",
        domain="User Data",
        grammar=pydantic_model,
    )

    assert tongue.name == "UserSchema"
    assert tongue.version == "1.0.0"
    assert tongue.domain == "User Data"
    assert tongue.level == GrammarLevel.SCHEMA
    assert tongue.format == GrammarFormat.PYDANTIC
    assert tongue.parser_config.strategy == "pydantic"
    assert tongue.interpreter_config.pure_functions_only is True


def test_create_command_tongue():
    """Test creating a COMMAND-level tongue."""
    bnf_grammar = 'CMD ::= "CHECK" | "ADD"'
    constraints = ["No DELETE operations", "No overwrites"]

    tongue = create_command_tongue(
        name="CalendarCommands",
        domain="Calendar Management",
        grammar=bnf_grammar,
        constraints=constraints,
    )

    assert tongue.name == "CalendarCommands"
    assert tongue.level == GrammarLevel.COMMAND
    assert tongue.format == GrammarFormat.BNF
    assert tongue.parser_config.strategy == "regex"
    assert "CHECK" in tongue.lexicon
    assert len(tongue.constraints) == 2


def test_create_recursive_tongue():
    """Test creating a RECURSIVE-level tongue."""
    lark_grammar = """
    expr: atom | "(" op expr+ ")"
    op: "filter" | "map" | "reduce"
    atom: STRING | NUMBER
    """

    tongue = create_recursive_tongue(
        name="DataTransform",
        domain="Data Transformation",
        grammar=lark_grammar,
    )

    assert tongue.name == "DataTransform"
    assert tongue.level == GrammarLevel.RECURSIVE
    assert tongue.format == GrammarFormat.LARK
    assert tongue.parser_config.strategy == "lark"
    assert tongue.interpreter_config.runtime == "sandboxed"
    assert tongue.interpreter_config.pure_functions_only is True


# ============================================================================
# Evolution Tests
# ============================================================================


def test_evolve_tongue_version():
    """Test evolving a Tongue with new version."""
    tongue_v1 = (
        TongueBuilder("TestTongue", "1.0.0")
        .with_domain("Test")
        .with_grammar("TEST")
        .build()
    )

    tongue_v2 = evolve_tongue(tongue_v1, version="2.0.0")

    assert tongue_v2.version == "2.0.0"
    assert tongue_v2.name == tongue_v1.name
    assert tongue_v2.grammar == tongue_v1.grammar


def test_evolve_tongue_grammar():
    """Test evolving a Tongue with new grammar."""
    tongue_v1 = (
        TongueBuilder("TestTongue", "1.0.0")
        .with_domain("Test")
        .with_grammar("TEST ::= old")
        .validated(True)
        .build()
    )

    tongue_v2 = evolve_tongue(
        tongue_v1,
        version="2.0.0",
        grammar="TEST ::= new",
        validated=False,  # New grammar needs revalidation
    )

    assert tongue_v2.version == "2.0.0"
    assert tongue_v2.grammar == "TEST ::= new"
    assert tongue_v2.validated is False


def test_evolve_tongue_constraints():
    """Test evolving a Tongue with new constraints."""
    tongue_v1 = (
        TongueBuilder("TestTongue", "1.0.0")
        .with_domain("Test")
        .with_grammar("TEST")
        .with_constraint("Old constraint")
        .build()
    )

    new_constraints = ("New constraint 1", "New constraint 2")
    tongue_v2 = evolve_tongue(tongue_v1, constraints=new_constraints)

    assert tongue_v2.constraints == new_constraints
    assert len(tongue_v2.constraints) == 2


def test_evolve_tongue_immutability():
    """Test that evolving creates a new Tongue (immutable)."""
    tongue_v1 = (
        TongueBuilder("TestTongue", "1.0.0")
        .with_domain("Test")
        .with_grammar("TEST")
        .build()
    )

    tongue_v2 = evolve_tongue(tongue_v1, version="2.0.0")

    # Original unchanged
    assert tongue_v1.version == "1.0.0"
    # New version created
    assert tongue_v2.version == "2.0.0"
    # Different objects
    assert tongue_v1 is not tongue_v2


# ============================================================================
# Integration Tests
# ============================================================================


def test_builder_validation_integration():
    """Test that built Tongue passes validation."""
    tongue = (
        TongueBuilder("ValidTongue", "1.0.0")
        .with_domain("Valid Domain")
        .with_grammar('VALID ::= "test"')
        .with_constraint("No DELETE")
        .with_proof(
            ConstraintProof(
                constraint="No DELETE",
                mechanism="DELETE not in lexicon - syntax error",
            )
        )
        .validated(True)
        .build()
    )

    is_valid, errors = validate_tongue(tongue)
    assert is_valid, f"Validation failed: {errors}"


def test_template_validation_integration():
    """Test that template-created Tongues pass validation."""
    tongue = create_command_tongue(
        name="SafeQuery",
        domain="Database Queries",
        grammar='QUERY ::= "SELECT" | "INSERT"',
        # lexicon={"SELECT", "INSERT"},
        constraints=["No DELETE", "No DROP"],
    )

    # Note: This will fail because we don't have proofs
    is_valid, errors = validate_tongue(tongue)
    assert not is_valid
    assert any("no proofs provided" in error for error in errors)


def test_serialization_round_trip_integration():
    """Test full round-trip: build -> save -> load -> validate."""
    tongue = (
        TongueBuilder("RoundTripTongue", "1.0.0")
        .with_domain("Round Trip Test")
        .with_grammar("TEST")
        .with_example("test example")
        .build()
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        filepath = f.name

    try:
        save_tongue_json(tongue, filepath)
        loaded = load_tongue_json(filepath)

        # Verify round-trip preservation
        assert loaded.name == tongue.name
        assert loaded.version == tongue.version
        assert loaded.grammar == tongue.grammar
        assert len(loaded.examples) == len(tongue.examples)
        assert hash(loaded) == hash(tongue)
    finally:
        Path(filepath).unlink()
