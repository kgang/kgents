"""
Obligation Extraction: From Failures to Theorems.

This module extracts proof obligations from various sources:
- Test failures (primary): pytest AssertionError → formal property
- Type signatures: AD-013 @node decorators → type invariants
- Spec assertions (future): docstring ensures → properties

Heritage: "Every test failure is a theorem waiting to be stated."

The extraction is intentionally simple—complex assertions need human guidance.
The goal is to bootstrap the proof pipeline, not replace human judgment.

Teaching:
    gotcha: Context extraction is bounded to 5 lines. Large tracebacks
            would bloat obligations and slow proof search. Prefer relevant
            excerpts over complete dumps.
    gotcha: Assertion parsing is pattern-based, not AST-based. This is
            intentional—we want readable properties, not compiled forms.

AGENTESE:
    concept.ashc.obligation → Generate proof obligation from failure
"""

from __future__ import annotations

import ast
import re
import uuid
from dataclasses import dataclass, field
from typing import Any

from .contracts import ObligationId, ObligationSource, ProofObligation

# =============================================================================
# Constants
# =============================================================================

# Maximum context lines to extract (prevents bloat)
MAX_CONTEXT_LINES = 5

# Maximum length of a single context line
MAX_CONTEXT_LINE_LENGTH = 200


# =============================================================================
# Obligation Extractor
# =============================================================================


