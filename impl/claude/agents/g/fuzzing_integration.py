"""
G-gent Phase 6: T-gent Fuzzing Integration

This module integrates G-gent tongues with T-gent fuzzing and property-based testing.
It enables grammar-based test generation and property verification for tongues.

Key capabilities:
1. Grammar-based fuzzing: Generate valid, invalid, and boundary inputs from grammar
2. Property testing: Verify round-trip, idempotence, and constraint encoding
3. Adversarial testing: Discover grammar weaknesses and edge cases
4. Mutation testing: Inject semantic noise to verify robustness

Category Theoretic Definition:
    T: Tongue × Seed → FuzzReport
    P: Tongue × Property[] → PropertyTestReport
"""

from __future__ import annotations

import random
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agents.g.types import (
    Tongue,
    ParseResult,
    GrammarLevel,
    ConstraintProof,
    CounterExample,
)


# ============================================================================
# Fuzz Result Types
# ============================================================================


class FuzzInputType(Enum):
    """Type of fuzzed input."""

    VALID = "valid"  # Should parse successfully
    INVALID = "invalid"  # Should fail to parse
    BOUNDARY = "boundary"  # Edge cases (empty, max length, special chars)
    ADVERSARIAL = "adversarial"  # Injection/overflow attempts
    MUTATED = "mutated"  # Valid input with noise injected


@dataclass
class FuzzResult:
    """Result of a single fuzz test."""

    input_text: str
    input_type: FuzzInputType
    expected_success: bool
    actual_success: bool
    parse_result: ParseResult | None = None
    error: str | None = None

    @property
    def passed(self) -> bool:
        """Whether the fuzz test passed."""
        return self.expected_success == self.actual_success


@dataclass
class FuzzReport:
    """
    Comprehensive report from fuzzing a tongue.

    Tracks valid/invalid input generation and parse success rates.
    """

    tongue_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    results: list[FuzzResult] = field(default_factory=list)
    failures: list[FuzzResult] = field(default_factory=list)
    duration_ms: float = 0.0

    # Breakdown by input type
    valid_count: int = 0
    valid_passed: int = 0
    invalid_count: int = 0
    invalid_passed: int = 0
    boundary_count: int = 0
    boundary_passed: int = 0
    adversarial_count: int = 0
    adversarial_passed: int = 0

    @property
    def pass_rate(self) -> float:
        """Overall pass rate."""
        if self.total_tests == 0:
            return 0.0
        return self.passed_tests / self.total_tests

    @property
    def all_passed(self) -> bool:
        """Whether all tests passed."""
        return self.failed_tests == 0

    def summary(self) -> str:
        """Human-readable summary."""
        return (
            f"FuzzReport({self.tongue_name}): "
            f"{self.passed_tests}/{self.total_tests} passed "
            f"({self.pass_rate:.1%}) in {self.duration_ms:.0f}ms"
        )


# ============================================================================
# Property Test Types
# ============================================================================


class PropertyType(Enum):
    """Types of properties that can be tested."""

    ROUND_TRIP = "round_trip"  # parse(render(ast)) == ast
    IDEMPOTENCE = "idempotence"  # parse(text) == parse(render(parse(text)))
    CONSTRAINT = "constraint"  # Constraints are structurally enforced
    DETERMINISM = "determinism"  # Same input → same output
    COMPLETENESS = "completeness"  # All examples parse


@dataclass
class PropertyResult:
    """Result of testing a single property."""

    property_type: PropertyType
    property_name: str
    passed: bool
    total_cases: int
    passed_cases: int
    failed_cases: int
    failures: list[tuple[str, str]] = field(default_factory=list)  # (input, error)
    duration_ms: float = 0.0

    @property
    def pass_rate(self) -> float:
        """Pass rate for this property."""
        if self.total_cases == 0:
            return 0.0
        return self.passed_cases / self.total_cases


