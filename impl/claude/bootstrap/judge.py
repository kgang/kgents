"""
Judge (⊢) - The value function.

Type: (Agent, Principles) → Verdict
Returns: {accept, reject, revise(how)}

Embodies the seven principles as executable judgment.

Why irreducible: Taste cannot be computed. "Is this tasteful?"
                 "Is this ethical?" requires grounding in human values.
What it grounds: Quality control. The stopping condition for generation.

Substructure (composable via >>):
- Judge is composed from 7 mini-judges, one per principle
- Each mini-judge: VerdictAccumulator → VerdictAccumulator (pure function)
- Final aggregation: list[PartialVerdict] → Verdict
- Agent wrapping happens at composition boundary
"""

from dataclasses import dataclass, field
from typing import Any, Callable

from .types import Agent, Principles, Verdict, VerdictType


@dataclass
class JudgeInput:
    """Input to Judge: the agent to evaluate and the principles to use."""
    agent: Agent[Any, Any]
    principles: Principles


@dataclass
class PartialVerdict:
    """
    Result from a single mini-judge evaluating one principle.

    Accumulates through the composition chain to form the final Verdict.
    """
    principle: str
    passed: bool
    reasons: list[str] = field(default_factory=list)
    revisions: list[str] = field(default_factory=list)


@dataclass
class VerdictAccumulator:
    """
    Accumulates partial verdicts through the composition pipeline.

    Type: Contains JudgeInput + accumulated PartialVerdicts.
    This allows mini-judges to be composed via >>.
    """
    input: JudgeInput
    partial_verdicts: list[PartialVerdict] = field(default_factory=list)


# Seven Mini-Judges (Pure Functions)
#
# Each mini-judge: VerdictAccumulator → VerdictAccumulator
# Stateless morphisms - no need for Agent wrapping at this level.
# Agent wrapping happens once at composition boundary.

def judge_tasteful(acc: VerdictAccumulator) -> VerdictAccumulator:
    """
    Mini-judge for tasteful principle.

    Checks: Does this agent have a clear, justified purpose?
    """
    agent = acc.input.agent

    # Check: has name, docstring, clear purpose
    passed = bool(agent.name and agent.__doc__)

    partial = PartialVerdict(
        principle="tasteful",
        passed=passed,
        reasons=[] if passed else ["Agent lacks name or docstring"],
        revisions=[] if passed else ["Add docstring explaining purpose"],
    )

    acc.partial_verdicts.append(partial)
    return acc


def judge_curated(acc: VerdictAccumulator) -> VerdictAccumulator:
    """
    Mini-judge for curated principle.

    Checks: Does this add unique value?
    """
    agent = acc.input.agent

    # This requires context about existing agents
    # Placeholder: assume unique (future: registry lookup)
    passed = True

    partial = PartialVerdict(
        principle="curated",
        passed=passed,
        reasons=[] if passed else ["Similar agent already exists"],
    )

    acc.partial_verdicts.append(partial)
    return acc


def judge_ethical(acc: VerdictAccumulator) -> VerdictAccumulator:
    """
    Mini-judge for ethical principle.

    Checks: Does this respect human agency and privacy?
    """
    agent = acc.input.agent

    # Check: no hidden data collection, preserves human agency
    # Placeholder: assume ethical (future: deep inspection)
    passed = True

    partial = PartialVerdict(
        principle="ethical",
        passed=passed,
        reasons=[] if passed else ["Agent violates privacy or autonomy"],
    )

    acc.partial_verdicts.append(partial)
    return acc


def judge_joyful(acc: VerdictAccumulator) -> VerdictAccumulator:
    """
    Mini-judge for joy-inducing principle.

    Checks: Would I enjoy interacting with this?
    """
    agent = acc.input.agent

    # This is inherently subjective - requires Ground
    # Placeholder: assume joyful (future: persona-based evaluation)
    passed = True

    partial = PartialVerdict(
        principle="joy-inducing",
        passed=passed,
        reasons=[] if passed else ["Interaction would be tedious or frustrating"],
    )

    acc.partial_verdicts.append(partial)
    return acc


def judge_composable(acc: VerdictAccumulator) -> VerdictAccumulator:
    """
    Mini-judge for composable principle.

    Checks: Can this work with other agents?
    """
    agent = acc.input.agent

    # Check: has callable invoke method
    passed = callable(getattr(agent, "invoke", None))

    partial = PartialVerdict(
        principle="composable",
        passed=passed,
        reasons=[] if passed else ["Agent lacks invoke method"],
        revisions=[] if passed else ["Implement async invoke(input) -> output"],
    )

    acc.partial_verdicts.append(partial)
    return acc


