"""
Tests for Grammarian Agent (G-gent)

Tests the main reify() capability and convenience functions.
"""

import pytest
from agents.g import (
    Grammarian,
    GrammarLevel,
    reify,
    reify_command,
    reify_recursive,
    reify_schema,
)

# ============================================================================
# Grammarian Basic Tests
# ============================================================================


def test_grammarian_instantiation():
    """Test Grammarian can be instantiated."""
    g_gent = Grammarian()
    assert g_gent.name == "G-gent"


def test_grammarian_custom_name():
    """Test Grammarian with custom name."""
    g_gent = Grammarian(name="CustomGent")
    assert g_gent.name == "CustomGent"


# ============================================================================
# reify() Method Tests
# ============================================================================


@pytest.mark.asyncio
async def test_reify_command_level():
    """Test reify() creates a COMMAND-level Tongue."""
    g_gent = Grammarian()

    tongue = await g_gent.reify(
        domain="Calendar Management",
        constraints=["No deletes"],
        level=GrammarLevel.COMMAND,
        examples=["CHECK 2024-12-15", "ADD meeting tomorrow"],
    )

    assert tongue.name == "CalendarManagementTongue"
    assert tongue.level == GrammarLevel.COMMAND
    assert tongue.domain == "Calendar Management"
    assert "No deletes" in tongue.constraints


@pytest.mark.asyncio
async def test_reify_schema_level():
    """Test reify() creates a SCHEMA-level Tongue."""
    g_gent = Grammarian()

    tongue = await g_gent.reify(
        domain="User Profile",
        constraints=["Name required"],
        level=GrammarLevel.SCHEMA,
    )

    assert tongue.level == GrammarLevel.SCHEMA
    assert "BaseModel" in tongue.grammar


@pytest.mark.asyncio
async def test_reify_recursive_level():
    """Test reify() creates a RECURSIVE-level Tongue."""
    g_gent = Grammarian()

    tongue = await g_gent.reify(
        domain="Query Language",
        constraints=["No mutations"],
        level=GrammarLevel.RECURSIVE,
    )

    assert tongue.level == GrammarLevel.RECURSIVE
    assert "start:" in tongue.grammar


@pytest.mark.asyncio
async def test_reify_encodes_constraints():
    """Test reify() structurally encodes constraints."""
    g_gent = Grammarian()

    tongue = await g_gent.reify(
        domain="Safe File Operations",
        constraints=["No deletes", "No overwrites"],
        level=GrammarLevel.COMMAND,
    )

    # DELETE should not be in grammar
    assert "DELETE" not in tongue.grammar


@pytest.mark.asyncio
async def test_reify_generates_examples():
    """Test reify() includes examples in Tongue."""
    g_gent = Grammarian()
    examples = ["READ file.txt", "LIST directory"]

    tongue = await g_gent.reify(
        domain="File Operations",
        constraints=[],
        level=GrammarLevel.COMMAND,
        examples=examples,
    )

    assert len(tongue.examples) == 2
    assert tongue.examples[0].text == "READ file.txt"


@pytest.mark.asyncio
async def test_reify_generates_proofs():
    """Test reify() generates constraint proofs."""
    g_gent = Grammarian()

    tongue = await g_gent.reify(
        domain="Calendar",
        constraints=["No deletes"],
        level=GrammarLevel.COMMAND,
    )

    assert len(tongue.constraint_proofs) >= 1
    proof = tongue.constraint_proofs[0]
    assert proof.constraint == "No deletes"
    assert proof.is_structural()


@pytest.mark.asyncio
async def test_reify_custom_name():
    """Test reify() with custom Tongue name."""
    g_gent = Grammarian()

    tongue = await g_gent.reify(
        domain="Test Domain",
        constraints=[],
        level=GrammarLevel.COMMAND,
        name="CustomTongue",
    )

    assert tongue.name == "CustomTongue"


@pytest.mark.asyncio
async def test_reify_custom_version():
    """Test reify() with custom version."""
    g_gent = Grammarian()

    tongue = await g_gent.reify(
        domain="Test Domain",
        constraints=[],
        level=GrammarLevel.COMMAND,
        version="2.0.0",
    )

    assert tongue.version == "2.0.0"


@pytest.mark.asyncio
async def test_reify_validation():
    """Test reify() validates Tongue when requested."""
    g_gent = Grammarian()

    tongue = await g_gent.reify(
        domain="Test Domain",
        constraints=[],
        level=GrammarLevel.COMMAND,
        validate=True,
    )

    assert tongue.validated is True


@pytest.mark.asyncio
async def test_reify_no_validation():
    """Test reify() can skip validation."""
    g_gent = Grammarian()

    tongue = await g_gent.reify(
        domain="Test Domain",
        constraints=[],
        level=GrammarLevel.COMMAND,
        validate=False,
    )

    # Should still build, but not validated
    assert tongue.validated is False


# ============================================================================
# refine() Method Tests
# ============================================================================


@pytest.mark.asyncio
async def test_refine_increments_version():
    """Test refine() increments version."""
    g_gent = Grammarian()

    tongue_v1 = await g_gent.reify(
        domain="Test",
        constraints=[],
        level=GrammarLevel.COMMAND,
        version="1.0.0",
    )

    tongue_v2 = await g_gent.refine(tongue_v1)

    assert tongue_v2.version == "1.0.1"


