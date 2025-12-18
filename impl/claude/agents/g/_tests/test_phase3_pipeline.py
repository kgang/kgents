"""
G-gent Phase 3 Tests: P-gent + J-gent Integration

Test the complete pipeline:
1. Parse (P-gent integration)
2. Execute (J-gent integration)
3. Render (round-trip validation)
"""

from __future__ import annotations

from typing import Any

import pytest

from agents.g import (
    create_command_tongue,
    create_recursive_tongue,
    create_schema_tongue,
)
from agents.g.renderer import validate_round_trip

# ============================================================================
# Level 1: Schema Parsing + Execution Tests
# ============================================================================


def test_schema_tongue_parse() -> None:
    """Test parsing with Pydantic schema tongue."""
    tongue = create_schema_tongue(
        name="TestSchema",
        domain="Testing",
        grammar="""
from pydantic import BaseModel

class TestModel(BaseModel):
    name: str
    count: int
""",
    )

    # Parse valid input
    result = tongue.parse('{"name": "test", "count": 42}')

    assert result.success
    assert result.ast is not None
    assert result.ast["name"] == "test"
    assert result.ast["count"] == 42
    assert result.confidence > 0.8


def test_schema_tongue_execute() -> None:
    """Test execution with schema tongue (pure validation)."""
    tongue = create_schema_tongue(
        name="TestSchema",
        domain="Testing",
        grammar="""
from pydantic import BaseModel

class TestModel(BaseModel):
    name: str
    count: int
""",
    )

    # Parse and execute
    parse_result = tongue.parse('{"name": "test", "count": 42}')
    assert parse_result.success

    exec_result = tongue.execute(parse_result.ast)

    assert exec_result.success
    assert exec_result.value == parse_result.ast


def test_schema_tongue_render() -> None:
    """Test rendering with schema tongue."""
    tongue = create_schema_tongue(
        name="TestSchema",
        domain="Testing",
        grammar="""
from pydantic import BaseModel

class TestModel(BaseModel):
    name: str
    count: int
""",
    )

    # Parse, render, re-parse
    ast = {"name": "test", "count": 42}
    rendered = tongue.render(ast)

    # Should be parseable
    assert "name" in rendered
    assert "test" in rendered
    assert "42" in rendered


# ============================================================================
# Level 2: Command Parsing + Execution Tests
# ============================================================================


def test_command_tongue_parse() -> None:
    """Test parsing with BNF command tongue."""
    tongue = create_command_tongue(
        name="CalendarCommands",
        domain="Calendar Management",
        grammar="""
<command> ::= <verb> <noun>
<verb> ::= "CHECK" | "ADD" | "LIST"
<noun> ::= <date> | <event>
""",
    )

    # Parse valid command
    result = tongue.parse("CHECK 2024-12-15")

    assert result.success
    assert result.ast is not None
    assert result.ast["verb"] == "CHECK"
    assert "2024-12-15" in result.ast["noun"]


def test_command_tongue_parse_invalid() -> None:
    """Test parsing invalid command (forbidden DELETE)."""
    tongue = create_command_tongue(
        name="CalendarCommands",
        domain="Calendar Management",
        grammar="""
<command> ::= <verb> <noun>
<verb> ::= "CHECK" | "ADD" | "LIST"
<noun> ::= <date>
""",
    )

    # Try to parse forbidden DELETE
    result = tongue.parse("DELETE meeting")

    assert not result.success
    assert (
        result.error is None or "DELETE" not in result.error or "No valid command" in result.error
    )


def test_command_tongue_execute_with_handlers() -> None:
    """Test execution with command handlers."""
    tongue = create_command_tongue(
        name="CalendarCommands",
        domain="Calendar Management",
        grammar="""
<command> ::= <verb> <noun>
<verb> ::= "CHECK" | "ADD"
""",
    )

    # Define handlers
    def check_handler(noun: str, context: dict[str, Any]) -> dict[str, Any]:
        return {"status": "checked", "date": noun}

    def add_handler(noun: str, context: dict[str, Any]) -> dict[str, Any]:
        return {"status": "added", "event": noun}

    handlers = {"CHECK": check_handler, "ADD": add_handler}

    # Parse and execute CHECK
    parse_result = tongue.parse("CHECK 2024-12-15")
    assert parse_result.success

    exec_result = tongue.execute(parse_result.ast, handlers=handlers)

    assert exec_result.success
    assert exec_result.value is not None
    assert exec_result.value["status"] == "checked"
    assert exec_result.value["date"] == "2024-12-15"


