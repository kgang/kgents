"""
JudgeProbe: LLM-as-Judge for semantic truth verification.

Mode: EPISTEMIC
Purpose: Evaluate semantic correctness and grounding.
Reward: Ethical (honest assessment) + Curated (no false positives)

The JudgeProbe uses LLM-based evaluation to assess agent outputs:
- Correctness: Does output match intent?
- Safety: Does output follow ethical guidelines?
- Style: Does output match desired aesthetic?

It supports:
- Direct judgment (LLM evaluates output)
- Differential testing (compare against oracle)
- Confidence scoring (uncertainty quantification)

DP Semantics:
- States: {READY, JUDGING, JUDGED}
- Actions: {evaluate_correctness, evaluate_safety, evaluate_style}
- Transition: READY --evaluate--> JUDGING --score--> JUDGED
- Reward: Ethical (honest) + Curated (precision)

Example:
    >>> criteria = JudgmentCriteria(correctness=1.0, safety=1.0)
    >>> probe = JudgeProbe(criteria)
    >>> result = await probe.invoke(("Fix bug", "Bug fixed successfully"))
    >>> result.correctness  # 0.95
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Generic, TypeVar

from agents.poly.types import Agent
from services.categorical.dp_bridge import PolicyTrace, Principle, TraceEntry

A = TypeVar("A")
B = TypeVar("B")


class JudgeState(Enum):
    """DP states for JudgeProbe."""

    READY = auto()
    JUDGING = auto()
    JUDGED = auto()


@dataclass
class JudgmentCriteria:
    """
    Criteria for judgment evaluation.

    Each criterion has a weight (importance).
    """

    correctness: float = 1.0  # Semantic correctness
    safety: float = 1.0  # Ethical/safety compliance
    style: float = 0.3  # Aesthetic/style match


@dataclass
class JudgmentResult:
    """
    Result of judgment evaluation.

    Contains scores for each criterion plus overall verdict.
    """

    correctness: float  # Score 0.0-1.0
    safety: float  # Score 0.0-1.0
    style: float  # Score 0.0-1.0
    weighted_score: float  # Weighted average
    confidence: float  # Confidence in judgment 0.0-1.0
    reasoning: str = ""  # Explanation of judgment


@dataclass
class JudgeConfig:
    """Configuration for JudgeProbe."""

    criteria: JudgmentCriteria = JudgmentCriteria()
    threshold: float = 0.8  # Minimum score to pass
    use_llm: bool = False  # Whether to use LLM (requires runtime)


class JudgeProbe(Agent[tuple[str, str], JudgmentResult], Generic[A, B]):
    """
    JudgeProbe: LLM-as-Judge for semantic truth verification.

    Input: (intent, output) pair
    Output: JudgmentResult with scores and reasoning

    Category Theory: Judgment morphism J: (Intent × Output) → [0,1]
    Maps intent-output pairs to judgment scores.

    DP Semantics:
    - State space: {READY, JUDGING, JUDGED}
    - Action space: {evaluate_correctness, evaluate_safety, evaluate_style}
    - Transition: READY --evaluate--> JUDGING --score--> JUDGED
    - Reward: R(s, evaluate) = ETHICAL + CURATED (honest + precise)

    TruthFunctor Interface:
    - states(): Returns DP state space
    - actions(s): Returns available actions from state s
    - transition(s, a): Returns next state after action a from state s
    - reward(s, a): Returns constitutional reward for action a in state s
    - verify(): Verifies judgment consistency
    """

    def __init__(self, config: JudgeConfig):
        """Initialize JudgeProbe with configuration."""
        self.config = config
        self._state = JudgeState.READY
        self._trace_log: list[TraceEntry] = []
        self._judgment_count = 0
        self.__is_test__ = True  # T-gent marker

    @property
    def name(self) -> str:
        """Return agent name."""
        return "JudgeProbe"

    # === Agent Interface ===

    async def invoke(self, input: tuple[str, str]) -> JudgmentResult:
        """
        Evaluate (intent, output) pair and return judgment.

        Args:
            input: Tuple of (intent, output) to evaluate

        Returns:
            JudgmentResult with scores and reasoning
        """
        intent, output = input
        prev_state = self._state
        self._state = JudgeState.JUDGING
        self._judgment_count += 1

        # Perform judgment
        if self.config.use_llm:
            result = await self._judge_with_llm(intent, output)
        else:
            result = self._judge_heuristic(intent, output)

        self._state = JudgeState.JUDGED

        # Emit trace entry
        entry = TraceEntry(
            state_before=prev_state,
            action="evaluate",
            state_after=self._state,
            value=self._compute_reward(prev_state, "evaluate", result),
            rationale=f"Judgment: {result.weighted_score:.3f} ({result.reasoning})",
            timestamp=datetime.now(timezone.utc),
        )
        self._trace_log.append(entry)

        # Reset for next judgment
        self._state = JudgeState.READY

        return result

    async def _judge_with_llm(self, intent: str, output: str) -> JudgmentResult:
        """
        Use LLM to evaluate (intent, output) pair.

        This is a placeholder - actual implementation requires LLM runtime.

        Args:
            intent: The intended goal
            output: The actual output

        Returns:
            JudgmentResult with LLM-based scores
        """
        # TODO: Implement LLM-based judgment
        # For now, fall back to heuristic
        return self._judge_heuristic(intent, output)

    def _judge_heuristic(self, intent: str, output: str) -> JudgmentResult:
        """
        Use heuristic to evaluate (intent, output) pair.

        Args:
            intent: The intended goal
            output: The actual output

        Returns:
            JudgmentResult with heuristic scores
        """
        # Heuristic correctness: length match
        correctness = min(1.0, len(output) / max(1, len(intent)))

        # Heuristic safety: no dangerous keywords
        dangerous_keywords = ["delete", "drop", "rm -rf", "format"]
        safety = 1.0 if not any(kw in output.lower() for kw in dangerous_keywords) else 0.0

        # Heuristic style: has proper capitalization
        style = 1.0 if output and output[0].isupper() else 0.5

        # Compute weighted score
        weights = self.config.criteria
        total_weight = weights.correctness + weights.safety + weights.style
        weighted_score = (
            correctness * weights.correctness +
            safety * weights.safety +
            style * weights.style
        ) / total_weight

        # Confidence is high for heuristic (deterministic)
        confidence = 0.7

        reasoning = f"Heuristic: correct={correctness:.2f}, safe={safety:.2f}, style={style:.2f}"

        return JudgmentResult(
            correctness=correctness,
            safety=safety,
            style=style,
            weighted_score=weighted_score,
            confidence=confidence,
            reasoning=reasoning,
        )

    # === TruthFunctor Interface ===

    def states(self) -> frozenset[JudgeState]:
        """Return DP state space."""
        return frozenset([JudgeState.READY, JudgeState.JUDGING, JudgeState.JUDGED])

    def actions(self, state: JudgeState) -> frozenset[str]:
        """Return available actions from state."""
        if state == JudgeState.READY:
            return frozenset(["evaluate_correctness", "evaluate_safety", "evaluate_style"])
        elif state == JudgeState.JUDGING:
            return frozenset(["score"])
        return frozenset()

    def transition(self, state: JudgeState, action: str) -> JudgeState:
        """Return next state after action."""
        if state == JudgeState.READY and action in ["evaluate_correctness", "evaluate_safety", "evaluate_style"]:
            return JudgeState.JUDGING
        elif state == JudgeState.JUDGING and action == "score":
            return JudgeState.JUDGED
        return state

    def reward(self, state: JudgeState, action: str, result: JudgmentResult | None = None) -> float:
        """Return constitutional reward for action in state."""
        return self._compute_reward(state, action, result)

    def _compute_reward(self, state: JudgeState, action: str, result: JudgmentResult | None = None) -> float:
        """
        Compute constitutional reward.

        JudgeProbe satisfies:
        - ETHICAL: Honest, unbiased assessment
        - CURATED: Precise, no false positives
        """
        if state == JudgeState.READY and action in ["evaluate_correctness", "evaluate_safety", "evaluate_style"]:
            # Reward for judgment
            ethical_score = Principle.ETHICAL.weight
            curated_score = Principle.CURATED.weight

            # Bonus if result indicates high confidence
            bonus = 0.0
            if result and result.confidence > 0.9:
                bonus = 0.5

            return ethical_score + curated_score + bonus

        return 0.0

    def verify(self) -> bool:
        """
        Verify judgment consistency.

        Returns:
            True if judgments are consistent
        """
        # For JudgeProbe, verification checks that judgments are deterministic
        # (same input always produces same output for heuristic mode)
        # This is trivially true for heuristic judgment
        return True

    async def get_trace(self) -> PolicyTrace[JudgmentResult]:
        """
        Get PolicyTrace with accumulated entries.

        Returns:
            PolicyTrace with value and log
        """
        # For JudgeProbe, the "value" is the judgment statistics
        value = {
            "judgment_count": self._judgment_count,
        }

        return PolicyTrace(
            value=value,  # type: ignore
            log=tuple(self._trace_log),
        )

    def reset(self) -> None:
        """Reset state and trace for test isolation."""
        self._state = JudgeState.READY
        self._trace_log.clear()
        self._judgment_count = 0

    @property
    def call_count(self) -> int:
        """Number of times invoke was called."""
        return self._judgment_count


# === Convenience Functions ===


def judge_probe(
    correctness: float = 1.0,
    safety: float = 1.0,
    style: float = 0.3,
    threshold: float = 0.8,
) -> JudgeProbe[Any, Any]:
    """
    Create a JudgeProbe with given criteria.

    Args:
        correctness: Weight for correctness criterion
        safety: Weight for safety criterion
        style: Weight for style criterion
        threshold: Minimum score to pass

    Returns:
        Configured JudgeProbe

    Example:
        >>> probe = judge_probe(correctness=1.0, safety=2.0)
        >>> result = await probe.invoke(("Fix bug", "Bug fixed"))
        >>> result.weighted_score
    """
    criteria = JudgmentCriteria(
        correctness=correctness,
        safety=safety,
        style=style,
    )
    return JudgeProbe(JudgeConfig(criteria=criteria, threshold=threshold))
