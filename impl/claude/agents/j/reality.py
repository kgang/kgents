"""
Reality Classification - Classify tasks into DETERMINISTIC, PROBABILISTIC, or CHAOTIC.

The RealityClassifier determines how a task should be handled:
- DETERMINISTIC: Execute directly (atomic, bounded)
- PROBABILISTIC: Decompose into sub-promises (complex but tractable)
- CHAOTIC: Collapse to Ground immediately (unbounded, unsafe)

See spec/j-gents/reality.md for the full specification.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from bootstrap.types import Agent


class Reality(Enum):
    """The three types of reality a task can be classified as."""

    DETERMINISTIC = "deterministic"  # Atomic, bounded - execute directly
    PROBABILISTIC = "probabilistic"  # Complex but tractable - decompose
    CHAOTIC = "chaotic"  # Unbounded, unsafe - collapse to Ground


# --- Configuration ---

# Default entropy threshold below which everything becomes CHAOTIC
DEFAULT_CHAOS_THRESHOLD = 0.1

# Keywords that suggest atomicity (single operation)
ATOMIC_KEYWORDS = frozenset({
    "read",
    "get",
    "fetch",
    "query",
    "return",
    "format",
    "parse",
    "convert",
    "add",
    "subtract",
    "multiply",
    "divide",
    "calculate",
    "check",
    "validate",
    "lookup",
})

# Keywords that suggest complexity (decomposition needed)
COMPLEX_KEYWORDS = frozenset({
    "analyze",
    "refactor",
    "design",
    "implement",
    "fix",
    "debug",
    "optimize",
    "migrate",
    "improve",
    "review",
    "test",
    "build",
    "create",
    "develop",
    "integrate",
})

# Keywords that suggest unboundedness (collapse to Ground)
CHAOTIC_KEYWORDS = frozenset({
    "infinite",
    "forever",
    "everything",
    "all",
    "always",
    "never",
    "continuously",
    "unlimited",
    "perfect",
    "complete",
})


# --- Input/Output Types ---


@dataclass(frozen=True)
class ClassificationInput:
    """Input to the RealityClassifier agent."""

    intent: str  # What the task asks for
    context: dict[str, Any]  # Available information
    entropy_budget: float  # Remaining computation freedom (0.0-1.0)


@dataclass(frozen=True)
class ClassificationOutput:
    """Output from the RealityClassifier agent."""

    reality: Reality  # The classified reality type
    confidence: float  # Confidence in this classification (0.0-1.0)
    reasoning: str  # Why this classification was chosen


# --- Classification Logic ---


def _check_budget(budget: float, threshold: float = DEFAULT_CHAOS_THRESHOLD) -> Reality | None:
    """
    Test 1: Budget Check.

    If entropy budget is below threshold, force CHAOTIC.
    """
    if budget < threshold:
        return Reality.CHAOTIC
    return None


def _check_atomicity(intent: str) -> Reality | None:
    """
    Test 2: Atomicity Test.

    Check if the task can be done in one tool call.
    """
    intent_lower = intent.lower()

    # First check if there are ANY complex keywords - if so, not atomic
    for complex_kw in COMPLEX_KEYWORDS:
        if complex_kw in intent_lower:
            return None  # Contains complex keyword, continue to decomposition test

    # Check for chaotic keywords - if present, not atomic
    for chaotic_kw in CHAOTIC_KEYWORDS:
        if chaotic_kw in intent_lower:
            return None  # Contains chaotic keyword, continue

    # Check for atomic keywords
    for keyword in ATOMIC_KEYWORDS:
        if keyword in intent_lower:
            return Reality.DETERMINISTIC

    # Check for "and" or "then" which suggest multiple steps
    if " and " in intent_lower or " then " in intent_lower:
        return None  # Multiple steps, not atomic

    # Very short intents with no complex/chaotic keywords might be atomic
    words = intent.split()
    if len(words) <= 3:
        return Reality.DETERMINISTIC

    return None


def _check_decomposability(intent: str, context: dict[str, Any]) -> Reality | None:
    """
    Test 3: Decomposition Test.

    Check if the task can be broken into clear sub-tasks.
    """
    intent_lower = intent.lower()

    # First check for chaotic keywords - these override decomposability
    for chaotic_kw in CHAOTIC_KEYWORDS:
        if chaotic_kw in intent_lower:
            return None  # Defer to boundedness check for CHAOTIC

    # Check for complex keywords that suggest decomposition
    for keyword in COMPLEX_KEYWORDS:
        if keyword in intent_lower:
            return Reality.PROBABILISTIC

    # Check for conjunctions suggesting multiple steps
    if " and " in intent_lower or " then " in intent_lower:
        return Reality.PROBABILISTIC

    # Check if context suggests complexity
    if context.get("requires_multiple_steps"):
        return Reality.PROBABILISTIC

    if context.get("subtasks"):
        return Reality.PROBABILISTIC

    return None


def _check_boundedness(intent: str) -> Reality | None:
    """
    Test 4: Boundedness Test.

    Check if there's a clear stopping condition.
    """
    intent_lower = intent.lower()

    # Check for chaotic keywords
    for keyword in CHAOTIC_KEYWORDS:
        if keyword in intent_lower:
            return Reality.CHAOTIC

    # If we've made it this far without classification,
    # assume it's bounded (PROBABILISTIC by default)
    return Reality.PROBABILISTIC


def classify_intent(
    intent: str,
    context: dict[str, Any],
    entropy_budget: float,
    chaos_threshold: float = DEFAULT_CHAOS_THRESHOLD,
) -> ClassificationOutput:
    """
    Classify an intent into a Reality type.

    Applies tests in order:
    1. Budget check (force CHAOTIC if budget exhausted)
    2. Atomicity test (DETERMINISTIC if single operation)
    3. Decomposability test (PROBABILISTIC if multi-step)
    4. Boundedness test (CHAOTIC if no stopping condition)

    Args:
        intent: What the task asks for
        context: Available information
        entropy_budget: Remaining computation freedom (0.0-1.0)
        chaos_threshold: Budget level below which everything is CHAOTIC

    Returns:
        ClassificationOutput with reality type, confidence, and reasoning
    """
    # Test 1: Budget check
    result = _check_budget(entropy_budget, chaos_threshold)
    if result is not None:
        return ClassificationOutput(
            reality=result,
            confidence=1.0,
            reasoning=f"Entropy budget ({entropy_budget:.2f}) below threshold ({chaos_threshold})",
        )

    # Test 2: Atomicity test
    result = _check_atomicity(intent)
    if result is not None:
        return ClassificationOutput(
            reality=result,
            confidence=0.8,
            reasoning="Task appears atomic (single operation, no decomposition needed)",
        )

    # Test 3: Decomposability test
    result = _check_decomposability(intent, context)
    if result is not None:
        return ClassificationOutput(
            reality=result,
            confidence=0.7,
            reasoning="Task requires decomposition into sub-tasks",
        )

    # Test 4: Boundedness test
    result = _check_boundedness(intent)
    if result is not None:
        if result == Reality.CHAOTIC:
            return ClassificationOutput(
                reality=result,
                confidence=0.9,
                reasoning="Task appears unbounded (no clear stopping condition)",
            )
        return ClassificationOutput(
            reality=result,
            confidence=0.6,
            reasoning="Task appears bounded but complex, defaulting to PROBABILISTIC",
        )

    # Should never reach here, but default to PROBABILISTIC
    return ClassificationOutput(
        reality=Reality.PROBABILISTIC,
        confidence=0.5,
        reasoning="Unable to determine classification, defaulting to PROBABILISTIC",
    )


# --- Agent Implementation ---


class RealityClassifier(Agent[ClassificationInput, ClassificationOutput]):
    """
    Agent that classifies tasks into Reality types.

    Uses heuristic analysis to determine whether a task is:
    - DETERMINISTIC: Can be executed directly
    - PROBABILISTIC: Needs decomposition
    - CHAOTIC: Should collapse to Ground

    The classifier is derivable from bootstrap agents:
    RealityClassifier = Ground >> BudgetCheck >> AtomicityJudge >> DecompositionJudge >> BoundednessJudge
    """

    def __init__(self, chaos_threshold: float = DEFAULT_CHAOS_THRESHOLD):
        """
        Initialize the classifier.

        Args:
            chaos_threshold: Budget level below which everything is CHAOTIC
        """
        self._chaos_threshold = chaos_threshold

    @property
    def name(self) -> str:
        return "RealityClassifier"

    async def invoke(self, input: ClassificationInput) -> ClassificationOutput:
        """
        Classify the given intent into a Reality type.

        Args:
            input: ClassificationInput with intent, context, and entropy_budget

        Returns:
            ClassificationOutput with reality type, confidence, and reasoning
        """
        return classify_intent(
            intent=input.intent,
            context=input.context,
            entropy_budget=input.entropy_budget,
            chaos_threshold=self._chaos_threshold,
        )


# --- Convenience Functions ---


async def classify(
    intent: str,
    context: dict[str, Any] | None = None,
    entropy_budget: float = 1.0,
) -> Reality:
    """
    Convenience function to classify an intent.

    Args:
        intent: What the task asks for
        context: Optional context dictionary
        entropy_budget: Remaining computation freedom (default 1.0)

    Returns:
        The Reality type (DETERMINISTIC, PROBABILISTIC, or CHAOTIC)
    """
    classifier = RealityClassifier()
    result = await classifier.invoke(
        ClassificationInput(
            intent=intent,
            context=context or {},
            entropy_budget=entropy_budget,
        )
    )
    return result.reality


def classify_sync(
    intent: str,
    context: dict[str, Any] | None = None,
    entropy_budget: float = 1.0,
) -> Reality:
    """
    Synchronous version of classify for non-async contexts.

    Args:
        intent: What the task asks for
        context: Optional context dictionary
        entropy_budget: Remaining computation freedom (default 1.0)

    Returns:
        The Reality type (DETERMINISTIC, PROBABILISTIC, or CHAOTIC)
    """
    result = classify_intent(
        intent=intent,
        context=context or {},
        entropy_budget=entropy_budget,
    )
    return result.reality
