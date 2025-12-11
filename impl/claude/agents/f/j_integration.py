"""
Reality-Aware Contracts: J-gent × F-gent Integration.

This module bridges F-gent's GravityContract system with J-gent's Reality
classification. Contracts can check intents for "admissibility" before
execution, preventing chaotic tasks from being attempted.

Philosophy:
> "Gravity not only validates outputs; it gates inputs."

Integration Pattern:
    from agents.f.j_integration import (
        RealityGate,
        DeterministicOnly,
        BoundedComplexity,
    )
    from agents.f.gravity import Grounded

    # Gate chaotic intents before they reach the agent
    agent = Grounded(
        inner=MyAgent(),
        gravity=[RealityGate(), EthicalBoundary("strict")],
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from agents.f.gravity import GravityContract
from agents.j.reality import (
    Reality,
    classify_intent,
    CHAOTIC_KEYWORDS,
    COMPLEX_KEYWORDS,
    ATOMIC_KEYWORDS,
)


@dataclass
class RealityGate(GravityContract):
    """
    Contract that gates intents based on Reality classification.

    Rejects CHAOTIC intents entirely, optionally requiring DETERMINISTIC.

    Example:
        >>> gate = RealityGate(require_deterministic=True)
        >>> gate.admits("read the config file")  # True (deterministic)
        >>> gate.admits("fix everything forever")  # False (chaotic)
    """

    # If True, only DETERMINISTIC intents pass (strict mode)
    require_deterministic: bool = False

    # Entropy budget for classification
    entropy_budget: float = 1.0

    # Custom chaos threshold
    chaos_threshold: float = 0.1

    name: str = "RealityGate"

    def check(self, output: Any) -> str | None:
        """
        Check output for reality violations.

        For RealityGate, we primarily use admits() for input gating.
        Output checking ensures no CHAOTIC content leaked through.
        """
        output_str = str(output).lower()

        # Check for chaotic keywords in output
        for keyword in CHAOTIC_KEYWORDS:
            if keyword in output_str:
                return f"Output contains chaotic pattern: '{keyword}'"

        return None

    def admits(self, intent: str) -> bool:
        """
        Check if an intent is admissible under this contract.

        This is called BEFORE execution to gate chaotic intents.
        """
        result = classify_intent(
            intent=intent,
            context={},
            entropy_budget=self.entropy_budget,
            chaos_threshold=self.chaos_threshold,
        )

        if result.reality == Reality.CHAOTIC:
            return False

        if self.require_deterministic and result.reality != Reality.DETERMINISTIC:
            return False

        return True


@dataclass
class DeterministicOnly(GravityContract):
    """
    Contract that only admits DETERMINISTIC intents.

    Use this for high-reliability contexts where probabilistic
    outcomes are unacceptable.

    Example:
        >>> contract = DeterministicOnly()
        >>> contract.admits("fetch user data")  # True
        >>> contract.admits("analyze and optimize the system")  # False
    """

    name: str = "DeterministicOnly"

    def check(self, output: Any) -> str | None:
        """Outputs must be deterministic (no randomness indicators)."""
        output_str = str(output).lower()

        randomness_indicators = [
            "random",
            "might",
            "could",
            "possibly",
            "approximately",
            "about",
            "roughly",
        ]

        for indicator in randomness_indicators:
            if indicator in output_str:
                return f"Non-deterministic output: contains '{indicator}'"

        return None

    def admits(self, intent: str) -> bool:
        """Only admit intents that classify as DETERMINISTIC."""
        intent_lower = intent.lower()

        # Quick check: reject if contains complex keywords
        for keyword in COMPLEX_KEYWORDS:
            if keyword in intent_lower:
                return False

        # Quick check: reject if contains chaotic keywords
        for keyword in CHAOTIC_KEYWORDS:
            if keyword in intent_lower:
                return False

        # Accept if contains atomic keywords
        for keyword in ATOMIC_KEYWORDS:
            if keyword in intent_lower:
                return True

        # Short intents are likely deterministic
        return len(intent.split()) <= 5


@dataclass
class BoundedComplexity(GravityContract):
    """
    Contract that bounds task complexity.

    Prevents overly complex intents that might exhaust resources
    or produce unpredictable outputs.

    Example:
        >>> contract = BoundedComplexity(max_steps=3)
        >>> contract.admits("read, parse, and validate")  # True (3 steps)
        >>> contract.admits("read, parse, validate, transform, and store")  # False (5 steps)
    """

    max_steps: int = 5
    max_words: int = 50
    forbidden_patterns: list[str] = field(
        default_factory=lambda: ["everything", "all", "forever", "always"]
    )
    name: str = "BoundedComplexity"

    def check(self, output: Any) -> str | None:
        """Check output is reasonably sized."""
        try:
            length = len(str(output))
            if length > 100000:  # 100KB
                return f"Output exceeds size bound: {length} chars"
        except (TypeError, AttributeError):
            pass

        return None

    def admits(self, intent: str) -> bool:
        """
        Admit only intents with bounded complexity.

        Counts "and", "then", "," as step separators.
        """
        intent_lower = intent.lower()

        # Check forbidden patterns
        for pattern in self.forbidden_patterns:
            if pattern in intent_lower:
                return False

        # Count words
        words = intent.split()
        if len(words) > self.max_words:
            return False

        # Count steps (separated by and/then/comma)
        step_count = 1
        step_count += intent_lower.count(" and ")
        step_count += intent_lower.count(" then ")
        step_count += intent_lower.count(",")

        return step_count <= self.max_steps


@dataclass
class EntropyAware(GravityContract):
    """
    Contract that adjusts strictness based on remaining entropy budget.

    As entropy depletes, the contract becomes stricter, eventually
    rejecting all non-deterministic intents.

    This enables "graceful degradation" as resources are consumed.

    Example:
        >>> contract = EntropyAware(current_budget=0.8)
        >>> contract.admits("analyze the data")  # True (high budget)

        >>> contract = EntropyAware(current_budget=0.2)
        >>> contract.admits("analyze the data")  # False (low budget)
    """

    current_budget: float = 1.0

    # Budget thresholds
    probabilistic_threshold: float = 0.3  # Below this, reject PROBABILISTIC
    deterministic_threshold: float = 0.1  # Below this, reject everything

    name: str = "EntropyAware"

    def check(self, output: Any) -> str | None:
        """No output checks for entropy-aware contract."""
        return None

    def admits(self, intent: str) -> bool:
        """Admit based on entropy budget and intent complexity."""
        # Very low budget: reject everything
        if self.current_budget < self.deterministic_threshold:
            return False

        result = classify_intent(
            intent=intent,
            context={},
            entropy_budget=self.current_budget,
            chaos_threshold=self.deterministic_threshold,
        )

        # Always reject CHAOTIC
        if result.reality == Reality.CHAOTIC:
            return False

        # Low budget: only accept DETERMINISTIC
        if self.current_budget < self.probabilistic_threshold:
            return result.reality == Reality.DETERMINISTIC

        # Normal budget: accept DETERMINISTIC and PROBABILISTIC
        return True

    def with_budget(self, budget: float) -> "EntropyAware":
        """Create new contract with updated budget."""
        return EntropyAware(
            current_budget=budget,
            probabilistic_threshold=self.probabilistic_threshold,
            deterministic_threshold=self.deterministic_threshold,
        )


@dataclass
class IntentFilter(GravityContract):
    """
    Contract with custom intent filtering predicate.

    Allows fine-grained control over which intents are admitted.

    Example:
        >>> contract = IntentFilter(
        ...     predicate=lambda i: "delete" not in i.lower(),
        ...     description="No delete operations",
        ... )
        >>> contract.admits("read the file")  # True
        >>> contract.admits("delete all files")  # False
    """

    predicate: Callable[[str], bool]
    description: str = "Custom intent filter"
    name: str = "IntentFilter"

    def check(self, output: Any) -> str | None:
        """No output checks for intent filter."""
        return None

    def admits(self, intent: str) -> bool:
        """Apply custom predicate to intent."""
        try:
            return self.predicate(intent)
        except Exception:
            return False  # Fail closed


# --- Composite Reality Contracts ---


def create_safe_gate(
    require_deterministic: bool = False,
    max_steps: int = 5,
    entropy_budget: float = 1.0,
) -> list[GravityContract]:
    """
    Create a standard set of safety contracts for reality gating.

    Combines:
    - RealityGate: Rejects CHAOTIC intents
    - BoundedComplexity: Limits task complexity
    - EntropyAware: Adjusts strictness based on budget

    Args:
        require_deterministic: If True, only DETERMINISTIC intents pass
        max_steps: Maximum number of steps in an intent
        entropy_budget: Current entropy budget

    Returns:
        List of contracts to apply

    Example:
        >>> contracts = create_safe_gate(entropy_budget=0.5)
        >>> from agents.f.gravity import Grounded
        >>> agent = Grounded(inner=MyAgent(), gravity=contracts)
    """
    return [
        RealityGate(
            require_deterministic=require_deterministic,
            entropy_budget=entropy_budget,
        ),
        BoundedComplexity(max_steps=max_steps),
        EntropyAware(current_budget=entropy_budget),
    ]


def create_strict_gate() -> list[GravityContract]:
    """
    Create strict contracts for high-reliability contexts.

    Only admits DETERMINISTIC, atomic intents.
    """
    return [
        DeterministicOnly(),
        BoundedComplexity(max_steps=3, max_words=20),
    ]


# --- Convenience Functions ---


def admits_intent(intent: str, contracts: list[GravityContract]) -> bool:
    """
    Check if an intent is admitted by all contracts.

    Args:
        intent: The intent to check
        contracts: List of contracts to check against

    Returns:
        True if all contracts admit the intent
    """
    return all(c.admits(intent) for c in contracts)


def gate_intent(
    intent: str,
    contracts: list[GravityContract] | None = None,
) -> tuple[bool, str]:
    """
    Gate an intent, returning admission status and reason.

    Args:
        intent: The intent to gate
        contracts: Contracts to apply (default: create_safe_gate())

    Returns:
        Tuple of (admitted, reason)
    """
    if contracts is None:
        contracts = create_safe_gate()

    for contract in contracts:
        if not contract.admits(intent):
            return False, f"Rejected by {contract.name}"

    return True, "Admitted"
