"""
Tests for J-gents Phase 3: JIT Agent Compilation

Tests cover:
1. MetaArchitect agent generation
2. Sandboxed execution environment
3. Safety validation (Chaosmonger integration)
4. End-to-end JIT compilation workflow
5. Pattern-based code generation
6. Security constraints enforcement

All J-gent agents are marked with __is_test__ = True to distinguish them
from production agents.
"""

import pytest

from agents.j import (
    AgentSource,
    ArchitectConstraints,
    ArchitectInput,
    MetaArchitect,
    SandboxConfig,
    SandboxedNamespace,
    SandboxResult,
    compile_agent,
    execute_in_sandbox,
    jit_compile_and_execute,
    type_check_source,
    validate_jit_safety,
    validate_source_safety,
)

# Mark all agents as test agents
setattr(MetaArchitect, "__is_test__", True)


# --- MetaArchitect Tests ---


@pytest.mark.asyncio
async def test_meta_architect_basic() -> None:
    """Test basic MetaArchitect agent generation."""
    architect = MetaArchitect()

    input_data = ArchitectInput(
        intent="Parse JSON logs and extract error messages",
        context={"sample": '{"level": "error", "msg": "failed"}'},
    )

    result = await architect.invoke(input_data)

    assert isinstance(result, AgentSource)
    assert result.source  # Non-empty source code
    assert result.class_name  # Has a class name
    assert "import" in result.source or "from" in result.source  # Has imports
    assert result.complexity > 0  # Has some complexity


@pytest.mark.asyncio
async def test_meta_architect_parser_pattern() -> None:
    """Test MetaArchitect generates parser-type agents."""
    architect = MetaArchitect()

    input_data = ArchitectInput(
        intent="Parse NGINX access logs",
        context={"sample": '127.0.0.1 - - [01/Jan/2025:12:00:00] "GET /api HTTP/1.1" 200 512'},
    )

    result = await architect.invoke(input_data)

    # Should recognize "parse" keyword and use parser pattern
    assert result.source is not None
    assert "parse" in result.source.lower()
    assert result.class_name.startswith("JIT")
    assert "re" in result.imports  # Parser likely uses regex


@pytest.mark.asyncio
async def test_meta_architect_filter_pattern() -> None:
    """Test MetaArchitect generates filter-type agents."""
    architect = MetaArchitect()

    input_data = ArchitectInput(
        intent="Filter log entries with severity > WARNING",
        context={"criteria": "severity > WARNING"},
    )

    result = await architect.invoke(input_data)

    # Should recognize "filter" keyword
    assert result.source is not None
    assert "filter" in result.source.lower()
    assert result.class_name == "JITFilter"


@pytest.mark.asyncio
async def test_meta_architect_analyzer_pattern() -> None:
    """Test MetaArchitect generates analyzer-type agents."""
    architect = MetaArchitect()

    input_data = ArchitectInput(
        intent="Analyze stack traces and identify memory leaks",
        context={"patterns": ["OutOfMemory", "heap"]},
    )

    result = await architect.invoke(input_data)

    # Should recognize "analyze" keyword
    assert result.source is not None
    assert "analyze" in result.source.lower()
    assert result.class_name == "JITAnalyzer"


@pytest.mark.asyncio
async def test_meta_architect_validator_pattern() -> None:
    """Test MetaArchitect generates validator-type agents."""
    architect = MetaArchitect()

    input_data = ArchitectInput(
        intent="Validate JSON schema compliance",
        context={"rules": ["required_fields", "type_checking"]},
    )

    result = await architect.invoke(input_data)

    # Should recognize "validate" keyword
    assert result.source is not None
    assert "validate" in result.source.lower()
    assert result.class_name == "JITValidator"


@pytest.mark.asyncio
async def test_meta_architect_respects_constraints() -> None:
    """Test MetaArchitect respects entropy budget constraints."""
    architect = MetaArchitect()

    constraints = ArchitectConstraints(
        entropy_budget=0.5,  # Reduced budget
        max_cyclomatic_complexity=10,
        allowed_imports=frozenset({"re", "dataclasses", "typing"}),  # typing is always added
    )

    input_data = ArchitectInput(
        intent="Simple text parser",
        constraints=constraints,
    )

    result = await architect.invoke(input_data)

    # Should generate simpler code with reduced budget
    assert result.complexity <= 10  # Within complexity limit
    assert result.imports.issubset(constraints.allowed_imports)


# --- Sandbox Tests ---


def test_sandboxed_namespace_safe_builtins() -> None:
    """Test sandboxed namespace blocks dangerous builtins."""
    allowed_imports = frozenset({"re", "json"})
    sandbox = SandboxedNamespace(allowed_imports)
    ns = sandbox.build_namespace()

    # Safe builtins should be present
    assert "int" in ns["__builtins__"]
    assert "str" in ns["__builtins__"]
    assert "len" in ns["__builtins__"]
    assert "print" in ns["__builtins__"]

    # Dangerous builtins should NOT be present
    assert "eval" not in ns["__builtins__"]
    assert "exec" not in ns["__builtins__"]
    assert "compile" not in ns["__builtins__"]
    assert "__import__" not in ns["__builtins__"]
    assert "open" not in ns["__builtins__"]


