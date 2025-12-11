"""
Tests for Grammar Synthesis Engine

Tests the core G-gent synthesis capabilities:
- Domain analysis (entity/operation extraction)
- Grammar generation (SCHEMA, COMMAND, RECURSIVE levels)
- Constraint encoding verification
- Configuration generation
"""

import pytest
from agents.g.synthesis import (
    _apply_constraints,
    _extract_entities,
    _extract_operations,
    analyze_domain,
    generate_interpreter_config,
    generate_parser_config,
    synthesize_grammar,
)
from agents.g.types import GrammarFormat, GrammarLevel

# ============================================================================
# Domain Analysis Tests
# ============================================================================


@pytest.mark.asyncio
async def test_analyze_domain_extracts_entities() -> None:
    """Test entity extraction from intent."""
    intent = "Manage Calendar events and tasks for users"
    constraints = []

    analysis = await analyze_domain(intent, constraints)

    # Should extract common nouns
    assert "calendar" in analysis.entities or "event" in analysis.entities
    assert len(analysis.entities) > 0


@pytest.mark.asyncio
async def test_analyze_domain_extracts_operations() -> None:
    """Test operation extraction from intent."""
    intent = "Read and write files, but never delete them"
    constraints = []

    analysis = await analyze_domain(intent, constraints)

    # Should extract verbs
    assert "READ" in analysis.operations or "WRITE" in analysis.operations
    assert len(analysis.operations) > 0


@pytest.mark.asyncio
async def test_analyze_domain_applies_constraints() -> None:
    """Test constraint application filters operations."""
    intent = "Read, write, and delete files"
    constraints = ["No deletes"]

    analysis = await analyze_domain(intent, constraints)

    # DELETE should be filtered out
    assert "DELETE" not in analysis.operations


@pytest.mark.asyncio
async def test_analyze_domain_with_examples() -> None:
    """Test domain analysis with example inputs."""
    intent = "Command language for file operations"
    constraints = ["No deletes"]
    examples = ["READ file.txt", "LIST directory"]

    analysis = await analyze_domain(intent, constraints, examples)

    # Should extract from examples
    assert "READ" in analysis.operations or "LIST" in analysis.operations
    assert "file" in analysis.entities or "directory" in analysis.entities


def test_extract_entities_from_intent() -> None:
    """Test entity extraction heuristics."""
    intent = "Manage Event and Task items in the system"
    examples = []

    entities = _extract_entities(intent, examples)

    # Should find common nouns
    assert len(entities) > 0


def test_extract_operations_from_intent() -> None:
    """Test operation extraction heuristics."""
    intent = "Users can read, write, create, and delete resources"
    examples = []

    operations = _extract_operations(intent, examples)

    # Should find verbs
    assert any(op in ["READ", "WRITE", "CREATE", "DELETE"] for op in operations)


def test_apply_constraints_no_deletes() -> None:
    """Test 'No deletes' constraint filtering."""
    operations = ["READ", "WRITE", "DELETE", "LIST"]
    constraints = ["No deletes"]

    filtered = _apply_constraints(operations, constraints)

    assert "DELETE" not in filtered
    assert "READ" in filtered


def test_apply_constraints_read_only() -> None:
    """Test 'Read-only' constraint filtering."""
    operations = ["READ", "WRITE", "DELETE", "LIST", "GET"]
    constraints = ["Read-only"]

    filtered = _apply_constraints(operations, constraints)

    # Should only have read operations
    assert all(op in ["READ", "LIST", "GET", "QUERY", "CHECK"] for op in filtered)


# ============================================================================
# Grammar Generation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_synthesize_schema_grammar() -> None:
    """Test SCHEMA level grammar generation (Pydantic)."""
    analysis = await analyze_domain(
        intent="User profile with name and email",
        constraints=[],
    )

    grammar = await synthesize_grammar(analysis, GrammarLevel.SCHEMA)

    # Should be valid Python/Pydantic
    assert "class " in grammar
    assert "BaseModel" in grammar
    assert "from pydantic import" in grammar


@pytest.mark.asyncio
async def test_synthesize_command_grammar() -> None:
    """Test COMMAND level grammar generation (BNF)."""
    analysis = await analyze_domain(
        intent="File operations: read, write, list",
        constraints=["No deletes"],
    )

    grammar = await synthesize_grammar(analysis, GrammarLevel.COMMAND)

    # Should be valid BNF
    assert "::=" in grammar
    assert "VERB" in grammar
    assert "NOUN" in grammar
    # DELETE should not appear (constraint)
    assert "DELETE" not in grammar


@pytest.mark.asyncio
async def test_synthesize_recursive_grammar() -> None:
    """Test RECURSIVE level grammar generation (Lark)."""
    analysis = await analyze_domain(
        intent="Query language with filter, map, reduce",
        constraints=[],
    )

    grammar = await synthesize_grammar(analysis, GrammarLevel.RECURSIVE)

    # Should be valid Lark
    assert "start:" in grammar
    assert "expr:" in grammar
    # Recursive structure
    assert "expr*" in grammar or "expr+" in grammar


@pytest.mark.asyncio
async def test_command_grammar_encodes_constraints() -> None:
    """Test that constraints are structurally encoded in grammar."""
    analysis = await analyze_domain(
        intent="Calendar commands",
        constraints=["No deletes", "No overwrites"],
    )

    grammar = await synthesize_grammar(analysis, GrammarLevel.COMMAND)

    # Forbidden operations should NOT appear in VERB production
    assert "DELETE" not in grammar


