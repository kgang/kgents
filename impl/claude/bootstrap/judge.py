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
- Each mini-judge: JudgeInput → PartialVerdict
- Final aggregation: list[PartialVerdict] → Verdict
- Pattern: judge_tasteful >> judge_curated >> ... >> aggregate_verdicts
"""

from dataclasses import dataclass, field
from typing import Any

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


# Seven Mini-Judges (Composable via >>)
#
# Each mini-judge: VerdictAccumulator → VerdictAccumulator
# Evaluates one principle via Principles.check and adds a PartialVerdict.
# Final composition: judge = j_tasteful >> j_curated >> ... >> aggregate

class JudgeTasteful(Agent[VerdictAccumulator, VerdictAccumulator]):
    """
    Mini-judge for tasteful principle.

    Checks: Does this agent have a clear, justified purpose?
    """

    @property
    def name(self) -> str:
        return "Judge-Tasteful"

    async def invoke(self, acc: VerdictAccumulator) -> VerdictAccumulator:
        agent = acc.input.agent
        principle = acc.input.principles.tasteful

        passed = principle.check(agent)

        partial = PartialVerdict(
            principle="tasteful",
            passed=passed,
            reasons=[] if passed else ["Agent lacks name or docstring"],
            revisions=[] if passed else ["Add docstring explaining purpose"],
        )

        acc.partial_verdicts.append(partial)
        return acc


class JudgeCurated(Agent[VerdictAccumulator, VerdictAccumulator]):
    """
    Mini-judge for curated principle.

    Checks: Does this add unique value?
    """

    @property
    def name(self) -> str:
        return "Judge-Curated"

    async def invoke(self, acc: VerdictAccumulator) -> VerdictAccumulator:
        agent = acc.input.agent
        principle = acc.input.principles.curated

        passed = principle.check(agent)

        partial = PartialVerdict(
            principle="curated",
            passed=passed,
            reasons=[] if passed else ["Similar agent already exists"],
        )

        acc.partial_verdicts.append(partial)
        return acc


class JudgeEthical(Agent[VerdictAccumulator, VerdictAccumulator]):
    """
    Mini-judge for ethical principle.

    Checks: Does this respect human agency and privacy?
    """

    @property
    def name(self) -> str:
        return "Judge-Ethical"

    async def invoke(self, acc: VerdictAccumulator) -> VerdictAccumulator:
        agent = acc.input.agent
        principle = acc.input.principles.ethical

        passed = principle.check(agent)

        partial = PartialVerdict(
            principle="ethical",
            passed=passed,
            reasons=[] if passed else ["Agent violates privacy or autonomy"],
        )

        acc.partial_verdicts.append(partial)
        return acc


class JudgeJoyful(Agent[VerdictAccumulator, VerdictAccumulator]):
    """
    Mini-judge for joy-inducing principle.

    Checks: Would I enjoy interacting with this?
    """

    @property
    def name(self) -> str:
        return "Judge-Joyful"

    async def invoke(self, acc: VerdictAccumulator) -> VerdictAccumulator:
        agent = acc.input.agent
        principle = acc.input.principles.joy_inducing

        passed = principle.check(agent)

        partial = PartialVerdict(
            principle="joy-inducing",
            passed=passed,
            reasons=[] if passed else ["Interaction would be tedious or frustrating"],
        )

        acc.partial_verdicts.append(partial)
        return acc


class JudgeComposable(Agent[VerdictAccumulator, VerdictAccumulator]):
    """
    Mini-judge for composable principle.

    Checks: Can this work with other agents?
    """

    @property
    def name(self) -> str:
        return "Judge-Composable"

    async def invoke(self, acc: VerdictAccumulator) -> VerdictAccumulator:
        agent = acc.input.agent
        principle = acc.input.principles.composable

        passed = principle.check(agent)

        partial = PartialVerdict(
            principle="composable",
            passed=passed,
            reasons=[] if passed else ["Agent lacks invoke method"],
            revisions=[] if passed else ["Implement async invoke(input) -> output"],
        )

        acc.partial_verdicts.append(partial)
        return acc


class JudgeHeterarchical(Agent[VerdictAccumulator, VerdictAccumulator]):
    """
    Mini-judge for heterarchical principle.

    Checks: Does this avoid fixed hierarchy? Can it both lead and follow?
    """

    @property
    def name(self) -> str:
        return "Judge-Heterarchical"

    async def invoke(self, acc: VerdictAccumulator) -> VerdictAccumulator:
        agent = acc.input.agent
        principle = acc.input.principles.heterarchical

        passed = principle.check(agent)

        partial = PartialVerdict(
            principle="heterarchical",
            passed=passed,
            reasons=[] if passed else ["Agent cannot be composed (missing >>)"],
            revisions=[] if passed else ["Inherit from Agent or implement __rshift__"],
        )

        acc.partial_verdicts.append(partial)
        return acc


class JudgeGenerative(Agent[VerdictAccumulator, VerdictAccumulator]):
    """
    Mini-judge for generative principle.

    Checks: Could this be regenerated from spec?
    """

    @property
    def name(self) -> str:
        return "Judge-Generative"

    async def invoke(self, acc: VerdictAccumulator) -> VerdictAccumulator:
        agent = acc.input.agent
        principle = acc.input.principles.generative

        passed = principle.check(agent)

        partial = PartialVerdict(
            principle="generative",
            passed=passed,
            reasons=[] if passed else ["Insufficient documentation for regeneration"],
            revisions=[] if passed else ["Add docstring with type signature and examples"],
        )

        acc.partial_verdicts.append(partial)
        return acc


class AggregateVerdicts(Agent[VerdictAccumulator, Verdict]):
    """
    Final step in judge pipeline: converts accumulated partial verdicts to final Verdict.

    Type: VerdictAccumulator → Verdict
    """

    @property
    def name(self) -> str:
        return "AggregateVerdicts"

    async def invoke(self, acc: VerdictAccumulator) -> Verdict:
        """
        Aggregate partial verdicts into final verdict.

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