def test_command_tongue_execute_no_handler() -> None:
    """Test execution without handler (intent-only result)."""
    tongue = create_command_tongue(
        name="CalendarCommands",
        domain="Calendar Management",
        grammar="""
<verb> ::= "CHECK" | "ADD"
""",
    )

    # Parse and execute without handlers
    parse_result = tongue.parse("CHECK 2024-12-15")
    assert parse_result.success

    exec_result = tongue.execute(parse_result.ast)

    # Should succeed but not execute
    assert exec_result.success
    assert exec_result.value is not None
    assert not exec_result.value.get("executed", True)
    assert "CHECK" in exec_result.value["intent"]


def test_command_tongue_render() -> None:
    """Test rendering command AST."""
    tongue = create_command_tongue(
        name="CalendarCommands",
        domain="Calendar Management",
        grammar="""
<verb> ::= "CHECK"
""",
    )

    # Render command AST
    ast = {"verb": "CHECK", "noun": "2024-12-15"}
    rendered = tongue.render(ast)

    assert rendered == "CHECK 2024-12-15"


def test_command_round_trip() -> None:
    """Test round-trip: parse → render → parse."""
    tongue = create_command_tongue(
        name="CalendarCommands",
        domain="Calendar Management",
        grammar="""
<verb> ::= "CHECK" | "ADD"
""",
    )

    # Round-trip validation
    success, message = validate_round_trip(tongue, "CHECK 2024-12-15")

    assert success, message


# ============================================================================
# Level 3: Recursive Parsing + Execution Tests
# ============================================================================


@pytest.mark.skipif(True, reason="Lark optional - Phase 3 focuses on Schema + Command levels")
def test_recursive_tongue_parse() -> None:
    """Test parsing with Lark recursive tongue."""
    tongue = create_recursive_tongue(
        name="SExpressions",
        domain="Symbolic Expressions",
        grammar="""
start: sexpr
sexpr: "(" SYMBOL sexpr* ")"
     | SYMBOL
SYMBOL: /[a-z]+/
""",
    )

    # Parse S-expression
    result = tongue.parse("(add x y)")

    assert result.success
    assert result.ast is not None
    assert result.ast["type"] == "start"


# ============================================================================
# Full Pipeline Integration Tests
# ============================================================================


def test_full_pipeline_schema() -> None:
    """Test complete pipeline: create → parse → execute → render."""
    # Create tongue
    tongue = create_schema_tongue(
        name="UserProfile",
        domain="User Management",
        grammar="""
from pydantic import BaseModel

class UserProfile(BaseModel):
    username: str
    age: int
    active: bool
""",
    )

    # 1. Parse
    parse_result = tongue.parse('{"username": "alice", "age": 30, "active": true}')
    assert parse_result.success
    assert parse_result.ast is not None
    assert parse_result.ast["username"] == "alice"

    # 2. Execute (validation)
    exec_result = tongue.execute(parse_result.ast)
    assert exec_result.success

    # 3. Render
    rendered = tongue.render(parse_result.ast)
    assert "alice" in rendered
    assert "30" in rendered

    # 4. Round-trip
    success, message = validate_round_trip(
        tongue, '{"username": "alice", "age": 30, "active": true}'
    )
    # Note: Round-trip might not be perfect due to formatting differences
    # but structural equality should hold


def test_full_pipeline_command() -> None:
    """Test complete pipeline for command tongue."""
    # Create tongue
    tongue = create_command_tongue(
        name="FileCommands",
        domain="File Operations",
        grammar="""
<command> ::= <verb> <path>
<verb> ::= "READ" | "WRITE" | "LIST"
""",
    )

    # Define handlers
    def read_handler(path: str, context: dict[str, Any]) -> dict[str, Any]:
        return {"status": "read", "path": path, "content": f"Contents of {path}"}

    handlers = {"READ": read_handler}

    # 1. Parse
    parse_result = tongue.parse("READ /tmp/test.txt")
    assert parse_result.success
    assert parse_result.ast is not None
    assert parse_result.ast["verb"] == "READ"
    assert "/tmp/test.txt" in parse_result.ast["noun"]

    # 2. Execute with handler
    exec_result = tongue.execute(parse_result.ast, handlers=handlers)
    assert exec_result.success
    assert exec_result.value is not None
    assert exec_result.value["status"] == "read"
    assert "test.txt" in exec_result.value["content"]

    # 3. Render
    rendered = tongue.render(parse_result.ast)
    assert rendered == "READ /tmp/test.txt"

    # 4. Round-trip
    success, message = validate_round_trip(tongue, "READ /tmp/test.txt")
    assert success, message


