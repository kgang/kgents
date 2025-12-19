"""
Prototype generation for F-gents (Phase 3: Prototype).

This module implements the (Intent, Contract) → SourceCode morphism from spec/f-gents/forge.md.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agents.f.contract import Contract
from agents.f.intent import Intent


class ValidationStatus(Enum):
    """Result of validation step."""

    PASS = "pass"
    FAIL = "fail"


class ValidationCategory(Enum):
    """Type of validation check."""

    PARSE = "parse"  # AST parsing
    TYPE = "type"  # Type checking (future: mypy/pyright)
    LINT = "lint"  # Code quality (future: ruff/pylint)
    IMPORT = "import"  # Import safety
    SECURITY = "security"  # Security scan (future: G-gent)


@dataclass
class ValidationResult:
    """Result of a single validation check."""

    category: ValidationCategory
    status: ValidationStatus
    message: str = ""  # Details (error message or success confirmation)
    details: dict[str, Any] = field(default_factory=dict)  # Additional context


@dataclass
class StaticAnalysisReport:
    """
    Aggregated static analysis results.

    This is part of the Phase 3 output alongside SourceCode.
    """

    results: list[ValidationResult] = field(default_factory=list)
    passed: bool = False  # True if all checks passed

    def add_result(self, result: ValidationResult) -> None:
        """Add validation result and update passed status."""
        self.results.append(result)
        self.passed = all(r.status == ValidationStatus.PASS for r in self.results)

    def get_failures(self) -> list[ValidationResult]:
        """Get all failed validation checks."""
        return [r for r in self.results if r.status == ValidationStatus.FAIL]

    def failure_summary(self) -> str:
        """Generate summary of all failures for iteration feedback."""
        failures = self.get_failures()
        if not failures:
            return ""

        summary_parts = []
        for fail in failures:
            summary_parts.append(f"[{fail.category.value}] {fail.message}")

        return "\n".join(summary_parts)


@dataclass
class SourceCode:
    """
    Generated Python source code.

    This is the primary output of Phase 3 (Prototype).
    """

    code: str  # Python source code
    analysis_report: StaticAnalysisReport  # Validation results
    generation_attempt: int = 1  # Which iteration produced this (for debugging)

    @property
    def is_valid(self) -> bool:
        """Check if code passed all static analysis."""
        return self.analysis_report.passed


# ============================================================================
# Static Analysis Validators
# ============================================================================


def validate_parse(code: str) -> ValidationResult:
    """
    Validate that code parses as valid Python AST.

    This is the first gate - if code doesn't parse, all other checks are meaningless.
    """
    try:
        ast.parse(code)
        return ValidationResult(
            category=ValidationCategory.PARSE,
            status=ValidationStatus.PASS,
            message="Code parses successfully",
        )
    except SyntaxError as e:
        return ValidationResult(
            category=ValidationCategory.PARSE,
            status=ValidationStatus.FAIL,
            message=f"Syntax error at line {e.lineno}: {e.msg}",
            details={"lineno": e.lineno, "offset": e.offset, "text": e.text},
        )


def validate_imports(code: str) -> ValidationResult:
    """
    Validate that code only uses allowed imports.

    Security check: Prevent dangerous imports like os.system, subprocess, etc.
    Future: Make configurable per agent (some agents legitimately need file/network access).
    """
    # Forbidden imports that pose security risks
    forbidden = {
        "os.system",
        "subprocess",
        "eval",
        "exec",
        "__import__",
    }

    # Parse code to extract imports
    try:
        tree = ast.parse(code)
    except SyntaxError:
        # If it doesn't parse, the parse validator will catch it
        return ValidationResult(
            category=ValidationCategory.IMPORT,
            status=ValidationStatus.PASS,
            message="Skipping import check (parse failed)",
        )

    # Check for forbidden imports
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in forbidden:
                    violations.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for alias in node.names:
                    full_name = f"{node.module}.{alias.name}"
                    if full_name in forbidden or node.module in forbidden:
                        violations.append(full_name)

    if violations:
        return ValidationResult(
            category=ValidationCategory.IMPORT,
            status=ValidationStatus.FAIL,
            message=f"Forbidden imports detected: {', '.join(violations)}",
            details={"violations": violations},
        )

    return ValidationResult(
        category=ValidationCategory.IMPORT,
        status=ValidationStatus.PASS,
        message="All imports are safe",
    )


def validate_lint(code: str) -> ValidationResult:
    """
    Basic code quality checks.

    Future: Integrate ruff/pylint for comprehensive linting.
    Current: Simple heuristics for obviously bad code.
    """
    lines = code.split("\n")

    # Check for obviously bad patterns
    issues = []

    # Check for excessively long lines (>120 chars)
    for i, line in enumerate(lines, 1):
        if len(line) > 120:
            issues.append(f"Line {i} exceeds 120 characters ({len(line)} chars)")

    # Check for TODO/FIXME comments (suggests incomplete implementation)
    for i, line in enumerate(lines, 1):
        if re.search(r"\b(TODO|FIXME|XXX)\b", line, re.IGNORECASE):
            issues.append(f"Line {i} contains placeholder comment: {line.strip()}")

    if issues:
        return ValidationResult(
            category=ValidationCategory.LINT,
            status=ValidationStatus.FAIL,
            message=f"Code quality issues: {len(issues)} found",
            details={"issues": issues},
        )

    return ValidationResult(
        category=ValidationCategory.LINT,
        status=ValidationStatus.PASS,
        message="Code passes basic quality checks",
    )


def run_static_analysis(code: str) -> StaticAnalysisReport:
    """
    Run all static analysis validators.

    This implements the multi-stage validation from spec/f-gents/forge.md Phase 3.

    Validators run in order:
    1. Parse check (gates all others)
    2. Import check (security)
    3. Lint check (quality)

    Future: Add type checking (mypy/pyright), security scan (G-gent).
    """
    report = StaticAnalysisReport()

    # Validator pipeline
    validators = [
        validate_parse,
        validate_imports,
        validate_lint,
    ]

    for validator in validators:
        result = validator(code)
        report.add_result(result)

        # Early exit if parse fails (no point running other checks)
        if result.category == ValidationCategory.PARSE and result.status == ValidationStatus.FAIL:
            break

    return report


# ============================================================================
# Code Generation (LLM Integration Point)
# ============================================================================


def _build_generation_prompt(
    intent: Intent,
    contract: Contract,
    previous_failures: list[str] | None = None,
) -> str:
    """
    Build prompt for LLM code generation.

    This constructs a detailed prompt including:
    - Intent (natural language guidance)
    - Contract (type signatures + invariants)
    - Examples (test cases to satisfy)
    - Previous failures (if iteration)

    The prompt guides the LLM to generate Python code satisfying the contract.
    """
    # Base prompt structure
    prompt_parts = [
        "# Task: Generate Python Agent Implementation",
        "",
        "## Intent",
        f"Purpose: {intent.purpose}",
        "",
        "Behavior:",
    ]

    for behavior in intent.behavior:
        prompt_parts.append(f"- {behavior}")

    prompt_parts.append("")
    prompt_parts.append("Constraints:")
    for constraint in intent.constraints:
        prompt_parts.append(f"- {constraint}")

    # Add contract specification
    prompt_parts.extend(
        [
            "",
            "## Contract Specification",
            f"Agent Name: {contract.agent_name}",
            f"Input Type: {contract.input_type}",
            f"Output Type: {contract.output_type}",
            "",
            "Invariants (must be satisfied):",
        ]
    )

    for inv in contract.invariants:
        prompt_parts.append(f"- {inv.description} → {inv.property}")

    if contract.composition_rules:
        prompt_parts.append("")
        prompt_parts.append("Composition Rules:")
        for rule in contract.composition_rules:
            prompt_parts.append(f"- {rule.mode}: {rule.description}")

    # Add examples if provided
    if intent.examples:
        prompt_parts.extend(
            [
                "",
                "## Examples (Test Cases)",
            ]
        )
        for i, example in enumerate(intent.examples, 1):
            prompt_parts.append(f"Example {i}:")
            prompt_parts.append(f"  Input: {example.input}")
            prompt_parts.append(f"  Expected Output: {example.expected_output}")

    # Add iteration feedback if this is a retry
    if previous_failures:
        prompt_parts.extend(
            [
                "",
                "## Previous Attempt Failures",
                "The previous implementation failed with these errors:",
                "",
            ]
        )
        prompt_parts.extend(previous_failures)
        prompt_parts.extend(
            [
                "",
                "Please fix these issues in the new implementation.",
            ]
        )

    # Add code generation instructions
    prompt_parts.extend(
        [
            "",
            "## Implementation Requirements",
            "",
            "Generate a Python class that:",
            f"1. Is named '{contract.agent_name}'",
            f"2. Has a method 'invoke(self, input: {contract.input_type}) -> {contract.output_type}'",
            "3. Satisfies all invariants listed above",
            "4. Includes proper error handling",
            "5. Has a clear docstring explaining behavior",
            "",
            "Return ONLY the Python code, no explanations or markdown formatting.",
        ]
    )

    return "\n".join(prompt_parts)


def generate_code_stub(intent: Intent, contract: Contract) -> str:
    """
    Generate code without LLM (stub implementation for testing).

    This is a placeholder until we integrate actual LLM code generation.
    Generates a minimal valid Python class satisfying the contract structure.

    Future: Replace with OpenRouter LLM call using _build_generation_prompt().
    """
    # Build basic class structure
    code_parts = [
        '"""',
        f"{contract.semantic_intent or intent.purpose}",
        '"""',
        "",
        f"class {contract.agent_name}:",
        '    """',
        f"    {intent.purpose}",
        "    ",
    ]

    # Add behavior documentation
    if intent.behavior:
        code_parts.append("    Behavior:")
        for behavior in intent.behavior:
            code_parts.append(f"    - {behavior}")
        code_parts.append("    ")

    # Add invariants documentation
    if contract.invariants:
        code_parts.append("    Invariants:")
        for inv in contract.invariants:
            code_parts.append(f"    - {inv.description}")
        code_parts.append("    ")

    code_parts.append('    """')
    code_parts.append("")

    # Generate invoke method
    code_parts.extend(
        [
            f"    def invoke(self, input_data: {contract.input_type}) -> {contract.output_type}:",
            '        """',
            "        Process input and return output according to contract.",
            "        ",
            "        Args:",
            f"            input_data: {contract.input_type}",
            "        ",
            "        Returns:",
            f"            {contract.output_type}",
            '        """',
            "        # Stub implementation for testing",
        ]
    )

    # Generate minimal return value based on output type
    if contract.output_type == "str":
        code_parts.append("        return str(input_data)")
    elif contract.output_type == "dict":
        code_parts.append('        return {"result": str(input_data)}')
    elif contract.output_type == "list":
        code_parts.append("        return [input_data]")
    elif contract.output_type == "int":
        code_parts.append("        return 0")
    elif contract.output_type == "bool":
        code_parts.append("        return True")
    else:
        # Generic fallback
        code_parts.append("        return input_data")

    return "\n".join(code_parts)