@dataclass
class ObligationExtractor:
    """
    Extract proof obligations from various sources.

    Pattern: Container-Owns-Workflow (Pattern 1)
    The extractor owns a session of extractions, tracking obligations
    and providing unique IDs.

    Laws:
        1. Idempotency: Same input → same property (deterministic)
        2. Boundedness: Context is always limited to MAX_CONTEXT_LINES
        3. Traceability: Every obligation has a source_location

    Example:
        >>> extractor = ObligationExtractor()
        >>> obl = extractor.from_test_failure(
        ...     test_name="test_positive",
        ...     assertion="assert x > 0",
        ...     traceback="...",
        ...     source_file="test_math.py",
        ...     line_number=42,
        ... )
        >>> "∀" in obl.property
        True
    """

    # Session tracking
    _obligations: list[ProofObligation] = field(default_factory=list)

    def _generate_id(self, prefix: str) -> ObligationId:
        """Generate a unique obligation ID with prefix."""
        # Use UUID suffix for uniqueness
        suffix = uuid.uuid4().hex[:8]
        return ObligationId(f"obl-{prefix}-{suffix}")

    # =========================================================================
    # Test Failure Extraction
    # =========================================================================

    def from_test_failure(
        self,
        test_name: str,
        assertion: str,
        traceback: str,
        source_file: str,
        line_number: int,
    ) -> ProofObligation:
        """
        Extract obligation from a test failure.

        Transforms a pytest assertion failure into a formal property
        that could be proven by a proof checker.

        Args:
            test_name: The failing test function name (e.g., "test_positive")
            assertion: The failed assertion string (e.g., "assert x > 0")
            traceback: The full traceback text
            source_file: Path to the test file
            line_number: Line where assertion failed

        Returns:
            ProofObligation with formal property statement

        Example:
            >>> obl = extractor.from_test_failure(
            ...     test_name="test_add_zero",
            ...     assertion="assert x + 0 == x",
            ...     traceback="...",
            ...     source_file="test_math.py",
            ...     line_number=10,
            ... )
            >>> obl.property
            '∀ x. x + 0 == x'
        """
        # Generate unique ID
        obl_id = self._generate_id("test")

        # Parse assertion to formal property
        property_stmt = self._assertion_to_property(assertion, test_name)

        # Extract bounded context from traceback
        context = self._extract_context(traceback, source_file)

        # Add test name as context if meaningful
        if test_name and test_name not in str(context):
            context = (f"Test: {test_name}",) + context

        obl = ProofObligation(
            id=obl_id,
            property=property_stmt,
            source=ObligationSource.TEST,
            source_location=f"{source_file}:{line_number}",
            context=context,
        )

        self._obligations.append(obl)
        return obl

    def _assertion_to_property(self, assertion: str, test_name: str = "") -> str:
        """
        Convert Python assertion to formal property.

        This is intentionally simple—complex assertions need human guidance.
        The goal is to produce a readable starting point for proof search.

        Pattern matching hierarchy:
        1. Comparison operators (>, <, ==, !=, >=, <=)
        2. Identity checks (is, is not)
        3. Membership (in, not in)
        4. Boolean expressions (and, or, not)
        5. Fallback: wrap in forall

        Args:
            assertion: The assertion string (may include "assert " prefix)
            test_name: Optional test name for variable extraction hints

        Returns:
            Formal property string with ∀ quantifier
        """
        # Strip "assert " prefix if present
        expr = assertion.strip()
        if expr.lower().startswith("assert "):
            expr = expr[7:].strip()

        # Remove trailing comments
        if "#" in expr:
            expr = expr[: expr.index("#")].strip()

        # Extract variables from expression
        variables = self._extract_variables(expr)

        # Handle common patterns
        if not variables:
            # No variables found - constant assertion
            return f"Assertion: {expr}"

        # Build quantified property
        var_list = ", ".join(sorted(variables))

        # Handle comparison patterns
        if " > " in expr or " >= " in expr:
            return f"∀ {var_list}. {expr}"
        if " < " in expr or " <= " in expr:
            return f"∀ {var_list}. {expr}"
        if " == " in expr:
            return f"∀ {var_list}. {expr}"
        if " != " in expr:
            return f"∀ {var_list}. {expr}"

        # Handle membership patterns
        if " in " in expr:
            return f"∀ {var_list}. {expr}"
        if " not in " in expr:
            return f"∀ {var_list}. {expr}"

        # Handle boolean patterns
        if " and " in expr or " or " in expr:
            return f"∀ {var_list}. {expr}"

        # Handle function calls (common in tests)
        if "(" in expr and ")" in expr:
            return f"∀ {var_list}. {expr}"

        # Fallback: generic forall
        return f"∀ {var_list}. {expr}"

    def _extract_variables(self, expr: str) -> set[str]:
        """
        Extract variable names from a Python expression.

        Uses simple pattern matching to find identifiers that look like
        variables (not keywords, not function names, not constants).

        Args:
            expr: Python expression string

        Returns:
            Set of variable names found
        """
        # Python keywords to exclude
        keywords = {
            "True",
            "False",
            "None",
            "and",
            "or",
            "not",
            "in",
            "is",
            "if",
            "else",
            "for",
            "while",
            "def",
            "class",
            "return",
            "lambda",
            "assert",
        }

        # Common function names to exclude
        functions = {
            "len",
            "str",
            "int",
            "float",
            "bool",
            "list",
            "dict",
            "set",
            "tuple",
            "range",
            "type",
            "isinstance",
            "hasattr",
            "getattr",
            "all",
            "any",
            "sum",
            "min",
            "max",
            "abs",
            "sorted",
            "reversed",
        }

        # Find all identifiers
        # Pattern: word boundary + letter/underscore + alphanumeric*
        identifier_pattern = r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b"
        candidates = set(re.findall(identifier_pattern, expr))

        # Filter out keywords, functions, and all-caps constants
        variables = set()
        for name in candidates:
            if name in keywords:
                continue
            if name in functions:
                continue
            if name.isupper() and len(name) > 1:  # Constants like MAX_SIZE
                continue
            if name.startswith("_"):  # Private variables
                continue
            variables.add(name)

        return variables

    def _extract_context(
        self,
        traceback: str,
        source_file: str,
    ) -> tuple[str, ...]:
        """
        Extract relevant context from traceback.

        Bounded extraction that finds:
        1. Variable assignments near the failure
        2. Relevant code snippets
        3. Error messages

        Args:
            traceback: Full traceback text
            source_file: Source file path for filtering

        Returns:
            Tuple of context strings (max MAX_CONTEXT_LINES)
        """
        context: list[str] = []

        for line in traceback.split("\n"):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip traceback frame markers
            if line.startswith("Traceback"):
                continue
            if line.startswith("File "):
                continue

            # Capture variable assignments
            if "=" in line and not line.startswith("#"):
                # Truncate long lines
                if len(line) > MAX_CONTEXT_LINE_LENGTH:
                    line = line[: MAX_CONTEXT_LINE_LENGTH - 3] + "..."
                context.append(line)

            # Capture assertion-related lines
            if "assert" in line.lower():
                if len(line) > MAX_CONTEXT_LINE_LENGTH:
                    line = line[: MAX_CONTEXT_LINE_LENGTH - 3] + "..."
                context.append(line)

            # Capture error messages
            if "Error" in line or "error" in line:
                if len(line) > MAX_CONTEXT_LINE_LENGTH:
                    line = line[: MAX_CONTEXT_LINE_LENGTH - 3] + "..."
                context.append(line)

            # Stop at limit
            if len(context) >= MAX_CONTEXT_LINES:
                break

        return tuple(context[:MAX_CONTEXT_LINES])

    # =========================================================================
    # Type Signature Extraction (AD-013)
    # =========================================================================

    def from_type_signature(
        self,
        path: str,
        input_type: str,
        output_type: str,
        effects: tuple[str, ...] = (),
    ) -> ProofObligation:
        """
        Extract obligation from AD-013 typed AGENTESE path.

        AGENTESE paths can declare type contracts via the @node decorator.
        These contracts generate proof obligations that verify type safety.

        Args:
            path: AGENTESE path (e.g., "world.tools.bash")
            input_type: Input type annotation (e.g., "BashRequest")
            output_type: Output type annotation (e.g., "Witness[BashResult]")
            effects: Declared effects (e.g., ("filesystem", "subprocess"))

        Returns:
            ProofObligation with type safety property

        Example:
            >>> obl = extractor.from_type_signature(
            ...     path="world.tools.bash",
            ...     input_type="BashRequest",
            ...     output_type="Witness[BashResult]",
            ...     effects=("filesystem", "subprocess"),
            ... )
            >>> "BashRequest" in obl.property
            True
        """
        obl_id = self._generate_id("type")

        property_stmt = self._type_to_property(input_type, output_type, effects)

        # Build context from effects
        context: tuple[str, ...] = ()
        if effects:
            context = (f"Effects: {', '.join(effects)}",)

        obl = ProofObligation(
            id=obl_id,
            property=property_stmt,
            source=ObligationSource.TYPE,
            source_location=path,
            context=context,
        )

        self._obligations.append(obl)
        return obl

    def _type_to_property(
        self,
        input_type: str,
        output_type: str,
        effects: tuple[str, ...],
    ) -> str:
        """
        Convert type signature to formal property.

        Generates a universally quantified property stating that
        for all valid inputs, the function produces the expected output type.

        Args:
            input_type: Input type annotation
            output_type: Output type annotation
            effects: Declared side effects

        Returns:
            Formal property string
        """
        base = f"∀ x: {input_type}. invoke(x): {output_type}"

        if effects:
            effect_str = ", ".join(effects)
            base += f" {{ effects: {effect_str} }}"

        return base

    # =========================================================================
    # Composition Validation
    # =========================================================================

    def from_composition(
        self,
        pipeline_name: str,
        agents: tuple[str, ...],
        expected_type: str,
    ) -> ProofObligation:
        """
        Extract obligation from pipeline composition.

        When agents are composed via >>, type safety must be verified:
        Agent[A, B] >> Agent[B, C] → Agent[A, C]

        Args:
            pipeline_name: Name of the composed pipeline
            agents: Tuple of agent names in composition order
            expected_type: Expected final output type

        Returns:
            ProofObligation for composition safety

        Example:
            >>> obl = extractor.from_composition(
            ...     pipeline_name="ProcessPipeline",
            ...     agents=("Parser", "Validator", "Executor"),
            ...     expected_type="ExecutionResult",
            ... )
            >>> "composition" in obl.property.lower()
            True
        """
        obl_id = self._generate_id("comp")

        # Build composition expression
        chain = " >> ".join(agents)
        property_stmt = f"Composition({chain}) : {expected_type}"

        context = (
            f"Pipeline: {pipeline_name}",
            f"Agents: {', '.join(agents)}",
            "Law: (f >> g) >> h ≡ f >> (g >> h)",
        )

        obl = ProofObligation(
            id=obl_id,
            property=property_stmt,
            source=ObligationSource.COMPOSITION,
            source_location=pipeline_name,
            context=context[:MAX_CONTEXT_LINES],
        )

        self._obligations.append(obl)
        return obl

    # =========================================================================
    # Session Management
    # =========================================================================

    @property
    def obligations(self) -> list[ProofObligation]:
        """All obligations extracted in this session."""
        return list(self._obligations)

    @property
    def obligation_count(self) -> int:
        """Number of obligations extracted."""
        return len(self._obligations)

    def clear(self) -> None:
        """Clear all extracted obligations (start fresh session)."""
        self._obligations.clear()

    def to_dict(self) -> dict[str, Any]:
        """Serialize extraction session to dictionary."""
        return {
            "obligation_count": self.obligation_count,
            "obligations": [o.to_dict() for o in self._obligations],
        }


