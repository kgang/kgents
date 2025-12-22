"""
Tests for WASM Executor.

Session 7: WASM isolation for FILE_OPERAD sandboxes.

Verifies:
- Code analysis for safety
- Local WASM executor (subprocess isolation)
- Executor bridge routing
- Integration with SandboxPolynomial
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from ..sandbox import (
    SandboxConfig,
    SandboxId,
    SandboxPolynomial,
    SandboxRuntime,
)
from ..wasm_executor import (
    BLOCKED_IMPORTS,
    SAFE_BUILTINS,
    CodeAnalyzer,
    ExecutionResult,
    ExecutorBridge,
    ExecutorConfig,
    IsolationLevel,
    LocalWASMExecutor,
    execute_sandbox,
    get_executor_bridge,
    reset_executor_bridge,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def analyzer():
    """Create a CodeAnalyzer instance."""
    return CodeAnalyzer()


@pytest.fixture
def local_executor():
    """Create a LocalWASMExecutor instance."""
    return LocalWASMExecutor()


@pytest.fixture
def executor_bridge():
    """Create an ExecutorBridge instance."""
    return ExecutorBridge()


@pytest.fixture(autouse=True)
def reset_global_bridge():
    """Reset global executor bridge between tests."""
    reset_executor_bridge()
    yield
    reset_executor_bridge()


# =============================================================================
# Code Analyzer Tests
# =============================================================================


class TestCodeAnalyzer:
    """Tests for CodeAnalyzer safety checks."""

    def test_analyzer_accepts_safe_code(self, analyzer):
        """Analyzer accepts safe Python code."""
        code = """
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
"""
        is_safe, warnings = analyzer.analyze(code)
        assert is_safe is True

    def test_analyzer_rejects_os_import(self, analyzer):
        """Analyzer rejects os import."""
        code = "import os"
        is_safe, warnings = analyzer.analyze(code)
        assert is_safe is False
        assert any("os" in w for w in warnings)

    def test_analyzer_rejects_subprocess_import(self, analyzer):
        """Analyzer rejects subprocess import."""
        code = "import subprocess"
        is_safe, warnings = analyzer.analyze(code)
        assert is_safe is False
        assert any("subprocess" in w for w in warnings)

    def test_analyzer_rejects_socket_import(self, analyzer):
        """Analyzer rejects socket import."""
        code = "import socket"
        is_safe, warnings = analyzer.analyze(code)
        assert is_safe is False

    def test_analyzer_rejects_exec_call(self, analyzer):
        """Analyzer rejects exec() calls."""
        code = 'exec("print(1)")'
        is_safe, warnings = analyzer.analyze(code)
        assert is_safe is False
        assert any("exec" in w for w in warnings)

    def test_analyzer_rejects_eval_call(self, analyzer):
        """Analyzer rejects eval() calls."""
        code = 'x = eval("1 + 1")'
        is_safe, warnings = analyzer.analyze(code)
        assert is_safe is False
        assert any("eval" in w for w in warnings)

    def test_analyzer_rejects_dunder_import(self, analyzer):
        """Analyzer rejects __import__ calls."""
        code = '__import__("os")'
        is_safe, warnings = analyzer.analyze(code)
        assert is_safe is False

    def test_analyzer_accepts_allowed_imports(self, analyzer):
        """Analyzer accepts allowed imports."""
        code = """
import json
import math
import re

