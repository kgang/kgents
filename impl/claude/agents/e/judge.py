"""
Code Judge Agent: Evaluate improvements against the 7 kgents principles.

This agent provides principle-based evaluation of code improvements:
1. Tasteful - Clear purpose, no bloat
2. Curated - Quality over quantity
3. Ethical - No concerning patterns
4. Joyful - Readable, well-structured
5. Composable - Follows agent patterns
6. Heterarchical - Not creating god objects
7. Generative - Could be regenerated from spec

Morphism: JudgeInput → JudgeResult
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from bootstrap.types import Agent, Verdict, VerdictType

from .experiment import CodeImprovement


@dataclass(frozen=True)
class JudgeInput:
    """Input for code judgment."""
    improvement: CodeImprovement
    original_code: str
    module_name: str


@dataclass(frozen=True)
class PrincipleScore:
    """Score for a single principle."""
    name: str
    score: float  # 0.0 - 1.0
    reason: Optional[str] = None


@dataclass(frozen=True)
class JudgeResult:
    """Result of code judgment."""
    verdict: Verdict
    scores: tuple[PrincipleScore, ...]
    average_score: float
    reasons: tuple[str, ...]


def judge_code_improvement(
    improvement: CodeImprovement,
    original_code: str,
    module_name: str,
) -> tuple[Verdict, list[str], dict[str, float]]:
    """
    Judge a code improvement against the 7 principles.

    Returns (verdict, detailed_reasons, scores).

    Unlike the bootstrap Judge which evaluates Agent objects, this evaluates
    code improvements using heuristics tailored for evolution.
    """
    reasons: list[str] = []
    scores: dict[str, float] = {}

    new_code = improvement.code

    # 1. TASTEFUL: Clear purpose, no bloat
    original_lines = len(original_code.splitlines())
    new_lines = len(new_code.splitlines())
    line_delta = new_lines - original_lines

    if original_lines > 0 and line_delta > original_lines * 0.3:  # >30% increase
        reasons.append(
            f"Tasteful: +{line_delta} lines ({line_delta/original_lines*100:.0f}% increase) - may be bloat"
        )
        scores["tasteful"] = 0.5
    elif line_delta < 0:
        reasons.append(f"Tasteful: {abs(line_delta)} fewer lines - leaner")
        scores["tasteful"] = 1.0
    else:
        scores["tasteful"] = 0.8

    # 2. CURATED: Quality over quantity
    if improvement.confidence < 0.5:
        reasons.append(f"Curated: Low confidence ({improvement.confidence}) - uncertain value")
        scores["curated"] = 0.4
    else:
        scores["curated"] = improvement.confidence

    # 3. ETHICAL: No concerning patterns
    concerning = ["eval(", "exec(", "__import__", "os.system", "subprocess.call"]
    new_concerning = sum(1 for c in concerning if c in new_code and c not in original_code)
    if new_concerning > 0:
        reasons.append(f"Ethical: Introduces {new_concerning} potentially unsafe pattern(s)")
        scores["ethical"] = 0.3
    else:
        scores["ethical"] = 1.0

    # 4. JOYFUL: Readable, well-structured
    has_docstrings = '"""' in new_code or "'''" in new_code
    scores["joyful"] = 0.8 if has_docstrings else 0.6

    # 5. COMPOSABLE: Follows agent patterns
    composable_patterns = ["async def", "def invoke", "Agent[", ">> "]
    pattern_count = sum(1 for p in composable_patterns if p in new_code)
    original_pattern_count = sum(1 for p in composable_patterns if p in original_code)

    if pattern_count >= original_pattern_count:
        scores["composable"] = 1.0
    else:
        reasons.append("Composable: May break composition patterns")
        scores["composable"] = 0.6

    # 6. HETERARCHICAL: Not creating god objects
    class_count = new_code.count("class ")
    original_class_count = original_code.count("class ")
    if class_count > 5 and class_count > original_class_count + 2:
        reasons.append(f"Heterarchical: Adds {class_count - original_class_count} new classes")
        scores["heterarchical"] = 0.7
    else:
        scores["heterarchical"] = 1.0

    # 7. GENERATIVE: Could be regenerated from spec
    spec_refs = ["spec/", "See ", "per spec", "as specified"]
    has_spec_ref = any(ref in new_code for ref in spec_refs)
    scores["generative"] = 1.0 if has_spec_ref else 0.7

    # Aggregate
    avg_score = sum(scores.values()) / len(scores)

    if avg_score >= 0.75 and scores["ethical"] >= 0.8:
        verdict = Verdict.accept(reasons or ["Passes all principle checks"])
    elif avg_score < 0.5 or scores["ethical"] < 0.5:
        verdict = Verdict.reject(reasons or ["Failed critical principle checks"])
    else:
        revisions = [r for r in reasons if ":" in r]
        verdict = Verdict.revise(revisions, ["Needs refinement"])

    # Add score summary
    score_summary = ", ".join(f"{k}={v:.1f}" for k, v in scores.items())
    reasons.append(f"Scores: [{score_summary}] avg={avg_score:.2f}")

    return verdict, reasons, scores