# ============================================================================
# Phase 3: Prototype Generation (Main Morphism)
# ============================================================================


@dataclass
class PrototypeConfig:
    """Configuration for prototype generation."""

    max_attempts: int = 5  # Maximum generation attempts before escalation
    use_llm: bool = False  # Whether to use LLM (False = stub generation)
    runtime: Any | None = None  # LLM runtime (required if use_llm=True)


async def generate_prototype_async(
    intent: Intent,
    contract: Contract,
    config: PrototypeConfig | None = None,
) -> SourceCode:
    """
    Generate source code implementation from intent and contract (async version).

    This is the core morphism of Phase 3 (Prototype):
        (Intent, Contract) → SourceCode

    Process:
    1. Generate code (stub or LLM)
    2. Run static analysis
    3. If validation fails and attempts < max, iterate with feedback
    4. Return SourceCode with analysis report

    Args:
        intent: Natural language guidance from Phase 1
        contract: Formal specification from Phase 2
        config: Generation configuration (default: PrototypeConfig())

    Returns:
        SourceCode with analysis report

    Examples:
        >>> from agents.f import parse_intent, synthesize_contract
        >>> from runtime.claude import ClaudeRuntime
        >>> intent = parse_intent("Create an agent that doubles numbers")
        >>> contract = synthesize_contract(intent, "DoublerAgent")
        >>> runtime = ClaudeRuntime()
        >>> config = PrototypeConfig(use_llm=True, runtime=runtime)
        >>> source = await generate_prototype_async(intent, contract, config)
        >>> source.is_valid
        True
    """
    if config is None:
        config = PrototypeConfig()

    if config.use_llm and config.runtime is None:
        raise ValueError("runtime is required when use_llm=True")

    previous_failures: list[str] = []

    for attempt in range(1, config.max_attempts + 1):
        # Generate code
        if config.use_llm:
            # Import here to avoid circular dependency
            from agents.f.llm_generation import generate_code_with_llm

            # mypy: runtime is guaranteed non-None due to check above
            assert config.runtime is not None
            code = await generate_code_with_llm(
                intent,
                contract,
                config.runtime,
                previous_failures if previous_failures else None,
            )
        else:
            code = generate_code_stub(intent, contract)

        # Run static analysis
        report = run_static_analysis(code)

        # Create source code result
        source = SourceCode(
            code=code,
            analysis_report=report,
            generation_attempt=attempt,
        )

        # If valid, return immediately
        if source.is_valid:
            return source

        # If invalid and we have attempts left, collect failures for next iteration
        if attempt < config.max_attempts:
            failure_summary = report.failure_summary()
            previous_failures.append(f"Attempt {attempt}:")
            previous_failures.append(failure_summary)
            previous_failures.append("")
        else:
            # Max attempts exceeded - return the failed source
            # Caller should escalate to human
            return source

    # Should never reach here, but satisfy type checker
    return source