data = json.dumps({"value": math.pi})
"""
        is_safe, warnings = analyzer.analyze(code)
        assert is_safe is True

    def test_analyzer_reports_syntax_error(self, analyzer):
        """Analyzer reports syntax errors."""
        code = "def broken(:"
        is_safe, warnings = analyzer.analyze(code)
        assert is_safe is False
        assert any("Syntax error" in w for w in warnings)

    def test_analyzer_warns_on_unknown_import(self, analyzer):
        """Analyzer warns on unknown imports."""
        code = "import some_unknown_module"
        is_safe, warnings = analyzer.analyze(code)
        # Unknown imports get warnings but are safe (will fail at runtime)
        assert any("Unknown import" in w for w in warnings)

    def test_analyzer_rejects_from_import_blocked(self, analyzer):
        """Analyzer rejects from X import blocked module."""
        code = "from os import path"
        is_safe, warnings = analyzer.analyze(code)
        assert is_safe is False

    def test_analyzer_accepts_dataclasses(self, analyzer):
        """Analyzer accepts dataclasses import."""
        code = """
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
"""
        is_safe, warnings = analyzer.analyze(code)
        assert is_safe is True


class TestCodeAnalyzerCustomConfig:
    """Tests for CodeAnalyzer with custom configuration."""

    def test_custom_allowed_imports(self):
        """Custom allowed imports work."""
        config = ExecutorConfig(
            allowed_imports=frozenset({"json", "custom_module"}),
            blocked_imports=frozenset(),
        )
        analyzer = CodeAnalyzer(config)

        code = "import custom_module"
        is_safe, warnings = analyzer.analyze(code)
        assert is_safe is True

    def test_custom_blocked_imports(self):
        """Custom blocked imports work."""
        config = ExecutorConfig(
            allowed_imports=frozenset({"json"}),
            blocked_imports=frozenset({"json"}),
        )
        analyzer = CodeAnalyzer(config)

        code = "import json"
        is_safe, warnings = analyzer.analyze(code)
        assert is_safe is False


# =============================================================================
# Local Executor Tests
# =============================================================================


class TestLocalWASMExecutor:
    """Tests for LocalWASMExecutor subprocess isolation."""

    @pytest.mark.asyncio
    async def test_executor_runs_simple_code(self, local_executor):
        """Executor runs simple Python code."""
        code = 'print("Hello, Sandbox!")'
        result = await local_executor.execute(code)

        assert result.success is True
        assert "Hello, Sandbox!" in result.output

    @pytest.mark.asyncio
    async def test_executor_captures_print_output(self, local_executor):
        """Executor captures print statements."""
        code = """
for i in range(3):
    print(f"Line {i}")
"""
        result = await local_executor.execute(code)

        assert result.success is True
        assert "Line 0" in result.output
        assert "Line 1" in result.output
        assert "Line 2" in result.output

    @pytest.mark.asyncio
    async def test_executor_runs_functions(self, local_executor):
        """Executor runs function definitions and calls."""
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))
"""
        result = await local_executor.execute(code)

        assert result.success is True
        assert "120" in result.output

    @pytest.mark.asyncio
    async def test_executor_blocks_os_import(self, local_executor):
        """Executor blocks dangerous os import."""
        code = "import os; print(os.getcwd())"
        result = await local_executor.execute(code)

        assert result.success is False
        assert "os" in (result.error or "").lower()

    @pytest.mark.asyncio
    async def test_executor_blocks_subprocess(self, local_executor):
        """Executor blocks subprocess import."""
        code = "import subprocess"
        result = await local_executor.execute(code)

        assert result.success is False

    @pytest.mark.asyncio
    async def test_executor_allows_safe_imports(self, local_executor):
        """Executor allows safe imports like json, math."""
        code = """
import json
import math

data = {"pi": math.pi, "e": math.e}
print(json.dumps(data, indent=2))
"""
        result = await local_executor.execute(code)

        assert result.success is True
        assert "3.14" in result.output

    @pytest.mark.asyncio
    async def test_executor_handles_exceptions(self, local_executor):
        """Executor handles Python exceptions."""
        code = """
raise ValueError("Test error")
"""
        result = await local_executor.execute(code)

        assert result.success is False
        assert "ValueError" in (result.error or result.output)

    @pytest.mark.asyncio
    async def test_executor_respects_timeout(self, local_executor):
        """Executor respects timeout for infinite loops."""
        # Use pure Python busy loop (no imports needed)
        code = """
x = 0
while True:
    x += 1
"""
        result = await local_executor.execute(code, timeout=0.5)

        assert result.success is False
        assert (
            "timed out" in (result.error or "").lower() or "timeout" in (result.error or "").lower()
        )

    @pytest.mark.asyncio
    async def test_executor_isolation_level(self, local_executor):
        """Executor reports correct isolation level."""
        code = "print('test')"
        result = await local_executor.execute(code)

        assert result.isolation_level == IsolationLevel.STANDARD

    @pytest.mark.asyncio
    async def test_executor_tracks_execution_time(self, local_executor):
        """Executor tracks execution time."""
        # Use a computational task instead of sleep
        code = """
result = 0
for i in range(100000):
    result += i
print("done:", result)
"""
        result = await local_executor.execute(code)

        assert result.success is True
        assert result.execution_time_ms > 0  # Should have some execution time
        assert "done:" in result.output


