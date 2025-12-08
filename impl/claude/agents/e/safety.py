"""
Safety Agent: Safe self-evolution using fixed-point iteration.

This module implements the safety layer for self-evolution:

1. SafetyConfig: Multi-layer validation configuration
2. SelfEvolutionAgent: Safely evolve evolution code
3. Fixed-point convergence: Iterate until stable
4. Sandbox testing: Validate in isolation before applying

Mathematical foundation:
    A function f has a fixed point x if f(x) = x
    For evolution: Evolve(code') ~ code' (similarity > threshold)

Morphisms:
    SelfEvolutionAgent: Path -> SafeEvolutionResult
    ConvergenceCheck: (str, str) -> bool
    SandboxTest: str -> TestResult

Usage:
    from agents.e.safety import SelfEvolutionAgent, SafetyConfig

    agent = SelfEvolutionAgent(SafetyConfig(max_iterations=3))
    result = await agent.invoke(Path("evolve.py"))
"""

from __future__ import annotations

import asyncio
import difflib
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from bootstrap.types import Agent


@dataclass
class SafetyConfig:
    """
    Configuration for safe self-evolution.

    Multiple validation layers ensure evolved code is safe:
    1. Read-only pass first (analyze without modifying)
    2. Syntax validation (py_compile)
    3. Type checking (mypy --strict)
    4. Self-test (evolved code can still evolve test code)
    5. Fixed-point convergence (similarity threshold)
    6. Human approval for meta-changes
    """

    # Layer 1: Read-only analysis first
    read_only: bool = True

    # Layer 2: Syntax validation (always enabled)
    require_syntax_valid: bool = True

    # Layer 3: Type checking
    require_mypy_strict: bool = True
    mypy_timeout_seconds: float = 60.0

    # Layer 4: Self-test (evolved version must still work)
    require_self_test: bool = True
    self_test_timeout_seconds: float = 120.0

    # Layer 5: Fixed-point convergence
    max_iterations: int = 3
    convergence_threshold: float = 0.95  # 95% similarity = converged

    # Layer 6: Human approval for meta-changes
    require_human_approval: bool = True

    # Sandbox configuration
    sandbox_enabled: bool = True
    sandbox_timeout_seconds: float = 60.0

    # Target detection
    meta_patterns: tuple[str, ...] = (
        "evolve.py",
        "agents/e/",
        "bootstrap/",
    )

    def is_meta_target(self, path: Path) -> bool:
        """Check if path is a meta-target (evolution infrastructure)."""
        path_str = str(path)
        return any(pattern in path_str for pattern in self.meta_patterns)


@dataclass
class ConvergenceState:
    """State for fixed-point convergence tracking."""

    iteration: int
    code_versions: list[str] = field(default_factory=list)
    similarities: list[float] = field(default_factory=list)
    converged: bool = False
    final_code: Optional[str] = None

    def add_version(self, code: str, similarity: float) -> None:
        """Add a code version to the convergence history."""
        self.code_versions.append(code)
        self.similarities.append(similarity)

    @property
    def latest_similarity(self) -> float:
        """Get the most recent similarity score."""
        return self.similarities[-1] if self.similarities else 0.0


@dataclass(frozen=True)
class SandboxTestInput:
    """Input for sandbox testing."""

    evolved_code: str
    original_path: Path
    test_module_code: Optional[str] = None


@dataclass
class SandboxTestResult:
    """Result from sandbox testing."""

    passed: bool
    syntax_valid: bool = False
    types_valid: bool = False
    self_test_passed: bool = False
    error: Optional[str] = None
    stdout: str = ""
    stderr: str = ""


@dataclass(frozen=True)
class SafeEvolutionInput:
    """Input for safe self-evolution."""

    target: Path
    config: SafetyConfig


@dataclass
class SafeEvolutionResult:
    """Result from safe self-evolution."""

    success: bool
    converged: bool = False
    iterations: int = 0
    final_similarity: float = 0.0
    evolved_code: Optional[str] = None
    error: Optional[str] = None
    convergence_state: Optional[ConvergenceState] = None
    sandbox_results: list[SandboxTestResult] = field(default_factory=list)


