"""
Judge Agent (⊢)

Judge: (Agent, Principles) → Verdict
Judge(agent, principles) = {accept, reject, revise(how)}

The value function. Embodies the six principles as executable judgment.

Why irreducible: Taste cannot be computed. "Is this tasteful?" "Is this ethical?"
                 "Does this spark joy?" These require grounding in human values
                 that cannot be derived from logic alone.

What it grounds: Quality control. The reason we have 5 good agents instead of
                 500 mediocre ones. The stopping condition for generation.
"""

from dataclasses import dataclass
from typing import Any
from .types import (
    Agent,
    Verdict,
    VerdictStatus,
    Principle,
    PRINCIPLE_QUESTIONS,
)


@dataclass
class JudgeInput:
    """Input to the Judge agent"""
    subject: Any
    principles: list[Principle] | None = None  # None means all principles

    def __post_init__(self):
        if self.principles is None:
            self.principles = list(Principle)


@dataclass
class JudgeOutput:
    """Output from the Judge agent"""
    overall: Verdict
    by_principle: dict[Principle, Verdict]


class Judge(Agent[JudgeInput, JudgeOutput]):
    """
    The value function.

    Type signature: Judge: (subject, principles) → Verdict

    Substructure (decomposable for clarity, but Judge is atomic):
        - Judge-taste: Is this aesthetically considered?
        - Judge-curate: Does this add unique value?
        - Judge-ethics: Does this respect human agency?
        - Judge-joy: Would I enjoy this?
        - Judge-compose: Can this combine with others?
        - Judge-hetero: Does this avoid fixed hierarchy?
    """

    @property
    def name(self) -> str:
        return "Judge"

    @property
    def genus(self) -> str:
        return "bootstrap"

    @property
    def purpose(self) -> str:
        return "Value function; embodies the 6 principles as executable judgment"

    async def invoke(self, input: JudgeInput) -> JudgeOutput:
        """
        Evaluate the subject against principles.

        Default implementation uses heuristics. Override with LLM-backed
        evaluation for production use.
        """
        by_principle: dict[Principle, Verdict] = {}

        for principle in input.principles:
            verdict = await self._check_principle(principle, input.subject)
            by_principle[principle] = verdict

        # Overall verdict: reject if any reject, revise if any revise, else accept
        overall = self._aggregate(by_principle)

        return JudgeOutput(overall=overall, by_principle=by_principle)

    async def _check_principle(self, principle: Principle, subject: Any) -> Verdict:
        """
        Check a single principle. Override for sophisticated evaluation.

        Default: accept unless obviously problematic.
        """
        # If subject is an Agent, we can do basic structural checks
        if isinstance(subject, Agent):
            return await self._check_agent(principle, subject)

        # For non-agents, default to accept (override for real evaluation)
        return Verdict.accept()

    async def _check_agent(self, principle: Principle, agent: Agent) -> Verdict:
        """Structural checks for agents"""

        match principle:
            case Principle.TASTEFUL:
                # Must have a clear purpose
                if not agent.purpose or len(agent.purpose) < 10:
                    return Verdict.reject("Agent lacks clear purpose")
                return Verdict.accept()

            case Principle.CURATED:
                # Must have a unique name
                if not agent.name or agent.name == "unnamed":
                    return Verdict.reject("Agent lacks proper name")
                return Verdict.accept()

            case Principle.ETHICAL:
                # Structural check: must be an Agent (has invoke)
                if not hasattr(agent, 'invoke'):
                    return Verdict.reject("Not a proper agent")
                return Verdict.accept()

            case Principle.JOY_INDUCING:
                # Name should not be boring
                boring_names = {'agent', 'processor', 'handler', 'manager'}
                if agent.name.lower() in boring_names:
                    return Verdict.revise("Consider a more evocative name")
                return Verdict.accept()

            case Principle.COMPOSABLE:
                # Must have invoke method (can be composed)
                if not callable(getattr(agent, 'invoke', None)):
                    return Verdict.reject("Agent is not composable (no invoke)")
                return Verdict.accept()

            case Principle.HETERARCHICAL:
                # Default accept; hierarchy checking requires context
                return Verdict.accept()

    def _aggregate(self, verdicts: dict[Principle, Verdict]) -> Verdict:
        """Aggregate multiple verdicts into one"""
        rejections = [
            (p, v) for p, v in verdicts.items()
            if v.status == VerdictStatus.REJECT
        ]
        revisions = [
            (p, v) for p, v in verdicts.items()
            if v.status == VerdictStatus.REVISE
        ]

        if rejections:
            reasons = [f"{p.value}: {v.reason}" for p, v in rejections]
            return Verdict.reject("; ".join(reasons))

        if revisions:
            suggestions = [f"{p.value}: {v.suggestion}" for p, v in revisions]
            return Verdict.revise("; ".join(suggestions))

        return Verdict.accept()


# Singleton instance
judge_agent = Judge()


async def judge(subject: Any, principles: list[Principle] | None = None) -> JudgeOutput:
    """Convenience function to judge a subject"""
    return await judge_agent.invoke(JudgeInput(subject=subject, principles=principles))