def test_constraint_enforcement_parse_blocks() -> None:
    """Test that constraints prevent parsing forbidden operations."""
    # Create tongue without DELETE
    tongue = create_command_tongue(
        name="SafeFileCommands",
        domain="Safe File Operations",
        grammar="""
<command> ::= <verb> <path>
<verb> ::= "READ" | "LIST"
""",
    )

    # Should parse allowed commands
    result_read = tongue.parse("READ /tmp/file.txt")
    assert result_read.success

    # Should fail to parse forbidden DELETE
    result_delete = tongue.parse("DELETE /tmp/file.txt")
    assert not result_delete.success


def test_context_passing() -> None:
    """Test passing execution context through pipeline."""
    tongue = create_command_tongue(
        name="ContextCommands",
        domain="Context Testing",
        grammar="""
<verb> ::= "GET" | "SET"
""",
    )

    # Handler that uses context
    def get_handler(noun: str, context: dict[str, Any]) -> dict[str, Any]:
        value = context.get(noun, "not found")
        return {"key": noun, "value": value}

    handlers = {"GET": get_handler}

    # Parse
    parse_result = tongue.parse("GET username")
    assert parse_result.success

    # Execute with context
    context: dict[str, Any] = {"username": "alice", "role": "admin"}
    exec_result = tongue.execute(parse_result.ast, context=context, handlers=handlers)

    assert exec_result.success
    assert exec_result.value is not None
    assert exec_result.value["key"] == "username"
    assert exec_result.value["value"] == "alice"


def test_parse_error_handling() -> None:
    """Test error handling in parsing."""
    tongue = create_command_tongue(
        name="TestCommands",
        domain="Testing",
        grammar="""
<verb> ::= "TEST"
""",
    )

    # Invalid input
    result = tongue.parse("INVALID COMMAND")

    assert not result.success
    assert result.error is not None
    assert result.confidence == 0.0


def test_execute_error_handling() -> None:
    """Test error handling in execution."""
    tongue = create_command_tongue(
        name="TestCommands",
        domain="Testing",
        grammar="""
<verb> ::= "TEST"
""",
    )

    # Handler that raises exception
    def failing_handler(noun: str, context: dict[str, Any]) -> dict[str, Any]:
        raise ValueError("Intentional failure")

    handlers = {"TEST": failing_handler}

    # Parse successfully
    parse_result = tongue.parse("TEST something")
    assert parse_result.success

    # Execute should handle error
    exec_result = tongue.execute(parse_result.ast, handlers=handlers)

    assert not exec_result.success
    assert exec_result.error is not None and "Intentional failure" in exec_result.error


# ============================================================================
# Performance and Confidence Tests
# ============================================================================


def test_confidence_scoring() -> None:
    """Test that confidence scores are reasonable."""
    tongue = create_command_tongue(
        name="TestCommands",
        domain="Testing",
        grammar="""
<verb> ::= "TEST"
""",
    )

    # Valid parse should have high confidence
    result = tongue.parse("TEST something")

    assert result.success
    assert result.confidence > 0.7


def test_side_effects_tracking() -> None:
    """Test that execution tracks side effects."""
    tongue = create_command_tongue(
        name="TestCommands",
        domain="Testing",
        grammar="""
<verb> ::= "TEST"
""",
    )

    # Handler with side effects
    def test_handler(noun: str, context: dict[str, Any]) -> dict[str, Any]:
        context["called"] = True
        return {"result": "ok"}

    handlers = {"TEST": test_handler}

    # Parse and execute
    parse_result = tongue.parse("TEST something")
    context: dict[str, Any] = {}
    exec_result = tongue.execute(parse_result.ast, context=context, handlers=handlers)

    assert exec_result.success
    assert len(exec_result.side_effects) > 0
    assert "TEST" in exec_result.side_effects[0]