@pytest.mark.asyncio
async def test_refine_resets_validation():
    """Test refine() resets validation flag."""
    g_gent = Grammarian()

    tongue_v1 = await g_gent.reify(
        domain="Test",
        constraints=[],
        level=GrammarLevel.COMMAND,
        validate=True,
    )

    tongue_v2 = await g_gent.refine(tongue_v1)

    assert tongue_v2.validated is False  # Needs re-validation


# ============================================================================
# Convenience Function Tests
# ============================================================================


@pytest.mark.asyncio
async def test_reify_convenience_function():
    """Test reify() convenience function."""
    tongue = await reify(
        domain="Test Domain",
        constraints=["No deletes"],
        level=GrammarLevel.COMMAND,
    )

    assert tongue.domain == "Test Domain"
    assert "No deletes" in tongue.constraints


@pytest.mark.asyncio
async def test_reify_schema_convenience():
    """Test reify_schema() convenience function."""
    tongue = await reify_schema(
        domain="User Profile",
        constraints=["Name required"],
    )

    assert tongue.level == GrammarLevel.SCHEMA
    assert "BaseModel" in tongue.grammar


@pytest.mark.asyncio
async def test_reify_command_convenience():
    """Test reify_command() convenience function."""
    tongue = await reify_command(
        domain="File Operations",
        constraints=["No deletes"],
        examples=["READ file.txt"],
    )

    assert tongue.level == GrammarLevel.COMMAND
    assert len(tongue.examples) == 1


@pytest.mark.asyncio
async def test_reify_recursive_convenience():
    """Test reify_recursive() convenience function."""
    tongue = await reify_recursive(
        domain="Query Language",
        constraints=["No mutations"],
    )

    assert tongue.level == GrammarLevel.RECURSIVE
    assert "start:" in tongue.grammar


# ============================================================================
# Real-World Use Case Tests
# ============================================================================


@pytest.mark.asyncio
async def test_calendar_use_case():
    """Test realistic calendar management use case."""
    tongue = await reify_command(
        domain="Calendar Management",
        constraints=["No deletes", "No overwrites"],
        examples=[
            "CHECK 2024-12-15",
            "ADD meeting tomorrow 2pm",
            "LIST events this week",
        ],
    )

    # Verify structure
    assert "DELETE" not in tongue.grammar
    assert len(tongue.examples) == 3
    assert len(tongue.constraint_proofs) >= 1
    assert all(proof.is_structural() for proof in tongue.constraint_proofs)


@pytest.mark.asyncio
async def test_database_query_use_case():
    """Test realistic database query use case."""
    tongue = await reify_command(
        domain="Database Queries",
        constraints=["Read-only", "No admin operations"],
    )

    # Verify read-only constraint
    grammar_upper = tongue.grammar.upper()
    assert "DELETE" not in grammar_upper
    assert "DROP" not in grammar_upper
    assert "UPDATE" not in grammar_upper


@pytest.mark.asyncio
async def test_file_operations_use_case():
    """Test realistic file operations use case."""
    tongue = await reify_command(
        domain="Safe File Operations",
        constraints=["No deletes", "No modifications to system files"],
        examples=[
            "READ file.txt",
            "LIST directory",
            "COPY file.txt to backup.txt",
        ],
    )

    # Verify safety constraints
    assert "DELETE" not in tongue.grammar
    assert len(tongue.examples) == 3


@pytest.mark.asyncio
async def test_citation_exchange_use_case():
    """Test citation exchange schema use case."""
    tongue = await reify_schema(
        domain="Citation Exchange",
        constraints=["Minimal token usage", "Author required", "Year required"],
    )

    # Verify schema structure
    assert tongue.level == GrammarLevel.SCHEMA
    assert "BaseModel" in tongue.grammar
    assert len(tongue.constraints) == 3


# ============================================================================
# Edge Cases
# ============================================================================


@pytest.mark.asyncio
async def test_reify_empty_constraints():
    """Test reify() with empty constraints."""
    tongue = await reify(
        domain="Test",
        constraints=[],
        level=GrammarLevel.COMMAND,
    )

    assert len(tongue.constraints) == 0
    assert tongue.grammar is not None


@pytest.mark.asyncio
async def test_reify_no_examples():
    """Test reify() without examples."""
    tongue = await reify(
        domain="Test",
        constraints=["No deletes"],
        level=GrammarLevel.COMMAND,
        examples=None,
    )

    assert len(tongue.examples) == 0


@pytest.mark.asyncio
async def test_generate_tongue_name():
    """Test Tongue name generation."""
    g_gent = Grammarian()

    name = g_gent._generate_tongue_name("Calendar Management")
    assert name == "CalendarManagementTongue"

    name = g_gent._generate_tongue_name("Simple")
    assert name == "SimpleTongue"


def test_increment_version():
    """Test version increment logic."""
    g_gent = Grammarian()

    assert g_gent._increment_version("1.0.0") == "1.0.1"
    assert g_gent._increment_version("1.0.9") == "1.0.10"
    assert g_gent._increment_version("2.5.3") == "2.5.4"
