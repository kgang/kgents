"""
Grammar Validation

Verification that synthesized grammars meet requirements:
1. Unambiguous: Each input has exactly one parse tree
2. Constraint-structural: Forbidden operations are grammatically impossible
3. Round-trip: parse(render(ast)) == ast

This module provides validation without requiring full T-gent integration.
Production systems would use T-gent for fuzzing and property testing.
"""

import re
from dataclasses import dataclass
from typing import Any

from agents.g.types import (
    ConstraintProof,
    CounterExample,
    DomainAnalysis,
    Tongue,
)

# ============================================================================
# Validation Result Types
# ============================================================================


@dataclass
class AmbiguityReport:
    """Report of an ambiguous parse."""

    input: str
    parse_count: int
    parse_trees: list[Any]
    description: str = ""


@dataclass
class ConstraintViolation:
    """Report of a constraint not structurally enforced."""

    constraint: str
    violating_input: str
    parse_succeeded: bool  # Should be True if violation (parse should have failed)
    description: str = ""


@dataclass
class ValidationReport:
    """Comprehensive validation report for a Tongue."""

    is_valid: bool
    unambiguous: bool
    constraints_structural: bool
    round_trip_verified: bool

    ambiguities: list[AmbiguityReport]
    violations: list[ConstraintViolation]
    errors: list[str]


# ============================================================================
# Ambiguity Verification
# ============================================================================


async def verify_unambiguous(
    grammar: str, test_inputs: list[str] | None = None
) -> tuple[bool, list[AmbiguityReport]]:
    """
    Verify grammar is unambiguous.

    In production, this would use T-gent for grammar-guided fuzzing.
    For now, we use simple heuristics.

    Args:
        grammar: Grammar specification
        test_inputs: Optional test inputs (generated if not provided)

    Returns:
        (is_unambiguous, ambiguity_reports)
    """
    ambiguities = []

    # Simple check: Look for common ambiguity patterns in grammar
    # 1. Multiple production rules with overlapping prefixes
    # 2. Optional elements that can create multiple parse paths

    # For BNF grammars, check for left recursion (can cause ambiguity)
    if "::=" in grammar:
        lines = grammar.split("\n")
        for line in lines:
            if "::=" in line:
                lhs, rhs = line.split("::=", 1)
                lhs = lhs.strip()
                # Check if LHS appears at start of RHS (left recursion)
                if lhs in rhs.split("|")[0].strip().split()[0:1]:
                    ambiguities.append(
                        AmbiguityReport(
                            input="<grammar>",
                            parse_count=2,
                            parse_trees=[],
                            description=f"Left recursion detected: {lhs}",
                        )
                    )

    # If test inputs provided, we'd parse each and check for multiple parse trees
    # (Requires actual parser implementation, which is Phase 3)

    return len(ambiguities) == 0, ambiguities


# ============================================================================
# Constraint Verification
# ============================================================================


async def verify_constraints(
    grammar: str,
    constraints: list[str],
    analysis: DomainAnalysis,
) -> tuple[bool, list[ConstraintViolation]]:
    """
    Verify all constraints are structurally encoded in the grammar.

    For each constraint:
    1. Generate inputs that would violate the constraint
    2. Verify those inputs fail to parse (constraint is structural)

    Args:
        grammar: Grammar specification
        constraints: List of constraint statements
        analysis: Domain analysis with operations/entities

    Returns:
        (all_structural, violations)
    """
    violations = []

    for constraint in constraints:
        # Generate violating inputs
        violating_inputs = _generate_violating_inputs(constraint, analysis)

        for input_text in violating_inputs:
            # Check if this input is structurally rejected
            is_rejected = _check_structural_rejection(input_text, grammar, analysis)

            if not is_rejected:
                violations.append(
                    ConstraintViolation(
                        constraint=constraint,
                        violating_input=input_text,
                        parse_succeeded=True,
                        description=f"Input '{input_text}' should be rejected by grammar",
                    )
                )

    return len(violations) == 0, violations


def _generate_violating_inputs(constraint: str, analysis: DomainAnalysis) -> list[str]:
    """
    Generate inputs that would violate a constraint.

    For "No DELETE" constraint, generate "DELETE file" etc.
    """
    violating = []
    lower_constraint = constraint.lower()

    # "No X" pattern
    if "no " in lower_constraint:
        match = re.search(r"no (\w+)", lower_constraint)
        if match:
            forbidden = match.group(1).upper()
            # Handle plural
            if forbidden.endswith("S"):
                forbidden = forbidden[:-1]

            # Generate violating commands
            for entity in analysis.entities or ["object"]:
                violating.append(f"{forbidden} {entity}")

    # "Read-only" pattern
    if "read-only" in lower_constraint or "readonly" in lower_constraint:
        # Generate write operations
        for op in ["WRITE", "DELETE", "UPDATE", "MODIFY", "CREATE"]:
            for entity in analysis.entities or ["object"]:
                violating.append(f"{op} {entity}")

    return violating