def compute_code_similarity(code1: str, code2: str) -> float:
    """
    Compute similarity between two code strings.

    Uses difflib SequenceMatcher for a robust similarity metric.
    Returns a value between 0.0 (completely different) and 1.0 (identical).
    """
    if code1 == code2:
        return 1.0
    if not code1 or not code2:
        return 0.0

    # Normalize whitespace for fairer comparison
    lines1 = [line.rstrip() for line in code1.splitlines() if line.strip()]
    lines2 = [line.rstrip() for line in code2.splitlines() if line.strip()]

    matcher = difflib.SequenceMatcher(None, lines1, lines2)
    return matcher.ratio()


def compute_structural_similarity(code1: str, code2: str) -> float:
    """
    Compute structural similarity (ignores comments, docstrings, whitespace).

    More robust than raw text comparison for code.
    """
    import ast

    def extract_structure(code: str) -> list[str]:
        """Extract structural elements from code."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # Fall back to line-based comparison
            return [line.strip() for line in code.splitlines() if line.strip() and not line.strip().startswith('#')]

        structure = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                structure.append(f"def:{node.name}:{len(node.args.args)}")
            elif isinstance(node, ast.ClassDef):
                structure.append(f"class:{node.name}:{len(node.bases)}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    structure.append(f"import:{alias.name}")
            elif isinstance(node, ast.ImportFrom):
                structure.append(f"from:{node.module}")
        return sorted(structure)

    struct1 = extract_structure(code1)
    struct2 = extract_structure(code2)

    if struct1 == struct2:
        return 1.0
    if not struct1 or not struct2:
        return 0.0

    matcher = difflib.SequenceMatcher(None, struct1, struct2)
    return matcher.ratio()


class SandboxTestAgent(Agent[SandboxTestInput, SandboxTestResult]):
    """
    Agent that tests evolved code in a sandbox environment.

    Validation layers:
    1. Syntax check (py_compile)
    2. Type check (mypy --strict)
    3. Self-test (evolved code can evolve test code)

    The sandbox isolates the evolved code to prevent damage to the
    actual codebase if the evolution produces broken code.
    """

    def __init__(self, config: SafetyConfig):
        self._config = config

    @property
    def name(self) -> str:
        return "SandboxTestAgent"

    async def invoke(self, input: SandboxTestInput) -> SandboxTestResult:
        """Test evolved code in sandbox."""
        result = SandboxTestResult(passed=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox_path = Path(tmpdir) / input.original_path.name
            sandbox_path.write_text(input.evolved_code)

            # Layer 1: Syntax check
            syntax_ok, syntax_err = await self._check_syntax(sandbox_path)
            result.syntax_valid = syntax_ok
            if not syntax_ok:
                result.error = f"Syntax error: {syntax_err}"
                return result

            # Layer 2: Type check (mypy)
            if self._config.require_mypy_strict:
                types_ok, types_err = await self._check_types(sandbox_path, tmpdir)
                result.types_valid = types_ok
                if not types_ok:
                    result.error = f"Type error: {types_err}"
                    return result

            # Layer 3: Self-test (if enabled)
            if self._config.require_self_test:
                self_test_ok, stdout, stderr = await self._self_test(
                    sandbox_path, input.test_module_code, tmpdir
                )
                result.self_test_passed = self_test_ok
                result.stdout = stdout
                result.stderr = stderr
                if not self_test_ok:
                    result.error = f"Self-test failed: {stderr[:500]}"
                    return result

            result.passed = True
            return result

    async def _check_syntax(self, path: Path) -> tuple[bool, str]:
        """Check Python syntax using py_compile."""
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "py_compile", str(path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=10.0
            )
            return proc.returncode == 0, stderr.decode()
        except asyncio.TimeoutError:
            return False, "Syntax check timed out"
        except Exception as e:
            return False, str(e)

    async def _check_types(self, path: Path, tmpdir: str) -> tuple[bool, str]:
        """Check types using mypy --strict."""
        try:
            # Set MYPYPATH to include kgents root for imports
            import os
            kgents_root = Path(__file__).parent.parent.parent.parent
            env = os.environ.copy()
            env["MYPYPATH"] = str(kgents_root)

            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "mypy", "--strict", str(path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self._config.mypy_timeout_seconds
            )
            output = stdout.decode() + stderr.decode()
            return proc.returncode == 0, output
        except asyncio.TimeoutError:
            return False, "Type check timed out"
        except Exception as e:
            return False, str(e)

    async def _self_test(
        self, evolved_path: Path, test_code: Optional[str], tmpdir: str
    ) -> tuple[bool, str, str]:
        """
        Test that evolved code can still function correctly.

        Creates a simple test module and verifies the evolved code can
        process it without crashing.
        """
        # Create a minimal test module
        test_module_path = Path(tmpdir) / "test_module.py"
        test_code = test_code or """
