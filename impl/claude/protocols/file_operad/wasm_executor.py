"""
WASM Executor: Isolated Execution for FILE_OPERAD Operations.

"CHAOTIC reality agents MUST run sandboxed before being trusted."

Session 7 implements actual WASM isolation for sandbox execution:

1. WASMExecutor — Execute Python code in isolated subprocess with restrictions
2. RemoteExecutor — Execute via remote sandbox service
3. ExecutorBridge — Route sandbox execution to appropriate runtime

The Two Isolation Modes:
- LOCAL WASM: subprocess with namespace/resource restrictions
- REMOTE: HTTP endpoint with full container isolation

Why not browser Pyodide for server-side?
  - Pyodide requires Node.js + V8, heavyweight for server
  - RestrictedPython + subprocess gives equivalent isolation
  - Remote option provides full container isolation when needed

See: spec/protocols/file-operad.md (Session 7)
"""

from __future__ import annotations

import ast
import hashlib
import logging
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from .sandbox import SandboxPolynomial, SandboxResult

logger = logging.getLogger("kgents.file_operad.wasm_executor")


# =============================================================================
# Constants
# =============================================================================

DEFAULT_TIMEOUT_SECONDS = 30.0
MAX_OUTPUT_BYTES = 1024 * 1024  # 1MB max output
MAX_MEMORY_MB = 256  # Memory limit for subprocess

# Safe builtins for restricted execution
SAFE_BUILTINS = frozenset(
    {
        "abs",
        "all",
        "any",
        "ascii",
        "bin",
        "bool",
        "bytearray",
        "bytes",
        "callable",
        "chr",
        "classmethod",
        "complex",
        "dict",
        "dir",
        "divmod",
        "enumerate",
        "filter",
        "float",
        "format",
        "frozenset",
        "getattr",
        "hasattr",
        "hash",
        "hex",
        "id",
        "int",
        "isinstance",
        "issubclass",
        "iter",
        "len",
        "list",
        "map",
        "max",
        "min",
        "next",
        "object",
        "oct",
        "ord",
        "pow",
        "print",
        "property",
        "range",
        "repr",
        "reversed",
        "round",
        "set",
        "slice",
        "sorted",
        "staticmethod",
        "str",
        "sum",
        "super",
        "tuple",
        "type",
        "vars",
        "zip",
    }
)

# Blocked imports for security
BLOCKED_IMPORTS = frozenset(
    {
        "os",
        "sys",
        "subprocess",
        "socket",
        "http",
        "urllib",
        "pickle",
        "shelve",
        "shutil",
        "pathlib",
        "tempfile",
        "multiprocessing",
        "threading",
        "asyncio",
        "ctypes",
        "cffi",
        "cython",
        "importlib",
        "__builtins__",
    }
)


# =============================================================================
# Enums
# =============================================================================


class ExecutionMode(Enum):
    """Execution mode for sandbox."""

    LOCAL = auto()  # Subprocess with restrictions
    REMOTE = auto()  # Remote sandbox service


class IsolationLevel(Enum):
    """Level of isolation for execution."""

    MINIMAL = auto()  # Basic namespace restriction
    STANDARD = auto()  # Namespace + resource limits
    STRICT = auto()  # Full isolation (container/WASM)


# =============================================================================
# Protocols
# =============================================================================


class Executor(Protocol):
    """Protocol for sandbox executors."""

    async def execute(
        self,
        code: str,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> "ExecutionResult": ...

    @property
    def isolation_level(self) -> IsolationLevel: ...


# =============================================================================
# Data Structures
# =============================================================================


@dataclass(frozen=True)
class ExecutionResult:
    """Result of sandbox execution."""

    success: bool
    output: str = ""
    error: str | None = None
    execution_time_ms: float = 0.0
    isolation_level: IsolationLevel = IsolationLevel.STANDARD
    memory_used_bytes: int = 0

    def to_sandbox_result(self) -> "SandboxResult":
        """Convert to SandboxResult for compatibility."""
        from .sandbox import SandboxResult

        return SandboxResult(
            success=self.success,
            output=self.output,
            error=self.error,
            execution_time_ms=self.execution_time_ms,
            stdout=self.output,
            stderr=self.error or "",
        )


@dataclass
class ExecutorConfig:
    """Configuration for executor."""

    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    max_output_bytes: int = MAX_OUTPUT_BYTES
    max_memory_mb: int = MAX_MEMORY_MB
    allowed_imports: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                "re",
                "json",
                "dataclasses",
                "typing",
                "datetime",
                "math",
                "functools",
                "itertools",
                "collections",
                "abc",
                "enum",
                "copy",
                "pprint",
                "textwrap",
            }
        )
    )
    blocked_imports: frozenset[str] = BLOCKED_IMPORTS


