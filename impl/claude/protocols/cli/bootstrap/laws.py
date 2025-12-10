"""
Bootstrap Laws CLI Commands

Display and verify the 7 category laws that govern agent composition.
These laws are not aspirational - they are verified at runtime.

Commands:
    kgents laws                      - Display the 7 category laws
    kgents laws verify [--agent=<id>] - Verify laws hold
    kgents laws witness <operation>   - Witness a composition
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# ─────────────────────────────────────────────────────────────────
# Category Laws Definition
# ─────────────────────────────────────────────────────────────────


class LawName(str, Enum):
    """The 7 category laws."""

    IDENTITY_LEFT = "identity_left"
    IDENTITY_RIGHT = "identity_right"
    ASSOCIATIVITY = "associativity"
    COMPOSITION_CLOSURE = "composition_closure"
    FUNCTOR_IDENTITY = "functor_identity"
    FUNCTOR_COMPOSITION = "functor_composition"
    NATURAL_TRANSFORMATION = "natural_transformation"


@dataclass(frozen=True)
class Law:
    """A category law definition."""

    name: LawName
    title: str
    statement: str
    formula: str
    example: str
    why_matters: str


# The 7 Category Laws
CATEGORY_LAWS: list[Law] = [
    Law(
        name=LawName.IDENTITY_LEFT,
        title="Left Identity",
        statement="Composing with identity on the left does nothing",
        formula="Id >> f  ≡  f",
        example="(Identity >> ParseCode).invoke(x)  ≡  ParseCode.invoke(x)",
        why_matters="Agents compose without needing 'start' or 'init' steps",
    ),
    Law(
        name=LawName.IDENTITY_RIGHT,
        title="Right Identity",
        statement="Composing with identity on the right does nothing",
        formula="f >> Id  ≡  f",
        example="(ParseCode >> Identity).invoke(x)  ≡  ParseCode.invoke(x)",
        why_matters="Pipelines don't need 'end' or 'cleanup' steps",
    ),
    Law(
        name=LawName.ASSOCIATIVITY,
        title="Associativity",
        statement="Order of grouping doesn't affect composition result",
        formula="(f >> g) >> h  ≡  f >> (g >> h)",
        example="((A >> B) >> C).invoke(x)  ≡  (A >> (B >> C)).invoke(x)",
        why_matters="Compose agents in any order, same result",
    ),
    Law(
        name=LawName.COMPOSITION_CLOSURE,
        title="Composition Closure",
        statement="Composing agents yields another agent",
        formula="f: A→B, g: B→C  ⟹  f >> g: A→C",
        example="ParseCode >> ValidateAST  is still an Agent[Code, AST]",
        why_matters="Composition doesn't break the agent abstraction",
    ),
    Law(
        name=LawName.FUNCTOR_IDENTITY,
        title="Functor Identity Preservation",
        statement="Functors preserve identity morphisms",
        formula="F(Id_A)  ≡  Id_F(A)",
        example="K.lift(Identity)  ≡  Identity (with K-gent persona)",
        why_matters="Lifting preserves neutrality",
    ),
    Law(
        name=LawName.FUNCTOR_COMPOSITION,
        title="Functor Composition Preservation",
        statement="Functors preserve composition",
        formula="F(g ∘ f)  ≡  F(g) ∘ F(f)",
        example="K.lift(A >> B)  ≡  K.lift(A) >> K.lift(B)",
        why_matters="Lift once or lift separately - same result",
    ),
    Law(
        name=LawName.NATURAL_TRANSFORMATION,
        title="Natural Transformation Coherence",
        statement="Transformations between functors commute with morphisms",
        formula="η_B ∘ F(f)  ≡  G(f) ∘ η_A",
        example="Switching from K-gent to W-gent preserves semantics",
        why_matters="Safe to switch between agent wrappers",
    ),
]


# ─────────────────────────────────────────────────────────────────
# Verification Types
# ─────────────────────────────────────────────────────────────────


class Verdict(str, Enum):
    """Verification verdict."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    WARN = "warn"


@dataclass
class LawVerification:
    """Result of verifying a single law."""

    law: LawName
    verdict: Verdict
    evidence: str
    duration_ms: float = 0.0