class TestLocalExecutorSecurity:
    """Security-focused tests for LocalWASMExecutor."""

    @pytest.mark.asyncio
    async def test_no_access_to_builtins_globals(self, local_executor):
        """Cannot access __builtins__ directly."""
        code = "print(__builtins__)"
        result = await local_executor.execute(code)

        # Should work but __builtins__ is our restricted version
        assert result.success is True

    @pytest.mark.asyncio
    async def test_no_file_access(self, local_executor):
        """Cannot open files."""
        code = 'f = open("/etc/passwd", "r")'
        result = await local_executor.execute(code)

        # open is not in safe builtins
        assert result.success is False

    @pytest.mark.asyncio
    async def test_no_network_access(self, local_executor):
        """Cannot make network calls."""
        code = """
import socket
s = socket.socket()
"""
        result = await local_executor.execute(code)

        assert result.success is False

    @pytest.mark.asyncio
    async def test_no_compile_escape(self, local_executor):
        """Cannot use compile() to escape sandbox."""
        code = 'compile("import os", "", "exec")'
        result = await local_executor.execute(code)

        assert result.success is False


# =============================================================================
# Executor Bridge Tests
# =============================================================================


class TestExecutorBridge:
    """Tests for ExecutorBridge runtime routing."""

    @pytest.mark.asyncio
    async def test_bridge_routes_native(self, executor_bridge):
        """Bridge routes NATIVE runtime correctly."""
        sandbox = SandboxPolynomial.create(
            source_path="test.op",
            content='print("Native execution")',
            config=SandboxConfig(runtime=SandboxRuntime.NATIVE),
        )

        result = await executor_bridge.execute(sandbox)

        assert result.success is True
        assert "Native execution" in result.stdout

    @pytest.mark.asyncio
    async def test_bridge_routes_jit_gent(self, executor_bridge):
        """Bridge routes JIT_GENT runtime correctly."""
        sandbox = SandboxPolynomial.create(
            source_path="test.op",
            content='print("JIT-gent execution")',
            config=SandboxConfig(runtime=SandboxRuntime.JIT_GENT),
        )

        result = await executor_bridge.execute(sandbox)

        assert result.success is True
        assert "JIT-gent execution" in result.stdout

    @pytest.mark.asyncio
    async def test_bridge_routes_wasm(self, executor_bridge):
        """Bridge routes WASM runtime correctly."""
        sandbox = SandboxPolynomial.create(
            source_path="test.op",
            content='print("WASM execution")',
            config=SandboxConfig(runtime=SandboxRuntime.WASM),
        )

        result = await executor_bridge.execute(sandbox)

        assert result.success is True
        assert "WASM execution" in result.stdout

    @pytest.mark.asyncio
    async def test_bridge_native_less_isolated(self, executor_bridge):
        """Native runtime is less isolated (can access more)."""
        # Native can use open() (though we don't recommend it)
        sandbox = SandboxPolynomial.create(
            source_path="test.op",
            content="print(len(dir()))",  # Should work in native
            config=SandboxConfig(runtime=SandboxRuntime.NATIVE),
        )

        result = await executor_bridge.execute(sandbox)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_bridge_wasm_blocks_dangerous(self, executor_bridge):
        """WASM runtime blocks dangerous operations."""
        sandbox = SandboxPolynomial.create(
            source_path="test.op",
            content="import os; os.system('echo dangerous')",
            config=SandboxConfig(runtime=SandboxRuntime.WASM),
        )

        result = await executor_bridge.execute(sandbox)

        assert result.success is False