def generate_prototype(
    intent: Intent,
    contract: Contract,
    config: PrototypeConfig | None = None,
) -> SourceCode:
    """
    Generate source code implementation from intent and contract.

    This is the core morphism of Phase 3 (Prototype):
        (Intent, Contract) → SourceCode

    Process:
    1. Generate code (stub or LLM)
    2. Run static analysis
    3. If validation fails and attempts < max, iterate with feedback
    4. Return SourceCode with analysis report

    Args:
        intent: Natural language guidance from Phase 1
        contract: Formal specification from Phase 2
        config: Generation configuration (default: PrototypeConfig())

    Returns:
        SourceCode with analysis report

    Examples:
        >>> from agents.f import parse_intent, synthesize_contract
        >>> intent = parse_intent("Create an agent that doubles numbers")
        >>> contract = synthesize_contract(intent, "DoublerAgent")
        >>> source = generate_prototype(intent, contract)
        >>> source.is_valid
        True
    """
    if config is None:
        config = PrototypeConfig()

    previous_failures: list[str] = []

    for attempt in range(1, config.max_attempts + 1):
        # Generate code
        if config.use_llm:
            # Future: Call LLM with _build_generation_prompt()
            # For now, fall back to stub
            code = generate_code_stub(intent, contract)
        else:
            code = generate_code_stub(intent, contract)

        # Run static analysis
        report = run_static_analysis(code)

        # Create source code result
        source = SourceCode(
            code=code,
            analysis_report=report,
            generation_attempt=attempt,
        )

        # If valid, return immediately
        if source.is_valid:
            return source

        # If invalid and we have attempts left, collect failures for next iteration
        if attempt < config.max_attempts:
            failure_summary = report.failure_summary()
            previous_failures.append(f"Attempt {attempt}:")
            previous_failures.append(failure_summary)
            previous_failures.append("")
            # Note: In future LLM integration, we'd pass previous_failures to _build_generation_prompt
        else:
            # Max attempts exceeded - return the failed source
            # Caller should escalate to human
            return source

    # Should never reach here, but satisfy type checker
    return source