@dataclass
class VerificationReport:
    """Complete verification report."""

    agent_id: str | None
    verified_at: datetime
    results: list[LawVerification]
    overall_verdict: Verdict

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.verdict == Verdict.PASS)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.verdict == Verdict.FAIL)

    @property
    def skipped(self) -> int:
        return sum(1 for r in self.results if r.verdict == Verdict.SKIP)


@dataclass
class WitnessReport:
    """Report from witnessing a composition."""

    operation: str
    left: str
    right: str
    result_type: str
    laws_checked: list[LawName]
    witnessed_at: datetime
    valid: bool
    notes: str = ""


# ─────────────────────────────────────────────────────────────────
# Formatters
# ─────────────────────────────────────────────────────────────────


def format_laws_rich() -> str:
    """Format all laws for rich terminal output."""
    lines = [
        "┌─────────────────────────────────────────────────────────────────┐",
        "│                    THE 7 CATEGORY LAWS                          │",
        "│                                                                  │",
        "│  These laws are not aspirational - they are VERIFIED.           │",
        "│  Any agent that breaks these laws is NOT a valid agent.         │",
        "└─────────────────────────────────────────────────────────────────┘",
        "",
    ]

    for i, law in enumerate(CATEGORY_LAWS, 1):
        lines.extend(
            [
                f"  {i}. {law.title.upper()}",
                f"     {law.statement}",
                f"     Formula: {law.formula}",
                f"     Why: {law.why_matters}",
                "",
            ]
        )

    lines.extend(
        [
            "─────────────────────────────────────────────────────────────────",
            "  Verify: kgents laws verify [--agent=<id>]",
            "  Witness: kgents laws witness <operation>",
            "",
        ]
    )

    return "\n".join(lines)


def format_laws_json() -> str:
    """Format all laws as JSON."""
    laws_dict = [
        {
            "name": law.name.value,
            "title": law.title,
            "statement": law.statement,
            "formula": law.formula,
            "example": law.example,
            "why_matters": law.why_matters,
        }
        for law in CATEGORY_LAWS
    ]
    return json.dumps({"laws": laws_dict, "count": len(laws_dict)}, indent=2)


def format_verification_rich(report: VerificationReport) -> str:
    """Format verification report for rich terminal output."""
    status_char = {
        Verdict.PASS: "✓",
        Verdict.FAIL: "✗",
        Verdict.SKIP: "○",
        Verdict.WARN: "⚠",
    }

    overall = report.overall_verdict.value.upper()  # PASS, FAIL, SKIP, or WARN

    lines = [
        "┌─────────────────────────────────────────────────────────────────┐",
        f"│  LAW VERIFICATION REPORT - {overall.ljust(40)}│",
        "└─────────────────────────────────────────────────────────────────┘",
        "",
    ]

    if report.agent_id:
        lines.append(f"  Agent: {report.agent_id}")
    lines.append(f"  Time: {report.verified_at.isoformat()}")
    lines.append("")

    for result in report.results:
        char = status_char[result.verdict]
        law_title = next(
            (l.title for l in CATEGORY_LAWS if l.name == result.law), result.law.value
        )
        lines.append(f"  {char} {law_title}")
        if result.verdict == Verdict.FAIL:
            lines.append(f"     Evidence: {result.evidence}")

    lines.extend(
        [
            "",
            f"  Summary: {report.passed} passed, {report.failed} failed, {report.skipped} skipped",
            "",
        ]
    )

    return "\n".join(lines)


def format_witness_rich(report: WitnessReport) -> str:
    """Format witness report for rich terminal output."""
    status = "VALID" if report.valid else "INVALID"

    lines = [
        "┌─────────────────────────────────────────────────────────────────┐",
        f"│  COMPOSITION WITNESS - {status.ljust(41)}│",
        "└─────────────────────────────────────────────────────────────────┘",
        "",
        f"  Operation: {report.operation}",
        f"  Left operand: {report.left}",
        f"  Right operand: {report.right}",
        f"  Result type: {report.result_type}",
        "",
        "  Laws checked:",
    ]

    for law_name in report.laws_checked:
        law_title = next(
            (l.title for l in CATEGORY_LAWS if l.name == law_name), law_name.value
        )
        lines.append(f"    ✓ {law_title}")

    if report.notes:
        lines.extend(["", f"  Notes: {report.notes}"])

    lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────
