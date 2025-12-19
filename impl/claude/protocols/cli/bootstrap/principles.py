"""
Bootstrap Principles CLI Commands

Display and evaluate against the 7 design principles that guide kgents.

Commands:
    kgents principles               - Display the 7 design principles
    kgents principles check <input> - Evaluate input against principles
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

# ─────────────────────────────────────────────────────────────────
# Principle Definitions
# ─────────────────────────────────────────────────────────────────


class PrincipleName(str, Enum):
    """The 7 design principles."""

    TASTEFUL = "tasteful"
    CURATED = "curated"
    ETHICAL = "ethical"
    JOY_INDUCING = "joy_inducing"
    COMPOSABLE = "composable"
    HETERARCHICAL = "heterarchical"
    GENERATIVE = "generative"


@dataclass(frozen=True)
class Principle:
    """A design principle definition."""

    name: PrincipleName
    title: str
    essence: str
    question: str
    anti_patterns: list[str]


# The 7 Design Principles
DESIGN_PRINCIPLES: list[Principle] = [
    Principle(
        name=PrincipleName.TASTEFUL,
        title="Tasteful",
        essence="Each agent serves a clear, justified purpose",
        question="Does this agent have a clear, justified purpose?",
        anti_patterns=[
            "Agents that do 'everything'",
            "Kitchen-sink configurations",
            "Agents added 'just in case'",
        ],
    ),
    Principle(
        name=PrincipleName.CURATED,
        title="Curated",
        essence="Intentional selection over exhaustive cataloging",
        question="Does this add unique value, or does something similar exist?",
        anti_patterns=[
            "'Awesome list' sprawl",
            "Duplicative agents with slight variations",
            "Legacy agents kept for nostalgia",
        ],
    ),
    Principle(
        name=PrincipleName.ETHICAL,
        title="Ethical",
        essence="Agents augment human capability, never replace judgment",
        question="Does this respect human agency and privacy?",
        anti_patterns=[
            "Agents that claim certainty they don't have",
            "Hidden data collection",
            "Agents that manipulate rather than assist",
            "'Trust me' without explanation",
        ],
    ),
    Principle(
        name=PrincipleName.JOY_INDUCING,
        title="Joy-Inducing",
        essence="Delight in interaction; personality matters",
        question="Would I enjoy interacting with this?",
        anti_patterns=[
            "Robotic, lifeless responses",
            "Needless formality",
            "Agents that feel like forms to fill out",
        ],
    ),
    Principle(
        name=PrincipleName.COMPOSABLE,
        title="Composable",
        essence="Agents are morphisms in a category; composition is primary",
        question="Can this work with other agents?",
        anti_patterns=[
            "Monolithic agents that can't be broken apart",
            "Agents with hidden state that prevents composition",
            "'God agents' that must be used alone",
        ],
    ),
    Principle(
        name=PrincipleName.HETERARCHICAL,
        title="Heterarchical",
        essence="Agents exist in flux, not fixed hierarchy",
        question="Can this agent both lead and follow?",
        anti_patterns=[
            "Permanent orchestrator/worker relationships",
            "Agents that can only be called, never run autonomously",
            "Fixed resource budgets",
            "'Chain of command' that prevents peer interaction",
        ],
    ),
    Principle(
        name=PrincipleName.GENERATIVE,
        title="Generative",
        essence="Spec is compression; design should generate implementation",
        question="Could this be regenerated from spec?",
        anti_patterns=[
            "Specs that merely describe existing code",
            "Implementations that diverge from spec",
            "Designs requiring extensive prose to explain",
        ],
    ),
]


# ─────────────────────────────────────────────────────────────────
# Evaluation Types
# ─────────────────────────────────────────────────────────────────


class Verdict(str, Enum):
    """Evaluation verdict."""

    ACCEPT = "accept"
    REJECT = "reject"
    REVISE = "revise"
    UNCLEAR = "unclear"


@dataclass
class PrincipleEvaluation:
    """Result of evaluating against a single principle."""

    principle: PrincipleName
    verdict: Verdict
    reasoning: str
    confidence: float = 0.0  # 0.0 to 1.0
    suggestions: list[str] = field(default_factory=list)


@dataclass
class EvaluationReport:
    """Complete evaluation report."""

    input_description: str
    evaluated_at: datetime
    evaluations: list[PrincipleEvaluation]
    overall_verdict: Verdict
    summary: str

    @property
    def accepted(self) -> int:
        return sum(1 for e in self.evaluations if e.verdict == Verdict.ACCEPT)

    @property
    def rejected(self) -> int:
        return sum(1 for e in self.evaluations if e.verdict == Verdict.REJECT)

    @property
    def unclear(self) -> int:
        return sum(1 for e in self.evaluations if e.verdict == Verdict.UNCLEAR)


# ─────────────────────────────────────────────────────────────────
# Formatters
# ─────────────────────────────────────────────────────────────────


def format_principles_rich() -> str:
    """Format all principles for rich terminal output."""
    lines = [
        "┌─────────────────────────────────────────────────────────────────┐",
        "│                  THE 7 DESIGN PRINCIPLES                        │",
        "│                                                                  │",
        "│  These principles guide ALL kgents design decisions.            │",
        "│  A 'no' on any principle is a signal to reconsider.             │",
        "└─────────────────────────────────────────────────────────────────┘",
        "",
    ]

    for i, principle in enumerate(DESIGN_PRINCIPLES, 1):
        lines.extend(
            [
                f"  {i}. {principle.title.upper()}",
                f'     "{principle.essence}"',
                f"     Question: {principle.question}",
                "     Anti-patterns:",
            ]
        )
        for anti in principle.anti_patterns[:2]:  # Show first 2
            lines.append(f"       - {anti}")
        lines.append("")

    lines.extend(
        [
            "─────────────────────────────────────────────────────────────────",
            "  Check: kgents principles check <input>",
            "",
        ]
    )

    return "\n".join(lines)


def format_principles_json() -> str:
    """Format all principles as JSON."""
    principles_dict = [
        {
            "name": p.name.value,
            "title": p.title,
            "essence": p.essence,
            "question": p.question,
            "anti_patterns": p.anti_patterns,
        }
        for p in DESIGN_PRINCIPLES
    ]
    return json.dumps({"principles": principles_dict, "count": len(principles_dict)}, indent=2)


def format_evaluation_rich(report: EvaluationReport) -> str:
    """Format evaluation report for rich terminal output."""
    verdict_char = {
        Verdict.ACCEPT: "✓",
        Verdict.REJECT: "✗",
        Verdict.REVISE: "↻",
        Verdict.UNCLEAR: "?",
    }

    overall = report.overall_verdict.value.upper()

    lines = [
        "┌─────────────────────────────────────────────────────────────────┐",
        f"│  PRINCIPLE EVALUATION - {overall.ljust(40)}│",
        "└─────────────────────────────────────────────────────────────────┘",
        "",
        f"  Input: {report.input_description[:50]}{'...' if len(report.input_description) > 50 else ''}",
        f"  Time: {report.evaluated_at.isoformat()}",
        "",
    ]

    for evaluation in report.evaluations:
        char = verdict_char[evaluation.verdict]
        principle_title = next(
            (p.title for p in DESIGN_PRINCIPLES if p.name == evaluation.principle),
            evaluation.principle.value,
        )
        confidence_bar = "█" * int(evaluation.confidence * 5) + "░" * (
            5 - int(evaluation.confidence * 5)
        )

        lines.append(f"  {char} {principle_title} [{confidence_bar}]")
        if evaluation.reasoning:
            # Wrap reasoning to fit
            words = evaluation.reasoning.split()
            line = "     "
            for word in words:
                if len(line) + len(word) + 1 > 65:
                    lines.append(line)
                    line = "     " + word
                else:
                    line = line + " " + word if line.strip() else "     " + word
            if line.strip():
                lines.append(line)

        if evaluation.suggestions:
            lines.append("     Suggestions:")
            for suggestion in evaluation.suggestions[:2]:
                lines.append(f"       → {suggestion}")
        lines.append("")

    lines.extend(
        [
            f"  Summary: {report.summary}",
            f"  Score: {report.accepted}/{len(report.evaluations)} principles accepted",
            "",
        ]
    )

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────
# Evaluation Logic
# ─────────────────────────────────────────────────────────────────


async def evaluate_against_principles(
    input_text: str,
    use_llm: bool = False,
) -> EvaluationReport:
    """
    Evaluate input against the 7 design principles.

    Args:
        input_text: Text describing an agent, design, or proposal
        use_llm: If True, use LLM for deep analysis (requires API)

    Returns:
        EvaluationReport with per-principle evaluations
    """
    evaluations: list[PrincipleEvaluation] = []
    input_lower = input_text.lower()

    # Heuristic-based evaluation (Phase 1)
    # In Phase 2, this would integrate with an LLM for semantic analysis

    # 1. Tasteful
    tasteful_signals = ["clear purpose", "focused", "justified", "one thing"]
    tasteful_anti = ["everything", "all-in-one", "kitchen sink", "just in case"]
    tasteful_score = sum(1 for s in tasteful_signals if s in input_lower)
    tasteful_anti_score = sum(1 for s in tasteful_anti if s in input_lower)

    if tasteful_anti_score > 0:
        tasteful_verdict = Verdict.REJECT
        tasteful_reasoning = "Contains anti-pattern signals: feature sprawl detected"
    elif tasteful_score > 0:
        tasteful_verdict = Verdict.ACCEPT
        tasteful_reasoning = "Shows clear purpose and focus"
    else:
        tasteful_verdict = Verdict.UNCLEAR
        tasteful_reasoning = "Unable to assess purpose clarity from input"

    evaluations.append(
        PrincipleEvaluation(
            principle=PrincipleName.TASTEFUL,
            verdict=tasteful_verdict,
            reasoning=tasteful_reasoning,
            confidence=0.6 if tasteful_score > 0 or tasteful_anti_score > 0 else 0.3,
            suggestions=["Define a single clear purpose"]
            if tasteful_verdict != Verdict.ACCEPT
            else [],
        )
    )

    # 2. Curated
    curated_signals = ["unique", "essential", "core", "necessary"]
    curated_anti = ["comprehensive", "exhaustive", "all", "complete list"]

    curated_score = sum(1 for s in curated_signals if s in input_lower)
    curated_anti_score = sum(1 for s in curated_anti if s in input_lower)

    if curated_anti_score > 0:
        curated_verdict = Verdict.REVISE
        curated_reasoning = "May be accumulating rather than curating"
    elif curated_score > 0:
        curated_verdict = Verdict.ACCEPT
        curated_reasoning = "Shows intentional selection"
    else:
        curated_verdict = Verdict.UNCLEAR
        curated_reasoning = "Unable to assess curation from input"

    evaluations.append(
        PrincipleEvaluation(
            principle=PrincipleName.CURATED,
            verdict=curated_verdict,
            reasoning=curated_reasoning,
            confidence=0.5 if curated_score > 0 or curated_anti_score > 0 else 0.3,
            suggestions=["Consider what can be removed"]
            if curated_verdict == Verdict.REVISE
            else [],
        )
    )

    # 3. Ethical
    ethical_signals = ["transparent", "privacy", "human", "agency", "honest"]
    ethical_anti = ["hidden", "manipulate", "certain", "trust me"]

    ethical_score = sum(1 for s in ethical_signals if s in input_lower)
    ethical_anti_score = sum(1 for s in ethical_anti if s in input_lower)

    if ethical_anti_score > 0:
        ethical_verdict = Verdict.REJECT
        ethical_reasoning = "Contains concerning patterns around transparency/agency"
    elif ethical_score > 0:
        ethical_verdict = Verdict.ACCEPT
        ethical_reasoning = "Shows respect for human agency"
    else:
        ethical_verdict = Verdict.UNCLEAR
        ethical_reasoning = "Unable to assess ethical considerations from input"

    evaluations.append(
        PrincipleEvaluation(
            principle=PrincipleName.ETHICAL,
            verdict=ethical_verdict,
            reasoning=ethical_reasoning,
            confidence=0.7 if ethical_anti_score > 0 else 0.4,
            suggestions=["Add transparency about limitations"]
            if ethical_verdict != Verdict.ACCEPT
            else [],
        )
    )

    # 4. Joy-Inducing
    joy_signals = ["delight", "personality", "warm", "playful", "fun"]
    joy_anti = ["robotic", "formal", "sterile", "cold"]

    joy_score = sum(1 for s in joy_signals if s in input_lower)
    joy_anti_score = sum(1 for s in joy_anti if s in input_lower)

    if joy_anti_score > 0:
        joy_verdict = Verdict.REVISE
        joy_reasoning = "May lack warmth or personality"
    elif joy_score > 0:
        joy_verdict = Verdict.ACCEPT
        joy_reasoning = "Shows attention to user delight"
    else:
        joy_verdict = Verdict.UNCLEAR
        joy_reasoning = "Unable to assess joy factor from input"

    evaluations.append(
        PrincipleEvaluation(
            principle=PrincipleName.JOY_INDUCING,
            verdict=joy_verdict,
            reasoning=joy_reasoning,
            confidence=0.4 if joy_score > 0 or joy_anti_score > 0 else 0.2,
            suggestions=["Consider adding personality"] if joy_verdict != Verdict.ACCEPT else [],
        )
    )

    # 5. Composable
    composable_signals = ["compose", "combine", "modular", "interface", "pipeline"]
    composable_anti = ["monolithic", "all-in-one", "standalone", "god"]

    composable_score = sum(1 for s in composable_signals if s in input_lower)
    composable_anti_score = sum(1 for s in composable_anti if s in input_lower)

    if composable_anti_score > 0:
        composable_verdict = Verdict.REJECT
        composable_reasoning = "Design appears monolithic"
    elif composable_score > 0:
        composable_verdict = Verdict.ACCEPT
        composable_reasoning = "Shows composable design"
    else:
        composable_verdict = Verdict.UNCLEAR
        composable_reasoning = "Unable to assess composability from input"

    evaluations.append(
        PrincipleEvaluation(
            principle=PrincipleName.COMPOSABLE,
            verdict=composable_verdict,
            reasoning=composable_reasoning,
            confidence=0.6 if composable_score > 0 or composable_anti_score > 0 else 0.3,
            suggestions=["Define clear input/output types"]
            if composable_verdict != Verdict.ACCEPT
            else [],
        )
    )

    # 6. Heterarchical
    hetero_signals = ["flexible", "autonomous", "peer", "dynamic", "flux"]
    hetero_anti = ["hierarchy", "orchestrator", "master", "slave", "fixed"]

    hetero_score = sum(1 for s in hetero_signals if s in input_lower)
    hetero_anti_score = sum(1 for s in hetero_anti if s in input_lower)

    if hetero_anti_score > 0:
        hetero_verdict = Verdict.REVISE
        hetero_reasoning = "May impose fixed hierarchy"
    elif hetero_score > 0:
        hetero_verdict = Verdict.ACCEPT
        hetero_reasoning = "Shows heterarchical design"
    else:
        hetero_verdict = Verdict.UNCLEAR
        hetero_reasoning = "Unable to assess hierarchy from input"

    evaluations.append(
        PrincipleEvaluation(
            principle=PrincipleName.HETERARCHICAL,
            verdict=hetero_verdict,
            reasoning=hetero_reasoning,
            confidence=0.5 if hetero_score > 0 or hetero_anti_score > 0 else 0.3,
            suggestions=["Allow both autonomous and composed modes"]
            if hetero_verdict != Verdict.ACCEPT
            else [],
        )
    )

    # 7. Generative
    generative_signals = ["spec", "generate", "derive", "compress", "regenerate"]
    generative_anti = ["documentation", "describe", "prose", "manual"]

    generative_score = sum(1 for s in generative_signals if s in input_lower)
    generative_anti_score = sum(1 for s in generative_anti if s in input_lower)

    if generative_anti_score > 0:
        generative_verdict = Verdict.REVISE
        generative_reasoning = "May be documentation rather than generative spec"
    elif generative_score > 0:
        generative_verdict = Verdict.ACCEPT
        generative_reasoning = "Shows generative design intent"
    else:
        generative_verdict = Verdict.UNCLEAR
        generative_reasoning = "Unable to assess generativity from input"

    evaluations.append(
        PrincipleEvaluation(
            principle=PrincipleName.GENERATIVE,
            verdict=generative_verdict,
            reasoning=generative_reasoning,
            confidence=0.5 if generative_score > 0 or generative_anti_score > 0 else 0.3,
            suggestions=["Write spec that can regenerate implementation"]
            if generative_verdict != Verdict.ACCEPT
            else [],
        )
    )

    # Determine overall verdict
    reject_count = sum(1 for e in evaluations if e.verdict == Verdict.REJECT)
    revise_count = sum(1 for e in evaluations if e.verdict == Verdict.REVISE)
    accept_count = sum(1 for e in evaluations if e.verdict == Verdict.ACCEPT)

    if reject_count > 0:
        overall = Verdict.REJECT
        summary = f"Rejected: {reject_count} principle(s) failed"
    elif revise_count > 1:
        overall = Verdict.REVISE
        summary = f"Needs revision: {revise_count} principle(s) need attention"
    elif accept_count >= 4:
        overall = Verdict.ACCEPT
        summary = f"Accepted: {accept_count}/7 principles clearly satisfied"
    else:
        overall = Verdict.UNCLEAR
        summary = "Insufficient information for clear verdict"

    return EvaluationReport(
        input_description=input_text[:100],
        evaluated_at=datetime.now(),
        evaluations=evaluations,
        overall_verdict=overall,
        summary=summary,
    )


async def evaluate_file(file_path: Path) -> EvaluationReport:
    """Evaluate a file's contents against principles."""
    if not file_path.exists():
        return EvaluationReport(
            input_description=f"File not found: {file_path}",
            evaluated_at=datetime.now(),
            evaluations=[],
            overall_verdict=Verdict.REJECT,
            summary="File not found",
        )

    content = file_path.read_text()
    return await evaluate_against_principles(content)


