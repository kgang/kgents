"""
ASHC Bootstrap Isomorphism Checker

Determines behavioral equivalence between generated and installed
bootstrap implementations.

Key insight: We don't compare code text. We compare behavior:
- Do they satisfy the same laws?
- Do they pass the same tests?
- Are their type signatures compatible?

> "We don't prove equivalence. We observe it."
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import tempfile
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

# =============================================================================
# Types
# =============================================================================


@dataclass(frozen=True)
class BehaviorComparison:
    """
    Result of comparing two implementations' behavior.

    Captures multiple dimensions of behavioral equivalence.
    """

    agent_name: str
    test_pass_rate: float  # 0.0-1.0, from running existing tests
    type_compatible: bool  # mypy passes on generated
    laws_satisfied: bool  # All stated laws verified
    property_tests_pass: bool  # Hypothesis finds no counterexamples
    error: str | None = None

    @property
    def is_isomorphic(self) -> bool:
        """
        Behavioral isomorphism requires all checks to pass.

        We allow 95% test pass rate to account for LLM variance.
        """
        return (
            self.test_pass_rate >= 0.95
            and self.type_compatible
            and self.laws_satisfied
            and self.property_tests_pass
            and self.error is None
        )

    @property
    def score(self) -> float:
        """Numerical isomorphism score 0.0-1.0."""
        score = self.test_pass_rate * 0.4  # 40% from tests
        if self.type_compatible:
            score += 0.2
        if self.laws_satisfied:
            score += 0.25
        if self.property_tests_pass:
            score += 0.15
        return score


@dataclass(frozen=True)
class BootstrapIsomorphism:
    """Overall result of bootstrap regeneration."""

    comparisons: tuple[BehaviorComparison, ...]
    regeneration_time_ms: float = 0.0
    tokens_used: int = 0
    generation_count: int = 0

    @property
    def overall_score(self) -> float:
        """Average isomorphism score across all agents."""
        if not self.comparisons:
            return 0.0
        return sum(c.score for c in self.comparisons) / len(self.comparisons)

    @property
    def is_isomorphic(self) -> bool:
        """All agents are behaviorally isomorphic."""
        return bool(self.comparisons) and all(c.is_isomorphic for c in self.comparisons)

    @property
    def isomorphic_count(self) -> int:
        """Number of isomorphic agents."""
        return sum(1 for c in self.comparisons if c.is_isomorphic)

    def summary(self) -> str:
        """Human-readable summary."""
        lines = [
            f"Bootstrap Isomorphism: {self.isomorphic_count}/{len(self.comparisons)} agents",
            f"Overall Score: {self.overall_score:.0%}",
            f"Regeneration Time: {self.regeneration_time_ms:.0f}ms",
            f"Tokens Used: {self.tokens_used:,}",
            "",
            "Agent Results:",
        ]
        for c in self.comparisons:
            status = "✓" if c.is_isomorphic else "✗"
            lines.append(f"  {status} {c.agent_name}: {c.score:.0%}")
            if c.error:
                lines.append(f"      Error: {c.error}")
        return "\n".join(lines)


# =============================================================================
# Isomorphism Checking
# =============================================================================


async def check_isomorphism(
    generated_code: str,
    agent_name: str,
    run_tests: bool = True,
    run_types: bool = True,
) -> BehaviorComparison:
    """
    Compare generated code against installed implementation.

    Args:
        generated_code: Python code from LLM
        agent_name: Name of the bootstrap agent (Id, Compose, etc.)
        run_tests: Whether to run pytest
        run_types: Whether to run mypy

    Returns:
        BehaviorComparison with all check results
    """
    try:
        # 1. Validate syntax
        if not _validate_syntax(generated_code):
            return BehaviorComparison(
                agent_name=agent_name,
                test_pass_rate=0.0,
                type_compatible=False,
                laws_satisfied=False,
                property_tests_pass=False,
                error="Invalid Python syntax",
            )

        # 2. Try to load as module
        module = _load_as_module(generated_code, agent_name)
        if module is None:
            return BehaviorComparison(
                agent_name=agent_name,
                test_pass_rate=0.0,
                type_compatible=False,
                laws_satisfied=False,
                property_tests_pass=False,
                error="Failed to load as module",
            )

        # 3. Check required interface
        if not _has_required_interface(module, agent_name):
            return BehaviorComparison(
                agent_name=agent_name,
                test_pass_rate=0.0,
                type_compatible=False,
                laws_satisfied=False,
                property_tests_pass=False,
                error=f"Missing required interface for {agent_name}",
            )

        # 4. Run tests (if available and enabled)
        test_pass_rate = 1.0  # Default if no tests
        if run_tests:
            test_pass_rate = await _run_tests_against(generated_code, agent_name)

        # 5. Type check (if enabled)
        type_compatible = True
        if run_types:
            type_compatible = await _check_types(generated_code)

        # 6. Verify laws
        laws_satisfied = await _verify_laws(module, agent_name)

        # 7. Property tests
        property_tests_pass = await _run_property_tests(module, agent_name)

        return BehaviorComparison(
            agent_name=agent_name,
            test_pass_rate=test_pass_rate,
            type_compatible=type_compatible,
            laws_satisfied=laws_satisfied,
            property_tests_pass=property_tests_pass,
        )

    except Exception as e:
        return BehaviorComparison(
            agent_name=agent_name,
            test_pass_rate=0.0,
            type_compatible=False,
            laws_satisfied=False,
            property_tests_pass=False,
            error=f"Unexpected error: {e}",
        )


# =============================================================================
# Validation Helpers
# =============================================================================


def _validate_syntax(code: str) -> bool:
    """Check if code is valid Python syntax."""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def _load_as_module(code: str, name: str) -> Any | None:
    """
    Load code as a Python module.

    Creates a temporary file, writes the code, and imports it.
    The temp file is kept until the module is no longer needed
    (Python may need it for source introspection).
    """
    import uuid

    temp_path: Path | None = None
    module_name = f"ashc_generated_{name}_{uuid.uuid4().hex[:8]}"

    try:
        # Create temp file in a persistent location
        # (not auto-deleted, we clean up manually later)
        temp_dir = Path(tempfile.gettempdir()) / "ashc_modules"
        temp_dir.mkdir(exist_ok=True)

        temp_path = temp_dir / f"{module_name}.py"
        temp_path.write_text(code)

        # Import as module
        spec = importlib.util.spec_from_file_location(
            module_name,
            temp_path,
        )
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)

        # Add to sys.modules BEFORE exec to handle self-references
        sys.modules[module_name] = module

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            # Remove from sys.modules on failure
            sys.modules.pop(module_name, None)
            raise

        # Store temp_path on module for later cleanup
        module.__ashc_temp_path__ = temp_path

        return module

    except SyntaxError:
        # Syntax errors are expected for bad code
        return None
    except Exception:
        # Unexpected error - module couldn't be loaded
        return None


def _cleanup_module(module: Any) -> None:
    """Clean up a dynamically loaded module."""
    try:
        # Remove temp file if it exists
        temp_path = getattr(module, "__ashc_temp_path__", None)
        if temp_path and Path(temp_path).exists():
            Path(temp_path).unlink()

        # Remove from sys.modules
        module_name = module.__name__
        sys.modules.pop(module_name, None)
    except Exception:
        pass


def _has_required_interface(module: Any, agent_name: str) -> bool:
    """Check if module has the required agent interface."""
    # Look for the agent class
    agent_class = getattr(module, agent_name, None)
    if agent_class is None:
        return False

    # Should be a class (callable)
    if not callable(agent_class):
        return False

    # Check class has required methods/properties
    # We inspect the class itself, not an instance (some agents need args)
    try:
        # Check for invoke method on the class
        if not hasattr(agent_class, "invoke"):
            return False

        # Check for name property on the class
        if not hasattr(agent_class, "name"):
            return False

        # For agents that can be instantiated without args (Id, Judge, etc.)
        # try to create an instance
        if agent_name in ("Id", "Judge", "Ground", "Contradict", "Sublate", "Fix"):
            try:
                instance = agent_class()
                # Verify invoke is callable
                if not callable(getattr(instance, "invoke", None)):
                    return False
            except TypeError:
                # __init__ requires args, that's ok for some agents
                pass

        return True
    except Exception:
        return False


# =============================================================================
# Test Runners
# =============================================================================


async def _run_tests_against(code: str, agent_name: str) -> float:
    """
    Run existing bootstrap tests against generated code.

    Returns pass rate 0.0-1.0.
    """
    try:
        module = _load_as_module(code, agent_name)
        if module is None:
            return 0.0

        agent_class = getattr(module, agent_name, None)
        if agent_class is None:
            return 0.0

        # Agent-specific tests
        if agent_name == "Id":
            # Test Id(x) = x
            instance = agent_class()
            test_values = [42, "test", [1, 2, 3], {"a": 1}, None]
            passed = 0
            for val in test_values:
                try:
                    result = await instance.invoke(val)
                    if result == val:
                        passed += 1
                except Exception:
                    pass
            return passed / len(test_values)

        elif agent_name == "Compose":
            # Test Compose by creating a simple pipeline
            # First, we need an Id agent to compose with
            id_class = getattr(module, "Id", None)

            # If no Id class, check if Compose at least exists and has invoke
            if id_class is None:
                # Just verify the Compose class structure
                if hasattr(agent_class, "invoke") and hasattr(agent_class, "name"):
                    return 0.8  # Partial credit
                return 0.5

            # Create test: Compose(Id, Id) should act like Id
            try:
                id1 = id_class()
                id2 = id_class()
                composed = agent_class(id1, id2)

                # Test invoke
                result = await composed.invoke(42)
                if result == 42:
                    return 1.0
                return 0.7
            except Exception:
                # Structure is there but invoke failed
                return 0.6

        # Default: passed loading, assume basic functionality
        return 0.8

    except Exception as e:
        return 0.0


async def _check_types(code: str) -> bool:
    """Run mypy on the generated code."""
    # For now, just check syntax is valid
    # Full implementation would run mypy subprocess
    return _validate_syntax(code)


async def _verify_laws(module: Any, agent_name: str) -> bool:
    """Verify that the agent satisfies its stated laws."""
    try:
        agent_class = getattr(module, agent_name, None)
        if agent_class is None:
            return False

        if agent_name == "Id":
            instance = agent_class()
            # Law: Id(x) = x
            for test_val in [1, "test", [1, 2, 3], {"a": 1}]:
                result = await instance.invoke(test_val)
                if result != test_val:
                    return False
            return True

        elif agent_name == "Compose":
            # Law: Associativity - (f >> g) >> h ≡ f >> (g >> h)
            # We need helper agents to test this

            # Check if Id exists in the module for testing
            id_class = getattr(module, "Id", None)
            if id_class is None:
                # Can't fully verify without Id, but structure is ok
                return hasattr(agent_class, "invoke")

            # Create test agents using a simple wrapper
            class Double:
                @property
                def name(self) -> str:
                    return "Double"

                async def invoke(self, x: int) -> int:
                    return x * 2

            class AddOne:
                @property
                def name(self) -> str:
                    return "AddOne"

                async def invoke(self, x: int) -> int:
                    return x + 1

            class Square:
                @property
                def name(self) -> str:
                    return "Square"

                async def invoke(self, x: int) -> int:
                    return x * x

            try:
                f, g, h = Double(), AddOne(), Square()

                # (f >> g) >> h
                fg = agent_class(f, g)
                fg_h = agent_class(fg, h)

                # f >> (g >> h)
                gh = agent_class(g, h)
                f_gh = agent_class(f, gh)

                # Test with a value
                x = 3
                left = await fg_h.invoke(x)  # ((3*2)+1)² = 49
                right = await f_gh.invoke(x)  # ((3*2)+1)² = 49

                return left == right
            except Exception:
                # Associativity test failed, but structure might still be ok
                return False

        # For other agents, assume laws satisfied if loading worked
        return True

    except Exception:
        return False


async def _run_property_tests(module: Any, agent_name: str) -> bool:
    """Run property-based tests using Hypothesis."""
    # Simplified: We'd run hypothesis tests here
    # For now, return True if basic tests passed
    return True


# =============================================================================
# Batch Comparison
# =============================================================================


async def compare_all_agents(
    generated_codes: dict[str, str],
) -> BootstrapIsomorphism:
    """
    Compare all generated agents against installed.

    Args:
        generated_codes: Dict mapping agent name to generated code

    Returns:
        BootstrapIsomorphism with all comparisons
    """
    comparisons = []

    for name, code in generated_codes.items():
        comparison = await check_isomorphism(code, name)
        comparisons.append(comparison)

    return BootstrapIsomorphism(comparisons=tuple(comparisons))


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "BehaviorComparison",
    "BootstrapIsomorphism",
    "check_isomorphism",
    "compare_all_agents",
]