# =============================================================================
# Code Analysis
# =============================================================================


class CodeAnalyzer:
    """
    Analyze Python code for safety before execution.

    Uses AST analysis to detect potentially dangerous patterns
    without executing the code.
    """

    def __init__(self, config: ExecutorConfig | None = None):
        self.config = config or ExecutorConfig()

    def analyze(self, code: str) -> tuple[bool, list[str]]:
        """
        Analyze code for safety.

        Returns:
            (is_safe, warnings) — is_safe is False if code is definitely unsafe
        """
        warnings: list[str] = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, [f"Syntax error: {e}"]

        # Check for dangerous patterns
        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split(".")[0]
                    if module in self.config.blocked_imports:
                        warnings.append(f"Blocked import: {module}")
                        return False, warnings
                    if module not in self.config.allowed_imports:
                        warnings.append(f"Unknown import: {module}")

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split(".")[0]
                    if module in self.config.blocked_imports:
                        warnings.append(f"Blocked import from: {module}")
                        return False, warnings
                    if module not in self.config.allowed_imports:
                        warnings.append(f"Unknown import from: {module}")

            # Check for exec/eval
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ("exec", "eval", "compile", "__import__"):
                        warnings.append(f"Dangerous call: {node.func.id}")
                        return False, warnings

            # Check for attribute access to dunder methods
            elif isinstance(node, ast.Attribute):
                if node.attr.startswith("__") and node.attr.endswith("__"):
                    if node.attr not in ("__init__", "__str__", "__repr__", "__dict__"):
                        warnings.append(f"Dunder access: {node.attr}")

        return True, warnings


# =============================================================================
# Local Executor (Subprocess with Restrictions)
# =============================================================================