class CodeJudge(Agent[JudgeInput, JudgeResult]):
    """
    Agent that judges code improvements against principles.

    Morphism: JudgeInput → JudgeResult

    Usage:
        judge = CodeJudge()
        result = await judge.invoke(JudgeInput(
            improvement=improvement,
            original_code=original,
            module_name="types"
        ))
        if result.verdict.type == VerdictType.ACCEPT:
            print("Improvement approved!")
    """

    @property
    def name(self) -> str:
        return "CodeJudge"

    async def invoke(self, input: JudgeInput) -> JudgeResult:
        """Judge a code improvement against principles."""
        verdict, reasons, scores = judge_code_improvement(
            improvement=input.improvement,
            original_code=input.original_code,
            module_name=input.module_name,
        )

        principle_scores = tuple(
            PrincipleScore(name=name, score=score)
            for name, score in scores.items()
        )

        avg_score = sum(scores.values()) / len(scores) if scores else 0.0

        return JudgeResult(
            verdict=verdict,
            scores=principle_scores,
            average_score=avg_score,
            reasons=tuple(reasons),
        )


class GenericCodeJudge(Agent[JudgeInput, JudgeResult]):
    """
    Generic code judge for non-kgents codebases.

    Uses standard heuristics instead of kgents principles:
    - PEP 8 compliance hints
    - Cyclomatic complexity
    - Type coverage
    - Documentation

    Morphism: JudgeInput → JudgeResult
    """

    @property
    def name(self) -> str:
        return "GenericCodeJudge"

    async def invoke(self, input: JudgeInput) -> JudgeResult:
        """Judge code improvement using generic heuristics."""
        scores: dict[str, float] = {}
        reasons: list[str] = []

        new_code = input.improvement.code
        original = input.original_code

        # 1. Line delta (prefer smaller changes)
        new_lines = len(new_code.splitlines())
        orig_lines = len(original.splitlines())
        delta = new_lines - orig_lines
        if orig_lines > 0:
            delta_ratio = abs(delta) / orig_lines
            scores["size"] = max(0.3, 1.0 - delta_ratio)
        else:
            scores["size"] = 0.7

        # 2. Has docstrings
        has_docs = '"""' in new_code or "'''" in new_code
        scores["documentation"] = 0.9 if has_docs else 0.5

        # 3. Type hints present
        has_types = "->" in new_code or ": " in new_code
        scores["type_hints"] = 0.8 if has_types else 0.5

        # 4. Not adding unsafe patterns
        unsafe = ["eval(", "exec(", "__import__"]
        new_unsafe = sum(1 for u in unsafe if u in new_code and u not in original)
        scores["safety"] = 0.0 if new_unsafe > 0 else 1.0
        if new_unsafe > 0:
            reasons.append(f"Introduces {new_unsafe} unsafe pattern(s)")

        # 5. Confidence
        scores["confidence"] = input.improvement.confidence

        avg = sum(scores.values()) / len(scores)

        if avg >= 0.7 and scores["safety"] >= 0.8:
            verdict = Verdict.accept(reasons or ["Passes generic checks"])
        elif avg < 0.4 or scores["safety"] < 0.5:
            verdict = Verdict.reject(reasons or ["Failed checks"])
        else:
            verdict = Verdict.revise(reasons, ["Needs review"])

        principle_scores = tuple(
            PrincipleScore(name=k, score=v) for k, v in scores.items()
        )

        return JudgeResult(
            verdict=verdict,
            scores=principle_scores,
            average_score=avg,
            reasons=tuple(reasons),
        )


# Convenience factories

def code_judge() -> CodeJudge:
    """Create a kgents code judge."""
    return CodeJudge()


def generic_judge() -> GenericCodeJudge:
    """Create a generic code judge for non-kgents code."""
    return GenericCodeJudge()
