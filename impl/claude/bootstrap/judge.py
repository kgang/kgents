"""
Judge (⊢) - The value function.

Type: (Agent, Principles) → Verdict
Returns: {accept, reject, revise(how)}

Embodies the seven principles as executable judgment.

Why irreducible: Taste cannot be computed. "Is this tasteful?"
                 "Is this ethical?" requires grounding in human values.
What it grounds: Quality control. The stopping condition for generation.

Substructure (decomposable for clarity):
- Judge-taste: Is this aesthetically considered?
- Judge-curate: Does this add unique value?
- Judge-ethics: Does this respect human agency?
- Judge-joy: Would I enjoy this?
- Judge-compose: Can this combine with others?
- Judge-hetero: Does this avoid fixed hierarchy?
- Judge-generate: Could this be regenerated from spec?
"""

from dataclasses import dataclass
from typing import Any, Callable

from .types import Agent, Principles, Verdict, VerdictType


@dataclass
class JudgeInput:
    """Input to Judge: the agent to evaluate and the principles to use."""
    agent: Agent
    principles: Principles


class Judge(Agent[JudgeInput, Verdict]):
    """
    The value function: evaluates agents against the 7 principles.

    Usage:
        judge = Judge()
        verdict = await judge.invoke(JudgeInput(agent=my_agent, principles=p))

        if verdict.type == VerdictType.ACCEPT:
            # Agent passes
        elif verdict.type == VerdictType.REJECT:
            # Agent fails: verdict.reasons
        else:
            # Agent needs revision: verdict.revisions
    """

    @property
    def name(self) -> str:
        return "Judge"

    async def invoke(self, input: JudgeInput) -> Verdict:
        """
        Evaluate an agent against all principles.

        Returns accept if all pass, reject if any hard-fail,
        revise if improvements are suggested.
        """
        agent = input.agent
        principles = input.principles

        failures: list[str] = []
        revisions: list[str] = []

        for principle in principles.all():
            try:
                passes = principle.check(agent)
                if not passes:
                    failures.append(
                        f"{principle.name}: {principle.question}"
                    )
            except NotImplementedError:
                # Principle check not fully implemented - suggest revision
                revisions.append(
                    f"Implement check for: {principle.name}"
                )

        if failures:
            return Verdict.reject(failures)
        elif revisions:
            return Verdict.revise(
                reasons=["Some principle checks need implementation"],
                revisions=revisions,
            )
        else:
            return Verdict.accept(["All principles satisfied"])


# Sub-judges for finer-grained evaluation

class JudgeTaste(Agent[Agent, bool]):
    """Does this agent have a clear, justified purpose?"""

    @property
    def name(self) -> str:
        return "Judge-taste"

    async def invoke(self, agent: Agent) -> bool:
        # Check: has a name, has a docstring, purpose is clear
        return bool(agent.name and agent.__doc__)


class JudgeCurate(Agent[Agent, bool]):
    """Does this add unique value, or does something similar exist?"""

    @property
    def name(self) -> str:
        return "Judge-curate"

    async def invoke(self, agent: Agent) -> bool:
        # This requires context about existing agents
        # Placeholder: assume unique if it exists
        return True


class JudgeEthics(Agent[Agent, bool]):
    """Does this respect human agency and privacy?"""

    @property
    def name(self) -> str:
        return "Judge-ethics"

    async def invoke(self, agent: Agent) -> bool:
        # Check: no hidden data collection, preserves human agency
        # Placeholder: assume ethical by default
        return True


class JudgeJoy(Agent[Agent, bool]):
    """Would I enjoy interacting with this?"""

    @property
    def name(self) -> str:
        return "Judge-joy"

    async def invoke(self, agent: Agent) -> bool:
        # This is inherently subjective - requires Ground
        return True


class JudgeCompose(Agent[Agent, bool]):
    """Can this work with other agents?"""

    @property
    def name(self) -> str:
        return "Judge-compose"

    async def invoke(self, agent: Agent) -> bool:
        # Check: has invoke method, proper type hints
        return callable(getattr(agent, "invoke", None))


class JudgeHetero(Agent[Agent, bool]):
    """Can this agent both lead and follow? Does it avoid fixed hierarchy?"""

    @property
    def name(self) -> str:
        return "Judge-hetero"

    async def invoke(self, agent: Agent) -> bool:
        # Check: can be composed in either direction
        return hasattr(agent, "__rshift__")


class JudgeGenerate(Agent[Agent, bool]):
    """Could this be regenerated from spec?"""

    @property
    def name(self) -> str:
        return "Judge-generate"

    async def invoke(self, agent: Agent) -> bool:
        # Check: clear structure, documented, follows spec
        return bool(agent.__doc__)


# Default principle check implementations
def _check_has_purpose(agent: Agent) -> bool:
    """Default: agent has name and docstring."""
    return bool(agent.name and agent.__doc__)


def _check_is_unique(agent: Agent) -> bool:
    """Default: assume unique (requires registry context)."""
    return True


def _check_is_ethical(agent: Agent) -> bool:
    """Default: assume ethical (deep inspection needed)."""
    return True


def _check_is_joyful(agent: Agent) -> bool:
    """Default: requires Ground for subjective evaluation."""
    return True


def _check_is_composable(agent: Agent) -> bool:
    """Default: has callable invoke method."""
    return callable(getattr(agent, "invoke", None))


def _check_is_heterarchical(agent: Agent) -> bool:
    """Default: supports composition via __rshift__."""
    return hasattr(agent, "__rshift__")


def _check_is_generative(agent: Agent) -> bool:
    """Default: has documentation for regeneration."""
    return bool(agent.__doc__)


def make_default_principles(
    check_taste: Callable[[Agent], bool] | None = None,
    check_curate: Callable[[Agent], bool] | None = None,
    check_ethics: Callable[[Agent], bool] | None = None,
    check_joy: Callable[[Agent], bool] | None = None,
    check_compose: Callable[[Agent], bool] | None = None,
    check_hetero: Callable[[Agent], bool] | None = None,
    check_generate: Callable[[Agent], bool] | None = None,
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