# ─────────────────────────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────────────────────────


def cmd_principles(args: list[str]) -> int:
    """
    Principles command entry point.

    Usage:
        kgents principles               - Display the 7 design principles
        kgents principles check <input> - Evaluate input against principles
    """
    import asyncio

    parser = argparse.ArgumentParser(
        prog="kgents principles",
        description="Display and check against the 7 design principles",
    )
    parser.add_argument(
        "subcommand",
        nargs="?",
        choices=["check"],
        help="Subcommand: check",
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input to check (text or file path)",
    )
    parser.add_argument(
        "--format",
        choices=["rich", "json"],
        default="rich",
        help="Output format",
    )

    parsed = parser.parse_args(args)

    # No subcommand - display principles
    if parsed.subcommand is None:
        if parsed.format == "json":
            print(format_principles_json())
        else:
            print(format_principles_rich())
        return 0

    # Check subcommand
    if parsed.subcommand == "check":
        if not parsed.input:
            print("Error: check requires input text or file path")
            print("Usage: kgents principles check <input>")
            print('Example: kgents principles check "A monolithic agent that does everything"')
            return 1

        # Check if input is a file path
        input_path = Path(parsed.input)
        if input_path.exists():
            report = asyncio.run(evaluate_file(input_path))
        else:
            # Treat as text input
            report = asyncio.run(evaluate_against_principles(parsed.input))

        if parsed.format == "json":
            print(
                json.dumps(
                    {
                        "input": report.input_description,
                        "evaluated_at": report.evaluated_at.isoformat(),
                        "overall_verdict": report.overall_verdict.value,
                        "accepted": report.accepted,
                        "rejected": report.rejected,
                        "unclear": report.unclear,
                        "summary": report.summary,
                        "evaluations": [
                            {
                                "principle": e.principle.value,
                                "verdict": e.verdict.value,
                                "reasoning": e.reasoning,
                                "confidence": e.confidence,
                                "suggestions": e.suggestions,
                            }
                            for e in report.evaluations
                        ],
                    },
                    indent=2,
                )
            )
        else:
            print(format_evaluation_rich(report))

        # Return code based on verdict
        if report.overall_verdict == Verdict.ACCEPT:
            return 0
        elif report.overall_verdict == Verdict.REJECT:
            return 1
        else:
            return 0  # Unclear/Revise are not failures

    return 0


if __name__ == "__main__":
    sys.exit(cmd_principles(sys.argv[1:]))