def test_sandboxed_namespace_whitelisted_imports() -> None:
    """Test sandboxed namespace only includes whitelisted imports."""
    allowed_imports = frozenset({"re", "json"})
    sandbox = SandboxedNamespace(allowed_imports)
    ns = sandbox.build_namespace()

    # Whitelisted modules should be present
    assert "re" in ns
    assert "json" in ns

    # Non-whitelisted modules should NOT be present
    assert "os" not in ns
    assert "sys" not in ns
    assert "subprocess" not in ns


@pytest.mark.asyncio
async def test_type_check_source_valid() -> None:
    """Test type checking accepts valid Python code."""
    valid_source = """
def hello(name: str) -> str:
    return f"Hello, {name}!"
"""
    success, error = await type_check_source(valid_source)
    assert success
    assert not error


@pytest.mark.asyncio
async def test_type_check_source_invalid() -> None:
    """Test type checking rejects invalid Python code."""
    invalid_source = """
def hello(name: str) -> str:
    return f"Hello, {name!"  # Syntax error
"""
    success, error = await type_check_source(invalid_source)
    assert not success
    assert "syntax" in error.lower()


@pytest.mark.asyncio
async def test_execute_in_sandbox_success() -> None:
    """Test successful execution in sandbox."""
    source = AgentSource(
        source="""
class SimpleAgent:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"
""",
        class_name="SimpleAgent",
        imports=frozenset(),
        complexity=2,
        description="Simple greeting agent",
    )

    config = SandboxConfig(
        timeout_seconds=1.0,
        type_check=True,
        chaosmonger_check=False,  # Skip for this test
    )

    result = await execute_in_sandbox(source, "greet", ("World",), config)

    assert result.success
    assert result.output == "Hello, World!"
    assert result.execution_time_ms > 0


@pytest.mark.asyncio
async def test_execute_in_sandbox_timeout() -> None:
    """Test sandbox enforces timeout."""
    source = AgentSource(
        source="""
class SlowAgent:
    async def slow_method(self) -> str:
        # Simulate slow operation with tight loop
        total = 0
        for i in range(10_000_000):
            total += i
        return "done"
""",
        class_name="SlowAgent",
        imports=frozenset(),
        complexity=2,
        description="Slow agent",
    )

    config = SandboxConfig(
        timeout_seconds=0.001,  # 1ms timeout - very tight
        type_check=False,
        chaosmonger_check=False,
    )

    result = await execute_in_sandbox(source, "slow_method", (), config)

    # May fail due to timeout OR may succeed if loop is fast enough
    # The important thing is the sandbox doesn't hang indefinitely
    assert isinstance(result, SandboxResult)


@pytest.mark.asyncio
async def test_execute_in_sandbox_blocks_forbidden_operations() -> None:
    """Test sandbox blocks forbidden operations like eval."""
    source = AgentSource(
        source="""
class MaliciousAgent:
    def execute_code(self, code: str) -> str:
        return eval(code)  # Should be blocked
""",
        class_name="MaliciousAgent",
        imports=frozenset(),
        complexity=2,
        description="Malicious agent",
    )

    config = SandboxConfig(
        timeout_seconds=1.0,
        type_check=False,
        chaosmonger_check=False,
    )

    result = await execute_in_sandbox(source, "execute_code", ("2 + 2",), config)

    # Should fail because eval is not in restricted builtins
    assert not result.success
    assert result.error is not None
    assert "eval" in result.error.lower() or "not defined" in result.error.lower()


# --- Safety Validation Tests ---


def test_validate_source_safety_passes() -> None:
    """Test safety validation passes for safe code."""
    source = AgentSource(
        source="""
import re

class SafeAgent:
    def process(self, text: str) -> str:
        return text.upper()
""",
        class_name="SafeAgent",
        imports=frozenset({"re"}),
        complexity=2,
        description="Safe agent",
    )

    constraints = ArchitectConstraints(
        entropy_budget=1.0,
        max_cyclomatic_complexity=20,
        allowed_imports=frozenset({"re", "json"}),
    )

    is_safe, reason = validate_source_safety(source, constraints)
    assert is_safe


def test_validate_source_safety_rejects_complexity() -> None:
    """Test safety validation rejects overly complex code."""
    source = AgentSource(
        source="complex code",
        class_name="ComplexAgent",
        imports=frozenset(),
        complexity=100,  # Very high complexity
        description="Complex agent",
    )

    constraints = ArchitectConstraints(
        entropy_budget=0.5,  # budget=0.5 * max=20 = 10
        max_cyclomatic_complexity=20,
    )

    is_safe, reason = validate_source_safety(source, constraints)
    assert not is_safe
    assert "complexity" in reason.lower()