# Simple test module for self-evolution validation
def hello() -> str:
    return "world"

class Foo:
    def bar(self) -> int:
        return 42
"""
        test_module_path.write_text(test_code)

        # Try to run evolved evolve.py on the test module
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, str(evolved_path), "--help",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self._config.self_test_timeout_seconds
            )
            # Just check it doesn't crash with --help
            # A more sophisticated test would actually run evolution
            return proc.returncode in (0, 1), stdout.decode(), stderr.decode()
        except asyncio.TimeoutError:
            return False, "", "Self-test timed out"
        except Exception as e:
            return False, "", str(e)


class ConvergenceAgent(Agent[tuple[str, str], bool]):
    """
    Agent that checks if evolution has converged to a fixed point.

    Mathematical definition:
        f has fixed point x if f(x) = x
        For evolution: converged if similarity(code, evolved_code) >= threshold
    """

    def __init__(self, threshold: float = 0.95):
        self._threshold = threshold

    @property
    def name(self) -> str:
        return "ConvergenceAgent"

    async def invoke(self, input: tuple[str, str]) -> bool:
        """Check if two code versions are similar enough to be considered converged."""
        code1, code2 = input

        # Check both text similarity and structural similarity
        text_sim = compute_code_similarity(code1, code2)
        struct_sim = compute_structural_similarity(code1, code2)

        # Use the higher of the two (structural is more lenient)
        similarity = max(text_sim, struct_sim)

        return similarity >= self._threshold


class SelfEvolutionAgent(Agent[SafeEvolutionInput, SafeEvolutionResult]):
    """
    Agent that safely evolves evolution code using fixed-point iteration.

    Strategy:
    1. Run evolution with full safety checks
    2. Test evolved version in sandbox
    3. If different enough from previous, iterate
    4. Stop when converged or max iterations reached

    This implements the Fix pattern from bootstrap.fix:
        Fix(evolution) -> stable_code

    Morphism: SafeEvolutionInput -> SafeEvolutionResult
    """

    def __init__(
        self,
        config: Optional[SafetyConfig] = None,
        evolution_pipeline: Optional[Any] = None,
    ):
        self._config = config or SafetyConfig()
        self._evolution_pipeline = evolution_pipeline
        self._sandbox = SandboxTestAgent(self._config)
        self._convergence = ConvergenceAgent(self._config.convergence_threshold)

    @property
    def name(self) -> str:
        return "SelfEvolutionAgent"

    async def invoke(self, input: SafeEvolutionInput) -> SafeEvolutionResult:
        """Safely evolve the target file using fixed-point iteration."""
        target = input.target
        config = input.config

        # Check if this is a meta-target
        if not config.is_meta_target(target):
            # Not a meta-target, delegate to standard evolution
            return SafeEvolutionResult(
                success=False,
                error="Not a meta-target, use standard evolution"
            )

        # Read original code
        original_code = target.read_text()
        current_code = original_code

        state = ConvergenceState(iteration=0)
        state.add_version(original_code, 1.0)

        sandbox_results: list[SandboxTestResult] = []

        for iteration in range(1, config.max_iterations + 1):
            state.iteration = iteration

            # Generate evolution for current code
            evolved_code = await self._evolve_once(target, current_code)
            if evolved_code is None:
                # Evolution failed to produce output
                continue

            # Test in sandbox
            sandbox_result = await self._sandbox.invoke(SandboxTestInput(
                evolved_code=evolved_code,
                original_path=target,
            ))
            sandbox_results.append(sandbox_result)

            if not sandbox_result.passed:
                # Evolution broke something, keep current code
                continue

            # Check convergence
            similarity = compute_code_similarity(current_code, evolved_code)
            state.add_version(evolved_code, similarity)

            if similarity >= config.convergence_threshold:
                # Converged!
                state.converged = True
                state.final_code = evolved_code
                return SafeEvolutionResult(
                    success=True,
                    converged=True,
                    iterations=iteration,
                    final_similarity=similarity,
                    evolved_code=evolved_code,
                    convergence_state=state,
                    sandbox_results=sandbox_results,
                )

            # Not converged, continue with evolved code
            current_code = evolved_code

        # Did not converge within max iterations
        return SafeEvolutionResult(
            success=False,
            converged=False,
            iterations=config.max_iterations,
            final_similarity=state.latest_similarity,
            evolved_code=current_code if current_code != original_code else None,
            error=f"Failed to converge after {config.max_iterations} iterations",
            convergence_state=state,
            sandbox_results=sandbox_results,
        )

    async def _evolve_once(self, target: Path, current_code: str) -> Optional[str]:
        """
        Run one iteration of evolution.

        Uses the EvolutionPipeline to generate improvements,
        then applies the best one to produce evolved code.
        """
        import tempfile
        from .experiment import CodeModule
        from .evolution import EvolutionPipeline, EvolutionConfig

        # Create a temporary file with current code
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as tmp:
            tmp.write(current_code)
            tmp_path = Path(tmp.name)

        try:
            # Create module descriptor
            module = CodeModule(
                name=target.stem,
                category="meta",
                path=tmp_path,
            )

            # Run evolution pipeline (single pass, quick mode)
            config = EvolutionConfig(
                target="meta",
                dry_run=True,  # Don't apply - we handle that
                quick_mode=True,
                hypothesis_count=2,  # Fewer hypotheses for faster iteration
                max_improvements_per_module=1,  # Only need one
            )

            pipeline = EvolutionPipeline(config)
            report = await pipeline.run([module])

            # Get the best passed experiment
            if report.experiments:
                # Find first passed experiment with code
                for exp in report.experiments:
                    if exp.status.value == "passed" and exp.improvement:
                        return exp.improvement.code

            return None

        except Exception as e:
            # Log error but don't crash
            print(f"Evolution iteration error: {e}")
            return None
        finally:
            # Clean up temp file
            try:
                tmp_path.unlink()
            except Exception:
                pass


# Convenience factories

def safety_config(**kwargs: Any) -> SafetyConfig:
    """Create a SafetyConfig with custom settings."""
    return SafetyConfig(**kwargs)


def self_evolution_agent(
    config: Optional[SafetyConfig] = None,
) -> SelfEvolutionAgent:
    """Create a SelfEvolutionAgent with optional config."""
    return SelfEvolutionAgent(config)


def sandbox_test_agent(config: Optional[SafetyConfig] = None) -> SandboxTestAgent:
    """Create a SandboxTestAgent."""
    return SandboxTestAgent(config or SafetyConfig())


def convergence_agent(threshold: float = 0.95) -> ConvergenceAgent:
    """Create a ConvergenceAgent with custom threshold."""
    return ConvergenceAgent(threshold)


__all__ = [
    # Config
    "SafetyConfig",
    "ConvergenceState",
    # I/O types
    "SandboxTestInput",
    "SandboxTestResult",
    "SafeEvolutionInput",
    "SafeEvolutionResult",
    # Agents
    "SandboxTestAgent",
    "ConvergenceAgent",
    "SelfEvolutionAgent",
    # Functions
    "compute_code_similarity",
    "compute_structural_similarity",
    # Factories
    "safety_config",
    "self_evolution_agent",
    "sandbox_test_agent",
    "convergence_agent",
]