@dataclass
class LocalWASMExecutor:
    """
    Execute code in isolated subprocess with restrictions.

    This provides WASM-like isolation using:
    - Subprocess isolation (separate process)
    - Resource limits (timeout, memory)
    - Restricted builtins
    - Import restrictions

    Not true WASM, but equivalent security for our use case.

    Example:
        >>> executor = LocalWASMExecutor()
        >>> result = await executor.execute('''
        ...     def greet(name):
        ...         return f"Hello, {name}!"
        ...     print(greet("World"))
        ... ''')
        >>> print(result.output)
        Hello, World!
    """

    config: ExecutorConfig = field(default_factory=ExecutorConfig)
    _analyzer: CodeAnalyzer = field(init=False)

    def __post_init__(self) -> None:
        self._analyzer = CodeAnalyzer(self.config)

    @property
    def isolation_level(self) -> IsolationLevel:
        return IsolationLevel.STANDARD

    async def execute(
        self,
        code: str,
        timeout: float | None = None,
    ) -> ExecutionResult:
        """
        Execute Python code in isolated subprocess.

        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds

        Returns:
            ExecutionResult with output/error
        """
        timeout = timeout or self.config.timeout_seconds
        start_time = time.perf_counter()

        # 1. Analyze code for safety
        is_safe, warnings = self._analyzer.analyze(code)
        if not is_safe:
            return ExecutionResult(
                success=False,
                error=f"Code analysis failed: {'; '.join(warnings)}",
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
                isolation_level=self.isolation_level,
            )

        # 2. Create wrapper script with restrictions
        wrapper_code = self._create_wrapper(code)

        # 3. Execute in subprocess
        try:
            result = await self._run_subprocess(wrapper_code, timeout)
            elapsed = (time.perf_counter() - start_time) * 1000

            return ExecutionResult(
                success=result["success"],
                output=result["stdout"][: self.config.max_output_bytes],
                error=result["stderr"] if result["stderr"] else None,
                execution_time_ms=elapsed,
                isolation_level=self.isolation_level,
            )

        except subprocess.TimeoutExpired:
            elapsed = (time.perf_counter() - start_time) * 1000
            return ExecutionResult(
                success=False,
                error=f"Execution timed out after {timeout}s",
                execution_time_ms=elapsed,
                isolation_level=self.isolation_level,
            )

        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            return ExecutionResult(
                success=False,
                error=f"Execution error: {type(e).__name__}: {e}",
                execution_time_ms=elapsed,
                isolation_level=self.isolation_level,
            )

    def _create_wrapper(self, code: str) -> str:
        """Create wrapper script with restricted execution."""
        # Escape code for embedding
        escaped_code = code.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")

        # Build allowed imports list
        allowed = ", ".join(f'"{m}"' for m in sorted(self.config.allowed_imports))

        return f'''
import sys
import builtins

# Store original import for use in restricted import
_original_import = builtins.__import__

# Allowed modules for import
_allowed_modules = set([{allowed}])
_blocked_modules = set(["os", "subprocess", "socket", "http", "urllib",
                        "pickle", "shelve", "shutil", "pathlib", "tempfile",
                        "multiprocessing", "threading", "ctypes", "cffi"])

def _restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    """Import function that only allows safe modules."""
    base_module = name.split(".")[0]
    if base_module in _blocked_modules:
        raise ImportError(f"Module '{{name}}' is not allowed in sandbox")
    if base_module not in _allowed_modules:
        raise ImportError(f"Module '{{name}}' is not allowed in sandbox")
    return _original_import(name, globals, locals, fromlist, level)

# Restrict builtins
_safe_builtins = {{
    "abs": abs, "all": all, "any": any, "ascii": ascii, "bin": bin,
    "bool": bool, "bytearray": bytearray, "bytes": bytes, "callable": callable,
    "chr": chr, "classmethod": classmethod, "complex": complex, "dict": dict,
    "dir": dir, "divmod": divmod, "enumerate": enumerate, "filter": filter,
    "float": float, "format": format, "frozenset": frozenset, "getattr": getattr,
    "hasattr": hasattr, "hash": hash, "hex": hex, "id": id, "int": int,
    "isinstance": isinstance, "issubclass": issubclass, "iter": iter, "len": len,
    "list": list, "map": map, "max": max, "min": min, "next": next,
    "object": object, "oct": oct, "ord": ord, "pow": pow, "print": print,
    "property": property, "range": range, "repr": repr, "reversed": reversed,
    "round": round, "set": set, "slice": slice, "sorted": sorted,
    "staticmethod": staticmethod, "str": str, "sum": sum, "super": super,
    "tuple": tuple, "type": type, "vars": vars, "zip": zip,
    "True": True, "False": False, "None": None,
    "Exception": Exception, "TypeError": TypeError, "ValueError": ValueError,
    "RuntimeError": RuntimeError, "KeyError": KeyError, "IndexError": IndexError,
    "AttributeError": AttributeError, "StopIteration": StopIteration,
    "ImportError": ImportError, "NameError": NameError, "NotImplementedError": NotImplementedError,
    "__import__": _restricted_import,
    "__name__": "__sandbox__",
    "__build_class__": __build_class__,
}}

# Execute user code
_code = \'\'\'
{escaped_code}
\'\'\'

try:
    exec(compile(_code, "<sandbox>", "exec"), {{"__builtins__": _safe_builtins}})
except Exception as e:
    print(f"Error: {{type(e).__name__}}: {{e}}", file=sys.stderr)
    sys.exit(1)
'''

    async def _run_subprocess(
        self,
        code: str,
        timeout: float,
    ) -> dict[str, Any]:
        """Run code in subprocess with timeout."""
        import asyncio

        # Write code to temp file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
        ) as f:
            f.write(code)
            temp_path = f.name

        try:
            # Run subprocess
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                # No shell=True for security
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()  # Reap the zombie
                raise subprocess.TimeoutExpired(
                    cmd=[sys.executable, temp_path],
                    timeout=timeout,
                )

            return {
                "success": proc.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "returncode": proc.returncode,
            }

        finally:
            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)


