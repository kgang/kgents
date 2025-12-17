"""
Judge Agent - The value function evaluating against 7 principles.

Judge: (Agent, Principles) → Verdict
Judge(agent, principles) = {accept, reject, revise(how)}

Embodies the seven principles as executable judgment. Taste cannot be
computed. "Is this tasteful?" "Is this ethical?" "Does this spark joy?"
These require grounding in human values that cannot be derived from
logic alone.

The 7 Principles:
1. Tasteful - Clear, justified purpose; no bloat
2. Curated - Unique value; quality over quantity
3. Ethical - Transparent, respects agency
4. Joy-inducing - Personality, warmth, collaboration feel
5. Composable - Works with others; single outputs; category laws
6. Heterarchical - Can lead or follow; no fixed hierarchy
7. Generative - Regenerable from spec; compressed design

See spec/bootstrap.md lines 72-93, spec/principles.md.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Optional

from agents.poly.types import (
    Agent,
    JudgeInput,
    PartialVerdict,
    Principles,
    Verdict,
    VerdictType,
)

# --- Mini-Judge Functions (Pure Functions) ---
# Each mini-judge evaluates one principle.
# Refactored to pure functions per evolution improvement.


def check_tasteful(
    agent: Agent[Any, Any], context: Optional[dict[str, Any]] = None
) -> PartialVerdict:
    """
    Check if agent is tasteful.

    Criteria:
    - Clear, justified purpose
    - No bloat or feature creep
    - Aesthetic consideration in design
    """
    # Heuristic checks - could be enhanced with LLM
    reasons: list[str] = []
    passed = True

    # Check name clarity
    if not agent.name or agent.name.lower() in ("agent", "myagent", "test"):
        reasons.append("Name is generic; should describe purpose")
        passed = False

    # Name length heuristic - too long may indicate bloat
    if len(agent.name) > 50:
        reasons.append("Name is very long; may indicate unclear purpose")
        passed = False

    return PartialVerdict(
        principle=Principles.TASTEFUL,
        passed=passed,
        reasons=tuple(reasons),
        confidence=0.6,  # Heuristic-based, lower confidence
    )


def check_curated(
    agent: Agent[Any, Any], context: Optional[dict[str, Any]] = None
) -> PartialVerdict:
    """
    Check if agent is curated.

    Criteria:
    - Adds unique value
    - Not duplicative of existing agents
    - Quality over quantity
    """
    reasons: list[str] = []
    passed = True

    # Can't check for duplicates without registry context
    # This would need enhancement with agent catalog
    if context and "existing_agents" in context:
        existing = context["existing_agents"]
        if agent.name.lower() in [a.lower() for a in existing]:
            reasons.append(f"Agent name '{agent.name}' may duplicate existing agent")
            passed = False

    return PartialVerdict(
        principle=Principles.CURATED,
        passed=passed,
        reasons=tuple(reasons),
        confidence=0.5,  # Very limited without context
    )


def check_ethical(
    agent: Agent[Any, Any], context: Optional[dict[str, Any]] = None
) -> PartialVerdict:
    """
    Check if agent is ethical.

    Criteria:
    - Transparent about limitations
    - Respects human agency
    - No deception or manipulation
    - Privacy-respecting
    """
    reasons: list[str] = []
    passed = True

    # Check for concerning patterns in name
    concerning_terms = ["spy", "track", "steal", "hack", "deceive", "manipulate"]
    if any(term in agent.name.lower() for term in concerning_terms):
        reasons.append("Agent name contains concerning term")
        passed = False

    return PartialVerdict(
        principle=Principles.ETHICAL,
        passed=passed,
        reasons=tuple(reasons),
        confidence=0.4,  # Name-only check is very limited
    )


def check_joyful(
    agent: Agent[Any, Any], context: Optional[dict[str, Any]] = None
) -> PartialVerdict:
    """
    Check if agent is joy-inducing.

    Criteria:
    - Has personality (within bounds)
    - Warm interaction style
    - Collaboration feel
    """
    reasons: list[str] = []
    passed = True

    # This is inherently subjective - placeholder
    # Real implementation would need interaction testing

    return PartialVerdict(
        principle=Principles.JOYFUL,
        passed=passed,
        reasons=tuple(reasons),
        confidence=0.3,  # Highly subjective
    )


def check_composable(
    agent: Agent[Any, Any], context: Optional[dict[str, Any]] = None
) -> PartialVerdict:
    """
    Check if agent is composable.

    Criteria:
    - Implements Agent interface correctly
    - Has clear input/output types
    - Works with composition (>>)
    """
    reasons: list[str] = []
    passed = True

    # Check for Agent interface
    if not hasattr(agent, "invoke"):
        reasons.append("Missing invoke method")
        passed = False

    if not hasattr(agent, "name"):
        reasons.append("Missing name property")
        passed = False

    if not hasattr(agent, "__rshift__"):
        reasons.append("Missing composition operator (__rshift__)")
        passed = False

    return PartialVerdict(
        principle=Principles.COMPOSABLE,
        passed=passed,
        reasons=tuple(reasons),
        confidence=0.9,  # Interface check is reliable
    )


def check_heterarchical(
    agent: Agent[Any, Any], context: Optional[dict[str, Any]] = None
) -> PartialVerdict:
    """
    Check if agent is heterarchical.

    Criteria:
    - Can be composed (not a "god agent")
    - No fixed hierarchy assumptions
    - Can lead or follow
    """
    reasons: list[str] = []
    passed = True

    # Check for god-agent patterns in name
    god_patterns = ["master", "controller", "orchestrator", "manager"]
    if any(p in agent.name.lower() for p in god_patterns):
        reasons.append("Name suggests fixed hierarchy role")
        # Warning, not failure
        passed = True  # Still pass but note concern

    return PartialVerdict(
        principle=Principles.HETERARCHICAL,
        passed=passed,
        reasons=tuple(reasons),
        confidence=0.5,
    )


def check_generative(
    agent: Agent[Any, Any], context: Optional[dict[str, Any]] = None
) -> PartialVerdict:
    """
    Check if agent is generative.

    Criteria:
    - Could be regenerated from spec
    - Design is compressed
    - Not over-documented (spec > docs)
    """
    reasons: list[str] = []
    passed = True

    # Check if agent has docstring (minimal docs indication)
    if hasattr(agent, "__doc__") and agent.__doc__:
        doc = agent.__doc__
        # Very long docstring may indicate over-documentation
        if len(doc) > 2000:
            reasons.append("Very long docstring; consider compressing to spec")

    return PartialVerdict(
        principle=Principles.GENERATIVE,
        passed=passed,
        reasons=tuple(reasons),
        confidence=0.4,  # Hard to verify without spec
    )


# --- Verdict Accumulator (Immutable) ---


@dataclass(frozen=True)
class VerdictAccumulator:
    """
    Immutable accumulator for partial verdicts.

    Made immutable per evolution improvement for safer composition.
    """

    verdicts: tuple[PartialVerdict, ...] = ()
    context: Optional[dict[str, Any]] = None

    def add(self, verdict: PartialVerdict) -> "VerdictAccumulator":
        """Add a verdict, returning new accumulator."""
        return VerdictAccumulator(
            verdicts=self.verdicts + (verdict,),
            context=self.context,
        )

    def finalize(self) -> Verdict:
        """
        Finalize into a complete Verdict.

        Logic:
        - All pass → ACCEPT
        - Any critical fail → REJECT
        - Some fail → REVISE (with suggestions)
        """
        if not self.verdicts:
            return Verdict(
                type=VerdictType.ACCEPT,
                partial_verdicts=(),
                reasoning="No principles to check",
            )

        all_passed = all(v.passed for v in self.verdicts)
        any(not v.passed for v in self.verdicts)
        failed_verdicts = [v for v in self.verdicts if not v.passed]

        # Calculate weighted pass rate
        total_confidence = sum(v.confidence for v in self.verdicts)
        weighted_pass = sum(v.confidence for v in self.verdicts if v.passed)
        pass_rate = weighted_pass / total_confidence if total_confidence > 0 else 0

        # Determine verdict type
        if all_passed:
            verdict_type = VerdictType.ACCEPT
            reasoning = "All principles satisfied"
            revisions = None
        elif pass_rate < 0.3:
            verdict_type = VerdictType.REJECT
            reasoning = f"Critical failures: {[v.principle for v in failed_verdicts]}"
            revisions = None
        else:
            verdict_type = VerdictType.REVISE
            reasoning = f"Needs improvement: {[v.principle for v in failed_verdicts]}"
            # Collect revision suggestions from failed verdicts
            revisions = tuple(reason for v in failed_verdicts for reason in v.reasons)

        return Verdict(
            type=verdict_type,
            partial_verdicts=self.verdicts,
            revisions=revisions,
            reasoning=reasoning,
        )


# --- Mini-Judge Registry ---

# Map principle names to checker functions
MINI_JUDGES: dict[
    str, Callable[[Agent[Any, Any], Optional[dict[str, Any]]], PartialVerdict]
] = {
    Principles.TASTEFUL: check_tasteful,
    Principles.CURATED: check_curated,
    Principles.ETHICAL: check_ethical,
    Principles.JOYFUL: check_joyful,
    Principles.COMPOSABLE: check_composable,
    Principles.HETERARCHICAL: check_heterarchical,
    Principles.GENERATIVE: check_generative,
}


# --- Judge Agent ---


class Judge(Agent[JudgeInput, Verdict]):
    """
    The value function agent.

    Evaluates an agent against the seven principles (or a subset).
    Composed of seven mini-judges, one per principle.

    Usage:
        judge = Judge()
        verdict = await judge.invoke(JudgeInput(agent=my_agent))
        if verdict.type == VerdictType.ACCEPT:
            print("Agent passes all checks!")

    Architecture:
        Seven mini-judges are composed:
        judge_tasteful >> judge_curated >> ... >> aggregate_verdicts

        Each mini-judge produces a PartialVerdict, which are
        aggregated into a final Verdict.
    """

    def __init__(
        self,
        custom_judges: Optional[
            dict[
                str,
                Callable[[Agent[Any, Any], Optional[dict[str, Any]]], PartialVerdict],
            ]
        ] = None,
        parallel: bool = True,
    ):
        """
        Initialize Judge with optional custom mini-judges.

        Args:
            custom_judges: Override default mini-judges for specific principles
            parallel: Run mini-judges in parallel (default: True for performance)
        """
        self._judges = dict(MINI_JUDGES)
        if custom_judges:
            self._judges.update(custom_judges)
        self._parallel = parallel

    @property
    def name(self) -> str:
        return "Judge"

    async def invoke(self, input: JudgeInput) -> Verdict:
        """
        Evaluate agent against principles.

        If input.principles is None, checks all 7 principles.
        Otherwise, checks only the specified subset.

        Performance: Mini-judges run in parallel by default. Each principle
        check is independent, so parallelization provides near-linear speedup
        (7 principles → 7× faster if CPU-bound, or I/O-bound latency reduction).

        To disable parallelization (e.g., for debugging), set parallel=False
        in __init__.
        """
        principles_to_check = input.principles or Principles.all()

        # Filter out unknown principles
        valid_principles = [p for p in principles_to_check if p in self._judges]

        if self._parallel:
            # Run all mini-judges in parallel
            async def run_checker(principle: str) -> PartialVerdict:
                checker = self._judges[principle]
                # Run sync checker in thread pool to avoid blocking
                return await asyncio.to_thread(checker, input.agent, input.context)

            partial_verdicts = await asyncio.gather(
                *[run_checker(p) for p in valid_principles],
                return_exceptions=False,
            )

            # Build accumulator from all verdicts
            accumulator = VerdictAccumulator(context=input.context)
            for partial in partial_verdicts:
                accumulator = accumulator.add(partial)

        else:
            # Sequential execution (original behavior)
            accumulator = VerdictAccumulator(context=input.context)

            for principle in valid_principles:
                checker = self._judges[principle]
                partial = checker(input.agent, input.context)
                accumulator = accumulator.add(partial)

        return accumulator.finalize()


# --- Convenience Functions ---


async def judge(
    agent: Agent[Any, Any], principles: Optional[tuple[str, ...]] = None
) -> Verdict:
    """
    Judge an agent against principles.

    Convenience function for Judge().invoke(...).

    Args:
        agent: The agent to evaluate
        principles: Specific principles to check (default: all 7)

    Returns:
        Verdict with type ACCEPT, REVISE, or REJECT
    """
    return await Judge().invoke(JudgeInput(agent=agent, principles=principles))


async def accepts(agent: Agent[Any, Any]) -> bool:
    """
    Quick check if an agent passes all principles.

    Returns True if verdict is ACCEPT, False otherwise.
    """
    verdict = await judge(agent)
    return verdict.type == VerdictType.ACCEPT