@dataclass
class PropertyTestReport:
    """
    Report from property-based testing of a tongue.
    """

    tongue_name: str
    total_properties: int
    passed_properties: int
    failed_properties: int
    results: list[PropertyResult] = field(default_factory=list)
    duration_ms: float = 0.0

    @property
    def all_passed(self) -> bool:
        """Whether all properties passed."""
        return self.failed_properties == 0

    def summary(self) -> str:
        """Human-readable summary."""
        return (
            f"PropertyTestReport({self.tongue_name}): "
            f"{self.passed_properties}/{self.total_properties} properties passed "
            f"in {self.duration_ms:.0f}ms"
        )


# ============================================================================
# Input Generators
# ============================================================================


class TongueInputGenerator:
    """
    Generate test inputs from a Tongue's grammar.

    Produces:
    - Valid inputs (should parse)
    - Invalid inputs (should fail)
    - Boundary inputs (edge cases)
    - Adversarial inputs (attacks)
    """

    def __init__(self, tongue: Tongue, seed: int | None = None):
        self.tongue = tongue
        self.rng = random.Random(seed)
        self._verbs: list[str] = []
        self._extract_grammar_elements()

    def _extract_grammar_elements(self) -> None:
        """Extract verbs and other elements from grammar."""
        grammar = self.tongue.grammar

        # Extract verbs from BNF grammar
        quoted = re.findall(r'"([A-Z]+)"', grammar)
        unquoted = re.findall(r"\b([A-Z]{2,})\b", grammar)
        self._verbs = sorted(set(quoted + unquoted))

    def generate_valid(self, count: int) -> list[str]:
        """Generate valid inputs that should parse successfully."""
        inputs = []

        if self.tongue.level == GrammarLevel.COMMAND:
            inputs.extend(self._generate_valid_commands(count))
        elif self.tongue.level == GrammarLevel.SCHEMA:
            inputs.extend(self._generate_valid_schemas(count))
        elif self.tongue.level == GrammarLevel.RECURSIVE:
            inputs.extend(self._generate_valid_recursive(count))

        # Include examples from tongue
        for example in self.tongue.examples:
            if len(inputs) < count:
                inputs.append(example.text)

        return inputs[:count]

    def _generate_valid_commands(self, count: int) -> list[str]:
        """Generate valid VERB NOUN commands."""
        inputs = []
        nouns = [
            "task",
            "meeting",
            "event",
            "item",
            "entry",
            "record",
            "file",
            "document",
            "today",
            "tomorrow",
            "2024-12-15",
            "/path/to/file.txt",
            "user@example.com",
        ]

        for _ in range(count):
            if self._verbs:
                verb = self.rng.choice(self._verbs)
                noun = self.rng.choice(nouns)
                inputs.append(f"{verb} {noun}")

        return inputs

    def _generate_valid_schemas(self, count: int) -> list[str]:
        """Generate valid JSON schema inputs."""
        import json

        inputs = []

        # Simple schema templates
        templates = [
            {"name": "test", "value": 42},
            {"id": 1, "title": "Example"},
            {"type": "item", "data": {}},
        ]

        for i in range(count):
            template = self.rng.choice(templates).copy()
            template["id"] = i
            inputs.append(json.dumps(template))

        return inputs

    def _generate_valid_recursive(self, count: int) -> list[str]:
        """Generate valid S-expressions."""
        inputs = []

        operators = ["add", "sub", "mul", "div", "and", "or", "not"]
        atoms = ["1", "2", "3", "x", "y", "z", "true", "false"]

        for _ in range(count):
            depth = self.rng.randint(1, 3)
            expr = self._generate_sexpr(operators, atoms, depth)
            inputs.append(expr)

        return inputs

    def _generate_sexpr(
        self, operators: list[str], atoms: list[str], depth: int
    ) -> str:
        """Generate random S-expression."""
        if depth <= 0:
            return self.rng.choice(atoms)

        op = self.rng.choice(operators)
        num_args = self.rng.randint(1, 3)
        args = [
            self._generate_sexpr(operators, atoms, depth - 1) for _ in range(num_args)
        ]
        return f"({op} {' '.join(args)})"

    def generate_invalid(self, count: int) -> list[str]:
        """Generate invalid inputs that should fail to parse."""
        inputs = []

        # Wrong verbs
        wrong_verbs = ["BLARG", "ZZZZ", "FAKE", "NOPE", "12345"]
        for verb in wrong_verbs[:count]:
            inputs.append(f"{verb} something")

        # Malformed commands
        malformed = [
            "",  # Empty
            "   ",  # Whitespace only
            "no verb here",  # No valid verb
            "VERB",  # Missing noun (if required)
            "123 456",  # Numbers only
            "!@#$%",  # Special chars only
        ]
        inputs.extend(malformed[: count - len(inputs)])

        return inputs[:count]

    def generate_boundary(self, count: int) -> list[str]:
        """Generate boundary/edge case inputs."""
        inputs = []

        if self._verbs:
            verb = self._verbs[0]

            # Edge cases
            edges = [
                "",  # Empty
                " ",  # Single space
                f"{verb}",  # Verb only (no space/noun)
                f"{verb} ",  # Verb with trailing space
                f" {verb} noun",  # Leading space
                f"{verb}  noun",  # Double space
                f"{verb} " + "a" * 1000,  # Very long noun
                f"{verb} " + "x",  # Single char noun
                f"{verb.lower()} noun",  # Lowercase verb
                f"{verb} 日本語",  # Unicode
                f"{verb} emoji\U0001f600",  # Emoji
            ]
            inputs.extend(edges)

        return inputs[:count]

    def generate_adversarial(self, count: int) -> list[str]:
        """Generate adversarial inputs (injection attempts, etc.)."""
        if not self._verbs:
            return []

        verb = self._verbs[0]

        adversarial = [
            # SQL injection
            f"{verb} '; DROP TABLE users; --",
            f"{verb} 1 OR 1=1",
            # Command injection
            f"{verb} ; rm -rf /",
            f"{verb} `whoami`",
            f"{verb} $(cat /etc/passwd)",
            # Path traversal
            f"{verb} ../../../etc/passwd",
            f"{verb} ..\\..\\windows\\system32",
            # Buffer overflow
            f"{verb} " + "A" * 10000,
            # XSS
            f'{verb} <script>alert("XSS")</script>',
            f"{verb} javascript:alert(1)",
            # Null bytes
            f"{verb} test\x00.txt",
            # Format strings
            f"{verb} %s%s%s%s%s",
            f"{verb} %n%n%n%n%n",
        ]

        return adversarial[:count]

    def generate_mutated(self, valid_inputs: list[str], count: int) -> list[str]:
        """Generate mutated versions of valid inputs."""
        if not valid_inputs:
            return []

        mutations = []

        for _ in range(count):
            original = self.rng.choice(valid_inputs)
            mutated = self._mutate(original)
            mutations.append(mutated)

        return mutations

    def _mutate(self, text: str) -> str:
        """Apply random mutation to text."""
        mutations = [
            self._swap_case,
            self._add_typo,
            self._add_whitespace,
            self._remove_char,
            self._duplicate_char,
        ]

        mutation = self.rng.choice(mutations)
        return mutation(text)

    def _swap_case(self, text: str) -> str:
        """Swap case of random character."""
        if not text:
            return text
        i = self.rng.randint(0, len(text) - 1)
        char = text[i]
        swapped = char.swapcase() if char.isalpha() else char
        return text[:i] + swapped + text[i + 1 :]

    def _add_typo(self, text: str) -> str:
        """Add typo (adjacent key press)."""
        if not text:
            return text
        keyboard = {
            "a": "s",
            "s": "a",
            "d": "f",
            "f": "d",
            "e": "r",
            "r": "e",
        }
        i = self.rng.randint(0, len(text) - 1)
        char = text[i].lower()
        typo = keyboard.get(char, char)
        return text[:i] + typo + text[i + 1 :]

    def _add_whitespace(self, text: str) -> str:
        """Add extra whitespace."""
        if not text:
            return text
        i = self.rng.randint(0, len(text))
        return text[:i] + " " + text[i:]

    def _remove_char(self, text: str) -> str:
        """Remove random character."""
        if len(text) <= 1:
            return text
        i = self.rng.randint(0, len(text) - 1)
        return text[:i] + text[i + 1 :]

    def _duplicate_char(self, text: str) -> str:
        """Duplicate random character."""
        if not text:
            return text
        i = self.rng.randint(0, len(text) - 1)
        return text[:i] + text[i] + text[i:]