def make_default_principles() -> Principles:
    """
    Create the default 7 principles with standard checks.

    To customize evaluation logic, create Principles manually with
    custom check functions.

    Returns:
        Principles with default check implementations.
    """
    from .types import Principle

    return Principles(
        tasteful=Principle(
            name="tasteful",
            question="Does this agent have a clear, justified purpose?",
            check=_check_has_purpose,
        ),
        curated=Principle(
            name="curated",
            question="Does this add unique value?",
            check=_check_is_unique,
        ),
        ethical=Principle(
            name="ethical",
            question="Does this respect human agency and privacy?",
            check=_check_is_ethical,
        ),
        joy_inducing=Principle(
            name="joy-inducing",
            question="Would I enjoy interacting with this?",
            check=_check_is_joyful,
        ),
        composable=Principle(
            name="composable",
            question="Can this work with other agents?",
            check=_check_is_composable,
        ),
        heterarchical=Principle(
            name="heterarchical",
            question="Does this avoid fixed hierarchy?",
            check=_check_is_heterarchical,
        ),
        generative=Principle(
            name="generative",
            question="Could this be regenerated from spec?",
            check=_check_is_generative,
        ),
    )


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

    Returns:
        Composable Judge agent that evaluates all 7 principles.
    """
    return (
        InitializeAccumulator()
        >> JudgeTasteful()
        >> JudgeCurated()
        >> JudgeEthical()
        >> JudgeJoyful()
        >> JudgeComposable()
        >> JudgeHeterarchical()
        >> JudgeGenerative()
        >> AggregateVerdicts()
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
        - JudgeTasteful, JudgeCurated, JudgeEthical, JudgeJoyful,
        - JudgeComposable, JudgeHeterarchical, JudgeGenerative
        - Each evaluates one principle
        - AggregateVerdicts combines results
    """

    def __init__(self) -> None:
        self._composed = make_composed_judge()

    @property
    def name(self) -> str:
        return "Judge"

    async def invoke(self, input: JudgeInput) -> Verdict:
        """Delegate to composed mini-judge pipeline."""
        return await self._composed.invoke(input)