# =============================================================================
# Convenience Functions
# =============================================================================


def extract_from_pytest_report(report: dict[str, Any]) -> ProofObligation | None:
    """
    Extract obligation from a pytest JSON report entry.

    This function bridges pytest's output format to our obligation extractor.
    It handles the specific structure of pytest-json reports.

    Args:
        report: A single test result from pytest JSON output

    Returns:
        ProofObligation if the test failed, None otherwise

    Example:
        >>> report = {
        ...     "nodeid": "test_math.py::test_positive",
        ...     "outcome": "failed",
        ...     "longrepr": "assert x > 0\\nAssertionError",
        ... }
        >>> obl = extract_from_pytest_report(report)
        >>> obl is not None
        True
    """
    # Only process failures
    if report.get("outcome") != "failed":
        return None

    # Extract components from pytest report
    nodeid = report.get("nodeid", "unknown::unknown")
    longrepr = report.get("longrepr", "")

    # Parse nodeid: "path/to/test.py::test_function"
    if "::" in nodeid:
        source_file, test_name = nodeid.rsplit("::", 1)
    else:
        source_file = nodeid
        test_name = "unknown"

    # Extract assertion from longrepr
    assertion = "assert False"  # Default
    for line in str(longrepr).split("\n"):
        if "assert " in line.lower():
            assertion = line.strip()
            break

    # Extract line number if available
    line_number = report.get("lineno", 0)

    # Create extractor and extract
    extractor = ObligationExtractor()
    return extractor.from_test_failure(
        test_name=test_name,
        assertion=assertion,
        traceback=str(longrepr),
        source_file=source_file,
        line_number=line_number,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ObligationExtractor",
    "extract_from_pytest_report",
    "MAX_CONTEXT_LINES",
    "MAX_CONTEXT_LINE_LENGTH",
]