# ============================================================================
# TongueFuzzer
# ============================================================================


class TongueFuzzer:
    """
    Fuzz-test a tongue for robustness.

    Uses the tongue's grammar to generate valid, invalid, boundary,
    and adversarial inputs, then verifies the parser behaves correctly.
    """

    def __init__(
        self,
        tongue: Tongue,
        seed: int | None = None,
        valid_count: int = 50,
        invalid_count: int = 25,
        boundary_count: int = 25,
        adversarial_count: int = 25,
    ):
        self.tongue = tongue
        self.seed = seed
        self.generator = TongueInputGenerator(tongue, seed)

        self.valid_count = valid_count
        self.invalid_count = invalid_count
        self.boundary_count = boundary_count
        self.adversarial_count = adversarial_count

    def fuzz(self) -> FuzzReport:
        """
        Run full fuzz testing suite.

        Returns FuzzReport with all results.
        """
        start = time.time()
        results: list[FuzzResult] = []
        failures: list[FuzzResult] = []

        # Counts
        valid_passed = 0
        invalid_passed = 0
        boundary_passed = 0
        adversarial_passed = 0

        # Generate and test valid inputs
        valid_inputs = self.generator.generate_valid(self.valid_count)
        for text in valid_inputs:
            result = self._test_input(text, FuzzInputType.VALID, expected_success=True)
            results.append(result)
            if result.passed:
                valid_passed += 1
            else:
                failures.append(result)

        # Generate and test invalid inputs
        invalid_inputs = self.generator.generate_invalid(self.invalid_count)
        for text in invalid_inputs:
            result = self._test_input(
                text, FuzzInputType.INVALID, expected_success=False
            )
            results.append(result)
            if result.passed:
                invalid_passed += 1
            else:
                failures.append(result)

        # Generate and test boundary inputs
        boundary_inputs = self.generator.generate_boundary(self.boundary_count)
        for text in boundary_inputs:
            # Boundary inputs: we don't know if they should pass, so just record
            result = self._test_input(
                text, FuzzInputType.BOUNDARY, expected_success=None
            )  # type: ignore
            results.append(result)
            boundary_passed += 1  # Boundaries always "pass" (we're observing)

        # Generate and test adversarial inputs
        adversarial_inputs = self.generator.generate_adversarial(self.adversarial_count)
        for text in adversarial_inputs:
            result = self._test_input(
                text, FuzzInputType.ADVERSARIAL, expected_success=False
            )
            results.append(result)
            if result.passed:
                adversarial_passed += 1
            else:
                failures.append(result)

        duration_ms = (time.time() - start) * 1000

        return FuzzReport(
            tongue_name=self.tongue.name,
            total_tests=len(results),
            passed_tests=sum(1 for r in results if r.passed),
            failed_tests=len(failures),
            results=results,
            failures=failures,
            duration_ms=duration_ms,
            valid_count=len(valid_inputs),
            valid_passed=valid_passed,
            invalid_count=len(invalid_inputs),
            invalid_passed=invalid_passed,
            boundary_count=len(boundary_inputs),
            boundary_passed=boundary_passed,
            adversarial_count=len(adversarial_inputs),
            adversarial_passed=adversarial_passed,
        )

    def _test_input(
        self, text: str, input_type: FuzzInputType, expected_success: bool | None
    ) -> FuzzResult:
        """Test a single input."""
        try:
            parse_result = self.tongue.parse(text)
            actual_success = parse_result.success

            # For boundary tests, we observe without expectation
            if expected_success is None:
                expected_success = actual_success

            return FuzzResult(
                input_text=text,
                input_type=input_type,
                expected_success=expected_success,
                actual_success=actual_success,
                parse_result=parse_result,
            )
        except Exception as e:
            return FuzzResult(
                input_text=text,
                input_type=input_type,
                expected_success=expected_success
                if expected_success is not None
                else False,
                actual_success=False,
                error=str(e),
            )