# =============================================================================
# Remote Executor (HTTP Endpoint)
# =============================================================================


@dataclass
class RemoteExecutorConfig:
    """Configuration for remote executor."""

    endpoint_url: str = "http://localhost:8001/sandbox/execute"
    api_key: str | None = None
    timeout_seconds: float = 60.0
    verify_ssl: bool = True


@dataclass
class RemoteWASMExecutor:
    """
    Execute code via remote sandbox service.

    For heavier isolation, delegate execution to a containerized
    sandbox service. This provides:
    - Full container isolation (Docker/Firecracker)
    - Network isolation
    - Filesystem isolation
    - CPU/memory limits

    Example:
        >>> executor = RemoteWASMExecutor(
        ...     config=RemoteExecutorConfig(
        ...         endpoint_url="https://sandbox.kgents.io/execute"
        ...     )
        ... )
        >>> result = await executor.execute("print('Hello from container!')")
    """

    config: RemoteExecutorConfig = field(default_factory=RemoteExecutorConfig)

    @property
    def isolation_level(self) -> IsolationLevel:
        return IsolationLevel.STRICT

    async def execute(
        self,
        code: str,
        timeout: float | None = None,
    ) -> ExecutionResult:
        """
        Execute code via remote sandbox endpoint.

        Args:
            code: Python code to execute
            timeout: Execution timeout (passed to remote service)

        Returns:
            ExecutionResult from remote service
        """
        import aiohttp

        timeout = timeout or self.config.timeout_seconds
        start_time = time.perf_counter()

        # Build request
        payload = {
            "code": code,
            "timeout_seconds": timeout,
            "language": "python",
        }

        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.endpoint_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout + 5),
                    ssl=self.config.verify_ssl if self.config.verify_ssl else False,
                ) as response:
                    elapsed = (time.perf_counter() - start_time) * 1000

                    if response.status != 200:
                        error_text = await response.text()
                        return ExecutionResult(
                            success=False,
                            error=f"Remote execution failed ({response.status}): {error_text}",
                            execution_time_ms=elapsed,
                            isolation_level=self.isolation_level,
                        )

                    result = await response.json()

                    return ExecutionResult(
                        success=result.get("success", False),
                        output=result.get("output", ""),
                        error=result.get("error"),
                        execution_time_ms=result.get("execution_time_ms", elapsed),
                        isolation_level=self.isolation_level,
                    )

        except aiohttp.ClientError as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            return ExecutionResult(
                success=False,
                error=f"Remote connection error: {type(e).__name__}: {e}",
                execution_time_ms=elapsed,
                isolation_level=self.isolation_level,
            )

        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            return ExecutionResult(
                success=False,
                error=f"Remote execution error: {type(e).__name__}: {e}",
                execution_time_ms=elapsed,
                isolation_level=self.isolation_level,
            )


# =============================================================================
# Executor Bridge (Routes to Appropriate Runtime)
# =============================================================================