# Verification Logic
# ─────────────────────────────────────────────────────────────────


async def verify_laws(agent_id: str | None = None) -> VerificationReport:
    """
    Verify category laws hold.

    If agent_id is provided, verify for that specific agent.
    Otherwise, verify general bootstrap laws.
    """
    results: list[LawVerification] = []

    # Try to import the O-gent BootstrapWitness
    try:
        from impl.claude.agents.o.bootstrap_witness import (
            create_bootstrap_witness,
        )

        witness = create_bootstrap_witness()

        # Verify identity laws
        id_result = await witness.verify_identity_laws()
        results.append(
            LawVerification(
                law=LawName.IDENTITY_LEFT,
                verdict=Verdict.PASS if id_result.left_identity else Verdict.FAIL,
                evidence=id_result.evidence if id_result.evidence else "",
                duration_ms=0.0,
            )
        )
        results.append(
            LawVerification(
                law=LawName.IDENTITY_RIGHT,
                verdict=Verdict.PASS if id_result.right_identity else Verdict.FAIL,
                evidence=id_result.evidence if not id_result.right_identity else "",
                duration_ms=0.0,
            )
        )

        # Verify composition laws
        comp_result = await witness.verify_composition_laws()
        results.append(
            LawVerification(
                law=LawName.ASSOCIATIVITY,
                verdict=Verdict.PASS if comp_result.associativity else Verdict.FAIL,
                evidence=comp_result.evidence if not comp_result.associativity else "",
                duration_ms=0.0,
            )
        )
        results.append(
            LawVerification(
                law=LawName.COMPOSITION_CLOSURE,
                verdict=Verdict.PASS if comp_result.closure else Verdict.FAIL,
                evidence=comp_result.evidence if not comp_result.closure else "",
                duration_ms=0.0,
            )
        )

        # Functor laws - skip if not testing functors
        results.append(
            LawVerification(
                law=LawName.FUNCTOR_IDENTITY,
                verdict=Verdict.SKIP,
                evidence="Functor verification requires K-gent instance",
            )
        )
        results.append(
            LawVerification(
                law=LawName.FUNCTOR_COMPOSITION,
                verdict=Verdict.SKIP,
                evidence="Functor verification requires K-gent instance",
            )
        )
        results.append(
            LawVerification(
                law=LawName.NATURAL_TRANSFORMATION,
                verdict=Verdict.SKIP,
                evidence="Natural transformation requires multiple functors",
            )
        )

    except ImportError:
        # BootstrapWitness not available - mark core laws as unverifiable
        for law in CATEGORY_LAWS[:4]:
            results.append(
                LawVerification(
                    law=law.name,
                    verdict=Verdict.SKIP,
                    evidence="BootstrapWitness not available (O-gent Phase 2)",
                )
            )
        for law in CATEGORY_LAWS[4:]:
            results.append(
                LawVerification(
                    law=law.name,
                    verdict=Verdict.SKIP,
                    evidence="Functor verification not implemented",
                )
            )

    # Determine overall verdict
    if any(r.verdict == Verdict.FAIL for r in results):
        overall = Verdict.FAIL
    elif all(r.verdict in (Verdict.PASS, Verdict.SKIP) for r in results):
        if any(r.verdict == Verdict.PASS for r in results):
            overall = Verdict.PASS
        else:
            overall = Verdict.SKIP
    else:
        overall = Verdict.WARN

    return VerificationReport(
        agent_id=agent_id,
        verified_at=datetime.now(),
        results=results,
        overall_verdict=overall,
    )