# ============================================================================
# TonguePropertyTester
# ============================================================================


class TonguePropertyTester:
    """
    Property-based testing for tongues.

    Tests algebraic properties:
    1. Round-trip: parse(render(ast)) == ast
    2. Idempotence: parse(text) == parse(render(parse(text)))
    3. Constraint encoding: forbidden inputs don't parse
    4. Determinism: same input → same output
    5. Completeness: all examples parse
    """

    def __init__(
        self, tongue: Tongue, seed: int | None = None, cases_per_property: int = 50
    ):
        self.tongue = tongue
        self.seed = seed
        self.cases_per_property = cases_per_property
        self.generator = TongueInputGenerator(tongue, seed)

    def test_all_properties(self) -> PropertyTestReport:
        """
        Run all property tests.

        Returns PropertyTestReport with results for each property.
        """
        start = time.time()
        results: list[PropertyResult] = []

        # Test each property
        results.append(self.test_round_trip())
        results.append(self.test_idempotence())
        results.append(self.test_constraint_encoding())
        results.append(self.test_determinism())
        results.append(self.test_completeness())

        duration_ms = (time.time() - start) * 1000

        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed

        return PropertyTestReport(
            tongue_name=self.tongue.name,
            total_properties=len(results),
            passed_properties=passed,
            failed_properties=failed,
            results=results,
            duration_ms=duration_ms,
        )

    def test_round_trip(self) -> PropertyResult:
        """
        Test round-trip property: parse(render(ast)) == ast

        For all valid inputs:
        1. Parse to AST
        2. Render AST back to text
        3. Parse again
        4. Compare ASTs
        """
        start = time.time()
        passed_cases = 0
        failed_cases = 0
        failures: list[tuple[str, str]] = []

        valid_inputs = self.generator.generate_valid(self.cases_per_property)

        for text in valid_inputs:
            try:
                # Parse
                result1 = self.tongue.parse(text)
                if not result1.success:
                    continue  # Skip inputs that don't parse

                # Render
                rendered = self.tongue.render(result1.ast)

                # Parse again
                result2 = self.tongue.parse(rendered)

                # Compare
                if result2.success and self._asts_equal(result1.ast, result2.ast):
                    passed_cases += 1
                else:
                    failed_cases += 1
                    failures.append(
                        (text, f"AST mismatch: {result1.ast} != {result2.ast}")
                    )
            except Exception as e:
                failed_cases += 1
                failures.append((text, str(e)))

        duration_ms = (time.time() - start) * 1000

        return PropertyResult(
            property_type=PropertyType.ROUND_TRIP,
            property_name="Round-trip: parse(render(ast)) == ast",
            passed=failed_cases == 0,
            total_cases=passed_cases + failed_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            failures=failures,
            duration_ms=duration_ms,
        )

    def test_idempotence(self) -> PropertyResult:
        """
        Test idempotence: parse(text) == parse(render(parse(text)))

        Parsing and re-rendering should stabilize.
        """
        start = time.time()
        passed_cases = 0
        failed_cases = 0
        failures: list[tuple[str, str]] = []

        valid_inputs = self.generator.generate_valid(self.cases_per_property)

        for text in valid_inputs:
            try:
                # First parse
                result1 = self.tongue.parse(text)
                if not result1.success:
                    continue

                # Render and re-parse
                rendered = self.tongue.render(result1.ast)
                result2 = self.tongue.parse(rendered)

                if not result2.success:
                    failed_cases += 1
                    failures.append((text, f"Re-parse failed for: {rendered}"))
                    continue

                # Render again
                rendered2 = self.tongue.render(result2.ast)

                # Should be identical
                if rendered == rendered2:
                    passed_cases += 1
                else:
                    failed_cases += 1
                    failures.append(
                        (text, f"Render not stable: {rendered} != {rendered2}")
                    )
            except Exception as e:
                failed_cases += 1
                failures.append((text, str(e)))

        duration_ms = (time.time() - start) * 1000

        return PropertyResult(
            property_type=PropertyType.IDEMPOTENCE,
            property_name="Idempotence: render stabilizes",
            passed=failed_cases == 0,
            total_cases=passed_cases + failed_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            failures=failures,
            duration_ms=duration_ms,
        )

    def test_constraint_encoding(self) -> PropertyResult:
        """
        Test constraint encoding: forbidden inputs don't parse.

        Uses counter-examples from constraint proofs.
        """
        start = time.time()
        passed_cases = 0
        failed_cases = 0
        failures: list[tuple[str, str]] = []

        # Get counter-examples from constraint proofs
        counter_examples: list[str] = []
        for proof in self.tongue.constraint_proofs:
            for ce in proof.counter_examples:
                counter_examples.append(ce.text)

        # Also generate some constraint violations
        for constraint in self.tongue.constraints:
            violations = self._generate_constraint_violations(constraint)
            counter_examples.extend(violations)

        for text in counter_examples:
            try:
                result = self.tongue.parse(text)

                if not result.success:
                    # Good - constraint violation was rejected
                    passed_cases += 1
                else:
                    # Bad - constraint violation was accepted
                    failed_cases += 1
                    failures.append(
                        (text, f"Constraint violation should not parse: {result.ast}")
                    )
            except Exception:
                # Exception counts as rejection (good)
                passed_cases += 1

        duration_ms = (time.time() - start) * 1000

        return PropertyResult(
            property_type=PropertyType.CONSTRAINT,
            property_name="Constraint encoding: violations rejected",
            passed=failed_cases == 0,
            total_cases=passed_cases + failed_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            failures=failures,
            duration_ms=duration_ms,
        )

    def _generate_constraint_violations(self, constraint: str) -> list[str]:
        """Generate inputs that violate a constraint."""
        violations = []
        constraint_lower = constraint.lower()

        # Map common constraint patterns to violations
        if "no delete" in constraint_lower:
            violations.extend(["DELETE item", "DELETE all", "DELETE 123"])
        if "no modify" in constraint_lower or "no overwrite" in constraint_lower:
            violations.extend(["MODIFY item", "UPDATE record", "OVERWRITE file"])
        if "no create" in constraint_lower:
            violations.extend(["CREATE new", "NEW item", "ADD entry"])
        if "read only" in constraint_lower or "read-only" in constraint_lower:
            violations.extend(["WRITE data", "DELETE item", "UPDATE record"])

        return violations

    def test_determinism(self) -> PropertyResult:
        """
        Test determinism: same input → same output.

        Parse the same input multiple times, verify consistent results.
        """
        start = time.time()
        passed_cases = 0
        failed_cases = 0
        failures: list[tuple[str, str]] = []

        valid_inputs = self.generator.generate_valid(self.cases_per_property // 5)

        for text in valid_inputs:
            try:
                # Parse multiple times
                results = []
                for _ in range(5):
                    result = self.tongue.parse(text)
                    results.append(result)

                # All should be identical
                first = results[0]
                all_same = all(
                    r.success == first.success and self._asts_equal(r.ast, first.ast)
                    for r in results
                )

                if all_same:
                    passed_cases += 1
                else:
                    failed_cases += 1
                    failures.append((text, "Non-deterministic parsing"))
            except Exception as e:
                failed_cases += 1
                failures.append((text, str(e)))

        duration_ms = (time.time() - start) * 1000

        return PropertyResult(
            property_type=PropertyType.DETERMINISM,
            property_name="Determinism: same input → same output",
            passed=failed_cases == 0,
            total_cases=passed_cases + failed_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            failures=failures,
            duration_ms=duration_ms,
        )

    def test_completeness(self) -> PropertyResult:
        """
        Test completeness: all examples in tongue parse successfully.
        """
        start = time.time()
        passed_cases = 0
        failed_cases = 0
        failures: list[tuple[str, str]] = []

        for example in self.tongue.examples:
            try:
                result = self.tongue.parse(example.text)

                if result.success:
                    passed_cases += 1
                else:
                    failed_cases += 1
                    failures.append(
                        (example.text, f"Example failed to parse: {result.error}")
                    )
            except Exception as e:
                failed_cases += 1
                failures.append((example.text, str(e)))

        duration_ms = (time.time() - start) * 1000

        return PropertyResult(
            property_type=PropertyType.COMPLETENESS,
            property_name="Completeness: all examples parse",
            passed=failed_cases == 0,
            total_cases=passed_cases + failed_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            failures=failures,
            duration_ms=duration_ms,
        )

    def _asts_equal(self, ast1: Any, ast2: Any) -> bool:
        """Compare two ASTs for equality."""
        if ast1 == ast2:
            return True

        # Handle dict comparison (ignore order)
        if isinstance(ast1, dict) and isinstance(ast2, dict):
            if set(ast1.keys()) != set(ast2.keys()):
                return False
            return all(self._asts_equal(ast1[k], ast2[k]) for k in ast1)

        # Handle list comparison
        if isinstance(ast1, list) and isinstance(ast2, list):
            if len(ast1) != len(ast2):
                return False
            return all(self._asts_equal(a, b) for a, b in zip(ast1, ast2))

        return False


# ============================================================================
# Convenience Functions
# ============================================================================


async def fuzz_tongue(
    tongue: Tongue,
    seed: int | None = None,
    n: int = 100,
) -> FuzzReport:
    """
    Fuzz-test a tongue for robustness.

    Args:
        tongue: The tongue to test
        seed: Random seed for reproducibility
        n: Total number of test cases (distributed across types)

    Returns:
        FuzzReport with results
    """
    # Distribute n across input types
    valid_count = n // 2
    invalid_count = n // 4
    boundary_count = n // 8
    adversarial_count = n - valid_count - invalid_count - boundary_count

    fuzzer = TongueFuzzer(
        tongue,
        seed=seed,
        valid_count=valid_count,
        invalid_count=invalid_count,
        boundary_count=boundary_count,
        adversarial_count=adversarial_count,
    )

    return fuzzer.fuzz()


async def property_test_tongue(
    tongue: Tongue,
    seed: int | None = None,
    cases_per_property: int = 50,
) -> PropertyTestReport:
    """
    Run property-based tests on a tongue.

    Args:
        tongue: The tongue to test
        seed: Random seed for reproducibility
        cases_per_property: Number of test cases per property

    Returns:
        PropertyTestReport with results
    """
    tester = TonguePropertyTester(
        tongue,
        seed=seed,
        cases_per_property=cases_per_property,
    )

    return tester.test_all_properties()


async def validate_tongue_with_t_gent(
    tongue: Tongue,
    seed: int | None = None,
) -> tuple[FuzzReport, PropertyTestReport]:
    """
    Full T-gent validation of a tongue.

    Runs both fuzzing and property testing.

    Args:
        tongue: The tongue to validate
        seed: Random seed for reproducibility

    Returns:
        Tuple of (FuzzReport, PropertyTestReport)
    """
    fuzz_report = await fuzz_tongue(tongue, seed=seed)
    property_report = await property_test_tongue(tongue, seed=seed)

    return fuzz_report, property_report


def generate_constraint_proofs(
    tongue: Tongue,
    seed: int | None = None,
) -> list[ConstraintProof]:
    """
    Generate constraint proofs by testing violations.

    For each constraint in the tongue, generates counter-examples
    and verifies they are rejected.

    Args:
        tongue: The tongue to test
        seed: Random seed

    Returns:
        List of ConstraintProof with verification status
    """
    proofs = []
    tester = TonguePropertyTester(tongue, seed=seed)

    for constraint in tongue.constraints:
        violations = tester._generate_constraint_violations(constraint)
        counter_examples = []
        mechanism = "grammatically impossible"
        verified = True

        for text in violations:
            try:
                result = tongue.parse(text)
                if result.success:
                    verified = False
                    mechanism = "runtime check (not structural)"
                counter_examples.append(
                    CounterExample(
                        text=text,
                        expected_error="parse failure",
                        description=f"Violates: {constraint}",
                    )
                )
            except Exception:
                # Exception counts as rejection
                counter_examples.append(
                    CounterExample(
                        text=text,
                        expected_error="exception",
                        description=f"Violates: {constraint}",
                    )
                )

        proofs.append(
            ConstraintProof(
                constraint=constraint,
                mechanism=mechanism if verified else "runtime check",
                verified_by="T-gent",
                counter_examples=counter_examples,
            )
        )

    return proofs