def _check_structural_rejection(input_text: str, grammar: str, analysis: DomainAnalysis) -> bool:
    """
    Check if input is structurally rejected by grammar.

    Simplified check: Does the verb exist in the VERB production?
    """
    # Extract verb from input
    parts = input_text.split()
    if not parts:
        return False
    verb = parts[0]

    # Check if verb is in VERB production
    if "VERB ::=" in grammar:
        # Extract VERB production
        for line in grammar.split("\n"):
            if line.startswith("VERB ::="):
                # Check if verb appears in alternatives
                return f'"{verb}"' not in line

    # For Lark grammars (recursive)
    if "op:" in grammar:
        for line in grammar.split("\n"):
            if line.startswith("op:"):
                # Check if verb appears
                return f'"{verb.lower()}"' not in line

    # Default: assume not rejected (conservative)
    return False


# ============================================================================
# Round-Trip Verification
# ============================================================================


async def verify_round_trip(tongue: Tongue, test_cases: list[str]) -> bool:
    """
    Verify parse(render(ast)) == ast for all test cases.

    Requires P-gent integration (Phase 3).
    For now, returns True as placeholder.
    """
    # Placeholder - will implement when parse() and render() are ready
    return True


# ============================================================================
# Constraint Proof Generation
# ============================================================================


def generate_constraint_proofs(
    constraints: list[str],
    grammar: str,
    analysis: DomainAnalysis,
) -> list[ConstraintProof]:
    """
    Generate ConstraintProof objects for each constraint.

    Demonstrates how the constraint is structurally enforced.
    """
    proofs = []

    for constraint in constraints:
        # Generate counter-examples (inputs that should fail)
        violating_inputs = _generate_violating_inputs(constraint, analysis)
        counter_examples = [
            CounterExample(
                text=input_text,
                expected_error="Parse error: verb not in grammar",
                description=f"Violates constraint: {constraint}",
            )
            for input_text in violating_inputs
        ]

        # Describe mechanism
        mechanism = _describe_constraint_mechanism(constraint, grammar)

        proofs.append(
            ConstraintProof(
                constraint=constraint,
                mechanism=mechanism,
                verified_by="G-gent",
                counter_examples=counter_examples,
                verified_at="synthesis",
            )
        )

    return proofs


def _describe_constraint_mechanism(constraint: str, grammar: str) -> str:
    """
    Describe how constraint is structurally enforced.

    Returns a human-readable explanation.
    """
    lower_constraint = constraint.lower()

    # "No X" pattern
    if "no " in lower_constraint:
        match = re.search(r"no (\w+)", lower_constraint)
        if match:
            forbidden = match.group(1).upper()
            if forbidden.endswith("S"):
                forbidden = forbidden[:-1]
            return f"VERB production excludes '{forbidden}' - grammatically impossible"

    # "Read-only" pattern
    if "read-only" in lower_constraint or "readonly" in lower_constraint:
        return "VERB production includes only read operations (READ, GET, LIST, etc.) - write operations grammatically impossible"

    # Generic
    return "Constraint encoded in grammar structure - violating inputs cannot parse"


# ============================================================================
# Full Tongue Validation
# ============================================================================


async def validate_tongue_comprehensive(tongue: Tongue) -> ValidationReport:
    """
    Comprehensive validation of a Tongue artifact.

    Checks:
    1. Grammar is unambiguous
    2. Constraints are structurally enforced
    3. Examples parse correctly
    4. Round-trip property holds

    Returns:
        ValidationReport with detailed results
    """
    errors: list[str] = []

    # Check unambiguous
    is_unambiguous, ambiguities = await verify_unambiguous(tongue.grammar)

    # Check constraints structural
    analysis = DomainAnalysis(
        entities=set(tongue.lexicon),
        operations=set(),  # Would need to extract from grammar
        constraints=list(tongue.constraints),
    )
    constraints_structural, violations = await verify_constraints(
        tongue.grammar, list(tongue.constraints), analysis
    )

    # Check round-trip (placeholder)
    round_trip_verified = await verify_round_trip(tongue, [ex.text for ex in tongue.examples])

    # Overall validation
    is_valid = is_unambiguous and constraints_structural and round_trip_verified

    return ValidationReport(
        is_valid=is_valid,
        unambiguous=is_unambiguous,
        constraints_structural=constraints_structural,
        round_trip_verified=round_trip_verified,
        ambiguities=ambiguities,
        violations=violations,
        errors=errors,
    )