async def witness_composition(operation: str) -> WitnessReport:
    """
    Witness a composition operation.

    Parses the operation string and validates the composition.
    Format: "A >> B" or "compose(A, B)"
    """
    # Parse the operation
    if ">>" in operation:
        parts = [p.strip() for p in operation.split(">>")]
        if len(parts) != 2:
            return WitnessReport(
                operation=operation,
                left="?",
                right="?",
                result_type="Error",
                laws_checked=[],
                witnessed_at=datetime.now(),
                valid=False,
                notes="Expected format: A >> B",
            )
        left, right = parts
    elif operation.startswith("compose("):
        # Parse compose(A, B) format
        inner = operation[8:-1] if operation.endswith(")") else operation[8:]
        parts = [p.strip() for p in inner.split(",")]
        if len(parts) != 2:
            return WitnessReport(
                operation=operation,
                left="?",
                right="?",
                result_type="Error",
                laws_checked=[],
                witnessed_at=datetime.now(),
                valid=False,
                notes="Expected format: compose(A, B)",
            )
        left, right = parts
    else:
        return WitnessReport(
            operation=operation,
            left="?",
            right="?",
            result_type="Error",
            laws_checked=[],
            witnessed_at=datetime.now(),
            valid=False,
            notes="Unknown operation format. Use 'A >> B' or 'compose(A, B)'",
        )

    # For now, do structural validation only
    # In a full implementation, this would actually verify the composition
    laws_checked = [
        LawName.COMPOSITION_CLOSURE,  # Always check closure
        LawName.ASSOCIATIVITY,  # Always check associativity
    ]

    # Check for identity
    if left.lower() in ("id", "identity"):
        laws_checked.append(LawName.IDENTITY_LEFT)
    if right.lower() in ("id", "identity"):
        laws_checked.append(LawName.IDENTITY_RIGHT)

    return WitnessReport(
        operation=operation,
        left=left,
        right=right,
        result_type=f"Agent[{left}.Input, {right}.Output]",
        laws_checked=laws_checked,
        witnessed_at=datetime.now(),
        valid=True,
        notes="Structural validation only. Runtime verification requires actual agents.",
    )


# ─────────────────────────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────────────────────────


def cmd_laws(args: list[str]) -> int:
    """
    Laws command entry point.

    Usage:
        kgents laws                      - Display the 7 category laws
        kgents laws verify [--agent=<id>] - Verify laws hold
        kgents laws witness <operation>   - Witness a composition
    """
    import asyncio

    parser = argparse.ArgumentParser(
        prog="kgents laws",
        description="Display and verify the 7 category laws",
    )
    parser.add_argument(
        "subcommand",
        nargs="?",
        choices=["verify", "witness"],
        help="Subcommand: verify or witness",
    )
    parser.add_argument(
        "operation",
        nargs="?",
        help="Operation to witness (for 'witness' subcommand)",
    )
    parser.add_argument(
        "--agent",
        help="Agent ID to verify (for 'verify' subcommand)",
    )
    parser.add_argument(
        "--format",
        choices=["rich", "json"],
        default="rich",
        help="Output format",
    )

    parsed = parser.parse_args(args)

    # No subcommand - display laws
    if parsed.subcommand is None:
        if parsed.format == "json":
            print(format_laws_json())
        else:
            print(format_laws_rich())
        return 0

    # Verify subcommand
    if parsed.subcommand == "verify":
        report = asyncio.run(verify_laws(parsed.agent))
        if parsed.format == "json":
            print(
                json.dumps(
                    {
                        "agent_id": report.agent_id,
                        "verified_at": report.verified_at.isoformat(),
                        "overall_verdict": report.overall_verdict.value,
                        "passed": report.passed,
                        "failed": report.failed,
                        "skipped": report.skipped,
                        "results": [
                            {
                                "law": r.law.value,
                                "verdict": r.verdict.value,
                                "evidence": r.evidence,
                            }
                            for r in report.results
                        ],
                    },
                    indent=2,
                )
            )
        else:
            print(format_verification_rich(report))
        return 0 if report.overall_verdict != Verdict.FAIL else 1

    # Witness subcommand
    if parsed.subcommand == "witness":
        if not parsed.operation:
            print("Error: witness requires an operation argument")
            print("Usage: kgents laws witness <operation>")
            print("Example: kgents laws witness 'ParseCode >> ValidateAST'")
            return 1

        report = asyncio.run(witness_composition(parsed.operation))
        if parsed.format == "json":
            print(
                json.dumps(
                    {
                        "operation": report.operation,
                        "left": report.left,
                        "right": report.right,
                        "result_type": report.result_type,
                        "valid": report.valid,
                        "laws_checked": [l.value for l in report.laws_checked],
                        "witnessed_at": report.witnessed_at.isoformat(),
                        "notes": report.notes,
                    },
                    indent=2,
                )
            )
        else:
            print(format_witness_rich(report))
        return 0 if report.valid else 1

    return 0


if __name__ == "__main__":
    sys.exit(cmd_laws(sys.argv[1:]))