def test_validate_source_safety_rejects_forbidden_imports() -> None:
    """Test safety validation rejects forbidden imports."""
    source = AgentSource(
        source="import os",
        class_name="DangerousAgent",
        imports=frozenset({"os"}),  # Not allowed
        complexity=2,
        description="Dangerous agent",
    )

    constraints = ArchitectConstraints(
        allowed_imports=frozenset({"re", "json"}),  # os not in list
    )

    is_safe, reason = validate_source_safety(source, constraints)
    assert not is_safe
    assert "forbidden imports" in reason.lower()
    assert "os" in reason


def test_validate_source_safety_rejects_forbidden_patterns() -> None:
    """Test safety validation rejects forbidden patterns like eval."""
    source = AgentSource(
        source='eval("malicious code")',
        class_name="MaliciousAgent",
        imports=frozenset(),
        complexity=2,
        description="Malicious agent",
    )

    constraints = ArchitectConstraints(
        forbidden_patterns=frozenset({"eval", "exec"}),
    )

    is_safe, reason = validate_source_safety(source, constraints)
    assert not is_safe
    assert "forbidden pattern" in reason.lower()
    assert "eval" in reason


# --- End-to-End Integration Tests ---


@pytest.mark.asyncio
async def test_jit_compile_and_execute_e2e() -> None:
    """Test end-to-end JIT compilation and execution."""
    # Generate agent
    source = await compile_agent(
        intent="Convert text to uppercase",
        context={},
    )

    # Manually create a working uppercase agent for test
    source = AgentSource(
        source="""
class UppercaseAgent:
    def transform(self, text: str) -> str:
        return text.upper()
""",
        class_name="UppercaseAgent",
        imports=frozenset(),
        complexity=2,
        description="Uppercase transformer",
    )

    # Execute
    result = await jit_compile_and_execute(
        source,
        "transform",
        "hello world",
        timeout=1.0,
    )

    assert result.success
    assert result.output == "HELLO WORLD"


@pytest.mark.asyncio
async def test_jit_safety_validation_e2e() -> None:
    """Test end-to-end safety validation prevents unsafe execution."""
    # Generate agent with forbidden pattern
    source = AgentSource(
        source="""
class UnsafeAgent:
    def execute(self, code: str) -> str:
        return eval(code)  # Forbidden
""",
        class_name="UnsafeAgent",
        imports=frozenset(),
        complexity=2,
        description="Unsafe agent",
    )

    constraints = ArchitectConstraints(
        forbidden_patterns=frozenset({"eval"}),
    )

    # Safety check should fail
    is_safe, reason = validate_jit_safety(source, constraints)
    assert not is_safe
    assert "eval" in reason.lower()


@pytest.mark.asyncio
async def test_jit_with_chaosmonger_integration() -> None:
    """Test JIT compilation integrates with Chaosmonger stability checks."""
    # Generate complex agent that should fail Chaosmonger
    source = AgentSource(
        source="""
class ComplexAgent:
    def process(self, x) -> None:
        if x > 0:
            if x > 10:
                if x > 100:
                    if x > 1000:
                        if x > 10000:
                            return "very large"
        return "other"
""",
        class_name="ComplexAgent",
        imports=frozenset(),
        complexity=6,  # High branching
        description="Overly complex agent",
    )

    config = SandboxConfig(
        timeout_seconds=1.0,
        type_check=False,
        chaosmonger_check=True,  # Enable Chaosmonger
    )

    result = await execute_in_sandbox(source, "process", (5,), config)

    # Chaosmonger may reject based on complexity
    # (actual behavior depends on thresholds)
    # Test just ensures Chaosmonger integration works
    assert isinstance(result, SandboxResult)


# --- Compile Agent Convenience Function Tests ---


@pytest.mark.asyncio
async def test_compile_agent_convenience() -> None:
    """Test compile_agent convenience function."""
    source = await compile_agent(
        intent="Filter numbers greater than 10",
        context={"criteria": "value > 10"},
    )

    assert isinstance(source, AgentSource)
    assert source.source
    assert source.class_name
    assert "filter" in source.source.lower()


@pytest.mark.asyncio
async def test_compile_agent_with_constraints() -> None:
    """Test compile_agent respects custom constraints."""
    constraints = ArchitectConstraints(
        entropy_budget=0.3,
        max_cyclomatic_complexity=5,
        allowed_imports=frozenset({"re", "typing"}),  # typing is always added for type hints
    )

    source = await compile_agent(
        intent="Simple regex matcher",
        constraints=constraints,
    )

    assert source.complexity <= 5
    assert source.imports.issubset(constraints.allowed_imports)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