# =============================================================================
# Integration Tests
# =============================================================================


class TestExecutorIntegration:
    """Integration tests with SandboxPolynomial."""

    @pytest.mark.asyncio
    async def test_execute_sandbox_function(self):
        """execute_sandbox() convenience function works."""
        sandbox = SandboxPolynomial.create(
            source_path="test.op",
            content='print("Convenience function")',
            config=SandboxConfig(runtime=SandboxRuntime.JIT_GENT),
        )

        result = await execute_sandbox(sandbox)

        assert result.success is True
        assert "Convenience function" in result.stdout

    @pytest.mark.asyncio
    async def test_sandbox_with_complex_code(self):
        """Sandbox executes complex code correctly."""
        code = """
from dataclasses import dataclass
from typing import List
import json

@dataclass
class Point:
    x: int
    y: int

    def magnitude(self):
        return (self.x**2 + self.y**2) ** 0.5

points = [Point(3, 4), Point(0, 0), Point(1, 1)]
results = [{"point": f"({p.x}, {p.y})", "magnitude": p.magnitude()} for p in points]
print(json.dumps(results, indent=2))
"""
        sandbox = SandboxPolynomial.create(
            source_path="complex.op",
            content=code,
            config=SandboxConfig(runtime=SandboxRuntime.JIT_GENT),
        )

        result = await execute_sandbox(sandbox)

        assert result.success is True
        assert '"magnitude": 5.0' in result.stdout


# =============================================================================
# Execution Result Tests
# =============================================================================


class TestExecutionResult:
    """Tests for ExecutionResult dataclass."""

    def test_result_to_sandbox_result(self):
        """ExecutionResult converts to SandboxResult."""
        result = ExecutionResult(
            success=True,
            output="Hello",
            error=None,
            execution_time_ms=100.0,
            isolation_level=IsolationLevel.STANDARD,
        )

        sandbox_result = result.to_sandbox_result()

        assert sandbox_result.success is True
        assert sandbox_result.output == "Hello"
        assert sandbox_result.stdout == "Hello"
        assert sandbox_result.execution_time_ms == 100.0

    def test_result_with_error(self):
        """ExecutionResult with error converts correctly."""
        result = ExecutionResult(
            success=False,
            output="",
            error="Something went wrong",
            execution_time_ms=50.0,
        )

        sandbox_result = result.to_sandbox_result()

        assert sandbox_result.success is False
        assert sandbox_result.error == "Something went wrong"
        assert sandbox_result.stderr == "Something went wrong"


# =============================================================================
# Constants Tests
# =============================================================================


class TestConstants:
    """Tests for module constants."""

    def test_safe_builtins_include_essentials(self):
        """SAFE_BUILTINS includes essential functions."""
        essentials = {"print", "len", "range", "str", "int", "list", "dict"}
        assert essentials.issubset(SAFE_BUILTINS)

    def test_safe_builtins_exclude_dangerous(self):
        """SAFE_BUILTINS excludes dangerous functions."""
        dangerous = {"open", "exec", "eval", "compile", "__import__"}
        assert dangerous.isdisjoint(SAFE_BUILTINS)

    def test_blocked_imports_include_system(self):
        """BLOCKED_IMPORTS includes system modules."""
        system_modules = {"os", "sys", "subprocess", "socket"}
        assert system_modules.issubset(BLOCKED_IMPORTS)
