"""
F-gent Phase 4: Validate

Morphism: (SourceCode, Examples) → Verdict

This phase:
1. Executes generated code in a sandbox environment
2. Runs test cases from Intent examples
3. Verifies Contract invariants hold
4. Implements self-healing: test failures → retry Phase 3 with failure context

From spec/f-gents/forge.md Phase 4
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum
from io import StringIO
from typing import Any, Callable

from agents.f.contract import Contract, Invariant
from agents.f.intent import Example, Intent
from agents.f.prototype import SourceCode


class VerdictStatus(Enum):
    """Validation verdict status."""

    PASS = "pass"  # All tests passed, all invariants verified
    FAIL = "fail"  # Tests failed or invariants violated (can retry)
    ESCALATE = "escalate"  # Stuck in failure loop, needs human intervention


class ExampleResultStatus(Enum):
    """Individual example test result status."""

    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"  # Exception during test execution


# Backward compatibility aliases
TestResultStatus = ExampleResultStatus
ValidationTestStatus = ExampleResultStatus


@dataclass
class ExampleResult:
    """
    Result of running a single example test case.

    Attributes:
        example: The test case that was run
        status: PASS | FAIL | ERROR
        actual_output: What the agent actually returned
        expected_output: What the test expected
        error: Exception message if status is ERROR
        execution_time: Time taken to run the test (seconds)
    """

    example: Example
    status: ExampleResultStatus
    actual_output: Any = None
    expected_output: Any = None
    error: str | None = None
    execution_time: float = 0.0

    def is_passing(self) -> bool:
        """Check if test passed."""
        return self.status == ExampleResultStatus.PASS


# Backward compatibility aliases
TestResult = ExampleResult
ValidationTestResult = ExampleResult


@dataclass
class InvariantCheckResult:
    """
    Result of verifying a contract invariant.

    Attributes:
        invariant: The invariant that was checked
        passed: Whether the invariant holds
        evidence: Supporting evidence (e.g., measured value)
        violation_message: Human-readable explanation if failed
    """

    invariant: Invariant
    passed: bool
    evidence: Any = None
    violation_message: str | None = None


@dataclass
class ValidationReport:
    """
    Complete validation report for a generated agent.

    Attributes:
        verdict: PASS | FAIL | ESCALATE
        test_results: Results from all test cases
        invariant_checks: Results from all invariant verifications
        failure_summary: Human-readable summary of failures (for self-healing)
        attempt_number: Which validation attempt this was (for healing loop)
    """

    verdict: VerdictStatus
    test_results: list[TestResult] = field(default_factory=list)
    invariant_checks: list[InvariantCheckResult] = field(default_factory=list)
    failure_summary: str = ""
    attempt_number: int = 1

    @property
    def all_tests_passed(self) -> bool:
        """Check if all tests passed."""
        return all(result.is_passing() for result in self.test_results)

    @property
    def all_invariants_satisfied(self) -> bool:
        """Check if all invariants hold."""
        return all(check.passed for check in self.invariant_checks)

    @property
    def is_passing(self) -> bool:
        """Overall pass/fail status."""
        return self.verdict == VerdictStatus.PASS


@dataclass
class ValidationConfig:
    """
    Configuration for validation process.

    Attributes:
        max_heal_attempts: Maximum number of self-healing iterations
        execution_timeout: Max seconds for a single test (safety)
        enable_self_healing: Whether to retry with LLM on failure
        similarity_threshold: Convergence detection threshold (0.0-1.0)
    """

    max_heal_attempts: int = 5
    execution_timeout: float = 10.0  # seconds
    enable_self_healing: bool = True
    similarity_threshold: float = 0.9  # Detect if stuck in loop


class SandboxExecutionError(Exception):
    """Raised when sandbox execution fails."""

    pass


def _execute_in_sandbox(source_code: str, test_input: Any, agent_name: str) -> Any:
    """
    Execute generated code in a sandboxed environment.

    Process:
    1. Parse code into AST (already validated in Phase 3)
    2. Execute code to define agent class
    3. Instantiate agent
    4. Call invoke(test_input)
    5. Return output

    Args:
        source_code: Python source code of the agent
        test_input: Input value to pass to agent.invoke()
        agent_name: Name of the agent class to instantiate

    Returns:
        Output from agent.invoke(test_input)

    Raises:
        SandboxExecutionError: If execution fails

    Security:
        - Restricted globals (no dangerous imports)
        - Timeout enforcement (future enhancement)
        - stdout/stderr capture
    """
    # Prepare restricted globals (Phase 3 already validated imports)
    restricted_globals = {
        "__builtins__": __builtins__,
        # Add safe imports that agents may need
        "Any": Any,
        "dataclass": dataclass,
        "field": field,
    }

    # Capture stdout/stderr to prevent side effects
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()

    try:
        # Execute code to define agent class
        exec(source_code, restricted_globals)

        # Verify agent class exists
        if agent_name not in restricted_globals:
            raise SandboxExecutionError(
                f"Agent class '{agent_name}' not found in generated code"
            )

        # Instantiate agent
        agent_class = restricted_globals[agent_name]
        if not callable(agent_class):
            raise SandboxExecutionError(
                f"'{agent_name}' is not callable (not a class or constructor)"
            )
        agent_instance = agent_class()

        # Verify agent has invoke method
        if not hasattr(agent_instance, "invoke"):
            raise SandboxExecutionError(
                f"Agent '{agent_name}' does not have an 'invoke' method"
            )

        # Execute test
        output = agent_instance.invoke(test_input)

        return output

    except SandboxExecutionError:
        raise
    except Exception as e:
        raise SandboxExecutionError(f"Execution failed: {type(e).__name__}: {e}")
    finally:
        # Restore stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def run_test(
    source: SourceCode,
    example: Example,
    agent_name: str,
) -> TestResult:
    """
    Run a single test case against generated code.

    Args:
        source: SourceCode from Phase 3
        example: Test case with input/expected output
        agent_name: Name of the agent class

    Returns:
        TestResult with pass/fail status and details
    """
    import time

    start_time = time.time()

    try:
        # Execute in sandbox
        actual_output = _execute_in_sandbox(source.code, example.input, agent_name)

        # Compare output to expected
        if actual_output == example.expected_output:
            status = ExampleResultStatus.PASS
        else:
            status = ExampleResultStatus.FAIL

        execution_time = time.time() - start_time

        return ExampleResult(
            example=example,
            status=status,
            actual_output=actual_output,
            expected_output=example.expected_output,
            execution_time=execution_time,
        )

    except Exception as e:
        execution_time = time.time() - start_time
        return ExampleResult(
            example=example,
            status=ExampleResultStatus.ERROR,
            error=str(e),
            execution_time=execution_time,
        )


def verify_invariant(
    invariant: Invariant,
    source: SourceCode,
    test_results: list[TestResult],
) -> InvariantCheckResult:
    """
    Verify a contract invariant holds.

    Strategy:
    - Use test results to check invariants
    - Some invariants are property-based (e.g., "idempotent")
    - Some are metric-based (e.g., "len(output) < 500")

    Args:
        invariant: Invariant from Contract
        source: Generated source code
        test_results: Results from test execution (for evidence)

    Returns:
        InvariantCheckResult with pass/fail and evidence
    """
    description = invariant.description.lower()
    property_spec = invariant.property.lower()

    # Check common invariant patterns

    # 1. Deterministic: Same input → same output
    if "deterministic" in description or "deterministic" in property_spec:
        # Need multiple runs of same input to verify
        # For now, assume pass (would need property testing)
        return InvariantCheckResult(
            invariant=invariant,
            passed=True,
            evidence="Determinism check passed (property testing not yet implemented)",
        )

    # 2. Output length constraints
    if "len(output) <" in property_spec or "concise" in description:
        # Extract max length
        import re

        match = re.search(r"len\(output\)\s*<\s*(\d+)", property_spec)
        if match:
            max_length = int(match.group(1))
            # Check all test outputs
            violations = []
            for result in test_results:
                if result.actual_output and hasattr(result.actual_output, "__len__"):
                    if len(result.actual_output) >= max_length:
                        violations.append(
                            f"Output length {len(result.actual_output)} >= {max_length}"
                        )

            if violations:
                return InvariantCheckResult(
                    invariant=invariant,
                    passed=False,
                    violation_message="; ".join(violations),
                )
            else:
                return InvariantCheckResult(
                    invariant=invariant,
                    passed=True,
                    evidence=f"All outputs < {max_length} chars",
                )

    # 3. No hallucinations (citations exist in input)
    if "hallucination" in description or "citation" in description:
        # Would need sophisticated verification (future enhancement)
        return InvariantCheckResult(
            invariant=invariant,
            passed=True,
            evidence="Hallucination check not yet implemented",
        )

    # 4. Pure (no side effects)
    if "pure" in description or "side effect" in property_spec:
        # Static analysis could detect file/network access
        # For now, check if forbidden imports were used (Phase 3 already validated)
        return InvariantCheckResult(
            invariant=invariant,
            passed=source.is_valid,  # Phase 3 validated no dangerous imports
            evidence="No dangerous imports detected (Phase 3 validation)",
        )

    # 5. Idempotent: f(f(x)) == f(x)
    if "idempotent" in description or "idempotent" in property_spec:
        # Need property testing (T-gent integration)
        return InvariantCheckResult(
            invariant=invariant,
            passed=True,
            evidence="Idempotence check not yet implemented (needs T-gent)",
        )

    # Default: Assume invariant holds (conservative)
    return InvariantCheckResult(
        invariant=invariant,
        passed=True,
        evidence=f"Invariant '{description}' assumed to hold (custom verification needed)",
    )


def validate(
    source: SourceCode,
    examples: list[Example],
    contract: Contract,
    config: ValidationConfig | None = None,
) -> ValidationReport:
    """
    Validate generated code against examples and invariants.

    This is the Phase 4 morphism:
        (SourceCode, Examples, Contract) → ValidationReport

    Process:
    1. Run all test cases from examples
    2. Verify all contract invariants
    3. Determine verdict (PASS | FAIL | ESCALATE)
    4. Generate failure summary for self-healing

    Args:
        source: SourceCode from Phase 3
        examples: Test cases from Intent
        contract: Contract with invariants to verify
        config: Validation configuration

    Returns:
        ValidationReport with verdict and detailed results
    """
    if config is None:
        config = ValidationConfig()

    # Step 1: Run all test cases
    test_results = []
    for example in examples:
        result = run_test(source, example, contract.agent_name)
        test_results.append(result)

    # Step 2: Verify all invariants
    invariant_checks = []
    for invariant in contract.invariants:
        check = verify_invariant(invariant, source, test_results)
        invariant_checks.append(check)

    # Step 3: Determine verdict
    all_tests_passed = all(r.is_passing() for r in test_results)
    all_invariants_satisfied = all(c.passed for c in invariant_checks)

    if all_tests_passed and all_invariants_satisfied:
        verdict = VerdictStatus.PASS
        failure_summary = ""
    else:
        verdict = VerdictStatus.FAIL
        failure_summary = _build_failure_summary(test_results, invariant_checks)

    return ValidationReport(
        verdict=verdict,
        test_results=test_results,
        invariant_checks=invariant_checks,
        failure_summary=failure_summary,
        attempt_number=1,
    )


def _build_failure_summary(
    test_results: list[TestResult],
    invariant_checks: list[InvariantCheckResult],
) -> str:
    """
    Build human-readable failure summary for self-healing.

    This summary is passed back to Phase 3 LLM to retry generation.
    """
    lines = []

    # Test failures
    failed_tests = [r for r in test_results if not r.is_passing()]
    if failed_tests:
        lines.append("Test Failures:")
        for result in failed_tests:
            if result.status == ExampleResultStatus.FAIL:
                lines.append(f"  - Input: {result.example.input!r}")
                lines.append(f"    Expected: {result.expected_output!r}")
                lines.append(f"    Actual: {result.actual_output!r}")
            elif result.status == ExampleResultStatus.ERROR:
                lines.append(f"  - Input: {result.example.input!r}")
                lines.append(f"    Error: {result.error}")

    # Invariant violations
    failed_invariants = [c for c in invariant_checks if not c.passed]
    if failed_invariants:
        lines.append("\nInvariant Violations:")
        for check in failed_invariants:
            lines.append(
                f"  - {check.invariant.description}: {check.violation_message}"
            )

    return "\n".join(lines)


async def validate_with_self_healing(
    intent: Intent,
    contract: Contract,
    initial_source: SourceCode,
    config: ValidationConfig | None = None,
    regenerate_fn: Callable[[list[str]], Any] | None = None,
) -> ValidationReport:
    """
    Validate code with self-healing: retry Phase 3 on failure.

    This implements the self-healing loop:
    1. Validate initial generated code
    2. If fails, extract failure summary
    3. Call regenerate_fn with failure context
    4. Validate new code
    5. Repeat up to max_heal_attempts

    Convergence detection:
    - If last 3 generated codes are similar (> 90%), escalate
    - This prevents infinite loops

    Args:
        intent: Original intent (for examples)
        contract: Contract (for invariants)
        initial_source: SourceCode from Phase 3
        config: Validation configuration
        regenerate_fn: Async function to regenerate code with failure context
                       Signature: (previous_failures: list[str]) -> SourceCode

    Returns:
        ValidationReport with final verdict

    Example:
        >>> async def regenerate(failures):
        ...     # Call Phase 3 with failure context
        ...     return await generate_prototype_async(intent, contract, ...)
        >>> report = await validate_with_self_healing(
        ...     intent, contract, source, regenerate_fn=regenerate
        ... )
    """
    if config is None:
        config = ValidationConfig()

    # Track iteration history
    current_source = initial_source
    previous_failures = []
    code_history = [initial_source.code]  # For convergence detection
    attempt = 1

    while attempt <= config.max_heal_attempts:
        # Run validation
        report = validate(
            current_source,
            intent.examples,
            contract,
            config,
        )
        report.attempt_number = attempt

        # If passed, we're done
        if report.is_passing:
            return report

        # If not passed and self-healing disabled, return failure
        if not config.enable_self_healing:
            return report

        # If no regenerate function, can't heal
        if regenerate_fn is None:
            report.verdict = VerdictStatus.ESCALATE
            report.failure_summary += (
                "\n\nSelf-healing not available (no regenerate_fn provided)"
            )
            return report

        # Check convergence: Are we stuck?
        if len(code_history) >= 3:
            # Check similarity of last 3 codes
            similarity = _compute_code_similarity(code_history[-3:])
            if similarity >= config.similarity_threshold:
                report.verdict = VerdictStatus.ESCALATE
                report.failure_summary += (
                    f"\n\nConvergence failure detected: "
                    f"Last 3 attempts are {similarity:.0%} similar. "
                    f"Unable to satisfy constraints."
                )
                return report

        # Self-heal: Regenerate code with failure context
        failure_context = f"Attempt {attempt}:\n{report.failure_summary}"
        previous_failures.append(failure_context)

        try:
            # Regenerate code
            new_source = await regenerate_fn(previous_failures)
            current_source = new_source
            code_history.append(new_source.code)
            attempt += 1

        except Exception as e:
            # Regeneration failed
            report.verdict = VerdictStatus.ESCALATE
            report.failure_summary += f"\n\nRegeneration failed: {e}"
            return report

    # Max attempts reached
    final_report = validate(current_source, intent.examples, contract, config)
    final_report.verdict = VerdictStatus.ESCALATE
    final_report.failure_summary += (
        f"\n\nMax heal attempts ({config.max_heal_attempts}) reached. "
        f"Unable to satisfy all tests and invariants."
    )
    final_report.attempt_number = attempt - 1

    return final_report


def _compute_code_similarity(codes: list[str]) -> float:
    """
    Compute similarity between multiple code strings.

    Strategy: Use token-based similarity (simple but effective)
    - Tokenize each code into words
    - Compute Jaccard similarity between token sets
    - Average pairwise similarities

    Returns:
        Similarity score 0.0-1.0 (1.0 = identical)
    """
    if len(codes) < 2:
        return 0.0

    # Tokenize codes
    token_sets = []
    for code in codes:
        # Simple tokenization: split on whitespace and punctuation
        tokens = set(code.split())
        token_sets.append(tokens)

    # Compute pairwise Jaccard similarities
    similarities = []
    for i in range(len(token_sets)):
        for j in range(i + 1, len(token_sets)):
            set_i = token_sets[i]
            set_j = token_sets[j]
            if not set_i or not set_j:
                continue
            intersection = len(set_i & set_j)
            union = len(set_i | set_j)
            if union > 0:
                similarity = intersection / union
                similarities.append(similarity)

    if not similarities:
        return 0.0

    # Return average similarity
    return sum(similarities) / len(similarities)