def judge_heterarchical(acc: VerdictAccumulator) -> VerdictAccumulator:
    """
    Mini-judge for heterarchical principle.

    Checks: Does this avoid fixed hierarchy? Can it both lead and follow?
    """
    agent = acc.input.agent

    # Check: supports composition via __rshift__
    passed = hasattr(agent, "__rshift__")

    partial = PartialVerdict(
        principle="heterarchical",
        passed=passed,
        reasons=[] if passed else ["Agent cannot be composed (missing >>)"],
        revisions=[] if passed else ["Inherit from Agent or implement __rshift__"],
    )

    acc.partial_verdicts.append(partial)
    return acc


def judge_generative(acc: VerdictAccumulator) -> VerdictAccumulator:
    """
    Mini-judge for generative principle.

    Checks: Could this be regenerated from spec?
    """
    agent = acc.input.agent

    # Check: has documentation for regeneration
    passed = bool(agent.__doc__)

    partial = PartialVerdict(
        principle="generative",
        passed=passed,
        reasons=[] if passed else ["Insufficient documentation for regeneration"],
        revisions=[] if passed else ["Add docstring with type signature and examples"],
    )

    acc.partial_verdicts.append(partial)
    return acc


def aggregate_verdicts(acc: VerdictAccumulator) -> Verdict:
    """
    Final step in judge pipeline: converts accumulated partial verdicts to final Verdict.

    Type: VerdictAccumulator → Verdict

    - If any hard failures → REJECT
    - If any revisions suggested → REVISE
    - If all pass → ACCEPT
    """
    failures = [pv for pv in acc.partial_verdicts if not pv.passed]
    all_revisions = [r for pv in acc.partial_verdicts for r in pv.revisions]

    if failures:
        all_reasons = [
            f"{pv.principle}: {r}"
            for pv in failures
            for r in pv.reasons
        ]
        return Verdict.reject(all_reasons)
    elif all_revisions:
        return Verdict.revise(
            reasons=["Some principles could be improved"],
            revisions=all_revisions,
        )
    else:
        return Verdict.accept(["All 7 principles satisfied"])


# Default principle check implementations
def _check_has_purpose(agent: Agent[Any, Any]) -> bool:
    """Default: agent has name and docstring."""
    return bool(agent.name and agent.__doc__)


def _check_is_unique(agent: Agent[Any, Any]) -> bool:
    """Default: assume unique (requires registry context)."""
    return True


def _check_is_ethical(agent: Agent[Any, Any]) -> bool:
    """Default: assume ethical (deep inspection needed)."""
    return True


def _check_is_joyful(agent: Agent[Any, Any]) -> bool:
    """Default: requires Ground for subjective evaluation."""
    return True


def _check_is_composable(agent: Agent[Any, Any]) -> bool:
    """Default: has callable invoke method."""
    return callable(getattr(agent, "invoke", None))


def _check_is_heterarchical(agent: Agent[Any, Any]) -> bool:
    """Default: supports composition via __rshift__."""
    return hasattr(agent, "__rshift__")


def _check_is_generative(agent: Agent[Any, Any]) -> bool:
    """Default: has documentation for regeneration."""
    return bool(agent.__doc__)


def make_default_principles(
    check_taste: Callable[[Agent[Any, Any]], bool] | None = None,
    check_curate: Callable[[Agent[Any, Any]], bool] | None = None,
    check_ethics: Callable[[Agent[Any, Any]], bool] | None = None,
    check_joy: Callable[[Agent[Any, Any]], bool] | None = None,
    check_compose: Callable[[Agent[Any, Any]], bool] | None = None,
    check_hetero: Callable[[Agent[Any, Any]], bool] | None = None,
    check_generate: Callable[[Agent[Any, Any]], bool] | None = None,
) -> Principles:
    """
    Create the default 7 principles with injectable checks.

    Dependency injection enables:
    - Testing with mocks
    - Production customization
    - Decoupling from Agent interface

    Args:
        check_*: Optional custom check functions. If None, uses defaults.
    """
    from .types import Principle

    return Principles(
        tasteful=Principle(
            name="tasteful",
            question="Does this agent have a clear, justified purpose?",
            check=check_taste or _check_has_purpose,
        ),
        curated=Principle(
            name="curated",
            question="Does this add unique value?",
            check=check_curate or _check_is_unique,
        ),
        ethical=Principle(
            name="ethical",
            question="Does this respect human agency and privacy?",
            check=check_ethics or _check_is_ethical,
        ),
        joy_inducing=Principle(
            name="joy-inducing",
            question="Would I enjoy interacting with this?",
            check=check_joy or _check_is_joyful,
        ),
        composable=Principle(
            name="composable",
            question="Can this work with other agents?",
            check=check_compose or _check_is_composable,
        ),
        heterarchical=Principle(
            name="heterarchical",
            question="Does this avoid fixed hierarchy?",
            check=check_hetero or _check_is_heterarchical,
        ),
        generative=Principle(
            name="generative",
            question="Could this be regenerated from spec?",
            check=check_generate or _check_is_generative,
        ),
    )