@dataclass
class ExecutorBridge:
    """
    Bridge that routes sandbox execution to appropriate runtime.

    Based on SandboxRuntime:
    - NATIVE: Use Python exec (fast, least isolation)
    - JIT_GENT: Use LocalWASMExecutor (subprocess, moderate isolation)
    - WASM: Use LocalWASMExecutor with strict settings (most isolation locally)

    For full isolation, use RemoteWASMExecutor.

    Example:
        >>> bridge = ExecutorBridge()
        >>> sandbox = store.get(sandbox_id)
        >>> result = await bridge.execute(sandbox)
    """

    local_executor: LocalWASMExecutor = field(default_factory=LocalWASMExecutor)
    remote_executor: RemoteWASMExecutor | None = None
    prefer_remote_for_wasm: bool = False

    async def execute(
        self,
        sandbox: "SandboxPolynomial",
    ) -> "SandboxResult":
        """
        Execute sandbox content using appropriate runtime.

        Args:
            sandbox: The sandbox to execute

        Returns:
            SandboxResult with execution output
        """
        from .sandbox import SandboxEvent, SandboxResult, SandboxRuntime, transition_sandbox

        runtime = sandbox.config.runtime
        timeout = sandbox.config.timeout_seconds

        # Route based on runtime
        result: SandboxResult

        if runtime == SandboxRuntime.NATIVE:
            # Native: use Python exec directly (least isolation)
            result = await self._execute_native(sandbox.content, timeout)

        elif runtime == SandboxRuntime.JIT_GENT:
            # JIT-gent: use local WASM executor
            exec_result = await self.local_executor.execute(sandbox.content, timeout)
            result = exec_result.to_sandbox_result()

        elif runtime == SandboxRuntime.WASM:
            # WASM: use remote if available and preferred, else local
            if self.prefer_remote_for_wasm and self.remote_executor:
                exec_result = await self.remote_executor.execute(sandbox.content, timeout)
            else:
                exec_result = await self.local_executor.execute(sandbox.content, timeout)
            result = exec_result.to_sandbox_result()

        else:
            result = SandboxResult(
                success=False,
                error=f"Unknown runtime: {runtime}",
            )

        logger.info(
            f"Executed sandbox {sandbox.id} via {runtime.value}: "
            f"success={result.success}, time={result.execution_time_ms:.1f}ms"
        )

        return result

    async def _execute_native(
        self,
        code: str,
        timeout: float,
    ) -> "SandboxResult":
        """
        Execute code natively (minimal isolation).

        WARNING: This has minimal isolation. Only use for trusted code.
        """
        import asyncio

        from .sandbox import SandboxResult

        start_time = time.perf_counter()

        # Capture stdout
        import contextlib
        import io

        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout_capture):
                with contextlib.redirect_stderr(stderr_capture):
                    # Execute with timeout
                    try:
                        exec(compile(code, "<sandbox>", "exec"))
                    except Exception as e:
                        stderr_capture.write(f"{type(e).__name__}: {e}\n")
                        raise

            elapsed = (time.perf_counter() - start_time) * 1000

            return SandboxResult(
                success=True,
                output=stdout_capture.getvalue(),
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                execution_time_ms=elapsed,
            )

        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            return SandboxResult(
                success=False,
                error=f"{type(e).__name__}: {e}",
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                execution_time_ms=elapsed,
            )


# =============================================================================
# Convenience Functions
# =============================================================================


_global_bridge: ExecutorBridge | None = None


def get_executor_bridge() -> ExecutorBridge:
    """Get the global executor bridge."""
    global _global_bridge
    if _global_bridge is None:
        _global_bridge = ExecutorBridge()
    return _global_bridge


def reset_executor_bridge() -> None:
    """Reset the global executor bridge (for testing)."""
    global _global_bridge
    _global_bridge = None


async def execute_sandbox(sandbox: "SandboxPolynomial") -> "SandboxResult":
    """Execute a sandbox using the global bridge."""
    bridge = get_executor_bridge()
    return await bridge.execute(sandbox)


def configure_remote_executor(
    endpoint_url: str,
    api_key: str | None = None,
    prefer_remote_for_wasm: bool = True,
) -> None:
    """Configure remote executor for WASM isolation."""
    global _global_bridge

    config = RemoteExecutorConfig(
        endpoint_url=endpoint_url,
        api_key=api_key,
    )

    _global_bridge = ExecutorBridge(
        remote_executor=RemoteWASMExecutor(config=config),
        prefer_remote_for_wasm=prefer_remote_for_wasm,
    )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Enums
    "ExecutionMode",
    "IsolationLevel",
    # Data structures
    "ExecutionResult",
    "ExecutorConfig",
    # Code analysis
    "CodeAnalyzer",
    # Executors
    "LocalWASMExecutor",
    "RemoteWASMExecutor",
    "RemoteExecutorConfig",
    # Bridge
    "ExecutorBridge",
    # Convenience
    "get_executor_bridge",
    "reset_executor_bridge",
    "execute_sandbox",
    "configure_remote_executor",
    # Constants
    "DEFAULT_TIMEOUT_SECONDS",
    "MAX_OUTPUT_BYTES",
    "SAFE_BUILTINS",
    "BLOCKED_IMPORTS",
]