@pytest.mark.asyncio
async def test_schema_grammar_has_valid_pydantic() -> None:
    """Test that SCHEMA grammar is valid Pydantic."""
    analysis = await analyze_domain(
        intent="Simple data model",
        constraints=[],
    )

    grammar = await synthesize_grammar(analysis, GrammarLevel.SCHEMA)

    # Should be executable Python
    assert "from pydantic import BaseModel" in grammar
    assert "class GeneratedModel(BaseModel):" in grammar


# ============================================================================
# Configuration Generation Tests
# ============================================================================


def test_generate_parser_config_schema() -> None:
    """Test parser config for SCHEMA level."""
    config = generate_parser_config("", GrammarLevel.SCHEMA, GrammarFormat.PYDANTIC)

    assert config.strategy == "pydantic"
    assert config.grammar_format == GrammarFormat.PYDANTIC
    assert config.confidence_threshold == 1.0  # Binary validation


def test_generate_parser_config_command() -> None:
    """Test parser config for COMMAND level."""
    config = generate_parser_config("", GrammarLevel.COMMAND, GrammarFormat.BNF)

    assert config.strategy == "regex"
    assert config.grammar_format == GrammarFormat.BNF
    assert config.repair_strategy == "best_effort"


def test_generate_parser_config_recursive() -> None:
    """Test parser config for RECURSIVE level."""
    config = generate_parser_config("", GrammarLevel.RECURSIVE, GrammarFormat.LARK)

    assert config.strategy == "lark"
    assert config.grammar_format == GrammarFormat.LARK


def test_generate_interpreter_config_schema() -> None:
    """Test interpreter config for SCHEMA level."""
    config = generate_interpreter_config(GrammarLevel.SCHEMA)

    assert config.runtime == "python"
    assert config.pure_functions_only is True  # Schemas are pure
    assert config.timeout_ms == 1000  # Fast


def test_generate_interpreter_config_command() -> None:
    """Test interpreter config for COMMAND level."""
    config = generate_interpreter_config(GrammarLevel.COMMAND)

    assert config.runtime == "python"
    assert config.pure_functions_only is False  # Commands may have side effects


def test_generate_interpreter_config_recursive() -> None:
    """Test interpreter config for RECURSIVE level."""
    config = generate_interpreter_config(GrammarLevel.RECURSIVE)

    assert config.runtime == "sandboxed"  # Needs isolation
    assert config.pure_functions_only is True
    assert config.timeout_ms == 10000  # More time for complex evaluation


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.asyncio
async def test_full_synthesis_pipeline_command() -> None:
    """Test complete synthesis pipeline for COMMAND level."""
    # Analyze
    analysis = await analyze_domain(
        intent="Safe file operations",
        constraints=["No deletes", "No overwrites"],
        examples=["READ file.txt", "LIST directory"],
    )

    # Synthesize grammar
    grammar = await synthesize_grammar(analysis, GrammarLevel.COMMAND)

    # Generate configs
    parser_config = generate_parser_config(
        grammar, GrammarLevel.COMMAND, GrammarFormat.BNF
    )
    interpreter_config = generate_interpreter_config(GrammarLevel.COMMAND)

    # Verify
    assert grammar is not None
    assert "VERB" in grammar
    assert "DELETE" not in grammar  # Constraint encoded
    assert parser_config.strategy == "regex"
    assert interpreter_config.runtime == "python"


@pytest.mark.asyncio
async def test_full_synthesis_pipeline_schema() -> None:
    """Test complete synthesis pipeline for SCHEMA level."""
    # Analyze
    analysis = await analyze_domain(
        intent="User profile with required fields",
        constraints=["Name required", "Email required"],
    )

    # Synthesize grammar
    grammar = await synthesize_grammar(analysis, GrammarLevel.SCHEMA)

    # Generate configs
    parser_config = generate_parser_config(
        grammar, GrammarLevel.SCHEMA, GrammarFormat.PYDANTIC
    )
    interpreter_config = generate_interpreter_config(GrammarLevel.SCHEMA)

    # Verify
    assert "BaseModel" in grammar
    assert parser_config.strategy == "pydantic"
    assert interpreter_config.pure_functions_only is True


@pytest.mark.asyncio
async def test_constraint_no_deletes_encoded_structurally() -> None:
    """Test 'No deletes' constraint is structurally encoded."""
    analysis = await analyze_domain(
        intent="Database queries",
        constraints=["No deletes"],
    )

    grammar = await synthesize_grammar(analysis, GrammarLevel.COMMAND)

    # DELETE should not be in VERB production
    lines = grammar.split("\n")
    verb_line = next((line for line in lines if line.startswith("VERB")), "")

    assert "DELETE" not in verb_line


@pytest.mark.asyncio
async def test_constraint_read_only_encoded_structurally() -> None:
    """Test 'Read-only' constraint is structurally encoded."""
    analysis = await analyze_domain(
        intent="Query interface",
        constraints=["Read-only"],
    )

    grammar = await synthesize_grammar(analysis, GrammarLevel.COMMAND)

    # Should only have read operations
    lines = grammar.split("\n")
    verb_line = next((line for line in lines if line.startswith("VERB")), "")

    # No write operations
    for forbidden in ["WRITE", "DELETE", "UPDATE", "MODIFY", "CREATE"]:
        assert forbidden not in verb_line