# Utility: Wrap pure function as Agent for composition
class FunctionAgent(Agent[VerdictAccumulator, VerdictAccumulator]):
    """
    Wraps a pure function VerdictAccumulator → VerdictAccumulator as an Agent.

    This allows pure mini-judge functions to participate in >> composition.
    """

    def __init__(self, fn: Callable[[VerdictAccumulator], VerdictAccumulator], fn_name: str) -> None:
        self._fn = fn
        self._fn_name = fn_name

    @property
    def name(self) -> str:
        return self._fn_name

    async def invoke(self, acc: VerdictAccumulator) -> VerdictAccumulator:
        """Invoke the wrapped function."""
        return self._fn(acc)


class AggregateAgent(Agent[VerdictAccumulator, Verdict]):
    """
    Wraps the aggregate_verdicts function as an Agent for final composition step.

    Type: VerdictAccumulator → Verdict
    """

    @property
    def name(self) -> str:
        return "AggregateVerdicts"

    async def invoke(self, acc: VerdictAccumulator) -> Verdict:
        """Invoke aggregate_verdicts function."""
        return aggregate_verdicts(acc)


# Convenience functions for composed judge

class InitializeAccumulator(Agent[JudgeInput, VerdictAccumulator]):
    """
    Helper agent: JudgeInput → VerdictAccumulator

    Initializes the accumulator for the mini-judge pipeline.
    """

    @property
    def name(self) -> str:
        return "InitializeAccumulator"

    async def invoke(self, input: JudgeInput) -> VerdictAccumulator:
        """Initialize accumulator from JudgeInput."""
        return VerdictAccumulator(input=input, partial_verdicts=[])


def make_composed_judge() -> Agent[JudgeInput, Verdict]:
    """
    Create the fully composed Judge from 7 mini-judges.

    Pattern:
        initialize >> j_tasteful >> j_curated >> j_ethical >>
        j_joyful >> j_composable >> j_heterarchical >> j_generative >> aggregate

    Mini-judges are pure functions wrapped as Agents at composition boundary.

    Returns:
        Composable Judge agent that evaluates all 7 principles.
    """
    return (
        InitializeAccumulator()
        >> FunctionAgent(judge_tasteful, "Judge-Tasteful")
        >> FunctionAgent(judge_curated, "Judge-Curated")
        >> FunctionAgent(judge_ethical, "Judge-Ethical")
        >> FunctionAgent(judge_joyful, "Judge-Joyful")
        >> FunctionAgent(judge_composable, "Judge-Composable")
        >> FunctionAgent(judge_heterarchical, "Judge-Heterarchical")
        >> FunctionAgent(judge_generative, "Judge-Generative")
        >> AggregateAgent()
    )


# For backward compatibility, make original Judge use composed implementation
class Judge(Agent[JudgeInput, Verdict]):
    """
    The value function: evaluates agents against the 7 principles.

    IMPLEMENTATION: Composes 7 mini-judges via >> operator.

    Usage:
        judge = Judge()
        verdict = await judge.invoke(JudgeInput(agent=my_agent, principles=p))

        if verdict.type == VerdictType.ACCEPT:
            # Agent passes
        elif verdict.type == VerdictType.REJECT:
            # Agent fails: verdict.reasons
        else:
            # Agent needs revision: verdict.revisions

    Structure:
        Judge is implemented as a composition of 7 mini-judges:
        - judge_tasteful, judge_curated, judge_ethical, judge_joyful,
        - judge_composable, judge_heterarchical, judge_generative
        - Each is a pure function wrapped as Agent at boundary
        - AggregateAgent combines results
    """

    def __init__(self) -> None:
        self._composed = make_composed_judge()

    @property
    def name(self) -> str:
        return "Judge"

    async def invoke(self, input: JudgeInput) -> Verdict:
        """Delegate to composed mini-judge pipeline."""
        return await self._composed.invoke(input)